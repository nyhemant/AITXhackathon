(() => {
  const card = document.getElementById("home-giraffe-card");
  const cta = document.getElementById("home-open-dallas");
  const fineHover = window.matchMedia("(hover: hover) and (pointer: fine)");

  function track(name, params) {
    if (typeof window.FPTrack === "function") {
      window.FPTrack(name, params || {});
      return;
    }
    const fn =
      (window.OneLessAnalytics && window.OneLessAnalytics.track) || window.trackEvent;
    if (typeof fn === "function") fn(name, params || {});
  }

  if (cta) {
    cta.addEventListener("click", () => {
      track("hero_cta_clicked", { source: "home_open_dallas", venue_slug: "dallas-zoo" });
    });
  }

  if (!card) return;

  card.addEventListener("click", (e) => {
    if (fineHover.matches) return;
    if (e.target.closest && e.target.closest("a.home-first-cta")) return;
    const hit = e.target.closest && e.target.closest(".home-giraffe-card-hit");
    if (!hit) return;
    if (!card.classList.contains("is-open")) {
      e.preventDefault();
      card.classList.add("is-open");
      card.setAttribute("data-peek", "open");
    }
  });

  document.addEventListener("click", (e) => {
    if (!card.classList.contains("is-open")) return;
    if (e.target.closest && e.target.closest("#home-giraffe-card")) return;
    card.classList.remove("is-open");
    card.removeAttribute("data-peek");
  });
})();
