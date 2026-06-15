#!/usr/bin/env python3
"""Audit accepted Light-B2-C64 run metadata against final evidence files."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path


WORKSPACE = Path("/root/data-tmp/workspace")
DEFAULT_RUN_DIR = WORKSPACE / "02_experiments" / "runs" / "light_b2_c64_e120_s42"
DEFAULT_EVAL_RUN = WORKSPACE / "02_experiments" / "runs" / "light_b2_c64_e120_s42_prob_eval_v2"
DEFAULT_METRICS = WORKSPACE / "02_experiments" / "tables" / "metrics_all.csv"
DEFAULT_PROFILES = WORKSPACE / "02_experiments" / "tables" / "profiles.csv"
DEFAULT_OUT = WORKSPACE / "04_paper" / "drafts" / "light_final_metadata_audit_latest.md"

DATASETS = {"CAMO", "COD10K", "NC4K"}
TRAIN_EXP_ID = "light_b2_c64_e120_s42"
EVAL_EXP_ID = "light_b2_c64_e120_s42_prob_eval_v2"
PROFILE_EXP_ID = "light_b2_c64_trained_416"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run_dir", default=str(DEFAULT_RUN_DIR))
    parser.add_argument("--eval_run", default=str(DEFAULT_EVAL_RUN))
    parser.add_argument("--metrics_csv", default=str(DEFAULT_METRICS))
    parser.add_argument("--profiles_csv", default=str(DEFAULT_PROFILES))
    parser.add_argument("--out_md", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    eval_run = Path(args.eval_run).expanduser().resolve()
    metrics_csv = Path(args.metrics_csv).expanduser().resolve()
    profiles_csv = Path(args.profiles_csv).expanduser().resolve()
    out_md = Path(args.out_md).expanduser().resolve()

    findings: list[str] = []
    notes: list[str] = []

    metadata_path = run_dir / "metadata.json"
    if not metadata_path.is_file():
        findings.append(f"missing metadata: {metadata_path}")
        metadata = {}
    else:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    expected = {
        "exp_id": TRAIN_EXP_ID,
        "status": "complete_final_main_light",
        "completed_epoch": 120,
        "final_avg_train_loss": 1.369,
        "prob_eval_exp_id": EVAL_EXP_ID,
        "prob_eval_status": "final_main_light",
        "prob_eval_protocol": "prob_map",
    }
    for key, value in expected.items():
        if metadata.get(key) != value:
            findings.append(f"metadata `{key}` expected `{value}`, found `{metadata.get(key)}`")
        else:
            notes.append(f"metadata {key} ok: {value}")

    checkpoint_paths = sorted(run_dir.glob("epoch_*.pth"))
    if metadata.get("checkpoint_count") != len(checkpoint_paths):
        findings.append(
            f"checkpoint_count expected {len(checkpoint_paths)}, found {metadata.get('checkpoint_count')}"
        )
    final_checkpoint = Path(str(metadata.get("final_checkpoint", "")))
    if not final_checkpoint.is_file():
        findings.append(f"final checkpoint missing: {final_checkpoint}")
    elif metadata.get("final_checkpoint_sha256") != sha256(final_checkpoint):
        findings.append("final checkpoint sha256 mismatch")
    else:
        notes.append("final checkpoint sha256 ok")

    for key in ["config", "train_log", "train_loss_csv", "profile_json"]:
        path_value = Path(str(metadata.get(key, "")))
        hash_key = f"{key}_sha256"
        if not path_value.is_file():
            findings.append(f"metadata path missing for `{key}`: {path_value}")
            continue
        actual_hash = sha256(path_value)
        if metadata.get(hash_key) != actual_hash:
            findings.append(f"{hash_key} mismatch for {path_value}")
        else:
            notes.append(f"{hash_key} ok")

    train_loss_csv = Path(str(metadata.get("train_loss_csv", "")))
    if train_loss_csv.is_file():
        rows = read_csv(train_loss_csv)
        if not rows:
            findings.append("train_loss.csv has no rows")
        else:
            last = rows[-1]
            if int(last.get("epoch", "-1")) != 120:
                findings.append(f"last train_loss epoch expected 120, found {last.get('epoch')}")
            if float(last.get("avg_loss", "nan")) != 1.369:
                findings.append(f"last train_loss avg_loss expected 1.369, found {last.get('avg_loss')}")
            notes.append(f"train_loss last row: epoch={last.get('epoch')} avg_loss={last.get('avg_loss')}")

    integrity_path = eval_run / "integrity.csv"
    if not integrity_path.is_file():
        findings.append(f"missing integrity csv: {integrity_path}")
    else:
        integrity_rows = read_csv(integrity_path)
        datasets = {row.get("dataset", "") for row in integrity_rows}
        if datasets != DATASETS:
            findings.append(f"integrity datasets expected {sorted(DATASETS)}, found {sorted(datasets)}")
        for row in integrity_rows:
            if row.get("gt_count") != row.get("pred_count"):
                findings.append(
                    f"integrity count mismatch for {row.get('dataset')}: "
                    f"gt={row.get('gt_count')} pred={row.get('pred_count')}"
                )
            if not Path(row.get("result_txt", "")).is_file():
                findings.append(f"integrity result_txt missing for {row.get('dataset')}: {row.get('result_txt')}")
        notes.append(f"integrity datasets: {','.join(sorted(datasets))}")

    metric_rows = [
        row for row in read_csv(metrics_csv)
        if row.get("exp_id") == EVAL_EXP_ID
    ] if metrics_csv.is_file() else []
    if {row.get("dataset", "") for row in metric_rows} != DATASETS:
        findings.append(f"metrics rows for {EVAL_EXP_ID} are not complete")
    if {row.get("status", "") for row in metric_rows} != {"final_main_light"}:
        findings.append(f"metrics status for {EVAL_EXP_ID} is not final_main_light")
    if {row.get("protocol", "") for row in metric_rows} != {"prob_map"}:
        findings.append(f"metrics protocol for {EVAL_EXP_ID} is not prob_map")
    notes.append(f"metrics rows for {EVAL_EXP_ID}: {len(metric_rows)}")

    profile_rows = [
        row for row in read_csv(profiles_csv)
        if row.get("exp_id") == PROFILE_EXP_ID
    ] if profiles_csv.is_file() else []
    if len(profile_rows) != 1:
        findings.append(f"profile row count for {PROFILE_EXP_ID} expected 1, found {len(profile_rows)}")
    else:
        profile = profile_rows[0]
        if profile.get("checkpoint_status") != "loaded":
            findings.append(f"profile checkpoint_status expected loaded, found {profile.get('checkpoint_status')}")
        if Path(profile.get("profile_json", "")).resolve() != Path(str(metadata.get("profile_json", ""))).resolve():
            findings.append("profile row profile_json does not match metadata")
        notes.append("profile row ok")

    status = "pass" if not findings else "fail"
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(
        "\n".join(
            [
                "# Light Final Metadata Audit",
                "",
                f"- Status: `{status}`",
                f"- Run dir: `{run_dir}`",
                f"- Eval run: `{eval_run}`",
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
    print(f"light_final_metadata_audit={status}")
    print(f"report={out_md}")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())

