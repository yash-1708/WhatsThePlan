from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
import os
from dotenv import load_dotenv
from backend.app.core.logger import get_logger

load_dotenv()

logger = get_logger(__name__)

def get_db_collection():
    """
    Returns the specific MongoDB collection for storing searches.
    """
    # 1. Get URI from env
    uri = os.getenv("MONGODB_URI")
    if not uri:
        logger.error("MONGODB_URI not found in environment variables")
        raise ValueError("MONGODB_URI not found in .env")

    logger.debug("Connecting to MongoDB")

    try:
        # 2. Connect
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)

        # 3. Verify connection is working
        client.admin.command('ping')
        logger.debug("MongoDB connection established successfully")

        # 4. Select Database & Collection
        db_name = "tavily_events_db"
        collection_name = "searches"
        db = client.get_database(db_name)
        collection = db.get_collection(collection_name)

        logger.debug(f"Using database: {db_name}, collection: {collection_name}")
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
