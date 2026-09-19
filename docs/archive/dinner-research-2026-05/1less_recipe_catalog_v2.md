# 1Less Recipe Catalog v2

Date: 2026-05-18

## Change

Expanded the Chapter 1 dinner decision catalog from 15 to 40 bounded dinner templates.

## Why

A 15-template catalog was enough to prove the logic, but repeated sparse prompts would over-select a few defaults. The next alpha-safe step is to widen the catalog with simple family-realistic templates while keeping the decision rules constraint-first.

## Added coverage areas

- Pasta/noodle variants: buttered pea noodles, pasta bean marinara, tuna pasta, pasta pea cheese bowls.
- Tortilla/quesadilla variants: tortilla pizza, turkey/chicken quesadilla plates, corn bean quesadillas, paneer tortilla melts.
- Low-cook kid plates: snack plate dinner, grilled cheese, chicken nugget plates, yogurt oat fruit bowls.
- Rice/bowl variants: turkey rice taco bowls, chicken rice veggie bowls, edamame rice bowls, salmon rice pea plates.
- Potato/egg/freezer variants: potato egg hash, sweet potato bean bowls, potato cheese skillet, parotta egg roll-ups.

## Guardrails

- User-stated ingredients still outrank the typical-family baseline.
- Exclusions like “no sauce,” “no tortillas,” or “kids hate beans” block those items.
- Allergy/avoidance caveats remain separate from ordinary missing-item constraints.
- New templates intentionally use bounded, common ingredients; they are templates, not complex recipe search results.

## Remaining recommendation

Catalog size is now demo-credible. The next quality layer should be controlled variety, not pure randomness: choose the highest-scoring valid meal unless the top few are close, then rotate within near-ties and avoid same-session repeats.
