# Setup & Running (project-specific)

This project uses a local `python_libs/` folder and wrapper scripts to avoid modifying system Python on Debian/Ubuntu systems (PEP 668). The instructions below reflect the implementation in this repository.

1) Install dependencies into the project-local folder

```bash
cd /path/to/AEGIS
python3 -m pip install --target ./python_libs -r requirements.txt
```

If you need to install a single package, use `--target ./python_libs`:

```bash
python3 -m pip install --target ./python_libs gradio
```

2) Environment variables

Create `.env` from `.env.example` and set your Google API key:

```bash
cp .env.example .env
# Edit .env and set GOOGLE_API_KEY
export GOOGLE_API_KEY=$(grep GOOGLE_API_KEY .env | cut -d '=' -f2)
```

3) Run the API server (recommended)

Use the `run_uvicorn.sh` wrapper which ensures `python_libs/` is on `PYTHONPATH`:

```bash
./run_uvicorn.sh src.main:app_service --reload
```

Endpoints:

- `GET /health` — health check
- `POST /chat?question=...` — chat endpoint
- `GET /docs` — Swagger UI

4) Run the frontend (optional)

The Gradio front-end is provided in `src/frontend.py` and can be launched with the `run.sh` wrapper:

```bash
./run.sh src/frontend.py
```

5) Notes

- Avoid committing `python_libs/`; add it to `.gitignore`.
- Wrapper scripts: `run.sh` for ad-hoc Python scripts, `run_uvicorn.sh` for the API server.
- The LLM is lazily initialized at FastAPI startup to ensure the `GOOGLE_API_KEY` is present.
