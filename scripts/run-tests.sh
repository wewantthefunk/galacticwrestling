#!/usr/bin/env bash
# Run the test suite with coverage (run scripts/bootstrap.sh first).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -d .venv ]]; then
  echo "No .venv found. Run:  bash scripts/bootstrap.sh" >&2
  exit 1
fi

# shellcheck source=/dev/null
source .venv/bin/activate

exec python -m pytest "$@"
