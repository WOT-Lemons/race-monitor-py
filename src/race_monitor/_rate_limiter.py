import asyncio
import logging
import threading
import time
from collections import deque

_logger = logging.getLogger(__name__)
_sync_limiters: dict[str, "_SyncRateLimiter"] = {}
_async_limiters: dict[str, "_AsyncRateLimiter"] = {}
_registry_lock = threading.Lock()


class _SyncRateLimiter:
    def __init__(self, rate: int, window: float = 60.0) -> None:
        if rate < 1:
            raise ValueError(f"rate must be >= 1, got {rate}")
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
                slots_used = len(self._timestamps)
                oldest_age = now - self._timestamps[0]
            _logger.warning(
                "Rate limited: sleeping %.2fs [%d/%d slots used over %.0fs window; oldest request %.2fs ago]",
                max(0.0, wait), slots_used, self._rate, self._window, oldest_age,
            )
            time.sleep(max(0.0, wait))


class _AsyncRateLimiter:
    def __init__(self, rate: int, window: float = 60.0) -> None:
        if rate < 1:
            raise ValueError(f"rate must be >= 1, got {rate}")
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
                slots_used = len(self._timestamps)
                oldest_age = now - self._timestamps[0]
            _logger.warning(
                "Rate limited: sleeping %.2fs [%d/%d slots used over %.0fs window; oldest request %.2fs ago]",
                max(0.0, wait), slots_used, self._rate, self._window, oldest_age,
            )
            await asyncio.sleep(max(0.0, wait))


def get_sync_limiter(token: str, rate: int, window: float) -> _SyncRateLimiter:
    """Return the rate limiter for *token*, creating it if needed.

    Raises ``ValueError`` if a limiter already exists for *token* with different
    ``rate`` or ``window`` values — callers sharing a token must agree on the config.
    """
    with _registry_lock:
        limiter = _sync_limiters.get(token)
        if limiter is None:
            limiter = _SyncRateLimiter(rate, window)
            _sync_limiters[token] = limiter
        elif limiter._rate != rate or limiter._window != window:
            raise ValueError(
                f"Limiter for token already exists with rate={limiter._rate}, "
                f"window={limiter._window}; got rate={rate}, window={window}"
            )
        return limiter


def get_async_limiter(token: str, rate: int, window: float) -> _AsyncRateLimiter:
    """Return the async rate limiter for *token*, creating it if needed.

    Raises ``ValueError`` if a limiter already exists for *token* with different
    ``rate`` or ``window`` values — callers sharing a token must agree on the config.
    """
    with _registry_lock:
        limiter = _async_limiters.get(token)
        if limiter is None:
            limiter = _AsyncRateLimiter(rate, window)
            _async_limiters[token] = limiter
        elif limiter._rate != rate or limiter._window != window:
            raise ValueError(
                f"Limiter for token already exists with rate={limiter._rate}, "
                f"window={limiter._window}; got rate={rate}, window={window}"
            )
        return limiter
