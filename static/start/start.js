(() => {
  const doors = document.querySelectorAll(".start-door");

  function track(name, params) {
    if (typeof window.FPTrack === "function") {
      window.FPTrack(name, params || {});
      return;
    }
    const fn =
      (window.OneLessAnalytics && window.OneLessAnalytics.track) || window.trackEvent;
    if (typeof fn === "function") fn(name, params || {});
  }

  doors.forEach((door) => {
    door.addEventListener("click", () => {
      track("hero_cta_clicked", {
        source: door.id || "start_door",
        venue_slug: "dallas-zoo",
      });
    });
  });
})();
