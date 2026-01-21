from langchain_core.messages import HumanMessage, SystemMessage

from backend.app.core.llmClient import get_llm
from backend.app.core.logger import get_logger
from backend.app.models.schemas import AgentState

logger = get_logger(__name__)


def query_validator_node(state: AgentState):
    """
    Agent 0: Check if the user query is valid and relevant to event finding.

    A valid query must include:
    1. A type of event (e.g., concert, festival, show).
    2. A location (e.g., city, state, venue).

    This prevents wasting tokens on queries like "Hello" or "What is 2+2".
    The response sets 'query_status' to 'valid' or 'invalid' for the graph router.
    """
    user_query = state["user_query"]
    logger.info(f"Agent 0: Validating query: '{user_query[:50]}...'")

    llm = get_llm()

    # Concise system prompt to force fast output
    system_prompt = (
        "You are a strict query validator. Your task is to determine if a user query "
        "is a request for finding a real-world event (like a concert, festival, show, "
        "or conference) and includes a relevant location (like a city or country). "
        "Respond with 'valid' if the query is about finding events somewhere, else respond with 'invalid'."
    )

    try:
        response = (
            llm.invoke(
                [SystemMessage(content=system_prompt), HumanMessage(content=f"Query: {user_query}")]
            )
            .content.strip()
            .lower()
        )

        # Check if the LLM returned the expected output
        if "invalid" in response:
            logger.info(f"Query status: INVALID (LLM response: {response}). Stopping flow.")
            return {"query_status": "invalid"}
        else:
            return {"query_status": "valid"}

    except Exception as e:
        logger.error(f"Error during query validation LLM call: {e}", exc_info=True)
        # Default to valid if the validator fails, allowing the rest of the graph to handle it.
        return {"query_status": "valid"}
