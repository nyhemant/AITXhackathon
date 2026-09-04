"""Every parent-tappable INTERNAL Field Trip Kit link must resolve.

This is a local/static crawl. It does not fetch houstonzoo.org, YouTube,
NatGeo, or any other live-cam host — those stay out of scope.

What is crawled
---------------
1. Every <a href> in static/field-pack HTML (place pages, card pages, home,
   app.html, type hubs, Virtual Field Trip, print/mission drawers, cards hub).
2. Catalog-derived routes that the outing app actually uses:
   - #/venue/<venueId>
   - #/venue/<venueId>/item/<itemId>
   - /field-pack/<venueId>/
   - /field-pack/cards/<itemId>/  (published card pages only)

Internal vs ignored
-------------------
INTERNAL: paths starting with /, # hashes on 1less/field-pack, relative
links, and https://1less.app/... (same product).
IGNORED: http(s) to other hosts, mailto:, tel:, javascript:.

How a target is judged
----------------------
- The path must return 200 (or a redirect to a real page) from the same
  local server that serves 1less.app.
- #/venue/<id> must be a catalog venue.
- #/venue/<id>/item/<itemId> must pass the same itemOnVenue check as the
  live app. Unknown item hashes must NOT stay on a stale card — they
  rewrite to #/venue/<id> (the outing list).
- In-page hashes (#about, #at-home, #mission, #print, #start-here, …)
  must match an id= on that page.
- Virtual Field Trip #habitat=<animal> : the VFT page itself must load.
  Open Virtual Field Trip uses #habitat=… ; virtual-venue.js opens that
  animal from the hash (deep links skip the sequential “next stop” lock).
  An unknown habitat still loads the VFT page; the dialog stays closed.

Run
---
  python3 -m unittest tests.test_field_pack_internal_links
  python3 -m unittest discover -s tests
"""

from __future__ import annotations

import json
import re
import subprocess
import unittest
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

from busyparent_agent.web import (
    ABOUT_PREFIX,
    DINNER_PATH,
    FIELD_PACK_PREFIX,
    LOGO_ASSETS,
    START_PREFIX,
    WebHandler,
    _SITEMAP_URLS,
    _safe_about_path,
    _safe_field_pack_path,
    _safe_shell_path,
    _safe_start_path,
    _safe_static_root_file,
)


REPO = Path(__file__).resolve().parents[1]
FP = REPO / "static" / "field-pack"
CATALOG_JS = FP / "js" / "catalog.js"
APP_JS = FP / "js" / "app.js"
VFT_JS = FP / "js" / "virtual-venue.js"

SKIP_SCHEMES = ("mailto:", "tel:", "javascript:", "data:")
INTERNAL_HOSTS = {"", "1less.app", "www.1less.app"}
HREF_RE = re.compile(r"""href\s*=\s*(['"])(.*?)\1""", re.I | re.S)
BASE_RE = re.compile(r"""<base\s+[^>]*href\s*=\s*(['"])(.*?)\1""", re.I | re.S)
ID_RE = re.compile(r"""\bid\s*=\s*(['"])(.*?)\1""", re.I)
ITEM_HASH_RE = re.compile(r"^/venue/([^/]+)/item/([^/]+)$")
VENUE_HASH_RE = re.compile(r"^/venue/([^/]+)$")
VFT_TABS = frozenset({"zoo", "aquarium", "natural-history", "science", "parks"})
VFT_JSON = {
    "zoo": "virtual-zoo.json",
    "aquarium": "virtual-aquarium.json",
    "natural-history": "virtual-nhm.json",
    "science": "virtual-science.json",
    "parks": "virtual-parks.json",
}
DALLAS_CHAIN = (
    ("reticulated-giraffe", "/field-pack/cards/african-elephant/?from=dallas-zoo"),
    ("african-elephant", "/field-pack/cards/african-lion/?from=dallas-zoo"),
)


def _load_catalog() -> dict:
    js = r"""
const fs = require("fs");
const vm = require("vm");
const window = {};
vm.runInNewContext(fs.readFileSync(process.argv[1], "utf8"), { window });
const venues = window.FIELD_PACK_VENUES || {};
const catalog = window.FIELD_PACK_CATALOG || {};
const out = { venueIds: Object.keys(venues), itemIds: Object.keys(catalog), venueItems: {} };
for (const [vid, v] of Object.entries(venues)) {
  const ids = new Set(v.animalIds || []);
  for (const it of v.items || []) if (it && it.id) ids.add(it.id);
  out.venueItems[vid] = [...ids];
}
process.stdout.write(JSON.stringify(out));
"""
    proc = subprocess.run(
        ["node", "-e", js, str(CATALOG_JS)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


def _resolve_item_hash(venue_id: str, item_id: str) -> str:
    """Same outcome as app.js showItem + itemOnVenue (hash after route)."""
    js = r"""
const fs = require("fs");
const vm = require("vm");
const window = {};
vm.runInNewContext(fs.readFileSync(process.argv[1], "utf8"), { window });
const appSrc = fs.readFileSync(process.argv[2], "utf8");
const fn = appSrc.match(/function itemOnVenue\(venue, itemId\) \{[\s\S]*?\n  \}\n/);
if (!fn) throw new Error("itemOnVenue not found");
const itemOnVenue = vm.runInNewContext(fn[0] + "\nitemOnVenue;");
const venueId = process.argv[3];
const itemId = process.argv[4];
const venue = window.FIELD_PACK_VENUES[venueId];
const item = window.FIELD_PACK_CATALOG[itemId];
if (!venue || !itemOnVenue(venue, itemId) || !item) {
  process.stdout.write(venue ? ("#/venue/" + venue.id) : "#/venue/" + venueId);
} else {
  process.stdout.write("#/venue/" + venue.id + "/item/" + itemId);
}
"""
    proc = subprocess.run(
        ["node", "-e", js, str(CATALOG_JS), str(APP_JS), venue_id, item_id],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def _is_internal_href(raw: str) -> bool:
    href = (raw or "").strip()
    if not href or href.startswith(SKIP_SCHEMES):
        return False
    if href.startswith(("http://", "https://")):
        host = (urlsplit(href).hostname or "").lower()
        return host in INTERNAL_HOSTS
    return True


def _page_url(html_path: Path) -> str:
    rel = html_path.relative_to(FP).as_posix()
    if rel == "index.html":
        return "/field-pack/"
    if rel.endswith("/index.html"):
        return "/field-pack/" + rel[: -len("index.html")]
    return "/field-pack/" + rel


def _resolve_href(raw: str, page: str, base: str) -> str:
    href = raw.strip()
    if href.startswith(("http://", "https://")):
        parts = urlsplit(href)
        out = parts.path or "/"
        if parts.query:
            out += "?" + parts.query
        if parts.fragment:
            out += "#" + parts.fragment
        return out
    if href.startswith("#"):
        return page.split("#", 1)[0] + href
    if href.startswith("/"):
        return href
    origin = base if base else page
    return urljoin(origin, href)


def _collect_html_hrefs() -> list[dict]:
    found = []
    for path in sorted(FP.rglob("*.html")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        page = _page_url(path)
        bm = BASE_RE.search(text)
        base = bm.group(2).strip() if bm else page
        if base.startswith("http"):
            base = urlsplit(base).path or "/field-pack/"
        if not base.endswith("/") and "." not in Path(base).name:
            base += "/"
        for m in HREF_RE.finditer(text):
            raw = m.group(2).strip()
            if not _is_internal_href(raw):
                continue
            found.append(
                {
                    "source": str(path.relative_to(REPO)),
                    "raw": raw,
                    "resolved": _resolve_href(raw, page, base),
                    "page": page,
                }
            )
    return found


def _published_card_ids() -> set[str]:
    return {p.parent.name for p in (FP / "cards").glob("*/index.html")}


def _vft_habitats() -> dict[str, set[str]]:
    out = {}
    for tab, fname in VFT_JSON.items():
        data = json.loads((FP / "data" / "virtual-venues" / fname).read_text(encoding="utf-8"))
        ids = set()
        for h in data.get("habitats") or []:
            if h.get("id"):
                ids.add(h["id"])
            if h.get("cardId"):
                ids.add(h["cardId"])
        out[tab] = ids
    return out


def _ids_on_page(html: str) -> set[str]:
    return {m.group(2) for m in ID_RE.finditer(html)}


def _served_status(path: str) -> int:
    """Same outcomes as WebHandler.do_GET, without opening a socket."""
    if path in {"/", "/index.html"}:
        return 302
    if path in _SITEMAP_URLS or _safe_static_root_file(path) is not None:
        return 200
    if path in {DINNER_PATH, DINNER_PATH + "/"}:
        return 200
    if path == START_PREFIX:
        return 301
    if _safe_start_path(path) is not None:
        return 200
    if path == ABOUT_PREFIX:
        return 301
    if _safe_about_path(path) is not None:
        return 200
    if path == FIELD_PACK_PREFIX:
        return 301
    if path.startswith(FIELD_PACK_PREFIX + "/places/"):
        slug = path[len(FIELD_PACK_PREFIX + "/places/") :]
        if slug.endswith(".html"):
            slug = slug[: -len(".html")]
        slug = slug.strip("/")
        if slug and "/" not in slug and ".." not in slug:
            return 301
    logo = LOGO_ASSETS.get(path.lstrip("/"))
    if logo is not None:
        return 200 if logo.exists() else 404
    if _safe_shell_path(path) is not None:
        return 200
    if _safe_field_pack_path(path) is not None:
        return 200
    return 404


def _served_body(path: str) -> str:
    if path in {DINNER_PATH, DINNER_PATH + "/"}:
        return "<html></html>"
    fp = _safe_field_pack_path(path)
    if fp is not None:
        return fp.read_text(encoding="utf-8", errors="ignore")
    return ""


class FieldPackInternalLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = _load_catalog()
        cls.hrefs = _collect_html_hrefs()
        cls.published_cards = _published_card_ids()
        cls.vft_habitats = _vft_habitats()

    def _http_status(self, path: str) -> int:
        return _served_status(path)

    def _body_for(self, path: str) -> str:
        return _served_body(path)

    def _catalog_targets(self) -> list[str]:
        extra = []
        for vid in self.catalog["venueIds"]:
            extra.append(f"/field-pack/{vid}/")
            extra.append(f"/field-pack/#/venue/{vid}")
            extra.append(f"/field-pack/app.html#/venue/{vid}")
            for iid in self.catalog["venueItems"].get(vid, []):
                extra.append(f"/field-pack/app.html#/venue/{vid}/item/{iid}")
        for iid in self.published_cards:
            extra.append(f"/field-pack/cards/{iid}/")
        return extra

    def _judge(self, target: str, sources: list[str]) -> list[str]:
        parts = urlsplit(target)
        path = parts.path or "/"
        frag = unquote(parts.fragment or "")
        code = self._http_status(path)
        if code not in {200, 301, 302}:
            src = sources[:2]
            return [f"{code} {target} from {src}"]
        if not frag:
            return []
        m = ITEM_HASH_RE.match(frag)
        if m:
            vid, iid = m.group(1), m.group(2)
            on_venue = iid in self.catalog["venueItems"].get(vid, [])
            in_catalog = iid in self.catalog["itemIds"]
            venue_ok = vid in self.catalog["venueIds"]
            if not (venue_ok and on_venue and in_catalog):
                landed = f"#/venue/{vid}" if venue_ok else f"#/venue/{vid}"
                return [
                    f"item hash {target} does not stay on a real card "
                    f"(itemOnVenue → {landed}) from {sources[:2]}"
                ]
            return []
        m = VENUE_HASH_RE.match(frag)
        if m:
            if m.group(1) not in self.catalog["venueIds"]:
                return [f"unknown venue hash {target} from {sources[:2]}"]
            return []
        if frag.startswith("habitat="):
            # VFT page already 200'd. Deep-link open is asserted separately.
            return []
        if frag in VFT_TABS:
            return []
        html = self._body_for(path)
        if frag not in _ids_on_page(html):
            return [f"missing id #{frag} on {path} ({target}) from {sources[:2]}"]
        return []

    def test_every_internal_href_and_catalog_route_resolves(self):
        self.assertGreater(len(self.hrefs), 500)
        self.assertGreater(len(self.catalog["venueIds"]), 200)
        self.assertGreater(len(self.published_cards), 40)

        by_target: dict[str, list[str]] = {}
        for h in self.hrefs:
            by_target.setdefault(h["resolved"], []).append(h["source"])
        for t in self._catalog_targets():
            by_target.setdefault(t, [])

        failures = []
        for target, sources in sorted(by_target.items()):
            failures.extend(self._judge(target, sources))

        self.assertEqual(failures, [], "\n".join(failures[:80]))

    def test_unknown_item_hash_does_not_stay_on_stale_card(self):
        js = APP_JS.read_text(encoding="utf-8")
        self.assertIn("function itemOnVenue(venue, itemId)", js)
        self.assertIn("if (!venueEarly || !itemOnVenue(venueEarly, itemId))", js)
        self.assertIn("return showOuting(", js)

        good = _resolve_item_hash("dallas-zoo", "reticulated-giraffe")
        self.assertEqual(good, "#/venue/dallas-zoo/item/reticulated-giraffe")

        unknown = _resolve_item_hash("dallas-zoo", "not-a-real-animal-xyz")
        self.assertEqual(unknown, "#/venue/dallas-zoo")
        self.assertNotIn("/item/", unknown)

        # Seahorse is a real catalog card, but not a Dallas Zoo stop.
        off_list = _resolve_item_hash("dallas-zoo", "seahorse")
        self.assertEqual(off_list, "#/venue/dallas-zoo")

    def test_dallas_start_here_next_chain(self):
        dallas = (FP / "dallas-zoo" / "index.html").read_text(encoding="utf-8")
        visible = dallas.split('id="venue-data"', 1)[0]
        start = visible.split('id="route90-heading"', 1)[1].split("</section>", 1)[0]
        self.assertIn("/field-pack/cards/reticulated-giraffe/?from=dallas-zoo", start)
        self.assertIn("/field-pack/cards/african-elephant/?from=dallas-zoo", start)
        self.assertIn("/field-pack/cards/african-lion/?from=dallas-zoo", start)

        giraffe = (FP / "cards" / "reticulated-giraffe" / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="/field-pack/cards/african-elephant/?from=dallas-zoo"', giraffe)
        self.assertIn("Next: African elephant", giraffe)

        elephant = (FP / "cards" / "african-elephant" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-next-from="dallas-zoo"', elephant)
        self.assertIn('href="/field-pack/cards/african-lion/?from=dallas-zoo"', elephant)
        self.assertIn("Next: African lion", elephant)

        for cid, href in DALLAS_CHAIN:
            path = urlsplit(href).path
            self.assertEqual(self._http_status(path), 200, f"{cid} next {href}")

        next_hrefs = []
        for card in sorted((FP / "cards").glob("*/index.html")):
            html = card.read_text(encoding="utf-8")
            block = html
            if "card-page-next" not in block and "Next:" not in block:
                continue
            for m in HREF_RE.finditer(block):
                raw = m.group(2)
                if "/field-pack/cards/" in raw and card.parent.name not in raw:
                    next_hrefs.append((card.parent.name, raw))
                    if _is_internal_href(raw):
                        resolved = _resolve_href(raw, f"/field-pack/cards/{card.parent.name}/", "/field-pack/")
                        self.assertEqual(
                            self._http_status(urlsplit(resolved).path),
                            200,
                            f"Next on {card.parent.name} → {raw}",
                        )
        self.assertTrue(any("african-elephant" in h for _, h in next_hrefs))

    def test_vft_habitat_hash_opens_or_still_loads_page(self):
        vft = "/field-pack/virtual-field-trip/"
        self.assertEqual(self._http_status(vft), 200)
        html = self._body_for(vft)
        self.assertIn("Virtual Field Trip", html)

        js = VFT_JS.read_text(encoding="utf-8")
        self.assertIn("fromHash", js)
        self.assertIn("habitat=", js)
        self.assertIn("function onHash()", js)

        habitat_hrefs = [
            h
            for h in self.hrefs
            if "#habitat=" in h["resolved"] and "virtual-field-trip" in h["resolved"]
        ]
        self.assertGreater(len(habitat_hrefs), 10)
        missing = []
        for h in habitat_hrefs:
            parts = urlsplit(h["resolved"])
            hid = unquote(parts.fragment.split("=", 1)[1])
            tab = "zoo"
            qm = re.search(r"(?:^|&)tab=([^&]+)", parts.query or "")
            if qm:
                tab = unquote(qm.group(1))
            known = self.vft_habitats.get(tab) or set()
            if hid not in known and hid not in set().union(*self.vft_habitats.values()):
                missing.append(f"{hid} from {h['source']}")
            self.assertEqual(self._http_status(parts.path), 200, h["resolved"])
        self.assertEqual(missing, [], "VFT #habitat= ids must exist in that tab's map JSON")

    def test_local_server_agrees_on_flagship_paths(self):
        """Spot-check the real WebHandler so the crawl is not only file-exists."""

        class FakeHandler(WebHandler):
            def __init__(self, path):
                self.path = path
                self.headers = {}
                self._code = None
                self.wfile = _Buf()

            def send_response(self, code, message=None):
                self._code = code

            def send_error(self, code, message=None):
                self._code = code

            def send_header(self, k, v):
                return

            def end_headers(self):
                return

            def log_message(self, format, *args):
                return

        samples = {
            "/field-pack/": 200,
            "/field-pack/dallas-zoo/": 200,
            "/field-pack/cards/reticulated-giraffe/": 200,
            "/field-pack/virtual-field-trip/": 200,
            "/field-pack/app.html": 200,
            "/dinner": 200,
            "/start/": 200,
            "/start": 301,
            "/about/": 200,
            "/about": 301,
            "/field-pack": 301,
            "/": 302,
            "/field-pack/cards/acad-cadillac-view/": 404,
            "/field-pack/not-a-real-place/": 404,
        }
        for path, expect in samples.items():
            h = FakeHandler(path)
            h.do_GET()
            self.assertEqual(h._code, expect, path)
            self.assertEqual(_served_status(path), expect, path)

    def test_unpublished_cards_retarget_to_outing_hash(self):
        import sys

        sys.path.insert(0, str(REPO / "scripts"))
        from generate_bdo_seo import item_public_href, published_card_ids

        self.assertIn("reticulated-giraffe", published_card_ids())
        self.assertNotIn("acad-cadillac-view", published_card_ids())
        self.assertEqual(
            item_public_href("reticulated-giraffe", "dallas-zoo"),
            "/field-pack/cards/reticulated-giraffe/",
        )
        self.assertEqual(
            item_public_href("acad-cadillac-view", "acadia"),
            "/field-pack/app.html#/venue/acadia/item/acad-cadillac-view",
        )
        self.assertEqual(
            item_public_href("african-elephant", "dallas-zoo", extra_query="from=dallas-zoo"),
            "/field-pack/cards/african-elephant/?from=dallas-zoo",
        )


class _Buf:
    def __init__(self):
        self._b = bytearray()

    def write(self, data):
        self._b.extend(data)

    def getvalue(self):
        return bytes(self._b)


if __name__ == "__main__":
    unittest.main()
