"""Python client for the Race Monitor API (https://www.race-monitor.com).

All endpoints require an API token, obtainable from your Race Monitor account page.
Requests are POST-only over SSL. The token is injected automatically into every request.

Basic usage::

    from race_monitor import RaceMonitorClient

    with RaceMonitorClient(api_token="YOUR_TOKEN") as client:
        race = client.race.details(race_id=12345)
        print(race["Race"]["Name"])

Async usage::

    from race_monitor import AsyncRaceMonitorClient

    async with AsyncRaceMonitorClient(api_token="YOUR_TOKEN") as client:
        race = await client.race.details(race_id=12345)

Response types are available in :mod:`race_monitor.types` for use in type annotations::

    from race_monitor.types import RaceDetailsResponse, Race
"""

from .client import RaceMonitorClient
from .async_client import AsyncRaceMonitorClient
from ._core import RaceMonitorError, RaceMonitorHTTPError

__all__ = [
    "RaceMonitorClient",
    "AsyncRaceMonitorClient",
    "RaceMonitorError",
    "RaceMonitorHTTPError",
]
