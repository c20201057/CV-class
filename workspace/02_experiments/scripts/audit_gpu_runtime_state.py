#!/usr/bin/env python3
"""Audit live GPU handoff processes against the current orchestrator tick.

This is a read-only runtime guard. The document-level handoff audit proves
that the instructions are consistent; this script proves that the live watcher
chain still matches those instructions.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


WORKSPACE = Path("/root/data-tmp/workspace")
DEFAULT_TICK = WORKSPACE / "00_project" / "orchestrator_tick_latest.json"
DEFAULT_METRICS = WORKSPACE / "02_experiments" / "tables" / "metrics_all.csv"
DEFAULT_OUT = WORKSPACE / "00_project" / "gpu_runtime_state_audit_latest.md"

BASELINE_EXP_ID = "baseline_escnet_b5_clean_prob_e120"
BASELINE_RUN_DIR = WORKSPACE / "02_experiments" / "runs" / BASELINE_EXP_ID
KD_RECOVERY_RUNS = [
    WORKSPACE / "02_experiments" / "runs" / "kd_light_b2_c64_e120_s42_recover_b2w0_4gpu",
    WORKSPACE / "02_experiments" / "runs" / "kd_light_b2_c64_e120_s42_recover_b2w0_2gpu",
    WORKSPACE / "02_experiments" / "runs" / "kd_light_b2_c64_e120_s42_recover_b2w0_1gpu",
    Path("/dev/shm/escnet_fast_kd/runs/kd_light_b2_c64_e120_s42_recover_epoch10_fast_shm_4gpu"),
    WORKSPACE / "02_experiments" / "runs" / "kd_light_b2_c64_e120_s42_recover_epoch10_fast_shm_4gpu",
    Path("/dev/shm/escnet_fast_kd/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu"),
    WORKSPACE / "02_experiments" / "runs" / "kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu",
]
KD_CONFIG_MARKERS = [
    "config_resume_epoch5_b2_workers0_4gpu.yaml",
    "config_resume_epoch5_b2_workers0_2gpu.yaml",
    "config_resume_epoch5_b2_workers0_1gpu.yaml",
    "config_resume_epoch10_fast_shm_4gpu.yaml",
    "config_continue_epoch20_b6_w8_4gpu.yaml",
]
KD_MASTER_PORT_MARKERS = ["--master_port=29505", "--master_port=29506", "--master_port=29508", "--master_port=29511"]

REQUIRED_LOGS = [
    WORKSPACE / "02_experiments" / "runs" / "watch_gpu_then_start_baseline_clean.log",
    WORKSPACE / "02_experiments" / "runs" / "resume_stopped_baseline_prob_eval_when_gpu_idle.log",
    WORKSPACE / "02_experiments" / "runs" / "watch_baseline_then_start_kd.log",
    WORKSPACE / "02_experiments" / "runs" / "watch_external_mobilemamba_progress.log",
]


@dataclass(frozen=True)
class Finding:
    level: str
    message: str


@dataclass(frozen=True)
class Proc:
    pid: int
    ppid: int
    stat: str
    etime: str
    args: str


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_processes() -> list[Proc]:
    output = subprocess.check_output(
        ["ps", "-eo", "pid=,ppid=,stat=,etime=,args="],
        text=True,
    )
    rows: list[Proc] = []
    for line in output.splitlines():
        parts = line.strip().split(None, 4)
        if len(parts) < 5:
            continue
        pid, ppid, stat, etime, args = parts
        try:
            rows.append(Proc(int(pid), int(ppid), stat, etime, args))
        except ValueError:
            continue
    return rows


def find_procs(procs: list[Proc], *needles: str) -> list[Proc]:
    return [proc for proc in procs if all(needle in proc.args for needle in needles)]


def find_script_procs(procs: list[Proc], script_name: str) -> list[Proc]:
    """Return processes that are actually executing a script.

    Plain substring matching also catches transient parent shells whose command
    text contains the script path. That is too loose for watcher-count audits.
    """
    matches: list[Proc] = []
    for proc in procs:
        try:
            tokens = shlex.split(proc.args)
        except ValueError:
            tokens = proc.args.split()
        executable = Path(tokens[0]).name if tokens else ""
        if executable in {"bash", "sh"} and len(tokens) > 1 and Path(tokens[1]).name == script_name:
            matches.append(proc)
        elif executable == script_name:
            matches.append(proc)
    return matches


def pid_exists(procs: list[Proc], pid: int) -> Proc | None:
    for proc in procs:
        if proc.pid == pid:
            return proc
    return None


def extract_pid_arg(args: str, name: str) -> int | None:
    match = re.search(rf"(?:^|\s){re.escape(name)}\s+([0-9]+)(?:\s|$)", args)
    if not match:
        return None
    return int(match.group(1))


def baseline_complete(metrics_csv: Path) -> bool:
    if not metrics_csv.is_file():
        return False
    required = {"CAMO", "COD10K", "NC4K"}
    rows: list[dict[str, str]] = []
    with metrics_csv.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("exp_id") == BASELINE_EXP_ID:
                rows.append(dict(row))
    if not rows:
        return False
    datasets = {row.get("dataset", "").upper() for row in rows}
    statuses = {row.get("status", "") for row in rows}
    protocols = {row.get("protocol", "") for row in rows}
    return required.issubset(datasets) and statuses == {"clean_prob_re_eval_complete"} and protocols == {"prob_map"}


def audit_logs(findings: list[Finding], notes: list[str]) -> None:
    for log_path in REQUIRED_LOGS:
        if not log_path.is_file():
            findings.append(Finding("error", f"missing watcher log: {log_path}"))
            continue
        if log_path.stat().st_size == 0:
            findings.append(Finding("error", f"empty watcher log: {log_path}"))
            continue
        notes.append(f"log ok: {log_path}")


def audit_runtime(tick: dict, metrics_csv: Path, procs: list[Proc], findings: list[Finding], notes: list[str]) -> None:
    gates = tick.get("gates", {})
    baseline = tick.get("baseline_progress", {})
    training = tick.get("training", {})
    mobile = tick.get("mobilemamba", {})
    baseline_is_complete = baseline_complete(metrics_csv)

    gate1_status = gates.get("Gate 1 clean baseline", {}).get("status")
    if baseline_is_complete:
        if gate1_status not in {"pending", "pass"}:
            findings.append(Finding("error", f"Gate 1 status `{gate1_status}` is incompatible with complete baseline metrics"))
        notes.append("baseline metrics complete; runtime audit allows Gate 1 -> KD handoff")
    elif gate1_status != "pending":
        findings.append(Finding("error", "Gate 1 status is not pending while baseline metrics are incomplete"))

    if gates.get("Gate 2 KD", {}).get("status") not in {"pending", "pass"}:
        findings.append(Finding("error", "Gate 2 status is not pending; runtime audit needs a route update"))

    if not baseline_is_complete and baseline.get("state") != "paused_waiting_gpu":
        findings.append(Finding("error", f"baseline state is `{baseline.get('state')}`, expected paused_waiting_gpu"))

    completed = set(baseline.get("completed_results", []))
    if not baseline_is_complete and not {"CAMO", "COD10K"}.issubset(completed):
        findings.append(Finding("error", f"baseline completed datasets are {sorted(completed)}, expected CAMO/COD10K"))
    if not baseline_is_complete and "NC4K" in completed:
        findings.append(Finding("error", "baseline NC4K is marked complete but Gate 1 is still pending"))

    stopped_wrappers = [
        proc
        for proc in find_procs(procs, "run_prob_eval_suite.sh", BASELINE_EXP_ID)
        if "T" in proc.stat
    ]
    if baseline_is_complete:
        target_wrapper = stopped_wrappers[0] if stopped_wrappers else None
        if stopped_wrappers:
            notes.append(
                "baseline metrics are complete but a stopped Gate 1 wrapper is still present: "
                + ", ".join(str(proc.pid) for proc in stopped_wrappers)
            )
    elif len(stopped_wrappers) != 1:
        findings.append(Finding("error", f"expected exactly one stopped Gate 1 wrapper, found {len(stopped_wrappers)}"))
        target_wrapper: Proc | None = stopped_wrappers[0] if stopped_wrappers else None
    else:
        target_wrapper = stopped_wrappers[0]
        notes.append(f"stopped Gate 1 wrapper ok: pid={target_wrapper.pid} stat={target_wrapper.stat}")
        required_args = [
            str(BASELINE_RUN_DIR.parent),
            "/root/data-tmp/epoch_120.pth",
            "clean_baseline_snapshot",
            "clean_prob_re_eval_pending_integrity",
            "CAMO,COD10K,NC4K",
        ]
        for marker in required_args:
            if marker not in target_wrapper.args:
                findings.append(Finding("error", f"stopped Gate 1 wrapper missing arg marker `{marker}`"))

    active_baseline_gpu = [
        proc
        for proc in procs
        if ("infer_prob.py" in proc.args or "eval.py" in proc.args)
        and BASELINE_EXP_ID in proc.args
        and "T" not in proc.stat
    ]
    if not baseline_is_complete and active_baseline_gpu:
        findings.append(
            Finding(
                "error",
                "baseline eval has active GPU-like children while MobileMamba is busy: "
                + ", ".join(str(proc.pid) for proc in active_baseline_gpu),
            )
        )

    baseline_watchers = find_procs(procs, "watch_gpu_then_start_baseline_clean.sh")
    main_baseline_watchers = [proc for proc in baseline_watchers if "--device cuda:0" in proc.args]
    if baseline_is_complete:
        notes.append(f"baseline watcher count after completion: {len(main_baseline_watchers)}")
    elif len(main_baseline_watchers) != 1:
        findings.append(Finding("error", f"expected one main baseline watcher, found {len(main_baseline_watchers)}"))
    else:
        notes.append(f"baseline watcher ok: pid={main_baseline_watchers[0].pid}")

    resume_watchers = find_procs(procs, "resume_stopped_prob_eval_when_gpu_idle.sh")
    if baseline_is_complete:
        notes.append(f"resume watcher count after baseline completion: {len(resume_watchers)}")
    elif len(resume_watchers) != 1:
        findings.append(Finding("error", f"expected one resume watcher, found {len(resume_watchers)}"))
    else:
        resume = resume_watchers[0]
        target_pid = extract_pid_arg(resume.args, "--pid")
        if target_pid is None:
            findings.append(Finding("error", "resume watcher does not expose --pid"))
        elif target_wrapper is not None and target_pid != target_wrapper.pid:
            findings.append(
                Finding(
                    "error",
                    f"resume watcher targets pid {target_pid}, expected stopped wrapper pid {target_wrapper.pid}",
                )
            )
        elif target_pid is not None and pid_exists(procs, target_pid) is None:
            findings.append(Finding("error", f"resume watcher target pid {target_pid} no longer exists"))
        else:
            notes.append(f"resume watcher ok: pid={resume.pid} target={target_pid}")

    kd_train_markers = [
        *KD_CONFIG_MARKERS,
        *KD_MASTER_PORT_MARKERS,
        *(str(path) for path in KD_RECOVERY_RUNS),
    ]
    kd_running = [proc for proc in procs if any(marker in proc.args for marker in kd_train_markers)]
    kd_final_checkpoints = [path / "epoch_120.pth" for path in KD_RECOVERY_RUNS if (path / "epoch_120.pth").exists()]

    kd_watchers = find_script_procs(procs, "watch_baseline_then_start_kd.sh")
    if len(kd_watchers) != 1:
        if baseline_is_complete and (kd_running or kd_final_checkpoints):
            notes.append(
                "KD watcher is absent because KD recovery has launched/completed: "
                f"watchers={len(kd_watchers)}"
            )
        elif baseline_is_complete:
            notes.append(
                "KD watcher is absent because KD is paused for 4-GPU recovery work; "
                f"watchers={len(kd_watchers)}"
            )
        else:
            findings.append(Finding("error", f"expected one KD watcher, found {len(kd_watchers)}"))
    else:
        notes.append(f"KD watcher ok: pid={kd_watchers[0].pid}")

    if kd_running and not baseline_is_complete:
        findings.append(Finding("error", "KD recovery appears launched before Gate 1 completion"))
    elif kd_running:
        notes.append("KD recovery process is allowed because baseline metrics are complete")
    for checkpoint in kd_final_checkpoints:
        notes.append(
            "KD recovery final checkpoint exists; Gate 2 eval/acceptance must decide whether it is paper evidence: "
            f"{checkpoint}"
        )

    if training.get("mobilemamba_t2_running") is True:
        mobile_procs = find_procs(procs, "configs/mobilemamba_t2.yaml")
        if len(mobile_procs) < 5:
            findings.append(Finding("error", f"tick says MobileMamba running but only {len(mobile_procs)} processes found"))
        if mobile.get("checkpoint_status") != "absent":
            findings.append(Finding("error", f"MobileMamba checkpoint status is `{mobile.get('checkpoint_status')}`, expected absent"))
        notes.append(f"MobileMamba runtime ok: processes={len(mobile_procs)} latest={mobile.get('latest_iter', 'unknown')}")
    else:
        notes.append("MobileMamba is not marked running in tick; Gate 1 handoff may be imminent")


def write_report(out_md: Path, tick_path: Path, metrics_csv: Path, findings: list[Finding], notes: list[str]) -> None:
    errors = [item.message for item in findings if item.level == "error"]
    warnings = [item.message for item in findings if item.level == "warning"]
    status = "pass" if not errors else "fail"
    out_md.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# GPU Runtime State Audit",
        "",
        f"- Status: `{status}`",
        f"- Tick JSON: `{tick_path}`",
        f"- Metrics CSV: `{metrics_csv}`",
        f"- Errors: {len(errors)}",
        f"- Warnings: {len(warnings)}",
        "",
        "## Errors",
        "",
        *([f"- {item}" for item in errors] or ["- none"]),
        "",
        "## Warnings",
        "",
        *([f"- {item}" for item in warnings] or ["- none"]),
        "",
        "## Notes",
        "",
        *([f"- {item}" for item in notes] or ["- none"]),
    ]
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tick_json", default=str(DEFAULT_TICK))
    parser.add_argument("--metrics_csv", default=str(DEFAULT_METRICS))
    parser.add_argument("--out_md", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    tick_path = Path(args.tick_json).expanduser().resolve()
    metrics_csv = Path(args.metrics_csv).expanduser().resolve()
    out_md = Path(args.out_md).expanduser().resolve()

    findings: list[Finding] = []
    notes: list[str] = []

    if not tick_path.is_file():
        findings.append(Finding("error", f"missing tick JSON: {tick_path}"))
        tick: dict = {}
    else:
        tick = load_json(tick_path)
        notes.append(f"tick updated: {tick.get('updated_utc', 'unknown')}")

    if not metrics_csv.is_file():
        findings.append(Finding("error", f"missing metrics CSV: {metrics_csv}"))

    audit_logs(findings, notes)
    if tick and metrics_csv.is_file():
        audit_runtime(tick, metrics_csv, read_processes(), findings, notes)

    write_report(out_md, tick_path, metrics_csv, findings, notes)

    errors = [finding for finding in findings if finding.level == "error"]
    for finding in findings:
        stream = sys.stderr if finding.level == "error" else sys.stdout
        print(f"{finding.level.upper()}: {finding.message}", file=stream)
    print(f"gpu_runtime_state_audit={'pass' if not errors else 'fail'}")
    print(f"report={out_md}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
