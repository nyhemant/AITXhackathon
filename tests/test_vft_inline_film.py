"""Virtual Field Trip Pre-recorded stays in-page — no youtube.com dump."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FP = REPO / "static" / "field-pack"
VFT_PAGES = (
    FP / "virtual-field-trip" / "index.html",
    FP / "virtual-zoo" / "index.html",
)
VFT_JS = FP / "js" / "virtual-venue.js"
NOSCRIPT_RE = re.compile(r"<noscript\b[^>]*>.*?</noscript>", re.I | re.S)
HREF_RE = re.compile(r"""\bhref\s*=\s*(['"])(.*?)\1""", re.I)


def without_noscript(html: str) -> str:
    return NOSCRIPT_RE.sub("", html)


class VftInlineFilmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = {p: p.read_text(encoding="utf-8") for p in VFT_PAGES}
        cls.js = VFT_JS.read_text(encoding="utf-8")

    def test_first_run_and_dialog_film_are_not_youtube_hrefs(self):
        for path, html in self.pages.items():
            with self.subTest(page=str(path.relative_to(REPO))):
                visible = without_noscript(html)
                first = visible.split('id="vz-first-run-film"', 1)[1].split(">", 1)[0]
                self.assertNotIn("youtube.com", first.lower())
                self.assertNotIn("youtu.be", first.lower())
                self.assertIn("habitat=caribbean-flamingo", first)
                dialog = visible.split('id="vz-film"', 1)[1].split(">", 1)[0]
                self.assertNotIn("youtube.com", dialog.lower())
                self.assertIn('href="#"', dialog)

    def test_visible_static_film_anchors_stay_on_vft(self):
        for path, html in self.pages.items():
            with self.subTest(page=str(path.relative_to(REPO))):
                visible = without_noscript(html)
                self.assertGreater(len(re.findall(r'class="vz-static-film"', visible)), 20)
                for m in re.finditer(r"<a\b[^>]*class=\"[^\"]*vz-static-film[^\"]*\"[^>]*>", visible):
                    tag = m.group(0)
                    self.assertNotIn("youtube.com", tag.lower(), tag)
                    self.assertNotIn("youtu.be", tag.lower(), tag)
                    href = HREF_RE.search(tag)
                    self.assertIsNotNone(href, tag)
                    self.assertTrue(
                        "habitat=" in href.group(2) or href.group(2) == "#",
                        href.group(2),
                    )
                    self.assertIn("data-habitat=", tag)
                    self.assertIn('role="button"', tag)
                self.assertIn("youtube.com", html)
                self.assertIn("vz-static-film-offsite", html)
                self.assertIn("<noscript>", html)

    def test_js_never_assigns_youtube_watch_href_to_film_controls(self):
        self.assertNotIn("filmLink.href = video.url", self.js)
        self.assertIn("function playFilmInline(", self.js)
        self.assertIn("function youtubeEmbed(", self.js)
        self.assertIn("function sealFilmControl(", self.js)
        self.assertIn("function sealStaticFilms(", self.js)
        self.assertIn("function playFirstRunFilm(", self.js)
        self.assertIn("function habitatFromFilmControl(", self.js)
        self.assertIn("((config && config.habitats) || [])", self.js)
        self.assertIn("filmLink.href = inPageFilmHref(h.id)", self.js)
        self.assertIn("openHabitat(hab.id, t, { fromHash: true })", self.js)
        self.assertIn("playFilmInline(video.url", self.js)
        static_film = self.js.split('if (t.classList.contains("vz-static-film")) {', 2)[2]
        static_film = static_film.split("const stopA", 1)[0]
        self.assertNotIn("openCamPopup", static_film)
        self.assertIn("playFilmInline", static_film)
        film_fn = self.js.split("function openCamPopup", 1)[1].split("function closeDialog", 1)[0]
        film_branch = film_fn.split("if (film)", 1)[1]
        self.assertIn("playFilmInline(url, label)", film_branch)
        after_film = film_branch.split("if (local && camFrame)", 1)[0]
        self.assertNotIn("openExternal", after_film)

    def test_js_intercepts_modified_clicks_on_film_controls(self):
        self.assertIn('["click", "auxclick"]', self.js)
        self.assertIn("filmControlFromEvent", self.js)
        self.assertIn("playFirstRunFilm", self.js)

    def test_generator_primary_film_action_is_in_page(self):
        sys.path.insert(0, str(REPO / "scripts"))
        import generate_vft_static as gen

        html = gen.film_line(
            {
                "id": "caribbean-flamingo",
                "video": {
                    "url": "https://www.youtube.com/watch?v=u2k4lSTZxS4",
                    "title": "Flamingo chicks at the Houston Zoo",
                },
            },
            "zoo",
        )
        primary = html.split("<noscript>", 1)[0]
        self.assertNotIn("youtube.com", primary.lower())
        self.assertIn("data-habitat=\"caribbean-flamingo\"", primary)
        self.assertIn("#habitat=caribbean-flamingo", primary)
        self.assertIn('role="button"', primary)
        self.assertIn("<noscript>", html)
        self.assertIn("vz-static-film-offsite", html)
        self.assertIn("youtube.com/watch?v=u2k4lSTZxS4", html.split("<noscript>", 1)[1])

    def test_live_cam_links_still_leave_site(self):
        for html in self.pages.values():
            visible = without_noscript(html)
            self.assertIn('class="vz-static-cam" href="https://www.houstonzoo.org/', visible)
            first_cam = visible.split('id="vz-first-run-cam"', 1)[1].split(">", 1)[0]
            self.assertIn("houstonzoo.org", first_cam)

    def test_cache_bump(self):
        for html in self.pages.values():
            self.assertIn("virtual-venue.js?v=84", html)


if __name__ == "__main__":
    unittest.main()
