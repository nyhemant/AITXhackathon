# Weekly email box (grown-ups only)

## Sub-features
- Box `form.kz-nl` on /printables/ and the 3 printable sheet pages only (never on kids' pages).
- Fix-it message for empty or bad addresses (`aria-invalid`), honeypot `input[name=website]` off-screen.
- "See a sample email" dialog (`dialog.kz-nl-dialog`), Escape closes and focus returns.
- Success: "You're in! Check your inbox for “Confirm your KidZooKit weekly animal card” from KidZooKit…", box locks, `kz_nl_subscribed_v2` hides boxes later.
- Sign-ups go through the server (Kit v4 API). Parents should not see a robot-check page. A leftover `{error:"verify"}` reply still shows a check link and does not lock the box.
- No-JS: bad address → `/newsletter/oops/?reason=email`; Kit error → `/newsletter/try-again/`; robot check → `/newsletter/one-more-step/`; success → `/newsletter/thanks/`.

## How to get to it (user POV)
/printables/ → "For grown-ups" box at the bottom.

## Driving it with verify.py
`--only j5`: errors, honeypot, sample dialog, then a MOCKED signup (page.route answers /api/newsletter in the browser:
robot-check leftover → "One more step" with the check link; success reply → the confirmation-subject line, box locks; both posts must be caught).
Real signups stay paused; `--real-signup` needs `KZK_LIVE_SIGNUP_APPROVED=yes` and a new owner OK. j7 posts a bad address with no JS and
expects 303 to `/newsletter/oops/?reason=email`, and checks the no-JS pages name one cause each.

## Gotchas
- The confirmation email comes from "KidZooKit <ask@kidzookit.com>" with subject "Confirm your KidZooKit weekly animal card". /privacy/ names this sender and no longer mentions a robot check; j7 checks that.
- Live signups are paused. When allowed again: never click a confirmation link, never trigger a broadcast, never sign up any address but nyhemant+…@gmail.com.
- The server limits signups to 5 per visitor IP per hour (in memory); repeated runs can hit "Too many sign-up tries".
