import asyncio

import httpx

from ._core import BASE_URL, _parse_response
from ._namespaces.live import AsyncLiveNamespace
from ._namespaces.race import AsyncRaceNamespace
from ._namespaces.results import AsyncResultsNamespace


class AsyncRaceMonitorClient:
    def __init__(self, api_token: str, retry_delay: float = 10.0, **kwargs) -> None:
        self._token = api_token
        self._retry_delay = retry_delay
        self._http = httpx.AsyncClient(**kwargs)
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
