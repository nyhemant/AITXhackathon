# 1Less Product Reference

Status: active standalone product reference  
Last updated: 2026-05-19

## Canonical Product Identity

- Product: **1Less**
- Primary domain: <https://1less.app>
- Company promise: **One less decision for busy parents.**
- Chapter 1 promise: **Tonight's dinner, decided.**

1Less is a standalone parent decision-relief product. Historical prototype/submission material is retained only as archive context.

## Current Chapter

Chapter 1 is dinner decision relief.

The product should help a tired parent answer:

> What should we actually do for dinner tonight?

The answer should be one practical, good-enough decision — not a recipe feed, weekly plan, grocery optimization system, nutrition program, or family operating system.

## Current Public URLs

- Primary: <https://1less.app>
- WWW: <https://www.1less.app>
- Temporary backup alias: <https://aitx.myglucoach.app>

The backup alias exists for continuity only. New product references should use `1less.app`.

## Repo / Implementation Note

The active GitHub repo currently remains:

- <https://github.com/nyhemant/AITXhackathon>

The active local working copy currently remains:

- `/Users/arku/Projects/AITXhackathon`

Those names are historical implementation details. Product documentation, roadmap language, and public-facing copy should refer to **1Less**, not AITX, BusyMom, BusyParent, or HomePlate.

The internal Python package currently remains `busyparent_agent` to avoid a risky mechanical refactor while product direction is changing.

## Legacy Baseline

The current launch build was frozen before the next overhaul:

- Branch: `legacy/model-1.1`
- Tag: `legacy-model-1.1`
- Freeze note: `docs/legacy/model-1.1.md`

Use this as the rollback/reference point while `main` moves forward.

## Product Boundaries

1Less should avoid claiming or implying:

- allergy safety guarantees
- medical/nutrition optimization
- precise pantry knowledge without user-provided current-turn input
- grocery fulfillment or checkout
- budget optimization
- child-feeding guarantees
- family surveillance or productivity tracking

## Current Documentation Map

- `README.md` — top-level standalone product overview and local run instructions
- `docs/product-reference.md` — canonical current product/reference note
- `docs/demo.md` — local validation guide
- `docs/product/` — product research, briefs, and task packets
- `docs/legacy/model-1.1.md` — frozen legacy model 1.1 reference
- `docs/archive/` — historical prototype and deprecated concept docs retained for history only
