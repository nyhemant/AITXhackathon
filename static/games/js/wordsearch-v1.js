(() => {
  const DATA_URL = "/games/data/memory-v1.json";
  const EASY = 6;
  const HARD = 8;
  const EASY_WORDS = 5;
  const HARD_WORDS = 7;
  const MOD = new Set(
    "AFRICAN AMERICAN ASIAN CARIBBEAN GIANT RED SEA NILE RING TAILED TWO TOED WESTERN LOWLAND SUMATRAN RETICULATED GALAPAGOS SMALL CLAWED RIVER LAKE FRESHWATER".split(" ")
  );
  const root = document.getElementById("kz-wordsearch");
  if (!root) return;

  const params = new URLSearchParams(location.search);
  const placeSlug = (params.get("place") || "").trim();

  const els = {
    setup: document.getElementById("kz-setup"),
    play: document.getElementById("kz-play"),
    finish: document.getElementById("kz-finish"),
    place: document.getElementById("kz-place-label"),
    grid: document.getElementById("kz-grid"),
    list: document.getElementById("kz-list"),
    live: document.getElementById("kz-live"),
    status: document.getElementById("kz-status"),
    hunt: document.getElementById("kz-hunt-link"),
    again: document.getElementById("kz-again"),
    easy: document.getElementById("kz-easy"),
    hard: document.getElementById("kz-hard"),
  };

  let data = null;
  let lastMode = "easy";
  let size = EASY;
  let entries = []; // {name, word, id}
  let found = new Set();
  let foundCells = new Set();
  let grid = [];
  let cells = [];
  let dragging = false;
  let moved = false;
  let path = [];
  let tapStart = null;

  function say(text) {
    if (els.live) els.live.textContent = text;
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

  function stripAccents(s) {
    return String(s).normalize("NFKD").replace(/[\u0300-\u036f]/g, "");
  }

  function tokens(name) {
    return stripAccents(name).toUpperCase().match(/[A-Z]+/g) || [];
  }

  function compact(name) {
    return tokens(name).join("");
  }

  function gridWord(name, max) {
    const c = compact(name);
    if (c.length >= 3 && c.length <= max) return c;
    const toks = tokens(name);
    const animal = toks.filter((t) => !MOD.has(t) && t.length >= 3 && t.length <= max);
    if (animal.length) {
      const last = animal[animal.length - 1];
      if (last.length >= 4) return last;
      animal.sort((a, b) => b.length - a.length);
      return animal[0];
    }
    return null;
  }

  function wordsFrom(animals, max) {
    const out = [];
    const seen = new Set();
    for (const a of animals) {
      const word = gridWord(a.name, max);
      if (!word || seen.has(word)) continue;
      seen.add(word);
      out.push({ id: a.id, name: a.name, word, fact: a.fact || "", hunt: a.card });
    }
    return out;
  }

  function poolFor(max) {
    const map = byId();
    const info = placeInfo();
    let listed = [];
    if (info) listed = info.ids.map((id) => map[id]).filter(Boolean);
    let words = wordsFrom(listed, max);
    if (words.length < 4) {
      const have = new Set(words.map((w) => w.word));
      for (const extra of wordsFrom(data.animals.slice(), max)) {
        if (have.has(extra.word)) continue;
        words.push(extra);
        have.add(extra.word);
        if (words.length >= 4) break;
      }
    }
    return words;
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

  function canPlace(g, word, r, c, dr, dc, n) {
    for (let i = 0; i < word.length; i++) {
      const rr = r + i * dr;
      const cc = c + i * dc;
      if (rr < 0 || cc < 0 || rr >= n || cc >= n) return false;
      const ch = g[rr][cc];
      if (ch && ch !== word[i]) return false;
    }
    return true;
  }

  function buildGrid(words, n) {
    const dirs = [
      [0, 1],
      [1, 0],
    ];
    for (let attempt = 0; attempt < 40; attempt++) {
      const g = Array.from({ length: n }, () => Array(n).fill(""));
      const placed = [];
      const order = shuffle(words.slice());
      let ok = true;
      for (const entry of order) {
        const spots = [];
        for (const [dr, dc] of dirs) {
          for (let r = 0; r < n; r++) {
            for (let c = 0; c < n; c++) {
              if (canPlace(g, entry.word, r, c, dr, dc, n)) spots.push([r, c, dr, dc]);
            }
          }
        }
        if (!spots.length) {
          ok = false;
          break;
        }
        const [r, c, dr, dc] = spots[Math.floor(Math.random() * spots.length)];
        for (let i = 0; i < entry.word.length; i++) g[r + i * dr][c + i * dc] = entry.word[i];
        placed.push(entry);
      }
      if (ok && placed.length === words.length) {
        const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        for (let r = 0; r < n; r++) {
          for (let c = 0; c < n; c++) {
            if (!g[r][c]) g[r][c] = alphabet[Math.floor(Math.random() * 26)];
          }
        }
        return { grid: g, placed };
      }
    }
    return null;
  }

  function pickRound(mode) {
    size = mode === "hard" ? HARD : EASY;
    const want = mode === "hard" ? HARD_WORDS : EASY_WORDS;
    const pool = shuffle(poolFor(size).slice());
    const take = pool.slice(0, Math.max(4, Math.min(want, pool.length)));
    // try full set, then drop words if the grid cannot hold them
    for (let n = take.length; n >= 4; n--) {
      const built = buildGrid(take.slice(0, n), size);
      if (built) return built;
    }
    return buildGrid(take.slice(0, 4), size);
  }

  function cellKey(r, c) {
    return r + "," + c;
  }

  function paint() {
    for (const btn of cells) {
      const key = cellKey(btn.dataset.r, btn.dataset.c);
      const onPath = path.some((p) => p.r === +btn.dataset.r && p.c === +btn.dataset.c);
      btn.classList.toggle("is-found", foundCells.has(key));
      btn.classList.toggle("is-path", onPath);
      const isStart = !!(tapStart && tapStart.r === +btn.dataset.r && tapStart.c === +btn.dataset.c && path.length <= 1);
      btn.classList.toggle("is-start", isStart);
    }
  }

  function cellFromPoint(x, y) {
    const el = document.elementFromPoint(x, y);
    if (!el) return null;
    return el.closest ? el.closest(".kz-ws-cell") : null;
  }

  function asStep(a, b) {
    const dr = Math.sign(b.r - a.r);
    const dc = Math.sign(b.c - a.c);
    if (dr && dc) return null; // no diagonals
    if (!dr && !dc) return { dr: 0, dc: 0 };
    return { dr, dc };
  }

  function lineBetween(a, b) {
    const step = asStep(a, b);
    if (!step) return null;
    if (!step.dr && !step.dc) return [{ r: a.r, c: a.c }];
    const out = [];
    let r = a.r;
    let c = a.c;
    while (true) {
      out.push({ r, c });
      if (r === b.r && c === b.c) return out;
      r += step.dr;
      c += step.dc;
      if (out.length > size) return null;
    }
  }

  function pathWord(p) {
    return p.map((cell) => grid[cell.r][cell.c]).join("");
  }

  function tryMatch(p) {
    if (!p || p.length < 3) return null;
    const letters = pathWord(p);
    const rev = letters.split("").reverse().join("");
    for (const entry of entries) {
      if (found.has(entry.word)) continue;
      if (entry.word === letters || entry.word === rev) return entry;
    }
    return null;
  }

  function markFound(entry, p) {
    found.add(entry.word);
    for (const cell of p) foundCells.add(cellKey(cell.r, cell.c));
    const item = els.list.querySelector(`[data-word="${entry.word}"]`);
    if (item) item.classList.add("is-found");
    updateStatus();
    say("You found " + entry.name + ".");
    path = [];
    tapStart = null;
    paint();
    if (found.size === entries.length) win();
  }

  function updateStatus() {
    if (els.status) els.status.textContent = `${found.size} of ${entries.length} words`;
  }

  function onDown(ev) {
    const btn = ev.target.closest && ev.target.closest(".kz-ws-cell");
    if (!btn) return;
    ev.preventDefault();
    els.grid.setPointerCapture?.(ev.pointerId);
    dragging = true;
    moved = false;
    const cell = { r: +btn.dataset.r, c: +btn.dataset.c };
    path = [cell];
    paint();
  }

  function onMove(ev) {
    if (!dragging) return;
    const btn = cellFromPoint(ev.clientX, ev.clientY);
    if (!btn || !els.grid.contains(btn)) return;
    const cell = { r: +btn.dataset.r, c: +btn.dataset.c };
    const last = path[path.length - 1];
    if (last && last.r === cell.r && last.c === cell.c) return;
    moved = true;
    if (path.length === 1) {
      if (!asStep(path[0], cell) || (cell.r !== path[0].r && cell.c !== path[0].c)) return;
      // fill intermediates (in case of fast move)
      const line = lineBetween(path[0], cell);
      if (line) path = line;
      paint();
      return;
    }
    const start = path[0];
    const line = lineBetween(start, cell);
    if (!line) return;
    path = line;
    paint();
  }

  function onUp(ev) {
    if (!dragging) return;
    dragging = false;
    try {
      els.grid.releasePointerCapture?.(ev.pointerId);
    } catch (e) {}
    const match = tryMatch(path);
    if (match) {
      markFound(match, path);
      return;
    }
    if (!moved && path.length === 1) {
      const cell = path[0];
      if (!tapStart) {
        tapStart = cell;
        path = [cell];
        say("Now tap the last letter of the word.");
        paint();
        return;
      }
      const line = lineBetween(tapStart, cell);
      const hit = tryMatch(line);
      if (hit) {
        markFound(hit, line);
        return;
      }
      tapStart = cell;
      path = [cell];
      say("Now tap the last letter of the word.");
      paint();
      return;
    }
    path = tapStart ? [tapStart] : [];
    paint();
  }

  function renderGrid() {
    els.grid.dataset.size = String(size);
    els.grid.style.gridTemplateColumns = `repeat(${size}, minmax(0, 1fr))`;
    els.play.classList.toggle("is-wide", size === HARD);
    els.grid.replaceChildren();
    cells = [];
    for (let r = 0; r < size; r++) {
      for (let c = 0; c < size; c++) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "kz-ws-cell";
        btn.dataset.r = String(r);
        btn.dataset.c = String(c);
        btn.textContent = grid[r][c];
        btn.setAttribute("role", "gridcell");
        btn.setAttribute("aria-label", `Row ${r + 1}, column ${c + 1}, ${grid[r][c]}`);
        els.grid.appendChild(btn);
        cells.push(btn);
      }
    }
  }

  function renderList() {
    els.list.replaceChildren();
    for (const entry of entries) {
      const li = document.createElement("li");
      li.dataset.word = entry.word;
      li.textContent = entry.name;
      els.list.appendChild(li);
    }
  }

  function start(mode) {
    lastMode = mode;
    const built = pickRound(mode);
    if (!built) {
      say("The words could not be placed. Try again.");
      return;
    }
    grid = built.grid;
    entries = built.placed;
    found = new Set();
    foundCells = new Set();
    path = [];
    tapStart = null;
    dragging = false;
    els.setup.hidden = true;
    els.finish.hidden = true;
    els.play.hidden = false;
    renderGrid();
    renderList();
    updateStatus();
    say("Find a word from the list.");
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
          game_name: "word_search",
          difficulty: lastMode,
          place: info ? placeSlug : "all",
        });
      }
    } catch (e) {}
  }

  function ready() {
    const info = placeInfo();
    if (info && els.place) {
      els.place.hidden = false;
      els.place.textContent = `${info.name} animals`;
    }
    els.easy.addEventListener("click", () => start("easy"));
    els.hard.addEventListener("click", () => start("hard"));
    els.again.addEventListener("click", () => start(lastMode));
    els.grid.addEventListener("pointerdown", onDown);
    els.grid.addEventListener("pointermove", onMove);
    els.grid.addEventListener("pointerup", onUp);
    els.grid.addEventListener("pointercancel", onUp);
    els.grid.addEventListener("lostpointercapture", () => {
      /* keep path until pointerup */
    });
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
      say("The animal names could not load. Try the page again when the signal is stronger.");
      if (els.easy) els.easy.disabled = true;
      if (els.hard) els.hard.disabled = true;
    });
})();
