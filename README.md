# 1Less

1Less is a standalone parent decision-relief product.

Company promise: **One less decision for busy parents.**

Chapter 1 promise: **Tonight's dinner, decided.**

The current product starts with a narrow dinner decision flow. A parent gives only the context needed for tonight: time, energy, simple constraints, optional ingredients, and anything to avoid. 1Less returns one practical dinner recommendation, not a recipe browser, weekly planner, nutrition tracker, or family command center.

## Current Product Surface

The local web app supports:

- Quick prompts for 10 / 20 / 30 minute dinners
- Energy levels: barely cooking, normal, can cook
- Lightweight constraints such as picky-kid friendly, vegetarian, nut-free, dairy-free, leftovers, and pantry/freezer basics
- Optional free text for what the parent has tonight or wants to avoid
- One recommendation with meal name, why it fits, time/effort, simple steps, and one fallback/tweak
- Feedback actions: Good enough, Too much work, Kid won't eat, Missing ingredient, Give me backup

If allergy or avoidance input is present, the recommendation shows:

> 1Less can help avoid ingredients you flag, but it cannot guarantee allergy safety. Always check labels and use your judgment for serious allergies.

## Boundaries

This MVP does not claim allergy safety, nutrition optimization, medical diet support, budget optimization, cultural or religious dietary correctness, pantry accuracy, or grocery fulfillment.

It does not ask for child names, medical conditions, precise location, detailed health or nutrition goals, school schedules, pantry/fridge photos, or grocery purchase history.

## Standalone Product Status

Treat this repository as the active standalone 1Less product workspace going forward.

Two implementation details remain for continuity and low-risk iteration:

- The GitHub repository is still `nyhemant/AITXhackathon` until a future repo rename/migration.
- The Python package is still `busyparent_agent` until a future refactor.

Do not use either name as product branding in new documentation, product copy, outreach, or roadmap work.

Legacy model 1.1 is frozen for rollback/reference at:

- Branch: `legacy/model-1.1`
- Tag: `legacy-model-1.1`
- Notes: `docs/legacy/model-1.1.md`

## Quick Start

Requirements:

- Python >=3.10

From the repo root:

```bash
python3 -m unittest discover -s tests
```

Local QA (MacBook — same server as 1less.app, not live):

```bash
./scripts/dev-serve.sh
```

Then browse `http://127.0.0.1:8000/field-pack/`. Edit, refresh. When a chunk is good: `git push`. On the Mini (live): `./scripts/sync-from-github.sh` once, or leave it manual.

Same server, any host/port:

```bash
python3 -m busyparent_agent.web --host 0.0.0.0 --port 8000
```

Then browse locally to:

```text
http://127.0.0.1:8000
```

If port `8000` is busy:

```bash
python3 -m busyparent_agent.web --host 0.0.0.0 --port 8001
```

Then browse to:

```text
http://127.0.0.1:8001
```

Public origin rate limits (no accounts, no email, no CAPTCHA) live in
`busyparent_agent.rate_limit` and hook `web.py`. Defaults, tune env, disable
switch, and a burst-test command: `docs/rate-limit.md`. Emergency off:

```bash
ONELESS_RATE_LIMIT=0 python3 -m busyparent_agent.web --host 127.0.0.1 --port 8000
# or
python3 -m busyparent_agent.web --no-rate-limit
```

## Documentation

- Current product reference: `docs/product-reference.md`
- Origin scrape/bot rate limits: `docs/rate-limit.md`
- Local validation guide: `docs/demo.md`
- Product research and planning: `docs/product/`
- Legacy model 1.1 freeze: `docs/legacy/model-1.1.md`
- Archived historical prototype docs: `docs/archive/`

## Project Structure

```text
src/busyparent_agent/
  app.py      legacy CLI entry point
  service.py  channel-neutral service helpers and Chapter 1 dinner MVP session
  web.py      stdlib local web chat adapter
  rate_limit.py  per-IP scrape/bot limits (429 + Retry-After)
  agent.py    older deterministic dinner internals
  tools.py    older local mocked tools
tests/        unittest coverage
docs/product/ source-of-truth product research, briefs, and planning
docs/archive/ historical prototype and deprecated concept material
```
