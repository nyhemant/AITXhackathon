"""Sourced animal ↔ national-park suggestion rails (Yellowstone PoC).

Strong links only. Keep try-next (same-kind animals) separate.
Do not invent weak edges or park study tiers.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LINKS_JSON = REPO / "static" / "field-pack" / "data" / "animal-park-links.json"

CARD_PARK_RAIL_KICKER = "See them in the wild"
CARD_PARK_RAIL_ARIA = "See them in the wild"
PARK_ANIMALS_H2 = "Animals you might meet"
PARK_ANIMALS_LEAD_DEFAULT = (
    "Sightings aren’t promised. Give wildlife lots of space — "
    "stay in the car or far back."
)


def _esc(s: str) -> str:
    return (
        str(s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


@lru_cache(maxsize=1)
def load_animal_park_links() -> dict:
    return json.loads(LINKS_JSON.read_text(encoding="utf-8"))


def parks_for_animal(card_id: str) -> list[dict]:
    """Park edges for a card, primary first, strong/sourced only."""
    cid = str(card_id or "").strip()
    data = load_animal_park_links()
    animal = (data.get("animals") or {}).get(cid) or {}
    parks_meta = data.get("parks") or {}
    out: list[dict] = []
    for raw in animal.get("parks") or []:
        pid = str(raw.get("id") or "").strip()
        if not pid:
            continue
        meta = parks_meta.get(pid) or {}
        out.append(
            {
                "id": pid,
                "primary": bool(raw.get("primary")),
                "source": str(raw.get("source") or meta.get("source") or ""),
                "note": str(raw.get("note") or ""),
                "name": str(meta.get("name") or pid.replace("-", " ")),
                "full_name": str(meta.get("full_name") or meta.get("name") or pid),
                "photo": str(meta.get("photo") or f"/field-pack/photos/np-hero-{pid}.jpg?v=q2"),
            }
        )
    out.sort(key=lambda p: (not p["primary"], p["name"].lower()))
    return out


def animals_for_park(park_id: str) -> list[dict]:
    """Animal edges listed on a park page (reverse of the animal graph)."""
    pid = str(park_id or "").strip()
    data = load_animal_park_links()
    park = (data.get("parks") or {}).get(pid) or {}
    animals_meta = data.get("animals") or {}
    out: list[dict] = []
    for cid in park.get("animals") or []:
        cid = str(cid or "").strip()
        if not cid:
            continue
        meta = animals_meta.get(cid) or {}
        note = ""
        for edge in meta.get("parks") or []:
            if str(edge.get("id") or "") == pid:
                note = str(edge.get("note") or "")
                break
        out.append(
            {
                "id": cid,
                "name": str(meta.get("name") or cid.replace("-", " ")),
                "emoji": str(meta.get("emoji") or ""),
                "photo": str(meta.get("photo") or f"/field-pack/photos/{cid}.jpg?v=img2"),
                "note": note,
            }
        )
    return out


def park_page_lead(park_id: str) -> str:
    park = (load_animal_park_links().get("parks") or {}).get(str(park_id or "").strip()) or {}
    return str(park.get("lead") or PARK_ANIMALS_LEAD_DEFAULT)


def animal_park_rail_html(card_id: str) -> str:
    """Screen-only park thumbs under Try next. Empty when no strong links."""
    parks = parks_for_animal(card_id)
    if not parks:
        return ""
    thumbs: list[str] = []
    for park in parks:
        href = f"/field-pack/{_esc(park['id'])}/"
        photo = park["photo"]
        if photo.startswith("/field-pack/"):
            src = photo
        elif photo.startswith("photos/"):
            src = "/field-pack/" + photo
        else:
            src = f"/field-pack/photos/np-hero-{_esc(park['id'])}.jpg?v=q2"
        name = park["name"]
        thumbs.append(
            f'<a class="card-try-next-link" href="{href}" '
            f'data-park="{_esc(park["id"])}" '
            f'aria-label="{_esc(CARD_PARK_RAIL_ARIA)}: {_esc(name)}">'
            f'<img class="card-try-next-thumb" src="{_esc(src)}" alt="" '
            f'width="160" height="120" loading="lazy" decoding="async" />'
            f'<span class="card-try-next-name">{_esc(name)}</span>'
            f"</a>"
        )
    return (
        f'<nav class="card-try-next card-park-rail no-print" '
        f'data-rail="parks" aria-label="{_esc(CARD_PARK_RAIL_ARIA)}">'
        f'<p class="card-try-next-kicker">{_esc(CARD_PARK_RAIL_KICKER)}</p>'
        f'<div class="card-try-next-grid card-park-rail-grid">{"".join(thumbs)}</div>'
        f"</nav>"
    )


def park_animals_html(park_id: str) -> str:
    """Place-page animal thumbs. Empty when the park has no reverse edges."""
    animals = animals_for_park(park_id)
    if not animals:
        return ""
    cards: list[str] = []
    for animal in animals:
        cid = animal["id"]
        href = f"/field-pack/cards/{_esc(cid)}/"
        photo = animal["photo"]
        if photo.startswith("/field-pack/"):
            src = photo[len("/field-pack/") :]
        elif photo.startswith("photos/"):
            src = photo
        else:
            src = f"photos/{_esc(cid)}.jpg?v=img2"
        emoji = animal["emoji"]
        name = animal["name"]
        title = f"{emoji} {name}".strip()
        blurb = animal["note"] or PARK_ANIMALS_LEAD_DEFAULT
        cards.append(
            f'<a class="seo-animal-card" href="{href}" role="listitem" '
            f'data-animal="{_esc(cid)}">'
            f'<img src="{_esc(src)}" alt="" width="640" height="640" '
            f'loading="lazy" decoding="async" />'
            f'<div class="seo-animal-meta">'
            f"<h3>{_esc(title)}</h3>"
            f"<p>{_esc(blurb)}</p>"
            f"</div>"
            f"</a>"
        )
    lead = park_page_lead(park_id)
    return (
        f'<section class="seo-home-session seo-park-animals no-print" '
        f'id="animals-you-might-meet" aria-labelledby="park-animals-heading">'
        f'<h2 id="park-animals-heading">{_esc(PARK_ANIMALS_H2)}</h2>'
        f'<p class="seo-home-lead">{_esc(lead)}</p>'
        f'<div class="seo-animal-grid" role="list">{"".join(cards)}</div>'
        f"</section>"
    )
