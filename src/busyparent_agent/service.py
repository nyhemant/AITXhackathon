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
        "ingredient_keywords": {"rice", "pea", "peas", "frozen peas"},
        "ingredients": "rice, frozen peas, and one simple add-on if you have it: olive oil, soy sauce, beans, or any protein",
        "steps": "Warm the rice and peas together, season simply, and put any add-on on the side so kids can opt in.",
        "fallback": "If there is no add-on, this can still be the simplest dinner from only the rice and peas you listed.",
    },
    {
        "name": "Black Bean Tacos with fruit",
        "minutes": 15,
        "effort": "low",
        "tags": {"low_energy", "picky", "vegetarian", "pantry", "leftovers", "nut_free", "dairy_free", "egg_free"},
        "ingredient_keywords": {"tortilla", "tortillas", "bean", "beans", "black beans", "fruit", "avocado", "salsa"},
        "ingredients": "tortillas, black beans, mild salsa or avocado, and any fruit or crunchy side that fits your house",
        "steps": "Warm beans, fold them into tortillas with mild salsa or avocado, and serve fruit or a simple side.",
        "fallback": "If tortillas are missing, make quick bean-and-rice bowls with the same toppings.",
    },
    {
        "name": "Egg Fried Rice with peas",
        "minutes": 20,
        "effort": "normal",
        "tags": {"fast", "picky", "pantry", "leftovers", "dairy_free", "nut_free"},
        "ingredient_keywords": {"rice", "egg", "eggs", "pea", "peas", "frozen peas", "vegetable", "vegetables"},
        "ingredients": "rice, eggs, frozen peas or another vegetable that fits your house, and a light sauce",
        "steps": "Scramble eggs, stir-fry rice with peas, keep sauce light for kids, and add grown-up heat at the table.",
        "fallback": "If eggs are out, make quick vegetable fried rice with beans, tofu, or another protein you have.",
    },
    {
        "name": "Pasta Marinara with carrots",
        "minutes": 25,
        "effort": "normal",
        "tags": {"picky", "vegetarian", "nut_free"},
        "ingredient_keywords": {"pasta", "marinara", "carrot", "carrots", "vegetable", "vegetables", "cheese"},
        "ingredients": "pasta, jarred marinara, carrots or another simple vegetable, and optional cheese",
        "steps": "Boil pasta, warm sauce, add shredded carrots or a side vegetable, and keep toppings optional.",
        "fallback": "If pasta is missing, serve the sauce over toast, rice, or any grain you already have.",
    },
    {
        "name": "Sheet-pan chicken and corn rice bowls",
        "minutes": 30,
        "effort": "can cook",
        "tags": {"can_cook", "leftovers", "dairy_free", "nut_free"},
        "ingredient_keywords": {"chicken", "protein", "rice", "corn", "beans"},
        "ingredients": "chicken or another protein that fits your house, rice, corn, and a mild topping",
        "steps": "Cook the protein and corn together, serve over rice, and keep sauces on the side.",
        "fallback": "If chicken is missing, use beans, eggs, or leftovers as the bowl protein.",
    },
]


class DinnerDecisionSession:
    """Small Chapter 1 MVP flow that uses only current-turn parent input."""

    def __init__(self):
        self.current_recommendation: dict[str, Any] | None = None
        self.last_context: dict[str, Any] | None = None
        self.rejected: set[str] = set()

    def send(self, parent_message: str, scenario: str | None = None) -> dict[str, Any]:
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
                message = (
                    f"Good enough. Tonight is decided: {self.current_recommendation['name']}.\n"
                    "I will keep this as a lightweight signal for this session only."
                )
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
            },
        }


def create_dinner_decision_session() -> DinnerDecisionSession:
    return DinnerDecisionSession()


def parse_dinner_decision_context(parent_message: str) -> dict[str, Any]:
    message = parent_message.lower().replace("’", "'")
    minutes = None
    if any(phrase in message for phrase in ("10 min", "10 minutes", "ten minutes")):
        minutes = 10
    elif any(phrase in message for phrase in ("15 min", "15 minutes", "fifteen minutes")):
        minutes = 15
    elif any(phrase in message for phrase in ("20 min", "20 minutes", "twenty minutes")):
        minutes = 20
    elif any(phrase in message for phrase in ("30 min", "30 minutes", "thirty minutes")):
        minutes = 30

    avoid_terms = _parse_avoid_terms(message)
    positive_ingredients = [term for term in _parse_positive_ingredients(message) if term not in avoid_terms]

    return {
        "minutes": minutes,
        "energy": _parse_energy(message),
        "picky": any(phrase in message for phrase in ("picky", "kid friendly", "kid-friendly", "familiar", "kids may eat")),
        "vegetarian": _has_word(message, "vegetarian"),
        "nut_free": any(term in avoid_terms for term in ("peanut", "nut")),
        "dairy_free": any(term in avoid_terms for term in ("dairy", "milk", "cheese", "yogurt")),
        "egg_free": "egg" in avoid_terms,
        "leftovers": _has_word(message, "leftover") or _has_word(message, "leftovers"),
        "pantry": any(phrase in message for phrase in ("pantry", "freezer", "use what", "already have", "no grocery")),
        "only_have": _has_only_have_signal(message),
        "avoid_terms": avoid_terms,
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
            value += 12 if meal["effort"] == "can cook" else 0
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
        if _meal_mentions_avoided_term(meal, context.get("avoid_terms", [])):
            value -= 1000
        matched_ingredients = _matching_positive_ingredients(meal, context.get("positive_ingredients", []))
        if meal["name"] == "Rice and Peas Bowl" and not (context.get("only_have") or context.get("fallback_relief")):
            value -= 80
        value += 25 * len(matched_ingredients)
        if len(matched_ingredients) >= 2:
            value += 20
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
            if rejected_effort == "low" and meal["minutes"] >= rejected_minutes:
                value -= 30
        if context.get("leftovers"):
            value += 20 if "leftovers" in tags else 0
        if context.get("pantry"):
            value += 20 if "pantry" in tags else -8
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
            f"Time/effort: about {meal['minutes']} minutes, {meal['effort']} effort.",
        ]
    )
    if context.get("only_have"):
        lines.append("Constraint heard: I am using the ingredients you listed first, not assuming a remembered pantry.")
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


def dinner_fit_reason(meal: dict[str, Any], context: dict[str, Any]) -> str:
    reasons = []
    if context.get("minutes"):
        reasons.append(f"it fits the {context['minutes']}-minute window" if meal["minutes"] <= context["minutes"] else "it is the closest practical fit")
    if context.get("energy") == "barely cooking":
        reasons.append("it keeps cooking effort low")
    if context.get("picky"):
        reasons.append("it is a familiar kid-friendly direction based on what you told me")
    if context.get("vegetarian"):
        reasons.append("it avoids meat")
    matched_ingredients = _matching_positive_ingredients(meal, context.get("positive_ingredients", []))
    if matched_ingredients:
        reasons.append("it uses ingredients you said you have")
    if context.get("dairy_free") or context.get("egg_free") or context.get("avoid_terms"):
        reasons.append("it respects the avoidances you flagged")
    if context.get("leftovers"):
        reasons.append("it can use leftovers")
    if context.get("pantry"):
        reasons.append("it is built around ingredients you say you have")
    if not reasons:
        reasons.append("it is fast, familiar, and low-decision for tonight")
    return "; ".join(reasons) + "."


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
    for term in (
        "rice",
        "egg",
        "eggs",
        "pea",
        "peas",
        "frozen peas",
        "tortilla",
        "tortillas",
        "bean",
        "beans",
        "black beans",
        "pasta",
        "marinara",
        "carrot",
        "carrots",
        "chicken",
        "corn",
        "fruit",
        "avocado",
        "salsa",
    ):
        if _has_positive_ingredient_signal(message, term):
            ingredients.append(term)
    return ingredients


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
