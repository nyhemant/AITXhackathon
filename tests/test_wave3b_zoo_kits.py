"""Wave 3b Field Trip Kit: official 3+10 + catalog-kind filter."""

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
from test_wave3a_zoo_kits import (  # noqa: E402
    WAVE1_ITEMS,
    WAVE1_ROUTES,
    WAVE2A_ROUTES,
    WAVE2B_ROUTES,
    WAVE3A_ROUTES,
)

FP = REPO / "static" / "field-pack"
VENUES = FP / "data" / "venues"
CATALOG_JS = FP / "js" / "catalog.js"

WAVE3B = (
    "al-ain-zoo",
    "antwerp-zoo",
    "athens-attica-zoo",
    "bangalore-bannerghatta",
    "bangkok-safari-world",
    "beijing-zoo",
    "bogota-zoo",
    "budapest-zoo",
    "cairo-zoo",
    "chapultepec-zoo",
    "delhi-zoo",
    "ecoparque-ba",
    "helsinki-zoo",
    "hong-kong-ocean-park",
    "jakarta-ragunan",
    "johannesburg-zoo",
    "kuala-lumpur-zoo",
    "lima-leyendas",
    "lisbon-zoo",
    "madrid-zoo",
    "manila-zoo",
    "moscow-zoo",
    "mumbai-byculla-zoo",
    "munich-zoo",
    "nairobi-safari-walk",
    "oslo-zoo",
    "rio-zoo",
    "rome-bioparco",
    "santiago-zoo",
    "sao-paulo-zoo",
    "seoul-zoo",
    "singapore-night-safari",
    "stockholm-skansen",
    "taipei-zoo",
    "ueno-zoo",
    "warsaw-zoo",
)

WAVE3B_ROUTES = {
    "al-ain-zoo": ["reticulated_giraffe", "african_lion", "zebra"],
    "antwerp-zoo": ["western_lowland_gorilla", "chimpanzee", "african_penguin"],
    "athens-attica-zoo": ["sumatran_tiger", "african_lion", "african_penguin"],
    "bangalore-bannerghatta": ["cheetah", "zebra", "ostrich"],
    "bangkok-safari-world": ["zebra", "orangutan", "reticulated_giraffe"],
    "beijing-zoo": ["giant_panda", "reticulated_giraffe"],
    "bogota-zoo": ["african_lion", "ostrich", "nile_hippo"],
    "budapest-zoo": ["african_penguin", "orangutan", "nile_hippo"],
    "cairo-zoo": [],
    "chapultepec-zoo": ["giant_panda", "african_lion", "orangutan"],
    "delhi-zoo": ["african_elephant", "nile_hippo", "ostrich"],
    "ecoparque-ba": [],
    "helsinki-zoo": ["red_panda"],
    "hong-kong-ocean-park": ["giant_panda", "red_panda", "two_toed_sloth"],
    "jakarta-ragunan": ["orangutan", "sumatran_tiger", "cheetah"],
    "johannesburg-zoo": ["african_lion", "african_elephant", "nile_hippo"],
    "kuala-lumpur-zoo": ["giant_panda", "orangutan", "african_lion"],
    "lima-leyendas": ["two_toed_sloth", "african_lion", "reticulated_giraffe"],
    "lisbon-zoo": ["african_elephant", "sumatran_tiger", "koala"],
    "madrid-zoo": ["giant_panda", "western_lowland_gorilla", "african_penguin"],
    "manila-zoo": ["african_lion", "ostrich", "freshwater_fish"],
    "moscow-zoo": ["giant_panda", "western_lowland_gorilla", "orangutan"],
    "mumbai-byculla-zoo": [],
    "munich-zoo": ["western_lowland_gorilla", "orangutan", "reticulated_giraffe"],
    "nairobi-safari-walk": ["african_lion", "cheetah", "zebra"],
    "oslo-zoo": ["chimpanzee", "african_lion", "cheetah"],
    "rio-zoo": ["african_lion", "orangutan", "two_toed_sloth"],
    "rome-bioparco": ["reticulated_giraffe", "sumatran_tiger", "african_penguin"],
    "santiago-zoo": ["african_elephant", "african_lion", "chimpanzee"],
    "sao-paulo-zoo": ["african_lion", "chimpanzee", "nile_hippo"],
    "seoul-zoo": ["red_panda", "chimpanzee", "african_lion"],
    "singapore-night-safari": ["asian_small_clawed_otter"],
    "stockholm-skansen": [],
    "taipei-zoo": ["giant_panda", "koala", "red_panda"],
    "ueno-zoo": ["red_panda", "sumatran_tiger", "western_lowland_gorilla"],
    "warsaw-zoo": ["african_elephant", "western_lowland_gorilla", "african_penguin"],
}

STARTER = {
    "al-ain-zoo",
    "bangkok-safari-world",
    "beijing-zoo",
    "bogota-zoo",
    "cairo-zoo",
    "chapultepec-zoo",
    "ecoparque-ba",
    "helsinki-zoo",
    "jakarta-ragunan",
    "johannesburg-zoo",
    "kuala-lumpur-zoo",
    "moscow-zoo",
    "mumbai-byculla-zoo",
    "rio-zoo",
    "sao-paulo-zoo",
    "stockholm-skansen",
}
SHORT = {
    "beijing-zoo",
    "cairo-zoo",
    "ecoparque-ba",
    "helsinki-zoo",
    "mumbai-byculla-zoo",
    "singapore-night-safari",
    "stockholm-skansen",
}
EMPTY = {"cairo-zoo", "ecoparque-ba", "mumbai-byculla-zoo", "stockholm-skansen"}
HAS_START_HERE = tuple(slug for slug in WAVE3B if slug not in EMPTY)
ZOO_AQ = ("hong-kong-ocean-park", "madrid-zoo")
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

    def test_wave3a_start_here_unchanged(self):
        for slug, route in WAVE3A_ROUTES.items():
            self.assertEqual(_load_venue(slug).get("route_90m"), route, slug)


class Wave3bKindFilterTests(unittest.TestCase):
    def test_no_aquarium_only_or_neither_on_wave3b(self):
        kinds = load_card_kinds()
        aquarium = {s for s, row in kinds.items() if row["kind"] == AQUARIUM_ONLY_KIND}
        neither = {s for s, row in kinds.items() if row["kind"] == "neither"}
        venues = _load_catalog_venues()
        for slug in WAVE3B:
            data = _load_venue(slug)
            cids = [it.get("catalog_id") for it in data.get("items") or []]
            if slug not in SHORT:
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
        for slug in WAVE3B:
            data = _load_venue(slug)
            cids = [it.get("catalog_id") for it in data.get("items") or []]
            self.assertEqual(venues[slug]["animalIds"], cids, slug)
            self.assertEqual(venues[slug]["featuredAnimalIds"][:3], cids[:3], slug)
            self.assertEqual(data.get("route_90m"), WAVE3B_ROUTES[slug], slug)

    def test_starter_vs_verified_dates(self):
        for slug in WAVE3B:
            data = _load_venue(slug)
            if slug in STARTER:
                self.assertIsNone(data.get("last_verified"), slug)
                self.assertEqual(data.get("status"), "partial", slug)
                self.assertEqual(data.get("list_confidence"), "partial", slug)
            else:
                self.assertEqual(data.get("last_verified"), "2026-08-23", slug)
                self.assertEqual(data.get("status"), "verified", slug)
                self.assertEqual(data.get("list_confidence"), "audited", slug)

    def test_official_urls_are_http(self):
        expected = {
            "cairo-zoo": "http://www.giza.gov.eg/English/Tourism/Landmarks/EZoo.aspx",
            "oslo-zoo": "https://www.dyreparken.no/",
            "chapultepec-zoo": "http://www.data.sedema.cdmx.gob.mx/zoo_chapultepec/",
            "ueno-zoo": "https://www.tokyo-zoo.net/en/ueno/",
            "moscow-zoo": "https://moscowzoo.ru/",
            "ecoparque-ba": "https://buenosaires.gob.ar/ecoparque",
        }
        for slug in WAVE3B:
            url = _load_venue(slug).get("official_url") or ""
            self.assertTrue(url.startswith("http"), slug)
            if slug in expected:
                self.assertEqual(url, expected[slug], slug)


class Wave3bHonestyTests(unittest.TestCase):
    def test_false_labels_are_banned(self):
        cases = {
            "al-ain-zoo": ("african-elephant", "sumatran-tiger", "african-penguin"),
            "antwerp-zoo": ("african-elephant", "nile-hippo", "sumatran-tiger"),
            "athens-attica-zoo": ("african-elephant", "nile-hippo", "galapagos-tortoise"),
            "bangalore-bannerghatta": ("african-elephant", "sumatran-tiger"),
            "bangkok-safari-world": ("african-elephant", "sumatran-tiger", "nile-hippo", "shark"),
            "beijing-zoo": ("african-elephant", "sumatran-tiger"),
            "bogota-zoo": ("african-elephant", "sumatran-tiger", "reticulated-giraffe"),
            "budapest-zoo": ("african-elephant", "african-lion", "sumatran-tiger", "chimpanzee"),
            "cairo-zoo": ("african-lion", "african-elephant", "nile-hippo"),
            "chapultepec-zoo": ("sumatran-tiger", "african-penguin"),
            "delhi-zoo": ("african-lion", "sumatran-tiger", "chimpanzee", "zebra"),
            "ecoparque-ba": ("caribbean-flamingo", "orangutan", "african-elephant", "sumatran-tiger"),
            "helsinki-zoo": ("sumatran-tiger", "african-lion", "asian-small-clawed-otter"),
            "hong-kong-ocean-park": ("african-penguin", "sumatran-tiger", "shark"),
            "jakarta-ragunan": ("african-elephant", "nile-hippo"),
            "johannesburg-zoo": ("sumatran-tiger", "orangutan", "ostrich", "african-penguin"),
            "kuala-lumpur-zoo": ("african-elephant", "sumatran-tiger", "african-penguin", "western-lowland-gorilla"),
            "lima-leyendas": ("sumatran-tiger", "african-penguin", "caribbean-flamingo", "african-elephant"),
            "lisbon-zoo": ("galapagos-tortoise",),
            "madrid-zoo": ("african-elephant", "sumatran-tiger", "african-lion", "shark"),
            "manila-zoo": ("african-elephant", "sumatran-tiger", "reticulated-giraffe", "nile-hippo"),
            "moscow-zoo": ("african-elephant", "nile-hippo", "sumatran-tiger", "african-lion"),
            "mumbai-byculla-zoo": ("african-elephant", "african-penguin", "sumatran-tiger", "cm-outdoor"),
            "munich-zoo": ("african-elephant", "sumatran-tiger", "african-penguin", "nile-hippo"),
            "nairobi-safari-walk": ("nile-hippo", "african-elephant", "sumatran-tiger"),
            "oslo-zoo": ("sumatran-tiger", "african-elephant", "western-lowland-gorilla", "african-penguin"),
            "rio-zoo": ("african-elephant", "sumatran-tiger"),
            "rome-bioparco": ("african-elephant", "african-lion", "western-lowland-gorilla"),
            "santiago-zoo": ("sumatran-tiger", "caribbean-flamingo"),
            "sao-paulo-zoo": ("african-elephant", "western-lowland-gorilla", "sumatran-tiger"),
            "seoul-zoo": ("african-elephant", "sumatran-tiger", "african-penguin"),
            "singapore-night-safari": ("african-elephant", "african-lion", "sumatran-tiger", "orangutan", "cheetah"),
            "stockholm-skansen": ("red-panda", "asian-small-clawed-otter", "african-lion", "cm-outdoor"),
            "taipei-zoo": ("sumatran-tiger", "caribbean-flamingo"),
            "ueno-zoo": ("giant-panda", "african-elephant", "chimpanzee", "asian-small-clawed-otter"),
            "warsaw-zoo": ("galapagos-tortoise", "caribbean-flamingo"),
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
            self.assertNotIn("shark", cids, f"{slug} shark")

    def test_night_safari_is_not_singapore_zoo(self):
        data = _load_venue("singapore-night-safari")
        self.assertEqual(data.get("type"), "safari_zoo")
        self.assertEqual(data.get("route_90m"), WAVE3B_ROUTES["singapore-night-safari"])
        cids = [it.get("catalog_id") for it in data.get("items") or []]
        self.assertEqual(cids, ["asian-small-clawed-otter"])
        self.assertNotIn("orangutan", cids)
        self.assertNotIn("two-toed-sloth", cids)
        self.assertNotIn("cheetah", cids)
        zoo = _load_venue("singapore-zoo")
        self.assertEqual(zoo.get("route_90m"), WAVE3A_ROUTES["singapore-zoo"])

    def test_skansen_drops_neither_cards(self):
        data = _load_venue("stockholm-skansen")
        cids = {it.get("catalog_id") for it in data.get("items") or []}
        self.assertNotIn("cm-outdoor", cids)
        venues = _load_catalog_venues()
        self.assertEqual(venues["stockholm-skansen"].get("animalIds") or [], [])
        self.assertEqual(data.get("route_90m"), [])

    def test_no_invented_cards(self):
        kinds = load_card_kinds()
        for slug in WAVE3B:
            data = _load_venue(slug)
            for it in data.get("items") or []:
                cid = it.get("catalog_id")
                self.assertIn(cid, kinds, f"{slug} invented {cid}")
                self.assertTrue((FP / "cards" / cid / "index.html").is_file(), f"{slug} unpublished {cid}")


class StartHereFromAndNextTests(unittest.TestCase):
    def test_kit_from_query_covers_wave3b(self):
        self.assertEqual(kit_from_query("madrid-zoo"), "from=madrid-zoo")
        self.assertEqual(kit_from_query("singapore-night-safari"), "from=singapore-night-safari")
        self.assertEqual(kit_from_query("hong-kong-ocean-park"), "from=hong-kong-ocean-park")
        self.assertEqual(kit_from_query("ueno-zoo"), "from=ueno-zoo")
        self.assertEqual(kit_from_query("yellowstone"), "")

    def test_start_here_hrefs_include_from(self):
        for slug in WAVE3B:
            href = start_here_card_href("african-lion", slug)
            self.assertIn(f"from={slug}", href, slug)

    def test_place_page_start_here_has_from(self):
        for slug in HAS_START_HERE:
            start = _start_here(slug)
            self.assertIn(f"from={slug}", start, slug)
            self.assertNotIn("from=dallas-zoo", start, slug)

    def test_prior_wave_place_pages_keep_start_here(self):
        dallas = _start_here("dallas-zoo")
        self.assertIn("Reticulated giraffe", dallas)
        self.assertIn("from=dallas-zoo", dallas)
        singapore = _start_here("singapore-zoo")
        self.assertIn("from=singapore-zoo", singapore)
        self.assertIn("Orangutan", singapore)

    def test_next_follows_that_kit(self):
        panda = card_next_matches("giant-panda")
        by_slug = {slug: nxt["id"] for slug, nxt in panda}
        self.assertEqual(by_slug["san-diego-zoo"], "koala")
        self.assertEqual(by_slug["national-zoo"], "asian-small-clawed-otter")
        self.assertEqual(by_slug["adelaide-zoo"], "koala")
        self.assertEqual(by_slug["taipei-zoo"], "koala")
        self.assertEqual(by_slug["madrid-zoo"], "western-lowland-gorilla")
        self.assertEqual(by_slug["hong-kong-ocean-park"], "red-panda")
        kits = start_here_next_by_kit()
        self.assertEqual(kits["dallas-zoo"]["reticulated-giraffe"]["id"], "african-elephant")
        self.assertEqual(kits["singapore-zoo"]["orangutan"]["id"], "two-toed-sloth")
        self.assertEqual(kits["lisbon-zoo"]["african-elephant"]["id"], "sumatran-tiger")
        self.assertEqual(kits["munich-zoo"]["western-lowland-gorilla"]["id"], "orangutan")
        self.assertEqual(kits["rome-bioparco"]["reticulated-giraffe"]["id"], "sumatran-tiger")
        self.assertEqual(kits["ueno-zoo"]["red-panda"]["id"], "sumatran-tiger")
        self.assertNotIn("singapore-night-safari", kits)

    def test_card_pages_emit_kit_aware_panda_next(self):
        html = (FP / "cards" / "giant-panda" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-next-from="national-zoo"', html)
        self.assertIn('data-next-from="san-diego-zoo"', html)
        self.assertIn('data-next-from="taipei-zoo"', html)
        self.assertIn("Next: Asian small-clawed otter", html)
        self.assertIn("Next: Koala", html)

    def test_no_aquarium_only_on_wave3b_place_pages(self):
        kinds = load_card_kinds()
        aquarium = [s for s, row in kinds.items() if row["kind"] == AQUARIUM_ONLY_KIND]
        for slug in WAVE3B:
            html = (FP / slug / "index.html").read_text(encoding="utf-8")
            visible = _visible(html)
            for aid in aquarium:
                self.assertNotIn(f"/field-pack/cards/{aid}/", visible, f"{slug} {aid}")


if __name__ == "__main__":
    unittest.main()
