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
- `[decision] pantry-first because it is close to dinner`
- One meal first: `Black Bean Quesadillas`
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
- The agent does not force pantry-only
- `Reviewable grocery list: avocado, berries.`
- This is still a reviewable list, not an automatic order

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
Agent: Make Black Bean Quesadillas tonight.

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
