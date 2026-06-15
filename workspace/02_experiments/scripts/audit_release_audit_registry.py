#!/usr/bin/env python3
"""Audit the fixed release-audit registry against the wrapper and reports."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


WORKSPACE = Path("/root/data-tmp/workspace")
DEFAULT_REGISTRY = WORKSPACE / "02_experiments" / "scripts" / "RELEASE_AUDIT_REGISTRY.md"
DEFAULT_WRAPPER = WORKSPACE / "02_experiments" / "scripts" / "run_release_audits.sh"
DEFAULT_REPORT = WORKSPACE / "04_paper" / "drafts" / "release_audit_latest.md"
DEFAULT_OUT = WORKSPACE / "02_experiments" / "scripts" / "release_audit_registry_audit_latest.md"


@dataclass(frozen=True)
class Finding:
    level: str
    message: str


@dataclass(frozen=True)
class RegistryRow:
    order: int
    script: str
    report: str
    guarded_surface: str
    control_docs: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_registry(text: str) -> list[RegistryRow]:
    rows: list[RegistryRow] = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        if "---" in line or "Order" in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 5:
            continue
        try:
            order = int(cells[0])
        except ValueError:
            continue
        clean = [re.sub(r"`", "", cell) for cell in cells]
        rows.append(
            RegistryRow(
                order=order,
                script=clean[1],
                report=clean[2],
                guarded_surface=clean[3],
                control_docs=clean[4],
            )
        )
    return rows


def extract_wrapper_fixed_scripts(wrapper_text: str) -> list[str]:
    names = re.findall(r"run_cmd python \"\$([A-Z0-9_]+)\"", wrapper_text)
    assignments = {
        name: value
        for name, value in re.findall(
            r"^([A-Z0-9_]+)=\"\$WORKSPACE/([^\"]+)\"",
            wrapper_text,
            flags=re.MULTILINE,
        )
    }
    scripts: list[str] = []
    for name in names:
        if name == "INTEGRITY_SCRIPT":
            continue
        value = assignments.get(name)
        if value:
            scripts.append(value)
    return scripts


def audit_registry(
    rows: list[RegistryRow],
    wrapper_text: str,
    release_text: str,
    findings: list[Finding],
    notes: list[str],
) -> None:
    if not rows:
        findings.append(Finding("error", "registry has no parsed rows"))
        return

    orders = [row.order for row in rows]
    expected_orders = list(range(1, len(rows) + 1))
    if orders != expected_orders:
        findings.append(Finding("error", f"registry orders are {orders}, expected {expected_orders}"))

    scripts = [row.script for row in rows]
    duplicate_scripts = sorted({script for script in scripts if scripts.count(script) > 1})
    for script in duplicate_scripts:
        findings.append(Finding("error", f"duplicate registry script: {script}"))

    wrapper_scripts = extract_wrapper_fixed_scripts(wrapper_text)
    if scripts != wrapper_scripts:
        findings.append(
            Finding(
                "error",
                "registry fixed script order does not match run_release_audits.sh: "
                f"registry={scripts}; wrapper={wrapper_scripts}",
            )
        )

    for row in rows:
        script_path = WORKSPACE / row.script
        report_path = WORKSPACE / row.report
        if not script_path.is_file():
            findings.append(Finding("error", f"registry script missing: {row.script}"))
        if not report_path.exists():
            findings.append(Finding("error", f"registry report missing: {row.report}"))
        if row.script not in wrapper_text:
            findings.append(Finding("error", f"wrapper missing registry script: {row.script}"))
        if row.script not in release_text:
            findings.append(Finding("error", f"latest release report missing command for: {row.script}"))
        if not row.guarded_surface or row.guarded_surface == "":
            findings.append(Finding("error", f"{row.script}: empty guarded surface"))
        for doc in [item.strip() for item in row.control_docs.split(",")]:
            if not doc:
                continue
            doc_path = WORKSPACE / doc
            if not doc_path.exists():
                findings.append(Finding("error", f"{row.script}: control doc missing: {doc}"))

    required_registry_markers = [
        "audit_gpu_runtime_state.py",
        "audit_task_board_consistency.py",
        "audit_agent_acceptance_ledger.py",
        "audit_submission_protocol.py",
        "audit_release_audit_registry.py",
        "run_release_audits.sh",
    ]
    registry_text = "\n".join([row.script + " " + row.report for row in rows])
    full_text = registry_text + "\n" + wrapper_text
    for marker in required_registry_markers:
        if marker not in full_text:
            findings.append(Finding("error", f"registry/wrapper missing marker `{marker}`"))

    notes.append(f"registry_rows={len(rows)}")
    notes.append(f"wrapper_fixed_scripts={len(wrapper_scripts)}")


def write_report(out_md: Path, findings: list[Finding], notes: list[str], registry: Path, wrapper: Path, release_report: Path) -> None:
    errors = [finding.message for finding in findings if finding.level == "error"]
    warnings = [finding.message for finding in findings if finding.level == "warning"]
    status = "pass" if not errors else "fail"
    out_md.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Release Audit Registry Audit",
        "",
        f"- Status: `{status}`",
        f"- Registry: `{registry}`",
        f"- Wrapper: `{wrapper}`",
        f"- Release report: `{release_report}`",
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
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--wrapper", default=str(DEFAULT_WRAPPER))
    parser.add_argument("--release_report", default=str(DEFAULT_REPORT))
    parser.add_argument("--out_md", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    registry = Path(args.registry).expanduser().resolve()
    wrapper = Path(args.wrapper).expanduser().resolve()
    release_report = Path(args.release_report).expanduser().resolve()
    out_md = Path(args.out_md).expanduser().resolve()
    findings: list[Finding] = []
    notes: list[str] = []

    if not registry.is_file():
        findings.append(Finding("error", f"missing registry: {registry}"))
        registry_text = ""
    else:
        registry_text = read_text(registry)

    if not wrapper.is_file():
        findings.append(Finding("error", f"missing wrapper: {wrapper}"))
        wrapper_text = ""
    else:
        wrapper_text = read_text(wrapper)

    if not release_report.is_file():
        findings.append(Finding("error", f"missing release report: {release_report}"))
        release_text = ""
    else:
        release_text = read_text(release_report)

    if registry_text and wrapper_text and release_text:
        audit_registry(parse_registry(registry_text), wrapper_text, release_text, findings, notes)

    write_report(out_md, findings, notes, registry, wrapper, release_report)

    errors = [finding for finding in findings if finding.level == "error"]
    for finding in findings:
        stream = sys.stderr if finding.level == "error" else sys.stdout
        print(f"{finding.level.upper()}: {finding.message}", file=stream)
    print(f"release_audit_registry_audit={'pass' if not errors else 'fail'}")
    print(f"report={out_md}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
