# BusyParent Kitchen Agent / HomePlate AI

This is a local Python agent demo for the AITX Community x Codex Hackathon, Agents Track.

Busy parents do not need another recipe app. They need dinner handled. This demo leads with one practical dinner recommendation, then adapts when the parent rejects it or adds guest constraints.

## What It Does

The agent uses mocked local JSON data to answer:

- What family are we feeding?
- What food is likely at home?
- Is there enough time for groceries, or should dinner be pantry-first?
- What is the one best dinner recommendation right now?
- What should change if the parent rejects it?
- What should change if a guest child needs no nuts and no spicy food?

The demo is intentionally small and deterministic so it is reliable live.

## Run It

From the project root:

```bash
cd /Users/arku/Projects/AITXhackathon
python -m busyparent_agent.app
```

On Macs where `python` is not installed, use `python3`:

```bash
python3 -m busyparent_agent.app
```

Run the scripted hackathon conversation:

```bash
python -m busyparent_agent.app --demo
python3 -m busyparent_agent.app --demo
```

Show tool calls and decisions:

```bash
python -m busyparent_agent.app --demo --trace
python3 -m busyparent_agent.app --demo --trace
```

Test a specific time:

```bash
python -m busyparent_agent.app --demo --now "2026-05-08 13:00"
python -m busyparent_agent.app --demo --now "2026-05-08 17:30"
python3 -m busyparent_agent.app --demo --now "2026-05-08 13:00"
python3 -m busyparent_agent.app --demo --now "2026-05-08 17:30"
```

Lunchtime planning demo, with trace:

```bash
python3 -m busyparent_agent.app --demo --trace --now "2026-05-09 12:30"
```

At lunchtime, the trace should show that grocery delivery can still help. Near dinner, the trace should switch to pantry-first.

## Demo Conversation

```text
Parent: What should I make for dinner tonight?
Parent: Not feeling that. Anything else?
Parent: Let's do egg fried rice.
Parent: My daughter has a friend coming over. No nuts, no spicy food.
```

## Run Tests

```bash
python -m unittest discover -s tests
python3 -m unittest discover -s tests
```

## Mocked vs. Real

Mocked today:

- Family profile
- Fridge, freezer, and pantry snapshot
- Grocery history
- Meal options
- Grocery list updates
- Delivery window logic

Real later:

- Fridge or receipt scanning
- Grocery provider availability
- User preference memory
- Calendar-aware dinner timing
- LLM reasoning over a larger meal library

## Why This Is Agentic

This is not a static recipe picker. It follows an agent loop:

1. Understand the parent goal.
2. Use tools and local data.
3. Make one decision.
4. Listen to feedback.
5. Adapt the plan.
6. Produce a reviewable grocery list, not an auto-buy order.

The important behavior is adaptation. The first answer is one meal. A rejection produces three alternatives. A guest constraint revises the selected dinner with careful allergy wording.

## Allergy Wording

The demo can help avoid named ingredients such as nuts or spicy foods, but it is not an allergy safety guarantee. Allergy-sensitive families must verify packaged labels before serving.
