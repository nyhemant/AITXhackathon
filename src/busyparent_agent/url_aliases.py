"""Canonical Field Trip Kit URL aliases — one table for HTTP 301s and static stubs.

Short animal slugs match the in-app soft-alias list in ``app.js``
(``lookupPromptBank``). Do not invent animals here.
"""

from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

FIELD_PACK_PREFIX = "/field-pack"
VFT_PATH = "/field-pack/virtual-field-trip/"
PRINT_PATH = "/field-pack/print/"
PRINT_TARGET = "/field-pack/virtual-field-trip/?print=1"
PLACES_PATH = "/field-pack/"
NATIONAL_PARKS_PATH = "/field-pack/national-parks/"

# Short typed card slugs → canonical card ids (app.js soft aliases).
CARD_SLUG_ALIASES: dict[str, str] = {
    "elephant": "african-elephant",
    "giraffe": "reticulated-giraffe",
    "lion": "african-lion",
    "gorilla": "western-lowland-gorilla",
    "hippo": "nile-hippo",
    "penguin": "african-penguin",
    "flamingo": "caribbean-flamingo",
    "tortoise": "galapagos-tortoise",
    "otter": "asian-small-clawed-otter",
    "lemur": "ring-tailed-lemur",
    "sloth": "two-toed-sloth",
    "sea-star": "starfish",
    "jelly": "jellyfish",
    "panda": "giant-panda",
}


def card_alias_redirects() -> dict[str, str]:
    """``/field-pack/cards/{short}[/]`` → canonical card page."""
    out: dict[str, str] = {}
    for src, dest in CARD_SLUG_ALIASES.items():
        dest_url = f"{FIELD_PACK_PREFIX}/cards/{dest}/"
        out[f"{FIELD_PACK_PREFIX}/cards/{src}"] = dest_url
        out[f"{FIELD_PACK_PREFIX}/cards/{src}/"] = dest_url
    return out


# Exact path → Location (query appended by ``redirect_location``).
# Print is a named path so Start / About extras never dump into a bare VFT.
PATH_REDIRECTS: dict[str, str] = {
    f"{FIELD_PACK_PREFIX}/virtual-zoo": VFT_PATH,
    f"{FIELD_PACK_PREFIX}/virtual-zoo/": VFT_PATH,
    f"{FIELD_PACK_PREFIX}/parks": NATIONAL_PARKS_PATH,
    f"{FIELD_PACK_PREFIX}/parks/": NATIONAL_PARKS_PATH,
    f"{FIELD_PACK_PREFIX}/app.html": PLACES_PATH,
    f"{FIELD_PACK_PREFIX}/print": PRINT_TARGET,
    f"{FIELD_PACK_PREFIX}/print/": PRINT_TARGET,
}


def _merge_query(dest: str, query: str) -> str:
    """Append or merge ``query`` onto ``dest``, dest keys win on collision."""
    if not query:
        return dest
    parts = urlsplit(dest)
    incoming = dict(parse_qsl(query, keep_blank_values=True))
    existing = dict(parse_qsl(parts.query, keep_blank_values=True))
    incoming.update(existing)
    merged = urlencode(incoming)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, merged, parts.fragment))


def redirect_location(path: str, query: str = "") -> str | None:
    """Return a 301 Location for ``path`` (+ query), or None."""
    dest = PATH_REDIRECTS.get(path) or card_alias_redirects().get(path)
    if not dest:
        return None
    return _merge_query(dest, query)


# Built once for tests / web.py that want a flat dict.
CARD_ALIAS_REDIRECTS = card_alias_redirects()
