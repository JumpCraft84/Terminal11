#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
sudo apt update
sudo apt install -y python3-tk python3-venv python3-pip
python3 -m venv --system-site-packages .venv
.venv/bin/python -m pip install -r requirements.txt
printf '\nInstalled! Run: .venv/bin/python terminal11.py\n'
