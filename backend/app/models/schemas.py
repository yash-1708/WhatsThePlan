from typing import Optional, TypedDict

from pydantic import BaseModel, Field

# --- 1. Structured Output Models (Pydantic) ---
# These ensure the LLM generates clean data we can save to MongoDB.


class Event(BaseModel):
    """Structured data model for a single event extracted from search results."""

    title: str = Field(description="The name of the event.")
    date: str = Field(
        description="The specific date or time of the event (e.g., '2023-12-25' or 'Friday, 8:00 PM')."
    )
    location: str = Field(description="The venue, city, or address of the event.")
    description: str = Field(description="A brief summary of what the event is.")
    url: str = Field(description="The URL where the event information was found.")
    score: Optional[float] = Field(
        description="A relevance score (1-10) assigned by the agent.", default=None
    )


# --- 2. LangGraph State (TypedDict) ---
# This is the shared memory passed between agents.


class AgentState(TypedDict):
    # --- Inputs ---
    user_query: str  # The raw query from the user
    current_date: str  # Grounding context (e.g., "Friday, Nov 24, 2023")

    # --- Internal Logic ---
    retry_count: int  # To prevent infinite loops if no events are found
    search_queries: list[str]  # The generated search queries for Tavily
    query_status: str

    # --- Outputs ---
    raw_results: list[dict]  # Raw snippets from Tavily
    events: list[Event]  # The structured list of extracted events
    final_response: str  # The human-readable summary
