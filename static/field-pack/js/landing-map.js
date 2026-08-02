(() => {
  const places = window.FP_PLACES || [];
  const svg = document.getElementById("usa-map");
  const pinsLayer = document.getElementById("map-pins");
  const detail = document.getElementById("pin-detail");
  const grid = document.getElementById("places-grid");
  const width = 960;
  const height = 560;

  let filter = "all";
  let selectedId = null;

  // Cluster nearby pins slightly so DFW/LA/NY don't fully stack
  function layoutPlaces(list) {
    const projected = list.map((p) => {
      const pt = window.fpProjectUS(p.lat, p.lon, width, height);
      return { ...p, x: pt.x, y: pt.y };
    });
    // simple repulsion
    for (let iter = 0; iter < 8; iter += 1) {
      for (let i = 0; i < projected.length; i += 1) {
        for (let j = i + 1; j < projected.length; j += 1) {
          const a = projected[i];
          const b = projected[j];
          const dx = b.x - a.x;
          const dy = b.y - a.y;
          const dist = Math.hypot(dx, dy) || 0.01;
          if (dist < 28) {
            const push = ((28 - dist) / 28) * 6;
            const ux = dx / dist;
            const uy = dy / dist;
            a.x -= ux * push;
            a.y -= uy * push;
            b.x += ux * push;
            b.y += uy * push;
          }
        }
      }
    }
    return projected;
  }

  const laidOut = layoutPlaces(places);

  function matchesFilter(p) {
    if (filter === "all") return true;
    if (filter === "ready") return p.status === "ready";
    if (filter === "soon") return p.status === "soon";
    if (filter === "tx") return p.state === "TX";
    return true;
  }

  function renderPins() {
    pinsLayer.innerHTML = "";
    for (const p of laidOut) {
      const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
      g.classList.add("map-pin", p.status);
      if (!matchesFilter(p)) g.classList.add("dim");
      if (selectedId === p.id) g.classList.add("selected");
      g.setAttribute("tabindex", matchesFilter(p) ? "0" : "-1");
      g.setAttribute("role", "button");
      g.setAttribute("aria-label", `${p.name}, ${p.city} ${p.state}, ${p.status}`);
      g.dataset.id = p.id;
      g.style.transform = `translate(${p.x}px, ${p.y}px)`;

      g.innerHTML = `
        <circle class="pin-ring" r="16" cx="0" cy="0"></circle>
        <circle class="pin-core" r="10" cx="0" cy="0"></circle>
        <text x="14" y="5">${escapeXml(p.emoji || "📍")}</text>
      `;

      const activate = () => selectPlace(p.id);
      g.addEventListener("click", activate);
      g.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          activate();
        }
      });
      pinsLayer.appendChild(g);
    }
  }

  function selectPlace(id) {
    selectedId = id;
    const p = places.find((x) => x.id === id);
    renderPins();
    if (!p) return;
    const ready = p.status === "ready";
    detail.className = "pin-detail";
    detail.innerHTML = `
      <p class="pin-detail-kicker">${escapeHtml(p.type)} · ${escapeHtml(p.city)}, ${escapeHtml(p.state)}</p>
      <h3>${escapeHtml(p.emoji || "")} ${escapeHtml(p.name)}</h3>
      <p class="pd-meta">${ready ? "Live on Field Pack" : "Page up · pack coming soon"}</p>
      <span class="pd-status ${p.status}">${ready ? "Ready to play" : "Coming soon"}</span>
      <p class="pd-blurb">${escapeHtml(p.blurb)}</p>
      <div class="pd-actions">
        <a class="btn btn-primary" href="${escapeAttr(p.href)}">Open place page →</a>
        ${
          p.appHref
            ? `<a class="btn btn-secondary" href="${escapeAttr(p.appHref)}">Start outing</a>`
            : `<button type="button" class="btn btn-ghost" disabled>Outing soon</button>`
        }
      </div>
    `;
  }

  function renderGrid() {
    grid.innerHTML = "";
    const sorted = [...places].sort((a, b) => {
      if (a.status !== b.status) return a.status === "ready" ? -1 : 1;
      return a.name.localeCompare(b.name);
    });
    for (const p of sorted) {
      if (!matchesFilter(p)) continue;
      const a = document.createElement("a");
      a.className = "place-card";
      a.href = p.href;
      a.innerHTML = `
        <div class="pc-top">
          <span class="pc-emoji">${escapeHtml(p.emoji || "📍")}</span>
          <span class="pc-badge ${p.status}">${p.status === "ready" ? "Ready" : "Soon"}</span>
        </div>
        <div class="pc-name">${escapeHtml(p.name)}</div>
        <div class="pc-city">${escapeHtml(p.city)}, ${escapeHtml(p.state)} · ${escapeHtml(p.type)}</div>
        <div class="pc-blurb">${escapeHtml(p.blurb)}</div>
      `;
      a.addEventListener("mouseenter", () => {
        selectedId = p.id;
        renderPins();
      });
      grid.appendChild(a);
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
  function escapeXml(s) {
    return escapeHtml(s);
  }

  document.querySelectorAll(".map-filters .chip").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".map-filters .chip").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      filter = btn.dataset.filter || "all";
      renderPins();
      renderGrid();
    });
  });

  // Default select first ready place
  const firstReady = places.find((p) => p.status === "ready");
  renderPins();
  renderGrid();
  if (firstReady) selectPlace(firstReady.id);
})();
