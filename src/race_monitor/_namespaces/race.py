from typing import Callable


class RaceNamespace:
    def __init__(self, post: Callable) -> None:
        self._post = post

    def details(self, race_id: int | str) -> dict:
        return self._post("/v2/Race/RaceDetails", raceID=race_id)

    def is_live(self, race_id: int | str) -> dict:
        return self._post("/v2/Race/IsLive", raceID=race_id)


class AsyncRaceNamespace:
    def __init__(self, post: Callable) -> None:
        self._post = post

    async def details(self, race_id: int | str) -> dict:
        return await self._post("/v2/Race/RaceDetails", raceID=race_id)

    async def is_live(self, race_id: int | str) -> dict:
        return await self._post("/v2/Race/IsLive", raceID=race_id)
