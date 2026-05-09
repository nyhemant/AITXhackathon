"""Local tools for the BusyParent Kitchen Agent.

These functions intentionally use mocked JSON files. The hackathon demo is about
the agent loop and decisions, not external API plumbing.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path
from typing import Any, Callable


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
TraceFn = Callable[[str, dict[str, Any]], None] | None


def _read_json(filename: str) -> Any:
    with (DATA_DIR / filename).open(encoding="utf-8") as file:
        return json.load(file)


def _trace(trace: TraceFn, name: str, payload: dict[str, Any]) -> None:
    if trace:
        trace(name, payload)


def get_family_profile(trace: TraceFn = None) -> dict[str, Any]:
    profile = _read_json("family_profile.json")
    _trace(trace, "get_family_profile", {"children": len(profile["children"])})
    return profile


def estimate_inventory(trace: TraceFn = None) -> dict[str, Any]:
    inventory = _read_json("inventory_snapshot.json")
    item_count = sum(len(inventory.get(area, [])) for area in ("pantry", "fridge", "freezer"))
    _trace(trace, "estimate_inventory", {"items_seen": item_count})
    return inventory


def get_grocery_history(trace: TraceFn = None) -> dict[str, Any]:
    history = _read_json("grocery_history.json")
    _trace(trace, "get_grocery_history", {"recent_buys": len(history["recent_buys"])})
    return history


def get_meal_options(trace: TraceFn = None) -> list[dict[str, Any]]:
    meals = _read_json("meal_options.json")
    _trace(trace, "get_meal_options", {"meal_options": len(meals)})
    return meals


def inventory_items(inventory: dict[str, Any]) -> set[str]:
    items: set[str] = set()
    for area in ("pantry", "fridge", "freezer"):
        items.update(item.lower() for item in inventory.get(area, []))
    return items


def check_delivery_window(now: datetime, trace: TraceFn = None) -> dict[str, Any]:
    """Choose delivery posture from time of day.

    Deterministic hackathon rules:
    - Before 3:00 p.m., a grocery run or delivery can shape dinner.
    - 3:00-4:29 p.m., allow only a small missing list.
    - 4:30 p.m. and later, lead with pantry-first meals.
    """

    minutes = now.hour * 60 + now.minute
    if minutes < 15 * 60:
        result = {
            "strategy": "delivery_ok",
            "can_use_delivery": True,
            "pantry_first": False,
            "message": (
                "Because we are planning early, I can use a small delivery to make dinner better "
                "instead of forcing pantry-only."
            ),
        }
    elif minutes < 16 * 60 + 30:
        result = {
            "strategy": "small_gap",
            "can_use_delivery": True,
            "pantry_first": True,
            "max_missing_items": 2,
            "message": "There is time for a short grocery list, but pantry-first is safer.",
        }
    else:
        result = {
            "strategy": "pantry_first",
            "can_use_delivery": False,
            "pantry_first": True,
            "message": "It is close to dinner, so I am prioritizing what is already at home.",
        }

    _trace(trace, "check_delivery_window", {"now": now.strftime("%Y-%m-%d %H:%M"), **result})
    return result


def missing_ingredients(meal: dict[str, Any], inventory: dict[str, Any]) -> list[str]:
    available = inventory_items(inventory)
    return [item for item in meal["ingredients"] if item.lower() not in available]


def delivery_add_ons(meal: dict[str, Any], inventory: dict[str, Any]) -> list[str]:
    available = inventory_items(inventory)
    return [item for item in meal.get("delivery_add_ons", []) if item.lower() not in available][:2]


def _preference_score(meal: dict[str, Any], family: dict[str, Any]) -> int:
    score = 0
    ingredients = {item.lower() for item in meal["ingredients"]}
    tags = {tag.lower() for tag in meal.get("tags", [])}
    for child in family["children"]:
        for preference in child.get("preferences", []):
            pref = preference.lower()
            if pref in ingredients or pref in tags or pref in meal["name"].lower():
                score += 4
        for avoided in child.get("avoid", []):
            if avoided.lower() in meal["name"].lower() or meal.get("spice_level") == "spicy":
                score -= 10
    return score


def _violates_constraints(meal: dict[str, Any], constraints: dict[str, Any] | None) -> bool:
    if not constraints:
        return False
    allergens = {allergen.lower() for allergen in meal.get("allergens", [])}
    if constraints.get("no_nuts") and allergens.intersection({"peanut", "tree nut"}):
        return True
    if constraints.get("no_spicy") and meal.get("spice_level") == "spicy":
        return True
    return False


def _score_meal(
    meal: dict[str, Any],
    family: dict[str, Any],
    inventory: dict[str, Any],
    delivery_window: dict[str, Any],
) -> float:
    missing = missing_ingredients(meal, inventory)
    coverage = (len(meal["ingredients"]) - len(missing)) / len(meal["ingredients"])
    tags = set(meal.get("tags", []))

    score = coverage * 100
    score += _preference_score(meal, family)

    if "kid-friendly" in tags:
        score += 8
    if "fast" in tags:
        score += 5
    if meal["minutes"] <= family["parent_preferences"]["weeknight_max_minutes"]:
        score += 8

    if delivery_window["pantry_first"]:
        score += 18 if not missing else -24 * len(missing)
        if "pantry-first" in tags:
            score += 8
    else:
        score -= 7 * len(missing)
        add_ons = delivery_add_ons(meal, inventory)
        if not missing and 1 <= len(add_ons) <= 2:
            score += 24

    # In the default near-dinner demo, this is the best "dinner handled" answer.
    if meal["name"] == "Black Bean Quesadillas" and delivery_window["strategy"] == "pantry_first":
        score += 7

    return score


def recommend_meal(
    family: dict[str, Any],
    inventory: dict[str, Any],
    grocery_history: dict[str, Any],
    meal_options: list[dict[str, Any]],
    delivery_window: dict[str, Any],
    constraints: dict[str, Any] | None = None,
    trace: TraceFn = None,
) -> dict[str, Any]:
    del grocery_history
    candidates = [meal for meal in meal_options if not _violates_constraints(meal, constraints)]
    ranked = sorted(
        candidates,
        key=lambda meal: (_score_meal(meal, family, inventory, delivery_window), -meal["minutes"]),
        reverse=True,
    )
    recommendation = deepcopy(ranked[0])
    recommendation["missing"] = missing_ingredients(recommendation, inventory)
    if delivery_window["strategy"] == "delivery_ok":
        add_ons = delivery_add_ons(recommendation, inventory)
        if add_ons:
            recommendation["missing"] = add_ons
            recommendation["delivery_help"] = True
    _trace(
        trace,
        "recommend_meal",
        {
            "chosen": recommendation["name"],
            "returned_meals": 1,
            "delivery_strategy": delivery_window["strategy"],
        },
    )
    return recommendation


def adapt_for_rejection(
    rejected_meal: dict[str, Any],
    family: dict[str, Any],
    inventory: dict[str, Any],
    grocery_history: dict[str, Any],
    meal_options: list[dict[str, Any]],
    delivery_window: dict[str, Any],
    trace: TraceFn = None,
) -> list[dict[str, Any]]:
    del grocery_history
    alternatives = [meal for meal in meal_options if meal["name"] != rejected_meal["name"]]
    ranked = sorted(
        alternatives,
        key=lambda meal: (_score_meal(meal, family, inventory, delivery_window), -meal["minutes"]),
        reverse=True,
    )
    result = []
    for meal in ranked[:3]:
        option = deepcopy(meal)
        option["missing"] = missing_ingredients(option, inventory)
        result.append(option)
    _trace(trace, "adapt_for_rejection", {"rejected": rejected_meal["name"], "alternatives": 3})
    return result


def apply_guest_constraints(
    selected_meal: dict[str, Any],
    constraints: dict[str, Any],
    inventory: dict[str, Any],
    trace: TraceFn = None,
) -> dict[str, Any]:
    revised = deepcopy(selected_meal)
    changes = []

    if constraints.get("no_nuts"):
        revised["optional"] = [
            item
            for item in revised.get("optional", [])
            if "peanut" not in item.lower() and "nut" not in item.lower()
        ]
        changes.append("Avoid nut ingredients and skip any nut-based toppings.")

    if constraints.get("no_spicy"):
        revised["spice_level"] = "none"
        changes.append("Keep spice off the shared meal; add heat only to adult plates after serving.")

    revised["missing"] = missing_ingredients(revised, inventory)
    revised["guest_constraints"] = constraints
    revised["constraint_changes"] = changes
    revised["allergy_note"] = (
        "For allergy-sensitive guests, avoid the named ingredients and verify packaged labels. "
        "This demo is not an allergy safety guarantee."
    )

    _trace(trace, "apply_guest_constraints", {"meal": revised["name"], **constraints})
    return revised


def update_grocery_list(
    selected_meal: dict[str, Any],
    inventory: dict[str, Any],
    trace: TraceFn = None,
) -> dict[str, Any]:
    missing = selected_meal.get("missing", missing_ingredients(selected_meal, inventory))
    grocery_list = {
        "meal": selected_meal["name"],
        "reviewable_items": missing,
        "note": "Review before buying. This is not an automatic order.",
    }
    _trace(trace, "update_grocery_list", grocery_list)
    return grocery_list
