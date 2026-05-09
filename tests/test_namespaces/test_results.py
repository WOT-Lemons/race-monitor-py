SUCCESS = {"Successful": True}


def test_sessions_for_race(make_client):
    client, transport = make_client((200, SUCCESS))
    client.results.sessions_for_race(race_id=1)
    assert b"raceID=1" in transport.last_request.read()


def test_sessions_for_race_with_device(make_client):
    client, transport = make_client((200, SUCCESS))
    client.results.sessions_for_race(race_id=1, device_id="abc")
    body = transport.last_request.read()
    assert b"raceID=1" in body
    assert b"deviceID=abc" in body


def test_session_details_with_laps(make_client):
    client, transport = make_client((200, SUCCESS))
    client.results.session_details(session_id=99, include_lap_times=True)
    body = transport.last_request.read()
    assert b"sessionID=99" in body
    assert b"includeLapTimes=true" in body


def test_session_details_without_laps(make_client):
    client, transport = make_client((200, SUCCESS))
    client.results.session_details(session_id=99, include_lap_times=False)
    assert b"includeLapTimes=false" in transport.last_request.read()


def test_recent_results(make_client):
    client, _ = make_client((200, SUCCESS))
    assert client.results.recent_results() == SUCCESS


def test_recent_results_with_params(make_client):
    client, transport = make_client((200, SUCCESS))
    client.results.recent_results(app_section_id=3, past_days=14)
    body = transport.last_request.read()
    assert b"appSectionID=3" in body
    assert b"pastDays=14" in body


def test_grouped_sessions_for_race(make_client):
    client, transport = make_client((200, SUCCESS))
    client.results.grouped_sessions_for_race(race_id=1)
    assert b"raceID=1" in transport.last_request.read()


def test_grouped_sessions_force_standard(make_client):
    client, transport = make_client((200, SUCCESS))
    client.results.grouped_sessions_for_race(race_id=1, force_standard_behavior=True)
    assert b"forceStandardBehavior=true" in transport.last_request.read()


def test_competitor_details(make_client):
    client, transport = make_client((200, SUCCESS))
    client.results.competitor_details(competitor_id=5)
    assert b"competitorID=5" in transport.last_request.read()


def test_competitors_with_transponder(make_client):
    client, transport = make_client((200, SUCCESS))
    client.results.competitors_with_transponder(transponder="12345")
    assert b"transponder=12345" in transport.last_request.read()


def test_racer_results_for_race(make_client):
    client, transport = make_client((200, SUCCESS))
    client.results.racer_results_for_race(race_id=1, transponder="ABC", last_name="Smith")
    body = transport.last_request.read()
    assert b"raceID=1" in body
    assert b"transponder=ABC" in body
    assert b"lastName=Smith" in body


def test_races_with_transponder(make_client):
    client, transport = make_client((200, SUCCESS))
    client.results.races_with_transponder(transponder="ABC", last_name="Smith")
    body = transport.last_request.read()
    assert b"transponder=ABC" in body
    assert b"lastName=Smith" in body


def test_search_results(make_client):
    client, transport = make_client((200, SUCCESS))
    client.results.search_results(search_term="lemons")
    assert b"searchTerm=lemons" in transport.last_request.read()


def test_search_results_with_app_section_id(make_client):
    client, transport = make_client((200, SUCCESS))
    client.results.search_results(search_term="lemons", app_section_id=3)
    body = transport.last_request.read()
    assert b"searchTerm=lemons" in body
    assert b"appSectionID=3" in body


def test_sessions_in_date_range(make_client):
    client, transport = make_client((200, SUCCESS))
    client.results.sessions_in_date_range_for_race(
        race_id=1, start_date_epoc=1000, end_date_epoc=2000)
    body = transport.last_request.read()
    assert b"raceID=1" in body
    assert b"startDateEpoc=1000" in body
    assert b"endDateEpoc=2000" in body


async def test_async_sessions_for_race(make_async_client):
    client, _ = make_async_client((200, SUCCESS))
    result = await client.results.sessions_for_race(race_id=1)
    assert result == SUCCESS


async def test_async_session_details(make_async_client):
    client, _ = make_async_client((200, SUCCESS))
    result = await client.results.session_details(session_id=99, include_lap_times=True)
    assert result == SUCCESS
