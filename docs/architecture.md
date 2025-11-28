# Architecture and LangGraph Flow

AEGIS uses a multi-agent design where monitoring and user-facing interaction are implemented as composable LangGraph workflows. The current codebase implements the Interaction Agent and documents the Analyst Agent design.

## 1) Shared State

- The system uses an `AgentState` (a Python `TypedDict`) to carry conversation history and operational fields between nodes. Common fields include:
  - `messages`: list of `BaseMessage` objects (User, Agent, ToolMessage)
  - `monitoring_alert` (optional): string describing an issue the Analyst detected
  - `alert_target` (optional): which agent should act (e.g., `performance`)

## 2) Core Monitoring Loop (Design)

- The Analyst Agent is the central monitoring node in the full design. It periodically samples metrics and runs diagnostic queries. If it detects anomalies it sets `monitoring_alert` and selects an `alert_target` to trigger action.

- Action agents (Performance, Security, Data Quality) receive alerts, run tools, apply fixes (where appropriate), and return control to the Analyst for verification.

## 3) Interaction Agent (Implemented)

- The Interaction Agent is implemented in `src/main.py` as a small LangGraph flow with two primary nodes:
  - `agent` (`call_model`): sends system + user messages to the LLM (Gemini via `langchain-google-genai`).
  - `tools` (`tool_node`): executes SQL tools returned by the LLM and packages outputs as `ToolMessage` objects.

- The flow uses `should_continue` to decide whether to route to `tools` or end the interaction.

## 4) Implementation notes

- Packages are installed to a local `python_libs/` directory to avoid system-managed Python changes (PEP 668). Use the project's wrapper scripts to add this folder to `PYTHONPATH`:
  - `./run.sh` — run arbitrary Python scripts with `python_libs/` on `PYTHONPATH`.
  - `./run_uvicorn.sh` — run Uvicorn with `python_libs/` on `PYTHONPATH`.

- The LLM is lazily initialized at FastAPI startup (FastAPI lifespan). This requires `GOOGLE_API_KEY` to be exported in the environment before starting the server; it prevents `DefaultCredentialsError` that happens when the LLM is constructed at module import time.

## 5) Tools and DB

- The Interaction Agent uses `SQLDatabaseToolkit` from `langchain_community.agent_toolkits.sql.toolkit` to construct helpful SQL tools, such as `sql_db_query` and `sql_db_list_tables`.
- The tools operate on `data/sakila.db` (SQLite). Ensure `sakila.db` exists by running `python3 utility/create_db.py`.

## 6) Running the system

- Start the API server with the wrapper (recommended):

```bash
export GOOGLE_API_KEY="your_key_here"
./run_uvicorn.sh src.main:app_service --reload
```

- Test the agent:

```bash
curl -X POST "http://127.0.0.1:8000/chat?question=What%20tables%20are%20in%20the%20database"
```

---

For more detailed setup steps, see `docs/SETUP_DOC.md` and `docs/usage.md`.
# Architecture and LangGraph Flow

The AEGIS system uses a **decentralized, hub-and-spoke model** where the **Analyst Agent** acts as the continuous monitoring hub, feeding data to specialized functional agents. 

[Image of multi-agent system flow diagram]


## 1. The Agent State (Shared Memory)

The core of the LangGraph implementation is the **shared state**, which allows information to be passed between agents. We use a custom `AgentState` based on a Python `TypedDict` to manage conversation history and operational data.

This state includes fields for:
* `messages`: The running log of all communications (from User, Agent, Tool).
* `monitoring_alert`: A string set by the Analyst to describe the problem detected (e.g., "slow\_query\_detected").
* `alert_target`: A string set by the Analyst to specify which agent should handle the problem (e.g., "performance" or "security").

---

## 2. The Core Monitoring Loop (AEGIS Protocol)

The graph runs in a **continuous, perpetual loop**, cycling between monitoring and necessary action. This loop is the foundation of the system's **autonomous governance**. 

1.  **START → Analyst Agent:** The system initializes or is periodically routed back to the **Analyst Agent**.
2.  **Analyst Agent (Node):** This agent runs diagnostic tools (e.g., SQL queries for latency, log scanners) and compares real-time metrics against the established performance and security baseline.
3.  **Conditional Edge (Analyst):** The Analyst runs the core decision function:
    * **If** a **critical event** is detected (e.g., query execution time exceeds 3x baseline), the agent sets the `monitoring_alert` and `alert_target` fields in the shared state. The graph then routes to the specified action agent.
    * **Else**, the graph routes to **END** (or continues polling in a persistent deployment).
4.  **Action Agent (Node):** The designated agent (e.g., **Performance Agent**) receives the alert, uses its own tools to formulate a solution (e.g., generates a `CREATE INDEX` SQL statement), and applies the fix.
5.  **Action Agent → Analyst:** After taking action, the agent always returns to the **Analyst Agent** to verify the fix and log the resolution.

---

## 3. The Interaction Agent (User Interface)

The **Interaction Agent** operates asynchronously to the core monitoring loop but leverages the same database and tools. It serves as the user-facing natural language interface.

It functions as a standard **ReAct-style agent** built on a simple two-node cycle:

1.  **User Input → Interaction Node (LLM):** The LLM receives the user's question.
2.  **Conditional Edge:** It decides whether the question requires external data:
    * **If** a tool is required (e.g., `sql_db_query`), route to the **Tool Node**.
    * **Else**, end with a direct answer.
3.  **Tool Node:** Executes the generated SQL query against the `sakila.db` database.
4.  **Tool Node → Interaction Node:** The query results are fed back to the LLM for final formatting and presentation to the user.