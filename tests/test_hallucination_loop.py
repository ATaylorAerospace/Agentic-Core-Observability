# Agentic Core Observability - Hallucination Loop Detection Tests
# Copyright (c) 2026 A Taylor. All rights reserved.
# Licensed under the MIT License.
#
# Unit tests for the hallucination-loop detection logic in supervisor.py.
# Run with: pytest tests/test_hallucination_loop.py -v

from __future__ import annotations

from src.agents.supervisor import (
    CONFIDENCE_FLOOR,
    MAX_ROUTING_ITERATIONS,
    SupervisorAgent,
    _check_hallucination_loop,
    _is_low_confidence,
)
from src.agents.tools import (
    analysis_tool,
    memory_recall_tool,
    memory_store_tool,
    research_tool,
)


class TestHallucinationLoopDetection:
    """Tests for _check_hallucination_loop."""

    def test_no_loop_when_trace_is_empty(self):
        """An empty trace should never trigger loop detection."""
        assert _check_hallucination_loop([]) is False

    def test_no_loop_when_trace_is_short(self):
        """A trace shorter than the threshold should not trigger."""
        trace = [{"action": "supervisor_response"}] * (MAX_ROUTING_ITERATIONS - 1)
        assert _check_hallucination_loop(trace) is False

    def test_loop_detected_with_identical_actions(self):
        """Repeated identical actions at the threshold should trigger."""
        trace = [{"action": "supervisor_response"}] * MAX_ROUTING_ITERATIONS
        assert _check_hallucination_loop(trace) is True

    def test_no_loop_with_varied_actions(self):
        """A trace with diverse actions should not trigger."""
        trace = [
            {"action": "research"},
            {"action": "analysis"},
            {"action": "research"},
            {"action": "memory_recall"},
            {"action": "supervisor_response"},
        ]
        assert _check_hallucination_loop(trace) is False

    def test_loop_detected_only_checks_recent_entries(self):
        """Old varied entries should not prevent detection of recent loops."""
        trace = [
            {"action": "research"},
            {"action": "analysis"},
            {"action": "memory_recall"},
        ] + [{"action": "stuck_action"}] * MAX_ROUTING_ITERATIONS
        assert _check_hallucination_loop(trace) is True

    def test_custom_threshold(self):
        """The threshold parameter should override the default."""
        trace = [{"action": "same"}] * 3
        assert _check_hallucination_loop(trace, threshold=3) is True
        assert _check_hallucination_loop(trace, threshold=4) is False

    def test_missing_action_key_does_not_crash(self):
        """Entries without an 'action' key should not raise exceptions."""
        trace = [{}] * MAX_ROUTING_ITERATIONS
        # None actions are all the same, so loop is detected
        assert _check_hallucination_loop(trace) is True

    def test_two_unique_actions_no_loop(self):
        """Two alternating actions should not be flagged as a loop."""
        trace = [
            {"action": "research"},
            {"action": "analysis"},
            {"action": "research"},
            {"action": "analysis"},
            {"action": "research"},
        ]
        assert _check_hallucination_loop(trace) is False

    def test_single_entry_trace(self):
        """A single-entry trace should never trigger."""
        trace = [{"action": "supervisor_response"}]
        assert _check_hallucination_loop(trace) is False

    def test_threshold_of_one(self):
        """Edge case: threshold of 1 should trigger on any single entry."""
        trace = [{"action": "anything"}]
        assert _check_hallucination_loop(trace, threshold=1) is True

    def test_non_positive_threshold_returns_false(self):
        """Non-positive thresholds should never trigger or raise IndexError."""
        assert _check_hallucination_loop([], threshold=0) is False
        assert _check_hallucination_loop([{"action": "a"}], threshold=0) is False
        assert _check_hallucination_loop([{"action": "a"}], threshold=-1) is False

    def test_low_confidence_helper(self):
        """Confidence values below CONFIDENCE_FLOOR or NaN are flagged."""
        assert _is_low_confidence(0.5) is True
        assert _is_low_confidence(float("nan")) is True
        assert _is_low_confidence(CONFIDENCE_FLOOR) is False
        assert _is_low_confidence(0.95) is False


class TestSupervisorAndTools:
    """Tests for SupervisorAgent helpers and custom tools."""

    def test_recall_preferences_ignores_empty_results_dict(self):
        """Empty recall results should return an empty string instead of dict repr."""
        agent = SupervisorAgent()
        assert agent.session_id == agent._session_id
        assert agent._recall_preferences("user-123") == ""
        assert agent._enrich_input("hello", "") == "hello"
        agent._trace.append({"action": "test"})
        agent.reset_trace()
        assert agent.get_trace() == []

    def test_recall_preferences_formats_non_empty_results(self, monkeypatch):
        """Populated recall results are formatted into the preference string."""
        import src.agents.supervisor as sup_mod

        monkeypatch.setattr(
            sup_mod,
            "memory_recall_tool",
            lambda query, namespace: {"results": ["concise", "markdown"]},
        )
        agent = SupervisorAgent()
        prefs = agent._recall_preferences("user-123")
        assert prefs == "concise, markdown"
        enriched = agent._enrich_input("analyze this", prefs)
        assert "[User Preferences from Memory]: concise, markdown" in enriched

    def test_tools_input_normalization_and_validation(self):
        """Custom tools normalize inputs and handle malformed metadata safely."""
        res = research_tool(query="photonics", sources=" web , arxiv , ")
        assert res["sources_consulted"] == ["web", "arxiv"]

        ana_upper = analysis_tool(data="1,2,3", analysis_type=" TREND ")
        assert ana_upper["analysis_type"] == "trend"

        ana_invalid = analysis_tool(data="1,2,3", analysis_type="invalid_mode")
        assert ana_invalid["analysis_type"] == "summary"

        store_non_dict = memory_store_tool(content="pref", metadata="[1, 2, 3]")
        assert store_non_dict["metadata"] == {}

        store_bad_json = memory_store_tool(content="pref", metadata="{not-json")
        assert store_bad_json["metadata"] == {}

        recall = memory_recall_tool(query="pref", max_results=0)
        assert recall["max_results"] == 5
