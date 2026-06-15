#!/usr/bin/env python3
"""Summarize the current KD B2-C64 recovery run.

This is a read-only helper for the main Gate 2 route. It never starts,
stops, or signals training; it only parses the active log/checkpoint/process
state and writes a compact status report under the workspace.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml


WORKSPACE = Path("/root/data-tmp/workspace")
KD_RUN_ROOT = WORKSPACE / "02_experiments" / "runs" / "kd_light_b2_c64_e120_s42"
FAST_LOCAL_LOG_DIR = Path("/dev/shm/escnet_fast_kd/logs")
LEGACY_CONFIG = KD_RUN_ROOT / "config_resume_epoch5_b2_workers0_4gpu.yaml"
LEGACY_LOG = KD_RUN_ROOT / "logs" / "train_resume_epoch5_b2_workers0_4gpu_20260614T073026Z.log"
LEGACY_RUN_DIR = (
    WORKSPACE / "02_experiments" / "runs" / "kd_light_b2_c64_e120_s42_recover_b2w0_4gpu"
)
KD_CANDIDATES = (
    (
        KD_RUN_ROOT / "config_continue_epoch20_b6_w8_4gpu.yaml",
        Path("/dev/shm/escnet_fast_kd/logs"),
        Path("/dev/shm/escnet_fast_kd/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu"),
    ),
    (
        KD_RUN_ROOT / "config_resume_epoch10_fast_shm_4gpu.yaml",
        Path("/dev/shm/escnet_fast_kd/logs"),
        Path("/dev/shm/escnet_fast_kd/runs/kd_light_b2_c64_e120_s42_recover_epoch10_fast_shm_4gpu"),
    ),
    (
        KD_RUN_ROOT / "config_resume_epoch5_b2_workers0_4gpu.yaml",
        KD_RUN_ROOT / "logs",
        WORKSPACE / "02_experiments" / "runs" / "kd_light_b2_c64_e120_s42_recover_b2w0_4gpu",
    ),
)

ITER_PATTERN = re.compile(
    r"(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+).*?"
    r"Epoch\[(?P<epoch>\d+)/(?P<total>\d+)\] Iter\[(?P<iter>\d+)/(?P<iters>\d+)\].*?"
    r"Total Loss: (?P<total_loss>[0-9.]+).*?"
    r"Structure Loss: (?P<structure_loss>[0-9.]+).*?"
    r"Edge Loss: (?P<edge_loss>[0-9.]+).*?"
    r"KD Loss: (?P<kd_loss>[0-9.]+).*?"
    r"KD Weight: (?P<kd_weight>[0-9.]+)"
)
FINAL_PATTERN = re.compile(
    r"(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+).*?"
    r"@==Final== Epoch\[(?P<epoch>\d+)/(?P<total>\d+)\] Avg Training Loss: (?P<loss>[0-9.]+)"
)
CKPT_SAVE_PATTERN = re.compile(
    r"(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+).*?"
    r"Checkpoint saved to (?P<path>\S+)"
)


def read_log(log_path: Path) -> tuple[dict[str, str] | None, list[dict[str, str]], list[dict[str, str]]]:
    latest_iter: dict[str, str] | None = None
    finals: list[dict[str, str]] = []
    saved_ckpts: list[dict[str, str]] = []
    if not log_path.is_file():
        return latest_iter, finals, saved_ckpts
    for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
        iter_match = ITER_PATTERN.search(line)
        if iter_match:
            latest_iter = iter_match.groupdict()
        final_match = FINAL_PATTERN.search(line)
        if final_match:
            finals.append(final_match.groupdict())
        ckpt_match = CKPT_SAVE_PATTERN.search(line)
        if ckpt_match:
            saved_ckpts.append(ckpt_match.groupdict())
    return latest_iter, finals, saved_ckpts


def list_checkpoints(run_dir: Path) -> list[Path]:
    if not run_dir.is_dir():
        return []

    def epoch_key(path: Path) -> tuple[int, str]:
        match = re.search(r"epoch_(\d+)\.pth$", path.name)
        return (int(match.group(1)) if match else -1, path.name)

    return sorted(run_dir.glob("epoch_*.pth"), key=epoch_key)


def process_lines(markers: list[str]) -> list[str]:
    try:
        output = subprocess.check_output(
            ["ps", "-eo", "pid,ppid,stat,etime,cmd"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return []
    rows = []
    for line in output.splitlines():
        if (
            is_training_process_line(line)
            and any(marker in line for marker in markers)
            and "summarize_kd_recovery.py" not in line
        ):
            rows.append(line)
    return rows


def is_training_process_line(line: str) -> bool:
    return (
        " train.py --config " in line
        or " -u train.py --config " in line
        or "/torchrun " in line
        or " torchrun " in line
    )


def all_process_lines() -> list[str]:
    try:
        output = subprocess.check_output(
            ["ps", "-eo", "pid,ppid,stat,etime,cmd"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return []
    return output.splitlines()


def active_kd_config() -> Path | None:
    candidates: list[str] = []
    for line in all_process_lines():
        if "summarize_kd_recovery.py" in line:
            continue
        if not is_training_process_line(line):
            continue
        match = re.search(r"--config\s+(\S+)", line)
        if not match:
            continue
        config = match.group(1)
        if "kd_light_b2_c64_e120_s42" in config or "config_resume_epoch" in Path(config).name:
            candidates.append(config)
    if not candidates:
        return None
    candidates.sort(key=lambda item: ("fast_shm" not in item, item))
    return Path(candidates[0]).expanduser().resolve()


def config_stem(config: Path) -> str:
    stem = config.stem
    return stem.removeprefix("config_") if stem.startswith("config_") else stem


def read_config(config: Path) -> dict:
    if not config.is_file():
        return {}
    with config.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def infer_run_dir(config: Path, explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    for candidate_config, _log_dir, candidate_run_dir in KD_CANDIDATES:
        if config.resolve() == candidate_config.resolve():
            return candidate_run_dir.resolve()
    cfg = read_config(config)
    save_model_dir = cfg.get("save_model_dir")
    name = cfg.get("name")
    if save_model_dir and name:
        return (Path(save_model_dir).expanduser() / str(name)).resolve()
    return LEGACY_RUN_DIR.resolve()


def infer_log_path(config: Path, explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()

    stem = config_stem(config)
    pointer = KD_RUN_ROOT / f"latest_{stem}_local_log.txt"
    candidates: list[Path] = []
    if pointer.is_file():
        pointed = Path(pointer.read_text(encoding="utf-8", errors="replace").strip())
        if pointed.is_file():
            candidates.append(pointed)
    for log_dir in (FAST_LOCAL_LOG_DIR, KD_RUN_ROOT / "logs"):
        if log_dir.is_dir():
            candidates.extend(log_dir.glob(f"train_{stem}_*.log"))
    if candidates:
        candidates = [path.expanduser().resolve() for path in candidates if path.is_file()]
        if candidates:
            return max(candidates, key=lambda item: item.stat().st_mtime)
    return LEGACY_LOG.resolve()


def infer_config(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    active = active_kd_config()
    if active:
        return active
    final_candidates = [
        config
        for config, _log_dir, run_dir in KD_CANDIDATES
        if config.is_file() and (run_dir / "epoch_120.pth").is_file()
    ]
    if final_candidates:
        return final_candidates[0].resolve()
    checkpoint_candidates = [
        (max(list_checkpoints(run_dir), key=lambda path: path.stat().st_mtime), config)
        for config, _log_dir, run_dir in KD_CANDIDATES
        if config.is_file() and list_checkpoints(run_dir)
    ]
    if checkpoint_candidates:
        return max(checkpoint_candidates, key=lambda item: item[0].stat().st_mtime)[1].resolve()
    return LEGACY_CONFIG.resolve()


def gpu_lines() -> list[str]:
    try:
        output = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=index,name,memory.used,memory.total,utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def checkpoint_row(path: Path) -> str:
    stat = path.stat()
    mtime = datetime.fromtimestamp(stat.st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"| `{path.name}` | {stat.st_size} | `{mtime}` |"


def write_report(
    *,
    out_md: Path,
    config: Path,
    log_path: Path,
    run_dir: Path,
    latest_iter: dict[str, str] | None,
    finals: list[dict[str, str]],
    saved_ckpts: list[dict[str, str]],
    checkpoints: list[Path],
    processes: list[str],
    gpus: list[str],
    final_epoch: int,
) -> None:
    out_md.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    status = "running" if processes else "not_observed_running"
    final_ckpt = run_dir / f"epoch_{final_epoch}.pth"
    final_status = "present" if final_ckpt.is_file() else "absent"
    latest_ckpt = checkpoints[-1].name if checkpoints else "none"

    lines = [
        "# KD Recovery Status Latest",
        "",
        f"- Updated UTC: `{now}`",
        f"- Status: `{status}`",
        "- Gate: `Gate 2 KD`",
        "- Evidence boundary: `pending_gate_no_kd_claims`",
        f"- Config: `{config}`",
        f"- Log: `{log_path}`",
        f"- Run dir: `{run_dir}`",
        f"- Latest checkpoint: `{latest_ckpt}`",
        f"- Final checkpoint status: `{final_status}`",
        "",
        "## Latest Training",
        "",
    ]
    if latest_iter:
        lines.append(
            "- Latest iter: "
            f"epoch {latest_iter['epoch']}/{latest_iter['total']}, "
            f"iter {latest_iter['iter']}/{latest_iter['iters']}, "
            f"log time `{latest_iter['ts']}`, "
            f"total loss {latest_iter['total_loss']}, "
            f"KD loss {latest_iter['kd_loss']}"
        )
    else:
        lines.append("- Latest iter: unavailable")
    if finals:
        last_final = finals[-1]
        lines.append(
            "- Latest completed epoch: "
            f"{last_final['epoch']}/{last_final['total']} "
            f"with avg loss {last_final['loss']}, log time `{last_final['ts']}`"
        )
    else:
        lines.append("- Latest completed epoch: unavailable")
    if saved_ckpts:
        last_saved = saved_ckpts[-1]
        lines.append(
            f"- Latest checkpoint save log: `{Path(last_saved['path']).name}` at `{last_saved['ts']}`"
        )

    lines.extend(["", "## Checkpoints", ""])
    if checkpoints:
        lines.extend(["| checkpoint | bytes | mtime UTC |", "| --- | ---: | --- |"])
        lines.extend(checkpoint_row(path) for path in checkpoints)
    else:
        lines.append("- none")

    lines.extend(["", "## GPU Snapshot", ""])
    lines.extend([f"- `{line}`" for line in gpus] or ["- unavailable"])

    lines.extend(["", "## Process Snapshot", ""])
    lines.extend([f"- `{line.strip()}`" for line in processes] or ["- none"])

    lines.extend(["", "## Acceptance Boundary", ""])
    if final_status == "present":
        lines.append(
            "- Final checkpoint is present; do not claim KD improvement until CAMO/COD10K/NC4K probability eval, integrity checks, and release audits pass."
        )
    else:
        lines.append("- This report is recovery evidence only while the final checkpoint is absent.")
        lines.append(
            "- Do not claim KD improvement until a final checkpoint, CAMO/COD10K/NC4K probability eval, integrity checks, and release audits pass."
        )
    lines.append(
        "- Do not restart `watch_baseline_then_start_kd.sh` or duplicate `start_kd_full_train.sh` while this run is active."
    )
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize active KD recovery run.")
    parser.add_argument(
        "--config",
        default="",
    )
    parser.add_argument(
        "--log",
        default="",
    )
    parser.add_argument(
        "--run_dir",
        default="",
    )
    parser.add_argument(
        "--out_md",
        default="/root/data-tmp/workspace/02_experiments/runs/kd_recovery_status_latest.md",
    )
    parser.add_argument("--final_epoch", type=int, default=120)
    args = parser.parse_args()

    config = infer_config(args.config)
    log_path = infer_log_path(config, args.log)
    run_dir = infer_run_dir(config, args.run_dir)
    out_md = Path(args.out_md).expanduser().resolve()

    latest_iter, finals, saved_ckpts = read_log(log_path)
    checkpoints = list_checkpoints(run_dir)
    markers = [str(config), str(run_dir), log_path.name]
    processes = process_lines(markers)
    gpus = gpu_lines()

    write_report(
        out_md=out_md,
        config=config,
        log_path=log_path,
        run_dir=run_dir,
        latest_iter=latest_iter,
        finals=finals,
        saved_ckpts=saved_ckpts,
        checkpoints=checkpoints,
        processes=processes,
        gpus=gpus,
        final_epoch=args.final_epoch,
    )

    print(f"kd_recovery_status_report={out_md}")
    if latest_iter:
        print(
            "latest_iter="
            f"epoch_{latest_iter['epoch']}_iter_{latest_iter['iter']}_of_{latest_iter['iters']}"
        )
    if checkpoints:
        print(f"latest_checkpoint={checkpoints[-1].name}")
    print(f"checkpoint_count={len(checkpoints)}")
    print(f"final_checkpoint={'present' if (run_dir / f'epoch_{args.final_epoch}.pth').is_file() else 'absent'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
