"""Card pages are image-first: photo + Q&A dominant, short labels, no tutorial essays."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from generate_bdo_seo import (  # noqa: E402
    CARD_PRINT_NOTE,
    CARD_TALK_H2,
    CARDS_PLAY_BROWSE,
    CARDS_PLAY_CTA,
    CARDS_PLAY_H1,
    CARDS_PLAY_PRINT_HREF,
    CTA_AT_HOME,
    CTA_CARD_PLACE,
    CTA_CARDS_HUB,
    CTA_PRINT,
    CTA_PRINT_CARD,
    HOME_HREF,
    PLACE_VFT_CTA,
    CARD_SEO_CSS_VER,
    is_youtube_url,
    watch_links_html,
)

FP = REPO / "static" / "field-pack"
GENERATOR = REPO / "scripts" / "generate_bdo_seo.py"
GIRAFFE = FP / "cards" / "reticulated-giraffe" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
HUB = FP / "cards" / "index.html"
WORDY = (
    "Explore at home",
    "At-home card",
    "Talk this card through at home",
    "print only if you want paper",
    "6 questions · talk, tap, or print",
    "Print a hunt for the visit",
    "This zoo's cards",
    "This museum's cards",
    "This place's cards",
    "Place page",
    "Open card — 6 talk questions",
    "from Field Trip Kit place lists",
)


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class CardPageSparseChromeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.giraffe = GIRAFFE.read_text(encoding="utf-8")
        cls.lion = LION.read_text(encoding="utf-8")
        cls.hub = HUB.read_text(encoding="utf-8")
        cls.gen = GENERATOR.read_text(encoding="utf-8")
        cls.pages = {
            "reticulated-giraffe": cls.giraffe,
            "african-lion": cls.lion,
        }

    def test_generator_locks_sparse_strings(self):
        self.assertEqual(CTA_AT_HOME, "At home")
        self.assertEqual(CTA_PRINT, "Print")
        self.assertEqual(CTA_PRINT_CARD, "Print this card")
        self.assertEqual(CARD_PRINT_NOTE, "One animal sheet — not the hide-and-seek cutouts")
        self.assertEqual(CARDS_PLAY_H1, "Print cutouts to play")
        self.assertEqual(CARDS_PLAY_CTA, "Print the cutouts")
        self.assertEqual(CARDS_PLAY_BROWSE, "Browse cards on the screen")
        self.assertEqual(CARDS_PLAY_PRINT_HREF, "/field-pack/virtual-zoo/?print=1")
        self.assertEqual(CARD_TALK_H2, "Talk")
        self.assertEqual(CTA_CARDS_HUB, "Cards")
        self.assertEqual(CTA_CARD_PLACE, "Place")
        self.assertEqual(PLACE_VFT_CTA, "Virtual Field Trip")
        self.assertIn('CARD_TALK_H2 = "Talk"', self.gen)
        self.assertIn('CTA_CARD_PLACE = "Place"', self.gen)
        self.assertIn('CTA_PRINT_CARD = "Print this card"', self.gen)
        self.assertIn("film_via_vft", self.gen)
        self.assertIn("def is_youtube_url(", self.gen)
        self.assertIn("--cards-only", self.gen)
        self.assertNotIn("6 questions · talk, tap, or print", self.gen)

    def test_card_pages_drop_instructional_chrome(self):
        for cid, html in self.pages.items():
            main = _main(html)
            with self.subTest(card=cid):
                for phrase in WORDY:
                    self.assertNotIn(phrase, main, phrase)
                self.assertNotIn("step-chip", main)
                self.assertIn(f">{CARD_TALK_H2}</h2>", main)
                self.assertIn(f">{CTA_PRINT_CARD}</button>", main)
                self.assertIn(CARD_PRINT_NOTE, main)

    def test_photo_is_first_and_dominant(self):
        for cid, html in self.pages.items():
            main = _main(html)
            with self.subTest(card=cid):
                photo_at = main.find('class="card-page-photo"')
                title_at = main.find("<h1>")
                self.assertGreater(photo_at, 0)
                self.assertGreater(title_at, photo_at)
                self.assertIn('class="card-page-blurb"', main)
                blurbs = re.findall(r'class="card-page-blurb"[^>]*>(.*?)</p>', main, re.S)
                self.assertEqual(len(blurbs), 1)
                self.assertLessEqual(len(_text(blurbs[0])), 90)
                self.assertIn(f"seo-venue.css?v={CARD_SEO_CSS_VER}", html)

    def test_actions_are_few_and_short(self):
        for cid, html in self.pages.items():
            main = _main(html)
            actions = main.split('class="card-page-actions"', 1)[1]
            with self.subTest(card=cid):
                self.assertIn(f">{PLACE_VFT_CTA}</a>", actions)
                self.assertIn(f">{CTA_PRINT_CARD}</button>", actions)
                self.assertNotIn("Explore at home", actions)
                self.assertLessEqual(actions.count('class="btn '), 3)

    def test_pre_recorded_film_uses_vft_not_youtube(self):
        for cid, html in self.pages.items():
            main = _main(html)
            with self.subTest(card=cid):
                self.assertNotIn("youtube.com", main.lower())
                self.assertIn("/field-pack/virtual-field-trip/?tab=", main)
                self.assertIn("#habitat=", main)

    def test_watch_links_helper_routes_youtube_film_to_vft(self):
        item = {
            "vft": {
                "cam_url": "https://nationalzoo.si.edu/webcams/lion-cam",
                "cam_label": "Lion cam at the Smithsonian National Zoo",
                "film_url": "https://www.youtube.com/watch?v=tlZwYsJpqjo",
                "film_title": "Giraffe calf at the Houston Zoo",
                "vft_href": "/field-pack/virtual-field-trip/?tab=zoo#habitat=african-lion",
            }
        }
        place = watch_links_html(item)
        card = watch_links_html(item, film_via_vft=True)
        self.assertIn("youtube.com", place)
        self.assertNotIn("youtube.com", card)
        self.assertIn("/field-pack/virtual-field-trip/?tab=zoo#habitat=african-lion", card)
        self.assertIn("Film from Houston Zoo", card)
        self.assertIn("Live from Smithsonian National Zoo", card)
        self.assertTrue(is_youtube_url("https://www.youtube.com/watch?v=tlZwYsJpqjo"))
        self.assertFalse(is_youtube_url("https://nationalzoo.si.edu/webcams/lion-cam"))

    def test_brand_and_explorer_paths_unchanged(self):
        for html in self.pages.values():
            self.assertIn(f'class="shell-brand" href="{HOME_HREF}"', html)
            self.assertIn(f'class="shell-product" href="{HOME_HREF}"', html)
            self.assertIn('href="/field-pack/" role="menuitem">All places', html)
            self.assertIn('href="/field-pack/virtual-field-trip/"', html)
            self.assertIn('href="/field-pack/cards/"', html)

    def test_cards_hub_stays_a_finder_without_sales_copy(self):
        self.assertIn("Print cutouts to play", self.hub)
        self.assertIn("Find a card", self.hub)
        self.assertIn('id="cards-hub-search"', self.hub)
        self.assertIn('data-card-filter="wildlife"', self.hub)
        self.assertIn("58 cards", self.hub)
        self.assertNotIn("from Field Trip Kit place lists", self.hub)
        self.assertNotIn("Print is optional", self.hub)
        self.assertNotIn("Explore animal", self.hub)
        self.assertIn('href="/start/"', self.hub)
        self.assertIn('href="/field-pack/"', self.hub)
        self.assertNotIn("youtube.com", self.hub)
        all_wrap = self.hub.split('id="cards-all-wrap"', 1)[1]
        self.assertNotIn("cards-hub-teaser", all_wrap)

    def test_youtube_host_helper_is_narrow(self):
        self.assertEqual(urlparse("https://www.youtube.com/watch?v=x").hostname, "www.youtube.com")
        self.assertTrue(is_youtube_url("https://youtu.be/abc"))
        self.assertFalse(is_youtube_url(""))


if __name__ == "__main__":
    unittest.main()
