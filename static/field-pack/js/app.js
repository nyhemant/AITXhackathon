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

  /** Answers namespaced by talk level so switching 5–8 ↔ Bonus does not clash. */
  function answerSlot(missionId, level) {
    const lv = level || qaAge || "4-5";
    return lv + "::" + missionId;
  }

  function getAnswers(aState, missionId, level) {
    const slot = answerSlot(missionId, level);
    if (Array.isArray(aState.answers[slot])) return aState.answers[slot];
    // legacy un-namespaced
    if (Array.isArray(aState.answers[missionId])) return aState.answers[missionId];
    return [];
  }

  function setAnswers(aState, missionId, level, list) {
    aState.answers[answerSlot(missionId, level)] = list;
  }

  function answeredCount(trip, itemId, missions, level) {
    const a = itemState(trip, itemId);
    const lv = level || qaAge || "4-5";
    return missions.filter((m) => getAnswers(a, m.id, lv).length > 0).length;
  }

  function talkLevelLabel(age) {
    if (age === "2-3") return "Ages 2–4";
    if (age === "6-8") return "Ages 9–12";
    if (age === "bonus") return "Bonus";
    if (age === "alpha") return "Alpha";
    return "Ages 5–8";
  }

  function stripPromptPrefix(text) {
    return String(text || "")
      .replace(/^ALPHA · /i, "")
      .replace(/^★\s*/u, "")
      .trim();
  }

  /**
   * One talk pack drives floor prompts + pick-ones + print card.
   * age: 2-3 | 4-5 | 6-8 | bonus | alpha
   */
  function talkPackFor(item, venue, age) {
    const band = QA_AGE_ORDER.includes(age) ? age : "4-5";
    const prompts = floorPromptsFor(item, venue, band).slice(0, 6);
    while (prompts.length < 6) {
      prompts.push(padPromptLine(item, venue, band, prompts.length));
    }
    const label = talkLevelLabel(band);
    const kicker = qaKickerFor(band);
    const base = missionsFor(venue) || [];
    const byId = Object.fromEntries(base.map((m) => [m.id, m]));
    const clone = (m, patch) => Object.assign({}, m, patch || {});
    const rewriteQ = {
      food: {
        "4-5": "What do they eat?",
        "6-8": "What clues show what they eat?",
      },
      home: {
        "4-5": "Where is home?",
        "6-8": "What habitat clues do you see here?",
      },
      superpower: {
        "4-5": "What is their superpower?",
        "6-8": "What body tool is working hardest right now?",
      },
      grow: {
        "4-5": "Baby or grown-up?",
        "6-8": "Baby, young, or grown — and how can you tell?",
      },
      cam: {
        "4-5": "Did we see one live?",
        "6-8": "Live here, on a cam, or not today — what is true?",
      },
      teach: {
        "4-5": "I want to teach about…",
        "6-8": "What would you teach a friend in one sentence?",
      },
      try: {
        "4-5": "What did I do here?",
        "6-8": "What did you actually do at this stop?",
      },
      body: {
        "4-5": "How did I move?",
        "6-8": "How did your body work here?",
      },
      senses: {
        "4-5": "What did I notice?",
        "6-8": "Which sense told you the most?",
      },
      feel: {
        "4-5": "How did it feel?",
        "6-8": "What feeling stuck with you — and why?",
      },
      again: {
        "4-5": "Would I do this again?",
        "6-8": "Would you come back — favorite, once more, or skip?",
      },
    };

    let missions = [];
    if (band === "bonus" || band === "alpha") {
      const tag = band === "alpha" ? "Alpha" : "Bonus";
      const choices =
        band === "alpha"
          ? ["I noticed something real", "Still watching", "Told a grown-up", "Want another look"]
          : ["I spotted it", "Not sure yet", "Told a grown-up", "Want to try later"];
      missions = prompts.slice(0, 6).map((text, i) => ({
        id: band + "_q" + (i + 1),
        num: String(i + 1),
        title: tag + " " + (i + 1),
        question: stripPromptPrefix(text),
        choices,
        multi: false,
        checkable: false,
        openNote: "Your observation counts — not a test!",
        talkLevel: band,
      }));
    } else if (band === "2-3") {
      const littleMeta = [
        { id: "little_look", title: "Look", choices: ["Big", "Small", "Moving", "Still", "A color", "Not sure"] },
        { id: "little_move", title: "Move", choices: ["Moving", "Still", "I copied it", "Too far to see"] },
        { id: "little_say", title: "Say", choices: ["A color", "A sound", "A feeling", "Told a grown-up"] },
        { id: "little_touch", title: "Soft", choices: ["Looks soft", "Looks rough", "Looks wet", "Not sure"] },
        { id: "little_friend", title: "Friend", choices: ["I like it", "A little scary", "Funny", "Quiet"] },
        { id: "little_again", title: "Again", choices: ["See again!", "Maybe later", "All done", "Photo time"] },
      ];
      missions = littleMeta.map((meta, i) => ({
        id: meta.id,
        num: String(i + 1),
        title: meta.title,
        question: stripPromptPrefix(prompts[i] || meta.title + "?"),
        choices: meta.choices,
        multi: true,
        checkable: false,
        openNote: "Pointing and talking both count!",
        talkLevel: band,
      }));
    } else {
      // 4-5 and 6-8: full catalog set (6 missions)
      const animalOrder = ["food", "home", "superpower", "grow", "cam", "teach"];
      const exhibitOrder = ["try", "body", "senses", "feel", "again", "teach"];
      const order =
        venue && venue.packTemplate === "exhibits" ? exhibitOrder : animalOrder;
      const picked = [];
      for (const id of order) {
        if (byId[id]) picked.push(byId[id]);
      }
      // fill any missing slots from remaining base
      for (const m of base) {
        if (picked.length >= 6) break;
        if (!picked.some((x) => x.id === m.id)) picked.push(m);
      }
      if (!picked.length) picked.push(...base.slice(0, 6));
      missions = picked.slice(0, 6).map((m, i) => {
        const qmap = rewriteQ[m.id];
        const q = (qmap && qmap[band]) || m.question;
        return clone(m, { num: String(i + 1), question: q, talkLevel: band });
      });
    }

    missions = missions.slice(0, 6);
    // Single stream: prompts mirror mission questions (print + any leftover callers)
    const missionPrompts = missions.map((m) => m.question || "");
    return {
      level: band,
      label,
      kicker,
      prompts: missionPrompts,
      missions,
    };
  }

  function padPromptLine(item, venue, band, index) {
    const name = (item && item.name) || "this stop";
    const place = (venue && (venue.shortName || venue.name)) || "here";
    const extras = {
      "2-3": [
        `Can you find the eyes on the ${name}?`,
        `Is the ${name} alone or with friends?`,
        `Would you say hi soft or loud?`,
      ],
      "4-5": [
        `What is one thing the ${name} is doing right now?`,
        `What would you tell a friend about ${name}?`,
        `Find something big and something small near ${name}.`,
      ],
      "6-8": [
        `What problem does ${name} solve with its body or design?`,
        `Compare two details — which surprised you more?`,
        `If you only had one photo at ${place}, what would you capture?`,
      ],
      bonus: [
        `What’s a detail most visitors miss at ${name}?`,
        `If ${name} could change one thing about this habitat, what?`,
        `Teach a grown-up one true thing you just proved with your eyes.`,
      ],
      alpha: [
        `ALPHA · 20s watch: write one measurement word (fast, slow, high, low…).`,
        `ALPHA · Counterfactual: what if ${name} were nocturnal — what changes?`,
        `ALPHA · One-sentence field note you’d put in a scientist’s notebook.`,
      ],
    };
    const list = extras[band] || extras["4-5"];
    return list[index % list.length];
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

    function evaluateItem(trip, item, missions, level) {
    const aState = itemState(trip, item.id);
    const lv = level || qaAge || "4-5";
    return missions.map((mission) => ({
      mission,
      result: evaluateMission(item, mission, getAnswers(aState, mission.id, lv)),
    }));
  }

  /** Q&A talk levels (not the same as mission "Adults" sheet). */
  const QA_AGE_KEY = "1less-qa-talk-level";
  const QA_AGE_ORDER = ["2-3", "4-5", "6-8", "bonus", "alpha"];
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

  function normCatalogKey(raw) {
    return String(raw || "")
      .toLowerCase()
      .replace(/_/g, "-")
      .replace(/\s+/g, "-");
  }

  /** Hard wow facts → bonus questions (animal-specific when we can). */
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
    tiger: [
      "No two tigers have the same stripe pattern. Sketch one stripe set in your mind.",
      "White or orange coat: which would hide better in snow vs forest?",
      "Tigers are mostly solo. What would change if they lived in a pride like lions?",
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
    orangutan: [
      "Orangutans are mostly solitary tree travelers. Why live high instead of on the ground?",
      "Long arms are climbing tools. Time 15s — hands or feet doing more work?",
      "Fruit brains: what’s one smart move you notice (look, reach, tool-like hold)?",
    ],
    "african-penguin": [
      "They “fly” underwater with wing-like flippers. Compare swimming vs walking.",
      "A layer of air under the feathers helps insulation. Why stay dry under the feathers?",
      "Colony noise is part of finding mates and chicks. What sounds do you hear?",
    ],
    "nile-hippo": [
      "Hippos look slow on land but can charge fast. Are they mostly water or bank right now?",
      "Eyes, ears, and nostrils sit high so they can breathe while almost sunk. Spot that lineup.",
      "They make dung showers to mark territory. Gross but useful — what else marks space here?",
    ],
    cheetah: [
      "Fastest land mammal — but only in short bursts. Why not sprint all day?",
      "Semi-retractable claws grip like cleats. Look at the feet if you can.",
      "A still cheetah is still hunting practice. Statue or stretch — call it after 20 quiet seconds.",
    ],
    "caribbean-flamingo": [
      "Pink comes from food pigments (not paint). What color would *you* turn on a shrimp diet joke?",
      "One-leg standing may save heat. Count how many are on one leg (best guess).",
      "That weird bent “knee” is really an ankle. Trace the leg joints with your eyes.",
    ],
    "galapagos-tortoise": [
      "Giant tortoises can live longer than most humans. What would you do with 100 slow years?",
      "Shells are living bone covered in scutes. Tap? No — just look: high dome or saddle shape?",
      "Patience prize: wait for one step, or admit statue after 30 seconds.",
    ],
    "asian-small-clawed-otter": [
      "Smallest otter species — huge hand energy. Count finger-like toes if paws are visible.",
      "They use tools and teamwork in the wild. Spot a splash, roll, or pass-the-food moment.",
      "Dense fur traps air for warmth. Why stay dry under the wet look?",
    ],
    "ring-tailed-lemur": [
      "Ringed tails are flags for the troop. How many black/white rings can you estimate?",
      "Sun-worship pose: belly out, arms open. Anyone soaking sun?",
      "Female-led groups are common. Who moves first when the group shifts?",
    ],
    "two-toed-sloth": [
      "Sloths move so slow algae can grow in their fur. Spot green tint?",
      "They come down to poop about once a week — risky! Why risk the ground?",
      "Upside-down life: what would be hard if *you* hung like that for an hour?",
    ],
    zebra: [
      "Every zebra’s stripe map is unique. Find a wide stripe vs a thin one on the same animal.",
      "Stripes may confuse biting flies and predators. Stand back — do stripes blur together?",
      "Herd math: is this a tight group or a loner right now?",
    ],
    "red-panda": [
      "Not a giant panda — closer to raccoons in the family tree. What looks “cat-like” vs “bear-like”?",
      "They use a wrist bone like a thumb to climb. Watch the front paws on branches.",
      "Mostly crepuscular (dawn/dusk). Why might heat or crowds change when you see them?",
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
    wolf: [
      "Wolves talk with ears, tails, and posture — not just howls. Read one body cue.",
      "Pack hunting needs teamwork. Who looks like leader energy right now?",
      "Quiet 20 seconds: any soft whine, huff, or stillness that feels “packed”?",
    ],
    "black-bear": [
      "Bears are omnivores with a great nose. What would you smell-hunt first here?",
      "Climbing claws vs walking paws — what are the feet doing?",
      "Winter slowdown is not always true hibernation. Does this one look sleepy or busy?",
    ],
    alligator: [
      "Eyes and nostrils on top = ambush snorkel. How much of the body is under?",
      "Cold-blooded: sunny bank vs cool water — which did they pick?",
      "Powerful tail, short legs. How would *you* swim with that body plan?",
    ],
    peacock: [
      "Train feathers are mostly show — not great for flying far. Why keep such a heavy billboard?",
      "Eyespots may startle predators or impress mates. Count a few if the train is open.",
      "Free-roamers choose people paths. Why hang near visitors (food? shade? curiosity)?",
    ],
    capybara: [
      "World’s largest rodent — semi-aquatic. Wet fur or dry sun pose?",
      "They get along with many species in the wild. Who else shares this space?",
      "Webbed feet help swim. Spot a paddle move if they enter water.",
    ],
    shark: [
      "Many sharks never stop swimming — water must move over gills. Is this one cruising or resting?",
      "A sandpapery skin of tiny teeth (denticles) cuts drag. Why smooth vs rough matter?",
      "Senses include smell and tiny electrical cues. What would *you* sense in dark water?",
    ],
    stingray: [
      "Wing-flaps are modified fins. Flap or glide — name the motion.",
      "Mouth and gills are on the underside. How do they eat without seeing the plate?",
      "Buried in sand = camouflage. Spot any outline that almost disappears.",
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
    seahorse: [
      "Upright swimming + a prehensile tail. Anchored or drifting right now?",
      "Males carry the eggs in a pouch. Why might dad-pregnancy help survival?",
      "Tiny snout = vacuum straw. What size prey fits that tool?",
    ],
    eel: [
      "Long body = hiding in holes. Head out or fully tucked?",
      "Some eels make shocking voltage; many don’t. What’s the “weapon” you *can* see (teeth, speed)?",
      "Sidewinding swim. Count one full body wave if it moves.",
    ],
    "sci-dinosaur": [
      "Birds are living dinosaurs. What on a bird is a dino clue?",
      "Teeth and hips tell diet and stance. What would *your* fossil say about you?",
      "Size fools us in museums. What looks bigger up close than you expected?",
    ],
    "sci-planet": [
      "Scale lies: models shrink solar systems. What would crush the room if Earth were this size?",
      "Find one number (distance, temperature, years) that surprises you.",
      "If you could visit one world on this floor, which — and why not the flashiest?",
    ],
    "sci-hands-on": [
      "What variable did you change (speed, angle, weight) — and what stayed the same?",
      "Explain the result in one sentence a tired grown-up would remember.",
      "Find a control or “fair test” idea hiding in this exhibit.",
    ],
    "sci-rocket": [
      "Rockets shed weight as they climb. What would *you* drop first to go farther?",
      "Thrust vs gravity: which force is winning in the story of this craft?",
      "Find a human-scale clue (seat, hatch, footprint) that makes space feel real.",
    ],
  };

  /**
   * Alpha = extra-hard cool talk: patience timers, multi-step notice, deeper why.
   * Harder than Bonus; still floor-safe (no trivia exam).
   */
  const ALPHA_WOW = {
    "african-elephant": [
      "ALPHA · Trunk job audit: 30 silent seconds — tool, snorkel, sniffer, or rest? Write one verb.",
      "ALPHA · Footquake: elephants detect rumbles through fat pads in their feet. Where would *you* stand to “hear” a far herd?",
      "ALPHA · Matriarch logic: if elders remember water holes, what memory would save *your* family on a hot trip?",
    ],
    "reticulated-giraffe": [
      "ALPHA · Blood pressure puzzle: a giraffe’s heart fights gravity to the brain. Why don’t they faint every time they lift their head?",
      "ALPHA · Tongue spy: dark tongue = sunscreen hypothesis. Confirm tongue color if it feeds — or note “off duty.”",
      "ALPHA · Ossicone check: horn-like nubs are covered in skin. Count ossicones you can see (best guess).",
    ],
    "african-lion": [
      "ALPHA · Energy budget: lions rest most of the day. After 30s quiet watch — nap, scan, or social groom?",
      "ALPHA · Mane tradeoff: thick mane = heat + intimidation. Would *you* take the heat for the look?",
      "ALPHA · Ambush math: short chase, not marathon. Point to body parts built for burst, not distance.",
    ],
    "sumatran-tiger": [
      "ALPHA · Stripe fingerprint: memorize 3 stripe “forks,” look away 10s, look back — still the same tiger?",
      "ALPHA · Solo vs pride: invent one hunting problem a solo tiger faces that lions solve with teamwork.",
      "ALPHA · Vertical space: tigers swim and climb more than people think. Water, height, or ground preference here?",
    ],
    tiger: [
      "ALPHA · Coat story: white/orange is genetics + rarity, not a separate species magic. What *does* change with coat color?",
      "ALPHA · 30s silence: pacing loop, stare, or out of view — call it with evidence.",
      "ALPHA · Soft paws, hard end: retractable claws. When would claws stay in vs out?",
    ],
    "western-lowland-gorilla": [
      "ALPHA · Silverback read: age signal in the back hair. Who looks like decision-maker energy?",
      "ALPHA · Hands story: 20s — knuckle-walk, forage, or social touch? One verb only.",
      "ALPHA · Folivore life: huge gut for leaves. Why chew a lot for “low-quality” food?",
    ],
    chimpanzee: [
      "ALPHA · Theory of mind lite: does anyone watch another chimp before acting?",
      "ALPHA · Tool culture: wild chimps crack nuts and fish termites. Design a tool from things you see *outside* the habitat.",
      "ALPHA · Face → feeling: name an emotion, then point to the face clue that sold you.",
    ],
    orangutan: [
      "ALPHA · Canopy IQ: long arms + slow care. Time a single reach — rushed or planned?",
      "ALPHA · Nest engineers: wild orangutans build day/night nests. Rate this habitat’s “nest materials” 1–10.",
      "ALPHA · Loners with depth: why might smart animals still avoid big groups?",
    ],
    "african-penguin": [
      "ALPHA · Countershade: dark back / light belly. From above and below in water — who gets fooled?",
      "ALPHA · Porpoising: leap-breathe while swimming. Catch one surface breath cycle.",
      "ALPHA · Colony code: bray calls help find partners. Softest vs loudest sound in 15s?",
    ],
    "nile-hippo": [
      "ALPHA · Underwater window test: is a hippo fully in frame, partial, or ghost? Mark yes/partial/no.",
      "ALPHA · Semi-aquatic trap: heavy on land, graceful in water. Which medium are they built for *today*?",
      "ALPHA · Territory chemistry: dung-marking is real. What human “marks” do we leave without thinking?",
    ],
    cheetah: [
      "ALPHA · Sprint physics: huge nostrils + tail rudder. Point to two speed tools you can see.",
      "ALPHA · 30-second statue score (1–10 stillness). Cheetahs win by patience too.",
      "ALPHA · Semi-retractable claws = permanent cleats. Tradeoff vs a house cat’s full retract?",
    ],
    "caribbean-flamingo": [
      "ALPHA · Filter feeding: upside-down bill comb. If they eat, watch the head wiggle pattern.",
      "ALPHA · One-leg thermodynamics: estimate % of flock on one leg without double-counting.",
      "ALPHA · Knees that aren’t: the bend you see is ankle. Trace hip → ankle → toes with a finger in the air.",
    ],
    "galapagos-tortoise": [
      "ALPHA · Deep time: some individuals outlive nations. What habit is worth a century of slow?",
      "ALPHA · Shell engineering: dome vs saddle-back shapes fit different islands/food heights. Which shape here?",
      "ALPHA · Step challenge: full 45s — any step? If not, what *did* move (eye, head, breath)?",
    ],
    "asian-small-clawed-otter": [
      "ALPHA · Dexterity lab: 20s — food handle, water play, or social wrestle?",
      "ALPHA · Whisker map: vibrissae read currents. Why “feel” water instead of only seeing?",
      "ALPHA · Waterproofing: air in fur. After a dive, do they look slick or fluffy-dry?",
    ],
    "ring-tailed-lemur": [
      "ALPHA · Stink fights are real (male wrist scent). Invent a polite human version of a stink fight.",
      "ALPHA · Tail semaphore: raised tail while walking = follow-me flag. Catch a raised-tail move.",
      "ALPHA · Sun ritual: belly-to-sun pose. Thermoregulation or just vibes? Defend your call.",
    ],
    "two-toed-sloth": [
      "ALPHA · Metabolic minimalism: slow = survive on leaves. What would you cut from *your* day to save energy?",
      "ALPHA · Algae camouflage: green tint is ecosystem on fur. Camouflage or just damp?",
      "ALPHA · Motion lottery: 30s — any limb move? Record yes/no like a scientist.",
    ],
    zebra: [
      "ALPHA · Motion dazzle: do stripes make distance harder to judge when they walk? Step back and test.",
      "ALPHA · Stripe width map: shoulder vs rump — which is busier?",
      "ALPHA · Fly hypothesis: stripes may cut tsetse landings. Why might bugs hate high-contrast edges?",
    ],
    "red-panda": [
      "ALPHA · False thumb: radial sesamoid bone. Watch a grip — thumb-like or not?",
      "ALPHA · Bamboo cousin energy without being a bear. List 2 traits that fooled the name “panda.”",
      "ALPHA · Arboreal escape: height vs speed. If startled, up or out?",
    ],
    "giant-panda": [
      "ALPHA · Gut vs diet mismatch: carnivore-ish gut on bamboo. Why chew forever?",
      "ALPHA · Pseudo-thumb mechanics: pause on a grip and describe the hold in 5 words.",
      "ALPHA · Conservation icon: what one habitat need (bamboo, quiet, space) would you fund first?",
    ],
    koala: [
      "ALPHA · Toxic leaf specialist: liver works overtime. Why not switch to easier food?",
      "ALPHA · Sleep budget: up to ~18–20h. Is “lazy” fair — or efficient?",
      "ALPHA · Pouch down: joey climbs up into a downward pouch. Engineering win or weird?",
    ],
    wolf: [
      "ALPHA · Rank is fluid, not cartoon. After 30s, who yields space to whom?",
      "ALPHA · Endurance hunters: long chase strategy. What body clue says “marathon,” not “cheetah”?",
      "ALPHA · Howl purpose: assemble, advertise, bond. If they howled now, which job fits the scene?",
    ],
    "black-bear": [
      "ALPHA · Nose first: smell >> sight for bears. Design a “scent map” of this habitat in 3 zones.",
      "ALPHA · Plantigrade feet (flat). Compare to a dog’s digitigrade tip-toe run.",
      "ALPHA · Omnivore menu: invent today’s buffet from what you see in the yard.",
    ],
    alligator: [
      "ALPHA · Sit-and-wait predator: energy cheap until strike. Still water or micro-move?",
      "ALPHA · Temperature choice: sun bake vs shade soak — pick their thermostat setting.",
      "ALPHA · Parental care surprise: gators guard nests/young. What would “good parent” look like here?",
    ],
    peacock: [
      "ALPHA · Honest signal debate: huge train = healthy genes *or* just hard to escape predators. Pick a side.",
      "ALPHA · Iridescence: color from structure, not only pigment. Tilt your view — does color shift?",
      "ALPHA · Ground risk: flashy + flight-limited. Why didn’t evolution “fix” that?",
    ],
    capybara: [
      "ALPHA · Semi-aquatic rodent: eyes/ears/nose high like a hippo lite. Spot the snorkel line.",
      "ALPHA · Social calm: capybaras famously chill with other species. Who’s sharing space?",
      "ALPHA · Grazers with swims: land food + water escape. Which need seems primary today?",
    ],
    shark: [
      "ALPHA · Ram ventilation vs buccal pump: must-swim vs can-rest species differ. Cruising nonstop here?",
      "ALPHA · Ampullae of Lorenzini: sense tiny electric fields. What “hidden” prey cue is that?",
      "ALPHA · Pass count: how many full crossings of your window in 30s?",
    ],
    stingray: [
      "ALPHA · Spiracles: some breathe through holes behind the eyes when buried. Find eye line + bury clues.",
      "ALPHA · Undulation vs oscillation: wave along the whole fin or flap like wings?",
      "ALPHA · Bottom hunter: what would you taste/feel in sand if you were a ray?",
    ],
    octopus: [
      "ALPHA · Distributed brain: more neurons in arms than central brain. Does an arm explore “on its own”?",
      "ALPHA · Beak is the only hard part. Estimate the smallest square hole it could escape through.",
      "ALPHA · Camouflage score 1–10 after 20s — and name the background it matched.",
    ],
    jellyfish: [
      "ALPHA · Nerve net democracy: no brain, still pulsing. Count 10 pulses and note even vs uneven rhythm.",
      "ALPHA · Mesoglea: jelly mass is support + buoyancy. Why not need bones?",
      "ALPHA · Sting ecology: nematocysts fire on touch. Why is “look don’t poke” science, not just manners?",
    ],
    "sea-turtle": [
      "ALPHA · Magnetic natal homing: hatchlings encode beach fields. What human “home beacon” is closest?",
      "ALPHA · Shell tradeoff: armor vs dive agility. Lightweight feel or tank?",
      "ALPHA · Light pollution problem: hatchlings crawl toward glow. Invent a beach fix in one sentence.",
    ],
    seahorse: [
      "ALPHA · Male pregnancy: brood pouch oxygen + salt control. Why might that raise survival?",
      "ALPHA · Anchor tail: prehensile hold on seagrass. Anchored point + body sway?",
      "ALPHA · Independent eye turret: each eye can track differently. Catch a weird eye split?",
    ],
    eel: [
      "ALPHA · Elongate hydrodynamics: whole-body wave. Trace one wave from head to tip.",
      "ALPHA · Crevice niche: ambush from holes. What’s the best hide geometry here?",
      "ALPHA · Mucus + smooth skin: different from scaled fish. Advantage in tight rocks?",
    ],
    "sci-dinosaur": [
      "ALPHA · Phylogeny punchline: birds ⊂ dinosaurs. Find one trait that survives in a pigeon.",
      "ALPHA · Allometry: big animals need thicker legs. Which bone looks “overbuilt”?",
      "ALPHA · Trace vs body fossil: which would prove behavior better — trackway or skull?",
    ],
    "sci-planet": [
      "ALPHA · Order-of-magnitude: pick two distances and say which is ~10× or ~100× the other.",
      "ALPHA · Selection effect: pretty images ≠ common worlds. What’s likely ugly but important?",
      "ALPHA · Energy story: sunlight vs internal heat — which powers the thing you’re viewing?",
    ],
    "sci-hands-on": [
      "ALPHA · Isolate variables: change only one thing twice. What broke when you changed two?",
      "ALPHA · Error bars of life: redo once — same result? Why might it differ?",
      "ALPHA · Teach-back: 15-second explanation with no jargon allowed.",
    ],
    "sci-rocket": [
      "ALPHA · Tsiolkovsky intuition: more fuel helps, but tank mass hurts. What’s the cruel trade?",
      "ALPHA · Staging: why drop empty cans instead of hauling them to orbit?",
      "ALPHA · Human system: life support is cargo. Point to one crew-need this craft must solve.",
    ],
  };

  function itemTags(item) {
    return new Set((item && item.tags) || []);
  }

  function itemCatalogId(item) {
    return normCatalogKey((item && (item.catalog_id || item.id)) || "");
  }

  function lookupPromptBank(bank, item) {
    const id = itemCatalogId(item);
    if (bank[id]) return bank[id];
    const bare = id.replace(/^w-/, "");
    if (bank[bare]) return bank[bare];
    // soft aliases
    const aliases = {
      elephant: "african-elephant",
      giraffe: "reticulated-giraffe",
      lion: "african-lion",
      gorilla: "western-lowland-gorilla",
      hippo: "nile-hippo",
      penguin: "african-penguin",
      flamingo: "caribbean-flamingo",
      tortoise: "galapagos-tortoise",
      otter: "asian-small-clawed-otter",
      lemur: "ring-tailed-lemur",
      sloth: "two-toed-sloth",
      "sea-star": "starfish",
      jelly: "jellyfish",
      panda: "giant-panda",
    };
    for (const [k, v] of Object.entries(aliases)) {
      if (id.includes(k) && bank[v]) return bank[v];
    }
    const name = String((item && item.name) || "").toLowerCase();
    for (const [k, v] of Object.entries(aliases)) {
      if (name.includes(k.replace(/-/g, " ")) && bank[v]) return bank[v];
    }
    return null;
  }

  function finishSixPrompts(list, item, venue, band) {
    const out = (list || []).slice(0, 6);
    let i = out.length;
    while (out.length < 6) {
      out.push(padPromptLine(item, venue, band, i));
      i += 1;
    }
    return out;
  }

  function bonusPromptsFor(item, venue) {
    const name = item.name || "this stop";
    const tags = itemTags(item);
    const place = (venue && (venue.shortName || venue.name)) || "here";
    const bank = lookupPromptBank(BONUS_WOW, item);
    let list = bank && bank.length ? bank.slice() : null;

    if (!list) {
      if (tags.has("big-cats") || /lion|tiger|cheetah|leopard/i.test(name)) {
        list = [
          `Big cats hide in plain sight. Where would ${name} vanish in wild cover?`,
          "Quiet feet + sharp eyes: which body part is the real hunting tool?",
          `If you only had 60 seconds at ${place}, what one detail would you photograph?`,
          `Watch 15 seconds — is ${name} hunting-energy, rest-energy, or social-energy?`,
          "Find a camouflage clue: stripes, spots, stillness, or shadow.",
          `What would you put on a warning sign for animals that meet ${name}?`,
        ];
      } else if (tags.has("water") || isAquariumVenue(venue)) {
        list = [
          `Water is thicker than air. How does ${name} move differently than a land animal?`,
          "Find one adaptation for breathing, steering, or staying hidden.",
          "What’s the quietest thing happening in this tank right now?",
          "Count a pass or pulse — how many in about 15 seconds (best guess)?",
          "Where is the best hidey spot in this tank or pool?",
          `If you were ${name} for a day, what would annoy you about visitors?`,
        ];
      } else if (isMuseumVenue(venue) || tags.has("read") || tags.has("hands")) {
        list = [
          `What’s the one design choice at “${name}” that makes kids stop walking?`,
          "If you had to explain this stop in one sentence to a friend, what would you say?",
          "Find a detail most visitors walk past — label, texture, or hidden model.",
          "What did your hands or body do here (or wish they could)?",
          "What question is this exhibit trying to answer?",
          "What would you add to make this stop even clearer for a tired grown-up?",
        ];
      } else {
        list = [
          `What’s the strangest true thing you can spot about ${name} in 30 seconds?`,
          "If this animal (or exhibit) could talk, what would it complain about today?",
          `Why is ${name} a highlight of ${place} — not just “another stop”?`,
          `What is ${name} doing with its body right now?`,
          "Find something tiny near something huge.",
          "Teach a grown-up one fact you didn’t know before today.",
        ];
      }
    }
    return finishSixPrompts(list, item, venue, "bonus");
  }

  function alphaPromptsFor(item, venue) {
    const name = item.name || "this stop";
    const tags = itemTags(item);
    const place = (venue && (venue.shortName || venue.name)) || "here";
    const bank = lookupPromptBank(ALPHA_WOW, item);
    let list = bank && bank.length ? bank.slice() : null;

    if (!list) {
      if (tags.has("big-cats") || /lion|tiger|cheetah|leopard/i.test(name)) {
        list = [
          `ALPHA · 30 silent seconds on ${name}: one verb only for what happened.`,
          "ALPHA · Ambush vs stamina: which body clues say “burst,” not “marathon”?",
          `ALPHA · Camouflage design: where in wild cover would ${name} disappear first?`,
          "ALPHA · Ear/eye check: alert, half-rest, or full nap — evidence?",
          "ALPHA · Soft pad vs hard claw: when would each matter more?",
          `ALPHA · Field note: one sentence a zookeeper might write about ${name} today.`,
        ];
      } else if (tags.has("water") || isAquariumVenue(venue)) {
        list = [
          `ALPHA · Hydrodynamics: name two body parts that cut drag or steer for ${name}.`,
          "ALPHA · 20s stillness test: what moved first — animal, water, or reflection?",
          "ALPHA · Sensory swap: if you lost sight, what non-eye sense would save you here?",
          "ALPHA · Pass/pulse count in 30s (best estimate) — write the number.",
          "ALPHA · Best hide score 1–10 and name the background it matches.",
          "ALPHA · Teach-back in 12 words: how this body works in water.",
        ];
      } else if (isMuseumVenue(venue) || tags.has("read") || tags.has("hands")) {
        list = [
          `ALPHA · Mechanism: what invisible force or idea is “${name}” really about?`,
          "ALPHA · Fair test: what would you change twice to check the result isn’t luck?",
          "ALPHA · Overlook: find a label or texture most visitors skip — read it aloud softly.",
          "ALPHA · Variable hunt: what can you change vs what stays fixed?",
          "ALPHA · Scale check: what is bigger or smaller than you expected?",
          "ALPHA · Explain it to a 6-year-old in one breath.",
        ];
      } else {
        list = [
          `ALPHA · 30s scientist mode on ${name}: write one careful observation (not a feeling).`,
          `ALPHA · Counterfactual: if ${name} vanished from ${place}, what story would be missing?`,
          "ALPHA · Teach-back: explain this stop in 12 words or fewer to a grown-up.",
          "ALPHA · Pattern or texture match: find two similar details in different places.",
          "ALPHA · Energy budget: rest, move, or social — which wins this minute?",
          "ALPHA · One question you’d ask a keeper (write it even if you don’t ask).",
        ];
      }
    }
    return finishSixPrompts(list, item, venue, "alpha");
  }

  function floorPromptsFor(item, venue, age) {
    const name = item.name || "it";
    const band = QA_AGE_ORDER.includes(age) ? age : "4-5";
    const museum = isMuseumVenue(venue);
    const key = item.key || {};
    const food = (key.food && key.food[0]) || "";
    const home = (key.home && key.home[0]) || "";
    const power = (key.superpower && key.superpower[0]) || "";

    if (band === "alpha") return alphaPromptsFor(item, venue);
    if (band === "bonus") return bonusPromptsFor(item, venue);

    if (band === "2-3") {
      if (museum) {
        return finishSixPrompts(
          [
            `Point to something at ${name}. Big or small?`,
            "Can you copy a move — climb, reach, or tiptoe?",
            "Make a sound or a quiet face for what you saw.",
            "What color jumps out first?",
            "Is it loud here or quiet?",
            "Show me your favorite part with a point.",
          ],
          item,
          venue,
          band
        );
      }
      return finishSixPrompts(
        [
          `Find the ${name}. Wave or point!`,
          "Is it moving or still? Show me with your body.",
          "What color do you see first?",
          "Can you find the eyes? The nose? The feet?",
          "Is it alone or with friends?",
          "Would you say hi soft or loud?",
        ],
        item,
        venue,
        band
      );
    }

    if (band === "6-8") {
      if (museum) {
        return finishSixPrompts(
          [
            `What problem does “${name}” help you understand?`,
            "Compare two parts of this stop — which surprised you more?",
            "Teach a friend one fact you’d actually remember tomorrow.",
            "What would you change to make this clearer?",
            "What did your hands or eyes do that felt scientific?",
            "One sentence: why does this stop matter?",
          ],
          item,
          venue,
          band
        );
      }
      return finishSixPrompts(
        [
          `How is ${name} built for its job${power ? ` (think: ${power})` : ""}?`,
          food ? `What clue says it might eat like “${food}”?` : `What would ${name} eat — and how can you tell?`,
          home ? `Home is like “${home}”. What here matches that habitat?` : `Where would ${name} hide or rest in the wild?`,
          `Watch 20 seconds — what is ${name} doing with its body?`,
          "Find two different textures or patterns nearby.",
          "What would you put on a kid label that isn’t here yet?",
        ],
        item,
        venue,
        band
      );
    }

    // 4-5 kids (default)
    if (museum) {
      return finishSixPrompts(
        [
          `What did you try or notice at ${name}?`,
          "How did your body move — climb, hands, quiet look?",
          "Tell a grown-up one thing you discovered.",
          "What color or sound stands out?",
          "Was anything tricky or surprising?",
          "Would you do this stop again — yes, maybe, or later?",
        ],
        item,
        venue,
        band
      );
    }
    return finishSixPrompts(
      [
        `What do you notice about the ${name}?`,
        "How does it move — or stay still?",
        food ? `What might it eat? (Hint family: ${food})` : "What might it eat?",
        home ? `Does this place feel like “${home}”?` : "Where might it sleep or hide?",
        "What is one color you see on its body?",
        "Tell a grown-up your favorite thing about it.",
      ],
      item,
      venue,
      band
    );
  }

  function qaKickerFor(age) {
    if (age === "alpha") return "Alpha · extra-hard cool questions";
    if (age === "bonus") return "Bonus · hard wow questions";
    if (age === "2-3") return "Little kids · notice & play";
    if (age === "6-8") return "Big kids · think & compare";
    return "Notice & talk";
  }

  function syncQaAgeChips() {
    document.querySelectorAll(".qa-level-chip").forEach((btn) => {
      if (!btn.hasAttribute("data-qa-age")) return;
      const on = btn.getAttribute("data-qa-age") === qaAge;
      if (on) btn.classList.add("is-active");
      else btn.classList.remove("is-active");
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    });
    const k = document.getElementById("floor-prompts-kicker");
    if (k) k.textContent = qaKickerFor(qaAge);
    const wrap =
      document.getElementById("qa-level-wrap") || document.querySelector(".floor-prompts-wrap");
    if (wrap) {
      wrap.classList.toggle("is-bonus", qaAge === "bonus");
      wrap.classList.toggle("is-alpha", qaAge === "alpha");
    }
  }

  function renderDetail(trip, item, venue) {
    loadQaAge();
    const pack = talkPackFor(item, venue, qaAge);
    const missions = pack.missions;
    const aState = itemState(trip, item.id);
    const showCheck = Boolean(aState.submitted);
    const evals = showCheck ? evaluateItem(trip, item, missions, qaAge) : null;

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

    syncQaAgeChips();
    const levelHint = document.getElementById("talk-level-hint");
    if (levelHint) {
      levelHint.textContent =
        "Six questions for " + pack.label + " — tap on screen or print the same list.";
    }
    const wrap = document.getElementById("qa-level-wrap") || document.querySelector(".floor-prompts-wrap");
    if (wrap) {
      wrap.classList.toggle("is-bonus", qaAge === "bonus");
      wrap.classList.toggle("is-alpha", qaAge === "alpha");
    }
    if (els.btnPrint) {
      els.btnPrint.textContent = "Print · " + pack.label;
      els.btnPrint.setAttribute("aria-label", "Print the same 6 questions for " + pack.label);
    }
    // Legacy jump control (removed from HTML) — keep safe if missing
    if (els.btnMoreQuestions) {
      els.btnMoreQuestions.hidden = true;
    }

    const done = answeredCount(trip, item.id, missions, qaAge);
    if (els.progressPill) {
      els.progressPill.hidden = !showCheck && !done;
      els.progressPill.innerHTML = showCheck
        ? `Checked <span class="stamp">✅</span>`
        : done
          ? `${done} of ${missions.length}`
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
      const selected = new Set(getAnswers(aState, mission.id, qaAge));
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
    let list = [...getAnswers(aState, mission.id, qaAge)];
    if (mission.multi) {
      list = list.includes(choice) ? list.filter((c) => c !== choice) : [...list, choice];
    } else {
      list = list.includes(choice) ? [] : [choice];
    }
    setAnswers(aState, mission.id, qaAge, list);
    // clear submitted when changing answers at this level
    if (aState.submitted) aState.submitted = false;
    trip.updatedAt = Date.now();
    saveStore();
    renderDetail(trip, item, venue);
  }

  function submitAnswers() {
    const trip = getTrip(currentTripId);
    const item = getItem(currentItemId);
    const venue = trip ? getVenue(trip.venueId) : null;
    if (!trip || !item || !venue) return;
    const pack = talkPackFor(item, venue, qaAge);
    const missions = pack.missions;
    if (answeredCount(trip, item.id, missions, qaAge) === 0) {
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
    loadQaAge();
    const pack = talkPackFor(item, venue, qaAge);
    const aState = itemState(trip, item.id);
    // Flatten namespaced answers for this talk level into missionId → picks
    const answers = {};
    for (const m of pack.missions) {
      answers[m.id] = getAnswers(aState, m.id, qaAge);
    }
    // Shared layout: talk prompts + level-matched pick-ones + photo
    if (window.FPPrint && typeof window.FPPrint.fillQaPrintSheet === "function") {
      window.FPPrint.fillQaPrintSheet(item, venue, {
        answers,
        missions: pack.missions,
        prompts: [], // one stream: questions live on the 6 cards only
        talkLabel: pack.label,
        talkLevel: pack.level,
        bannerNote: `${venue.name} · ${pack.label} · 6 questions · Circle answers · No scores`,
        footer: "Same 6 questions as on screen · Field Trip Kit",
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
    const grid = document.getElementById("mission-grid");
    if (grid) grid.scrollIntoView({ behavior: "smooth", block: "start" });
  }
  if (els.btnMoreQuestions) {
    els.btnMoreQuestions.addEventListener("click", openPickOneQuestions);
  }

  // Q&A talk level: 2–4 / 5–8 / 9–12 / Bonus / Alpha
  loadQaAge();
  document.querySelectorAll(".qa-level-chip[data-qa-age]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
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
