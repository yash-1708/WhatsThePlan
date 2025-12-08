# 🗓️ What's The Plan? - Multi-Agent Event Finder

This project implements a robust, multi-agent system using LangGraph to find real-time events based on natural language queries. It utilises the Gemini API for reasoning and structured data extraction, the Tavily Search API for up-to-date web data, and MongoDB Atlas for persistence.

The backend is built with FastAPI, and the frontend is a simple, modern HTML/Vanilla JS interface.

# 🚀 Architecture and Agent Flow

The system orchestrates a set of specialised agents into a directed graph, ensuring efficiency and data quality. The addition of the Validator Agent ensures we stop processing irrelevant queries immediately.

### Agent Responsibilities:

| Agent Node | Role | Input | Output | 
 | ----- | ----- | ----- | ----- | 
| **0. Validator** | **Pre-Check & Guardrail.** Ensures the query is relevant (event type + location) before proceeding. | `user_query` | `query_status` (`valid` or `invalid`) | 
| **1. Rewriter** | **Query Preparation.** Takes the user query, resolves relative dates (e.g., "this weekend"), and generates 3-5 specific search queries. | `user_query`, `retry_count` | `search_queries` | 
| **2. Searcher** | **Real-Time Retrieval.** Executes all generated queries in **parallel** using the Tavily API. | `search_queries` | `raw_search_results` | 
| **3. Extractor** | **Data Synthesis.** Uses Gemini's structured output to read search snippets, filter noise, resolve dates, and output a clean, structured JSON list of `Event` objects. | `raw_search_results` | `events` (List of Events) | 
| **4. Persistence** | **Logging & Storage.** Saves the entire execution context (original query, search results, final events, etc.) to MongoDB Atlas. | Final State | `search_id` |

![Agent Flow Mermaid Diagram](https://github.com/yash-1708/WhatsThePlan/blob/main/WhatsThePlanGraph.png "Agent Flow")
# 🛠️ Project Setup and Installation

Follow these steps to set up the project locally.

## 1. Prerequisites

- You must have Python 3.9+ installed on your system
- MongoDB Atlas Cluster (A free M0 tier cluster is sufficient)

## 2. Install Python Dependencies

Navigate to the root of the project folder (WhatsThePlan/) and install the required libraries.
(Note that python and pip are aliases set for python3 and pip3 using 
~~~
alias python = python3
alias pip = pip3
~~~

- Create and activate a Python virtual environment (recommended)
~~~
python -m venv venv
~~~

- On Windows:
~~~
.\venv\Scripts\activate
~~~
- On macOS/Linux:
~~~
source venv/bin/activate
~~~

- Install required packages
~~~
pip install -r requirements.txt
~~~

## 3. Configure Environment Variables

Create a file named .env in the root directory (WhatsThePlan/.env) and populate it with your confidential keys. These are necessary for the application to function. A sample file named 'env.dist' is in the repo.

### LLM API Key (Required for Reasoning/Extraction/Validation)
~~~
OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
~~~

### Tavily API Key (Required for Search)
~~~
TAVILY_API_KEY="YOUR_TAVILY_API_KEY"
~~~

### MongoDB Atlas Connection String (Required for Persistence)
Ensure you replace <username>, <password>, and <cluster-name>
~~~
MONGODB_URI="mongodb+srv://<username>:<password>@<cluster-name>.mongodb.net/...."
~~~

## 4. Start the Backend Server (FastAPI)

Ensure your virtual environment is active. The backend runs on port 8000.

### In the WhatsThePlan/ directory
~~~
python main.py
~~~

Success: The server will start and be accessible at http://127.0.0.1:8000.

(You can verify the API is live by navigating to http://127.0.0.1:8000/docs in your browser to access the OpenAPI documentation for the FastAPI endpoint).

## 5. Start the Frontend UI

The frontend is a static HTML file that calls the local backend API.

Keep the FastAPI server running in one terminal.

Open the frontend UI by double-clicking the file ui/index.html in your file explorer.

# 📝 Usage and Testing the Validator

Open the UI (ui/index.html).

Test 1 (Valid Query): Enter Electronic music festival in Barcelona this summer.

Expected Result: The console will show the Validator agent returning valid, and the full agent pipeline will execute, leading to results.

Test 2 (Invalid Query): Enter What is the square root of 9?.

Expected Result: The console will show the Validator agent returning invalid. The search button will quickly reset, and the UI will display the orange warning message: "Please enter a valid query that specifies both an event type and a location..."
