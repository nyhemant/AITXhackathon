#!/usr/bin/env python3
"""Build the KZK Science Bee practice section from its question bank.

Source of truth: static/science-bee/data/questions-v1.json (original
questions written for KidZooKit; never copied from any competition packet).

Writes, and only writes, files under static/science-bee/:
  sb-questions-v1.js            bank + picture SVGs for the play page
  index.html                    hub (indexed)
  questions/<topic>/index.html  6 topic pages (indexed)
  play/index.html               the phone game (noindex,follow)
  (--print-html PATH writes the print sheet source for the versioned PDF)

Targeted: it never touches place pages, the shared templates, or the
generator outputs elsewhere. Re-running it is idempotent.

Usage: python3 scripts/science_bee_build_v1.py
"""
from __future__ import annotations

import html
import json
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ROOT = REPO / "static" / "science-bee"
BANK = ROOT / "data" / "questions-v1.json"
SITE = "https://kidzookit.com"

ASSET_V = {"css": 1, "js": 1, "bank": 1}
PDF_NAME = "science-bee-practice-sheet-v1.pdf"
OG_IMAGE = "/science-bee/img/science-bee-og-v1.png"

TOPICS = [
    # key, slug, short label, long label, page h1 noun, intro
    ("life", "life-science", "Living things", "Living things (life science)",
     "Life Science",
     "Alive or not alive, life cycles, food chains, habitats and the big animal groups."),
    ("earth", "earth-and-space", "Earth & space", "Earth and space",
     "Earth and Space",
     "The Sun, Moon and planets, rocks and volcanoes, oceans, glaciers and the stars."),
    ("physical", "physical-science", "Matter & forces", "Matter, forces and energy (physical science)",
     "Physical Science",
     "Solids, liquids and gases, magnets, gravity, light, sound, simple machines and circuits."),
    ("body", "human-body", "Human body", "The human body",
     "Human Body",
     "The five senses, bones and muscles, heart and lungs, and how food gets used."),
    ("weather", "weather", "Weather", "Weather",
     "Weather",
     "Rain, snow and rainbows, clouds, storms, seasons and the tools that measure weather."),
    ("plants", "plants-and-animals", "Plants & animals", "Plants and animals",
     "Plants and Animals",
     "Plant parts and pollination, animal babies, record-setting animals and clever adaptations."),
]
TOPIC_BY_KEY = {t[0]: t for t in TOPICS}
BANDS = [("little", "Little", "Pre-K to K"), ("big", "Big", "1st to 3rd grade")]

PHOTOS = {
    # Only photos with a recorded author and licence (the citable-card set).
    "whale-shark": {
        "alt": "A spotted whale shark swimming in blue water",
        "credit": "Arturo de Frias Marques",
        "licence": "CC BY-SA 4.0",
        "licence_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "file_url": "https://commons.wikimedia.org/wiki/File:Whale_Shark_1_AdF.jpg",
        "note": "resized",
    },
    "manta-ray": {
        "alt": "A giant manta ray gliding with wide fins",
        "credit": "Arturo de Frias Marques",
        "licence": "CC BY-SA 4.0",
        "licence_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "file_url": "https://commons.wikimedia.org/wiki/File:Giant_Manta_AdF.jpg",
        "note": "resized",
    },
    "african-elephant": {
        "alt": "An African elephant with its long trunk and big ears",
        "credit": "Bernard DUPONT",
        "licence": "CC BY-SA 2.0",
        "licence_url": "https://creativecommons.org/licenses/by-sa/2.0/",
        "file_url": "https://commons.wikimedia.org/wiki/File:African_Elephant_(Loxodonta_africana)_male_(17289351322).jpg",
        "note": "cropped and colour-adjusted",
    },
}

# Simple inline drawings for picture questions. No external images.
SVGS = {
    "moon-crescent": '<svg viewBox="0 0 120 120" role="img" aria-label="A thin crescent Moon in a dark sky"><rect width="120" height="120" rx="18" fill="#1d2b4a"/><circle cx="20" cy="22" r="1.6" fill="#fff"/><circle cx="98" cy="96" r="1.4" fill="#fff"/><circle cx="96" cy="20" r="1.2" fill="#fff"/><circle cx="60" cy="60" r="36" fill="#f6e7a1"/><circle cx="78" cy="52" r="34" fill="#1d2b4a"/></svg>',
    "moon-full": '<svg viewBox="0 0 120 120" role="img" aria-label="A round full Moon in a dark sky"><rect width="120" height="120" rx="18" fill="#1d2b4a"/><circle cx="18" cy="96" r="1.5" fill="#fff"/><circle cx="100" cy="18" r="1.3" fill="#fff"/><circle cx="60" cy="60" r="36" fill="#f6e7a1"/><circle cx="48" cy="50" r="7" fill="#e3d185"/><circle cx="70" cy="70" r="9" fill="#e3d185"/><circle cx="72" cy="44" r="4" fill="#e3d185"/></svg>',
    "magnet-clip": '<svg viewBox="0 0 160 120" role="img" aria-label="A horseshoe magnet next to a paper clip"><rect width="160" height="120" rx="18" fill="#eaf4ff"/><path d="M30 25 h22 v45 a14 14 0 0 0 28 0 v-45 h22 v45 a36 36 0 0 1 -72 0z" fill="#d23c3c"/><rect x="30" y="20" width="22" height="14" fill="#c9ced6"/><rect x="80" y="20" width="22" height="14" fill="#c9ced6"/><path d="M118 40 h22 a6 6 0 0 1 0 12 h-22 a6 6 0 0 1 0 -12 m4 4 h16 a2 2 0 0 1 0 4 h-16" fill="none" stroke="#5b6573" stroke-width="3"/><path d="M106 46 h8 M106 40 l6 -4 M106 52 l6 4" stroke="#0f5c5c" stroke-width="2" stroke-dasharray="3 3"/></svg>',
    "thermo-hot": '<svg viewBox="0 0 120 140" role="img" aria-label="A thermometer with the red line almost at the top, and a bright sun"><rect width="120" height="140" rx="18" fill="#fff4dc"/><circle cx="92" cy="30" r="14" fill="#ffcf5a"/><rect x="40" y="16" width="20" height="92" rx="10" fill="#fff" stroke="#5b6573" stroke-width="3"/><circle cx="50" cy="114" r="14" fill="#d23c3c" stroke="#5b6573" stroke-width="3"/><rect x="45" y="24" width="10" height="90" rx="5" fill="#d23c3c"/><path d="M62 30h8M62 50h8M62 70h8M62 90h8" stroke="#5b6573" stroke-width="2"/></svg>',
    "plant-parts": '<svg viewBox="0 0 140 160" role="img" aria-label="A plant with three numbered parts: 1 under the soil, 2 a leaf, 3 the flower"><rect width="140" height="160" rx="18" fill="#eaf4ff"/><rect y="104" width="140" height="56" fill="#8a5a3c"/><path d="M70 104 v-62" stroke="#3c8a3c" stroke-width="5"/><path d="M70 78 q-30 -6 -36 -24 q24 2 36 24z" fill="#4caf50"/><g fill="#ff8fb1"><circle cx="70" cy="28" r="9"/><circle cx="58" cy="36" r="9"/><circle cx="82" cy="36" r="9"/><circle cx="62" cy="48" r="9"/><circle cx="78" cy="48" r="9"/></g><circle cx="70" cy="40" r="7" fill="#ffcf5a"/><path d="M70 104 l-14 22 M70 104 l0 30 M70 104 l16 20 M58 120 l-8 10 M84 120 l8 12" stroke="#f3e2c7" stroke-width="3" fill="none"/><g font-family="system-ui,sans-serif" font-size="15" font-weight="800" fill="#152238"><circle cx="112" cy="128" r="11" fill="#fff"/><text x="107" y="133">1</text><circle cx="22" cy="62" r="11" fill="#fff"/><text x="17" y="67">2</text><circle cx="112" cy="26" r="11" fill="#fff"/><text x="107" y="31">3</text></g><path d="M101 128 h-12 M33 62 h8 M101 28 h-14" stroke="#152238" stroke-width="2"/></svg>',
    "circuit-closed": '<svg viewBox="0 0 160 120" role="img" aria-label="A battery and a glowing bulb joined by wires in a complete loop"><rect width="160" height="120" rx="18" fill="#eaf4ff"/><path d="M40 80 V30 H120 V60 M40 80 V96 H120 V80" fill="none" stroke="#c46a1c" stroke-width="5"/><rect x="24" y="62" width="32" height="26" rx="4" fill="#2f3e57"/><rect x="34" y="56" width="12" height="6" fill="#2f3e57"/><text x="31" y="80" font-family="system-ui,sans-serif" font-size="14" font-weight="800" fill="#fff">+ -</text><circle cx="120" cy="66" r="16" fill="#ffe680" stroke="#c9a400" stroke-width="3"/><path d="M114 66 l3 -6 l3 6 l3 -6" stroke="#c46a1c" stroke-width="2" fill="none"/><path d="M120 44 v-6 M138 56 l6 -4 M102 56 l-6 -4" stroke="#ffb300" stroke-width="3"/></svg>',
    "circuit-open": '<svg viewBox="0 0 160 120" role="img" aria-label="A battery and a dark bulb with a gap in the wire"><rect width="160" height="120" rx="18" fill="#eaf4ff"/><path d="M40 80 V30 H72 M92 30 H120 V50 M40 80 V96 H120 V82" fill="none" stroke="#c46a1c" stroke-width="5"/><rect x="24" y="62" width="32" height="26" rx="4" fill="#2f3e57"/><rect x="34" y="56" width="12" height="6" fill="#2f3e57"/><text x="31" y="80" font-family="system-ui,sans-serif" font-size="14" font-weight="800" fill="#fff">+ -</text><circle cx="120" cy="66" r="16" fill="#e4e7ec" stroke="#8a93a3" stroke-width="3"/><path d="M114 66 l3 -6 l3 6 l3 -6" stroke="#8a93a3" stroke-width="2" fill="none"/><text x="70" y="22" font-family="system-ui,sans-serif" font-size="12" font-weight="800" fill="#d23c3c">gap</text></svg>',
    "shadow": '<svg viewBox="0 0 180 120" role="img" aria-label="The sun on the left side and a tree in the middle on grass"><rect width="180" height="120" rx="18" fill="#eaf4ff"/><circle cx="26" cy="28" r="14" fill="#ffcf5a"/><path d="M26 6v6M26 44v6M4 28h6M42 28h6M11 13l4 4M37 39l4 4M11 43l4-4M37 17l4-4" stroke="#ffb300" stroke-width="3"/><rect y="88" width="180" height="32" fill="#a8d5a2"/><rect x="86" y="56" width="8" height="34" fill="#7a4e2d"/><circle cx="90" cy="48" r="20" fill="#3c8a3c"/><text x="118" y="110" font-family="system-ui,sans-serif" font-size="13" font-weight="800" fill="#152238">?</text><text x="56" y="110" font-family="system-ui,sans-serif" font-size="13" font-weight="800" fill="#152238">?</text></svg>',
}

WARMUPS = [
    ("🦀", "Crab walk to the door and back."),
    ("🐸", "Frog jump three times. Ribbit!"),
    ("🌱", "Be a seed: curl up small, then grow slowly into a tall sunflower."),
    ("🌍", "Be the Earth: spin slowly once, then walk a circle around the table like you are going around the Sun."),
    ("🐧", "Penguin waddle with your arms flat at your sides."),
    ("💓", "Jump 10 times, then put a hand on your chest. Can you feel your heart beating faster?"),
    ("🌪️", "Spin like a tornado, slowly, then freeze like a statue."),
    ("🧲", "Magnet game: stick together like magnets, then push apart like two north poles."),
    ("🦩", "Flamingo stand: balance on one foot while counting to 10."),
    ("🐻", "Bear crawl across the room on hands and feet."),
    ("🌧️", "Make a rainstorm: rub hands, snap fingers, pat legs, then stomp for thunder."),
    ("🐍", "Slither like a snake, then shed your skin with a wiggle."),
    ("🚀", "Rocket launch: crouch down, count 5-4-3-2-1, and blast off with a jump."),
    ("🦋", "Be a caterpillar curled in a chrysalis, then open your wings and fly around the table."),
    ("🦒", "Giraffe stretch: reach as high as you can for the tallest leaves."),
]


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def load_bank() -> list[dict]:
    data = json.loads(BANK.read_text(encoding="utf-8"))
    return data["questions"]


def menu() -> str:
    """The site's standard shell menu (same doors and hub links as every page)."""
    return """  <header class="oneless-shell no-print" data-product="bdo">
    <a class="shell-product" href="/start/">KidZooKit <small>Watch it. Print it. Go find it.</small></a>
    <div class="shell-more-wrap">
      <button type="button" class="shell-more" aria-expanded="false" aria-haspopup="true" aria-controls="shell-menu" aria-label="Open menu">
        <span class="shell-more-bars" aria-hidden="true"><span></span><span></span><span></span></span>
      </button>
      <div id="shell-menu" class="shell-menu" hidden role="menu">
        <a href="/start/" role="menuitem">Start</a>
        <a href="/field-pack/cards/" role="menuitem">Cards</a>
        <a href="/field-pack/virtual-field-trip/" role="menuitem">Watch Live</a>
        <a href="/field-pack/" role="menuitem">Places</a>
        <!-- kz-menu:hubs -->
        <a class="shell-menu-sub" href="/field-pack/zoos/" role="menuitem" data-related-link="menu_hub">Zoos</a>
        <a class="shell-menu-sub" href="/field-pack/aquariums/" role="menuitem" data-related-link="menu_hub">Aquariums</a>
        <a class="shell-menu-sub" href="/field-pack/museums/" role="menuitem" data-related-link="menu_hub">Museums</a>
        <a class="shell-menu-sub" href="/field-pack/national-parks/" role="menuitem" data-related-link="menu_hub">Parks</a>
        <!-- /kz-menu:hubs -->
        <a href="/printables/" role="menuitem">Printables</a>
        <a href="/about/" role="menuitem">About</a>
      </div>
    </div>
  </header>"""


def head(title: str, desc: str, path: str, robots: str, ld: dict | None, extra: str = "") -> str:
    # Site search rules (tests/test_seo_alt_titles.py): title <= 60, description <= 160.
    assert len(title) <= 60, title
    assert len(desc) <= 160, desc
    url = SITE + path
    ld_html = ""
    if ld is not None:
        ld_html = '  <script type="application/ld+json">\n' + json.dumps(ld, ensure_ascii=False) + "\n  </script>\n"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}" />
  <link rel="canonical" href="{url}" />
  <meta name="robots" content="{robots}" />
  <meta name="theme-color" content="#0f5c5c" />
  <link rel="icon" href="/favicon.ico?v=1" sizes="48x48" />
  <link rel="icon" type="image/png" href="/pwa/favicon-96-v1.png" sizes="96x96" />
  <link rel="apple-touch-icon" href="/pwa/apple-touch-icon.png" />
  <link rel="manifest" href="/manifest.webmanifest" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="KidZooKit" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(desc)}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="{SITE}{OG_IMAGE}" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="Science Bee practice for kids on KidZooKit" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{esc(title)}" />
  <meta name="twitter:description" content="{esc(desc)}" />
  <meta name="twitter:image" content="{SITE}{OG_IMAGE}" />
  <link rel="stylesheet" href="/shell/shell.css?v=13" />
  <link rel="stylesheet" href="/science-bee/sb-v1.css?v={ASSET_V['css']}" />
{ld_html}{extra}</head>
"""


FOOT_LINKS = """      <footer class="sb-foot">
        <p><a href="/science-bee/">Science Bee</a> <span aria-hidden="true">&middot;</span> <a href="/start/">Start</a> <span aria-hidden="true">&middot;</span> <a href="/printables/">Printables</a> <span aria-hidden="true">&middot;</span> <a href="/privacy/">Privacy</a> <span aria-hidden="true">&middot;</span> <a href="/about/">About</a></p>
        <p class="sb-disclaim">Practice inspired by kid science bees. Original questions written for KidZooKit; not connected to or endorsed by any competition.</p>
      </footer>"""

SCRIPTS = """  <script src="/shell/shell.js?v=8"></script>
  <script src="/pwa/register.js?v=1"></script>
"""


def pic_html(q: dict, big: bool = True) -> str:
    pic = q.get("pic")
    if not pic:
        return ""
    if "emoji" in pic:
        return f'<div class="sb-pic sb-pic-emoji" aria-hidden="true">{pic["emoji"]}</div>'
    if "svg" in pic:
        return f'<div class="sb-pic sb-pic-svg">{SVGS[pic["svg"]]}</div>'
    if "photo" in pic:
        slug = pic["photo"]
        p = PHOTOS[slug]
        return (
            f'<figure class="sb-pic sb-pic-photo"><picture style="display:contents">'
            f'<source type="image/webp" srcset="/field-pack/photos/{slug}-480-v1.webp 480w, /field-pack/photos/{slug}-640-v1.webp 640w" sizes="(max-width: 600px) 80vw, 320px" />'
            f'<img src="/field-pack/photos/{slug}.jpg?v=img2" alt="{esc(p["alt"])}" width="640" height="640" loading="lazy" decoding="async" /></picture>'
            f'<figcaption>Photo: {esc(p["credit"])}, {esc(p["licence"])}, via Wikimedia Commons ({esc(p["note"])}). <a href="/science-bee/#credits">Credits</a></figcaption></figure>'
        )
    raise ValueError(pic)


def counts(bank: list[dict]) -> dict:
    c: dict = {}
    for q in bank:
        c.setdefault(q["topic"], {"little": 0, "big": 0, "pic": 0})
        c[q["topic"]][q["band"]] += 1
        if q.get("pic"):
            c[q["topic"]]["pic"] += 1
    return c


def build_bank_js(bank: list[dict]) -> str:
    topics = [{"key": t[0], "slug": t[1], "label": t[2]} for t in TOPICS]
    photos = {k: {"alt": v["alt"], "credit": f'Photo: {v["credit"]}, {v["licence"]}, via Wikimedia Commons ({v["note"]})'} for k, v in PHOTOS.items()}
    payload = {
        "version": 1,
        "topics": topics,
        "questions": bank,
        "svgs": SVGS,
        "photos": photos,
        "warmups": [{"emoji": e, "text": t} for e, t in WARMUPS],
    }
    return (
        "/* KZK Science Bee question bank v1. Generated by scripts/science_bee_build_v1.py\n"
        " * from static/science-bee/data/questions-v1.json. Do not edit by hand. */\n"
        "window.SB_BANK = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n"
    )


def build_hub(bank: list[dict]) -> str:
    c = counts(bank)
    total = len(bank)
    n_little = sum(1 for q in bank if q["band"] == "little")
    n_big = total - n_little
    n_pic = sum(1 for q in bank if q.get("pic"))
    title = "Science Bee Practice for Kids, Pre-K to 3rd | KidZooKit"
    desc = (f"A 10-15 minute after-dinner science bee game: {total} original kid questions in two age "
            "bands, picture rounds and a two-kid buzzer on one phone. No signup.")
    faqs = [
        ("Is this an official Science Bee?",
         "No. These are original practice questions written for KidZooKit, inspired by the kinds of topics kid science bees cover: living things, Earth and space, matter and energy, the human body, weather, and plants and animals. KidZooKit is not connected to or endorsed by any competition organizer."),
        ("What ages is it for?",
         "Roughly ages 4 to 8. The Little band (Pre-K to K) has short questions with two or three answer choices read aloud. The Big band (1st to 3rd grade) has open answers, like a real bee, with a button that brings up choices when a child is stuck."),
        ("Does anyone need an account?",
         "No. There is nothing to sign up for. Scores live only on the phone while the round is open and disappear when the round ends. The phone remembers the game settings, such as age band and topics, and nothing else."),
        ("Can two kids of different ages play together?",
         "Yes. Set one player to Little and one to Big. Questions alternate between the bands, and when the Little player buzzes in, answer choices appear for them."),
        ("Does it work without internet?",
         "Once the game page has loaded, a whole round plays without a connection: the questions and pictures are already on the phone. There are no sounds or videos, and nothing plays by itself."),
        ("Where do the facts come from?",
         "Every question uses standard, well-established science, the kind found in early-grades science lessons. Questions that depend on shaky trivia, exact counts that are hard to check, or contested ideas were left out."),
    ]
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "LearningResource", "name": "Science Bee Practice for Kids", "url": SITE + "/science-bee/",
             "description": desc, "inLanguage": "en", "educationalLevel": "Pre-K to 3rd grade",
             "learningResourceType": "Quiz game",
             "teaches": [t[3] for t in TOPICS],
             "hasPart": [{"@type": "WebPage", "name": f"{t[4]} questions", "url": f"{SITE}/science-bee/questions/{t[1]}/"} for t in TOPICS]},
            {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Start", "item": SITE + "/start/"},
                {"@type": "ListItem", "position": 2, "name": "Science Bee", "item": SITE + "/science-bee/"}]},
        ],
    }
    topic_cards = "\n".join(
        f'          <li><a href="/science-bee/questions/{t[1]}/"><strong>{esc(t[3])}</strong>'
        f'<span>{c[t[0]]["little"]} Little &middot; {c[t[0]]["big"]} Big &middot; {c[t[0]]["pic"]} with pictures</span>'
        f'<span class="sb-topic-blurb">{esc(t[5])}</span></a></li>'
        for t in TOPICS
    )
    faq_html = "\n".join(f"        <h3>{esc(q)}</h3>\n        <p>{esc(a)}</p>" for q, a in faqs)
    credit_items = "\n".join(
        f'          <li>{esc(p["alt"])}: {esc(p["credit"])}, <a href="{p["licence_url"]}" rel="noopener">{esc(p["licence"])}</a>, via <a href="{esc(p["file_url"])}" rel="noopener">Wikimedia Commons</a> ({esc(p["note"])}).</li>'
        for p in PHOTOS.values()
    )
    return head(title, desc, "/science-bee/", "index,follow", ld) + f"""<body class="sb-page">
{menu()}
  <div class="wrap">
    <main>
      <p class="crumbs"><a href="/start/">&larr; Start</a></p>
      <h1>Science Bee Practice for Little Kids</h1>
      <p class="lead">A 10 to 15 minute after-dinner science game. One grown-up reads, the kids race to answer, and every round ends on an easy win.</p>
      <div class="sb-cta" role="group" aria-label="Play">
        <a class="btn" href="/science-bee/play/" data-sb-cta="round">Start tonight&rsquo;s round</a>
        <a class="btn alt" href="/science-bee/play/#buzzer" data-sb-cta="buzzer">Two-kid buzzer game</a>
      </div>
      <p class="meta">{total} original questions &middot; {n_little} Little (Pre-K&ndash;K) &middot; {n_big} Big (1st&ndash;3rd) &middot; {n_pic} picture questions &middot; one phone, no signup</p>
      <section class="box" aria-labelledby="flow-h">
        <h2 id="flow-h">How tonight&rsquo;s round goes</h2>
        <ol class="sb-steps">
          <li><strong>Move first, 1 minute.</strong> A silly science warm-up, like a crab walk or growing from a seed into a sunflower.</li>
          <li><strong>8 or 10 questions.</strong> Topics mix, with a picture or two. The first one is a gentle starter.</li>
          <li><strong>An easy win to finish.</strong> The last question is always one everyone can get.</li>
          <li><strong>Stop while it&rsquo;s still fun.</strong> A cheer, a peek at the stars, and done. Tap Play again for a fresh shuffle tomorrow.</li>
        </ol>
      </section>
      <section class="box" id="buzzer" aria-labelledby="buzz-h">
        <h2 id="buzz-h">Two kids, one phone: the buzzer game</h2>
        <ul>
          <li>Lay the phone flat between the kids. The grown-up reads the question out loud.</li>
          <li>Each kid gets a big buzzer at their end of the screen. The first tap wins the turn and locks the other buzzer.</li>
          <li>Right answer: a star. Not yet: the other kid gets a turn to try, just like a real bee.</li>
          <li>Set the younger kid to Little and answer choices pop up when they buzz in.</li>
          <li>A 10-second think timer starts only when the grown-up taps it. No sounds, nothing plays by itself.</li>
          <li>Stars are just for fun. Hide them with one tap if the score gets in the way.</li>
        </ul>
      </section>
      <section class="box" aria-labelledby="bands-h">
        <h2 id="bands-h">Two age bands</h2>
        <h3>Little: Pre-K to K</h3>
        <p>Short questions about things kids can see and touch, with two or three answer choices read aloud. Lots of picture questions.</p>
        <h3>Big: 1st to 3rd grade</h3>
        <p>Open answers, like a real bee: words like evaporation, vertebrate and photosynthesis. Stuck? Tap Give choices, then Make it simpler for two choices.</p>
      </section>
      <section class="box sb-topics" aria-labelledby="bank-h">
        <h2 id="bank-h">Question bank by topic</h2>
        <p>Every question has the answer, a gentle hint and a kind &ldquo;here&rsquo;s why&rdquo; line. Read them through, or play a round from one topic.</p>
        <ul class="steps">
{topic_cards}
        </ul>
      </section>
      <section class="box" id="print" aria-labelledby="print-h">
        <h2 id="print-h">Print a question sheet</h2>
        <p>Two pages for the car or a restaurant table: 20 Little questions on page 1 and 20 Big questions on page 2, answers at the bottom of each page.</p>
        <p><a class="btn" href="/science-bee/pdf/{PDF_NAME}" download data-sb-cta="pdf">Print PDF (US Letter)</a></p>
      </section>
      <section class="box" aria-labelledby="tips-h">
        <h2 id="tips-h">Tips for grown-ups</h2>
        <ul>
          <li>Keep it short: 10 to 15 minutes, a few nights a week. Skipping a night is fine.</li>
          <li>Cheer a good try as loudly as a right answer.</li>
          <li>Read slowly and say the whole question. For bigger kids, try reading it twice, the second time a bit faster.</li>
          <li>Let the younger sibling answer first sometimes, or give them the easy-win question.</li>
          <li>Real bee questions often start with harder clues and end with easier ones. Practice listening all the way to the end before buzzing.</li>
        </ul>
      </section>
      <section class="box faq" aria-labelledby="faq-h">
        <h2 id="faq-h">Questions from grown-ups</h2>
{faq_html}
      </section>
      <section class="box" id="credits" aria-labelledby="credits-h">
        <h2 id="credits-h">Picture credits</h2>
        <p>Most pictures are emoji or simple drawings made for this page. Three animal photos come from KidZooKit&rsquo;s animal cards:</p>
        <ul>
{credit_items}
        </ul>
      </section>
{FOOT_LINKS}
    </main>
  </div>
{SCRIPTS}</body>
</html>
"""


def build_topic(bank: list[dict], t: tuple) -> str:
    key, slug, short, long_label, noun, blurb = t
    qs = [q for q in bank if q["topic"] == key]
    title = f"Kids Science Bee Questions: {noun} | KidZooKit"
    n_l = sum(1 for q in qs if q["band"] == "little")
    n_b = len(qs) - n_l
    desc = (f"{len(qs)} {noun.lower()} questions for kids with answers, hints and kind explanations: "
            f"{n_l} for Pre-K to K, {n_b} for 1st to 3rd grade. Play a round on one phone.")
    path = f"/science-bee/questions/{slug}/"
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "LearningResource", "name": f"{noun} science bee questions for kids", "url": SITE + path,
             "description": desc, "inLanguage": "en", "educationalLevel": "Pre-K to 3rd grade",
             "learningResourceType": "Practice questions", "about": long_label,
             "isPartOf": {"@type": "LearningResource", "name": "Science Bee Practice for Kids", "url": SITE + "/science-bee/"}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Science Bee", "item": SITE + "/science-bee/"},
                {"@type": "ListItem", "position": 2, "name": noun, "item": SITE + path}]},
        ],
    }
    sections = []
    for band, label, grades in BANDS:
        items = []
        for q in [q for q in qs if q["band"] == band]:
            choices = [q["a"]] + list(q["wrong"])
            rnd = random.Random(q["id"])
            rnd.shuffle(choices)
            ch = " &middot; ".join(esc(x) for x in choices)
            items.append(
                f'          <li class="sb-q" id="{q["id"]}">{pic_html(q)}<p class="sb-q-text">{esc(q["q"])}</p>'
                f'<p class="sb-q-choices"><span class="sb-k">Choices:</span> {ch}</p>'
                f'<details><summary>Answer</summary><p><strong>{esc(q["a"])}</strong></p>'
                f'<p class="sb-q-hint"><span class="sb-k">Hint:</span> {esc(q["hint"])}</p>'
                f'<p class="sb-q-fix"><span class="sb-k">Why:</span> {esc(q["fix"])}</p></details></li>'
            )
        sections.append(
            f'      <section class="box sb-band" id="{band}" aria-labelledby="{band}-h">\n'
            f'        <h2 id="{band}-h">{label}: {grades} <small>({len(items)} questions)</small></h2>\n'
            f'        <ol class="sb-qlist">\n' + "\n".join(items) + "\n        </ol>\n      </section>"
        )
    others = " ".join(
        f'<a href="/science-bee/questions/{o[1]}/">{esc(o[3])}</a>' for o in TOPICS if o[0] != key
    )
    return head(title, desc, path, "index,follow", ld) + f"""<body class="sb-page">
{menu()}
  <div class="wrap">
    <main>
      <p class="crumbs"><a href="/science-bee/">&larr; Science Bee practice</a></p>
      <h1>{esc(noun)} Science Bee Questions for Kids</h1>
      <p class="lead">{esc(blurb)} {len(qs)} questions in two age bands, each with the answer, a gentle hint and a kind &ldquo;here&rsquo;s why&rdquo; line.</p>
      <div class="sb-cta" role="group" aria-label="Play">
        <a class="btn" href="/science-bee/play/?topic={key}" data-sb-cta="topic_round">Play a {esc(short.lower())} round</a>
        <a class="btn alt" href="#little">Little: Pre-K&ndash;K</a>
        <a class="btn alt" href="#big">Big: 1st&ndash;3rd</a>
      </div>
      <p class="use">Read a question out loud and let the kids answer before you open the answer. Little kids: read the choices too.</p>
{chr(10).join(sections)}
      <section class="box" aria-labelledby="more-h">
        <h2 id="more-h">More science bee topics</h2>
        <p class="others">{others} <a href="/science-bee/">All Science Bee practice</a></p>
      </section>
{FOOT_LINKS}
    </main>
  </div>
{SCRIPTS}</body>
</html>
"""


def build_play() -> str:
    title = "Science Bee Game: Tonight's Round | KidZooKit"
    desc = "Phone game for a 10 to 15 minute family science bee: warm-up, 8 or 10 questions, a two-kid buzzer and an easy win to finish."
    return head(title, desc, "/science-bee/play/", "noindex,follow", None) + f"""<body class="sb-page sb-play">
{menu()}
  <main id="sb-app" class="sb-app" aria-live="polite">
    <noscript><p class="box">The game needs JavaScript. The questions are also on the <a href="/science-bee/">Science Bee page</a> to read aloud.</p></noscript>
    <p class="sb-loading">Loading the questions&hellip;</p>
  </main>
  <p class="sb-disclaim sb-app">Practice inspired by kid science bees. Original questions written for KidZooKit; not connected to or endorsed by any competition.</p>
  <script src="/science-bee/sb-questions-v1.js?v={ASSET_V['bank']}"></script>
  <script src="/science-bee/sb-game-v1.js?v={ASSET_V['js']}"></script>
{SCRIPTS}</body>
</html>
"""


def pick_sheet(bank: list[dict], band: str, n: int) -> list[dict]:
    """Deterministic, topic-balanced pick of non-picture questions for print."""
    out: list[dict] = []
    per = {t[0]: [q for q in bank if q["topic"] == t[0] and q["band"] == band and not q.get("pic")] for t in TOPICS}
    i = 0
    while len(out) < n:
        for t in TOPICS:
            lst = per[t[0]]
            # Every other question, so the sheet spreads across each topic.
            if 2 * i < len(lst) and len(out) < n:
                out.append(lst[2 * i])
        i += 1
    return out


def build_print(bank: list[dict]) -> str:
    def block(band: str, label: str, qs: list[dict]) -> str:
        lis = []
        for q in qs:
            choices = [q["a"]] + list(q["wrong"])
            random.Random(q["id"]).shuffle(choices)
            ch = " / ".join(esc(x) for x in choices)
            lis.append(f'<li><span class="q">{esc(q["q"])}</span>' + (f'<span class="c">{ch}</span>' if band == "little" else f'<span class="c c-big">Choices if stuck: {ch}</span>') + "</li>")
        answers = " &middot; ".join(f"<b>{i}</b>&nbsp;{esc(q['a'])}" for i, q in enumerate(qs, 1))
        return (f'<h2>{label}</h2><ol>' + "".join(lis) + "</ol>"
                f'<div class="ans"><h3>Answers ({label.split(":")[0]})</h3><p>{answers}</p></div>')
    little = pick_sheet(bank, "little", 20)
    big = pick_sheet(bank, "big", 20)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>KidZooKit Science Bee practice sheet v1</title>
<meta name="robots" content="noindex,nofollow">
<style>
@page{{size:Letter;margin:0.5in}}
body{{font-family:"DejaVu Sans",system-ui,sans-serif;color:#152238;font-size:10pt;line-height:1.28;margin:0}}
h1{{font-size:17pt;margin:0 0 2pt;color:#0a4545}} .sub{{margin:0 0 8pt;color:#3d4f6f}}
h2{{font-size:12.5pt;margin:6pt 0 6pt;color:#0a4545;border-bottom:1.5pt solid #0f5c5c}}
h3{{font-size:10pt;margin:0 0 2pt;color:#0a4545}}
ol{{margin:0;padding-left:18pt;columns:2;column-gap:22pt}} li{{margin:0 0 7pt;break-inside:avoid}}
.q{{display:block;font-weight:700}} .c{{display:block;color:#3d4f6f}} .c-big{{font-size:8.6pt}}
.page{{page-break-after:always}} .page:last-child{{page-break-after:auto}}
.ans{{margin-top:8pt;border-top:1pt dashed #9aa7b8;padding-top:5pt;font-size:8.6pt;color:#3d4f6f}} .ans p{{margin:0}}
.foot{{margin-top:8pt;font-size:8.5pt;color:#3d4f6f}}
</style></head><body>
<div class="page"><h1>Science Bee practice sheet</h1><p class="sub">Grown-up reads aloud. Little: read the choices too. Big: let them answer first, then offer the choices if stuck. Answers are at the bottom; fold it under.</p>
{block('little','Little: Pre-K to K',little)}
<p class="foot">kidzookit.com/science-bee &middot; Original practice questions. Not connected to or endorsed by any competition.</p></div>
<div class="page">{block('big','Big: 1st to 3rd grade',big)}
<p class="foot">Play these and {len(bank) - 40} more on one phone, with a two-kid buzzer: kidzookit.com/science-bee</p></div>
</body></html>
"""


def main() -> None:
    bank = load_bank()
    (ROOT / "sb-questions-v1.js").write_text(build_bank_js(bank), encoding="utf-8")
    (ROOT / "index.html").write_text(build_hub(bank), encoding="utf-8")
    for t in TOPICS:
        d = ROOT / "questions" / t[1]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(build_topic(bank, t), encoding="utf-8")
    (ROOT / "play").mkdir(exist_ok=True)
    (ROOT / "play" / "index.html").write_text(build_play(), encoding="utf-8")
    if len(sys.argv) > 2 and sys.argv[1] == "--print-html":
        # Source for the versioned PDF; not served (lives outside static/).
        Path(sys.argv[2]).write_text(build_print(bank), encoding="utf-8")
    print(f"science bee: {len(bank)} questions; wrote hub, {len(TOPICS)} topic pages, play, print, bank js")


if __name__ == "__main__":
    main()
