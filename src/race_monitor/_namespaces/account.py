from typing import Callable


class AccountNamespace:
    def __init__(self, post: Callable) -> None:
        self._post = post

    def all_races(self, series_id: int = 0, race_type_id: int = 0) -> dict:
        return self._post("/v2/Account/AllRaces", seriesID=series_id, raceTypeID=race_type_id)

    def current_races(self, series_id: int = 0, race_type_id: int = 0) -> dict:
        return self._post("/v2/Account/CurrentRaces", seriesID=series_id, raceTypeID=race_type_id)

    def past_races(self, series_id: int = 0, race_type_id: int = 0) -> dict:
        return self._post("/v2/Account/PastRaces", seriesID=series_id, raceTypeID=race_type_id)

    def series(self) -> dict:
        return self._post("/v2/Account/Series")

    def upcoming_races(self, series_id: int = 0, race_type_id: int = 0) -> dict:
        return self._post("/v2/Account/UpcomingRaces", seriesID=series_id, raceTypeID=race_type_id)


class AsyncAccountNamespace:
    def __init__(self, post: Callable) -> None:
        self._post = post

    async def all_races(self, series_id: int = 0, race_type_id: int = 0) -> dict:
        return await self._post("/v2/Account/AllRaces", seriesID=series_id, raceTypeID=race_type_id)

    async def current_races(self, series_id: int = 0, race_type_id: int = 0) -> dict:
        return await self._post("/v2/Account/CurrentRaces", seriesID=series_id, raceTypeID=race_type_id)

    async def past_races(self, series_id: int = 0, race_type_id: int = 0) -> dict:
        return await self._post("/v2/Account/PastRaces", seriesID=series_id, raceTypeID=race_type_id)

    async def series(self) -> dict:
        return await self._post("/v2/Account/Series")

    async def upcoming_races(self, series_id: int = 0, race_type_id: int = 0) -> dict:
        return await self._post("/v2/Account/UpcomingRaces", seriesID=series_id, raceTypeID=race_type_id)
