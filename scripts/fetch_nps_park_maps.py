#!/usr/bin/env python3
"""
Discover and download official NPS park maps (public domain) for US national parks.

For each US park venue:
  1. Parse park code from official_url (nps.gov/{code}/)
  2. Scrape maps.htm (+ fallbacks) for PDF/image map assets on nps.gov
  3. Fall back to NPMaps / Wikimedia Commons NPS map assets when needed
  4. Download best candidate; smart-crop multi-page unigrids (map page + trim)
  5. Write static/field-pack/media/maps/{slug}.jpg (enlarged map preview)
  6. Link visitor_map_page to full PDF (or maps.htm) for deep dives
  7. Update venue media + rebuild print-maps.js

Usage:
  python3 scripts/fetch_nps_park_maps.py
  python3 scripts/fetch_nps_park_maps.py --slug yellowstone
  python3 scripts/fetch_nps_park_maps.py --dry-run
"""
from __future__ import annotations

import argparse
import html as htmlmod
import json
import re
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENUE_DIR = ROOT / "static/field-pack/data/venues"
MAP_DIR = ROOT / "static/field-pack/media/maps"
PRINT_MAPS_JS = ROOT / "static/field-pack/js/print-maps.js"
LEDGER = ROOT / "scripts/data/nps_park_maps_ledger.json"
UA = {
    "User-Agent": "1LessFieldTripKit/1.0 (https://1less.app; educational; NPS public-domain maps)",
    "Accept": "text/html,application/xhtml+xml,application/pdf,image/*;q=0.9,*/*;q=0.8",
}
CTX = ssl.create_default_context()
TODAY = date.today().isoformat()
BASE = "https://www.nps.gov"

# Prefer true cartographic products (park-wide map > area/trail > newspaper)
PDF_SCORE_WORDS = (
    (r"unigrid", 100),
    (r"(^|/)[a-z]{4}map\d", 95),  # GRCAmap2.pdf style
    (r"park[-_]?map", 90),
    (r"pocket[-_]?map", 88),
    (r"map[-_]?page", 88),
    (r"tear[-_]?off", 80),
    (r"visitor[-_]?map", 80),
    (r"brochure.*map|map.*brochure", 75),
    (r"grte-tear|yell-grte", 70),
    (r"national[-_]?park[-_]?map", 70),
    (r"(^|/)map", 60),
    (r"map", 40),
)
BAD_PDF = re.compile(
    r"campground|trail[-_]?guide|newspaper|centennial|info[-_]?guide|"
    r"visitor[-_]?guide|hike|accessibility-only|fees|pass\.pdf|application|"
    r"backcountry|intro-bc|north-rim-pocket",
    re.I,
)
BAD_IMG = re.compile(
    r"campground|trail[-_]?guide|thumb|icon|logo|branding|app-promo|clear\.gif|"
    r"crop16_9|grid_builder",
    re.I,
)
IMG_MAP = re.compile(r"map|unigrid|brochure", re.I)

# slug → NPMaps path segment (usually same as slug)
NPMAPS_SLUG = {
    "gates-of-arctic": "gates-of-the-arctic",
    "great-smoky-mountains": "great-smoky-mountains",
    "wrangell-st-elias": "wrangell-st-elias",
    "black-canyon-gunnison": "black-canyon-of-the-gunnison",
    "haleakala": "haleakala",
    "hawaii-volcanoes": "hawaii-volcanoes",
    "american-samoa": "national-park-of-american-samoa",
}


def fetch(url: str, timeout: int = 60) -> tuple[bytes, str]:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, context=CTX, timeout=timeout) as r:
        ctype = (r.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        return r.read(), ctype


def abs_url(href: str, page_url: str) -> str:
    href = htmlmod.unescape(href).strip()
    if href.startswith("//"):
        return "https:" + href
    return urllib.parse.urljoin(page_url, href)


def park_code(v: dict) -> str:
    url = (v.get("official_url") or "").strip()
    m = re.search(r"nps\.gov/([a-z]{4})(/|$)", url, re.I)
    if m:
        return m.group(1).lower()
    # slug fallbacks for odd cases
    slug = (v.get("slug") or "").lower()
    FALL = {
        "great-smoky-mountains": "grsm",
        "rocky-mountain": "romo",
        "grand-canyon": "grca",
        "bryce-canyon": "brca",
        "canyonlands": "cany",
        "capitol-reef": "care",
        "carlsbad-caverns": "cave",
        "channel-islands": "chis",
        "crater-lake": "crla",
        "cuyahoga-valley": "cuva",
        "death-valley": "deva",
        "dry-tortugas": "drto",
        "everglades": "ever",
        "gates-of-arctic": "gaar",
        "gateway-arch": "jeff",  # sometimes gate
        "glacier-bay": "glba",
        "grand-teton": "grte",
        "great-basin": "grba",
        "great-sand-dunes": "grsa",
        "guadalupe-mountains": "gumo",
        "haleakala": "hale",
        "hawaii-volcanoes": "havo",
        "hot-springs": "hosp",
        "indiana-dunes": "indu",
        "isle-royale": "isro",
        "joshua-tree": "jotr",
        "kenai-fjords": "kefj",
        "kings-canyon": "seki",
        "kobuk-valley": "kova",
        "lake-clark": "lacl",
        "lassen-volcanic": "lavo",
        "mammoth-cave": "maca",
        "mesa-verde": "meve",
        "mount-rainier": "mora",
        "new-river-gorge": "neri",
        "north-cascades": "noca",
        "petrified-forest": "pefo",
        "pinnacles": "pinn",
        "redwood": "redw",
        "saguaro": "sagu",
        "sequoia": "seki",
        "shenandoah": "shen",
        "theodore-roosevelt": "thro",
        "virgin-islands": "viis",
        "voyageurs": "voya",
        "white-sands": "whsa",
        "wind-cave": "wica",
        "wrangell-st-elias": "wrst",
        "american-samoa": "npsa",
        "black-canyon-gunnison": "blca",
        "big-bend": "bibe",
        "biscayne": "bisc",
        "congaree": "cong",
        "denali": "dena",
        "katmai": "katm",
        "glacier": "glac",
        "yellowstone": "yell",
        "yosemite": "yose",
        "zion": "zion",
        "acadia": "acad",
        "arches": "arch",
        "olympic": "olym",
        "rocky-mountain": "romo",
        "badlands": "badl",
    }
    return FALL.get(slug, "")


def score_pdf(url: str) -> int:
    u = url.lower()
    if BAD_PDF.search(u):
        return -100
    best = 0
    for pat, sc in PDF_SCORE_WORDS:
        if re.search(pat, u):
            best = max(best, sc)
    if u.endswith(".pdf") and best == 0:
        best = 10
    return best


def score_img(url: str) -> int:
    u = url.lower()
    if BAD_IMG.search(u) or BAD_PDF.search(u):
        return -100
    if not IMG_MAP.search(u):
        return 0
    if "park-map" in u or "parkmap" in u or re.search(r"[a-z]{4}map\d", u):
        return 70
    if "map" in u:
        return 50
    return 20


def extract_assets(page_html: str, page_url: str) -> list[tuple[int, str, str]]:
    """Return list of (score, kind, url)."""
    out: list[tuple[int, str, str]] = []
    page_html = htmlmod.unescape(page_html)
    hrefs = re.findall(r'(?:href|src)=["\']([^"\']+)["\']', page_html, re.I)
    for h in hrefs:
        u = abs_url(h, page_url)
        if "nps.gov" not in u and not u.startswith("/"):
            # allow only nps on park pages
            if not u.startswith(BASE):
                continue
        if not u.startswith("http"):
            u = abs_url(u, BASE + "/")
        if "nps.gov" not in u:
            continue
        path = urllib.parse.urlparse(u).path.lower()
        if path.endswith(".pdf") or ".pdf?" in u.lower():
            sc = score_pdf(u)
            if sc > 0:
                out.append((sc, "pdf", u.split("?")[0]))
        elif re.search(r"\.(jpe?g|png|gif|webp)$", path):
            sc = score_img(u)
            if sc > 0:
                # strip resize query for max quality where possible
                clean = u
                if "maxwidth=" in u:
                    clean = re.sub(r"maxwidth=\d+", "maxwidth=2000", u)
                    clean = re.sub(r"maxheight=\d+", "maxheight=2000", clean)
                # drop format=webp — prefer original jpeg when available
                clean = re.sub(r"([&?])format=webp", r"\1", clean).rstrip("?&")
                out.append((sc, "image", clean))
    # dedupe by url keep max score
    best: dict[str, tuple[int, str, str]] = {}
    for sc, kind, u in out:
        prev = best.get(u)
        if not prev or sc > prev[0]:
            best[u] = (sc, kind, u)
    return sorted(best.values(), key=lambda x: -x[0])


def discover_npmaps(slug: str) -> list[tuple[int, str, str]]:
    """NPMaps hosts high-res NPS public-domain park maps."""
    seg = NPMAPS_SLUG.get(slug, slug)
    page = f"https://www.npmaps.com/{seg}/"
    try:
        raw, _ = fetch(page, timeout=40)
        html = raw.decode("utf-8", "replace")
    except Exception:
        return []
    # Prefer full park map jpg, not thumbs/downloads/amazon
    urls = re.findall(
        r"https?://(?:www\.)?npmaps\.com/wp-content/uploads/[^\"'\s>]+\.(?:jpe?g|png|gif)",
        html,
        re.I,
    )
    out: list[tuple[int, str, str]] = []
    seen = set()
    for u in urls:
        u = u.split()[0].rstrip(".,)")
        if u in seen:
            continue
        seen.add(u)
        low = u.lower()
        if "thumb" in low or "amazon" in low or "download" in low and "park-map" not in low:
            # keep *-park-map-download only if no better
            if "national-park-map-download" not in low and "park-map-download" not in low:
                continue
        sc = 55
        if re.search(r"national-park-map\.jpe?g$", low) or re.search(r"park-map\.jpe?g$", low):
            sc = 72
        elif re.search(r"-map\.jpe?g$", low) and "trail" not in low and "detail" not in low:
            sc = 65
        elif "detail" in low or "trail" in low:
            sc = 40
        out.append((sc, "image", u))
    return sorted(out, key=lambda x: -x[0])


def discover_commons(slug: str, code: str) -> list[tuple[int, str, str]]:
    """Wikimedia Commons often mirrors NPS map PDFs (File:NPS {park}-map.pdf)."""
    name = slug.replace("-", " ")
    # Tokenize slug for title matching (avoid cuyahoga hit for haleakala)
    tokens = [t for t in slug.split("-") if len(t) > 2 and t not in ("the", "and", "national", "park")]
    queries = [
        f'intitle:"NPS" intitle:map {name}',
        f"File:NPS {slug}-map",
        f"File:NPS {name}-map",
        f"NPS {code} map",
    ]
    titles: list[str] = []
    for q in queries:
        api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
            {
                "action": "query",
                "list": "search",
                "srsearch": q,
                "srnamespace": 6,
                "srlimit": 8,
                "format": "json",
            }
        )
        try:
            raw, _ = fetch(api, timeout=30)
            j = json.loads(raw.decode("utf-8", "replace"))
            for hit in j.get("query", {}).get("search", []):
                t = hit.get("title") or ""
                if t and t not in titles:
                    titles.append(t)
        except Exception:
            continue
        time.sleep(0.2)
    if not titles:
        return []
    api2 = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "titles": "|".join(titles[:12]),
            "prop": "imageinfo",
            "iiprop": "url|size|mime",
            "format": "json",
        }
    )
    out: list[tuple[int, str, str]] = []
    try:
        raw, _ = fetch(api2, timeout=40)
        j = json.loads(raw.decode("utf-8", "replace"))
        pages = (j.get("query") or {}).get("pages") or {}
        for _pid, pg in pages.items():
            info = (pg.get("imageinfo") or [{}])[0]
            url = info.get("url") or ""
            mime = (info.get("mime") or "").lower()
            title = (pg.get("title") or "").lower()
            if not url:
                continue
            if "map" not in title and "map" not in url.lower():
                continue
            # Must mention park name tokens or 4-letter code — reject cross-park hits
            if code and f" {code} " not in f" {title} " and code not in title.replace("-", " "):
                if tokens and not all(tok in title for tok in tokens[:2]):
                    # require at least first distinctive token
                    if tokens[0] not in title:
                        continue
            sc = 45
            if title.startswith("file:nps ") and "map" in title:
                sc = 68
            if "geologic" in title or "geology" in title or "3d" in title or "visitor-center" in title:
                sc = min(sc, 22)
            if "trail" in title or "backcountry" in title or "topo" in title:
                sc = min(sc, 35)
            # Prefer plain park-wide NPS maps (not specialty overlays)
            if re.search(r"nps [a-z0-9 -]+-map\.(pdf|jpe?g|png)", title) and "geologic" not in title:
                sc = max(sc, 66)
            if "park-map" in title or "national-park-map" in title:
                sc = max(sc, 70)
            kind = "pdf" if "pdf" in mime or url.lower().endswith(".pdf") else "image"
            out.append((sc, kind, url))
    except Exception:
        return []
    return sorted(out, key=lambda x: -x[0])


def discover(code: str, slug: str = "") -> list[tuple[int, str, str]]:
    pages = [
        f"{BASE}/{code}/planyourvisit/maps.htm",
        f"{BASE}/{code}/planyourvisit/maps.html",
        f"{BASE}/{code}/planyourvisit/parkmaps.htm",
        f"{BASE}/{code}/planyourvisit/brochures.htm",
        f"{BASE}/{code}/planyourvisit/index.htm",
        f"{BASE}/{code}/index.htm",
    ]
    found: list[tuple[int, str, str]] = []
    for page in pages:
        try:
            raw, ctype = fetch(page, timeout=45)
            if "html" not in ctype and not raw[:200].lstrip().lower().startswith(b"<!doctype"):
                continue
            html = raw.decode("utf-8", "replace")
            found.extend(extract_assets(html, page))
            time.sleep(0.35)
        except Exception:
            continue
    # common upload guesses
    guesses = [
        f"{BASE}/{code}/planyourvisit/upload/{code.upper()}map.pdf",
        f"{BASE}/{code}/planyourvisit/upload/{code.upper()}map2.pdf",
        f"{BASE}/{code}/planyourvisit/upload/{code}map.pdf",
        f"{BASE}/{code}/planyourvisit/upload/parkmap.pdf",
        f"{BASE}/{code}/planyourvisit/upload/{code.upper()}_Unigrid.pdf",
        f"{BASE}/{code}/planyourvisit/images/{code.upper()}map1.jpg",
        f"{BASE}/{code}/planyourvisit/images/{code}map1.jpg",
    ]
    for g in guesses:
        try:
            req = urllib.request.Request(g, method="HEAD", headers=UA)
            with urllib.request.urlopen(req, context=CTX, timeout=20) as r:
                if 200 <= r.status < 300:
                    kind = "pdf" if g.lower().endswith(".pdf") else "image"
                    sc = score_pdf(g) if kind == "pdf" else score_img(g)
                    if sc > 0:
                        found.append((sc, kind, g))
        except Exception:
            pass
        time.sleep(0.1)

    # Fallbacks when NPS page is JS-thin or links 404
    n_good = sum(1 for sc, _, _ in found if sc >= 50)
    if slug and n_good < 1:
        found.extend(discover_npmaps(slug))
        found.extend(discover_commons(slug, code))

    # dedupe
    best: dict[str, tuple[int, str, str]] = {}
    for sc, kind, u in found:
        prev = best.get(u)
        if not prev or sc > prev[0]:
            best[u] = (sc, kind, u)
    return sorted(best.values(), key=lambda x: -x[0])


def save_image_bytes(data: bytes, jpg_path: Path) -> bool:
    # if already jpeg/png write; convert via sips/Pillow
    jpg_path.parent.mkdir(parents=True, exist_ok=True)
    if data[:3] == b"\xff\xd8\xff":
        jpg_path.write_bytes(data)
        return jpg_path.stat().st_size > 15000
    tmp = jpg_path.with_suffix(".srcbin")
    tmp.write_bytes(data)
    r = subprocess.run(
        ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "88", str(tmp), "--out", str(jpg_path)],
        capture_output=True,
        text=True,
    )
    tmp.unlink(missing_ok=True)
    if r.returncode == 0 and jpg_path.exists() and jpg_path.stat().st_size > 15000:
        return True
    # Pillow fallback (gif/png/webp)
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from PIL import Image  # type: ignore
        import io

        im = Image.open(io.BytesIO(data)).convert("RGB")
        im.save(jpg_path, "JPEG", quality=88, optimize=True)
        return jpg_path.exists() and jpg_path.stat().st_size > 15000
    except Exception:
        return False


def smart_crop_to(dest: Path, pdf_path: Path | None = None) -> dict:
    """Pick map page + trim non-map chrome. Falls back to plain image if crop module missing."""
    try:
        # Prefer project venv Pillow if present
        venv_py = ROOT / "scripts/.venv-maps/bin/python"
        crop_py = ROOT / "scripts/crop_park_map.py"
        if venv_py.exists() and crop_py.exists():
            if pdf_path and pdf_path.exists():
                cmd = [str(venv_py), str(crop_py), "--pdf", str(pdf_path), "--out", str(dest)]
            else:
                cmd = [str(venv_py), str(crop_py), "--image", str(dest), "--out", str(dest)]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            if r.returncode == 0 and dest.exists() and dest.stat().st_size > 10000:
                try:
                    return json.loads(r.stdout)
                except Exception:
                    return {"ok": True}
        # in-process import
        sys.path.insert(0, str(ROOT / "scripts"))
        import crop_park_map as cpm  # type: ignore

        if pdf_path and pdf_path.exists():
            return cpm.process_pdf(pdf_path, dest)
        return cpm.process_image(dest, dest)
    except Exception as e:
        return {"error": str(e)[:160]}


def rebuild_print_maps_js() -> int:
    """Rebuild FP_PRINT_MAPS + FP_PRINT_MAP_CREDITS from maps + venue JSON."""
    venue_slugs = {p.stem for p in VENUE_DIR.glob("*.json")}
    entries = []
    credits = []
    for img in sorted(MAP_DIR.glob("*.jpg")):
        slug = img.stem
        if slug not in venue_slugs:
            continue
        if img.stat().st_size < 20000:
            continue
        entries.append((slug, f"/field-pack/media/maps/{slug}.jpg"))
        vp = VENUE_DIR / f"{slug}.json"
        try:
            media = (json.loads(vp.read_text(encoding="utf-8")).get("media") or {})
            attr = (media.get("map_attribution") or "").strip()
            if attr:
                credits.append((slug, attr))
        except Exception:
            pass
    lines = [
        "/* Auto-generated print-safe local map paths for hunt one-pager */\n",
        "window.FP_PRINT_MAPS = {\n",
    ]
    for i, (slug, path) in enumerate(entries):
        comma = "," if i < len(entries) - 1 else ""
        lines.append(f'  "{slug}": "{path}"{comma}\n')
    lines.append("};\n")
    lines.append("window.FP_PRINT_MAP_CREDITS = {\n")
    for i, (slug, attr) in enumerate(credits):
        comma = "," if i < len(credits) - 1 else ""
        safe = attr.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'  "{slug}": "{safe}"{comma}\n')
    lines.append("};\n")
    PRINT_MAPS_JS.write_text("".join(lines), encoding="utf-8")
    return len(entries)


def _image_usable(path: Path, min_bytes: int = 25000, min_edge: int = 400) -> bool:
    if not path.exists() or path.stat().st_size < min_bytes:
        return False
    try:
        from PIL import Image  # type: ignore

        im = Image.open(path)
        w, h = im.size
        return min(w, h) >= min_edge or (w * h) >= 350_000
    except Exception:
        # size-only fallback
        return path.stat().st_size >= 80_000


def process_venue(v: dict, dry: bool = False) -> dict:
    slug = v["slug"]
    code = park_code(v)
    result = {
        "slug": slug,
        "code": code,
        "status": "skip",
        "source": "",
        "kind": "",
        "path": "",
        "error": "",
    }
    if not code:
        result["status"] = "no_code"
        return result

    cands = discover(code, slug=slug)
    # Always append fallbacks lower priority so broken top hits can recover
    extra = discover_npmaps(slug) + discover_commons(slug, code)
    seen = {u for _, _, u in cands}
    for item in extra:
        if item[2] not in seen:
            cands.append(item)
            seen.add(item[2])
    cands.sort(key=lambda x: -x[0])

    if not cands:
        result["status"] = "no_assets"
        return result

    result["candidates"] = [{"score": s, "kind": k, "url": u} for s, k, u in cands[:8]]

    if dry:
        score, kind, url = cands[0]
        result["source"] = url
        result["kind"] = kind
        result["score"] = score
        result["status"] = "dry"
        return result

    MAP_DIR.mkdir(parents=True, exist_ok=True)
    dest = MAP_DIR / f"{slug}.jpg"
    last_err = ""
    used = None

    for score, kind, url in cands[:10]:
        try:
            data, ctype = fetch(url, timeout=90)
        except Exception as e:
            last_err = str(e)[:160]
            continue

        pdf_path = None
        try:
            if kind == "pdf" or "pdf" in ctype or data[:4] == b"%PDF":
                pdf_path = MAP_DIR / f"{slug}.src.pdf"
                pdf_path.write_bytes(data)
                crop_meta = smart_crop_to(dest, pdf_path=pdf_path)
                if crop_meta.get("error") and not dest.exists():
                    last_err = crop_meta.get("error", "pdf_crop_fail")
                    pdf_path.unlink(missing_ok=True)
                    continue
                pdf_path.unlink(missing_ok=True)
                pdf_path = None
            else:
                if not save_image_bytes(data, dest):
                    if len(data) > 30000:
                        dest.write_bytes(data)
                    if not dest.exists() or dest.stat().st_size < 12000:
                        last_err = "image_save_fail"
                        continue
                # Smart-trim margins/chrome on already-map images
                smart_crop_to(dest, pdf_path=None)

            if not _image_usable(dest):
                last_err = f"too_small after {url[-50:]}"
                continue

            used = (score, kind, url)
            break
        except Exception as e:
            last_err = str(e)[:160]
            if pdf_path:
                pdf_path.unlink(missing_ok=True)
            continue

    if not used or not dest.exists():
        result["status"] = "download_fail"
        result["error"] = last_err or "no candidate produced usable map"
        return result

    score, kind, url = used
    result["source"] = url
    result["kind"] = kind
    result["score"] = score

    # update venue media — local cropped map for display; deep link to full PDF/site
    media = dict(v.get("media") or {})
    media["visitor_map_url"] = f"/field-pack/media/maps/{slug}.jpg"
    media["print_map"] = f"/field-pack/media/maps/{slug}.jpg"
    media["visitor_map_kind"] = "image"
    if kind == "pdf" or url.lower().endswith(".pdf"):
        media["visitor_map_page"] = url  # full brochure/unigrid PDF
        media["visitor_map_full"] = url
    else:
        media["visitor_map_page"] = (
            f"{BASE}/{code}/planyourvisit/maps.htm"
            if code
            else (media.get("visitor_map_page") or v.get("official_url") or "")
        )
        media["visitor_map_full"] = url
    if "npmaps.com" in url:
        media["map_attribution"] = "Map: NPS via NPMaps (public domain)"
    elif "wikimedia.org" in url or "wikipedia.org" in url:
        media["map_attribution"] = "Map: NPS via Wikimedia Commons (public domain)"
    else:
        media["map_attribution"] = "Map: National Park Service (public domain)"
    if not media.get("hero_illustration"):
        media["hero_illustration"] = f"/field-pack/photos/np-hero-{slug}.jpg"
    v["media"] = media
    (VENUE_DIR / f"{slug}.json").write_text(
        json.dumps(v, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    result["status"] = "ok"
    result["path"] = str(dest.relative_to(ROOT))
    result["bytes"] = dest.stat().st_size
    result["deep_link"] = media.get("visitor_map_page")
    return result


def ledger_from_disk() -> int:
    """Rebuild nps_park_maps_ledger.json from venue media + map files (no download)."""
    old = {}
    if LEDGER.exists():
        for r in json.loads(LEDGER.read_text(encoding="utf-8")).get("results") or []:
            if r.get("slug"):
                old[r["slug"]] = r
    results = []
    for p in sorted(VENUE_DIR.glob("*.json")):
        v = json.loads(p.read_text(encoding="utf-8"))
        if v.get("type") != "national_park":
            continue
        slug = v.get("slug") or p.stem
        dest = MAP_DIR / f"{slug}.jpg"
        media = v.get("media") or {}
        prev = old.get(slug) or {}
        page = str(media.get("visitor_map_page") or "")
        kind = prev.get("kind") or ("pdf" if page.lower().endswith(".pdf") else "image")
        source = (
            prev.get("source")
            or media.get("visitor_map_full")
            or page
            or ""
        )
        exists = dest.exists() and dest.stat().st_size >= 20000
        results.append(
            {
                "slug": slug,
                "code": park_code(v),
                "status": "ok" if exists else "missing",
                "source": source,
                "kind": kind,
                "path": str(dest.relative_to(ROOT)) if dest.exists() else "",
                "error": "" if exists else "map jpg missing on disk",
                "bytes": dest.stat().st_size if dest.exists() else 0,
                "deep_link": page,
                "map_attribution": media.get("map_attribution") or "",
            }
        )
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(
        json.dumps({"updated": TODAY, "source": "disk", "results": results}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    return len(results)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", default="")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument(
        "--ledger-from-disk",
        action="store_true",
        help="Refresh ledger + print-maps.js from existing files (no download)",
    )
    args = ap.parse_args()

    if args.ledger_from_disk:
        n = ledger_from_disk()
        n_maps = rebuild_print_maps_js()
        print(f"ledger from disk: {n} parks → {LEDGER}")
        print(f"print_maps_entries={n_maps}")
        return

    venues = []
    for p in sorted(VENUE_DIR.glob("*.json")):
        v = json.loads(p.read_text(encoding="utf-8"))
        if v.get("type") != "national_park":
            continue
        c = (v.get("country") or "US").upper()
        if c not in ("US", "USA", ""):
            continue
        if args.slug and v.get("slug") != args.slug:
            continue
        venues.append(v)
    if args.limit:
        venues = venues[: args.limit]

    print(f"US parks to process: {len(venues)} dry={args.dry_run}")
    results = []
    ok = fail = 0
    for i, v in enumerate(venues, 1):
        slug = v.get("slug")
        print(f"[{i}/{len(venues)}] {slug} …", flush=True)
        r = process_venue(v, dry=args.dry_run)
        results.append(r)
        st = r["status"]
        if st == "ok" or st == "dry":
            ok += 1
            print(f"  {st} score={r.get('score')} {r.get('kind')} {r.get('source','')[:80]}")
        else:
            fail += 1
            print(f"  FAIL {st} {r.get('error','')}")
        time.sleep(0.4)

    n_maps = rebuild_print_maps_js() if not args.dry_run else 0
    ledger = {"updated": TODAY, "results": results}
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(ledger, indent=2) + "\n")
    print(f"\nDONE ok={ok} fail={fail} print_maps_entries={n_maps}")
    print("ledger", LEDGER)


if __name__ == "__main__":
    main()
