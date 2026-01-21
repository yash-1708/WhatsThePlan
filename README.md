# What's The Plan? - Multi-Agent Event Finder

A multi-agent system using LangGraph to find real-time events based on natural language queries. It uses the OpenAI API for reasoning and structured data extraction, the Tavily Search API for up-to-date web data, and MongoDB Atlas for persistence.

The backend is built with FastAPI, and the frontend is a modern HTML/Vanilla JS interface with dark mode, animated transitions, and mobile-responsive design.

## Architecture and Agent Flow

The system orchestrates a set of specialized agents into a directed graph, ensuring efficiency and data quality. The Validator Agent ensures we stop processing irrelevant queries immediately.

### Agent Responsibilities

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| **0. Validator** | Pre-check guardrail. Ensures the query is relevant (event type + location) before proceeding. | `user_query` | `query_status` (`valid` or `invalid`) |
| **1. Rewriter** | Query preparation. Resolves relative dates (e.g., "this weekend") and generates targeted search queries. | `user_query`, `retry_count` | `search_queries` |
| **2. Searcher** | Real-time retrieval. Executes all generated queries in **parallel** using the Tavily API. | `search_queries` | `raw_search_results` |
| **3. Extractor** | Data synthesis. Uses LLM structured output to filter noise, resolve dates, and output clean `Event` objects. | `raw_search_results` | `events` (List of Events) |
| **4. Persistence** | Logging & storage. Saves the entire execution context to MongoDB Atlas. | Final State | `search_id` |

![Agent Flow Mermaid Diagram](https://github.com/yash-1708/WhatsThePlan/blob/main/WhatsThePlanGraph.png "Agent Flow")

## Project Setup and Installation

### 1. Prerequisites

- Python 3.9+
- MongoDB Atlas Cluster (free M0 tier is sufficient)

### 2. Install Python Dependencies

```bash
# Create and activate virtual environment
python -m venv venv

# On Windows:
.\venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory. See `.env.dist` for the full template.

**Required variables:**

```bash
# API Keys (required)
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/...
```

**Optional configuration (with defaults):**

```bash
# LLM Configuration
LLM_MODEL=gpt-4o                    # OpenAI model to use
LLM_TEMPERATURE=0                   # Temperature (0-2)

# Tavily Search Configuration
TAVILY_MAX_RESULTS=3                # Results per search query
TAVILY_SEARCH_DEPTH=advanced        # basic or advanced
TAVILY_INCLUDE_ANSWER=true          # Include AI-generated answer

# Agent Configuration
MAX_RETRY_COUNT=1                   # Retry attempts when no results found
REWRITER_NUM_QUERIES=3              # Number of search queries to generate

# MongoDB Configuration
MONGODB_DB_NAME=tavily_events_db    # Database name
MONGODB_COLLECTION_NAME=searches    # Collection name
MONGODB_TIMEOUT_MS=5000             # Connection timeout

# Server Configuration
SERVER_HOST=0.0.0.0                 # Server bind address
PORT=8000                           # Server port
UVICORN_RELOAD=true                 # Hot reload (set false for production)

# CORS Configuration
CORS_ORIGINS=*                      # Comma-separated origins or * for all

# Logging Configuration
LOG_LEVEL=INFO                      # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### 4. Start the Server

```bash
python main.py
```

The server will start at http://127.0.0.1:8000. The frontend is served automatically at the root URL.

You can also access the API documentation at http://127.0.0.1:8000/docs.

## Usage

Open http://127.0.0.1:8000 in your browser.

**Valid query example:** "Electronic music festival in Barcelona this summer"
- The Validator returns `valid`, the full pipeline executes, and results are displayed.

**Invalid query example:** "What is the square root of 9?"
- The Validator returns `invalid`, and the UI displays a warning message.

## Project Structure

```
WhatsThePlan/
├── main.py                          # FastAPI app entry point
├── backend/app/
│   ├── graph.py                     # LangGraph workflow definition
│   ├── agents/
│   │   ├── agentValidator.py        # Agent 0: Query validation
│   │   ├── agentRewriter.py         # Agent 1: Query rewriting
│   │   ├── agentSearch.py           # Agent 2: Tavily search
│   │   ├── agentExtractor.py        # Agent 3: Event extraction
│   │   └── agentPersistence.py      # Agent 4: MongoDB persistence
│   ├── core/
│   │   ├── config.py                # Central configuration
│   │   ├── logger.py                # Logging configuration
│   │   ├── llmClient.py             # OpenAI client
│   │   ├── tavilyClient.py          # Tavily client
│   │   └── dbClient.py              # MongoDB client
│   └── models/
│       └── schemas.py               # Pydantic models
├── frontend/                        # Static frontend files
│   ├── index.html                   # Main HTML page
│   ├── style.css                    # Styles with dark mode support
│   └── script.js                    # Frontend logic
├── tests/                           # Test suite (pytest)
│   ├── conftest.py                  # Shared fixtures
│   ├── test_config.py               # Config helper tests
│   ├── test_logger.py               # Logger tests
│   ├── test_graph.py                # Graph routing tests
│   ├── test_agents.py               # Agent unit tests
│   ├── test_api.py                  # API integration tests
│   └── test_db_client.py            # Database client tests
├── .env.dist                        # Environment template
├── requirements.txt                 # Production dependencies
├── requirements-dev.txt             # Development dependencies (linting, testing)
└── pyproject.toml                   # Tool configuration (ruff, mypy, pytest)
```

## API

**POST `/search`** - Search for events (rate limited: 10 requests/minute)

Request:
```json
{"query": "Comedy shows in Chicago this weekend"}
```

Response:
```json
{
  "status": "success",
  "search_id": "...",
  "query_status": "valid",
  "elapsed_time": 3.45,
  "events": [
    {
      "title": "...",
      "date": "...",
      "location": "...",
      "description": "...",
      "url": "...",
      "score": 0.95
    }
  ]
}
```

**GET `/health`** - Health check endpoint

Response:
```json
{
  "status": "healthy",
  "components": {
    "api": "healthy",
    "database": "healthy"
  }
}
```

Returns HTTP 503 if database is unhealthy.

## Frontend Features

The UI includes several enhancements for a better user experience:

- **Dark Mode**: Toggle between light and dark themes (persisted in localStorage)
- **Example Query Chips**: Click to populate common search queries
- **Loading Spinner**: Animated spinner during search
- **Relevance Scores**: Color-coded badges showing event match quality (green ≥70%, yellow ≥40%, gray <40%)
- **Search Metadata**: Shows "Found X events in Y seconds" after search
- **Smooth Animations**: Fade-in card animations with staggered delays
- **Mobile Responsive**: Optimized layout for phones and tablets

## Logging

The application uses structured logging with configurable levels:

```bash
# More verbose (shows client initialization, debug info)
LOG_LEVEL=DEBUG python main.py

# Production (only warnings and errors)
LOG_LEVEL=WARNING python main.py
```

Log format:
```
2024-01-21 10:05:55 - backend.app.agents.agentSearch - INFO - Agent 2: Searching Tavily (3 queries in parallel)
```

## Development

### Linting and Type Checking

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linter
ruff check .

# Auto-fix linting issues
ruff check . --fix

# Type checking
mypy backend/ main.py --ignore-missing-imports --no-site-packages
```

Tools configured in `pyproject.toml`:
- **ruff**: Fast linter (replaces flake8, isort, pyupgrade)
- **mypy**: Static type checker

### Pre-commit Hooks

Automatically run linters before each commit:

```bash
# Install hooks (one-time setup)
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

Hooks configured in `.pre-commit-config.yaml`:
- **ruff**: Linting + auto-fix
- **ruff-format**: Code formatting
- **mypy**: Type checking

### Testing

```bash
# Run all tests
pytest

# Verbose output
pytest tests/ -v

# With coverage report
pytest --cov=backend --cov-report=term-missing

# Run specific test file
pytest tests/test_agents.py

# Run specific test class
pytest tests/test_agents.py::TestValidatorAgent
```

Test suite includes:
- **65 tests** covering all modules
- Unit tests for config helpers, logger, graph logic, database client
- Agent tests with mocked LLM/API responses
- API integration tests (including health endpoint)
- Uses httpx AsyncClient for async endpoint testing

## Deployment

For production deployment:

```bash
# .env settings for production
UVICORN_RELOAD=false
CORS_ORIGINS=https://yourdomain.com
LOG_LEVEL=WARNING
```

Procfile for Heroku/similar:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```
