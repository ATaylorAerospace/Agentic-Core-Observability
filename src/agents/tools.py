# Agentic Core Observability - Tool Definitions
# Copyright (c) 2026 A Taylor. All rights reserved.
# Licensed under the MIT License.
#
# Custom Strands tools used by the Supervisor, Researcher, and Analyst agents.
# Each tool is decorated with @tool so the Strands SDK can register it
# automatically in the agent's tool belt.

from __future__ import annotations

import json
import logging
from typing import Any

from strands import tool

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Research Tool
# ---------------------------------------------------------------------------
@tool
def research_tool(query: str, sources: str = "web,arxiv") -> dict[str, Any]:
    """Search authoritative sources and return structured findings.

    Args:
        query: The research question or topic to investigate.
        sources: Comma-separated list of source categories to search
                 (e.g. 'web', 'arxiv', 'github').

    Returns:
        A dict with keys: findings, sources_consulted, confidence.
    """
    logger.info("Research tool invoked | query='%s' sources='%s'", query, sources)

    parsed_sources = [s.strip() for s in sources.split(",") if s.strip()]
    if not parsed_sources:
        parsed_sources = ["web", "arxiv"]

    # In production this delegates to the AgentCore Browser tool (Nova Act)
    # and/or the Bedrock Research Agent via the Gateway.
    # Placeholder structure for local development and testing.
    return {
        "findings": f"Research results for: {query}",
        "sources_consulted": parsed_sources,
        "confidence": 0.0,
        "status": "placeholder - connect live sources via AgentCore Gateway",
    }


# ---------------------------------------------------------------------------
# Analysis Tool
# ---------------------------------------------------------------------------
@tool
def analysis_tool(data: str, analysis_type: str = "summary") -> dict[str, Any]:
    """Analyse the provided data and return structured insights.

    Args:
        data: Raw data or text to analyse.
        analysis_type: The kind of analysis to perform.
                       One of 'summary', 'trend', 'comparison', 'sentiment'.

    Returns:
        A dict with keys: analysis, analysis_type, confidence.
    """
    logger.info("Analysis tool invoked | type='%s' data_len=%d", analysis_type, len(data))

    valid_types = {"summary", "trend", "comparison", "sentiment"}
    normalized_type = analysis_type.strip().lower()
    if normalized_type not in valid_types:
        logger.warning(
            "Invalid analysis_type '%s' received; falling back to 'summary'. "
            "Valid types: %s",
            analysis_type,
            ", ".join(sorted(valid_types)),
        )
        normalized_type = "summary"

    # In production the AgentCore Code Interpreter executes analytical
    # scripts against the supplied data.
    return {
        "analysis": f"{normalized_type.title()} analysis of provided data",
        "analysis_type": normalized_type,
        "data_length": len(data),
        "confidence": 0.0,
        "status": "placeholder - connect Code Interpreter via AgentCore",
    }


# ---------------------------------------------------------------------------
# Semantic Memory Tools
# ---------------------------------------------------------------------------
@tool
def memory_store_tool(
    content: str,
    namespace: str = "agentic-observability",
    metadata: str = "{}",
) -> dict[str, Any]:
    """Store content in AgentCore semantic memory.

    Args:
        content: The text content to persist.
        namespace: Memory namespace for isolation.
        metadata: JSON string of additional metadata tags.

    Returns:
        A dict confirming the storage operation.
    """
    logger.info("Memory store | namespace='%s' content_len=%d", namespace, len(content))

    try:
        parsed_meta = json.loads(metadata) if metadata else {}
        if isinstance(parsed_meta, dict):
            meta = parsed_meta
        else:
            logger.warning(
                "Metadata must be a JSON object, got %s; falling back to empty dict.",
                type(parsed_meta).__name__,
            )
            meta = {}
    except json.JSONDecodeError:
        logger.warning("Invalid JSON metadata '%s'; falling back to empty dict.", metadata)
        meta = {}

    # In production this calls the AgentCore Memory API.
    return {
        "stored": True,
        "namespace": namespace,
        "content_preview": content[:100],
        "metadata": meta,
        "status": "placeholder - connect AgentCore Semantic Memory",
    }


@tool
def memory_recall_tool(
    query: str,
    namespace: str = "agentic-observability",
    max_results: int = 5,
) -> dict[str, Any]:
    """Recall relevant content from AgentCore semantic memory.

    Args:
        query: Natural-language query for semantic search.
        namespace: Memory namespace to search within.
        max_results: Maximum number of results to return.

    Returns:
        A dict with matching memory entries.
    """
    logger.info("Memory recall | namespace='%s' query='%s'", namespace, query)

    if max_results < 1:
        logger.warning("Invalid max_results=%d; falling back to 5.", max_results)
        max_results = 5

    # In production this calls the AgentCore Memory API with vector similarity.
    return {
        "results": [],
        "query": query,
        "namespace": namespace,
        "max_results": max_results,
        "status": "placeholder - connect AgentCore Semantic Memory",
    }
