from typing import Callable

from race_monitor.types import (
    AppSectionsResponse,
    CommonRacesResponse,
    RaceTypesResponse,
    TimeZonesResponse,
)


class CommonNamespace:
    """Endpoints under /v2/Common."""

    def __init__(self, post: Callable) -> None:
        self._post = post

    def app_sections(self) -> AppSectionsResponse:
        """Get app sections (e.g. Oval Racing, Road Racing, Karting).

        Stability: Production.
        """
        return self._post("/v2/Common/AppSections")

    def current_races(self, series_id: int = 0) -> CommonRacesResponse:
        """Get all current races.

        Stability: Production.

        Args:
            series_id: Filter by series ID. 0 returns all.
        """
        return self._post("/v2/Common/CurrentRaces", seriesID=series_id)

    def past_races(
        self, series_id: int = 0, first_result: int = 0, max_results: int = 100
    ) -> CommonRacesResponse:
        """Get past races.

        Stability: Beta — subject to change without notice.

        Args:
            series_id: Filter by series ID. 0 returns all.
            first_result: Pagination offset.
            max_results: Maximum number of results to return.
        """
        return self._post(
            "/v2/Common/PastRaces",
            seriesID=series_id,
            firstResult=first_result,
            maxResults=max_results,
        )

    def race_types(self) -> RaceTypesResponse:
        """Get race types available in Race Monitor.

        Stability: Production.
        """
        return self._post("/v2/Common/RaceTypes")

    def time_zones(self) -> TimeZonesResponse:
        """Get system time zones (as defined by .NET) used by races.

        Stability: Production.
        """
        return self._post("/v2/Common/TimeZones")

    def upcoming_races(self, series_id: int = 0) -> CommonRacesResponse:
        """Get all upcoming races.

        Stability: Production.

        Args:
            series_id: Filter by series ID. 0 returns all.
        """
        return self._post("/v2/Common/UpcomingRaces", seriesID=series_id)


class AsyncCommonNamespace:
    """Async endpoints under /v2/Common."""

    def __init__(self, post: Callable) -> None:
        self._post = post

    async def app_sections(self) -> AppSectionsResponse:
        """Get app sections (e.g. Oval Racing, Road Racing, Karting).

        Stability: Production.
        """
        return await self._post("/v2/Common/AppSections")

    async def current_races(self, series_id: int = 0) -> CommonRacesResponse:
        """Get all current races.

        Stability: Production.

        Args:
            series_id: Filter by series ID. 0 returns all.
        """
        return await self._post("/v2/Common/CurrentRaces", seriesID=series_id)

    async def past_races(
        self, series_id: int = 0, first_result: int = 0, max_results: int = 100
    ) -> CommonRacesResponse:
        """Get past races.

        Stability: Beta — subject to change without notice.

        Args:
            series_id: Filter by series ID. 0 returns all.
            first_result: Pagination offset.
            max_results: Maximum number of results to return.
        """
        return await self._post(
            "/v2/Common/PastRaces",
            seriesID=series_id,
            firstResult=first_result,
            maxResults=max_results,
        )

    async def race_types(self) -> RaceTypesResponse:
        """Get race types available in Race Monitor.

        Stability: Production.
        """
        return await self._post("/v2/Common/RaceTypes")

    async def time_zones(self) -> TimeZonesResponse:
        """Get system time zones (as defined by .NET) used by races.

        Stability: Production.
        """
        return await self._post("/v2/Common/TimeZones")

    async def upcoming_races(self, series_id: int = 0) -> CommonRacesResponse:
        """Get all upcoming races.

        Stability: Production.

        Args:
            series_id: Filter by series ID. 0 returns all.
        """
        return await self._post("/v2/Common/UpcomingRaces", seriesID=series_id)
