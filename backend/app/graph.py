from langgraph.graph import StateGraph, START, END
from backend.app.models.schemas import AgentState
from backend.app.agents.agentRewriter import query_rewriter_node
from backend.app.agents.agentSearch import search_node
from backend.app.agents.agentExtractor import extraction_node
from backend.app.agents.agentPersistence import persistence_node
from backend.app.agents.agentValidator import query_validator_node # <--- NEW IMPORT

def check_results(state: AgentState):
    """
    Determines if the extraction was successful, needs a retry, or should give up.
    """
    events = state.get("events", [])
    retry_count = state.get("retry_count", 0)

    if events:
        return "success"
    elif retry_count < 1:
        # Increment retry count and signal to retry
        state["retry_count"] = retry_count + 1 
        print(f"--- DECISION: RETRY. Attempt: {retry_count + 1} ---")
        return "retry"
    else:
        print("--- DECISION: GIVE UP. Max retries reached ---")
        return "give_up"


def build_graph():
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("validator", query_validator_node) # <--- AGENT 0: VALIDATION
    workflow.add_node("rewriter", query_rewriter_node)  # <--- AGENT 1: REWRITE
    workflow.add_node("searcher", search_node)          # <--- AGENT 2: SEARCH
    workflow.add_node("extractor", extraction_node)     # <--- AGENT 3: EXTRACTION
    workflow.add_node("persistence", persistence_node)  # <--- AGENT 4: PERSISTENCE

    # 1. Starting Point: Validator
    # All queries must first pass through the validator.
    workflow.add_edge(START, "validator")
    
    # 2. Conditional Edge after Validator
    # The graph routes based on the 'query_status' output by the validator agent.
    workflow.add_conditional_edges(
        "validator",
        # Router function based on the validator's output
        lambda state: state.get("query_status"),
        {
            "valid": "rewriter",  # If valid, proceed to the Rewriter (Agent 1)
            "invalid": END,       # If invalid, stop the graph immediately
        }
    )

    # 3. Standard Edges
    workflow.add_edge("rewriter", "searcher")
    workflow.add_edge("searcher", "extractor")

    # 4. Conditional Edge after Extractor (Retry/Success/Give Up)
    # This logic remains the same: retry if needed, otherwise persist/end.
    workflow.add_conditional_edges(
        "extractor",
        check_results,
        {
            "success": "persistence",
            "retry": "rewriter",
            "give_up": "persistence" 
        }
    )
    
    # 5. Final Flow
    workflow.add_edge("persistence", END)

    return workflow.compile()