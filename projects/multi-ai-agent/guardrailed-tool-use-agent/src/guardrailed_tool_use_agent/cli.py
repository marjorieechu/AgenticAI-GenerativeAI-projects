from __future__ import annotations

import argparse
import json
from pathlib import Path

from openai import APIError

from guardrailed_tool_use_agent.agent import GuardrailedSentimentWorkflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the guardrailed sentiment workflow with handoffs and nested search."
    )
    parser.add_argument(
        "--mode",
        choices=["writer_handoff", "sentiment_only"],
        default="writer_handoff",
        help="Whether to run the full planner-to-writer handoff or only the sentiment specialist.",
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Prompt to send into the workflow.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="OpenAI model to use. Defaults to OPENAI_MODEL or the project default.",
    )
    parser.add_argument(
        "--session-id",
        default="guardrailed_sentiment_demo",
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
        help="Clear the SQLite-backed session before sending the prompt.",
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

    workflow = GuardrailedSentimentWorkflow(
        model=args.model,
        session_id=args.session_id,
        db_path=args.db_path,
        stateless=args.stateless,
    )

    if args.clear_session:
        workflow.clear_session()

    try:
        if args.mode == "writer_handoff":
            result = workflow.run_writer_handoff(args.prompt)
        else:
            result = workflow.run_sentiment_only(args.prompt)
    except RuntimeError as exc:
        parser.exit(1, f"{exc}\n")
    except APIError as exc:
        parser.exit(1, f"OpenAI API error: {exc}\n")
    except Exception as exc:
        parser.exit(1, f"Unexpected error: {exc}\n")

    print(json.dumps(result.to_dict(), indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
