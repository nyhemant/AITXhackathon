# 1Less Local Validation Guide

Use this guide to validate the current 1Less dinner-decision flow locally.

This is no longer the product's public story; it is a development and smoke-test guide for the local Python implementation.

Requirements: Python >=3.10.

## 1. Run Tests

Before validation, reset mutable local meal memory:

```bash
git restore data/meal_history.json
```

Then run:

```bash
python3 -m unittest discover -s tests
```

Expected result: `OK`.

## 2. Run the Local Web App

```bash
python3 -m busyparent_agent.web --host 0.0.0.0 --port 8000
```

Origin scrape/bot limits are on by default (see `docs/rate-limit.md`). A normal family browse will not notice them. To disable locally: `--no-rate-limit` or `ONELESS_RATE_LIMIT=0`.

Browse locally to:

```text
http://127.0.0.1:8000
```

`0.0.0.0` is the bind address for the server. Use `127.0.0.1` in the browser.

If port `8000` is busy:

```bash
python3 -m busyparent_agent.web --host 0.0.0.0 --port 8001
```

Then browse to:

```text
http://127.0.0.1:8001
```

Restart the web server before validating UI copy or behavior so it serves the latest code.

## 3. Dinner Decision Smoke Tests

### Close-to-dinner pantry-first path

```bash
python3 -m busyparent_agent.app --scenario dinner --trace
```

Expected cues:

- `[decision] pantry-first because it is close to dinner`
- one dinner recommendation first
- `Reviewable grocery list: nothing required.`
- fallback behavior is available if the parent rejects the first idea

### Earlier-day light grocery path

```bash
python3 -m busyparent_agent.app --scenario lunch --trace
```

Expected cues:

- `[decision] grocery delivery can help because planning starts earlier`
- any cart/list is reviewable only
- required-for-tonight items are separated from nice-to-have add-ons
- no real checkout, live pricing, account access, scraping, taxes, fees, or order placement

### Guest / allergy-avoidance path

```bash
python3 -m busyparent_agent.app --scenario guest --trace
```

Expected cues:

- Starts from the parent's guest-child constraint
- Avoids flagged nut/spicy ingredients
- Includes the serious-allergy caveat
- Does not guarantee allergy safety

## 4. Manual Web Checks

In the web app, smoke-test:

1. no constraints
2. low-energy / 15-minute dinner
3. nut-free or ingredient avoidance
4. picky-kid friendly
5. missing ingredient / fallback
6. copy check: 1Less is not framed as dinner-only forever
7. copy check: no allergy guarantee, medical claim, or nutrition promise

## 5. Fixture and Adapter Notes

The local implementation still contains deterministic fixtures and mocked adapters from the original prototype. Treat those as implementation scaffolding, not product positioning.

- `data/photo_scan_results.json` contains deterministic scan outputs.
- Mocked grocery catalog data is representative fixture data only.
- No real grocery API, account, checkout, scraping, or order placement is included.
- Local meal memory in `data/meal_history.json` can mutate during tests and demos; reset it before validation.

A future production version can replace fixtures with real adapters while preserving the product boundary: one practical dinner decision, low setup burden, and no false precision.
