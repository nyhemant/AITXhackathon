"""Kit-tier badge + freshness mailto — two labels only, no invented dates."""

from pathlib import Path
import json
import sys
import unittest
from urllib.parse import unquote

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from field_pack_kit_tier import (  # noqa: E402
    CHECKED_DATE_FIELD,
    KIT_LABEL_STARTER,
    VERIFIED_CONFIDENCE,
    checked_month_label,
    freshness_html,
    freshness_mailto,
    kit_tier_label,
    print_status_line,
    status_chip_html,
)

FP = REPO / "static" / "field-pack"
VENUES = FP / "data" / "venues"


def _visible(html: str) -> str:
    return html.split('id="venue-data"', 1)[0]


def _load_venue(slug: str) -> dict:
    return json.loads((VENUES / f"{slug}.json").read_text(encoding="utf-8"))


class KitTierHelperTests(unittest.TestCase):
    def test_month_from_existing_iso_date(self):
        self.assertEqual(checked_month_label("2026-08-08"), "Aug 2026")
        self.assertEqual(checked_month_label("2026-08"), "Aug 2026")

    def test_unreadable_date_is_empty(self):
        self.assertEqual(checked_month_label(""), "")
        self.assertEqual(checked_month_label("checked recently"), "")
        self.assertEqual(checked_month_label("2026-13-01"), "")

    def test_verified_needs_audited_and_real_date(self):
        self.assertEqual(
            kit_tier_label(
                {
                    "list_confidence": "audited",
                    "last_presence_audit": "2026-08-08",
                }
            ),
            "Verified kit · checked Aug 2026",
        )

    def test_audited_without_date_is_starter(self):
        self.assertEqual(
            kit_tier_label({"list_confidence": "audited"}),
            KIT_LABEL_STARTER,
        )

    def test_status_verified_alone_is_not_a_depth_signal(self):
        self.assertEqual(
            kit_tier_label(
                {
                    "status": "verified",
                    "content_mode": "curated",
                    "last_verified": "2026-08-16",
                    "list_confidence": "partial",
                }
            ),
            KIT_LABEL_STARTER,
        )

    def test_print_line_matches_chip(self):
        v = {
            "list_confidence": "audited",
            "last_presence_audit": "2026-08-09",
        }
        self.assertEqual(print_status_line(v), kit_tier_label(v))
        self.assertIn("Verified kit · checked Aug 2026", status_chip_html(v))
        self.assertIn("Starter list", status_chip_html({"list_confidence": "template"}))

    def test_freshness_subject_includes_slug(self):
        accurate = freshness_mailto("dallas-zoo", "accurate")
        changed = freshness_mailto("dallas-zoo", "changed")
        self.assertTrue(accurate.startswith("mailto:hello@1less.app?subject="))
        self.assertIn("dallas-zoo", unquote(accurate))
        self.assertIn("accurate", unquote(accurate))
        self.assertIn("dallas-zoo", unquote(changed))
        self.assertIn("something changed", unquote(changed))
        html = freshness_html("houston-zoo")
        self.assertIn("Was this list accurate?", html)
        self.assertIn("houston-zoo", unquote(html))


class KitTierPageTests(unittest.TestCase):
    def test_dallas_and_san_diego_use_source_audit_date(self):
        for slug in ("dallas-zoo", "san-diego-zoo"):
            data = _load_venue(slug)
            self.assertEqual(data.get("list_confidence"), VERIFIED_CONFIDENCE)
            self.assertTrue(data.get(CHECKED_DATE_FIELD))
            expected = kit_tier_label(data)
            self.assertTrue(expected.startswith("Verified kit · checked "))
            html = (FP / slug / "index.html").read_text(encoding="utf-8")
            visible = _visible(html)
            self.assertIn(expected, visible)
            self.assertNotIn("Verified with venue website", visible)
            self.assertIn("Was this list accurate?", visible)
            self.assertIn(f"Field Trip Kit · {slug} · accurate", unquote(visible))
            self.assertIn(f"Field Trip Kit · {slug} · something changed", unquote(visible))
            self.assertIn(expected, html)  # print header uses the same label
            footer = html.split('class="ms-footer"', 1)[1].split("</p>", 1)[0]
            self.assertIn("Was this list accurate?", footer)
            self.assertIn(f"Field Trip Kit · {slug} · accurate", unquote(footer))

    def test_starter_venue_says_starter_list(self):
        data = _load_venue("houston-zoo")
        self.assertNotEqual(data.get("list_confidence"), VERIFIED_CONFIDENCE)
        html = (FP / "houston-zoo" / "index.html").read_text(encoding="utf-8")
        visible = _visible(html)
        self.assertIn("Starter list", visible)
        self.assertNotIn("Verified kit", visible)
        self.assertIn("Was this list accurate?", visible)
        self.assertIn("houston-zoo", unquote(visible))

    def test_label_counts_match_source_json(self):
        verified = 0
        starter = 0
        for path in sorted(VENUES.glob("*.json")):
            label = kit_tier_label(json.loads(path.read_text(encoding="utf-8")))
            if label.startswith("Verified kit"):
                verified += 1
            else:
                starter += 1
        self.assertEqual(verified + starter, 218)
        self.assertEqual(verified, 59)
        self.assertEqual(starter, 159)
        self.assertNotIn("Local shortlist", (FP / "dallas-zoo" / "index.html").read_text())


if __name__ == "__main__":
    unittest.main()
