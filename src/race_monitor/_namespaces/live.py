from typing import Callable


class LiveNamespace:
    def __init__(self, post: Callable) -> None:
        self._post = post

    def get_racer(self, race_id: int | str, racer_id: int | str) -> dict:
        return self._post("/v2/Live/GetRacer", raceID=race_id, racerID=racer_id)

    def get_racer_count(self, race_id: int | str) -> dict:
        return self._post("/v2/Live/GetRacerCount", raceID=race_id)

    def get_session(self, race_id: int | str) -> dict:
        return self._post("/v2/Live/GetSession", raceID=race_id)

    def get_streaming_connection(
        self, race_id: int | str, use_host_name_for_socket: bool = False
    ) -> dict:
        return self._post(
            "/v2/Live/GetStreamingConnection",
            raceID=race_id,
            useHostNameForSocket=use_host_name_for_socket,
        )

    def get_web_timing(
        self,
        source_mode: str,
        source_mode_value: int,
        layout: str = "auto",
        width: int = 550,
        height: int = 510,
        style_id: int = 0,
    ) -> dict:
        return self._post(
            "/v2/Live/GetWebTiming",
            sourceMode=source_mode,
            sourceModeValue=source_mode_value,
            layout=layout,
            width=width,
            height=height,
            styleID=style_id,
        )


class AsyncLiveNamespace:
    def __init__(self, post: Callable) -> None:
        self._post = post

    async def get_racer(self, race_id: int | str, racer_id: int | str) -> dict:
        return await self._post("/v2/Live/GetRacer", raceID=race_id, racerID=racer_id)

    async def get_racer_count(self, race_id: int | str) -> dict:
        return await self._post("/v2/Live/GetRacerCount", raceID=race_id)

    async def get_session(self, race_id: int | str) -> dict:
        return await self._post("/v2/Live/GetSession", raceID=race_id)

    async def get_streaming_connection(
        self, race_id: int | str, use_host_name_for_socket: bool = False
    ) -> dict:
        return await self._post(
            "/v2/Live/GetStreamingConnection",
            raceID=race_id,
            useHostNameForSocket=use_host_name_for_socket,
        )

    async def get_web_timing(
        self,
        source_mode: str,
        source_mode_value: int,
        layout: str = "auto",
        width: int = 550,
        height: int = 510,
        style_id: int = 0,
    ) -> dict:
        return await self._post(
            "/v2/Live/GetWebTiming",
            sourceMode=source_mode,
            sourceModeValue=source_mode_value,
            layout=layout,
            width=width,
            height=height,
            styleID=style_id,
        )
