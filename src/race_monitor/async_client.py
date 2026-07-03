"""Asynchronous Race Monitor API client."""

import asyncio
import logging
from typing import Any

import httpx

from ._core import BASE_URL, RaceMonitorHTTPError, _parse_response, _retry_after_seconds
from ._namespaces.account import AsyncAccountNamespace
from ._namespaces.common import AsyncCommonNamespace
from ._namespaces.live import AsyncLiveNamespace
from ._namespaces.race import AsyncRaceNamespace
from ._namespaces.results import AsyncResultsNamespace
from ._rate_limiter import get_pool

_logger = logging.getLogger(__name__)


class AsyncRaceMonitorClient:
    """Asynchronous Race Monitor API client.

    Args:
        api_token: Your Race Monitor API token(s). Accepts:
            - ``str``: single token, uses ``requests_per_minute`` as its rate.
            - ``list[str]``: multiple tokens, all using ``requests_per_minute``.
            - ``dict[str, int | None]``: maps each token to its own requests-per-minute
              limit; ``requests_per_minute`` is ignored.
        retry_delay: Base cooldown applied to a token after a 429, in seconds.
            Consecutive 429s on the same token double it, up to 120s. Defaults
            to 10s (the developer plan rate limit window).
        requests_per_minute: Maximum requests per minute for ``str`` and
            ``list[str]`` inputs. Defaults to 6 (developer plan limit).
        max_retries: Maximum retries after 429 responses per request before
            raising :class:`RaceMonitorHTTPError`. Defaults to 5.
        **kwargs: Passed through to ``httpx.AsyncClient`` (e.g. ``transport`` for
            testing, or ``timeout`` — defaults to 30 seconds if not given).

    Note:
        Budgets are shared per token process-wide, including with
        :class:`~race_monitor.RaceMonitorClient` instances using the same token.

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
        max_retries: int = 5,
        **kwargs,
    ) -> None:
        """Initialize the client. See class docstring for parameter details."""
        if isinstance(api_token, str):
            token_rates = {api_token: requests_per_minute}
        elif isinstance(api_token, list):
            if not api_token:
                raise ValueError("api_token list must contain at least one token")
            token_rates = dict.fromkeys(api_token, requests_per_minute)
        elif isinstance(api_token, dict):
            if not api_token:
                raise ValueError("api_token dict must contain at least one token")
            token_rates = api_token
        else:
            raise TypeError("api_token must be a str, list[str], or dict[str, int | None]")
        self._pool = get_pool(token_rates, 60.0)
        self._retry_delay = retry_delay
        self._max_retries = max_retries
        kwargs.setdefault("timeout", 30)
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

    async def aclose(self) -> None:
        """Close the underlying HTTP connection pool.

        Use this when the client is not managed by an ``async with`` block.
        """
        await self._http.aclose()

    async def _post(self, path: str, **kwargs) -> dict[str, Any]:
        """POST to the API, selecting the least-loaded token and retrying on 429.

        A 429 puts the offending token in an escalating cooldown so the next
        attempt rotates to another token; we only sleep when every token is
        unavailable. After ``max_retries`` retries the request fails with
        :class:`RaceMonitorHTTPError`.
        """
        attempts = 0
        while True:
            acquired = self._pool.try_acquire()
            if acquired is None:
                wait = self._pool.wait_time()
                _logger.info("All tokens rate-limited or cooling; sleeping %.2fs", wait)
                await asyncio.sleep(wait)
                continue
            token, budget = acquired
            data = {**kwargs, "apiToken": token}
            response = await self._http.post(f"{BASE_URL}{path}", data=data)
            if response.status_code == 429:
                budget.release()
                budget.mark_cooldown(self._retry_delay, _retry_after_seconds(response))
                attempts += 1
                if attempts > self._max_retries:
                    raise RaceMonitorHTTPError(429, response.text)
                continue
            parsed = _parse_response(response)
            budget.note_success()
            return parsed

    async def post(self, path: str, **kwargs) -> dict[str, Any]:
        """Make a POST request to the given API path."""
        return await self._post(path, **kwargs)
