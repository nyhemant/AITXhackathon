"""A tiny deterministic agent loop for HomePlate AI."""

from __future__ import annotations

from datetime import datetime, timedelta
import re
from typing import Any, Callable

from busyparent_agent import tools


class BusyParentAgent:
    def __init__(self, now: datetime, trace: bool = False, trace_sink: Callable[[str], None] | None = None):
        self.now = now
        self.trace_enabled = trace
        self.trace_sink = trace_sink
        self.family = tools.get_family_profile(self._trace)
        self.inventory = tools.estimate_inventory(self._trace, now)
        self.grocery_history = tools.get_grocery_history(self._trace)
        self.meal_options = tools.get_meal_options(self._trace)
        self.meal_history = tools.get_meal_history(self._trace)
        self.delivery_window = tools.check_delivery_window(now, self._trace)
        self.current_recommendation: dict[str, Any] | None = None
        self.alternatives: list[dict[str, Any]] = []
        self.selected_meal: dict[str, Any] | None = None

    def _trace(self, tool_name: str, payload: dict[str, Any]) -> None:
        if self.trace_enabled:
            if tool_name in {"memory_score", "save_meal_feedback"}:
                self._emit_trace(f"[memory] {self._format_tool_trace(tool_name, payload)}")
                return
            if tool_name == "inventory_confidence":
                self._emit_trace(f"[inventory] {self._format_tool_trace(tool_name, payload)}")
                return
            if tool_name.startswith("vision_"):
                self._emit_trace(f"[vision] {self._format_tool_trace(tool_name, payload)}")
                return
            if tool_name.startswith("cart_"):
                self._emit_trace(f"[cart] {self._format_tool_trace(tool_name, payload)}")
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
        feedback = self._feedback_intent(message)
        if feedback:
            return self._handle_meal_feedback(parent_message, feedback)

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
            self._decision("use Instacart only for fresh gaps; rely on Costco for pantry/freezer staples")

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
                self._inventory_confidence_line(),
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

    def _handle_meal_feedback(self, parent_message: str, feedback: dict[str, Any]) -> str:
        meal = self._find_referenced_meal(parent_message) or self.selected_meal or self.current_recommendation
        if not meal:
            return "I can remember that. Which meal should I attach it to?"

        event = tools.save_meal_feedback(
            meal["name"],
            feedback["event"],
            feedback["date"],
            self._trace,
        )
        self.meal_history.append(event)
        return self._feedback_confirmation(meal["name"], feedback["event"])

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

    def _find_referenced_meal(self, parent_message: str) -> dict[str, Any] | None:
        normalized = self._normalize_message(parent_message)
        candidates = self.alternatives + self.meal_options
        seen = set()
        unique_candidates = []
        for meal in candidates:
            if meal["name"] not in seen:
                seen.add(meal["name"])
                unique_candidates.append(meal)

        for meal in unique_candidates:
            if self._normalize_message(meal["name"]) in normalized:
                return meal

        matches = []
        message_words = set(normalized.split())
        for meal in unique_candidates:
            meal_words = self._meal_words(meal["name"])
            match_count = len(meal_words.intersection(message_words))
            if match_count:
                matches.append((match_count, meal))
        if not matches:
            return None
        matches.sort(key=lambda item: item[0], reverse=True)
        if len(matches) == 1 or matches[0][0] > matches[1][0]:
            return matches[0][1]
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

    def _feedback_intent(self, message: str) -> dict[str, Any] | None:
        normalized = self._normalize_message(message)
        event_date = self.now.date()
        if "yesterday" in normalized:
            event_date = event_date - timedelta(days=1)

        if any(phrase in normalized for phrase in ("dont suggest", "do not suggest", "avoid this week", "again this week")):
            return {"event": "avoid_this_week", "date": event_date}
        if "favorite" in normalized or "favourite" in normalized:
            return {"event": "favorite_added", "date": event_date}
        if "too spicy" in normalized:
            return {"event": "too_spicy", "date": event_date}
        if any(phrase in normalized for phrase in ("didnt eat", "did not eat", "wouldnt eat", "would not eat")):
            return {"event": "kid_rejected", "date": event_date}
        if any(phrase in normalized for phrase in ("kids loved", "kid loved", "kids liked", "kid liked", "was a hit")):
            return {"event": "kid_liked", "date": event_date}
        if any(phrase in normalized for phrase in ("we served", "served this", "served it", "served tonight")):
            return {"event": "served", "date": event_date}
        if any(phrase in normalized for phrase in ("we had", "had this", "had it")):
            return {"event": "served", "date": event_date}
        if any(phrase in normalized for phrase in ("worked well", "we liked", "i liked")):
            return {"event": "accepted", "date": event_date}
        return None

    @staticmethod
    def _normalize_message(message: str) -> str:
        normalized = message.lower().replace("’", "'").replace("'", "")
        normalized = normalized.replace("-", " ")
        return re.sub(r"[^a-z0-9 ]+", " ", normalized)

    @staticmethod
    def _meal_words(meal_name: str) -> set[str]:
        words = set()
        for word in re.split(r"\W+", meal_name.lower()):
            if len(word) <= 3 or word in {"with", "and", "the"}:
                continue
            words.add(word)
            if word.endswith("s") and len(word) > 4:
                words.add(word[:-1])
        return words

    @staticmethod
    def _feedback_confirmation(meal_name: str, event_type: str) -> str:
        if event_type == "avoid_this_week":
            return f"Got it — I’ll avoid {meal_name} for the next few days."
        if event_type == "favorite_added":
            return f"Got it — I’ll remember {meal_name} is a favorite."
        if event_type == "served":
            return f"Got it — I’ll remember you served {meal_name}."
        if event_type == "kid_liked":
            return f"Got it — I’ll remember {meal_name} was a hit."
        if event_type == "kid_rejected":
            return f"Got it — I’ll remember {meal_name} did not work for the kids."
        if event_type == "too_spicy":
            return f"Got it — I’ll remember {meal_name} was too spicy."
        return f"Got it — I’ll remember {meal_name} worked."

    def _already_have_line(self, meal: dict[str, Any]) -> str:
        available = tools.inventory_items(self.inventory)
        have = [item for item in meal["ingredients"] if item.lower() in available]
        return ", ".join(have) if have else "not much"

    @staticmethod
    def _grocery_line(grocery_list: dict[str, Any]) -> str:
        items = grocery_list["reviewable_items"]
        if not items:
            return "Reviewable grocery list: nothing required."
        cart = grocery_list.get("reviewable_cart") or {}
        if cart.get("line_items"):
            lines = [
                f"Reviewable cart/list: {', '.join(items)}.",
                "Required for tonight:",
            ]
            lines.extend(
                f"- {line['name']} - ${line['price']:.2f}"
                for line in cart.get("required_items", [])
            )
            if cart.get("smart_addons"):
                lines.append("Smart add-ons to make delivery worthwhile:")
                lines.extend(
                    f"- {line['name']} - ${line['price']:.2f} - {line['reason']}"
                    for line in cart["smart_addons"]
                )
            lines.extend(
                [
                    f"Mock subtotal: ${cart['subtotal']:.2f}",
                    f"Mock Instacart minimum: ${cart['minimum_order_amount']:.2f}",
                    f"Status: {cart['status']}",
                ]
            )
            return "\n".join(lines)
        return f"Reviewable cart/list: {', '.join(items)}."

    def _inventory_confidence_line(self) -> str:
        cadence = self.inventory.get("costco_cadence", {})
        if cadence.get("days_until_next_run") is not None and cadence["days_until_next_run"] <= 3:
            return f"Inventory confidence: Costco restock is due this {cadence['usual_day']}."
        if self.inventory.get("photo_scans"):
            suffix = " a few unknown items need confirmation." if self.inventory.get("photo_unknowns") else " no unknown items flagged."
            return "Photo evidence confirms eggs, rice, tortillas, and Costco freezer staples;" + suffix
        if not self.inventory.get("needs_photo_hint"):
            return "Inventory confidence: high enough for tonight."
        return "Inventory confidence: a quick fridge photo would improve this, but I can still plan from recent orders."

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
            return (
                f"{payload['items_seen']} visible items, "
                f"{payload['high_confidence']} high-confidence, "
                f"{payload['medium_confidence']} medium-confidence"
            )
        if tool_name == "inventory_confidence":
            return f"{payload['item']} -> {payload['bucket'].replace('_', ' ')}: {payload['reason']}"
        if tool_name == "mock_instacart.get_recent_orders":
            return f"{payload['orders']} orders"
        if tool_name == "mock_instacart.get_last_delivery":
            return payload["delivered_at"] or "none"
        if tool_name == "mock_instacart.get_frequently_bought_items":
            return f"{payload['items']} items"
        if tool_name == "mock_instacart.get_catalog_items":
            return f"{payload['items']} catalog items"
        if tool_name == "mock_instacart.search_catalog":
            return f"{payload['matches']} matches for {payload['query']}"
        if tool_name == "mock_instacart.get_item":
            return "found" if payload["found"] else "not found"
        if tool_name == "mock_instacart.check_availability":
            return f"{payload['available']} available, {payload['unavailable']} unavailable"
        if tool_name == "mock_instacart.check_delivery_window":
            return payload["message"]
        if tool_name == "mock_instacart.get_order_rules":
            return f"minimum ${payload['minimum_order_amount']:.2f}, target ${payload['cart_target_amount']:.2f}"
        if tool_name == "mock_instacart.build_reviewable_cart":
            return ", ".join(payload["items"]) if payload["items"] else "empty"
        if tool_name == "mock_photo_scan.list_available_scans":
            return f"{payload['scans']} scans"
        if tool_name == "mock_photo_scan.get_scan":
            return f"{payload['scan_id']} {'found' if payload['found'] else 'not found'}"
        if tool_name == "mock_photo_scan.get_latest_scan":
            return payload["scan_id"] or f"none for {payload['source_type']}"
        if tool_name == "mock_photo_scan.scan_photo":
            return f"{payload['scan_id']}, {payload['items']} items, {payload['unknowns']} unknowns"
        if tool_name == "vision_item":
            return f"{payload['item']} -> {payload['bucket'].replace('_', ' ')}: {payload['reason']}"
        if tool_name == "vision_unknown":
            return f"{payload['description']} -> unknown: {payload['reason']}, ask parent if needed"
        if tool_name == "vision_receipt":
            return f"{payload['source_type']} -> parsed mock receipt with {payload['items']} Costco items"
        if tool_name == "cart_required_subtotal":
            return f"required tonight subtotal: ${payload['subtotal']:.2f}"
        if tool_name == "cart_below_minimum":
            return f"below mock Instacart minimum: ${payload['minimum_order_amount']:.2f}"
        if tool_name == "cart_added_smart_addon":
            return f"added {payload['item']} because {payload['reason']}"
        if tool_name == "cart_skipped_item":
            return f"skipped {payload['item']} because {payload['reason']}"
        if tool_name == "cart_final_subtotal":
            return f"final subtotal: ${payload['subtotal']:.2f}"
        if tool_name == "costco_bulk.get_cadence":
            return f"every {payload['frequency_days']} days, {payload['usual_day']} {payload['usual_time']}"
        if tool_name == "costco_bulk.get_recent_receipts":
            days = payload["last_run_days_ago"]
            return f"last run {days} days ago" if days is not None else "no recent receipts"
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
        if tool_name == "save_meal_feedback":
            return f"saved feedback -> {payload['meal']}, {payload['event']}"
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
