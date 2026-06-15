# Light-ESCNet B2-C64 方法说明

更新时间：2026-06-13T16:24:17Z

本文件用于组内讲解、答辩和论文方法图绘制。它解释的是当前已完成主实验 `light_b2_c64_e120_s42`，不是 KD 版本。

## 一句话概括

Light-ESCNet B2-C64 是在 ESCNet 上做的可控轻量化版本：把重主干 PVTv2-B5 换成 PVTv2-B2，把边缘-语义解码通道从 128 压到 64，但保留 ESCNet 对伪装目标很关键的边缘预测和 edge-guided decoder。

## 名字含义

- `B2`：backbone 使用 PVTv2-B2。
- `C64`：AETP、FEM、MTA、预测头等解码与协同模块的中间通道数使用 64。
- `Light`：相对 ESCNet-B5 C128 的轻量化结构。

对应配置：

```yaml
backbone: pvt_v2_b2
lateral_channels: [512, 320, 128, 64]
inter_channel: 64
bb_pretrained: true
```

论文和复现实验应优先引用已验收 run 配置：

```text
/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/config.yaml
```

源码目录里的默认 `config.yaml` 仍保留了 ESCNet 基底默认值，不能单独作为 Light-B2-C64 训练证据。

## 模型流程

```text
Input Image I
  -> PVTv2-B2 Encoder
  -> four-level features F1, F2, F3, F4
  -> 1x1 projection to 64 channels: X1, X2, X3, X4
  -> AETP edge branch predicts edge logits E
  -> Decoder uses sigmoid(E) to guide multi-scale semantic fusion
  -> mask logits P4, P3, P2, P1
```

`F1` 分辨率最高，保留纹理和细节；`F4` 语义最强，用于定位目标大致区域。四级特征先通过 1x1 convolution 对齐到 64 通道，这是 C64 的核心入口。

## 为什么保留边缘分支

伪装目标分割的难点不是普通前景背景差异，而是目标和背景纹理、颜色、亮度非常接近。模型容易知道“这里可能有东西”，但难以确定“边界在哪里”。因此 Light-ESCNet 没有直接砍掉 ESCNet 的边缘分支，而是保留 AETP：

```text
E = AETP(X1, X2, X3, X4)
```

AETP 把深层语义逐级上采样，与浅层细节融合，使用可变形卷积和空间注意力产生边缘预测。这个边缘预测不是最终结果，而是给 decoder 当结构提示。

## Decoder 怎么用边缘

Decoder 在每个尺度上做三件事：

1. 从原图切出与当前特征分辨率对应的 patch 信息，补充局部纹理。
2. 把 patch 信息和当前尺度特征拼接。
3. 使用 edge-guided FEM，让边缘图参与可变形卷积和多尺度卷积融合。

随后模型从深层到浅层逐步恢复 mask：

```text
P4 -> P3 -> P2 -> P1
```

`P4` 最粗，`P1` 最细。训练时多尺度预测共同参与损失，推理时使用最高分辨率预测。

## 轻量化来自哪里

Light-B2-C64 的压缩来自两个位置：

1. Encoder 压缩：PVTv2-B5 -> PVTv2-B2。
2. Decoder/edge branch 压缩：inter_channel 128 -> 64。

第二点很重要，因为 ESCNet 的后半部分并不小。把 `inter_channel` 降到 64 后，AETP、FEM、MTA 和预测头中的卷积计算都会同步减少。

可以把 B2-C64 理解成两个控制变量同时收缩：

- `B2` 收缩 encoder 的语义容量和 Transformer 计算。
- `C64` 收缩边缘预测、局部 patch 融合、edge-guided FEM、MTA 解码块和 mask head 的共同中间宽度。

因此它不是“换个小 backbone 就结束”，而是 encoder 和 decoder 两端都降复杂度，同时保留 ESCNet 原本针对弱边界设计的结构路径。

## 为什么不是直接换 MobileNet

当前路线选择 PVTv2-B2，而不是直接换 MobileNet/ShuffleNet，原因是控制变量更清楚：

- PVTv2-B2 与 PVTv2-B5 都输出四级金字塔特征。
- 特征尺度和 decoder 接口保持兼容。
- 这样能把主要变化控制在 backbone 容量和 decoder 宽度，而不是重新适配一套完全不同的特征体系。

这种同族替换减少了接口适配变量，使实验更能聚焦于主干容量和解码宽度对精度-效率折中的影响。

换成完全不同的小主干也不是不能做，但那会引入新的变量：特征尺度、通道维度、预训练权重、token/卷积表征差异、decoder 接口适配都会同时变化。B2-C64 的价值是先回答一个更可验收的问题：在 ESCNet 原有边缘-语义协同框架内，只缩放同族 PVTv2 主干和 decoder 宽度，能获得怎样的精度-效率折中。

## 当前实验证据

Light-B2-C64 no-KD 已完成 120 epoch 和三数据集概率图评测：

| Dataset | S-measure | wF | MAE |
| --- | ---: | ---: | ---: |
| CAMO | 0.862 | 0.818 | 0.051 |
| COD10K | 0.866 | 0.782 | 0.024 |
| NC4K | 0.886 | 0.840 | 0.033 |

相对历史 ESCNet-B5，平均 S-measure 下降约 0.009，MAE 增加约 0.006。结构 profile 显示：

| Model | Params | GMACs | Model Size | Peak Mem |
| --- | ---: | ---: | ---: | ---: |
| ESCNet-B5 C128 | 99.90M | 129.02 | 381.17 MB | 829.77 MB |
| Light-B2-C64 | 29.81M | 36.39 | 113.74 MB | 237.44 MB |

因此论文主张应是：Light-B2-C64 在显著压缩复杂度的同时保持接近性能，而不是宣称达到 SOTA。

## 方法图建议

建议画成四段：

1. 左侧输入图像。
2. 中间 PVTv2-B2 encoder 输出四级特征。
3. 上方 AETP edge branch 输出 edge map。
4. 下方 edge-guided decoder 输出多尺度 masks。

图中标注两个轻量化点：

- `Backbone: PVTv2-B5 -> PVTv2-B2`
- `Decoder width: C128 -> C64`

不要把 KD 画进主模型图。KD 是补偿训练分支，等完整训练和评估完成后再画 teacher-student training diagram。
