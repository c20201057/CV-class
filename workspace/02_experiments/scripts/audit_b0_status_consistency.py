#!/usr/bin/env python3
"""Audit external B0 status notes for stale evidence-boundary wording."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path


WORKSPACE = Path("/root/data-tmp/workspace")
DEFAULT_STATUS = WORKSPACE / "02_experiments" / "runs" / "b0_external_status_latest.md"
DEFAULT_RESULT = Path("/root/data-tmp/results_train/pvt_v2_b0/result.txt")
DEFAULT_OUT = WORKSPACE / "04_paper" / "drafts" / "b0_status_consistency_audit_latest.md"
DEFAULT_TARGETS = [
    WORKSPACE / "00_project" / "route_decision.md",
    WORKSPACE / "00_project" / "orchestrator_status.md",
    WORKSPACE / "00_project" / "resume_handoff.md",
    WORKSPACE / "00_project" / "current_run_snapshot.md",
    WORKSPACE / "02_experiments" / "scripts" / "GPU_QUEUE.md",
    WORKSPACE / "02_experiments" / "runs" / "b0_external_observation.md",
    WORKSPACE / "02_experiments" / "runs" / "b0_intermediate_trend_note.md",
    WORKSPACE / "04_paper" / "drafts" / "b0_cod10k_trend_note.md",
    WORKSPACE / "03_agent_tasks" / "task_board.md",
    WORKSPACE / "04_paper" / "drafts" / "evidence_index.md",
    WORKSPACE / "04_paper" / "drafts" / "finalization_gates.md",
    WORKSPACE / "04_paper" / "drafts" / "claim_evidence_audit.md",
    WORKSPACE / "04_paper" / "drafts" / "paper_claim_evidence_matrix.md",
    WORKSPACE / "04_paper" / "drafts" / "paper_submission_readiness.md",
    WORKSPACE / "04_paper" / "drafts" / "teacher_share_pack.md",
    WORKSPACE / "04_paper" / "drafts" / "paper_draft.md",
    WORKSPACE / "04_paper" / "drafts" / "paper_interim_submission.md",
    WORKSPACE / "04_paper" / "drafts" / "presentation_outline.md",
    WORKSPACE / "04_paper" / "drafts" / "writing_status.md",
    WORKSPACE / "04_paper" / "tables" / "main_results_template.md",
]

CHECKPOINT_STALE_PATTERNS = [
    re.compile(r"No checkpoint has appeared", re.I),
    re.compile(r"No `\*\.pth` checkpoint has been found", re.I),
    re.compile(r"no checkpoint; observe", re.I),
    re.compile(r"no checkpoint \|", re.I),
    re.compile(r"无 checkpoint"),
    re.compile(r"尚无 checkpoint"),
    re.compile(r"checkpoint 目录仍只有"),
    re.compile(r"只有 `log\.txt`"),
    re.compile(r"only `log\.txt` exists", re.I),
]

METRICS_PENDING_PATTERNS = [
    re.compile(r"metrics pending", re.I),
    re.compile(r"metrics row pending", re.I),
    re.compile(r"metrics are pending", re.I),
    re.compile(r"metrics have not yet been appended", re.I),
    re.compile(r"metrics 行尚未"),
    re.compile(r"尚未写入 result"),
    re.compile(r"尚未落表"),
    re.compile(r"eval 已启动但 metrics"),
]

B0_STALE_LATEST_PATTERNS = [
    re.compile(
        r"epoch[_ ]?(?P<epoch>\d+)[^。\n.;；]{0,80}"
        r"(?:latest complete|latest completed|latest row|latest result|最新完整|最新已落表|最新结果)",
        re.I,
    ),
    re.compile(
        r"(?:latest complete|latest completed|latest row|latest result|最新完整|最新已落表|最新结果)"
        r"[^。\n.;；]{0,80}epoch[_ ]?(?P<epoch>\d+)",
        re.I,
    ),
]

B0_STALE_BEST_PATTERNS = [
    re.compile(
        r"epoch[_ ]?(?P<epoch>\d+)[^。\n.;；]{0,80}"
        r"(?:best|strongest|current best|最好|最强|当前最好)",
        re.I,
    ),
    re.compile(
        r"(?:best|strongest|current best|最好|最强|当前最好)"
        r"[^。\n.;；]{0,80}epoch[_ ]?(?P<epoch>\d+)",
        re.I,
    ),
]

LATEST_ITER_RE = re.compile(r"Latest iter: epoch (?P<epoch>\d+)/120, iter (?P<iter>\d+)/252")
LATEST_EVAL_RE = re.compile(r"Latest eval start: epoch (?P<epoch>\d+)")


@dataclass(frozen=True)
class ResultRow:
    epoch: int
    s: str
    wf: str
    mean_f: str
    mean_e: str
    mae: str

    @property
    def csv_line(self) -> str:
        return ",".join([str(self.epoch), self.s, self.wf, self.mean_f, self.mean_e, self.mae])

    @property
    def compact_metrics(self) -> str:
        return f"S={float(self.s):.4f}/wF={float(self.wf):.4f}/MAE={float(self.mae):.4f}"

    @property
    def markdown_row(self) -> str:
        return f"| {self.epoch} | {self.s} | {self.wf} | {self.mean_f} | {self.mean_e} | {self.mae} |"


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


def checkpoint_paths() -> list[Path]:
    ckpt_dir = Path("/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0")
    return sorted(
        ckpt_dir.glob("epoch_*.pth"),
        key=lambda item: int(re.search(r"epoch_(\d+)\.pth", item.name).group(1))
        if re.search(r"epoch_(\d+)\.pth", item.name)
        else -1,
    )


def has_checkpoint(status_text: str, checkpoints: list[Path]) -> bool:
    return "Checkpoint status: `present`" in status_text or bool(checkpoints)


def audit_target(
    target: Path,
    *,
    checkpoint_present: bool,
    latest_checkpoint_name: str | None,
    metrics_appended_epochs: set[int],
    metrics_pending_allowed: bool,
    latest_row: ResultRow | None,
    best_epochs: set[int],
) -> tuple[list[str], list[str]]:
    findings: list[str] = []
    notes: list[str] = []
    if not target.is_file():
        findings.append(f"missing target: {target}")
        return findings, notes

    text = read_text(target)
    delegates_latest_state = (
        "b0_external_status_latest.md" in text or "orchestrator_tick_latest.md" in text
    )
    if checkpoint_present:
        for pattern in CHECKPOINT_STALE_PATTERNS:
            for match in pattern.finditer(text):
                findings.append(f"{target}: stale checkpoint wording `{match.group(0)}`")
        if (
            latest_checkpoint_name
            and "epoch_" in text
            and latest_checkpoint_name not in text
            and not delegates_latest_state
        ):
            findings.append(
                f"{target}: mentions B0 checkpoints but misses latest checkpoint "
                f"`{latest_checkpoint_name}`"
            )

    if metrics_appended_epochs and not metrics_pending_allowed:
        for pattern in METRICS_PENDING_PATTERNS:
            for match in pattern.finditer(text):
                findings.append(f"{target}: stale metrics-pending wording `{match.group(0)}`")

    if latest_row and target.name in {
        "b0_external_observation.md",
        "b0_intermediate_trend_note.md",
        "b0_cod10k_trend_note.md",
    }:
        if (
            not delegates_latest_state
            and latest_row.csv_line not in text
            and latest_row.compact_metrics not in text
            and latest_row.markdown_row not in text
        ):
            findings.append(
                f"{target}: missing latest B0 result row for epoch {latest_row.epoch}: "
                f"{latest_row.csv_line}"
            )
        elif delegates_latest_state:
            notes.append(f"{target}: delegates latest B0 row state to live status file")

    if latest_row and ("B0" in text or "PVTv2-B0" in text):
        for pattern in B0_STALE_LATEST_PATTERNS:
            for match in pattern.finditer(text):
                snippet = match.group(0)
                line_start = text.rfind("\n", 0, match.start()) + 1
                line_end = text.find("\n", match.end())
                if line_end == -1:
                    line_end = len(text)
                line_context = text[line_start:line_end]
                if "MobileMamba" in line_context:
                    continue
                epoch_text = match.group("epoch")
                if epoch_text and int(epoch_text) != latest_row.epoch:
                    findings.append(
                        f"{target}: stale B0 latest wording references epoch {epoch_text} "
                        f"while latest result epoch is {latest_row.epoch}: `{snippet}`"
                    )
        for pattern in B0_STALE_BEST_PATTERNS:
            for match in pattern.finditer(text):
                snippet = match.group(0)
                line_start = text.rfind("\n", 0, match.start()) + 1
                line_end = text.find("\n", match.end())
                if line_end == -1:
                    line_end = len(text)
                line_context = text[line_start:line_end]
                if "MobileMamba" in line_context:
                    continue
                epoch_text = match.group("epoch")
                if epoch_text and int(epoch_text) not in best_epochs:
                    findings.append(
                        f"{target}: stale B0 best wording references epoch {epoch_text} "
                        f"while current best epochs are {sorted(best_epochs)}: `{snippet}`"
                    )

    notes.append(f"{target}: scanned")
    return findings, notes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status", default=str(DEFAULT_STATUS))
    parser.add_argument("--result", default=str(DEFAULT_RESULT))
    parser.add_argument("--out_md", default=str(DEFAULT_OUT))
    parser.add_argument("--targets", nargs="*", default=[str(item) for item in DEFAULT_TARGETS])
    args = parser.parse_args()

    status_path = Path(args.status).expanduser().resolve()
    result_path = Path(args.result).expanduser().resolve()
    out_path = Path(args.out_md).expanduser().resolve()
    targets = [Path(item).expanduser().resolve() for item in args.targets]

    findings: list[str] = []
    notes: list[str] = []

    if not status_path.is_file():
        findings.append(f"missing status file: {status_path}")
        status_text = ""
    else:
        status_text = read_text(status_path)

    if not result_path.is_file():
        findings.append(f"missing result file: {result_path}")
        result_rows: list[ResultRow] = []
    else:
        result_rows = parse_result_rows(result_path)

    checkpoints = checkpoint_paths()
    checkpoint_present = has_checkpoint(status_text, checkpoints)
    latest_row = max(result_rows, key=lambda item: item.epoch) if result_rows else None
    best_epochs: set[int] = set()
    if result_rows:
        best_epochs.add(max(result_rows, key=lambda item: float(item.s)).epoch)
        best_epochs.add(max(result_rows, key=lambda item: float(item.wf)).epoch)
        best_epochs.add(max(result_rows, key=lambda item: float(item.mean_f)).epoch)
        best_epochs.add(max(result_rows, key=lambda item: float(item.mean_e)).epoch)
        best_epochs.add(min(result_rows, key=lambda item: float(item.mae)).epoch)
    metrics_appended_epochs = {item.epoch for item in result_rows}
    latest_iter = parse_latest_iter(status_text)
    latest_eval_epoch = parse_latest_eval_epoch(status_text)
    metrics_pending_allowed = (
        latest_eval_epoch is not None and latest_eval_epoch not in metrics_appended_epochs
    )

    notes.append(f"checkpoint_present={checkpoint_present}")
    if checkpoints:
        notes.append(f"latest_checkpoint={checkpoints[-1]}")
        notes.append("checkpoints=" + ",".join(item.name for item in checkpoints))
    notes.append(f"latest_iter={latest_iter}")
    notes.append(f"latest_eval_epoch={latest_eval_epoch}")
    notes.append(f"metrics_pending_allowed={metrics_pending_allowed}")
    if latest_row:
        notes.append(f"latest_result_epoch={latest_row.epoch}")
        notes.append(f"latest_result_metrics={latest_row.compact_metrics}")
    if best_epochs:
        notes.append("best_result_epochs=" + ",".join(str(item) for item in sorted(best_epochs)))

    for target in targets:
        target_findings, target_notes = audit_target(
            target,
            checkpoint_present=checkpoint_present,
            latest_checkpoint_name=checkpoints[-1].name if checkpoints else None,
            metrics_appended_epochs=metrics_appended_epochs,
            metrics_pending_allowed=metrics_pending_allowed,
            latest_row=latest_row,
            best_epochs=best_epochs,
        )
        findings.extend(target_findings)
        notes.extend(target_notes)

    status = "pass" if not findings else "fail"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        "\n".join(
            [
                "# B0 Status Consistency Audit",
                "",
                f"- Status: `{status}`",
                f"- Status file: `{status_path}`",
                f"- Result file: `{result_path}`",
                f"- Targets: {len(targets)}",
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
    print(f"b0_status_consistency_audit={status}")
    print(f"report={out_path}")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
