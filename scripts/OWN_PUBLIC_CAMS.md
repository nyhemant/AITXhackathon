# own_public_cams

Per-place bool on `static/field-pack/data/venues/{slug}.json`.

**Rule:** `true` only when a Virtual Field Trip cam URL hostname matches that
venue’s `official_url` host (or an NPS webcam path maps to that park slug).
Inspected from `static/field-pack/data/virtual-venues/*.json` `habitats[].cam.url`.

Currently true for:

- houston-zoo (`houstonzoo.org`)
- san-diego-zoo (`zoo.sandiegozoo.org`)
- san-diego-safari-park (`sdzsafaripark.org`)
- national-zoo (`nationalzoo.si.edu`)
- monterey-bay-aquarium (`montereybayaquarium.org`)
- NPS parks with sourced nps.gov webcams: acadia, glacier, grand-canyon,
  great-smoky-mountains, olympic, rocky-mountain, yellowstone, yosemite

Everyone else stays `false`. Place pages show a third-party cam disclaimer in
`#at-home` only when `own_public_cams` is false **and** the talk/cards section
lists at least one live `cam_url`.
