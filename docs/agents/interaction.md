# Interaction Agent

This document describes the implemented **Interaction Agent** — the user-facing natural language interface to the `sakila.db` test database.

Overview
--

- The Interaction Agent receives a user question (plain text) and decides whether to answer directly or call a tool (SQL tools) to fetch structured data.
- It's implemented as a compact LangGraph workflow with two primary nodes: `agent` and `tools`.

Implementation details
--

- LLM: `ChatGoogleGenerativeAI` (via `langchain_google_genai`) — initialized lazily at FastAPI startup. This avoids credential errors at import time.
- Tools: Provided by `langchain_community.agent_toolkits.sql.toolkit.SQLDatabaseToolkit` and include SQL helpers such as `sql_db_query`, `sql_db_list_tables`, etc.
- Flow:
  1. `agent` node (`call_model`): sends the system and user messages to the LLM. The LLM may return text or a tool call (a `ToolMessage`).
  2. If a tool call is present, the graph routes to the `tools` node (`tool_node`) which looks up the requested tool in `tools_by_name`, invokes it, and packages the result as a `ToolMessage` back to the LLM.
  3. The `agent` node receives the tool output and produces a final answer.

Key code elements (high-level)
--

- `call_model(state)` — invokes `llm_with_tools.invoke(messages)` and returns an LLM message.
- `tool_node(state)` — iterates tool calls, runs the corresponding tool, and returns tool output messages.
- `should_continue(state)` — decides whether to follow the tool path or finish.

Running the Interaction Agent
--

- FastAPI server: `./run_uvicorn.sh src.main:app_service --reload` (ensures `python_libs/` is on `PYTHONPATH`).
- Health endpoint: `GET /health` — quick liveness check.
- Chat endpoint: `POST /chat?question=<your_question>` — queries the agent.

Notes
--

- The Interaction Agent uses a local `python_libs/` folder to host third-party packages (avoids PEP 668 on Debian/Ubuntu). The repo provides `run.sh` and `run_uvicorn.sh` wrappers that set `PYTHONPATH` automatically.
- For an interactive UI, run the Gradio frontend with: `./run.sh src/frontend.py` (default Gradio port 7860).
