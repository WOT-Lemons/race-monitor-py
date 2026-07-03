import logging

import pytest

from race_monitor._rate_limiter import (
    _AsyncRateLimiter,
    _AsyncTokenPool,
    _NoOpAsyncLimiter,
    _NoOpSyncLimiter,
    _SyncRateLimiter,
    _TokenBudget,
    _TokenPool,
    get_async_limiter,
    get_async_pool,
    get_budget,
    get_sync_limiter,
    get_sync_pool,
)

# --- _SyncRateLimiter ---


def test_sync_limiter_rejects_invalid_rate():
    with pytest.raises(ValueError, match="rate must be >= 1"):
        _SyncRateLimiter(rate=0)


def test_sync_allows_requests_within_rate():
    limiter = _SyncRateLimiter(rate=3, window=60.0)
    for _ in range(3):
        limiter.acquire()
    assert len(limiter._timestamps) == 3


def test_sync_sleeps_when_rate_exceeded(monkeypatch):
    t = [0.0]
    monkeypatch.setattr("race_monitor._rate_limiter.time.monotonic", lambda: t[0])

    slept = []

    def mock_sleep(secs):
        t[0] += secs
        slept.append(secs)

    monkeypatch.setattr("race_monitor._rate_limiter.time.sleep", mock_sleep)

    limiter = _SyncRateLimiter(rate=2, window=60.0)
    limiter.acquire()  # t=0 → timestamps=[0.0]
    limiter.acquire()  # t=0 → timestamps=[0.0, 0.0]
    limiter.acquire()  # t=0 → full → sleep(60) → t=60 → evict both → timestamps=[60.0]

    assert len(slept) == 1
    assert slept[0] == pytest.approx(60.0)


def test_sync_logs_info_when_throttled(monkeypatch, caplog):
    t = [0.0]
    monkeypatch.setattr("race_monitor._rate_limiter.time.monotonic", lambda: t[0])

    def mock_sleep(secs):
        t[0] += secs

    monkeypatch.setattr("race_monitor._rate_limiter.time.sleep", mock_sleep)

    limiter = _SyncRateLimiter(rate=2, window=60.0)
    limiter.acquire()  # slot 1
    limiter.acquire()  # slot 2 — full

    with caplog.at_level(logging.INFO, logger="race_monitor._rate_limiter"):
        limiter.acquire()  # throttled → should log

    assert "Rate limited" in caplog.text
    assert "2/2" in caplog.text
    assert "60" in caplog.text
    assert "sleeping" in caplog.text


def test_sync_no_log_when_not_throttled(caplog):
    limiter = _SyncRateLimiter(rate=3, window=60.0)
    with caplog.at_level(logging.INFO, logger="race_monitor._rate_limiter"):
        limiter.acquire()
    assert caplog.text == ""


def test_sync_capacity_empty():
    limiter = _SyncRateLimiter(rate=3, window=60.0)
    assert limiter.capacity() == 3


def test_sync_capacity_after_acquires():
    limiter = _SyncRateLimiter(rate=3, window=60.0)
    limiter.acquire()
    limiter.acquire()
    assert limiter.capacity() == 1


def test_sync_capacity_zero_when_full():
    limiter = _SyncRateLimiter(rate=2, window=60.0)
    limiter.acquire()
    limiter.acquire()
    assert limiter.capacity() == 0


def test_sync_label_in_log_message(monkeypatch, caplog):
    t = [0.0]
    monkeypatch.setattr("race_monitor._rate_limiter.time.monotonic", lambda: t[0])

    def mock_sleep(secs):
        t[0] += secs

    monkeypatch.setattr("race_monitor._rate_limiter.time.sleep", mock_sleep)

    limiter = _SyncRateLimiter(rate=1, window=60.0, label="abcd")
    limiter.acquire()

    with caplog.at_level(logging.INFO, logger="race_monitor._rate_limiter"):
        limiter.acquire()

    assert "...abcd" in caplog.text


def test_get_sync_limiter_sets_label():
    limiter = get_sync_limiter("label-test-sync-abcd", 6, 60.0)
    assert limiter._label == "abcd"


# --- _AsyncRateLimiter ---


async def test_async_limiter_rejects_invalid_rate():
    with pytest.raises(ValueError, match="rate must be >= 1"):
        _AsyncRateLimiter(rate=0)


async def test_async_allows_requests_within_rate():
    limiter = _AsyncRateLimiter(rate=3, window=60.0)
    for _ in range(3):
        await limiter.acquire()
    assert len(limiter._timestamps) == 3


async def test_async_sleeps_when_rate_exceeded(monkeypatch):
    t = [0.0]
    monkeypatch.setattr("race_monitor._rate_limiter.time.monotonic", lambda: t[0])

    slept = []

    async def mock_sleep(secs):
        t[0] += secs
        slept.append(secs)

    monkeypatch.setattr("race_monitor._rate_limiter.asyncio.sleep", mock_sleep)

    limiter = _AsyncRateLimiter(rate=2, window=60.0)
    await limiter.acquire()  # t=0 → timestamps=[0.0]
    await limiter.acquire()  # t=0 → timestamps=[0.0, 0.0]
    await limiter.acquire()  # t=0 → full → sleep(60) → t=60 → evict both → timestamps=[60.0]

    assert len(slept) == 1
    assert slept[0] == pytest.approx(60.0)


async def test_async_logs_info_when_throttled(monkeypatch, caplog):
    t = [0.0]
    monkeypatch.setattr("race_monitor._rate_limiter.time.monotonic", lambda: t[0])

    async def mock_sleep(secs):
        t[0] += secs

    monkeypatch.setattr("race_monitor._rate_limiter.asyncio.sleep", mock_sleep)

    limiter = _AsyncRateLimiter(rate=2, window=60.0)
    await limiter.acquire()  # slot 1
    await limiter.acquire()  # slot 2 — full

    with caplog.at_level(logging.INFO, logger="race_monitor._rate_limiter"):
        await limiter.acquire()  # throttled → should log

    assert "Rate limited" in caplog.text
    assert "2/2" in caplog.text
    assert "60" in caplog.text
    assert "sleeping" in caplog.text


async def test_async_no_log_when_not_throttled(caplog):
    limiter = _AsyncRateLimiter(rate=3, window=60.0)
    with caplog.at_level(logging.INFO, logger="race_monitor._rate_limiter"):
        await limiter.acquire()
    assert caplog.text == ""


async def test_async_capacity_empty():
    limiter = _AsyncRateLimiter(rate=3, window=60.0)
    assert limiter.capacity() == 3


async def test_async_capacity_after_acquires():
    limiter = _AsyncRateLimiter(rate=3, window=60.0)
    await limiter.acquire()
    await limiter.acquire()
    assert limiter.capacity() == 1


async def test_async_label_in_log_message(monkeypatch, caplog):
    t = [0.0]
    monkeypatch.setattr("race_monitor._rate_limiter.time.monotonic", lambda: t[0])

    async def mock_sleep(secs):
        t[0] += secs

    monkeypatch.setattr("race_monitor._rate_limiter.asyncio.sleep", mock_sleep)

    limiter = _AsyncRateLimiter(rate=1, window=60.0, label="efgh")
    await limiter.acquire()

    with caplog.at_level(logging.INFO, logger="race_monitor._rate_limiter"):
        await limiter.acquire()

    assert "...efgh" in caplog.text


def test_get_async_limiter_sets_label():
    limiter = get_async_limiter("label-test-async-efgh", 6, 60.0)
    assert limiter._label == "efgh"


def test_sync_release_restores_capacity():
    limiter = _SyncRateLimiter(rate=2, window=60.0)
    ts = limiter.acquire()
    assert limiter.capacity() == 1
    limiter.release(ts)
    assert limiter.capacity() == 2


async def test_async_release_restores_capacity():
    limiter = _AsyncRateLimiter(rate=2, window=60.0)
    ts = await limiter.acquire()
    assert limiter.capacity() == 1
    limiter.release(ts)
    assert limiter.capacity() == 2


def test_no_op_sync_limiter_release_is_noop():
    limiter = _NoOpSyncLimiter()
    limiter.release(0.0)  # must not raise


async def test_no_op_async_limiter_release_is_noop():
    limiter = _NoOpAsyncLimiter()
    limiter.release(0.0)  # must not raise


# --- Registry ---


def test_get_sync_limiter_same_token_returns_same_instance():
    a = get_sync_limiter("registry-same", 6, 60.0)
    b = get_sync_limiter("registry-same", 6, 60.0)
    assert a is b


def test_get_sync_limiter_different_tokens_return_different_instances():
    a = get_sync_limiter("registry-sync-a", 6, 60.0)
    b = get_sync_limiter("registry-sync-b", 6, 60.0)
    assert a is not b


def test_get_async_limiter_same_token_returns_same_instance():
    a = get_async_limiter("registry-async-same", 6, 60.0)
    b = get_async_limiter("registry-async-same", 6, 60.0)
    assert a is b


def test_get_async_limiter_different_tokens_return_different_instances():
    a = get_async_limiter("registry-async-a", 6, 60.0)
    b = get_async_limiter("registry-async-b", 6, 60.0)
    assert a is not b


def test_get_sync_limiter_raises_on_conflicting_rate():
    get_sync_limiter("conflict-sync", 6, 60.0)
    with pytest.raises(ValueError, match="already exists"):
        get_sync_limiter("conflict-sync", 10, 60.0)


def test_get_async_limiter_raises_on_conflicting_rate():
    get_async_limiter("conflict-async", 6, 60.0)
    with pytest.raises(ValueError, match="already exists"):
        get_async_limiter("conflict-async", 10, 60.0)


# --- _TokenPool / _AsyncTokenPool ---


def test_sync_pool_select_returns_highest_capacity():
    limiter_a = _SyncRateLimiter(rate=6, window=60.0)
    limiter_b = _SyncRateLimiter(rate=6, window=60.0)
    limiter_a.acquire()
    limiter_a.acquire()  # a: 4 remaining, b: 6 remaining
    pool = _TokenPool([("tok_a", limiter_a), ("tok_b", limiter_b)])
    token, selected = pool.select()
    assert token == "tok_b"
    assert selected is limiter_b


def test_sync_pool_select_single_entry():
    limiter = _SyncRateLimiter(rate=6, window=60.0)
    pool = _TokenPool([("only", limiter)])
    token, selected = pool.select()
    assert token == "only"
    assert selected is limiter


def test_sync_pool_select_prefers_higher_rate_limit():
    limiter_a = _SyncRateLimiter(rate=6, window=60.0)
    limiter_b = _SyncRateLimiter(rate=10, window=60.0)
    pool = _TokenPool([("tok_a", limiter_a), ("tok_b", limiter_b)])
    token, _ = pool.select()
    assert token == "tok_b"


async def test_async_pool_select_returns_highest_capacity():
    limiter_a = _AsyncRateLimiter(rate=6, window=60.0)
    limiter_b = _AsyncRateLimiter(rate=6, window=60.0)
    await limiter_a.acquire()
    await limiter_a.acquire()  # a: 4 remaining, b: 6 remaining
    pool = _AsyncTokenPool([("tok_a", limiter_a), ("tok_b", limiter_b)])
    token, selected = pool.select()
    assert token == "tok_b"
    assert selected is limiter_b


def test_get_sync_pool_builds_entries_with_correct_rates():
    pool = get_sync_pool({"pool-sync-alpha": 6, "pool-sync-beta": 10}, 60.0)
    assert len(pool._entries) == 2
    rates = {t: lim._rate for t, lim in pool._entries}
    assert rates["pool-sync-alpha"] == 6
    assert rates["pool-sync-beta"] == 10


async def test_get_async_pool_builds_entries_with_correct_rates():
    pool = get_async_pool({"pool-async-alpha": 6, "pool-async-beta": 10}, 60.0)
    assert len(pool._entries) == 2
    rates = {t: lim._rate for t, lim in pool._entries}
    assert rates["pool-async-alpha"] == 6
    assert rates["pool-async-beta"] == 10


def test_no_op_sync_limiter_capacity_is_large():
    limiter = _NoOpSyncLimiter()
    assert limiter.capacity() == 10**9


def test_no_op_sync_limiter_acquire_is_noop():
    limiter = _NoOpSyncLimiter()
    limiter.acquire()  # must not raise or block


async def test_no_op_async_limiter_capacity_is_large():
    limiter = _NoOpAsyncLimiter()
    assert limiter.capacity() == 10**9


async def test_no_op_async_limiter_acquire_is_noop():
    limiter = _NoOpAsyncLimiter()
    await limiter.acquire()  # must not raise or block


def test_sync_pool_none_rate_uses_noop_limiter():
    pool = get_sync_pool({"unlimited-sync-tok": None}, 60.0)
    _, limiter = pool._entries[0]
    assert isinstance(limiter, _NoOpSyncLimiter)


def test_sync_pool_none_rate_wins_select_over_rate_limited():
    pool = get_sync_pool({"limited-tok": 6, "unlimited-tok": None}, 60.0)
    token, _ = pool.select()
    assert token == "unlimited-tok"


async def test_async_pool_none_rate_uses_noop_limiter():
    pool = get_async_pool({"unlimited-async-tok": None}, 60.0)
    _, limiter = pool._entries[0]
    assert isinstance(limiter, _NoOpAsyncLimiter)


# --- 429 cooldown ---


def test_sync_limiter_not_cooling_initially():
    limiter = _SyncRateLimiter(rate=6, window=60.0)
    assert limiter.cooling() == 0.0


def test_sync_mark_cooldown_makes_limiter_cool():
    limiter = _SyncRateLimiter(rate=6, window=60.0)
    limiter.mark_cooldown(10.0)
    assert limiter.cooling() == pytest.approx(10.0, abs=0.5)


def test_sync_cooldown_expires(monkeypatch):
    t = [100.0]
    monkeypatch.setattr("race_monitor._rate_limiter.time.monotonic", lambda: t[0])
    limiter = _SyncRateLimiter(rate=6, window=60.0)
    limiter.mark_cooldown(10.0)
    assert limiter.cooling() == 10.0
    t[0] = 110.0
    assert limiter.cooling() == 0.0


def test_sync_pool_select_skips_cooling_token():
    cooling = _SyncRateLimiter(rate=6, window=60.0)
    healthy = _SyncRateLimiter(rate=6, window=60.0)
    cooling.mark_cooldown(10.0)
    pool = _TokenPool([("cooling-tok", cooling), ("healthy-tok", healthy)])
    # Even though both have full local capacity, the cooling token is skipped.
    for _ in range(10):
        token, selected = pool.select()
        assert token == "healthy-tok"
        assert selected is healthy


def test_sync_pool_select_returns_none_when_all_cooling():
    a = _SyncRateLimiter(rate=6, window=60.0)
    b = _SyncRateLimiter(rate=6, window=60.0)
    a.mark_cooldown(10.0)
    b.mark_cooldown(10.0)
    pool = _TokenPool([("a", a), ("b", b)])
    assert pool.select() is None


def test_sync_pool_cooldown_wait_returns_soonest_expiry(monkeypatch):
    t = [0.0]
    monkeypatch.setattr("race_monitor._rate_limiter.time.monotonic", lambda: t[0])
    a = _SyncRateLimiter(rate=6, window=60.0)
    b = _SyncRateLimiter(rate=6, window=60.0)
    a.mark_cooldown(10.0)
    b.mark_cooldown(3.0)
    pool = _TokenPool([("a", a), ("b", b)])
    assert pool.cooldown_wait() == 3.0


def test_sync_pool_cooldown_wait_zero_when_none_cooling():
    pool = _TokenPool([("a", _SyncRateLimiter(rate=6, window=60.0))])
    assert pool.cooldown_wait() == 0.0


def test_no_op_sync_limiter_honors_cooldown():
    limiter = _NoOpSyncLimiter()
    assert limiter.cooling() == 0.0
    limiter.mark_cooldown(10.0)
    assert limiter.cooling() == pytest.approx(10.0, abs=0.5)


async def test_async_mark_cooldown_makes_limiter_cool():
    limiter = _AsyncRateLimiter(rate=6, window=60.0)
    limiter.mark_cooldown(10.0)
    assert limiter.cooling() == pytest.approx(10.0, abs=0.5)


def test_async_pool_select_skips_cooling_token():
    cooling = _AsyncRateLimiter(rate=6, window=60.0)
    healthy = _AsyncRateLimiter(rate=6, window=60.0)
    cooling.mark_cooldown(10.0)
    pool = _AsyncTokenPool([("cooling-tok", cooling), ("healthy-tok", healthy)])
    token, selected = pool.select()
    assert token == "healthy-tok"
    assert selected is healthy


def test_async_pool_select_returns_none_when_all_cooling():
    a = _AsyncRateLimiter(rate=6, window=60.0)
    b = _AsyncRateLimiter(rate=6, window=60.0)
    a.mark_cooldown(10.0)
    b.mark_cooldown(10.0)
    pool = _AsyncTokenPool([("a", a), ("b", b)])
    assert pool.select() is None


def test_no_op_async_limiter_honors_cooldown():
    limiter = _NoOpAsyncLimiter()
    assert limiter.cooling() == 0.0
    limiter.mark_cooldown(10.0)
    assert limiter.cooling() == pytest.approx(10.0, abs=0.5)


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
