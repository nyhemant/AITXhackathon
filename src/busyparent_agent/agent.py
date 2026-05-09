"""A tiny deterministic agent loop for HomePlate AI."""

from __future__ import annotations

from datetime import datetime
import re
from typing import Any

from busyparent_agent import tools


class BusyParentAgent:
    def __init__(self, now: datetime, trace: bool = False):
        self.now = now
        self.trace_enabled = trace
        self.family = tools.get_family_profile(self._trace)
        self.inventory = tools.estimate_inventory(self._trace)
        self.grocery_history = tools.get_grocery_history(self._trace)
        self.meal_options = tools.get_meal_options(self._trace)
        self.delivery_window = tools.check_delivery_window(now, self._trace)
        self.current_recommendation: dict[str, Any] | None = None
        self.alternatives: list[dict[str, Any]] = []
        self.selected_meal: dict[str, Any] | None = None

    def _trace(self, tool_name: str, payload: dict[str, Any]) -> None:
        if self.trace_enabled:
            print(f"[trace] {tool_name}: {payload}")

    def reply(self, parent_message: str) -> str:
        message = parent_message.lower()

        if self._mentions_guest_constraints(message):
            return self._handle_guest_constraints(message)

        if self._selects_meal(message):
            return self._handle_selection(parent_message)

        if self._rejects(message):
            return self._handle_rejection()

        return self._handle_first_recommendation()

    def _handle_first_recommendation(self) -> str:
        meal = tools.recommend_meal(
            self.family,
            self.inventory,
            self.grocery_history,
            self.meal_options,
            self.delivery_window,
            trace=self._trace,
        )
        self.current_recommendation = meal
        self.selected_meal = None
        grocery_list = tools.update_grocery_list(meal, self.inventory, self._trace)

        return "\n".join(
            [
                f"Make {meal['name']} tonight.",
                f"Why: {meal['why']}",
                f"Time: about {meal['minutes']} minutes, {meal['effort']} effort.",
                f"Plan: {self.delivery_window['message']}",
                self._grocery_line(grocery_list),
                "I am leading with one option so dinner moves forward.",
            ]
        )

    def _handle_rejection(self) -> str:
        if not self.current_recommendation:
            return self._handle_first_recommendation()

        self.alternatives = tools.adapt_for_rejection(
            self.current_recommendation,
            self.family,
            self.inventory,
            self.grocery_history,
            self.meal_options,
            self.delivery_window,
            trace=self._trace,
        )

        lines = ["Totally. Here are three better directions:"]
        for index, meal in enumerate(self.alternatives, start=1):
            missing = "nothing important" if not meal["missing"] else ", ".join(meal["missing"])
            lines.append(f"{index}. {meal['name']} - {meal['minutes']} min. Missing: {missing}.")
        lines.append("Pick one and I will tighten the plan.")
        return "\n".join(lines)

    def _handle_selection(self, parent_message: str) -> str:
        meal = self._find_meal(parent_message)
        if not meal:
            return "I did not catch the meal name. Say something like, \"Let's do egg fried rice.\""

        meal = dict(meal)
        meal["missing"] = tools.missing_ingredients(meal, self.inventory)
        self.selected_meal = meal
        grocery_list = tools.update_grocery_list(meal, self.inventory, self._trace)

        return "\n".join(
            [
                f"Good. Let’s do {meal['name']}.",
                f"Use what you have: {self._already_have_line(meal)}.",
                self._grocery_line(grocery_list),
                f"Parent upgrade: {meal['parent_upgrade']}",
                f"Leftover plan: {meal['leftover_plan']}",
            ]
        )

    def _handle_guest_constraints(self, message: str) -> str:
        constraints = self._parse_constraints(message)
        meal = self.selected_meal or self.current_recommendation
        if not meal:
            return self._handle_first_recommendation()

        revised = tools.apply_guest_constraints(meal, constraints, self.inventory, self._trace)
        self.selected_meal = revised
        grocery_list = tools.update_grocery_list(revised, self.inventory, self._trace)

        lines = [
            f"Keep {revised['name']}, but make it guest-safe in practice:",
            *[f"- {change}" for change in revised["constraint_changes"]],
            self._grocery_line(grocery_list),
            revised["allergy_note"],
        ]
        return "\n".join(lines)

    def _find_meal(self, parent_message: str) -> dict[str, Any] | None:
        normalized = parent_message.lower()
        candidates = self.alternatives + self.meal_options
        for meal in candidates:
            if meal["name"].lower() in normalized:
                return meal
        for meal in candidates:
            words = [word for word in re.split(r"\W+", meal["name"].lower()) if len(word) > 2]
            if all(word in normalized for word in words[:2]):
                return meal
        return None

    @staticmethod
    def _rejects(message: str) -> bool:
        return any(phrase in message for phrase in ("not feeling", "anything else", "another", "no thanks"))

    @staticmethod
    def _selects_meal(message: str) -> bool:
        return any(
            phrase in message
            for phrase in ("let's do", "lets do", "we'll do", "we will do", "i choose", "we choose")
        )

    @staticmethod
    def _mentions_guest_constraints(message: str) -> bool:
        return any(word in message for word in ("friend", "guest", "allergy", "allergic", "no nuts", "no spicy"))

    @staticmethod
    def _parse_constraints(message: str) -> dict[str, Any]:
        return {
            "no_nuts": "nut" in message or "allerg" in message,
            "no_spicy": "spicy" in message or "no spice" in message,
        }

    def _already_have_line(self, meal: dict[str, Any]) -> str:
        available = tools.inventory_items(self.inventory)
        have = [item for item in meal["ingredients"] if item.lower() in available]
        return ", ".join(have) if have else "not much"

    @staticmethod
    def _grocery_line(grocery_list: dict[str, Any]) -> str:
        items = grocery_list["reviewable_items"]
        if not items:
            return "Reviewable grocery list: nothing required."
        return f"Reviewable grocery list: {', '.join(items)}."
