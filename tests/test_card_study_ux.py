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
    study_print_html_for,
    STUDY_CARDS,
    STUDY_QUIZ_H2,
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

    def test_study_pack_has_top_picker_and_next_tier_prompt(self):
        deck = study_deck_for("galapagos-tortoise")
        html = study_talk_html(deck)
        self.assertEqual(html.count('role="group"'), 1)
        self.assertEqual(html.count("study-level-picker-bottom"), 0)
        self.assertIn('aria-label="Study level"', html)
        self.assertNotIn('aria-label="Study level at the end"', html)
        self.assertIn("Got them all? Try Park Ranger", html)
        self.assertIn("study-next-tier", html)
        self.assertIn("A grown-up can help you try a harder set.", html)
        self.assertNotIn("Jump to a harder set any time.", html)
        self.assertNotIn("Tougher quizzes", html)
        self.assertLess(html.find("study-level-picker"), html.find("study-explore"))
        self.assertLess(html.find("study-next-tier"), html.find("Push further"))
        self.assertIn('class="study-foot no-print"', html)
        self.assertEqual(html.count('class="study-score"'), 1)
        self.assertIn("data-pending", html)
        self.assertRegex(html, r"\d+ questions · (Junior Ranger|Park Ranger|Zoologist)</p>")
        self.assertEqual(html.count('data-study-correct'), 0)
        self.assertIn(f"{STUDY_QUIZ_H2}</h2>", html)
        self.assertIn('aria-label="Quiz"', html)
        self.assertIn("Explore more", html)
        self.assertNotIn('<aside class="study-deepen"', html)

        page = (FP / "cards" / "galapagos-tortoise" / "index.html").read_text(encoding="utf-8")
        main = _main(page)
        self.assertEqual(main.count('role="group"'), 1)
        self.assertIn("study-next-tier", main)
        self.assertNotIn("study-level-picker-bottom", main)
        zebra_deck = study_deck_for("zebra")
        zebra_html = study_talk_html(zebra_deck)
        self.assertEqual(zebra_html.count('role="group"'), 1)
        self.assertIn("study-next-tier", zebra_html)
        self.assertNotIn("study-level-picker-bottom", zebra_html)
        self.assertIn('data-study-pick="hard"', zebra_html)
        self.assertIn('data-study-pick="zoologist"', zebra_html)
        zebra_page = (FP / "cards" / "zebra" / "index.html").read_text(encoding="utf-8")
        zebra_main = _main(zebra_page)
        self.assertEqual(zebra_main.count('role="group"'), 1)
        self.assertIn("study-next-tier", zebra_main)
        self.assertNotIn("study-level-picker-bottom", zebra_main)
        self.assertIn("Park Ranger", zebra_main)
        self.assertIn("Zoologist", zebra_main)
        zoo_html = study_talk_html(study_deck_for("zebra", "zoologist"))
        self.assertIn("Try next:", zoo_html)
        self.assertNotIn("Got them all?", zoo_html)
        print_tpl = study_print_html_for("zebra")
        self.assertNotIn("study-level-picker", print_tpl)
        self.assertNotIn("study-foot", print_tpl)
        self.assertNotIn("study-explore", print_tpl)

    def test_study_heading_is_quiz_with_bottom_score_and_explore_more(self):
        deck = study_deck_for("galapagos-tortoise")
        html = study_talk_html(deck)
        self.assertEqual(STUDY_QUIZ_H2, "Quiz")
        self.assertIn('aria-label="Quiz"', html)
        self.assertIn(">Quiz</h2>", html)
        self.assertIn("Talk about it", html)
        self.assertIn('<details class="study-explore no-print">', html)
        self.assertNotIn('<details class="study-explore no-print" open', html)
        self.assertEqual(html.count("data-study-correct"), 0)
        self.assertEqual(html.count('class="study-score"'), 1)
        self.assertIn("data-pending", html)
        self.assertLess(html.find("study-toolbar"), html.find("study-grid"))
        self.assertLess(html.find("study-grid"), html.find("study-foot"))
        self.assertLess(html.find("study-foot"), html.find("study-explore"))
        self.assertLess(html.find("study-foot"), html.find('class="study-score"'))
        toolbar = html.split("study-toolbar", 1)[1].split("</div>", 1)[0]
        self.assertNotIn("study-score", toolbar)
        self.assertIn("data-study-reveal", toolbar)

        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("function hasAnyAnswer(", js)
        self.assertIn("function paintNextTier(", js)
        self.assertIn("Got them all? Try", js)
        self.assertIn("function exploreHtml(", js)
        self.assertIn('insertAdjacentHTML("afterend", nextExplore)', js)
        self.assertNotIn("function deepenHtml(", js)
        css = STUDY_CSS.read_text(encoding="utf-8")
        self.assertIn("min-height: 44px", css)
        self.assertIn(".card-page .card-study-pack .study-explore", css)
        self.assertIn(".card-page .card-study-pack .study-foot", css)

        for cid in ("galapagos-tortoise", "zebra", "african-lion"):
            page = (FP / "cards" / cid / "index.html").read_text(encoding="utf-8")
            main = _main(page)
            with self.subTest(card=cid):
                self.assertIn('aria-label="Quiz"', main)
                self.assertIn(">Quiz</h2>", main)
                self.assertEqual(main.count("data-study-correct"), 0)
                self.assertIn("Explore more", main)
                self.assertIn("Talk about it", main)
                self.assertNotIn('<aside class="study-deepen"', main)
                print_tpl = study_print_html_for(cid)
                self.assertIn("Talk about it", print_tpl)
                self.assertNotIn("Explore more", print_tpl)
                self.assertNotIn("study-explore", print_tpl)

        jelly = _main((FP / "cards" / "jellyfish" / "index.html").read_text(encoding="utf-8"))
        self.assertIn('aria-label="Quiz"', jelly)
        self.assertIn(">Quiz</h2>", jelly)
        self.assertIn("study-explore", jelly)
        self.assertNotIn(">Talk</h2>", jelly)
        kelp = _main((FP / "cards" / "kelp-forest" / "index.html").read_text(encoding="utf-8"))
        self.assertIn('aria-label="Quiz"', kelp)
        self.assertIn(">Quiz</h2>", kelp)
        self.assertIn("study-explore", kelp)
        self.assertNotIn(">Talk</h2>", kelp)
        octo = _main((FP / "cards" / "octopus" / "index.html").read_text(encoding="utf-8"))
        self.assertIn('aria-label="Quiz"', octo)
        self.assertIn(">Quiz</h2>", octo)
        self.assertIn("study-explore", octo)
        self.assertNotIn(">Talk</h2>", octo)
        turtle = _main((FP / "cards" / "sea-turtle" / "index.html").read_text(encoding="utf-8"))
        self.assertIn('aria-label="Quiz"', turtle)
        self.assertIn(">Quiz</h2>", turtle)
        self.assertIn("study-explore", turtle)
        self.assertNotIn(">Talk</h2>", turtle)
        star = _main((FP / "cards" / "starfish" / "index.html").read_text(encoding="utf-8"))
        self.assertIn('aria-label="Quiz"', star)
        self.assertIn(">Quiz</h2>", star)
        self.assertIn("study-explore", star)
        self.assertNotIn(">Talk</h2>", star)
        horse = _main((FP / "cards" / "seahorse" / "index.html").read_text(encoding="utf-8"))
        self.assertIn('aria-label="Quiz"', horse)
        self.assertIn(">Quiz</h2>", horse)
        self.assertIn("study-explore", horse)
        self.assertNotIn(">Talk</h2>", horse)
        ray = _main((FP / "cards" / "stingray" / "index.html").read_text(encoding="utf-8"))
        self.assertIn('aria-label="Quiz"', ray)
        self.assertIn(">Quiz</h2>", ray)
        self.assertIn("study-explore", ray)
        self.assertNotIn(">Talk</h2>", ray)
        whale = _main((FP / "cards" / "whale-shark" / "index.html").read_text(encoding="utf-8"))
        self.assertIn('aria-label="Quiz"', whale)
        self.assertIn(">Quiz</h2>", whale)
        self.assertNotIn(">Talk</h2>", whale)
        self.assertIn("study-explore", whale)
        sea = _main((FP / "cards" / "sea-otter" / "index.html").read_text(encoding="utf-8"))
        self.assertIn('aria-label="Quiz"', sea)
        self.assertIn(">Quiz</h2>", sea)
        self.assertIn("study-explore", sea)
        self.assertNotIn(">Talk</h2>", sea)
        otter = _main((FP / "cards" / "asian-small-clawed-otter" / "index.html").read_text(encoding="utf-8"))
        self.assertIn('aria-label="Quiz"', otter)
        self.assertIn(">Quiz</h2>", otter)
        self.assertIn("study-explore", otter)
        self.assertNotIn(">Talk</h2>", otter)

    def test_explore_more_sits_between_bottom_foot_and_try_next(self):
        deck = study_deck_for("galapagos-tortoise")
        html = study_talk_html(deck)
        self.assertLess(html.find("study-foot"), html.find("study-explore"))
        self.assertLess(html.find("study-next-tier"), html.find("study-explore"))

        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn('if (foot) foot.insertAdjacentHTML("afterend", nextExplore)', js)

        for cid in ("galapagos-tortoise", "zebra", "nile-hippo", "western-lowland-gorilla", "cheetah", "red-panda", "koala", "chimpanzee", "asian-small-clawed-otter", "two-toed-sloth", "freshwater-fish", "polar-bear", "sea-otter", "american-alligator", "american-bison", "elk", "puffin", "clownfish", "crab", "cuttlefish", "eel", "jellyfish", "kelp-forest", "manta-ray", "octopus", "sea-turtle", "seahorse", "starfish", "stingray"):
            page = (FP / "cards" / cid / "index.html").read_text(encoding="utf-8")
            main = _main(page)
            with self.subTest(card=cid):
                foot_at = main.find("study-foot")
                explore_at = main.find("study-explore")
                try_at = main.find("card-try-next")
                self.assertGreater(foot_at, -1)
                self.assertGreater(explore_at, -1)
                self.assertGreater(try_at, -1)
                self.assertLess(foot_at, explore_at)
                self.assertLess(explore_at, try_at)

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
        self.assertEqual(
            study_try_next_ids("sumatran-tiger"),
            ["african-lion", "reticulated-giraffe", "african-elephant"],
        )
        self.assertEqual(
            study_try_next_ids("western-lowland-gorilla"),
            ["african-elephant", "african-lion", "reticulated-giraffe"],
        )
        self.assertEqual(
            study_try_next_ids("cheetah"),
            ["african-lion", "zebra", "reticulated-giraffe"],
        )
        self.assertEqual(
            study_try_next_ids("red-panda"),
            ["sumatran-tiger", "zebra", "african-lion"],
        )
        self.assertEqual(
            study_try_next_ids("koala"),
            ["red-panda", "sumatran-tiger", "african-lion"],
        )
        self.assertEqual(
            study_try_next_ids("chimpanzee"),
            ["western-lowland-gorilla", "african-elephant", "african-lion"],
        )
        self.assertEqual(
            study_try_next_ids("ostrich"),
            ["caribbean-flamingo", "african-penguin", "african-lion"],
        )
        self.assertEqual(
            study_try_next_ids("warthog"),
            ["zebra", "ostrich", "african-lion"],
        )
        self.assertEqual(
            study_try_next_ids("shark"),
            ["clownfish", "crab", "cuttlefish"],
        )
        self.assertEqual(
            study_try_next_ids("asian-small-clawed-otter"),
            ["red-panda", "african-lion", "reticulated-giraffe"],
        )
        self.assertEqual(
            study_try_next_ids("two-toed-sloth"),
            ["orangutan", "koala", "african-lion"],
        )
        self.assertEqual(
            study_try_next_ids("freshwater-fish"),
            ["shark", "clownfish", "crab"],
        )
        self.assertEqual(
            study_try_next_ids("polar-bear"),
            ["african-penguin", "asian-small-clawed-otter", "african-lion"],
        )
        self.assertEqual(
            study_try_next_ids("sea-otter"),
            ["clownfish", "crab", "cuttlefish"],
        )
        self.assertEqual(
            study_try_next_ids("american-alligator"),
            ["galapagos-tortoise", "african-lion", "reticulated-giraffe"],
        )
        self.assertEqual(
            study_try_next_ids("american-bison"),
            ["zebra", "warthog", "african-lion"],
        )
        self.assertEqual(
            study_try_next_ids("elk"),
            ["american-bison", "zebra", "african-lion"],
        )
        self.assertEqual(
            study_try_next_ids("puffin"),
            ["clownfish", "crab", "cuttlefish"],
        )
        self.assertEqual(
            study_try_next_ids("clownfish"),
            ["crab", "cuttlefish", "eel"],
        )
        self.assertEqual(
            study_try_next_ids("crab"),
            ["clownfish", "cuttlefish", "eel"],
        )
        self.assertEqual(
            study_try_next_ids("cuttlefish"),
            ["crab", "clownfish", "eel"],
        )
        self.assertEqual(
            study_try_next_ids("eel"),
            ["cuttlefish", "crab", "clownfish"],
        )
        self.assertEqual(
            study_try_next_ids("jellyfish"),
            ["eel", "cuttlefish", "clownfish"],
        )
        self.assertEqual(
            study_try_next_ids("kelp-forest"),
            ["jellyfish", "sea-otter", "clownfish"],
        )
        self.assertEqual(
            study_try_next_ids("manta-ray"),
            ["jellyfish", "clownfish", "crab"],
        )
        self.assertEqual(
            study_try_next_ids("octopus"),
            ["cuttlefish", "jellyfish", "clownfish"],
        )
        self.assertEqual(
            study_try_next_ids("sea-turtle"),
            ["octopus", "manta-ray", "clownfish"],
        )
        self.assertEqual(
            study_try_next_ids("seahorse"),
            ["octopus", "sea-turtle", "clownfish"],
        )
        self.assertEqual(
            study_try_next_ids("starfish"),
            ["sea-turtle", "octopus", "clownfish"],
        )
        self.assertEqual(
            study_try_next_ids("stingray"),
            ["manta-ray", "seahorse", "clownfish"],
        )
        self.assertEqual(
            study_try_next_ids("whale-shark"),
            ["manta-ray", "clownfish", "crab"],
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
        try_next = main.split('aria-label="Try next"', 1)[1].split("</nav>", 1)[0]
        self.assertEqual(try_next.count("card-try-next-link"), 3)
        talk_at = main.find('class="card-talk-pack')
        try_at = main.find('class="card-try-next')
        actions_at = main.find('class="card-page-actions"')
        self.assertLess(actions_at, talk_at)
        self.assertLess(talk_at, try_at)
        print_tpl = study_print_html_for("galapagos-tortoise")
        self.assertNotIn("card-try-next", print_tpl)
        whale = (FP / "cards" / "whale-shark" / "index.html").read_text(encoding="utf-8")
        self.assertIn('aria-label="Try next"', whale)
        self.assertIn("card-study-pack", whale)

    def test_photos_and_watch_live_share_hero_row(self):
        self.assertEqual(CARD_SEO_CSS_VER, "38")
        self.assertEqual(STUDY_CARD_JS_VER, "17")
        self.assertEqual(STUDY_CARD_CSS_VER, "14")
        css = SEO_CSS.read_text(encoding="utf-8")
        self.assertIn(".card-page .card-hero-links", css)
        self.assertIn("display: contents", css)
        self.assertIn("flex-wrap: wrap", css)
        self.assertIn("card-page-photo-zoom", css)
        self.assertIn("card-photo-lightbox", css)

        more = '<div class="action-row detail-links">Photos</div>'
        # Helper still builds a watch row for non-page callers; card pages omit it.
        watch = watch_links_html(
            {
                "vft": {
                    "tab": "zoo",
                    "habitat_id": "african-lion",
                    "film_url": "https://www.youtube.com/watch?v=x",
                    "film_title": "Lion film at the Smithsonian National Zoo",
                    "vft_href": "/field-pack/virtual-field-trip/?tab=zoo#habitat=african-lion",
                }
            },
            film_via_vft=True,
            watch_live=True,
        )
        row = card_hero_links_html(more, watch)
        self.assertIn('class="card-hero-links no-print"', row)
        self.assertIn("Photos", row)
        self.assertIn("Watch film from Smithsonian National Zoo", row)
        self.assertNotIn("Watch live", row)
        self.assertEqual(card_hero_links_html("", ""), "")
        # Photos-only hero links when watch is empty (page dedupe path)
        photos_only = card_hero_links_html(more, "")
        self.assertIn("Photos", photos_only)
        self.assertNotIn("Watch film", photos_only)

        for cid in ("african-lion", "reticulated-giraffe"):
            html = (FP / "cards" / cid / "index.html").read_text(encoding="utf-8")
            main = _main(html)
            with self.subTest(card=cid):
                actions_at = main.find('class="card-page-actions"')
                talk_at = main.find('class="card-talk-pack')
                self.assertGreater(actions_at, 0)
                self.assertLess(actions_at, talk_at)
                actions = main.split('class="card-page-actions"', 1)[1]
                self.assertIn("card-page-actions-primary", actions)
                self.assertIn("card-page-actions-print", actions)
                primary = actions.split('class="card-page-actions-primary"', 1)[1].split(
                    'class="card-page-actions-print"', 1
                )[0]
                print_row = actions.split('class="card-page-actions-print"', 1)[1]
                self.assertIn("card-watch-live", primary)
                self.assertIn("More photos at", primary)
                self.assertIn("card-page-photos", primary)
                watch_at = primary.find("card-watch-live")
                photos_at = primary.find("card-page-photos")
                self.assertLess(watch_at, photos_at)
                self.assertIn("print-this-card", print_row)
                self.assertIn("print-spec", print_row)
                self.assertNotIn("card-watch-live", print_row)
                self.assertNotIn("card-page-photos", print_row)
                self.assertEqual(main.find('class="seo-watch-row"'), -1)
                # Photos left the hero quiet row (Learn more may remain).
                hero = ""
                if 'class="card-hero-links' in main:
                    hero = main.split('class="card-hero-links', 1)[1].split(
                        'class="card-page-actions"', 1
                    )[0]
                self.assertNotIn("More photos at", hero)
                self.assertIn("study-card.js?v=17", html)
                self.assertIn("study-card.css?v=14", html)
                self.assertIn(f"seo-venue.css?v={CARD_SEO_CSS_VER}", html)

        warthog = _main((FP / "cards" / "warthog" / "index.html").read_text(encoding="utf-8"))
        self.assertIn("More photos at", warthog.split('class="card-page-actions"', 1)[1])
        self.assertNotIn('class="seo-watch-row"', warthog)
        self.assertIn("card-watch-live", warthog.split('class="card-page-actions"', 1)[1])
        self.assertIn("#habitat=warthog", warthog)

    def test_hero_photo_matches_watch_live_href(self):
        href = "/field-pack/virtual-field-trip/?tab=zoo&from=card#habitat=zebra"
        # Legacy cam-on-hero still supported by helper
        linked = card_hero_photo_html(
            photo="/field-pack/photos/zebra.jpg?v=img2",
            name="Zebra",
            emoji="🦓",
            pos_attr="",
            watch_href=href,
        )
        self.assertIn('class="card-page-photo-link"', linked)
        self.assertIn('aria-label="Watch Live: Zebra"', linked)
        self.assertIn(f'href="{href.replace("&", "&amp;")}"', linked)
        self.assertRegex(linked, r'<a class="card-page-photo-link"[^>]*>\s*<img class="card-page-photo"')

        zoom = card_hero_photo_html(
            photo="/field-pack/photos/zebra.jpg?v=img2",
            name="Zebra",
            emoji="🦓",
            enlarge=True,
        )
        self.assertIn('class="card-page-photo-zoom"', zoom)
        self.assertIn('aria-label="View larger photo: Zebra"', zoom)
        self.assertIn('data-photo-src="/field-pack/photos/zebra.jpg?v=img2"', zoom)
        self.assertNotIn("card-page-photo-link", zoom)

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
        self.assertIn("card-page-photo-zoom", css)
        gen = SEO.read_text(encoding="utf-8")
        self.assertIn('document.querySelectorAll("a.card-watch-live")', gen)
        self.assertIn("button.card-page-photo-zoom", gen)
        self.assertNotIn("a.card-watch-live, a.card-page-photo-link", gen)

        for cid in ("african-lion", "reticulated-giraffe"):
            html = (FP / "cards" / cid / "index.html").read_text(encoding="utf-8")
            main = _main(html)
            with self.subTest(card=cid):
                self.assertIn('class="card-page-photo-zoom"', main)
                self.assertNotIn("card-page-photo-link", main)
                self.assertNotIn('class="seo-watch-row"', main)
                self.assertIn("View larger photo:", main)
                actions = main.split('class="card-page-actions"', 1)[1]
                self.assertIn("card-watch-live", actions)
                self.assertIn("from=card", actions)
                self.assertIn("#habitat=", actions)
                print_tpl = study_print_html_for(cid)
                self.assertNotIn("card-page-photo-link", print_tpl)
                self.assertNotIn("card-page-photo-zoom", print_tpl)

        fish = _main((FP / "cards" / "freshwater-fish" / "index.html").read_text(encoding="utf-8"))
        self.assertNotIn("card-page-photo-link", fish)
        self.assertIn("card-page-photo-zoom", fish)
        self.assertIn('class="card-page-photo"', fish)
        self.assertLess(fish.find("card-page-photo"), fish.find("<h1>"))

        dino = _main((FP / "cards" / "sci-dinosaur" / "index.html").read_text(encoding="utf-8"))
        self.assertNotIn("card-page-photo-link", dino)
        self.assertNotIn("Watch Live", dino)
        self.assertNotIn("Watch live at", dino)


if __name__ == "__main__":
    unittest.main()
