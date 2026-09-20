"""Place-page chrome: Option A fork, sticky hunt bar, sparse labels."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from generate_bdo_seo import (  # noqa: E402
    CTA_AT_HOME,
    CTA_PRINT,
    CTA_SETUP_HUNT,
    CUSTOMIZE_SUMMARY_DEFAULT,
    FORK_GOING_TITLE,
    FORK_HOME_TITLE,
    HOME_EMPTY,
    HOME_SESSION_H2,
    HOME_SESSION_LEAD,
    HUNT_H2,
    HUNT_STYLE_CHALLENGE_LABEL,
    MISSION_CSS_VER,
    MISSION_DRAWER_H2,
    OFFER_SENTENCE,
    PLACE_VFT_CTA,
    PRINT_SPEC,
    SEO_CSS_VER,
    START_HERE_H2,
    START_HERE_LEAD,
    TYPE_HUB_LEAD,
    TYPE_LANDINGS,
    quiet_hero_lead,
)

FP = REPO / "static" / "field-pack"
GENERATOR = REPO / "scripts" / "generate_bdo_seo.py"
WORDY = (
    "Optional hunt for the visit",
    "Create and print your mission",
    "Print a hunt for the visit",
    "At home? Use the cards below",
    "Going in person?",
    "Talk through the cards",
    "no printer needed",
    "for rainy days",
    "Kid shortlist",
    "More if you have energy",
    "Sheet updates live",
    "Classic = first visit",
    "Open card — 6 talk questions",
)


def _visible(html: str) -> str:
    return html.split('id="venue-data"', 1)[0]


def _article(html: str) -> str:
    vis = _visible(html)
    return vis.split('<article class="seo-article">', 1)[1]


def _hero(html: str) -> str:
    return _article(html).split('class="seo-hero"', 1)[1].split("</header>", 1)[0]


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class PlacePageSparseChromeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dallas = (FP / "dallas-zoo" / "index.html").read_text(encoding="utf-8")
        cls.cairo = (FP / "cairo-zoo" / "index.html").read_text(encoding="utf-8")
        cls.yellowstone = (FP / "yellowstone" / "index.html").read_text(encoding="utf-8")
        cls.houston = (FP / "houston-zoo" / "index.html").read_text(encoding="utf-8")
        cls.gen = GENERATOR.read_text(encoding="utf-8")
        cls.pages = {
            "dallas-zoo": cls.dallas,
            "cairo-zoo": cls.cairo,
            "yellowstone": cls.yellowstone,
            "houston-zoo": cls.houston,
        }

    def test_generator_locks_sparse_strings(self):
        self.assertEqual(CTA_AT_HOME, "At home")
        self.assertEqual(CTA_PRINT, "Print")
        self.assertEqual(CTA_SETUP_HUNT, "Set up your hunt")
        self.assertEqual(FORK_GOING_TITLE, "Going soon")
        self.assertEqual(FORK_HOME_TITLE, "Not going yet")
        self.assertEqual(HOME_SESSION_H2, "Can't go this week? Watch and talk at home")
        self.assertEqual(START_HERE_H2, "Start here")
        self.assertEqual(START_HERE_LEAD, "")
        self.assertEqual(HUNT_H2, "Hunt")
        self.assertEqual(MISSION_DRAWER_H2, "Set up your hunt")
        self.assertEqual(HUNT_STYLE_CHALLENGE_LABEL, "Challenge")
        self.assertEqual(PLACE_VFT_CTA, "Virtual Field Trip")
        self.assertLessEqual(len(HOME_SESSION_LEAD), 56)
        self.assertEqual(HOME_EMPTY, "No cards for this place yet.")
        self.assertIn(OFFER_SENTENCE[:40], self.gen)
        self.assertIn('CTA_AT_HOME = "At home"', self.gen)
        self.assertIn('CTA_PRINT = "Print"', self.gen)
        self.assertIn("def hunt_teaser_html(", self.gen)
        self.assertIn("def quiet_hero_lead(", self.gen)
        self.assertNotIn('START_HERE_LEAD = (\n    "At home, open a card', self.gen)

    def test_quiet_hero_lead_drops_dual_mode_essays(self):
        self.assertEqual(
            quiet_hero_lead(
                {"blurb": "Explore Dallas Zoo at home with cards, photos, and talk prompts — or print a hunt for the visit."}
            ),
            "",
        )
        self.assertEqual(
            quiet_hero_lead({"blurb": "Giraffe Ridge feeding plus Penguin Cove and a hippo window."}),
            "Giraffe Ridge feeding plus Penguin Cove and a hippo window",
        )
        self.assertEqual(quiet_hero_lead({"blurb": ""}), "")

    def test_place_pages_drop_instructional_chrome(self):
        for slug, html in self.pages.items():
            article = _article(html)
            hero = _hero(html)
            with self.subTest(slug=slug):
                for phrase in WORDY:
                    self.assertNotIn(phrase, article, phrase)
                self.assertNotIn("seo-print-fallback", hero)
                self.assertNotIn("seo-secondary-links", hero)
                self.assertNotIn("seo-start-lead", article)
                self.assertNotIn("mission-filters-hint", html)
                self.assertNotIn("mission-hunt-hint", html)

    def test_hero_has_option_a_fork_and_offer(self):
        for slug, html in self.pages.items():
            hero = _hero(html)
            with self.subTest(slug=slug):
                self.assertIn(OFFER_SENTENCE, hero)
                self.assertIn("seo-fork", hero)
                self.assertIn(FORK_GOING_TITLE, hero)
                self.assertIn(FORK_HOME_TITLE, hero)
                self.assertIn('id="mission-open-btn"', hero)
                self.assertIn('data-how="going-soon"', hero)
                self.assertIn('data-how="not-going-yet"', hero)
                self.assertIn('href="#at-home"', hero)
                self.assertIn("seo-fork-print-spec", hero)
                self.assertIn("US Letter or A4", hero)
                # Print-spec only on Going soon card, not under explore card
                home_card = hero.split("seo-fork-home", 1)[1].split("</a>", 1)[0]
                self.assertNotIn("print-spec", home_card)
                self.assertNotIn("seo-customize-disclosure", hero)
                self.assertNotIn("Customize hunt", hero)
                leads = re.findall(r'class="lead"[^>]*>(.*?)</p>', hero, re.S)
                if leads:
                    self.assertLessEqual(len(_text(leads[0])), 90)

    def test_customize_after_stops_opens_modal(self):
        for slug, html in self.pages.items():
            visible = _visible(html)
            with self.subTest(slug=slug):
                self.assertIn("seo-customize-open", visible)
                self.assertIn(CUSTOMIZE_SUMMARY_DEFAULT, visible)
                self.assertIn('data-how="open-customize"', visible)
                # Customize sits after start-here
                start_i = visible.find('id="start-here"')
                cust_i = visible.find("seo-customize-open")
                self.assertGreater(start_i, 0)
                self.assertGreater(cust_i, start_i)

    def test_at_home_below_map_and_collapsed(self):
        for slug, html in self.pages.items():
            visible = _visible(html)
            with self.subTest(slug=slug):
                self.assertIn(f">{HOME_SESSION_H2}</span>", visible)
                self.assertIn('id="at-home"', visible)
                self.assertIn("seo-home-summary-count", visible)
                home_i = visible.find('id="at-home"')
                map_i = visible.find("seo-map")
                if map_i > 0:
                    self.assertGreater(home_i, map_i)
                # Collapsed details by default (no open attr on details opener)
                chunk = visible[max(0, home_i - 80) : home_i + 160]
                self.assertIn("<details", chunk)
                self.assertNotIn("<details open", chunk)
                self.assertIn('class="seo-home-session" id="at-home"', visible)
                self.assertIn(HOME_SESSION_LEAD, visible)
                self.assertIn(f">{PLACE_VFT_CTA}</a>", visible)

    def test_start_here_and_hunt_labels(self):
        for slug, html in self.pages.items():
            visible = _visible(html)
            with self.subTest(slug=slug):
                self.assertIn(f">{START_HERE_H2}</h2>", visible)
                self.assertIn(f">{HUNT_H2}</h2>", visible)
                hunt = visible.split('id="hunt-heading"', 1)[1].split("</section>", 1)[0]
                self.assertIn("seo-hunt-print-link", hunt)
                self.assertIn(CTA_SETUP_HUNT, hunt)
                self.assertIn('data-how="print-hunt"', hunt)
                self.assertNotIn('class="btn ', hunt)

    def test_print_spec_not_under_explore_path(self):
        for slug, html in self.pages.items():
            visible = _visible(html)
            with self.subTest(slug=slug):
                hunt = visible.split('id="hunt-heading"', 1)[1].split("</section>", 1)[0]
                self.assertNotIn('class="print-spec"', hunt)
                self.assertIn("seo-hunt-sticky", html)
                self.assertIn(PRINT_SPEC.replace("&", "&amp;") if False else "US Letter or A4", html)

    def test_empty_kit_stays_honest(self):
        cairo = _visible(self.cairo)
        self.assertIn("Starter list", cairo)
        self.assertIn(HOME_EMPTY, cairo)
        self.assertNotIn("We checked the animal list", cairo)
        start = cairo.split('id="route90-heading"', 1)[1].split("</section>", 1)[0]
        self.assertNotIn("/field-pack/cards/", start)
        self.assertIn("seo-start-emoji", start)
        home = cairo.split('id="at-home"', 1)[1].split("</details>", 1)[0]
        self.assertNotIn("seo-home-card", home)

    def test_verified_and_feedback_placement(self):
        dallas = _visible(self.dallas)
        self.assertIn("We checked the animal list, exhibit names, and map link in", dallas)
        self.assertIn("Starter list", _visible(self.houston))
        self.assertIn("🦁 Dallas Zoo", self.dallas)
        self.assertIn("seo-park-hero", self.yellowstone)
        # Feedback near official line (bottom), not in hero
        hero = _hero(self.dallas)
        self.assertNotIn("Was this list accurate?", hero)
        self.assertIn("Was this list accurate?", dallas)
        self.assertIn("seo-freshness-bottom", dallas)

    def test_drawer_challenge_label_and_setup(self):
        for slug, html in self.pages.items():
            with self.subTest(slug=slug):
                self.assertIn('id="mission-drawer"', html)
                self.assertIn('id="mission-print-btn"', html)
                self.assertIn(f'id="mission-heading">{MISSION_DRAWER_H2}</h2>', html)
                self.assertIn(f'id="mission-print-btn">{CTA_PRINT}</button>', html)
                self.assertIn('id="mission-who-seg"', html)
                self.assertIn('id="mission-time-seg"', html)
                self.assertIn('id="mission-hunt-seg"', html)
                self.assertRegex(html, r">\s*Challenge\s*<")
                self.assertIn('data-hunt="alpha"', html)
                self.assertIn(HUNT_STYLE_CHALLENGE_LABEL, html)
                self.assertIn("Hunt style", html)
                self.assertIn("/start/", html)
                self.assertIn('href="/field-pack/">All places</a>', html)

    def test_brand_and_explorer_paths_unchanged(self):
        for html in self.pages.values():
            self.assertIn('class="shell-brand" href="/start/"', html)
            self.assertIn('class="shell-product" href="/start/"', html)
            self.assertIn('href="/field-pack/">All places</a>', html)
            self.assertIn('href="/field-pack/virtual-field-trip/', html)
            self.assertIn(f"seo-venue.css?v={SEO_CSS_VER}", html)
            self.assertIn(f"mission.css?v={MISSION_CSS_VER}", html)

    def test_type_hubs_share_the_same_sparse_shell(self):
        self.assertEqual(TYPE_HUB_LEAD, HOME_SESSION_LEAD)
        for meta in TYPE_LANDINGS:
            self.assertEqual(meta["blurb"], TYPE_HUB_LEAD)
            self.assertEqual(meta["h1"], meta["nav"])
            self.assertLessEqual(len(meta["h1"]), 12)
        for path in ("zoos", "aquariums", "museums", "national-parks"):
            html = (FP / path / "index.html").read_text(encoding="utf-8")
            with self.subTest(hub=path):
                self.assertIn(f">{CTA_AT_HOME}</a>", html)
                self.assertIn(">Map</a>", html)
                self.assertNotIn("Print a hunt for the visit", html)
                self.assertNotIn("Explore a zoo at home", html)
                self.assertNotIn("optional hunt", html.lower())
                self.assertIn('href="/field-pack/virtual-field-trip/"', html)


if __name__ == "__main__":
    unittest.main()
