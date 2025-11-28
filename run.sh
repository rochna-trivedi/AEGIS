#!/bin/bash
# Wrapper script to run Python with python_libs on PATH
export PYTHONPATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/python_libs:$PYTHONPATH"
python3 "$@"
