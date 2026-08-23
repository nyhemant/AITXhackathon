"""Card kind for Field Trip Kit hub / featured / lint.

Source-of-truth enum: animal | sea_life | attraction | place_feature.
Hub sections are derived from kind — do not hardcode Wildlife/Parks id lists.

This module does not migrate catalog.js. It reads optional `kind` and
`venue_attribution`, then derives the rest from existing fields.
"""

from __future__ import annotations

CARD_KINDS = ("animal", "sea_life", "attraction", "place_feature")

# Hub chrome derived from kind. Order is display order.
HUB_SECTIONS = (
    ("wildlife", "Wildlife", "animal"),
    ("sealife", "Sea life", "sea_life"),
    ("attractions", "Attractions", "attraction"),
    ("parks", "Parks & trails", "place_feature"),
)

# Kind fallback until catalog cards carry `kind`. Not a hub membership list.
SEA_LIFE_IDS = frozenset(
    {
        "clownfish",
        "eel",
        "freshwater-fish",
        "seahorse",
        "shark",
        "stingray",
        "sea-turtle",
        "crab",
        "jellyfish",
        "octopus",
        "starfish",
    }
)

_ILLUSTRATION_MARKERS = (
    "illustration",
    "imagine",
    "ai generated",
    "ai-generated",
    "ai image",
)


def _norm_type(raw: str) -> str:
    return (raw or "").lower().replace("-", "_").replace(" ", "_")


def venue_type_is_park(vtype: str) -> bool:
    t = _norm_type(vtype)
    if "park" in t:
        return True
    return t in {"trail", "trails", "nature_preserve"}


def card_kind(card: dict | None) -> str:
    """Return a CARD_KINDS value. Explicit `kind` wins; never id-special-case Towpath."""
    card = card or {}
    explicit = card.get("kind")
    if explicit in CARD_KINDS:
        return explicit
    cid = str(card.get("id") or "")
    pt = str(card.get("packTemplate") or card.get("pt") or "").strip()
    if pt == "exhibits" or cid.startswith("cm-") or cid.startswith("sci-"):
        return "attraction"
    if pt == "park_features":
        return "place_feature"
    if cid in SEA_LIFE_IDS:
        return "sea_life"
    if venue_type_is_park(str(card.get("venue_type") or card.get("home_venue_type") or "")):
        return "place_feature"
    if pt == "animals":
        return "animal"
    return "animal"


def hub_section_id(kind: str) -> str:
    for sid, _label, k in HUB_SECTIONS:
        if k == kind:
            return sid
    return "wildlife"


def hub_section_label(section_id: str) -> str:
    for sid, label, _k in HUB_SECTIONS:
        if sid == section_id:
            return label
    return section_id


def group_cards_by_hub_section(cards: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {sid: [] for sid, _label, _k in HUB_SECTIONS}
    for card in cards:
        sid = hub_section_id(card_kind(card))
        out.setdefault(sid, []).append(card)
    return out


def card_photo_is_illustration(card: dict | None) -> bool:
    credit = str((card or {}).get("photoCredit") or (card or {}).get("photo_credit") or "").lower()
    return any(m in credit for m in _ILLUSTRATION_MARKERS)


def card_is_todo_or_unsourced(card: dict | None) -> bool:
    card = card or {}
    status = str(card.get("status") or "").lower()
    if status in {"todo", "unsourced", "draft"}:
        return True
    return card_photo_is_illustration(card)


def card_may_feature(card: dict | None) -> bool:
    """todo/unsourced/illustration cards may sit on the hub but must not be featured."""
    return not card_is_todo_or_unsourced(card)


def attraction_venue_attribution(
    card: dict | None,
    venues_by_id: dict | None = None,
) -> dict | None:
    """Require {venue_slug, venue_name} for kind=attraction. Derive name if only slug exists."""
    card = card or {}
    if card_kind(card) != "attraction":
        return None
    raw = card.get("venue_attribution") or {}
    slug = ""
    name = ""
    if isinstance(raw, dict):
        slug = str(raw.get("venue_slug") or "").strip()
        name = str(raw.get("venue_name") or "").strip()
    if not slug:
        slug = str(card.get("venue") or "").strip()
    if not name and slug and venues_by_id:
        v = venues_by_id.get(slug) or {}
        name = str(v.get("shortName") or v.get("name") or "").strip()
    if not slug or not name:
        return None
    return {"venue_slug": slug, "venue_name": name}


def catalog_has_venue_attribution(card: dict | None) -> bool:
    raw = (card or {}).get("venue_attribution") or {}
    if not isinstance(raw, dict):
        return False
    return bool(str(raw.get("venue_slug") or "").strip() and str(raw.get("venue_name") or "").strip())


def card_shows_venue_attribution(card: dict | None) -> bool:
    """Animal and sea-life cards are shared across zoos/aquariums — no home-venue chrome.

    Attractions and place_feature cards may still name their venue.
    """
    return card_kind(card) not in {"animal", "sea_life"}
