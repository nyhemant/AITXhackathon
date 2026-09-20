# NPS public-domain assets manifest (T9)

Local storage under `/field-pack/media/maps/`. No hotlinking at runtime.
NPS-produced maps and photos are public domain; credit: **Map/Photo: National Park Service (public domain)**.

## Depth-pass parks (T7/T8)

| Park slug | Local map | print-maps.js | Hero/stop PD photo status | Source notes |
|-----------|-----------|---------------|---------------------------|--------------|
| great-smoky-mountains | `media/maps/great-smoky-mountains.jpg` | yes | fallback illustrated/generic where no local PD stop photo | nps.gov/grsm |
| zion | `media/maps/zion.jpg` | yes | same | nps.gov/zion |
| yellowstone | `media/maps/yellowstone.jpg` | yes | same | nps.gov/yell |
| grand-canyon | `media/maps/grand-canyon.jpg` | yes | same | nps.gov/grca |
| yosemite | `media/maps/yosemite.jpg` | yes | same | nps.gov/yose |
| rocky-mountain | `media/maps/rocky-mountain.jpg` | yes | same | nps.gov/romo |
| acadia | `media/maps/acadia.jpg` | yes | same | nps.gov/acad |
| glacier | `media/maps/glacier.jpg` | yes | same | nps.gov/glac |
| arches | `media/maps/arches.jpg` | yes | same | nps.gov/arch |
| olympic | `media/maps/olympic.jpg` | yes | same | nps.gov/olym |

## Gap list (post-launch candidates)

- Stop-specific PD hero replacements for top-3 items per park (currently kit uses shared/local illustrated assets where PD stop photos were not batch-imported this pass).
- Cropped slice maps (e.g. Old Faithful Basin only) — full park maps are embedded today.

## Credit line (on-page)

Park SEO pages use the visitor-map component with official-site link + public-domain credit (generator / mission UI).

## Verification

- Assets live under `static/field-pack/media/maps/` (repo-local).
- Registry: `static/field-pack/js/print-maps.js`.
