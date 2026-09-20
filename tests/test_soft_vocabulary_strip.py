"""Editorial soft jargon must not appear in user-visible study copy."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from study_cards import (  # noqa: E402
    SOURCE_APPROX_NOTE,
    STUDY_CARDS,
    strip_editorial_soft_display,
)

SOFT_MARK = re.compile(
    r"\(soft\)|\([^)]*\bsoft\)|Soft on |\bstay soft\b|\bstays soft\b",
    re.I,
)


class SoftVocabularyStripTests(unittest.TestCase):
    def test_strip_helpers(self):
        self.assertEqual(
            strip_editorial_soft_display(
                "The biggest living fish in the ocean (size soft)."
            ),
            "The biggest living fish in the ocean.",
        )
        self.assertEqual(
            strip_editorial_soft_display(
                "Wikipedia: filter feeder. Soft on litres-per-hour."
            ),
            "Wikipedia: filter feeder.",
        )
        self.assertIn(
            "still vary",
            strip_editorial_soft_display(
                "Family-tree site details stay soft. Why not lock one fossil beach forever?"
            ),
        )
        self.assertIn(
            "stay soft and fluffy",
            strip_editorial_soft_display(
                "so they stay soft and fluffy. The wings still help."
            ),
        )
        self.assertEqual(
            strip_editorial_soft_display(
                "Tiny stinging cells (many stings feel mild to people — soft)"
            ),
            "Tiny stinging cells (many stings feel mild to people)",
        )
        self.assertEqual(
            strip_editorial_soft_display(
                "Endangered — snapshot from fishing, bycatch, and ship strikes (soft)"
            ),
            "Endangered — snapshot from fishing, bycatch, and ship strikes",
        )

    def test_all_cards_source_approx_note(self):
        for cid, card in STUDY_CARDS.items():
            note = card.get("source_note") or ""
            self.assertIn(SOURCE_APPROX_NOTE, note, cid)

    def test_no_editorial_soft_in_display_fields(self):
        leftover = []
        for cid, card in STUDY_CARDS.items():
            for level, pack in (card.get("levels") or {}).items():
                for teach in pack.get("teach") or []:
                    if SOFT_MARK.search(teach) and "stay soft and fluffy" not in teach.lower():
                        leftover.append(f"{cid} {level} teach: {teach}")
                for q in pack.get("questions") or []:
                    for field in ("title", "stem", "why"):
                        val = str(q.get(field) or "")
                        if SOFT_MARK.search(val) and "stay soft and fluffy" not in val.lower():
                            leftover.append(
                                f"{cid} {level} {q.get('id')} {field}: {val[:100]}"
                            )
                    for ch in q.get("choices") or []:
                        if SOFT_MARK.search(ch):
                            leftover.append(f"{cid} {level} {q.get('id')} choice: {ch}")
            for key in ("talk_about", "push_further"):
                for line in card.get(key) or []:
                    if SOFT_MARK.search(line) and "stay soft and fluffy" not in line.lower():
                        leftover.append(f"{cid} {key}: {line}")
        self.assertEqual(leftover, [], "\n".join(leftover[:30]))

    def test_whale_shark_brief_examples_gone(self):
        easy = STUDY_CARDS["whale-shark"]["levels"]["easy"]
        self.assertEqual(easy["teach"][0], "The biggest living fish in the ocean.")
        whys = " ".join(q["why"] for q in easy["questions"])
        self.assertNotIn("Soft on", whys)
        self.assertNotIn("size soft", whys)
        hard = STUDY_CARDS["whale-shark"]["levels"]["hard"]
        for q in hard["questions"]:
            for ch in q["choices"]:
                self.assertNotIn("(soft)", ch)
                self.assertFalse(re.search(r"[—–-]\s*soft\s*$", ch))


if __name__ == "__main__":
    unittest.main()
