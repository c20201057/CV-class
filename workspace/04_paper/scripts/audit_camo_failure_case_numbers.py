#!/usr/bin/env python3
"""Audit CAMO failure-case statistics against the case-selection CSV."""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path


WORKSPACE = Path("/root/data-tmp/workspace")
DEFAULT_CSV = WORKSPACE / "04_paper" / "figures" / "camo_case_selection_b5_light.csv"
DEFAULT_OUT = WORKSPACE / "04_paper" / "drafts" / "camo_failure_case_number_audit_latest.md"
DEFAULT_DOCS = [
    WORKSPACE / "04_paper" / "drafts" / "camo_failure_case_analysis.md",
    WORKSPACE / "04_paper" / "drafts" / "paper_draft.md",
    WORKSPACE / "04_paper" / "drafts" / "paper_interim_submission.md",
    WORKSPACE / "04_paper" / "drafts" / "presentation_outline.md",
    WORKSPACE / "04_paper" / "drafts" / "writing_status.md",
]


@dataclass(frozen=True)
class CaseRow:
    stem: str
    baseline_mae: float
    light_mae: float
    delta: float


def read_cases(path: Path) -> list[CaseRow]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {
            "stem",
            "ESCNet-B5_mae",
            "Light-B2-C64_mae",
            "Light-B2-C64_minus_ESCNet-B5_mae",
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"missing CSV columns: {', '.join(sorted(missing))}")
        return [
            CaseRow(
                stem=row["stem"],
                baseline_mae=float(row["ESCNet-B5_mae"]),
                light_mae=float(row["Light-B2-C64_mae"]),
                delta=float(row["Light-B2-C64_minus_ESCNet-B5_mae"]),
            )
            for row in reader
        ]


def compute_stats(rows: list[CaseRow]) -> dict[str, str]:
    if not rows:
        raise ValueError("no CAMO case rows found")
    mean_delta = sum(row.delta for row in rows) / len(rows)
    worse = sum(1 for row in rows if row.delta > 0)
    better = sum(1 for row in rows if row.delta < 0)
    close = sum(1 for row in rows if abs(row.delta) < 0.005)
    worse_002 = sum(1 for row in rows if row.delta >= 0.02)
    better_002 = sum(1 for row in rows if row.delta <= -0.02)
    max_row = max(rows, key=lambda row: row.delta)
    min_row = min(rows, key=lambda row: row.delta)

    return {
        "samples": str(len(rows)),
        "mean_delta": f"{mean_delta:+.6f}",
        "mean_delta_plain": f"{mean_delta:.6f}",
        "worse": str(worse),
        "better": str(better),
        "close_abs_lt_0005": str(close),
        "worse_ge_002": str(worse_002),
        "better_le_neg_002": str(better_002),
        "max_stem": max_row.stem,
        "max_delta": f"{max_row.delta:+.6f}",
        "max_base": f"{max_row.baseline_mae:.6f}",
        "max_light": f"{max_row.light_mae:.6f}",
        "min_stem": min_row.stem,
        "min_delta": f"{min_row.delta:+.6f}",
        "min_base": f"{min_row.baseline_mae:.6f}",
        "min_light": f"{min_row.light_mae:.6f}",
    }


def expect_literal(text: str, literal: str, doc: Path, findings: list[str], label: str) -> None:
    if literal not in text:
        findings.append(f"{doc}: missing {label}: `{literal}`")


def audit_docs(docs: list[Path], stats: dict[str, str]) -> tuple[list[str], list[str]]:
    findings: list[str] = []
    notes: list[str] = []

    common_literals = [
        ("sample count", stats["samples"]),
        ("mean delta", stats["mean_delta_plain"]),
        ("close abs<0.005", stats["close_abs_lt_0005"]),
        ("worse >=0.02", stats["worse_ge_002"]),
    ]
    optional_literals = [
        ("better <=-0.02", stats["better_le_neg_002"]),
        ("worse count", stats["worse"]),
        ("better count", stats["better"]),
    ]
    analysis_only_literals = [
        ("max worse stem", stats["max_stem"]),
        ("max worse delta", stats["max_delta"]),
        ("max worse baseline", stats["max_base"]),
        ("max worse light", stats["max_light"]),
        ("max better stem", stats["min_stem"]),
        ("max better delta", stats["min_delta"]),
        ("max better baseline", stats["min_base"]),
        ("max better light", stats["min_light"]),
    ]

    for doc in docs:
        if not doc.is_file():
            findings.append(f"missing audited document: {doc}")
            continue
        text = doc.read_text(encoding="utf-8")
        if "camo_failure_case_analysis.md" not in doc.name and "CAMO" not in text:
            notes.append(f"{doc}: skipped no CAMO text")
            continue
        for label, literal in common_literals:
            expect_literal(text, literal, doc, findings, label)
        if doc.name in {"camo_failure_case_analysis.md", "paper_draft.md"}:
            for label, literal in optional_literals:
                expect_literal(text, literal, doc, findings, label)
        if doc.name == "camo_failure_case_analysis.md":
            for label, literal in analysis_only_literals:
                expect_literal(text, literal, doc, findings, label)
        notes.append(f"{doc}: checked")

    return findings, notes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case_csv", default=str(DEFAULT_CSV))
    parser.add_argument("--out_md", default=str(DEFAULT_OUT))
    parser.add_argument("--docs", nargs="*", default=[str(path) for path in DEFAULT_DOCS])
    args = parser.parse_args()

    case_csv = Path(args.case_csv).expanduser().resolve()
    out_path = Path(args.out_md).expanduser().resolve()
    docs = [Path(item).expanduser().resolve() for item in args.docs]

    findings: list[str] = []
    notes: list[str] = []
    try:
        rows = read_cases(case_csv)
        stats = compute_stats(rows)
        doc_findings, doc_notes = audit_docs(docs, stats)
        findings.extend(doc_findings)
        notes.extend(doc_notes)
    except Exception as exc:  # noqa: BLE001 - audit should report failures cleanly.
        findings.append(str(exc))
        stats = {}

    status = "pass" if not findings else "fail"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    stat_lines = [f"- {key}: `{value}`" for key, value in sorted(stats.items())]
    out_path.write_text(
        "\n".join(
            [
                "# CAMO Failure Case Number Audit",
                "",
                f"- Status: `{status}`",
                f"- Case CSV: `{case_csv}`",
                f"- Findings: {len(findings)}",
                "",
                "## Recomputed Stats",
                "",
                *(stat_lines or ["- unavailable"]),
                "",
                "## Findings",
                "",
                *([f"- {item}" for item in findings] or ["- none"]),
                "",
                "## Checked Documents",
                "",
                *([f"- {item}" for item in notes] or ["- none"]),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    for finding in findings:
        print(f"ERROR: {finding}", file=sys.stderr)
    print(f"camo_failure_case_number_audit={status}")
    print(f"report={out_path}")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())

