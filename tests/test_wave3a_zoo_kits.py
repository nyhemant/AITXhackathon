"""Wave 3a Field Trip Kit: official 3+10 + catalog-kind filter."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from field_pack_catalog_kind import (  # noqa: E402
    AQUARIUM_ONLY_KIND,
    ZOO_OK_KINDS,
    card_ok_on_zoo_kit,
    load_card_kinds,
)
from generate_bdo_seo import (  # noqa: E402
    card_next_matches,
    kit_from_query,
    start_here_card_href,
    start_here_next_by_kit,
)

FP = REPO / "static" / "field-pack"
VENUES = FP / "data" / "venues"
CATALOG_JS = FP / "js" / "catalog.js"

WAVE1 = ("dallas-zoo", "houston-zoo", "san-diego-zoo", "national-zoo")
WAVE1_ITEMS = {
    "dallas-zoo": [
        "reticulated-giraffe",
        "african-elephant",
        "african-lion",
        "zebra",
        "nile-hippo",
        "african-penguin",
        "caribbean-flamingo",
        "galapagos-tortoise",
        "sumatran-tiger",
        "western-lowland-gorilla",
    ],
    "houston-zoo": [
        "western-lowland-gorilla",
        "chimpanzee",
        "african-lion",
        "orangutan",
        "galapagos-tortoise",
        "cheetah",
        "zebra",
        "ostrich",
        "ring-tailed-lemur",
        "warthog",
    ],
    "san-diego-zoo": [
        "giant-panda",
        "koala",
        "african-elephant",
        "african-penguin",
        "polar-bear",
        "nile-hippo",
        "orangutan",
        "western-lowland-gorilla",
        "african-lion",
        "red-panda",
    ],
    "national-zoo": [
        "giant-panda",
        "asian-small-clawed-otter",
        "red-panda",
        "african-lion",
        "sumatran-tiger",
        "western-lowland-gorilla",
        "orangutan",
        "ring-tailed-lemur",
        "two-toed-sloth",
        "caribbean-flamingo",
    ],
}
WAVE1_ROUTES = {
    "dallas-zoo": ["giraffe", "elephant", "lion"],
    "houston-zoo": ["western_lowland_gorilla", "chimpanzee", "african_lion"],
    "san-diego-zoo": ["giant_panda", "koala", "african_elephant"],
    "national-zoo": ["giant_panda", "asian_small_clawed_otter", "red_panda"],
}

WAVE2A_ROUTES = {
    "fort-worth-zoo": ["african_lion", "sumatran_tiger", "nile_hippo"],
    "san-antonio-zoo": ["western_lowland_gorilla", "caribbean_flamingo", "african_lion"],
    "austin-zoo": ["african_lion", "cheetah", "galapagos_tortoise"],
    "lincoln-park-zoo": ["western_lowland_gorilla", "african_penguin", "asian_small_clawed_otter"],
    "bronx-zoo": ["western_lowland_gorilla", "red_panda", "caribbean_flamingo"],
    "la-zoo": ["chimpanzee", "western_lowland_gorilla", "orangutan"],
    "oregon-zoo": ["red_panda", "chimpanzee", "african_lion"],
    "columbus-zoo": ["western_lowland_gorilla", "african_lion", "cheetah"],
    "denver-zoo": ["western_lowland_gorilla", "orangutan", "african_penguin"],
    "st-louis-zoo": ["western_lowland_gorilla", "chimpanzee", "reticulated_giraffe"],
}

WAVE2B_ROUTES = {
    "albuquerque-biopark": ["western_lowland_gorilla", "chimpanzee", "reticulated_giraffe"],
    "audubon-zoo": ["african_lion", "caribbean_flamingo", "western_lowland_gorilla"],
    "cincinnati-zoo": ["nile_hippo", "western_lowland_gorilla", "cheetah"],
    "cleveland-metroparks-zoo": ["african_elephant", "western_lowland_gorilla", "cheetah"],
    "detroit-zoo": ["western_lowland_gorilla", "chimpanzee", "african_lion"],
    "hogle-zoo": ["western_lowland_gorilla", "orangutan", "african_lion"],
    "honolulu-zoo": ["african_penguin", "sumatran_tiger", "reticulated_giraffe"],
    "kansas-city-zoo": ["chimpanzee", "western_lowland_gorilla", "sumatran_tiger"],
    "memphis-zoo": ["african_elephant", "reticulated_giraffe", "sumatran_tiger"],
    "miami-zoo": ["african_elephant", "sumatran_tiger", "orangutan"],
    "milwaukee-zoo": ["african_elephant", "reticulated_giraffe", "western_lowland_gorilla"],
    "minnesota-zoo": ["african_penguin", "red_panda", "ring_tailed_lemur"],
    "nashville-zoo": ["sumatran_tiger", "two_toed_sloth", "caribbean_flamingo"],
    "north-carolina-zoo": ["african_elephant", "western_lowland_gorilla", "african_lion"],
    "omaha-henry-doorly": ["african_elephant", "western_lowland_gorilla", "orangutan"],
    "philadelphia-zoo": ["african_lion", "western_lowland_gorilla", "reticulated_giraffe"],
    "phoenix-zoo": ["sumatran_tiger", "orangutan", "african_penguin"],
    "pittsburgh-zoo": ["african_elephant", "african_lion", "red_panda"],
    "point-defiance-zoo": ["sumatran_tiger", "asian_small_clawed_otter", "ring_tailed_lemur"],
    "san-diego-safari-park": ["african_elephant", "reticulated_giraffe", "sumatran_tiger"],
    "tampa-zoo": ["african_elephant", "african_penguin", "koala"],
    "woodland-park-zoo": ["western_lowland_gorilla", "asian_small_clawed_otter", "ring_tailed_lemur"],
}

WAVE3A = (
    "london-zoo",
    "edinburgh-zoo",
    "dublin-zoo",
    "toronto-zoo",
    "calgary-zoo",
    "melbourne-zoo",
    "taronga-zoo",
    "perth-zoo",
    "adelaide-zoo",
    "auckland-zoo",
    "wellington-zoo",
    "singapore-zoo",
    "paris-zoo",
    "berlin-zoo",
    "artis-zoo",
    "barcelona-zoo",
    "prague-zoo",
    "vienna-zoo",
    "zurich-zoo",
    "copenhagen-zoo",
)

WAVE3A_ROUTES = {
    "london-zoo": ["western_lowland_gorilla", "sumatran_tiger", "two_toed_sloth"],
    "edinburgh-zoo": ["koala", "chimpanzee", "sumatran_tiger"],
    "dublin-zoo": ["orangutan", "western_lowland_gorilla", "nile_hippo"],
    "toronto-zoo": ["western_lowland_gorilla", "african_penguin", "caribbean_flamingo"],
    "calgary-zoo": ["western_lowland_gorilla", "nile_hippo", "red_panda"],
    "melbourne-zoo": ["koala", "western_lowland_gorilla", "orangutan"],
    "taronga-zoo": ["koala", "sumatran_tiger", "chimpanzee"],
    "perth-zoo": ["koala", "orangutan", "galapagos_tortoise"],
    "adelaide-zoo": ["giant_panda", "koala", "orangutan"],
    "auckland-zoo": ["sumatran_tiger", "galapagos_tortoise", "orangutan"],
    "wellington-zoo": ["chimpanzee", "sumatran_tiger", "red_panda"],
    "singapore-zoo": ["orangutan", "two_toed_sloth", "cheetah"],
    "paris-zoo": ["two_toed_sloth", "ring_tailed_lemur", "reticulated_giraffe"],
    "berlin-zoo": ["giant_panda", "western_lowland_gorilla", "orangutan"],
    "artis-zoo": ["african_penguin", "reticulated_giraffe", "western_lowland_gorilla"],
    "barcelona-zoo": ["african_elephant", "nile_hippo", "caribbean_flamingo"],
    "prague-zoo": ["western_lowland_gorilla", "reticulated_giraffe", "ring_tailed_lemur"],
    "vienna-zoo": ["giant_panda", "koala", "orangutan"],
    "zurich-zoo": ["koala", "orangutan", "western_lowland_gorilla"],
    "copenhagen-zoo": ["giant_panda", "reticulated_giraffe", "nile_hippo"],
}

STARTER = {
    "melbourne-zoo",
    "taronga-zoo",
    "perth-zoo",
    "paris-zoo",
    "berlin-zoo",
    "prague-zoo",
}

AQUARIUM_ONLY = ("jellyfish", "octopus", "sea-turtle", "stingray", "clownfish", "seahorse")


def _load_venue(slug: str) -> dict:
    return json.loads((VENUES / f"{slug}.json").read_text(encoding="utf-8"))


def _load_catalog_venues() -> dict:
    js = r"""
const fs = require("fs");
const vm = require("vm");
const window = {};
vm.runInNewContext(fs.readFileSync(process.argv[1], "utf8"), { window });
process.stdout.write(JSON.stringify(window.FIELD_PACK_VENUES));
"""
    proc = subprocess.run(
        ["node", "-e", js, str(CATALOG_JS)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


def _visible(html: str) -> str:
    return html.split('id="venue-data"', 1)[0]


def _start_here(slug: str) -> str:
    html = _visible((FP / slug / "index.html").read_text(encoding="utf-8"))
    return html.split('id="route90-heading"', 1)[1].split("</section>", 1)[0]


class PriorWavesUnchangedTests(unittest.TestCase):
    def test_wave1_json_lists(self):
        for slug, expect in WAVE1_ITEMS.items():
            data = _load_venue(slug)
            got = [it.get("catalog_id") for it in data.get("items") or []]
            self.assertEqual(got, expect, slug)
            self.assertEqual(data.get("route_90m"), WAVE1_ROUTES[slug], slug)

    def test_wave2a_start_here_unchanged(self):
        for slug, route in WAVE2A_ROUTES.items():
            self.assertEqual(_load_venue(slug).get("route_90m"), route, slug)

    def test_wave2b_start_here_unchanged(self):
        for slug, route in WAVE2B_ROUTES.items():
            self.assertEqual(_load_venue(slug).get("route_90m"), route, slug)

    def test_out_of_scope_venues_untouched(self):
        # Madrid Zoo Aquarium and Night Safari moved to Wave 3b; 3a kits stay intact.
        self.assertEqual(_load_venue("singapore-zoo").get("route_90m"), WAVE3A_ROUTES["singapore-zoo"])
        self.assertEqual(_load_venue("london-zoo").get("route_90m"), WAVE3A_ROUTES["london-zoo"])


class Wave3aKindFilterTests(unittest.TestCase):
    def test_no_aquarium_only_or_neither_on_wave3a(self):
        kinds = load_card_kinds()
        aquarium = {s for s, row in kinds.items() if row["kind"] == AQUARIUM_ONLY_KIND}
        neither = {s for s, row in kinds.items() if row["kind"] == "neither"}
        venues = _load_catalog_venues()
        for slug in WAVE3A:
            data = _load_venue(slug)
            cids = [it.get("catalog_id") for it in data.get("items") or []]
            self.assertTrue(cids, slug)
            self.assertGreaterEqual(len(cids), 3, slug)
            for cid in cids:
                self.assertIn(cid, kinds, f"{slug} unknown slug {cid}")
                self.assertIn(kinds[cid]["kind"], ZOO_OK_KINDS, f"{slug} {cid}")
                self.assertNotIn(cid, aquarium)
                self.assertNotIn(cid, neither)
            ven = venues[slug]
            for cid in list(ven.get("animalIds") or []) + list(ven.get("featuredAnimalIds") or []):
                self.assertTrue(card_ok_on_zoo_kit(cid, kinds), f"{slug} catalog {cid}")
                self.assertNotIn(cid, aquarium)
                self.assertNotIn(cid, neither)

    def test_catalog_js_matches_venue_json(self):
        venues = _load_catalog_venues()
        for slug in WAVE3A:
            data = _load_venue(slug)
            cids = [it.get("catalog_id") for it in data.get("items") or []]
            self.assertEqual(venues[slug]["animalIds"], cids, slug)
            self.assertEqual(venues[slug]["featuredAnimalIds"][:3], cids[:3], slug)
            self.assertEqual(data.get("route_90m"), WAVE3A_ROUTES[slug], slug)

    def test_starter_vs_verified_dates(self):
        for slug in WAVE3A:
            data = _load_venue(slug)
            if slug in STARTER:
                self.assertIsNone(data.get("last_verified"), slug)
                self.assertEqual(data.get("status"), "partial", slug)
                self.assertEqual(data.get("list_confidence"), "partial", slug)
            else:
                self.assertEqual(data.get("last_verified"), "2026-08-23", slug)
                self.assertEqual(data.get("status"), "verified", slug)


class Wave3aHonestyTests(unittest.TestCase):
    def test_false_labels_are_banned(self):
        cases = {
            "london-zoo": ("african-elephant", "african-lion", "african-penguin", "nile-hippo"),
            "edinburgh-zoo": ("african-penguin", "african-lion", "nile-hippo", "western-lowland-gorilla"),
            "dublin-zoo": ("african-elephant", "african-lion", "sumatran-tiger", "african-penguin"),
            "toronto-zoo": ("african-elephant", "sumatran-tiger", "chimpanzee", "giant-panda"),
            "calgary-zoo": ("sumatran-tiger", "african-penguin", "african-elephant", "giant-panda"),
            "melbourne-zoo": ("african-elephant", "nile-hippo", "african-penguin"),
            "taronga-zoo": ("nile-hippo", "african-penguin", "african-elephant"),
            "perth-zoo": ("african-penguin", "nile-hippo", "african-elephant"),
            "adelaide-zoo": ("nile-hippo", "african-penguin", "african-lion", "african-elephant"),
            "auckland-zoo": ("african-elephant", "african-penguin", "caribbean-flamingo"),
            "wellington-zoo": ("african-penguin", "african-elephant", "western-lowland-gorilla"),
            "singapore-zoo": ("african-elephant", "sumatran-tiger", "nile-hippo", "western-lowland-gorilla"),
            "paris-zoo": ("african-penguin", "caribbean-flamingo", "african-elephant"),
            "berlin-zoo": ("african-elephant", "african-penguin", "sumatran-tiger"),
            "artis-zoo": ("african-elephant", "caribbean-flamingo", "galapagos-tortoise"),
            "barcelona-zoo": ("african-penguin", "galapagos-tortoise", "asian-small-clawed-otter"),
            "prague-zoo": ("african-elephant", "african-lion", "african-penguin"),
            "vienna-zoo": ("sumatran-tiger", "african-penguin", "caribbean-flamingo"),
            "zurich-zoo": ("african-elephant", "african-lion", "sumatran-tiger", "african-penguin"),
            "copenhagen-zoo": ("african-elephant", "sumatran-tiger", "african-penguin", "western-lowland-gorilla"),
        }
        for slug, banned in cases.items():
            data = _load_venue(slug)
            cids = {it.get("catalog_id") for it in data.get("items") or []}
            bans = {row.get("catalog_id") for row in data.get("do_not_list") or []}
            for cid in banned:
                self.assertNotIn(cid, cids, f"{slug} still lists {cid}")
                self.assertIn(cid, bans, f"{slug} missing do_not_list {cid}")

    def test_zurich_drops_neither_outdoor_card(self):
        data = _load_venue("zurich-zoo")
        cids = {it.get("catalog_id") for it in data.get("items") or []}
        self.assertNotIn("cm-outdoor", cids)
        venues = _load_catalog_venues()
        self.assertNotIn("cm-outdoor", venues["zurich-zoo"].get("animalIds") or [])
        self.assertEqual(data.get("route_90m"), WAVE3A_ROUTES["zurich-zoo"])

    def test_singapore_zoo_is_not_night_safari(self):
        data = _load_venue("singapore-zoo")
        self.assertEqual(data.get("route_90m"), WAVE3A_ROUTES["singapore-zoo"])
        cids = {it.get("catalog_id") for it in data.get("items") or []}
        self.assertIn("orangutan", cids)
        self.assertNotIn("african-elephant", cids)
        self.assertNotIn("sumatran-tiger", cids)
        night = _load_venue("singapore-night-safari")
        self.assertNotEqual(night.get("route_90m"), WAVE3A_ROUTES["singapore-zoo"])

    def test_no_invented_cards(self):
        kinds = load_card_kinds()
        for slug in WAVE3A:
            data = _load_venue(slug)
            for it in data.get("items") or []:
                cid = it.get("catalog_id")
                self.assertIn(cid, kinds, f"{slug} invented {cid}")
                self.assertTrue((FP / "cards" / cid / "index.html").is_file(), f"{slug} unpublished {cid}")


class StartHereFromAndNextTests(unittest.TestCase):
    def test_kit_from_query_covers_wave3a(self):
        self.assertEqual(kit_from_query("london-zoo"), "from=london-zoo")
        self.assertEqual(kit_from_query("singapore-zoo"), "from=singapore-zoo")
        self.assertEqual(kit_from_query("copenhagen-zoo"), "from=copenhagen-zoo")
        self.assertEqual(kit_from_query("yellowstone"), "")

    def test_start_here_hrefs_include_from(self):
        for slug in WAVE3A:
            href = start_here_card_href("african-lion", slug)
            self.assertIn(f"from={slug}", href, slug)

    def test_place_page_start_here_has_from(self):
        for slug in WAVE3A:
            start = _start_here(slug)
            self.assertIn(f"from={slug}", start, slug)
            self.assertNotIn("from=dallas-zoo", start, slug)

    def test_us_wave_place_pages_keep_start_here(self):
        dallas = _start_here("dallas-zoo")
        self.assertIn("Reticulated giraffe", dallas)
        self.assertIn("from=dallas-zoo", dallas)
        safari = _start_here("san-diego-safari-park")
        self.assertIn("from=san-diego-safari-park", safari)
        self.assertNotIn("Giant panda", safari)

    def test_next_follows_that_kit(self):
        panda = card_next_matches("giant-panda")
        by_slug = {slug: nxt["id"] for slug, nxt in panda}
        self.assertEqual(by_slug["san-diego-zoo"], "koala")
        self.assertEqual(by_slug["national-zoo"], "asian-small-clawed-otter")
        self.assertEqual(by_slug["adelaide-zoo"], "koala")
        self.assertEqual(by_slug["vienna-zoo"], "koala")
        self.assertEqual(by_slug["copenhagen-zoo"], "reticulated-giraffe")
        kits = start_here_next_by_kit()
        self.assertEqual(kits["dallas-zoo"]["reticulated-giraffe"]["id"], "african-elephant")
        self.assertEqual(kits["london-zoo"]["western-lowland-gorilla"]["id"], "sumatran-tiger")
        self.assertEqual(kits["edinburgh-zoo"]["koala"]["id"], "chimpanzee")
        self.assertEqual(kits["singapore-zoo"]["orangutan"]["id"], "two-toed-sloth")
        self.assertEqual(kits["zurich-zoo"]["koala"]["id"], "orangutan")
        self.assertEqual(kits["barcelona-zoo"]["african-elephant"]["id"], "nile-hippo")

    def test_card_pages_emit_kit_aware_panda_next(self):
        html = (FP / "cards" / "giant-panda" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-next-from="national-zoo"', html)
        self.assertIn('data-next-from="san-diego-zoo"', html)
        self.assertIn('data-next-from="adelaide-zoo"', html)
        self.assertIn("Next: Asian small-clawed otter", html)
        self.assertIn("Next: Koala", html)

    def test_no_aquarium_only_on_wave3a_place_pages(self):
        kinds = load_card_kinds()
        aquarium = [s for s, row in kinds.items() if row["kind"] == AQUARIUM_ONLY_KIND]
        for slug in WAVE3A:
            html = (FP / slug / "index.html").read_text(encoding="utf-8")
            visible = _visible(html)
            for aid in aquarium:
                self.assertNotIn(f"/field-pack/cards/{aid}/", visible, f"{slug} {aid}")


if __name__ == "__main__":
    unittest.main()
