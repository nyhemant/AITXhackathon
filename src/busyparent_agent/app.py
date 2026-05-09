"""Command-line entry point for the BusyParent Kitchen Agent demo."""

from __future__ import annotations

import argparse

from busyparent_agent.service import (
    APP_SUBTITLE,
    APP_TITLE,
    AgentSession,
    create_session,
    parse_now,
    run_scenario as run_service_scenario,
)


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


def run_demo(session: AgentSession) -> None:
    for message in FIRST_DEMO_MESSAGES:
        print_response(session.send(message))

    selected = choose_demo_alternative(session)
    selection_message = f"Let's do {selected}."
    print_response(session.send(selection_message))

    guest_message = "My daughter has a friend coming over. No nuts, no spicy food."
    print_response(session.send(guest_message))


def choose_demo_alternative(session: AgentSession) -> str:
    alternatives = [meal["name"] for meal in session.agent.alternatives]
    if "Egg Fried Rice" in alternatives:
        return "Egg Fried Rice"
    return alternatives[0]


def run_scenario(session: AgentSession, scenario: str) -> None:
    for response in run_service_scenario(session, scenario):
        context = response.get("context")
        if context:
            print(f"Context: {context}\n")
        print_response(response)


def run_chat(session: AgentSession) -> None:
    print(APP_TITLE)
    print("Type a dinner question. Press Ctrl+C or Ctrl+D to exit.\n")
    while True:
        try:
            message = input("Parent: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGood luck tonight.")
            break
        if not message:
            continue
        print_response(session.send(message))


def print_response(response: dict) -> None:
    for line in response["trace"]:
        print(line)
    print(f"Parent: {response['parent_message']}")
    print(f"Agent: {response['message']}\n")


def main() -> None:
    args = parse_args()
    now = parse_now(args.now, args.demo, args.scenario)
    if args.demo or args.scenario:
        print(APP_TITLE)
        print(f"{APP_SUBTITLE}\n")
    session = create_session(
        now=now,
        trace=args.trace,
        scenario=args.scenario,
        locked_time_context=bool(args.now or args.demo or args.scenario),
    )
    if args.scenario:
        run_scenario(session, args.scenario)
    elif args.demo:
        run_demo(session)
    else:
        run_chat(session)


if __name__ == "__main__":
    main()
