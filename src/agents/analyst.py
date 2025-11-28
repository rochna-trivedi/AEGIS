"""Analyst agent scaffold.

This module provides a minimal, testable scaffold for the Analyst agent described
in `docs/agents/analyst.md`. It intentionally avoids heavy dependencies and can
be integrated into the LangGraph workflow later.
"""
from typing import Dict, Any, Tuple
import sqlite3
import time


def sample_query_latency(db_path: str, sample_sql: str = "SELECT 1") -> float:
    """Run a simple query and return elapsed time in seconds."""
    start = time.perf_counter()
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(sample_sql)
        _ = cur.fetchall()
        conn.commit()
    finally:
        conn.close()
    return time.perf_counter() - start


def compute_baseline(latencies: "list[float]") -> Dict[str, float]:
    """Compute simple baseline statistics (mean, median, max)."""
    if not latencies:
        return {"mean": 0.0, "median": 0.0, "max": 0.0}
    sorted_l = sorted(latencies)
    n = len(sorted_l)
    mean = sum(sorted_l) / n
    median = sorted_l[n // 2] if n % 2 == 1 else (sorted_l[n//2 - 1] + sorted_l[n//2]) / 2
    return {"mean": mean, "median": median, "max": max(sorted_l)}


def detect_anomaly(current_latency: float, baseline: Dict[str, float], threshold: float = 3.0) -> Tuple[bool, str]:
    """Detect if current latency exceeds threshold * baseline_mean."""
    mean = baseline.get("mean", 0.0)
    if mean <= 0:
        return False, "baseline not established"
    if current_latency > threshold * mean:
        return True, f"latency {current_latency:.3f}s > {threshold}x baseline mean ({mean:.3f}s)"
    return False, "ok"


if __name__ == "__main__":
    print("Analyst scaffold loaded. Use functions for baseline sampling and anomaly detection.")
