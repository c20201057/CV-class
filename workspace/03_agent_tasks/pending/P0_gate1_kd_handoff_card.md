# P0 Gate 1 / KD Handoff Card

更新时间：2026-06-14T08:31:44Z / 2026-06-14 16:31:44 CST

## Purpose

This is the short handoff card for the next GPU queue operator. It does not
replace `GPU_QUEUE.md` or `gate_result_acceptance_runbook.md`; it exists so an
agent can avoid the two dangerous mistakes in one screen:

1. duplicating the completed Gate 1 baseline wrapper;
2. restarting the historical KD watcher or duplicating active KD recovery because KD is risky.

## Work Principle

不偷懒，不因为怕风险而保守。Do not skip clean baseline or KD just because they
are slow or risky. Also do not fake completion by promoting partial,
dirty-tree, historical, B0 or MobileMamba evidence into final paper claims.

## Current State To Assume Only After Refresh

Before acting, run:

```bash
python /root/data-tmp/workspace/02_experiments/scripts/orchestrator_tick.py
sed -n '1,120p' /root/data-tmp/workspace/00_project/orchestrator_tick_latest.md
sed -n '1,120p' /root/data-tmp/workspace/02_experiments/runs/mobilemamba_t2_external_status_latest.md
```

At the time this card was written:

- External `/root/ESCNet/all.sh` is stopped by user instruction. B0 is outside
  the active plan and remains a dirty-tree observation branch, not the clean
  baseline and not a main-paper result.
- B0 has an earlier completed COD10K observation series through epoch120. The
  latest completed row remains epoch120 S=.8004, wF=.6862, meanF=.7203,
  meanE=.8878, MAE=.0350; the best observed row remains epoch100 S=.8014,
  wF=.6882, meanF=.7221, meanE=.8899, MAE=.0346. The live rerun state is
  delegated to `b0_external_status_latest.md`.
- MobileMamba-T2 is not observed running in the current tick. Its latest and
  highest-S COD10K observation row is epoch50 S=.7487, wF=.6019,
  meanF=.6482, meanE=.8477, MAE=.0465. Its evidence boundary is
  `external_dirty_tree_observation_only`, and it has no accepted checkpoint.
- Gate 1 clean baseline is complete: CAMO/COD10K/NC4K are all present in
  `metrics_all.csv` with `status=clean_prob_re_eval_complete`.
- The baseline and resume watchers are no longer required. Keep the historical
  marker `resume_stopped_prob_eval_when_gpu_idle.sh` only for traceability; do
  not restart it unless Gate 1 evidence regresses and the main controller
  explicitly approves.
- The Gate 2 KD watcher has completed its handoff and should stay absent while
  KD recovery is running. Do not restart `watch_baseline_then_start_kd.sh`.
  Current active KD recovery is fast-shm four-GPU PID 838519, config
  `config_resume_epoch10_fast_shm_4gpu.yaml`, active log
  `/dev/shm/escnet_fast_kd/logs/train_resume_epoch10_fast_shm_4gpu_20260614T090334Z.log`;
  it resumed from epoch10 train state with `loaded_epoch=10, start_epoch=11`,
  writes data/output on `/dev/shm`, and has no final KD checkpoint yet.

## Do Not Do

- Do not restart the external B0 rerun or B0 watcher; if B0 training resurrects,
  follow the user's current scope and stop only B0-related process groups.
- Do not manually start another baseline wrapper now that Gate 1 is complete.
- Do not restart `watch_baseline_then_start_kd.sh` or start a duplicate KD run
  while the current four-GPU recovery is active.
- Do not use `/root/ESCNet/checkpoints/escnet/epoch_120.pth` as teacher or main
  baseline.
- Do not write large outputs outside `/root/data-tmp/workspace` or
  `/root/data-tmp/tmp`.
- Do not put B0 or MobileMamba into the main table, abstract or conclusion.

## When The Active KD Recovery Changes State

1. Refresh `orchestrator_tick.py`.
2. Confirm whether active `torchrun|train.py|test.py|infer_prob.py` processes
   are the current KD recovery or an unexpected external branch.
3. Confirm Gate 1 is still complete with three `clean_prob_re_eval_complete`
   rows. If it is complete, do not run `start_baseline_prob_eval_clean.sh`.
4. If KD recovery is still running, monitor log/checkpoints only. If it failed,
   preserve logs and ask the main controller before a new four-GPU launch; keep
   `watch_baseline_then_start_kd.sh` as a historical marker, not the default
   next action.

## Gate 1 Acceptance

Gate 1 can upgrade ESCNet-B5 from historical reference to fixed-baseline
probability result only after all of these are true:

- CAMO/COD10K/NC4K result files exist.
- `check_run_integrity.py` passes for
  `baseline_escnet_b5_clean_prob_e120`.
- `metrics_all.csv` has three rows with `status=clean_prob_re_eval_complete`.
- release audit passes.

Current status: Gate 1 passes these conditions. If any item later regresses,
write only Gate 1 progress and do not start KD until the baseline is repaired.

## Gate 2 KD Recovery

After Gate 1 passes, KD recovery uses this command only when GPUs are idle and
no active recovery exists:

```bash
TMPDIR=/root/data-tmp/tmp bash /root/data-tmp/workspace/02_experiments/scripts/start_kd_full_train.sh
```

Default KD recovery:

- code: `/root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64`
- checkpoint: `/dev/shm/escnet_fast_kd/checkpoints/latest_train_state_epoch_10.pth`
- active attempt: four GPUs, per-GPU batch 4, workers 4, save_step 20, `/dev/shm` data/output
- if SIGKILL repeats: preserve logs, then decide between two GPUs, one GPU, or offline KD
- current active attempt: fast-shm four GPUs, PID 838519, log `/dev/shm/escnet_fast_kd/logs/train_resume_epoch10_fast_shm_4gpu_20260614T090334Z.log`

KD must either produce a full three-dataset probability evaluation or be written
as an honest negative/failed engineering result. Do not silently drop it.

## Required Report

Write your report to:

```text
/root/data-tmp/workspace/03_agent_tasks/reports/P0_gate1_kd_handoff_card.md
```

Use this format:

```text
任务 ID / 实验 ID:
完成状态: pass / partial / fail
GPU 状态:
Gate 1 wrapper / watcher 状态:
Gate 2 KD watcher 状态:
使用命令:
新增或修改文件:
新增 metrics/profile/status:
完整性检查:
release audit:
仍禁止写入论文的内容:
下一步:
```
