from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.app.graph import build_graph
from backend.app.core.logger import get_logger
from datetime import datetime
import uvicorn
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

logger = get_logger(__name__)

app = FastAPI(title="Tavily Events Finder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify domain.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Tavily Events Finder API")
    logger.info("CORS enabled for all origins (configure for production)")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Tavily Events Finder API")

class SearchRequest(BaseModel):
    query: str

@app.post("/search")
async def search_events(request: SearchRequest):
    try:
        graph = build_graph()
        
        initial_state = {
            "user_query": request.query,
            "current_date": datetime.now().strftime("%Y-%m-%d"),
            "retry_count": 0
        }
        
        logger.info(f"Processing query: {request.query}")
        result = await graph.ainvoke(initial_state)

        events = result.get("events", [])
        logger.info(f"Search completed: {len(events)} events found (search_id: {result.get('search_id')})")

        # Pure JSON Response for UI
        return {
            "status": "success",
            "search_id": result.get("search_id"),
            "query_status": result.get("query_status"),
            # The UI will loop through this list to create elements
            "events": [e.model_dump() for e in events]
        }

    except Exception as e:
        logger.error(f"Error processing search request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/")
async def read_root():
    # When user visits root URL, serve the index.html
    return FileResponse('frontend/index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)