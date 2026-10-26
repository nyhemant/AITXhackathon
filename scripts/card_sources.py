"""Citable-card pilot (2026-10-26): a small "Sources & credits" box on a few cards.

Rules (reviewer consensus, Oct 26 2026):
- Only facts we actually spot-checked get a "Spot-checked" line, each tied to
  that one fact and its source. Nothing implies the whole card was reviewed.
- Photo credits come from the Wikimedia Commons API (extmetadata Artist /
  LicenseShortName / LicenseUrl), traced to the exact file page. A card whose
  hero photo cannot be traced to an author AND a licence is NOT in the pilot
  (no credit guesses). Panda, lion and bison were dropped for that reason.
- The box is loaded only on pilot cards (card-sources.css / card-sources.js).
"""

from __future__ import annotations

from html import escape as _esc

CARD_SOURCES_CSS_VER = "3"
CARD_SOURCES_JS_VER = "2"
CHECKED_MONTH = "Oct 2026"
CITE_ACCESSED_DEFAULT = "October 26, 2026"

PILOT: dict[str, dict] = {
    "whale-shark": {
        "name": "Whale shark",
        "wiki_title": "Whale shark",
        "wiki_url": "https://en.wikipedia.org/wiki/Whale_shark",
        "checks": [
            {
                "fact": "the whale shark is the largest living fish, and a filter feeder",
                "source": "U.S. Bureau of Ocean Energy Management",
                "key": "boem",
                "url": "https://www.boem.gov/newsroom/ocean-science-news/whale-shark-whale-fish",
            },
            {
                "fact": "each whale shark’s spot pattern is unique",
                "source": "NOAA Fisheries",
                "key": "noaa",
                "url": "https://www.fisheries.noaa.gov/feature-story/12-shark-facts-may-surprise-you",
            },
        ],
        "photo": {
            "author": "Arturo de Frias Marques",
            "license": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "file_page": "https://commons.wikimedia.org/wiki/File:Whale_Shark_1_AdF.jpg",
            "changes": "resized",
        },
    },
    "african-elephant": {
        "name": "African elephant",
        "wiki_title": "African elephant",
        "wiki_url": "https://en.wikipedia.org/wiki/African_elephant",
        "checks": [
            {
                "fact": "an elephant pregnancy lasts about 22 months",
                "source": "Smithsonian Magazine",
                "key": "smithsonian",
                "url": "https://www.smithsonianmag.com/science-nature/14-fun-facts-about-elephants-14572816/",
            },
        ],
        "photo": {
            "author": "Bernard DUPONT",
            "license": "CC BY-SA 2.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/2.0/",
            "file_page": "https://commons.wikimedia.org/wiki/File:African_Elephant_(Loxodonta_africana)_male_(17289351322).jpg",
            "changes": "cropped and colour-adjusted",
        },
    },
    "manta-ray": {
        "name": "Manta ray",
        "wiki_title": "Manta ray",
        "wiki_url": "https://en.wikipedia.org/wiki/Manta_ray",
        "checks": [
            {
                "fact": "a third manta species, the Atlantic manta (Mobula yarae), was described in 2025",
                "source": "Marine Megafauna Foundation",
                "key": "mmf",
                "url": "https://marinemegafauna.org/news/third-manta-ray-species-mobula-yarae-discovered-in-atlantic-ocean",
            },
        ],
        "photo": {
            "author": "Arturo de Frias Marques",
            "license": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "file_page": "https://commons.wikimedia.org/wiki/File:Giant_Manta_AdF.jpg",
            "changes": "resized",
        },
    },
}


def photo_credit_ok(photo: dict | None) -> bool:
    """A credit is shown only with an author, an exact licence and the Commons file page."""
    if not photo:
        return False
    return all(str(photo.get(k) or "").strip() for k in ("author", "license", "license_url", "file_page")) and str(
        photo.get("file_page")
    ).startswith("https://commons.wikimedia.org/wiki/File:")


def cite_text(cid: str, accessed: str = CITE_ACCESSED_DEFAULT) -> str:
    name = PILOT[cid]["name"]
    return f'KidZooKit. "{name} study card." kidzookit.com/field-pack/cards/{cid}/. Accessed {accessed}.'


def is_pilot(cid: str) -> bool:
    return cid in PILOT and photo_credit_ok(PILOT[cid].get("photo"))


def head_link(cid: str) -> str:
    if not is_pilot(cid):
        return ""
    return f'\n  <link rel="stylesheet" href="/field-pack/css/card-sources.css?v={CARD_SOURCES_CSS_VER}" />'


def script_tag(cid: str) -> str:
    if not is_pilot(cid):
        return ""
    return f'  <script src="/field-pack/js/card-sources.js?v={CARD_SOURCES_JS_VER}"></script>\n'


def _a(href: str, text: str, cid: str, key: str) -> str:
    return (
        f'<a href="{_esc(href)}" target="_blank" rel="noopener" data-cite-source="{_esc(key)}" '
        f'data-cite-card="{_esc(cid)}">{_esc(text)}</a>'
    )


def render_html(cid: str) -> str:
    if not is_pilot(cid):
        return ""
    c = PILOT[cid]
    n = len(c["checks"])
    facts_word = "fact" if n == 1 else "facts"
    checks = "".join(
        f'<li>Spot-checked: {_esc(ch["fact"])} — {_a(ch["url"], ch["source"], cid, ch["key"])}</li>'
        for ch in c["checks"]
    )
    p = c["photo"]
    accessed_default = CITE_ACCESSED_DEFAULT
    cite = cite_text(cid, f"\x00")
    pre, post = cite.split("\x00")
    return (
        f'<section class="card-sources" id="sources" aria-labelledby="card-sources-h" data-card="{_esc(cid)}">'
        f'<h2 id="card-sources-h" class="card-sources-h">Sources &amp; credits</h2>'
        f'<p class="card-sources-lead">Facts drawn from Wikipedia’s {_a(c["wiki_url"], c["wiki_title"], cid, "wikipedia")} article; '
        f"{n} {facts_word} spot-checked against another source in {CHECKED_MONTH}. Other facts were not separately checked.</p>"
        f'<ul class="card-sources-checks">{checks}</ul>'
        f'<p class="card-sources-photo">Photo: {_esc(p["author"])}, '
        f'{_a(p["license_url"], p["license"], cid, "licence")}, via '
        f'{_a(p["file_page"], "Wikimedia Commons", cid, "commons")} ({_esc(p["changes"])} for this page).</p>'
        f'<div class="card-cite"><p class="card-cite-h">How to cite this card</p>'
        f'<p class="card-cite-text" data-cite-text>{_esc(pre)}<span data-cite-date>{_esc(accessed_default)}</span>{_esc(post)}</p>'
        f'<button type="button" class="btn btn-secondary card-cite-copy" data-cite-copy hidden>Copy citation</button>'
        f'<p class="card-cite-status" role="status" aria-live="polite"></p></div>'
        f"</section>"
    )
