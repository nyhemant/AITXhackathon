"""No half-sentences in study-card text shown to kids (2026-10-26).

The editorial "soft" stripper used to cut a note only up to the word "soft",
leaving fragments such as "… wild populations. and do not lock one infection
rate." This scans every displayed string in the shipped study data (teach,
talk/push, titles, stems, choices, why) for fragment patterns, and checks the
stripper drops editorial notes as whole sentences.
"""

from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from study_cards import strip_editorial_soft_display  # noqa: E402

STUDY_JSON = REPO / "static" / "field-pack" / "data" / "study-cards.json"
STUDY_DATA_JS = REPO / "static" / "field-pack" / "js" / "study-cards-data.js"

# Abbreviations that may be followed by a lowercase word: one-letter genus or
# species initials (P. l. leo, F. a. arctica), e.g., i.e., et al., vs., c., ca.
_ABBREV_BEFORE = re.compile(r"(?:\b[A-Za-z]|\be\.g|\bi\.e|\bet al|\bvs|\bc|\bca|\bapprox)$")

FRAGMENT_CHECKS = (
    ("conjunction starts a sentence after a period", re.compile(r"[.!?]\s+(?:and|but|or|so|nor)\b")),
    ("doubled space", re.compile(r" {2,}")),
    ("doubled period / period-comma", re.compile(r"\.\s*\.|\.,|,\.|[,;:]\s*[.!?]")),
    ("dangling dash at sentence end", re.compile(r"[—–]\s*[.!?]?$")),
)


def displayed_strings(cards: dict):
    for cid, card in cards.items():
        if card.get("source_note"):
            yield f"{cid}/source_note", str(card["source_note"])
        for key in ("talk_about", "push_further"):
            for i, line in enumerate(card.get(key) or []):
                yield f"{cid}/{key}[{i}]", str(line)
        for level, pack in (card.get("levels") or {}).items():
            for key in ("teach", "talk_about", "push_further"):
                for i, line in enumerate(pack.get(key) or []):
                    yield f"{cid}/{level}/{key}[{i}]", str(line)
            for q in pack.get("questions") or []:
                qid = q.get("id")
                for field in ("title", "stem", "why"):
                    if q.get(field):
                        yield f"{cid}/{level}/{qid}.{field}", str(q[field])
                for i, ch in enumerate(q.get("choices") or []):
                    yield f"{cid}/{level}/{qid}.choice[{i}]", str(ch)


def lowercase_after_period(text: str) -> list[str]:
    hits = []
    for m in re.finditer(r"\.\s+(?=[a-z])", text):
        before = text[: m.start()]
        if _ABBREV_BEFORE.search(before):
            continue
        hits.append(text[max(0, m.start() - 40) : m.end() + 30])
    return hits


def fragment_problems(text: str) -> list[str]:
    out = [f"lowercase after period: …{h}…" for h in lowercase_after_period(text)]
    for label, pat in FRAGMENT_CHECKS:
        m = pat.search(text)
        if m:
            out.append(f"{label}: …{text[max(0, m.start() - 40) : m.end() + 30]}…")
    return out


def load_cards_from_data_js() -> dict:
    js = STUDY_DATA_JS.read_text(encoding="utf-8")
    m = re.search(r"window\.FP_STUDY_CARDS = (\{.*?\});\n", js, re.S)
    assert m, "FP_STUDY_CARDS missing from study-cards-data.js"
    return json.loads(m.group(1))


class StudyTextFragmentTests(unittest.TestCase):
    def _assert_clean(self, cards: dict, where: str) -> None:
        problems = []
        for key, text in displayed_strings(cards):
            for p in fragment_problems(text):
                problems.append(f"{key}: {p}")
        self.assertEqual(problems, [], f"half-sentence text in {where}:\n" + "\n".join(problems))

    def test_shipped_json_has_no_fragments(self):
        self._assert_clean(json.loads(STUDY_JSON.read_text(encoding="utf-8")), "study-cards.json")

    def test_shipped_data_js_has_no_fragments(self):
        self._assert_clean(load_cards_from_data_js(), "study-cards-data.js")

    def test_scanner_catches_known_fragment_shapes(self):
        bad = (
            "Major health threats in many wild populations. and do not lock one infection rate.",
            "Big drops since about 1970., and not every kind dropped the same way.",
            "Adult males may clash with neighbours. here.",
            "Two  spaces.",
            "Ends twice..",
        )
        for text in bad:
            self.assertTrue(fragment_problems(text), text)
        ok = (
            "Lions: P. l. leo and P. l. melanochaita.",
            "Three subspecies: F. a. arctica, grabae, and naumanni.",
            "Named proteins (e.g. cystatins) exist.",
        )
        for text in ok:
            self.assertEqual(fragment_problems(text), [], text)

    def test_stripper_drops_whole_editorial_sentences(self):
        self.assertEqual(
            strip_editorial_soft_display(
                "Wikipedia lists two threats. We keep the medical detail soft and do not lock one rate."
            ),
            "Wikipedia lists two threats.",
        )
        self.assertEqual(
            strip_editorial_soft_display(
                "Many can drop a limb to escape — we keep that trick soft."
            ),
            "Many can drop a limb to escape.",
        )
        self.assertEqual(
            strip_editorial_soft_display(
                "Litter sizes vary; we keep the count soft rather than locking one number."
            ),
            "Litter sizes vary.",
        )
        self.assertEqual(
            strip_editorial_soft_display(
                "They hide well. We keep that split soft — not “just small ones.”"
            ),
            "They hide well.",
        )
        self.assertEqual(
            strip_editorial_soft_display(
                "Fish stay put. Soft physiology: spines help keep that row in place."
            ),
            "Fish stay put. Spines help keep that row in place.",
        )

    def test_stingray_kind_count_matches_explanation(self):
        cards = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        q = next(
            q
            for q in cards["stingray"]["levels"]["easy"]["questions"]
            if q["id"] == "many-kinds-soft"
        )
        right = q["choices"][ord(q["correct"]) - ord("A")]
        self.assertIn("About 220", right)
        self.assertNotIn("two hundred", right)
        self.assertIn("about 220", q["why"])

    def test_scan_covers_stems_and_every_choice_including_distractors(self):
        cards = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        keys = {k for k, _ in displayed_strings(cards)}
        n_q = n_ch = 0
        for cid, card in cards.items():
            for level, pack in card["levels"].items():
                for q in pack["questions"]:
                    n_q += 1
                    self.assertIn(f"{cid}/{level}/{q['id']}.stem", keys)
                    for i in range(len(q["choices"])):
                        n_ch += 1
                        self.assertIn(f"{cid}/{level}/{q['id']}.choice[{i}]", keys)
        self.assertGreater(n_q, 1200)
        self.assertGreater(n_ch, n_q * 2)
        fake = {"x": {"levels": {"easy": {"questions": [{
            "id": "q", "stem": "Which one? and why", "why": "Fine.",
            "choices": ["Right answer", "Wrong distractor. and more", "Other"]}]}}}}
        flagged = [k for k, t in displayed_strings(fake) if fragment_problems(t)]
        self.assertIn("x/easy/q.choice[1]", flagged)
        self.assertIn("x/easy/q.stem", flagged)

    def test_honesty_hedges_survive_the_stripper(self):
        """Never lose a hedge: uncertain numbers keep their 'debated/varies' words."""
        cards = json.loads(STUDY_JSON.read_text(encoding="utf-8"))

        def why(cid, level, qid):
            return next(q for q in cards[cid]["levels"][level]["questions"] if q["id"] == qid)["why"]

        self.assertIn("figures are debated", why("nile-hippo", "zoologist", "whale-clade"))
        self.assertIn("estimates vary", why("two-toed-sloth", "zoologist", "species-split-soft"))
        self.assertIn("as a snapshot", why("american-bison", "hard", "nt-recovery-soft"))
        self.assertIn("Exact percents vary", why("shark", "zoologist", "ocean-declines-soft"))
        self.assertIn("exact totals vary", why("crab", "hard", "brachyura-soft"))
        self.assertIn("Not every kind", why("starfish", "easy", "regrow-soft"))
        self.assertIn("Litter sizes vary", why("stingray", "easy", "live-young-soft"))
        self.assertIn("Exact totals shift", why("stingray", "easy", "many-kinds-soft"))


if __name__ == "__main__":
    unittest.main()
