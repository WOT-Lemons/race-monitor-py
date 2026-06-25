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

    def test_does_not_raise_for_none(self):
        assert _mod.is_streaming_command(None) is False

    def test_does_not_raise_for_integer(self):
        assert _mod.is_streaming_command(42) is False


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
        with pytest.raises(Exception):
            cmd.name = "mutated"  # type: ignore[misc]

    def test_fields_are_accessible(self):
        cmd = _mod.get_streaming_command("$A")
        assert hasattr(cmd, "name")
        assert hasattr(cmd, "description")
        assert hasattr(cmd, "when")


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
        assert StreamingCommand("a", "b", "c").name == "a"
