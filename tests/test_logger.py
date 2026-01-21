"""
Tests for backend.app.core.logger module.
"""

import logging


class TestGetLogger:
    """Tests for get_logger function."""

    def test_creates_logger_with_name(self):
        """Should create a logger with the specified name."""
        from backend.app.core.logger import get_logger

        logger = get_logger("test.module")
        assert logger.name == "test.module"

    def test_logger_has_handler(self):
        """Should add a StreamHandler to the logger."""
        from backend.app.core.logger import get_logger

        logger = get_logger("test.handler")
        # Check that at least one handler exists
        assert len(logger.handlers) >= 1
        # Check that one of them is a StreamHandler
        handler_types = [type(h).__name__ for h in logger.handlers]
        assert "StreamHandler" in handler_types

    def test_logger_respects_log_level(self, monkeypatch):
        """Should set the correct log level from config."""
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")

        # Force reimport
        import importlib

        from backend.app.core import config, logger

        importlib.reload(config)
        importlib.reload(logger)

        test_logger = logger.get_logger("test.level")
        assert test_logger.level == logging.DEBUG

    def test_logger_prevents_duplicate_handlers(self):
        """Should not add duplicate handlers when called multiple times."""
        from backend.app.core.logger import get_logger

        # Get the same logger twice
        logger1 = get_logger("test.duplicate")
        handler_count_1 = len(logger1.handlers)

        logger2 = get_logger("test.duplicate")
        handler_count_2 = len(logger2.handlers)

        # Should be the same logger instance
        assert logger1 is logger2
        # Handler count should not increase
        assert handler_count_1 == handler_count_2

    def test_logger_format_includes_required_fields(self):
        """Should format logs with timestamp, name, level, and message."""
        from backend.app.core.logger import get_logger

        logger = get_logger("test.format")

        # Find the StreamHandler
        stream_handler = None
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                stream_handler = handler
                break

        assert stream_handler is not None
        format_str = stream_handler.formatter._fmt
        assert "%(asctime)s" in format_str
        assert "%(name)s" in format_str
        assert "%(levelname)s" in format_str
        assert "%(message)s" in format_str

    def test_logger_does_not_propagate(self):
        """Should set propagate=False to avoid duplicate logs."""
        from backend.app.core.logger import get_logger

        logger = get_logger("test.propagate")
        assert logger.propagate is False
