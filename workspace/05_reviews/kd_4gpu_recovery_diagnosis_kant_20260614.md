# KD Four-GPU Recovery Diagnosis

更新时间：2026-06-14T07:38:39Z / 2026-06-14 15:38:39 CST

本文记录 Kant 只读诊断 subagent 与主控复核后的 Gate 2 KD 四卡恢复结论。它是工程/调度证据，不是 KD 性能结果；在完整 `epoch_120.pth`、三数据集 probability eval 和 integrity gate 完成前，不得写 KD 提升。

## Scope

- KD code: `/root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64`
- Four-GPU config: `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config_resume_epoch5_b2_workers0_4gpu.yaml`
- Failed four-GPU log: `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/logs/train_resume_epoch5_b2w0_4gpu_20260614T062550Z.log`
- Active recovery log: `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/logs/train_resume_epoch5_b2_workers0_4gpu_20260614T073026Z.log`
- Output run: `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_recover_b2w0_4gpu`

## Diagnosis

Kant and the main controller agreed that the previous four-GPU failure was a rank0 disappearance during model/DDP initialization, not a teacher checkpoint or resume-file error. The evidence is:

- Rank0's last old-log message was dataloader creation; no Python traceback was emitted.
- Rank1/2/3 failed while retrieving NCCL unique id from rank0 during DDP parameter verification.
- Single-GPU recovery loaded the same `epoch_5.pth` and teacher checkpoint successfully.
- A pure four-GPU NCCL all-reduce probe passed.
- A four-GPU KD student DDP-init probe passed after GPU idleness was confirmed.

The most likely root cause was process/runtime instability around rank0 under the previous launch context, amplified by root overlay space risk and sparse rank logging. It was not accepted as evidence that KD is invalid.

## Main-Controller Actions

- Added rank-level diagnostics and DDP cleanup to `kd_light_escnet_b2_c64/train.py`.
- Switched DDP wrapping to explicit `device_id` while preserving `config.device_ids`.
- Added `/root/data-tmp/tmp` cache/TMP isolation and PyTorch NCCL async handling to `start_kd_full_train.sh`.
- Added diagnostic probes:
  - `/root/data-tmp/workspace/02_experiments/scripts/probe_nccl_allreduce.py`
  - `/root/data-tmp/workspace/02_experiments/scripts/probe_kd_ddp_init.py`
- Verified:
  - `python -m py_compile` passed for KD train and probes.
  - `bash -n start_kd_full_train.sh` passed.
  - `audit_gpu_runtime_state.py` passed before launch.

## Current Recovery Evidence

The four-GPU recovery was launched through:

```bash
TMPDIR=/root/data-tmp/tmp bash /root/data-tmp/workspace/02_experiments/scripts/start_kd_full_train.sh
```

Launch evidence:

- PID: `806897`
- Config: `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config_resume_epoch5_b2_workers0_4gpu.yaml`
- Log: `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/logs/train_resume_epoch5_b2_workers0_4gpu_20260614T073026Z.log`

The active run has passed the previous failure region:

- `DDP wrap done` on all ranks.
- Resume loaded `epoch_5.pth`, `start_epoch=6`.
- Online B5 teacher loaded from `/root/data-tmp/epoch_120.pth`.
- Training entered `Epoch[6/120] Iter[0/505]`.
- Training reached `Epoch[6/120] Iter[100/505]` by 2026-06-14 15:36:54 CST.

## Paper Boundary

- Allowed now: KD online route is implemented, smoke-tested, diagnosed, and currently running under four-GPU recovery.
- Forbidden now: KD improves Light-B2-C64, KD narrows the clean-baseline gap, KD final metrics, KD speed, or KD model readiness.
- Gate 2 remains pending until final checkpoint, CAMO/COD10K/NC4K probability eval, integrity checks, and release audit pass.
