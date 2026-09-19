# 1Less Recipe Quality Tiers

Date: 2026-05-18

## Goal

Keep the 40-template catalog practical without making every template equally likely for a vague dinner prompt.

The catalog contains real parent-life meals, but some are full dinner defaults while others are emergency saves, breakfast-for-dinner, snack plates, or household-specific ideas. Ranking should reflect that.

## Tiers

- `core_dinner`: reasonable first answers for broad prompts like “What should I make for dinner tonight?”
- `quick_backup`: practical fallback dinners when the parent signals low energy, low cleanup, picky kids, freezer/pantry constraints, or short time.
- `snack_plate`: valid emergency meals only when the parent asks for snack/plate/grazing/no-cook style help or names matching ingredients.
- `breakfast_for_dinner`: valid when breakfast/no-cook ingredients are named or the prompt explicitly supports that mode.
- `niche_household`: useful only with explicit ingredient support; not assumed as a generic household default.

## Ranking rule

Sparse/common-staples prompts may still rotate for variety, but rotation now stays inside quality-appropriate choices. It should not casually rotate from pasta into yogurt bowls, cream-cheese cucumber wraps, parotta, salmon, or tuna unless the user gives relevant context.

## Examples

- “What should I make for dinner tonight?” → rotates among core dinners only.
- “Tuna pasta peas 15 minutes” → Tuna Pasta Plates, stable because the ingredients are explicit.
- “No cooking, kids starving, just need a snack plate dinner” → Snack Plate Dinner.
- “Yogurt oats fruit no cooking” → Yogurt Oat Fruit Bowls.

## Why this matters

This keeps the product honest: more variety without feeling like random ingredient assembly.
