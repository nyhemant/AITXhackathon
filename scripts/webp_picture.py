#!/usr/bin/env python3
"""Right-size heavy images as NEW versioned WebP files and serve them via <picture>.

Idempotent post-pass (run after generate_bdo_seo.py / cards_hub_groups.py):
  python3 scripts/webp_picture.py            # make missing WebP files + wrap <img> tags

Rules (2026-10-29 mobile speed):
  * never overwrites an existing image: WebP names are <stem>-<w>-v1.webp; existing files are skipped
  * the original JPEG/PNG stays as the <img> src fallback; alt text and every other attribute unchanged
  * <picture style="display:contents"> so layout (flex/grid children, CSS on the img) is unaffected
"""
from __future__ import annotations
import re, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "static"
VER = "v1"
Q = 78

# img class (or src regex) -> (widths, sizes)
PHOTO_RULES = {
    "cards-hub-thumb": ((320, 480), "160px"),
    "card-try-next-thumb": ((320,), "160px"),
    "card-page-photo": ((640, 960), "(max-width: 700px) 92vw, 480px"),
}
SRC_RULES = [  # (src path regex, widths, sizes)
    (r"^/start/playing-card-(koala|tiger|zebra)\.png$", (240, 360), "120px"),
    (r"^/start/hero-world-map\.jpg$", (1280, 1792), "max(100vw, calc(100svh * 1792 / 1008))"),
    (r"^/start/going-(giraffe|georgia-aquarium|san-diego-zoo)\.jpg$", (480, 640, 1024), None),
    (r"^/start/home-print-table\.jpg$", (480, 640, 1024), None),
    (r"^/field-pack/photos/[a-z0-9-]+\.jpg$", (320, 480), "160px"),  # try-card tiles (cards hub only)
]
HUB_ONLY_RX = r"^/field-pack/photos/"
LCP_CLASSES = ("card-page-photo", "cards-play-still")  # fetchpriority=high, never lazy

def webp_name(path: Path, w: int) -> Path:
    return path.with_name(f"{path.stem}-{w}-{VER}.webp")

def ensure_webp(src_file: Path, widths) -> list[tuple[str, int]]:
    """Create missing WebP variants (never overwrite). Returns [(filename, width)]."""
    out = []
    im = None
    for w in widths:
        dst = webp_name(src_file, w)
        if not dst.exists():
            if im is None:
                im = Image.open(src_file)
                im.load()
            ow, oh = im.size
            tw = min(w, ow)
            rim = im if tw == ow else im.resize((tw, round(oh * tw / ow)), Image.LANCZOS)
            if rim.mode not in ("RGB", "RGBA"):
                rim = rim.convert("RGBA" if "A" in rim.getbands() else "RGB")
            rim.save(dst, "WEBP", quality=Q, method=6)
        out.append((dst.name, min(w, Image.open(dst).size[0] if dst.exists() else w)))
    return out

def attr(tag: str, name: str):
    m = re.search(r'\s' + name + r'="([^"]*)"', tag)
    return m.group(1) if m else None

def rule_for(tag: str, is_hub: bool = False):
    cls = attr(tag, "class") or ""
    for c, (ws, sz) in PHOTO_RULES.items():
        if c in cls.split():
            return ws, sz
    src = attr(tag, "src") or attr(tag, "data-src") or ""
    path = src.split("?")[0]
    for rx, ws, sz in SRC_RULES:
        if re.match(rx, path):
            if rx.startswith(HUB_ONLY_RX) and not is_hub:
                return None
            return ws, sz
    return None

IMG_RX = re.compile(r"(<picture\b[^>]*>\s*(?:<source\b[^>]*>\s*)*)?(<img\b[^>]*?/?>)", re.S)

def add_priority(tag: str) -> str:
    cls = (attr(tag, "class") or "").split()
    if any(c in cls for c in LCP_CLASSES) and "fetchpriority=" not in tag and 'loading="lazy"' not in tag:
        tag = re.sub(r"\s*/?>$", lambda m: ' fetchpriority="high"' + m.group(0), tag, count=1)
    return tag

def wrap_html(html: str, stats: dict, is_hub: bool = False) -> str:
    def fix(m):
        if m.group(1):  # already wrapped by us (picture + sources directly before img)
            return m.group(0)
        if "image/webp" in html[max(0, m.start() - 600): m.start()].rsplit("<img", 1)[-1]:
            return m.group(0)  # a webp source already sits right before this img
        tag = add_priority(m.group(2))
        r = rule_for(tag, is_hub)
        if not r:
            return tag
        ws, sizes = r
        lazy_src = attr(tag, "data-src")
        if "/start/going-" in (attr(tag, "src") or "") and not lazy_src:
            return tag  # no-JS Dallas fallback still stays a single plain JPEG (test_going_chapter_is_local_jpeg)
        src = attr(tag, "src") or lazy_src
        if not src or not src.startswith("/"):
            return tag
        f = STATIC / src.split("?")[0].lstrip("/")
        if not f.is_file():
            return tag
        variants = ensure_webp(f, ws)
        base = "/" + str(f.parent.relative_to(STATIC)).replace("\\", "/") + "/"
        srcset = ", ".join(f"{base}{n} {w}w" for n, w in variants)
        sizes = sizes or attr(tag, "sizes") or "100vw"
        sattr = "data-srcset" if (lazy_src and not attr(tag, "src")) else "srcset"
        stats["wrapped"] = stats.get("wrapped", 0) + 1
        source = f'<source type="image/webp" {sattr}="{srcset}" sizes="{sizes}" />'
        before = html[: m.start()]
        if before.rfind("<picture") > before.rfind("</picture>"):
            # already inside an author <picture> (e.g. media-switched art direction):
            # add the WebP source just before the <img>, after the existing sources.
            return source + "\n        " + tag
        return (f'<picture style="display:contents"><source type="image/webp" {sattr}="{srcset}" '
                f'sizes="{sizes}" />{tag}</picture>')
    # skip <noscript>/<template>-free assumption: only static HTML tags are touched
    return IMG_RX.sub(fix, html)

def targets() -> list[Path]:
    fp = STATIC / "field-pack"
    pages = [STATIC / "start" / "index.html", fp / "cards" / "index.html"]
    pages += sorted(p for p in (fp / "cards").glob("*/index.html"))
    return [p for p in pages if p.is_file()]

def main(argv):
    total = {}
    for p in targets():
        s = p.read_text(encoding="utf-8")
        st = {}
        s2 = wrap_html(s, st, is_hub=(p.parent.name == "cards"))
        if s2 != s:
            p.write_text(s2, encoding="utf-8")
        for k, v in st.items():
            total[k] = total.get(k, 0) + v
    print("webp_picture:", total)

if __name__ == "__main__":
    main(sys.argv[1:])
