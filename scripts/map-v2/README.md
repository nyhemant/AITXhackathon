# Home map v2 build scripts (2026-11-12)

- `build_map_v2.mjs`: projects Natural Earth (public domain) land, lakes, state lines and world-atlas 2.0.2 countries into the static plates in `static/start/map-v2/` (`a-usa-v1.svg`, `a-world-v1.svg`) and prints the pin/label HTML fragments. Needs `d3-geo`, `d3-geo-projection`, `topojson-client`, `world-atlas`, `mapshaper` from npm and the Natural Earth GeoJSON files listed at the top of the script.
- `inject.py`: swaps those fragments into `static/start/index.html` and joins `home-map-v2.css` + `map-v2-a-v1.css` into `home-map-v2-a.css`.
- `art.py`: crops the Grok Imagine decoration and sticker sheets into the versioned WebP files.

Paths at the top of each script point at the build box; edit them before re-running. New outputs need a new `-vN` filename or a `?v=` bump.
