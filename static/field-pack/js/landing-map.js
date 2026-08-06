(() => {
  const allPlaces = window.FP_PLACES || [];
  const TOP_IDS = new Set(window.FP_TOP_PLACE_IDS || []);
  const INTL_IDS = new Set(window.FP_INTL_PLACE_IDS || []);
  const detail = document.getElementById("pin-detail");
  const mapHost = document.getElementById("map-host");
  const citySelect = document.getElementById("city-select");
  const venueSelect = document.getElementById("venue-select-landing");
  const scopeTop = document.getElementById("scope-top");
  const scopeMore = document.getElementById("scope-more");
  const scopeIntl = document.getElementById("scope-intl");
  const stateSelect = document.getElementById("state-select");
  const stateField = document.getElementById("state-field");
  const metroField = document.getElementById("metro-field");
  const filterOr = document.querySelector(".filter-or");
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

  let mapScope = "more"; // top | more | intl — default: all US places
  let basemap = "us"; // us | world — world only when International selected
  let mapLoadToken = 0;
  let selectedMetroId = "all";
  let selectedState = "";
  let selectedCountry = "";
  let selectedVenueId = "";
  let clusterFocusIds = []; // nearby group open in side panel
  let zoom = 1;
  let panX = 0;
  let panY = 0;
  let svgEl = null;
  let pinsLayer = null;

  function isUSPlace(p) {
    if (!p) return false;
    const c = (p.country || "US").toUpperCase();
    return c === "US" || c === "USA";
  }

  function isIntlPlace(p) {
    return Boolean(p) && !isUSPlace(p);
  }

  function placeRegionLabel(p) {
    if (!p) return "";
    if (isIntlPlace(p)) return p.countryName || p.country || "";
    return p.state || "";
  }

  function placeById(id) {
    return allPlaces.find((p) => p.id === id);
  }

  function placesInScope() {
    if (mapScope === "intl") {
      return allPlaces.filter(
        (p) => isIntlPlace(p) || INTL_IDS.has(p.id) || p.tier === "intl"
      );
    }
    const us = allPlaces.filter(isUSPlace);
    if (mapScope === "top") {
      return us.filter((p) => TOP_IDS.has(p.id) || p.tier === "top");
    }
    return us;
  }

  /**
   * Places for the Place dropdown + map pins.
   * US scopes never include international pins (wrong basemap).
   * A selected state always uses the FULL US catalog for that state (not Popular top-N).
   */
  function filteredPlaces() {
    let list;
    if (mapScope === "intl") {
      list = placesInScope();
      if (selectedCountry) {
        list = list.filter((p) => (p.country || "").toUpperCase() === selectedCountry);
      }
    } else if (selectedState) {
      // Full catalog for this state — ignore Popular/top tier cap
      list = allPlaces.filter((p) => isUSPlace(p) && p.state === selectedState);
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
      list = placesInScope(); // all US places
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
    const city = p.city === "Escondido" ? "San Diego area" : p.city;
    const region = placeRegionLabel(p);
    return region
      ? `${p.emoji || "📍"} ${p.name} — ${city}, ${region}`
      : `${p.emoji || "📍"} ${p.name} — ${city}`;
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
        .filter(isUSPlace)
        .map((p) => (p && typeof p.state === "string" ? p.state.trim() : ""))
        .filter(Boolean)
    );
    return [...set].sort((a, b) => a.localeCompare(b));
  }

  /** Distinct countries for international scope: [{code, name}] sorted by name. */
  function distinctCountries(list) {
    const map = new Map();
    for (const p of list || []) {
      if (!isIntlPlace(p)) continue;
      const code = (p.country || "").toUpperCase();
      if (!code) continue;
      if (!map.has(code)) {
        map.set(code, p.countryName || code);
      }
    }
    return [...map.entries()]
      .map(([code, name]) => ({ code, name }))
      .sort((a, b) => a.name.localeCompare(b.name));
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
  function setStateFieldLabel(text) {
    const label = stateField && stateField.querySelector(".select-label");
    if (label) label.textContent = text;
    if (stateSelect) {
      stateSelect.setAttribute("aria-label", text === "Country" ? "Filter by country" : "Filter by state");
    }
  }

  function fillCountrySelectOptions() {
    const countries = distinctCountries(placesInScope());
    if (!stateSelect) return countries;
    const prev = selectedCountry;
    clearSelect(stateSelect);
    const o0 = document.createElement("option");
    o0.value = "";
    o0.textContent = "All countries";
    stateSelect.appendChild(o0);
    for (const c of countries) {
      const o = document.createElement("option");
      o.value = c.code;
      o.textContent = c.name;
      stateSelect.appendChild(o);
    }
    if (prev && countries.some((c) => c.code === prev)) {
      selectedCountry = prev;
      stateSelect.value = prev;
    } else {
      selectedCountry = "";
      stateSelect.value = "";
    }
    return countries;
  }

  function fillLocationSelect() {
    if (!citySelect) return;

    if (mapScope === "intl") {
      if (metroField) metroField.hidden = true;
      if (filterOr) filterOr.hidden = true;
      if (citySelect) citySelect.disabled = true;
      setStateFieldLabel("Country");
      const countries = fillCountrySelectOptions();
      if (stateField) stateField.hidden = countries.length === 0;
      return;
    }

    // US scopes: Metro + State
    if (metroField) metroField.hidden = false;
    if (filterOr) filterOr.hidden = false;
    setStateFieldLabel("State");
    selectedCountry = "";

    const states = fillStateSelectOptions();

    // Never show an empty state control; never hide metro (layout must stay fixed)
    if (stateField) {
      stateField.hidden = states.length === 0;
    }
    if (!states.length) {
      selectedState = "";
    }

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
      const usCount = allPlaces.filter(isUSPlace).length;
      const topN = allPlaces.filter((p) => isUSPlace(p) && (TOP_IDS.has(p.id) || p.tier === "top")).length;
      if (mapScope === "intl") {
        const readyN = list.filter((p) => p.status === "ready").length;
        if (selectedCountry) {
          const name =
            (list[0] && list[0].countryName) ||
            selectedCountry;
          mapCount.textContent =
            readyN > 0
              ? `International · ${list.length} in ${name} (${readyN} ready to print)`
              : `International · ${list.length} places in ${name}`;
        } else {
          mapCount.textContent =
            readyN > 0
              ? `International · ${list.length} on the world map · ${readyN} ready to print`
              : `International · ${list.length} places on the world map`;
        }
      } else if (selectedState) {
        mapCount.textContent = `Showing all ${list.length} places in ${selectedState} — pick one below or tap a pin`;
      } else if (mapScope === "top") {
        mapCount.textContent = `Showing ${topN} popular places — switch to “All places” for more`;
      } else {
        mapCount.textContent = `Showing ${usCount} places — tap a pin or pick from the lists`;
      }
    }
  }

  /** Ensure UI is on All places so state filter can show, without wiping selectedState. */
  function ensureAllPlacesScope() {
    if (mapScope === "more") return;
    if (mapScope === "intl") return; // don't yank off world map for US state filter
    mapScope = "more";
    selectedMetroId = "all";
    updateScopeButtons();
  }

  function updateScopeButtons() {
    const isTop = mapScope === "top";
    const isMore = mapScope === "more";
    const isIntl = mapScope === "intl";
    if (scopeTop) {
      scopeTop.setAttribute("aria-pressed", isTop ? "true" : "false");
      scopeTop.classList.toggle("active", isTop);
    }
    if (scopeMore) {
      scopeMore.setAttribute("aria-pressed", isMore ? "true" : "false");
      scopeMore.classList.toggle("active", isMore);
    }
    if (scopeIntl) {
      scopeIntl.setAttribute("aria-pressed", isIntl ? "true" : "false");
      scopeIntl.classList.toggle("active", isIntl);
    }
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
    if (basemap === "world") {
      const w = (vb && vb.width) || 1000;
      const h = (vb && vb.height) || 500;
      if (typeof window.fpProjectWorld !== "function") return null;
      const pt = window.fpProjectWorld(p.lat, p.lon, w, h);
      if (!pt || !Number.isFinite(pt.x) || !Number.isFinite(pt.y)) return null;
      if (pt.x < 4 || pt.x > w - 4 || pt.y < 4 || pt.y > h - 4) return null;
      return pt;
    }
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
              <small>${escapeHtml([p.city, placeRegionLabel(p)].filter(Boolean).join(", "))}</small>
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
      mapScope === "intl"
        ? `${list.length} international places on the world map`
        : mapScope === "top"
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

  function catalogVenue(venueId) {
    return typeof window.fpGetVenue === "function" ? window.fpGetVenue(venueId) : null;
  }

  function catalogItem(itemId) {
    return (window.FIELD_PACK_CATALOG && window.FIELD_PACK_CATALOG[itemId]) || null;
  }

  function sampleItemForVenue(venueId) {
    const ven = catalogVenue(venueId);
    if (!ven) return null;
    const topId =
      (window.FPPrint && window.FPPrint.topPickItemId && window.FPPrint.topPickItemId(ven)) ||
      (ven.featuredAnimalIds && ven.featuredAnimalIds[0]) ||
      (ven.animalIds && ven.animalIds[0]) ||
      null;
    return topId ? catalogItem(topId) : null;
  }

  function photoSrc(photo) {
    if (!photo) return "";
    if (photo.startsWith("http") || photo.startsWith("/")) return photo;
    return `/field-pack/${photo}`;
  }

  function syncVenueHash(venueId) {
    const next = venueId ? `#/venue/${encodeURIComponent(venueId)}` : "#us-map";
    if (location.hash !== next) {
      history.replaceState(null, "", next);
    }
  }

  function venueIdFromHash() {
    const m = (location.hash || "").match(/^#\/venue\/([^/?#]+)/);
    return m ? decodeURIComponent(m[1]) : "";
  }

  function showVenueDetail(venueId) {
    const p = placeById(venueId);
    if (!p) {
      showOverview();
      return;
    }
    selectedVenueId = venueId;
    detail.className = "pin-detail pin-detail-rich";
    const blurb = (p.blurb || "").trim();
    const ven = catalogVenue(venueId);
    const canPrintHunt = Boolean(ven && (ven.treasureHunt || []).length);
    const sample = sampleItemForVenue(venueId);
    const samplePhoto = sample ? photoSrc(sample.photo) : "";
    const appHref = p.appHref || `/field-pack/app.html#/venue/${encodeURIComponent(venueId)}`;

    const sampleCard = sample
      ? `<button type="button" class="pd-sample-card" id="pd-print-sample" aria-label="Print sample Q&A card for ${escapeHtml(sample.name)}">
          ${
            samplePhoto
              ? `<img src="${escapeHtml(samplePhoto)}" alt="${escapeHtml(sample.name)} — sample find" width="320" height="200" loading="lazy" decoding="async" />`
              : `<span class="pd-sample-fallback" aria-hidden="true">${escapeHtml(sample.emoji || "⭐")}</span>`
          }
          <span class="pd-sample-body">
            <span class="pd-sample-kicker">Sample Q&amp;A card</span>
            <span class="pd-sample-name">${escapeHtml(sample.emoji || "")} ${escapeHtml(sample.name)}</span>
            <span class="pd-sample-blurb">${escapeHtml(sample.blurb || "Tap to print a one-page sample card.")}</span>
            <span class="pd-sample-cta">Tap to print this card →</span>
          </span>
        </button>`
      : "";

    const locLine = [p.city, placeRegionLabel(p)].filter(Boolean).join(", ");
    const isSoon = p.status === "soon";
    const statusBadge = isSoon
      ? `<span class="pd-status soon">Coming soon</span>`
      : canPrintHunt
        ? `<span class="pd-status ready">Ready to print</span>`
        : "";
    detail.innerHTML = `
      <p class="pin-detail-kicker">${escapeHtml(locLine)}</p>
      <div class="pd-title-row">
        <h3>${escapeHtml(p.emoji || "")} ${escapeHtml(p.name)}</h3>
        <button type="button" class="pd-clear" id="pd-clear-selection" aria-label="Clear selection">×</button>
      </div>
      ${statusBadge}
      ${blurb ? `<p class="pd-blurb">${escapeHtml(blurb)}</p>` : ""}
      ${
        isSoon
          ? `<p class="pd-hint">International pack in progress — shortlist and printable hunt coming next.</p>`
          : ""
      }
      <div class="pd-actions">
        ${
          !isSoon && canPrintHunt
            ? `<button type="button" class="btn btn-primary" id="pd-print-hunt">One-page hunt to print</button>`
            : ""
        }
      </div>
      ${isSoon ? "" : sampleCard}
      ${
        !isSoon && sample
          ? `<p class="pd-more-hint">More cards in the full list</p>`
          : ""
      }
      ${
        isSoon
          ? ""
          : `<div class="pd-actions pd-actions-secondary">
        <a class="btn btn-secondary" href="${appHref}">Open full list →</a>
      </div>`
      }
    `;
    detail.querySelector("#pd-clear-selection")?.addEventListener("click", () => setVenue(""));
    detail.querySelector("#pd-print-hunt")?.addEventListener("click", () => {
      if (window.FPPrint && window.FPPrint.printTreasureForVenue(venueId)) return;
      location.href = appHref;
    });
    detail.querySelector("#pd-print-sample")?.addEventListener("click", () => {
      if (window.FPPrint && window.FPPrint.printSampleQaForVenue(venueId)) return;
      location.href = appHref;
    });
  }

  async function setVenue(venueId, opts = {}) {
    const skipHash = opts.skipHash === true;
    if (!venueId) {
      selectedVenueId = "";
      clusterFocusIds = [];
      fillVenueSelect();
      renderPins();
      showOverview();
      if (!skipHash) syncVenueHash("");
      return;
    }
    clusterFocusIds = [];
    selectedVenueId = venueId;
    const p = placeById(venueId);

    // Deep-link / pin: switch basemap only when needed (US default stays until intl)
    if (p && isIntlPlace(p) && mapScope !== "intl") {
      mapScope = "intl";
      selectedMetroId = "all";
      selectedState = "";
      selectedCountry = (p.country || "").toUpperCase();
      updateScopeButtons();
      await loadBasemap("world");
    } else if (p && isUSPlace(p) && mapScope === "intl") {
      mapScope = "more";
      selectedCountry = "";
      updateScopeButtons();
      await loadBasemap("us");
    } else if (p && mapScope === "top" && isUSPlace(p) && !(TOP_IDS.has(p.id) || p.tier === "top")) {
      // Don't call setScope (resets selection) — just flip mode quietly if needed
      mapScope = "more";
      updateScopeButtons();
      fillLocationSelect();
    }

    if (p && mapScope === "intl" && p.country) {
      selectedCountry = (p.country || "").toUpperCase();
      if (stateSelect) stateSelect.value = selectedCountry;
    }
    if (p && mapScope !== "intl" && selectedState && p.state && p.state !== selectedState) {
      selectedState = p.state;
      if (stateSelect) stateSelect.value = selectedState;
    }
    fillLocationSelect();
    fillVenueSelect();
    venueSelect.value = venueId;
    showVenueDetail(venueId);
    renderPins();
    if (!skipHash) syncVenueHash(venueId);
    if (opts.scroll !== false) {
      document.getElementById("us-map")?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  // Allow ready-cards / external links: /field-pack/#/venue/dallas-zoo
  window.fpSelectVenueOnMap = (id) => {
    void setVenue(id);
  };

  async function loadBasemap(kind) {
    const next = kind === "world" ? "world" : "us";
    const token = ++mapLoadToken;
    const url =
      next === "world"
        ? "/field-pack/img/world-map.svg?v=1"
        : "/field-pack/img/usa-map.svg?v=5";
    if (mapHost) {
      mapHost.innerHTML = `<p class="map-loading">Loading map…</p>`;
      mapHost.setAttribute("aria-label", next === "world" ? "World map" : "United States map");
    }
    try {
      const res = await fetch(url);
      const svgText = await res.text();
      if (token !== mapLoadToken) return;
      mapHost.innerHTML = svgText;
      svgEl = mapHost.querySelector("svg");
      if (svgEl) {
        svgEl.removeAttribute("width");
        svgEl.removeAttribute("height");
        svgEl.setAttribute(
          "class",
          next === "world" ? "world-real-map usa-real-map" : "usa-real-map"
        );
        svgEl.style.transition = "transform 0.15s ease";
        const NS = "http://www.w3.org/2000/svg";
        pinsLayer = document.createElementNS(NS, "g");
        pinsLayer.setAttribute("id", "venue-pins-layer");
        svgEl.appendChild(pinsLayer);
      }
      basemap = next;
      panX = 0;
      panY = 0;
      zoom = 1;
      applyMapTransform();
    } catch (err) {
      if (token !== mapLoadToken) return;
      mapHost.innerHTML = `<p class="map-loading">Map unavailable — use the menus.</p>`;
      console.error(err);
      svgEl = null;
      pinsLayer = null;
    }
  }

  async function setScope(scope) {
    const next = scope === "intl" ? "intl" : scope === "more" ? "more" : "top";
    const wasIntl = mapScope === "intl";
    const willIntl = next === "intl";
    mapScope = next;
    selectedVenueId = "";
    selectedMetroId = "all";
    selectedState = "";
    selectedCountry = "";
    clusterFocusIds = [];
    updateScopeButtons();

    if (wasIntl !== willIntl) {
      await loadBasemap(willIntl ? "world" : "us");
    }

    fillLocationSelect();
    fillVenueSelect();
    renderPins();
    showOverview();
    if (mapScope === "more" && basemap === "us") setZoom(1.15);
    else setZoom(1);
  }

  async function boot() {
    if (scopeTop) scopeTop.addEventListener("click", () => void setScope("top"));
    if (scopeMore) scopeMore.addEventListener("click", () => void setScope("more"));
    if (scopeIntl) scopeIntl.addEventListener("click", () => void setScope("intl"));
    citySelect.addEventListener("change", () => {
      if (mapScope === "intl") return;
      selectedMetroId = citySelect.value || "all";
      selectedVenueId = "";
      // Metro and State are alternatives — picking a metro clears state
      if (selectedMetroId && selectedMetroId !== "all" && selectedState) {
        selectedState = "";
        if (stateSelect) stateSelect.value = "";
      }
      fillLocationSelect();
      fillVenueSelect();
      renderPins();
      showOverview();
    });
    if (stateSelect) {
      stateSelect.addEventListener("change", () => {
        selectedVenueId = "";
        if (mapScope === "intl") {
          selectedCountry = (stateSelect.value || "").trim().toUpperCase();
          fillLocationSelect();
          fillVenueSelect();
          renderPins();
          showOverview();
          if (selectedCountry) setZoom(Math.max(zoom, 1.8));
          else setZoom(1);
          return;
        }
        selectedState = (stateSelect.value || "").trim();
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
    venueSelect.addEventListener("change", () => void setVenue(venueSelect.value));

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

    // Default: US map + All places (never world until International is clicked)
    await loadBasemap("us");
    mapScope = "more";
    updateScopeButtons();
    fillLocationSelect();
    fillVenueSelect();
    renderPins();
    showOverview();
    if (zoom < 1.2) setZoom(1.15);

    // Deep link: /field-pack/#/venue/dallas-zoo (intl ids switch basemap)
    const fromHash = venueIdFromHash();
    if (fromHash && placeById(fromHash)) {
      await setVenue(fromHash, { skipHash: true, scroll: true });
    }
    window.addEventListener("hashchange", () => {
      const id = venueIdFromHash();
      if (id && placeById(id)) {
        if (id !== selectedVenueId) void setVenue(id, { skipHash: true, scroll: true });
      } else if (!id && selectedVenueId) {
        void setVenue("", { skipHash: true });
      }
    });
  }

  boot();
})();
