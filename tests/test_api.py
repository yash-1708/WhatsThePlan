"""
Tests for the FastAPI application endpoints.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.models.schemas import Event


@pytest.fixture
def sample_graph_result(sample_events):
    """Sample result from graph.ainvoke()."""
    return {
        "user_query": "Comedy shows in Chicago",
        "current_date": "2024-12-20",
        "search_id": "test-search-id-123",
        "query_status": "valid",
        "events": sample_events,
    }


class TestSearchEndpoint:
    """Tests for POST /search endpoint."""

    @pytest.mark.asyncio
    async def test_successful_search_returns_events(self, sample_graph_result):
        """Should return events on successful search."""
        with patch("main.build_graph") as mock_build:
            mock_graph = MagicMock()
            mock_graph.ainvoke = AsyncMock(return_value=sample_graph_result)
            mock_build.return_value = mock_graph

            from main import app

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post("/search", json={"query": "Comedy shows in Chicago"})

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["search_id"] == "test-search-id-123"
            assert len(data["events"]) == 2

    @pytest.mark.asyncio
    async def test_search_with_empty_results(self):
        """Should handle searches with no events found."""
        with patch("main.build_graph") as mock_build:
            mock_graph = MagicMock()
            mock_graph.ainvoke = AsyncMock(
                return_value={
                    "user_query": "Nonexistent event",
                    "search_id": "test-id",
                    "query_status": "valid",
                    "events": [],
                }
            )
            mock_build.return_value = mock_graph

            from main import app

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post("/search", json={"query": "Nonexistent event in Mars"})

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["events"] == []

    @pytest.mark.asyncio
    async def test_search_with_invalid_query(self):
        """Should handle invalid queries gracefully."""
        with patch("main.build_graph") as mock_build:
            mock_graph = MagicMock()
            mock_graph.ainvoke = AsyncMock(
                return_value={
                    "user_query": "What is 2+2?",
                    "search_id": None,
                    "query_status": "invalid",
                    "events": [],
                }
            )
            mock_build.return_value = mock_graph

            from main import app

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post("/search", json={"query": "What is 2+2?"})

            assert response.status_code == 200
            data = response.json()
            assert data["query_status"] == "invalid"

    @pytest.mark.asyncio
    async def test_search_handles_graph_error(self):
        """Should return 500 on internal errors."""
        with patch("main.build_graph") as mock_build:
            mock_graph = MagicMock()
            mock_graph.ainvoke = AsyncMock(side_effect=Exception("Graph execution failed"))
            mock_build.return_value = mock_graph

            from main import app

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post("/search", json={"query": "Test query"})

            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_search_requires_query_field(self):
        """Should return 422 when query field is missing."""
        from main import app

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/search", json={})

        assert response.status_code == 422


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    @pytest.mark.asyncio
    async def test_root_serves_index_html(self):
        """Should serve frontend/index.html at root."""
        from main import app

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/")

        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")


class TestStaticFiles:
    """Tests for static file serving."""

    @pytest.mark.asyncio
    async def test_frontend_files_accessible(self):
        """Should serve files from /frontend path."""
        from main import app

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/frontend/index.html")

        assert response.status_code == 200


class TestEventModel:
    """Tests for the Event Pydantic model."""

    def test_event_model_serialization(self, sample_event):
        """Should serialize Event model correctly."""
        data = sample_event.model_dump()

        assert data["title"] == "Test Concert"
        assert data["date"] == "2024-12-25"
        assert data["location"] == "Test Venue, Chicago"
        assert data["url"] == "https://example.com/event"
        assert data["score"] == 0.95

    def test_event_model_optional_score(self):
        """Should allow None score."""
        event = Event(
            title="Test",
            date="2024-01-01",
            location="Test",
            description="Test",
            url="http://test.com",
            score=None,
        )
        data = event.model_dump()
        assert data["score"] is None

    def test_event_model_validation(self):
        """Should validate required fields."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            Event(
                title="Test",
                # Missing required fields
            )
