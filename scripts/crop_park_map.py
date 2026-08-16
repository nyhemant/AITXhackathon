#!/usr/bin/env python3
"""
Smart-crop NPS brochure/unigrid maps for Field Trip Kit print/web previews.

Goals:
  - Prefer the cartographic PAGE of multi-page PDFs (not the photo/info side)
  - Trim white/near-white margins and solid text footer strips
  - Optionally trim low-value header inset bars when the main map dominates
  - Keep full PDF linked via visitor_map_page for deep dives

Usage:
  scripts/.venv-maps/bin/python scripts/crop_park_map.py --pdf /tmp/x.pdf --out maps/yellowstone.jpg
  scripts/.venv-maps/bin/python scripts/crop_park_map.py --image maps/foo.jpg --out maps/foo.jpg
  scripts/.venv-maps/bin/python scripts/crop_park_map.py --all-us   # reprocess from ledger sources
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

try:
    from PIL import Image
except ImportError as e:
    raise SystemExit("Need Pillow: scripts/.venv-maps/bin/pip install pillow") from e

ROOT = Path(__file__).resolve().parents[1]
MAP_DIR = ROOT / "static/field-pack/media/maps"
VENUE_DIR = ROOT / "static/field-pack/data/venues"
LEDGER = ROOT / "scripts/data/nps_park_maps_ledger.json"


def render_pdf_pages(pdf: Path, out_dir: Path, dpi: int = 150) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = out_dir / "page"
    r = subprocess.run(
        ["pdftoppm", "-jpeg", "-jpegopt", "quality=90", "-r", str(dpi), str(pdf), str(prefix)],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(r.stderr[:300])
    pages = sorted(out_dir.glob("page*.jpg"))
    if not pages:
        raise RuntimeError("pdftoppm produced no pages")
    return pages


def _band_stats(im: Image.Image, axis: str, bands: int = 24):
    """Yield (index, white_frac, sat_frac, mean_luma) along axis."""
    im = im.convert("RGB")
    # downsample
    w, h = im.size
    scale = max(1, max(w, h) // 600)
    small = im.resize((max(1, w // scale), max(1, h // scale)), Image.Resampling.BILINEAR)
    px = small.load()
    W, H = small.size
    out = []
    if axis == "h":
        for bi in range(bands):
            y0 = int(H * bi / bands)
            y1 = max(y0 + 1, int(H * (bi + 1) / bands))
            n = white = sat = luma = 0
            for y in range(y0, y1):
                for x in range(W):
                    r, g, b = px[x, y]
                    n += 1
                    luma += (r + g + b)
                    if r > 235 and g > 235 and b > 235:
                        white += 1
                    if max(r, g, b) - min(r, g, b) > 28:
                        sat += 1
            out.append((bi, white / n, sat / n, luma / (n * 3)))
    else:
        for bi in range(bands):
            x0 = int(W * bi / bands)
            x1 = max(x0 + 1, int(W * (bi + 1) / bands))
            n = white = sat = luma = 0
            for y in range(H):
                for x in range(x0, x1):
                    r, g, b = px[x, y]
                    n += 1
                    luma += r + g + b
                    if r > 235 and g > 235 and b > 235:
                        white += 1
                    if max(r, g, b) - min(r, g, b) > 28:
                        sat += 1
            out.append((bi, white / n, sat / n, luma / (n * 3)))
    return out


def map_score(path: Path) -> float:
    """Higher = more cartographic / less brochure-info photo collage.

    NPS unigrids are usually 2 pages: one photo/story side, one map side.
    Maps have many thin lines (roads/contours), muted terrain colors, and
    fewer large photographic blocks than the info side.
    """
    im = Image.open(path).convert("RGB")
    w, h = im.size
    scale = max(1, max(w, h) // 420)
    s = im.resize((max(1, w // scale), max(1, h // scale)), Image.Resampling.BILINEAR)
    px = s.load()
    W, H = s.size
    n = white = sat = 0
    buckets = set()
    # simple edge energy (horizontal + vertical diffs)
    edge = 0
    edge_n = 0
    # photo-block detector: high local contrast tiles
    tile = 12
    photo_tiles = 0
    tiles = 0
    for ty in range(0, H - tile, tile):
        for tx in range(0, W - tile, tile):
            tiles += 1
            vals = []
            for y in range(ty, ty + tile):
                for x in range(tx, tx + tile):
                    r, g, b = px[x, y]
                    vals.append((r + g + b) / 3)
            mn, mx = min(vals), max(vals)
            # big bright-dark swings => photo
            if mx - mn > 90 and (sum(vals) / len(vals)) > 70:
                photo_tiles += 1
    for y in range(H):
        for x in range(W):
            r, g, b = px[x, y]
            n += 1
            if r > 235 and g > 235 and b > 235:
                white += 1
            if max(r, g, b) - min(r, g, b) > 28:
                sat += 1
            buckets.add((r // 40, g // 40, b // 40))
            if x + 1 < W:
                r2, g2, b2 = px[x + 1, y]
                edge += abs(r - r2) + abs(g - g2) + abs(b - b2)
                edge_n += 1
            if y + 1 < H:
                r2, g2, b2 = px[x, y + 1]
                edge += abs(r - r2) + abs(g - g2) + abs(b - b2)
                edge_n += 1
    white_f = white / max(1, n)
    sat_f = sat / max(1, n)
    diversity = len(buckets) / 400.0
    edge_f = (edge / max(1, edge_n)) / 255.0  # 0..~3 scaled
    photo_f = photo_tiles / max(1, tiles)
    # Maps: high edge (lines), decent diversity, moderate sat, low photo blocks
    # Info sides: high photo blocks, high sat from photos, more pure layout white
    score = (
        edge_f * 4.5
        + diversity * 1.2
        + min(sat_f, 0.35) * 0.8  # some color good; extreme sat = photos
        - white_f * 1.8
        - photo_f * 5.0
    )
    return score


def pick_best_page(pages: list[Path]) -> Path:
    if len(pages) == 1:
        return pages[0]
    scored = [(map_score(p), p) for p in pages]
    scored.sort(key=lambda x: -x[0])
    return scored[0][1]


def find_content_box(im: Image.Image) -> tuple[int, int, int, int]:
    """
    Return crop box (left, upper, right, lower) that:
      - trims near-white margins
      - trims solid light footer/header strips that are mostly text/white
    """
    w, h = im.size
    bands_h = _band_stats(im, "h", 32)
    bands_v = _band_stats(im, "v", 32)

    def trim_edges(bands, size, is_white_strip):
        # find first/last non-strip band from each edge
        lo = 0
        hi = len(bands) - 1
        # require leaving at least 55% of content
        max_trim = int(len(bands) * 0.28)
        trimmed = 0
        while lo < hi and trimmed < max_trim and is_white_strip(bands[lo]):
            lo += 1
            trimmed += 1
        trimmed = 0
        while hi > lo and trimmed < max_trim and is_white_strip(bands[hi]):
            hi -= 1
            trimmed += 1
        # convert band index to pixel
        y0 = int(size * lo / len(bands))
        y1 = int(size * (hi + 1) / len(bands))
        return y0, y1

    def is_strip(b):
        # white-heavy OR very low saturation with high luma (text panels)
        _i, white, sat, luma = b
        if white >= 0.45:
            return True
        if white >= 0.28 and sat < 0.08:
            return True
        if luma > 210 and sat < 0.06:
            return True
        return False

    top, bottom = trim_edges(bands_h, h, is_strip)
    left, right = trim_edges(bands_v, w, is_strip)

    # Unigrid map side: title + ROW OF INSET area maps, then a solid black
    # horizontal rule, then the main park map. Prefer a *full-width* near-black
    # bar in the upper portion (not just the title bar at y≈0).
    im_rgb = im if im.mode == "RGB" else im.convert("RGB")
    # Downsample for speed; keep full height resolution for y precision
    sw = max(1, w // 6)
    sample = im_rgb.resize((sw, h), Image.Resampling.BILINEAR)
    sp = sample.load()
    row_luma = []
    row_dark = []  # fraction of near-black pixels
    for y in range(h):
        ssum = 0
        dark = 0
        for x in range(sw):
            r, g, b = sp[x, y]
            ssum += (r + g + b) / 3
            if r < 50 and g < 50 and b < 50:
                dark += 1
        row_luma.append(ssum / sw)
        row_dark.append(dark / sw)

    def rl(y, rad=2):
        y0 = max(0, y - rad)
        y1 = min(h, y + rad + 1)
        return sum(row_luma[y0:y1]) / (y1 - y0)

    def rd(y, rad=1):
        y0 = max(0, y - rad)
        y1 = min(h, y + rad + 1)
        return sum(row_dark[y0:y1]) / (y1 - y0)

    # Search top 45% for solid black rules (Yellowstone insets end ~16%)
    search_lo = int(h * 0.04)
    search_hi = int(h * 0.48)
    best_y = None
    best_score = -1e9
    for y in range(search_lo, search_hi):
        dark_f = rd(y)
        v = rl(y)
        # Prefer nearly solid black bars spanning the page
        if dark_f < 0.35 and v > 55:
            continue
        a0 = max(0, y - int(h * 0.08))
        a1 = max(0, y - int(h * 0.01))
        b0 = min(h, y + int(h * 0.01))
        b1 = min(h, y + int(h * 0.08))
        if a1 <= a0 or b1 <= b0:
            continue
        above = sum(row_luma[a0:a1]) / (a1 - a0)
        below = sum(row_luma[b0:b1]) / (b1 - b0)
        # Need lighter content both sides (insets above, map below)
        if above < v + 20 or below < v + 20:
            continue
        # Keep enough main-map remaining below the cut
        if (h - y) < h * 0.40:
            continue
        # Score: solid black + contrast; prefer lower separators (after insets)
        sc = dark_f * 120 + (above - v) + (below - v) + (y / h) * 50
        # Bonus if bar is very solid (classic unigrid rule)
        if dark_f > 0.7:
            sc += 40
        if sc > best_score:
            best_score = sc
            best_y = y
    if best_y is not None and best_score > 60:
        top = max(top, best_y + 6)

    # Trim dense text/legend footers: bottom bands that are mostly white + low edge
    # (keep a little legend/scale — don't cut into the park body)
    footer_hi = int(h * 0.97)
    footer_lo = max(top + int(h * 0.45), int(h * 0.78))
    # Walk up from bottom while bands stay white-heavy
    fb = _band_stats(im, "h", 40)
    cut_b = len(fb) - 1
    trimmed = 0
    max_footer = int(len(fb) * 0.18)
    while cut_b > 0 and trimmed < max_footer:
        _i, white, sat, luma = fb[cut_b]
        # footer text panels: high white, low-mid sat
        if white >= 0.40 or (luma > 200 and sat < 0.12):
            cut_b -= 1
            trimmed += 1
            continue
        break
    footer_y = int(h * (cut_b + 1) / len(fb))
    if footer_y > top + int(h * 0.40):
        bottom = min(bottom, footer_y)

    # ensure minimum crop size
    if right - left < w * 0.5:
        left, right = 0, w
    if bottom - top < h * 0.35:
        # Don't collapse — keep from top cut if we have a good separator
        if best_y is not None and best_score > 60:
            bottom = h
        else:
            top, bottom = 0, h

    # pad 1% back so we don't clip labels
    pad_x = int(w * 0.008)
    pad_y = int(h * 0.006)
    left = max(0, left - pad_x)
    top = max(0, top - pad_y)
    right = min(w, right + pad_x)
    bottom = min(h, bottom + pad_y)
    return left, top, right, bottom


def process_image(src: Path, dest: Path, quality: int = 88) -> dict:
    """Crop non-map chrome. Refuse destructive crops (tiny / over-trimmed)."""
    im = Image.open(src).convert("RGB")
    box = find_content_box(im)
    cropped = im.crop(box)
    w0, h0 = im.size
    w1, h1 = cropped.size
    area_ratio = (w1 * h1) / max(1, w0 * h0)

    # Safety: keep original when crop is too aggressive or collapses a usable map.
    # Unigrid inset-strip crops usually keep ~0.55–0.85; <0.40 often means
    # white-margin maps got shredded or the source was already a thumbnail.
    reject = False
    reason = ""
    aspect1 = w1 / max(1, h1)
    aspect0 = w0 / max(1, h0)
    if area_ratio < 0.40 and min(w1, h1) < 0.55 * min(w0, h0):
        reject = True
        reason = "area_and_min_edge"
    elif area_ratio < 0.28:
        reject = True
        reason = "area_floor"
    elif min(w1, h1) < 280 and min(w0, h0) >= 400:
        reject = True
        reason = "min_edge_floor"
    elif (w1 * h1) < 80_000 and (w0 * h0) >= 200_000:
        reject = True
        reason = "pixel_floor"
    # Side-trim that turns a normal map into a skinny ribbon (bad for print/web)
    elif area_ratio < 0.9 and (
        (aspect1 < 0.32 and aspect0 >= 0.38) or (aspect1 > 3.2 and aspect0 <= 2.8)
    ):
        reject = True
        reason = "extreme_aspect"

    if reject:
        cropped = im
        box = (0, 0, w0, h0)
        w1, h1 = w0, h0
        area_ratio = 1.0

    dest.parent.mkdir(parents=True, exist_ok=True)
    # Cap long edge for web (~2200) while staying sharp in print frame
    max_edge = 2200
    if max(cropped.size) > max_edge:
        cropped.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)
    cropped.save(dest, "JPEG", quality=quality, optimize=True)
    meta = {
        "src": str(src),
        "box": list(box),
        "src_size": [w0, h0],
        "out_size": list(cropped.size),
        "area_kept": round(area_ratio, 3),
        "bytes": dest.stat().st_size,
    }
    if reject:
        meta["crop_rejected"] = reason
    return meta


def process_pdf(pdf: Path, dest: Path, dpi: int = 160) -> dict:
    with tempfile.TemporaryDirectory(prefix="mapcrop-") as td:
        td = Path(td)
        pages = render_pdf_pages(pdf, td, dpi=dpi)
        scores = [(map_score(p), p.name) for p in pages]
        best = pick_best_page(pages)
        meta = process_image(best, dest)
        meta["pages"] = len(pages)
        meta["page_scores"] = scores
        meta["chosen_page"] = best.name
        return meta


def process_pdf_url_or_file(source: str, dest: Path) -> dict:
    import tempfile
    import urllib.request

    if source.startswith("http"):
        req = urllib.request.Request(
            source,
            headers={"User-Agent": "1LessFieldTripKit/1.0 (educational; NPS PD maps)"},
        )
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(data)
            pdf = Path(f.name)
        try:
            return process_pdf(pdf, dest)
        finally:
            pdf.unlink(missing_ok=True)
    return process_pdf(Path(source), dest)


def main():
    import tempfile

    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", default="")
    ap.add_argument("--image", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--all-from-ledger", action="store_true")
    ap.add_argument("--slug", default="")
    args = ap.parse_args()

    if args.pdf and args.out:
        meta = process_pdf_url_or_file(args.pdf, Path(args.out))
        print(json.dumps(meta, indent=2))
        return

    if args.image and args.out:
        meta = process_image(Path(args.image), Path(args.out))
        print(json.dumps(meta, indent=2))
        return

    if args.all_from_ledger or args.slug:
        # Re-fetch from ledger source when PDF; else crop existing JPG
        ledger = {}
        if LEDGER.exists():
            ledger = {r["slug"]: r for r in json.loads(LEDGER.read_text()).get("results") or []}
        slugs = [args.slug] if args.slug else sorted(
            p.stem for p in VENUE_DIR.glob("*.json")
            if json.loads(p.read_text()).get("type") == "national_park"
            and (json.loads(p.read_text()).get("country") or "US").upper() in ("US", "USA", "")
        )
        # unique load
        us = []
        for p in sorted(VENUE_DIR.glob("*.json")):
            v = json.loads(p.read_text())
            if v.get("type") != "national_park":
                continue
            if (v.get("country") or "US").upper() not in ("US", "USA", ""):
                continue
            if args.slug and v["slug"] != args.slug:
                continue
            us.append(v)

        report = []
        for v in us:
            slug = v["slug"]
            dest = MAP_DIR / f"{slug}.jpg"
            src_info = ledger.get(slug) or {}
            source = src_info.get("source") or ""
            kind = src_info.get("kind") or ""
            print(f"[{slug}] …", flush=True)
            try:
                if source and (kind == "pdf" or source.lower().endswith(".pdf")):
                    meta = process_pdf_url_or_file(source, dest)
                elif dest.exists():
                    # crop in place via temp
                    tmp = dest.with_suffix(".precrop.jpg")
                    dest.replace(tmp)
                    meta = process_image(tmp, dest)
                    tmp.unlink(missing_ok=True)
                else:
                    print("  skip no source/file")
                    continue
                meta["slug"] = slug
                meta["source"] = source
                report.append(meta)
                print(
                    f"  ok page={meta.get('chosen_page')} kept={meta.get('area_kept')} "
                    f"{meta.get('src_size')}→{meta.get('out_size')} {meta.get('bytes')}b"
                )
            except Exception as e:
                print(f"  FAIL {e}")
                report.append({"slug": slug, "error": str(e)[:200]})

        outp = ROOT / "scripts/data/nps_map_crop_report.json"
        outp.write_text(json.dumps(report, indent=2) + "\n")
        print("report", outp)
        return

    ap.error("Need --pdf/--image/--out or --all-from-ledger")


if __name__ == "__main__":
    main()
