"""Virtual Field Trip pictorial map: circular photo pins + winding dual-stroke trail."""

from __future__ import annotations

import json
import re
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
ZOO_SVG = FP / "media" / "virtual-zoo" / "map.svg"
ZOO_JSON = FP / "data" / "virtual-venues" / "virtual-zoo.json"


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


def _rule(css: str, selector: str) -> str:
    token = selector + " {"
    start = css.rindex(token) + len(token)
    return css[start : css.index("}", start)]


class VftMapPolishTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.js = VFT_JS.read_text(encoding="utf-8")
        cls.css = VFT_CSS.read_text(encoding="utf-8")
        cls.zoo_svg = ZOO_SVG.read_text(encoding="utf-8")
        cls.zoo = json.loads(ZOO_JSON.read_text(encoding="utf-8"))
        cls.pages = {p: p.read_text(encoding="utf-8") for p in VFT_PAGES}

    def test_pictorial_pins_are_circular_photo_buttons(self):
        self.assertIn(
            ".vz-map-wrap.is-pictorial .vz-spot .vz-silo,\n.vz-map-wrap.is-pictorial .vz-spot .vz-halo {\n  rx: 50%;\n  ry: 50%;\n}",
            self.css,
        )
        silo = _rule(self.css, ".vz-map-wrap.is-pictorial .vz-spot .vz-silo")
        self.assertIn("fill: #fff", silo)
        self.assertIn("stroke: #fff", silo)
        self.assertIn("stroke-width: 6.5", silo)
        self.assertIn("filter: url(#pad-shadow)", silo)
        self.assertNotIn("fill: none", silo)
        img = _rule(self.css, ".vz-map-wrap.is-pictorial .vz-spot image")
        self.assertIn("clip-path: circle(50%", img)
        self.assertIn("function polishPictorialMap(", self.js)
        self.assertIn("function roundPictorialPins(", self.js)
        self.assertIn("function circlePhotoClip(", self.js)
        round_fn = _fn_body(self.js, "roundPictorialPins")
        self.assertIn('setAttribute("rx"', round_fn)
        self.assertIn('setAttribute("ry"', round_fn)

    def test_pin_states_keep_selected_next_and_visited(self):
        self.assertIn("stroke: #e8b923", self.css)
        self.assertIn("stroke-width: 8", self.css)
        self.assertIn("stroke: #8ed4c2", self.css)
        self.assertIn(
            '.vz-map-wrap.is-pictorial .vz-spot[data-next="1"] .vz-silo {\n  stroke-dasharray: none;\n}',
            self.css,
        )
        self.assertIn("function placeStampMark(", self.js)
        self.assertIn("function refreshOpenChip(", self.js)
        self.assertIn("vz-open-chip", self.js)

    def test_trail_is_dual_stroke_not_yellow_dash(self):
        self.assertIn("stroke-dasharray: none", self.css)
        self.assertIn("stroke: #f3e4c0", self.css)
        self.assertNotIn("stroke-dasharray: 10 8", self.css)
        self.assertIn("stroke: #3f6f69", self.css)
        self.assertIn("stroke-width: 16", self.css)
        self.assertIn(".vz-trail-shadow", self.css)
        self.assertIn("stroke-width: 20", self.css)
        self.assertIn("function windTrailD(", self.js)
        self.assertIn("function polishTrail(", self.js)
        self.assertIn("vz-trail-shadow", self.js)

    def test_zoo_svg_has_circular_clip_and_winding_quads(self):
        self.assertIn('<circle cx="0.5" cy="0.5" r="0.5"/>', self.zoo_svg)
        self.assertNotIn('rx="0.14"', self.zoo_svg)
        self.assertIn("Q368.3,699.6", self.zoo_svg)
        self.assertNotIn("Q347.5,716.0", self.zoo_svg)
        self.assertIn('class="vz-trail-shadow"', self.zoo_svg)
        self.assertEqual(self.zoo["mapSvg"], "/field-pack/media/virtual-zoo/map.svg?v=11")
        habs = sorted(self.zoo.get("habitats") or [], key=lambda h: h.get("seq") or 0)
        self.assertEqual(habs[0]["id"], "caribbean-flamingo")

    def test_free_stops_and_print_paths_untouched(self):
        can_open = _fn_body(self.js, "canOpen")
        self.assertIn("return Boolean(id)", can_open)
        self.assertNotIn("isSequential()", can_open)
        self.assertIn('const DEFAULT_ZOO_STOP = "caribbean-flamingo"', self.js)
        for html in self.pages.values():
            self.assertIn("Print the cutouts", html)
            self.assertIn("virtual-venue.js?v=93", html)
            self.assertIn("virtual-venue.css?v=54", html)

    def test_wind_trail_offsets_midpoint_quads(self):
        body = _fn_body(self.js, "windTrailD")
        self.assertIn("nearMid", body)
        self.assertIn("0.26", body)
        self.assertIn("bulge", body)


if __name__ == "__main__":
    unittest.main()
