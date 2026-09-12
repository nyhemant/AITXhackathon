"""Virtual Field Trip Pre-recorded stays in-page — no youtube.com dump."""

from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FP = REPO / "static" / "field-pack"
VDIR = FP / "data" / "virtual-venues"
VFT_PAGES = (
    FP / "virtual-field-trip" / "index.html",
)
VFT_JS = FP / "js" / "virtual-venue.js"
NOSCRIPT_RE = re.compile(r"<noscript\b[^>]*>.*?</noscript>", re.I | re.S)
HREF_RE = re.compile(r"""\bhref\s*=\s*(['"])(.*?)\1""", re.I)

# Watch Live wildlife / sea film sources. Science + park libs do not feed
# animal/sea card Watch Live (no overlapping cardIds).
WILDLIFE_SEA_FILM_FILES = (
    "virtual-zoo.json",
    "virtual-aquarium.json",
    "zoo-film-library.json",
    "aquarium-film-library.json",
)
# Explicit start: 0 is honored by filmStartSec and skips the 20s default.
# Allowlist a (file, card_id, url) only when 20s would miss the animal moment.
START_ZERO_ALLOWLIST: frozenset[tuple[str, str, str]] = frozenset()


def _wildlife_sea_film_entries():
    for name in WILDLIFE_SEA_FILM_FILES:
        data = json.loads((VDIR / name).read_text(encoding="utf-8"))
        for entry in list(data.get("habitats") or []) + list(data.get("cards") or []):
            cid = str(entry.get("id") or entry.get("cardId") or "")
            video = entry.get("video")
            if isinstance(video, dict) and video.get("url"):
                yield name, cid, "primary", video
            for i, extra in enumerate(entry.get("videos") or []):
                if isinstance(extra, dict) and extra.get("url"):
                    yield name, cid, f"videos[{i}]", extra


def without_noscript(html: str) -> str:
    return NOSCRIPT_RE.sub("", html)


class VftInlineFilmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = {p: p.read_text(encoding="utf-8") for p in VFT_PAGES}
        cls.js = VFT_JS.read_text(encoding="utf-8")

    def test_dialog_film_is_not_a_youtube_href(self):
        for path, html in self.pages.items():
            with self.subTest(page=str(path.relative_to(REPO))):
                visible = without_noscript(html)
                self.assertNotIn("vz-first-run-film", visible)
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
        self.assertNotIn("function playFirstRunFilm(", self.js)
        self.assertIn("function habitatFromFilmControl(", self.js)
        self.assertIn("((config && config.habitats) || [])", self.js)
        self.assertIn("filmLink.href = inPageFilmHref(h.id)", self.js)
        self.assertIn("openHabitat(hab.id, t, { fromHash: true })", self.js)
        self.assertIn("function playHabitatFilm(", self.js)
        self.assertIn("function habitatFilms(", self.js)
        self.assertIn("playHabitatFilm(h)", self.js)
        self.assertIn("playFilmInline(", self.js)
        static_film = self.js.split('if (t.classList.contains("vz-static-film")) {', 2)[2]
        static_film = static_film.split("const stopA", 1)[0]
        self.assertNotIn("openCamPopup", static_film)
        self.assertIn("playHabitatFilm", static_film)
        film_fn = self.js.split("function openCamPopup", 1)[1].split("function closeDialog", 1)[0]
        film_branch = film_fn.split("if (film)", 1)[1]
        self.assertIn("playFilmInline(url, label)", film_branch)
        after_film = film_branch.split("if (local && camFrame)", 1)[0]
        self.assertNotIn("openExternal", after_film)

    def test_js_intercepts_modified_clicks_on_film_controls(self):
        self.assertIn('["click", "auxclick"]', self.js)
        self.assertIn("filmControlFromEvent", self.js)
        self.assertNotIn("playFirstRunFilm", self.js)

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
            self.assertNotIn("vz-first-run-cam", visible)

    def test_sound_tip_shows_when_in_page_film_starts(self):
        film = self.js.split("function playFilmInline(", 1)[1].split("function closeCamPopup", 1)[0]
        self.assertIn("showSoundTip()", film)
        self.assertIn('const SOUND_TIP_KEY = "fp-vft-sound-tip-v1"', self.js)
        self.assertIn("sessionStorage.getItem(SOUND_TIP_KEY)", self.js)
        self.assertIn("sessionStorage.setItem(SOUND_TIP_KEY, \"1\")", self.js)
        show = self.js.split("function showSoundTip()", 1)[1].split("function playFilmInline", 1)[0]
        self.assertIn("soundTipSeen()", show)
        self.assertNotIn("openCamPopup", show)
        self.assertNotIn("function playFirstRunFilm(", self.js)
        for path, html in self.pages.items():
            with self.subTest(page=str(path.relative_to(REPO))):
                self.assertNotIn("vz-first-run", html)
                self.assertIn('id="vz-sound-tip"', html)
                self.assertIn("Sound is often off — tap the volume control on the film to listen.", html)
                self.assertIn('id="vz-sound-tip-dismiss"', html)
        css = (FP / "css" / "virtual-venue.css").read_text(encoding="utf-8")
        self.assertIn(".vz-sound-tip", css)
        self.assertIn(".vz-sound-tip-dismiss", css)

    def test_pre_recorded_honors_explicit_start_including_zero(self):
        self.assertIn("const FILM_START_DEFAULT = 20", self.js)
        self.assertIn("function filmStartSec(", self.js)
        body = self.js.split("function filmStartSec(", 1)[1].split("function youtubeEmbed", 1)[0]
        self.assertIn("FILM_START_DEFAULT", body)
        self.assertIn("n >= 0", body)
        self.assertNotIn("n > FILM_START_DEFAULT", body)
        embed = self.js.split("function youtubeEmbed(", 1)[1].split("function isYoutubeWatchUrl", 1)[0]
        self.assertIn("filmStartSec(opts && opts.start)", embed)
        self.assertIn("&start=", embed)
        film = self.js.split("function playFilmInline(", 1)[1].split("function closeCamPopup", 1)[0]
        self.assertIn("filmStartSec(start)", film)
        cam = self.js.split("function openCamPopup(", 1)[1].split("function closeDialog", 1)[0]
        self.assertNotIn("filmStartSec", cam.split("if (film)", 1)[0])
        zoo = json.loads((FP / "data" / "virtual-venues" / "virtual-zoo.json").read_text(encoding="utf-8"))
        flamingo = next(h for h in zoo["habitats"] if h["id"] == "caribbean-flamingo")
        self.assertEqual(flamingo["video"]["start"], 20)

    def test_pre_recorded_embed_loops_the_picked_clip(self):
        embed = self.js.split("function youtubeEmbed(", 1)[1].split("function isYoutubeWatchUrl", 1)[0]
        self.assertIn("&loop=1", embed)
        self.assertIn("&playlist=", embed)
        self.assertIn("encodeURIComponent(id)", embed)
        self.assertNotIn("playlist.join", embed)
        self.assertNotIn("opts.playlist", embed)
        self.assertIn("youtube-nocookie.com/embed/", embed)
        self.assertIn("rel=0", embed)
        self.assertIn("modestbranding=1", embed)
        self.assertIn("playsinline=1", embed)
        self.assertIn("autoplay=1&mute=1", embed)
        self.assertIn("function playHabitatFilm(", self.js)
        self.assertIn("function habitatFilms(", self.js)
        self.assertIn("function pickHabitatFilm(", self.js)
        films = self.js.split("function habitatFilms(", 1)[1].split("function cardHasFilm", 1)[0]
        self.assertIn("h.videos", films)
        self.assertIn("h.video && h.video.url", films)
        play = self.js.split("function playHabitatFilm(", 1)[1].split("function playFilmInline", 1)[0]
        self.assertIn("pickHabitatFilm(h)", play)
        self.assertNotIn("films[0]", play)

    def test_session_aware_random_pool_pick(self):
        self.assertIn('const FILM_SEEN_KEY = "fp-vft-film-seen-v1"', self.js)
        pick = self.js.split("function pickHabitatFilm(", 1)[1].split("function playHabitatFilm", 1)[0]
        self.assertIn("sessionStorage.getItem(FILM_SEEN_KEY)", self.js)
        self.assertIn("sessionStorage.setItem(FILM_SEEN_KEY", self.js)
        self.assertIn("Math.random()", pick)
        self.assertIn("unseen", pick)
        self.assertIn("shownSet", pick)
        self.assertIn("youtubeId(f.url)", pick)
        self.assertIn("h.id || h.cardId", self.js)
        self.assertIn("unseen.length ? unseen : films", pick)
        self.assertIn("unseen.length ? shown.concat([pickId]) : [pickId]", pick)

    def test_immersive_default_films_replaced(self):
        zoo = json.loads((FP / "data" / "virtual-venues" / "virtual-zoo.json").read_text(encoding="utf-8"))
        aqua = json.loads((FP / "data" / "virtual-venues" / "virtual-aquarium.json").read_text(encoding="utf-8"))
        by_id = {h["id"]: h for h in zoo["habitats"] + aqua["habitats"]}
        expected = {
            "caribbean-flamingo": "7nK3gZqtlOM",
            "asian-small-clawed-otter": "9IR2Ij9375w",
            "reticulated-giraffe": "WXsrwyNhfYw",
            "jellyfish": "8C3fzRYXSNE",
        }
        for hid, vid in expected.items():
            url = by_id[hid]["video"]["url"]
            self.assertIn(vid, url, hid)
            self.assertNotIn("live", url.lower())
            self.assertEqual(by_id[hid]["video"]["start"], 20)
        stale = ("u2k4lSTZxS4", "zboaajdMGHg", "TMvYXAkHIFo", "nbY7dSf3GYE")
        blob = json.dumps(zoo) + json.dumps(aqua)
        for old in stale:
            self.assertNotIn(old, blob)

    def test_default_tour_pools_keep_legacy_video_fallback(self):
        zoo = json.loads((FP / "data" / "virtual-venues" / "virtual-zoo.json").read_text(encoding="utf-8"))
        aqua = json.loads((FP / "data" / "virtual-venues" / "virtual-aquarium.json").read_text(encoding="utf-8"))
        by_id = {h["id"]: h for h in zoo["habitats"] + aqua["habitats"]}
        expected = {
            "caribbean-flamingo": {"7nK3gZqtlOM", "a3GkW5vuhAo", "-1BF2XqboOo"},
            "asian-small-clawed-otter": {"9IR2Ij9375w", "XQGB3AT90o8"},
            "reticulated-giraffe": {"WXsrwyNhfYw", "9L7RAUD8pu4"},
            "jellyfish": {"8C3fzRYXSNE", "uhJoXRgVd_8"},
        }
        for hid, ids in expected.items():
            hab = by_id[hid]
            videos = hab["videos"]
            pool = {v["url"].split("v=", 1)[1] for v in videos}
            self.assertEqual(pool, ids)
            self.assertIn(hab["video"]["url"].split("v=", 1)[1], pool)
            self.assertEqual(hab["video"]["start"], 20)
            for v in videos:
                self.assertNotIn("live", v["url"].lower())
                self.assertEqual(v["start"], 20)
                self.assertEqual(v["verify"]["status"], "sourced")

    def test_wildlife_sea_primary_films_are_not_start_zero(self):
        zeros = []
        for name, cid, role, film in _wildlife_sea_film_entries():
            if film.get("start") != 0:
                continue
            key = (name, cid, str(film["url"]))
            if role == "primary" and key not in START_ZERO_ALLOWLIST:
                zeros.append(f"{name}:{cid}:{film['url']}")
        self.assertEqual(zeros, [])

    def test_wildlife_sea_films_use_explicit_intro_skip(self):
        for name, cid, role, film in _wildlife_sea_film_entries():
            key = (name, cid, str(film["url"]))
            if film.get("start") == 0 and key in START_ZERO_ALLOWLIST:
                continue
            self.assertEqual(film.get("start"), 20, f"{name} {cid} {role}")

    def test_lion_habitat_and_library_use_default_skip(self):
        zoo = json.loads((VDIR / "virtual-zoo.json").read_text(encoding="utf-8"))
        lib = json.loads((VDIR / "zoo-film-library.json").read_text(encoding="utf-8"))
        habitat = next(h for h in zoo["habitats"] if h["id"] == "african-lion")
        library = next(c for c in lib["cards"] if c["cardId"] == "african-lion")
        self.assertEqual(habitat["video"]["url"], library["video"]["url"])
        self.assertEqual(habitat["video"]["start"], 20)
        self.assertEqual(library["video"]["start"], 20)

    def test_wildlife_sea_duplicate_urls_agree_on_start(self):
        by_url: dict[str, list[tuple[str, str, str, object]]] = {}
        for name, cid, role, film in _wildlife_sea_film_entries():
            by_url.setdefault(str(film["url"]), []).append((name, cid, role, film.get("start")))
        disagreements = []
        for url, rows in by_url.items():
            starts = {row[3] for row in rows}
            if len(starts) > 1:
                disagreements.append(f"{url}: {rows}")
        self.assertEqual(disagreements, [])

    def test_cache_bump(self):
        for html in self.pages.values():
            self.assertIn("virtual-venue.js?v=104", html)
            self.assertIn("virtual-venue.css?v=57", html)
        self.assertIn("virtual-zoo.json?v=27", self.js)
        self.assertIn("virtual-aquarium.json?v=27", self.js)
        self.assertIn("zoo-film-library.json?v=10", self.js)
        self.assertIn("aquarium-film-library.json?v=6", self.js)


if __name__ == "__main__":
    unittest.main()
