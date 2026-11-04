"""2026-11-04 search visibility: title/description length and real alt text."""
import glob
import html
import re
import unittest
from pathlib import Path

STATIC = Path(__file__).resolve().parents[1] / "static"
SITEMAP_PAGES = [
    STATIC / (re.sub(r"^https?://[^/]+/", "", loc) + "index.html")
    for loc in re.findall(r"<loc>([^<]+/)</loc>", (STATIC / "sitemap.xml").read_text(encoding="utf-8"))
]


def _pages():
    return [p for p in SITEMAP_PAGES if p.exists()]


class SeoAltTitleTests(unittest.TestCase):
    def test_titles_at_most_60(self):
        bad = []
        for p in _pages():
            m = re.search(r"<title>(.*?)</title>", p.read_text(encoding="utf-8"), re.S)
            if m and len(html.unescape(m.group(1)).strip()) > 60:
                bad.append(str(p.relative_to(STATIC)))
        self.assertEqual(bad, [])

    def test_descriptions_at_most_160(self):
        bad = []
        for p in _pages():
            m = re.search(r'<meta name="description" content="([^"]*)"', p.read_text(encoding="utf-8"))
            if m and len(html.unescape(m.group(1))) > 160:
                bad.append(str(p.relative_to(STATIC)))
        self.assertEqual(bad, [])

    def test_no_empty_alt_on_start_and_cards(self):
        files = [STATIC / "start/index.html"] + [Path(f) for f in glob.glob(str(STATIC / "field-pack/cards/**/index.html"), recursive=True)]
        bad = []
        for f in files:
            for tag in re.findall(r"<img\b[^>]*>", f.read_text(encoding="utf-8"), re.S):
                if re.search(r'\salt=""', tag) and not re.search(r'\shidden\b|aria-hidden="true"', tag):
                    bad.append((str(f.relative_to(STATIC)), tag[:80]))
        self.assertEqual(bad, [])

    def test_start_teach_slides_named(self):
        s = (STATIC / "start/index.html").read_text(encoding="utf-8")
        for src in ("teach-lion", "teach-elephant", "teach-giraffe"):
            m = re.search(r'<img\b[^>]*data-src="/start/%s\.jpg"[^>]*>' % src, s, re.S)
            self.assertIsNotNone(m)
            self.assertRegex(m.group(0), r'alt="[A-Z][^"]+"')


if __name__ == "__main__":
    unittest.main()
