# 1Less — session handoff

**Last updated:** 2026-08-17 (unique lists + Ready 6 + park polish)  
**Session:** `1less`  
**Pre-rearch restore:** `git checkout snapshot/pre-rearch-2026-08-02`

## Product
- **1Less** brand · **Field Trip Kit** default (`/` → `/field-pack/`) · **Dinner** secondary (`/dinner` via More)
- Kid printables: **mission**. Do not use “Baby’s Day Out” in new user-facing copy.

## Shell
- `static/shell/` — logo **52px** (44px mobile), product name, More menu
- CSS cache: `shell.css?v=6`

## Landing
- First screen: giraffe headline + real Dallas giraffe card + **Open Dallas Zoo** → `/field-pack/dallas-zoo/`
- Map, search, Ready strip, and catalog stay **below the fold** (not a twin first homepage)
- Ready IDs: one list `window.FP_READY_STRIP` in `landing-map.js` (US six + intl London / Singapore / Ueno)
- US six: Dallas Zoo, Children’s Aquarium Dallas, Children’s Museum (Perot), Houston Zoo, San Diego Zoo, National Zoo
- Popular chips go to `/field-pack/{slug}/`
- Cache: `home-first.css?v=2`, `home-first.js?v=1`, `landing.css?v=95`, `landing-map.js?v=84`, `landing-hook.js?v=34`, `catalog.js?v=36`

## Flow (3 levels — current)
1. **Home** `/` → `/field-pack/` — city + venue
2. **Outing** `app.html#/venue/{id}` — item list + print treasure hunt (+ optional customize)
3. **Item** `#/venue/{id}/item/{itemId}` — optional Q&A + print card

## Unique lists — wave 1 (2026-08-17)
Dual-write `catalog.js` + `data/venues/{slug}.json` for **8 packs only** (not all 218):

| Pack | Distinctive featured |
|------|----------------------|
| `dallas-zoo` | Giraffe Ridge / elephant / penguin / hippo / flamingo / cheetah |
| `childrens-aquarium-dallas` | Small-tank list (no DWA clone, no otter) |
| `childrens-museum-perot` | `cm-*` kids floor |
| `dallas-world-aquarium` | Sloth / lemur rainforest — **no** Asian small-clawed otter |
| `perot-museum` | Dinos + sports/energy, not generic `sci-*` deck |
| `houston-zoo` | Apes + red panda / zebra / warthog / ostrich (not Dallas first six) |
| `san-diego-zoo` | Panda / koala-led |
| `national-zoo` | Smithsonian pandas + otter / red panda |

- Hunt lines are venue-specific (not the cloned “taller than a grown-up” block)
- Honesty: Houston has no African elephant / African penguin / Nile hippo / otter; National Zoo has no African elephant / giraffe
- Out of scope: Virtual Zoo films, intl zoo clones, AMNH/Field Museum NHM decks
- Lint: wave-1 pairwise core share ≤50%. Global lint still flags the other ~210 venues
- SEO regen: `python3 scripts/generate_bdo_seo.py` (mission renderer `v` NameError in drawer kicker is fixed)

## Ready strip (2026-08-17)
- Restored after T4b hero removed the HTML
- 6 cards, 2-up on mobile (`max-width: 720px`), emoji+text only
- Static no-JS fallback: `#ready-heading` + `#ready-grid` in `index.html`

## National parks — photos done + polish (2026-08-17)
- **78/78 heroes are real Wikimedia** (not Imagine). Policy: no AI park heroes/cards
- Parks hub `og:image` → `np-hero-yellowstone.jpg`. Zoo/aquarium/museum hubs keep Dallas Zoo sample
- SEO hero alt is **“park day”** (not “illustrated park day”)
- Print maps: `FP_PRINT_MAP_CREDITS` in `print-maps.js`; `print-kit.js` shows `map_attribution` (not hardcoded “Official visitor map”)
- Cache: `print-maps.js?v=5`, `print-kit.js?v=13`, `styles.css?v=35`
- US D/C recrop: Shenandoah + New River Gorge then six C-grades via `crop_park_map.py`. In-place trim helped some C-grades; D-grades were already fully cropped (tall unigrid source). Re-fetch blocked: Python SSL certs + no `pdftoppm`
- Intl OSM (Blue Mountains, Fuji-Hakone-Izu, Killarney, Nikkō): **accepted gaps** — official visitor maps are not freely licensable for hosting. See `MAP_STATUS.md`
- Ledger: `nps_park_maps_ledger.json` rebuilt from disk (78/78 ok). Unique stop/wildlife `source_url`: copied from shared paths + 3 hero landmark matches; 25 unique JPEGs still empty (Commons lookup needs working Python SSL)
- **P2 later:** `np_intl_phase2.json` not started. No new parks this pass

## Smoke
Local: `./scripts/dev-serve.sh` → `http://127.0.0.1:8000/field-pack/`

```bash
curl -sI http://127.0.0.1:8000/ | grep Location
curl -sf -o /dev/null -w "%{http_code}\n" \
  http://127.0.0.1:8000/field-pack/ \
  http://127.0.0.1:8000/field-pack/national-parks/ \
  http://127.0.0.1:8000/field-pack/dallas-zoo/ \
  http://127.0.0.1:8000/field-pack/houston-zoo/ \
  http://127.0.0.1:8000/field-pack/san-diego-zoo/ \
  http://127.0.0.1:8000/field-pack/yellowstone/ \
  http://127.0.0.1:8000/field-pack/photos/np-hero-yellowstone.jpg
```

Landing (~390px): giraffe headline + real card + Open Dallas Zoo; map/search/Ready stay below the fold; Popular chips → `/field-pack/{slug}/`  
App: `#/venue/dallas-zoo` vs Houston vs San Diego featured chips differ; DWA shortlist includes sloth, not CAD otter  
Park: Yellowstone / Banff alt is not “illustrated”; `/field-pack/national-parks/` og:image is a park hero; print sheet shows map credit

## Regen
```bash
python3 scripts/generate_bdo_seo.py
python3 scripts/lint_item_uniqueness.py
python3 scripts/fetch_nps_park_maps.py --ledger-from-disk
scripts/.venv-maps/bin/python scripts/crop_park_map.py --slug shenandoah
```

## Next optional
- Intl parks P2 (new countries / hubs) — not started
- Unique lists for remaining ~210 venues
- Python SSL / `pdftoppm` so D-grade maps can re-fetch NPS PDFs
- Commons `source_url` backfill for 25 unique stop JPEGs
- Email notify for saved cities
