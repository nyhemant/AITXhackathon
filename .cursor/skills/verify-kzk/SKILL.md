---
name: verify-kzk
description: Drive live KZK (kidzookit.com, KidZooKit) like a tired parent on a phone (390x844) and a desktop (1280x800) with Playwright, and prove the /start/ front door (approved H1, "Arya’s Wildlife Project" wordmark, print path above the fold), a map pin to the printed scavenger hunt (card, #printable-hunt, print drawer, window.print), animal cards, the kid quiz, the grown-up weekly email box (errors, sample dialog, Kit robot check, one real test signup), printable PDFs and printed QR destinations, and the about/privacy/404/newsletter pages. Use before and after any KZK change ships, or when someone asks "does kidzookit.com still work".
---

# Verify KZK (kidzookit.com)

KZK is one Python stdlib server (`src/busyparent_agent/web.py`, `ThreadingHTTPServer`) serving `static/`.
Live it runs on imini as launchd job `ai.openclaw.aitx-busymom-app` from `~/Projects/AITXhackathon`, behind a
Cloudflare tunnel for `kidzookit.com`. The harness drives the public URL (or a local copy) from any machine with
Playwright + Chrome. Name the site as "KZK (kidzookit.com)" everywhere; the script stops on any other host.
1LESS (1less.app) and MGC (myglucoach.app) are other sites: never point this at them.

## Launch

- Live: nothing to launch. Target `https://kidzookit.com`.
- Local copy of a branch (never switch branches in `~/Projects/AITXhackathon`; use a clone or worktree):
  `PYTHONPATH=src:. python3 -m busyparent_agent.web --host 127.0.0.1 --port 8771 & echo $! > /tmp/kzk-local.pid`
  Ready when `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8771/printables/` prints `200`.
  A local copy forwards a real signup to Kit from your machine's IP, so only drive j5 locally with
  `page.route("**/api/newsletter", ...)` stubs, never with `--real-signup`.
- Teardown: `kill $(cat /tmp/kzk-local.pid)`. Never `pkill python` (other apps run on imini).

## Doctor (read-only, run first)

```bash
.cursor/skills/verify-kzk/scripts/doctor.sh https://kidzookit.com     # or http://127.0.0.1:8771
```
Checks: host is kidzookit.com (stops on any other domain), `/` answers 301 to `/start/`, `/start/` 200 with the
CSP header and the approved H1, `/printables/` 200 with the weekly email box, one printable PDF starts with `%PDF`,
and on imini the launchd job has a PID.

## Drive

```bash
PY=/workspace/prod-ready/.venv/bin/python     # any Python with `pip install playwright`
$PY .cursor/skills/verify-kzk/scripts/verify.py --out /tmp/kzk-verify/run1                 # all journeys, phone + desktop
$PY .cursor/skills/verify-kzk/scripts/verify.py --only j2,j4 --out /tmp/kzk-verify/run2     # some journeys
```
**Live newsletter signups are PAUSED (owner rule 2026-11-18).** j5 mocks the signup by default: `page.route` answers
`/api/newsletter` inside the browser (a robot-check reply, then a success reply), so nothing reaches the server or Kit
and no email can go out. `--real-signup` refuses to run unless `KZK_LIVE_SIGNUP_APPROVED=yes` is also set, and that
needs a new OK from the owner. Do not set it on your own.
Uses Chrome at `/usr/bin/google-chrome` when present. About 1 minute for a full run.
Rules the script keeps:
- Locators only for waits. No `wait_for_function` string predicates: the CSP has no `'unsafe-eval'`.
- Analytics opt-out on every request: cookie `one_less_analytics=off`, `?notrack=1`, UA containing `kz-verify`.
- `window.print` is replaced before page scripts (CDP init script) by a counter on `<html data-kzv-printed>`,
  so Print is proven without a dialog.
- Tap the visible pin label (`[data-home-pin=…] .kzm-tag`), not the pin button: some pins are "tag only" and their
  44px box centre sits under a neighbour (Perot's centre is under Fort Worth Zoo's label).
- Paused: `KZK_LIVE_SIGNUP_APPROVED=yes ... --real-signup` would send ONE real signup to
  `hemant+kzkverify-<MMDDHHMM>@mail.grokbot.com` (phone only). Never nyhemant@gmail.com or a nyhemant+ alias, never a broadcast.

Journeys (details in `features/`): j1 front door, j2 pin → printed hunt, j3 animal cards, j4 quiz,
j5 weekly email box, j6 PDFs + printed QR codes + `/` 301, j7 trust/legal/error pages + no-JS newsletter post.
Key handles: `h1`, `.start-wordmark`, `a.hxd-sheet[data-kz-cta=home-demo]`, `[data-home-pin]`, `#home-pin-card`,
`#home-pin-close`, `#printable-hunt`, `button.kz-scav-print`, `#mission-overlay`, `#mission-sheet`,
`#mission-print-btn`, `.study-choice[data-choice=…]`, `.study-level-btn`, `[data-study-reveal]`, `form.kz-nl`,
`.kz-nl-msg`, `a.kz-nl-sample`, `dialog.kz-nl-dialog`.

## Evidence

`<out>/results.json` (one row per check: journey, viewport, check, PASS/WARN/FAIL, detail) and `<out>/j*-*.png`.
Exit code 1 means at least one FAIL. WARN = Cloudflare beacon noise or an off-site request.
Proof standards: drive the real path (tap, type, Print), compare what a parent sees with the page's own data, and
check side effects. For a real signup (paused) the screen is not proof: search the bot inbox
hemant@mail.grokbot.com for the `+kzkverify-<stamp>` address (include spam). Exactly ONE confirmation email must arrive
within a few minutes. None = the site lied (see K2 below). The robot-check path was removed on 2026-11-20.
Never click a confirmation link: that adds a test address to the real KidZooKit Weekly list.

Known (2026-11-19): sign-ups go through Kit's v4 API on the server, so parents should not see a robot-check page.
The box says to look for "Confirm your KidZooKit weekly animal card" from KidZooKit. Live newsletter signups stay
paused unless the owner sets KZK_LIVE_SIGNUP_APPROVED=yes (and then only to an approved test address).

## Cleanup

The script closes its own browser. Local server: `kill $(cat /tmp/kzk-local.pid)`. Evidence stays in `<out>/`;
keep it outside the repo.

## Maintenance

When a check fails, decide site bug vs harness bug first. Fix wrong selectors in the harness; never loosen a check
to make a site bug pass. Approved copy (H1, wordmark) is pinned in `scripts/verify.py`; the title/meta/H1 freeze
runs through 2026-11-24, so change the pin only with Heymant's yes. Keep `features/` in step with the app
(`/maintain-verification-skill`). The SEO release checks (sitemap, titles, 24 scav pages, freeze digests) live in
`/workspace/kidzookit-loop/weekly-2026-11-16/live_check_v6.py`, not here.
