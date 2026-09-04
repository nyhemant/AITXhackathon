"""Virtual Field Trip: any stop opens without sequential stamps.

Map pins and the stops drawer must not wait for stop 1, then 2, then 3.
A suggested Next may still highlight the first unvisited habitat, but it
must not gate openHabitat. Flamingo first-run stays a separate intro.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
FP = REPO / "static" / "field-pack"
VFT_PAGES = (
    FP / "virtual-field-trip" / "index.html",
    FP / "virtual-zoo" / "index.html",
)
VFT_JS = FP / "js" / "virtual-venue.js"
VFT_CSS = FP / "css" / "virtual-venue.css"
ZOO_JSON = FP / "data" / "virtual-venues" / "virtual-zoo.json"
AHEAD_STOPS = (
    "reticulated-giraffe",
    "african-lion",
    "sumatran-tiger",
    "giant-panda",
)
HINT = "Tap any stop. A suggested Next is marked if you want a path."


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


class VftFreeStopsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = {p: p.read_text(encoding="utf-8") for p in VFT_PAGES}
        cls.js = VFT_JS.read_text(encoding="utf-8")
        cls.css = VFT_CSS.read_text(encoding="utf-8")
        cls.zoo = json.loads(ZOO_JSON.read_text(encoding="utf-8"))
        cls.habitats = sorted(cls.zoo.get("habitats") or [], key=lambda h: h.get("seq") or 0)

    def test_can_open_does_not_require_prior_stamps(self):
        body = _fn_body(self.js, "canOpen")
        self.assertNotIn("isSequential()", body)
        self.assertNotIn("nextHabitat()", body)
        self.assertNotIn("stamps.includes", body)
        self.assertIn("return Boolean(id)", body)

    def test_open_habitat_does_not_block_ahead_map_taps(self):
        body = _fn_body(self.js, "openHabitat")
        self.assertNotIn("!fromHash && !canOpen", body)
        self.assertNotIn("scrollIntoView", body)
        self.assertIn("Next is a suggestion, not a gate", body)
        self.assertIn("if (!canOpen(id)) return;", body)

    def test_map_pins_never_lock_or_disable_ahead_stops(self):
        body = _fn_body(self.js, "markMapStamps")
        self.assertNotIn('data-lock", locked', body)
        self.assertNotIn('setAttribute("data-lock", locked', body)
        self.assertIn('setAttribute("data-lock", "0")', body)
        self.assertIn('setAttribute("tabindex", "0")', body)
        self.assertIn('removeAttribute("aria-disabled")', body)
        self.assertNotIn('aria-disabled", locked', body)
        self.assertIn("data-next", body)

    def test_hint_invites_any_stop_not_only_next(self):
        self.assertIn(HINT, self.js)
        self.assertNotIn("Start at the gate. The next stop is marked Next.", self.js)
        self.assertNotIn("Follow the road from Start to Finish.", self.js)
        for path, html in self.pages.items():
            with self.subTest(page=str(path.relative_to(REPO))):
                self.assertIn(HINT, html)
                self.assertNotIn("Start at the gate.", html)

    def test_every_zoo_stop_is_openable_without_prior_stamps(self):
        self.assertGreaterEqual(len(self.habitats), 8)
        ids = [h["id"] for h in self.habitats]
        self.assertEqual(ids[0], "caribbean-flamingo")
        for hid in AHEAD_STOPS:
            self.assertIn(hid, ids)
        self.assertTrue(all(ids), ids)
        can_open = _fn_body(self.js, "canOpen")
        for hid in ids:
            self.assertTrue(hid, hid)
            self.assertIn("return Boolean(id)", can_open)

    def test_flamingo_first_run_still_present(self):
        self.assertIn('const FIRST_RUN_KEY = "fp-virtual-zoo-firstrun-v1"', self.js)
        self.assertIn('const FIRST_RUN_STOP = "caribbean-flamingo"', self.js)
        self.assertIn("function shouldSkipFirstRun()", self.js)
        self.assertIn("function engageFirstRun()", self.js)
        for html in self.pages.values():
            self.assertIn('id="vz-first-run"', html)
            self.assertIn("Start with the flamingo", html)

    def test_locked_pin_css_does_not_look_dead(self):
        lock = self.css.split('.vz-spot[data-lock="1"] {', 1)[1].split("}", 1)[0]
        self.assertIn("cursor: pointer;", lock)
        self.assertNotIn("cursor: default;", lock)

    def test_cache_bump(self):
        for html in self.pages.values():
            self.assertIn("virtual-venue.js?v=85", html)
            self.assertIn("virtual-venue.css?v=50", html)
        self.assertIn("virtual-zoo.json?v=21", self.js)
        self.assertIn("virtual-aquarium.json?v=22", self.js)
        self.assertIn("virtual-science.json?v=15", self.js)
        self.assertIn("virtual-parks.json?v=23", self.js)


if __name__ == "__main__":
    unittest.main()
