import pytest
from race_monitor import RaceMonitorError, RaceMonitorHTTPError

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
    monkeypatch.setattr(client._limiter, "acquire", lambda: acquire_calls.append(1))
    client.post("/v2/Race/RaceDetails", raceID=1)
    assert acquire_calls == [1]


def test_rate_limiter_acquire_called_on_each_attempt(make_client, monkeypatch):
    acquire_calls = []
    client, _ = make_client((429, {}), (200, SUCCESS), retry_delay=0)
    monkeypatch.setattr(client._limiter, "acquire", lambda: acquire_calls.append(1))
    client.post("/v2/Race/RaceDetails", raceID=1)
    assert acquire_calls == [1, 1]


async def test_async_rate_limiter_acquire_called_before_request(make_async_client, monkeypatch):
    acquire_calls = []
    client, _ = make_async_client((200, SUCCESS))

    async def mock_acquire():
        acquire_calls.append(1)

    monkeypatch.setattr(client._limiter, "acquire", mock_acquire)
    await client.post("/v2/Race/RaceDetails", raceID=1)
    assert acquire_calls == [1]


async def test_async_rate_limiter_acquire_called_on_each_attempt(make_async_client, monkeypatch):
    acquire_calls = []
    client, _ = make_async_client((429, {}), (200, SUCCESS), retry_delay=0)

    async def mock_acquire():
        acquire_calls.append(1)

    monkeypatch.setattr(client._limiter, "acquire", mock_acquire)
    await client.post("/v2/Race/RaceDetails", raceID=1)
    assert acquire_calls == [1, 1]
