"""Hub #/venue/{id} on the landing map leaves for the SEO place page."""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from busyparent_agent.web import _safe_field_pack_path


REPO = Path(__file__).resolve().parents[1]
FP = REPO / "static" / "field-pack"
MAP_JS = FP / "js" / "landing-map.js"
APP_JS = FP / "js" / "app.js"
APP_HTML = FP / "app.html"

_EXTRACT_JS = r"""
const fs = require("fs");
const src = fs.readFileSync(process.argv[1], "utf8");
function extract(name) {
  const re = new RegExp("function " + name + "\\([^{]*\\) \\{[\\s\\S]*?\\n  \\}\\n");
  const m = src.match(re);
  if (!m) throw new Error(name + " not found");
  return m[0];
}
const fn = extract("placePagePath") + extract("resolveHubVenueHash");
const hashes = JSON.parse(process.argv[2]);
const resolve = eval(fn + "; resolveHubVenueHash");
const out = {};
for (const h of hashes) out[h] = resolve(h);
process.stdout.write(JSON.stringify(out));
"""


def _resolve(hashes: list[str]) -> dict[str, str]:
    proc = subprocess.run(
        ["node", "-e", _EXTRACT_JS, str(MAP_JS), json.dumps(hashes)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


class HubVenueHashTests(unittest.TestCase):
    def test_hub_venue_hash_resolves_to_place_page(self):
        resolved = _resolve(
            [
                "#/venue/houston-zoo",
                "#/venue/yellowstone",
                "#venue/houston-zoo",
                "#/venue/yellowstone/item/np-visitor-center",
                "#us-map",
                "",
            ]
        )
        self.assertEqual(resolved["#/venue/houston-zoo"], "/field-pack/houston-zoo/")
        self.assertEqual(resolved["#/venue/yellowstone"], "/field-pack/yellowstone/")
        self.assertEqual(resolved["#venue/houston-zoo"], "/field-pack/houston-zoo/")
        self.assertEqual(
            resolved["#/venue/yellowstone/item/np-visitor-center"],
            "/field-pack/yellowstone/",
        )
        self.assertEqual(resolved["#us-map"], "")
        self.assertEqual(resolved[""], "")

        self.assertIsNotNone(_safe_field_pack_path("/field-pack/houston-zoo/"))
        self.assertIsNotNone(_safe_field_pack_path("/field-pack/yellowstone/"))
        houston = (FP / "houston-zoo" / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="/field-pack/#us-map">Find on map</a>', houston)
        self.assertNotIn('href="/field-pack/#/venue/houston-zoo"', houston)
        yellowstone = (FP / "yellowstone" / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="/field-pack/#us-map">Map</a>', yellowstone)

    def test_hub_leaves_on_hash_and_pin_click(self):
        index = (FP / "index.html").read_text(encoding="utf-8")
        self.assertIn("location.replace(\"/field-pack/\" + encodeURIComponent(id) + \"/\")", index)
        self.assertLess(index.find("location.replace(\"/field-pack/\""), index.find("landing-map.js"))
        js = MAP_JS.read_text(encoding="utf-8")
        self.assertIn("function resolveHubVenueHash(hash)", js)
        self.assertIn("function goToPlacePage(venueId, opts)", js)
        self.assertIn("location.replace(fromHash)", js)
        self.assertIn("location.replace(dest)", js)
        self.assertIn("else goToPlacePage(cl.places[0].id);", js)
        self.assertIn("goToPlacePage(id);", js)
        self.assertIn("if (id) goToPlacePage(id);", js)
        self.assertNotIn(
            'const next = venueId ? `#/venue/${encodeURIComponent(venueId)}` : "#us-map";',
            js,
        )
        # Rich pin panel is not the venue destination anymore.
        set_venue = js.split("async function setVenue(venueId, opts = {})", 1)[1]
        set_venue = set_venue.split("\n  async function ", 1)[0]
        self.assertIn("if (!stayOnMap && goToPlacePage(venueId)) return;", set_venue)
        self.assertNotIn("showVenueDetail(venueId)", set_venue)

    def test_outing_app_hash_routes_stay(self):
        app = APP_JS.read_text(encoding="utf-8")
        self.assertIn("if ((m = hash.match(/^#\\/venue\\/([^/]+)\\/item\\/([^/]+)/)))", app)
        self.assertIn("if ((m = hash.match(/^#\\/venue\\/([^/]+)/)))", app)
        html = APP_HTML.read_text(encoding="utf-8")
        self.assertIn("id=", html)
        self.assertTrue((FP / "app.html").is_file())


if __name__ == "__main__":
    unittest.main()
