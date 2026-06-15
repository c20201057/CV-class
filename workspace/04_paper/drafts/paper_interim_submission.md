# 面向伪装目标分割的轻量化模型研究

## 摘要

伪装目标分割需要在前景与背景高度相似的图像中恢复目标区域。与普通显著性目标分割相比，伪装目标通常具有低对比、弱边界、多尺度和复杂纹理干扰等特点，因此模型既要具备全局语义定位能力，也要保留细粒度边界恢复能力 [1-3]。现有高性能伪装目标分割方法往往依赖较大的 Transformer 主干或复杂多尺度解码器，带来较高参数量、计算量和显存占用，限制了其在资源受限场景中的应用 [8-10]。

本文以 ESCNet 为实验基底，研究一种面向伪装目标分割的轻量化改造模型 Light-ESCNet B2-C64 [8]。该模型保留 ESCNet 中的边缘-语义协同思想，将 PVTv2-B5 主干替换为 PVTv2-B2 [7]，并将解码器隐藏通道由 128 降至 64，从编码器和解码器两部分降低结构复杂度。本文进一步建立了概率图推理、三数据集评测和结构复杂度统计的统一流程，以避免二值化预测和权重混用对结论造成影响。

已完成实验表明，Light-ESCNet B2-C64 在 CAMO、COD10K 和 NC4K 上完成了 120 epoch 训练后的概率图评测。相对固定源码同协议 ESCNet-B5 基线，其三数据集平均 S-measure 从 0.885 变为 0.871，MAE 从 0.031 变为 0.036；同时参数量由 99.90M 降至 29.81M，GMACs 由 129.02 降至 36.39，模型大小由 381.17 MB 降至 113.74 MB，峰值显存由 829.77 MB 降至 237.44 MB。受控速度复测中，ESCNet-B5 为 73.01 ms / 13.70 FPS，Light-ESCNet 为 34.31 ms / 29.15 FPS。在线输出级 KD 分支也已完成 120 epoch 训练和三数据集评测，但相对 no-KD 基本持平或略低，因此本文不将其写作正向贡献。结果说明，在保留边缘-语义协同结构的前提下，对主干规模和解码宽度进行压缩，可以为伪装目标分割提供有价值的精度-效率折中。

关键词：伪装目标分割；轻量化模型；边缘-语义协同；PVTv2；知识蒸馏；精度-效率折中

## 1 引言

伪装目标分割要求模型从自然场景中发现与背景颜色、纹理和轮廓高度相似的目标区域。由于伪装目标通过弱化外观差异来隐藏自身，图像中的局部对比、边缘强度和颜色分布往往不足以直接区分前景和背景。模型若过度依赖局部纹理，容易把背景误判为目标；若只依赖高层语义，又容易丢失细长结构、小目标和模糊边界。因此，伪装目标分割模型需要同时建模全局上下文、多尺度结构和边界细节。

CAMO、COD10K 和 NC4K 等数据集推动了伪装目标分割任务的发展 [1-3]。SINet、PFNet、FDCOD、DGNet、CamoFormer、HGINet 和 ESCNet 等方法分别从搜索定位、干扰挖掘、频域增强、梯度学习、注意力建模、图交互和边缘-语义协同等角度提升分割质量 [2,4-6,8-10]。这些方法证明了复杂上下文建模和边界恢复对伪装目标分割的重要性，但也常伴随更高的参数量和计算成本。对于野外监测、移动巡检、搜救辅助和资源受限设备，模型不仅要准确，还需要较小模型体积、较低计算量和稳定的部署成本。

本文关注的问题是：在不破坏伪装目标边界感知能力的前提下，如何将一个强分割模型改造为更轻的模型。ESCNet 的边缘-语义协同结构适合伪装目标的弱边界特点，但原始 PVTv2-B5 主干和 128 通道解码器使模型整体较重 [7,8]。本文选择在 ESCNet 强基底上进行可控压缩，而不是从零设计新的复杂网络。这样既能保留已经验证有效的边界协同机制，也有利于将性能变化归因于主干规模和解码宽度的变化。

本文主要工作如下：

1. 基于 ESCNet 搭建了可复查的轻量化实验流程，统一权重核验、概率图推理、三数据集评测和结构复杂度统计协议。
2. 构建 Light-ESCNet B2-C64，通过 PVTv2-B5 到 PVTv2-B2 的主干压缩和 128 到 64 的解码通道压缩，显著降低结构复杂度，同时保留边缘-语义协同机制。
3. 在 CAMO、COD10K 和 NC4K 上分析 Light-ESCNet 的精度-效率折中，并报告在线输出级 KD 的中性/负向结果、受控速度复测结果以及极限压缩分支的证据边界。

需要强调的是，本文的目标不是给出一个与所有最新 COD 方法横向竞争的绝对排名，而是围绕同一强基底建立可追溯的结构压缩证据。为避免把不同协议、不同权重或不同代码状态下的数字混作同一结论，本文将完整主结果、固定基线、历史参考、验证性复核和探索分支分别标注。这样的边界使 KD、速度和外部探索结果只能按已验收证据进入论文，而不会改变当前已验收 Light-ESCNet no-KD 结果的含义。

## 2 相关工作

### 2.1 伪装目标分割基准与经典方法

CAMO 较早系统化推动了伪装目标分割任务 [1]，COD10K 提供了更大规模和更丰富类别的伪装目标图像 [2]，NC4K 则常用于检验模型在复杂场景中的泛化能力 [3]。SINet 采用搜索和识别阶段定位伪装目标 [2]，PFNet 从干扰挖掘角度减少背景误检 [4]，SegMaR 通过分阶段放大和细化提升困难区域质量。这些经典方法说明，伪装目标分割既依赖全局定位，也依赖局部细化。

### 2.2 边界、频域与语义增强

弱边界是伪装目标分割的关键难点。FDCOD 从频域角度挖掘伪装目标与背景的差异，说明高频或频谱线索能够补充 RGB 外观信息 [5]。CamoFormer 和 HGINet 等 Transformer 方法进一步强化上下文建模和困难区域交互 [9,10]。ESCNet 则通过边缘-语义协同结构，将边界线索与语义分割相互补充 [8]。本文选择 ESCNet 作为实验基底，原因在于该结构与伪装目标的弱边界特点高度相关，也与本课题“轻量化时保留关键归纳偏置”的目标一致。

### 2.3 轻量化伪装目标分割

近期轻量化伪装目标分割逐渐受到关注。DGNet-S、FINet、CSFIN、BPNet、LiteCOD 和 Ulcod-net 等工作分别从梯度学习、频域注入、跨阶段特征交互、边界感知、局部-全局融合和特征复用等角度探索高效模型 [6,11-14]。这些研究表明，轻量化 COD 不能简单等同于减少通道数，还需要保留对弱边界、纹理干扰和多尺度目标有帮助的结构。与从零设计轻量网络不同，本文关注强 COD 模型的结构级压缩：在 ESCNet 中保留边缘-语义协同路径，同时缩小主干和解码器宽度。

### 2.4 知识蒸馏与模型压缩

知识蒸馏通过教师模型向学生模型传递软预测或中间表征，是模型压缩中的常用策略 [15]。在 COD 领域，CamoTeacher 使用 teacher-student 一致性处理半监督伪标签问题 [16]，SAM-COD 在弱监督场景中引入 prompt-adaptive knowledge distillation [17]，CFF-KDNet 等近期工作也探索了知识蒸馏与跨尺度特征融合 [18]。本文不能主张首次将蒸馏用于 COD；本文中的蒸馏分支定位为 ESCNet-B5 teacher 到 Light-ESCNet student 的输出级概率约束，用于验证轻量化后的精度补偿潜力。该分支已完成完整训练与三数据集评测，但实测结果没有带来稳定正向收益，因此本文把它作为补偿路线的负结果分析，而不是方法贡献。

## 3 方法

### 3.1 ESCNet 基线

ESCNet 使用 PVTv2 作为层级编码器 [7]，提取 1/4、1/8、1/16 和 1/32 四个尺度的特征。高层语义特征用于定位伪装目标整体区域，浅层特征包含更多边缘和纹理细节。ESCNet 的核心在于边缘-语义协同：边缘分支利用多尺度特征预测目标边界，语义解码器再利用边界信息指导 mask 恢复，从而缓解伪装目标边界模糊的问题 [8]。

本文将 ESCNet-B5 C128 作为重模型参考和教师模型。为了避免后续探索实验污染基线边界，本文固化了 ESCNet-B5 源码版本，并确认历史教师权重能够严格加载到该版本中，missing keys 和 unexpected keys 均为 0。另一个后续重训产生的 ESCNet 权重不作为教师模型或参考基线使用。

### 3.2 Light-ESCNet B2-C64

Light-ESCNet 的设计目标不是移除 ESCNet 中对 COD 有效的边缘分支 [8]，而是在保持边缘-语义交互路径基本不变的前提下，压缩模型中参数量和计算量最集中的编码器与解码器通道。本文采用两个主要改动：

1. 主干轻量化：将 PVTv2-B5 替换为 PVTv2-B2。
2. 解码器窄化：将内部隐藏通道由 128 降至 64。

这两个改动分别对应“语义容量压缩”和“融合宽度压缩”。主干决定四级金字塔特征的全局建模能力和主要计算开销，解码器宽度则影响边缘分支、特征融合模块和多尺度 mask 预测头的卷积计算。与直接替换为 MobileNet、ShuffleNet 或重新设计一个轻量网络相比，同族 PVTv2-B5 到 PVTv2-B2 的缩放能够保持四级输出接口一致 [7]，使后续 AETP 边缘分支和 edge-guided decoder 不需要改变拓扑结构。这样做的好处是控制变量更清楚：性能变化主要来自 backbone scale 和 `inter_channel` 宽度下降，而不是来自完全不同特征体系带来的结构混杂。

由于 PVTv2-B2 与 PVTv2-B5 都提供四级层级特征，主干替换后后续边缘分支和语义解码器的输入组织方式保持一致。给定输入图像，PVTv2-B2 编码器输出四级金字塔特征：

```text
{F1, F2, F3, F4} = Encoder(I)
```

其中 `F1` 保留较高分辨率细节，`F4` 包含更强语义信息。Light-ESCNet 使用 1x1 卷积将不同层特征统一映射到 64 通道：

```text
Xi = Proj64(Fi), i in {1,2,3,4}
```

随后边缘增强分支从多尺度特征中聚合浅层细节和深层语义，得到边缘预测 `E`。语义解码器继续以 `E` 作为引导，输出从粗到细的多尺度 mask logits：

```text
E = EdgeBranch(X1, X2, X3, X4)
P4, P3, P2, P1 = Decoder(X1, X2, X3, X4, sigmoid(E))
```

训练时多尺度 mask 和边缘预测共同参与监督，推理时使用最高分辨率预测生成概率图。因此，Light-ESCNet B2-C64 不是简单缩小输入尺寸或删除边界分支，而是在保留 ESCNet 关键归纳偏置的条件下，对主干容量和解码宽度进行压缩。

从代码实现看，`inter_channel=64` 同时作用于四级 `1x1` 投影、AETP 边缘增强分支、FEM 边缘引导融合模块、MTA 解码块和最终预测头。因此 C64 不是只压缩某一个孤立层，而是让边缘预测、局部 patch 融合和逐级 mask 恢复共享同一个较窄的中间表征。本文保留这些路径，是因为当前课题的核心问题并不是证明“删掉边缘分支也能工作”，而是在弱边界任务中检验保留边缘-语义协同后，模型容量可以压缩到什么程度。

![图 1 Light-ESCNet B2-C64 结构示意图](../figures/light_b2_c64_method.png)

### 3.3 训练目标与蒸馏分支

无蒸馏版本沿用分割损失和边界辅助损失。记学生模型 mask 输出为 `Ps`，边缘输出为 `Es`，真值 mask 为 `G`，边界标签为 `Ge`，基础训练目标可写为：

```text
Lbase = Lseg(Ps, G) + lambda_edge Ledge(Es, Ge)
```

为进一步验证轻量模型的补偿潜力，本文实现了 ESCNet-B5 teacher 到 Light-ESCNet student 的输出级蒸馏分支 [8,15]。记 teacher 输出为 `Pt`，当前实现采用 MSE 约束学生和教师的概率输出：

```text
L = Lbase + lambda_kd Lkd(Ps, Pt)
```

在线 teacher 前向能够与训练增强保持对齐，但显存和训练稳定性压力更高；离线 teacher map 缓存吞吐更稳定，但需要额外处理增强对齐。本文采用在线输出级蒸馏完成 120 epoch 训练，并与 no-KD student 进行同协议三数据集概率图比较。由于实测结果没有稳定改善 no-KD student，本文只将该分支作为负结果和训练成本分析。

### 3.4 复杂度来源

Light-ESCNet 的复杂度下降来自两个部分。首先，PVTv2-B5 到 PVTv2-B2 的替换显著降低 encoder 参数量和计算量。其次，解码器隐藏通道从 128 降至 64 后，多尺度融合、边缘预测和 mask 预测中的卷积开销同步下降。因此，B2 和 C64 的组合同时压缩了主干和解码端，而不是只压缩单个模块。

## 4 实验

### 4.1 数据集与指标

训练集采用项目整理后的 COD 训练集，共 4040 张图像，来源对应 COD10K 与 CAMO 的常用训练设置 [1,2]。测试集采用 CAMO-Test、COD10K-Test 和 NC4K [1-3]。

精度指标包括 S-measure、weighted F-measure、mean F-measure、mean E-measure 和 MAE。其中 S-measure、F-measure 和 E-measure 越高越好，MAE 越低越好。效率指标包括参数量、GMACs、模型大小、峰值显存、单张推理延迟和 FPS。延迟和 FPS 使用空闲 GPU、同一测量流程、416 输入、batch size 1、warmup=50、repeat=100 的受控设置单独报告。

本文主结果使用概率图推理协议，即保存 sigmoid 后的灰度概率图进行评估，不使用固定阈值二值化输出作为主表结果。这样可以避免二值化预测影响 MAE、F-measure 和 E-measure 曲线。

### 4.2 实现细节

所有输入图像 resize 到 416。Light-ESCNet B2-C64 使用 PVTv2-B2 ImageNet 预训练权重初始化，训练 120 epoch，随机种子设为 42。训练使用四张 Tesla V100-SXM2-16GB，通过 DDP 进行完整训练；每卡 batch size 为 4，验证 batch size 为 8，初始学习率为 7.5e-5，weight decay 为 1.5e-4。训练增强包括随机翻转、旋转、椒盐噪声和随机裁剪。每个实验保存配置、日志、权重、预测结果和评估结果。结构复杂度统计在 416 输入和 batch size 1 下统计参数量、GMACs、模型大小和峰值显存。

进入论文主结果表的评测必须满足三个条件：预测图数量与 GT 数量一致，预测图为概率灰度图而不是二值图，并且能够追溯评测协议、代码版本、权重路径和证据状态。该规则用于区分完整主结果、历史参考、CAMO-only 验证和待完成分支。

### 4.3 Baseline 核验与证据边界

本文对 ESCNet-B5 基线采用分层证据。第一，固定的 ESCNet-B5 源码版本能够严格加载历史教师权重，missing keys 和 unexpected keys 均为 0，说明权重与模型结构匹配。第二，ESCNet-B5 已完成 CAMO、COD10K 和 NC4K 三个数据集的同协议概率图复评，分别得到 CAMO S/wF/MAE=0.881/0.842/0.043、COD10K S/wF/MAE=0.877/0.802/0.021、NC4K S/wF/MAE=0.897/0.857/0.029。第三，预测数量与标注数量一致，概率图评测和证据登记已完成，因此该行可作为本文当前的固定源码同协议 ESCNet-B5 基线。

因此，下文涉及 Light-ESCNet 与 ESCNet-B5 的精度差值均以固定源码同协议概率图复评为准。历史结果文件只作为参考证据，不再作为当前主差值口径。

### 4.4 精度结果

表 1 给出当前已完成的 Light-ESCNet B2-C64 概率图评测结果、在线 KD 版本结果，以及固定源码同协议 ESCNet-B5 基线。三者均使用概率图评测，适合直接分析结构压缩和 KD 后的精度变化。

| 模型 | 证据状态 | CAMO S/wF/MAE | COD10K S/wF/MAE | NC4K S/wF/MAE |
| --- | --- | --- | --- | --- |
| ESCNet-B5 C128 | 固定源码同协议基线 | 0.881/0.842/0.043 | 0.877/0.802/0.021 | 0.897/0.857/0.029 |
| Light-ESCNet B2-C64 | 概率图评测已完成 | 0.862/0.818/0.051 | 0.866/0.782/0.024 | 0.886/0.840/0.033 |
| Light-ESCNet B2-C64 + KD | 完整评测已完成；不作为提升主张 | 0.863/0.818/0.050 | 0.864/0.782/0.024 | 0.885/0.838/0.033 |

从三数据集平均结果看，Light-ESCNet B2-C64 的 S-measure 为 0.871，固定 ESCNet-B5 基线为 0.885，差值为 -0.014；MAE 从 0.031 增加到 0.036，差值为 +0.005。分数据集看，Light-ESCNet 在 COD10K 和 NC4K 上的 S-measure 差值均为 -0.011；CAMO 上 weighted F-measure 和 MAE 下降更明显，说明轻量模型在小样本、弱边界和复杂纹理干扰场景中仍有细节恢复不足的问题。KD student 与 no-KD student 的三数据集均值几乎一致：平均 S-measure 约 -0.001，weighted F-measure 约 -0.001，MAE 基本不变；因此本文不把在线输出级 KD 写作精度补偿成功。

表 2 给出更完整的五项指标。

| 模型 | 数据集 | S | wF | mF | mE | MAE | 证据状态 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| ESCNet-B5 C128 | CAMO | 0.881 | 0.842 | 0.864 | 0.933 | 0.043 | 固定源码同协议基线 |
| ESCNet-B5 C128 | COD10K | 0.877 | 0.802 | 0.824 | 0.938 | 0.021 | 固定源码同协议基线 |
| ESCNet-B5 C128 | NC4K | 0.897 | 0.857 | 0.878 | 0.942 | 0.029 | 固定源码同协议基线 |
| Light-ESCNet B2-C64 | CAMO | 0.862 | 0.818 | 0.843 | 0.918 | 0.051 | 当前主结果 |
| Light-ESCNet B2-C64 | COD10K | 0.866 | 0.782 | 0.808 | 0.928 | 0.024 | 当前主结果 |
| Light-ESCNet B2-C64 | NC4K | 0.886 | 0.840 | 0.862 | 0.933 | 0.033 | 当前主结果 |
| Light-ESCNet B2-C64 + KD | CAMO | 0.863 | 0.818 | 0.844 | 0.920 | 0.050 | 负结果分析 |
| Light-ESCNet B2-C64 + KD | COD10K | 0.864 | 0.782 | 0.809 | 0.929 | 0.024 | 负结果分析 |
| Light-ESCNet B2-C64 + KD | NC4K | 0.885 | 0.838 | 0.860 | 0.932 | 0.033 | 负结果分析 |

这些结果说明，B2-C64 的结构压缩带来了一定精度损失，尤其体现在 wF 和 MAE 上；但在 S-measure 上仍保持较接近的整体结构感知能力。该现象符合伪装目标分割的任务特点：模型压缩后高层定位能力仍可保持，但弱边界和局部细节更容易受影响。

从模型设计角度看，这一结果支持“保留边界协同再压缩容量”作为当前阶段的主线假设，但是否优于删除或弱化边界路径仍需要边界分支消融确认。S-measure 对整体区域结构更敏感，而 wF 和 MAE 更容易反映边界错分、局部漏检和背景误检；Light-ESCNet 在这些指标上的差异提示后续补偿应优先围绕边界质量和局部细节展开。因此，KD、边界消融和可视化分析不是额外装饰，而是解释轻量化损失来源和补偿方向的必要实验。

### 4.5 效率结果

表 3 给出 ESCNet-B5 C128 与 Light-ESCNet B2-C64 的结构效率对比。

| 模型 | 参数量(M) | GMACs | 模型大小(MB) | 峰值显存(MB) | 结构降幅 |
| --- | ---: | ---: | ---: | ---: | --- |
| ESCNet-B5 C128 | 99.90 | 129.02 | 381.17 | 829.77 | 参考 |
| Light-ESCNet B2-C64 | 29.81 | 36.39 | 113.74 | 237.44 | 参数量 -70.16%; GMACs -71.79%; 模型大小 -70.16%; 显存 -71.38% |

与精度下降幅度相比，结构复杂度下降更加显著。相对固定源码同协议 ESCNet-B5 基线，Light-ESCNet 以平均 S-measure 下降 0.014、MAE 增加 0.005 的代价，将参数量、GMACs、模型大小和峰值显存均降低约 70%。这一对比说明，同族 PVTv2 主干缩放和解码器窄化能够有效降低模型部署成本。

表 4 给出空闲 V100 上的同命令速度复测结果。该复测使用 416 输入、batch size 1、warmup=50、repeat=100。Light-ESCNet no-KD 的单张延迟为 34.31 ms，ESCNet-B5 为 73.01 ms；对应 FPS 分别为 29.15 和 13.70。KD student 结构与 no-KD student 相同，推理侧结果接近，为 34.84 ms 和 28.71 FPS。

| 模型 | 延迟(ms) | FPS | 测量条件 |
| --- | ---: | ---: | --- |
| ESCNet-B5 C128 | 73.01 | 13.70 | V100, 416, batch 1 |
| Light-ESCNet B2-C64 | 34.31 | 29.15 | V100, 416, batch 1 |
| Light-ESCNet B2-C64 + KD | 34.84 | 28.71 | V100, 416, batch 1 |

![图 2 平均 S-measure 与 GMACs 的精度-效率折中](../figures/accuracy_efficiency_scatter.png)

### 4.6 消融与待补实验

当前已完成的核心实验是 Light-ESCNet B2-C64 no-KD，KD student 也已完成但未带来稳定正向收益。为了进一步拆分不同设计因素，后续实验将重点验证：

1. 主干压缩：比较 PVTv2-B5 与 PVTv2-B2 的精度和效率变化。
2. 解码宽度：比较 C128 与 C64，分析窄解码器的性价比。
3. 边界分支：移除或弱化边界辅助监督，观察 CAMO 等弱边界场景中的 MAE 和 wF 变化。
4. 知识蒸馏替代形式：当前在线输出级 MSE KD 未改善 no-KD student，后续若继续探索，应优先考虑 teacher cache、特征级蒸馏或边界蒸馏，并单独标注实验定义变化。
5. 极限压缩与替代主干：观察 PVTv2-B0 分支在更小容量下的稳定性和精度下限，并记录 MobileMamba-T2 作为替代轻量主干的高风险探索。

这些分支在完整权重、三数据集概率图评测和完整性检查完成前，只作为待补实验或工程观察，不进入本文当前结果表。当前 KD 分支已经满足完整评测条件，但由于结果不支持精度改善，只进入负结果分析，不改变 Light no-KD 作为主学生结果的定位。

当前 KD 结果说明，单纯 online output-level MSE 约束不足以稳定补偿 B2-C64 的容量损失，还会显著增加训练吞吐和调度成本。对于 B0 极限压缩分支，当前 COD10K 中间结果已经显示其容量下限风险较高，因此它更适合作为高风险探索或失败分析，而不是替代 B2-C64 主线。MobileMamba-T2 外部探索分支仍在未隔离的实验目录中观察，只能作为替代轻量主干记录；在完成独立代码归档、权重加载核验、结构复杂度统计、三数据集概率图评测和完整性检查前，不进入主表、摘要或结论。

### 4.7 可视化分析

当前已基于 CAMO 样本生成 Image、GT、ESCNet-B5 reference 和 Light-ESCNet B2-C64 的可视化对比。CAMO 250 个样本的 per-image MAE 统计显示，Light 相对 reference 的平均 MAE delta 为 +0.008056，其中 140 个样本 `abs(delta)<0.005`，36 个样本 `delta>=0.02`，13 个样本 `delta<=-0.02`。人工检查显示，Light-ESCNet 在部分样本中能够保持目标整体区域，并减少一些背景误检；但在复杂纹理、细长结构、多目标粘连和弱边界区域中更容易出现边界扩张、目标局部漏检或背景高置信误检。这与表格结果一致：S-measure 的整体下降较小，而 wF 和 MAE 对边界质量和局部错分更敏感。详细选例和边界说明见 `camo_failure_case_analysis.md`。

KD 分支已完成数值评测；后续若扩展可视化图，可增加 KD 列，用于分析为什么在线输出级蒸馏没有稳定改善边界断裂、局部漏检和背景误检。

![图 3 CAMO 样本可视化对比](../figures/camo_visual_grid_b5_light_b2c64.png)

### 4.8 当前运行状态

Light-ESCNet B2-C64 no-KD 已完成 120 epoch 四卡训练、三数据集概率图评测、结构复杂度统计和受控速度复测，可作为当前论文主结果。ESCNet-B5 固定源码同协议复评已完成 CAMO、COD10K 和 NC4K，可作为当前重模型基线。KD 分支已完成 120 epoch 训练、三数据集概率图评测和受控速度复测，但相对 no-KD student 基本持平或略低，因此只作为负结果分析。

PVTv2-B0 和 MobileMamba-T2 分支只作为外部探索证据，用于判断极限压缩和替代轻量主干的风险；它们尚未完成独立代码归档、权重核验、结构复杂度统计、CAMO/COD10K/NC4K 概率图评测和完整性检查，因此不进入主表、摘要或结论。实时训练进度和 COD10K 中间观察不在正文展开，统一由对应实验状态文件记录。

## 5 结论

本文围绕“面向伪装目标分割的轻量化模型研究”构建了基于 ESCNet 的可复查实验流程，并提出 Light-ESCNet B2-C64 作为主力轻量模型。该模型保留 ESCNet 的边缘-语义协同机制，同时将主干由 PVTv2-B5 缩小到 PVTv2-B2，并将解码器隐藏通道由 128 降至 64。已完成实验表明，Light-ESCNet B2-C64 在三数据集概率图评测中保持了接近固定源码同协议 ESCNet-B5 基线的 S-measure，同时将参数量、GMACs、模型大小和峰值显存降低约 70%。

当前结果支持一个相对简单但有价值的结论：对于伪装目标分割，轻量化不应只追求删除模块或减少通道，而应尽量保留对弱边界和复杂纹理场景有帮助的结构归纳偏置。Light-ESCNet 的结果说明，保留边缘-语义协同并压缩主干和解码宽度，是一条可复现的精度-效率折中路线。

本文仍有若干限制。第一，当前结论主要来自 B2-C64 这一条轻量化路径，主干压缩、解码宽度和边界分支的独立贡献仍需更多消融。第二，在线输出级 MSE KD 已完成但没有带来稳定改善，说明轻量模型的补偿可能需要更有针对性的边界或特征级蒸馏。第三，速度复测仍局限于 V100 上的受控测量，尚未覆盖真实边缘设备部署。后续工作将继续完成边界分支消融、KD 替代形式和更贴近部署环境的速度测试，并进一步探索极限压缩模型的稳定性。

从当前阶段看，本文最稳定的结论是：Light-ESCNet B2-C64 用约 70% 的结构复杂度下降换取较小的整体结构感知损失，并在受控 V100 测量中呈现更低单张延迟和更高吞吐；但细节质量仍需要补偿，且当前在线输出级 KD 没有解决这一问题。

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
