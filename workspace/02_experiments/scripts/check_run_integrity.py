#!/usr/bin/env python3
"""Check whether an experiment run has the artifacts needed for paper tables."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


KNOWN_DATASETS = ["CAMO", "COD10K", "NC4K"]


def count_files(path: Path) -> int:
    if not path.is_dir():
        return -1
    return sum(1 for item in path.iterdir() if item.is_file())


def find_single_method(pred_dataset_dir: Path) -> tuple[str | None, Path | None]:
    if not pred_dataset_dir.is_dir():
        return None, None
    method_dirs = sorted(path for path in pred_dataset_dir.iterdir() if path.is_dir())
    if len(method_dirs) != 1:
        return None, None
    return method_dirs[0].name, method_dirs[0]


def load_metric_keys(metrics_csv: Path, exp_id: str) -> set[tuple[str, str]]:
    if not metrics_csv.is_file():
        return set()
    keys = set()
    with metrics_csv.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row.get("exp_id") == exp_id:
                keys.add((row.get("dataset", ""), row.get("method", "")))
    return keys


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate run artifacts.")
    parser.add_argument("--run_dir", required=True, help="Experiment run directory.")
    parser.add_argument("--exp_id", required=True, help="Experiment ID in metrics CSV.")
    parser.add_argument(
        "--dataset_root",
        default="/root/data-tmp/COD/Test",
        help="Test dataset root containing DATASET/GT_Object.",
    )
    parser.add_argument(
        "--datasets",
        default="CAMO,COD10K,NC4K",
        help="Comma/space separated datasets to check.",
    )
    parser.add_argument(
        "--metrics_csv",
        default="/root/data-tmp/workspace/02_experiments/tables/metrics_all.csv",
    )
    parser.add_argument("--require_checkpoint", action="store_true")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    dataset_root = Path(args.dataset_root).expanduser().resolve()
    metrics_csv = Path(args.metrics_csv).expanduser().resolve()
    datasets = [
        item.strip().upper()
        for item in args.datasets.replace(",", " ").split()
        if item.strip()
    ]

    errors: list[str] = []
    warnings: list[str] = []

    if not run_dir.is_dir():
        errors.append(f"Missing run_dir: {run_dir}")
    if not dataset_root.is_dir():
        errors.append(f"Missing dataset_root: {dataset_root}")

    checkpoints = sorted(run_dir.glob("epoch_*.pth")) if run_dir.is_dir() else []
    if args.require_checkpoint and not checkpoints:
        errors.append(f"No epoch_*.pth checkpoint found in {run_dir}")

    metric_keys = load_metric_keys(metrics_csv, args.exp_id)
    if not metric_keys:
        warnings.append(f"No metrics rows found for exp_id={args.exp_id}")

    for dataset in datasets:
        gt_dir = dataset_root / dataset / "GT_Object"
        gt_count = count_files(gt_dir)
        if gt_count < 0:
            errors.append(f"Missing GT dir for {dataset}: {gt_dir}")
            continue

        pred_dataset_dir = run_dir / "preds" / dataset
        method, method_dir = find_single_method(pred_dataset_dir)
        if method_dir is None:
            errors.append(
                f"Expected exactly one method dir under {pred_dataset_dir}"
            )
        else:
            pred_count = count_files(method_dir)
            if pred_count != gt_count:
                errors.append(
                    f"{dataset} pred/GT count mismatch: pred={pred_count}, gt={gt_count}"
                )
            if (dataset, method or "") not in metric_keys:
                warnings.append(
                    f"No metrics row for exp_id={args.exp_id}, dataset={dataset}, method={method}"
                )

        result_txt = run_dir / "results" / dataset / "result.txt"
        alt_result_txt = run_dir / "eval" / dataset / "result.txt"
        if not result_txt.is_file() and not alt_result_txt.is_file():
            errors.append(f"Missing result.txt for {dataset}")

    print(f"run_dir={run_dir}")
    print(f"checkpoints={len(checkpoints)}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if errors:
        return 1
    print("Integrity check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
