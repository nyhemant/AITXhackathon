(() => {
  const places = window.FP_PLACES || [];
  const detail = document.getElementById("pin-detail");
  const mapHost = document.getElementById("map-host");
  const citySelect = document.getElementById("city-select");
  const venueSelect = document.getElementById("venue-select-landing");

  /**
   * City options for the dropdown.
   * placeIds = venues in that city's vicinity (Dallas includes Fort Worth).
   * mapPinId = matching pin on the SVG (optional).
   */
  const CITY_DEFS = [
    {
      id: "all",
      label: "All cities",
      kidLine: "Everywhere on our map",
      symbols: "🇺🇸",
      status: "ready",
      placeIds: null, // all
      mapPinId: null,
    },
    {
      id: "dallas",
      label: "Dallas area",
      kidLine: "Zoo · Aquarium · Museum · nearby Fort Worth Zoo",
      symbols: "🦁🦈🎨",
      status: "ready",
      // Vicinity: Dallas venues + Fort Worth Zoo
      placeIds: [
        "dallas-zoo",
        "childrens-aquarium-dallas",
        "childrens-museum-perot",
        "fort-worth-zoo",
      ],
      mapPinId: "dfw",
    },
    {
      id: "austin",
      label: "Austin",
      kidLine: "Museum · Zoo",
      symbols: "🔬🦒",
      status: "soon",
      placeIds: ["thinkery", "austin-zoo"],
      mapPinId: "austin",
    },
    {
      id: "san-antonio",
      label: "San Antonio",
      kidLine: "Museum",
      symbols: "🧩",
      status: "soon",
      placeIds: ["doseum"],
      mapPinId: "san-antonio",
    },
    {
      id: "houston",
      label: "Houston",
      kidLine: "Zoo",
      symbols: "🐘",
      status: "soon",
      placeIds: ["houston-zoo"],
      mapPinId: "houston",
    },
    {
      id: "san-diego",
      label: "San Diego",
      kidLine: "Zoo · Safari",
      symbols: "🐼🦏",
      status: "soon",
      placeIds: ["san-diego-zoo", "san-diego-safari-park"],
      mapPinId: "san-diego",
    },
    {
      id: "la",
      label: "Los Angeles",
      kidLine: "Zoo · Aquarium · Science",
      symbols: "🦅🦭🛰️",
      status: "soon",
      placeIds: ["la-zoo", "aquarium-of-the-pacific", "california-science-center"],
      mapPinId: "la",
    },
    {
      id: "monterey",
      label: "Monterey",
      kidLine: "Aquarium",
      symbols: "🌊",
      status: "soon",
      placeIds: ["monterey-bay-aquarium"],
      mapPinId: "monterey",
    },
    {
      id: "sf",
      label: "San Francisco",
      kidLine: "Science",
      symbols: "🌿",
      status: "soon",
      placeIds: ["cal-academy"],
      mapPinId: "sf",
    },
    {
      id: "chicago",
      label: "Chicago",
      kidLine: "Aquarium · Museum",
      symbols: "🐠🦖",
      status: "soon",
      placeIds: ["shedd-aquarium", "field-museum"],
      mapPinId: "chicago",
    },
    {
      id: "indy",
      label: "Indianapolis",
      kidLine: "Museum",
      symbols: "🚀",
      status: "soon",
      placeIds: ["indy-childrens-museum"],
      mapPinId: "indy",
    },
    {
      id: "atlanta",
      label: "Atlanta",
      kidLine: "Aquarium",
      symbols: "🐋",
      status: "soon",
      placeIds: ["georgia-aquarium"],
      mapPinId: "atlanta",
    },
    {
      id: "dc",
      label: "Washington, DC",
      kidLine: "Zoo",
      symbols: "🦥",
      status: "soon",
      placeIds: ["national-zoo"],
      mapPinId: "dc",
    },
    {
      id: "nyc",
      label: "New York",
      kidLine: "Museum · Zoo",
      symbols: "🦴🦍",
      status: "soon",
      placeIds: ["amnh", "bronx-zoo"],
      mapPinId: "nyc",
    },
    {
      id: "florida",
      label: "Florida Space",
      kidLine: "Rockets",
      symbols: "🚀",
      status: "soon",
      placeIds: ["kennedy-space-center"],
      mapPinId: "florida",
    },
  ];

  // Map pin id (on SVG) → city dropdown id
  const PIN_TO_CITY = {
    dfw: "dallas",
    "fort-worth": "dallas", // pin still exists; selecting it focuses Dallas area (vicinity)
    austin: "austin",
    "san-antonio": "san-antonio",
    houston: "houston",
    "san-diego": "san-diego",
    la: "la",
    monterey: "monterey",
    sf: "sf",
    chicago: "chicago",
    indy: "indy",
    atlanta: "atlanta",
    dc: "dc",
    nyc: "nyc",
    florida: "florida",
  };

  let selectedCityId = "all";
  let selectedVenueId = "";

  function placeById(id) {
    return places.find((p) => p.id === id);
  }

  function cityById(id) {
    return CITY_DEFS.find((c) => c.id === id);
  }

  function venuesForCity(cityId) {
    const city = cityById(cityId);
    if (!city || city.id === "all" || !city.placeIds) {
      return [...places].sort((a, b) => {
        if (a.status !== b.status) return a.status === "ready" ? -1 : 1;
        return a.name.localeCompare(b.name);
      });
    }
    return city.placeIds.map(placeById).filter(Boolean);
  }

  function kidTypeLabel(type) {
    const t = (type || "").toLowerCase();
    if (t.includes("safari")) return "Safari zoo";
    if (t.includes("zoo")) return "Zoo";
    if (t.includes("aquarium")) return "Aquarium";
    if (t.includes("children")) return "Kids museum";
    if (t.includes("space")) return "Rockets / space";
    if (t.includes("science")) return "Science";
    if (t.includes("natural") || t.includes("history")) return "Nature museum";
    return type || "Place";
  }

  function venueOptionLabel(p) {
    // Kid-friendly: type + short city cue, official name secondary in data
    const kind = kidTypeLabel(p.type);
    const city = p.city === "Escondido" ? "San Diego area" : p.city;
    const ready = p.status === "ready" ? " ✓" : "";
    return `${p.emoji || "📍"} ${kind} — ${city}${ready}`;
  }

  function escapeHtml(s) {
    return String(s)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function fillCitySelect() {
    citySelect.innerHTML = "";
    for (const c of CITY_DEFS) {
      const opt = document.createElement("option");
      opt.value = c.id;
      const mark = c.status === "ready" && c.id !== "all" ? " ✓" : "";
      opt.textContent =
        c.id === "all" ? "All cities" : `${c.symbols} ${c.label}${mark}`;
      citySelect.appendChild(opt);
    }
    citySelect.value = selectedCityId;
  }

  function fillVenueSelect() {
    const list = venuesForCity(selectedCityId);
    venueSelect.innerHTML = "";
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent =
      selectedCityId === "all"
        ? "Pick a venue…"
        : `Venues near ${cityById(selectedCityId)?.label || "city"}…`;
    venueSelect.appendChild(placeholder);

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
  }

  function highlightMapPins() {
    const city = cityById(selectedCityId);
    const allowedPins = new Set();
    if (selectedCityId === "all") {
      Object.keys(PIN_TO_CITY).forEach((k) => allowedPins.add(k));
    } else if (city?.mapPinId) {
      allowedPins.add(city.mapPinId);
      // Dallas area also keeps fort-worth pin visible
      if (selectedCityId === "dallas") allowedPins.add("fort-worth");
    }

    document.querySelectorAll(".city-pin").forEach((el) => {
      const pinId = el.dataset.city;
      const on = allowedPins.has(pinId);
      el.classList.toggle("dim", !on);
      el.classList.toggle(
        "selected",
        selectedCityId !== "all" &&
          (pinId === city?.mapPinId ||
            (selectedCityId === "dallas" && (pinId === "dfw" || pinId === "fort-worth")))
      );
    });
  }

  function showCitySummary() {
    const city = cityById(selectedCityId);
    if (!city) return;
    const list = venuesForCity(selectedCityId);
    const readyN = list.filter((p) => p.status === "ready").length;

    if (selectedCityId === "all") {
      detail.className = "pin-detail";
      detail.innerHTML = `
        <p class="pin-detail-kicker">City filter</p>
        <h3>🇺🇸 All cities</h3>
        <p class="pd-meta">${list.length} venues on the map</p>
        <p class="pd-blurb">Pick a <strong>city</strong> to narrow the venue list, or choose a venue from the dropdown. Dallas area includes nearby Fort Worth Zoo.</p>
        <p class="pd-blurb"><strong>${readyN}</strong> ready to play now (Dallas).</p>
      `;
      return;
    }

    detail.className = "pin-detail";
    detail.innerHTML = `
      <p class="pin-detail-kicker">City selected</p>
      <h3>${escapeHtml(city.symbols)} ${escapeHtml(city.label)}</h3>
      <p class="pd-meta">${escapeHtml(city.kidLine)}</p>
      <span class="pd-status ${city.status}">${
        city.status === "ready" ? "Has ready venues" : "Coming soon"
      }</span>
      <p class="pd-blurb">
        Venue dropdown now shows <strong>only places near ${escapeHtml(city.label)}</strong>
        (${list.length} ${list.length === 1 ? "place" : "places"}).
        ${
          selectedCityId === "dallas"
            ? " Fort Worth Zoo is included because it’s in the Dallas area."
            : ""
        }
      </p>
      <p class="pd-blurb">Next: pick a venue in the dropdown → open its page.</p>
    `;
  }

  function showVenueDetail(venueId) {
    const p = placeById(venueId);
    if (!p) {
      showCitySummary();
      return;
    }
    selectedVenueId = venueId;
    const kind = kidTypeLabel(p.type);
    const ready = p.status === "ready";
    detail.className = "pin-detail";
    detail.innerHTML = `
      <p class="pin-detail-kicker">${escapeHtml(kind)} · ${escapeHtml(p.city)}</p>
      <h3>${escapeHtml(p.emoji || "")} ${escapeHtml(kind)}</h3>
      <p class="pd-meta">${escapeHtml(p.city)}, ${escapeHtml(p.state)}</p>
      <span class="pd-status ${p.status}">${ready ? "Ready to play" : "Coming soon"}</span>
      <p class="pd-blurb">${escapeHtml(p.blurb)}</p>
      <p class="pd-official">Official name: <span class="muted">${escapeHtml(p.name)}</span></p>
      <div class="pd-actions">
        <a class="btn btn-primary" href="${p.href}">Open place page →</a>
        ${
          ready && p.appHref
            ? `<a class="btn btn-secondary" href="${p.appHref}">Start outing</a>`
            : `<span class="btn btn-ghost" style="opacity:.7;pointer-events:none">Outing soon</span>`
        }
      </div>
    `;
  }

  function setCity(cityId, { fromPin } = {}) {
    if (!cityById(cityId)) cityId = "all";
    selectedCityId = cityId;
    citySelect.value = cityId;
    selectedVenueId = "";
    fillVenueSelect();
    highlightMapPins();
    showCitySummary();
  }

  function setVenue(venueId) {
    if (!venueId) {
      selectedVenueId = "";
      showCitySummary();
      return;
    }
    // If venue not in current city filter, switch city to one that contains it
    const list = venuesForCity(selectedCityId);
    if (!list.some((p) => p.id === venueId)) {
      const owner = CITY_DEFS.find(
        (c) => c.id !== "all" && c.placeIds && c.placeIds.includes(venueId)
      );
      if (owner) {
        selectedCityId = owner.id;
        citySelect.value = owner.id;
        fillVenueSelect();
        highlightMapPins();
      }
    }
    selectedVenueId = venueId;
    venueSelect.value = venueId;
    showVenueDetail(venueId);
  }

  function wirePins(root) {
    root.querySelectorAll(".city-pin").forEach((el) => {
      const pinId = el.dataset.city;
      const go = () => {
        const cityId = PIN_TO_CITY[pinId] || "all";
        setCity(cityId, { fromPin: true });
      };
      el.addEventListener("click", go);
      el.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          go();
        }
      });
    });
  }

  function fillCitySelect() {
    citySelect.innerHTML = "";
    for (const c of CITY_DEFS) {
      const opt = document.createElement("option");
      opt.value = c.id;
      if (c.id === "all") opt.textContent = "All cities";
      else {
        const mark = c.status === "ready" ? " ✓" : "";
        opt.textContent = `${c.symbols} ${c.label}${mark}`;
      }
      citySelect.appendChild(opt);
    }
  }

  async function boot() {
    fillCitySelect();
    fillVenueSelect();

    citySelect.addEventListener("change", () => setCity(citySelect.value));
    venueSelect.addEventListener("change", () => setVenue(venueSelect.value));

    try {
      const res = await fetch("/field-pack/img/usa-map.svg?v=3");
      const svgText = await res.text();
      mapHost.innerHTML = svgText;
      const svg = mapHost.querySelector("svg");
      if (svg) {
        svg.removeAttribute("width");
        svg.removeAttribute("height");
        svg.setAttribute("class", "usa-real-map");
        wirePins(svg);
      }
    } catch (err) {
      mapHost.innerHTML = `<p class="map-loading">Map failed to load — use the city and venue menus.</p>`;
      console.error(err);
    }

    setCity("all");
  }

  boot();
})();
