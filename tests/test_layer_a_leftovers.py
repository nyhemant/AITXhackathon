"""Layer A leftovers after PR #207: Photos, polar-bear TSV, JR soft, try-next, Watch Live."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from field_pack_catalog_kind import load_card_kinds  # noqa: E402
from generate_bdo_seo import (  # noqa: E402
    load_vft_by_card,
    vft_can_watch_live,
)
from rewrite_card_try_next import (  # noqa: E402
    check_grids,
    sealife_ids,
)
from study_cards import (  # noqa: E402
    STUDY_CARDS,
    strip_jr_soft_choice_label,
    study_try_next_hub,
    study_try_next_ids,
)

FP = REPO / "static" / "field-pack"
TSV = FP / "data" / "card-kinds.tsv"
HUB = FP / "cards" / "index.html"
SOFT_MARK = re.compile(r"\(soft\)|—\s*soft")


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


def _try_next_ids(html: str) -> list[str]:
    if "card-try-next-grid" not in html:
        return []
    grid = html.split("card-try-next-grid", 1)[1].split("</div>", 1)[0]
    return re.findall(r"/cards/([^/]+)/", grid)


class LayerALeftoversTests(unittest.TestCase):
    def test_polar_bear_is_wildlife_zoo_in_tsv_and_hub(self):
        kinds = load_card_kinds()
        row = kinds["polar-bear"]
        self.assertEqual(row["hub"], "wildlife")
        self.assertEqual(row["kind"], "zoo")
        self.assertEqual(row["title"], "Polar bear")
        self.assertIn("polar-bear\tPolar bear\twildlife\tzoo", TSV.read_text(encoding="utf-8"))
        hub = HUB.read_text(encoding="utf-8")
        wildlife = hub.split('id="cards-wildlife"', 1)[1].split('id="cards-', 1)[0]
        self.assertIn('data-card-id="polar-bear"', wildlife)
        self.assertIn('data-card-group="wildlife"', wildlife)
        self.assertIn('Wildlife <span class="seo-dir-count">22</span>', hub)

    def test_jr_easy_choice_labels_drop_soft_markers(self):
        self.assertEqual(
            strip_jr_soft_choice_label(
                "Cartilage — tough and flexible, like a shark’s skeleton (soft)"
            ),
            "Cartilage — tough and flexible, like a shark’s skeleton",
        )
        self.assertEqual(
            strip_jr_soft_choice_label(
                "Tiny stinging cells (many stings feel mild to people — soft)"
            ),
            "Tiny stinging cells (many stings feel mild to people)",
        )
        leftover = []
        for cid, card in STUDY_CARDS.items():
            easy = (card.get("levels") or {}).get("easy") or {}
            for q in easy.get("questions") or []:
                for ch in q.get("choices") or []:
                    if SOFT_MARK.search(ch):
                        leftover.append(f"{cid} {q.get('id')}: {ch}")
        self.assertEqual(leftover, [], "\n".join(leftover[:20]))

        choice_re = re.compile(r'data-choice="([^"]*)"')
        for cid in (
            "eel",
            "jellyfish",
            "kelp-forest",
            "manta-ray",
            "octopus",
            "sea-turtle",
            "seahorse",
            "starfish",
            "stingray",
            "whale-shark",
        ):
            html = (FP / "cards" / cid / "index.html").read_text(encoding="utf-8")
            main = _main(html)
            for raw in choice_re.findall(main):
                label = raw.replace("&amp;", "&").replace("&quot;", '"')
                self.assertFalse(SOFT_MARK.search(label), f"{cid}: {label}")

    def test_seahorse_jr_choice_drops_hippocampus(self):
        easy = STUDY_CARDS["seahorse"]["levels"]["easy"]
        labels = [ch for q in easy["questions"] for ch in q.get("choices") or []]
        self.assertTrue(any("real bony fish" in ch for ch in labels))
        self.assertFalse(any("Hippocampus" in ch for ch in labels))
        html = (FP / "cards" / "seahorse" / "index.html").read_text(encoding="utf-8")
        main = _main(html)
        self.assertIn("Yes — they are real bony fish, with many kinds", main)
        for raw in re.findall(r'data-choice="([^"]*)"', main):
            label = raw.replace("&amp;", "&").replace("&quot;", '"')
            self.assertNotIn("Hippocampus", label)

    def test_sealife_baked_try_next_stays_in_hub(self):
        kinds = load_card_kinds()
        tsv_sea = [cid for cid, row in kinds.items() if row.get("hub") == "sealife"]
        sealife = sealife_ids(kinds)
        self.assertEqual(sorted(sealife), sorted(tsv_sea))
        self.assertGreaterEqual(len(sealife), 17)
        self.assertIn("stingray", sealife)
        self.assertIn("starfish", sealife)
        self.assertIn("manta-ray", sealife)
        self.assertIn("whale-shark", sealife)
        for cid in sealife:
            want = study_try_next_ids(cid)
            html = (FP / "cards" / cid / "index.html").read_text(encoding="utf-8")
            baked = _try_next_ids(html)
            with self.subTest(card=cid):
                self.assertEqual(baked, want)
                self.assertNotIn("african-lion", baked)
                for nxt in baked:
                    self.assertEqual(study_try_next_hub(nxt, kinds), "sealife", nxt)
        self.assertEqual(check_grids(), [])

    def test_stingray_and_starfish_baked_try_next_never_offer_african_lion(self):
        """ParentTest: stingray + starfish first paint must stay sea — JS not required."""
        cases = {
            "stingray": ["manta-ray", "seahorse", "clownfish"],
            "starfish": ["sea-turtle", "octopus", "clownfish"],
        }
        for cid, want in cases.items():
            html = (FP / "cards" / cid / "index.html").read_text(encoding="utf-8")
            baked = _try_next_ids(html)
            with self.subTest(card=cid):
                self.assertEqual(baked, want)
                self.assertNotIn("african-lion", baked)
                grid = html.split("card-try-next-grid", 1)[1].split("</nav>", 1)[0]
                self.assertNotIn("/cards/african-lion/", grid)

    def test_library_only_cards_hide_watch_live(self):
        vft = load_vft_by_card()
        hidden = []
        for cid, rec in vft.items():
            path = FP / "cards" / cid / "index.html"
            if not path.is_file():
                continue
            if vft_can_watch_live(rec):
                continue
            kind_hub = (load_card_kinds().get(cid) or {}).get("hub")
            if kind_hub not in {"wildlife", "sealife"}:
                continue
            hidden.append(cid)
            html = path.read_text(encoding="utf-8")
            main = _main(html)
            with self.subTest(card=cid):
                self.assertNotIn("card-watch-live", main)
                self.assertNotIn("Watch Live", main)
                self.assertNotIn("card-page-photo-link", main)
        self.assertIn("cheetah", hidden)
        self.assertIn("koala", hidden)
        self.assertIn("manta-ray", hidden)
        self.assertIn("whale-shark", hidden)


if __name__ == "__main__":
    unittest.main()
