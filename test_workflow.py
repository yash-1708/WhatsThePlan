import asyncio
from datetime import datetime

from backend.app.core.logger import get_logger
from backend.app.graph import build_graph

logger = get_logger(__name__)


async def main():
    # 1. Build the graph
    app = build_graph()

    # 2. Define the initial state
    initial_state = {
        "user_query": "Comedy shows in Chicago this weekend",
        "current_date": datetime.now().strftime("%Y-%m-%d"),
        "retry_count": 0,
    }

    logger.info("Running async graph...")

    # 3. Use 'ainvoke' for async execution
    result = await app.ainvoke(initial_state)

    # 4. Log the output
    logger.info("Final result received")
    logger.info(f"Events found: {len(result.get('events', []))}")
    if result.get("events"):
        logger.debug(f"First event: {result['events'][0]}")


if __name__ == "__main__":
    asyncio.run(main())
