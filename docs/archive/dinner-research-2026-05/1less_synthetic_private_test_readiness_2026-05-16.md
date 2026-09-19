# 1Less Chapter 1 — Synthetic Private-Test Readiness Packet

Date: 2026-05-16  
Evaluation type: synthetic/non-human readiness pass  
Scope: Chapter 1 dinner decision flow only  
Decision: **Ready for 3–5 moderated private parent tests; do not expand features yet.**

## Boundary

This evaluation can validate logic, trust, copy, obvious friction, and regressions. It cannot prove that parents actually feel relief. That still requires human/private testing.

## What was run

- 30 messy parent-style prompts across:
  - tired / short time
  - picky kid
  - vegetarian / dairy-free / nut-free
  - ingredient context
  - explicit avoidances
  - allergy wording
  - fallback requests
  - vague parent input
  - contradictory input
  - low-ingredient input
  - safety edge cases
- fallback stress prompts:
  - `Too much work`
  - `Kid won't eat that`
  - `Missing ingredient`
  - `I need easier`
  - `Give me backup`
  - `I only have 10 minutes`
  - `No cooking if possible`
- trust/copy review of output language.

Raw synthetic output table is saved at:

```text
work/evals/1less_synthetic_parent_gauntlet_2026-05-16.md
```

## Summary

Main recommendation logic: **passes synthetic readiness.**

The 30-prompt gauntlet passed the core scored checks:

- one clear dinner
- why it fits
- rough effort/time
- safe ingredient wording
- fallback/tweak present
- no false allergy caveat on plain ingredient or time wording
- allergy/avoidance caveat appears when explicit safety/avoidance wording is present
- no creepy pantry/memory implication in recommendation copy
- no allergy, medical, nutrition, budget, or pantry-accuracy promise

Trust/copy review: **no hard safety/copy blocker found.**

## Main weakness

Fallback relief is weak.

The fallback stress run found that backup responses often return a meal that is not easier/faster than the first recommendation. Examples:

- Parent says: `Too much work`
- Backup returns: `Egg Fried Rice with peas`
- Output says: `Time/effort: about 20 minutes, normal effort.`

That may not feel like relief, even though it technically returns one backup.

## Additional watch item

Low-ingredient hard constraints need human observation.

Example:

- Prompt: `Only rice and frozen peas tonight.`
- Current output: `Black Bean Tacos with fruit.`

This is not an allergy/safety issue, but it can be a trust hit because `only` implies a hard-ish ingredient constraint. Watch for this in private tests before deciding whether to add a small constraint parser fix.

## Trust/copy review

No hard blocker found for:

- allergy overclaim
- nutrition or medical overclaim
- hidden pantry/memory implication
- “we know your family” language
- advice that sounds medical
- allergy caveat wording

The existing caveat remains appropriate:

> 1Less can help avoid ingredients you flag, but it cannot guarantee allergy safety. Always check labels and use your judgment for serious allergies.

## Recommendation

Proceed to **3–5 moderated private parent tests**.

Moderated means: watch the parent use the flow or ask for immediate reactions, especially around whether fallback helped. Do not treat this as unmoderated launch readiness.

If private tests are unmoderated, fix fallback relief first.

## What to observe in human/private tests

Ask or observe:

- Did the parent accept the first dinner suggestion?
- Did they need to think harder after seeing it?
- Did the fallback help?
- Did any wording feel unsafe, creepy, or overconfident?
- Did the app avoid allergy/nutrition/medical promises?
- Did it feel like “one less decision,” or just another mini form?

## Do not do next

Do not add:

- Chapter 2
- Story Picker expansion
- weekly planning
- grocery optimization
- pantry inventory
- saved ingredient profiles
- nutrition/macros
- medical diet handling
- multi-chapter architecture

## Possible next fix only if needed

Only if human tests or another focused gate confirms the fallback issue, consider a narrow bugfix:

- detect `Too much work`, `I need easier`, `No cooking if possible`, and `I only have 10 minutes` as stronger fallback constraints
- return a backup that is faster, lower effort, or explicitly explains why it is still the simplest realistic option
- do not add broad NLP, meal planning, pantry storage, or new architecture

Until then, the next loop should be usage/trust feedback, not feature expansion.
