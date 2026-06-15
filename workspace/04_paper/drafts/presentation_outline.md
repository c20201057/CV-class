# 组会/答辩汇报提纲

更新时间：2026-06-14T15:12:38Z

用途：把当前论文工作整理成 10-12 页组会或开题后阶段汇报 PPT。该提纲使用当前已验收证据；固定基线、KD 评测和受控速度复测均已完成，但 KD 只能作为中性/负向结果分析。

## Slide 1 题目

题目：面向伪装目标分割的轻量化模型研究

建议口径：

- 实验基底：ESCNet
- 主模型：Light-ESCNet B2-C64
- 当前状态：主学生模型、固定基线、KD 评测和受控速度复测已完成

## Slide 2 研究背景与问题

要点：

- 伪装目标与背景在颜色、纹理和边界上高度相似。
- COD 模型既需要全局语义定位，也需要弱边界细节恢复。
- 高性能模型通常依赖大主干和复杂解码器，部署成本较高。

讲述目标：

把问题定义为“如何在保留边界感知能力的同时降低结构复杂度”。

## Slide 3 基线与路线选择

要点：

- ESCNet 的边缘-语义协同适合 COD 弱边界问题。
- 原始 ESCNet-B5 C128 较重，适合作为教师模型和参考基线。
- 本文不从零设计新网络，而是在强基底上做结构级轻量化。

必须说明：

- 当前开发目录不是用于论文复评的固定基线版本；固定基线代码已固化到实验工作区。
- ESCNet-B5 固定源码同协议三数据集概率图复评已完成。

## Slide 4 方法：Light-ESCNet B2-C64

配图：`../figures/light_b2_c64_method.png`

要点：

- Backbone：PVTv2-B5 -> PVTv2-B2。
- Decoder hidden channel：128 -> 64。
- 保留边缘分支和 edge-guided decoder。
- 推理输出概率图，不使用固定阈值二值图作为主表结果。

一句话解释：

Light-ESCNet B2-C64 不是删除边界模块，而是在保留 ESCNet 关键归纳偏置的前提下压缩 encoder 和 decoder。

## Slide 5 训练与评测协议

要点：

- 输入尺寸：416。
- 训练：Light B2-C64 完成 120 epoch 四卡训练。
- 测试集：CAMO、COD10K、NC4K。
- 指标：S-measure、weighted F-measure、mean F-measure、mean E-measure、MAE。
- 效率：Params、GMACs、model size、peak memory、受控 latency/FPS。

必须说明：

- 主表使用概率图协议。
- latency/FPS 只按空闲 V100、416 输入、batch 1、warmup=50、repeat=100 的受控测量报告。

## Slide 6 精度结果

表格：

| 模型 | 证据状态 | CAMO S/wF/MAE | COD10K S/wF/MAE | NC4K S/wF/MAE |
| --- | --- | --- | --- | --- |
| ESCNet-B5 C128 | 固定源码同协议基线 | 0.881/0.842/0.043 | 0.877/0.802/0.021 | 0.897/0.857/0.029 |
| Light-ESCNet B2-C64 | 当前主结果 | 0.862/0.818/0.051 | 0.866/0.782/0.024 | 0.886/0.840/0.033 |
| Light-ESCNet B2-C64 + KD | 负结果分析 | 0.863/0.818/0.050 | 0.864/0.782/0.024 | 0.885/0.838/0.033 |

讲述口径：

- 相对固定源码同协议 ESCNet-B5 基线，平均 S-measure 从 0.885 到 0.871。
- 平均 MAE 从 0.031 到 0.036。
- 当前差值说明结构压缩主要损失在细节质量上；在线输出级 KD 没有稳定补偿该损失，后续重点看边界分析和更细粒度蒸馏。

## Slide 7 效率结果

表格：

| 模型 | 参数量 | GMACs | 模型大小 | 峰值显存 | 延迟/FPS |
| --- | ---: | ---: | ---: | ---: | ---: |
| ESCNet-B5 C128 | 99.90M | 129.02 | 381.17 MB | 829.77 MB | 73.01 ms / 13.70 |
| Light-ESCNet B2-C64 | 29.81M | 36.39 | 113.74 MB | 237.44 MB | 34.31 ms / 29.15 |

讲述口径：

- 参数量下降 70.16%。
- GMACs 下降 71.79%。
- 模型大小下降 70.16%。
- 峰值显存下降 71.38%。
- 速度数字来自空闲 V100 受控测量，不推广为真实边缘端部署。

## Slide 8 精度-效率折中

配图：`../figures/accuracy_efficiency_scatter.png`

要点：

- Light B2-C64 用较小的 S-measure 损失换来约 70% 的结构复杂度下降。
- CAMO 的 wF/MAE 损失更明显，说明复杂弱边界场景仍需要补偿。
- 这也解释了后续 KD 和边界消融的必要性。

## Slide 9 可视化分析

配图：`../figures/camo_visual_grid_b5_light_b2c64.png`

讲述口径：

- Light 模型能保留多数目标整体区域。
- CAMO 250 个样本中，Light 相对 ESCNet-B5 参考预测的平均 MAE delta 为 +0.008056；140 个样本 `abs(delta)<0.005`，36 个样本 `delta>=0.02`，13 个样本 `delta<=-0.02`。
- 复杂纹理、细长结构、多目标粘连和弱边界区域更容易出现局部漏检、边界扩张或背景高置信误检。
- 这与 wF 和 MAE 的下降一致；详细选例见 `camo_failure_case_analysis.md`。

## Slide 10 已完成证据与保留边界

表格：

| 证据项 | 当前状态 | 论文作用 |
| --- | --- | --- |
| 固定 ESCNet-B5 概率图基线 | 已完成 CAMO/COD10K/NC4K | 支撑 Light 与重模型同协议差值 |
| KD B2-C64 | 已完成；相对 no-KD 基本持平或略低 | 作为负结果分析，不作为贡献 |
| 空闲 GPU 速度复测 | 已完成 | 可报告受控 latency/FPS |
| B0 extreme branch | 外部探索证据 | 只可能作为附录探索或失败分析 |
| MobileMamba-T2 branch | 外部探索证据 | 只可能作为替代轻量主干观察或失败分析 |

必须说明：

- B0 当前只有 COD10K 中间观察，结果明显低于 Light-B2-C64；该分支没有可验收权重，也没有三数据集评估，不进入主表。
- MobileMamba-T2 当前只是外部探索分支；未完成候选权重验收、结构复杂度统计和三数据集评估前，不进入主表。

## Slide 11 当前结论

可以讲：

- Light-ESCNet B2-C64 是当前已验收的主学生模型。
- 在三数据集概率图评测中，它保留了较接近的整体结构感知能力。
- 结构复杂度约下降 70%，证明 PVTv2 同族主干缩放和 decoder 窄化是一条有效轻量化路线。
- 保留边缘-语义协同是本文路线的关键，不是简单砍模块。

必须保留：

- 与 ESCNet-B5 的精度差值目前是固定源码同协议口径。
- KD 不能写成正向提升；速度只能按受控测量条件报告；B0、MobileMamba 仍不能提前写成结论。

## Slide 12 下一步计划

执行顺序：

1. 完成论文正文、阅读说明、汇报提纲和提交材料的 KD/速度结果回填。
2. 完成内部一致性审查，并显式复核 KD 三数据集评测。
3. 若时间允许，补边界分支、解码宽度或 KD 替代形式消融。
4. B0/MobileMamba 只有完成候选权重验收和三数据集评测后，才考虑附录探索。

## 备份页：不可越界表述

- 不说 SOTA。
- 不说 KD 已提升。
- 不把受控 V100 测量说成真实边缘端部署。
- 不把 B0 或 MobileMamba 写入主表。
- 不把未隔离的开发目录当固定基线。
- 不使用后续重训产生的 ESCNet 权重作为教师模型或主基线。

## 备份页：可追溯文件

- 论文稿：`paper_interim_submission.md`
- 外发说明：`teacher_share_pack.md`
- 主张-证据矩阵：`paper_claim_evidence_matrix.md`
- readiness：`paper_submission_readiness.md`
- release audit：`release_audit_latest.md`
