# Performance notes

## 2026-10-22 — photo and map right-sizing (`scripts/resize_photos.py`)
- 384 images (222 in `static/field-pack/photos`, 162 in `static/field-pack/media/maps`) went from 262 MB to ~94 MB. URLs, filenames and aspect ratios are unchanged.
- Caps: photos 960px wide, `np-hero-*` 1600px, maps 1400px (4:4:4 chroma so map text stays sharp), JPEG q80 progressive.
- 30 photographic PNGs saved under `.jpg` names were written as real JPEGs. Fully opaque RGBA was treated as RGB. Files with real transparency or CMYK are skipped (one CMYK map: `audubon-aquarium.jpg`).
- `image-resize-manifest.csv` lists each file's original and new size, dimensions and sha256. `git revert` of the PR restores the original blobs, and the hashes confirm it.
- `tests/test_image_weight.py` keeps future uploads under the caps.
- Cloudflare caches images for up to 24h (no purge access), so the old, bigger files can keep showing for up to a day after this ships or after a revert.
