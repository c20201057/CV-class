#!/usr/bin/env python3
"""Audit alignment between the CV proposal and current paper/workflow docs."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


WORKSPACE = Path("/root/data-tmp/workspace")
DEFAULT_REPORT = WORKSPACE / "00_project" / "cv_report_extracted.txt"
DEFAULT_OUT = WORKSPACE / "04_paper" / "drafts" / "cv_report_alignment_audit_latest.md"
DEFAULT_TARGETS = [
    WORKSPACE / "00_project" / "project_profile.md",
    WORKSPACE / "00_project" / "master_plan.md",
    WORKSPACE / "00_project" / "route_decision.md",
    WORKSPACE / "04_paper" / "drafts" / "paper_interim_submission.md",
    WORKSPACE / "04_paper" / "drafts" / "paper_draft.md",
    WORKSPACE / "04_paper" / "drafts" / "presentation_outline.md",
]


@dataclass(frozen=True)
class Requirement:
    key: str
    pattern: re.Pattern[str]
    rationale: str


REPORT_REQUIREMENTS = [
    Requirement("topic", re.compile(r"面向伪装目标分割的轻量化模型研究"), "proposal topic"),
    Requirement("camouflaged segmentation", re.compile(r"伪装目标分割|COD|COS"), "task definition"),
    Requirement("datasets", re.compile(r"COD10K.*NC4K.*CAMO|CAMO.*COD10K.*NC4K", re.S), "core datasets"),
    Requirement("light backbone", re.compile(r"轻量编码器|轻量主干|MobileNetV3|GhostNet|ShuffleNetV2|轻量 PVT"), "light encoder route"),
    Requirement("light fusion", re.compile(r"轻量多尺度融合|depthwise|Ghost module|ASPP|频域"), "light fusion route"),
    Requirement("boundary branch", re.compile(r"边界辅助分支|边界辅助监督|边界图"), "boundary compensation"),
    Requirement("distillation", re.compile(r"知识蒸馏|Lkd|MSE|KL"), "KD route"),
    Requirement("quantization", re.compile(r"量化|INT8|剪枝"), "deployment compression route"),
    Requirement("metrics", re.compile(r"Sα|Eϕ|F|MAE|Params|FLOPs|FPS|Latency|Model Size"), "accuracy and efficiency metrics"),
    Requirement("visualization", re.compile(r"可视化|精度.?效率折中"), "visual analysis and tradeoff"),
]

TARGET_REQUIREMENTS = [
    Requirement("ESCNet substrate", re.compile(r"ESCNet"), "chosen experiment substrate"),
    Requirement("Light model", re.compile(r"Light-ESCNet|Light B2-C64|B2-C64"), "current light model"),
    Requirement("PVTv2-B2 route", re.compile(r"PVTv2-B2|pvt_v2_b2"), "light backbone implementation"),
    Requirement("C64 decoder", re.compile(r"C64|inter_channel=64|64 通道|隐藏通道.*64"), "decoder width compression"),
    Requirement("boundary retained", re.compile(r"边缘-语义|边界|edge"), "boundary/edge compensation retained"),
    Requirement("KD boundary", re.compile(r"知识蒸馏|KD|teacher"), "distillation route tracked"),
    Requirement("datasets", re.compile(r"CAMO.*COD10K.*NC4K|COD10K.*CAMO.*NC4K|COD10K.*NC4K.*CAMO", re.S), "three core datasets"),
    Requirement("efficiency", re.compile(r"参数量|GMACs|FLOPs|Model Size|峰值显存|FPS|Latency"), "efficiency evidence"),
    Requirement("visualization", re.compile(r"可视化|visual|图 3|presentation"), "visual/report material"),
    Requirement("claim boundary", re.compile(r"不写 SOTA|不夸大|historical|历史.*参考|clean baseline|Gate"), "evidence boundary"),
]

PROFILE_REQUIREMENTS = [
    Requirement("proposal constraints section", re.compile(r"开题报告约束"), "explicit proposal mapping"),
    Requirement("four technical routes", re.compile(r"轻量编码器.*轻量多尺度融合.*边界辅助分支.*知识蒸馏", re.S), "proposal routes summarized"),
    Requirement("core datasets", re.compile(r"COD10K.*CAMO.*NC4K|COD10K.*NC4K.*CAMO", re.S), "proposal dataset mapping"),
]

MASTER_PLAN_REQUIREMENTS = [
    Requirement("non-lazy principle", re.compile(r"不偷懒"), "user principle"),
    Requirement("non-conservative principle", re.compile(r"不保守"), "user principle"),
    Requirement("workflow phases", re.compile(r"Phase 0.*Phase 1.*Phase 2.*Phase 3.*Phase 4", re.S), "workflow coverage"),
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_requirements(label: str, text: str, requirements: list[Requirement]) -> tuple[list[str], list[str]]:
    findings: list[str] = []
    notes: list[str] = []
    for req in requirements:
        if not req.pattern.search(text):
            findings.append(f"{label}: missing `{req.key}` ({req.rationale})")
        else:
            notes.append(f"{label}: found `{req.key}`")
    return findings, notes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--targets", nargs="*", default=[str(path) for path in DEFAULT_TARGETS])
    parser.add_argument("--out_md", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    report = Path(args.report).expanduser().resolve()
    targets = [Path(item).expanduser().resolve() for item in args.targets]
    out_path = Path(args.out_md).expanduser().resolve()

    findings: list[str] = []
    notes: list[str] = []

    if not report.is_file():
        findings.append(f"missing extracted CV report: {report}")
        report_text = ""
    else:
        report_text = read_text(report)
        sub_findings, sub_notes = check_requirements("cv_report", report_text, REPORT_REQUIREMENTS)
        findings.extend(sub_findings)
        notes.extend(sub_notes)

    combined_target_text = ""
    for target in targets:
        if not target.is_file():
            findings.append(f"missing alignment target: {target}")
            continue
        combined_target_text += "\n" + read_text(target)

    if combined_target_text:
        sub_findings, sub_notes = check_requirements(
            "paper_and_workflow_targets",
            combined_target_text,
            TARGET_REQUIREMENTS,
        )
        findings.extend(sub_findings)
        notes.extend(sub_notes)

    project_profile = WORKSPACE / "00_project" / "project_profile.md"
    if project_profile.is_file():
        sub_findings, sub_notes = check_requirements(
            "project_profile",
            read_text(project_profile),
            PROFILE_REQUIREMENTS,
        )
        findings.extend(sub_findings)
        notes.extend(sub_notes)
    else:
        findings.append(f"missing project profile: {project_profile}")

    master_plan = WORKSPACE / "00_project" / "master_plan.md"
    if master_plan.is_file():
        sub_findings, sub_notes = check_requirements(
            "master_plan",
            read_text(master_plan),
            MASTER_PLAN_REQUIREMENTS,
        )
        findings.extend(sub_findings)
        notes.extend(sub_notes)
    else:
        findings.append(f"missing master plan: {master_plan}")

    status = "pass" if not findings else "fail"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        "\n".join(
            [
                "# CV Report Alignment Audit",
                "",
                f"- Status: `{status}`",
                f"- Report: `{report}`",
                f"- Targets: {len(targets)}",
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
    print(f"cv_report_alignment_audit={status}")
    print(f"report={out_path}")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
