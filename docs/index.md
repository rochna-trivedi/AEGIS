# 🛡️ Project AEGIS: Autonomous Ecosystem for Governance and Intelligent Security

## 💡 Abstract

AEGIS demonstrates how a set of specialized, collaborative agents can autonomously interact with a relational database (the Sakila sample DB) to answer natural language questions, monitor performance, and propose actions.

The current repository focuses on the **Interaction Agent** (natural language → SQL) and includes designs and scaffolding for monitoring agents such as the Analyst, Performance, Security, and Data Quality agents.

### Key Agent Components

| Agent | Function | Status |
| :--- | :--- | :--- |
| **Interaction** | Translates natural language to SQL, executes queries, and formats results. | Implemented |
| **Analyst** | Periodically inspects query patterns and system metrics to detect anomalies. | Draft / Design |
| **Performance** | Suggests and applies optimizations (indexes, config). | Planned |
| **Security** | Monitors and responds to suspicious access patterns. | Planned |
| **Data Quality** | Detects and remediates inconsistent data. | Planned |

## 🏗️ Technical Architecture (LangGraph Flow)

AEGIS uses **LangGraph** to model the control flow between compact functional nodes (LLM call, tool invocation, decision logic). The Interaction Agent implements a two-node ReAct-style loop:

- `agent` node: sends messages to the LLM (Gemini via `langchain-google-genai`) and receives responses (may include tool calls).
- `tools` node: executes requested tools (SQL query, list tables, etc.) and returns tool outputs as `ToolMessage` objects.

See `docs/architecture.md` for the monitoring loop and design notes.

---

Start with [Usage](usage.md) to run the server and frontend locally.
# 🛡️ Project AEGIS: Autonomous Ecosystem for Governance and Intelligent Security

## 💡 Abstract

The management of modern database systems is increasingly complex, demanding significant manual effort for optimization, security, and maintenance. **AEGIS** is a novel framework built on a decentralized multi-agent architecture. It distributes core management tasks among a team of specialized, collaborative agents to create a **self-driving, self-securing, and self-repairing database ecosystem.**

### Key Agent Components

| Agent | Function | Status |
| :--- | :--- | :--- |
| **Interaction** | Translates natural language questions/commands to SQL. | Implemented |
| **Analyst** | Monitors query patterns and establishes performance/security baselines. | Next Priority |
| **Performance** | Proactively optimizes the database (indexing, tuning). | Future |
| **Security** | Detects SQL injection and anomalous access. | Future |
| **Data Quality** | Identifies and cleans inconsistent or duplicate data. | Future |

## 🏗️ Technical Architecture (LangGraph Flow)

AEGIS is built using the **LangGraph** framework to manage the state and collaboration between the independent agents. The core agent loop, called the **AEGIS Protocol**, is designed for durability and real-time response.

---

**See [Architecture](architecture.md) for the detailed agent loop.**