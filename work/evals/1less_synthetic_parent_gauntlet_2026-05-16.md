# 1Less Synthetic Parent Gauntlet — 2026-05-16

Generated from current local `main` service code. This is non-human logic/trust/copy validation, not proof of felt relief.

## Summary

30-prompt gauntlet: 30/30 passed.

No hard failures in scored checks.

## Fallback stress summary

Fallback stress: 1/7 passed the easier/faster/clearer-backup heuristic.

### `Too much work` — PASS

Expected: should be easier or clearly explain practical fallback

First: Black Bean Tacos with fruit / 15 min / effort rank 1

Backup: Egg Fried Rice with peas / 20 min / effort rank 2

Backup output:

```text
Backup: Egg Fried Rice with peas.
Why it fits: it is the closest practical fit; it keeps cooking effort low; it is a familiar kid-friendly direction based on what you told me.
Time/effort: about 20 minutes, normal effort.
Works with common basics like: rice, eggs, frozen peas or another vegetable that fits your house, and a light sauce.
Simple plan: Scramble eggs, stir-fry rice with peas, keep sauce light for kids, and add grown-up heat at the table.
Fallback/tweak: If eggs are out, make quick vegetable fried rice with beans, tofu, or another protein you have.
One decision, not a recipe search.
```

### `Kid won't eat that` — FAIL

Expected: should become more familiar/kid-friendly

First: Black Bean Tacos with fruit / 15 min / effort rank 1

Backup: Egg Fried Rice with peas / 20 min / effort rank 2

Backup output:

```text
Backup: Egg Fried Rice with peas.
Why it fits: it fits the 20-minute window; it is a familiar kid-friendly direction based on what you told me.
Time/effort: about 20 minutes, normal effort.
Works with common basics like: rice, eggs, frozen peas or another vegetable that fits your house, and a light sauce.
Simple plan: Scramble eggs, stir-fry rice with peas, keep sauce light for kids, and add grown-up heat at the table.
Fallback/tweak: If eggs are out, make quick vegetable fried rice with beans, tofu, or another protein you have.
One decision, not a recipe search.
```

### `Missing ingredient` — FAIL

Expected: should offer different backup

First: Black Bean Tacos with fruit / 15 min / effort rank 1

Backup: Egg Fried Rice with peas / 20 min / effort rank 2

Backup output:

```text
Backup: Egg Fried Rice with peas.
Why it fits: it fits the 20-minute window; it is a familiar kid-friendly direction based on what you told me.
Time/effort: about 20 minutes, normal effort.
Works with common basics like: rice, eggs, frozen peas or another vegetable that fits your house, and a light sauce.
Simple plan: Scramble eggs, stir-fry rice with peas, keep sauce light for kids, and add grown-up heat at the table.
Fallback/tweak: If eggs are out, make quick vegetable fried rice with beans, tofu, or another protein you have.
One decision, not a recipe search.
```

### `I need easier` — FAIL

Expected: should not ignore easier request

First: Black Bean Tacos with fruit / 15 min / effort rank 1

Backup: Black Bean Tacos with fruit / 15 min / effort rank 1

Backup output:

```text
Tonight: Black Bean Tacos with fruit.
Why it fits: it fits the 20-minute window; it is a familiar kid-friendly direction based on what you told me.
Time/effort: about 15 minutes, low effort.
Works with common basics like: tortillas, black beans, mild salsa or avocado, and any fruit or crunchy side that fits your house.
Simple plan: Warm beans, fold them into tortillas with mild salsa or avocado, and serve fruit or a simple side.
Fallback/tweak: If tortillas are missing, make quick bean-and-rice bowls with the same toppings.
One decision, not a recipe search.
```

### `Give me backup` — FAIL

Expected: should provide one backup

First: Black Bean Tacos with fruit / 15 min / effort rank 1

Backup: Egg Fried Rice with peas / 20 min / effort rank 2

Backup output:

```text
Backup: Egg Fried Rice with peas.
Why it fits: it fits the 20-minute window; it is a familiar kid-friendly direction based on what you told me.
Time/effort: about 20 minutes, normal effort.
Works with common basics like: rice, eggs, frozen peas or another vegetable that fits your house, and a light sauce.
Simple plan: Scramble eggs, stir-fry rice with peas, keep sauce light for kids, and add grown-up heat at the table.
Fallback/tweak: If eggs are out, make quick vegetable fried rice with beans, tofu, or another protein you have.
One decision, not a recipe search.
```

### `I only have 10 minutes` — FAIL

Expected: should bias shorter/easier

First: Black Bean Tacos with fruit / 15 min / effort rank 1

Backup: Black Bean Tacos with fruit / 15 min / effort rank 1

Backup output:

```text
Tonight: Black Bean Tacos with fruit.
Why it fits: it is the closest practical fit; it is a familiar kid-friendly direction based on what you told me.
Time/effort: about 15 minutes, low effort.
Works with common basics like: tortillas, black beans, mild salsa or avocado, and any fruit or crunchy side that fits your house.
Simple plan: Warm beans, fold them into tortillas with mild salsa or avocado, and serve fruit or a simple side.
Fallback/tweak: If tortillas are missing, make quick bean-and-rice bowls with the same toppings.
One decision, not a recipe search.
```

### `No cooking if possible` — FAIL

Expected: should bias lower effort if recognized

First: Black Bean Tacos with fruit / 15 min / effort rank 1

Backup: Black Bean Tacos with fruit / 15 min / effort rank 1

Backup output:

```text
Tonight: Black Bean Tacos with fruit.
Why it fits: it fits the 20-minute window; it is a familiar kid-friendly direction based on what you told me.
Time/effort: about 15 minutes, low effort.
Works with common basics like: tortillas, black beans, mild salsa or avocado, and any fruit or crunchy side that fits your house.
Simple plan: Warm beans, fold them into tortillas with mild salsa or avocado, and serve fruit or a simple side.
Fallback/tweak: If tortillas are missing, make quick bean-and-rice bowls with the same toppings.
One decision, not a recipe search.
```

## Full gauntlet table

| # | Category | Prompt | Result | Meal | Caveat | Failed checks |
|---|---|---|---|---|---|---|
| 1 | tired_short | I have 10 minutes and barely cooking energy. Make it picky-kid friendly. | PASS | Black Bean Tacos with fruit | no | - |
| 2 | tired_short | I'm exhausted and everyone is hungry. Need the easiest dinner. | PASS | Black Bean Tacos with fruit | no | - |
| 3 | tired_short | 10 minutes before meltdown, no cooking if possible. | PASS | Black Bean Tacos with fruit | no | - |
| 4 | picky | My kid is picky and I have 20 minutes. | PASS | Black Bean Tacos with fruit | no | - |
| 5 | picky | Give me something mild both kids may eat tonight. | PASS | Black Bean Tacos with fruit | no | - |
| 6 | vegetarian | Vegetarian tonight. I have 25 minutes. | PASS | Black Bean Tacos with fruit | no | - |
| 7 | dairy_free | Dairy-free tonight. I have 20 minutes. | PASS | Black Bean Tacos with fruit | yes | - |
| 8 | nut_free | Nut-free tonight, picky kid, 15 minutes. | PASS | Black Bean Tacos with fruit | yes | - |
| 9 | ingredients | I have rice, eggs, and frozen peas. I have 20 minutes and normal energy. | PASS | Egg Fried Rice with peas | no | - |
| 10 | ingredients | We have tortillas, black beans, salsa, and fruit. 15 minutes. | PASS | Black Bean Tacos with fruit | no | - |
| 11 | ingredients | Use pasta and marinara. I have 25 minutes. | PASS | Pasta Marinara with carrots | no | - |
| 12 | ingredients | I have chicken, rice, and corn. I can cook for 30 minutes. | PASS | Sheet-pan chicken and corn rice bowls | no | - |
| 13 | low_ingredient | I have pasta and butter. Kids are hungry. | PASS | Pasta Marinara with carrots | no | - |
| 14 | low_ingredient | Only rice and frozen peas tonight. | PASS | Black Bean Tacos with fruit | no | - |
| 15 | avoid | Avoid eggs. I have rice and frozen peas. I have 20 minutes. | PASS | Black Bean Tacos with fruit | yes | - |
| 16 | avoid | No dairy. Vegetarian. 20 minutes. | PASS | Black Bean Tacos with fruit | yes | - |
| 17 | avoid | Without nuts and no spicy food for a guest kid. | PASS | Black Bean Tacos with fruit | yes | - |
| 18 | allergy | Peanut allergy. Need dinner in 15 minutes. | PASS | Black Bean Tacos with fruit | yes | - |
| 19 | allergy | Egg allergy. I have rice and frozen peas. I have 20 minutes. | PASS | Black Bean Tacos with fruit | yes | - |
| 20 | allergy | Milk allergy, vegetarian, 20 minutes. | PASS | Black Bean Tacos with fruit | yes | - |
| 21 | false_caveat | I have dairy, rice, and frozen peas. 20 minutes. | PASS | Egg Fried Rice with peas | no | - |
| 22 | false_caveat | I have 30 minutes and can cook. | PASS | Sheet-pan chicken and corn rice bowls | no | - |
| 23 | false_caveat | I have peanuts for lunch tomorrow but dinner can be simple. | PASS | Black Bean Tacos with fruit | no | - |
| 24 | vague | What should I make tonight? I'm tired. | PASS | Black Bean Tacos with fruit | no | - |
| 25 | vague | Everyone is cranky and dinner is not planned. | PASS | Black Bean Tacos with fruit | no | - |
| 26 | contradictory | I have 10 minutes but can cook something involved. | PASS | Sheet-pan chicken and corn rice bowls | no | - |
| 27 | contradictory | Picky kid but make it adventurous. 20 minutes. | PASS | Black Bean Tacos with fruit | no | - |
| 28 | fallback_request | Give me backup for dinner. 20 minutes. | PASS | Black Bean Tacos with fruit | no | - |
| 29 | fallback_request | I need easier than a normal dinner tonight. | PASS | Black Bean Tacos with fruit | no | - |
| 30 | safety_edge | Dairy-free, nut-free, egg-free. 15 minutes. | PASS | Black Bean Tacos with fruit | yes | - |

## Five worst / watch outputs

### fallback:Kid won't eat that — fallback

Prompt: Kid won't eat that

```text
Backup: Egg Fried Rice with peas.
Why it fits: it fits the 20-minute window; it is a familiar kid-friendly direction based on what you told me.
Time/effort: about 20 minutes, normal effort.
Works with common basics like: rice, eggs, frozen peas or another vegetable that fits your house, and a light sauce.
Simple plan: Scramble eggs, stir-fry rice with peas, keep sauce light for kids, and add grown-up heat at the table.
Fallback/tweak: If eggs are out, make quick vegetable fried rice with beans, tofu, or another protein you have.
One decision, not a recipe search.
```

Failed/watch checks: fallback_easier

### fallback:Missing ingredient — fallback

Prompt: Missing ingredient

```text
Backup: Egg Fried Rice with peas.
Why it fits: it fits the 20-minute window; it is a familiar kid-friendly direction based on what you told me.
Time/effort: about 20 minutes, normal effort.
Works with common basics like: rice, eggs, frozen peas or another vegetable that fits your house, and a light sauce.
Simple plan: Scramble eggs, stir-fry rice with peas, keep sauce light for kids, and add grown-up heat at the table.
Fallback/tweak: If eggs are out, make quick vegetable fried rice with beans, tofu, or another protein you have.
One decision, not a recipe search.
```

Failed/watch checks: fallback_easier

### fallback:I need easier — fallback

Prompt: I need easier

```text
Tonight: Black Bean Tacos with fruit.
Why it fits: it fits the 20-minute window; it is a familiar kid-friendly direction based on what you told me.
Time/effort: about 15 minutes, low effort.
Works with common basics like: tortillas, black beans, mild salsa or avocado, and any fruit or crunchy side that fits your house.
Simple plan: Warm beans, fold them into tortillas with mild salsa or avocado, and serve fruit or a simple side.
Fallback/tweak: If tortillas are missing, make quick bean-and-rice bowls with the same toppings.
One decision, not a recipe search.
```

Failed/watch checks: fallback_easier

### fallback:Give me backup — fallback

Prompt: Give me backup

```text
Backup: Egg Fried Rice with peas.
Why it fits: it fits the 20-minute window; it is a familiar kid-friendly direction based on what you told me.
Time/effort: about 20 minutes, normal effort.
Works with common basics like: rice, eggs, frozen peas or another vegetable that fits your house, and a light sauce.
Simple plan: Scramble eggs, stir-fry rice with peas, keep sauce light for kids, and add grown-up heat at the table.
Fallback/tweak: If eggs are out, make quick vegetable fried rice with beans, tofu, or another protein you have.
One decision, not a recipe search.
```

Failed/watch checks: fallback_easier

### fallback:I only have 10 minutes — fallback

Prompt: I only have 10 minutes

```text
Tonight: Black Bean Tacos with fruit.
Why it fits: it is the closest practical fit; it is a familiar kid-friendly direction based on what you told me.
Time/effort: about 15 minutes, low effort.
Works with common basics like: tortillas, black beans, mild salsa or avocado, and any fruit or crunchy side that fits your house.
Simple plan: Warm beans, fold them into tortillas with mild salsa or avocado, and serve fruit or a simple side.
Fallback/tweak: If tortillas are missing, make quick bean-and-rice bowls with the same toppings.
One decision, not a recipe search.
```

Failed/watch checks: fallback_easier

