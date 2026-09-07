"""Per-card study decks (Easy now; Hard / Zoologist later).

Facts for african-lion Easy are Wikipedia-backed:
https://en.wikipedia.org/wiki/Lion
Do not invent stats. Soften contested numbers. Roar distance may cite
“about 8 km / 5 miles (Wikipedia).”

Slot ids stay stable so later levels can plug into the same 10 questions.
Visible copy must not show age badges or Easy / Hard / Zoologist titles.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FIELD = REPO / "static" / "field-pack"
STUDY_JSON = FIELD / "data" / "study-cards.json"
STUDY_DATA_JS = FIELD / "js" / "study-cards-data.js"

# https://en.wikipedia.org/wiki/Lion — source for Easy facts (not invented).
WIKI_LION = "https://en.wikipedia.org/wiki/Lion"

LETTERS = ("A", "B", "C")
STUDY_SLOTS = 10
DEFAULT_LEVEL = "easy"

# Only Easy ships this PR. Hard / Zoologist stay absent.
STUDY_CARDS: dict[str, dict] = {
    "african-lion": {
        "id": "african-lion",
        "source": WIKI_LION,
        "source_note": "Facts from Wikipedia, Lion.",
        "levels": {
            "easy": {
                # Teaching-first: same front as the quiz. Hard later may hide these.
                "teach": [
                    "A group of lions is a pride.",
                    "A baby is a cub.",
                    "They live on grasslands / savannah, not jungle.",
                    "Their famous sound is a roar.",
                    "Male lions often grow a big mane.",
                ],
                "questions": [
                    {
                        "slot": 1,
                        "id": "family",
                        "title": "Family",
                        "stem": "What do you call a group of lions?",
                        "choices": ["A pack", "A pride", "A herd"],
                        "correct": "B",
                        "why": "Lions live together in a pride — a social group that shares space and raises cubs.",
                    },
                    {
                        "slot": 2,
                        "id": "food",
                        "title": "Food",
                        "stem": "What do lions mostly eat?",
                        "choices": ["Grass", "Fruit", "Meat"],
                        "correct": "C",
                        "why": "Lions eat meat. They mostly hunt hooved animals such as zebra, wildebeest, and antelope.",
                    },
                    {
                        "slot": 3,
                        "id": "voice",
                        "title": "Voice",
                        "stem": "What sound is a lion famous for?",
                        "choices": ["A moo", "A roar", "A squeak"],
                        "correct": "B",
                        "why": "A lion’s roar can travel a long way — about 8 km / 5 miles (Wikipedia).",
                    },
                    {
                        "slot": 4,
                        "id": "mane",
                        "title": "Body",
                        "stem": "Which lion usually grows a big fluffy mane?",
                        "choices": ["The male", "The female", "Both"],
                        "correct": "A",
                        "why": "Male lions often grow a big mane around the head and neck.",
                    },
                    {
                        "slot": 5,
                        "id": "young",
                        "title": "Young",
                        "stem": "What is a baby lion called?",
                        "choices": ["A calf", "A chick", "A cub"],
                        "correct": "C",
                        "why": "A baby lion is a cub. Many cubs have faint spots that fade as they grow.",
                    },
                    {
                        "slot": 6,
                        "id": "home",
                        "title": "Home",
                        "stem": "Where do wild lions mostly live?",
                        "choices": ["Thick jungle", "Grassland / savannah", "Deep ocean"],
                        "correct": "B",
                        "why": "Wild lions mostly live on grassland, savannah, and shrubland — rarely in closed forest.",
                    },
                    {
                        "slot": 7,
                        "id": "rest",
                        "title": "Rest",
                        "stem": "How much of the day do lions often spend resting?",
                        "choices": ["About 2 hours", "About 8 hours", "About 20 hours"],
                        "correct": "C",
                        "why": "Lions often rest or stay inactive for about 20 hours a day.",
                    },
                    {
                        "slot": 8,
                        "id": "hunting",
                        "title": "Hunting",
                        "stem": "In a pride, who usually does most of the hunting?",
                        "choices": ["The dads", "The moms (lionesses)", "The cubs"],
                        "correct": "B",
                        "why": "In a pride, lionesses usually do most of the hunting, often together.",
                    },
                    {
                        "slot": 9,
                        "id": "tail",
                        "title": "Body",
                        "stem": "What special tip does a lion’s tail have?",
                        "choices": ["Feathers", "A dark hairy tuft", "A shell"],
                        "correct": "B",
                        "why": "A lion’s tail ends in a dark hairy tuft.",
                    },
                    {
                        "slot": 10,
                        "id": "myth",
                        "title": "Myth buster",
                        "stem": "Do lions really live in a jungle like in some cartoons?",
                        "choices": ["Yes, always", "No — mostly open grassland", "Only in snow"],
                        "correct": "B",
                        "why": "Cartoons show jungle lions, but wild lions mostly live on open grassland.",
                    },
                ],
            }
        },
    }
}


def _esc(s: str) -> str:
    return (
        str(s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def study_card_ids() -> tuple[str, ...]:
    return tuple(STUDY_CARDS)


def study_deck_for(card_id: str, level: str = DEFAULT_LEVEL) -> dict | None:
    """Return a flattened deck for one card + level, or None."""
    raw = STUDY_CARDS.get(str(card_id or "").strip())
    if not raw:
        return None
    pack = (raw.get("levels") or {}).get(level)
    if not pack:
        return None
    questions = list(pack.get("questions") or [])
    if len(questions) != STUDY_SLOTS:
        return None
    return {
        "id": raw["id"],
        "level": level,
        "source": raw.get("source") or "",
        "source_note": raw.get("source_note") or "",
        "teach": list(pack.get("teach") or []),
        "questions": questions,
    }


def validate_deck(deck: dict) -> list[str]:
    """Return human-readable problems. Empty means the Easy (or given) deck is locked."""
    errors: list[str] = []
    if not deck:
        return ["missing deck"]
    teach = deck.get("teach") or []
    if not teach:
        errors.append("teach strip empty")
    questions = deck.get("questions") or []
    if len(questions) != STUDY_SLOTS:
        errors.append(f"expected {STUDY_SLOTS} questions, got {len(questions)}")
    seen_slots: set[int] = set()
    seen_ids: set[str] = set()
    for i, q in enumerate(questions, start=1):
        slot = int(q.get("slot") or 0)
        if slot != i:
            errors.append(f"slot {i} has slot={slot}")
        if slot in seen_slots:
            errors.append(f"duplicate slot {slot}")
        seen_slots.add(slot)
        qid = str(q.get("id") or "")
        if not qid:
            errors.append(f"slot {i} missing id")
        if qid in seen_ids:
            errors.append(f"duplicate id {qid}")
        seen_ids.add(qid)
        choices = list(q.get("choices") or [])
        if len(choices) != 3:
            errors.append(f"slot {i} needs 3 choices")
        correct = str(q.get("correct") or "")
        if correct not in LETTERS:
            errors.append(f"slot {i} correct must be A/B/C")
        elif choices and LETTERS.index(correct) >= len(choices):
            errors.append(f"slot {i} correct letter out of range")
        if not str(q.get("stem") or "").strip():
            errors.append(f"slot {i} missing stem")
        if not str(q.get("why") or "").strip():
            errors.append(f"slot {i} missing why")
        if not str(q.get("title") or "").strip():
            errors.append(f"slot {i} missing title")
    return errors


def decks_as_jsonable() -> dict:
    return STUDY_CARDS


def write_study_artifacts() -> None:
    """JSON + window.FP_STUDY_CARDS for print-kit / study-card.js."""
    STUDY_JSON.parent.mkdir(parents=True, exist_ok=True)
    STUDY_DATA_JS.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(STUDY_CARDS, indent=2, ensure_ascii=False)
    STUDY_JSON.write_text(payload + "\n", encoding="utf-8")
    STUDY_DATA_JS.write_text(
        "/* Generated from scripts/study_cards.py — edit the Python source. */\n"
        "window.FP_STUDY_CARDS = "
        + json.dumps(STUDY_CARDS, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )


def study_talk_html(deck: dict, *, heading: str = "Talk") -> str:
    """Screen: teach strip + 10 MCQs + reveal/why. No level title in the UI."""
    teach_items = "".join(f"<li>{_esc(line)}</li>" for line in deck.get("teach") or [])
    teach = (
        f'<div class="study-teach">'
        f'<p class="study-teach-kicker">Learn first</p>'
        f"<ul>{teach_items}</ul>"
        f"</div>"
        if teach_items
        else ""
    )
    cards: list[str] = []
    for q in deck.get("questions") or []:
        choices = []
        for letter, label in zip(LETTERS, q.get("choices") or []):
            choices.append(
                f'<button type="button" class="choice study-choice" '
                f'data-letter="{letter}" data-choice="{_esc(label)}">'
                f'<span class="dot" aria-hidden="true"></span>'
                f'<span><span class="study-letter">{letter}</span> {_esc(label)}</span>'
                f"</button>"
            )
        why = _esc(q.get("why") or "")
        cards.append(
            f'<section class="mission card-talk-q study-q" data-slot="{int(q["slot"])}" '
            f'data-qid="{_esc(q.get("id") or "")}" data-correct="{_esc(q.get("correct") or "")}">'
            f'<div class="mission-head"><span class="badge">{int(q["slot"])}</span>'
            f'<p class="mission-title">{_esc(q.get("title") or "")}</p></div>'
            f'<h3 class="mission-q">{_esc(q.get("stem") or "")}</h3>'
            f'<div class="choices" data-multi="0" data-count="3">{"".join(choices)}</div>'
            f'<p class="study-why" hidden>{why}</p>'
            f"</section>"
        )
    source = _esc(deck.get("source_note") or "")
    source_html = f'<p class="study-source">{source}</p>' if source else ""
    n = STUDY_SLOTS
    return (
        f'<section class="card-talk-pack card-study-pack" aria-label="{_esc(heading)}" '
        f'data-study-id="{_esc(deck.get("id") or "")}" data-study-level="{_esc(deck.get("level") or DEFAULT_LEVEL)}">'
        f'<h2 class="card-talk-h">{_esc(heading)}</h2>'
        f"{teach}"
        f'<div class="study-toolbar no-print">'
        f'<p class="study-score">Score <span data-study-correct>0</span>/{n}</p>'
        f'<button type="button" class="btn btn-secondary" data-study-reveal>Show answers</button>'
        f"</div>"
        f'<div class="mission-grid study-grid">{"".join(cards)}</div>'
        f"{source_html}"
        f"</section>"
    )


def _print_q_card(q: dict) -> str:
    choice_html = []
    for letter, label in zip(LETTERS, q.get("choices") or []):
        choice_html.append(
            f'<div class="ps-choice"><span class="ps-dot"></span>'
            f"<span>{letter} · {_esc(label)}</span></div>"
        )
    return (
        f'<section class="ps-card ps-study-q">'
        f'<div class="ps-card-head"><span class="ps-num">{int(q["slot"])}</span>'
        f'<p class="ps-title">{_esc(q.get("title") or "")}</p></div>'
        f'<h3 class="ps-q">{_esc(q.get("stem") or "")}</h3>'
        f'<div class="ps-choices ps-study-choices">{"".join(choice_html)}</div>'
        f"</section>"
    )


def study_print_html(
    deck: dict,
    *,
    name: str,
    emoji: str = "",
    photo: str = "",
    photo_pos: str = "",
) -> str:
    """A4 duplex-ready: front quiz + back answers. Each face is one 9.4in sheet."""
    questions = list(deck.get("questions") or [])
    teach_items = "".join(f"<li>{_esc(line)}</li>" for line in deck.get("teach") or [])
    teach = (
        f'<div class="ps-study-teach"><p class="ps-talk-label">Learn first</p>'
        f"<ul>{teach_items}</ul></div>"
        if teach_items
        else ""
    )
    pos_style = ""
    if photo_pos:
        pos_style = (
            f' style="--ps-photo-pos:{_esc(photo_pos)};object-position:{_esc(photo_pos)}"'
        )
    photo_block = (
        f'<div class="ps-study-photo"><img class="ps-photo-big" src="{_esc(photo)}" '
        f'alt="{_esc(name)}" decoding="async"{pos_style} /></div>'
        if photo
        else ""
    )
    top_qs = "".join(_print_q_card(q) for q in questions[:2])
    rest_qs = "".join(_print_q_card(q) for q in questions[2:])
    answers = []
    for q in questions:
        letter = str(q.get("correct") or "")
        idx = LETTERS.index(letter) if letter in LETTERS else 0
        label = (q.get("choices") or [""])[idx]
        answers.append(
            f"<li><strong>{int(q['slot'])} {_esc(q.get('title') or '')} — {letter} {_esc(label)}.</strong> "
            f"{_esc(q.get('why') or '')}</li>"
        )
    source = _esc(deck.get("source_note") or "Facts from Wikipedia, Lion.")
    banner_name = f"{emoji} {name}".strip()
    return (
        f'<div class="ps-study-front ps-page">'
        f'<div class="ps-banner"><h1>FIELD TRIP KIT</h1>'
        f"<p>{_esc(name)} · Circle one · Flip for answers</p></div>"
        f'<header class="ps-head"><h2>{_esc(banner_name)}</h2>'
        f'<p class="ps-line"><strong>Explorer:</strong> <span class="write-in-line">________________</span></p>'
        f"</header>"
        f"{teach}"
        f'<div class="ps-study-top">{photo_block}'
        f'<div class="ps-study-top-qs">{top_qs}</div></div>'
        f'<div class="ps-study-grid">{rest_qs}</div>'
        f'<p class="ps-footer">{source} · 1less.app · Duplex: this side questions, back answers</p>'
        f"</div>"
        f'<div class="ps-study-back ps-page">'
        f'<div class="ps-banner"><h1>FIELD TRIP KIT</h1>'
        f"<p>{_esc(name)} · Answers</p></div>"
        f'<ol class="ps-study-answers">{"".join(answers)}</ol>'
        f'<p class="ps-footer">{source} · {_esc(deck.get("source") or WIKI_LION)}</p>'
        f"</div>"
    )
