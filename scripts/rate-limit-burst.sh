#!/bin/bash
# Burst-test the origin rate limiter. Does not create accounts or post email.
# Usage: ./scripts/rate-limit-burst.sh [url] [n]
# Example: ./scripts/rate-limit-burst.sh http://127.0.0.1:8000/field-pack/ 16
set -euo pipefail
URL="${1:-http://127.0.0.1:8000/field-pack/}"
N="${2:-16}"
UA="${RATE_LIMIT_BURST_UA:-Mozilla/5.0 BurstTestFamily}"

echo "burst $N  GET $URL"
echo "ua    $UA"
ok=0
limited=0
other=0
for i in $(seq 1 "$N"); do
  headers="$(curl -sS -D - -o /tmp/1less-rate-limit-body.txt \
    -A "$UA" \
    -w "HTTP_CODE:%{http_code}\n" \
    "$URL" || true)"
  code="$(printf '%s\n' "$headers" | awk -F: '/^HTTP_CODE:/{print $2}' | tail -n 1)"
  retry="$(printf '%s\n' "$headers" | awk -F': ' 'tolower($1)=="retry-after"{print $2}' | tr -d '\r' | tail -n 1)"
  if [ "$code" = "200" ] || [ "$code" = "301" ] || [ "$code" = "302" ]; then
    ok=$((ok + 1))
    echo "  $i  $code"
  elif [ "$code" = "429" ]; then
    limited=$((limited + 1))
    echo "  $i  429  Retry-After=${retry:-?}"
  else
    other=$((other + 1))
    echo "  $i  $code"
  fi
done
echo "ok=$ok limited=$limited other=$other"
if [ "$limited" -gt 0 ]; then
  echo "limiter responded 429 (no signup, no captcha page)."
fi
