#!/usr/bin/env python3
"""Generate indexable Field Trip Kit venue pages + sitemap/robots.

Run from repo root:
  python3 scripts/generate_bdo_seo.py

Outputs:
  static/field-pack/<venue-id>/index.html  (×N)
  static/sitemap.xml
  static/robots.txt
  static/field-pack/seo-venues.json        (machine list of URLs)
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FIELD = REPO / "static" / "field-pack"
VENUE_DATA_DIR = FIELD / "data" / "venues"
CHALLENGES_JSON = FIELD / "data" / "challenges.json"
WONDERS_JSON = FIELD / "data" / "wonders.json"
BONUS_HUNTS_JSON = FIELD / "data" / "bonus-hunts.json"
MISSION_ENGINE = FIELD / "js" / "mission" / "mission-engine.js"
STATIC = REPO / "static"
CATALOG_JS = FIELD / "js" / "catalog.js"
PLACES_JS = FIELD / "js" / "places-data.js"
SITE = "https://1less.app"
TODAY = date.today().isoformat()

RESERVED = {
    "app.html",
    "css",
    "img",
    "index.html",
    "js",
    "photos",
    "places",
    "seo-venues.json",
    "zoos",
    "aquariums",
    "museums",
    "national-parks",
    "parks",
    "media",
    "cards",
}

# Type hub landings: path segment → filter + copy
HEADER_TAGLINE = "Zoo, aquarium, museum &amp; park days"
OG_SHARE_IMAGE = f"{SITE}/field-pack/photos/sample-mission-dallas-zoo.jpg"
PARK_OG_IMAGE = f"{SITE}/field-pack/photos/np-hero-yellowstone.jpg"

# Dual-mode framing — at home stands alone; print is an optional visit companion.
# Swap these strings only; templates read the constants.
NAV_PLACES_SUB = "Map &amp; places"
NAV_CARDS_SUB = "Talk, photos &amp; Q&amp;A"
NAV_VFT_SUB = "Explore at home"
NAV_ABOUT_SUB = "1Less &amp; contact"

CTA_EXPLORE_HOME = "Explore at home"
CTA_PRINT_VISIT = "Print a hunt for the visit"
CTA_PRINT_VISIT_SHORT = "Print a hunt"
CTA_PRINT_CARD = "Print this card"
CTA_READY = "Explore →"

HOME_SESSION_H2 = "Explore at home"
HOME_SESSION_LEAD = (
    "Talk through the cards, look at the photos, and open a live cam or film when we have one. "
    "This works on a phone or laptop — no printer needed."
)
HOME_SESSION_VFT = "Open Virtual Field Trip"
START_HERE_H2 = "Start here"
START_HERE_LEAD = (
    "At home, open a card for talk, photos, and a cam when we have one. "
    "Going in person? Add a stop to the hunt — print only if you want paper."
)
CTA_TALK_HOME = "Talk at home"
CTA_ADD_HUNT = "Add to hunt"
CTA_ZOO_CARDS = "This zoo's cards"
HOME_CARD_MORE = "Open card — 6 talk questions"
SHORTLIST_LEAD = "Open a card for talk tips, photos, and Q&amp;A."
HUNT_BLOCK_P = (
    "Optional for a real visit. Print a one-page hunt from the button above, "
    "or skip paper and use the cards on this page."
)
PRINT_FALLBACK = (
    "At home? Use the cards below — no printer needed. "
    "Going in person? Print a hunt, or open the sheet on your phone."
)

# Catalog outing template — same wording as FIELD_PACK_MISSIONS_* in catalog.js.
# Public cards use this 6-question set. Do not invent new Q&A. Do not ship notice-stubs as “full.”
OUTING_TALK_ANIMAL = (
    {
        "id": "food",
        "num": "1",
        "title": "Food detective",
        "question": "What do they eat?",
        "choices": ["Plants / leaves", "Meat", "Both", "Insects", "Fish", "Bamboo / special"],
        "multi": True,
        "key_field": "food",
        "open_note": "",
    },
    {
        "id": "home",
        "num": "2",
        "title": "Home map",
        "question": "Where is home?",
        "choices": ["Forest", "Water / wet", "Desert / dry", "Cold / snow", "Grassland", "Zoo / tank house"],
        "multi": True,
        "key_field": "home",
        "open_note": "",
    },
    {
        "id": "superpower",
        "num": "3",
        "title": "Superpower",
        "question": "What is their superpower?",
        "choices": ["Climb", "Swim", "Hide", "Run fast", "Stomp / strong", "Fly"],
        "multi": True,
        "key_field": "superpower",
        "open_note": "",
    },
    {
        "id": "grow",
        "num": "4",
        "title": "Grow up",
        "question": "Baby or grown-up?",
        "choices": ["Baby / young", "Grown-up", "Not sure yet"],
        "multi": False,
        "key_field": "",
        "open_note": "Your eyes decide — baby or grown-up from what you saw!",
    },
    {
        "id": "cam",
        "num": "5",
        "title": "Live check",
        "question": "Did we see one live?",
        "choices": ["Yes — at the place", "Yes — on a screen/cam", "Not today", "Want to try later"],
        "multi": True,
        "key_field": "",
        "open_note": "Your adventure — whatever is true for you!",
    },
    {
        "id": "teach",
        "num": "6",
        "title": "Teach time",
        "question": "I want to teach about…",
        "choices": ["Their food", "Their home", "Their body", "Baby / family", "A fun fact", "My photo"],
        "multi": True,
        "key_field": "",
        "open_note": "You pick what to teach a grown-up!",
    },
)
OUTING_TALK_EXHIBIT = (
    {
        "id": "try",
        "num": "1",
        "title": "I tried",
        "question": "What did I do here?",
        "choices": ["Climb", "Build / make", "Splash / water", "Pretend play", "Art / create", "Quiet look"],
        "multi": True,
        "key_field": "try",
        "open_note": "",
    },
    {
        "id": "body",
        "num": "2",
        "title": "My body",
        "question": "How did I move?",
        "choices": ["Ran / jumped", "Climbed high", "Used hands a lot", "Sat and focused", "Splashed", "Slow and careful"],
        "multi": True,
        "key_field": "body",
        "open_note": "",
    },
    {
        "id": "senses",
        "num": "3",
        "title": "Senses",
        "question": "What did I notice?",
        "choices": ["Colors", "Sounds", "Textures / touch", "Water", "Something funny", "Something new"],
        "multi": True,
        "key_field": "senses",
        "open_note": "",
    },
    {
        "id": "feel",
        "num": "4",
        "title": "Feelings",
        "question": "How did it feel?",
        "choices": ["Exciting", "Calm", "Tricky", "Proud", "Silly", "Not sure yet"],
        "multi": True,
        "key_field": "",
        "open_note": "All feelings are OK — this is your story!",
    },
    {
        "id": "again",
        "num": "5",
        "title": "Again?",
        "question": "Would I do this again?",
        "choices": ["Yes — favorite!", "Yes — once more", "Maybe later", "No thanks"],
        "multi": False,
        "key_field": "",
        "open_note": "Your choice!",
    },
    {
        "id": "teach",
        "num": "6",
        "title": "Teach time",
        "question": "I want to teach about…",
        "choices": ["How to play here", "What I built", "A funny moment", "A tip for next time", "My favorite part", "A photo"],
        "multi": True,
        "key_field": "",
        "open_note": "You pick what to teach a grown-up!",
    },
)

SEO_CSS_VER = "23"
LANDING_CSS_VER = "95"
STYLES_CSS_VER = "35"

# Landing catalog seeds (T5) — review in POLISH-TASKS completion notes
FEATURED_CARD_IDS = (
    "african-lion",
    "shark",
    "sci-dinosaur",
    "reticulated-giraffe",
    "octopus",
    "sci-rocket",
    "giant-panda",
    "jellyfish",
    "cm-makery",
    "african-elephant",
    "clownfish",
    "sea-turtle",
)
FEATURED_BY_GROUP = {
    "wildlife": (
        "african-lion",
        "reticulated-giraffe",
        "giant-panda",
        "african-elephant",
        "western-lowland-gorilla",
        "sumatran-tiger",
        "nile-hippo",
        "african-penguin",
        "caribbean-flamingo",
        "asian-small-clawed-otter",
        "cheetah",
        "chimpanzee",
    ),
    "sealife": (
        "shark",
        "octopus",
        "jellyfish",
        "clownfish",
        "sea-turtle",
        "stingray",
        "seahorse",
        "eel",
        "crab",
        "starfish",
        "freshwater-fish",
    ),
    "attractions": (
        "sci-rocket",
        "sci-dinosaur",
        "cm-makery",
        "sci-hands-on",
        "sci-mammal-hall",
        "sci-planet",
        "sci-rainforest",
        "cm-art-lab",
        "cm-imaginarium",
        "sci-astronaut",
        "cm-woven",
        "sci-aquarium-zone",
    ),
}
POPULAR_VENUE_IDS = (
    "dallas-zoo",
    "san-diego-zoo",
    "bronx-zoo",
    "national-zoo",
    "georgia-aquarium",
    "monterey-bay-aquarium",
    "amnh",
    "childrens-museum-perot",
    "yellowstone",
    "grand-canyon",
    "yosemite",
    "zion",
)

TYPE_LANDINGS = [
    {
        "path": "zoos",
        "kind": "zoo",
        "nav": "Zoos",
        "title": "Virtual Zoo Days & Printable Hunts for Kids · Field Trip Kit",
        "h1": "Explore a zoo at home — or print a hunt",
        "blurb": "Animal cards, talk prompts, photos, and live cams for a zoo session at home. Optional one-page hunt if you’re going in person.",
        "map_type": "zoo",
        "pitch": "Cards and cams at home · optional hunt for the visit",
    },
    {
        "path": "aquariums",
        "kind": "aquarium",
        "nav": "Aquariums",
        "title": "Virtual Aquarium Days & Printable Hunts for Kids · Field Trip Kit",
        "h1": "Explore an aquarium at home — or print a hunt",
        "blurb": "Sea-life cards, talk prompts, photos, and live cams when we have them. Optional one-page hunt for a real visit.",
        "map_type": "aquarium",
        "pitch": "Cards and cams at home · optional hunt for the visit",
    },
    {
        "path": "museums",
        "kind": "museum",
        "nav": "Museums",
        "title": "Virtual Museum Days & Printable Hunts for Kids · Field Trip Kit",
        "h1": "Explore a museum at home — or print a hunt",
        "blurb": "Attraction cards, talk prompts, and photos for science, natural history, space, and children’s museums. Optional printable hunt for the visit.",
        "map_type": "museum",
        "pitch": "Cards at home · optional hunt for the visit",
    },
    {
        "path": "national-parks",
        "kind": "park",
        "nav": "Parks",
        "title": "Virtual Park Days & Printable Hunts for Kids · Field Trip Kit",
        "h1": "Explore a park at home — or print a hunt",
        "blurb": "Maps, photos, and Virtual Field Trip stops for U.S. and international parks. Optional one-page hunt for one finishable slice (rim, boardwalk, lakeshore).",
        "map_type": "park",
        "pitch": "Explore at home · optional hunt for one park slice",
    },
]


def venue_type_kind(v: dict) -> str:
    """Map venue/place type → zoo | aquarium | museum | park | other."""
    raw = str(v.get("type") or v.get("placeType") or "").lower().strip()
    t = raw.replace("-", "_").replace(" ", "_")
    # Short catalog codes first
    if t in ("aq",) or "aquarium" in t:
        return "aquarium"
    if t in ("national_park", "park") or "national_park" in t:
        return "park"
    if t in ("safari_zoo",) or "safari" in t:
        return "zoo"
    if t in ("zoo", "zoo_aq") or t.endswith("_zoo") or t.startswith("zoo"):
        return "zoo"
    if t in (
        "sci",
        "nh",
        "cm",
        "sci_aq",
        "science",
        "natural_history",
        "childrens_museum",
        "space",
    ) or any(
        x in t
        for x in (
            "museum",
            "science",
            "natural",
            "history",
            "children",
            "space",
            "air",
        )
    ):
        return "museum"
    return "other"

TYPE_PHRASE = {
    "zoo": ("zoo", "animals", "scavenger hunt"),
    "safari_zoo": ("safari park", "animals", "scavenger hunt"),
    "zoo_aq": ("zoo and aquarium", "animals", "scavenger hunt"),
    "aquarium": ("aquarium", "sea life", "scavenger hunt"),
    "aq": ("aquarium", "sea life", "scavenger hunt"),
    "sci_aq": ("science museum and aquarium", "exhibits", "scavenger hunt"),
    "childrens_museum": ("children's museum", "play zones", "scavenger hunt"),
    "cm": ("children's museum", "play zones", "scavenger hunt"),
    "science": ("science museum", "exhibits", "scavenger hunt"),
    "sci": ("science museum", "exhibits", "scavenger hunt"),
    "natural_history": ("natural history museum", "exhibits", "scavenger hunt"),
    "nh": ("natural history museum", "exhibits", "scavenger hunt"),
    "space": ("space center", "exhibits", "scavenger hunt"),
    "national_park": ("national park", "trails and overlooks", "scavenger hunt"),
    "park": ("national park", "trails and overlooks", "scavenger hunt"),
}


def esc(s: str) -> str:
    return (
        str(s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def nav_more_menu_html(*, current: str = "") -> str:
    """Shared More menu — keep VFT subtitle dual-mode, not print-first."""

    def item(href: str, label: str, sub: str, key: str) -> str:
        cur = ' aria-current="page"' if current == key else ""
        return (
            f'<a href="{href}"{cur} role="menuitem">{label}<small>{sub}</small></a>'
        )

    return f"""      <div class="shell-more-wrap">
        <button type="button" class="shell-more" aria-expanded="false" aria-haspopup="true" aria-controls="shell-menu">More</button>
        <div id="shell-menu" class="shell-menu" hidden role="menu">
          {item("/field-pack/", "All places", NAV_PLACES_SUB, "places")}
          {item("/field-pack/cards/", "Animal cards", NAV_CARDS_SUB, "cards")}
          {item("/field-pack/virtual-field-trip/", "Virtual Field Trip", NAV_VFT_SUB, "vft")}
          {item("/field-pack/#about", "About", NAV_ABOUT_SUB, "about")}
        </div>
      </div>"""


_CATALOG_DEPTH: dict[str, dict] | None = None
_VFT_BY_CARD: dict[str, dict] | None = None


def load_catalog_depth() -> dict[str, dict]:
    """FIELD_PACK_CATALOG entries with talk keys + links. No new facts."""
    script = r"""
const fs = require('fs');
const vm = require('vm');
const ctx = { window: {}, console };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[1], 'utf8'), ctx);
const cat = ctx.window.FIELD_PACK_CATALOG || {};
const out = {};
for (const [id, it] of Object.entries(cat)) {
  if (!it || !it.name) continue;
  out[id] = {
    id,
    name: it.name,
    emoji: it.emoji || '',
    photo: String(it.photo || ''),
    blurb: String(it.blurb || it.one_liner || ''),
    key: it.key && typeof it.key === 'object' ? it.key : {},
    links: it.links && typeof it.links === 'object' ? it.links : {},
    packTemplate: it.packTemplate || (String(id).startsWith('cm-') || String(id).startsWith('sci-') ? 'exhibits' : 'animals'),
  };
}
process.stdout.write(JSON.stringify(out));
"""
    raw = subprocess.check_output(["node", "-e", script, str(CATALOG_JS)], text=True)
    return json.loads(raw)


def catalog_depth() -> dict[str, dict]:
    global _CATALOG_DEPTH
    if _CATALOG_DEPTH is None:
        try:
            _CATALOG_DEPTH = load_catalog_depth()
        except Exception:
            _CATALOG_DEPTH = {}
    return _CATALOG_DEPTH


def load_vft_by_card() -> dict[str, dict]:
    """Index Virtual Field Trip habitats by catalog cardId. Cams/films only if already sourced."""
    out: dict[str, dict] = {}
    vdir = FIELD / "data" / "virtual-venues"
    files = (
        "virtual-zoo.json",
        "virtual-aquarium.json",
        "virtual-nhm.json",
        "virtual-science.json",
        "virtual-parks.json",
    )
    for name in files:
        path = vdir / name
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        tab = str(data.get("tab") or data.get("kind") or "").strip()
        for h in data.get("habitats") or []:
            cid = str(h.get("cardId") or h.get("id") or "").strip()
            if not cid or cid in out:
                continue
            cam = h.get("cam") or {}
            video = h.get("video") or {}
            cam_url = str(cam.get("url") or "").strip()
            film_url = str(video.get("url") or "").strip()
            hid = str(h.get("id") or cid)
            out[cid] = {
                "tab": tab,
                "habitat_id": hid,
                "label": h.get("label") or "",
                "cam_url": cam_url,
                "cam_label": str(cam.get("camLabel") or "").strip(),
                "film_url": film_url,
                "film_title": str(video.get("title") or "").strip(),
                "vft_href": f"/field-pack/virtual-field-trip/?tab={esc(tab)}#habitat={esc(hid)}",
            }
    return out


def vft_by_card() -> dict[str, dict]:
    global _VFT_BY_CARD
    if _VFT_BY_CARD is None:
        _VFT_BY_CARD = load_vft_by_card()
    return _VFT_BY_CARD


def enrich_item(it: dict) -> dict:
    """Merge catalog DEPTH + VFT onto a shortlist/card item. Never invent facts."""
    cid = str(it.get("id") or "").strip()
    depth = catalog_depth().get(cid) or {}
    out = dict(it)
    if depth.get("key") and not out.get("key"):
        out["key"] = depth["key"]
    if depth.get("links") and not out.get("links"):
        out["links"] = depth["links"]
    if depth.get("photo") and not out.get("photo"):
        out["photo"] = depth["photo"]
    if depth.get("blurb") and not _card_blurb(out.get("blurb") or ""):
        if not out.get("blurb"):
            out["blurb"] = depth.get("blurb") or ""
    if depth.get("emoji") and not out.get("emoji"):
        out["emoji"] = depth["emoji"]
    if depth.get("name") and not out.get("name"):
        out["name"] = depth["name"]
    out["packTemplate"] = out.get("packTemplate") or depth.get("packTemplate") or "animals"
    out["vft"] = vft_by_card().get(cid) or {}
    if it.get("qa_card") and not out.get("qa_card"):
        out["qa_card"] = it["qa_card"]
    return out


def is_generic_notice_qa(question: str, answer: str) -> bool:
    """Venue stubs like “What did you notice about X?” are not full Q&A."""
    q = (question or "").strip().lower()
    a = (answer or "").strip().lower()
    if q.startswith("what did you notice about"):
        return True
    if "tell a grown-up one thing you saw" in a:
        return True
    return False


def _key_values(key: dict, field: str) -> set[str]:
    raw = (key or {}).get(field)
    if isinstance(raw, list):
        return {str(x).strip() for x in raw if str(x).strip()}
    val = str(raw or "").strip()
    return {val} if val else set()


def outing_missions_for(item: dict) -> tuple[dict, ...]:
    pt = str(item.get("packTemplate") or "")
    key = item.get("key") or {}
    if pt == "exhibits" or any(k in key for k in ("try", "body", "senses")):
        return OUTING_TALK_EXHIBIT
    return OUTING_TALK_ANIMAL


def real_extra_qa_pairs(item: dict) -> list[tuple[str, str]]:
    """Venue qa_card only when it is not a notice stub. VFT stops own no facts."""
    pairs: list[tuple[str, str]] = []
    qa = item.get("qa_card") or {}
    if not isinstance(qa, dict):
        return pairs
    q, a = str(qa.get("question") or "").strip(), str(qa.get("answer") or "").strip()
    if q and a and not is_generic_notice_qa(q, a):
        pairs.append((q, a))
    return pairs


def real_extra_qa_html(item: dict, *, heading: str = "More talk") -> str:
    bits = [f"<dt>{esc(q)}</dt><dd>{esc(a)}</dd>" for q, a in real_extra_qa_pairs(item)]
    if not bits:
        return ""
    return (
        f'<div class="seo-talk-qa">'
        f"<h3>{heading}</h3>"
        f"<dl>{''.join(bits)}</dl>"
        f"</div>"
    )


def outing_talk_html(item: dict) -> str:
    """On-screen 6-question outing template from catalog.js. No invented Q&A."""
    key = item.get("key") or {}
    cards: list[str] = []
    for m in outing_missions_for(item):
        hints = _key_values(key, m["key_field"]) if m.get("key_field") else set()
        choices = []
        for label in m["choices"]:
            on = label in hints
            choices.append(
                f'<button type="button" class="choice" data-choice="{esc(label)}" '
                f'aria-pressed="{"true" if on else "false"}">'
                f'<span class="dot" aria-hidden="true"></span>'
                f"<span>{esc(label)}</span></button>"
            )
        note = f'<p class="card-talk-note">{esc(m["open_note"])}</p>' if m.get("open_note") else ""
        cards.append(
            f'<section class="mission card-talk-q" data-mission="{esc(m["id"])}">'
            f'<div class="mission-head"><span class="badge">{esc(m["num"])}</span>'
            f'<p class="mission-title">{esc(m["title"])}</p></div>'
            f'<h3 class="mission-q">{esc(m["question"])}</h3>'
            f'<div class="choices" data-multi="{"1" if m.get("multi") else "0"}">'
            f"{''.join(choices)}</div>{note}</section>"
        )
    extra = real_extra_qa_html(item)
    return (
        f'<section class="card-talk-pack" aria-label="Six talk questions">'
        f'<p class="step-chip">6 questions · talk, tap, or print</p>'
        f'<div class="mission-grid">{"".join(cards)}</div>'
        f"{extra}</section>"
    )


def catalog_more_links_html(item: dict) -> str:
    """Photos / learn-more from catalog.links. Prefer VFT cam over catalog cam."""
    links = item.get("links") or {}
    vft = item.get("vft") or {}
    bits: list[str] = []
    if not vft.get("cam_url"):
        cam = str(links.get("cam") or "").strip()
        if cam:
            bits.append(
                f'<a class="btn btn-ghost" href="{esc(cam)}" target="_blank" rel="noopener noreferrer">Live cam</a>'
            )
    pics = str(links.get("pictures") or "").strip()
    if pics:
        bits.append(
            f'<a class="btn btn-ghost" href="{esc(pics)}" target="_blank" rel="noopener noreferrer">Photos</a>'
        )
    more = str(links.get("more") or "").strip()
    if more:
        bits.append(
            f'<a class="btn btn-ghost" href="{esc(more)}" target="_blank" rel="noopener noreferrer">Learn more</a>'
        )
    if not bits:
        return ""
    return f'<div class="action-row detail-links detail-links-quiet no-print">{"".join(bits)}</div>'


def venue_real_qa_for_card(cid: str, vid: str) -> dict:
    """Real qa_card from this card’s home venue JSON, if it is not a notice stub."""
    if not cid or not vid:
        return {}
    mv = load_mission_venue(vid)
    if not mv:
        return {}
    for it in mv.get("items") or []:
        if (it.get("catalog_id") or "").strip() != cid:
            continue
        qa = it.get("qa_card") or {}
        if not isinstance(qa, dict):
            return {}
        q, a = str(qa.get("question") or ""), str(qa.get("answer") or "")
        if q and a and not is_generic_notice_qa(q, a):
            return {"question": q, "answer": a}
        return {}
    return {}


def watch_links_html(item: dict) -> str:
    """Live cam / film only when Virtual Field Trip already has a sourced URL."""
    vft = item.get("vft") or {}
    links: list[str] = []
    if vft.get("cam_url"):
        label = vft.get("cam_label") or "Watch live cam"
        links.append(
            f'<a class="seo-watch-link" href="{esc(vft["cam_url"])}" target="_blank" rel="noopener noreferrer">{esc(label)}</a>'
        )
    if vft.get("film_url"):
        label = vft.get("film_title") or "Watch a short film"
        links.append(
            f'<a class="seo-watch-link" href="{esc(vft["film_url"])}" target="_blank" rel="noopener noreferrer">{esc(label)}</a>'
        )
    if vft.get("vft_href") and (vft.get("cam_url") or vft.get("film_url")):
        links.append(
            f'<a class="seo-watch-link" href="{vft["vft_href"]}">{esc(HOME_SESSION_VFT)}</a>'
        )
    if not links:
        return ""
    return f'<p class="seo-watch-row">{" · ".join(links)}</p>'


def home_session_html(items: list[dict], *, venue_kind: str = "") -> str:
    """First-class at-home block: catalog cards + talk Q&A + existing VFT cams/films."""
    cards: list[str] = []
    for raw in items[:12]:
        it = enrich_item(raw)
        cid = str(it.get("id") or "").strip()
        if not cid:
            continue
        src = _photo_src(it.get("photo") or "")
        if not src:
            if (FIELD / "photos" / f"{cid}.jpg").is_file():
                src = f"photos/{cid}.jpg?v=img2"
        emoji = it.get("emoji") or ""
        name = it.get("name") or cid
        blurb = _card_blurb(it.get("blurb") or "") or (it.get("blurb") or "")
        extra = real_extra_qa_html(it)
        watch = watch_links_html(it)
        href = f"/field-pack/cards/{esc(cid)}/"
        if src:
            media = (
                f'<img src="{esc(src)}" alt="" width="640" height="400" loading="lazy" decoding="async" />'
            )
        else:
            media = f'<span class="seo-start-emoji" aria-hidden="true">{esc(emoji or "✨")}</span>'
        cards.append(
            f"""<article class="seo-home-card" id="home-{esc(cid)}">
        <a class="seo-home-card-media" href="{href}">{media}</a>
        <div class="seo-home-card-body">
          <h3><a href="{href}">{esc(emoji + " " if emoji else "")}{esc(name)}</a></h3>
          {f"<p class='seo-home-blurb'>{esc(blurb)}</p>" if blurb else ""}
          {extra}
          {watch}
          <p class="seo-home-card-more"><a href="{href}">{esc(HOME_CARD_MORE)}</a></p>
        </div>
      </article>"""
        )
    kind = (venue_kind or "").lower()
    if "aquarium" in kind:
        vft_tab = "aquarium"
    elif "museum" in kind or kind in {"sci", "nh", "cm"}:
        vft_tab = "science"
    elif "park" in kind:
        vft_tab = "parks"
    else:
        vft_tab = "zoo"
    vft_href = f"/field-pack/virtual-field-trip/?tab={vft_tab}"
    grid = f'<div class="seo-home-grid">{"".join(cards)}</div>' if cards else ""
    empty = (
        ""
        if cards
        else (
            f'<p class="seo-home-empty">No animal cards for this place yet. '
            f'<a href="{esc(vft_href)}">{esc(HOME_SESSION_VFT)}</a> still works at home.</p>'
        )
    )
    return f"""
    <section class="seo-home-session" id="at-home" aria-labelledby="home-session-heading">
      <h2 id="home-session-heading">{esc(HOME_SESSION_H2)}</h2>
      <p class="seo-home-lead">{esc(HOME_SESSION_LEAD)}</p>
      <p class="seo-home-vft"><a class="btn btn-secondary" href="{esc(vft_href)}">{esc(HOME_SESSION_VFT)}</a></p>
      {grid}
      {empty}
    </section>"""


def load_venues() -> list[dict]:
    """Extract venues via Node (same source of truth as the app)."""
    script = r"""
const fs = require('fs');
const vm = require('vm');
const ctx = { window: {}, console };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[1], 'utf8'), ctx);
vm.runInContext(fs.readFileSync(process.argv[2], 'utf8'), ctx);
const venues = ctx.window.FIELD_PACK_VENUES;
const places = ctx.window.FP_PLACES;
const catalog = ctx.window.FIELD_PACK_CATALOG;
const byId = Object.fromEntries(places.map(p => [p.id, p]));
const out = Object.keys(venues).map(id => {
  const ven = venues[id];
  const pl = byId[id] || {};
  const idList = [...new Set([...(ven.featuredAnimalIds || []), ...(ven.animalIds || [])])];
  const items = idList.slice(0, 12).map(iid => {
    const it = catalog[iid];
    if (!it) return null;
    return {
      id: iid,
      name: it.name,
      emoji: it.emoji || '',
      blurb: it.blurb || '',
      photo: it.photo || '',
      key: it.key && typeof it.key === 'object' ? it.key : {},
      links: it.links && typeof it.links === 'object' ? it.links : {},
      packTemplate: it.packTemplate || '',
    };
  }).filter(Boolean);
  const hunt = (ven.treasureHunt || []).map(h => h.text);
  return {
    id,
    name: ven.name,
    shortName: ven.shortName || ven.name,
    location: ven.location || [pl.city, pl.state || pl.country].filter(Boolean).join(', '),
    city: pl.city || '',
    state: pl.state || '',
    country: pl.country || ven.country || '',
    lat: pl.lat != null ? pl.lat : (ven.lat != null ? ven.lat : null),
    lng: pl.lon != null ? pl.lon : (pl.lng != null ? pl.lng : (ven.lng != null ? ven.lng : null)),
    type: ven.type || pl.type || 'zoo',
    blurb: ven.blurb || pl.blurb || '',
    website: ven.website || '',
    emoji: pl.emoji || '',
    tier: pl.tier || '',
    itemLabel: ven.itemLabel || 'things',
    packTemplate: ven.packTemplate || 'animals',
    quality: ven.quality || 'starter',
    lastVerified: ven.lastVerified || '',
    featured: items,
    hunt,
  };
});
process.stdout.write(JSON.stringify(out));
"""
    proc = subprocess.run(
        ["node", "-e", script, str(CATALOG_JS), str(PLACES_JS)],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


def type_bits(v: dict) -> tuple[str, str, str]:
    t = (v.get("type") or "zoo").lower().replace(" ", "_").replace("-", "_")
    place, things, hunt = TYPE_PHRASE.get(t, ("attraction", "things to find", "scavenger hunt"))
    return place, things, hunt


def pick(seed: str, options: list[str]) -> str:
    h = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    return options[h % len(options)]



def status_chip_html(mission_venue: dict) -> str:
    """Honest list status — never claim Verified without presence audit."""
    conf = (mission_venue or {}).get("list_confidence") or ""
    audited = (mission_venue or {}).get("last_presence_audit") or ""
    month = audited[:7] if len(audited) >= 7 else ""
    if conf == "audited" and month:
        return (
            f'<p class="seo-checked seo-checked-verified">'
            f'✓ Verified with venue website · {esc(month)}</p>'
        )
    if conf == "partial":
        m = month or ((mission_venue or {}).get("last_verified") or "")[:7]
        extra = f" · {esc(m)}" if m else ""
        return (
            f'<p class="seo-checked seo-checked-partial">'
            f'Local shortlist · confirm on arrival{extra}</p>'
        )
    # template / unknown
    return (
        '<p class="seo-checked seo-checked-starter">'
        'Starter hunt · flexible finds — skip anything closed</p>'
    )


def print_status_line(mission_venue: dict) -> str:
    conf = (mission_venue or {}).get("list_confidence") or ""
    audited = (mission_venue or {}).get("last_presence_audit") or ""
    month = audited[:7] if len(audited) >= 7 else ""
    if conf == "audited" and month:
        return f"Verified {month}"
    if conf == "partial":
        return "Confirm on arrival"
    return "Flexible finds"


def practical_chips_html(practical: dict | None, last_v: str = "") -> str:
    """Scannable venue facts — duration, energy, tickets, transit. No paragraph soup."""
    p = practical or {}
    chips: list[tuple[str, str]] = []
    if p.get("typical_duration"):
        chips.append(("Time", str(p["typical_duration"])))
    if p.get("energy_note"):
        chips.append(("Setting", str(p["energy_note"])))
    if p.get("ticket_note"):
        chips.append(("Tickets", str(p["ticket_note"])))
    if p.get("transit_note"):
        chips.append(("Get there", str(p["transit_note"])))
    if not chips and not last_v:
        return ""
    lis = "".join(
        f'<li class="seo-fact-chip"><span class="seo-fact-k">{esc(k)}</span>'
        f'<span class="seo-fact-v">{esc(val)}</span></li>'
        for k, val in chips
    )
    return f"""
        <ul class="seo-fact-chips" aria-label="Visit facts">{lis}</ul>"""


def unique_body(
    v: dict,
    exclude_ids: set[str] | None = None,
) -> str:
    """Visual shortlist + hunt checklist. No long SEO prose walls."""
    featured_all = v.get("featured") or []
    # Prefer remaining stops when “start here” already showed the first picks
    exclude_ids = exclude_ids or set()
    featured_rest = [it for it in featured_all if it.get("id") not in exclude_ids]
    featured = featured_rest if len(featured_rest) >= 2 else featured_all
    hunt = v.get("hunt") or []

    # Photo cards first (visual), plus crawlable text for SEO
    cards = []
    feat_html_parts = []
    for it in featured[:12]:
        photo = (it.get("photo") or "").strip()
        # Catalog paths are like photos/foo.jpg; base href is /field-pack/
        if photo and not photo.startswith("/") and not photo.startswith("http"):
            src = photo
        elif photo.startswith("/field-pack/"):
            src = photo[len("/field-pack/") :]
        else:
            src = photo
        alt = f"{it.get('name') or 'Animal'} — shortlist photo"
        item_blurb = _card_blurb(it.get("blurb") or "") or "Worth a look if you have time."
        item_id = it.get("id") or ""
        card_inner = ""
        if src:
            card_inner = f"""<img src="{esc(src)}" alt="{esc(alt)}" width="640" height="400" loading="lazy" decoding="async" />
          <div class="seo-animal-meta">
            <h3>{esc(it.get('emoji',''))} {esc(it['name'])}</h3>
            <p>{esc(item_blurb)}</p>
          </div>"""
        if card_inner:
            # At-home card session. Hunt drawer stays on the print button.
            href = (
                f"/field-pack/cards/{esc(item_id)}/"
                if item_id
                else f"/field-pack/{esc(v['id'])}/#at-home"
            )
            cards.append(
                f"""<a class="seo-animal-card" href="{href}" role="listitem">
          {card_inner}
        </a>"""
            )
        feat_html_parts.append(
            f"<li><strong>{esc(it.get('emoji',''))} {esc(it['name'])}</strong> — {esc(item_blurb)}</li>"
        )

    hunt_lis = "".join(
        f'<li><span class="seo-hunt-box" aria-hidden="true">☐</span><span>{esc(t)}</span></li>'
        for t in hunt[:8]
    ) or '<li><span class="seo-hunt-box" aria-hidden="true">☐</span><span>Find your favorite stop and check it off</span></li>'
    cards_html = (
        f'<div class="seo-animal-grid" role="list">{"".join(cards)}</div>'
        if cards
        else ""
    )

    showing_rest = bool(
        exclude_ids and featured is not featured_all and len(featured_all) > len(featured)
    )
    shortlist_lead = (
        "More stops if you have the energy."
        if showing_rest
        else SHORTLIST_LEAD
    )
    return f"""
    <section class="seo-list-block seo-visual-shortlist" aria-labelledby="shortlist-heading">
      <h2 id="shortlist-heading">{"More if you have energy" if showing_rest else "Kid shortlist"}</h2>
      <p>{shortlist_lead}</p>
      {cards_html}
      <ul class="seo-shortlist seo-shortlist-sr">
        {"".join(feat_html_parts) or "<li>Open the interactive outing for the full shortlist.</li>"}
      </ul>
    </section>
    <section class="seo-list-block seo-hunt-block" aria-labelledby="hunt-heading">
      <h2 id="hunt-heading">Optional hunt for the visit</h2>
      <p>{HUNT_BLOCK_P}</p>
      <details class="seo-hunt-examples">
        <summary>Example finds</summary>
        <ol class="seo-hunt-list">
          {hunt_lis}
        </ol>
      </details>
    </section>
"""


def h1_for(v: dict) -> str:
    """Visible page heading — venue name only. SEO phrase lives in title/meta."""
    return v["name"]


def seo_hunt_label(v: dict) -> str:
    """Search/social title phrase (not the on-page H1). Dual-mode — not print-only."""
    return f"{v['name']} for Kids — Explore at Home or Print a Hunt"


def title_for(v: dict) -> str:
    return f"{seo_hunt_label(v)} · 1Less"


def meta_for(v: dict) -> str:
    city = v["city"] or v["location"] or ""
    place, things, _ = type_bits(v)
    # Keep well under ~155 chars so SERP/OG don't truncate mid-word
    name = v["name"]
    loc = f" in {city}" if city else ""
    base = (
        f"{name}{loc}: animal cards, talk prompts, photos, and live cams at home. "
        "Optional printable hunt — Field Trip Kit."
    )
    if len(base) > 155:
        base = f"{name}{loc}: explore cards at home, or print a hunt — Field Trip Kit."
    return base[:155].rsplit(" ", 1)[0] if len(base) > 155 else base


def venue_json_ld(v: dict, url: str) -> str:
    steps = []
    for i, t in enumerate((v.get("hunt") or [])[:8], 1):
        steps.append(
            {
                "@type": "HowToStep",
                "position": i,
                "text": t,
            }
        )
    if not steps:
        steps = [{"@type": "HowToStep", "position": 1, "text": f"Explore {v['name']} with kids using the shortlist."}]

    hunt_name = seo_hunt_label(v)
    howto = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": hunt_name,
        "description": meta_for(v),
        "totalTime": "PT2H",
        "tool": [
            {"@type": "HowToTool", "name": "Phone or laptop (cards, photos, cams)"},
            {"@type": "HowToTool", "name": "Optional printed one-page hunt sheet"},
        ],
        "step": steps,
        "url": url,
    }
    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": hunt_name,
        "description": meta_for(v),
        "author": {"@type": "Organization", "name": "1Less"},
        "publisher": {"@type": "Organization", "name": "1Less", "url": SITE},
        "mainEntityOfPage": url,
        "about": {"@type": "Place", "name": v["name"], "address": v.get("location") or ""},
    }
    return json.dumps(howto, ensure_ascii=False) + "\n" + json.dumps(article, ensure_ascii=False)



def load_mission_venue(slug: str) -> dict | None:
    p = VENUE_DATA_DIR / f"{slug}.json"
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def default_mission_via_node(venue: dict) -> dict:
    """Run mission-engine.js in Node for SEO default list (age 4-5, half day)."""
    script = r"""
const fs = require('fs');
const vm = require('vm');
const ctx = { console, globalThis: {} };
vm.createContext(ctx);
const engine = fs.readFileSync(process.argv[1], 'utf8');
vm.runInContext(engine + '\nthis.FPMission = globalThis.FPMission;', ctx);
const venue = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const challenges = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const wonders = JSON.parse(fs.readFileSync(process.argv[4], 'utf8'));
const FP = ctx.FPMission || ctx.globalThis.FPMission;
const mission = FP.selectMission(venue, challenges, { age: '4-5', time: 'half', name: '', seed: 1 }, wonders);
process.stdout.write(JSON.stringify(mission));
"""
    proc = subprocess.run(
        [
            "node",
            "-e",
            script,
            str(MISSION_ENGINE),
            str(VENUE_DATA_DIR / f"{venue['slug']}.json"),
            str(CHALLENGES_JSON),
            str(WONDERS_JSON),
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


def content_mode_of(mission_venue: dict, catalog_v: dict | None = None) -> str:
    """SEO body mode. Template / unaudited lists never show a fake species grid."""
    conf = (mission_venue or {}).get("list_confidence") or ""
    if conf == "template":
        return "wonder"
    m = (mission_venue or {}).get("content_mode") or ""
    if m in ("wonder", "hybrid", "curated"):
        # Hybrid without print-safe named items → wonder page body
        if m == "hybrid" and not _print_safe_items(mission_venue):
            return "wonder"
        return m
    by = (mission_venue or {}).get("verified_by") or ""
    if by == "catalog-scaffold" or conf == "template":
        return "wonder"
    if by == "owner" or conf == "audited":
        return "curated"
    # "research" alone is not a collection census
    q = (catalog_v or {}).get("quality") or ""
    return "wonder" if conf == "template" else ("curated" if q == "full" and conf == "partial" else "wonder")


def _do_not_list_keys(mission_venue: dict) -> set[str]:
    keys: set[str] = set()
    for row in (mission_venue or {}).get("do_not_list") or []:
        if isinstance(row, str):
            keys.add(row.lower())
            continue
        if not isinstance(row, dict):
            continue
        for k in ("catalog_id", "name", "id"):
            if row.get(k):
                keys.add(str(row[k]).lower())
    return keys


def _item_presence_ok(it: dict, mission_venue: dict) -> bool:
    """Mirror mission-engine itemPresenceOk for SEO shortlist / start-here."""
    if not it:
        return False
    fid = str(it.get("id") or "")
    if fid.startswith("w_") or str(it.get("zone") or "").lower() == "wonder":
        return True
    p = str(it.get("presence") or "").lower()
    if p == "absent":
        return False
    label = str(it.get("display_label") or it.get("label") or it.get("name") or "").lower()
    cid = str(it.get("catalog_id") or "").lower()
    for row in (mission_venue or {}).get("do_not_list") or []:
        if isinstance(row, str):
            ban_name, ban_cat = row.lower(), ""
        elif isinstance(row, dict):
            ban_name = str(row.get("name") or "").lower()
            ban_cat = str(row.get("catalog_id") or "").lower()
        else:
            continue
        if ban_name and len(ban_name) >= 4 and ban_name in label:
            return False
        if ban_cat and cid == ban_cat:
            if p in ("verified", "high") and ban_name and ban_name not in label:
                pass  # soft label + verified photo reuse
            elif p not in ("verified", "high"):
                return False
            elif not ban_name:
                return False
    if p in ("template", "medium"):
        return False
    if p in ("verified", "high"):
        return True
    conf = (mission_venue or {}).get("list_confidence") or ""
    if conf == "audited":
        return True
    if conf == "template":
        return False
    if conf == "partial":
        return True
    return False


def _print_safe_items(mission_venue: dict) -> list[dict]:
    return [it for it in (mission_venue or {}).get("items") or [] if _item_presence_ok(it, mission_venue)]


def _item_sheet_label(it: dict) -> str:
    return (it.get("display_label") or it.get("label") or it.get("name") or "").strip()


def _featured_from_mission(mission_venue: dict, catalog_v: dict | None = None) -> list[dict]:
    """Build SEO photo shortlist from print-safe mission items only."""
    feat_by_id = {
        f.get("id"): f for f in (catalog_v or {}).get("featured") or [] if f.get("id")
    }
    # Also index global catalog via mission catalog_id when available on catalog_v featured only
    out: list[dict] = []
    for it in _print_safe_items(mission_venue):
        cid = (it.get("catalog_id") or "").strip()
        iid = (it.get("id") or "").replace("_", "-")
        feat = feat_by_id.get(cid) or feat_by_id.get(iid) or {}
        name = _item_sheet_label(it) or feat.get("name") or "Stop"
        out.append(
            enrich_item(
                {
                    "id": cid or iid,
                    "name": name,
                    "emoji": it.get("emoji") or feat.get("emoji") or "",
                    "blurb": it.get("one_liner") or feat.get("blurb") or "",
                    "photo": feat.get("photo") or it.get("photo") or "",
                    "key": feat.get("key") or {},
                    "links": feat.get("links") or {},
                    "packTemplate": feat.get("packTemplate") or "",
                    "qa_card": it.get("qa_card") or {},
                }
            )
        )
    return out


def map_card_html(mission_venue: dict) -> str:
    """Official map card — thumbnail + hover/focus enlarge when image URL known."""
    media = (mission_venue or {}).get("media") or {}
    page = (media.get("visitor_map_page") or mission_venue.get("official_url") or "").strip()
    img = (media.get("visitor_map_url") or "").strip()
    kind = (media.get("visitor_map_kind") or "page").strip()
    attr = (media.get("map_attribution") or "Official visitor map").strip()
    if not page and not img:
        return ""
    href = page or img
    def _safe_map_img(u: str) -> bool:
        u = (u or "").strip()
        if u.startswith("https://") or u.startswith("http://"):
            return True
        # Self-hosted previews (e.g. PDF→PNG) under /field-pack/media/maps/
        if u.startswith("/field-pack/media/maps/") and ".." not in u:
            return True
        return False

    has_img = _safe_map_img(img)
    is_pdf = ".pdf" in href.lower() or href.lower().endswith("/pdf")
    vt = str((mission_venue or {}).get("type") or "").lower()
    if "aquarium" in vt:
        map_kicker = "Aquarium map"
    elif "museum" in vt:
        map_kicker = "Museum map"
    elif "zoo" in vt:
        map_kicker = "Zoo map"
    elif "park" in vt:
        map_kicker = "Park map"
    else:
        map_kicker = "Visitor map"
    # Prefer image mode whenever we have a verified map image (kind may lag)
    if has_img and kind in ("image", "page", ""):
        # Local previews don't need no-referrer; remote maps keep it for fewer hotlink blocks
        refpol = "" if img.startswith("/") else ' referrerpolicy="no-referrer"'
        ext_label = "Open PDF on official site ↗" if is_pdf else "Open on official site ↗"
        # Click pins enlarge in-page; external leave is a small secondary link only
        return f"""
    <div class="seo-map-card seo-map-card-image seo-map-has-preview no-print" data-map-preview>
      <button type="button" class="seo-map-enlarge-hit" aria-expanded="false" aria-controls="seo-map-preview-panel" aria-label="Enlarge visitor map">
        <span class="seo-map-thumb-wrap">
          <img class="seo-map-thumb" src="{esc(img)}" alt="Visitor map preview" width="640" height="400" loading="lazy" decoding="async"{refpol} />
          <span class="seo-map-hover-hint" aria-hidden="true">Tap to enlarge</span>
        </span>
      </button>
      <div class="seo-map-card-body">
        <span class="seo-map-kicker">{esc(map_kicker)}</span>
        <strong>Visitor map</strong>
        <small>{esc(attr)} · tap to enlarge</small>
        <a class="seo-map-ext-link" href="{esc(href)}" target="_blank" rel="noopener noreferrer">{esc(ext_label)}</a>
      </div>
      <div class="seo-map-preview" id="seo-map-preview-panel" role="dialog" aria-label="Enlarged visitor map" hidden>
        <button type="button" class="seo-map-preview-close" aria-label="Close enlarged map">×</button>
        <img src="{esc(img)}" alt="Enlarged visitor map" loading="lazy" decoding="async"{refpol} />
        <span class="seo-map-preview-cap">
          {esc(attr)}
          · <a class="seo-map-preview-ext" href="{esc(href)}" target="_blank" rel="noopener noreferrer">{esc(ext_label)}</a>
        </span>
      </div>
    </div>"""
    tab_note = "PDF · opens in a new tab" if is_pdf else "opens in a new tab"
    cta = "Open the print map (PDF)" if is_pdf else "Open the official map page"
    return f"""
    <a class="seo-map-card no-print" href="{esc(href)}" target="_blank" rel="noopener noreferrer">
      <span class="seo-map-icon" aria-hidden="true">🗺️</span>
      <span class="seo-map-card-body">
        <span class="seo-map-kicker">Official map</span>
        <strong>{cta}</strong>
        <small>{esc(attr)} · {tab_note}</small>
      </span>
      <span class="seo-map-go" aria-hidden="true">→</span>
    </a>"""

def is_wonder_find(find: dict) -> bool:
    """True flexible backups (taller than you, three colors) — not real animals/exhibits.

    Animals carry catalog_id and belong in photo shortlist / Q&A, not emoji stubs.
    """
    if not find:
        return False
    if find.get("catalog_id"):
        return False
    fid = str(find.get("id") or "")
    if fid.startswith("w_"):
        return True
    # Wonder-pool items never use catalog_id; zone sometimes tagged Wonder
    zone = str(find.get("zone") or "").lower()
    if zone == "wonder":
        return True
    # Abstract backup: no catalog link and not a venue item id pattern
    return not fid or fid.startswith("w")


def wonder_grid_html(mission: dict) -> str:
    """Emoji tiles for flexible backups only — animals stay out of this block."""
    finds = [f for f in (mission.get("finds") or []) if is_wonder_find(f)][:8]
    if not finds:
        return ""
    tiles = "".join(
        f"""<li class="seo-wonder-tile">
        <span class="seo-wonder-emoji" aria-hidden="true">{esc(f.get("emoji") or "✨")}</span>
        <strong>{esc(f.get("label") or "Wonder")}</strong>
        <small>{esc(_card_blurb(f.get("one_liner") or "") or f.get("one_liner") or "")}</small>
      </li>"""
        for f in finds
    )
    return f"""
    <section class="seo-wonder-block" aria-labelledby="wonder-heading">
      <h2 id="wonder-heading">Also look for</h2>
      <p class="seo-wonder-lead">Flexible backups if a favorite is closed, crowded, or napping — no fixed path.</p>
      <ul class="seo-wonder-grid">{tiles}</ul>
    </section>"""


def page_mission_chrome_html() -> str:
    """Dual CTA: at-home session first, print hunt secondary. Chips still drive the drawer."""
    return f"""
        <div class="seo-mission-bar no-print" aria-label="{esc(CTA_EXPLORE_HOME)} or {esc(CTA_PRINT_VISIT)}">
          <a class="btn btn-primary seo-home-btn" href="#at-home">{esc(CTA_EXPLORE_HOME)}</a>
          <button type="button" class="btn btn-secondary seo-print-btn" id="mission-open-btn" aria-haspopup="dialog" aria-controls="mission-drawer" aria-label="{esc(CTA_PRINT_VISIT)}">
            <span class="seo-print-btn-long">
              <span class="seo-print-btn-line">{esc(CTA_PRINT_VISIT)}</span>
            </span>
            <span class="seo-print-btn-short">{esc(CTA_PRINT_VISIT_SHORT)}</span>
          </button>
          <div class="seo-mission-chrome" id="seo-mission-chrome">
            <div class="seo-chrome-row">
              <span class="seo-chrome-k" id="seo-who-label">Who</span>
              <div class="seo-chip-row" role="group" aria-labelledby="seo-who-label">
                <button type="button" class="seo-age-chip" data-age="2-3">2–4</button>
                <button type="button" class="seo-age-chip is-active" data-age="4-5" aria-pressed="true">5–8</button>
                <button type="button" class="seo-age-chip" data-age="6-8">9–12</button>
                <button type="button" class="seo-age-chip" data-age="adult">Adults</button>
              </div>
            </div>
            <div class="seo-chrome-row">
              <span class="seo-chrome-k" id="seo-time-label">Time</span>
              <div class="seo-chip-row" role="group" aria-labelledby="seo-time-label">
                <button type="button" class="seo-time-chip" data-time="90m">90 min</button>
                <button type="button" class="seo-time-chip is-active" data-time="half" aria-pressed="true">Half day</button>
                <button type="button" class="seo-time-chip" data-time="full">Full day</button>
              </div>
            </div>
            <div class="seo-chrome-row seo-chrome-row-hunt">
              <span class="seo-chrome-k" id="seo-hunt-label">Style</span>
              <div class="seo-chip-row seo-chip-row-hunt" role="group" aria-labelledby="seo-hunt-label">
                <button type="button" class="seo-hunt-chip is-active" data-hunt="classic" aria-pressed="true">Classic</button>
                <button type="button" class="seo-hunt-chip seo-hunt-bonus" data-hunt="bonus">Bonus</button>
                <button type="button" class="seo-hunt-chip seo-hunt-alpha" data-hunt="alpha">Alpha</button>
              </div>
            </div>
          </div>
        </div>
        <p class="seo-print-fallback no-print">{esc(PRINT_FALLBACK)} <span class="seo-bonus-hint">Classic · Bonus · Alpha (extra-hard cool finds).</span></p>"""


def _photo_src(photo: str) -> str:
    photo = (photo or "").strip()
    if not photo:
        return ""
    if photo.startswith("/field-pack/"):
        return photo[len("/field-pack/") :]
    return photo


def _route_90m_picks(mission_venue: dict, mission: dict) -> list[dict]:
    """Same pick order as the start-here section (print-safe route_90m, else mission finds)."""
    safe = _print_safe_items(mission_venue)
    items = {it.get("id"): it for it in safe}
    picks: list[dict] = []
    for rid in (mission_venue.get("route_90m") or [])[:3]:
        if rid in items:
            picks.append(items[rid])
    if len(picks) < 3:
        for f in mission.get("finds") or []:
            if len(picks) >= 3:
                break
            if not any(p.get("id") == f.get("id") for p in picks):
                picks.append(f)
    return picks[:3]


def _start_here_catalog_ids(mission_venue: dict, mission: dict) -> set[str]:
    out: set[str] = set()
    for p in _route_90m_picks(mission_venue, mission):
        cid = (p.get("catalog_id") or "").strip()
        if cid:
            out.add(cid)
        elif p.get("id"):
            out.add(str(p["id"]).replace("_", "-"))
    return out


def _card_blurb(text: str) -> str:
    """Use a one-liner only if it reads as a full clue, not a 2–3 word stub."""
    t = (text or "").strip()
    if not t:
        return ""
    # Cryptic stubs create more questions than they answer
    if len(t.split()) < 5 and len(t) < 28:
        return ""
    return t


def route_90m_html(mission_venue: dict, mission: dict, catalog_v: dict | None = None) -> str:
    """Short-visit picks: 2–3 real stops with photos — the “start here” path.

    Exists so a half-day page still answers “we only have an hour.”
    Not a second shortlist: same finds, tighter cut, numbered.
    No separate “First stop” tip — the numbered cards are the plan.
    """
    # catalog featured: id (sci-dinosaur) → photo/blurb
    feat_by_id = {f.get("id"): f for f in (catalog_v or {}).get("featured") or [] if f.get("id")}
    picks = _route_90m_picks(mission_venue, mission)
    if len(picks) < 2:
        return ""

    slug = mission_venue.get("slug") or ""
    n = min(3, len(picks))
    cards = []
    for i, p in enumerate(picks[:3], 1):
        cat_id = (p.get("catalog_id") or "").replace("_", "-") or (p.get("id") or "").replace("_", "-")
        feat = feat_by_id.get(cat_id) or feat_by_id.get(p.get("id") or "") or {}
        # also try matching featured by name-ish catalog ids already hyphenated
        if not feat and p.get("catalog_id"):
            feat = feat_by_id.get(p["catalog_id"]) or {}
        src = _photo_src(feat.get("photo") or p.get("photo") or "")
        if not src:
            for cand in (cat_id, p.get("catalog_id"), p.get("id")):
                cid = str(cand or "").replace("_", "-").strip()
                if cid and (FIELD / "photos" / f"{cid}.jpg").is_file():
                    src = f"photos/{cid}.jpg?v=img2"
                    break
        label = _item_sheet_label(p) or feat.get("name") or "Stop"
        emoji = p.get("emoji") or feat.get("emoji") or ""
        one = _card_blurb(p.get("one_liner") or feat.get("blurb") or "")
        # Prefer catalog id for public card pages; underscore venue ids won't resolve in catalog
        item_id = (p.get("catalog_id") or "").strip() or cat_id
        href = f"/field-pack/cards/{esc(item_id)}/" if item_id else (
            f"/field-pack/{esc(slug)}/#at-home" if slug else "/field-pack/"
        )
        if src:
            media = (
                f'<img src="{esc(src)}" alt="" width="640" height="400" '
                f'loading="{"eager" if i == 1 else "lazy"}" decoding="async" />'
            )
        else:
            media = f'<span class="seo-start-emoji" aria-hidden="true">{esc(emoji or "✨")}</span>'
        cards.append(
            f"""<article class="seo-start-card">
        <a class="seo-start-card-main" href="{href}">
          <span class="seo-start-num" aria-hidden="true">{i}</span>
          {media}
          <span class="seo-start-meta">
            <strong>{esc(emoji + " " if emoji else "")}{esc(label)}</strong>
            {f"<small>{esc(one)}</small>" if one else ""}
          </span>
        </a>
        <p class="seo-start-actions">
          <a class="seo-start-talk" href="{href}">{esc(CTA_TALK_HOME)}</a>
          <button type="button" class="seo-start-hunt" data-how="print-hunt">{esc(CTA_ADD_HUNT)}</button>
        </p>
      </article>"""
        )

    lead = START_HERE_LEAD
    return f"""
    <section class="seo-start-here no-print" aria-labelledby="route90-heading">
      <h2 id="route90-heading">{esc(START_HERE_H2)}</h2>
      <p class="seo-start-lead">{esc(lead)}</p>
      <div class="seo-start-grid">{"".join(cards)}</div>
    </section>"""


def mission_drawer_html(mission_venue: dict, mission: dict) -> str:
    """Slide-over drawer: filters + live sheet. Page stays clean; CTA opens this."""
    vid = mission_venue["slug"]
    loc = ", ".join(x for x in [mission_venue.get("city"), mission_venue.get("region")] if x)
    verified_line = print_status_line(mission_venue)
    mission_title = esc(mission.get("title") or f"Your Mission at {mission_venue['name']}")
    age_label = esc(mission.get("ageLabel") or "Kids · 5–8")
    time_label = esc(mission.get("timeLabel") or "Half day")
    finds_html = "".join(
        f'<li class="mission-find">'
        f'<span class="mission-check" aria-hidden="true">☐</span>'
        f'<span class="mission-emoji">{esc(f.get("emoji") or "📍")}</span>'
        f'<span class="mission-find-body"><strong>{esc(f["label"])}</strong>'
        f'<small>{esc(f.get("one_liner") or "")}'
        f'{(" · " + esc(f["zone"])) if f.get("zone") else ""}</small></span></li>'
        for f in mission.get("finds") or []
    )
    ch_html = "".join(
        f'<li class="mission-challenge">'
        f'<span class="mission-check" aria-hidden="true">☐</span>'
        f"<span>{esc(c.get('text') or '')}</span></li>"
        for c in mission.get("challenges") or []
    )
    return f"""
  <div class="mission-overlay no-print" id="mission-overlay" hidden>
    <div
      class="mission-drawer"
      id="mission-drawer"
      role="dialog"
      aria-modal="true"
      aria-labelledby="mission-heading"
      tabindex="-1"
    >
      <header class="mission-drawer-head">
        <div>
          <p class="mission-drawer-kicker"><a class="mission-home" href="/field-pack/">Field Trip Kit</a> · <span class="mission-place-now">{esc(mission_venue.get("short_name") or mission_venue.get("name") or "This place")}</span> · <a class="mission-change-place" href="/field-pack/?find=1">Different place?</a></p>
          <h2 id="mission-heading">Create and print your mission</h2>
        </div>
        <button type="button" class="mission-drawer-close" id="mission-close" aria-label="Close">×</button>
      </header>
      <div class="mission-drawer-body">
        <aside class="mission-filters" id="mission-controls" aria-label="Personalize">
          <div class="mission-field mission-field-name">
            <label for="mission-name">Kid name <span class="mission-opt">(optional)</span></label>
            <input type="text" id="mission-name" maxlength="24" placeholder="e.g. Arya" autocomplete="off" />
            <p class="mission-privacy">Stays on this page — never sent anywhere.</p>
          </div>
          <div class="mission-field mission-field-who">
            <span class="mission-field-label" id="mission-who-label">Who’s going?</span>
            <div class="mission-seg" id="mission-who-seg" role="group" aria-labelledby="mission-who-label">
              <button type="button" class="mission-seg-btn" data-age="2-3">2–4</button>
              <button type="button" class="mission-seg-btn is-active" data-age="4-5" aria-pressed="true">5–8</button>
              <button type="button" class="mission-seg-btn" data-age="6-8">9–12</button>
              <button type="button" class="mission-seg-btn" data-age="adult">Adults</button>
            </div>
          </div>
          <div class="mission-field mission-field-time">
            <span class="mission-field-label" id="mission-time-label">How long?</span>
            <div class="mission-seg" id="mission-time-seg" role="group" aria-labelledby="mission-time-label">
              <button type="button" class="mission-seg-btn" data-time="90m">90 min</button>
              <button type="button" class="mission-seg-btn is-active" data-time="half" aria-pressed="true">Half day</button>
              <button type="button" class="mission-seg-btn" data-time="full">Full day</button>
            </div>
          </div>
          <div class="mission-field mission-field-hunt">
            <span class="mission-field-label" id="mission-hunt-label">Mission style</span>
            <div class="mission-seg" id="mission-hunt-seg" role="group" aria-labelledby="mission-hunt-label">
              <button type="button" class="mission-seg-btn is-active" data-hunt="classic" aria-pressed="true">Classic</button>
              <button type="button" class="mission-seg-btn mission-seg-bonus" data-hunt="bonus">Bonus</button>
              <button type="button" class="mission-seg-btn mission-seg-alpha" data-hunt="alpha">Alpha</button>
            </div>
            <p class="mission-hunt-hint">Classic = first visit · Bonus = trickier · Alpha = extra-hard cool finds</p>
          </div>
          <div class="mission-field">
            <label for="mission-interest">What are they into? <span class="mission-opt">(optional)</span></label>
            <select id="mission-interest">
              <option value="">Any</option>
            </select>
          </div>
          <p class="mission-filters-hint">Sheet updates live — then print one page.</p>
        </aside>
        <div class="mission-preview">
          <div class="mission-sheet" id="mission-sheet">
            <p class="ms-brand">Field Trip Kit{f' · {esc(loc)}' if loc else ""}</p>
            <h3 class="ms-title" id="mission-title">{mission_title}</h3>
            <p class="ms-meta" id="mission-meta">{age_label} · {time_label}</p>
            <h4 class="ms-section" id="mission-finds-heading">Find these</h4>
            <ol class="mission-finds" id="mission-finds" aria-label="Finds">{finds_html}</ol>
            <h4 class="ms-section" id="mission-bonus-heading">Bonus</h4>
            <ul class="mission-challenges" id="mission-challenges" aria-label="Challenges">{ch_html}</ul>
            <p class="ms-favorite">My favorite was _______________________</p>
            <p class="ms-footer">
              <span id="mission-verified">{esc(verified_line)}</span>
              · free at 1less.app/field-pack/{esc(vid)}/
            </p>
            <p class="ms-map-hint" id="mission-map-hint"></p>
          </div>
        </div>
      </div>
      <footer class="mission-drawer-foot">
        <button type="button" class="btn btn-ghost" id="mission-shuffle-btn">Give me different stops</button>
        <button type="button" class="btn btn-primary btn-big" id="mission-print-btn">Create and print your mission</button>
      </footer>
    </div>
  </div>
"""


def hero_illustration_path(mission_venue: dict | None, venue_id: str = "") -> str:
    """Relative path under /field-pack/ for park (or any) hero art, or empty."""
    media = (mission_venue or {}).get("media") or {}
    raw = (media.get("hero_illustration") or "").strip()
    if not raw and venue_id:
        candidate = FIELD / "photos" / f"np-hero-{venue_id}.jpg"
        if candidate.is_file():
            raw = f"/field-pack/photos/np-hero-{venue_id}.jpg"
    if not raw:
        return ""
    if raw.startswith("http"):
        return raw
    if raw.startswith("/field-pack/"):
        return raw
    if raw.startswith("/"):
        return raw
    return f"/field-pack/{raw.lstrip('/')}"


def hero_img_src(mission_venue: dict | None, venue_id: str = "", bust: str = "q2") -> str:
    """Browser-relative src (base href=/field-pack/) for hero image."""
    path = hero_illustration_path(mission_venue, venue_id)
    if not path:
        return ""
    # Strip /field-pack/ for base-relative URLs used on SEO pages
    if path.startswith("/field-pack/"):
        rel = path[len("/field-pack/") :]
    elif path.startswith("http"):
        return f"{path}?v={bust}" if "?" not in path else path
    else:
        rel = path.lstrip("/")
    return f"{rel}?v={bust}"


def render_mission_venue_page(v: dict, mission_venue: dict) -> str:
    """Full SEO venue page (photos + shortlist); mission opens in a drawer."""
    vid = v["id"]
    if vid in RESERVED:
        raise SystemExit(f"Venue id collides with reserved path: {vid}")
    url = f"{SITE}/field-pack/{vid}/"
    app_href = f"/field-pack/app.html#/venue/{vid}"
    map_href = f"/field-pack/#/venue/{vid}"
    place, _, _ = type_bits(v)

    def soft_title(s: str) -> str:
        parts = []
        for w in (s or "").replace("_", " ").split():
            if not w:
                continue
            if "'" in w:
                a, b = w.split("'", 1)
                parts.append(
                    (a[:1].upper() + a[1:].lower())
                    + "'"
                    + (b[:1].upper() + b[1:].lower() if b else "")
                )
            else:
                parts.append(w[:1].upper() + w[1:].lower() if len(w) > 1 else w.upper())
        return " ".join(parts)

    loc_chip = " · ".join(
        x for x in [soft_title(place.replace("_", " ")), v.get("location") or ""] if x
    )
    mode = content_mode_of(mission_venue, v)
    last_v = (v.get("lastVerified") or mission_venue.get("last_verified") or "")[:7]

    mission = default_mission_via_node(mission_venue)
    drawer = mission_drawer_html(mission_venue, mission)
    map_card = map_card_html(mission_venue)
    chrome = page_mission_chrome_html()
    route90 = route_90m_html(mission_venue, mission, catalog_v=v)
    # Catalog ids already shown in “start here” — don’t repeat in shortlist grid
    start_exclude = _start_here_catalog_ids(mission_venue, mission)
    practical = mission_venue.get("practical") or {}
    # Prefer print-safe mission items over catalog.js animal pack (stops false elephants)
    v_body = dict(v)
    safe_feat = _featured_from_mission(mission_venue, catalog_v=v)
    if safe_feat:
        v_body["featured"] = safe_feat
    elif (mission_venue or {}).get("list_confidence") == "template":
        v_body["featured"] = []  # never show template catalog pack
    home_items = [enrich_item(it) for it in (v_body.get("featured") or v.get("featured") or [])]
    home_sec = home_session_html(home_items, venue_kind=str(v.get("type") or ""))
    if mode == "wonder":
        hunt = v.get("hunt") or []
        hunt_lis = "".join(
            f'<li><span class="seo-hunt-box" aria-hidden="true">☐</span><span>{esc(t)}</span></li>'
            for t in hunt[:8]
        )
        hunt_sec = (
            f"""
    <section class="seo-list-block seo-hunt-block" aria-labelledby="hunt-heading">
      <h2 id="hunt-heading">Optional hunt for the visit</h2>
      <p>{HUNT_BLOCK_P}</p>
      <details class="seo-hunt-examples">
        <summary>Example finds</summary>
        <ol class="seo-hunt-list">{hunt_lis}</ol>
      </details>
    </section>"""
            if hunt_lis
            else ""
        )
        body = wonder_grid_html(mission) + hunt_sec
    elif mode == "hybrid":
        wonder_sec = wonder_grid_html(mission)
        body = unique_body(v_body, exclude_ids=start_exclude) + wonder_sec
    else:
        body = unique_body(v_body, exclude_ids=start_exclude)
    h1 = h1_for(v)
    title = title_for(v)
    desc = meta_for(v)
    hero_abs = hero_illustration_path(mission_venue, vid)
    hero_src = hero_img_src(mission_venue, vid, bust="q2")
    if hero_abs.startswith("http"):
        og_img = hero_abs.split("?")[0]
    elif hero_abs.startswith("/"):
        og_img = f"{SITE}{hero_abs.split('?')[0]}"
    else:
        og_img = OG_SHARE_IMAGE
    hero_banner = ""
    if hero_src:
        hero_banner = (
            f'<div class="seo-park-hero no-print">'
            f'<img src="{esc(hero_src)}" alt="{esc(v.get("name") or vid)} park day" '
            f'width="1280" height="720" loading="eager" decoding="async" />'
            f"</div>"
        )
    json_ld = venue_json_ld(v, url)
    venue_json = json.dumps(mission_venue, ensure_ascii=False)
    challenges_json = CHALLENGES_JSON.read_text(encoding="utf-8")
    wonders_json = WONDERS_JSON.read_text(encoding="utf-8") if WONDERS_JSON.is_file() else "{}"
    # Per-venue bonus slice only — full catalog is huge; engine also reads venue.bonus_hunt.
    bonus_json = "{}"
    if BONUS_HUNTS_JSON.is_file():
        try:
            _bh_all = json.loads(BONUS_HUNTS_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            _bh_all = {}
        _slug = mission_venue.get("slug") or v.get("id") or ""
        _bh_slim = {
            "version": _bh_all.get("version", 1),
            "generic": _bh_all.get("generic") or {},
        }
        if _bh_all.get("kits"):
            _bh_slim["kits"] = _bh_all["kits"]
        _one = (_bh_all.get("venues") or {}).get(_slug)
        if not _one and isinstance(mission_venue.get("bonus_hunt"), dict):
            _one = mission_venue["bonus_hunt"]
        if _one:
            _bh_slim["venues"] = {_slug: _one}
        else:
            _bh_slim["venues"] = {}
        # Alpha slice (extra-hard mode)
        _alpha_all = _bh_all.get("alpha") or {}
        _alpha_one = (_alpha_all.get("venues") or {}).get(_slug)
        if not _alpha_one and isinstance(mission_venue.get("alpha_hunt"), dict):
            _alpha_one = mission_venue["alpha_hunt"]
        _alpha_slim = {
            "generic": _alpha_all.get("generic") or {},
            "venues": {_slug: _alpha_one} if _alpha_one else {},
        }
        _bh_slim["alpha"] = _alpha_slim
        bonus_json = json.dumps(_bh_slim, ensure_ascii=False)
    lead = (
        mission_venue.get("tagline")
        or v.get("blurb")
        or f"Explore {v['name']} at home with cards, photos, and talk prompts — or print a hunt for the visit."
    )
    facts_html = practical_chips_html(practical, last_v) + status_chip_html(mission_venue)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}" />
  <link rel="canonical" href="{esc(url)}" />
  <meta name="robots" content="index,follow" />
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="1Less" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(desc)}" />
  <meta property="og:url" content="{esc(url)}" />
  <meta property="og:image" content="{esc(og_img)}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{esc(title)}" />
  <meta name="twitter:description" content="{esc(desc)}" />
  <meta name="twitter:image" content="{esc(og_img)}" />
  <meta name="color-scheme" content="light" />
  <base href="/field-pack/" />
  <link rel="stylesheet" href="/shell/shell.css?v=6" />
  <link rel="stylesheet" href="/field-pack/css/styles.css?v={STYLES_CSS_VER}" />
  <link rel="stylesheet" href="/field-pack/css/landing.css?v={LANDING_CSS_VER}" />
  <link rel="stylesheet" href="/field-pack/css/seo-venue.css?v={SEO_CSS_VER}" />
  <link rel="stylesheet" href="/field-pack/css/mission.css?v=16" />
  <script type="application/ld+json">
{json_ld.split(chr(10))[0]}
  </script>
  <script type="application/ld+json">
{json_ld.split(chr(10))[1]}
  </script>
</head>
<body class="landing-body seo-venue-body mission-venue-body" data-content-mode="{esc(mode)}">
  <div class="app landing-app seo-venue">
    <header class="oneless-shell no-print" data-product="bdo">
      <a class="shell-brand" href="/field-pack/" aria-label="Field Trip Kit home">
        <img src="/1LessMark.png" alt="" width="52" height="52" />
      </a>
      <a class="shell-product" href="/field-pack/">
        Field Trip Kit
        <small>{HEADER_TAGLINE}</small>
      </a>
{nav_more_menu_html()}
    </header>

    <nav class="seo-crumbs no-print" aria-label="Breadcrumb">
      <a href="/field-pack/">All places</a>
      <span aria-hidden="true"> / </span>
      <span>{esc(v['shortName'])}</span>
      <span class="seo-crumb-extra"> · <a href="{esc(map_href)}">Map</a></span>
    </nav>

    <article class="seo-article">
      <header class="seo-hero">
        <p class="promise-pill">{esc(loc_chip)}</p>
        <h1>{esc(v.get('emoji',''))} {esc(h1)}</h1>
        <p class="lead">{esc(lead)}</p>
        {hero_banner}
        {facts_html}
        {chrome}
        <p class="seo-secondary-links no-print">
          <a href="#at-home">{esc(CTA_EXPLORE_HOME)}</a>
          <span aria-hidden="true"> · </span>
          <a href="/field-pack/virtual-field-trip/">{esc(HOME_SESSION_VFT)}</a>
          <span aria-hidden="true"> · </span>
          <a href="#at-home">{esc(CTA_ZOO_CARDS)}</a>
          <span aria-hidden="true"> · </span>
          <a href="{esc(map_href)}">Find on map</a>
        </p>
      </header>

      {home_sec}
      {map_card}
      {route90}
      <div id="seo-play-target" class="seo-play-anchor" tabindex="-1"></div>
      {body}

      <p class="seo-official no-print">
        {f'Official site: <a href="{esc(v["website"])}" rel="noopener noreferrer" target="_blank">{esc(v["name"])} website</a>.' if v.get("website") else ""}
        Always check hours and tickets before you go.
      </p>
    </article>

    <footer class="site-footer site-footer-slim no-print">
      <p>
        <strong>Field Trip Kit</strong>
        <span class="footer-dot">·</span>
        <a href="/field-pack/">All places</a>
        <span class="footer-dot">·</span>
        <a href="/field-pack/cards/">Cards</a>
        <span class="footer-dot">·</span>
        <a href="/field-pack/#about">About</a>
        <span class="footer-dot">·</span>
        <a href="mailto:hello@1less.app">Contact</a>
      </p>
      <p class="footer-privacy">Kid names stay on your device. We don’t collect accounts or emails for hunts.</p>
    </footer>
  </div>

  {drawer}

  <div id="print-sheet" class="print-sheet" aria-hidden="true"></div>
  <div id="treasure-sheet" class="print-sheet treasure-sheet" aria-hidden="true"></div>

  <script type="application/json" id="venue-data">{venue_json}</script>
  <script type="application/json" id="challenges-data">{challenges_json}</script>
  <script type="application/json" id="wonders-data">{wonders_json}</script>
  <script type="application/json" id="bonus-hunts-data">{bonus_json}</script>
  <script src="/shell/shell.js?v=5"></script>
  <script src="/field-pack/js/fp-analytics.js?v=1"></script>
  <script src="/field-pack/js/catalog.js?v=34"></script>
  <script src="/field-pack/js/print-maps.js?v=5"></script>
  <script src="/field-pack/js/print-kit.js?v=13"></script>
  <script src="/field-pack/js/mission/mission-engine.js?v=13"></script>
  <script src="/field-pack/js/mission/mission-ui.js?v=15"></script>
</body>
</html>
"""



def render_venue_page(v: dict) -> str:
    vid = v["id"]
    if vid in RESERVED:
        raise SystemExit(f"Venue id collides with reserved path: {vid}")
    url = f"{SITE}/field-pack/{vid}/"
    app_href = f"/field-pack/app.html#/venue/{vid}"
    map_href = f"/field-pack/#/venue/{vid}"
    place, things, _ = type_bits(v)
    # Apostrophe-safe title case (avoid Children'S)
    def soft_title(s: str) -> str:
        parts = []
        for w in (s or "").replace("_", " ").split():
            if not w:
                continue
            if "'" in w:
                a, b = w.split("'", 1)
                parts.append((a[:1].upper() + a[1:].lower()) + "'" + (b[:1].upper() + b[1:].lower() if b else ""))
            else:
                parts.append(w[:1].upper() + w[1:].lower() if len(w) > 1 else w.upper())
        return " ".join(parts)

    loc_chip = " · ".join(
        x for x in [soft_title(place.replace("_", " ")), v.get("location") or ""] if x
    )
    body = unique_body(v)
    home_sec = home_session_html(
        [enrich_item(it) for it in (v.get("featured") or [])],
        venue_kind=str(v.get("type") or ""),
    )
    h1 = h1_for(v)
    title = title_for(v)
    desc = meta_for(v)
    og_img = OG_SHARE_IMAGE
    json_ld = venue_json_ld(v, url)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}" />
  <link rel="canonical" href="{esc(url)}" />
  <meta name="robots" content="index,follow" />
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="1Less" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(desc)}" />
  <meta property="og:url" content="{esc(url)}" />
  <meta property="og:image" content="{esc(og_img)}" />
  <meta name="twitter:card" content="summary" />
  <meta name="twitter:title" content="{esc(title)}" />
  <meta name="twitter:description" content="{esc(desc)}" />
  <meta name="twitter:image" content="{esc(og_img)}" />
  <meta name="color-scheme" content="light" />
  <base href="/field-pack/" />
  <link rel="stylesheet" href="/shell/shell.css?v=6" />
  <link rel="stylesheet" href="/field-pack/css/styles.css?v={STYLES_CSS_VER}" />
  <link rel="stylesheet" href="/field-pack/css/landing.css?v={LANDING_CSS_VER}" />
  <link rel="stylesheet" href="/field-pack/css/seo-venue.css?v={SEO_CSS_VER}" />
  <script type="application/ld+json">
{json_ld.split(chr(10))[0]}
  </script>
  <script type="application/ld+json">
{json_ld.split(chr(10))[1]}
  </script>
</head>
<body class="landing-body seo-venue-body">
  <div class="app landing-app seo-venue">
    <header class="oneless-shell no-print" data-product="bdo">
      <a class="shell-brand" href="/field-pack/" aria-label="Field Trip Kit home">
        <img src="/1LessMark.png" alt="" width="52" height="52" />
      </a>
      <a class="shell-product" href="/field-pack/">
        Field Trip Kit
        <small>{HEADER_TAGLINE}</small>
      </a>
{nav_more_menu_html()}
    </header>

    <nav class="seo-crumbs no-print" aria-label="Breadcrumb">
      <a href="/field-pack/">All places</a>
      <span aria-hidden="true"> / </span>
      <span>{esc(v['shortName'])}</span>
    </nav>

    <article class="seo-article">
      <header class="seo-hero">
        <p class="promise-pill">{esc(loc_chip)}</p>
        <h1>{esc(v.get('emoji',''))} {esc(h1)}</h1>
        <p class="lead">{esc(v.get('blurb') or f'Explore {v["name"]} at home with cards and talk prompts — or print a hunt for the visit.')}</p>
        <p class="seo-quality-note">{esc(
          (
            "Short kid list for a half-day visit."
            + (f' Status {v["lastVerified"][:7]}.' if (v.get("lastVerified") or "")[:7] else "")
          )
          if (v.get("quality") or "starter") == "full"
          else "Short flexible list — animals and exhibits change; skip anything closed or missing."
        )}</p>
        <p class="seo-brand-note"><strong>Field Trip Kit</strong> by 1Less — free printable hunts for families.</p>
        <div class="landing-cta-row seo-cta no-print">
          <a class="btn btn-primary btn-big" href="{esc(map_href)}">Open on map →</a>
          <button type="button" class="btn btn-secondary btn-big" id="seo-print-hunt" data-venue="{esc(vid)}">
            One-page hunt to print
          </button>
          <a class="btn btn-ghost" href="{esc(app_href)}">Full interactive list →</a>
        </div>
      </header>

      {home_sec}
      <div id="seo-play-target" class="seo-play-anchor" tabindex="-1"></div>
      {body}

      <section class="seo-how no-print" aria-labelledby="how-heading">
        <h2 id="how-heading">How it works</h2>
        <p class="how-hint">Tap a step to jump there.</p>
        <ol class="how-steps how-steps-visual how-steps-linked">
          <li>
            <a class="how-step-btn" href="#at-home" data-how="home" id="how-home-link">
              <span class="how-ico" aria-hidden="true">🏠</span>
              <strong>At home</strong>
              <span>Cards, photos, talk</span>
            </a>
          </li>
          <li>
            <button type="button" class="how-step-btn" data-how="print-hunt" id="how-print-btn">
              <span class="how-ico" aria-hidden="true">🖨️</span>
              <strong>Visit</strong>
              <span>Optional one-page hunt</span>
            </button>
          </li>
          <li>
            <a class="how-step-btn" href="#at-home" data-how="talk" id="how-talk-link">
              <span class="how-ico" aria-hidden="true">💬</span>
              <strong>Cards</strong>
              <span>Talk again after</span>
            </a>
          </li>
        </ol>
      </section>

      <p class="seo-official">
        {f'Official site: <a href="{esc(v["website"])}" rel="noopener noreferrer" target="_blank">{esc(v["name"])} website</a>.' if v.get("website") else ""}
        Always check hours and tickets before you go.
      </p>
    </article>

    <footer class="site-footer site-footer-slim no-print">
      <p>
        <a href="/field-pack/">All places</a> ·
        <strong>Field Trip Kit</strong> ·
        <a href="/field-pack/#about">About</a>
      </p>
    </footer>
  </div>

  <div id="print-sheet" class="print-sheet" aria-hidden="true"></div>
  <div id="treasure-sheet" class="print-sheet treasure-sheet" aria-hidden="true"></div>

  <script src="/shell/shell.js?v=5"></script>
  <script src="/field-pack/js/fp-analytics.js?v=1"></script>
  <script src="/field-pack/js/catalog.js?v=34"></script>
  <script src="/field-pack/js/print-maps.js?v=5"></script>
  <script src="/field-pack/js/print-kit.js?v=13"></script>
  <script>
    (function () {{
      var btn = document.getElementById("seo-print-hunt");
      function printHunt() {{
        // Prefer mission drawer when present; else legacy static treasure
        if (window.FPPrint && window.FPPrint.printTreasureForVenue) {{
          var id = (btn && btn.getAttribute("data-venue")) || "";
          if (window.FPPrint.printTreasureForVenue(id)) return true;
        }}
        if (btn) {{
          location.href = "/field-pack/app.html#/venue/" + encodeURIComponent(btn.getAttribute("data-venue") || "");
        }}
        return false;
      }}
      if (btn) btn.addEventListener("click", printHunt);
      document.querySelectorAll("[data-how]").forEach(function (el) {{
        el.addEventListener("click", function (e) {{
          var how = el.getAttribute("data-how");
          if (how === "print-hunt" || how === "print") {{
            e.preventDefault();
            printHunt();
            return;
          }}
          if (how === "play") {{
            var t = document.getElementById("seo-play-target")
              || document.getElementById("shortlist-heading");
            if (t) {{
              e.preventDefault();
              t.scrollIntoView({{ behavior: "smooth", block: "start" }});
            }}
          }}
        }});
      }});
    }})();
  </script>
</body>
</html>
"""


def write_type_landing(meta: dict, venues: list[dict]) -> str:
    """Write /field-pack/<path>/index.html type hub. Returns path URL."""
    kind = meta["kind"]
    path = meta["path"]
    filtered = [v for v in venues if venue_type_kind(v) == kind]
    filtered.sort(key=lambda v: ((v.get("city") or "").lower(), (v.get("name") or "").lower()))

    # Directory by continent (same as main landing)
    buckets: dict[str, list[dict]] = {c: [] for c in _CONTINENT_ORDER}
    for v in filtered:
        cont = _venue_continent(v)
        buckets.setdefault(cont, []).append(v)
    parts = [
        _dir_continent_html(title, buckets[title])
        for title in _CONTINENT_ORDER
        if buckets.get(title)
    ]
    for title, vs in buckets.items():
        if title not in _CONTINENT_ORDER and vs:
            parts.append(_dir_continent_html(title, vs))
    dir_html = "\n        ".join(parts) or "<p>Kits are rolling out — check the map soon.</p>"

    # Featured cards (first 6) — park heroes when available
    feat_bits = []
    # Prefer popular / named heroes first for parks hub
    featured_pool = list(filtered)
    prefer_by_kind = {
        "park": [
            "yellowstone",
            "grand-canyon",
            "yosemite",
            "zion",
            "acadia",
            "rocky-mountain",
            "great-smoky-mountains",
            "arches",
            "sequoia",
            "everglades",
            "mount-rainier",
            "joshua-tree",
        ],
        "zoo": [
            "dallas-zoo",
            "san-diego-zoo",
            "bronx-zoo",
            "national-zoo",
            "houston-zoo",
            "fort-worth-zoo",
        ],
        "aquarium": [
            "georgia-aquarium",
            "monterey-bay-aquarium",
            "childrens-aquarium-dallas",
            "shedd-aquarium",
            "aquarium-of-the-pacific",
            "seattle-aquarium",
        ],
        "museum": [
            "amnh",
            "childrens-museum-perot",
            "field-museum",
            "california-science-center",
            "air-and-space",
            "please-touch-museum",
        ],
    }
    if kind in prefer_by_kind:
        prefer = prefer_by_kind[kind]
        by_id = {v["id"]: v for v in filtered}
        ordered = [by_id[s] for s in prefer if s in by_id]
        rest = [v for v in filtered if v["id"] not in prefer]
        featured_pool = ordered + rest
    for v in featured_pool[:6]:
        emoji = esc(v.get("emoji") or "📍")
        name = esc(v.get("name") or v["id"])
        city = esc(v.get("city") or "")
        blurb = esc((v.get("blurb") or "")[:120])
        slug = esc(v["id"])
        mv = load_mission_venue(v["id"]) if kind == "park" else None
        hero = hero_img_src(mv, v["id"], bust="q2") if kind == "park" else ""
        if not hero and kind == "park":
            # base-relative for type pages (base=/field-pack/)
            cand = f"photos/np-hero-{v['id']}.jpg"
            if (FIELD / cand).is_file():
                hero = f"{cand}?v=q2"
        thumb = (
            f'<span class="type-feat-thumb"><img src="{esc(hero)}" alt="" width="640" height="360" loading="lazy" decoding="async" /></span>'
            if hero
            else f'<span class="type-feat-emoji" aria-hidden="true">{emoji}</span>'
        )
        feat_bits.append(
            f'<a class="type-feat-card{" type-feat-has-hero" if hero else ""}" href="/field-pack/{slug}/">'
            f"{thumb}"
            f"<strong>{name}</strong>"
            f"<small>{city}</small>"
            f'<span class="type-feat-blurb">{blurb}</span>'
            f"</a>"
        )
    featured = "\n          ".join(feat_bits) if feat_bits else ""

    url = f"{SITE}/field-pack/{path}/"
    map_href = f"/field-pack/?type={esc(meta['map_type'])}"
    nav_bits = []
    for t in TYPE_LANDINGS:
        cur = ' aria-current="page"' if t["path"] == path else ""
        nav_bits.append(
            f'<a class="place-type-tab{" is-active" if t["path"] == path else ""}" '
            f'href="/field-pack/{t["path"]}/"{cur}>{esc(t["nav"])}</a>'
        )
    type_nav = "\n            ".join(nav_bits)

    item_list = ", ".join(
        f'{{"@type":"ListItem","position":{i+1},"url":"{SITE}/field-pack/{esc(v["id"])}/","name":{json.dumps(v.get("name") or v["id"])}}}'
        for i, v in enumerate(filtered[:40])
    )
    json_ld = (
        "{"
        f'"@context":"https://schema.org","@type":"CollectionPage","name":{json.dumps(meta["h1"])},'
        f'"url":{json.dumps(url)},"description":{json.dumps(meta["blurb"])},'
        f'"isPartOf":{{"@type":"WebSite","name":"1Less Field Trip Kit","url":"{SITE}/field-pack/"}},'
        f'"mainEntity":{{"@type":"ItemList","numberOfItems":{len(filtered)},"itemListElement":[{item_list}]}}'
        "}"
    )

    og_img = PARK_OG_IMAGE if meta.get("kind") == "park" else OG_SHARE_IMAGE
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(meta["title"])}</title>
  <meta name="description" content="{esc(meta["blurb"])}" />
  <link rel="canonical" href="{esc(url)}" />
  <meta name="robots" content="index,follow" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="1Less" />
  <meta property="og:title" content="{esc(meta["title"])}" />
  <meta property="og:description" content="{esc(meta["blurb"])}" />
  <meta property="og:url" content="{esc(url)}" />
  <meta property="og:image" content="{og_img}" />
  <base href="/field-pack/" />
  <link rel="stylesheet" href="/shell/shell.css?v=6" />
  <link rel="stylesheet" href="/field-pack/css/styles.css?v={STYLES_CSS_VER}" />
  <link rel="stylesheet" href="/field-pack/css/landing.css?v={LANDING_CSS_VER}" />
  <link rel="stylesheet" href="/field-pack/css/seo-venue.css?v={SEO_CSS_VER}" />
  <script type="application/ld+json">
{json_ld}
  </script>
  <style>
    .type-landing {{ max-width: 56rem; margin: 0 auto 2rem; padding: 0 1rem 2rem; }}
    .type-landing h1 {{ margin: 0.5rem 0 0.75rem; font-size: clamp(1.5rem, 4vw, 2rem); color: #0a4545; }}
    .type-landing .type-lead {{ color: #3d4f6f; font-size: 1.05rem; line-height: 1.45; max-width: 40rem; }}
    .type-feat-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(11.5rem, 1fr)); gap: 0.85rem; margin: 1.25rem 0 1.5rem; }}
    .type-feat-card {{ display: flex; flex-direction: column; gap: 0.25rem; padding: 0.65rem 0.65rem 0.85rem; border-radius: 14px;
      background: rgba(255,255,255,0.92); border: 1.5px solid rgba(15,92,92,0.12); text-decoration: none; color: inherit;
      overflow: hidden; }}
    .type-feat-card:hover {{ border-color: #0f5c5c; }}
    .type-feat-emoji {{ font-size: 1.4rem; padding: 0.2rem 0.25rem 0; }}
    .type-feat-thumb {{ display: block; margin: -0.65rem -0.65rem 0.35rem; border-radius: 12px 12px 0 0; overflow: hidden;
      aspect-ratio: 16/10; background: #e8f2ee; }}
    .type-feat-thumb img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
    .type-feat-card strong {{ font-size: 0.92rem; color: #0a4545; padding: 0 0.25rem; }}
    .type-feat-card small {{ color: #5a6a84; padding: 0 0.25rem; }}
    .type-feat-blurb {{ font-size: 0.8rem; color: #3d4f6f; line-height: 1.3; padding: 0 0.25rem; }}
    .type-cta-row {{ display: flex; flex-wrap: wrap; gap: 0.6rem; margin: 1rem 0 1.5rem; }}
    .type-cta-row a {{ display: inline-flex; align-items: center; padding: 0.55rem 1rem; border-radius: 999px;
      font-weight: 750; text-decoration: none; }}
    .type-cta-primary {{ background: #0f5c5c; color: #fff; }}
    .type-cta-secondary {{ background: #fff; color: #0a4545; border: 1.5px solid rgba(15,92,92,0.2); }}
    .type-count {{ font-weight: 700; color: #0f5c5c; }}
    .place-type-tabs a.place-type-tab {{ text-decoration: none; }}
  </style>
</head>
<body class="seo-venue-body type-hub-body" data-place-type="{esc(meta["map_type"])}">
  <div class="app-shell">
    <header class="shell-bar no-print">
      <a class="shell-brand" href="/field-pack/" aria-label="Field Trip Kit home">
        <img src="/1LessMark.png" alt="" width="52" height="52" />
      </a>
      <a class="shell-product" href="/field-pack/">
        Field Trip Kit
        <small>{HEADER_TAGLINE}</small>
      </a>
    </header>

    <nav class="place-type-tabs no-print" aria-label="Place type">
      <div class="place-type-seg" role="navigation">
        <a class="place-type-tab" href="/field-pack/">All</a>
        {type_nav}
      </div>
    </nav>

    <main class="type-landing">
      <p class="seo-crumbs"><a href="/field-pack/">Field Trip Kit</a> · {esc(meta["nav"])}</p>
      <h1>{esc(meta["h1"])}</h1>
      <p class="type-lead">{esc(meta["blurb"])}</p>
      <p class="type-count">{len(filtered)} places</p>
      <div class="type-cta-row">
        <a class="type-cta-primary" href="/field-pack/virtual-field-trip/">{esc(CTA_EXPLORE_HOME)}</a>
        <a class="type-cta-secondary" href="{map_href}">Open map · {esc(meta["nav"])}</a>
        <a class="type-cta-secondary" href="/field-pack/">{esc(CTA_PRINT_VISIT)}</a>
      </div>
      {"<h2>Start here</h2><div class=\"type-feat-grid\">" + featured + "</div>" if featured else ""}
      <h2 id="dir-heading">{esc(meta["nav"])}</h2>
      <p id="dir-blurb">{esc(meta["pitch"])}</p>
      <div id="seo-venue-directory" class="seo-dir-body">
        {dir_html}
      </div>
    </main>
  </div>
  <script src="/shell/shell.js?v=5" defer></script>
</body>
</html>
"""
    out_dir = FIELD / path
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(html, encoding="utf-8")
    return f"/field-pack/{path}/"


def write_parks_alias() -> None:
    """ /field-pack/parks/ → national-parks (meta refresh + link). """
    out_dir = FIELD / "parks"
    out_dir.mkdir(parents=True, exist_ok=True)
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>National Parks · Field Trip Kit</title>
  <link rel="canonical" href="https://1less.app/field-pack/national-parks/" />
  <meta http-equiv="refresh" content="0;url=/field-pack/national-parks/" />
  <script>location.replace("/field-pack/national-parks/");</script>
</head>
<body>
  <p><a href="/field-pack/national-parks/">National &amp; world park scavenger hunts</a></p>
</body>
</html>
"""
    (out_dir / "index.html").write_text(html, encoding="utf-8")


def write_type_landings(venues: list[dict]) -> list[str]:
    urls = []
    for meta in TYPE_LANDINGS:
        u = write_type_landing(meta, venues)
        urls.append(u)
        print(f"  type landing {u} ({sum(1 for v in venues if venue_type_kind(v) == meta['kind'])} places)")
    write_parks_alias()
    print("  type landing alias /field-pack/parks/ → national-parks")
    return urls


def write_sitemap(venues: list[dict], extra_urls: list[str] | None = None) -> None:
    urls = [f"{SITE}/field-pack/"]
    for u in extra_urls or []:
        if u.startswith("http"):
            urls.append(u)
        else:
            urls.append(f"{SITE}{u}")
    urls += [f"{SITE}/field-pack/{v['id']}/" for v in venues]
    # also root redirect target
    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    seen = set()
    for u in urls:
        if u in seen:
            continue
        seen.add(u)
        pri = "1.0" if u.rstrip("/").endswith("field-pack") else ("0.9" if any(x in u for x in ("/zoos", "/aquariums", "/museums", "/national-parks", "/cards", "/virtual-zoo", "/virtual-field-trip")) else "0.8")
        body.append("  <url>")
        body.append(f"    <loc>{esc(u)}</loc>")
        body.append(f"    <lastmod>{TODAY}</lastmod>")
        body.append(f"    <changefreq>weekly</changefreq>")
        body.append(f"    <priority>{pri}</priority>")
        body.append("  </url>")
    body.append("</urlset>")
    body.append("")
    (STATIC / "sitemap.xml").write_text("\n".join(body), encoding="utf-8")
    # also under field-pack for convenience
    (FIELD / "sitemap.xml").write_text("\n".join(body), encoding="utf-8")


def write_robots() -> None:
    text = f"""User-agent: *
Allow: /
Allow: /field-pack/
Disallow: /dinner
Disallow: /analytics/
Disallow: /api/

Sitemap: {SITE}/sitemap.xml
"""
    (STATIC / "robots.txt").write_text(text, encoding="utf-8")
    (REPO / "static" / "robots.txt").write_text(text, encoding="utf-8")


SEO_CSS = """/* SEO venue pages — visual-first, same brand language as outing cards */
.seo-venue-body .seo-crumbs {
  margin: 0 0 12px;
  font-weight: 700;
  font-size: 0.9rem;
  color: #3d4f6f;
}
.seo-venue-body .seo-crumbs a {
  color: #0f5c5c;
  font-weight: 800;
  text-decoration: none;
}
.seo-venue-body .seo-crumbs a:hover { text-decoration: underline; }
.seo-article {
  max-width: 52rem;
  margin: 0 auto 28px;
  padding: 22px 22px 28px;
  border-radius: 24px;
  background: rgba(255,255,255,0.92);
  border: 1.5px solid rgba(15, 92, 92, 0.12);
  box-shadow: 0 12px 36px rgba(21, 34, 56, 0.08);
}
.seo-hero h1 {
  margin: 8px 0 12px;
  font-size: clamp(1.55rem, 4vw, 2.1rem);
  line-height: 1.15;
  color: #0a4545;
  letter-spacing: -0.02em;
}
.seo-brand-note {
  margin: 0 0 14px;
  font-weight: 650;
  color: #3d4f6f;
  font-size: 0.95rem;
}

/* Top photo strip under CTAs */
.seo-hero-photos {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin: 0 0 22px;
}
.seo-hero-photos img {
  width: 100%;
  height: 148px;
  object-fit: cover;
  border-radius: 16px;
  border: 1.5px solid rgba(15, 92, 92, 0.12);
  box-shadow: 0 8px 20px rgba(21, 34, 56, 0.08);
  background: #dfe7f2;
  display: block;
}

/* Animal / exhibit photo cards (match outing visual energy) */
.seo-animal-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin: 12px 0 8px;
}
.seo-animal-card {
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1.5px solid rgba(15, 92, 92, 0.12);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 14px rgba(21, 34, 56, 0.06);
  min-height: 220px;
  text-decoration: none;
  color: inherit;
  transition: border-color 0.15s ease, box-shadow 0.15s ease, transform 0.15s ease;
}
.seo-animal-card:hover {
  border-color: #d9652e;
  box-shadow: 0 8px 20px rgba(217, 101, 46, 0.14);
  transform: translateY(-1px);
}
.seo-card-hint {
  margin: 4px 0 0 !important;
  font-size: 0.8rem !important;
  font-weight: 800 !important;
  color: #d9652e !important;
}
.seo-animal-card {
  cursor: pointer;
}
.seo-animal-card img {
  width: 100%;
  height: 132px;
  object-fit: cover;
  background: linear-gradient(145deg, #e8f0f8, #d4e4d8);
  display: block;
}
.seo-animal-meta {
  padding: 12px 12px 14px;
  display: grid;
  gap: 4px;
}
.seo-animal-meta h3 {
  margin: 0;
  font-size: 1.02rem;
  font-weight: 800;
  letter-spacing: -0.01em;
  color: #0a4545;
  line-height: 1.2;
}
.seo-animal-meta p {
  margin: 0;
  font-size: 0.88rem;
  font-weight: 650;
  color: #3d4f6f;
  line-height: 1.35;
}

/* Keep text list for crawlers / no-image clients, but de-emphasize visually */
.seo-shortlist-sr {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.seo-prose p {
  margin: 0 0 12px;
  line-height: 1.55;
  font-weight: 600;
  color: #2a3d55;
  font-size: 1.02rem;
}
.seo-list-block {
  margin: 22px 0 8px;
  position: relative;
}
.seo-list-block h2 {
  margin: 0 0 8px;
  font-size: 1.2rem;
  color: #0a4545;
}
.seo-list-block > p {
  margin: 0 0 8px;
  font-weight: 650;
  color: #3d4f6f;
}
.seo-shortlist, .seo-hunt-list {
  margin: 0;
  padding-left: 1.2rem;
  font-weight: 650;
  color: #2a3d55;
  line-height: 1.5;
}
.seo-shortlist li, .seo-hunt-list li { margin-bottom: 6px; }
.seo-how { margin-top: 22px; }
.seo-how h2 { margin: 0 0 10px; font-size: 1.2rem; color: #0a4545; }
.seo-official {
  margin: 18px 0 0;
  font-weight: 650;
  color: #3d4f6f;
  font-size: 0.95rem;
}
.seo-official a { color: #0f5c5c; font-weight: 800; }
.seo-cta { flex-wrap: wrap; gap: 10px; }
.seo-directory {
  margin: 28px 0 18px;
  padding: 20px 18px 22px;
  border-radius: 24px;
  background: rgba(255,255,255,0.9);
  border: 1.5px solid rgba(15, 92, 92, 0.12);
}
.seo-directory h2 {
  margin: 0 0 8px;
  font-size: 1.25rem;
  color: #0a4545;
}
.seo-directory > p {
  margin: 0 0 14px;
  font-weight: 650;
  color: #3d4f6f;
}
.seo-dir-grid {
  columns: 2;
  column-gap: 24px;
  margin: 0;
  padding: 0;
  list-style: none;
}
.seo-dir-grid li {
  break-inside: avoid;
  margin: 0 0 8px;
  font-weight: 700;
}
.seo-dir-grid a {
  color: #0a4545;
  text-decoration: none;
  border-bottom: 1px solid rgba(15, 92, 92, 0.25);
}
.seo-dir-grid a:hover { color: #0f5c5c; border-bottom-color: #0f5c5c; }
.seo-dir-grid small {
  display: block;
  font-weight: 600;
  color: #5a6b82;
  font-size: 0.82rem;
  margin-top: 1px;
}
.seo-faq {
  margin: 18px 0 24px;
  padding: 20px 18px 8px;
  border-radius: 24px;
  background: rgba(255,255,255,0.9);
  border: 1.5px solid rgba(15, 92, 92, 0.12);
}
.seo-faq h2 {
  margin: 0 0 12px;
  font-size: 1.25rem;
  color: #0a4545;
}
.seo-faq details {
  margin: 0 0 12px;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(232, 246, 240, 0.55);
  border: 1px solid rgba(15, 92, 92, 0.1);
}
.seo-faq summary {
  cursor: pointer;
  font-weight: 800;
  color: #0a4545;
}
.seo-faq details p {
  margin: 8px 0 0;
  font-weight: 600;
  color: #2a3d55;
  line-height: 1.5;
}
@media (max-width: 720px) {
  .seo-animal-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .seo-hero-photos { grid-template-columns: 1fr 1fr; }
  .seo-hero-photos img:nth-child(3) { display: none; }
}
@media (max-width: 640px) {
  .seo-dir-grid { columns: 1; }
  .seo-article { padding: 16px; }
  .seo-animal-grid { grid-template-columns: 1fr; }
  .seo-hero-photos { grid-template-columns: 1fr 1fr; }
  .seo-animal-card img, .seo-hero-photos img { height: 160px; }
}
"""


# Light continent buckets (<10) — venue names stay visible under each heading
_CONTINENT_ORDER = (
    "North America",
    "South America",
    "Europe",
    "Africa & Middle East",
    "Asia",
    "Oceania",
)

# Country / territory label (from location string) → continent
_COUNTRY_CONTINENT = {
    "united states": "North America",
    "usa": "North America",
    "us": "North America",
    "canada": "North America",
    "mexico": "North America",
    "brazil": "South America",
    "argentina": "South America",
    "chile": "South America",
    "peru": "South America",
    "colombia": "South America",
    "united kingdom": "Europe",
    "uk": "Europe",
    "france": "Europe",
    "germany": "Europe",
    "spain": "Europe",
    "italy": "Europe",
    "netherlands": "Europe",
    "belgium": "Europe",
    "ireland": "Europe",
    "austria": "Europe",
    "switzerland": "Europe",
    "portugal": "Europe",
    "sweden": "Europe",
    "norway": "Europe",
    "finland": "Europe",
    "denmark": "Europe",
    "poland": "Europe",
    "hungary": "Europe",
    "czechia": "Europe",
    "czech republic": "Europe",
    "greece": "Europe",
    "russia": "Europe",
    "türkiye": "Europe",
    "turkey": "Europe",
    "uae": "Africa & Middle East",
    "united arab emirates": "Africa & Middle East",
    "south africa": "Africa & Middle East",
    "kenya": "Africa & Middle East",
    "egypt": "Africa & Middle East",
    "india": "Asia",
    "japan": "Asia",
    "china": "Asia",
    "south korea": "Asia",
    "korea": "Asia",
    "singapore": "Asia",
    "taiwan": "Asia",
    "thailand": "Asia",
    "indonesia": "Asia",
    "philippines": "Asia",
    "malaysia": "Asia",
    "hong kong": "Asia",
    "australia": "Oceania",
    "new zealand": "Oceania",
    "croatia": "Europe",
    "ireland": "Europe",
    "wales": "Europe",
    "scotland": "Europe",
    "england": "Europe",
    "u.s. virgin islands": "North America",
    "us virgin islands": "North America",
    "virgin islands": "North America",
    "american samoa": "Oceania",
    "puerto rico": "North America",
}


def _venue_country_label(v: dict) -> str:
    loc = (v.get("location") or "").strip()
    if "," in loc:
        return loc.split(",")[-1].strip()
    st = (v.get("state") or "").strip()
    if st and len(st) <= 3:
        return "United States"
    if loc and loc not in (v.get("city") or ""):
        return loc
    if st:
        return "United States"
    # Single-name city-states (Singapore) or bare city
    city = (v.get("city") or loc or "").strip()
    if city.lower() in _COUNTRY_CONTINENT:
        return city
    if city.lower() == "singapore":
        return "Singapore"
    if city.lower() == "hong kong":
        return "Hong Kong"
    return city or "International"


def _venue_continent(v: dict) -> str:
    """Bucket venues for directory headings. Prefer explicit country codes."""
    # Explicit ISO / territory codes on venue JSON
    cc = (v.get("country") or "").strip().upper()
    st0 = (v.get("state") or v.get("region") or "").strip().upper()
    # American Samoa is a US territory in Oceania (check before broad US → NA)
    if cc in {"AS"} or st0 == "AS":
        return "Oceania"
    if cc in {"US", "USA", "CA", "MX", "PR", "VI", "GU", "MP"}:
        return "North America"
    if cc in {"BR", "AR", "CL", "PE", "CO", "EC", "UY", "PY", "BO", "VE"}:
        return "South America"
    if cc in {"GB", "UK", "IE", "FR", "DE", "ES", "IT", "NL", "BE", "AT", "CH", "PT",
              "SE", "NO", "FI", "DK", "PL", "HU", "CZ", "GR", "RU", "TR", "HR", "RO", "UA"}:
        return "Europe"
    if cc in {"ZA", "KE", "EG", "AE", "MA", "NG", "TZ", "UG", "ET"}:
        return "Africa & Middle East"
    if cc in {"JP", "CN", "KR", "IN", "SG", "TW", "TH", "ID", "PH", "MY", "HK", "VN"}:
        return "Asia"
    if cc in {"AU", "NZ", "FJ", "PG", "WS"}:
        return "Oceania"

    st = (v.get("state") or v.get("region") or "").strip().upper()
    # US states + DC
    _US_STATES = {
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI",
        "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN",
        "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH",
        "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA",
        "WV", "WI", "WY",
    }
    # US Caribbean / Pacific territories (not states)
    _US_TERR_NA = {"PR", "VI", "GU", "MP"}  # North America / Caribbean / western Pacific US
    _US_TERR_OC = {"AS"}  # American Samoa → Oceania
    if st in _US_STATES or st in _US_TERR_NA:
        return "North America"
    if st in _US_TERR_OC:
        return "Oceania"
    # Canadian provinces commonly appear as 2-letter codes
    if st in {"AB", "BC", "MB", "NB", "NL", "NS", "NT", "NU", "ON", "PE", "QC", "SK", "YT"}:
        return "North America"

    country = _venue_country_label(v)
    key = country.lower()
    # Territory names that appear after comma in location strings
    if key in {"vi", "u.s. virgin islands", "us virgin islands", "virgin islands",
               "puerto rico", "pr", "guam", "northern mariana islands"}:
        return "North America"
    if key in {"as", "american samoa"}:
        return "Oceania"
    if key in _COUNTRY_CONTINENT:
        return _COUNTRY_CONTINENT[key]
    city = (v.get("city") or "").strip().lower()
    if city in _COUNTRY_CONTINENT:
        return _COUNTRY_CONTINENT[city]
    # Last resort: lat/lon hemisphere hints for known gaps
    try:
        lat = float(v.get("lat") or 0)
        lng = float(v.get("lng") or v.get("lon") or 0)
        if 17 <= lat <= 19 and -66 <= lng <= -64:  # USVI
            return "North America"
        if -15 <= lat <= -13 and -172 <= lng <= -169:  # American Samoa
            return "Oceania"
    except (TypeError, ValueError):
        pass
    return "Asia"  # rare unknown intl → Asia bucket rather than orphan


def _dir_item_html(v: dict) -> str:
    loc = v.get("city") or ""
    if not loc:
        loc = (v.get("location") or "").split(",")[0].strip()
    city = esc(loc) if loc else ""
    small = f"<small>{city}</small>" if city else ""
    return (
        f'<li><a href="/field-pack/{esc(v["id"])}/">{esc(v.get("emoji") or "")} {esc(v["name"])}</a>'
        f"{small}</li>"
    )


def _dir_region_slug(title: str) -> str:
    return (
        title.lower()
        .replace("&", "and")
        .replace(" ", "-")
        .replace(",", "")
    )


def _dir_continent_html(title: str, venues: list[dict], *, heading: str = "h4") -> str:
    """Always-open region section — venue names stay visible (light structure only).

    heading: h3 when region is top-level (hubs); h4 when nested under day-type (landing).
    """
    if not venues:
        return ""
    if heading not in {"h3", "h4"}:
        heading = "h4"
    venues = sorted(
        venues,
        key=lambda x: ((x.get("city") or "").lower(), (x.get("name") or "").lower()),
    )
    items = "\n            ".join(_dir_item_html(v) for v in venues)
    slug = esc(_dir_region_slug(title))
    return (
        f'<section class="seo-dir-region" data-region="{slug}">\n'
        f'          <{heading} class="seo-dir-region-title">{esc(title)} '
        f'<span class="seo-dir-count">{len(venues)}</span></{heading}>\n'
        f'          <ul class="seo-dir-grid">\n            {items}\n          </ul>\n'
        f"        </section>"
    )


# Landing catalog: Places (type→region→venue) + Cards (group→item)
# Collapsed <details>; ~3 sample links visible before expand.
_DIR_SAMPLE_N = 10

_TYPE_DIR_META = (
    {
        "kind": "zoo",
        "id": "dir-zoos",
        "label": "Zoos &amp; safaris",
        "hub": "/field-pack/zoos/",
        "hub_label": "All zoos",
        "sample_ids": ("dallas-zoo", "san-diego-zoo", "bronx-zoo", "singapore-zoo", "london-zoo"),
    },
    {
        "kind": "aquarium",
        "id": "dir-aquariums",
        "label": "Aquariums",
        "hub": "/field-pack/aquariums/",
        "hub_label": "All aquariums",
        "sample_ids": (
            "georgia-aquarium",
            "monterey-bay-aquarium",
            "national-aquarium-baltimore",
            "shedd-aquarium",
        ),
    },
    {
        "kind": "museum",
        "id": "dir-museums",
        "label": "Museums &amp; science",
        "hub": "/field-pack/museums/",
        "hub_label": "All museums",
        "sample_ids": (
            "kennedy-space-center",
            "air-and-space",
            "amnh",
            "childrens-museum-perot",
            "thinkery",
        ),
    },
    {
        "kind": "park",
        "id": "dir-parks",
        "label": "Parks",
        "hub": "/field-pack/national-parks/",
        "hub_label": "All parks",
        "sample_ids": ("yellowstone", "yosemite", "grand-canyon", "zion", "banff"),
    },
)

# Card families pair with place types (top tabs):
#   wildlife → zoos | sealife → aquariums | attractions → museums
_WILDLIFE_GROUP_ORDER = (
    ("mammals", "Mammals", ("african-lion", "reticulated-giraffe", "giant-panda")),
    ("birds", "Birds", ("african-penguin", "caribbean-flamingo", "ostrich")),
    ("reptiles", "Reptiles", ("galapagos-tortoise",)),
)

_WILDLIFE_GROUP_BY_ID = {
    "african-elephant": "mammals",
    "african-lion": "mammals",
    "asian-small-clawed-otter": "mammals",
    "cheetah": "mammals",
    "chimpanzee": "mammals",
    "giant-panda": "mammals",
    "koala": "mammals",
    "nile-hippo": "mammals",
    "orangutan": "mammals",
    "red-panda": "mammals",
    "reticulated-giraffe": "mammals",
    "ring-tailed-lemur": "mammals",
    "sumatran-tiger": "mammals",
    "two-toed-sloth": "mammals",
    "warthog": "mammals",
    "western-lowland-gorilla": "mammals",
    "zebra": "mammals",
    "african-penguin": "birds",
    "caribbean-flamingo": "birds",
    "ostrich": "birds",
    "galapagos-tortoise": "reptiles",
}

_SEALIFE_GROUP_ORDER = (
    (
        "fish",
        "Sharks, fish &amp; turtles",
        ("shark", "clownfish", "stingray", "sea-turtle", "seahorse"),
    ),
    (
        "inverts",
        "Jellies &amp; ocean invertebrates",
        ("octopus", "jellyfish", "crab", "starfish"),
    ),
)

_SEALIFE_GROUP_BY_ID = {
    "clownfish": "fish",
    "eel": "fish",
    "freshwater-fish": "fish",
    "seahorse": "fish",
    "shark": "fish",
    "stingray": "fish",
    "sea-turtle": "fish",
    "crab": "inverts",
    "jellyfish": "inverts",
    "octopus": "inverts",
    "starfish": "inverts",
}

# Back-compat aliases used nowhere new — keep empty maps for safety
_ANIMAL_GROUP_ORDER = _WILDLIFE_GROUP_ORDER
_ANIMAL_GROUP_BY_ID = {**_WILDLIFE_GROUP_BY_ID, **_SEALIFE_GROUP_BY_ID}

# Museum / science attraction cards
_ATTRACTION_GROUP_ORDER = (
    ("space", "Space &amp; rockets", ("sci-rocket", "sci-shuttle", "sci-astronaut", "sci-planet")),
    (
        "nature-halls",
        "Dinosaurs &amp; nature halls",
        ("sci-dinosaur", "sci-mammal-hall", "sci-rainforest", "sci-aquarium-zone"),
    ),
    (
        "kids-play",
        "Kids play zones",
        (
            "cm-makery",
            "cm-imaginarium",
            "cm-toddler-garden",
            "cm-art-lab",
            "cm-waterfall",
            "cm-woven",
            "cm-free-explore",
            "sci-hands-on",
        ),
    ),
)

_ATTRACTION_GROUP_BY_ID = {
    "sci-rocket": "space",
    "sci-shuttle": "space",
    "sci-astronaut": "space",
    "sci-planet": "space",
    "sci-dinosaur": "nature-halls",
    "sci-mammal-hall": "nature-halls",
    "sci-rainforest": "nature-halls",
    "sci-aquarium-zone": "nature-halls",
    "cm-makery": "kids-play",
    "cm-imaginarium": "kids-play",
    "cm-toddler-garden": "kids-play",
    "cm-art-lab": "kids-play",
    "cm-waterfall": "kids-play",
    "cm-woven": "kids-play",
    "cm-free-explore": "kids-play",
    "sci-hands-on": "kids-play",
}


def _sort_venues(venues: list[dict]) -> list[dict]:
    return sorted(
        venues,
        key=lambda x: ((x.get("city") or "").lower(), (x.get("name") or "").lower()),
    )


def _pick_samples(items: list[dict], preferred_ids: tuple[str, ...] | list[str], n: int = _DIR_SAMPLE_N) -> list[dict]:
    """Prefer curated ids, then fill from sorted list."""
    by_id = {str(x.get("id") or ""): x for x in items}
    out: list[dict] = []
    seen: set[str] = set()
    for pid in preferred_ids or ():
        it = by_id.get(pid)
        if it and pid not in seen:
            out.append(it)
            seen.add(pid)
        if len(out) >= n:
            return out
    for it in items:
        iid = str(it.get("id") or "")
        if not iid or iid in seen:
            continue
        out.append(it)
        seen.add(iid)
        if len(out) >= n:
            break
    return out


def _venue_li_html(v: dict) -> str:
    return _dir_item_html(v)


def _item_li_html(it: dict) -> str:
    """Printable card row — print via JS; fallback link opens outing with that card."""
    iid = esc(it["id"])
    venue = esc(it.get("venue") or "")
    name = esc(it.get("name") or it["id"])
    emoji = esc(it.get("emoji") or "")
    label = f"{emoji} {name}".strip()
    href = f"/field-pack/cards/{iid}/"
    return (
        f'<li class="seo-dir-card-item">'
        f'<a class="seo-dir-card-link" href="{href}" data-print-item="{iid}"'
        f'{f" data-print-venue=\"{venue}\"" if venue else ""}>'
        f"{label}</a>"
        f'<button type="button" class="seo-dir-print-btn no-print" data-print-item="{iid}"'
        f'{f" data-print-venue=\"{venue}\"" if venue else ""} aria-label="Print {name}">Print</button>'
        f"</li>"
    )


def _samples_and_rest_html(
    items: list[dict],
    *,
    li_fn,
    preferred_ids: tuple[str, ...] = (),
    list_class: str = "seo-dir-grid",
    rest_label: str | None = None,
) -> str:
    """Always show ~3 samples; full list behind one nested details if longer."""
    if not items:
        return ""
    samples = _pick_samples(items, preferred_ids, _DIR_SAMPLE_N)
    sample_ids = {str(s.get("id") or "") for s in samples}
    rest = [x for x in items if str(x.get("id") or "") not in sample_ids]
    sample_ul = (
        f'<ul class="{list_class} seo-dir-samples">\n            '
        + "\n            ".join(li_fn(x) for x in samples)
        + "\n          </ul>"
    )
    if not rest:
        return sample_ul
    label = rest_label or f"Show all {len(items)}"
    rest_ul = (
        f'<ul class="{list_class}">\n            '
        + "\n            ".join(li_fn(x) for x in items)
        + "\n          </ul>"
    )
    return (
        f"{sample_ul}\n"
        f'          <details class="seo-dir-more">\n'
        f'            <summary class="seo-dir-more-sum">{esc(label)}</summary>\n'
        f"            {rest_ul}\n"
        f"          </details>"
    )


def _place_is_us(v: dict) -> bool:
    """US + territories; intl has explicit non-US country or no US state."""
    cc = (v.get("country") or "").strip().upper()
    st = (v.get("state") or "").strip().upper()
    if cc in {"CA", "GB", "UK", "AU", "NZ", "ZA", "JP", "FR", "HR", "AR", "CL", "PE", "KE",
              "MX", "BR", "DE", "ES", "IT", "NL", "BE", "AT", "CH", "PT", "SE", "NO", "FI",
              "DK", "PL", "HU", "CZ", "GR", "RU", "TR", "IE", "SG", "KR", "CN", "IN", "TH",
              "ID", "PH", "MY", "HK", "TW", "AE", "EG", "CO", "PE"}:
        return False
    if cc in {"US", "USA", "PR", "VI", "GU", "MP"}:
        return True
    if cc == "AS":
        return True  # American Samoa NP still “US system”
    if st and len(st) == 2:
        return True
    # Domestic places-data often omits country and uses state
    if not cc and st:
        return True
    if not cc and not st:
        # Heuristic: US city list isn't available — treat missing as US only if lat in US box
        try:
            lat = float(v.get("lat") or 0)
            lng = float(v.get("lng") or 0)
            if 24 <= lat <= 50 and -125 <= lng <= -66:
                return True
        except (TypeError, ValueError):
            pass
        return False
    return cc in {"US", "USA"} or not cc


# --- Smart L2 categories (not geography — map handles region) ---
# Only emit a category when it has enough venues (see _MIN_CAT).

_MIN_CAT = 4

_ZOO_SAFARI_IDS = frozenset(
    {
        "san-diego-safari-park",
        "singapore-night-safari",
        "nairobi-safari-walk",
        "bangalore-bannerghatta",
        "bangkok-safari-world",
        "hong-kong-ocean-park",
    }
)
_ZOO_LARGE_IDS = frozenset(
    {
        # US flagships / major metros
        "dallas-zoo",
        "fort-worth-zoo",
        "houston-zoo",
        "san-diego-zoo",
        "la-zoo",
        "bronx-zoo",
        "national-zoo",
        "national-zoo",
        "omaha-henry-doorly",
        "columbus-zoo",
        "st-louis-zoo",
        "cincinnati-zoo",
        "philadelphia-zoo",
        "detroit-zoo",
        "denver-zoo",
        "minnesota-zoo",
        "north-carolina-zoo",
        "oregon-zoo",
        "woodland-park-zoo",
        "miami-zoo",
        "toronto-zoo",
        "calgary-zoo",
        # World flagships
        "london-zoo",
        "singapore-zoo",
        "berlin-zoo",
        "beijing-zoo",
        "ueno-zoo",
        "taronga-zoo",
        "melbourne-zoo",
        "perth-zoo",
        "auckland-zoo",
        "prague-zoo",
        "vienna-zoo",
        "artis-zoo",
        "antwerp-zoo",
        "barcelona-zoo",
        "paris-zoo",
        "munich-zoo",
        "copenhagen-zoo",
        "dublin-zoo",
        "edinburgh-zoo",
        "budapest-zoo",
        "warsaw-zoo",
        "moscow-zoo",
        "seoul-zoo",
        "taipei-zoo",
        "jakarta-ragunan",
        "chapultepec-zoo",
        "sao-paulo-zoo",
        "johannesburg-zoo",
        "cairo-zoo",
        "delhi-zoo",
        "mumbai-byculla-zoo",
        "manila-zoo",
        "zurich-zoo",
        "ecoparque-ba",
    }
)
_ZOO_SMALL_IDS = frozenset(
    {
        "austin-zoo",
        "adelaide-zoo",
        "wellington-zoo",
        "honolulu-zoo",
        "oslo-zoo",
        "helsinki-zoo",
        "stockholm-skansen",
        "athens-attica-zoo",
        "al-ain-zoo",
        "point-defiance-zoo",
        "hogle-zoo",
        "audubon-zoo",
        "lima-leyendas",
        "bogota-zoo",
        "santiago-zoo",
        "rio-zoo",
        "nashville-zoo",
        "memphis-zoo",
    }
)

_AQ_COMPACT_IDS = frozenset(
    {
        "childrens-aquarium-dallas",
        "dallas-world-aquarium",
        "waikiki-aquarium",
        "lotte-aquarium-seoul",
    }
)


def _zoo_category(v: dict) -> str:
    vid = str(v.get("id") or "")
    name = f"{v.get('name') or ''} {v.get('type') or ''}".lower()
    if vid in _ZOO_SAFARI_IDS or "safari" in name or "wildlife park" in name or "biological park" in name:
        return "safari"
    if vid in _ZOO_SMALL_IDS:
        return "small"
    blurb = (v.get("blurb") or "").lower()
    if any(
        x in blurb
        for x in (
            "without a stadium",
            "compact",
            "short walkable",
            "small loop",
            "perfect first",
            "first zoo",
        )
    ):
        return "small"
    if vid in _ZOO_LARGE_IDS or (v.get("tier") or "") == "top":
        return "large"
    # quality full + many featured often = major day
    feat = v.get("featured") or []
    if (v.get("quality") or "") == "full" and len(feat) >= 10 and vid not in _ZOO_SMALL_IDS:
        return "large"
    return "other"


def _aquarium_category(v: dict) -> str:
    vid = str(v.get("id") or "")
    name = (v.get("name") or "").lower()
    if vid in _AQ_COMPACT_IDS or "children" in name or "kids" in name:
        return "compact"
    return "major"


def _museum_category(v: dict) -> str:
    raw = str(v.get("type") or "").lower().strip()
    t = raw.replace("-", " ").replace("_", " ")
    name = (v.get("name") or "").lower()
    vid = str(v.get("id") or "")
    if (
        "children" in t
        or raw in {"cm", "childrens_museum"}
        or "children" in name
        or "please touch" in name
        or "doseum" in name
        or "thinkery" in name
    ):
        return "childrens"
    # Natural history — short codes + names (before generic "science")
    if raw in {"nh", "natural_history"} or "natural history" in t or "natural history" in name:
        return "natural_history"
    if any(
        x in vid
        for x in (
            "field-museum",
            "amnh",
            "smithsonian-natural",
            "carnegie-natural",
            "nhm-london",
            "denver-museum-nature",
        )
    ):
        return "natural_history"
    # Space folds into science & space (not enough for its own bucket)
    return "science"


def _park_category(v: dict) -> str:
    return "us" if _place_is_us(v) else "world"


# kind → ordered (cat_id, label, sample_ids)
_PLACE_CATS: dict[str, tuple[tuple[str, str, tuple[str, ...]], ...]] = {
    "zoo": (
        ("large", "Large city zoos", ("dallas-zoo", "san-diego-zoo", "bronx-zoo", "singapore-zoo", "london-zoo", "berlin-zoo", "national-zoo", "houston-zoo", "taronga-zoo", "beijing-zoo")),
        ("safari", "Safari &amp; wildlife parks", ("san-diego-safari-park", "singapore-night-safari", "bangkok-safari-world", "nairobi-safari-walk", "bangalore-bannerghatta")),
        ("small", "Smaller &amp; local zoos", ("austin-zoo", "honolulu-zoo", "wellington-zoo", "adelaide-zoo", "audubon-zoo", "hogle-zoo")),
        ("other", "More zoos", ("phoenix-zoo", "milwaukee-zoo", "kansas-city-zoo", "pittsburgh-zoo", "madrid-zoo", "rome-bioparco")),
    ),
    "aquarium": (
        ("major", "Major aquariums", ("georgia-aquarium", "monterey-bay-aquarium", "shedd-aquarium", "national-aquarium-baltimore", "osaka-aquarium", "two-oceans-aquarium")),
        ("compact", "Compact &amp; kids aquariums", ("childrens-aquarium-dallas", "waikiki-aquarium", "dallas-world-aquarium", "lotte-aquarium-seoul")),
    ),
    "museum": (
        ("science", "Science &amp; space", ("kennedy-space-center", "air-and-space", "california-science-center", "perot-museum", "frost-science", "museum-of-science-boston")),
        ("natural_history", "Natural history", ("amnh", "field-museum", "smithsonian-natural-history", "carnegie-natural-history", "nhm-london")),
        ("childrens", "Children’s museums", ("childrens-museum-perot", "thinkery", "doseum", "indy-childrens-museum", "please-touch-museum")),
    ),
    "park": (
        ("us", "US national parks", ("yellowstone", "yosemite", "grand-canyon", "zion", "acadia", "rocky-mountain", "olympic", "glacier")),
        ("world", "Parks worldwide", ("banff", "kruger", "plitvice-lakes", "torres-del-paine", "fiordland", "table-mountain", "iguazu-argentina")),
    ),
}


def _classify_place(kind: str, v: dict) -> str:
    if kind == "zoo":
        return _zoo_category(v)
    if kind == "aquarium":
        return _aquarium_category(v)
    if kind == "museum":
        return _museum_category(v)
    if kind == "park":
        return _park_category(v)
    return "other"


def _dir_cat_details_html(
    cat_id: str,
    title: str,
    venues: list[dict],
    preferred_ids: tuple[str, ...] = (),
) -> str:
    """L2 smart category under a place type — collapsed, samples + expand all."""
    if not venues:
        return ""
    venues = _sort_venues(venues)
    slug = esc(cat_id)
    body = _samples_and_rest_html(
        venues,
        li_fn=_venue_li_html,
        preferred_ids=preferred_ids,
        rest_label=f"Show all {len(venues)}",
    )
    return (
        f'<details class="seo-dir-region seo-dir-cat" data-cat="{slug}">\n'
        f'            <summary class="seo-dir-region-sum">'
        f'<span class="seo-dir-region-label">{title}</span> '
        f'<span class="seo-dir-count">{len(venues)}</span></summary>\n'
        f"            {body}\n"
        f"          </details>"
    )


def _bucket_places(kind: str, venues: list[dict]) -> list[tuple[str, str, tuple[str, ...], list[dict]]]:
    """Return non-empty categories; merge undersized into 'other' / last bucket."""
    specs = list(_PLACE_CATS.get(kind) or (("other", "More", ()),))
    buckets: dict[str, list[dict]] = {sid: [] for sid, _, _ in specs}
    for v in venues:
        cid = _classify_place(kind, v)
        if cid not in buckets:
            # map unknown → last bucket
            cid = specs[-1][0]
        buckets[cid].append(v)

    # Merge tiny categories into a fallthrough bucket
    fallthrough = "other" if "other" in buckets else specs[-1][0]
    if fallthrough not in buckets:
        buckets[fallthrough] = []
        specs.append((fallthrough, "More", ()))

    for sid, label, pref in list(specs):
        if sid == fallthrough:
            continue
        items = buckets.get(sid) or []
        if 0 < len(items) < _MIN_CAT:
            buckets[fallthrough].extend(items)
            buckets[sid] = []

    out: list[tuple[str, str, tuple[str, ...], list[dict]]] = []
    for sid, label, pref in specs:
        items = buckets.get(sid) or []
        if not items:
            continue
        # If only one category would remain after filters, still show it
        out.append((sid, label, pref, items))

    # If everything collapsed to one group, rename label to plain list feel
    if len(out) == 1:
        sid, label, pref, items = out[0]
        out = [(sid, "All", pref, items)]
    return out


def _dir_type_details_html(meta: dict, venues: list[dict]) -> str:
    """L1 place type — collapsed; samples + smart categories (not continents)."""
    if not venues:
        return ""
    venues = _sort_venues(venues)
    kind = meta["kind"]
    cats = _bucket_places(kind, venues)
    cat_html = "\n          ".join(
        _dir_cat_details_html(cid, label, items, pref)
        for cid, label, pref, items in cats
    )
    sample_only = _pick_samples(venues, tuple(meta.get("sample_ids") or ()), _DIR_SAMPLE_N)
    sample_ul = (
        f'<ul class="seo-dir-grid seo-dir-samples">\n            '
        + "\n            ".join(_venue_li_html(v) for v in sample_only)
        + "\n          </ul>"
    )
    kind_esc = esc(kind)
    return (
        f'<details class="seo-dir-type" data-place-type="{kind_esc}" id="{esc(meta["id"])}">\n'
        f'          <summary class="seo-dir-type-sum">'
        f'<span class="seo-dir-type-label">{meta["label"]}</span> '
        f'<span class="seo-dir-count">{len(venues)}</span>'
        f'<a class="seo-dir-hub" href="{esc(meta["hub"])}" onclick="event.stopPropagation()">{esc(meta["hub_label"])}</a>'
        f"</summary>\n"
        f'          <div class="seo-dir-type-body">\n'
        f'            <p class="seo-dir-hint">Samples — open a category for more (map above filters by place)</p>\n'
        f"            {sample_ul}\n"
        f'            <div class="seo-dir-regions seo-dir-cats">\n          {cat_html}\n            </div>\n'
        f"          </div>\n"
        f"        </details>"
    )



def load_all_catalog_cards() -> list[dict]:
    """Every FIELD_PACK_CATALOG entry with a name (for cards hub completeness)."""
    script = r"""
const fs = require('fs');
const vm = require('vm');
const ctx = { window: {}, console };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[1], 'utf8'), ctx);
const cat = ctx.window.FIELD_PACK_CATALOG || {};
const venues = ctx.window.FIELD_PACK_VENUES || {};
const home = {};
for (const [vid, v] of Object.entries(venues)) {
  for (const id of new Set([...(v.featuredAnimalIds || []), ...(v.animalIds || [])])) {
    if (!home[id]) home[id] = vid;
  }
}
const out = [];
for (const [id, it] of Object.entries(cat)) {
  if (!it || !it.name) continue;
  if (/^np-/.test(id)) continue;
  if (it.packTemplate === 'park_features') continue;
  if (/^(grsm|yell|zion|yose|grca|romo|acad|glac|arch|olym|npsa)[-_]/.test(id)) continue;
  if (/-(view|overlook|boardwalk|trail|path|summit|falls|waterfall|hoodoo|shore|meadow|grove|sign|vc|shuttle|lodge|basin|rim|creek|pebbles|fins)/.test(id)) continue;
  if (/^(cadillac|sequoia|old-faithful|yosemite-falls|smokies-)/.test(id)) continue;
  if (!home[id]) continue;
  out.push({
    id,
    name: it.name,
    emoji: it.emoji || '',
    photo: String(it.photo || ''),
    blurb: String(it.blurb || it.one_liner || '').slice(0, 160),
    pt: it.packTemplate || (String(id).startsWith('cm-') || String(id).startsWith('sci-') ? 'exhibits' : 'animals'),
    packTemplate: it.packTemplate || (String(id).startsWith('cm-') || String(id).startsWith('sci-') ? 'exhibits' : 'animals'),
    key: it.key && typeof it.key === 'object' ? it.key : {},
    links: it.links && typeof it.links === 'object' ? it.links : {},
    venue: home[id],
  });
}
process.stdout.write(JSON.stringify(out));
"""
    cat_js = FIELD / "js" / "catalog.js"
    raw = subprocess.check_output(["node", "-e", script, str(cat_js)], text=True)
    return json.loads(raw)


def load_print_cards() -> list[dict]:
    """Animals + exhibit cards with a home venue for print/app deep links."""
    script = r"""
const fs = require('fs');
const vm = require('vm');
const ctx = { window: {}, console };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[1], 'utf8'), ctx);
const cat = ctx.window.FIELD_PACK_CATALOG || {};
const venues = ctx.window.FIELD_PACK_VENUES || {};
const byId = {};
for (const [vid, v] of Object.entries(venues)) {
  const pt = v.packTemplate || 'animals';
  for (const id of new Set([...(v.featuredAnimalIds || []), ...(v.animalIds || [])])) {
    if (!byId[id]) byId[id] = { counts: {}, venues: [] };
    byId[id].counts[pt] = (byId[id].counts[pt] || 0) + 1;
    if (byId[id].venues.length < 12) byId[id].venues.push(vid);
  }
}
function pri(c) {
  return Object.entries(c).sort((a, b) => b[1] - a[1])[0][0];
}
const out = [];
for (const [id, rec] of Object.entries(byId)) {
  const it = cat[id];
  if (!it || !it.name) continue;
  const pt = pri(rec.counts);
  if (pt === 'park_features') continue;
  if (pt === 'animals' && /^(cm-|sci-)/.test(id)) continue;
  if (/^(grsm|yell|zion|yose|grca|romo|acad|glac|arch|olym)[-_]/.test(id)) continue;
  if (/^(cadillac|sequoia|old-faithful|yosemite-falls|smokies-)/.test(id)) continue;
  out.push({
    id,
    name: it.name,
    emoji: it.emoji || '',
    photo: String(it.photo || ''),
    blurb: String(it.blurb || it.one_liner || '').slice(0, 160),
    pt,
    venue: rec.venues[0] || '',
  });
}
process.stdout.write(JSON.stringify(out));
"""
    import subprocess

    cat_js = FIELD / "js" / "catalog.js"
    raw = subprocess.check_output(
        ["node", "-e", script, str(cat_js)],
        text=True,
    )
    return json.loads(raw)


def _dir_card_group_html(
    group_id: str,
    label: str,
    items: list[dict],
    preferred_ids: tuple[str, ...] = (),
) -> str:
    if not items:
        return ""
    items = sorted(items, key=lambda x: (x.get("name") or "").lower())
    body = _samples_and_rest_html(
        items,
        li_fn=_item_li_html,
        preferred_ids=preferred_ids,
        list_class="seo-dir-grid seo-dir-card-grid",
        rest_label=f"Show all {len(items)}",
    )
    return (
        f'<details class="seo-dir-card-group" data-card-group="{esc(group_id)}">\n'
        f'            <summary class="seo-dir-region-sum">'
        f'<span class="seo-dir-region-label">{label}</span> '
        f'<span class="seo-dir-count">{len(items)}</span></summary>\n'
        f"            {body}\n"
        f"          </details>"
    )


def _split_creature_cards(cards: list[dict]) -> tuple[list[dict], list[dict]]:
    """Animal-pack cards → wildlife (land) vs sea life (aquarium)."""
    wildlife: list[dict] = []
    sealife: list[dict] = []
    for c in cards:
        if c.get("pt") != "animals":
            continue
        iid = c.get("id") or ""
        if iid in _SEALIFE_GROUP_BY_ID:
            sealife.append(c)
        else:
            wildlife.append(c)
    return wildlife, sealife


def _card_family_html(
    *,
    catalog_id: str,
    pairs_place: str,
    dom_id: str,
    label: str,
    hint: str,
    items: list[dict],
    group_order: tuple,
    group_by_id: dict,
    sample_prefs: tuple[str, ...],
    extra_label: str,
) -> str:
    if not items:
        return ""
    buckets: dict[str, list[dict]] = {gid: [] for gid, _, _ in group_order}
    for c in items:
        gid = group_by_id.get(c["id"], group_order[0][0] if group_order else "other")
        buckets.setdefault(gid, []).append(c)
    groups = [
        _dir_card_group_html(gid, glabel, buckets.get(gid) or [], pref)
        for gid, glabel, pref in group_order
    ]
    mapped = set(group_by_id)
    extra = [c for c in items if c["id"] not in mapped]
    if extra:
        groups.append(_dir_card_group_html(f"more-{catalog_id}", extra_label, extra))
    body = "\n          ".join(g for g in groups if g)
    samples = _pick_samples(
        sorted(items, key=lambda x: (x.get("name") or "").lower()),
        sample_prefs,
        _DIR_SAMPLE_N,
    )
    sample_ul = (
        f'<ul class="seo-dir-grid seo-dir-card-grid seo-dir-samples">\n            '
        + "\n            ".join(_item_li_html(x) for x in samples)
        + "\n          </ul>"
        if samples
        else ""
    )
    return (
        f'<details class="seo-dir-type seo-dir-cards" data-catalog="{esc(catalog_id)}" '
        f'data-pairs-place="{esc(pairs_place)}" id="{esc(dom_id)}">\n'
        f'          <summary class="seo-dir-type-sum">'
        f'<span class="seo-dir-type-label">{label}</span> '
        f'<span class="seo-dir-count">{len(items)}</span></summary>\n'
        f'          <div class="seo-dir-type-body">\n'
        f'            <p class="seo-dir-hint">{hint}</p>\n'
        f"            {sample_ul}\n"
        f'            <div class="seo-dir-regions">\n          {body}\n            </div>\n'
        f"          </div>\n"
        f"        </details>"
    )


def _dir_cards_rail_html(cards: list[dict]) -> str:
    """Wildlife (→zoos), sea life (→aquariums), attractions (→museums)."""
    wildlife, sealife = _split_creature_cards(cards)
    exhibits = [c for c in cards if c.get("pt") == "exhibits"]

    parts = [
        _card_family_html(
            catalog_id="wildlife",
            pairs_place="zoo",
            dom_id="dir-wildlife",
            label="Wildlife",
            hint="Zoo-day Q&amp;A cards — mammals, birds, reptiles",
            items=wildlife,
            group_order=_WILDLIFE_GROUP_ORDER,
            group_by_id=_WILDLIFE_GROUP_BY_ID,
            sample_prefs=("african-lion", "reticulated-giraffe", "giant-panda", "galapagos-tortoise"),
            extra_label="More wildlife",
        ),
        _card_family_html(
            catalog_id="sealife",
            pairs_place="aquarium",
            dom_id="dir-sealife",
            label="Sea life",
            hint="Aquarium-day Q&amp;A cards — sharks, fish, jellies…",
            items=sealife,
            group_order=_SEALIFE_GROUP_ORDER,
            group_by_id=_SEALIFE_GROUP_BY_ID,
            sample_prefs=("shark", "octopus", "jellyfish", "clownfish", "sea-turtle"),
            extra_label="More sea life",
        ),
        _card_family_html(
            catalog_id="attractions",
            pairs_place="museum",
            dom_id="dir-attractions",
            label="Attractions",
            hint="Museum-day cards — rockets, dinos, play zones",
            items=exhibits,
            group_order=_ATTRACTION_GROUP_ORDER,
            group_by_id=_ATTRACTION_GROUP_BY_ID,
            sample_prefs=("sci-rocket", "sci-dinosaur", "cm-makery"),
            extra_label="More attractions",
        ),
    ]
    return "\n        ".join(p for p in parts if p)


def _card_href(card: dict) -> str:
    iid = card.get("id") or ""
    return f"/field-pack/cards/{esc(iid)}/"


def _card_venue_label(card: dict, venues_by_id: dict[str, dict]) -> str:
    vid = card.get("venue") or ""
    v = venues_by_id.get(vid) or {}
    name = v.get("shortName") or v.get("name") or vid.replace("-", " ").title()
    if not name:
        return ""
    return f"· {esc(name)}"


def _featured_cards(cards: list[dict]) -> list[dict]:
    by_id = {c["id"]: c for c in cards}
    out = []
    for cid in FEATURED_CARD_IDS:
        if cid in by_id:
            c = dict(by_id[cid])
            c["featured"] = True
            out.append(c)
    if len(out) < 12:
        for c in cards:
            if c["id"] in {x["id"] for x in out}:
                continue
            out.append(dict(c, featured=True))
            if len(out) >= 12:
                break
    return out[:12]


def _pick_group_cards(cards: list[dict], group: str, n: int = 12) -> list[dict]:
    by_id = {c["id"]: c for c in cards if (c.get("group") or _card_group_key(c)) == group}
    out: list[dict] = []
    seen: set[str] = set()
    for cid in FEATURED_BY_GROUP.get(group) or ():
        if cid in by_id and cid not in seen:
            out.append(by_id[cid])
            seen.add(cid)
        if len(out) >= n:
            return out
    for c in sorted(by_id.values(), key=lambda x: (x.get("name") or "").lower()):
        if c["id"] in seen:
            continue
        out.append(c)
        seen.add(c["id"])
        if len(out) >= n:
            break
    return out


def _landing_teaser_cards(all_cards: list[dict]) -> list[dict]:
    """All-row featured 12 (interleaved so mobile All can show 6 mixed) plus up to 12 per group."""
    featured = _featured_cards(all_cards)
    feat_ids = {c["id"] for c in featured}
    by_id: dict[str, dict] = {}
    for c in featured:
        cc = dict(c)
        cc["featured_all"] = True
        by_id[cc["id"]] = cc
    ordered = [by_id[c["id"]] for c in featured]
    for g in ("wildlife", "sealife", "attractions"):
        for c in _pick_group_cards(all_cards, g, 12):
            if c["id"] in by_id:
                continue
            cc = dict(c)
            cc["featured_all"] = False
            by_id[cc["id"]] = cc
            ordered.append(cc)
    return ordered


def _card_group_key(card: dict) -> str:
    pt = card.get("pt") or "animals"
    if pt == "exhibits":
        return "attractions"
    if card.get("id") in _SEALIFE_GROUP_BY_ID:
        return "sealife"
    if pt == "animals":
        return "wildlife"
    return "wildlife"


def write_cards_hub(venues: list[dict]) -> str:
    """Static crawlable index of every Q&A card → /field-pack/cards/."""
    cards: list[dict] = []
    try:
        cards = load_all_catalog_cards()
    except Exception as e:
        print(f"  WARN: load_all_catalog_cards failed: {e}")
        try:
            cards = load_print_cards()
        except Exception as e2:
            print(f"  WARN: load_print_cards failed for cards hub: {e2}")
            return "/field-pack/cards/"

    venues_by_id = {v["id"]: v for v in venues}
    wildlife, sealife = _split_creature_cards(cards)
    exhibits = [c for c in cards if c.get("pt") == "exhibits"]
    sections = [
        ("wildlife", "Wildlife", wildlife),
        ("sealife", "Sea life", sealife),
        ("attractions", "Attractions", exhibits),
    ]
    total = sum(len(s[2]) for s in sections)

    def section_html(sid: str, label: str, items: list[dict]) -> str:
        if not items:
            return ""
        items = sorted(items, key=lambda x: (x.get("name") or "").lower())
        lis = []
        for c in items:
            blurb = esc((c.get("blurb") or "").strip() or "Printable Q&A card for kids.")
            href = _card_href(c)
            cid = c.get("id") or ""
            photo = (c.get("photo") or "").strip()
            if photo.startswith("photos/"):
                src = "/field-pack/" + photo.split("?")[0]
            elif photo.startswith("/field-pack/"):
                src = photo.split("?")[0]
            elif (FIELD / "photos" / f"{cid}.jpg").is_file():
                src = f"/field-pack/photos/{cid}.jpg"
            else:
                src = ""
            media = (
                f'<img class="cards-hub-thumb" src="{esc(src)}" alt="" width="120" height="90" loading="lazy" decoding="async" />'
                if src
                else f'<span class="cards-hub-emoji" aria-hidden="true">{esc(c.get("emoji") or "🎴")}</span>'
            )
            lis.append(
                f'<li class="cards-hub-item" data-card-id="{esc(cid)}" data-card-group="{esc(sid)}" '
                f'data-card-search="{esc((c.get("name") or "") + " " + (c.get("blurb") or "") + " " + cid)}">'
                f'<a class="cards-hub-link" href="{href}" data-card-id="{esc(cid)}">'
                f"{media}"
                f'<span class="cards-hub-copy">'
                f'<span class="cards-hub-name">{esc(c.get("name") or cid)}</span>'
                f'<span class="cards-hub-teaser">{blurb}</span>'
                f"</span>"
                f"</a></li>"
            )
        return (
            f'<section class="cards-hub-section" id="cards-{esc(sid)}" aria-labelledby="h-{esc(sid)}">\n'
            f'  <h2 id="h-{esc(sid)}">{label} <span class="seo-dir-count">{len(items)}</span></h2>\n'
            f'  <ul class="cards-hub-list">\n    '
            + "\n    ".join(lis)
            + "\n  </ul>\n</section>"
        )

    body_sections = "\n".join(section_html(*s) for s in sections if s[2])
    title = "Animal & Discovery Cards for Kids — Talk, Photos & Q&A · Field Trip Kit"
    desc = (
        "Explore animal, sea-life, and museum cards at home — photos, talk prompts, and Q&A. "
        f"Browse all {total} cards. Print is optional. No account."
    )
    url = f"{SITE}/field-pack/cards/"
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}" />
  <link rel="canonical" href="{esc(url)}" />
  <meta name="robots" content="index,follow" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="1Less" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(desc)}" />
  <meta property="og:url" content="{esc(url)}" />
  <meta property="og:image" content="{OG_SHARE_IMAGE}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:image" content="{OG_SHARE_IMAGE}" />
  <base href="/field-pack/" />
  <link rel="stylesheet" href="/shell/shell.css?v=6" />
  <link rel="stylesheet" href="/field-pack/css/styles.css?v=26" />
  <link rel="stylesheet" href="/field-pack/css/landing.css?v=89" />
  <link rel="stylesheet" href="/field-pack/css/seo-venue.css?v=21" />
  <style>
    .cards-hub {{ max-width: 52rem; margin: 0 auto; padding: 0.75rem 1rem 3rem; }}
    .cards-hub h1 {{ font-size: clamp(1.45rem, 4vw, 2rem); color: #0a4545; margin: 0.5rem 0 0.5rem; }}
    .cards-hub-lead {{ color: #3d4f6f; line-height: 1.45; max-width: 40rem; }}
    .cards-hub-count {{ font-weight: 700; color: #0f5c5c; margin: 0.5rem 0 1.25rem; }}
    .cards-hub-section {{ margin: 1.5rem 0; }}
    .cards-hub-section h2 {{ font-size: 1.15rem; color: #0a4545; margin: 0 0 0.65rem; }}
    .cards-hub-search-label {{ display: block; font-weight: 750; font-size: 0.88rem; margin: 0.75rem 0 0.35rem; color: #0a4545; }}
    .cards-hub-search {{ width: 100%; max-width: 28rem; min-height: 46px; font: inherit; font-size: 1rem; padding: 0.55rem 0.75rem; border-radius: 12px; border: 1.5px solid rgba(15,92,92,0.22); box-sizing: border-box; }}
    .cards-hub-list {{ list-style: none; margin: 0; padding: 0; display: grid; gap: 0.6rem; }}
    @media (min-width: 720px) {{
      .cards-hub-list {{ grid-template-columns: 1fr 1fr; }}
    }}
    .cards-hub-link {{
      display: grid; grid-template-columns: 100px 1fr; gap: 0.7rem; align-items: center;
      padding: 0.5rem; border: 1.5px solid rgba(196,92,38,0.22); border-radius: 14px;
      text-decoration: none; color: inherit; background: #fff; min-height: 88px;
    }}
    .cards-hub-link:hover, .cards-hub-link:focus-visible {{ border-color: #c45c26; outline: 2px solid #c45c26; outline-offset: 2px; }}
    .cards-hub-thumb {{ width: 100px; height: 75px; object-fit: cover; object-position: 50% 18%; border-radius: 10px; background: #f4f1ea; }}
    .cards-hub-emoji {{ font-size: 2.2rem; text-align: center; width: 100px; }}
    .cards-hub-copy {{ display: flex; flex-direction: column; gap: 0.2rem; min-width: 0; }}
    .cards-hub-name {{ font-weight: 800; color: #0a4545; font-size: 0.95rem; }}
    .cards-hub-teaser {{
      color: #3d4f6f; font-size: 0.84rem; line-height: 1.3;
      display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
    }}
    .cards-hub-item[hidden] {{ display: none !important; }}
    .cards-hub-crumbs {{ font-size: 0.9rem; color: #5a6a84; }}
    .cards-hub-crumbs a {{ color: #0f5c5c; }}
  </style>
</head>
<body class="landing-body seo-venue-body">
  <div class="app landing-app">
    <header class="oneless-shell no-print" data-product="bdo">
      <a class="shell-brand" href="/field-pack/" aria-label="Field Trip Kit home">
        <img src="/1LessMark.png" alt="" width="52" height="52" />
      </a>
      <a class="shell-product" href="/field-pack/">
        Field Trip Kit
        <small>{HEADER_TAGLINE}</small>
      </a>
      <div class="shell-more-wrap">
        <button type="button" class="shell-more" aria-expanded="false" aria-haspopup="true" aria-controls="shell-menu">More</button>
        <div id="shell-menu" class="shell-menu" hidden role="menu">
          <a href="/field-pack/" role="menuitem">All places<small>{NAV_PLACES_SUB}</small></a>
          <a href="/field-pack/cards/" aria-current="page" role="menuitem">Animal cards<small>{NAV_CARDS_SUB}</small></a>
          <a href="/field-pack/virtual-field-trip/" role="menuitem">Virtual Field Trip<small>{NAV_VFT_SUB}</small></a>
          <a href="/field-pack/#about" role="menuitem">About<small>{NAV_ABOUT_SUB}</small></a>
        </div>
      </div>
    </header>
    <main class="cards-hub">
      <p class="cards-hub-crumbs"><a href="/field-pack/">Field Trip Kit</a> · Cards</p>
      <h1>Animal &amp; Discovery Cards for Kids</h1>
      <p class="cards-hub-lead">
        Talk prompts, photos, and Q&amp;A for a session at home — wildlife, sea life, and museum attractions.
        Print a card if you want paper. Free. No account.
      </p>
      <p class="cards-hub-count">{total} cards · from Field Trip Kit place lists</p>
      <label class="cards-hub-search-label" for="cards-hub-search">Find a card</label>
      <input type="search" id="cards-hub-search" class="cards-hub-search" placeholder="Lion, shark, dinosaur…" autocomplete="off" />
      <nav class="place-type-tabs place-type-tabs-cards no-print" aria-label="Filter cards">
        <div class="place-type-seg" role="tablist" aria-label="Card type">
          <button type="button" class="place-type-tab is-active" role="tab" data-card-filter="all" aria-selected="true">All</button>
          <button type="button" class="place-type-tab" role="tab" data-card-filter="wildlife" aria-selected="false">Wildlife</button>
          <button type="button" class="place-type-tab" role="tab" data-card-filter="sealife" aria-selected="false">Sea life</button>
          <button type="button" class="place-type-tab" role="tab" data-card-filter="attractions" aria-selected="false">Attractions</button>
        </div>
      </nav>
      {body_sections}
    </main>
  </div>
  <script src="/shell/shell.js?v=5"></script>
  <script src="/field-pack/js/fp-analytics.js?v=1"></script>
  <script>
    (function () {{
      if (typeof FPTrack === "function") FPTrack("cards_hub_visited", {{ source: "cards_hub" }});
      document.querySelectorAll("a.cards-hub-link[data-card-id]").forEach(function (a) {{
        a.addEventListener("click", function () {{
          if (typeof FPTrack === "function") FPTrack("card_opened", {{ card_id: a.getAttribute("data-card-id") || "", source: "cards_hub" }});
        }});
      }});
      var q = document.getElementById("cards-hub-search");
      var tabs = document.querySelectorAll(".place-type-tab[data-card-filter]");
      var filter = "all";
      function applyHubFilter() {{
        var n = q ? (q.value || "").trim().toLowerCase() : "";
        var searching = n.length >= 2;
        document.querySelectorAll(".cards-hub-section").forEach(function (sec) {{
          var gid = (sec.id || "").replace("cards-", "");
          sec.hidden = !searching && filter !== "all" && gid !== filter;
        }});
        document.querySelectorAll(".cards-hub-item").forEach(function (li) {{
          var blob = (li.getAttribute("data-card-search") || li.textContent || "").toLowerCase();
          var g = li.getAttribute("data-card-group") || "";
          var missSearch = searching && blob.indexOf(n) === -1;
          var missFilter = !searching && filter !== "all" && g !== filter;
          li.hidden = missSearch || missFilter;
        }});
      }}
      tabs.forEach(function (btn) {{
        btn.addEventListener("click", function () {{
          filter = btn.getAttribute("data-card-filter") || "all";
          tabs.forEach(function (b) {{
            var on = b === btn;
            b.classList.toggle("is-active", on);
            b.setAttribute("aria-selected", on ? "true" : "false");
          }});
          applyHubFilter();
        }});
      }});
      if (q) q.addEventListener("input", applyHubFilter);
    }})();
  </script>
</body>
</html>
"""
    out_dir = FIELD / "cards"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(html, encoding="utf-8")
    extra = write_card_pages(cards, venues_by_id)
    print(f"  cards hub → /field-pack/cards/ ({total} cards) + {len(extra)} card pages")
    return ["/field-pack/cards/"] + extra



def write_card_pages(cards: list[dict], venues_by_id: dict[str, dict]) -> list[str]:
    """Static /field-pack/cards/<id>/ pages — catalog 6-Q + real extras + VFT cam/film."""
    urls: list[str] = []
    for c in cards:
        cid = (c.get("id") or "").strip()
        if not cid or "/" in cid or ".." in cid:
            continue
        item = enrich_item(c)
        vid = c.get("venue") or ""
        real_qa = venue_real_qa_for_card(cid, vid)
        if real_qa:
            item["qa_card"] = real_qa
        name = item.get("name") or cid
        emoji = item.get("emoji") or "🎴"
        blurb = (item.get("blurb") or "").strip()
        v = venues_by_id.get(vid) or {}
        vname = v.get("shortName") or v.get("name") or ""
        venue_line = f" · {esc(vname)}" if vname else ""
        venue_href = f"/field-pack/{esc(vid)}/#at-home" if vid else "/field-pack/"
        photo = ""
        if (FIELD / "photos" / f"{cid}.jpg").is_file():
            photo = f"/field-pack/photos/{cid}.jpg?v=img2"
        elif (item.get("photo") or "").startswith("photos/"):
            photo = "/field-pack/" + str(item["photo"]).split("?")[0]
        img_html = (
            f'<img class="card-page-photo" src="{esc(photo)}" alt="" width="640" height="400" decoding="async" />'
            if photo
            else f'<p class="card-page-emoji" aria-hidden="true">{esc(emoji)}</p>'
        )
        talk_html = outing_talk_html(item)
        more_links = catalog_more_links_html(item)
        watch_html = watch_links_html(item)
        title = f"{name} for Kids — Talk, Photos & Q&A · Field Trip Kit"
        desc = (
            f"Explore the {name} card at home: photo, six talk questions, and Q&A. "
            + (blurb + " " if blurb else "")
            + "Print is optional. No account."
        )
        url = f"{SITE}/field-pack/cards/{cid}/"
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}" />
  <link rel="canonical" href="{esc(url)}" />
  <meta name="robots" content="index,follow" />
  <meta property="og:type" content="article" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(desc)}" />
  <meta property="og:url" content="{esc(url)}" />
  <meta property="og:image" content="{OG_SHARE_IMAGE}" />
  <link rel="stylesheet" href="/shell/shell.css?v=6" />
  <link rel="stylesheet" href="/field-pack/css/styles.css?v={STYLES_CSS_VER}" />
  <link rel="stylesheet" href="/field-pack/css/landing.css?v={LANDING_CSS_VER}" />
  <link rel="stylesheet" href="/field-pack/css/seo-venue.css?v={SEO_CSS_VER}" />
  <style>
    .card-page {{ max-width: 28rem; margin: 0 auto; padding: 1rem 1rem 3rem; }}
    .card-page h1 {{ font-size: clamp(1.35rem, 4vw, 1.75rem); color: #0a4545; margin: 0.4rem 0; }}
    .card-page-venue a {{ color: #0f5c5c; font-weight: 750; }}
    .card-page-photo {{ width: 100%; height: auto; border-radius: 14px; border: 1.5px solid rgba(15,92,92,.14); }}
    .card-page-emoji {{ font-size: 3rem; margin: 0.5rem 0; }}
    .card-page-blurb {{ color: #3d4f6f; line-height: 1.45; }}
    .card-page-actions {{ display: flex; flex-wrap: wrap; gap: 0.6rem; margin-top: 1rem; }}
    .card-page-crumbs {{ font-size: 0.9rem; color: #5a6a84; }}
    .card-page-crumbs a {{ color: #0f5c5c; }}
  </style>
</head>
<body class="landing-body">
  <div class="app">
    <header class="oneless-shell no-print" data-product="bdo">
      <a class="shell-brand" href="/field-pack/" aria-label="Field Trip Kit home">
        <img src="/1LessMark.png" alt="" width="52" height="52" />
      </a>
      <a class="shell-product" href="/field-pack/">Field Trip Kit <small>{HEADER_TAGLINE}</small></a>
    </header>
    <main class="card-page">
      <p class="card-page-crumbs"><a href="/field-pack/">Field Trip Kit</a> · <a href="/field-pack/cards/">Cards</a></p>
      <h1>{esc(emoji)} {esc(name)}</h1>
      <p class="card-page-venue">At-home card{venue_line}
        {f'· <a href="{venue_href}">Place page</a>' if vid else ""}</p>
      {img_html}
      <p class="card-page-blurb">{esc(blurb) if blurb else "Talk this card through at home — print only if you want paper."}</p>
      {more_links}
      {watch_html}
      {talk_html}
      <p class="card-page-actions">
        <a class="btn btn-secondary" href="{venue_href}">{esc(CTA_ZOO_CARDS) if vid else esc(CTA_EXPLORE_HOME)}</a>
        <button type="button" class="btn btn-secondary" id="print-this-card" data-card-id="{esc(cid)}" data-venue="{esc(vid)}">{esc(CTA_PRINT_CARD)}</button>
      </p>
    </main>
  </div>
  <div id="print-sheet" class="print-sheet" aria-hidden="true"></div>
  <div id="treasure-sheet" class="print-sheet treasure-sheet" aria-hidden="true"></div>
  <script src="/shell/shell.js?v=5"></script>
  <script src="/field-pack/js/fp-analytics.js?v=1"></script>
  <script src="/field-pack/js/catalog.js?v=34"></script>
  <script src="/field-pack/js/print-kit.js?v=13"></script>
  <script>
    (function () {{
      if (typeof FPTrack === "function") FPTrack("card_page_viewed", {{ card_id: "{esc(cid)}" }});
      var btn = document.getElementById("print-this-card");
      if (btn) btn.addEventListener("click", function () {{
        var id = btn.getAttribute("data-card-id") || "";
        var vid = btn.getAttribute("data-venue") || "";
        if (typeof FPTrack === "function") FPTrack("card_opened", {{ card_id: id, source: "card_page_print" }});
        if (window.FPPrint && FPPrint.printQaForItem) FPPrint.printQaForItem(id, vid || null);
      }});
      document.querySelectorAll(".card-talk-pack .choice").forEach(function (choice) {{
        choice.addEventListener("click", function () {{
          var group = choice.parentElement;
          var multi = group && group.getAttribute("data-multi") === "1";
          var on = choice.getAttribute("aria-pressed") === "true";
          if (!multi && group) {{
            group.querySelectorAll(".choice").forEach(function (b) {{
              b.setAttribute("aria-pressed", "false");
            }});
          }}
          choice.setAttribute("aria-pressed", on && multi ? "false" : (on ? "false" : "true"));
        }});
      }});
    }})();
  </script>
</body>
</html>
"""
        dest = FIELD / "cards" / cid
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "index.html").write_text(html, encoding="utf-8")
        urls.append(f"/field-pack/cards/{cid}/")
    return urls


def patch_landing_directory(venues: list[dict]) -> None:
    """T5: cards showcase + compact places (no full dual-rail lists on landing)."""
    index = FIELD / "index.html"
    html = index.read_text(encoding="utf-8")
    venues_by_id = {v["id"]: v for v in venues}

    by_type: dict[str, list[dict]] = {m["kind"]: [] for m in _TYPE_DIR_META}
    for v in venues:
        kind = venue_type_kind(v)
        if kind in by_type:
            by_type[kind].append(v)

    cards: list[dict] = []
    try:
        cards = load_print_cards()
    except Exception as e:
        print(f"  WARN: load_print_cards failed: {e}")
    all_cards: list[dict] = []
    try:
        all_cards = load_all_catalog_cards()
    except Exception:
        all_cards = cards

    for c in cards:
        c.setdefault("blurb", "")
        c["group"] = _card_group_key(c)
    for c in all_cards:
        c.setdefault("blurb", "")
        c["group"] = _card_group_key(c)

    pool = all_cards if all_cards else cards
    featured = _landing_teaser_cards(pool)
    n_cards = len(all_cards) if all_cards else len(cards)

    tile_lis = []
    for c in featured:
        g = c.get("group") or "wildlife"
        cid = c.get("id") or ""
        src = ""
        if (FIELD / "photos" / f"{cid}.jpg").is_file():
            src = f"/field-pack/photos/{cid}.jpg?v=img2"
        elif (c.get("photo") or "").startswith("photos/"):
            src = "/field-pack/" + str(c["photo"]).split("?")[0]
        if src:
            media = (
                f'<span class="cat-card-media">'
                f'<img class="cat-card-thumb" src="{esc(src)}" alt="" width="320" height="240" loading="lazy" decoding="async" />'
                f"</span>"
            )
        else:
            media = (
                f'<span class="cat-card-media cat-card-media-emoji">'
                f'<span class="cat-card-emoji" aria-hidden="true">{esc(c.get("emoji") or "🎴")}</span>'
                f"</span>"
            )
        tile_lis.append(
            f'<li class="cat-card-tile" data-card-group="{esc(g)}" data-card-id="{esc(cid)}"'
            f'{" data-featured-all=\"1\"" if c.get("featured_all") else " hidden"}>'
            f'<a class="cat-card-tile-link" href="{_card_href(c)}" data-card-id="{esc(cid)}">'
            f"{media}"
            f'<span class="cat-card-name">{esc(c.get("name") or cid)}</span>'
            f"</a></li>"
        )
    tiles_ul = (
        '<ul class="cat-card-grid" id="cat-card-grid">\n            '
        + "\n            ".join(tile_lis)
        + "\n          </ul>"
    )

    hub_meta = [
        ("zoo", "Zoos & safaris", "🦁", "/field-pack/zoos/"),
        ("aquarium", "Aquariums", "🦈", "/field-pack/aquariums/"),
        ("museum", "Museums & science", "🦕", "/field-pack/museums/"),
        ("park", "National parks", "🏞️", "/field-pack/national-parks/"),
    ]
    hub_cards = []
    for kind, label, emoji, href in hub_meta:
        n = len(by_type.get(kind) or [])
        hub_cards.append(
            f'<a class="cat-place-hub" href="{href}" data-place-kind="{esc(kind)}">'
            f'<span class="cat-place-emoji" aria-hidden="true">{emoji}</span>'
            f'<span class="cat-place-label">{esc(label)}</span>'
            f'<span class="cat-place-count">{n}</span>'
            f"</a>"
        )
    hubs_html = (
        '<div class="cat-place-hubs" id="cat-place-hubs">\n          '
        + "\n          ".join(hub_cards)
        + "\n        </div>"
    )

    pop_chips = []
    for pid in POPULAR_VENUE_IDS:
        v = venues_by_id.get(pid)
        if not v:
            continue
        name = v.get("shortName") or v.get("name") or pid
        emoji = v.get("emoji") or "📍"
        pop_chips.append(
            f'<a class="cat-popular-chip" href="/field-pack/{esc(pid)}/" data-venue-slug="{esc(pid)}">'
            f"{esc(emoji)} {esc(name)}</a>"
        )
    popular_html = (
        '<div class="cat-popular" id="cat-popular">'
        '<p class="cat-popular-label">Popular places</p>'
        '<div class="cat-popular-chips">'
        + "".join(pop_chips)
        + "</div></div>"
    )

    n_places = len(venues)

    places_inner = (
        f'<div class="cat-places-compact" id="cat-places-compact">\n'
        f"            {hubs_html}\n"
        f"            {popular_html}\n"
        f"          </div>"
    )
    cards_inner = (
        f'<div class="cat-cards-showcase" id="cat-cards-showcase">\n'
        f'            <nav class="place-type-tabs place-type-tabs-cards no-print" aria-label="Filter cards">\n'
        f'              <div class="place-type-seg" role="tablist" aria-label="Card type">\n'
        f'                <button type="button" class="place-type-tab is-active" role="tab" data-card-filter="all" aria-selected="true">All</button>\n'
        f'                <button type="button" class="place-type-tab" role="tab" data-card-filter="wildlife" aria-selected="false">Wildlife</button>\n'
        f'                <button type="button" class="place-type-tab" role="tab" data-card-filter="sealife" aria-selected="false">Sea life</button>\n'
        f'                <button type="button" class="place-type-tab" role="tab" data-card-filter="attractions" aria-selected="false">Attractions</button>\n'
        f"              </div>\n"
        f"            </nav>\n"
        f"            {tiles_ul}\n"
        f'            <p class="cat-cards-all"><a href="/field-pack/cards/" id="cat-all-cards-link">All {n_cards} cards →</a></p>\n'
        f"          </div>"
    )
    cards_block = (
        f'<div id="seo-venue-directory" class="seo-dir-body seo-dir-body-compact seo-dir-cards-only" '
        f'data-place-count-build="{n_places}" data-card-count-build="{n_cards}">\n'
        f"          {cards_inner}\n"
        f"        </div>"
    )

    places_pat = re.compile(
        r"(<!-- SEO:PLACES-BODY:START -->)([\s\S]*?)(<!-- SEO:PLACES-BODY:END -->)",
        re.M,
    )
    cards_pat = re.compile(
        r"(<!-- SEO:CARDS-BODY:START -->)([\s\S]*?)(<!-- SEO:CARDS-BODY:END -->)",
        re.M,
    )
    dir_pat = re.compile(
        r"(<!-- SEO:DIR-BODY:START -->)([\s\S]*?)(<!-- SEO:DIR-BODY:END -->)",
        re.M,
    )

    if places_pat.search(html):
        html = places_pat.sub(rf"\1\n          {places_inner}\n          \3", html)
    if cards_pat.search(html):
        html = cards_pat.sub(rf"\1\n        {cards_block}\n        \3", html)
    elif dir_pat.search(html):
        # legacy single block
        legacy = (
            f'<div id="seo-venue-directory" class="seo-dir-body seo-dir-body-compact" '
            f'data-place-count-build="{n_places}" data-card-count-build="{n_cards}">\n'
            f"          {cards_inner}\n"
            f"          {places_inner}\n"
            f"        </div>"
        )
        html = dir_pat.sub(rf"\1\n        {legacy}\n        \3", html)
    else:
        print("  WARN: landing directory marker not found")
        return

    html = re.sub(
        r'(<section class="seo-directory"[^>]*>\s*)<h2 id="dir-heading">[^<]*</h2>\s*<p id="dir-blurb">[\s\S]*?</p>',
        r"\1",
        html,
        count=1,
    )

    html = re.sub(
        r"<span data-place-count>\d+</span>",
        f"<span data-place-count>{n_places}</span>",
        html,
        count=1,
    )

    if 'href="/field-pack/cards/"' not in html:
        html = html.replace(
            f'<a href="/field-pack/" aria-current="page" role="menuitem">All places<small>{NAV_PLACES_SUB}</small></a>\n            <a href="/field-pack/#about"',
            f'<a href="/field-pack/" aria-current="page" role="menuitem">All places<small>{NAV_PLACES_SUB}</small></a>\n            <a href="/field-pack/cards/" role="menuitem">Animal cards<small>{NAV_CARDS_SUB}</small></a>\n            <a href="/field-pack/#about"',
            1,
        )

    index.write_text(html, encoding="utf-8")
    counts = {m["kind"]: len(by_type[m["kind"]]) for m in _TYPE_DIR_META}
    print(
        f"  patched landing compact catalog places={counts} "
        f"featured_cards={len(featured)} total_cards={n_cards} popular={len(pop_chips)}"
    )


def patch_places_data_hrefs(venues: list[dict]) -> None:
    """Point places-data href to indexable /field-pack/<id>/ URLs."""
    path = PLACES_JS
    text = path.read_text(encoding="utf-8")
    for v in venues:
        # href: "places/dallas-zoo.html" → href: "/field-pack/dallas-zoo/"
        text = re.sub(
            rf'(id:\s*"{re.escape(v["id"])}"[\s\S]*?href:\s*)"(?:places/)?{re.escape(v["id"])}\.html"',
            rf'\1"/field-pack/{v["id"]}/"',
            text,
            count=1,
        )
    path.write_text(text, encoding="utf-8")
    print("  patched places-data.js hrefs → /field-pack/<id>/")


def main() -> int:
    print("Loading venues…")
    venues = load_venues()
    venues.sort(key=lambda v: (v.get("state") or "", v.get("city") or "", v["name"]))
    print(f"  {len(venues)} venues")

    css_path = FIELD / "css" / "seo-venue.css"
    # Prefer hand-maintained css (visual-first enhancements); seed once if missing
    if not css_path.is_file() or css_path.stat().st_size < 500:
        css_path.write_text(SEO_CSS, encoding="utf-8")
        print(f"  seeded {css_path.relative_to(REPO)}")
    else:
        print(f"  kept {css_path.relative_to(REPO)} (not overwritten)")

    # Validate mission venue data when present
    try:
        from validate_venue_data import main as validate_main
        import sys as _sys
        _rc = validate_main()
        if _rc != 0:
            print("  WARN: venue data validation reported issues")
    except Exception as ex:
        print(f"  WARN: validator skip ({ex})")

    urls = []
    for v in venues:
        out_dir = FIELD / v["id"]
        out_dir.mkdir(parents=True, exist_ok=True)
        mission_v = load_mission_venue(v["id"])
        if mission_v:
            try:
                html = render_mission_venue_page(v, mission_v)
                print(f"  mission page {v['id']}")
            except Exception as ex:
                print(f"  WARN mission page failed {v['id']}: {ex}; using legacy")
                html = render_venue_page(v)
        else:
            html = render_venue_page(v)
        (out_dir / "index.html").write_text(html, encoding="utf-8")
        urls.append(f"/field-pack/{v['id']}/")
        text = re.sub(r"<[^>]+>", " ", html)
        words = len(re.findall(r"\w+", text))
        if words < 120:
            print(f"  WARN thin page {v['id']}: ~{words} words")

    patch_landing_directory(venues)
    patch_places_data_hrefs(venues)
    type_urls = write_type_landings(venues)
    cards_urls = write_cards_hub(venues)
    if isinstance(cards_urls, str):
        cards_urls = [cards_urls]
    write_sitemap(venues, extra_urls=type_urls + cards_urls + ["/field-pack/virtual-zoo/", "/field-pack/virtual-field-trip/"])
    write_robots()
    manifest = {
        "generated": TODAY,
        "count": len(urls),
        "urls": [f"{SITE}{u}" for u in urls],
        "type_landings": [f"{SITE}{u}" for u in type_urls],
        "landing": f"{SITE}/field-pack/",
    }
    (FIELD / "seo-venues.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    # human-readable URL list for Search Console
    (FIELD / "SEO_URLS.txt").write_text(
        "\n".join([manifest["landing"]] + manifest["type_landings"] + manifest["urls"]) + "\n",
        encoding="utf-8",
    )
    print(f"  wrote {len(urls)} venue pages")
    print(f"  wrote {len(type_urls)} type landings")
    print(f"  sitemap → static/sitemap.xml")
    print(f"  robots  → static/robots.txt")
    print(f"  URL list → static/field-pack/SEO_URLS.txt")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as e:
        print(e.stderr or e.stdout, file=sys.stderr)
        raise SystemExit(1)
