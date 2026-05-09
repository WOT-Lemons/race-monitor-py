import httpx

BASE_URL = "https://api.race-monitor.com"


class RaceMonitorError(Exception):
    pass


class RaceMonitorHTTPError(RaceMonitorError):
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}")


def _parse_response(response: httpx.Response) -> dict:
    if response.status_code == 200:
        data = response.json()
        if not data.get("Successful"):
            raise RaceMonitorError(data.get("Message", "Request unsuccessful"))
        return data
    raise RaceMonitorHTTPError(response.status_code)
