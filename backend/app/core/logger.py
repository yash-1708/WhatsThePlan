"""
Centralized logging configuration for the WhatsThePlan application.

Usage:
    from backend.app.core.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Message here")
"""

import logging
import os
import sys
from typing import Optional


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (typically __name__)
        level: Optional override for log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured (avoid duplicate handlers)
    if not logger.handlers:
        # Get log level from environment or use default
        log_level = level or os.getenv("LOG_LEVEL", "INFO").upper()
        logger.setLevel(getattr(logging, log_level, logging.INFO))

        # Console handler with formatting
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, log_level, logging.INFO))

        # Format: timestamp - logger name - level - message
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Prevent propagation to root logger to avoid duplicate logs
        logger.propagate = False

    return logger
