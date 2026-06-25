"""Synchronous Race Monitor API client."""

import time
from typing import Any

import httpx

from ._core import BASE_URL, _parse_response
from ._namespaces.account import AccountNamespace
from ._namespaces.common import CommonNamespace
from ._namespaces.live import LiveNamespace
from ._namespaces.race import RaceNamespace
from ._namespaces.results import ResultsNamespace
from ._rate_limiter import get_sync_pool


class RaceMonitorClient:
    """Synchronous Race Monitor API client.

    Args:
        api_token: Your Race Monitor API token(s). Accepts:
            - ``str``: single token, uses ``requests_per_minute`` as its rate.
            - ``list[str]``: multiple tokens, all using ``requests_per_minute``.
            - ``dict[str, int]``: maps each token to its own requests-per-minute
              limit; ``requests_per_minute`` is ignored.
        retry_delay: Seconds to wait before retrying a 429 response. Defaults
            to 10s (the developer plan rate limit window).
        requests_per_minute: Maximum requests per minute for ``str`` and
            ``list[str]`` inputs. Defaults to 6 (developer plan limit).
        **kwargs: Passed through to ``httpx.Client`` (e.g. ``transport`` for testing).

    Example::

        with RaceMonitorClient(api_token="TOKEN") as client:
            if client.race.is_live(race_id=12345)["IsLive"]:
                session = client.live.get_session(race_id=12345)

        # Two tokens, double the rate limit:
        with RaceMonitorClient(api_token=["TOKEN1", "TOKEN2"]) as client:
            session = client.live.get_session(race_id=12345)
    """

    def __init__(
        self,
        api_token: str | list[str] | dict[str, int | None],
        retry_delay: float = 10.0,
        requests_per_minute: int | None = 6,
        **kwargs,
    ) -> None:
        """Initialize the client. See class docstring for parameter details."""
        if isinstance(api_token, str):
            token_rates = {api_token: requests_per_minute}
        elif isinstance(api_token, list):
            if not api_token:
                raise ValueError("api_token list must contain at least one token")
            token_rates = {t: requests_per_minute for t in api_token}
        else:
            if not api_token:
                raise ValueError("api_token dict must contain at least one token")
            token_rates = api_token
        self._pool = get_sync_pool(token_rates, 60.0)
        self._retry_delay = retry_delay
        self._http = httpx.Client(**kwargs)
        self.account = AccountNamespace(self._post)
        self.common = CommonNamespace(self._post)
        self.live = LiveNamespace(self._post)
        self.race = RaceNamespace(self._post)
        self.results = ResultsNamespace(self._post)

    def __enter__(self) -> "RaceMonitorClient":
        """Enter the context manager."""
        self._http.__enter__()
        return self

    def __exit__(self, *args):
        """Exit the context manager."""
        return self._http.__exit__(*args)

    def _post(self, path: str, **kwargs) -> dict[str, Any]:
        """POST to the API, selecting the least-loaded token and retrying on 429."""
        while True:
            token, limiter = self._pool.select()
            limiter.acquire()
            data = {"apiToken": token, **kwargs}
            response = self._http.post(f"{BASE_URL}{path}", data=data, timeout=30)
            if response.status_code == 429:
                time.sleep(self._retry_delay)
                continue
            return _parse_response(response)

    def post(self, path: str, **kwargs) -> dict[str, Any]:
        """Make a POST request to the given API path."""
        return self._post(path, **kwargs)
