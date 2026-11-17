"""Weekly 2026-11-16 item 2: aquarium and science-museum sections on /printables/scavenger-hunt/."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "static/printables/scavenger-hunt/index.html"
NOINDEX = "ecoparque-ba stockholm-skansen cairo-zoo beijing-zoo nairobi-safari-walk bogota-zoo lotte-aquarium-seoul".split()


def section(t, sid):
    return re.search(rf'<section[^>]*id="{sid}".*?</section>', t, re.S).group(0)


class ScavHubSections(unittest.TestCase):
    def setUp(self):
        self.t = PAGE.read_text(encoding="utf-8")

    def test_sections_exist_with_headings(self):
        self.assertIn(">Aquarium scavenger hunts</h2>", self.t)
        self.assertIn(">Science museum scavenger hunts</h2>", self.t)

    def test_links_are_live_indexed_place_pages(self):
        for sid, minimum in (("aquarium-hunts", 15), ("science-museum-hunts", 10)):
            hrefs = re.findall(r'href="/field-pack/([a-z0-9-]+)/"', section(self.t, sid))
            self.assertGreaterEqual(len(hrefs), minimum, sid)
            self.assertEqual(len(hrefs), len(set(hrefs)), sid)
            for s in hrefs:
                self.assertNotIn(s, NOINDEX)
                page = (ROOT / f"static/field-pack/{s}/index.html").read_text(encoding="utf-8")
                self.assertIn('content="index,follow"', page, s)

    def test_every_indexed_aquarium_listed(self):
        import json
        want = set()
        for p in (ROOT / "static/field-pack/data/venues").glob("*.json"):
            d = json.loads(p.read_text(encoding="utf-8"))
            if d["type"] == "aquarium" and d["slug"] not in NOINDEX:
                want.add(d["slug"])
        got = set(re.findall(r'href="/field-pack/([a-z0-9-]+)/"', section(self.t, "aquarium-hunts")))
        self.assertEqual(got, want)

    def test_copy_rules(self):
        for sid in ("aquarium-hunts", "science-museum-hunts"):
            text = re.sub(r"<[^>]+>", " ", section(self.t, sid)).lower()
            self.assertNotRegex(text, r"\bfree\b|no-cost|\bwe\b|\bour\b|\bus\b")


if __name__ == "__main__":
    unittest.main()
