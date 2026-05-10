import pytest
from race_monitor._rate_limiter import (
    _AsyncRateLimiter,
    _SyncRateLimiter,
    get_async_limiter,
    get_sync_limiter,
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
    limiter.acquire()   # t=0 → timestamps=[0.0]
    limiter.acquire()   # t=0 → timestamps=[0.0, 0.0]
    limiter.acquire()   # t=0 → full → sleep(60) → t=60 → evict both → timestamps=[60.0]

    assert len(slept) == 1
    assert slept[0] == pytest.approx(60.0)


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
    await limiter.acquire()   # t=0 → timestamps=[0.0]
    await limiter.acquire()   # t=0 → timestamps=[0.0, 0.0]
    await limiter.acquire()   # t=0 → full → sleep(60) → t=60 → evict both → timestamps=[60.0]

    assert len(slept) == 1
    assert slept[0] == pytest.approx(60.0)


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
