(() => {
  const places = window.FP_PLACES || [];
  const detail = document.getElementById("pin-detail");
  const grid = document.getElementById("places-grid");
  const mapHost = document.getElementById("map-host");

  let filter = "all";
  let selectedCityId = null;
  let cities = [];

  // City hubs for kid-friendly labels (loaded with map interaction)
  const CITY_DEFS = [
    {
      id: "dfw",
      label: "Dallas",
      kidLine: "Zoo · Aquarium · Museum",
      symbols: "🦁🦈🎨",
      status: "ready",
      placeIds: ["dallas-zoo", "childrens-aquarium-dallas", "childrens-museum-perot"],
    },
    {
      id: "fort-worth",
      label: "Fort Worth",
      kidLine: "Zoo",
      symbols: "🐯",
      status: "soon",
      placeIds: ["fort-worth-zoo"],
    },
    {
      id: "austin",
      label: "Austin",
      kidLine: "Museum · Zoo",
      symbols: "🔬🦒",
      status: "soon",
      placeIds: ["thinkery", "austin-zoo"],
    },
    {
      id: "san-antonio",
      label: "San Antonio",
      kidLine: "Museum",
      symbols: "🧩",
      status: "soon",
      placeIds: ["doseum"],
    },
    {
      id: "houston",
      label: "Houston",
      kidLine: "Zoo",
      symbols: "🐘",
      status: "soon",
      placeIds: ["houston-zoo"],
    },
    {
      id: "san-diego",
      label: "San Diego",
      kidLine: "Zoo · Safari",
      symbols: "🐼🦏",
      status: "soon",
      placeIds: ["san-diego-zoo", "san-diego-safari-park"],
    },
    {
      id: "la",
      label: "Los Angeles",
      kidLine: "Zoo · Aquarium · Science",
      symbols: "🦅🦭🛰️",
      status: "soon",
      placeIds: ["la-zoo", "aquarium-of-the-pacific", "california-science-center"],
    },
    {
      id: "monterey",
      label: "Monterey",
      kidLine: "Aquarium",
      symbols: "🌊",
      status: "soon",
      placeIds: ["monterey-bay-aquarium"],
    },
    {
      id: "sf",
      label: "San Francisco",
      kidLine: "Science",
      symbols: "🌿",
      status: "soon",
      placeIds: ["cal-academy"],
    },
    {
      id: "chicago",
      label: "Chicago",
      kidLine: "Aquarium · Museum",
      symbols: "🐠🦖",
      status: "soon",
      placeIds: ["shedd-aquarium", "field-museum"],
    },
    {
      id: "indy",
      label: "Indianapolis",
      kidLine: "Museum",
      symbols: "🚀",
      status: "soon",
      placeIds: ["indy-childrens-museum"],
    },
    {
      id: "atlanta",
      label: "Atlanta",
      kidLine: "Aquarium",
      symbols: "🐋",
      status: "soon",
      placeIds: ["georgia-aquarium"],
    },
    {
      id: "dc",
      label: "Washington, DC",
      kidLine: "Zoo",
      symbols: "🦥",
      status: "soon",
      placeIds: ["national-zoo"],
    },
    {
      id: "nyc",
      label: "New York",
      kidLine: "Museum · Zoo",
      symbols: "🦴🦍",
      status: "soon",
      placeIds: ["amnh", "bronx-zoo"],
    },
    {
      id: "florida",
      label: "Florida Space",
      kidLine: "Rockets",
      symbols: "🚀",
      status: "soon",
      placeIds: ["kennedy-space-center"],
    },
  ];

  function placeById(id) {
    return places.find((p) => p.id === id);
  }

  function cityPlaces(city) {
    return (city.placeIds || []).map(placeById).filter(Boolean);
  }

  function matchesFilter(city) {
    if (filter === "all") return true;
    if (filter === "ready") return city.status === "ready";
    if (filter === "soon") return city.status === "soon";
    if (filter === "tx") {
      return cityPlaces(city).some((p) => p.state === "TX");
    }
    return true;
  }

  function escapeHtml(s) {
    return String(s)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function selectCity(cityId) {
    selectedCityId = cityId;
    const city = CITY_DEFS.find((c) => c.id === cityId);
    document.querySelectorAll(".city-pin").forEach((el) => {
      el.classList.toggle("selected", el.dataset.city === cityId);
      el.classList.toggle("dim", !matchesFilter(CITY_DEFS.find((c) => c.id === el.dataset.city) || {}));
    });

    if (!city) return;
    const list = cityPlaces(city);
    const readyCount = list.filter((p) => p.status === "ready").length;
    const links = list
      .map((p) => {
        const badge = p.status === "ready" ? "Ready" : "Soon";
        const play =
          p.status === "ready" && p.appHref
            ? `<a class="btn btn-secondary btn-sm" href="${p.appHref}">Start</a>`
            : "";
        return `<li class="pd-place">
          <a href="${p.href}"><span class="pd-emoji">${escapeHtml(p.emoji || "")}</span>
          <span><strong>${escapeHtml(kidTypeLabel(p.type))}</strong><br/><span class="muted">${escapeHtml(
          p.name
        )}</span></span></a>
          <span class="pc-badge ${p.status}">${badge}</span>
          ${play}
        </li>`;
      })
      .join("");

    detail.className = "pin-detail";
    detail.innerHTML = `
      <p class="pin-detail-kicker">City adventure</p>
      <h3>${escapeHtml(city.symbols)} ${escapeHtml(city.label)}</h3>
      <p class="pd-meta">${escapeHtml(city.kidLine)}</p>
      <span class="pd-status ${city.status}">${
        city.status === "ready" ? "Ready to play" : "Coming soon"
      }</span>
      <p class="pd-blurb">Kid labels show the <strong>city</strong> and what kind of place — zoo, aquarium, museum, science, or rockets. Tap a place card below.</p>
      <ul class="pd-place-list">${links}</ul>
    `;
  }

  function kidTypeLabel(type) {
    const t = (type || "").toLowerCase();
    if (t.includes("zoo") && t.includes("safari")) return "Safari zoo";
    if (t.includes("zoo")) return "Zoo";
    if (t.includes("aquarium")) return "Aquarium";
    if (t.includes("children")) return "Kids museum";
    if (t.includes("science") || t.includes("space")) return t.includes("space") ? "Rockets / space" : "Science";
    if (t.includes("natural") || t.includes("history")) return "Nature museum";
    return type || "Place";
  }

  function renderGrid() {
    grid.innerHTML = "";
    const shownCities = CITY_DEFS.filter(matchesFilter);
    for (const city of shownCities) {
      const list = cityPlaces(city);
      for (const p of list) {
        const a = document.createElement("a");
        a.className = "place-card";
        a.href = p.href;
        a.innerHTML = `
          <div class="pc-top">
            <span class="pc-emoji">${escapeHtml(city.symbols)}</span>
            <span class="pc-badge ${p.status}">${p.status === "ready" ? "Ready" : "Soon"}</span>
          </div>
          <div class="pc-name">${escapeHtml(city.label)}</div>
          <div class="pc-city">${escapeHtml(kidTypeLabel(p.type))} · ${escapeHtml(p.city)}, ${escapeHtml(
          p.state
        )}</div>
          <div class="pc-blurb">${escapeHtml(p.blurb)}</div>
          <div class="pc-official muted">${escapeHtml(p.name)}</div>
        `;
        a.addEventListener("mouseenter", () => selectCity(city.id));
        grid.appendChild(a);
      }
    }
  }

  function wirePins(root) {
    root.querySelectorAll(".city-pin").forEach((el) => {
      const id = el.dataset.city;
      const city = CITY_DEFS.find((c) => c.id === id);
      if (!city) return;
      el.classList.toggle("dim", !matchesFilter(city));
      const go = () => selectCity(id);
      el.addEventListener("click", go);
      el.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          go();
        }
      });
    });
  }

  function applyFilter() {
    document.querySelectorAll(".city-pin").forEach((el) => {
      const city = CITY_DEFS.find((c) => c.id === el.dataset.city);
      el.classList.toggle("dim", city ? !matchesFilter(city) : true);
    });
    renderGrid();
    if (selectedCityId) {
      const c = CITY_DEFS.find((x) => x.id === selectedCityId);
      if (c && matchesFilter(c)) selectCity(selectedCityId);
    }
  }

  async function boot() {
    try {
      const res = await fetch("/field-pack/img/usa-map.svg?v=2");
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
      mapHost.innerHTML = `<p class="empty-note">Map failed to load. Use the place list below.</p>`;
      console.error(err);
    }

    document.querySelectorAll(".map-filters .chip").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".map-filters .chip").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        filter = btn.dataset.filter || "all";
        applyFilter();
      });
    });

    renderGrid();
    selectCity("dfw");
  }

  boot();
})();
