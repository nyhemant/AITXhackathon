"""KZK (kidzookit.com) /start/ landing pass, 2026-11-18: identity lockup, 'Pin -> printed hunt' demo, a11y fixes."""
import html
import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
START = REPO / "static" / "start" / "index.html"
ABOUT = REPO / "static" / "about" / "index.html"
SLUG = "perot-museum"


def _demo(page: str) -> str:
    m = re.search(r'<div class="hx-demo" id="hx-demo">([\s\S]*?)\n    </div>\n  </div>', page)
    assert m, "demo block missing"
    return m.group(1)


def _css(page: str) -> str:
    return re.search(r'<style id="hx-demo-css">([\s\S]*?)</style>', page).group(1)


class StartWowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = START.read_text(encoding="utf-8")
        cls.demo = _demo(cls.page)
        cls.css = _css(cls.page)

    # --- identity -----------------------------------------------------------------------
    def test_project_name_stays_on_start_and_about(self):
        # Owner decision 2026-10-23: Arya’s Wildlife Project stays on /start/ and /about/.
        self.assertIn('<p class="start-wordmark">Arya’s Wildlife Project</p>', self.page)
        self.assertIn("Arya’s Wildlife Project", ABOUT.read_text(encoding="utf-8"))
        header = re.search(r'<header class="start-top">([\s\S]*?)</header>', self.page).group(1)
        self.assertIn('<div class="start-idlock"><p class="start-wordmark">Arya’s Wildlife Project</p><p class="start-idsite">KidZooKit</p></div>', header)

    def test_one_headline_and_title_unchanged(self):
        self.assertEqual(self.page.count("<h1"), 1)
        self.assertIn('<h1 id="start-heading">Printable scavenger hunts for your next zoo, aquarium or museum trip</h1>', self.page)
        self.assertNotIn('id="home-hunts-tagline"', self.page)
        self.assertIn("<title>Zoo, Aquarium &amp; Museum Scavenger Hunts for Kids | KidZooKit</title>", self.page)
        self.assertIn('<section id="home-hunts" class="home-hunts" aria-labelledby="start-heading">', self.page)

    # --- demo shows only what the product really returns ----------------------------------
    def test_demo_sheet_matches_the_real_hunt(self):
        venue = json.loads((REPO / "static/field-pack/data/venues" / f"{SLUG}.json").read_text(encoding="utf-8"))
        pin = re.search(r'data-home-pin="perot-museum" data-members="([^"]+)".*?<span class="kzm-tag" aria-hidden="true">([^<]+)</span>', self.page)
        members = json.loads(html.unescape(pin.group(1)))
        self.assertEqual(members[0]["slug"], SLUG)
        self.assertEqual(members[0]["name"], venue["name"])
        label = pin.group(2)
        hunt_page = (REPO / "static/field-pack" / SLUG / "index.html").read_text(encoding="utf-8")
        block = hunt_page[hunt_page.index('id="printable-hunt"'):]
        first = html.unescape(re.search(r"☐</span><span>([^<—]+?) —", block).group(1))
        stops = re.search(r"A (\d+)-stop hunt", block).group(1)
        sheet = re.search(r'<a class="hxd-sheet" data-kz-cta="home-demo" href="([^"]+)">([\s\S]*?)</a>', self.demo)
        self.assertEqual(sheet.group(1), f"/field-pack/{SLUG}/#printable-hunt")
        body = sheet.group(2)
        self.assertIn(f'<span class="hxd-k">{stops}-stop hunt</span>', body)
        self.assertIn(f'<span class="hxd-t">{html.escape(label)}</span>', body)
        self.assertIn(f"</span>{html.escape(first)}</span>", body)
        self.assertIn(f">{html.escape(label)}</text>", self.demo)  # mini-map tag says the same place
        self.assertIn('id="printable-hunt"', hunt_page)

    def test_demo_venue_is_outside_the_scav_test(self):
        from scripts import scav_test_2026_11 as scav
        self.assertNotIn(SLUG, scav.TEST_SLUGS)
        self.assertNotIn(SLUG, scav.COMPARISON_SLUGS)

    # --- build rules ------------------------------------------------------------------------
    def test_css_svg_only_plays_once_and_reduced_motion_is_final_frame(self):
        self.assertNotIn("<img", self.demo)
        self.assertNotIn("<video", self.demo)
        self.assertNotIn("<canvas", self.demo)
        self.assertNotIn("infinite", self.css)
        self.assertIn("@media (prefers-reduced-motion: reduce)", self.css)
        self.assertIn(".hx-demo *, .kzm.kzm-pop .home-place-pin, .kzm.kzm-pop .home-place-pin::after { animation: none !important; }", self.css)
        # Defaults are the final frame: the tick is drawn and the sheet sits out of the printer.
        self.assertIn("stroke-dashoffset: 0; animation: hxd-tick", self.css)
        self.assertRegex(self.css, r"\.hx-demo \{[^}]*height: 190px")
        self.assertNotRegex(self.css, r"position:\s*(sticky|fixed)")
        # Pins only animate opacity and scale.
        pop = re.search(r"@keyframes kzm-pop \{([^\n]*)\}", self.css).group(1)
        self.assertEqual(set(re.findall(r"([a-z-]+):", pop)), {"opacity", "scale"})
        js = re.findall(r"<script>([^<]*)</script>", self.page)
        self.assertEqual(len(js), 1)
        self.assertLess(len(js[0]), 1500)
        self.assertIn('classList.remove("kzm-pop")', js[0])

    def test_decorative_svg_hidden_and_one_named_link(self):
        for svg in re.findall(r"<svg[^>]*>", self.demo):
            self.assertIn('aria-hidden="true"', svg)
            self.assertIn('focusable="false"', svg)
        for inner in re.findall(r"<svg[\s\S]*?</svg>", self.demo):
            self.assertNotRegex(inner, r"<a |tabindex|<button")
        self.assertEqual(len(re.findall(r"<a ", self.demo)), 1)
        self.assertIn('<ol class="hxd-steps" aria-label="How it works">', self.demo)

    def test_copy_rules(self):
        text = re.sub(r"<[^>]+>", " ", self.demo + re.search(r'<div class="hx-head">([\s\S]*?)</div>', self.page).group(1))
        self.assertNotRegex(text.lower(), r"\bfree\b|no-cost|\bwe\b|\bour\b|\bus\b")

    # --- the three Lighthouse a11y failures -----------------------------------------------
    def test_no_focusable_inside_aria_hidden(self):
        for block in re.findall(r'<div class="start-chapter-line" aria-hidden="true">([\s\S]*?)</div>', self.page):
            self.assertNotIn("tabindex", block)

    def test_teach_slides_have_names(self):
        for slug, name in (("african-lion", "Lion"), ("african-elephant", "Elephant"), ("reticulated-giraffe", "Giraffe")):
            self.assertIn(f'<a class="start-teach-slide" href="/field-pack/cards/{slug}/"><span class="sr-only">{name} card</span>', self.page)

    def test_pin_names_contain_visible_text(self):
        pins = re.findall(r'data-home-pin="[^"]+" data-members="([^"]+)" aria-label="([^"]+)".*?<span class="kzm-tag" aria-hidden="true">(.*?)</span></button>', self.page)
        self.assertGreaterEqual(len(pins), 16)
        for members, aria, tag in pins:
            shown = html.unescape(re.sub(r"<[^>]+>", "", tag.replace("<br>", " ")))
            self.assertIn(re.sub(r"\s+", " ", shown).strip().lower(), html.unescape(aria).lower(), aria)
            m = json.loads(html.unescape(members))
            label = html.unescape(tag.split("<b>")[0]).replace("<br>", " ").strip()
            full = f"{m[0]['name']}, {m[0]['city']}"
            want = f"{label} {len(m)} places" if len(m) > 1 else (full if label.lower() in full.lower() else f"{label} ({m[0]['name']}), {m[0]['city']}")
            self.assertEqual(html.unescape(aria), want)  # same rule as scripts/map-v2/build_map_v2.mjs
        gen = (REPO / "scripts/map-v2/build_map_v2.mjs").read_text(encoding="utf-8")
        self.assertIn("`${shown} ${n} places`", gen)
        self.assertIn("` <b>${n}</b>`", gen)

    def test_flamingo_link_named_by_its_heading_content(self):
        self.assertIn('id="start-wildlife-hit" href="/field-pack/virtual-field-trip/?tab=zoo#habitat=caribbean-flamingo">', self.page)


if __name__ == "__main__":
    unittest.main()
