#!/usr/bin/env python3
"""Check local evidence paths cited by the paper claim-evidence matrix."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


WORKSPACE = Path("/root/data-tmp/workspace")
DEFAULT_MATRIX = WORKSPACE / "04_paper" / "drafts" / "paper_claim_evidence_matrix.md"
DEFAULT_OUT = WORKSPACE / "04_paper" / "drafts" / "claim_evidence_matrix_audit_latest.md"
DEFAULT_TICK = WORKSPACE / "00_project" / "orchestrator_tick_latest.json"

ABS_PATH_RE = re.compile(r"`(?P<path>/root/[^`]+)`")
ACCEPTED_STATUSES = {
    "accepted",
    "reference only",
    "accepted for checkpoint boundary",
    "engineering status only",
    "accepted boundary",
    "observation only",
}


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_data_row(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("| C") and "|" in stripped


def metric_tokens(text: str) -> list[str]:
    return re.findall(r"\d+\.\d+", text)


def token_present(text: str, token: str) -> bool:
    return token in text or (token.startswith("0.") and token[1:] in text)


def audit_matrix(path: Path, tick_path: Path | None = None) -> tuple[list[str], list[str]]:
    findings: list[str] = []
    notes: list[str] = []

    if not path.is_file():
        return [f"missing matrix file: {path}"], notes

    matrix_text = path.read_text(encoding="utf-8")
    tick: dict = {}
    if tick_path is not None:
        if not tick_path.is_file():
            findings.append(f"missing tick json: {tick_path}")
        else:
            tick = json.loads(tick_path.read_text(encoding="utf-8"))
            notes.append(f"tick_updated={tick.get('updated_utc', 'unknown')}")

    row_count = 0
    checked_paths = 0
    for lineno, line in enumerate(matrix_text.splitlines(), start=1):
        if not is_data_row(line):
            continue
        row_count += 1
        cells = split_table_row(line)
        if len(cells) < 5:
            findings.append(f"{path}:{lineno}: malformed claim row")
            continue
        claim_id, _claim, evidence_cell, _location, status = cells[:5]
        status_norm = status.lower()
        if status_norm not in ACCEPTED_STATUSES:
            findings.append(f"{path}:{lineno}: {claim_id} has unrecognized status `{status}`")

        paths = [Path(match.group("path")) for match in ABS_PATH_RE.finditer(evidence_cell)]
        if not paths:
            findings.append(f"{path}:{lineno}: {claim_id} cites no absolute evidence path")
            continue

        missing = [item for item in paths if not item.exists()]
        empty_files = [item for item in paths if item.exists() and item.is_file() and item.stat().st_size <= 0]
        checked_paths += len(paths)
        for item in missing:
            findings.append(f"{path}:{lineno}: {claim_id} missing evidence path `{item}`")
        for item in empty_files:
            findings.append(f"{path}:{lineno}: {claim_id} empty evidence file `{item}`")
        notes.append(
            f"{claim_id}: status={status}; paths={len(paths)}; missing={len(missing)}; "
            f"empty_files={len(empty_files)}"
        )

    if row_count == 0:
        findings.append(f"{path}: no claim rows found")

    if tick:
        mobile = tick.get("mobilemamba", {})
        mobile_result = mobile.get("latest_result", "")
        if mobile_result and "MobileMamba-T2" in matrix_text:
            missing_mobile = [
                token for token in metric_tokens(mobile_result) if not token_present(matrix_text, token)
            ]
            if missing_mobile:
                findings.append(
                    f"{path}: C13/MobileMamba claim missing current tick tokens "
                    f"{missing_mobile} from `{mobile_result}`"
                )
            if mobile.get("boundary") == "external_dirty_tree_observation_only" and "observation only" not in matrix_text:
                findings.append(f"{path}: MobileMamba boundary missing `observation only`")
        notes.append(f"mobilemamba_latest_result={mobile_result or 'unknown'}")

    notes.insert(0, f"claim_rows={row_count}")
    notes.insert(1, f"checked_paths={checked_paths}")
    return findings, notes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", default=str(DEFAULT_MATRIX))
    parser.add_argument("--tick_json", default=str(DEFAULT_TICK))
    parser.add_argument("--out_md", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    matrix = Path(args.matrix).expanduser().resolve()
    tick_path = Path(args.tick_json).expanduser().resolve()
    findings, notes = audit_matrix(matrix, tick_path)
    status = "pass" if not findings else "fail"

    out_path = Path(args.out_md).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        "\n".join(
            [
                "# Claim Evidence Matrix Audit",
                "",
                f"- Status: `{status}`",
                f"- Matrix: `{matrix}`",
                f"- Tick JSON: `{tick_path}`",
                f"- Findings: {len(findings)}",
                "",
                "## Findings",
                "",
                *([f"- {item}" for item in findings] or ["- none"]),
                "",
                "## Checked Rows",
                "",
                *([f"- {item}" for item in notes] or ["- none"]),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    for finding in findings:
        print(f"ERROR: {finding}", file=sys.stderr)
    print(f"claim_evidence_matrix_audit={status}")
    print(f"report={out_path}")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
