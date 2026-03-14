#!/usr/bin/env python3
# Agentic Core Observability - Connection Verification Test
# Copyright (c) 2026 A Taylor. All rights reserved.
# Licensed under the MIT License.
#
# Quick smoke test to verify that the Strands SDK can reach Bedrock
# and that the agent pipeline initializes correctly. Run this from
# your IDE or terminal after configuring AWS credentials.
#
# Usage:
#   python -m tests.test_connection
#   -- or --
#   pytest tests/test_connection.py -v

from __future__ import annotations

import json
import sys

import boto3
from botocore.exceptions import ClientError, NoCredentialsError


def test_aws_credentials() -> bool:
    """Verify that valid AWS credentials are available."""
    print("[1/5] Checking AWS credentials...")
    try:
        sts = boto3.client("sts")
        identity = sts.get_caller_identity()
        print(f"  OK  - Account: {identity['Account']}, ARN: {identity['Arn']}")
        return True
    except NoCredentialsError:
        print("  FAIL - No AWS credentials found. Configure your environment.")
        return False
    except ClientError as exc:
        print(f"  FAIL - {exc}")
        return False


def test_bedrock_model_access(
    model_id: str = "us.anthropic.claude-sonnet-4-20250514",
    region: str = "us-east-1",
) -> bool:
    """Verify that the configured Bedrock model is accessible."""
    print(f"[2/5] Testing Bedrock model access ({model_id})...")
    try:
        client = boto3.client("bedrock-runtime", region_name=region)
        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 32,
                "messages": [{"role": "user", "content": "Say OK"}],
            }),
        )
        body = json.loads(response["body"].read())
        output = body.get("content", [{}])[0].get("text", "")
        print(f"  OK  - Model responded: {output[:50]}")
        return True
    except ClientError as exc:
        print(f"  FAIL - {exc}")
        return False
    except Exception as exc:
        print(f"  FAIL - Unexpected error: {exc}")
        return False


def test_strands_import() -> bool:
    """Verify that the Strands SDK is installed and importable."""
    print("[3/5] Importing Strands SDK...")
    try:
        import strands  # noqa: F401
        from strands import Agent, tool  # noqa: F401
        from strands.models.bedrock import BedrockModel  # noqa: F401

        print(f"  OK  - strands version: {getattr(strands, '__version__', 'unknown')}")
        return True
    except ImportError as exc:
        print(f"  FAIL - {exc}")
        print("  Hint: pip install strands-agents strands-agents-tools")
        return False


def test_supervisor_init() -> bool:
    """Verify that the SupervisorAgent initializes without errors."""
    print("[4/5] Initializing SupervisorAgent...")
    try:
        from src.agents.supervisor import SupervisorAgent

        agent = SupervisorAgent()
        print(f"  OK  - Session: {agent._session_id}")
        return True
    except Exception as exc:
        print(f"  FAIL - {exc}")
        return False


def test_tool_registration() -> bool:
    """Verify that custom tools are callable."""
    print("[5/5] Testing tool registration...")
    try:
        from src.agents.tools import (
            analysis_tool,
            memory_recall_tool,
            memory_store_tool,
            research_tool,
        )

        r = research_tool(query="test query", sources="web")
        assert "findings" in r, "research_tool missing 'findings' key"

        a = analysis_tool(data="sample data", analysis_type="summary")
        assert "analysis" in a, "analysis_tool missing 'analysis' key"

        s = memory_store_tool(content="test content")
        assert s.get("stored") is True, "memory_store_tool did not confirm storage"

        m = memory_recall_tool(query="test recall")
        assert "results" in m, "memory_recall_tool missing 'results' key"

        print("  OK  - All 4 tools responded correctly")
        return True
    except Exception as exc:
        print(f"  FAIL - {exc}")
        return False


def main() -> None:
    """Run all connection verification tests."""
    print("=" * 60)
    print("  Agentic Core Observability - Connection Test")
    print("  Author: A Taylor")
    print("=" * 60)
    print()

    results = {
        "AWS Credentials": test_aws_credentials(),
        "Bedrock Model": test_bedrock_model_access(),
        "Strands SDK": test_strands_import(),
        "Supervisor Init": test_supervisor_init(),
        "Tool Registration": test_tool_registration(),
    }

    print()
    print("-" * 60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Results: {passed}/{total} passed\n")

    for name, ok in results.items():
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {name}")

    print()
    if passed == total:
        print("All checks passed. Your environment is ready!")
    else:
        print("Some checks failed. Review the output above and fix issues.")
        print("Tip: Ensure AWS credentials are configured and dependencies installed.")

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
