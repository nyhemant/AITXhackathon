# 1Less Chapter 1 — Private Parent Test Plan v0

Status: updated after Reddit community observation scan  
Scope: usage/trust feedback only; no feature expansion

## Core question

Does the current Chapter 1 dinner flow remove one dinner decision without creating another chore — specifically at the late-day “4:47pm dinner meltdown” moment?

## Test size

Run with either:

- 3–5 private parent testers, preferably working parents / working moms with young or school-age kids, or
- 3–5 realistic parent-style scenarios if live testers are not ready yet.

This is not a growth, onboarding, or retention test. It is a trust/usefulness gate.

Positioning under test:

> For the 4:47pm dinner meltdown: one realistic dinner decision, not a recipe rabbit hole.

Watch whether this feels true, too cute, too narrow, or genuinely relieving.

## What to observe

For each tester/scenario, capture:

1. Did the parent accept the first dinner suggestion?
2. Did they need to think harder after seeing it?
3. Did the fallback help?
4. Did any wording feel unsafe, creepy, or overconfident?
5. Did the app avoid allergy, nutrition, and medical promises?
6. Did it feel like “one less decision,” or just another mini form?
7. Did it feel like one realistic answer, not twenty recipes?
8. Did “use what I have” feel grounded in what they typed, without implying pantry memory?

## Suggested test scenarios

### Scenario 1 — 4:47pm dinner meltdown

Prompt:

> It is 4:47pm, everyone is hungry, I have 10 minutes and barely cooking energy. Make it picky-kid friendly.

Watch for:

- one clear dinner
- low-effort framing
- no allergy caveat
- no pantry/memory implication

### Scenario 2 — explicit dietary constraint

Prompt:

> Vegetarian and dairy-free tonight. I have 20 minutes.

Watch for:

- one clear dinner
- caveat appears because dairy-free is an avoidance/safety constraint
- no medical/nutrition/allergy guarantee
- no overconfident “safe” language

### Scenario 3 — use what I have

Prompt:

> I have rice, eggs, and frozen peas. I have 20 minutes and normal energy.

Watch for:

- recommendation uses ingredient context positively
- no allergy caveat
- no implication that the app knows the pantry beyond what the parent typed

### Scenario 4 — explicit allergy/avoidance

Prompt:

> Avoid eggs. I have rice and frozen peas. I have 20 minutes.

Watch for:

- egg-based meals are avoided
- allergy/avoidance caveat appears near recommendation
- no guarantee of allergy safety

### Scenario 5 — fallback pressure

Prompt sequence:

1. Ask for dinner with a realistic constraint.
2. Click or type: `Too much work` or `Kid won't eat this`.

Watch for:

- fallback reduces burden rather than opening a new decision tree
- `Too much work` reduces at least one of time, cleanup, steps, active attention, or ingredient complexity
- `Kid won't eat this` tries a deconstructed/familiar-side version before a totally unrelated adult recipe
- parent still ends with one plausible dinner

### Scenario 6 — no store run / pantry constraint

Prompt:

> No store run. I only have pasta, jarred sauce, frozen peas, yogurt, and apples. I have 15 minutes.

Watch for:

- uses current-turn ingredients as constraints
- does not invent groceries as required items
- gives a good-enough default rather than a full meal plan

### Scenario 7 — parent has ideas but no brain

Prompt:

> I have a few dinner ideas but no brain left to decide. We have tortillas, cheese, beans, rice, and fruit. Pick one.

Watch for:

- acknowledges decision fatigue without being patronizing
- chooses one path
- avoids presenting a comparison list that recreates the decision

## Pass condition

The MVP is usable enough for small private testing if most scenarios/testers show:

- one clear dinner
- why it fits
- rough effort/time
- safe ingredient wording
- one fallback/tweak
- no allergy caveat unless actual allergy/avoidance is present
- no creepy memory/pantry implication
- no allergy, nutrition, medical, budget, or pantry-accuracy promises
- tester feels relief rather than another chore
- tester understands the product as dinner-crunch relief, not recipe discovery or meal planning

## Stop conditions

Do not continue adding features if feedback points to trust/copy/usability issues. Fix the smallest trust or flow problem first.

Stop immediately if the next proposed work drifts into:

- Chapter 2
- Story Picker expansion
- weekly planning
- grocery optimization
- pantry inventory
- saved ingredient profiles
- nutrition/macros
- medical diet handling
- multi-chapter architecture

## Next learning loop

The next learning loop is usage/trust feedback, not platform architecture.

Recommended next artifact after testing: a short findings note with:

- accepted first suggestion: yes/no
- fallback used: yes/no
- confusing or unsafe wording
- what felt like relief
- what felt like a chore
- whether “4:47pm dinner meltdown” resonated or felt gimmicky
- whether “one realistic answer, not twenty recipes” was visible in the experience
- one recommended next fix, if any
