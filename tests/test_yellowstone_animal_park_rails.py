"""Yellowstone ↔ bison/elk bidirectional suggestion rails (PoC)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from animal_park_links import (  # noqa: E402
    CARD_PARK_RAIL_KICKER,
    PARK_ANIMALS_H2,
    animal_park_rail_html,
    animals_for_park,
    load_animal_park_links,
    park_animals_html,
    parks_for_animal,
)
from study_cards import study_try_next_html, study_try_next_ids  # noqa: E402

FP = REPO / "static" / "field-pack"
GENERATOR = REPO / "scripts" / "generate_bdo_seo.py"
BISON = FP / "cards" / "american-bison" / "index.html"
ELK = FP / "cards" / "elk" / "index.html"
CLOWNFISH = FP / "cards" / "clownfish" / "index.html"
YELLOWSTONE = FP / "yellowstone" / "index.html"
LINKS = FP / "data" / "animal-park-links.json"
STUDY_JS = FP / "js" / "study-card.js"


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


def _visible_venue(html: str) -> str:
    return html.split('id="venue-data"', 1)[0]


def _park_rail(html: str) -> str:
    start = html.find('data-rail="parks"')
    if start < 0:
        return ""
    chunk = html[start:]
    end = chunk.find("</nav>")
    return chunk[: end + len("</nav>")]


def _animals_section(html: str) -> str:
    vis = _visible_venue(html)
    start = vis.find('id="animals-you-might-meet"')
    if start < 0:
        return ""
    return vis[start:].split("</section>", 1)[0]


class YellowstoneAnimalParkRailsTests(unittest.TestCase):
    def test_graph_is_strong_sourced_and_bidirectional(self):
        bison_parks = parks_for_animal("american-bison")
        elk_parks = parks_for_animal("elk")
        self.assertEqual([p["id"] for p in bison_parks], ["yellowstone", "badlands", "grand-teton"])
        self.assertTrue(bison_parks[0]["primary"])
        self.assertEqual(bison_parks[0]["id"], "yellowstone")
        self.assertEqual(
            [p["id"] for p in elk_parks],
            ["yellowstone", "banff", "grand-teton", "jasper", "rocky-mountain"],
        )
        self.assertTrue(elk_parks[0]["primary"])
        self.assertEqual([a["id"] for a in animals_for_park("yellowstone")], ["american-bison", "elk"])
        self.assertEqual([a["id"] for a in animals_for_park("grand-teton")], ["american-bison", "elk"])
        self.assertEqual([a["id"] for a in animals_for_park("rocky-mountain")], ["elk"])
        self.assertEqual([a["id"] for a in animals_for_park("badlands")], ["american-bison"])
        self.assertEqual(parks_for_animal("clownfish"), [])
        self.assertEqual(animal_park_rail_html("clownfish"), "")
        raw = LINKS.read_text(encoding="utf-8")
        self.assertIn("nps.gov/yell", raw)
        self.assertNotIn('"clownfish"', raw)
        self.assertNotIn("clownfish", load_animal_park_links().get("animals") or {})

    def test_card_helper_is_a_second_rail_not_try_next(self):
        rail = animal_park_rail_html("american-bison")
        nxt = study_try_next_html("american-bison")
        self.assertIn('data-rail="parks"', rail)
        self.assertIn(CARD_PARK_RAIL_KICKER, rail)
        self.assertIn('href="/field-pack/yellowstone/"', rail)
        self.assertIn("np-hero-yellowstone.jpg", rail)
        self.assertIn('href="/field-pack/grand-teton/"', rail)
        self.assertIn('href="/field-pack/badlands/"', rail)
        self.assertNotIn("/field-pack/cards/zebra/", rail)
        self.assertIn("Try next", nxt)
        self.assertIn("/field-pack/cards/zebra/", nxt)
        self.assertNotIn("yellowstone", nxt)
        self.assertNotIn("Junior Ranger", rail)
        self.assertNotIn("Park Ranger", rail)
        self.assertNotIn("Zoologist", rail)

    def test_published_bison_and_elk_cards_keep_try_next_and_add_parks(self):
        bison = BISON.read_text(encoding="utf-8")
        elk = ELK.read_text(encoding="utf-8")
        clown = CLOWNFISH.read_text(encoding="utf-8")
        bison_main = _main(bison)
        elk_main = _main(elk)
        self.assertIn('data-rail="parks"', bison_main)
        self.assertIn('data-rail="parks"', elk_main)
        self.assertNotIn('data-rail="parks"', clown)
        self.assertIn(CARD_PARK_RAIL_KICKER, bison_main)
        self.assertIn(CARD_PARK_RAIL_KICKER, elk_main)
        self.assertLess(bison_main.find("Try next"), bison_main.find('data-rail="parks"'))
        self.assertLess(elk_main.find("Try next"), elk_main.find('data-rail="parks"'))
        bison_rail = _park_rail(bison_main)
        elk_rail = _park_rail(elk_main)
        self.assertIn('href="/field-pack/yellowstone/"', bison_rail)
        self.assertIn('href="/field-pack/yellowstone/"', elk_rail)
        self.assertIn("np-hero-yellowstone.jpg", bison_rail)
        self.assertIn("np-hero-yellowstone.jpg", elk_rail)
        self.assertIn("/field-pack/cards/zebra/", bison_main)
        self.assertIn("/field-pack/cards/american-bison/", elk_main)
        self.assertEqual(
            study_try_next_ids("american-bison"),
            ["zebra", "warthog", "african-lion"],
        )
        self.assertEqual(
            study_try_next_ids("elk"),
            ["american-bison", "zebra", "african-lion"],
        )
        self.assertNotIn("Junior Ranger", bison_rail)
        self.assertNotIn('data-study-pick="easy"', bison_rail)

    def test_yellowstone_page_adds_animal_thumbs_without_rewriting_basin(self):
        html = YELLOWSTONE.read_text(encoding="utf-8")
        vis = _visible_venue(html)
        section = _animals_section(html)
        self.assertIn(PARK_ANIMALS_H2, section)
        self.assertIn('href="/field-pack/cards/american-bison/"', section)
        self.assertIn('href="/field-pack/cards/elk/"', section)
        self.assertIn("photos/american-bison.jpg", section)
        self.assertIn("photos/elk.jpg", section)
        self.assertIn("Give wildlife lots of space", section)
        self.assertIn("Old Faithful", vis)
        self.assertIn("Castle Geyser", vis)
        self.assertIn("seo-start-here", vis)
        hunt = vis.split('id="hunt-heading"', 1)[1].split("</section>", 1)[0]
        self.assertIn("Find Old Faithful’s next predicted time", hunt)
        self.assertIn("Favorite basin stop — draw the steam later", hunt)
        self.assertLess(vis.find("id=\"start-here\""), vis.find("id=\"animals-you-might-meet\""))
        self.assertNotIn("Junior Ranger", section)
        self.assertNotIn("Park Ranger", section)
        self.assertNotIn("Zoologist", section)
        self.assertNotIn("clownfish", section.lower())

    def test_generator_and_try_next_js_keep_rails_separate(self):
        gen = GENERATOR.read_text(encoding="utf-8")
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("animal_park_rail_html", gen)
        self.assertIn("park_animals_html(vid)", gen)
        self.assertIn("{park_rail_html}", gen)
        self.assertIn("card-park-rail", js)
        self.assertIn("function paintTryNext(", js)


if __name__ == "__main__":
    unittest.main()
