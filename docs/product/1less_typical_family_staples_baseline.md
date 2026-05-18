# 1Less Typical Family Staples Baseline

Date: 2026-05-18

Purpose: give the Chapter 1 dinner demo a conservative fallback before a parent shares actual fridge/pantry contents.

## Research inputs

- Food Network pantry/fridge/freezer essentials checklist: emphasizes grains/pasta, tortillas, oats/cereal, canned beans/tomatoes/salsa, eggs/dairy, sturdy produce, frozen vegetables, freezer proteins, and kid/family-friendly basics.
- USDA/FNS MyPlate parent materials: reinforces balanced family meals built from grains, fruits/vegetables, dairy, and protein groups.
- Product judgment: avoid niche, expensive, spicy, or allergy-risky assumptions as defaults. Peanut butter is common, but not used as a dinner baseline because allergy risk is too high.

## Conservative default baseline

Before a user shares actual inventory, 1Less may assume *common staples*, not verified inventory:

- Pantry/counter: rice, pasta, marinara/jar sauce, beans/black beans, tortillas, bread, crackers, potatoes, oats, cereal.
- Fridge: eggs, cheese, milk, yogurt, carrots, fruit/apples/bananas, salad/salad kit.
- Freezer: frozen peas, frozen vegetables, corn, nuggets, chicken, ground turkey.

## Logic rules

1. User-stated ingredients always outrank this baseline.
2. Avoidances/allergies block baseline ingredients and matching meals.
3. Sparse prompts must be transparent: copy should say this is an assumption based on common staples.
4. The baseline should improve odds for typical families, not pretend to know the kitchen.
5. Public prompt chips and sparse random prompts are regression fixtures.

## Expected sparse-prompt behavior

- “What should I make for dinner tonight?” → pasta marinara style answer.
- “Use what we have, picky kid, 10 minutes.” → egg/cheese/tortilla style answer.
- “Nothing thawed, pantry/freezer only.” → rice/egg/frozen-peas or similar pantry/freezer answer.
- “Dairy-free” sparse prompts must not mention cheese, milk, or yogurt.
