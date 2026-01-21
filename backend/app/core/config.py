"""
Central configuration module for the WhatsThePlan application.

All configurable values are loaded from environment variables with sensible defaults.
"""

import os

from dotenv import load_dotenv

load_dotenv()


def _get_bool(key: str, default: bool) -> bool:
    """Parse boolean from environment variable."""
    value = os.getenv(key)
    if value is None:
        return default
    return value.lower() in ("true", "1", "yes")


def _get_int(key: str, default: int) -> int:
    """Parse integer from environment variable."""
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _get_float(key: str, default: float) -> float:
    """Parse float from environment variable."""
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _get_list(key: str, default: list) -> list:
    """Parse comma-separated list from environment variable."""
    value = os.getenv(key)
    if value is None:
        return default
    if value == "*":
        return ["*"]
    return [item.strip() for item in value.split(",") if item.strip()]


# =============================================================================
# API Keys (required)
# =============================================================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")

# =============================================================================
# LLM Configuration
# =============================================================================
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
LLM_TEMPERATURE = _get_float("LLM_TEMPERATURE", 0.0)

# =============================================================================
# Tavily Search Configuration
# =============================================================================
TAVILY_MAX_RESULTS = _get_int("TAVILY_MAX_RESULTS", 3)
TAVILY_SEARCH_DEPTH = os.getenv("TAVILY_SEARCH_DEPTH", "advanced")
TAVILY_INCLUDE_ANSWER = _get_bool("TAVILY_INCLUDE_ANSWER", True)

# =============================================================================
# Agent Configuration
# =============================================================================
MAX_RETRY_COUNT = _get_int("MAX_RETRY_COUNT", 1)
REWRITER_NUM_QUERIES = _get_int("REWRITER_NUM_QUERIES", 3)

# =============================================================================
# MongoDB Configuration
# =============================================================================
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "tavily_events_db")
MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME", "searches")
MONGODB_TIMEOUT_MS = _get_int("MONGODB_TIMEOUT_MS", 5000)

# =============================================================================
# Server Configuration
# =============================================================================
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = _get_int("PORT", 8000)
UVICORN_RELOAD = _get_bool("UVICORN_RELOAD", True)

# =============================================================================
# CORS Configuration
# =============================================================================
CORS_ORIGINS = _get_list("CORS_ORIGINS", ["*"])

# =============================================================================
# Logging Configuration
# =============================================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
