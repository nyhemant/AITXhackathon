# 1Less Reddit 12-Month Evidence Map — Hermes Phase 2B Review

Date: 2026-05-16  
Reviewer: Hermes / Arku_Ginnie  
Reviewed files:

- `docs/product/1less_reddit_12mo_evidence_table_pilot_2026-05-16.md`
- `docs/product/1less_reddit_12mo_evidence_pilot_findings_2026-05-16.md`

## Verification

Hermes verified the Phase 2B table counts programmatically:

- Total pilot rows: 40
- Phase 2B rows: 20
- Phase 2B community split:
  - `r/SAHP`: 8
  - `r/MealPrepSunday`: 8
  - `r/workingmoms`: 2
  - `r/Parenting`: 2
- Phase 2B confidence split:
  - High: 12
  - Medium: 8
- Phase 2B outside-window rows counted in main table: 0

The evidence table structure is clean enough to proceed.

## Review decision

Approve Phase 3 scaling.

Ginnie/OpenClaw can now proceed from pilot mode to the full 12-month structured evidence map, with guardrails.

Recommended next step:

> Run Phase 3 and produce the full 12-month evidence map across the original five communities, targeting roughly 125–160 total main-table rows before deciding whether more are needed.

Do not expand to new subreddits or new social platforms yet.

## Why Phase 3 is approved

Phase 2B fixed the main weakness from the first pilot.

The first pilot proved the rubric worked, but `r/SAHP` and `r/MealPrepSunday` were uneven. Phase 2B showed that:

- `r/SAHP` can produce current, useful evidence when queried for invisible work, grocery/time burden, partner handoff, and budget pressure.
- `r/MealPrepSunday` produces strong mechanics/workaround evidence when treated as a mechanics library rather than a core emotional-persona source.
- `r/workingmoms` remains the best direct emotional signal for Chapter 1.
- `r/Parenting` remains the best guardrail source for picky-eating, safe foods, and avoiding short-order-cook dynamics.
- `r/homeschool` should remain mostly future-architecture contrast, not Chapter 1 scope.

The Phase 2B evidence strengthened the “one small answer” direction:

- one dinner that works tonight
- one fallback when energy collapses
- one kid-tolerable adaptation
- one visible handoff another adult can execute
- one use-up-what-I-have answer

That is exactly aligned with the 1Less test:

> Does this remove one real decision for a busy parent without creating another chore?

## Phase 3 scope

Keep the original five communities:

1. `r/workingmoms`
2. `r/MealPrepSunday`
3. `r/SAHP`
4. `r/Parenting`
5. `r/homeschool`

Do not add more Reddit groups yet.

Do not move to TikTok, Instagram, Facebook, Mumsnet, BabyCenter, or other sites yet.

Phase 3 should complete the original evidence map first.

## Recommended row target

The original plan allowed 125–200 rows. After seeing the quality of the pilot, a tighter target is better.

Recommended target:

- Main evidence table: 125–160 total rows
- Stop at 125 if themes are already saturated
- Continue toward 160 only if new rows are adding new insight
- Avoid pushing to 200 just to hit a number

Reason: this is product discovery, not academic quantification. Repetitive rows create false precision and waste time.

## Recommended community allocation

Use unequal allocation based on each community’s role.

### r/workingmoms — 35–45 rows

Role: primary Chapter 1 emotional signal.

Look for:

- after-work depletion
- dinner decision fatigue
- “no brain left” language
- kids asking “what’s for dinner”
- visible dinner plan / partner handoff
- late-day meal chaos
- working-parent guilt and time pressure

### r/Parenting — 25–35 rows

Role: picky-eating and trust guardrails.

Look for:

- safe foods
- deconstructed family meals
- boring fallback options
- avoiding short-order-cook dynamics
- pressure-free feeding language
- toddler/preschool dinner constraints
- bedtime/routine hints only as future signal

### r/SAHP — 25–35 rows

Role: invisible labor, default-parent burden, handoff, grocery/budget pressure.

Look for:

- household project-management resentment
- partner/spouse handoff gaps
- grocery pickup/delivery as legitimacy/time relief
- one-income budget pressure
- leftovers allocation
- meal planning as invisible work
- systems that become another chore

### r/MealPrepSunday — 20–30 rows

Role: mechanics/workaround primitives, not core persona.

Look for:

- no-thaw freezer meals
- small frozen portions
- cook once / remix
- staple reuse
- convenience ingredients
- tiny-start meal prep
- app/tool complexity
- “realistic, not impressive” prep

Avoid over-weighting:

- macro tracking
- adult fitness meal prep
- polished meal-prep inspiration

### r/homeschool — 10–20 rows

Role: future 1Less architecture contrast.

Look for:

- rhythm over schedule
- meals as anchors
- minimum viable routine
- planning overwhelm
- too many choices
- parent anxiety around doing enough

Do not let this become:

- curriculum planning
- education advice
- Chapter 2 implementation
- generic family operating system

## Acquisition rules for Phase 3

Use the refined acquisition strategy:

1. Start with search-engine snippets.
2. Open only high-signal public threads when snippets are too thin.
3. Use public thread context to improve coding of workaround failure, exact language, and parent intent.
4. Main table should include only within-last-12-month rows.
5. If an older row is unusually insightful, put it in a separate background appendix and do not count it toward the main row target.
6. Preserve observation-only boundary.

Observation-only still means:

- no posting
- no commenting
- no voting/reactions
- no DMs
- no product mentions
- no tester recruitment from Reddit
- no private scraping
- no private/gated groups

## Required Phase 3 deliverables

Ginnie/OpenClaw should create or update:

1. Full evidence table

Suggested path:

`docs/product/1less_reddit_12mo_evidence_table_2026-05.md`

2. Full synthesis report

Suggested path:

`docs/product/1less_reddit_12mo_evidence_map_2026-05.md`

3. Optional appendix for older/background rows

Suggested path:

`docs/product/1less_reddit_background_evidence_appendix_2026-05.md`

## Required synthesis sections

The full synthesis report should include:

1. Executive summary
2. What changed from the original 30-day scan
3. What changed from the 40-row pilot
4. Strongest recurring pain moments
5. Exact parent language worth reusing
6. Current workarounds parents already trust
7. Where current workarounds fail
8. Product implications for Chapter 1
9. Copy implications
10. Alpha interview questions
11. Scenario tests to add or refine
12. Feature temptations to avoid
13. Confidence / caveats
14. Appendix/link to coded evidence table

## Product interpretation to preserve during Phase 3

The evidence so far does **not** justify expanding product scope.

It justifies sharpening Chapter 1:

- “No brain left” / bare-minimum mode
- easier fallback when parent says “Too much work”
- kid-safe deconstruction / familiar-side path
- handoff-ready dinner card/copy
- use-current-ingredients honesty
- helper/convenience ingredient normalization
- emergency/no-thaw/no-store-run fallback primitives

Continue protecting:

- one recommendation, not a list
- low/no setup
- current-turn honesty: “based on what you told me”
- no allergy/nutrition/medical overclaims
- fallback must be easier, not just different
- do not imply pantry memory unless explicitly implemented and consented

Continue avoiding:

- weekly meal planner as default
- grocery optimization
- meal-kit clone
- full pantry inventory
- nutrition/macro positioning
- recipe marketplace
- child feeding therapy claims
- homeschool/curriculum product scope
- generic family command center

## Stop conditions during Phase 3

Stop before the target row count if:

- rows become repetitive and no longer add new insight
- the table is drifting into generic recipe content
- `r/MealPrepSunday` becomes too macro/fitness-oriented
- `r/homeschool` starts pulling the product into curriculum/schedule scope
- evidence starts suggesting feature expansion before parent alpha feedback
- acquisition starts requiring aggressive scraping or questionable access

If at least 100 rows show theme saturation, stop and synthesize rather than forcing 160.

## Parallel recommendation

Continue real-parent alpha preparation in parallel.

Do not wait for Phase 3 to finish before lining up 3–5 private parent testers.

Reddit research can improve product language and scope discipline. It cannot prove that 1Less creates emotional relief in the actual dinner-crunch moment.

The next real validation question remains:

> Did the first suggestion feel like relief, or did it create another decision?

## Suggested instruction to Ginnie/OpenClaw

Use this as the next task packet:

> Phase 2B is approved. Please proceed to Phase 3 of the 1Less Reddit 12-month evidence map using the guardrails in `docs/product/1less_reddit_12mo_phase2b_hermes_review_2026-05-16.md`. Keep the original five communities only. Target 125–160 total main-table rows, stopping early if themes saturate. Use unequal allocation: r/workingmoms as primary Chapter 1 emotional signal, r/Parenting for picky-eating/trust guardrails, r/SAHP for invisible work/handoff/grocery/budget pressure, r/MealPrepSunday for mechanics/workarounds, and r/homeschool for future routine-architecture contrast. Use search snippets first and open only high-signal public threads when needed. Keep observation-only boundaries. Produce a full evidence table and concise synthesis report under `docs/product/`. Do not make product/code changes from this research yet; convert findings into recommendations and alpha-test questions.

## Decision summary

Approved:

- Phase 3 scaling
- tuned acquisition strategy
- unequal community weighting
- selected public-thread opening after snippet discovery
- within-12-month main table rule

Not approved:

- adding more subreddits
- moving to new social platforms
- product/code changes solely from Reddit evidence
- broadening 1Less beyond Chapter 1 dinner relief

## Confidence

High.

Phase 2B fixed the pilot’s main weakness. The research process is now good enough to scale once, synthesize, and then return to real parent validation.
