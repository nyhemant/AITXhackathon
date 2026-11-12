// Builds the home map v2 base layers from Natural Earth (public domain) vector data.
// Output: static SVGs (pre-projected, no runtime map library) + pin positions as % of each plate.
import fs from "fs";
import * as d3 from "d3-geo";
import { geoMiller } from "d3-geo-projection";
import * as topo from "topojson-client";

const NE = "ne/";
const OUT = process.argv[2] || "out/";
const read = (f) => JSON.parse(fs.readFileSync(f, "utf8"));
const worldLand = read(NE + "s_world_land.json");
const worldLakes = read(NE + "s_world_lakes.json");
const usLakes = read(NE + "s_us_lakes.json");
const usStates = read(NE + "s_us_states.json");
const countries = read(NE + "s_us_countries1.json");
const venues = read("venues.json");
// d3-geo wants clockwise outer rings; mapshaper writes RFC 7946 (counter-clockwise). Flip any polygon whose area is > a hemisphere.
const rewind = (fc) => { for (const f of fc.features) { const g = f.geometry; if (!g) continue;
  const polys = g.type === "Polygon" ? [g.coordinates] : g.type === "MultiPolygon" ? g.coordinates : [];
  for (const poly of polys) for (const ring of poly) { if (d3.geoArea({ type: "Polygon", coordinates: [ring] }) > 2 * Math.PI) ring.reverse(); } } return fc; };
[worldLand, worldLakes, usLakes, countries].forEach(rewind);

// ---------- World plate: Miller, centred 11.7°E so the seam falls in the Bering Strait (168.3°W); lat 80N..56S.
const WW = 2000;
const world = geoMiller().rotate([-11.7, 0]).scale(1).translate([0, 0]);
const k = WW / (2 * Math.PI);
world.scale(k);
const yTop = world([11.7, 80])[1], yBot = world([11.7, -56])[1];
world.translate([WW / 2, -yTop]);
const WH = Math.round(yBot - yTop);
world.clipExtent([[-8, -8], [WW + 8, WH + 8]]); // clip just outside the plate so no outline runs along its edge

// ---------- US plate: Albers equal-area conic (the familiar US atlas look).
const us = d3.geoAlbers().parallels([29.5, 45.5]).rotate([96, 0]).center([0, 37.5]);
const frame = { type: "MultiPoint", coordinates: [] };
for (let lon = -124.8; lon <= -67; lon += 0.5) { frame.coordinates.push([lon, 24.6], [lon, 50.6]); }
const UW = 1600;
us.fitWidth(UW - 60, frame); // 30px margin each side
let b = d3.geoPath(us).bounds(frame);
const [tx, ty] = us.translate();
us.translate([tx - b[0][0] + 30, ty - b[0][1] + 20]);
b = d3.geoPath(us).bounds(frame);
const UH = Math.round(b[1][1] + 20);
us.clipExtent([[-8, -8], [UW + 8, UH + 8]]);

const pathW = d3.geoPath(world).digits(1);
const pathU = d3.geoPath(us).digits(1);
const gratW = d3.geoGraticule().step([30, 30])();
const gratU = d3.geoGraticule().step([10, 10]).extent([[-140, 15], [-50, 60]])();

const isUSA = (f) => f.properties.name === "United States of America";
const usaFC = { type: "FeatureCollection", features: countries.features.filter(isUSA) };
const otherNA = { type: "FeatureCollection", features: countries.features.filter((f) => !isUSA(f)) };
// Land borders between countries = shared arcs; built from a quick topology of the clipped countries.
import * as topoServer from "topojson-server";
const tp = topoServer.topology({ c: countries }, 1e5);

const P = {
  wLand: pathW(worldLand), wLakes: pathW(worldLakes), wGrat: pathW(gratW),
  uUSA: pathU(usaFC), uOther: pathU(otherNA), uLakes: pathU(usLakes), uStates: pathU(usStates), uGrat: pathU(gratU),
  uBorders: pathU(topo.mesh(tp, tp.objects.c, (a, b2) => a !== b2)),
};

// ---------- Pins, as % of each plate.
const pct = (proj, W, H, lon, lat) => { const [x, y] = proj([lon, lat]); return { x: +(x / W * 100).toFixed(3), y: +(y / H * 100).toFixed(3) }; };
const venuePins = {};
for (const [id, v] of Object.entries(venues)) venuePins[id] = { ...v, us: pct(us, UW, UH, v.lon, v.lat), world: pct(world, WW, WH, v.lon, v.lat) };
// Animal habitat points (real ranges): see notes.md.
const animals = {
  "american-bison": [-103.5, 44.6], // Great Plains / Badlands, South Dakota
  "caribbean-flamingo": [-73.3, 21.1], // Great Inagua, Bahamas
  "galapagos-tortoise": [-91.1, -0.7], // Isabela Island, Galápagos
  "zebra": [35.0, -2.3], // Serengeti, Tanzania
  "giant-panda": [103.0, 30.8], // Sichuan, China
  "sumatran-tiger": [101.5, -1.5], // Kerinci Seblat, Sumatra
  "whale-shark": [72.8, 3.5], // South Ari Atoll, Maldives (year-round whale sharks)
  "koala": [152.5, -28.5], // eastern Australia (QLD/NSW)
};
const animalPins = {};
for (const [id, [lon, lat]] of Object.entries(animals)) animalPins[id] = { lon, lat, world: pct(world, WW, WH, lon, lat) };
const labels = {
  world: {
    "Pacific Ocean": pct(world, WW, WH, -140, 8), "Atlantic Ocean": pct(world, WW, WH, -38, 26), "Indian Ocean": pct(world, WW, WH, 80, -30),
    "Pacific Ocean ": pct(world, WW, WH, 165, 15),
  },
  us: {
    "Pacific Ocean": pct(us, UW, UH, -129, 33), "Atlantic Ocean": pct(us, UW, UH, -69, 33.5), "Gulf of Mexico": pct(us, UW, UH, -89.5, 26),
    "UNITED STATES": pct(us, UW, UH, -99.5, 39.6), "CANADA": pct(us, UW, UH, -103, 50.6), "MEXICO": pct(us, UW, UH, -105, 26.5),
  },
};
// Decoration anchors (lat/lon so they sit on the right water/land).
const deco = {
  world: { compass: pct(world, WW, WH, -150, -40), ship: pct(world, WW, WH, -32, 5), whale: pct(world, WW, WH, -140, 30) },
  us: { compass: pct(us, UW, UH, -127.5, 27.2), liberty: pct(us, UW, UH, -71.6, 39.4), capitol: pct(us, UW, UH, -74.2, 36.3), forest: pct(us, UW, UH, -120.5, 46.2), ship: pct(us, UW, UH, -67, 29.5) },
};
const meta = { world: { W: WW, H: WH }, us: { W: UW, H: UH } };

// ---------- SVG writers
const svg = (W, H, body, extra = "") => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}"${extra}>${body}</svg>\n`;


const PARCH = "data:image/webp;base64," + fs.readFileSync("art/out/tex-parchment-256-v1.webp").toString("base64");
const aSvg = (W, H, land, other, lakes, extras, grat, sw, tex = true) => svg(W, H,
  `<defs><path id="L" d="${land}"/>${other ? `<path id="O" d="${other}"/>` : ""}${tex ? `<pattern id="p" width="${256 * sw}" height="${256 * sw}" patternUnits="userSpaceOnUse"><image href="${PARCH}" width="${256 * sw}" height="${256 * sw}"/></pattern>` : ""}<clipPath id="l"><use href="#L"/></clipPath><mask id="s"><rect width="${W}" height="${H}" fill="#fff"/><use href="#L" fill="#000"/></mask></defs>` +
  `<path d="${grat}" fill="none" stroke="#5f8790" stroke-opacity=".3" stroke-width="${sw * 0.9}" stroke-dasharray="${sw * 6} ${sw * 5}"/>` +
  `<g mask="url(#s)" fill="none" stroke="#3f7f8a" stroke-linejoin="round"><use href="#L" stroke-opacity=".09" stroke-width="${sw * 26}"/><use href="#L" stroke-opacity=".12" stroke-width="${sw * 13}"/><use href="#L" stroke-opacity=".2" stroke-width="${sw * 5}"/></g>` +
  `<use href="#L" fill="${tex ? "url(#p)" : "#f2e3c2"}"/>` +
  (other ? `<use href="#O" fill="#fffaf0" fill-opacity=".42"/>` : "") +
  `<g clip-path="url(#l)" fill="none" stroke-linejoin="round"><use href="#L" stroke="#a5743a" stroke-opacity=".26" stroke-width="${sw * 16}"/><use href="#L" stroke="#8a5a2b" stroke-opacity=".22" stroke-width="${sw * 5}"/></g>` +
  extras +
  `<path d="${lakes}" fill="#b7d8df" stroke="#3d5a5c" stroke-width="${sw * 1.1}"/>` +
  `<use href="#L" fill="none" stroke="#3d4a3f" stroke-width="${sw * 1.7}" stroke-linejoin="round"/>`);
fs.writeFileSync(OUT + "a-world-v1.svg", aSvg(WW, WH, P.wLand, null, P.wLakes, "", P.wGrat, 1));
const uLandAll = P.uUSA + P.uOther;
fs.writeFileSync(OUT + "a-usa-v1.svg", aSvg(UW, UH, uLandAll, P.uOther, P.uLakes,
  `<path d="${P.uStates}" fill="none" stroke="#7a5a36" stroke-opacity=".55" stroke-width="1.4" stroke-dasharray="5 4"/>` +
  `<path d="${P.uBorders}" fill="none" stroke="#7a4a20" stroke-opacity=".8" stroke-width="2.8" stroke-dasharray="10 5"/>`, P.uGrat, 1.25, false));

// B: one self-contained SVG per plate: gradient sea, soft lifted land, white state lines.
const bSvg = (W, H, body, sw) => svg(W, H,
  `<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#dcedf2"/><stop offset="1" stop-color="#c6e0e8"/></linearGradient>` +
  `<filter id="sh" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="${sw * 5}"/></filter></defs>` +
  `<rect width="${W}" height="${H}" fill="url(#g)"/>` + body);
fs.writeFileSync(OUT + "b-world-v1.svg", bSvg(WW, WH,
  `<path d="${P.wGrat}" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="1"/>` +
  `<g filter="url(#sh)" transform="translate(0 4)" fill="#0b4f4a" fill-opacity=".16"><path id="L" d="${P.wLand}"/></g>` +
  `<use href="#L" transform="translate(0 -4)" fill="#f4efe1" fill-opacity="1" stroke="#9fb8a5" stroke-width="1.2" stroke-linejoin="round"/>` +
  `<path d="${P.wLakes}" fill="#cfe5ec" stroke="#9fb8a5" stroke-width=".8"/>`, 1));
fs.writeFileSync(OUT + "b-usa-v1.svg", bSvg(UW, UH,
  `<path d="${P.uGrat}" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="1.2"/>` +
  `<g filter="url(#sh)" transform="translate(0 5)" fill="#0b4f4a" fill-opacity=".16"><path id="O" d="${P.uOther}"/><path id="U" d="${P.uUSA}"/></g>` +
  `<use href="#O" transform="translate(0 -5)" fill="#f1eee6" fill-opacity="1" stroke="#b5c4b6" stroke-width="1.3" stroke-linejoin="round"/>` +
  `<use href="#U" transform="translate(0 -5)" fill="#e4ecd9" fill-opacity="1" stroke="#9fb8a5" stroke-width="1.4" stroke-linejoin="round"/>` +
  `<path d="${P.uStates}" fill="none" stroke="#fff" stroke-width="1.8"/>` +
  `<path d="${P.uBorders}" fill="none" stroke="#8fa999" stroke-width="2"/>` +
  `<path d="${P.uLakes}" fill="#cfe5ec" stroke="#9fb8a5" stroke-width="1"/>`, 1.2));

fs.writeFileSync(OUT + "pins.json", JSON.stringify({ meta, venuePins, animalPins, labels, deco }, null, 1));
for (const d of ["a", "b"]) { const f = OUT + `${d}-usa-v1.svg`; let t = fs.readFileSync(f, "utf8");
  t = t.replace(/id="([A-Za-z]+)"/g, 'id="kzu-$1"').replace(/href="#([A-Za-z]+)"/g, 'href="#kzu-$1"').replace(/url\(#([A-Za-z]+)\)/g, "url(#kzu-$1)");
  fs.writeFileSync(f, t); }
for (const f of fs.readdirSync(OUT)) console.log(f, fs.statSync(OUT + f).size);
console.log(meta);

// ---------- HTML fragments (one per direction). Pins carry their % position inline, so no JS is needed to place them (CLS 0).
const esc = (t) => String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const V = (id, print) => ({ slug: id, name: venues[id].name, city: venues[id].city, print, page: `/field-pack/${id}/` });
const SH = "/printables/pdf/letter/scavenger-hunt.pdf", PK = "/printables/pdf/letter/park-scavenger-hunt.pdf";
// Same members and print links as the live #424/#425 pins; DC and Baltimore are split so each city has its own label.
const groups = [
  // New York: two venues a few km apart share one dot, so each gets its own tag (the tags are the tap targets).
  { id: "bronx-zoo", label: "Bronx Zoo", members: [V("bronx-zoo", SH)], dx: 14, dy: -50, w: [44, -46], tagOnly: true },
  { id: "amnh", label: "Natural History\nMuseum", members: [V("amnh", "/field-pack/amnh/#printable-hunt")], dx: 58, dy: 0, w: [56, 14], tagOnly: true, noDot: true },
  { id: "dc", label: "Washington, DC", members: [V("air-and-space", "/field-pack/air-and-space/#printable-hunt"), V("national-zoo", SH)], dx: 12, dy: 54 },
  { id: "baltimore", label: "Baltimore", members: [V("national-aquarium-baltimore", SH)], dx: -60, dy: 2, w: [-58, 8] },
  { id: "chicago", label: "Chicago", members: [V("shedd-aquarium", SH), V("lincoln-park-zoo", SH)], dx: -56, dy: -20, w: [-40, -30] },
  { id: "toronto", label: "Toronto", members: [V("toronto-zoo", SH)], dx: -4, dy: -32, w: [-12, -32] },
  { id: "nashville", label: "Nashville", members: [V("nashville-adventure-science", "/field-pack/nashville-adventure-science/#printable-hunt")], dx: -20, dy: 36, w: [-34, 30] },
  { id: "austin", label: "Austin", members: [V("austin-zoo", SH)], dx: 50, dy: 6, w: [50, 14] },
  { id: "redwood", label: "Redwood", members: [V("redwood", PK)], dx: 52, dy: -4 },
  { id: "joshua-tree", label: "Joshua Tree", members: [V("joshua-tree", PK)], dx: 52, dy: 30 },
];
const animalInfo = {
  "american-bison": "American bison", "caribbean-flamingo": "Caribbean flamingo", "galapagos-tortoise": "Galápagos tortoise", "zebra": "Zebra",
  "giant-panda": "Giant panda", "sumatran-tiger": "Sumatran tiger", "whale-shark": "Whale shark", "koala": "Koala",
};
const region = { "american-bison": "americas", "caribbean-flamingo": "americas", "galapagos-tortoise": "americas" };
const at = (q) => `left:${q.x}%;top:${q.y}%`;
const P2 = (proj, W, H) => (lon, lat) => pct(proj, W, H, lon, lat);
const pu = P2(us, UW, UH), pw = P2(world, WW, WH);
const LABELS = {
  us: [["Pacific\nOcean", pu(-125.9, 33.6), "sea"], ["Atlantic\nOcean", pu(-72.6, 29.4), "sea"], ["Gulf of Mexico", pu(-90.2, 26.2), "sea"],
       ["CANADA", pu(-104, 50.2), "land"], ["MEXICO", pu(-106.5, 27.3), "land"], ["UNITED STATES", pu(-99.6, 39.2), "land big"]],
  world: [["Pacific Ocean", pw(-140, 4), "sea"], ["Atlantic Ocean", pw(-40, 30), "sea"], ["Indian Ocean", pw(80, -27), "sea"],
          ["North America", pw(-104, 58), "land"], ["South America", pw(-57, -24), "land"], ["Europe", pw(18, 53), "land"], ["Africa", pw(16, 13), "land"],
          ["Asia", pw(88, 52), "land"], ["Australia", pw(123, -25), "land"]],
};
const DECO = {
  a: {
    us: [["compass", pu(-122.2, 24.6), 6.2], ["liberty", pu(-66.6, 31.6), 3.4], ["ship", pu(-77.6, 25.9), 6], ["forest", pu(-114, 46.4), 6.5]],
    world: [["compass", pw(-150, -38), 6], ["ship", pw(-28, -22), 5], ["whale", pw(-150, 30), 5.2]],
  },
  b: { us: [], world: [] },
};
// Optional wider-screen tag offset (641px and up), where the plate is shown whole and pins sit closer together.
const wide = (g) => { if (!g.w) return ""; const [dx, dy] = g.w; return `;--dxw:${dx}px;--dyw:${dy}px;--lenw:${Math.hypot(dx, dy).toFixed(1)}px;--angw:${(Math.atan2(dy, dx) * 180 / Math.PI).toFixed(1)}deg`; };
function fragment(dir) {
  const ar = (W, H) => `--kzm-w:${W};--kzm-h:${H}`;
  const labels = (list) => list.map(([t, q, k]) => `<span class="kzm-label kzm-${k.replace(" ", " kzm-")}" style="${at(q)}" aria-hidden="true">${esc(t).replace("\n", "<br>")}</span>`).join("");
  const deco = (list) => list.map(([n, q, w]) => `<img class="kzm-deco kzm-deco-${n}" src="/start/map-v2/deco-${n}-96-v1.webp" srcset="/start/map-v2/deco-${n}-96-v1.webp 96w, /start/map-v2/deco-${n}-192-v1.webp 192w" sizes="(max-width: 640px) 44px, 64px" style="${at(q)};width:${w}%" width="96" height="96" alt="" aria-hidden="true" loading="lazy" decoding="async">`).join("");
  const pins = groups.map((g) => {
    const xs = g.members.map((m) => venues[m.slug]); const lon = xs.reduce((a, v) => a + v.lon, 0) / xs.length, lat = xs.reduce((a, v) => a + v.lat, 0) / xs.length;
    const q = pu(lon, lat); const len = Math.hypot(g.dx, g.dy).toFixed(1), ang = (Math.atan2(g.dy, g.dx) * 180 / Math.PI).toFixed(1);
    const n = g.members.length; const aria = n > 1 ? `${g.label.replace("\n", " ")}, ${n} places` : `${g.members[0].name}, ${g.members[0].city}`;
    return `<button type="button" class="home-place-pin kzm-pin${g.tagOnly ? " kzm-tagonly" : ""}${g.noDot ? " kzm-nodot" : ""}" data-home-pin="${g.id}" data-members="${esc(JSON.stringify(g.members))}" aria-label="${esc(aria)}" style="${at(q)};--dx:${g.dx}px;--dy:${g.dy}px;--len:${len}px;--ang:${ang}deg${wide(g)}"><span class="kzm-lead" aria-hidden="true"></span><span class="kzm-tag" aria-hidden="true">${esc(g.label).replace("\n", "<br>")}${n > 1 ? `<b>${n}</b>` : ""}</span></button>`;
  }).join("\n          ");
  const places = `<div id="home-places-map" class="home-places-map kzm kzm-usa kzm-${dir}">
        <p class="kzm-hint" id="kzm-usa-hint" aria-hidden="true">Drag sideways to see more</p>
        <div class="kzm-pan" id="kzm-usa-pan" data-start="0.735">
        <div class="kzm-plate" style="${ar(UW, UH)}" aria-label="Map of the United States with places that have a printable scavenger hunt">
          <div class="kzm-base" data-kzm-svg="/start/map-v2/${dir}-usa-v1.svg?v=1"></div>
          <span class="kzm-snap" style="left:73.5%" aria-hidden="true"></span>
          ${deco(DECO[dir].us)}${labels(LABELS.us)}
          <div class="home-pin-layer" id="home-pin-layer">
          ${pins}
          </div>
        </div>
        </div>
      </div>`;
  const animals = Object.entries(animalPins).map(([id, a]) =>
    `<a class="start-hero-hotspot kzm-animal kzm-animal-${id}${id === "caribbean-flamingo" ? " kzm-name-right" : ""}" data-hero-region="${region[id] || "east"}" href="/field-pack/cards/${id}/" aria-label="${esc(animalInfo[id])}" style="${at(a.world)}"><img src="/start/map-v2/animal-${id}-96-v1.webp" srcset="/start/map-v2/animal-${id}-96-v1.webp 96w, /start/map-v2/animal-${id}-192-v1.webp 192w" sizes="(max-width: 640px) 60px, 84px" width="96" height="96" alt="" aria-hidden="true" loading="lazy" decoding="async"><span class="kzm-name">${esc(animalInfo[id])}</span></a>`).join("\n        ");
  const world = `<div class="kzm kzm-world kzm-${dir}">
      <p class="start-pan-hint kzm-hint" id="start-pan-hint" aria-hidden="true">Drag sideways to see more</p>
      <div class="kzm-pan" id="start-hero-pan" data-start="0.22">
      <div class="kzm-plate" style="${ar(WW, WH)}">
        <img class="kzm-base start-hero-still" src="/start/map-v2/${dir}-world-v1.svg" width="${WW}" height="${WH}" alt="World map with eight animals where they live in the wild" loading="lazy" decoding="async">
        <span class="kzm-snap" style="left:22%" aria-hidden="true"></span>
        ${deco(DECO[dir].world)}${labels(LABELS.world)}
        ${animals}
      </div>
      </div>
    </div>`;
  return { places, world };
}
for (const d of ["a", "b"]) { const f = fragment(d); fs.writeFileSync(OUT + `fragment-${d}-places.html`, f.places); fs.writeFileSync(OUT + `fragment-${d}-world.html`, f.world); }
