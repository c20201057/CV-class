#!/usr/bin/env python3
"""Audit GPU handoff documents against the current orchestrator tick.

This is a read-only workflow guard. It checks the handoff materials that a
future GPU operator will read before taking over Gate 1 baseline, KD recovery
and speed profiling. The goal is to catch stale or dangerous instructions such
as duplicating the paused Gate 1 wrapper, treating MobileMamba as a main result,
or skipping KD because it is risky.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


WORKSPACE = Path("/root/data-tmp/workspace")
DEFAULT_TICK = WORKSPACE / "00_project" / "orchestrator_tick_latest.json"
DEFAULT_OUT = WORKSPACE / "00_project" / "gpu_handoff_consistency_audit_latest.md"

HANDOFF_TARGETS = [
    WORKSPACE / "02_experiments" / "scripts" / "GPU_QUEUE.md",
    WORKSPACE / "00_project" / "current_run_snapshot.md",
    WORKSPACE / "00_project" / "resume_handoff.md",
    WORKSPACE / "00_project" / "orchestrator_status.md",
    WORKSPACE / "03_agent_tasks" / "task_board.md",
    WORKSPACE / "03_agent_tasks" / "pending" / "P0_gpu_queue_operator.md",
    WORKSPACE / "03_agent_tasks" / "pending" / "P0_gate1_kd_handoff_card.md",
    WORKSPACE / "03_agent_tasks" / "prompts" / "DISPATCH_PACKETS.md",
    WORKSPACE / "03_agent_tasks" / "acceptance" / "gate_result_acceptance_runbook.md",
]

CORE_MARKERS = {
    "no_duplicate_gate1": [
        "不要重复启动",
        "do not duplicate",
        "paused Gate 1",
        "暂停",
    ],
    "resume_watcher": [
        "resume_stopped_prob_eval_when_gpu_idle",
        "resume watcher",
        "恢复 watcher",
    ],
    "kd_after_gate1": [
        "watch_baseline_then_start_kd",
        "Gate 1",
        "KD",
    ],
    "non_lazy_non_conservative": [
        "不偷懒",
        "不因为怕风险而保守",
    ],
    "data_tmp_boundary": [
        "/root/data-tmp/workspace",
        "/root/data-tmp/tmp",
    ],
}

FORBIDDEN_DYNAMIC_PATTERNS = [
    ("stale MobileMamba epoch11 wording", re.compile(r"epoch 11/120|epoch10 COD10K")),
    (
        "hard-coded MobileMamba live epoch in handoff text",
        re.compile(
            r"(?i)(?:MobileMamba[^\n]*(?:latest|current|refresh|around|tick|最新|当前|刷新|记录到|已到)[^\n]*epoch\s*\d+\s*/\s*120|(?:latest|current|refresh|around|tick|最新|当前|刷新|记录到|已到)[^\n]*MobileMamba[^\n]*epoch\s*\d+\s*/\s*120)"
        ),
    ),
]

MANUAL_BASELINE_PATTERN = re.compile(
    r"(?:先|直接|优先|马上|立即)[^。\n]*start_baseline_prob_eval_clean"
)
SAFE_MANUAL_BASELINE_CONTEXT = re.compile(r"不要|不得|除非|only if|wrapper 不存在|已消失", re.I)


@dataclass(frozen=True)
class Finding:
    level: str
    message: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_tick(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def contains_any(text: str, needles: list[str]) -> bool:
    lower = text.lower()
    return any(item.lower() in lower for item in needles)


def metric_tokens(text: str) -> list[str]:
    return re.findall(r"\d+\.\d+", text)


def metric_token_present(all_text: str, token: str) -> bool:
    if token in all_text:
        return True
    if token.startswith("0."):
        return token[1:] in all_text
    return False


def audit_required_files(findings: list[Finding], notes: list[str]) -> None:
    for path in HANDOFF_TARGETS:
        if not path.is_file():
            findings.append(Finding("error", f"missing handoff target: {path}"))
        elif path.stat().st_size == 0:
            findings.append(Finding("error", f"empty handoff target: {path}"))
        else:
            notes.append(f"handoff target ok: {path}")


def audit_tick_state(tick: dict, findings: list[Finding], notes: list[str]) -> None:
    gates = tick.get("gates", {})
    training = tick.get("training", {})
    baseline = tick.get("baseline_progress", {})
    mobile = tick.get("mobilemamba", {})
    b0 = tick.get("b0", {})
    watchers = tick.get("watchers", {})

    allowed_gates = {
        "Light main result": {"pass"},
        "Gate 1 clean baseline": {"pending", "pass"},
        "Gate 2 KD": {"pending", "pass"},
        "Gate 3 speed": {"pending", "pass"},
        "Gate 4A B0": {"observation_only", "candidate"},
        "Gate 4B MobileMamba": {"observation_only", "candidate"},
    }
    for gate, expected in allowed_gates.items():
        actual = gates.get(gate, {}).get("status")
        if actual not in expected:
            findings.append(Finding("error", f"{gate} status `{actual}` not in {sorted(expected)}"))

    if training.get("mobilemamba_t2_running") is not True:
        notes.append("MobileMamba-T2 not running in current tick.")
    else:
        notes.append(f"MobileMamba-T2 running: {mobile.get('latest_iter', 'unknown')}")

    if training.get("b0_running") is True:
        findings.append(
            Finding(
                "error",
                "B0 external dirty-tree process is running, but the user has removed B0 from the active plan",
            )
        )
    if b0.get("boundary") != "external_dirty_tree_observation_only":
        findings.append(Finding("error", f"B0 boundary is `{b0.get('boundary')}`"))
    if mobile.get("boundary") != "external_dirty_tree_observation_only":
        findings.append(Finding("error", f"MobileMamba boundary is `{mobile.get('boundary')}`"))

    gate1_status = gates.get("Gate 1 clean baseline", {}).get("status")
    completed = set(baseline.get("completed_results", []))
    if gate1_status == "pass":
        if baseline.get("state") != "complete":
            findings.append(Finding("error", f"Gate 1 passed but baseline state is `{baseline.get('state')}`"))
        missing = {"CAMO", "COD10K", "NC4K"} - completed
        if missing:
            findings.append(Finding("error", f"Gate 1 passed but completed results miss {sorted(missing)}"))
        notes.append("Gate 1 baseline is complete; baseline/resume watchers may be absent.")
    else:
        if not {"CAMO", "COD10K"}.issubset(completed):
            findings.append(Finding("error", f"Gate 1 should have CAMO/COD10K complete, found {sorted(completed)}"))
        if "NC4K" in completed:
            findings.append(Finding("error", "Gate 1 unexpectedly lists NC4K complete while status is pending"))
        if baseline.get("state") != "paused_waiting_gpu":
            findings.append(Finding("error", f"Gate 1 baseline state is `{baseline.get('state')}`"))
        stopped = baseline.get("stopped_processes", [])
        if not stopped:
            findings.append(Finding("error", "Gate 1 has no stopped wrapper process recorded"))

    required_watchers = {
        "MobileMamba read-only watcher": "watch_external_mobilemamba_progress",
    }
    if gate1_status != "pass":
        required_watchers.update(
            {
                "Gate 1 baseline watcher": "watch_gpu_then_start_baseline_clean",
                "Gate 1 resume watcher": "resume_stopped_prob_eval_when_gpu_idle",
            }
        )
    for watcher, command_hint in required_watchers.items():
        info = watchers.get(watcher, {})
        if info.get("status") != "running":
            findings.append(Finding("error", f"{watcher} not running"))
            continue
        if command_hint not in info.get("process", ""):
            findings.append(Finding("error", f"{watcher} process missing `{command_hint}`"))

    b0_watcher = watchers.get("B0 read-only watcher", {})
    if b0_watcher.get("status") == "running":
        findings.append(
            Finding(
                "error",
                "B0 read-only watcher is running, but B0 is outside the current plan and should not be restarted",
            )
        )
    else:
        notes.append("B0 read-only watcher is absent as expected after the user removed B0 from scope.")

    kd_info = watchers.get("Gate 2 KD watcher", {})
    kd_recovery = training.get("kd_recovery", {})
    if gate1_status == "pass" and kd_recovery.get("running") is True:
        notes.append("KD recovery is running; KD watcher may be absent after handoff.")
    elif gate1_status == "pass":
        notes.append("Gate 1 is complete and KD is paused for 4-GPU recovery work; KD watcher should stay absent.")
    elif kd_info.get("status") != "running":
        findings.append(Finding("error", "Gate 2 KD watcher not running"))
    elif "watch_baseline_then_start_kd" not in kd_info.get("process", ""):
        findings.append(Finding("error", "Gate 2 KD watcher process missing `watch_baseline_then_start_kd`"))


def audit_handoff_texts(tick: dict, findings: list[Finding], notes: list[str]) -> None:
    all_text = ""
    gate1_status = tick.get("gates", {}).get("Gate 1 clean baseline", {}).get("status")
    for path in HANDOFF_TARGETS:
        if not path.is_file():
            continue
        text = read_text(path)
        all_text += "\n" + text
        for label, pattern in FORBIDDEN_DYNAMIC_PATTERNS:
            if pattern.search(text):
                findings.append(Finding("error", f"{path}: stale/dangerous wording: {label}"))
        for line in text.splitlines():
            if MANUAL_BASELINE_PATTERN.search(line) and not SAFE_MANUAL_BASELINE_CONTEXT.search(line):
                findings.append(
                    Finding(
                        "error",
                        f"{path}: manual baseline command lacks safe context: {line.strip()}",
                    )
                )

    for marker_name, alternatives in CORE_MARKERS.items():
        if not contains_any(all_text, alternatives):
            findings.append(
                Finding(
                    "error",
                    f"handoff docs missing marker group `{marker_name}`: {alternatives}",
                )
            )

    required_exact = [
        "P0_gate1_kd_handoff_card.md",
        "MobileMamba",
        "clean_prob_re_eval_complete",
        "epoch_5.pth",
        "external_dirty_tree_observation_only",
    ]
    if gate1_status != "pass":
        required_exact.extend(["last command", "最后一个"])
    for marker in required_exact:
        if marker not in all_text:
            findings.append(Finding("error", f"handoff docs missing required marker `{marker}`"))

    mobile = tick.get("mobilemamba", {})
    latest_result = mobile.get("latest_result", "")
    missing_mobile_metrics = [
        token for token in metric_tokens(latest_result) if not metric_token_present(all_text, token)
    ]
    if missing_mobile_metrics:
        findings.append(
            Finding(
                "error",
                "handoff docs do not mention current MobileMamba metric tokens "
                f"{missing_mobile_metrics} from `{latest_result}`",
            )
        )
    if "epoch 20" in latest_result and "epoch20 COD10K" not in all_text and "epoch20" not in all_text:
        findings.append(Finding("error", "handoff docs missing epoch20 MobileMamba status marker"))

    notes.append("handoff text marker coverage checked")


def write_report(out_md: Path, findings: list[Finding], notes: list[str], tick_path: Path) -> None:
    errors = [item.message for item in findings if item.level == "error"]
    warnings = [item.message for item in findings if item.level == "warning"]
    status = "pass" if not errors else "fail"
    out_md.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# GPU Handoff Consistency Audit",
        "",
        f"- Status: `{status}`",
        f"- Tick JSON: `{tick_path}`",
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
        *[f"- {item}" for item in notes],
    ]
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tick_json", default=str(DEFAULT_TICK))
    parser.add_argument("--out_md", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    tick_path = Path(args.tick_json).expanduser().resolve()
    out_md = Path(args.out_md).expanduser().resolve()

    findings: list[Finding] = []
    notes: list[str] = []
    if not tick_path.is_file():
        findings.append(Finding("error", f"missing tick json: {tick_path}"))
        tick = {}
    else:
        tick = load_tick(tick_path)
        notes.append(f"tick updated: {tick.get('updated_utc', 'unknown')}")

    audit_required_files(findings, notes)
    if tick:
        audit_tick_state(tick, findings, notes)
        audit_handoff_texts(tick, findings, notes)

    write_report(out_md, findings, notes, tick_path)

    errors = [item for item in findings if item.level == "error"]
    for finding in findings:
        stream = sys.stderr if finding.level == "error" else sys.stdout
        print(f"{finding.level.upper()}: {finding.message}", file=stream)
    print(f"gpu_handoff_consistency_audit={'pass' if not errors else 'fail'}")
    print(f"report={out_md}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
