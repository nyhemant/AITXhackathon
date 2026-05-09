"""Mock Epic-style kids book catalog adapter.

No login, scraping, network calls, or real account access happen here.
"""

from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import re
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data"
RECENT_DAYS = 7


def get_catalog_books() -> list[dict[str, Any]]:
    with (DATA_DIR / "mock_epic_book_catalog.json").open(encoding="utf-8") as file:
        payload = json.load(file)
    return payload["books"]


def get_book(book_id: str) -> dict[str, Any] | None:
    return next((book for book in get_catalog_books() if book["id"] == book_id), None)


def search_books(query: str) -> list[dict[str, Any]]:
    normalized = _normalize(query)
    if not normalized:
        return []

    results = []
    for book in get_catalog_books():
        haystack = " ".join(
            [
                book["title"],
                book["author"],
                book["reading_level"],
                book.get("series") or "",
                *book.get("themes", []),
                *book.get("mood_tags", []),
            ]
        )
        if normalized in _normalize(haystack):
            results.append(book)
    return results


def filter_books(
    child_age: int,
    mood: str,
    max_minutes: int,
    child_ages: list[int] | None = None,
    exclude_book_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    excluded = set(exclude_book_ids or [])
    return [
        book
        for book in get_catalog_books()
        if book["available"]
        and book["id"] not in excluded
        and _age_matches(book, child_age, child_ages)
        and book["read_minutes"] <= max_minutes
        and _matches_mood(book, mood)
    ]


def recommend_book(
    child_profile: dict[str, Any],
    mood: str,
    max_minutes: int,
    reading_history: dict[str, Any] | list[dict[str, Any]],
    exclude_book_ids: list[str] | None = None,
    child_ages: list[int] | None = None,
) -> dict[str, Any]:
    excluded = set(exclude_book_ids or [])
    candidates = filter_books(child_profile["age"], mood, max_minutes, child_ages, list(excluded))
    if not candidates:
        candidates = [
            book
            for book in get_catalog_books()
            if book["available"]
            and book["id"] not in excluded
            and _age_matches(book, child_profile["age"], child_ages)
            and book["read_minutes"] <= max_minutes
        ]

    scored = [
        _score_book(book, child_profile, mood, max_minutes, reading_history)
        for book in candidates
    ]
    scored.sort(key=lambda item: (-item["score"], item["book"]["read_minutes"], item["book"]["title"]))

    top_pick = scored[0] if scored else None
    alternatives = scored[1:3]
    return {
        "top_pick": top_pick,
        "alternatives": alternatives,
        "all_candidates": scored,
    }


def _score_book(
    book: dict[str, Any],
    child_profile: dict[str, Any],
    mood: str,
    max_minutes: int,
    reading_history: dict[str, Any] | list[dict[str, Any]],
) -> dict[str, Any]:
    score = 0
    reasons = []

    if book["available"]:
        score += 2
        reasons.append("available +2")
    if book["age_min"] <= child_profile["age"] <= book["age_max"]:
        score += 3
        reasons.append("age fit +3")
    if book["read_minutes"] <= max_minutes:
        score += 2
        reasons.append("time fit +2")

    mood_score = _mood_score(book, mood)
    if mood_score:
        score += mood_score
        reasons.append(f"mood match +{mood_score}")

    preference_score = _preference_score(book, child_profile)
    if preference_score:
        score += preference_score
        reasons.append(f"child preference +{preference_score}")

    history_score, history_reason = _history_adjustment(book, child_profile, reading_history)
    if history_score:
        score += history_score
        reasons.append(history_reason)
    elif history_reason:
        reasons.append(history_reason)

    return {
        "book": book,
        "score": score,
        "reasons": reasons,
    }


def _age_matches(book: dict[str, Any], child_age: int, child_ages: list[int] | None) -> bool:
    if child_ages:
        return book["age_min"] <= min(child_ages) and max(child_ages) <= book["age_max"]
    return book["age_min"] <= child_age <= book["age_max"]


def _mood_score(book: dict[str, Any], mood: str) -> int:
    mood_terms = _terms(mood)
    tag_terms = _book_terms(book, ("mood_tags", "themes"))
    if _normalize(mood) in {_normalize(tag) for tag in book.get("mood_tags", [])}:
        return 4
    if mood_terms.intersection(tag_terms):
        return 3
    return 0


def _preference_score(book: dict[str, Any], child_profile: dict[str, Any]) -> int:
    preferences = set()
    for field in ("interests", "favorite_moods"):
        for value in child_profile.get(field, []):
            preferences.update(_terms(value))

    matches = preferences.intersection(_book_terms(book, ("themes", "mood_tags", "title")))
    return min(4, len(matches) * 2)


def _history_adjustment(
    book: dict[str, Any],
    child_profile: dict[str, Any],
    reading_history: dict[str, Any] | list[dict[str, Any]],
) -> tuple[int, str | None]:
    events = _history_events(reading_history)
    applicable = [
        event
        for event in events
        if event.get("book_id") == book["id"]
        and event.get("child_id") in {child_profile["id"], "siblings"}
    ]
    if not applicable:
        return 1, "not recent +1"

    latest_date = _latest_history_date(events)
    recent = [event for event in applicable if _is_recent(event, latest_date)]
    if not recent:
        return 1, "not recent +1"

    latest_event = sorted(recent, key=lambda event: event.get("date", ""), reverse=True)[0]
    if latest_event.get("reaction") == "disliked":
        return -10, "recently disliked -10"

    if _repeat_allowed(book, child_profile, latest_event):
        return -1, "recent repeat allowed -1"
    return -8, "recently read -8"


def _repeat_allowed(book: dict[str, Any], child_profile: dict[str, Any], event: dict[str, Any]) -> bool:
    repeat_preference = child_profile.get("repetition_preference") == "high"
    repeat_book = "repeat_friendly" in book.get("themes", [])
    loved_repeat = event.get("event") == "repeated" or event.get("reaction") == "loved"
    return repeat_book and (repeat_preference or loved_repeat)


def _history_events(reading_history: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(reading_history, dict):
        return reading_history.get("events", [])
    return reading_history


def _latest_history_date(events: list[dict[str, Any]]) -> date | None:
    parsed = [_parse_date(event.get("date")) for event in events]
    parsed = [value for value in parsed if value is not None]
    return max(parsed) if parsed else None


def _is_recent(event: dict[str, Any], latest_date: date | None) -> bool:
    event_date = _parse_date(event.get("date"))
    if not event_date or not latest_date:
        return False
    return (latest_date - event_date).days <= RECENT_DAYS


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _matches_mood(book: dict[str, Any], mood: str) -> bool:
    mood_terms = _terms(mood)
    return bool(mood_terms.intersection(_book_terms(book, ("mood_tags", "themes"))))


def _book_terms(book: dict[str, Any], fields: tuple[str, ...]) -> set[str]:
    terms = set()
    for field in fields:
        value = book.get(field, [])
        if isinstance(value, str):
            values = [value]
        else:
            values = value
        for item in values:
            terms.update(_terms(item))
    return terms


def _terms(value: str) -> set[str]:
    normalized = _normalize(value).replace("_", " ")
    words = {word for word in normalized.split() if len(word) > 2}
    if normalized:
        words.add(normalized)
    if "short" in words:
        words.add("short because parent is tired")
    if "curiosity" in words:
        words.add("science")
    return words


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower().replace("-", " "))
