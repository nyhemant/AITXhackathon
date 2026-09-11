"""Everglades ↔ alligator rails + reverse sides for Teton / Rocky / Badlands."""

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
    animals_pointing_to_park,
    load_animal_park_links,
    park_animals_html,
    parks_for_animal,
)
from study_cards import study_try_next_html, study_try_next_ids  # noqa: E402

FP = REPO / "static" / "field-pack"
GATOR = FP / "cards" / "american-alligator" / "index.html"
CLOWNFISH = FP / "cards" / "clownfish" / "index.html"
EVERGLADES = FP / "everglades" / "index.html"
GRAND_TETON = FP / "grand-teton" / "index.html"
ROCKY = FP / "rocky-mountain" / "index.html"
BADLANDS = FP / "badlands" / "index.html"
LINKS = FP / "data" / "animal-park-links.json"
BIG_CYPRESS = FP / "big-cypress" / "index.html"


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


class EvergladesAnimalParkRailsTests(unittest.TestCase):
    def test_graph_is_strong_sourced_and_bidirectional(self):
        gator_parks = parks_for_animal("american-alligator")
        self.assertEqual([p["id"] for p in gator_parks], ["everglades"])
        self.assertTrue(gator_parks[0]["primary"])
        self.assertEqual(gator_parks[0]["source"], "https://www.nps.gov/ever/learn/nature/alligator.htm")
        self.assertEqual(
            [a["id"] for a in animals_for_park("everglades")],
            ["american-alligator", "sea-turtle"],
        )
        self.assertEqual(parks_for_animal("clownfish"), [])
        self.assertEqual(animal_park_rail_html("clownfish"), "")
        raw = LINKS.read_text(encoding="utf-8")
        self.assertIn("nps.gov/ever", raw)
        self.assertNotIn("big-cypress", raw)
        self.assertFalse(BIG_CYPRESS.is_file())
        self.assertNotIn('"clownfish"', raw)
        data = load_animal_park_links()
        self.assertNotIn("clownfish", data.get("animals") or {})
        self.assertNotIn("big-cypress", data.get("parks") or {})
        for park_id, meta in (data.get("parks") or {}).items():
            listed = [str(x) for x in (meta.get("animals") or [])]
            incoming = animals_pointing_to_park(park_id)
            self.assertEqual(sorted(listed), sorted(incoming), park_id)
            self.assertTrue(str(meta.get("source") or "").startswith("https://www.nps.gov/"))

    def test_card_helper_is_a_second_rail_not_try_next(self):
        rail = animal_park_rail_html("american-alligator")
        nxt = study_try_next_html("american-alligator")
        self.assertIn('data-rail="parks"', rail)
        self.assertIn(CARD_PARK_RAIL_KICKER, rail)
        self.assertIn('href="/field-pack/everglades/"', rail)
        self.assertIn("np-hero-everglades.jpg", rail)
        self.assertNotIn("big-cypress", rail)
        self.assertNotIn("/field-pack/cards/freshwater-fish/", rail)
        self.assertIn("Try next", nxt)
        self.assertIn("/field-pack/cards/freshwater-fish/", nxt)
        self.assertNotIn("everglades", nxt)
        self.assertNotIn("Junior Ranger", rail)
        self.assertNotIn("Park Ranger", rail)
        self.assertNotIn("Zoologist", rail)

    def test_published_alligator_card_keeps_try_next_and_adds_everglades(self):
        gator = GATOR.read_text(encoding="utf-8")
        clown = CLOWNFISH.read_text(encoding="utf-8")
        gator_main = _main(gator)
        self.assertIn('data-rail="parks"', gator_main)
        self.assertNotIn('data-rail="parks"', clown)
        self.assertIn(CARD_PARK_RAIL_KICKER, gator_main)
        self.assertLess(gator_main.find("Try next"), gator_main.find('data-rail="parks"'))
        rail = _park_rail(gator_main)
        self.assertIn('href="/field-pack/everglades/"', rail)
        self.assertIn("np-hero-everglades.jpg", rail)
        self.assertNotIn("big-cypress", rail)
        self.assertIn("/field-pack/cards/freshwater-fish/", gator_main)
        self.assertEqual(
            study_try_next_ids("american-alligator"),
            ["galapagos-tortoise", "african-lion", "reticulated-giraffe"],
        )
        self.assertNotIn("Junior Ranger", rail)
        self.assertNotIn('data-study-pick="easy"', rail)

    def test_everglades_page_adds_alligator_without_rewriting_boardwalk(self):
        html = EVERGLADES.read_text(encoding="utf-8")
        vis = _visible_venue(html)
        section = _animals_section(html)
        self.assertIn(PARK_ANIMALS_H2, section)
        self.assertIn('href="/field-pack/cards/american-alligator/"', section)
        self.assertIn("photos/american-alligator.jpg", section)
        self.assertIn("stay on the path", section.lower())
        self.assertIn("water edge", section.lower())
        self.assertIn("Anhinga boardwalk", vis)
        self.assertIn("Sawgrass and slough views", vis)
        self.assertIn("seo-start-here", vis)
        hunt = vis.split('id="hunt-heading"', 1)[1].split("</section>", 1)[0]
        self.assertIn("Find: Anhinga boardwalk", hunt)
        self.assertIn("Pick your favorite Everglades stop — draw it later", hunt)
        self.assertLess(vis.find('id="start-here"'), vis.find("id=\"animals-you-might-meet\""))
        self.assertNotIn("Junior Ranger", section)
        self.assertNotIn("Park Ranger", section)
        self.assertNotIn("Zoologist", section)
        self.assertNotIn("clownfish", section.lower())
        self.assertNotIn("big-cypress", vis.lower())

    def test_reverse_park_pages_list_animals_already_pointing_at_them(self):
        pages = (
            (GRAND_TETON, ["american-bison", "elk"], "Craig Thomas or Jenny Lake visitor center"),
            (ROCKY, ["elk"], "Start at Beaver Meadows Visitor Center"),
            (BADLANDS, ["american-bison"], "Find: Ben Reifel / Badlands visitor center"),
        )
        for path, animal_ids, hunt_keep in pages:
            html = path.read_text(encoding="utf-8")
            vis = _visible_venue(html)
            section = _animals_section(html)
            self.assertIn(PARK_ANIMALS_H2, section, path.name)
            for cid in animal_ids:
                self.assertIn(f'href="/field-pack/cards/{cid}/"', section)
                self.assertIn(f"photos/{cid}.jpg", section)
            self.assertIn("Sightings", section)
            self.assertTrue(
                "far back" in section.lower() or "far from" in section.lower(),
                section,
            )
            hunt = vis.split('id="hunt-heading"', 1)[1].split("</section>", 1)[0]
            self.assertIn(hunt_keep, hunt)
            self.assertLess(vis.find('id="start-here"'), vis.find("id=\"animals-you-might-meet\""))
            self.assertNotIn("Junior Ranger", section)
            self.assertNotIn("Park Ranger", section)
            self.assertNotIn("Zoologist", section)
            self.assertNotIn("clownfish", section.lower())
            self.assertTrue(park_animals_html(path.parent.name))


if __name__ == "__main__":
    unittest.main()
