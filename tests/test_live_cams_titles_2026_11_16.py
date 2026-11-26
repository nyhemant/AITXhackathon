"""/start/ and the Virtual Field Trip no longer share "Live Cams" in their titles (2026-11-16)."""
from __future__ import annotations

import html
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START = ROOT / "static" / "start" / "index.html"
VFT = ROOT / "static" / "field-pack" / "virtual-field-trip" / "index.html"
FREE_RE = re.compile(r"\b(free|no-cost)\b", re.IGNORECASE)
WE_RE = re.compile(r"\b(we|our|us)\b", re.IGNORECASE)


def _title(path: Path) -> str:
    found = re.findall(r"<title>(.*?)</title>", path.read_text(encoding="utf-8"), re.S)
    assert len(found) == 1, path
    return html.unescape(found[0].strip())


class LiveCamsTitleOverlap(unittest.TestCase):
    def test_titles_are_distinct_and_only_vft_says_live_cams(self):
        start, vft = _title(START), _title(VFT)
        self.assertEqual(start, "Zoo, Aquarium & Museum Scavenger Hunts for Kids | KidZooKit")
        self.assertEqual(vft, "Virtual Field Trip for Kids: Live Cams & Films | KidZooKit")
        self.assertNotEqual(start, vft)
        self.assertNotIn("live cams", start.lower())
        self.assertIn("Live Cams", vft)
        for t in (start, vft):
            self.assertLessEqual(len(t), 60)
            self.assertIsNone(FREE_RE.search(t))
            self.assertIsNone(WE_RE.search(t))

    def test_start_title_matches_the_hunts_h1(self):
        # 2026-11-26 Gemini SEO consult: the scavenger test freeze ended Nov 20, so the
        # title now matches the visible H1 ("Printable scavenger hunts for your next zoo,
        # aquarium or museum trip"); "Printable" leads the meta description, since the
        # hub title must also keep "for Kids" within 60 characters.
        start = _title(START).lower()
        self.assertIn("scavenger hunts", start)
        for word in ("zoo", "aquarium", "museum"):
            self.assertIn(word, start)
        self.assertNotIn("virtual zoo", start)

    def test_start_heads_match(self):
        page = START.read_text(encoding="utf-8")
        title = "Zoo, Aquarium &amp; Museum Scavenger Hunts for Kids | KidZooKit"
        self.assertIn(f'<meta property="og:title" content="{title}" />', page)
        self.assertIn(f'<meta name="twitter:title" content="{title}" />', page)
        # 2026-11-18 landing pass: H1 is the visible hunts headline; title/og/twitter stay as above.
        self.assertIn('<h1 id="start-heading">Printable scavenger hunts for your next zoo, aquarium or museum trip</h1>', page)
        self.assertIn("Arya", page)


if __name__ == "__main__":
    unittest.main()
