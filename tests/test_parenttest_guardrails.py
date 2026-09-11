"""ParentTest production guardrails — Try-next kingdom, Watch Live, Photos.

These fail `python3 -m unittest discover -s tests` when Sep 2026 Layer A/B
regressions return. Checkers live in scripts/parenttest_guardrails.py so the
same assertions can run as:

    python3 -m unittest tests.test_parenttest_guardrails
    python3 scripts/parenttest_guardrails.py --check
    pytest tests/test_parenttest_guardrails.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from field_pack_card_kind import card_kind  # noqa: E402
from field_pack_catalog_kind import load_card_kinds  # noqa: E402
from parenttest_guardrails import (  # noqa: E402
    ANIMAL_SEA_LIFE_HUBS,
    EMPTY_PICTURES_ALLOW,
    TRY_NEXT_CROSS_KINGDOM_ALLOW,
    WATCH_LIVE_WITHOUT_HABITAT_ALLOW,
    card_kingdom,
    cross_kingdom_try_next_issues,
    dead_watch_live_issues,
    empty_pictures_issues,
    published_animal_sea_life_ids,
    tour_habitat_ids,
)
from study_cards import study_try_next_hub  # noqa: E402

FP = REPO / "static" / "field-pack"

# Sep 11 ParentTest fixtures — synthetic HTML / catalog, not live files.
LION_ON_SEALIFE_HTML = """
<main class="card-page">
<nav class="card-try-next no-print" aria-label="Try next">
  <p class="card-try-next-kicker">Try next</p>
  <div class="card-try-next-grid">
    <a class="card-try-next-link" href="/field-pack/cards/african-lion/">African lion</a>
    <a class="card-try-next-link" href="/field-pack/cards/jellyfish/">Jellyfish</a>
  </div>
</nav>
</main>
"""
MANTA_DEAD_LIVE_HTML = """
<main class="card-page">
  <a class="btn btn-primary card-watch-live"
     href="/field-pack/virtual-field-trip/?tab=aquarium&amp;from=card#habitat=manta-ray">Watch Live</a>
</main>
"""
EMPTY_PICTURES_CATALOG = {
    "asian-small-clawed-otter": {
        "id": "asian-small-clawed-otter",
        "links": {"pictures": ""},
    },
    "eel": {"id": "eel", "links": {"pictures": ""}},
}


class KingdomMappingTests(unittest.TestCase):
    """Lock the TSV mapping the other checks use — no new ontology."""

    def test_tsv_hubs_are_the_kingdom_table(self):
        kinds = load_card_kinds()
        self.assertEqual(ANIMAL_SEA_LIFE_HUBS, frozenset({"wildlife", "sealife"}))
        self.assertEqual(kinds["african-lion"]["hub"], "wildlife")
        self.assertEqual(kinds["stingray"]["hub"], "sealife")
        self.assertEqual(kinds["manta-ray"]["hub"], "sealife")
        self.assertEqual(kinds["american-bison"]["hub"], "parks")
        self.assertEqual(kinds["sci-dinosaur"]["hub"], "attractions")

        self.assertEqual(card_kind({"id": "african-lion"}), "animal")
        self.assertEqual(card_kind({"id": "stingray"}), "sea_life")
        self.assertEqual(card_kind({"id": "american-bison"}), "place_feature")
        self.assertEqual(card_kind({"id": "sci-dinosaur"}), "attraction")

        self.assertEqual(study_try_next_hub("stingray", kinds), "sealife")
        self.assertEqual(study_try_next_hub("african-lion", kinds), "wildlife")
        self.assertEqual(card_kingdom("stingray", kinds), "sealife")
        self.assertEqual(card_kingdom("african-lion", kinds), "wildlife")
        # Parks study cards group as wildlife under the existing helper only.
        self.assertEqual(study_try_next_hub("american-bison", kinds), "wildlife")

        published = published_animal_sea_life_ids(kinds)
        self.assertIn("african-lion", published)
        self.assertIn("stingray", published)
        self.assertIn("eel", published)
        self.assertIn("asian-small-clawed-otter", published)
        self.assertNotIn("american-bison", published)
        self.assertNotIn("cuyahoga-towpath", published)
        self.assertNotIn("sci-dinosaur", published)
        self.assertGreaterEqual(len(published), 39)

    def test_allowlists_stay_empty_or_tiny(self):
        self.assertEqual(TRY_NEXT_CROSS_KINGDOM_ALLOW, ())
        self.assertEqual(WATCH_LIVE_WITHOUT_HABITAT_ALLOW, ())
        self.assertEqual(EMPTY_PICTURES_ALLOW, ())


class TryNextKingdomTests(unittest.TestCase):
    def test_baked_try_next_stays_in_kingdom(self):
        issues = cross_kingdom_try_next_issues()
        self.assertEqual(issues, [], "\n".join(issues))

    def test_sep11_lion_on_sealife_would_fail(self):
        """Bake lag: sealife first paint still showing african-lion thumb."""
        issues = cross_kingdom_try_next_issues(
            html_by_id={"stingray": LION_ON_SEALIFE_HTML}
        )
        self.assertTrue(issues)
        self.assertTrue(
            any("african-lion" in row and "stingray" in row for row in issues),
            issues,
        )


class WatchLiveHabitatTests(unittest.TestCase):
    def test_visible_watch_live_has_tour_habitat(self):
        issues = dead_watch_live_issues()
        self.assertEqual(issues, [], "\n".join(issues))
        real = tour_habitat_ids()
        self.assertIn("african-lion", real)
        self.assertIn("eel", real)
        self.assertNotIn("manta-ray", real)

    def test_sep11_manta_dead_live_would_fail(self):
        """Library-only / missing aquarium habitat still showing Watch Live."""
        issues = dead_watch_live_issues(
            html_by_id={"manta-ray": MANTA_DEAD_LIVE_HTML}
        )
        self.assertTrue(issues)
        self.assertTrue(any("manta-ray" in row for row in issues), issues)


class PhotosNotEmptyTests(unittest.TestCase):
    def test_animal_sea_life_pictures_are_nonempty(self):
        issues = empty_pictures_issues()
        self.assertEqual(issues, [], "\n".join(issues))

    def test_sep11_empty_pictures_would_fail(self):
        """Otter / eel catalog pictures wiped — Photos button would hide."""
        issues = empty_pictures_issues(
            catalog=EMPTY_PICTURES_CATALOG,
            ids=["asian-small-clawed-otter", "eel"],
        )
        self.assertEqual(len(issues), 2)
        joined = "\n".join(issues)
        self.assertIn("asian-small-clawed-otter", joined)
        self.assertIn("eel", joined)

    def test_parks_and_attractions_are_excluded(self):
        kinds = load_card_kinds()
        published = set(published_animal_sea_life_ids(kinds))
        for cid in ("cuyahoga-towpath", "sci-dinosaur", "american-bison", "elk"):
            self.assertNotIn(cid, published)
        # Default sweep uses published animal/sea_life only — empty park pictures stay out.
        issues = empty_pictures_issues(
            catalog={
                "cuyahoga-towpath": {"id": "cuyahoga-towpath", "links": {"pictures": ""}},
                "sci-dinosaur": {"id": "sci-dinosaur", "links": {"pictures": ""}},
            }
        )
        self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main()
