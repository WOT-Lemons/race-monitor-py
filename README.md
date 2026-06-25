# race-monitor-py

A Python library for [Race Monitor](https://www.race-monitor.com/)

[![Python Tests](https://github.com/WOT-Lemons/race-monitor-py/actions/workflows/pytest.yml/badge.svg?branch=main&event=push)](https://github.com/WOT-Lemons/race-monitor-py/actions/workflows/pytest.yml)

## Requirements

- Python 3.10 or later
- A Race Monitor API token — obtainable from your account at [race-monitor.com](https://www.race-monitor.com/)

## Installation

```bash
pip install race-monitor
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add race-monitor
```

## Quick Start

### Sync

```python
from race_monitor import RaceMonitorClient

with RaceMonitorClient(api_token="YOUR_TOKEN") as client:
    race = client.race.details(race_id=12345)
    print(race["Race"]["Name"])

    if client.race.is_live(race_id=12345)["IsLive"]:
        session = client.live.get_session(race_id=12345)
        for racer_id, competitor in session["Session"]["Competitors"].items():
            print(competitor["Position"], competitor["FirstName"], competitor["LastName"])
```

### Async

```python
import asyncio
from race_monitor import AsyncRaceMonitorClient

async def main():
    async with AsyncRaceMonitorClient(api_token="YOUR_TOKEN") as client:
        race = await client.race.details(race_id=12345)
        print(race["Race"]["Name"])

asyncio.run(main())
```

## API Namespaces

All endpoints are grouped into namespaces, accessible as `client.<namespace>`:

| Namespace | Description |
| --------- | ----------- |
| `account` | Races associated with your relaying account |
| `common` | Reference data: app sections, race types, series |
| `live` | Real-time timing data: session, competitors, lap times |
| `race` | Race details and live status |
| `results` | Post-race results and competitor details |

## Type Annotations

All methods return typed dicts from `race_monitor.types`, enabling IDE autocompletion
and static type checking:

```python
from race_monitor import RaceMonitorClient
from race_monitor.types import GetSessionResponse, LiveCompetitor

with RaceMonitorClient(api_token="YOUR_TOKEN") as client:
    session: GetSessionResponse = client.live.get_session(race_id=12345)
    competitor: LiveCompetitor = session["Session"]["Competitors"]["42"]
```

## Contributing

Contributions are welcome. A few areas where help is especially useful:

- **Live streaming** — `client.live.get_streaming_connection()` returns a socket endpoint, but testing the full streaming protocol requires an active Race Monitor relay account. If you have relay access and want to validate or extend the streaming support, please open an issue or PR.
- **Media endpoints** — The `/v2/Media` controller (HLS video stream management) is not yet implemented. See [`docs/api-coverage.md`](docs/api-coverage.md) for the full list of missing endpoints.

## Documentation

- Full library API reference: <https://wot-lemons.github.io/race-monitor-py>
- Race Monitor API: <https://www.race-monitor.com/APIDocs>
- API coverage: [`docs/api-coverage.md`](docs/api-coverage.md)
