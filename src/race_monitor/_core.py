"""Shared constants, exceptions, and response parsing for the Race Monitor clients."""

import json

import httpx

BASE_URL = "https://api.race-monitor.com"


class RaceMonitorError(Exception):
    """Base error for Race Monitor API failures."""


class RaceMonitorHTTPError(RaceMonitorError):
    """Non-200 HTTP response from the API.

    Attributes:
        status_code: The HTTP status code.
        body: The response body text, truncated to 500 characters ("" if empty).
    """

    def __init__(self, status_code: int, body: str = "") -> None:
        self.status_code = status_code
        self.body = body[:500]
        message = f"HTTP {status_code}"
        if self.body:
            message = f"{message}: {self.body}"
        super().__init__(message)


def _retry_after_seconds(response: httpx.Response) -> float | None:
    """Parse a Retry-After header in seconds form; ``None`` if absent or unparseable."""
    value = response.headers.get("Retry-After")
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:  # HTTP-date form — not worth parsing for this API
        return None


def _parse_response(response: httpx.Response) -> dict:
    """Parse an API response, raising within the RaceMonitorError hierarchy on failure."""
    if response.status_code == 200:
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise RaceMonitorError(
                f"Non-JSON 200 response from API: {response.text[:200]!r}"
            ) from e
        if not isinstance(data, dict):
            raise RaceMonitorError(
                f"Unexpected JSON response type: expected object, got {type(data).__name__}"
            )
        if not data.get("Successful"):
            raise RaceMonitorError(data.get("Message", "Request unsuccessful"))
        return data
    raise RaceMonitorHTTPError(response.status_code, response.text)
