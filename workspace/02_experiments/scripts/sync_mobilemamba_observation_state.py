#!/usr/bin/env python3
"""Refresh MobileMamba-T2 observation docs and non-GPU gates.

This is a read-only synchronizer for the external dirty-tree MobileMamba-T2
branch. It does not start, stop, signal, evaluate, profile, or train a model.
It only:

1. refreshes the MobileMamba status markdown;
2. propagates the latest/best COD10K observation row into internal control docs;
3. refreshes the orchestrator tick and consistency audits.
"""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


WORKSPACE = Path("/root/data-tmp/workspace")
SCRIPTS = WORKSPACE / "02_experiments" / "scripts"
PAPER_SCRIPTS = WORKSPACE / "04_paper" / "scripts"
RUNS = WORKSPACE / "02_experiments" / "runs"
DEFAULT_RESULT = Path("/root/data-tmp/results_train/mobilemamba_t2/result.txt")
DEFAULT_STATUS = RUNS / "mobilemamba_t2_external_status_latest.md"
DEFAULT_REPORT = RUNS / "mobilemamba_observation_sync_latest.md"


@dataclass(frozen=True)
class ResultRow:
    epoch: int
    s: str
    wf: str
    mean_f: str
    mean_e: str
    mae: str

    @property
    def dotted(self) -> str:
        return (
            f"epoch{self.epoch} COD10K S={_dot(self.s)}, wF={_dot(self.wf)}, "
            f"meanF={_dot(self.mean_f)}, meanE={_dot(self.mean_e)}, MAE={_dot(self.mae)}"
        )

    @property
    def slash(self) -> str:
        return (
            f"epoch{self.epoch} COD10K S={_dot(self.s)}/wF={_dot(self.wf)}/"
            f"meanF={_dot(self.mean_f)}/meanE={_dot(self.mean_e)}/MAE={_dot(self.mae)}"
        )

    @property
    def paren(self) -> str:
        return (
            f"epoch{self.epoch}（S={_dot(self.s)}、wF={_dot(self.wf)}、"
            f"meanF={_dot(self.mean_f)}、meanE={_dot(self.mean_e)}、MAE={_dot(self.mae)}）"
        )


@dataclass(frozen=True)
class DocPatch:
    rel_path: str
    pattern: str
    replacement: str
    flags: int = re.MULTILINE
    required: bool = True


@dataclass(frozen=True)
class Step:
    name: str
    cmd: list[str]


def _dot(value: str) -> str:
    return value[1:] if value.startswith("0.") else value


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def read_results(path: Path) -> list[ResultRow]:
    if not path.is_file():
        raise FileNotFoundError(f"missing result CSV: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        rows = []
        for item in csv.DictReader(handle):
            rows.append(
                ResultRow(
                    epoch=int(item["epoch"]),
                    s=item["Smeasure"],
                    wf=item["wFmeasure"],
                    mean_f=item["meanFm"],
                    mean_e=item["meanEm"],
                    mae=item["MAE"],
                )
            )
    if not rows:
        raise ValueError(f"empty result CSV: {path}")
    return rows


def checkpoint_phrase(status_text: str) -> str:
    if "- Checkpoint status: `present`" in status_text:
        return "checkpoint present; candidate snapshot/load/profile/probability eval still required"
    return "checkpoint 仍 absent"


def epoch_list(rows: list[ResultRow]) -> str:
    return "/".join(str(row.epoch) for row in rows)


def now_strings() -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    utc = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    cst = (now + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S CST")
    return utc, cst


def update_timestamp(text: str, utc: str, cst: str) -> str:
    return re.sub(r"^更新时间：.*$", f"更新时间：{utc} / {cst}", text, count=1, flags=re.MULTILINE)


def build_doc_patches(rows: list[ResultRow], best: ResultRow, latest: ResultRow, ckpt: str) -> list[DocPatch]:
    latest_best = latest if latest.epoch == best.epoch else best
    latest_best_phrase = latest_best.dotted
    latest_best_slash = latest_best.slash
    epochs = epoch_list(rows)
    checkpoint_cn = "checkpoint 仍 absent" if "absent" in ckpt else "checkpoint 已出现但仍未候选验收"

    return [
        DocPatch(
            "00_project/route_decision.md",
            r"当前调度判断：B0/MobileMamba 不应抢占 Gate 1 clean baseline 和 Gate 2 KD 的优先级。.*?这些外部分支只作为极限压缩或替代主干风险分析候选，不替代 clean baseline、KD 和同条件速度复测这些主论文证据。",
            "当前调度判断：B0/MobileMamba 不应抢占 Gate 1 clean baseline 和 Gate 2 KD 的优先级。"
            "它们仍保留候选验收入口，体现“不因风险保守”的探索原则；但 B0 最终 epoch120 COD10K 未出现接近 Light-B2-C64 的强反转。"
            f"MobileMamba 仍在训练且无已验收候选 checkpoint，最新且最高 S 的 COD10K 中间观察行为 {latest_best_phrase}；"
            "实时训练进度继续委托 tick/status。MobileMamba 证据边界为 `external_dirty_tree_observation_only`。"
            "因此这些外部分支只作为极限压缩或替代主干风险分析候选，不替代 clean baseline、KD 和同条件速度复测这些主论文证据。",
            flags=re.DOTALL,
        ),
        DocPatch(
            "00_project/orchestrator_status.md",
            r"^- MobileMamba-T2 实时 epoch/iter 以 `orchestrator_tick_latest\.md` 和状态报告为准；.*$",
            f"- MobileMamba-T2 实时 epoch/iter 以 `orchestrator_tick_latest.md` 和状态报告为准；最新且最高 S 的观察行是 {latest_best_phrase}，{checkpoint_cn}。",
        ),
        DocPatch(
            "00_project/orchestrator_status.md",
            r"MobileMamba epoch[0-9/]+ COD10K 中间 eval 已落表但仍只是 dirty-tree observation",
            f"MobileMamba epoch{epochs} COD10K 中间 eval 已落表但仍只是 dirty-tree observation",
            required=False,
        ),
        DocPatch(
            "00_project/resume_handoff.md",
            r"^- MobileMamba-T2 实时 epoch/iter 以 `orchestrator_tick_latest\.md` 和状态报告为准；.*$",
            f"- MobileMamba-T2 实时 epoch/iter 以 `orchestrator_tick_latest.md` 和状态报告为准；最新且最高 S 的观察行是 {latest_best_phrase}，{checkpoint_cn}。",
        ),
        DocPatch(
            "00_project/current_run_snapshot.md",
            r"- MobileMamba 实时 epoch/iter 进度以 `orchestrator_tick_latest\.md` 和\n  `mobilemamba_t2_external_status_latest\.md` 为准；.*?$",
            "- MobileMamba 实时 epoch/iter 进度以 `orchestrator_tick_latest.md` 和\n"
            f"  `mobilemamba_t2_external_status_latest.md` 为准；本文件不硬编码 live 迭代数。最新且最高 S 的观察行是 {latest_best_phrase}，{checkpoint_cn}。",
            flags=re.MULTILINE | re.DOTALL,
        ),
        DocPatch(
            "00_project/goal_completion_matrix.md",
            r"\| MobileMamba risk branch \| .*? \| observation_only Gate 4B \| checkpoint 后候选 snapshot/load/profile/三数据集 eval \|",
            f"| MobileMamba risk branch | running, epoch{latest_best.epoch} latest/best COD10K row, no accepted checkpoint | observation_only Gate 4B | checkpoint 后候选 snapshot/load/profile/三数据集 eval |",
        ),
        DocPatch(
            "00_project/goal_completion_matrix.md",
            r"^- MobileMamba latest.*$",
            f"- MobileMamba latest and best observed row: {latest_best_phrase}; still no accepted checkpoint。",
        ),
        DocPatch(
            "02_experiments/scripts/GPU_QUEUE.md",
            r"MobileMamba-T2 实时 epoch/iter 以 `orchestrator_tick_latest\.md` 和 `mobilemamba_t2_external_status_latest\.md` 为准；.*?；证据边界为 `external_dirty_tree_observation_only`。",
            f"MobileMamba-T2 实时 epoch/iter 以 `orchestrator_tick_latest.md` 和 `mobilemamba_t2_external_status_latest.md` 为准；最新且最高 S 的观察行是 {latest_best_phrase}，{checkpoint_cn}；证据边界为 `external_dirty_tree_observation_only`。",
        ),
        DocPatch(
            "03_agent_tasks/task_board.md",
            r"^\| P1 \| MobileMamba-T2 online KD external branch \|.*$",
            f"| P1 | MobileMamba-T2 online KD external branch | external/main | `/root/data-tmp/ESCNet/checkpoints/mobilemamba_t2`; `external_dirty_tree_observation_only`; currently occupying four GPUs; live epoch/iter delegated to `orchestrator_tick_latest.md` and `mobilemamba_t2_external_status_latest.md`; MobileMamba latest/highest-S observation row is {latest_best_slash}; no accepted checkpoint yet |",
        ),
        DocPatch(
            "03_agent_tasks/pending/P0_gate1_kd_handoff_card.md",
            r"- MobileMamba-T2 is a dirty-tree observation branch; read its live epoch/iter\n  from `orchestrator_tick_latest\.md`\. Its latest/highest-S observation row is\n  .*?\n  Its evidence boundary is `external_dirty_tree_observation_only`\.",
            "- MobileMamba-T2 is a dirty-tree observation branch; read its live epoch/iter\n"
            f"  from `orchestrator_tick_latest.md`. Its latest/highest-S observation row is\n  {latest_best.dotted}.\n"
            "  Its evidence boundary is `external_dirty_tree_observation_only`.",
            flags=re.DOTALL,
        ),
        DocPatch(
            "04_paper/drafts/evidence_index.md",
            r"^- 当前 checkpoint/result：checkpoint .*?MobileMamba latest.*$",
            f"- 当前 checkpoint/result：{checkpoint_cn}；MobileMamba latest/highest-S epoch{latest_best.epoch} COD10K 中间 eval 已落表，S={_dot(latest_best.s)}、wF={_dot(latest_best.wf)}、meanF={_dot(latest_best.mean_f)}、meanE={_dot(latest_best.mean_e)}、MAE={_dot(latest_best.mae)}。",
        ),
        DocPatch(
            "04_paper/drafts/finalization_gates.md",
            r"^- MobileMamba-T2 只读 watcher 日志为 `02_experiments/runs/watch_external_mobilemamba_progress\.log`；.*$",
            f"- MobileMamba-T2 只读 watcher 日志为 `02_experiments/runs/watch_external_mobilemamba_progress.log`；实时 epoch/iter 以 tick/status 为准且 {checkpoint_cn}。当前已落表的最新/最佳 COD10K 中间 eval 为 {latest_best.paren}，证据边界为 `external_dirty_tree_observation_only`，因此只能作为替代轻量主干路线观察。",
        ),
        DocPatch(
            "04_paper/drafts/paper_claim_evidence_matrix.md",
            r"\| C13 \| .*? \| `/root/data-tmp/workspace/02_experiments/runs/mobilemamba_t2_external_status_latest\.md`;.*? \| 4\.6、4\.8 或工程备注 \| observation only \|",
            f"| C13 | MobileMamba-T2 外部分支正在 dirty `/root/ESCNet` 中四卡训练；当前只作为替代轻量主干观察。最新且最高 S 的 COD10K 观察行是 epoch{latest_best.epoch} S={_dot(latest_best.s)}/wF={_dot(latest_best.wf)}/meanF={_dot(latest_best.mean_f)}/meanE={_dot(latest_best.mean_e)}/MAE={_dot(latest_best.mae)}；最新状态以 live status 为准，未完成候选 checkpoint 验证、profile、三数据集评估和完整性检查前，不能入主表或摘要。 | `/root/data-tmp/workspace/02_experiments/runs/mobilemamba_t2_external_status_latest.md`; `/root/data-tmp/workspace/02_experiments/runs/watch_external_mobilemamba_progress.log`; `/root/data-tmp/workspace/02_experiments/scripts/start_mobilemamba_candidate_eval.sh`; `/root/data-tmp/workspace/02_experiments/scripts/snapshot_external_mobilemamba_dirty_tree.sh`; `/root/data-tmp/ESCNet/checkpoints/mobilemamba_t2` | 4.6、4.8 或工程备注 | observation only |",
        ),
        DocPatch(
            "04_paper/drafts/paper_submission_readiness.md",
            r"\| MobileMamba-T2 branch \|.*? \| observation only \| not in main table; possible engineering note after Gate 4B \|.*?\|",
            f"| MobileMamba-T2 branch | external dirty `/root/ESCNet` run is currently training; live epoch/iter delegated to `orchestrator_tick_latest.md` and `mobilemamba_t2_external_status_latest.md`; no accepted checkpoint yet; MobileMamba latest/highest-S epoch{latest_best.epoch} COD10K row is S={_dot(latest_best.s)}/wF={_dot(latest_best.wf)}/meanF={_dot(latest_best.mean_f)}/meanE={_dot(latest_best.mean_e)}/MAE={_dot(latest_best.mae)}; candidate eval wrapper and snapshot script are ready | observation only | not in main table; possible engineering note after Gate 4B | do not preempt Gate 1/KD for MobileMamba candidate eval; verify checkpoint load/profile with `start_mobilemamba_candidate_eval.sh` only as Gate 4B appendix/failure-analysis evidence |",
        ),
        DocPatch(
            "04_paper/drafts/paper_submission_readiness.md",
            r"MobileMamba epoch\d+/latest/highest-S observation row",
            f"MobileMamba epoch{latest_best.epoch}/latest/highest-S observation row",
            required=False,
        ),
        DocPatch(
            "04_paper/drafts/paper_submission_packet.md",
            r"- 当前占用四卡的是同一 dirty `/root/ESCNet/all\.sh` 后续启动的 MobileMamba-T2\n  online KD observation branch；.*?不能进入主表或摘要。",
            "- 当前占用四卡的是同一 dirty `/root/ESCNet/all.sh` 后续启动的 MobileMamba-T2\n"
            f"  online KD observation branch；实时 epoch/iter 委托 `orchestrator_tick_latest.md`，最新且最高 S 的 epoch{latest_best.epoch} COD10K 中间行为\n"
            f"  S={_dot(latest_best.s)}、wF={_dot(latest_best.wf)}、meanF={_dot(latest_best.mean_f)}、meanE={_dot(latest_best.mean_e)}、MAE={_dot(latest_best.mae)}。它仍未完成候选\n"
            "  checkpoint 验收、profile、三数据集 probability eval 和完整性检查，不能进入主表或摘要。",
            flags=re.DOTALL,
        ),
        DocPatch(
            "04_paper/drafts/writing_status.md",
            r"^- 外部 MobileMamba-T2 替代主干分支正在 dirty `/root/ESCNet` 中训练，占用四卡；.*$",
            f"- 外部 MobileMamba-T2 替代主干分支正在 dirty `/root/ESCNet` 中训练，占用四卡；实时 epoch/iter 以 `orchestrator_tick_latest.md` 和 `mobilemamba_t2_external_status_latest.md` 为准，{checkpoint_cn}；最新且最高 S 的 epoch{latest_best.epoch} COD10K 中间 eval 已落表，S={_dot(latest_best.s)}、wF={_dot(latest_best.wf)}、meanF={_dot(latest_best.mean_f)}、meanE={_dot(latest_best.mean_e)}、MAE={_dot(latest_best.mae)}。它的证据边界为 `external_dirty_tree_observation_only`，只能作为 Gate 4B observation candidate，不能进入主表、摘要或结论。",
        ),
        DocPatch(
            "03_agent_tasks/acceptance/agent_acceptance_ledger.md",
            r"^\| A21 \| Main orchestrator / MobileMamba external observation \|.*$",
            f"| A21 | Main orchestrator / MobileMamba external observation | `02_experiments/runs/mobilemamba_t2_external_status_latest.md`, `04_paper/drafts/mobilemamba_status_consistency_audit_latest.md`, `02_experiments/scripts/watch_external_mobilemamba_progress.sh` | accepted_reference_only | dirty-tree MobileMamba 正在训练；latest/highest-S epoch{latest_best.epoch} COD10K row 已记录，S={_dot(latest_best.s)}/wF={_dot(latest_best.wf)}/meanF={_dot(latest_best.mean_f)}/meanE={_dot(latest_best.mean_e)}/MAE={_dot(latest_best.mae)}；无已验收 checkpoint，状态一致性审计 pass；watcher 已支持未来重启时用 `--sync_on_change` 触发 observation sync | observation only，不进主表、摘要、结论 | 训练结束或 checkpoint 出现后才能 Gate 4B candidate；不抢占 Gate 1/Gate 2 主队列 |",
        ),
        DocPatch(
            "04_paper/drafts/paper_delivery_manifest.md",
            r"^- Gate 4B MobileMamba-T2: observation only;.*$",
            f"- Gate 4B MobileMamba-T2: observation only; epoch{latest_best.epoch} COD10K intermediate row is now the latest/highest-S observation, S={_dot(latest_best.s)}/wF={_dot(latest_best.wf)}/meanF={_dot(latest_best.mean_f)}/meanE={_dot(latest_best.mean_e)}/MAE={_dot(latest_best.mae)}, with no accepted checkpoint yet.",
        ),
    ]


def apply_doc_patches(patches: list[DocPatch], *, dry_run: bool) -> tuple[list[str], list[str]]:
    changed: list[str] = []
    notes: list[str] = []
    utc, cst = now_strings()

    for patch in patches:
        path = WORKSPACE / patch.rel_path
        if not path.is_file():
            message = f"missing target doc: {patch.rel_path}"
            if patch.required:
                raise FileNotFoundError(message)
            notes.append(message)
            continue

        text = read_text(path)
        text = update_timestamp(text, utc, cst)
        new_text, count = re.subn(patch.pattern, patch.replacement, text, count=1, flags=patch.flags)
        if count == 0:
            message = f"pattern not found in {patch.rel_path}"
            if patch.required:
                raise RuntimeError(message)
            notes.append(message)
            new_text = text

        if new_text != read_text(path):
            changed.append(patch.rel_path)
            if not dry_run:
                path.write_text(new_text, encoding="utf-8")

    return sorted(set(changed)), notes


def run_step(step: Step, *, dry_run: bool) -> None:
    print(f"\n==> {step.name}", flush=True)
    print("cmd=" + " ".join(step.cmd), flush=True)
    if dry_run:
        return
    subprocess.run(step.cmd, check=True)


def write_report(
    *,
    out_md: Path,
    status: str,
    latest: ResultRow,
    best: ResultRow,
    changed: list[str],
    notes: list[str],
    steps: list[Step],
) -> None:
    out_md.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# MobileMamba Observation Sync",
        "",
        f"- Status: `{status}`",
        f"- Updated UTC: `{now_strings()[0]}`",
        f"- Latest row: `{latest.slash}`",
        f"- Best-S row: `{best.slash}`",
        "- Boundary: `external_dirty_tree_observation_only`",
        "",
        "## Changed Docs",
        "",
        *([f"- `{item}`" for item in changed] or ["- none"]),
        "",
        "## Notes",
        "",
        *([f"- {item}" for item in notes] or ["- none"]),
        "",
        "## Steps",
        "",
        *[f"- {step.name}: `{' '.join(step.cmd)}`" for step in steps],
    ]
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", default=str(DEFAULT_RESULT))
    parser.add_argument("--status_md", default=str(DEFAULT_STATUS))
    parser.add_argument("--out_md", default=str(DEFAULT_REPORT))
    parser.add_argument(
        "--skip_release_audit",
        "--skip-release-audit",
        action="store_true",
        help="Skip the full release audit after MobileMamba-specific checks.",
    )
    parser.add_argument(
        "--dry_run",
        "--dry-run",
        action="store_true",
        help="Print planned commands and patches without writing files.",
    )
    args = parser.parse_args()

    steps = [
        Step("refresh_external_mobilemamba_status", ["python", str(SCRIPTS / "summarize_external_mobilemamba.py")]),
    ]

    try:
        for step in steps:
            run_step(step, dry_run=args.dry_run)

        rows = read_results(Path(args.result).expanduser().resolve())
        latest = max(rows, key=lambda row: row.epoch)
        best = max(rows, key=lambda row: float(row.s))
        status_text = read_text(Path(args.status_md).expanduser().resolve())
        patches = build_doc_patches(rows, best=best, latest=latest, ckpt=checkpoint_phrase(status_text))
        changed, notes = apply_doc_patches(patches, dry_run=args.dry_run)

        audit_steps = [
            Step("refresh_orchestrator_tick", ["python", str(SCRIPTS / "orchestrator_tick.py"), "--no_refresh_mobilemamba"]),
            Step("audit_mobilemamba_status_consistency", ["python", str(SCRIPTS / "audit_mobilemamba_status_consistency.py")]),
            Step("audit_gpu_handoff_consistency", ["python", str(SCRIPTS / "audit_gpu_handoff_consistency.py")]),
            Step("audit_route_decision_consistency", ["python", str(SCRIPTS / "audit_route_decision_consistency.py")]),
            Step("audit_goal_completion_matrix", ["python", str(SCRIPTS / "audit_goal_completion_matrix.py")]),
            Step("audit_paper_delivery_manifest", ["python", str(PAPER_SCRIPTS / "audit_paper_delivery_manifest.py")]),
            Step("audit_claim_evidence_matrix", ["python", str(PAPER_SCRIPTS / "audit_claim_evidence_matrix.py")]),
            Step("audit_submission_protocol", ["python", str(PAPER_SCRIPTS / "audit_submission_protocol.py")]),
            Step("audit_agent_acceptance_ledger", ["python", str(WORKSPACE / "03_agent_tasks/acceptance/audit_agent_acceptance_ledger.py")]),
            Step("audit_task_board_consistency", ["python", str(WORKSPACE / "03_agent_tasks/audit_task_board_consistency.py")]),
        ]
        if not args.skip_release_audit:
            audit_steps.append(Step("run_release_audits", ["bash", str(SCRIPTS / "run_release_audits.sh")]))

        for step in audit_steps:
            run_step(step, dry_run=args.dry_run)
        all_steps = steps + audit_steps
        write_report(
            out_md=Path(args.out_md).expanduser().resolve(),
            status="pass",
            latest=latest,
            best=best,
            changed=changed,
            notes=notes,
            steps=all_steps,
        )
    except (subprocess.CalledProcessError, OSError, RuntimeError, ValueError) as exc:
        print(f"sync_mobilemamba_observation_state=fail error={exc}", file=sys.stderr)
        return getattr(exc, "returncode", 1) or 1

    print("\nsync_mobilemamba_observation_state=pass")
    print(f"status={Path(args.status_md).expanduser().resolve()}")
    print(f"report={Path(args.out_md).expanduser().resolve()}")
    print(f"latest={latest.slash}")
    print(f"best={best.slash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
