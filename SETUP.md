# AEGIS Setup Guide

## Quick Start

This project uses a local `python_libs/` folder instead of virtual environments due to PEP 668 restrictions on Debian/Ubuntu.

### 1. Install Dependencies

```bash
python3 -m pip install --target ./python_libs --upgrade \
  gradio \
  langchain-google-genai \
  langchain-community \
  langgraph
```

Or install everything at once:
```bash
python3 -m pip install --target ./python_libs -r requirements.txt
```

### 2. Set Up Google API Key

Copy `.env.example` to `.env` and add your Google API key:
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

Then export it before running:
```bash
export GOOGLE_API_KEY=$(grep GOOGLE_API_KEY .env | cut -d '=' -f2)
```

### 3. Run the Application

#### Option A (Step-1): Using the wrapper script (recommended)
```bash
./run_uvicorn.sh src.main:app_service --reload
```

#### Option A (Step-2): Run Python scripts directly (In a new terminal)
```bash
./run.sh src/frontend.py
```

#### Option B: Manual PYTHONPATH setup
```bash
export PYTHONPATH="$PWD/python_libs:$PYTHONPATH"
uvicorn src.main:app_service --reload
```

The server will be available at: `http://127.0.0.1:8000`

API docs: `http://127.0.0.1:8000/docs`

## Installed Packages

See `requirements.txt` for the complete list of pinned versions.

Key packages:
- `gradio==6.0.0` — UI framework
- `langchain-google-genai==3.2.0` — Google Generative AI integration
- `langchain-community==0.4.1` — LangChain community tools
- `langgraph==1.0.3` — Graph-based agent framework

## Troubleshooting

**ImportError: No module named 'langchain_google_genai'**
- Make sure you're using `./run.sh` or `./run_uvicorn.sh` or have `PYTHONPATH` set correctly.

**DefaultCredentialsError from Google API**
- Ensure `GOOGLE_API_KEY` environment variable is set before running.

**ModuleNotFoundError for other packages**
- Run `python3 -m pip install --target ./python_libs <package_name>` and update `requirements.txt`.

## Database Setup

If you need to create the database:
```bash
./run.sh utility/create_db.py
```
