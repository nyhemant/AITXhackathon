"""2026-11-26 Gemini SEO consult (ChiefGrok plan items 2 and 5): Honolulu-pattern pages.

Each venue here gets a "Starter list:" lead and every find on the page is sourced to an
official page on the venue's own site (presence_url, checked 2026-11-26). The committed HTML
was patched in place, so the embedded venue-data must keep matching the venue JSON.
"""
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
}
# finds that are not a place on the venue site (kid's-choice cards) skip the source check
UNSOURCED_OK = {"free_explore"}
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
                self.assertIn(f'<p class="lead">{lead}</p>', _html(slug))
                self.assertEqual(len(v["route_90m"]), 3)

    def test_every_find_is_sourced_to_the_official_site(self):
        for slug, domain in VENUES.items():
            for item in _venue(slug)["items"]:
                if item["id"] in UNSOURCED_OK:
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


if __name__ == "__main__":
    unittest.main()
