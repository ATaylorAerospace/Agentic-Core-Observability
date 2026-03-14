# Agentic Core Observability - Application Entry Point
# Copyright (c) 2026 A Taylor. All rights reserved.
# Licensed under the MIT License.
#
# Main entry point for the Agentic Core Observability platform.
# Launches the Supervisor agent and exposes a simple interactive loop
# for local development. In production, AgentCore Runtime invokes main()
# directly as configured in .agentcore/config.yaml.

from __future__ import annotations

import argparse
import json
import logging
import sys

from src.agents.supervisor import SupervisorAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main(
    model_id: str = "us.anthropic.claude-sonnet-4-20250514",
    region: str = "us-east-1",
    user_id: str = "default",
) -> None:
    """Start the Supervisor agent and enter an interactive session."""

    logger.info("Initializing Agentic Core Observability...")
    logger.info("Model: %s | Region: %s", model_id, region)

    supervisor = SupervisorAgent(model_id=model_id, region=region)
    logger.info("Supervisor agent ready. Session: %s", supervisor._session_id)

    print("\n=== Agentic Core Observability ===")
    print("Type your request below. Type 'quit' to exit, 'trace' to view execution trace.\n")

    while True:
        try:
            user_input = input("You > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("Goodbye.")
            break

        if user_input.lower() == "trace":
            trace = supervisor.get_trace()
            print(json.dumps(trace, indent=2, default=str))
            continue

        result = supervisor.run(user_input, user_id=user_id)

        if result["loop_detected"]:
            print(f"\n[LOOP DETECTED] {result['response']}\n")
        else:
            print(f"\nAgent > {result['response']}\n")


def cli() -> None:
    """Parse CLI arguments and launch the application."""
    parser = argparse.ArgumentParser(
        description="Agentic Core Observability - Hybrid Agentic Workflow",
    )
    parser.add_argument(
        "--model-id",
        default="us.anthropic.claude-sonnet-4-20250514",
        help="Bedrock model ID for the agents",
    )
    parser.add_argument(
        "--region",
        default="us-east-1",
        help="AWS region for Bedrock and AgentCore services",
    )
    parser.add_argument(
        "--user-id",
        default="default",
        help="User ID for semantic memory personalization",
    )
    args = parser.parse_args()
    main(model_id=args.model_id, region=args.region, user_id=args.user_id)


if __name__ == "__main__":
    cli()
