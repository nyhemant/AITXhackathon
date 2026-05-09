"""Command-line entry point for the BusyParent Kitchen Agent demo."""

from __future__ import annotations

import argparse
from datetime import datetime

from busyparent_agent.agent import BusyParentAgent


DEMO_MESSAGES = [
    "What should I make for dinner tonight?",
    "Not feeling that. Anything else?",
    "Let's do egg fried rice.",
    "My daughter has a friend coming over. No nuts, no spicy food.",
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
    print("BusyParent Kitchen Agent / HomePlate AI")
    print("Local Python agent demo\n")
    for message in DEMO_MESSAGES:
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
    now = parse_now(args.now, args.demo)
    agent = BusyParentAgent(now=now, trace=args.trace)
    if args.demo:
        run_demo(agent)
    else:
        run_chat(agent)


if __name__ == "__main__":
    main()
