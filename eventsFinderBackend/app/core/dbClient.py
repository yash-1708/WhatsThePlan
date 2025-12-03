from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_collection():
    """
    Returns the specific MongoDB collection for storing searches.
    """
    # 1. Get URI from env
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise ValueError("MONGODB_URI not found in .env")

    # 2. Connect
    client = MongoClient(uri)
    
    # 3. Select Database & Collection
    # DB 'tavily_events_db' and collection 'searches'
    db = client.get_database("tavily_events_db")
    return db.get_collection("searches")