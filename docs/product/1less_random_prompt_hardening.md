# 1Less Random Prompt Hardening

Date: 2026-05-18

## Problem

The public prompt chips exposed symptoms of weak decision logic: the system could over-index on generic “low effort” and ignore important user facts. A real user will be messier than a chip: “no sauce,” “kids hate beans,” “chicken nuggets but no tortillas,” “leftover rice/chicken/carrots,” etc.

## New hardening rules

1. Positive ingredients are not enough; parse ruled-out ingredients too.
2. “No X,” “without X,” “don’t have X,” “out of X,” and “kids hate/won’t eat X” should block X from the chosen meal and visible copy.
3. Missing non-allergy items should not trigger the allergy safety caveat.
4. User-stated positives still outrank typical-family assumptions.
5. Raw/unclear chicken should not silently become a cooked-leftover chicken bowl.
6. Public chips plus messy random prompts are regression fixtures.

## Added meal coverage

- Cheese Quesadillas with fruit: covers tortillas + cheese, especially when eggs are ruled out.
- Cheesy Pasta with carrots: covers pasta + cheese when sauce is missing.
- Chicken Rice Veggie Bowls: covers leftover/cooked chicken + rice + vegetables.
- Chicken Nugget Plates: covers nuggets when tortillas/wraps are unavailable.

## Synthetic prompt gauntlet examples

- “I have pasta and cheese but no sauce.” → Cheesy Pasta with carrots; no sauce/marinara leak.
- “Only tortillas and cheese, no eggs.” → Cheese Quesadillas with fruit; no egg leak.
- “I have chicken nuggets but no tortillas.” → Chicken Nugget Plates; no tortilla leak or allergy caveat.
- “Low cleanup, no rice, no pasta.” → Crispy Chicken Wraps with salad; no rice/pasta leak.
- “Use leftovers: rice, chicken, carrots. 15 min.” → Chicken Rice Veggie Bowls.
- “Can cook 40 minutes, chicken in fridge, kids picky.” → Sheet-pan chicken and corn rice bowls.

## Validation

The regression suite now includes a random-prompt gauntlet and missing-item/non-allergy tests.
