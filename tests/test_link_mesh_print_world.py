"""2026-10-28 internal links: card -> its reviewed printable, world slots in "Where to see",
and reciprocal nearby links so far-away place pages are not orphaned."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FP = ROOT / "static" / "field-pack"
DATA = json.loads((ROOT / "data" / "quiz_printables.json").read_text(encoding="utf-8"))
THIN = ["helsinki-zoo", "johannesburg-zoo", "moscow-zoo", "nairobi-safari-walk", "stockholm-skansen", "voyageurs"]


def _block(s: str, name: str) -> str:
    m = re.search(rf"<!-- kz-mesh:{name} -->(.*?)<!-- /kz-mesh:{name} -->", s, re.S)
    return m.group(1) if m else ""


class PrintLinkTests(unittest.TestCase):
    def test_every_mapped_card_links_its_one_printable(self):
        self.assertEqual(len(DATA["cards"]), 42)
        for cid, row in DATA["cards"].items():
            s = (FP / "cards" / cid / "index.html").read_text(encoding="utf-8")
            blk = _block(s, "print")
            with self.subTest(card=cid):
                hrefs = re.findall(r'href="(/printables/[a-z-]+/)"', blk)
                self.assertEqual(hrefs, [DATA["pages"][row["sheet"]]["href"]])
                self.assertIn('data-related-link="printable"', blk)

    def test_unmapped_cards_have_no_print_block(self):
        for d in sorted((FP / "cards").iterdir()):
            if d.is_dir() and d.name not in DATA["cards"] and (d / "index.html").exists():
                with self.subTest(card=d.name):
                    self.assertNotIn("kz-mesh:print", (d / "index.html").read_text(encoding="utf-8"))


class WhereAndNearbyTests(unittest.TestCase):
    def test_where_lists_stay_at_most_eight(self):
        for f in (FP / "cards").glob("*/index.html"):
            n = _block(f.read_text(encoding="utf-8"), "where").count('data-related-link="place"')
            self.assertLessEqual(n, 8, f.parent.name)

    def test_thin_places_have_at_least_three_page_links_in(self):
        inbound = {s: set() for s in THIN}
        for f in FP.glob("**/index.html"):
            s = f.read_text(encoding="utf-8")
            src = f.parent.name
            for name in ("explore", "where"):
                for slug in re.findall(r'href="/field-pack/([a-z0-9-]+)/"', _block(s, name)):
                    if slug in inbound and slug != src:
                        inbound[slug].add(src)
        for slug, srcs in inbound.items():
            with self.subTest(place=slug):
                self.assertGreaterEqual(len(srcs), 3, sorted(srcs))

    def test_nearby_lists_capped(self):
        for f in FP.glob("*/index.html"):
            blk = _block(f.read_text(encoding="utf-8"), "explore")
            for ul in re.findall(r"<h3>(?:Nearby and similar places|More [^<]+ to explore)</h3><ul>(.*?)</ul>", blk):
                self.assertLessEqual(ul.count("<li>"), 6, f.parent.name)


if __name__ == "__main__":
    unittest.main()
