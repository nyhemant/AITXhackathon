#!/usr/bin/env python3
"""Write crawlable Virtual Field Trip tab sections from existing JSON + catalog blurbs."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path("/Users/arku/Projects/AITXhackathon/static/field-pack")
VENUES = ROOT / "data/virtual-venues"
CATALOG = ROOT / "js/catalog.js"
PAGES = [
    ROOT / "virtual-field-trip/index.html",
    ROOT / "virtual-zoo/index.html",
]
START = "<!-- VFT:PANELS:START -->"
END = "<!-- VFT:PANELS:END -->"

TABS = [
    {
        "id": "zoo",
        "json": "virtual-zoo.json",
        "h2": "Virtual Zoo",
        "href": "/field-pack/virtual-field-trip/?tab=zoo#zoo",
        "label": "Zoo",
    },
    {
        "id": "aquarium",
        "json": "virtual-aquarium.json",
        "h2": "Virtual Aquarium Field Trip",
        "href": "/field-pack/virtual-field-trip/?tab=aquarium#aquarium",
        "label": "Aquarium",
    },
    {
        "id": "natural-history",
        "json": "virtual-nhm.json",
        "h2": "Virtual Natural History Museum",
        "href": "/field-pack/virtual-field-trip/?tab=natural-history#natural-history",
        "label": "Natural history",
    },
    {
        "id": "science",
        "json": "virtual-science.json",
        "h2": "Virtual Science Museum Field Trip",
        "href": "/field-pack/virtual-field-trip/?tab=science#science",
        "label": "Science museum",
    },
    {
        "id": "parks",
        "json": "virtual-parks.json",
        "h2": "Virtual National Parks Field Trip",
        "href": "/field-pack/virtual-field-trip/?tab=parks#parks",
        "label": "National parks",
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
        return f"/field-pack/cards/{cid}/", "Card"
    hid = h.get("id") or cid or ""
    return f"/field-pack/virtual-field-trip/?tab={tab}#habitat={hid}", "Card"


def cam_line(h: dict) -> str:
    cam = h.get("cam") or {}
    url = cam.get("url")
    if not url:
        return ""
    label = cam.get("camLabel") or "Live camera"
    return f'<a class="vz-static-cam" href="{esc(url)}" rel="noopener">Live cam — {esc(label)}</a>'


def film_line(h: dict) -> str:
    video = h.get("video") or {}
    url = video.get("url")
    if not url:
        return ""
    label = video.get("title") or "A short film"
    return f'<a class="vz-static-film" href="{esc(url)}" rel="noopener">Pre-recorded — {esc(label)}</a>'


def render_panels(cat: dict) -> str:
    chunks = [
        '<noscript><style>.vz-tab-panel[hidden]{display:block!important}html:not([data-vft-chrome="tour"]) .vz-stops-drawer{display:block!important}</style></noscript>',
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
            cam = cam_line(h)
            film = film_line(h)
            items.append(
                f"""          <li>
            <a href="{esc(href)}">{esc(name)}</a>
            {f'<p>{esc(line)}</p>' if line else ''}
            {cam}
            {film}
            <p class="vz-static-kind">{esc(kind)}</p>
          </li>"""
            )
        chunks.append(
            f"""      <section class="vz-tab-panel" id="{spec['id']}" data-vz-panel="{spec['id']}">
        <h2>{esc(spec['h2'])}</h2>
        <p class="vz-static-count">{len(habs)} {'halls' if spec['id']=='natural-history' else 'stops'} · existing Field Trip Kit {('park kits' if spec['id']=='parks' else 'cards')}</p>
        <ol class="vz-static-stops">
{chr(10).join(items)}
        </ol>
      </section>"""
        )
    chunks.append("      </div>")
    return "\n".join(chunks)


def render_tabs() -> str:
    links = []
    for spec in TABS:
        links.append(
            f'<a class="vz-tab" href="{esc(spec["href"])}" data-tab="{esc(spec["id"])}">{esc(spec["label"])}</a>'
        )
    return (
        '        <nav class="vz-tabs no-print" id="vz-tabs" aria-label="Virtual field trip">\n          '
        + "\n          ".join(links)
        + "\n        </nav>"
    )


def splice(html: str, start: str, end: str, inner: str) -> str:
    a = html.find(start)
    b = html.find(end)
    if a == -1 or b == -1 or b < a:
        raise SystemExit(f"missing markers {start}")
    return html[: a + len(start)] + "\n" + inner + "\n        " + html[b:]


def main() -> None:
    cat = catalog_index(CATALOG.read_text(encoding="utf-8"))
    panels = render_panels(cat)
    tabs = render_tabs()
    for page in PAGES:
        html = page.read_text(encoding="utf-8")
        html = splice(html, START, END, panels)
        if "<!-- VFT:TABS:START -->" in html:
            html = splice(html, "<!-- VFT:TABS:START -->", "<!-- VFT:TABS:END -->", tabs)
        page.write_text(html, encoding="utf-8")
        print(f"wrote panels into {page.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
