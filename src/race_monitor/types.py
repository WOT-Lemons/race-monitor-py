"""TypedDict definitions for all Race Monitor API response shapes.

Import these to annotate variables or function return types when working with
responses from :class:`~race_monitor.RaceMonitorClient` or
:class:`~race_monitor.AsyncRaceMonitorClient`.

Example::

    from race_monitor import RaceMonitorClient
    from race_monitor.types import RaceDetailsResponse, Race

    with RaceMonitorClient(api_token="...") as client:
        response: RaceDetailsResponse = client.race.details(race_id=12345)
        race: Race = response["Race"]
"""

from typing import TypedDict

# ---------------------------------------------------------------------------
# Shared object types
# ---------------------------------------------------------------------------


class SeriesInfo(TypedDict):
    """A series, used in race objects and as additional/secondary series."""

    ID: int
    Name: str
    ImageUrl: str


class RaceNotification(TypedDict):
    """A notification message attached to a race."""

    Message: str
    SendDateEpoc: int


class Race(TypedDict):
    """Full race detail, as returned by the Account and Race namespaces."""

    ID: int
    Name: str
    SeriesID: int
    AdditionalSeries: list[SeriesInfo]
    RaceTypeID: int
    ImageUrl: str
    StartDateEpoc: int
    EndDateEpoc: int
    TimeZoneID: str
    TimeZoneName: str
    TimeZoneOffset: int
    Times: str
    Track: str
    TestRace: bool
    HasResults: bool
    ExcludeFromWebsite: bool
    WebTimingUrl: str
    RaceNotifications: list[RaceNotification]
    Schedule: str


class PublicRace(TypedDict):
    """Race listing entry from the Common namespace (includes live/pricing info)."""

    IsLive: bool
    SeriesName: str
    IsFree: bool
    HasVideo: bool
    HasAudio: bool
    ID: int
    Name: str
    SeriesID: int
    AdditionalSeries: list[SeriesInfo]
    RaceTypeID: int
    ImageUrl: str
    DecoratorUrl: str
    StartDateEpoc: int
    EndDateEpoc: int
    TimeZoneOffset: int
    Times: str
    Track: str
    TestRace: bool
    HasResults: bool
    IsLongRunning: bool


class ResultsRace(TypedDict):
    """Minimal race summary returned by Results search/listing endpoints."""

    ID: int
    Name: str
    StartDateEpoc: int
    EndDateEpoc: int
    Times: str
    Track: str
    TimeZoneID: str
    TimeZoneName: str
    TimeZoneOffset: int
    DecoratorUrl: str


class AppSection(TypedDict):
    """An app section (e.g. Oval Racing, Road Racing, Karting)."""

    Name: str
    ID: int


class RaceType(TypedDict):
    """A race type available in Race Monitor."""

    ID: int
    Name: str


class TimeZoneInfo(TypedDict):
    """A system time zone as defined by .NET."""

    ID: str
    Name: str
    UTCOffsetMinutes: float


# ---------------------------------------------------------------------------
# Live namespace object types
# ---------------------------------------------------------------------------


class LiveCompetitor(TypedDict):
    """A competitor entry in a live timing session."""

    RacerID: str
    Number: str
    Transponder: str
    FirstName: str
    LastName: str
    Nationality: str
    AdditionalData: str
    ClassID: str
    Position: str
    Laps: str
    TotalTime: str
    BestPosition: str
    BestLap: str
    BestLapTime: str
    LastLapTime: str


class LiveLap(TypedDict):
    """A single lap entry within a live racer's history."""

    Lap: str
    Position: str
    LapTime: str
    FlagStatus: str
    TotalTime: str


class LiveClassInfo(TypedDict):
    """A racing class/category within a live session."""

    ClassID: str
    Description: str


class SocketInfo(TypedDict):
    """TCP socket coordinates for a streaming connection."""

    IPAddress: str
    Port: int


class StreamingConnectionInfo(TypedDict):
    """Connection credentials for a live data stream."""

    RaceID: int
    Socket: SocketInfo
    WS: str
    WSS: str
    WebsocketURL: str
    Instance: int
    LiveTimingToken: str
    IsLive: bool
    WebsiteRestrictions: str


class LiveSessionState(TypedDict):
    """Full live session state snapshot."""

    RunNumber: str
    SessionName: str
    TrackName: str
    TrackLength: str
    CurrentTime: str
    SessionTime: str
    TimeToGo: str
    LapsToGo: str
    FlagStatus: str
    SortMode: str
    Classes: dict[str, LiveClassInfo]
    Competitors: dict[str, LiveCompetitor]


class LiveRacerDetails(TypedDict):
    """Competitor and lap history detail, as returned by ``live.get_racer``."""

    Competitor: LiveCompetitor
    Laps: list[LiveLap]


class WebTimingDetails(TypedDict):
    """Web timing embed payload."""

    ScriptBlock: str


# ---------------------------------------------------------------------------
# Results namespace object types
# ---------------------------------------------------------------------------


class LapTime(TypedDict):
    """A single lap time entry within a results competitor."""

    Lap: str
    LapTime: str
    Position: str
    FlagStatus: int
    TotalTime: str


class Competitor(TypedDict):
    """A competitor with full results data including lap times."""

    ID: int
    SessionID: int
    RaceID: int
    FirstName: str
    LastName: str
    Position: str
    Laps: str
    LastLapTime: str
    BestPosition: str
    BestLap: str
    BestLapTime: str
    TotalTime: str
    Number: str
    Transponder: str
    Nationality: str
    AdditionalData: str
    Category: str
    LapTimes: list[LapTime]


class CategoryEntry(TypedDict):
    """A category/class entry within a session's category map."""

    ID: str
    Name: str


class Session(TypedDict):
    """A results session (without individual competitor details)."""

    ID: int
    RaceID: int
    Name: str
    SessionDate: str
    SessionTime: str
    SortMode: str
    Categories: dict[str, CategoryEntry]
    CategoryString: str
    ResultsProcessorVersion: int
    SessionStartDateEpoc: int


class SessionWithCompetitors(TypedDict):
    """A results session including the sorted competitor list."""

    ID: int
    RaceID: int
    Name: str
    SessionDate: str
    SessionTime: str
    SortMode: str
    SortedCompetitors: list[Competitor]
    Categories: dict[str, CategoryEntry]
    CategoryString: str
    ResultsProcessorVersion: int
    SessionStartDateEpoc: int


class GroupedSession(TypedDict):
    """A group of sessions under a common category label."""

    Category: str
    Sessions: list[Session]


class RacerResult(TypedDict):
    """A single racer result entry pairing a competitor with their session."""

    Competitor: Competitor
    RaceSession: SessionWithCompetitors


class RacerResultsPayload(TypedDict):
    """The inner ``Details`` object from ``results.racer_results_for_race``."""

    Results: list[RacerResult]


# ---------------------------------------------------------------------------
# Response types — Account namespace
# ---------------------------------------------------------------------------


class AccountRacesResponse(TypedDict):
    """Response from Account race-listing endpoints (all/current/past/upcoming)."""

    Successful: bool
    Races: list[Race]


class AccountSeriesResponse(TypedDict):
    """Response from ``account.series``."""

    Successful: bool
    Series: list[SeriesInfo]


# ---------------------------------------------------------------------------
# Response types — Common namespace
# ---------------------------------------------------------------------------


class AppSectionsResponse(TypedDict):
    """Response from ``common.app_sections``."""

    Successful: bool
    AppSections: list[AppSection]


class CommonRacesResponse(TypedDict):
    """Response from Common race-listing endpoints (current/past/upcoming)."""

    Successful: bool
    Races: list[PublicRace]


class RaceTypesResponse(TypedDict):
    """Response from ``common.race_types``."""

    Successful: bool
    RaceTypes: list[RaceType]


class TimeZonesResponse(TypedDict):
    """Response from ``common.time_zones``."""

    Successful: bool
    TimeZones: list[TimeZoneInfo]


# ---------------------------------------------------------------------------
# Response types — Live namespace
# ---------------------------------------------------------------------------


class GetRacerResponse(TypedDict):
    """Response from ``live.get_racer``."""

    Successful: bool
    Details: LiveRacerDetails


class GetRacerCountResponse(TypedDict):
    """Response from ``live.get_racer_count``."""

    Successful: bool
    Count: int


class GetSessionResponse(TypedDict):
    """Response from ``live.get_session``."""

    Successful: bool
    Session: LiveSessionState


class GetStreamingConnectionResponse(TypedDict):
    """Response from ``live.get_streaming_connection``."""

    Successful: bool
    ConnectionInfo: StreamingConnectionInfo


class GetWebTimingResponse(TypedDict):
    """Response from ``live.get_web_timing``."""

    Successful: bool
    Details: WebTimingDetails


# ---------------------------------------------------------------------------
# Response types — Race namespace
# ---------------------------------------------------------------------------


class IsLiveResponse(TypedDict):
    """Response from ``race.is_live``."""

    Successful: bool
    IsLive: bool


class RaceDetailsResponse(TypedDict):
    """Response from ``race.details``."""

    Successful: bool
    Race: Race


# ---------------------------------------------------------------------------
# Response types — Results namespace
# ---------------------------------------------------------------------------


class CompetitorDetailsResponse(TypedDict):
    """Response from ``results.competitor_details``."""

    Successful: bool
    Competitor: Competitor


class CompetitorsWithTransponderResponse(TypedDict):
    """Response from ``results.competitors_with_transponder``."""

    Successful: bool
    Competitors: list[Competitor]


class GroupedSessionsForRaceResponse(TypedDict):
    """Response from ``results.grouped_sessions_for_race``."""

    Successful: bool
    GroupedSessions: list[GroupedSession]


class RacerResultsForRaceResponse(TypedDict):
    """Response from ``results.racer_results_for_race``."""

    Successful: bool
    Details: RacerResultsPayload


class ResultsRacesResponse(TypedDict):
    """Response from Results race-listing endpoints.

    Covers ``races_with_transponder``, ``recent_results``, and ``search_results``.
    """

    Successful: bool
    Races: list[ResultsRace]


class SessionDetailsResponse(TypedDict):
    """Response from ``results.session_details``."""

    Successful: bool
    Session: SessionWithCompetitors


class SessionsResponse(TypedDict):
    """Response from ``results.sessions_for_race`` and ``sessions_in_date_range_for_race``."""

    Successful: bool
    Sessions: list[Session]
