"""2026-11-16 weekly item 1: each big scavenger-hunt query maps to one place page.

Only the San Francisco science-museum query lands on a non-frozen page (cal-academy).
The other five queries land on frozen test/comparison pages, which stay as they are.
"""
import re
import unittest
from pathlib import Path

FP = Path(__file__).resolve().parents[1] / "static/field-pack"
QUERY_PAGES = {
    "science museum scavenger hunt chicago": "museum-of-science-industry-chi",
    "science museum scavenger hunt san francisco": "cal-academy",
    "aquarium scavenger hunt washington dc": "national-aquarium-baltimore",
    "aquarium scavenger hunt los angeles": "aquarium-of-the-pacific",
    "american museum of natural history scavenger hunt": "amnh",
    "science museum scavenger hunt los angeles": "california-science-center",
}


def page(slug):
    return (FP / slug / "index.html").read_text(encoding="utf-8")


class QueryPages(unittest.TestCase):
    def test_sf_title_h1_match_query(self):
        t = page("cal-academy")
        title = re.search(r"<title>([^<]*)</title>", t).group(1)
        h1 = re.search(r"<h1>([^<]*)</h1>", t).group(1)
        for s in (title, h1):
            self.assertIn("San Francisco Science Museum Scavenger Hunt", s)
        self.assertLessEqual(len(title), 60)
        self.assertIn("California Academy of Sciences", h1)

    def test_sf_printable_sheet_and_answer_near_top(self):
        t = page("cal-academy")
        h1 = t.index("<h1>")
        self.assertLess(t.index('id="printable-hunt"'), t.index('id="start-here"'))
        self.assertLess(t.index('id="printable-hunt"') - h1, 600)
        intro = re.search(r'<p class="lead seo-intro">([^<]*)</p>', t).group(1)
        self.assertEqual(len(re.findall(r"[.?!](?:\s|$)", intro)), 3)  # question + 2-sentence answer
        self.assertNotRegex(intro.lower(), r"\bfree\b|no-cost|\bwe\b|\bour\b|\bus\b")

    def test_one_page_per_query(self):
        # No other place page claims the SF science-museum title.
        hits = [p.parent.name for p in FP.glob("*/index.html")
                if "San Francisco Science Museum Scavenger Hunt" in re.search(r"<title>([^<]*)</title>", p.read_text(encoding="utf-8")).group(1)]
        self.assertEqual(hits, ["cal-academy"])
        for slug in QUERY_PAGES.values():
            self.assertTrue((FP / slug / "index.html").exists(), slug)


if __name__ == "__main__":
    unittest.main()
