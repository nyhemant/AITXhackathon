"""November 2026 scavenger-hunt block on 12 test place pages.

Comparison pages stay byte-identical. Frozen head fields stay equal to
origin/main. New lines are additive. Facts come from each venue JSON.
"""
from __future__ import annotations

import html
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scav_test_2026_11 import (  # noqa: E402
    COMPARISON_SLUGS,
    TEST_SLUGS,
    bonus_lines,
    hunt_items,
    item_line,
    load_venue,
    scav_top_block,
    sticky_single_print_html,
)

FIELD = ROOT / "static" / "field-pack"
FREE_RE = re.compile(r"\b(free|no-cost)\b", re.IGNORECASE)
WE_RE = re.compile(r"\b(we|our|us)\b")
EXPECTED = {
    "amnh": (7, 5),
    "nashville-adventure-science": (10, 6),
    "air-and-space": (7, 5),
    "national-aquarium-baltimore": (10, 4),
    "shedd-aquarium": (10, 4),
    "lincoln-park-zoo": (10, 4),
    "toronto-zoo": (10, 4),
    "austin-zoo": (5, 4),
    "national-zoo": (10, 6),
    "bronx-zoo": (7, 4),
    "redwood": (8, 10),
    "joshua-tree": (8, 10),
}


def _git_show(rel: str) -> str:
    return subprocess.check_output(
        ["git", "show", f"origin/main:{rel}"],
        cwd=ROOT,
        text=True,
    )


def _git_show_bytes(rel: str) -> bytes:
    return subprocess.check_output(["git", "show", f"origin/main:{rel}"], cwd=ROOT)


def _page(slug: str) -> str:
    return (FIELD / slug / "index.html").read_text(encoding="utf-8")


def _section(page: str) -> str:
    m = re.search(
        r'<section class="kz-scav-top no-print" id="printable-hunt".*?</section>',
        page,
        re.S,
    )
    if not m:
        raise AssertionError("missing printable-hunt section")
    return m.group(0)


def _tag(page: str, pattern: str) -> str:
    m = re.search(pattern, page, re.S)
    if not m:
        raise AssertionError(pattern)
    return m.group(0)


def _ld_blocks(page: str) -> list[str]:
    return re.findall(r'<script type="application/ld\+json">.*?</script>', page, re.S)


def _li_texts(section: str) -> list[str]:
    return [
        html.unescape(text)
        for text in re.findall(
            r'<li><span class="seo-hunt-box"[^>]*>☐</span><span>(.*?)</span></li>',
            section,
        )
    ]


class ScavTestPages(unittest.TestCase):
    def test_slug_sets_are_the_agreed_twelve(self):
        self.assertEqual(len(TEST_SLUGS), 12)
        self.assertEqual(len(COMPARISON_SLUGS), 12)
        self.assertFalse(TEST_SLUGS & COMPARISON_SLUGS)

    def test_builder_is_empty_off_the_test_list(self):
        self.assertEqual(scav_top_block("dallas-zoo"), "")
        self.assertEqual(scav_top_block("banff"), "")
        self.assertTrue(scav_top_block("amnh"))

    def test_each_test_page_block(self):
        for slug in sorted(TEST_SLUGS):
            with self.subTest(slug=slug):
                page = _page(slug)
                origin = _git_show(f"static/field-pack/{slug}/index.html")
                venue = load_venue(slug)
                self.assertEqual(page.count('id="printable-hunt"'), 1, slug)
                section = _section(page)
                name = venue["name"]
                self.assertIn(f"<h2 id=\"scav-top-h\">Printable scavenger hunt for {html.escape(name)}</h2>", section)
                hero = page.find('<header class="seo-hero">')
                h1_end = page.find("</h1>", hero)
                block_at = page.find('id="printable-hunt"', hero)
                fork_at = page.find('class="seo-fork-wrap', hero)
                hero_end = page.find("</header>", hero)
                self.assertLess(hero, h1_end)
                self.assertLess(h1_end, block_at)
                self.assertLess(block_at, fork_at)
                self.assertLess(fork_at, hero_end)
                self.assertNotIn('id="mission-open-btn"', section)
                self.assertIn(
                    '<button type="button" class="kz-scav-print" data-how="print-hunt" '
                    'data-kz-cta="scav-top">Build and print the hunt</button>',
                    section,
                )
                self.assertIn("black &amp; white is fine", section)
                self.assertIn('href="/field-pack/css/scav-top-v1.css?v=2"', page)
                self.assertIn('<script src="/shell/qr-welcome.js?v=4" defer></script>', page)
                items = hunt_items(venue)
                bonus = bonus_lines(venue)
                want_items, want_bonus = EXPECTED[slug]
                self.assertEqual(len(items), want_items, slug)
                self.assertEqual(len(bonus), want_bonus, slug)
                lines = _li_texts(section)
                self.assertEqual(lines, [item_line(item) for item in items] + bonus)
                self.assertEqual(page.count('class="kz-scav-list'), 2 if bonus else 1)
                plain = html.unescape(section)
                self.assertIsNone(FREE_RE.search(plain), plain[:240])
                self.assertIsNone(WE_RE.search(plain), plain[:240])
                self._assert_no_banned_name(plain, venue)
                self._assert_pdfs(section, venue)
                self._assert_frozen(page, origin)
                self._assert_scoped_edit(origin, page)

    def test_comparison_pages_are_byte_identical(self):
        for slug in sorted(COMPARISON_SLUGS):
            rel = f"static/field-pack/{slug}/index.html"
            with self.subTest(slug=slug):
                got = (ROOT / rel).read_bytes()
                self.assertEqual(got, _git_show_bytes(rel))
                self.assertNotIn(b"kz-scav-top", got)
                self.assertNotIn(b"printable-hunt", got)
                self.assertNotIn(b"scav-top-v1.css", got)

    def test_diff_stays_in_scope(self):
        diff = subprocess.check_output(
            ["git", "diff", "--name-only", "origin/main"],
            cwd=ROOT,
            text=True,
        ).split()
        untracked = subprocess.check_output(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=ROOT,
            text=True,
        ).split()
        names = sorted(set(diff) | set(untracked))
        extra = [path for path in names if not _in_scope(path)]
        self.assertEqual(extra, [], "out of scope:\n" + "\n".join(extra))
        for slug in TEST_SLUGS:
            self.assertIn(f"static/field-pack/{slug}/index.html", names)
        for slug in COMPARISON_SLUGS:
            self.assertNotIn(f"static/field-pack/{slug}/index.html", names)
        self.assertIn("scripts/scav_test_2026_11.py", names)
        self.assertIn("scripts/generate_bdo_seo.py", names)
        self.assertIn("scripts/pdf_counts_report.py", names)
        self.assertIn("static/field-pack/css/scav-top-v1.css", names)
        self.assertIn("static/field-pack/js/mission/mission-ui.js", names)
        self.assertIn("static/shell/qr-welcome.js", names)
        self.assertIn("src/busyparent_agent/web.py", names)
        self.assertIn("docs/download-metric.md", names)

    def test_pdf_labels_are_distinct(self):
        for slug in sorted(TEST_SLUGS):
            with self.subTest(slug=slug):
                section = _section(_page(slug))
                venue = load_venue(slug)
                labels = re.findall(r'class="kz-scav-pdf"[^>]*>([^<]+)</a>', section)
                kind = venue.get("type")
                if kind == "museum":
                    self.assertEqual(labels, ["Trip journal"])
                    self.assertIn("US Letter or A4 · black &amp; white is fine", section)
                    continue
                self.assertEqual(labels, ["PDF, US Letter", "PDF, A4"])
                self.assertEqual(len(set(labels)), 2)
                self.assertIn('<p class="kz-scav-spec">black &amp; white is fine</p>', section)
                self.assertNotIn("US Letter or A4", section)
                for href in re.findall(r'href="(/printables/pdf/[^"]+\.pdf)"', section):
                    self.assertIn(f'href="{href}" download data-kz-cta="scav-top"', section)
                name = "Park &amp; Backyard Hunt" if kind == "national_park" else "Zoo &amp; Park Scavenger Hunt"
                self.assertIn(f'class="kz-scav-pdf-name">{name}</span>', section)

    def test_one_print_wording_on_test_pages(self):
        for slug in sorted(TEST_SLUGS):
            with self.subTest(slug=slug):
                page = _page(slug)
                sticky = re.search(
                    r'<div class="seo-hunt-sticky no-print" id="seo-hunt-sticky".*?</div>',
                    page,
                    re.S,
                )
                self.assertIsNotNone(sticky, slug)
                block = sticky.group(0)
                text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", block)).strip()
                self.assertEqual(text, "Build and print the hunt")
                self.assertIn('data-kz-scav-print="1"', block)
                self.assertIn('data-how="print-hunt"', block)
                self.assertIn('data-kz-cta="scav-top"', block)
                self.assertNotIn("Suggested stops", page)
                self.assertNotIn(">Print</button>", block)
                print_ctas = [
                    label.strip()
                    for label in re.findall(r'data-how="print-hunt"[^>]*>([^<]+)</', page)
                    if re.search(r"print", label, re.I)
                ]
                self.assertEqual(set(print_ctas), {"Build and print the hunt"})
                self.assertEqual(print_ctas.count("Build and print the hunt"), 2)
                self.assertIn('id="mission-print-btn">Print</button>', page)
                self.assertIn(sticky_single_print_html().lstrip("\n"), page)

    def test_sticky_script_is_gated_and_events_carry_page_path(self):
        ui = (FIELD / "js" / "mission" / "mission-ui.js").read_text(encoding="utf-8")
        self.assertIn('bar.getAttribute("data-kz-scav-print") === "1"', ui)
        self.assertIn("page_path: pagePathOnly()", ui)
        self.assertIn("venue: mission.slug", ui)
        self.assertIn('btn.textContent = "Build and print the hunt"', ui)
        qr = (ROOT / "static" / "shell" / "qr-welcome.js").read_text(encoding="utf-8")
        self.assertIn("page_path: pagePath", qr)
        self.assertIn("location.pathname", qr)

    def test_generator_fragments_match_test_pages(self):
        import generate_bdo_seo as gen

        venues = {row["id"]: row for row in gen.load_venues()}
        for slug in ("lincoln-park-zoo", "amnh", "redwood", "dallas-zoo"):
            mission = gen.load_mission_venue(slug)
            html = gen.render_mission_venue_page(venues[slug], mission)
            with self.subTest(slug=slug):
                if slug in TEST_SLUGS:
                    self.assertIn(scav_top_block(slug), html)
                    self.assertIn(sticky_single_print_html().strip(), html)
                    self.assertNotIn("Suggested stops · Print", html)
                else:
                    self.assertNotIn("printable-hunt", html)
                    self.assertNotIn("data-kz-scav-print", html)
                    self.assertIn("Suggested stops · Print (1 page)", html)
                    self.assertIn(
                        'id="seo-sticky-print" data-how="print-hunt">Print</button>',
                        html,
                    )

    def _assert_pdfs(self, section: str, venue: dict) -> None:
        hrefs = re.findall(r'href="(/printables/pdf/[^"]+\.pdf)"', section)
        kind = venue.get("type")
        labels = re.findall(r'class="kz-scav-pdf"[^>]*>([^<]+)</a>', section)
        if kind == "museum":
            self.assertEqual(hrefs, [])
            self.assertEqual(labels, ["Trip journal"])
            self.assertIn('href="/printables/zoo-day-journal/"', section)
            self.assertIn(">Trip journal</a>", section)
            self.assertIn("US Letter or A4 · black &amp; white is fine", section)
            return
        self.assertEqual(labels, ["PDF, US Letter", "PDF, A4"])
        if kind == "national_park":
            self.assertEqual(hrefs, [
                "/printables/pdf/letter/park-scavenger-hunt.pdf",
                "/printables/pdf/a4/park-scavenger-hunt-a4.pdf",
            ])
        else:
            self.assertIn(kind, {"zoo", "aquarium", "safari_zoo"})
            self.assertEqual(hrefs, [
                "/printables/pdf/letter/scavenger-hunt.pdf",
                "/printables/pdf/a4/scavenger-hunt-a4.pdf",
            ])
        for href in hrefs:
            path = ROOT / "static" / href.lstrip("/")
            self.assertTrue(path.is_file(), href)
            self.assertIn(f'href="{href}" download', section)

    def _assert_no_banned_name(self, plain: str, venue: dict) -> None:
        remaining = plain
        for item in hunt_items(venue):
            for blob in (
                item_line(item),
                str(item.get("one_liner") or ""),
                str(item.get("display_label") or ""),
                str(item.get("label") or ""),
                str(item.get("zone") or ""),
            ):
                if blob:
                    remaining = remaining.replace(blob, "")
        for text in bonus_lines(venue):
            remaining = remaining.replace(text, "")
        for row in venue.get("do_not_list") or []:
            name = str(row.get("name") or "").strip()
            if name:
                self.assertNotIn(name.lower(), remaining.lower(), name)

    def _assert_frozen(self, page: str, origin: str) -> None:
        patterns = (
            r"<title>.*?</title>",
            r'<meta name="description" content="[^"]*"\s*/?>',
            r'<meta property="og:title" content="[^"]*"\s*/?>',
            r'<meta property="og:description" content="[^"]*"\s*/?>',
            r'<meta name="twitter:title" content="[^"]*"\s*/?>',
            r'<meta name="twitter:description" content="[^"]*"\s*/?>',
            r"<h1[^>]*>.*?</h1>",
            r'<link rel="canonical" href="[^"]*"\s*/?>',
        )
        for pattern in patterns:
            self.assertEqual(_tag(page, pattern), _tag(origin, pattern), pattern)
        self.assertEqual(_ld_blocks(page), _ld_blocks(origin))

    def _assert_scoped_edit(self, origin: str, page: str) -> None:
        import difflib

        diff = difflib.unified_diff(origin.splitlines(), page.splitlines(), lineterm="")
        for line in diff:
            if not line.startswith(("+", "-")) or line.startswith(("+++", "---")):
                continue
            body = line[1:]
            self.assertTrue(_page_edit_ok(body), "unexpected line edit: " + body[:220])


def _page_edit_ok(body: str) -> bool:
    markers = (
        "printable-hunt",
        "kz-scav",
        "scav-top-v1.css",
        "seo-hunt-sticky",
        "seo-sticky-print",
        "seo-hunt-sticky-label",
        "seo-sticky-print-spec",
        "data-kz-scav-print",
    )
    return any(marker in body for marker in markers)


def _in_scope(path: str) -> bool:
    if path in {
        "scripts/scav_test_2026_11.py",
        "scripts/generate_bdo_seo.py",
        "scripts/pdf_counts_report.py",
        "src/busyparent_agent/web.py",
        "static/shell/qr-welcome.js",
        "static/field-pack/css/scav-top-v1.css",
        "static/field-pack/js/mission/mission-ui.js",
        "docs/download-metric.md",
        "tests/test_pdf_download_counter.py",
        "tests/test_pdf_counts_report.py",
        "tests/test_scav_test_2026_11.py",
        "tests/test_origin_cache.py",
        "tests/test_qr_welcome.py",
    }:
        return True
    if path.startswith("static/shell/qr-welcome"):
        return True
    if path.startswith("tests/") or path.startswith("docs/"):
        return True
    for slug in TEST_SLUGS:
        if path.startswith(f"static/field-pack/{slug}/"):
            return True
    if path.endswith((".html", ".py", ".js", ".css", ".md")) and _only_qr_version_bump(path):
        return True
    return False


def _only_qr_version_bump(path: str) -> bool:
    diff = subprocess.check_output(
        ["git", "diff", "origin/main", "--", path],
        cwd=ROOT,
        text=True,
    )
    body = [
        line[1:]
        for line in diff.splitlines()
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
    ]
    if not body:
        return False
    return all("qr-welcome.js?v=" in line for line in body)


if __name__ == "__main__":
    unittest.main()
