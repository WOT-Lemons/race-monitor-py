SUCCESS = {"Successful": True}


def test_app_sections(make_client):
    client, _ = make_client((200, SUCCESS))
    assert client.common.app_sections() == SUCCESS


def test_current_races(make_client):
    client, _ = make_client((200, SUCCESS))
    assert client.common.current_races() == SUCCESS


def test_current_races_with_series(make_client):
    client, transport = make_client((200, SUCCESS))
    client.common.current_races(series_id=5)
    assert b"seriesID=5" in transport.last_request.read()


def test_past_races(make_client):
    client, _ = make_client((200, SUCCESS))
    assert client.common.past_races() == SUCCESS


def test_past_races_with_pagination(make_client):
    client, transport = make_client((200, SUCCESS))
    client.common.past_races(first_result=50, max_results=25)
    body = transport.last_request.read()
    assert b"firstResult=50" in body
    assert b"maxResults=25" in body


def test_race_types(make_client):
    client, _ = make_client((200, SUCCESS))
    assert client.common.race_types() == SUCCESS


def test_time_zones(make_client):
    client, _ = make_client((200, SUCCESS))
    assert client.common.time_zones() == SUCCESS


def test_upcoming_races(make_client):
    client, _ = make_client((200, SUCCESS))
    assert client.common.upcoming_races() == SUCCESS


async def test_async_app_sections(make_async_client):
    client, _ = make_async_client((200, SUCCESS))
    assert await client.common.app_sections() == SUCCESS
