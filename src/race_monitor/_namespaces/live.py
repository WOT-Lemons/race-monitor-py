from typing import Callable


class LiveNamespace:
    """Endpoints under /v2/Live."""

    def __init__(self, post: Callable) -> None:
        self._post = post

    def get_racer(self, race_id: int | str, racer_id: int | str) -> dict:
        """Get details for a specific competitor including all lap times.

        Stability: Production.

        Args:
            race_id: The race ID.
            racer_id: The racer/competitor ID.
        """
        return self._post("/v2/Live/GetRacer", raceID=race_id, racerID=racer_id)

    def get_racer_count(self, race_id: int | str) -> dict:
        """Get the number of racers in the current live session.

        Stability: Production.

        Args:
            race_id: The race ID.
        """
        return self._post("/v2/Live/GetRacerCount", raceID=race_id)

    def get_session(self, race_id: int | str) -> dict:
        """Get the current session state of a live race.

        Stability: Production.

        Args:
            race_id: The race ID.
        """
        return self._post("/v2/Live/GetSession", raceID=race_id)

    def get_streaming_connection(
        self, race_id: int | str, use_host_name_for_socket: bool = False
    ) -> dict:
        """Get connection info for a live socket/WebSocket streaming connection.

        Returns connection credentials only. WebSocket session management is the
        caller's responsibility. Requires a payment method on file with Race Monitor.

        Stability: Production.

        Args:
            race_id: The race ID.
            use_host_name_for_socket: Return a hostname instead of an IP for DNS
                load balancing across server clusters.
        """
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
        """Generate a web timing script block for embedding live timing.

        Stability: Beta — subject to change without notice.

        Args:
            source_mode: ``'race'`` or ``'series'``.
            source_mode_value: ID of the race or series.
            layout: ``'auto'``, ``'wide'``, ``'stacked'``, or ``'compressed'``.
            width: Display width in pixels.
            height: Display height in pixels.
            style_id: Style ID to apply (must be permitted for the race/series).
        """
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
    """Async endpoints under /v2/Live."""

    def __init__(self, post: Callable) -> None:
        self._post = post

    async def get_racer(self, race_id: int | str, racer_id: int | str) -> dict:
        """Get details for a specific competitor including all lap times.

        Stability: Production.

        Args:
            race_id: The race ID.
            racer_id: The racer/competitor ID.
        """
        return await self._post("/v2/Live/GetRacer", raceID=race_id, racerID=racer_id)

    async def get_racer_count(self, race_id: int | str) -> dict:
        """Get the number of racers in the current live session.

        Stability: Production.

        Args:
            race_id: The race ID.
        """
        return await self._post("/v2/Live/GetRacerCount", raceID=race_id)

    async def get_session(self, race_id: int | str) -> dict:
        """Get the current session state of a live race.

        Stability: Production.

        Args:
            race_id: The race ID.
        """
        return await self._post("/v2/Live/GetSession", raceID=race_id)

    async def get_streaming_connection(
        self, race_id: int | str, use_host_name_for_socket: bool = False
    ) -> dict:
        """Get connection info for a live socket/WebSocket streaming connection.

        Returns connection credentials only. WebSocket session management is the
        caller's responsibility. Requires a payment method on file with Race Monitor.

        Stability: Production.

        Args:
            race_id: The race ID.
            use_host_name_for_socket: Return a hostname instead of an IP for DNS
                load balancing across server clusters.
        """
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
        """Generate a web timing script block for embedding live timing.

        Stability: Beta — subject to change without notice.

        Args:
            source_mode: ``'race'`` or ``'series'``.
            source_mode_value: ID of the race or series.
            layout: ``'auto'``, ``'wide'``, ``'stacked'``, or ``'compressed'``.
            width: Display width in pixels.
            height: Display height in pixels.
            style_id: Style ID to apply (must be permitted for the race/series).
        """
        return await self._post(
            "/v2/Live/GetWebTiming",
            sourceMode=source_mode,
            sourceModeValue=source_mode_value,
            layout=layout,
            width=width,
            height=height,
            styleID=style_id,
        )
