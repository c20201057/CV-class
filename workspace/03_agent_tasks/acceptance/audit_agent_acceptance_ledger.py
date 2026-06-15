#!/usr/bin/env python3
"""Audit the orchestrator's acceptance ledger for subagent work."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


WORKSPACE = Path("/root/data-tmp/workspace")
DEFAULT_LEDGER = WORKSPACE / "03_agent_tasks" / "acceptance" / "agent_acceptance_ledger.md"
DEFAULT_OUT = WORKSPACE / "03_agent_tasks" / "acceptance" / "agent_acceptance_ledger_audit_latest.md"

REQUIRED_REPORT_FILES = [
    WORKSPACE / "03_agent_tasks" / "reports" / "P0_light_b2_c64_impl.md",
    WORKSPACE / "03_agent_tasks" / "reports" / "P0_profile_baseline.md",
    WORKSPACE / "03_agent_tasks" / "reports" / "P0_eval_suite.md",
    WORKSPACE / "03_agent_tasks" / "reports" / "P1_probability_inference.md",
]

REQUIRED_REVIEW_FILES = [
    WORKSPACE / "05_reviews" / "experiment_gap_audit.md",
    WORKSPACE / "05_reviews" / "kd_recovery_config_audit.md",
    WORKSPACE / "05_reviews" / "light_b2_c64_narrative_bridge_review_feynman.md",
    WORKSPACE / "05_reviews" / "paper_baseline_boundary_audit_20260613.md",
    WORKSPACE / "05_reviews" / "paper_evidence_audit_20260613.md",
    WORKSPACE / "05_reviews" / "paper_gate_patch_matrix_review_feynman.md",
    WORKSPACE / "05_reviews" / "subagent_reviews.md",
]

REQUIRED_ARTIFACT_MARKERS = [
    "light_b2_c64_e120_s42_prob_eval_v2",
    "baseline_escnet_b5_clean_prob_e120",
    "b0_external_status_latest.md",
    "b0_status_consistency_audit_latest.md",
    "mobilemamba_t2_external_status_latest.md",
    "mobilemamba_status_consistency_audit_latest.md",
    "sync_mobilemamba_observation_state.py",
    "mobilemamba_observation_sync_latest.md",
    "task_board_consistency_audit_latest.md",
    "audit_task_board_consistency.py",
    "gpu_runtime_state_audit_latest.md",
    "audit_gpu_runtime_state.py",
    "RELEASE_AUDIT_REGISTRY.md",
    "audit_release_audit_registry.py",
    "release_audit_registry_audit_latest.md",
    "paper_delivery_manifest.md",
    "audit_paper_delivery_manifest.py",
    "paper_delivery_manifest_audit_latest.md",
    "paper_gate_patch_matrix.md",
    "gate_result_acceptance_runbook.md",
]

REQUIRED_BOUNDARY_MARKERS = [
    "not enter paper",
    "not enter main table",
    "rejected_for_paper",
    "pending_gate",
    "observation only",
    "Gate 1",
    "Gate 2",
    "Gate 3",
    "Gate 4A",
    "Gate 4B",
    "不进主表",
]

ALLOWED_STATES = {
    "accepted_main_evidence",
    "accepted_tooling",
    "accepted_review",
    "accepted_reference_only",
    "pending_gate",
    "rejected_for_paper",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_table_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    in_ledger = False
    for line in text.splitlines():
        if line.strip() == "## Ledger":
            in_ledger = True
            continue
        if in_ledger and line.startswith("## "):
            break
        if not in_ledger or not line.startswith("|"):
            continue
        if "---" in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and cells[0] != "ID":
            rows.append(cells)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    parser.add_argument("--out_md", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    ledger = Path(args.ledger).expanduser().resolve()
    out_md = Path(args.out_md).expanduser().resolve()
    findings: list[str] = []
    notes: list[str] = []

    if not ledger.is_file():
        findings.append(f"missing acceptance ledger: {ledger}")
        text = ""
    else:
        text = read_text(ledger)

    if text:
        rows = extract_table_rows(text)
        if len(rows) < 15:
            findings.append(f"ledger has too few rows: {len(rows)}")
        ids = [row[0] for row in rows if row]
        duplicate_ids = sorted({item for item in ids if ids.count(item) > 1})
        for item in duplicate_ids:
            findings.append(f"duplicate ledger ID: {item}")

        for row in rows:
            if len(row) != 7:
                findings.append(f"ledger row has {len(row)} columns, expected 7: {row[:2]}")
                continue
            item_id, _agent, artifact, state, evidence, boundary, followup = row
            if not re.fullmatch(r"A[0-9]{2}", item_id):
                findings.append(f"invalid ledger ID format: {item_id}")
            if state not in ALLOWED_STATES:
                findings.append(f"{item_id}: invalid acceptance state `{state}`")
            if not artifact or artifact == "":
                findings.append(f"{item_id}: missing artifact")
            if not evidence or evidence == "":
                findings.append(f"{item_id}: missing evidence checked")
            if not boundary or boundary == "":
                findings.append(f"{item_id}: missing paper boundary")
            if not followup or followup == "":
                findings.append(f"{item_id}: missing follow-up")

        for path in REQUIRED_REPORT_FILES + REQUIRED_REVIEW_FILES:
            if not path.is_file():
                findings.append(f"required report/review file missing: {path}")
                continue
            if path.name not in text:
                findings.append(f"ledger missing required report/review marker: {path.name}")

        for marker in REQUIRED_ARTIFACT_MARKERS:
            if marker not in text:
                findings.append(f"ledger missing artifact marker `{marker}`")

        for marker in REQUIRED_BOUNDARY_MARKERS:
            if marker not in text:
                findings.append(f"ledger missing boundary marker `{marker}`")

        state_counts = {state: 0 for state in sorted(ALLOWED_STATES)}
        for row in rows:
            if len(row) == 7 and row[3] in state_counts:
                state_counts[row[3]] += 1
        notes.extend([f"{state}={count}" for state, count in state_counts.items()])
        notes.append(f"ledger_rows={len(rows)}")

    status = "pass" if not findings else "fail"
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(
        "\n".join(
            [
                "# Agent Acceptance Ledger Audit",
                "",
                f"- Status: `{status}`",
                f"- Ledger: `{ledger}`",
                f"- Findings: {len(findings)}",
                "",
                "## Findings",
                "",
                *([f"- {item}" for item in findings] or ["- none"]),
                "",
                "## Notes",
                "",
                *([f"- {item}" for item in notes] or ["- none"]),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    for finding in findings:
        print(f"ERROR: {finding}", file=sys.stderr)
    print(f"agent_acceptance_ledger_audit={status}")
    print(f"report={out_md}")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
