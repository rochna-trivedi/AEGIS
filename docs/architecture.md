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