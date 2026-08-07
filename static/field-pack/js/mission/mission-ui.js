/**
 * Live controls for printable mission sheet pages.
 * Expects: #venue-data, #challenges-data, #mission-sheet, window.FPMission
 */
(function () {
  function $(sel, root) {
    return (root || document).querySelector(sel);
  }

  function track(event, params) {
    try {
      if (typeof gtag === "function") {
        gtag("event", event, params || {});
      } else if (window.dataLayer) {
        window.dataLayer.push(Object.assign({ event: event }, params || {}));
      }
    } catch (_) {
      /* ignore */
    }
  }

  function esc(s) {
    return String(s || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function renderSheet(mission) {
    const title = $("#mission-title");
    const meta = $("#mission-meta");
    const findsEl = $("#mission-finds");
    const chEl = $("#mission-challenges");
    if (title) title.textContent = mission.title;
    if (meta) meta.textContent = `${mission.ageLabel} · ${mission.timeLabel}`;
    if (findsEl) {
      findsEl.innerHTML = (mission.finds || [])
        .map(
          (f) => `<li class="mission-find">
          <span class="mission-check" aria-hidden="true">☐</span>
          <span class="mission-emoji">${esc(f.emoji || "📍")}</span>
          <span class="mission-find-body">
            <strong>${esc(f.label)}</strong>
            <small>${esc(f.one_liner || "")}${f.zone ? ` · ${esc(f.zone)}` : ""}</small>
          </span>
        </li>`
        )
        .join("");
    }
    if (chEl) {
      chEl.innerHTML = (mission.challenges || [])
        .map(
          (c) => `<li class="mission-challenge">
          <span class="mission-check" aria-hidden="true">☐</span>
          <span>${esc(c.text)}</span>
        </li>`
        )
        .join("");
    }
  }

  function printMission(mission) {
    track("mission_printed", {
      venue: mission.slug,
      age_band: mission.age,
      time_budget: mission.time,
      personalized: mission.personalized ? "1" : "0",
    });
    window.print();
  }

  let venue = null;
  let challenges = null;
  let state = { age: "4-5", time: "half", interest: "", name: "", seed: 1 };
  let lastMission = null;
  let genTimer = null;

  function AGE_FROM_SLIDER(v) {
    const n = parseInt(v, 10) || 1;
    return ["2-3", "4-5", "6-8", "9+"][Math.max(0, Math.min(3, n))] || "4-5";
  }

  function readControls() {
    const nameEl = $("#mission-name");
    const ageEl = $("#mission-age");
    const timeEl = document.querySelector('input[name="mission-time"]:checked');
    const interestEl = $("#mission-interest");
    state.name = nameEl ? nameEl.value : "";
    state.age = ageEl ? AGE_FROM_SLIDER(ageEl.value) : "4-5";
    state.time = timeEl ? timeEl.value : "half";
    state.interest = interestEl ? interestEl.value : "";
    const ageLabel = $("#mission-age-label");
    if (ageLabel && window.FPMission) {
      ageLabel.textContent = window.FPMission.AGE_LABELS[state.age] || state.age;
    }
  }

  function recompute(fromShuffle) {
    if (!venue || !challenges || !window.FPMission) return;
    readControls();
    lastMission = window.FPMission.selectMission(venue, challenges, state);
    renderSheet(lastMission);
    if (genTimer) clearTimeout(genTimer);
    genTimer = setTimeout(() => {
      track("mission_generated", {
        venue: venue.slug,
        age_band: state.age,
        time_budget: state.time,
        interest: state.interest || "any",
        personalized: state.name.trim() ? "1" : "0",
        shuffle: fromShuffle ? "1" : "0",
      });
    }, 500);
  }

  function wire() {
    ["mission-name", "mission-age", "mission-interest"].forEach((id) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.addEventListener("input", () => recompute(false));
      el.addEventListener("change", () => recompute(false));
    });
    document.querySelectorAll('input[name="mission-time"]').forEach((el) => {
      el.addEventListener("change", () => recompute(false));
    });
    $("#mission-print-btn")?.addEventListener("click", () => {
      if (lastMission) printMission(lastMission);
      else window.print();
    });
    $("#mission-shuffle-btn")?.addEventListener("click", () => {
      state.seed = (state.seed || 1) + 1;
      recompute(true);
    });
  }

  function boot() {
    const dataEl = document.getElementById("venue-data");
    const chEl = document.getElementById("challenges-data");
    if (!dataEl || !window.FPMission) return;
    try {
      venue = JSON.parse(dataEl.textContent);
      challenges = chEl ? JSON.parse(chEl.textContent) : { challenges: [] };
    } catch (e) {
      console.error(e);
      return;
    }
    const sel = $("#mission-interest");
    if (sel) {
      const opts = window.FPMission.interestOptions(venue);
      if (opts.length < 3) {
        sel.closest(".mission-field")?.setAttribute("hidden", "");
      } else {
        opts.forEach((o) => {
          const op = document.createElement("option");
          op.value = o.value;
          op.textContent = o.label.charAt(0).toUpperCase() + o.label.slice(1);
          sel.appendChild(op);
        });
      }
    }
    const age = $("#mission-age");
    if (age) age.value = "1";
    wire();
    recompute(false);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
