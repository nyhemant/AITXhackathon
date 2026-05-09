"""Channel-neutral service layer for CLI, web, and future adapters."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from busyparent_agent.agent import BusyParentAgent
from busyparent_agent import tools


APP_TITLE = "BusyParent Kitchen Agent / HomePlate AI"
APP_SUBTITLE = "Local Python agent demo"

SCENARIO_MESSAGES = {
    "dinner": "What should I make for dinner tonight?",
    "lunch": "What should I make for dinner tonight?",
    "guest": "My daughter has a friend coming over. No nuts, no spicy food.",
}


def parse_now(value: str | None, demo: bool = False, scenario: str | None = None) -> datetime:
    if value:
        return datetime.strptime(value, "%Y-%m-%d %H:%M")
    if scenario == "lunch":
        return datetime.strptime("2026-05-09 12:30", "%Y-%m-%d %H:%M")
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
    if scenario == "guest":
        session.set_selected_meal("Egg Fried Rice")
        return [
            {
                "context": "Selected meal is Egg Fried Rice.",
                **session.send(SCENARIO_MESSAGES["guest"], scenario=scenario),
            }
        ]

    return [session.send(SCENARIO_MESSAGES[scenario], scenario=scenario)]


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
