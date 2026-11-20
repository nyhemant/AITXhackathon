"""Polish 2026-11-20: internal links go straight to the final URL, not through a 301."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from busyparent_agent.url_aliases import PRINT_TARGET, redirect_location  # noqa: E402


class DirectLinks(unittest.TestCase):
    def test_print_from_watch_links_go_to_the_final_url(self):
        for rel in ("static/about/index.html", "static/field-pack/cards/index.html"):
            html = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn(f'href="{PRINT_TARGET}"', html, rel)
            self.assertNotIn('href="/field-pack/print/"', html, rel)

    def test_the_301_itself_still_works(self):
        self.assertEqual(redirect_location("/field-pack/print/"), PRINT_TARGET)


if __name__ == "__main__":
    unittest.main()
