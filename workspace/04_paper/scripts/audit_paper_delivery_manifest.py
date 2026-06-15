#!/usr/bin/env python3
"""Audit the paper delivery manifest and its referenced artifacts."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


WORKSPACE = Path("/root/data-tmp/workspace")
DEFAULT_MANIFEST = WORKSPACE / "04_paper" / "drafts" / "paper_delivery_manifest.md"
DEFAULT_OUT = WORKSPACE / "04_paper" / "drafts" / "paper_delivery_manifest_audit_latest.md"

REQUIRED_MARKERS = [
    "不偷懒",
    "不因为怕风险而保守",
    "honest interim",
    "paper_interim_submission.md",
    "teacher_share_pack.md",
    "presentation_outline.md",
    "reproducibility_manifest.md",
    "evidence_index.md",
    "paper_claim_evidence_matrix.md",
    "orchestrator_tick_latest.md",
    "release_audit_latest.md",
    "RELEASE_AUDIT_REGISTRY.md",
    "release_audit_registry_audit_latest.md",
    "Light-ESCNet B2-C64",
    "CAMO S=.862",
    "COD10K S=.866",
    "NC4K S=.886",
    "历史 ESCNet-B5 reference",
    "Gate 1",
    "Gate 2",
    "Gate 3",
    "Gate 4A",
    "Gate 4B",
    "不能写作已证明提升",
]

REQUIRED_PATHS = [
    "04_paper/drafts/paper_interim_submission.md",
    "04_paper/drafts/teacher_share_pack.md",
    "04_paper/drafts/presentation_outline.md",
    "04_paper/drafts/paper_submission_packet.md",
    "04_paper/drafts/reproducibility_manifest.md",
    "04_paper/drafts/evidence_index.md",
    "04_paper/drafts/paper_claim_evidence_matrix.md",
    "04_paper/drafts/submission_protocol_checklist.md",
    "00_project/goal_completion_matrix.md",
    "00_project/orchestrator_tick_latest.md",
    "04_paper/drafts/release_audit_latest.md",
    "02_experiments/scripts/RELEASE_AUDIT_REGISTRY.md",
    "02_experiments/scripts/release_audit_registry_audit_latest.md",
    "04_paper/figures/light_b2_c64_method.png",
    "04_paper/figures/accuracy_efficiency_scatter.png",
    "04_paper/figures/camo_visual_grid_b5_light_b2c64.png",
    "04_paper/figures/camo_light_worse_cases.png",
    "04_paper/figures/camo_light_close_cases.png",
    "04_paper/figures/camo_light_better_cases.png",
    "04_paper/figures/b0_cod10k_intermediate_trend.png",
]

FORBIDDEN_UNSAFE_CLAIMS = [
    re.compile(r"final clean probability baseline(?![^.\n]*(?:直到|unless|pending|withheld|不能|不得|不写))", re.I),
    re.compile(r"KD[^.\n]*(?:提升|有效|缩小差距|improves|improved)(?![^.\n]*(?:不能|不写|直到|unless|pending|withheld))", re.I),
    re.compile(r"(?:latency|FPS|速度|加速)[^.\n]*(?:最终|提升|降低|faster|speedup)(?![^.\n]*(?:不能|不写|直到|unless|pending|withheld))", re.I),
    re.compile(r"SOTA|state-of-the-art|首次 KD-COD|实时部署|边缘端部署", re.I),
]

WITHHELD_LINE_HINTS = [
    "不写",
    "不能",
    "不得",
    "只能",
    "until",
    "unless",
    "pending",
    "withheld",
    "Gate ",
]


@dataclass(frozen=True)
class Finding:
    level: str
    message: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def audit_manifest(manifest: Path, findings: list[Finding], notes: list[str]) -> None:
    if not manifest.is_file():
        findings.append(Finding("error", f"missing manifest: {manifest}"))
        return
    text = read_text(manifest)
    if not text.strip():
        findings.append(Finding("error", f"empty manifest: {manifest}"))
        return

    for marker in REQUIRED_MARKERS:
        if marker not in text:
            findings.append(Finding("error", f"manifest missing marker `{marker}`"))

    for rel_path in REQUIRED_PATHS:
        path = WORKSPACE / rel_path
        if rel_path not in text:
            findings.append(Finding("error", f"manifest missing path `{rel_path}`"))
        if not path.exists():
            findings.append(Finding("error", f"referenced path missing: {rel_path}"))
        elif path.is_file() and path.stat().st_size == 0:
            findings.append(Finding("error", f"referenced path empty: {rel_path}"))
        else:
            notes.append(f"path ok: {rel_path}")

    required_sections = [
        "## External-Facing Files",
        "## Core Figure Assets",
        "## Internal Evidence And Reproducibility",
        "## Allowed Delivery Claims",
        "## Withheld Claims",
        "## Current Gate Snapshot",
        "## Required Commands",
    ]
    for section in required_sections:
        if section not in text:
            findings.append(Finding("error", f"manifest missing section `{section}`"))

    for pattern in FORBIDDEN_UNSAFE_CLAIMS:
        for match in pattern.finditer(text):
            line_start = text.rfind("\n", 0, match.start()) + 1
            line_end = text.find("\n", match.end())
            if line_end == -1:
                line_end = len(text)
            line = text[line_start:line_end].strip()
            if any(hint in line for hint in WITHHELD_LINE_HINTS):
                notes.append(f"withheld unsafe-claim phrase allowed: {line}")
                continue
            findings.append(
                Finding(
                    "error",
                    f"unsafe delivery claim: {line}",
                )
            )


def write_report(out_md: Path, manifest: Path, findings: list[Finding], notes: list[str]) -> None:
    errors = [finding.message for finding in findings if finding.level == "error"]
    warnings = [finding.message for finding in findings if finding.level == "warning"]
    status = "pass" if not errors else "fail"
    out_md.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Paper Delivery Manifest Audit",
        "",
        f"- Status: `{status}`",
        f"- Manifest: `{manifest}`",
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
        *([f"- {note}" for note in notes] or ["- none"]),
    ]
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--out_md", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    manifest = Path(args.manifest).expanduser().resolve()
    out_md = Path(args.out_md).expanduser().resolve()
    findings: list[Finding] = []
    notes: list[str] = []

    audit_manifest(manifest, findings, notes)
    write_report(out_md, manifest, findings, notes)

    errors = [finding for finding in findings if finding.level == "error"]
    for finding in findings:
        stream = sys.stderr if finding.level == "error" else sys.stdout
        print(f"{finding.level.upper()}: {finding.message}", file=stream)
    print(f"paper_delivery_manifest_audit={'pass' if not errors else 'fail'}")
    print(f"report={out_md}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
