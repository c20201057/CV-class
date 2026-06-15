# 方法更新

本文档记录当前工作区已经加入的实现更新。
English version: `method.md`。

当本文档发生变化时，请在同一次修改中同步更新 `method.md`，保证两份文档内容一致。

## Backbone 更新

### MobileMamba 延迟导入

`models/backbones/build_backbone.py` 现在使用显式 backbone 注册表，不再通过 `eval` 构建模型。
MobileMamba 相关 backbone 只会在选择 `mobilemamba_*` backbone 时才被延迟导入。这样 PVT 或 PoolFormer 实验在导入阶段不会依赖 MobileMamba 专属依赖。

### PoolFormer-S12 Backbone

新增 `poolformer_s12`，作为 COD 实验中的轻量化层级 backbone。

- Wrapper：`models/backbones/poolformer.py`
- 注册入口：`models/backbones/build_backbone.py`
- 配置字段：`config.py` 中的 `weights.poolformer_s12`
- 训练配置：`configs/poolformer_s12.yaml`
- Backbone 参数量：`11,401,152`
- 特征通道：`[64, 128, 320, 512]`
- 特征下采样倍率：`[4, 8, 16, 32]`
- ESCNet lateral channels：`[512, 320, 128, 64]`

权重：

- 原始官方 checkpoint：`/root/data-tmp/weights/poolformer_s12.pth.tar`
- 转换后的 timm feature 模型兼容 checkpoint：`/root/data-tmp/weights/poolformer_s12.timm.pth`

原始 checkpoint 使用官方 PoolFormer 的键名。它已被转换成 timm feature 模型键名，因此可以直接复用现有 `load_weights` 加载路径。

运行：

```bash
cd /root/CV-class
bash run.sh -c configs/poolformer_s12.yaml
```

## 蒸馏更新

此前的蒸馏 loss 只对齐输出 logits：

- mask logits：使用 temperature-scaled BCE
- edge logits：使用 temperature-scaled BCE

现在新增 feature-level distillation，用于对齐 Teacher 和 Student 的 backbone 输出。

### Backbone Feature Alignment Loss

在 `loss.py` 中新增 `BackboneFeatureDistillationLoss`。

对于每一个 backbone stage，该 loss 由两部分组成：

- 归一化 feature MSE
- 基于空间能量图的 attention transfer loss

attention map 根据通道能量计算：

```text
A(F) = L2Normalize(flatten(mean(F^2, channel)))
```

整体 feature 对齐项为：

```text
L_feature = feature_mse_weight * L_mse + feature_attention_weight * L_at
L_total_kd = L_logit_kd + feature_loss_weight * L_feature
```

### Mask-Guided Feature Distillation

新增可选的 mask-guided feature alignment，用于更贴合 COD 训练。该方法只在训练时复用 GT mask 和 edge map，将它们下采样到每个 backbone stage，并对目标区域和边界区域赋予更高 loss 权重：

```text
W = Normalize(1 + feature_mask_foreground_weight * GT + feature_mask_edge_weight * Edge)
L_mask_feature = mean(W * ||Normalize(F_student) - Normalize(F_teacher)||^2)
```

完整 feature loss 现在为：

```text
L_feature =
  feature_mse_weight * L_mse
  + feature_attention_weight * L_at
  + feature_mask_guided_weight * L_mask_feature
```

该方法只影响训练，不增加推理开销。默认通过 `feature_mask_guided_weight: 0.0` 关闭。

同时支持 stage 权重和 feature loss warmup：

- `feature_stage_weights`：可选的逐 stage 权重，适合更强调深层语义特征
- `feature_loss_warmup_epochs`：在训练早期线性增加 `feature_loss_weight`

### 通道适配器

Teacher 和 Student backbone 可能具有不同的通道宽度。启用 feature distillation 时，`ESCNet` 会自动创建可选的 `feature_adapters`：

- adapter 是 1x1 convolution
- adapter 属于 Student model，因此 DDP、optimizer、checkpoint 保存和梯度同步都会正确处理它
- 构建 teacher model 加载 checkpoint 时会禁用 teacher adapter

示例：

- `poolformer_s12 -> pvt_v2_b5`：通道已经一致，因此 adapter 是 identity module
- `pvt_v2_b0 -> pvt_v2_b5`：adapter 将 `[32, 64, 160, 256]` 映射到 `[64, 128, 320, 512]`

### 配置字段

在 `distillation` 配置中新增：

```yaml
feature_loss_weight: 0.05
feature_loss_warmup_epochs: 0
feature_mse_weight: 1.0
feature_attention_weight: 0.5
feature_mask_guided_weight: 0.0
feature_mask_foreground_weight: 2.0
feature_mask_edge_weight: 3.0
feature_stage_weights: null
```

同时新增 teacher-structure distillation 配置：

```yaml
teacher_structure_loss_weight: 0.0
teacher_structure_loss_levels: final
teacher_structure_temperature: 1.0
```

该 loss 使用同样的边界感知 structure loss，让 Student mask 学习 Teacher 的 soft mask。默认关闭。

`feature_loss_weight: 0.0` 会关闭 feature distillation，并保持旧行为不变。

已在以下配置中启用：

- `configs/poolformer_s12.yaml`
- `configs/pvt_v2_b0_lowerlr.yaml`
- `configs/pvt_v2_b0.yaml`

### Finetune Resume 控制

新增可选 resume 控制项：

```yaml
resume_optimizer: true
resume_lr_scheduler: true
resume_scaler: true
resume_epoch: true
resume_strict: true
```

默认值保持此前的完整 resume 行为。用于 finetune 时，现在可以只加载模型权重，同时重置 optimizer、scheduler、AMP scaler 和 epoch 计数。`resume_strict: false` 适用于旧 checkpoint 训练完成后又新增了 feature adapter 这类训练模块的情况。

### 强化版 PoolFormer Mask-KD Finetune 配置

新增 `configs/poolformer_s12_maskkd_finetune.yaml`。它组合了当前最可能有效的轻量化改进：

- 从 `/root/data-tmp/ESCNet/checkpoints/poolformer_s12_higherlr/latest.ckpt` 初始化
- 重置 optimizer/scheduler/scaler/epoch，保证干净 finetune
- 使用更强的 mask 和 edge logit KD
- 提高 feature KD 权重，并加入 warmup
- 启用 mask-guided feature KD，并加强边界区域权重
- 略微提高 supervised edge loss 权重

运行：

```bash
cd /root/CV-class
bash run.sh -c configs/poolformer_s12_maskkd_finetune.yaml
```

### PVT-v2-B0 Mask-KD Finetune 配置

对比当前 log 和 result 后，新增 `configs/pvt_v2_b0_maskkd_finetune.yaml`。`pvt_v2_b0_lowerlr` 在 epoch 120 达到 `S=0.8097`、`wF=0.7052`、`MAE=0.0317`，且后期曲线仍有提升，说明在当前框架里 PVT-v2-B0 比 PoolFormer-S12 更有继续优化的空间。

该配置：

- 从 `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0_lowerlr/epoch_120.pth` 初始化
- 重置 optimizer/scheduler/scaler/epoch，进行干净的低学习率 finetune
- 使用 `resume_strict: false`，让新增的 feature adapter 可以正常初始化
- 相比 PoolFormer mask-KD 方案，更保守地使用 feature KD
- 略微加强 mask/edge KD 和 supervised edge loss
- 通过 `feature_stage_weights: [0.4, 0.8, 1.2, 1.4]` 更强调深层语义特征

运行：

```bash
cd /root/CV-class
bash run.sh -c configs/pvt_v2_b0_maskkd_finetune.yaml
```

### PVT-v2-B0 512 Structure-KD 配置

在 PVT-v2-B0 mask-KD finetune 只有小幅提升后，新增更激进的 `configs/pvt_v2_b0_512_structkd.yaml`。这个方向不再继续强化已经较弱的 feature KD，而是直接优化 mask 质量：

- 使用 `512x512` 训练和评估，保留更多边界与小目标细节
- 从 epoch 0 训练 ESCNet，不 resume 任何 ESCNet checkpoint
- 使用 `120` epochs 和 `lr: 5e-5`，这是针对 512 分辨率小 batch 更保守的完整训练学习率
- 对 GT mask 使用 weighted structure loss
- 使用 teacher final soft mask 加入 teacher-structure KD
- 加入较小权重的 mask-edge consistency loss
- 关闭 feature KD，避免优化被较弱的 adapter 对齐信号牵制
- 增加 color enhancement 数据增强

这是一个风险更高但更可能突破现有平台期的实验。为控制显存，配置中使用 `batch_size: 2` 和 `batch_size_valid: 4`。PVT-v2-B0 backbone 仍使用配置中的 ImageNet 预训练权重；这里只关闭 ESCNet 训练 checkpoint resume。

运行：

```bash
cd /root/CV-class
bash run.sh -c configs/pvt_v2_b0_512_structkd.yaml
```

### PVT-v2-B0 512 No-TS 配置

新增 `configs/pvt_v2_b0_512_no_ts.yaml`，作为激进 512 实验的无 Teacher-Student 直接对照组。

它保留 `pvt_v2_b0_512_structkd.yaml` 中不依赖蒸馏的改动：

- `512x512` 训练和评估
- weighted GT structure loss
- 更强的 supervised edge loss
- final mask 的 edge consistency loss
- color enhancement 数据增强
- 不 resume 任何 ESCNet 训练 checkpoint
- `120` epochs 和 `lr: 5e-5`

它通过 `enabled: false` 关闭整个 `distillation` 模块，因此不会构建 teacher model，也不会使用任何 TS/KD loss。这个配置可以作为干净消融，用来判断收益主要来自高分辨率结构训练，还是来自 Teacher-Student 监督。

运行：

```bash
cd /root/CV-class
bash run.sh -c configs/pvt_v2_b0_512_no_ts.yaml
```

## Decoder/Head 轻量化更新

新增独立轻量模型架构 `lite_escnet`，不改变原始 `escnet` 模型。

相关文件：

- `models/LiteESCNet.py`
- `models/build_model.py`
- 配置字段：`architecture`，默认值为 `escnet`
- 配置字段：`lite_head_channels`，默认值为 `64`
- 训练配置：`configs/pvt_v2_b0_litehead_512_no_ts.yaml`

轻量模型保留所选 backbone，但将原 ESCNet 的重型 head 替换为紧凑的 depthwise-separable FPN：

- 使用 1x1 projection 将 backbone 多层特征映射到统一轻量通道数
- top-down 融合使用 depthwise-separable convolution 和轻量 channel gate
- edge prediction 使用浅层高分辨率融合特征
- 仍返回 4 个 mask logits，保持现有 multi-level structure loss 接口不变

在 PVT-v2-B0 和 `lite_head_channels: 64` 下，学生模型约 `3.50M` 参数：

- 总参数：约 `3.50M`
- backbone：约 `3.41M`
- lightweight decoder/head：约 `0.09M`

这比单纯更换 backbone 更直接地实现轻量化，因为原 PVT-v2-B0 ESCNet 模型约 `21.80M` 参数，其中大部分参数集中在 decoder/head。

运行：

```bash
cd /root/CV-class
bash run.sh -c configs/pvt_v2_b0_litehead_512_no_ts.yaml
```

## 保持 ESCNet 方法结构的 Slim 更新

新增 `escnet_slim`，作为更忠实于原 ESCNet 方法的轻量版本。不同于 `lite_escnet`，该版本保留原 ESCNet decoder/head 的核心设计：

- AETP edge prediction
- FEM blocks
- MTA blocks
- deformable convolutions
- image patch injection
- edge-guided semantic decoding
- 4 个 mask 输出和 1 个 edge 输出

唯一的结构性缩减是降低 ESCNet 内部统一通道宽度：

```yaml
architecture: escnet_slim
escnet_width: 64
```

原始 `escnet` 仍保持 `escnet_width: 128`，因此已有配置维持原模型不变。PVT-v2-B0 slim 配置为 `configs/pvt_v2_b0_escnet_slim_512_no_ts.yaml`。

在 PVT-v2-B0 下，`escnet_width: 64` 约 `8.34M` 参数：

- backbone：约 `3.41M`
- 保持原方法结构的 slim decoder/head：约 `4.93M`

作为对比，原始宽度的 PVT-v2-B0 ESCNet 约 `21.80M` 参数。

这个版本不如 `lite_escnet` 激进，但更适合需要声明“基本保持原 ESCNet 方法，只做轻量化宽度缩放”的实验。

运行：

```bash
cd /root/CV-class
bash run.sh -c configs/pvt_v2_b0_escnet_slim_512_no_ts.yaml
```

## 其它可选高级对齐 Loss

当前实现使用 feature MSE 加 attention transfer，因为它稳定、开销低，并且适用于 Teacher/Student 架构不同的情况。对于 COD，还可以考虑以下高级对齐 loss：

### Relational Knowledge Distillation

对齐像素或 patch 之间的成对关系，而不是直接对齐原始 feature 值。这能更好地迁移 teacher 的上下文建模能力和前景/背景分离能力，但显存开销更高。

### Contrastive Feature Distillation

使用 GT mask 的前景/背景区域构造正负 feature pair。该方法很适合 COD，因为模型需要从高度相似的背景中分离伪装目标。需要谨慎采样，避免小目标带来的噪声。

### Mask-Guided Feature Distillation

使用 GT mask、edge mask 或 teacher confidence map 对 feature 对齐进行加权。这样可以让 KD 更关注目标内部和边界区域，减少强制复制背景激活的压力。

### Channel-Wise KL Distillation

将每层 feature map 转换为通道分布，并最小化 Teacher 与 Student 之间的 KL divergence。该方法可以迁移通道重要性，对空间错位不如像素级 MSE 敏感。

### Multi-Scale Gram Loss

在每个 stage 对齐 feature covariance 或 Gram matrix。它可以迁移纹理和上下文统计信息，但相比 attention 或 mask-guided loss，与目标定位的关联可能更弱。

## 验证

已完成的针对性检查：

- 修改过的 Python 文件通过 `py_compile`
- `configs/poolformer_s12.yaml` 能够加载转换后的 checkpoint
- PoolFormer-S12 预训练权重转换后能严格匹配 timm feature 模型
- 对 `416x416` 输入，PoolFormer-S12 backbone 输出四层 feature，分辨率为 `[104, 52, 26, 13]`
- 使用 PoolFormer-S12 的完整 ESCNet 前向输出 edge shape `(1, 1, 416, 416)`
- `pvt_v2_b0 -> pvt_v2_b5` feature KD 小前向/反向传播通过
- PVT-B0 feature adapters 能收到梯度
