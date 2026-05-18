"""Channel-neutral service layer for CLI, web, and future adapters."""

from __future__ import annotations

from datetime import datetime
import json
import re
from typing import Any

from busyparent_agent.agent import BusyParentAgent
from busyparent_agent import tools
from busyparent_agent.adapters import mock_epic


APP_TITLE = "1Less"
APP_SUBTITLE = "Chapter 1 dinner decision demo"
ALLERGY_CAVEAT = (
    "1Less can help avoid ingredients you flag, but it cannot guarantee allergy safety. "
    "Always check labels and use your judgment for serious allergies."
)
TYPICAL_FAMILY_STAPLES = {
    # Conservative baseline for a family of 4 with young kids before the user shares real inventory.
    # Derived from common pantry/fridge/freezer staple guidance: grains/pasta, canned beans/tomatoes,
    # tortillas/bread, eggs/dairy, sturdy produce, frozen vegetables, and simple freezer proteins.
    "pantry": {
        "rice",
        "pasta",
        "marinara",
        "jar sauce",
        "beans",
        "black beans",
        "tortillas",
        "bread",
        "crackers",
        "potatoes",
        "oats",
        "cereal",
    },
    "fridge": {
        "eggs",
        "cheese",
        "milk",
        "yogurt",
        "carrots",
        "fruit",
        "apples",
        "bananas",
        "salad",
        "salad kit",
    },
    "freezer": {
        "frozen peas",
        "frozen vegetables",
        "corn",
        "nuggets",
        "chicken",
        "ground turkey",
    },
}
TYPICAL_FAMILY_STAPLE_TERMS = frozenset().union(*TYPICAL_FAMILY_STAPLES.values())

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


DINNER_MVP_MEALS = [
    {
        "name": "Rice and Peas Bowl",
        "minutes": 10,
        "effort": "low",
        "tags": {"low_energy", "picky", "vegetarian", "pantry", "leftovers", "nut_free", "dairy_free", "egg_free"},
        "ingredient_keywords": {"rice", "pea", "peas", "frozen peas", "bean", "beans"},
        "typical_family_staples": {"rice", "frozen peas", "beans"},
        "ingredients": "rice, frozen peas, and one simple add-on if you have it: olive oil, soy sauce, beans, or any protein",
        "steps": "Warm the rice and peas together. Season simply. Put any add-on on the side so kids can opt in.",
        "fallback": "If there is no add-on, warm the rice and peas together, season simply, and put any extra protein or sauce on the side.",
        "typical_family_bias": 12,
    },
    {
        "name": "Black Bean Tacos with fruit",
        "minutes": 15,
        "effort": "low",
        "tags": {"low_energy", "picky", "vegetarian", "pantry", "leftovers", "nut_free", "dairy_free", "egg_free"},
        "ingredient_keywords": {"tortilla", "tortillas", "bean", "beans", "black beans", "fruit", "avocado", "salsa"},
        "typical_family_staples": {"tortillas", "black beans", "salsa", "fruit"},
        "ingredients": "tortillas, black beans, mild salsa or avocado, and any fruit or crunchy side that fits your house",
        "steps": "Warm the beans. Fold them into tortillas with mild salsa or avocado. Serve fruit or a simple side.",
        "fallback": "If tortillas are missing, make quick bean-and-rice bowls with the same toppings.",
        "typical_family_bias": 8,
    },
    {
        "name": "Bean Rice Avocado Bowls",
        "minutes": 15,
        "effort": "low",
        "tags": {"low_energy", "picky", "vegetarian", "pantry", "leftovers", "nut_free", "egg_free"},
        "ingredient_keywords": {"bean", "beans", "black beans", "rice", "cheese", "avocado"},
        "typical_family_staples": {"beans", "rice", "cheese"},
        "ingredients": "canned beans, rice, cheese, avocado, and any mild salsa or crunchy side",
        "steps": "Warm the beans and rice. Add cheese and avocado on top, or keep toppings separate for kids.",
        "fallback": "If avocado is not usable, keep it as beans, rice, and cheese with fruit or a crunchy side.",
        "typical_family_bias": 14,
    },
    {
        "name": "Egg-and-cheese Tortilla Fold-ups",
        "minutes": 10,
        "effort": "low",
        "tags": {"low_energy", "picky", "vegetarian", "pantry", "nut_free"},
        "ingredient_keywords": {"tortilla", "tortillas", "egg", "eggs", "cheese"},
        "typical_family_staples": {"tortillas", "eggs", "cheese"},
        "ingredients": "tortillas, eggs, cheese, and any mild fruit or vegetable side",
        "steps": "Scramble the eggs. Fold eggs and cheese into warmed tortillas. Keep sauce or extras on the side.",
        "fallback": "If eggs are out, make cheese quesadillas with fruit or a simple side.",
        "typical_family_bias": 30,
    },
    {
        "name": "Cheese Quesadillas with fruit",
        "minutes": 10,
        "effort": "low",
        "tags": {"low_energy", "picky", "vegetarian", "pantry", "nut_free", "egg_free"},
        "ingredient_keywords": {"tortilla", "tortillas", "cheese", "fruit"},
        "typical_family_staples": {"tortillas", "cheese", "fruit"},
        "ingredients": "tortillas, cheese, and fruit or any simple crunchy side",
        "steps": "Melt cheese inside folded tortillas. Cut into triangles and put fruit or a crunchy side next to it.",
        "fallback": "If tortillas are out, melt cheese on toast or serve cheese, crackers, and fruit as a snack-plate dinner.",
        "typical_family_bias": 24,
    },
    {
        "name": "Egg Fried Rice with peas",
        "minutes": 20,
        "effort": "normal",
        "tags": {"fast", "picky", "pantry", "leftovers", "dairy_free", "nut_free"},
        "ingredient_keywords": {"rice", "egg", "eggs", "pea", "peas", "frozen peas", "vegetable", "vegetables"},
        "typical_family_staples": {"rice", "eggs", "frozen peas"},
        "ingredients": "rice, eggs, frozen peas or another vegetable that fits your house, and a light sauce",
        "steps": "Scramble the eggs. Stir-fry rice with peas. Keep sauce mild for kids; add grown-up heat at the table.",
        "fallback": "If eggs are out, make quick vegetable fried rice with beans, tofu, or another protein you have.",
        "typical_family_bias": 22,
    },
    {
        "name": "Pasta Marinara with carrots",
        "minutes": 25,
        "effort": "normal",
        "tags": {"picky", "vegetarian", "nut_free"},
        "ingredient_keywords": {"pasta", "marinara", "jar sauce", "sauce", "carrot", "carrots", "vegetable", "vegetables", "cheese"},
        "typical_family_staples": {"pasta", "marinara", "carrots", "cheese"},
        "ingredients": "pasta, jarred marinara, carrots or another simple vegetable, and optional cheese",
        "steps": "Boil the pasta. Warm the sauce with shredded carrots or a side vegetable. Keep toppings optional.",
        "fallback": "If pasta is missing, serve the sauce over toast, rice, or any grain you already have.",
        "typical_family_bias": 42,
    },
    {
        "name": "Cheesy Pasta with carrots",
        "minutes": 15,
        "effort": "low",
        "tags": {"low_energy", "picky", "vegetarian", "nut_free", "egg_free"},
        "ingredient_keywords": {"pasta", "cheese", "carrot", "carrots"},
        "typical_family_staples": {"pasta", "cheese", "carrots"},
        "ingredients": "pasta, cheese, butter or olive oil, and carrots or fruit on the side",
        "steps": "Boil pasta, toss with a little butter or oil and cheese, and serve carrots or fruit on the side.",
        "fallback": "If cheese is not usable, toss pasta with olive oil and a simple side instead.",
        "typical_family_bias": 30,
    },
    {
        "name": "Sheet-pan chicken and corn rice bowls",
        "minutes": 30,
        "effort": "can cook",
        "tags": {"can_cook", "leftovers", "dairy_free", "nut_free"},
        "ingredient_keywords": {"chicken", "protein", "rice", "corn", "beans"},
        "typical_family_staples": {"chicken", "rice", "corn"},
        "ingredients": "chicken or another protein that fits your house, rice, corn, and a mild topping",
        "steps": "Cook the protein and corn together. Serve over rice. Keep sauces on the side.",
        "fallback": "If chicken is missing, use beans, eggs, or leftovers as the bowl protein.",
        "typical_family_bias": 30,
    },
    {
        "name": "Chicken Rice Veggie Bowls",
        "minutes": 15,
        "effort": "low",
        "tags": {"low_energy", "picky", "leftovers", "dairy_free", "nut_free", "egg_free"},
        "ingredient_keywords": {"chicken", "rice", "carrot", "carrots", "vegetable", "vegetables", "veggie", "veggies", "frozen vegetables", "frozen veggies"},
        "typical_family_staples": {"chicken", "rice", "carrots", "frozen vegetables"},
        "ingredients": "cooked chicken or rotisserie-style chicken, rice, and carrots or frozen vegetables",
        "steps": "Warm chicken and rice together. Add carrots or frozen vegetables, keeping sauce optional at the table.",
        "fallback": "If chicken is not cooked, use nuggets, beans, or another quick protein with the same rice bowl base.",
        "typical_family_bias": 18,
    },
    {
        "name": "Chicken and Potato Tray Dinner",
        "minutes": 35,
        "effort": "can cook",
        "tags": {"can_cook", "leftovers", "dairy_free", "nut_free", "egg_free"},
        "ingredient_keywords": {"chicken", "potato", "potatoes"},
        "typical_family_staples": {"chicken", "potatoes"},
        "ingredients": "chicken thighs, potatoes, oil, salt, and any simple vegetable or fruit on the side",
        "steps": "Roast chicken and potato chunks on one tray until the potatoes are tender and the chicken is cooked through. Keep seasoning mild and add grown-up sauce at the table.",
        "fallback": "If potatoes are short, serve the chicken with rice, toast, or any freezer vegetable you have.",
        "typical_family_bias": 20,
    },
    {
        "name": "Turkey Pasta Skillet",
        "minutes": 25,
        "effort": "normal",
        "tags": {"picky", "nut_free", "egg_free"},
        "ingredient_keywords": {"turkey", "ground turkey", "pasta", "jar sauce", "sauce", "marinara"},
        "typical_family_staples": {"ground turkey", "pasta", "jar sauce"},
        "ingredients": "ground turkey, pasta, jarred sauce, and optional cheese or frozen vegetables",
        "steps": "Brown the turkey, stir in jarred sauce, and toss with cooked pasta. Keep toppings optional.",
        "fallback": "If turkey is missing, make the same pasta with beans, tofu, or just sauce and cheese.",
        "typical_family_bias": 28,
    },
    {
        "name": "Tofu or Paneer Veggie Rice Bowl",
        "minutes": 20,
        "effort": "normal",
        "tags": {"picky", "vegetarian", "pantry", "leftovers", "nut_free", "egg_free"},
        "ingredient_keywords": {"tofu", "paneer", "rice", "vegetable", "vegetables", "veggie", "veggies", "frozen veggies", "frozen vegetables"},
        "typical_family_staples": {"rice", "frozen vegetables"},
        "ingredients": "tofu or paneer, rice, frozen vegetables, and a mild sauce or seasoning",
        "steps": "Warm the rice and vegetables. Crisp or warm the tofu/paneer separately. Keep sauce mild and optional.",
        "fallback": "If tofu or paneer is missing, use eggs, beans, or any leftover protein with the same rice bowl base.",
        "typical_family_bias": 10,
    },
    {
        "name": "Crispy Chicken Wraps with salad",
        "minutes": 15,
        "effort": "low",
        "tags": {"low_energy", "picky", "nut_free", "egg_free"},
        "ingredient_keywords": {"nugget", "nuggets", "crispy chicken", "tortilla", "tortillas", "salad", "salad kit", "bagged salad"},
        "typical_family_staples": {"nuggets", "tortillas", "salad kit"},
        "ingredients": "frozen nuggets or crispy chicken, tortillas, and a bagged salad kit or crunchy side",
        "steps": "Heat the nuggets. Wrap them in tortillas with a little salad kit, or serve everything deconstructed for a picky kid.",
        "fallback": "If tortillas are out, make nugget-and-salad plates with toast, crackers, or fruit.",
        "typical_family_bias": 32,
    },
    {
        "name": "Chicken Nugget Plates",
        "minutes": 12,
        "effort": "low",
        "tags": {"low_energy", "picky", "nut_free", "egg_free"},
        "ingredient_keywords": {"nugget", "nuggets", "crispy chicken", "salad", "salad kit", "bagged salad", "fruit", "crackers"},
        "typical_family_staples": {"nuggets", "fruit", "crackers"},
        "ingredients": "frozen nuggets, fruit, crackers, or any crunchy side",
        "steps": "Heat the nuggets and make simple kid plates with fruit, crackers, or a crunchy side. Keep sauces optional.",
        "fallback": "If fruit is out, use crackers, toast, carrots, or whatever crunchy side is easiest.",
        "typical_family_bias": 18,
    },
    {
        "name": "Buttered Pea Noodles",
        "minutes": 15,
        "effort": "low",
        "tags": {"low_energy", "picky", "vegetarian", "nut_free", "egg_free"},
        "ingredient_keywords": {"pasta", "noodles", "frozen peas", "pea", "peas", "cheese"},
        "typical_family_staples": {"pasta", "frozen peas", "cheese"},
        "ingredients": "pasta or noodles, frozen peas, butter or olive oil, and optional cheese",
        "steps": "Boil noodles and peas together, then toss with butter or olive oil. Add cheese only if it fits.",
        "fallback": "If peas are out, use carrots, corn, or any simple vegetable side.",
        "typical_family_bias": 18,
    },
    {
        "name": "Pasta Bean Marinara Bowls",
        "minutes": 20,
        "effort": "low",
        "tags": {"low_energy", "picky", "vegetarian", "pantry", "nut_free", "egg_free"},
        "ingredient_keywords": {"pasta", "beans", "bean", "black beans", "marinara", "jar sauce", "sauce"},
        "typical_family_staples": {"pasta", "beans", "marinara"},
        "ingredients": "pasta, canned beans, and jarred marinara",
        "steps": "Warm beans in marinara while pasta cooks. Keep beans on the side if kids are skeptical.",
        "fallback": "If sauce is out, make cheesy pasta or rice-and-bean bowls instead.",
        "typical_family_bias": 16,
    },
    {
        "name": "Tortilla Pizza Triangles",
        "minutes": 12,
        "effort": "low",
        "tags": {"low_energy", "picky", "vegetarian", "pantry", "nut_free", "egg_free"},
        "ingredient_keywords": {"tortilla", "tortillas", "cheese", "marinara", "jar sauce", "sauce"},
        "typical_family_staples": {"tortillas", "cheese", "marinara"},
        "ingredients": "tortillas, a little marinara or jar sauce, and cheese",
        "steps": "Make quick tortilla pizzas in a pan or oven. Cut into triangles and keep toppings plain.",
        "fallback": "If sauce is missing, make cheese quesadillas instead.",
        "typical_family_bias": 20,
    },
    {
        "name": "Grilled Cheese and Fruit Plates",
        "minutes": 12,
        "effort": "low",
        "tags": {"low_energy", "picky", "vegetarian", "nut_free", "egg_free"},
        "ingredient_keywords": {"bread", "toast", "cheese", "fruit", "carrot", "carrots"},
        "typical_family_staples": {"bread", "cheese", "fruit", "carrots"},
        "ingredients": "bread, cheese, and fruit or carrots",
        "steps": "Make grilled cheese or cheese toast and add fruit or carrots beside it.",
        "fallback": "If bread is out, make cheese quesadillas or a crackers-and-cheese plate.",
        "typical_family_bias": 22,
    },
    {
        "name": "Snack Plate Dinner",
        "minutes": 8,
        "effort": "low",
        "tags": {"low_energy", "picky", "vegetarian", "nut_free", "egg_free"},
        "ingredient_keywords": {"cheese", "crackers", "fruit", "carrot", "carrots", "cucumber", "cucumbers", "yogurt"},
        "typical_family_staples": {"cheese", "crackers", "fruit", "carrots", "yogurt"},
        "ingredients": "cheese, crackers, fruit, carrots, yogurt, or whatever snacky bits are easiest",
        "steps": "Make kid plates with 3–4 easy items. Put anything unfamiliar in a tiny optional pile.",
        "fallback": "If dairy is out, use crackers, fruit, carrots, beans, or nuggets as the anchor.",
        "typical_family_bias": 16,
    },
    {
        "name": "Turkey Rice Taco Bowls",
        "minutes": 25,
        "effort": "normal",
        "tags": {"picky", "nut_free", "egg_free"},
        "ingredient_keywords": {"ground turkey", "turkey", "rice", "corn", "beans", "bean", "salsa", "cheese"},
        "typical_family_staples": {"ground turkey", "rice", "corn", "beans"},
        "ingredients": "ground turkey, rice, corn, beans, and optional salsa or cheese",
        "steps": "Cook turkey, warm rice/corn/beans, and serve as mild bowls with toppings separate.",
        "fallback": "If turkey is out, use beans, eggs, tofu, or leftover chicken as the protein.",
        "typical_family_bias": 18,
    },
    {
        "name": "Turkey Cheese Quesadilla Plates",
        "minutes": 18,
        "effort": "low",
        "tags": {"low_energy", "picky", "nut_free", "egg_free"},
        "ingredient_keywords": {"ground turkey", "turkey", "tortilla", "tortillas", "cheese", "fruit"},
        "typical_family_staples": {"ground turkey", "tortillas", "cheese", "fruit"},
        "ingredients": "ground turkey, tortillas, cheese, and fruit or a simple side",
        "steps": "Cook turkey quickly, tuck into cheese quesadillas, and serve fruit on the side.",
        "fallback": "If tortillas are out, serve turkey and cheese over rice or with crackers.",
        "typical_family_bias": 16,
    },
    {
        "name": "Chicken Cheese Quesadilla Plates",
        "minutes": 15,
        "effort": "low",
        "tags": {"low_energy", "picky", "leftovers", "nut_free", "egg_free"},
        "ingredient_keywords": {"chicken", "tortilla", "tortillas", "cheese", "fruit"},
        "typical_family_staples": {"chicken", "tortillas", "cheese", "fruit"},
        "ingredients": "cooked chicken, tortillas, cheese, and fruit or a crunchy side",
        "steps": "Warm chicken in cheese quesadillas. Cut into triangles and keep sauce optional.",
        "fallback": "If chicken is raw or not ready, use cheese-only quesadillas or nuggets.",
        "typical_family_bias": 14,
    },
    {
        "name": "Chicken Corn Rice Soup Bowls",
        "minutes": 25,
        "effort": "normal",
        "tags": {"picky", "leftovers", "dairy_free", "nut_free", "egg_free"},
        "ingredient_keywords": {"chicken", "rice", "corn", "carrot", "carrots"},
        "typical_family_staples": {"chicken", "rice", "corn", "carrots"},
        "ingredients": "chicken, rice, corn, carrots, and broth or water with seasoning",
        "steps": "Simmer chicken, rice, corn, and carrots into a simple bowl. Keep broth light for kids.",
        "fallback": "If broth is not around, make chicken rice bowls instead.",
        "typical_family_bias": 12,
    },
    {
        "name": "Potato Egg Hash",
        "minutes": 20,
        "effort": "normal",
        "tags": {"picky", "vegetarian", "pantry", "nut_free"},
        "ingredient_keywords": {"potato", "potatoes", "egg", "eggs", "cheese"},
        "typical_family_staples": {"potatoes", "eggs", "cheese"},
        "ingredients": "potatoes, eggs, and optional cheese",
        "steps": "Crisp small potato pieces, then add scrambled or fried eggs. Keep cheese optional.",
        "fallback": "If eggs are out, make potato cheese skillet or potato wedges with fruit.",
        "typical_family_bias": 14,
    },
    {
        "name": "Salmon Rice Pea Plates",
        "minutes": 25,
        "effort": "normal",
        "tags": {"dairy_free", "nut_free", "egg_free"},
        "ingredient_keywords": {"salmon", "rice", "frozen peas", "pea", "peas"},
        "typical_family_staples": {"rice", "frozen peas"},
        "ingredients": "salmon, rice, and frozen peas",
        "steps": "Cook salmon simply, warm rice and peas, and serve sauce separately for adults.",
        "fallback": "If salmon is out, use chicken, tofu, beans, or eggs with the same rice-and-peas base.",
        "typical_family_bias": 4,
    },
    {
        "name": "Bacon Egg Tortilla Tacos",
        "minutes": 15,
        "effort": "low",
        "tags": {"low_energy", "picky", "pantry", "nut_free"},
        "ingredient_keywords": {"bacon", "egg", "eggs", "tortilla", "tortillas", "cheese"},
        "typical_family_staples": {"eggs", "tortillas", "cheese"},
        "ingredients": "bacon, eggs, tortillas, and optional cheese",
        "steps": "Scramble eggs and tuck into tortillas with bacon. Keep cheese optional.",
        "fallback": "If bacon is out, make egg-and-cheese tortilla fold-ups.",
        "typical_family_bias": 8,
    },
    {
        "name": "Edamame Rice Bowls",
        "minutes": 15,
        "effort": "low",
        "tags": {"low_energy", "picky", "vegetarian", "pantry", "dairy_free", "nut_free", "egg_free"},
        "ingredient_keywords": {"edamame", "rice", "frozen vegetables", "frozen veggies", "vegetable", "vegetables"},
        "typical_family_staples": {"rice", "frozen vegetables"},
        "ingredients": "rice, edamame, and frozen vegetables",
        "steps": "Warm rice, edamame, and vegetables. Keep sauce mild and optional.",
        "fallback": "If edamame is out, use peas, beans, tofu, or eggs if allowed.",
        "typical_family_bias": 8,
    },
    {
        "name": "Sweet Potato Bean Bowls",
        "minutes": 25,
        "effort": "normal",
        "tags": {"vegetarian", "pantry", "dairy_free", "nut_free", "egg_free"},
        "ingredient_keywords": {"sweet potato", "potato", "potatoes", "bean", "beans", "black beans", "corn", "avocado"},
        "typical_family_staples": {"potatoes", "beans", "corn"},
        "ingredients": "sweet potatoes or potatoes, beans, corn, and optional avocado",
        "steps": "Roast or microwave potato pieces, warm beans and corn, and serve as separate bowl parts.",
        "fallback": "If potatoes are out, use rice as the base.",
        "typical_family_bias": 8,
    },
    {
        "name": "Parotta Egg Roll-Ups",
        "minutes": 15,
        "effort": "low",
        "tags": {"low_energy", "picky", "vegetarian", "pantry", "nut_free"},
        "ingredient_keywords": {"parotta", "egg", "eggs", "cheese"},
        "typical_family_staples": {"eggs", "cheese"},
        "ingredients": "frozen parotta, eggs, and optional cheese",
        "steps": "Heat parotta, add scrambled egg, and roll it up. Keep sauce optional.",
        "fallback": "If parotta is out, use tortillas or toast.",
        "typical_family_bias": 4,
    },
    {
        "name": "Paneer Tortilla Melts",
        "minutes": 15,
        "effort": "low",
        "tags": {"low_energy", "picky", "vegetarian", "pantry", "nut_free", "egg_free"},
        "ingredient_keywords": {"paneer", "tortilla", "tortillas", "cheese", "frozen vegetables", "frozen veggies"},
        "typical_family_staples": {"tortillas", "cheese", "frozen vegetables"},
        "ingredients": "paneer, tortillas, cheese, and optional frozen vegetables",
        "steps": "Warm paneer and fold into tortillas with a little cheese. Keep spices mild.",
        "fallback": "If paneer is out, use tofu, beans, or cheese-only quesadillas.",
        "typical_family_bias": 6,
    },
    {
        "name": "Tofu Veggie Noodles",
        "minutes": 20,
        "effort": "normal",
        "tags": {"picky", "vegetarian", "dairy_free", "nut_free", "egg_free"},
        "ingredient_keywords": {"tofu", "pasta", "noodles", "frozen vegetables", "frozen veggies", "vegetable", "vegetables"},
        "typical_family_staples": {"pasta", "frozen vegetables"},
        "ingredients": "tofu, noodles or pasta, frozen vegetables, and a mild sauce",
        "steps": "Warm tofu and vegetables, toss with noodles, and keep sauce mild.",
        "fallback": "If tofu is out, use edamame, beans, chicken, or eggs if allowed.",
        "typical_family_bias": 6,
    },
    {
        "name": "Tuna Pasta Plates",
        "minutes": 15,
        "effort": "low",
        "tags": {"low_energy", "picky", "dairy_free", "nut_free", "egg_free"},
        "ingredient_keywords": {"tuna", "pasta", "pea", "peas", "frozen peas"},
        "typical_family_staples": {"pasta", "frozen peas"},
        "ingredients": "pasta, canned tuna, frozen peas, and olive oil or a mild dressing",
        "steps": "Cook pasta and peas, then fold in tuna. Keep it plain or deconstructed for kids.",
        "fallback": "If tuna is out, use beans, chicken, or cheese if allowed.",
        "typical_family_bias": 6,
    },
    {
        "name": "Avocado Egg Toast Plates",
        "minutes": 12,
        "effort": "low",
        "tags": {"low_energy", "picky", "vegetarian", "nut_free"},
        "ingredient_keywords": {"avocado", "egg", "eggs", "bread", "toast", "fruit"},
        "typical_family_staples": {"eggs", "bread", "fruit"},
        "ingredients": "eggs, bread or toast, avocado, and fruit",
        "steps": "Make eggs and toast. Add avocado for whoever wants it and fruit on the side.",
        "fallback": "If avocado is out, keep it eggs, toast, and fruit.",
        "typical_family_bias": 10,
    },
    {
        "name": "Yogurt Oat Fruit Bowls",
        "minutes": 8,
        "effort": "low",
        "tags": {"low_energy", "picky", "vegetarian", "nut_free", "egg_free"},
        "ingredient_keywords": {"yogurt", "oats", "cereal", "fruit", "berries", "banana", "bananas"},
        "typical_family_staples": {"yogurt", "oats", "cereal", "fruit", "bananas"},
        "ingredients": "yogurt, oats or cereal, and fruit",
        "steps": "Make yogurt bowls with oats/cereal and fruit. Call it breakfast-for-dinner if needed.",
        "fallback": "If yogurt is out, make snack plates or toast with fruit.",
        "typical_family_bias": 8,
    },
    {
        "name": "Corn Bean Quesadillas",
        "minutes": 15,
        "effort": "low",
        "tags": {"low_energy", "picky", "vegetarian", "pantry", "nut_free", "egg_free"},
        "ingredient_keywords": {"corn", "bean", "beans", "black beans", "tortilla", "tortillas", "cheese"},
        "typical_family_staples": {"corn", "beans", "tortillas", "cheese"},
        "ingredients": "corn, beans, tortillas, and optional cheese",
        "steps": "Warm corn and beans, fold into tortillas with cheese if allowed, and keep fillings light for kids.",
        "fallback": "If tortillas are out, serve corn and beans over rice.",
        "typical_family_bias": 10,
    },
    {
        "name": "Cream Cheese Cucumber Wraps",
        "minutes": 10,
        "effort": "low",
        "tags": {"low_energy", "picky", "vegetarian", "nut_free", "egg_free"},
        "ingredient_keywords": {"cream cheese", "cheese", "cucumber", "cucumbers", "tortilla", "tortillas", "bread"},
        "typical_family_staples": {"tortillas", "cheese", "bread"},
        "ingredients": "cream cheese, cucumbers, tortillas or bread",
        "steps": "Spread cream cheese on tortillas or bread, add cucumber if available, and roll or cut into small pieces.",
        "fallback": "If cucumbers are out, make plain cream-cheese roll-ups with fruit.",
        "typical_family_bias": 4,
    },
    {
        "name": "Chicken Salad Crackers Plate",
        "minutes": 12,
        "effort": "low",
        "tags": {"low_energy", "picky", "leftovers", "nut_free", "egg_free"},
        "ingredient_keywords": {"chicken", "salad", "salad kit", "bagged salad", "crackers", "fruit"},
        "typical_family_staples": {"chicken", "salad kit", "crackers", "fruit"},
        "ingredients": "cooked chicken, salad kit, crackers, and fruit",
        "steps": "Make deconstructed plates: chicken, crackers, fruit, and optional salad for whoever wants it.",
        "fallback": "If chicken is not cooked, use nuggets, cheese, tuna, or beans as the plate anchor.",
        "typical_family_bias": 8,
    },
    {
        "name": "Potato Cheese Skillet",
        "minutes": 20,
        "effort": "normal",
        "tags": {"picky", "vegetarian", "pantry", "nut_free", "egg_free"},
        "ingredient_keywords": {"potato", "potatoes", "cheese", "corn"},
        "typical_family_staples": {"potatoes", "cheese", "corn"},
        "ingredients": "potatoes, cheese, and corn or another simple side",
        "steps": "Crisp potato pieces, add corn if useful, and melt cheese on top or serve it separately.",
        "fallback": "If cheese is out, make potato wedges with fruit or beans.",
        "typical_family_bias": 8,
    },
    {
        "name": "Pasta Pea Cheese Bowls",
        "minutes": 15,
        "effort": "low",
        "tags": {"low_energy", "picky", "vegetarian", "nut_free", "egg_free"},
        "ingredient_keywords": {"pasta", "pea", "peas", "frozen peas", "cheese"},
        "typical_family_staples": {"pasta", "frozen peas", "cheese"},
        "ingredients": "pasta, frozen peas, and cheese",
        "steps": "Cook pasta and peas together, then add cheese lightly or keep it on the side.",
        "fallback": "If cheese is out, use olive oil or butter if allowed.",
        "typical_family_bias": 12,
    },
]


class DinnerDecisionSession:
    """Small Chapter 1 MVP flow that uses only current-turn parent input."""

    def __init__(self):
        self.current_recommendation: dict[str, Any] | None = None
        self.last_context: dict[str, Any] | None = None
        self.rejected: set[str] = set()

    def send(self, parent_message: str, scenario: str | None = None) -> dict[str, Any]:
        accepted = False
        context = parse_dinner_decision_context(parent_message)
        if self.last_context:
            context = {**self.last_context, **{key: value for key, value in context.items() if value}}

        feedback = _dinner_feedback(parent_message)
        if feedback and self.current_recommendation:
            if feedback in {"too_much_work", "kid_wont_eat", "missing_ingredient", "backup"}:
                rejected_meal = self.current_recommendation
                already_minimal = feedback == "too_much_work" and rejected_meal["minutes"] <= 10 and rejected_meal["effort"] == "low"
                if not already_minimal:
                    self.rejected.add(self.current_recommendation["name"])
                if feedback == "too_much_work":
                    context["fallback_relief"] = True
                    context["fallback_already_minimal"] = already_minimal
                    context["rejected_minutes"] = rejected_meal["minutes"]
                    context["rejected_effort"] = rejected_meal["effort"]
                    context["energy"] = "barely cooking"
                    context["minutes"] = min(context.get("minutes") or 20, 15)
                if feedback == "kid_wont_eat":
                    context["picky"] = True
                if feedback == "missing_ingredient":
                    context["use_current_input"] = True
                recommendation = choose_dinner_decision(context, self.rejected)
                self.current_recommendation = recommendation
                self.last_context = context
                message = format_dinner_decision(recommendation, context, prefix="Backup:")
            else:
                accepted = True
                message = f"Good enough counts. Dinner decided: {self.current_recommendation['name']}."
        else:
            recommendation = choose_dinner_decision(context, self.rejected)
            self.current_recommendation = recommendation
            self.last_context = context
            message = format_dinner_decision(recommendation, context)

        return {
            "parent_message": parent_message,
            "message": message,
            "trace": [],
            "grocery_items": [],
            "metadata": {
                "scenario": scenario,
                "chapter": "chapter_1_dinner_decision",
                "current_recommendation": (
                    self.current_recommendation["name"] if self.current_recommendation else None
                ),
                "allergy_caveat": _needs_allergy_caveat(context),
                "accepted": accepted,
            },
        }


def create_dinner_decision_session() -> DinnerDecisionSession:
    return DinnerDecisionSession()


def parse_dinner_decision_context(parent_message: str) -> dict[str, Any]:
    message = parent_message.lower().replace("’", "'")
    minutes = None
    minute_match = re.search(r"(?<![a-z0-9])(\d{1,2})\s*(?:min|mins|minute|minutes)(?![a-z0-9])", message)
    if minute_match:
        parsed_minutes = int(minute_match.group(1))
        if 5 <= parsed_minutes <= 60:
            minutes = parsed_minutes
    elif any(phrase in message for phrase in ("ten minutes",)):
        minutes = 10
    elif any(phrase in message for phrase in ("fifteen minutes",)):
        minutes = 15
    elif any(phrase in message for phrase in ("twenty minutes",)):
        minutes = 20
    elif any(phrase in message for phrase in ("thirty minutes",)):
        minutes = 30

    avoid_terms = _parse_avoid_terms(message)
    excluded_ingredients = _parse_excluded_ingredients(message)
    blocked_ingredients = _expanded_blocked_ingredients(avoid_terms, excluded_ingredients)
    positive_ingredients = [term for term in _parse_positive_ingredients(message) if term not in blocked_ingredients]

    return {
        "minutes": minutes,
        "energy": _parse_energy(message),
        "picky": any(phrase in message for phrase in ("picky", "kid friendly", "kid-friendly", "familiar", "kids may eat")),
        "vegetarian": _has_word(message, "vegetarian"),
        "nut_free": any(term in avoid_terms for term in ("peanut", "nut")),
        "dairy_free": any(term in avoid_terms for term in ("dairy", "milk", "cheese", "yogurt")),
        "egg_free": "egg" in avoid_terms,
        "leftovers": _has_word(message, "leftover") or _has_word(message, "leftovers"),
        "pantry": any(phrase in message for phrase in ("pantry", "freezer", "use what", "already have", "no grocery", "no store run", "no shopping")),
        "only_have": _has_only_have_signal(message),
        "avoid_terms": avoid_terms,
        "excluded_ingredients": excluded_ingredients,
        "positive_ingredients": positive_ingredients,
        "free_text": parent_message.strip(),
    }


def choose_dinner_decision(context: dict[str, Any], rejected: set[str] | None = None) -> dict[str, Any]:
    rejected = rejected or set()
    candidates = [meal for meal in DINNER_MVP_MEALS if meal["name"] not in rejected] or DINNER_MVP_MEALS[:]

    def score(meal: dict[str, Any]) -> int:
        tags = meal["tags"]
        value = 0
        minutes = context.get("minutes")
        if minutes:
            value += 35 if meal["minutes"] <= minutes else -25
        if context.get("energy") == "barely cooking":
            value += 35 if meal["effort"] == "low" else -20
        elif context.get("energy") == "can cook":
            value += 35 if meal["effort"] == "can cook" else -6
        if context.get("picky"):
            value += 30 if "picky" in tags else -10
        if context.get("vegetarian"):
            value += 40 if "vegetarian" in tags else -60
        if context.get("nut_free"):
            value += 15 if "nut_free" in tags else -60
        if context.get("dairy_free"):
            value += 35 if "dairy_free" in tags else -60
        if context.get("egg_free"):
            value += 35 if "egg_free" in tags else -80
        blocked_ingredients = _expanded_blocked_ingredients(
            context.get("avoid_terms", []), context.get("excluded_ingredients", [])
        )
        if _meal_mentions_avoided_term(meal, context.get("avoid_terms", [])):
            value -= 1000
        if _meal_mentions_excluded_ingredient(meal, blocked_ingredients):
            value -= 1000
        positive_ingredients = context.get("positive_ingredients", [])
        matched_ingredients = _matching_positive_ingredients(meal, positive_ingredients)
        if meal["name"] == "Rice and Peas Bowl" and not (
            context.get("only_have")
            or context.get("fallback_relief")
            or context.get("pantry")
            or context.get("leftovers")
            or len(matched_ingredients) >= 2
        ):
            value -= 80
        value += 42 * len(matched_ingredients)
        if len(matched_ingredients) >= 2:
            value += 35
        if positive_ingredients and not matched_ingredients:
            value -= 35
        cooked_chicken_meals = {
            "Chicken Rice Veggie Bowls",
            "Chicken Cheese Quesadilla Plates",
            "Chicken Salad Crackers Plate",
        }
        if meal["name"] in cooked_chicken_meals and "chicken" in positive_ingredients:
            text = context.get("free_text", "").lower()
            if not (context.get("leftovers") or any(word in text for word in ("cooked chicken", "rotisserie", "leftover chicken", "nugget", "nuggets"))):
                value -= 70
        if context.get("only_have"):
            value += 60 * len(matched_ingredients)
            unmatched_count = max(0, len(context.get("positive_ingredients", [])) - len(matched_ingredients))
            value -= 20 * unmatched_count
            if not matched_ingredients:
                value -= 120
        if context.get("fallback_relief"):
            rejected_minutes = context.get("rejected_minutes") or 30
            rejected_effort = context.get("rejected_effort")
            if meal["minutes"] < rejected_minutes:
                value += 45
            else:
                value -= 35
            if meal["minutes"] <= 15:
                value += 25
            if meal["effort"] == "low":
                value += 25
            if meal["name"] == "Rice and Peas Bowl":
                value += 35
            if rejected_effort == "low" and meal["minutes"] >= rejected_minutes:
                value -= 30
        if context.get("leftovers"):
            value += 20 if "leftovers" in tags else 0
        if context.get("pantry"):
            value += 20 if "pantry" in tags else -8
        if _uses_typical_family_baseline(context):
            assumed_matches = _matching_typical_family_staples(meal, blocked_ingredients)
            value += int(meal.get("typical_family_bias", 0))
            value += 7 * len(assumed_matches)
            if len(assumed_matches) >= 3:
                value += 12
            free_text = context.get("free_text", "").lower()
            if any(phrase in free_text for phrase in ("freezer", "nothing thawed", "no thawed")):
                value += 18 if {"nuggets", "frozen peas", "frozen vegetables", "chicken"} & set(assumed_matches) else -8
        value -= meal["minutes"] // 5
        return value

    return dict(max(candidates, key=score))


def format_dinner_decision(meal: dict[str, Any], context: dict[str, Any], prefix: str = "Tonight:") -> str:
    lines = [
        f"{prefix} {meal['name']}.",
    ]
    if prefix.startswith("Backup") and context.get("fallback_relief"):
        if context.get("fallback_already_minimal"):
            lines.append("Why this is easier: this is already the low-effort version — use this if cooking energy is gone.")
        else:
            lines.append("Why this is easier: faster and fewer steps — this is the low-effort version if cooking energy is gone.")
    lines.extend(
        [
            f"Why it fits: {dinner_fit_reason(meal, context)}",
            f"Time/effort: about {meal['minutes']} minutes, {_effort_label(meal['effort'])}.",
        ]
    )
    if context.get("only_have"):
        lines.append("Constraint heard: I am using the ingredients you listed first, not assuming a remembered pantry.")
    elif _uses_typical_family_baseline(context):
        lines.append("Assumption: using common family staples because you have not shared actual kitchen contents yet.")
    lines.extend(
        [
            f"Works with common basics like: {meal['ingredients']}.",
            f"Simple plan: {meal['steps']}",
            f"Fallback/tweak: {meal['fallback']}",
        ]
    )
    if _needs_allergy_caveat(context):
        lines.append(ALLERGY_CAVEAT)
    lines.append("One decision, not a recipe search.")
    return "\n".join(lines)


def _effort_label(effort: str) -> str:
    labels = {
        "low": "low effort",
        "normal": "normal effort",
        "can cook": "some cooking",
    }
    return labels.get(effort, f"{effort} effort")


def dinner_fit_reason(meal: dict[str, Any], context: dict[str, Any]) -> str:
    reasons = []
    matched_ingredients = _matching_positive_ingredients(meal, context.get("positive_ingredients", []))
    if matched_ingredients:
        reasons.append(f"Uses your {_human_join(_friendly_ingredient_terms(matched_ingredients))}")
    elif _uses_typical_family_baseline(context):
        assumed_matches = _matching_typical_family_staples(
            meal, _expanded_blocked_ingredients(context.get("avoid_terms", []), context.get("excluded_ingredients", []))
        )
        if assumed_matches:
            reasons.append(f"Leans on common family staples like {_human_join(_friendly_ingredient_terms(assumed_matches[:4]))}")
        else:
            reasons.append("Uses a conservative common-staples fallback")
    elif context.get("only_have"):
        reasons.append("Uses the sparse pantry constraint you gave")
    elif context.get("pantry"):
        reasons.append("Starts from pantry/freezer basics")

    if context.get("minutes"):
        if meal["minutes"] <= context["minutes"]:
            reasons.append(f"Fits about {meal['minutes']} minutes")
        else:
            reasons.append("Closest practical fit for tonight")
    else:
        reasons.append(f"About {meal['minutes']} minutes")

    if meal["effort"] == "low":
        reasons.append("Keeps effort low")
    elif context.get("energy") == "barely cooking":
        reasons.append("Still doable tonight")
    elif context.get("picky"):
        reasons.append("Easy to keep familiar for kids")

    if context.get("vegetarian"):
        reasons.append("Keeps it vegetarian")
    if context.get("dairy_free") or context.get("egg_free") or context.get("avoid_terms"):
        reasons.append("Respects the avoidances you flagged")
    elif context.get("excluded_ingredients"):
        reasons.append("Respects what you ruled out")
    if context.get("leftovers"):
        reasons.append("Works with leftovers")
    if not reasons:
        reasons.append("Fast, familiar, and low-decision for tonight")
    return "; ".join(dict.fromkeys(reasons)) + "."


def _uses_typical_family_baseline(context: dict[str, Any]) -> bool:
    return bool(
        not context.get("positive_ingredients")
        and not context.get("only_have")
        and not context.get("fallback_relief")
    )


def _matching_typical_family_staples(meal: dict[str, Any], avoid_terms: list[str]) -> list[str]:
    keywords = meal.get("typical_family_staples", meal.get("ingredient_keywords", set()))
    blocked = set(avoid_terms)
    if "dairy" in blocked:
        blocked.update({"milk", "cheese", "yogurt"})
    if "egg" in blocked:
        blocked.update({"egg", "eggs"})
    return sorted(term for term in TYPICAL_FAMILY_STAPLE_TERMS if term in keywords and term not in blocked)


def _friendly_ingredient_terms(terms: list[str]) -> list[str]:
    normalized_terms = list(terms)
    if "paneer" in normalized_terms and "tofu" in normalized_terms:
        normalized_terms = [term for term in normalized_terms if term not in {"paneer", "tofu"}]
        normalized_terms.append("tofu or paneer")
    friendly = []
    seen = set()
    names = {
        "egg": "eggs",
        "pea": "peas",
        "frozen peas": "frozen peas",
        "bean": "beans",
        "black beans": "black beans",
        "tortilla": "tortillas",
        "carrot": "carrots",
        "potato": "potatoes",
        "veggie": "vegetables",
        "veggies": "vegetables",
        "frozen veggies": "frozen vegetables",
        "nugget": "nuggets",
        "bagged salad": "salad kit",
        "jar sauce": "jarred sauce",
        "marinara": "marinara",
        "ground turkey": "ground turkey",
        "fruit": "fruit",
        "apples": "apples",
        "banana": "bananas",
        "bananas": "bananas",
        "berries": "berries",
        "bread": "bread",
        "toast": "toast",
        "crackers": "crackers",
        "cream cheese": "cream cheese",
        "cucumber": "cucumbers",
        "cucumbers": "cucumbers",
        "sweet potato": "sweet potato",
        "noodles": "noodles",
        "salad": "salad",
        "salad kit": "salad kit",
    }
    for term in normalized_terms:
        name = names.get(term, term)
        if name not in seen:
            seen.add(name)
            friendly.append(name)
    order = {"rice": 0, "eggs": 1, "frozen peas": 2, "peas": 3, "chicken": 4, "potatoes": 5}
    return sorted(friendly, key=lambda item: order.get(item, 99))


def _human_join(items: list[str]) -> str:
    if not items:
        return "ingredients"
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{', '.join(items[:-1])}, and {items[-1]}"


def _parse_avoid_terms(message: str) -> list[str]:
    terms: list[str] = []
    checks = {
        "peanut": ("peanut", "peanuts"),
        "nut": ("nut", "nuts", "tree nut", "tree nuts"),
        "dairy": ("dairy",),
        "milk": ("milk",),
        "cheese": ("cheese",),
        "yogurt": ("yogurt", "yoghurt"),
        "egg": ("egg", "eggs"),
        "spicy": ("spicy",),
    }
    for term, words in checks.items():
        if any(_has_avoidance_signal(message, word) for word in words):
            terms.append(term)
    return terms


def _parse_excluded_ingredients(message: str) -> list[str]:
    terms: list[str] = []
    for term in _known_dinner_terms():
        if _has_exclusion_signal(message, term):
            terms.append(term)
    return terms


def _known_dinner_terms() -> tuple[str, ...]:
    manual_terms = {
        "banana",
        "bananas",
        "bacon",
        "berries",
        "bread",
        "butter",
        "cereal",
        "cream cheese",
        "crackers",
        "cucumber",
        "cucumbers",
        "edamame",
        "noodles",
        "oats",
        "parotta",
        "salmon",
        "sweet potato",
        "toast",
        "tuna",
        "yogurt",
    }
    terms = set(TYPICAL_FAMILY_STAPLE_TERMS) | manual_terms
    for meal in DINNER_MVP_MEALS:
        terms.update(meal.get("ingredient_keywords", set()))
        terms.update(meal.get("typical_family_staples", set()))
    return tuple(sorted(terms, key=lambda term: (-len(term.split()), -len(term), term)))


def _has_exclusion_signal(message: str, term: str) -> bool:
    escaped = re.escape(term)
    patterns = (
        rf"(?<![a-z0-9])(no|without)\s+{escaped}(?![a-z0-9])",
        rf"(?<![a-z0-9])(don't|do not|dont|didn't|didnt)\s+have[^.?!;]*\b{escaped}\b",
        rf"(?<![a-z0-9])out\s+of\s+{escaped}(?![a-z0-9])",
        rf"(?<![a-z0-9])(hate|hates|won't eat|wont eat|will not eat)[^.?!;]*\b{escaped}\b",
        rf"(?<![a-z0-9]){escaped}[- ]free(?![a-z0-9])",
    )
    return any(re.search(pattern, message) for pattern in patterns)


def _expanded_blocked_ingredients(avoid_terms: list[str], excluded_ingredients: list[str]) -> set[str]:
    blocked = set(avoid_terms) | set(excluded_ingredients)
    expansions = {
        "dairy": {"milk", "cheese", "yogurt"},
        "egg": {"egg", "eggs"},
        "eggs": {"egg", "eggs"},
        "bean": {"bean", "beans", "black beans"},
        "beans": {"bean", "beans", "black beans"},
        "black beans": {"bean", "beans", "black beans"},
        "pea": {"pea", "peas", "frozen peas"},
        "peas": {"pea", "peas", "frozen peas"},
        "frozen peas": {"pea", "peas", "frozen peas"},
        "tortilla": {"tortilla", "tortillas"},
        "tortillas": {"tortilla", "tortillas"},
        "nugget": {"nugget", "nuggets"},
        "nuggets": {"nugget", "nuggets"},
        "potato": {"potato", "potatoes"},
        "potatoes": {"potato", "potatoes"},
        "sauce": {"sauce", "jar sauce", "marinara", "salsa"},
        "jar sauce": {"sauce", "jar sauce", "marinara"},
        "marinara": {"sauce", "jar sauce", "marinara"},
        "vegetable": {"vegetable", "vegetables", "veggie", "veggies", "frozen vegetables", "frozen veggies"},
        "vegetables": {"vegetable", "vegetables", "veggie", "veggies", "frozen vegetables", "frozen veggies"},
        "veggie": {"vegetable", "vegetables", "veggie", "veggies", "frozen vegetables", "frozen veggies"},
        "veggies": {"vegetable", "vegetables", "veggie", "veggies", "frozen vegetables", "frozen veggies"},
        "salad": {"salad", "salad kit", "bagged salad"},
        "salad kit": {"salad", "salad kit", "bagged salad"},
        "bagged salad": {"salad", "salad kit", "bagged salad"},
        "bread": {"bread", "toast"},
        "toast": {"bread", "toast"},
        "noodles": {"pasta", "noodles"},
        "pasta": {"pasta", "noodles"},
        "cream cheese": {"cream cheese", "cheese"},
        "cucumber": {"cucumber", "cucumbers"},
        "cucumbers": {"cucumber", "cucumbers"},
        "banana": {"banana", "bananas"},
        "bananas": {"banana", "bananas"},
    }
    for term in list(blocked):
        blocked.update(expansions.get(term, {term}))
    return blocked


def _has_avoidance_signal(message: str, word: str) -> bool:
    escaped = re.escape(word)
    patterns = (
        rf"(?<![a-z0-9])(avoid|avoiding|no|without)\s+{escaped}(?![a-z0-9])",
        rf"(?<![a-z0-9]){escaped}\s+(allergy|allergies)(?![a-z0-9])",
        rf"(?<![a-z0-9])allergic\s+to\s+{escaped}(?![a-z0-9])",
        rf"(?<![a-z0-9]){escaped}[- ]free(?![a-z0-9])",
    )
    return any(re.search(pattern, message) for pattern in patterns)


def _parse_positive_ingredients(message: str) -> list[str]:
    ingredients = []
    broad_inventory_context = any(
        phrase in message
        for phrase in (
            "leftover",
            "leftovers",
            "no store run",
            "no shopping",
            "use what",
            "already have",
            "what we have",
            "what i have",
        )
    )
    list_style_context = _has_inventory_list_signal(message) or _has_shorthand_ingredient_signal(message)
    for term in _known_dinner_terms():
        if term in ("pea", "peas") and "frozen peas" in ingredients:
            continue
        if term == "egg" and "eggs" in ingredients:
            continue
        if term == "tortilla" and "tortillas" in ingredients:
            continue
        if term == "potato" and "potatoes" in ingredients:
            continue
        if term == "nugget" and "nuggets" in ingredients:
            continue
        if term == "turkey" and "ground turkey" in ingredients:
            continue
        if term == "sauce" and "jar sauce" in ingredients:
            continue
        if term == "salad" and ("bagged salad" in ingredients or "salad kit" in ingredients):
            continue
        if term == "vegetables" and ("frozen vegetables" in ingredients or "frozen veggies" in ingredients):
            continue
        if term == "veggies" and ("frozen vegetables" in ingredients or "frozen veggies" in ingredients or "vegetables" in ingredients):
            continue
        if _has_positive_ingredient_signal(message, term) or ((broad_inventory_context or list_style_context) and _has_word(message, term)):
            ingredients.append(term)
    return ingredients


def _has_inventory_list_signal(message: str) -> bool:
    if message.count(",") >= 1:
        return True
    if " + " in message or " / " in message:
        return True
    return False


def _has_shorthand_ingredient_signal(message: str) -> bool:
    matches = [term for term in _known_dinner_terms() if _has_word(message, term)]
    return len(matches) >= 2


def _has_positive_ingredient_signal(message: str, term: str) -> bool:
    escaped = re.escape(term)
    patterns = (
        rf"(?<![a-z0-9])(i|we)\s+have[^.?!;]*\b{escaped}\b",
        rf"(?<![a-z0-9])(i|we)\s+only\s+have[^.?!;]*\b{escaped}\b",
        rf"(?<![a-z0-9])only\s+[^.?!;]*\b{escaped}\b",
        rf"(?<![a-z0-9])use[^.?!;]*\b{escaped}\b",
        rf"(?<![a-z0-9])leftover\s+{escaped}\b",
        rf"(?<![a-z0-9]){escaped}\s+in\s+the\s+(fridge|freezer|pantry)\b",
    )
    return any(re.search(pattern, message) for pattern in patterns)


def _has_only_have_signal(message: str) -> bool:
    return any(
        phrase in message
        for phrase in (
            "only have",
            "only got",
            "only rice",
            "only pasta",
            "only beans",
            "only tortillas",
        )
    )


def _matching_positive_ingredients(meal: dict[str, Any], positive_ingredients: list[str]) -> list[str]:
    if not positive_ingredients:
        return []
    keywords = meal.get("ingredient_keywords", set())
    return [term for term in positive_ingredients if term in keywords]


def _has_word(message: str, word: str) -> bool:
    pattern = r"(?<![a-z0-9])" + re.escape(word) + r"(?![a-z0-9])"
    return re.search(pattern, message) is not None


def _meal_mentions_avoided_term(meal: dict[str, Any], avoid_terms: list[str]) -> bool:
    if not avoid_terms:
        return False
    haystack = " ".join(str(meal.get(field, "")) for field in ("name", "ingredients", "steps", "fallback")).lower()
    blocked_words = {
        "peanut": ("peanut", "peanuts"),
        "nut": ("nut", "nuts", "tree nut", "tree nuts"),
        "dairy": ("dairy", "milk", "cheese", "yogurt", "yoghurt"),
        "milk": ("milk",),
        "cheese": ("cheese",),
        "yogurt": ("yogurt", "yoghurt"),
        "egg": ("egg", "eggs"),
        "spicy": ("spicy",),
    }
    for term in avoid_terms:
        if any(_has_word(haystack, word) for word in blocked_words.get(term, (term,))):
            return True
    return False


def _meal_mentions_excluded_ingredient(meal: dict[str, Any], blocked_ingredients: set[str]) -> bool:
    if not blocked_ingredients:
        return False
    haystack = " ".join(str(meal.get(field, "")) for field in ("name", "ingredients", "steps")).lower()
    return any(_has_word(haystack, term) for term in blocked_ingredients)


def _parse_energy(message: str) -> str | None:
    if any(
        phrase in message
        for phrase in (
            "barely cooking",
            "cooking energy is gone",
            "exhausted",
            "too much work",
            "need easier",
            "easiest",
            "lowest effort",
            "lowest-effort",
            "low effort",
            "no cooking",
            "not in the mood to cook",
            "not in mood to cook",
            "low cooking mood",
            "no brain left",
        )
    ):
        return "barely cooking"
    if "can cook" in message or "okay cooking" in message or "ok cooking" in message:
        return "can cook"
    if "normal" in message:
        return "normal"
    return None


def _needs_allergy_caveat(context: dict[str, Any]) -> bool:
    return bool(context.get("nut_free") or context.get("dairy_free") or context.get("avoid_terms"))


def _dinner_feedback(parent_message: str) -> str | None:
    normalized = parent_message.lower().replace("’", "'")
    if "good enough" in normalized or "works" in normalized:
        return "accepted"
    if any(
        phrase in normalized
        for phrase in (
            "too much work",
            "too much cooking",
            "barely cooking",
            "need easier",
            "i need easier",
            "easier than",
            "make it easier",
            "no cooking",
            "only have 10 minutes",
            "only 10 minutes",
        )
    ):
        return "too_much_work"
    if any(phrase in normalized for phrase in ("kid won't eat", "kid wont eat", "kids won't eat", "kids wont eat")):
        return "kid_wont_eat"
    if "missing ingredient" in normalized or "don't have" in normalized or "do not have" in normalized:
        return "missing_ingredient"
    if "backup" in normalized or "fallback" in normalized or "give me backup" in normalized:
        return "backup"
    return None


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
