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
`--only j5` (UI, no signup) and `--only j5 --viewports phone --real-signup` (ONE signup to
`nyhemant+kzkverify-<stamp>@gmail.com`). Then check the inbox as SKILL.md says. j7 posts a bad address with no JS and
expects 303 to `/newsletter/oops/?reason=email`, and checks the no-JS pages name one cause each.

## Gotchas
- Kit quarantines signups forwarded from imini's IP (2026-11-18). Expect the robot-check message on live until the owner switches to Kit's API or the IP clears.
- The Kit confirmation email comes from "1Less <ask@1less.app>" with subject "Important: confirm your subscription" (Kit account setting).
- Never click a confirmation link, never trigger a broadcast, never sign up any address but nyhemant+…@gmail.com.
- The server limits signups to 5 per visitor IP per hour (in memory); repeated runs can hit "Too many sign-up tries".
