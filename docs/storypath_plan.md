# Story Picker v2 Plan

Working name: Story Picker.

## 1. Product Framing

BusyParent Agent reduces parent evening decision load after work.

v1: Dinner Planner handles what to make for dinner, pantry fit, and grocery gaps.

v2: Story Picker handles what to read tonight, kid fit, bedtime mood, and mocked Epic-style availability.

The product theme stays the same: a parent should not have to make a dozen small evening decisions when they are already tired. Dinner and bedtime reading are naturally linked:

- "What should we make for dinner?"
- "What should I read with my kid tonight?"

The v2 extension should not pivot away from the dinner agent. It should add a second, clearly separated room that starts after dinner from Story Picker. The shared promise is still one practical recommendation first, not a menu of options.

Story Picker should answer:

- Which child are we reading with tonight?
- What mood or mode fits tonight?
- How much parent energy/time is available?
- What has the child read recently?
- Which available book is the best fit?
- What can the parent say or do with the book without extra planning?

## 2. Epic-Style Mock Catalog

Do not use Dallas Public Library, Libby, Hoopla, or Texas public data as core dependencies. Story Picker should use a deterministic mocked Epic-style kids book catalog, analogous to how v1 uses `data/mock_grocery_catalog.json` for Instacart-like grocery availability.

Proposed source of availability:

- `data/mock_epic_book_catalog.json`

This is the single source for book availability in the demo. No real Epic login, scraping, account access, or live catalog checks.

Proposed fields:

```json
{
  "books": [
    {
      "id": "jabari-jumps",
      "title": "Jabari Jumps",
      "author": "Gaia Cornwall",
      "age_min": 4,
      "age_max": 8,
      "reading_level": "early_read_aloud",
      "themes": ["bravery", "parent_support", "trying_again"],
      "mood_tags": ["bravery", "confidence", "calm bedtime"],
      "read_minutes": 7,
      "format": "read_aloud",
      "available": true,
      "series": null,
      "parent_prompts": [
        "What helped Jabari feel ready?",
        "When did you feel brave today?",
        "What would you say to a friend who was nervous?"
      ],
      "tiny_activity": "Draw one brave thing you might try tomorrow.",
      "similar_book_ids": ["after-the-fall", "the-most-magnificent-thing"]
    }
  ]
}
```

Allowed `format` values:

- `ebook`
- `read_aloud`
- `audiobook`
- `animated`

Catalog expectations:

- 30-60 curated children’s books is enough for a convincing v2 demo.
- Include a mix of preschool, early reader, sibling-friendly read-aloud, science/curiosity, confidence, silly, and short bedtime books.
- Include some unavailable books to prove the agent filters correctly.
- Include series metadata for books where repetition is useful.
- Include similar-book links so rejection can offer alternatives without inventing titles.

## 3. Recommendation Logic

Inputs:

- Child: Arya or Kunal
- Mood/mode:
  - Calm bedtime
  - Silly
  - Bravery
  - Science
  - Phonics
  - Short because parent is tired
- Available minutes
- Recent reading history
- Child preferences

Rules:

- Filter by age: `age_min <= child.age <= age_max`.
- Filter to `available: true`.
- Fit read time to parent energy:
  - tired parent: prefer 3-6 minutes
  - normal bedtime: prefer 5-10 minutes
  - weekend/extra time: allow 10-15 minutes
- Match mood/mode using `mood_tags` and `themes`.
- Boost child preferences from profile.
- Penalize recently read books.
- Allow recent repeat only when the child profile says repetition is loved or the prior reaction was strongly positive.
- Recommend exactly one book first.
- Offer alternatives only after rejection.
- Never imply real catalog availability; availability is fixture-backed for demo.

Example scoring signals:

```text
[book] Little Blue Truck -> age fit +3, short read +3, Kunal vehicle interest +2, rhyme +2, available +2
[book] Ada Twist, Scientist -> Arya curiosity +3, science mode +3, read time fit +2, not recent +1
[decision] chose Little Blue Truck because Kunal needs a short calm read and parent energy is low
```

## 4. Data Model Proposal

Child profiles:

```json
{
  "children": [
    {
      "id": "arya",
      "name": "Arya",
      "age": 6,
      "reading_level": "early reader with parent support",
      "interests": ["space", "animals", "science", "brave characters", "drawing"],
      "favorite_moods": ["science", "bravery", "calm bedtime"],
      "sensitivities": ["nothing too scary before bed"],
      "repetition_preference": "moderate"
    },
    {
      "id": "kunal",
      "name": "Kunal",
      "age": 3,
      "reading_level": "preschool read-aloud",
      "interests": ["trucks", "dinosaurs", "silly sounds", "rhymes"],
      "favorite_moods": ["silly", "phonics", "short because parent is tired"],
      "sensitivities": ["short attention span"],
      "repetition_preference": "high"
    }
  ]
}
```

Mock Epic-style book catalog:

```json
{
  "books": [
    {
      "id": "little-blue-truck",
      "title": "Little Blue Truck",
      "author": "Alice Schertle",
      "age_min": 2,
      "age_max": 5,
      "reading_level": "preschool read-aloud",
      "themes": ["kindness", "vehicles", "animal_sounds"],
      "mood_tags": ["calm bedtime", "phonics", "silly", "short because parent is tired"],
      "read_minutes": 5,
      "format": "read_aloud",
      "available": true,
      "series": "Little Blue Truck",
      "parent_prompts": [
        "Which animal sound should we do again?",
        "Who helped Little Blue Truck?",
        "What is one kind thing we can do tomorrow?"
      ],
      "tiny_activity": "Point out one truck, bus, or helper vehicle tomorrow.",
      "similar_book_ids": ["goodnight-goodnight-construction-site", "the-little-engine-that-could"]
    }
  ]
}
```

Reading history:

```json
{
  "events": [
    {
      "date": "2026-05-08",
      "child_id": "kunal",
      "book_id": "little-blue-truck",
      "event": "read",
      "reaction": "loved",
      "notes": "Asked for animal sounds again."
    },
    {
      "date": "2026-05-07",
      "child_id": "arya",
      "book_id": "ada-twist-scientist",
      "event": "read",
      "reaction": "liked",
      "notes": "Wanted to talk about experiments."
    }
  ]
}
```

Session input:

```json
{
  "child_id": "kunal",
  "mode": "short because parent is tired",
  "available_minutes": 6,
  "siblings_together": false
}
```

## 5. Example Outputs

Kunal: short calm bedtime

```text
Tonight's book for Kunal: Little Blue Truck by Alice Schertle.

Why this child tonight: Kunal is more likely to settle with a short, familiar read-aloud that still lets him make animal sounds.
Read time: about 5 minutes.
Available in demo catalog: yes, as a read-aloud.

Parent prompts:
1. Which animal sound should we do again?
2. Who helped Little Blue Truck?
3. What is one kind thing we can do tomorrow?

Tiny next-day activity: Point out one truck, bus, or helper vehicle tomorrow.
```

Arya: curiosity/confidence

```text
Tonight's book for Arya: Ada Twist, Scientist by Andrea Beaty.

Why this child tonight: Arya has been interested in science questions, and this gives her a confident problem-solver without turning bedtime into homework.
Read time: about 9 minutes.
Available in demo catalog: yes, as an ebook/read-aloud.

Parent prompts:
1. What question would you ask if you were Ada?
2. What did Ada do when she did not know the answer yet?
3. What is one experiment we could try this weekend?

Tiny next-day activity: Pick one household object and ask, "How does this work?"
```

Siblings together: funny read-aloud

```text
Tonight's book for Arya and Kunal together: The Book with No Pictures by B.J. Novak.

Why together tonight: It is silly enough for Kunal, still funny for Arya, and lets the parent carry the moment without managing two separate book choices.
Read time: about 6 minutes.
Available in demo catalog: yes, as a read-aloud.

Parent prompts:
1. Which nonsense word was funniest?
2. Who had the best laugh tonight?
3. Should the reader use a serious voice or a silly voice next time?

Tiny next-day activity: Make up one silly word at breakfast.
```

## 6. Lowest-Risk MVP

Recommended v2 MVP:

- Add `data/mock_epic_book_catalog.json`.
- Add `data/reading_history.json`.
- Add or extend family profile with reading preferences for Arya and Kunal.
- Add a small `storypath.py` module that returns one book recommendation.
- Add CLI scenario: `python3 -m busyparent_agent.app --scenario book`.
- Add a second top-level room in the existing web UI called `Story Picker`.
- Keep dinner/lunch/guest flows unchanged.
- Use port `8001` for v2 demos later; keep port `8000` pinned to v1.
- Add focused tests for recommendation logic and regression tests that v1 dinner behavior remains unchanged.
- Update docs only after behavior is implemented.

Implementation shape:

- `src/busyparent_agent/storypath.py`
  - load child profiles
  - load mock catalog
  - load reading history
  - score books
  - return one recommendation and trace
- `src/busyparent_agent/service.py`
  - optionally route a `book` scenario without changing meal sessions
- `src/busyparent_agent/web.py`
  - add a small second room/button only after CLI is stable
- `tests/test_storypath.py`
  - cover all new behavior independently

Preserve v1 behavior:

- No changes to meal scoring.
- No changes to inventory confidence.
- No changes to mocked Instacart catalog/cart.
- No changes to photo scan behavior.
- No changes to guest/allergy behavior.
- Existing `dinner`, `lunch`, and `guest` scenario outputs should continue to pass tests.

## 7. Demo Story

Show continuity from dinner to reading:

1. Parent opens BusyParent after work.
2. Dinner Planner room answers: "Make Egg Fried Rice tonight" or "Make Black Bean Quesadillas tonight" with the existing inventory/cart reasoning.
3. After dinner, parent switches to `Story Picker`.
4. Parent chooses child and mood:
   - Kunal + short calm bedtime
   - Arya + curiosity/confidence
   - siblings together + funny read-aloud
5. Story Picker recommends one book, not a shelf of options.
6. Parent gets three prompts and one tiny next-day activity.

Narrative:

```text
BusyParent is not just a recipe app. It removes evening decision load.
First it handles dinner from what is likely at home. Then it handles the next parent decision: what to read tonight.
Both flows use the same principle: one practical recommendation, grounded in household context, with a reviewable explanation.
```

## 8. Safety and Limitations

- Mock Epic-style catalog only.
- No real Epic login.
- No scraping.
- No real account access.
- No real book checkout or borrowing.
- Availability is deterministic demo fixture availability.
- Book metadata is curated for demo and should be labeled as such.
- Future real integration would require an official API, partner terms, or licensed catalog access.
- Parent prompts are conversation aids, not educational or developmental assessment.
- Age fit is a recommendation heuristic, not a substitute for parent judgment.

## 9. Risks

- Scope creep: a second domain can distract from the already strong dinner demo. Mitigation: keep Story Picker as a narrow second room and one CLI scenario.
- UI clutter: adding another mode may make the app feel less focused. Mitigation: use clear top-level rooms: `Dinner Planner` and `Story Picker`.
- Catalog quality: mocked books need enough variety to feel credible. Mitigation: curate 30-60 records with clear tags.
- Availability claims: must stay fixture-backed. Mitigation: always say "Available in demo catalog" rather than implying real Epic availability.
- Regression risk: dinner v1 must remain stable. Mitigation: keep v1 worktree on port `8000`, develop v2 on `v2-storypath`, and use port `8001` for future v2 demo.

## Bottom Line

Build Story Picker as BusyParent Agent v2 if time allows. The concept strengthens the broader pitch: BusyParent Agent lifts evening decision load, starting with dinner and naturally continuing into bedtime reading. The safest version uses a mocked Epic-style catalog as the single availability source, recommends exactly one book, and keeps all v1 dinner/cart/photo/Instacart behavior intact.
