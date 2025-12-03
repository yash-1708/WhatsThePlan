from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.app.graph import build_graph
from datetime import datetime
import uvicorn
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Tavily Events Finder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev/demo, allow all. For production, specify domain.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        
        print(f"Processing: {request.query}")
        result = await graph.ainvoke(initial_state)
        
        # Pure JSON Response for your UI
        return {
            "status": "success",
            "search_id": result.get("search_id"),
            # The UI will loop through this list to create elements
            "events": [e.model_dump() for e in result.get("events", [])]
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/")
async def read_root():
    # When user visits root URL, serve the index.html
    return FileResponse('frontend/index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)