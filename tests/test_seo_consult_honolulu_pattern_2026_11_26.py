"""2026-11-26 Gemini SEO consult (ChiefGrok plan items 2 and 5): Honolulu-pattern pages.

Each venue here gets a "Starter list:" lead and every find on the page is sourced to an
official page on the venue's own site (presence_url, checked 2026-11-26). The committed HTML
was patched in place, so the embedded venue-data must keep matching the venue JSON.
"""
import html
import json
import pathlib
import re
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

# slug -> official domain every sourced find must point at
VENUES = {
    "aquarium-of-the-pacific": "www.aquariumofpacific.org",
    "museum-of-science-industry-chi": "www.griffinmsi.org",
    "perot-museum": "www.perotmuseum.org",
    "fort-worth-zoo": "www.fortworthzoo.org",
    "cincinnati-zoo": "cincinnatizoo.org",
    "oregon-zoo": "www.oregonzoo.org",
    "nhm-london": "www.nhm.ac.uk",
    "auckland-zoo": "www.aucklandzoo.co.nz",
    "manila-zoo": "www.manilazoo.ph",
    "discovery-place": "discoveryplace.org",
}
# finds that are not a place on the venue site (kid's-choice cards) skip the source check
UNSOURCED_OK = {"free_explore", "cm_free_explore"}
# NHM's Investigate centre page 404s (2026-11-26), so its hands-on card is an open prompt, not a presence claim.
UNSOURCED_BY_VENUE = {"nhm-london": {"sci_hands_on"}}
BANNED = re.compile(r"\b(?:free|we|our|us)\b|no-cost", re.I)


def _venue(slug):
    return json.loads((ROOT / f"static/field-pack/data/venues/{slug}.json").read_text(encoding="utf-8"))


def _html(slug):
    return (ROOT / f"static/field-pack/{slug}/index.html").read_text(encoding="utf-8")


class SeoConsultHonoluluPattern(unittest.TestCase):
    def test_starter_list_lead_is_visible(self):
        import generate_bdo_seo as g

        for slug in VENUES:
            with self.subTest(slug=slug):
                v = _venue(slug)
                self.assertTrue(v["tagline"].startswith("Starter list: "), v["tagline"])
                lead = g.quiet_hero_lead({}, v)
                self.assertIn(f'<p class="lead">{html.escape(lead, quote=False)}</p>', _html(slug))
                self.assertEqual(len(v["route_90m"]), 3)

    def test_every_find_is_sourced_to_the_official_site(self):
        for slug, domain in VENUES.items():
            for item in _venue(slug)["items"]:
                if item["id"] in UNSOURCED_OK or item["id"] in UNSOURCED_BY_VENUE.get(slug, ()):
                    continue
                with self.subTest(slug=slug, item=item["id"]):
                    self.assertTrue(item.get("presence_url", "").startswith(f"https://{domain}/"), item.get("presence_url"))
                    self.assertEqual(item.get("presence_checked"), "2026-11-26")

    def test_embedded_venue_data_matches_json(self):
        for slug in VENUES:
            with self.subTest(slug=slug):
                v = _venue(slug)
                m = re.search(r'<script type="application/json" id="venue-data">(.*?)</script>', _html(slug), re.S)
                emb = json.loads(m.group(1))
                self.assertEqual(emb["tagline"], v["tagline"])
                self.assertEqual({i["id"]: i["one_liner"] for i in emb["items"]}, {i["id"]: i["one_liner"] for i in v["items"]})
                for item in v["items"]:
                    self.assertIn(item["one_liner"][:30], _html(slug))

    def test_copy_rules(self):
        for slug in VENUES:
            v = _venue(slug)
            for text in [v["tagline"]] + [i["one_liner"] for i in v["items"] if i["id"] not in UNSOURCED_OK]:
                with self.subTest(slug=slug, text=text):
                    self.assertIsNone(BANNED.search(text))

    def test_caveats_kept(self):
        self.assertIn("Magellanic penguins, not African", _venue("aquarium-of-the-pacific")["tagline"])
        self.assertIn("Asian elephants, not African", _venue("cincinnati-zoo")["tagline"])
        self.assertIn("Asian elephants, not African", _venue("oregon-zoo")["tagline"])
        self.assertIn("elephants have left", _venue("auckland-zoo")["tagline"])
        self.assertIn("tigers are Bengal and Siberian", _venue("manila-zoo")["tagline"])

    def test_al_ain_says_checklist_not_official_map(self):
        page = (ROOT / "static/field-pack/al-ain-zoo/index.html").read_text(encoding="utf-8")
        self.assertIn("printable hunt checklist, not an official zoo map", page)

    def test_fiona_is_not_named_in_the_cincinnati_hunt(self):
        # Fiona the hippo died on Nov 19, 2026 (cincinnatizoo.org/fiona-the-world-famous-hippo/).
        self.assertNotIn("Fiona", _html("cincinnati-zoo"))
        self.assertNotIn("Fiona", (ROOT / "static/field-pack/js/catalog.js").read_text(encoding="utf-8"))

    def test_perot_sports_hall_closure_is_noted(self):
        items = {i["id"]: i for i in _venue("perot-museum")["items"]}
        self.assertIn("closed for renovation Jan 5 – March 2027", items["sci_hands_on"]["one_liner"])


if __name__ == "__main__":
    unittest.main()
