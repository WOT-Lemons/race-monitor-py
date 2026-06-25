# Race Monitor API Coverage

**Source:** https://www.race-monitor.com/APIDocs  
**Base URL:** https://api.race-monitor.com  
**Total endpoints:** 32 across 6 controllers  
**Implemented:** 28 ✅  **Not implemented:** 4 ❌ (all in /v2/Media)

---

## /v2/Account

| Endpoint | Stability | Description | Status | Python method |
|----------|-----------|-------------|--------|---------------|
| AllRaces | Production | Get a list of all races associated with your relaying account | ✅ | `client.account.all_races()` |
| CurrentRaces | Production | Get a list of all current races associated with your relaying account | ✅ | `client.account.current_races()` |
| PastRaces | Production | Get a list of all past races associated with your relaying account | ✅ | `client.account.past_races()` |
| Series | Production | Get a list of series that your account has permission for | ✅ | `client.account.series()` |
| UpcomingRaces | Production | Get a list of all upcoming races associated with your relaying account | ✅ | `client.account.upcoming_races()` |

**Coverage: 5/5**

---

## /v2/Common

| Endpoint | Stability | Description | Status | Python method |
|----------|-----------|-------------|--------|---------------|
| AppSections | Production | Get a list of App Sections (e.g., Oval Racing, Road Racing, Karting) | ✅ | `client.common.app_sections()` |
| CurrentRaces | Production | Get a list of Current Races, optionally filtered by series | ✅ | `client.common.current_races()` |
| PastRaces | Beta | Get a list of Past Races, limited by maxResults | ✅ | `client.common.past_races()` |
| RaceTypes | Production | Get a list of Race Types that Race Monitor has available | ✅ | `client.common.race_types()` |
| TimeZones | Production | Get a list of system TimeZones used by races | ✅ | `client.common.time_zones()` |
| UpcomingRaces | Production | Get a list of Upcoming Races, optionally filtered by series | ✅ | `client.common.upcoming_races()` |

**Coverage: 6/6**

---

## /v2/Live

| Endpoint | Stability | Description | Status | Python method |
|----------|-----------|-------------|--------|---------------|
| GetRacer | Production | Returns details about a specific competitor including all lap times | ✅ | `client.live.get_racer()` |
| GetRacerCount | Production | Returns a count of the number of racers in the given session | ✅ | `client.live.get_racer_count()` |
| GetSession | Production | Returns the current session state of the given race | ✅ | `client.live.get_session()` |
| GetStreamingConnection | Production | Returns connection info for socket/websocket streaming data connection | ✅ | `client.live.get_streaming_connection()` |
| GetWebTiming | Beta | Generates a web timing script block (Source Mode: 'series' or 'race') | ✅ | `client.live.get_web_timing()` |

**Coverage: 5/5**

---

## /v2/Media

| Endpoint | Stability | Description | Status | Python method |
|----------|-----------|-------------|--------|---------------|
| AddHLSVideoStream | Beta | Add an HLS Video Stream to a race | ❌ | — |
| DeleteMedia | Beta | Delete a Media Item | ❌ | — |
| HLSVideosForRace | Beta | List HLS Video Streams for a race | ❌ | — |
| UpdateHLSVideoStream | Beta | Update an HLS Video stream that you have previously created | ❌ | — |

**Coverage: 0/4**  
The Media controller covers HLS video stream management for races. All four endpoints are Beta stability. No `_namespaces/media.py` exists in this library.

---

## /v2/Race

| Endpoint | Stability | Description | Status | Python method |
|----------|-----------|-------------|--------|---------------|
| IsLive | Production | Check whether Race Monitor servers are currently receiving data from this race | ✅ | `client.race.is_live()` |
| RaceDetails | Production | Get information about a specific race | ✅ | `client.race.details()` |

**Coverage: 2/2**

---

## /v2/Results

| Endpoint | Stability | Description | Status | Python method |
|----------|-----------|-------------|--------|---------------|
| CompetitorDetails | Production | Get the details for an individual competitor | ✅ | `client.results.competitor_details()` |
| CompetitorsWithTransponder | Beta | Find competitors in results with the specified transponder value | ✅ | `client.results.competitors_with_transponder()` |
| GroupedSessionsForRace | Production | Get sessions grouped by category for a given race | ✅ | `client.results.grouped_sessions_for_race()` |
| RacerResultsForRace | Production | Returns competitor and session objects for the given race and transponder | ✅ | `client.results.racer_results_for_race()` |
| RacesWithTransponder | Production | Returns races containing competitors with the given transponder | ✅ | `client.results.races_with_transponder()` |
| RecentResults | Production | Find recent races with results, optionally filtered by appSectionID | ✅ | `client.results.recent_results()` |
| SearchResults | Production | Search races with results by race name and track | ✅ | `client.results.search_results()` |
| SessionDetails | Production | Get results from a given Race Session (lap times optional, large payload) | ✅ | `client.results.session_details()` |
| SessionsForRace | Production | Get sessions for a given race | ✅ | `client.results.sessions_for_race()` |
| SessionsInDateRangeForRace | Experimental | Get sessions within a date range for a given race | ✅ | `client.results.sessions_in_date_range_for_race()` |

**Coverage: 10/10**

---

## Summary

| Controller | Endpoints | Implemented | Missing |
|------------|-----------|-------------|---------|
| /v2/Account | 5 | 5 | 0 |
| /v2/Common | 6 | 6 | 0 |
| /v2/Live | 5 | 5 | 0 |
| /v2/Media | 4 | 0 | 4 |
| /v2/Race | 2 | 2 | 0 |
| /v2/Results | 10 | 10 | 0 |
| **Total** | **32** | **28** | **4** |

The only gap is `/v2/Media` — all four HLS video stream management endpoints are unimplemented. Everything else in the public API is fully covered.
