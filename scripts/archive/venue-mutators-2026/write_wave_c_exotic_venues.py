#!/usr/bin/env python3
"""Write thin Wave C exotic park venue JSONs (Giant Panda NP, French Island, Galápagos)."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VENUE_DIR = REPO / "static" / "field-pack" / "data" / "venues"
TODAY = "2026-09-12"
AGES = ["2-3", "4-5", "6-8", "9+"]
CHALLENGE_AGES = ["2-3", "4-5", "6-8", "adult"]

GPNP_SOURCE = "https://www.forestry.gov.cn/c/www/wmdgjgy/119160.jhtml"
GPNP_VISIT = "https://www.chinawolong.gov.cn/"
FRENCH_SOURCE = "https://www.parks.vic.gov.au/places-to-see/parks/french-island-national-park"
GALAPAGOS_SOURCE = "https://galapagos.gob.ec/parque-nacional-galapagos/"


def item(
    iid: str,
    label: str,
    emoji: str,
    one: str,
    catalog_id: str,
    *,
    tags: list[str],
    zone: str,
    presence: str = "verified",
) -> dict:
    return {
        "id": iid,
        "label": label,
        "emoji": emoji,
        "one_liner": one,
        "tags": tags,
        "age_fit": list(AGES),
        "zone": zone,
        "qa_card": {
            "question": f"What did you notice at the {label}?",
            "answer": "Tell a grown-up one thing you saw, heard, or felt!",
        },
        "catalog_id": catalog_id,
        "presence": presence,
        "presence_checked": TODAY,
        "presence_source": "official_park_research",
        "display_label": label,
    }


def watch(challenge_id: str, zone: str, label: str) -> dict:
    return {
        "id": challenge_id,
        "text": f"{zone}: take 15 seconds on the {label} — what is it doing right now?",
        "age_fit": list(CHALLENGE_AGES),
    }


SHARED_CHALLENGES = [
    {
        "id": "np_still",
        "text": "Quiet 20 seconds on the trail — bird, wind, water, or people: what wins?",
        "age_fit": list(CHALLENGE_AGES),
    },
    {
        "id": "np_far_near",
        "text": "Name something far first — then something by your feet",
        "age_fit": list(CHALLENGE_AGES),
    },
    {
        "id": "np_camo",
        "text": "Best natural camouflage (rock, bark, shadow) you can spot",
        "age_fit": ["4-5", "6-8", "adult"],
    },
    {
        "id": "np_map",
        "text": "Find a map or zone name you haven’t noticed — point it out",
        "age_fit": ["4-5", "6-8", "adult"],
    },
    {
        "id": "np_tiny_huge",
        "text": "Something tiny next to something huge in this area",
        "age_fit": list(CHALLENGE_AGES),
    },
]


def park(
    *,
    slug: str,
    name: str,
    city: str,
    region: str,
    country: str,
    lat: float,
    lng: float,
    official_url: str,
    tagline: str,
    practical: dict,
    items: list[dict],
    hero: str,
    osm: str,
    route: list[str],
    find_ids: list[str],
    watches: list[dict],
    research_notes: str,
) -> dict:
    return {
        "slug": slug,
        "name": name,
        "type": "national_park",
        "city": city,
        "region": region,
        "country": country,
        "lat": lat,
        "lng": lng,
        "official_url": official_url,
        "last_verified": TODAY,
        "verified_by": "research",
        "status": "verified",
        "tagline": tagline,
        "practical": practical,
        "items": items,
        "content_mode": "curated",
        "media": {
            "visitor_map_page": official_url,
            "visitor_map_kind": "image",
            "map_attribution": "Map: © OpenStreetMap contributors",
            "hero_illustration": hero,
            "visitor_map_full": osm,
        },
        "parent_script": [
            "Bathroom first",
            "Water & weather check",
            "One big view",
            "Leave while happy",
        ],
        "route_90m": route,
        "research_notes": research_notes,
        "list_confidence": "partial",
        "do_not_list": [],
        "presence_sources": [official_url],
        "last_presence_audit": TODAY,
        "bonus_hunt": {
            "tagline": f"{name} bonus · second look on the trail",
            "find_ids": find_ids,
            "challenges": watches + SHARED_CHALLENGES,
            "easter_egg": "★ Easter egg: find a park map or zone sign — name one animal that lives that way",
            "easter_egg_little": "★ Easter egg: pick a favorite bench — sit 60 seconds and name three sounds",
            "researched": TODAY,
            "status": "solid",
            "sources": [official_url],
        },
    }


def gpnp() -> dict:
    items = [
        item(
            "vc",
            "Wolong visitor center",
            "🏛️",
            "Maps and questions — start the Sichuan slice here.",
            "np-visitor-center",
            tags=["rest"],
            zone="Entrance",
        ),
        item(
            "panda",
            "Giant panda (if you see one)",
            "🐼",
            "Mountain bamboo forests — never promised, stay far back.",
            "giant-panda",
            tags=["wow"],
            zone="Forest",
            presence="medium",
        ),
        item(
            "bamboo",
            "Bamboo forest edge",
            "🌳",
            "Look, don’t step off the path.",
            "np-giant-tree",
            tags=["outdoor"],
            zone="Forest",
        ),
        item(
            "overlook",
            "Mountain valley overlook",
            "🌄",
            "Sichuan ridges from a safe pullout.",
            "np-scenic-overlook",
            tags=["wow"],
            zone="Overlook",
        ),
        item(
            "sign",
            "Trail / stay-back sign",
            "🥾",
            "Read the rules before you walk.",
            "np-trailhead-sign",
            tags=["read"],
            zone="Trail",
        ),
        item(
            "path",
            "Marked forest path",
            "🪵",
            "Stay on the path — fragile ground.",
            "np-boardwalk",
            tags=["walk"],
            zone="Trail",
        ),
        item(
            "meadow",
            "Mountain meadow break",
            "🌿",
            "Quiet stop — wildlife never guaranteed.",
            "np-meadow",
            tags=["outdoor"],
            zone="Meadow",
        ),
        item(
            "ranger",
            "Giant Panda National Park ranger talk (if offered)",
            "🗣️",
            "Check the day’s board at the visitor center.",
            "np-ranger-program",
            tags=["hands"],
            zone="VC",
            presence="medium",
        ),
    ]
    return park(
        slug="giant-panda-national-park",
        name="Giant Panda National Park",
        city="Wolong",
        region="Sichuan",
        country="CN",
        lat=31.0294,
        lng=103.1967,
        official_url=GPNP_VISIT,
        tagline="Giant Panda National Park — Wolong visitor slice; wild pandas never promised.",
        practical={
            "typical_duration": "half day",
            "ticket_note": "Check current Wolong / park access; some areas need permits.",
            "transit_note": "Sichuan mountain roads; plan a car or tour day from Chengdu.",
            "energy_note": "Altitude and winding roads; stay on marked paths.",
            "best_start": "Wolong visitor center → one forest overlook → leave while happy",
            "slice_name": "Wolong visitor slice",
            "season_note": "Mountain weather changes fast; sightings are never promised.",
        },
        items=items,
        hero="/field-pack/photos/np-hero-giant-panda-national-park.jpg",
        osm="https://www.openstreetmap.org/#map=11/31.0294/103.1967",
        route=["vc", "panda", "overlook"],
        find_ids=["path", "bamboo", "sign", "vc", "overlook", "meadow", "panda"],
        watches=[
            watch("gpnp_path_watch", "Trail", "Marked forest path"),
            watch("gpnp_bamboo_watch", "Forest", "Bamboo forest edge"),
            watch("gpnp_sign_watch", "Trail", "Trail / stay-back sign"),
            watch("gpnp_vc_watch", "Entrance", "Wolong visitor center"),
            watch("gpnp_over_watch", "Overlook", "Mountain valley overlook"),
        ],
        research_notes=(
            "Wave C 2026-09-12 · NFGA Giant Panda National Park page + Wolong administration · "
            "thin slice, shared catalog cards only"
        ),
    )


def french_island() -> dict:
    items = [
        item(
            "jetty",
            "Tankerton jetty / visitor info",
            "🏛️",
            "Ferry landing — maps and questions start here.",
            "np-visitor-center",
            tags=["rest"],
            zone="Entrance",
        ),
        item(
            "koala",
            "Koala (if you see one)",
            "🐨",
            "Look up in the woodland — never promised.",
            "koala",
            tags=["wow"],
            zone="Woodland",
            presence="high",
        ),
        item(
            "woodland",
            "Manna gum woodland",
            "🌳",
            "Koala food trees — hug with your eyes only.",
            "np-giant-tree",
            tags=["outdoor"],
            zone="Woodland",
        ),
        item(
            "overlook",
            "Wetland / Western Port view",
            "🌄",
            "Saltmarsh and bay from a safe lookout.",
            "np-scenic-overlook",
            tags=["wow"],
            zone="Overlook",
        ),
        item(
            "sign",
            "Walk / cycle sign",
            "🥾",
            "Read distance and rules before you go.",
            "np-trailhead-sign",
            tags=["read"],
            zone="Trail",
        ),
        item(
            "beach",
            "Fairhaven beach walk",
            "🌊",
            "Shore birds at low tide — stay far back.",
            "np-tide-coast",
            tags=["water", "wow"],
            zone="Shore",
        ),
        item(
            "heath",
            "Heathland walk",
            "🌿",
            "Short walk from Tankerton as energy allows.",
            "np-meadow",
            tags=["walk"],
            zone="Heath",
        ),
        item(
            "ranger",
            "French Island ranger talk (if offered)",
            "🗣️",
            "Check the day’s board if a talk is posted.",
            "np-ranger-program",
            tags=["hands"],
            zone="VC",
            presence="medium",
        ),
    ]
    return park(
        slug="french-island",
        name="French Island National Park",
        city="Tankerton",
        region="VIC",
        country="AU",
        lat=-38.3514,
        lng=145.3372,
        official_url=FRENCH_SOURCE,
        tagline="French Island — Tankerton ferry day; koalas never promised.",
        practical={
            "typical_duration": "half day",
            "ticket_note": "Park free; Western Port ferry tickets separate.",
            "transit_note": "Passenger ferry from Stony Point to Tankerton; services can cancel.",
            "energy_note": "Mosquitoes; limited medical help on the island; pack water.",
            "best_start": "Tankerton jetty → short woodland walk → one wetland view",
            "slice_name": "Tankerton woodland walk",
            "season_note": "Year-round ferry weather; winter can be wet and windy.",
        },
        items=items,
        hero="/field-pack/photos/np-hero-french-island.jpg",
        osm="https://www.openstreetmap.org/#map=12/-38.3514/145.3372",
        route=["jetty", "koala", "woodland"],
        find_ids=["heath", "woodland", "sign", "jetty", "overlook", "beach", "koala"],
        watches=[
            watch("fi_heath_watch", "Heath", "Heathland walk"),
            watch("fi_wood_watch", "Woodland", "Manna gum woodland"),
            watch("fi_sign_watch", "Trail", "Walk / cycle sign"),
            watch("fi_jetty_watch", "Entrance", "Tankerton jetty / visitor info"),
            watch("fi_over_watch", "Overlook", "Wetland / Western Port view"),
        ],
        research_notes=(
            "Wave C 2026-09-12 · Parks Victoria French Island page names Victoria’s "
            "most significant koala population · thin slice, shared catalog cards only"
        ),
    )


def galapagos() -> dict:
    items = [
        item(
            "vc",
            "Santa Cruz visitor center",
            "🏛️",
            "Maps and questions — start the island slice here.",
            "np-visitor-center",
            tags=["rest"],
            zone="Entrance",
        ),
        item(
            "tortoise",
            "Giant tortoise (if you see one)",
            "🐢",
            "The park’s emblem — keep a long, quiet distance.",
            "galapagos-tortoise",
            tags=["wow"],
            zone="Highlands",
            presence="high",
        ),
        item(
            "overlook",
            "Highland or island overlook",
            "🌄",
            "Volcano slopes from a marked viewpoint.",
            "np-scenic-overlook",
            tags=["wow"],
            zone="Overlook",
        ),
        item(
            "sign",
            "Trail / landing sign",
            "🥾",
            "Read the stay-back rules before you walk.",
            "np-trailhead-sign",
            tags=["read"],
            zone="Trail",
        ),
        item(
            "path",
            "Marked visitor path",
            "🪵",
            "Stay on the path — fragile ground.",
            "np-boardwalk",
            tags=["walk"],
            zone="Trail",
        ),
        item(
            "shore",
            "Rocky shore or landing",
            "🌊",
            "From a boat or marked landing — never chase wildlife.",
            "np-tide-coast",
            tags=["water", "wow"],
            zone="Shore",
        ),
        item(
            "tree",
            "Highland tree / cactus edge",
            "🌳",
            "Look, don’t step off the path.",
            "np-giant-tree",
            tags=["outdoor"],
            zone="Highlands",
        ),
        item(
            "ranger",
            "Galápagos park guide talk (if offered)",
            "🗣️",
            "Check the day’s board or your licensed guide.",
            "np-ranger-program",
            tags=["hands"],
            zone="VC",
            presence="medium",
        ),
    ]
    return park(
        slug="galapagos",
        name="Galápagos National Park",
        city="Puerto Ayora",
        region="Galápagos",
        country="EC",
        lat=-0.7439,
        lng=-90.3131,
        official_url=GALAPAGOS_SOURCE,
        tagline="Galápagos — Santa Cruz visitor slice; giant tortoises never promised.",
        practical={
            "typical_duration": "half day",
            "ticket_note": "Parque Nacional Galápagos entry is required; check current fees.",
            "transit_note": "Fly to Baltra or San Cristóbal; Santa Cruz is the usual first slice.",
            "energy_note": "Sun and heat; stay on marked paths; licensed guide rules apply.",
            "best_start": "Santa Cruz visitor center → one highland stop → leave while happy",
            "slice_name": "Santa Cruz visitor slice",
            "season_note": "Year-round; landings and paths can close. Sightings aren’t promised.",
        },
        items=items,
        hero="/field-pack/photos/np-hero-galapagos.jpg",
        osm="https://www.openstreetmap.org/#map=12/-0.7439/-90.3131",
        route=["vc", "tortoise", "overlook"],
        find_ids=["path", "tree", "sign", "vc", "overlook", "shore", "tortoise"],
        watches=[
            watch("gp_path_watch", "Trail", "Marked visitor path"),
            watch("gp_tree_watch", "Highlands", "Highland tree / cactus edge"),
            watch("gp_sign_watch", "Trail", "Trail / landing sign"),
            watch("gp_vc_watch", "Entrance", "Santa Cruz visitor center"),
            watch("gp_over_watch", "Overlook", "Highland or island overlook"),
        ],
        research_notes=(
            "Wave C 2026-09-12 · Parque Nacional Galápagos official page names giant tortoises "
            "as the park’s most representative species · thin slice, shared catalog cards only"
        ),
    )


def main() -> int:
    VENUE_DIR.mkdir(parents=True, exist_ok=True)
    for venue in (gpnp(), french_island(), galapagos()):
        path = VENUE_DIR / f"{venue['slug']}.json"
        path.write_text(json.dumps(venue, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("wrote", path.relative_to(REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
