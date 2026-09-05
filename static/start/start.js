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

  initHomeTeaser();

  function initHomeTeaser() {
    const box = document.querySelector("#start-home .start-chapter-box");
    const plate = box && box.querySelector(".start-chapter-still");
    const tease = box && box.querySelector("[data-start-tease]");
    const screen = tease && tease.querySelector(".start-home-screen");
    const video = screen && screen.querySelector(".start-home-video");
    const fallback = screen && screen.querySelector(".start-home-fallback");
    const continueEl = box && box.querySelector(".start-home-continue");
    const hit = box && box.querySelector(".start-chapter-hit");
    const watchPill = document.querySelector('#start-home .start-pill[href*="virtual-field-trip"]');
    if (!box || !plate || !tease || !screen || !video || !continueEl || !hit) return;

    const WATCH = "/field-pack/virtual-field-trip/";
    const SEEN_KEY = "fp-start-teaser-seen-v1";
    const MAX_SEC = 8;
    /*
      Laptop LCD inner bezel on home-print-table.jpg (1024×1536).
      Image-space % corners TL → TR → BR → BL. JS maps them through
      object-fit:cover + object-position (42% 28%) into matrix3d.
    */
    const HOTBOX = [
      { x: 8.2, y: 20.57 },
      { x: 55.76, y: 17.12 },
      { x: 60.84, y: 40.56 },
      { x: 15.53, y: 47.33 },
    ];
    const TEASERS = [
      {
        id: "flamingo",
        habitat: "caribbean-flamingo",
        src: "/start/teasers/flamingo.mp4",
        poster: "/start/teasers/flamingo.jpg",
        label: "Flamingo",
      },
      {
        id: "giraffe",
        habitat: "reticulated-giraffe",
        src: "/start/teasers/giraffe.mp4",
        poster: "/start/teasers/giraffe.jpg",
        label: "Giraffe",
      },
      {
        id: "lion",
        habitat: "african-lion",
        src: "/start/teasers/lion.mp4",
        poster: "/start/teasers/lion.jpg",
        label: "Lion",
      },
      {
        id: "otter",
        habitat: "asian-small-clawed-otter",
        src: "/start/teasers/otter.mp4",
        poster: "/start/teasers/otter.jpg",
        label: "Otter",
      },
    ];

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const teaser = pickTeaser(TEASERS, SEEN_KEY);
    const dest = watchHref(WATCH, teaser);
    continueEl.href = dest;
    hit.href = dest;
    if (watchPill) watchPill.href = dest;
    continueEl.setAttribute("aria-label", `Continue to Watch Live — ${teaser.label}`);

    let aligned = false;
    let ended = false;
    let maxTimer = 0;

    function align() {
      if (!plate.naturalWidth || !plate.naturalHeight) return;
      const boxRect = box.getBoundingClientRect();
      const corners = HOTBOX.map((pt) => imagePctToBox(pt, plate, boxRect));
      applyScreenTransform(screen, corners);
      placeContinue(continueEl, corners);
      aligned = true;
    }

    function showStill() {
      tease.hidden = false;
      video.hidden = true;
      fallback.hidden = false;
      fallback.alt = "";
      fallback.src = teaser.poster;
      continueEl.hidden = false;
    }

    function showContinue() {
      if (ended) return;
      ended = true;
      if (maxTimer) window.clearTimeout(maxTimer);
      try {
        video.pause();
      } catch (_) {}
      continueEl.hidden = false;
    }

    function playTeaser() {
      tease.hidden = false;
      fallback.hidden = true;
      video.hidden = false;
      video.muted = true;
      video.playsInline = true;
      video.setAttribute("playsinline", "");
      video.poster = teaser.poster;
      video.src = teaser.src;
      const kick = video.play();
      if (kick && typeof kick.catch === "function") {
        kick.catch(() => showStill());
      }
      maxTimer = window.setTimeout(showContinue, MAX_SEC * 1000);
    }

    video.addEventListener("ended", showContinue);
    video.addEventListener("error", showStill);
    video.addEventListener("timeupdate", () => {
      if (video.currentTime >= MAX_SEC) showContinue();
    });

    function onReady() {
      align();
      if (!aligned) return;
      if (reduceMotion) {
        showStill();
        return;
      }
      playTeaser();
    }

    if (plate.complete && plate.naturalWidth) onReady();
    else plate.addEventListener("load", onReady, { once: true });

    window.addEventListener("resize", align);

    if ("IntersectionObserver" in window) {
      const io = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (reduceMotion || ended || !video.src) return;
            if (entry.isIntersecting) {
              const p = video.play();
              if (p && typeof p.catch === "function") p.catch(() => {});
            } else {
              video.pause();
            }
          });
        },
        { threshold: 0.35 }
      );
      io.observe(box);
    }
  }

  function watchHref(base, teaser) {
    if (!teaser || !teaser.habitat) return base;
    return `${base}?tab=zoo#habitat=${teaser.habitat}`;
  }

  function pickTeaser(pool, key) {
    let seen = [];
    try {
      const raw = sessionStorage.getItem(key);
      seen = raw ? JSON.parse(raw) : [];
      if (!Array.isArray(seen)) seen = [];
    } catch (_) {
      seen = [];
    }
    const unseen = pool.filter((t) => !seen.includes(t.id));
    const bag = unseen.length ? unseen : pool;
    const pick = bag[Math.floor(Math.random() * bag.length)];
    const next = unseen.length ? seen.concat([pick.id]) : [pick.id];
    try {
      sessionStorage.setItem(key, JSON.stringify(next));
    } catch (_) {}
    return pick;
  }

  function parseObjectPosition(value) {
    const parts = String(value || "50% 50%").trim().split(/\s+/);
    const x = parts[0] && parts[0].endsWith("%") ? parseFloat(parts[0]) / 100 : 0.5;
    const y = parts[1] && parts[1].endsWith("%") ? parseFloat(parts[1]) / 100 : 0.5;
    return {
      x: Number.isFinite(x) ? x : 0.5,
      y: Number.isFinite(y) ? y : 0.5,
    };
  }

  function imagePctToBox(pt, img, boxRect) {
    const nw = img.naturalWidth;
    const nh = img.naturalHeight;
    const rect = img.getBoundingClientRect();
    const pos = parseObjectPosition(getComputedStyle(img).objectPosition);
    const scale = Math.max(rect.width / nw, rect.height / nh);
    const dw = nw * scale;
    const dh = nh * scale;
    const left = rect.left + (rect.width - dw) * pos.x;
    const top = rect.top + (rect.height - dh) * pos.y;
    return {
      x: left + (pt.x / 100) * nw * scale - boxRect.left,
      y: top + (pt.y / 100) * nh * scale - boxRect.top,
    };
  }

  function applyScreenTransform(el, corners) {
    const w = el.offsetWidth || 160;
    const h = el.offsetHeight || 90;
    const from = [
      { x: 0, y: 0 },
      { x: w, y: 0 },
      { x: w, y: h },
      { x: 0, y: h },
    ];
    el.style.transform = matrix3d(from, corners);
  }

  function placeContinue(el, corners) {
    const midBottom = {
      x: (corners[2].x + corners[3].x) / 2,
      y: (corners[2].y + corners[3].y) / 2,
    };
    const midTop = {
      x: (corners[0].x + corners[1].x) / 2,
      y: (corners[0].y + corners[1].y) / 2,
    };
    el.style.left = `${(midBottom.x + midTop.x) / 2}px`;
    el.style.top = `${midBottom.y - (midBottom.y - midTop.y) * 0.22}px`;
  }

  function matrix3d(from, to) {
    const A = [];
    const b = [];
    for (let i = 0; i < 4; i += 1) {
      const s = from[i];
      const d = to[i];
      A.push([s.x, s.y, 1, 0, 0, 0, -s.x * d.x, -s.y * d.x]);
      b.push(d.x);
      A.push([0, 0, 0, s.x, s.y, 1, -s.x * d.y, -s.y * d.y]);
      b.push(d.y);
    }
    const h = solve(A, b);
    if (!h) return "none";
    const m = [h[0], h[3], 0, h[6], h[1], h[4], 0, h[7], 0, 0, 1, 0, h[2], h[5], 0, 1];
    return `matrix3d(${m.map((n) => Number(n.toFixed(6))).join(",")})`;
  }

  function solve(A, b) {
    const n = b.length;
    const M = A.map((row, i) => row.concat([b[i]]));
    for (let col = 0; col < n; col += 1) {
      let pivot = col;
      for (let r = col + 1; r < n; r += 1) {
        if (Math.abs(M[r][col]) > Math.abs(M[pivot][col])) pivot = r;
      }
      if (Math.abs(M[pivot][col]) < 1e-10) return null;
      if (pivot !== col) {
        const tmp = M[col];
        M[col] = M[pivot];
        M[pivot] = tmp;
      }
      const div = M[col][col];
      for (let c = col; c <= n; c += 1) M[col][c] /= div;
      for (let r = 0; r < n; r += 1) {
        if (r === col) continue;
        const f = M[r][col];
        for (let c = col; c <= n; c += 1) M[r][c] -= f * M[col][c];
      }
    }
    return M.map((row) => row[n]);
  }
})();
