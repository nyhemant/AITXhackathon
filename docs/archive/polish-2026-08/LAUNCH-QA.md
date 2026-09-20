# Field Trip Kit — Launch QA (polish program close)

**Date:** 2026-08-12  
**Program:** T1–T11 sequential polish (PROMPT pack)  
**Brief:** `docs/AGENT-BRIEF.md` · Queue: `docs/POLISH-TASKS.md`

## Task completion summary

| ID | Status | Note |
|----|--------|------|
| T1 | done | Continents OK (VI→NA, AS→Oceania); tagline via `HEADER_TAGLINE`; counts build-time (trust `218`, hubs `len()`, compact catalog counts). No reclassifications needed this pass. |
| T2 | done | `js/fp-analytics.js` → `FPTrack` / `FPTrackVenuePageView`; `mission_printed` props retained; venue `venue_page_viewed`; wired in mission-ui, print-kit, landing-hook, generated pages. |
| T3 | done | `/field-pack/cards/` — 109 Q&A cards (Wildlife / Sea life / Attractions), nav + sitemap, indexable, `cards_hub_visited` + `card_opened`. |
| T4 | done | Paired mission+lion card previews; cards secondary CTA only; B/D/A strip; extras near FAQ; hero events. Search remains primary CTA. |
| T5 | done | Compact catalog: 12 featured tiles + pills; 4 place hubs; 12 popular chips; map tabs decoupled; reachability 218/218. |
| T6 | done | Lint warn-only default → `docs/item-uniqueness-report.md`. Headline: desc 36 · generic-core 68 · pairs 4511 · **top-10 clean YES**. |
| T7 | done | Batch 1 parks already depth-sourced; slice labels present; residual `todo` verifies listed below. |
| T8 | done | Batch 2 same; residual `todo` verifies listed below. |
| T9 | done | Maps on disk for all 10 + `docs/nps-assets-manifest.md`. Gap: stop-specific PD photo batch import deferred. |
| T10 | done | Slice in mission title + park safety footer already in engine/print; structure verified on yellowstone page. Full iOS Safari print matrix deferred to device QA. |
| T11 | done | `--enforce-top10` passes; reachability 0 missing; dinner untouched; smoke script `scripts/smoke_field_pack_polish.sh`. |

## Open `verify.todo` items (human review)

| Park | Item id | Label |
|------|---------|-------|
| great-smoky-mountains | grsm_fighting_creek | Fighting Creek nature trail stretch |
| great-smoky-mountains | grsm_meadow_edge | Open valley edge |
| zion | zion_lodge_lawn | Zion Lodge lawn |
| zion | zion_cottonwood | Cottonwood shade |
| yellowstone | yell_ofi_lobby | Old Faithful Inn lobby |
| grand-canyon | grca_village_green | Village green space |
| yosemite | yose_pines | Valley pines |
| rocky-mountain | romo_pines | Lodgepole pines |
| acadia | acad_spruce | Coastal spruce forest |
| glacier | glac_pebbles | Colored lake pebbles |
| arches | arch_flats | Desert flats between fins |
| olympic | olymp_nurse_log → olymp_nurse_log | Nurse log |
| olympic | olymp_clearing | Rainforest clearing |

(Exact ids: `olym_nurse_log`, `olym_clearing`.)

## Lint status

- Default build step: **warn-only** (`python3 scripts/lint_item_uniqueness.py`)
- Launch gate: **`python3 scripts/lint_item_uniqueness.py --enforce-top10`** → OK (top-10 clean)
- Report: `docs/item-uniqueness-report.md`
- Long-tail description reuse and museum template sharing remain warn-only

## Reachability

- `docs/venue-reachability-report.md`: **218/218** venues ≤2 static clicks from `/field-pack/`

## Popular venues seeded (T5 — review)

dallas-zoo, san-diego-zoo, bronx-zoo, national-zoo, georgia-aquarium, monterey-bay-aquarium, amnh, childrens-museum-perot, yellowstone, grand-canyon, yosemite, zion

## Featured cards seeded (T5)

african-lion, reticulated-giraffe, giant-panda, african-elephant, shark, octopus, jellyfish, clownfish, sea-turtle, sci-rocket, sci-dinosaur, cm-makery

## Lighthouse

Not re-baselined in this pass (no CI Lighthouse run). Recommend capturing landing + dallas-zoo + yellowstone on next deploy.

Local HTTP smoke (200): `/field-pack/`, `/cards/`, `/dallas-zoo/`, `/yellowstone/`, `/zoos/`, analytics JS, sample images.

## `/dinner` untouched

No dinner product paths modified in this program (field-pack + docs + scripts only).

## Known gaps deferred post-launch

1. Stop-specific NPS PD photo import for 10 parks (maps already local).
2. Device print matrix: Letter/A4 × iOS Safari × Chrome with attached screenshots.
3. Lighthouse numeric table vs pre-program baseline.
4. Long-tail item uniqueness (zoos/museums template sharing) — warn-only.
5. Cards hub may still include a few park-adjacent catalog entries; core animal/sea/museum cards covered.
6. Before/after hero screenshots at 390/1280 not re-captured this session (prior hero-after assets exist under `photos/`).

## How to regenerate

```bash
python3 scripts/generate_bdo_seo.py
python3 scripts/smoke_field_pack_polish.sh
```
