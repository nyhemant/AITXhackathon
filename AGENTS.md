# 1Less (AITXhackathon)

## Brand
- **1Less** = initiative / site.
- **Dinner** = meal thread (`/`).
- **Field Trip Kit** = outing thread (parent-facing UI name). Code path stays `static/field-pack/` and URL `/field-pack/`.
- Kid-facing language in printables: **mission** (e.g. “Your mission at the Dallas Zoo”).
- Do not use “Baby’s Day Out” in new user-facing copy.

## Continuity
- Read `.grok/HANDOFF.md` when continuing 1Less / Field Trip Kit work.
- Grok session title for this initiative: **1less**.

## Engineering
- Serve Field Trip Kit static via `web.py` at `/field-pack/`.
- In-app links: absolute `/field-pack/...` (pages use `<base href="/field-pack/">`).
- Before claiming live: smoke landing, app, place pages, Start outing hrefs (see HANDOFF).
- Global agent prefs: `~/.grok/rules/`.
