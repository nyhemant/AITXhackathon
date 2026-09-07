"""Animal / sea-life cards open Watch Live in-page — no outbound zoo cams."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from generate_bdo_seo import (  # noqa: E402
    CTA_WATCH_LIVE,
    card_watch_href,
    vft_has_inpage_media,
    watch_links_html,
)

FP = REPO / "static" / "field-pack"
LION = FP / "cards" / "african-lion" / "index.html"
GIRAFFE = FP / "cards" / "reticulated-giraffe" / "index.html"
JELLY = FP / "cards" / "jellyfish" / "index.html"
CHEETAH = FP / "cards" / "cheetah" / "index.html"
DINO = FP / "cards" / "sci-dinosaur" / "index.html"
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

    def test_cheetah_hides_watch_live_and_has_no_outbound_cam(self):
        html = CHEETAH.read_text(encoding="utf-8")
        main = _main(html)
        self.assertNotIn("card-watch-live", main)
        self.assertNotIn("Watch Live", main)
        self.assertNotIn('class="seo-watch-row"', main)
        self.assertNotIn("Live cam", main)
        self.assertNotIn("sandiegozoo.org", main)
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

    def test_player_keeps_card_session_on_site(self):
        js = VFT_JS.read_text(encoding="utf-8")
        self.assertIn("function fromCard(", js)
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
            self.assertIn("virtual-venue.js?v=99", html)
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
        self.assertIn('q.set("habitat", hid)', js)
        walk = body("walkList")
        self.assertIn("fromCard()", walk)
        self.assertIn("cardFocusId()", walk)
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
