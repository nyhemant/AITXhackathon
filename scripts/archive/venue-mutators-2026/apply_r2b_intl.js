#!/usr/bin/env node
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const FIELD = path.join(__dirname, "..", "static", "field-pack");
const VENUE_DIR = path.join(FIELD, "data", "venues");
const TODAY = new Date().toISOString().slice(0, 10);
const ctx = { window: {}, console };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(FIELD, "js/catalog.js"), "utf8"), ctx);
vm.runInContext(fs.readFileSync(path.join(FIELD, "js/places-data.js"), "utf8"), ctx);
const catalog = ctx.window.FIELD_PACK_CATALOG;
const venuesCat = ctx.window.FIELD_PACK_VENUES;
const places = Object.fromEntries((ctx.window.FP_PLACES || []).map((p) => [p.id, p]));

function item(id, zone, one, tags) {
  const it = catalog[id];
  if (!it) throw new Error("missing " + id);
  return {
    id: id.replace(/-/g, "_").slice(0, 28),
    label: it.name,
    emoji: it.emoji || "📍",
    one_liner: one || it.blurb,
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

function P(type, tagline, blurb, practical, mapPage, mapAttr, icons) {
  return { type, tagline, blurb, practical, mapPage, mapAttr, icons };
}
const half = (a, b, c, d) => ({
  typical_duration: "half day",
  ticket_note: a,
  transit_note: b,
  energy_note: c,
  best_start: d,
});

const packs = {
  "beijing-zoo": P("zoo", "Beijing Zoo — pandas are the magnet; verify viewing rules before you go.", "Giant pandas first if open; don’t promise every hall.", half("Panda houses can have lines — check current access.", "Beijing Zoo station area.", "stroller-easy", "Pandas if available, then one more loop."), "https://www.beijingzoo.com/", "Beijing Zoo", [
    item("giant-panda", "Pandas", "Pandas when accessible — the reason many visit.", ["wow", "big"]),
    item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
    item("african-elephant", "Elephants", "Elephants.", ["big"]),
    item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
    item("red-panda", "Red pandas", "Red pandas.", ["climb"]),
  ]),
  "osaka-aquarium": P("aquarium", "Kaiyukan — whale shark fame in a spiral building.", "Start at the biggest tank story; spiral is the experience.", half("Popular; tickets ahead in peak.", "Osaka bay area.", "indoor", "Biggest tank first."), "https://www.kaiyukan.com/language/eng/", "Kaiyukan", [
    item("shark", "Pacific tank", "Whale-shark-scale wow in the huge tank.", ["water", "big", "wow"]),
    item("stingray", "Tanks", "Rays.", ["water", "flat"]),
    item("jellyfish", "Jellies", "Jellies.", ["water", "glow"]),
    item("sea-turtle", "Turtles", "Turtles.", ["water", "shell"]),
    item("octopus", "Octopus", "Octopus.", ["water", "hide"]),
  ]),
  "two-oceans-aquarium": P("aquarium", "Cape Town waterfront — two oceans story.", "V&A Waterfront indoor wow; pair outdoor plans carefully.", half("Waterfront location.", "V&A Waterfront.", "indoor", "Predator exhibit energy first."), "https://www.aquarium.co.za/", "Two Oceans Aquarium", [
    item("shark", "Predators", "Sharks.", ["water", "big", "wow"]),
    item("african-penguin", "Penguins", "Penguin connections to the Cape.", ["water", "wow"]),
    item("jellyfish", "Jellies", "Jellies.", ["water", "glow"]),
    item("stingray", "Rays", "Rays.", ["water", "flat"]),
    item("sea-turtle", "Turtles", "Turtles.", ["water", "shell"]),
  ]),
  "lisbon-zoo": P("zoo", "Lisbon Zoo — cable car option and classic European zoo day.", "Hills and heat; cable car can save little legs.", half("Extras like cable car cost more.", "Sete Rios area.", "hills", "One loop + shade."), "https://www.zoo.pt/en", "Lisbon Zoo", [
    item("african-elephant", "Elephants", "Elephants.", ["big", "wow"]),
    item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
    item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
    item("western-lowland-gorilla", "Gorillas", "Gorillas.", ["primates"]),
    item("african-lion", "Lions", "Lions.", ["big-cats"]),
  ]),
  "madrid-zoo": P("zoo", "Madrid Zoo Aquarium — combined day is big; pick a focus.", "Pick zoo OR aquarium emphasis with little kids.", half("Casa de Campo area.", "Cable car / bus options.", "heat", "Morning; one half of the park."), "https://www.zoomadrid.com/en", "Zoo Aquarium de Madrid", [
    item("african-elephant", "Elephants", "Elephants.", ["big"]),
    item("shark", "Aquarium", "Sharks if you do the aquarium side.", ["water", "big"]),
    item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
    item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
    item("western-lowland-gorilla", "Gorillas", "Gorillas.", ["primates"]),
  ]),
  "munich-zoo": P("zoo", "Hellabrunn Munich — geo-zoo idea, Isar river setting.", "Spacious habitats; half day with a clear realm pick.", half("Check hellabrunn.de.", "Thalkirchen.", "stroller-easy", "One continent zone."), "https://www.hellabrunn.de/en/", "Tierpark Hellabrunn", [
    item("african-elephant", "Elephants", "Elephants.", ["big", "wow"]),
    item("western-lowland-gorilla", "Gorillas", "Gorillas.", ["primates"]),
    item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
    item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
    item("african-lion", "Lions", "Lions.", ["big-cats"]),
  ]),
  "stockholm-skansen": P("museum", "Skansen — open-air museum + Nordic animals.", "Not a classic safari zoo; historic Sweden + some animals.", half("Djurgården island access.", "Ferry/tram to Djurgården.", "hills", "Kid pace through yards + animal stops."), "https://skansen.se/en/", "Skansen", [
    item("cm-outdoor", "Historic yards", "Outdoor cultural paths.", ["outdoor", "play"]),
    item("cm-free-explore", "Kid lead", "They pick a cottage or animal stop.", ["play"]),
    item("red-panda", "Animals", "Red pandas if on animal route.", ["climb"]),
    item("sci-hands-on", "Discovery", "Hands-on kids corners.", ["hands"]),
    item("cm-toddler-garden", "Little kids", "Softer resets.", ["rest", "play"]),
  ]),
  "taipei-zoo": P("zoo", "Taipei Zoo — giant pandas and a large East Asian campus.", "Panda first if that’s the goal; otherwise one area only.", half("MRT to zoo; crowds at pandas.", "Wenhu line.", "stroller-easy", "Pandas if open, else one loop."), "https://www.zoo.gov.taipei/", "Taipei Zoo", [
    item("giant-panda", "Pandas", "Pandas when viewing is open.", ["wow", "big"]),
    item("red-panda", "Red pandas", "Red pandas.", ["climb"]),
    item("african-elephant", "Elephants", "Elephants.", ["big"]),
    item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
    item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
  ]),
  "seoul-zoo": P("zoo", "Seoul Grand Park zoo — huge; plan like a park day.", "Don’t combine every Grand Park attraction.", half("Grand Park complex.", "Seoul Grand Park station.", "hills", "One zoo loop only."), "https://grandpark.seoul.go.kr/", "Seoul Grand Park Zoo", [
    item("african-elephant", "Elephants", "Elephants.", ["big"]),
    item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
    item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
    item("western-lowland-gorilla", "Gorillas", "Gorillas.", ["primates"]),
    item("red-panda", "Red pandas", "Red pandas.", ["climb"]),
  ]),
  "perth-zoo": P("zoo", "Perth Zoo — intimate Aussie zoo with strong kids’ focus.", "Half day; easy city add-on.", half("South Perth.", "Bus/ferry options.", "heat", "Australian animals + shade."), "https://perthzoo.wa.gov.au/", "Perth Zoo", [
    item("koala", "Australian", "Koalas.", ["wow"]),
    item("orangutan", "Orangutans", "Orangutans.", ["primates", "climb", "wow"]),
    item("african-lion", "Lions", "Lions.", ["big-cats"]),
    item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
    item("african-elephant", "Elephants", "Elephants.", ["big"]),
  ]),
  "wellington-zoo": P("zoo", "Wellington Zoo — hilltop city zoo, compact visit.", "Bus up; shorter than mega zoos.", half("Hill suburb.", "Bus from city.", "hills", "One loop."), "https://wellingtonzoo.com/", "Wellington Zoo", [
    item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats", "wow"]),
    item("chimpanzee", "Chimps", "Chimps.", ["primates", "play"]),
    item("western-lowland-gorilla", "Primates", "Gorillas / primates.", ["primates"]),
    item("red-panda", "Red pandas", "Red pandas.", ["climb"]),
    item("african-lion", "Lions", "Lions.", ["big-cats"]),
  ]),
  "budapest-zoo": P("zoo", "Budapest Zoo — historic setting by City Park.", "City-center dense zoo; half day max.", half("City Park area.", "Heroes’ Square area.", "stroller-easy", "One calm circuit."), "https://www.zoobudapest.com/en", "Budapest Zoo", [
    item("african-elephant", "Elephants", "Elephants.", ["big"]),
    item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
    item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
    item("western-lowland-gorilla", "Gorillas", "Gorillas.", ["primates"]),
    item("african-penguin", "Penguins", "Penguins.", ["water"]),
  ]),
  "copenhagen-zoo": P("zoo", "Copenhagen Zoo — spiral tower and modern habitats.", "Tower views optional; animals first.", half("Frederiksberg.", "Metro/bus.", "stroller-easy", "One habitat realm."), "https://www.zoo.dk/en", "Copenhagen Zoo", [
    item("african-elephant", "Elephants", "Elephants.", ["big", "wow"]),
    item("reticulated-giraffe", "Giraffes", "Giraffes — tower views nearby.", ["tall", "wow"]),
    item("african-lion", "Lions", "Lions.", ["big-cats"]),
    item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
    item("western-lowland-gorilla", "Gorillas", "Gorillas.", ["primates"]),
  ]),
  "shanghai-ocean-aquarium": P("aquarium", "Shanghai ocean tunnel — long underwater walk wow.", "Short focused tourist aquarium visit.", half("People’s Square area.", "Metro.", "indoor", "Tunnel walk."), "https://www.aquarium.sh.com/", "Shanghai Ocean Aquarium", [
    item("shark", "Tunnel", "Sharks overhead.", ["water", "big", "wow"]),
    item("stingray", "Tanks", "Rays.", ["water", "flat"]),
    item("jellyfish", "Jellies", "Jellies.", ["water", "glow"]),
    item("sea-turtle", "Turtles", "Turtles.", ["water", "shell"]),
    item("clownfish", "Reef", "Reef colors.", ["water", "color"]),
  ]),
  "nhm-london": P("museum", "London NHM — free Hintze Hall wow and dinos.", "Pick dinosaurs or mammals; don’t marathon.", half("Free entry; special exhibits ticketed.", "South Kensington.", "indoor", "Hintze Hall + one gallery."), "https://www.nhm.ac.uk/", "Natural History Museum", [
    item("sci-dinosaur", "Dinosaurs", "Dinos are the magnet.", ["wow", "read"]),
    item("sci-mammal-hall", "Mammals", "Mammals and giant life.", ["wow"]),
    item("sci-planet", "Earth", "Earth galleries.", ["wow"]),
    item("sci-hands-on", "Investigate", "Hands-on when open.", ["hands"]),
    item("cm-free-explore", "Kid pick", "They choose next.", ["play"]),
  ]),
};

let n = 0;
const blurbs = {};
for (const [slug, pack] of Object.entries(packs)) {
  const fp = path.join(VENUE_DIR, slug + ".json");
  if (!fs.existsSync(fp)) {
    console.warn("miss", slug);
    continue;
  }
  const cur = JSON.parse(fs.readFileSync(fp, "utf8"));
  if (cur.content_mode === "curated") continue;
  const iconIds = new Set(pack.icons.map((i) => i.catalog_id));
  const prior = (cur.items || []).filter((it) => it.catalog_id && !iconIds.has(it.catalog_id));
  const p = places[slug] || {};
  const next = {
    ...cur,
    type: pack.type,
    content_mode: "hybrid",
    verified_by: "research",
    last_verified: new Date().toISOString().slice(0, 10),
    status: "verified",
    tagline: pack.tagline,
    practical: pack.practical,
    media: {
      visitor_map_url: "",
      visitor_map_page: pack.mapPage,
      visitor_map_kind: "page",
      map_attribution: pack.mapAttr,
    },
    parent_script: cur.parent_script || ["Bathroom first", "One big wow", "Snack when needed", "Leave while happy"],
    route_90m: pack.icons.slice(0, 3).map((i) => i.id),
    research_notes: "R2b " + new Date().toISOString().slice(0, 10),
    items: [...pack.icons, ...prior].slice(0, 14),
  };
  while (next.items.length < 8) {
    next.items.push({
      id: "ex" + next.items.length,
      label: "Kid choice stop",
      emoji: "🧭",
      one_liner: "They pick next for five minutes.",
      tags: ["play"],
      age_fit: ["2-3", "4-5", "6-8", "9+"],
      zone: "Explore",
      qa_card: { question: "Favorite?", answer: "Whatever made you smile!" },
      catalog_id: "cm-free-explore",
    });
  }
  if (p.city) next.city = p.city;
  if (p.state) next.region = p.state;
  if (venuesCat[slug]?.website) next.official_url = venuesCat[slug].website;
  fs.writeFileSync(fp, JSON.stringify(next, null, 2) + "\n");
  blurbs[slug] = pack.blurb;
  n++;
}

let placesSrc = fs.readFileSync(path.join(FIELD, "js/places-data.js"), "utf8");
for (const [slug, blurb] of Object.entries(blurbs)) {
  const re = new RegExp(`(id: "${slug}",[\\s\\S]{0,450}?blurb:\\s*)("[^"]*")`);
  if (re.test(placesSrc)) placesSrc = placesSrc.replace(re, `$1${JSON.stringify(blurb)}`);
}
fs.writeFileSync(path.join(FIELD, "js/places-data.js"), placesSrc);

let catSrc = fs.readFileSync(path.join(FIELD, "js/catalog.js"), "utf8");
function patch(src, slug, featured, blurb) {
  const idPos = src.indexOf(`id: "${slug}"`);
  if (idPos < 0) return src;
  let start = idPos;
  while (start > 0 && src[start] !== "{") start--;
  let depth = 0,
    end = -1;
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
  const setStr = (f, v) => {
    const re = new RegExp(`${f}:\\s*"[^"]*"`, "m");
    if (re.test(block)) block = block.replace(re, `${f}: ${JSON.stringify(v)}`);
  };
  const setArr = (f, arr) => {
    const re = new RegExp(`${f}:\\s*\\[[\\s\\S]*?\\]`, "m");
    if (re.test(block))
      block = block.replace(re, `${f}: [\n${arr.map((x) => `      "${x}"`).join(",\n")}\n    ]`);
  };
  const today = new Date().toISOString().slice(0, 10);
  setStr("quality", "full");
  setStr("lastVerified", today);
  setStr("blurb", blurb);
  setArr("featuredAnimalIds", featured);
  return src.slice(0, start) + block + src.slice(end);
}
for (const [slug, pack] of Object.entries(packs)) {
  catSrc = patch(
    catSrc,
    slug,
    pack.icons.map((i) => i.catalog_id).slice(0, 8),
    pack.blurb
  );
}
fs.writeFileSync(path.join(FIELD, "js/catalog.js"), catSrc);
console.log("updated", n);
