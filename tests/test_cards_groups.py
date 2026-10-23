"""Cards hub 'Browse by group' (2026-10-23, scripts/cards_hub_groups.py)."""
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HUB = REPO / "static" / "field-pack" / "cards" / "index.html"


class CardsGroupsTest(unittest.TestCase):
    def setUp(self):
        self.html = HUB.read_text(encoding="utf-8")

    def test_chips_are_plain_anchors_to_existing_targets(self):
        chips = re.findall(r'<a class="cards-group-chip" href="/field-pack/cards/#(g-[a-z]+)"[^>]*data-related-link="group"', self.html)
        self.assertEqual(chips, ["g-mammals", "g-birds", "g-reptiles", "g-ocean", "g-museum"])
        for c in chips:
            self.assertEqual(self.html.count(f'id="{c}"'), 1, c)
        # chips sit in the hero, before the grid
        self.assertLess(self.html.find("cards-groups"), self.html.find('id="cards-accordion"'))

    def test_every_hub_card_in_exactly_one_group(self):
        groups = {}
        body = self.html[self.html.find('id="cards-accordion"'):]
        cuts = [(m.start(), m.group(1)) for m in re.finditer(r'id="(g-[a-z]+)"', body)]
        self.assertEqual([c for _, c in cuts], ["g-mammals", "g-birds", "g-reptiles", "g-ocean", "g-museum"])
        cuts.append((len(body), None))
        seen = []
        for (s, gid), (e, _) in zip(cuts, cuts[1:]):
            ids = re.findall(r'<li class="cards-hub-item" data-card-id="([^"]+)"', body[s:e])
            self.assertTrue(ids, gid)
            groups[gid] = ids
            seen += ids
        self.assertEqual(len(seen), len(set(seen)))
        self.assertEqual(len(seen), self.html.count('<li class="cards-hub-item"'))
        self.assertIn("zebra", groups["g-mammals"])
        self.assertIn("ostrich", groups["g-birds"])
        self.assertIn("galapagos-tortoise", groups["g-reptiles"])
        self.assertIn("octopus", groups["g-ocean"])
        self.assertIn("sci-dinosaur", groups["g-museum"])

    def test_tiles_use_card_page_photo_url(self):
        for cid, src in re.findall(r'data-card-id="([^"]+)"[^>]*><a[^>]*><img class="cards-hub-thumb" src="([^"]+)"', self.html):
            page = (HUB.parent / cid / "index.html").read_text(encoding="utf-8")
            hero = re.search(r'class="card-page-photo" src="([^"]+)"', page).group(1)
            self.assertEqual(src, hero, cid)

    def test_assets_and_tracking(self):
        self.assertIn("/field-pack/css/cards-groups.css?v=1", self.html)
        self.assertIn("/field-pack/js/cards-groups.js?v=1", self.html)
        self.assertIn("/shell/related-links.js?v=1", self.html)
        self.assertIn('id="cards-hub-search"', self.html)
        self.assertIn("qr-welcome.js", self.html)
        for img in re.findall(r"<img [^>]*>", self.html):
            self.assertIn("width=", img)
            self.assertIn("height=", img)


if __name__ == "__main__":
    unittest.main()
