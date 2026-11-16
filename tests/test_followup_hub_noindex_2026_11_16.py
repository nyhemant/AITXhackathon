"""Follow-up 2026-11-16: noindex places stay live but are not listed on hubs, related links or the hub map."""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_bdo_seo as gen  # noqa: E402

FP = ROOT / "static" / "field-pack"
HUBS = [FP / "index.html"] + [FP / h / "index.html" for h in ("zoos", "aquariums", "museums", "national-parks")]


class HubNoindex(unittest.TestCase):
    def test_hubs_do_not_link_noindex(self):
        for f in HUBS:
            page = f.read_text(encoding="utf-8")
            for s in gen.NOINDEX_PLACE_SLUGS:
                self.assertNotIn(f"/field-pack/{s}/", page, f"{f.parent.name} lists {s}")

    def test_no_related_link_to_noindex(self):
        for f in FP.glob("**/index.html"):
            page = f.read_text(encoding="utf-8")
            for s in gen.NOINDEX_PLACE_SLUGS:
                self.assertNotIn(f'href="/field-pack/{s}/" data-related-link', page, str(f))

    def test_counts_agree(self):
        idx = (FP / "index.html").read_text(encoding="utf-8")
        listed = len(set(re.findall(r'<li><a href="/field-pack/([a-z0-9-]+)/">', idx.split('id="all-places-dir"', 1)[1].split("</details>", 1)[0])))
        nums = {int(x) for x in re.findall(r"(\d+) places worldwide", idx)}
        nums |= {int(x) for x in re.findall(r"<span data-place-count>(\d+)</span>", idx)}
        nums |= {int(x) for x in re.findall(r"All (\d+) places", idx)}
        nums |= {int(x) for x in re.findall(r'data-place-count-build="(\d+)"', idx)}
        self.assertEqual(nums, {listed})
        js = (FP / "js" / "places-data.js").read_text(encoding="utf-8")
        flagged = set(re.findall(r'id: "([a-z0-9-]+)",\n    listed: false,', js))
        self.assertEqual(flagged, set(gen.NOINDEX_PLACE_SLUGS))
        self.assertEqual(len(re.findall(r'^    id: "', js, re.M)) - len(flagged), listed)

    def test_url_lists_skip_noindex(self):
        d = json.loads((FP / "seo-venues.json").read_text(encoding="utf-8"))
        self.assertEqual(d["count"], len(d["urls"]))
        txt = (FP / "SEO_URLS.txt").read_text(encoding="utf-8")
        for s in gen.NOINDEX_PLACE_SLUGS:
            self.assertFalse(any(u.endswith(f"/field-pack/{s}/") for u in d["urls"]))
            self.assertNotIn(f"/field-pack/{s}/\n", txt)

    def test_pages_still_exist(self):
        for s in gen.NOINDEX_PLACE_SLUGS:
            self.assertTrue((FP / s / "index.html").is_file(), s)


if __name__ == "__main__":
    unittest.main()
