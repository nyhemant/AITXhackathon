"""Wave C exotic animal ↔ park rails (strong, sourced only)."""

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
    is_official_source,
    load_animal_park_links,
    park_animals_html,
    parks_for_animal,
)
from study_cards import study_try_next_html, study_try_next_ids  # noqa: E402

FP = REPO / "static" / "field-pack"
LINKS = FP / "data" / "animal-park-links.json"
CLOWNFISH = FP / "cards" / "clownfish" / "index.html"
BLUE_MOUNTAINS = FP / "blue-mountains" / "index.html"

CARDS = {
    "giant-panda": FP / "cards" / "giant-panda" / "index.html",
    "koala": FP / "cards" / "koala" / "index.html",
    "galapagos-tortoise": FP / "cards" / "galapagos-tortoise" / "index.html",
}

PARKS = {
    "giant-panda-national-park": FP / "giant-panda-national-park" / "index.html",
    "french-island": FP / "french-island" / "index.html",
    "galapagos": FP / "galapagos" / "index.html",
}

HUNT_KEEP = {
    "giant-panda-national-park": "Wolong visitor center",
    "french-island": "Tankerton jetty / visitor info",
    "galapagos": "Santa Cruz visitor center",
}

PARK_ANIMALS = {
    "giant-panda-national-park": ["giant-panda"],
    "french-island": ["koala"],
    "galapagos": ["galapagos-tortoise"],
}

GPNP_SOURCE = "https://www.forestry.gov.cn/c/www/wmdgjgy/119160.jhtml"
FRENCH_SOURCE = "https://www.parks.vic.gov.au/places-to-see/parks/french-island-national-park"
GALAPAGOS_SOURCE = "https://galapagos.gob.ec/parque-nacional-galapagos/"

STUDY_DECK_ANIMALS = ("giant-panda", "koala", "galapagos-tortoise")

FORBIDDEN_PARKS = (
    "blue-mountains",
    "killarney",
    "table-mountain",
    "serengeti",
    "orangutan",
    "african-penguin",
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


class ExoticAnimalParkRailsTests(unittest.TestCase):
    def test_graph_is_strong_sourced_and_bidirectional(self):
        self.assertEqual(
            [p["id"] for p in parks_for_animal("giant-panda")],
            ["giant-panda-national-park"],
        )
        self.assertTrue(parks_for_animal("giant-panda")[0]["primary"])
        self.assertEqual(parks_for_animal("giant-panda")[0]["source"], GPNP_SOURCE)
        self.assertEqual([p["id"] for p in parks_for_animal("koala")], ["french-island"])
        self.assertTrue(parks_for_animal("koala")[0]["primary"])
        self.assertEqual(parks_for_animal("koala")[0]["source"], FRENCH_SOURCE)
        self.assertEqual(
            [p["id"] for p in parks_for_animal("galapagos-tortoise")],
            ["galapagos"],
        )
        self.assertTrue(parks_for_animal("galapagos-tortoise")[0]["primary"])
        self.assertEqual(
            parks_for_animal("galapagos-tortoise")[0]["source"],
            GALAPAGOS_SOURCE,
        )
        self.assertEqual(parks_for_animal("clownfish"), [])
        self.assertEqual(animal_park_rail_html("clownfish"), "")
        self.assertEqual(parks_for_animal("orangutan"), [])
        self.assertEqual(parks_for_animal("african-penguin"), [])

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
        self.assertNotIn('"orangutan"', raw)
        self.assertNotIn('"african-penguin"', raw)
        self.assertNotIn("blue-mountains", {p["id"] for p in parks_for_animal("koala")})
        self.assertNotIn('"blue-mountains"', raw)
        self.assertTrue(BLUE_MOUNTAINS.is_file())
        for forbidden in FORBIDDEN_PARKS:
            self.assertNotIn(f'"{forbidden}"', raw, forbidden)

        self.assertIn("kruger", raw)
        self.assertIn("banff", raw)
        self.assertIn("jasper", raw)
        self.assertEqual([p["id"] for p in parks_for_animal("african-lion")], ["kruger"])
        elk_ids = [p["id"] for p in parks_for_animal("elk")]
        self.assertIn("banff", elk_ids)
        self.assertIn("jasper", elk_ids)
        self.assertIn("yellowstone", elk_ids)

        for park_id, meta in (data.get("parks") or {}).items():
            listed = [str(x) for x in (meta.get("animals") or [])]
            incoming = animals_pointing_to_park(park_id)
            self.assertEqual(sorted(listed), sorted(incoming), park_id)
            self.assertTrue(is_official_source(str(meta.get("source") or "")), park_id)
        for cid, meta in (data.get("animals") or {}).items():
            for edge in meta.get("parks") or []:
                self.assertTrue(
                    is_official_source(str(edge.get("source") or "")),
                    f"{cid} → {edge.get('id')}",
                )

        self.assertEqual(
            (data.get("parks") or {}).get("giant-panda-national-park", {}).get("source"),
            GPNP_SOURCE,
        )
        self.assertEqual(
            (data.get("parks") or {}).get("french-island", {}).get("source"),
            FRENCH_SOURCE,
        )
        self.assertEqual(
            (data.get("parks") or {}).get("galapagos", {}).get("source"),
            GALAPAGOS_SOURCE,
        )

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
        self.assertIn(
            "np-hero-giant-panda-national-park.jpg",
            animal_park_rail_html("giant-panda"),
        )
        self.assertIn("np-hero-french-island.jpg", animal_park_rail_html("koala"))
        self.assertIn("np-hero-galapagos.jpg", animal_park_rail_html("galapagos-tortoise"))
        self.assertEqual(
            study_try_next_ids("giant-panda"),
            ["red-panda", "koala", "african-lion"],
        )
        self.assertEqual(
            study_try_next_ids("koala"),
            ["red-panda", "sumatran-tiger", "african-lion"],
        )
        self.assertEqual(
            study_try_next_ids("galapagos-tortoise"),
            ["african-elephant", "reticulated-giraffe", "african-lion"],
        )

    def test_published_exotic_cards_add_park_rails(self):
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
            for forbidden in ("blue-mountains", "killarney", "table-mountain", "serengeti"):
                self.assertNotIn(forbidden, rail)
            self.assertNotIn("Junior Ranger", rail)
            self.assertNotIn("Park Ranger", rail)
            self.assertNotIn("Zoologist", rail)
            self.assertNotIn('data-study-pick="easy"', rail)
            if cid in STUDY_DECK_ANIMALS:
                self.assertLess(main.find("Try next"), main.find('data-rail="parks"'), cid)
        panda_rail = _park_rail(_main(CARDS["giant-panda"].read_text(encoding="utf-8")))
        self.assertIn("giant-panda-national-park", panda_rail)
        self.assertNotIn("san-diego-zoo", panda_rail)
        koala_rail = _park_rail(_main(CARDS["koala"].read_text(encoding="utf-8")))
        self.assertIn("french-island", koala_rail)
        self.assertNotIn("blue-mountains", koala_rail)
        tortoise_rail = _park_rail(_main(CARDS["galapagos-tortoise"].read_text(encoding="utf-8")))
        self.assertIn("galapagos", tortoise_rail)
        self.assertNotIn("dry-tortugas", tortoise_rail)

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
                or "don’t touch" in section.lower(),
                section,
            )
            hunt = vis.split('id="hunt-heading"', 1)[1].split("</section>", 1)[0]
            self.assertIn(HUNT_KEEP[park_id], hunt)
            self.assertLess(vis.find('id="start-here"'), vis.find('id="animals-you-might-meet"'))
            self.assertNotIn("Junior Ranger", section)
            self.assertNotIn("Park Ranger", section)
            self.assertNotIn("Zoologist", section)
            self.assertNotIn("clownfish", section.lower())
            self.assertNotIn("orangutan", section.lower())
            self.assertTrue(park_animals_html(park_id))
        panda_park = _animals_section(PARKS["giant-panda-national-park"].read_text(encoding="utf-8"))
        self.assertIn("not a zoo hall", panda_park)
        self.assertNotIn("koala", panda_park)
        french = _animals_section(PARKS["french-island"].read_text(encoding="utf-8"))
        self.assertIn("koala", french)
        self.assertNotIn("giant-panda", french)
        galapagos = _animals_section(PARKS["galapagos"].read_text(encoding="utf-8"))
        self.assertIn("galapagos-tortoise", galapagos)
        self.assertNotIn("giant-panda", galapagos)


if __name__ == "__main__":
    unittest.main()
