# BusyParent Kitchen Agent / HomePlate AI

Local Python agent demo for the **AITX Community x Codex Hackathon, Agents Track**.

Busy parents do not need another recipe app. They need dinner handled. This demo proves an agent loop: understand the dinner goal, call local tools, make a time-aware decision, adapt after feedback, and revise for a guest child constraint.

## Why It Fits The Agents Track

This is a small, deterministic agent demo rather than a web app. The visible trace shows:

- `[tool]` calls into mocked family, inventory, Instacart-like order history, meal, delivery-window, and grocery-list tools
- `[inventory]` lines that explain confidence from visible snapshots, recent orders, and bulk purchases
- `[memory]` scoring lines from local household meal history
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

Run the local web chat:

```bash
python3 -m busyparent_agent.web
```

Then open:

```text
http://127.0.0.1:8000
```

## Demo Commands

Short mentor/judge scenarios:

```bash
python3 -m busyparent_agent.app --scenario dinner --trace
python3 -m busyparent_agent.app --scenario lunch --trace
python3 -m busyparent_agent.app --scenario guest --trace
```

Close-to-dinner branch: pantry-first, nothing required.

```bash
python3 -m busyparent_agent.app --demo --trace --now "2026-05-08 17:30"
```

Lunchtime branch: delivery-aware, small reviewable cart/list.

```bash
python3 -m busyparent_agent.app --demo --trace --now "2026-05-09 12:30"
```

Interactive local chat:

```bash
python3 -m busyparent_agent.app
```

Local web chat for UX testing:

```bash
python3 -m busyparent_agent.web
```

## What Judges Should Notice

In the close-to-dinner demo, the agent says it is close to dinner and chooses a pantry-first meal using high-confidence inventory.

In the lunchtime demo, the agent says planning starts early enough to use a small mock Instacart delivery, then recommends dinner with a reviewable cart/list such as `avocado, berries`. It never places an automatic order.

The mock cart is backed by `data/mock_grocery_catalog.json`, a local grocery universe with representative demo prices, stock status, categories, sizes, brands, tags, and substitutes. The agent only adds catalog-backed, in-stock items or available substitutes to a mock cart.

The Inventory Confidence Engine reconciles `fridge_snapshot.json`, `pantry_snapshot.json`, mock Instacart orders, mock Costco bulk purchases, household usage patterns, and meal history. For example, visible eggs become high-confidence, avocado ordered a few days ago becomes medium-confidence, and older kid snack berries become likely low.

The agent also reads sample household memory from `data/meal_history.json`. Favorites, kid-approved meals, and popular meals get boosted, while meals served, recommended, or rejected recently are penalized so the agent avoids repeating yesterday's dinner when a strong pantry alternative exists.

Parents can update that local memory conversationally in CLI or web chat. Messages like `Egg fried rice was a hit`, `The kids loved this`, `We had quesadillas yesterday`, or `Don't suggest quesadillas again this week` append simple events to `data/meal_history.json` and affect later recommendations.

After the parent rejects the first recommendation, the agent returns three alternatives and gives a clear next pick. The scripted demo then chooses a valid current alternative.

When a guest child has no-nuts/no-spicy constraints, the agent revises the selected meal, avoids the named ingredients, keeps heat off the shared meal, and reminds the parent to verify packaged labels.

## Mocked vs. Real Integrations

Mocked today:

- `data/family_profile.json`
- `data/inventory_snapshot.json`
- `data/grocery_history.json`
- `data/meal_options.json`
- `data/meal_history.json`
- `data/fridge_snapshot.json`
- `data/pantry_snapshot.json`
- `data/instacart_orders.json`
- `data/mock_grocery_catalog.json`
- `data/costco_bulk_purchases.json`
- `src/busyparent_agent/adapters/mock_instacart.py`
- Delivery timing logic
- Inventory confidence scoring from local fixtures
- Mock grocery catalog search, availability, substitutions, and demo pricing
- Household memory and recency-aware recommendation scoring
- Conversational feedback capture into local JSON memory
- Reviewable grocery cart/list updates

Real later:

- Real grocery provider availability and cart APIs
- Real prices, taxes, fees, promotions, and substitution rules
- Receipt, pantry, or fridge scanning
- Photo recognition for fridge/pantry snapshots
- Calendar-aware dinner timing
- User preference memory learned from accept, reject, recommended, and served events
- LLM reasoning over a larger meal library

No real grocery APIs, purchases, auth, web scraping, Telegram bot, or photo recognition are included in this version.

The local web chat is only a demo shell around the agent. It does not add auth, persistence, deployment, or external integrations.

## Interface Architecture

`src/busyparent_agent/service.py` is the channel-neutral adapter used by the CLI and web chat. It returns structured response dictionaries with:

- visible message text
- `[tool]` and `[decision]` trace lines
- reviewable grocery items
- scenario/state metadata

The future Telegram adapter should call this same service instead of duplicating agent logic. Agent response text should stay channel-neutral so the same content can work in CLI, web chat, and Telegram.

## Project Structure

```text
src/busyparent_agent/
  adapters/   mock external-service adapters
  app.py      CLI entry point
  agent.py    deterministic agent loop and response policy
  inventory.py Inventory Confidence Engine
  service.py  channel-neutral response service
  tools.py    local mocked tools
  web.py      stdlib local web chat adapter
data/         mocked JSON inputs
tests/        unittest coverage for agent behavior
docs/demo.md  judge-facing demo script
```

## Allergy Wording

The demo can help avoid named ingredients such as nuts or spicy foods, but it is not an allergy safety guarantee. Allergy-sensitive families must verify packaged labels before serving.
