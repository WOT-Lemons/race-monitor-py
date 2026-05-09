from typing import Callable


class RaceNamespace:
    """Endpoints under /v2/Race."""

    def __init__(self, post: Callable) -> None:
        self._post = post

    def details(self, race_id: int | str) -> dict:
        """Get information about a specific race.

        Stability: Production.

        Args:
            race_id: The race ID.
        """
        return self._post("/v2/Race/RaceDetails", raceID=race_id)

    def is_live(self, race_id: int | str) -> dict:
        """Check whether Race Monitor servers are receiving live data from this race.

        Live means live timing data has been received within the last two minutes.

        Stability: Production.

        Args:
            race_id: The race ID.
        """
        return self._post("/v2/Race/IsLive", raceID=race_id)


class AsyncRaceNamespace:
    """Async endpoints under /v2/Race."""

    def __init__(self, post: Callable) -> None:
        self._post = post

    async def details(self, race_id: int | str) -> dict:
        """Get information about a specific race.

        Stability: Production.

        Args:
            race_id: The race ID.
        """
        return await self._post("/v2/Race/RaceDetails", raceID=race_id)

    async def is_live(self, race_id: int | str) -> dict:
        """Check whether Race Monitor servers are receiving live data from this race.

        Live means live timing data has been received within the last two minutes.

        Stability: Production.

        Args:
            race_id: The race ID.
        """
        return await self._post("/v2/Race/IsLive", raceID=race_id)
