# Bonus hunt catalog — rollout progress

Optional **Bonus hunt** mission style (orthogonal to age). Data lives in each
`venues/<slug>.json` → `bonus_hunt`, synced to `data/bonus-hunts.json` for SEO embed.

## Status legend

| status | meaning |
|--------|---------|
| **researched** | Venue-specific tagline, find_ids, challenges, easter egg (zones/names) |
| **solid** | Type-kit + inventory-derived challenges; good enough to print |
| **thin** | Weak/template inventory — generic challenges only; no fake finds |

## Wave checklist

| Wave | Scope | State |
|------|--------|--------|
| **0** | `scaffold_bonus_hunt.py`, `validate_bonus_hunts.py`, type kits, sync | **done** |
| **1** | Signature US/UK pilots (Dallas first + ~20 museums/zoos/aquariums) | **done** |
| **2** | Remaining audited US + major aquariums/museums | **done** (curated) |
| **3** | Audited / high-traffic intl (Taronga, Singapore, Ueno, NHM, Safari Park, …) | **done** (curated) |
| **4** | Partial inventory — solid auto packs from safe items | **done** |
| **5** | Template / thin long-tail — thin packs, no fake presence | **done** |

## Counts (2026-08-08)

- Venues with `bonus_hunt`: **140 / 140**
- researched ≈ **84** · solid ≈ **29** · thin ≈ **27**
- Validate: `python3 scripts/validate_bonus_hunts.py` → 0 errors

## Tooling

```bash
# Scaffold missing only
python3 scripts/scaffold_bonus_hunt.py --all --write --only-missing

# Sync venues → bonus-hunts.json
python3 scripts/scaffold_bonus_hunt.py --sync-file

# Validate + Node smoke (dallas, detroit, fort-worth, georgia-aquarium, perot)
python3 scripts/validate_bonus_hunts.py

# Embed into SEO pages
python3 scripts/generate_bdo_seo.py
```

## Rules (do not regress)

1. **Presence gate** — `find_ids` only verified/high (or audited-safe); never template/absent.
2. **Thin honesty** — empty/short find_ids OK; challenges still print via type kits + engine top-up.
3. **Bonus ≠ age** — Who’s going? stays audience; Bonus hunt is Style.
4. **Q&A “Bonus”** is talk-level wow; mission **Bonus hunt** is the printable hard mode.
5. Prefer upgrading `solid` → `researched` with real zone names over inventing animals.

## Next upgrades (optional polish)

- Re-research thin packs when list_confidence leaves template.
- Spot-check live Bonus chip on 5 cities after each deploy.
- Add sources/notes when habitat closures matter (e.g. FW elephants, Ueno pandas absent).


## Alpha hunt (2026-08-08+)

Third Style tab: **Classic · Bonus · Alpha**.

- Data: `venues/<slug>.alpha_hunt` + `bonus-hunts.json` → `alpha.venues` / `alpha.generic`
- Pilots (researched): **dallas-zoo**, **austin-zoo**
- Engine: `hunt: "alpha"` — extra-hard scoring, ultra challenges, easter egg
- UI: purple Alpha chip; other venues fall back to bonus pack or generic alpha challenges until authored
