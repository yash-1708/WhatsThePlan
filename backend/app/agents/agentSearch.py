from backend.app.core.tavilyClient import get_async_tavily_client
from backend.app.core.logger import get_logger
from backend.app.models.schemas import AgentState
import asyncio

logger = get_logger(__name__)
async def search_node(state: AgentState):
    """
    Agent 2: Execute search queries in PARALLEL using asyncio.
    """
    queries = state["search_queries"]
    logger.info(f"Agent 2: Searching Tavily ({len(queries)} queries in parallel)")
    
    tavily_async = get_async_tavily_client()
    
    # Create a list of coroutine tasks
    search_tasks = []
    for q in queries:
        # Schedule the coroutine
        task = tavily_async.search(
            query=q, 
            search_depth="advanced", 
            max_results=3,
            include_answer=True # Useful for context
        )
        search_tasks.append(task)

    # Execute all tasks concurrently and wait for them to finish
    try:
        search_responses = await asyncio.gather(*search_tasks, return_exceptions=True)
    except Exception as e:
        logger.error(f"Critical async error during search: {e}", exc_info=True)
        return {"raw_results": []}

    # Process results
    all_results = []
    for i, response in enumerate(search_responses):
        query_used = queries[i]
        
        # Handle individual task failures (if one query fails, others shouldn't die)
        if isinstance(response, Exception):
            logger.warning(f"Error searching for '{query_used}': {response}")
            continue
            
        # Tag results with context
        for result in response.get('results', []):
            result['query_context'] = query_used
            all_results.append(result)

    logger.info(f"Found {len(all_results)} raw results")

    return {"raw_results": all_results}