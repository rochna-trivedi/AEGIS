# Analyst Agent (Design Notes)

The Analyst Agent is planned to be the continuous monitoring and decision-making component of AEGIS. It inspects runtime metrics, query patterns, and system health, then decides whether other agents (Performance, Security, Data Quality) should act.

Goals
--

- Continuously sample query performance and error rates.
- Maintain baselines (mean/median latencies, variance) for critical queries and endpoints.
- Detect anomalies (slow queries, sudden traffic spikes, unusual access patterns) and raise `monitoring_alert` state entries.
- Route alerts to appropriate action agents and verify the outcomes.

Design overview
--

- **State**: The Analyst updates the shared `AgentState` (e.g., `monitoring_alert`, `alert_target`) used by LangGraph to route execution.
- **Tools**: SQL diagnostics tools (EXPLAIN, sampling queries), log parsers, and optional telemetry collectors.
- **Decision logic**: Threshold-based + lightweight statistical checks; machine-learned models may be added later for anomaly detection.

Integration points
--

- Runs within the LangGraph monitoring loop (START -> Analyst -> conditional edge -> Action agent).
- Logs decisions and actions for auditing.

Next steps for implementation
--

1. Implement sampling queries and a small stateful baseline store.
2. Add tool implementations to run EXPLAIN and identify missing indexes.
3. Create an `analyst` node similar to the Interaction `agent` node, returning structured alerts when thresholds are exceeded.
