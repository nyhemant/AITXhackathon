(() => {
  const catalog = window.FIELD_PACK_CATALOG;
  const storageKey = "1less-babys-day-out-trips-v1";
  const legacyStorageKeys = ["arya-field-pack-trips-v2", "arya-field-pack-trips-v1"];
  const precooked = window.fpPrecookedVenueIds || ["dallas-zoo"];

  const els = {
    home: document.getElementById("view-home"),
    picker: document.getElementById("view-picker"),
    trip: document.getElementById("view-trip"),
    detail: document.getElementById("view-detail"),
    backBtn: document.getElementById("btn-back"),
    resetBtn: document.getElementById("btn-reset"),
    brandSub: document.getElementById("brand-sub"),
    venueSelect: document.getElementById("venue-select"),
    homeTitle: document.getElementById("home-title"),
    homeBlurb: document.getElementById("home-blurb"),
    venueCards: document.getElementById("venue-cards"),
    tripList: document.getElementById("trip-list"),
    tripListEmpty: document.getElementById("trip-list-empty"),
    btnNewTrip: document.getElementById("btn-new-trip"),
    btnTreasureHome: document.getElementById("btn-treasure-home"),
    btnTreasurePicker: document.getElementById("btn-treasure-picker"),
    btnTreasureTrip: document.getElementById("btn-treasure-trip"),
    tripTitleInput: document.getElementById("trip-title-input"),
    tripDateInput: document.getElementById("trip-date-input"),
    pickerFeatured: document.getElementById("picker-featured"),
    pickerExtra: document.getElementById("picker-extra"),
    pickerFeaturedHeading: document.getElementById("picker-featured-heading"),
    pickerExtraHeading: document.getElementById("picker-extra-heading"),
    btnSaveTrip: document.getElementById("btn-save-trip"),
    pickerVenueChip: document.getElementById("picker-venue-chip"),
    pickerTitle: document.getElementById("picker-title"),
    pickerBlurb: document.getElementById("picker-blurb"),
    tripHeading: document.getElementById("trip-heading"),
    tripMeta: document.getElementById("trip-meta"),
    tripVenueChip: document.getElementById("trip-venue-chip"),
    tripAnimalGrid: document.getElementById("trip-animal-grid"),
    tripAnimalsEmpty: document.getElementById("trip-animals-empty"),
    tripGridHeading: document.getElementById("trip-grid-heading"),
    btnEditAnimals: document.getElementById("btn-edit-animals"),
    btnZooSite: document.getElementById("btn-zoo-site"),
    btnZooMap: document.getElementById("btn-zoo-map"),
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
    btnShareLink: document.getElementById("btn-share-link"),
    shareLinkStatus: document.getElementById("share-link-status"),
    winBanner: document.getElementById("win-banner"),
    btnWinPrint: document.getElementById("btn-win-print"),
  };

  let store = loadStore();
  let selectedVenueId = store.selectedVenueId || window.fpDefaultVenueId || "dallas-zoo";
  let currentTripId = null;
  let currentItemId = null;
  let pickerDraft = null;

  function loadStore() {
    try {
      let raw = localStorage.getItem(storageKey);
      if (!raw) {
        for (const k of legacyStorageKeys) {
          raw = localStorage.getItem(k);
          if (raw) break;
        }
      }
      if (!raw) return { trips: [], selectedVenueId: "dallas-zoo" };
      const parsed = JSON.parse(raw);
      if (!parsed || !Array.isArray(parsed.trips)) return { trips: [], selectedVenueId: "dallas-zoo" };
      return {
        trips: (parsed.trips || []).map((t) => ({ ...t, venueId: t.venueId || "dallas-zoo" })),
        selectedVenueId: parsed.selectedVenueId || "dallas-zoo",
      };
    } catch {
      return { trips: [], selectedVenueId: "dallas-zoo" };
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

  function hideAll() {
    [els.home, els.picker, els.trip, els.detail].forEach((v) => v.classList.add("hidden"));
  }

  function setBack(on, label) {
    if (!on) {
      els.backBtn.classList.add("hidden");
      return;
    }
    els.backBtn.classList.remove("hidden");
    els.backBtn.textContent = label || "← Back";
  }

  const VENUE_CARD_COPY = {
    "dallas-zoo": {
      emoji: "🦁",
      blurb: "Animals · smart shortlist for Dallas Zoo",
      cover: "photos/sumatran-tiger.jpg",
    },
    "childrens-aquarium-dallas": {
      emoji: "🦈",
      blurb: "Water life · half-day kid aquarium list",
      cover: "photos/shark.jpg",
    },
    "childrens-museum-perot": {
      emoji: "🎨",
      blurb: "Play zones · Moody Family Children’s Museum",
      cover: "photos/cm-woven.jpg",
    },
  };

  function fillVenueSelect() {
    els.venueSelect.innerHTML = "";
    for (const id of precooked) {
      const v = getVenue(id);
      if (!v) continue;
      const opt = document.createElement("option");
      opt.value = id;
      opt.textContent = v.shortName || v.name;
      els.venueSelect.appendChild(opt);
    }
    const stub = document.createElement("option");
    stub.value = "__add__";
    stub.textContent = "＋ Add a place… (soon)";
    els.venueSelect.appendChild(stub);
    els.venueSelect.value = precooked.includes(selectedVenueId)
      ? selectedVenueId
      : precooked[0];
    selectedVenueId = els.venueSelect.value;
    renderVenueCards();
  }

  function renderVenueCards() {
    if (!els.venueCards) return;
    els.venueCards.innerHTML = "";
    for (const id of precooked) {
      const v = getVenue(id);
      if (!v) continue;
      const meta = VENUE_CARD_COPY[id] || { emoji: "📍", blurb: v.blurb || "" };
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "venue-card" + (id === selectedVenueId ? " selected" : "");
      btn.setAttribute("aria-pressed", id === selectedVenueId ? "true" : "false");
      const cover = meta.cover || (getItem(v.featuredAnimalIds[0]) || {}).photo || "";
      btn.innerHTML = `
        ${
          cover
            ? `<img class="vc-photo" src="${escapeAttr(cover)}" alt="" loading="lazy" />`
            : `<span class="vc-emoji" aria-hidden="true">${meta.emoji}</span>`
        }
        <span class="vc-name">${meta.emoji || ""} ${escapeHtml(v.shortName || v.name)}</span>
        <span class="vc-meta">${escapeHtml(meta.blurb)}</span>
      `;
      btn.addEventListener("click", () => {
        selectedVenueId = id;
        els.venueSelect.value = id;
        saveStore();
        showHome();
      });
      els.venueCards.appendChild(btn);
    }
  }

  function currentVenue() {
    return getVenue(selectedVenueId);
  }

  // ---- nav ----
  function showHome() {
    const homeTrips = (store.trips || []).filter((tr) => tr.venueId === selectedVenueId);
    showWinBanner(homeTrips.some(tripHasCheckedOrTaught));
    currentTripId = null;
    currentItemId = null;
    pickerDraft = null;
    hideAll();
    els.home.classList.remove("hidden");
    setBack(false);
    const v = currentVenue();
    els.brandSub.textContent = "Outing kit · shortlist, hunt, optional missions";
    // Keep the fixed objective headline; only refine blurb with venue context.
    if (v) {
      els.homeBlurb.innerHTML = `${escapeHtml(v.blurb)} <strong>Selected:</strong> ${escapeHtml(
        v.name
      )} (${escapeHtml(v.location || "")}). Print a treasure hunt before you go. Missions after the visit are optional.`;
      els.btnNewTrip.textContent = `Build shortlist · ${v.shortName || v.name} →`;
    } else {
      els.btnNewTrip.textContent = "Build shortlist & start →";
    }
    renderVenueCards();
    renderTripList();
    history.replaceState(null, "", `#/venue/${selectedVenueId}`);
  }

  function showPicker(tripIdOrNull) {
    const venue = currentVenue();
    if (!venue) return showHome();
    hideAll();
    els.picker.classList.remove("hidden");
    setBack(true, tripIdOrNull ? "← Trip" : "← Trips");

    const label = venue.itemLabel || "items";
    els.pickerTitle.textContent = `Pick ${label} for this trip`;
    els.pickerBlurb.textContent =
      venue.packTemplate === "exhibits"
        ? "Featured play zones are checked. Keep it small!"
        : "Featured are checked. Add extras only if you want.";
    els.pickerFeaturedHeading.textContent = "⭐ Featured (great default)";
    els.pickerExtraHeading.textContent =
      venue.animalIds.length > venue.featuredAnimalIds.length
        ? "➕ Optional extras"
        : "➕ All set (no extras)";
    els.pickerExtraHeading.classList.toggle(
      "hidden",
      venue.animalIds.length <= venue.featuredAnimalIds.length
    );

    if (tripIdOrNull) {
      const trip = getTrip(tripIdOrNull);
      if (!trip) return showHome();
      currentTripId = trip.id;
      selectedVenueId = trip.venueId;
      els.venueSelect.value = selectedVenueId;
      pickerDraft = {
        tripId: trip.id,
        title: trip.title,
        date: trip.date || "",
        venueId: trip.venueId,
        selected: new Set(trip.selectedAnimalIds),
      };
    } else {
      currentTripId = null;
      pickerDraft = {
        tripId: null,
        title: `Outing · ${venue.shortName || venue.name}`,
        date: "",
        venueId: venue.id,
        selected: new Set(venue.featuredAnimalIds),
      };
    }

    els.tripTitleInput.value = pickerDraft.title;
    els.tripDateInput.value = pickerDraft.date || "";
    els.pickerVenueChip.textContent = `📍 ${venue.name} · ${venue.location}`;
    els.brandSub.textContent = `${venue.shortName} · pick ${label}`;
    renderPicker(venue);
    history.replaceState(
      null,
      "",
      pickerDraft.tripId
        ? `#/trip/${pickerDraft.tripId}/edit`
        : `#/venue/${venue.id}/new`
    );
  }

  function showTrip(tripId) {
    const trip = getTrip(tripId);
    if (!trip) return showHome();
    currentTripId = tripId;
    currentItemId = null;
    pickerDraft = null;
    selectedVenueId = trip.venueId;
    els.venueSelect.value = selectedVenueId;
    hideAll();
    els.trip.classList.remove("hidden");
    setBack(true, "← Trips");
    const venue = getVenue(trip.venueId);
    els.brandSub.textContent = `${venue ? venue.shortName : "Trip"} · ${trip.title}`;
    renderTrip(trip, venue);
    history.replaceState(null, "", `#/trip/${tripId}`);
  }

  function showItem(tripId, itemId) {
    const trip = getTrip(tripId);
    const item = getItem(itemId);
    if (!trip || !item) return showHome();
    if (!trip.selectedAnimalIds.includes(itemId)) return showTrip(tripId);
    currentTripId = tripId;
    currentItemId = itemId;
    selectedVenueId = trip.venueId;
    els.venueSelect.value = selectedVenueId;
    hideAll();
    els.detail.classList.remove("hidden");
    setBack(true, "← Trip");
    els.brandSub.textContent = `${item.name} · missions`;
    renderDetail(trip, item, getVenue(trip.venueId));
    history.replaceState(null, "", `#/trip/${tripId}/item/${itemId}`);
  }

  // ---- render ----
  function renderTripList() {
    els.tripList.innerHTML = "";
    const trips = store.trips
      .filter((t) => t.venueId === selectedVenueId)
      .sort((a, b) => (b.updatedAt || 0) - (a.updatedAt || 0));
    els.tripListEmpty.classList.toggle("hidden", trips.length > 0);
    const venue = currentVenue();
    const missions = missionsFor(venue);

    for (const trip of trips) {
      const total = trip.selectedAnimalIds.length;
      let submitted = 0;
      let taught = 0;
      for (const id of trip.selectedAnimalIds) {
        const st = itemState(trip, id);
        if (st.submitted) submitted += 1;
        if (st.taught) taught += 1;
      }
      const card = document.createElement("button");
      card.type = "button";
      card.className = "trip-card";
      card.innerHTML = `
        <span class="trip-card-title">${escapeHtml(trip.title)}</span>
        <span class="trip-card-meta">${escapeHtml(venue ? venue.name : "")}${
          trip.date ? " · " + escapeHtml(trip.date) : ""
        }</span>
        <span class="trip-card-stats">${total} ${
          venue ? venue.itemLabel : "items"
        } · ${submitted} checked · ${taught} taught</span>
      `;
      card.addEventListener("click", () => showTrip(trip.id));
      els.tripList.appendChild(card);
    }
  }

  function renderPicker(venue) {
    const featured = venue.featuredAnimalIds;
    const extra = venue.animalIds.filter((id) => !featured.includes(id));
    els.pickerExtra.classList.toggle("hidden", extra.length === 0);

    const fill = (container, ids) => {
      container.innerHTML = "";
      for (const id of ids) {
        const item = getItem(id);
        if (!item) continue;
        const on = pickerDraft.selected.has(id);
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "picker-card" + (on ? " selected" : "");
        btn.innerHTML = `
          <img src="${item.photo}" alt="" loading="lazy" onerror="this.style.background='#ccc'" />
          <span class="picker-check">${on ? "✓" : ""}</span>
          <span class="picker-name">${item.emoji || ""} ${escapeHtml(item.name)}</span>
        `;
        btn.addEventListener("click", () => {
          if (pickerDraft.selected.has(id)) pickerDraft.selected.delete(id);
          else pickerDraft.selected.add(id);
          renderPicker(venue);
        });
        container.appendChild(btn);
      }
    };
    fill(els.pickerFeatured, featured);
    fill(els.pickerExtra, extra);
  }

  function renderTrip(trip, venue) {
    const missions = missionsFor(venue);
    els.tripHeading.textContent = trip.title;
    els.tripVenueChip.textContent = `📍 ${venue ? venue.name : ""} · ${venue ? venue.location : ""}`;
    const n = trip.selectedAnimalIds.length;
    let checked = 0;
    for (const id of trip.selectedAnimalIds) {
      if (itemState(trip, id).submitted) checked += 1;
    }
    els.tripMeta.textContent = trip.date
      ? `${n} ${venue.itemLabel} · ${checked} checked · ${trip.date}`
      : `${n} ${venue.itemLabel} · ${checked} checked`;
    els.tripGridHeading.textContent = `On this trip (${venue.itemLabel})`;

    if (venue) {
      els.btnZooSite.href = venue.website || "#";
      els.btnZooMap.href = venue.mapUrl || venue.website || "#";
    }

    els.tripAnimalGrid.innerHTML = "";
    els.tripAnimalsEmpty.classList.toggle("hidden", n > 0);

    for (const id of trip.selectedAnimalIds) {
      const item = getItem(id);
      if (!item) continue;
      const st = itemState(trip, id);
      const done = answeredCount(trip, id, missions);
      let status = "Tap to explore";
      if (st.submitted) status = "Checked ✓";
      else if (st.taught) status = "Taught ⭐";
      else if (done) status = `${done} of 6 missions`;

      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "animal-card" + (done || st.taught || st.submitted ? " has-progress" : "");
      btn.innerHTML = `
        <img src="${item.photo}" alt="${escapeHtml(item.name)}" loading="lazy" />
        <span class="meta">
          <span class="name">${item.emoji || ""} ${escapeHtml(item.name)}</span>
          <span class="status">${status}</span>
        </span>
      `;
      btn.addEventListener("click", () => showItem(trip.id, id));
      els.tripAnimalGrid.appendChild(btn);
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
    // if no key defined, any pick is ok
    const ok =
      keyList.length === 0
        ? selected.length > 0 && wrongPicks.length === 0
        : hasCoreHit && wrongPicks.length === 0;

    let feedback;
    if (selected.length === 0) {
      feedback = keyList.length
        ? `No circles yet. Try: ${keyList.join(" · ")}`
        : "Circle what you did!";
    } else if (ok) {
      feedback = `Yes! Explorer match: ${rightPicks.join(" · ") || selected.join(" · ")}`;
    } else if (wrongPicks.length && hasCoreHit) {
      feedback = `Close! Keep ${rightPicks.join(" · ")}. Look again at: ${wrongPicks.join(
        " · "
      )}. Tips: ${keyList.join(" · ")}`;
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

    // hide cam label for exhibits
    els.btnCam.textContent =
      venue && venue.packTemplate === "exhibits" ? "🏛️ Museum site" : "📹 Live cam / look";

    const done = answeredCount(trip, item.id, missions);
    els.progressPill.innerHTML = showCheck
      ? `Answers checked <span class="stamp">✅</span>`
      : done === 6
        ? `All 6 missions picked! <span class="stamp">🎉</span>`
        : `${done} of 6 missions picked`;

    els.teachBanner.classList.toggle("show", aState.taught);
    if (aState.taught) {
      els.teachBanner.textContent = `⭐ They taught a grown-up about ${item.name}!`;
    }
    els.btnTaught.textContent = aState.taught ? "Taught! ⭐" : "I taught a grown-up!";
    els.btnSubmit.textContent = showCheck ? "✅ Checked — submit again" : "✅ Submit & check answers";
    let optNote = document.getElementById("mission-optional-note");
    if (!optNote && els.missionGrid && els.missionGrid.parentElement) {
      optNote = document.createElement("p");
      optNote.id = "mission-optional-note";
      optNote.className = "mission-optional-note no-print";
      optNote.textContent = "Optional after the visit — skip anytime. The treasure hunt is enough for a great day.";
      els.missionGrid.parentElement.insertBefore(optNote, els.missionGrid);
    }


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
            else if (!on && (correctSet.has(label) || alwaysOk.has(label)))
              extra = " is-correct-key";
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
        ${fbHtml}
      `;
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
    let headline;
    if (okCount === checkable.length) {
      headline = `🌟 Amazing work on ${item.name}! Checked: ${okCount}/${checkable.length}`;
    } else if (okCount > 0) {
      headline = `🔎 Nice try on ${item.name}! Matched: ${okCount}/${checkable.length}`;
    } else {
      headline = `🗺️ Keep exploring ${item.name} — use the tips and try again!`;
    }
    const items = evals
      .map(({ mission, result }) => {
        let cls = "r-open";
        let mark = "⭐";
        if (result.kind === "ok") {
          cls = "r-ok";
          mark = "✅";
        } else if (result.kind === "try") {
          cls = "r-try";
          mark = "🔄";
        }
        const keyLine =
          mission.checkable && result.correctKey.length
            ? `<span class="r-key">Guide: ${escapeHtml(result.correctKey.join(" · "))}</span>`
            : "";
        return `<li>
          <span class="r-title">${mark} ${escapeHtml(mission.num)}. ${escapeHtml(mission.title)}</span>
          <span class="${cls}">${escapeHtml(result.feedback)}</span>${keyLine}
        </li>`;
      })
      .join("");
    els.resultsPanel.hidden = false;
    els.resultsPanel.innerHTML = `
      <p class="results-summary">${escapeHtml(headline)}</p>
      <p style="margin:0 0 10px;font-weight:700;color:var(--muted)">Story boxes picked: ${openOk}</p>
      <ul class="results-list">${items}</ul>`;
    els.resultsPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function toggleChoice(trip, item, mission, choice, venue) {
    const aState = itemState(trip, item.id);
    let list = Array.isArray(aState.answers[mission.id])
      ? [...aState.answers[mission.id]]
      : [];
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

  function saveTripFromPicker() {
    if (!pickerDraft) return;
    const venue = getVenue(pickerDraft.venueId) || currentVenue();
    pickerDraft.title =
      (els.tripTitleInput.value || "").trim() || `Outing · ${venue.shortName || venue.name}`;
    pickerDraft.date = els.tripDateInput.value || "";
    const selected = [...pickerDraft.selected];
    if (!selected.length) {
      alert("Pick at least one item!");
      return;
    }
    let trip;
    if (pickerDraft.tripId) {
      trip = getTrip(pickerDraft.tripId);
      if (!trip) return showHome();
      trip.title = pickerDraft.title;
      trip.date = pickerDraft.date;
      trip.selectedAnimalIds = selected;
      trip.updatedAt = Date.now();
    } else {
      trip = {
        id: uid(),
        title: pickerDraft.title,
        venueId: venue.id,
        date: pickerDraft.date,
        selectedAnimalIds: selected,
        animals: {},
        createdAt: Date.now(),
        updatedAt: Date.now(),
      };
      store.trips.push(trip);
    }
    saveStore();
    showTrip(trip.id);
  }

  // ---- print mission card ----
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
      <div class="ps-banner"><h1>ARYA'S FIELD PACK</h1>
      <p>${escapeHtml(venue.name)} · Circle answers · No scores</p></div>
      <section class="ps-hero">
        <img src="${escapeAttr(item.photo)}" alt="" />
        <div>
          <h2>${escapeHtml(item.name)}</h2>
          <p class="ps-meta">${escapeHtml(item.blurb || "")}</p>
          <p class="ps-line"><strong>Explorer:</strong> <span class="write-in-line" aria-label="Write name">________________</span> <span class="write-in-hint">(write name)</span></p>
          <p class="ps-line"><strong>Trip:</strong> ${escapeHtml(trip.title)}</p>
          <p class="ps-line"><strong>Day:</strong> ${escapeHtml(trip.date || "________")}</p>
        </div>
      </section>
      <div class="ps-grid">${cards}</div>
      <p class="ps-footer">Mission card · check on screen with Submit</p>`;
  }

  function printMissionCard() {
    const trip = getTrip(currentTripId);
    const item = getItem(currentItemId);
    if (!trip || !item) return;
    const venue = getVenue(trip.venueId);
    buildPrintSheet(item, trip, venue);
    els.treasureSheet.innerHTML = "";
    requestAnimationFrame(() => requestAnimationFrame(() => window.print()));
  }

  // ---- treasure hunt (pre-visit) ----
  function buildTreasureSheet(venue, tripTitle, tripDate) {
    const hunts = venue.treasureHunt || [];
    const rows = hunts
      .map(
        (h, i) => `
      <div class="th-row">
        <span class="th-box"></span>
        <span class="th-num">${i + 1}</span>
        <span class="th-text">${escapeHtml(h.text)}</span>
      </div>`
      )
      .join("");

    const stars = (venue.featuredAnimalIds || [])
      .slice(0, 8)
      .map((id) => {
        const it = getItem(id);
        return it ? `<span class="th-chip">${it.emoji || "•"} ${escapeHtml(it.name)}</span>` : "";
      })
      .join("");

    els.treasureSheet.innerHTML = `
      <div class="th-page">
        <div class="th-banner">
          <h1>🗺️ TREASURE HUNT</h1>
          <p>Print before you go · Baby’s Day Out</p>
        </div>
        <div class="th-meta">
          <p><strong>Place:</strong> ${escapeHtml(venue.name)}</p>
          <p><strong>Where:</strong> ${escapeHtml(venue.location || "")}</p>
          <p><strong>Explorer:</strong> <span class="write-in-line">________________</span> <span class="write-in-hint">(write name)</span> &nbsp;&nbsp; <strong>Date:</strong> ${escapeHtml(
            tripDate || "____________"
          )}</p>
          <p><strong>Trip name:</strong> ${escapeHtml(tripTitle || "____________")}</p>
        </div>
        <p class="th-intro">Find or try each one. Check the box when you do. No rush — have fun!</p>
        <div class="th-list">${rows}</div>
        <div class="th-stars">
          <p class="th-stars-title">Star list (ideas while you walk)</p>
          <div class="th-chips">${stars}</div>
        </div>
        <div class="th-map">
          <p class="th-map-title">My path doodle</p>
          <p class="th-map-hint">Draw where you went — start → favorite stop → end</p>
          <div class="th-map-box"></div>
        </div>
        <p class="th-footer">After the visit: open Baby's Day Out on the computer → finish missions → Submit!</p>
      </div>`;
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

  function tripHasCheckedOrTaught(trip) {
    if (!trip || !trip.animals) return false;
    return Object.values(trip.animals).some(
      (a) => a && (a.taught || a.submitted)
    );
  }

    function printTreasureHunt(opts = {}) {
    const venue = opts.venue || currentVenue();
    if (!venue) return;
    const trip = opts.tripId ? getTrip(opts.tripId) : null;
    buildTreasureSheet(
      venue,
      opts.title || (trip && trip.title) || els.tripTitleInput?.value || "",
      opts.date || (trip && trip.date) || els.tripDateInput?.value || ""
    );
    els.printSheet.innerHTML = "";
    // mark body for treasure-only print
    document.body.classList.add("printing-treasure");
    const cleanup = () => {
      document.body.classList.remove("printing-treasure");
      window.removeEventListener("afterprint", cleanup);
    };
    window.addEventListener("afterprint", cleanup);
    requestAnimationFrame(() => requestAnimationFrame(() => window.print()));
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

  // ---- events ----
  fillVenueSelect();

  els.venueSelect.addEventListener("change", () => {
    if (els.venueSelect.value === "__add__") {
      alert(
        "“Add a place…” is coming soon!\n\nFor now pick:\n• Dallas Zoo\n• Children’s Aquarium\n• Children’s Museum (Perot)"
      );
      els.venueSelect.value = selectedVenueId;
      return;
    }
    selectedVenueId = els.venueSelect.value;
    saveStore();
    showHome();
  });

  els.btnNewTrip.addEventListener("click", () => showPicker(null));
  els.btnSaveTrip.addEventListener("click", saveTripFromPicker);
  els.btnEditAnimals.addEventListener("click", () => {
    if (currentTripId) showPicker(currentTripId);
  });

  async function copyOutingLink() {
    const url = `${location.origin}/field-pack/app.html#/venue/${encodeURIComponent(selectedVenueId || "dallas-zoo")}`;
    try {
      await navigator.clipboard.writeText(url);
      if (els.shareLinkStatus) {
        els.shareLinkStatus.hidden = false;
        setTimeout(() => {
          els.shareLinkStatus.hidden = true;
        }, 2500);
      }
    } catch {
      prompt("Copy this outing link:", url);
    }
  }
  if (els.btnShareLink) els.btnShareLink.addEventListener("click", () => copyOutingLink());

  els.btnTreasureHome.addEventListener("click", () => printTreasureHunt());
  els.btnTreasurePicker.addEventListener("click", () =>
    printTreasureHunt({
      title: els.tripTitleInput.value,
      date: els.tripDateInput.value,
    })
  );
  els.btnTreasureTrip.addEventListener("click", () => {
    if (currentTripId) printTreasureHunt({ tripId: currentTripId });
  });

  els.backBtn.addEventListener("click", () => {
    if (!els.detail.classList.contains("hidden") && currentTripId) return showTrip(currentTripId);
    if (!els.picker.classList.contains("hidden")) {
      if (pickerDraft && pickerDraft.tripId) return showTrip(pickerDraft.tripId);
      return showHome();
    }
    if (!els.trip.classList.contains("hidden")) return showHome();
    showHome();
  });

  els.resetBtn.addEventListener("click", () => {
    if (!els.detail.classList.contains("hidden") && currentTripId && currentItemId) {
      if (!confirm("Clear answers for this item only?")) return;
      const trip = getTrip(currentTripId);
      trip.animals[currentItemId] = { answers: {}, taught: false, submitted: false };
      trip.updatedAt = Date.now();
      saveStore();
      renderDetail(trip, getItem(currentItemId), getVenue(trip.venueId));
      return;
    }
    if (!els.trip.classList.contains("hidden") && currentTripId) {
      if (!confirm("Delete this whole trip?")) return;
      store.trips = store.trips.filter((t) => t.id !== currentTripId);
      saveStore();
      showHome();
      return;
    }
    if (!confirm("Delete ALL trips for all places on this computer?")) return;
    store = { trips: [], selectedVenueId };
    saveStore();
    showHome();
  });

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
  if (els.btnWinPrint) {
    els.btnWinPrint.addEventListener("click", () => printTreasureHunt({ tripId: currentTripId }));
  }

  function routeFromHash() {
    const hash = location.hash || "#/";
    let m;
    if ((m = hash.match(/^#\/trip\/([^/]+)\/item\/([^/]+)/))) {
      showItem(m[1], m[2]);
      return;
    }
    // legacy animal path
    if ((m = hash.match(/^#\/trip\/([^/]+)\/animal\/([^/]+)/))) {
      showItem(m[1], m[2]);
      return;
    }
    if ((m = hash.match(/^#\/trip\/([^/]+)\/edit/))) {
      const t = getTrip(m[1]);
      if (t) selectedVenueId = t.venueId;
      fillVenueSelect();
      showPicker(m[1]);
      return;
    }
    if ((m = hash.match(/^#\/trip\/([^/]+)/))) {
      showTrip(m[1]);
      return;
    }
    if ((m = hash.match(/^#\/venue\/([^/]+)\/new/))) {
      selectedVenueId = m[1];
      fillVenueSelect();
      showPicker(null);
      return;
    }
    if ((m = hash.match(/^#\/venue\/([^/]+)/))) {
      selectedVenueId = m[1];
      fillVenueSelect();
      showHome();
      return;
    }
    showHome();
  }

  window.addEventListener("hashchange", routeFromHash);
  routeFromHash();
})();
