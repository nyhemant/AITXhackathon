/**
 * Easy study-card quiz: tap a choice to lock it, see why, optional score + Show answers.
 * Hard / Zoologist later can reuse the same 10 slots (data-study-level).
 */
(() => {
  function pack() {
    return document.querySelector(".card-study-pack");
  }

  function questions(root) {
    return [...(root || document).querySelectorAll(".study-q")];
  }

  function markChoice(qEl, btn, revealed) {
    const correct = (qEl.getAttribute("data-correct") || "").toUpperCase();
    const letter = (btn.getAttribute("data-letter") || "").toUpperCase();
    const why = qEl.querySelector(".study-why");
    qEl.querySelectorAll(".study-choice").forEach((b) => {
      b.setAttribute("aria-pressed", b === btn ? "true" : "false");
      b.classList.remove("is-correct-pick", "is-wrong-pick", "is-correct-key");
    });
    if (letter === correct) {
      btn.classList.add("is-correct-pick");
    } else {
      btn.classList.add("is-wrong-pick");
      const right = qEl.querySelector(`.study-choice[data-letter="${correct}"]`);
      if (right) right.classList.add("is-correct-key");
    }
    if (why) why.hidden = false;
    qEl.classList.toggle("mission-ok", letter === correct);
    qEl.classList.toggle("mission-try", letter !== correct);
    qEl.setAttribute("data-picked", letter);
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
  }

  function bind(root) {
    root.addEventListener("click", (ev) => {
      const choice = ev.target.closest(".study-choice");
      if (choice && root.contains(choice)) {
        const qEl = choice.closest(".study-q");
        if (!qEl) return;
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
  }

  function boot() {
    const root = pack();
    if (!root) return;
    bind(root);
    paintScore(root);
    const deckEl = document.getElementById("study-card-data");
    if (deckEl && window.FP_STUDY_CARDS) {
      try {
        const deck = JSON.parse(deckEl.textContent || "{}");
        if (deck && deck.id) window.FP_STUDY_CARDS[deck.id] = window.FP_STUDY_CARDS[deck.id] || deck;
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
