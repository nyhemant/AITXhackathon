"""Printed study-card titles use the catalog animal name, not a venue chip.

Venue ``itemDisplayNames`` (for example "Panda Ridge red panda") stay on
on-venue chips. The study-card heading is the catalog name ("Red panda").
A venue subtitle adds a zone only when that zone is a shared display prefix.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
CATALOG = REPO / "static" / "field-pack" / "js" / "catalog.js"
PRINT_KIT = REPO / "static" / "field-pack" / "js" / "print-kit.js"

NODE = r"""
const fs = require("fs");
const vm = require("vm");
const window = {};
vm.runInNewContext(fs.readFileSync(process.argv[1], "utf8"), { window, console });
vm.runInNewContext(fs.readFileSync(process.argv[2], "utf8"), { window, console });
const FP = window.FPPrint;
const venues = window.FIELD_PACK_VENUES || {};
const catalog = window.FIELD_PACK_CATALOG || {};
const deck = { level: "easy", level_label: "Junior Ranger", questions: [] };

function decode(s) {
  return String(s)
    .replaceAll("&amp;", "&")
    .replaceAll("&lt;", "<")
    .replaceAll("&gt;", ">")
    .replaceAll("&quot;", '"')
    .replaceAll("&#39;", "'");
}
function headerTitle(html) {
  const m = html.match(/<header class="ps-head">\s*<h3>([^<]*)<\/h3>/);
  return m ? decode(m[1]).trim() : "";
}
function venueLine(html) {
  const m = html.match(/<p class="ps-line">([^<]*)<\/p>/);
  return m ? decode(m[1]) : "";
}
function banner(html) {
  const m = html.match(/<div class="ps-banner"><h2>KIDZOOKIT<\/h2>\s*<p>([^<]*)<\/p>/);
  return m ? decode(m[1]) : "";
}

const rows = [];
let venueCount = 0;
for (const [venueId, venue] of Object.entries(venues)) {
  const names = venue && venue.itemDisplayNames;
  if (!names) continue;
  venueCount += 1;
  for (const itemId of Object.keys(names)) {
    const base = catalog[itemId];
    if (!base) continue;
    const chip = FP.getItem(itemId, venue);
    const html = FP.buildStudyCardHtml(chip, venue, deck);
    const qa = FP.buildQaCardHtml(chip, venue, {});
    rows.push({
      venueId,
      itemId,
      catalogName: base.name,
      displayName: names[itemId],
      chipName: chip && chip.name,
      title: headerTitle(html),
      banner: banner(html),
      venueLine: venueLine(html),
      qaTitle: headerTitle(qa),
    });
  }
}
const solo = FP.buildStudyCardHtml(catalog["red-panda"], null, deck);
process.stdout.write(JSON.stringify({
  venueCount,
  rows,
  standaloneTitle: headerTitle(solo),
  standaloneLine: venueLine(solo),
}));
"""


class StudyCardPrintTitleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        node = shutil.which("node")
        if not node:
            raise unittest.SkipTest("node is required to render print-kit titles")
        proc = subprocess.run(
            [node, "-e", NODE, str(CATALOG), str(PRINT_KIT)],
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if proc.returncode != 0:
            raise AssertionError(proc.stderr or proc.stdout)
        cls.data = json.loads(proc.stdout)
        cls.by_key = {(row["venueId"], row["itemId"]): row for row in cls.data["rows"]}

    def _row(self, venue_id: str, item_id: str) -> dict:
        row = self.by_key.get((venue_id, item_id))
        self.assertIsNotNone(row, f"missing {venue_id} {item_id}")
        return row

    def test_every_venue_display_name_prints_catalog_title(self):
        rows = self.data["rows"]
        self.assertGreaterEqual(self.data["venueCount"], 190)
        self.assertGreaterEqual(len(rows), 1400)
        bad = []
        for row in rows:
            title = row["title"]
            catalog_name = row["catalogName"]
            display = row["displayName"]
            if not title.endswith(catalog_name):
                bad.append(f"{row['venueId']} {row['itemId']} title {title!r} != {catalog_name!r}")
            elif display.casefold() != catalog_name.casefold() and display in title:
                bad.append(f"{row['venueId']} {row['itemId']} title still contains {display!r}")
            elif not row["banner"].startswith(catalog_name + " ·"):
                bad.append(f"{row['venueId']} {row['itemId']} banner {row['banner']!r}")
            elif row["qaTitle"] and not row["qaTitle"].endswith(catalog_name):
                bad.append(f"{row['venueId']} {row['itemId']} qa {row['qaTitle']!r}")
            elif row["chipName"] != display:
                bad.append(
                    f"{row['venueId']} {row['itemId']} chip {row['chipName']!r} != {display!r}"
                )
        self.assertEqual(bad, [])

    def test_red_panda_from_san_diego_zoo_uses_plain_name_and_zone(self):
        row = self._row("san-diego-zoo", "red-panda")
        self.assertEqual(row["catalogName"], "Red panda")
        self.assertTrue(row["title"].endswith("Red panda"))
        self.assertNotIn("Panda Ridge", row["title"])
        self.assertEqual(row["venueLine"], "At San Diego Zoo: Panda Ridge")
        self.assertEqual(row["chipName"], "Panda Ridge red panda")
        panda = self._row("san-diego-zoo", "giant-panda")
        self.assertTrue(panda["title"].endswith("Giant panda"))
        self.assertEqual(panda["venueLine"], "At San Diego Zoo: Panda Ridge")

    def test_zone_omitted_when_prefix_is_not_a_shared_place(self):
        lion = self._row("san-diego-zoo", "african-lion")
        self.assertEqual(lion["venueLine"], "At San Diego Zoo")
        self.assertNotIn("San Diego lion", lion["title"])
        koala = self._row("san-diego-zoo", "koala")
        self.assertEqual(koala["venueLine"], "At San Diego Zoo")
        self.assertNotIn("Outback", koala["venueLine"])
        zebra = self._row("san-diego-safari-park", "zebra")
        self.assertEqual(zebra["venueLine"], "At San Diego Zoo Safari Park")
        self.assertNotIn("Grevy", zebra["venueLine"])

    def test_card_without_venue_has_no_at_line(self):
        self.assertTrue(self.data["standaloneTitle"].endswith("Red panda"))
        self.assertEqual(self.data["standaloneLine"], "")
