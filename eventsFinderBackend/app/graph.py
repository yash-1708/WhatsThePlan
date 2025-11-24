from langgraph.graph import StateGraph, START, END
from eventsFinderBackend.app.models.schemas import AgentState
from eventsFinderBackend.app.agents.agentRewriter import query_rewriter_node
from eventsFinderBackend.app.agents.agentSearch import search_node
from eventsFinderBackend.app.agents.agentExtractor import extraction_node
from eventsFinderBackend.app.agents.agentPersistence import persistence_node

def check_results(state: AgentState):
    """
    Decides the next step based on whether events were found.
    """
    events = state.get("events", [])
    retry_count = state.get("retry_count", 0)
    
    # 1. Success Case
    if len(events) > 0:
        print("--- DECISION: EVENTS FOUND -> FINISH ---")
        return "success"
    
    # 2. Retry Case (Max 1 retry, meaning 2 attempts total)
    if retry_count < 2:
        print("--- DECISION: NO EVENTS -> RETRY (Loop back to Agent 1) ---")
        return "retry"
    
    # 3. Give Up Case
    print("--- DECISION: NO EVENTS AFTER RETRY -> GIVE UP ---")
    return "give_up"

def build_graph():
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("rewriter", query_rewriter_node)
    workflow.add_node("searcher", search_node)
    workflow.add_node("extractor", extraction_node)
    workflow.add_node("persistence", persistence_node)  

    # Add Standard Edges
    workflow.add_edge(START, "rewriter")
    workflow.add_edge("rewriter", "searcher")
    workflow.add_edge("searcher", "extractor")

    # --- Conditional Edge Updated ---
    workflow.add_conditional_edges(
        "extractor",
        check_results,
        {
            "success": "persistence",  # <--- Valid results? Go to Persistence
            "retry": "rewriter",       # Logic loop
            "give_up": "persistence"   # Even if we fail, we might want to log it
        }
    )
    
    # Finish the flow
    workflow.add_edge("persistence", END) 

    return workflow.compile()