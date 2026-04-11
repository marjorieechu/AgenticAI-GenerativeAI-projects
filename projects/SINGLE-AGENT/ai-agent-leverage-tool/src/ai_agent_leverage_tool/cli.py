from __future__ import annotations

import argparse
import json
from pathlib import Path

from openai import APIError

from ai_agent_leverage_tool.agent import ToolEnabledAgent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a tool-enabled single agent with Tavily or OpenAI built-in tools."
    )
    parser.add_argument(
        "--mode",
        choices=["tavily", "openai_web", "hybrid", "file_search"],
        default="tavily",
        help="Tool mode to run.",
    )
    parser.add_argument(
        "--message",
        action="append",
        default=[],
        help="Message to send to the agent. Pass multiple times for a multi-turn session.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="OpenAI model to use. Defaults to OPENAI_MODEL or the project default.",
    )
    parser.add_argument(
        "--session-id",
        default="tool_agent_demo",
        help="Session identifier used by SQLiteSession.",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=Path("data/session.db"),
        help="Path to the SQLite database backing session memory.",
    )
    parser.add_argument(
        "--stateless",
        action="store_true",
        help="Disable session memory.",
    )
    parser.add_argument(
        "--clear-session",
        action="store_true",
        help="Clear the SQLite-backed session before sending messages.",
    )
    parser.add_argument(
        "--vector-store-id",
        action="append",
        default=[],
        help="Vector store id to use when mode=file_search. Pass multiple times if needed.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.message:
        parser.error("Provide at least one --message value.")

    try:
        agent = ToolEnabledAgent(
            mode=args.mode,
            model=args.model,
            session_id=args.session_id,
            db_path=args.db_path,
            stateless=args.stateless,
            vector_store_ids=args.vector_store_id,
        )
    except ValueError as exc:
        parser.exit(1, f"{exc}\n")

    if args.clear_session:
        agent.clear_session()

    results = []
    try:
        for message in args.message:
            result = agent.respond(message)
            results.append({"message": message, "result": result.to_dict()})
    except RuntimeError as exc:
        parser.exit(1, f"{exc}\n")
    except APIError as exc:
        parser.exit(1, f"OpenAI API error: {exc}\n")
    except Exception as exc:
        parser.exit(1, f"Unexpected error: {exc}\n")

    print(json.dumps(results, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
