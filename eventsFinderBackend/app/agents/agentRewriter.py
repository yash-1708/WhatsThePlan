from langchain_core.messages import SystemMessage, HumanMessage
from eventsFinderBackend.app.core.llmClient import get_llm
from eventsFinderBackend.app.models.schemas import AgentState
from pydantic import BaseModel, Field
from typing import List
import datetime

class QueryList(BaseModel):
    queries: List[str] = Field(description="A list of targeted search queries.")

def query_rewriter_node(state: AgentState):
    """
    Agent 1: Analyze user input and generate search queries.
    Now includes logic to handle RETRIES by broadening the scope.
    """
    user_query = state["user_query"]
    # Default to 0 if not set
    retry_count = state.get("retry_count", 0)
    current_date = state.get("current_date", datetime.datetime.now().strftime("%Y-%m-%d"))
    
    print(f"--- AGENT 1: REWRITING QUERY (Attempt: {retry_count + 1}) ---")

    llm = get_llm(temperature=0)
    structured_llm = llm.with_structured_output(QueryList)

    # Standard Prompt
    system_msg = f"""You are an expert event researcher. Current Date: {current_date}.
    Generate 3-5 targeted search queries for the user's request.
    Resolve relative dates (e.g., "this weekend") to specific YYYY-MM-DD dates.
    """

    # --- RETRY LOGIC ---
    # If this is a retry (retry_count > 0), we modify the instructions.
    if retry_count > 0:
        system_msg += """
        \nIMPORTANT: Your previous queries returned ZERO results.
        Please generate NEW queries that are BROADER and less specific.
        - Try removing specific venue names.
        - Try broader date ranges.
        - Try general terms like "events near me" or "city calendar".
        - Try searching for generic events in the specified location and date range.
        Ensure the new queries still relate to the user's original intent.
        """

    msg = [SystemMessage(content=system_msg), HumanMessage(content=user_query)]

    response = structured_llm.invoke(msg)
    
    # Return state update: New queries AND incremented retry_count
    return {
        "search_queries": response.queries,
        "retry_count": retry_count + 1
    }