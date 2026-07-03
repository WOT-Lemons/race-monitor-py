import asyncio

import httpx
import pytest

from race_monitor import RaceMonitorError, RaceMonitorHTTPError
from tests.conftest import AsyncMockTransport, MockTransport

SUCCESS = {"Successful": True, "Value": 42}
FAILURE = {"Successful": False, "Message": "bad token"}


def test_token_injected_in_post_body(make_client):
    client, transport = make_client((200, SUCCESS))
    client.post("/v2/Race/RaceDetails", raceID=1)
    assert b"apiToken=test-token" in transport.last_request.read()


def test_post_returns_dict_on_success(make_client):
    client, _ = make_client((200, SUCCESS))
    result = client.post("/v2/Race/RaceDetails", raceID=1)
    assert result == SUCCESS


def test_post_raises_on_api_failure(make_client):
    client, _ = make_client((200, FAILURE))
    with pytest.raises(RaceMonitorError, match="bad token"):
        client.post("/v2/Race/RaceDetails", raceID=1)


def test_post_raises_http_error_on_403(make_client):
    client, _ = make_client((403, FAILURE))
    with pytest.raises(RaceMonitorHTTPError) as exc_info:
        client.post("/v2/Race/RaceDetails", raceID=1)
    assert exc_info.value.status_code == 403


def test_post_raises_http_error_on_404(make_client):
    client, _ = make_client((404, FAILURE))
    with pytest.raises(RaceMonitorHTTPError) as exc_info:
        client.post("/v2/Race/RaceDetails", raceID=1)
    assert exc_info.value.status_code == 404


def test_post_raises_http_error_on_500(make_client):
    client, _ = make_client((500, {}))
    with pytest.raises(RaceMonitorHTTPError) as exc_info:
        client.post("/v2/Race/RaceDetails", raceID=1)
    assert exc_info.value.status_code == 500


def test_retry_on_429(make_client):
    client, _ = make_client(
        (429, {}),
        (200, SUCCESS),
        retry_delay=0,
    )
    result = client.post("/v2/Race/RaceDetails", raceID=1)
    assert result == SUCCESS


def test_context_manager(make_client):
    client, _ = make_client((200, SUCCESS))
    with client as c:
        result = c.post("/v2/Race/RaceDetails", raceID=1)
    assert result == SUCCESS


def test_budget_try_acquire_called_before_request(make_client, monkeypatch):
    calls = []
    client, _ = make_client((200, SUCCESS))
    budget = client._pool._entries[0][1]
    monkeypatch.setattr(budget, "try_acquire", lambda: calls.append(1) or 0.0)
    client.post("/v2/Race/RaceDetails", raceID=1)
    assert calls == [1]


def test_budget_try_acquire_called_on_each_attempt(make_client, monkeypatch):
    calls = []
    client, _ = make_client((429, {}), (200, SUCCESS), retry_delay=0)
    budget = client._pool._entries[0][1]
    monkeypatch.setattr(budget, "try_acquire", lambda: calls.append(1) or 0.0)
    client.post("/v2/Race/RaceDetails", raceID=1)
    assert calls == [1, 1]


async def test_async_budget_try_acquire_called_before_request(make_async_client, monkeypatch):
    calls = []
    client, _ = make_async_client((200, SUCCESS))
    budget = client._pool._entries[0][1]
    monkeypatch.setattr(budget, "try_acquire", lambda: calls.append(1) or 0.0)
    await client.post("/v2/Race/RaceDetails", raceID=1)
    assert calls == [1]


async def test_async_budget_try_acquire_called_on_each_attempt(make_async_client, monkeypatch):
    calls = []
    client, _ = make_async_client((429, {}), (200, SUCCESS), retry_delay=0)
    budget = client._pool._entries[0][1]
    monkeypatch.setattr(budget, "try_acquire", lambda: calls.append(1) or 0.0)
    await client.post("/v2/Race/RaceDetails", raceID=1)
    assert calls == [1, 1]


# --- Multi-token constructor ---


def test_str_token_builds_single_entry_pool():
    from race_monitor import RaceMonitorClient

    transport = MockTransport((200, {"Successful": True}))
    client = RaceMonitorClient(api_token="single-tok", requests_per_minute=6, transport=transport)
    assert len(client._pool._entries) == 1
    token, limiter = client._pool._entries[0]
    assert token == "single-tok"
    assert limiter._rate == 6


def test_list_token_builds_multi_entry_pool():
    from race_monitor import RaceMonitorClient

    transport = MockTransport((200, {"Successful": True}))
    client = RaceMonitorClient(
        api_token=["list-tok-a", "list-tok-b"],
        requests_per_minute=6,
        transport=transport,
    )
    assert len(client._pool._entries) == 2
    tokens = {t for t, _ in client._pool._entries}
    assert tokens == {"list-tok-a", "list-tok-b"}
    for _, limiter in client._pool._entries:
        assert limiter._rate == 6


def test_dict_token_builds_pool_with_per_token_rates():
    from race_monitor import RaceMonitorClient

    transport = MockTransport((200, {"Successful": True}))
    client = RaceMonitorClient(
        api_token={"dict-tok-a": 6, "dict-tok-b": 10},
        transport=transport,
    )
    assert len(client._pool._entries) == 2
    rates = {t: lim._rate for t, lim in client._pool._entries}
    assert rates["dict-tok-a"] == 6
    assert rates["dict-tok-b"] == 10


def test_empty_dict_raises():
    from race_monitor import RaceMonitorClient

    transport = MockTransport()
    with pytest.raises(ValueError, match="at least one token"):
        RaceMonitorClient(api_token={}, transport=transport)


def test_empty_list_raises():
    from race_monitor import RaceMonitorClient

    transport = MockTransport()
    with pytest.raises(ValueError, match="at least one token"):
        RaceMonitorClient(api_token=[], transport=transport)


def test_none_requests_per_minute_builds_unlimited_budget():
    from race_monitor import RaceMonitorClient

    transport = MockTransport((200, {"Successful": True}))
    client = RaceMonitorClient(
        api_token="unlimited-tok", requests_per_minute=None, transport=transport
    )
    _, budget = client._pool._entries[0]
    assert budget._rate is None


def test_list_with_none_rate_builds_unlimited_budgets():
    from race_monitor import RaceMonitorClient

    transport = MockTransport((200, {"Successful": True}))
    client = RaceMonitorClient(
        api_token=["unlimited-a", "unlimited-b"],
        requests_per_minute=None,
        transport=transport,
    )
    for _, budget in client._pool._entries:
        assert budget._rate is None


def test_post_injects_token_from_pool(make_client, monkeypatch):
    from race_monitor._rate_limiter import _TokenBudget

    client, transport = make_client((200, SUCCESS))
    fake_budget = _TokenBudget(rate=6, window=60.0)
    monkeypatch.setattr(client._pool, "try_acquire", lambda: ("injected-token", fake_budget))
    client.post("/v2/Race/RaceDetails", raceID=1)
    assert b"apiToken=injected-token" in transport.last_request.read()


# --- Async multi-token constructor ---


async def test_async_str_token_builds_single_entry_pool():
    from race_monitor import AsyncRaceMonitorClient

    transport = AsyncMockTransport((200, {"Successful": True}))
    client = AsyncRaceMonitorClient(
        api_token="async-single-tok", requests_per_minute=6, transport=transport
    )
    assert len(client._pool._entries) == 1
    token, limiter = client._pool._entries[0]
    assert token == "async-single-tok"
    assert limiter._rate == 6


async def test_async_list_token_builds_multi_entry_pool():
    from race_monitor import AsyncRaceMonitorClient

    transport = AsyncMockTransport((200, {"Successful": True}))
    client = AsyncRaceMonitorClient(
        api_token=["async-list-a", "async-list-b"],
        requests_per_minute=6,
        transport=transport,
    )
    assert len(client._pool._entries) == 2
    tokens = {t for t, _ in client._pool._entries}
    assert tokens == {"async-list-a", "async-list-b"}


async def test_async_dict_token_builds_pool_with_per_token_rates():
    from race_monitor import AsyncRaceMonitorClient

    transport = AsyncMockTransport((200, {"Successful": True}))
    client = AsyncRaceMonitorClient(
        api_token={"async-dict-a": 6, "async-dict-b": 10},
        transport=transport,
    )
    rates = {t: lim._rate for t, lim in client._pool._entries}
    assert rates["async-dict-a"] == 6
    assert rates["async-dict-b"] == 10


async def test_async_empty_dict_raises():
    from race_monitor import AsyncRaceMonitorClient

    transport = AsyncMockTransport()
    with pytest.raises(ValueError, match="at least one token"):
        AsyncRaceMonitorClient(api_token={}, transport=transport)


async def test_async_post_injects_token_from_pool(make_async_client, monkeypatch):
    from race_monitor._rate_limiter import _TokenBudget

    client, transport = make_async_client((200, SUCCESS))
    fake_budget = _TokenBudget(rate=6, window=60.0)
    monkeypatch.setattr(client._pool, "try_acquire", lambda: ("injected-async-token", fake_budget))
    await client.post("/v2/Race/RaceDetails", raceID=1)
    assert b"apiToken=injected-async-token" in transport.last_request.read()


# --- 429 slot release ---


def test_429_does_not_consume_limiter_slot(make_client):
    client, _ = make_client((429, {}), (200, SUCCESS), retry_delay=0)
    limiter = client._pool._entries[0][1]
    initial_capacity = limiter.capacity()
    client.post("/v2/Race/RaceDetails", raceID=1)
    assert limiter.capacity() == initial_capacity - 1


async def test_async_429_does_not_consume_limiter_slot(make_async_client):
    client, _ = make_async_client((429, {}), (200, SUCCESS), retry_delay=0)
    limiter = client._pool._entries[0][1]
    initial_capacity = limiter.capacity()
    await client.post("/v2/Race/RaceDetails", raceID=1)
    assert limiter.capacity() == initial_capacity - 1


# --- 429 rotates to a different token ---


class _RecordingTransport(httpx.BaseTransport):
    """Records which apiToken each request carried; replays a status sequence."""

    def __init__(self, *statuses: int) -> None:
        self._statuses = list(statuses)
        self._index = 0
        self.tokens_used: list[str] = []

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        body = request.read().decode()
        self.tokens_used.append("AAAA" if "apiToken=AAAA" in body else "BBBB")
        status = self._statuses[self._index]
        self._index += 1
        return httpx.Response(status, json=SUCCESS if status == 200 else {})


class _AsyncRecordingTransport(httpx.AsyncBaseTransport):
    def __init__(self, *statuses: int) -> None:
        self._statuses = list(statuses)
        self._index = 0
        self.tokens_used: list[str] = []

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        body = request.read().decode()
        self.tokens_used.append("AAAA" if "apiToken=AAAA" in body else "BBBB")
        status = self._statuses[self._index]
        self._index += 1
        return httpx.Response(status, json=SUCCESS if status == 200 else {})


def test_429_rotates_to_other_token(monkeypatch):
    from race_monitor import RaceMonitorClient

    # Make selection deterministic: always take the first eligible candidate.
    monkeypatch.setattr("race_monitor._rate_limiter.random.choice", lambda seq: seq[0])
    monkeypatch.setattr("race_monitor.client.time.sleep", lambda secs: None)
    transport = _RecordingTransport(429, 200)
    client = RaceMonitorClient(
        api_token=["AAAA", "BBBB"], retry_delay=60, transport=transport
    )
    result = client.post("/v2/Race/RaceDetails", raceID=1)
    assert result == SUCCESS
    # First attempt 429'd on AAAA; the retry must switch to BBBB, not reuse AAAA.
    assert transport.tokens_used == ["AAAA", "BBBB"]


async def test_async_429_rotates_to_other_token(monkeypatch):
    from race_monitor import AsyncRaceMonitorClient

    async def _noop_sleep(secs):
        return None

    monkeypatch.setattr("race_monitor._rate_limiter.random.choice", lambda seq: seq[0])
    monkeypatch.setattr("race_monitor.async_client.asyncio.sleep", _noop_sleep)
    transport = _AsyncRecordingTransport(429, 200)
    client = AsyncRaceMonitorClient(
        api_token=["AAAA", "BBBB"], retry_delay=60, transport=transport
    )
    result = await client.post("/v2/Race/RaceDetails", raceID=1)
    assert result == SUCCESS
    assert transport.tokens_used == ["AAAA", "BBBB"]


def test_429_on_unlimited_token_backs_off(monkeypatch):
    """An unlimited (rate=None) token must still sleep on 429, not hot-loop."""
    from race_monitor import RaceMonitorClient

    # Fake clock so the mocked sleep advances time past the cooldown.
    clock = [1000.0]
    monkeypatch.setattr("race_monitor._rate_limiter.time.monotonic", lambda: clock[0])
    sleeps: list[float] = []

    def _sleep(secs):
        sleeps.append(secs)
        clock[0] += secs

    monkeypatch.setattr("race_monitor.client.time.sleep", _sleep)
    transport = _RecordingTransport(429, 200)
    client = RaceMonitorClient(
        api_token={"AAAA": None}, retry_delay=60, transport=transport
    )
    result = client.post("/v2/Race/RaceDetails", raceID=1)
    assert result == SUCCESS
    # The 429 must trigger a single backoff sleep before the retry succeeds.
    assert sleeps == [pytest.approx(60.0, abs=0.5)]


async def test_async_429_on_unlimited_token_backs_off(monkeypatch):
    from race_monitor import AsyncRaceMonitorClient

    clock = [1000.0]
    monkeypatch.setattr("race_monitor._rate_limiter.time.monotonic", lambda: clock[0])
    sleeps: list[float] = []

    async def _sleep(secs):
        sleeps.append(secs)
        clock[0] += secs

    monkeypatch.setattr("race_monitor.async_client.asyncio.sleep", _sleep)
    transport = _AsyncRecordingTransport(429, 200)
    client = AsyncRaceMonitorClient(
        api_token={"AAAA": None}, retry_delay=60, transport=transport
    )
    result = await client.post("/v2/Race/RaceDetails", raceID=1)
    assert result == SUCCESS
    assert sleeps == [pytest.approx(60.0, abs=0.5)]


# --- max_retries / Retry-After / lifecycle / timeout ---


class _RetryAfterTransport(httpx.BaseTransport):
    """First request 429s with a Retry-After header; second succeeds."""

    def __init__(self) -> None:
        self.requests = 0

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        self.requests += 1
        if self.requests == 1:
            return httpx.Response(429, headers={"Retry-After": "45"}, json={})
        return httpx.Response(200, json=SUCCESS)


def test_max_retries_exhaustion_raises_429(make_client):
    client, transport = make_client(*[(429, {})] * 3, retry_delay=0, max_retries=2)
    with pytest.raises(RaceMonitorHTTPError) as exc_info:
        client.post("/v2/Race/RaceDetails", raceID=1)
    assert exc_info.value.status_code == 429
    # initial attempt + 2 retries = exactly 3 requests, then give up
    assert transport._index == 3


def test_max_retries_not_exhausted_by_eventual_success(make_client):
    client, _ = make_client((429, {}), (429, {}), (200, SUCCESS), retry_delay=0, max_retries=2)
    assert client.post("/v2/Race/RaceDetails", raceID=1) == SUCCESS


def test_retry_after_header_extends_cooldown(monkeypatch):
    from race_monitor import RaceMonitorClient

    clock = [0.0]
    monkeypatch.setattr("race_monitor._rate_limiter.time.monotonic", lambda: clock[0])
    sleeps: list[float] = []

    def _sleep(secs):
        sleeps.append(secs)
        clock[0] += secs

    monkeypatch.setattr("race_monitor.client.time.sleep", _sleep)
    client = RaceMonitorClient(
        api_token="retry-after-tok", retry_delay=10, transport=_RetryAfterTransport()
    )
    result = client.post("/v2/Race/RaceDetails", raceID=1)
    assert result == SUCCESS
    # Retry-After: 45 beats the computed 10s first-429 cooldown.
    assert sleeps == [pytest.approx(45.0)]


def test_success_resets_backoff_escalation(make_client):
    client, _ = make_client((429, {}), (200, SUCCESS), retry_delay=0)
    client.post("/v2/Race/RaceDetails", raceID=1)
    assert client._pool._entries[0][1]._consecutive_429s == 0


def test_error_response_does_not_reset_backoff_escalation(make_client):
    # A 429 escalates the counter; a following non-429 error response is not a
    # success, so it must not reset the escalation (note_success runs only after
    # _parse_response confirms a genuine success).
    client, _ = make_client((429, {}), (500, {}), retry_delay=0)
    with pytest.raises(RaceMonitorHTTPError):
        client.post("/v2/Race/RaceDetails", raceID=1)
    assert client._pool._entries[0][1]._consecutive_429s == 1


def test_unsuccessful_200_does_not_reset_backoff_escalation(make_client):
    # A 200 body with Successful=False makes _parse_response raise; escalation
    # from a prior 429 must survive because no genuine success occurred.
    client, _ = make_client((429, {}), (200, FAILURE), retry_delay=0)
    with pytest.raises(RaceMonitorError, match="bad token"):
        client.post("/v2/Race/RaceDetails", raceID=1)
    assert client._pool._entries[0][1]._consecutive_429s == 1


def test_close_closes_http_client(make_client):
    client, _ = make_client()
    client.close()
    assert client._http.is_closed


def test_default_timeout_is_30s():
    from race_monitor import RaceMonitorClient

    client = RaceMonitorClient(api_token="timeout-default-tok", transport=MockTransport())
    assert client._http.timeout == httpx.Timeout(30)


def test_user_timeout_overrides_default():
    from race_monitor import RaceMonitorClient

    client = RaceMonitorClient(
        api_token="timeout-custom-tok", timeout=httpx.Timeout(60), transport=MockTransport()
    )
    assert client._http.timeout == httpx.Timeout(60)


# --- async: error paths, lifecycle, loop reuse, shared budgets ---


async def test_async_post_raises_on_api_failure(make_async_client):
    client, _ = make_async_client((200, FAILURE))
    with pytest.raises(RaceMonitorError, match="bad token"):
        await client.post("/v2/Race/RaceDetails", raceID=1)


async def test_async_post_raises_http_error_on_403(make_async_client):
    client, _ = make_async_client((403, FAILURE))
    with pytest.raises(RaceMonitorHTTPError) as exc_info:
        await client.post("/v2/Race/RaceDetails", raceID=1)
    assert exc_info.value.status_code == 403


async def test_async_max_retries_exhaustion_raises_429(make_async_client):
    client, transport = make_async_client(*[(429, {})] * 3, retry_delay=0, max_retries=2)
    with pytest.raises(RaceMonitorHTTPError) as exc_info:
        await client.post("/v2/Race/RaceDetails", raceID=1)
    assert exc_info.value.status_code == 429
    assert transport._index == 3


async def test_aclose_closes_http_client(make_async_client):
    client, _ = make_async_client()
    await client.aclose()
    assert client._http.is_closed


async def test_async_user_timeout_overrides_default():
    from race_monitor import AsyncRaceMonitorClient

    client = AsyncRaceMonitorClient(
        api_token="async-timeout-tok", timeout=httpx.Timeout(60), transport=AsyncMockTransport()
    )
    assert client._http.timeout == httpx.Timeout(60)


def test_async_client_survives_multiple_event_loops():
    """Regression: budgets hold no event-loop-bound state (old asyncio.Lock bug)."""
    from race_monitor import AsyncRaceMonitorClient

    async def use_client():
        transport = AsyncMockTransport((200, SUCCESS))
        client = AsyncRaceMonitorClient(api_token="loop-reuse-tok", transport=transport)
        result = await client.post("/v2/Race/RaceDetails", raceID=1)
        await client.aclose()
        return result

    assert asyncio.run(use_client()) == SUCCESS
    assert asyncio.run(use_client()) == SUCCESS


async def test_sync_and_async_clients_share_budget():
    """One token used from both client flavors draws from a single budget."""
    from race_monitor import AsyncRaceMonitorClient, RaceMonitorClient

    sync_client = RaceMonitorClient(
        api_token="cross-flavor-tok",
        requests_per_minute=2,
        transport=MockTransport((200, SUCCESS)),
    )
    async_client = AsyncRaceMonitorClient(
        api_token="cross-flavor-tok",
        requests_per_minute=2,
        transport=AsyncMockTransport((200, SUCCESS)),
    )
    assert sync_client._pool._entries[0][1] is async_client._pool._entries[0][1]
    sync_client.post("/v2/Race/RaceDetails", raceID=1)
    # The sync call consumed one of the 2 shared slots.
    assert async_client._pool._entries[0][1].capacity() == 1
