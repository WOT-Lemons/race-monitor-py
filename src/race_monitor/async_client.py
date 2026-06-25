"""Asynchronous Race Monitor API client."""

import asyncio
from typing import Any

import httpx

from ._core import BASE_URL, _parse_response
from ._namespaces.account import AsyncAccountNamespace
from ._namespaces.common import AsyncCommonNamespace
from ._namespaces.live import AsyncLiveNamespace
from ._namespaces.race import AsyncRaceNamespace
from ._namespaces.results import AsyncResultsNamespace
from ._rate_limiter import get_async_pool


class AsyncRaceMonitorClient:
    """Asynchronous Race Monitor API client.

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
        **kwargs: Passed through to ``httpx.AsyncClient`` (e.g. ``transport`` for testing).

    Example::

        async with AsyncRaceMonitorClient(api_token="TOKEN") as client:
            if (await client.race.is_live(race_id=12345))["IsLive"]:
                session = await client.live.get_session(race_id=12345)

        # Two tokens, double the rate limit:
        async with AsyncRaceMonitorClient(api_token=["TOKEN1", "TOKEN2"]) as client:
            session = await client.live.get_session(race_id=12345)
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
        self._pool = get_async_pool(token_rates, 60.0)
        self._retry_delay = retry_delay
        self._http = httpx.AsyncClient(**kwargs)
        self.account = AsyncAccountNamespace(self._post)
        self.common = AsyncCommonNamespace(self._post)
        self.live = AsyncLiveNamespace(self._post)
        self.race = AsyncRaceNamespace(self._post)
        self.results = AsyncResultsNamespace(self._post)

    async def __aenter__(self) -> "AsyncRaceMonitorClient":
        """Enter the async context manager."""
        await self._http.__aenter__()
        return self

    async def __aexit__(self, *args):
        """Exit the async context manager."""
        return await self._http.__aexit__(*args)

    async def _post(self, path: str, **kwargs) -> dict[str, Any]:
        """POST to the API, selecting the least-loaded token and retrying on 429."""
        while True:
            token, limiter = self._pool.select()
            await limiter.acquire()
            data = {"apiToken": token, **kwargs}
            response = await self._http.post(f"{BASE_URL}{path}", data=data, timeout=30)
            if response.status_code == 429:
                limiter.release()
                await asyncio.sleep(self._retry_delay)
                continue
            return _parse_response(response)

    async def post(self, path: str, **kwargs) -> dict[str, Any]:
        """Make a POST request to the given API path."""
        return await self._post(path, **kwargs)
