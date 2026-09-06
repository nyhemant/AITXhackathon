# Field Trip Kit — Agent Brief

Shared context for the multi-session polish program (`docs/POLISH-TASKS.md`).
Read this at the start of every task session.

## Hard constraints

- **Static site** under `/field-pack/` (repo: `static/field-pack/`).
- **Deterministic client-side generation** of missions and shortlists.
- **No runtime LLM calls.**
- **No accounts, logins, or backends** for Field Trip Kit product flows.
- **All URLs stay under `/field-pack/`.** Never break an existing URL or anchor; alias if renaming.
- **Kid names never leave the device** (personalization is local-only).
- **Analytics** = lightweight visit and print events only; **no PII**.
- **The `/dinner` project is frozen** — never touch it.
- **Mobile-first**, **390px baseline** (Pinterest traffic).

## Product context

Two first-class utilities:

1. **Venue missions** — pick a place, get a shortlist and a printable one-page mission.
   Primary entry intent; used **during** the visit.
2. **Animal / sea-life / attraction Q&A cards** — standalone explore-and-learn product used
   at home **before and after** visits. Currently often buried behind `app.html#/…` hash routes.

**Unifying frame:** one day, three moments —

- **Before** — cards at home  
- **During** — paper mission, phone in the bag  
- **After** — cards again  

Zoos lead the launch; parks are a fast-follow. **Dallas Zoo** is the content quality bar.

## Content rules

- **Never invent facts** about venues, animals, or parks.
- Any new factual claim gets a `verify` field:
  - `{ "status": "sourced", "source": "<URL>" }` when grounded in an official source
    (nps.gov, the venue’s own site)
  - `{ "status": "todo" }` for human review otherwise
- **NPS maps/photos** are public domain and may be used with a credit line.
- **Zoo/museum maps** are linked, never copied into the repo as if they were ours.

## Conventions

- **All displayed counts** computed from data at **build time** (or clearly from live data
  arrays at runtime), never hardcoded literals that drift.
- **Copy strings** as editable constants (comments OK for A/B alternates).
- **Real list markup** — no empty spacer elements.
- **Reuse existing design tokens** — no new design system.
- **Every task ends with** that task’s QA checklist executed and a **completion note** in
  `docs/POLISH-TASKS.md`.

## Repo map (recon)

| Area | Location |
|------|----------|
| Venue mission JSON (SoT) | `static/field-pack/data/venues/{slug}.json` (~218) |
| Landing place pins | `static/field-pack/js/places-data.js` → `window.FP_PLACES` |
| Q&A / animal catalog | `static/field-pack/js/catalog.js` → `window.FIELD_PACK_CATALOG` (+ mission templates) |
| Card deep links (today) | `/field-pack/app.html#/venue/{venue}/item/{id}` |
| Page generator | `scripts/generate_bdo_seo.py` → venue pages, type hubs, landing catalog, sitemaps |
| Continent bucketing | `_venue_continent()` in `generate_bdo_seo.py` |
| Print sheet | `js/print-kit.js`, `js/mission/mission-ui.js`, `js/mission/mission-engine.js` |
| Mission map images | `js/print-maps.js` + `media/maps/` |
| Shell + analytics | `static/shell/shell.js` → `window.OneLessAnalytics.track` / `window.trackEvent` |
| Landing hero/map JS | `js/landing-hook.js`, `js/landing-map.js` |
| Item uniqueness lint | `scripts/lint_item_uniqueness.py` → `scripts/data/item-uniqueness-report.md` |
| Sitemap | `static/field-pack/sitemap.xml` |
| LLM site map | `static/llms.txt` is public at `/llms.txt` (`web.py`) |
| Search Console | `static/google*.html` served at `/google*.html` (`web.py`) |
| Brand / path rules | `AGENTS.md`, `.grok/HANDOFF.md` |

**Slug note:** Great Smoky Mountains = `great-smoky-mountains`.

## Task workflow

1. Read this brief + the task row in `docs/POLISH-TASKS.md`.
2. Skip sub-items marked `already-shipped`.
3. Stay inside task scope; no drive-by refactors.
4. Run the task QA list; write a completion note; set status.
5. Stop for human review before the next task unless the user says otherwise.
