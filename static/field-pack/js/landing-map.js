(() => {
  const allPlaces = window.FP_PLACES || [];
  const TOP_IDS = new Set(window.FP_TOP_PLACE_IDS || []);
  const detail = document.getElementById("pin-detail");
  const mapHost = document.getElementById("map-host");
  const citySelect = document.getElementById("city-select");
  const venueSelect = document.getElementById("venue-select-landing");
  const scopeTop = document.getElementById("scope-top");
  const scopeMore = document.getElementById("scope-more");
  const stateSelect = document.getElementById("state-select");
  const stateField = document.getElementById("state-field");
  const metroField = document.getElementById("metro-field");
  const mapCount = document.getElementById("map-count");
  const btnZoomIn = document.getElementById("map-zoom-in");
  const btnZoomOut = document.getElementById("map-zoom-out");
  const btnZoomReset = document.getElementById("map-zoom-reset");
  const mapViewport = document.getElementById("map-viewport");

  /** Metro groups for Top mode dropdown (not every pin). */
  const METRO_DEFS = [
    { id: "all", label: "Any area", symbols: "🇺🇸", states: null },
    { id: "dallas", label: "Dallas area", symbols: "🦁", states: ["TX"], regions: ["dfw"] },
    { id: "houston", label: "Houston", symbols: "🐘", states: ["TX"], cities: ["Houston"] },
    { id: "austin", label: "Austin", symbols: "🔬", states: ["TX"], cities: ["Austin"] },
    { id: "san-diego", label: "San Diego", symbols: "🐼", states: ["CA"], cities: ["San Diego", "Escondido"] },
    { id: "la", label: "Los Angeles", symbols: "🦅", states: ["CA"], cities: ["Los Angeles", "Long Beach"] },
    { id: "monterey", label: "Monterey", symbols: "🌊", states: ["CA"], cities: ["Monterey"] },
    { id: "sf", label: "San Francisco", symbols: "🌿", states: ["CA"], cities: ["San Francisco"] },
    { id: "chicago", label: "Chicago", symbols: "🐠", states: ["IL"], cities: ["Chicago"] },
    { id: "atlanta", label: "Atlanta", symbols: "🐋", states: ["GA"], cities: ["Atlanta"] },
    { id: "dc", label: "Washington, DC", symbols: "🦥", states: ["DC"], cities: ["Washington"] },
    { id: "nyc", label: "New York", symbols: "🦴", states: ["NY"], cities: ["New York", "Bronx"] },
    { id: "boston", label: "Boston", symbols: "🦞", states: ["MA"], cities: ["Boston"] },
    { id: "florida", label: "Florida", symbols: "🚀", states: ["FL"], cities: ["Merritt Island"] },
  ];

  let mapScope = "top"; // top | more
  let selectedMetroId = "all";
  let selectedState = "";
  let selectedVenueId = "";
  let clusterFocusIds = []; // nearby group open in side panel
  let zoom = 1;
  let panX = 0;
  let panY = 0;
  let svgEl = null;
  let pinsLayer = null;

  function placeById(id) {
    return allPlaces.find((p) => p.id === id);
  }

  function placesInScope() {
    if (mapScope === "top") {
      return allPlaces.filter((p) => TOP_IDS.has(p.id) || p.tier === "top");
    }
    return [...allPlaces];
  }

  /**
   * Places for the Place dropdown + map pins.
   * A selected state always uses the FULL catalog for that state (not Popular top-N).
   */
  function filteredPlaces() {
    let list;
    if (selectedState) {
      // Full catalog for this state — ignore Popular/top tier cap
      list = allPlaces.filter((p) => p.state === selectedState);
    } else if (mapScope === "top") {
      list = placesInScope();
      if (selectedMetroId !== "all") {
        const m = METRO_DEFS.find((x) => x.id === selectedMetroId);
        if (m) {
          list = list.filter((p) => {
            if (m.regions && m.regions.includes(p.region)) return true;
            if (m.cities && m.cities.includes(p.city)) return true;
            if (m.states && m.states.includes(p.state) && !m.cities && !m.regions) return true;
            if (m.id === "dallas") return p.region === "dfw" || ["Dallas", "Fort Worth"].includes(p.city);
            if (m.id === "houston") return p.city === "Houston";
            if (m.id === "austin") return p.city === "Austin";
            return m.states && m.states.includes(p.state) && (!m.cities || m.cities.includes(p.city));
          });
        }
      }
    } else {
      list = placesInScope(); // all places
    }
    return list.sort((a, b) => a.name.localeCompare(b.name));
  }

  function kidTypeLabel(type) {
    const t = (type || "").toLowerCase();
    if (t.includes("safari")) return "Safari zoo";
    if (t.includes("zoo")) return "Zoo";
    if (t.includes("aquarium")) return "Aquarium";
    if (t.includes("children")) return "Kids museum";
    if (t.includes("space") || t.includes("air")) return "Space / air";
    if (t.includes("science")) return "Science";
    if (t.includes("natural") || t.includes("history")) return "Nature museum";
    return type || "Place";
  }

  function venueOptionLabel(p) {
    const kind = kidTypeLabel(p.type);
    const city = p.city === "Escondido" ? "San Diego area" : p.city;
    return `${p.emoji || "📍"} ${p.name} — ${city}, ${p.state}`;
  }

  function escapeHtml(s) {
    return String(s)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  /** Distinct state codes from the venue catalog (or a subset). */
  function distinctStates(list) {
    const set = new Set(
      (list || [])
        .map((p) => (p && typeof p.state === "string" ? p.state.trim() : ""))
        .filter(Boolean)
    );
    return [...set].sort((a, b) => a.localeCompare(b));
  }

  function clearSelect(sel) {
    if (!sel) return;
    sel.innerHTML = "";
  }

  /**
   * Always keep the State <select> filled from the full catalog so it is never
   * empty if CSS fails to honor [hidden]. Visibility depends on whether we have data.
   * Returns the sorted state list (may be empty).
   */
  function fillStateSelectOptions() {
    const states = distinctStates(allPlaces);
    if (!stateSelect) return states;

    const prev = selectedState;
    clearSelect(stateSelect);
    const o0 = document.createElement("option");
    o0.value = "";
    o0.textContent = "All states";
    stateSelect.appendChild(o0);
    for (const st of states) {
      const o = document.createElement("option");
      o.value = st;
      o.textContent = st;
      stateSelect.appendChild(o);
    }
    if (prev && states.includes(prev)) {
      selectedState = prev;
      stateSelect.value = prev;
    } else {
      selectedState = "";
      stateSelect.value = "";
    }
    return states;
  }

  /**
   * Populate Metroarea + State filters.
   * Both stay in the layout always (plus fixed Place column) so selecting State
   * never shifts the Place dropdown. When a state is chosen, metro is disabled
   * but still occupies its slot; clearing state re-enables metro.
   */
  function fillLocationSelect() {
    if (!citySelect) return;

    const states = fillStateSelectOptions();

    // Never show an empty state control; never hide metro (layout must stay fixed)
    if (stateField) {
      stateField.hidden = states.length === 0;
    }
    if (!states.length) {
      selectedState = "";
    }
    if (metroField) metroField.hidden = false;

    clearSelect(citySelect);
    for (const m of METRO_DEFS) {
      const opt = document.createElement("option");
      opt.value = m.id;
      opt.textContent = m.id === "all" ? m.label : `${m.symbols} ${m.label}`;
      citySelect.appendChild(opt);
    }
    citySelect.value = selectedMetroId || "all";
    // State selection wins: keep metro visible but inactive so Place stays put
    citySelect.disabled = Boolean(selectedState);
  }

  function fillVenueSelect() {
    const list = filteredPlaces();
    venueSelect.innerHTML = "";
    const ph = document.createElement("option");
    ph.value = "";
    if (selectedState) {
      ph.textContent = `All places in ${selectedState} (${list.length})…`;
    } else if (mapScope === "top") {
      ph.textContent = `Choose a place (${list.length})…`;
    } else {
      ph.textContent = `Choose a place (${list.length})…`;
    }
    venueSelect.appendChild(ph);
    for (const p of list) {
      const opt = document.createElement("option");
      opt.value = p.id;
      opt.textContent = venueOptionLabel(p);
      venueSelect.appendChild(opt);
    }
    if (selectedVenueId && list.some((p) => p.id === selectedVenueId)) {
      venueSelect.value = selectedVenueId;
    } else {
      selectedVenueId = "";
      venueSelect.value = "";
    }
    if (mapCount) {
      const topN = allPlaces.filter((p) => TOP_IDS.has(p.id) || p.tier === "top").length;
      if (selectedState) {
        mapCount.textContent = `Showing all ${list.length} places in ${selectedState} — pick one below or tap a pin`;
      } else if (mapScope === "top") {
        mapCount.textContent = `Showing ${topN} popular places — switch to “All places” for more`;
      } else {
        mapCount.textContent = `Showing ${allPlaces.length} places — tap a pin or pick from the lists`;
      }
    }
  }

  /** Ensure UI is on All places so state filter can show, without wiping selectedState. */
  function ensureAllPlacesScope() {
    if (mapScope === "more") return;
    mapScope = "more";
    selectedMetroId = "all";
    if (scopeTop) scopeTop.setAttribute("aria-pressed", "false");
    if (scopeMore) scopeMore.setAttribute("aria-pressed", "true");
    scopeTop?.classList.remove("active");
    scopeMore?.classList.add("active");
  }

  function applyMapTransform() {
    if (!svgEl) return;
    svgEl.style.transformOrigin = "center center";
    svgEl.style.transform = `translate(${panX}px, ${panY}px) scale(${zoom})`;
  }

  function setZoom(z) {
    zoom = Math.min(3.5, Math.max(1, z));
    if (zoom === 1) {
      panX = 0;
      panY = 0;
    }
    applyMapTransform();
    renderPins();
  }

  /** Zoom so the viewport point (clientX/Y) becomes the center. */
  function zoomToClientPoint(clientX, clientY, newZoom) {
    if (!mapViewport) {
      setZoom(newZoom);
      return;
    }
    const rect = mapViewport.getBoundingClientRect();
    const ox = clientX - rect.left - rect.width / 2;
    const oy = clientY - rect.top - rect.height / 2;
    const z0 = zoom || 1;
    const z1 = Math.min(3.5, Math.max(1, newZoom));
    const contentX = (ox - panX) / z0;
    const contentY = (oy - panY) / z0;
    zoom = z1;
    if (zoom <= 1) {
      panX = 0;
      panY = 0;
    } else {
      panX = -contentX * zoom;
      panY = -contentY * zoom;
    }
    applyMapTransform();
    renderPins();
  }

  function pinXY(p) {
    if (!svgEl || p.lat == null || p.lon == null) return null;
    const vb = svgEl.viewBox && svgEl.viewBox.baseVal;
    const w = (vb && vb.width) || 959;
    const h = (vb && vb.height) || 593;
    if (typeof window.fpProjectUS !== "function") return null;
    const pt = window.fpProjectUS(p.lat, p.lon, w, h, p.state);
    if (!pt || !Number.isFinite(pt.x) || !Number.isFinite(pt.y)) return null;
    if (pt.x < 25 || pt.x > 940 || pt.y < 50 || pt.y > 560) return null;
    return pt;
  }

  /** Group venues whose map dots would sit on top of each other. */
  function buildClusters(list) {
    const items = [];
    for (const p of list) {
      const xy = pinXY(p);
      if (!xy) continue;
      items.push({ p, x: xy.x, y: xy.y });
    }
    // ~28px in SVG space; slightly tighter when zoomed in
    const thresh = zoom >= 2 ? 14 : zoom >= 1.4 ? 20 : 28;
    const used = new Array(items.length).fill(false);
    const clusters = [];
    for (let i = 0; i < items.length; i++) {
      if (used[i]) continue;
      const group = [items[i]];
      used[i] = true;
      for (let j = i + 1; j < items.length; j++) {
        if (used[j]) continue;
        const dx = items[i].x - items[j].x;
        const dy = items[i].y - items[j].y;
        if (dx * dx + dy * dy <= thresh * thresh) {
          used[j] = true;
          group.push(items[j]);
        }
      }
      // also merge if any member close to group centroid iteratively
      let changed = true;
      while (changed) {
        changed = false;
        const cx = group.reduce((s, g) => s + g.x, 0) / group.length;
        const cy = group.reduce((s, g) => s + g.y, 0) / group.length;
        for (let j = 0; j < items.length; j++) {
          if (used[j]) continue;
          const dx = cx - items[j].x;
          const dy = cy - items[j].y;
          if (dx * dx + dy * dy <= thresh * thresh) {
            used[j] = true;
            group.push(items[j]);
            changed = true;
          }
        }
      }
      const cx = group.reduce((s, g) => s + g.x, 0) / group.length;
      const cy = group.reduce((s, g) => s + g.y, 0) / group.length;
      const places = group.map((g) => g.p).sort((a, b) => a.name.localeCompare(b.name));
      clusters.push({ x: cx, y: cy, places, ids: places.map((p) => p.id) });
    }
    return clusters;
  }

  function renderPins() {
    if (!svgEl || !pinsLayer) return;
    while (pinsLayer.firstChild) pinsLayer.removeChild(pinsLayer.firstChild);
    svgEl.querySelectorAll(".city-pin").forEach((el) => {
      el.style.display = "none";
    });

    const list = filteredPlaces();
    const clusters = buildClusters(list);
    const NS = "http://www.w3.org/2000/svg";
    const focusSet = new Set(clusterFocusIds);

    for (const cl of clusters) {
      const n = cl.places.length;
      const selectedHere =
        (selectedVenueId && cl.ids.includes(selectedVenueId)) ||
        (focusSet.size && cl.ids.some((id) => focusSet.has(id)));
      const x = cl.x;
      const y = cl.y;

      const g = document.createElementNS(NS, "g");
      g.setAttribute(
        "class",
        "venue-pin" +
          (selectedHere ? " selected" : "") +
          (n > 1 ? " is-cluster" : "")
      );
      g.setAttribute("tabindex", "0");
      g.setAttribute("role", "button");
      g.setAttribute(
        "aria-label",
        n > 1
          ? `${n} places near ${cl.places[0].city || "here"}`
          : cl.places[0].name
      );
      g.dataset.clusterIds = cl.ids.join(",");
      g.style.cursor = "pointer";

      const halo = document.createElementNS(NS, "circle");
      halo.setAttribute("class", "vpin-halo");
      halo.setAttribute("cx", x);
      halo.setAttribute("cy", y);
      halo.setAttribute("r", n > 1 ? "18" : mapScope === "more" ? "12" : "16");
      g.appendChild(halo);

      const core = document.createElementNS(NS, "circle");
      core.setAttribute("class", "vpin-core");
      core.setAttribute("cx", x);
      core.setAttribute("cy", y);
      core.setAttribute("r", n > 1 ? "11" : selectedHere ? "8" : mapScope === "more" ? "5" : "7");
      g.appendChild(core);

      if (n > 1) {
        const count = document.createElementNS(NS, "text");
        count.setAttribute("class", "vpin-count");
        count.setAttribute("x", x);
        count.setAttribute("y", y + 4);
        count.setAttribute("text-anchor", "middle");
        count.textContent = String(n);
        g.appendChild(count);
      }

      // Hover / selected name chip (single only; clusters open list in panel)
      const chip = document.createElementNS(NS, "g");
      const showChipSelected = selectedHere && n === 1;
      chip.setAttribute(
        "class",
        "vpin-chip" + (showChipSelected ? " vpin-chip-on is-visible" : "")
      );
      chip.setAttribute("transform", `translate(${x + 12}, ${y - 10})`);
      const hoverName =
        n > 1
          ? `${n} places · ${cl.places[0].city || "area"}`
          : `${cl.places[0].emoji || "•"} ${
              cl.places[0].name.length > 26
                ? cl.places[0].name.slice(0, 24) + "…"
                : cl.places[0].name
            }`;
      const textW = Math.min(210, 12 + hoverName.length * 6.2 + (showChipSelected ? 18 : 0));
      const bg = document.createElementNS(NS, "rect");
      bg.setAttribute("class", "vpin-chip-bg");
      bg.setAttribute("x", "0");
      bg.setAttribute("y", "-12");
      bg.setAttribute("rx", "8");
      bg.setAttribute("ry", "8");
      bg.setAttribute("width", String(textW));
      bg.setAttribute("height", "22");
      chip.appendChild(bg);
      const label = document.createElementNS(NS, "text");
      label.setAttribute("class", "vpin-label" + (showChipSelected ? " vpin-label-on" : ""));
      label.setAttribute("x", "6");
      label.setAttribute("y", "4");
      label.textContent = hoverName;
      chip.appendChild(label);

      if (showChipSelected) {
        const dismiss = document.createElementNS(NS, "g");
        dismiss.setAttribute("class", "vpin-dismiss");
        dismiss.setAttribute("aria-label", "Clear selection");
        dismiss.style.cursor = "pointer";
        const dx = textW - 14;
        const dCircle = document.createElementNS(NS, "circle");
        dCircle.setAttribute("cx", String(dx));
        dCircle.setAttribute("cy", "0");
        dCircle.setAttribute("r", "8");
        dCircle.setAttribute("class", "vpin-dismiss-bg");
        const dX = document.createElementNS(NS, "text");
        dX.setAttribute("x", String(dx));
        dX.setAttribute("y", "4");
        dX.setAttribute("text-anchor", "middle");
        dX.setAttribute("class", "vpin-dismiss-x");
        dX.textContent = "×";
        dismiss.appendChild(dCircle);
        dismiss.appendChild(dX);
        const clear = (e) => {
          e.stopPropagation();
          e.preventDefault();
          setVenue("");
        };
        dismiss.addEventListener("click", clear);
        dismiss.addEventListener("pointerdown", (e) => e.stopPropagation());
        chip.appendChild(dismiss);
      }
      g.appendChild(chip);

      const showName = () => chip.classList.add("is-visible");
      const hideName = () => {
        if (!(selectedHere && n === 1)) chip.classList.remove("is-visible");
      };
      g.addEventListener("pointerenter", showName);
      g.addEventListener("pointerleave", hideName);
      g.addEventListener("focus", showName);
      g.addEventListener("blur", hideName);

      const activate = () => {
        if (n > 1) showClusterPicker(cl.places);
        else setVenue(cl.places[0].id, { fromPin: true });
      };

      g.addEventListener("click", (e) => {
        if (e.target.closest && e.target.closest(".vpin-dismiss")) return;
        e.stopPropagation();
        e.preventDefault();
        activate();
      });
      g.addEventListener("dblclick", (e) => {
        if (e.target.closest && e.target.closest(".vpin-dismiss")) return;
        e.stopPropagation();
        e.preventDefault();
        activate();
        zoomToClientPoint(e.clientX, e.clientY, Math.min(3.5, zoom + 0.75));
      });
      g.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          activate();
        }
      });
      pinsLayer.appendChild(g);
    }

    const sel = pinsLayer.querySelector(".venue-pin.selected");
    if (sel) pinsLayer.appendChild(sel);
  }

  function showClusterPicker(places) {
    clusterFocusIds = places.map((p) => p.id);
    selectedVenueId = "";
    fillVenueSelect();
    renderPins();
    const city = places[0].city || "this area";
    const area =
      places[0].region === "dfw" || ["Dallas", "Fort Worth"].includes(places[0].city)
        ? "Dallas–Fort Worth area"
        : city;
    detail.className = "pin-detail";
    detail.innerHTML = `
      <p class="pin-detail-kicker">A few places here</p>
      <div class="pd-title-row">
        <h3>${escapeHtml(area)}</h3>
        <button type="button" class="pd-clear" id="pd-clear-selection" aria-label="Clear">×</button>
      </div>
      <p class="pd-hint">Choose one to get a kid list and printable hunt.</p>
      <div class="nearby-list" role="listbox" aria-label="Places nearby">
        ${places
          .map(
            (p) => `
          <button type="button" class="nearby-item" data-venue-id="${escapeHtml(p.id)}" role="option">
            <span class="nearby-emoji">${escapeHtml(p.emoji || "📍")}</span>
            <span class="nearby-copy">
              <strong>${escapeHtml(p.name)}</strong>
              <small>${escapeHtml(p.city)}</small>
            </span>
            <span class="nearby-go">Choose →</span>
          </button>`
          )
          .join("")}
      </div>
    `;
    detail.querySelector("#pd-clear-selection")?.addEventListener("click", () => {
      clusterFocusIds = [];
      setVenue("");
    });
    detail.querySelectorAll(".nearby-item").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = btn.getAttribute("data-venue-id");
        clusterFocusIds = [];
        setVenue(id, { fromPin: true });
      });
    });
  }

  function showOverview() {
    const list = filteredPlaces();
    const scopeNote =
      mapScope === "top"
        ? `${list.length} popular places on the map`
        : `${list.length} places on the map`;
    detail.className = "pin-detail empty";
    detail.innerHTML = `
      <p class="pin-detail-kicker">What you get</p>
      <h3>Pick a place</h3>
      <p class="pd-hint">
        Tap a pin (or use the lists under the map). You’ll get a <strong>short kid list</strong> and a
        <strong>printable treasure hunt</strong> for that zoo, aquarium, or museum.
      </p>
      <p class="pd-meta">${escapeHtml(scopeNote)}. A number on a pin means several places share that spot — tap it to choose.</p>
    `;
  }

  function showVenueDetail(venueId) {
    const p = placeById(venueId);
    if (!p) {
      showOverview();
      return;
    }
    selectedVenueId = venueId;
    detail.className = "pin-detail";
    const blurb = (p.blurb || "").trim();
    const canPrintHunt =
      window.FPPrint &&
      typeof window.fpGetVenue === "function" &&
      window.fpGetVenue(venueId) &&
      (window.fpGetVenue(venueId).treasureHunt || []).length > 0;
    detail.innerHTML = `
      <p class="pin-detail-kicker">${escapeHtml(p.city)}, ${escapeHtml(p.state)}</p>
      <div class="pd-title-row">
        <h3>${escapeHtml(p.emoji || "")} ${escapeHtml(p.name)}</h3>
        <button type="button" class="pd-clear" id="pd-clear-selection" aria-label="Clear selection">×</button>
      </div>
      ${blurb ? `<p class="pd-blurb">${escapeHtml(blurb)}</p>` : ""}
      <p class="pd-hint">Print a one-page hunt for the bag, or open the full kid list.</p>
      <div class="pd-actions">
        ${
          canPrintHunt
            ? `<button type="button" class="btn btn-primary" id="pd-print-hunt">🖨️ Print treasure hunt</button>`
            : ""
        }
        <a class="btn ${canPrintHunt ? "btn-secondary" : "btn-primary"}" href="${p.appHref || "#"}">Get kid list &amp; hunt →</a>
        <a class="btn btn-ghost" href="${p.href || "#"}">About this place</a>
      </div>
    `;
    detail.querySelector("#pd-clear-selection")?.addEventListener("click", () => setVenue(""));
    detail.querySelector("#pd-print-hunt")?.addEventListener("click", () => {
      if (window.FPPrint && window.FPPrint.printTreasureForVenue(venueId)) return;
      // Fallback: open outing if print kit unavailable
      location.href = p.appHref || `/field-pack/app.html#/venue/${encodeURIComponent(venueId)}`;
    });
  }

  function setVenue(venueId, opts = {}) {
    if (!venueId) {
      selectedVenueId = "";
      clusterFocusIds = [];
      fillVenueSelect();
      renderPins();
      showOverview();
      return;
    }
    clusterFocusIds = [];
    selectedVenueId = venueId;
    const p = placeById(venueId);
    // Don't call setScope (resets selection) — just flip mode quietly if needed
    if (p && mapScope === "top" && !(TOP_IDS.has(p.id) || p.tier === "top")) {
      mapScope = "more";
      scopeTop?.setAttribute("aria-pressed", "false");
      scopeMore?.setAttribute("aria-pressed", "true");
      scopeTop?.classList.remove("active");
      scopeMore?.classList.add("active");
      fillLocationSelect();
    }
    if (p && mapScope === "more" && selectedState && p.state !== selectedState) {
      selectedState = p.state;
      if (stateSelect) stateSelect.value = selectedState;
    }
    fillVenueSelect();
    venueSelect.value = venueId;
    showVenueDetail(venueId);
    renderPins();
  }

  function setScope(scope) {
    mapScope = scope === "more" ? "more" : "top";
    selectedVenueId = "";
    selectedMetroId = "all";
    selectedState = "";
    if (scopeTop) scopeTop.setAttribute("aria-pressed", mapScope === "top" ? "true" : "false");
    if (scopeMore) scopeMore.setAttribute("aria-pressed", mapScope === "more" ? "true" : "false");
    scopeTop?.classList.toggle("active", mapScope === "top");
    scopeMore?.classList.toggle("active", mapScope === "more");
    fillLocationSelect();
    fillVenueSelect();
    renderPins();
    showOverview();
    if (mapScope === "more" && zoom < 1.2) setZoom(1.15);
    if (mapScope === "top") setZoom(1);
  }

  async function boot() {
    if (scopeTop) scopeTop.addEventListener("click", () => setScope("top"));
    if (scopeMore) scopeMore.addEventListener("click", () => setScope("more"));
    citySelect.addEventListener("change", () => {
      selectedMetroId = citySelect.value || "all";
      selectedVenueId = "";
      // Metro and State are alternatives — picking a metro clears state
      if (selectedMetroId && selectedMetroId !== "all" && selectedState) {
        selectedState = "";
        if (stateSelect) stateSelect.value = "";
      }
      if (selectedMetroId && selectedMetroId !== "all") {
        // Metro filter uses Popular-style metro defs; stay on top unless All places
        // already active with no state
      }
      fillLocationSelect();
      fillVenueSelect();
      renderPins();
      showOverview();
    });
    if (stateSelect) {
      stateSelect.addEventListener("change", () => {
        selectedState = (stateSelect.value || "").trim();
        selectedVenueId = "";
        // Picking a state always means full catalog for that state (not Popular top-N)
        if (selectedState) {
          selectedMetroId = "all";
          ensureAllPlacesScope();
        }
        fillLocationSelect();
        fillVenueSelect();
        renderPins();
        showOverview();
        if (selectedState) setZoom(Math.max(zoom, 1.6));
        else setZoom(mapScope === "more" ? 1.15 : 1);
      });
    }
    venueSelect.addEventListener("change", () => setVenue(venueSelect.value));

    btnZoomIn?.addEventListener("click", () => {
      if (!mapViewport) return setZoom(zoom + 0.35);
      const r = mapViewport.getBoundingClientRect();
      zoomToClientPoint(r.left + r.width / 2, r.top + r.height / 2, zoom + 0.35);
    });
    btnZoomOut?.addEventListener("click", () => {
      if (!mapViewport) return setZoom(zoom - 0.35);
      const r = mapViewport.getBoundingClientRect();
      zoomToClientPoint(r.left + r.width / 2, r.top + r.height / 2, zoom - 0.35);
    });
    btnZoomReset?.addEventListener("click", () => setZoom(1));

    // Double-click empty map: zoom in centered on that point (no drag-pan)
    mapViewport?.addEventListener("dblclick", (e) => {
      if (e.target.closest && e.target.closest(".venue-pin")) return;
      e.preventDefault();
      zoomToClientPoint(e.clientX, e.clientY, Math.min(3.5, zoom + 0.75));
    });

    // Wheel zoom toward cursor only — dragging disabled (left the USA / felt broken)
    mapViewport?.addEventListener(
      "wheel",
      (e) => {
        e.preventDefault();
        zoomToClientPoint(e.clientX, e.clientY, zoom + (e.deltaY < 0 ? 0.15 : -0.15));
      },
      { passive: false }
    );

    try {
      const res = await fetch("/field-pack/img/usa-map.svg?v=5");
      const svgText = await res.text();
      mapHost.innerHTML = svgText;
      svgEl = mapHost.querySelector("svg");
      if (svgEl) {
        svgEl.removeAttribute("width");
        svgEl.removeAttribute("height");
        svgEl.setAttribute("class", "usa-real-map");
        svgEl.style.transition = "transform 0.15s ease";
        const NS = "http://www.w3.org/2000/svg";
        pinsLayer = document.createElementNS(NS, "g");
        pinsLayer.setAttribute("id", "venue-pins-layer");
        svgEl.appendChild(pinsLayer);
      }
    } catch (err) {
      mapHost.innerHTML = `<p class="map-loading">Map unavailable — use the menus.</p>`;
      console.error(err);
    }

    fillLocationSelect();
    fillVenueSelect();
    renderPins();
    showOverview();
    scopeTop?.classList.add("active");
  }

  boot();
})();
