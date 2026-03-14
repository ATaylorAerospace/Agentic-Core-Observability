# Architecture Overview

**Project:** Agentic Core Observability
**Author:** A Taylor
**Version:** 1.0.0

---

## High-Level Design

Agentic Core Observability is a hybrid agentic workflow that combines three AWS
services into a single, observable multi-agent system:

```
                          +---------------------+
                          |   User / Client     |
                          +----------+----------+
                                     |
                                     v
                          +----------+----------+
                          |  Supervisor Agent    |
                          |  (Strands SDK)       |
                          +----+----------+-----+
                               |          |
                    +----------+    +-----+--------+
                    |               |              |
               +----v----+   +-----v-----+  +-----v------+
               |Researcher|  |  Analyst   |  |  Memory    |
               |  Agent   |  |   Agent    |  |  (Semantic)|
               +----+-----+  +-----+-----+  +------------+
                    |               |
         +----------+-----+ +------+-------+
         | Bedrock Agent  | | Code         |
         | (via Gateway)  | | Interpreter  |
         +----------------+ +--------------+
```

## Component Breakdown

### 1. Supervisor Agent (Strands SDK)

The Supervisor is the orchestration layer. It receives every user request,
classifies it by intent (RESEARCH, ANALYSIS, or GENERAL), and delegates to the
appropriate specialist agent.

- **Framework:** Strands Agents SDK
- **Model:** Amazon Bedrock (configurable)
- **Responsibilities:**
  - Intent classification and task routing
  - Execution trace management
  - Hallucination-loop detection and circuit breaking
  - User preference enrichment via semantic memory

### 2. Researcher Agent

Handles information gathering tasks. Uses the AgentCore Browser tool (Nova Act)
for live web research and can delegate to a managed Bedrock Agent via the
AgentCore Gateway for deep, document-level synthesis.

- **Tools:** research_tool, http_request, Browser (Nova Act)
- **Gateway:** Connects to `bedrock-research-agent` via A2A protocol

### 3. Analyst Agent

Handles data interpretation and trend analysis. Leverages the AgentCore Code
Interpreter for running analytical Python scripts in a sandboxed environment.

- **Tools:** analysis_tool, Code Interpreter
- **Capabilities:** Summary, trend, comparison, and sentiment analysis

### 4. AgentCore Memory (Semantic)

Provides long-term, user-scoped memory using vector similarity search. The
Supervisor stores and recalls user preferences (report format, preferred
sources, analysis depth) so the system improves with each interaction.

- **Embedding Model:** Amazon Titan Embed Text v2
- **Retention:** 90 days (configurable)
- **Namespace Isolation:** Per-application and per-user

### 5. AgentCore Gateway (A2A)

Exposes managed Bedrock Agents as callable tools. This enables Agent-to-Agent
orchestration where the Strands-based Supervisor can invoke fully managed
Bedrock Agents without managing their lifecycle directly.

## Observability and Hallucination Detection

The platform implements multi-layer observability:

1. **Execution Tracing:** Every agent action is recorded in a structured trace
   array. Traces include action type, input preview, session ID, and timestamps.

2. **Hallucination-Loop Detection:** The Supervisor monitors its own trace for
   repetitive routing patterns. If the same action is taken N times in
   succession without meaningful progress, the loop is broken and the user
   receives a transparent explanation.

3. **Confidence Scoring:** Tools return a `confidence` field with every result.
   Responses below the configured threshold (0.85) trigger additional
   verification or a candid "low confidence" disclaimer.

4. **AWS X-Ray Integration:** Distributed tracing across all agent invocations,
   memory lookups, and Gateway calls for end-to-end visibility.

5. **Structured Logging:** JSON-formatted logs with trace IDs for correlation
   across CloudWatch Log Insights queries.

## Deployment

Infrastructure is defined as code using AWS CDK (Python). A single
`cdk deploy` provisions:

- Bedrock Agents (Research + Analyst) with IAM roles
- S3 bucket for artifacts and knowledge base documents
- CloudWatch Log Group for centralized observability
- Resource tags for AgentCore Runtime discovery

The Strands-based agents are deployed via AgentCore Runtime using the
`.agentcore/config.yaml` configuration file.

## Security

- All S3 buckets enforce `BlockPublicAccess.BLOCK_ALL`
- Bedrock Agent roles follow least-privilege IAM policies
- Code Interpreter runs in a sandboxed environment
- Browser tool restricts navigation to an allowlist of domains
- No credentials are stored in code; all secrets use environment variables
