from tavily import TavilyClient, AsyncTavilyClient
from backend.app.core.logger import get_logger
from backend.app.core import config

logger = get_logger(__name__)


def get_tavily_client():
    """Initialize the Tavily client with the API key."""
    if not config.TAVILY_API_KEY:
        logger.error("TAVILY_API_KEY not found in environment variables")
        raise ValueError("TAVILY_API_KEY not found in .env")

    logger.debug("Initializing sync Tavily client")

    try:
        client = TavilyClient(api_key=config.TAVILY_API_KEY)
        logger.debug("Sync Tavily client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize sync Tavily client: {e}", exc_info=True)
        raise


def get_async_tavily_client():
    """Async client for parallel operations."""
    if not config.TAVILY_API_KEY:
        logger.error("TAVILY_API_KEY not found in environment variables")
        raise ValueError("TAVILY_API_KEY not found in .env")

    logger.debug("Initializing async Tavily client")

    try:
        client = AsyncTavilyClient(api_key=config.TAVILY_API_KEY)
        logger.debug("Async Tavily client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize async Tavily client: {e}", exc_info=True)
        raise
