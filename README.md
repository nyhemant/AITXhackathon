# 1Less

1Less is a parent decision-relief demo.

Company promise: **One less decision for busy parents.**

Chapter 1 promise: **Tonight's dinner, decided.**

This implementation starts with a narrow dinner decision flow. A parent gives only the context needed for tonight: time, energy, simple constraints, optional ingredients, and anything to avoid. 1Less returns one practical dinner recommendation, not a recipe browser or weekly planning system.

## Chapter 1 Flow

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

The existing repository still contains older deterministic demo internals and Story Picker code from prior hackathon work. This Chapter 1 pass keeps that code intact where possible, but the public dinner web flow is the active 1Less MVP surface.

## Quick Start

Requirements:

- Python >=3.10

From the repo root:

```bash
python3 -m unittest discover -s tests
```

Run the local web chat:

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

## Project Structure

```text
src/busyparent_agent/
  app.py      legacy CLI entry point
  service.py  channel-neutral service helpers and Chapter 1 dinner MVP session
  web.py      stdlib local web chat adapter
  agent.py    older deterministic dinner demo internals
  tools.py    older local mocked tools
tests/        unittest coverage
docs/product/ source-of-truth product brief and task packet
```
