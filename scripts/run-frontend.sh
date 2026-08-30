#!/usr/bin/env bash
# Serve the CREST frontend (static SPA). Run alongside the backend.
set -euo pipefail
cd "$(dirname "$0")/../frontend"
PORT="${1:-5500}"
echo "==> CREST SPA on http://localhost:${PORT}"
exec python3 -m http.server "${PORT}"
