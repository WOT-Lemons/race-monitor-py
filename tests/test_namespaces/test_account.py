SUCCESS = {"Successful": True}


def test_all_races(make_client):
    client, _ = make_client((200, SUCCESS))
    assert client.account.all_races() == SUCCESS


def test_all_races_with_filter(make_client):
    client, transport = make_client((200, SUCCESS))
    client.account.all_races(series_id=3, race_type_id=2)
    body = transport.last_request.read()
    assert b"seriesID=3" in body
    assert b"raceTypeID=2" in body


def test_current_races(make_client):
    client, _ = make_client((200, SUCCESS))
    assert client.account.current_races() == SUCCESS


def test_past_races(make_client):
    client, _ = make_client((200, SUCCESS))
    assert client.account.past_races() == SUCCESS


def test_series(make_client):
    client, _ = make_client((200, SUCCESS))
    assert client.account.series() == SUCCESS


def test_upcoming_races(make_client):
    client, _ = make_client((200, SUCCESS))
    assert client.account.upcoming_races() == SUCCESS


async def test_async_all_races(make_async_client):
    client, _ = make_async_client((200, SUCCESS))
    assert await client.account.all_races() == SUCCESS
