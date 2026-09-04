"""Virtual Field Trip chrome is short: image-first, venue toggle primary."""

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
VENUES = FP / "data" / "virtual-venues"
LEAD = "Live cams · short films · free"
WORDY = (
    "Tap any stop",
    "Tap any pool",
    "Tap any hall",
    "Tap any park",
    "For rainy days",
    "classroom Friday",
    "Free. No account.",
    "Explore at home",
)


class VftSparseChromeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = {p: p.read_text(encoding="utf-8") for p in VFT_PAGES}
        cls.js = VFT_JS.read_text(encoding="utf-8")
        cls.configs = {
            "zoo": json.loads((VENUES / "virtual-zoo.json").read_text(encoding="utf-8")),
            "aquarium": json.loads((VENUES / "virtual-aquarium.json").read_text(encoding="utf-8")),
            "natural-history": json.loads((VENUES / "virtual-nhm.json").read_text(encoding="utf-8")),
            "science": json.loads((VENUES / "virtual-science.json").read_text(encoding="utf-8")),
            "parks": json.loads((VENUES / "virtual-parks.json").read_text(encoding="utf-8")),
        }

    def test_pages_drop_instructional_chrome(self):
        for path, html in self.pages.items():
            with self.subTest(page=str(path.relative_to(REPO))):
                self.assertNotIn('id="vz-map-hint"', html)
                self.assertNotIn('id="vz-use"', html)
                self.assertNotIn("class=\"vz-map-hint\"", html)
                self.assertNotIn("class=\"vz-use\"", html)
                chrome = html.split('<main class="vz-page">', 1)[1].split("<!-- VFT:PANELS:START -->", 1)[0]
                for phrase in WORDY:
                    self.assertNotIn(phrase, chrome)

    def test_lead_is_one_quiet_subline(self):
        for path, html in self.pages.items():
            with self.subTest(page=str(path.relative_to(REPO))):
                lead = re.search(r'id="vz-lead"[^>]*>(.*?)</p>', html, re.S)
                self.assertTrue(lead, html)
                text = re.sub(r"\s+", " ", lead.group(1)).strip()
                self.assertEqual(text, LEAD)
                self.assertLessEqual(len(text), 40)
        vft = self.pages[VFT_PAGES[0]]
        title = re.search(r'id="vz-title"[^>]*>(.*?)</h1>', vft, re.S)
        self.assertEqual(re.sub(r"\s+", " ", title.group(1)).strip(), "Virtual Field Trip")
        zoo = self.pages[VFT_PAGES[1]]
        zoo_title = re.search(r'id="vz-title"[^>]*>(.*?)</h1>', zoo, re.S)
        self.assertEqual(re.sub(r"\s+", " ", zoo_title.group(1)).strip(), "A zoo day at home")

    def test_json_leads_stay_sparse(self):
        expected = {
            "zoo": ("A zoo day at home", LEAD),
            "aquarium": ("An aquarium day at home", LEAD),
            "natural-history": ("A museum day at home", "Halls · short films · free"),
            "science": ("A science day at home", "Labs · short films · free"),
            "parks": ("A park day at home", LEAD),
        }
        for key, (h1, lead) in expected.items():
            cfg = self.configs[key]
            self.assertEqual(cfg["h1"], h1)
            self.assertEqual(cfg["lead"], lead)
            self.assertNotIn("use", cfg)
            for phrase in WORDY:
                self.assertNotIn(phrase, cfg["h1"])
                self.assertNotIn(phrase, cfg["lead"])

    def test_js_rewrites_lead_in_the_same_sparse_voice(self):
        self.assertIn("Your parks · lower 48 · free", self.js)
        self.assertNotIn("Your parks on a real map of the lower 48", self.js)
        self.assertNotIn("For rainy days, a classroom Friday", self.js)
        self.assertNotIn("Tap any stop. A suggested Next", self.js)
        self.assertIn("function resolveVenueTab(", self.js)
        self.assertIn("function renderMuseumChips(", self.js)
        self.assertIn('id === "museum"', self.js)

    def test_four_primary_venue_tabs_plus_museum_chips(self):
        for path, html in self.pages.items():
            with self.subTest(page=str(path.relative_to(REPO))):
                nav = html.split('id="vz-venues"', 1)[1].split("<!-- VFT:TABS:END -->", 1)[0]
                self.assertIn('data-tab="zoo">Zoo</a>', nav)
                self.assertIn('data-tab="aquarium">Aquarium</a>', nav)
                self.assertIn('data-tab="museum" data-venue="museum">Museum</a>', nav)
                self.assertIn('data-tab="parks">Parks</a>', nav)
                self.assertNotIn("Science museum", nav)
                self.assertNotIn("National parks", nav)
                self.assertIn('id="vz-museum-chips"', nav)
                self.assertIn('data-tab="natural-history">Natural history</a>', nav)
                self.assertIn('data-tab="science">Science</a>', nav)
                self.assertEqual(nav.count("class=\"vz-tab\""), 4)
        self.assertIn('id: "museum"', self.js)
        self.assertIn("natural-history", self.js)
        self.assertIn("science", self.js)

    def test_brand_and_sibling_paths_unchanged(self):
        for html in self.pages.values():
            self.assertIn('class="shell-brand" href="/start/"', html)
            self.assertIn('class="shell-product" href="/start/"', html)
            self.assertIn('href="/field-pack/" role="menuitem">All places', html)
            self.assertIn('href="/field-pack/virtual-field-trip/"', html)
            self.assertIn('id="vz-first-run"', html)
            self.assertIn("Start with the flamingo", html)


if __name__ == "__main__":
    unittest.main()
