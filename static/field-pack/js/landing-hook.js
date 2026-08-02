(() => {
  const places = window.FP_PLACES || [];
  const grid = document.getElementById("ready-grid");
  const chips = document.getElementById("city-chips");
  const continueChip = document.getElementById("continue-chip");
  const citySelect = document.getElementById("city-select");

  const FEATURED_READY_IDS = [
    "dallas-zoo",
    "childrens-aquarium-dallas",
    "childrens-museum-perot",
  ];
  const READY = FEATURED_READY_IDS.map((id) => places.find((p) => p.id === id)).filter(Boolean);

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  if (grid) {
    grid.innerHTML = READY.map((p) => {
      const href = p.appHref || p.href;
      return `<a class="ready-card" href="${escapeHtml(href)}">
        <span class="rc-emoji" aria-hidden="true">${escapeHtml(p.emoji || "")}</span>
        <h3>${escapeHtml(p.name)}</h3>
        <p>${escapeHtml(p.blurb || "")}</p>
        <span class="rc-cta">Start outing →</span>
      </a>`;
    }).join("");
  }

  // City chips: highlight ready cities first
  const chipDefs = [
    { id: "dallas", label: "Dallas area", ready: true },
    { id: "austin", label: "Austin", ready: true },
    { id: "nyc", label: "New York", ready: true },
    { id: "chicago", label: "Chicago", ready: true },
    { id: "la", label: "Los Angeles", ready: true },
    { id: "san-diego", label: "San Diego", ready: true },
  ];

  if (chips) {
    chips.innerHTML = chipDefs
      .map(
        (c) =>
          `<button type="button" class="city-chip" data-city="${c.id}" aria-pressed="false">
            ${escapeHtml(c.label)}
            <span class="chip-tag">${c.ready ? "ready" : "soon"}</span>
          </button>`
      )
      .join("");

    chips.addEventListener("click", (e) => {
      const btn = e.target.closest(".city-chip");
      if (!btn) return;
      const id = btn.dataset.city;
      chips.querySelectorAll(".city-chip").forEach((b) => b.setAttribute("aria-pressed", "false"));
      btn.setAttribute("aria-pressed", "true");
      if (citySelect && citySelect.querySelector(`option[value="${id}"]`)) {
        citySelect.value = id;
        citySelect.dispatchEvent(new Event("change", { bubbles: true }));
      }
      document.getElementById("us-map")?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }

  // Continue last outing — deep-link trip if possible
  try {
    const raw =
      localStorage.getItem("1less-babys-day-out-trips-v1") ||
      localStorage.getItem("arya-field-pack-trips-v2");
    if (raw && continueChip) {
      const store = JSON.parse(raw);
      const trips = store.trips || [];
      if (trips.length) {
        const last = trips[trips.length - 1];
        const venueId = last.venueId || store.selectedVenueId || "dallas-zoo";
        const href = last.id
          ? `/field-pack/app.html#/trip/${encodeURIComponent(last.id)}`
          : `/field-pack/app.html#/venue/${encodeURIComponent(venueId)}`;
        const label = last.title || "last outing";
        continueChip.hidden = false;
        continueChip.removeAttribute("hidden");
        continueChip.style.display = "block";
        continueChip.innerHTML = `Continue <strong>${escapeHtml(label)}</strong> →
          <a href="${href}">Open outing</a>`;
      }
    }
  } catch {
    /* ignore */
  }

  // Waiting-on cities
  function renderWaiting() {
    const el = document.getElementById("waiting-cities");
    if (!el) return;
    let ids = [];
    try {
      ids = JSON.parse(localStorage.getItem("1less-saved-cities") || "[]");
    } catch {
      ids = [];
    }
    if (!ids.length) {
      el.hidden = true;
      el.textContent = "";
      return;
    }
    const labels = ids.map((id) => {
      const opt = citySelect?.querySelector(`option[value="${id}"]`);
      return opt ? opt.textContent.replace(/\s*·.*$/, "").trim() : id;
    });
    el.hidden = false;
    el.innerHTML = `You’re waiting on: <strong>${labels.map(escapeHtml).join(", ")}</strong>`;
  }
  renderWaiting();
  window.addEventListener("1less-cities-saved", renderWaiting);
})();
