import logging
import random
import threading
import time
from collections import deque

_logger = logging.getLogger(__name__)
_budgets: dict[str, "_TokenBudget"] = {}
_registry_lock = threading.Lock()

MAX_BACKOFF = 120.0


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


class _BudgetPool:
    """The set of token budgets a client draws from."""

    def __init__(self, entries: list[tuple[str, _TokenBudget]]) -> None:
        self._entries = entries

    def select(self) -> tuple[str, _TokenBudget] | None:
        """Return the highest-capacity token not in 429 cooldown, or ``None``."""
        eligible = [e for e in self._entries if e[1].cooling() == 0.0]
        if not eligible:
            return None
        caps = [(e, e[1].capacity()) for e in eligible]
        max_cap = max(c for _, c in caps)
        candidates = [e for e, c in caps if c == max_cap]
        return random.choice(candidates)

    def try_acquire(self) -> tuple[str, _TokenBudget] | None:
        """One non-blocking acquisition attempt: select a token, then take a slot.

        Returns ``(token, budget)`` on success, or ``None`` when nothing is
        available right now — including when the selected token refuses because
        it entered cooldown or filled up between selection and acquisition.
        Callers loop: sleep ``wait_time()`` seconds, then try again.
        """
        selected = self.select()
        if selected is None:
            return None
        token, budget = selected
        if budget.try_acquire() == 0.0:
            return token, budget
        return None

    def wait_time(self) -> float:
        """Seconds until the soonest budget could accept a request."""
        return min(b.next_available() for _, b in self._entries)


def get_pool(token_rates: dict[str, int | None], window: float) -> _BudgetPool:
    """Build a pool of shared per-token budgets (one registry for sync and async)."""
    return _BudgetPool([(t, get_budget(t, r, window)) for t, r in token_rates.items()])
