# 1Less Chapter 1 — Private Parent Scenario Loop Findings

Date: 2026-05-16  
Type: simulated parent-style scenario loop, not live user testing  
Commit under test: `9d5e7c8` / latest `main` at run time

## Core question

Does the current Chapter 1 dinner flow remove one dinner decision without creating another chore?

## Summary

Five scenario loops were run against the current service flow.

Overall result: **usable enough for a small private parent test, with one fallback caveat to watch.**

The core first-suggestion flow is working:

- one clear dinner
- why it fits
- rough effort/time
- safe ingredient wording
- fallback/tweak
- allergy caveat only when explicit avoidance/safety wording appears
- no creepy memory/pantry implication in the recommendation text
- no allergy, nutrition, medical, budget, or pantry-accuracy promises

Main watch item:

- The `Too much work` fallback can return a backup that is still about 20 minutes / normal effort. That may not feel like relief to a tired parent, even though it technically returns one backup. Treat this as a private-test observation point before adding features.

## Scenario results

### S1 — Tired parent, 10 minutes, picky kid, no allergy

Prompt:

> I have 10 minutes and barely cooking energy. Make it picky-kid friendly.

Result:

> Tonight: Black Bean Tacos with fruit.

Pass notes:

- One clear dinner.
- No allergy caveat.
- No memory/pantry implication.
- Wording is mostly safe.

Watch note:

- The app says it is the closest practical fit because the meal is about 15 minutes, not 10. In live testing, watch whether that still feels like relief or feels like a miss.

### S2 — Vegetarian + dairy-free constraint

Prompt:

> Vegetarian and dairy-free tonight. I have 20 minutes.

Result:

> Tonight: Black Bean Tacos with fruit.

Pass notes:

- One clear dinner.
- Caveat appears because dairy-free is treated as an avoidance/safety constraint.
- No medical/nutrition/allergy guarantee.
- No overconfident “safe” language.

### S3 — Ingredient context: rice, eggs, frozen peas

Prompt:

> I have rice, eggs, and frozen peas. I have 20 minutes and normal energy.

Result:

> Tonight: Egg Fried Rice with peas.

Pass notes:

- Ingredient context is used positively.
- No allergy caveat.
- No implication that 1Less knows the pantry beyond what the parent typed.

### S4 — Explicit egg avoidance

Prompt:

> Avoid eggs. I have rice and frozen peas. I have 20 minutes.

Result:

> Tonight: Black Bean Tacos with fruit.

Pass notes:

- Egg-based meal avoided.
- Allergy/avoidance caveat appears near recommendation.
- No guarantee of allergy safety.

### S5 — Fallback pressure

Prompt sequence:

1. `I have 20 minutes and normal energy. Make it picky-kid friendly.`
2. `Too much work`

Initial result:

> Tonight: Black Bean Tacos with fruit.

Backup result:

> Backup: Egg Fried Rice with peas.

Pass notes:

- Returns one backup, not a list.
- Keeps decision flow simple.
- No allergy caveat or overclaim.

Watch / possible issue:

- Parent said `Too much work`, but backup is about 20 minutes / normal effort. This may not actually reduce burden.
- This should be observed in live private testing before deciding whether to adjust fallback logic or meal options.

## Recommendation

Proceed to a small private parent test with 3–5 people or tightly moderated scenario sessions.

Do **not** add Chapter 2, expand Story Picker, build weekly planning, or add platform architecture yet.

The next learning loop should collect usage/trust feedback:

- Did the parent accept the first suggestion?
- Did they need to think harder after seeing it?
- Did the fallback help?
- Did any wording feel unsafe, creepy, or overconfident?
- Did it feel like “one less decision,” or just another mini form?

## Suggested decision after live test

Only consider a code change if live/private testing confirms a repeated issue, especially:

- first suggestion not accepted because it misses time/energy constraints
- fallback does not feel lower burden
- allergy/privacy wording creates confusion or warning fatigue

Until then, keep the product in learning mode, not feature-expansion mode.
