#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo "== item uniqueness (warn-only) =="
python3 scripts/lint_item_uniqueness.py
echo "== reachability =="
python3 scripts/check_venue_reachability.py
echo "== enforce top10 (T11) =="
python3 scripts/lint_item_uniqueness.py --enforce-top10
echo "OK"
