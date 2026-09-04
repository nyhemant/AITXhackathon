"""Virtual Field Trip first-run: flamingo stop before map teaching.

Fresh visitors on /field-pack/virtual-field-trip/ (and virtual-zoo) should
land in the Caribbean flamingo stop — card photo + Houston live cam —
without hunting a map hint or auto-opening YouTube.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from busyparent_agent.web import SECURITY_HEADERS


REPO = Path(__file__).resolve().parents[1]
FP = REPO / "static" / "field-pack"
VFT_PAGES = (
    FP / "virtual-field-trip" / "index.html",
    FP / "virtual-zoo" / "index.html",
)
VFT_JS = FP / "js" / "virtual-venue.js"
VFT_CSS = FP / "css" / "virtual-venue.css"
ZOO_JSON = FP / "data" / "virtual-venues" / "virtual-zoo.json"

FLAMINGO_PHOTO = "/field-pack/photos/caribbean-flamingo.jpg"
HOUSTON_CAM = "https://www.houstonzoo.org/explore/webcams/flamingo-cam/"
HOUSTON_PLAYER = "https://ams-28635.antmedia.cloud:5443/live/play.html?id=flamingo-camera&playOrder=hls"
FLAMINGO_FILM = "https://www.youtube.com/watch?v=u2k4lSTZxS4"
FIRST_RUN_KEY = "fp-virtual-zoo-firstrun-v1"
STAMPS_KEY = "fp-virtual-zoo-stamps-v1"


class VftFirstRunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = {p: p.read_text(encoding="utf-8") for p in VFT_PAGES}
        cls.js = VFT_JS.read_text(encoding="utf-8")
        cls.css = VFT_CSS.read_text(encoding="utf-8")
        cls.zoo = json.loads(ZOO_JSON.read_text(encoding="utf-8"))

    def test_flamingo_is_still_zoo_stop_one(self):
        habs = sorted(self.zoo.get("habitats") or [], key=lambda h: h.get("seq") or 0)
        self.assertTrue(habs)
        first = habs[0]
        self.assertEqual(first["id"], "caribbean-flamingo")
        self.assertEqual(first["cardId"], "caribbean-flamingo")
        self.assertEqual(first["label"], "Flamingo Lagoon")
        self.assertEqual(first["cam"]["url"], HOUSTON_CAM)
        self.assertEqual(first["video"]["url"], FLAMINGO_FILM)
        self.assertEqual(first["cam"]["embed"], HOUSTON_PLAYER)

    def test_pages_land_on_flamingo_stop_not_map_hint(self):
        for path, html in self.pages.items():
            with self.subTest(page=path.name):
                self.assertIn('id="vz-first-run"', html)
                self.assertIn('id="vz-first-run-start"', html)
                self.assertIn("Start with the flamingo", html)
                self.assertIn("Flamingo Lagoon", html)
                self.assertIn("Bright pink wader — long legs for shallow water.", html)
                self.assertIn(FLAMINGO_PHOTO, html)
                self.assertIn(HOUSTON_CAM, html)
                self.assertIn('id="vz-first-run-cam"', html)
                self.assertIn("Watch live", html)
                start = html.split('id="vz-first-run-start"', 1)[1].split("</button>", 1)[0]
                self.assertNotIn("youtube.com", start.lower())
                wrap = html.split('id="vz-first-run-film-wrap"', 1)[1].split(">", 1)[0]
                self.assertIn("hidden", wrap)
                film = html.split('id="vz-first-run-film"', 1)[1].split(">", 1)[0]
                self.assertNotIn("youtube.com", film.lower())
                self.assertIn("habitat=caribbean-flamingo", film)
                self.assertIn('role="button"', film)

    def test_early_script_skips_intro_for_progress_and_deep_links(self):
        for path, html in self.pages.items():
            with self.subTest(page=str(path.relative_to(REPO))):
                self.assertIn(FIRST_RUN_KEY, html)
                self.assertIn(STAMPS_KEY, html)
                self.assertIn('habitat=', html)
                self.assertIn('data-vft-chrome', html)
                self.assertIn('tab !== "zoo"', html)

    def test_js_first_run_is_flamingo_only_and_skips_auto_youtube(self):
        self.assertIn('const FIRST_RUN_KEY = "fp-virtual-zoo-firstrun-v1"', self.js)
        self.assertIn('const FIRST_RUN_STOP = "caribbean-flamingo"', self.js)
        self.assertIn("function shouldSkipFirstRun()", self.js)
        self.assertIn("function tryFlamingoLiveEmbed(", self.js)
        self.assertIn("function engageFirstRun()", self.js)
        self.assertIn("function continueFirstRun()", self.js)
        self.assertIn("syncFirstRun()", self.js)
        self.assertIn("const skipFilm = Boolean(opts && opts.skipFilm) || vftChrome() === \"intro\"", self.js)
        self.assertIn("if (hasFilm && !skipFilm) playFilmInline", self.js)
        self.assertIn("hasVftDeepLink()", self.js)
        # Do not rewrite every stop's cam into an embed.
        self.assertEqual(self.js.count("tryFlamingoLiveEmbed"), 4)
        self.assertIn("fromHash", self.js)
        self.assertIn("function onHash()", self.js)

    def test_css_hides_tabs_map_picker_until_flamingo_engaged(self):
        self.assertIn('html:not([data-vft-chrome="tour"]):not([data-vft-chrome="path"]) .vz-tabs', self.css)
        self.assertIn('html:not([data-vft-chrome="tour"]):not([data-vft-chrome="path"]) .vz-map-wrap', self.css)
        self.assertIn('html:not([data-vft-chrome="tour"]):not([data-vft-chrome="path"]) .vz-stops-drawer', self.css)
        self.assertIn('html[data-vft-chrome="tour"] .vz-first-run', self.css)
        self.assertIn(".vz-first-run-frame", self.css)

    def test_csp_allows_official_houston_flamingo_player(self):
        csp = SECURITY_HEADERS["Content-Security-Policy"]
        self.assertIn("https://www.youtube-nocookie.com", csp)
        self.assertIn("https://ams-28635.antmedia.cloud:5443", csp)

    def test_other_zoo_cams_remain_link_out(self):
        habs = {h["id"]: h for h in self.zoo["habitats"]}
        otter = habs["asian-small-clawed-otter"]
        self.assertIsNone(otter["cam"].get("embed"))
        self.assertTrue(otter["cam"]["url"].startswith("https://www.houstonzoo.org/"))
        self.assertEqual(self.js.count("tryFlamingoLiveEmbed"), 4)

    def test_cache_bumps_point_at_new_assets(self):
        for html in self.pages.values():
            self.assertIn("virtual-venue.css?v=48", html)
            self.assertIn("virtual-venue.js?v=83", html)
        self.assertIn("virtual-zoo.json?v=20", self.js)


if __name__ == "__main__":
    unittest.main()
