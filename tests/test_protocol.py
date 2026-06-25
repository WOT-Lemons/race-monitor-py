import dataclasses

import pytest

import race_monitor._protocol as _mod
from race_monitor._protocol import StreamingCommand


class TestIsStreamingCommand:
    @pytest.mark.parametrize("token", [
        "$A", "$B", "$C", "$COMP", "$E", "$F", "$G", "$H", "$I", "$J",
        "$RMS", "$RMLT", "$RMDTL", "$RMCA", "$RMHL",
    ])
    def test_returns_true_for_all_known_commands(self, token):
        assert _mod.is_streaming_command(token) is True

    @pytest.mark.parametrize("value", [
        "3$H",       # seen in LapTime field in production — has $ but not at start
        "$UNKNOWN",  # unknown command name
        "$",         # bare dollar sign, no command name
        "",
        None,
        42,
        [],
    ])
    def test_returns_false_for_non_commands(self, value):
        assert _mod.is_streaming_command(value) is False


class TestGetStreamingCommand:
    def test_returns_streaming_command_for_known_token(self):
        result = _mod.get_streaming_command("$J")
        assert isinstance(result, StreamingCommand)
        assert result.name == "Passing Information"

    def test_returns_none_for_unknown_token(self):
        assert _mod.get_streaming_command("$UNKNOWN") is None

    def test_returns_none_for_none_input(self):
        assert _mod.get_streaming_command(None) is None

    def test_returns_none_for_bare_dollar(self):
        assert _mod.get_streaming_command("$") is None

    def test_returns_none_for_no_leading_dollar(self):
        assert _mod.get_streaming_command("3$H") is None

    @pytest.mark.parametrize("token", [
        "$A", "$B", "$C", "$COMP", "$E", "$F", "$G", "$H", "$I", "$J",
        "$RMS", "$RMLT", "$RMDTL", "$RMCA", "$RMHL",
    ])
    def test_all_known_commands_return_streaming_command(self, token):
        result = _mod.get_streaming_command(token)
        assert isinstance(result, StreamingCommand)
        assert result.token == token
        assert result.name
        assert result.description
        assert result.when

    def test_g_command_details(self):
        result = _mod.get_streaming_command("$G")
        assert result.name == "Race Information"
        assert "position" in result.description.lower()

    def test_rmhl_command_details(self):
        result = _mod.get_streaming_command("$RMHL")
        assert result.name == "Historical Lap"

    def test_f_command_sent_every_second(self):
        result = _mod.get_streaming_command("$F")
        assert "second" in result.when.lower()


class TestStreamingCommandDataclass:
    def test_is_frozen(self):
        cmd = _mod.get_streaming_command("$J")
        with pytest.raises(dataclasses.FrozenInstanceError):
            cmd.name = "mutated"  # type: ignore[misc]

    def test_fields_are_accessible(self):
        cmd = _mod.get_streaming_command("$A")
        assert hasattr(cmd, "token")
        assert hasattr(cmd, "name")
        assert hasattr(cmd, "description")
        assert hasattr(cmd, "when")

    def test_token_matches_lookup_key(self):
        cmd = _mod.get_streaming_command("$J")
        assert cmd.token == "$J"

    def test_token_field_on_construction(self):
        cmd = StreamingCommand(token="$X", name="Test", description="desc", when="always")
        assert cmd.token == "$X"


class TestGetAllStreamingCommands:
    def test_returns_all_commands(self):
        result = _mod.get_all_streaming_commands()
        assert len(result) == len(_mod._COMMAND_INFO)

    def test_values_are_streaming_commands(self):
        result = _mod.get_all_streaming_commands()
        assert all(isinstance(v, StreamingCommand) for v in result.values())

    def test_keys_are_dollar_prefixed_tokens(self):
        result = _mod.get_all_streaming_commands()
        assert all(k.startswith("$") for k in result)

    def test_known_token_present(self):
        result = _mod.get_all_streaming_commands()
        assert "$J" in result
        assert result["$J"].name == "Passing Information"

    def test_keys_match_token_field(self):
        result = _mod.get_all_streaming_commands()
        assert all(k == v.token for k, v in result.items())

    def test_returns_independent_copy(self):
        result1 = _mod.get_all_streaming_commands()
        result1["$FAKE"] = None  # type: ignore[assignment]
        result2 = _mod.get_all_streaming_commands()
        assert "$FAKE" not in result2


class TestPublicExports:
    def test_is_streaming_command_importable_from_package(self):
        from race_monitor import is_streaming_command
        assert is_streaming_command("$J") is True

    def test_get_streaming_command_importable_from_package(self):
        from race_monitor import get_streaming_command
        result = get_streaming_command("$J")
        assert result is not None
        assert result.name == "Passing Information"

    def test_streaming_command_importable_from_package(self):
        from race_monitor import StreamingCommand
        assert StreamingCommand(token="$X", name="a", description="b", when="c").name == "a"

    def test_get_all_streaming_commands_importable_from_package(self):
        from race_monitor import get_all_streaming_commands
        result = get_all_streaming_commands()
        assert len(result) == len(_mod._COMMAND_INFO)
        assert all(k == v.token for k, v in result.items())
