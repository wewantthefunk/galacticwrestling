#!/usr/bin/env bash
# Create a local virtualenv and install the project (editable) with dev dependencies.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  echo "Created .venv"
else
  echo "Using existing .venv"
fi

# shellcheck source=/dev/null
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

echo ""
echo "Seeding AI opponents (creates roster if missing)..."
python -m galactic_wrestling.ai_opponents

echo ""
echo "Done. Activate the environment with:"
echo "  source .venv/bin/activate"
