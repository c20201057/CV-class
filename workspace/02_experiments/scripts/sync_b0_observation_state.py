#!/usr/bin/env python3
"""Refresh B0 observation artifacts and run the non-GPU gates.

This script is intentionally read-only with respect to training jobs. It does
not start, stop, signal, evaluate or profile a model. It only refreshes status
artifacts that describe the external dirty-tree B0 branch.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


WORKSPACE = Path("/root/data-tmp/workspace")
SCRIPTS = WORKSPACE / "02_experiments" / "scripts"
PAPER_SCRIPTS = WORKSPACE / "04_paper" / "scripts"


@dataclass(frozen=True)
class Step:
    name: str
    cmd: list[str]


def run_step(step: Step, *, dry_run: bool) -> None:
    print(f"\n==> {step.name}", flush=True)
    print("cmd=" + " ".join(step.cmd), flush=True)
    if dry_run:
        return
    subprocess.run(step.cmd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip_release_audit",
        "--skip-release-audit",
        action="store_true",
        help="Skip the full release audit after B0-specific checks.",
    )
    parser.add_argument(
        "--dry_run",
        "--dry-run",
        action="store_true",
        help="Print commands without executing them.",
    )
    args = parser.parse_args()

    steps = [
        Step("refresh_external_b0_status", ["python", str(SCRIPTS / "summarize_external_b0.py")]),
        Step("refresh_b0_trend_figure", ["python", str(PAPER_SCRIPTS / "draw_b0_trend_figure.py")]),
        Step(
            "refresh_orchestrator_tick",
            ["python", str(SCRIPTS / "orchestrator_tick.py"), "--no_refresh_b0"],
        ),
        Step("audit_b0_status_consistency", ["python", str(SCRIPTS / "audit_b0_status_consistency.py")]),
    ]
    if not args.skip_release_audit:
        steps.append(
            Step("run_release_audits", ["bash", str(SCRIPTS / "run_release_audits.sh")])
        )

    try:
        for step in steps:
            run_step(step, dry_run=args.dry_run)
    except subprocess.CalledProcessError as exc:
        print(f"sync_b0_observation_state=fail step_exit={exc.returncode}", file=sys.stderr)
        return exc.returncode

    print("\nsync_b0_observation_state=pass")
    print(f"status={WORKSPACE / '02_experiments/runs/b0_external_status_latest.md'}")
    print(f"tick={WORKSPACE / '00_project/orchestrator_tick_latest.md'}")
    print(f"trend={WORKSPACE / '04_paper/drafts/b0_cod10k_trend_note.md'}")
    print(f"audit={WORKSPACE / '04_paper/drafts/b0_status_consistency_audit_latest.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
