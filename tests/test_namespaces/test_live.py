SUCCESS = {"Successful": True}


def test_get_racer(make_client):
    client, transport = make_client((200, SUCCESS))
    client.live.get_racer(race_id=1, racer_id=42)
    body = transport.last_request.read()
    assert b"raceID=1" in body
    assert b"racerID=42" in body


def test_get_racer_count(make_client):
    client, transport = make_client((200, SUCCESS))
    client.live.get_racer_count(race_id=1)
    assert b"raceID=1" in transport.last_request.read()


def test_get_session(make_client):
    client, transport = make_client((200, SUCCESS))
    client.live.get_session(race_id=1)
    assert b"raceID=1" in transport.last_request.read()


def test_get_streaming_connection_default(make_client):
    client, transport = make_client((200, SUCCESS))
    client.live.get_streaming_connection(race_id=1)
    body = transport.last_request.read()
    assert b"raceID=1" in body
    assert b"useHostNameForSocket=false" in body


def test_get_streaming_connection_with_hostname(make_client):
    client, transport = make_client((200, SUCCESS))
    client.live.get_streaming_connection(race_id=1, use_host_name_for_socket=True)
    assert b"useHostNameForSocket=true" in transport.last_request.read()


def test_get_web_timing(make_client):
    client, transport = make_client((200, SUCCESS))
    client.live.get_web_timing(source_mode="race", source_mode_value=12345)
    body = transport.last_request.read()
    assert b"sourceMode=race" in body
    assert b"sourceModeValue=12345" in body


def test_get_web_timing_custom_layout(make_client):
    client, transport = make_client((200, SUCCESS))
    client.live.get_web_timing(source_mode="series", source_mode_value=7, layout="wide")
    assert b"layout=wide" in transport.last_request.read()


async def test_async_get_session(make_async_client):
    client, _ = make_async_client((200, SUCCESS))
    result = await client.live.get_session(race_id=1)
    assert result == SUCCESS


async def test_async_get_racer(make_async_client):
    client, _ = make_async_client((200, SUCCESS))
    result = await client.live.get_racer(race_id=1, racer_id=42)
    assert result == SUCCESS
