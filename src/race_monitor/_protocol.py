from dataclasses import dataclass


@dataclass(frozen=True)
class StreamingCommand:
    """Metadata for a Race Monitor live streaming protocol command."""

    name: str
    description: str
    when: str


_COMMAND_INFO: dict[str, StreamingCommand] = {
    "A": StreamingCommand(
        "Competitor Information",
        "Racer ID, number, transponder, name, nationality, class",
        "On connect, info change, or reset",
    ),
    "B": StreamingCommand(
        "Run Information",
        "Run ID and session name",
        "On connect, session name change, or reset",
    ),
    "C": StreamingCommand(
        "Class Information",
        "Class ID and description",
        "On connect, class description change, or reset",
    ),
    "COMP": StreamingCommand(
        "Competitor Information (extended)",
        "Racer ID, number, class, name, nationality, additional data",
        "On connect, info change, or reset",
    ),
    "E": StreamingCommand(
        "Setting Information",
        "Track name or track length setting",
        "On setting update or reset",
    ),
    "F": StreamingCommand(
        "Heartbeat",
        "Laps to go, time to go, time of day, race time, flag status",
        "Every second",
    ),
    "G": StreamingCommand(
        "Race Information",
        "Race position, racer ID, laps completed, total time",
        "On connect, race info change, or reset",
    ),
    "H": StreamingCommand(
        "Qualifying Information",
        "Qualifying position, racer ID, best lap number and time",
        "On connect, qualifying info update, or reset",
    ),
    "I": StreamingCommand(
        "Reset Command",
        "Time of day and date from timing system",
        "On run group change or manual reset",
    ),
    "J": StreamingCommand(
        "Passing Information",
        "Racer ID, lap time, total time",
        "On connect and each timing loop crossing; not sent on reset",
    ),
    "RMS": StreamingCommand(
        "Sort Mode",
        "Sort order: 'race' or 'qualifying'",
        "On connect and sort mode change",
    ),
    "RMLT": StreamingCommand(
        "Lap Ticks",
        "Racer ID and epoch-ms timestamp of last passing",
        "On connect and each passing ($J)",
    ),
    "RMDTL": StreamingCommand(
        "Don't Track Locally",
        "Signals that historical laps can be fetched from the server",
        "On connect",
    ),
    "RMCA": StreamingCommand(
        "Clock Adjust",
        "Relay server epoch-ms time for correlating $RMLT timestamps",
        "On connect",
    ),
    "RMHL": StreamingCommand(
        "Historical Lap",
        "Racer ID, lap number, position, lap time, flag status, total time",
        "On new lap entry or $GET,RACERID request",
    ),
}


def is_streaming_command(value: object) -> bool:
    """Return True if *value* is a Race Monitor streaming protocol command token.

    The REST API occasionally returns streaming protocol tokens (e.g. ``'$J'``,
    ``'$G'``) in response fields such as ``Lap`` or ``Position``. Use this to
    distinguish those values from other unparseable data in error paths.

    Returns False for any non-string input, strings that do not start with
    ``'$'``, and ``'$'``-prefixed strings whose suffix is not a known command.
    Never raises.
    """
    if not isinstance(value, str) or not value.startswith("$"):
        return False
    return value[1:] in _COMMAND_INFO


def get_streaming_command(value: object) -> StreamingCommand | None:
    """Return protocol metadata for a streaming command token, or None.

    Returns None if *value* is not a string, does not start with ``'$'``, or
    its suffix is not a known command name. Never raises.
    """
    if not isinstance(value, str) or not value.startswith("$"):
        return None
    return _COMMAND_INFO.get(value[1:])
