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
})();
