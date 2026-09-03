/* Find-a-card explorer: samples first; full list on search, filter, or All cards. */
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
  var tabs = document.querySelectorAll(".place-type-tab[data-card-filter]");
  var browse = document.getElementById("cards-all-wrap");
  var tryRow = document.getElementById("try-a-card");
  var countEl = document.getElementById("cards-hub-count");
  var filter = "all";
  var TOTAL = document.querySelectorAll(".cards-hub-item").length;

  function applyHubFilter() {
    var n = q ? (q.value || "").trim().toLowerCase() : "";
    var searching = n.length >= 1;
    var filtering = filter !== "all";
    var visible = 0;

    document.querySelectorAll(".cards-hub-item").forEach(function (li) {
      var blob = (li.getAttribute("data-card-search") || li.textContent || "").toLowerCase();
      var g = li.getAttribute("data-card-group") || "";
      var missSearch = searching && blob.indexOf(n) === -1;
      var missFilter = filtering && g !== filter;
      var hide = missSearch || missFilter;
      li.hidden = hide;
      if (!hide) visible += 1;
    });

    document.querySelectorAll(".cards-hub-section").forEach(function (sec) {
      var any = false;
      sec.querySelectorAll(".cards-hub-item").forEach(function (li) {
        if (!li.hidden) any = true;
      });
      sec.hidden = !any;
    });

    if (browse && (searching || filtering)) browse.open = true;
    if (tryRow) tryRow.hidden = searching || filtering;

    if (countEl) {
      if (searching || filtering) {
        countEl.textContent = visible === 1 ? "1 card" : visible + " cards";
      } else {
        countEl.textContent = TOTAL + " cards · from Field Trip Kit place lists";
      }
    }
  }

  tabs.forEach(function (btn) {
    btn.addEventListener("click", function () {
      filter = btn.getAttribute("data-card-filter") || "all";
      tabs.forEach(function (b) {
        var on = b === btn;
        b.classList.toggle("is-active", on);
        b.setAttribute("aria-selected", on ? "true" : "false");
      });
      applyHubFilter();
    });
  });
  if (q) q.addEventListener("input", applyHubFilter);
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      applyHubFilter();
    });
  }
  if (browse) browse.addEventListener("toggle", applyHubFilter);

  if (q && q.value) applyHubFilter();
})();
