from eventsFinderBackend.app.graph import build_graph
from datetime import datetime

app = build_graph()

# A query designed to fail initially (hopefully prompting a retry)
initial_state = {
    "user_query": "Underwater basket weaving championship in Antarctica tomorrow",
    "current_date": datetime.now().strftime("%Y-%m-%d"),
    "retry_count": 0
}

print("Running Graph with Logic Loop...")
result = app.invoke(initial_state)

print("\n--- FINAL RESULT ---")
print(f"Events Found: {len(result.get('events', []))}")
print(f"Total Attempts: {result.get('retry_count')}")

print(f"RESULT: {result}")