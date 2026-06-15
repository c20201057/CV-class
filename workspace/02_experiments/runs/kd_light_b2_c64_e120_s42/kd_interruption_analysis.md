# KD B2-C64 Interruption Analysis

更新时间：2026-06-13T16:20:30Z

本文件记录 `kd_light_b2_c64_e120_s42` 的长训中断事实、已完成修复和下一步恢复策略。结论先行：KD 代码链路已通过 smoke，但 full train 还没有可入论文的完整 checkpoint；当前唯一有效可恢复点是 `epoch_5.pth`。

## Run Paths

- 代码目录：`/root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64`
- 运行目录：`/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42`
- teacher checkpoint：`/root/data-tmp/epoch_120.pth`
- 基础配置：`config.yaml`
- workers=0 恢复配置：`config_resume_epoch5_workers0.yaml`
- 第一次 rerun 日志：`logs/train_ddp_rerun_session_20260613T1530Z.log`
- workers=0 恢复日志：`logs/train_ddp_resume_epoch5_workers0_20260613T1554Z.log`
- 四卡 batch2 recovery config：`config_resume_epoch5_b2_workers0_4gpu.yaml`
- 双卡 batch2 recovery config：`config_resume_epoch5_b2_workers0_2gpu.yaml`
- 单卡 batch2 recovery config：`config_resume_epoch5_b2_workers0_1gpu.yaml`

## Completed Evidence

- GPU batch 1 smoke 通过，peak memory 约 2298.573 MB。
- GPU batch 4 smoke 通过，peak memory 约 6730.948 MB。
- 第一次 full train 曾完成 epoch 4，并在 epoch 5 iter 50 后被 SIGKILL。
- 第一次 rerun 成功保存 `epoch_1.pth` 至 `epoch_5.pth`，说明逐 epoch checkpoint 生效。
- `train.py` 已补充 resume 能力：
  - 可从 `resume` 指向的 `epoch_N.pth` 加载模型权重并推断 `start_epoch=N+1`。
  - 新保存 checkpoint 时额外写入 `latest_train_state.pth`，包含 model、optimizer、scheduler、scaler 和 epoch。
  - `python -m py_compile train.py` 已通过。
- `train.py` 单卡分支已移除内部强制设置 `CUDA_VISIBLE_DEVICES` 的行为，避免物理卡号与逻辑可见卡号重映射冲突；`python -m py_compile train.py` 已通过。
- Lagrange 已完成只读恢复配置审计：`/root/data-tmp/workspace/05_reviews/kd_recovery_config_audit.md`，主控已验收并据此新增三份降级恢复配置。

## Failure Timeline

| Time (UTC) | Attempt | Last Confirmed State | Failure |
| --- | --- | --- | --- |
| 2026-06-13 | original full train | epoch 5 iter 50, total loss 2.313 | rank0 SIGKILL |
| 2026-06-13T15:30Z | first rerun with per-epoch saves | `epoch_5.pth` saved; epoch 5 avg loss 2.805 | epoch 6 附近 DataLoader worker SIGKILL |
| 2026-06-13T15:54Z | resume from `epoch_5.pth`, `num_workers=0` | resumed with `loaded_epoch=5, start_epoch=6`; reached epoch 6 iter 100/252 | rank0 SIGKILL before epoch 6 checkpoint |

当前 checkpoint 清单：

| Checkpoint | Status |
| --- | --- |
| `epoch_1.pth` | partial KD checkpoint; not paper result |
| `epoch_2.pth` | partial KD checkpoint; not paper result |
| `epoch_3.pth` | partial KD checkpoint; not paper result |
| `epoch_4.pth` | partial KD checkpoint; not paper result |
| `epoch_5.pth` | latest valid recovery point; not paper result |
| `epoch_6.pth` | not produced |

## Resource Observations

- Root filesystem `/` is full; all new artifacts must remain under `/root/data-tmp` or `/root/data-tmp/tmp`.
- `/root/data-tmp` still has about 1.3T available.
- Cgroup memory evidence around the second failure:
  - `memory.current` about 97.9 GB.
  - `memory.max` about 266.3 GB.
  - `memory.events`: `oom=0`, `oom_kill=0`.
- This makes a container-level memory OOM less likely.
- Multiple external four-card jobs were observed around the same period. At the time of this note, `/root/ESCNet` is running an external PVTv2-B0 online KD job from `configs/pvt_v2_b0.yaml` using `torchrun --nproc_per_node=4 --master_port=29501`.

## Current Judgment

KD is still a valid experimental route, but it is not yet valid evidence for the paper. The correct paper boundary is:

- 可以写：online KD 工程链路已实现并通过 smoke；长训尝试暴露了四卡环境下的稳定性风险；当前保留 `epoch_5.pth` 作为恢复点。
- 不能写：KD 提升、KD 缩小精度差距、KD final metrics、KD 速度或资源收益。

## Recovery Strategy

Do not restart KD while another external four-card job is active. When GPUs are available, use the following escalation order:

1. Wait for the external B0 four-GPU job to finish. Do not compete with it.
2. First recovery attempt: four-GPU DDP, per-GPU `batch_size=2`, `num_workers=0`, resume from `epoch_5.pth`. This is now preferred over repeating batch4 because workers0 batch4 already failed.
3. If four-card batch2 still fails, reduce to two-GPU DDP, per-GPU `batch_size=2`, `num_workers=0`.
4. If DDP remains unstable, run a single-GPU continuation from `epoch_5.pth` with `batch_size=2` or `batch_size=1`. It will be slower, but it avoids elastic DDP killing all ranks after one rank exits.
5. If online teacher forward remains the bottleneck, switch to an offline KD design: generate teacher probability maps under a fixed no-random-transform protocol and train a deterministic KD variant. This will no longer match online random crop/rotate perfectly, so it should be reported as an engineering compromise.
6. If KD cannot complete within available wall time, keep it as an attempted compensation branch and write failure analysis honestly instead of claiming an unverified improvement.

## Prepared Recovery Commands

Four-GPU batch2:

```bash
cd /root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64
export TMPDIR=/root/data-tmp/tmp
/root/miniconda3/envs/escnet/bin/torchrun --nproc_per_node=4 --master_port=29505 train.py \
  --config /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config_resume_epoch5_b2_workers0_4gpu.yaml \
  2>&1 | tee -a /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/logs/train_resume_epoch5_b2w0_4gpu_$(date -u +%Y%m%dT%H%M%SZ).log
```

Two-GPU batch2:

```bash
cd /root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64
export TMPDIR=/root/data-tmp/tmp
/root/miniconda3/envs/escnet/bin/torchrun --nproc_per_node=2 --master_port=29506 train.py \
  --config /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config_resume_epoch5_b2_workers0_2gpu.yaml \
  2>&1 | tee -a /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/logs/train_resume_epoch5_b2w0_2gpu_$(date -u +%Y%m%dT%H%M%SZ).log
```

Single-GPU batch2:

```bash
cd /root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64
export TMPDIR=/root/data-tmp/tmp
/root/miniconda3/envs/escnet/bin/python train.py \
  --config /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config_resume_epoch5_b2_workers0_1gpu.yaml \
  2>&1 | tee -a /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/logs/train_resume_epoch5_b2w0_1gpu_$(date -u +%Y%m%dT%H%M%SZ).log
```

## Monitoring Commands

```bash
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader,nounits
ps -eo pid,ppid,stat,etime,rss,cmd | grep -E 'torchrun|train.py|run.sh' | grep -v grep
tail -n 80 /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/logs/train_ddp_resume_epoch5_workers0_20260613T1554Z.log
find /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42 -maxdepth 1 -name 'epoch_*.pth' -printf '%f %s bytes %TY-%Tm-%Td %TH:%TM\n' | sort -V
```
