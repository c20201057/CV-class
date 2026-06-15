#!/usr/bin/env python3
"""Collect ESCNet prettytable result.txt files into a metrics CSV."""

from __future__ import annotations

import argparse
import csv
import os
import re
from pathlib import Path
from typing import Iterable


FIELDS = [
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

METRIC_FIELDS = FIELDS[3:8]
KNOWN_DATASETS = {"CAMO", "COD10K", "NC4K"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Parse ESCNet eval.py result.txt files and update metrics_all.csv."
    )
    parser.add_argument("--exp_id", "--exp-id", required=True, help="Experiment ID.")
    parser.add_argument(
        "--out_csv",
        "--out-csv",
        default="metrics_all.csv",
        help="CSV to create or update. Existing rows are preserved unless they share "
        "the same exp_id,dataset,method key.",
    )
    parser.add_argument(
        "--result",
        action="append",
        default=[],
        metavar="[DATASET=]RESULT_TXT",
        help="Result file to parse. DATASET= is optional when --datasets is supplied "
        "or the dataset can be inferred from the parent directory.",
    )
    parser.add_argument(
        "--result_root",
        "--result-root",
        default=None,
        help="Directory containing DATASET/result.txt children.",
    )
    parser.add_argument(
        "--datasets",
        default="",
        help="Comma/space separated dataset names. For one unlabeled result.txt with "
        "multiple appended tables, names are assigned in this order.",
    )
    parser.add_argument(
        "--out_md",
        "--out-md",
        default=None,
        help="Optional Markdown table output for the newly parsed rows.",
    )
    parser.add_argument(
        "--protocol",
        default="",
        help="Evaluation protocol label, e.g. prob_map or historical_legacy.",
    )
    parser.add_argument(
        "--repo_boundary",
        "--repo-boundary",
        default="",
        help="Code boundary label, e.g. clean_snapshot or dirty_history_result.",
    )
    parser.add_argument(
        "--checkpoint",
        default="",
        help="Checkpoint path or identifier used to produce the metrics.",
    )
    parser.add_argument(
        "--status",
        default="",
        help="Evidence status label, e.g. final_main_light or verification_only_camo.",
    )
    args = parser.parse_args()

    if not args.result and not args.result_root:
        parser.error("Provide at least one --result or --result_root.")
    return args


def split_names(raw: str) -> list[str]:
    return [item.strip().upper() for item in re.split(r"[\s,]+", raw or "") if item.strip()]


def normalize_metric(value: str) -> str:
    text = value.strip()
    if not text:
        raise ValueError("empty metric value")
    if text.startswith("."):
        number = float(f"0{text}")
    elif re.fullmatch(r"\d{1,3}", text):
        number = int(text) / 1000.0
    else:
        number = float(text)
    return f"{number:.3f}"


def split_pretty_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("&").split("&")]


def parse_result_tables(result_path: Path) -> list[list[dict[str, str]]]:
    """Return a list of tables; each table is a list of metric rows."""
    tables: list[list[dict[str, str]]] = []
    current: list[dict[str, str]] = []

    for raw_line in result_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line.startswith("&"):
            continue

        cells = split_pretty_row(line)
        if not cells:
            continue
        if cells[0] == "Method":
            if current:
                tables.append(current)
                current = []
            continue
        if len(cells) < 6:
            continue

        row = {"method": cells[0]}
        for field, value in zip(METRIC_FIELDS, cells[1:6]):
            row[field] = normalize_metric(value)
        current.append(row)

    if current:
        tables.append(current)
    if not tables:
        raise ValueError(f"No metric rows found in {result_path}")
    return tables


def infer_dataset_from_path(path: Path) -> str | None:
    for part in reversed(path.parts):
        upper = part.upper()
        if upper in KNOWN_DATASETS:
            return upper
    return None


def parse_result_specs(args: argparse.Namespace) -> list[tuple[str | None, Path]]:
    specs: list[tuple[str | None, Path]] = []

    for raw in args.result:
        if "=" in raw:
            dataset, file_path = raw.split("=", 1)
            specs.append((dataset.strip().upper(), Path(file_path).expanduser()))
        else:
            specs.append((None, Path(raw).expanduser()))

    if args.result_root:
        root = Path(args.result_root).expanduser()
        datasets = split_names(args.datasets) or sorted(KNOWN_DATASETS)
        for dataset in datasets:
            candidate = root / dataset / "result.txt"
            if candidate.exists():
                specs.append((dataset, candidate))

    return specs


def build_rows(args: argparse.Namespace) -> list[dict[str, str]]:
    dataset_order = split_names(args.datasets)
    rows: list[dict[str, str]] = []

    for dataset_hint, result_path in parse_result_specs(args):
        result_path = result_path.resolve()
        if not result_path.is_file():
            raise FileNotFoundError(result_path)

        tables = parse_result_tables(result_path)
        if dataset_hint:
            table_datasets = [dataset_hint] * len(tables)
        elif dataset_order and len(dataset_order) == len(tables):
            table_datasets = dataset_order
        elif len(tables) == 1:
            inferred = infer_dataset_from_path(result_path)
            if not inferred:
                if len(dataset_order) == 1:
                    inferred = dataset_order[0]
                else:
                    raise ValueError(
                        f"Cannot infer dataset for {result_path}; pass DATASET=path "
                        "or --datasets."
                    )
            table_datasets = [inferred]
        else:
            raise ValueError(
                f"{result_path} contains {len(tables)} tables but no dataset mapping. "
                "Pass --datasets with the same number of names."
            )

        for dataset, table in zip(table_datasets, tables):
            for parsed in table:
                row = {
                    "exp_id": args.exp_id,
                    "dataset": dataset,
                    "method": parsed["method"],
                    "source": str(result_path),
                    "protocol": args.protocol,
                    "repo_boundary": args.repo_boundary,
                    "checkpoint": args.checkpoint,
                    "status": args.status,
                }
                for field in METRIC_FIELDS:
                    row[field] = parsed[field]
                rows.append(row)

    if not rows:
        raise ValueError("No rows parsed.")
    return rows


def read_existing(csv_path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not csv_path.exists():
        return [], FIELDS.copy()
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or FIELDS)
        rows = [dict(row) for row in reader]

    for field in FIELDS:
        if field not in fieldnames:
            fieldnames.append(field)
    return rows, fieldnames


def update_csv(csv_path: Path, new_rows: Iterable[dict[str, str]]) -> tuple[int, int]:
    new_rows = list(new_rows)
    existing_rows, fieldnames = read_existing(csv_path)
    new_by_key = {
        (row["exp_id"], row["dataset"], row["method"]): row for row in new_rows
    }

    updated_rows: list[dict[str, str]] = []
    replaced = 0
    for row in existing_rows:
        key = (row.get("exp_id", ""), row.get("dataset", ""), row.get("method", ""))
        if key in new_by_key:
            merged = {field: "" for field in fieldnames}
            merged.update(row)
            merged.update(new_by_key.pop(key))
            updated_rows.append(merged)
            replaced += 1
        else:
            updated_rows.append(row)

    for row in new_by_key.values():
        merged = {field: "" for field in fieldnames}
        merged.update(row)
        updated_rows.append(merged)

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = csv_path.with_suffix(csv_path.suffix + ".tmp")
    with tmp_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)
    os.replace(tmp_path, csv_path)
    return replaced, len(new_rows) - replaced


def write_markdown(md_path: Path, rows: list[dict[str, str]]) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "| " + " | ".join(FIELDS) + " |",
        "| " + " | ".join(["---"] * len(FIELDS)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row.get(field, "") for field in FIELDS) + " |")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    rows = build_rows(args)
    out_csv = Path(args.out_csv).expanduser().resolve()
    replaced, inserted = update_csv(out_csv, rows)

    if args.out_md:
        write_markdown(Path(args.out_md).expanduser().resolve(), rows)

    print(
        f"parsed={len(rows)} inserted={inserted} replaced={replaced} "
        f"out_csv={out_csv}"
    )
    for row in rows:
        print(
            "{exp_id},{dataset},{method},{Smeasure},{wFmeasure},{meanFm},"
            "{meanEm},{MAE},{source},{protocol},{repo_boundary},{checkpoint},"
            "{status}".format(**row)
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
