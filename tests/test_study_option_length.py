"""Study-card option length: correct choice must not dwarf distractors.

Scans all cards and reports offenders. Fails the suite only for cards in
OPTION_LENGTH_ENFORCED_CARD_IDS (whale-shark first; expand as cards are fixed).
Also run: python3 scripts/check_study_option_length.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from study_cards import (  # noqa: E402
    OPTION_LENGTH_ENFORCED_CARD_IDS,
    OPTION_LENGTH_RATIO,
    STUDY_CARDS,
    option_length_failures,
    option_length_offenders,
)


class StudyOptionLengthTests(unittest.TestCase):
    def test_enforced_cards_pass_option_length_gate(self):
        self.assertIn("whale-shark", OPTION_LENGTH_ENFORCED_CARD_IDS)
        failures = option_length_failures()
        self.assertEqual(
            failures,
            [],
            msg=(
                "correct option > "
                f"{OPTION_LENGTH_RATIO}× median on enforced cards: "
                + "; ".join(
                    f"{r['card_id']}/{r['level']}/{r['question_id']} "
                    f"ratio={r['ratio']} counts={r['counts']}"
                    for r in failures
                )
            ),
        )

    def test_scan_lists_offenders_for_rollout(self):
        """Collect-only catalog scan — documents remaining drift."""
        rows = option_length_offenders()
        enforced = [
            r for r in rows if r["card_id"] in OPTION_LENGTH_ENFORCED_CARD_IDS
        ]
        self.assertEqual(enforced, [])
        # Sanity: catalog still has other offenders until rollout expands.
        other = [r for r in rows if r["card_id"] not in OPTION_LENGTH_ENFORCED_CARD_IDS]
        self.assertGreater(
            len(other),
            0,
            msg="expected other cards still to fail until rollout expands",
        )
        self.assertIn("whale-shark", STUDY_CARDS)


if __name__ == "__main__":
    unittest.main()
