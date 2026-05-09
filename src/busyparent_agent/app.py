"""Command-line entry point for the BusyParent Kitchen Agent demo."""

from __future__ import annotations

import argparse
from datetime import datetime

from busyparent_agent.agent import BusyParentAgent
from busyparent_agent import tools


FIRST_DEMO_MESSAGES = [
    "What should I make for dinner tonight?",
    "Not feeling that. Anything else?",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the BusyParent Kitchen Agent / HomePlate AI local demo."
    )
    parser.add_argument("--trace", action="store_true", help="Print tool calls and decisions.")
    parser.add_argument("--demo", action="store_true", help="Run the scripted hackathon demo conversation.")
    parser.add_argument(
        "--scenario",
        choices=["dinner", "lunch", "guest"],
        help="Run a short judge-friendly scenario.",
    )
    parser.add_argument("--now", help='Override current time, for example: "2026-05-08 17:30".')
    return parser.parse_args()


def parse_now(value: str | None, demo: bool, scenario: str | None = None) -> datetime:
    if value:
        return datetime.strptime(value, "%Y-%m-%d %H:%M")
    if scenario == "lunch":
        return datetime.strptime("2026-05-09 12:30", "%Y-%m-%d %H:%M")
    if scenario in {"dinner", "guest"}:
        return datetime.strptime("2026-05-08 17:30", "%Y-%m-%d %H:%M")
    if demo:
        return datetime.strptime("2026-05-08 17:30", "%Y-%m-%d %H:%M")
    return datetime.now()


def run_demo(agent: BusyParentAgent) -> None:
    for message in FIRST_DEMO_MESSAGES:
        print(f"Parent: {message}")
        print(f"Agent: {agent.reply(message)}\n")

    selected = choose_demo_alternative(agent)
    selection_message = f"Let's do {selected}."
    print(f"Parent: {selection_message}")
    print(f"Agent: {agent.reply(selection_message)}\n")

    guest_message = "My daughter has a friend coming over. No nuts, no spicy food."
    print(f"Parent: {guest_message}")
    print(f"Agent: {agent.reply(guest_message)}\n")


def choose_demo_alternative(agent: BusyParentAgent) -> str:
    alternatives = [meal["name"] for meal in agent.alternatives]
    if "Egg Fried Rice" in alternatives:
        return "Egg Fried Rice"
    return alternatives[0]


def run_scenario(agent: BusyParentAgent, scenario: str) -> None:
    if scenario in {"dinner", "lunch"}:
        message = "What should I make for dinner tonight?"
        print(f"Parent: {message}")
        print(f"Agent: {agent.reply(message)}\n")
        return

    egg_fried_rice = next(meal for meal in agent.meal_options if meal["name"] == "Egg Fried Rice")
    selected = dict(egg_fried_rice)
    selected["missing"] = tools.missing_ingredients(selected, agent.inventory)
    agent.selected_meal = selected

    print("Context: Selected meal is Egg Fried Rice.\n")
    message = "My daughter has a friend coming over. No nuts, no spicy food."
    print(f"Parent: {message}")
    print(f"Agent: {agent.reply(message)}\n")


def run_chat(agent: BusyParentAgent) -> None:
    print("BusyParent Kitchen Agent / HomePlate AI")
    print("Type a dinner question. Press Ctrl+C or Ctrl+D to exit.\n")
    while True:
        try:
            message = input("Parent: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGood luck tonight.")
            break
        if not message:
            continue
        print(f"Agent: {agent.reply(message)}\n")


def main() -> None:
    args = parse_args()
    now = parse_now(args.now, args.demo, args.scenario)
    if args.demo or args.scenario:
        print("BusyParent Kitchen Agent / HomePlate AI")
        print("Local Python agent demo\n")
    agent = BusyParentAgent(now=now, trace=args.trace)
    if args.scenario:
        run_scenario(agent, args.scenario)
    elif args.demo:
        run_demo(agent)
    else:
        run_chat(agent)


if __name__ == "__main__":
    main()
