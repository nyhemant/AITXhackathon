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
    renderDetail(trip, item, getVenue(trip.venueId));
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
      let status = "Optional tips";
      if (st.submitted) status = "Answers checked ✓";
      else if (st.taught) status = "Taught a grown-up ⭐";
      else if (done) status = `${done} answered`;
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "animal-card" + (done || st.taught || st.submitted ? " has-progress" : "");
      btn.innerHTML = `
        <img src="${item.photo}" alt="${escapeHtml(item.name)}" loading="lazy" />
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
    els.btnCam.href = (item.links && item.links.cam) || "#";
    els.btnPictures.href = (item.links && item.links.pictures) || "#";
    els.btnMore.href = (item.links && item.links.more) || "#";
    els.btnCam.textContent =
      venue && venue.packTemplate === "exhibits" ? "Museum site" : "Look up / live cam";

    const done = answeredCount(trip, item.id, missions);
    els.progressPill.innerHTML = showCheck
      ? `Checked <span class="stamp">✅</span>`
      : done
        ? `${done} of ${missions.length} answered`
        : `Optional Q&A`;

    els.teachBanner.classList.toggle("show", aState.taught);
    if (aState.taught) {
      els.teachBanner.textContent = `⭐ They taught a grown-up about ${item.name}!`;
    }
    els.btnTaught.textContent = aState.taught ? "Taught a grown-up ⭐" : "Kid taught a grown-up";
    els.btnSubmit.textContent = showCheck ? "Check again" : "Check answers";

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
    const missions = missionsFor(venue);
    const aState = itemState(trip, item.id);
    const cards = missions
      .map((mission, index) => {
        const selected = new Set(aState.answers[mission.id] || []);
        const choices = mission.choices
          .map(
            (label) =>
              `<div class="ps-choice${selected.has(label) ? " on" : ""}"><span class="ps-dot"></span><span>${escapeHtml(
                label
              )}</span></div>`
          )
          .join("");
        return `<section class="ps-card c${index}">
          <div class="ps-card-head"><span class="ps-num">${mission.num}</span>
          <p class="ps-title">${escapeHtml(mission.title)}</p></div>
          <h3 class="ps-q">${escapeHtml(mission.question)}</h3>
          <div class="ps-choices">${choices}</div></section>`;
      })
      .join("");
    els.printSheet.innerHTML = `
      <div class="ps-banner"><h1>BABY'S DAY OUT</h1>
      <p>${escapeHtml(venue.name)} · Circle answers · No scores</p></div>
      <section class="ps-hero">
        <img src="${escapeAttr(item.photo)}" alt="" />
        <div>
          <h2>${escapeHtml(item.name)}</h2>
          <p class="ps-meta">${escapeHtml(item.blurb || "")}</p>
          <p class="ps-line"><strong>Explorer:</strong> <span class="write-in-line">________________</span> <span class="write-in-hint">(write name)</span></p>
          <p class="ps-line"><strong>Place:</strong> ${escapeHtml(venue.name)}</p>
        </div>
      </section>
      <div class="ps-grid">${cards}</div>
      <p class="ps-footer">Q&A card · check on screen with Submit</p>`;
  }

  function printMissionCard() {
    const trip = getTrip(currentTripId);
    const item = getItem(currentItemId);
    if (!trip || !item) return;
    buildPrintSheet(item, trip, getVenue(trip.venueId));
    els.treasureSheet.innerHTML = "";
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
          <h1>🗺️ TREASURE HUNT</h1>
          <p>One page · Baby’s Day Out</p>
        </div>
        <div class="th-meta">
          <p><strong>Place:</strong> ${escapeHtml(venue.name)}
          &nbsp;·&nbsp; <strong>Where:</strong> ${escapeHtml(venue.location || "")}</p>
          <p><strong>Explorer:</strong> <span class="write-in-line">________________</span>
          &nbsp;&nbsp; <strong>Date:</strong> ____________</p>
        </div>
        <p class="th-intro">Check each box when you find it. No rush!</p>
        <div class="th-list">${huntHtml}</div>
        <div class="th-stars">
          <p class="th-stars-title">Star list (top picks)</p>
          <div class="th-chips">${stars}</div>
        </div>
        <div class="th-map">
          <p class="th-map-title">Path doodle <span class="th-map-hint">— start → favorite → end</span></p>
          <div class="th-map-box"></div>
        </div>
        <p class="th-footer">Optional after: open Baby's Day Out → tap a card → Q&A</p>
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

  // events
  els.btnTreasure.addEventListener("click", printTreasureHunt);
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
    const url = `${location.origin}/field-pack/app.html#/venue/${encodeURIComponent(selectedVenueId)}`;
    try {
      await navigator.clipboard.writeText(url);
      els.shareLinkStatus.hidden = false;
      setTimeout(() => {
        els.shareLinkStatus.hidden = true;
      }, 2000);
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
  els.btnPrint.addEventListener("click", printMissionCard);
  els.btnSubmit.addEventListener("click", submitAnswers);
  if (els.btnWinPrint) els.btnWinPrint.addEventListener("click", printTreasureHunt);
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
