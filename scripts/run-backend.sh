#!/usr/bin/env bash
# Bootstrap & launch the CREST backend (development).
set -euo pipefail

cd "$(dirname "$0")/../backend"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

# shellcheck source=/dev/null
source .venv/bin/activate

if ! python -c "import fastapi" >/dev/null 2>&1; then
  echo "==> Installing dependencies..."
  pip install --upgrade pip >/dev/null
  pip install -r requirements.txt
fi

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "==> Created .env from .env.example — edit secrets before production use."
fi

echo "==> Starting CREST API on http://${APP_HOST:-0.0.0.0}:${APP_PORT:-8000}"
exec uvicorn app.main:app --reload --host "${APP_HOST:-0.0.0.0}" --port "${APP_PORT:-8000}"
