"""African elephant stop must not pretend an Asian-elephant film is African."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
VDIR = REPO / "static" / "field-pack" / "data" / "virtual-venues"
URL = "https://www.youtube.com/watch?v=Qzy0r4MUlQk"
TITLE = "Asian elephants — cousins / compare"


class ElephantFilmHonestyTests(unittest.TestCase):
    def test_habitat_and_library_share_the_honest_caption(self):
        zoo = json.loads((VDIR / "virtual-zoo.json").read_text(encoding="utf-8"))
        lib = json.loads((VDIR / "zoo-film-library.json").read_text(encoding="utf-8"))
        habitat = next(h for h in zoo["habitats"] if h["id"] == "african-elephant")
        row = next(c for c in lib["cards"] if c["cardId"] == "african-elephant")
        self.assertEqual(habitat["video"]["url"], URL)
        self.assertEqual(row["video"]["url"], URL)
        self.assertEqual(habitat["video"]["title"], TITLE)
        self.assertEqual(row["video"]["title"], TITLE)
        self.assertNotIn("Asian elephants at the National Zoo", habitat["video"]["title"])


if __name__ == "__main__":
    unittest.main()
