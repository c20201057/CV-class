#!/usr/bin/env python3
"""Audit MobileMamba-T2 observation notes for stale branch state.

MobileMamba-T2 is an external dirty-tree branch. It may keep producing
intermediate COD10K rows while the main Gate 1/KD queue waits. This audit makes
sure route and paper-control documents mention the current observed row without
promoting the branch into a main-paper result.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path


WORKSPACE = Path("/root/data-tmp/workspace")
DEFAULT_STATUS = WORKSPACE / "02_experiments" / "runs" / "mobilemamba_t2_external_status_latest.md"
DEFAULT_RESULT = Path("/root/data-tmp/results_train/mobilemamba_t2/result.txt")
DEFAULT_OUT = WORKSPACE / "04_paper" / "drafts" / "mobilemamba_status_consistency_audit_latest.md"
DEFAULT_TARGETS = [
    WORKSPACE / "00_project" / "route_decision.md",
    WORKSPACE / "00_project" / "orchestrator_status.md",
    WORKSPACE / "00_project" / "resume_handoff.md",
    WORKSPACE / "00_project" / "current_run_snapshot.md",
    WORKSPACE / "00_project" / "goal_completion_matrix.md",
    WORKSPACE / "02_experiments" / "scripts" / "GPU_QUEUE.md",
    WORKSPACE / "03_agent_tasks" / "task_board.md",
    WORKSPACE / "03_agent_tasks" / "pending" / "P0_gate1_kd_handoff_card.md",
    WORKSPACE / "04_paper" / "drafts" / "evidence_index.md",
    WORKSPACE / "04_paper" / "drafts" / "finalization_gates.md",
    WORKSPACE / "04_paper" / "drafts" / "paper_claim_evidence_matrix.md",
    WORKSPACE / "04_paper" / "drafts" / "paper_submission_readiness.md",
    WORKSPACE / "04_paper" / "drafts" / "paper_submission_packet.md",
    WORKSPACE / "04_paper" / "drafts" / "writing_status.md",
]

LATEST_ITER_RE = re.compile(r"Latest iter: epoch (?P<epoch>\d+)/120, iter (?P<iter>\d+)/252")
LATEST_EVAL_RE = re.compile(r"Latest eval start: epoch (?P<epoch>\d+)")
CHECKPOINT_PRESENT_RE = re.compile(r"Checkpoint status: `present`")
CHECKPOINT_ABSENT_RE = re.compile(r"Checkpoint status: `absent`")

PROMOTION_PATTERNS = [
    re.compile(r"MobileMamba[^。\n|]*主表"),
    re.compile(r"MobileMamba[^。\n|]*摘要"),
    re.compile(r"MobileMamba[^。\n|]*结论"),
    re.compile(r"MobileMamba[^.\n|]*main table", re.I),
    re.compile(r"MobileMamba[^.\n|]*accepted main", re.I),
]


@dataclass(frozen=True)
class ResultRow:
    epoch: int
    s: str
    wf: str
    mean_f: str
    mean_e: str
    mae: str

    @property
    def tokens(self) -> list[str]:
        return [self.s, self.wf, self.mean_f, self.mean_e, self.mae]

    @property
    def compact(self) -> str:
        return (
            f"epoch{self.epoch} S={float(self.s):.4f}/wF={float(self.wf):.4f}/"
            f"meanF={float(self.mean_f):.4f}/meanE={float(self.mean_e):.4f}/"
            f"MAE={float(self.mae):.4f}"
        )


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_result_rows(path: Path) -> list[ResultRow]:
    rows: list[ResultRow] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for item in reader:
            rows.append(
                ResultRow(
                    epoch=int(item["epoch"]),
                    s=item["Smeasure"],
                    wf=item["wFmeasure"],
                    mean_f=item["meanFm"],
                    mean_e=item["meanEm"],
                    mae=item["MAE"],
                )
            )
    return rows


def token_present(text: str, token: str) -> bool:
    return token in text or (token.startswith("0.") and token[1:] in text)


def line_context(text: str, start: int, end: int) -> str:
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", end)
    if line_end == -1:
        line_end = len(text)
    return text[line_start:line_end]


def parse_latest_iter(status_text: str) -> str:
    match = LATEST_ITER_RE.search(status_text)
    if not match:
        return "unknown"
    return f"epoch {match.group('epoch')}/120 iter {match.group('iter')}/252"


def parse_latest_eval_epoch(status_text: str) -> int | None:
    match = LATEST_EVAL_RE.search(status_text)
    if not match:
        return None
    return int(match.group("epoch"))


def audit_target(
    target: Path,
    *,
    latest_row: ResultRow | None,
    best_row: ResultRow | None,
    checkpoint_present: bool,
) -> tuple[list[str], list[str]]:
    findings: list[str] = []
    notes: list[str] = []
    if not target.is_file():
        findings.append(f"missing target: {target}")
        return findings, notes

    text = read_text(target)
    mentions_branch = "MobileMamba" in text or "mobilemamba_t2" in text
    if not mentions_branch:
        notes.append(f"{target}: no MobileMamba mention")
        return findings, notes

    if "external_dirty_tree_observation_only" not in text and "observation only" not in text:
        findings.append(f"{target}: missing MobileMamba observation-only boundary")

    if latest_row:
        missing_latest = [token for token in latest_row.tokens if not token_present(text, token)]
        delegates_latest_state = (
            "mobilemamba_t2_external_status_latest.md" in text
            or "orchestrator_tick_latest.md" in text
        )
        if missing_latest and not delegates_latest_state:
            findings.append(
                f"{target}: missing latest MobileMamba tokens {missing_latest} "
                f"from {latest_row.compact}"
            )
        if f"epoch{latest_row.epoch}" not in text and f"epoch {latest_row.epoch}" not in text and not delegates_latest_state:
            findings.append(f"{target}: missing latest MobileMamba epoch {latest_row.epoch}")

    if best_row and "best" in text.lower() or ("最高" in text):
        if best_row:
            missing_best = [token for token in best_row.tokens if not token_present(text, token)]
            if missing_best:
                findings.append(
                    f"{target}: mentions MobileMamba best/highest observation but misses "
                    f"tokens {missing_best} from {best_row.compact}"
                )

    if checkpoint_present:
        stale_absent_markers = ["checkpoint 仍 absent", "no checkpoint yet", "Checkpoint status: `absent`"]
        for marker in stale_absent_markers:
            if marker in text:
                findings.append(f"{target}: stale MobileMamba checkpoint-absent marker `{marker}`")

    for pattern in PROMOTION_PATTERNS:
        for match in pattern.finditer(text):
            context = line_context(text, match.start(), match.end())
            safe_context = any(
                marker in context
                for marker in [
                    "不能",
                    "不进入",
                    "不得",
                    "不把",
                    "not in",
                    "Do not",
                    "do not",
                    "until",
                    "除非",
                ]
            )
            if not safe_context:
                findings.append(f"{target}: possible MobileMamba promotion wording `{match.group(0)}`")

    notes.append(f"{target}: scanned")
    return findings, notes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status", type=Path, default=DEFAULT_STATUS)
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    parser.add_argument("--out_md", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--targets", nargs="*", default=[str(item) for item in DEFAULT_TARGETS])
    args = parser.parse_args()

    findings: list[str] = []
    notes: list[str] = []

    if not args.status.is_file():
        findings.append(f"missing status file: {args.status}")
        status_text = ""
    else:
        status_text = read_text(args.status)

    if not args.result.is_file():
        findings.append(f"missing result file: {args.result}")
        rows: list[ResultRow] = []
    else:
        rows = parse_result_rows(args.result)

    latest_row = max(rows, key=lambda row: row.epoch) if rows else None
    best_row = max(rows, key=lambda row: float(row.s)) if rows else None
    checkpoint_present = bool(CHECKPOINT_PRESENT_RE.search(status_text)) and not bool(
        CHECKPOINT_ABSENT_RE.search(status_text)
    )

    notes.append(f"latest_iter={parse_latest_iter(status_text)}")
    notes.append(f"latest_eval_epoch={parse_latest_eval_epoch(status_text)}")
    notes.append(f"checkpoint_present={checkpoint_present}")
    if latest_row:
        notes.append(f"latest_result={latest_row.compact}")
    if best_row:
        notes.append(f"best_s_result={best_row.compact}")

    for target in [Path(item).expanduser().resolve() for item in args.targets]:
        target_findings, target_notes = audit_target(
            target,
            latest_row=latest_row,
            best_row=best_row,
            checkpoint_present=checkpoint_present,
        )
        findings.extend(target_findings)
        notes.extend(target_notes)

    status = "pass" if not findings else "fail"
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(
        "\n".join(
            [
                "# MobileMamba Status Consistency Audit",
                "",
                f"- Status: `{status}`",
                f"- Status file: `{args.status}`",
                f"- Result file: `{args.result}`",
                f"- Targets: {len(args.targets)}",
                f"- Findings: {len(findings)}",
                "",
                "## Findings",
                "",
                *([f"- {item}" for item in findings] or ["- none"]),
                "",
                "## Notes",
                "",
                *[f"- {item}" for item in notes],
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    for finding in findings:
        print(f"ERROR: {finding}", file=sys.stderr)
    print(f"mobilemamba_status_consistency_audit={status}")
    print(f"report={args.out_md}")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
