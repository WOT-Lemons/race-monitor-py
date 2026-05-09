SUCCESS_DETAILS = {"Successful": True, "Race": {"Name": "24 Hours of Lemons"}}
SUCCESS_LIVE = {"Successful": True, "IsLive": True}


def test_race_details(make_client):
    client, transport = make_client((200, SUCCESS_DETAILS))
    result = client.race.details(race_id=12345)
    assert result == SUCCESS_DETAILS
    assert b"raceID=12345" in transport.last_request.read()


def test_race_is_live(make_client):
    client, transport = make_client((200, SUCCESS_LIVE))
    result = client.race.is_live(race_id=12345)
    assert result == SUCCESS_LIVE
    assert b"raceID=12345" in transport.last_request.read()


async def test_async_race_details(make_async_client):
    client, transport = make_async_client((200, SUCCESS_DETAILS))
    result = await client.race.details(race_id=12345)
    assert result == SUCCESS_DETAILS


async def test_async_race_is_live(make_async_client):
    client, transport = make_async_client((200, SUCCESS_LIVE))
    result = await client.race.is_live(race_id=12345)
    assert result == SUCCESS_LIVE
