from pymongo import MongoClient
from pymongo.errors import ConfigurationError, ConnectionFailure

from backend.app.core import config
from backend.app.core.logger import get_logger

logger = get_logger(__name__)


def get_db_collection():
    """
    Returns the specific MongoDB collection for storing searches.
    """
    if not config.MONGODB_URI:
        logger.error("MONGODB_URI not found in environment variables")
        raise ValueError("MONGODB_URI not found in .env")

    logger.debug("Connecting to MongoDB")

    try:
        client: MongoClient = MongoClient(
            config.MONGODB_URI,
            serverSelectionTimeoutMS=config.MONGODB_TIMEOUT_MS
        )

        # Verify connection is working
        client.admin.command('ping')
        logger.debug("MongoDB connection established successfully")

        # Select Database & Collection
        db = client.get_database(config.MONGODB_DB_NAME)
        collection = db.get_collection(config.MONGODB_COLLECTION_NAME)

        logger.debug(f"Using database: {config.MONGODB_DB_NAME}, collection: {config.MONGODB_COLLECTION_NAME}")
        return collection

    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}", exc_info=True)
        raise
    except ConfigurationError as e:
        logger.error(f"MongoDB configuration error: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {e}", exc_info=True)
        raise
