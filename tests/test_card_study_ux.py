"""Systemic study-card UX: no print note, dual picker, try-next, hero links."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from generate_bdo_seo import (  # noqa: E402
    CARD_SEO_CSS_VER,
    STUDY_CARD_CSS_VER,
    STUDY_CARD_JS_VER,
    card_hero_links_html,
    card_hero_photo_html,
    watch_links_html,
)
from study_cards import (  # noqa: E402
    STUDY_CARDS,
    study_card_ids,
    study_talk_html,
    study_try_next_html,
    study_try_next_ids,
    study_deck_for,
)

FP = REPO / "static" / "field-pack"
SEO = REPO / "scripts" / "generate_bdo_seo.py"
STUDY_JS = FP / "js" / "study-card.js"
STUDY_CSS = FP / "css" / "study-card.css"
SEO_CSS = FP / "css" / "seo-venue.css"
PRINT_NOTE = "One animal sheet — not the hide-and-seek cutouts"

STUDY_PAGES = {
    cid: FP / "cards" / cid / "index.html" for cid in study_card_ids()
}


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


class CardStudyUxTests(unittest.TestCase):
    def test_print_note_is_gone_from_generator_and_cards(self):
        gen = SEO.read_text(encoding="utf-8")
        self.assertNotIn("CARD_PRINT_NOTE", gen)
        self.assertNotIn("card-print-note", gen)
        self.assertNotIn(PRINT_NOTE, gen)
        for cid, path in STUDY_PAGES.items():
            html = path.read_text(encoding="utf-8")
            with self.subTest(card=cid):
                self.assertNotIn(PRINT_NOTE, html)
                self.assertNotIn("card-print-note", html)
                self.assertIn('id="print-this-card"', html)

    def test_study_pack_has_top_and_bottom_pickers(self):
        deck = study_deck_for("galapagos-tortoise")
        html = study_talk_html(deck)
        self.assertEqual(html.count('role="group"'), 2)
        self.assertEqual(html.count("study-level-picker-bottom"), 1)
        self.assertIn('aria-label="Study level"', html)
        self.assertIn('aria-label="Study level at the end"', html)
        self.assertLess(html.find("study-level-picker"), html.find("study-deepen"))
        self.assertGreater(html.find("study-level-picker-bottom"), html.find("Push further"))
        self.assertIn('class="study-foot no-print"', html)

        page = (FP / "cards" / "galapagos-tortoise" / "index.html").read_text(encoding="utf-8")
        main = _main(page)
        self.assertEqual(main.count('role="group"'), 2)
        self.assertIn("study-level-picker-bottom", main)
        zebra_deck = study_deck_for("zebra")
        zebra_html = study_talk_html(zebra_deck)
        self.assertEqual(zebra_html.count('role="group"'), 2)
        self.assertIn("study-level-picker-bottom", zebra_html)
        self.assertIn('data-study-pick="hard"', zebra_html)
        self.assertNotIn('data-study-pick="zoologist"', zebra_html)
        zebra_page = (FP / "cards" / "zebra" / "index.html").read_text(encoding="utf-8")
        zebra_main = _main(zebra_page)
        self.assertEqual(zebra_main.count('role="group"'), 2)
        self.assertIn("study-level-picker-bottom", zebra_main)
        self.assertIn("Park Ranger", zebra_main)
        self.assertNotIn("Zoologist", zebra_main)
        print_tpl = page.split('id="study-print-template">', 1)[1].split("</template>", 1)[0]
        self.assertNotIn("study-level-picker", print_tpl)
        self.assertNotIn("study-foot", print_tpl)

    def test_level_switch_resets_and_scrolls(self):
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("function scrollStudyIntoView(", js)
        self.assertIn('behavior: "smooth"', js)
        self.assertIn('block: "start"', js)
        self.assertIn("scrollStudyIntoView(root)", js)
        self.assertIn("applyDeck(root, deck)", js)
        css = STUDY_CSS.read_text(encoding="utf-8")
        self.assertIn("scroll-margin-top:", css)

    def test_try_next_is_three_other_study_animals(self):
        self.assertEqual(
            study_try_next_ids("african-lion"),
            ["reticulated-giraffe", "african-elephant", "african-penguin"],
        )
        self.assertEqual(
            study_try_next_ids("reticulated-giraffe"),
            ["african-elephant", "african-lion", "african-penguin"],
        )
        self.assertEqual(
            study_try_next_ids("african-elephant"),
            ["reticulated-giraffe", "african-lion", "african-penguin"],
        )
        self.assertEqual(
            study_try_next_ids("african-penguin"),
            ["caribbean-flamingo", "african-lion", "reticulated-giraffe"],
        )
        self.assertEqual(
            study_try_next_ids("caribbean-flamingo"),
            ["african-penguin", "african-lion", "reticulated-giraffe"],
        )
        self.assertEqual(
            study_try_next_ids("galapagos-tortoise"),
            ["african-elephant", "reticulated-giraffe", "african-lion"],
        )
        self.assertEqual(
            study_try_next_ids("zebra"),
            ["african-lion", "reticulated-giraffe", "african-elephant"],
        )
        for cid in study_card_ids():
            nxt = study_try_next_ids(cid)
            with self.subTest(card=cid):
                self.assertEqual(len(nxt), 3)
                self.assertNotIn(cid, nxt)
                self.assertTrue(set(nxt).issubset(STUDY_CARDS))

        block = study_try_next_html("galapagos-tortoise")
        self.assertIn('aria-label="Try next"', block)
        self.assertIn('aria-label="Try next: African elephant"', block)
        self.assertIn('href="/field-pack/cards/african-elephant/"', block)
        self.assertIn("/field-pack/photos/african-elephant.jpg", block)
        self.assertNotIn("galapagos-tortoise", block.split("card-try-next-grid", 1)[1])

        page = (FP / "cards" / "galapagos-tortoise" / "index.html").read_text(encoding="utf-8")
        main = _main(page)
        self.assertIn('class="card-try-next no-print"', main)
        self.assertEqual(main.count("card-try-next-link"), 3)
        talk_at = main.find('class="card-talk-pack')
        try_at = main.find('class="card-try-next')
        actions_at = main.find('class="card-page-actions"')
        self.assertLess(talk_at, try_at)
        self.assertLess(try_at, actions_at)
        print_tpl = page.split('id="study-print-template">', 1)[1].split("</template>", 1)[0]
        self.assertNotIn("card-try-next", print_tpl)
        koala = (FP / "cards" / "koala" / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("card-try-next", koala)

    def test_photos_and_watch_live_share_hero_row(self):
        self.assertEqual(CARD_SEO_CSS_VER, "35")
        self.assertEqual(STUDY_CARD_JS_VER, "7")
        self.assertEqual(STUDY_CARD_CSS_VER, "8")
        css = SEO_CSS.read_text(encoding="utf-8")
        self.assertIn(".card-page .card-hero-links", css)
        self.assertIn("display: contents", css)
        self.assertIn("flex-wrap: wrap", css)

        more = '<div class="action-row detail-links">Photos</div>'
        watch = watch_links_html(
            {
                "vft": {
                    "tab": "zoo",
                    "habitat_id": "african-lion",
                    "film_url": "https://www.youtube.com/watch?v=x",
                    "film_title": "Lion film at the Smithsonian National Zoo",
                    "vft_href": "/field-pack/virtual-zoo/#habitat=african-lion",
                }
            },
            film_via_vft=True,
            watch_live=True,
        )
        row = card_hero_links_html(more, watch)
        self.assertIn('class="card-hero-links no-print"', row)
        self.assertIn("Photos", row)
        self.assertIn("Watch Live", row)
        self.assertEqual(card_hero_links_html("", ""), "")

        for cid in ("african-lion", "galapagos-tortoise", "reticulated-giraffe"):
            html = (FP / "cards" / cid / "index.html").read_text(encoding="utf-8")
            main = _main(html)
            with self.subTest(card=cid):
                self.assertIn('class="card-hero-links no-print"', main)
                hero_at = main.find('class="card-hero-links')
                photos_at = main.find(">Photos</a>")
                watch_at = main.find('class="seo-watch-row"')
                talk_at = main.find('class="card-talk-pack')
                self.assertGreater(photos_at, hero_at)
                self.assertGreater(watch_at, photos_at)
                self.assertLess(watch_at, talk_at)
                self.assertIn("study-card.js?v=7", html)
                self.assertIn("study-card.css?v=8", html)
                self.assertIn(f"seo-venue.css?v={CARD_SEO_CSS_VER}", html)

        warthog = _main((FP / "cards" / "warthog" / "index.html").read_text(encoding="utf-8"))
        self.assertIn("card-hero-links", warthog)
        self.assertIn(">Photos</a>", warthog)
        self.assertNotIn("Watch Live", warthog)
        self.assertNotIn('class="seo-watch-row"', warthog)

    def test_hero_photo_matches_watch_live_href(self):
        href = "/field-pack/virtual-zoo/?from=card#habitat=zebra"
        linked = card_hero_photo_html(
            photo="/field-pack/photos/zebra.jpg?v=img2",
            name="Zebra",
            emoji="🦓",
            pos_attr="",
            watch_href=href,
        )
        self.assertIn('class="card-page-photo-link"', linked)
        self.assertIn('aria-label="Watch Live: Zebra"', linked)
        self.assertIn(f'href="{href}"', linked)
        self.assertRegex(linked, r'<a class="card-page-photo-link"[^>]*>\s*<img class="card-page-photo"')

        bare = card_hero_photo_html(
            photo="/field-pack/photos/warthog.jpg?v=img2",
            name="Warthog",
            emoji="🐗",
            pos_attr="",
            watch_href="",
        )
        self.assertNotIn("<a ", bare)
        self.assertNotIn("card-page-photo-link", bare)
        self.assertIn('class="card-page-photo"', bare)
        self.assertIn(
            'aria-hidden="true"',
            card_hero_photo_html(photo="", name="Zebra", emoji="🦓", watch_href=href),
        )

        css = SEO_CSS.read_text(encoding="utf-8")
        self.assertIn(".card-page a.card-page-photo-link", css)
        self.assertIn("cursor: pointer", css)
        gen = SEO.read_text(encoding="utf-8")
        self.assertIn("a.card-watch-live, a.card-page-photo-link", gen)

        for cid in ("galapagos-tortoise", "zebra", "african-lion"):
            html = (FP / "cards" / cid / "index.html").read_text(encoding="utf-8")
            main = _main(html)
            with self.subTest(card=cid):
                self.assertIn('class="card-page-photo-link"', main)
                photo_block = main.split('class="card-page-photo-link"', 1)[1].split("<h1>", 1)[0]
                watch_block = main.split('class="seo-watch-row"', 1)[1].split("</p>", 1)[0]
                photo_href = photo_block.split('href="', 1)[1].split('"', 1)[0]
                watch_href = watch_block.split('href="', 1)[1].split('"', 1)[0]
                self.assertEqual(photo_href, watch_href)
                self.assertIn("from=card", photo_href)
                self.assertIn("#habitat=", photo_href)
                self.assertIn(f'aria-label="Watch Live:', main)
                print_tpl = html.split('id="study-print-template">', 1)[1].split("</template>", 1)[0]
                self.assertNotIn("card-page-photo-link", print_tpl)

        warthog = _main((FP / "cards" / "warthog" / "index.html").read_text(encoding="utf-8"))
        self.assertNotIn("card-page-photo-link", warthog)
        self.assertIn('class="card-page-photo"', warthog)
        self.assertLess(warthog.find("card-page-photo"), warthog.find("<h1>"))

        dino = _main((FP / "cards" / "sci-dinosaur" / "index.html").read_text(encoding="utf-8"))
        self.assertNotIn("card-page-photo-link", dino)
        self.assertNotIn("Watch Live", dino)


if __name__ == "__main__":
    unittest.main()
