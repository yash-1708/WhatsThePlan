"""
Tests for agent modules in backend.app.agents.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.app.models.schemas import Event


class TestValidatorAgent:
    """Tests for the query_validator_node agent."""

    def test_returns_valid_for_event_query(self, sample_agent_state):
        """Should return 'valid' for proper event queries."""
        with patch("backend.app.agents.agentValidator.get_llm") as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = MagicMock(content="valid")
            mock_get_llm.return_value = mock_llm

            from backend.app.agents.agentValidator import query_validator_node

            result = query_validator_node(sample_agent_state)
            assert result["query_status"] == "valid"

    def test_returns_invalid_for_non_event_query(self, sample_agent_state):
        """Should return 'invalid' for non-event queries."""
        with patch("backend.app.agents.agentValidator.get_llm") as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = MagicMock(content="invalid")
            mock_get_llm.return_value = mock_llm

            from backend.app.agents.agentValidator import query_validator_node

            sample_agent_state["user_query"] = "What is 2+2?"
            result = query_validator_node(sample_agent_state)
            assert result["query_status"] == "invalid"

    def test_defaults_to_valid_on_error(self, sample_agent_state):
        """Should default to 'valid' if LLM call fails."""
        with patch("backend.app.agents.agentValidator.get_llm") as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.side_effect = Exception("LLM Error")
            mock_get_llm.return_value = mock_llm

            from backend.app.agents.agentValidator import query_validator_node

            result = query_validator_node(sample_agent_state)
            assert result["query_status"] == "valid"


class TestRewriterAgent:
    """Tests for the query_rewriter_node agent."""

    def test_generates_search_queries(self, sample_agent_state):
        """Should generate search queries from user input."""
        with patch("backend.app.agents.agentRewriter.get_llm") as mock_get_llm:
            mock_llm = MagicMock()
            mock_structured = MagicMock()
            mock_structured.invoke.return_value = MagicMock(
                queries=["comedy shows Chicago December 2024", "stand-up comedy Chicago"]
            )
            mock_llm.with_structured_output.return_value = mock_structured
            mock_get_llm.return_value = mock_llm

            from backend.app.agents.agentRewriter import query_rewriter_node

            result = query_rewriter_node(sample_agent_state)

            assert "search_queries" in result
            assert len(result["search_queries"]) == 2
            assert result["retry_count"] == 1  # Incremented from 0

    def test_increments_retry_count(self, sample_agent_state):
        """Should increment retry_count on each call."""
        with patch("backend.app.agents.agentRewriter.get_llm") as mock_get_llm:
            mock_llm = MagicMock()
            mock_structured = MagicMock()
            mock_structured.invoke.return_value = MagicMock(queries=["test query"])
            mock_llm.with_structured_output.return_value = mock_structured
            mock_get_llm.return_value = mock_llm

            from backend.app.agents.agentRewriter import query_rewriter_node

            sample_agent_state["retry_count"] = 2
            result = query_rewriter_node(sample_agent_state)
            assert result["retry_count"] == 3

    def test_falls_back_to_original_query_on_error(self, sample_agent_state):
        """Should use original query as fallback if LLM fails."""
        with patch("backend.app.agents.agentRewriter.get_llm") as mock_get_llm:
            mock_llm = MagicMock()
            mock_structured = MagicMock()
            mock_structured.invoke.side_effect = Exception("LLM Error")
            mock_llm.with_structured_output.return_value = mock_structured
            mock_get_llm.return_value = mock_llm

            from backend.app.agents.agentRewriter import query_rewriter_node

            result = query_rewriter_node(sample_agent_state)
            assert result["search_queries"] == [sample_agent_state["user_query"]]


class TestSearchAgent:
    """Tests for the search_node agent."""

    @pytest.mark.asyncio
    async def test_executes_parallel_searches(self, sample_agent_state):
        """Should execute multiple search queries in parallel."""
        with patch("backend.app.agents.agentSearch.get_async_tavily_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.search.return_value = {
                "results": [{"title": "Test", "url": "http://test.com", "content": "Test content"}]
            }
            mock_get_client.return_value = mock_client

            from backend.app.agents.agentSearch import search_node

            sample_agent_state["search_queries"] = ["query1", "query2"]
            result = await search_node(sample_agent_state)

            assert "raw_results" in result
            assert mock_client.search.call_count == 2

    @pytest.mark.asyncio
    async def test_handles_search_failures_gracefully(self, sample_agent_state):
        """Should continue if individual searches fail."""
        with patch("backend.app.agents.agentSearch.get_async_tavily_client") as mock_get_client:
            mock_client = AsyncMock()
            # First call succeeds, second fails
            mock_client.search.side_effect = [
                {"results": [{"title": "Success", "url": "http://test.com", "content": "OK"}]},
                Exception("Search failed"),
            ]
            mock_get_client.return_value = mock_client

            from backend.app.agents.agentSearch import search_node

            sample_agent_state["search_queries"] = ["query1", "query2"]
            result = await search_node(sample_agent_state)

            # Should still have results from the successful query
            assert "raw_results" in result
            assert len(result["raw_results"]) == 1

    @pytest.mark.asyncio
    async def test_returns_empty_on_critical_error(self, sample_agent_state):
        """Should return empty results on critical async error."""
        with patch("backend.app.agents.agentSearch.get_async_tavily_client") as mock_get_client:
            mock_get_client.side_effect = RuntimeError("Client creation failed")

            from backend.app.agents.agentSearch import search_node

            sample_agent_state["search_queries"] = ["query1"]

            # This should raise a RuntimeError since client creation fails
            with pytest.raises(RuntimeError, match="Client creation failed"):
                await search_node(sample_agent_state)


class TestExtractorAgent:
    """Tests for the extraction_node agent."""

    def test_extracts_events_from_raw_results(self, sample_agent_state, sample_raw_results):
        """Should extract structured events from raw search results."""
        with patch("backend.app.agents.agentExtractor.get_llm") as mock_get_llm:
            mock_llm = MagicMock()
            mock_structured = MagicMock()
            mock_structured.invoke.return_value = MagicMock(
                events=[
                    Event(
                        title="Test Event",
                        date="2024-12-25",
                        location="Chicago",
                        description="A test event",
                        url="http://test.com",
                        score=0.9,
                    )
                ]
            )
            mock_llm.with_structured_output.return_value = mock_structured
            mock_get_llm.return_value = mock_llm

            from backend.app.agents.agentExtractor import extraction_node

            sample_agent_state["raw_results"] = sample_raw_results
            result = extraction_node(sample_agent_state)

            assert "events" in result
            assert len(result["events"]) == 1
            assert result["events"][0].title == "Test Event"

    def test_returns_empty_for_no_raw_results(self, sample_agent_state):
        """Should return empty events list when no raw results."""
        from backend.app.agents.agentExtractor import extraction_node

        sample_agent_state["raw_results"] = []
        result = extraction_node(sample_agent_state)

        assert result["events"] == []

    def test_handles_extraction_error(self, sample_agent_state, sample_raw_results):
        """Should return empty list on extraction error."""
        with patch("backend.app.agents.agentExtractor.get_llm") as mock_get_llm:
            mock_llm = MagicMock()
            mock_structured = MagicMock()
            mock_structured.invoke.side_effect = Exception("Extraction failed")
            mock_llm.with_structured_output.return_value = mock_structured
            mock_get_llm.return_value = mock_llm

            from backend.app.agents.agentExtractor import extraction_node

            sample_agent_state["raw_results"] = sample_raw_results
            result = extraction_node(sample_agent_state)

            assert result["events"] == []


class TestPersistenceAgent:
    """Tests for the persistence_node agent."""

    def test_saves_to_mongodb(self, sample_agent_state, sample_events):
        """Should save search results to MongoDB."""
        with patch("backend.app.agents.agentPersistence.get_db_collection") as mock_get_db:
            mock_collection = MagicMock()
            mock_get_db.return_value = mock_collection

            from backend.app.agents.agentPersistence import persistence_node

            sample_agent_state["events"] = sample_events
            result = persistence_node(sample_agent_state)

            assert "search_id" in result
            mock_collection.insert_one.assert_called_once()

    def test_handles_db_error_gracefully(self, sample_agent_state, sample_events):
        """Should handle MongoDB errors without crashing."""
        with patch("backend.app.agents.agentPersistence.get_db_collection") as mock_get_db:
            mock_collection = MagicMock()
            mock_collection.insert_one.side_effect = Exception("DB Error")
            mock_get_db.return_value = mock_collection

            from backend.app.agents.agentPersistence import persistence_node

            sample_agent_state["events"] = sample_events
            result = persistence_node(sample_agent_state)

            # Should still return a search_id even if save fails
            assert "search_id" in result

    def test_generates_unique_search_id(self, sample_agent_state):
        """Should generate a unique UUID for each search."""
        with patch("backend.app.agents.agentPersistence.get_db_collection") as mock_get_db:
            mock_collection = MagicMock()
            mock_get_db.return_value = mock_collection

            from backend.app.agents.agentPersistence import persistence_node

            result1 = persistence_node(sample_agent_state)
            result2 = persistence_node(sample_agent_state)

            assert result1["search_id"] != result2["search_id"]
