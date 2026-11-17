import json, pathlib, re, sys, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
FP = ROOT / "static/field-pack"
NOI = ["ecoparque-ba", "stockholm-skansen", "cairo-zoo", "beijing-zoo",
       "nairobi-safari-walk", "bogota-zoo", "lotte-aquarium-seoul"]
class WeeklyCleanup20261116(unittest.TestCase):
    def test_cairo_closure_line_is_first(self):
        t = (FP / "cairo-zoo/index.html").read_text()
        art = t.index('<article class="seo-article">')
        self.assertLess(t.index('class="seo-place-notice"'), t.index("<h1>"))
        self.assertGreater(t.index('class="seo-place-notice"'), art)
        self.assertEqual(t.count('class="seo-place-notice"'), 1)
    def test_no_card_query_links_to_noindex_places(self):
        pat = re.compile(r'href="/field-pack/cards/[a-z0-9-]+/\?from=(' + "|".join(NOI) + r')"')
        bad = [str(p.relative_to(FP)) for p in FP.glob("**/index.html") if pat.search(p.read_text())]
        self.assertEqual(bad, [])
    def test_cards_read_from_in_fragment(self):
        for cid in ["african-lion", "cheetah", "giant-panda", "ostrich", "shark"]:
            t = (FP / f"cards/{cid}/index.html").read_text()
            self.assertIn('new URLSearchParams((window.location.hash || "").slice(1)).get("from")', t, cid)
    def test_generator_uses_fragment_for_noindex(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        import generate_bdo_seo as g
        self.assertTrue(g.item_public_href("shark", extra_query="from=lotte-aquarium-seoul").endswith("/shark/#from=lotte-aquarium-seoul"))
        self.assertTrue(g.item_public_href("shark", extra_query="from=dallas-zoo").endswith("/shark/?from=dallas-zoo"))
    def test_helsinki_zones_sourced(self):
        v = json.loads((FP / "data/venues/helsinki-zoo.json").read_text())
        z = {i["id"]: i.get("zone") for i in v["items"]}
        self.assertEqual(z["red_panda"], "Cat Valley")
        self.assertEqual(z["kor_snow_leopard"], "Cat Valley")
        self.assertEqual(z["kor_amur_leopard"], "Cat Valley")
        self.assertEqual(z["kor_brown_bear"], "Bear Castle")
        self.assertEqual(z["kor_wolverine"], "Korpi")
        self.assertIn("· Cat Valley", (FP / "helsinki-zoo/index.html").read_text())
if __name__ == "__main__":
    unittest.main()
