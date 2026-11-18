/* KZK Science Bee: tonight's round + two-kid buzzer. v1
 * Game state lives in memory only. localStorage keeps settings (band, mode,
 * topics, length, score on/off) and nothing else. No sounds, no media, no
 * network requests after load. */
(function () {
  "use strict";
  var BANK = window.SB_BANK;
  var app = document.getElementById("sb-app");
  if (!BANK || !app) return;

  var KEY = "kzk-sb-settings-v1";
  var TIMER_SECONDS = 10;
  var TOPIC_KEYS = BANK.topics.map(function (t) { return t.key; });
  var TOPIC_LABEL = {};
  BANK.topics.forEach(function (t) { TOPIC_LABEL[t.key] = t.label; });
  var BAND_LABEL = { little: "Little", big: "Big" };
  var PLAYERS = [
    { id: 0, name: "Otter", emoji: "\uD83E\uDDA6", cls: "p1" },
    { id: 1, name: "Owl", emoji: "\uD83E\uDD89", cls: "p2" }
  ];
  var CHEERS = [
    "Super science thinking tonight!",
    "Brains on, and what great guesses!",
    "That was a real science bee round!",
    "Curious minds win every time.",
    "Scientists ask questions, and you answered them!"
  ];
  var TALKS = [
    "Talk about it: which question made you think the hardest?",
    "Talk about it: what is one new thing you learned tonight?",
    "Talk about it: which animal or planet would you like to learn more about?",
    "Talk about it: if you could ask a scientist one question, what would it be?"
  ];

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function shuffle(a) {
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }
  function track(name, params) {
    try {
      var fn = (window.OneLessAnalytics && window.OneLessAnalytics.track) || window.trackEvent;
      if (typeof fn === "function") fn(name, params || {});
    } catch (e) { /* analytics must never break the game */ }
  }

  /* ---------- settings (localStorage: settings only) ---------- */
  var DEFAULTS = { mode: "solo", soloBand: "little", p1Band: "little", p2Band: "big", kind: "mixed", length: 8, topics: TOPIC_KEYS.slice(), showScore: true };
  function loadSettings() {
    var s = {};
    try { s = JSON.parse(window.localStorage.getItem(KEY) || "{}") || {}; } catch (e) { s = {}; }
    var out = {};
    Object.keys(DEFAULTS).forEach(function (k) { out[k] = s[k] !== undefined ? s[k] : DEFAULTS[k]; });
    if (["solo", "buzz"].indexOf(out.mode) < 0) out.mode = "solo";
    ["soloBand", "p1Band", "p2Band"].forEach(function (k) { if (["little", "big"].indexOf(out[k]) < 0) out[k] = DEFAULTS[k]; });
    if ([8, 10].indexOf(out.length) < 0) out.length = 8;
    if (["mixed", "pictures"].indexOf(out.kind) < 0) out.kind = "mixed";
    if (!Array.isArray(out.topics)) out.topics = TOPIC_KEYS.slice();
    out.topics = out.topics.filter(function (t) { return TOPIC_KEYS.indexOf(t) >= 0; });
    if (!out.topics.length) out.topics = TOPIC_KEYS.slice();
    out.showScore = out.showScore !== false;
    return out;
  }
  function saveSettings() {
    try {
      window.localStorage.setItem(KEY, JSON.stringify({
        mode: S.mode, soloBand: S.soloBand, p1Band: S.p1Band, p2Band: S.p2Band,
        kind: S.kind, length: S.length, topics: urlTopic ? savedTopics : S.topics, showScore: S.showScore
      }));
    } catch (e) { /* private mode: fine */ }
  }

  var S = loadSettings();
  var savedTopics = S.topics.slice();
  var urlTopic = null;    // a ?topic= link picks topics for this visit only
  (function applyUrl() {
    var m = /[?&]topic=([a-z]+)/.exec(window.location.search);
    if (m && TOPIC_KEYS.indexOf(m[1]) >= 0) { urlTopic = m[1]; S.topics = [m[1]]; }
    if (window.location.hash === "#buzzer") S.mode = "buzz";
  })();

  /* ---------- round state (memory only) ---------- */
  var seen = {};          // ids asked this visit, so Play again brings fresh questions
  var R = null;           // current round
  var timerId = null;
  var wakeLock = null;

  function bandsFor(n) {
    var out = [];
    for (var i = 0; i < n; i++) {
      if (S.mode === "solo") out.push(S.soloBand);
      else if (S.p1Band === S.p2Band) out.push(S.p1Band);
      else out.push(i % 2 === 0 ? "little" : "big");
    }
    return out;
  }

  function pickOne(pool, used, prefer) {
    var fresh = pool.filter(function (q) { return !used[q.id] && !seen[q.id]; });
    var any = pool.filter(function (q) { return !used[q.id]; });
    var src = fresh.length ? fresh : any;
    if (!src.length) return null;
    if (prefer) {
      var p = src.filter(prefer);
      if (p.length) src = p;
    }
    return src[Math.floor(Math.random() * src.length)];
  }

  function buildRound() {
    var n = S.length;
    var topics = S.topics.length ? S.topics : TOPIC_KEYS;
    var bands = bandsFor(n);
    var used = {};
    var list = [];
    var topicOrder = shuffle(topics.slice());
    var lastTopic = null;
    var picSlots = S.kind === "pictures" ? null : { 2: true, 5: true };
    for (var i = 0; i < n; i++) {
      var band = bands[i];
      var inBand = BANK.questions.filter(function (q) { return q.band === band; });
      var inTopics = inBand.filter(function (q) { return topics.indexOf(q.topic) >= 0; });
      var pool;
      if (S.kind === "pictures") {
        pool = inTopics.filter(function (q) { return q.pic; });
        if (pool.filter(function (q) { return !used[q.id]; }).length === 0) pool = inBand.filter(function (q) { return q.pic; });
      } else if (picSlots[i]) {
        pool = inTopics.filter(function (q) { return q.pic; });
        if (pool.filter(function (q) { return !used[q.id]; }).length === 0) pool = inTopics;
      } else {
        pool = inTopics.filter(function (q) { return !q.pic; });
      }
      if (pool.filter(function (q) { return !used[q.id]; }).length === 0) pool = inTopics.length ? inTopics : inBand;
      var want = topicOrder[i % topicOrder.length];
      var prefer;
      if (i === 0) prefer = function (q) { return q.easy; };
      else if (topics.length > 1) prefer = function (q) { return q.topic === want && q.topic !== lastTopic; };
      var q = pickOne(pool, used, prefer) || pickOne(inBand, used, null);
      if (!q) break;
      used[q.id] = true;
      lastTopic = q.topic;
      list.push(q);
    }
    // Guaranteed easy win to finish: youngest band in play, easy-flagged.
    var finalBand = (S.mode === "solo" ? S.soloBand : ((S.p1Band === "little" || S.p2Band === "little") ? "little" : "big"));
    var easyPool = BANK.questions.filter(function (q) { return q.easy && q.band === finalBand; });
    var easyInTopics = easyPool.filter(function (q) { return topics.indexOf(q.topic) >= 0; });
    var fin = pickOne(easyInTopics.length ? easyInTopics : easyPool, used, null) || pickOne(easyPool, {}, null);
    var items = list.map(function (q) { return makeItem(q, false); });
    if (fin) items.push(makeItem(fin, true));
    items.forEach(function (it) { seen[it.q.id] = true; });
    return {
      items: items, idx: 0,
      stars: [0, 0], solo: 0,
      missed: [],
      players: S.mode === "buzz" ? PLAYERS : [],
      warm: BANK.warmups[Math.floor(Math.random() * BANK.warmups.length)]
    };
  }

  function makeItem(q, isFinal) {
    var choices = shuffle([q.a].concat(q.wrong));
    var simple = shuffle([q.a, q.wrong[0]]);
    return {
      q: q, final: isFinal,
      choices: choices, simple: simple,
      level: (q.band === "little" || isFinal) ? 1 : 0,  // 0 open, 1 all choices, 2 two choices
      hint: false, revealed: false, result: null, tried: {},
      buzzed: null, out: {}, armedAt: 0
    };
  }

  /* ---------- screens ---------- */
  var confettiBox = null;
  function setInGame(on) {
    document.body.classList.toggle("sb-ingame", !!on);
    if (on && confettiBox && confettiBox.parentNode) confettiBox.parentNode.removeChild(confettiBox);
  }
  function top() {
    try { window.scrollTo(0, 0); } catch (e) { /* ignore */ }
  }
  function clearTimer() {
    if (timerId) { window.clearInterval(timerId); timerId = null; }
  }
  function keepAwake(on) {
    try {
      if (on && navigator.wakeLock && !wakeLock) {
        navigator.wakeLock.request("screen").then(function (l) { wakeLock = l; }).catch(function () {});
      } else if (!on && wakeLock) {
        wakeLock.release().catch(function () {}); wakeLock = null;
      }
    } catch (e) { /* not supported */ }
  }

  function segBtn(group, value, label, current) {
    return '<button type="button" data-set="' + group + '" data-val="' + esc(value) + '" aria-pressed="' + (String(current) === String(value)) + '">' + label + "</button>";
  }

  function renderSetup() {
    clearTimer(); setInGame(false); keepAwake(false);
    var h = '<section class="sb-card">';
    h += '<h1>Tonight&rsquo;s science bee</h1>';
    h += '<p class="sb-sub">10 to 15 minutes: a move-around warm-up, ' + S.length + ' questions, then an easy win.</p>';
    h += "<h2>Who&rsquo;s playing?</h2>";
    h += '<div class="sb-seg">' + segBtn("mode", "solo", "One kid", S.mode) + segBtn("mode", "buzz", "Two kids: buzzer", S.mode) + "</div>";
    if (S.mode === "solo") {
      h += "<h2>Age band</h2>";
      h += '<div class="sb-seg">' + segBtn("soloBand", "little", "Little (Pre-K&ndash;K)", S.soloBand) + segBtn("soloBand", "big", "Big (1st&ndash;3rd)", S.soloBand) + "</div>";
    } else {
      h += '<p class="sb-small">Lay the phone flat between the kids. Each one taps the buzzer at their end. A Little player gets answer choices when they buzz in.</p>';
      h += '<div class="sb-players">';
      [["p1Band", PLAYERS[0]], ["p2Band", PLAYERS[1]]].forEach(function (pair) {
        h += '<div class="sb-player"><p class="sb-who">' + pair[1].emoji + " " + pair[1].name + "</p>";
        h += '<div class="sb-seg">' + segBtn(pair[0], "little", "Little", S[pair[0]]) + segBtn(pair[0], "big", "Big", S[pair[0]]) + "</div></div>";
      });
      h += "</div>";
    }
    h += "<h2>Kind of round</h2>";
    h += '<div class="sb-seg">' + segBtn("kind", "mixed", "Mixed, with 2 pictures", S.kind) + segBtn("kind", "pictures", "Picture round", S.kind) + "</div>";
    h += "<h2>How many questions?</h2>";
    h += '<div class="sb-seg">' + segBtn("length", 8, "8 + easy win", S.length) + segBtn("length", 10, "10 + easy win", S.length) + "</div>";
    h += "<h2>Topics</h2>";
    h += '<div class="sb-seg">';
    BANK.topics.forEach(function (t) {
      h += '<button type="button" class="sb-chip" data-topic="' + t.key + '" aria-pressed="' + (S.topics.indexOf(t.key) >= 0) + '">' + esc(t.label) + "</button>";
    });
    h += "</div>";
    h += '<div class="sb-row"><button type="button" class="sb-chip" data-score aria-pressed="' + S.showScore + '">Show stars (just for fun)</button></div>';
    h += '<button type="button" class="btn sb-go" data-start>Start tonight&rsquo;s round</button>';
    h += '<p class="sb-small">No sounds and nothing plays by itself. Scores stay on this phone only until the round ends. Practice inspired by kid science bees; not connected to any competition.</p>';
    h += "</section>";
    h += '<p class="sb-small"><a href="/science-bee/">About this game and the full question bank</a></p>';
    app.innerHTML = h;
  }

  function renderWarmup() {
    clearTimer(); setInGame(true); top();
    var w = R.warm;
    var h = '<section class="sb-card sb-warm">';
    h += topBar("Warm-up");
    h += '<p class="sb-sub">Move first! About one minute, everyone joins in.</p>';
    h += '<div class="sb-big-emoji" aria-hidden="true">' + w.emoji + "</div>";
    h += '<p class="sb-warm-text">' + esc(w.text) + "</p>";
    h += timerBlock(60, "Start 1-minute timer");
    h += '<div class="sb-tools" style="justify-content:center"><button type="button" class="btn ghost" data-warm-next>Another warm-up</button><button type="button" class="btn" data-begin>We&rsquo;re ready: first question</button></div>';
    h += "</section>";
    app.innerHTML = h;
  }

  function topBar(label) {
    return '<div class="sb-top"><span class="sb-progress">' + label + '</span><span><button type="button" class="sb-linkbtn" data-reshuffle>' + (R && R.confirmReshuffle ? "Tap again for a new round" : "New round") + '</button><button type="button" class="sb-linkbtn" data-end>End</button></span></div>';
  }

  function timerBlock(seconds, label) {
    return '<div class="sb-timerwrap" data-seconds="' + seconds + '"><button type="button" class="btn ghost" data-timer>\u23F1 ' + label + '</button><div class="sb-timer-live" hidden><span class="sb-timer"><span data-left>' + seconds + '</span> s</span><div class="sb-timer-bar"><span></span></div></div></div>';
  }

  function startTimer(wrap) {
    clearTimer();
    var total = parseInt(wrap.getAttribute("data-seconds"), 10) || TIMER_SECONDS;
    var live = wrap.querySelector(".sb-timer-live");
    var left = wrap.querySelector("[data-left]");
    var bar = wrap.querySelector(".sb-timer-bar span");
    var btn = wrap.querySelector("[data-timer]");
    var end = Date.now() + total * 1000;
    live.hidden = false;
    btn.textContent = "\u23F1 Restart timer";
    var tick = function () {
      var ms = Math.max(0, end - Date.now());
      var s = Math.ceil(ms / 1000);
      left.textContent = String(s);
      bar.style.width = (ms / (total * 1000) * 100) + "%";
      if (ms <= 0) {
        clearTimer();
        live.querySelector(".sb-timer").innerHTML = '<span class="sb-timer-done">Time! Take a guess.</span>';
      }
    };
    tick();
    timerId = window.setInterval(tick, 250);
  }

  function picHtml(q) {
    var p = q.pic;
    if (!p) return "";
    if (p.emoji) return '<div class="sb-gpic"><div class="sb-pic sb-pic-emoji" aria-hidden="true">' + p.emoji + "</div></div>";
    if (p.svg) return '<div class="sb-gpic"><div class="sb-pic sb-pic-svg">' + (BANK.svgs[p.svg] || "") + "</div></div>";
    if (p.photo) {
      var ph = BANK.photos[p.photo] || { alt: "", credit: "" };
      return '<div class="sb-gpic"><figure class="sb-pic sb-pic-photo"><picture style="display:contents"><source type="image/webp" srcset="/field-pack/photos/' + p.photo + '-480-v1.webp 480w, /field-pack/photos/' + p.photo + '-640-v1.webp 640w" sizes="66vw" /><img src="/field-pack/photos/' + p.photo + '.jpg?v=img2" alt="' + esc(ph.alt) + '" width="640" height="640" decoding="async" /></picture><figcaption>' + esc(ph.credit) + "</figcaption></figure></div>";
    }
    return "";
  }

  function currentChoices(it) {
    if (it.level === 0) return [];
    return it.level === 2 ? it.simple : it.choices;
  }

  function renderQuestion() {
    clearTimer(); setInGame(true);
    var it = R.items[R.idx];
    var q = it.q;
    var total = R.items.length;
    var buzz = S.mode === "buzz";
    var h = '<section class="sb-card">';
    h += topBar(it.final ? "Last one!" : "Question " + (R.idx + 1) + " of " + total);
    h += '<div>' + (it.final ? '<span class="sb-easy-tag">Easy win</span> ' : "") + '<span class="sb-topic-tag">' + esc(TOPIC_LABEL[q.topic]) + '</span><span class="sb-band-tag">' + BAND_LABEL[q.band] + "</span></div>";
    if (it.final && buzz) h += '<p class="sb-sub">Everybody answers together on this one!</p>';
    h += picHtml(q);
    h += '<p class="sb-qtext" data-qid="' + esc(q.id) + '">' + esc(q.q) + "</p>";
    var ch = currentChoices(it);
    if (ch.length) {
      h += '<div class="sb-choices" role="group" aria-label="Answer choices">';
      ch.forEach(function (c) {
        var cls = "sb-choice";
        if (it.revealed && c === q.a) cls += " is-right";
        else if (it.tried[c]) cls += " is-wrong";
        h += '<button type="button" class="' + cls + '" data-choice="' + esc(c) + '"' + (it.revealed ? " disabled" : "") + ">" + esc(c) + "</button>";
      });
      h += "</div>";
    }
    if (it.hint && !it.revealed) h += '<p class="sb-note sb-hint">\uD83D\uDCA1 Hint: ' + esc(q.hint) + "</p>";
    if (it.flash && !it.revealed) h += '<p class="sb-note sb-hint">' + esc(it.flash) + "</p>";
    if (it.revealed) {
      if (it.result === "right") h += '<p class="sb-note sb-yay">\u2B50 ' + esc(it.yay || "Yes!") + " The answer is <strong>" + esc(q.a) + "</strong>.</p>";
      h += '<p class="sb-note sb-fix">' + (it.result === "right" ? "" : "<strong>Good try!</strong> ") + esc(q.fix) + "</p>";
    }
    if (buzz && !it.final) h += '<p class="sb-status" role="status">' + buzzStatus(it) + "</p>";
    // Tools for the grown-up.
    h += '<div class="sb-tools">';
    if (!it.revealed) {
      if (!it.hint) h += '<button type="button" class="btn ghost" data-hint>\uD83D\uDCA1 Hint</button>';
      if (it.level === 0) h += '<button type="button" class="btn ghost" data-level="1">Give choices</button>';
      else if (it.level === 1 && it.choices.length > 2) h += '<button type="button" class="btn ghost" data-level="2">Make it simpler</button>';
      if (buzz && !it.final && it.buzzed !== null) {
        h += '<button type="button" class="btn" data-judge="right">Right \u2B50</button><button type="button" class="btn alt" data-judge="notyet">Not yet</button>';
      } else if (buzz && it.final) {
        h += '<button type="button" class="btn" data-together>We got it! \u2B50 for both</button>';
      } else if (!buzz && it.level === 0) {
        if (it.showAns) {
          h += '<p class="sb-note sb-fix" style="width:100%">Answer: <strong>' + esc(q.a) + "</strong></p>";
          h += '<button type="button" class="btn" data-judge="right">Got it \u2B50</button><button type="button" class="btn alt" data-judge="notyet">Not yet</button>';
        } else {
          h += '<button type="button" class="btn alt" data-showans>Show answer</button>';
        }
      }
      if (buzz || it.level > 0) h += '<button type="button" class="sb-linkbtn" data-skip>Show answer</button>';
    } else {
      h += '<button type="button" class="btn sb-go" data-next>' + (R.idx + 1 < R.items.length ? "Next question \u2192" : "Finish \uD83C\uDF89") + "</button>";
    }
    h += "</div>";
    if (!it.revealed) h += timerBlock(TIMER_SECONDS, "Start 10-second think timer");
    if (buzz && !it.final) h += buzzers(it);
    else if (S.showScore) h += '<p class="sb-small">Stars so far: ' + scoreText() + "</p>";
    h += "</section>";
    app.innerHTML = h;
    if (!it.armedAt) it.armedAt = Date.now() + 350; // ignore a carry-over tap from Next
  }

  function buzzStatus(it) {
    if (it.revealed) return "";
    if (it.buzzed !== null) {
      var p = PLAYERS[it.buzzed];
      return p.emoji + " " + p.name + " buzzed first! What&rsquo;s your answer?";
    }
    var outs = Object.keys(it.out);
    if (outs.length === 1) {
      var other = PLAYERS[outs[0] === "0" ? 1 : 0];
      return "Your turn to try, " + other.emoji + " " + other.name + "!";
    }
    return "Listen to the whole question, then buzz!";
  }

  function buzzers(it) {
    var h = '<div class="sb-buzzers">';
    PLAYERS.forEach(function (p) {
      var locked = it.revealed || it.out[p.id] || (it.buzzed !== null && it.buzzed !== p.id);
      var cls = "sb-buzz " + p.cls + (it.buzzed === p.id ? " is-buzzed" : "") + (it.out[p.id] ? " is-out" : "");
      h += '<button type="button" class="' + cls + '" data-buzz="' + p.id + '"' + (locked || it.buzzed === p.id ? " disabled" : "") + ' aria-label="' + p.name + ' buzzer">';
      h += '<span class="sb-buzz-emoji" aria-hidden="true">' + p.emoji + "</span>" + p.name;
      if (S.showScore) h += '<span class="sb-buzz-stars">\u2B50 ' + R.stars[p.id] + "</span>";
      h += "</button>";
    });
    return h + "</div>";
  }

  function scoreText() {
    if (S.mode === "buzz") return PLAYERS.map(function (p) { return p.emoji + " " + R.stars[p.id]; }).join(" \u00B7 ");
    return "\u2B50 " + R.solo;
  }

  function reveal(it, result, who) {
    it.revealed = true;
    it.result = result;
    if (result === "right") {
      var yays = ["Yes!", "You got it!", "Super!", "Brilliant!", "Nailed it!"];
      it.yay = (who !== undefined && who !== null && S.mode === "buzz" ? PLAYERS[who].name + ": " : "") + yays[Math.floor(Math.random() * yays.length)];
    } else {
      R.missed.push(it.q);
    }
  }

  function award(who) {
    if (S.mode === "buzz") {
      if (who === "both") { R.stars[0] += 1; R.stars[1] += 1; }
      else R.stars[who] += 1;
    } else {
      R.solo += 1;
    }
  }

  function renderFinish() {
    clearTimer(); setInGame(false); keepAwake(false); top();
    track("science_bee_round_complete", { mode: S.mode, kind: S.kind });
    var h = '<section class="sb-card sb-finish">';
    h += '<div class="sb-big-emoji" aria-hidden="true">\uD83C\uDF89</div>';
    h += "<h1>Round complete!</h1>";
    h += '<p class="sb-sub">' + esc(CHEERS[Math.floor(Math.random() * CHEERS.length)]) + "</p>";
    if (S.showScore) {
      h += '<div class="sb-scores">';
      if (S.mode === "buzz") {
        PLAYERS.forEach(function (p) { h += '<span class="sb-score ' + p.cls + '">' + p.emoji + " " + p.name + " \u2B50 " + R.stars[p.id] + "</span>"; });
      } else {
        h += '<span class="sb-score solo">\u2B50 ' + R.solo + " stars</span>";
      }
      h += "</div>";
      if (S.mode === "buzz") h += '<p class="sb-sub">Great buzzing, both of you!</p>';
    }
    h += "<p>" + esc(TALKS[Math.floor(Math.random() * TALKS.length)]) + "</p>";
    if (R.missed.length) {
      h += '<details class="sb-again"><summary class="sb-linkbtn">Ones to try again another night (' + R.missed.length + ")</summary><ul>";
      R.missed.forEach(function (q) { h += "<li>" + esc(q.q) + " <strong>" + esc(q.a) + "</strong></li>"; });
      h += "</ul></details>";
    }
    h += '<button type="button" class="btn sb-go" data-again>Play another round</button>';
    h += '<div class="sb-tools" style="justify-content:center"><button type="button" class="btn ghost" data-setup>Change settings</button></div>';
    h += "</section>";
    app.innerHTML = h;
    confetti();
  }

  function confetti() {
    if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    var box = document.createElement("div");
    box.className = "sb-confetti";
    box.setAttribute("aria-hidden", "true");
    var bits = ["\u2B50", "\uD83C\uDF1F", "\uD83E\uDDEA", "\uD83E\uDE90", "\uD83C\uDF31", "\uD83E\uDD8B"];
    for (var i = 0; i < 18; i++) {
      var s = document.createElement("span");
      s.textContent = bits[i % bits.length];
      s.style.left = Math.round(Math.random() * 95) + "%";
      s.style.animationDelay = (Math.random() * 0.6).toFixed(2) + "s";
      box.appendChild(s);
    }
    document.body.appendChild(box);
    confettiBox = box;
    window.setTimeout(function () { if (box.parentNode) box.parentNode.removeChild(box); }, 2800);
  }

  function startRound() {
    saveSettings();
    R = buildRound();
    keepAwake(true);
    // Warm the browser cache for any photo in this round so it still shows offline.
    R.items.forEach(function (it) {
      if (it.q.pic && it.q.pic.photo) { var im = new Image(); im.src = "/field-pack/photos/" + it.q.pic.photo + ".jpg?v=img2"; }
    });
    track("science_bee_round_start", { mode: S.mode, kind: S.kind });
    renderWarmup();
  }

  function next() {
    if (R.idx + 1 < R.items.length) { R.idx += 1; renderQuestion(); top(); }
    else renderFinish();
  }

  /* ---------- events ---------- */
  function onBuzz(id) {
    if (!R) return;
    var it = R.items[R.idx];
    if (!it || it.final || it.revealed || it.buzzed !== null || it.out[id]) return;
    if (Date.now() < it.armedAt) return;
    it.buzzed = id;
    it.flash = null;
    var band = id === 0 ? S.p1Band : S.p2Band;
    if (band === "little") {
      if (it.level === 0) it.level = it.q.band === "big" ? 2 : 1;
    }
    try { if (navigator.vibrate) navigator.vibrate(40); } catch (e) { /* ignore */ }
    renderQuestion();
  }

  // Buzzers react on pointerdown so the faster finger wins.
  app.addEventListener("pointerdown", function (ev) {
    var b = ev.target.closest && ev.target.closest("[data-buzz]");
    if (!b || b.disabled) return;
    ev.preventDefault();
    onBuzz(parseInt(b.getAttribute("data-buzz"), 10));
  });

  app.addEventListener("click", function (ev) {
    var t = ev.target.closest ? ev.target.closest("button") : null;
    if (!t) return;
    if (t.hasAttribute("data-buzz")) {
      // Keyboard / assistive tech path (pointerdown already handled taps).
      if (ev.detail === 0) onBuzz(parseInt(t.getAttribute("data-buzz"), 10));
      return;
    }
    var it = R && R.items[R.idx];
    if (t.hasAttribute("data-set")) {
      var g = t.getAttribute("data-set"), v = t.getAttribute("data-val");
      S[g] = g === "length" ? parseInt(v, 10) : v;
      renderSetup(); return;
    }
    if (t.hasAttribute("data-topic")) {
      var k = t.getAttribute("data-topic");
      var i = S.topics.indexOf(k);
      if (i >= 0) { if (S.topics.length > 1) S.topics.splice(i, 1); }
      else S.topics.push(k);
      urlTopic = null;  // the grown-up chose topics by hand: remember them
      renderSetup(); return;
    }
    if (t.hasAttribute("data-score")) { S.showScore = !S.showScore; renderSetup(); return; }
    if (t.hasAttribute("data-start") || t.hasAttribute("data-again")) { startRound(); return; }
    if (t.hasAttribute("data-setup")) { R = null; renderSetup(); top(); return; }
    if (t.hasAttribute("data-timer")) { startTimer(t.closest(".sb-timerwrap")); return; }
    if (t.hasAttribute("data-warm-next")) {
      var cur = R.warm, w = cur;
      while (BANK.warmups.length > 1 && w === cur) w = BANK.warmups[Math.floor(Math.random() * BANK.warmups.length)];
      R.warm = w; renderWarmup(); return;
    }
    if (t.hasAttribute("data-begin")) { R.idx = 0; renderQuestion(); top(); return; }
    if (t.hasAttribute("data-end")) { renderFinish(); return; }
    if (t.hasAttribute("data-reshuffle")) {
      if (R && R.confirmReshuffle) { startRound(); return; }
      R.confirmReshuffle = true;
      t.textContent = "Tap again for a new round";
      window.setTimeout(function () { if (R) R.confirmReshuffle = false; }, 4000);
      return;
    }
    if (!it) return;
    if (t.hasAttribute("data-hint")) { it.hint = true; it.flash = null; renderQuestion(); return; }
    if (t.hasAttribute("data-level")) { it.level = parseInt(t.getAttribute("data-level"), 10); it.flash = null; renderQuestion(); return; }
    if (t.hasAttribute("data-showans")) { it.showAns = true; renderQuestion(); return; }
    if (t.hasAttribute("data-skip")) { reveal(it, "skip"); renderQuestion(); return; }
    if (t.hasAttribute("data-next")) { next(); return; }
    if (t.hasAttribute("data-together")) { award("both"); reveal(it, "right"); renderQuestion(); return; }
    if (t.hasAttribute("data-judge")) {
      var right = t.getAttribute("data-judge") === "right";
      judge(it, right);
      return;
    }
    if (t.hasAttribute("data-choice")) {
      var c = t.getAttribute("data-choice");
      if (S.mode === "buzz" && !it.final && it.buzzed === null) {
        it.flash = "Buzz in first, then pick!";
        renderQuestion(); return;
      }
      if (S.mode === "buzz" && it.final) {
        if (c === it.q.a) { award("both"); reveal(it, "right"); }
        else { it.tried[c] = true; it.flash = "So close! Try another one together."; }
        renderQuestion(); return;
      }
      judge(it, c === it.q.a, c);
    }
  });

  function judge(it, right, choice) {
    var buzz = S.mode === "buzz";
    if (right) {
      var who = buzz ? it.buzzed : null;
      award(buzz ? it.buzzed : null);
      reveal(it, "right", who);
      renderQuestion();
      return;
    }
    if (choice !== undefined) it.tried[choice] = true;
    if (buzz) {
      it.out[it.buzzed] = true;
      it.buzzed = null;
      it.flash = null;
      it.armedAt = Date.now() + 250;
      if (Object.keys(it.out).length >= 2) reveal(it, "miss");
      renderQuestion();
      return;
    }
    // One kid: with choices, let them try again; open answers show the kind fix.
    var left = currentChoices(it).filter(function (c) { return c !== it.q.a && !it.tried[c]; });
    if (choice !== undefined && left.length > 0) {
      it.flash = "Not quite. Try another one!";
      renderQuestion();
      return;
    }
    reveal(it, "miss");
    renderQuestion();
  }

  renderSetup();
})();
