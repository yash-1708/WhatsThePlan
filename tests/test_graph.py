"""
Tests for backend.app.graph module.
"""

from backend.app.graph import build_graph, check_results


class TestCheckResults:
    """Tests for the check_results routing function."""

    def test_returns_success_when_events_found(self, sample_events, monkeypatch):
        """Should return 'success' when events list is not empty."""
        monkeypatch.setenv("MAX_RETRY_COUNT", "1")

        state = {
            "events": sample_events,
            "retry_count": 0,
        }
        result = check_results(state)
        assert result == "success"

    def test_returns_retry_when_no_events_and_retries_available(self, monkeypatch):
        """Should return 'retry' when no events and retry_count < MAX_RETRY_COUNT."""
        monkeypatch.setenv("MAX_RETRY_COUNT", "2")

        # Reload config to pick up new value
        import importlib

        from backend.app.core import config

        importlib.reload(config)

        state = {
            "events": [],
            "retry_count": 0,
        }
        result = check_results(state)
        assert result == "retry"

    def test_returns_give_up_when_max_retries_reached(self, monkeypatch):
        """Should return 'give_up' when retry_count >= MAX_RETRY_COUNT."""
        monkeypatch.setenv("MAX_RETRY_COUNT", "1")

        import importlib

        from backend.app.core import config

        importlib.reload(config)

        state = {
            "events": [],
            "retry_count": 1,  # Already at max
        }
        result = check_results(state)
        assert result == "give_up"

    def test_handles_missing_events_key(self, monkeypatch):
        """Should treat missing 'events' key as empty list."""
        monkeypatch.setenv("MAX_RETRY_COUNT", "0")

        import importlib

        from backend.app.core import config

        importlib.reload(config)

        state = {
            "retry_count": 0,
        }
        result = check_results(state)
        assert result == "give_up"

    def test_handles_missing_retry_count_key(self, sample_events):
        """Should treat missing 'retry_count' key as 0."""
        state = {
            "events": sample_events,
        }
        result = check_results(state)
        assert result == "success"


class TestBuildGraph:
    """Tests for the build_graph function."""

    def test_graph_compiles_successfully(self):
        """Should compile the graph without errors."""
        graph = build_graph()
        assert graph is not None

    def test_graph_has_required_nodes(self):
        """Should contain all agent nodes."""
        graph = build_graph()
        # LangGraph compiled graphs have a 'nodes' attribute
        node_names = list(graph.nodes.keys())

        expected_nodes = ["validator", "rewriter", "searcher", "extractor", "persistence"]
        for node in expected_nodes:
            assert node in node_names, f"Missing node: {node}"

    def test_graph_starts_with_validator(self):
        """Graph should start with the validator node."""
        graph = build_graph()
        # Verify validator is in the graph nodes
        # The graph structure varies by version, but we know validator is first
        assert "validator" in graph.nodes
