#!/usr/bin/env python3
"""Summarize the external dirty-tree PVTv2-B0 observation branch.

This is a read-only monitor for the high-risk run currently launched from
`/root/ESCNet`. It deliberately does not promote the branch to paper evidence.
"""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


LOG_PATTERN = re.compile(
    r"(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+).*?"
    r"Epoch\[(?P<epoch>\d+)/(?P<total>\d+)\] Iter\[(?P<iter>\d+)/(?P<iters>\d+)\]"
)
FINAL_PATTERN = re.compile(
    r"(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+).*?"
    r"@==Final== Epoch\[(?P<epoch>\d+)/(?P<total>\d+)\] Avg Training Loss: (?P<loss>[0-9.]+)"
)
EVAL_START_PATTERN = re.compile(
    r"(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+).*?"
    r"Running eval at epoch (?P<epoch>\d+)\. Predictions: (?P<predictions>\S+)"
)


def read_latest_log(
    log_path: Path,
) -> tuple[dict[str, str] | None, dict[str, str] | None, dict[str, str] | None]:
    latest_iter = None
    latest_final = None
    latest_eval_start = None
    if not log_path.is_file():
        return latest_iter, latest_final, latest_eval_start

    for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = LOG_PATTERN.search(line)
        if match:
            latest_iter = match.groupdict()
        final_match = FINAL_PATTERN.search(line)
        if final_match:
            latest_final = final_match.groupdict()
        eval_match = EVAL_START_PATTERN.search(line)
        if eval_match:
            latest_eval_start = eval_match.groupdict()
    return latest_iter, latest_final, latest_eval_start


def read_results(result_path: Path) -> list[dict[str, str]]:
    if not result_path.is_file():
        return []
    with result_path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def list_checkpoints(ckpt_dir: Path) -> list[Path]:
    if not ckpt_dir.is_dir():
        return []
    return sorted(ckpt_dir.glob("*.pth"))


def process_lines(pattern: str) -> list[str]:
    try:
        output = subprocess.check_output(
            ["ps", "-eo", "pid,ppid,stat,etime,cmd"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return []
    return [line for line in output.splitlines() if pattern in line and "grep" not in line]


def gpu_lines() -> list[str]:
    try:
        output = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=index,memory.used,memory.total,utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def write_report(
    out_md: Path,
    log_path: Path,
    result_path: Path,
    ckpt_dir: Path,
    latest_iter: dict[str, str] | None,
    latest_final: dict[str, str] | None,
    latest_eval_start: dict[str, str] | None,
    results: list[dict[str, str]],
    checkpoints: list[Path],
    processes: list[str],
    gpus: list[str],
) -> None:
    out_md.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    status = "running" if processes else "not_observed_running"
    checkpoint_status = "present" if checkpoints else "absent"

    lines = [
        "# External B0 Status Latest",
        "",
        f"- Updated UTC: `{now}`",
        f"- Status: `{status}`",
        f"- Evidence boundary: `external_dirty_tree_observation_only`",
        f"- Log: `{log_path}`",
        f"- Result CSV: `{result_path}`",
        f"- Checkpoint dir: `{ckpt_dir}`",
        f"- Checkpoint status: `{checkpoint_status}`",
        "",
        "## Latest Training",
        "",
    ]
    if latest_iter:
        lines.append(
            "- Latest iter: "
            f"epoch {latest_iter['epoch']}/{latest_iter['total']}, "
            f"iter {latest_iter['iter']}/{latest_iter['iters']}, "
            f"log time `{latest_iter['ts']}`"
        )
    else:
        lines.append("- Latest iter: unavailable")
    if latest_final:
        lines.append(
            "- Latest completed epoch: "
            f"{latest_final['epoch']}/{latest_final['total']} "
            f"with avg loss {latest_final['loss']}"
        )
    else:
        lines.append("- Latest completed epoch: unavailable")
    if latest_eval_start:
        result_epochs = {row.get("epoch") for row in results}
        eval_status = (
            "metrics_appended"
            if latest_eval_start["epoch"] in result_epochs
            else "in_progress_or_pending_metrics"
        )
        lines.append(
            "- Latest eval start: "
            f"epoch {latest_eval_start['epoch']}, "
            f"log time `{latest_eval_start['ts']}`, "
            f"predictions `{latest_eval_start['predictions']}`, "
            f"status `{eval_status}`"
        )
    else:
        lines.append("- Latest eval start: unavailable")

    lines.extend(["", "## Intermediate COD10K Results", ""])
    if results:
        lines.extend(
            [
                "| epoch | Smeasure | wFmeasure | meanFm | meanEm | MAE |",
                "| ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in results:
            lines.append(
                "| {epoch} | {Smeasure} | {wFmeasure} | {meanFm} | {meanEm} | {MAE} |".format(
                    **row
                )
            )
    else:
        lines.append("- No result rows found.")

    lines.extend(["", "## Checkpoints", ""])
    if checkpoints:
        lines.extend([f"- `{path}`" for path in checkpoints])
    else:
        lines.append("- none")

    lines.extend(["", "## GPU Snapshot", ""])
    lines.extend([f"- `{line}`" for line in gpus] or ["- unavailable"])

    lines.extend(["", "## Process Snapshot", ""])
    lines.extend([f"- `{line.strip()}`" for line in processes] or ["- none"])

    lines.extend(
        [
            "",
            "## Acceptance Boundary",
            "",
            "- Do not use this branch as a final main-table result while it is launched from dirty `/root/ESCNet`.",
            "- Require a checkpoint, code/config snapshot under `/root/data-tmp/workspace`, and CAMO/COD10K/NC4K probability evaluation before any paper-facing result use.",
            "- Current COD10K-only intermediate rows are observation evidence only.",
        ]
    )

    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize external PVTv2-B0 run.")
    parser.add_argument(
        "--log",
        default="/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/log.txt",
    )
    parser.add_argument(
        "--result",
        default="/root/data-tmp/results_train/pvt_v2_b0/result.txt",
    )
    parser.add_argument(
        "--ckpt_dir",
        default="/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0",
    )
    parser.add_argument(
        "--out_md",
        default="/root/data-tmp/workspace/02_experiments/runs/b0_external_status_latest.md",
    )
    args = parser.parse_args()

    log_path = Path(args.log).expanduser().resolve()
    result_path = Path(args.result).expanduser().resolve()
    ckpt_dir = Path(args.ckpt_dir).expanduser().resolve()
    out_md = Path(args.out_md).expanduser().resolve()

    latest_iter, latest_final, latest_eval_start = read_latest_log(log_path)
    results = read_results(result_path)
    checkpoints = list_checkpoints(ckpt_dir)
    processes = process_lines("pvt_v2_b0")
    gpus = gpu_lines()

    write_report(
        out_md,
        log_path,
        result_path,
        ckpt_dir,
        latest_iter,
        latest_final,
        latest_eval_start,
        results,
        checkpoints,
        processes,
        gpus,
    )
    print(f"external_b0_status_report={out_md}")
    if latest_iter:
        print(
            "latest_iter="
            f"epoch_{latest_iter['epoch']}_iter_{latest_iter['iter']}_of_{latest_iter['iters']}"
        )
    if latest_eval_start:
        print(f"latest_eval_start=epoch_{latest_eval_start['epoch']}")
    print(f"checkpoint_count={len(checkpoints)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
