import asyncio
import contextlib
import logging
import random
import threading
import time
from collections import deque

_logger = logging.getLogger(__name__)
_sync_limiters: dict[str, "_SyncRateLimiter"] = {}
_async_limiters: dict[str, "_AsyncRateLimiter"] = {}
_budgets: dict[str, "_TokenBudget"] = {}
_registry_lock = threading.Lock()

MAX_BACKOFF = 120.0


class _SyncRateLimiter:
    def __init__(self, rate: int, window: float = 60.0, label: str = "") -> None:
        if rate < 1:
            raise ValueError(f"rate must be >= 1, got {rate}")
        self._rate = rate
        self._window = window
        self._label = label
        self._timestamps: deque[float] = deque()
        self._cooldown_until = 0.0
        self._lock = threading.Lock()

    def cooling(self) -> float:
        """Seconds remaining before this token may be used again (0 if available)."""
        with self._lock:
            return max(0.0, self._cooldown_until - time.monotonic())

    def mark_cooldown(self, duration: float) -> None:
        """Mark this token unusable for *duration* seconds (e.g. after a server 429)."""
        with self._lock:
            self._cooldown_until = time.monotonic() + duration

    def capacity(self) -> int:
        with self._lock:
            now = time.monotonic()
            in_window = sum(1 for ts in self._timestamps if ts > now - self._window)
            return self._rate - in_window

    def acquire(self) -> float:
        while True:
            with self._lock:
                now = time.monotonic()
                while self._timestamps and self._timestamps[0] <= now - self._window:
                    self._timestamps.popleft()
                if len(self._timestamps) < self._rate:
                    self._timestamps.append(now)
                    return now
                wait = self._window - (now - self._timestamps[0])
                slots_used = len(self._timestamps)
                oldest_age = now - self._timestamps[0]
            _logger.info(
                "Rate limited on ...%s: sleeping %.2fs "
                "[%d/%d slots used over %.0fs window; oldest request %.2fs ago]",
                self._label,
                max(0.0, wait),
                slots_used,
                self._rate,
                self._window,
                oldest_age,
            )
            time.sleep(max(0.0, wait))

    def release(self, ts: float) -> None:
        with self._lock, contextlib.suppress(ValueError):  # ValueError: evicted by window cleanup
            self._timestamps.remove(ts)


class _AsyncRateLimiter:
    def __init__(self, rate: int, window: float = 60.0, label: str = "") -> None:
        if rate < 1:
            raise ValueError(f"rate must be >= 1, got {rate}")
        self._rate = rate
        self._window = window
        self._label = label
        self._timestamps: deque[float] = deque()
        self._cooldown_until = 0.0
        self._lock = asyncio.Lock()

    def cooling(self) -> float:
        """Seconds remaining before this token may be used again (0 if available).

        No lock needed: a single float read/write is atomic under asyncio's
        cooperative scheduling (same rationale as ``release``).
        """
        return max(0.0, self._cooldown_until - time.monotonic())

    def mark_cooldown(self, duration: float) -> None:
        """Mark this token unusable for *duration* seconds (e.g. after a server 429)."""
        self._cooldown_until = time.monotonic() + duration

    def capacity(self) -> int:
        now = time.monotonic()
        return self._rate - sum(1 for ts in self._timestamps if ts > now - self._window)

    async def acquire(self) -> float:
        while True:
            async with self._lock:
                now = time.monotonic()
                while self._timestamps and self._timestamps[0] <= now - self._window:
                    self._timestamps.popleft()
                if len(self._timestamps) < self._rate:
                    self._timestamps.append(now)
                    return now
                wait = self._window - (now - self._timestamps[0])
                slots_used = len(self._timestamps)
                oldest_age = now - self._timestamps[0]
            _logger.info(
                "Rate limited on ...%s: sleeping %.2fs "
                "[%d/%d slots used over %.0fs window; oldest request %.2fs ago]",
                self._label,
                max(0.0, wait),
                slots_used,
                self._rate,
                self._window,
                oldest_age,
            )
            await asyncio.sleep(max(0.0, wait))

    def release(self, ts: float) -> None:
        # No lock needed: asyncio cooperative scheduling ensures no other coroutine
        # modifies _timestamps between statement boundaries, and deque.remove is atomic.
        with contextlib.suppress(ValueError):  # may be evicted by window cleanup
            self._timestamps.remove(ts)


class _NoOpSyncLimiter:
    """Unlimited-rate limiter: no local throttling, but still honors 429 cooldown
    so an unlimited token backs off on a server 429 instead of hot-looping."""

    def __init__(self) -> None:
        self._cooldown_until = 0.0

    def capacity(self) -> int:
        return 10**9

    def acquire(self) -> float:
        return 0.0

    def release(self, ts: float) -> None:
        pass

    def cooling(self) -> float:
        return max(0.0, self._cooldown_until - time.monotonic())

    def mark_cooldown(self, duration: float) -> None:
        self._cooldown_until = time.monotonic() + duration


class _NoOpAsyncLimiter:
    """Unlimited-rate limiter: no local throttling, but still honors 429 cooldown
    so an unlimited token backs off on a server 429 instead of hot-looping."""

    def __init__(self) -> None:
        self._cooldown_until = 0.0

    def capacity(self) -> int:
        return 10**9

    async def acquire(self) -> float:
        return 0.0

    def release(self, ts: float) -> None:
        pass

    def cooling(self) -> float:
        return max(0.0, self._cooldown_until - time.monotonic())

    def mark_cooldown(self, duration: float) -> None:
        self._cooldown_until = time.monotonic() + duration


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


class _TokenBudget:
    """Thread-safe per-token request budget: sliding window plus 429 cooldown.

    One instance exists per token (see ``get_budget``) and is shared by sync and
    async clients alike. All state is guarded by a ``threading.Lock`` and no
    asyncio primitives are held, so instances survive event-loop restarts.

    ``rate=None`` means unlimited: no local throttling, but 429 cooldown still
    applies so an unlimited token backs off instead of hot-looping.
    """

    def __init__(self, rate: int | None, window: float = 60.0, label: str = "") -> None:
        if rate is not None and rate < 1:
            raise ValueError(f"rate must be >= 1, got {rate}")
        self._rate = rate
        self._window = window
        self._label = label
        self._timestamps: deque[float] = deque()
        self._cooldown_until = 0.0
        self._consecutive_429s = 0
        self._lock = threading.Lock()

    def try_acquire(self) -> float:
        """Atomically try to take a request slot.

        Returns 0.0 if a slot was taken. Otherwise returns the seconds until an
        attempt could succeed (cooldown remaining or oldest-slot expiry) and
        takes nothing. Checking cooldown here, under the lock, prevents a token
        that was 429'd after pool selection from being used anyway.
        """
        with self._lock:
            now = time.monotonic()
            if now < self._cooldown_until:
                return self._cooldown_until - now
            if self._rate is not None:
                while self._timestamps and self._timestamps[0] <= now - self._window:
                    self._timestamps.popleft()
                if len(self._timestamps) >= self._rate:
                    return self._window - (now - self._timestamps[0])
                self._timestamps.append(now)
            return 0.0

    def next_available(self) -> float:
        """Seconds until ``try_acquire`` could succeed (0.0 if it would now).

        Read-only: never takes a slot or evicts timestamps.
        """
        with self._lock:
            now = time.monotonic()
            wait = max(0.0, self._cooldown_until - now)
            if self._rate is not None:
                in_window = [ts for ts in self._timestamps if ts > now - self._window]
                if len(in_window) >= self._rate:
                    wait = max(wait, self._window - (now - in_window[0]))
            return wait

    def release(self) -> None:
        """Refund the most recently taken slot (the request got a 429)."""
        with self._lock:
            if self._timestamps:
                self._timestamps.pop()

    def capacity(self) -> int:
        """Free slots in the current window (a large sentinel when unlimited)."""
        with self._lock:
            if self._rate is None:
                return 10**9
            now = time.monotonic()
            return self._rate - sum(1 for ts in self._timestamps if ts > now - self._window)

    def cooling(self) -> float:
        """Seconds of 429 cooldown remaining (0.0 if none)."""
        with self._lock:
            return max(0.0, self._cooldown_until - time.monotonic())

    def mark_cooldown(self, base_delay: float, retry_after: float | None = None) -> None:
        """Record a 429: cooldown escalates exponentially with consecutive 429s.

        Duration is ``base_delay * 2**(consecutive - 1)`` capped at ``MAX_BACKOFF``;
        a server-provided ``retry_after`` overrides the computed value when larger.
        """
        with self._lock:
            self._consecutive_429s += 1
            duration = min(base_delay * 2 ** (self._consecutive_429s - 1), MAX_BACKOFF)
            if retry_after is not None:
                duration = max(duration, retry_after)
            self._cooldown_until = time.monotonic() + duration

    def note_success(self) -> None:
        """Reset 429 escalation after a successful response."""
        with self._lock:
            self._consecutive_429s = 0


def get_budget(token: str, rate: int | None, window: float) -> _TokenBudget:
    """Return the shared budget for *token*, creating it if needed.

    One registry serves sync and async clients, so a token used from both
    flavors draws from a single budget. Raises ``ValueError`` if a budget
    already exists for *token* with a different ``rate`` or ``window`` —
    callers sharing a token must agree on the config.
    """
    with _registry_lock:
        budget = _budgets.get(token)
        if budget is None:
            budget = _TokenBudget(rate, window, label=token[-4:])
            _budgets[token] = budget
        elif budget._rate != rate or budget._window != window:
            raise ValueError(
                f"Budget for token already exists with rate={budget._rate}, "
                f"window={budget._window}; got rate={rate}, window={window}"
            )
        return budget


class _TokenPool:
    def __init__(self, entries: list[tuple[str, _SyncRateLimiter | _NoOpSyncLimiter]]) -> None:
        self._entries = entries

    def select(self) -> tuple[str, _SyncRateLimiter | _NoOpSyncLimiter] | None:
        """Return the highest-capacity token not in 429 cooldown, or ``None`` if
        every token is cooling down (caller should wait ``cooldown_wait()`` seconds)."""
        eligible = [e for e in self._entries if e[1].cooling() == 0.0]
        if not eligible:
            return None
        caps = [(e, e[1].capacity()) for e in eligible]
        max_cap = max(c for _, c in caps)
        candidates = [e for e, c in caps if c == max_cap]
        return random.choice(candidates)

    def cooldown_wait(self) -> float:
        """Seconds until the soonest token leaves cooldown (0 if any is available now)."""
        cooling = [c for c in (e[1].cooling() for e in self._entries) if c > 0.0]
        return min(cooling) if cooling else 0.0


class _AsyncTokenPool:
    def __init__(self, entries: list[tuple[str, _AsyncRateLimiter | _NoOpAsyncLimiter]]) -> None:
        self._entries = entries

    def select(self) -> tuple[str, _AsyncRateLimiter | _NoOpAsyncLimiter] | None:
        """Return the highest-capacity token not in 429 cooldown, or ``None`` if
        every token is cooling down (caller should wait ``cooldown_wait()`` seconds)."""
        eligible = [e for e in self._entries if e[1].cooling() == 0.0]
        if not eligible:
            return None
        caps = [(e, e[1].capacity()) for e in eligible]
        max_cap = max(c for _, c in caps)
        candidates = [e for e, c in caps if c == max_cap]
        return random.choice(candidates)

    def cooldown_wait(self) -> float:
        """Seconds until the soonest token leaves cooldown (0 if any is available now)."""
        cooling = [c for c in (e[1].cooling() for e in self._entries) if c > 0.0]
        return min(cooling) if cooling else 0.0


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
