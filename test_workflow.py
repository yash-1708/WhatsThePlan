import asyncio
from backend.app.graph import build_graph
from datetime import datetime

async def main():
    # 1. Build the graph
    app = build_graph()

    # 2. Define the initial state
    initial_state = {
        "user_query": "Comedy shows in Chicago this weekend",
        "current_date": datetime.now().strftime("%Y-%m-%d"),
        "retry_count": 0
    }

    print("Running Async Graph...")
    
    # 3. Use 'ainvoke' for async execution
    result = await app.ainvoke(initial_state)

    # 4. Print the output
    print("\n--- FINAL RESULT ---")
    print(f"Events Found: {len(result.get('events', []))}")
    if result.get('events'):
        print(f"First Event: {result['events'][0]}")

if __name__ == "__main__":
    asyncio.run(main())