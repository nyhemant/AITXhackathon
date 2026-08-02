# 1Less (AITXhackathon)

## Brand
- **1Less** = initiative / site.
- **Dinner** = meal thread (`/`).
- **Baby's Day Out** = outing thread (UI name). Code path stays `static/field-pack/` and URL `/field-pack/` unless a redirect migration is planned.
- Do not call the product “Baby’s Day Out” in user-facing copy.

## Continuity
- Read `.grok/HANDOFF.md` when continuing 1Less / Baby's Day Out work.
- Grok session title for this initiative: **1less**.

## Engineering
- Serve Baby's Day Out static via `web.py` at `/field-pack/`.
- In-app links: absolute `/field-pack/...` (pages use `<base href="/field-pack/">`).
- Before claiming live: smoke landing, app, place pages, Start outing hrefs (see HANDOFF).
- Global agent prefs: `~/.grok/rules/`.
