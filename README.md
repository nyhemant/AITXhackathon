# BusyParent Kitchen Agent / HomePlate AI

Local Python agent demo for the **AITX Community x Codex Hackathon, Agents Track**.

Busy parents do not need another recipe app. They need dinner handled. This demo proves an agent loop: understand the dinner goal, call local tools, make a time-aware decision, adapt after feedback, and revise for a guest child constraint.

## Why It Fits The Agents Track

This is a small, deterministic agent demo rather than a web app. The visible trace shows:

- `[tool]` calls into mocked family, inventory, grocery history, meal, delivery-window, and grocery-list tools
- `[decision]` lines explaining why the agent chooses pantry-first or delivery-aware planning
- One meal recommendation first, not a recipe list
- Adaptation after rejection
- Guest child handling for no nuts and no spicy food, with careful allergy wording

## Quick Start

From the project root:

```bash
cd /Users/arku/Projects/AITXhackathon
python3 -m busyparent_agent.app --demo --trace
```

Run tests:

```bash
python3 -m unittest discover -s tests
```

## Demo Commands

Close-to-dinner branch: pantry-first, nothing required.

```bash
python3 -m busyparent_agent.app --demo --trace --now "2026-05-08 17:30"
```

Lunchtime branch: delivery-aware, small reviewable grocery list.

```bash
python3 -m busyparent_agent.app --demo --trace --now "2026-05-09 12:30"
```

Interactive local chat:

```bash
python3 -m busyparent_agent.app
```

## What Judges Should Notice

In the close-to-dinner demo, the agent says it is close to dinner and chooses a pantry-first meal with no required grocery list.

In the lunchtime demo, the agent says planning starts early enough to use a small delivery, then recommends dinner with a reviewable grocery list such as `avocado, berries`.

After the parent rejects the first recommendation, the agent returns three alternatives and gives a clear next pick. The scripted demo then chooses a valid current alternative.

When a guest child has no-nuts/no-spicy constraints, the agent revises the selected meal, avoids the named ingredients, keeps heat off the shared meal, and reminds the parent to verify packaged labels.

## Mocked vs. Real Integrations

Mocked today:

- `data/family_profile.json`
- `data/inventory_snapshot.json`
- `data/grocery_history.json`
- `data/meal_options.json`
- Delivery timing logic
- Reviewable grocery list updates

Real later:

- Grocery provider availability
- Receipt, pantry, or fridge scanning
- Calendar-aware dinner timing
- User preference memory
- LLM reasoning over a larger meal library

No real grocery APIs, web UI, Telegram bot, or photo recognition are included in this version.

## Project Structure

```text
src/busyparent_agent/
  app.py      CLI entry point
  agent.py    deterministic agent loop and response policy
  tools.py    local mocked tools
data/         mocked JSON inputs
tests/        unittest coverage for agent behavior
docs/demo.md  judge-facing demo script
```

## Allergy Wording

The demo can help avoid named ingredients such as nuts or spicy foods, but it is not an allergy safety guarantee. Allergy-sensitive families must verify packaged labels before serving.
