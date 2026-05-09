from typing import Callable


class ResultsNamespace:
    """Endpoints under /v2/Results."""

    def __init__(self, post: Callable) -> None:
        self._post = post

    def competitor_details(self, competitor_id: int) -> dict:
        """Get details for an individual competitor.

        Stability: Production.

        Args:
            competitor_id: The competitor ID (Int64).
        """
        return self._post("/v2/Results/CompetitorDetails", competitorID=competitor_id)

    def competitors_with_transponder(self, transponder: str) -> dict:
        """Find competitors in results that have a given transponder value.

        Stability: Beta — subject to change without notice.

        Args:
            transponder: The transponder value to search for.
        """
        return self._post("/v2/Results/CompetitorsWithTransponder", transponder=transponder)

    def grouped_sessions_for_race(
        self,
        race_id: int | str,
        device_id: str = "",
        force_standard_behavior: bool = False,
    ) -> dict:
        """Get sessions grouped by category for a race.

        Only valid sessions or those manually marked 'Display In App' are returned.
        Long Running Races return up to 100 sessions grouped by date unless
        ``force_standard_behavior`` is True.

        Stability: Production.

        Args:
            race_id: The race ID.
            device_id: Optional device filter.
            force_standard_behavior: Return all sessions grouped by class even
                for Long Running Races.
        """
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
        """Get competitor and session objects for a race and transponder.

        Stability: Production.

        Args:
            race_id: The race ID.
            transponder: Transponder value to match.
            last_name: Last name to match.
            only_results_with_finish_flag: Limit to results with a finish flag.
            sort_descending: Sort results in descending order.
        """
        return self._post(
            "/v2/Results/RacerResultsForRace",
            raceID=race_id,
            transponder=transponder,
            lastName=last_name,
            onlyResultsWithFinishFlag=only_results_with_finish_flag,
            sortDescending=sort_descending,
        )

    def races_with_transponder(self, transponder: str, last_name: str) -> dict:
        """Get races containing sessions with competitors matching a transponder.

        Stability: Production.

        Args:
            transponder: Transponder value to search for.
            last_name: Last name to match.
        """
        return self._post(
            "/v2/Results/RacesWithTransponder",
            transponder=transponder,
            lastName=last_name,
        )

    def recent_results(self, app_section_id: int = 0, past_days: int = 0) -> dict:
        """Find recent races with results.

        Default look-back is 9 days (or the section-configured value).
        ``past_days`` overrides this up to a maximum of 60.

        Stability: Production.

        Args:
            app_section_id: Limit to a specific app section. 0 returns all.
            past_days: Number of past days to include. 0 uses the default.
        """
        return self._post(
            "/v2/Results/RecentResults",
            appSectionID=app_section_id,
            pastDays=past_days,
        )

    def search_results(self, search_term: str, app_section_id: int = 0) -> dict:
        """Search races with results by race name and track.

        Terms under 3 characters only match the start of the name/track.

        Stability: Production.

        Args:
            search_term: Text to search for.
            app_section_id: Limit search to a specific app section. 0 searches all.
        """
        return self._post(
            "/v2/Results/SearchResults",
            searchTerm=search_term,
            appSectionID=app_section_id,
        )

    def session_details(self, session_id: int, include_lap_times: bool = False) -> dict:
        """Get results from a race session.

        Lap times are not included by default as they can produce very large
        responses. Prefer ``competitor_details`` for individual lap times.

        Stability: Production.

        Args:
            session_id: The session ID (Int64).
            include_lap_times: Include individual lap times for all competitors.
        """
        return self._post(
            "/v2/Results/SessionDetails",
            sessionID=session_id,
            includeLapTimes=include_lap_times,
        )

    def sessions_for_race(self, race_id: int | str, device_id: str = "") -> dict:
        """Get sessions for a race.

        Only valid sessions or those manually marked 'Display In App' are returned.

        Stability: Production.

        Args:
            race_id: The race ID.
            device_id: Optional device filter.
        """
        return self._post(
            "/v2/Results/SessionsForRace",
            raceID=race_id,
            deviceID=device_id,
        )

    def sessions_in_date_range_for_race(
        self, race_id: int | str, start_date_epoc: int, end_date_epoc: int
    ) -> dict:
        """Get sessions within a date range for a race.

        Currently only works with Long Running Races. Non-Long Running Races
        return all sessions regardless of the date range.

        Stability: Experimental — subject to change or removal without notice.

        Args:
            race_id: The race ID.
            start_date_epoc: Range start as a Unix epoch (Int64).
            end_date_epoc: Range end as a Unix epoch (Int64).
        """
        return self._post(
            "/v2/Results/SessionsInDateRangeForRace",
            raceID=race_id,
            startDateEpoc=start_date_epoc,
            endDateEpoc=end_date_epoc,
        )


class AsyncResultsNamespace:
    """Async endpoints under /v2/Results."""

    def __init__(self, post: Callable) -> None:
        self._post = post

    async def competitor_details(self, competitor_id: int) -> dict:
        """Get details for an individual competitor.

        Stability: Production.

        Args:
            competitor_id: The competitor ID (Int64).
        """
        return await self._post("/v2/Results/CompetitorDetails", competitorID=competitor_id)

    async def competitors_with_transponder(self, transponder: str) -> dict:
        """Find competitors in results that have a given transponder value.

        Stability: Beta — subject to change without notice.

        Args:
            transponder: The transponder value to search for.
        """
        return await self._post("/v2/Results/CompetitorsWithTransponder", transponder=transponder)

    async def grouped_sessions_for_race(
        self,
        race_id: int | str,
        device_id: str = "",
        force_standard_behavior: bool = False,
    ) -> dict:
        """Get sessions grouped by category for a race.

        Only valid sessions or those manually marked 'Display In App' are returned.
        Long Running Races return up to 100 sessions grouped by date unless
        ``force_standard_behavior`` is True.

        Stability: Production.

        Args:
            race_id: The race ID.
            device_id: Optional device filter.
            force_standard_behavior: Return all sessions grouped by class even
                for Long Running Races.
        """
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
        """Get competitor and session objects for a race and transponder.

        Stability: Production.

        Args:
            race_id: The race ID.
            transponder: Transponder value to match.
            last_name: Last name to match.
            only_results_with_finish_flag: Limit to results with a finish flag.
            sort_descending: Sort results in descending order.
        """
        return await self._post(
            "/v2/Results/RacerResultsForRace",
            raceID=race_id,
            transponder=transponder,
            lastName=last_name,
            onlyResultsWithFinishFlag=only_results_with_finish_flag,
            sortDescending=sort_descending,
        )

    async def races_with_transponder(self, transponder: str, last_name: str) -> dict:
        """Get races containing sessions with competitors matching a transponder.

        Stability: Production.

        Args:
            transponder: Transponder value to search for.
            last_name: Last name to match.
        """
        return await self._post(
            "/v2/Results/RacesWithTransponder",
            transponder=transponder,
            lastName=last_name,
        )

    async def recent_results(self, app_section_id: int = 0, past_days: int = 0) -> dict:
        """Find recent races with results.

        Default look-back is 9 days (or the section-configured value).
        ``past_days`` overrides this up to a maximum of 60.

        Stability: Production.

        Args:
            app_section_id: Limit to a specific app section. 0 returns all.
            past_days: Number of past days to include. 0 uses the default.
        """
        return await self._post(
            "/v2/Results/RecentResults",
            appSectionID=app_section_id,
            pastDays=past_days,
        )

    async def search_results(self, search_term: str, app_section_id: int = 0) -> dict:
        """Search races with results by race name and track.

        Terms under 3 characters only match the start of the name/track.

        Stability: Production.

        Args:
            search_term: Text to search for.
            app_section_id: Limit search to a specific app section. 0 searches all.
        """
        return await self._post(
            "/v2/Results/SearchResults",
            searchTerm=search_term,
            appSectionID=app_section_id,
        )

    async def session_details(self, session_id: int, include_lap_times: bool = False) -> dict:
        """Get results from a race session.

        Lap times are not included by default as they can produce very large
        responses. Prefer ``competitor_details`` for individual lap times.

        Stability: Production.

        Args:
            session_id: The session ID (Int64).
            include_lap_times: Include individual lap times for all competitors.
        """
        return await self._post(
            "/v2/Results/SessionDetails",
            sessionID=session_id,
            includeLapTimes=include_lap_times,
        )

    async def sessions_for_race(self, race_id: int | str, device_id: str = "") -> dict:
        """Get sessions for a race.

        Only valid sessions or those manually marked 'Display In App' are returned.

        Stability: Production.

        Args:
            race_id: The race ID.
            device_id: Optional device filter.
        """
        return await self._post(
            "/v2/Results/SessionsForRace",
            raceID=race_id,
            deviceID=device_id,
        )

    async def sessions_in_date_range_for_race(
        self, race_id: int | str, start_date_epoc: int, end_date_epoc: int
    ) -> dict:
        """Get sessions within a date range for a race.

        Currently only works with Long Running Races. Non-Long Running Races
        return all sessions regardless of the date range.

        Stability: Experimental — subject to change or removal without notice.

        Args:
            race_id: The race ID.
            start_date_epoc: Range start as a Unix epoch (Int64).
            end_date_epoc: Range end as a Unix epoch (Int64).
        """
        return await self._post(
            "/v2/Results/SessionsInDateRangeForRace",
            raceID=race_id,
            startDateEpoc=start_date_epoc,
            endDateEpoc=end_date_epoc,
        )
