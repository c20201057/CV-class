#!/usr/bin/env python3
"""Audit paper-table evidence boundaries from metrics_all.csv.

This script is intentionally conservative about what can be called final
paper evidence. It does not compute metrics; it checks whether existing rows
carry enough metadata and whether final-status rows cover all required
datasets.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path


REQUIRED_COLUMNS = [
    "exp_id",
    "dataset",
    "method",
    "Smeasure",
    "wFmeasure",
    "meanFm",
    "meanEm",
    "MAE",
    "source",
    "protocol",
    "repo_boundary",
    "checkpoint",
    "status",
]
REQUIRED_DATASETS = {"CAMO", "COD10K", "NC4K"}
FINAL_STATUSES = {
    "final_main_light",
    "final_main_kd",
    "clean_prob_re_eval_complete",
}
REFERENCE_ONLY_STATUSES = {
    "historical_reference_not_clean_prob_final",
    "verification_only_camo",
    "external_dirty_tree_observation_candidate",
}
FORBIDDEN_FINAL_REPO_BOUNDARIES = {
    "dirty_history_result",
    "legacy_repo_camo_verification",
}
ALLOWED_FINAL_CHECKPOINT_PREFIXES = (
    "/root/data-tmp/workspace/",
    "/root/data-tmp/epoch_120.pth",
)


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), [dict(row) for row in reader]


def existing_path(value: str) -> bool:
    return bool(value) and Path(value).expanduser().exists()


def allowed_final_checkpoint(value: str) -> bool:
    return any(value == prefix or value.startswith(prefix) for prefix in ALLOWED_FINAL_CHECKPOINT_PREFIXES)


def row_id(row: dict[str, str]) -> str:
    return f"{row.get('exp_id', '')}/{row.get('dataset', '')}/{row.get('method', '')}"


def audit(metrics_csv: Path) -> tuple[list[str], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []

    if not metrics_csv.is_file():
        return [f"Missing metrics CSV: {metrics_csv}"], warnings, notes

    columns, rows = read_rows(metrics_csv)
    missing_cols = [column for column in REQUIRED_COLUMNS if column not in columns]
    if missing_cols:
        errors.append(f"Missing required columns: {', '.join(missing_cols)}")
        return errors, warnings, notes

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        exp_id = row.get("exp_id", "")
        grouped[exp_id].append(row)
        for column in REQUIRED_COLUMNS:
            if not row.get(column, "").strip():
                errors.append(f"{row_id(row)} has empty required column `{column}`")

        status = row.get("status", "")
        protocol = row.get("protocol", "")
        repo_boundary = row.get("repo_boundary", "")
        checkpoint = row.get("checkpoint", "")
        exp_lower = exp_id.lower()

        if status in FINAL_STATUSES and protocol != "prob_map":
            errors.append(
                f"{row_id(row)} has final status `{status}` but protocol `{protocol}`"
            )
        if status in FINAL_STATUSES:
            if not existing_path(row.get("source", "")):
                errors.append(f"{row_id(row)} final row source path does not exist")
            if not existing_path(checkpoint):
                errors.append(f"{row_id(row)} final row checkpoint path does not exist")
            if repo_boundary in FORBIDDEN_FINAL_REPO_BOUNDARIES:
                errors.append(
                    f"{row_id(row)} final row uses forbidden repo_boundary `{repo_boundary}`"
                )
            if not allowed_final_checkpoint(checkpoint):
                errors.append(
                    f"{row_id(row)} final row checkpoint is outside allowed final evidence roots: {checkpoint}"
                )
        if status in REFERENCE_ONLY_STATUSES:
            notes.append(f"{row_id(row)} is reference/verification only: {status}")
        if re.search(r"(?:^|[_-])(b0|pvt_v2_b0)(?:$|[_-])", exp_lower) and status in FINAL_STATUSES:
            errors.append(f"{row_id(row)} is a B0/extreme branch marked as final")

    for exp_id, exp_rows in sorted(grouped.items()):
        datasets = {row.get("dataset", "") for row in exp_rows}
        statuses = {row.get("status", "") for row in exp_rows}
        if statuses & FINAL_STATUSES:
            missing = sorted(REQUIRED_DATASETS - datasets)
            if missing:
                errors.append(
                    f"{exp_id} has final evidence status but misses datasets: {', '.join(missing)}"
                )
            mixed_reference = sorted(statuses & REFERENCE_ONLY_STATUSES)
            if mixed_reference:
                errors.append(
                    f"{exp_id} mixes final and reference-only statuses: {', '.join(mixed_reference)}"
                )
        if "verification_only_camo" in statuses and datasets != {"CAMO"}:
            warnings.append(
                f"{exp_id} is marked verification_only_camo but has datasets {sorted(datasets)}"
            )

    if not rows:
        warnings.append("metrics CSV has no rows")
    return errors, warnings, notes


def write_report(
    out_md: Path | None,
    metrics_csv: Path,
    errors: list[str],
    warnings: list[str],
    notes: list[str],
) -> None:
    if out_md is None:
        return
    out_md.parent.mkdir(parents=True, exist_ok=True)
    status = "pass" if not errors else "fail"
    lines = [
        "# Paper Evidence Audit",
        "",
        f"- Metrics CSV: `{metrics_csv}`",
        f"- Status: `{status}`",
        f"- Errors: {len(errors)}",
        f"- Warnings: {len(warnings)}",
        "",
        "## Errors",
        "",
    ]
    lines.extend([f"- {item}" for item in errors] or ["- none"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {item}" for item in warnings] or ["- none"])
    lines.extend(["", "## Reference Notes", ""])
    lines.extend([f"- {item}" for item in notes] or ["- none"])
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit paper evidence metadata.")
    parser.add_argument(
        "--metrics_csv",
        default="/root/data-tmp/workspace/02_experiments/tables/metrics_all.csv",
    )
    parser.add_argument(
        "--out_md",
        default="/root/data-tmp/workspace/04_paper/drafts/paper_evidence_audit_latest.md",
    )
    args = parser.parse_args()

    metrics_csv = Path(args.metrics_csv).expanduser().resolve()
    out_md = Path(args.out_md).expanduser().resolve() if args.out_md else None
    errors, warnings, notes = audit(metrics_csv)
    write_report(out_md, metrics_csv, errors, warnings, notes)

    for warning in warnings:
        print(f"WARNING: {warning}")
    for note in notes:
        print(f"NOTE: {note}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    print(f"paper_evidence_audit={'pass' if not errors else 'fail'}")
    if out_md:
        print(f"report={out_md}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
