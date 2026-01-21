from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.app.core import config
from backend.app.core.logger import get_logger
from backend.app.graph import build_graph

logger = get_logger(__name__)

app = FastAPI(title="Tavily Events Finder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Tavily Events Finder API")
    if ["*"] == config.CORS_ORIGINS:
        logger.info("CORS enabled for all origins (configure CORS_ORIGINS for production)")
    else:
        logger.info(f"CORS enabled for: {config.CORS_ORIGINS}")


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
            "retry_count": 0,
        }

        logger.info(f"Processing query: {request.query}")
        result = await graph.ainvoke(initial_state)

        events = result.get("events", [])
        logger.info(
            f"Search completed: {len(events)} events found (search_id: {result.get('search_id')})"
        )

        # Pure JSON Response for UI
        return {
            "status": "success",
            "search_id": result.get("search_id"),
            "query_status": result.get("query_status"),
            # The UI will loop through this list to create elements
            "events": [e.model_dump() for e in events],
        }

    except Exception as e:
        logger.error(f"Error processing search request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


@app.get("/")
async def read_root():
    # When user visits root URL, serve the index.html
    return FileResponse("frontend/index.html")


if __name__ == "__main__":
    logger.info(f"Starting server on {config.SERVER_HOST}:{config.SERVER_PORT}")
    uvicorn.run(
        "main:app", host=config.SERVER_HOST, port=config.SERVER_PORT, reload=config.UVICORN_RELOAD
    )
