#!/usr/bin/env bash
# Read-only: is this KZK (kidzookit.com) instance worth driving?  usage: doctor.sh [BASE]
set -u
BASE="${1:-https://kidzookit.com}"; BASE="${BASE%/}"
HOST=$(echo "$BASE" | sed -E 's#^https?://([^/:]+).*#\1#')
case "$HOST" in kidzookit.com|127.0.0.1|localhost) ;; *) echo "STOP: host $HOST is not kidzookit.com"; exit 2;; esac
UA="Mozilla/5.0 (compatible; KidZooKitCheck/1.0; kz-verify)"; CK="one_less_analytics=off"
fail=0
ok() { echo "ok   $*"; }; bad() { echo "FAIL $*"; fail=1; }
loc=$(curl -s -o /dev/null -w '%{http_code} %{redirect_url}' -A "$UA" -b "$CK" "$BASE/?notrack=1")
[[ "$loc" == 301\ *"/start/"* ]] && ok "/ -> $loc" || bad "/ -> $loc"
hdr=$(curl -s -D - -o /tmp/kzk-doctor-start.html -A "$UA" -b "$CK" "$BASE/start/?notrack=1")
echo "$hdr" | head -1 | grep -q " 200" && ok "/start/ 200" || bad "/start/ $(echo "$hdr" | head -1)"
echo "$hdr" | grep -qi "^content-security-policy:.*frame-ancestors 'none'" && ok "CSP header" || bad "CSP header missing"
grep -q "Printable scavenger hunts for your next zoo, aquarium or museum trip" /tmp/kzk-doctor-start.html && ok "approved H1" || bad "H1 changed"
grep -q "Arya’s Wildlife Project" /tmp/kzk-doctor-start.html && ok "wordmark" || bad "wordmark missing"
curl -s -A "$UA" -b "$CK" "$BASE/printables/?notrack=1" | grep -q 'class="kz-nl ' && ok "/printables/ email box" || bad "/printables/ email box missing"
head4=$(curl -s -A "$UA" -b "$CK" "$BASE/printables/pdf/letter/scavenger-hunt.pdf?notrack=1" | head -c 4)
[ "$head4" = "%PDF" ] && ok "printable PDF" || bad "printable PDF ($head4)"
if [ "$HOST" = kidzookit.com ] && command -v ssh >/dev/null; then
  pid=$(ssh -o ConnectTimeout=8 -o BatchMode=yes arku@imini.tail7a88f5.ts.net 'launchctl list | grep ai.openclaw.aitx-busymom-app' 2>/dev/null | awk '{print $1}')
  [ -n "$pid" ] && [ "$pid" != "-" ] && ok "imini launchd ai.openclaw.aitx-busymom-app pid $pid" || echo "skip imini launchd check (no ssh or no pid: '$pid')"
fi
exit $fail
