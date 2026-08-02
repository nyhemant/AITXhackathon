# Archive snapshot — before major rearchitecture

**Date:** 2026-08-02  
**Git tag:** `snapshot/pre-rearch-2026-08-02`  
**Branch:** `archive/pre-rearch-babys-day-out-2026-08-02`  
**Remote:** `origin` → `nyhemant/AITXhackathon` (push when auth works)

## What this freezes

- 1Less two-thread product: **Baby's Day Out** (`/field-pack/`) + **Dinner** (`/`)
- Static Field Pack site: map, city/venue dropdowns, Dallas ready packs, place pages
- Brand rename from Arya's Field Pack → Baby's Day Out
- Thread order: Baby's Day Out first, Dinner second
- Start-outing absolute URLs under `/field-pack/`
- HANDOFF + AGENTS for continuity

## Why

Baseline before hook/retention-focused reengineering (tourist parent acquisition, ready-now strip, thinner national shell). Restore anytime:

```bash
git fetch origin
git checkout snapshot/pre-rearch-2026-08-02
# or
git checkout archive/pre-rearch-babys-day-out-2026-08-02
```

## Sister repo (optional)

`~/Projects/arya-zoo-field-pack` — earlier pack experiments; not required for 1Less serve path.
