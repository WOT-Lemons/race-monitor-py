import json

import httpx
import pytest

from race_monitor._core import (
    BASE_URL,
    RaceMonitorError,
    RaceMonitorHTTPError,
    _parse_response,
    _retry_after_seconds,
)


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


def test_non_json_200_raises_race_monitor_error():
    response = httpx.Response(200, text="<html>gateway error</html>")
    with pytest.raises(RaceMonitorError, match="Non-JSON"):
        _parse_response(response)


def test_non_json_200_chains_decode_error():
    response = httpx.Response(200, text="not json")
    with pytest.raises(RaceMonitorError) as exc_info:
        _parse_response(response)
    assert isinstance(exc_info.value.__cause__, json.JSONDecodeError)


def test_non_dict_json_200_raises_race_monitor_error():
    response = httpx.Response(200, json=[1, 2, 3])
    with pytest.raises(RaceMonitorError, match="expected object, got list"):
        _parse_response(response)


def test_http_error_includes_body():
    response = httpx.Response(403, text="Account plan does not permit this")
    with pytest.raises(RaceMonitorHTTPError, match="Account plan") as exc_info:
        _parse_response(response)
    assert exc_info.value.status_code == 403
    assert exc_info.value.body == "Account plan does not permit this"


def test_http_error_body_truncated_to_500_chars():
    err = RaceMonitorHTTPError(500, "x" * 2000)
    assert len(err.body) == 500


def test_http_error_message_without_body_unchanged():
    assert str(RaceMonitorHTTPError(500)) == "HTTP 500"


def test_retry_after_seconds_parses_numeric():
    response = httpx.Response(429, headers={"Retry-After": "45"})
    assert _retry_after_seconds(response) == 45.0


def test_retry_after_seconds_none_when_absent():
    response = httpx.Response(429)
    assert _retry_after_seconds(response) is None


def test_retry_after_seconds_none_for_http_date():
    response = httpx.Response(429, headers={"Retry-After": "Wed, 21 Oct 2026 07:28:00 GMT"})
    assert _retry_after_seconds(response) is None
