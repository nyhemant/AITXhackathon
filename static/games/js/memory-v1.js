(() => {
  const DATA_URL = "/games/data/memory-v1.json";
  const EASY = 6;
  const HARD = 8;
  const root = document.getElementById("kz-memory");
  if (!root) return;

  const reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const params = new URLSearchParams(location.search);
  const placeSlug = (params.get("place") || "").trim();

  const els = {
    setup: document.getElementById("kz-setup"),
    play: document.getElementById("kz-play"),
    finish: document.getElementById("kz-finish"),
    place: document.getElementById("kz-place-label"),
    board: document.getElementById("kz-board"),
    live: document.getElementById("kz-live"),
    status: document.getElementById("kz-status"),
    hunt: document.getElementById("kz-hunt-link"),
    again: document.getElementById("kz-again"),
    easy: document.getElementById("kz-easy"),
    hard: document.getElementById("kz-hard"),
  };

  let data = null;
  let deckAnimals = [];
  let lastMode = "easy";
  let lock = false;
  let first = null;
  let matched = 0;
  let pairs = EASY;

  function say(html, text) {
    if (els.live) els.live.innerHTML = html;
    if (text) els.live.setAttribute("aria-label", text);
  }

  function placeInfo() {
    if (!data || !placeSlug) return null;
    return data.places[placeSlug] || null;
  }

  function byId() {
    const map = {};
    for (const a of data.animals) map[a.id] = a;
    return map;
  }

  function poolForPlace() {
    const info = placeInfo();
    const map = byId();
    if (!info) return data.animals.slice();
    const listed = info.ids.map((id) => map[id]).filter(Boolean);
    if (listed.length >= EASY) return listed;
    return data.animals.slice();
  }

  function pick(count) {
    const pool = poolForPlace().slice();
    shuffle(pool);
    const chosen = pool.slice(0, Math.min(count, pool.length));
    if (chosen.length < count) {
      const have = new Set(chosen.map((a) => a.id));
      for (const a of shuffle(data.animals.slice())) {
        if (have.has(a.id)) continue;
        chosen.push(a);
        if (chosen.length === count) break;
      }
    }
    return chosen;
  }

  function shuffle(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      const t = arr[i];
      arr[i] = arr[j];
      arr[j] = t;
    }
    return arr;
  }

  function preload(animals) {
    for (const a of animals) {
      const img = new Image();
      img.src = a.photo;
    }
  }

  function start(mode) {
    lastMode = mode;
    pairs = mode === "hard" ? HARD : EASY;
    deckAnimals = pick(pairs);
    preload(deckAnimals);
    const cards = [];
    deckAnimals.forEach((a, i) => {
      cards.push({ key: a.id + "-a", animal: a, i });
      cards.push({ key: a.id + "-b", animal: a, i });
    });
    shuffle(cards);
    matched = 0;
    first = null;
    lock = false;
    els.board.dataset.pairs = String(pairs);
    els.board.replaceChildren();
    cards.forEach((c, idx) => els.board.appendChild(renderCard(c, idx, cards.length)));
    els.setup.hidden = true;
    els.finish.hidden = true;
    els.play.hidden = false;
    updateStatus();
    say("Tap two cards. Find the matching animals.", "Tap two cards. Find the matching animals.");
    els.board.querySelector("button")?.focus();
  }

  function renderCard(c, idx, total) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "kz-mem";
    btn.dataset.id = c.animal.id;
    btn.dataset.key = c.key;
    const downLabel = `Card ${idx + 1} of ${total}, face down`;
    btn.setAttribute("aria-label", downLabel);
    btn.dataset.down = downLabel;
    btn.innerHTML =
      '<span class="kz-mem-inner">' +
      '<span class="kz-face kz-face-back" aria-hidden="true">?</span>' +
      '<span class="kz-face kz-face-front"><img alt="" width="320" height="320"></span>' +
      "</span>";
    btn.querySelector("img").src = c.animal.photo;
    btn.querySelector("img").alt = c.animal.name;
    btn.addEventListener("click", () => onFlip(btn, c));
    return btn;
  }

  function onFlip(btn, c) {
    if (lock || btn.classList.contains("is-flipped") || btn.classList.contains("is-matched")) return;
    btn.classList.add("is-flipped");
    btn.setAttribute("aria-label", c.animal.name);
    if (!first) {
      first = { btn, c };
      return;
    }
    const prev = first;
    first = null;
    if (prev.c.animal.id === c.animal.id) {
      prev.btn.classList.add("is-matched");
      btn.classList.add("is-matched");
      prev.btn.disabled = true;
      btn.disabled = true;
      matched += 1;
      updateStatus();
      const fact = escapeHtml(c.animal.fact);
      const name = escapeHtml(c.animal.name);
      say(`<strong>A match! ${name}.</strong> ${fact}`, `A match! ${c.animal.name}. ${c.animal.fact}`);
      if (matched === pairs) win();
      return;
    }
    lock = true;
    const wait = reduce ? 450 : 900;
    window.setTimeout(() => {
      prev.btn.classList.remove("is-flipped");
      btn.classList.remove("is-flipped");
      prev.btn.setAttribute("aria-label", prev.btn.dataset.down || "Card, face down");
      btn.setAttribute("aria-label", btn.dataset.down || "Card, face down");
      lock = false;
    }, wait);
  }

  function updateStatus() {
    if (els.status) els.status.textContent = `${matched} of ${pairs} pairs`;
  }

  function win() {
    els.play.hidden = true;
    els.finish.hidden = false;
    const info = placeInfo();
    if (els.hunt) {
      const hunt = (info && info.hunt) || "/printables/scavenger-hunt/";
      els.hunt.href = hunt;
      els.hunt.textContent =
        info && hunt.endsWith("#printable-hunt")
          ? `Print the ${info.name} scavenger hunt`
          : "Print a scavenger hunt";
    }
    document.getElementById("kz-finish-title")?.focus();
    try {
      if (typeof window.gtag === "function") {
        window.gtag("event", "game_complete", {
          game_name: "memory_match",
          difficulty: lastMode,
          place: info ? placeSlug : "all",
        });
      }
    } catch (e) {}
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function ready() {
    const info = placeInfo();
    if (info && els.place) {
      els.place.hidden = false;
      els.place.textContent = `${info.name} animals`;
    }
    const pool = poolForPlace();
    if (els.hard) els.hard.disabled = pool.length < HARD && data.animals.length < HARD;
    els.easy.addEventListener("click", () => start("easy"));
    els.hard.addEventListener("click", () => start("hard"));
    els.again.addEventListener("click", () => start(lastMode));
  }

  fetch(DATA_URL, { credentials: "same-origin" })
    .then((r) => {
      if (!r.ok) throw new Error("data");
      return r.json();
    })
    .then((j) => {
      data = j;
      ready();
    })
    .catch(() => {
      say("The animal cards could not load. Try the page again when the signal is stronger.", "");
      if (els.easy) els.easy.disabled = true;
      if (els.hard) els.hard.disabled = true;
    });
})();
