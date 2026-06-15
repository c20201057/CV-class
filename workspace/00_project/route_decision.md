# 路线判断

更新时间：2026-06-14T15:12:38Z / 2026-06-14 23:12:38 CST

总控态度：不偷懒，不保守。主线要稳，但不能只做低风险复现；P0 工程完成后必须推进完整训练与 KD，对高风险模块轻量化保留隔离分支。

## 总体路线

论文应采用“强基线复现 + 渐进轻量化 + 边界/蒸馏补偿 + 效率验证”的叙事。

推荐模型名：Light-ESCNet。

推荐核心论点：

> ESCNet 的边缘-语义协同机制对伪装目标边界有价值，但原始 PVTv2-B5 主干和 128 通道解码器使模型过重。通过轻量主干、窄通道解码并保留边界监督，Light-ESCNet B2-C64 相对 clean ESCNet-B5 probability baseline 在 CAMO、COD10K、NC4K 上平均 S-measure 下降约 0.014、平均 MAE 增加约 0.005，同时换来约 70% 的参数量、GMACs 和模型大小下降，并在受控 V100 profile 中取得 34.31 ms / 29.15 FPS。在线输出级教师蒸馏已完成验证，但相对 no-KD 基本持平或略低，只能作为负结果分析。

## Gate 1 Clean Baseline Complete

clean ESCNet-B5 probability re-eval 已完成 CAMO/COD10K/NC4K，并写入 `clean_prob_re_eval_complete`。当前固定源码同协议结果：

| Dataset | Clean ESCNet-B5 S | wF | meanF | meanE | MAE | Light B2-C64 S | Light MAE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| CAMO | 0.881 | 0.842 | 0.864 | 0.933 | 0.043 | 0.862 | 0.051 |
| COD10K | 0.877 | 0.802 | 0.824 | 0.938 | 0.021 | 0.866 | 0.024 |
| NC4K | 0.897 | 0.857 | 0.878 | 0.942 | 0.029 | 0.886 | 0.033 |

路线判断：clean baseline 完成后，Light-vs-baseline 的性能差距比 historical interim 口径更清楚。论文叙事应保持进攻性但诚实：主贡献不是“几乎无损”，而是“在保留边界-语义机制的同时，以约 70% 结构压缩换取可接受的精度保持，并在受控 profile 中降低推理成本”。Gate 2 KD 已完成但没有稳定收益，因此不再作为收窄差距的正向证据；外部 B0/MobileMamba 不阻塞论文回填和审计闭环。

## 实验优先级

### P0: 必做

1. 固化 ESCNet-B5 epoch 120 作为 teacher/heavy baseline，checkpoint 使用 `/root/data-tmp/epoch_120.pth`。
2. 补齐 profiling：Params、FLOPs/GMACs、model size、peak memory 可作为结构效率证据；FPS/Latency 必须等空闲 GPU 同条件复测后再写。
3. 构建一个最小轻量模型：`pvt_v2_b2 + inter_channel=64` 或 `pvt_v2_b0 + inter_channel=64`。
4. 三数据集评估：CAMO、COD10K、NC4K。
5. 可视化：Image、GT、ESCNet-B5、Light baseline、Light-ESCNet。

### P1: 强烈建议

1. 做 `inter_channel=128 -> 64` 消融，证明 decoder 窄化收益。
2. 做 `pvt_v2_b5 -> pvt_v2_b2/b0` 消融，证明 backbone 是主要压缩点。
3. 蒸馏：用 ESCNet-B5 teacher 的概率预测约束 student，至少实现 output-level MSE/KL。
4. 修正或新增概率图推理脚本，避免二值预测影响 MAE 和 F/E 曲线指标。

### P2: 时间允许

1. 替换 DeformableConv/FEM 为 depthwise separable FEM。
2. 用 Laplacian/Sobel 高频图构造轻量频域/边界门控。
3. 导出 ONNX 或做 PyTorch dynamic quantization/PTQ，用作部署压缩验证。
4. 少量新数据集扩展，如 R2C7K 或视频抽帧，只放未来工作或附录。

## 推荐实验矩阵

| ID | Model | Backbone | Decoder | Training | Purpose |
| --- | --- | --- | --- | --- | --- |
| E0 | ESCNet-B5 | PVTv2-B5 | 128 | existing epoch120 | 强教师/重基线 |
| E1 | LightBackbone | PVTv2-B2 | 128 | 120 epoch if possible | 主干轻量化，约 43.3M 参数 |
| E2 | LightWidth | PVTv2-B2 | 64 | 120 epoch if possible | 推荐主 student，约 29.8M 参数 |
| E3 | Light-ESCNet | PVTv2-B2 | 64 | KD from E0 | 蒸馏补偿 |
| E4 | Tiny-ESCNet | PVTv2-B0 | 64 | short/full depending time | 极限压缩 |
| E5 | Light-ESCNet-Fast | best student | 64 | optional quant/profile | 部署验证 |

如果算力不足，优先完整训练 E2 和 E3；E1/E4 可以做短训筛选和 profiling 辅助论证。当前 E2 已完成，E3 也已通过 fast-shm 四卡路线完成 120 epoch 与三数据集 probability eval。E3 的实测结果相对 no-KD 基本持平或略低，因此路线结论是：当前 online output-level MSE KD 不能作为主贡献，但它是有价值的负结果和训练成本证据。B0 分支保留为 E4 冒险观察，外部 dirty `/root/ESCNet` 四卡训练已完成，COD10K intermediate eval 已落表到 epoch120。该分支经历 epoch20 退化后逐步恢复，epoch100 是当前最佳完整中间行 S=.8014、wF=.6882、meanF=.7221、meanE=.8899、MAE=.0346；epoch120 最新完整行 S=.8004、wF=.6862、meanF=.7203、meanE=.8878、MAE=.0350，仍明显低于已验收 Light-B2-C64 COD10K S=.866、wF=.782、meanF=.808、meanE=.928、MAE=.024。实时训练进度以 `02_experiments/runs/b0_external_status_latest.md` 为准；只有 clean snapshot、checkpoint load/profile、三数据集评估与 integrity gate 都通过后才可作为附录或失败分析。

当前调度判断：B0/MobileMamba 不应抢占 Gate 1/2/3 已完成证据的论文回填和审计闭环。它们仍保留候选验收入口，体现“不因风险保守”的探索原则；但 B0 epoch120 COD10K 未出现接近 Light-B2-C64 的强反转，且外部 B0 dirty rerun 已按用户明确要求停止。MobileMamba 未观察到运行且无已验收候选 checkpoint，最新且最高 S 的 COD10K 中间观察行为 epoch50 COD10K S=.7487, wF=.6019, meanF=.6482, meanE=.8477, MAE=.0465；实时状态继续委托 tick/status。MobileMamba 证据边界为 `external_dirty_tree_observation_only`。因此这些外部分支只作为极限压缩或替代主干风险分析候选，不替代当前核心论文证据。

## 当前硬件下的调度判断

已确认 4 张 Tesla V100-SXM2-16GB 可用。ESCNet-B5 单卡 120 epoch 约 17.9 小时，B2-C64 预计更快，因此不能只停留在短训筛选。推荐：

1. 先并行完成 baseline profile、评估套件、概率图推理和 B2-C64 smoke。
2. B2-C64 smoke 通过后，四卡优先跑无 KD 完整训练。
3. 无 KD 完整训练完成后，继续推进 KD；如果 online teacher 四卡 DDP 反复 SIGKILL，转向更小 batch、单/双卡或离线 teacher map，不把中断当成路线终点。
4. 若完整训练过程中发现 B2-C64 精度崩坏，立刻补 B2-C128 或 B5-C64，而不是放弃轻量化主线。

## 当前主实验结果

Light-ESCNet B2-C64 no-KD 已完成 120 epoch 四卡训练，并通过统一概率图协议在三数据集上评测。相比 clean ESCNet-B5 probability baseline：

| Metric | ESCNet-B5 Avg | Light B2-C64 Avg | Delta |
| --- | ---: | ---: | ---: |
| S-measure | 0.885 | 0.871 | -0.014 |
| wF-measure | 0.834 | 0.813 | -0.020 |
| mean F-measure | 0.855 | 0.838 | -0.018 |
| mean E-measure | 0.938 | 0.926 | -0.011 |
| MAE | 0.031 | 0.036 | +0.005 |

逐数据集看，Light B2-C64 在 COD10K/NC4K 上 S-measure 均低 0.011；CAMO 的 wF/MAE 下降更明显，说明小样本复杂边界场景仍需要更针对性的边界补偿。当前论文可以把这些数字作为固定源码同协议主差值；KD 已完成但不支持有效补偿的主张。

## 当前 KD 判断

KD B2-C64 已通过 batch 1/batch 4 smoke，并最终经 fast-shm 四卡路线完成 120 epoch 训练。final checkpoint 为 `kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu/epoch_120.pth`，三数据集 probability eval 为 CAMO S=.863/wF=.818/MAE=.050，COD10K S=.864/wF=.782/MAE=.024，NC4K S=.885/wF=.838/MAE=.033。与 no-KD 相比，三数据集平均 S 约 -0.001，wF 约 -0.001，MAE 基本不变。Gate 2 已通过，但结论是“未带来稳定正向收益”。

路线判断：

1. KD 已完成，不再是 pending 训练队列。
2. 当前可入论文的 KD 内容是完整训练、三数据集评测、负结果分析和 online teacher 训练成本；不能写提升。
3. 若继续探索 KD，应改变实验定义，例如 teacher cache、特征级蒸馏或边界蒸馏，并单独验收。

## 当前效率证据

使用 `profile_model.py` 在 416 输入、batch=1、V100 上 profile。结构指标和受控 latency/FPS 已完成：

| Model | Params | GMACs | Model Size | Peak Mem | Controlled Speed |
| --- | ---: | ---: | ---: | ---: | --- |
| ESCNet-B5 C128 | 99.90M | 129.02 | 381.17 MB | 829.77 MB | 73.01 ms / 13.70 FPS |
| Light-ESCNet B2 C64 | 29.81M | 36.39 | 113.74 MB | 237.44 MB | 34.31 ms / 29.15 FPS |
| KD Light-ESCNet B2 C64 | 29.81M | 36.39 | 113.74 MB | 237.44 MB | 34.84 ms / 28.71 FPS |

相对 baseline，Light-ESCNet B2-C64 在未训练前结构 profile 上已实现：

- 参数量降低 70.16%。
- GMACs 降低 71.79%。
- 模型大小降低 70.16%。
- 峰值显存降低 71.38%。

这组结构数字和受控速度数字可以支撑论文效率表；latency/FPS 必须注明 idle V100、416 输入、batch 1、warmup=50、repeat=100 条件，不推广为真实边缘端部署。

## Baseline Checkpoint Decision

必须使用 `/root/data-tmp/epoch_120.pth` 作为 ESCNet-B5 teacher。理由：

- 历史预测目录 `preds_epoch120_*` 生成于 2026-06-11。
- `/root/data-tmp/epoch_120.pth` 生成于 2026-06-11，与历史预测时间匹配。
- `/root/ESCNet/checkpoints/escnet/epoch_120.pth` 现在经 symlink 指向 `/root/data-tmp/workspace/02_experiments/runs/legacy_root_ESCNet_checkpoints_escnet_20260613/epoch_120.pth`，该文件生成于 2026-06-13，是后续重训产物。
- 用 2026-06-13 checkpoint 重新 CAMO 推理约为 S=.819/MAE=.069，低于历史 baseline。
- 用 `/root/data-tmp/epoch_120.pth` 重新 CAMO 概率推理得到 S=.881、wF=.842、meanF=.864、meanE=.933、MAE=.043，和历史 baseline S=.875、wF=.849、meanF=.867、meanE=.937、MAE=.041 高度一致。

因此后续 KD、teacher 预测缓存、baseline 复评都使用 `/root/data-tmp/epoch_120.pth`。`/root/ESCNet/checkpoints/escnet/epoch_120.pth` 只可作为 legacy 复现实验结果，不能混入主 baseline。

## 不推荐作为主线

- 重新复现 SINet/PFNet/SegMaR 等多个外部仓库：课程时间成本过高，且当前已有 ESCNet 强基线。
- 把 R2C7K/CamoVid60K 纳入核心实验：任务范式不同，会稀释“轻量静态 COD”的主线。
- 过早把 DeformConv/FEM/MTA 全部重写：这是 ESCNet 边缘-语义协同的主体，风险高；先完成 backbone/channel/KD。
- 同时尝试 MobileNetV3/GhostNet/ShuffleNetV2 全部替换：需要适配特征尺度和通道，风险高；可作为备选，不作为第一路线。

## 论文贡献表述

可写成三点：

1. 基于 ESCNet 构建可复现实验流程，系统评估伪装目标分割中的精度-效率折中。
2. 提出 Light-ESCNet：以轻量主干和窄边缘-语义解码器降低计算复杂度，并保留边界辅助监督。
3. 报告 teacher-student 蒸馏的中性/负向结果和受控 profiling，在 CAMO、COD10K、NC4K 上验证轻量模型的精度-效率折中。
