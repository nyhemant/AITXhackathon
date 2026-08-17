/**
 * Shared print helpers for Field Trip Kit (landing pin panel + outing app).
 * Requires: catalog.js (fpGetVenue, FIELD_PACK_CATALOG, fpMissionsForVenue)
 * DOM: #print-sheet, #treasure-sheet
 */
(() => {
  function escapeHtml(s) {
    return String(s ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }
  function escapeAttr(s) {
    return escapeHtml(s).replaceAll("'", "&#39;");
  }

  function track(name, params) {
    if (typeof window.FPTrack === "function") {
      window.FPTrack(name, params || {});
      return;
    }
    const fn =
      (window.OneLessAnalytics && window.OneLessAnalytics.track) || window.trackEvent;
    if (typeof fn === "function") fn(name, params || {});
  }

  function sheets() {
    return {
      printSheet: document.getElementById("print-sheet"),
      treasureSheet: document.getElementById("treasure-sheet"),
    };
  }

  function getVenue(id) {
    return typeof window.fpGetVenue === "function" ? window.fpGetVenue(id) : null;
  }

  function getItem(id, venue) {
    const base = (window.FIELD_PACK_CATALOG && window.FIELD_PACK_CATALOG[id]) || null;
    if (!base) return null;
    const names = venue && venue.itemDisplayNames;
    const custom = names && (names[id] || names[base.id]);
    if (!custom) return base;
    return Object.assign({}, base, { name: custom, displayName: custom });
  }

  function missionsFor(venue) {
    if (typeof window.fpMissionsForVenue === "function") return window.fpMissionsForVenue(venue);
    return window.FIELD_PACK_MISSIONS_ANIMALS || [];
  }

  /** Featured / top-pick item id for a venue (first featured, else first animal). */
  function topPickItemId(venue) {
    if (!venue) return null;
    const featured = venue.featuredAnimalIds || [];
    if (featured.length) return featured[0];
    const all = venue.animalIds || [];
    return all[0] || null;
  }

  /** Print-safe local map path (prefer hosted preview under /field-pack/media/maps/). */
  function printMapForVenue(venue) {
    const id = (venue && (venue.id || venue.slug)) || "";
    const maps = window.FP_PRINT_MAPS || {};
    if (id && maps[id]) return maps[id];
    // SEO pages embed full mission venue JSON
    try {
      const el = document.getElementById("venue-data");
      if (el && el.textContent) {
        const data = JSON.parse(el.textContent);
        const m = (data && data.media) || {};
        const u = m.print_map || m.visitor_map_url || "";
        if (u && String(u).startsWith("/field-pack/media/maps/")) return u;
      }
    } catch (_) {
      /* ignore */
    }
    const m = (venue && venue.media) || {};
    const u = m.print_map || m.visitor_map_url || "";
    if (u && String(u).startsWith("/field-pack/media/maps/")) return u;
    return "";
  }

  function buildTreasureHtml(venue, starIds) {
    const hunts = (venue.treasureHunt || []).slice(0, 8);
    const huntHtml = hunts
      .map(
        (h, i) => `
      <div class="th-row">
        <span class="th-box"></span>
        <span class="th-num">${i + 1}</span>
        <span class="th-text">${escapeHtml(h.text)}</span>
      </div>`
      )
      .join("");
    const ids = (starIds && starIds.length ? starIds : venue.featuredAnimalIds || []).slice(0, 6);
    const stars = ids
      .map((id) => {
        const it = getItem(id, venue);
        return it ? `<span class="th-chip">${it.emoji || "•"} ${escapeHtml(it.name)}</span>` : "";
      })
      .join("");
    const mapSrc = printMapForVenue(venue);
    const mapBlock = mapSrc
      ? `<div class="th-map th-map-has-photo">
          <p class="th-map-title">Park map — mark start → favorite → end</p>
          <div class="th-map-photo-wrap">
            <img class="th-map-photo" src="${escapeAttr(mapSrc)}" alt="Official visitor map" />
          </div>
        </div>`
      : `<div class="th-map">
          <p class="th-map-title">Path doodle <span class="th-map-hint">— start → favorite → end</span></p>
          <div class="th-map-box"></div>
        </div>`;
    return `
      <div class="th-page${mapSrc ? " th-page-with-map" : ""}">
        <div class="th-banner">
          <h1>🗺️ Your mission${venue && (venue.sliceLabel || venue.slice_label || (venue.practical && venue.practical.slice_name)) ? ` · ${escapeHtml(venue.sliceLabel || venue.slice_label || venue.practical.slice_name)}` : ""}</h1>
          <p>${escapeHtml(venue.name)} · One-page hunt · Field Trip Kit</p>
        </div>
        <div class="th-meta">
          <p><strong>Place:</strong> ${escapeHtml(venue.name)}
          &nbsp;·&nbsp; <strong>Where:</strong> ${escapeHtml(venue.location || "")}</p>
          <p><strong>Explorer:</strong> <span class="write-in-line">________________</span>
          &nbsp;&nbsp; <strong>Date:</strong> ____________</p>
        </div>
        <p class="th-intro">Your mission: check each box when you find it. No rush!</p>
        <div class="th-list">${huntHtml}</div>
        <div class="th-stars">
          <p class="th-stars-title">Star list (top picks)</p>
          <div class="th-chips">${stars}</div>
        </div>
        ${mapBlock}
        ${
          (venue.safetyFooter ||
            venue.safety_footer ||
            (String(venue.type || "").toLowerCase() === "national_park"
              ? "Stay on boardwalks and trails · give wildlife lots of space · bring water"
              : ""))
            ? `<p class="th-safety">${escapeHtml(
                venue.safetyFooter ||
                  venue.safety_footer ||
                  "Stay on boardwalks and trails · give wildlife lots of space · bring water"
              )}</p>`
            : ""
        }
        <p class="th-footer">Optional after: open Field Trip Kit → tap a card → Q&A</p>
      </div>`;
  }

  /** Resolve catalog photo path for print/screen. */
  function itemPhotoSrc(item) {
    const p = (item && item.photo) || "";
    if (!p) return "";
    if (/^https?:\/\//i.test(p) || p.startsWith("/")) return p;
    // catalog uses "photos/foo.jpg"
    if (p.startsWith("photos/")) return "/field-pack/" + p;
    return "/field-pack/photos/" + p.replace(/^\/+/, "");
  }

  /**
   * Curated kid/parent wow facts for the strip under the Q&A photo.
   * Prefer surprising numbers or "wait, really?" hooks over habitat tips.
   * Shape: { q, a } — short Q + punchy A (print-safe one line).
   */
  const WOW_FACTS = {
    "african-elephant": {
      q: "Did you know?",
      a: "An elephant’s trunk has about 40,000 muscles — more than your whole body!",
    },
    "reticulated-giraffe": {
      q: "How tall is a giraffe baby?",
      a: "About 6 feet at birth — already taller than most grown-ups!",
    },
    "african-lion": {
      q: "How far can a lion’s roar travel?",
      a: "Up to 5 miles (8 km) — other prides can hear it across the savanna.",
    },
    "sumatran-tiger": {
      q: "Are any two tigers the same?",
      a: "Nope — every tiger’s stripe pattern is unique, like a fingerprint.",
    },
    "western-lowland-gorilla": {
      q: "How strong is a gorilla?",
      a: "A silverback can lift several times its own weight — and still be gentle with babies.",
    },
    "nile-hippo": {
      q: "Can hippos swim?",
      a: "They mostly walk or bounce on the river bottom — and can hold their breath ~5 minutes!",
    },
    "african-penguin": {
      q: "Why do penguins look like they’re wearing tuxedos?",
      a: "Countershading: dark back fools hunters above; white belly fools fish below.",
    },
    "caribbean-flamingo": {
      q: "Why are flamingos pink?",
      a: "They eat pink shrimp and algae — without that food, they’d turn pale!",
    },
    "asian-small-clawed-otter": {
      q: "What’s special about otter hands?",
      a: "They have the most nimble paws of any otter — great for cracking open snacks.",
    },
    "ring-tailed-lemur": {
      q: "Why the stripy tail?",
      a: "They wave it like a flag and even have “stink fights” to say who’s boss!",
    },
    cheetah: {
      q: "How fast can a cheetah run?",
      a: "About 60–70 mph in short bursts — fastest land animal on Earth.",
    },
    "american-alligator": {
      q: "Why does an alligator look like a log?",
      a: "Still water and a bumpy back hide it so fish and birds come close.",
    },
    "two-toed-sloth": {
      q: "How slow is a sloth?",
      a: "So slow that algae grows in its fur — free camouflage!",
    },
    "galapagos-tortoise": {
      q: "How long can a giant tortoise live?",
      a: "Over 100 years — some of the oldest animals you’ll ever meet.",
    },
    chimpanzee: {
      q: "What makes chimps so smart?",
      a: "They use tools — sticks for termites, rocks to crack nuts — just like inventors.",
    },
    warthog: {
      q: "How do warthogs stay cool?",
      a: "They kneel on padded knees to dig and love a good mud bath sunscreen.",
    },
    ostrich: {
      q: "Can an ostrich fly?",
      a: "No wings for flight — but they can sprint over 40 mph and kick hard!",
    },
    shark: {
      q: "Do sharks have bones?",
      a: "Nope — their skeletons are cartilage (like your nose and ears), so they’re super bendy.",
    },
    stingray: {
      q: "Where is a stingray’s mouth?",
      a: "On its belly! It “flies” over the sand and vacuum-scoops snacks underneath.",
    },
    seahorse: {
      q: "Who carries the babies?",
      a: "Dad does! Father seahorses keep the eggs in a pouch until they hatch.",
    },
    jellyfish: {
      q: "Do jellyfish have brains?",
      a: "No brain, no bones, no heart — just a soft body that pulses through the sea.",
    },
    clownfish: {
      q: "Why don’t clownfish get stung by anemones?",
      a: "A special slime coat protects them — the anemone is their fortress home.",
    },
    "sea-turtle": {
      q: "How far do sea turtles travel?",
      a: "Some swim thousands of miles and still find the same beach they hatched on.",
    },
    octopus: {
      q: "How many hearts does an octopus have?",
      a: "Three hearts and blue blood — plus they can squeeze through tiny cracks!",
    },
    eel: {
      q: "How do eels hide so well?",
      a: "They slip into rock holes and wait — only eyes and jaws peek out.",
    },
    crab: {
      q: "Why do crabs walk sideways?",
      a: "Their legs bend that way — sideways is their super-speed mode!",
    },
    starfish: {
      q: "Can a sea star regrow an arm?",
      a: "Yes! Lose a ray and it can grow back — some species grow a whole new body from one arm.",
    },
    "freshwater-fish": {
      q: "What’s different about river fish?",
      a: "They live in lakes and rivers, not the salty ocean — same “fish,” different neighborhoods.",
    },
    "sea-otter": {
      q: "Why do sea otters float on their backs?",
      a: "A back-float turns the belly into a table. Kelp is an anchor so they don’t drift away.",
    },
    "whale-shark": {
      q: "Is a whale shark a whale?",
      a: "Nope — it’s a shark, the biggest fish in the sea. A giant mouth sifts tiny food from the water.",
    },
    cuttlefish: {
      q: "How can a cuttlefish change color so fast?",
      a: "Tiny skin spots open and close like pixels — for hiding, talking, and tricking.",
    },
    puffin: {
      q: "How can a puffin fly and also swim?",
      a: "Short wings work as flippers underwater and as wings in the air.",
    },
    "manta-ray": {
      q: "Why is a manta ray so wide and flat?",
      a: "Wide wings let it glide and scoop tiny food. Little fish even nibble it clean.",
    },
    "kelp-forest": {
      q: "Why does kelp grow so tall so fast?",
      a: "Sunlight and waving water help it shoot up. Fish and otters hide in it like a forest.",
    },
    beluga: {
      q: "Why do people call a beluga a sea canary?",
      a: "It clicks, whistles, and chirps — a whole song to talk with its pod.",
    },
    walrus: {
      q: "What are walrus tusks for?",
      a: "They help it haul onto ice and keep a spot in a crowded herd. Blubber keeps it warm.",
    },
    piranha: {
      q: "Do piranhas really hunt in a big group?",
      a: "They often swim in schools. Sharp teeth cut food fast, and they find it by smell and movement.",
    },
    shrimp: {
      q: "How does a shrimp escape so fast?",
      a: "A tail flick shoots it backward. Some shrimp also change color to match the reef.",
    },
    nudibranch: {
      q: "Why is a nudibranch so colorful with no shell?",
      a: "Bright colors warn “I taste bad.” The frills on its back are gills for breathing.",
    },
    "weedy-sea-dragon": {
      q: "Who carries sea dragon eggs?",
      a: "Dad does — like a seahorse. The leafy bits hide the dragon in kelp.",
    },
    "coral-reef": {
      q: "Are corals plants or animals?",
      a: "Animals! Tiny coral polyps build rocky homes. Algae living inside them help make food.",
    },
    "sea-anemone": {
      q: "Why don’t clownfish get stung by anemones?",
      a: "A special slime coat protects them — the anemone is their fortress home.",
    },
    "giant-clam": {
      q: "Why is a giant clam so colorful inside?",
      a: "Tiny algae live in its lips and make extra food — and those rainbow colors.",
    },
    "ocean-sunfish": {
      q: "Why does a mola look like a giant swimming head?",
      a: "It is the heaviest bony fish — a huge body with a tiny tail. It often eats jellies.",
    },
    frogfish: {
      q: "How does a frogfish catch dinner without chasing?",
      a: "It waits in camouflage, wiggles a worm-like lure, then gulps.",
    },
    nautilus: {
      q: "How does a nautilus go up and down?",
      a: "It pumps water in and out of shell chambers — a living submarine.",
    },
    orangutan: {
      q: "How long are orangutan arms?",
      a: "Longer than their legs — perfect for swinging through the canopy.",
    },
    koala: {
      q: "How much do koalas sleep?",
      a: "Up to 18–22 hours a day — eucalyptus leaves take lots of energy to digest.",
    },
    "giant-panda": {
      q: "What do giant pandas eat almost all day?",
      a: "Bamboo! They can munch 20–40 pounds a day with a special “thumb” grip.",
    },
    "red-panda": {
      q: "Is a red panda a mini giant panda?",
      a: "Nope — closer to raccoons/weasels. Same bamboo snack habit, different family!",
    },
    zebra: {
      q: "Why do zebras have stripes?",
      a: "Each pattern is unique — and stripes may confuse flies and predators.",
    },
    "polar-bear": {
      q: "Why is a polar bear’s fur white?",
      a: "The coat helps it hide on ice and snow. Underneath, the skin is actually black.",
    },
    "panther-chameleon": {
      q: "Why can a chameleon change color?",
      a: "Tiny crystals in the skin shift how light bounces — for mood, heat, and hiding.",
    },
    "saltwater-crocodile": {
      q: "Why does a crocodile look like a log?",
      a: "Still water and a bumpy back hide it so fish and birds come close.",
    },
    "red-kangaroo": {
      q: "Why does a kangaroo have a pouch?",
      a: "A joey is born tiny. The pouch is a warm pocket where it drinks milk and grows.",
    },
    "snow-leopard": {
      q: "Why does a snow leopard have a huge tail?",
      a: "The tail is a balance pole on cliffs and a scarf it wraps around itself to stay warm.",
    },
    "monarch-butterfly": {
      q: "How can a tiny butterfly travel so far?",
      a: "Monarchs ride wind and rest on flowers for fuel. It takes generations to finish the trip.",
    },
    "black-rhino": {
      q: "What’s a rhino horn made of?",
      a: "The same stuff as your hair and nails — keratin — packed tight, not bone.",
    },
    "hyacinth-macaw": {
      q: "Why is a macaw’s beak so huge?",
      a: "It cracks hard nuts. Two toes forward and two back help it climb like a parrot ladder.",
    },
    /* Children’s museum / science “wow” hooks (same strip UI) */
    "cm-outdoor": {
      q: "Try this",
      a: "Name one sound, one smell, and one thing that moves.",
    },
    "cm-toddler-garden": {
      q: "Toddler tip",
      a: "Doing the same path twice is normal — repetition is how little kids learn.",
    },
    "cm-imaginarium": {
      q: "Try this",
      a: "Ask what they “see” in pretend play — you don’t need a right answer.",
    },
    "cm-woven": {
      q: "Climbing tip",
      a: "Cheer the try, not only the top. Coming down counts too.",
    },
    "cm-makery": {
      q: "Maker tip",
      a: "“What if we try…?” beats getting it perfect on the first try.",
    },
    "cm-art-lab": {
      q: "Art tip",
      a: "Ask them to tell the story of their picture — mess is allowed.",
    },
    "cm-free-explore": {
      q: "Try this",
      a: "Let them pick the next stop for five minutes. Follow what pulls them in.",
    },
    "cm-waterfall": {
      q: "Water play",
      a: "Watch where the water goes — kids notice flow long before we name it “science.”",
    },
    "sci-dinosaur": {
      q: "Did you know?",
      a: "T. rex lived closer in time to us than to Stegosaurus.",
    },
    "sci-mammal-hall": {
      q: "Look closer",
      a: "In a diorama, find eyes, feet, and a place an animal might hide.",
    },
    "sci-planet": {
      q: "Space scale",
      a: "If Earth were a peppercorn, the Sun would be about beach-ball size across the room.",
    },
    "sci-hands-on": {
      q: "Lab tip",
      a: "Touch, test, mess up, try again — that’s the whole point.",
    },
    "sci-rainforest": {
      q: "Look up",
      a: "A lot of rainforest life lives high in the trees, not on the ground.",
    },
    "sci-aquarium-zone": {
      q: "Tank tip",
      a: "Stand still for 20 seconds — shy fish often come out when people stop bouncing.",
    },
    "sci-rocket": {
      q: "Did you know?",
      a: "To stay in orbit, spacecraft go about 17,500 mph.",
    },
    "sci-shuttle": {
      q: "Did you know?",
      a: "A space shuttle launched like a rocket, flew in space, and landed on a runway.",
    },
    "sci-astronaut": {
      q: "Did you know?",
      a: "Astronauts sleep strapped in — without gravity you’d float off the bed.",
    },
    "sci-magnet": {
      q: "Why does the black sand make spikes?",
      a: "The sand is magnetite — tiny bits of iron. Each grain becomes a little magnet and lines up along the field, so you can see the push and pull.",
    },
    "sci-light": {
      q: "Why can a shadow be red, green, or blue?",
      a: "Three lights mix to make white on the wall. Your body blocks one color, so the leftover mix paints a colored shadow.",
    },
    "sci-flight": {
      q: "How did the first airplane leave the ground?",
      a: "Moving air over a wing makes lift. Long wings help that air do more work, so a light plane can rise.",
    },
    "sci-robot": {
      q: "How can a robot fly where there is almost no air?",
      a: "Mars air is thin, so the blades spin very fast to grab enough lift. A computer flies it because a person on Earth is too far away to steer in time.",
    },
    "sci-lightning": {
      q: "Why does lightning jump?",
      a: "Storm clouds build opposite charges until a spark jumps. Light is fast; thunder is the boom of air that got super-hot, so sound arrives later.",
    },
    "sci-storm": {
      q: "Why does a giant storm spin?",
      a: "Warm ocean air rises and the spinning Earth twists it into a swirl. The eye is calmer because the strongest winds circle around it.",
    },
  };

  /**
   * One kid/parent wow line under the big photo.
   * Prefer curated fact → item.wow_fact → punchy blurb (not generic tags).
   */
  function wowFactFromItem(item) {
    if (!item) return null;
    const id = item.id || "";
    if (WOW_FACTS[id]) return WOW_FACTS[id];

    if (item.wow_fact) {
      const wf = item.wow_fact;
      if (typeof wf === "string" && wf.trim()) return { q: "Did you know?", a: wf.trim() };
      if (wf && wf.a) return { q: wf.q || "Did you know?", a: String(wf.a).trim() };
    }

    const blurb = item.blurb && String(item.blurb).trim();
    if (blurb && blurb.length >= 24) {
      return { q: "Did you know?", a: blurb };
    }

    const name = item.name || "This animal";
    const key = item.key || {};
    const superpower = [].concat(key.superpower || []).filter(Boolean);
    // Only use superpower if we can phrase it as a real sentence (not bare tags alone).
    if (superpower.length) {
      const powers = superpower.slice(0, 2).join(" and ").toLowerCase();
      return {
        q: `What's ${name}'s superpower?`,
        a: `They’re built to ${powers} — watch for it at the habitat!`,
      };
    }
    return null;
  }

  /**
   * One-letter-page Q&A card HTML (big bottom photo + wow fact).
   * @param {object} item catalog animal/exhibit
   * @param {object} venue
   * @param {object} [opts]
   * @param {Record<string, string[]>} [opts.answers] missionId → selected choice labels
   * @param {string} [opts.bannerNote] line under FIELD TRIP KIT title
   * @param {string} [opts.footer] footer line
   */
  function buildQaCardHtml(item, venue, opts) {
    const o = opts || {};
    const answerMap = o.answers || {};
    // Prefer caller-supplied missions (talk-level pack); else venue defaults
    // Hard cap content so letter print never needs page 2
    const missions = (Array.isArray(o.missions) && o.missions.length ? o.missions : missionsFor(venue)).slice(0, 6);
    const prompts = (Array.isArray(o.prompts) ? o.prompts : []).slice(0, 4);
    const talkLabel = o.talkLabel || o.talkLevel || "";
    const cards = missions
      .map((mission, index) => {
        const mid = mission.id || String(index);
        const selected = new Set(answerMap[mid] || answerMap[mission.id] || []);
        const choices = (mission.choices || [])
          .slice(0, 6)
          .map((label) => {
            const on = selected.has(label) ? " on" : "";
            return `<div class="ps-choice${on}"><span class="ps-dot"></span><span>${escapeHtml(label)}</span></div>`;
          })
          .join("");
        const writeIn =
          !mission.choices || !mission.choices.length
            ? `<p class="ps-write">________________________________</p><p class="ps-write">________________________________</p>`
            : "";
        return `<section class="ps-card c${index}">
          <div class="ps-card-head"><span class="ps-num">${escapeHtml(mission.num || String(index + 1))}</span>
          <p class="ps-title">${escapeHtml(mission.title || "Question")}</p></div>
          <h3 class="ps-q">${escapeHtml(mission.question || "")}</h3>
          <div class="ps-choices">${choices}</div>
          ${writeIn}</section>`;
      })
      .join("");
    const promptBlock =
      prompts.length > 0
        ? `<div class="ps-talk">
            <p class="ps-talk-label">${escapeHtml(talkLabel ? talkLabel + " · talk prompts" : "Talk prompts")}</p>
            <ol class="ps-talk-list">${prompts
              .slice(0, 6)
              .map((t) => `<li>${escapeHtml(String(t).replace(/^ALPHA · /, "").replace(/^★ /, ""))}</li>`)
              .join("")}</ol>
          </div>`
        : "";
    const photo = itemPhotoSrc(item);
    const wow = wowFactFromItem(item);
    const wowHtml = wow
      ? `<div class="ps-wow">
          <strong class="ps-wow-q">${escapeHtml(wow.q)}</strong>
          <span class="ps-wow-a">${escapeHtml(wow.a)}</span>
        </div>`
      : "";
    // Head-shot bias: catalog photoPosition (e.g. "50% 0%") overrides CSS default
    const photoPos = (item && (item.photoPosition || item.photoFocus)) || "";
    const photoPosStyle = photoPos
      ? ` style="--ps-photo-pos:${escapeAttr(String(photoPos))};object-position:${escapeAttr(String(photoPos))}"`
      : "";
    const photoBlock = photo
      ? `<div class="ps-photo-fill">
          <div class="ps-photo-frame">
            <img class="ps-photo-big" src="${escapeAttr(photo)}" alt="${escapeAttr(item.name || "Animal")}" decoding="async"${photoPosStyle} />
          </div>
          ${wowHtml}
        </div>`
      : wowHtml
        ? `<div class="ps-wow ps-wow-solo">
            <strong class="ps-wow-q">${escapeHtml(wow.q)}</strong>
            <span class="ps-wow-a">${escapeHtml(wow.a)}</span>
          </div>`
        : "";

    const levelBit = talkLabel ? ` · ${talkLabel}` : "";
    const bannerNote =
      o.bannerNote ||
      `${venue.name || ""} · Q&A card${levelBit} · Circle or write · No scores`;
    const footer =
      o.footer || "Q&amp;A card · same talk level as on screen";

    return `
      <div class="ps-page${photo ? " ps-page-with-photo" : ""}">
        <div class="ps-banner"><h1>FIELD TRIP KIT</h1>
        <p>${escapeHtml(bannerNote)}</p></div>
        <header class="ps-head">
          <h2>${escapeHtml(item.emoji || "")} ${escapeHtml(item.name)}</h2>
          <p class="ps-line"><strong>Explorer:</strong> <span class="write-in-line">________________</span>
          &nbsp;&nbsp; <strong>Place:</strong> ${escapeHtml(venue.name)}</p>
        </header>
        ${promptBlock}
        <div class="ps-grid">${cards}</div>
        ${photoBlock}
        <p class="ps-footer">${footer}</p>
      </div>`;
  }

  function setSafariLandscape(on) {
    let el = document.getElementById("hs-print-page-rule");
    if (on) {
      if (!el) {
        el = document.createElement("style");
        el.id = "hs-print-page-rule";
        el.textContent = "@page { size: letter landscape; margin: 0.35in; }";
        document.head.appendChild(el);
      }
    } else if (el) {
      el.remove();
    }
  }

  function runPrint({ treasure, safari }) {
    document.body.classList.toggle("printing-treasure", Boolean(treasure));
    document.body.classList.toggle("printing-safari", Boolean(safari));
    setSafariLandscape(Boolean(safari));
    const cleanup = () => {
      document.body.classList.remove("printing-treasure");
      document.body.classList.remove("printing-safari");
      setSafariLandscape(false);
      window.removeEventListener("afterprint", cleanup);
    };
    window.addEventListener("afterprint", cleanup);
    requestAnimationFrame(() => requestAnimationFrame(() => window.print()));
  }

  function waitForPrintImages(root) {
    const imgs = root ? [...root.querySelectorAll("img")] : [];
    if (!imgs.length) return Promise.resolve();
    return Promise.all(
      imgs.map(
        (img) =>
          new Promise((resolve) => {
            if (img.complete) {
              resolve();
              return;
            }
            const done = () => resolve();
            img.addEventListener("load", done, { once: true });
            img.addEventListener("error", done, { once: true });
            setTimeout(done, 2500);
          })
      )
    );
  }

  /**
   * Prefer mission drawer (age/time/interest → live sheet) when this page has one.
   * Falls back to legacy static treasure sheet only on app/landing without a drawer.
   */
  function openMissionDrawerIfPresent() {
    if (window.FPMissionUI && typeof window.FPMissionUI.open === "function") {
      window.FPMissionUI.open();
      return true;
    }
    if (document.getElementById("mission-drawer") || document.getElementById("mission-open-btn")) {
      if (location.hash !== "#mission") location.hash = "#mission";
      else {
        // Hash already set — still try click the open control
        const btn = document.getElementById("mission-open-btn");
        if (btn) btn.click();
      }
      return true;
    }
    return false;
  }

  /**
   * Print treasure hunt for a venue.
   * On SEO venue pages: opens customizable mission drawer (not static list).
   */
  function printTreasureForVenue(venueId) {
    if (openMissionDrawerIfPresent()) return true;

    const venue = getVenue(venueId);
    const { printSheet, treasureSheet } = sheets();
    if (!venue || !treasureSheet) {
      console.warn("[FPPrint] missing venue or #treasure-sheet", venueId);
      return false;
    }
    if (!(venue.treasureHunt && venue.treasureHunt.length)) {
      console.warn("[FPPrint] no treasure hunt for", venueId);
      return false;
    }
    treasureSheet.innerHTML = buildTreasureHtml(venue, venue.featuredAnimalIds);
    if (printSheet) printSheet.innerHTML = "";
    track("hunt_generated", {
      venue_slug: venue.id || venueId,
      venue_name: venue.name || "",
      product: "babys_day_out",
      source: "print_kit",
    });
    runPrint({ treasure: true });
    return true;
  }

  /**
   * Print one sample Q&A card — first featured / top-pick item for the venue.
   */
  function printSampleQaForVenue(venueId) {
    const venue = getVenue(venueId);
    const itemId = topPickItemId(venue);
    const item = itemId ? getItem(itemId, venue) : null;
    const { printSheet, treasureSheet } = sheets();
    if (!venue || !item || !printSheet) {
      console.warn("[FPPrint] sample Q&A unavailable for", venueId);
      return false;
    }
    printSheet.innerHTML = buildQaCardHtml(item, venue, {
      bannerNote: `${venue.name} · Sample mission card · Circle answers · No scores`,
      footer: "Sample Q&amp;A · open the outing for more animals &amp; tips",
    });
    if (treasureSheet) treasureSheet.innerHTML = "";
    track("qa_sample_printed", {
      venue_slug: venue.id || venueId,
      venue_name: venue.name || "",
      item_id: item.id,
      item_name: item.name || "",
      product: "babys_day_out",
    });
    runPrint({ treasure: false });
    return true;
  }

  /**
   * Fill #print-sheet with a Q&A card for any catalog item (shared by app print button).
   * Does not call window.print — caller owns the dialog.
   */
  function fillQaPrintSheet(item, venue, opts) {
    const { printSheet, treasureSheet } = sheets();
    if (!item || !venue || !printSheet) return false;
    printSheet.innerHTML = buildQaCardHtml(item, venue, opts);
    if (treasureSheet) treasureSheet.innerHTML = "";
    return true;
  }

  /** First venue that lists this catalog item (for standalone card print). */
  function venueIdForItem(itemId) {
    if (!itemId) return null;
    const venues = window.FIELD_PACK_VENUES || {};
    for (const [vid, v] of Object.entries(venues)) {
      const ids = [...(v.featuredAnimalIds || []), ...(v.animalIds || [])];
      if (ids.includes(itemId)) return vid;
    }
    return null;
  }

  /**
   * Print a Q&A one-pager for any catalog item (animal / attraction).
   * Uses preferredVenueId when provided; else first venue that lists the item;
   * else a lightweight synthetic venue with animal missions.
   */
  function printQaForItem(itemId, preferredVenueId) {
    const item = getItem(itemId, null);
    if (!item) {
      console.warn("[FPPrint] unknown item", itemId);
      return false;
    }
    const vid = preferredVenueId || venueIdForItem(itemId);
    let venue = vid ? getVenue(vid) : null;
    if (!venue) {
      venue = {
        id: "catalog",
        name: "Field Trip Kit",
        packTemplate:
          itemId && String(itemId).startsWith("sci-")
            ? "exhibits"
            : itemId && String(itemId).startsWith("cm-")
              ? "exhibits"
              : "animals",
        animalIds: [itemId],
        featuredAnimalIds: [itemId],
      };
    }
    const resolved = getItem(itemId, venue) || item;
    const { printSheet, treasureSheet } = sheets();
    if (!printSheet) return false;
    printSheet.innerHTML = buildQaCardHtml(resolved, venue, {
      bannerNote: `${resolved.name || itemId} · Q&A card · Circle answers · No scores`,
      footer: "Catalog card · Field Trip Kit",
    });
    if (treasureSheet) treasureSheet.innerHTML = "";
    track("qa_catalog_printed", {
      item_id: resolved.id || itemId,
      item_name: resolved.name || "",
      venue_slug: venue.id || "",
      product: "babys_day_out",
      source: "catalog",
    });
    runPrint({ treasure: false });
    return true;
  }

  function habitatEmoji(h) {
    if (!h) return "";
    if (h.emoji) return h.emoji;
    const id = h.cardId || h.id;
    const item = getItem(id, null);
    return (item && item.emoji) || "🐾";
  }

  function habitatName(h) {
    if (!h) return "";
    const id = h.cardId || h.id;
    const item = getItem(id, null);
    return (item && item.name) || h.label || id || "";
  }

  function habitatPhoto(h) {
    if (!h) return "";
    if (h.photo) {
      const p = h.photo;
      if (/^https?:\/\//i.test(p) || p.startsWith("/")) return p;
      if (p.startsWith("photos/")) return "/field-pack/" + p;
      return "/field-pack/photos/" + String(p).replace(/^\/+/, "");
    }
    const id = h.cardId || h.id;
    const item = getItem(id, null);
    return item ? itemPhotoSrc(item) : "";
  }

  const HS_SLOTS = 10;
  const HS_COLS = 5;

  function padHuntSlots(habitats) {
    const list = (habitats || []).slice(0, HS_SLOTS);
    while (list.length < HS_SLOTS) list.push(null);
    return list;
  }

  /**
   * Two landscape pages for duplex: photo+question, then answers.
   * Landscape two-sided (flip on the long edge) swaps top and bottom only.
   * Page 2 is row-mirrored + 180° type so each answer sits on the back of its photo.
   */
  function printHomeSafari(config, habitats) {
    const { printSheet, treasureSheet } = sheets();
    if (!printSheet || !config) return false;
    const raw = (Array.isArray(habitats) && habitats.length ? habitats : config.habitats) || [];
    const list = padHuntSlots(raw);
    printSheet.innerHTML = buildCutPageHtml(config, list) + buildAnswerPageHtml(config, list);
    if (treasureSheet) treasureSheet.innerHTML = "";
    track("home_mission_printed", {
      mode: "cut+answers",
      venue_kind: config.kind || "zoo",
      tab: config.tab || config.kind || "zoo",
      count: list.length,
      product: "field_trip_kit",
    });
    waitForPrintImages(printSheet).then(() => runPrint({ treasure: false, safari: true }));
    return true;
  }

  function habitatAnswer(h) {
    return (h && (h.printAnswer || h.answer)) || "";
  }

  function cutCardHtml(h) {
    if (!h) return `<article class="hs-cut is-blank" aria-hidden="true"></article>`;
    const src = habitatPhoto(h);
    const media = src
      ? `<img class="hs-cut-photo" src="${escapeAttr(src)}" alt="" />`
      : `<span class="hs-cut-emoji">${escapeHtml(habitatEmoji(h))}</span>`;
    const ask = h.challenge
      ? `<p class="hs-cut-ask">${escapeHtml(h.challenge)}</p>`
      : "";
    return `<article class="hs-cut">
      <div class="hs-cut-media">${media}<span class="hs-box" title="Found" aria-hidden="true"></span></div>
      <div class="hs-cut-write" aria-hidden="true"><span class="hs-cut-rule"></span><span class="hs-cut-rule"></span></div>
      <div class="hs-cut-foot">
        <span class="hs-cut-name">${escapeHtml(habitatName(h))}</span>
        ${ask}
      </div>
    </article>`;
  }

  function answerCardHtml(h) {
    if (!h) return `<article class="hs-cut hs-cut-answer is-blank" aria-hidden="true"></article>`;
    const ans = habitatAnswer(h);
    return `<article class="hs-cut hs-cut-answer">
      <div class="hs-answer-turn">
        <span class="hs-cut-name">${escapeHtml(habitatName(h))}</span>
        ${ans ? `<p class="hs-cut-ans">${escapeHtml(ans)}</p>` : ""}
      </div>
    </article>`;
  }

  function huntGridCols(n) {
    if (n <= 2) return Math.max(n, 1);
    if (n <= 4) return 2;
    if (n <= 6) return 3;
    if (n <= 8) return 4;
    if (n === 9) return 3;
    return 5;
  }

  function longEdgeMirrorIndex(i, n, cols) {
    const col = i % cols;
    const row = Math.floor(i / cols);
    const rows = Math.max(1, Math.ceil(n / cols));
    return (rows - 1 - row) * cols + col;
  }

  function buildCutPageHtml(config, habitats) {
    const banner = (config && config.printHideBanner) || "Hide-and-seek at home";
    const sub =
      (config && config.printHideSub) ||
      "Cut the cards. Hide them. Write in the box. Ask the question.";
    const footer = (config && config.printFooter) || "1less.app/field-pack/virtual-field-trip/ · Field Trip Kit";
    const cols = HS_COLS;
    return `<div class="hs-page hs-page-cut">
      <div class="hs-banner"><h1>${escapeHtml(banner)}</h1>
      <p>${escapeHtml(sub)}</p></div>
      <div class="hs-cuts" style="--hs-cols:${cols}">${habitats.map(cutCardHtml).join("")}</div>
      <p class="hs-footer">${escapeHtml(footer)}</p>
    </div>`;
  }

  function buildAnswerPageHtml(config, habitats) {
    const banner = (config && config.printHideBanner) || "Hide-and-seek at home";
    const sub = "Answers. Print two-sided.";
    const footer = (config && config.printFooter) || "1less.app/field-pack/virtual-field-trip/ · Field Trip Kit";
    const cols = HS_COLS;
    const cards = habitats
      .map((_, i) => answerCardHtml(habitats[longEdgeMirrorIndex(i, habitats.length, cols)]))
      .join("");
    return `<div class="hs-page hs-page-answers">
      <div class="hs-banner"><h1>${escapeHtml(banner)}</h1>
      <p>${escapeHtml(sub)}</p></div>
      <div class="hs-cuts" style="--hs-cols:${cols}">${cards}</div>
      <p class="hs-footer">${escapeHtml(footer)}</p>
    </div>`;
  }

  window.FPPrint = {
    printTreasureForVenue,
    printSampleQaForVenue,
    printQaForItem,
    fillQaPrintSheet,
    printHomeSafari,
    buildQaCardHtml,
    itemPhotoSrc,
    wowFactFromItem,
    topPickItemId,
    venueIdForItem,
    getVenue,
    getItem,
  };
})();
