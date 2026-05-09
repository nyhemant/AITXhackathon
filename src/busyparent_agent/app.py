"""Command-line entry point for the BusyParent Kitchen Agent demo."""

from __future__ import annotations

import argparse
from datetime import datetime

from busyparent_agent.agent import BusyParentAgent


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
    parser.add_argument("--now", help='Override current time, for example: "2026-05-08 17:30".')
    return parser.parse_args()


def parse_now(value: str | None, demo: bool) -> datetime:
    if value:
        return datetime.strptime(value, "%Y-%m-%d %H:%M")
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
    now = parse_now(args.now, args.demo)
    if args.demo:
        print("BusyParent Kitchen Agent / HomePlate AI")
        print("Local Python agent demo\n")
    agent = BusyParentAgent(now=now, trace=args.trace)
    if args.demo:
        run_demo(agent)
    else:
        run_chat(agent)


if __name__ == "__main__":
    main()
