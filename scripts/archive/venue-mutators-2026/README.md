# Archived venue mutators (2026)

Spent one-shot writers. Their kits already live in committed venue JSON / catalogs / VFT HTML.

**DO NOT RE-RUN.** Tests lock that committed JSON/HTML, not these scripts. Restoring a writer to `scripts/` would rewrite live venue JSON.

`write_wave3b_venues.py` and `write_wave4_venues.py` import `write_wave3a_venues.py`, so this folder is one bundle.

`apply_map_images.js` is paired with `data/visitor_map_images.json`.

`apply_presence_audits.py` already landed its audits in venue JSON. It is not idempotent (appends `research_notes` on every run).
