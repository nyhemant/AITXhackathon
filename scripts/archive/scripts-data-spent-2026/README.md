# Archived scripts/data dumps (2026)

Spent one-shot research JSON and reports. No live callers. Kits, maps, and photos they describe already live in committed venue JSON / media.

**DO NOT treat these as tool inputs.** Live fetch / crop / photo tools still read:

- `scripts/data/nps_park_maps_ledger.json`
- `scripts/data/park_photo_ledger.json`
- `scripts/data/ftk_imagine_prompt.md`

`visitor_map_pages.json` is the leftover pair of archived `apply_map_images.js` (`scripts/archive/venue-mutators-2026/`). `item-uniqueness-report.md` is a leftover dual-write snapshot; live lint writes `docs/item-uniqueness-report.md` only. `park_photo_audit_report.md` is a leftover dump; live photo audit writes `docs/park-photo-audit-report.md` (ledger stays `scripts/data/park_photo_ledger.json`).

A later `--all-from-ledger` crop may recreate `scripts/data/nps_map_crop_report.json`. That is a new run, not these snapshots.
