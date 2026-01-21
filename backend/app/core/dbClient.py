from typing import Optional

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import ConfigurationError, ConnectionFailure

from backend.app.core import config
from backend.app.core.logger import get_logger

logger = get_logger(__name__)

# Module-level connection pool (singleton pattern)
_client: Optional[MongoClient] = None
_collection: Optional[Collection] = None


def get_db_client() -> MongoClient:
    """
    Returns a shared MongoDB client instance (connection pool).
    Creates the client on first call, reuses on subsequent calls.
    """
    global _client

    if _client is not None:
        return _client

    if not config.MONGODB_URI:
        logger.error("MONGODB_URI not found in environment variables")
        raise ValueError("MONGODB_URI not found in .env")

    logger.info("Initializing MongoDB connection pool")

    try:
        _client = MongoClient(
            config.MONGODB_URI,
            serverSelectionTimeoutMS=config.MONGODB_TIMEOUT_MS,
            maxPoolSize=10,
            minPoolSize=1,
        )

        # Verify connection is working
        _client.admin.command("ping")
        logger.info("MongoDB connection pool established successfully")

        return _client

    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}", exc_info=True)
        raise
    except ConfigurationError as e:
        logger.error(f"MongoDB configuration error: {e}", exc_info=True)
        raise


def get_db_collection() -> Collection:
    """
    Returns the specific MongoDB collection for storing searches.
    Uses the shared connection pool.
    """
    global _collection

    if _collection is not None:
        return _collection

    client = get_db_client()

    # Select Database & Collection
    db = client.get_database(config.MONGODB_DB_NAME)
    _collection = db.get_collection(config.MONGODB_COLLECTION_NAME)

    logger.debug(
        f"Using database: {config.MONGODB_DB_NAME}, collection: {config.MONGODB_COLLECTION_NAME}"
    )
    return _collection


def close_db_connection():
    """
    Closes the MongoDB connection pool.
    Should be called on application shutdown.
    """
    global _client, _collection

    if _client is not None:
        logger.info("Closing MongoDB connection pool")
        _client.close()
        _client = None
        _collection = None


def check_db_health() -> bool:
    """
    Check if MongoDB connection is healthy.
    Returns True if connected, False otherwise.
    """
    try:
        client = get_db_client()
        client.admin.command("ping")
        return True
    except Exception as e:
        logger.warning(f"MongoDB health check failed: {e}")
        return False
