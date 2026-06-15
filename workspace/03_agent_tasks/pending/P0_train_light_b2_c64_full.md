# P0 Task: Train Light-ESCNet B2-C64 Full

## Agent Role

完整训练实验 agent。

## Goal

在评估协议确认后，训练主 student：`light_b2_c64_e120_s42`。

## Inputs

- Code: `/root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64`
- Config: `/root/data-tmp/workspace/02_experiments/configs/light_b2_c64.yaml`
- Dataset: `/root/data-tmp/COD/Train`
- PVTv2-B2 weights: `/root/data-tmp/weights/pvt_v2_b2.pth`
- Output run: `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42`

## Constraints

- 不修改 `/root/ESCNet`。
- 不覆盖已存在 run 目录。
- checkpoint、日志、config、metadata 必须写入 run 目录。
- 不偷懒，不因为怕风险而保守；优先尝试四卡 DDP，失败后才使用单卡 fallback，并保留失败证据。

## Required Config Adjustments

正式训练 config 应确认：

```yaml
backbone: pvt_v2_b2
inter_channel: 64
bb_pretrained: true
weights:
  pvt_v2_b2: /root/data-tmp/weights/pvt_v2_b2.pth
save_model_dir: /root/data-tmp/workspace/02_experiments/runs
name: light_b2_c64_e120_s42
```

若四卡 DDP：

```yaml
device_ids: [0, 1, 2, 3]
multi_GPU: true
```

## Preferred Command

```bash
cd /root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64
torchrun --nproc_per_node=4 train.py \
  --config /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/config.yaml
```

## Fallback Command

```bash
cd /root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64
CUDA_VISIBLE_DEVICES=0 python train.py \
  --config /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/config.yaml
```

## Acceptance

1. 训练日志显示 epoch 120 完成，或失败有可复现日志。
2. 至少保存 final/late checkpoint。
3. run 目录包含 config 快照、metadata、git status、GPU/env 记录。
4. 完成后交给评估套件跑 CAMO/COD10K/NC4K。
5. 短训或失败不能伪装成完整训练。

## Report Format

```text
实验 ID:
训练方式: DDP / single GPU
实际配置:
启动命令:
checkpoint:
训练耗时:
日志路径:
异常:
下一步评估命令:
```
