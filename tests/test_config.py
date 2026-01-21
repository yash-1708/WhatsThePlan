"""
Tests for backend.app.core.config module.
"""


class TestGetBool:
    """Tests for _get_bool helper function."""

    def test_returns_default_when_env_not_set(self, monkeypatch):
        """Should return default when env var is not set."""
        monkeypatch.delenv("TEST_BOOL_VAR", raising=False)

        # Import after env manipulation to get fresh module
        from backend.app.core.config import _get_bool

        assert _get_bool("TEST_BOOL_VAR", True) is True
        assert _get_bool("TEST_BOOL_VAR", False) is False

    def test_parses_true_values(self, monkeypatch):
        """Should parse 'true', '1', 'yes' as True."""
        from backend.app.core.config import _get_bool

        for value in ["true", "True", "TRUE", "1", "yes", "Yes", "YES"]:
            monkeypatch.setenv("TEST_BOOL_VAR", value)
            assert _get_bool("TEST_BOOL_VAR", False) is True

    def test_parses_false_values(self, monkeypatch):
        """Should parse other values as False."""
        from backend.app.core.config import _get_bool

        for value in ["false", "False", "0", "no", "No", "anything"]:
            monkeypatch.setenv("TEST_BOOL_VAR", value)
            assert _get_bool("TEST_BOOL_VAR", True) is False


class TestGetInt:
    """Tests for _get_int helper function."""

    def test_returns_default_when_env_not_set(self, monkeypatch):
        """Should return default when env var is not set."""
        monkeypatch.delenv("TEST_INT_VAR", raising=False)

        from backend.app.core.config import _get_int

        assert _get_int("TEST_INT_VAR", 42) == 42

    def test_parses_valid_integers(self, monkeypatch):
        """Should parse valid integer strings."""
        from backend.app.core.config import _get_int

        monkeypatch.setenv("TEST_INT_VAR", "123")
        assert _get_int("TEST_INT_VAR", 0) == 123

        monkeypatch.setenv("TEST_INT_VAR", "-5")
        assert _get_int("TEST_INT_VAR", 0) == -5

    def test_returns_default_for_invalid_integers(self, monkeypatch):
        """Should return default for non-integer strings."""
        from backend.app.core.config import _get_int

        monkeypatch.setenv("TEST_INT_VAR", "not_a_number")
        assert _get_int("TEST_INT_VAR", 99) == 99

        monkeypatch.setenv("TEST_INT_VAR", "3.14")
        assert _get_int("TEST_INT_VAR", 99) == 99


class TestGetFloat:
    """Tests for _get_float helper function."""

    def test_returns_default_when_env_not_set(self, monkeypatch):
        """Should return default when env var is not set."""
        monkeypatch.delenv("TEST_FLOAT_VAR", raising=False)

        from backend.app.core.config import _get_float

        assert _get_float("TEST_FLOAT_VAR", 3.14) == 3.14

    def test_parses_valid_floats(self, monkeypatch):
        """Should parse valid float strings."""
        from backend.app.core.config import _get_float

        monkeypatch.setenv("TEST_FLOAT_VAR", "2.5")
        assert _get_float("TEST_FLOAT_VAR", 0.0) == 2.5

        monkeypatch.setenv("TEST_FLOAT_VAR", "-1.5")
        assert _get_float("TEST_FLOAT_VAR", 0.0) == -1.5

        monkeypatch.setenv("TEST_FLOAT_VAR", "10")
        assert _get_float("TEST_FLOAT_VAR", 0.0) == 10.0

    def test_returns_default_for_invalid_floats(self, monkeypatch):
        """Should return default for non-numeric strings."""
        from backend.app.core.config import _get_float

        monkeypatch.setenv("TEST_FLOAT_VAR", "not_a_number")
        assert _get_float("TEST_FLOAT_VAR", 1.0) == 1.0


class TestGetList:
    """Tests for _get_list helper function."""

    def test_returns_default_when_env_not_set(self, monkeypatch):
        """Should return default when env var is not set."""
        monkeypatch.delenv("TEST_LIST_VAR", raising=False)

        from backend.app.core.config import _get_list

        assert _get_list("TEST_LIST_VAR", ["default"]) == ["default"]

    def test_parses_comma_separated_list(self, monkeypatch):
        """Should parse comma-separated strings into list."""
        from backend.app.core.config import _get_list

        monkeypatch.setenv("TEST_LIST_VAR", "a,b,c")
        assert _get_list("TEST_LIST_VAR", []) == ["a", "b", "c"]

        monkeypatch.setenv("TEST_LIST_VAR", "  a , b , c  ")
        assert _get_list("TEST_LIST_VAR", []) == ["a", "b", "c"]

    def test_handles_wildcard(self, monkeypatch):
        """Should return ['*'] for wildcard."""
        from backend.app.core.config import _get_list

        monkeypatch.setenv("TEST_LIST_VAR", "*")
        assert _get_list("TEST_LIST_VAR", []) == ["*"]

    def test_filters_empty_items(self, monkeypatch):
        """Should filter out empty items."""
        from backend.app.core.config import _get_list

        monkeypatch.setenv("TEST_LIST_VAR", "a,,b,  ,c")
        assert _get_list("TEST_LIST_VAR", []) == ["a", "b", "c"]


class TestConfigDefaults:
    """Tests for config default values."""

    def test_llm_defaults(self, monkeypatch):
        """Should have correct LLM defaults."""
        monkeypatch.delenv("LLM_MODEL", raising=False)
        monkeypatch.delenv("LLM_TEMPERATURE", raising=False)

        # Force reimport to get fresh values
        import importlib

        from backend.app.core import config

        importlib.reload(config)

        assert config.LLM_MODEL == "gpt-4o"
        assert config.LLM_TEMPERATURE == 0.0

    def test_server_defaults(self, monkeypatch):
        """Should have correct server defaults."""
        monkeypatch.delenv("SERVER_HOST", raising=False)
        monkeypatch.delenv("PORT", raising=False)
        monkeypatch.delenv("UVICORN_RELOAD", raising=False)

        import importlib

        from backend.app.core import config

        importlib.reload(config)

        assert config.SERVER_HOST == "0.0.0.0"
        assert config.SERVER_PORT == 8000
        assert config.UVICORN_RELOAD is True
