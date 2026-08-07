/**
 * Live mission controls (Kayak-style) for pilot venue pages.
 * Expects: #venue-data JSON, #mission-controls, #mission-live, window.FPMission
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

  function renderLive(mission) {
    const root = $("#mission-live");
    if (!root) return;
    const finds = (mission.finds || [])
      .map(
        (f, i) => `<li class="mission-find">
        <span class="mission-check" aria-hidden="true">☐</span>
        <span class="mission-emoji">${esc(f.emoji || "📍")}</span>
        <span class="mission-find-body">
          <strong>${esc(f.label)}</strong>
          <small>${esc(f.one_liner || "")}${f.zone ? ` · ${esc(f.zone)}` : ""}</small>
        </span>
      </li>`
      )
      .join("");
    const challenges = (mission.challenges || [])
      .map(
        (c) => `<li class="mission-challenge">
        <span class="mission-check" aria-hidden="true">☐</span>
        <span>${esc(c.text)}</span>
      </li>`
      )
      .join("");

    root.innerHTML = `
      <div class="mission-card">
        <p class="mission-kicker">${esc(mission.ageLabel)} · ${esc(mission.timeLabel)}</p>
        <h2 class="mission-title">${esc(mission.title)}</h2>
        <ol class="mission-finds" aria-label="Finds">${finds}</ol>
        <h3 class="mission-subhead">Bonus challenges</h3>
        <ul class="mission-challenges" aria-label="Challenges">${challenges}</ul>
        <div class="mission-actions">
          <button type="button" class="btn btn-primary btn-big" id="mission-print-btn">Print mission</button>
          <button type="button" class="btn btn-secondary" id="mission-shuffle-btn">Shuffle finds</button>
        </div>
      </div>`;

    $("#mission-print-btn")?.addEventListener("click", () => printMission(mission));
    $("#mission-shuffle-btn")?.addEventListener("click", () => {
      state.seed = (state.seed || 1) + 1;
      recompute(true);
    });
  }

  function fillPrintSheet(mission) {
    let sheet = $("#mission-print-sheet");
    if (!sheet) {
      sheet = document.createElement("div");
      sheet.id = "mission-print-sheet";
      sheet.className = "mission-print-sheet";
      sheet.setAttribute("aria-hidden", "true");
      document.body.appendChild(sheet);
    }
    const dateLine = new Date().toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
    const finds = (mission.finds || [])
      .map(
        (f) =>
          `<li><span class="mp-box">☐</span> <strong>${esc(f.emoji || "")} ${esc(f.label)}</strong>
          <span class="mp-line">${esc(f.one_liner || "")}${f.zone ? ` (${esc(f.zone)})` : ""}</span></li>`
      )
      .join("");
    const ch = (mission.challenges || [])
      .map((c) => `<li><span class="mp-box">☐</span> ${esc(c.text)}</li>`)
      .join("");
    const url = `https://1less.app/field-pack/${esc(mission.slug)}/`;
    sheet.innerHTML = `
      <div class="mp-inner">
        <p class="mp-brand">1Less Field Trip Kit</p>
        <h1>${esc(mission.title)}</h1>
        <p class="mp-meta">${esc(mission.ageLabel)} · ${esc(mission.timeLabel)} · ${esc(dateLine)}</p>
        <h2>Find these</h2>
        <ol class="mp-finds">${finds}</ol>
        <h2>Bonus challenges</h2>
        <ul class="mp-challenges">${ch}</ul>
        <p class="mp-footer">Free hunts for 140+ zoos &amp; museums → ${url}</p>
      </div>`;
    return sheet;
  }

  function printMission(mission) {
    fillPrintSheet(mission);
    track("mission_printed", {
      venue: mission.slug,
      age_band: mission.age,
      time_budget: mission.time,
      personalized: mission.personalized ? "1" : "0",
    });
    document.body.classList.add("printing-mission");
    const done = () => document.body.classList.remove("printing-mission");
    window.addEventListener("afterprint", done, { once: true });
    setTimeout(() => window.print(), 50);
  }

  let venue = null;
  let challenges = null;
  let state = { age: "4-5", time: "half", interest: "", name: "", seed: 1 };
  let lastMission = null;
  let genTimer = null;

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

  function AGE_FROM_SLIDER(v) {
    const n = parseInt(v, 10) || 1;
    return ["2-3", "4-5", "6-8", "9+"][Math.max(0, Math.min(3, n))] || "4-5";
  }

  function recompute(fromShuffle) {
    if (!venue || !challenges || !window.FPMission) return;
    readControls();
    lastMission = window.FPMission.selectMission(venue, challenges, state);
    renderLive(lastMission);
    // Update SEO-visible default list region for accessibility (optional)
    const seoList = $("#mission-default-list");
    if (seoList) {
      seoList.innerHTML = (lastMission.finds || [])
        .map(
          (f) =>
            `<li><strong>${esc(f.emoji || "")} ${esc(f.label)}</strong> — ${esc(f.one_liner || "")}</li>`
        )
        .join("");
    }
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
    window.addEventListener("beforeprint", () => {
      if (lastMission) {
        fillPrintSheet(lastMission);
        document.body.classList.add("printing-mission");
      }
    });
    window.addEventListener("afterprint", () => {
      document.body.classList.remove("printing-mission");
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
    // Populate interest dropdown
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
    // Default age slider to Ready (4-5) = index 1
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
