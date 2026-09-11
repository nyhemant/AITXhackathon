"""Wave A marine/coastal animal ↔ park rails (strong, sourced only)."""

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
PADRE = FP / "padre-island"
ACADIA = FP / "acadia" / "index.html"

CARDS = {
    "sea-turtle": FP / "cards" / "sea-turtle" / "index.html",
    "shark": FP / "cards" / "shark" / "index.html",
    "crab": FP / "cards" / "crab" / "index.html",
    "starfish": FP / "cards" / "starfish" / "index.html",
    "seahorse": FP / "cards" / "seahorse" / "index.html",
    "octopus": FP / "cards" / "octopus" / "index.html",
    "stingray": FP / "cards" / "stingray" / "index.html",
    "kelp-forest": FP / "cards" / "kelp-forest" / "index.html",
    "sea-otter": FP / "cards" / "sea-otter" / "index.html",
    "puffin": FP / "cards" / "puffin" / "index.html",
}

PARKS = {
    "biscayne": FP / "biscayne" / "index.html",
    "dry-tortugas": FP / "dry-tortugas" / "index.html",
    "channel-islands": FP / "channel-islands" / "index.html",
    "olympic": FP / "olympic" / "index.html",
    "kenai-fjords": FP / "kenai-fjords" / "index.html",
    "glacier-bay": FP / "glacier-bay" / "index.html",
    "everglades": FP / "everglades" / "index.html",
}

HUNT_KEEP = {
    "biscayne": "Find: Dante Fascell / Biscayne visitor center",
    "dry-tortugas": "Find: Garden Key / fort visitor center",
    "channel-islands": "Find: Mainland Channel Islands visitor center",
    "olympic": "Visit Hoh Rain Forest Visitor Center",
    "kenai-fjords": "Find: Seward / Kenai Fjords visitor center",
    "glacier-bay": "Find: Bartlett Cove visitor center",
    "everglades": "Find: Anhinga boardwalk",
}

PARK_ANIMALS = {
    "biscayne": ["sea-turtle", "shark", "stingray", "octopus", "seahorse", "crab", "starfish"],
    "dry-tortugas": ["sea-turtle", "shark"],
    "channel-islands": ["kelp-forest", "starfish", "crab"],
    "olympic": ["sea-otter", "kelp-forest", "starfish", "crab", "octopus"],
    "kenai-fjords": ["sea-otter", "puffin"],
    "glacier-bay": ["puffin"],
    "everglades": ["american-alligator", "sea-turtle"],
}

STUDY_DECK_ANIMALS = ("shark", "crab", "sea-otter", "puffin", "octopus", "sea-turtle", "seahorse", "starfish")


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


class MarineAnimalParkRailsTests(unittest.TestCase):
    def test_graph_is_strong_sourced_and_bidirectional(self):
        self.assertEqual(
            [p["id"] for p in parks_for_animal("sea-turtle")],
            ["dry-tortugas", "biscayne", "everglades"],
        )
        self.assertTrue(parks_for_animal("sea-turtle")[0]["primary"])
        self.assertEqual(
            parks_for_animal("sea-turtle")[0]["source"],
            "https://www.nps.gov/drto/learn/nature/sea-turtles.htm",
        )
        self.assertEqual(
            [p["id"] for p in parks_for_animal("shark")],
            ["dry-tortugas", "biscayne"],
        )
        self.assertEqual(
            [p["id"] for p in parks_for_animal("crab")],
            ["olympic", "biscayne", "channel-islands"],
        )
        self.assertEqual(
            [p["id"] for p in parks_for_animal("starfish")],
            ["olympic", "biscayne", "channel-islands"],
        )
        self.assertEqual([p["id"] for p in parks_for_animal("seahorse")], ["biscayne"])
        self.assertEqual(
            [p["id"] for p in parks_for_animal("octopus")],
            ["biscayne", "olympic"],
        )
        self.assertEqual([p["id"] for p in parks_for_animal("stingray")], ["biscayne"])
        self.assertEqual(
            [p["id"] for p in parks_for_animal("kelp-forest")],
            ["channel-islands", "olympic"],
        )
        self.assertEqual(
            [p["id"] for p in parks_for_animal("sea-otter")],
            ["kenai-fjords", "olympic"],
        )
        self.assertEqual(
            [p["id"] for p in parks_for_animal("puffin")],
            ["kenai-fjords", "glacier-bay"],
        )
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
        self.assertNotIn("padre-island", raw)
        self.assertFalse(PADRE.exists())
        self.assertNotIn("acadia", raw)
        self.assertTrue(ACADIA.is_file())
        otter_parks = {p["id"] for p in parks_for_animal("sea-otter")}
        self.assertNotIn("channel-islands", otter_parks)
        self.assertNotIn("channel-islands", raw.split('"sea-otter"', 1)[1].split('"puffin"', 1)[0])
        puffin_parks = {p["id"] for p in parks_for_animal("puffin")}
        self.assertNotIn("acadia", puffin_parks)
        self.assertNotIn("everglades", {p["id"] for p in parks_for_animal("shark")})
        self.assertNotIn("channel-islands", {p["id"] for p in parks_for_animal("seahorse")})
        self.assertNotIn("olympic", {p["id"] for p in parks_for_animal("seahorse")})
        for park_id, meta in (data.get("parks") or {}).items():
            listed = [str(x) for x in (meta.get("animals") or [])]
            incoming = animals_pointing_to_park(park_id)
            self.assertEqual(sorted(listed), sorted(incoming), park_id)
            self.assertTrue(str(meta.get("source") or "").startswith("https://www.nps.gov/"))
        for cid, meta in (data.get("animals") or {}).items():
            for edge in meta.get("parks") or []:
                self.assertTrue(
                    str(edge.get("source") or "").startswith("https://www.nps.gov/"),
                    f"{cid} → {edge.get('id')}",
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
        self.assertIn("np-hero-dry-tortugas.jpg", animal_park_rail_html("shark"))
        self.assertIn("/field-pack/cards/african-penguin/", study_try_next_html("shark"))
        self.assertEqual(
            study_try_next_ids("shark"),
            ["african-penguin", "caribbean-flamingo", "african-lion"],
        )
        self.assertEqual(
            study_try_next_ids("crab"),
            ["shark", "clownfish", "african-lion"],
        )
        self.assertEqual(
            study_try_next_ids("sea-otter"),
            ["asian-small-clawed-otter", "shark", "african-lion"],
        )
        self.assertEqual(
            study_try_next_ids("puffin"),
            ["african-penguin", "polar-bear", "african-lion"],
        )
        self.assertEqual(
            study_try_next_ids("octopus"),
            ["cuttlefish", "jellyfish", "african-lion"],
        )
        self.assertEqual(
            study_try_next_ids("sea-turtle"),
            ["octopus", "manta-ray", "african-lion"],
        )
        self.assertEqual(
            study_try_next_ids("seahorse"),
            ["octopus", "sea-turtle", "african-lion"],
        )
        self.assertEqual(
            study_try_next_ids("starfish"),
            ["sea-turtle", "octopus", "african-lion"],
        )

    def test_published_marine_cards_add_park_rails(self):
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
            self.assertNotIn("padre-island", rail)
            self.assertNotIn("acadia", rail)
            self.assertNotIn("Junior Ranger", rail)
            self.assertNotIn("Park Ranger", rail)
            self.assertNotIn("Zoologist", rail)
            self.assertNotIn('data-study-pick="easy"', rail)
            if cid in STUDY_DECK_ANIMALS:
                self.assertLess(main.find("Try next"), main.find('data-rail="parks"'), cid)
        otter_rail = _park_rail(_main(CARDS["sea-otter"].read_text(encoding="utf-8")))
        self.assertNotIn("channel-islands", otter_rail)
        puffin_rail = _park_rail(_main(CARDS["puffin"].read_text(encoding="utf-8")))
        self.assertNotIn("acadia", puffin_rail)
        shark_rail = _park_rail(_main(CARDS["shark"].read_text(encoding="utf-8")))
        self.assertNotIn("everglades", shark_rail)

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
                "far" in section.lower() or "distance" in section.lower() or "don’t touch" in section.lower(),
                section,
            )
            hunt = vis.split('id="hunt-heading"', 1)[1].split("</section>", 1)[0]
            self.assertIn(HUNT_KEEP[park_id], hunt)
            self.assertLess(vis.find('id="start-here"'), vis.find('id="animals-you-might-meet"'))
            self.assertNotIn("Junior Ranger", section)
            self.assertNotIn("Park Ranger", section)
            self.assertNotIn("Zoologist", section)
            self.assertNotIn("clownfish", section.lower())
            self.assertNotIn("padre-island", vis.lower())
            self.assertTrue(park_animals_html(park_id))
        olympic = _animals_section(PARKS["olympic"].read_text(encoding="utf-8"))
        self.assertIn("not the Hoh rainforest", olympic)
        kenai = _animals_section(PARKS["kenai-fjords"].read_text(encoding="utf-8"))
        self.assertIn("not at Exit Glacier", kenai)
        chis = _animals_section(PARKS["channel-islands"].read_text(encoding="utf-8"))
        self.assertNotIn("sea-otter", chis)
        self.assertNotIn("Sea otter", chis)


if __name__ == "__main__":
    unittest.main()
