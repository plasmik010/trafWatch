#!/bin/sh

set -eo pipefail

source ./venv/bin/activate
exec python3 ./main.py
