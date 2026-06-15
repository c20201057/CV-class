#!/usr/bin/env python3
"""Generate compact Markdown tables from metrics/profile CSV files."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


METRIC_ORDER = ["Smeasure", "wFmeasure", "meanFm", "meanEm", "MAE"]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def metric_triplet(row: dict[str, str]) -> str:
    if not row:
        return "TBD"
    return f"{row.get('Smeasure', '')}/{row.get('wFmeasure', '')}/{row.get('MAE', '')}"


def evidence_status(rows: list[dict[str, str]]) -> str:
    statuses = sorted({row.get("status", "") for row in rows if row.get("status", "")})
    if not statuses:
        return "pending"
    return ", ".join(statuses)


def fmt_float(value: str, digits: int = 2) -> str:
    if value in {"", None}:  # type: ignore[comparison-overlap]
        return "TBD"
    try:
        return f"{float(value):.{digits}f}"
    except ValueError:
        return str(value)


def parse_alias(raw: str) -> dict[str, tuple[str, str]]:
    aliases: dict[str, tuple[str, str]] = {}
    for spec in [item.strip() for item in raw.split(",") if item.strip()]:
        parts = [part.strip() for part in spec.split(":")]
        if len(parts) == 2:
            aliases[parts[0]] = (parts[1], parts[1])
        elif len(parts) == 3:
            aliases[parts[0]] = (parts[1], parts[2])
        else:
            raise ValueError(
                "--aliases entries must be label:exp_id or label:metrics_exp_id:profile_exp_id"
            )
    return aliases


def build_table(
    metrics_rows: list[dict[str, str]],
    profile_rows: list[dict[str, str]],
    exp_ids: list[str],
    aliases: dict[str, tuple[str, str]],
) -> str:
    metrics_by_exp_dataset: dict[tuple[str, str], dict[str, str]] = {}
    metrics_by_exp: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in metrics_rows:
        exp_id = row.get("exp_id", "")
        metrics_by_exp_dataset[(exp_id, row.get("dataset", ""))] = row
        if exp_id:
            metrics_by_exp[exp_id].append(row)

    profiles_by_exp = {row.get("exp_id", ""): row for row in profile_rows}

    lines = [
        "| Exp ID | Params(M) | GMACs | Speed Status | Metric Status | CAMO S/wF/MAE | COD10K S/wF/MAE | NC4K S/wF/MAE |",
        "| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |",
    ]
    for label in exp_ids:
        metrics_exp_id, profile_exp_id = aliases.get(label, (label, label))
        profile = profiles_by_exp.get(profile_exp_id, {})
        params_m = "TBD"
        if profile.get("params"):
            params_m = fmt_float(str(float(profile["params"]) / 1_000_000), 2)
        gmacs = fmt_float(profile.get("gmacs", ""), 2)
        if profile:
            latency = profile.get("latency_ms", "")
            fps = profile.get("fps", "")
            device = profile.get("device", "")
            warmup = profile.get("warmup", "")
            repeat = profile.get("repeat", "")
            if latency and fps:
                speed_status = (
                    f"{fmt_float(latency, 2)} ms / {fmt_float(fps, 2)} FPS "
                    f"({device}, warmup={warmup}, repeat={repeat})"
                )
            else:
                speed_status = "profile present; latency/FPS missing"
        else:
            speed_status = "TBD"
        status = evidence_status(metrics_by_exp.get(metrics_exp_id, []))
        camo = metric_triplet(metrics_by_exp_dataset.get((metrics_exp_id, "CAMO"), {}))
        cod10k = metric_triplet(metrics_by_exp_dataset.get((metrics_exp_id, "COD10K"), {}))
        nc4k = metric_triplet(metrics_by_exp_dataset.get((metrics_exp_id, "NC4K"), {}))
        lines.append(
            f"| {label} | {params_m} | {gmacs} | {speed_status} | {status} | {camo} | {cod10k} | {nc4k} |"
        )
    return "\n".join(lines) + "\n"


def table_notes(exp_ids: list[str], aliases: dict[str, tuple[str, str]]) -> str:
    notes: list[str] = []
    if "baseline_escnet_b5_clean_prob_e120" in exp_ids:
        notes.append(
            "- `baseline_escnet_b5_clean_prob_e120` is the accepted clean probability "
            "baseline row when CAMO/COD10K/NC4K all have "
            "`clean_prob_re_eval_complete`; its structural profile is shared with "
            "`baseline_escnet_b5_416_idle` for controlled speed."
        )
    if "baseline_escnet_b5_416_e120" in exp_ids:
        notes.append(
            "- `baseline_escnet_b5_416_e120` is a historical reference row archived in "
            "`02_experiments/tables/metrics_all.csv` and "
            "`02_experiments/metadata/baseline_escnet_b5_416_e120.json`; it is not yet "
            "the final clean snapshot probability-protocol baseline."
        )
    if "light_b2_c64_trained_416" in exp_ids:
        notes.append(
            "- `light_b2_c64_trained_416` uses the trained-checkpoint profile for "
            "params/GMACs/model size/peak memory and the idle same-command profile "
            "for latency/FPS."
        )
    if "kd_light_b2_c64_trained_416" in exp_ids:
        notes.append(
            "- `kd_light_b2_c64_trained_416` reports the final KD checkpoint only as "
            "measured evidence; precision claims must follow the observed deltas."
        )
    if not notes:
        return ""
    return "\n".join(notes) + "\n"


def coverage(metrics_rows: list[dict[str, str]]) -> str:
    grouped: dict[str, set[str]] = defaultdict(set)
    statuses: dict[str, set[str]] = defaultdict(set)
    for row in metrics_rows:
        exp_id = row.get("exp_id", "")
        grouped[exp_id].add(row.get("dataset", ""))
        if row.get("status", ""):
            statuses[exp_id].add(row.get("status", ""))

    lines = [
        "| Exp ID | Datasets | Three Datasets Present | Evidence Status |",
        "| --- | --- | --- | --- |",
    ]
    for exp_id in sorted(grouped):
        datasets = sorted(item for item in grouped[exp_id] if item)
        complete = all(dataset in grouped[exp_id] for dataset in ["CAMO", "COD10K", "NC4K"])
        status = ", ".join(sorted(statuses.get(exp_id, set()))) or "pending"
        lines.append(
            f"| {exp_id} | {', '.join(datasets)} | {'yes' if complete else 'no'} | {status} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate COD metrics/profile tables.")
    parser.add_argument(
        "--metrics_csv",
        default="/root/data-tmp/workspace/02_experiments/tables/metrics_all.csv",
    )
    parser.add_argument(
        "--profiles_csv",
        default="/root/data-tmp/workspace/02_experiments/tables/profiles.csv",
    )
    parser.add_argument("--out_md", required=True)
    parser.add_argument(
        "--exp_ids",
        default="baseline_escnet_b5_clean_prob_e120,light_b2_c64_trained_416,kd_light_b2_c64_trained_416",
        help="Comma/space separated row labels to include in the compact table.",
    )
    parser.add_argument(
        "--aliases",
        default=(
            "baseline_escnet_b5_clean_prob_e120:"
            "baseline_escnet_b5_clean_prob_e120:"
            "baseline_escnet_b5_416_idle,"
            "light_b2_c64_trained_416:light_b2_c64_e120_s42_prob_eval_v2:light_b2_c64_trained_416_idle,"
            "kd_light_b2_c64_trained_416:"
            "kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval:"
            "kd_light_b2_c64_trained_416_idle"
        ),
        help="Comma separated aliases as label:metrics_exp_id:profile_exp_id.",
    )
    args = parser.parse_args()

    metrics_rows = read_csv(Path(args.metrics_csv).expanduser())
    profile_rows = read_csv(Path(args.profiles_csv).expanduser())
    exp_ids = [
        item.strip()
        for item in args.exp_ids.replace(",", " ").split()
        if item.strip()
    ]
    aliases = parse_alias(args.aliases)

    out = Path(args.out_md).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    text = (
        "# Aggregated Results\n\n"
        "## Main Compact Table\n\n"
        + build_table(metrics_rows, profile_rows, exp_ids, aliases)
        + "\n"
        + table_notes(exp_ids, aliases)
        + "\n## Metric Coverage\n\n"
        + coverage(metrics_rows)
    )
    out.write_text(text, encoding="utf-8")
    print({"out": str(out), "exp_ids": exp_ids})


if __name__ == "__main__":
    main()
