# 面向伪装目标分割的轻量化模型研究

## 摘要

伪装目标分割旨在从前景与背景高度相似的图像中定位并分割目标，广泛存在于野外监测、安防巡检、灾害搜救和医学图像辅助分析等应用场景。与普通显著性目标检测相比，伪装目标往往具有弱边界、低对比、尺度变化大和背景纹理干扰强等特点，因此模型既需要全局语义定位能力，也需要细粒度边界恢复能力 [1-3]。现有高性能模型通常依赖较大的 Transformer 主干、复杂多尺度解码器或多阶段推理流程，带来较高的参数量、计算量和推理延迟，限制了其在资源受限设备上的部署 [8-10]。

本文以 ESCNet 为实验基底，研究面向伪装目标分割的轻量化模型 Light-ESCNet [8]。我们保留 ESCNet 中对伪装目标有价值的边缘-语义协同思想，将原始 PVTv2-B5 主干替换为更轻的 PVTv2-B2 主干 [7]，并将解码器隐藏通道由 128 降至 64，从结构上降低模型复杂度。同时，我们建立概率图评测协议和结构复杂度统计流程，对 Light-ESCNet 在 CAMO、COD10K 和 NC4K 三个基准上的精度-效率折中进行分析，并使用固定源码同协议 ESCNet-B5 作为重模型基线。已完成实验显示，Light-ESCNet B2-C64 相比 ESCNet-B5 C128 参数量降低约 70.16%，GMACs 降低约 71.79%，模型大小降低约 70.16%，峰值显存降低约 71.38%；其三数据集概率图评测结果相对固定基线的平均 S-measure 下降约 0.014、MAE 增加约 0.005。受控速度复测中，ESCNet-B5 为 73.01 ms / 13.70 FPS，Light-ESCNet 为 34.31 ms / 29.15 FPS。本文同时完成了基于 ESCNet-B5 教师模型的输出级蒸馏分支，但该分支相对 no-KD 学生模型基本持平或略低，因此作为负结果分析而非正向贡献。

关键词：伪装目标分割；轻量化模型；边界监督；知识蒸馏；精度-效率折中

## 1 引言

伪装目标分割（Camouflaged Object Segmentation, COS）或伪装目标检测（Camouflaged Object Detection, COD）要求模型在自然场景中发现与背景颜色、纹理、轮廓高度相似的目标区域。由于伪装目标通过弱化外观差异来隐藏自身，图像中的前景和背景常常在局部纹理、边缘强度和颜色分布上非常接近。模型若只依赖局部对比，容易把背景纹理误判为目标；若只依赖高层语义，又容易丢失目标边界、小目标和细长结构。因此，COD 模型需要同时具备全局上下文建模、多尺度感知和边界细节恢复能力。

从 CAMO、COD10K 到 NC4K，公开基准推动了 COD 任务快速发展 [1-3]。SINet、PFNet、FDCOD、DGNet 和 ESCNet 等方法分别从搜索定位、干扰挖掘、频域增强、梯度学习和边缘-语义协同等角度提升了分割质量 [2,4-6,8]。然而，这类高性能模型往往使用较大的主干网络或较复杂的解码结构，训练和推理成本较高。实际应用中的野外监测、移动巡检、应急搜救和边缘端辅助诊断不仅需要较高精度，也要求模型具备较小模型体积、较低 FLOPs、较低显存占用和可验证的推理吞吐。

本课题关注的问题是：在不放弃伪装目标边界感知能力的前提下，如何将一个强 COD 模型改造为更轻、更低复杂度、仍具备实用精度的模型。我们选择 ESCNet 作为重模型基线和教师模型 [8]。ESCNet 的边缘-语义协同机制适合伪装目标的弱边界特点，但原始 PVTv2-B5 主干和 128 通道解码器使模型整体较重 [7,8]。基于此，本文构建 Light-ESCNet：采用 PVTv2-B2 轻量主干、64 通道解码器，并保留边界辅助监督；同时实现教师-学生蒸馏分支，用于检验软概率图能否补偿轻量化带来的表达能力下降 [15]。

本文的主要工作如下：

1. 基于 ESCNet 搭建可复现的 COD 轻量化实验流程，统一数据、权重核验、概率图推理、精度评测与结构复杂度统计协议。
2. 构建 Light-ESCNet B2-C64，通过轻量主干和窄通道边缘-语义解码器显著降低参数量、GMACs、模型大小和显存占用。
3. 在 CAMO、COD10K 和 NC4K 上验证已完成模型的精度-效率折中，并对在线输出级 KD 的中性/负向结果、受控速度复测、极限压缩和结构消融边界进行记录，为轻量 COD 模型的实用分析提供系统依据。

## 2 相关工作

### 2.1 伪装目标分割基准与经典方法

CAMO 数据集和 Anabranch Network 较早系统化推动了伪装目标分割任务 [1]。随后，COD10K 提供了更大规模和更丰富类别的伪装目标图像，并与 SINet 一起成为 COD 领域的重要基准 [2]。NC4K 进一步提供大规模测试集，常用于评价模型在复杂场景中的泛化能力 [3]。本文沿用 COD 领域高频设置，使用项目整理后的 COD Train 目录作为训练集，共 4040 张图像，来源对应 COD10K/CAMO 常用训练设置，并在 CAMO-Test、COD10K-Test 和 NC4K 上进行测试。

经典 COD 方法通常围绕“先定位再细化”的思路展开。SINet 通过搜索模块定位潜在伪装区域，再逐步恢复目标结构 [2]；PFNet 从干扰挖掘角度减少背景误检 [4]；SegMaR 等方法通过分阶段放大和细化提升困难区域分割质量。这些方法证明了多阶段上下文建模和局部细节恢复对 COD 的价值，但也带来额外计算成本。

### 2.2 边界、频域与语义增强

伪装目标的核心难点之一是边界弱和纹理相似。FDCOD 将频域信息引入 COD，说明高频或频谱线索可以为伪装区域提供额外判别信息 [5]。进入 Transformer 与注意力建模阶段后，CamoFormer 通过 masked separable attention 强化目标与背景区分 [9]，HGINet 利用动态 token 聚类和层级图交互挖掘难辨别区域 [10]。ESCNet 则以边缘-语义协同为核心，通过边界线索辅助语义分割，并利用语义上下文反哺边缘恢复 [8]。本文选择 ESCNet 作为基底，原因在于其机制与开题报告中“保留边界细节、避免单纯堆叠复杂模块”的目标一致。

### 2.3 轻量化 COD

轻量化 COD 近期逐渐受到关注。DGNet-S、FINet、CSFIN、BPNet、LiteCOD 和 Ulcod-net 等工作从梯度学习、频域注入、跨阶段交互、边界感知、局部-全局融合和多层特征复用等角度降低模型复杂度并保持分割性能 [6,11-14]。这些研究说明，COD 轻量化不能仅做简单通道缩减，还需要对弱边界和困难区域进行补偿。与从零设计新的轻量网络不同，本文采用较稳健但不保守的路线：在 ESCNet 强基底上进行可控结构压缩，保留边缘-语义协同机制，并用统一概率图评测和结构复杂度统计量化精度-效率折中。

### 2.4 知识蒸馏与模型压缩

知识蒸馏通过教师模型向学生模型传递软预测或中间表征，是模型压缩中的常用策略 [15]。在 COD 领域，CamoTeacher 将 teacher-student 一致性用于半监督伪装目标检测 [16]，SAM-COD 在弱监督场景中引入 prompt-adaptive knowledge distillation [17]，近期 CFF-KDNet 等工作也探索了知识蒸馏与跨尺度特征融合 [18]。上述研究表明，KD 已经在 COD 中出现，因此本文不能主张首次引入 KD；本文的定位是使用 ESCNet-B5 教师模型对轻量 Light-ESCNet 学生模型进行输出级概率图约束，验证其是否能补偿主干和解码宽度压缩后的精度损失。实测结果显示，当前在线输出级 MSE KD 未带来稳定正向收益。

## 3 方法

### 3.1 ESCNet 基线

ESCNet 使用 PVTv2 作为多尺度编码器 [7]，并围绕边缘-语义协同设计解码结构 [8]。编码器提取 1/4、1/8、1/16 和 1/32 多尺度特征；高层语义分支用于定位伪装目标区域，边缘分支用于恢复弱边界信息，二者通过协同模块交互。该结构适合 COD 中“目标整体可见但边界不清”的任务特点。

在本文实验中，ESCNet-B5 C128 被作为重模型基线与教师模型。为避免后续探索实验污染基线边界，本文固定了一个与原始 ESCNet 提交一致的源码版本；当前开发目录中的 B0/KD 等探索性修改不直接作为固定基线引用。经过权重核验，主实验统一使用已归档的 ESCNet-B5 epoch 120 教师权重。该权重与固定基线结构严格匹配，而后续重训产生的权重不混入主基线。

### 3.2 Light-ESCNet B2-C64

Light-ESCNet 的核心思想是在保留 ESCNet 边缘-语义协同归纳偏置的同时，压缩主要计算来源 [8]。具体而言，模型将 ESCNet 的 PVTv2-B5 主干替换为 PVTv2-B2 [7]，并将解码器内部隐藏通道从 128 降到 64。这样既减少 encoder 参数和计算量，也降低边缘分支、融合模块和预测头的通道开销。

给定输入图像 `I`，PVTv2-B2 编码器输出四级金字塔特征：

```text
{F1, F2, F3, F4} = Encoder(I),
```

其中 `F1` 保留较高分辨率细节，`F4` 包含高层语义。由于不同层的原始通道数不同，Light-ESCNet 首先使用 1x1 convolution 将四级特征统一映射到 64 通道：

```text
Xi = Proj64(Fi),  i in {1,2,3,4}.
```

随后，AETP 边缘增强分支从 `{X1, X2, X3, X4}` 中聚合浅层纹理细节和深层语义信息，得到边缘 logits `E`。该分支保留了 ESCNet 对弱边界的显式建模能力：高层特征提供目标位置和整体语义，浅层特征补充边缘与局部纹理，二者经过逐级上采样、可变形卷积和空间注意力融合后输出边界预测。

```text
E = AETP(X1, X2, X3, X4).
```

语义解码器继续使用 `E` 作为引导信号。具体做法是：在每个尺度上，从原图提取与当前特征分辨率对应的 patch 信息，并与对应尺度特征拼接；随后通过边缘引导的 FEM 模块进行局部形变感知和多尺度卷积融合。这样，decoder 在恢复目标区域时不仅依赖高层语义，还能利用边缘预测约束伪装目标的轮廓。

```text
P4, P3, P2, P1 = Decoder(X1, X2, X3, X4, sigmoid(E)).
```

其中 `P4` 到 `P1` 对应由粗到细的多尺度 mask logits，训练时共同参与结构损失；最终推理主要使用最高分辨率预测 `P1`。因此，Light-ESCNet B2-C64 不是简单缩小输入或删减边缘分支，而是在保持 ESCNet 关键边缘-语义协同路径的前提下，把主干容量和协同模块宽度控制在更轻的尺度。

该设计比彻底替换为 MobileNet/ShuffleNet 风险更可控，因为 PVTv2-B2 与原始 ESCNet 的四级特征尺度和接口保持一致 [7,8]；同时它又不是简单复现，而是对原始强模型做了实质结构压缩。B2 主要压缩 encoder，C64 则同步压缩 AETP、FEM、MTA 和预测头等后续模块。二者结合后，模型仍保留边界辅助监督和 edge-guided semantic decoding，因此更适合 COD 中低对比、弱边界和纹理混淆的目标区域。

图 1 给出了 Light-ESCNet B2-C64 的整体结构。图中可以看到，本文的轻量化并没有切断 ESCNet 的边缘分支，而是在四级特征统一投影后继续使用 AETP 产生边缘引导，再由 decoder 输出多尺度 mask。

![图 1 Light-ESCNet B2-C64 方法结构图](../figures/light_b2_c64_method.png)

### 3.3 训练目标与知识蒸馏

无蒸馏版本使用 ESCNet 原有的结构损失和边界损失训练。令学生模型输出为 `Ps`，边界输出为 `Es`，真值掩码为 `G`，边界标签为 `Ge`，基础损失可写为：

```text
Lbase = Lseg(Ps, G) + lambda_edge Ledge(Es, Ge).
```

为了弥补轻量化带来的表达能力下降，后续 KD 实验使用 ESCNet-B5 教师模型的概率图作为软监督 [8,15]。令教师输出为 `Pt`，本文当前实现采用 output-level MSE 作为蒸馏损失，KL 等形式可作为后续替代方案：

```text
L = Lbase + lambda_kd Lkd(Ps, Pt).
```

KD 有两种实现路线：在线教师模型前向和离线缓存教师概率图。在线方案与训练时的随机翻转、旋转和裁剪天然对齐，但显存和时间开销较高；离线缓存方案吞吐更稳定，却必须额外处理教师概率图与训练增强的一致性。本文采用在线教师模型 output-level MSE 蒸馏完成 120 epoch 训练，并进行三数据集概率图评测。结果表明，该设置没有稳定改善 no-KD 学生模型，因此本文将其作为负结果和训练成本分析。

### 3.4 复杂度分析

Light-ESCNet 的压缩主要来自两个部分。第一，PVTv2-B5 到 PVTv2-B2 的替换显著减少 encoder 参数和计算。第二，解码器中间通道从 128 降至 64，使多尺度融合、边缘分支和预测头的卷积开销同步下降。结构复杂度统计结果表明，Light-ESCNet B2-C64 在 416 输入尺寸下参数量为 29.81M、GMACs 为 36.39、模型大小为 113.74 MB；ESCNet-B5 C128 对应为 99.90M、129.02 GMACs、381.17 MB。

## 4 实验

### 4.1 数据集与指标

训练集采用项目整理后的 COD Train 目录，共 4040 张图像，来源对应 COD10K/CAMO 常用训练设置 [1,2]。测试集采用 CAMO-Test、COD10K-Test 和 NC4K [1-3]。CAMO 用于保持与早期经典方法可比，COD10K 用于大规模标准测试，NC4K 用于检验复杂场景泛化能力。

精度指标包括 S-measure、weighted F-measure、mean F-measure、mean E-measure 和 MAE。其中 S-measure、F-measure、E-measure 越高越好，MAE 越低越好。效率指标包括参数量、GMACs、模型大小、单张推理延迟、FPS 和峰值显存。Light-ESCNet 与 ESCNet-B5 主结果统一使用概率图评测协议，不使用二值化输出作为主结果，以避免 MAE 和 F/E 曲线被阈值化推理影响。

### 4.2 实现细节

所有模型输入尺寸设为 416。实验环境为 4 张 Tesla V100-SXM2-16GB，PyTorch 2.5.1 + CUDA 12.1。Light-ESCNet B2-C64 使用 PVTv2-B2 ImageNet 预训练权重初始化，训练 120 epoch，四卡 DDP 下每卡 batch size 为 4，初始学习率为 7.5e-5，weight decay 为 1.5e-4，数据增强包括翻转、旋转、椒盐噪声和随机裁剪。ESCNet-B5 教师权重在所有相关实验中保持固定。

为保证实验可复现，每个实验独立保存配置、训练日志、权重、预测结果和评估结果。训练日志解析为 epoch-level loss 表；模型效率在 416 输入、batch size 1 下统计参数量、GMACs、模型大小、推理延迟、FPS 和峰值显存。所有进入论文主表的预测结果必须满足三个条件：预测数量与 GT 数量一致，输出灰度图不是二值化结果，指标由统一评测流程汇总。完整代码目录、脚本入口、权重校验和复现实验命令见 `reproducibility_manifest.md`。

### 4.3 Baseline 核验

权重核验是本文实验可靠性的关键步骤，但不同证据只能支撑不同层面的结论。第一，固定基线源码版本中的关键模型与训练文件和原始提交对齐；在 CPU 上实例化 ESCNet-B5 并加载归档教师权重时，state dict 的 missing keys 和 unexpected keys 均为 0，参数量为 99,903,234，这证明权重与固定 ESCNet-B5 结构完全匹配。第二，ESCNet-B5 同协议概率图复评已经完成 CAMO、COD10K 和 NC4K：CAMO 为 S-measure 0.881、weighted F-measure 0.842、mean F-measure 0.864、mean E-measure 0.933、MAE 0.043，COD10K 为 S-measure 0.877、weighted F-measure 0.802、mean F-measure 0.824、mean E-measure 0.938、MAE 0.021，NC4K 为 S-measure 0.897、weighted F-measure 0.857、mean F-measure 0.878、mean E-measure 0.942、MAE 0.029。因此本文将该归档权重固定为 ESCNet-B5 教师模型和当前重模型基线；历史三数据集结果只作为参考证据。

### 4.4 精度结果

当前已完成的主精度结果来自固定源码同协议 ESCNet-B5 基线、Light-ESCNet B2-C64 no-KD 和 Light-ESCNet B2-C64 + KD 的三数据集概率图评测。KD 版本完整评测已经完成，但由于相对 no-KD 基本持平或略低，不作为精度提升主张。

| 模型 | 证据状态 | CAMO S/wF/MAE | COD10K S/wF/MAE | NC4K S/wF/MAE |
| --- | --- | --- | --- | --- |
| ESCNet-B5 | 固定源码同协议基线 | 0.881/0.842/0.043 | 0.877/0.802/0.021 | 0.897/0.857/0.029 |
| Light-ESCNet B2-C64 | 概率图评测与完整性检查已完成 | 0.862/0.818/0.051 | 0.866/0.782/0.024 | 0.886/0.840/0.033 |
| Light-ESCNet B2-C64 + KD | 完整评测已完成；不作为提升主张 | 0.863/0.818/0.050 | 0.864/0.782/0.024 | 0.885/0.838/0.033 |

相对固定源码同协议 ESCNet-B5 基线，Light-ESCNet B2-C64 在三数据集平均 S-measure 上下降约 0.014，在 weighted F-measure 上下降约 0.020，在 MAE 上增加约 0.005。当前 Light 结果已经说明 B2-C64 在完整概率图协议下具备可用精度；CAMO 上 wF 与 MAE 的下降更明显，提示弱边界和小样本困难场景仍需要更强边界补偿。KD student 相对 no-KD 的三数据集均值几乎不变，平均 S-measure 和 weighted F-measure 均约低 0.001，MAE 基本不变，因此当前在线 KD 设置没有解决这一细节质量问题。

### 4.5 效率结果

结构效率统计已完成结构级对比。ESCNet-B5 C128 约 99.90M 参数、129.02 GMACs、381.17 MB 模型大小、829.77 MB 峰值显存。Light-ESCNet B2-C64 约 29.81M 参数、36.39 GMACs、113.74 MB 模型大小、237.44 MB 峰值显存。相对重模型，Light-ESCNet 在参数量、计算量、模型大小和峰值显存上均取得约 70% 的降低。受控速度复测采用空闲 V100、416 输入、batch size 1、warmup=50、repeat=100；ESCNet-B5 为 73.01 ms / 13.70 FPS，Light-ESCNet no-KD 为 34.31 ms / 29.15 FPS，KD student 为 34.84 ms / 28.71 FPS。

| 模型 | 参数量(M) | GMACs | 模型大小(MB) | 峰值显存(MB) | 结构降幅 |
| --- | ---: | ---: | ---: | ---: | --- |
| ESCNet-B5 C128 | 99.90 | 129.02 | 381.17 | 829.77 | 参考 |
| Light-ESCNet B2-C64 | 29.81 | 36.39 | 113.74 | 237.44 | 参数量 -70.16%; GMACs -71.79%; 模型大小 -70.16%; 显存 -71.38% |

| 模型 | 延迟(ms) | FPS | 测量条件 |
| --- | ---: | ---: | --- |
| ESCNet-B5 C128 | 73.01 | 13.70 | V100, 416, batch 1 |
| Light-ESCNet B2-C64 | 34.31 | 29.15 | V100, 416, batch 1 |
| Light-ESCNet B2-C64 + KD | 34.84 | 28.71 | V100, 416, batch 1 |

图 2 进一步展示了三数据集平均 S-measure 与 GMACs 的精度-效率关系。Light-ESCNet B2-C64 位于明显更低计算量区域；图中 ESCNet-B5 点使用固定源码同协议基线。

![图 2 精度-效率折中散点图](../figures/accuracy_efficiency_scatter.png)

### 4.6 消融实验计划与待补项

当前消融实验尚未形成完整结果表，不作为本文已有结论。后续实验关注四个问题：

1. 主干轻量化：比较 PVTv2-B5 与 PVTv2-B2，分析 encoder 压缩对精度和效率的影响。
2. 解码器通道：比较 C128 与 C64，验证窄解码器是否能在较小代价下保持边界恢复能力。
3. 边界监督：保留或移除边界辅助分支，观察 MAE 与可视化边界质量变化。
4. 知识蒸馏替代形式：当前在线输出级 MSE KD 未改善 no-KD student，后续重点分析 teacher cache、特征级蒸馏或边界蒸馏是否更适合该任务。

其中，B2-C64 无 KD 与 B2-C64 + KD 已完成完整训练和评测；B2-C128、B0-C64、MobileMamba-T2 替代主干和去边界分支可作为短训或后续补充实验。若最终定稿前仍无法完成这些分支，本节应移动到实验缺口或未来工作，而不是作为消融结论呈现。

### 4.7 当前运行状态

截至当前实验记录，Light-ESCNet B2-C64 无 KD 四卡 DDP 训练已完成 120/120 epoch，最终平均训练损失为 1.369。训练后结构复杂度统计与三数据集概率图评测均已完成，相关权重、评测目录和哈希信息见复现 manifest。

KD 版本已在独立代码目录中实现在线教师模型 MSE 蒸馏，教师模型为 ESCNet-B5 epoch 120，学生模型为 Light-ESCNet B2-C64。该分支已完成 120 epoch 训练、三数据集概率图评测和受控速度复测，但相对 no-KD student 基本持平或略低。因此，当前论文中只能把 KD 描述为已测得的负结果和工程成本观察，不能把 KD 效果写为正向结论。

此外，PVTv2-B0 极限压缩分支仍属于外部高风险探索分支。现有 COD10K 中间观察显示，该容量下限路线明显低于已验收 Light-ESCNet B2-C64 的 COD10K 结果，更适合作为附录探索或失败分析，而不是替代当前 B2-C64 主线。由于该分支尚未完成独立代码归档、权重核验、结构复杂度统计、CAMO/COD10K/NC4K 三数据集概率图评估和完整性检查，因此不纳入本文主表或结论；运行细节仅作为工程记录保存在对应实验状态文件中。

MobileMamba-T2 在线 KD 分支是替代轻量主干的高风险探索。该分支不属于固定基线、Light-B2-C64 主结果或 KD 主线；只有在产生候选权重，并完成独立代码归档、权重核验、结构复杂度统计、三数据集概率图评估和完整性检查后，才可作为附录观察或失败分析。当前阶段它只能作为路线判断记录，不能进入主表、摘要或结论；实时状态保存在对应实验状态文件中。

### 4.8 可视化与失败案例

可视化结果应覆盖弱边界、大目标、小目标、多目标、纹理背景干扰和失败案例。当前已基于 CAMO per-image MAE 自动选择样本，生成原图、GT、ESCNet-B5 参考预测、Light-ESCNet B2-C64 四列图；后续可增加 KD 列，分析为什么在线输出级蒸馏没有稳定改善边界断裂、局部漏检和背景误检。CAMO 250 个样本的参考可视化统计显示，Light 相对 ESCNet-B5 参考预测的平均 MAE delta 为 +0.008056，其中 141 个样本更差、109 个样本更好，140 个样本 `abs(delta)<0.005`，说明大部分样本差异较小，但 36 个 `delta>=0.02` 的困难样本贡献了更明显退化。人工检查这些样本后，主要失败类型集中在强纹理低对比下的目标局部漏检或位置偏移、细长结构过扩张、背景高置信误检以及多部件目标的局部遗漏；同时也存在部分样本中 Light 预测更紧凑、背景误检更少的情况。该观察解释了 CAMO 上 S-measure 仍较接近而 wF/MAE 更敏感的现象，也支持后续优先验证边界分支消融和更细粒度蒸馏。样本选择依据见 `04_paper/figures/camo_case_selection_b5_light.md`，详细分析见 `04_paper/drafts/camo_failure_case_analysis.md`，相关图像位于 `04_paper/figures/camo_light_worse_cases.png`、`camo_light_close_cases.png` 和 `camo_light_better_cases.png`。

![图 3 CAMO 可视化对比](../figures/camo_visual_grid_b5_light_b2c64.png)

## 5 结论

本文围绕“面向伪装目标分割的轻量化模型研究”构建了基于 ESCNet 的可复现实验流程，并提出 Light-ESCNet B2-C64 作为主力轻量模型。实验表明，该模型在保留边缘-语义协同机制的同时，显著降低了参数量、GMACs、模型大小和显存占用；在 CAMO、COD10K 和 NC4K 上已经完成统一概率图评测，并相对固定源码同协议 ESCNet-B5 基线只产生有限的平均 S-measure 与 MAE 差距。受控速度复测也显示，Light-ESCNet 的单张延迟和吞吐表现明显优于 ESCNet-B5。当前结果已经说明，对 ESCNet 进行轻量主干替换和解码通道压缩是一条有价值的轻量化路线。

当前结论仍需保持严谨：Light-ESCNet no-KD 精度结果已经由统一概率图评测支撑，结构效率收益和受控速度数字已经由同条件测量支撑；在线输出级 KD 已完成但未带来稳定正向收益。后续将继续完成边界分支消融、KD 替代形式和更贴近部署环境的速度测试，并把现有 CAMO 失败案例分析整理进最终论文。

## 参考文献

[1] Le T. N., Nguyen T. V., Nie Z., Tran M. T., Sugimoto A. Anabranch Network for Camouflaged Object Segmentation. Computer Vision and Image Understanding, 2019.

[2] Fan D. P., Ji G. P., Sun G., Cheng M. M., Shen J., Shao L. Camouflaged Object Detection. CVPR, 2020.

[3] Lv Y., Zhang J., Dai Y., Li A., Barnes N. Simultaneously Localize, Segment and Rank the Camouflaged Objects. CVPR, 2021.

[4] Mei H., Ji G. P., Wei Z., Yang X., Wei X., Fan D. P. Camouflaged Object Segmentation with Distraction Mining. CVPR, 2021.

[5] Zhong Y., Li B., Tang L., Kuang S., Wu S., Ding S. Detecting Camouflaged Object in Frequency Domain. CVPR, 2022.

[6] He C., Li K., Zhang Y., Xu G., Tang L., Zhang Y., Guo Z., Li X. Deep Gradient Learning for Efficient Camouflaged Object Detection. Machine Intelligence Research, 2023.

[7] Wang W., Xie E., Li X., Fan D. P., Song K., Liang D., Lu T., Luo P., Shao L. PVT v2: Improved Baselines with Pyramid Vision Transformer. arXiv:2106.13797, 2021.

[8] Ye X., Liu Y., Li X., et al. ESCNet: Edge-Semantic Collaborative Network for Camouflaged Object Detection. ICCV, 2025.

[9] Yin B., Zhang X., Fan D. P., Jiao S., Cheng M. M., Van Gool L., Hou Q. CamoFormer: Masked Separable Attention for Camouflaged Object Detection. IEEE TPAMI, 2024.

[10] Yao S., Sun H., Xiang T. Z., Wang X., Cao X. Hierarchical Graph Interaction Transformer With Dynamic Token Clustering for Camouflaged Object Detection. IEEE TIP, 2024.

[11] Liang W., Wu J., Wu Y., Mu X., Xu J. FINet: Frequency Injection Network for Lightweight Camouflaged Object Detection. IEEE Signal Processing Letters, 2024.

[12] Li M., Zhao Y., Zhang F., Gui G., Luo B., Yang C., Gui W., Chang K. CSFIN: A Lightweight Network for Camouflaged Object Detection via Cross-Stage Feature Interaction. Expert Systems with Applications, 2025.

[13] Chen C., Liang W., Wang D., Wang B., Xu J. Vision-Inspired Boundary Perception Network for Lightweight Camouflaged Object Detection. IEEE Signal Processing Letters, 2025.

[14] Khan A., Ullah H., Munir A., et al. LiteCOD: Lightweight Camouflaged Object Detection via Holistic Understanding of Local-Global Features and Multi-Scale Fusion. AI, 2025.

[15] Hinton G., Vinyals O., Dean J. Distilling the Knowledge in a Neural Network. arXiv:1503.02531, 2015.

[16] Lai X., Yang Z., Hu J., Zhang S., Cao L., Jiang G., Wang Z., Zhang S., Ji R. CamoTeacher: Dual-Rotation Consistency Learning for Semi-Supervised Camouflaged Object Detection. ECCV, 2024.

[17] Chen H., Wei P., Guo G., Gao S. SAM-COD: SAM-guided Unified Framework for Weakly-Supervised Camouflaged Object Detection. ECCV, 2024.

[18] Cai B., Li H., Yang Y., Yan J. CFF-KDNet: Cross-Scale Feature Fusion Network with Knowledge Distillation for Camouflaged Object Detection. Expert Systems with Applications, 2025.
