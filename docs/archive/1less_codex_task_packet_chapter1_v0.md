# Official Codex Task Packet — 1Less Chapter 1 Dinner Decision MVP v0

**Status:** Archived Chapter 1 implementation packet. Keep for historical context; do not treat as the current overhaul prompt.

## Source of truth

- GitHub: <https://github.com/nyhemant/AITXhackathon> — legacy repo name; product name is 1Less.
- Only active local working copy: `/Users/arku/Projects/AITXhackathon` on the Mac mini
- Do not use MacBook Air or iCloud Drive copies.

## Current repo context

The existing app is a plain Python implementation under `src/busyparent_agent/` with:

- deterministic dinner agent: `agent.py`, `tools.py`, `service.py`
- local web UI/server: `web.py`
- fixture data under `data/`
- tests under `tests/`
- current test command: `python3 -m unittest discover -s tests`
- current local run command: `python3 -m busyparent_agent.web --host 0.0.0.0 --port 8000`

This packet captured the transition from the earlier BusyMom/Story Picker prototype toward **1Less**. Going forward, new work should treat 1Less as the standalone product and keep old names as implementation history only.

## Objective

Implement the first public-facing 1Less MVP flow: **Chapter 1 — Dinner Decision**, where the parent gets one clear dinner recommendation with minimal input and lightweight feedback.

The build should prove this product test:

> Does 1Less remove one real dinner decision for a busy parent without creating another chore?

## Product direction to preserve

- Company promise: **One less decision for busy parents.**
- Chapter 1 promise: **Tonight’s dinner, decided.**
- Dinner is the first proof point, not the whole brand identity.
- The product should feel like relief, not a recipe browser or meal-planning system.

## Scope

Make the smallest coherent changes needed to advance the existing implementation as a 1Less Chapter 1 MVP flow.

### 1. Branding/copy repositioning

Update public-facing copy so the app reads as **1Less**, with dinner as Chapter 1 / starting point.

Required copy ideas:

- Product name: `1Less`
- Primary positioning: `One less decision for busy parents.`
- Dinner chapter promise: `Tonight’s dinner, decided.`
- Explain that dinner is the first chapter/proof point without building other chapters.

Use chapter language at the product/copy level only. Do not introduce a chapter registry, generic decision engine, chapter routing system, or multi-chapter data model in this task.

Do not fully refactor package/module/class names unless required. Keep internal `busyparent_agent` naming if changing it would create risk.

### 2. Dinner-first MVP flow

Update the existing dinner web flow so the parent can provide minimal context through quick prompts/chips and/or free text:

- time available: 10 / 20 / 30 minutes
- energy level: barely cooking / normal / can cook
- constraints: picky eater/familiar kid-friendly option, vegetarian, nut-free, dairy-free, use leftovers, pantry/freezer meal
- optional free text for what they have or what to avoid

Any pantry/use-what-you-have language must be based only on what the parent enters in the current flow. Do not imply 1Less knows the household pantry or inventory.

The parent should not face a long setup wizard.

### 3. Recommendation output

The dinner recommendation must return **one clear decision**, not a list.

Every recommendation must include:

- meal name
- why it fits tonight
- rough time/effort
- simple ingredient/use-what-you-have guidance based only on parent input
- one fallback/tweak path
- allergy/preference caveat when relevant

### 4. Lightweight feedback actions

Add or expose low-friction feedback actions in the UI, using existing backend feedback behavior where possible:

- Good enough
- Too much work
- Kid won’t eat
- Missing ingredient
- Give me backup / fallback

Feedback should not require account creation, a heavy profile setup, a new database/profile schema, or long-term family memory storage beyond existing trivial feedback behavior.

### 5. Trust/safety copy

If allergy, privacy, kids, or family-memory wording is touched, use cautious language:

Good language:

- `Based on what you told me...`
- `I’ll avoid ingredients you marked as unsafe.`
- `Please check labels for allergies.`
- `For serious allergies, verify packaged foods and cross-contact risk.`

Avoid:

- `Safe for your child`
- `Guaranteed allergy-free`
- `Medically approved`
- `Perfectly balanced`
- `Nutritionist recommended` unless truly backed

Important trust contract:

- Do not claim allergy safety, nutrition optimization, medical diet support, budget optimization, cultural/religious dietary correctness, or pantry accuracy.
- Do not ask for or require child names, medical conditions, precise location, detailed health/nutrition goals, school schedules, pantry/fridge photos, or grocery purchase history.
- If a parent voluntarily types sensitive information into free text, do not highlight it, build profile features around it, or require it for future use.

Mandatory in-product allergy/avoidance caveat:

> 1Less can help avoid ingredients you flag, but it cannot guarantee allergy safety. Always check labels and use your judgment for serious allergies.

If allergy or avoidance input is present, this caveat must appear near the recommendation. It cannot live only in docs, policy text, or footer copy.

## Non-goals

Do **not** implement:

- bedtime/story choice as a new feature
- new Story Picker behavior, bedtime/story recommendation logic, or Story Picker polish beyond minimal copy-safe adjustments needed to avoid brand confusion or keep existing tests passing
- a generic multi-chapter platform
- chapter registry, generic decision engine, chapter router, reusable chapter infrastructure, or multi-chapter data model
- full chapter navigation beyond trivial copy/labels
- full weekly meal planning
- grocery delivery integrations
- photo pantry scanning
- calendar integration
- nutrition/macros optimization
- medical diet management
- broad parent command center behavior
- heavy family profile setup
- asking for or requiring child names, medical conditions, precise location, detailed health/nutrition goals, school schedules, pantry/fridge photos, or grocery purchase history
- authentication/login
- social sharing
- unrelated refactors
- changes outside `/Users/arku/Projects/AITXhackathon`

Do not let Codex decide broader product direction. Implement only this approved packet.

## Likely files to inspect/touch

Codex should inspect before editing, but likely files are:

- `src/busyparent_agent/web.py` — public web UI/copy, prompt chips, feedback controls, empty/loading/error UI
- `src/busyparent_agent/service.py` — if additional API/session handling is needed
- `src/busyparent_agent/agent.py` — only if feedback/constraint handling needs small changes
- `src/busyparent_agent/tools.py` — only if intent parsing needs small additions
- `tests/test_agent_rules.py` — backend/service tests
- `tests/test_storypath.py` — only if existing Story Picker tests need copy-safe adjustment; do not add Story Picker behavior
- `README.md` and/or `docs/demo.md` — update public docs to 1Less positioning

Avoid touching fixture data unless needed for a test.

## Acceptance criteria

### Product/UX

- A parent can reach a dinner recommendation in under 60 seconds.
- Output is one clear dinner decision, not many competing options.
- UI/copy preserves broader 1Less positioning: parent decision relief, starting with dinner.
- Dinner is framed as Chapter 1 / first proof point, not the entire brand identity.
- The flow feels low-burden: no long setup wizard, no heavy profile form.
- Feedback/fallback actions are visible or easily available.

### Trust/safety

- Allergy/diet constraints affect the recommendation or caveat.
- When allergy or avoidance input is selected or typed, the recommendation UI shows the mandatory in-product caution near the recommendation.
- UI does not imply guaranteed allergy safety.
- No medical, nutrition, budget, pantry-accuracy, cultural/religious dietary, or allergy guarantees are introduced.
- UI does not ask for or require child names, medical conditions, precise location, detailed health/nutrition goals, school schedules, pantry/fridge photos, or grocery purchase history.
- Privacy/family-memory copy does not encourage unnecessary sensitive data collection.

### Engineering

- Existing tests pass.
- New or updated tests cover the changed behavior where practical:
  - recommendation remains one meal
  - constraint/allergy caveat remains cautious
  - feedback/fallback path remains available
  - public copy includes 1Less positioning and does not frame the product as dinner-only
- Git diff contains only intended changes.
- App still runs locally with `python3 -m busyparent_agent.web --host 0.0.0.0 --port 8000`.

## Required verification commands

From `/Users/arku/Projects/AITXhackathon`:

```bash
pwd
git rev-parse --show-toplevel
git fetch origin --prune
git status --short --branch
git log -1 --oneline HEAD
git log -1 --oneline origin/main
python3 -m unittest discover -s tests
```

Manual smoke after implementation:

```bash
python3 -m busyparent_agent.web --host 0.0.0.0 --port 8000
```

Smoke cases:

1. No constraints: parent asks for dinner and gets one recommendation.
2. 15-minute low-energy dinner: recommendation should be fast/low effort.
3. Nut allergy / ingredient avoidance: no guarantee language; caveat appears.
4. Picky eater: recommendation adapts or explains kid-friendly choice.
5. Missing ingredient / fallback: parent can request a backup/tweak.
6. Copy check: 1Less is not framed as dinner-only.
7. Copy check: no allergy guarantee, no medical/nutrition claim.

## Sophie review gate

Before finalizing/committing user-facing copy, ask Sophie or apply a Sophie-style trust review for:

- allergy caveat
- privacy language
- onboarding prompt
- parent-facing tone
- wording around kids, safety, family memory, or trust

## Stop / rollback conditions

Stop and ask Hemant if implementation starts expanding into:

- bedtime/story buildout
- Story Picker behavior changes beyond minimal copy-safe adjustments
- generic multi-chapter platform
- chapter registry, generic decision engine, chapter routing system, or multi-chapter data model
- weekly meal planning
- grocery integrations
- detailed family profiles
- sensitive child/medical/location/nutrition data collection
- nutrition/medical claims
- broad parent command center functionality
- large architecture rewrite

Stop if Codex starts making product decisions beyond this task packet.

Rollback plan:

```bash
git diff --stat
git restore <unwanted-files>
```

If changes are committed and need rollback later:

```bash
git revert <commit-sha>
```

## Suggested Codex prompt

```text
You are working in the repo /Users/arku/Projects/AITXhackathon.

Do not use any MacBook Air or iCloud Drive project copy. Do not execute broad refactors. Do not decide product direction beyond this packet.

Task: Implement 1Less Chapter 1 — Dinner Decision MVP Flow v0.

Read docs/product/1less_mvp_product_brief_v0.2.md and docs/product/1less_codex_task_packet_chapter1_v0.md first.

Objective:
Advance the existing implementation as 1Less: parent decision relief, starting with dinner. Make the dinner flow feel like one low-burden decision helper, not a recipe browser or full meal-planning system.

Scope:
- Update public-facing web/docs copy to 1Less.
- Keep dinner as Chapter 1 / first proof point.
- Do not build future chapters or a generic chapter engine.
- Use chapter language at the product/copy level only; do not add chapter architecture.
- The repo already has Story Picker code. Do not expand Story Picker or build bedtime/story behavior. Only make minimal copy-safe adjustments if necessary.
- Add/update minimal dinner context controls/prompts if they fit the existing web architecture.
- Preserve one recommendation first.
- Expose lightweight feedback/fallback actions where practical.
- Preserve cautious allergy/privacy language.
- Important trust contract: do not claim allergy safety, nutrition optimization, medical diet support, budget optimization, cultural/religious dietary correctness, or pantry accuracy. If allergy/avoidance input is present, show an in-product allergy caveat near the recommendation. Do not ask for or require child names, medical conditions, precise location, detailed health/nutrition goals, school schedules, pantry/fridge photos, or grocery purchase history.
- Add/update tests for changed behavior.

Non-goals:
No bedtime/story buildout, no Story Picker behavior expansion, no generic chapter architecture, no full weekly planning, no grocery integrations, no photo scanning, no auth, no heavy profiles, no sensitive child/medical/location/nutrition data prompts, no medical/nutrition/allergy/budget/pantry-accuracy guarantees, no unrelated refactors.

Before editing:
- Show current git status.
- Identify likely files to touch.
- Confirm the smallest implementation plan.

After editing:
- Run python3 -m unittest discover -s tests.
- Show git diff --stat and summarize changed files.
- Do not commit unless Hemant/Ginnie explicitly approves.
```
