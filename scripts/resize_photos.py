#!/usr/bin/env python3
"""Right-size KidZooKit photos and park maps in place (same filenames).

2026-10-22 mobile speed pass. Pages show photos at 102-326 CSS px and maps
at ~322 px inline (tap to enlarge / print), but files were up to 3.4 MB and
1920-2200 px wide. This keeps every URL and aspect ratio and only lowers
pixel width and JPEG quality:

  static/field-pack/photos/*.jpg      width <= 960  (np-hero-* <= 1600), q80
  static/field-pack/media/maps/*.jpg  width <= 1400, q80, 4:4:4 chroma (text)

Rules
- Files with real transparency (alpha < 255 anywhere) or CMYK are skipped.
- Photographic PNG data saved under a .jpg name is written as real JPEG.
- A file is only rewritten when the result is at least 10% smaller.
- Writes a manifest CSV (path, original dims/bytes/sha256, new dims/bytes/
  sha256, action) so a rollback is deterministic: `git revert` restores the
  original blobs, and the manifest hashes prove which file is which.

Usage: python3 scripts/resize_photos.py [--dry-run] [--manifest PATH]
Needs Pillow. Idempotent: a second run leaves already-sized files alone.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PHOTOS = ROOT / "static" / "field-pack" / "photos"
MAPS = ROOT / "static" / "field-pack" / "media" / "maps"

PHOTO_MAX_W = 960
HERO_MAX_W = 1600
MAP_MAX_W = 1400
QUALITY = 80
MIN_SAVING = 0.10  # rewrite only if >=10% smaller


def max_width(path: Path) -> int:
    if path.parent == MAPS:
        return MAP_MAX_W
    if path.name.startswith("np-hero-"):
        return HERO_MAX_W
    return PHOTO_MAX_W


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def process(path: Path, dry: bool) -> dict:
    raw = path.read_bytes()
    im = Image.open(io.BytesIO(raw))
    im.load()
    row = {
        "path": str(path.relative_to(ROOT)),
        "orig_format": im.format,
        "orig_mode": im.mode,
        "orig_w": im.size[0],
        "orig_h": im.size[1],
        "orig_bytes": len(raw),
        "orig_sha256": sha(raw),
    }
    keep = dict(new_w=im.size[0], new_h=im.size[1], new_bytes=len(raw), new_sha256=row["orig_sha256"])
    if im.mode == "CMYK":
        return {**row, **keep, "action": "skip-cmyk"}
    if im.mode in ("RGBA", "LA", "PA") or (im.mode == "P" and "transparency" in im.info):
        alpha = im.convert("RGBA").getchannel("A")
        if alpha.getextrema()[0] < 255:
            return {**row, **keep, "action": "skip-alpha"}
        im = im.convert("RGB")
    elif im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    cap = max_width(path)
    w, h = im.size
    if w > cap:
        nh = round(h * cap / w)
        im = im.resize((cap, nh), Image.LANCZOS)
    opts = dict(format="JPEG", quality=QUALITY, optimize=True, progressive=True)
    if path.parent == MAPS:
        opts["subsampling"] = 0
    icc = Image.open(io.BytesIO(raw)).info.get("icc_profile")
    if icc:
        opts["icc_profile"] = icc
    buf = io.BytesIO()
    im.save(buf, **opts)
    out = buf.getvalue()
    if w <= cap and row["orig_format"] == "JPEG" and len(out) > len(raw) * (1 - MIN_SAVING):
        return {**row, **keep, "action": "keep-small"}
    # verify it decodes and kept the aspect ratio
    chk = Image.open(io.BytesIO(out))
    chk.load()
    if chk.size[0] != im.size[0] or abs(chk.size[1] - h * chk.size[0] / w) > 1:
        raise SystemExit(f"aspect drift on {path}")
    if not dry:
        path.write_bytes(out)
    return {**row, "new_w": chk.size[0], "new_h": chk.size[1], "new_bytes": len(out),
            "new_sha256": sha(out), "action": "resized" if w > cap else "reencoded"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--manifest", default=str(ROOT / "docs" / "perf" / "image-resize-manifest.csv"))
    a = ap.parse_args()
    rows = [process(p, a.dry_run) for d in (PHOTOS, MAPS) for p in sorted(d.glob("*.jpg"))]
    cols = ["path", "action", "orig_format", "orig_mode", "orig_w", "orig_h", "orig_bytes", "orig_sha256",
            "new_w", "new_h", "new_bytes", "new_sha256"]
    with open(a.manifest, "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        wr.writerows(rows)
    before = sum(r["orig_bytes"] for r in rows)
    after = sum(r["new_bytes"] for r in rows)
    acts: dict[str, int] = {}
    for r in rows:
        acts[r["action"]] = acts.get(r["action"], 0) + 1
    print(f"{len(rows)} files, {before/1e6:.1f} MB -> {after/1e6:.1f} MB; {acts}")


if __name__ == "__main__":
    main()
