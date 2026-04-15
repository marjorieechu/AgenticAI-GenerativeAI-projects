from __future__ import annotations

import argparse
import asyncio
from typing import Any

from autogen_devops_war_room.config import load_env, supported_team_modes, validate_env_for_mode
from autogen_devops_war_room.team import build_team


DEFAULT_TASK = (
    "We have a production deployment failure after a GitHub Actions release. "
    "One migration failed, rollback safety is unclear, and leadership needs a quick operational update. "
    "Discuss the likely root cause, safe next action, and a concise stakeholder status note."
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run an AutoGen DevOps war-room group chat with three AI agents and a human operator."
    )
    parser.add_argument(
        "--team-mode",
        choices=list(supported_team_modes()),
        default="openai_only",
        help="Use the OpenAI-only team or the mixed Gemini + OpenAI team.",
    )
    parser.add_argument(
        "--task",
        default=DEFAULT_TASK,
        help="Incident scenario to send into the war room.",
    )
    parser.add_argument(
        "--max-rounds",
        type=int,
        default=10,
        help="Maximum group chat rounds before termination.",
    )
    parser.add_argument(
        "--auto-human-reply",
        default=None,
        help="Optional fixed reply for the human proxy. If omitted, the CLI will prompt interactively.",
    )
    return parser


def _make_input_func(auto_reply: str | None):
    if auto_reply is not None:
        return lambda prompt: auto_reply
    return lambda prompt: input(prompt)


def _render_event(event: Any) -> str | None:
    type_name = type(event).__name__

    if type_name == "TextMessage":
        source = getattr(event, "source", "Unknown")
        content = getattr(event, "content", "")
        return f"\n[{source}]\n{content}\n"

    if type_name == "UserInputRequestedEvent":
        source = getattr(event, "source", "Human_Operator")
        return f"\n[{source}] Waiting for human input...\n"

    if type_name == "TaskResult":
        return "\n[System] War room finished.\n"

    if type_name == "GroupChatError":
        error = getattr(event, "error", None)
        message = str(error) if error is not None else "Unknown group chat error."
        return f"\n[System Error]\n{message}\n"

    return None


def _print_provider_hint(message: str) -> None:
    lowered = message.lower()
    if "quota exceeded" in lowered or "resource_exhausted" in lowered:
        print(
            "\n[Hint]\n"
            "A provider quota limit was hit. In your current setup this is most likely the Gemini commander role.\n"
            "You can either wait and retry, switch the Gemini model, enable Gemini billing/quota, or temporarily run `--team-mode openai_only`.\n"
        )


async def _run(args: argparse.Namespace) -> None:
    load_env()
    missing = validate_env_for_mode(args.team_mode)
    if missing:
        missing_display = ", ".join(missing)
        raise RuntimeError(
            f"Missing environment variables for team mode '{args.team_mode}': {missing_display}"
        )

    bundle = build_team(
        args.team_mode,
        human_input_func=_make_input_func(args.auto_human_reply),
        max_rounds=args.max_rounds,
    )
    try:
        async for event in bundle.team.run_stream(task=args.task):
            rendered = _render_event(event)
            if rendered:
                print(rendered, end="")
                if type(event).__name__ == "GroupChatError":
                    _print_provider_hint(rendered)
    finally:
        for client in bundle.model_clients:
            close = getattr(client, "close", None)
            if callable(close):
                maybe_awaitable = close()
                if asyncio.iscoroutine(maybe_awaitable):
                    await maybe_awaitable


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        asyncio.run(_run(args))
    except RuntimeError as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
