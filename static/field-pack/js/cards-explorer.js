/* Find-a-card explorer: samples first; accordion library; All cards = primary set. */
(function () {
  if (typeof FPTrack === "function") FPTrack("cards_hub_visited", { source: "cards_hub" });
  document.querySelectorAll("a[data-card-id]").forEach(function (a) {
    a.addEventListener("click", function () {
      if (typeof FPTrack === "function") {
        FPTrack("card_opened", { card_id: a.getAttribute("data-card-id") || "", source: "cards_hub" });
      }
    });
  });

  var q = document.getElementById("cards-hub-search");
  var form = document.getElementById("cards-hub-form");
  var allBtn = document.getElementById("cards-all-wrap");
  var tryRow = document.getElementById("try-a-card");
  var countEl = document.getElementById("cards-hub-count");
  var panels = Array.prototype.slice.call(document.querySelectorAll("[data-card-accordion]"));
  var TOTAL = document.querySelectorAll(".cards-hub-item:not([data-card-group='attractions'])").length;
  var syncing = false;

  function setAllPressed(on) {
    if (allBtn) allBtn.setAttribute("aria-pressed", on ? "true" : "false");
  }

  function panelGroup(panel) {
    return panel.getAttribute("data-card-accordion") || "";
  }

  function isPrimary(panel) {
    return panelGroup(panel) !== "attractions";
  }

  function endSync() {
    requestAnimationFrame(function () {
      syncing = false;
    });
  }

  function openOnly(id) {
    syncing = true;
    panels.forEach(function (p) {
      p.open = panelGroup(p) === id;
    });
    setAllPressed(false);
    endSync();
  }

  function openPrimaryAll() {
    syncing = true;
    panels.forEach(function (p) {
      p.open = isPrimary(p);
    });
    setAllPressed(true);
    endSync();
  }

  function applyHubFilter() {
    var n = q ? (q.value || "").trim().toLowerCase() : "";
    var searching = n.length >= 1;
    var allPrimary = allBtn && allBtn.getAttribute("aria-pressed") === "true";
    var visible = 0;
    var visiblePrimary = 0;

    document.querySelectorAll(".cards-hub-item").forEach(function (li) {
      var blob = (li.getAttribute("data-card-search") || li.textContent || "").toLowerCase();
      var g = li.getAttribute("data-card-group") || "";
      var hide = searching && blob.indexOf(n) === -1;
      li.hidden = hide;
      if (!hide) {
        visible += 1;
        if (g !== "attractions") visiblePrimary += 1;
      }
    });

    if (searching) {
      syncing = true;
      panels.forEach(function (panel) {
        var any = false;
        panel.querySelectorAll(".cards-hub-item").forEach(function (li) {
          if (!li.hidden) any = true;
        });
        panel.hidden = !any;
        panel.open = any;
      });
      syncing = false;
      setAllPressed(false);
    } else {
      panels.forEach(function (panel) {
        panel.hidden = false;
      });
    }

    if (tryRow) tryRow.hidden = searching;

    if (countEl) {
      if (searching) {
        countEl.textContent = visible === 1 ? "1 card" : visible + " cards";
      } else if (allPrimary) {
        countEl.textContent = TOTAL + " cards";
      } else {
        countEl.textContent = TOTAL + " cards";
      }
    }
  }

  panels.forEach(function (panel) {
    var summary = panel.querySelector("summary");
    if (summary) {
      summary.addEventListener("click", function (e) {
        if (allBtn && allBtn.getAttribute("aria-pressed") === "true") {
          e.preventDefault();
          openOnly(panelGroup(panel));
          applyHubFilter();
        }
      });
    }
    panel.addEventListener("toggle", function () {
      if (syncing) return;
      if (panel.open && !(allBtn && allBtn.getAttribute("aria-pressed") === "true")) {
        syncing = true;
        panels.forEach(function (other) {
          if (other !== panel) other.open = false;
        });
        setAllPressed(false);
        endSync();
      }
      applyHubFilter();
    });
  });

  if (allBtn) {
    allBtn.addEventListener("click", function () {
      if (q) q.value = "";
      openPrimaryAll();
      applyHubFilter();
    });
  }
  if (q) q.addEventListener("input", applyHubFilter);
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      applyHubFilter();
    });
  }

  var hash = (location.hash || "").replace(/^#/, "");
  if (hash === "cards-attractions") openOnly("attractions");
  else if (hash === "cards-wildlife" || hash === "cards-wildlife-wrap") openOnly("wildlife");
  else if (hash === "cards-sealife" || hash === "cards-sealife-wrap") openOnly("sealife");
  else if (hash === "cards-all-wrap" || hash === "cards-accordion") openPrimaryAll();

  if (q && q.value) applyHubFilter();
})();
