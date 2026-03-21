# 🔭 Agentic Core Observability

**Advanced AI architecture demonstrating enterprise orchestration using Bedrock Agents, Strands SDK, and AgentCore Runtime.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-FF9900?logo=amazonaws&logoColor=white)](https://aws.amazon.com/bedrock/)
[![Contact A Taylor](https://img.shields.io/badge/Contact-A%20Taylor-brightgreen?logo=mail.ru&logoColor=white)](https://ataylor.getform.com/5w8wz)

---

This is a  multi-agent research and automation hub where every routing decision, every tool call, and every memory lookup is traced, measured, and guarded against hallucination drift.

The core idea is simple. Wire up a Strands SDK supervisor that routes tasks to specialized agents, deploy the whole thing on AgentCore Runtime with semantic memory baked in, and connect managed Bedrock Agents through the Gateway for true Agent-to-Agent orchestration. Then wrap every layer in observability so you can actually see what your agents are doing and catch them before they spin out.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- AWS CLI configured with valid credentials
- Access to Amazon Bedrock models

### Installation

```bash
# Clone the repository
git clone https://github.com/ATaylorAerospace/Agentic-Core-Observability.git
cd Agentic-Core-Observability

# Install dependencies
pip install -r src/requirements.txt

# Verify your environment
python -m tests.test_connection
```

### Run the Agent

```bash
# Interactive mode
python -m src.app

# With custom configuration
python -m src.app --model-id us.anthropic.claude-sonnet-4-20250514 --region us-east-1 --user-id your-user-id
```

### Deploy Infrastructure

```bash
cd cdk
pip install -r ../src/requirements.txt
cdk bootstrap
cdk deploy
```

### Verify the Connection

Run the built-in test script to check that everything is wired up:

```bash
python -m tests.test_connection
```

This runs 5 checks: AWS credentials, Bedrock model access, Strands SDK import, Supervisor initialization, and tool registration. Green across the board means you are good to go.

---

## 🧠 Architecture Overview

```
                     +---------------------+
                     |   User / Client     |
                     +----------+----------+
                                |
                                v
                     +----------+----------+
                     |  Supervisor Agent    |  <-- Strands SDK Orchestrator
                     |  (Intent Router)     |
                     +----+----------+-----+
                          |          |
               +----------+    +-----+--------+
               |               |              |
          +----v----+   +-----v-----+  +------v------+
          |Researcher|  |  Analyst   |  |  Semantic   |
          |  Agent   |  |   Agent    |  |  Memory     |
          +----+-----+  +-----+-----+  +-------------+
               |               |
    +----------+-----+ +------+--------+
    | Bedrock Agent  | | Code          |
    | (A2A Gateway)  | | Interpreter   |
    +----------------+ +---------------+
```

**Supervisor Agent** receives every request, classifies intent (RESEARCH / ANALYSIS / GENERAL), and routes to the right specialist. It maintains a full execution trace and runs hallucination-loop detection on every cycle.

**Researcher Agent** gathers information from authoritative sources using the AgentCore Browser tool (Nova Act) and delegates deep synthesis tasks to a managed Bedrock Agent via the A2A Gateway.

**Analyst Agent** interprets data and identifies trends using the AgentCore Code Interpreter in a sandboxed Python environment.

**Semantic Memory** stores and recalls user preferences (report format, preferred sources, analysis depth) so the system gets smarter with each session.

For the full technical breakdown, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## 🛠️ Multi-Protocol Tooling

This repository demonstrates three distinct integration patterns running in a single workflow:

| Protocol | Component | Purpose |
|---|---|---|
| **Strands Native** | Supervisor, Researcher, Analyst | Direct tool invocation via `@tool` decorators |
| **AgentCore Gateway (A2A)** | Bedrock Research Agent | Agent-to-Agent orchestration across managed and custom agents |
| **AgentCore Built-in** | Code Interpreter, Browser (Nova Act) | Sandboxed code execution and live web navigation |

### Tool Registry

- `research_tool` - Structured source retrieval with confidence scoring
- `analysis_tool` - Multi-mode data analysis (summary, trend, comparison, sentiment)
- `memory_store_tool` - Persist content to AgentCore semantic memory
- `memory_recall_tool` - Vector similarity search over stored memory
- `http_request` - Direct HTTP calls via Strands tools
- **Code Interpreter** - Sandboxed Python execution (AgentCore built-in)
- **Browser / Nova Act** - Headless web navigation with domain allowlisting

---

## 📊 Observability & Tracing

This is the heart of the project. Every agent interaction is observable at multiple levels:

### Hallucination Loop Detection

The Supervisor monitors its own execution trace for repetitive routing patterns. When the same action fires N times without meaningful progress, the circuit breaks:

```python
# The agent stops itself and tells you why
{
    "response": "I detected a repetitive pattern in my reasoning and stopped...",
    "loop_detected": true,
    "trace": [...]
}
```

No more silent hallucination spirals burning tokens in a loop. The agent catches itself, stops, and gives you a transparent explanation.

### Confidence Scoring

Every tool response includes a `confidence` field. Responses below the threshold (default 0.85) trigger additional verification or a low-confidence disclaimer to the user.

### Trace Inspection

Pull the full execution trace at any time during an interactive session:

```
You > trace
[
  {
    "action": "supervisor_response",
    "input_preview": "Research the latest trends in...",
    "session_id": "a1b2c3d4-...",
    "user_id": "default"
  }
]
```

### AWS X-Ray Integration

Distributed tracing across all agent invocations, memory lookups, and Gateway calls. Configured in `.agentcore/config.yaml` with a default sample rate of 1.0 (every request traced).

### Structured Logging

JSON-formatted logs with trace IDs for correlation. Query patterns across sessions using CloudWatch Log Insights.

---

## 📁 Project Structure

```
Agentic-Core-Observability/
├── .agentcore/
│   └── config.yaml              # AgentCore runtime, memory, and gateway config
├── src/
│   ├── agents/
│   │   ├── __init__.py          # Module exports
│   │   ├── supervisor.py        # Strands Supervisor/Orchestrator agent
│   │   └── tools.py             # Custom @tool definitions
│   ├── app.py                   # Application entry point
│   └── requirements.txt         # Python dependencies
├── cdk/
│   ├── app.py                   # CDK application entry
│   └── agent_stack.py           # Infrastructure stack (Bedrock, IAM, S3, Logs)
├── docs/
│   └── ARCHITECTURE.md          # Detailed architecture documentation
├── tests/
│   └── test_connection.py       # Environment and connection verification
├── LICENSE
└── README.md
```

---

## 🔐 Security

- S3 buckets enforce `BlockPublicAccess.BLOCK_ALL` with versioning enabled
- Bedrock Agent roles follow least-privilege IAM policies
- Code Interpreter runs in a sandboxed environment with execution time limits
- Browser tool restricts navigation to an explicit domain allowlist
- No credentials stored in code; all secrets use environment variables or AWS IAM roles

---

## 👨‍💻 Author

**A Taylor** ·<p align="left">
  <a href="https://ataylor.getform.com/5w8wz">
    <img src="https://img.shields.io/badge/Contact_A_Taylor-Get_In_Touch-brightgreen?logo=mail.ru&logoColor=white" alt="Contact A Taylor" />
  </a>
</p>
---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

Copyright (c) 2026 A Taylor. All rights reserved.
