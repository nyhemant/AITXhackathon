#!/usr/bin/env python3
"""Build parks-map-library.json: CONUS kits + Albers x,y fitted to the live map SVG.

Films: cinematic / wordless first. `start` skips title cards so autoplay hits the icon.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENUES = ROOT / "static/field-pack/data/venues"
OUT = ROOT / "static/field-pack/data/virtual-venues/parks-map-library.json"
PARKS_JSON = ROOT / "static/field-pack/data/virtual-venues/virtual-parks.json"

LAT0 = math.radians(37.5)
LON0 = math.radians(-96.0)
SP1 = math.radians(29.5)
SP2 = math.radians(45.5)
N = 0.5 * (math.sin(SP1) + math.sin(SP2))
C = math.cos(SP1) ** 2 + 2 * N * math.sin(SP1)
RHO0 = math.sqrt(C - 2 * N * math.sin(LAT0)) / N

SKIP = {
    "denali",
    "gates-of-arctic",
    "glacier-bay",
    "katmai",
    "kenai-fjords",
    "kobuk-valley",
    "lake-clark",
    "wrangell-st-elias",
    "haleakala",
    "hawaii-volcanoes",
    "american-samoa",
    "virgin-islands",
}

# Live map.svg pin positions (habitat order on the road trip).
KNOWN_XY = {
    "acadia": (926.0, 127.1),
    "great-smoky-mountains": (723.9, 361.2),
    "everglades": (803.3, 573.6),
    "big-bend": (374.5, 510.2),
    "grand-canyon": (234.8, 343.3),
    "yosemite": (119.0, 281.4),
    "olympic": (120.2, 52.8),
    "glacier": (267.3, 66.1),
    "yellowstone": (285.0, 168.1),
    "rocky-mountain": (353.6, 266.2),
}

DEFAULT_TOUR = [
    "acadia",
    "great-smoky-mountains",
    "everglades",
    "big-bend",
    "grand-canyon",
    "yosemite",
    "olympic",
    "glacier",
    "yellowstone",
    "rocky-mountain",
]

# start = seconds to skip logos so the first frame is the landmark.
FILMS = {
    "acadia": {
        "url": "https://www.youtube.com/watch?v=4bRKthFQfXo",
        "title": "Acadia granite coast and Cadillac",
        "channel": "More Than Just Parks",
        "start": 6,
        "icon": "Atlantic granite + Cadillac",
    },
    "great-smoky-mountains": {
        "url": "https://www.youtube.com/watch?v=i_WME0gAO_g",
        "title": "Smokies ridges in fall",
        "channel": "More Than Just Parks",
        "start": 6,
        "icon": "blue ridgelines",
    },
    "everglades": {
        "url": "https://www.youtube.com/watch?v=4IFn0t0rkiE",
        "title": "Alligators and wildlife of the Everglades",
        "channel": "4K Relaxation Channel",
        "start": 8,
        "icon": "gators in the water",
    },
    "big-bend": {
        "url": "https://www.youtube.com/watch?v=izPFPJS3Ohs",
        "title": "Big Bend Chisos mountains and canyons",
        "channel": "4K Healing Scenery",
        "start": 5,
        "icon": "Chisos desert mountains",
    },
    "grand-canyon": {
        "url": "https://www.youtube.com/watch?v=LtEG2UEbD4U",
        "title": "Grand Canyon from the rim",
        "channel": "Amazing Places on Our Planet",
        "start": 8,
        "icon": "rim abyss",
    },
    "yosemite": {
        "url": "https://www.youtube.com/watch?v=HLmOkDBfxv0",
        "title": "Yosemite granite and waterfalls",
        "channel": "Amazing Places on Our Planet",
        "start": 8,
        "icon": "valley granite / falls",
    },
    "olympic": {
        "url": "https://www.youtube.com/watch?v=6jQ_eu3b_BA",
        "title": "Olympic rainforest, coast, and ridge",
        "channel": "More Than Just Parks",
        "start": 6,
        "icon": "moss forest + coast",
    },
    "glacier": {
        "url": "https://www.youtube.com/watch?v=zrHlFPRI_0c",
        "title": "Glacier lakes and peaks",
        "channel": "Amazing Places on Our Planet",
        "start": 8,
        "icon": "Going-to-the-Sun peaks",
    },
    "yellowstone": {
        "url": "https://www.youtube.com/watch?v=635UZAPkElg",
        "title": "Yellowstone Grand Prismatic Spring",
        "channel": "Amazing Places on Our Planet",
        "start": 2,
        "icon": "Grand Prismatic from above",
    },
    "rocky-mountain": {
        "url": "https://www.youtube.com/watch?v=9Gh44EYQ2zw",
        "title": "Rocky Mountain high meadows",
        "channel": "More Than Just Parks",
        "start": 6,
        "icon": "alpine meadows",
    },
    "arches": {
        "url": "https://www.youtube.com/watch?v=cgkizvteN0M",
        "title": "Arches — sunrise through South Window",
        "channel": "Amazing Places on Our Planet",
        "start": 7,
        "icon": "sunrise through South Window",
    },
    "badlands": {
        "url": "https://www.youtube.com/watch?v=Wp3yXVTIugQ",
        "title": "Badlands striped buttes",
        "channel": "More Than Just Parks",
        "start": 6,
        "icon": "banded badlands",
    },
    "biscayne": {
        "url": "https://www.youtube.com/watch?v=taSrHXYX7uc",
        "title": "Biscayne water and reef",
        "channel": "A Glimpse of the Journey",
        "start": 6,
        "icon": "turquoise bay",
    },
    "black-canyon-gunnison": {
        "url": "https://www.youtube.com/watch?v=Sa3DcKwikj0",
        "title": "Black Canyon of the Gunnison walls",
        "channel": "Amazing Places on Our Planet",
        "start": 8,
        "icon": "dark narrow canyon",
    },
    "bryce-canyon": {
        "url": "https://www.youtube.com/watch?v=mn7Zv1ZNF4s",
        "title": "Bryce Canyon hoodoos",
        "channel": "Amazing Places on Our Planet",
        "start": 8,
        "icon": "amphitheater hoodoos",
    },
    "canyonlands": {
        "url": "https://www.youtube.com/watch?v=MOzSqGyhKbs",
        "title": "Canyonlands Island in the Sky",
        "channel": "More Than Just Parks",
        "start": 6,
        "icon": "mesa and canyon drop",
    },
    "capitol-reef": {
        "url": "https://www.youtube.com/watch?v=a99ioa2tszw",
        "title": "Capitol Reef Waterpocket Fold",
        "channel": "More Than Just Parks",
        "start": 6,
        "icon": "red fold and white domes",
    },
    "carlsbad-caverns": {
        "url": "https://www.youtube.com/watch?v=R0Otx2OmIyk",
        "title": "Carlsbad Caverns Big Room — no talking",
        "channel": "Rain Hours",
        "start": 45,
        "icon": "underground Big Room",
    },
    "channel-islands": {
        "url": "https://www.youtube.com/watch?v=SicHkn869kQ",
        "title": "Channel Islands from the sea",
        "channel": "Ventura Harbor",
        "start": 8,
        "icon": "islands in the Pacific",
    },
    "congaree": {
        "url": "https://www.youtube.com/watch?v=oIvUfKDgvno",
        "title": "Congaree floodplain forest walk",
        "channel": "MileMarker4K",
        "start": 5,
        "icon": "boardwalk among giants",
    },
    "crater-lake": {
        "url": "https://www.youtube.com/watch?v=GFskQm2vAV0",
        "title": "Crater Lake blue water",
        "channel": "Amazing Places on Our Planet",
        "start": 8,
        "icon": "caldera blue + Wizard Island",
    },
    "cuyahoga-valley": {
        "url": "https://www.youtube.com/watch?v=D3leZ5R5aGw",
        "title": "Cuyahoga Ledges Trail",
        "channel": "DroneRoamer",
        "start": 0,
        "icon": "ledges and forest",
    },
    "death-valley": {
        "url": "https://www.youtube.com/watch?v=uvJfZutjpHA",
        "title": "Death Valley dunes and Badwater",
        "channel": "More Than Just Parks",
        "start": 6,
        "icon": "dunes / salt flats",
    },
    "dry-tortugas": {
        "url": "https://www.youtube.com/watch?v=F6o2EZPNSRA",
        "title": "Dry Tortugas Fort Jefferson",
        "channel": "VISIT FLORIDA",
        "start": 8,
        "icon": "brick fort in turquoise water",
    },
    "gateway-arch": {
        "url": "https://www.youtube.com/watch?v=DwnLsWZsKfs",
        "title": "Gateway Arch on the river",
        "channel": "MileMarker4K",
        "start": 5,
        "icon": "the Arch",
    },
    "grand-teton": {
        "url": "https://www.youtube.com/watch?v=oRxLvMHLI3I",
        "title": "Grand Teton peaks and wildlife",
        "channel": "More Than Just Parks",
        "start": 6,
        "icon": "Teton skyline",
    },
    "great-basin": {
        "url": "https://www.youtube.com/watch?v=km7dBhMGx_U",
        "title": "Great Basin National Park film",
        "channel": "GreatBasinNPS",
        "start": 8,
        "icon": "Wheeler Peak / bristlecones",
    },
    "great-sand-dunes": {
        "url": "https://www.youtube.com/watch?v=5UDssG7XlgY",
        "title": "Great Sand Dunes against the mountains",
        "channel": "Amazing Places on Our Planet",
        "start": 8,
        "icon": "dunes + Sangre de Cristo",
    },
    "guadalupe-mountains": {
        "url": "https://www.youtube.com/watch?v=3yR5x3SSeTA",
        "title": "Guadalupe Mountains scenic drive",
        "channel": "Adventure Theater",
        "start": 8,
        "icon": "El Capitan reef mountain",
    },
    "hot-springs": {
        "url": "https://www.youtube.com/watch?v=Dn3nkDip3P4",
        "title": "Hot Springs historic bathhouse row",
        "channel": "Adventure Theater",
        "start": 8,
        "icon": "Bathhouse Row",
    },
    "indiana-dunes": {
        "url": "https://www.youtube.com/watch?v=k12qsuez4Ec",
        "title": "Indiana Dunes from the air",
        "channel": "TAPP Channel",
        "start": 3,
        "icon": "dunes on Lake Michigan",
    },
    "isle-royale": {
        "url": "https://www.youtube.com/watch?v=4cxWWTSHui4",
        "title": "Isle Royale from the water",
        "channel": "Pure Michigan",
        "start": 8,
        "icon": "island wilderness",
    },
    "joshua-tree": {
        "url": "https://www.youtube.com/watch?v=rbHTLIxdCCg",
        "title": "Joshua Tree boulders and night sky",
        "channel": "More Than Just Parks",
        "start": 6,
        "icon": "Joshua trees + rocks",
    },
    "kings-canyon": {
        "url": "https://www.youtube.com/watch?v=DUFqAAuSwog",
        "title": "Kings Canyon sequoias and granite",
        "channel": "World Scenery 4K",
        "start": 5,
        "icon": "deep granite canyon",
    },
    "lassen-volcanic": {
        "url": "https://www.youtube.com/watch?v=z_u7iz2LyGk",
        "title": "Lassen volcanic peaks and lakes",
        "channel": "PrimoMedia - Chris Biela",
        "start": 8,
        "icon": "Lassen Peak",
    },
    "mammoth-cave": {
        "url": "https://www.youtube.com/watch?v=fo-zi_83U5I",
        "title": "Mammoth Cave historic tour walk",
        "channel": "The Perfect Walk",
        "start": 20,
        "icon": "lit cave passage",
    },
    "mesa-verde": {
        "url": "https://www.youtube.com/watch?v=bCbryviVgwY",
        "title": "Mesa Verde cliff dwellings",
        "channel": "Amazing Places on Our Planet",
        "start": 8,
        "icon": "Cliff Palace",
    },
    "mount-rainier": {
        "url": "https://www.youtube.com/watch?v=n4uOuy3Zac4",
        "title": "Mount Rainier meadows and glacier",
        "channel": "Amazing Places on Our Planet",
        "start": 8,
        "icon": "Rainier above wildflowers",
    },
    "new-river-gorge": {
        "url": "https://www.youtube.com/watch?v=__lLTJmTsp4",
        "title": "New River Gorge bridge and gorge",
        "channel": "More Than Just Parks",
        "start": 6,
        "icon": "bridge over the gorge",
    },
    "north-cascades": {
        "url": "https://www.youtube.com/watch?v=duGVGKvyKiI",
        "title": "North Cascades jagged peaks",
        "channel": "Amazing Places on Our Planet",
        "start": 8,
        "icon": "ice and spires",
    },
    "petrified-forest": {
        "url": "https://www.youtube.com/watch?v=4vHCYNa5yq0",
        "title": "Petrified Forest painted desert",
        "channel": "Alaskan Ram Travel Adventures",
        "start": 6,
        "icon": "petrified logs + painted desert",
    },
    "pinnacles": {
        "url": "https://www.youtube.com/watch?v=sm_1PUZoW5A",
        "title": "Pinnacles rock spires",
        "channel": "Machine Bazi",
        "start": 5,
        "icon": "volcanic spires",
    },
    "redwood": {
        "url": "https://www.youtube.com/watch?v=LKavDOPMq4o",
        "title": "Redwood cathedral forest",
        "channel": "More Than Just Parks",
        "start": 6,
        "icon": "looking up the trunks",
    },
    "saguaro": {
        "url": "https://www.youtube.com/watch?v=xGzHrrozRH8",
        "title": "Saguaro desert forest",
        "channel": "More Than Just Parks",
        "start": 6,
        "icon": "saguaro skyline",
    },
    "sequoia": {
        "url": "https://www.youtube.com/watch?v=WWorX7kqC9g",
        "title": "Sequoia Giant Forest",
        "channel": "At Home In Wild Spaces",
        "start": 5,
        "icon": "Giant Forest trunks",
    },
    "shenandoah": {
        "url": "https://www.youtube.com/watch?v=1GfyOs__FIg",
        "title": "Shenandoah Skyline Drive in summer",
        "channel": "New Horizons",
        "start": 6,
        "icon": "Blue Ridge overlook",
    },
    "theodore-roosevelt": {
        "url": "https://www.youtube.com/watch?v=o7X2oPGLGq8",
        "title": "Theodore Roosevelt badlands",
        "channel": "More Than Just Parks",
        "start": 6,
        "icon": "Little Missouri badlands",
    },
    "voyageurs": {
        "url": "https://www.youtube.com/watch?v=2_GQ7oS3orE",
        "title": "Voyageurs lakes and islands",
        "channel": "More Than Just Parks",
        "start": 6,
        "icon": "glassy lake country",
    },
    "white-sands": {
        "url": "https://www.youtube.com/watch?v=tSruWf7iaQM",
        "title": "White Sands gypsum dunes",
        "channel": "Amazing Places on Our Planet",
        "start": 8,
        "icon": "white dune field",
    },
    "wind-cave": {
        "url": "https://www.youtube.com/watch?v=8HtADDs3Xq4",
        "title": "Wind Cave prairie and cave",
        "channel": "More Than Just Parks",
        "start": 6,
        "icon": "prairie + cave",
    },
    "zion": {
        "url": "https://www.youtube.com/watch?v=ecc7t3PkkiM",
        "title": "Zion Canyon in fall",
        "channel": "More Than Just Parks",
        "start": 6,
        "icon": "red Zion Canyon",
    },
}

QA = {
    "acadia": ("Why is ocean water salty? What happens when waves hit rock?", "Rivers carry a little salt from rocks, and it stays in the sea. Waves slowly wear the rock away."),
    "great-smoky-mountains": ("Why do faraway mountains look blue or smoky?", "Air and tiny drops scatter light, so far ridges look blue or hazy."),
    "everglades": ("Why is a wetland so important? Who lives in the sawgrass?", "Wetlands clean water and make a home for birds, fish, and gators. Sawgrass is a wet prairie, not a dry field."),
    "big-bend": ("How can a river cut through a desert? Where does the water go?", "Even a dry place can have a strong river. The water carved the land for a long time and keeps flowing on."),
    "grand-canyon": ("How did a river cut a canyon this deep?", "The Colorado River wore away rock, grain by grain, for millions of years. Slow water can cut a huge canyon."),
    "yosemite": ("How does a waterfall start? Why is granite so steep?", "A river falls where the land drops. Ice and rock-cracking made the granite walls steep."),
    "olympic": ("Why can one park have rain forest and ocean?", "Mountains catch wet air from the sea. One side stays rainy and green; the coast stays wild and salty."),
    "glacier": ("Why is glacier ice blue? How does a glacier move?", "Thick ice swallows other colors and lets blue through. The ice is a slow river — it slides under its own weight."),
    "yellowstone": ("Why does a geyser shoot up? What’s under the ground?", "Water soaks down, hits hot rock, and blasts out as steam. A huge heat source sits under the park."),
    "rocky-mountain": ("Why is it harder to breathe up high? Why are mountains snowy?", "The air is thinner up high, so each breath has less oxygen. It stays colder, so snow can last."),
    "arches": ("How does a rock become an arch?", "Softer rock underneath wears away first. The harder rock on top stays, and a window opens."),
    "badlands": ("Why are the hills striped with color?", "Each stripe is a different layer of old mud and ash. Wind and rain cut them into sharp hills."),
    "biscayne": ("Why is the water so blue-green here?", "Shallow water over sand and coral lets light bounce back. The sea is a home, not just a swimming pool."),
    "black-canyon-gunnison": ("Why is this canyon so dark and skinny?", "Hard rock and a fast river cut down more than they cut sideways. Sunlight barely reaches the bottom."),
    "bryce-canyon": ("What are hoodoos? How do they stand up?", "Hoodoos are skinny rock towers. Ice and rain nibble the sides but leave a harder cap on top."),
    "canyonlands": ("Why do rivers make such a maze of canyons?", "Two rivers cut down through stacked rock. Side washes join in, so the land looks like a puzzle."),
    "capitol-reef": ("What is a fold in the earth?", "Layers of rock got pushed and bent like a rug. The fold makes cliffs, domes, and a wrinkle you can see."),
    "carlsbad-caverns": ("How does a cave get so huge underground?", "Water dissolved limestone for a very long time. Drips built stone icicles after the rooms were hollow."),
    "channel-islands": ("Why do islands have animals you don’t see on the mainland?", "Water isolates them. Animals change over time when they can’t mix with the shore."),
    "congaree": ("Why are these trees so tall in a swamp?", "Floods bring rich mud. The trees drink it and race upward for light."),
    "crater-lake": ("How did a lake get inside a mountain?", "A volcano collapsed and left a bowl. Rain and snow filled it with very deep, clear water."),
    "cuyahoga-valley": ("How can a river park sit next to a city?", "The river kept a wild strip. Trails and a towpath follow water that carved the valley."),
    "death-valley": ("Why is this one of the hottest, lowest places?", "Mountains trap heat and dry air. The floor sits below sea level, so heat piles up."),
    "dry-tortugas": ("Why is there a huge brick fort in the ocean?", "Ships needed a lookout. Builders used an island of coral and sand far from the mainland."),
    "gateway-arch": ("Why is the Arch a giant curve?", "A catenary curve is strong — like a chain hanging, flipped up. It marks the river gateway."),
    "grand-teton": ("Why do these peaks look so sharp and sudden?", "A fault lifted the range. Ice carved the horns. The valley floor sits close to the wall."),
    "great-basin": ("Why can trees live thousands of years here?", "High, dry, and slow. Bristlecones grow a little each year and hold on in tough rock."),
    "great-sand-dunes": ("How did sand piles get so tall next to mountains?", "Wind drops sand when it hits the range. The piles grow into the tallest dunes in North America."),
    "guadalupe-mountains": ("What was this mountain when it was under the sea?", "An ancient reef. The sea left, and the reef became a mountain of limestone."),
    "hot-springs": ("Why is the water hot coming out of the ground?", "Rain soaks deep, hits hot rock, and rises again. People built bathhouses on the springs."),
    "indiana-dunes": ("How do dunes form on a lake, not an ocean?", "Wind pushes beach sand inland. Plants grab it, and the piles grow along the shore."),
    "isle-royale": ("Why is this park mostly reached by boat?", "It’s an island in a huge cold lake. Water protects the quiet and the wolves and moose."),
    "joshua-tree": ("Why do Joshua trees look so spiky?", "They’re yuccas built for dry heat. Spikes save water and make shade in tiny pieces."),
    "kings-canyon": ("Why is this canyon so deep?", "A river and old ice cut granite. The walls stay steep because the rock is tough."),
    "lassen-volcanic": ("What clues show a volcano is still around?", "Steam vents, hot ground, and a big peak. The mountain is quieter now, but the heat is still under it."),
    "mammoth-cave": ("How can a cave be hundreds of miles long?", "Limestone and water. Passages join like underground streets on many levels."),
    "mesa-verde": ("Why build homes in a cliff?", "Overhangs shade and shelter. People farmed the mesa top and lived in the alcove."),
    "mount-rainier": ("Why does this mountain wear a white hat all year?", "It’s tall and cold. Snow piles into glaciers that creep down the sides."),
    "new-river-gorge": ("Is the New River actually new?", "The name is old and a little backwards — the river is ancient. It cut a deep gorge through the plateau."),
    "north-cascades": ("Why are these mountains so jagged?", "Ice chewed the peaks. What’s left are sharp horns and hanging glaciers."),
    "petrified-forest": ("How does wood turn to stone?", "Trees buried in mud. Minerals soak in and copy the wood, cell by cell."),
    "pinnacles": ("Where did these pointy rocks come from?", "An old volcano. The mountain split and moved. What’s left are spires and caves."),
    "redwood": ("Why are redwoods so tall?", "Fog drips water onto the needles. They grow toward light for centuries."),
    "saguaro": ("How does a cactus store water in a desert?", "Pleats expand like an accordion. Spines shade the skin and slow the wind."),
    "sequoia": ("How can a tree get this thick?", "It adds a ring every year for thousands of years. Fire can hollow it and it still lives."),
    "shenandoah": ("Why do these mountains look soft and blue?", "They’re old and worn. Haze and distance turn ridges blue from Skyline Drive."),
    "theodore-roosevelt": ("What carved these North Dakota badlands?", "The Little Missouri and weather. Soft rock cuts fast into buttes and valleys."),
    "voyageurs": ("Why is this park a maze of lakes?", "Ice gouged the rock. Water filled the scratches, so you travel more by boat than by trail."),
    "white-sands": ("Why is the sand white, not yellow?", "It’s gypsum, not beach quartz. The crystals stay bright and cool on your feet."),
    "wind-cave": ("What’s special about the cave’s boxwork?", "Thin fins of harder rock stick out of the walls. Wind and water left a honeycomb."),
    "zion": ("How did a river cut such tall red walls?", "The Virgin River cut down through sandstone. The walls stay steep because the rock is stacked."),
}

SHORT = {
    "great-smoky-mountains": "Smokies",
    "black-canyon-gunnison": "Black Canyon",
    "carlsbad-caverns": "Carlsbad",
    "channel-islands": "Channel Is.",
    "cuyahoga-valley": "Cuyahoga",
    "death-valley": "Death Valley",
    "dry-tortugas": "Dry Tortugas",
    "gateway-arch": "Gateway Arch",
    "grand-canyon": "Grand Canyon",
    "grand-teton": "Grand Teton",
    "great-basin": "Great Basin",
    "great-sand-dunes": "Sand Dunes",
    "guadalupe-mountains": "Guadalupe",
    "hot-springs": "Hot Springs",
    "indiana-dunes": "Ind. Dunes",
    "isle-royale": "Isle Royale",
    "joshua-tree": "Joshua Tree",
    "kings-canyon": "Kings Canyon",
    "lassen-volcanic": "Lassen",
    "mammoth-cave": "Mammoth Cave",
    "mesa-verde": "Mesa Verde",
    "mount-rainier": "Rainier",
    "new-river-gorge": "New River",
    "north-cascades": "N. Cascades",
    "petrified-forest": "Petrified",
    "rocky-mountain": "Rocky Mtn",
    "theodore-roosevelt": "T. Roosevelt",
    "white-sands": "White Sands",
    "wind-cave": "Wind Cave",
}

EMOJI = {
    "acadia": "🌅",
    "arches": "🪨",
    "badlands": "🧡",
    "big-bend": "🏜️",
    "biscayne": "🐠",
    "black-canyon-gunnison": "🌑",
    "bryce-canyon": "🧡",
    "canyonlands": "🗺️",
    "capitol-reef": "🏛️",
    "carlsbad-caverns": "🦇",
    "channel-islands": "🦭",
    "congaree": "🌳",
    "crater-lake": "🔵",
    "cuyahoga-valley": "🍂",
    "death-valley": "☀️",
    "dry-tortugas": "🏰",
    "everglades": "🐊",
    "gateway-arch": "🌉",
    "glacier": "🏔️",
    "grand-canyon": "🏞️",
    "grand-teton": "⛰️",
    "great-basin": "🌲",
    "great-sand-dunes": "🏜️",
    "great-smoky-mountains": "🌫️",
    "guadalupe-mountains": "⛰️",
    "hot-springs": "♨️",
    "indiana-dunes": "🏖️",
    "isle-royale": "🐺",
    "joshua-tree": "🌵",
    "kings-canyon": "🌲",
    "lassen-volcanic": "🌋",
    "mammoth-cave": "🕯️",
    "mesa-verde": "🏘️",
    "mount-rainier": "🗻",
    "new-river-gorge": "🌉",
    "north-cascades": "❄️",
    "olympic": "🌲",
    "petrified-forest": "🪵",
    "pinnacles": "🦅",
    "redwood": "🌲",
    "rocky-mountain": "🏔️",
    "saguaro": "🌵",
    "sequoia": "🌲",
    "shenandoah": "🌄",
    "theodore-roosevelt": "🦬",
    "voyageurs": "🛶",
    "white-sands": "⬜",
    "wind-cave": "🌬️",
    "yellowstone": "💨",
    "yosemite": "⛰️",
    "zion": "🔴",
}


def albers(lat: float, lon: float) -> tuple[float, float]:
    la = math.radians(lat)
    lo = math.radians(lon)
    theta = N * (lo - LON0)
    rho = math.sqrt(C - 2 * N * math.sin(la)) / N
    x = rho * math.sin(theta)
    y = RHO0 - rho * math.cos(theta)
    return x, y


def fit_svg() -> tuple[float, float, float]:
    """svg_x = s*ax + bx; svg_y = -s*ay + by  (isotropic, y-flipped)."""
    parks = json.loads(PARKS_JSON.read_text())["habitats"]
    by_id = {h["id"]: h for h in parks}
    axs, ays, sxs, sys = [], [], [], []
    for pid, (sx, sy) in KNOWN_XY.items():
        # lat/lon from venue files for glacier etc.
        pass
    venues = {}
    for p in VENUES.glob("*.json"):
        d = json.loads(p.read_text())
        if d.get("type") == "national_park":
            venues[d.get("slug") or p.stem] = d
    for pid, (sx, sy) in KNOWN_XY.items():
        v = venues[pid]
        ax, ay = albers(v["lat"], v["lng"])
        axs.append(ax)
        ays.append(ay)
        sxs.append(sx)
        sys.append(sy)
    # Solve s, bx from x; s, by from y with shared s.
    # Least squares: [ax, 1; -ay, 0 mixed] — do two-pass average s.
    n = len(axs)
    # From x: s, bx. From y: s, by. Average s.
    # s*ax + bx = sx
    sum_ax = sum(axs)
    sum_sx = sum(sxs)
    sum_ax2 = sum(a * a for a in axs)
    sum_axsx = sum(a * x for a, x in zip(axs, sxs))
    det = n * sum_ax2 - sum_ax * sum_ax
    s1 = (n * sum_axsx - sum_ax * sum_sx) / det
    bx = (sum_sx - s1 * sum_ax) / n
    sum_ay = sum(ays)
    sum_sy = sum(sys)
    sum_ay2 = sum(a * a for a in ays)
    sum_aysy = sum(a * y for a, y in zip(ays, sys))
    # -s*ay + by = sy  =>  s*ay + (-by) = -sy
    dety = n * sum_ay2 - sum_ay * sum_ay
    s2 = -(n * sum_aysy - sum_ay * sum_sy) / dety
    by = (sum_sy + s2 * sum_ay) / n
    s = (s1 + s2) / 2
    # Recompute bx, by with shared s
    bx = (sum_sx - s * sum_ax) / n
    by = (sum_sy + s * sum_ay) / n
    rms = 0.0
    for ax, ay, sx, sy in zip(axs, ays, sxs, sys):
        px, py = s * ax + bx, -s * ay + by
        rms += (px - sx) ** 2 + (py - sy) ** 2
    rms = math.sqrt(rms / n)
    print(f"fit s={s:.4f} bx={bx:.2f} by={by:.2f} rms={rms:.2f}px")
    return s, bx, by


def project(lat, lon, s, bx, by):
    ax, ay = albers(lat, lon)
    return round(s * ax + bx, 1), round(-s * ay + by, 1)


def main() -> None:
    s, bx, by = fit_svg()
    tour = {pid: i + 1 for i, pid in enumerate(DEFAULT_TOUR)}
    parks_cfg = json.loads(PARKS_JSON.read_text())
    cam_by_id = {
        h["id"]: h.get("cam")
        for h in parks_cfg.get("habitats") or []
        if h.get("cam") and h["cam"].get("url")
    }
    cards = []
    missing_film = []
    for p in sorted(VENUES.glob("*.json")):
        d = json.loads(p.read_text())
        if d.get("type") != "national_park":
            continue
        slug = d.get("slug") or p.stem
        if slug in SKIP:
            continue
        lat, lng = d.get("lat"), d.get("lng")
        if lat is None or lng is None:
            continue
        if not (24 <= lat <= 50 and -130 <= lng <= -66):
            continue
        film = FILMS.get(slug)
        if not film:
            missing_film.append(slug)
            continue
        x, y = project(lat, lng, s, bx, by)
        q, a = QA[slug]
        name = d.get("name") or slug
        short = SHORT.get(slug) or name.replace(" National Park", "").replace(" National and State Parks", "")
        label = short
        if slug == "great-smoky-mountains":
            label = "Great Smoky Mountains"
        elif slug == "rocky-mountain":
            label = "Rocky Mountain"
        card = {
            "cardId": slug,
            "label": label,
            "short": short,
            "emoji": EMOJI.get(slug, "🏞️"),
            "photo": f"/field-pack/photos/np-hero-{slug}.jpg?v=q3",
            "blurb": d.get("tagline") or "",
            "challenge": q,
            "printAnswer": a,
            "placeHref": f"/field-pack/{slug}/",
            "lat": lat,
            "lng": lng,
            "x": x,
            "y": y,
            "defaultTour": slug in tour,
            "seq": tour.get(slug, 99),
            "video": {
                "url": film["url"],
                "title": film["title"],
                "provider": "youtube",
                "channel": film["channel"],
                "start": film["start"],
                "icon": film["icon"],
                "verify": {
                    "status": "sourced",
                    "source": film["url"],
                    "checked": "2026-08-16",
                },
            },
        }
        if cam_by_id.get(slug):
            card["cam"] = cam_by_id[slug]
        cards.append(card)
    if missing_film:
        raise SystemExit("missing films: " + ", ".join(missing_film))
    cards.sort(key=lambda c: (0 if c["defaultTour"] else 1, c["seq"], c["label"]))
    out = {
        "id": "parks-map-library",
        "checked": "2026-08-16",
        "note": "Lower-48 park kits for the virtual map picker. Default tour is the Maine-to-Rockies road. Custom maps hide the road and pin parks at true lat/lon. Films skip title cards (video.start) so autoplay opens on the iconic shot. Alaska, Hawaii, and territories omitted — they do not sit on this CONUS SVG.",
        "omit": [
            {"cardId": "denali", "reason": "Alaska — off this map"},
            {"cardId": "gates-of-arctic", "reason": "Alaska — off this map"},
            {"cardId": "glacier-bay", "reason": "Alaska — off this map"},
            {"cardId": "katmai", "reason": "Alaska — off this map"},
            {"cardId": "kenai-fjords", "reason": "Alaska — off this map"},
            {"cardId": "kobuk-valley", "reason": "Alaska — off this map"},
            {"cardId": "lake-clark", "reason": "Alaska — off this map"},
            {"cardId": "wrangell-st-elias", "reason": "Alaska — off this map"},
            {"cardId": "haleakala", "reason": "Hawaii — off this map"},
            {"cardId": "hawaii-volcanoes", "reason": "Hawaii — off this map"},
            {"cardId": "american-samoa", "reason": "Territory — off this map"},
            {"cardId": "virgin-islands", "reason": "Territory — off this map"},
        ],
        "proj": {"s": round(s, 6), "bx": round(bx, 4), "by": round(by, 4)},
        "cards": cards,
    }
    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(cards)} cards)")
    for c in cards:
        if c["defaultTour"]:
            print(f"  TOUR {c['seq']:2d} {c['cardId']:28s} {c['x']:7.1f},{c['y']:7.1f}  start={c['video']['start']} {c['video']['icon']}")


if __name__ == "__main__":
    main()
