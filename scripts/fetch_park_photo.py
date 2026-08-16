#!/usr/bin/env python3
"""
Fetch a researched park photo into place and patch catalog.js credit/path.

Usage:
  python3 scripts/fetch_park_photo.py --catalog-id np-boardwalk --commons-file "Boardwalk_in_Everglades.jpg"
  python3 scripts/fetch_park_photo.py --hero yellowstone --commons-file "Old_Faithful_Geyser.jpg"
  python3 scripts/fetch_park_photo.py --catalog-id np-river --url "https://upload.wikimedia.org/..."

License: only use PD/CC images you have verified. Updates park_photo_ledger.json.
"""
from __future__ import annotations
import argparse, json, re, ssl, time, urllib.parse, urllib.request
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
PHOTOS = ROOT / "static/field-pack/photos"
CAT = ROOT / "static/field-pack/js/catalog.js"
LEDGER = ROOT / "scripts/data/park_photo_ledger.json"
UA = {"User-Agent": "1LessFieldTripKit/1.0 (https://1less.app; educational park photos)"}
CTX = ssl.create_default_context()
TODAY = date.today().isoformat()

def commons_thumb(title: str, width: int = 1400) -> tuple[str|None, str]:
    if not title.startswith("File:"):
        title = f"File:{title}"
    api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "titles": title, "prop": "imageinfo",
        "iiprop": "url|extmetadata|size", "iiurlwidth": str(width), "format": "json",
    })
    req = urllib.request.Request(api, headers=UA)
    with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
        data = json.loads(r.read().decode())
    for pg in data.get("query", {}).get("pages", {}).values():
        if "missing" in pg:
            continue
        ii = (pg.get("imageinfo") or [{}])[0]
        url = ii.get("thumburl") or ii.get("url")
        meta = ii.get("extmetadata") or {}
        lic = (meta.get("LicenseShortName") or {}).get("value") or ""
        artist = re.sub(r"<[^>]+>", "", (meta.get("Artist") or {}).get("value") or "")[:80]
        return url, f"{lic} · {artist}".strip(" ·")
    return None, ""

def download(url: str, dest: Path, min_size: int = 40000) -> int:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, context=CTX, timeout=120) as r:
        raw = r.read()
    if len(raw) < min_size:
        raise RuntimeError(f"too small {len(raw)}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
    return len(raw)

def patch_catalog(catalog_id: str, photo_rel: str, credit: str) -> None:
    t = CAT.read_text(encoding="utf-8")
    # find object "catalog_id": {
    i = t.find(f'"{catalog_id}":')
    if i < 0:
        raise SystemExit(f"catalog id not found: {catalog_id}")
    j = t.find("{", i)
    depth = 0
    k = j
    while k < len(t):
        if t[k] == "{":
            depth += 1
        elif t[k] == "}":
            depth -= 1
            if depth == 0:
                k += 1
                break
        k += 1
    block = t[j:k]
    photo_path = photo_rel if photo_rel.startswith("photos/") else f"photos/{photo_rel}"
    if "?v=" not in photo_path:
        photo_path = photo_path + "?v=r1"
    block2 = re.sub(r'photo:\s*"[^"]*"', f'photo: {json.dumps(photo_path)}', block, count=1)
    block2 = re.sub(r'photoCredit:\s*"[^"]*"', f'photoCredit: {json.dumps(credit)}', block2, count=1)
    CAT.write_text(t[:j] + block2 + t[k:], encoding="utf-8")

def update_ledger(asset_id: str, **fields):
    ledger = {"version": 1, "assets": []}
    if LEDGER.exists():
        ledger = json.loads(LEDGER.read_text())
    found = False
    for a in ledger.get("assets") or []:
        if a.get("asset_id") == asset_id:
            a.update(fields)
            a["checked_date"] = TODAY
            found = True
            break
    if not found:
        row = {"asset_id": asset_id, **fields, "checked_date": TODAY}
        ledger.setdefault("assets", []).append(row)
    ledger["updated"] = TODAY
    LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog-id", default="")
    ap.add_argument("--hero", default="", help="park slug for np-hero-{slug}.jpg")
    ap.add_argument("--commons-file", default="", help="Commons file title")
    ap.add_argument("--url", default="", help="Direct image URL")
    ap.add_argument("--credit", default="Photo via Wikimedia Commons")
    ap.add_argument("--license", default="")
    ap.add_argument("--score", type=int, default=4)
    ap.add_argument("--notes", default="")
    args = ap.parse_args()

    if bool(args.catalog_id) == bool(args.hero):
        raise SystemExit("Specify exactly one of --catalog-id or --hero")

    url = args.url
    meta = args.license
    if args.commons_file:
        url2, meta2 = commons_thumb(args.commons_file)
        if not url2:
            raise SystemExit(f"Commons miss: {args.commons_file}")
        url = url2
        meta = meta or meta2
        time.sleep(0.4)

    if not url:
        raise SystemExit("Need --commons-file or --url")

    if args.hero:
        dest = PHOTOS / f"np-hero-{args.hero}.jpg"
        asset_id = f"hero:{args.hero}"
        n = download(url, dest)
        # heroes are path-stable; no catalog patch required
        update_ledger(
            asset_id, role="hero", slug=args.hero, status="accepted",
            provenance="wikimedia" if "wikimedia" in args.credit.lower() or args.commons_file else "real_other",
            source_url=url, source_page=f"File:{args.commons_file}" if args.commons_file else "",
            license=meta, credit_ui=args.credit, credit_full=meta,
            local_path=f"photos/np-hero-{args.hero}.jpg", score=args.score, notes=args.notes,
        )
        print("OK hero", args.hero, n, dest)
        return 0

    # catalog card
    cid = args.catalog_id
    # keep filename stable when possible
    dest_name = cid + ".jpg" if not cid.endswith(".jpg") else cid
    # np-visitor-center -> np-visitor-center.jpg
    dest = PHOTOS / dest_name
    n = download(url, dest)
    rel = f"photos/{dest.name}"
    patch_catalog(cid, rel, args.credit)
    update_ledger(
        f"catalog:{cid}", role="shared" if cid.startswith("np-") else "stop",
        catalog_id=cid, status="accepted",
        provenance="wikimedia" if args.commons_file or "Wikimedia" in args.credit else "real_other",
        source_url=url, source_page=f"File:{args.commons_file}" if args.commons_file else "",
        license=meta, credit_ui=args.credit, credit_full=meta,
        local_path=rel, score=args.score, notes=args.notes,
    )
    print("OK catalog", cid, n, dest)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
