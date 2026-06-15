#!/usr/bin/env python3
"""Audit key numbers in the interim submission against CSV evidence."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path


WORKSPACE = Path("/root/data-tmp/workspace")
DEFAULT_PAPER = WORKSPACE / "04_paper" / "drafts" / "paper_interim_submission.md"
DEFAULT_METRICS = WORKSPACE / "02_experiments" / "tables" / "metrics_all.csv"
DEFAULT_PROFILES = WORKSPACE / "02_experiments" / "tables" / "profiles.csv"
DEFAULT_OUT = WORKSPACE / "04_paper" / "drafts" / "interim_submission_number_audit_latest.md"

DATASETS = ["CAMO", "COD10K", "NC4K"]
METRICS = ["Smeasure", "wFmeasure", "meanFm", "meanEm", "MAE"]
HISTORICAL_BASELINE_EXP = "baseline_escnet_b5_416_e120"
CLEAN_BASELINE_EXP = "baseline_escnet_b5_clean_prob_e120"
LIGHT_EXP = "light_b2_c64_e120_s42_prob_eval_v2"
BASELINE_PROFILE = "baseline_escnet_b5_416_e120"
LIGHT_PROFILE = "light_b2_c64_trained_416"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def fnum(value: str) -> float:
    return float(value)


def metric_rows(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    rows = read_csv(path)
    return {
        (row["exp_id"], row["dataset"]): row
        for row in rows
        if row.get("exp_id") and row.get("dataset")
    }


def choose_baseline_exp(rows: dict[tuple[str, str], dict[str, str]]) -> str:
    clean_complete = all(
        rows.get((CLEAN_BASELINE_EXP, dataset), {}).get("status") == "clean_prob_re_eval_complete"
        for dataset in DATASETS
    )
    return CLEAN_BASELINE_EXP if clean_complete else HISTORICAL_BASELINE_EXP


def profile_rows(path: Path) -> dict[str, dict[str, str]]:
    return {row["exp_id"]: row for row in read_csv(path) if row.get("exp_id")}


def mean_metric(rows: dict[tuple[str, str], dict[str, str]], exp_id: str, metric: str) -> float:
    return sum(fnum(rows[(exp_id, dataset)][metric]) for dataset in DATASETS) / len(DATASETS)


def expect_contains(text: str, needle: str, findings: list[str], label: str) -> None:
    if needle not in text:
        findings.append(f"missing {label}: expected literal `{needle}`")


def expect_table_row(
    text: str,
    model: str,
    dataset: str,
    values: list[str],
    findings: list[str],
) -> None:
    pattern = re.compile(rf"^\| {re.escape(model)} \| {re.escape(dataset)} \| (?P<body>.+?) \|$", re.M)
    match = pattern.search(text)
    if not match:
        findings.append(f"missing metric table row for {model}/{dataset}")
        return
    row_text = match.group(0)
    for value in values:
        if value not in row_text:
            findings.append(f"{model}/{dataset} row missing value `{value}`")


def pct_reduction(reference: float, light: float) -> float:
    return (reference - light) / reference * 100.0


def audit(args: argparse.Namespace) -> tuple[list[str], list[str]]:
    paper_path = Path(args.paper)
    text = paper_path.read_text(encoding="utf-8")
    metrics = metric_rows(Path(args.metrics_csv))
    profiles = profile_rows(Path(args.profiles_csv))

    findings: list[str] = []
    notes: list[str] = []

    baseline_exp = choose_baseline_exp(metrics)
    notes.append(f"baseline exp: {baseline_exp}")

    required_metric_keys = [
        (exp_id, dataset)
        for exp_id in [baseline_exp, LIGHT_EXP]
        for dataset in DATASETS
    ]
    for key in required_metric_keys:
        if key not in metrics:
            findings.append(f"missing metrics row: {key[0]}/{key[1]}")

    for exp_id in [BASELINE_PROFILE, LIGHT_PROFILE]:
        if exp_id not in profiles:
            findings.append(f"missing profile row: {exp_id}")

    if findings:
        return findings, notes

    baseline_s = mean_metric(metrics, baseline_exp, "Smeasure")
    light_s = mean_metric(metrics, LIGHT_EXP, "Smeasure")
    baseline_mae = mean_metric(metrics, baseline_exp, "MAE")
    light_mae = mean_metric(metrics, LIGHT_EXP, "MAE")

    for label, value in [
        ("baseline mean S", baseline_s),
        ("light mean S", light_s),
        ("baseline mean MAE", baseline_mae),
        ("light mean MAE", light_mae),
    ]:
        literal = f"{value:.3f}"
        expect_contains(text, literal, findings, label)
        notes.append(f"{label}: {literal}")

    for exp_id, display in [
        (baseline_exp, "ESCNet-B5 C128"),
        (LIGHT_EXP, "Light-ESCNet B2-C64"),
    ]:
        for dataset in DATASETS:
            row = metrics[(exp_id, dataset)]
            values = [f"{fnum(row[metric]):.3f}" for metric in METRICS]
            expect_table_row(text, display, dataset, values, findings)
            notes.append(f"{display}/{dataset}: " + ", ".join(values))

    baseline_profile = profiles[BASELINE_PROFILE]
    light_profile = profiles[LIGHT_PROFILE]
    params_ref = fnum(baseline_profile["params"]) / 1_000_000.0
    params_light = fnum(light_profile["params"]) / 1_000_000.0
    gmacs_ref = fnum(baseline_profile["gmacs"])
    gmacs_light = fnum(light_profile["gmacs"])
    size_ref = fnum(baseline_profile["model_size_mb"])
    size_light = fnum(light_profile["model_size_mb"])
    mem_ref = fnum(baseline_profile["peak_mem_mb"])
    mem_light = fnum(light_profile["peak_mem_mb"])

    profile_literals = [
        ("baseline params", f"{params_ref:.2f}M"),
        ("light params", f"{params_light:.2f}M"),
        ("baseline gmacs", f"{gmacs_ref:.2f}"),
        ("light gmacs", f"{gmacs_light:.2f}"),
        ("baseline model size", f"{size_ref:.2f} MB"),
        ("light model size", f"{size_light:.2f} MB"),
        ("baseline peak mem", f"{mem_ref:.2f} MB"),
        ("light peak mem", f"{mem_light:.2f} MB"),
        ("params reduction", f"{pct_reduction(params_ref, params_light):.2f}%"),
        ("gmacs reduction", f"{pct_reduction(gmacs_ref, gmacs_light):.2f}%"),
        ("model size reduction", f"{pct_reduction(size_ref, size_light):.2f}%"),
        ("peak mem reduction", f"{pct_reduction(mem_ref, mem_light):.2f}%"),
    ]
    for label, literal in profile_literals:
        expect_contains(text, literal, findings, label)
        notes.append(f"{label}: {literal}")

    forbidden_literals = [
        "final clean probability baseline",
        "KD 进一步",
        "KD 提升",
        "蒸馏有效",
        "实时部署",
        "SOTA",
    ]
    for literal in forbidden_literals:
        if literal in text:
            findings.append(f"forbidden over-claim literal present: `{literal}`")

    return findings, notes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper", default=str(DEFAULT_PAPER))
    parser.add_argument("--metrics_csv", default=str(DEFAULT_METRICS))
    parser.add_argument("--profiles_csv", default=str(DEFAULT_PROFILES))
    parser.add_argument("--out_md", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    findings, notes = audit(args)
    status = "pass" if not findings else "fail"
    out_path = Path(args.out_md)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        "\n".join(
            [
                "# Interim Submission Number Audit",
                "",
                f"- Status: `{status}`",
                f"- Paper: `{Path(args.paper)}`",
                f"- Metrics CSV: `{Path(args.metrics_csv)}`",
                f"- Profiles CSV: `{Path(args.profiles_csv)}`",
                f"- Findings: {len(findings)}",
                "",
                "## Findings",
                "",
                *([f"- {item}" for item in findings] or ["- none"]),
                "",
                "## Checked Values",
                "",
                *([f"- {item}" for item in notes] or ["- none"]),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    for finding in findings:
        print(f"ERROR: {finding}", file=sys.stderr)
    print(f"interim_submission_number_audit={status}")
    print(f"report={out_path}")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
