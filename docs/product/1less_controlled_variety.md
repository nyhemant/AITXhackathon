# 1Less Controlled Variety

Date: 2026-05-18

## Goal

Avoid the same safe default appearing over and over for vague prompts, without making the product feel random or flaky.

## Rules

1. Hard constraints still win first: allergies, avoidances, missing ingredients, explicit ingredients, time, effort.
2. Explicit ingredient prompts stay stable inside the same session. Example: “Tuna pasta peas 15 minutes” should keep returning Tuna Pasta Plates.
3. Sparse/common-staples prompts may rotate only within near-ties.
4. Rotation is same-session only and uses recent recommendation history.
5. Stateless preview remains stable: a new preview session for the same prompt returns the same first answer.
6. Niche/low-baseline templates are not used merely for variety; they need explicit ingredient support.

## Current behavior

Repeated sparse prompt:

- “What should I make for dinner tonight?”
  - first: Pasta Marinara with carrots
  - follow-ups in same session can move to another close-fit option instead of repeating pasta immediately.

Explicit prompt:

- “Tuna pasta peas 15 minutes”
  - remains Tuna Pasta Plates even if repeated.

## Why not pure randomness

Blind randomness makes identical prompts produce unexplained changes. Controlled variety preserves trust: the system is deterministic when facts are specific and only varies when the user is asking a broad/vague question where multiple options are legitimately close.
