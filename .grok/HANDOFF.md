# 1Less — session handoff

**Last updated:** 2026-08-09 (Intl parks P1 ship)  
**Session:** `1less`  
**Pre-rearch restore:** `git checkout snapshot/pre-rearch-2026-08-02`

## Product
- **1Less** brand · **Baby's Day Out** default (`/` → `/field-pack/`) · **Dinner** secondary (`/dinner` via More)

## Shell
- `static/shell/` — logo **52px** (44px mobile), product name, More menu
- CSS cache: `shell.css?v=2`

## BDO landing
- Hook hero + Ready now cards + city chips + map
- Map ready venue: **Start outing** primary, Place info secondary
- Soon city: **Save this city** → `localStorage` `1less-saved-cities`
- Waiting line + continue last outing (deep-link `#/trip/id`)

## Planner
- Print treasure hunt promoted on home
- Win banner after submit/teach
- Storage: `1less-babys-day-out-trips-v1`

## Smoke
```bash
curl -sI http://localhost:8000/ | grep Location
curl -sf -o /dev/null -w "%{http_code}\n" http://localhost:8000/field-pack/ http://localhost:8000/dinner http://localhost:8000/shell/shell.css
```

## Next optional
- Email notify for saved cities
- `/outings` alias
- More ready packs

## Voice & polish
- Voice: no Arya; kid-neutral; print blank explorer name
- Ready cards static HTML fallback; logo 52px attrs
- Missions framed optional after visit; planner topbar compact under shell

## Flow (3 levels — current)
1. **Home** `/` → `/field-pack/` — city + venue
2. **Outing** `app.html#/venue/{id}` — item list + print treasure hunt (+ optional customize)
3. **Item** `#/venue/{id}/item/{itemId}` — optional Q&A + print card

Removed from main path: planner home, build-shortlist step, saved-trips list, required place brochure hop.

## National MVP packs (2026-08-02)
- **23 venues ready** (shared catalog reuse). Home Ready strip still **Dallas 3 only**.
- All map cities/venues open outing packs: shortlist + hunt + optional Q&A.
- New shared items: giant-panda, red-panda, zebra, sci-* exhibit cards.
- Depth is MVP (not zoo-specific unique animals). Unique polish later.

## National Parks — complete Phase 1 ship (2026-08-08)

### Waves done
1. **Imagine art** — 62 `photos/np-*.jpg` via grok-imagine-image (style anchor + shared + landmarks + 30 heroes). Credit: Illustration · Field Trip Kit.
2. **SEO type landings** — `/field-pack/zoos|aquariums|museums|national-parks/` (+ `/parks/` alias). Tabs on home are crawlable `<a>` (left-click still filters map).
3. **P1b** — **63 US National Parks** full designated set (1a+1b+1c long-tail). Dual-write + bonus solid + SEO.

### Smoke
```bash
curl -sf -o /dev/null -w "%{http_code}
" \
  http://localhost:8000/field-pack/ \
  http://localhost:8000/field-pack/national-parks/ \
  http://localhost:8000/field-pack/zoos/ \
  http://localhost:8000/field-pack/yellowstone/ \
  http://localhost:8000/field-pack/joshua-tree/ \
  http://localhost:8000/field-pack/photos/np-hero-yellowstone.jpg
```

### Regen
```bash
python3 scripts/generate_bdo_seo.py
python3 scripts/scaffold_bonus_hunt.py --sync-file
python3 scripts/validate_bonus_hunts.py
```

### Park image wow (2026-08-09)
- Heroes **wired**: SEO banner + og:image, `/national-parks/` featured thumbs, map pin `pd-park-hero`.
- Regenerated with **`grok-imagine-image-quality`** (95+ assets: US heroes + shared stops + landmarks + intl).
- Cache `?v=q2` after scale-policy regen. Prompts: `scripts/data/np_hero_prompts.json`.
- **Scale policy:** vast vistas = no people; near scenes only = family ~1/9–1/7 frame; wildlife = animals only.

### International parks — P1 ship (2026-08-09)
- **78 parks total** = 63 US + **15 intl pilots**. Same `national_park` type; map `tier: "intl"` + `country`/`countryName`.
- Pilots: Banff, Jasper, Yoho, Plitvice, Eryri/Snowdonia, Lake District, Killarney, Fuji-Hakone-Izu, Nikkō, Fiordland, Blue Mountains, Kruger, Table Mountain, Torres del Paine, Iguazú (AR).
- Source list: `scripts/data/np_intl_phase1.json`. Dual-write venues + places + catalog; bonus solid (7 finds); SEO mission pages; hub copy worldwide (78 on `/national-parks/`).
- Unique landmarks: `np-lake-louise`, `np-plitvice-lakes`, `np-mount-fuji-lake`, `np-three-sisters`, `np-torres-towers`, `np-iguazu-falls`, `np-milford-sound`, `np-table-mountain` (inside `FIELD_PACK_CATALOG` — never inject outside the object).
- **Slice-specific cards (2026-08-09):** All **78** park venue JSON labels scrubbed (US + intl). No generic “Visitor center / Scenic overlook / Trailhead sign” left. SEO/mission uses `display_label`.
- **App parity:** `FIELD_PACK_VENUES[slug].itemDisplayNames` maps catalog id → park label; `app.js` / `print-kit.js` `getItem(id, venue)` applies it without mutating shared catalog cards.
- **Shared living cards with zoos:** parks use the same catalog ids + Wikimedia photos as zoos when practical (`african-lion`, `zebra`, `american-bison`, `elk`, `american-alligator`, …). Infra stops (VC, boardwalk, overlook) stay illustrated `np-*`. Do **not** global-replace catalog keys (duplicates last-wins).
- **P2 later:** more per region, contact-sheet art audit, optional country hubs. Not started.

### Smoke (intl + US regression)
```bash
python3 -m http.server 8000 --directory static
curl -sf -o /dev/null -w "%{http_code}\n" \
  http://localhost:8000/field-pack/national-parks/ \
  http://localhost:8000/field-pack/banff/ \
  http://localhost:8000/field-pack/plitvice-lakes/ \
  http://localhost:8000/field-pack/fuji-hakone-izu/ \
  http://localhost:8000/field-pack/kruger/ \
  http://localhost:8000/field-pack/photos/np-hero-banff.jpg \
  http://localhost:8000/field-pack/yellowstone/ \
  http://localhost:8000/field-pack/dallas-zoo/
```

### Parks polish pass (pre-release, 2026-08-09)
- Continent: VI→NA, AS→Oceania; `_venue_continent` prefers country/territory codes.
- Header tagline unified: "Zoo, aquarium, museum & park days". Landing H1 includes parks.
- Map count: live JS only (no hardcoded 74).
- Top-10 depth packs with unique cores + `verify` fields; lint `scripts/lint_item_uniqueness.py`.
- Maps `/field-pack/media/maps/{slug}.jpg`; stop photos Commons; print slice title + park safety footer.
- Analytics `mission_printed`: venue_type, venue_slug, age_band, time_length, style.
- Summary: `scripts/data/np-polish-pass-summary.md`.

### Park photos = real only (in progress)
- Policy: no AI park heroes/cards. Tools: `scripts/audit_park_photos.py`, `scripts/fetch_park_photo.py`, ledger `scripts/data/park_photo_ledger.json`.
- Done: all shared `np-*` templates → Wikimedia real photos; top-10 heroes real; depth-pass cards recredited when using shared files.
- All **78 park heroes** now real Wikimedia/Commons photos (batch + quality pass). Shared np-* templates real. Ledger: scripts/data/park_photo_ledger.json.

### NPS official maps (2026-08-10)
- **63/63 US parks** have local official/NPS-sourced maps at `media/maps/{slug}.jpg` + `media.print_map` + `FP_PRINT_MAPS`.
- Fetcher: `scripts/fetch_nps_park_maps.py` (nps.gov unigrid/PDF/map images; fallbacks NPMaps/Commons).
- Print: SEO mission + print-kit + **app treasure sheet** show map photo when available; doodle only as fallback.
- Attribution: `Map: National Park Service (public domain)` (or via NPMaps/Commons where noted).
