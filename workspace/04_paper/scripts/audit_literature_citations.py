#!/usr/bin/env python3
"""Audit literature notes and paper reference coverage.

This guardrail is intentionally concrete: it checks that the local literature
files exist, that paper-facing drafts cite the core COD/lightweight/KD works, and
that the literature notes preserve the novelty boundaries used by the paper.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


WORKSPACE = Path("/root/data-tmp/workspace")
DEFAULT_OUT = WORKSPACE / "04_paper" / "drafts" / "literature_citation_audit_latest.md"
DEFAULT_LITERATURE_FILES = [
    WORKSPACE / "01_literature" / "verified_literature.md",
    WORKSPACE / "01_literature" / "literature_gap_update_2026.md",
    WORKSPACE / "01_literature" / "citation_notes.md",
    WORKSPACE / "01_literature" / "web_search_notes.md",
]
DEFAULT_CITATION_MANIFEST = WORKSPACE / "04_paper" / "drafts" / "citation_manifest.md"
DEFAULT_PAPER_FILES = [
    WORKSPACE / "04_paper" / "drafts" / "paper_interim_submission.md",
    WORKSPACE / "04_paper" / "drafts" / "paper_draft.md",
]

REQUIRED_INLINE_REFERENCE_IDS = set(range(1, 19))
REQUIRED_INLINE_GROUPS = {
    "datasets": {1, 2, 3},
    "classic_cod": {2, 4, 5, 6},
    "backbone_and_substrate": {7, 8},
    "recent_strong_cod": {9, 10},
    "lightweight_cod": {11, 12, 13, 14},
    "distillation_cod": {15, 16, 17, 18},
}


@dataclass(frozen=True)
class RequiredWork:
    key: str
    pattern: re.Pattern[str]
    rationale: str


REQUIRED_REFERENCE_WORKS = [
    RequiredWork("CAMO/Anabranch", re.compile(r"Anabranch|CAMO", re.I), "dataset/task origin"),
    RequiredWork("COD10K/SINet", re.compile(r"Camouflaged Object Detection|COD10K|SINet", re.I), "COD10K and classic COD"),
    RequiredWork("NC4K/Rank", re.compile(r"Simultaneously Localize|NC4K|Rank", re.I), "NC4K generalization benchmark"),
    RequiredWork("PFNet", re.compile(r"Distraction Mining|PFNet", re.I), "classic distraction mining COD"),
    RequiredWork("FDCOD", re.compile(r"Frequency Domain|FDCOD", re.I), "frequency-domain COD"),
    RequiredWork("DGNet", re.compile(r"Deep Gradient Learning|DGNet", re.I), "efficient COD baseline"),
    RequiredWork("PVTv2", re.compile(r"PVT ?v2|Pyramid Vision Transformer", re.I), "backbone family"),
    RequiredWork("ESCNet", re.compile(r"ESCNet|Edge-Semantic Collaborative", re.I), "experiment substrate"),
    RequiredWork("CamoFormer", re.compile(r"CamoFormer|Masked Separable Attention", re.I), "recent strong COD"),
    RequiredWork("HGINet", re.compile(r"HGINet|Hierarchical Graph Interaction", re.I), "recent transformer COD"),
    RequiredWork("FINet", re.compile(r"FINet|Frequency Injection", re.I), "lightweight COD"),
    RequiredWork("CSFIN", re.compile(r"CSFIN|Cross-Stage Feature Interaction", re.I), "lightweight COD"),
    RequiredWork("BPNet", re.compile(r"Boundary Perception|BPNet", re.I), "boundary-aware lightweight COD"),
    RequiredWork("LiteCOD", re.compile(r"LiteCOD|Local-Global Features", re.I), "lightweight COD"),
    RequiredWork("KD/Hinton", re.compile(r"Distilling the Knowledge|Hinton", re.I), "knowledge distillation basis"),
    RequiredWork("CamoTeacher", re.compile(r"CamoTeacher|Dual-Rotation", re.I), "teacher-student COD boundary"),
    RequiredWork("SAM-COD", re.compile(r"SAM-COD|SAM-guided", re.I), "KD in weakly supervised COD"),
    RequiredWork("CFF-KDNet", re.compile(r"CFF-KDNet|Cross-Scale Feature Fusion", re.I), "recent KD-COD boundary"),
]

REQUIRED_NOTE_MARKERS = {
    "verified_literature.md": [
        "公开材料不足的 2026 工作只作趋势或未来工作",
        "ESCNet",
        "FINet",
        "CamoTeacher",
        "SAM-COD",
    ],
    "literature_gap_update_2026.md": [
        "不能主张",
        "不能说本文是首个轻量 COD 方法",
        "不能说本文首次将知识蒸馏用于 COD",
        "PVTv2 压缩路线",
    ],
    "citation_notes.md": [
        "## 引言",
        "## 相关工作 2.1",
        "## 相关工作 2.2",
        "## 相关工作 2.3",
        "## 方法",
        "## 未来工作",
    ],
    "web_search_notes.md": [
        "核心基准",
        "边界、频域与强基线",
        "轻量化 COD",
        "模型压缩与 KD",
    ],
    "citation_manifest.md": [
        "Paper use",
        "Evidence source",
        "Boundary",
        "Do not claim",
        "Pending evidence",
        "R01 / [1]",
        "R18 / [18]",
        "本文不是首个轻量 COD",
        "本文不能主张首次将 KD 用于 COD",
        "当前与 ESCNet-B5 的差值只能写作历史参考口径",
    ],
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def reference_section(text: str) -> str:
    marker = "## 参考文献"
    if marker not in text:
        return ""
    return text.split(marker, maxsplit=1)[1]


def body_section(text: str) -> str:
    marker = "## 参考文献"
    return text.split(marker, maxsplit=1)[0] if marker in text else text


def expand_inline_reference_ids(match: str) -> set[int]:
    ids: set[int] = set()
    for token in re.split(r"\s*,\s*", match):
        if "-" in token:
            start_text, end_text = token.split("-", maxsplit=1)
            if start_text.isdigit() and end_text.isdigit():
                start = int(start_text)
                end = int(end_text)
                if start <= end:
                    ids.update(range(start, end + 1))
        elif token.isdigit():
            ids.add(int(token))
    return ids


def inline_reference_ids(text: str) -> set[int]:
    ids: set[int] = set()
    for match in re.findall(r"\[([0-9,\-\s]+)\]", text):
        ids.update(expand_inline_reference_ids(match))
    return ids


def audit_literature_files(paths: list[Path]) -> tuple[list[str], list[str]]:
    findings: list[str] = []
    notes: list[str] = []
    for path in paths:
        if not path.is_file():
            findings.append(f"missing literature file: {path}")
            continue
        text = read_text(path)
        markers = REQUIRED_NOTE_MARKERS.get(path.name, [])
        missing_markers = [marker for marker in markers if marker not in text]
        for marker in missing_markers:
            findings.append(f"{path}: missing required marker `{marker}`")
        notes.append(f"{path.name}: markers={len(markers)} missing={len(missing_markers)}")
    return findings, notes


def audit_paper_references(paths: list[Path]) -> tuple[list[str], list[str]]:
    findings: list[str] = []
    notes: list[str] = []
    for path in paths:
        if not path.is_file():
            findings.append(f"missing paper file: {path}")
            continue
        text = read_text(path)
        refs = reference_section(text)
        if not refs:
            findings.append(f"{path}: missing `## 参考文献` section")
            continue
        body_refs = inline_reference_ids(body_section(text))
        missing_inline_refs = sorted(REQUIRED_INLINE_REFERENCE_IDS - body_refs)
        if missing_inline_refs:
            findings.append(
                f"{path}: missing inline citations for refs {missing_inline_refs}"
            )
        for group_name, required_ids in REQUIRED_INLINE_GROUPS.items():
            missing_group_ids = sorted(required_ids - body_refs)
            if missing_group_ids:
                findings.append(
                    f"{path}: inline citation group `{group_name}` misses refs {missing_group_ids}"
                )
        ref_count = len(re.findall(r"^\[[0-9]+\]", refs, flags=re.MULTILINE))
        if ref_count < len(REQUIRED_REFERENCE_WORKS):
            findings.append(
                f"{path}: reference count {ref_count} is below required core works "
                f"{len(REQUIRED_REFERENCE_WORKS)}"
            )
        missing_works = [work.key for work in REQUIRED_REFERENCE_WORKS if not work.pattern.search(refs)]
        for key in missing_works:
            findings.append(f"{path}: missing core reference `{key}`")
        notes.append(
            f"{path.name}: refs={ref_count} inline_refs={len(body_refs)} "
            f"missing_inline={len(missing_inline_refs)} missing_core={len(missing_works)}"
        )
    return findings, notes


def audit_verified_alignment(verified_path: Path) -> tuple[list[str], list[str]]:
    findings: list[str] = []
    notes: list[str] = []
    if not verified_path.is_file():
        return [f"missing verified literature file: {verified_path}"], notes
    text = read_text(verified_path)
    missing_works = [work.key for work in REQUIRED_REFERENCE_WORKS if not work.pattern.search(text)]
    for key in missing_works:
        findings.append(f"{verified_path}: missing verified entry for `{key}`")
    notes.append(f"verified_literature core coverage missing={len(missing_works)}")
    return findings, notes


def audit_citation_manifest(path: Path) -> tuple[list[str], list[str]]:
    findings: list[str] = []
    notes: list[str] = []
    if not path.is_file():
        return [f"missing citation manifest: {path}"], notes
    text = read_text(path)
    missing_markers = [marker for marker in REQUIRED_NOTE_MARKERS["citation_manifest.md"] if marker not in text]
    for marker in missing_markers:
        findings.append(f"{path}: missing required marker `{marker}`")

    for idx in range(1, len(REQUIRED_REFERENCE_WORKS) + 1):
        label = f"R{idx:02d} / [{idx}]"
        if label not in text:
            findings.append(f"{path}: missing reference map label `{label}`")

    missing_works = [work.key for work in REQUIRED_REFERENCE_WORKS if not work.pattern.search(text)]
    for key in missing_works:
        findings.append(f"{path}: missing manifest entry for `{key}`")

    boundary_terms = [
        "首个轻量 COD",
        "首个边界感知轻量 COD",
        "首个 KD-COD",
        "COD SOTA",
        "实时部署",
        "固定基线",
        "完整训练",
        "空闲 GPU",
    ]
    missing_boundaries = [term for term in boundary_terms if term not in text]
    for term in missing_boundaries:
        findings.append(f"{path}: missing boundary term `{term}`")

    notes.append(
        f"{path.name}: refs={len(REQUIRED_REFERENCE_WORKS)} "
        f"missing_markers={len(missing_markers)} missing_core={len(missing_works)}"
    )
    return findings, notes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out_md", default=str(DEFAULT_OUT))
    parser.add_argument(
        "--literature_files",
        nargs="*",
        default=[str(path) for path in DEFAULT_LITERATURE_FILES],
    )
    parser.add_argument("--citation_manifest", default=str(DEFAULT_CITATION_MANIFEST))
    parser.add_argument("--paper_files", nargs="*", default=[str(path) for path in DEFAULT_PAPER_FILES])
    args = parser.parse_args()

    literature_files = [Path(item).expanduser().resolve() for item in args.literature_files]
    citation_manifest = Path(args.citation_manifest).expanduser().resolve()
    paper_files = [Path(item).expanduser().resolve() for item in args.paper_files]

    findings: list[str] = []
    notes: list[str] = []

    sub_findings, sub_notes = audit_literature_files(literature_files)
    findings.extend(sub_findings)
    notes.extend(sub_notes)

    verified_path = WORKSPACE / "01_literature" / "verified_literature.md"
    sub_findings, sub_notes = audit_verified_alignment(verified_path)
    findings.extend(sub_findings)
    notes.extend(sub_notes)

    sub_findings, sub_notes = audit_citation_manifest(citation_manifest)
    findings.extend(sub_findings)
    notes.extend(sub_notes)

    sub_findings, sub_notes = audit_paper_references(paper_files)
    findings.extend(sub_findings)
    notes.extend(sub_notes)

    status = "pass" if not findings else "fail"
    out_path = Path(args.out_md).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        "\n".join(
            [
                "# Literature Citation Audit",
                "",
                f"- Status: `{status}`",
                f"- Literature files: {len(literature_files)}",
                f"- Citation manifest: `{citation_manifest}`",
                f"- Paper files: {len(paper_files)}",
                f"- Required core works: {len(REQUIRED_REFERENCE_WORKS)}",
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
    print(f"literature_citation_audit={status}")
    print(f"report={out_path}")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
