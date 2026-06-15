#!/usr/bin/env python3
"""Audit the goal-completion matrix against the latest orchestrator tick.

The matrix is the guardrail for the long-running user objective. It must make
clear that an interim paper is not the same thing as a fully completed goal
while Gate 1/KD/speed/external-branch validation remain pending.
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
DEFAULT_MATRIX = WORKSPACE / "00_project" / "goal_completion_matrix.md"
DEFAULT_OUT = WORKSPACE / "00_project" / "goal_completion_matrix_audit_latest.md"


EXPECTED_GATE_STATUS = {
    "Light main result": {"pass"},
    "Gate 1 clean baseline": {"pending", "pass"},
    "Gate 2 KD": {"pending", "pass"},
    "Gate 3 speed": {"pending", "pass"},
    "Gate 4A B0": {"observation_only", "candidate"},
    "Gate 4B MobileMamba": {"observation_only", "candidate"},
}

REQUIRED_MARKERS = [
    "当前目标未完成",
    "honest interim",
    "不偷懒",
    "不因为怕风险而保守",
    "不要抢占 Gate 1",
    "CV开题报告.pdf",
    "/root/ESCNet",
    "/root/data-tmp/workspace",
    "MASTER_TARGET_PROMPT.md",
    "audit_prompt_principles.py",
    "agent_acceptance_ledger.md",
    "paper_interim_submission.md",
    "paper_draft.md",
    "run_release_audits.sh",
    "task_board_consistency_audit_latest.md",
    "audit_task_board_consistency.py",
    "gpu_runtime_state_audit_latest.md",
    "audit_gpu_runtime_state.py",
    "RELEASE_AUDIT_REGISTRY.md",
    "audit_release_audit_registry.py",
    "paper_delivery_manifest.md",
    "audit_paper_delivery_manifest.py",
    "orchestrator_tick_latest.md",
    "clean_prob_re_eval_complete",
    "epoch_5.pth",
    "external_dirty_tree_observation_only",
    "Gate 1",
    "Gate 2",
    "Gate 3",
    "Gate 4A",
    "Gate 4B",
]

FORBIDDEN_MARKERS = [
    "当前目标已完成",
    "Status: complete",
    "目标完成：是",
]


@dataclass(frozen=True)
class Finding:
    level: str
    message: str


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def metric_tokens(text: str) -> list[str]:
    return re.findall(r"\d+\.\d+", text)


def token_present(text: str, token: str) -> bool:
    return token in text or (token.startswith("0.") and token[1:] in text)


def contains_casefold(text: str, needle: str) -> bool:
    return needle.casefold() in text.casefold()


def audit_tick(tick: dict, findings: list[Finding], notes: list[str]) -> None:
    gates = tick.get("gates", {})
    for gate, expected in EXPECTED_GATE_STATUS.items():
        actual = gates.get(gate, {}).get("status")
        if actual not in expected:
            findings.append(Finding("error", f"{gate} status `{actual}` not in {sorted(expected)}"))

    baseline = tick.get("baseline_progress", {})
    training = tick.get("training", {})
    mobile = tick.get("mobilemamba", {})
    b0 = tick.get("b0", {})

    gate1_status = gates.get("Gate 1 clean baseline", {}).get("status")
    completed = set(baseline.get("completed_results", []))
    if gate1_status == "pass":
        if baseline.get("state") != "complete":
            findings.append(Finding("error", f"Gate 1 passed but baseline state is `{baseline.get('state')}`"))
        missing = {"CAMO", "COD10K", "NC4K"} - completed
        if missing:
            findings.append(Finding("error", f"Gate 1 passed but completed results miss {sorted(missing)}"))
    else:
        if baseline.get("state") != "paused_waiting_gpu":
            findings.append(Finding("error", f"Gate 1 baseline state is `{baseline.get('state')}`"))
        if "NC4K" in completed:
            findings.append(Finding("error", "Gate 1 NC4K is complete but gate remains pending"))
    if training.get("mobilemamba_t2_running") is not True:
        notes.append("MobileMamba-T2 is not currently running; matrix may need a Gate 1 handoff update.")
    if mobile.get("boundary") != "external_dirty_tree_observation_only":
        findings.append(Finding("error", f"MobileMamba boundary is `{mobile.get('boundary')}`"))
    if b0.get("boundary") != "external_dirty_tree_observation_only":
        findings.append(Finding("error", f"B0 boundary is `{b0.get('boundary')}`"))

    notes.append(f"tick updated: {tick.get('updated_utc', 'unknown')}")
    notes.append(f"B0 latest result: {b0.get('latest_result', 'unknown')}")
    notes.append(f"MobileMamba latest result: {mobile.get('latest_result', 'unknown')}")


def audit_matrix_text(tick: dict, text: str, findings: list[Finding], notes: list[str]) -> None:
    if not text.strip():
        findings.append(Finding("error", "goal completion matrix is empty"))
        return

    for marker in REQUIRED_MARKERS:
        if marker not in text:
            findings.append(Finding("error", f"matrix missing marker `{marker}`"))
    gate1_status = tick.get("gates", {}).get("Gate 1 clean baseline", {}).get("status")
    dynamic_marker = "Gate 1 clean baseline | complete" if gate1_status == "pass" else "paused_waiting_gpu"
    if dynamic_marker not in text:
        findings.append(Finding("error", f"matrix missing marker `{dynamic_marker}`"))

    for marker in FORBIDDEN_MARKERS:
        if contains_casefold(text, marker):
            findings.append(Finding("error", f"matrix contains forbidden completion marker `{marker}`"))

    required_sections = [
        "## Current Verdict",
        "## Objective Coverage",
        "## Current Accepted Evidence",
        "## Completion Blockers",
        "## Final Completion Criteria",
        "## Next Action",
    ]
    for section in required_sections:
        if section not in text:
            findings.append(Finding("error", f"matrix missing section `{section}`"))

    required_requirements = [
        "根据 `CV开题报告.pdf` 推进课题",
        "以 `/root/ESCNet` 为实验基底",
        "以 `/root/data-tmp/workspace` 为后续工作空间",
        "制定工作计划",
        "搭建 workflow",
        "给 subagent 的目标模式 prompt",
        "整合全局信息做路线判断",
        "验收 agent 工作",
        "论文草稿",
        "文献和网络调研支撑",
        "Light 轻量模型实验证据",
        "Clean ESCNet-B5 final baseline",
        "KD 补偿路线",
        "Controlled speed",
        "B0 risk branch",
        "MobileMamba risk branch",
        "最终论文强结论",
    ]
    for requirement in required_requirements:
        if requirement not in text:
            findings.append(Finding("error", f"matrix missing objective row `{requirement}`"))

    mobile_result = tick.get("mobilemamba", {}).get("latest_result", "")
    b0_result = tick.get("b0", {}).get("latest_result", "")
    for token in metric_tokens(mobile_result):
        if not token_present(text, token):
            findings.append(
                Finding(
                    "error",
                    f"matrix missing current MobileMamba token `{token}` from `{mobile_result}`",
                )
            )
    for token in metric_tokens(b0_result):
        if not token_present(text, token):
            findings.append(Finding("error", f"matrix missing current B0 token `{token}` from `{b0_result}`"))

    if "Gate 1 clean baseline is either complete" not in text:
        findings.append(Finding("error", "matrix missing Gate 1 final completion criterion"))
    if "Gate 2 KD is either complete" not in text:
        findings.append(Finding("error", "matrix missing Gate 2 final completion criterion"))
    if "Gate 3 speed is either complete" not in text:
        findings.append(Finding("error", "matrix missing Gate 3 final completion criterion"))

    notes.append("goal completion matrix marker coverage checked")


def write_report(out_md: Path, findings: list[Finding], notes: list[str], tick_path: Path, matrix_path: Path) -> None:
    errors = [finding.message for finding in findings if finding.level == "error"]
    warnings = [finding.message for finding in findings if finding.level == "warning"]
    status = "pass" if not errors else "fail"
    out_md.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Goal Completion Matrix Audit",
        "",
        f"- Status: `{status}`",
        f"- Tick JSON: `{tick_path}`",
        f"- Matrix: `{matrix_path}`",
        f"- Errors: {len(errors)}",
        f"- Warnings: {len(warnings)}",
        "",
        "## Errors",
        "",
        *([f"- {error}" for error in errors] or ["- none"]),
        "",
        "## Warnings",
        "",
        *([f"- {warning}" for warning in warnings] or ["- none"]),
        "",
        "## Notes",
        "",
        *[f"- {note}" for note in notes],
    ]
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tick_json", type=Path, default=DEFAULT_TICK)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--out_md", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    findings: list[Finding] = []
    notes: list[str] = []

    if not args.tick_json.is_file():
        findings.append(Finding("error", f"missing tick json: {args.tick_json}"))
        tick = {}
    else:
        tick = load_json(args.tick_json)

    if not args.matrix.is_file():
        findings.append(Finding("error", f"missing goal completion matrix: {args.matrix}"))
        matrix_text = ""
    else:
        matrix_text = args.matrix.read_text(encoding="utf-8")

    if tick:
        audit_tick(tick, findings, notes)
    if matrix_text:
        audit_matrix_text(tick, matrix_text, findings, notes)

    write_report(args.out_md, findings, notes, args.tick_json, args.matrix)

    errors = [finding for finding in findings if finding.level == "error"]
    status = "fail" if errors else "pass"
    stream = sys.stderr if errors else sys.stdout
    print(f"goal_completion_matrix_audit={status}", file=stream)
    print(f"report={args.out_md}", file=stream)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
