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


def test_rate_limiter_acquire_called_before_request(make_client, monkeypatch):
    acquire_calls = []
    client, _ = make_client((200, SUCCESS))
    monkeypatch.setattr(
        client._pool._entries[0][1], "acquire", lambda: acquire_calls.append(1) or 0.0
    )
    client.post("/v2/Race/RaceDetails", raceID=1)
    assert acquire_calls == [1]


def test_rate_limiter_acquire_called_on_each_attempt(make_client, monkeypatch):
    acquire_calls = []
    client, _ = make_client((429, {}), (200, SUCCESS), retry_delay=0)
    monkeypatch.setattr(
        client._pool._entries[0][1], "acquire", lambda: acquire_calls.append(1) or 0.0
    )
    client.post("/v2/Race/RaceDetails", raceID=1)
    assert acquire_calls == [1, 1]


async def test_async_rate_limiter_acquire_called_before_request(make_async_client, monkeypatch):
    acquire_calls = []
    client, _ = make_async_client((200, SUCCESS))

    async def mock_acquire():
        acquire_calls.append(1)
        return 0.0

    monkeypatch.setattr(client._pool._entries[0][1], "acquire", mock_acquire)
    await client.post("/v2/Race/RaceDetails", raceID=1)
    assert acquire_calls == [1]


async def test_async_rate_limiter_acquire_called_on_each_attempt(make_async_client, monkeypatch):
    acquire_calls = []
    client, _ = make_async_client((429, {}), (200, SUCCESS), retry_delay=0)

    async def mock_acquire():
        acquire_calls.append(1)
        return 0.0

    monkeypatch.setattr(client._pool._entries[0][1], "acquire", mock_acquire)
    await client.post("/v2/Race/RaceDetails", raceID=1)
    assert acquire_calls == [1, 1]


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


def test_none_requests_per_minute_builds_noop_limiter():
    from race_monitor import RaceMonitorClient
    from race_monitor._rate_limiter import _NoOpSyncLimiter

    transport = MockTransport((200, {"Successful": True}))
    client = RaceMonitorClient(
        api_token="unlimited-tok", requests_per_minute=None, transport=transport
    )
    _, limiter = client._pool._entries[0]
    assert isinstance(limiter, _NoOpSyncLimiter)


def test_list_with_none_rate_builds_noop_limiters():
    from race_monitor import RaceMonitorClient
    from race_monitor._rate_limiter import _NoOpSyncLimiter

    transport = MockTransport((200, {"Successful": True}))
    client = RaceMonitorClient(
        api_token=["unlimited-a", "unlimited-b"],
        requests_per_minute=None,
        transport=transport,
    )
    for _, limiter in client._pool._entries:
        assert isinstance(limiter, _NoOpSyncLimiter)


def test_post_injects_token_from_pool(make_client, monkeypatch):
    from race_monitor._rate_limiter import _SyncRateLimiter

    client, transport = make_client((200, SUCCESS))
    fake_limiter = _SyncRateLimiter(rate=6, window=60.0)
    monkeypatch.setattr(client._pool, "select", lambda: ("injected-token", fake_limiter))
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
    from race_monitor._rate_limiter import _AsyncRateLimiter

    client, transport = make_async_client((200, SUCCESS))
    fake_limiter = _AsyncRateLimiter(rate=6, window=60.0)

    async def mock_acquire():
        pass

    fake_limiter.acquire = mock_acquire
    monkeypatch.setattr(client._pool, "select", lambda: ("injected-async-token", fake_limiter))
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
