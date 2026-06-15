#!/usr/bin/env python3
"""Audit route-decision documents against the latest orchestrator tick.

The route decision and finalization gates are the documents most likely to
guide a future agent's judgment. This guard keeps them aligned with the current
B0/MobileMamba/Gate state so stale observation rows do not become strategy.
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
DEFAULT_OUT = WORKSPACE / "00_project" / "route_decision_consistency_audit_latest.md"

TARGETS = [
    WORKSPACE / "00_project" / "goal_completion_matrix.md",
    WORKSPACE / "00_project" / "route_decision.md",
    WORKSPACE / "04_paper" / "drafts" / "finalization_gates.md",
    WORKSPACE / "04_paper" / "drafts" / "paper_submission_readiness.md",
    WORKSPACE / "04_paper" / "drafts" / "paper_submission_packet.md",
    WORKSPACE / "04_paper" / "drafts" / "evidence_index.md",
    WORKSPACE / "03_agent_tasks" / "task_board.md",
]

STRATEGY_TARGETS = [
    WORKSPACE / "00_project" / "goal_completion_matrix.md",
    WORKSPACE / "00_project" / "route_decision.md",
    WORKSPACE / "04_paper" / "drafts" / "finalization_gates.md",
]

EXPECTED_GATES = {
    "Light main result": {"pass"},
    "Gate 1 clean baseline": {"pending", "pass"},
    "Gate 2 KD": {"pending", "pass"},
    "Gate 3 speed": {"pending", "pass"},
    "Gate 4A B0": {"observation_only", "candidate"},
    "Gate 4B MobileMamba": {"observation_only", "candidate"},
}

STALE_MOBILEMAMBA_METRICS = [
    "0.7190",
    "0.5578",
    "0.6139",
    "0.8103",
    "0.0497",
]

FORBIDDEN_DYNAMIC_PATTERNS = [
    (
        "hard-coded MobileMamba live epoch in route/status text",
        re.compile(
            r"(?i)(?:MobileMamba[^\n]*(?:latest|current|refresh|around|tick|最新|当前|刷新|记录到|已到)[^\n]*epoch\s*\d+\s*/\s*120|(?:latest|current|refresh|around|tick|最新|当前|刷新|记录到|已到)[^\n]*MobileMamba[^\n]*epoch\s*\d+\s*/\s*120)"
        ),
    ),
]


@dataclass(frozen=True)
class Finding:
    level: str
    message: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_tick(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def metric_tokens(text: str) -> list[str]:
    return re.findall(r"\d+\.\d+", text)


def token_present(text: str, token: str) -> bool:
    return token in text or (token.startswith("0.") and token[1:] in text)


def contains_any(text: str, needles: list[str]) -> bool:
    lower = text.lower()
    return any(needle.lower() in lower for needle in needles)


def audit_tick(tick: dict, findings: list[Finding], notes: list[str]) -> None:
    gates = tick.get("gates", {})
    for gate, expected in EXPECTED_GATES.items():
        actual = gates.get(gate, {}).get("status")
        if actual not in expected:
            findings.append(Finding("error", f"{gate} status `{actual}` not in {sorted(expected)}"))

    b0 = tick.get("b0", {})
    mobile = tick.get("mobilemamba", {})
    baseline = tick.get("baseline_progress", {})
    training = tick.get("training", {})

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
    else:
        if baseline.get("state") != "paused_waiting_gpu":
            findings.append(Finding("error", f"Gate 1 baseline state is `{baseline.get('state')}`"))
        if "NC4K" in completed:
            findings.append(Finding("error", "Gate 1 lists NC4K complete while gate status is pending"))
    if training.get("b0_running") is True:
        notes.append("B0 external dirty-tree branch is currently running; route text must keep it observation-only.")

    notes.append(f"tick updated: {tick.get('updated_utc', 'unknown')}")
    notes.append(f"B0 latest result: {b0.get('latest_result', 'unknown')}")
    notes.append(f"MobileMamba latest result: {mobile.get('latest_result', 'unknown')}")
    notes.append(f"MobileMamba latest iter: {mobile.get('latest_iter', 'unknown')}")


def audit_required_files(findings: list[Finding], notes: list[str]) -> dict[Path, str]:
    texts: dict[Path, str] = {}
    for path in TARGETS:
        if not path.is_file():
            findings.append(Finding("error", f"missing route target: {path}"))
            continue
        text = read_text(path)
        if not text.strip():
            findings.append(Finding("error", f"empty route target: {path}"))
            continue
        texts[path] = text
        for label, pattern in FORBIDDEN_DYNAMIC_PATTERNS:
            if pattern.search(text):
                findings.append(Finding("error", f"{path}: stale/dangerous wording: {label}"))
        notes.append(f"route target ok: {path}")
    return texts


def audit_strategy_text(tick: dict, texts: dict[Path, str], findings: list[Finding]) -> None:
    b0_result = tick.get("b0", {}).get("latest_result", "")
    mobile_result = tick.get("mobilemamba", {}).get("latest_result", "")

    for path in STRATEGY_TARGETS:
        text = texts.get(path, "")
        if not text:
            continue

        if "MobileMamba" not in text:
            findings.append(Finding("error", f"{path}: missing MobileMamba route boundary"))
        if "B0" not in text:
            findings.append(Finding("error", f"{path}: missing B0 route boundary"))
        if not contains_any(text, ["不偷懒"]):
            findings.append(Finding("error", f"{path}: missing non-lazy principle"))
        if not contains_any(text, ["不保守", "不因为怕风险而保守"]):
            findings.append(Finding("error", f"{path}: missing non-conservative principle"))
        if not contains_any(text, ["不抢占 Gate 1", "不要抢占 Gate 1", "不应抢占 Gate 1", "不阻塞 Gate 2"]):
            findings.append(Finding("error", f"{path}: missing Gate 1/Gate 2 preemption boundary"))
        if not contains_any(text, ["KD"]):
            findings.append(Finding("error", f"{path}: missing KD continuation boundary"))

        missing_b0 = [token for token in metric_tokens(b0_result) if not token_present(text, token)]
        if missing_b0:
            findings.append(
                Finding(
                    "error",
                    f"{path}: missing current B0 metric tokens {missing_b0} from `{b0_result}`",
                )
            )

        missing_mobile = [
            token for token in metric_tokens(mobile_result) if not token_present(text, token)
        ]
        if missing_mobile:
            findings.append(
                Finding(
                    "error",
                    f"{path}: missing current MobileMamba metric tokens "
                    f"{missing_mobile} from `{mobile_result}`",
                )
            )

        if "MobileMamba" in text:
            for stale in STALE_MOBILEMAMBA_METRICS:
                if token_present(text, stale) and not token_present(text, "0.7376"):
                    findings.append(
                        Finding(
                            "error",
                            f"{path}: stale MobileMamba metric `{stale}` appears without current epoch20 row",
                        )
                    )


def audit_cross_file_text(tick: dict, texts: dict[Path, str], findings: list[Finding]) -> None:
    all_text = "\n".join(texts.values())
    mobile_result = tick.get("mobilemamba", {}).get("latest_result", "")
    b0_result = tick.get("b0", {}).get("latest_result", "")

    for token in metric_tokens(mobile_result):
        if not token_present(all_text, token):
            findings.append(Finding("error", f"no route/status document mentions MobileMamba token `{token}`"))
    for token in metric_tokens(b0_result):
        if not token_present(all_text, token):
            findings.append(Finding("error", f"no route/status document mentions B0 token `{token}`"))

    required_markers = [
        "external_dirty_tree_observation_only",
        "clean_prob_re_eval_complete",
        "epoch_5.pth",
        "release_audit_latest.md",
    ]
    if tick.get("gates", {}).get("Gate 1 clean baseline", {}).get("status") == "pass":
        required_markers.append("complete")
    else:
        required_markers.append("paused_waiting_gpu")
    for marker in required_markers:
        if marker not in all_text:
            findings.append(Finding("error", f"route/status docs missing marker `{marker}`"))


def write_report(out_md: Path, findings: list[Finding], notes: list[str], tick_path: Path) -> None:
    errors = [item.message for item in findings if item.level == "error"]
    warnings = [item.message for item in findings if item.level == "warning"]
    status = "pass" if not errors else "fail"
    out_md.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Route Decision Consistency Audit",
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--tick_json", type=Path, default=DEFAULT_TICK)
    parser.add_argument("--out_md", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    findings: list[Finding] = []
    notes: list[str] = []

    if not args.tick_json.is_file():
        findings.append(Finding("error", f"missing tick json: {args.tick_json}"))
        write_report(args.out_md, findings, notes, args.tick_json)
        print(f"route_decision_consistency_audit=fail\nreport={args.out_md}", file=sys.stderr)
        return 1

    tick = load_tick(args.tick_json)
    audit_tick(tick, findings, notes)
    texts = audit_required_files(findings, notes)
    audit_strategy_text(tick, texts, findings)
    audit_cross_file_text(tick, texts, findings)
    write_report(args.out_md, findings, notes, args.tick_json)

    status = "fail" if any(item.level == "error" for item in findings) else "pass"
    stream = sys.stderr if status == "fail" else sys.stdout
    print(f"route_decision_consistency_audit={status}", file=stream)
    print(f"report={args.out_md}", file=stream)
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
