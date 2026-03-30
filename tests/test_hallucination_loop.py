# Agentic Core Observability - Hallucination Loop Detection Tests
# Copyright (c) 2026 A Taylor. All rights reserved.
# Licensed under the MIT License.
#
# Unit tests for the hallucination-loop detection logic in supervisor.py.
# Run with: pytest tests/test_hallucination_loop.py -v

from __future__ import annotations

from src.agents.supervisor import _check_hallucination_loop, MAX_ROUTING_ITERATIONS


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
