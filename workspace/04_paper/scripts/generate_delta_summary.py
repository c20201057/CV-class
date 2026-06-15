#!/usr/bin/env python3
"""Generate paper-ready delta summaries from metrics and profile CSV files."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


DATASETS = ["CAMO", "COD10K", "NC4K"]
METRICS = ["Smeasure", "wFmeasure", "meanFm", "meanEm", "MAE"]

DEFAULT_WORKSPACE = Path("/root/data-tmp/workspace")
DEFAULT_METRICS = DEFAULT_WORKSPACE / "02_experiments" / "tables" / "metrics_all.csv"
DEFAULT_PROFILES = DEFAULT_WORKSPACE / "02_experiments" / "tables" / "profiles.csv"
DEFAULT_OUT = DEFAULT_WORKSPACE / "04_paper" / "drafts" / "current_delta_summary.md"
HISTORICAL_BASELINE_EXP = "baseline_escnet_b5_416_e120"
CLEAN_BASELINE_EXP = "baseline_escnet_b5_clean_prob_e120"
LIGHT_EXP = "light_b2_c64_e120_s42_prob_eval_v2"
KD_EXP = "kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval"
BASELINE_PROFILE_EXP = "baseline_escnet_b5_416_idle"
LIGHT_PROFILE_EXP = "light_b2_c64_trained_416_idle"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def rows_by_exp_dataset(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    result: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        exp_id = row.get("exp_id", "")
        dataset = row.get("dataset", "")
        if exp_id and dataset:
            result[(exp_id, dataset)] = row
    return result


def rows_by_exp(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    result: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        exp_id = row.get("exp_id", "")
        if exp_id:
            result[exp_id].append(row)
    return result


def profile_by_exp(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("exp_id", ""): row for row in rows if row.get("exp_id", "")}


def fnum(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def fmt(value: float | None, digits: int = 3) -> str:
    if value is None:
        return "TBD"
    return f"{value:.{digits}f}"


def fmt_signed(value: float | None, digits: int = 3) -> str:
    if value is None:
        return "TBD"
    return f"{value:+.{digits}f}"


def fmt_pct(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "TBD"
    return f"{value:.{digits}f}%"


def metric_status(rows: list[dict[str, str]]) -> str:
    statuses = sorted({row.get("status", "") for row in rows if row.get("status", "")})
    return ", ".join(statuses) if statuses else "missing"


def has_three_dataset_status(
    by_key: dict[tuple[str, str], dict[str, str]],
    exp_id: str,
    status: str,
) -> bool:
    return all(
        by_key.get((exp_id, dataset), {}).get("status", "") == status
        for dataset in DATASETS
    )


def complete_three_dataset_exp(
    by_key: dict[tuple[str, str], dict[str, str]],
    exp_id: str,
) -> bool:
    return all((exp_id, dataset) in by_key for dataset in DATASETS)


def choose_reference_exp(by_key: dict[tuple[str, str], dict[str, str]]) -> tuple[str, str]:
    if has_three_dataset_status(by_key, CLEAN_BASELINE_EXP, "clean_prob_re_eval_complete"):
        return CLEAN_BASELINE_EXP, "clean ESCNet-B5 probability baseline"
    return HISTORICAL_BASELINE_EXP, "historical ESCNet-B5 reference row"


def mean_metric(
    by_key: dict[tuple[str, str], dict[str, str]],
    exp_id: str,
    metric: str,
) -> float | None:
    values: list[float] = []
    for dataset in DATASETS:
        value = fnum(by_key.get((exp_id, dataset), {}).get(metric))
        if value is None:
            return None
        values.append(value)
    return sum(values) / len(values)


def delta_table(
    by_key: dict[tuple[str, str], dict[str, str]],
    reference_exp: str,
    light_exp: str,
) -> str:
    lines = [
        "| Dataset | Ref S | Light S | Delta S | Ref wF | Light wF | Delta wF | Ref MAE | Light MAE | Delta MAE |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for dataset in DATASETS:
        ref = by_key.get((reference_exp, dataset), {})
        light = by_key.get((light_exp, dataset), {})
        ref_s = fnum(ref.get("Smeasure"))
        light_s = fnum(light.get("Smeasure"))
        ref_wf = fnum(ref.get("wFmeasure"))
        light_wf = fnum(light.get("wFmeasure"))
        ref_mae = fnum(ref.get("MAE"))
        light_mae = fnum(light.get("MAE"))
        lines.append(
            "| "
            + " | ".join(
                [
                    dataset,
                    fmt(ref_s),
                    fmt(light_s),
                    fmt_signed(None if ref_s is None or light_s is None else light_s - ref_s),
                    fmt(ref_wf),
                    fmt(light_wf),
                    fmt_signed(None if ref_wf is None or light_wf is None else light_wf - ref_wf),
                    fmt(ref_mae),
                    fmt(light_mae),
                    fmt_signed(None if ref_mae is None or light_mae is None else light_mae - ref_mae),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def mean_delta_table(
    by_key: dict[tuple[str, str], dict[str, str]],
    reference_exp: str,
    light_exp: str,
) -> str:
    lines = [
        "| Metric | Reference Mean | Light Mean | Delta Light-Reference |",
        "| --- | ---: | ---: | ---: |",
    ]
    for metric in METRICS:
        ref_mean = mean_metric(by_key, reference_exp, metric)
        light_mean = mean_metric(by_key, light_exp, metric)
        delta = None if ref_mean is None or light_mean is None else light_mean - ref_mean
        lines.append(f"| {metric} | {fmt(ref_mean)} | {fmt(light_mean)} | {fmt_signed(delta)} |")
    return "\n".join(lines)


def reduction_table(
    profiles: dict[str, dict[str, str]],
    reference_exp: str,
    light_exp: str,
) -> str:
    refs = profiles.get(reference_exp, {})
    lights = profiles.get(light_exp, {})
    fields = [
        ("params", "Params"),
        ("gmacs", "GMACs"),
        ("model_size_mb", "Model size MB"),
        ("peak_mem_mb", "Peak memory MB"),
    ]
    lines = [
        "| Quantity | Reference | Light | Reduction |",
        "| --- | ---: | ---: | ---: |",
    ]
    for key, label in fields:
        ref_value = fnum(refs.get(key))
        light_value = fnum(lights.get(key))
        reduction = None
        if ref_value and light_value is not None:
            reduction = (ref_value - light_value) / ref_value * 100.0
        if key == "params":
            ref_display = None if ref_value is None else ref_value / 1_000_000.0
            light_display = None if light_value is None else light_value / 1_000_000.0
            lines.append(
                f"| {label} | {fmt(ref_display, 2)}M | {fmt(light_display, 2)}M | {fmt_pct(reduction)} |"
            )
        else:
            lines.append(
                f"| {label} | {fmt(ref_value, 2)} | {fmt(light_value, 2)} | {fmt_pct(reduction)} |"
            )
    return "\n".join(lines)


def gate_status(
    by_key: dict[tuple[str, str], dict[str, str]],
    profiles: dict[str, dict[str, str]],
) -> str:
    gate1 = has_three_dataset_status(
        by_key,
        "baseline_escnet_b5_clean_prob_e120",
        "clean_prob_re_eval_complete",
    )
    gate2 = has_three_dataset_status(
        by_key,
        "kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval",
        "final_main_kd",
    )
    gate3 = (
        "baseline_escnet_b5_416_idle" in profiles
        and "light_b2_c64_trained_416_idle" in profiles
        and "kd_light_b2_c64_trained_416_idle" in profiles
    )
    rows = [
        "| Gate | Status | Paper Action |",
        "| --- | --- | --- |",
        (
            "| Gate 1 clean baseline | "
            + ("pass" if gate1 else "pending")
            + " | "
            + (
                "Promote ESCNet-B5 to clean probability baseline."
                if gate1
                else "Keep ESCNet-B5 as historical/reference only."
            )
            + " |"
        ),
        (
            "| Gate 2 KD | "
            + ("pass" if gate2 else "pending")
            + " | "
            + (
                "Add KD result and rewrite KD claims according to measured deltas."
                if gate2
                else "Keep KD as implemented but not yet validated."
            )
            + " |"
        ),
        (
            "| Gate 3 speed | "
            + ("pass" if gate3 else "pending")
            + " | "
            + (
                "Latency/FPS can be reported if same-command idle profiles agree."
                if gate3
                else "Do not report final latency/FPS speedup."
            )
            + " |"
        ),
    ]
    return "\n".join(rows)


def comparison_section(
    by_key: dict[tuple[str, str], dict[str, str]],
    reference_exp: str,
    reference_label: str,
    target_exp: str,
    target_label: str,
) -> list[str]:
    if not complete_three_dataset_exp(by_key, reference_exp):
        return [
            f"## {target_label} vs {reference_label}",
            "",
            f"- skipped: reference `{reference_exp}` is incomplete.",
            "",
        ]
    if not complete_three_dataset_exp(by_key, target_exp):
        return [
            f"## {target_label} vs {reference_label}",
            "",
            f"- skipped: target `{target_exp}` is incomplete.",
            "",
        ]
    return [
        f"## {target_label} vs {reference_label}",
        "",
        delta_table(by_key, reference_exp, target_exp),
        "",
        "### Three-Dataset Mean Deltas",
        "",
        mean_delta_table(by_key, reference_exp, target_exp),
        "",
    ]


def write_summary(
    metrics_rows: list[dict[str, str]],
    profile_rows: list[dict[str, str]],
    out_path: Path,
) -> None:
    by_key = rows_by_exp_dataset(metrics_rows)
    grouped = rows_by_exp(metrics_rows)
    profiles = profile_by_exp(profile_rows)
    reference_exp, reference_label = choose_reference_exp(by_key)
    kd_complete = has_three_dataset_status(by_key, KD_EXP, "final_main_kd")
    clean_complete = reference_exp == CLEAN_BASELINE_EXP

    lines = [
        "# Current Delta Summary",
        "",
        "This file is generated from `metrics_all.csv` and `profiles.csv`.",
        "It is safe to cite only within the evidence boundaries shown below.",
        "",
        "## Evidence Status",
        "",
        f"- Historical ESCNet-B5 status: `{metric_status(grouped.get(HISTORICAL_BASELINE_EXP, []))}`.",
        f"- Clean ESCNet-B5 status: `{metric_status(grouped.get(CLEAN_BASELINE_EXP, []))}`.",
        f"- Light B2-C64 status: `{metric_status(grouped.get(LIGHT_EXP, []))}`.",
        f"- KD B2-C64 status: `{metric_status(grouped.get(KD_EXP, []))}`.",
        f"- Active reference for delta tables: `{reference_exp}` ({reference_label}).",
        (
            "- Current Light-vs-ESCNet deltas are clean same-protocol deltas."
            if clean_complete
            else "- Current Light-vs-ESCNet deltas are relative to the historical reference row, not the final clean probability baseline."
        ),
        "",
        "## Light B2-C64 vs Active ESCNet Reference",
        "",
        delta_table(by_key, reference_exp, LIGHT_EXP),
        "",
        "### Three-Dataset Mean Deltas",
        "",
        mean_delta_table(by_key, reference_exp, LIGHT_EXP),
        "",
        "## Structural Reductions",
        "",
        reduction_table(profiles, BASELINE_PROFILE_EXP, LIGHT_PROFILE_EXP),
        "",
        "## Gate Status",
        "",
        gate_status(by_key, profiles),
        "",
    ]
    if kd_complete:
        lines.extend(
            comparison_section(
                by_key,
                LIGHT_EXP,
                "Light B2-C64 no-KD",
                KD_EXP,
                "KD B2-C64",
            )
        )
        lines.extend(
            comparison_section(
                by_key,
                reference_exp,
                reference_label,
                KD_EXP,
                "KD B2-C64",
            )
        )
    else:
        lines.extend(
            [
                "## KD Comparisons",
                "",
                "- skipped: KD three-dataset final evidence is not complete.",
                "",
            ]
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics_csv", default=str(DEFAULT_METRICS))
    parser.add_argument("--profiles_csv", default=str(DEFAULT_PROFILES))
    parser.add_argument("--out_md", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    metrics_rows = read_csv(Path(args.metrics_csv).expanduser())
    profile_rows = read_csv(Path(args.profiles_csv).expanduser())
    out_path = Path(args.out_md).expanduser()
    write_summary(metrics_rows, profile_rows, out_path)
    print(f"delta_summary={out_path}")


if __name__ == "__main__":
    main()
