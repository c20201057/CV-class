#!/usr/bin/env python3
"""Audit the agent task board for stale paths and unsafe dispatch state."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


WORKSPACE = Path("/root/data-tmp/workspace")
DEFAULT_TASK_BOARD = WORKSPACE / "03_agent_tasks" / "task_board.md"
DEFAULT_OUT = WORKSPACE / "03_agent_tasks" / "task_board_consistency_audit_latest.md"

REQUIRED_MARKERS = [
    "00_project/orchestrator_tick_latest.md",
    "03_agent_tasks/prompts/MASTER_TARGET_PROMPT.md",
    "03_agent_tasks/prompts/DISPATCH_PACKETS.md",
    "03_agent_tasks/acceptance/agent_acceptance_ledger.md",
    "audit_agent_acceptance_ledger.py",
    "resume_stopped_prob_eval_when_gpu_idle.sh",
    "watch_baseline_then_start_kd.sh",
    "start_kd_full_train.sh",
    "external_dirty_tree_observation_only",
    "不偷懒",
    "不因为怕风险而保守",
]

FORBIDDEN_MARKERS = [
    "`prompts/DISPATCH_PACKETS.md`",
]

PATH_TOKEN_RE = re.compile(r"`([^`]+)`")
PATHISH_RE = re.compile(r"^(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.#-]+$")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def resolve_path(token: str) -> Path | None:
    if " " in token:
        return None
    path_part = token.split("#", 1)[0]
    if not path_part or path_part.startswith("status="):
        return None
    if path_part.startswith("configs/"):
        return None
    if path_part.startswith("/"):
        return Path(path_part)
    if path_part.startswith(("00_project/", "01_literature/", "02_experiments/", "03_agent_tasks/", "04_paper/", "05_reviews/")):
        return WORKSPACE / path_part
    if path_part.startswith(("prompts/", "pending/", "acceptance/", "reports/")):
        return WORKSPACE / "03_agent_tasks" / path_part
    if PATHISH_RE.match(path_part):
        return WORKSPACE / path_part
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task_board", default=str(DEFAULT_TASK_BOARD))
    parser.add_argument("--out_md", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    task_board = Path(args.task_board).expanduser().resolve()
    out_md = Path(args.out_md).expanduser().resolve()
    findings: list[str] = []
    notes: list[str] = []

    if not task_board.is_file():
        findings.append(f"missing task board: {task_board}")
        text = ""
    else:
        text = read_text(task_board)

    if text:
        for marker in REQUIRED_MARKERS:
            if marker not in text:
                findings.append(f"task board missing required marker `{marker}`")
        for marker in FORBIDDEN_MARKERS:
            if marker in text:
                findings.append(f"task board contains stale marker `{marker}`")

        for match in PATH_TOKEN_RE.finditer(text):
            token = match.group(1)
            line_start = text.rfind("\n", 0, match.start()) + 1
            line_end = text.find("\n", match.end())
            if line_end == -1:
                line_end = len(text)
            line = text[line_start:line_end]
            if "planned:" in line and token.startswith(("02_experiments/runs/", "start_", "epoch_")):
                notes.append(f"planned path skipped: `{token}`")
                continue
            candidate = resolve_path(token)
            if candidate is None:
                continue
            if not candidate.exists():
                findings.append(f"referenced path does not exist: `{token}` -> {candidate}")
            else:
                notes.append(f"path ok: `{token}`")

        required_sections = [
            "## Current Dispatch Note",
            "## Running",
            "## Completed",
            "## Ready / Pending",
            "## Dispatch Rules",
            "## GPU Queue",
        ]
        for section in required_sections:
            if section not in text:
                findings.append(f"task board missing section `{section}`")

    status = "pass" if not findings else "fail"
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(
        "\n".join(
            [
                "# Task Board Consistency Audit",
                "",
                f"- Status: `{status}`",
                f"- Task board: `{task_board}`",
                f"- Findings: {len(findings)}",
                "",
                "## Findings",
                "",
                *([f"- {item}" for item in findings] or ["- none"]),
                "",
                "## Notes",
                "",
                *([f"- {item}" for item in notes] or ["- none"]),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    for finding in findings:
        print(f"ERROR: {finding}", file=sys.stderr)
    print(f"task_board_consistency_audit={status}")
    print(f"report={out_md}")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
