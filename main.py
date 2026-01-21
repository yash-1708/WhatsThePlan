import time
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from backend.app.core import config
from backend.app.core.dbClient import check_db_health, close_db_connection
from backend.app.core.logger import get_logger
from backend.app.graph import build_graph

logger = get_logger(__name__)

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Tavily Events Finder API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
    close_db_connection()


class SearchRequest(BaseModel):
    query: str


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    Returns service status and component health.
    """
    db_healthy = check_db_health()

    status = "healthy" if db_healthy else "degraded"
    status_code = 200 if db_healthy else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": status,
            "components": {
                "api": "healthy",
                "database": "healthy" if db_healthy else "unhealthy",
            },
        },
    )


@app.post("/search")
@limiter.limit("10/minute")
async def search_events(request: Request, search_request: SearchRequest):
    start_time = time.time()

    try:
        graph = build_graph()

        initial_state = {
            "user_query": search_request.query,
            "current_date": datetime.now().strftime("%Y-%m-%d"),
            "retry_count": 0,
        }

        logger.info(f"Processing query: {search_request.query}")
        result = await graph.ainvoke(initial_state)

        events = result.get("events", [])
        elapsed_time = round(time.time() - start_time, 2)

        logger.info(
            f"Search completed: {len(events)} events found in {elapsed_time}s "
            f"(search_id: {result.get('search_id')})"
        )

        # Pure JSON Response for UI
        return {
            "status": "success",
            "search_id": result.get("search_id"),
            "query_status": result.get("query_status"),
            "elapsed_time": elapsed_time,
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
