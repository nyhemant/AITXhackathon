"""Wave B international animal ↔ park rails (strong, sourced only)."""

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
LINKS = FP / "data" / "animal-park-links.json"
CLOWNFISH = FP / "cards" / "clownfish" / "index.html"
KILLARNEY = FP / "killarney" / "index.html"
TABLE_MOUNTAIN = FP / "table-mountain" / "index.html"

CARDS = {
    "african-lion": FP / "cards" / "african-lion" / "index.html",
    "african-elephant": FP / "cards" / "african-elephant" / "index.html",
    "zebra": FP / "cards" / "zebra" / "index.html",
    "reticulated-giraffe": FP / "cards" / "reticulated-giraffe" / "index.html",
    "warthog": FP / "cards" / "warthog" / "index.html",
    "elk": FP / "cards" / "elk" / "index.html",
}

PARKS = {
    "kruger": FP / "kruger" / "index.html",
    "banff": FP / "banff" / "index.html",
    "jasper": FP / "jasper" / "index.html",
}

HUNT_KEEP = {
    "kruger": "Find: Rest camp paths",
    "banff": "Find: Lake Louise shoreline",
    "jasper": "Find: Jasper visitor center",
}

PARK_ANIMALS = {
    "kruger": ["african-lion", "african-elephant", "zebra", "reticulated-giraffe", "warthog"],
    "banff": ["elk"],
    "jasper": ["elk"],
}

KRUGER_SOURCE = "https://www.sanparks.org/parks/kruger/explore/fauna-flora/mammals"
BANFF_ELK_SOURCE = (
    "https://parks.canada.ca/pn-np/ab/banff/nature/faune-wildlife/mammal/ongules/cervids/wapiti"
)
JASPER_ELK_SOURCE = (
    "https://parks.canada.ca/pn-np/ab/jasper/nature/faune-wildlife/cervides-deer"
)

STUDY_DECK_ANIMALS = (
    "african-lion",
    "african-elephant",
    "zebra",
    "reticulated-giraffe",
    "warthog",
    "elk",
)

FORBIDDEN_PARKS = (
    "killarney",
    "table-mountain",
    "serengeti",
    "galapagos",
    "koala",
    "giant-panda",
    "panda",
)


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


def _official_source(url: str) -> bool:
    return str(url or "").startswith(
        (
            "https://www.nps.gov/",
            "https://www.sanparks.org/",
            "https://parks.canada.ca/",
        )
    )


class IntlAnimalParkRailsTests(unittest.TestCase):
    def test_graph_is_strong_sourced_and_bidirectional(self):
        self.assertEqual([p["id"] for p in parks_for_animal("african-lion")], ["kruger"])
        self.assertTrue(parks_for_animal("african-lion")[0]["primary"])
        self.assertEqual(parks_for_animal("african-lion")[0]["source"], KRUGER_SOURCE)
        self.assertEqual([p["id"] for p in parks_for_animal("african-elephant")], ["kruger"])
        self.assertEqual([p["id"] for p in parks_for_animal("zebra")], ["kruger"])
        self.assertEqual([p["id"] for p in parks_for_animal("reticulated-giraffe")], ["kruger"])
        self.assertEqual([p["id"] for p in parks_for_animal("warthog")], ["kruger"])
        self.assertEqual(
            [p["id"] for p in parks_for_animal("elk")],
            ["yellowstone", "banff", "grand-teton", "jasper", "rocky-mountain"],
        )
        self.assertTrue(parks_for_animal("elk")[0]["primary"])
        self.assertEqual(parks_for_animal("elk")[0]["id"], "yellowstone")
        elk_by_id = {p["id"]: p for p in parks_for_animal("elk")}
        self.assertEqual(elk_by_id["banff"]["source"], BANFF_ELK_SOURCE)
        self.assertEqual(elk_by_id["jasper"]["source"], JASPER_ELK_SOURCE)
        self.assertEqual(elk_by_id["yellowstone"]["source"], "https://www.nps.gov/yell/learn/nature/elk.htm")
        self.assertEqual(parks_for_animal("clownfish"), [])
        self.assertEqual(animal_park_rail_html("clownfish"), "")

        for park_id, animal_ids in PARK_ANIMALS.items():
            self.assertEqual(
                [a["id"] for a in animals_for_park(park_id)],
                animal_ids,
                park_id,
            )

        data = load_animal_park_links()
        raw = LINKS.read_text(encoding="utf-8")
        self.assertNotIn("clownfish", data.get("animals") or {})
        self.assertNotIn('"clownfish"', raw)
        for forbidden in FORBIDDEN_PARKS:
            self.assertNotIn(f'"{forbidden}"', raw, forbidden)
        self.assertNotIn("killarney", {p["id"] for p in parks_for_animal("elk")})
        self.assertTrue(KILLARNEY.is_file())
        self.assertTrue(TABLE_MOUNTAIN.is_file())
        self.assertNotIn("table-mountain", {p["id"] for p in parks_for_animal("african-penguin")})
        self.assertEqual(parks_for_animal("giant-panda"), [])
        self.assertEqual(parks_for_animal("koala"), [])

        for park_id, meta in (data.get("parks") or {}).items():
            listed = [str(x) for x in (meta.get("animals") or [])]
            incoming = animals_pointing_to_park(park_id)
            self.assertEqual(sorted(listed), sorted(incoming), park_id)
            self.assertTrue(_official_source(str(meta.get("source") or "")), park_id)
        for cid, meta in (data.get("animals") or {}).items():
            for edge in meta.get("parks") or []:
                self.assertTrue(
                    _official_source(str(edge.get("source") or "")),
                    f"{cid} → {edge.get('id')}",
                )

        self.assertEqual((data.get("parks") or {}).get("kruger", {}).get("source"), KRUGER_SOURCE)
        self.assertEqual((data.get("parks") or {}).get("banff", {}).get("source"), BANFF_ELK_SOURCE)
        self.assertEqual((data.get("parks") or {}).get("jasper", {}).get("source"), JASPER_ELK_SOURCE)

    def test_card_helpers_are_a_second_rail_not_try_next(self):
        for cid in STUDY_DECK_ANIMALS:
            rail = animal_park_rail_html(cid)
            nxt = study_try_next_html(cid)
            self.assertIn('data-rail="parks"', rail, cid)
            self.assertIn(CARD_PARK_RAIL_KICKER, rail)
            self.assertIn("Try next", nxt)
            self.assertNotIn("Junior Ranger", rail)
            self.assertNotIn("Park Ranger", rail)
            self.assertNotIn("Zoologist", rail)
            for park in parks_for_animal(cid):
                self.assertNotIn(park["id"], nxt)
                self.assertIn(f'href="/field-pack/{park["id"]}/"', rail)
        self.assertIn("np-hero-kruger.jpg", animal_park_rail_html("african-lion"))
        self.assertIn("np-hero-banff.jpg", animal_park_rail_html("elk"))
        self.assertIn("np-hero-jasper.jpg", animal_park_rail_html("elk"))
        self.assertIn("np-hero-yellowstone.jpg", animal_park_rail_html("elk"))
        self.assertIn("/field-pack/cards/reticulated-giraffe/", study_try_next_html("african-lion"))
        self.assertEqual(
            study_try_next_ids("african-lion"),
            ["reticulated-giraffe", "african-elephant", "african-penguin"],
        )
        self.assertEqual(
            study_try_next_ids("african-elephant"),
            ["reticulated-giraffe", "african-lion", "african-penguin"],
        )
        self.assertEqual(
            study_try_next_ids("reticulated-giraffe"),
            ["african-elephant", "african-lion", "african-penguin"],
        )
        self.assertEqual(
            study_try_next_ids("zebra"),
            ["african-lion", "reticulated-giraffe", "african-elephant"],
        )
        self.assertEqual(
            study_try_next_ids("warthog"),
            ["zebra", "ostrich", "african-lion"],
        )
        self.assertEqual(
            study_try_next_ids("elk"),
            ["american-bison", "zebra", "african-lion"],
        )

    def test_published_intl_cards_add_park_rails(self):
        clown = CLOWNFISH.read_text(encoding="utf-8")
        self.assertNotIn('data-rail="parks"', clown)
        for cid, path in CARDS.items():
            html = path.read_text(encoding="utf-8")
            main = _main(html)
            self.assertIn('data-rail="parks"', main, cid)
            self.assertIn(CARD_PARK_RAIL_KICKER, main)
            rail = _park_rail(main)
            self.assertTrue(rail, cid)
            for park in parks_for_animal(cid):
                self.assertIn(f'href="/field-pack/{park["id"]}/"', rail)
                self.assertIn(f"np-hero-{park['id']}.jpg", rail)
            for forbidden in ("killarney", "table-mountain", "serengeti"):
                self.assertNotIn(forbidden, rail)
            self.assertNotIn("Junior Ranger", rail)
            self.assertNotIn("Park Ranger", rail)
            self.assertNotIn("Zoologist", rail)
            self.assertNotIn('data-study-pick="easy"', rail)
            if cid in STUDY_DECK_ANIMALS:
                self.assertLess(main.find("Try next"), main.find('data-rail="parks"'), cid)
        lion_rail = _park_rail(_main(CARDS["african-lion"].read_text(encoding="utf-8")))
        self.assertIn("kruger", lion_rail)
        self.assertNotIn("yellowstone", lion_rail)
        elk_rail = _park_rail(_main(CARDS["elk"].read_text(encoding="utf-8")))
        self.assertIn("yellowstone", elk_rail)
        self.assertIn("banff", elk_rail)
        self.assertIn("jasper", elk_rail)
        self.assertIn("rocky-mountain", elk_rail)
        self.assertIn("grand-teton", elk_rail)
        self.assertNotIn("killarney", elk_rail)

    def test_park_pages_list_animals_without_rewriting_hunts(self):
        for park_id, path in PARKS.items():
            html = path.read_text(encoding="utf-8")
            vis = _visible_venue(html)
            section = _animals_section(html)
            self.assertIn(PARK_ANIMALS_H2, section, park_id)
            for cid in PARK_ANIMALS[park_id]:
                self.assertIn(f'href="/field-pack/cards/{cid}/"', section)
                self.assertIn(f"photos/{cid}.jpg", section)
            self.assertIn("Sightings", section)
            self.assertTrue(
                "far" in section.lower()
                or "distance" in section.lower()
                or "stay in the car" in section.lower(),
                section,
            )
            hunt = vis.split('id="hunt-heading"', 1)[1].split("</section>", 1)[0]
            self.assertIn(HUNT_KEEP[park_id], hunt)
            self.assertLess(vis.find('id="start-here"'), vis.find('id="animals-you-might-meet"'))
            self.assertNotIn("Junior Ranger", section)
            self.assertNotIn("Park Ranger", section)
            self.assertNotIn("Zoologist", section)
            self.assertNotIn("clownfish", section.lower())
            self.assertNotIn("killarney", vis.lower())
            self.assertTrue(park_animals_html(park_id))
        kruger = _animals_section(PARKS["kruger"].read_text(encoding="utf-8"))
        self.assertIn("not on foot outside camp", kruger)
        self.assertNotIn("elk", kruger)
        banff = _animals_section(PARKS["banff"].read_text(encoding="utf-8"))
        self.assertIn("elk", banff)
        self.assertNotIn("african-lion", banff)
        jasper = _animals_section(PARKS["jasper"].read_text(encoding="utf-8"))
        self.assertIn("elk", jasper)
        self.assertNotIn("african-lion", jasper)


if __name__ == "__main__":
    unittest.main()
