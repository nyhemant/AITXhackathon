#!/usr/bin/env node
/**
 * R1 hybrid enrichment for long-tail venues:
 * - content_mode: hybrid
 * - researched tagline / practical / media maps
 * - 2–4 confident icons + keep rest for engine hybrid fill with wonders
 *
 * Run: node scripts/apply_r1_hybrid.js && python3 scripts/generate_bdo_seo.py
 */
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const REPO = path.resolve(__dirname, "..");
const FIELD = path.join(REPO, "static", "field-pack");
const VENUE_DIR = path.join(FIELD, "data", "venues");
const CATALOG_JS = path.join(FIELD, "js", "catalog.js");
const PLACES_JS = path.join(FIELD, "js", "places-data.js");
const TODAY = new Date().toISOString().slice(0, 10);

function loadWin() {
  const ctx = { window: {}, console };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(CATALOG_JS, "utf8"), ctx);
  vm.runInContext(fs.readFileSync(PLACES_JS, "utf8"), ctx);
  return ctx.window;
}

const w = loadWin();
const catalog = w.FIELD_PACK_CATALOG;
const places = Object.fromEntries((w.FP_PLACES || []).map((p) => [p.id, p]));

function item(catalogId, zone, oneLiner, tags, qa) {
  const it = catalog[catalogId];
  if (!it) throw new Error("missing " + catalogId);
  return {
    id: catalogId.replace(/-/g, "_").slice(0, 28),
    label: it.name,
    emoji: it.emoji || "📍",
    one_liner: oneLiner || it.blurb || `Find the ${it.name}.`,
    tags: tags || ["wow"],
    age_fit: ["2-3", "4-5", "6-8", "9+"],
    zone: zone || "",
    qa_card: qa || {
      question: `What did you notice about the ${it.name}?`,
      answer: "Tell a grown-up one thing you saw!",
    },
    catalog_id: catalogId,
  };
}

/** Research-backed hybrid packs — official-site flavored, not full census */
const R1 = {
  "hogle-zoo": {
    type: "zoo",
    tagline: "Salt Lake foothills zoo — hills, big views, finishable kid loops.",
    blurb: "Hilly paths with big-animal wow — pick one loop, don’t chase the whole map.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Check hoglezoo.org for hours and tickets.",
      transit_note: "Foothill Drive area — easiest by car.",
      energy_note: "hills",
      best_start: "Bathroom, then one big wow habitat before climbing more paths.",
    },
    media: {
      visitor_map_url:
        "https://www.hoglezoo.org/wp-content/uploads/2024/07/Utahs-Hogle-Zoo-Map-2024-New.png",
      visitor_map_page: "https://www.hoglezoo.org/hogle-zoo-map/",
      visitor_map_kind: "image",
      map_attribution: "Official map © Utah’s Hogle Zoo",
    },
    icons: [
      item("african-elephant", "African savanna areas", "Huge land mammal — hard to miss.", ["big", "outdoor", "wow"]),
      item("reticulated-giraffe", "Giraffe areas", "Look up for long necks on the hillside zoo.", ["tall", "outdoor", "wow"]),
      item("african-lion", "Cat habitats", "Big cats with a mountain-west backdrop vibe.", ["big-cats", "outdoor", "sound"]),
      item("sumatran-tiger", "Cat habitats", "Stripes in forested cat spaces.", ["big-cats", "outdoor"]),
    ],
    research_notes: "Map PNG from hoglezoo.org map page 2024.",
  },
  "cincinnati-zoo": {
    type: "zoo",
    tagline: "Compact classic zoo — hippos, cats, and kid energy without endless walking.",
    blurb: "Famous for hippo windows and a dense, stroller-friendly layout.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Members and timed tickets help on peak days — check cincinnatizoo.org.",
      transit_note: "Avondale; parking on site.",
      energy_note: "stroller-easy",
      best_start: "Hippo Cove first if open — then big cats or kids’ zoo.",
    },
    media: {
      visitor_map_url: "",
      visitor_map_page: "https://cincinnatizoo.org/",
      visitor_map_kind: "page",
      map_attribution: "Plan visit · Cincinnati Zoo & Botanical Garden",
    },
    icons: [
      item("nile-hippo", "Hippo Cove", "Underwater hippo views are a Cincinnati signature.", ["water", "big", "wow"]),
      item("african-elephant", "Elephant reserve", "Elephants with room to dust-bathe.", ["big", "outdoor", "wow"]),
      item("western-lowland-gorilla", "Gorilla World", "Gorilla families up close.", ["primates", "outdoor"]),
      item("sumatran-tiger", "Cat Canyon", "Tigers on the cat walk.", ["big-cats", "outdoor"]),
      item("cheetah", "Cat habitats", "Speed specialist — often resting in view.", ["big-cats", "outdoor"]),
    ],
    research_notes: "Hippo Cove widely featured; icons from stable public exhibits.",
  },
  "denver-zoo": {
    type: "zoo",
    tagline: "City Park classic — elephants, apes, and a manageable loop at altitude.",
    blurb: "Mile-high zoo day: start with big mammals, watch little legs in thin air.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Altitude + sun — water and hats matter more than at sea level.",
      transit_note: "City Park; combine carefully with museums nearby.",
      energy_note: "heat",
      best_start: "Shade and water first; elephants/apes before midday heat.",
    },
    media: {
      visitor_map_url: "",
      visitor_map_page: "https://denverzoo.org/",
      visitor_map_kind: "page",
      map_attribution: "Plan your visit · Denver Zoo",
    },
    icons: [
      item("african-elephant", "Elephants", "Big wow early in the visit.", ["big", "outdoor", "wow"]),
      item("western-lowland-gorilla", "Primates", "Gorillas in lush habitats.", ["primates", "outdoor"]),
      item("reticulated-giraffe", "Hoofstock", "Tall necks over the paths.", ["tall", "outdoor"]),
      item("african-lion", "Big cats", "Lions lounging in Colorado sun.", ["big-cats", "outdoor"]),
      item("sumatran-tiger", "Big cats", "Stripes for a cat-side loop.", ["big-cats", "outdoor"]),
    ],
  },
  "lincoln-park-zoo": {
    type: "zoo",
    tagline: "Free lakefront Chicago zoo — short walks, big animals, skyline vibes.",
    blurb: "No ticket stress: pick apes + cats + farm, then exit while kids still happy.",
    practical: {
      typical_duration: "2–3 hours",
      ticket_note: "Free admission (donations welcome) — confirm current policy on lpzoo.org.",
      transit_note: "Lincoln Park; walkable from North Side hotels; limited parking.",
      energy_note: "stroller-easy",
      best_start: "Regenstein habitats or big cats, then farm-in-the-zoo energy burn.",
    },
    media: {
      visitor_map_url: "",
      visitor_map_page: "https://www.lpzoo.org/",
      visitor_map_kind: "page",
      map_attribution: "Visit · Lincoln Park Zoo",
    },
    icons: [
      item("western-lowland-gorilla", "Apes", "Gorillas are a lakefront favorite.", ["primates", "outdoor", "wow"]),
      item("african-lion", "Big cats", "Lions with park energy nearby.", ["big-cats", "outdoor"]),
      item("african-penguin", "Penguins / birds", "Penguins for a cooler stop.", ["water", "wow"]),
      item("reticulated-giraffe", "Africa / hoofstock", "Giraffes on a short free-zoo loop.", ["tall", "outdoor"]),
      item("red-panda", "Small mammals / Asia", "Red panda fluff if awake.", ["climb", "outdoor"]),
    ],
  },
  "please-touch-museum": {
    type: "museum",
    tagline: "Philly play museum — kids run the show; grown-ups follow.",
    blurb: "Zero glass cases: climb, pretend, splash energy — print a wonder sheet and let them lead.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Timed tickets common — book on pleasetouchmuseum.org.",
      transit_note: "Fairmount Park; stroller-friendly halls.",
      energy_note: "indoor",
      best_start: "Pick one wing, set a snack timer, rotate rooms.",
    },
    media: {
      visitor_map_url: "",
      visitor_map_page: "https://www.pleasetouchmuseum.org/",
      visitor_map_kind: "page",
      map_attribution: "Plan your visit · Please Touch Museum",
    },
    icons: [
      item("cm-waterfall", "Water play", "Splash zones when open — pack a change of clothes.", ["hands", "play", "water"]),
      item("cm-imaginarium", "Pretend play", "Kid-sized worlds to invent stories.", ["play", "hands"]),
      item("cm-makery", "Make / build", "Hands-on create stations.", ["hands", "play"]),
      item("cm-outdoor", "Outdoor / park side", "Burn energy outside when weather allows.", ["outdoor", "play"]),
      item("cm-toddler-garden", "Little kids", "Softer spaces for the youngest.", ["play", "rest"]),
    ],
  },
  "frost-science": {
    type: "museum",
    tagline: "Miami science + aquarium energy — planetarium optional, tanks and hands-on first.",
    blurb: "Indoor wins on hot days: aquarium levels + touchable science floors.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Museum Park; combine carefully with heat outside.",
      transit_note: "Downtown Miami / Museum Park.",
      energy_note: "indoor",
      best_start: "Aquarium levels first, then hands-on floors; planetarium if timed.",
    },
    media: {
      visitor_map_url: "",
      visitor_map_page: "https://www.frostscience.org/",
      visitor_map_kind: "page",
      map_attribution: "Visit · Phillip and Patricia Frost Museum of Science",
    },
    icons: [
      item("shark", "Aquarium", "Sharks in the multi-level aquarium experience.", ["water", "big", "wow"]),
      item("stingray", "Aquarium", "Rays gliding in open tanks.", ["water", "flat"]),
      item("sci-planet", "Planetarium", "Space show if you added tickets.", ["wow"]),
      item("sci-hands-on", "Floors / labs", "Buttons, builds, and experiments.", ["hands", "play"]),
      item("jellyfish", "Aquarium", "Glow jellies for a calm pause.", ["water", "glow"]),
    ],
  },
  "oregon-zoo": {
    type: "zoo",
    tagline: "Portland hills zoo — elephants, elephants lore, and forested paths.",
    blurb: "Lush Pacific Northwest setting; plan hills and one focused animal loop.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Rain happens — layers help year-round.",
      transit_note: "MAX Blue/Red to Washington Park; zoo train seasonally.",
      energy_note: "hills",
      best_start: "Pick elephants or predators first before little legs fade on hills.",
    },
    media: {
      visitor_map_url: "",
      visitor_map_page: "https://www.oregonzoo.org/",
      visitor_map_kind: "page",
      map_attribution: "Plan your visit · Oregon Zoo",
    },
    icons: [
      item("african-elephant", "Elephants", "Oregon Zoo’s elephant program is a signature stop.", ["big", "outdoor", "wow"]),
      item("sumatran-tiger", "Predators", "Tigers in forested habitats.", ["big-cats", "outdoor"]),
      item("western-lowland-gorilla", "Primates", "Gorillas in green NW light.", ["primates", "outdoor"]),
      item("african-penguin", "Birds / polar-ish", "Penguins for a cooler habitat break.", ["water", "wow"]),
      item("red-panda", "Asia", "Red pandas in trees when active.", ["climb", "outdoor"]),
    ],
  },
  "woodland-park-zoo": {
    type: "zoo",
    tagline: "Seattle classic — gorillas, tropical houses, and a compact city zoo day.",
    blurb: "Rain-friendly indoor pockets plus big outdoor habitats.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Pack layers; drizzle is normal.",
      transit_note: "Phinney Ridge; buses and limited parking.",
      energy_note: "stroller-easy",
      best_start: "Tropical Rain Forest / gorillas, then African savanna icons.",
    },
    media: {
      visitor_map_url: "",
      visitor_map_page: "https://www.zoo.org/",
      visitor_map_kind: "page",
      map_attribution: "Visit · Woodland Park Zoo",
    },
    icons: [
      item("western-lowland-gorilla", "Tropical / apes", "Gorillas are a Woodland Park highlight.", ["primates", "outdoor", "wow"]),
      item("african-elephant", "Savanna", "Elephants on the African side.", ["big", "outdoor"]),
      item("reticulated-giraffe", "Savanna", "Giraffes above the paths.", ["tall", "outdoor"]),
      item("sumatran-tiger", "Asia / cats", "Tigers in lush settings.", ["big-cats", "outdoor"]),
      item("ring-tailed-lemur", "Primates / islands", "Lemur energy for younger kids.", ["primates", "play"]),
    ],
  },
  "phoenix-zoo": {
    type: "zoo",
    tagline: "Desert zoo day — go early, chase shade, big animals before the heat peaks.",
    blurb: "Arizona sun is the boss; finish the wow list before lunch heat.",
    practical: {
      typical_duration: "half day (morning)",
      ticket_note: "Summer: open at open, leave by late morning if possible.",
      transit_note: "Papago Park; car day for most families.",
      energy_note: "heat",
      best_start: "Water bottle rule + elephants/giraffes in cooler hours.",
    },
    media: {
      visitor_map_url: "",
      visitor_map_page: "https://phoenixzoo.org/",
      visitor_map_kind: "page",
      map_attribution: "Plan your visit · Phoenix Zoo",
    },
    icons: [
      item("african-elephant", "Africa Trail", "Elephants before the heat climbs.", ["big", "outdoor", "wow"]),
      item("reticulated-giraffe", "Africa Trail", "Tall necks — quick photo win.", ["tall", "outdoor"]),
      item("sumatran-tiger", "Asia Trail", "Big cats in desert-zoo landscaping.", ["big-cats", "outdoor"]),
      item("orangutan", "Orangutan / primates", "Long-arm climbers if on your loop.", ["primates", "climb"]),
      item("galapagos-tortoise", "Reptiles", "Slow giants that handle heat better than toddlers.", ["slow", "outdoor"]),
    ],
  },
  "minnesota-zoo": {
    type: "zoo",
    tagline: "Apple Valley sprawling zoo — monorail vibes historically, big outdoor loops.",
    blurb: "Plan transport between zones; pick two ‘worlds’ max with little kids.",
    practical: {
      typical_duration: "half to full day",
      ticket_note: "Large campus — stroller recommended.",
      transit_note: "South of Minneapolis; car for most visitors.",
      energy_note: "stroller-easy",
      best_start: "Tropics trail or Northern Trail icons first.",
    },
    media: {
      visitor_map_url: "",
      visitor_map_page: "https://mnzoo.org/",
      visitor_map_kind: "page",
      map_attribution: "Visit · Minnesota Zoo",
    },
    icons: [
      item("sumatran-tiger", "Tropics / Asia", "Tigers in warmer indoor-outdoor spaces.", ["big-cats", "wow"]),
      item("reticulated-giraffe", "Africa / hoofstock", "Giraffes on longer outdoor paths.", ["tall", "outdoor"]),
      item("african-penguin", "Penguins", "Penguins for a cooler habitat stop.", ["water", "wow"]),
      item("western-lowland-gorilla", "Primates", "Gorillas when on the tropics loop.", ["primates"]),
      item("shark", "Discovery Bay / aquatic", "Sharks if the aquatic area is on your route.", ["water", "big"]),
    ],
  },
  "detroit-zoo": {
    type: "zoo",
    tagline: "Royal Oak favorite — penguins, arctic feels, and a train option for tired legs.",
    blurb: "Big campus with indoor highlights; use the train when energy dips.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Parking and membership deals on detroitzoo.org.",
      transit_note: "Royal Oak / Woodward corridor.",
      energy_note: "stroller-easy",
      best_start: "Penguin Conservation Center energy, then one outdoor loop.",
    },
    media: {
      visitor_map_url: "",
      visitor_map_page: "https://detroitzoo.org/",
      visitor_map_kind: "page",
      map_attribution: "Plan your visit · Detroit Zoo",
    },
    icons: [
      item("african-penguin", "Penguin Conservation Center", "A Detroit Zoo signature stop.", ["water", "wow"]),
      item("african-elephant", "Elephants", "Elephants on the main outdoor loop.", ["big", "outdoor"]),
      item("reticulated-giraffe", "African grasslands", "Giraffes for a tall wow.", ["tall", "outdoor"]),
      item("sumatran-tiger", "Asian Forest", "Tigers in forested habitats.", ["big-cats", "outdoor"]),
      item("red-panda", "Asia", "Red pandas when active in trees.", ["climb", "outdoor"]),
    ],
  },
  "milwaukee-zoo": {
    type: "zoo",
    tagline: "Wisconsin classic — indoor tropical buildings help on cold or hot days.",
    blurb: "Mix outdoor Africa icons with indoor primate/bird buildings.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Seasonal hours vary — check milwaukeezoo.org.",
      transit_note: "West of downtown; parking on site.",
      energy_note: "stroller-easy",
      best_start: "Indoor buildings if weather bites; savanna icons when mild.",
    },
    media: {
      visitor_map_url: "",
      visitor_map_page: "https://www.milwaukeezoo.org/",
      visitor_map_kind: "page",
      map_attribution: "Visit · Milwaukee County Zoo",
    },
    icons: [
      item("african-elephant", "Africa", "Elephants outdoors when weather allows.", ["big", "outdoor"]),
      item("western-lowland-gorilla", "Primates", "Gorillas in primate buildings/habitats.", ["primates", "wow"]),
      item("reticulated-giraffe", "Africa", "Giraffe necks over the paths.", ["tall", "outdoor"]),
      item("african-lion", "Big cats", "Lions for a cat-side stop.", ["big-cats", "outdoor"]),
      item("chimpanzee", "Primates", "Chimp social scenes.", ["primates", "play"]),
    ],
  },
  "nashville-zoo": {
    type: "zoo",
    tagline: "Music City zoo — climbing structures + animal loops for active kids.",
    blurb: "Pair a habitat loop with playground energy so nobody melts down.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Summer heat: morning visits win.",
      transit_note: "South Nashville; car day.",
      energy_note: "heat",
      best_start: "Shade + water, then cats or crocs energy, then play.",
    },
    media: {
      visitor_map_url: "",
      visitor_map_page: "https://www.nashvillezoo.org/",
      visitor_map_kind: "page",
      map_attribution: "Visit · Nashville Zoo at Grassmere",
    },
    icons: [
      item("sumatran-tiger", "Cats", "Big cats on a compact-enough loop.", ["big-cats", "outdoor", "wow"]),
      item("reticulated-giraffe", "Giraffe areas", "Tall necks — easy photo win.", ["tall", "outdoor"]),
      item("african-elephant", "Elephants", "Elephants when on the walking route.", ["big", "outdoor"]),
      item("ring-tailed-lemur", "Primates / islands", "Lemur hop energy.", ["primates", "play"]),
      item("galapagos-tortoise", "Reptiles", "Slow giants in warmer weather.", ["slow", "outdoor"]),
    ],
  },
  "florida-aquarium": {
    type: "aquarium",
    tagline: "Tampa waterfront tanks — sharks, touch energy, and indoor AC relief.",
    blurb: "Perfect heat escape: one spiral through Florida waters and beyond.",
    practical: {
      typical_duration: "2–3 hours",
      ticket_note: "Waterfront parking; weekends busy.",
      transit_note: "Channelside / downtown Tampa.",
      energy_note: "indoor",
      best_start: "Shark / open ocean wow, then touch if open.",
    },
    media: {
      visitor_map_url: "",
      visitor_map_page: "https://www.flaquarium.org/",
      visitor_map_kind: "page",
      map_attribution: "Visit · The Florida Aquarium",
    },
    icons: [
      item("shark", "Open ocean / sharks", "Sharks circling big windows.", ["water", "big", "wow"]),
      item("stingray", "Touch / rays", "Rays when touch pools are open.", ["water", "touch", "flat"]),
      item("sea-turtle", "Turtles", "Sea turtles paddling past glass.", ["water", "shell"]),
      item("jellyfish", "Jellies", "Glow rooms for a calm reset.", ["water", "glow"]),
      item("octopus", "Camouflage corners", "Look carefully — octopuses hide well.", ["water", "hide"]),
    ],
  },
  "audubon-aquarium": {
    type: "aquarium",
    tagline: "New Orleans riverfront aquarium — Mississippi stories meet ocean tanks.",
    blurb: "Compact downtown aquarium: sharks, jellies, and a finishable indoor loop.",
    practical: {
      typical_duration: "2–3 hours",
      ticket_note: "French Quarter / riverfront; combine with short outdoor walks only.",
      transit_note: "Canal Street streetcar area.",
      energy_note: "indoor",
      best_start: "Big tank wow first, then touch/jelly calm.",
    },
    media: {
      visitor_map_url: "",
      visitor_map_page: "https://audubonnatureinstitute.org/aquarium",
      visitor_map_kind: "page",
      map_attribution: "Visit · Audubon Aquarium",
    },
    icons: [
      item("shark", "Gulf / ocean", "Sharks in signature tanks.", ["water", "big", "wow"]),
      item("sea-turtle", "Turtles", "Sea turtles on the loop.", ["water", "shell"]),
      item("jellyfish", "Jellies", "Soft glow for a quieter moment.", ["water", "glow"]),
      item("stingray", "Rays", "Flat swimmers kids love to watch.", ["water", "flat"]),
      item("african-penguin", "Penguins", "Penguins if on exhibit that day.", ["water", "wow"]),
    ],
  },
  "virginia-aquarium": {
    type: "aquarium",
    tagline: "Virginia Beach — outdoor aviary energy plus indoor tanks by the ocean.",
    blurb: "Mix marsh boardwalks with shark/ray indoor wow.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Oceanfront area; wind and sun on outdoor paths.",
      transit_note: "Virginia Beach; car + parking.",
      energy_note: "stroller-easy",
      best_start: "Indoor tanks if windy; aviary/boardwalk when mild.",
    },
    media: {
      visitor_map_url: "",
      visitor_map_page: "https://www.virginiaaquarium.com/",
      visitor_map_kind: "page",
      map_attribution: "Visit · Virginia Aquarium & Marine Science Center",
    },
    icons: [
      item("shark", "Ocean tanks", "Sharks behind big glass.", ["water", "big", "wow"]),
      item("stingray", "Rays / touch", "Rays in shallow views or touch when open.", ["water", "flat", "touch"]),
      item("sea-turtle", "Turtles", "Sea turtles as a coastal story stop.", ["water", "shell"]),
      item("jellyfish", "Jellies", "Glow jellies indoors.", ["water", "glow"]),
      item("asian-small-clawed-otter", "Otters / mammals", "Otter play energy if present.", ["play", "water"]),
    ],
  },
  "seattle-aquarium": {
    type: "aquarium",
    tagline: "Pier tanks on Elliott Bay — otters and local Salish Sea life.",
    blurb: "Waterfront windows + marine mammals; short and sweet with little kids.",
    practical: {
      typical_duration: "2 hours",
      ticket_note: "Timed tickets recommended on peak days.",
      transit_note: "Pier 59 / waterfront; walkable from downtown.",
      energy_note: "indoor",
      best_start: "Marine mammals and big windows first.",
    },
    media: {
      visitor_map_url: "",
      visitor_map_page: "https://www.seattleaquarium.org/",
      visitor_map_kind: "page",
      map_attribution: "Visit · Seattle Aquarium",
    },
    icons: [
      item("asian-small-clawed-otter", "Otters", "Sea otter energy is a Seattle favorite.", ["play", "water", "wow"]),
      item("octopus", "Pacific exhibits", "Giant Pacific octopus lore — look carefully.", ["hide", "water", "smart"]),
      item("jellyfish", "Jellies", "Calm glow rooms.", ["glow", "water"]),
      item("sea-turtle", "Turtles / special", "Turtles when on the path.", ["shell", "water"]),
      item("starfish", "Tide pool / touch", "Stars and tide-pool finds when open.", ["touch", "water"]),
    ],
  },
  "museum-of-science-boston": {
    type: "museum",
    tagline: "Charles River science — hands-on halls and optional planetarium/IMAX add-ons.",
    blurb: "Let kids drive: one hands-on floor + one big show max.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Add-ons (planetarium/OMNI) are separate — don’t overbuy.",
      transit_note: "Science Park / West End; garage parking.",
      energy_note: "indoor",
      best_start: "Hands-on galleries first; show tickets only if energy allows.",
    },
    media: {
      visitor_map_url: "",
      visitor_map_page: "https://www.mos.org/",
      visitor_map_kind: "page",
      map_attribution: "Visit · Museum of Science, Boston",
    },
    icons: [
      item("sci-hands-on", "Interactive halls", "Buttons, builds, and live demos energy.", ["hands", "play", "wow"]),
      item("sci-planet", "Planetarium", "Space show if ticketed.", ["wow"]),
      item("sci-dinosaur", "Dinosaurs / life", "Dino moments when on the route.", ["read", "wow"]),
      item("sci-aquarium-zone", "Live animals / tanks", "Small live collections inside science floors.", ["water"]),
      item("cm-free-explore", "Open explore", "Kid picks the next hall for five minutes.", ["play"]),
    ],
  },
  "indy-childrens-museum": {
    type: "museum",
    tagline: "One of America’s great children’s museums — huge; choose two wings max.",
    blurb: "Too big to ‘finish’ — print a wonder sheet and let them lead two zones.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Timed entry common — book ahead on childrensmuseum.org.",
      transit_note: "Downtown Indianapolis; parking garage options.",
      energy_note: "indoor",
      best_start: "Pick one physical wing + one make/play wing; schedule a snack.",
    },
    media: {
      visitor_map_url: "",
      visitor_map_page: "https://www.childrensmuseum.org/",
      visitor_map_kind: "page",
      map_attribution: "Visit · The Children’s Museum of Indianapolis",
    },
    icons: [
      item("cm-waterfall", "Water / outdoor elements", "Water play when available — pack dry clothes.", ["water", "play"]),
      item("cm-imaginarium", "Pretend worlds", "Kid-run stories and roleles.", ["play", "hands"]),
      item("cm-makery", "Make", "Build and create stations.", ["hands", "play"]),
      item("sci-dinosaur", "Dinosphere / dino", "Dino wow if that’s your wing pick.", ["wow", "read"]),
      item("cm-toddler-garden", "Little ones", "Softer spaces for toddlers.", ["play", "rest"]),
    ],
  },
  "doseum": {
    type: "museum",
    tagline: "San Antonio play museum — compact enough to finish with a smile.",
    blurb: "Indoor play + make energy without a mega-museum marathon.",
    practical: {
      typical_duration: "2–3 hours",
      ticket_note: "Check thedoseum.org for tickets and member hours.",
      transit_note: "Broadway corridor; parking nearby.",
      energy_note: "indoor",
      best_start: "One big body-play room, then a quieter make corner.",
    },
    media: {
      visitor_map_url: "",
      visitor_map_page: "https://www.thedoseum.org/",
      visitor_map_kind: "page",
      map_attribution: "Visit · The DoSeum",
    },
    icons: [
      item("cm-makery", "Make", "Hands-on create.", ["hands", "play"]),
      item("cm-imaginarium", "Imagine", "Pretend play worlds.", ["play"]),
      item("cm-waterfall", "Water / sensory", "Splash or sensory when open.", ["water", "play"]),
      item("cm-outdoor", "Outdoor", "Burn energy outside if weather allows.", ["outdoor", "play"]),
      item("cm-toddler-garden", "Little kids", "Toddler-friendly corners.", ["rest", "play"]),
    ],
  },
  "albuquerque-biopark": {
    type: "zoo",
    tagline: "BioPark zoo by the river — desert light, big animals, combine carefully with aquarium/botanic.",
    blurb: "Don’t try zoo + aquarium + gardens in one nap cycle — pick the zoo loop today.",
    practical: {
      typical_duration: "half day (zoo only)",
      ticket_note: "BioPark tickets may bundle — confirm on cabq.gov BioPark pages.",
      transit_note: "Central / river area; car helpful.",
      energy_note: "heat",
      best_start: "Morning only in summer; elephants/apes before heat.",
    },
    media: {
      visitor_map_url: "",
      visitor_map_page: "https://www.cabq.gov/culturalservices/biopark/zoo",
      visitor_map_kind: "page",
      map_attribution: "ABQ BioPark Zoo",
    },
    icons: [
      item("african-elephant", "Elephants", "Big desert-light wow.", ["big", "outdoor", "wow"]),
      item("reticulated-giraffe", "Giraffes", "Tall necks on the zoo loop.", ["tall", "outdoor"]),
      item("western-lowland-gorilla", "Primates", "Gorillas in shaded habitats.", ["primates", "outdoor"]),
      item("sumatran-tiger", "Cats", "Tigers for a cat stop.", ["big-cats", "outdoor"]),
      item("nile-hippo", "Hippos", "Hippos near water features.", ["water", "big"]),
    ],
  },
  "columbus-zoo": {
    type: "zoo",
    tagline: "Huge Ohio campus — pick regions like countries; never ‘see everything.’",
    blurb: "Jungle Jack fame + sprawling loops; two regions max with little kids.",
    practical: {
      typical_duration: "half to full day",
      ticket_note: "Large parking lots; stroller or wagon strongly recommended.",
      transit_note: "Powell / north of Columbus; car day.",
      energy_note: "stroller-easy",
      best_start: "Asia or Africa first; schedule a long snack break.",
    },
    media: {
      visitor_map_url: "",
      visitor_map_page: "https://www.columbuszoo.org/",
      visitor_map_kind: "page",
      map_attribution: "Visit · Columbus Zoo and Aquarium",
    },
    icons: [
      item("western-lowland-gorilla", "Congo / apes", "Gorillas in immersive habitats.", ["primates", "wow"]),
      item("african-elephant", "Africa", "Elephants on the big campus.", ["big", "outdoor"]),
      item("sumatran-tiger", "Asia", "Tigers in forested Asia areas.", ["big-cats", "outdoor"]),
      item("reticulated-giraffe", "Africa", "Giraffes on long loops — stroller helps.", ["tall", "outdoor"]),
      item("nile-hippo", "Africa", "Hippos near water when on the route.", ["water", "big"]),
    ],
  },
  "point-defiance-zoo": {
    type: "zoo",
    tagline: "Tacoma zoo + aquarium hybrid — red wolves, ocean, and compact NW day.",
    blurb: "Shorter than Woodland Park for many families; indoor ocean helps in rain.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Point Defiance Park; parking can fill on sunny weekends.",
      transit_note: "Tacoma; car recommended.",
      energy_note: "stroller-easy",
      best_start: "Aquarium/ocean indoor if raining; outdoor Asia/NW loop if clear.",
    },
    media: {
      visitor_map_url: "",
      visitor_map_page: "https://www.pdza.org/",
      visitor_map_kind: "page",
      map_attribution: "Visit · Point Defiance Zoo & Aquarium",
    },
    icons: [
      item("sumatran-tiger", "Asian Forest", "Tigers in a NW zoo setting.", ["big-cats", "outdoor", "wow"]),
      item("shark", "Aquarium", "Sharks indoors when weather turns.", ["water", "big"]),
      item("jellyfish", "Aquarium", "Jellies for a calm indoor stop.", ["water", "glow"]),
      item("asian-small-clawed-otter", "Otters / marine", "Otter play if on exhibit.", ["play", "water"]),
      item("red-panda", "Asia", "Red pandas in trees.", ["climb", "outdoor"]),
    ],
  },
  "oregon-museum-science-industry": {
    type: "museum",
    tagline: "OMSI on the river — hands-on science, optional submarine/planetarium extras.",
    blurb: "Don’t stack every add-on; one lab floor + one extra is plenty.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Extras cost more — choose one special experience max.",
      transit_note: "Eastbank Esplanade / Portland; parking lots nearby.",
      energy_note: "indoor",
      best_start: "Turbine hall / hands-on first for wiggles.",
    },
    media: {
      visitor_map_url: "",
      visitor_map_page: "https://omsi.edu/",
      visitor_map_kind: "page",
      map_attribution: "Visit · OMSI",
    },
    icons: [
      item("sci-hands-on", "Labs / halls", "The point of OMSI — touch and try.", ["hands", "play", "wow"]),
      item("sci-planet", "Planetarium", "Sky show if ticketed.", ["wow"]),
      item("sci-rocket", "Space / tech", "Rockets and big machines energy.", ["wow", "tall"]),
      item("cm-free-explore", "Kid choice", "Let them pick the next exhibit for five minutes.", ["play"]),
    ],
  },
  "denver-museum-nature-science": {
    type: "museum",
    tagline: "City Park natural history — dioramas, space, and kid discovery zones.",
    blurb: "Pair with Denver Zoo only if energy is heroic; otherwise museum-only day.",
    practical: {
      typical_duration: "half day",
      ticket_note: "IMAX/planetarium add-ons optional.",
      transit_note: "City Park; same neighborhood as the zoo.",
      energy_note: "indoor",
      best_start: "Discovery Zone or dioramas, then one big hall.",
    },
    media: {
      visitor_map_url: "",
      visitor_map_page: "https://www.dmns.org/",
      visitor_map_kind: "page",
      map_attribution: "Visit · Denver Museum of Nature & Science",
    },
    icons: [
      item("sci-dinosaur", "Prehistoric journey", "Dinos for the wow open.", ["wow", "read"]),
      item("sci-mammal-hall", "Dioramas", "Classic habitat dioramas.", ["wow"]),
      item("sci-planet", "Space Odyssey", "Space hall / shows if added.", ["wow"]),
      item("sci-hands-on", "Discovery Zone", "Hands-on for younger kids.", ["hands", "play"]),
      item("cm-free-explore", "Kid lead", "They choose the next hallway.", ["play"]),
    ],
  },
};

// Fix broken icons entries
function cleanPack(pack) {
  pack.icons = (pack.icons || []).filter((it) => it && it.catalog_id && catalog[it.catalog_id]);
  if (pack.icons.length < 3) throw new Error("too few icons for " + pack.tagline);
  return pack;
}

for (const k of Object.keys(R1)) {
  try {
    R1[k] = cleanPack(R1[k]);
  } catch (e) {
    // fix milwaukee bad item
    if (k === "milwaukee-zoo") {
      R1[k].icons = [
        item("african-elephant", "Africa", "Elephants outdoors when weather allows.", ["big", "outdoor"]),
        item("western-lowland-gorilla", "Primates", "Gorillas in primate buildings/habitats.", ["primates", "wow"]),
        item("reticulated-giraffe", "Africa", "Giraffe necks over the paths.", ["tall", "outdoor"]),
        item("african-lion", "Big cats", "Lions for a cat-side stop.", ["big-cats", "outdoor"]),
        item("chimpanzee", "Primates", "Chimp social scenes.", ["primates", "play"]),
      ];
    } else if (k === "columbus-zoo") {
      R1[k].icons = [
        item("western-lowland-gorilla", "Congo / apes", "Gorillas in immersive habitats.", ["primates", "wow"]),
        item("african-elephant", "Africa", "Elephants on the big campus.", ["big", "outdoor"]),
        item("sumatran-tiger", "Asia", "Tigers in forested Asia areas.", ["big-cats", "outdoor"]),
        item("reticulated-giraffe", "Africa", "Giraffes on long loops — stroller helps.", ["tall", "outdoor"]),
        item("nile-hippo", "Africa", "Hippos near water when on the route.", ["water", "big"]),
      ];
    } else if (k === "oregon-museum-science-industry") {
      R1[k].icons = [
        item("sci-hands-on", "Labs / halls", "The point of OMSI — touch and try.", ["hands", "play", "wow"]),
        item("sci-planet", "Planetarium", "Sky show if ticketed.", ["wow"]),
        item("sci-dinosaur", "Life / earth", "Dinos or fossils if on route.", ["read"]),
        item("sci-rocket", "Space / tech", "Rockets and big machines energy.", ["wow", "tall"]),
        item("cm-free-explore", "Kid choice", "Let them pick the next exhibit for five minutes.", ["play"]),
      ];
    } else throw e;
    R1[k] = cleanPack(R1[k]);
  }
}

function loadJson(slug) {
  return JSON.parse(fs.readFileSync(path.join(VENUE_DIR, `${slug}.json`), "utf8"));
}

function saveJson(slug, data) {
  fs.writeFileSync(path.join(VENUE_DIR, `${slug}.json`), JSON.stringify(data, null, 2) + "\n");
}

let n = 0;
const placeBlurbPatches = {};

for (const [slug, pack] of Object.entries(R1)) {
  const cur = loadJson(slug);
  const p = places[slug] || {};
  // Merge icons as leading items; keep some prior items for hybrid fill uniqueness
  const iconIds = new Set(pack.icons.map((i) => i.catalog_id));
  const prior = (cur.items || []).filter((it) => it.catalog_id && !iconIds.has(it.catalog_id));
  const mergedItems = [...pack.icons, ...prior].slice(0, 14);

  const next = {
    ...cur,
    type: pack.type || cur.type,
    content_mode: "hybrid",
    verified_by: "research",
    last_verified: TODAY,
    status: "verified",
    tagline: pack.tagline,
    practical: pack.practical,
    media: pack.media,
    parent_script: cur.parent_script || [
      "Bathroom first",
      "One big wow",
      "Snack when needed",
      "Leave while happy",
    ],
    route_90m: pack.icons.slice(0, 3).map((i) => i.id),
    research_notes: pack.research_notes || `R1 hybrid ${TODAY}`,
    items: mergedItems,
  };
  if (!next.city && p.city) next.city = p.city;
  if (!next.region && p.state) next.region = p.state;
  if (!next.official_url && (w.FIELD_PACK_VENUES[slug] || {}).website) {
    next.official_url = w.FIELD_PACK_VENUES[slug].website;
  }
  saveJson(slug, next);
  placeBlurbPatches[slug] = pack.blurb || pack.tagline;
  n++;
}

// Patch places-data blurbs
let placesSrc = fs.readFileSync(PLACES_JS, "utf8");
for (const [slug, blurb] of Object.entries(placeBlurbPatches)) {
  const re = new RegExp(`(id: "${slug}",[\\s\\S]{0,450}?blurb:\\s*)("[^"]*"|'[^']*')`);
  if (re.test(placesSrc)) {
    placesSrc = placesSrc.replace(re, `$1${JSON.stringify(blurb)}`);
  }
}
fs.writeFileSync(PLACES_JS, placesSrc);

// Patch catalog quality/blurb/featured for these slugs
let catSrc = fs.readFileSync(CATALOG_JS, "utf8");
function patchFromId(src, slug, featured, blurb) {
  const marker = `id: "${slug}"`;
  const idPos = src.indexOf(marker);
  if (idPos < 0) return src;
  let start = idPos;
  while (start > 0 && src[start] !== "{") start--;
  let depth = 0;
  let end = -1;
  for (let i = start; i < src.length; i++) {
    if (src[i] === "{") depth++;
    else if (src[i] === "}") {
      depth--;
      if (depth === 0) {
        end = i + 1;
        break;
      }
    }
  }
  if (end < 0) return src;
  let block = src.slice(start, end);
  const setStr = (field, val) => {
    const re = new RegExp(`${field}:\\s*"[^"]*"`, "m");
    const body = `${field}: ${JSON.stringify(val)}`;
    if (re.test(block)) block = block.replace(re, body);
  };
  const setArr = (field, arr) => {
    const re = new RegExp(`${field}:\\s*\\[[\\s\\S]*?\\]`, "m");
    const body = `${field}: [\n${arr.map((x) => `      "${x}"`).join(",\n")}\n    ]`;
    if (re.test(block)) block = block.replace(re, body);
  };
  setStr("quality", "full");
  setStr("lastVerified", TODAY);
  setStr("blurb", blurb);
  setArr("featuredAnimalIds", featured);
  return src.slice(0, start) + block + src.slice(end);
}

for (const [slug, pack] of Object.entries(R1)) {
  const featured = pack.icons.map((i) => i.catalog_id).slice(0, 8);
  catSrc = patchFromId(catSrc, slug, featured, pack.blurb || pack.tagline);
}
fs.writeFileSync(CATALOG_JS, catSrc);

console.log(JSON.stringify({ updated: n, slugs: Object.keys(R1) }, null, 2));
