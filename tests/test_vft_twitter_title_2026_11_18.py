"""2026-11-18: the virtual field trip page has twitter:title matching og:title (KZK, kidzookit.com)."""
import pathlib, re, unittest
P = pathlib.Path(__file__).resolve().parents[1] / "static/field-pack/virtual-field-trip/index.html"
class VftTwitterTitle20261118(unittest.TestCase):
    def test_twitter_title_matches_og_title(self):
        t = P.read_text()
        og = re.findall(r'<meta property="og:title" content="([^"]*)"', t)
        tw = re.findall(r'<meta name="twitter:title" content="([^"]*)"', t)
        self.assertEqual(len(og), 1); self.assertEqual(tw, og)
        self.assertEqual(re.findall(r"<title>(.*?)</title>", t), og)
if __name__ == "__main__":
    unittest.main()
