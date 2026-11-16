"""Every indexable, non-frozen place page shows at least 5 place-specific finds in its hunt list.

Generic hall/activity labels ("Free explore", "Hands-on exhibits", "Dinosaur hall", "Planetarium",
"Outdoor Area", ...) do not count. Reused template names ("Imaginarium", "Creative Makery", ...)
count only when the venue item behind them has a source URL. Rules live in
scripts/lint_place_finds_v1.py so the build and this test use one definition.
"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import lint_place_finds_v1 as L  # noqa: E402

FP = ROOT / "static/field-pack"
# Pages fixed in the finds-floor follow-up: every hunt find there must carry a source URL.
FLOOR_FIXED = (
    "dallas-arboretum denver-museum-nature-science museum-of-science-boston smithsonian-natural-history "
    "thinkery union-station-kc-science childrens-museum-perot carnegie-natural-history nhm-london "
    "arizona-science-center montreal-biodome oregon-museum-science-industry orlando-science-center "
    "frost-science perot-museum please-touch-museum kennedy-space-center"
).split()


class PlaceFindsFloor(unittest.TestCase):
    def test_every_indexed_place_page_has_five_specific_finds(self):
        counts = L.counts(str(FP))
        self.assertGreater(len(counts), 150)
        thin = {s: v for s, v in counts.items() if len(v) < L.FLOOR}
        self.assertEqual(thin, {}, f"under {L.FLOOR} place-specific finds: {thin}")

    def test_generic_labels_do_not_count(self):
        for lab in ("Free explore", "Hands-on exhibits", "Hands-on lab", "Dinosaur hall", "Planetarium",
                    "Outdoor Area", "Animal / mammal hall", "Planet / space hall", "Life sciences", "Make", "Space"):
            self.assertTrue(L.ALWAYS_GENERIC.match(lab), lab)
        for lab in ("Hall of Fossils – Deep Time", "Morrison Planetarium", "Kinetic Climber", "Hope the blue whale"):
            self.assertFalse(L.ALWAYS_GENERIC.match(lab), lab)

    def test_template_names_need_a_source(self):
        row = '<ol class="seo-hunt-list"><li><span>Imaginarium — x · Halls</span></li></ol>'
        self.assertEqual(L.specific(row, {}), [])
        self.assertEqual(L.specific(row, {"Imaginarium": {"presence_url": "https://example.org/"}}), ["Imaginarium"])

    def test_fixed_pages_hunt_finds_are_sourced(self):
        for s in FLOOR_FIXED:
            d = json.loads((FP / f"data/venues/{s}.json").read_text(encoding="utf-8"))
            by = {i["id"]: i for i in d["items"]}
            ids = d.get("classic_find_ids") or []
            self.assertGreaterEqual(len(ids), 6, s)
            for iid in ids:
                self.assertIn(iid, by, (s, iid))
                url = str(by[iid].get("presence_url") or "")
                if s in ("oregon-museum-science-industry", "frost-science", "perot-museum", "cal-academy") and not url:
                    # catalog animals / halls verified in #447 without a per-item URL
                    self.assertIn(by[iid].get("presence"), ("verified", "high"), (s, iid))
                    continue
                self.assertTrue(url.startswith("http"), (s, iid))

    def test_unsupported_template_stops_marked_absent(self):
        for s, ids in {"thinkery": ["cm_makery", "cm_imaginarium", "cm_woven"],
                       "smithsonian-natural-history": ["cm_imaginarium"],
                       "union-station-kc-science": ["cm_imaginarium", "sci_shuttle"]}.items():
            d = json.loads((FP / f"data/venues/{s}.json").read_text(encoding="utf-8"))
            by = {i["id"]: i for i in d["items"]}
            for iid in ids:
                self.assertEqual(by[iid]["presence"], "absent", (s, iid))
            html = (FP / f"{s}/index.html").read_text(encoding="utf-8")
            hunt = " ".join(L.finds(html))
            self.assertNotIn("Imaginarium", hunt, s)
            self.assertNotIn("Creative Makery", hunt, s)


if __name__ == "__main__":
    unittest.main()
