/**
 * Study-card quiz: tap a choice. Wrong greys + disables that pick for a second try.
 * Correct (first or later) shows why and scores. Show answers still reveals the key.
 * Level keys stay easy / hard / zoologist; visible names come from FPStudyLevelName.
 * Lion, giraffe, and African elephant ship JR + Park Ranger + Zoologist
 * (query ?level= or picker).
 */
(() => {
  const LETTERS = ["A", "B", "C"];

  function pack() {
    return document.querySelector(".card-study-pack");
  }

  function questions(root) {
    return [...(root || document).querySelectorAll(".study-q")];
  }

  function esc(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function normalizeLevel(raw) {
    const key = String(raw || "")
      .trim()
      .toLowerCase()
      .replace(/\s+/g, "-");
    if (key === "hard" || key === "park-ranger") return "hard";
    if (key === "easy" || key === "junior-ranger") return "easy";
    if (key === "zoologist") return "zoologist";
    return "";
  }

  function levelFromQuery() {
    try {
      return normalizeLevel(new URLSearchParams(window.location.search).get("level"));
    } catch (_) {
      return "";
    }
  }

  function rawCard(id) {
    const cards = window.FP_STUDY_CARDS || {};
    return cards[id] || null;
  }

  function shippedLevels(id) {
    const raw = rawCard(id);
    const levels = (raw && raw.levels) || {};
    return ["easy", "hard", "zoologist"].filter((key) => levels[key] && Array.isArray(levels[key].questions));
  }

  function flattenDeck(id, level) {
    const raw = rawCard(id);
    if (!raw) return null;
    const want = normalizeLevel(level) || "easy";
    let pack;
    let used = want;
    if (raw.levels && raw.levels[want]) {
      pack = raw.levels[want];
    } else if (Array.isArray(raw.questions) && (raw.level || "easy") === want) {
      pack = raw;
    } else if (raw.levels && raw.levels.easy) {
      pack = raw.levels.easy;
      used = "easy";
    } else {
      return null;
    }
    const questions = pack.questions || [];
    if (questions.length !== 10) return null;
    const label =
      (typeof window.FPStudyLevelName === "function" && window.FPStudyLevelName(used)) ||
      pack.level_label ||
      "";
    return {
      id: raw.id || id,
      level: used,
      level_label: label,
      source: raw.source || "",
      source_note: raw.source_note || "",
      teach: pack.teach || [],
      talk_about: pack.talk_about || raw.talk_about || [],
      push_further: pack.push_further || raw.push_further || [],
      questions,
    };
  }

  function questionHtml(q) {
    const choices = (q.choices || []).slice(0, 3).map((label, i) => {
      const letter = LETTERS[i] || "";
      return (
        `<button type="button" class="choice study-choice" data-letter="${letter}" data-choice="${esc(label)}">` +
        `<span class="dot" aria-hidden="true"></span>` +
        `<span><span class="study-letter">${letter}</span> ${esc(label)}</span>` +
        `</button>`
      );
    });
    return (
      `<section class="mission card-talk-q study-q" data-slot="${esc(String(q.slot || ""))}" ` +
      `data-qid="${esc(q.id || "")}" data-correct="${esc(q.correct || "")}">` +
      `<div class="mission-head"><span class="badge">${esc(String(q.slot || ""))}</span>` +
      `<p class="mission-title">${esc(q.title || "")}</p></div>` +
      `<h3 class="mission-q">${esc(q.stem || "")}</h3>` +
      `<div class="choices" data-multi="0" data-count="3">${choices.join("")}</div>` +
      `<p class="study-why" hidden>${esc(q.why || "")}</p>` +
      `</section>`
    );
  }

  function teachStorageKey(id) {
    return "fp-study-teach-open:" + String(id || "");
  }

  function teachWasOpen(id) {
    try {
      return sessionStorage.getItem(teachStorageKey(id)) === "1";
    } catch (_) {
      return false;
    }
  }

  function rememberTeachOpen(id, open) {
    try {
      sessionStorage.setItem(teachStorageKey(id), open ? "1" : "0");
    } catch (_) {
      /* ignore */
    }
  }

  function teachHtml(teach, id) {
    const lines = (teach || []).filter(Boolean);
    if (!lines.length) return "";
    const openAttr = teachWasOpen(id) ? " open" : "";
    return (
      `<details class="study-teach"${openAttr}>` +
      `<summary class="study-teach-kicker">Learn first ` +
      `<span class="study-teach-hint">— tap to open</span></summary>` +
      `<ul>${lines.map((line) => `<li>${esc(line)}</li>`).join("")}</ul></details>`
    );
  }

  function deepenHtml(deck) {
    const talk = (deck && deck.talk_about) || [];
    const push = (deck && deck.push_further) || [];
    if (!talk.length && !push.length) return "";
    function col(title, lines) {
      if (!lines.length) return "";
      return (
        `<div class="study-deepen-col"><p class="study-deepen-kicker">${esc(title)}</p>` +
        `<ol>${lines.map((line) => `<li>${esc(line)}</li>`).join("")}</ol></div>`
      );
    }
    return (
      `<aside class="study-deepen" hidden aria-label="Go further">` +
      col("Talk about it", talk) +
      col("Push further", push) +
      `</aside>`
    );
  }

  function markChoice(qEl, btn, revealed) {
    if (!qEl || !btn) return;
    if (btn.disabled || btn.classList.contains("is-wrong-pick")) return;
    if (qEl.classList.contains("mission-ok")) return;

    const correct = (qEl.getAttribute("data-correct") || "").toUpperCase();
    const letter = (btn.getAttribute("data-letter") || "").toUpperCase();
    const why = qEl.querySelector(".study-why");
    const isRight = letter === correct;

    if (isRight) {
      btn.classList.add("is-correct-pick");
      btn.setAttribute("aria-pressed", "true");
      if (why) why.hidden = false;
      qEl.classList.add("mission-ok");
      qEl.classList.remove("mission-try");
      qEl.setAttribute("data-picked", letter);
      qEl.querySelectorAll(".study-choice").forEach((b) => {
        if (b !== btn) b.disabled = true;
      });
    } else {
      btn.classList.add("is-wrong-pick");
      btn.disabled = true;
      btn.setAttribute("aria-pressed", "false");
      // Second try: keep prior wrongs; do not mark the key or show why.
      if (!revealed && why) why.hidden = true;
      qEl.classList.remove("mission-ok");
      qEl.setAttribute("data-picked", letter);
    }
    if (revealed) qEl.setAttribute("data-revealed", "1");
  }

  function scoreOf(root) {
    let n = 0;
    questions(root).forEach((qEl) => {
      const picked = qEl.getAttribute("data-picked") || "";
      const correct = (qEl.getAttribute("data-correct") || "").toUpperCase();
      if (picked && picked === correct) n += 1;
    });
    return n;
  }

  function paintScore(root) {
    const el = root.querySelector("[data-study-correct]");
    if (el) el.textContent = String(scoreOf(root));
  }

  function revealAll(root, on) {
    questions(root).forEach((qEl) => {
      const correct = (qEl.getAttribute("data-correct") || "").toUpperCase();
      const why = qEl.querySelector(".study-why");
      if (on) {
        qEl.querySelectorAll(".study-choice").forEach((b) => {
          const letter = (b.getAttribute("data-letter") || "").toUpperCase();
          b.classList.toggle("is-correct-key", letter === correct);
        });
        if (why) why.hidden = false;
        qEl.setAttribute("data-revealed", "1");
      } else if (!qEl.getAttribute("data-picked")) {
        qEl.querySelectorAll(".study-choice").forEach((b) => {
          b.classList.remove("is-correct-key", "is-correct-pick", "is-wrong-pick");
          b.setAttribute("aria-pressed", "false");
          b.disabled = false;
        });
        if (why) why.hidden = true;
        qEl.removeAttribute("data-revealed");
        qEl.classList.remove("mission-ok", "mission-try");
      }
    });
    const btn = root.querySelector("[data-study-reveal]");
    if (btn) {
      btn.textContent = on ? "Hide answers" : "Show answers";
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    }
    root.setAttribute("data-revealed", on ? "1" : "0");
    const deepen = root.querySelector(".study-deepen");
    if (deepen) deepen.hidden = !on;
  }

  function paintPicker(root, level) {
    root.querySelectorAll("[data-study-pick]").forEach((btn) => {
      const on = btn.getAttribute("data-study-pick") === level;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    });
    const badge = root.querySelector(".study-level-badge");
    if (badge && typeof window.FPStudyLevelName === "function") {
      badge.textContent = window.FPStudyLevelName(level);
    }
  }

  function rememberLevel(level) {
    try {
      const url = new URL(window.location.href);
      if (level && level !== "easy") url.searchParams.set("level", level);
      else url.searchParams.delete("level");
      history.replaceState(null, "", url.pathname + url.search + url.hash);
    } catch (_) {
      /* ignore */
    }
  }

  function refreshPrintTemplate(deck) {
    const tpl = document.getElementById("study-print-template");
    if (!tpl || !deck || !window.FPPrint || typeof window.FPPrint.buildStudyCardHtml !== "function") {
      return;
    }
    const item = window.FPPrint.getItem ? window.FPPrint.getItem(deck.id, null) : null;
    const venue = window.FPPrint.getVenue && item ? window.FPPrint.getVenue(item.venue) : null;
    if (!item) return;
    tpl.innerHTML = window.FPPrint.buildStudyCardHtml(item, venue, deck);
  }

  function applyDeck(root, deck) {
    if (!root || !deck) return;
    root.setAttribute("data-study-level", deck.level);
    root.setAttribute("data-revealed", "0");
    const teach = root.querySelector(".study-teach");
    const nextTeach = teachHtml(deck.teach, deck.id);
    if (teach && nextTeach) {
      teach.outerHTML = nextTeach;
    } else if (teach && !nextTeach) {
      teach.remove();
    } else if (!teach && nextTeach) {
      const toolbar = root.querySelector(".study-toolbar");
      if (toolbar) toolbar.insertAdjacentHTML("beforebegin", nextTeach);
    }
    const nextDeepen = deepenHtml(deck);
    const deepen = root.querySelector(".study-deepen");
    if (deepen && nextDeepen) {
      deepen.outerHTML = nextDeepen;
    } else if (deepen && !nextDeepen) {
      deepen.remove();
    } else if (!deepen && nextDeepen) {
      const source = root.querySelector(".study-source");
      const gridEl = root.querySelector(".study-grid");
      if (source) source.insertAdjacentHTML("beforebegin", nextDeepen);
      else if (gridEl) gridEl.insertAdjacentHTML("afterend", nextDeepen);
    }
    const freshDeepen = root.querySelector(".study-deepen");
    if (freshDeepen) freshDeepen.hidden = true;
    const grid = root.querySelector(".study-grid");
    if (grid) grid.innerHTML = (deck.questions || []).map(questionHtml).join("");
    paintPicker(root, deck.level);
    paintScore(root);
    const reveal = root.querySelector("[data-study-reveal]");
    if (reveal) {
      reveal.textContent = "Show answers";
      reveal.setAttribute("aria-pressed", "false");
    }
    refreshPrintTemplate(deck);
  }

  function selectLevel(root, level) {
    const id = root.getAttribute("data-study-id") || "";
    const deck = flattenDeck(id, level);
    if (!deck) return;
    applyDeck(root, deck);
    rememberLevel(deck.level);
  }

  function bind(root) {
    root.addEventListener("click", (ev) => {
      const pick = ev.target.closest("[data-study-pick]");
      if (pick && root.contains(pick)) {
        const next = normalizeLevel(pick.getAttribute("data-study-pick")) || "easy";
        if (next !== (root.getAttribute("data-study-level") || "easy")) {
          selectLevel(root, next);
        }
        return;
      }
      const choice = ev.target.closest(".study-choice");
      if (choice && root.contains(choice)) {
        const qEl = choice.closest(".study-q");
        if (!qEl || choice.disabled || choice.classList.contains("is-wrong-pick")) return;
        markChoice(qEl, choice, root.getAttribute("data-revealed") === "1");
        paintScore(root);
        return;
      }
      const reveal = ev.target.closest("[data-study-reveal]");
      if (reveal && root.contains(reveal)) {
        const on = root.getAttribute("data-revealed") !== "1";
        revealAll(root, on);
      }
    });
    root.addEventListener(
      "toggle",
      (ev) => {
        const details = ev.target;
        if (!details || !details.classList || !details.classList.contains("study-teach")) return;
        rememberTeachOpen(root.getAttribute("data-study-id") || "", details.open);
      },
      true
    );
  }

  function boot() {
    const root = pack();
    if (!root) return;
    bind(root);
    const id = root.getAttribute("data-study-id") || "";
    const wanted = levelFromQuery() || root.getAttribute("data-study-level") || "easy";
    const available = shippedLevels(id);
    const level = available.includes(wanted) ? wanted : "easy";
    const deck = flattenDeck(id, level);
    if (deck && (deck.level !== (root.getAttribute("data-study-level") || "easy") || levelFromQuery() === "hard" || levelFromQuery() === "zoologist")) {
      applyDeck(root, deck);
      rememberLevel(deck.level);
    } else {
      paintPicker(root, root.getAttribute("data-study-level") || "easy");
      paintScore(root);
      const details = root.querySelector("details.study-teach");
      if (details && teachWasOpen(id)) details.open = true;
    }
    const deckEl = document.getElementById("study-card-data");
    if (deckEl && window.FP_STUDY_CARDS) {
      try {
        const inline = JSON.parse(deckEl.textContent || "{}");
        if (inline && inline.id) {
          window.FP_STUDY_CARDS[inline.id] = window.FP_STUDY_CARDS[inline.id] || inline;
        }
      } catch (_) {
        /* ignore */
      }
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
