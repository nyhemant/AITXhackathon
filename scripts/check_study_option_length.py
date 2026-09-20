#!/usr/bin/env python3
"""Flag study-card questions whose correct option is much longer than peers.

Correct option word-count must not exceed 1.5× the median option length in
that question. Scans all cards; exits 1 only for ENFORCED card ids
(currently whale-shark). Expand OPTION_LENGTH_ENFORCED_CARD_IDS as more
cards are rewritten.

Usage (repo root):
  python3 scripts/check_study_option_length.py
  python3 scripts/check_study_option_length.py --all-fail  # fail on any card
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from study_cards import (  # noqa: E402
    OPTION_LENGTH_ENFORCED_CARD_IDS,
    OPTION_LENGTH_RATIO,
    option_length_failures,
    option_length_offenders,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--all-fail",
        action="store_true",
        help="Exit 1 on any offender (full-catalog enforcement)",
    )
    ap.add_argument(
        "--list-all",
        action="store_true",
        help="Print every offender even when exit is gated",
    )
    args = ap.parse_args()

    all_rows = option_length_offenders(ratio=OPTION_LENGTH_RATIO)
    if args.all_fail:
        fail_rows = all_rows
        gate = "all cards"
    else:
        fail_rows = option_length_failures(ratio=OPTION_LENGTH_RATIO)
        gate = (
            "enforced cards only: "
            + ", ".join(sorted(OPTION_LENGTH_ENFORCED_CARD_IDS))
        )

    if args.list_all or not fail_rows:
        print(
            f"option-length scan: {len(all_rows)} offender(s) across all cards "
            f"(ratio > {OPTION_LENGTH_RATIO}× median)"
        )
        for row in all_rows:
            print(
                f"  {row['card_id']}/{row['level']}/{row['question_id']} "
                f"correct={row['correct_words']} med={row['median_words']} "
                f"ratio={row['ratio']} counts={row['counts']}"
            )
    else:
        print(
            f"option-length scan: {len(all_rows)} offender(s) total; "
            f"failing {len(fail_rows)} on {gate}"
        )
        for row in fail_rows:
            print(
                f"  FAIL {row['card_id']}/{row['level']}/{row['question_id']} "
                f"correct={row['correct_words']} med={row['median_words']} "
                f"ratio={row['ratio']} counts={row['counts']}"
            )

    if fail_rows:
        print(
            f"FAIL: {len(fail_rows)} question(s) exceed "
            f"{OPTION_LENGTH_RATIO}× median ({gate})",
            file=sys.stderr,
        )
        return 1
    print(f"OK: no failures under gate ({gate})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
