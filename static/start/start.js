(() => {
  const pills = document.querySelectorAll(".start-pill");

  function track(name, params) {
    if (typeof window.FPTrack === "function") {
      window.FPTrack(name, params || {});
      return;
    }
    const fn =
      (window.OneLessAnalytics && window.OneLessAnalytics.track) || window.trackEvent;
    if (typeof fn === "function") fn(name, params || {});
  }

  pills.forEach((pill) => {
    pill.addEventListener("click", () => {
      const href = pill.getAttribute("href") || "";
      track("hero_cta_clicked", {
        source: "start_pill",
        label: (pill.textContent || "").trim(),
        href,
      });
    });
  });

  const trackEl = document.getElementById("start-teach-track");
  if (trackEl) {
    const cue = document.querySelector("[data-teach-cue]");
    const dots = document.querySelectorAll(".start-teach-dots span");
    const count = trackEl.querySelectorAll(".start-teach-slide").length;

    function currentIndex() {
      const width = trackEl.clientWidth || 1;
      const raw = Math.round(trackEl.scrollLeft / width);
      return Math.min(count - 1, Math.max(0, raw));
    }

    function syncCue() {
      const idx = currentIndex();
      if (cue) cue.textContent = String(idx + 1);
      dots.forEach((dot, i) => {
        dot.classList.toggle("is-current", i === idx);
      });
    }

    trackEl.addEventListener("scroll", syncCue, { passive: true });
    window.addEventListener("resize", syncCue);
    syncCue();
  }
})();
