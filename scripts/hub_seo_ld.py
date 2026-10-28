"""Structured data for hub pages (2026-10-28, search visibility).

- cards_hub_json_ld(html): CollectionPage + ItemList built from the card links already on the
  /field-pack/cards/ hub (same order, same names). No new facts.
- START_JSON_LD: WebSite + Organization for the home page (/start/; "/" 301s there).

generate_bdo_seo.write_cards_hub() calls cards_hub_json_ld(); run this file as a script
(`python3 scripts/hub_seo_ld.py`) to refresh the block in the committed cards hub in place
(idempotent, between <!-- kz-seo:hub-ld --> markers).
"""
from __future__ import annotations

import html as _html
import json
import re
import sys
from pathlib import Path

SITE = "https://kidzookit.com"
MARK_START = "<!-- kz-seo:hub-ld -->"
MARK_END = "<!-- /kz-seo:hub-ld -->"

_LINK_RE = re.compile(
    r'<a class="cards-hub-link" href="(/field-pack/cards/[a-z0-9-]+/)" data-card-id="[a-z0-9-]+">'
    r'.*?<span class="cards-hub-name">([^<]+)</span>',
    re.S,
)


def _meta(h: str, attr: str, key: str) -> str:
    m = re.search(rf'<meta {attr}="{re.escape(key)}" content="([^"]*)"', h)
    return _html.unescape(m.group(1)) if m else ""


def cards_hub_items(h: str) -> list[tuple[str, str]]:
    seen: set[str] = set()
    out: list[tuple[str, str]] = []
    for href, name in _LINK_RE.findall(h):
        if href in seen:
            continue
        seen.add(href)
        out.append((href, _html.unescape(name.strip())))
    return out


def cards_hub_json_ld(h: str) -> str:
    items = cards_hub_items(h)
    m = re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S)
    name = _html.unescape(re.sub(r"<[^>]+>", "", m.group(1)).strip()) if m else "Animal Cards for Kids"
    data = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": name,
        "url": f"{SITE}/field-pack/cards/",
        "description": _meta(h, "name", "description"),
        "isPartOf": {"@type": "WebSite", "name": "KidZooKit", "url": f"{SITE}/"},
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(items),
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "url": f"{SITE}{href}", "name": nm}
                for i, (href, nm) in enumerate(items)
            ],
        },
    }
    body = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return f'{MARK_START}<script type="application/ld+json">{body}</script>{MARK_END}'


START_JSON_LD_DATA = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": "WebSite",
            "@id": f"{SITE}/#website",
            "name": "KidZooKit",
            "url": f"{SITE}/",
            "inLanguage": "en",
            "publisher": {"@id": f"{SITE}/#organization"},
        },
        {
            "@type": "Organization",
            "@id": f"{SITE}/#organization",
            "name": "KidZooKit",
            "url": f"{SITE}/",
            "logo": f"{SITE}/pwa/icon-512.png",
        },
    ],
}


def start_json_ld() -> str:
    body = json.dumps(START_JSON_LD_DATA, ensure_ascii=False)
    return f'{MARK_START}<script type="application/ld+json">{body}</script>{MARK_END}'


def upsert_before_head_end(h: str, block: str, *, end_tag: str = "</head>") -> str:
    if MARK_START in h:
        return re.sub(re.escape(MARK_START) + r".*?" + re.escape(MARK_END), lambda _m: block, h, count=1, flags=re.S)
    assert end_tag in h
    return h.replace(end_tag, f"  {block}\n{end_tag}", 1)


def upsert_cards_hub(h: str) -> str:
    """Cards hub: the block sits just before </body> so the visible card rows stay the first
    lines that mention each card id (tests and tools read the hub line by line)."""
    return upsert_before_head_end(h, cards_hub_json_ld(h), end_tag="</body>")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    p = root / "static" / "field-pack" / "cards" / "index.html"
    h = p.read_text(encoding="utf-8")
    p.write_text(upsert_cards_hub(h), encoding="utf-8")
    print(f"cards hub LD: {len(cards_hub_items(h))} items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
