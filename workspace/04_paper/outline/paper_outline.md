# 论文大纲

题目：面向伪装目标分割的轻量化模型研究

## 摘要

写作要点：

- 伪装目标分割需要全局定位和边界细节。
- 现有高精度模型通常参数量和计算量较大。
- 本文基于 ESCNet 构建 Light-ESCNet，通过轻量主干、窄解码器、边界监督和知识蒸馏降低复杂度。
- 已完成结果只报告 Light-B2-C64 no-KD 的 CAMO、COD10K、NC4K 概率图评测和结构效率；ESCNet-B5 三数据集行在 clean 复评前必须标为 historical reference。

## 1. 引言

逻辑：

1. COD/COS 的困难：低对比、纹理相似、边界弱、多尺度。
2. 应用需求：野外监测、安防、搜救、医学辅助更看重部署成本。
3. ESCNet 等边界/语义协同模型性能强但较重。
4. 本文问题：如何在保持边界感知能力的同时轻量化。
5. 贡献三点：可复现实验流程、Light-ESCNet、精度-效率系统分析；KD/B0/速度只按已验证证据边界表述。

## 2. 相关工作

### 2.1 伪装目标分割基准

CAMO、COD10K、NC4K。

### 2.2 边界、频域与语义增强

SINet、PFNet、FDCOD、ESCNet、FINet/FDESNet。

### 2.3 轻量化 COD

DGNet-S、CSFIN、BPNet、LiteCOD，引出本文选择“结构轻量化 + 蒸馏补偿”。

## 3. 方法

### 3.1 ESCNet 基线回顾

描述 encoder、edge branch AETP、decoder、edge-semantic collaboration。

### 3.2 Light-ESCNet

写轻量化策略：

- Backbone 从 PVTv2-B5 替换为 PVTv2-B2。
- Decoder hidden channel 从 128 降为 64。
- 保留边界分支，减少精度损失。
- B0 只作为外部高风险观察，不能写成主方法结果。

### 3.3 蒸馏训练

给出 loss：

```text
L = Lseg + lambda_edge Ledge + lambda_kd Lkd
```

说明 teacher 为 ESCNet-B5 epoch 120，checkpoint 固定为 `/root/data-tmp/epoch_120.pth`。当前 KD 只完成 smoke 和 partial checkpoint，未完成前不能写提升。

### 3.4 复杂度分析

报告参数量和理论计算量，说明压缩主要来自 encoder 和 decoder。

## 4. 实验

### 4.1 数据集与指标

训练：COD10K-Train + CAMO-Train 共 4040 张。

测试：CAMO、COD10K、NC4K。

指标：S-measure、weighted F-measure、mean F-measure、mean E-measure、MAE；效率指标当前定稿只使用 Params、GMACs、Model Size、Peak Memory。FPS/Latency 需空闲 GPU 同命令复测后才可写。

### 4.2 实现细节

输入尺寸 416，AdamW，学习率、batch size、epoch、数据增强，硬件环境。

### 4.3 Baseline 核验

拆分三类证据：

- clean snapshot strict checkpoint load：证明 `/root/data-tmp/epoch_120.pth` 与 ESCNet-B5 结构匹配。
- CAMO probability re-eval：证明 checkpoint 与概率图评测链路一致。
- historical ESCNet-B5 three-dataset result：仅作 reference，等待 clean snapshot 三数据集复评。

### 4.4 精度结果

主表拆分：

- Completed probability-protocol result：Light-B2-C64 no-KD。
- ESCNet-B5 reference/verification：historical reference + CAMO verification。
- Pending rows：KD、B0、B2-C128/B5-C64。

### 4.5 效率分析

报告 Params、GMACs、Model Size、Peak Memory 约 70% 降低；不报告 final FPS/Latency，直到 Gate 3 通过。

### 4.6 消融实验计划

- Backbone 选择。
- Decoder channel。
- KD。
- 边界/频域模块可选。
- 未完成的消融只能写作计划/待补项。

### 4.7 可视化与失败案例

展示边界质量、弱目标、小目标和失败模式。

## 5. 结论

总结 Light-B2-C64 的结构轻量化收益和概率图评测结果，同时明确 clean baseline 复评、KD 完整训练、速度同条件复测仍是定稿前 gate。

未来工作：

- R2C7K/referring COD。
- CamoVid60K/video COD。
- 更系统的量化和边缘设备部署。
