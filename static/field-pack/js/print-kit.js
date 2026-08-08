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

  function getItem(id) {
    return (window.FIELD_PACK_CATALOG && window.FIELD_PACK_CATALOG[id]) || null;
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
        const it = getItem(id);
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
          <h1>🗺️ Your mission</h1>
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
    const missions = (Array.isArray(o.missions) && o.missions.length ? o.missions : missionsFor(venue)).slice(0, 6);
    const prompts = (Array.isArray(o.prompts) ? o.prompts : []).slice(0, 6);
    const talkLabel = o.talkLabel || o.talkLevel || "";
    const cards = missions
      .map((mission, index) => {
        const mid = mission.id || String(index);
        const selected = new Set(answerMap[mid] || answerMap[mission.id] || []);
        const choices = (mission.choices || [])
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
    const photoBlock = photo
      ? `<div class="ps-photo-fill">
          <div class="ps-photo-frame">
            <img class="ps-photo-big" src="${escapeAttr(photo)}" alt="${escapeAttr(item.name || "Animal")}" />
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

  function runPrint({ treasure }) {
    document.body.classList.toggle("printing-treasure", Boolean(treasure));
    const cleanup = () => {
      document.body.classList.remove("printing-treasure");
      window.removeEventListener("afterprint", cleanup);
    };
    window.addEventListener("afterprint", cleanup);
    requestAnimationFrame(() => requestAnimationFrame(() => window.print()));
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
    const item = itemId ? getItem(itemId) : null;
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

  window.FPPrint = {
    printTreasureForVenue,
    printSampleQaForVenue,
    fillQaPrintSheet,
    buildQaCardHtml,
    itemPhotoSrc,
    wowFactFromItem,
    topPickItemId,
    getVenue,
    getItem,
  };
})();
