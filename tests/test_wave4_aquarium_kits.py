"""Wave 4 Field Trip Kit: official 3+10 + flipped aquarium catalog-kind filter."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))

from field_pack_catalog_kind import (  # noqa: E402
    AQUARIUM_OK_KINDS,
    NEITHER_KIND,
    ZOO_ONLY_KIND,
    card_ok_on_aquarium_kit,
    load_card_kinds,
)
from generate_bdo_seo import (  # noqa: E402
    card_next_matches,
    kit_from_query,
    start_here_card_href,
    start_here_next_by_kit,
)
from test_wave3a_zoo_kits import (  # noqa: E402
    WAVE1_ITEMS,
    WAVE1_ROUTES,
    WAVE2A_ROUTES,
    WAVE2B_ROUTES,
    WAVE3A_ROUTES,
)
from test_wave3b_zoo_kits import WAVE3B_ROUTES  # noqa: E402

FP = REPO / "static" / "field-pack"
VENUES = FP / "data" / "venues"
CATALOG_JS = FP / "js" / "catalog.js"

WAVE4 = (
    "aquarium-of-the-pacific",
    "audubon-aquarium",
    "childrens-aquarium-dallas",
    "dallas-world-aquarium",
    "dubai-aquarium",
    "florida-aquarium",
    "georgia-aquarium",
    "istanbul-aquarium",
    "lotte-aquarium-seoul",
    "milan-aquarium",
    "monterey-bay-aquarium",
    "national-aquarium-baltimore",
    "new-england-aquarium",
    "osaka-aquarium",
    "seattle-aquarium",
    "shanghai-ocean-aquarium",
    "shedd-aquarium",
    "two-oceans-aquarium",
    "vancouver-aquarium",
    "virginia-aquarium",
    "waikiki-aquarium",
)

WAVE4_ROUTES = {
    "aquarium-of-the-pacific": ["sea_otter", "puffin", "shark"],
    "audubon-aquarium": ["african_penguin", "shark", "stingray"],
    "childrens-aquarium-dallas": ["shark", "stingray", "octopus"],
    "dallas-world-aquarium": ["two_toed_sloth", "african_penguin", "caribbean_flamingo"],
    "dubai-aquarium": ["asian_small_clawed_otter", "shark", "stingray"],
    "florida-aquarium": ["african_penguin", "two_toed_sloth", "jellyfish"],
    "georgia-aquarium": ["whale_shark", "manta_ray", "african_penguin"],
    "istanbul-aquarium": ["shark", "stingray", "clownfish"],
    "lotte-aquarium-seoul": ["shark", "stingray"],
    "milan-aquarium": ["freshwater_fish", "jellyfish", "stingray"],
    "monterey-bay-aquarium": ["jellyfish", "sea_otter", "kelp_forest"],
    "national-aquarium-baltimore": ["puffin", "two_toed_sloth", "jellyfish"],
    "new-england-aquarium": ["african_penguin", "sea_turtle", "shark"],
    "osaka-aquarium": ["whale_shark", "jellyfish", "manta_ray"],
    "seattle-aquarium": ["sea_otter", "puffin", "octopus"],
    "shanghai-ocean-aquarium": ["shark", "sea_turtle", "jellyfish"],
    "shedd-aquarium": ["sea_otter", "shark", "jellyfish"],
    "two-oceans-aquarium": ["african_penguin", "shark", "kelp_forest"],
    "vancouver-aquarium": ["sea_otter", "jellyfish", "two_toed_sloth"],
    "virginia-aquarium": ["shark", "sea_turtle", "jellyfish"],
    "waikiki-aquarium": ["seahorse", "jellyfish", "shark"],
}

STARTER = {
    "audubon-aquarium",
    "childrens-aquarium-dallas",
    "dubai-aquarium",
    "florida-aquarium",
    "istanbul-aquarium",
    "lotte-aquarium-seoul",
    "milan-aquarium",
    "new-england-aquarium",
    "osaka-aquarium",
    "seattle-aquarium",
    "shanghai-ocean-aquarium",
    "virginia-aquarium",
}
SHORT = {
    "audubon-aquarium",
    "dubai-aquarium",
    "lotte-aquarium-seoul",
    "milan-aquarium",
    "virginia-aquarium",
}
ZOO_UNTOUCHED = (
    "omaha-henry-doorly",
    "pittsburgh-zoo",
    "point-defiance-zoo",
    "san-diego-safari-park",
)


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

    def test_wave3a_start_here_unchanged(self):
        for slug, route in WAVE3A_ROUTES.items():
            self.assertEqual(_load_venue(slug).get("route_90m"), route, slug)

    def test_wave3b_start_here_unchanged(self):
        for slug, route in WAVE3B_ROUTES.items():
            self.assertEqual(_load_venue(slug).get("route_90m"), route, slug)

    def test_zoo_aq_and_safari_untouched(self):
        self.assertEqual(_load_venue("omaha-henry-doorly").get("route_90m"), WAVE2B_ROUTES["omaha-henry-doorly"])
        self.assertEqual(_load_venue("pittsburgh-zoo").get("route_90m"), WAVE2B_ROUTES["pittsburgh-zoo"])
        self.assertEqual(_load_venue("point-defiance-zoo").get("route_90m"), WAVE2B_ROUTES["point-defiance-zoo"])
        self.assertEqual(_load_venue("san-diego-safari-park").get("type"), "safari_zoo")


class Wave4KindFilterTests(unittest.TestCase):
    def test_only_aquarium_or_both_on_wave4(self):
        kinds = load_card_kinds()
        zoo_only = {s for s, row in kinds.items() if row["kind"] == ZOO_ONLY_KIND}
        neither = {s for s, row in kinds.items() if row["kind"] == NEITHER_KIND}
        venues = _load_catalog_venues()
        for slug in WAVE4:
            data = _load_venue(slug)
            self.assertEqual(data.get("type"), "aquarium", slug)
            cids = [it.get("catalog_id") for it in data.get("items") or []]
            if slug not in SHORT:
                self.assertGreaterEqual(len(cids), 3, slug)
            for cid in cids:
                self.assertIn(cid, kinds, f"{slug} unknown slug {cid}")
                self.assertIn(kinds[cid]["kind"], AQUARIUM_OK_KINDS, f"{slug} {cid}")
                self.assertNotIn(cid, zoo_only)
                self.assertNotIn(cid, neither)
            ven = venues[slug]
            for cid in list(ven.get("animalIds") or []) + list(ven.get("featuredAnimalIds") or []):
                self.assertTrue(card_ok_on_aquarium_kit(cid, kinds), f"{slug} catalog {cid}")
                self.assertNotIn(cid, zoo_only)
                self.assertNotIn(cid, neither)

    def test_catalog_js_matches_venue_json(self):
        venues = _load_catalog_venues()
        for slug in WAVE4:
            data = _load_venue(slug)
            cids = [it.get("catalog_id") for it in data.get("items") or []]
            self.assertEqual(venues[slug]["animalIds"], cids, slug)
            self.assertEqual(venues[slug]["featuredAnimalIds"][:3], cids[:3], slug)
            self.assertEqual(data.get("route_90m"), WAVE4_ROUTES[slug], slug)

    def test_starter_vs_verified_dates(self):
        for slug in WAVE4:
            data = _load_venue(slug)
            if slug in STARTER:
                self.assertIsNone(data.get("last_verified"), slug)
                self.assertEqual(data.get("status"), "partial", slug)
                self.assertEqual(data.get("list_confidence"), "partial", slug)
                self.assertFalse(data.get("last_presence_audit"), slug)
            else:
                self.assertEqual(data.get("last_verified"), "2026-08-23", slug)
                self.assertEqual(data.get("status"), "verified", slug)
                self.assertEqual(data.get("list_confidence"), "audited", slug)


class Wave4HonestyTests(unittest.TestCase):
    def test_no_lemur_on_dwa(self):
        data = _load_venue("dallas-world-aquarium")
        cids = {it.get("catalog_id") for it in data.get("items") or []}
        self.assertNotIn("ring-tailed-lemur", cids)
        self.assertIn("two-toed-sloth", cids)
        bans = {row.get("catalog_id") for row in data.get("do_not_list") or []}
        self.assertIn("ring-tailed-lemur", bans)
        venues = _load_catalog_venues()
        self.assertNotIn("ring-tailed-lemur", venues["dallas-world-aquarium"].get("animalIds") or [])
        self.assertEqual(data.get("route_90m"), WAVE4_ROUTES["dallas-world-aquarium"])

    def test_false_labels_are_banned(self):
        cases = {
            "aquarium-of-the-pacific": ("african-penguin", "asian-small-clawed-otter"),
            "audubon-aquarium": ("asian-small-clawed-otter", "two-toed-sloth"),
            "childrens-aquarium-dallas": ("asian-small-clawed-otter", "two-toed-sloth", "crab"),
            "dallas-world-aquarium": ("ring-tailed-lemur", "asian-small-clawed-otter", "sea-turtle"),
            "dubai-aquarium": ("african-penguin", "sea-otter"),
            "florida-aquarium": ("asian-small-clawed-otter", "sea-otter"),
            "istanbul-aquarium": ("african-penguin", "asian-small-clawed-otter"),
            "lotte-aquarium-seoul": ("african-penguin", "asian-small-clawed-otter"),
            "milan-aquarium": ("sea-turtle", "clownfish"),
            "monterey-bay-aquarium": ("african-penguin", "asian-small-clawed-otter", "clownfish"),
            "national-aquarium-baltimore": ("african-penguin", "asian-small-clawed-otter"),
            "osaka-aquarium": ("african-penguin", "stingray"),
            "seattle-aquarium": ("sea-turtle", "african-penguin"),
            "shanghai-ocean-aquarium": ("african-penguin", "eel"),
            "shedd-aquarium": ("african-penguin", "asian-small-clawed-otter"),
            "vancouver-aquarium": ("asian-small-clawed-otter", "african-penguin", "sea-turtle"),
            "virginia-aquarium": ("asian-small-clawed-otter", "sea-otter"),
            "waikiki-aquarium": ("sea-turtle", "clownfish"),
        }
        for slug, banned in cases.items():
            data = _load_venue(slug)
            cids = {it.get("catalog_id") for it in data.get("items") or []}
            bans = {row.get("catalog_id") for row in data.get("do_not_list") or []}
            for cid in banned:
                self.assertNotIn(cid, cids, f"{slug} still lists {cid}")
                self.assertIn(cid, bans, f"{slug} missing do_not_list {cid}")

    def test_no_invented_cards(self):
        kinds = load_card_kinds()
        for slug in WAVE4:
            data = _load_venue(slug)
            for it in data.get("items") or []:
                cid = it.get("catalog_id")
                self.assertIn(cid, kinds, f"{slug} invented {cid}")
                self.assertTrue((FP / "cards" / cid / "index.html").is_file(), f"{slug} unpublished {cid}")


class StartHereFromAndNextTests(unittest.TestCase):
    def test_kit_from_query_covers_wave4(self):
        self.assertEqual(kit_from_query("georgia-aquarium"), "from=georgia-aquarium")
        self.assertEqual(kit_from_query("dallas-world-aquarium"), "from=dallas-world-aquarium")
        self.assertEqual(kit_from_query("monterey-bay-aquarium"), "from=monterey-bay-aquarium")
        self.assertEqual(kit_from_query("yellowstone"), "")

    def test_start_here_hrefs_include_from(self):
        for slug in WAVE4:
            href = start_here_card_href("shark", slug)
            self.assertIn(f"from={slug}", href, slug)

    def test_place_page_start_here_has_from(self):
        for slug in WAVE4:
            start = _start_here(slug)
            self.assertIn(f"from={slug}", start, slug)
            self.assertNotIn("from=dallas-zoo", start, slug)

    def test_prior_wave_place_pages_keep_start_here(self):
        dallas = _start_here("dallas-zoo")
        self.assertIn("Reticulated giraffe", dallas)
        self.assertIn("from=dallas-zoo", dallas)
        safari = _start_here("san-diego-safari-park")
        self.assertIn("from=san-diego-safari-park", safari)
        self.assertNotIn("Giant panda", safari)

    def test_next_follows_that_kit(self):
        kits = start_here_next_by_kit()
        self.assertEqual(kits["dallas-zoo"]["reticulated-giraffe"]["id"], "african-elephant")
        self.assertEqual(kits["georgia-aquarium"]["whale-shark"]["id"], "manta-ray")
        self.assertEqual(kits["monterey-bay-aquarium"]["jellyfish"]["id"], "sea-otter")
        self.assertEqual(kits["dallas-world-aquarium"]["two-toed-sloth"]["id"], "african-penguin")
        self.assertEqual(kits["shedd-aquarium"]["sea-otter"]["id"], "shark")
        self.assertEqual(kits["two-oceans-aquarium"]["african-penguin"]["id"], "shark")
        panda = card_next_matches("giant-panda")
        by_slug = {slug: nxt["id"] for slug, nxt in panda}
        self.assertEqual(by_slug["san-diego-zoo"], "koala")
        self.assertEqual(by_slug["national-zoo"], "asian-small-clawed-otter")
        self.assertNotIn("dallas-world-aquarium", by_slug)

    def test_no_zoo_only_on_wave4_place_pages(self):
        kinds = load_card_kinds()
        zoo_only = [s for s, row in kinds.items() if row["kind"] == ZOO_ONLY_KIND]
        neither = [s for s, row in kinds.items() if row["kind"] == NEITHER_KIND]
        for slug in WAVE4:
            html = (FP / slug / "index.html").read_text(encoding="utf-8")
            visible = _visible(html)
            for aid in zoo_only + neither:
                self.assertNotIn(f"/field-pack/cards/{aid}/", visible, f"{slug} {aid}")


if __name__ == "__main__":
    unittest.main()
