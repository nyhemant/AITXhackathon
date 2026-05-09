# Demo Script

Use this for a short judge walkthrough. The demo is local Python only.

## 1. Run Tests

```bash
python3 -m unittest discover -s tests
```

Expected result: `OK`.

## 2. Local Web Chat

```bash
python3 -m busyparent_agent.web
```

Open:

```text
http://127.0.0.1:8000
```

Use this when you want a mentor or judge to test the UX without typing in a terminal. The web UI is a demo shell around the same agent service used by the CLI.

## 3. Close-To-Dinner Branch

Short version:

```bash
python3 -m busyparent_agent.app --scenario dinner --trace
```

Full scripted version:

```bash
python3 -m busyparent_agent.app --demo --trace --now "2026-05-08 17:30"
```

Call out:

- `[tool] check_delivery_window`
- `[inventory]` confidence lines show what is visible, recently ordered, or likely low
- `[decision] pantry-first because it is close to dinner`
- `[memory]` scoring lines boost household favorites and penalize recent repeats
- One meal first: `Egg Fried Rice`
- `Reviewable grocery list: nothing required.`
- Rejection produces three alternatives
- Guest child constraint revises the selected meal

## 4. Lunchtime Branch

Short version:

```bash
python3 -m busyparent_agent.app --scenario lunch --trace
```

Full scripted version:

```bash
python3 -m busyparent_agent.app --demo --trace --now "2026-05-09 12:30"
```

Call out:

- `[decision] grocery delivery can help because planning starts earlier`
- `[tool] mock_instacart.get_recent_orders`
- `[tool] mock_instacart.build_reviewable_cart`
- `[memory]` scoring still runs before the recommendation
- The agent does not force pantry-only
- `Reviewable cart/list: avocado, berries.`
- This is still a reviewable mock cart/list, not an automatic order

## Inventory Confidence

The demo uses local fixtures for visible food snapshots, mock Instacart orders, and mock Costco bulk purchases. The Inventory Confidence Engine ranks items as high-confidence, medium-confidence, low-confidence, likely low, or needing a parent check.

Late-day planning prefers high-confidence items. Lunch planning can use the mock Instacart adapter to build a reviewable cart for fresh add-ons like avocado and berries. A real version could replace the fixtures with provider APIs and photo recognition for fridge or pantry snapshots.

## Mock Grocery Catalog

`data/mock_grocery_catalog.json` is the local shopping universe for the demo. It includes representative prices, brands, sizes, stock status, tags, and substitutes for common household items. The adapter can search this catalog, check availability, substitute an out-of-stock item, and build a priced reviewable cart.

The prices are fixture prices for demo realism only. No real Instacart API, live pricing, account, checkout, scraping, taxes, fees, or order placement is included.

## Household Memory

The demo uses local sample memory in `data/meal_history.json` with `served`, `accepted`, `rejected`, and `recommended` events. The recommendation score boosts family favorites, kid-approved meals, and popular meals, then penalizes meals served or recommended in the last 1-2 days and meals rejected recently.

The same memory file can be updated through natural chat feedback. Try `The kids loved this`, `Egg fried rice was a hit`, `We had quesadillas yesterday`, or `Don't suggest quesadillas again this week`; the agent saves an event and confirms it conversationally.

A real version could learn this history from parent accept/reject clicks, completed dinner plans, and repeated household behavior. This demo keeps that memory deterministic and local so judge scenarios remain reliable.

## 5. Guest Constraint Branch

```bash
python3 -m busyparent_agent.app --scenario guest --trace
```

Call out:

- Starts from selected context: `Egg Fried Rice`
- Parent adds a guest child constraint
- `[tool] apply_guest_constraints`
- Avoids nuts and keeps spicy food off the shared meal
- Reminds parent to verify packaged labels

## Future Telegram Adapter

CLI and web both call `busyparent_agent.service.AgentSession`. A future Telegram bot should call that same service from a Telegram-specific adapter and send the returned `message` text plus optional trace/debug metadata. The Telegram layer should not reimplement dinner rules, allergy wording, grocery-list logic, or scenario handling.

## Sample Transcript Cues

```text
Parent: What should I make for dinner tonight?
[decision] pantry-first because it is close to dinner
Agent: Make Egg Fried Rice tonight.

Parent: Not feeling that. Anything else?
Agent: Totally. Here are three better directions:

Parent: Let's do Egg Fried Rice.
Agent: Timing: 5 minutes prep, 12-15 minutes cook.

Parent: My daughter has a friend coming over. No nuts, no spicy food.
Agent: Avoid nut ingredients...
Agent: ...verify packaged labels. This demo is not an allergy safety guarantee.
```

## One-Sentence Pitch

HomePlate AI is an agent that decides what dinner should be, explains the time-aware tradeoff, and adapts when a real parent changes the constraints.
