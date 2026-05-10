import logging

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
