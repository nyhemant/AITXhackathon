# 1Less — session handoff

**Last updated:** 2026-08-02  
**Session name / resume title:** `1less`  
**Session id:** `019fbec4-7ce9-7671-a86f-dcd91de08328` (cwd `/Users/arku`)  
Resume: `/resume` → **1less**, or `grok --resume 1less` from `/Users/arku`.

## Naming (keep tied)

| Name | Role |
|------|------|
| **1Less** | Parent initiative / brand / site (1less.app) |
| **Dinner** | Meal thread — `/` |
| **Baby's Day Out** | Outing thread (was “Arya’s Field Pack”) — `/field-pack/` |
| URL path `field-pack` | Technical path only; **do not** rename in URLs unless migrating redirects |

Product copy and nav labels say **Baby's Day Out**. Code folders may still say `field-pack`.

## What this is

- **Live:** https://1less.app/field-pack/ (tunnel → localhost:8000)
- **Code:** `~/Projects/AITXhackathon` → `static/field-pack/` + `web.py` prefix `/field-pack`
- **Sister:** `~/Projects/arya-zoo-field-pack` (earlier pack/docs; name is legacy)

## Current product shape

- Landing: US map + City + Venue dropdowns
- **Fort Worth under Dallas area only** (no separate FW city/pin); FW Zoo in Dallas venue list
- Ready packs: Dallas Zoo, Children’s Aquarium Dallas, Perot children’s museum
- Most other venues: soon pages
- Strategy: DFW home; TX/Austin-heavy; national magnets; LA yes; Orlando = KSC only

## Recent fixes (do not regress)

1. Start outing 404: `<base href="/field-pack/">` + `../app.html` → `/app.html`. Use absolute `/field-pack/app.html#/venue/...`
2. Global agent rules: `~/.grok/rules/release-hygiene.md`, `learn-over-time.md`; memory on
3. Branding: **Baby's Day Out** under **1Less** (not Arya’s Field Pack)

## Key paths

```
static/field-pack/   # Baby's Day Out UI
  index.html, app.html, js/, places/, img/usa-map.svg
src/busyparent_agent/web.py  # Dinner + Baby's Day Out threads
```

## Pending

- [ ] Hard-refresh confirm Start outing + new name live
- [ ] Git push when auth works
- [ ] More precooked packs; SEO polish; PWA later
- [ ] Optional later: pretty URL `/babys-day-out` → redirect from `/field-pack`

## Smoke

```bash
curl -sf -o /dev/null -w "%{http_code}\n" http://localhost:8000/field-pack/
curl -sf -o /dev/null -w "%{http_code}\n" http://localhost:8000/field-pack/app.html
curl -sf http://localhost:8000/field-pack/ | grep -o "Baby's Day Out" | head -3
grep -R "app.html" static/field-pack/places static/field-pack/js/places-data.js | grep -v '/field-pack/app.html' || true
```

## Archive (pre-rearchitecture)
- Tag: `snapshot/pre-rearch-2026-08-02`
- Branch: `archive/pre-rearch-babys-day-out-2026-08-02`
- See `.grok/ARCHIVE-PRE-REARCH.md`

