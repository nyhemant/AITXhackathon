/**
 * Field Trip Kit — deterministic mission composition (no network, no LLM).
 * Browser: window.FPMission
 * Node (SEO build): load via vm
 */
(function (root) {
  /**
   * Audience bands (UI chips). Internal keys stay short for data compatibility.
   * 2-3  → Little kids 2–4 (shorter, play-first sheet)
   * 4-5  → Kids 5–8
   * 6-8  → Big kids 9–12
   * adult → Solo adults / young tourists (not a parenting sheet)
   * Legacy "9+" in item age_fit maps to big kids + adults.
   */
  const AGE_ORDER = ["2-3", "4-5", "6-8", "adult"];
  const AGE_LABELS = {
    "2-3": "Little · 2–4",
    "4-5": "Kids · 5–8",
    "6-8": "Big · 9–12",
    adult: "Adults",
    // legacy display if stored mid-migrate
    "9+": "Adults",
  };
  const AGE_CHIP_LABELS = {
    "2-3": "2–4",
    "4-5": "5–8",
    "6-8": "9–12",
    adult: "Adults",
  };
  const TIME_N = { "1hr": 4, half: 6, full: 8, "90m": 4 };
  const TIME_LABELS = {
    "1hr": "~1 hr",
    "90m": "~90 min",
    half: "Half day",
    full: "Full day",
  };

  function normalizeAge(age) {
    const a = String(age || "4-5");
    if (a === "9+" || a === "adults" || a === "solo") return "adult";
    if (AGE_ORDER.includes(a)) return a;
    return "4-5";
  }

  function isAdult(age) {
    return normalizeAge(age) === "adult";
  }

  function isLittle(age) {
    return normalizeAge(age) === "2-3";
  }

  function needCount(time, age) {
    const base = TIME_N[time] || TIME_N.half || 6;
    const a = normalizeAge(age);
    if (a === "2-3") return Math.max(3, base - 2); // half → 4, shorter attention
    if (a === "adult") return Math.min(10, base + 1); // half → 7, denser solo day
    return base;
  }

  function defaultOptions() {
    return { age: "4-5", time: "half", interest: "", name: "", seed: 1, hunt: "classic" };
  }

  function normalizeHunt(h) {
    const s = String(h || "classic").toLowerCase();
    if (s === "alpha" || s === "ultra" || s === "expert") return "alpha";
    if (s === "bonus" || s === "hard" || s === "easter") return "bonus";
    return "classic";
  }

  function isBonusHunt(opts) {
    return normalizeHunt(opts && opts.hunt) === "bonus";
  }

  function isAlphaHunt(opts) {
    return normalizeHunt(opts && opts.hunt) === "alpha";
  }

  function isSpecialHunt(opts) {
    const h = normalizeHunt(opts && opts.hunt);
    return h === "bonus" || h === "alpha";
  }

  /** Venue-authored bonus pack, optional file overlay via wonders-style global. */
  function bonusPack(venue, bonusFile) {
    const slug = (venue && (venue.slug || venue.id)) || "";
    const local = (venue && venue.bonus_hunt) || null;
    if (local && (local.find_ids || local.challenges || local.easter_egg)) return local;
    const file = bonusFile || (typeof window !== "undefined" && window.FP_BONUS_HUNTS) || null;
    if (file && file.venues && file.venues[slug]) return file.venues[slug];
    if (file && file.generic) return file.generic;
    return null;
  }

  /** Alpha = extra-hard / cool second layer (venue.alpha_hunt or file.alpha). */
  function alphaPack(venue, bonusFile) {
    const slug = (venue && (venue.slug || venue.id)) || "";
    const local = (venue && venue.alpha_hunt) || null;
    if (local && (local.find_ids || local.challenges || local.easter_egg)) return local;
    const file = bonusFile || (typeof window !== "undefined" && window.FP_BONUS_HUNTS) || null;
    const alphaRoot = file && file.alpha;
    if (alphaRoot && alphaRoot.venues && alphaRoot.venues[slug]) return alphaRoot.venues[slug];
    if (alphaRoot && alphaRoot.generic) return alphaRoot.generic;
    // Soft fallback: reuse bonus pack if no alpha authored yet
    return bonusPack(venue, bonusFile);
  }

  function huntPack(venue, bonusFile, hunt) {
    const h = normalizeHunt(hunt);
    if (h === "alpha") return alphaPack(venue, bonusFile);
    if (h === "bonus") return bonusPack(venue, bonusFile);
    return null;
  }

  function contentMode(venue) {
    const m = (venue && venue.content_mode) || "";
    if (m === "wonder" || m === "hybrid" || m === "curated") return m;
    // Scaffolds / unaudited templates: wonder-first (honest long-tail)
    if ((venue && venue.list_confidence) === "template") return "wonder";
    if ((venue && venue.verified_by) === "catalog-scaffold") return "wonder";
    // Owner lists may be curated; plain "research" without content_mode is not a census
    if ((venue && venue.verified_by) === "owner") return "curated";
    if ((venue && venue.list_confidence) === "audited") return "curated";
    return "wonder";
  }

  /** Presence gate — never print a named find we only guessed. */
  const PRESENCE_OK = new Set(["verified", "high"]);
  const PRESENCE_BLOCK = new Set(["absent", "template", "medium"]);

  function listConfidence(venue) {
    const c = (venue && venue.list_confidence) || "";
    if (c === "audited" || c === "partial" || c === "template") return c;
    if ((venue && venue.verified_by) === "owner") return "partial";
    if ((venue && venue.verified_by) === "catalog-scaffold") return "template";
    // Hybrid "research" without a presence audit is template-risk
    if ((venue && venue.content_mode) === "hybrid") return "template";
    return "partial";
  }

  function doNotListSet(venue) {
    const out = new Set();
    for (const row of (venue && venue.do_not_list) || []) {
      if (!row) continue;
      if (typeof row === "string") {
        out.add(row.toLowerCase());
        continue;
      }
      if (row.catalog_id) out.add(String(row.catalog_id).toLowerCase());
      if (row.name) out.add(String(row.name).toLowerCase());
      if (row.id) out.add(String(row.id).toLowerCase());
    }
    return out;
  }

  function isWonderItem(it) {
    if (!it) return false;
    const id = String(it.id || "");
    if (id.startsWith("w_")) return true;
    if (String(it.zone || "").toLowerCase() === "wonder") return true;
    if (it.kind === "wonder") return true;
    return false;
  }

  /**
   * Named animals/exhibits need presence confidence.
   * Wonders always allowed. Grandfather: owner/partial venues may use
   * items without a presence field until Wave A tags them.
   */
  function itemPresenceOk(it, venue) {
    if (!it) return false;
    if (isWonderItem(it)) return true;

    const p = String(it.presence || "").toLowerCase();
    if (p === "absent") return false;

    // Sheet-facing label (soft names win over catalog species)
    const label = String(it.display_label || it.label || it.name || "").toLowerCase();
    const cid = String(it.catalog_id || "").toLowerCase();
    const id = String(it.id || "").toLowerCase();

    // do_not_list blocks by *name* always; catalog_id ban only if label wasn't softened
    for (const row of (venue && venue.do_not_list) || []) {
      if (!row) continue;
      const banName = String((typeof row === "string" ? row : row.name) || "").toLowerCase();
      const banCat = String((typeof row === "object" && row.catalog_id) || "").toLowerCase();
      if (banName && banName.length >= 4 && label.includes(banName)) return false;
      // catalog_id ban: skip when presence is verified/high and label differs from ban name
      if (banCat && cid === banCat) {
        if (PRESENCE_OK.has(p) && banName && !label.includes(banName)) {
          /* photo reuse OK — e.g. catalog african-penguin + label "Penguin" */
        } else if (!PRESENCE_OK.has(p)) {
          return false;
        } else if (!banName) {
          return false;
        }
      }
    }

    if (PRESENCE_BLOCK.has(p)) return false;
    if (PRESENCE_OK.has(p)) return true;

    // No presence field yet
    const conf = listConfidence(venue);
    if (conf === "audited") return true; // venue-level audit without per-item tags
    if (conf === "template") return false;
    // partial (owner / museum halls): allow until per-item audit lands
    if (conf === "partial") return true;
    return false;
  }

  function printSafeItems(venue) {
    return (venue.items || []).filter((it) => itemPresenceOk(it, venue));
  }

  /** Prefer display_label (soft species name) on sheets. */
  function sheetLabel(it) {
    if (!it) return "";
    return (it.display_label || it.label || it.name || "").trim();
  }

  function mulberry32(a) {
    return function () {
      let t = (a += 0x6d2b79f5);
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function hashSeed(str) {
    let h = 2166136261;
    const s = String(str || "");
    for (let i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return h >>> 0;
  }

  function scoreItem(item, interest, age) {
    let s = 0;
    const tags = item.tags || [];
    const a = normalizeAge(age);
    if (interest && tags.includes(interest)) s += 2;
    if (tags.includes("wow")) s += 1;
    if (item.zone) s += 1;

    const lab = String(item.label || item.display_label || item.id || "").toLowerCase();
    if (a === "2-3") {
      // Little kids: play / reset / easy wow — not long reads
      if (tags.includes("kids") || tags.includes("play")) s += 3;
      if (tags.includes("rest") || tags.includes("hands")) s += 2;
      if (tags.includes("read")) s -= 2;
      if (/toddler|early explor|children|kids zoo|farm|playground|garden|tower|climb|splash|water play/.test(lab)) {
        s += 2.5;
      }
      if (/planetarium|label|evolution|history hall/.test(lab)) s -= 1.5;
    } else if (a === "4-5") {
      if (tags.includes("play") || tags.includes("hands")) s += 1;
      if (tags.includes("wow")) s += 0.5;
    } else if (a === "6-8") {
      if (tags.includes("read") || tags.includes("wow")) s += 1;
      if (tags.includes("kids") && tags.includes("rest") && !tags.includes("wow")) s -= 1;
    } else if (a === "adult") {
      // Solo adults: signature stops, not toddler pens
      if (tags.includes("kids") && tags.includes("rest") && !tags.includes("wow")) s -= 4;
      if (tags.includes("kids") && !tags.includes("wow") && !tags.includes("big")) s -= 2;
      if (tags.includes("wow") || tags.includes("big")) s += 2;
      if (/toddler|early explor|children's zoo|quiet corner|free explore/.test(lab)) s -= 3;
      if (/submarine|storms|dinosaur|gorilla|elephant|panda|planetarium|tower|tunnel/.test(lab)) s += 1.5;
    }
    return s;
  }

  /** Does this item belong on a sheet for the selected audience? */
  function itemFitsAge(it, age) {
    if (!it) return false;
    const a = normalizeAge(age);
    const fit = it.age_fit;
    const tags = it.tags || [];
    const lab = String(it.label || it.id || "").toLowerCase();

    if (a === "adult") {
      // Drop toddler-only and pure little-kid reset stops
      if (fit && fit.length && fit.every((x) => x === "2-3")) return false;
      if (/toddler|early explor|quiet corner/.test(lab)) return false;
      if (tags.includes("kids") && tags.includes("rest") && !tags.includes("wow") && !tags.includes("big")) {
        return false;
      }
      return true;
    }

    // No age_fit → allow all kid bands (legacy data)
    if (!fit || !fit.length) return true;

    if (a === "2-3") {
      // Little: must be ok for 2-3, OR explicitly play/kids tagged even if age_fit missed 2-3
      if (fit.includes("2-3")) return true;
      if ((tags.includes("kids") || tags.includes("play")) && fit.includes("4-5")) return true;
      return false;
    }
    if (a === "4-5") {
      return fit.includes("4-5") || fit.includes("6-8") || fit.includes("2-3");
    }
    if (a === "6-8") {
      // Big kids: older bands; still allow 4-5 staples
      return fit.includes("6-8") || fit.includes("9+") || fit.includes("4-5");
    }
    return fit.includes(a);
  }

  function filterByAge(items, age) {
    return (items || []).filter((it) => itemFitsAge(it, age));
  }

  function simplifyOneLiner(text, age) {
    const t = String(text || "").trim();
    if (!t) return isLittle(age) ? "Go see it together." : "";
    if (!isLittle(age)) return t;
    const part = t.split(/[.—]/)[0].trim();
    if (part.length <= 42) return part;
    return part.slice(0, 40).trim() + "…";
  }

  /** Normalize venue.type → wonder/challenge pool keys: zoo | aquarium | museum | safari_zoo | national_park */
  function normalizeVenueType(venue) {
    const raw = String((venue && venue.type) || "zoo")
      .toLowerCase()
      .replace(/[\s+/]+/g, "_");
    if (raw.includes("aquarium") || raw === "aq" || raw === "sci_aq" || raw === "zoo_aq") {
      return "aquarium";
    }
    if (raw.includes("safari")) return "safari_zoo";
    if (raw.includes("zoo")) return "zoo";
    if (
      raw.includes("national_park") ||
      raw === "park" ||
      raw.includes("nationalpark") ||
      (raw.includes("park") && !raw.includes("safari"))
    ) {
      return "national_park";
    }
    if (
      /museum|science|natural|history|children|space|air|^sci$|^nh$|^cm$|childrens/.test(raw)
    ) {
      return "museum";
    }
    return raw || "zoo";
  }

  function typeAllows(poolTypes, kind) {
    const types = poolTypes || [];
    if (!types.length) return true;
    if (types.includes(kind)) return true;
    if (kind === "safari_zoo" && types.includes("zoo")) return true;
    // Park kits may reuse outdoor wonder/challenge pools tagged "park"
    if (kind === "national_park" && (types.includes("park") || types.includes("national_park"))) {
      return true;
    }
    return false;
  }

  function wonderPool(venue, wondersFile) {
    const kind = normalizeVenueType(venue);
    const list = (wondersFile && wondersFile.wonders) || [];
    return list.filter((w) => {
      if (!typeAllows(w.types, kind)) return false;
      // Museum-safe: no water/splash or live-animal sleep hunts
      const tags = w.tags || [];
      if (kind === "museum") {
        if (tags.includes("water")) return false;
        if (w.id === "w_splash" || w.id === "w_sleep") return false;
      }
      return true;
    });
  }

  /** Must-include stops: route_90m first, else first print-safe venue items. */
  function anchorItems(venue, age) {
    const a = normalizeAge(age);
    const items = printSafeItems(venue);
    const byId = Object.fromEntries(items.map((it) => [it.id, it]));
    const out = [];
    const push = (it) => {
      if (!it || out.some((x) => x.id === it.id)) return;
      if (!itemPresenceOk(it, venue)) return;
      if (!itemFitsAge(it, a)) return;
      out.push(it);
    };
    for (const id of venue.route_90m || []) {
      if (out.length >= 3) break;
      push(byId[id]);
    }
    // Little kids: if route anchors are all "hard", still keep 1–2 icons then fill play stops later
    if (!out.length || (a === "2-3" && out.length < 2)) {
      const rankedLittle = filterByAge(items, a)
        .slice()
        .sort((x, y) => scoreItem(y, "", a) - scoreItem(x, "", a));
      for (const it of rankedLittle) {
        if (out.length >= 3) break;
        push(it);
      }
    }
    if (!out.length) {
      for (const it of filterByAge(items, a)) {
        if (out.length >= 3) break;
        push(it);
      }
    }
    // If age filter emptied anchors, take raw print-safe route/items that fit
    if (!out.length) {
      for (const id of venue.route_90m || []) {
        if (out.length >= 3) break;
        const it = byId[id];
        if (it && itemFitsAge(it, a)) out.push(it);
      }
      for (const it of items) {
        if (out.length >= 3) break;
        if (!out.some((x) => x.id === it.id) && itemFitsAge(it, a)) out.push(it);
      }
    }
    return out.slice(0, a === "2-3" ? 2 : 3);
  }

  function scoreItemBonus(item, interest, age, routeSet) {
    let s = scoreItem(item, interest, age);
    const id = String(item.id || "");
    const cid = String(item.catalog_id || "").replace(/_/g, "-");
    const tags = item.tags || [];
    // Bonus: de-emphasize the default first-timer megafauna loop after anchors
    if (routeSet.has(id)) s -= 1.2;
    // Prefer second-visit depth: penguins, hippos, cheetahs, tortoises, patterns
    if (/penguin|hippo|cheetah|tortoise|flamingo|otter|sloth|red.?panda|koala/.test(id + " " + cid)) {
      s += 2.5;
    }
    if (tags.includes("kids") && tags.includes("rest") && !tags.includes("wow")) s -= 2;
    // Still allow one big wow
    if (tags.includes("wow") && !routeSet.has(id)) s += 0.6;
    return s;
  }
  function scoreItemAlpha(item, interest, age, routeSet) {
    let s = scoreItemBonus(item, interest, age, routeSet);
    const id = String(item.id || "");
    const cid = String(item.catalog_id || "").replace(/_/g, "-");
    const lab = String(item.display_label || item.label || "").toLowerCase();
    const tags = item.tags || [];
    // Alpha: skip the tourist megafauna loop harder
    if (routeSet.has(id)) s -= 2.5;
    // Cool / patience finds
    if (/cheetah|hippo|penguin|tortoise|otter|sloth|wolf|bear|alligator|peacock|capybara|jelly|octopus|eel|lemur|tiger|flamingo/.test(id + " " + cid + " " + lab)) {
      s += 1.8;
    }
    if (tags.includes("kids") || tags.includes("rest") || tags.includes("play")) s -= 3;
    if (tags.includes("wow") && !routeSet.has(id)) s += 1.2;
    return s;
  }


  function pickItems(venue, opts, wondersFile, bonusFile) {
    const age = normalizeAge(opts.age || "4-5");
    const time = opts.time || "half";
    const interest = (opts.interest || "").trim();
    const need = needCount(time, age);
    const seed = opts.seed || 1;
    const mode = contentMode(venue);
    const hunt = normalizeHunt(opts.hunt);
    const special = hunt === "bonus" || hunt === "alpha";
    const pack = special ? huntPack(venue, bonusFile, hunt) : null;
    const rand = mulberry32(
      hashSeed(
        venue.slug + "|" + mode + "|" + hunt + "|" + age + "|" + time + "|" + interest + "|" + seed
      )
    );

    const safeNamed = printSafeItems(venue);
    const byId = Object.fromEntries(safeNamed.map((it) => [it.id, it]));
    const routeSet = new Set(venue.route_90m || []);

    // Bonus/Alpha: preferred find list from venue research (presence-filtered)
    if (special && pack && Array.isArray(pack.find_ids) && pack.find_ids.length) {
      const preferred = [];
      const seenP = new Set();
      for (const rid of pack.find_ids) {
        const it = byId[rid];
        if (!it || !itemPresenceOk(it, venue) || !itemFitsAge(it, age)) continue;
        if (seenP.has(it.id)) continue;
        preferred.push(it);
        seenP.add(it.id);
      }
      // Top up with hunt-scored safe items
      const scorer = hunt === "alpha" ? scoreItemAlpha : scoreItemBonus;
      const rest = filterByAge(safeNamed, age)
        .filter((it) => itemPresenceOk(it, venue) && !seenP.has(it.id))
        .map((it, idx) => ({ it, idx, score: scorer(it, interest, age, routeSet) + rand() * 0.01 }))
        .sort((a, b) => b.score - a.score || a.idx - b.idx)
        .map((x) => x.it);
      const merged = preferred.concat(rest);
      if (merged.length) {
        return merged.slice(0, need).map((it) => {
          const lab = sheetLabel(it);
          const line = simplifyOneLiner(it.one_liner, age);
          const out = Object.assign({}, it);
          if (lab && lab !== it.label) out.label = lab;
          if (line) out.one_liner = line;
          if (special) out._bonus = true;
          if (hunt === "alpha") out._alpha = true;
          return out;
        });
      }
    }

    let sourceItems = safeNamed;
    if (mode === "wonder" && wondersFile) {
      sourceItems = wonderPool(venue, wondersFile);
    } else if (mode === "hybrid" && wondersFile) {
      const icons = filterByAge(safeNamed, age);
      const wonders = filterByAge(wonderPool(venue, wondersFile), age);
      sourceItems = icons.concat(wonders.filter((w) => !icons.some((i) => i.id === w.id)));
    } else if (mode === "curated" && wondersFile && filterByAge(safeNamed, age).length < need) {
      const icons = filterByAge(safeNamed, age);
      const wonders = filterByAge(wonderPool(venue, wondersFile), age);
      sourceItems = icons.concat(wonders.filter((w) => !icons.some((i) => i.id === w.id)));
    }

    let pool = filterByAge(sourceItems, age).filter((it) => itemPresenceOk(it, venue) || isWonderItem(it));
    if (!pool.length) {
      pool = wondersFile ? filterByAge(wonderPool(venue, wondersFile), age) : [];
    }

    const ranked = pool
      .map((it, idx) => ({
        it,
        idx,
        score:
          (hunt === "alpha"
            ? scoreItemAlpha(it, interest, age, routeSet)
            : hunt === "bonus"
              ? scoreItemBonus(it, interest, age, routeSet)
              : scoreItem(it, interest, age)) +
          rand() * 0.01,
      }))
      .sort((a, b) => b.score - a.score || a.idx - b.idx)
      .map((x) => x.it);

    // Classic: route anchors. Bonus: 1–2. Alpha: none (pure deep cuts) except littles get 1.
    let anchors = [];
    if (mode !== "wonder") {
      anchors = anchorItems(venue, age);
      if (hunt === "alpha") anchors = age === "2-3" ? anchors.slice(0, 1) : [];
      else if (hunt === "bonus") anchors = anchors.slice(0, age === "2-3" ? 1 : 2);
    }
    const picked = [];
    const seen = new Set();
    for (const a of anchors) {
      if (picked.length >= need) break;
      picked.push(a);
      seen.add(a.id);
    }
    for (const it of ranked) {
      if (picked.length >= need) break;
      if (seen.has(it.id)) continue;
      picked.push(it);
      seen.add(it.id);
    }
    if (picked.length < need && wondersFile) {
      for (const it of filterByAge(wonderPool(venue, wondersFile), age)) {
        if (picked.length >= need) break;
        if (seen.has(it.id)) continue;
        picked.push(it);
        seen.add(it.id);
      }
    }
    return picked.slice(0, need).map((it) => {
      const lab = sheetLabel(it);
      const line = simplifyOneLiner(it.one_liner, age);
      const out = Object.assign({}, it);
      if (lab && lab !== it.label) out.label = lab;
      if (line) out.one_liner = line;
      if (special) out._bonus = true;
      if (hunt === "alpha") out._alpha = true;
      return out;
    });
  }

  function challengeFitsAge(c, age) {
    const a = normalizeAge(age);
    const fit = c.age_fit || [];
    if (!fit.length) return a !== "adult";
    // Explicit bands only — don't leak "read a kid label" into little/kids
    if (a === "adult") return fit.includes("adult");
    if (a === "2-3") return fit.includes("2-3");
    if (a === "4-5") return fit.includes("4-5");
    if (a === "6-8") return fit.includes("6-8") || fit.includes("9+");
    return fit.includes(a);
  }

  function pickChallenges(challengesFile, venue, opts, selectedItems, bonusFile) {
    const age = normalizeAge(opts.age || "4-5");
    const seed = (opts.seed || 1) + 17;
    const hunt = normalizeHunt(opts.hunt);
    const huntSpecial = hunt === "bonus" || hunt === "alpha";
    const rand = mulberry32(
      hashSeed(venue.slug + "|ch|" + (huntSpecial ? hunt + "|" : "") + age + "|" + seed)
    );
    const kind = normalizeVenueType(venue);
    const blocked = new Set();
    (selectedItems || []).forEach((it) => (it.tags || []).forEach((t) => blocked.add(t)));

    let pool = [];

    // Bonus/Alpha: venue-researched challenges first
    if (huntSpecial) {
      const pack = huntPack(venue, bonusFile, hunt) || {};
      const file = bonusFile || (typeof window !== "undefined" && window.FP_BONUS_HUNTS) || null;
      let generic = [];
      if (hunt === "alpha") {
        generic =
          (file && file.alpha && file.alpha.generic && file.alpha.generic.challenges) ||
          (file && file.generic && file.generic.challenges) ||
          [];
      } else {
        generic = (file && file.generic && file.generic.challenges) || [];
      }
      const raw = [].concat(pack.challenges || [], generic);
      pool = raw
        .filter((c) => c && c.text)
        .filter((c) => {
          const fit = c.age_fit || [];
          if (!fit.length) return true;
          if (age === "adult") return fit.includes("adult") || fit.includes("6-8") || fit.includes("4-5");
          return fit.includes(age);
        })
        .map((c) => ({
          id: c.id || (hunt === "alpha" ? "ah_" : "bh_") + String(c.text).slice(0, 12),
          text: c.text,
          age_fit: c.age_fit || [],
          tags: hunt === "alpha" ? ["alpha", "bonus"] : ["bonus"],
          types: [kind],
        }));
    }

    if (!pool.length) {
      pool = (challengesFile.challenges || []).filter((c) => {
        if (!challengeFitsAge(c, age)) return false;
        return typeAllows(c.types, kind);
      });
      if (age === "adult") {
        pool = pool.filter((c) => (c.age_fit || []).includes("adult") || (c.tags || []).includes("adult"));
      }
    }

    pool = pool
      .map((c, idx) => {
        const tags = c.tags || [];
        const overlap = tags.filter((t) => blocked.has(t)).length;
        let boost = 0;
        if (age === "2-3" && (tags.includes("rest") || tags.includes("play") || tags.includes("color"))) boost += 1;
        if (age === "adult" && tags.includes("adult")) boost += 2;
        if (hunt === "alpha" && (tags.includes("alpha") || tags.includes("bonus"))) boost += 3;
        else if (hunt === "bonus" && tags.includes("bonus")) boost += 2;
        return { c, idx, score: -overlap + boost + rand() };
      })
      .sort((a, b) => b.score - a.score || a.idx - b.idx)
      .map((x) => x.c);

    const out = [];
    const used = new Set();
    const want = 3;
    for (const c of pool) {
      if (out.length >= want) break;
      if (used.has(c.id)) continue;
      out.push(c);
      used.add(c.id);
    }
    for (const c of pool) {
      if (out.length >= want) break;
      if (!used.has(c.id)) {
        out.push(c);
        used.add(c.id);
      }
    }
    return out.slice(0, want);
  }

  function sliceLabelOf(venue) {
    if (!venue) return "";
    return (
      venue.slice_label ||
      venue.sliceLabel ||
      (venue.practical && venue.practical.slice_name) ||
      ""
    ).trim();
  }

  function placeTitle(venue) {
    const slice = sliceLabelOf(venue);
    const name = (venue && venue.name) || "this place";
    if (slice) {
      // "Yellowstone National Park" + "Old Faithful Basin" → "Yellowstone — Old Faithful Basin"
      const short = String(name)
        .replace(/\s+National Park.*$/i, "")
        .replace(/\s+National Park & Preserve.*$/i, "")
        .trim();
      return `${short} — ${slice}`;
    }
    return name;
  }

  function missionTitle(venue, name, age, hunt) {
    const h = normalizeHunt(hunt);
    const place = placeTitle(venue);
    if (h === "alpha") {
      const n = (name || "").trim();
      if (n) return `${n}'s Alpha Hunt · ${place}`;
      return `Alpha Hunt at ${place}`;
    }
    if (h === "bonus") {
      const n = (name || "").trim();
      if (n) return `${n}'s Bonus Hunt · ${place}`;
      return `Bonus Hunt at ${place}`;
    }
    if (isAdult(age)) {
      const n = (name || "").trim();
      if (n) return `${n} · ${place}`;
      return `Solo day at ${place}`;
    }
    const n = (name || "").trim();
    if (!n) return `Your Mission at ${place}`;
    const poss = /s$/i.test(n) ? `${n}'` : `${n}'s`;
    return `${poss} Mission at ${place}`;
  }

  function parkSafetyFooter(venue) {
    if (!venue) return "";
    const custom = venue.safety_footer || venue.safetyFooter || "";
    if (custom) return custom;
    const t = String(venue.type || "").toLowerCase();
    if (t === "national_park" || venue.packTemplate === "park_features") {
      return "Stay on boardwalks and trails · give wildlife lots of space · bring water";
    }
    return "";
  }

  function easterEggLine(venue, age, bonusFile, hunt) {
    const pack = huntPack(venue, bonusFile, hunt || "bonus");
    if (!pack) return "";
    if (isLittle(age) && pack.easter_egg_little) return pack.easter_egg_little;
    return pack.easter_egg || "";
  }

  function selectMission(venue, challengesFile, options, wondersFile, bonusFile) {
    const opts = Object.assign(defaultOptions(), options || {});
    opts.age = normalizeAge(opts.age);
    opts.hunt = normalizeHunt(opts.hunt);
    if (opts.time === "90m") opts.time = "90m";
    if (opts.age === "adult") opts.name = (opts.name || "").trim();
    const mode = contentMode(venue);
    const hunt = opts.hunt;
    const special = hunt === "bonus" || hunt === "alpha";
    const pack = special ? huntPack(venue, bonusFile, hunt) : null;
    const finds = pickItems(venue, opts, wondersFile, bonusFile);
    const challenges = pickChallenges(challengesFile, venue, opts, finds, bonusFile);
    const adult = opts.age === "adult";
    const egg = special ? easterEggLine(venue, opts.age, bonusFile, hunt) : "";
    const huntLabel =
      hunt === "alpha" ? "Alpha" : hunt === "bonus" ? "Bonus hunt" : "Classic";
    const huntTagline = special
      ? (pack && pack.tagline) ||
        (hunt === "alpha" ? "Extra-hard · cool deep cuts" : "Second visit · curious explorers")
      : "";
    let findsHeading = "Find these";
    if (hunt === "alpha") findsHeading = isLittle(opts.age) ? "Cool hard finds" : "Alpha finds";
    else if (hunt === "bonus") findsHeading = "Trickier finds";
    else if (adult) findsHeading = "Don't miss";
    else if (isLittle(opts.age)) findsHeading = "Go see";
    let bonusHeading = adult ? "While you're there" : "Bonus";
    if (hunt === "alpha") bonusHeading = "Ultra challenges";
    else if (hunt === "bonus") bonusHeading = "Hard mode";
    return {
      title: missionTitle(venue, opts.name, opts.age, opts.hunt),
      slug: venue.slug || venue.id || "",
      type: venue.type || "",
      venue_type: venue.type || "",
      sliceLabel: sliceLabelOf(venue),
      safetyFooter: parkSafetyFooter(venue),
      venueName: venue.name,
      slug: venue.slug,
      age: opts.age,
      ageLabel: AGE_LABELS[opts.age] || opts.age,
      time: opts.time,
      timeLabel: TIME_LABELS[opts.time] || opts.time,
      hunt: opts.hunt,
      huntLabel,
      huntTagline,
      interest: opts.interest || "",
      personalized: Boolean((opts.name || "").trim()),
      contentMode: mode,
      audience: adult ? "adult" : "kid",
      findsHeading,
      bonusHeading,
      nameLabel: adult ? "Your name (optional)" : "Kid name",
      easterEgg: egg,
      finds,
      challenges,
      lastVerified: venue.last_verified || "",
      tagline: venue.tagline || "",
      practical: venue.practical || null,
      media: venue.media || null,
    };
  }

  function interestOptions(venue) {
    const counts = {};
    (venue.items || []).forEach((it) => {
      (it.tags || []).forEach((t) => {
        if (t === "wow") return;
        counts[t] = (counts[t] || 0) + 1;
      });
    });
    return Object.keys(counts)
      .filter((t) => counts[t] >= 1)
      .sort()
      .map((t) => ({ value: t, label: t.replace(/-/g, " ") }));
  }

  function collectTags(venue) {
    return interestOptions(venue);
  }

  root.FPMission = {
    AGE_ORDER,
    AGE_LABELS,
    AGE_CHIP_LABELS,
    TIME_N,
    TIME_LABELS,
    defaultOptions,
    normalizeAge,
    normalizeHunt,
    isAdult,
    isBonusHunt,
    isAlphaHunt,
    isSpecialHunt,
    bonusPack,
    alphaPack,
    huntPack,
    contentMode,
    listConfidence,
    itemPresenceOk,
    itemFitsAge,
    printSafeItems,
    sheetLabel,
    selectMission,
    interestOptions,
    collectTags,
    missionTitle,
    placeTitle,
    sliceLabelOf,
    parkSafetyFooter,
    wonderPool,
  };
})(typeof window !== "undefined" ? window : globalThis);
