import asyncio
import threading
import time
from collections import deque

_sync_limiters: dict[str, "_SyncRateLimiter"] = {}
_async_limiters: dict[str, "_AsyncRateLimiter"] = {}
_registry_lock = threading.Lock()


class _SyncRateLimiter:
    def __init__(self, rate: int, window: float = 60.0) -> None:
        self._rate = rate
        self._window = window
        self._timestamps: deque[float] = deque()
        self._lock = threading.Lock()

    def acquire(self) -> None:
        while True:
            with self._lock:
                now = time.monotonic()
                while self._timestamps and self._timestamps[0] <= now - self._window:
                    self._timestamps.popleft()
                if len(self._timestamps) < self._rate:
                    self._timestamps.append(now)
                    return
                wait = self._window - (now - self._timestamps[0])
            time.sleep(max(0.0, wait))


class _AsyncRateLimiter:
    def __init__(self, rate: int, window: float = 60.0) -> None:
        self._rate = rate
        self._window = window
        self._timestamps: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        while True:
            async with self._lock:
                now = time.monotonic()
                while self._timestamps and self._timestamps[0] <= now - self._window:
                    self._timestamps.popleft()
                if len(self._timestamps) < self._rate:
                    self._timestamps.append(now)
                    return
                wait = self._window - (now - self._timestamps[0])
            await asyncio.sleep(max(0.0, wait))


def get_sync_limiter(token: str, rate: int, window: float) -> _SyncRateLimiter:
    with _registry_lock:
        if token not in _sync_limiters:
            _sync_limiters[token] = _SyncRateLimiter(rate, window)
        return _sync_limiters[token]


def get_async_limiter(token: str, rate: int, window: float) -> _AsyncRateLimiter:
    with _registry_lock:
        if token not in _async_limiters:
            _async_limiters[token] = _AsyncRateLimiter(rate, window)
        return _async_limiters[token]
