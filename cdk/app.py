#!/usr/bin/env python3
# Agentic Core Observability - CDK Application Entry Point
# Copyright (c) 2026 A Taylor. All rights reserved.
# Licensed under the MIT License.

from __future__ import annotations

import os

import aws_cdk as cdk

from agent_stack import AgenticCoreObservabilityStack

app = cdk.App()

AgenticCoreObservabilityStack(
    app,
    "AgenticCoreObservabilityStack",
    env=cdk.Environment(
        account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
        region=os.environ.get("CDK_DEFAULT_REGION", "us-east-1"),
    ),
    description="Agentic Core Observability - Hybrid Agentic Workflow Infrastructure",
)

app.synth()
