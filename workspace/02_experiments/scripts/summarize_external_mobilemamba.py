#!/usr/bin/env python3
"""Summarize the external dirty-tree MobileMamba-T2 observation branch.

The run is launched by `/root/ESCNet/all.sh` and is not part of the clean
baseline/KD main queue. This script is read-only and only writes a status
report under the workspace.
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


def read_log(log_path: Path) -> tuple[dict[str, str] | None, dict[str, str] | None, dict[str, str] | None]:
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
    return [
        line
        for line in output.splitlines()
        if pattern in line
        and "grep" not in line
        and "summarize_external_mobilemamba.py" not in line
    ]


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


def best_result(results: list[dict[str, str]]) -> dict[str, str] | None:
    if not results:
        return None
    return max(results, key=lambda row: float(row.get("Smeasure") or 0.0))


def write_report(
    *,
    out_md: Path,
    branch_name: str,
    process_pattern: str,
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
    best = best_result(results)

    lines = [
        f"# External {branch_name} Status Latest",
        "",
        f"- Updated UTC: `{now}`",
        f"- Status: `{status}`",
        "- Evidence boundary: `external_dirty_tree_observation_only`",
        f"- Process pattern: `{process_pattern}`",
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
        if best:
            lines.extend(
                [
                    "",
                    "Best observed row by S-measure:",
                    f"`epoch {best.get('epoch')}: S={best.get('Smeasure')}, "
                    f"wF={best.get('wFmeasure')}, meanF={best.get('meanFm')}, "
                    f"meanE={best.get('meanEm')}, MAE={best.get('MAE')}`",
                ]
            )
    else:
        lines.append("- No result rows found yet.")

    lines.extend(["", "## Checkpoints", ""])
    lines.extend([f"- `{path}`" for path in checkpoints] or ["- none"])

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
            "- Require an isolated workspace snapshot, checkpoint load/profile, CAMO/COD10K/NC4K probability eval, and run integrity before paper-facing use.",
            "- Until then, treat it only as route-search evidence for whether a state-space/mobile backbone is promising.",
        ]
    )

    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize external MobileMamba-T2 run.")
    parser.add_argument("--branch_name", default="MobileMamba-T2")
    parser.add_argument("--process_pattern", default="mobilemamba_t2")
    parser.add_argument("--log", default="/root/data-tmp/ESCNet/checkpoints/mobilemamba_t2/log.txt")
    parser.add_argument("--result", default="/root/data-tmp/results_train/mobilemamba_t2/result.txt")
    parser.add_argument("--ckpt_dir", default="/root/data-tmp/ESCNet/checkpoints/mobilemamba_t2")
    parser.add_argument(
        "--out_md",
        default="/root/data-tmp/workspace/02_experiments/runs/mobilemamba_t2_external_status_latest.md",
    )
    args = parser.parse_args()

    log_path = Path(args.log).expanduser().resolve()
    result_path = Path(args.result).expanduser().resolve()
    ckpt_dir = Path(args.ckpt_dir).expanduser().resolve()
    out_md = Path(args.out_md).expanduser().resolve()

    latest_iter, latest_final, latest_eval_start = read_log(log_path)
    results = read_results(result_path)
    checkpoints = list_checkpoints(ckpt_dir)
    processes = process_lines(args.process_pattern)
    gpus = gpu_lines()

    write_report(
        out_md=out_md,
        branch_name=args.branch_name,
        process_pattern=args.process_pattern,
        log_path=log_path,
        result_path=result_path,
        ckpt_dir=ckpt_dir,
        latest_iter=latest_iter,
        latest_final=latest_final,
        latest_eval_start=latest_eval_start,
        results=results,
        checkpoints=checkpoints,
        processes=processes,
        gpus=gpus,
    )
    print(f"external_mobilemamba_status_report={out_md}")
    if latest_iter:
        print(
            "latest_iter="
            f"epoch_{latest_iter['epoch']}_iter_{latest_iter['iter']}_of_{latest_iter['iters']}"
        )
    print(f"checkpoint_count={len(checkpoints)}")
    print(f"result_rows={len(results)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
