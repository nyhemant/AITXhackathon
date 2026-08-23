"""Flagship at-home session: honest start-here, 6-Q cards, no notice-stubs."""

from collections import Counter
from pathlib import Path
import json
import re
import sys
import unittest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
FP = REPO / "static" / "field-pack"


class FlagshipSessionTests(unittest.TestCase):
    def test_map_count_never_places_loading(self):
        html = (FP / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("Places loading", html)
        self.assertIn("218 places worldwide", html)
        self.assertIn("<noscript><p class=\"map-count-quiet\">218 places worldwide</p></noscript>", html)
        self.assertIn('href="/field-pack/dallas-zoo/#mission"', html)
        self.assertIn(
            "Use the at-home cards and session together; print is optional for a group visit.",
            html,
        )
        self.assertNotIn("Print one sheet per child or share one for the group.", html)

    def _visible(self, html: str) -> str:
        return html.split('id="venue-data"', 1)[0]

    def test_dallas_start_here_is_dual_cta(self):
        html = (FP / "dallas-zoo" / "index.html").read_text(encoding="utf-8")
        visible = self._visible(html)
        self.assertIn("Talk at home", visible)
        self.assertIn("Add to hunt", visible)
        self.assertIn('href="/field-pack/cards/reticulated-giraffe/?from=dallas-zoo"', visible)
        self.assertIn('href="/field-pack/cards/african-elephant/?from=dallas-zoo"', visible)
        self.assertIn('href="/field-pack/cards/african-lion/?from=dallas-zoo"', visible)
        self.assertIn('data-how="print-hunt"', visible)
        self.assertIn("This zoo's cards", visible)
        self.assertIn('href="#at-home"', visible)
        start = visible.split('id="route90-heading"', 1)[1].split("</section>", 1)[0]
        self.assertNotIn('class="seo-start-card" href="#mission"', start)
        self.assertNotIn("What did you notice about", visible)
        self.assertIn('id="mission"', html)
        self.assertIn('id="print"', html)
        self.assertIn('id="mission-drawer"', html)
        ui = (FP / "js" / "mission" / "mission-ui.js").read_text(encoding="utf-8")
        self.assertIn('h === "#mission"', ui)
        self.assertIn('h === "#print"', ui)
        self.assertIn('h === "#mission-drawer"', ui)

    def test_san_diego_start_here_is_dual_cta(self):
        html = (FP / "san-diego-zoo" / "index.html").read_text(encoding="utf-8")
        visible = self._visible(html)
        self.assertIn("Talk at home", visible)
        self.assertIn("Add to hunt", visible)
        self.assertIn('href="/field-pack/cards/giant-panda/?from=san-diego-zoo"', visible)
        self.assertIn('href="/field-pack/cards/koala/?from=san-diego-zoo"', visible)
        self.assertIn("This zoo's cards", visible)
        self.assertNotIn("What did you notice about the Koala?", visible)

    def test_lion_card_has_outing_six_and_cam(self):
        html = (FP / "cards" / "african-lion" / "index.html").read_text(encoding="utf-8")
        for q in (
            "What do they eat?",
            "Where is home?",
            "What is their superpower?",
            "Baby or grown-up?",
            "Did we see one live?",
            "I want to teach about…",
        ):
            self.assertIn(q, html)
        self.assertIn("nationalzoo.si.edu/webcams/lion-cam", html)
        self.assertIn("Print this card", html)
        self.assertNotIn("Open in outing view", html)
        self.assertNotIn("What did you notice about", html)
        # VFT stop may have a challenge; it does not own card facts.
        self.assertNotIn("Why does a lion have a mane?", html)
        self.assertNotIn("A pride is a family that hunts and raises cubs together.", html)

    def test_flagship_cards_reuse_vft_cams_when_present(self):
        expect = {
            "reticulated-giraffe": "houstonzoo.org/explore/webcams/giraffe-feeding-platform",
            "african-elephant": "nationalzoo.si.edu/webcams/elephants",
            "african-lion": "nationalzoo.si.edu/webcams/lion-cam",
            "giant-panda": "nationalzoo.si.edu/webcams/panda-cam",
            "african-penguin": "zoo.sandiegozoo.org/cams/penguin-cam",
        }
        for cid, needle in expect.items():
            html = (FP / "cards" / cid / "index.html").read_text(encoding="utf-8")
            self.assertIn(needle, html, cid)
            self.assertIn("What do they eat?", html)
        koala = (FP / "cards" / "koala" / "index.html").read_text(encoding="utf-8")
        self.assertIn("What do they eat?", koala)
        self.assertNotIn("What did you notice about the Koala?", koala)

    def _card_chrome(self, html: str) -> str:
        venue = ""
        actions = ""
        if 'class="card-page-venue"' in html:
            venue = html.split('class="card-page-venue"', 1)[1].split("</p>", 1)[0]
        if 'class="card-page-actions"' in html:
            actions = html.split('class="card-page-actions"', 1)[1].split("</p>", 1)[0]
        return venue + "\n" + actions

    def test_shared_animal_cards_have_no_home_zoo_chrome(self):
        """Gorilla / panda cards are shared — no other zoo's name in page chrome."""
        gorilla = (FP / "cards" / "western-lowland-gorilla" / "index.html").read_text(encoding="utf-8")
        panda = (FP / "cards" / "giant-panda" / "index.html").read_text(encoding="utf-8")
        seahorse = (FP / "cards" / "seahorse" / "index.html").read_text(encoding="utf-8")

        for html, cid in (
            (gorilla, "western-lowland-gorilla"),
            (panda, "giant-panda"),
            (seahorse, "seahorse"),
        ):
            chrome = self._card_chrome(html)
            self.assertIn("At-home card", chrome, cid)
            self.assertNotIn("Place page", chrome, cid)
            self.assertNotIn("This zoo's cards", chrome, cid)
            self.assertNotIn("This aquarium's cards", chrome, cid)
            for name in (
                "Dallas Zoo",
                "Houston Zoo",
                "San Diego Zoo",
                "National Zoo",
                "Smithsonian",
                "Fort Worth Zoo",
                "Children's Aquarium",
            ):
                self.assertNotIn(name, chrome, f"{cid} chrome names {name}")
            self.assertNotIn("/field-pack/dallas-zoo/", chrome, cid)
            self.assertNotIn("/field-pack/houston-zoo/", chrome, cid)
            self.assertNotIn("/field-pack/san-diego-zoo/", chrome, cid)
            self.assertNotIn("/field-pack/national-zoo/", chrome, cid)

        houston = self._visible((FP / "houston-zoo" / "index.html").read_text(encoding="utf-8"))
        san_diego = self._visible((FP / "san-diego-zoo" / "index.html").read_text(encoding="utf-8"))
        national = self._visible((FP / "national-zoo" / "index.html").read_text(encoding="utf-8"))
        self.assertIn("Houston Zoo", houston)
        self.assertIn("San Diego Zoo", san_diego)
        self.assertIn("National Zoo", national)
        self.assertIn('href="/field-pack/cards/western-lowland-gorilla/?from=houston-zoo"', houston)
        self.assertIn('href="/field-pack/cards/giant-panda/?from=san-diego-zoo"', san_diego)
        self.assertIn('href="/field-pack/cards/giant-panda/?from=national-zoo"', national)

        art = self._card_chrome((FP / "cards" / "cm-art-lab" / "index.html").read_text(encoding="utf-8"))
        towpath = self._card_chrome(
            (FP / "cards" / "cuyahoga-towpath" / "index.html").read_text(encoding="utf-8")
        )
        bison = self._card_chrome(
            (FP / "cards" / "american-bison" / "index.html").read_text(encoding="utf-8")
        )
        rocket = self._card_chrome((FP / "cards" / "sci-rocket" / "index.html").read_text(encoding="utf-8"))
        self.assertIn("Perot Museum", art)
        self.assertIn("Place page", art)
        self.assertIn("Cuyahoga Valley", towpath)
        self.assertIn("Yellowstone", bison)
        self.assertIn("CA Science Center", rocket)

    def test_dallas_real_qa_kept_generic_notice_not_shipped(self):
        dallas = self._visible((FP / "dallas-zoo" / "index.html").read_text(encoding="utf-8"))
        giraffe = (FP / "cards" / "reticulated-giraffe" / "index.html").read_text(encoding="utf-8")
        self.assertIn("How does a giraffe drink water?", giraffe)
        self.assertIn("What does an elephant use its trunk for?", (FP / "cards" / "african-elephant" / "index.html").read_text(encoding="utf-8"))
        self.assertNotIn("What did you notice about", dallas)
        self.assertNotIn("A long neck reaches high leaves.", dallas)
        self.assertNotIn("Why can’t penguins fly?", dallas)

    def test_dinner_route_still_defined(self):
        web = (REPO / "src" / "busyparent_agent" / "web.py").read_text(encoding="utf-8")
        self.assertIn('DINNER_PATH = "/dinner"', web)

    def test_hub_towpath_is_parks_not_wildlife(self):
        hub = (FP / "cards" / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="cards-parks"', hub)
        self.assertIn('data-card-id="cuyahoga-towpath"', hub)
        self.assertIn('data-card-kind="place_feature"', hub)
        wildlife = hub.split('id="cards-wildlife"', 1)[1].split('id="cards-', 1)[0]
        parks = hub.split('id="cards-parks"', 1)[1].split("</section>", 1)[0]
        self.assertNotIn("cuyahoga-towpath", wildlife)
        self.assertIn("cuyahoga-towpath", parks)
        self.assertIn('data-card-filter="parks"', hub)

    def test_art_lab_renders_perot_attribution(self):
        html = (FP / "cards" / "cm-art-lab" / "index.html").read_text(encoding="utf-8")
        self.assertIn("· Perot Museum", html)
        self.assertIn("/field-pack/childrens-museum-perot/#at-home", html)
        self.assertNotIn("This zoo's cards", html)
        self.assertIn("This museum's cards", html)
        hub = (FP / "cards" / "index.html").read_text(encoding="utf-8")
        art = [line for line in hub.splitlines() if "cm-art-lab" in line][0]
        self.assertIn("Perot Museum", art)

    def test_lion_card_keeps_chip_labels_without_home_zoo_cta(self):
        html = (FP / "cards" / "african-lion" / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("This zoo's cards", html)
        self.assertIn("Explore at home", html)
        self.assertIn("Meat", html)
        self.assertIn("Run fast", html)
        dallas = self._visible((FP / "dallas-zoo" / "index.html").read_text(encoding="utf-8"))
        self.assertIn("This zoo's cards", dallas)
        css = (FP / "css" / "styles.css").read_text(encoding="utf-8")
        seo = (FP / "css" / "seo-venue.css").read_text(encoding="utf-8")
        self.assertIn("overflow-wrap: anywhere", css)
        self.assertIn(".card-page .card-talk-pack .mission-grid", seo)
        self.assertIn("grid-template-columns: 1fr", seo)

    def test_dallas_start_here_is_above_at_home_dump(self):
        visible = self._visible((FP / "dallas-zoo" / "index.html").read_text(encoding="utf-8"))
        start = visible.find('id="route90-heading"')
        dump = visible.find('id="at-home"')
        self.assertNotEqual(start, -1)
        self.assertNotEqual(dump, -1)
        self.assertLess(start, dump)
        start_block = visible.split('id="route90-heading"', 1)[1].split("</section>", 1)[0]
        self.assertIn("Reticulated giraffe", start_block)
        self.assertIn("African elephant", start_block)
        self.assertIn("African lion", start_block)

    def test_dallas_giraffe_card_has_next_elephant(self):
        html = (FP / "cards" / "reticulated-giraffe" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Next: African elephant", html)
        self.assertIn('href="/field-pack/cards/african-elephant/?from=dallas-zoo"', html)
        dallas = self._visible((FP / "dallas-zoo" / "index.html").read_text(encoding="utf-8"))
        start = dallas.split('id="route90-heading"', 1)[1].split("</section>", 1)[0]
        self.assertIn("/field-pack/cards/african-elephant/?from=dallas-zoo", start)
        sd = self._visible((FP / "san-diego-zoo" / "index.html").read_text(encoding="utf-8"))
        sd_start = sd.split('id="route90-heading"', 1)[1].split("</section>", 1)[0]
        self.assertNotIn("from=dallas-zoo", sd_start)

    def test_elephant_next_lion_only_from_dallas(self):
        html = (FP / "cards" / "african-elephant" / "index.html").read_text(encoding="utf-8")
        self.assertIn('class="card-page-next" hidden data-next-from="dallas-zoo"', html)
        self.assertIn("Next: African lion", html)
        self.assertIn('get("from")', html)
        self.assertIn('from === nextEl.getAttribute("data-next-from")', html)
        show = lambda q: q == "dallas-zoo"
        self.assertFalse(show(None))
        self.assertFalse(show("san-diego-zoo"))
        self.assertTrue(show("dallas-zoo"))
        koala = (FP / "cards" / "koala" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Next: African elephant", koala)
        self.assertIn("from=san-diego-zoo", koala)
        self.assertNotIn("from=dallas-zoo", koala)

    def test_national_panda_next_is_otter_not_koala(self):
        """Shared panda card: National Start here → otter; San Diego → koala."""
        national = self._visible((FP / "national-zoo" / "index.html").read_text(encoding="utf-8"))
        start = national.split('id="route90-heading"', 1)[1].split("</section>", 1)[0]
        self.assertIn("/field-pack/cards/giant-panda/?from=national-zoo", start)
        self.assertNotIn("from=san-diego-zoo", start)

        panda = (FP / "cards" / "giant-panda" / "index.html").read_text(encoding="utf-8")
        self.assertIn('class="card-page-next" hidden data-next-from="national-zoo"', panda)
        self.assertIn('href="/field-pack/cards/asian-small-clawed-otter/?from=national-zoo"', panda)
        self.assertIn("Next: Asian small-clawed otter", panda)
        self.assertIn('class="card-page-next" hidden data-next-from="san-diego-zoo"', panda)
        self.assertIn('href="/field-pack/cards/koala/?from=san-diego-zoo"', panda)
        self.assertIn("Next: Koala", panda)

        def shown_next(from_q: str | None) -> str:
            import re as _re

            shown = []
            for m in _re.finditer(
                r'<p class="card-page-next"([^>]*)><a href="([^"]+)">Next: ([^<]+)</a></p>',
                panda,
            ):
                attrs, href, label = m.group(1), m.group(2), m.group(3)
                hidden = " hidden" in f" {attrs} "
                data_from = ""
                dm = _re.search(r'data-next-from="([^"]+)"', attrs)
                if dm:
                    data_from = dm.group(1)
                if hidden and from_q != data_from:
                    continue
                shown.append((label, href))
            return shown

        self.assertEqual(
            shown_next("national-zoo"),
            [("Asian small-clawed otter", "/field-pack/cards/asian-small-clawed-otter/?from=national-zoo")],
        )
        self.assertEqual(
            shown_next("san-diego-zoo"),
            [("Koala", "/field-pack/cards/koala/?from=san-diego-zoo")],
        )
        self.assertEqual(shown_next(None), [])
        self.assertEqual(shown_next("houston-zoo"), [])

        sd = self._visible((FP / "san-diego-zoo" / "index.html").read_text(encoding="utf-8"))
        sd_start = sd.split('id="route90-heading"', 1)[1].split("</section>", 1)[0]
        self.assertIn("/field-pack/cards/giant-panda/?from=san-diego-zoo", sd_start)

    def test_houston_gorilla_card_chrome_is_not_dallas(self):
        """Houston gorilla Print / Learn more must not stamp Dallas Zoo."""
        houston = self._visible((FP / "houston-zoo" / "index.html").read_text(encoding="utf-8"))
        start = houston.split('id="route90-heading"', 1)[1].split("</section>", 1)[0]
        self.assertIn("/field-pack/cards/western-lowland-gorilla/?from=houston-zoo", start)

        gorilla = (FP / "cards" / "western-lowland-gorilla" / "index.html").read_text(encoding="utf-8")
        chrome = self._card_chrome(gorilla)
        self.assertNotIn("dallas-zoo", chrome)
        self.assertNotIn("dallaszoo.com", chrome)
        self.assertNotIn('data-venue="dallas-zoo"', gorilla)
        more = gorilla.split("detail-links", 1)[1].split("</div>", 1)[0]
        self.assertNotIn("dallaszoo.com", more)
        self.assertNotIn("dallas-zoo", more)
        self.assertIn("card-learn-more", gorilla)
        self.assertIn("Next: Chimpanzee", gorilla)
        self.assertIn('href="/field-pack/cards/chimpanzee/?from=houston-zoo"', gorilla)
        self.assertIn('"houston-zoo":"https://www.houstonzoo.org/"', gorilla)

        from generate_bdo_seo import is_place_site_url

        self.assertTrue(is_place_site_url("https://www.dallaszoo.com/"))
        self.assertTrue(is_place_site_url("https://nationalzoo.si.edu/animals/giant-panda"))
        self.assertFalse(is_place_site_url("https://kids.nationalgeographic.com/animals/mammals/facts/mountain-gorilla"))

    def test_cousin_cam_first_visible_line_names_source_zoo(self):
        html = (FP / "cards" / "reticulated-giraffe" / "index.html").read_text(encoding="utf-8")
        watch = html.split('class="seo-watch-row"', 1)[1].split("</p>", 1)[0]
        first_link = watch.split("<a", 1)[1].split("</a>", 1)[0]
        source = first_link.split('class="seo-watch-source"', 1)[1].split(">", 1)[1].split("<", 1)[0].strip()
        self.assertEqual(source, "Live from Houston Zoo")
        self.assertLess(first_link.find("Live from Houston Zoo"), first_link.find("Giraffe cam at the Houston Zoo"))
        self.assertNotIn("Dallas", source)

    def test_dallas_does_not_duplicate_more_if_you_have_energy(self):
        visible = self._visible((FP / "dallas-zoo" / "index.html").read_text(encoding="utf-8"))
        self.assertNotIn("More if you have energy", visible)
        self.assertIn("Optional hunt for the visit", visible)
        self.assertIn('id="at-home"', visible)

    def test_landing_featured_skips_illustration_heroes(self):
        landing = (FP / "index.html").read_text(encoding="utf-8")
        grid = landing.split('id="cat-card-grid"', 1)[1].split("</ul>", 1)[0]
        self.assertNotIn("cm-art-lab", grid)
        self.assertNotIn("cm-woven", grid)
        self.assertNotIn("cm-makery", grid)
        self.assertNotIn("sci-dinosaur", grid)
        self.assertNotIn("sci-rocket", grid)

    def test_giraffe_next_is_before_talk_pack(self):
        html = (FP / "cards" / "reticulated-giraffe" / "index.html").read_text(encoding="utf-8")
        next_at = html.find("Next: African elephant")
        talk_at = html.find('class="card-talk-pack"')
        watch_at = html.find('class="seo-watch-row"')
        self.assertNotEqual(next_at, -1)
        self.assertNotEqual(talk_at, -1)
        self.assertLess(watch_at, next_at)
        self.assertLess(next_at, talk_at)
        elephant = (FP / "cards" / "african-elephant" / "index.html").read_text(encoding="utf-8")
        self.assertLess(
            elephant.find('class="card-page-next" hidden data-next-from="dallas-zoo"'),
            elephant.find('class="card-talk-pack"'),
        )

    def test_phone_session_css_locks(self):
        seo = (FP / "css" / "seo-venue.css").read_text(encoding="utf-8")
        mission = (FP / "css" / "mission.css").read_text(encoding="utf-8")
        self.assertIn("overflow-x: clip", seo)
        self.assertIn("safe-area-inset-top", seo)
        self.assertIn("safe-area-inset-bottom", seo)
        self.assertIn("safe-area-inset-left", seo)
        self.assertIn(".seo-start-here", seo)
        self.assertIn("scroll-margin-top: calc(10rem + env(safe-area-inset-top, 0px))", seo)
        self.assertIn(".seo-start-talk", seo)
        self.assertIn(".card-page-next a", seo)
        self.assertIn("min-height: 44px", seo)
        self.assertIn(".card-page-next {\n  order: 1;", seo)
        self.assertIn("safe-area-inset-top", mission)
        self.assertIn("min-width: 44px", mission)
        self.assertIn("min-height: 44px", mission)
        dallas = (FP / "dallas-zoo" / "index.html").read_text(encoding="utf-8")
        giraffe = (FP / "cards" / "reticulated-giraffe" / "index.html").read_text(encoding="utf-8")
        landing = (FP / "index.html").read_text(encoding="utf-8")
        self.assertIn("viewport-fit=cover", dallas)
        self.assertIn("viewport-fit=cover", giraffe)
        self.assertIn("viewport-fit=cover", landing)
        self.assertIn("Live from Houston Zoo", giraffe)

    def _css_rule(self, css: str, selector: str) -> str:
        needle = selector + " {"
        start = css.find(needle)
        self.assertNotEqual(start, -1, selector)
        end = css.find("}", start)
        self.assertNotEqual(end, -1, selector)
        return css[start : end + 1]

    def test_place_page_card_photos_are_square(self):
        """Start here + at-home/shortlist thumbs are 1:1; park hero stays a scene."""
        seo = (FP / "css" / "seo-venue.css").read_text(encoding="utf-8")
        start_img = self._css_rule(seo, ".seo-start-card img")
        animal_img = self._css_rule(seo, ".seo-animal-card img")
        home_img = self._css_rule(seo, ".seo-home-card-media img")
        park_hero = self._css_rule(seo, ".seo-park-hero")
        for rule in (start_img, animal_img, home_img):
            self.assertIn("aspect-ratio: 1 / 1", rule)
            self.assertIn("object-fit: cover", rule)
            self.assertNotIn("height: 132px", rule)
            self.assertNotIn("height: 120px", rule)
            self.assertNotIn("aspect-ratio: 16 / 10", rule)
        self.assertIn("aspect-ratio: 16 / 9", park_hero)
        self.assertNotIn(".seo-animal-card img, .seo-hero-photos img { height: 160px; }", seo)
        self.assertIn("min-height: 44px", seo)
        self.assertIn(".seo-start-talk", seo)
        self.assertIn(".card-page-next a", seo)

        # Shared selectors (not zoo-only) cover every place-page venue type.
        self.assertNotIn("zoo-start-card", seo)
        self.assertNotIn("zoo-animal-card", seo)

        for slug in (
            "dallas-zoo",
            "houston-zoo",
            "monterey-bay-aquarium",
            "perot-museum",
            "yellowstone",
        ):
            page = self._visible((FP / slug / "index.html").read_text(encoding="utf-8"))
            start = page.split('id="route90-heading"', 1)[1].split("</section>", 1)[0]
            home = page.split('id="at-home"', 1)[1].split("</section>", 1)[0]
            self.assertIn('width="640" height="640"', start, slug)
            self.assertIn('width="640" height="640"', home, slug)
            self.assertNotIn('width="640" height="400"', start, slug)
            self.assertNotIn('width="640" height="400"', home, slug)

        dallas = self._visible((FP / "dallas-zoo" / "index.html").read_text(encoding="utf-8"))
        start = dallas.split('id="route90-heading"', 1)[1].split("</section>", 1)[0]
        self.assertIn('style="object-position: 50% 18%"', start)
        self.assertIn("photos/reticulated-giraffe.jpg", start)

        houston = self._visible((FP / "houston-zoo" / "index.html").read_text(encoding="utf-8"))
        houston_start = houston.split('id="route90-heading"', 1)[1].split("</section>", 1)[0]
        self.assertLess(
            houston_start.find("western-lowland-gorilla"),
            houston_start.find("chimpanzee"),
        )
        self.assertLess(
            houston_start.find("chimpanzee"),
            houston_start.find("african-lion"),
        )

        yellowstone = (FP / "yellowstone" / "index.html").read_text(encoding="utf-8")
        self.assertIn('class="seo-park-hero', yellowstone)
        self.assertIn('width="1280" height="720"', yellowstone)

        card = (FP / "cards" / "reticulated-giraffe" / "index.html").read_text(encoding="utf-8")
        self.assertIn('class="card-page-photo"', card)
        self.assertIn('width="640" height="640"', card)
        self.assertIn("aspect-ratio: 1 / 1", card)
        self.assertIn("object-fit: cover", card)
        self.assertIn('style="object-position: 50% 18%"', card)

        from generate_bdo_seo import _card_thumb_img, _photo_position

        self.assertEqual(_photo_position({"photoPosition": "50% 18%"}), "50% 18%")
        self.assertEqual(_photo_position({"photoFocus": "center top"}), "center top")
        self.assertEqual(_photo_position({"photoPosition": "url(evil)"}), "")
        self.assertIn('width="640" height="640"', _card_thumb_img("photos/x.jpg", pos="50% 22%"))
        self.assertIn('style="object-position: 50% 22%"', _card_thumb_img("photos/x.jpg", pos="50% 22%"))
        self.assertNotIn("object-position", _card_thumb_img("photos/x.jpg"))

    def test_every_catalog_place_page_uses_shared_square_frames(self):
        """Zoo, aquarium, museum, and park place pages all share the 1:1 card rules."""
        from generate_bdo_seo import venue_type_kind

        seo = (FP / "css" / "seo-venue.css").read_text(encoding="utf-8")
        self.assertNotRegex(seo, r"\.(zoo|aquarium|museum)-start-card")
        self.assertNotRegex(seo, r"\.(zoo|aquarium|museum)-animal-card")
        self.assertNotRegex(seo, r"\.(zoo|aquarium|museum)-home-card")
        self.assertNotIn("data-venue-type", seo)
        self.assertIn(".seo-start-card img", seo)
        self.assertIn(".seo-home-card-media img", seo)
        self.assertIn(".seo-animal-card img", seo)

        img_wh = re.compile(r'width="(\d+)" height="(\d+)"')
        kinds = Counter()
        for path in sorted((FP / "data" / "venues").glob("*.json")):
            venue = json.loads(path.read_text(encoding="utf-8"))
            slug = venue.get("slug") or path.stem
            kind = venue_type_kind(venue)
            kinds[kind] += 1
            html = (FP / slug / "index.html").read_text(encoding="utf-8")
            visible = self._visible(html)
            self.assertIn("seo-venue.css?v=28", html, slug)
            start = visible.split('id="route90-heading"', 1)[1].split("</section>", 1)[0]
            home = visible.split('id="at-home"', 1)[1].split("</section>", 1)[0]
            for label, block in (("start", start), ("home", home)):
                dims = img_wh.findall(block)
                if dims:
                    self.assertTrue(
                        all(dim == ("640", "640") for dim in dims),
                        f"{kind}/{slug} {label} not square: {dims}",
                    )
                else:
                    self.assertIn(
                        "seo-start-emoji",
                        block,
                        f"{kind}/{slug} {label} has neither square photo nor 1:1 emoji frame",
                    )
            if kind == "park":
                self.assertIn('class="seo-park-hero', visible, slug)
                hero = visible.split('class="seo-park-hero', 1)[1].split("</div>", 1)[0]
                hero_dims = img_wh.findall(hero)
                self.assertTrue(hero_dims, slug)
                self.assertTrue(
                    all(w != h for w, h in hero_dims),
                    f"{slug} park hero is not a wide scene: {hero_dims}",
                )

        for kind in ("zoo", "aquarium", "museum", "park"):
            self.assertGreater(kinds[kind], 0, kind)
        self.assertEqual(sum(kinds.values()), 218)


if __name__ == "__main__":
    unittest.main()
