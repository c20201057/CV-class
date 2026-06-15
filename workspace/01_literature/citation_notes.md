# Citation Notes

本文件用于论文写作时快速决定“哪里引用哪篇”，避免把相关工作写成无序堆砌。

## 引言

- CAMO/ANet：用于说明伪装目标分割任务早期形成和数据驱动背景。
- COD10K/SINet：用于说明大规模 COD 基准与经典搜索-识别路线。
- ESCNet：用于引出强基线的边缘-语义协同价值与轻量化动机。
- DGNet-S/FINet/BPNet/LiteCOD：用于说明轻量化 COD 已成为近期趋势。

## 相关工作 2.1

数据集与经典模型：

- Le et al. 2019：CAMO。
- Fan et al. 2020：COD10K 和 SINet。
- Lv et al. 2021：NC4K 和 localization/segmentation/ranking。
- Mei et al. 2021：PFNet 和 distraction mining。

写作边界：不要把 NC4K 写成训练集；它在本文中主要是测试和泛化评估。

## 相关工作 2.2

边界、频域和语义增强：

- FDCOD：频域信息可帮助发现伪装目标。
- FINet：轻量化与频域注入的代表。
- ESCNet：边缘-语义协同是本文保留的核心归纳偏置。

写作边界：本文当前没有实现频域模块，因此 FDCOD/FINet 只能作为动机和相关工作，不要暗示本文提出频域创新。

## 相关工作 2.3

轻量化 COD：

- DGNet/DGNet-S：高效 COD 与梯度监督。
- CSFIN：跨阶段特征交互轻量网络。
- BPNet：边界感知轻量 COD。
- LiteCOD：local-global 与 multi-scale fusion 的轻量化路线。

写作边界：除非完成统一复现或引用官方表格，否则不要写本文优于这些方法。

## 方法

- ESCNet：引用于基线回顾和 teacher 选择。
- PVTv2：引用 PVTv2 原文，说明 B5/B2 属于同一金字塔视觉 Transformer 家族，接口兼容使结构轻量化更稳。
- KD：引用 Hinton et al.，说明 teacher-student soft target/输出蒸馏的模型压缩动机。

## 未来工作

- R2C7K/referring COD：作为开放词汇/指代表达扩展方向。
- CamoVid60K/MoCA-Mask：作为视频伪装目标理解扩展方向。

这些不进入核心实验承诺，避免稀释静态轻量 COD 主线。
