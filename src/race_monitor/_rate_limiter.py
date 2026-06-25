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
    def __init__(self, rate: int, window: float = 60.0, label: str = "") -> None:
        if rate < 1:
            raise ValueError(f"rate must be >= 1, got {rate}")
        self._rate = rate
        self._window = window
        self._label = label
        self._timestamps: deque[float] = deque()
        self._lock = threading.Lock()

    def capacity(self) -> int:
        with self._lock:
            now = time.monotonic()
            in_window = sum(1 for ts in self._timestamps if ts > now - self._window)
            return self._rate - in_window

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
            _logger.info(
                "Rate limited on ...%s: sleeping %.2fs "
                "[%d/%d slots used over %.0fs window; oldest request %.2fs ago]",
                self._label, max(0.0, wait), slots_used, self._rate, self._window, oldest_age,
            )
            time.sleep(max(0.0, wait))


class _AsyncRateLimiter:
    def __init__(self, rate: int, window: float = 60.0, label: str = "") -> None:
        if rate < 1:
            raise ValueError(f"rate must be >= 1, got {rate}")
        self._rate = rate
        self._window = window
        self._label = label
        self._timestamps: deque[float] = deque()
        self._lock = asyncio.Lock()

    def capacity(self) -> int:
        now = time.monotonic()
        return self._rate - sum(1 for ts in self._timestamps if ts > now - self._window)

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
            _logger.info(
                "Rate limited on ...%s: sleeping %.2fs "
                "[%d/%d slots used over %.0fs window; oldest request %.2fs ago]",
                self._label, max(0.0, wait), slots_used, self._rate, self._window, oldest_age,
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
            limiter = _SyncRateLimiter(rate, window, label=token[-4:])
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
            limiter = _AsyncRateLimiter(rate, window, label=token[-4:])
            _async_limiters[token] = limiter
        elif limiter._rate != rate or limiter._window != window:
            raise ValueError(
                f"Limiter for token already exists with rate={limiter._rate}, "
                f"window={limiter._window}; got rate={rate}, window={window}"
            )
        return limiter


class _NoOpSyncLimiter:
    def capacity(self) -> int:
        return 10**9

    def acquire(self) -> None:
        pass


class _NoOpAsyncLimiter:
    def capacity(self) -> int:
        return 10**9

    async def acquire(self) -> None:
        pass


class _TokenPool:
    def __init__(self, entries: list[tuple[str, _SyncRateLimiter | _NoOpSyncLimiter]]) -> None:
        self._entries = entries

    def select(self) -> tuple[str, _SyncRateLimiter | _NoOpSyncLimiter]:
        return max(self._entries, key=lambda e: e[1].capacity())


class _AsyncTokenPool:
    def __init__(self, entries: list[tuple[str, _AsyncRateLimiter | _NoOpAsyncLimiter]]) -> None:
        self._entries = entries

    def select(self) -> tuple[str, _AsyncRateLimiter | _NoOpAsyncLimiter]:
        return max(self._entries, key=lambda e: e[1].capacity())


def get_sync_pool(token_rates: dict[str, int | None], window: float) -> _TokenPool:
    entries = []
    for t, r in token_rates.items():
        limiter = _NoOpSyncLimiter() if r is None else get_sync_limiter(t, r, window)
        entries.append((t, limiter))
    return _TokenPool(entries)


def get_async_pool(token_rates: dict[str, int | None], window: float) -> _AsyncTokenPool:
    entries = []
    for t, r in token_rates.items():
        limiter = _NoOpAsyncLimiter() if r is None else get_async_limiter(t, r, window)
        entries.append((t, limiter))
    return _AsyncTokenPool(entries)
