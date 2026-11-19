# Weekly email box (grown-ups only)

## Sub-features
- Box `form.kz-nl` on /printables/ and the 3 printable sheet pages only (never on kids' pages).
- Fix-it message for empty or bad addresses (`aria-invalid`), honeypot `input[name=website]` off-screen.
- "See a sample email" dialog (`dialog.kz-nl-dialog`), Escape closes and focus returns.
- Success: "You're in! Check your inbox to confirm…", box locks, `kz_nl_subscribed_v2` hides boxes later.
- Kit robot check: reply `{error:"verify", verify_url}` shows "One more step … Do the check (opens a new tab)" (`a.kz-nl-verify`), no sign_up event, box stays usable.
- No-JS: bad address → `/newsletter/oops/?reason=email`; Kit error → `/newsletter/try-again/`; robot check → `/newsletter/one-more-step/`; success → `/newsletter/thanks/`.

## How to get to it (user POV)
/printables/ → "For grown-ups" box at the bottom.

## Driving it with verify.py
`--only j5`: errors, honeypot, sample dialog, then a MOCKED signup (page.route answers /api/newsletter in the browser:
robot-check reply → "One more step" with Kit's link; success reply → "You're in", box locks; both posts must be caught).
Real signups are paused since 2026-11-18; `--real-signup` needs `KZK_LIVE_SIGNUP_APPROVED=yes` and a new owner OK. j7 posts a bad address with no JS and
expects 303 to `/newsletter/oops/?reason=email`, and checks the no-JS pages name one cause each.

## Gotchas
- Kit quarantines signups forwarded from imini's IP (2026-11-18). Expect the robot-check message on live until the owner switches to Kit's API or the IP clears.
- The Kit confirmation email comes from "KidZooKit <ask@kidzookit.com>" with subject "Confirm your KidZooKit weekly animal card" (Kit account setting since 2026-11-18 10:03 PM CT). /privacy/ names this sender; j7 checks it.
- Live signups are paused. When allowed again: never click a confirmation link, never trigger a broadcast, never sign up any address but nyhemant+…@gmail.com.
- The server limits signups to 5 per visitor IP per hour (in memory); repeated runs can hit "Too many sign-up tries".
