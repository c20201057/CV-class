#!/usr/bin/env python3
"""Audit whether Gate 1/2/3/4A/4B results are ready to patch into the paper.

This check is intentionally read-only. Pending gates are allowed; partial or
malformed evidence is reported as an error because it is exactly the state that
can lead to accidental over-claiming in the manuscript.
"""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path


WORKSPACE = Path("/root/data-tmp/workspace")
DATASETS = {"CAMO", "COD10K", "NC4K"}
DEFAULT_METRICS = WORKSPACE / "02_experiments" / "tables" / "metrics_all.csv"
DEFAULT_PROFILES = WORKSPACE / "02_experiments" / "tables" / "profiles.csv"
DEFAULT_OUT = WORKSPACE / "04_paper" / "drafts" / "gate_patch_readiness_latest.md"
DEFAULT_PATCH_MATRIX = WORKSPACE / "04_paper" / "drafts" / "paper_gate_patch_matrix.md"
DEFAULT_PATCH_PLAN = WORKSPACE / "04_paper" / "drafts" / "paper_final_patch_plan.md"

GATE1_EXP = "baseline_escnet_b5_clean_prob_e120"
GATE1_STATUS = "clean_prob_re_eval_complete"
GATE2_EXP = "kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval"
GATE2_STATUS = "final_main_kd"
B0_STATUS = "external_dirty_tree_observation_candidate"
B0_REPO_BOUNDARY = "external_b0_dirty_snapshot_candidate"
B0_METRIC_RE = re.compile(r"^b0_external_epoch(?P<epoch>\d+)_candidate_prob_eval$")
B0_PROFILE_RE = re.compile(r"^b0_external_epoch(?P<epoch>\d+)_candidate_profile$")
MOBILEMAMBA_STATUS = "external_dirty_tree_observation_candidate"
MOBILEMAMBA_REPO_BOUNDARY = "external_mobilemamba_dirty_snapshot_candidate"
MOBILEMAMBA_METRIC_RE = re.compile(
    r"^mobilemamba_t2_epoch(?P<epoch>\d+)_candidate_prob_eval$"
)
MOBILEMAMBA_PROFILE_RE = re.compile(
    r"^mobilemamba_t2_epoch(?P<epoch>\d+)_candidate_profile$"
)
IDLE_PROFILE_IDS = {
    "baseline_escnet_b5_416_idle",
    "light_b2_c64_trained_416_idle",
    "kd_light_b2_c64_trained_416_idle",
}

PATCH_MATRIX_REQUIRED_MARKERS = {
    "global": [
        "paper_interim_submission.md",
        "paper_claim_evidence_matrix.md",
        "teacher_share_pack.md",
        "presentation_outline.md",
        "paper_submission_packet.md",
        "reproducibility_manifest.md",
    ],
    "Gate 1": [
        "clean ESCNet-B5 probability baseline",
        "paper_interim_submission.md",
        "current_delta_summary.md",
        "paper_claim_evidence_matrix.md",
        "paper_submission_packet.md",
        "reproducibility_manifest.md",
    ],
    "Gate 2": [
        "final_main_kd",
        "paper_interim_submission.md",
        "paper_claim_evidence_matrix.md",
        "teacher_share_pack.md",
        "presentation_outline.md",
        "KD 不改善",
    ],
    "Gate 3": [
        "controlled speed",
        "paper_interim_submission.md",
        "paper_claim_evidence_matrix.md",
        "paper_submission_packet.md",
        "reproducibility_manifest.md",
        "Speed Status",
    ],
    "Gate 4A": [
        "external_dirty_tree_observation_candidate",
        "paper_interim_submission.md",
        "teacher_share_pack.md",
        "presentation_outline.md",
        "paper_claim_evidence_matrix.md",
        "agent_acceptance_ledger.md",
        "audit_b0_status_consistency.py",
        "audit_agent_acceptance_ledger.py",
    ],
    "Gate 4B": [
        "external_dirty_tree_observation_candidate",
        "paper_interim_submission.md",
        "teacher_share_pack.md",
        "presentation_outline.md",
        "paper_claim_evidence_matrix.md",
        "agent_acceptance_ledger.md",
        "audit_mobilemamba_status_consistency.py",
        "audit_agent_acceptance_ledger.py",
    ],
}

PATCH_PLAN_REQUIRED_MARKERS = [
    "Gate 1: Clean ESCNet-B5 Baseline",
    "Gate 2: KD B2-C64",
    "Gate 3: Controlled Speed",
    "Gate 4A: B0 Observation Candidate",
    "Gate 4B: MobileMamba-T2 Observation Candidate",
    "paper_gate_patch_matrix.md",
    "paper_interim_submission.md",
    "teacher_share_pack.md",
    "presentation_outline.md",
    "paper_submission_packet.md",
    "reproducibility_manifest.md",
    "audit_gate_patch_readiness.py",
    "audit_route_decision_consistency.py",
    "audit_gpu_handoff_consistency.py",
    "audit_b0_status_consistency.py",
    "audit_mobilemamba_status_consistency.py",
    "audit_agent_acceptance_ledger.py",
    "run_release_audits.sh",
    "external_dirty_tree_observation_candidate",
    "final_main_kd",
    "clean_prob_re_eval_complete",
]


@dataclass
class GateReport:
    gate: str
    state: str
    evidence: str
    action: str


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def existing_path(value: str) -> bool:
    return bool(value) and Path(value).expanduser().exists()


def rows_for_exp(rows: list[dict[str, str]], exp_id: str) -> list[dict[str, str]]:
    return [row for row in rows if row.get("exp_id") == exp_id]


def profile_by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("exp_id", ""): row for row in rows if row.get("exp_id", "")}


def section_text(text: str, heading: str) -> str:
    pattern = re.compile(rf"^## {re.escape(heading)}(?:\n|:).*?(?=^## |\Z)", re.M | re.S)
    match = pattern.search(text)
    return match.group(0) if match else ""


def audit_patch_matrix_contract(path: Path) -> tuple[GateReport, list[str]]:
    findings: list[str] = []
    if not path.is_file():
        return (
            GateReport(
                "Patch matrix coverage",
                "missing",
                f"matrix missing: {path}",
                "Restore patch matrix before applying any gate result.",
            ),
            [f"Patch matrix coverage: missing file {path}"],
        )

    text = path.read_text(encoding="utf-8")
    for marker in PATCH_MATRIX_REQUIRED_MARKERS["global"]:
        if marker not in text:
            findings.append(f"Patch matrix coverage: missing global marker `{marker}`")

    for gate, markers in PATCH_MATRIX_REQUIRED_MARKERS.items():
        if gate == "global":
            continue
        body = section_text(text, gate)
        if not body:
            findings.append(f"Patch matrix coverage: missing section `{gate}`")
            continue
        for marker in markers:
            if marker not in body:
                findings.append(f"Patch matrix coverage: section `{gate}` missing `{marker}`")

    state = "ready" if not findings else "incomplete"
    action = (
        "Patch matrix covers paper-facing deliverables before gate results are applied."
        if not findings
        else "Expand patch matrix before applying gate results to paper-facing claims."
    )
    evidence = (
        f"matrix={path}, checked_sections="
        + ",".join(key for key in PATCH_MATRIX_REQUIRED_MARKERS if key != "global")
    )
    return GateReport("Patch matrix coverage", state, evidence, action), findings


def audit_patch_plan_contract(path: Path) -> tuple[GateReport, list[str]]:
    findings: list[str] = []
    if not path.is_file():
        return (
            GateReport(
                "Patch plan coverage",
                "missing",
                f"plan missing: {path}",
                "Restore final patch plan before applying any gate result.",
            ),
            [f"Patch plan coverage: missing file {path}"],
        )

    text = path.read_text(encoding="utf-8")
    for marker in PATCH_PLAN_REQUIRED_MARKERS:
        if marker not in text:
            findings.append(f"Patch plan coverage: missing marker `{marker}`")

    state = "ready" if not findings else "incomplete"
    action = (
        "Patch plan covers Gate 1/2/3/4A/4B execution order and audit commands."
        if not findings
        else "Expand patch plan before applying gate results."
    )
    evidence = f"plan={path}, checked_markers={len(PATCH_PLAN_REQUIRED_MARKERS)}"
    return GateReport("Patch plan coverage", state, evidence, action), findings


def audit_metric_gate(
    rows: list[dict[str, str]],
    *,
    gate_name: str,
    exp_id: str,
    final_status: str,
    ready_action: str,
    pending_action: str,
) -> tuple[GateReport, list[str]]:
    findings: list[str] = []
    exp_rows = rows_for_exp(rows, exp_id)
    if not exp_rows:
        return (
            GateReport(gate_name, "pending", "no rows found", pending_action),
            findings,
        )

    datasets = {row.get("dataset", "") for row in exp_rows}
    statuses = {row.get("status", "") for row in exp_rows}
    protocols = {row.get("protocol", "") for row in exp_rows}
    missing = DATASETS - datasets
    extra = datasets - DATASETS

    if missing:
        findings.append(
            f"{gate_name}: {exp_id} has partial rows and misses datasets: {', '.join(sorted(missing))}"
        )
    if extra:
        findings.append(
            f"{gate_name}: {exp_id} has unexpected datasets: {', '.join(sorted(extra))}"
        )
    if statuses != {final_status}:
        findings.append(
            f"{gate_name}: {exp_id} statuses must all be `{final_status}`, found {sorted(statuses)}"
        )
    if protocols != {"prob_map"}:
        findings.append(
            f"{gate_name}: {exp_id} protocols must all be `prob_map`, found {sorted(protocols)}"
        )

    for row in exp_rows:
        row_name = f"{exp_id}/{row.get('dataset', '')}"
        source = row.get("source", "")
        checkpoint = row.get("checkpoint", "")
        if row.get("dataset") in DATASETS and not existing_path(source):
            findings.append(f"{gate_name}: {row_name} source path missing: {source}")
        if row.get("dataset") in DATASETS and not existing_path(checkpoint):
            findings.append(f"{gate_name}: {row_name} checkpoint path missing: {checkpoint}")

    if findings:
        state = "partial_invalid"
        action = "Do not patch paper claims; repair metadata/evidence first."
    elif datasets == DATASETS and statuses == {final_status} and protocols == {"prob_map"}:
        state = "ready_to_patch"
        action = ready_action
    else:
        state = "pending"
        action = pending_action
    evidence = (
        f"rows={len(exp_rows)}, datasets={','.join(sorted(datasets)) or 'none'}, "
        f"statuses={','.join(sorted(statuses)) or 'none'}"
    )
    return GateReport(gate_name, state, evidence, action), findings


def audit_speed_gate(profile_rows: list[dict[str, str]]) -> tuple[GateReport, list[str]]:
    findings: list[str] = []
    profiles = profile_by_id(profile_rows)
    present = IDLE_PROFILE_IDS & set(profiles)
    if not present:
        return (
            GateReport(
                "Gate 3 controlled speed",
                "pending",
                "no idle profile rows found",
                "Keep latency/FPS claims withheld.",
            ),
            findings,
        )

    missing = IDLE_PROFILE_IDS - present
    if missing:
        findings.append(
            "Gate 3 controlled speed: idle profile rows are partial; missing "
            + ", ".join(sorted(missing))
        )

    fields = ["latency_ms", "fps", "device", "img_size", "warmup", "repeat", "profile_json"]
    for exp_id in sorted(present):
        row = profiles[exp_id]
        for field in fields:
            if not row.get(field, ""):
                findings.append(f"Gate 3 controlled speed: {exp_id} missing `{field}`")
        profile_json = row.get("profile_json", "")
        if profile_json and not existing_path(profile_json):
            findings.append(
                f"Gate 3 controlled speed: {exp_id} profile_json path missing: {profile_json}"
            )

    if len(present) == len(IDLE_PROFILE_IDS):
        baseline = profiles["baseline_escnet_b5_416_idle"]
        light = profiles["light_b2_c64_trained_416_idle"]
        kd = profiles["kd_light_b2_c64_trained_416_idle"]
        comparable_fields = ["device", "img_size", "warmup", "repeat"]
        for field in comparable_fields:
            if baseline.get(field, "") != light.get(field, ""):
                findings.append(
                    "Gate 3 controlled speed: baseline/light idle profiles use different "
                    f"{field}: {baseline.get(field, '')} vs {light.get(field, '')}"
                )
            if light.get(field, "") != kd.get(field, ""):
                findings.append(
                    "Gate 3 controlled speed: light/KD idle profiles use different "
                    f"{field}: {light.get(field, '')} vs {kd.get(field, '')}"
                )

    if findings:
        return (
            GateReport(
                "Gate 3 controlled speed",
                "partial_invalid",
                f"present idle profiles={','.join(sorted(present))}",
                "Do not patch latency/FPS claims; repair profile metadata/evidence first.",
            ),
            findings,
        )
    return (
        GateReport(
            "Gate 3 controlled speed",
            "ready_to_patch",
            f"present idle profiles={','.join(sorted(present))}",
            "Patch controlled speed table; only claim speedup if numbers support it.",
        ),
        findings,
    )


def b0_epoch_from_metric_exp(exp_id: str) -> str | None:
    match = B0_METRIC_RE.match(exp_id)
    return match.group("epoch") if match else None


def b0_epoch_from_profile_exp(exp_id: str) -> str | None:
    match = B0_PROFILE_RE.match(exp_id)
    return match.group("epoch") if match else None


def mobilemamba_epoch_from_metric_exp(exp_id: str) -> str | None:
    match = MOBILEMAMBA_METRIC_RE.match(exp_id)
    return match.group("epoch") if match else None


def mobilemamba_epoch_from_profile_exp(exp_id: str) -> str | None:
    match = MOBILEMAMBA_PROFILE_RE.match(exp_id)
    return match.group("epoch") if match else None


def audit_b0_gate(
    metric_rows: list[dict[str, str]], profile_rows: list[dict[str, str]]
) -> tuple[GateReport, list[str]]:
    findings: list[str] = []
    profiles = profile_by_id(profile_rows)
    metric_exp_ids = sorted(
        {
            row.get("exp_id", "")
            for row in metric_rows
            if b0_epoch_from_metric_exp(row.get("exp_id", "")) is not None
        }
    )
    profile_epochs = {
        epoch: exp_id
        for exp_id in profiles
        for epoch in [b0_epoch_from_profile_exp(exp_id)]
        if epoch is not None
    }

    if not metric_exp_ids and not profile_epochs:
        return (
            GateReport(
                "Gate 4A B0 observation candidate",
                "pending",
                "no candidate rows or profiles found",
                "Keep B0 as dirty-tree observation only.",
            ),
            findings,
        )

    ready_metric_exp_ids: list[str] = []
    metric_epochs: set[str] = set()
    for exp_id in metric_exp_ids:
        epoch = b0_epoch_from_metric_exp(exp_id)
        if epoch is None:
            findings.append(f"Gate 4A B0: candidate metric exp_id has unexpected format: {exp_id}")
            continue
        metric_epochs.add(epoch)
        exp_rows = rows_for_exp(metric_rows, exp_id)
        datasets = {row.get("dataset", "") for row in exp_rows}
        statuses = {row.get("status", "") for row in exp_rows}
        protocols = {row.get("protocol", "") for row in exp_rows}
        repo_boundaries = {row.get("repo_boundary", "") for row in exp_rows}
        missing = DATASETS - datasets
        extra = datasets - DATASETS

        if missing:
            findings.append(
                f"Gate 4A B0: {exp_id} has partial rows and misses datasets: "
                + ", ".join(sorted(missing))
            )
        if extra:
            findings.append(
                f"Gate 4A B0: {exp_id} has unexpected datasets: {', '.join(sorted(extra))}"
            )
        if statuses != {B0_STATUS}:
            findings.append(
                f"Gate 4A B0: {exp_id} statuses must all be `{B0_STATUS}`, found {sorted(statuses)}"
            )
        if protocols != {"prob_map"}:
            findings.append(
                f"Gate 4A B0: {exp_id} protocols must all be `prob_map`, found {sorted(protocols)}"
            )
        if repo_boundaries != {B0_REPO_BOUNDARY}:
            findings.append(
                f"Gate 4A B0: {exp_id} repo_boundary must be `{B0_REPO_BOUNDARY}`, "
                f"found {sorted(repo_boundaries)}"
            )
        for row in exp_rows:
            row_name = f"{exp_id}/{row.get('dataset', '')}"
            source = row.get("source", "")
            checkpoint = row.get("checkpoint", "")
            if row.get("dataset") in DATASETS and not existing_path(source):
                findings.append(f"Gate 4A B0: {row_name} source path missing: {source}")
            if row.get("dataset") in DATASETS and not existing_path(checkpoint):
                findings.append(f"Gate 4A B0: {row_name} checkpoint path missing: {checkpoint}")

        profile_exp_id = f"b0_external_epoch{epoch}_candidate_profile"
        profile = profiles.get(profile_exp_id)
        if profile is None:
            findings.append(f"Gate 4A B0: {exp_id} missing paired profile row `{profile_exp_id}`")
        else:
            for field in ["params", "gmacs", "peak_mem_mb", "checkpoint_status", "profile_json"]:
                if not profile.get(field, ""):
                    findings.append(f"Gate 4A B0: {profile_exp_id} missing `{field}`")
            if profile.get("checkpoint_status", "") != "loaded":
                findings.append(
                    f"Gate 4A B0: {profile_exp_id} checkpoint_status must be `loaded`, "
                    f"found `{profile.get('checkpoint_status', '')}`"
                )
            profile_json = profile.get("profile_json", "")
            if profile_json and not existing_path(profile_json):
                findings.append(
                    f"Gate 4A B0: {profile_exp_id} profile_json path missing: {profile_json}"
                )

        if (
            not missing
            and not extra
            and statuses == {B0_STATUS}
            and protocols == {"prob_map"}
            and repo_boundaries == {B0_REPO_BOUNDARY}
            and profile is not None
        ):
            ready_metric_exp_ids.append(exp_id)

    profile_only_epochs = sorted(set(profile_epochs) - metric_epochs)
    for epoch in profile_only_epochs:
        findings.append(
            "Gate 4A B0: profile exists without paired three-dataset candidate metrics: "
            f"{profile_epochs[epoch]}"
        )

    if findings:
        return (
            GateReport(
                "Gate 4A B0 observation candidate",
                "partial_invalid",
                f"metric candidates={','.join(metric_exp_ids) or 'none'}, "
                f"profile epochs={','.join(sorted(profile_epochs)) or 'none'}",
                "Do not patch B0 into paper-facing claims; repair candidate evidence first.",
            ),
            findings,
        )

    return (
        GateReport(
            "Gate 4A B0 observation candidate",
            "ready_to_patch",
            f"metric candidates={','.join(ready_metric_exp_ids)}",
            "Patch only appendix/failure-analysis notes; keep B0 out of main table, abstract and conclusion.",
        ),
        findings,
    )


def audit_mobilemamba_gate(
    metric_rows: list[dict[str, str]], profile_rows: list[dict[str, str]]
) -> tuple[GateReport, list[str]]:
    findings: list[str] = []
    profiles = profile_by_id(profile_rows)
    metric_exp_ids = sorted(
        {
            row.get("exp_id", "")
            for row in metric_rows
            if mobilemamba_epoch_from_metric_exp(row.get("exp_id", "")) is not None
        }
    )
    profile_epochs = {
        epoch: exp_id
        for exp_id in profiles
        for epoch in [mobilemamba_epoch_from_profile_exp(exp_id)]
        if epoch is not None
    }

    if not metric_exp_ids and not profile_epochs:
        return (
            GateReport(
                "Gate 4B MobileMamba observation candidate",
                "pending",
                "no candidate rows or profiles found",
                "Keep MobileMamba-T2 as dirty-tree observation only.",
            ),
            findings,
        )

    ready_metric_exp_ids: list[str] = []
    metric_epochs: set[str] = set()
    for exp_id in metric_exp_ids:
        epoch = mobilemamba_epoch_from_metric_exp(exp_id)
        if epoch is None:
            findings.append(
                f"Gate 4B MobileMamba: candidate metric exp_id has unexpected format: {exp_id}"
            )
            continue
        metric_epochs.add(epoch)
        exp_rows = rows_for_exp(metric_rows, exp_id)
        datasets = {row.get("dataset", "") for row in exp_rows}
        statuses = {row.get("status", "") for row in exp_rows}
        protocols = {row.get("protocol", "") for row in exp_rows}
        repo_boundaries = {row.get("repo_boundary", "") for row in exp_rows}
        missing = DATASETS - datasets
        extra = datasets - DATASETS

        if missing:
            findings.append(
                f"Gate 4B MobileMamba: {exp_id} has partial rows and misses datasets: "
                + ", ".join(sorted(missing))
            )
        if extra:
            findings.append(
                f"Gate 4B MobileMamba: {exp_id} has unexpected datasets: "
                + ", ".join(sorted(extra))
            )
        if statuses != {MOBILEMAMBA_STATUS}:
            findings.append(
                f"Gate 4B MobileMamba: {exp_id} statuses must all be "
                f"`{MOBILEMAMBA_STATUS}`, found {sorted(statuses)}"
            )
        if protocols != {"prob_map"}:
            findings.append(
                f"Gate 4B MobileMamba: {exp_id} protocols must all be `prob_map`, "
                f"found {sorted(protocols)}"
            )
        if repo_boundaries != {MOBILEMAMBA_REPO_BOUNDARY}:
            findings.append(
                f"Gate 4B MobileMamba: {exp_id} repo_boundary must be "
                f"`{MOBILEMAMBA_REPO_BOUNDARY}`, found {sorted(repo_boundaries)}"
            )
        for row in exp_rows:
            row_name = f"{exp_id}/{row.get('dataset', '')}"
            source = row.get("source", "")
            checkpoint = row.get("checkpoint", "")
            if row.get("dataset") in DATASETS and not existing_path(source):
                findings.append(
                    f"Gate 4B MobileMamba: {row_name} source path missing: {source}"
                )
            if row.get("dataset") in DATASETS and not existing_path(checkpoint):
                findings.append(
                    f"Gate 4B MobileMamba: {row_name} checkpoint path missing: {checkpoint}"
                )

        profile_exp_id = f"mobilemamba_t2_epoch{epoch}_candidate_profile"
        profile = profiles.get(profile_exp_id)
        if profile is None:
            findings.append(
                f"Gate 4B MobileMamba: {exp_id} missing paired profile row `{profile_exp_id}`"
            )
        else:
            for field in ["params", "gmacs", "peak_mem_mb", "checkpoint_status", "profile_json"]:
                if not profile.get(field, ""):
                    findings.append(f"Gate 4B MobileMamba: {profile_exp_id} missing `{field}`")
            if profile.get("checkpoint_status", "") != "loaded":
                findings.append(
                    f"Gate 4B MobileMamba: {profile_exp_id} checkpoint_status must be "
                    f"`loaded`, found `{profile.get('checkpoint_status', '')}`"
                )
            profile_json = profile.get("profile_json", "")
            if profile_json and not existing_path(profile_json):
                findings.append(
                    f"Gate 4B MobileMamba: {profile_exp_id} profile_json path missing: "
                    f"{profile_json}"
                )

        if (
            not missing
            and not extra
            and statuses == {MOBILEMAMBA_STATUS}
            and protocols == {"prob_map"}
            and repo_boundaries == {MOBILEMAMBA_REPO_BOUNDARY}
            and profile is not None
        ):
            ready_metric_exp_ids.append(exp_id)

    profile_only_epochs = sorted(set(profile_epochs) - metric_epochs)
    for epoch in profile_only_epochs:
        findings.append(
            "Gate 4B MobileMamba: profile exists without paired three-dataset "
            f"candidate metrics: {profile_epochs[epoch]}"
        )

    if findings:
        return (
            GateReport(
                "Gate 4B MobileMamba observation candidate",
                "partial_invalid",
                f"metric candidates={','.join(metric_exp_ids) or 'none'}, "
                f"profile epochs={','.join(sorted(profile_epochs)) or 'none'}",
                "Do not patch MobileMamba into paper-facing claims; repair candidate evidence first.",
            ),
            findings,
        )

    return (
        GateReport(
            "Gate 4B MobileMamba observation candidate",
            "ready_to_patch",
            f"metric candidates={','.join(ready_metric_exp_ids)}",
            "Patch only appendix/failure-analysis notes; keep MobileMamba out of main table, abstract and conclusion.",
        ),
        findings,
    )


def write_report(
    out_md: Path,
    reports: list[GateReport],
    findings: list[str],
    patch_matrix: Path,
    patch_plan: Path,
) -> None:
    out_md.parent.mkdir(parents=True, exist_ok=True)
    status = "pass" if not findings else "fail"
    lines = [
        "# Gate Patch Readiness Audit",
        "",
        f"- Status: `{status}`",
        f"- Findings: {len(findings)}",
        f"- Patch matrix: `{patch_matrix}`",
        f"- Patch plan: `{patch_plan}`",
        "",
        "## Gate Readiness",
        "",
        "| Gate | State | Evidence | Required Paper Action |",
        "| --- | --- | --- | --- |",
    ]
    for report in reports:
        lines.append(
            f"| {report.gate} | {report.state} | {report.evidence} | {report.action} |"
        )
    lines.extend(["", "## Findings", ""])
    lines.extend([f"- {item}" for item in findings] or ["- none"])
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `pending` is acceptable and means the manuscript must keep the current evidence boundary.",
            "- `ready_to_patch` means the corresponding section of `paper_gate_patch_matrix.md` can be applied.",
            "- `partial_invalid` is unsafe: do not patch claims until metadata and integrity evidence are repaired.",
        ]
    )
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics_csv", default=str(DEFAULT_METRICS))
    parser.add_argument("--profiles_csv", default=str(DEFAULT_PROFILES))
    parser.add_argument("--patch_matrix", default=str(DEFAULT_PATCH_MATRIX))
    parser.add_argument("--patch_plan", default=str(DEFAULT_PATCH_PLAN))
    parser.add_argument("--out_md", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    metrics_csv = Path(args.metrics_csv).expanduser().resolve()
    profiles_csv = Path(args.profiles_csv).expanduser().resolve()
    patch_matrix = Path(args.patch_matrix).expanduser().resolve()
    patch_plan = Path(args.patch_plan).expanduser().resolve()
    out_md = Path(args.out_md).expanduser().resolve()

    metric_rows = read_csv(metrics_csv)
    profile_rows = read_csv(profiles_csv)
    reports: list[GateReport] = []
    findings: list[str] = []

    patch_report, patch_findings = audit_patch_matrix_contract(patch_matrix)
    reports.append(patch_report)
    findings.extend(patch_findings)

    patch_plan_report, patch_plan_findings = audit_patch_plan_contract(patch_plan)
    reports.append(patch_plan_report)
    findings.extend(patch_plan_findings)

    gate1, gate1_findings = audit_metric_gate(
        metric_rows,
        gate_name="Gate 1 clean baseline",
        exp_id=GATE1_EXP,
        final_status=GATE1_STATUS,
        ready_action="Apply Gate 1 patch matrix and promote clean baseline deltas.",
        pending_action="Keep ESCNet-B5 as historical/reference only.",
    )
    reports.append(gate1)
    findings.extend(gate1_findings)

    gate2, gate2_findings = audit_metric_gate(
        metric_rows,
        gate_name="Gate 2 KD",
        exp_id=GATE2_EXP,
        final_status=GATE2_STATUS,
        ready_action="Apply Gate 2 patch matrix according to measured KD result.",
        pending_action="Keep KD as engineering route only, with no improvement claim.",
    )
    reports.append(gate2)
    findings.extend(gate2_findings)

    gate3, gate3_findings = audit_speed_gate(profile_rows)
    reports.append(gate3)
    findings.extend(gate3_findings)

    gate4, gate4_findings = audit_b0_gate(metric_rows, profile_rows)
    reports.append(gate4)
    findings.extend(gate4_findings)

    mobilemamba_gate, mobilemamba_findings = audit_mobilemamba_gate(metric_rows, profile_rows)
    reports.append(mobilemamba_gate)
    findings.extend(mobilemamba_findings)

    write_report(out_md, reports, findings, patch_matrix, patch_plan)
    for finding in findings:
        print(f"ERROR: {finding}")
    print(f"gate_patch_readiness_audit={'pass' if not findings else 'fail'}")
    print(f"report={out_md}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
