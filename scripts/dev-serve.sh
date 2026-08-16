#!/bin/bash
# Local QA — same server as 1less.app, this machine only.
# Usage: ./scripts/dev-serve.sh [port]
# Then open http://127.0.0.1:8000/field-pack/virtual-field-trip/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"
PORT="${1:-8000}"
echo "Local QA (not 1less.app)"
echo "  http://127.0.0.1:${PORT}/field-pack/"
echo "  http://127.0.0.1:${PORT}/field-pack/virtual-field-trip/"
echo "Ctrl+C to stop."
exec python3 -m busyparent_agent.web --host 127.0.0.1 --port "$PORT"
