# P0 Task: GPU Queue Operator And Gate Validator

## Agent Role

GPU 队列接管与 gate 验收 agent。

## Goal

按权威队列推进论文定稿前的关键 gate。当前占卡任务以 `orchestrator_tick_latest.md/json` 为准；最近状态是授权的 Gate 2 KD 四卡 recovery，而不是 clean baseline、B0 或 MobileMamba 主线。

1. Gate 1 clean ESCNet-B5 三数据集 probability baseline 已完成，负责复核而不是重复启动。
2. KD Light-B2-C64 从 `epoch_5.pth` 恢复完整训练与三数据集 probability eval。
3. 空闲 GPU 同条件 latency/FPS re-profile。

## Work Principle

不偷懒，不因为怕风险而保守。不要因为 KD 或 clean baseline 复评麻烦就跳过，也不要为了显得完成而把 partial、dirty-tree 或 historical evidence 写成 final evidence。

## Must Read First

- `/root/data-tmp/workspace/03_agent_tasks/prompts/MASTER_TARGET_PROMPT.md`
- `/root/data-tmp/workspace/02_experiments/scripts/GPU_QUEUE.md`
- `/root/data-tmp/workspace/04_paper/drafts/finalization_gates.md`
- `/root/data-tmp/workspace/04_paper/drafts/submission_protocol_checklist.md`
- `/root/data-tmp/workspace/03_agent_tasks/acceptance/gate_result_acceptance_runbook.md`
- `/root/data-tmp/workspace/00_project/orchestrator_tick_latest.md`
- `/root/data-tmp/workspace/00_project/orchestrator_tick_latest.json`
- `/root/data-tmp/workspace/02_experiments/runs/b0_external_status_latest.md`
- `/root/data-tmp/workspace/02_experiments/runs/mobilemamba_t2_external_status_latest.md`
- `/root/data-tmp/workspace/00_project/orchestrator_status.md`
- `/root/data-tmp/workspace/00_project/resume_handoff.md`

## Current Boundaries

- `/root/ESCNet` 当前是 dirty 外部探索工作树，不是 clean baseline。
- Clean baseline 固定为 `/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean`。
- ESCNet-B5 teacher checkpoint 固定为 `/root/data-tmp/epoch_120.pth`。
- 不得使用 `/root/ESCNet/checkpoints/escnet/epoch_120.pth` 作为 teacher 或主 baseline。
- 大文件、日志和 `TMPDIR` 必须放在 `/root/data-tmp/workspace` 或 `/root/data-tmp/tmp`。
- 现有 watcher 存活时不要重复启动 watcher；先读 PID 和日志。
- Gate 1 当前为 complete：`metrics_all.csv` 中 `baseline_escnet_b5_clean_prob_e120`
  的 CAMO/COD10K/NC4K 三行均为 `clean_prob_re_eval_complete`。不要重复运行
  `start_baseline_prob_eval_clean.sh`。
- 当前外部 B0 rerun 已按用户要求停止；早前 B0 epoch120 观察行共享 dirty 输出路径。它仍是
  `external_dirty_tree_observation_only`，不能进入主表、摘要或结论。
- 当前 Gate 2 KD 四卡 recovery 若仍在运行，不要重启 `watch_baseline_then_start_kd.sh` 或重复调用 `start_kd_full_train.sh`；只监控 active log/checkpoints。

## Inputs

- B0 one-click observation sync: `/root/data-tmp/workspace/02_experiments/scripts/sync_b0_observation_state.py`
- B0 low-level status script: `/root/data-tmp/workspace/02_experiments/scripts/summarize_external_b0.py`
- MobileMamba low-level status script: `/root/data-tmp/workspace/02_experiments/scripts/summarize_external_mobilemamba.py`
- KD recovery low-level status script: `/root/data-tmp/workspace/02_experiments/scripts/summarize_kd_recovery.py`
- Clean baseline launcher: `/root/data-tmp/workspace/02_experiments/scripts/start_baseline_prob_eval_clean.sh`
- KD recovery launcher: `/root/data-tmp/workspace/02_experiments/scripts/start_kd_full_train.sh`
- Probability eval suite: `/root/data-tmp/workspace/02_experiments/scripts/run_prob_eval_suite.sh`
- Release audit wrapper: `/root/data-tmp/workspace/02_experiments/scripts/run_release_audits.sh`

## Output

Allowed write scope:

- `/root/data-tmp/workspace/02_experiments/runs/baseline_escnet_b5_clean_prob_e120/`
- `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_recover_b2w0_4gpu/`
- `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_recover_b2w0_4gpu_prob_eval/`
- New profile run directories under `/root/data-tmp/workspace/02_experiments/runs/`
- `/root/data-tmp/workspace/03_agent_tasks/reports/P0_gpu_queue_operator.md`

Do not modify `/root/ESCNet` unless the main orchestrator explicitly changes the boundary.

## Execution Order

1. Read `orchestrator_tick_latest.md/json`, then refresh current state. For routine B0 observation use:

```bash
python /root/data-tmp/workspace/02_experiments/scripts/sync_b0_observation_state.py \
  --skip_release_audit
```

If a new B0 checkpoint or new COD10K intermediate row appeared, or before report/handoff, run the full sync:

```bash
python /root/data-tmp/workspace/02_experiments/scripts/sync_b0_observation_state.py
```

This sync is read-only with respect to training: it must not start, stop, or signal any train/eval process. After it, also capture `nvidia-smi` and process listing for the report.
For routine MobileMamba observation use:

```bash
python /root/data-tmp/workspace/02_experiments/scripts/summarize_external_mobilemamba.py
```

For routine KD recovery observation use:

```bash
python /root/data-tmp/workspace/02_experiments/scripts/summarize_kd_recovery.py
sed -n '1,160p' /root/data-tmp/workspace/02_experiments/runs/kd_recovery_status_latest.md
```

2. If authorized KD recovery is running, monitor it and do not duplicate it. If external B0 or MobileMamba unexpectedly occupies GPUs, report status; B0 is outside the current plan and should not be restarted.
3. Gate 1 is already complete. Keep `resume_stopped_prob_eval_when_gpu_idle.sh`
   as a historical marker in reports, but do not restart it or duplicate the
   baseline wrapper unless the main controller confirms Gate 1 evidence has
   regressed.
4. Gate 1 acceptance requires `clean_prob_re_eval_complete`, three datasets, integrity pass, and release audit pass.
   After any Gate 1/2/3/4 result changes state, follow `/root/data-tmp/workspace/03_agent_tasks/acceptance/gate_result_acceptance_runbook.md` before editing paper-facing conclusions.
5. If `orchestrator_tick_latest.md` reports KD recovery running, do not restart the
   KD watcher and do not duplicate `start_kd_full_train.sh` or
   `start_kd_fast_shm_train.sh`. Monitor the active recovery log/checkpoints
   instead. The current active recovery is expected to use the fast-shm four-GPU
   config `config_resume_epoch10_fast_shm_4gpu.yaml`. If KD
   recovery is not running, Gate 2 is still pending, and no final checkpoint
   exists, do not automatically restart the historical handoff watcher; first
   ask the main controller whether to launch the four-GPU recovery directly or
   to restore watcher-based handoff. Historical watcher command, for traceability:

```bash
TMPDIR=/root/data-tmp/tmp nohup /root/data-tmp/workspace/02_experiments/scripts/watch_baseline_then_start_kd.sh \
  --poll_seconds 120 \
  > /root/data-tmp/workspace/02_experiments/runs/watch_baseline_then_start_kd.nohup.log 2>&1 &
```

6. If a fresh launch is explicitly needed, it should run release checks, confirm
   GPU idle, and then invoke KD recovery:

```bash
TMPDIR=/root/data-tmp/tmp bash /root/data-tmp/workspace/02_experiments/scripts/start_kd_full_train.sh
```

7. If four-card batch2 workers0 KD fails again, do not abandon KD. Follow `kd_interruption_analysis.md` and downgrade to two-card then one-card recovery, preserving logs.
8. After KD checkpoint is complete, run probability eval exactly as specified in `GPU_QUEUE.md`.
9. Run same-command idle speed profile only when no training/eval process is active.

## Acceptance

1. No duplicated watcher or overlapping `torchrun|train.py` launch.
2. Clean baseline results use the clean snapshot and `/root/data-tmp/epoch_120.pth`.
3. `metrics_all.csv` rows include `protocol`, `repo_boundary`, `checkpoint`, and `status`.
4. Each final probability eval run passes `check_run_integrity.py`.
5. `run_release_audits.sh` passes after every gate update.
6. KD failure, if repeated, is reported with command, log path, checkpoint state, and next downgrade attempted.
7. No partial KD/B0/MobileMamba result is written into the main paper table.

## Report Template

```text
任务 ID / 实验 ID:
完成状态: pass / partial / fail
GPU 空闲证据:
启动或未启动原因:
使用命令:
写入或修改文件:
新增 metrics/profile/status:
完整性检查结果:
release audit 结果:
风险和异常:
是否可入论文: yes / no / only as reference / only as failure analysis
下一步:
```
