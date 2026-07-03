import pytest

from race_monitor._rate_limiter import (
    _BudgetPool,
    _TokenBudget,
    get_budget,
    get_pool,
)

# --- _TokenBudget ---


def test_budget_rejects_invalid_rate():
    with pytest.raises(ValueError, match="rate must be >= 1"):
        _TokenBudget(rate=0)


def test_budget_try_acquire_takes_slots_within_rate():
    budget = _TokenBudget(rate=3, window=60.0)
    for _ in range(3):
        assert budget.try_acquire() == 0.0
    assert budget.capacity() == 0


def test_budget_try_acquire_reports_window_wait(monkeypatch):
    t = [0.0]
    monkeypatch.setattr("race_monitor._rate_limiter.time.monotonic", lambda: t[0])
    budget = _TokenBudget(rate=2, window=60.0)
    assert budget.try_acquire() == 0.0
    assert budget.try_acquire() == 0.0
    assert budget.try_acquire() == pytest.approx(60.0)  # full — refused, nothing taken
    assert budget.capacity() == 0
    t[0] = 60.5
    assert budget.try_acquire() == 0.0  # oldest slots evicted


def test_budget_try_acquire_refuses_while_cooling():
    budget = _TokenBudget(rate=6, window=60.0)
    budget.mark_cooldown(10.0)
    wait = budget.try_acquire()
    assert wait == pytest.approx(10.0, abs=0.5)
    assert budget.capacity() == 6  # refusal must not consume a slot


def test_budget_next_available_is_read_only(monkeypatch):
    t = [0.0]
    monkeypatch.setattr("race_monitor._rate_limiter.time.monotonic", lambda: t[0])
    budget = _TokenBudget(rate=1, window=60.0)
    assert budget.next_available() == 0.0
    assert budget.capacity() == 1  # nothing consumed
    budget.try_acquire()
    assert budget.next_available() == pytest.approx(60.0)


def test_budget_release_refunds_slot():
    budget = _TokenBudget(rate=2, window=60.0)
    budget.try_acquire()
    assert budget.capacity() == 1
    budget.release()
    assert budget.capacity() == 2


def test_budget_cooldown_expires(monkeypatch):
    t = [100.0]
    monkeypatch.setattr("race_monitor._rate_limiter.time.monotonic", lambda: t[0])
    budget = _TokenBudget(rate=6, window=60.0)
    budget.mark_cooldown(10.0)
    assert budget.cooling() == 10.0
    t[0] = 110.0
    assert budget.cooling() == 0.0


def test_budget_consecutive_429_cooldowns_escalate(monkeypatch):
    t = [0.0]
    monkeypatch.setattr("race_monitor._rate_limiter.time.monotonic", lambda: t[0])
    budget = _TokenBudget(rate=6, window=60.0)
    for expected in [10.0, 20.0, 40.0, 80.0, 120.0, 120.0]:  # capped at MAX_BACKOFF
        budget.mark_cooldown(10.0)
        assert budget.cooling() == pytest.approx(expected)
        t[0] += expected  # let the cooldown expire before the next 429
    budget.note_success()
    budget.mark_cooldown(10.0)
    assert budget.cooling() == pytest.approx(10.0)  # escalation reset


def test_budget_retry_after_overrides_when_larger(monkeypatch):
    t = [0.0]
    monkeypatch.setattr("race_monitor._rate_limiter.time.monotonic", lambda: t[0])
    budget = _TokenBudget(rate=6, window=60.0)
    budget.mark_cooldown(10.0, retry_after=45.0)
    assert budget.cooling() == pytest.approx(45.0)


def test_budget_retry_after_ignored_when_smaller(monkeypatch):
    t = [0.0]
    monkeypatch.setattr("race_monitor._rate_limiter.time.monotonic", lambda: t[0])
    budget = _TokenBudget(rate=6, window=60.0)
    budget.mark_cooldown(10.0, retry_after=2.0)
    assert budget.cooling() == pytest.approx(10.0)


def test_unlimited_budget_never_throttles():
    budget = _TokenBudget(rate=None, window=60.0)
    for _ in range(100):
        assert budget.try_acquire() == 0.0
    assert budget.capacity() == 10**9


def test_unlimited_budget_honors_cooldown():
    budget = _TokenBudget(rate=None, window=60.0)
    budget.mark_cooldown(10.0)
    assert budget.try_acquire() == pytest.approx(10.0, abs=0.5)


# --- get_budget registry ---


def test_get_budget_same_token_returns_same_instance():
    a = get_budget("budget-same", 6, 60.0)
    b = get_budget("budget-same", 6, 60.0)
    assert a is b


def test_get_budget_different_tokens_return_different_instances():
    a = get_budget("budget-diff-a", 6, 60.0)
    b = get_budget("budget-diff-b", 6, 60.0)
    assert a is not b


def test_get_budget_conflicting_rate_raises():
    get_budget("budget-conflict", 6, 60.0)
    with pytest.raises(ValueError, match="already exists"):
        get_budget("budget-conflict", 10, 60.0)


def test_get_budget_sets_label():
    budget = get_budget("budget-label-abcd", 6, 60.0)
    assert budget._label == "abcd"


def test_get_budget_registers_unlimited_tokens():
    a = get_budget("budget-unlimited", None, 60.0)
    b = get_budget("budget-unlimited", None, 60.0)
    assert a is b  # unlimited tokens share cooldown state too


# --- _BudgetPool ---


def test_budget_pool_select_returns_highest_capacity():
    a = _TokenBudget(rate=6, window=60.0)
    b = _TokenBudget(rate=6, window=60.0)
    a.try_acquire()
    a.try_acquire()  # a: 4 remaining, b: 6 remaining
    pool = _BudgetPool([("tok_a", a), ("tok_b", b)])
    token, selected = pool.select()
    assert token == "tok_b"
    assert selected is b


def test_budget_pool_select_skips_cooling_token():
    cooling = _TokenBudget(rate=6, window=60.0)
    healthy = _TokenBudget(rate=6, window=60.0)
    cooling.mark_cooldown(10.0)
    pool = _BudgetPool([("cooling-tok", cooling), ("healthy-tok", healthy)])
    for _ in range(10):
        token, selected = pool.select()
        assert token == "healthy-tok"
        assert selected is healthy


def test_budget_pool_select_returns_none_when_all_cooling():
    a = _TokenBudget(rate=6, window=60.0)
    b = _TokenBudget(rate=6, window=60.0)
    a.mark_cooldown(10.0)
    b.mark_cooldown(10.0)
    pool = _BudgetPool([("a", a), ("b", b)])
    assert pool.select() is None


def test_budget_pool_try_acquire_returns_token_and_budget():
    budget = _TokenBudget(rate=6, window=60.0)
    pool = _BudgetPool([("tok", budget)])
    token, acquired = pool.try_acquire()
    assert token == "tok"
    assert acquired is budget
    assert budget.capacity() == 5  # slot actually taken


def test_budget_pool_try_acquire_none_when_all_cooling():
    budget = _TokenBudget(rate=6, window=60.0)
    budget.mark_cooldown(10.0)
    pool = _BudgetPool([("tok", budget)])
    assert pool.try_acquire() is None


def test_budget_pool_try_acquire_refuses_token_cooled_after_selection(monkeypatch):
    """A 429 landing between select() and try_acquire() must not let the token through."""
    budget = _TokenBudget(rate=6, window=60.0)
    pool = _BudgetPool([("tok", budget)])
    original_select = pool.select

    def select_then_429():
        selected = original_select()
        budget.mark_cooldown(10.0)  # concurrent 429 lands after selection
        return selected

    monkeypatch.setattr(pool, "select", select_then_429)
    assert pool.try_acquire() is None
    assert budget.capacity() == 6  # no slot consumed


def test_budget_pool_wait_time_is_min_across_budgets(monkeypatch):
    t = [0.0]
    monkeypatch.setattr("race_monitor._rate_limiter.time.monotonic", lambda: t[0])
    a = _TokenBudget(rate=6, window=60.0)
    b = _TokenBudget(rate=6, window=60.0)
    a.mark_cooldown(10.0)
    b.mark_cooldown(3.0)
    pool = _BudgetPool([("a", a), ("b", b)])
    assert pool.wait_time() == 3.0


def test_budget_pool_wait_time_zero_when_available():
    pool = _BudgetPool([("a", _TokenBudget(rate=6, window=60.0))])
    assert pool.wait_time() == 0.0


def test_get_pool_builds_entries_with_correct_rates():
    pool = get_pool({"pool-budget-alpha": 6, "pool-budget-beta": 10}, 60.0)
    assert len(pool._entries) == 2
    rates = {t: b._rate for t, b in pool._entries}
    assert rates["pool-budget-alpha"] == 6
    assert rates["pool-budget-beta"] == 10


def test_get_pool_unlimited_token_wins_select():
    pool = get_pool({"pool-limited-tok": 6, "pool-unlimited-tok": None}, 60.0)
    token, _ = pool.select()
    assert token == "pool-unlimited-tok"


def test_get_pool_shares_budgets_across_pools():
    pool_a = get_pool({"pool-shared-tok": 6}, 60.0)
    pool_b = get_pool({"pool-shared-tok": 6}, 60.0)
    assert pool_a._entries[0][1] is pool_b._entries[0][1]
