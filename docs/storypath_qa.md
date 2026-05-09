# StoryPath v2 QA

## Golden Demo Flow

Theme: BusyParent reduces evening decision load.

1. Dinner handled:
   - Open the v2 local web app.
   - Use the `Dinner` tab.
   - Click `Dinner now`.
   - Show the agent leading with one practical dinner default.
2. Bedtime book handled:
   - Switch to the `Bedtime Book` tab.
   - Click `Pick tonight's book`.
   - Show the agent leading with one book, parent prompts, and a tiny tomorrow activity.

CLI equivalents:

```bash
python3 -m busyparent_agent.app --scenario dinner --trace
python3 -m busyparent_agent.app --scenario book --trace
```

## v2 Local Run Command

Keep v1 pinned separately on port `8000`. Run v2 StoryPath locally on port `8001`:

```bash
python3 -m busyparent_agent.web --host 127.0.0.1 --port 8001
```

Browse locally to:

```text
http://127.0.0.1:8001
```

## Expected Dinner Tab Result

Expected primary result:

```text
Make Egg Fried Rice tonight.
```

Expected supporting points:

- Pantry-first because it is close to dinner.
- Photo evidence confirms core staples.
- Reviewable grocery list says nothing required.
- No StoryPath or mocked Epic-style catalog copy appears in the dinner response.

Relevant trace lines:

```text
[decision] pantry-first because it is close to dinner
[tool] recommend_meal -> Egg Fried Rice, one meal returned, pantry-first
```

## Expected Bedtime Book Tab Result

Expected primary result:

```text
Tonight's pick: The Very Hungry Caterpillar by Eric Carle.
```

Expected supporting points:

- Explains why it fits Kunal tonight.
- Read time is about 5 minutes.
- Format/source says mocked Epic-style catalog.
- Includes exactly 3 parent prompts.
- Includes a tiny tomorrow activity.
- Includes a clear note that there is no real Epic login, API, scraping, or checkout.

Relevant trace lines:

```text
[book] mock_epic.get_catalog_books -> 35 books
[book] filter age/mood/time/availability
[memory] recent reading history checked
[decision] chose The Very Hungry Caterpillar because it fits Kunal's calm bedtime mode, stays within 10 minutes, and is available in the demo catalog
```

## Mocked-vs-Real Limitations

- StoryPath uses `data/mock_epic_book_catalog.json` as a deterministic mocked Epic-style book catalog.
- `data/reading_history.json` is local sample memory only.
- There is no real Epic login.
- There is no real Epic API.
- There is no scraping.
- There is no book checkout, borrowing, purchase, or account access.
- Book availability means available in the local demo fixture only.
- Parent prompts are conversation aids, not educational or developmental assessment.

## Risks and Blockers

### P0 Must Fix

None found.

### P1 Should Fix Before Demo

None found.

### P2 Nice-To-Have

- Add a visible CLI/web scenario for Arya or siblings together if there is time.
- Make the Bedtime Book tab allow choosing child and mode instead of using the default Kunal calm-bedtime scenario.
- Consider renaming the app header to `BusyParent / HomePlate AI` if the pitch moves beyond kitchen-only branding.
- Add a short v2 section to `docs/submission.md` only if v2 becomes part of the final submitted demo.

## Verification Performed

Commands run:

```bash
git status --short
python3 -m unittest discover -s tests
python3 -m busyparent_agent.app --scenario dinner --trace
python3 -m busyparent_agent.app --scenario book --trace
```

Result:

- Working tree was clean before creating this QA note.
- Test suite passed: 69 tests.
- Dinner CLI scenario returned the expected pantry-first Egg Fried Rice flow.
- Book CLI scenario returned the expected mocked Epic-style StoryPath flow.
- README, `docs/demo.md`, and web UI copy clearly communicate the v2 decision-load story and port `8001` run command.
