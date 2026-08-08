(() => {
  const catalog = window.FIELD_PACK_CATALOG;
  const storageKey = "1less-babys-day-out-trips-v1";
  const legacyStorageKeys = ["arya-field-pack-trips-v2", "arya-field-pack-trips-v1"];
  const defaultVenue = window.fpDefaultVenueId || "dallas-zoo";
  const precooked = window.fpPrecookedVenueIds || ["dallas-zoo"];

  const els = {
    outing: document.getElementById("view-outing"),
    detail: document.getElementById("view-detail"),
    backBtn: document.getElementById("btn-back"),
    brandSub: document.getElementById("brand-sub"),
    outingVenueChip: document.getElementById("outing-venue-chip"),
    outingHeading: document.getElementById("outing-heading"),
    outingBlurb: document.getElementById("outing-blurb"),
    outingGrid: document.getElementById("outing-grid"),
    outingEmpty: document.getElementById("outing-empty"),
    outingGridHeading: document.getElementById("outing-grid-heading"),
    btnTreasure: document.getElementById("btn-treasure"),
    btnSampleQa: document.getElementById("btn-sample-qa"),
    sampleQaHint: document.getElementById("sample-qa-hint"),
    btnShareLink: document.getElementById("btn-share-link"),
    shareLinkStatus: document.getElementById("share-link-status"),
    btnZooSite: document.getElementById("btn-zoo-site"),
    btnToggleCustomize: document.getElementById("btn-toggle-customize"),
    customizePanel: document.getElementById("customize-panel"),
    customizeGrid: document.getElementById("customize-grid"),
    detailName: document.getElementById("detail-name"),
    detailBlurb: document.getElementById("detail-blurb"),
    detailPhoto: document.getElementById("detail-photo"),
    detailCredit: document.getElementById("detail-credit"),
    missionGrid: document.getElementById("mission-grid"),
    progressPill: document.getElementById("progress-pill"),
    teachBanner: document.getElementById("teach-banner"),
    btnCam: document.getElementById("btn-cam"),
    btnPictures: document.getElementById("btn-pictures"),
    btnMore: document.getElementById("btn-more"),
    btnTaught: document.getElementById("btn-taught"),
    btnMoreQuestions: document.getElementById("btn-more-questions"),
    advancedQa: document.getElementById("advanced-qa"),
    btnPrint: document.getElementById("btn-print"),
    btnSubmit: document.getElementById("btn-submit"),
    resultsPanel: document.getElementById("results-panel"),
    printSheet: document.getElementById("print-sheet"),
    treasureSheet: document.getElementById("treasure-sheet"),
    winBanner: document.getElementById("win-banner"),
    btnWinPrint: document.getElementById("btn-win-print"),
    btnWinList: document.getElementById("btn-win-list"),
  };

  let store = loadStore();
  let selectedVenueId = store.selectedVenueId || defaultVenue;
  let currentTripId = null;
  let currentItemId = null;

  function loadStore() {
    try {
      let raw = localStorage.getItem(storageKey);
      if (!raw) {
        for (const k of legacyStorageKeys) {
          raw = localStorage.getItem(k);
          if (raw) break;
        }
      }
      if (!raw) return { trips: [], selectedVenueId: defaultVenue };
      const parsed = JSON.parse(raw);
      if (!parsed || !Array.isArray(parsed.trips)) return { trips: [], selectedVenueId: defaultVenue };
      return {
        trips: (parsed.trips || []).map((t) => ({ ...t, venueId: t.venueId || defaultVenue })),
        selectedVenueId: parsed.selectedVenueId || defaultVenue,
      };
    } catch {
      return { trips: [], selectedVenueId: defaultVenue };
    }
  }

  function saveStore() {
    store.selectedVenueId = selectedVenueId;
    localStorage.setItem(storageKey, JSON.stringify(store));
  }

  function uid() {
    return "t-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 7);
  }

  function getVenue(id) {
    return window.fpGetVenue(id);
  }
  function getItem(id) {
    return catalog[id] || null;
  }
  function getTrip(id) {
    return store.trips.find((t) => t.id === id) || null;
  }
  function missionsFor(venue) {
    return window.fpMissionsForVenue(venue);
  }

  function itemState(trip, itemId) {
    if (!trip.animals) trip.animals = {};
    if (!trip.animals[itemId]) {
      trip.animals[itemId] = { answers: {}, taught: false, submitted: false };
    }
    if (!trip.animals[itemId].answers) trip.animals[itemId].answers = {};
    return trip.animals[itemId];
  }

  function answeredCount(trip, itemId, missions) {
    const a = itemState(trip, itemId);
    return missions.filter((m) => (a.answers[m.id] || []).length > 0).length;
  }

  /** One active outing per venue — auto featured shortlist */
  function ensureOuting(venueId) {
    const venue = getVenue(venueId);
    if (!venue) return null;
    selectedVenueId = venueId;
    let trip = store.trips
      .filter((t) => t.venueId === venueId)
      .sort((a, b) => (b.updatedAt || 0) - (a.updatedAt || 0))[0];
    if (!trip) {
      const featured = venue.featuredAnimalIds || venue.animalIds || [];
      trip = {
        id: uid(),
        title: venue.name || venue.shortName || "Visit",
        venueId: venue.id,
        date: "",
        selectedAnimalIds: [...featured],
        animals: {},
        createdAt: Date.now(),
        updatedAt: Date.now(),
      };
      store.trips.push(trip);
      saveStore();
    } else if (!trip.selectedAnimalIds || !trip.selectedAnimalIds.length) {
      trip.selectedAnimalIds = [...(venue.featuredAnimalIds || venue.animalIds || [])];
      trip.updatedAt = Date.now();
      saveStore();
    }
    currentTripId = trip.id;
    return trip;
  }

  function hideAll() {
    els.outing.classList.add("hidden");
    els.detail.classList.add("hidden");
  }

  function setBackToList(on) {
    if (!on) {
      els.backBtn.classList.add("hidden");
      return;
    }
    els.backBtn.classList.remove("hidden");
    els.backBtn.textContent = "← Back to list";
  }

  function showOuting(venueId) {
    const id = venueId || selectedVenueId || defaultVenue;
    if (!precooked.includes(id) && !getVenue(id)) {
      location.href = "/field-pack/";
      return;
    }
    const trip = ensureOuting(id);
    const venue = getVenue(id);
    if (!trip || !venue) {
      location.href = "/field-pack/";
      return;
    }
    currentItemId = null;
    hideAll();
    showWinBanner(false);
    els.outing.classList.remove("hidden");
    setBackToList(false);
    els.customizePanel.classList.add("hidden");
    els.btnToggleCustomize.setAttribute("aria-expanded", "false");
    const placeLabel = venue.name || venue.shortName || "This place";
    els.brandSub.textContent = placeLabel;
    els.outingVenueChip.textContent = venue.location
      ? `📍 ${venue.location}`
      : `📍 ${placeLabel}`;
    els.outingHeading.textContent = placeLabel;
    els.outingBlurb.textContent =
      "Print the treasure hunt for your bag. Cards below are things to find — tap one later for optional tips.";
    els.btnZooSite.href = venue.website || "#";
    setDocMeta({
      title: `${placeLabel} · Kid list & hunt · Field Trip Kit · 1Less`,
      description: `Free printable scavenger hunt and short kid list for ${placeLabel}${
        venue.location ? ` in ${venue.location}` : ""
      }. Field Trip Kit by 1Less.`,
    });
    // Prefer indexable SEO URL in the browser URL bar when sharing is not mid-session
    try {
      const seoPath = `/field-pack/${encodeURIComponent(venue.id)}/`;
      const linkCanon = document.querySelector('link[rel="canonical"]');
      if (!linkCanon) {
        const l = document.createElement("link");
        l.rel = "canonical";
        l.href = `${location.origin}${seoPath}`;
        document.head.appendChild(l);
      } else {
        linkCanon.setAttribute("href", `${location.origin}${seoPath}`);
      }
    } catch {
      /* ignore */
    }
    els.outingGridHeading.textContent = "Things to find";
    const gridSub = document.getElementById("outing-grid-sub");
    if (gridSub) {
      const kind = venue.itemLabel || "things";
      gridSub.textContent = `Your short list (${kind}) · tap a card for optional tips`;
    }
    // Sample Q&A: top featured pick — label button with animal name when known
    const topId =
      (window.FPPrint && window.FPPrint.topPickItemId(venue)) ||
      (venue.featuredAnimalIds && venue.featuredAnimalIds[0]) ||
      null;
    const topItem = topId ? getItem(topId) : null;
    if (els.btnSampleQa) {
      const canSample = Boolean(topItem);
      els.btnSampleQa.hidden = !canSample;
      els.btnSampleQa.disabled = !canSample;
      if (canSample) {
        const short = topItem.name.length > 22 ? topItem.name.slice(0, 20) + "…" : topItem.name;
        els.btnSampleQa.innerHTML = `Try a sample: ${topItem.emoji || ""} ${escapeHtml(short)}`.trim();
        els.btnSampleQa.setAttribute(
          "aria-label",
          `Try a sample Q&A card for ${topItem.name}`
        );
      }
    }
    if (els.sampleQaHint) {
      els.sampleQaHint.hidden = !topItem;
      if (topItem) {
        els.sampleQaHint.textContent = `Try a top-pick Q&A card (${topItem.name}) — then open more ${
          venue.itemLabel || "items"
        } below.`;
      }
    }
    renderOutingGrid(trip, venue);
    renderCustomize(trip, venue);
    history.replaceState(null, "", `#/venue/${venue.id}`);
  }

  function showItem(tripId, itemId) {
    const trip = getTrip(tripId) || ensureOuting(selectedVenueId);
    const item = getItem(itemId);
    if (!trip || !item) return showOuting(selectedVenueId);
    if (!trip.selectedAnimalIds.includes(itemId)) {
      // allow opening from customize even if temporarily off
      if (!(getVenue(trip.venueId).animalIds || []).includes(itemId)) return showOuting(trip.venueId);
      if (!trip.selectedAnimalIds.includes(itemId)) {
        trip.selectedAnimalIds.push(itemId);
        saveStore();
      }
    }
    currentTripId = trip.id;
    currentItemId = itemId;
    selectedVenueId = trip.venueId;
    hideAll();
    els.detail.classList.remove("hidden");
    setBackToList(true);
    els.brandSub.textContent = item.name;
    const venue = getVenue(trip.venueId);
    const placeLabel = (venue && (venue.name || venue.shortName)) || "This place";
    setDocMeta({
      title: `${item.name} · ${placeLabel} · Field Trip Kit · 1Less`,
      description: `Optional tips and printable Q&A for ${item.name} at ${placeLabel}. Field Trip Kit by 1Less.`,
    });
    renderDetail(trip, item, venue);
    history.replaceState(null, "", `#/venue/${trip.venueId}/item/${itemId}`);
  }

  function renderOutingGrid(trip, venue) {
    const missions = missionsFor(venue);
    const ids = trip.selectedAnimalIds || [];
    els.outingGrid.innerHTML = "";
    els.outingEmpty.classList.toggle("hidden", ids.length > 0);
    for (const id of ids) {
      const item = getItem(id);
      if (!item) continue;
      const st = itemState(trip, id);
      const done = answeredCount(trip, id, missions);
      let status = "Talk prompts · print card";
      if (st.submitted) status = "Picks checked ✓";
      else if (st.taught) status = "Spotted ⭐";
      else if (done) status = `${done} pick-one started`;
      const hasCam = Boolean(item.links && item.links.cam);
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "animal-card" + (done || st.taught || st.submitted ? " has-progress" : "");
      btn.innerHTML = `
        <span class="animal-card-media">
          <img src="${item.photo}" alt="${escapeHtml(item.name)}" loading="lazy" />
          ${hasCam ? `<span class="animal-cam-badge" title="Live cam available">Live cam</span>` : ""}
        </span>
        <span class="meta">
          <span class="name">${item.emoji || ""} ${escapeHtml(item.name)}</span>
          <span class="status">${status}</span>
        </span>`;
      btn.addEventListener("click", () => showItem(trip.id, id));
      els.outingGrid.appendChild(btn);
    }
  }

  function renderCustomize(trip, venue) {
    const all = venue.animalIds || [];
    const selected = new Set(trip.selectedAnimalIds || []);
    els.customizeGrid.innerHTML = "";
    for (const id of all) {
      const item = getItem(id);
      if (!item) continue;
      const on = selected.has(id);
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "picker-card" + (on ? " selected" : "");
      btn.innerHTML = `
        <img src="${item.photo}" alt="" loading="lazy" />
        <span class="picker-check">${on ? "✓" : ""}</span>
        <span class="picker-name">${item.emoji || ""} ${escapeHtml(item.name)}</span>`;
      btn.addEventListener("click", () => {
        const set = new Set(trip.selectedAnimalIds || []);
        if (set.has(id)) {
          if (set.size <= 1) return; // keep at least one
          set.delete(id);
        } else set.add(id);
        trip.selectedAnimalIds = [...set];
        trip.updatedAt = Date.now();
        saveStore();
        renderCustomize(trip, venue);
        renderOutingGrid(trip, venue);
      });
      els.customizeGrid.appendChild(btn);
    }
  }

  function evaluateMission(item, mission, selectedList) {
    const selected = selectedList || [];
    if (!mission.checkable) {
      return {
        kind: "open",
        ok: selected.length > 0,
        feedback:
          selected.length > 0
            ? `⭐ ${mission.openNote || "Nice pick!"}`
            : `Pick something for “${mission.title}”`,
        correctKey: [],
        wrongPicks: [],
        rightPicks: selected,
        alwaysOk: [],
      };
    }
    const keyList = (item.key && item.key[mission.id]) || [];
    const alwaysOk = new Set(mission.alwaysOk || []);
    const correct = new Set(keyList);
    const accepted = new Set([...keyList, ...alwaysOk]);
    const rightPicks = selected.filter((c) => accepted.has(c));
    const wrongPicks = selected.filter((c) => !accepted.has(c));
    const hasCoreHit = keyList.length === 0 ? selected.length > 0 : selected.some((c) => correct.has(c));
    const ok =
      keyList.length === 0
        ? selected.length > 0 && wrongPicks.length === 0
        : hasCoreHit && wrongPicks.length === 0;
    let feedback;
    if (selected.length === 0) {
      feedback = keyList.length ? `No circles yet. Try: ${keyList.join(" · ")}` : "Circle what you did!";
    } else if (ok) {
      feedback = `Yes! Explorer match: ${rightPicks.join(" · ") || selected.join(" · ")}`;
    } else if (wrongPicks.length && hasCoreHit) {
      feedback = `Close! Keep ${rightPicks.join(" · ")}. Look again at: ${wrongPicks.join(" · ")}.`;
    } else if (wrongPicks.length) {
      feedback = `Let’s look again. Tips: ${keyList.join(" · ") || "what you really tried"}`;
    } else {
      feedback = `Good start! Also think about: ${keyList.join(" · ")}`;
    }
    return {
      kind: ok ? "ok" : "try",
      ok,
      feedback,
      correctKey: keyList,
      wrongPicks,
      rightPicks,
      alwaysOk: [...alwaysOk],
    };
  }

  function evaluateItem(trip, item, missions) {
    const aState = itemState(trip, item.id);
    return missions.map((mission) => ({
      mission,
      result: evaluateMission(item, mission, aState.answers[mission.id] || []),
    }));
  }

  /** Q&A talk levels (not the same as mission "Adults" sheet). */
  const QA_AGE_KEY = "1less-qa-talk-level";
  const QA_AGE_ORDER = ["2-3", "4-5", "6-8", "bonus"];
  let qaAge = "4-5";

  function loadQaAge() {
    try {
      const v = localStorage.getItem(QA_AGE_KEY);
      if (v && QA_AGE_ORDER.includes(v)) qaAge = v;
    } catch (_) {
      /* ignore */
    }
    return qaAge;
  }

  function saveQaAge(v) {
    qaAge = QA_AGE_ORDER.includes(v) ? v : "4-5";
    try {
      localStorage.setItem(QA_AGE_KEY, qaAge);
    } catch (_) {
      /* ignore */
    }
    return qaAge;
  }

  function isMuseumVenue(venue) {
    return Boolean(
      venue &&
        (venue.packTemplate === "exhibits" ||
          /museum|science|space|history|children/i.test(String(venue.type || "")))
    );
  }

  function isAquariumVenue(venue) {
    return Boolean(venue && /aquarium|aq/i.test(String(venue.type || venue.packTemplate || "")));
  }

  /** Hard wow facts → turn into bonus questions (animal-specific when we can). */
  const BONUS_WOW = {
    "african-elephant": [
      "An elephant’s trunk has about 40,000 muscles — more than your whole body. Why might that help?",
      "Elephants can hear low rumbles through their feet. What would you “hear” if you could feel sound?",
      "They use mud like sunscreen. Spot any mud (or dust) on this one?",
    ],
    "reticulated-giraffe": [
      "A giraffe’s tongue can be ~45 cm long and dark to avoid sunburn. Did you see the tongue?",
      "They only need short naps. Why might a tall animal sleep so little in the wild?",
      "Every giraffe’s spot pattern is unique — like a fingerprint. Compare two if you can.",
    ],
    "african-lion": [
      "A lion’s roar can carry for miles. Why roar instead of sneak all the time?",
      "Males often have manes; females often lead hunts. What jobs do you see here?",
      "Lions rest a huge part of the day. What burns their energy when they *do* move?",
    ],
    "sumatran-tiger": [
      "No two tigers have the same stripe pattern. Sketch one stripe set in your mind.",
      "Tigers are mostly solo hunters. How is that different from lions?",
      "Orange + black looks loud to us — in forest shade it can hide. Where would you hide?",
    ],
    "western-lowland-gorilla": [
      "A silverback can weigh as much as two adults. What clues show strength without fighting?",
      "Gorillas build new nests almost every night. What would you use for a nest here?",
      "They eat mostly plants. Find evidence of munching or foraging.",
    ],
    chimpanzee: [
      "Chimps use tools in the wild (sticks, stones). What “tool” would help *you* here?",
      "Faces and hands look almost human. What emotion do you read right now?",
      "They live in complex social groups. Who seems in charge of the moment?",
    ],
    "african-penguin": [
      "They “fly” underwater with wing-like flippers. Compare swimming vs walking.",
      "A layer of air under the feathers helps insulation. Why stay dry under the feathers?",
      "Colony noise is part of finding mates and chicks. What sounds do you hear?",
    ],
    "giant-panda": [
      "Bamboo is low-calorie — pandas eat many hours a day. Spot chewing?",
      "A “pseudo-thumb” helps grip bamboo. Watch the front paws carefully.",
      "Black-and-white may help in forests and snow. Where would each color hide?",
    ],
    koala: [
      "Eucalyptus leaves are tough and toxic to many animals. Why chew so slowly?",
      "They sleep a huge part of the day to save energy. Is this one awake or out?",
      "A koala’s pouch opens downward. Why might that help a climbing mom?",
    ],
    "red-panda": [
      "Not a giant panda — closer to raccoons in the family tree. What looks “cat-like” vs “bear-like”?",
      "They use a wrist bone like a thumb to climb. Watch the front paws on branches.",
      "Mostly crepuscular (dawn/dusk). Why might heat or crowds change when you see them?",
    ],
    shark: [
      "Many sharks never stop swimming — water must move over gills. Is this one cruising or resting?",
      "A sandpapery skin of tiny teeth (denticles) cuts drag. Why smooth vs rough matter?",
      "Senses include smell and tiny electrical cues. What would *you* sense in dark water?",
    ],
    octopus: [
      "Three hearts and blue blood — built for cold, low-oxygen water. What looks “alien” here?",
      "They can squeeze through any hole bigger than their beak. Find the hard beak area.",
      "Camouflage is instant. How many colors/textures do you see in one minute?",
    ],
    jellyfish: [
      "No brain — just a nerve net. How do they still pulse and catch food?",
      "Mostly water by weight. Why do they still sting?",
      "Some glow. What would light help with in deep or dark water?",
    ],
    "sea-turtle": [
      "They return to nesting beaches using Earth’s magnetic field. What “map” would you use?",
      "Flippers ≠ feet. How is swimming shape different from a tortoise?",
      "Plastic bags can look like jellyfish. Why is trash a sea-turtle problem?",
    ],
    "sci-dinosaur": [
      "Birds are living dinosaurs. What on a bird is a dino clue?",
      "Teeth and hips tell diet and stance. What would *your* fossil say about you?",
      "Size fools us in museums. What looks bigger up close than you expected?",
    ],
  };

  function itemTags(item) {
    return new Set((item && item.tags) || []);
  }

  function itemCatalogId(item) {
    return String((item && (item.catalog_id || item.id)) || "").toLowerCase();
  }

  function bonusPromptsFor(item, venue) {
    const name = item.name || "this stop";
    const id = itemCatalogId(item);
    const tags = itemTags(item);
    const place = (venue && (venue.shortName || venue.name)) || "here";
    const bank = BONUS_WOW[id] || BONUS_WOW[id.replace(/_/g, "-")] || null;
    if (bank && bank.length) return bank.slice(0, 3);

    // Tag / type fallbacks — still harder than kid prompts
    if (tags.has("big-cats") || /lion|tiger|cheetah|leopard/i.test(name)) {
      return [
        `Big cats hide in plain sight. Where would ${name} vanish in wild cover?`,
        "Quiet feet + sharp eyes: which body part is the real hunting tool?",
        `If you only had 60 seconds at ${place}, what one detail would you photograph?`,
      ];
    }
    if (tags.has("water") || isAquariumVenue(venue)) {
      return [
        `Water is thicker than air. How does ${name} move differently than a land animal?`,
        "Find one adaptation for breathing, steering, or staying hidden.",
        "What’s the quietest thing happening in this tank right now?",
      ];
    }
    if (isMuseumVenue(venue) || tags.has("read") || tags.has("hands")) {
      return [
        `What’s the one design choice at “${name}” that makes kids stop walking?`,
        "If you had to explain this stop in one sentence to a friend, what would you say?",
        "Find a detail most visitors walk past — label, texture, or hidden model.",
      ];
    }
    // Generic hard wow
    return [
      `What’s the strangest true thing you can spot about ${name} in 30 seconds?`,
      "If this animal (or exhibit) could talk, what would it complain about today?",
      `Why is ${name} a highlight of ${place} — not just “another stop”?`,
    ];
  }

  function floorPromptsFor(item, venue, age) {
    const name = item.name || "it";
    const band = QA_AGE_ORDER.includes(age) ? age : "4-5";
    const museum = isMuseumVenue(venue);
    const key = item.key || {};
    const food = (key.food && key.food[0]) || "";
    const home = (key.home && key.home[0]) || "";
    const power = (key.superpower && key.superpower[0]) || "";

    if (band === "bonus") return bonusPromptsFor(item, venue);

    if (band === "2-3") {
      if (museum) {
        return [
          `Point to something at ${name}. Big or small?`,
          "Can you copy a move — climb, reach, or tiptoe?",
          "Make a sound or a quiet face for what you saw.",
        ];
      }
      return [
        `Find the ${name}. Wave or point!`,
        "Is it moving or still? Show me with your body.",
        "What color do you see first?",
      ];
    }

    if (band === "6-8") {
      if (museum) {
        return [
          `What problem does “${name}” help you understand?`,
          "Compare two parts of this stop — which surprised you more?",
          "Teach a friend one fact you’d actually remember tomorrow.",
        ];
      }
      return [
        `How is ${name} built for its job${power ? ` (think: ${power})` : ""}?`,
        food ? `What clue says it might eat like “${food}”?` : `What would ${name} eat — and how can you tell?`,
        home ? `Home is like “${home}”. What here matches that habitat?` : `Where would ${name} hide or rest in the wild?`,
      ];
    }

    // 4-5 kids (default)
    if (museum) {
      return [
        `What did you try or notice at ${name}?`,
        "How did your body move — climb, hands, quiet look?",
        "Tell a grown-up one thing you discovered.",
      ];
    }
    return [
      `What do you notice about the ${name}?`,
      "How does it move — or stay still?",
      food ? `What might it eat? (Hint family: ${food})` : "What might it eat?",
    ];
  }

  function qaKickerFor(age) {
    if (age === "bonus") return "Bonus round · hard wow questions";
    if (age === "2-3") return "Little kids · notice & play";
    if (age === "6-8") return "Big kids · think & compare";
    return "Notice & talk";
  }

  function syncQaAgeChips() {
    document.querySelectorAll(".qa-level-chip").forEach((btn) => {
      const on = btn.getAttribute("data-qa-age") === qaAge;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    });
    const k = document.getElementById("floor-prompts-kicker");
    if (k) k.textContent = qaKickerFor(qaAge);
    const wrap = document.querySelector(".floor-prompts-wrap");
    if (wrap) wrap.classList.toggle("is-bonus", qaAge === "bonus");
  }

  function renderDetail(trip, item, venue) {
    const missions = missionsFor(venue);
    const aState = itemState(trip, item.id);
    const showCheck = Boolean(aState.submitted);
    const evals = showCheck ? evaluateItem(trip, item, missions) : null;

    els.detailName.textContent = `${item.emoji || ""} ${item.name}`;
    els.detailBlurb.textContent = item.blurb;
    els.detailPhoto.src = item.photo;
    els.detailPhoto.alt = item.name;
    els.detailCredit.textContent = item.photoCredit || "";
    const camUrl = (item.links && item.links.cam) || "";
    const picUrl = (item.links && item.links.pictures) || "";
    const moreUrl = (item.links && item.links.more) || "";
    if (els.btnCam) {
      els.btnCam.hidden = !camUrl;
      els.btnCam.href = camUrl || "#";
      els.btnCam.textContent = "Live cam";
    }
    if (els.btnPictures) {
      els.btnPictures.hidden = !picUrl;
      els.btnPictures.href = picUrl || "#";
      els.btnPictures.textContent = "Photos";
    }
    if (els.btnMore) {
      els.btnMore.hidden = !moreUrl;
      els.btnMore.href = moreUrl || "#";
      els.btnMore.textContent =
        venue && venue.packTemplate === "exhibits" ? "Museum site" : "Learn more";
    }

    const promptsEl = document.getElementById("floor-prompts");
    if (promptsEl) {
      loadQaAge();
      syncQaAgeChips();
      const prompts = floorPromptsFor(item, venue, qaAge);
      const bonus = qaAge === "bonus";
      promptsEl.innerHTML = prompts
        .map(
          (t, i) =>
            `<div class="floor-prompt-card${bonus ? " floor-prompt-bonus" : ""}"><span class="floor-prompt-n">${
              bonus ? "★" : i + 1
            }</span><p>${escapeHtml(t)}</p></div>`
        )
        .join("");
    }
    // Pick-one is optional extra — quieter for little kids & bonus talk focus
    if (els.btnMoreQuestions) {
      els.btnMoreQuestions.hidden = qaAge === "2-3";
    }
    if (els.advancedQa && qaAge === "2-3" && els.advancedQa.open) {
      els.advancedQa.open = false;
    }

    const done = answeredCount(trip, item.id, missions);
    if (els.btnMoreQuestions) {
      const n = missions.length;
      if (showCheck) {
        els.btnMoreQuestions.textContent = "See pick-one questions ↑";
      } else if (done) {
        els.btnMoreQuestions.textContent = `Continue pick-one (${done}/${n}) ↓`;
      } else {
        els.btnMoreQuestions.textContent = "Try pick-one questions ↓";
      }
    }
    if (els.progressPill) {
      els.progressPill.hidden = !showCheck && !done;
      els.progressPill.innerHTML = showCheck
        ? `Checked <span class="stamp">✅</span>`
        : done
          ? `${done} of ${missions.length} picked`
          : "";
    }

    els.teachBanner.classList.toggle("show", aState.taught);
    if (aState.taught) {
      els.teachBanner.textContent = `⭐ Spotted ${item.name} — nice!`;
    }
    els.btnTaught.textContent = aState.taught ? "Spotted it ⭐" : "Spotted it ⭐";
    if (els.btnSubmit) els.btnSubmit.textContent = showCheck ? "Check again" : "Check my picks";

    els.missionGrid.innerHTML = "";
    missions.forEach((mission, index) => {
      const selected = new Set(aState.answers[mission.id] || []);
      const ev = evals ? evals.find((e) => e.mission.id === mission.id).result : null;
      let missionClass = "mission" + (selected.size ? " done" : "");
      if (ev) {
        if (ev.kind === "open") missionClass += " mission-open";
        else if (ev.ok) missionClass += " mission-ok";
        else missionClass += " mission-try";
      }
      const correctSet = new Set(ev ? ev.correctKey : []);
      const alwaysOk = new Set(ev ? ev.alwaysOk || [] : []);
      const wrongSet = new Set(ev ? ev.wrongPicks : []);
      const rightSet = new Set(ev ? ev.rightPicks : []);

      const choicesHtml = mission.choices
        .map((label) => {
          const on = selected.has(label);
          let extra = "";
          if (ev && mission.checkable) {
            if (on && rightSet.has(label)) extra = " is-correct-pick";
            else if (on && wrongSet.has(label)) extra = " is-wrong-pick";
            else if (!on && (correctSet.has(label) || alwaysOk.has(label))) extra = " is-correct-key";
          }
          return `<button type="button" class="choice${extra}" data-mission="${
            mission.id
          }" data-choice="${escapeAttr(label)}" aria-pressed="${on}">
            <span class="dot" aria-hidden="true"></span><span>${escapeHtml(label)}</span>
          </button>`;
        })
        .join("");

      let fbHtml = "";
      if (ev) {
        const cls = ev.kind === "open" ? "open" : ev.ok ? "ok" : "try";
        fbHtml = `<p class="mission-feedback ${cls}">${escapeHtml(ev.feedback)}</p>`;
      }

      const card = document.createElement("section");
      card.className = missionClass;
      card.dataset.color = String(index);
      card.innerHTML = `
        <div class="mission-head">
          <span class="badge">${mission.num}</span>
          <p class="mission-title">${escapeHtml(mission.title)}</p>
        </div>
        <h3 class="mission-q">${escapeHtml(mission.question)}</h3>
        <div class="choices">${choicesHtml}</div>
        ${fbHtml}`;
      card.querySelectorAll(".choice").forEach((btn) => {
        btn.addEventListener("click", () => {
          if (aState.submitted) {
            aState.submitted = false;
            saveStore();
          }
          toggleChoice(trip, item, mission, btn.dataset.choice, venue);
        });
      });
      els.missionGrid.appendChild(card);
    });
    renderResults(item, evals);
  }

  function renderResults(item, evals) {
    if (!evals) {
      els.resultsPanel.hidden = true;
      els.resultsPanel.innerHTML = "";
      return;
    }
    const checkable = evals.filter((e) => e.mission.checkable);
    const okCount = checkable.filter((e) => e.result.ok).length;
    const openOk = evals.filter((e) => !e.mission.checkable && e.result.ok).length;
    let headline =
      okCount === checkable.length
        ? `🌟 Amazing on ${item.name}!`
        : okCount > 0
          ? `🔎 Nice try on ${item.name}`
          : `🗺️ Keep exploring ${item.name}`;
    const items = evals
      .map(({ mission, result }) => {
        let mark = result.kind === "ok" ? "✅" : result.kind === "try" ? "🔄" : "⭐";
        return `<li><span class="r-title">${mark} ${escapeHtml(mission.num)}. ${escapeHtml(
          mission.title
        )}</span><span>${escapeHtml(result.feedback)}</span></li>`;
      })
      .join("");
    els.resultsPanel.hidden = false;
    els.resultsPanel.innerHTML = `<p class="results-summary">${escapeHtml(
      headline
    )}</p><p style="margin:0 0 10px;font-weight:700;color:var(--muted)">Story picks: ${openOk}</p><ul class="results-list">${items}</ul>`;
  }

  function toggleChoice(trip, item, mission, choice, venue) {
    const aState = itemState(trip, item.id);
    let list = Array.isArray(aState.answers[mission.id]) ? [...aState.answers[mission.id]] : [];
    if (mission.multi) {
      list = list.includes(choice) ? list.filter((c) => c !== choice) : [...list, choice];
    } else {
      list = list.includes(choice) ? [] : [choice];
    }
    aState.answers[mission.id] = list;
    trip.updatedAt = Date.now();
    saveStore();
    renderDetail(trip, item, venue);
  }

  function submitAnswers() {
    const trip = getTrip(currentTripId);
    const item = getItem(currentItemId);
    const venue = trip ? getVenue(trip.venueId) : null;
    if (!trip || !item || !venue) return;
    const missions = missionsFor(venue);
    if (answeredCount(trip, item.id, missions) === 0) {
      alert("Circle at least one answer first!");
      return;
    }
    itemState(trip, item.id).submitted = true;
    trip.updatedAt = Date.now();
    saveStore();
    renderDetail(trip, item, venue);
    showWinBanner(true);
  }

  function buildPrintSheet(item, trip, venue) {
    const aState = itemState(trip, item.id);
    const answers = (aState && aState.answers) || {};
    // Shared layout: big bottom photo + curated wow fact (print-kit.js)
    if (window.FPPrint && typeof window.FPPrint.fillQaPrintSheet === "function") {
      window.FPPrint.fillQaPrintSheet(item, venue, {
        answers,
        bannerNote: `${venue.name} · Mission card · Circle answers · No scores`,
        footer: "Q&amp;A card · check on screen with Submit",
      });
      return;
    }
    // Fallback if print-kit failed to load (should not happen)
    const photo =
      item.photo && !/^https?:\/\//i.test(item.photo) && !item.photo.startsWith("/")
        ? "/field-pack/" + String(item.photo).replace(/^\/+/, "")
        : item.photo || "";
    els.printSheet.innerHTML = `
      <div class="ps-page${photo ? " ps-page-with-photo" : ""}">
        <div class="ps-banner"><h1>FIELD TRIP KIT</h1>
        <p>${escapeHtml(venue.name)} · Mission card · Circle answers · No scores</p></div>
        <header class="ps-head">
          <h2>${escapeHtml(item.emoji || "")} ${escapeHtml(item.name)}</h2>
          <p class="ps-line"><strong>Explorer:</strong> <span class="write-in-line">________________</span>
          &nbsp;&nbsp; <strong>Place:</strong> ${escapeHtml(venue.name)}</p>
        </header>
        ${
          photo
            ? `<div class="ps-photo-fill"><div class="ps-photo-frame">
                <img class="ps-photo-big" src="${escapeAttr(photo)}" alt="" /></div></div>`
            : ""
        }
        <p class="ps-footer">Q&A card · check on screen with Submit</p>
      </div>`;
  }

  function printMissionCard() {
    const trip = getTrip(currentTripId);
    const item = getItem(currentItemId);
    if (!trip || !item) return;
    buildPrintSheet(item, trip, getVenue(trip.venueId));
    if (els.treasureSheet) els.treasureSheet.innerHTML = "";
    requestAnimationFrame(() => requestAnimationFrame(() => window.print()));
  }

  function buildTreasureSheet(venue, trip) {
    // Keep print content bounded so letter always stays one page
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
    const ids = (trip && trip.selectedAnimalIds) || venue.featuredAnimalIds || [];
    const stars = ids
      .slice(0, 6)
      .map((id) => {
        const it = getItem(id);
        return it ? `<span class="th-chip">${it.emoji || "•"} ${escapeHtml(it.name)}</span>` : "";
      })
      .join("");
    els.treasureSheet.innerHTML = `
      <div class="th-page">
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
        <div class="th-map">
          <p class="th-map-title">Path doodle <span class="th-map-hint">— start → favorite → end</span></p>
          <div class="th-map-box"></div>
        </div>
        <p class="th-footer">Optional after: open Field Trip Kit → tap a card → Q&A</p>
      </div>`;
  }

  function printTreasureHunt() {
    const venue = getVenue(selectedVenueId);
    const trip = getTrip(currentTripId) || ensureOuting(selectedVenueId);
    if (!venue) return;
    buildTreasureSheet(venue, trip);
    els.printSheet.innerHTML = "";
    document.body.classList.add("printing-treasure");
    // Core conversion: printable kid list + treasure hunt produced
    const track = (window.OneLessAnalytics && window.OneLessAnalytics.track) || window.trackEvent;
    if (typeof track === "function") {
      track("hunt_generated", {
        venue_slug: venue.id || selectedVenueId,
        venue_name: venue.name || "",
        product: "babys_day_out",
      });
    }
    const cleanup = () => {
      document.body.classList.remove("printing-treasure");
      window.removeEventListener("afterprint", cleanup);
    };
    window.addEventListener("afterprint", cleanup);
    requestAnimationFrame(() => requestAnimationFrame(() => window.print()));
  }

  function showWinBanner(show) {
    if (!els.winBanner) return;
    if (show) {
      els.winBanner.hidden = false;
      els.winBanner.classList.add("show");
    } else {
      els.winBanner.hidden = true;
      els.winBanner.classList.remove("show");
    }
  }

  function escapeHtml(s) {
    return String(s)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }
  function escapeAttr(s) {
    return escapeHtml(s).replaceAll("'", "&#39;");
  }

  /** Pretty SEO path when a venue page exists; else hash SPA. */
  function shareUrlForVenue(venueId, itemId) {
    const id = venueId || selectedVenueId;
    if (!id) return `${location.origin}/field-pack/`;
    if (itemId) {
      return `${location.origin}/field-pack/app.html#/venue/${encodeURIComponent(id)}/item/${encodeURIComponent(itemId)}`;
    }
    // Prefer indexable venue page for family share / paste
    return `${location.origin}/field-pack/${encodeURIComponent(id)}/`;
  }

  function setDocMeta({ title, description }) {
    if (title) document.title = title;
    if (!description) return;
    let meta = document.querySelector('meta[name="description"]');
    if (!meta) {
      meta = document.createElement("meta");
      meta.setAttribute("name", "description");
      document.head.appendChild(meta);
    }
    meta.setAttribute("content", description);
  }

  // events
  // One print path: venue mission drawer (age/time), not legacy static hunt
  els.btnTreasure.addEventListener("click", () => {
    const id = selectedVenueId || defaultVenue;
    if (!id) return;
    location.href = `/field-pack/${encodeURIComponent(id)}/#mission`;
  });
  if (els.btnSampleQa) {
    els.btnSampleQa.addEventListener("click", () => {
      const venue = getVenue(selectedVenueId);
      if (!venue) return;
      if (window.FPPrint && window.FPPrint.printSampleQaForVenue(selectedVenueId)) return;
      // Fallback: open first featured item for on-screen Q&A
      const topId =
        (venue.featuredAnimalIds && venue.featuredAnimalIds[0]) ||
        (venue.animalIds && venue.animalIds[0]);
      if (topId) {
        ensureOuting(selectedVenueId);
        showItem(currentTripId, topId);
      }
    });
  }
  els.btnShareLink.addEventListener("click", async () => {
    const url = shareUrlForVenue(selectedVenueId, currentItemId);
    try {
      await navigator.clipboard.writeText(url);
      if (els.shareLinkStatus) {
        els.shareLinkStatus.hidden = false;
        els.shareLinkStatus.textContent = "Link copied — send to family";
        setTimeout(() => {
          els.shareLinkStatus.hidden = true;
        }, 2500);
      }
    } catch {
      prompt("Copy link:", url);
    }
  });
  els.btnToggleCustomize.addEventListener("click", () => {
    const open = els.customizePanel.classList.toggle("hidden");
    // toggle returns true if now has hidden - inverted
    const isHidden = els.customizePanel.classList.contains("hidden");
    els.btnToggleCustomize.setAttribute("aria-expanded", isHidden ? "false" : "true");
    els.btnToggleCustomize.textContent = isHidden ? "Customize list ▾" : "Customize list ▴";
  });
  els.backBtn.addEventListener("click", () => showOuting(selectedVenueId));
  els.btnTaught.addEventListener("click", () => {
    const trip = getTrip(currentTripId);
    const item = getItem(currentItemId);
    if (!trip || !item) return;
    const st = itemState(trip, item.id);
    st.taught = !st.taught;
    trip.updatedAt = Date.now();
    saveStore();
    renderDetail(trip, item, getVenue(trip.venueId));
    if (st.taught) showWinBanner(true);
  });
  function openPickOneQuestions() {
    const d = els.advancedQa;
    if (!d) return;
    d.open = true;
    // Let layout paint open state, then scroll
    requestAnimationFrame(() => {
      d.scrollIntoView({ behavior: "smooth", block: "start" });
      try {
        d.querySelector("summary")?.focus({ preventScroll: true });
      } catch (_) {
        /* ignore */
      }
    });
  }
  if (els.btnMoreQuestions) {
    els.btnMoreQuestions.addEventListener("click", openPickOneQuestions);
  }

  // Q&A talk level: 2–4 / 5–8 / 9–12 / Bonus (hard animal-specific)
  loadQaAge();
  document.querySelectorAll(".qa-level-chip").forEach((btn) => {
    btn.addEventListener("click", () => {
      saveQaAge(btn.getAttribute("data-qa-age") || "4-5");
      syncQaAgeChips();
      const trip = getTrip(currentTripId);
      const item = currentItemId ? getItem(currentItemId) : null;
      const venue = trip ? getVenue(trip.venueId) : null;
      if (trip && item && venue) renderDetail(trip, item, venue);
    });
  });
  syncQaAgeChips();
  if (els.progressPill) {
    els.progressPill.style.cursor = "pointer";
    els.progressPill.title = "Open pick-one questions";
    els.progressPill.addEventListener("click", openPickOneQuestions);
  }
  els.btnPrint.addEventListener("click", printMissionCard);
  els.btnSubmit.addEventListener("click", submitAnswers);
  if (els.btnWinPrint) {
    els.btnWinPrint.addEventListener("click", () => {
      const id = selectedVenueId || defaultVenue;
      if (id) location.href = `/field-pack/${encodeURIComponent(id)}/#mission`;
    });
  }
  if (els.btnWinList) els.btnWinList.addEventListener("click", () => showOuting(selectedVenueId));

  function routeFromHash() {
    const hash = location.hash || "";
    let m;
    if ((m = hash.match(/^#\/venue\/([^/]+)\/item\/([^/]+)/))) {
      ensureOuting(m[1]);
      showItem(currentTripId, m[2]);
      return;
    }
    if ((m = hash.match(/^#\/venue\/([^/]+)/))) {
      showOuting(m[1]);
      return;
    }
    // legacy trip routes
    if ((m = hash.match(/^#\/trip\/([^/]+)\/item\/([^/]+)/))) {
      const trip = getTrip(m[1]);
      if (trip) {
        selectedVenueId = trip.venueId;
        showItem(trip.id, m[2]);
        return;
      }
    }
    if ((m = hash.match(/^#\/trip\/([^/]+)/))) {
      const trip = getTrip(m[1]);
      if (trip) {
        showOuting(trip.venueId);
        return;
      }
    }
    // no hash → home place picker
    if (!hash || hash === "#" || hash === "#/") {
      location.replace("/field-pack/");
      return;
    }
    showOuting(selectedVenueId || defaultVenue);
  }

  window.addEventListener("hashchange", routeFromHash);
  routeFromHash();
})();
