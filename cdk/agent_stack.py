# Agentic Core Observability - CDK Infrastructure Stack
# Copyright (c) 2026 A Taylor. All rights reserved.
# Licensed under the MIT License.
#
# Provisions all AWS resources required by the Agentic Core Observability
# platform: Bedrock Agent, IAM roles, Lambda layers, and AgentCore-compatible
# resource tags for runtime discovery.

from __future__ import annotations

from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    Tags,
    aws_bedrock as bedrock,
    aws_iam as iam,
    aws_logs as logs,
    aws_s3 as s3,
)
from constructs import Construct


class AgenticCoreObservabilityStack(Stack):
    """CloudFormation stack for the Agentic Core Observability platform."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ------------------------------------------------------------------
        # S3 Bucket - Agent artifacts and knowledge base storage
        # ------------------------------------------------------------------
        artifacts_bucket = s3.Bucket(
            self,
            "AgentArtifactsBucket",
            bucket_name=f"agentic-observability-artifacts-{self.account}",
            removal_policy=RemovalPolicy.RETAIN,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            versioned=True,
        )

        # ------------------------------------------------------------------
        # IAM Role - Bedrock Agent execution role
        # ------------------------------------------------------------------
        agent_role = iam.Role(
            self,
            "BedrockAgentRole",
            assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com"),
            description="Execution role for the Agentic Core Observability Bedrock Agent",
        )

        agent_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                ],
                resources=["arn:aws:bedrock:*::foundation-model/*"],
            )
        )

        agent_role.add_to_policy(
            iam.PolicyStatement(
                actions=["s3:GetObject", "s3:ListBucket"],
                resources=[
                    artifacts_bucket.bucket_arn,
                    f"{artifacts_bucket.bucket_arn}/*",
                ],
            )
        )

        # ------------------------------------------------------------------
        # CloudWatch Log Group - Observability
        # ------------------------------------------------------------------
        log_group = logs.LogGroup(
            self,
            "AgentLogGroup",
            log_group_name="/agentic-core-observability/agents",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # ------------------------------------------------------------------
        # Bedrock Agent - Research Agent (managed, exposed via Gateway)
        # ------------------------------------------------------------------
        research_agent = bedrock.CfnAgent(
            self,
            "ResearchAgent",
            agent_name="agentic-obs-research-agent",
            agent_resource_role_arn=agent_role.role_arn,
            foundation_model="us.anthropic.claude-sonnet-4-20250514",
            instruction=(
                "You are a Research Agent for the Agentic Core Observability platform. "
                "Your role is to search authoritative sources, retrieve relevant documents, "
                "and provide well-sourced summaries. Always cite your sources. "
                "Never fabricate references or data."
            ),
            description="Managed Bedrock Agent for deep research tasks",
            idle_session_ttl_in_seconds=600,
            auto_prepare=True,
        )

        # ------------------------------------------------------------------
        # Bedrock Agent - Analyst Agent
        # ------------------------------------------------------------------
        analyst_agent = bedrock.CfnAgent(
            self,
            "AnalystAgent",
            agent_name="agentic-obs-analyst-agent",
            agent_resource_role_arn=agent_role.role_arn,
            foundation_model="us.anthropic.claude-sonnet-4-20250514",
            instruction=(
                "You are an Analyst Agent for the Agentic Core Observability platform. "
                "Your role is to interpret data, identify trends, and produce concise "
                "analytical summaries. Ground every conclusion in the data provided. "
                "Flag low-confidence findings explicitly."
            ),
            description="Managed Bedrock Agent for data analysis tasks",
            idle_session_ttl_in_seconds=600,
            auto_prepare=True,
        )

        # ------------------------------------------------------------------
        # Tags for AgentCore Runtime discovery
        # ------------------------------------------------------------------
        Tags.of(self).add("project", "agentic-core-observability")
        Tags.of(self).add("managed-by", "aws-cdk")
        Tags.of(self).add("author", "a-taylor")
