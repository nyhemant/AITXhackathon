"""2026-11-16 unfreeze (A): the five frozen query pages get the cal-academy treatment."""
import html, re, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
FP = ROOT / "static/field-pack"
QUERIES = {
    "museum-of-science-industry-chi": ("science museum", "chicago"),
    "national-aquarium-baltimore": ("aquarium", "washington dc"),
    "aquarium-of-the-pacific": ("aquarium", "los angeles"),
    "amnh": ("museum of natural history", "amnh"),
    "california-science-center": ("science museum", "los angeles"),
}
def one(t, p): return html.unescape(re.search(p, t, re.S).group(1))
class UnfreezeQueryPages20261116(unittest.TestCase):
    def test_title_h1_meta_match_query_and_sheet_under_h1(self):
        import generate_bdo_seo as gen
        venues = {r["id"]: r for r in gen.load_venues()}
        for slug, (a, b) in QUERIES.items():
            with self.subTest(slug=slug):
                t = (FP / slug / "index.html").read_text()
                h1 = one(t, r"<h1>(.*?)</h1>").lower()
                meta = one(t, r'<meta name="description" content="([^"]*)"')
                title = one(t, r"<title>(.*?)</title>")
                self.assertEqual(title, gen.title_for(venues[slug]))
                self.assertEqual(meta, gen.meta_for(venues[slug]))
                self.assertLessEqual(len(title), 60); self.assertLessEqual(len(meta), 155)
                for word in (a, b.split()[0]):
                    self.assertTrue(word in h1 or word.replace("los angeles", "la") in title.lower(), (slug, word))
                end = t.index("</h1>")
                self.assertLess(t.index('id="printable-hunt"') - end, 80)
                intro = one(t, r'<p class="lead seo-intro">(.*?)</p>')
                self.assertEqual(intro, gen.page_copy(f"/field-pack/{slug}/")["intro"])
                body = re.sub(r"<script.*?</script>", "", intro, flags=re.S)
                self.assertNotRegex(body.lower(), r"\bfree\b|\bno-cost\b|\bwe\b|\bour\b|\bus\b")
    def test_dc_page_is_honest_about_baltimore(self):
        t = (FP / "national-aquarium-baltimore/index.html").read_text()
        self.assertIn("Baltimore", one(t, r"<h1>(.*?)</h1>"))
        self.assertIn("in Baltimore", one(t, r'<meta name="description" content="([^"]*)"'))
        self.assertNotIn("DC aquarium", t)
    def test_la_aquarium_says_long_beach(self):
        t = (FP / "aquarium-of-the-pacific/index.html").read_text()
        self.assertIn("Long Beach", one(t, r"<h1>(.*?)</h1>"))
if __name__ == "__main__":
    unittest.main()
