# race-monitor-py

A Python library for [Race Monitor](https://www.race-monitor.com/)

![Tests](https://github.com/WOT-Lemons/race-monitor-py/actions/workflows/pytest.yml/badge.svg?branch=main)

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

# All methods return parsed JSON as Python dicts.
with RaceMonitorClient(api_token="YOUR_TOKEN") as client:
    race = client.race.details(race_id=12345)
    print(race["Race"]["Name"])

    if client.race.is_live(race_id=12345)["IsLive"]:
        session = client.live.get_session(race_id=12345)
        # work with session data — see API docs for field names
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

## Documentation

- Full library API reference: <https://wot-lemons.github.io/race-monitor-py>
- Race Monitor API: <https://www.race-monitor.com/APIDocs>
