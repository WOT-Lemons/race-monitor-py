import logging

import pytest

from race_monitor._rate_limiter import (
    _AsyncRateLimiter,
    _AsyncTokenPool,
    _NoOpAsyncLimiter,
    _NoOpSyncLimiter,
    _SyncRateLimiter,
    _TokenPool,
    get_async_limiter,
    get_async_pool,
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
