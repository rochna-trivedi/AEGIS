#!/bin/bash
# Wrapper script to run uvicorn with python_libs on PATH
export PYTHONPATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/python_libs:$PYTHONPATH"
exec python3 -m uvicorn "$@"
