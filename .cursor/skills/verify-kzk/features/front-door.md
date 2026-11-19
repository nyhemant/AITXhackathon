# Front door (/start/)

## Sub-features
- `/` answers 301 to `/start/`.
- Approved H1 "Printable scavenger hunts for your next zoo, aquarium or museum trip" (frozen through 2026-11-24).
- Header wordmark "Arya’s Wildlife Project" with a small KIDZOOKIT line (`.start-wordmark`); must stay.
- Pin → printed hunt demo (`#hx-demo`), its sheet links to `/field-pack/perot-museum/#printable-hunt` (`a.hxd-sheet[data-kz-cta=home-demo]`).
- Phone: "Print a scavenger hunt" button above the fold. Desktop: "Tap a pin to print" hint with the map.

## How to get to it (user POV)
Type kidzookit.com, or scan the carpool sheet's QR code (it opens /start/ with printable QR tracking tags).

## Driving it with verify.py
`--only j1`. Checks one H1 with the approved text, the wordmark, the fold, the demo href, no "free"/"no-cost",
contact is only `mailto:ask@kidzookit.com`, every link stays on kidzookit.com, then taps the demo sheet and expects
the Perot hunt section visible. Hygiene: no JS errors, no off-site requests, no sideways scroll.

## Gotchas
- Cloudflare may inject its beacon on tracked pages; the opt-out cookie and `kz-verify` UA stop that. Beacon errors are WARN.
- The demo plays for about 2.2 s; reduced motion shows the final frame. The script waits for network idle plus 600 ms.
