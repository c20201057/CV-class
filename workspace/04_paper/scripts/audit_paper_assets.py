#!/usr/bin/env python3
"""Check that paper-facing Markdown image assets exist and are non-empty."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


WORKSPACE = Path("/root/data-tmp/workspace")
DEFAULT_TARGETS = [
    WORKSPACE / "04_paper" / "drafts" / "paper_draft.md",
    WORKSPACE / "04_paper" / "drafts" / "paper_interim_submission.md",
    WORKSPACE / "04_paper" / "drafts" / "teacher_share_pack.md",
    WORKSPACE / "04_paper" / "drafts" / "presentation_outline.md",
]
DEFAULT_OUT = WORKSPACE / "04_paper" / "drafts" / "paper_asset_audit_latest.md"
IMAGE_RE = re.compile(r"!\[[^\]]*\]\((?P<path>[^)]+)\)")


def audit_file(path: Path) -> list[str]:
    findings: list[str] = []
    if not path.is_file():
        return [f"missing markdown target: {path}"]
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        for match in IMAGE_RE.finditer(line):
            raw = match.group("path").strip()
            if raw.startswith(("http://", "https://")):
                continue
            asset = (path.parent / raw).resolve()
            if not asset.is_file():
                findings.append(f"{path}:{lineno}: missing image asset `{raw}` -> `{asset}`")
            elif asset.stat().st_size <= 0:
                findings.append(f"{path}:{lineno}: empty image asset `{raw}` -> `{asset}`")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--targets", nargs="*", default=[str(p) for p in DEFAULT_TARGETS])
    parser.add_argument("--out_md", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    targets = [Path(item).expanduser().resolve() for item in args.targets]
    findings: list[str] = []
    image_count = 0
    for target in targets:
        if target.is_file():
            image_count += len(IMAGE_RE.findall(target.read_text(encoding="utf-8")))
        findings.extend(audit_file(target))

    status = "pass" if not findings else "fail"
    out_path = Path(args.out_md).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        "\n".join(
            [
                "# Paper Asset Audit",
                "",
                f"- Status: `{status}`",
                f"- Targets: {len(targets)}",
                f"- Markdown image references: {image_count}",
                f"- Findings: {len(findings)}",
                "",
                "## Findings",
                "",
                *([f"- {item}" for item in findings] or ["- none"]),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    for finding in findings:
        print(f"ERROR: {finding}", file=sys.stderr)
    print(f"paper_asset_audit={status}")
    print(f"report={out_path}")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
