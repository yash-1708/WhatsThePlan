from backend.app.core.dbClient import get_db_collection
from backend.app.core.logger import get_logger
from backend.app.models.schemas import AgentState
import datetime
import uuid

logger = get_logger(__name__)

def persistence_node(state: AgentState):
    """
    Agent 4: Save the query and results to MongoDB Atlas.
    """
    logger.info("Agent 4: Saving to MongoDB")
    
    # Prepare the document and generate a unique ID for this specific run
    search_id = str(uuid.uuid4())
    
    document = {
        "_id": search_id,
        "user_query": state.get("user_query"),
        "timestamp": datetime.datetime.utcnow(),
        "date_context": state.get("current_date"),
        "events": [event.model_dump() for event in state.get("events", [])],
        "raw_results_count": len(state.get("raw_results", [])),
        "raw_results": state.get("raw_results", []),
        "status": "SUCCESS"
    }

    # Insert into DB
    try:
        collection = get_db_collection()
        collection.insert_one(document)
        logger.info(f"Saved search with ID: {search_id}")
    except Exception as e:
        logger.error(f"Error saving to MongoDB: {e}", exc_info=True)
        
    # Don't change the state, just pass it through
    return {"search_id": search_id}