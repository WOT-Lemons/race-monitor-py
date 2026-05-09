import asyncio

import httpx

from ._core import BASE_URL, _parse_response
from ._namespaces.account import AsyncAccountNamespace
from ._namespaces.common import AsyncCommonNamespace
from ._namespaces.live import AsyncLiveNamespace
from ._namespaces.race import AsyncRaceNamespace
from ._namespaces.results import AsyncResultsNamespace


class AsyncRaceMonitorClient:
    """Asynchronous Race Monitor API client.

    Args:
        api_token: Your Race Monitor API token.
        retry_delay: Seconds to wait before retrying a 429 response. Defaults
            to 10s (the developer plan rate limit window).
        **kwargs: Passed through to ``httpx.AsyncClient`` (e.g. ``transport`` for testing).

    Example::

        async with AsyncRaceMonitorClient(api_token="TOKEN") as client:
            if (await client.race.is_live(race_id=12345))["IsLive"]:
                session = await client.live.get_session(race_id=12345)
    """

    def __init__(self, api_token: str, retry_delay: float = 10.0, **kwargs) -> None:
        self._token = api_token
        self._retry_delay = retry_delay
        self._http = httpx.AsyncClient(**kwargs)
        self.account = AsyncAccountNamespace(self._post)
        self.common = AsyncCommonNamespace(self._post)
        self.live = AsyncLiveNamespace(self._post)
        self.race = AsyncRaceNamespace(self._post)
        self.results = AsyncResultsNamespace(self._post)

    async def __aenter__(self) -> "AsyncRaceMonitorClient":
        await self._http.__aenter__()
        return self

    async def __aexit__(self, *args):
        return await self._http.__aexit__(*args)

    async def _post(self, path: str, **kwargs) -> dict:
        data = {"apiToken": self._token, **kwargs}
        while True:
            response = await self._http.post(f"{BASE_URL}{path}", data=data, timeout=30)
            if response.status_code == 429:
                await asyncio.sleep(self._retry_delay)
                continue
            return _parse_response(response)

    async def post(self, path: str, **kwargs) -> dict:
        return await self._post(path, **kwargs)
