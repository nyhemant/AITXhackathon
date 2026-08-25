(() => {
  const card = document.getElementById("start-giraffe-card");
  const ctas = document.querySelectorAll("#start-open-dallas, #start-open-dallas-after");
  const fineHover = window.matchMedia("(hover: hover) and (pointer: fine)");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  function track(name, params) {
    if (typeof window.FPTrack === "function") {
      window.FPTrack(name, params || {});
      return;
    }
    const fn =
      (window.OneLessAnalytics && window.OneLessAnalytics.track) || window.trackEvent;
    if (typeof fn === "function") fn(name, params || {});
  }

  ctas.forEach((cta) => {
    cta.addEventListener("click", () => {
      track("hero_cta_clicked", {
        source: cta.id || "start_open_dallas",
        venue_slug: "dallas-zoo",
      });
    });
  });

  if (!card) return;

  function setOpen(open) {
    card.classList.toggle("is-open", open);
    card.setAttribute("aria-expanded", open || reduceMotion.matches ? "true" : "false");
  }

  if (reduceMotion.matches) setOpen(true);

  card.addEventListener("click", () => {
    if (fineHover.matches || reduceMotion.matches) return;
    setOpen(!card.classList.contains("is-open"));
  });

  card.addEventListener("keydown", (e) => {
    if (e.key !== "Enter" && e.key !== " ") return;
    if (fineHover.matches || reduceMotion.matches) return;
    e.preventDefault();
    setOpen(!card.classList.contains("is-open"));
  });

  document.addEventListener("click", (e) => {
    if (fineHover.matches || reduceMotion.matches) return;
    if (!card.classList.contains("is-open")) return;
    if (e.target.closest && e.target.closest("#start-giraffe-card")) return;
    setOpen(false);
  });
})();
