# light_b2_c64_e120_s42 Status

## Final Accepted Summary

更新时间：2026-06-14 00:43 UTC

状态：已完成并验收为当前主学生模型结果。

- Code: `/root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64`
- Config: `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/config.yaml`
- Final checkpoint: `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/epoch_120.pth`
- Final checkpoint sha256: `a6886fded30bef1e59f1ddc3d05078d6b8023aa0387867ded225b4d0775b3c7d`
- Final epoch: 120/120
- Final avg training loss: 1.369
- Checkpoint count: 11
- Probability eval run: `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42_prob_eval_v2`
- Evidence status: `final_main_light`
- Integrity: CAMO/COD10K/NC4K prediction counts match GT counts and result files exist.
- Profile: `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/profile_epoch120.json`

以下旧进度记录保留为训练过程日志，不能覆盖上面的最终状态。

## Historical Progress Log

更新时间：2026-06-13 19:53 UTC+8

## 当前状态

四卡 DDP 训练中。

- Code: `/root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64`
- Config: `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/config.yaml`
- Log: `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/train_ddp.log`
- Output dir: `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42`
- Backbone: PVTv2-B2
- Decoder channel: 64
- PVTv2-B2 pretrained weight: `/root/data-tmp/weights/pvt_v2_b2.pth`

## DDP Smoke

`smoke_light_b2_c64_ddp_e1` 已完成 1 epoch，证明四卡 DDP 和保存路径可用。

## Training Progress

已进入 epoch 15/120。

近期 epoch 平均 loss：

| Epoch | Avg Loss |
| ---: | ---: |
| 1 | 4.123 |
| 2 | 3.356 |
| 3 | 3.123 |
| 4 | 2.889 |
| 5 | 2.787 |
| 6 | 2.707 |
| 7 | 2.598 |
| 8 | 2.492 |
| 9 | 2.331 |
| 10 | 2.270 |
| 11 | 2.399 |
| 12 | 2.216 |
| 13 | 2.127 |
| 14 | 2.087 |

## Baseline/Teacher Decision

Teacher checkpoint 使用 `/root/data-tmp/epoch_120.pth`，不要使用 `/root/ESCNet/checkpoints/escnet/epoch_120.pth`。

原因：后者是 2026-06-13 后续重训产物，不复现历史 baseline；前者与历史预测时间匹配，CAMO 概率复评接近历史指标。
## Update: Epoch 20

时间：2026-06-13 20:02 UTC+8

训练已完成 epoch 20/120，四卡 DDP 仍稳定。

近期 avg loss：e15 2.002, e16 1.932, e17 1.925, e18 2.032, e19 1.952, e20 1.860。
## Update: Epoch 30

时间：2026-06-13 20:17 UTC+8

训练已完成 epoch 30/120，四卡 DDP 稳定。

近期 avg loss：e21 1.941, e22 1.871, e23 1.845, e24 1.807, e25 1.766, e26 1.764, e27 1.729, e28 1.764, e29 1.718, e30 1.807。

注意：配置为 `save_last: 30`、`save_step: 3`，因此 checkpoint 从 epoch 90 开始保存；epoch 30 无 checkpoint 是预期行为。

## Update: Epoch 44

时间：2026-06-13 20:38 UTC

训练已完成 epoch 44/120，四卡 DDP 稳定。

近期 avg loss：e31 1.732, e32 1.720, e33 1.670, e34 1.687, e35 1.644, e36 1.651, e37 1.649, e38 1.700, e39 1.660, e40 1.647, e41 1.628, e42 1.623, e43 1.589, e44 1.594。

截至 epoch 44 仍未保存 checkpoint，这是 `save_last: 30`、`save_step: 3` 的预期行为。

## Update: Epoch 50

时间：2026-06-13 20:47 UTC

训练已完成 epoch 50/120，四卡 DDP 稳定并已进入 epoch 51。

近期 avg loss：e45 1.579, e46 1.548, e47 1.669, e48 1.666, e49 1.629, e50 1.602。

已生成训练 loss 汇总：

- CSV: `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/train_loss.csv`
- Markdown: `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/train_loss.md`

截至 epoch 50 仍未保存 checkpoint，这是 `save_last: 30`、`save_step: 3` 的预期行为。

## Update: Epoch 60

时间：2026-06-13 21:02 UTC

训练已完成 epoch 60/120，四卡 DDP 稳定并已进入 epoch 61。

近期 avg loss：e51 1.561, e52 1.556, e53 1.556, e54 1.569, e55 1.525, e56 1.539, e57 1.547, e58 1.532, e59 1.527, e60 1.520。

训练已过半，loss 缓慢下降。当前 checkpoint 数量仍为 0，这是 `save_last: 30`、`save_step: 3` 的预期行为；第一个 checkpoint 预计为 `epoch_90.pth`。

## Update: Epoch 70

时间：2026-06-13 21:17 UTC

训练已完成 epoch 70/120，四卡 DDP 稳定并已进入 epoch 71。

近期 avg loss：e61 1.497, e62 1.523, e63 1.528, e64 1.509, e65 1.499, e66 1.496, e67 1.493, e68 1.503, e69 1.478, e70 1.482。

当前最低训练 avg loss 为 epoch 69 的 1.478。checkpoint 数量仍为 0，这是保存策略预期；下一个关键节点是 epoch 90。

## Update: Epoch 83

时间：2026-06-13 21:36 UTC

训练已完成 epoch 83/120，四卡 DDP 稳定并已进入 epoch 84。

近期 avg loss：e72 1.472, e73 1.470, e74 1.483, e75 1.461, e76 1.473, e77 1.454, e78 1.459, e79 1.462, e80 1.481, e81 1.466, e82 1.434, e83 1.451。

当前最低训练 avg loss 为 epoch 82 的 1.434。checkpoint 数量仍为 0，这是 `save_last: 30`、`save_step: 3` 的预期行为；第一个 checkpoint 预计为 `epoch_90.pth`，之后每 3 epoch 保存一次。
