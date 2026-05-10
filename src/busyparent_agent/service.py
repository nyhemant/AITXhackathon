"""Channel-neutral service layer for CLI, web, and future adapters."""

from __future__ import annotations

from datetime import datetime
import json
from typing import Any

from busyparent_agent.agent import BusyParentAgent
from busyparent_agent import tools
from busyparent_agent.adapters import mock_epic


APP_TITLE = "BusyMom Agent"
APP_SUBTITLE = "Local Python agent demo"

SCENARIO_MESSAGES = {
    "dinner": "What should I make for dinner tonight?",
    "lunch": "What should I make for dinner tonight?",
    "guest": "My daughter has a friend coming over. No nuts, no spicy food.",
    "book": "What should I read with Kunal tonight?",
}
STORYPATH_CHILDREN = {
    "kunal": {
        "id": "kunal",
        "name": "Kunal",
        "age": 3,
        "reading_level": "preschool read-aloud",
        "interests": ["trucks", "dinosaurs", "silly sounds", "rhymes"],
        "favorite_moods": ["silly", "phonics", "short because parent is tired", "calm bedtime"],
        "repetition_preference": "high",
    },
    "arya": {
        "id": "arya",
        "name": "Arya",
        "age": 6,
        "reading_level": "early reader with parent support",
        "interests": ["space", "animals", "science", "brave characters", "drawing"],
        "favorite_moods": ["science", "bravery", "calm bedtime"],
        "repetition_preference": "moderate",
    },
    "siblings": {
        "id": "siblings",
        "name": "Arya and Kunal",
        "age": 3,
        "child_ages": [6, 3],
        "reading_level": "shared read-aloud",
        "interests": ["trucks", "dinosaurs", "silly sounds", "rhymes", "space", "animals", "science", "brave characters"],
        "favorite_moods": ["silly", "calm bedtime", "science", "bravery"],
        "repetition_preference": "moderate",
    },
}


def parse_now(value: str | None, demo: bool = False, scenario: str | None = None) -> datetime:
    if value:
        return datetime.strptime(value, "%Y-%m-%d %H:%M")
    if scenario == "lunch":
        return datetime.strptime("2026-05-09 12:30", "%Y-%m-%d %H:%M")
    if scenario == "book":
        return datetime.strptime("2026-05-08 20:00", "%Y-%m-%d %H:%M")
    if scenario in {"dinner", "guest"}:
        return datetime.strptime("2026-05-08 17:30", "%Y-%m-%d %H:%M")
    if demo:
        return datetime.strptime("2026-05-08 17:30", "%Y-%m-%d %H:%M")
    return datetime.now()


class AgentSession:
    """Stateful wrapper that returns reusable response dictionaries."""

    def __init__(self, now: datetime, trace: bool = False, locked_time_context: bool = False):
        self.trace = trace
        self.locked_time_context = locked_time_context
        self._trace_lines: list[str] = []
        self.agent = self._new_agent(now)

    def send(self, parent_message: str, scenario: str | None = None) -> dict[str, Any]:
        self._apply_message_time_context(parent_message)
        trace_lines = self._consume_trace()
        message_text = self.agent.reply(parent_message)
        trace_lines.extend(self._consume_trace())
        return self._response(parent_message, message_text, trace_lines, scenario)

    def _new_agent(self, now: datetime) -> BusyParentAgent:
        return BusyParentAgent(now=now, trace=self.trace, trace_sink=self._trace_lines.append)

    def _apply_message_time_context(self, parent_message: str) -> None:
        if self.locked_time_context or self.agent.current_recommendation or self.agent.selected_meal:
            return

        message = parent_message.lower()
        if message_implies_early_planning(message):
            self._trace_lines.clear()
            self.agent = self._new_agent(parse_now(None, scenario="lunch"))
        elif message_implies_dinner_now(message):
            self._trace_lines.clear()
            self.agent = self._new_agent(parse_now(None, scenario="dinner"))

    def set_selected_meal(self, meal_name: str) -> None:
        meal = next(meal for meal in self.agent.meal_options if meal["name"] == meal_name)
        selected = dict(meal)
        selected["missing"] = tools.missing_ingredients(selected, self.agent.inventory)
        self.agent.selected_meal = selected

    def _consume_trace(self) -> list[str]:
        lines = self._trace_lines[:]
        self._trace_lines.clear()
        return lines

    def _response(
        self,
        parent_message: str,
        message_text: str,
        trace_lines: list[str],
        scenario: str | None,
    ) -> dict[str, Any]:
        active_meal = self.agent.selected_meal or self.agent.current_recommendation or {}
        return {
            "parent_message": parent_message,
            "message": message_text,
            "trace": trace_lines,
            "grocery_items": active_meal.get("missing", []),
            "metadata": {
                "scenario": scenario,
                "delivery_strategy": self.agent.delivery_window["strategy"],
                "current_recommendation": (
                    self.agent.current_recommendation["name"] if self.agent.current_recommendation else None
                ),
                "selected_meal": self.agent.selected_meal["name"] if self.agent.selected_meal else None,
            },
        }


def create_session(
    now: datetime | None = None,
    trace: bool = False,
    scenario: str | None = None,
    locked_time_context: bool = False,
) -> AgentSession:
    return AgentSession(
        now=now or parse_now(None, scenario=scenario),
        trace=trace,
        locked_time_context=locked_time_context or scenario is not None,
    )


def run_scenario(session: AgentSession, scenario: str) -> list[dict[str, Any]]:
    if scenario == "book":
        session._consume_trace()
        return [run_book_scenario(trace=session.trace)]

    return [session.send(SCENARIO_MESSAGES[scenario], scenario=scenario)]


def run_book_scenario(
    trace: bool = False,
    parent_message: str | None = None,
    exclude_book_ids: list[str] | None = None,
) -> dict[str, Any]:
    parent_message = parent_message or SCENARIO_MESSAGES["book"]
    request = parse_book_request(parent_message)
    child_profile = request["child_profile"]
    mood = request["mood"]
    max_minutes = request["max_minutes"]
    book_intent = request["book_intent"]
    excluded = [] if request["allow_repeat"] else (exclude_book_ids or [])
    reading_history = _get_reading_history()
    catalog_count = len(mock_epic.get_catalog_books())
    recommendation = mock_epic.recommend_book(
        child_profile,
        mood,
        max_minutes,
        reading_history,
        exclude_book_ids=excluded,
        child_ages=child_profile.get("child_ages"),
        book_intent=book_intent,
    )
    top_pick = recommendation["top_pick"]
    book = top_pick["book"]

    trace_lines = []
    if trace:
        trace_lines.extend(
            [
                f"[book] mock_epic.get_catalog_books -> {catalog_count} books",
                f"[book] filter age/mood/time/availability -> {child_profile['name']}, {mood}, {max_minutes} min",
                f"[book] prompt intent -> {', '.join(book_intent['labels']) if book_intent['labels'] else 'default bedtime'}",
                "[memory] recent reading history checked",
                f"[decision] chose {book['title']} because {_book_decision_reason(child_profile, mood, max_minutes, top_pick)}",
            ]
        )

    return {
        "parent_message": parent_message,
        "message": _format_book_message(child_profile, mood, max_minutes, top_pick),
        "trace": trace_lines,
        "grocery_items": [],
        "metadata": {
            "scenario": "book",
            "child_id": child_profile["id"],
            "child": child_profile["name"],
            "mode": mood,
            "max_minutes": max_minutes,
            "book_id": book["id"],
            "book_recommendation": book["title"],
        },
    }


def parse_book_request(parent_message: str) -> dict[str, Any]:
    message = parent_message.lower()
    labels = []
    if any(
        phrase in message
        for phrase in ("both", "both of them", "siblings", "arya and kunal", "kunal and arya", "they have not")
    ):
        child_profile = STORYPATH_CHILDREN["siblings"]
        labels.append("siblings")
    elif "arya" in message:
        child_profile = STORYPATH_CHILDREN["arya"]
    elif "kunal" in message:
        child_profile = STORYPATH_CHILDREN["kunal"]
    else:
        child_profile = STORYPATH_CHILDREN["kunal"]

    mood = "calm bedtime"
    explicit_calm = any(word in message for word in ("calm", "bedtime", "sleep"))
    silly = any(word in message for word in ("silly", "funny"))
    science = any(word in message for word in ("science", "science-y", "curious", "curiosity"))
    bravery = any(word in message for word in ("bravery", "brave", "confidence", "confident"))
    rhyme_repetition = any(word in message for word in ("rhyme", "rhyming", "repetition", "repeat", "phonics"))
    grown_up = any(phrase in message for phrase in ("grown-up", "grown up", "older", "big kid"))
    short_tired = any(word in message for word in ("short", "quick", "tired"))
    easy_prompts = any(phrase in message for phrase in ("easy parent prompts", "parent prompts", "easy prompts"))
    not_recent = any(phrase in message for phrase in ("not read recently", "not recently", "have not read", "haven't read"))

    if any(word in message for word in ("silly", "funny")):
        mood = "silly"
    elif science:
        mood = "science"
    elif bravery:
        mood = "bravery"
    elif rhyme_repetition:
        mood = "phonics"
    elif easy_prompts:
        mood = "short because parent is tired"
    elif explicit_calm:
        mood = "calm bedtime"

    max_minutes = 10
    if short_tired:
        max_minutes = 6

    if explicit_calm:
        labels.append("explicit_calm")
    if silly:
        labels.append("silly")
    if science:
        labels.append("science")
    if bravery:
        labels.append("bravery")
    if rhyme_repetition:
        labels.append("rhyme_repetition")
    if grown_up:
        labels.append("grown_up")
    if short_tired:
        labels.append("short_tired")
    if easy_prompts:
        labels.append("easy_prompts")
    if not_recent:
        labels.append("not_recent")

    return {
        "child_profile": child_profile,
        "mood": mood,
        "max_minutes": max_minutes,
        "allow_repeat": any(phrase in message for phrase in ("same", "again", "repeat")),
        "book_intent": {
            "labels": labels,
            "siblings": "siblings" in labels,
            "explicit_calm": explicit_calm,
            "silly": silly,
            "science": science,
            "bravery": bravery,
            "rhyme_repetition": rhyme_repetition,
            "grown_up": grown_up,
            "short_tired": short_tired,
            "easy_prompts": easy_prompts,
            "not_recent": not_recent,
        },
    }


def _get_reading_history() -> dict[str, Any]:
    with (mock_epic.DATA_DIR / "reading_history.json").open(encoding="utf-8") as file:
        return json.load(file)


def _format_book_message(
    child_profile: dict[str, Any],
    mood: str,
    max_minutes: int,
    top_pick: dict[str, Any],
) -> str:
    book = top_pick["book"]
    prompts = book["parent_prompts"]
    return "\n".join(
        [
            f"Tonight's pick: {book['title']} by {book['author']}.",
            f"Why it fits {child_profile['name']} tonight: {_book_decision_reason(child_profile, mood, max_minutes, top_pick)}.",
            f"Read time: about {book['read_minutes']} minutes.",
            f"Format/source: {book['format'].replace('_', ' ')} from the mocked Epic-style catalog.",
            "Parent prompts:",
            f"1. {prompts[0]}",
            f"2. {prompts[1]}",
            f"3. {prompts[2]}",
            f"Tiny tomorrow activity: {book['tiny_activity']}",
            "Note: availability is from a mocked Epic-style fixture only; no real Epic login, API, scraping, or checkout is used.",
        ]
    )


def _book_decision_reason(
    child_profile: dict[str, Any],
    mood: str,
    max_minutes: int,
    top_pick: dict[str, Any],
) -> str:
    book = top_pick["book"]
    if child_profile["id"] == "siblings":
        return (
            f"it works as a shared read for both Arya and Kunal, fits {mood}, "
            f"stays within {max_minutes} minutes, and is available in the demo catalog"
        )
    return (
        f"it fits {child_profile['name']}'s {mood} mode, stays within {max_minutes} minutes, "
        f"and is available in the demo catalog"
    )


def message_implies_early_planning(message: str) -> bool:
    phrases = (
        "noon",
        "lunch",
        "lunchtime",
        "early",
        "plan ahead",
        "plan for dinner tonight",
        "planning for dinner tonight",
        "this afternoon",
    )
    return any(phrase in message for phrase in phrases)


def message_implies_dinner_now(message: str) -> bool:
    phrases = (
        "just got home",
        "dinner now",
        "need dinner now",
        "right now",
        "last minute",
    )
    return any(phrase in message for phrase in phrases)
