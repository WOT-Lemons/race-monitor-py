import time

import httpx

from ._core import BASE_URL, _parse_response
from ._namespaces.account import AccountNamespace
from ._namespaces.common import CommonNamespace
from ._namespaces.live import LiveNamespace
from ._namespaces.race import RaceNamespace
from ._namespaces.results import ResultsNamespace
from ._rate_limiter import get_sync_limiter


class RaceMonitorClient:
    """Synchronous Race Monitor API client.

    Args:
        api_token: Your Race Monitor API token.
        retry_delay: Seconds to wait before retrying a 429 response. Defaults
            to 10s (the developer plan rate limit window).
        requests_per_minute: Maximum requests per minute, shared across all
            client instances using the same token. Defaults to 6 (developer
            plan limit). Set higher if your plan allows more.
        **kwargs: Passed through to ``httpx.Client`` (e.g. ``transport`` for testing).

    Example::

        with RaceMonitorClient(api_token="TOKEN") as client:
            if client.race.is_live(race_id=12345)["IsLive"]:
                session = client.live.get_session(race_id=12345)
    """

    def __init__(
        self,
        api_token: str,
        retry_delay: float = 10.0,
        requests_per_minute: int = 6,
        **kwargs,
    ) -> None:
        self._token = api_token
        self._retry_delay = retry_delay
        self._limiter = get_sync_limiter(api_token, requests_per_minute, 60.0)
        self._http = httpx.Client(**kwargs)
        self.account = AccountNamespace(self._post)
        self.common = CommonNamespace(self._post)
        self.live = LiveNamespace(self._post)
        self.race = RaceNamespace(self._post)
        self.results = ResultsNamespace(self._post)

    def __enter__(self) -> "RaceMonitorClient":
        self._http.__enter__()
        return self

    def __exit__(self, *args):
        return self._http.__exit__(*args)

    def _post(self, path: str, **kwargs) -> dict:
        data = {"apiToken": self._token, **kwargs}
        while True:
            self._limiter.acquire()
            response = self._http.post(f"{BASE_URL}{path}", data=data, timeout=30)
            if response.status_code == 429:
                time.sleep(self._retry_delay)
                continue
            return _parse_response(response)

    def post(self, path: str, **kwargs) -> dict:
        return self._post(path, **kwargs)
