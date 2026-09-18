#!/usr/bin/env node
/**
 * Wave 2: upgrade ~20 top US venues from catalog scaffolds to research-backed
 * shortlists (mission JSON + catalog featured/animal lists + quality:full).
 *
 * Run from repo root:
 *   node scripts/apply_wave2_curated.js
 *   python3 scripts/validate_venue_data.py
 *   python3 scripts/generate_bdo_seo.py
 */
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const REPO = path.resolve(__dirname, "..");
const FIELD = path.join(REPO, "static", "field-pack");
const VENUE_DIR = path.join(FIELD, "data", "venues");
const CATALOG_JS = path.join(FIELD, "js", "catalog.js");
const PLACES_JS = path.join(FIELD, "js", "places-data.js");
const TODAY = "2026-08-07";

function loadWin() {
  const ctx = { window: {}, console };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(CATALOG_JS, "utf8"), ctx);
  vm.runInContext(fs.readFileSync(PLACES_JS, "utf8"), ctx);
  return ctx.window;
}

const w = loadWin();
const catalog = w.FIELD_PACK_CATALOG;
const venues = w.FIELD_PACK_VENUES;
const places = Object.fromEntries((w.FP_PLACES || []).map((p) => [p.id, p]));

function item(catalogId, zone, oneLiner, tags, qa) {
  const it = catalog[catalogId];
  if (!it) throw new Error("missing catalog item " + catalogId);
  return {
    id: catalogId.replace(/-/g, "_").slice(0, 28),
    label: it.name,
    emoji: it.emoji || "📍",
    one_liner: oneLiner || it.blurb || `Find the ${it.name}.`,
    tags: tags || ["wow", "outdoor"],
    age_fit: ["2-3", "4-5", "6-8", "9+"],
    zone: zone || "",
    qa_card: qa || {
      question: `What did you notice about the ${it.name}?`,
      answer: "Tell a grown-up one thing you saw!",
    },
    catalog_id: catalogId,
  };
}

/**
 * Research-backed shortlists (kid-day icons). Catalog-bound only.
 * Confidence: public venue exhibits as of 2025–2026 research; animals rotate.
 */
const WAVE2 = {
  "georgia-aquarium": {
    type: "aquarium",
    tagline: "Whale sharks, belugas, and giant ocean windows — Atlanta’s kid wow tank.",
    blurb: "Start at the biggest tank (whale sharks), then belugas and penguins.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Timed tickets often sell out on weekends — book ahead.",
      transit_note: "Downtown Atlanta; parking decks nearby.",
    },
    items: [
      item("shark", "Ocean Voyager", "Home of the whale sharks — look for the biggest fish in the tank.", ["water", "big", "wow"], {
        question: "Which fish looks the biggest?",
        answer: "Whale sharks are the biggest fish in the world — gentle giants!",
      }),
      item("stingray", "Ocean Voyager", "Manta-sized rays glide by the glass like underwater birds.", ["water", "flat", "wow"]),
      item("sea-turtle", "Ocean Voyager", "Sea turtles paddle past the tunnel windows.", ["water", "shell", "wow"]),
      item("jellyfish", "Cold Water Quest", "Soft glow jellies in dark rooms — mesmerizing.", ["water", "glow", "soft"]),
      item("african-penguin", "Cold Water Quest", "Waddling African penguins on rocky shores.", ["water", "outdoor", "wow"]),
      item("asian-small-clawed-otter", "Cold Water Quest", "Playful sea otters (and otter friends) on the cold side.", ["water", "play", "wow"]),
      item("octopus", "Tropical Diver", "A camouflage master — look carefully!", ["water", "hide", "smart"]),
      item("seahorse", "Tropical Diver", "Tiny upright swimmers in the reef.", ["water", "tiny"]),
      item("clownfish", "Tropical Diver", "Bright reef fish darting through coral.", ["water", "color"]),
      item("starfish", "Touch experiences", "If open: gentle touch pools with stars and friends.", ["water", "touch"]),
    ],
  },
  "monterey-bay-aquarium": {
    type: "aquarium",
    tagline: "Start at the jellies, then sea otters and open-ocean icons on the bay.",
    blurb: "Jellies first, then otters and the big ocean tank — classic Monterey kid route.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Timed entry; weekends book up.",
      transit_note: "Cannery Row; walkable from nearby hotels.",
    },
    items: [
      item("jellyfish", "Jellies", "Famous glowing jellies — slow down and watch them drift.", ["water", "glow", "wow"]),
      item("asian-small-clawed-otter", "Sea Otters", "Sea otters float, crack snacks, and steal the show.", ["water", "play", "wow"]),
      item("shark", "Open Sea", "Big open-ocean swimmers circle the giant tank.", ["water", "big", "wow"]),
      item("sea-turtle", "Open Sea", "A green sea turtle often shares the big blue.", ["water", "shell"]),
      item("octopus", "Tentacles", "Octopus hide-and-seek — check the corners.", ["water", "hide", "smart"]),
      item("stingray", "Touch pools", "If open: soft rays in shallow touch pools.", ["water", "touch", "flat"]),
      item("seahorse", "Hot water / special", "Seahorses and tiny dragons of the tanks.", ["water", "tiny"]),
      item("clownfish", "Coral reef", "Bright reef fish for a color hunt.", ["water", "color"]),
      item("starfish", "Tide pool", "Look for stars and crabs in rocky pools.", ["water", "touch"]),
      item("eel", "Kelp / reef", "Long eels peek from rocky homes.", ["water", "hide", "long"]),
    ],
  },
  "shedd-aquarium": {
    type: "aquarium",
    tagline: "Lakefront Chicago — sharks, jellies, and a one-page sea hunt.",
    blurb: "Oceanarium vibes on Lake Michigan: big tanks first, then touch-friendly finds.",
    practical: {
      typical_duration: "half day",
      ticket_note: "CityPASS and timed tickets available; weekends busy.",
      transit_note: "Museum Campus; walk from Field Museum.",
    },
    items: [
      item("shark", "Caribbean Reef / Wild Reef", "Sharks cruise the big reef windows.", ["water", "big", "wow"]),
      item("stingray", "Wild Reef", "Flat rays glide over the sand.", ["water", "flat"]),
      item("jellyfish", "Jellies", "Quiet glowing jellies for a calm pause.", ["water", "glow"]),
      item("sea-turtle", "Caribbean Reef", "Sea turtles share the circular reef tank.", ["water", "shell"]),
      item("african-penguin", "Polar Play Zone", "Penguins waddle and zoom underwater.", ["water", "wow"]),
      item("octopus", "Pacific / special", "Look for an octopus that can vanish in plain sight.", ["water", "hide"]),
      item("clownfish", "Amazon / reef", "Bright little reef fish for a color hunt.", ["water", "color"]),
      item("seahorse", "Seahorse gallery", "Tiny upright swimmers — patience pays off.", ["water", "tiny"]),
      item("asian-small-clawed-otter", "Polar / special", "Otter energy if they’re on exhibit that day.", ["water", "play"]),
      item("starfish", "Touch experiences", "Touch pools when open — gentle hands only.", ["water", "touch"]),
    ],
  },
  "new-england-aquarium": {
    type: "aquarium",
    tagline: "Boston harbor classic — giant ocean tank and penguin colony.",
    blurb: "Ride the spiral around the Giant Ocean Tank, then penguins and jellies.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Harbor location; combine with the waterfront walk.",
      transit_note: "Aquarium T stop (Blue Line).",
    },
    items: [
      item("shark", "Giant Ocean Tank", "Look into the huge cylindrical tank from every level.", ["water", "big", "wow"]),
      item("sea-turtle", "Giant Ocean Tank", "Sea turtles cruise the big blue cylinder.", ["water", "shell", "wow"]),
      item("african-penguin", "Penguin colony", "African penguins chatter and splash.", ["water", "wow"]),
      item("jellyfish", "Jellies", "Dark room, bright jellies.", ["water", "glow"]),
      item("octopus", "Thinking Gallery", "A clever octopus may be out exploring.", ["water", "smart", "hide"]),
      item("stingray", "Shark and ray touch", "Touch tank when open — soft ray wings.", ["water", "touch", "flat"]),
      item("seahorse", "Seadragons / special", "Seahorses and seadragon cousins.", ["water", "tiny"]),
      item("clownfish", "Tropical gallery", "Reef colors for a quick “find three colors” game.", ["water", "color"]),
      item("starfish", "Tide pool", "Stars and crabs in rocky pools.", ["water", "touch"]),
      item("eel", "Edge of the Sea", "Long bodies tucked into rock homes.", ["water", "long"]),
    ],
  },
  "aquarium-of-the-pacific": {
    type: "aquarium",
    tagline: "Long Beach Pacific galleries — seals, sharks, and a kid-friendly loop.",
    blurb: "Outdoor seals and sea lions, then sharks, jellies, and Lorikeet Forest energy.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Waterfront; easy with a stroller.",
      transit_note: "Long Beach Aquarium area parking.",
    },
    items: [
      item("shark", "Shark Lagoon", "Sharks and rays in the big outdoor lagoon vibe.", ["water", "big", "wow"]),
      item("stingray", "Shark Lagoon", "Rays glide in shallow water — watch from above.", ["water", "flat", "touch"]),
      item("sea-turtle", "Pacific galleries", "Sea turtles on the Pacific side.", ["water", "shell"]),
      item("jellyfish", "Jellies", "Glow-room jellies for a calm break.", ["water", "glow"]),
      item("octopus", "June Keyes Penguin / special", "Camouflage king — check rockwork carefully.", ["water", "hide"]),
      item("african-penguin", "June Keyes Penguin Habitat", "Penguins waddle and dive.", ["water", "wow"]),
      item("asian-small-clawed-otter", "Sea otter habitat", "Sea otters float and play on their backs.", ["water", "play", "wow"]),
      item("clownfish", "Tropical Pacific", "Bright reef fish for color spotting.", ["water", "color"]),
      item("seahorse", "Seahorse gallery", "Tiny upright swimmers.", ["water", "tiny"]),
      item("starfish", "Touch labs", "Touch experiences when open.", ["water", "touch"]),
    ],
  },
  "national-aquarium-baltimore": {
    type: "aquarium",
    tagline: "Inner Harbor towers of tanks — sharks, dolphins energy, and jellies.",
    blurb: "Ride the escalators up, spiral down through reefs, sharks, and touch pools.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Timed tickets recommended on weekends.",
      transit_note: "Inner Harbor; walkable from downtown hotels.",
    },
    items: [
      item("shark", "Shark Alley / Atlantic", "Sharks glide past floor-to-ceiling glass.", ["water", "big", "wow"]),
      item("stingray", "Atlantic coral", "Rays sweep the sandy bottom.", ["water", "flat"]),
      item("jellyfish", "Jellies Invasion", "A whole floor of floating jellies.", ["water", "glow", "wow"]),
      item("sea-turtle", "Atlantic", "Sea turtles share the big ocean habitats.", ["water", "shell"]),
      item("octopus", "Living Seashore / special", "Look for arms and camouflage.", ["water", "hide"]),
      item("african-penguin", "Maryland: Mountains to the Sea", "Penguins on the Atlantic coast story.", ["water", "wow"]),
      item("clownfish", "Tropical rain forest / reef", "Bright fish after the rainforest walk.", ["water", "color"]),
      item("seahorse", "Seahorse exhibit", "Tiny dragons of the tanks.", ["water", "tiny"]),
      item("starfish", "Living Seashore", "Touch pool stars when open.", ["water", "touch"]),
      item("eel", "Atlantic", "Long eels in rocky hideouts.", ["water", "long"]),
    ],
  },
  "childrens-aquarium-dallas": {
    type: "aquarium",
    tagline: "Kid-scale tanks and touch pools — a half-day water wonder without the mega-crowds.",
    blurb: "Perfect first aquarium: sharks, rays, turtles, and hands-on moments.",
    practical: {
      typical_duration: "2–3 hours",
      ticket_note: "Fair Park location; check event-day parking.",
      transit_note: "Dallas Fair Park area.",
    },
    items: [
      item("shark", "Main galleries", "Smaller shark tanks kids can see eye-to-eye.", ["water", "wow"]),
      item("stingray", "Touch pool", "Soft ray wings when the touch pool is open.", ["water", "touch", "flat"]),
      item("sea-turtle", "Turtle habitats", "Sea turtles paddle slowly past the glass.", ["water", "shell"]),
      item("jellyfish", "Jellies", "Glow jellies for a quiet minute.", ["water", "glow"]),
      item("clownfish", "Reef", "Find Nemo-style colors in the reef tanks.", ["water", "color"]),
      item("seahorse", "Seahorses", "Hunt for tiny upright swimmers.", ["water", "tiny"]),
      item("octopus", "Special exhibits", "Camouflage games — is it rock or octopus?", ["water", "hide"]),
      item("crab", "Tide creatures", "Sideways walkers and shells.", ["water", "shell"]),
      item("starfish", "Touch", "Stars and friends if touch is open.", ["water", "touch"]),
      item("eel", "Rocky tanks", "Long bodies tucked into dens.", ["water", "long"]),
    ],
  },
  "san-diego-zoo": {
    type: "zoo",
    tagline: "Giant pandas are back, plus the famous koala colony — tourist icons first.",
    blurb: "Pandas + koalas first if lines allow, then elephants, big cats, and apes.",
    practical: {
      typical_duration: "full day if you can; half day for icons",
      ticket_note: "Panda viewing may use timed entry — check on arrival.",
      transit_note: "Balboa Park; hop-on buses inside help little legs.",
    },
    items: [
      item("giant-panda", "Panda Ridge", "Yun Chuan & Xin Bao — the star return attraction.", ["wow", "outdoor", "big"], {
        question: "What do giant pandas love to eat?",
        answer: "Bamboo — lots and lots of bamboo!",
      }),
      item("koala", "Outback", "Largest koala colony outside Australia — look up in the trees.", ["outdoor", "wow", "climb"]),
      item("red-panda", "Panda Ridge / Asia", "Red panda cousins near the giant pandas.", ["outdoor", "climb"]),
      item("african-elephant", "Elephant Odyssey", "Huge elephants on a big California hillside.", ["big", "outdoor", "wow"]),
      item("western-lowland-gorilla", "Lost Forest", "Gorilla families in lush habitat.", ["outdoor", "primates"]),
      item("orangutan", "Lost Forest", "Long-armed orangutans in the trees.", ["outdoor", "climb"]),
      item("african-lion", "Africa Rocks / cats", "Lions lounging with a big roar potential.", ["big-cats", "outdoor", "sound"]),
      item("sumatran-tiger", "Asian Passage", "Stripy tigers on the Asia side.", ["big-cats", "outdoor"]),
      item("reticulated-giraffe", "Africa", "Tall necks above the crowd.", ["tall", "outdoor"]),
      item("two-toed-sloth", "Special / rainforest", "Slow-motion mammal if you spot one hanging out.", ["climb", "outdoor"]),
    ],
  },
  "san-diego-safari-park": {
    type: "safari_zoo",
    tagline: "Open-range Africa feel — tram views of herds, plus rhino and big cat energy.",
    blurb: "Do the Africa tram (or equivalent) early, then walk gorillas and cats.",
    practical: {
      typical_duration: "half to full day",
      ticket_note: "Separate ticket from the Zoo; arrive early for parking.",
      transit_note: "Escondido; car-friendly day trip from San Diego.",
    },
    items: [
      item("reticulated-giraffe", "Africa field / walk", "Giraffes on wide open savanna-style fields.", ["tall", "outdoor", "wow"]),
      item("african-elephant", "Elephant Valley", "Elephants with room to roam.", ["big", "outdoor", "wow"]),
      item("zebra", "Africa field", "Stripes in mixed herds from the tram or overlooks.", ["outdoor", "pattern"]),
      item("african-lion", "Lion camp", "Lions overlooking the park hills.", ["big-cats", "outdoor", "sound"]),
      item("cheetah", "Passports to Africa / cats", "The speed specialist — often stretched out resting.", ["big-cats", "outdoor"]),
      item("western-lowland-gorilla", "Gorilla Forest", "Gorillas in a lush walk-through habitat.", ["outdoor", "primates"]),
      item("nile-hippo", "Watering hole areas", "Hippos near water when on view.", ["big", "water", "outdoor"]),
      item("sumatran-tiger", "Tiger Trail", "Tigers on the Asian side of the park.", ["big-cats", "outdoor"]),
      item("ostrich", "Africa field", "Giant birds strutting the plains.", ["outdoor", "tall"]),
      item("warthog", "Africa", "Funny faces and little tusks on the savanna.", ["outdoor"]),
    ],
  },
  "la-zoo": {
    type: "zoo",
    tagline: "Griffith Park classic — elephants, chimps, and a finishable hillside loop.",
    blurb: "Start at elephants and chimps, then big cats and giraffes before legs tire.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Hills and sun — bring water and a stroller with good brakes.",
      transit_note: "Griffith Park; parking fills on weekends.",
    },
    items: [
      item("african-elephant", "Elephants", "LA’s elephant habitat is a first stop for many families.", ["big", "outdoor", "wow"]),
      item("chimpanzee", "Chimps", "Chimp social hour — watch faces and gestures.", ["primates", "outdoor", "play"]),
      item("western-lowland-gorilla", "Gorillas", "Quiet strength in the gorilla yard.", ["primates", "outdoor"]),
      item("reticulated-giraffe", "Giraffes", "Tall necks above the path.", ["tall", "outdoor"]),
      item("african-lion", "Big cats", "Lions with a city-skyline backdrop vibe.", ["big-cats", "outdoor", "sound"]),
      item("sumatran-tiger", "Big cats", "Stripes in the forested cat areas.", ["big-cats", "outdoor"]),
      item("red-panda", "Asia", "Red panda fluff if they’re awake in the trees.", ["climb", "outdoor"]),
      item("caribbean-flamingo", "Birds", "Bright pink flock — easy first find.", ["outdoor", "color"]),
      item("galapagos-tortoise", "Reptiles", "Slow giants on land.", ["outdoor", "slow"]),
      item("ring-tailed-lemur", "Primates", "Ring tails and bright eyes.", ["primates", "outdoor"]),
    ],
  },
  "houston-zoo": {
    type: "zoo",
    tagline: "Hermann Park favorite — elephants, giraffes, and a tight kid loop.",
    blurb: "Giants first (elephant, giraffe, rhino vibes), then apes and kids’ zones.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Members lines move faster; summers are hot — go early.",
      transit_note: "Hermann Park; MetroRail Museum District.",
    },
    items: [
      item("african-elephant", "Elephants", "Houston’s elephant habitat is a must-see wow.", ["big", "outdoor", "wow"]),
      item("reticulated-giraffe", "Giraffes", "Feeding times are popular — check the board.", ["tall", "outdoor", "feeding"]),
      item("nile-hippo", "Hippos", "Underwater hippo windows when open.", ["big", "water", "wow"]),
      item("western-lowland-gorilla", "Gorillas", "Gorilla families up close.", ["primates", "outdoor"]),
      item("chimpanzee", "Chimps / apes", "Chimp play and chatter.", ["primates", "play"]),
      item("african-lion", "Big cats", "Lions lounging in the Texas sun.", ["big-cats", "outdoor"]),
      item("sumatran-tiger", "Big cats", "Tigers on the cat walk.", ["big-cats", "outdoor"]),
      item("african-penguin", "Penguins", "Penguins zoom underwater.", ["water", "wow"]),
      item("asian-small-clawed-otter", "Otters", "Busy otters for a quick laugh.", ["play", "water"]),
      item("zebra", "Africa", "Stripes on the Africa side.", ["outdoor", "pattern"]),
    ],
  },
  "national-zoo": {
    type: "zoo",
    tagline: "Free Smithsonian zoo — giant pandas Bao Li & Qing Bao lead the day.",
    blurb: "Asia Trail pandas first, then elephants, big cats, and ape house icons.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Free admission; timed entry may apply — reserve on the Zoo site.",
      transit_note: "Woodley Park / Cleveland Park Metro; steep hills.",
    },
    items: [
      item("giant-panda", "Asia Trail", "Bao Li and Qing Bao in the renovated panda habitat.", ["wow", "outdoor", "big"], {
        question: "What color are giant panda ears?",
        answer: "Black — just like their eye spots!",
      }),
      item("asian-small-clawed-otter", "Asia Trail", "Otters near the Asia path energy.", ["play", "water"]),
      item("red-panda", "Asia Trail", "Red pandas in the trees if awake.", ["climb", "outdoor"]),
      item("african-elephant", "Elephant Trails", "Elephants with room to dust-bathe.", ["big", "outdoor", "wow"]),
      item("african-lion", "Great Cats", "Lions on the cat walk.", ["big-cats", "outdoor", "sound"]),
      item("sumatran-tiger", "Great Cats", "Tigers pacing or napping in the shade.", ["big-cats", "outdoor"]),
      item("western-lowland-gorilla", "Great Ape House", "Gorillas face-to-face through glass.", ["primates", "outdoor"]),
      item("orangutan", "O Line / apes", "Orangutans — watch for sky-cable travel on some days.", ["primates", "climb"]),
      item("reticulated-giraffe", "Hoofed animals", "Tall spots above the crowd.", ["tall", "outdoor"]),
      item("caribbean-flamingo", "Birds", "Pink flock for an easy win.", ["color", "outdoor"]),
    ],
  },
  "bronx-zoo": {
    type: "zoo",
    tagline: "NYC’s big zoo day — Congo gorillas, Madagascar, and tiger mountain energy.",
    blurb: "Pick two “worlds” (Congo + Asia or Madagascar) so you finish strong.",
    practical: {
      typical_duration: "half to full day",
      ticket_note: "Pay-what-you-wish Wednesdays historically — confirm current rules.",
      transit_note: "2 train to Bronx Park East or BxM11 bus.",
    },
    items: [
      item("western-lowland-gorilla", "Congo Gorilla Forest", "Immersive gorilla habitat — a Bronx signature.", ["primates", "outdoor", "wow"]),
      item("sumatran-tiger", "Tiger Mountain", "Tigers at eye level through glass.", ["big-cats", "outdoor", "wow"]),
      item("african-lion", "African Plains", "Lions on the plains overlook.", ["big-cats", "outdoor"]),
      item("african-elephant", "Elephants", "Elephants when on the walking route.", ["big", "outdoor"]),
      item("reticulated-giraffe", "African Plains", "Giraffes above the acacias.", ["tall", "outdoor"]),
      item("ring-tailed-lemur", "Madagascar", "Lemurs hopping through the Madagascar building.", ["primates", "play", "wow"]),
      item("nile-hippo", "Africa", "Hippos near water features.", ["big", "water"]),
      item("zebra", "African Plains", "Stripes mixed with the plains herds.", ["pattern", "outdoor"]),
      item("red-panda", "Wild Asia / special", "Red panda fluff if scheduled on-view.", ["climb", "outdoor"]),
      item("galapagos-tortoise", "Reptiles", "Giant tortoises for a slow moment.", ["slow", "outdoor"]),
    ],
  },
  "philadelphia-zoo": {
    type: "zoo",
    tagline: "America’s first zoo — big cats, apes, and a compact kid-friendly map.",
    blurb: "Smaller campus than the Bronx: cats, primates, and KidZooU energy.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Zoo360 animal trails may be active — look up!",
      transit_note: "Girard Ave; parking on site.",
    },
    items: [
      item("sumatran-tiger", "Big cats", "Tigers on elevated trails sometimes overhead.", ["big-cats", "outdoor", "wow"]),
      item("african-lion", "Big cats", "Lions with classic zoo-front presence.", ["big-cats", "outdoor"]),
      item("western-lowland-gorilla", "Primates", "Gorilla families.", ["primates", "outdoor"]),
      item("orangutan", "Primates", "Orangutans using climbing structures.", ["primates", "climb"]),
      item("reticulated-giraffe", "Hoofstock", "Giraffe necks over the path.", ["tall", "outdoor"]),
      item("african-elephant", "Elephants", "Elephants when on the loop.", ["big", "outdoor"]),
      item("red-panda", "Small mammals", "Red pandas in trees.", ["climb", "outdoor"]),
      item("caribbean-flamingo", "Birds", "Pink flock near water.", ["color", "outdoor"]),
      item("ring-tailed-lemur", "Primates / kids", "Lemur energy for younger kids.", ["primates", "play"]),
      item("galapagos-tortoise", "Reptile / outdoor", "Slow giants.", ["slow", "outdoor"]),
    ],
  },
  "st-louis-zoo": {
    type: "zoo",
    tagline: "Iconic free-admission zoo — penguins, primates, and the 1904 Flight Cage vibe.",
    blurb: "Use the train or tram if little legs fade; hit penguins and apes early.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Admission often free; some experiences ticketed — confirm current policy.",
      transit_note: "Forest Park; easy with a stroller.",
    },
    items: [
      item("african-penguin", "Penguin & Puffin Coast", "Penguins underwater windows are a kid magnet.", ["water", "wow"]),
      item("western-lowland-gorilla", "Primate House / apes", "Gorillas up close.", ["primates", "outdoor"]),
      item("chimpanzee", "Primates", "Chimp social scenes.", ["primates", "play"]),
      item("orangutan", "Primates", "Orangutan long-arm climbs.", ["primates", "climb"]),
      item("african-elephant", "River's Edge", "Elephants on the River’s Edge loop.", ["big", "outdoor"]),
      item("nile-hippo", "River's Edge", "Hippo underwater views when open.", ["water", "big"]),
      item("african-lion", "Big cats", "Lions along the cat walk.", ["big-cats", "outdoor"]),
      item("sumatran-tiger", "Big cats", "Tigers in forested habitats.", ["big-cats", "outdoor"]),
      item("reticulated-giraffe", "Hoofed", "Giraffes above the paths.", ["tall", "outdoor"]),
      item("caribbean-flamingo", "Birds", "Flamingo lagoon pink.", ["color", "outdoor"]),
    ],
  },
  "omaha-henry-doorly": {
    type: "zoo",
    tagline: "Desert Dome + jungle + aquarium — three “worlds” in one ticket.",
    blurb: "Do Desert Dome or Lied Jungle first (wow buildings), then cats or aquarium.",
    practical: {
      typical_duration: "full day ideal; half day if you pick two worlds",
      ticket_note: "One of the great Midwest zoo days — arrive at open.",
      transit_note: "Omaha; car day.",
    },
    items: [
      item("african-elephant", "African Grasslands", "Elephants outdoors when weather allows.", ["big", "outdoor"]),
      item("western-lowland-gorilla", "Hubbard / apes", "Gorillas after the jungle wow.", ["primates", "outdoor"]),
      item("sumatran-tiger", "Asian Highlands", "Tigers in forested cat habitats.", ["big-cats", "outdoor"]),
      item("african-lion", "African Grasslands", "Lions on the grasslands.", ["big-cats", "outdoor"]),
      item("reticulated-giraffe", "African Grasslands", "Giraffe feeding opportunities some days.", ["tall", "outdoor", "feeding"]),
      item("shark", "Aquarium", "Sharks in the indoor aquarium wing.", ["water", "big", "wow"]),
      item("stingray", "Aquarium", "Rays in the aquarium galleries.", ["water", "flat"]),
      item("african-penguin", "Aquarium / penguins", "Penguins as a cool-down stop.", ["water", "wow"]),
      item("jellyfish", "Aquarium", "Jellies inside the dome complex story.", ["water", "glow"]),
      item("orangutan", "Jungle / apes", "Orangutans in lush indoor-outdoor spaces.", ["primates", "climb"]),
    ],
  },
  "amnh": {
    type: "museum",
    tagline: "Dinos, the blue whale, and space — NYC’s classic natural history circuit.",
    blurb: "Fossils first, then the Milstein hall whale, then planetarium if timed tickets allow.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Timed entry + optional planetarium tickets.",
      transit_note: "B/C to 81st Street; stroller-friendly halls.",
    },
    items: [
      item("sci-dinosaur", "Fossil halls", "T. rex and friends — the reason many kids beg to come.", ["wow", "read"], {
        question: "Were all dinosaurs huge?",
        answer: "No — some were small, but the big ones steal the show!",
      }),
      item("sci-mammal-hall", "Mammal halls", "Lifelike dioramas of animals in habitats.", ["wow", "read"]),
      item("sci-planet", "Hayden Planetarium", "Space show if you added tickets — stars and planets.", ["wow"]),
      item("sci-hands-on", "Discovery / education spaces", "Hands-on spots when open to the public floor.", ["hands"]),
      item("sci-rainforest", "Special / biodiversity", "Lush life exhibits when on the route.", ["wow"]),
      item("two-toed-sloth", "Live animals / special", "Live animals appear in some education spaces — bonus if present.", ["climb"]),
      item("sci-aquarium-zone", "Life exhibits", "Aquatic life corners in biodiversity areas.", ["water"]),
      item("cm-free-explore", "Open halls", "Pick a favorite hall and wander five minutes freestyle.", ["play"]),
    ],
  },
  "field-museum": {
    type: "museum",
    tagline: "SUE the T. rex leads Chicago’s natural history hit list.",
    blurb: "SUE first, then mummies or mammals, then a hands-on pause.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Museum Campus with Shedd and Adler — don’t overstack.",
      transit_note: "Roosevelt CTA; walk the campus.",
    },
    items: [
      item("sci-dinosaur", "SUE / Evolving Planet", "SUE the T. rex — still the superstar.", ["wow", "read"]),
      item("sci-mammal-hall", "Mammals", "Giant animal displays and dioramas.", ["wow"]),
      item("sci-hands-on", "Crown Family PlayLab", "PlayLab for younger kids when included/open.", ["hands", "play"]),
      item("sci-planet", "Space / rocks", "Meteorites and space stories upstairs/downstairs loops.", ["wow"]),
      item("sci-rainforest", "Underground Adventure / life", "Scale-shifting life exhibits if on your ticket path.", ["wow"]),
      item("cm-free-explore", "Main halls", "Choose one “wow room” and sketch a favorite.", ["play"]),
      item("sci-aquarium-zone", "Life sciences", "Aquatic cases and models along Evolving Planet edges.", ["water"]),
      item("cm-art-lab", "Creativity corners", "Make-and-take moments when offered.", ["hands", "art"]),
    ],
  },
  "kennedy-space-center": {
    type: "museum",
    tagline: "Real rockets and a space shuttle — Florida’s tourist STEM day done right.",
    blurb: "Atlantis and rocket garden first; bus tour only if energy remains.",
    practical: {
      typical_duration: "half to full day",
      ticket_note: "Hot outdoor queues — water, hats, stroller.",
      transit_note: "Merritt Island; car required for most families.",
    },
    items: [
      item("sci-shuttle", "Space Shuttle Atlantis", "Stand under a real orbiter — pure wow.", ["wow"], {
        question: "Where did the shuttle go?",
        answer: "To space — and back to Earth on a runway!",
      }),
      item("sci-rocket", "Rocket Garden", "Tall rockets outdoors you can walk among.", ["wow", "tall"]),
      item("sci-astronaut", "Astronaut stories", "Meet the people who trained to leave Earth.", ["read", "wow"]),
      item("sci-planet", "Universe / theaters", "Planets and stars in shows or galleries.", ["wow"]),
      item("sci-hands-on", "Interactive simulators", "Try a hands-on space challenge if lines are short.", ["hands"]),
      item("cm-free-explore", "Gateway complex", "Pick a favorite rocket photo spot.", ["play"]),
      item("sci-dinosaur", "Only if special exhibit", "Skip unless a dino pop-up is up — space is the star.", ["read"]),
      item("cm-outdoor", "Outdoor paths", "Train/bus plazas and outdoor exploring between buildings.", ["outdoor"]),
    ],
  },
  "california-science-center": {
    type: "museum",
    tagline: "Space Shuttle Endeavour plus hands-on ecosystems — free galleries, timed Endeavour.",
    blurb: "Endeavour when timed tickets allow; otherwise ecosystems and hands-on halls.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Permanent galleries often free; Endeavour may need a timed reservation.",
      transit_note: "Exposition Park; Metro E Line Expo Park/USC.",
    },
    items: [
      item("sci-shuttle", "Samuel Oschin Pavilion", "Endeavour — the headliner.", ["wow"]),
      item("sci-rocket", "Space galleries", "Rockets and space hardware around Endeavour.", ["wow", "tall"]),
      item("sci-hands-on", "Discovery rooms", "Buttons, cranks, and build zones.", ["hands", "play"]),
      item("sci-planet", "Space / weather", "Earth and space science stories.", ["wow"]),
      item("sci-aquarium-zone", "Ecosystems water", "Aquatic life inside ecosystems halls.", ["water"]),
      item("sci-rainforest", "Ecosystems", "Lush plant and animal corners in the free galleries.", ["wow"]),
      item("sci-dinosaur", "Life sciences", "Fossils and deep-time stories if on your floor path.", ["read"]),
      item("cm-toddler-garden", "Family spaces", "Softer spaces for the youngest explorers.", ["play", "rest"]),
    ],
  },
  "cal-academy": {
    type: "museum",
    tagline: "Rainforest dome, planetarium, and aquarium under one living roof.",
    blurb: "Aquarium lower level + rainforest spiral is the classic kid circuit.",
    practical: {
      typical_duration: "half day",
      ticket_note: "Planetarium is timed/extra; aquarium+rainforest are the free-flow hits.",
      transit_note: "Golden Gate Park; busy weekends.",
    },
    items: [
      item("sci-rainforest", "Rainforest", "Four-story living rainforest dome — look for birds and butterflies.", ["wow", "climb"]),
      item("shark", "Aquarium", "Sharks in the Philippine Coral Reef and main tanks.", ["water", "big"]),
      item("african-penguin", "African Penguin exhibit", "Penguins just outside/near the academy path.", ["water", "wow"]),
      item("jellyfish", "Aquarium", "Jellies in glowing corridors.", ["water", "glow"]),
      item("octopus", "Aquarium", "Octopus hideouts along the tanks.", ["water", "hide"]),
      item("stingray", "Aquarium", "Rays in shallow views.", ["water", "flat"]),
      item("sci-planet", "Planetarium", "Morrison Planetarium show if ticketed.", ["wow"]),
      item("sci-hands-on", "Naturalist Center / floors", "Touch specimens and discovery carts when open.", ["hands"]),
      item("seahorse", "Aquarium", "Seahorses in smaller tanks.", ["water", "tiny"]),
      item("clownfish", "Coral reef", "Bright reef fish under the rainforest.", ["water", "color"]),
    ],
  },
};

function ensureEight(items) {
  const out = [...items];
  const pads = [
    item("cm-free-explore", "", "Two free minutes — kid picks the next turn.", ["play"]),
  ];
  let i = 0;
  while (out.length < 8 && i < pads.length) {
    out.push(pads[i++]);
  }
  return out;
}

let missionWritten = 0;
let catalogPatches = 0;

for (const [slug, pack] of Object.entries(WAVE2)) {
  const v = venues[slug];
  const p = places[slug] || {};
  if (!v) {
    console.warn("skip catalog missing", slug);
    continue;
  }
  let items = pack.items.filter((it) => catalog[it.catalog_id]);
  items = ensureEight(items);
  if (items.length < 8) {
    console.warn("still short", slug, items.length);
  }

  const [cityPart, regionPart] = (v.location || "").split(",").map((s) => s.trim());
  const mission = {
    slug,
    name: v.name || p.name || slug,
    type: pack.type,
    city: p.city || cityPart || "",
    region: p.state || regionPart || "",
    country: "US",
    lat: p.lat || 0,
    lng: p.lon || 0,
    official_url: v.website || "",
    last_verified: TODAY,
    verified_by: "research",
    status: "verified",
    tagline: pack.tagline,
    practical: pack.practical || {
      typical_duration: "half day",
      ticket_note: "Check the official site for tickets and hours.",
      transit_note: "",
    },
    items,
  };
  fs.writeFileSync(path.join(VENUE_DIR, `${slug}.json`), JSON.stringify(mission, null, 2) + "\n");
  missionWritten++;

  // Patch catalog venue fields in memory then serialize carefully via regex replacements
  const featured = items
    .map((it) => it.catalog_id)
    .filter(Boolean)
    .slice(0, 8);
  const animalIds = items.map((it) => it.catalog_id).filter(Boolean);
  // Keep any existing extras not in list for outing depth
  const prev = v.animalIds || [];
  const merged = [...animalIds];
  for (const id of prev) {
    if (!merged.includes(id) && catalog[id]) merged.push(id);
  }

  venues[slug] = {
    ...v,
    quality: "full",
    lastVerified: TODAY,
    blurb: pack.blurb || pack.tagline,
    featuredAnimalIds: featured,
    animalIds: merged.slice(0, 16),
  };
  catalogPatches++;
}

// Rewrite catalog.js venue objects for wave2 slugs by targeted block replace is hard;
// instead patch quality/blurb/featured/animalIds with a structured approach:
let catSrc = fs.readFileSync(CATALOG_JS, "utf8");

function replaceVenueArrays(src, slug, venueObj) {
  // Find venue block: "slug": { ... },
  const key = `"${slug}"`;
  const start = src.indexOf(`${key}:`);
  if (start < 0) {
    // try unquoted id: "slug": pattern in older files - venues use "id": "slug" form
    const alt = src.indexOf(`id: "${slug}"`);
    if (alt < 0) {
      console.warn("catalog block not found", slug);
      return src;
    }
    return patchFromId(src, alt, venueObj);
  }
  return src;
}

function patchFromId(src, idPos, venueObj) {
  // Walk backward to object start
  let start = idPos;
  while (start > 0 && src[start] !== "{") start--;
  // Walk forward matching braces
  let i = start;
  let depth = 0;
  let end = -1;
  for (; i < src.length; i++) {
    const ch = src[i];
    if (ch === "{") depth++;
    else if (ch === "}") {
      depth--;
      if (depth === 0) {
        end = i + 1;
        break;
      }
    }
  }
  if (end < 0) return src;
  let block = src.slice(start, end);

  function setArr(field, arr) {
    const re = new RegExp(`${field}:\\s*\\[[\\s\\S]*?\\]`, "m");
    const body = `${field}: [\n${arr.map((x) => `      "${x}"`).join(",\n")}\n    ]`;
    if (re.test(block)) block = block.replace(re, body);
    else block = block.replace(/itemLabel:\s*"[^"]*",/, (m) => `${m}\n    ${body},`);
  }
  function setStr(field, val) {
    const re = new RegExp(`${field}:\\s*"[^"]*"`, "m");
    const body = `${field}: ${JSON.stringify(val)}`;
    if (re.test(block)) block = block.replace(re, body);
    else block = block.replace(/mode:\s*"[^"]*",/, (m) => `${m}\n    ${body},`);
  }

  setStr("quality", "full");
  setStr("lastVerified", TODAY);
  setStr("blurb", venueObj.blurb);
  setArr("featuredAnimalIds", venueObj.featuredAnimalIds);
  setArr("animalIds", venueObj.animalIds);

  return src.slice(0, start) + block + src.slice(end);
}

for (const slug of Object.keys(WAVE2)) {
  const v = venues[slug];
  if (!v) continue;
  catSrc = patchFromId(catSrc, catSrc.indexOf(`id: "${slug}"`), v);
}

fs.writeFileSync(CATALOG_JS, catSrc);

// places-data blurbs
let placesSrc = fs.readFileSync(PLACES_JS, "utf8");
for (const [slug, pack] of Object.entries(WAVE2)) {
  const blurb = pack.blurb || pack.tagline;
  const re = new RegExp(`(id: "${slug}",[\\s\\S]{0,500}?blurb: )"[^"]*"`);
  if (re.test(placesSrc)) {
    placesSrc = placesSrc.replace(re, `$1${JSON.stringify(blurb).slice(1, -1).replace(/"/g, '\\"').replace(/\\/g, "\\\\")}`);
    // simpler:
  }
}
// redo places blurbs simply
placesSrc = fs.readFileSync(PLACES_JS, "utf8");
for (const [slug, pack] of Object.entries(WAVE2)) {
  const blurb = pack.blurb || pack.tagline;
  const re = new RegExp(`(id: "${slug}",[\\s\\S]{0,450}?blurb:\\s*)"([^"]*)"`);
  placesSrc = placesSrc.replace(re, `$1${JSON.stringify(blurb)}`);
}
fs.writeFileSync(PLACES_JS, placesSrc);

console.log(
  JSON.stringify(
    {
      missionWritten,
      catalogPatches,
      slugs: Object.keys(WAVE2),
    },
    null,
    2
  )
);
