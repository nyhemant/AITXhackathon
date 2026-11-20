# Map pin to the printed hunt

## Sub-features
- 16 place pins on the /start/ map (`[data-home-pin]`); 2-place pins (DC, Chicago) list each place.
- Pin card `#home-pin-card` with "Print the scavenger hunt" and "See the full page"; Close button `#home-pin-close`, Escape closes on desktop.
- Animals/Places toggle (`#home-map-animals`, `#home-map-places`) closes an open place card.
- Venue page `#printable-hunt` section: stop list, "Print the hunt" (`button.kz-scav-print`) prints the default hunt in one tap (round 2, 2026-11-20; same for the sticky `#seo-sticky-print`). "Change" (`button.kz-scav-change`) opens the options drawer `#mission-overlay` with a live sheet `#mission-sheet`, age chips `#mission-who-seg [data-age]`, Print `#mission-print-btn`.
- After a print, the weekly email card `form[data-placement="place_print"]` appears (hidden before; never printed).

## How to get to it (user POV)
On /start/, drag the map, tap a place label, tap "Print the scavenger hunt", tap "Print the hunt". For options: tap "Change", pick, tap Print.

## Driving it with verify.py
`--only j2`. Taps the Perot label (`[data-home-pin="perot-museum"] .kzm-tag`), checks the card names Perot, closes and
reopens it, checks the DC pin lists 2 print links, follows the print link, expects the hunt section in the top half of
the screen with at least 8 stops, taps "Print the hunt" and expects exactly one `window.print` call
(`html[data-kzv-printed="1"]`) with the drawer still closed and the sheet naming Perot, then taps "Change", expects the
drawer, taps Print (one more call), double-taps Print (one more call, K4), then Escape closes the drawer.

## Gotchas
- Never tap the pin button centre: "tag only" pins sit under neighbours. Tap the visible `.kzm-tag`.
- K4 (a quick double tap printing twice) is fixed by `print-guard-v1.js` on every place page (#478, #484).
- The scav freeze ended on 2026-11-20 (Heymant: "The freeze is gone"); the 24 pages are checked against main, not frozen digests.
