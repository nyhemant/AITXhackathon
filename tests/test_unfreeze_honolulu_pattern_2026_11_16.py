"""2026-11-16 unfreeze (B): Honolulu pattern on Calgary, Toronto and Joshua Tree."""
import json, re, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
FP = ROOT / "static/field-pack"
def venue(s): return json.loads((FP / f"data/venues/{s}.json").read_text())
def page(s): return (FP / s / "index.html").read_text()
class UnfreezeHonoluluPattern20261116(unittest.TestCase):
    def test_starter_list_taglines(self):
        for s in ["calgary-zoo", "toronto-zoo", "joshua-tree"]:
            self.assertTrue(venue(s)["tagline"].startswith("Starter list: "), s)
            self.assertIn('<p class="lead">Starter list: ', page(s), s)
    def test_start_here_is_three_animals(self):
        self.assertEqual(venue("joshua-tree")["route_90m"], ["jt_spiny_lizard", "jt_roadrunner", "jt_gambels_quail"])
        for s in ["calgary-zoo", "toronto-zoo"]:
            self.assertEqual(len(venue(s)["route_90m"]), 3)
    def test_new_finds_are_sourced(self):
        for s, ids, host in [("calgary-zoo", ["polar_bear"], "calgaryzoo.com"),
                             ("joshua-tree", ["jt_spiny_lizard", "jt_roadrunner", "jt_gambels_quail", "jt_ground_squirrel"], "nps.gov/jotr")]:
            items = {i["id"]: i for i in venue(s)["items"]}
            for k in ids:
                self.assertIn(host, items[k]["presence_url"], k)
        self.assertEqual({i["id"]: i for i in venue("calgary-zoo")["items"]}["polar_bear"].get("catalog_id"), "polar-bear")
    def test_calgary_keeps_last_checked_chip(self):
        self.assertIn('Last checked</span><span class="seo-fact-v">August 23, 2026</span>', page("calgary-zoo"))
if __name__ == "__main__":
    unittest.main()
