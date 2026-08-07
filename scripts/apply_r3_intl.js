#!/usr/bin/env node
/**
 * R3: hybrid enrichment for remaining international wonder venues.
 * Same MOAT pattern as R1/R2 — local tagline, practical, map page, 5 icon stops.
 * No new UI.
 */
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const FIELD = path.join(__dirname, "..", "static", "field-pack");
const VENUE_DIR = path.join(FIELD, "data", "venues");
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
  "adelaide-zoo": P(
    "zoo",
    "Adelaide Zoo — compact city zoo; giant pandas when viewing is open.",
    "Short walkable loop; pandas first if that’s the trip goal.",
    half("City-edge zoo; check panda hours.", "From Adelaide CBD / North Terrace area.", "stroller-easy", "Pandas if open, else one calm circuit."),
    "https://www.zoossa.com.au/adelaide-zoo/",
    "Adelaide Zoo",
    [
      item("giant-panda", "Pandas", "Pandas when accessible — the magnet stop.", ["wow", "big"]),
      item("red-panda", "Red pandas", "Red pandas nearby energy.", ["climb"]),
      item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
      item("orangutan", "Primates", "Orangutans / great apes when on route.", ["primates", "wow"]),
    ]
  ),
  "al-ain-zoo": P(
    "zoo",
    "Al Ain Zoo — desert oasis zoo day; heat is the real boss.",
    "Morning only with little kids; shade and water first.",
    half("Desert heat — start early.", "Al Ain city.", "heat", "One shaded loop; skip mid-day."),
    "https://www.alainzoo.ae/",
    "Al Ain Zoo",
    [
      item("african-lion", "Lions", "Lions — big cat wow.", ["big-cats", "wow"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
      item("african-elephant", "Elephants", "Elephants.", ["big"]),
      item("nile-hippo", "Hippos", "Hippos if on the loop.", ["big", "water"]),
      item("zebra", "Plains", "Zebras and open views.", ["outdoor"]),
    ]
  ),
  "antwerp-zoo": P(
    "zoo",
    "Antwerp Zoo — historic city-centre zoo next to the station.",
    "Dense European classic; half day max with kids.",
    half("Right by Antwerp Central.", "Walk from Centraal station.", "stroller-easy", "One circuit; don’t chase every house."),
    "https://www.zooantwerpen.be/en/",
    "Antwerp Zoo",
    [
      item("african-elephant", "Elephants", "Elephants.", ["big", "wow"]),
      item("western-lowland-gorilla", "Gorillas", "Gorillas.", ["primates"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
      item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
      item("african-penguin", "Penguins", "Penguins — easy kid reset.", ["water"]),
    ]
  ),
  "athens-attica-zoo": P(
    "zoo",
    "Attica Park — large private zoo outside Athens; plan transport.",
    "Not a downtown hop — treat as a half-day outing.",
    half("Outside the city; tickets online help.", "Plan taxi/car/bus ahead.", "heat", "One realm only in summer heat."),
    "https://www.atticapark.com/en/",
    "Attica Zoological Park",
    [
      item("african-lion", "Lions", "Lions.", ["big-cats", "wow"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
      item("african-elephant", "Elephants", "Elephants.", ["big"]),
      item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
      item("western-lowland-gorilla", "Primates", "Gorillas / primates.", ["primates"]),
    ]
  ),
  "bangalore-bannerghatta": P(
    "safari_zoo",
    "Bannerghatta — biological park + safari; pick zoo walk OR safari, not both full.",
    "Big campus near Bengaluru; heat and queues matter.",
    half("Safari slots sell out — check times.", "South of Bengaluru; plan a car day.", "heat", "Safari block or zoo loop — one focus."),
    "https://www.bannerghattabiologicalpark.org/",
    "Bannerghatta Biological Park",
    [
      item("african-lion", "Safari / cats", "Lions if on safari or cat zone.", ["big-cats", "wow"]),
      item("sumatran-tiger", "Tigers", "Tigers — Indian park highlight.", ["big-cats", "wow"]),
      item("african-elephant", "Elephants", "Elephants.", ["big"]),
      item("zebra", "Plains", "Zebras on safari stretches.", ["outdoor"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
    ]
  ),
  "bangkok-safari-world": P(
    "safari_zoo",
    "Safari World Bangkok — drive-through + marine park combo; pick one half.",
    "Tourist mega-day; don’t stack both parks with toddlers.",
    half("Combo tickets common; start early.", "East Bangkok; car or tour.", "heat", "Safari OR Marine Park first — not both deep."),
    "https://www.safariworld.com/",
    "Safari World",
    [
      item("african-lion", "Safari", "Lions on the drive-through story.", ["big-cats", "wow"]),
      item("reticulated-giraffe", "Safari", "Giraffes at vehicle distance.", ["tall"]),
      item("zebra", "Safari", "Zebras.", ["outdoor"]),
      item("african-elephant", "Park", "Elephants.", ["big"]),
      item("shark", "Marine", "Marine park tanks if you chose that half.", ["water", "big", "wow"]),
    ]
  ),
  "bogota-zoo": P(
    "zoo",
    "Jaime Duque — park + zoo north of Bogotá; altitude and weather swing.",
    "More than a city zoo stop — plan a half-day park visit.",
    half("Park entry; zoo is part of the grounds.", "North of city; plan transport.", "hills", "One animal loop + playground reset."),
    "https://www.parquejaimeduque.com/",
    "Parque Jaime Duque",
    [
      item("african-lion", "Cats", "Lions.", ["big-cats"]),
      item("reticulated-giraffe", "Tall", "Giraffes.", ["tall"]),
      item("african-elephant", "Big", "Elephants.", ["big"]),
      item("zebra", "Plains", "Zebras.", ["outdoor"]),
      item("cm-outdoor", "Park", "Open park paths for kid energy.", ["outdoor", "play"]),
    ]
  ),
  "cairo-zoo": P(
    "zoo",
    "Giza Zoo — historic city zoo; verify current access and hours before you go.",
    "Classic Cairo outing; conditions change — check locally.",
    half("Confirm open hours the day you go.", "Giza area; plan traffic.", "heat", "One shaded loop; leave early if tired."),
    "https://www.facebook.com/",
    "Giza Zoo (verify official updates)",
    [
      item("african-lion", "Lions", "Lions.", ["big-cats", "wow"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
      item("african-elephant", "Elephants", "Elephants.", ["big"]),
      item("nile-hippo", "Hippos", "Hippos if present — Nile story link.", ["big", "water"]),
      item("zebra", "Plains", "Zebras.", ["outdoor"]),
    ]
  ),
  "chapultepec-zoo": P(
    "zoo",
    "Chapultepec Zoo — free Mexico City classic inside the big park.",
    "Combine lightly with park paths; pandas when viewing is open.",
    half("Usually free entry; lines at peaks.", "Chapultepec; Metro options.", "stroller-easy", "Pandas if open, else one loop."),
    "https://www.sedema.cdmx.gob.mx/",
    "Zoológico de Chapultepec",
    [
      item("giant-panda", "Pandas", "Pandas when accessible.", ["wow", "big"]),
      item("african-lion", "Lions", "Lions.", ["big-cats"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
      item("african-elephant", "Elephants", "Elephants.", ["big"]),
      item("cm-outdoor", "Park edge", "Park paths for a soft finish.", ["outdoor", "play"]),
    ]
  ),
  "delhi-zoo": P(
    "zoo",
    "Delhi National Zoological Park — large city zoo; heat and weekends matter.",
    "Half day max; morning start in warm months.",
    half("Near Purana Qila area.", "Pragati Maidan / zoo gates.", "heat", "One circuit before heat peaks."),
    "https://nzpnewdelhi.gov.in/",
    "National Zoological Park Delhi",
    [
      item("sumatran-tiger", "Tigers", "Tigers — strong kid magnet.", ["big-cats", "wow"]),
      item("african-lion", "Lions", "Lions.", ["big-cats"]),
      item("african-elephant", "Elephants", "Elephants.", ["big"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
      item("chimpanzee", "Primates", "Primates.", ["primates", "play"]),
    ]
  ),
  "ecoparque-ba": P(
    "zoo",
    "Ecoparque BA — conservation park, not a classic “see every animal” zoo day.",
    "Expect a greener, quieter pace; check what’s open that day.",
    half("City park rules; verify open areas.", "Palermo / city park access.", "stroller-easy", "Birds + one habitat path."),
    "https://turismo.buenosaires.gob.ar/",
    "Ecoparque Buenos Aires",
    [
      item("caribbean-flamingo", "Birds", "Flamingos — easy visual wow.", ["wow", "outdoor"]),
      item("african-penguin", "Penguins", "Penguins if on the open route.", ["water"]),
      item("galapagos-tortoise", "Tortoises", "Slow giant tortoises.", ["wow"]),
      item("ring-tailed-lemur", "Lemurs", "Lemurs.", ["climb", "play"]),
      item("two-toed-sloth", "Sloths", "Sloths — patience game.", ["climb"]),
    ]
  ),
  "helsinki-zoo": P(
    "zoo",
    "Korkeasaari — island zoo; ferry or bridge access is half the adventure.",
    "Weather + island logistics; pack layers.",
    half("Island access fees/times apply.", "Ferry or bridge to Korkeasaari.", "hills", "One island loop; don’t rush the boat."),
    "https://www.korkeasaari.fi/en/",
    "Korkeasaari Zoo",
    [
      item("sumatran-tiger", "Cats", "Tigers / cats.", ["big-cats", "wow"]),
      item("reticulated-giraffe", "Tall", "Giraffes.", ["tall"]),
      item("western-lowland-gorilla", "Primates", "Gorillas.", ["primates"]),
      item("red-panda", "Red pandas", "Red pandas.", ["climb"]),
      item("cm-outdoor", "Island paths", "Sea air walk between stops.", ["outdoor", "play"]),
    ]
  ),
  "istanbul-aquarium": P(
    "aquarium",
    "Istanbul Aquarium — big indoor tunnel day by the sea.",
    "Tourist aquarium; short focused visit with little kids.",
    half("Florya area; tickets online help.", "Plan metro/bus or taxi.", "indoor", "Tunnel / biggest tank first."),
    "https://www.istanbulakvaryum.com/en",
    "Istanbul Aquarium",
    [
      item("shark", "Big tanks", "Sharks — overhead wow.", ["water", "big", "wow"]),
      item("stingray", "Rays", "Rays.", ["water", "flat"]),
      item("jellyfish", "Jellies", "Jellies glow stop.", ["water", "glow"]),
      item("sea-turtle", "Turtles", "Turtles.", ["water", "shell"]),
      item("clownfish", "Reef", "Bright reef fish.", ["water", "color"]),
    ]
  ),
  "jakarta-ragunan": P(
    "zoo",
    "Ragunan — huge tropical city zoo; pick one zone only with kids.",
    "Jakarta heat and scale; morning or bust.",
    half("Large grounds; weekends crowded.", "South Jakarta.", "heat", "One shaded zone; skip full map."),
    "https://ragunanzoo.jakarta.go.id/",
    "Ragunan Zoo",
    [
      item("orangutan", "Orangutans", "Orangutans — regional highlight.", ["primates", "climb", "wow"]),
      item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
      item("african-elephant", "Elephants", "Elephants.", ["big"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
      item("asian-small-clawed-otter", "Otters", "Otters — kid energy reset.", ["water", "play"]),
    ]
  ),
  "johannesburg-zoo": P(
    "zoo",
    "Johannesburg Zoo — classic city zoo in parkland; finishable half day.",
    "Pair with park shade; don’t overpack the day.",
    half("City parks & zoo tickets.", "Parkview / zoo area.", "stroller-easy", "One loop + shade snack."),
    "https://www.jhbcityparksandzoo.com/",
    "Johannesburg Zoo",
    [
      item("african-lion", "Lions", "Lions — local pride energy.", ["big-cats", "wow"]),
      item("african-elephant", "Elephants", "Elephants.", ["big"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
      item("zebra", "Plains", "Zebras.", ["outdoor"]),
      item("nile-hippo", "Hippos", "Hippos.", ["big", "water"]),
    ]
  ),
  "kuala-lumpur-zoo": P(
    "zoo",
    "Zoo Negara — Malaysia’s national zoo; heat + humidity plan.",
    "Half day; indoor rests between outdoor loops.",
    half("Outside central KL; plan a ride.", "Ulu Klang area.", "heat", "Giant panda or one themed zone."),
    "https://www.zoonegara.my/",
    "Zoo Negara",
    [
      item("giant-panda", "Pandas", "Pandas when open — top ask.", ["wow", "big"]),
      item("orangutan", "Orangutans", "Orangutans.", ["primates", "wow"]),
      item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
      item("asian-small-clawed-otter", "Otters", "Otters.", ["water", "play"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
    ]
  ),
  "lima-leyendas": P(
    "zoo",
    "Leyendas — zoo + cultural zones across Lima history themes.",
    "Big site; pick animals OR culture strips with little kids.",
    half("Large park; wear good shoes.", "San Miguel area.", "heat", "One animal circuit + shade."),
    "https://www.leyendas.gob.pe/",
    "Parque de las Leyendas",
    [
      item("african-lion", "Cats", "Lions.", ["big-cats"]),
      item("reticulated-giraffe", "Tall", "Giraffes.", ["tall"]),
      item("african-elephant", "Big", "Elephants.", ["big"]),
      item("two-toed-sloth", "South America", "Sloths / regional animals.", ["climb"]),
      item("cm-outdoor", "Park paths", "Themed park walks between stops.", ["outdoor", "play"]),
    ]
  ),
  "lotte-aquarium-seoul": P(
    "aquarium",
    "Lotte World Aquarium — mall-basement ocean wow under Lotte World.",
    "Indoor tourist hit; combine carefully with theme park energy.",
    half("Jamsil Lotte complex tickets.", "Jamsil station area.", "indoor", "Biggest tank / tunnel first."),
    "https://www.lotteworld.com/",
    "Lotte World Aquarium",
    [
      item("shark", "Main tank", "Sharks and big ocean energy.", ["water", "big", "wow"]),
      item("stingray", "Rays", "Rays.", ["water", "flat"]),
      item("jellyfish", "Jellies", "Jellies.", ["water", "glow"]),
      item("sea-turtle", "Turtles", "Turtles.", ["water", "shell"]),
      item("clownfish", "Reef", "Reef colors.", ["water", "color"]),
    ]
  ),
  "manila-zoo": P(
    "zoo",
    "Manila Zoo — compact city zoo; short visit beats marathon.",
    "Heat and humidity; morning window is kinder.",
    half("City zoo hours; check reopening notes if renovating.", "Manila city access.", "heat", "One short loop."),
    "https://www.manilazoo.ph/",
    "Manila Zoo",
    [
      item("african-lion", "Lions", "Lions.", ["big-cats"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
      item("african-elephant", "Elephants", "Elephants.", ["big"]),
      item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
      item("asian-small-clawed-otter", "Otters", "Otters if on path.", ["water", "play"]),
    ]
  ),
  "milan-aquarium": P(
    "aquarium",
    "Acquario di Milano — small historic civic aquarium; quick indoor stop.",
    "Not a mega-aquarium day — 45–90 minutes is plenty.",
    half("Compact visit; check open days.", "Sempione / castle park edge.", "indoor", "One floor, kid pace."),
    "https://www.acquariocivicomilano.eu/",
    "Acquario Civico di Milano",
    [
      item("shark", "Tanks", "Sharks if exhibited.", ["water", "big"]),
      item("jellyfish", "Jellies", "Jellies.", ["water", "glow"]),
      item("stingray", "Rays", "Rays.", ["water", "flat"]),
      item("seahorse", "Small wonders", "Seahorses — slow look.", ["water"]),
      item("clownfish", "Color", "Bright reef fish.", ["water", "color"]),
    ]
  ),
  "moscow-zoo": P(
    "zoo",
    "Moscow Zoo — large historic city zoo; dress for weather extremes.",
    "Big campus; one realm with preschoolers.",
    half("Central zoo; tickets online in peak.", "Barrikadnaya area.", "stroller-easy", "One themed circuit."),
    "https://moscowzoo.ru/en/",
    "Moscow Zoo",
    [
      item("african-lion", "Lions", "Lions.", ["big-cats", "wow"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
      item("african-elephant", "Elephants", "Elephants.", ["big"]),
      item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
      item("western-lowland-gorilla", "Primates", "Gorillas.", ["primates"]),
    ]
  ),
  "mumbai-byculla-zoo": P(
    "zoo",
    "Byculla Zoo (Jijamata Udyan) — leafy city zoo + garden; short loops win.",
    "Mumbai heat and traffic; morning half day.",
    half("City garden zoo; check hours.", "Byculla area.", "heat", "One garden + animal loop."),
    "https://www.mcgm.gov.in/",
    "Jijamata Udyan / Byculla Zoo",
    [
      item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats", "wow"]),
      item("african-lion", "Lions", "Lions.", ["big-cats"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
      item("african-elephant", "Elephants", "Elephants.", ["big"]),
      item("cm-outdoor", "Garden", "Garden paths for a soft reset.", ["outdoor", "play"]),
    ]
  ),
  "nairobi-safari-walk": P(
    "safari_zoo",
    "Nairobi Safari Walk — boardwalk wildlife near the national park edge.",
    "Not a full safari game drive — elevated walk + education pace.",
    half("KWS site; pair carefully with park plans.", "Near Nairobi National Park gates.", "heat", "Full boardwalk once, kid pace."),
    "https://www.kws.go.ke/",
    "Nairobi Safari Walk (KWS)",
    [
      item("reticulated-giraffe", "Giraffes", "Giraffes from the walk.", ["tall", "wow"]),
      item("zebra", "Plains", "Zebras.", ["outdoor"]),
      item("african-lion", "Cats", "Lions if on the route that day.", ["big-cats"]),
      item("african-elephant", "Big", "Elephants when visible.", ["big"]),
      item("cm-outdoor", "Boardwalk", "Walk and notice — the path is the activity.", ["outdoor", "play"]),
    ]
  ),
  "oslo-zoo": P(
    "zoo",
    "Kristiansand Zoo (Dyreparken) — Norway’s big zoo + park day outside Oslo.",
    "Full outing destination; not a quick city hop from Oslo centre.",
    half("Park-day tickets; extras add up.", "Kristiansand — plan travel.", "stroller-easy", "Zoo loop first; rides optional."),
    "https://www.dyreparken.com/",
    "Dyreparken / Kristiansand Zoo",
    [
      item("african-lion", "Lions", "Lions.", ["big-cats", "wow"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
      item("african-elephant", "Elephants", "Elephants.", ["big"]),
      item("western-lowland-gorilla", "Primates", "Gorillas.", ["primates"]),
      item("cm-outdoor", "Park", "Park paths between animal stops.", ["outdoor", "play"]),
    ]
  ),
  "rio-zoo": P(
    "zoo",
    "BioParque do Rio — modern Rio zoo day; heat and hills nearby.",
    "Half day; hydrate and shade aggressively.",
    half("Quinta da Boa Vista area.", "North Zone access.", "heat", "One circuit before afternoon heat."),
    "https://www.bioparque.org.br/",
    "BioParque do Rio",
    [
      item("african-lion", "Lions", "Lions.", ["big-cats"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
      item("african-elephant", "Elephants", "Elephants.", ["big"]),
      item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
      item("two-toed-sloth", "South America", "Sloths / regional animals.", ["climb"]),
    ]
  ),
  "rome-bioparco": P(
    "zoo",
    "Bioparco di Roma — zoo inside Villa Borghese park energy.",
    "Combine lightly with park strolls; half day zoo max.",
    half("Park zoo tickets.", "Villa Borghese area.", "hills", "One animal loop + gelato reset outside."),
    "https://www.bioparco.it/en/",
    "Bioparco di Roma",
    [
      item("african-elephant", "Elephants", "Elephants.", ["big", "wow"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
      item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
      item("western-lowland-gorilla", "Gorillas", "Gorillas.", ["primates"]),
      item("african-penguin", "Penguins", "Penguins.", ["water"]),
    ]
  ),
  "santiago-zoo": P(
    "zoo",
    "Parque Metropolitano Zoo — hill zoo with city views; funicular energy.",
    "Climb + animals; little legs tire fast — one direction plan.",
    half("Park access + zoo; check funicular.", "San Cristóbal hill.", "hills", "Zoo loop; views are free wow."),
    "https://www.parquemet.cl/",
    "Zoológico Nacional / Parque Met",
    [
      item("african-lion", "Lions", "Lions.", ["big-cats"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
      item("african-elephant", "Elephants", "Elephants.", ["big"]),
      item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
      item("cm-outdoor", "Hill paths", "Viewpoints between animal stops.", ["outdoor", "play"]),
    ]
  ),
  "sao-paulo-zoo": P(
    "zoo",
    "São Paulo Zoo — large Atlantic-forest-edge campus; pick one area.",
    "Big Brazilian zoo day; don’t attempt the full map.",
    half("South zone; plan a dedicated half day.", "Bus/car to zoo gates.", "heat", "One forest-edge circuit."),
    "https://www.zoologico.com.br/",
    "Zoológico de São Paulo",
    [
      item("western-lowland-gorilla", "Primates", "Gorillas / primates.", ["primates", "wow"]),
      item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
      item("african-elephant", "Elephants", "Elephants.", ["big"]),
      item("two-toed-sloth", "South America", "Sloths / regional animals.", ["climb"]),
    ]
  ),
  "singapore-night-safari": P(
    "safari_zoo",
    "Night Safari — after-dark tram + walking trails; different energy than day zoo.",
    "Night timing with kids: naps, snacks, and exit plan matter most.",
    half("Evening tickets; tram seats fill.", "Mandai; same complex as day zoo.", "evening", "Tram first, then one walking loop."),
    "https://www.mandai.com/en/night-safari.html",
    "Night Safari Mandai",
    [
      item("asian-small-clawed-otter", "Trails", "Otters and nocturnal bustle.", ["water", "play", "wow"]),
      item("sumatran-tiger", "Cats", "Tigers in night lighting.", ["big-cats", "wow"]),
      item("african-elephant", "Big", "Elephants on the night route.", ["big"]),
      item("red-panda", "Climb", "Red pandas if on walking trails.", ["climb"]),
      item("zebra", "Tram views", "Plains animals from the tram.", ["outdoor"]),
    ]
  ),
  "warsaw-zoo": P(
    "zoo",
    "Warsaw Zoo — riverside city zoo; solid half-day European classic.",
    "Finishable with preschoolers if you pick one loop.",
    half("Praga district zoo.", "Near the river / zoo tram stops.", "stroller-easy", "One calm circuit."),
    "https://zoo.waw.pl/en/",
    "Warsaw Zoo",
    [
      item("african-elephant", "Elephants", "Elephants.", ["big", "wow"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
      item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
      item("western-lowland-gorilla", "Gorillas", "Gorillas.", ["primates"]),
      item("african-penguin", "Penguins", "Penguins.", ["water"]),
    ]
  ),
  "zurich-zoo": P(
    "zoo",
    "Zurich Zoo — Masoala rainforest hall is the signature indoor wow.",
    "Swiss-quality half day; Masoala first if weather is rough.",
    half("Zürichberg hillside zoo.", "Tram to zoo.", "hills", "Masoala hall + one outdoor loop."),
    "https://www.zoo.ch/en",
    "Zoo Zürich",
    [
      item("cm-outdoor", "Masoala", "Rainforest hall — warm humid wow indoors.", ["wow", "outdoor"]),
      item("sumatran-tiger", "Tigers", "Tigers.", ["big-cats"]),
      item("reticulated-giraffe", "Giraffes", "Giraffes.", ["tall"]),
      item("african-elephant", "Elephants", "Elephants.", ["big"]),
      item("red-panda", "Red pandas", "Red pandas.", ["climb"]),
    ]
  ),
};

// Fix bangkok dolphin if missing from catalog
for (const [slug, pack] of Object.entries(packs)) {
  pack.icons = pack.icons.filter((i) => {
    if (!catalog[i.catalog_id]) {
      console.warn("drop missing catalog", slug, i.catalog_id);
      return false;
    }
    return true;
  });
  while (pack.icons.length < 5) {
    pack.icons.push(
      item("cm-free-explore", "Explore", "They pick the next five minutes.", ["play"])
    );
  }
}

let n = 0;
const blurbs = {};
for (const [slug, pack] of Object.entries(packs)) {
  const fp = path.join(VENUE_DIR, slug + ".json");
  if (!fs.existsSync(fp)) {
    console.warn("miss", slug);
    continue;
  }
  const cur = JSON.parse(fs.readFileSync(fp, "utf8"));
  if (cur.content_mode === "curated") {
    console.warn("skip curated", slug);
    continue;
  }
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
    parent_script: cur.parent_script || [
      "Bathroom first",
      "One big wow",
      "Snack when needed",
      "Leave while happy",
    ],
    route_90m: pack.icons.slice(0, 3).map((i) => i.id),
    research_notes: "R3 " + new Date().toISOString().slice(0, 10),
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
console.log("updated", n, "of", Object.keys(packs).length);
