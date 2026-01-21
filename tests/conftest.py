"""
Shared pytest fixtures for WhatsThePlan test suite.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.app.models.schemas import Event

# =============================================================================
# Environment Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Set required environment variables for tests."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("TAVILY_API_KEY", "test-tavily-key")
    monkeypatch.setenv("MONGODB_URI", "mongodb://localhost:27017")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")  # Reduce test noise


# =============================================================================
# Mock LLM Fixtures
# =============================================================================


@pytest.fixture
def mock_llm():
    """Create a mock LLM that returns configurable responses."""
    mock = MagicMock()
    mock.invoke = MagicMock()
    return mock


@pytest.fixture
def mock_structured_llm():
    """Create a mock structured LLM for agents that use with_structured_output."""
    mock = MagicMock()
    mock.with_structured_output = MagicMock(return_value=mock)
    mock.invoke = MagicMock()
    return mock


# =============================================================================
# Sample Data Fixtures
# =============================================================================


@pytest.fixture
def sample_event():
    """A single sample Event object."""
    return Event(
        title="Test Concert",
        date="2024-12-25",
        location="Test Venue, Chicago",
        description="A test concert event",
        url="https://example.com/event",
        score=0.95,
    )


@pytest.fixture
def sample_events(sample_event):
    """A list of sample Event objects."""
    return [
        sample_event,
        Event(
            title="Comedy Show",
            date="2024-12-26",
            location="Laugh Factory, Chicago",
            description="Stand-up comedy night",
            url="https://example.com/comedy",
            score=0.88,
        ),
    ]


@pytest.fixture
def sample_raw_results():
    """Sample raw search results from Tavily."""
    return [
        {
            "title": "Chicago Concert Calendar",
            "url": "https://example.com/concerts",
            "content": "Upcoming concerts in Chicago this weekend include...",
            "score": 0.92,
            "query_context": "concerts Chicago December 2024",
        },
        {
            "title": "Chicago Events Guide",
            "url": "https://example.com/events",
            "content": "Find the best events happening in Chicago...",
            "score": 0.85,
            "query_context": "events Chicago this weekend",
        },
    ]


@pytest.fixture
def sample_agent_state():
    """A sample AgentState for testing agents."""
    return {
        "user_query": "Comedy shows in Chicago this weekend",
        "current_date": "2024-12-20",
        "retry_count": 0,
        "search_queries": [],
        "query_status": "",
        "raw_results": [],
        "events": [],
        "final_response": "",
    }


# =============================================================================
# Mock Client Fixtures
# =============================================================================


@pytest.fixture
def mock_tavily_client():
    """Mock Tavily sync client."""
    mock = MagicMock()
    mock.search = MagicMock(return_value={"results": []})
    return mock


@pytest.fixture
def mock_async_tavily_client():
    """Mock Tavily async client."""
    mock = AsyncMock()
    mock.search = AsyncMock(return_value={"results": []})
    return mock


@pytest.fixture
def mock_mongodb_collection():
    """Mock MongoDB collection."""
    mock = MagicMock()
    mock.insert_one = MagicMock(return_value=MagicMock(inserted_id="test-id-123"))
    mock.find_one = MagicMock(return_value=None)
    return mock
