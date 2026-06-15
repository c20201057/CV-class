#!/usr/bin/env python3
"""Audit that subagent prompts explicitly carry the project work principles."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


WORKSPACE = Path("/root/data-tmp/workspace")
DEFAULT_ROOT = WORKSPACE / "03_agent_tasks"
DEFAULT_OUT = DEFAULT_ROOT / "prompts" / "prompt_principles_audit_latest.md"

RISK_PHRASES = [
    "不因为怕风险而保守",
    "不保守",
    "不要因为担心风险",
]


def check_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    findings: list[str] = []
    if "不偷懒" not in text:
        findings.append(f"{path}: missing `不偷懒`")
    if not any(phrase in text for phrase in RISK_PHRASES):
        findings.append(f"{path}: missing non-conservative risk principle")
    if path.name != "README.md" and "MASTER_TARGET_PROMPT.md" not in text and "不偷懒" not in text:
        findings.append(f"{path}: neither references MASTER_TARGET_PROMPT.md nor states the principle")
    return findings


def target_files(root: Path) -> list[Path]:
    prompt_dir = root / "prompts"
    pending_dir = root / "pending"
    files = sorted(prompt_dir.glob("*.md")) + sorted(pending_dir.glob("*.md"))
    return [
        item
        for item in files
        if item.is_file()
        and not item.name.endswith("_audit_latest.md")
        and item.name != "prompt_principles_audit_latest.md"
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--out_md", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    files = target_files(root)
    findings: list[str] = []
    notes: list[str] = []
    for file_path in files:
        file_findings = check_file(file_path)
        findings.extend(file_findings)
        notes.append(f"{file_path}: {'pass' if not file_findings else 'fail'}")

    status = "pass" if not findings else "fail"
    out_path = Path(args.out_md).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        "\n".join(
            [
                "# Prompt Principles Audit",
                "",
                f"- Status: `{status}`",
                f"- Root: `{root}`",
                f"- Files checked: {len(files)}",
                f"- Findings: {len(findings)}",
                "",
                "## Findings",
                "",
                *([f"- {item}" for item in findings] or ["- none"]),
                "",
                "## Checked Files",
                "",
                *[f"- {item}" for item in notes],
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    for finding in findings:
        print(f"ERROR: {finding}", file=sys.stderr)
    print(f"prompt_principles_audit={status}")
    print(f"report={out_path}")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
