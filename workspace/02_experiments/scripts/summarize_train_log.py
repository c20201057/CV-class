#!/usr/bin/env python3
"""Parse ESCNet training logs into CSV/Markdown loss summaries."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


FINAL_RE = re.compile(
    r"@==Final== Epoch\[(?P<epoch>\d+)/(?P<total>\d+)\] Avg Training Loss: (?P<loss>[0-9.]+)"
)


def parse_log(path: Path) -> list[dict[str, str]]:
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = FINAL_RE.search(line)
        if not match:
            continue
        rows.append(
            {
                "epoch": match.group("epoch"),
                "total_epochs": match.group("total"),
                "avg_loss": f"{float(match.group('loss')):.3f}",
            }
        )
    if not rows:
        raise ValueError(f"No epoch-final loss rows found in {path}")
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["epoch", "total_epochs", "avg_loss"])
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "| epoch | total_epochs | avg_loss |",
        "| ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(f"| {row['epoch']} | {row['total_epochs']} | {row['avg_loss']} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize ESCNet train_ddp.log losses.")
    parser.add_argument("--log", required=True, help="Path to train log.")
    parser.add_argument("--out_csv", required=True, help="Output CSV path.")
    parser.add_argument("--out_md", default=None, help="Optional Markdown output.")
    args = parser.parse_args()

    rows = parse_log(Path(args.log).expanduser())
    write_csv(Path(args.out_csv).expanduser(), rows)
    if args.out_md:
        write_md(Path(args.out_md).expanduser(), rows)
    print({"epochs": len(rows), "last": rows[-1]})


if __name__ == "__main__":
    main()
