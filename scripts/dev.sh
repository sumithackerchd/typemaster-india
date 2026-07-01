#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

# Create the virtualenv on first run.
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
. .venv/bin/activate

# Install / update Python dependencies (fast no-op when already satisfied).
pip install -q --disable-pip-version-check -r requirements.txt

# Run the Flask dev server on the port the preview expects.
# --debug enables the auto-reloader so code/template changes are picked up.
exec python -m flask --app app.py run --host=0.0.0.0 --port=3000 --debug
