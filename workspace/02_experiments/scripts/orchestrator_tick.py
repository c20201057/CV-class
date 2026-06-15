#!/usr/bin/env python3
"""Write a one-page orchestration status tick for the COD lightweight project.

The script is intentionally read-only with respect to training jobs: it may
refresh B0's status markdown by calling the existing read-only summarizer, but
it never starts, stops or signals any train/eval process.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


WORKSPACE = Path("/root/data-tmp/workspace")
DEFAULT_METRICS = WORKSPACE / "02_experiments" / "tables" / "metrics_all.csv"
DEFAULT_PROFILE = WORKSPACE / "02_experiments" / "tables" / "profiles.csv"
DEFAULT_B0_STATUS = WORKSPACE / "02_experiments" / "runs" / "b0_external_status_latest.md"
DEFAULT_MOBILEMAMBA_STATUS = (
    WORKSPACE / "02_experiments" / "runs" / "mobilemamba_t2_external_status_latest.md"
)
DEFAULT_KD_STATUS = WORKSPACE / "02_experiments" / "runs" / "kd_recovery_status_latest.md"
DEFAULT_BASELINE_RUN = WORKSPACE / "02_experiments" / "runs" / "baseline_escnet_b5_clean_prob_e120"
DEFAULT_RELEASE = WORKSPACE / "04_paper" / "drafts" / "release_audit_latest.md"
DEFAULT_DELTA = WORKSPACE / "04_paper" / "drafts" / "current_delta_summary.md"
DEFAULT_OUT_MD = WORKSPACE / "00_project" / "orchestrator_tick_latest.md"
DEFAULT_OUT_JSON = WORKSPACE / "00_project" / "orchestrator_tick_latest.json"
DEFAULT_B0_SUMMARIZER = WORKSPACE / "02_experiments" / "scripts" / "summarize_external_b0.py"
DEFAULT_MOBILEMAMBA_SUMMARIZER = (
    WORKSPACE / "02_experiments" / "scripts" / "summarize_external_mobilemamba.py"
)
DEFAULT_KD_SUMMARIZER = WORKSPACE / "02_experiments" / "scripts" / "summarize_kd_recovery.py"
DEFAULT_DATASET_ROOT = Path("/root/data-tmp/COD/Test")
BASELINE_EXP_ID = "baseline_escnet_b5_clean_prob_e120"
REQUIRED_DATASETS = ("CAMO", "COD10K", "NC4K")
KD_RUN_DIR = WORKSPACE / "02_experiments" / "runs" / "kd_light_b2_c64_e120_s42"
KD_CONFIG_MARKERS = (
    "config_resume_epoch5_b2_workers0_4gpu.yaml",
    "config_resume_epoch5_b2_workers0_2gpu.yaml",
    "config_resume_epoch5_b2_workers0_1gpu.yaml",
    "config_resume_epoch10_fast_shm_4gpu.yaml",
    "config_continue_epoch20_b6_w8_4gpu.yaml",
)
KD_RECOVERY_RUN_MARKERS = (
    "kd_light_b2_c64_e120_s42_recover_b2w0_4gpu",
    "kd_light_b2_c64_e120_s42_recover_b2w0_2gpu",
    "kd_light_b2_c64_e120_s42_recover_b2w0_1gpu",
    "kd_light_b2_c64_e120_s42_recover_epoch10_fast_shm_4gpu",
    "kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu",
)

WATCHERS = {
    "Gate 1 baseline watcher": "watch_gpu_then_start_baseline_clean.sh",
    "Gate 1 resume watcher": "resume_stopped_prob_eval_when_gpu_idle.sh",
    "Gate 2 KD watcher": "watch_baseline_then_start_kd.sh",
    "B0 read-only watcher": "watch_external_b0_progress.sh",
    "MobileMamba read-only watcher": "watch_external_mobilemamba_progress.sh",
}


@dataclass(frozen=True)
class GateState:
    status: str
    action: str


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def run_text(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return ""


def refresh_b0_status(summarizer: Path) -> None:
    if summarizer.is_file():
        subprocess.run(["python", str(summarizer)], check=False)


def refresh_mobilemamba_status(summarizer: Path) -> None:
    if summarizer.is_file():
        subprocess.run(["python", str(summarizer)], check=False)


def refresh_kd_status(summarizer: Path) -> None:
    if summarizer.is_file():
        subprocess.run(["python", str(summarizer)], check=False)


def parse_metrics(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def parse_profiles(path: Path) -> dict[str, dict[str, str]]:
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        return {row.get("exp_id", ""): dict(row) for row in csv.DictReader(handle)}


def datasets_for_status(rows: list[dict[str, str]], *, exp_id: str, status: str) -> set[str]:
    return {
        row.get("dataset", "")
        for row in rows
        if row.get("exp_id") == exp_id and row.get("status") == status
    }


def has_three_dataset_status(rows: list[dict[str, str]], *, exp_id: str, status: str) -> bool:
    return {"CAMO", "COD10K", "NC4K"}.issubset(
        datasets_for_status(rows, exp_id=exp_id, status=status)
    )


def latest_status_by_dataset(rows: list[dict[str, str]], *, exp_id: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for row in rows:
        if row.get("exp_id") == exp_id and row.get("dataset"):
            statuses[row["dataset"].upper()] = row.get("status", "")
    return statuses


def infer_gates(rows: list[dict[str, str]], profiles: dict[str, dict[str, str]]) -> dict[str, GateState]:
    light_done = has_three_dataset_status(
        rows, exp_id="light_b2_c64_e120_s42_prob_eval_v2", status="final_main_light"
    )
    baseline_done = has_three_dataset_status(
        rows, exp_id="baseline_escnet_b5_clean_prob_e120", status="clean_prob_re_eval_complete"
    )
    kd_done = any(
        has_three_dataset_status(rows, exp_id=exp_id, status="final_main_kd")
        for exp_id in {row.get("exp_id", "") for row in rows if "kd" in row.get("exp_id", "")}
    )
    b0_candidate = any(
        row.get("status") == "external_dirty_tree_observation_candidate"
        and (
            "b0" in row.get("exp_id", "").lower()
            or "external_b0" in row.get("repo_boundary", "").lower()
        )
        for row in rows
    )
    mobilemamba_candidate = any(
        row.get("status") == "external_dirty_tree_observation_candidate"
        and (
            "mobilemamba" in row.get("exp_id", "").lower()
            or "external_mobilemamba" in row.get("repo_boundary", "").lower()
        )
        for row in rows
    )
    speed_done = all(
        exp_id in profiles
        and profiles[exp_id].get("latency_ms")
        and profiles[exp_id].get("fps")
        and profiles[exp_id].get("device")
        and profiles[exp_id].get("img_size") == "416"
        and profiles[exp_id].get("warmup") == "50"
        and profiles[exp_id].get("repeat") == "100"
        for exp_id in (
            "baseline_escnet_b5_416_idle",
            "light_b2_c64_trained_416_idle",
            "kd_light_b2_c64_trained_416_idle",
        )
    )
    return {
        "Light main result": GateState(
            "pass" if light_done else "missing",
            "Use Light B2-C64 as current accepted student result."
            if light_done
            else "Do not write a main student result until Light integrity passes.",
        ),
        "Gate 1 clean baseline": GateState(
            "pass" if baseline_done else "pending",
            "Upgrade Light-vs-ESCNet deltas to clean probability baseline."
            if baseline_done
            else "Keep ESCNet-B5 as historical/reference until clean probability re-eval finishes.",
        ),
        "Gate 2 KD": GateState(
            "pass" if kd_done else "pending",
            "Patch KD result into paper according to measured improvement/failure."
            if kd_done
            else "Keep KD as implemented/smoke-tested engineering route only.",
        ),
        "Gate 3 speed": GateState(
            "pass" if speed_done else "pending",
            "Patch controlled latency/FPS according to same-command idle profiles."
            if speed_done
            else "Do not claim final latency/FPS until idle-GPU same-command profile is complete.",
        ),
        "Gate 4A B0": GateState(
            "candidate" if b0_candidate else "observation_only",
            "Only appendix/failure-analysis use after load/profile/prob-eval integrity."
            if b0_candidate
            else "Keep B0 out of main table, abstract and conclusion.",
        ),
        "Gate 4B MobileMamba": GateState(
            "candidate" if mobilemamba_candidate else "observation_only",
            "Only appendix/failure-analysis use after snapshot/load/profile/prob-eval integrity."
            if mobilemamba_candidate
            else "Keep MobileMamba-T2 out of main table, abstract and conclusion.",
        ),
    }


def parse_release(text: str) -> dict[str, str]:
    status = "missing"
    started = "unknown"
    finished = "unknown"
    match = re.search(r"- Overall status: `?([A-Za-z_]+)`?", text)
    if match:
        status = match.group(1)
    start_match = re.search(r"- Started UTC: `([^`]+)`", text)
    if start_match:
        started = start_match.group(1)
    finish_match = re.search(r"- Finished UTC: `([^`]+)`", text)
    if finish_match:
        finished = finish_match.group(1)
    return {"status": status, "started_utc": started, "finished_utc": finished}


def parse_b0_status(text: str) -> dict[str, str]:
    def first(pattern: str, default: str = "unknown") -> str:
        match = re.search(pattern, text)
        return match.group(1).strip() if match else default

    latest_result = "unknown"
    result_rows = re.findall(
        r"^\|\s*(\d+)\s*\|\s*([0-9.]+)\s*\|\s*([0-9.]+)\s*\|\s*([0-9.]+)\s*\|\s*([0-9.]+)\s*\|\s*([0-9.]+)\s*\|",
        text,
        flags=re.MULTILINE,
    )
    if result_rows:
        epoch, s, wf, mean_f, mean_e, mae = result_rows[-1]
        latest_result = f"epoch {epoch}: S={s}, wF={wf}, meanF={mean_f}, meanE={mean_e}, MAE={mae}"
    return {
        "updated_utc": first(r"- Updated UTC: `([^`]+)`"),
        "status": first(r"- Status: `([^`]+)`"),
        "boundary": first(r"- Evidence boundary: `([^`]+)`"),
        "checkpoint_status": first(r"- Checkpoint status: `([^`]+)`"),
        "latest_iter": first(r"- Latest iter: (.+)"),
        "latest_eval": first(r"- Latest eval start: (.+)"),
        "latest_result": latest_result,
    }


def parse_kd_status(text: str) -> dict[str, str]:
    def first(pattern: str, default: str = "unknown") -> str:
        match = re.search(pattern, text)
        return match.group(1).strip() if match else default

    return {
        "updated_utc": first(r"- Updated UTC: `([^`]+)`"),
        "status": first(r"- Status: `([^`]+)`"),
        "boundary": first(r"- Evidence boundary: `([^`]+)`"),
        "config": first(r"- Config: `([^`]+)`"),
        "log": first(r"- Log: `([^`]+)`"),
        "run_dir": first(r"- Run dir: `([^`]+)`"),
        "latest_checkpoint": first(r"- Latest checkpoint: `([^`]+)`"),
        "final_checkpoint_status": first(r"- Final checkpoint status: `([^`]+)`"),
        "latest_iter": first(r"- Latest iter: (.+)"),
        "latest_completed_epoch": first(r"- Latest completed epoch: (.+)"),
    }


def process_lines() -> list[str]:
    output = run_text(["ps", "-eo", "pid,ppid,stat,etime,cmd"])
    return [line for line in output.splitlines() if line.strip()]


def process_stat(line: str) -> str:
    fields = line.strip().split(maxsplit=4)
    return fields[2] if len(fields) >= 3 else ""


def parse_result_txt(path: Path) -> dict[str, str]:
    text = read_text(path)
    match = re.search(
        r"&\s*epoch_120\s*&\s*(\d+)\s*&\s*(\d+)\s*&\s*(\d+)\s*&\s*(\d+)\s*&\s*(\d+)\s*&",
        text,
    )
    if not match:
        return {}
    s, wf, mean_f, mean_e, mae = match.groups()
    return {
        "Smeasure": f"0.{s.zfill(3)}",
        "wFmeasure": f"0.{wf.zfill(3)}",
        "meanFm": f"0.{mean_f.zfill(3)}",
        "meanEm": f"0.{mean_e.zfill(3)}",
        "MAE": f"0.{mae.zfill(3)}",
    }


def watcher_status(processes: list[str]) -> dict[str, dict[str, str]]:
    status: dict[str, dict[str, str]] = {}
    for label, pattern in WATCHERS.items():
        matches = [line.strip() for line in processes if pattern in line and "grep" not in line]
        status[label] = {
            "status": "running" if matches else "missing",
            "process": matches[0] if matches else "",
        }
    return status


def latest_kd_log(config_path: str) -> str:
    if not config_path:
        return ""
    stem = Path(config_path).stem
    if stem.startswith("config_"):
        stem = stem.removeprefix("config_")
    log_dirs = [Path("/dev/shm/escnet_fast_kd/logs"), KD_RUN_DIR / "logs"]
    candidates = sorted(
        [
            candidate
            for log_dir in log_dirs
            if log_dir.is_dir()
            for candidate in log_dir.glob(f"train_{stem}_*.log")
        ],
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    return str(candidates[0]) if candidates else ""


def kd_recovery_status(processes: list[str]) -> dict[str, Any]:
    matches = [
        line.strip()
        for line in processes
        if any(marker in line for marker in KD_CONFIG_MARKERS)
        or any(marker in line for marker in KD_RECOVERY_RUN_MARKERS)
    ]
    process = matches[0] if matches else ""
    pid = ""
    config_path = ""
    if process:
        fields = process.split(None, 1)
        pid = fields[0] if fields else ""
        config_match = re.search(r"--config\s+(\S+)", process)
        if config_match:
            config_path = config_match.group(1)
    return {
        "running": bool(matches),
        "processes": len(matches),
        "process": process,
        "pid": pid,
        "config": config_path,
        "log": latest_kd_log(config_path),
    }


def training_status(processes: list[str]) -> dict[str, Any]:
    train_matches = [
        line.strip()
        for line in processes
        if ("torchrun" in line or " train.py" in line or line.endswith("train.py"))
        and "grep" not in line
        and "orchestrator_tick.py" not in line
    ]
    b0_matches = [line for line in train_matches if "pvt_v2_b0.yaml" in line]
    mobilemamba_matches = [line for line in train_matches if "mobilemamba_t2.yaml" in line]
    gpu_like_matches = [
        line.strip()
        for line in processes
        if any(token in line for token in ("torchrun", " train.py", " test.py", "infer_prob.py"))
        and "grep" not in line
        and "orchestrator_tick.py" not in line
    ]
    return {
        "active_train_processes": len(train_matches),
        "active_gpu_like_processes": len(gpu_like_matches),
        "b0_processes": len(b0_matches),
        "b0_running": bool(b0_matches),
        "mobilemamba_t2_processes": len(mobilemamba_matches),
        "mobilemamba_t2_running": bool(mobilemamba_matches),
        "kd_recovery": kd_recovery_status(processes),
        "sample_processes": train_matches[:8],
    }


def _count_files(path: Path, pattern: str = "*") -> int:
    if not path.is_dir():
        return 0
    return sum(1 for item in path.glob(pattern) if item.is_file())


def baseline_progress(
    *,
    rows: list[dict[str, str]],
    processes: list[str],
    run_dir: Path,
    dataset_root: Path,
) -> dict[str, Any]:
    metrics_status = latest_status_by_dataset(rows, exp_id=BASELINE_EXP_ID)
    active_processes = [
        line.strip()
        for line in processes
        if BASELINE_EXP_ID in line or str(run_dir) in line
    ]
    stopped_processes = [line for line in active_processes if "T" in process_stat(line)]
    dataset_rows: list[dict[str, Any]] = []
    completed_results = set()

    for dataset in REQUIRED_DATASETS:
        gt_count = _count_files(dataset_root / dataset / "GT_Object")
        pred_count = _count_files(run_dir / "preds" / dataset / "epoch_120", "*.png")
        result_txt = run_dir / "results" / dataset / "result.txt"
        result_exists = result_txt.is_file()
        partial_metrics = parse_result_txt(result_txt) if result_exists else {}
        if result_exists:
            completed_results.add(dataset)
        dataset_rows.append(
            {
                "dataset": dataset,
                "gt_count": gt_count,
                "pred_count": pred_count,
                "result_exists": result_exists,
                "metrics_status": metrics_status.get(dataset, ""),
                "partial_metrics": partial_metrics,
            }
        )

    complete = has_three_dataset_status(
        rows, exp_id=BASELINE_EXP_ID, status="clean_prob_re_eval_complete"
    )
    if complete:
        state = "complete"
    elif stopped_processes:
        state = "paused_waiting_gpu"
    elif active_processes:
        state = "running"
    elif run_dir.exists():
        state = "partial_or_interrupted"
    else:
        state = "not_started"

    return {
        "state": state,
        "run_dir": str(run_dir),
        "completed_results": sorted(completed_results),
        "active_processes": active_processes[:8],
        "stopped_processes": stopped_processes[:8],
        "datasets": dataset_rows,
    }


def gpu_snapshot() -> list[str]:
    output = run_text(
        [
            "nvidia-smi",
            "--query-gpu=index,name,memory.used,memory.total,utilization.gpu",
            "--format=csv,noheader,nounits",
        ]
    )
    return [line.strip() for line in output.splitlines() if line.strip()]


def light_profile_summary(profiles: dict[str, dict[str, str]]) -> dict[str, str]:
    ref = profiles.get("baseline_escnet_b5_416_e120", {})
    light = profiles.get("light_b2_c64_trained_416", {})
    return {
        "baseline_params_m": _safe_millions(ref.get("params")),
        "baseline_gmacs": _safe_float(ref.get("gmacs")),
        "light_params_m": _safe_millions(light.get("params")),
        "light_gmacs": _safe_float(light.get("gmacs")),
        "light_peak_mem_mb": _safe_float(light.get("peak_mem_mb")),
    }


def _safe_millions(value: str | None) -> str:
    try:
        return f"{float(value) / 1_000_000:.2f}"
    except Exception:
        return "unknown"


def _safe_float(value: str | None) -> str:
    try:
        return f"{float(value):.2f}"
    except Exception:
        return "unknown"


def write_outputs(
    *,
    out_md: Path,
    out_json: Path,
    payload: dict[str, Any],
) -> None:
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.parent.mkdir(parents=True, exist_ok=True)

    gates: dict[str, dict[str, str]] = payload["gates"]
    watchers: dict[str, dict[str, str]] = payload["watchers"]
    b0: dict[str, str] = payload["b0"]
    mobilemamba: dict[str, str] = payload["mobilemamba"]
    kd_status: dict[str, str] = payload["kd_recovery_status"]
    release: dict[str, str] = payload["release_audit"]
    training: dict[str, Any] = payload["training"]
    kd_recovery: dict[str, Any] = training.get("kd_recovery", {})
    profile: dict[str, str] = payload["profile_summary"]
    baseline: dict[str, Any] = payload["baseline_progress"]
    gate1_pass = gates.get("Gate 1 clean baseline", {}).get("status") == "pass"
    delta_line = (
        "- Current Light-vs-ESCNet deltas use the clean probability baseline."
        if gate1_pass
        else "- Current Light-vs-ESCNet deltas remain relative to the historical ESCNet-B5 reference until Gate 1."
    )
    queue_step2 = (
        "2. Gate 1 is complete; baseline/resume watchers are no longer required."
        if gate1_pass
        else "2. If Gate 1 is paused, let the resume watcher continue it only after GPU-like work is idle."
    )
    gate2_pass = gates.get("Gate 2 KD", {}).get("status") == "pass"
    gate3_pass = gates.get("Gate 3 speed", {}).get("status") == "pass"
    if gate1_pass and gate2_pass and gate3_pass:
        queue_step3 = (
            "3. Gate 2 KD eval and Gate 3 controlled speed are complete. Patch the "
            "paper and delivery docs with the measured KD neutral/negative result and "
            "the controlled latency/FPS evidence, then rerun release audits."
        )
    elif gate1_pass and gate2_pass:
        queue_step3 = (
            "3. Gate 2 KD eval is complete. Run Gate 3 controlled speed profiles on an "
            "idle GPU before writing final latency/FPS claims."
        )
    elif gate1_pass and kd_recovery.get("running"):
        queue_step3 = (
            "3. KD recovery is running; do not restart the KD watcher or duplicate "
            "`start_kd_full_train.sh`. Monitor the log/checkpoints, then run Gate 2 "
            "probability eval after a valid final checkpoint exists."
        )
    elif gate1_pass and kd_status.get("final_checkpoint_status") == "present":
        queue_step3 = (
            "3. KD final checkpoint is present; run Gate 2 CAMO/COD10K/NC4K probability "
            "eval, integrity checks, and release audits before making any KD claims."
        )
    elif gate1_pass:
        queue_step3 = (
            "3. KD recovery is paused by user instruction; do not restart the KD watcher. "
            "Prioritize fixing/resuming the 4-GPU KD route before any single-GPU fallback."
        )
    else:
        queue_step3 = "3. After Gate 1 passes, let the KD watcher start KD B2-C64 recovery."

    lines = [
        "# Orchestrator Tick Latest",
        "",
        f"- Updated UTC: `{payload['updated_utc']}`",
        f"- Workspace: `{payload['workspace']}`",
        f"- Release audit: `{release['status']}` (finished `{release['finished_utc']}`)",
        "",
        "## Gate State",
        "",
        "| Gate | Status | Action |",
        "| --- | --- | --- |",
    ]
    for gate, state in gates.items():
        lines.append(f"| {gate} | {state['status']} | {state['action']} |")

    lines.extend(
        [
            "",
            "## Current Runs",
            "",
            f"- Active train-like processes: {training['active_train_processes']}",
            f"- Active GPU-like processes: {training['active_gpu_like_processes']}",
            f"- B0 running: `{str(training['b0_running']).lower()}` "
            f"(process lines: {training['b0_processes']})",
            f"- MobileMamba-T2 running: `{str(training['mobilemamba_t2_running']).lower()}` "
            f"(process lines: {training['mobilemamba_t2_processes']})",
            f"- KD recovery running: `{str(kd_recovery.get('running', False)).lower()}` "
            f"(process lines: {kd_recovery.get('processes', 0)})",
            f"- KD recovery config: `{kd_recovery.get('config') or kd_status.get('config') or 'none'}`",
            f"- KD recovery log: `{kd_recovery.get('log') or kd_status.get('log') or 'none'}`",
            f"- KD recovery status report: `{payload['kd_status_path']}`",
            f"- KD recovery latest iter: {kd_status['latest_iter']}",
            f"- KD recovery latest checkpoint: `{kd_status['latest_checkpoint']}`",
            f"- KD recovery final checkpoint: `{kd_status['final_checkpoint_status']}`",
            f"- MobileMamba-T2 latest iter: {mobilemamba['latest_iter']}",
            f"- MobileMamba-T2 latest result: {mobilemamba['latest_result']}",
            f"- MobileMamba-T2 boundary: `{mobilemamba['boundary']}`",
            f"- B0 status updated: `{b0['updated_utc']}`",
            f"- B0 latest iter: {b0['latest_iter']}",
            f"- B0 latest eval: {b0['latest_eval']}",
            f"- B0 latest result: {b0['latest_result']}",
            f"- B0 boundary: `{b0['boundary']}`",
            f"- Gate 1 baseline run: `{baseline['state']}`",
            f"- Gate 1 stopped process lines: {len(baseline['stopped_processes'])}",
            "",
            "## Watchers",
            "",
            "| Watcher | Status | Process |",
            "| --- | --- | --- |",
        ]
    )
    for label, state in watchers.items():
        process = state["process"].replace("|", "\\|") if state["process"] else ""
        lines.append(f"| {label} | {state['status']} | `{process}` |")
    if kd_recovery.get("running"):
        lines.extend(
            [
                "",
                "- Gate 2 KD watcher may be missing because KD recovery has already launched; "
                "do not restart it while the KD recovery process is running.",
            ]
        )

    lines.extend(["", "## GPU Snapshot", ""])
    lines.extend([f"- `{line}`" for line in payload["gpu_snapshot"]] or ["- unavailable"])

    lines.extend(
        [
            "",
            "## Gate 1 Baseline Progress",
            "",
            f"- Run dir: `{baseline['run_dir']}`",
            f"- Completed result files: `{','.join(baseline['completed_results']) or 'none'}`",
            "",
            "| Dataset | GT | Pred PNG | Result | S | wF | meanF | meanE | MAE | Metrics Status |",
            "| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in baseline["datasets"]:
        result_state = "yes" if row["result_exists"] else "no"
        metrics = row.get("partial_metrics") or {}
        lines.append(
            f"| {row['dataset']} | {row['gt_count']} | {row['pred_count']} | "
            f"{result_state} | {metrics.get('Smeasure', '')} | "
            f"{metrics.get('wFmeasure', '')} | {metrics.get('meanFm', '')} | "
            f"{metrics.get('meanEm', '')} | {metrics.get('MAE', '')} | "
            f"`{row['metrics_status']}` |"
        )

    lines.extend(
        [
            "",
            "## Accepted Core Result",
            "",
            "- Light-ESCNet B2-C64 no-KD remains the accepted student result.",
            f"- Params: {profile['light_params_m']}M vs baseline {profile['baseline_params_m']}M.",
            f"- GMACs: {profile['light_gmacs']} vs baseline {profile['baseline_gmacs']}.",
            f"- Light peak memory: {profile['light_peak_mem_mb']} MB.",
            delta_line,
            "",
            "## Next Queue",
            "",
            f"1. Gate 1 baseline state is `{baseline['state']}`; do not duplicate the wrapper.",
            queue_step2,
            queue_step3,
            "4. Keep B0/MobileMamba external dirty-tree branches out of the main table unless their candidate integrity gates pass.",
            "5. Re-run release audits after every metrics/profile/manuscript change.",
        ]
    )

    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    if args.refresh_b0:
        refresh_b0_status(Path(args.b0_summarizer))
    if args.refresh_mobilemamba:
        refresh_mobilemamba_status(Path(args.mobilemamba_summarizer))
    if args.refresh_kd:
        refresh_kd_status(Path(args.kd_summarizer))

    metrics = parse_metrics(Path(args.metrics_csv))
    profiles = parse_profiles(Path(args.profiles_csv))
    processes = process_lines()
    gates = infer_gates(metrics, profiles)

    return {
        "updated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "workspace": str(WORKSPACE),
        "metrics_csv": str(Path(args.metrics_csv)),
        "profiles_csv": str(Path(args.profiles_csv)),
        "gates": {
            name: {"status": state.status, "action": state.action}
            for name, state in gates.items()
        },
        "release_audit": parse_release(read_text(Path(args.release_audit))),
        "b0": parse_b0_status(read_text(Path(args.b0_status))),
        "mobilemamba": parse_b0_status(read_text(Path(args.mobilemamba_status))),
        "kd_recovery_status": parse_kd_status(read_text(Path(args.kd_status))),
        "kd_status_path": str(Path(args.kd_status)),
        "watchers": watcher_status(processes),
        "training": training_status(processes),
        "baseline_progress": baseline_progress(
            rows=metrics,
            processes=processes,
            run_dir=Path(args.baseline_run_dir),
            dataset_root=Path(args.dataset_root),
        ),
        "gpu_snapshot": gpu_snapshot(),
        "profile_summary": light_profile_summary(profiles),
        "delta_summary": str(Path(args.delta_summary)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics_csv", default=str(DEFAULT_METRICS))
    parser.add_argument("--profiles_csv", default=str(DEFAULT_PROFILE))
    parser.add_argument("--b0_status", default=str(DEFAULT_B0_STATUS))
    parser.add_argument("--mobilemamba_status", default=str(DEFAULT_MOBILEMAMBA_STATUS))
    parser.add_argument("--kd_status", default=str(DEFAULT_KD_STATUS))
    parser.add_argument("--baseline_run_dir", default=str(DEFAULT_BASELINE_RUN))
    parser.add_argument("--dataset_root", default=str(DEFAULT_DATASET_ROOT))
    parser.add_argument("--release_audit", default=str(DEFAULT_RELEASE))
    parser.add_argument("--delta_summary", default=str(DEFAULT_DELTA))
    parser.add_argument("--b0_summarizer", default=str(DEFAULT_B0_SUMMARIZER))
    parser.add_argument("--mobilemamba_summarizer", default=str(DEFAULT_MOBILEMAMBA_SUMMARIZER))
    parser.add_argument("--kd_summarizer", default=str(DEFAULT_KD_SUMMARIZER))
    parser.add_argument("--out_md", default=str(DEFAULT_OUT_MD))
    parser.add_argument("--out_json", default=str(DEFAULT_OUT_JSON))
    parser.add_argument(
        "--no_refresh_b0",
        action="store_false",
        dest="refresh_b0",
        help="Do not call summarize_external_b0.py before reading B0 status.",
    )
    parser.add_argument(
        "--no_refresh_mobilemamba",
        action="store_false",
        dest="refresh_mobilemamba",
        help="Do not call summarize_external_mobilemamba.py before reading MobileMamba status.",
    )
    parser.add_argument(
        "--no_refresh_kd",
        action="store_false",
        dest="refresh_kd",
        help="Do not call summarize_kd_recovery.py before reading KD status.",
    )
    parser.set_defaults(refresh_b0=True)
    parser.set_defaults(refresh_mobilemamba=True)
    parser.set_defaults(refresh_kd=True)
    args = parser.parse_args()

    payload = build_payload(args)
    write_outputs(out_md=Path(args.out_md), out_json=Path(args.out_json), payload=payload)

    print(f"orchestrator_tick=pass")
    print(f"report={Path(args.out_md)}")
    print(f"json={Path(args.out_json)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
