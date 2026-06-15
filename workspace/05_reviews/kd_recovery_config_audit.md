# KD Recovery Config Audit

审计时间：2026-06-14

审计角色：Lagrange，KD B2-C64 恢复训练降级方案审计

范围：只读审计 `/root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64/config.py`、`train.py`、`kd.py`、现有 KD run 配置和中断日志。不启动训练，不 kill 进程，不占 GPU。

## 结论先行

KD B2-C64 当前最新有效恢复点是：

`/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/epoch_5.pth`

现有 `config_resume_epoch5_workers0.yaml` 已经从 epoch 5 恢复并设置 `num_workers: 0`，但仍在 epoch 6 iter 100/252 后 rank0 SIGKILL。仅把 DataLoader workers 降到 0 不是充分修复。下一轮不应再直接用四卡 batch4；应按资源压力逐级降级：

1. A：四卡 DDP，per-GPU batch2，workers0。最接近原四卡协议，优先尝试。
2. B：双卡 DDP，per-GPU batch2，workers0。降低总 GPU/进程/teacher 驻留压力。
3. C：单卡，batch2；若仍不稳则 batch1，workers0。最稳但最慢，且训练协议偏移最大。

所有方案都应新建 YAML，不覆盖现有 `config.yaml` 和 `config_resume_epoch5_workers0.yaml`；日志写 fresh timestamp 文件，checkpoint 仍可写当前 KD run 目录，但要明确这是 resume continuation。

## 代码行为核查

### Config 校验

`config.py` 的 `Config` 直接校验以下字段：

- `batch_size`、`batch_size_valid` 必须大于 0。
- `num_workers` 必须大于等于 0。
- `resume` 是可空字符串；非空时由 `train.py` 负责检查文件存在。
- `device_ids` 是 int list。
- `multi_GPU` 默认 false。
- `is_ddp` 只在 `multi_GPU and len(device_ids) > 1` 时为 true。
- online KD 要求 `kd_teacher_config` 和 `kd_teacher_ckpt` 存在，且当前只支持 `kd_loss: mse`。

关键含义：`multi_GPU: true` 但 `device_ids` 只有一个元素时，`config.is_ddp` 为 false；但 `__main__` 仍会走 `if config.multi_GPU` 分支，不设置 `CUDA_VISIBLE_DEVICES`，因此单卡方案应明确使用 `multi_GPU: false`。

### Device 与 DDP

`train.py` 中 `Trainer.__init__` 使用：

- `self.device = self.config.device_ids[self.rank]`
- `torch.cuda.set_device(self.device)`

DDP 入口使用：

- rank 来自 `LOCAL_RANK`。
- `world_size = len(config.device_ids)`。
- `setup_ddp(rank, world_size)` 使用 NCCL。

关键含义：

- 四卡 DDP：`device_ids: [0,1,2,3]`，`torchrun --nproc_per_node=4`，每个 rank 分别用对应 device。
- 双卡 DDP：`device_ids: [0,1]`，`torchrun --nproc_per_node=2`，每个 rank 分别用 device 0/1。
- 单卡：必须 `multi_GPU: false`，建议 `device_ids: [0]`，用 `python train.py` 启动；代码会设置 `CUDA_VISIBLE_DEVICES=0`，然后 rank0 使用 device 0。

风险提示：如果单卡想用物理 GPU 2/3，当前代码会先设置 `CUDA_VISIBLE_DEVICES=2`，随后又 `torch.cuda.set_device(2)`；在可见设备被重映射后这可能越界。因此单卡配置建议只写 `device_ids: [0]`，外部不要再用不同 `CUDA_VISIBLE_DEVICES` 叠加映射，除非先改代码。由于本次禁止改代码，单卡推荐物理 0 或等待无人占用窗口。

### Batch Size 与有效 batch

DataLoader 使用：

- `batch_size=self.config.batch_size`
- DDP 时 `DistributedSampler(dataset)`
- 非 DDP 时普通 shuffle。

因此 `batch_size` 是每个进程/GPU 的本地 batch，不是全局 batch。

有效 batch：

- 原四卡 batch4：4 x 4 = 16。
- A 四卡 batch2：4 x 2 = 8。
- B 双卡 batch2：2 x 2 = 4。
- C 单卡 batch2：2。
- C 单卡 batch1：1。

学习率不会自动随有效 batch 缩放，仍使用 YAML 的 `lr: 0.000075`。这会改变优化动态；如果不改 lr，则是“恢复完成优先”的工程降级，不是严格同协议训练。

### Num Workers

DataLoader 实际使用：

`num_workers=min(config.num_workers, config.batch_size)`

因此：

- `num_workers: 0` 会彻底禁用 worker 子进程。
- `num_workers: 4, batch_size: 2` 实际只会用 2 个 workers/进程。
- 之前 workers0 仍失败，说明 DataLoader worker 不是唯一问题。

### Resume

`train.py` 的 resume 逻辑：

- 若 `resume` 为空，从 epoch 1 开始。
- 若 checkpoint 是 dict 且含 `"model"`，则可加载 model、optimizer、lr_scheduler、scaler，并读取 `"epoch"`。
- 若 checkpoint 是纯 state_dict，则只加载模型权重，并从文件名 `epoch_N.pth` 推断 `loaded_epoch=N`，从 `N+1` 开始。

当前 `epoch_5.pth` 大小约 115 MB，属于 rank0 保存的模型权重 checkpoint，不是 `latest_train_state.pth`。当前 run 目录未见 `latest_train_state.pth`。所以从 `epoch_5.pth` 恢复会从 epoch 6 开始，但 optimizer、scheduler、scaler 会重新初始化。

这不会阻止继续训练，但会造成学习率日程不连续：`CosineAnnealingLR(T_max=120)` 被重新初始化后，在 epoch6 处实际仍处于 scheduler 初始阶段。论文中若使用该 KD 结果，应记录“resumed from model weights at epoch 5; optimizer/scheduler state unavailable”。

### Online KD 资源占用

`kd.py` 的 `load_teacher` 会在每个 rank/device 上加载一份 ESCNet-B5 teacher。训练时每个 iteration：

1. student forward/backward。
2. teacher 在 `torch.no_grad()` 下对同一 batch forward。
3. student last mask 与 teacher last mask 做 MSE。

因此 DDP 下每张卡会同时驻留 student、teacher 和中间激活；虽然 teacher 不反传，但 online teacher forward 仍增加显存、计算和进程稳定性压力。四卡 batch4 已两次中断，batch2 是合理的下一档。

## 当前失败事实

已读现有配置和日志：

- 基础 config：`batch_size: 4`、`device_ids: [0,1,2,3]`、`multi_GPU: true`、`num_workers: 4`。
- `config_resume_epoch5_workers0.yaml`：`resume: epoch_5.pth`、`batch_size: 4`、`device_ids: [0,1,2,3]`、`multi_GPU: true`、`num_workers: 0`。
- workers0 恢复日志确认：`loaded_epoch=5, start_epoch=6`，epoch6 到 iter100/252 后 rank0 SIGKILL。
- 早前 rerun 日志还出现过 DataLoader worker killed 和 `.nfs... Device or resource busy`，但 workers0 后仍 SIGKILL，说明问题可能是 GPU/系统资源竞争、online KD 资源压力、DDP rank 级联失败或外部四卡任务干扰的组合。

## 恢复配置建议

以下配置均为建议新建文件，暂不启动。建议文件放在：

`/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/`

不要覆盖已有 `config.yaml`、`config_resume_epoch5_workers0.yaml`。

### A. 四卡 batch2 workers0

推荐优先级：第一优先。它保留四卡 DDP 和 SyncBatchNorm，只把每卡 batch 从 4 降到 2，有效 batch 从 16 降到 8。

建议新增：

`config_resume_epoch5_4gpu_b2_workers0.yaml`

相对 `config_resume_epoch5_workers0.yaml` 修改字段：

```yaml
batch_size: 2
resume: /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/epoch_5.pth
device_ids: [0, 1, 2, 3]
multi_GPU: true
num_workers: 0
save_model_dir: /root/data-tmp/workspace/02_experiments/runs
name: kd_light_b2_c64_e120_s42
save_last: 120
save_step: 1
```

其余字段保持与当前 KD run 一致，包括 `lr: 0.000075`、`kd_weight: 0.5`、`kd_warmup_epochs: 5`、`compile: false`。

建议命令：

```bash
mkdir -p /root/data-tmp/tmp /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/logs
cd /root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64
TMPDIR=/root/data-tmp/tmp torchrun --nproc_per_node=4 train.py \
  --config /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config_resume_epoch5_4gpu_b2_workers0.yaml \
  2>&1 | tee /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/logs/train_resume_epoch5_4gpu_b2_workers0_$(date -u +%Y%m%dT%H%M%SZ).log
```

风险：

- 有效 batch 从 16 降为 8，学习率未缩放，训练动态与原 batch4 四卡不完全一致。
- 每卡 batch2 下 SyncBatchNorm 汇总全局统计，BN 风险较低，但与原 effective batch16 仍不同。
- DDP 仍是四进程，任一 rank 被 SIGKILL 会导致全局失败。
- 仍与外部四卡任务互斥；必须等外部 B0 四卡训练结束后再跑。
- 写入同一 run 目录，会覆盖后续 `epoch_6.pth` 及之后 checkpoint；这不是污染旧有效 checkpoint，但必须保存独立日志和配置以标注恢复方案。

### B. 双卡 batch2 workers0

推荐优先级：第二优先。若四卡 batch2 仍不稳，双卡能减少 GPU 数、teacher 副本数、DDP rank 数和系统竞争面。

建议新增：

`config_resume_epoch5_2gpu_b2_workers0.yaml`

相对当前恢复配置修改字段：

```yaml
batch_size: 2
resume: /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/epoch_5.pth
device_ids: [0, 1]
multi_GPU: true
num_workers: 0
save_model_dir: /root/data-tmp/workspace/02_experiments/runs
name: kd_light_b2_c64_e120_s42
save_last: 120
save_step: 1
```

建议命令：

```bash
mkdir -p /root/data-tmp/tmp /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/logs
cd /root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64
TMPDIR=/root/data-tmp/tmp torchrun --nproc_per_node=2 train.py \
  --config /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config_resume_epoch5_2gpu_b2_workers0.yaml \
  2>&1 | tee /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/logs/train_resume_epoch5_2gpu_b2_workers0_$(date -u +%Y%m%dT%H%M%SZ).log
```

风险：

- 有效 batch 从原 16 降为 4，优化协议变化明显。
- SyncBatchNorm 仍启用，但全局 batch 只有 4，BN 统计噪声比四卡方案大。
- 训练时间约为四卡同 per-GPU batch 的两倍量级，且相比原四卡 batch4 更慢。
- 仍使用 DDP/elastic，rank 失败仍会级联，但 rank 数减少后稳定性可能提升。
- 若机器上外部任务占用任意目标 GPU，仍不能启动；本审计不建议通过 `CUDA_VISIBLE_DEVICES` 重映射，因为代码内部按 `device_ids` 直接 `torch.cuda.set_device`。
- 同一 run 目录写入 checkpoint，必须保留独立 config/log 以追踪协议变化。

### C. 单卡 batch2 或 batch1 workers0

推荐优先级：保底方案。目标是尽可能完成 KD continuation，代价是训练很慢且协议偏移最大。

建议新增 batch2 配置：

`config_resume_epoch5_1gpu_b2_workers0.yaml`

字段：

```yaml
batch_size: 2
resume: /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/epoch_5.pth
device_ids: [0]
multi_GPU: false
num_workers: 0
save_model_dir: /root/data-tmp/workspace/02_experiments/runs
name: kd_light_b2_c64_e120_s42
save_last: 120
save_step: 1
```

若 batch2 仍不稳，再新增：

`config_resume_epoch5_1gpu_b1_workers0.yaml`

字段：

```yaml
batch_size: 1
resume: /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/epoch_5.pth
device_ids: [0]
multi_GPU: false
num_workers: 0
save_model_dir: /root/data-tmp/workspace/02_experiments/runs
name: kd_light_b2_c64_e120_s42
save_last: 120
save_step: 1
```

建议命令，batch2：

```bash
mkdir -p /root/data-tmp/tmp /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/logs
cd /root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64
TMPDIR=/root/data-tmp/tmp python train.py \
  --config /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config_resume_epoch5_1gpu_b2_workers0.yaml \
  2>&1 | tee /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/logs/train_resume_epoch5_1gpu_b2_workers0_$(date -u +%Y%m%dT%H%M%SZ).log
```

建议命令，batch1：

```bash
mkdir -p /root/data-tmp/tmp /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/logs
cd /root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64
TMPDIR=/root/data-tmp/tmp python train.py \
  --config /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config_resume_epoch5_1gpu_b1_workers0.yaml \
  2>&1 | tee /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/logs/train_resume_epoch5_1gpu_b1_workers0_$(date -u +%Y%m%dT%H%M%SZ).log
```

风险：

- 有效 batch 只有 2 或 1，学习率仍为 0.000075 时优化动态变化最大；如严格追求稳定，后续可另审计是否把 lr 降到原来的 1/8 或 1/16，但这会进一步改变协议。
- 非 DDP 不会调用 `SyncBatchNorm.convert_sync_batchnorm`，模型中的普通 BN 只看单卡小 batch；batch1 的 BN 统计风险最高。
- 训练时间最长。按 epoch6 workers0 日志，四卡 batch4 约 10 分钟内跑到 iter100，单卡 batch1 可能非常慢，可能无法在课程时间内完成 115 个 epoch。
- 单卡代码路径会设置 `CUDA_VISIBLE_DEVICES=str(device_ids[0])`，因此建议使用 `device_ids: [0]`，不要用 `[1]`、`[2]`、`[3]` 这类物理卡编号，避免可见设备重映射后 `torch.cuda.set_device` 越界。
- 与四卡/双卡不同，`DistributedSampler` 不启用，shuffle 行为会不同。
- 仍写同一 run 目录，必须用独立 YAML 与日志记录这是 single-GPU continuation。

## 是否污染现有 run 目录

三个方案如果保持：

```yaml
save_model_dir: /root/data-tmp/workspace/02_experiments/runs
name: kd_light_b2_c64_e120_s42
```

则都会继续写入现有 run 目录。好处是下游评估脚本路径简单，最终 `epoch_120.pth` 位于原 KD run 下。风险是不同恢复方案产生的 checkpoint 会混在同一个目录中。

为降低污染：

1. 不覆盖已有 YAML，新增带方案名的 config。
2. 不覆盖已有日志，日志带方案名和 UTC 时间戳。
3. 若某个方案失败，只保留它产生的最高 epoch checkpoint，并在审计/状态文件记录失败点。
4. 若要完全隔离，可把 `name` 改为 `kd_light_b2_c64_e120_s42_resume4gpu_b2` 等新 run 名；但这样会偏离既有评估脚本默认路径，且需要重新指定 eval/profile 路径。当前更推荐复用原 run 目录，但用 config/log 记录清楚。

## 推荐执行顺序

在外部 B0 四卡训练结束、GPU 空闲后：

1. 先新建 A 配置并跑四卡 batch2 workers0。
2. 若 A 在 epoch6 之后仍 rank0 SIGKILL，改跑 B 双卡 batch2 workers0。
3. 若 B 仍失败或 GPU 窗口不足，改跑 C 单卡 batch2；batch2 OOM/不稳再 batch1。
4. 每次启动前记录 `nvidia-smi`、目标 config、现有 checkpoint 清单；每次结束后记录最高 checkpoint 和失败/完成 epoch。

## 论文边界

在 KD 完成前，论文只能写：

- online KD 工程链路已实现；
- batch1/batch4 smoke 曾通过；
- full train 已多次中断，保留 epoch5 作为恢复点；
- 正在采用 batch/worker/GPU 数降级策略恢复。

不能写：

- KD 提升 Light B2-C64 精度；
- KD 改善 CAMO 边界或 MAE；
- KD final checkpoint、profile 或三数据集概率图指标。

## 主控验收附注

更新时间：2026-06-13T16:20:30Z

本审计接收。审计完成后，主控已继续做了两点工程落地：

1. `kd_light_escnet_b2_c64/train.py` 的单卡分支已移除内部强制设置 `CUDA_VISIBLE_DEVICES=str(device_ids[0])` 的行为，并通过 `python -m py_compile train.py`。因此单卡恢复可以直接使用 YAML 中的 `device_ids: [0]`，也可以由外部 `CUDA_VISIBLE_DEVICES` 做显卡屏蔽后再用逻辑 `device_ids: [0]`。
2. 已实际新增并校验三份恢复配置，均不覆盖原 KD run 目录，而是写入独立 recovery run name：
   - `config_resume_epoch5_b2_workers0_4gpu.yaml` -> `kd_light_b2_c64_e120_s42_recover_b2w0_4gpu`
   - `config_resume_epoch5_b2_workers0_2gpu.yaml` -> `kd_light_b2_c64_e120_s42_recover_b2w0_2gpu`
   - `config_resume_epoch5_b2_workers0_1gpu.yaml` -> `kd_light_b2_c64_e120_s42_recover_b2w0_1gpu`

主控采纳的下一步顺序：外部 B0 四卡任务结束后，优先跑四卡 batch2 workers0 recovery；若仍 SIGKILL，再降双卡；最后才单卡。所有 recovery 结果都必须独立记录 config、log、checkpoint 和评估路径，不能与原 `kd_light_b2_c64_e120_s42` final result 混写。
