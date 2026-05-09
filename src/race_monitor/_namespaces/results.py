from typing import Callable


class ResultsNamespace:
    def __init__(self, post: Callable) -> None:
        self._post = post

    def competitor_details(self, competitor_id: int) -> dict:
        return self._post("/v2/Results/CompetitorDetails", competitorID=competitor_id)

    def competitors_with_transponder(self, transponder: str) -> dict:
        return self._post("/v2/Results/CompetitorsWithTransponder", transponder=transponder)

    def grouped_sessions_for_race(
        self,
        race_id: int | str,
        device_id: str = "",
        force_standard_behavior: bool = False,
    ) -> dict:
        return self._post(
            "/v2/Results/GroupedSessionsForRace",
            raceID=race_id,
            deviceID=device_id,
            forceStandardBehavior=force_standard_behavior,
        )

    def racer_results_for_race(
        self,
        race_id: int | str,
        transponder: str,
        last_name: str,
        only_results_with_finish_flag: bool = False,
        sort_descending: bool = False,
    ) -> dict:
        return self._post(
            "/v2/Results/RacerResultsForRace",
            raceID=race_id,
            transponder=transponder,
            lastName=last_name,
            onlyResultsWithFinishFlag=only_results_with_finish_flag,
            sortDescending=sort_descending,
        )

    def races_with_transponder(self, transponder: str, last_name: str) -> dict:
        return self._post(
            "/v2/Results/RacesWithTransponder",
            transponder=transponder,
            lastName=last_name,
        )

    def recent_results(self, app_section_id: int = 0, past_days: int = 0) -> dict:
        return self._post(
            "/v2/Results/RecentResults",
            appSectionID=app_section_id,
            pastDays=past_days,
        )

    def search_results(self, search_term: str, app_section_id: int = 0) -> dict:
        return self._post(
            "/v2/Results/SearchResults",
            searchTerm=search_term,
            appSectionID=app_section_id,
        )

    def session_details(self, session_id: int, include_lap_times: bool = False) -> dict:
        return self._post(
            "/v2/Results/SessionDetails",
            sessionID=session_id,
            includeLapTimes=include_lap_times,
        )

    def sessions_for_race(self, race_id: int | str, device_id: str = "") -> dict:
        return self._post(
            "/v2/Results/SessionsForRace",
            raceID=race_id,
            deviceID=device_id,
        )

    def sessions_in_date_range_for_race(
        self, race_id: int | str, start_date_epoc: int, end_date_epoc: int
    ) -> dict:
        return self._post(
            "/v2/Results/SessionsInDateRangeForRace",
            raceID=race_id,
            startDateEpoc=start_date_epoc,
            endDateEpoc=end_date_epoc,
        )


class AsyncResultsNamespace:
    def __init__(self, post: Callable) -> None:
        self._post = post

    async def competitor_details(self, competitor_id: int) -> dict:
        return await self._post("/v2/Results/CompetitorDetails", competitorID=competitor_id)

    async def competitors_with_transponder(self, transponder: str) -> dict:
        return await self._post("/v2/Results/CompetitorsWithTransponder", transponder=transponder)

    async def grouped_sessions_for_race(
        self,
        race_id: int | str,
        device_id: str = "",
        force_standard_behavior: bool = False,
    ) -> dict:
        return await self._post(
            "/v2/Results/GroupedSessionsForRace",
            raceID=race_id,
            deviceID=device_id,
            forceStandardBehavior=force_standard_behavior,
        )

    async def racer_results_for_race(
        self,
        race_id: int | str,
        transponder: str,
        last_name: str,
        only_results_with_finish_flag: bool = False,
        sort_descending: bool = False,
    ) -> dict:
        return await self._post(
            "/v2/Results/RacerResultsForRace",
            raceID=race_id,
            transponder=transponder,
            lastName=last_name,
            onlyResultsWithFinishFlag=only_results_with_finish_flag,
            sortDescending=sort_descending,
        )

    async def races_with_transponder(self, transponder: str, last_name: str) -> dict:
        return await self._post(
            "/v2/Results/RacesWithTransponder",
            transponder=transponder,
            lastName=last_name,
        )

    async def recent_results(self, app_section_id: int = 0, past_days: int = 0) -> dict:
        return await self._post(
            "/v2/Results/RecentResults",
            appSectionID=app_section_id,
            pastDays=past_days,
        )

    async def search_results(self, search_term: str, app_section_id: int = 0) -> dict:
        return await self._post(
            "/v2/Results/SearchResults",
            searchTerm=search_term,
            appSectionID=app_section_id,
        )

    async def session_details(self, session_id: int, include_lap_times: bool = False) -> dict:
        return await self._post(
            "/v2/Results/SessionDetails",
            sessionID=session_id,
            includeLapTimes=include_lap_times,
        )

    async def sessions_for_race(self, race_id: int | str, device_id: str = "") -> dict:
        return await self._post(
            "/v2/Results/SessionsForRace",
            raceID=race_id,
            deviceID=device_id,
        )

    async def sessions_in_date_range_for_race(
        self, race_id: int | str, start_date_epoc: int, end_date_epoc: int
    ) -> dict:
        return await self._post(
            "/v2/Results/SessionsInDateRangeForRace",
            raceID=race_id,
            startDateEpoc=start_date_epoc,
            endDateEpoc=end_date_epoc,
        )
