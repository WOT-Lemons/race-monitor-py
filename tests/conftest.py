import httpx
import pytest


class MockTransport(httpx.BaseTransport):
    """Replays a fixed sequence of (status_code, json_body) responses."""

    def __init__(self, *responses: tuple[int, dict]) -> None:
        self._responses = list(responses)
        self._index = 0
        self._last_request: httpx.Request | None = None

    @property
    def last_request(self) -> httpx.Request:
        if self._last_request is None:
            raise AttributeError("last_request accessed before any request was made")
        return self._last_request

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        self._last_request = request
        if self._index >= len(self._responses):
            raise RuntimeError(
                f"MockTransport exhausted after {len(self._responses)} response(s); "
                f"request {self._index + 1} was not expected: {request.url}"
            )
        status, body = self._responses[self._index]
        self._index += 1
        return httpx.Response(status, json=body)


class AsyncMockTransport(httpx.AsyncBaseTransport):
    """Async version of MockTransport."""

    def __init__(self, *responses: tuple[int, dict]) -> None:
        self._responses = list(responses)
        self._index = 0
        self._last_request: httpx.Request | None = None

    @property
    def last_request(self) -> httpx.Request:
        if self._last_request is None:
            raise AttributeError("last_request accessed before any request was made")
        return self._last_request

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self._last_request = request
        if self._index >= len(self._responses):
            raise RuntimeError(
                f"AsyncMockTransport exhausted after {len(self._responses)} response(s); "
                f"request {self._index + 1} was not expected: {request.url}"
            )
        status, body = self._responses[self._index]
        self._index += 1
        return httpx.Response(status, json=body)


@pytest.fixture(autouse=True)
def _reset_rate_limiters():
    from race_monitor._rate_limiter import _async_limiters, _sync_limiters
    _sync_limiters.clear()
    _async_limiters.clear()
    yield
    _sync_limiters.clear()
    _async_limiters.clear()


@pytest.fixture
def make_client():
    from race_monitor import RaceMonitorClient

    def _make(*responses: tuple[int, dict], retry_delay: float = 0) -> tuple:
        transport = MockTransport(*responses)
        client = RaceMonitorClient(
            api_token="test-token", retry_delay=retry_delay, transport=transport
        )
        return client, transport

    return _make


@pytest.fixture
def make_async_client():
    from race_monitor import AsyncRaceMonitorClient

    def _make(*responses: tuple[int, dict], retry_delay: float = 0) -> tuple:
        transport = AsyncMockTransport(*responses)
        client = AsyncRaceMonitorClient(
            api_token="test-token", retry_delay=retry_delay, transport=transport
        )
        return client, transport

    return _make
