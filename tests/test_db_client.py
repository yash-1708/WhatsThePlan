"""
Tests for backend.app.core.dbClient module.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestGetDbClient:
    """Tests for get_db_client function."""

    def test_creates_client_on_first_call(self, monkeypatch):
        """Should create a new MongoDB client on first call."""
        # Reset module state
        import backend.app.core.dbClient as db_module

        db_module._client = None
        db_module._collection = None

        with patch("backend.app.core.dbClient.MongoClient") as mock_mongo:
            mock_client = MagicMock()
            mock_client.admin.command = MagicMock(return_value={"ok": 1})
            mock_mongo.return_value = mock_client

            from backend.app.core.dbClient import get_db_client

            client = get_db_client()

            mock_mongo.assert_called_once()
            assert client == mock_client

    def test_returns_cached_client_on_subsequent_calls(self):
        """Should return the same client instance on subsequent calls."""
        import backend.app.core.dbClient as db_module

        mock_client = MagicMock()
        db_module._client = mock_client

        from backend.app.core.dbClient import get_db_client

        client = get_db_client()
        assert client == mock_client

        # Reset state
        db_module._client = None

    def test_raises_error_when_mongodb_uri_missing(self, monkeypatch):
        """Should raise ValueError when MONGODB_URI is not set."""
        import backend.app.core.dbClient as db_module

        db_module._client = None
        monkeypatch.setenv("MONGODB_URI", "")

        # Reload config to pick up empty URI
        import importlib

        from backend.app.core import config

        importlib.reload(config)

        with pytest.raises(ValueError, match="MONGODB_URI not found"):
            from backend.app.core.dbClient import get_db_client

            get_db_client()

        # Reset for other tests
        db_module._client = None


class TestGetDbCollection:
    """Tests for get_db_collection function."""

    def test_returns_collection(self):
        """Should return MongoDB collection using connection pool."""
        import backend.app.core.dbClient as db_module

        db_module._client = None
        db_module._collection = None

        with patch("backend.app.core.dbClient.get_db_client") as mock_get_client:
            mock_client = MagicMock()
            mock_db = MagicMock()
            mock_collection = MagicMock()
            mock_client.get_database.return_value = mock_db
            mock_db.get_collection.return_value = mock_collection
            mock_get_client.return_value = mock_client

            from backend.app.core.dbClient import get_db_collection

            collection = get_db_collection()

            assert collection == mock_collection
            mock_client.get_database.assert_called_once()
            mock_db.get_collection.assert_called_once()

        # Reset state
        db_module._collection = None

    def test_returns_cached_collection(self):
        """Should return cached collection on subsequent calls."""
        import backend.app.core.dbClient as db_module

        mock_collection = MagicMock()
        db_module._collection = mock_collection

        from backend.app.core.dbClient import get_db_collection

        collection = get_db_collection()
        assert collection == mock_collection

        # Reset state
        db_module._collection = None


class TestCloseDbConnection:
    """Tests for close_db_connection function."""

    def test_closes_client_and_clears_cache(self):
        """Should close client and reset module state."""
        import backend.app.core.dbClient as db_module

        mock_client = MagicMock()
        mock_collection = MagicMock()
        db_module._client = mock_client
        db_module._collection = mock_collection

        from backend.app.core.dbClient import close_db_connection

        close_db_connection()

        mock_client.close.assert_called_once()
        assert db_module._client is None
        assert db_module._collection is None

    def test_handles_no_client_gracefully(self):
        """Should not error when no client exists."""
        import backend.app.core.dbClient as db_module

        db_module._client = None
        db_module._collection = None

        from backend.app.core.dbClient import close_db_connection

        # Should not raise
        close_db_connection()


class TestCheckDbHealth:
    """Tests for check_db_health function."""

    def test_returns_true_when_healthy(self):
        """Should return True when database responds to ping."""
        import backend.app.core.dbClient as db_module

        db_module._client = None

        with patch("backend.app.core.dbClient.get_db_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.admin.command = MagicMock(return_value={"ok": 1})
            mock_get_client.return_value = mock_client

            from backend.app.core.dbClient import check_db_health

            result = check_db_health()

            assert result is True
            mock_client.admin.command.assert_called_once_with("ping")

    def test_returns_false_when_unhealthy(self):
        """Should return False when database ping fails."""
        with patch("backend.app.core.dbClient.get_db_client") as mock_get_client:
            mock_get_client.side_effect = Exception("Connection failed")

            from backend.app.core.dbClient import check_db_health

            result = check_db_health()

            assert result is False
