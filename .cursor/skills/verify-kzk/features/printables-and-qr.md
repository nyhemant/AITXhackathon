# Printables, PDFs and printed QR codes

## Sub-features
- /printables/ hub and sheet pages (scavenger hunt, animal bingo, zoo day journal), 14 PDFs (7 Letter + 7 A4) plus the Science Bee practice sheet.
- Printed QR codes on 7 sheets point at fixed URLs that must answer 200 forever (a 301 only if a page moves).

## How to get to it (user POV)
/start/ "Play & learn printables", or scan the QR code on a printed sheet.

## Driving it with verify.py
`--only j6`. Collects every `a[href$=".pdf"]` on /printables/, fetches each (200, `application/pdf`, starts `%PDF`),
fetches the 7 QR destinations without following redirects (200 and `qr-welcome.js` present), and checks `/` is a 301
to `/start/`.

## Gotchas
- QR destinations are pinned in `QR_DESTS` in `scripts/verify.py` (source: `/workspace/kidzookit-loop/live29/printables_inventory.json`).
- New PDFs and images use versioned filenames (`-v1`, `-v2`); never overwrite a printed file name.
