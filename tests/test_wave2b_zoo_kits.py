"""Wave 2b Field Trip Kit: official 3+10 + catalog-kind filter."""

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
from test_wave2a_zoo_kits import (  # noqa: E402
    WAVE1,
    WAVE1_ITEMS,
    WAVE1_ROUTES,
    WAVE2A,
    _load_catalog_venues,
    _load_venue,
    _start_here,
    _visible,
)

FP = REPO / "static" / "field-pack"

WAVE2B = (
    "albuquerque-biopark",
    "audubon-zoo",
    "cincinnati-zoo",
    "cleveland-metroparks-zoo",
    "detroit-zoo",
    "hogle-zoo",
    "honolulu-zoo",
    "kansas-city-zoo",
    "memphis-zoo",
    "miami-zoo",
    "milwaukee-zoo",
    "minnesota-zoo",
    "nashville-zoo",
    "north-carolina-zoo",
    "omaha-henry-doorly",
    "philadelphia-zoo",
    "phoenix-zoo",
    "pittsburgh-zoo",
    "point-defiance-zoo",
    "san-diego-safari-park",
    "tampa-zoo",
    "woodland-park-zoo",
)

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

STARTER = {
    "cleveland-metroparks-zoo",
    "hogle-zoo",
    "honolulu-zoo",
    "kansas-city-zoo",
    "miami-zoo",
    "omaha-henry-doorly",
    "philadelphia-zoo",
    "phoenix-zoo",
    "pittsburgh-zoo",
    "point-defiance-zoo",
}
ZOO_AQ = ("omaha-henry-doorly", "pittsburgh-zoo", "point-defiance-zoo")
AQUARIUM_ONLY = ("jellyfish", "octopus", "sea-turtle", "stingray", "clownfish", "seahorse")


class PriorWavesUnchangedTests(unittest.TestCase):
    def test_wave1_json_lists(self):
        for slug, expect in WAVE1_ITEMS.items():
            data = _load_venue(slug)
            got = [it.get("catalog_id") for it in data.get("items") or []]
            self.assertEqual(got, expect, slug)
            self.assertEqual(data.get("route_90m"), WAVE1_ROUTES[slug], slug)

    def test_wave2a_start_here_unchanged(self):
        expect = {
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
        for slug, route in expect.items():
            self.assertEqual(_load_venue(slug).get("route_90m"), route, slug)


class Wave2bKindFilterTests(unittest.TestCase):
    def test_no_aquarium_only_or_neither_on_wave2b(self):
        kinds = load_card_kinds()
        aquarium = {s for s, row in kinds.items() if row["kind"] == AQUARIUM_ONLY_KIND}
        neither = {s for s, row in kinds.items() if row["kind"] == "neither"}
        venues = _load_catalog_venues()
        for slug in WAVE2B:
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

    def test_catalog_js_matches_venue_json(self):
        venues = _load_catalog_venues()
        for slug in WAVE2B:
            data = _load_venue(slug)
            cids = [it.get("catalog_id") for it in data.get("items") or []]
            self.assertEqual(venues[slug]["animalIds"], cids, slug)
            self.assertEqual(venues[slug]["featuredAnimalIds"][:3], cids[:3], slug)
            self.assertEqual(data.get("route_90m"), WAVE2B_ROUTES[slug], slug)

    def test_starter_vs_verified_dates(self):
        for slug in WAVE2B:
            data = _load_venue(slug)
            if slug in STARTER:
                self.assertIsNone(data.get("last_verified"), slug)
                self.assertEqual(data.get("status"), "partial", slug)
                self.assertEqual(data.get("list_confidence"), "partial", slug)
            else:
                self.assertEqual(data.get("last_verified"), "2026-08-23", slug)
                self.assertEqual(data.get("status"), "verified", slug)


class Wave2bHonestyTests(unittest.TestCase):
    def test_false_labels_are_banned(self):
        cases = {
            "albuquerque-biopark": ("african-elephant", "sumatran-tiger", "african-penguin", "african-lion"),
            "audubon-zoo": ("african-elephant", "sumatran-tiger", "african-penguin"),
            "cincinnati-zoo": ("african-elephant", "sumatran-tiger"),
            "detroit-zoo": ("african-penguin", "sumatran-tiger", "african-elephant"),
            "memphis-zoo": ("giant-panda",),
            "milwaukee-zoo": ("african-penguin", "sumatran-tiger", "chimpanzee"),
            "minnesota-zoo": ("sumatran-tiger", "reticulated-giraffe", "african-elephant", "african-lion"),
            "nashville-zoo": ("african-elephant", "african-penguin"),
            "omaha-henry-doorly": ("sumatran-tiger", "nile-hippo", "shark", "african-penguin"),
            "pittsburgh-zoo": ("sumatran-tiger", "nile-hippo", "shark", "african-penguin"),
            "point-defiance-zoo": ("african-penguin", "shark", "african-elephant"),
            "san-diego-safari-park": ("giant-panda", "koala"),
            "tampa-zoo": ("nile-hippo", "sumatran-tiger"),
            "woodland-park-zoo": ("african-penguin", "sumatran-tiger", "african-elephant"),
        }
        for slug, banned in cases.items():
            data = _load_venue(slug)
            cids = {it.get("catalog_id") for it in data.get("items") or []}
            bans = {row.get("catalog_id") for row in data.get("do_not_list") or []}
            for cid in banned:
                self.assertNotIn(cid, cids, f"{slug} still lists {cid}")
                self.assertIn(cid, bans, f"{slug} missing do_not_list {cid}")

    def test_zoo_aq_drops_aquarium_only(self):
        for slug in ZOO_AQ:
            data = _load_venue(slug)
            cids = {it.get("catalog_id") for it in data.get("items") or []}
            for aid in AQUARIUM_ONLY:
                self.assertNotIn(aid, cids, f"{slug} {aid}")
            venues = _load_catalog_venues()
            for aid in AQUARIUM_ONLY:
                self.assertNotIn(aid, venues[slug].get("animalIds") or [], f"{slug} catalog {aid}")

    def test_safari_park_is_not_the_zoo_panda_path(self):
        data = _load_venue("san-diego-safari-park")
        self.assertEqual(data.get("type"), "safari_zoo")
        self.assertEqual(data.get("route_90m"), WAVE2B_ROUTES["san-diego-safari-park"])
        cids = [it.get("catalog_id") for it in data.get("items") or []]
        self.assertEqual(cids[:3], ["african-elephant", "reticulated-giraffe", "sumatran-tiger"])
        self.assertNotIn("giant-panda", cids)
        self.assertNotIn("koala", cids)
        zoo = _load_venue("san-diego-zoo")
        self.assertEqual(zoo.get("route_90m"), ["giant_panda", "koala", "african_elephant"])


class StartHereFromAndNextTests(unittest.TestCase):
    def test_kit_from_query_covers_wave2b(self):
        self.assertEqual(kit_from_query("cincinnati-zoo"), "from=cincinnati-zoo")
        self.assertEqual(kit_from_query("san-diego-safari-park"), "from=san-diego-safari-park")
        self.assertEqual(kit_from_query("point-defiance-zoo"), "from=point-defiance-zoo")
        self.assertEqual(kit_from_query("yellowstone"), "")

    def test_start_here_hrefs_include_from(self):
        for slug in WAVE2B:
            href = start_here_card_href("african-lion", slug)
            self.assertIn(f"from={slug}", href, slug)

    def test_place_page_start_here_has_from(self):
        for slug in WAVE2B:
            start = _start_here(slug)
            self.assertIn(f"from={slug}", start, slug)
            self.assertNotIn("from=dallas-zoo", start, slug)

    def test_next_follows_that_kit(self):
        panda = card_next_matches("giant-panda")
        by_slug = {slug: nxt["id"] for slug, nxt in panda}
        self.assertEqual(by_slug["san-diego-zoo"], "koala")
        self.assertEqual(by_slug["national-zoo"], "asian-small-clawed-otter")
        self.assertNotIn("san-diego-safari-park", by_slug)
        kits = start_here_next_by_kit()
        self.assertEqual(kits["dallas-zoo"]["reticulated-giraffe"]["id"], "african-elephant")
        self.assertEqual(kits["cincinnati-zoo"]["nile-hippo"]["id"], "western-lowland-gorilla")
        self.assertEqual(kits["san-diego-safari-park"]["african-elephant"]["id"], "reticulated-giraffe")
        self.assertEqual(kits["minnesota-zoo"]["african-penguin"]["id"], "red-panda")
        self.assertEqual(kits["point-defiance-zoo"]["sumatran-tiger"]["id"], "asian-small-clawed-otter")

    def test_card_pages_emit_kit_aware_panda_next(self):
        html = (FP / "cards" / "giant-panda" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-next-from="national-zoo"', html)
        self.assertIn('data-next-from="san-diego-zoo"', html)
        self.assertIn("Next: Asian small-clawed otter", html)
        self.assertIn("Next: Koala", html)

    def test_no_aquarium_only_on_wave2b_place_pages(self):
        kinds = load_card_kinds()
        aquarium = [s for s, row in kinds.items() if row["kind"] == AQUARIUM_ONLY_KIND]
        for slug in WAVE2B:
            html = (FP / slug / "index.html").read_text(encoding="utf-8")
            visible = _visible(html)
            for aid in aquarium:
                self.assertNotIn(f"/field-pack/cards/{aid}/", visible, f"{slug} {aid}")


if __name__ == "__main__":
    unittest.main()
