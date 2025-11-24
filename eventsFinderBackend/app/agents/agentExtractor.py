from langchain_core.messages import SystemMessage, HumanMessage
from eventsFinderBackend.app.core.llmClient import get_llm
from eventsFinderBackend.app.models.schemas import AgentState, Event
from pydantic import BaseModel, Field
from typing import List
import json

# --- 1. Output Wrapper ---
class EventList(BaseModel):
    """A list of extracted events."""
    events: List[Event] = Field(description="The list of events found in the text.")

# --- 2. The Agent Function ---
def extraction_node(state: AgentState):
    """
    Agent 3: Extract structured event data from raw search results.
    """
    raw_results = state.get("raw_results", [])
    user_query = state["user_query"]
    current_date = state["current_date"]
    
    print(f"--- AGENT 3: EXTRACTING EVENTS (Input: {len(raw_results)} snippets) ---")
    
    # If no results, return empty list immediately
    if not raw_results:
        return {"events": []}

    # Prepare the context text for the LLM
    # We join titles and content to give the LLM the full picture
    context_text = "\n\n".join([
        f"Source {i+1} ({r.get('url', 'N/A')}):\nTitle: {r.get('title', '')}\nContent: {r.get('content', '')}"
        for i, r in enumerate(raw_results)
    ])

    # Initialize LLM
    llm = get_llm(temperature=0)
    structured_llm = llm.with_structured_output(EventList)

    # System Prompt
    system_msg = f"""You are an expert data extraction assistant.
    
    Context:
    - Current Date: {current_date}
    - User Query: {user_query}
    
    Your Goal:
    Extract a list of unique events from the provided search results.
    
    Guidelines:
    1. FOCUS on events that match the user's specific query (location, topic, date).
    2. DEDUPLICATE: If multiple sources mention the same event, combine the info into one entry.
    3. RESOLVE DATES: Convert "tonight" or "this Friday" to actual dates (YYYY-MM-DD) based on Current Date.
    4. IGNORE: General articles, "top 10" lists without specific dates, or events far in the past.
    5. If no relevant events are found, return an empty list.
    """

    msg = [
        SystemMessage(content=system_msg),
        HumanMessage(content=f"Here are the search results:\n\n{context_text}")
    ]

    # Invoke LLM
    try:
        response = structured_llm.invoke(msg)
        extracted_events = response.events
    except Exception as e:
        print(f"Error in extraction: {e}")
        extracted_events = []

    print(f"--- EXTRACTED {len(extracted_events)} EVENTS ---")
    
    return {"events": extracted_events}