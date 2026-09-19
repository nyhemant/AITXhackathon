# 1Less Synthetic Parent Gauntlet — fallback polish pass — 2026-05-16

Generated from current local service code after the narrow fallback-relief polish. Synthetic/non-human validation only; it does not prove felt parent relief.

## Summary

- 50-prompt gauntlet: 50/50 passed.
- Focused fallback stress: 10/10 passed.
- Regression focus: fallback relief, sparse `only have X`, allergy/avoidance, ingredient context not treated as avoidance, and no allergy caveat unless explicit safety/avoidance wording exists.

## Focused fallback stress

| Initial prompt | Feedback | First meal | Backup meal | First min | Backup min | Result | Failed checks |
|---|---|---|---|---:|---:|---|---|
| I have 30 minutes and can cook. | Too much work | Sheet-pan chicken and corn rice bowls | Rice and Peas Bowl | 30 | 10 | PASS | - |
| I have 30 minutes and can cook. | I need easier | Sheet-pan chicken and corn rice bowls | Rice and Peas Bowl | 30 | 10 | PASS | - |
| I have 30 minutes and can cook. | No cooking if possible | Sheet-pan chicken and corn rice bowls | Rice and Peas Bowl | 30 | 10 | PASS | - |
| I have 30 minutes and can cook. | I only have 10 minutes | Sheet-pan chicken and corn rice bowls | Rice and Peas Bowl | 30 | 10 | PASS | - |
| I have 25 minutes and normal energy. | Too much cooking | Black Bean Tacos with fruit | Rice and Peas Bowl | 15 | 10 | PASS | - |
| Avoid eggs. I have 30 minutes and can cook. | Too much work | Black Bean Tacos with fruit | Rice and Peas Bowl | 15 | 10 | PASS | - |
| Nut-free tonight. I have 30 minutes and can cook. | I need easier | Sheet-pan chicken and corn rice bowls | Rice and Peas Bowl | 30 | 10 | PASS | - |
| Only rice and frozen peas tonight. | Too much work | Rice and Peas Bowl | Rice and Peas Bowl | 10 | 10 | PASS | - |
| My kid is picky and I have 30 minutes. | Kid won't eat that | Black Bean Tacos with fruit | Egg Fried Rice with peas | 15 | 20 | PASS | - |
| I have 20 minutes and normal energy. | Give me backup | Black Bean Tacos with fruit | Egg Fried Rice with peas | 15 | 20 | PASS | - |

## Full gauntlet table

| # | Category | Prompt | Result | Meal | Caveat | Failed checks |
|---:|---|---|---|---|---|---|
| 1 | tired_short | I have 10 minutes and barely cooking energy. Make it picky-kid friendly. | PASS | Black Bean Tacos with fruit | no | - |
| 2 | tired_short | I'm exhausted and everyone is hungry. Need the easiest dinner. | PASS | Black Bean Tacos with fruit | no | - |
| 3 | tired_short | 10 minutes before meltdown, no cooking if possible. | PASS | Black Bean Tacos with fruit | no | - |
| 4 | tired_short | I need the low effort version tonight. | PASS | Black Bean Tacos with fruit | no | - |
| 5 | tired_short | Cooking energy is gone, but kids need dinner. | PASS | Black Bean Tacos with fruit | no | - |
| 6 | picky | My kid is picky and I have 20 minutes. | PASS | Black Bean Tacos with fruit | no | - |
| 7 | picky | Give me something mild both kids may eat tonight. | PASS | Black Bean Tacos with fruit | no | - |
| 8 | picky | Familiar dinner for a picky kid, no drama. | PASS | Black Bean Tacos with fruit | no | - |
| 9 | picky | My child will reject anything spicy or weird. | PASS | Black Bean Tacos with fruit | no | - |
| 10 | picky | Kids are cranky and I need a safe default. | PASS | Black Bean Tacos with fruit | no | - |
| 11 | vegetarian | Vegetarian tonight. I have 25 minutes. | PASS | Black Bean Tacos with fruit | no | - |
| 12 | vegetarian | No meat tonight, 15 minutes if possible. | PASS | Black Bean Tacos with fruit | no | - |
| 13 | dairy_free | Dairy-free tonight. I have 20 minutes. | PASS | Black Bean Tacos with fruit | yes | - |
| 14 | dairy_free | Without dairy tonight, but keep it kid friendly. | PASS | Black Bean Tacos with fruit | yes | - |
| 15 | nut_free | Nut-free tonight, picky kid, 15 minutes. | PASS | Black Bean Tacos with fruit | yes | - |
| 16 | nut_free | Avoid peanuts and tree nuts tonight. | PASS | Black Bean Tacos with fruit | yes | - |
| 17 | ingredients | I have rice, eggs, and frozen peas. I have 20 minutes and normal energy. | PASS | Egg Fried Rice with peas | no | - |
| 18 | ingredients | We have tortillas, black beans, salsa, and fruit. 15 minutes. | PASS | Black Bean Tacos with fruit | no | - |
| 19 | ingredients | Use pasta and marinara. I have 25 minutes. | PASS | Pasta Marinara with carrots | no | - |
| 20 | ingredients | I have chicken, rice, and corn. I can cook for 30 minutes. | PASS | Sheet-pan chicken and corn rice bowls | no | - |
| 21 | ingredients | Rice and peas in the freezer, can you decide dinner? | PASS | Egg Fried Rice with peas | no | - |
| 22 | low_ingredient | I have pasta and butter. Kids are hungry. | PASS | Pasta Marinara with carrots | no | - |
| 23 | low_ingredient | Only rice and frozen peas tonight. | PASS | Rice and Peas Bowl | no | - |
| 24 | low_ingredient | We only have rice and peas and maybe soy sauce. | PASS | Rice and Peas Bowl | no | - |
| 25 | low_ingredient | Only tortillas and beans in the house. | PASS | Black Bean Tacos with fruit | no | - |
| 26 | low_ingredient | I only have pasta and carrots. | PASS | Pasta Marinara with carrots | no | - |
| 27 | avoid | Avoid eggs. I have rice and frozen peas. I have 20 minutes. | PASS | Rice and Peas Bowl | yes | - |
| 28 | avoid | No dairy. Vegetarian. 20 minutes. | PASS | Black Bean Tacos with fruit | yes | - |
| 29 | avoid | Without nuts and no spicy food for a guest kid. | PASS | Black Bean Tacos with fruit | yes | - |
| 30 | avoid | Egg-free and dairy-free, use rice if possible. | PASS | Black Bean Tacos with fruit | yes | - |
| 31 | avoid | No cheese, no yogurt, no milk tonight. | PASS | Black Bean Tacos with fruit | yes | - |
| 32 | allergy | Peanut allergy. Need dinner in 15 minutes. | PASS | Black Bean Tacos with fruit | yes | - |
| 33 | allergy | Egg allergy. I have rice and frozen peas. I have 20 minutes. | PASS | Rice and Peas Bowl | yes | - |
| 34 | allergy | Milk allergy, vegetarian, 20 minutes. | PASS | Black Bean Tacos with fruit | yes | - |
| 35 | allergy | Allergic to peanuts, keep it simple. | PASS | Black Bean Tacos with fruit | yes | - |
| 36 | false_caveat | I have dairy, rice, and frozen peas. 20 minutes. | PASS | Egg Fried Rice with peas | no | - |
| 37 | false_caveat | I have 30 minutes and can cook. | PASS | Sheet-pan chicken and corn rice bowls | no | - |
| 38 | false_caveat | I have peanuts for lunch tomorrow but dinner can be simple. | PASS | Black Bean Tacos with fruit | no | - |
| 39 | false_caveat | Eggs are in the fridge and rice is cooked. | PASS | Black Bean Tacos with fruit | no | - |
| 40 | vague | What should I make tonight? I'm tired. | PASS | Black Bean Tacos with fruit | no | - |
| 41 | vague | Everyone is cranky and dinner is not planned. | PASS | Black Bean Tacos with fruit | no | - |
| 42 | vague | I cannot think about dinner anymore. | PASS | Black Bean Tacos with fruit | no | - |
| 43 | contradictory | I have 10 minutes but can cook something involved. | PASS | Sheet-pan chicken and corn rice bowls | no | - |
| 44 | contradictory | Picky kid but make it adventurous. 20 minutes. | PASS | Black Bean Tacos with fruit | no | - |
| 45 | fallback_request | Give me backup for dinner. 20 minutes. | PASS | Black Bean Tacos with fruit | no | - |
| 46 | fallback_request | I need easier than a normal dinner tonight. | PASS | Black Bean Tacos with fruit | no | - |
| 47 | fallback_request | Too much cooking, give me the lower effort decision. | PASS | Black Bean Tacos with fruit | no | - |
| 48 | safety_edge | Dairy-free, nut-free, egg-free. 15 minutes. | PASS | Black Bean Tacos with fruit | yes | - |
| 49 | safety_edge | No nuts, no dairy, picky kid, and I am exhausted. | PASS | Black Bean Tacos with fruit | yes | - |
| 50 | sparse_avoidance | Only rice and frozen peas, but avoid eggs. | PASS | Rice and Peas Bowl | yes | - |

## Watch outputs

No scored failures. Remaining limitation: this is synthetic logic/copy validation only, not evidence that real parents feel relief.
