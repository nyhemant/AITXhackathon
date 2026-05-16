# 1Less Reddit 12-Month Evidence Map — Hermes Pilot Review

Date: 2026-05-16  
Reviewer: Hermes / Arku_Ginnie  
Reviewed files:

- `docs/product/1less_reddit_12mo_evidence_table_pilot_2026-05-16.md`
- `docs/product/1less_reddit_12mo_evidence_pilot_findings_2026-05-16.md`

## Review decision

Approve the rubric.

Do **not** move directly to full Phase 3 scaling yet.

Run one short tuned-query pilot first, focused on the weaker communities and the exact gaps found in Phase 1–2.

Recommended next step:

> Phase 2B: tuned-query pilot, about 20 additional rows, before scaling to the 125–200 row full evidence map.

## Why not scale immediately

The first pilot did what it was supposed to do: it tested the rubric and acquisition approach.

The rubric worked, but the acquisition quality was uneven:

- `r/workingmoms`: strong direct Chapter 1 signal
- `r/Parenting`: strong picky-eating / safe-food guardrail signal
- `r/homeschool`: useful future-routine signal
- `r/MealPrepSunday`: useful mechanics, weaker parent-emotion signal
- `r/SAHP`: likely useful mental-load signal, but current queries were too narrow and pulled older rows

Because `r/MealPrepSunday` and `r/SAHP` produced lower-confidence / older rows, scaling with the same query families would likely create a noisy evidence table.

## Answers to Ginnie review questions

### 1. Are low-confidence older snippet rows acceptable in pilot files?

Yes, in pilot files only, if clearly labeled.

For Phase 3, reject anything outside the 12-month window unless it is included in a separate “background / outside-window” appendix.

Recommended Phase 3 rule:

- Main evidence table: last 12 months only.
- Outside-window rows: exclude by default.
- If an older row is unusually insightful, place it in a separate notes section and do not count it toward the 125–200 row target.

### 2. Should Phase 3 stay snippet-only?

No.

Use snippets for discovery, then open only high-signal public threads for deeper context when needed.

Recommended rule:

- Search snippets identify candidates.
- Open only the top 10–20 high-signal public threads across the whole pass.
- Use thread/comment context only to improve coding quality around workaround failure, exact language, and parent intent.
- Maintain observation-only boundary: no posting, commenting, voting, DMs, product mentions, private-group scraping, or account actions.

### 3. Is 20 rows enough to approve the rubric?

Yes. The rubric is approved.

But 20 rows is not enough to approve the acquisition strategy for all five communities.

Run a second 20-row tuned-query pilot before full Phase 3.

### 4. Should `r/MealPrepSunday` be sampled more for mechanics and less for parent-emotion language?

Yes.

Treat `r/MealPrepSunday` as mechanics/workaround evidence, not as the core emotional persona.

Good signal types from this community:

- freezer defaults
- cook-once/remix-all-week patterns
- component meals
- batch proteins
- work lunches / leftovers
- low-effort prep systems
- app/tool friction

Avoid over-weighting it for:

- 4:47pm emotional meltdown language
- working-parent exhaustion
- kid acceptance stress

### 5. Should `r/homeschool` be coded primarily for future routine/planning architecture rather than dinner?

Yes.

Use `r/homeschool` mostly for broader 1Less architecture:

- rhythm vs. rigid schedule
- parent overwhelm from planning
- routine simplification
- “minimum viable next step” patterns
- meals as anchors in the day

Do not let homeschool findings pull Chapter 1 into education, curriculum, or schedule-planner scope.

## Phase 2B tuned-query pilot recommendation

Run about 20 additional rows before Phase 3.

Suggested split:

- `r/SAHP`: 8 rows
- `r/MealPrepSunday`: 8 rows
- `r/workingmoms`: 2 rows, only for partner-handoff / visible-dinner-plan confirmation
- `r/Parenting`: 2 rows, only for picky-kid fallback confirmation
- `r/homeschool`: 0–2 rows only if needed for routine-architecture contrast

The point is not equal community coverage. The point is to repair weak evidence areas before scaling.

## Tuned query families

### r/SAHP — mental load, partner handoff, invisible work

```text
site:reddit.com/r/SAHP "meal planning"
site:reddit.com/r/SAHP "dinner" "husband"
site:reddit.com/r/SAHP "dinner" "partner"
site:reddit.com/r/SAHP "mental load" "meals"
site:reddit.com/r/SAHP "meal plan" "husband"
site:reddit.com/r/SAHP "leftovers" "kids"
site:reddit.com/r/SAHP "budget" "leftovers"
site:reddit.com/r/SAHP "what's for dinner"
site:reddit.com/r/SAHP "too tired to cook"
site:reddit.com/r/SAHP "invisible labor" "dinner"
```

### r/MealPrepSunday — mechanics/workaround primitives

```text
site:reddit.com/r/MealPrepSunday "freezer" "family"
site:reddit.com/r/MealPrepSunday "leftovers" "kids"
site:reddit.com/r/MealPrepSunday "cook once" "week"
site:reddit.com/r/MealPrepSunday "rotisserie chicken"
site:reddit.com/r/MealPrepSunday "work lunch"
site:reddit.com/r/MealPrepSunday "meal prep app"
site:reddit.com/r/MealPrepSunday "too much work"
site:reddit.com/r/MealPrepSunday "simple" "dinner"
site:reddit.com/r/MealPrepSunday "busy week"
site:reddit.com/r/MealPrepSunday "freezer meals"
```

### r/workingmoms — handoff / visible decision confirmation

```text
site:reddit.com/r/workingmoms "what's for dinner" "husband"
site:reddit.com/r/workingmoms "meal planning" "husband"
site:reddit.com/r/workingmoms "dinner" "mental load" "partner"
site:reddit.com/r/workingmoms "kids ask" "what's for dinner"
```

### r/Parenting — picky-kid fallback confirmation

```text
site:reddit.com/r/Parenting "safe food" "dinner"
site:reddit.com/r/Parenting "deconstruct" "dinner"
site:reddit.com/r/Parenting "kid won't eat" "fallback"
site:reddit.com/r/Parenting "picky eater" "family dinner"
```

## Phase 2B acceptance criteria

After the tuned pilot, proceed to full Phase 3 only if:

- At least 12 of 20 new rows are Medium or High confidence.
- `r/SAHP` produces current within-12-month evidence for mental load / partner handoff / invisible work.
- `r/MealPrepSunday` produces useful mechanics/workaround evidence without pretending to be the core emotional persona.
- The table can code workaround failure clearly in most rows.
- The results add nuance beyond what the first pilot already showed.

If those criteria fail, do not keep mining the same source. Either narrow the role of weak communities or move to contrast communities / off-Reddit later.

## Phase 3 guidance after Phase 2B

If Phase 2B passes, run the full 12-month structured pass with adjusted community roles:

### r/workingmoms

Primary Chapter 1 emotional signal.

Look for:

- after-work depletion
- dinner decision fatigue
- mental load
- partner handoff
- visible dinner decision
- late-day “no brain left” moments

### r/Parenting

Picky-eating and trust guardrails.

Look for:

- safe foods
- deconstructed meals
- boring fallback options
- pressure-free feeding language
- kid rejection realities

### r/SAHP

Invisible labor / default-parent / partner-handoff signal.

Look for:

- meal planning as household project management
- “I am the only one who thinks about this”
- spouse/partner execution gaps
- resentment around planning
- systems that become more work

### r/MealPrepSunday

Mechanics and workaround primitives.

Look for:

- freezer defaults
- batch components
- low-effort prep
- cook once / remix
- app/tool failure
- leftovers strategy

### r/homeschool

Future 1Less routine architecture, not Chapter 1 build scope.

Look for:

- rhythm over schedule
- planning overwhelm
- meals as day anchors
- minimum viable routine
- parent anxiety from too many choices

## Product interpretation from current pilot

The pilot strengthens, but does not materially change, the current 1Less direction.

Protect:

- one recommendation, not a list
- no/low setup
- “based on what you told me” honesty
- current-turn ingredient use
- fallback that is actually easier
- `Kid won't eat this` as deconstruct/familiar-side path

Likely strengthen soon:

- “no brain left” / bare-minimum mode
- partner-handoff wording
- activity-night / no-cook fallback language
- component meal logic: protein + carb + fruit/veg + familiar side

Continue avoiding:

- weekly planner as default
- grocery optimization
- meal-kit clone
- full pantry inventory
- nutrition/macros positioning
- child feeding therapy claims
- homeschool/curriculum product scope
- generic family command center

## Recommended instruction to Ginnie/OpenClaw

Use this as the next task packet:

> Please run Phase 2B, a tuned-query pilot, before full scaling. Keep the same observation-only boundary. Add about 20 new evidence rows, weighted toward the weak areas from Phase 1–2: about 8 rows from `r/SAHP`, 8 rows from `r/MealPrepSunday`, 2 rows from `r/workingmoms`, and 2 rows from `r/Parenting`. Use the tuned query families from `docs/product/1less_reddit_12mo_pilot_hermes_review_2026-05-16.md`. Reject outside-12-month rows from the main table unless separately marked as background notes. Open only high-signal public threads when snippets are too thin. Stop after Phase 2B and save an updated pilot table/findings note for review before Phase 3.

## Decision

Approved:

- rubric
- evidence table structure
- search-snippet-first posture
- opening only selected high-signal public threads after snippet discovery
- treating each community differently based on signal type

Not approved yet:

- full Phase 3 scaling to 125–200 rows
- adding more subreddits
- moving to TikTok/Instagram/Facebook/forums
- making product changes solely from Reddit evidence

## Confidence

High.

The first pilot succeeded as a pilot. The right next move is not full-scale yet; it is a short tuned-query pilot to improve acquisition quality before scaling.
