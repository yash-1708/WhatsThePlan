from eventsFinderBackend.app.core.tavilyClient import get_tavily_client
from eventsFinderBackend.app.models.schemas import AgentState
import json

def search_node(state: AgentState):
    """
    Agent 2: Execute search queries using the Tavily API.
    """
    queries = state["search_queries"]
    print(f"--- AGENT 2: SEARCHING TAVILY ({len(queries)} queries) ---")
    
    tavily = get_tavily_client()
    all_results = []

    # Execute searches
    # Note: In a production app, we would run these in parallel (async).
    # For this simple setup, a loop is sufficient and safer to debug.
    for q in queries:
        try:
            # We use 'search_depth="advanced"' for better quality results
            response = tavily.search(query=q, search_depth="advanced", max_results=3)
            
            # Tag each result with the query that generated it for context
            for result in response.get('results', []):
                if result.get('score', 0) < 0.4:
                    continue  # Skip low-confidence results
                result['query_context'] = q
                all_results.append(result)
                
        except Exception as e:
            print(f"Error searching for '{q}': {e}")

    print(f"--- FOUND {len(all_results)} RAW RESULTS ---")
    
    # Return the update to the state
    return {"raw_results": all_results}