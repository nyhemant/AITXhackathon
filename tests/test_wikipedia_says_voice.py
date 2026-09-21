"""Quiz why fields do not talk in a “Wikipedia says” voice.

Footer source_note may still credit Wikipedia.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from study_cards import STUDY_CARDS, strip_wikipedia_says_voice  # noqa: E402


WIKI_SAYS = re.compile(r"Wikipedia says", re.I)


class WikipediaSaysVoiceTests(unittest.TestCase):
    def test_strip_drops_attribution_and_keeps_the_fact(self):
        self.assertEqual(
            strip_wikipedia_says_voice(
                "Wikipedia says the giraffe heart must generate about double the blood pressure."
            ),
            "The giraffe heart must generate about double the blood pressure.",
        )
        self.assertEqual(
            strip_wikipedia_says_voice(
                "They hunt in the sea. Wikipedia says they feed primarily on fish and squid."
            ),
            "They hunt in the sea. They feed primarily on fish and squid.",
        )
        self.assertEqual(
            strip_wikipedia_says_voice(
                "They can go many months without drinking, and Wikipedia says they can endure about a year."
            ),
            "They can go many months without drinking, and they can endure about a year.",
        )

    def test_why_fields_do_not_say_wikipedia_says(self):
        hits = []
        notes = 0
        for cid, card in STUDY_CARDS.items():
            note = str(card.get("source_note") or "")
            if "Wikipedia" in note:
                notes += 1
            for level, pack in (card.get("levels") or {}).items():
                for q in pack.get("questions") or []:
                    why = str(q.get("why") or "")
                    if WIKI_SAYS.search(why):
                        hits.append(f"{cid} {level} {q.get('id')}: {why[:120]}")
        self.assertEqual(hits, [])
        self.assertEqual(notes, len(STUDY_CARDS))


if __name__ == "__main__":
    unittest.main()
