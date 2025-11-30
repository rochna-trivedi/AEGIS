# 🛡️ Project AEGIS: Autonomous Ecosystem for Governance and Intelligent Security

## 💡 Abstract

AEGIS demonstrates how a set of specialized, collaborative agents can autonomously interact with a relational database (the Sakila sample DB) to answer natural language questions, monitor performance, and propose actions.
 
![AEGIS demo](images/AEGIS_Demo.gif)

*Demo: AEGIS interaction example — natural language question → SQL → results.*

The current repository focuses on the **Interaction Agent** (natural language → SQL) and includes designs and scaffolding for monitoring agents such as the Analyst, Performance, Security, and Data Quality agents.

## 🧩 Key Agent Components

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

**See [Architecture](architecture.md) for the detailed agent loop.**