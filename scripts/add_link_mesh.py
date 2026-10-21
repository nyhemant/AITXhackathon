#!/usr/bin/env python3
"""Add the in-body internal link mesh to static Field Trip Kit pages (idempotent).

Post-processes the committed static HTML (it does NOT regenerate pages):
  * place pages  -> visible breadcrumb (KidZooKit / All places / <Type hub> / Place),
                    BreadcrumbList JSON-LD, and an in-body "Explore more" block with
                    3-4 animal cards the page already features, 4-6 nearby or
                    same-type places, and the matching printable page.
  * card pages   -> current-card crumb + BreadcrumbList JSON-LD, a "Where to see"
                    list of up to 8 place pages that feature the animal plus a
                    "see all" hub link, and "More cards" when the page has <3 "Try next".
  * /start/      -> one "Popular trips" line of place links.
Every block sits between <!-- kz-mesh:* --> markers so re-running replaces it.
Clicks fire ``related_link_click`` (link_type only) via /shell/related-links.js,
which uses the shell's trackEvent and so respects analytics-off.

Durability: scripts/generate_bdo_seo.py does not emit these blocks yet. Re-run
``python3 scripts/add_link_mesh.py`` after any page regeneration
(tests/test_link_mesh.py fails if the blocks disappear).
"""
from __future__ import annotations

import html
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "static"
FIELD = STATIC / "field-pack"
CARDS = FIELD / "cards"
SITE = "https://kidzookit.com"

CSS_TAG = '<link rel="stylesheet" href="/field-pack/css/link-mesh.css?v=1" />'
JS_TAG = '<script src="/shell/related-links.js?v=1"></script>'

HUB = {  # place type -> (hub path, crumb label, plural for "see all")
    "zoo": ("/field-pack/zoos/", "Zoos", "zoos"),
    "safari_zoo": ("/field-pack/zoos/", "Zoos", "zoos"),
    "aquarium": ("/field-pack/aquariums/", "Aquariums", "aquariums"),
    "museum": ("/field-pack/museums/", "Museums", "museums"),
    "national_park": ("/field-pack/national-parks/", "National parks", "national parks"),
}
GROUP = {"zoo": "zoo", "safari_zoo": "zoo", "aquarium": "aquarium", "museum": "museum", "national_park": "park"}
PRINTABLE = {
    "zoo": ("/printables/scavenger-hunt/", "Zoo scavenger hunt printable"),
    "aquarium": ("/printables/animal-bingo/", "Animal bingo printable"),
    "museum": ("/printables/zoo-day-journal/", "Draw-and-wonder trip journal printable"),
    "park": ("/printables/", "Park scavenger hunt printable"),
}
PROPER = {"African", "American", "Asian", "Caribbean", "Galápagos", "Nile", "Sumatran", "Western", "Woven"}
START_TRIPS = ["bronx-zoo", "houston-zoo", "monterey-bay-aquarium", "shedd-aquarium", "yellowstone", "great-smoky-mountains"]

E = lambda s: html.escape(str(s), quote=True)  # noqa: E731


def strip_block(s: str, name: str) -> str:
    return re.sub(rf"\s*<!-- kz-mesh:{name} -->.*?<!-- /kz-mesh:{name} -->", "", s, flags=re.S)


def wrap(name: str, body: str) -> str:
    return f"<!-- kz-mesh:{name} -->{body}<!-- /kz-mesh:{name} -->"


def km(a, b) -> float:
    if a.get("lat") is None or b.get("lat") is None:
        return 1e9
    p1, p2 = math.radians(a["lat"]), math.radians(b["lat"])
    dp, dl = p2 - p1, math.radians(b["lng"] - a["lng"])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


def where(v) -> str:
    parts = [v.get("city") or ""]
    if v.get("country") == "US":
        parts.append(v.get("region") or "")
    else:
        parts.append(v.get("country_name") or v.get("country") or "")
    return ", ".join(p for p in parts if p)


def load():
    places = {}
    for f in sorted(FIELD.glob("*/index.html")):
        s = f.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="venue-data">(.*?)</script>', s, re.S)
        if not m:
            continue
        v = json.loads(m.group(1))
        v["_path"] = f
        # cards the page already links (= animals the page features), in page order
        body = strip_block(s, "explore")
        seen = []
        for cid in re.findall(r'href="/field-pack/cards/([a-z0-9-]+)/', body):
            if cid not in seen and (CARDS / cid / "index.html").exists():
                seen.append(cid)
        v["_cards"] = seen
        places[v["slug"]] = v
    cards = {}
    for f in sorted(CARDS.glob("*/index.html")):
        s = f.read_text(encoding="utf-8")
        m = re.search(r'class="card-page-photo"[^>]*\salt="([^"]+)"', s) or re.search(r"<h1>(.*?)</h1>", s, re.S)
        name = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else f.parent.name
        name = re.sub(r"^[^\w(]+", "", name).strip()
        cards[f.parent.name] = {"name": html.unescape(name), "path": f}
    return places, cards


def card_anchor(name: str) -> str:
    return f"{name} card"


def place_block(v, places, cards):
    slug, grp = v["slug"], GROUP[v["type"]]
    # animals to find first: up to 4 cards the page already features
    feat = v["_cards"][:4]
    # places: up to 3 closest of any type within 350 km, then nearest same group; total 5
    others = [p for p in places.values() if p["slug"] != slug]
    near = sorted((p for p in others if km(v, p) <= 350), key=lambda p: km(v, p))[:3]
    picks = list(near)
    for p in sorted((p for p in others if GROUP[p["type"]] == grp), key=lambda p: (km(v, p), p["slug"])):
        if len(picks) >= 5:
            break
        if p not in picks:
            picks.append(p)
    plabel = "Nearby and similar places" if near else f"More {HUB[v['type']][2]} to explore"
    pr_href, pr_text = PRINTABLE[grp]
    out = ['\n    <section class="kz-explore no-print" id="explore-more" aria-labelledby="explore-more-heading">',
           f'\n      <h2 id="explore-more-heading">Explore more from {E(v["name"])}</h2>',
           '\n      <div class="kz-explore-grid">']
    if feat:
        out.append('\n        <div class="kz-explore-col"><h3>Animals to find first</h3><ul>')
        for cid in feat:
            out.append(f'<li><a href="/field-pack/cards/{cid}/" data-related-link="card">{E(card_anchor(cards[cid]["name"]))}</a></li>')
        out.append("</ul></div>")
    out.append(f'\n        <div class="kz-explore-col"><h3>{plabel}</h3><ul>')
    for p in picks:
        out.append(f'<li><a href="/field-pack/{p["slug"]}/" data-related-link="place">{E(p["name"])}</a> <small>{E(where(p))}</small></li>')
    out.append("</ul></div>")
    out.append('\n        <div class="kz-explore-col"><h3>Print for the trip</h3><ul>')
    out.append(f'<li><a href="{pr_href}" data-related-link="printable">{E(pr_text)}</a></li>')
    hub, hub_label, plural = HUB[v["type"]]
    out.append(f'<li><a href="{hub}" data-related-link="hub">All {E(plural)} with kid hunts</a></li>')
    out.append("</ul></div>\n      </div>\n    </section>\n")
    return "".join(out), feat, picks


def breadcrumb_ld(items):
    return ('<script type="application/ld+json">' + json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u}
                            for i, (n, u) in enumerate(items)]}, ensure_ascii=False) + "</script>")


def ensure_tags(s: str) -> str:
    if CSS_TAG not in s:
        s = s.replace("</head>", f"  {CSS_TAG}\n</head>", 1)
    if JS_TAG not in s:
        s = re.sub(r'(<script src="/shell/shell\.js\?v=\d+"></script>)', lambda m: m.group(1) + "\n  " + JS_TAG, s, count=1)
    return s


def do_places(places, cards):
    report = {}
    for v in places.values():
        f = v["_path"]
        s = f.read_text(encoding="utf-8")
        for n in ("explore", "crumb", "crumb-ld"):
            s = strip_block(s, n)
        hub, hub_label, _ = HUB[v["type"]]
        # visible breadcrumb
        crumb = (f'<a href="/start/" data-related-link="breadcrumb">KidZooKit</a>\n      <span aria-hidden="true"> / </span>\n      ')
        s, n1 = re.subn(r'(<nav class="seo-crumbs no-print" aria-label="Breadcrumb">\s*)(<a href="/field-pack/">All places</a>\s*<span aria-hidden="true"> / </span>\s*)(<span(?: aria-current="page")?>)',
                        lambda m: m.group(1) + wrap("crumb", crumb) + m.group(2) + wrap("crumb", f'<a href="{hub}" data-related-link="breadcrumb">{hub_label}</a>\n      <span aria-hidden="true"> / </span>\n      ') + '<span aria-current="page">',
                        s, count=1)
        # JSON-LD
        ld = breadcrumb_ld([("KidZooKit", "/start/"), ("All places", "/field-pack/"), (hub_label, hub), (v["name"], f"/field-pack/{v['slug']}/")])
        s = s.replace("</head>", "  " + wrap("crumb-ld", ld) + "\n</head>", 1)
        block, feat, picks = place_block(v, places, cards)
        s, n2 = re.subn(r'(\n\s*<p class="seo-official)', lambda m: "\n    " + wrap("explore", block) + m.group(1), s, count=1)
        if not (n1 and n2):
            raise SystemExit(f"anchor not found in {f} crumb={n1} explore={n2}")
        s = ensure_tags(s)
        f.write_text(s, encoding="utf-8")
        report[v["slug"]] = {"cards": feat, "places": [p["slug"] for p in picks]}
    return report


def do_cards(places, cards):
    by_card = {cid: [] for cid in cards}
    for v in places.values():
        for cid in v["_cards"]:
            by_card[cid].append(v)
    rank = {"verified": 0, "high": 1}
    report = {}
    for cid, c in cards.items():
        f = c["path"]
        s = f.read_text(encoding="utf-8")
        for n in ("where", "more-cards", "crumb", "crumb-ld"):
            s = strip_block(s, n)
        name = c["name"]
        # crumb: KidZooKit · Cards · <Name>
        s, n1 = re.subn(r'(<p class="card-page-crumbs"><a href="/start/">KidZooKit</a> · <a href="/field-pack/cards/">Cards</a>)',
                        lambda m: m.group(1) + wrap("crumb", f' · <span aria-current="page">{E(name)}</span>'), s, count=1)
        ld = breadcrumb_ld([("KidZooKit", "/start/"), ("Cards", "/field-pack/cards/"), (name, f"/field-pack/cards/{cid}/")])
        s = s.replace("</head>", "  " + wrap("crumb-ld", ld) + "\n</head>", 1)
        main_end = s.rfind("</main>")
        body = s[:main_end]
        linked = set(re.findall(r'href="/field-pack/([a-z0-9-]+)/"', body))
        def pr(v):
            item = next((i for i in v.get("items", []) if (i.get("catalog_id") or "").replace("_", "-") == cid), {})
            return (rank.get(item.get("presence"), 2), 0 if v.get("country") == "US" else 1, v["name"])
        hosts = sorted((v for v in by_card[cid] if v["slug"] not in linked), key=pr)
        extra = ""
        if hosts:
            shown = hosts[:8]
            types = [GROUP[v["type"]] for v in hosts]
            top = max(set(types), key=types.count)
            hub, _, plural = HUB[{"zoo": "zoo", "aquarium": "aquarium", "museum": "museum", "park": "national_park"}[top]]
            li = "".join(f'<li><a href="/field-pack/{v["slug"]}/" data-related-link="place">{E(v["name"])}</a> <small>{E(where(v))}</small></li>' for v in shown)
            more = f'<li class="kz-see-all"><a href="{hub}" data-related-link="see_all">See all {E(plural)}</a></li>'
            first = name.split()[0]
            low = name if first in PROPER else name[0].lower() + name[1:]
            title = f"Where to see the {low}" if not cid.startswith(("cm-", "sci-", "cuyahoga")) else f"Where to find {name}"
            extra += "\n      " + wrap("where", f'<nav class="kz-where no-print" aria-label="{E(title)}"><h2>{E(title)}</h2><ul>{li}{more}</ul></nav>')
        tn = len(re.findall(r'class="card-try-next-link" href="/field-pack/cards/', body))
        mc = []
        if tn < 3:
            co = {}
            for v in by_card[cid]:
                for o in v["_cards"]:
                    if o != cid:
                        co[o] = co.get(o, 0) + 1
            mc = [o for o, _ in sorted(co.items(), key=lambda kv: (-kv[1], kv[0]))][:4]
            if len(mc) < 3:  # thin co-occurrence: borrow cards from places of the same type
                grps = {GROUP[v["type"]] for v in by_card[cid]}
                co2 = {}
                for v in places.values():
                    if GROUP[v["type"]] in grps:
                        for o in v["_cards"]:
                            if o != cid and o not in mc:
                                co2[o] = co2.get(o, 0) + 1
                mc += [o for o, _ in sorted(co2.items(), key=lambda kv: (-kv[1], kv[0]))][: 4 - len(mc)]
            if mc:
                li = "".join(f'<li><a href="/field-pack/cards/{o}/" data-related-link="card">{E(card_anchor(cards[o]["name"]))}</a></li>' for o in mc)
                extra += "\n      " + wrap("more-cards", f'<nav class="kz-where kz-more-cards no-print" aria-label="More cards"><h2>More cards to try</h2><ul>{li}</ul></nav>')
        if extra:
            s = s[:main_end].rstrip() + extra + "\n    " + s[main_end:]
        if not n1:
            raise SystemExit(f"card crumb anchor missing in {f}")
        s = ensure_tags(s)
        f.write_text(s, encoding="utf-8")
        report[cid] = {"places": [v["slug"] for v in hosts[:8]], "hosts_total": len(hosts), "more_cards": mc, "try_next": tn}
    return report


def do_start(places):
    f = STATIC / "start" / "index.html"
    s = strip_block(f.read_text(encoding="utf-8"), "start-trips")
    links = '<span aria-hidden="true"> · </span>'.join(
        f'<a href="/field-pack/{slug}/" data-related-link="start_trip">{E(places[slug]["name"])}</a>' for slug in START_TRIPS)
    line = f'\n    ' + wrap("start-trips", f'<p class="start-open-cards start-popular-trips"><span class="start-open-label">Popular trips:</span>\n      {links}\n    </p>')
    s, n = re.subn(r'(<nav class="start-chapter-pills" aria-label="Going this week">.*?</nav>)', lambda m: m.group(1) + line, s, count=1, flags=re.S)
    if not n:
        raise SystemExit("start anchor missing")
    if JS_TAG not in s:
        s = re.sub(r'(<script src="/shell/shell\.js\?v=\d+"></script>)', lambda m: m.group(1) + "\n  " + JS_TAG, s, count=1)
    f.write_text(s, encoding="utf-8")


def main():
    places, cards = load()
    rp = do_places(places, cards)
    rc = do_cards(places, cards)
    do_start(places)
    if "--report" in sys.argv:
        print(json.dumps({"places": rp, "cards": rc}, indent=1))
    else:
        print(f"places {len(rp)} · cards {len(rc)} · start 1")


if __name__ == "__main__":
    main()
