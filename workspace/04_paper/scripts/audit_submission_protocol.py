#!/usr/bin/env python3
"""Audit the final-submission protocol boundary for the COD paper package."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


WORKSPACE = Path("/root/data-tmp/workspace")
DEFAULT_METRICS = WORKSPACE / "02_experiments" / "tables" / "metrics_all.csv"
DEFAULT_PROFILES = WORKSPACE / "02_experiments" / "tables" / "profiles.csv"
DEFAULT_OUT = WORKSPACE / "04_paper" / "drafts" / "submission_protocol_audit_latest.md"

REQUIRED_DATASETS = {"CAMO", "COD10K", "NC4K"}
FINAL_STATUSES = {"final_main_light", "clean_prob_re_eval_complete", "final_main_kd"}
REFERENCE_STATUSES = {
    "historical_reference_not_clean_prob_final",
    "verification_only_camo",
    "external_dirty_tree_observation_candidate",
}
FORBIDDEN_FINAL_BOUNDARIES = {"dirty_history_result", "legacy_repo_camo_verification"}
FORBIDDEN_TEACHER_PATH = "/root/ESCNet/checkpoints/escnet/epoch_120.pth"
FIXED_TEACHER_PATH = "/root/data-tmp/epoch_120.pth"
LIGHT_EXP_ID = "light_b2_c64_e120_s42_prob_eval_v2"
LIGHT_PROFILE_IDS = {"light_b2_c64_trained_416", "light_b2_c64_pretrain_416"}
CLEAN_BASELINE_EXP_ID = "baseline_escnet_b5_clean_prob_e120"
B0_BOUNDARY_HINTS = [
    "observation",
    "dirty",
    "not",
    "不能",
    "不得",
    "不纳入",
    "不进入",
    "尚未",
    "no accepted",
    "外部",
    "观察",
]
INTERIM_CONFIG_PHRASES = [
    "随机种子设为 42",
    "每卡 batch size 为 4",
    "验证 batch size 为 8",
    "7.5e-5",
    "1.5e-4",
    "随机翻转",
    "旋转",
    "椒盐噪声",
    "随机裁剪",
]

INTERIM_OBSERVATION_NOISE_PATTERNS = [
    re.compile(r"epoch10 COD10K", re.I),
    re.compile(r"epoch100"),
    re.compile(r"epoch120 metrics"),
    re.compile(r"S=\.8004"),
    re.compile(r"S=\.7190"),
    re.compile(r"wF=\.6862"),
    re.compile(r"wF=\.5578"),
]

REQUIRED_ARTIFACTS = [
    WORKSPACE / "04_paper" / "drafts" / "paper_draft.md",
    WORKSPACE / "04_paper" / "drafts" / "paper_interim_submission.md",
    WORKSPACE / "04_paper" / "drafts" / "teacher_share_pack.md",
    WORKSPACE / "04_paper" / "drafts" / "presentation_outline.md",
    WORKSPACE / "04_paper" / "drafts" / "paper_claim_evidence_matrix.md",
    WORKSPACE / "04_paper" / "drafts" / "paper_submission_packet.md",
    WORKSPACE / "04_paper" / "drafts" / "paper_delivery_manifest.md",
    WORKSPACE / "04_paper" / "drafts" / "paper_delivery_manifest_audit_latest.md",
    WORKSPACE / "04_paper" / "drafts" / "submission_protocol_checklist.md",
    WORKSPACE / "04_paper" / "drafts" / "paper_submission_readiness.md",
    WORKSPACE / "04_paper" / "drafts" / "current_delta_summary.md",
    WORKSPACE / "04_paper" / "drafts" / "reproducibility_manifest.md",
    WORKSPACE / "04_paper" / "drafts" / "b0_status_consistency_audit_latest.md",
    WORKSPACE / "04_paper" / "drafts" / "mobilemamba_status_consistency_audit_latest.md",
    WORKSPACE / "03_agent_tasks" / "task_board.md",
    WORKSPACE / "03_agent_tasks" / "audit_task_board_consistency.py",
    WORKSPACE / "03_agent_tasks" / "task_board_consistency_audit_latest.md",
    WORKSPACE / "03_agent_tasks" / "acceptance" / "agent_acceptance_ledger.md",
    WORKSPACE / "03_agent_tasks" / "acceptance" / "agent_acceptance_ledger_audit_latest.md",
    WORKSPACE / "04_paper" / "tables" / "main_results_template.md",
    WORKSPACE / "04_paper" / "tables" / "aggregated_results.md",
    WORKSPACE / "02_experiments" / "code" / "baseline_escnet_clean" / "BASELINE_SOURCE.md",
    Path(FIXED_TEACHER_PATH),
    WORKSPACE / "02_experiments" / "runs" / "light_b2_c64_e120_s42" / "epoch_120.pth",
]

SUBMISSION_CHECKLIST_REQUIRED_MARKERS = [
    "external_dirty_tree_observation_candidate",
    "audit_b0_status_consistency.py",
    "audit_mobilemamba_status_consistency.py",
    "audit_agent_acceptance_ledger.py",
    "audit_task_board_consistency.py",
    "audit_paper_delivery_manifest.py",
    "paper_delivery_manifest.md",
    "paper_delivery_manifest_audit_latest.md",
    "task_board_consistency_audit_latest.md",
    "03_agent_tasks/task_board.md",
    "agent_acceptance_ledger.md",
    "MobileMamba-T2 的 intermediate epoch metrics",
    "附录探索、工程观察或失败分析",
]

PAPER_TARGETS = [
    WORKSPACE / "04_paper" / "drafts" / "paper_draft.md",
    WORKSPACE / "04_paper" / "drafts" / "paper_interim_submission.md",
    WORKSPACE / "04_paper" / "drafts" / "teacher_share_pack.md",
    WORKSPACE / "04_paper" / "drafts" / "presentation_outline.md",
    WORKSPACE / "04_paper" / "tables" / "main_results_template.md",
    WORKSPACE / "04_paper" / "tables" / "aggregated_results.md",
]

PUBLIC_STYLE_TARGETS = [
    WORKSPACE / "04_paper" / "drafts" / "paper_draft.md",
    WORKSPACE / "04_paper" / "drafts" / "paper_interim_submission.md",
    WORKSPACE / "04_paper" / "drafts" / "teacher_share_pack.md",
    WORKSPACE / "04_paper" / "drafts" / "presentation_outline.md",
]

PUBLIC_STYLE_FORBIDDEN_PATTERNS = [
    ("gate jargon", re.compile(r"\bGate\b|\bgate\b")),
    ("dirty-tree jargon", re.compile(r"dirty(?:-tree)?|dirty 工作树", re.I)),
    (
        "internal evidence-table jargon",
        re.compile(r"\bmetadata\b|入表|repo boundary|evidence status|result files", re.I),
    ),
    (
        "internal process jargon",
        re.compile(r"\bsmoke\b|\bwatcher\b|\borchestrator\b|\btick\b|\brunbook\b", re.I),
    ),
    (
        "status-file phrasing",
        re.compile(r"\bpending\b|\bobservation only\b|\bsnapshot\b|\bprofiling\b|\bprofile\b", re.I),
    ),
    (
        "local absolute path",
        re.compile(r"/root/|data-tmp|workspace"),
    ),
    (
        "script or internal table name",
        re.compile(
            r"\b[a-zA-Z0-9_]+\.py\b|\b[a-zA-Z0-9_]+\.sh\b|metrics_all\.csv|profiles\.csv",
            re.I,
        ),
    ),
    (
        "internal checkpoint/status token",
        re.compile(r"epoch_[0-9]+\.pth|status=|git HEAD|SIGKILL|DataLoader|rank0|num_workers", re.I),
    ),
    (
        "english evidence-status label",
        re.compile(
            r"historical reference|probability eval complete|current main result|"
            r"integrity passed|clean full probability re-eval|final clean baseline|"
            r"clean same-protocol baseline|teacher soft prediction|Idle-GPU speed retest",
            re.I,
        ),
    ),
]


@dataclass(frozen=True)
class Finding:
    level: str
    message: str


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.is_file():
        return [], []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), [dict(row) for row in reader]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def clean_baseline_complete(metrics_csv: Path = DEFAULT_METRICS) -> bool:
    _columns, rows = read_csv(metrics_csv)
    datasets = {
        row.get("dataset", "")
        for row in rows
        if row.get("exp_id") == CLEAN_BASELINE_EXP_ID
        and row.get("status") == "clean_prob_re_eval_complete"
    }
    return REQUIRED_DATASETS.issubset(datasets)


def row_id(row: dict[str, str]) -> str:
    return f"{row.get('exp_id', '')}/{row.get('dataset', '')}/{row.get('method', '')}"


def path_exists(value: str) -> bool:
    return bool(value) and Path(value).expanduser().exists()


def is_b0_exp(exp_id: str) -> bool:
    return bool(re.search(r"(?:^|[_-])(b0|pvt_v2_b0)(?:$|[_-])", exp_id.lower()))


def allowed_final_checkpoint(value: str) -> bool:
    return value == FIXED_TEACHER_PATH or value.startswith(str(WORKSPACE) + "/")


def has_boundary_hint(text: str) -> bool:
    lower = text.lower()
    return any(hint.lower() in lower for hint in B0_BOUNDARY_HINTS)


def audit_required_artifacts(
    metrics_csv: Path,
    profiles_csv: Path,
    findings: list[Finding],
    notes: list[str],
) -> None:
    artifacts = [metrics_csv, profiles_csv, *REQUIRED_ARTIFACTS]
    for artifact in artifacts:
        if not artifact.exists():
            findings.append(Finding("error", f"missing required artifact: {artifact}"))
        elif artifact.is_file() and artifact.stat().st_size == 0:
            findings.append(Finding("error", f"empty required artifact: {artifact}"))
        else:
            notes.append(f"artifact ok: {artifact}")

    checklist = WORKSPACE / "04_paper" / "drafts" / "submission_protocol_checklist.md"
    if checklist.is_file():
        checklist_text = read_text(checklist)
        for marker in SUBMISSION_CHECKLIST_REQUIRED_MARKERS:
            if marker not in checklist_text:
                findings.append(
                    Finding(
                        "error",
                        f"submission protocol checklist missing marker `{marker}`",
                    )
                )


def audit_metrics(metrics_csv: Path, findings: list[Finding], notes: list[str]) -> None:
    required_columns = [
        "exp_id",
        "dataset",
        "method",
        "Smeasure",
        "wFmeasure",
        "meanFm",
        "meanEm",
        "MAE",
        "source",
        "protocol",
        "repo_boundary",
        "checkpoint",
        "status",
    ]
    columns, rows = read_csv(metrics_csv)
    missing = [column for column in required_columns if column not in columns]
    if missing:
        findings.append(Finding("error", f"metrics CSV missing columns: {', '.join(missing)}"))
        return

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row.get("exp_id", "")].append(row)
        status = row.get("status", "")
        exp_id = row.get("exp_id", "")
        checkpoint = row.get("checkpoint", "")
        repo_boundary = row.get("repo_boundary", "")
        protocol = row.get("protocol", "")

        if status in FINAL_STATUSES:
            if protocol != "prob_map":
                findings.append(
                    Finding("error", f"{row_id(row)} final row uses protocol `{protocol}`")
                )
            if repo_boundary in FORBIDDEN_FINAL_BOUNDARIES:
                findings.append(
                    Finding(
                        "error",
                        f"{row_id(row)} final row uses forbidden boundary `{repo_boundary}`",
                    )
                )
            if not allowed_final_checkpoint(checkpoint):
                findings.append(
                    Finding("error", f"{row_id(row)} final checkpoint outside evidence root")
                )
            if not path_exists(row.get("source", "")):
                findings.append(Finding("error", f"{row_id(row)} final source is missing"))
            if not path_exists(checkpoint):
                findings.append(Finding("error", f"{row_id(row)} final checkpoint is missing"))
            if is_b0_exp(exp_id):
                findings.append(Finding("error", f"{row_id(row)} B0 branch marked final"))
        elif status in REFERENCE_STATUSES:
            notes.append(f"reference-only metrics row: {row_id(row)} status={status}")

        if checkpoint == FORBIDDEN_TEACHER_PATH:
            findings.append(Finding("error", f"{row_id(row)} uses forbidden teacher path"))

    if LIGHT_EXP_ID not in grouped:
        findings.append(Finding("error", f"missing final Light metrics exp_id: {LIGHT_EXP_ID}"))
    else:
        light_rows = grouped[LIGHT_EXP_ID]
        light_datasets = {row.get("dataset", "") for row in light_rows}
        light_statuses = {row.get("status", "") for row in light_rows}
        if light_datasets != REQUIRED_DATASETS:
            findings.append(
                Finding(
                    "error",
                    f"Light final metrics datasets are {sorted(light_datasets)}, expected {sorted(REQUIRED_DATASETS)}",
                )
            )
        if light_statuses != {"final_main_light"}:
            findings.append(
                Finding("error", f"Light final metrics statuses are {sorted(light_statuses)}")
            )

    for exp_id, exp_rows in grouped.items():
        statuses = {row.get("status", "") for row in exp_rows}
        if statuses & FINAL_STATUSES:
            datasets = {row.get("dataset", "") for row in exp_rows}
            if not REQUIRED_DATASETS.issubset(datasets):
                findings.append(
                    Finding(
                        "error",
                        f"{exp_id} has final status but misses datasets {sorted(REQUIRED_DATASETS - datasets)}",
                    )
                )


def audit_profiles(profiles_csv: Path, findings: list[Finding], notes: list[str]) -> None:
    columns, rows = read_csv(profiles_csv)
    if not rows:
        findings.append(Finding("error", f"profiles CSV has no rows: {profiles_csv}"))
        return
    required = {"exp_id", "params", "gmacs", "model_size_mb", "peak_mem_mb", "profile_json"}
    missing = sorted(required - set(columns))
    if missing:
        findings.append(Finding("error", f"profiles CSV missing columns: {', '.join(missing)}"))
        return

    exp_ids = {row.get("exp_id", "") for row in rows}
    if "baseline_escnet_b5_416_e120" not in exp_ids:
        findings.append(Finding("error", "missing baseline structural profile row"))
    if not (exp_ids & LIGHT_PROFILE_IDS):
        findings.append(Finding("error", "missing Light-B2-C64 structural profile row"))

    for row in rows:
        profile_json = row.get("profile_json", "")
        if profile_json and not path_exists(profile_json):
            findings.append(
                Finding("error", f"profile json missing for {row.get('exp_id', '')}: {profile_json}")
            )
    notes.append(f"profile rows: {len(rows)}")


def audit_paper_text(findings: list[Finding], notes: list[str]) -> None:
    forbidden_path_pattern = re.compile(re.escape(FORBIDDEN_TEACHER_PATH))
    safe_context = re.compile(r"(不|not|cannot|不得|不能|不要|forbidden|legacy|后续|不混入)")
    speed_claim = re.compile(
        r"(FPS|latency|延迟|速度).*(提升|加速|speedup|faster|降低)|实测.*(FPS|latency|延迟)",
        re.I,
    )
    b0_terms = re.compile(r"(B0|PVTv2-B0|Tiny-ESCNet)")

    for target in PAPER_TARGETS:
        if not target.is_file():
            findings.append(Finding("error", f"paper target missing: {target}"))
            continue
        text = read_text(target)
        for lineno, line in enumerate(text.splitlines(), start=1):
            if forbidden_path_pattern.search(line) and not safe_context.search(line):
                findings.append(
                    Finding(
                        "error",
                        f"{target}:{lineno} unsafe forbidden teacher path mention: {line.strip()}",
                    )
                )
            if speed_claim.search(line) and not re.search(
                r"(pending|withheld|不能|不得|未|待|不写|不说|不作|不作为|只写结构效率|只使用结构|not)",
                line,
                re.I,
            ):
                findings.append(
                    Finding("error", f"{target}:{lineno} unsafe final speed claim: {line.strip()}")
                )

        if b0_terms.search(text):
            if not has_boundary_hint(text):
                findings.append(
                    Finding("error", f"{target} mentions B0/Tiny without an observation boundary")
                )
            notes.append(f"B0 boundary mentioned in: {target}")

    for target in PUBLIC_STYLE_TARGETS:
        if not target.is_file():
            findings.append(Finding("error", f"public-facing target missing: {target}"))
            continue
        text = read_text(target)
        for lineno, line in enumerate(text.splitlines(), start=1):
            for label, pattern in PUBLIC_STYLE_FORBIDDEN_PATTERNS:
                if pattern.search(line):
                    findings.append(
                        Finding(
                            "error",
                            f"{target}:{lineno} public-facing {label}: {line.strip()}",
                        )
                    )
        notes.append(f"public-facing style checked: {target}")

    interim = WORKSPACE / "04_paper" / "drafts" / "paper_interim_submission.md"
    if interim.is_file():
        interim_text = read_text(interim)
        for phrase in INTERIM_CONFIG_PHRASES:
            if phrase not in interim_text:
                findings.append(
                    Finding("error", f"interim paper missing implementation detail phrase: {phrase}")
                )
        for pattern in INTERIM_OBSERVATION_NOISE_PATTERNS:
            if pattern.search(interim_text):
                findings.append(
                    Finding(
                        "error",
                        "interim paper contains detailed dirty-tree observation metrics "
                        f"that should stay in status files: `{pattern.pattern}`",
                    )
                )

    main_table = WORKSPACE / "04_paper" / "tables" / "main_results_template.md"
    if main_table.is_file():
        table_text = read_text(main_table)
        if "final_main_light" not in table_text:
            findings.append(Finding("error", "main results template missing final_main_light row"))
        if clean_baseline_complete():
            if "clean_prob_re_eval_complete" not in table_text:
                findings.append(Finding("error", "main results template missing clean baseline label"))
        elif "historical_reference_not_clean_prob_final" not in table_text:
            findings.append(Finding("error", "main results template missing historical reference label"))
        if "b0_external_status_latest.md" not in table_text:
            findings.append(Finding("error", "main results template does not delegate B0 live status"))
        if "epoch40 best" in table_text or "epoch50 S=.7773" in table_text:
            findings.append(Finding("error", "main results template contains stale B0 epoch40/50 wording"))


def write_report(
    out_md: Path,
    metrics_csv: Path,
    profiles_csv: Path,
    findings: list[Finding],
    notes: list[str],
) -> None:
    errors = [item.message for item in findings if item.level == "error"]
    warnings = [item.message for item in findings if item.level == "warning"]
    status = "pass" if not errors else "fail"
    out_md.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Submission Protocol Audit",
        "",
        f"- Status: `{status}`",
        f"- Metrics CSV: `{metrics_csv}`",
        f"- Profiles CSV: `{profiles_csv}`",
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
    parser.add_argument("--metrics_csv", default=str(DEFAULT_METRICS))
    parser.add_argument("--profiles_csv", default=str(DEFAULT_PROFILES))
    parser.add_argument("--out_md", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    metrics_csv = Path(args.metrics_csv).expanduser().resolve()
    profiles_csv = Path(args.profiles_csv).expanduser().resolve()
    out_md = Path(args.out_md).expanduser().resolve()

    findings: list[Finding] = []
    notes: list[str] = []
    audit_required_artifacts(metrics_csv, profiles_csv, findings, notes)
    audit_metrics(metrics_csv, findings, notes)
    audit_profiles(profiles_csv, findings, notes)
    audit_paper_text(findings, notes)
    write_report(out_md, metrics_csv, profiles_csv, findings, notes)

    errors = [item for item in findings if item.level == "error"]
    for finding in findings:
        stream = sys.stderr if finding.level == "error" else sys.stdout
        print(f"{finding.level.upper()}: {finding.message}", file=stream)
    print(f"submission_protocol_audit={'pass' if not errors else 'fail'}")
    print(f"report={out_md}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
