# Agentic Core Observability - Supervisor / Orchestrator Agent
# Copyright (c) 2026 A Taylor. All rights reserved.
# Licensed under the MIT License.
#
# This module implements the Strands SDK-based Supervisor agent that routes
# incoming tasks to specialized Researcher and Analyst sub-agents, tracks
# execution traces, and enforces hallucination loop detection.

from __future__ import annotations

import logging
import uuid
from typing import Any

from strands import Agent, tool
from strands.models.bedrock import BedrockModel
from strands_tools import http_request

from src.agents.tools import (
    research_tool,
    analysis_tool,
    memory_store_tool,
    memory_recall_tool,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Hallucination-loop guard
# ---------------------------------------------------------------------------
MAX_ROUTING_ITERATIONS = 5
CONFIDENCE_FLOOR = 0.85


def _check_hallucination_loop(trace: list[dict], threshold: int = MAX_ROUTING_ITERATIONS) -> bool:
    """Return True if the agent has entered a repetitive routing loop.

    Detects when the same routing decision is made repeatedly without
    meaningful progress, which is a strong signal of hallucination drift.
    """
    if len(trace) < threshold:
        return False

    recent_actions = [entry.get("action") for entry in trace[-threshold:]]
    unique_actions = set(recent_actions)
    if len(unique_actions) <= 1:
        logger.warning(
            "Hallucination loop detected: %d identical actions '%s'",
            threshold,
            recent_actions[0],
        )
        return True
    return False


# ---------------------------------------------------------------------------
# Researcher Agent
# ---------------------------------------------------------------------------
def build_researcher_agent(model: BedrockModel) -> Agent:
    """Construct a Researcher agent with web browsing and retrieval tools."""

    system_prompt = (
        "You are a Senior Research Specialist. Your role is to gather, validate, "
        "and summarize information from authoritative sources. Always cite your "
        "sources and flag any uncertainty. Never fabricate references."
    )

    researcher = Agent(
        model=model,
        system_prompt=system_prompt,
        tools=[research_tool, http_request],
        callback_handler=None,
    )
    return researcher


# ---------------------------------------------------------------------------
# Analyst Agent
# ---------------------------------------------------------------------------
def build_analyst_agent(model: BedrockModel) -> Agent:
    """Construct an Analyst agent for data processing and trend analysis."""

    system_prompt = (
        "You are a Senior Data Analyst. Your role is to interpret datasets, "
        "identify trends, and produce concise analytical summaries. Always "
        "ground your conclusions in the data provided. Flag low-confidence "
        "findings explicitly."
    )

    analyst = Agent(
        model=model,
        system_prompt=system_prompt,
        tools=[analysis_tool],
        callback_handler=None,
    )
    return analyst


# ---------------------------------------------------------------------------
# Supervisor / Orchestrator Agent
# ---------------------------------------------------------------------------
class SupervisorAgent:
    """Strands-based orchestrator that routes tasks to sub-agents.

    The Supervisor inspects each incoming request, classifies the intent,
    and delegates to the appropriate specialist agent. It maintains an
    execution trace used for hallucination-loop detection and observability.
    """

    def __init__(
        self,
        model_id: str = "us.anthropic.claude-sonnet-4-20250514",
        region: str = "us-east-1",
    ) -> None:
        self.model = BedrockModel(
            model_id=model_id,
            region_name=region,
        )
        self.researcher = build_researcher_agent(self.model)
        self.analyst = build_analyst_agent(self.model)

        self.supervisor = Agent(
            model=self.model,
            system_prompt=self._supervisor_prompt(),
            tools=[
                research_tool,
                analysis_tool,
                memory_store_tool,
                memory_recall_tool,
            ],
            callback_handler=None,
        )

        self._trace: list[dict] = []
        self._session_id: str = str(uuid.uuid4())

    # ----- public API -----

    def run(self, user_input: str, user_id: str = "default") -> dict[str, Any]:
        """Process a user request through the orchestration pipeline.

        Returns a dict with keys: response, trace, session_id, loop_detected.
        """
        logger.info("Session %s | Processing: %s", self._session_id, user_input[:120])

        # Recall user preferences from semantic memory
        preferences = self._recall_preferences(user_id)

        # Route through the supervisor agent
        enriched_input = self._enrich_input(user_input, preferences)
        result = self.supervisor(enriched_input)

        # Record trace entry
        trace_entry = {
            "action": "supervisor_response",
            "input_preview": user_input[:200],
            "session_id": self._session_id,
            "user_id": user_id,
        }
        self._trace.append(trace_entry)

        loop_detected = _check_hallucination_loop(self._trace)
        if loop_detected:
            logger.error("Breaking hallucination loop for session %s", self._session_id)
            return {
                "response": (
                    "I detected a repetitive pattern in my reasoning and stopped "
                    "to avoid producing unreliable output. Please rephrase your "
                    "request or provide additional context."
                ),
                "trace": self._trace,
                "session_id": self._session_id,
                "loop_detected": True,
            }

        return {
            "response": str(result),
            "trace": self._trace,
            "session_id": self._session_id,
            "loop_detected": False,
        }

    def get_trace(self) -> list[dict]:
        """Return the full execution trace for observability dashboards."""
        return list(self._trace)

    # ----- internal helpers -----

    def _recall_preferences(self, user_id: str) -> str:
        """Retrieve stored user preferences from AgentCore semantic memory."""
        try:
            recall_result = memory_recall_tool(
                query=f"report preferences for user {user_id}",
                namespace="agentic-observability",
            )
            return str(recall_result) if recall_result else ""
        except Exception:
            logger.debug("No stored preferences found for user %s", user_id)
            return ""

    @staticmethod
    def _enrich_input(user_input: str, preferences: str) -> str:
        if not preferences:
            return user_input
        return (
            f"{user_input}\n\n"
            f"[User Preferences from Memory]: {preferences}"
        )

    @staticmethod
    def _supervisor_prompt() -> str:
        return (
            "You are the Supervisor Agent for Agentic Core Observability. "
            "Your job is to:\n"
            "1. Classify incoming requests as RESEARCH, ANALYSIS, or GENERAL.\n"
            "2. Delegate RESEARCH tasks to the Researcher agent.\n"
            "3. Delegate ANALYSIS tasks to the Analyst agent.\n"
            "4. Handle GENERAL tasks directly.\n"
            "5. Store useful user preferences to semantic memory for future recall.\n"
            "6. Always ground responses in retrieved data. If uncertain, say so.\n\n"
            "Never fabricate data. If a source cannot be verified, state that clearly."
        )
