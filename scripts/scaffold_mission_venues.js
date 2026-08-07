#!/usr/bin/env node
/**
 * Scaffold mission venue JSON for every catalog venue that lacks one.
 * Preserves existing hand-tuned files (dallas, london, …) unless --force.
 *
 * Usage (repo root):
 *   node scripts/scaffold_mission_venues.js
 *   node scripts/scaffold_mission_venues.js --force-slug=houston-zoo
 */
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const REPO = path.resolve(__dirname, "..");
const FIELD = path.join(REPO, "static", "field-pack");
const VENUE_DIR = path.join(FIELD, "data", "venues");
const OUT_PILOTS = path.join(FIELD, "js", "mission-pilots.js");

const args = new Set(process.argv.slice(2));
const forceAll = args.has("--force");
const forceSlug = [...args].find((a) => a.startsWith("--force-slug="))?.split("=")[1];

function loadBrowserJs(rel) {
  const ctx = { window: {}, console };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(FIELD, rel), "utf8"), ctx);
  return ctx.window;
}

const w = loadBrowserJs("js/catalog.js");
Object.assign(w, loadBrowserJs("js/places-data.js"));

const catalog = w.FIELD_PACK_CATALOG || {};
const venues = w.FIELD_PACK_VENUES || {};
const places = w.FP_PLACES || [];
const topIds = new Set(w.FP_TOP_PLACE_IDS || []);
const placeById = Object.fromEntries(places.map((p) => [p.id, p]));

const TYPE_MAP = {
  zoo: "zoo",
  safari_zoo: "safari_zoo",
  zoo_aq: "zoo",
  aquarium: "aquarium",
  aq: "aquarium",
  sci_aq: "aquarium",
  childrens_museum: "museum",
  cm: "museum",
  science: "museum",
  sci: "museum",
  natural_history: "museum",
  nh: "museum",
  space: "museum",
};

/** Keyword → tags for mission scoring */
function tagsFor(itemId, name, blurb) {
  const s = `${itemId} ${name} ${blurb}`.toLowerCase();
  const tags = new Set(["wow"]);
  const rules = [
    [/elephant|mammoth/, ["big", "outdoor"]],
    [/giraffe/, ["tall", "outdoor"]],
    [/lion|tiger|cheetah|leopard|jaguar/, ["big-cats", "outdoor"]],
    [/gorilla|orangutan|chimp|ape|monkey|lemur/, ["outdoor", "play"]],
    [/panda|bear|koala/, ["outdoor", "wow"]],
    [/penguin|seal|otter|walrus|dolphin|whale/, ["water", "outdoor"]],
    [/shark|ray|turtle|jelly|octopus|seahorse|fish|eel|crab|star|coral|anemone/, ["water"]],
    [/bird|eagle|owl|parrot|flamingo|peacock/, ["outdoor"]],
    [/reptile|snake|crocodile|alligator|lizard|tortoise|turtle/, ["outdoor"]],
    [/dino|fossil|skeleton|gem|planet|space|rocket|shuttle|train|submarine/, ["wow", "read"]],
    [/climb|splash|build|play|water table|maker|art/, ["hands", "play"]],
    [/rest|cafe|playground|kids/, ["rest", "kids"]],
  ];
  for (const [re, t] of rules) {
    if (re.test(s)) t.forEach((x) => tags.add(x));
  }
  if (tags.size === 1) tags.add("outdoor");
  return [...tags];
}

function qaFor(name, type) {
  const n = (name || "this").replace(/[.!?].*$/, "").trim();
  if (type === "aquarium" || /shark|ray|fish|jelly|octopus|turtle|seahorse/i.test(n)) {
    return {
      question: `What did you notice about the ${n}?`,
      answer: "Something about how it moves, its shape, or its home in the water!",
    };
  }
  if (type === "museum") {
    return {
      question: `What did you try or notice at ${n}?`,
      answer: "Tell a grown-up one thing you saw, touched, or built!",
    };
  }
  return {
    question: `What is special about the ${n}?`,
    answer: "Tell a grown-up one thing you noticed — size, color, sound, or how it moves!",
  };
}

function sanitizeLine(text, ownCity, ownName) {
  let t = String(text || "")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, 100);
  // Strip common city leak patterns that aren't our venue
  if (ownCity && ownCity.length >= 4) {
    /* keep own city if present — rare in blurbs */
  }
  // Remove other famous zoo name drops
  t = t.replace(/\b(Dallas Zoo|London Zoo|Ueno Zoo|feeding platform)\b/gi, "this place");
  return t;
}

function normalizeType(raw) {
  const t = (raw || "zoo").toLowerCase();
  return TYPE_MAP[t] || (t.includes("aqua") ? "aquarium" : t.includes("museum") || t.includes("sci") ? "museum" : "zoo");
}

function itemFromCatalog(catalogId, missionType, ownCity, ownName) {
  const it = catalog[catalogId];
  if (!it) return null;
  const label = it.name || catalogId;
  const one = sanitizeLine(it.blurb || `Find the ${label}.`, ownCity, ownName);
  const id = String(catalogId)
    .replace(/[^a-z0-9]+/gi, "_")
    .replace(/^_|_$/g, "")
    .slice(0, 28);
  return {
    id: id || catalogId,
    label,
    emoji: it.emoji || "📍",
    one_liner: one || `Find the ${label}.`,
    tags: tagsFor(catalogId, label, one),
    age_fit: ["2-3", "4-5", "6-8", "9+"],
    zone: missionType === "aquarium" ? "Galleries" : missionType === "museum" ? "Halls" : "Grounds",
    qa_card: qaFor(label, missionType),
    catalog_id: catalogId,
  };
}

function padItems(items, missionType) {
  const pads = [
    {
      id: "kids_rest",
      label: "Kids rest / play stop",
      emoji: "🛝",
      one_liner: "Take a break, then keep exploring.",
      tags: ["rest", "kids"],
      age_fit: ["2-3", "4-5", "6-8"],
      zone: "",
      qa_card: {
        question: "Did a rest stop help?",
        answer: "Breaks help little legs finish the day!",
      },
    },
    {
      id: "favorite_photo",
      label: "Favorite photo spot",
      emoji: "📷",
      one_liner: "Snap one favorite (or draw it later).",
      tags: ["wow"],
      age_fit: ["2-3", "4-5", "6-8", "9+"],
      zone: "",
      qa_card: {
        question: "What was your favorite thing to photograph?",
        answer: "Whatever made you smile — that is the right answer!",
      },
    },
    {
      id: "something_tall",
      label: "Something taller than you",
      emoji: "📏",
      one_liner: "Point to something huge.",
      tags: ["tall", "wow"],
      age_fit: ["2-3", "4-5", "6-8", "9+"],
      zone: "",
      qa_card: {
        question: "What was taller than you?",
        answer: "Buildings, trees, giraffes, dinosaurs — lots of tall wonders!",
      },
    },
  ];
  const out = [...items];
  let i = 0;
  while (out.length < 8 && i < pads.length) {
    const p = pads[i++];
    if (!out.some((x) => x.id === p.id)) out.push({ ...p });
  }
  return out;
}

function buildVenue(slug) {
  const v = venues[slug];
  if (!v) return null;
  const p = placeById[slug] || {};
  const missionType = normalizeType(v.type || p.type);
  const loc = v.location || [p.city, p.state].filter(Boolean).join(", ");
  const [cityPart, regionPart] = loc.split(",").map((s) => (s || "").trim());
  const city = p.city || cityPart || "Unknown";
  const region = p.state || regionPart || "";
  const ownName = v.name || p.name || slug;

  const ids = [...(v.animalIds || v.featuredAnimalIds || [])];
  const seen = new Set();
  const items = [];
  for (const cid of ids) {
    if (seen.has(cid)) continue;
    seen.add(cid);
    const row = itemFromCatalog(cid, missionType, city, ownName);
    if (row) items.push(row);
  }
  const padded = padItems(items, missionType);
  if (padded.length < 6) return null;

  return {
    slug,
    name: ownName,
    type: missionType,
    city,
    region,
    country: p.country && p.country !== "US" ? p.country : p.country || "US",
    lat: p.lat || 0,
    lng: p.lon || 0,
    official_url: v.website || "",
    last_verified: "2026-08-07",
    verified_by: "catalog-scaffold",
    status: padded.length >= 8 ? "verified" : "unverified",
    tagline: sanitizeLine(v.blurb || p.blurb || `Kid shortlist for ${ownName}.`, city, ownName),
    practical: {
      typical_duration: "half day",
      ticket_note: "Check the official site for tickets and hours.",
      transit_note: "",
    },
    items: padded,
  };
}

function shouldWrite(slug) {
  const dest = path.join(VENUE_DIR, `${slug}.json`);
  if (!fs.existsSync(dest)) return true;
  if (forceAll || forceSlug === slug) return true;
  // Preserve hand-tuned
  try {
    const cur = JSON.parse(fs.readFileSync(dest, "utf8"));
    if (cur.verified_by === "owner" || cur.verified_by === "research") return false;
    // Keep existing scaffold unless force
    return false;
  } catch {
    return true;
  }
}

fs.mkdirSync(VENUE_DIR, { recursive: true });

let written = 0;
let skipped = 0;
let failed = 0;
const allSlugs = Object.keys(venues).sort();

for (const slug of allSlugs) {
  if (!shouldWrite(slug)) {
    skipped++;
    continue;
  }
  const data = buildVenue(slug);
  if (!data) {
    failed++;
    console.warn("skip (insufficient items):", slug);
    continue;
  }
  fs.writeFileSync(path.join(VENUE_DIR, `${slug}.json`), JSON.stringify(data, null, 2) + "\n");
  written++;
}

// Collect all pilot slugs on disk
const pilotIds = fs
  .readdirSync(VENUE_DIR)
  .filter((f) => f.endsWith(".json"))
  .map((f) => f.replace(/\.json$/, ""))
  .filter((id) => venues[id] || placeById[id])
  .sort();

/** Featured strip on landing — top tier + a few intl flagships */
const FEATURED_ORDER = [
  "dallas-zoo",
  "fort-worth-zoo",
  "childrens-aquarium-dallas",
  "childrens-museum-perot",
  "houston-zoo",
  "georgia-aquarium",
  "shedd-aquarium",
  "monterey-bay-aquarium",
  "san-diego-zoo",
  "national-zoo",
  "bronx-zoo",
  "amnh",
  "field-museum",
  "kennedy-space-center",
  "london-zoo",
  "ueno-zoo",
  "singapore-zoo",
  "taronga-zoo",
];
const featured = FEATURED_ORDER.filter((id) => pilotIds.includes(id));

const pilotsJs = `/** Auto-generated by scripts/scaffold_mission_venues.js — do not edit by hand */
window.FP_MISSION_PILOTS = ${JSON.stringify(pilotIds)};
window.FP_MISSION_PILOTS_FEATURED = ${JSON.stringify(featured)};
window.FP_MISSION_PILOT_SET = new Set(window.FP_MISSION_PILOTS);
`;
fs.writeFileSync(OUT_PILOTS, pilotsJs);

console.log(
  JSON.stringify(
    {
      catalog: allSlugs.length,
      written,
      skippedExisting: skipped,
      failed,
      pilotsOnDisk: pilotIds.length,
      featured: featured.length,
      out: path.relative(REPO, OUT_PILOTS),
    },
    null,
    2
  )
);
