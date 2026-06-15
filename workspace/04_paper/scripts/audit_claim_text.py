#!/usr/bin/env python3
"""Scan paper-facing text for claims that exceed current evidence gates.

The evidence-gate documents intentionally contain forbidden phrases, so this
script defaults to scanning only paper-facing deliverables: the paper draft,
outline, and result tables. It is a guardrail for finalization, not a semantic
proof checker.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


DEFAULT_TARGETS = [
    "/root/data-tmp/workspace/04_paper/drafts/paper_draft.md",
    "/root/data-tmp/workspace/04_paper/drafts/paper_interim_submission.md",
    "/root/data-tmp/workspace/04_paper/drafts/teacher_share_pack.md",
    "/root/data-tmp/workspace/04_paper/drafts/presentation_outline.md",
    "/root/data-tmp/workspace/04_paper/outline/paper_outline.md",
    "/root/data-tmp/workspace/04_paper/tables/main_results_template.md",
    "/root/data-tmp/workspace/04_paper/tables/aggregated_results.md",
]

NEGATION_HINTS = [
    "不",
    "不能",
    "不得",
    "禁止",
    "未",
    "尚未",
    "待",
    "pending",
    "withheld",
    "not",
    "cannot",
    "until",
    "unless",
    "reference",
    "historical",
    "TBD",
    "待补",
]

RULES = [
    (
        "sota_claim",
        re.compile(r"\bSOTA\b|state[- ]of[- ]the[- ]art|最先进|最佳性能", re.I),
        "Do not claim SOTA/current best performance.",
    ),
    (
        "first_kd_claim",
        re.compile(r"首次|first.*KD|first.*distillation|首次.*蒸馏", re.I),
        "Do not claim first KD-COD or first distillation contribution.",
    ),
    (
        "deployment_claim",
        re.compile(r"实时部署|边缘端部署|edge[- ]device deployment|real[- ]time deployment", re.I),
        "Do not claim deployment without direct deployment evidence.",
    ),
    (
        "final_clean_baseline_claim",
        re.compile(r"final clean probability baseline|最终.*baseline|最终.*基线|统一协议 baseline"),
        "Do not present ESCNet-B5 as final clean probability baseline before Gate 1.",
    ),
    (
        "kd_improvement_claim",
        re.compile(
            r"KD.*(提升|有效|缩小|\bimprove\b|\bimproves\b|\bimproved\b|\bclose\b|\bcloses\b)"
            r"|蒸馏.*(提升|有效|缩小)",
            re.I,
        ),
        "Do not claim KD improvement before Gate 2.",
    ),
    (
        "speedup_claim",
        re.compile(r"(FPS|latency|延迟|速度).*(提升|加速|speedup|faster|降低)|实测.*(FPS|latency|延迟)", re.I),
        "Do not claim final latency/FPS speedup before Gate 3.",
    ),
    (
        "b0_main_claim",
        re.compile(r"(B0|PVTv2-B0|Tiny-ESCNet).*(主表|主结论|main table|conclusion)", re.I),
        "Do not put B0 intermediate branch into main table/conclusion before Gate 4A.",
    ),
    (
        "mobilemamba_main_claim",
        re.compile(r"(MobileMamba|mobilemamba_t2).*(主表|主结论|main table|conclusion)", re.I),
        "Do not put MobileMamba observation branch into main table/conclusion before Gate 4B.",
    ),
]


def is_negated(line: str) -> bool:
    lower = line.lower()
    return any(hint.lower() in lower for hint in NEGATION_HINTS)


def audit_file(path: Path) -> list[str]:
    findings: list[str] = []
    if not path.is_file():
        findings.append(f"{path}: missing file")
        return findings

    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        for rule_id, pattern, message in RULES:
            if pattern.search(stripped) and not is_negated(stripped):
                findings.append(f"{path}:{lineno}: {rule_id}: {message} :: {stripped}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit paper-facing claim text.")
    parser.add_argument(
        "--targets",
        nargs="*",
        default=DEFAULT_TARGETS,
        help="Files to scan. Defaults to paper-facing draft/table deliverables.",
    )
    parser.add_argument(
        "--out_md",
        default="/root/data-tmp/workspace/04_paper/drafts/claim_text_audit_latest.md",
    )
    args = parser.parse_args()

    targets = [Path(item).expanduser().resolve() for item in args.targets]
    findings: list[str] = []
    for target in targets:
        findings.extend(audit_file(target))

    out_md = Path(args.out_md).expanduser().resolve() if args.out_md else None
    if out_md:
        out_md.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "# Claim Text Audit",
            "",
            f"- Status: `{'pass' if not findings else 'fail'}`",
            f"- Targets: {len(targets)}",
            f"- Findings: {len(findings)}",
            "",
            "## Findings",
            "",
        ]
        lines.extend([f"- {item}" for item in findings] or ["- none"])
        out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    for finding in findings:
        print(f"ERROR: {finding}", file=sys.stderr)
    print(f"claim_text_audit={'pass' if not findings else 'fail'}")
    if out_md:
        print(f"report={out_md}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
