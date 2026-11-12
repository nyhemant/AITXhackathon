#!/usr/bin/env python3
"""Write crawlable Virtual Field Trip tab sections from existing JSON + catalog blurbs."""
from __future__ import annotations

import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "static" / "field-pack"
VENUES = ROOT / "data/virtual-venues"
CATALOG = ROOT / "js/catalog.js"
PAGES = [
    ROOT / "virtual-field-trip/index.html",
]
START = "<!-- VFT:PANELS:START -->"
END = "<!-- VFT:PANELS:END -->"
NEXT_START = "<!-- VFT:NEXT:START -->"
NEXT_END = "<!-- VFT:NEXT:END -->"
VFT_CSS_VER = "61"
REPO = Path(__file__).resolve().parents[1]

TABS = [
    {
        "id": "zoo",
        "json": "virtual-zoo.json",
        "h2": "Zoo",
        "href": "/field-pack/virtual-field-trip/?tab=zoo#zoo",
        "label": "Zoo",
    },
    {
        "id": "aquarium",
        "json": "virtual-aquarium.json",
        "h2": "Aquarium",
        "href": "/field-pack/virtual-field-trip/?tab=aquarium#aquarium",
        "label": "Aquarium",
    },
    {
        "id": "natural-history",
        "json": "virtual-nhm.json",
        "h2": "Natural History Museum",
        "href": "/field-pack/virtual-field-trip/?tab=natural-history#natural-history",
        "label": "Museum",
    },
    {
        "id": "science",
        "json": "virtual-science.json",
        "h2": "Science Museum",
        "href": "/field-pack/virtual-field-trip/?tab=science#science",
        "label": "Science",
    },
    {
        "id": "parks",
        "json": "virtual-parks.json",
        "h2": "National Parks",
        "href": "/field-pack/virtual-field-trip/?tab=parks#parks",
        "label": "Parks",
    },
]


def esc(s: str) -> str:
    return (
        str(s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def catalog_index(text: str) -> dict[str, dict]:
    """Pull name + blurb for catalog object keys. No new copy."""
    out: dict[str, dict] = {}
    for m in re.finditer(
        r'''(?:^|\n)\s*(?:(?P<bare>[A-Za-z0-9_-]+)|"(?P<qid>[^"]+)")\s*:\s*\{''',
        text,
    ):
        key = m.group("qid") or m.group("bare")
        chunk = text[m.end() : m.end() + 1800]
        name_m = re.search(r'name:\s*"((?:\\.|[^"\\])*)"', chunk)
        blurb_m = re.search(r'blurb:\s*"((?:\\.|[^"\\])*)"', chunk)
        if not name_m:
            continue
        def unesc(s: str) -> str:
            return s.replace('\\"', '"').replace("\\'", "'").replace("\\n", " ")

        out[key] = {
            "name": unesc(name_m.group(1)),
            "blurb": unesc(blurb_m.group(1)) if blurb_m else "",
        }
    return out


def teaser(h: dict, cat: dict) -> str:
    cid = h.get("cardId") or h.get("id")
    item = cat.get(cid) or {}
    return (h.get("blurb") or item.get("blurb") or "").strip()


def card_href(h: dict, tab: str = "zoo") -> tuple[str, str]:
    if h.get("placeHref"):
        return h["placeHref"], "Park kit"
    cid = h.get("cardId") or h.get("id")
    if cid and (ROOT / "cards" / cid / "index.html").is_file():
        return f"/field-pack/cards/{cid}/", "Open card"
    hid = h.get("id") or cid or ""
    return f"/field-pack/virtual-field-trip/?tab={tab}#habitat={hid}", ""


def cam_line(h: dict) -> str:
    cam = h.get("cam") or {}
    url = cam.get("url")
    if not url:
        return ""
    label = cam.get("camLabel") or "Live camera"
    return f'<a class="vz-static-cam" href="{esc(url)}" rel="noopener">Live cam — {esc(label)}</a>'


def _cam_embed(h: dict) -> str:
    cam = h.get("cam") if isinstance(h, dict) else None
    if not isinstance(cam, dict):
        return ""
    embed = cam.get("embed")
    if not embed:
        return ""
    return str(embed).strip()


def film_line(h: dict, tab: str = "zoo") -> str:
    """One in-page film control. The YouTube URL stays in the player, not a second link."""
    video = h.get("video") or {}
    url = video.get("url")
    if not url:
        return ""
    label = video.get("title") or "A short film"
    hid = h.get("id") or h.get("cardId") or ""
    href = f"/field-pack/virtual-field-trip/?tab={tab}#habitat={hid}"
    return (
        f'<a class="vz-static-film" href="{esc(href)}" data-habitat="{esc(hid)}" role="button">'
        f"Film — {esc(label)}</a>"
    )


def stop_watch_html(h: dict, tab: str = "zoo") -> str:
    """One watch control per stop.

    An in-page cam embed is the live door. Otherwise the film is the control.
    An outbound cam page is used only when there is no film. Never pair a film
    with a second YouTube link for the same title.
    """
    if _cam_embed(h):
        cam = cam_line(h)
        if cam:
            return cam
    film = film_line(h, tab)
    if film:
        return film
    return cam_line(h)


def render_panels(cat: dict) -> str:
    chunks = [
        '<noscript><style>.vz-tab-panel[hidden]{display:block!important}</style></noscript>',
        '<div class="vz-static-panels">',
    ]
    for spec in TABS:
        data = json.loads((VENUES / spec["json"]).read_text())
        habs = sorted(data.get("habitats") or [], key=lambda h: h.get("seq") or 0)
        items = []
        for h in habs:
            name = h.get("label") or (cat.get(h.get("cardId") or h.get("id")) or {}).get("name") or h.get("id")
            line = teaser(h, cat)
            href, kind = card_href(h, spec["id"])
            watch = stop_watch_html(h, spec["id"])
            kind_html = f'<p class="vz-static-kind">{esc(kind)}</p>' if kind else ""
            items.append(
                f"""          <li>
            <a href="{esc(href)}">{esc(name)}</a>
            {f'<p>{esc(line)}</p>' if line else ''}
            {watch}
            {kind_html}
          </li>"""
            )
        chunks.append(
            f"""      <section class="vz-tab-panel" id="{spec['id']}" data-vz-panel="{spec['id']}">
        <h2>{esc(spec['h2'])}</h2>
        <p class="vz-static-count">{len(habs)} {'halls' if spec['id']=='natural-history' else 'stops'}</p>
        <ol class="vz-static-stops">
{chr(10).join(items)}
        </ol>
      </section>"""
        )
    chunks.append("      </div>")
    return "\n".join(chunks)


def render_tabs() -> str:
    return (
        '        <nav class="vz-venues no-print" id="vz-venues" aria-label="Choose a venue">\n'
        '          <div class="vz-tabs" id="vz-tabs">\n'
        '            <a class="vz-tab" href="/field-pack/virtual-field-trip/?tab=zoo#zoo" data-tab="zoo">Zoo</a>\n'
        '            <a class="vz-tab" href="/field-pack/virtual-field-trip/?tab=aquarium#aquarium" data-tab="aquarium">Aquarium</a>\n'
        '            <a class="vz-tab" href="/field-pack/virtual-field-trip/?tab=natural-history#natural-history" data-tab="museum" data-venue="museum">Museum</a>\n'
        '            <a class="vz-tab" href="/field-pack/virtual-field-trip/?tab=parks#parks" data-tab="parks">Parks</a>\n'
        "          </div>\n"
        '          <div class="vz-chips" id="vz-museum-chips" hidden role="group" aria-label="Museum floor">\n'
        '            <a class="vz-chip" href="/field-pack/virtual-field-trip/?tab=natural-history#natural-history" data-tab="natural-history">Natural history</a>\n'
        '            <a class="vz-chip" href="/field-pack/virtual-field-trip/?tab=science#science" data-tab="science">Science</a>\n'
        "          </div>\n"
        "        </nav>"
    )


def splice(html: str, start: str, end: str, inner: str) -> str:
    a = html.find(start)
    b = html.find(end)
    if a == -1 or b == -1 or b < a:
        raise SystemExit(f"missing markers {start}")
    return html[: a + len(start)] + "\n" + inner + "\n        " + html[b:]


def _image_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] == b"\x89PNG\r\n\x1a\n" and len(data) >= 24:
        w, h = struct.unpack(">II", data[16:24])
        return int(w), int(h)
    if data[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack(">HH", data[i + 5 : i + 9])
                return int(w), int(h)
            if marker in (0xD8, 0xD9):
                i += 2
                continue
            seglen = struct.unpack(">H", data[i + 2 : i + 4])[0]
            i += 2 + seglen
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        j = data.find(b"VP8X")
        if j != -1 and j + 18 <= len(data):
            payload = data[j + 8 : j + 18]
            w = 1 + int.from_bytes(payload[4:7], "little")
            h = 1 + int.from_bytes(payload[7:10], "little")
            return w, h
        j = data.find(b"VP8 ")
        if j != -1:
            k = data.find(b"\x9d\x01\x2a", j)
            if k != -1 and k + 7 <= len(data):
                w = struct.unpack("<H", data[k + 3 : k + 5])[0] & 0x3FFF
                h = struct.unpack("<H", data[k + 5 : k + 7])[0] & 0x3FFF
                if w and h:
                    return int(w), int(h)
    raise SystemExit(f"could not read image size for {path}")


def explore_next_cards() -> list[dict]:
    """Three existing repo images. Alt text is the link label, set by the renderer."""
    static = REPO / "static"
    return [
        {
            "href": "/field-pack/cards/",
            "label": "Meet the animals",
            "klass": "vz-next-animals",
            "src": "/field-pack/photos/giant-panda-480-v1.webp",
            "file": static / "field-pack/photos/giant-panda-480-v1.webp",
        },
        {
            "href": "/field-pack/zoos/",
            "label": "Plan a real zoo trip",
            "klass": "vz-next-place",
            "src": "/start/going-san-diego-zoo-480.jpg",
            "file": static / "start/going-san-diego-zoo-480.jpg",
        },
        {
            "href": "/printables/scavenger-hunt/",
            "label": "Print a scavenger hunt",
            "klass": "vz-next-print",
            "src": "/printables/img/scavenger-hunt.png",
            "file": static / "printables/img/scavenger-hunt.png",
        },
    ]


def render_explore_next() -> str:
    cards = []
    for spec in explore_next_cards():
        if not spec["file"].is_file():
            raise SystemExit(f"missing explore-next image {spec['file']}")
        if re.search(r"\bfree\b", spec["label"], re.I):
            raise SystemExit("explore-next label must not say Free")
        w, h = _image_size(spec["file"])
        cards.append(
            f"""        <a class="vz-next-card {spec['klass']}" href="{esc(spec['href'])}">
          <img src="{esc(spec['src'])}" alt="{esc(spec['label'])}" width="{w}" height="{h}" loading="lazy" decoding="async" />
          <span>{esc(spec['label'])}</span>
        </a>"""
        )
    return (
        '      <section class="vz-next no-print" aria-label="Explore next">\n'
        "        <h2>Explore next</h2>\n"
        '        <div class="vz-next-row">\n'
        + "\n".join(cards)
        + "\n        </div>\n"
        "      </section>"
    )


def ensure_explore_next(html: str) -> str:
    block = render_explore_next()
    if NEXT_START in html and NEXT_END in html:
        return splice(html, NEXT_START, NEXT_END, block)
    needle = "</main>"
    idx = html.find(needle)
    if idx == -1:
        raise SystemExit("virtual field trip page is missing </main>")
    return html[:idx] + f"{NEXT_START}\n{block}\n        {NEXT_END}\n      " + html[idx:]


def main() -> None:
    cat = catalog_index(CATALOG.read_text(encoding="utf-8"))
    panels = render_panels(cat)
    tabs = render_tabs()
    for page in PAGES:
        html = page.read_text(encoding="utf-8")
        html = splice(html, START, END, panels)
        if "<!-- VFT:TABS:START -->" in html:
            html = splice(html, "<!-- VFT:TABS:START -->", "<!-- VFT:TABS:END -->", tabs)
        html = ensure_explore_next(html)
        html = re.sub(
            r"virtual-venue\.css\?v=\d+",
            f"virtual-venue.css?v={VFT_CSS_VER}",
            html,
            count=1,
        )
        page.write_text(html, encoding="utf-8")
        print(f"wrote panels into {page.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
