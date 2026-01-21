from tavily import TavilyClient, AsyncTavilyClient
import os
from dotenv import load_dotenv
from backend.app.core.logger import get_logger

load_dotenv()

logger = get_logger(__name__)

def get_tavily_client():
    """Initialize the Tavily client with the API key."""
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        logger.error("TAVILY_API_KEY not found in environment variables")
        raise ValueError("TAVILY_API_KEY not found in .env")

    logger.debug("Initializing sync Tavily client")

    try:
        client = TavilyClient(api_key=api_key)
        logger.debug("Sync Tavily client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize sync Tavily client: {e}", exc_info=True)
        raise

def get_async_tavily_client():
    """Async client for parallel operations."""
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        logger.error("TAVILY_API_KEY not found in environment variables")
        raise ValueError("TAVILY_API_KEY not found in .env")

    logger.debug("Initializing async Tavily client")

    try:
        client = AsyncTavilyClient(api_key=api_key)
        logger.debug("Async Tavily client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize async Tavily client: {e}", exc_info=True)
        raise
