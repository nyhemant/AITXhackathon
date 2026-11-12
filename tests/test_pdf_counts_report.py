"""Weekly and per-page totals from the PDF counts directory."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from pdf_counts_report import format_report, load_days, week_heading  # noqa: E402


class PdfCountsReportTests(unittest.TestCase):
    def test_week_heading_is_monday_to_sunday(self):
        self.assertEqual(week_heading("2026-11-12"), "2026-W46 (2026-11-09 to 2026-11-15)")
        self.assertIsNone(week_heading("not-a-date"))

    def test_weekly_totals_and_per_page_totals(self):
        days = {
            "2026-11-12": {
                "letter/scavenger-hunt": {
                    "site": 2,
                    "search": 1,
                    "other": 0,
                    "pages": {"/field-pack/amnh/": 2},
                },
                "a4/park-scavenger-hunt": {
                    "site": 1,
                    "pages": {"/field-pack/redwood/": 1, "other-page": 0},
                },
            },
            "2026-11-02": {
                "letter/scavenger-hunt": {"other": 4},
            },
        }
        text = format_report(days)
        self.assertIn("Weekly totals", text)
        self.assertIn("2026-W45 (2026-11-02 to 2026-11-08)", text)
        self.assertIn("letter/scavenger-hunt  site=0 search=0 other=4 total=4", text)
        self.assertIn("2026-W46 (2026-11-09 to 2026-11-15)", text)
        self.assertIn("letter/scavenger-hunt  site=2 search=1 other=0 total=3", text)
        self.assertIn("a4/park-scavenger-hunt  site=1 search=0 other=0 total=1", text)
        self.assertIn("ALL  site=3 search=1 other=0 total=4", text)
        self.assertIn("Per-page totals", text)
        self.assertIn("/field-pack/amnh/  2", text)
        self.assertIn("/field-pack/redwood/  1", text)
        self.assertIn("ALL  3", text)
        self.assertNotIn("other-page", text)
        weekly, _, pages = text.partition("Per-page totals")
        self.assertNotIn("/field-pack/", weekly)

    def test_cli_reads_counts_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = {
                "2026-11-12": {
                    "letter/scavenger-hunt": {
                        "site": 1,
                        "pages": {"/field-pack/lincoln-park-zoo/": 1},
                    }
                }
            }
            path = Path(tmp) / "pdf-counts-2026-11.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            (Path(tmp) / "notes.txt").write_text("ignore", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "pdf_counts_report.py"), "--dir", tmp],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn(f"Counts directory: {tmp}", proc.stdout)
            self.assertIn("/field-pack/lincoln-park-zoo/  1", proc.stdout)
            self.assertIn("letter/scavenger-hunt  site=1 search=0 other=0 total=1", proc.stdout)
            loaded = load_days(Path(tmp))
            self.assertEqual(loaded["2026-11-12"]["letter/scavenger-hunt"]["site"], 1)


if __name__ == "__main__":
    unittest.main()
