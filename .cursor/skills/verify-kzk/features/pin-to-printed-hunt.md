# Map pin to the printed hunt

## Sub-features
- 16 place pins on the /start/ map (`[data-home-pin]`); 2-place pins (DC, Chicago) list each place.
- Pin card `#home-pin-card` with "Print the scavenger hunt" and "See the full page"; Close button `#home-pin-close`, Escape closes on desktop.
- Animals/Places toggle (`#home-map-animals`, `#home-map-places`) closes an open place card.
- Venue page `#printable-hunt` section: stop list, "Build and print the hunt" (`button.kz-scav-print`) opens the drawer `#mission-overlay` with a live sheet `#mission-sheet`, age chips `#mission-who-seg [data-age]`, Print `#mission-print-btn`.

## How to get to it (user POV)
On /start/, drag the map, tap a place label, tap "Print the scavenger hunt", tap "Build and print the hunt", tap Print.

## Driving it with verify.py
`--only j2`. Taps the Perot label (`[data-home-pin="perot-museum"] .kzm-tag`), checks the card names Perot, closes and
reopens it, checks the DC pin lists 2 print links, follows the print link, expects the hunt section in the top half of
the screen with at least 8 stops, opens the drawer, expects the sheet to name Perot, taps Print and expects exactly one
`window.print` call (`html[data-kzv-printed="1"]`), then Escape closes the drawer.

## Gotchas
- Never tap the pin button centre: "tag only" pins sit under neighbours. Tap the visible `.kzm-tag`.
- A quick double tap on Print calls `window.print` twice (finding K4, 2026-11-18). The fix waits until the 10 frozen scav pages are released, because they load the same `mission-ui.js?v=21-scav3`.
- The 10 frozen scav pages (bronx-zoo, austin-zoo, national-zoo, lincoln-park-zoo, shedd-aquarium, seattle-aquarium, st-louis-zoo, fort-worth-zoo, san-antonio-zoo, dallas-zoo) may be read but never changed.
