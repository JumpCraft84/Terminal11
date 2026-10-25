#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if [ -x .venv/bin/python ]; then exec .venv/bin/python terminal11.py; fi
exec python3 terminal11.py
