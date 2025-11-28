# Setup & Usage

## Prerequisites

1.  **Python 3.10+**
2.  **API Key:** A **Google Gemini API Key** is required for the models used in the primary `main.py` script. Free tiers are available at Google AI Studio.
3.  **Virtual Environment:** Highly recommended to prevent dependency conflicts.

---

## 1. Installation

It is recommended to set up and activate a virtual environment (`venv`) in your project's root folder before installing dependencies.

    # 1. Activate your environment (Mac/Linux example)
    source venv/bin/activate

    # 2. Install core dependencies
    # This includes LangChain, LangGraph, Google GenAI, and Community tools.
    pip install langchain langchain-community langchain-google-genai langgraph

---

# Setup & Usage (AEGIS)

This doc covers the repository-specific workflow (no system-wide pip installs). The project uses a local `python_libs/` folder and wrapper scripts to avoid PEP 668 issues on Debian/Ubuntu systems.

Prerequisites
- Python 3.10+ (3.12 tested in development)
- Google Gemini API key for `langchain-google-genai`

1) Install dependencies (project-local)

```bash
cd /home/shubh/projects/AEGIS
python3 -m pip install --target ./python_libs -r requirements.txt
```

If you need to add a single package:

```bash
python3 -m pip install --target ./python_libs gradio
```

2) Set environment variables

Create a local `.env` from `.env.example` and export the Google API key before starting the server or frontend:

```bash
cp .env.example .env
# Edit .env to set GOOGLE_API_KEY
export GOOGLE_API_KEY=$(grep GOOGLE_API_KEY .env | cut -d '=' -f2)
```

3) Prepare the database (Sakila sample DB)

Run the database creation/population script if `data/sakila.db` is missing:

```bash
python3 utility/create_db.py
```

4) Run the API server (recommended)

Use the `run_uvicorn.sh` wrapper which ensures the `python_libs/` folder is on `PYTHONPATH`:

```bash
./run_uvicorn.sh src.main:app_service --reload
```

Key endpoints
- `GET /health` — Health check
- `POST /chat?question=...` — Chat endpoint (returns agent response)
- `GET /docs` — Swagger UI

5) Run the Gradio frontend (optional)

The frontend is provided for quick interactive exploration. It calls the running FastAPI chat endpoint.

```bash
./run.sh src/frontend.py
# Gradio typically serves at http://127.0.0.1:7860
```

Notes
- The repository provides two wrapper scripts:
  - `run.sh` — generic script wrapper that sets `PYTHONPATH` to `python_libs/` and runs a Python command.
  - `run_uvicorn.sh` — wrapper that runs Uvicorn with the same `PYTHONPATH` set.
- LLM initialization is deferred to FastAPI startup (lifespan) so that `GOOGLE_API_KEY` must be exported before server start. This prevents `DefaultCredentialsError` at import time.
- Avoid committing `python_libs/` (it's added to `.gitignore`). Use `requirements.txt` to reproduce installs.

Troubleshooting
- If you see `DefaultCredentialsError`, verify `GOOGLE_API_KEY` is set in your environment.
- If `Address already in use` occurs, make sure no other uvicorn process is running on port 8000 (use `pkill -f uvicorn` or change port with `--port`).

See `docs/SETUP_DOC.md` for a shorter quick-start checklist.
