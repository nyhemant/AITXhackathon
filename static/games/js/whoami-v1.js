(() => {
  const DATA_URL = "/games/data/whoami-v1.json";
  const ROUNDS = 6;
  const CHOICES = 3;
  const root = document.getElementById("kz-whoami");
  if (!root) return;

  const params = new URLSearchParams(location.search);
  const placeSlug = (params.get("place") || "").trim();

  const els = {
    setup: document.getElementById("kz-setup"),
    play: document.getElementById("kz-play"),
    finish: document.getElementById("kz-finish"),
    place: document.getElementById("kz-place-label"),
    clues: document.getElementById("kz-clues"),
    choices: document.getElementById("kz-choices"),
    live: document.getElementById("kz-live"),
    status: document.getElementById("kz-status"),
    next: document.getElementById("kz-next"),
    hunt: document.getElementById("kz-hunt-link"),
    again: document.getElementById("kz-again"),
    start: document.getElementById("kz-start"),
  };

  let data = null;
  let deck = [];
  let pool = [];
  let round = 0;
  let locked = false;

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

  function animalsForPlace() {
    const map = byId();
    const info = placeInfo();
    let listed = [];
    if (info) listed = info.ids.map((id) => map[id]).filter((a) => a && a.clues && a.clues.length >= 2);
    if (listed.length >= ROUNDS) return listed;
    const have = new Set(listed.map((a) => a.id));
    for (const a of data.animals) {
      if (have.has(a.id) || !a.clues || a.clues.length < 2) continue;
      listed.push(a);
      have.add(a.id);
      if (listed.length >= ROUNDS) break;
    }
    return listed;
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

  function pickChoices(correct) {
    const others = pool.filter((a) => a.id !== correct.id);
    shuffle(others);
    const picks = [correct, ...others.slice(0, CHOICES - 1)];
    while (picks.length < CHOICES) {
      const extra = data.animals.find((a) => !picks.some((p) => p.id === a.id));
      if (!extra) break;
      picks.push(extra);
    }
    return shuffle(picks);
  }

  function cluesFor(animal) {
    const all = animal.clues.slice();
    const n = all.length >= 3 ? 3 : 2;
    return all.slice(0, n);
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function renderRound() {
    const animal = deck[round];
    locked = false;
    els.next.hidden = true;
    els.status.textContent = `Round ${round + 1} of ${ROUNDS}`;
    say("Listen to the clues, then pick an animal.");
    const clues = cluesFor(animal);
    els.clues.replaceChildren();
    clues.forEach((text, i) => {
      const li = document.createElement("li");
      li.textContent = text;
      els.clues.appendChild(li);
    });
    const options = pickChoices(animal);
    els.choices.replaceChildren();
    options.forEach((opt) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "kz-who-choice";
      btn.dataset.id = opt.id;
      btn.innerHTML =
        '<img alt="" width="88" height="88">' +
        "<span>" +
        escapeHtml(opt.name) +
        "</span>";
      const img = btn.querySelector("img");
      img.src = opt.photo;
      img.alt = opt.name;
      btn.addEventListener("click", () => onPick(btn, opt, animal));
      els.choices.appendChild(btn);
    });
  }

  function onPick(btn, opt, animal) {
    if (locked) return;
    locked = true;
    const buttons = [...els.choices.querySelectorAll(".kz-who-choice")];
    buttons.forEach((b) => {
      b.disabled = true;
    });
    const right = buttons.find((b) => b.dataset.id === animal.id);
    if (opt.id === animal.id) {
      btn.classList.add("is-right");
      say("Yes — that's the " + animal.name + ". High five!");
    } else {
      btn.classList.add("is-wrong");
      if (right) right.classList.add("is-right");
      say("This one is the " + animal.name + ".");
    }
    if (round + 1 < ROUNDS) {
      els.next.textContent = "Next";
      els.next.hidden = false;
      els.next.focus();
    } else {
      els.next.textContent = "See how you did";
      els.next.hidden = false;
      els.next.focus();
    }
  }

  function goNext() {
    if (round + 1 < ROUNDS) {
      round += 1;
      renderRound();
    } else {
      win();
    }
  }

  function start() {
    pool = animalsForPlace();
    deck = shuffle(pool.slice()).slice(0, ROUNDS);
    if (deck.length < ROUNDS) {
      say("Not enough animal cards to play yet.");
      return;
    }
    preload(pool);
    round = 0;
    els.setup.hidden = true;
    els.finish.hidden = true;
    els.play.hidden = false;
    renderRound();
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
          game_name: "who_am_i",
          difficulty: "standard",
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
    els.start.addEventListener("click", start);
    els.again.addEventListener("click", start);
    els.next.addEventListener("click", goNext);
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
      say("The animal clues could not load. Try the page again when the signal is stronger.");
      if (els.start) els.start.disabled = true;
    });
})();
