import types as _types
from dataclasses import dataclass


@dataclass(frozen=True)
class StreamingCommand:
    """Metadata for a Race Monitor live streaming protocol command."""

    token: str
    name: str
    description: str
    when: str


_COMMAND_INFO: _types.MappingProxyType[str, StreamingCommand] = _types.MappingProxyType({
    "A": StreamingCommand(
        token="$A",
        name="Competitor Information",
        description="Racer ID, number, transponder, name, nationality, class",
        when="On connect, info change, or reset",
    ),
    "B": StreamingCommand(
        token="$B",
        name="Run Information",
        description="Run ID and session name",
        when="On connect, session name change, or reset",
    ),
    "C": StreamingCommand(
        token="$C",
        name="Class Information",
        description="Class ID and description",
        when="On connect, class description change, or reset",
    ),
    "COMP": StreamingCommand(
        token="$COMP",
        name="Competitor Information (extended)",
        description="Racer ID, number, class, name, nationality, additional data",
        when="On connect, info change, or reset",
    ),
    "E": StreamingCommand(
        token="$E",
        name="Setting Information",
        description="Track name or track length setting",
        when="On setting update or reset",
    ),
    "F": StreamingCommand(
        token="$F",
        name="Heartbeat",
        description="Laps to go, time to go, time of day, race time, flag status",
        when="Every second",
    ),
    "G": StreamingCommand(
        token="$G",
        name="Race Information",
        description="Race position, racer ID, laps completed, total time",
        when="On connect, race info change, or reset",
    ),
    "H": StreamingCommand(
        token="$H",
        name="Qualifying Information",
        description="Qualifying position, racer ID, best lap number and time",
        when="On connect, qualifying info update, or reset",
    ),
    "I": StreamingCommand(
        token="$I",
        name="Reset Command",
        description="Time of day and date from timing system",
        when="On run group change or manual reset",
    ),
    "J": StreamingCommand(
        token="$J",
        name="Passing Information",
        description="Racer ID, lap time, total time",
        when="On connect and each timing loop crossing; not sent on reset",
    ),
    "RMS": StreamingCommand(
        token="$RMS",
        name="Sort Mode",
        description="Sort order: 'race' or 'qualifying'",
        when="On connect and sort mode change",
    ),
    "RMLT": StreamingCommand(
        token="$RMLT",
        name="Lap Ticks",
        description="Racer ID and epoch-ms timestamp of last passing",
        when="On connect and each passing ($J)",
    ),
    "RMDTL": StreamingCommand(
        token="$RMDTL",
        name="Don't Track Locally",
        description="Signals that historical laps can be fetched from the server",
        when="On connect",
    ),
    "RMCA": StreamingCommand(
        token="$RMCA",
        name="Clock Adjust",
        description="Relay server epoch-ms time for correlating $RMLT timestamps",
        when="On connect",
    ),
    "RMHL": StreamingCommand(
        token="$RMHL",
        name="Historical Lap",
        description="Racer ID, lap number, position, lap time, flag status, total time",
        when="On new lap entry or $GET,RACERID request",
    ),
})

for _key, _cmd in _COMMAND_INFO.items():
    assert _cmd.token == f"${_key}", (
        f"_COMMAND_INFO key {_key!r} must equal cmd.token[1:], got {_cmd.token!r}"
    )
del _key, _cmd

_ALL_COMMANDS: dict[str, StreamingCommand] = {v.token: v for v in _COMMAND_INFO.values()}


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


def get_all_streaming_commands() -> dict[str, StreamingCommand]:
    """Return a copy of all known streaming commands keyed by their token (e.g. ``'$J'``)."""
    return dict(_ALL_COMMANDS)
