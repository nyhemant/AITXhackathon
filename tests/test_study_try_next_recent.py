"""Try next recent-path skip: catalog + pick-next helper."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from generate_bdo_seo import STUDY_CARD_JS_VER, STUDY_CARDS_DATA_JS_VER  # noqa: E402
from study_cards import (  # noqa: E402
    STUDY_CARDS,
    STUDY_NEIGHBORS,
    STUDY_TRAFFIC_ORDER,
    study_card_ids,
    study_try_next_catalog,
    study_try_next_html,
    study_try_next_ids,
)

FP = REPO / "static" / "field-pack"
STUDY_JS = FP / "js" / "study-card.js"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
SEO = REPO / "scripts" / "generate_bdo_seo.py"

RUNTIME = r"""
const fs = require("fs");
const src = fs.readFileSync(process.argv[2], "utf8");
const data = fs.readFileSync(process.argv[3], "utf8");
const prelude = src.slice(0, src.indexOf("(() => {"));
if (!prelude.includes("function FPStudyPickTryNextIds")) {
  console.error("missing FPStudyPickTryNextIds");
  process.exit(1);
}
eval(prelude);
const marker = "window.FP_STUDY_TRY_NEXT = ";
const start = data.indexOf(marker);
if (start < 0) {
  console.error("missing FP_STUDY_TRY_NEXT");
  process.exit(1);
}
let raw = data.slice(start + marker.length).trim();
if (raw.endsWith(";")) raw = raw.slice(0, -1);
const catalog = JSON.parse(raw);

function fail(msg) { console.error(msg); process.exit(1); }
function eq(got, want, label) {
  if (JSON.stringify(got) !== JSON.stringify(want)) {
    fail(label + " got " + JSON.stringify(got) + " want " + JSON.stringify(want));
  }
}

eq(FPStudyPickTryNextIds("african-lion", ["african-lion"], catalog, 3),
  ["reticulated-giraffe", "african-elephant", "african-penguin"],
  "lion first visit");
eq(FPStudyPickTryNextIds("reticulated-giraffe", ["african-lion", "reticulated-giraffe"], catalog, 3),
  ["african-elephant", "african-penguin", "caribbean-flamingo"],
  "giraffe after lion skips lion");
const after = FPStudyPickTryNextIds(
  "reticulated-giraffe",
  ["african-lion", "reticulated-giraffe"],
  catalog,
  3
);
if (after.includes("african-lion")) fail("recent lion must not be recommended");
if (after.includes("reticulated-giraffe")) fail("current must never be recommended");
if (after[0] !== "african-elephant") fail("prefer remaining neighbor when not recent");
if (after.length !== 3) fail("must fill to 3");

const onlyCurrent = FPStudyPickTryNextIds("cheetah", ["cheetah"], catalog, 3);
if (onlyCurrent.includes("cheetah")) fail("cheetah must not recommend itself");
if (onlyCurrent.length !== 3) fail("cheetah fills to 3");
if (onlyCurrent[0] !== "african-lion") fail("cheetah prefers lion neighbor");

const almostAll = Object.keys(catalog.titles).filter((id) => id !== "shark");
const filled = FPStudyPickTryNextIds("shark", almostAll, catalog, 3);
if (filled.includes("shark")) fail("fill pass still excludes current");
if (filled.length !== 3) fail("fill with older decks to keep 3 thumbs");

const remembered = FPStudyRememberRecent(
  "reticulated-giraffe",
  ["african-lion"],
  "african-elephant",
  8
);
eq(remembered, ["african-lion", "reticulated-giraffe"], "session wins over referrer hint");
const hinted = FPStudyRememberRecent("reticulated-giraffe", [], "african-lion", 8);
eq(hinted, ["african-lion", "reticulated-giraffe"], "referrer hint when session empty");
const capped = FPStudyRememberRecent("shark", ["a","b","c","d","e","f","g","h"], "", 8);
if (capped.length !== 8) fail("recent path max 8");
if (capped[capped.length - 1] !== "shark") fail("current moves to end");
if (capped.includes("a")) fail("oldest drops when over cap");

console.log("ok");
"""


class StudyTryNextRecentTests(unittest.TestCase):
    def test_catalog_exports_neighbors_traffic_titles(self):
        catalog = study_try_next_catalog()
        self.assertEqual(set(catalog["titles"]), set(STUDY_CARDS))
        self.assertEqual(tuple(catalog["traffic"]), STUDY_TRAFFIC_ORDER)
        self.assertEqual(catalog["neighbors"]["african-lion"], ["reticulated-giraffe", "african-elephant"])
        self.assertEqual(catalog["neighbors"]["warthog"], ["zebra", "ostrich"])
        self.assertEqual(catalog["neighbors"]["shark"], ["african-penguin", "caribbean-flamingo"])
        self.assertEqual(catalog["neighbors"]["ostrich"], ["caribbean-flamingo", "african-penguin"])
        self.assertEqual(catalog["titles"]["african-lion"], "African lion")
        self.assertEqual(catalog["titles"]["galapagos-tortoise"], "Galápagos tortoise")

        data = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("window.FP_STUDY_TRY_NEXT = ", data)
        raw = data.split("window.FP_STUDY_TRY_NEXT = ", 1)[1].strip()
        if raw.endswith(";"):
            raw = raw[:-1]
        shipped = json.loads(raw)
        self.assertEqual(shipped, catalog)

    def test_python_pick_excludes_recent_prefers_neighbor_fills_three(self):
        self.assertEqual(
            study_try_next_ids("african-lion"),
            ["reticulated-giraffe", "african-elephant", "african-penguin"],
        )
        self.assertEqual(
            study_try_next_ids("african-lion", exclude=["african-lion"]),
            ["reticulated-giraffe", "african-elephant", "african-penguin"],
        )
        after_lion = study_try_next_ids(
            "reticulated-giraffe",
            exclude=["african-lion", "reticulated-giraffe"],
        )
        self.assertEqual(
            after_lion,
            ["african-elephant", "african-penguin", "caribbean-flamingo"],
        )
        self.assertNotIn("african-lion", after_lion)
        self.assertNotIn("reticulated-giraffe", after_lion)
        self.assertEqual(after_lion[0], "african-elephant")
        self.assertEqual(len(after_lion), 3)

        cheetah = study_try_next_ids("cheetah", exclude=["cheetah"])
        self.assertEqual(cheetah[0], "african-lion")
        self.assertEqual(len(cheetah), 3)
        self.assertNotIn("cheetah", cheetah)

        almost_all = [cid for cid in study_card_ids() if cid != "shark"]
        filled = study_try_next_ids("shark", exclude=almost_all)
        self.assertEqual(len(filled), 3)
        self.assertNotIn("shark", filled)

        for cid in study_card_ids():
            nxt = study_try_next_ids(cid, exclude=["african-lion", cid])
            with self.subTest(card=cid):
                self.assertEqual(len(nxt), 3)
                self.assertNotIn(cid, nxt)
                self.assertTrue(set(nxt).issubset(STUDY_CARDS))

    def test_static_html_fallback_stays_baked(self):
        block = study_try_next_html("african-lion")
        self.assertIn('href="/field-pack/cards/reticulated-giraffe/"', block)
        self.assertIn('href="/field-pack/cards/african-elephant/"', block)
        self.assertIn("/field-pack/photos/reticulated-giraffe.jpg?v=img2", block)
        lion = (FP / "cards" / "african-lion" / "index.html").read_text(encoding="utf-8")
        self.assertIn('class="card-try-next-grid"', lion)
        self.assertIn("Try next: Reticulated giraffe", lion)
        self.assertIn(f"study-card.js?v={STUDY_CARD_JS_VER}", lion)
        self.assertIn(f"study-cards-data.js?v={STUDY_CARDS_DATA_JS_VER}", lion)

    def test_study_card_js_rewrites_try_next_from_session(self):
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("function FPStudyPickTryNextIds(", js)
        self.assertIn("function FPStudyRememberRecent(", js)
        self.assertIn('FP_STUDY_RECENT_KEY = "fp-study-recent"', js)
        self.assertIn("function paintTryNext(", js)
        self.assertIn("paintTryNext(id)", js)
        self.assertIn("card-try-next-grid", js)
        self.assertIn("sessionStorage", js)
        self.assertIn("document.referrer", js)
        seo = SEO.read_text(encoding="utf-8")
        self.assertIn(f'STUDY_CARD_JS_VER = "{STUDY_CARD_JS_VER}"', seo)
        self.assertIn(f'STUDY_CARDS_DATA_JS_VER = "{STUDY_CARDS_DATA_JS_VER}"', seo)
        self.assertEqual(STUDY_CARD_JS_VER, "10")
        self.assertEqual(STUDY_CARDS_DATA_JS_VER, "6")

    def test_js_helper_runtime_matches_python(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node is required for the try-next helper harness")
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
            fh.write(RUNTIME)
            harness = fh.name
        try:
            proc = subprocess.run(
                [node, harness, str(STUDY_JS), str(STUDY_DATA_JS)],
                check=False,
                capture_output=True,
                text=True,
                timeout=20,
            )
        finally:
            Path(harness).unlink(missing_ok=True)
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        self.assertIn("ok", proc.stdout)

        catalog = study_try_next_catalog()
        self.assertEqual(
            study_try_next_ids(
                "reticulated-giraffe",
                exclude=["african-lion", "reticulated-giraffe"],
            ),
            ["african-elephant", "african-penguin", "caribbean-flamingo"],
        )
        self.assertIn("warthog", catalog["neighbors"])
        self.assertIn("shark", catalog["neighbors"])
        self.assertIn("ostrich", catalog["neighbors"])
        self.assertIn("asian-small-clawed-otter", catalog["neighbors"])
        self.assertIn("two-toed-sloth", catalog["neighbors"])
        self.assertIn("freshwater-fish", catalog["neighbors"])
        self.assertIn("polar-bear", catalog["neighbors"])
        self.assertIn("sea-otter", catalog["neighbors"])
        self.assertEqual(len(STUDY_NEIGHBORS["warthog"]), 2)
        self.assertEqual(
            list(STUDY_NEIGHBORS["asian-small-clawed-otter"]),
            ["shark", "red-panda"],
        )
        self.assertEqual(
            list(STUDY_NEIGHBORS["two-toed-sloth"]),
            ["orangutan", "koala"],
        )
        self.assertEqual(
            list(STUDY_NEIGHBORS["freshwater-fish"]),
            ["shark", "asian-small-clawed-otter"],
        )
        self.assertEqual(
            list(STUDY_NEIGHBORS["polar-bear"]),
            ["african-penguin", "asian-small-clawed-otter"],
        )
        self.assertEqual(
            list(STUDY_NEIGHBORS["sea-otter"]),
            ["asian-small-clawed-otter", "shark"],
        )
        self.assertIn("american-alligator", catalog["neighbors"])
        self.assertEqual(
            list(STUDY_NEIGHBORS["american-alligator"]),
            ["freshwater-fish", "galapagos-tortoise"],
        )
        self.assertIn("american-bison", catalog["neighbors"])
        self.assertEqual(
            list(STUDY_NEIGHBORS["american-bison"]),
            ["zebra", "warthog"],
        )
        self.assertIn("elk", catalog["neighbors"])
        self.assertEqual(
            list(STUDY_NEIGHBORS["elk"]),
            ["american-bison", "zebra"],
        )


if __name__ == "__main__":
    unittest.main()
