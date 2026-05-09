"""A tiny deterministic agent loop for HomePlate AI."""

from __future__ import annotations

from datetime import datetime
import re
from typing import Any, Callable

from busyparent_agent import tools


class BusyParentAgent:
    def __init__(self, now: datetime, trace: bool = False, trace_sink: Callable[[str], None] | None = None):
        self.now = now
        self.trace_enabled = trace
        self.trace_sink = trace_sink
        self.family = tools.get_family_profile(self._trace)
        self.inventory = tools.estimate_inventory(self._trace)
        self.grocery_history = tools.get_grocery_history(self._trace)
        self.meal_options = tools.get_meal_options(self._trace)
        self.meal_history = tools.get_meal_history(self._trace)
        self.delivery_window = tools.check_delivery_window(now, self._trace)
        self.current_recommendation: dict[str, Any] | None = None
        self.alternatives: list[dict[str, Any]] = []
        self.selected_meal: dict[str, Any] | None = None

    def _trace(self, tool_name: str, payload: dict[str, Any]) -> None:
        if self.trace_enabled:
            if tool_name == "memory_score":
                self._emit_trace(f"[memory] {self._format_tool_trace(tool_name, payload)}")
                return
            self._emit_trace(f"[tool] {tool_name} -> {self._format_tool_trace(tool_name, payload)}")

    def _decision(self, message: str) -> None:
        if self.trace_enabled:
            self._emit_trace(f"[decision] {message}")

    def _emit_trace(self, line: str) -> None:
        if self.trace_sink:
            self.trace_sink(line)
        else:
            print(line)

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
        if self.delivery_window["pantry_first"]:
            self._decision("pantry-first because it is close to dinner")
        else:
            self._decision("grocery delivery can help because planning starts earlier")

        meal = tools.recommend_meal(
            self.family,
            self.inventory,
            self.grocery_history,
            self.meal_options,
            self.delivery_window,
            self.meal_history,
            self.now,
            trace=self._trace,
        )
        self.current_recommendation = meal
        self.selected_meal = None
        grocery_list = tools.update_grocery_list(meal, self.inventory, self._trace)
        self._decision(self._choice_decision(meal))

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

        self._decision("parent rejected the first plan, so offer three alternatives")

        self.alternatives = tools.adapt_for_rejection(
            self.current_recommendation,
            self.family,
            self.inventory,
            self.grocery_history,
            self.meal_options,
            self.delivery_window,
            self.meal_history,
            self.now,
            trace=self._trace,
        )

        lines = ["Totally. Here are three better directions:"]
        for index, meal in enumerate(self.alternatives, start=1):
            missing = "nothing important" if not meal["missing"] else ", ".join(meal["missing"])
            lines.append(f"{index}. {meal['name']} - {meal['minutes']} min. Missing: {missing}.")
        lines.append(self._alternative_pick_line())
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
        self._decision(f"tighten selected plan for {meal['name']}")

        if meal["name"] == "Egg Fried Rice":
            return "\n".join(
                [
                    "Good. Let’s do Egg Fried Rice.",
                    "Timing: 5 minutes prep, 12-15 minutes cook.",
                    f"Use what you have: {self._already_have_line(meal)}.",
                    "Kid adaptation: keep vegetables small and let soy sauce stay light.",
                    "Adult upgrade: add chili crisp or scallions after serving children.",
                    "Backup: if eggs get rejected, serve the rice with cheese quesadilla triangles.",
                    self._grocery_line(grocery_list),
                ]
            )

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
        self._decision("revise selected dinner for guest child constraints")

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

    def _alternative_pick_line(self) -> str:
        egg_option = next((meal for meal in self.alternatives if meal["name"] == "Egg Fried Rice"), None)
        pick = egg_option or self.alternatives[0]
        return f"I’d pick {pick['name']} if you want the least effort tonight."

    def _choice_decision(self, meal: dict[str, Any]) -> str:
        if meal["name"] == "Egg Fried Rice" and self.delivery_window["strategy"] == "pantry_first":
            return "chose Egg Fried Rice because it fits tonight and avoids repeating yesterday's meal"
        if meal.get("delivery_help"):
            return f"chose {meal['name']} because delivery can add small fresh items while keeping the core dinner familiar"
        return f"lead with one dinner: {meal['name']}"

    @staticmethod
    def _format_tool_trace(tool_name: str, payload: dict[str, Any]) -> str:
        if tool_name == "get_family_profile":
            return f"{payload['children']} children, mild spice, peanut-aware"
        if tool_name == "estimate_inventory":
            return f"{payload['items_seen']} likely items"
        if tool_name == "get_grocery_history":
            return f"{payload['recent_buys']} recent grocery signals"
        if tool_name == "get_meal_options":
            return f"{payload['meal_options']} candidate dinners"
        if tool_name == "get_meal_history":
            return f"{payload['events']} local household memory events"
        if tool_name == "check_delivery_window":
            return payload["message"]
        if tool_name == "memory_score":
            reasons = ", ".join(payload["reasons"])
            return f"{payload['meal']} -> {reasons}; score {payload['total_score']}"
        if tool_name == "recommend_meal":
            strategy = payload["delivery_strategy"].replace("_", "-")
            return f"{payload['chosen']}, one meal returned, {strategy}"
        if tool_name == "adapt_for_rejection":
            return f"rejected {payload['rejected']}, returned {payload['alternatives']} alternatives"
        if tool_name == "apply_guest_constraints":
            constraints = []
            if payload.get("no_nuts"):
                constraints.append("no nuts")
            if payload.get("no_spicy"):
                constraints.append("no spicy food")
            return f"{payload['meal']} revised for {', '.join(constraints)}"
        if tool_name == "update_grocery_list":
            items = payload["reviewable_items"]
            if not items:
                return f"{payload['meal']}, no missing items"
            return f"{payload['meal']}, review {', '.join(items)}"
        return str(payload)
