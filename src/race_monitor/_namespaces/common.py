from typing import Callable


class CommonNamespace:
    def __init__(self, post: Callable) -> None:
        self._post = post

    def app_sections(self) -> dict:
        return self._post("/v2/Common/AppSections")

    def current_races(self, series_id: int = 0) -> dict:
        return self._post("/v2/Common/CurrentRaces", seriesID=series_id)

    def past_races(
        self, series_id: int = 0, first_result: int = 0, max_results: int = 100
    ) -> dict:
        return self._post(
            "/v2/Common/PastRaces",
            seriesID=series_id,
            firstResult=first_result,
            maxResults=max_results,
        )

    def race_types(self) -> dict:
        return self._post("/v2/Common/RaceTypes")

    def time_zones(self) -> dict:
        return self._post("/v2/Common/TimeZones")

    def upcoming_races(self, series_id: int = 0) -> dict:
        return self._post("/v2/Common/UpcomingRaces", seriesID=series_id)


class AsyncCommonNamespace:
    def __init__(self, post: Callable) -> None:
        self._post = post

    async def app_sections(self) -> dict:
        return await self._post("/v2/Common/AppSections")

    async def current_races(self, series_id: int = 0) -> dict:
        return await self._post("/v2/Common/CurrentRaces", seriesID=series_id)

    async def past_races(
        self, series_id: int = 0, first_result: int = 0, max_results: int = 100
    ) -> dict:
        return await self._post(
            "/v2/Common/PastRaces",
            seriesID=series_id,
            firstResult=first_result,
            maxResults=max_results,
        )

    async def race_types(self) -> dict:
        return await self._post("/v2/Common/RaceTypes")

    async def time_zones(self) -> dict:
        return await self._post("/v2/Common/TimeZones")

    async def upcoming_races(self, series_id: int = 0) -> dict:
        return await self._post("/v2/Common/UpcomingRaces", seriesID=series_id)
