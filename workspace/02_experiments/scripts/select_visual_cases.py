#!/usr/bin/env python3
"""Select evidence-backed visual cases from COD predictions."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
from PIL import Image


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}


def parse_pred(raw: str) -> tuple[str, Path]:
    if "=" not in raw:
        raise argparse.ArgumentTypeError("--pred must be NAME=DIR")
    name, path = raw.split("=", 1)
    name = name.strip()
    if not name:
        raise argparse.ArgumentTypeError("Prediction column name cannot be empty")
    return name, Path(path).expanduser()


def list_by_stem(root: Path) -> dict[str, Path]:
    return {
        path.stem: path
        for path in sorted(root.iterdir())
        if path.is_file() and path.suffix.lower() in IMAGE_EXTS
    }


def load_gray(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("L"), dtype=np.float32) / 255.0


def mae(pred: Path, gt: Path) -> float:
    pred_arr = load_gray(pred)
    gt_arr = load_gray(gt)
    if pred_arr.shape != gt_arr.shape:
        pred_img = Image.open(pred).convert("L").resize(
            (gt_arr.shape[1], gt_arr.shape[0]), Image.Resampling.BILINEAR
        )
        pred_arr = np.asarray(pred_img, dtype=np.float32) / 255.0
    return float(np.mean(np.abs(pred_arr - gt_arr)))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_md(
    path: Path,
    rows: list[dict[str, str]],
    baseline: str,
    target: str,
    top_k: int,
) -> None:
    def names(items: list[dict[str, str]]) -> str:
        return ", ".join(row["stem"] for row in items)

    worse = sorted(rows, key=lambda row: float(row[f"{target}_minus_{baseline}_mae"]), reverse=True)[:top_k]
    better = sorted(rows, key=lambda row: float(row[f"{target}_minus_{baseline}_mae"]))[:top_k]
    hard = sorted(rows, key=lambda row: float(row[f"{target}_mae"]), reverse=True)[:top_k]
    close = sorted(
        rows,
        key=lambda row: (
            abs(float(row[f"{target}_minus_{baseline}_mae"])),
            float(row[f"{target}_mae"]),
        ),
    )[:top_k]

    lines = [
        "# Visual Case Selection",
        "",
        f"Baseline: `{baseline}`",
        f"Target: `{target}`",
        "",
        "MAE is computed per image after resizing predictions to GT size if needed.",
        "",
        "## Recommended Groups",
        "",
        f"- Light worse than baseline: {names(worse)}",
        f"- Light close to baseline: {names(close)}",
        f"- Light better than baseline: {names(better)}",
        f"- Hard cases for Light: {names(hard)}",
        "",
        "## Top Light-Worse Cases",
        "",
        f"| stem | {baseline} MAE | {target} MAE | delta |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in worse:
        lines.append(
            f"| {row['stem']} | {row[f'{baseline}_mae']} | "
            f"{row[f'{target}_mae']} | {row[f'{target}_minus_{baseline}_mae']} |"
        )
    lines.extend(["", "## Top Light-Better Cases", "", f"| stem | {baseline} MAE | {target} MAE | delta |", "| --- | ---: | ---: | ---: |"])
    for row in better:
        lines.append(
            f"| {row['stem']} | {row[f'{baseline}_mae']} | "
            f"{row[f'{target}_mae']} | {row[f'{target}_minus_{baseline}_mae']} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank visual cases by per-image MAE.")
    parser.add_argument("--gt_dir", required=True)
    parser.add_argument("--pred", action="append", type=parse_pred, default=[], required=True)
    parser.add_argument("--baseline", required=True, help="Prediction name used as teacher/baseline.")
    parser.add_argument("--target", required=True, help="Prediction name used as student/target.")
    parser.add_argument("--out_csv", required=True)
    parser.add_argument("--out_md", required=True)
    parser.add_argument("--top_k", type=int, default=8)
    args = parser.parse_args()

    gt_dir = Path(args.gt_dir).expanduser()
    gts = list_by_stem(gt_dir)
    pred_maps = {name: list_by_stem(path) for name, path in args.pred}
    if args.baseline not in pred_maps:
        raise ValueError(f"Missing baseline prediction: {args.baseline}")
    if args.target not in pred_maps:
        raise ValueError(f"Missing target prediction: {args.target}")

    common = set(gts)
    for pred_files in pred_maps.values():
        common &= set(pred_files)
    if not common:
        raise ValueError("No common prediction/GT stems found")

    names = sorted(common)
    fieldnames = ["stem"] + [f"{name}_mae" for name in pred_maps]
    delta_name = f"{args.target}_minus_{args.baseline}_mae"
    fieldnames.append(delta_name)

    rows: list[dict[str, str]] = []
    for stem in names:
        row: dict[str, str] = {"stem": stem}
        scores = {}
        for pred_name, pred_files in pred_maps.items():
            score = mae(pred_files[stem], gts[stem])
            scores[pred_name] = score
            row[f"{pred_name}_mae"] = f"{score:.6f}"
        row[delta_name] = f"{scores[args.target] - scores[args.baseline]:.6f}"
        rows.append(row)

    write_csv(Path(args.out_csv).expanduser(), rows, fieldnames)
    write_md(Path(args.out_md).expanduser(), rows, args.baseline, args.target, args.top_k)
    print(
        {
            "samples": len(rows),
            "out_csv": args.out_csv,
            "out_md": args.out_md,
            "baseline": args.baseline,
            "target": args.target,
        }
    )


if __name__ == "__main__":
    main()
