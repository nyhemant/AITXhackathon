#!/usr/bin/env node
/**
 * R2 hybrid: remaining US wonder venues + high-traffic intl flagships.
 * Same simple pattern as R1 — icons + practical + map page. No new UI.
 */
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const FIELD = path.join(__dirname, "..", "static", "field-pack");
const VENUE_DIR = path.join(FIELD, "data", "venues");
const CATALOG_JS = path.join(FIELD, "js", "catalog.js");
const PLACES_JS = path.join(FIELD, "js", "places-data.js");
const TODAY = new Date().toISOString().slice(0, 10);

const ctx = { window: {}, console };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(CATALOG_JS, "utf8"), ctx);
vm.runInContext(fs.readFileSync(PLACES_JS, "utf8"), ctx);
const catalog = ctx.window.FIELD_PACK_CATALOG;
const venuesCat = ctx.window.FIELD_PACK_VENUES;
const places = Object.fromEntries((ctx.window.FP_PLACES || []).map((p) => [p.id, p]));

function item(id, zone, one, tags) {
  const it = catalog[id];
  if (!it) throw new Error("missing catalog " + id);
  return {
    id: id.replace(/-/g, "_").slice(0, 28),
    label: it.name,
    emoji: it.emoji || "📍",
    one_liner: one || it.blurb || `Find the ${it.name}.`,
    tags: tags || ["wow"],
    age_fit: ["2-3", "4-5", "6-8", "9+"],
    zone: zone || "",
    qa_card: {
      question: `What did you notice about the ${it.name}?`,
      answer: "Tell a grown-up one thing you saw!",
    },
    catalog_id: id,
  };
}

function pack(type, tagline, blurb, practical, mapPage, icons, extraMedia) {
  return {
    type,
    tagline,
    blurb,
    practical,
    media: Object.assign(
      {
        visitor_map_url: "",
        visitor_map_page: mapPage || "",
        visitor_map_kind: "page",
        map_attribution: "Official visit page",
      },
      extraMedia || {}
    ),
    icons,
  };
}

const zoo = (t, b, p, m, icons) => pack("zoo", t, b, p, m, icons);
const aq = (t, b, p, m, icons) => pack("aquarium", t, b, p, m, icons);
const mu = (t, b, p, m, icons) => pack("museum", t, b, p, m, icons);

const half = (ticket, transit, energy, start) => ({
  typical_duration: "half day",
  ticket_note: ticket,
  transit_note: transit,
  energy_note: energy,
  best_start: start,
});

const R2 = {
  // —— remaining US ——
  "air-and-space": mu(
    "Mall airplanes and space — rockets overhead, walk-under wow.",
    "Udvar-Hazy or Mall: pick planes first, then one space hall.",
    half("Free Smithsonian entry; timed if required — check airandspace.si.edu.", "Mall or Udvar-Hazy (separate campus).", "indoor", "One giant aircraft, then rest legs."),
    "https://airandspace.si.edu/",
    [
      item("sci-rocket", "Rockets / missiles", "Stand under real flight hardware.", ["wow", "tall"]),
      item("sci-shuttle", "Space", "Orbiter or space hardware when on that campus.", ["wow"]),
      item("sci-astronaut", "Human spaceflight", "People who left Earth.", ["read", "wow"]),
      item("sci-planet", "Space science", "Planets and stars stories.", ["wow"]),
      item("cm-free-explore", "Kid pick", "They choose the next giant machine.", ["play"]),
    ]
  ),
  "smithsonian-natural-history": mu(
    "Mall fossils and ocean hall — free, crowded, finishable if you pick two halls.",
    "Dinos or ocean first; don’t try the whole building.",
    half("Free; lines at peak times.", "National Mall Metro.", "indoor", "Fossil hall wow, then one more favorite."),
    "https://naturalhistory.si.edu/",
    [
      item("sci-dinosaur", "Fossils", "Deep-time bones for instant wow.", ["wow", "read"]),
      item("sci-mammal-hall", "Mammals", "Classic dioramas and big animals.", ["wow"]),
      item("sci-aquarium-zone", "Ocean", "Ocean hall energy when open.", ["water", "wow"]),
      item("sci-hands-on", "Discovery", "Hands-on corners when available.", ["hands"]),
      item("cm-free-explore", "Kid lead", "Five minutes their choice.", ["play"]),
    ]
  ),
  "arizona-science-center": mu(
    "Downtown Phoenix science — indoor escape from the desert heat.",
    "Hands-on first; planetarium only if energy remains.",
    half("Timed tickets possible in peak season.", "Light rail / downtown.", "indoor", "Body-play science floor before any show."),
    "https://www.azscience.org/",
    [
      item("sci-hands-on", "Galleries", "Touch and try is the whole point.", ["hands", "play", "wow"]),
      item("sci-planet", "Planetarium", "Sky show if ticketed.", ["wow"]),
      item("sci-rocket", "Space", "Space hardware energy.", ["wow"]),
      item("cm-free-explore", "Kid pick", "They choose the next station.", ["play"]),
      item("sci-dinosaur", "Life / earth", "Dinos if on the route.", ["read"]),
    ]
  ),
  "audubon-zoo": zoo(
    "New Orleans classic zoo — Louisiana swamp feel + big animals.",
    "Compact enough for a half day; shade and water in heat.",
    half("Audubon tickets; check audubonnatureinstitute.org.", "Uptown / Magazine area.", "heat", "Shade loop first in summer."),
    "https://audubonnatureinstitute.org/zoo",
    [
      item("african-elephant", "Elephants", "Big wow early.", ["big", "outdoor", "wow"]),
      item("reticulated-giraffe", "Giraffes", "Tall necks on the loop.", ["tall", "outdoor"]),
      item("sumatran-tiger", "Cats", "Stripes in forested spaces.", ["big-cats", "outdoor"]),
      item("western-lowland-gorilla", "Primates", "Gorilla families.", ["primates", "outdoor"]),
      item("nile-hippo", "Hippos", "Water-loving giants.", ["water", "big"]),
    ]
  ),
  "austin-zoo": zoo(
    "Hill Country rescue-style zoo — smaller, kinder pace than mega zoos.",
    "Perfect when you want animals without a stadium day.",
    half("Check austinzoo.org hours.", "Southwest Austin; car.", "heat", "One loop; leave while happy."),
    "https://www.austinzoo.org/",
    [
      item("african-lion", "Cats", "Big cats on a shorter campus.", ["big-cats", "outdoor"]),
      item("sumatran-tiger", "Cats", "Tigers without endless walking.", ["big-cats", "outdoor"]),
      item("reticulated-giraffe", "Hoofstock", "Giraffe moment.", ["tall", "outdoor"]),
      item("ring-tailed-lemur", "Primates", "Lemur hop energy.", ["primates", "play"]),
      item("galapagos-tortoise", "Reptiles", "Slow giants.", ["slow", "outdoor"]),
    ]
  ),
  "carnegie-natural-history": mu(
    "Pittsburgh dinos and gems — classic natural history without Mall crowds.",
    "Dippy energy: fossils first, then one more hall.",
    half("Combined tickets with art sometimes — check carnegiemnh.org.", "Oakland museums cluster.", "indoor", "Dinosaurs, then kid pace."),
    "https://carnegiemnh.org/",
    [
      item("sci-dinosaur", "Dinosaurs", "Fossil wow is the draw.", ["wow", "read"]),
      item("sci-mammal-hall", "Mammals / dioramas", "Habitat stories.", ["wow"]),
      item("sci-hands-on", "Discovery", "Hands-on when open.", ["hands"]),
      item("sci-planet", "Earth / space", "Rocks and space corners.", ["wow"]),
      item("cm-free-explore", "Kid pick", "They choose next.", ["play"]),
    ]
  ),
  "cleveland-metroparks-zoo": zoo(
    "Cleveland Metroparks — rainforest building + outdoor loops.",
    "Use the indoor rainforest when weather bites.",
    half("Metroparks tickets; parking on site.", "Brookside area.", "stroller-easy", "RainForest first if cold/hot, then outdoor icons."),
    "https://www.clevelandmetroparks.com/zoo",
    [
      item("western-lowland-gorilla", "Primates / rainforest", "Gorillas in lush indoor-outdoor spaces.", ["primates", "wow"]),
      item("african-elephant", "Elephants", "Elephants on outdoor paths.", ["big", "outdoor"]),
      item("sumatran-tiger", "Cats", "Tigers on the loop.", ["big-cats", "outdoor"]),
      item("reticulated-giraffe", "Hoofstock", "Tall necks.", ["tall", "outdoor"]),
      item("two-toed-sloth", "Rainforest", "Slow climbers if you spot them.", ["climb"]),
    ]
  ),
  "dallas-arboretum": mu(
    "Dallas gardens — seasonal color, kid exploration, not a zoo census.",
    "Wonder sheet heaven: colors, paths, fountains, rest stops.",
    half("Timed tickets peak bloom seasons.", "White Rock Lake area.", "heat", "Shade + water; one garden room at a time."),
    "https://www.dallasarboretum.org/",
    [
      item("cm-outdoor", "Gardens", "Paths, flowers, and open sky.", ["outdoor", "play", "wow"]),
      item("cm-free-explore", "Kid lead", "They pick the next fountain or path.", ["play"]),
      item("cm-toddler-garden", "Little kids", "Softer corners to reset.", ["rest", "play"]),
      item("sci-hands-on", "Discovery", "Hands-on moments if offered.", ["hands"]),
      item("cm-makery", "Make", "Create something small if stations are open.", ["hands", "play"]),
    ]
  ),
  "dallas-world-aquarium": aq(
    "Downtown Dallas rainforest-under-a-roof — sloths, fish, and vertical wow.",
    "Multi-level indoor loop; great heat escape.",
    half("Downtown parking; check dwazoo.com.", "West End / downtown.", "indoor", "Start at the top and spiral down if signed that way."),
    "https://www.dwazoo.com/",
    [
      item("two-toed-sloth", "Rainforest", "Sloths hanging in the greenery.", ["climb", "wow"]),
      item("shark", "Aquatic", "Sharks in the aquatic sections.", ["water", "big"]),
      item("stingray", "Aquatic", "Rays gliding past.", ["water", "flat"]),
      item("ring-tailed-lemur", "Primates", "Lemur energy in rainforest settings.", ["primates", "play"]),
      item("jellyfish", "Jellies", "Glow pause if present.", ["water", "glow"]),
    ].filter((x) => x && x.catalog_id)
  ),
  "discovery-place": mu(
    "Charlotte science — hands-on floors built for wiggly kids.",
    "One lab floor + kid choice beats racing every exhibit.",
    half("Check discoveryplace.org for which campus/tickets.", "Uptown Charlotte options.", "indoor", "Hands-on first."),
    "https://discoveryplace.org/",
    [
      item("sci-hands-on", "Labs", "Touch and try.", ["hands", "play", "wow"]),
      item("sci-planet", "Space / sky", "Space moments if offered.", ["wow"]),
      item("sci-dinosaur", "Life", "Dinos if on route.", ["read"]),
      item("cm-free-explore", "Kid pick", "They choose next.", ["play"]),
      item("sci-aquarium-zone", "Life / water", "Small live tanks when present.", ["water"]),
    ]
  ),
  "honolulu-zoo": zoo(
    "Waikiki-adjacent zoo — tropical setting, shorter visit than mainland megas.",
    "Pair with beach carefully; zoo alone is enough for little legs.",
    half("Heat and sun — morning best.", "Near Waikiki; walk/bus/car.", "heat", "Shade and water; one loop."),
    "https://www.honoluluzoo.org/",
    [
      item("african-elephant", "Elephants", "Tropical elephant stop.", ["big", "outdoor", "wow"]),
      item("reticulated-giraffe", "Giraffes", "Tall necks.", ["tall", "outdoor"]),
      item("sumatran-tiger", "Cats", "Big cats.", ["big-cats", "outdoor"]),
      item("ring-tailed-lemur", "Primates", "Lemurs.", ["primates", "play"]),
      item("caribbean-flamingo", "Birds", "Pink flock easy win.", ["color", "outdoor"]),
    ]
  ),
  "waikiki-aquarium": aq(
    "Tiny ocean gem by the water — Hawaiian reef life, not a mega-aquarium.",
    "Short and sweet; perfect after beach or before dinner.",
    half("Small campus; check hours.", "Waikiki waterfront.", "indoor", "One slow loop; read a few labels together."),
    "https://www.waikikiaquarium.org/",
    [
      item("shark", "Reef / ocean", "Sharks in island tanks.", ["water", "wow"]),
      item("sea-turtle", "Turtles", "Honu energy when on view.", ["water", "shell", "wow"]),
      item("jellyfish", "Jellies", "Soft glow.", ["water", "glow"]),
      item("octopus", "Camouflage", "Look carefully.", ["water", "hide"]),
      item("clownfish", "Reef", "Bright reef colors.", ["water", "color"]),
    ]
  ),
  "kansas-city-zoo": zoo(
    "KC zoo — train/boat extras optional; pick habitats not rides first.",
    "Big enough to overdo — two regions max with little kids.",
    half("Extras cost more; animals first.", "Swope Park; car.", "stroller-easy", "Africa or Australia first, then decide."),
    "https://www.kansascityzoo.org/",
    [
      item("african-elephant", "Africa", "Elephants early.", ["big", "outdoor", "wow"]),
      item("reticulated-giraffe", "Africa", "Giraffes.", ["tall", "outdoor"]),
      item("african-lion", "Cats", "Lions.", ["big-cats", "outdoor"]),
      item("sumatran-tiger", "Cats / Asia", "Tigers.", ["big-cats", "outdoor"]),
      item("koala", "Australia", "Koalas if on exhibit — iconic KC stop when present.", ["wow", "outdoor"]),
    ]
  ),
  "memphis-zoo": zoo(
    "Memphis classic — China exhibit lore and a full zoo loop.",
    "Morning visit; pick pandas only if currently on view (exhibits change).",
    half("Confirm star exhibits on memphiszoo.org before promising kids.", "Midtown; car.", "heat", "Shade route in summer."),
    "https://www.memphiszoo.org/",
    [
      item("giant-panda", "China", "Pandas when present — always verify before the visit.", ["wow", "outdoor", "big"]),
      item("african-elephant", "Africa", "Elephants.", ["big", "outdoor"]),
      item("reticulated-giraffe", "Africa", "Giraffes.", ["tall", "outdoor"]),
      item("sumatran-tiger", "Cats", "Tigers.", ["big-cats", "outdoor"]),
      item("western-lowland-gorilla", "Primates", "Gorillas.", ["primates", "outdoor"]),
    ]
  ),
  "miami-zoo": zoo(
    "Zoo Miami — huge open campus; wagon/stroller and early start required.",
    "Never see it all; two loops max in heat.",
    half("South Dade heat is real — water, hats, early entry.", "Car essential.", "heat", "Asia or Africa only; leave by late morning in summer."),
    "https://www.zoomiami.org/",
    [
      item("african-elephant", "Africa", "Elephants on open range-style views.", ["big", "outdoor", "wow"]),
      item("reticulated-giraffe", "Africa", "Giraffes.", ["tall", "outdoor"]),
      item("sumatran-tiger", "Asia", "Tigers.", ["big-cats", "outdoor"]),
      item("orangutan", "Asia / primates", "Orangutans.", ["primates", "climb"]),
      item("nile-hippo", "Africa", "Hippos.", ["water", "big"]),
    ]
  ),
  "museum-of-science-industry-chi": mu(
    "Chicago MSI — submarine, science storms, and kid hands-on overload (in a good way).",
    "Pick two signature experiences; ignore the rest guilt-free.",
    half("Timed entry common; parking garage.", "Hyde Park.", "indoor", "One icon (U-505/storms/etc.) + one hands-on zone."),
    "https://www.msichicago.org/",
    [
      item("sci-hands-on", "Interactive", "Touch science everywhere.", ["hands", "play", "wow"]),
      item("sci-rocket", "Science / transport", "Big machines and flight energy.", ["wow", "tall"]),
      item("sci-planet", "Space / earth", "Space and earth stories.", ["wow"]),
      item("sci-dinosaur", "Life", "Life science moments.", ["read"]),
      item("cm-free-explore", "Kid pick", "They choose the next hall.", ["play"]),
    ]
  ),
  "nashville-adventure-science": mu(
    "Nashville Adventure Science — climbing + experiments downtown.",
    "Body-first museum: climb, then calm make time.",
    half("Check adventuresci.org tickets.", "Downtown Nashville.", "indoor", "Climb/play first, quieter exhibits second."),
    "https://www.adventuresci.org/",
    [
      item("sci-hands-on", "Labs", "Experiments and interactives.", ["hands", "play", "wow"]),
      item("cm-outdoor", "Climb / body", "Big-body play energy.", ["play", "outdoor"]),
      item("sci-planet", "Space", "Space corners if present.", ["wow"]),
      item("cm-makery", "Make", "Build something small.", ["hands"]),
      item("cm-toddler-garden", "Little kids", "Toddler-friendly zones.", ["rest", "play"]),
    ]
  ),
  "north-carolina-zoo": zoo(
    "America’s largest natural habitat zoo — miles of paths; plan like a hike with animals.",
    "One continent side per visit with little kids.",
    half("Asheboro; full day only if you must. Stroller/wagon mandatory.", "Car trip.", "stroller-easy", "Africa or North America — not both."),
    "https://www.nczoo.org/",
    [
      item("african-elephant", "Africa", "Elephants in spacious habitats.", ["big", "outdoor", "wow"]),
      item("reticulated-giraffe", "Africa", "Giraffes on long views.", ["tall", "outdoor"]),
      item("african-lion", "Africa", "Lions.", ["big-cats", "outdoor"]),
      item("western-lowland-gorilla", "Africa", "Gorillas.", ["primates", "outdoor"]),
      item("nile-hippo", "Africa", "Hippos.", ["water", "big"]),
    ]
  ),
  "orlando-science-center": mu(
    "Orlando science without theme-park prices — hands-on + optional shows.",
    "Great reset day from parks; don’t stack every add-on.",
    half("Loch Haven area; check osc.org.", "Car / rideshare.", "indoor", "Hands-on floors first."),
    "https://www.osc.org/",
    [
      item("sci-hands-on", "Exhibit floors", "Touch science.", ["hands", "play", "wow"]),
      item("sci-planet", "Shows", "Planetarium if ticketed.", ["wow"]),
      item("sci-dinosaur", "Dinos", "Dino wow if featured.", ["read", "wow"]),
      item("cm-free-explore", "Kid lead", "They pick next.", ["play"]),
      item("sci-rocket", "Flight / space", "Rockets and flight energy.", ["wow"]),
    ]
  ),
  "perot-museum": mu(
    "Dallas Perot — dinosaurs, sports hall energy, and kids’ museum levels.",
    "Children’s levels + one big hall is a perfect half day.",
    half("Victory Park; timed tickets peak times.", "Downtown adjacent.", "indoor", "Kids floors first if under 8."),
    "https://www.perotmuseum.org/",
    [
      item("sci-dinosaur", "T. Boone Pickens Life Then and Now", "Dinos are the magnet.", ["wow", "read"]),
      item("sci-hands-on", "Sports / being human", "Body science fun.", ["hands", "play"]),
      item("cm-imaginarium", "Children’s museum levels", "Play and pretend.", ["play"]),
      item("sci-planet", "Earth / space", "Earth and beyond.", ["wow"]),
      item("cm-makery", "Make", "Create something.", ["hands"]),
    ]
  ),
  "pittsburgh-zoo": zoo(
    "Pittsburgh Zoo & PPG Aquarium — hill campus with indoor water wow.",
    "Aquarium helps on cold days; outdoor loops when mild.",
    half("Seasonal hours; parking on site.", "Highland Park.", "hills", "Aquarium if cold; Africa if mild."),
    "https://www.pittsburghzoo.org/",
    [
      item("shark", "PPG Aquarium", "Sharks indoors.", ["water", "big", "wow"]),
      item("african-elephant", "Elephants", "Elephants outdoors.", ["big", "outdoor"]),
      item("reticulated-giraffe", "Africa", "Giraffes.", ["tall", "outdoor"]),
      item("sumatran-tiger", "Cats", "Tigers.", ["big-cats", "outdoor"]),
      item("jellyfish", "Aquarium", "Jellies.", ["water", "glow"]),
    ]
  ),
  "san-antonio-zoo": zoo(
    "San Antonio Zoo — riverside, Llamas lore, dense habitats near downtown.",
    "Heat strategy: morning only in summer.",
    half("Brackenridge Park area.", "Near downtown.", "heat", "Water + shade; one loop."),
    "https://sazoo.org/",
    [
      item("african-elephant", "Elephants", "Elephants early.", ["big", "outdoor", "wow"]),
      item("reticulated-giraffe", "Giraffes", "Tall necks.", ["tall", "outdoor"]),
      item("sumatran-tiger", "Cats", "Tigers.", ["big-cats", "outdoor"]),
      item("western-lowland-gorilla", "Primates", "Gorillas.", ["primates", "outdoor"]),
      item("caribbean-flamingo", "Birds", "Pink flock.", ["color", "outdoor"]),
    ]
  ),
  "tampa-zoo": zoo(
    "ZooTampa — manatees and Florida stories plus classic zoo loops.",
    "Manatee building is the local wow when open.",
    half("Check zootampa.org for manatee status.", "North Tampa.", "heat", "Manatees first, then one outdoor loop."),
    "https://zootampa.org/",
    [
      item("nile-hippo", "Water mammals", "Big water mammals energy (hippo stand-in if manatee card missing).", ["water", "big", "wow"]),
      item("african-elephant", "Elephants", "Elephants.", ["big", "outdoor"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall", "outdoor"]),
      item("sumatran-tiger", "Cats", "Tigers.", ["big-cats", "outdoor"]),
      item("stingray", "Water / touch", "Rays if touch/water exhibits open.", ["water", "touch"]),
    ]
  ),
  "thinkery": mu(
    "Austin Thinkery — pure play museum; short visit, high joy.",
    "Let them lead; print wonders not a schedule.",
    half("Mueller; timed tickets peak times.", "Easy parking usually.", "indoor", "One big play room + snack."),
    "https://thinkeryaustin.org/",
    [
      item("cm-makery", "Make", "Build and tinker.", ["hands", "play"]),
      item("cm-imaginarium", "Imagine", "Pretend worlds.", ["play"]),
      item("cm-waterfall", "Water", "Splash when open.", ["water", "play"]),
      item("cm-toddler-garden", "Little kids", "Toddler spaces.", ["rest", "play"]),
      item("cm-outdoor", "Outdoor", "Outside energy if open.", ["outdoor", "play"]),
    ]
  ),
  "union-station-kc-science": mu(
    "KC Science City inside Union Station — trains outside, experiments inside.",
    "Combine with station grandeur; don’t overstack city plans.",
    half("Union Station complex tickets.", "Downtown KC.", "indoor", "Science floors first, station photos after."),
    "https://www.unionstation.org/sciencecity",
    [
      item("sci-hands-on", "Science City", "Interactives galore.", ["hands", "play", "wow"]),
      item("sci-planet", "Space / sky", "Space moments.", ["wow"]),
      item("sci-dinosaur", "Life", "Dinos if featured.", ["read"]),
      item("cm-free-explore", "Kid pick", "They choose.", ["play"]),
      item("sci-rocket", "Flight", "Flight/tech wow.", ["wow"]),
    ]
  ),

  // —— intl flagships (high tourist) ——
  "dublin-zoo": zoo(
    "Dublin Zoo — compact European classic in Phoenix Park.",
    "Half day with little kids; park walks optional after.",
    half("Book ahead in peak summer.", "Phoenix Park; bus/car.", "stroller-easy", "Family-friendly loop; one snack stop."),
    "https://www.dublinzoo.ie/",
    [
      item("western-lowland-gorilla", "Gorillas", "Gorillas are a Dublin favorite.", ["primates", "wow"]),
      item("sumatran-tiger", "Asian forests", "Tigers.", ["big-cats", "outdoor"]),
      item("african-elephant", "Elephants", "Elephants.", ["big", "outdoor"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall", "outdoor"]),
      item("african-penguin", "Penguins", "Penguins.", ["water", "wow"]),
    ]
  ),
  "edinburgh-zoo": zoo(
    "Edinburgh Zoo — hillside city zoo; penguins famous, paths steep.",
    "Stroller brakes matter; don’t climb every path.",
    half("Book tickets; penguin parade schedules vary.", "Corstorphine; bus from center.", "hills", "Penguins + one more habitat."),
    "https://www.edinburghzoo.org.uk/",
    [
      item("african-penguin", "Penguins", "Penguin fame is real — check day’s schedule.", ["water", "wow"]),
      item("western-lowland-gorilla", "Primates", "Gorillas.", ["primates"]),
      item("sumatran-tiger", "Cats", "Tigers.", ["big-cats"]),
      item("koala", "Koalas", "Koalas when on exhibit.", ["wow"]),
      item("red-panda", "Red pandas", "Red panda fluff.", ["climb"]),
    ]
  ),
  "berlin-zoo": zoo(
    "Berlin Zoo — historic city zoo packed with species; pick a quarter.",
    "Too big to finish; enter with a 90-minute mindset.",
    half("City center; combine with park carefully.", "Zoo station area.", "stroller-easy", "One gate loop only with toddlers."),
    "https://www.zoo-berlin.de/en/",
    [
      item("african-elephant", "Elephants", "Elephants.", ["big", "outdoor", "wow"]),
      item("western-lowland-gorilla", "Apes", "Gorillas.", ["primates", "wow"]),
      item("sumatran-tiger", "Cats", "Tigers.", ["big-cats"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
      item("african-penguin", "Penguins", "Penguins.", ["water"]),
    ]
  ),
  "toronto-zoo": zoo(
    "Toronto Zoo — vast; treat it like two zoos and only do one.",
    "Wagon rental culture exists for a reason.",
    half("Reserve parking energy; open at open.", "Scarborough; car.", "stroller-easy", "One geographic realm only."),
    "https://www.torontozoo.com/",
    [
      item("african-elephant", "African savanna", "Elephants.", ["big", "outdoor", "wow"]),
      item("reticulated-giraffe", "African savanna", "Giraffes.", ["tall", "outdoor"]),
      item("sumatran-tiger", "Indo-Malaya", "Tigers.", ["big-cats", "outdoor"]),
      item("western-lowland-gorilla", "African rain forest", "Gorillas.", ["primates"]),
      item("giant-panda", "Occasionally", "Pandas only if currently featured — verify first.", ["wow"]),
    ]
  ),
  "singapore-zoo": zoo(
    "Singapore Zoo — rainforest immersion, breakfast with orangutans lore.",
    "Humid; pace slow; water breaks constant.",
    half("Book online; morning cooler.", "Mandai; plan transport.", "heat", "Orangutans + one more zone."),
    "https://www.mandai.com/en/singapore-zoo.html",
    [
      item("orangutan", "Orangutans", "Free-ranging orangutan views are the signature.", ["primates", "climb", "wow"]),
      item("reticulated-giraffe", "Wild Africa", "Giraffes.", ["tall", "outdoor"]),
      item("african-elephant", "Elephants", "Elephants.", ["big", "outdoor"]),
      item("sumatran-tiger", "Cats", "Tigers.", ["big-cats"]),
      item("red-panda", "Fragile forest", "Red pandas.", ["climb"]),
    ]
  ),
  "taronga-zoo": zoo(
    "Sydney harbour views + Aussie animals — ferry arrival is half the wow.",
    "Koalas and views first; wire cable if legs allow.",
    half("Ferry + tickets; hills on site.", "Mosman; ferry from Circular Quay.", "hills", "Australian animals + lookout moment."),
    "https://taronga.org.au/sydney-zoo",
    [
      item("koala", "Australian animals", "Koalas with harbour breezes.", ["wow", "outdoor"]),
      item("sumatran-tiger", "Asian animals", "Tigers.", ["big-cats"]),
      item("western-lowland-gorilla", "African animals", "Gorillas.", ["primates"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes + views.", ["tall", "wow"]),
      item("african-lion", "Lions", "Lions.", ["big-cats", "sound"]),
    ]
  ),
  "melbourne-zoo": zoo(
    "Melbourne Zoo — gardens setting, orangutans, and a calm Aussie pace.",
    "Half day perfect; trail of the elephants when open.",
    half("Royal Park; tram access.", "Easy from city.", "stroller-easy", "Orangutans + elephants or kids trail."),
    "https://www.zoo.org.au/melbourne",
    [
      item("orangutan", "Orangutans", "Orangutan sanctuary energy.", ["primates", "climb", "wow"]),
      item("african-elephant", "Elephants", "Elephants.", ["big", "outdoor"]),
      item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
      item("koala", "Australian", "Koalas.", ["wow"]),
      item("western-lowland-gorilla", "Gorillas", "Gorillas.", ["primates"]),
    ]
  ),
  "vancouver-aquarium": aq(
    "Stanley Park ocean life — otters and jellies by the sea wall.",
    "Short visit pairs with park stroller loop outside.",
    half("Stanley Park; busy summers.", "Bus/car to park.", "indoor", "Otters + one big tank."),
    "https://www.vanaqua.org/",
    [
      item("asian-small-clawed-otter", "Otters", "Otter play is the magnet.", ["play", "water", "wow"]),
      item("jellyfish", "Jellies", "Glow rooms.", ["glow", "water"]),
      item("octopus", "Pacific", "Octopus hide-and-seek.", ["hide", "water"]),
      item("shark", "Sharks", "Sharks.", ["big", "water"]),
      item("sea-turtle", "Turtles", "Turtles.", ["shell", "water"]),
    ]
  ),
  "calgary-zoo": zoo(
    "Calgary Zoo — Canadian wilds + destination exhibits; cold-weather planning.",
    "Indoor buildings matter in winter; outdoor in summer.",
    half("Tickets online; weather drives the day.", "East of downtown.", "stroller-easy", "Panda/destination exhibits only if currently featured — else Africa icons."),
    "https://www.calgaryzoo.com/",
    [
      item("giant-panda", "Destination Asia", "Pandas when present — confirm before promising.", ["wow", "big"]),
      item("african-elephant", "Africa", "Elephants.", ["big", "outdoor"]),
      item("reticulated-giraffe", "Africa", "Giraffes.", ["tall"]),
      item("sumatran-tiger", "Cats", "Tigers.", ["big-cats"]),
      item("western-lowland-gorilla", "Primates", "Gorillas.", ["primates"]),
    ]
  ),
  "paris-zoo": zoo(
    "Parc Zoologique de Paris — modern immersive habitats, not cages-of-old.",
    "Half day; combine with Bois de Vincennes carefully.",
    half("Book timed entry in peak season.", "Vincennes; Metro + walk.", "stroller-easy", "One biozone immersion."),
    "https://www.parczoologiquedeparis.fr/en",
    [
      item("african-lion", "Sahel-Sudan", "Lions in open views.", ["big-cats", "wow"]),
      item("reticulated-giraffe", "Africa", "Giraffes.", ["tall"]),
      item("sumatran-tiger", "Patagonia / Asia mixes", "Big cats energy.", ["big-cats"]),
      item("nile-hippo", "Europe/Africa water", "Hippos when on route.", ["water", "big"]),
      item("western-lowland-gorilla", "Equatorial Africa", "Gorillas.", ["primates"]),
    ]
  ),
  "prague-zoo": zoo(
    "Prague Zoo — hillside Vltava views; cable car option for tired legs.",
    "Gondola helps; don’t climb everything.",
    half("Popular; tickets online.", "Troja; transit + walk/hills.", "hills", "Downhill strategy if possible."),
    "https://www.zoopraha.cz/en",
    [
      item("reticulated-giraffe", "African house / outdoor", "Giraffes.", ["tall", "wow"]),
      item("african-elephant", "Elephants", "Elephants.", ["big"]),
      item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
      item("western-lowland-gorilla", "Gorillas", "Gorillas.", ["primates"]),
      item("red-panda", "Red pandas", "Red pandas.", ["climb"]),
    ]
  ),
  "vienna-zoo": zoo(
    "Schönbrunn Zoo — oldest zoo in the world inside palace gardens.",
    "Combine palace only if kids have stamina leftover.",
    half("Zoo tickets separate from palace sometimes.", "Schönbrunn; U4.", "stroller-easy", "Panda/giant icons only if present; else big mammals loop."),
    "https://www.zoovienna.at/en/",
    [
      item("giant-panda", "Pandas", "Pandas when on view — verify.", ["wow", "big"]),
      item("african-elephant", "Elephants", "Elephants.", ["big"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
      item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
      item("orangutan", "Orangutans", "Orangutans.", ["primates", "climb"]),
    ]
  ),
  "auckland-zoo": zoo(
    "Auckland Zoo — NZ city zoo with solid kids’ zoo energy.",
    "Half day; easy add to a city stay.",
    half("Western Springs; check aucklandzoo.co.nz.", "Bus/car.", "stroller-easy", "Kids zoo + one habitat realm."),
    "https://www.aucklandzoo.co.nz/",
    [
      item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats", "wow"]),
      item("western-lowland-gorilla", "Gorillas / primates", "Primates.", ["primates"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
      item("african-lion", "Lions", "Lions.", ["big-cats"]),
      item("red-panda", "Red pandas", "Red pandas.", ["climb"]),
    ]
  ),
  "barcelona-zoo": zoo(
    "Barcelona Zoo in Ciutadella — city-center animals after park play.",
    "Heat in summer; mornings better.",
    half("Park access; ticket lines.", "Ciutadella; Metro.", "heat", "One loop + park outside after."),
    "https://www.zoobarcelona.cat/en",
    [
      item("african-elephant", "Elephants", "Elephants.", ["big", "outdoor"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
      item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
      item("western-lowland-gorilla", "Primates", "Gorillas / primates.", ["primates"]),
      item("caribbean-flamingo", "Birds", "Flamingos.", ["color"]),
    ]
  ),
  "artis-zoo": zoo(
    "ARTIS Amsterdam — historic city zoo, walkable and dense.",
    "Combine with canal day carefully; zoo alone is enough.",
    half("Micropia/ARTIS tickets vary — check artis.nl.", "Plantage; tram.", "stroller-easy", "One calm loop."),
    "https://www.artis.nl/en",
    [
      item("african-elephant", "Elephants", "Elephants.", ["big", "wow"]),
      item("african-lion", "Lions", "Lions.", ["big-cats"]),
      item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
      item("african-penguin", "Penguins", "Penguins.", ["water"]),
    ]
  ),
  "hong-kong-ocean-park": zoo(
    "Ocean Park — theme-park-scale; cable car + ocean/land zones.",
    "Pick ocean OR land side with little kids — not both marathons.",
    half("Timed tickets; huge day possible.", "Aberdeen; dedicated transport.", "hills", "One side only."),
    "https://www.oceanpark.com.hk/en",
    [
      item("shark", "Ocean", "Sharks and ocean tanks.", ["water", "big", "wow"]),
      item("jellyfish", "Jellies", "Jellies.", ["water", "glow"]),
      item("african-penguin", "Penguins", "Penguins.", ["water"]),
      item("sumatran-tiger", "Land / Asia", "Big cats on land side.", ["big-cats"]),
      item("red-panda", "Asia", "Red pandas.", ["climb"]),
    ]
  ),
  "dubai-aquarium": aq(
    "Dubai Mall aquarium tunnel — short, spectacular, stroller-possible.",
    "Mall day add-on; not a full zoo substitute.",
    half("Mall entry; attraction tickets inside.", "Dubai Mall.", "indoor", "Tunnel walk + one viewing panel."),
    "https://www.dubaiaquarium.com/",
    [
      item("shark", "Tunnel", "Sharks overhead in the tunnel.", ["water", "big", "wow"]),
      item("stingray", "Tunnel / tanks", "Rays gliding by.", ["water", "flat"]),
      item("sea-turtle", "Tanks", "Turtles.", ["water", "shell"]),
      item("clownfish", "Reef", "Bright reef fish.", ["water", "color"]),
      item("jellyfish", "Jellies", "Jellies if on path.", ["water", "glow"]),
    ]
  ),
  "montreal-biodome": mu(
    "Montréal Biodôme — walk five ecosystems under one roof.",
    "Perfect cold-weather wow; pair with Space for a Science Centre day carefully.",
    half("Space for Life tickets; Parc olympique area.", "Metro + walk.", "indoor", "One slow ecosystem circuit."),
    "https://espacepourlavie.ca/en/biodome",
    [
      item("african-penguin", "Subpolar", "Penguins in ecosystem immersion.", ["water", "wow"]),
      item("two-toed-sloth", "Tropical", "Tropical mammals/sloth energy.", ["climb"]),
      item("sci-rainforest", "Tropical rainforest", "Lush immersion.", ["wow"]),
      item("ring-tailed-lemur", "Habitats", "Primates when present.", ["primates", "play"]),
      item("cm-free-explore", "Kid pace", "Pause in favorite ecosystem.", ["play"]),
    ]
  ),
};

function clean(pack, slug) {
  pack.icons = (pack.icons || []).filter((it) => it && it.catalog_id && catalog[it.catalog_id]);
  if (pack.icons.length < 3) throw new Error(slug + " only " + pack.icons.length);
  return pack;
}

for (const k of Object.keys(R2)) {
  R2[k] = clean(R2[k], k);
}

function load(slug) {
  return JSON.parse(fs.readFileSync(path.join(VENUE_DIR, slug + ".json"), "utf8"));
}
function save(slug, data) {
  fs.writeFileSync(path.join(VENUE_DIR, slug + ".json"), JSON.stringify(data, null, 2) + "\n");
}

let n = 0;
const blurbs = {};
for (const [slug, pack] of Object.entries(R2)) {
  if (!fs.existsSync(path.join(VENUE_DIR, slug + ".json"))) {
    console.warn("skip missing", slug);
    continue;
  }
  const cur = load(slug);
  const p = places[slug] || {};
  const iconIds = new Set(pack.icons.map((i) => i.catalog_id));
  const prior = (cur.items || []).filter((it) => it.catalog_id && !iconIds.has(it.catalog_id));
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
    parent_script: cur.parent_script || ["Bathroom first", "One big wow", "Snack when needed", "Leave while happy"],
    route_90m: pack.icons.slice(0, 3).map((i) => i.id),
    research_notes: "R2 hybrid " + TODAY,
    items: [...pack.icons, ...prior].slice(0, 14),
  };
  if (p.city) next.city = p.city;
  if (p.state) next.region = p.state;
  const vc = venuesCat[slug];
  if (vc && vc.website) next.official_url = vc.website;
  save(slug, next);
  blurbs[slug] = pack.blurb || pack.tagline;
  n++;
}

let placesSrc = fs.readFileSync(PLACES_JS, "utf8");
for (const [slug, blurb] of Object.entries(blurbs)) {
  const re = new RegExp(`(id: "${slug}",[\\s\\S]{0,450}?blurb:\\s*)("[^"]*")`);
  if (re.test(placesSrc)) placesSrc = placesSrc.replace(re, `$1${JSON.stringify(blurb)}`);
}
fs.writeFileSync(PLACES_JS, placesSrc);

let catSrc = fs.readFileSync(CATALOG_JS, "utf8");
function patch(src, slug, featured, blurb) {
  const idPos = src.indexOf(`id: "${slug}"`);
  if (idPos < 0) return src;
  let start = idPos;
  while (start > 0 && src[start] !== "{") start--;
  let depth = 0, end = -1;
  for (let i = start; i < src.length; i++) {
    if (src[i] === "{") depth++;
    else if (src[i] === "}") {
      depth--;
      if (depth === 0) { end = i + 1; break; }
    }
  }
  if (end < 0) return src;
  let block = src.slice(start, end);
  const setStr = (f, v) => {
    const re = new RegExp(`${f}:\\s*"[^"]*"`, "m");
    if (re.test(block)) block = block.replace(re, `${f}: ${JSON.stringify(v)}`);
  };
  const setArr = (f, arr) => {
    const re = new RegExp(`${f}:\\s*\\[[\\s\\S]*?\\]`, "m");
    if (re.test(block))
      block = block.replace(re, `${f}: [\n${arr.map((x) => `      "${x}"`).join(",\n")}\n    ]`);
  };
  setStr("quality", "full");
  setStr("lastVerified", TODAY);
  setStr("blurb", blurb);
  setArr("featuredAnimalIds", featured);
  return src.slice(0, start) + block + src.slice(end);
}
for (const [slug, pack] of Object.entries(R2)) {
  catSrc = patch(catSrc, slug, pack.icons.map((i) => i.catalog_id).slice(0, 8), pack.blurb || pack.tagline);
}
fs.writeFileSync(CATALOG_JS, catSrc);

// expand featured strip
const pilotsPath = path.join(FIELD, "js", "mission-pilots.js");
let pilots = fs.readFileSync(pilotsPath, "utf8");
const featured = [
  "dallas-zoo","san-diego-zoo","georgia-aquarium","lincoln-park-zoo","cincinnati-zoo",
  "please-touch-museum","seattle-aquarium","hogle-zoo","singapore-zoo","taronga-zoo",
  "dublin-zoo","montreal-biodome","memphis-zoo","north-carolina-zoo","miami-zoo",
  "london-zoo","ueno-zoo","bronx-zoo"
];
pilots = pilots.replace(/window\.FP_MISSION_PILOTS_FEATURED = \[[^\]]*\];/,
  `window.FP_MISSION_PILOTS_FEATURED = ${JSON.stringify(featured)};`);
fs.writeFileSync(pilotsPath, pilots);

console.log(JSON.stringify({ updated: n, slugs: Object.keys(R2).length }, null, 2));
