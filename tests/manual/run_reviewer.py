# ruff: noqa
"""Standalone runner for the Reviewer agent (Sprint 4) — MACHINE DE TEST (WSL) ONLY.

Purpose: exercise `reviewer_agent` IN ISOLATION over a chosen level_config.json, so the
Coder can't overwrite the input. Use it to prove the Reviewer catches a deliberately
broken config (off-site species, out-of-range values, spawn_weight 0, etc.).

It mirrors the Runner pattern of tests/integration/test_agent.py, but:
  - targets ONLY `reviewer_agent` (not the full pipeline),
  - seeds session.state["csr_summary"] with Clerac data (normally set by the Researcher),
  - swaps the config under test into public/level_config.json, then restores the original.

Usage (on the WSL test machine, after `agents-cli install`):
    uv run python tests/manual/run_reviewer.py                     # broken fixture (must FAIL)
    uv run python tests/manual/run_reviewer.py public/configs/examples/level_config.sprint3.json   # good config (should PASS)

Then read the written report: docs/reviews/review_clerac.md
This is a MANUAL script (real Gemini + MCP calls, needs Vertex auth + TAVILY_API_KEY),
not a pytest — it is not collected by `uv run pytest`.
"""

import shutil
import sys
from pathlib import Path

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agent import reviewer_agent

PROJECT_DIR = Path(__file__).resolve().parents[2]
LIVE_CONFIG = PROJECT_DIR / "public" / "level_config.json"
DEFAULT_UNDER_TEST = PROJECT_DIR / "public" / "configs" / "examples" / "level_config.broken.json"

# csr_summary as the Researcher would emit it for Clerac (seeds {csr_summary}).
CLERAC_CSR_SUMMARY = (
    '{"site_name": "Clerac", "mineral_name": "Chamotte Clay", '
    '"eco_target": "Migratory Birds (MNHN)", "protected_area": "Chestnut Groves (bats)", '
    '"danger_obstacle": "Blasting Zone", '
    '"headline_fact": "Like Imerys at Clerac, you supported bird monitoring with the MNHN through the ACRO-bag program.", '
    '"biodiversity_species": ["Migratory Birds", "Cave Bats", "European Roller", '
    '"Bee-eater", "Natterjack Toad", "Ocellated Lizard"]}'
)


def main() -> None:
    under_test = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_UNDER_TEST
    if not under_test.exists():
        raise SystemExit(f"Config under test not found: {under_test}")

    # Swap the config under test into place, keeping a backup of the live one.
    backup = None
    if LIVE_CONFIG.exists():
        backup = LIVE_CONFIG.with_suffix(".json.bak")
        shutil.copyfile(LIVE_CONFIG, backup)
    shutil.copyfile(under_test, LIVE_CONFIG)
    print(f"[run_reviewer] config under test -> public/level_config.json : {under_test.name}")

    try:
        session_service = InMemorySessionService()
        session = session_service.create_session_sync(
            user_id="reviewer_test",
            app_name="reviewer_test",
            state={"csr_summary": CLERAC_CSR_SUMMARY},
        )
        runner = Runner(
            agent=reviewer_agent,
            session_service=session_service,
            app_name="reviewer_test",
        )
        message = types.Content(
            role="user",
            parts=[types.Part.from_text(text="Review the level_config.json for Clerac.")],
        )
        for event in runner.run(
            new_message=message,
            user_id="reviewer_test",
            session_id=session.id,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if getattr(part, "function_call", None):
                        print(f"  [MCP tool_use] {part.function_call.name}({part.function_call.args})")
                    if getattr(part, "text", None):
                        print(f"  [text] {part.text}")
    finally:
        # Restore the live config so a test run isn't destructive.
        if backup and backup.exists():
            shutil.copyfile(backup, LIVE_CONFIG)
            backup.unlink()
            print("[run_reviewer] restored original public/level_config.json")

    report = PROJECT_DIR / "docs" / "reviews" / "review_clerac.md"
    print(f"[run_reviewer] done. Read the report: {report.relative_to(PROJECT_DIR)}")


if __name__ == "__main__":
    main()
