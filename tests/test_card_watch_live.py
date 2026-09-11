"""Animal / sea-life cards open Watch Live in-page — no outbound zoo cams."""

from __future__ import annotations

import json
import re
import sys
import unittest
from html import unescape
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from generate_bdo_seo import (  # noqa: E402
    CTA_WATCH_LIVE,
    card_watch_href,
    habitat_films,
    load_vft_by_card,
    vft_can_watch_live,
    vft_has_inpage_media,
    watch_links_html,
)

FP = REPO / "static" / "field-pack"
LION = FP / "cards" / "african-lion" / "index.html"
GIRAFFE = FP / "cards" / "reticulated-giraffe" / "index.html"
JELLY = FP / "cards" / "jellyfish" / "index.html"
CHEETAH = FP / "cards" / "cheetah" / "index.html"
KOALA = FP / "cards" / "koala" / "index.html"
WARTHOG = FP / "cards" / "warthog" / "index.html"
OSTRICH = FP / "cards" / "ostrich" / "index.html"
DINO = FP / "cards" / "sci-dinosaur" / "index.html"

# Zoo film-library overlays — not tour habitats. Watch Live stays hidden (PR #207).
# Aquarium film-library cards with film overlay via ensureDeepLinkHabitat.
LIBRARY_ONLY_CARDS = (
    ("koala", "zoo"),
    ("chimpanzee", "zoo"),
    ("orangutan", "zoo"),
    ("red-panda", "zoo"),
    ("cheetah", "zoo"),
    ("galapagos-tortoise", "zoo"),
    ("polar-bear", "zoo"),
    ("ring-tailed-lemur", "zoo"),
    ("two-toed-sloth", "zoo"),
    ("zebra", "zoo"),
)
AQUARIUM_LIBRARY_WATCH_CARDS = (
    "manta-ray",
    "whale-shark",
    "kelp-forest",
    "cuttlefish",
    "puffin",
    "sea-otter",
)
MISSING_HABITAT_CARDS = tuple(cid for cid, _tab in LIBRARY_ONLY_CARDS)
VFT_JS = FP / "js" / "virtual-venue.js"
VFT_PAGES = (
    FP / "virtual-field-trip" / "index.html",
    FP / "virtual-zoo" / "index.html",
)

OUTBOUND_CAM = (
    "nationalzoo.si.edu",
    "houstonzoo.org",
    "sandiegozoo.org",
    "sdzsafaripark.org",
    "montereybayaquarium.org",
)

HREF_RE = re.compile(r"""\bhref\s*=\s*(['"])(.*?)\1""", re.I)
WATCH_TAG_RE = re.compile(
    r'<a[^>]+class="[^"]*(?:card-watch-live|card-page-photo-link)[^"]*"[^>]*>',
    re.I,
)
HABITAT_RE = re.compile(r"#habitat=([^&\"'\s]+)")
VDIR = FP / "data" / "virtual-venues"


def _tour_habitat_ids() -> set[str]:
    ids: set[str] = set()
    for name in ("virtual-zoo.json", "virtual-aquarium.json"):
        data = json.loads((VDIR / name).read_text(encoding="utf-8"))
        for h in data.get("habitats") or []:
            hid = str(h.get("id") or "").strip()
            cid = str(h.get("cardId") or "").strip()
            if hid:
                ids.add(hid)
            if cid:
                ids.add(cid)
    return ids


def _playable_watch_ids() -> set[str]:
    """Tour habitats plus aquarium film-library overlays the player can inject."""
    ids = _tour_habitat_ids()
    data = json.loads((VDIR / "aquarium-film-library.json").read_text(encoding="utf-8"))
    for card in data.get("cards") or []:
        cid = str(card.get("cardId") or "").strip()
        if not cid:
            continue
        films = card.get("videos") if isinstance(card.get("videos"), list) else []
        has_film = any(isinstance(v, dict) and str(v.get("url") or "").strip() for v in films)
        video = card.get("video") if isinstance(card.get("video"), dict) else {}
        if str(video.get("url") or "").strip():
            has_film = True
        cam = card.get("cam") if isinstance(card.get("cam"), dict) else {}
        has_embed = bool(str(cam.get("embed") or "").strip())
        if has_film or has_embed:
            ids.add(cid)
    return ids


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


def _watch(html: str) -> str:
    return html.split('class="seo-watch-row"', 1)[1].split("</p>", 1)[0]


class CardWatchLiveTests(unittest.TestCase):
    def test_lion_watch_live_is_same_origin_virtual_zoo(self):
        html = LION.read_text(encoding="utf-8")
        main = _main(html)
        watch = _watch(html)
        self.assertIn(CTA_WATCH_LIVE, watch)
        self.assertIn('class="btn btn-primary card-watch-live"', watch)
        self.assertIn("/field-pack/virtual-zoo/?from=card#habitat=african-lion", watch)
        self.assertIn("Live from Smithsonian National Zoo", watch)
        self.assertNotIn('target="_blank"', watch)
        for host in OUTBOUND_CAM:
            self.assertNotIn(host, main)
        actions = main.split('class="card-page-actions"', 1)[1]
        self.assertIn("card-watch-live", actions)
        self.assertIn("#habitat=african-lion", actions)

    def test_giraffe_and_jellyfish_stay_on_site(self):
        giraffe = GIRAFFE.read_text(encoding="utf-8")
        jelly = JELLY.read_text(encoding="utf-8")
        self.assertIn("/field-pack/virtual-zoo/?from=card#habitat=reticulated-giraffe", giraffe)
        self.assertIn("Live from Houston Zoo", giraffe)
        self.assertNotIn("houstonzoo.org", _main(giraffe))
        self.assertIn("/field-pack/virtual-field-trip/?tab=aquarium&from=card#habitat=jellyfish", jelly)
        self.assertIn("Watch Live", jelly)
        self.assertNotIn("montereybayaquarium.org", _main(jelly))

    def test_library_only_animals_hide_watch_live(self):
        vft = load_vft_by_card()
        for cid, tab in LIBRARY_ONLY_CARDS:
            rec = vft[cid]
            self.assertTrue(rec.get("library_only"), cid)
            self.assertFalse(vft_can_watch_live(rec), cid)
            html = (FP / "cards" / cid / "index.html").read_text(encoding="utf-8")
            main = _main(html)
            self.assertNotIn("card-watch-live", main, cid)
            self.assertNotIn(CTA_WATCH_LIVE, main, cid)
            self.assertNotIn('class="seo-watch-row"', main, cid)
            self.assertNotIn("card-page-photo-link", main, cid)
            for host in OUTBOUND_CAM:
                self.assertNotIn(host, main, cid)
            actions = main.split('class="card-page-actions"', 1)[1]
            self.assertNotIn("card-watch-live", actions, cid)
            if tab == "zoo":
                href = f"/field-pack/virtual-zoo/?from=card#habitat={cid}"
            else:
                href = f"/field-pack/virtual-field-trip/?tab=aquarium&from=card#habitat={cid}"
            self.assertNotIn(href, actions, cid)
            self.assertNotIn(f"#habitat={cid}", main, cid)

    def test_aquarium_library_cards_keep_watch_live(self):
        """Aquarium-film-library overlays with film are live doors, not dead CTAs."""
        vft = load_vft_by_card()
        for cid in AQUARIUM_LIBRARY_WATCH_CARDS:
            rec = vft[cid]
            self.assertTrue(rec.get("library_only"), cid)
            self.assertEqual(rec.get("tab"), "aquarium", cid)
            self.assertTrue(vft_has_inpage_media(rec), cid)
            self.assertTrue(vft_can_watch_live(rec), cid)
            html = (FP / "cards" / cid / "index.html").read_text(encoding="utf-8")
            main = _main(html)
            href = f"/field-pack/virtual-field-trip/?tab=aquarium&from=card#habitat={cid}"
            self.assertIn("card-watch-live", main, cid)
            self.assertIn(CTA_WATCH_LIVE, main, cid)
            self.assertIn("card-page-photo-link", main, cid)
            self.assertIn(f"#habitat={cid}", main, cid)
            self.assertIn(href, main.replace("&amp;", "&"), cid)
            actions = main.split('class="card-page-actions"', 1)[1]
            self.assertIn("card-watch-live", actions, cid)

    def test_watch_live_hrefs_use_real_zoo_or_aquarium_habitats(self):
        """ParentTest: no card-watch-live / hero link to a missing VFT habitat."""
        real = _playable_watch_ids()
        self.assertIn("manta-ray", real)
        self.assertIn("whale-shark", real)
        self.assertIn("stingray", real)
        self.assertNotIn("manta-ray", _tour_habitat_ids())
        dead: list[str] = []
        for path in sorted((FP / "cards").glob("*/index.html")):
            html = path.read_text(encoding="utf-8")
            if '<main class="card-page">' not in html:
                continue
            main = _main(html)
            for tag in WATCH_TAG_RE.findall(main):
                href_m = HREF_RE.search(tag)
                if not href_m:
                    continue
                href = unescape(href_m.group(2))
                hid_m = HABITAT_RE.search(href)
                if not hid_m:
                    dead.append(f"{path.parent.name}: {href} (no habitat)")
                    continue
                hid = hid_m.group(1)
                if hid not in real:
                    dead.append(f"{path.parent.name}: #{hid} not in zoo/aquarium habitats or film library")
        self.assertEqual(dead, [])

    def test_missing_habitat_hides_watch_live(self):
        vft = load_vft_by_card()
        for cid in MISSING_HABITAT_CARDS:
            rec = vft[cid]
            self.assertTrue(rec.get("library_only"), cid)
            self.assertFalse(vft_can_watch_live(rec), cid)
            html = (FP / "cards" / cid / "index.html").read_text(encoding="utf-8")
            main = _main(html)
            self.assertNotIn("card-watch-live", main, cid)
            self.assertNotIn("Watch Live", main, cid)
            self.assertNotIn('class="seo-watch-row"', main, cid)
            self.assertNotIn("card-page-photo-link", main, cid)
            actions = main.split('class="card-page-actions"', 1)[1]
            self.assertIn("/field-pack/cards/", actions, cid)
            self.assertNotIn(f"#habitat={cid}", main, cid)

    def test_no_media_animals_stay_buttonless(self):
        vft = load_vft_by_card()
        for path in (WARTHOG, OSTRICH):
            cid = path.parent.name
            rec = vft.get(cid) or {}
            self.assertFalse(vft_has_inpage_media(rec), cid)
            html = path.read_text(encoding="utf-8")
            main = _main(html)
            self.assertNotIn("card-watch-live", main, cid)
            self.assertNotIn("Watch Live", main, cid)
            self.assertNotIn('class="seo-watch-row"', main, cid)
            self.assertNotIn("Live cam", main, cid)
            for host in OUTBOUND_CAM:
                self.assertNotIn(host, main, cid)
            self.assertIn("/field-pack/cards/", main.split('class="card-page-actions"', 1)[1])

    def test_attraction_card_drops_catalog_live_cam(self):
        html = DINO.read_text(encoding="utf-8")
        main = _main(html)
        self.assertNotIn(">Live cam</a>", main)
        self.assertNotIn("/field-pack/virtual-zoo/", main)
        self.assertIn("/field-pack/virtual-field-trip/?tab=natural-history#habitat=sci-dinosaur", main)

    def test_watch_live_helper_hides_cam_only_without_inpage_media(self):
        empty = watch_links_html(
            {"vft": {"cam_url": "https://nationalzoo.si.edu/webcams/lion-cam", "tab": "zoo", "habitat_id": "african-lion"}},
            film_via_vft=True,
            watch_live=True,
        )
        self.assertEqual(empty, "")
        self.assertFalse(vft_has_inpage_media({"cam_url": "https://example.com/cam"}))
        self.assertTrue(vft_has_inpage_media({"film_url": "https://www.youtube.com/watch?v=x"}))
        self.assertTrue(vft_has_inpage_media({"cam_embed": "https://example.com/embed"}))
        self.assertEqual(
            card_watch_href({"tab": "aquarium", "habitat_id": "jellyfish"}),
            "/field-pack/virtual-field-trip/?tab=aquarium&from=card#habitat=jellyfish",
        )
        films = habitat_films(
            {
                "videos": [{"url": "https://www.youtube.com/watch?v=abc", "title": "A"}],
                "video": {"url": "https://www.youtube.com/watch?v=zzz", "title": "Z"},
            }
        )
        self.assertEqual(films[0]["url"], "https://www.youtube.com/watch?v=abc")
        self.assertEqual(habitat_films({"video": {"url": "https://youtu.be/x"}})[0]["url"], "https://youtu.be/x")
        self.assertEqual(habitat_films({"cam": {"url": "https://example.com/cam"}}), [])
        koala = load_vft_by_card()["koala"]
        self.assertTrue(koala["library_only"])
        self.assertTrue(koala["film_url"])
        self.assertEqual(koala["tab"], "zoo")
        self.assertFalse(vft_can_watch_live(koala))
        self.assertEqual(
            card_watch_href(koala),
            "/field-pack/virtual-zoo/?from=card#habitat=koala",
        )
        place = watch_links_html({"vft": koala})
        self.assertEqual(place, "")
        card = watch_links_html({"vft": koala}, film_via_vft=True, watch_live=True)
        self.assertEqual(card, "")
        whale = load_vft_by_card()["whale-shark"]
        self.assertTrue(whale["library_only"])
        self.assertTrue(vft_can_watch_live(whale))
        whale_watch = watch_links_html({"vft": whale}, film_via_vft=True, watch_live=True)
        self.assertIn("card-watch-live", whale_watch)
        self.assertIn("#habitat=whale-shark", whale_watch)
        lion = load_vft_by_card()["african-lion"]
        self.assertFalse(lion.get("library_only"))
        self.assertTrue(vft_has_inpage_media(lion))

    def test_player_keeps_card_session_on_site(self):
        js = VFT_JS.read_text(encoding="utf-8")
        self.assertIn("function fromCard(", js)
        self.assertIn("function overlayLibCard(", js)
        self.assertIn("function ensureDeepLinkHabitat(", js)
        self.assertIn("ensureDeepLinkHabitat(cfg)", js)
        self.assertIn("function syncCardNav(", js)
        self.assertIn("function openCamEmbed(", js)
        self.assertIn('get("from") === "card"', js)
        self.assertIn("Back to card", js)
        self.assertIn("function nextAfter(", js)
        self.assertIn("q.set(\"from\", \"card\")", js)
        self.assertIn("if (fromCard()) {\n      return;\n    }", js)
        for path in VFT_PAGES:
            html = path.read_text(encoding="utf-8")
            self.assertIn('id="vz-card-nav"', html)
            self.assertIn('id="vz-back-card"', html)
            self.assertIn('id="vz-next-stop"', html)
            self.assertIn("virtual-venue.js?v=101", html)
            self.assertIn("virtual-venue.css?v=57", html)

    def test_card_watch_hrefs_are_internal(self):
        for path in (LION, GIRAFFE, JELLY):
            html = path.read_text(encoding="utf-8")
            watch = _watch(html)
            hrefs = HREF_RE.findall(watch)
            self.assertTrue(hrefs, path.name)
            for _, href in hrefs:
                host = (urlparse(href).hostname or "").lower()
                self.assertTrue(href.startswith("/field-pack/"), href)
                self.assertFalse(host)
                self.assertIn("from=card", href)
                self.assertIn("#habitat=", href)

    def test_card_session_keeps_habitat_hash_and_short_trail(self):
        js = VFT_JS.read_text(encoding="utf-8")

        def body(name: str) -> str:
            token = f"function {name}("
            start = js.index(token)
            depth = 0
            i = js.index("{", start)
            for j in range(i, len(js)):
                if js[j] == "{":
                    depth += 1
                elif js[j] == "}":
                    depth -= 1
                    if depth == 0:
                        return js[start : j + 1]
            raise AssertionError(f"unclosed function {name}")

        self.assertIn("function queryHabitat(", js)
        self.assertIn("function cardFocusId(", js)
        self.assertIn("function fullWalkList(", js)
        self.assertIn("function skipTrailVias(", js)
        self.assertIn("function localStopTrail(", js)
        self.assertIn("function refreshCardFocusMap(", js)
        self.assertIn("function syncTourGates(", js)
        self.assertIn("function stampedOnWalk(", js)
        self.assertIn('q.set("habitat", hid)', js)
        walk = body("walkList")
        self.assertIn("fromCard()", walk)
        self.assertIn("cardFocusId()", walk)
        self.assertIn("h.id === focus || h.cardId === focus", walk)
        self.assertIn("return one ? [one] : all", walk)
        nxt = body("nextAfter")
        self.assertIn("fullWalkList()", nxt)
        self.assertNotIn("walkList()", nxt)
        trail = body("zooTrailPoints")
        self.assertIn("skipTrailVias()", trail)
        self.assertIn("localStopTrail(byId)", trail)
        self.assertIn("if (shortPath) return", trail)
        close = body("closeDialog")
        self.assertIn("fromCard()", close)
        self.assertIn("tabUrl(currentTab(), hid || \"\")", close)
        on_hash = body("onHash")
        self.assertIn("queryHabitat()", on_hash)
        self.assertIn("openHabitat(DEFAULT_ZOO_STOP", on_hash)
        self.assertIn("if (fromCard())", on_hash)
        tab = body("tabUrl")
        self.assertIn('q.set("habitat", hid)', tab)
        self.assertIn('hid ? "#habitat=" + encodeURIComponent(hid) : "#" + id', tab)


if __name__ == "__main__":
    unittest.main()
