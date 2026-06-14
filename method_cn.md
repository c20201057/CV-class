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
feature_mse_weight: 1.0
feature_attention_weight: 0.5
```

`feature_loss_weight: 0.0` 会关闭 feature distillation，并保持旧行为不变。

已在以下配置中启用：

- `configs/poolformer_s12.yaml`
- `configs/pvt_v2_b0_lowerlr.yaml`
- `configs/pvt_v2_b0.yaml`

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
