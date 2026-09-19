# 1Less Reddit 12-Month Evidence Map Plan

Date: 2026-05-16  
Prepared for: Hemant, OpenClaw / Ginnie  
Project: 1Less  
Repo source of truth: `/Users/arku/Projects/AITXhackathon` until repo rename  
Related prior artifact: `docs/product/1less_reddit_community_observation_scan_2026-05-16.md`

## Executive recommendation

Use this as an **Advisor Pilot** workflow, not a duplicate-research workflow.

- **Hermes**: research architect, product critic, synthesis reviewer.
- **OpenClaw / Ginnie**: official operator, source-of-truth keeper, artifact owner.
- **Codex CLI**: optional tooling builder only if a repeatable collector/parser is needed.
- **Sophie**: optional skeptical user / trust / copy critic after synthesis.

Do **not** have Hermes and OpenClaw independently analyze the same Reddit communities and produce competing reports. That creates coordination drift.

Recommended next step:

> Convert the prior 30-day Reddit scan from angle validation into a structured 12-month evidence map for the same five communities before expanding to more subreddits or other social sites.

## Why this step

The last 30-day pass gave a strong directional signal:

> 1Less is best positioned around parent decision relief, with Chapter 1 focused on the late-day dinner crunch: one realistic dinner decision, not a recipe rabbit hole.

But that pass was still more **angle validation** than a durable **research asset**.

This next pass should produce reusable evidence for:

- product positioning
- landing/onboarding copy
- alpha interview questions
- scenario tests
- scope boundaries
- feature temptations to avoid

## Research goal

Build a structured evidence map of recurring parent decision-relief patterns across the original five Reddit communities over roughly the last 12 months.

The goal is **not** to crawl every post or build a statistically exhaustive dataset.

The goal is to identify and code recurring patterns:

- the exact moment of parent pain
- what parents are really asking for
- the natural language they use
- the workarounds they already trust
- where those workarounds fail
- what 1Less should strengthen
- what 1Less should avoid building

## Communities in scope

Use the original five communities only for this pass:

1. `r/workingmoms`
2. `r/MealPrepSunday`
3. `r/SAHP`
4. `r/Parenting`
5. `r/homeschool`

Do not add more subreddits yet. Additional Reddit groups should come after this evidence map is reviewed.

## Observation boundary

This is read-only public-community research.

Allowed:

- search public web/indexed Reddit results
- read public posts and comments where accessible
- summarize anonymized themes
- preserve short, useful public phrases as evidence snippets
- record source URLs when available

Not allowed without explicit Hemant approval:

- posting
- commenting
- voting/reacting
- DMs
- product mentions
- recruiting testers from Reddit
- joining private groups for research
- scraping private or gated content
- aggressive automation that violates platform expectations

Treat all public snippets as directional product evidence, not exhaustive truth.

## Recommended acquisition strategy

Avoid starting with direct Reddit crawling. It is rate-limit-prone and likely to hit 429/403 errors.

Use a layered approach instead.

### Layer 1 — Search-engine snippets first

Use targeted search queries rather than hammering Reddit directly.

This is the best first path because it avoids most Reddit `429` issues and surfaces high-signal public posts.

Example query patterns:

```text
site:reddit.com/r/workingmoms dinner decision fatigue parent
site:reddit.com/r/workingmoms "what's for dinner" "mental load"
site:reddit.com/r/workingmoms "no brain left" dinner
site:reddit.com/r/workingmoms "picky eater" "after work" dinner
site:reddit.com/r/MealPrepSunday "too much work" "meal planning"
site:reddit.com/r/Parenting "kid won't eat" dinner "tired"
site:reddit.com/r/SAHP "meal planning" "mental load"
site:reddit.com/r/homeschool "overwhelmed" "schedule" "meals"
```

Use date filters where the search provider supports them:

- past year
- custom range by quarter
- exact month if needed

### Layer 2 — Open only high-signal threads

Do not open hundreds of posts.

Open only threads that match the research lens:

- parent describes exhaustion, decision fatigue, mental load, dinner dread, picky eating, or household routine overload
- thread includes concrete workarounds
- comments show repeated agreement or alternative hacks
- language is emotionally vivid
- thread reveals why existing solutions fail

### Layer 3 — Use official/authenticated Reddit access only if needed

If snippets are too thin, use an official Reddit API/OAuth path with conservative rate limits.

Do not start here unless needed. API work adds setup/auth/rate-management overhead and can distract from product learning.

### Layer 4 — Manual/browser review for selected threads

For the top 10–20 high-signal threads, use manual/browser review if available to capture deeper context and comments.

Keep the same observation boundary:

- no posting
- no commenting
- no votes
- no DMs
- no product mentions

## Coding rubric

Create a coded evidence table. Use one row per useful evidence item.

Recommended columns:

| Column | Description |
|---|---|
| Community | Subreddit name |
| Date / timeframe | Exact date if visible; otherwise month/quarter/year |
| Source type | Search snippet, public thread, comment, indexed result, prior doc |
| Post context | Short neutral description of the situation |
| Pain moment | When the decision pain happens |
| Parent pain | What is hard emotionally/practically |
| Exact language | Short useful phrase, if available |
| Current workaround | What the parent already does |
| Workaround failure | Why the workaround does not fully solve it |
| What parent is really asking for | The underlying job-to-be-done |
| Product implication | What 1Less should strengthen/change |
| Feature temptation to avoid | What this evidence might tempt us to build too early |
| Confidence | Low / Medium / High |
| Evidence note / source URL | URL or note; avoid unnecessary personal detail |

## Product coding tags

Use these tags to keep synthesis consistent.

### Pain moment tags

- after work
- 4–6pm dinner crunch
- Sunday planning
- grocery day
- bedtime
- morning / school rush
- sports or activity night
- no plan and everyone is hungry
- homeschool planning block
- household routine overload

### Need type tags

- one answer
- permission to do bare minimum
- kid-safe fallback
- partner handoff
- planning system
- budget constraint
- freezer / pantry rescue
- emotional validation
- lower-cleanup option
- fewer steps
- routine simplification

### Workaround tags

- theme nights
- meal rotation
- freezer meals
- rotisserie chicken
- breakfast for dinner
- snack dinner
- meal kits
- leftovers
- batch prep
- partner text
- safe foods
- deconstructed meals
- grocery pickup
- takeout

### Failure mode tags

- still requires planning
- too many options
- kid rejects it
- ingredient mismatch
- too expensive
- still lands on mom
- guilt / nutrition pressure
- cleanup too high
- not enough time
- system becomes another chore
- partner does not execute

### 1Less implication tags

- protect one answer
- strengthen bare-minimum mode
- add easier fallback
- improve picky-kid adaptation
- improve handoff language
- avoid weekly planner
- avoid grocery optimization
- avoid nutrition / macro framing
- avoid full pantry inventory
- improve trust wording
- improve “based on what you told me” language

## Core research questions

For each evidence item, code against these product questions:

1. What exact moment causes the pain?
   - after work?
   - before sports?
   - Sunday planning?
   - bedtime?
   - grocery day?
   - no plan and everyone is hungry?

2. What is the parent really asking for?
   - one answer?
   - permission to be lazy?
   - a system?
   - partner handoff?
   - kid-safe fallback?
   - pantry/freezer rescue?

3. What wording do they naturally use?
   - “no brain left”
   - “I’m so tired of deciding”
   - “my kid won’t eat anything”
   - “what’s for dinner” stress
   - “mental load”

4. What solutions do they already use?
   - theme nights
   - freezer meals
   - nuggets
   - rotisserie chicken
   - leftovers
   - snack dinner
   - meal prep
   - meal kits
   - partner texting

5. Where do existing solutions fail?
   - too much planning
   - too many recipes
   - grocery mismatch
   - picky kids
   - mental load still lands on mom
   - cleanup/time mismatch
   - nutrition guilt

6. What should 1Less avoid building right now?
   - weekly meal planner
   - recipe rabbit hole
   - macro tracker
   - pantry manager
   - grocery optimization
   - guilt-heavy nutrition app
   - broad parent command center

## Query families

Run 6–8 query families per community. Adjust terms by community.

### 1. Dinner decision fatigue

```text
site:reddit.com/r/[community] "dinner decision fatigue"
site:reddit.com/r/[community] "what's for dinner"
site:reddit.com/r/[community] "no brain left" dinner
site:reddit.com/r/[community] "tired of deciding" dinner
site:reddit.com/r/[community] "mental load" dinner
```

### 2. Late-day crunch

```text
site:reddit.com/r/[community] "after work" dinner kids
site:reddit.com/r/[community] "5pm" dinner kids
site:reddit.com/r/[community] "everyone is hungry" dinner
site:reddit.com/r/[community] "last minute dinner" kids
site:reddit.com/r/[community] "weeknight dinner" kids tired
```

### 3. Picky eating / kid rejection

```text
site:reddit.com/r/[community] "kid won't eat" dinner
site:reddit.com/r/[community] "picky eater" dinner
site:reddit.com/r/[community] "safe foods" dinner
site:reddit.com/r/[community] "deconstructed" dinner kids
site:reddit.com/r/[community] toddler dinner picky
```

### 4. Bare minimum / low energy

```text
site:reddit.com/r/[community] "low effort dinner"
site:reddit.com/r/[community] "lazy dinner"
site:reddit.com/r/[community] "bare minimum" dinner
site:reddit.com/r/[community] "too tired to cook"
site:reddit.com/r/[community] "fed is fine" dinner
```

### 5. Workarounds / systems

```text
site:reddit.com/r/[community] "theme nights" dinner
site:reddit.com/r/[community] "meal rotation"
site:reddit.com/r/[community] "meal prep" family
site:reddit.com/r/[community] "freezer meals"
site:reddit.com/r/[community] "rotisserie chicken" dinner
site:reddit.com/r/[community] "breakfast for dinner"
```

### 6. Partner / household mental load

```text
site:reddit.com/r/[community] husband dinner mental load
site:reddit.com/r/[community] partner meal planning
site:reddit.com/r/[community] "invisible labor" meals
site:reddit.com/r/[community] "mental load" meals
site:reddit.com/r/[community] "only one who plans" dinner
```

### 7. App/tool frustration

```text
site:reddit.com/r/[community] "meal planning app"
site:reddit.com/r/[community] "recipe app"
site:reddit.com/r/[community] "too many recipes"
site:reddit.com/r/[community] "meal kit" dinner kids
site:reddit.com/r/[community] "grocery list app"
```

### 8. Broader 1Less chapter signal

Especially for `r/homeschool` and `r/Parenting`:

```text
site:reddit.com/r/[community] "bedtime" "too many choices"
site:reddit.com/r/[community] "bedtime routine" overwhelmed
site:reddit.com/r/[community] "schedule" overwhelmed parent
site:reddit.com/r/[community] "homeschool planning" overwhelmed
site:reddit.com/r/[community] "routine" "decision fatigue"
```

## Execution sequence

### Phase 0 — Confirm posture and owners

Decision:

- Read-only public-community research.
- Advisor Pilot mode.
- Ginnie/OpenClaw owns the official artifact.
- Hermes reviews structure and synthesis.
- Codex only builds tooling if needed.

Output:

- this plan file committed or saved under `docs/product/`

### Phase 1 — Create the table template

Create a working evidence table file, for example:

`docs/product/1less_reddit_12mo_evidence_table_2026-05.csv`

or markdown if easier:

`docs/product/1less_reddit_12mo_evidence_table_2026-05.md`

Use the rubric columns above.

### Phase 2 — Pilot pass

Run a small pilot before scaling.

Scope:

- 5 communities
- 2 query families per community
- about 20 total evidence rows

Suggested pilot query families:

- Dinner decision fatigue
- Bare minimum / low energy

Purpose:

- confirm the rubric works
- confirm snippets are useful enough
- identify whether search terms need adjustment
- avoid wasting time on bad query patterns

Stop after pilot and review quality before scaling.

Pilot review questions:

- Are we capturing real parent language?
- Are snippets sufficient, or do we need thread/comment review?
- Are product implications concrete?
- Are confidence labels useful?
- Are we over-indexing on dinner and missing broader 1Less moments?

### Phase 3 — Full 12-month structured pass

Only after pilot quality is acceptable, scale up.

Recommended target:

- 25–40 useful evidence rows per community
- 125–200 total coded rows

This is enough for product direction. More than that may create false precision and analysis drag.

Suggested sampling per community:

- 8–12 rows on dinner / meal decision fatigue
- 5–8 rows on workarounds
- 5–8 rows on family / kid constraints
- 3–5 rows on mental load / partner handoff
- 3–5 rows on future chapter signals

For `r/homeschool`, shift more rows toward routine/planning overload rather than dinner only.

### Phase 4 — Synthesis report

Create a concise synthesis report:

`docs/product/1less_reddit_12mo_evidence_map_2026-05.md`

Suggested report structure:

1. Executive summary
2. What changed from the 30-day scan
3. Strongest recurring pain moments
4. Exact parent language worth reusing
5. Current workarounds parents already trust
6. Where current workarounds fail
7. Product implications for Chapter 1
8. Copy implications
9. Alpha interview questions
10. Feature temptations to avoid
11. Confidence / caveats
12. Appendix: coded evidence table or link to table

### Phase 5 — Product review

Hermes should review the synthesis for:

- whether the conclusions are supported by evidence
- whether the product implications are actionable
- whether recommendations preserve “one answer, not a list”
- whether any recommendation creates another chore
- whether scope creep is sneaking in

Sophie can optionally review for:

- trust language
- parent guilt risk
- safety/allergy wording
- whether copy feels patronizing, creepy, or overconfident

### Phase 6 — Update product docs

After review, Ginnie/OpenClaw should update relevant product docs, likely including:

- `docs/product/1less_private_parent_test_plan_v0.md`
- any MVP brief / positioning docs currently used as source of truth
- the existing Reddit observation reference if needed

Do not change product behavior solely because of Reddit research. Convert findings into alpha-test questions first unless the evidence reveals a narrow trust/copy issue.

## Parallel track: private parent validation

Do not wait for the full 12-month research report before testing with real parents.

Run in parallel:

### Track A — Reddit 12-month evidence map

Purpose:

- sharpen language
- improve scope discipline
- identify recurring scenarios
- avoid building the wrong features

### Track B — Tiny private parent alpha

Purpose:

- test whether the actual product flow creates relief
- observe if parents accept the first suggestion
- observe whether fallback feels easier
- identify trust/copy issues

Reddit can tell us what parents complain about.

Only parent testing can answer:

> Did 1Less actually remove one real dinner decision in the dinner-crunch moment?

## Deliverables

The most valuable outputs are:

1. **Coded evidence table**
   - 125–200 rows after full pass
   - 20 rows after pilot

2. **Top 10 parent phrases**
   - Use for landing page, onboarding, button copy, and tester prompts.

3. **Top 5 dinner-crunch scenarios**
   - Use for product smoke tests and parent alpha scenarios.

4. **Top 5 trusted workarounds**
   - Use as meal logic primitives, not necessarily features.

5. **Top 5 workaround failures**
   - Use to avoid repeating current solution problems.

6. **Top 5 feature temptations to avoid**
   - Use as scope guardrails.

7. **Top 5 private alpha questions**
   - Use with 3–5 parent testers.

## Quality bar

A good evidence row should answer at least four of these:

- What was happening?
- What was painful?
- What language did the parent use?
- What did they already try?
- Why did that not fully work?
- What does this imply for 1Less?
- What should we avoid building from this?

Reject or mark low-confidence rows if:

- the snippet is too vague
- the source context is unclear
- the post is not actually about parent decision burden
- the implication is speculative
- it only confirms something already known without adding nuance

## Confidence labels

Use simple labels:

### High

- clear parent pain
- direct language available
- context fits 1Less research lens
- workaround/failure visible
- source/thread available or strongly indicated

### Medium

- useful but partial context
- snippet supports the theme but lacks comments/details
- product implication is plausible but not definitive

### Low

- vague snippet
- unclear date/context
- weak link to parent decision burden
- useful only as directional noise

## Stop / rollback conditions

Stop or pause if:

- research becomes mostly generic recipe/meal-prep content
- snippets are too thin to code meaningfully
- conclusions become repetitive before 125 rows
- the work starts delaying parent alpha testing
- the team drifts into designing new features before synthesis
- the process requires questionable scraping or private-group access

Rollback / narrow scope if:

- direct Reddit access triggers repeated 429/403 errors
- acquisition tooling becomes more work than the research itself
- the evidence table fills with low-confidence rows

## What not to do yet

Do not yet:

- expand to five more subreddits
- move to TikTok/Instagram
- study Facebook private groups
- build a weekly meal planner
- build grocery optimization
- build pantry inventory
- build macro/nutrition features
- implement Chapter 2
- turn 1Less into a generic parent command center

Those may come later, but only after the original five-community evidence map is complete and the private parent alpha loop has begun.

## Suggested instruction to Ginnie/OpenClaw

Use this as the operational prompt:

> Create a 12-month structured Reddit evidence map for 1Less using the original five communities: `r/workingmoms`, `r/MealPrepSunday`, `r/SAHP`, `r/Parenting`, and `r/homeschool`. Do not expand communities yet. Use search-engine snippets first to avoid Reddit 429s; only open high-signal public threads. Observation only: no posting, commenting, voting, DMs, product mentions, or private group scraping. Build a coded evidence table with columns: Community, Date/timeframe, Source type, Post context, Pain moment, Parent pain, Exact language, Current workaround, Workaround failure, What parent is really asking for, Product implication, Feature temptation to avoid, Confidence, Evidence note/source URL. First run a pilot of about 20 rows across all five communities and stop for review before scaling to 125–200 total rows. Save the plan and pilot findings under `/Users/arku/Projects/AITXhackathon/docs/product/`.

## Recommended first concrete task

Ginnie/OpenClaw should start with:

1. Save this plan under `docs/product/`.
2. Create the evidence table template.
3. Run the 20-row pilot only.
4. Stop and ask Hemant/Hermes to review pilot quality before scaling.

## Confidence

High.

This approach improves research quality without getting trapped by Reddit rate limits, avoids duplicate-agent confusion, and keeps 1Less focused on the core question:

> Does this remove one real decision for a busy parent without creating another chore?
