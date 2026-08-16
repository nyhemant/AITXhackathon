#!/bin/bash
# Production Mini only: fast-forward pull from GitHub if this checkout is clean.
# Skips if you have unsaved Mini edits (yolo on production still wins).
# Usage: ./scripts/sync-from-github.sh
# Optional launchd: copy scripts/com.1less.sync-from-github.plist to ~/Library/LaunchAgents/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "not a git repo: $ROOT" >&2
  exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "skip: local tracked changes (Mini yolo). Commit/stash or leave live as-is."
  exit 0
fi

git fetch origin
branch="$(git rev-parse --abbrev-ref HEAD)"
remote="origin/${branch}"
if ! git rev-parse --verify "$remote" >/dev/null 2>&1; then
  echo "skip: no $remote" >&2
  exit 0
fi

if [ "$(git rev-parse HEAD)" = "$(git rev-parse "$remote")" ]; then
  echo "already up to date with $remote"
  exit 0
fi

if ! git merge-base --is-ancestor HEAD "$remote"; then
  echo "skip: local history has commits GitHub does not. Push or fix by hand." >&2
  exit 1
fi

git pull --ff-only origin "$branch"
echo "live tree now $(git rev-parse --short HEAD)"
