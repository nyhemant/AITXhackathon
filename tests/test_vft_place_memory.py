"""Place links keep a venue slug when tabUrl rebuilds the query.

Not-yet / VFT arrivals use ?from={venueSlug}, not from=card. tabUrl used to
keep only from=card, which dropped the slug. return= is the channel that
survives openHabitat / replaceState.
"""

from __future__ import annotations

import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
VFT_JS = REPO / "static" / "field-pack" / "js" / "virtual-venue.js"


def _fn_body(src: str, name: str) -> str:
    token = f"function {name}("
    start = src.index(token)
    depth = 0
    i = src.index("{", start)
    for j in range(i, len(src)):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                return src[start : j + 1]
    raise AssertionError(f"unclosed function {name}")


class VftPlaceMemoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.js = VFT_JS.read_text(encoding="utf-8")

    def test_card_return_venue_copies_non_card_from(self):
        body = _fn_body(self.js, "cardReturnVenue")
        self.assertIn('.get("return")', body)
        self.assertIn('.get("from")', body)
        self.assertLess(body.find('.get("return")'), body.find('.get("from")'))
        self.assertIn('!== "card"', body)
        self.assertIn("if (ret) return ret;", body)
        self.assertIn("if (from && from !== \"card\") return from;", body)

    def test_tab_url_reemits_return_and_keeps_from_card(self):
        body = _fn_body(self.js, "tabUrl")
        self.assertIn("const ret = cardReturnVenue();", body)
        self.assertIn('if (ret) q.set("return", ret);', body)
        self.assertIn("if (fromCard()) q.set(\"from\", \"card\");", body)
        self.assertIn("openHabitat", self.js)
        open_body = _fn_body(self.js, "openHabitat")
        self.assertIn("tabUrl(currentTab(), h.id)", open_body)
        self.assertIn("history.replaceState", open_body)


if __name__ == "__main__":
    unittest.main()
