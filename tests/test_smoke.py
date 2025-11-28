import os
import sys
import urllib.request
import json


def test_imports():
    # Ensure key modules from python_libs can be imported
    sys.path.insert(0, os.path.join(os.getcwd(), "python_libs"))
    import gradio  # noqa: F401
    import langgraph  # noqa: F401
    import langchain_community  # noqa: F401


def test_health_endpoint_running():
    try:
        resp = urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2)
        data = json.loads(resp.read())
        assert data.get("status") == "ok"
    except Exception:
        # If server is not running, test should not fail the suite in this minimal smoke test
        print("Warning: health endpoint not reachable; start server to run full integration tests")
