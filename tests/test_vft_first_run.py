"""Virtual Field Trip zoo tab: full tour chrome, flamingo default, no Stop 1 shell.

Fresh visitors on /field-pack/virtual-zoo/ and /field-pack/virtual-field-trip/?tab=zoo
land on venue tabs + map with Caribbean flamingo already open. There is no
vz-first-run panel and no fp-virtual-zoo-firstrun-v1 localStorage gate.
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
AQUARIUM_JSON = FP / "data" / "virtual-venues" / "virtual-aquarium.json"
NHM_JSON = FP / "data" / "virtual-venues" / "virtual-nhm.json"
SCIENCE_JSON = FP / "data" / "virtual-venues" / "virtual-science.json"
PARKS_JSON = FP / "data" / "virtual-venues" / "virtual-parks.json"

HOUSTON_CAM = "https://www.houstonzoo.org/explore/webcams/flamingo-cam/"
HOUSTON_PLAYER = "https://ams-28635.antmedia.cloud:5443/live/play.html?id=flamingo-camera&playOrder=hls"
FLAMINGO_FILM = "https://www.youtube.com/watch?v=7nK3gZqtlOM"
FIRST_RUN_KEY = "fp-virtual-zoo-firstrun-v1"
DEAD_UI = (
    "vz-first-run",
    "vz-first-run-start",
    "vz-first-run-cam",
    "vz-first-run-film",
    "Start with the flamingo",
    "Stop 1 · Flamingo Lagoon",
    FIRST_RUN_KEY,
)


def _fn_body(src: str, name: str) -> str:
    token = f"function {name}("
    start = src.index(token)
    depth = 0
    i = src.index("{", start)
    for j in range(i, len(src)):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                return src[start : j + 1]
    raise AssertionError(f"unclosed function {name}")


class VftFirstRunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = {p: p.read_text(encoding="utf-8") for p in VFT_PAGES}
        cls.js = VFT_JS.read_text(encoding="utf-8")
        cls.css = VFT_CSS.read_text(encoding="utf-8")
        cls.zoo = json.loads(ZOO_JSON.read_text(encoding="utf-8"))
        cls.aquarium = json.loads(AQUARIUM_JSON.read_text(encoding="utf-8"))
        cls.nhm = json.loads(NHM_JSON.read_text(encoding="utf-8"))
        cls.science = json.loads(SCIENCE_JSON.read_text(encoding="utf-8"))
        cls.parks = json.loads(PARKS_JSON.read_text(encoding="utf-8"))

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

    def test_pages_have_no_first_run_shell(self):
        for path, html in self.pages.items():
            with self.subTest(page=str(path.relative_to(REPO))):
                for needle in DEAD_UI:
                    self.assertNotIn(needle, html)
                self.assertNotIn("localStorage.getItem", html)
                self.assertIn('data-vft-chrome="tour"', html)
                self.assertIn('id="vz-venues"', html)
                self.assertIn('id="vz-map"', html)
                self.assertIn('id="vz-dialog"', html)
                self.assertIn("Flamingo Lagoon", html)
                chrome = html.split('<main class="vz-page">', 1)[1].split('id="vz-map"', 1)[0]
                self.assertNotIn("Stop 1", chrome)
                self.assertIn('q.get("print") === "1"', html)
                self.assertIn('hash === "#print"', html)
                self.assertIn('data-vft-print', html)

    def test_js_opens_flamingo_on_zoo_tab_without_deep_link(self):
        self.assertIn('const DEFAULT_ZOO_STOP = "caribbean-flamingo"', self.js)
        self.assertIn("function setTourChrome()", self.js)
        self.assertIn("function habitatHashId()", self.js)
        self.assertIn("setTourChrome();", self.js)
        self.assertNotIn("FIRST_RUN_KEY", self.js)
        self.assertNotIn("function shouldSkipFirstRun()", self.js)
        self.assertNotIn("function syncFirstRun()", self.js)
        self.assertNotIn("function wireFirstRun()", self.js)
        self.assertNotIn("function setVftChrome(", self.js)
        self.assertNotIn("function playFirstRunFilm(", self.js)
        self.assertNotIn("tryFlamingoLiveEmbed", self.js)
        self.assertNotIn(FIRST_RUN_KEY, self.js)
        self.assertIn("function wantsCutoutPrint()", self.js)
        self.assertIn("function revealPrintReady()", self.js)
        self.assertIn("printHomeSafari", self.js)
        on_hash = _fn_body(self.js, "onHash")
        self.assertIn("habitatHashId()", on_hash)
        self.assertIn("wantsCutoutPrint()", on_hash)
        self.assertIn('currentTab() === "zoo"', on_hash)
        self.assertIn("openHabitat(DEFAULT_ZOO_STOP", on_hash)
        self.assertIn("closeDialog()", on_hash)
        self.assertIn("fromHash", on_hash)

    def test_deep_links_still_open_the_hashed_stop(self):
        on_hash = _fn_body(self.js, "onHash")
        self.assertIn("openHabitat(hid, null, { fromHash: true })", on_hash)
        open_h = _fn_body(self.js, "openHabitat")
        self.assertIn("fromHash", open_h)
        self.assertIn("const skipFilm = Boolean(opts && opts.skipFilm)", open_h)
        self.assertIn("if (hasFilm && !skipFilm) playHabitatFilm", open_h)
        self.assertNotIn('vftChrome() === "intro"', open_h)
        self.assertIn("function pickHabitatFilm(", self.js)
        self.assertIn('const FILM_SEEN_KEY = "fp-vft-film-seen-v1"', self.js)

    def test_css_does_not_hide_tour_chrome(self):
        self.assertNotIn("vz-first-run", self.css)
        self.assertNotIn("is-vft-first-run", self.css)
        self.assertNotIn('html:not([data-vft-chrome="tour"])', self.css)
        self.assertIn(".vz-venues", self.css)
        self.assertIn(".vz-map-wrap", self.css)
        self.assertIn('html[data-vft-print="1"] .vz-print-row', self.css)

    def test_other_venues_do_not_default_open_a_stop(self):
        on_hash = _fn_body(self.js, "onHash")
        self.assertNotIn("clownfish", on_hash)
        self.assertNotIn("sci-dinosaur", on_hash)
        self.assertNotIn("yellowstone", on_hash)
        self.assertNotIn("cm-woven", on_hash)
        self.assertEqual(self.aquarium["habitats"][0]["id"], "clownfish")
        self.assertEqual(self.nhm["habitats"][0]["id"], "sci-aquarium-zone")
        self.assertEqual(self.science["habitats"][0]["id"], "cm-woven")
        self.assertEqual(self.parks["habitats"][0]["id"], "acadia")

    def test_csp_allows_official_houston_flamingo_player(self):
        csp = SECURITY_HEADERS["Content-Security-Policy"]
        self.assertIn("https://www.youtube-nocookie.com", csp)
        self.assertIn("https://ams-28635.antmedia.cloud:5443", csp)

    def test_other_zoo_cams_remain_link_out(self):
        habs = {h["id"]: h for h in self.zoo["habitats"]}
        otter = habs["asian-small-clawed-otter"]
        self.assertIsNone(otter["cam"].get("embed"))
        self.assertTrue(otter["cam"]["url"].startswith("https://www.houstonzoo.org/"))

    def test_cache_bumps_point_at_new_assets(self):
        for html in self.pages.values():
            self.assertIn("virtual-venue.css?v=57", html)
            self.assertIn("virtual-venue.js?v=98", html)
        self.assertIn("virtual-zoo.json?v=26", self.js)

    def test_print_row_is_the_cutout_hunt_and_has_print_anchor(self):
        for path, html in self.pages.items():
            with self.subTest(page=str(path.relative_to(REPO))):
                row = re.search(r'<div class="vz-print-row[^"]*" id="print">[\s\S]*?</button>', html)
                self.assertIsNotNone(row)
                self.assertIn('id="vz-print-watch"', row.group(0))
                self.assertIn("btn-secondary", row.group(0))
                self.assertIn("Print the cutouts", row.group(0))
                self.assertIn(">Print</span>", html)
                self.assertIn(">Cut</span>", html)
                self.assertIn(">Hide</span>", html)
                self.assertNotIn("and maybe hide them for a hunt", html)


if __name__ == "__main__":
    unittest.main()
