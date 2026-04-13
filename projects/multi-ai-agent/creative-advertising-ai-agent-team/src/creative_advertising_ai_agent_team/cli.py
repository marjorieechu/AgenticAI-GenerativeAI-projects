from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import re

from openai import APIError

from creative_advertising_ai_agent_team.agent import CreativeAdvertisingPipeline
from creative_advertising_ai_agent_team.models import PipelineRunResult


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the creative advertising multi-agent pipeline."
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Product or campaign brief for the agent team.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="OpenAI model to use. Defaults to OPENAI_MODEL or the project default.",
    )
    parser.add_argument(
        "--session-id",
        default="creative_ad_team",
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
        help="Clear the SQLite-backed session before running the pipeline.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )
    parser.add_argument(
        "--export-dir",
        type=Path,
        default=None,
        help="Optional directory where the run JSON and markdown summary should be saved.",
    )
    parser.add_argument(
        "--export-prefix",
        default=None,
        help="Optional file prefix for exported artifacts. Defaults to a slug from the session id or prompt.",
    )
    return parser


def export_run_artifacts(
    result: PipelineRunResult,
    *,
    export_dir: Path,
    export_prefix: str | None = None,
) -> tuple[Path, Path]:
    export_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    prefix = export_prefix or _default_export_prefix(result)
    safe_prefix = _slugify(prefix)

    json_path = export_dir / f"{safe_prefix}-{timestamp}.json"
    markdown_path = export_dir / f"{safe_prefix}-{timestamp}.md"

    json_path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    markdown_path.write_text(_render_summary_markdown(result), encoding="utf-8")
    return json_path, markdown_path


def _default_export_prefix(result: PipelineRunResult) -> str:
    if result.session_id:
        return result.session_id
    return result.product_prompt


def _slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    collapsed = re.sub(r"-{2,}", "-", normalized).strip("-")
    return collapsed or "campaign-run"


def _render_summary_markdown(result: PipelineRunResult) -> str:
    lines = [
        "# Campaign Run Summary",
        "",
        "Prompt:",
        "",
        f"`{result.product_prompt}`",
        "",
        "Top campaigns:",
        "",
    ]
    lines.extend(f"- `{campaign}`" for campaign in result.top_campaigns)
    lines.extend(
        [
            "",
            "Reasoning:",
            "",
            result.reasoning,
            "",
            "Tweets:",
            "",
        ]
    )
    lines.extend(f"- {tweet}" for tweet in result.tweets)
    lines.extend(
        [
            "",
            "Channel plan:",
            "",
        ]
    )
    for channel, entries in result.channel_plan.items():
        lines.append(f"- `{channel}`")
        lines.extend(f"  - {entry}" for entry in entries)

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    pipeline = CreativeAdvertisingPipeline(
        model=args.model,
        session_id=args.session_id,
        db_path=args.db_path,
        stateless=args.stateless,
    )

    if args.clear_session:
        pipeline.clear_session()

    try:
        result = pipeline.run_campaign(args.prompt)
    except RuntimeError as exc:
        parser.exit(1, f"{exc}\n")
    except APIError as exc:
        parser.exit(1, f"OpenAI API error: {exc}\n")
    except Exception as exc:
        parser.exit(1, f"Unexpected error: {exc}\n")

    print(json.dumps(result.to_dict(), indent=2 if args.pretty else None))

    if args.export_dir is not None:
        json_path, markdown_path = export_run_artifacts(
            result,
            export_dir=args.export_dir,
            export_prefix=args.export_prefix,
        )
        print(f"Exported JSON: {json_path}")
        print(f"Exported summary: {markdown_path}")


if __name__ == "__main__":
    main()
