from typing import Callable


class AccountNamespace:
    """Endpoints under /v2/Account. All Production stability."""

    def __init__(self, post: Callable) -> None:
        self._post = post

    def all_races(self, series_id: int = 0, race_type_id: int = 0) -> dict:
        """Get all races associated with your relaying account.

        Args:
            series_id: Filter by series ID. 0 returns all.
            race_type_id: Filter by race type ID. 0 returns all.
        """
        return self._post("/v2/Account/AllRaces", seriesID=series_id, raceTypeID=race_type_id)

    def current_races(self, series_id: int = 0, race_type_id: int = 0) -> dict:
        """Get current races associated with your relaying account.

        Args:
            series_id: Filter by series ID. 0 returns all.
            race_type_id: Filter by race type ID. 0 returns all.
        """
        return self._post("/v2/Account/CurrentRaces", seriesID=series_id, raceTypeID=race_type_id)

    def past_races(self, series_id: int = 0, race_type_id: int = 0) -> dict:
        """Get past races associated with your relaying account.

        Args:
            series_id: Filter by series ID. 0 returns all.
            race_type_id: Filter by race type ID. 0 returns all.
        """
        return self._post("/v2/Account/PastRaces", seriesID=series_id, raceTypeID=race_type_id)

    def series(self) -> dict:
        """Get series that your account has permission for."""
        return self._post("/v2/Account/Series")

    def upcoming_races(self, series_id: int = 0, race_type_id: int = 0) -> dict:
        """Get upcoming races associated with your relaying account.

        Args:
            series_id: Filter by series ID. 0 returns all.
            race_type_id: Filter by race type ID. 0 returns all.
        """
        return self._post("/v2/Account/UpcomingRaces", seriesID=series_id, raceTypeID=race_type_id)


class AsyncAccountNamespace:
    """Async endpoints under /v2/Account. All Production stability."""

    def __init__(self, post: Callable) -> None:
        self._post = post

    async def all_races(self, series_id: int = 0, race_type_id: int = 0) -> dict:
        """Get all races associated with your relaying account.

        Args:
            series_id: Filter by series ID. 0 returns all.
            race_type_id: Filter by race type ID. 0 returns all.
        """
        return await self._post("/v2/Account/AllRaces", seriesID=series_id, raceTypeID=race_type_id)

    async def current_races(self, series_id: int = 0, race_type_id: int = 0) -> dict:
        """Get current races associated with your relaying account.

        Args:
            series_id: Filter by series ID. 0 returns all.
            race_type_id: Filter by race type ID. 0 returns all.
        """
        return await self._post("/v2/Account/CurrentRaces", seriesID=series_id, raceTypeID=race_type_id)

    async def past_races(self, series_id: int = 0, race_type_id: int = 0) -> dict:
        """Get past races associated with your relaying account.

        Args:
            series_id: Filter by series ID. 0 returns all.
            race_type_id: Filter by race type ID. 0 returns all.
        """
        return await self._post("/v2/Account/PastRaces", seriesID=series_id, raceTypeID=race_type_id)

    async def series(self) -> dict:
        """Get series that your account has permission for."""
        return await self._post("/v2/Account/Series")

    async def upcoming_races(self, series_id: int = 0, race_type_id: int = 0) -> dict:
        """Get upcoming races associated with your relaying account.

        Args:
            series_id: Filter by series ID. 0 returns all.
            race_type_id: Filter by race type ID. 0 returns all.
        """
        return await self._post("/v2/Account/UpcomingRaces", seriesID=series_id, raceTypeID=race_type_id)
