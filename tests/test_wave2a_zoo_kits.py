"""Wave 2a Field Trip Kit: official 3+10 + catalog-kind filter."""

from __future__ import annotations

import json
import re
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
WAVE2A = (
    "fort-worth-zoo",
    "san-antonio-zoo",
    "austin-zoo",
    "lincoln-park-zoo",
    "bronx-zoo",
    "la-zoo",
    "oregon-zoo",
    "columbus-zoo",
    "denver-zoo",
    "st-louis-zoo",
)

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


class CardKindsTsvTests(unittest.TestCase):
    def test_tsv_classifications(self):
        kinds = load_card_kinds()
        self.assertEqual(kinds["african-lion"]["kind"], "zoo")
        self.assertEqual(kinds["african-penguin"]["kind"], "both")
        self.assertEqual(kinds["shark"]["kind"], "both")
        self.assertEqual(kinds["clownfish"]["kind"], "aquarium")
        self.assertEqual(kinds["octopus"]["kind"], "aquarium")
        self.assertEqual(kinds["cm-art-lab"]["kind"], "neither")
        self.assertEqual(kinds["sci-dinosaur"]["kind"], "neither")
        self.assertEqual(kinds["american-alligator"]["kind"], "neither")
        self.assertEqual(kinds["cuyahoga-towpath"]["kind"], "neither")
        self.assertTrue(card_ok_on_zoo_kit("zebra", kinds))
        self.assertTrue(card_ok_on_zoo_kit("two-toed-sloth", kinds))
        self.assertFalse(card_ok_on_zoo_kit("jellyfish", kinds))
        self.assertFalse(card_ok_on_zoo_kit("american-bison", kinds))


class Wave1UnchangedTests(unittest.TestCase):
    def test_wave1_json_lists(self):
        for slug, expect in WAVE1_ITEMS.items():
            data = _load_venue(slug)
            got = [it.get("catalog_id") for it in data.get("items") or []]
            self.assertEqual(got, expect, slug)
            self.assertEqual(data.get("route_90m"), WAVE1_ROUTES[slug], slug)

    def test_wave1_catalog_animal_ids(self):
        venues = _load_catalog_venues()
        for slug, expect in WAVE1_ITEMS.items():
            catalog_ids = [cid for cid in expect if cid != "polar-bear"]
            # polar-bear stays on San Diego JSON/catalog; published-card filter is SEO-only
            self.assertEqual(venues[slug]["animalIds"], expect, slug)
            self.assertEqual(venues[slug]["featuredAnimalIds"], expect[:6], slug)


class Wave2aKindFilterTests(unittest.TestCase):
    def test_no_aquarium_only_on_wave2a_json_or_catalog(self):
        kinds = load_card_kinds()
        aquarium = {s for s, row in kinds.items() if row["kind"] == AQUARIUM_ONLY_KIND}
        neither = {s for s, row in kinds.items() if row["kind"] == "neither"}
        venues = _load_catalog_venues()
        for slug in WAVE2A:
            data = _load_venue(slug)
            cids = [it.get("catalog_id") for it in data.get("items") or []]
            self.assertTrue(cids, slug)
            for cid in cids:
                self.assertIn(cid, kinds, f"{slug} unknown slug {cid}")
                self.assertIn(kinds[cid]["kind"], ZOO_OK_KINDS, f"{slug} {cid}")
                self.assertNotIn(cid, aquarium)
                self.assertNotIn(cid, neither)
            ven = venues[slug]
            for cid in list(ven.get("animalIds") or []) + list(ven.get("featuredAnimalIds") or []):
                self.assertTrue(card_ok_on_zoo_kit(cid, kinds), f"{slug} catalog {cid}")
                self.assertNotIn(cid, aquarium)

    def test_austin_has_no_elephants_or_sumatran_tiger(self):
        data = _load_venue("austin-zoo")
        cids = {it.get("catalog_id") for it in data.get("items") or []}
        self.assertIn("african-lion", cids)
        self.assertIn("galapagos-tortoise", cids)
        self.assertNotIn("african-elephant", cids)
        self.assertNotIn("reticulated-giraffe", cids)
        self.assertNotIn("sumatran-tiger", cids)
        bans = {row.get("catalog_id") for row in data.get("do_not_list") or []}
        self.assertIn("african-elephant", bans)
        self.assertIn("sumatran-tiger", bans)

    def test_columbus_drops_leftover_sea_life(self):
        data = _load_venue("columbus-zoo")
        cids = {it.get("catalog_id") for it in data.get("items") or []}
        for banned in ("jellyfish", "octopus", "sea-turtle", "stingray", "shark"):
            self.assertNotIn(banned, cids)
        self.assertEqual(data.get("type"), "zoo")
        self.assertIn("western-lowland-gorilla", cids)
        self.assertIn("african-lion", cids)

    def test_catalog_js_matches_venue_json(self):
        venues = _load_catalog_venues()
        for slug in WAVE2A:
            data = _load_venue(slug)
            cids = [it.get("catalog_id") for it in data.get("items") or []]
            self.assertEqual(venues[slug]["animalIds"], cids, slug)
            featured = [it.get("catalog_id") for it in data.get("items") or [] if it.get("core")][:6]
            self.assertEqual(venues[slug]["featuredAnimalIds"][:3], cids[:3], slug)
            self.assertGreaterEqual(len(featured), 3, slug)


class StartHereFromAndNextTests(unittest.TestCase):
    def test_kit_from_query_covers_wave1_and_wave2a(self):
        self.assertEqual(kit_from_query("dallas-zoo"), "from=dallas-zoo")
        self.assertEqual(kit_from_query("national-zoo"), "from=national-zoo")
        self.assertEqual(kit_from_query("columbus-zoo"), "from=columbus-zoo")
        self.assertEqual(kit_from_query("yellowstone"), "")

    def test_start_here_hrefs_include_from(self):
        for slug in WAVE1 + WAVE2A:
            href = start_here_card_href("african-lion", slug)
            if slug in ("dallas-zoo",) or slug in WAVE2A or slug in WAVE1:
                self.assertIn(f"from={slug}", href, slug)

    def test_place_page_start_here_has_from(self):
        for slug in WAVE2A:
            start = _start_here(slug)
            self.assertIn(f"from={slug}", start, slug)
            self.assertNotIn("from=dallas-zoo", start, slug)

    def test_wave1_place_pages_keep_start_here_animals(self):
        dallas = _start_here("dallas-zoo")
        self.assertIn("Reticulated giraffe", dallas)
        self.assertIn("African elephant", dallas)
        self.assertIn("African lion", dallas)
        self.assertIn("from=dallas-zoo", dallas)
        national = _start_here("national-zoo")
        self.assertIn("Giant panda", national)
        self.assertIn("from=national-zoo", national)

    def test_next_follows_that_kit(self):
        panda = card_next_matches("giant-panda")
        by_slug = {slug: nxt["id"] for slug, nxt in panda}
        self.assertEqual(by_slug["san-diego-zoo"], "koala")
        self.assertEqual(by_slug["national-zoo"], "asian-small-clawed-otter")
        kits = start_here_next_by_kit()
        self.assertEqual(kits["dallas-zoo"]["reticulated-giraffe"]["id"], "african-elephant")
        self.assertEqual(kits["austin-zoo"]["african-lion"]["id"], "cheetah")
        self.assertEqual(kits["columbus-zoo"]["western-lowland-gorilla"]["id"], "african-lion")

    def test_card_pages_emit_kit_aware_panda_next(self):
        html = (FP / "cards" / "giant-panda" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-next-from="national-zoo"', html)
        self.assertIn('data-next-from="san-diego-zoo"', html)
        self.assertIn("Next: Asian small-clawed otter", html)
        self.assertIn("Next: Koala", html)
        self.assertIn("from=national-zoo", html)
        self.assertIn("from=san-diego-zoo", html)

    def test_no_aquarium_only_on_wave2a_place_pages(self):
        kinds = load_card_kinds()
        aquarium = [s for s, row in kinds.items() if row["kind"] == AQUARIUM_ONLY_KIND]
        for slug in WAVE2A:
            html = (FP / slug / "index.html").read_text(encoding="utf-8")
            visible = _visible(html)
            for aid in aquarium:
                self.assertNotIn(f"/field-pack/cards/{aid}/", visible, f"{slug} {aid}")


if __name__ == "__main__":
    unittest.main()
