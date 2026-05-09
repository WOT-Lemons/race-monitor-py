import httpx
import pytest
from race_monitor._core import BASE_URL, RaceMonitorError, RaceMonitorHTTPError, _parse_response


def _make_response(status_code, body):
    return httpx.Response(status_code, json=body)


def test_base_url():
    assert BASE_URL == "https://api.race-monitor.com"


def test_parse_response_success():
    response = _make_response(200, {"Successful": True, "Data": "value"})
    result = _parse_response(response)
    assert result == {"Successful": True, "Data": "value"}


def test_parse_response_api_failure():
    response = _make_response(200, {"Successful": False, "Message": "bad token"})
    with pytest.raises(RaceMonitorError, match="bad token"):
        _parse_response(response)


def test_parse_response_http_403():
    response = _make_response(403, {"Successful": False})
    with pytest.raises(RaceMonitorHTTPError) as exc_info:
        _parse_response(response)
    assert exc_info.value.status_code == 403


def test_parse_response_http_404():
    response = _make_response(404, {"Successful": False})
    with pytest.raises(RaceMonitorHTTPError) as exc_info:
        _parse_response(response)
    assert exc_info.value.status_code == 404


def test_parse_response_http_500():
    response = _make_response(500, {"Successful": False})
    with pytest.raises(RaceMonitorHTTPError) as exc_info:
        _parse_response(response)
    assert exc_info.value.status_code == 500


def test_http_error_is_race_monitor_error():
    response = _make_response(403, {"Successful": False})
    with pytest.raises(RaceMonitorError):
        _parse_response(response)
