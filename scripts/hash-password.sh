#!/usr/bin/env bash
# Generate an Argon2id password hash for a seed admin user (prints to stdout).
# Usage:   scripts/hash-password.sh "mySecretPassw0rd!"
set -euo pipefail
cd "$(dirname "$0")/../backend"
source .venv/bin/activate
python - <<PY
from app.core.security import hash_password
import sys
print(hash_password(sys.argv[1]))
PY
