# National Parks polish pass — summary

## (a) Stops flagged `todo` (need human verification)

| Park | Stop |
|------|------|
| yellowstone | Old Faithful Inn lobby (`yell_ofi_lobby`) |
| zion | Zion Lodge lawn (`zion_lodge_lawn`) |
| zion | Cottonwood shade (`zion_cottonwood`) |
| yosemite | Valley pines (`yose_pines`) |
| grand-canyon | Village green space (`grca_village_green`) |
| great-smoky-mountains | Fighting Creek nature trail stretch (`grsm_fighting_creek`) |
| great-smoky-mountains | Open valley edge (`grsm_meadow_edge`) |
| rocky-mountain | Lodgepole pines (`romo_pines`) |
| acadia | Coastal spruce forest (`acad_spruce`) |
| glacier | Colored lake pebbles (`glac_pebbles`) |
| arches | Desert flats between fins (`arch_flats`) |
| olympic | Nurse log (`olym_nurse_log`) |
| olympic | Rainforest clearing (`olym_clearing`) |

**Count:** 13

## (b) Continent audit reclassifications

| Venue | Before | After |
|-------|--------|-------|
| Virgin Islands NP | Asia (fallback) | **North America** (US territory `VI`) |
| American Samoa NP | Asia (fallback) | **Oceania** (US territory `AS` in South Pacific) |

Derivation fix in `scripts/generate_bdo_seo.py` `_venue_continent()`:
- Prefer explicit `country` codes
- US states + PR/VI/GU/MP → North America
- AS → Oceania (before broad US→NA)
- Canadian provinces, lat/lon fallbacks for USVI/AS
- Expanded country name map (Croatia, Virgin Islands, etc.)

Other parks (Hawaii HI, Banff CA, Fuji JP, Kruger ZA, etc.) land as intended after the fix.

## Deliverables checklist

- [x] T1 bugs: continent, header tagline, H1, counts
- [x] T2 uniqueness lint (`scripts/lint_item_uniqueness.py` → `scripts/data/item-uniqueness-report.md`)
- [x] T3 top-10 depth packs (unique core stops + verify fields)
- [x] T4 maps under `/field-pack/media/maps/` + stop photos (Commons downloads)
- [x] T5 print slice title + park safety footer
- [x] T6 analytics props on `mission_printed`
- [x] SEO regenerated; Dallas Zoo lead untouched
