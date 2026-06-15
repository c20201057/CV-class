# Method Updates

This document records the implementation updates added to this workspace.
Chinese version: `method_cn.md`.

When this file changes, update `method_cn.md` in the same commit so the two documents stay synchronized.

## Backbone Updates

### Lazy MobileMamba Import

`models/backbones/build_backbone.py` now uses an explicit backbone registry instead of `eval`.
MobileMamba backbones are imported lazily only when a `mobilemamba_*` backbone is selected. This prevents PVT or PoolFormer runs from requiring MobileMamba-only dependencies at import time.

### PoolFormer-S12 Backbone

Added `poolformer_s12` as a lightweight hierarchical backbone for COD experiments.

- Wrapper: `models/backbones/poolformer.py`
- Registry entry: `models/backbones/build_backbone.py`
- Config field: `weights.poolformer_s12` in `config.py`
- Training config: `configs/poolformer_s12.yaml`
- Backbone parameters: `11,401,152`
- Feature channels: `[64, 128, 320, 512]`
- Feature reductions: `[4, 8, 16, 32]`
- ESCNet lateral channels: `[512, 320, 128, 64]`

Weights:

- Original official checkpoint: `/root/data-tmp/weights/poolformer_s12.pth.tar`
- Converted timm-compatible feature checkpoint: `/root/data-tmp/weights/poolformer_s12.timm.pth`

The original checkpoint uses official PoolFormer key names. It was converted to timm feature-model key names so the existing `load_weights` path can load it directly.

Run:

```bash
cd /root/CV-class
bash run.sh -c configs/poolformer_s12.yaml
```

## Distillation Updates

The previous distillation loss aligned only output logits:

- mask logits via temperature-scaled BCE
- edge logits via temperature-scaled BCE

Feature-level distillation has been added to align Teacher and Student backbone outputs.

### Backbone Feature Alignment Loss

Added `BackboneFeatureDistillationLoss` in `loss.py`.

For each backbone stage, the loss combines:

- normalized feature MSE
- attention transfer loss over spatial energy maps

The attention map is computed from channel energy:

```text
A(F) = L2Normalize(flatten(mean(F^2, channel)))
```

The total feature alignment term is:

```text
L_feature = feature_mse_weight * L_mse + feature_attention_weight * L_at
L_total_kd = L_logit_kd + feature_loss_weight * L_feature
```

### Mask-Guided Feature Distillation

Added optional mask-guided feature alignment for COD-focused training. It reuses the GT mask and edge map at training time, downsamples them to each backbone stage, and gives higher loss weight to object and boundary pixels:

```text
W = Normalize(1 + feature_mask_foreground_weight * GT + feature_mask_edge_weight * Edge)
L_mask_feature = mean(W * ||Normalize(F_student) - Normalize(F_teacher)||^2)
```

The full feature loss is now:

```text
L_feature =
  feature_mse_weight * L_mse
  + feature_attention_weight * L_at
  + feature_mask_guided_weight * L_mask_feature
```

This is training-only and does not add inference cost. It is disabled by default through `feature_mask_guided_weight: 0.0`.

Stage weights and feature-loss warmup are also supported:

- `feature_stage_weights`: optional per-stage weighting, useful for emphasizing deeper semantic features
- `feature_loss_warmup_epochs`: linearly ramps `feature_loss_weight` during early epochs

### Channel Adapters

Teacher and Student backbones may have different channel widths. `ESCNet` now creates optional `feature_adapters` when feature distillation is enabled:

- adapters are 1x1 convolutions
- adapters are part of the Student model, so DDP, optimizer, checkpoint saving, and gradient synchronization handle them correctly
- teacher adapters are disabled when building the teacher model for checkpoint loading

Examples:

- `poolformer_s12 -> pvt_v2_b5`: channels already match, so adapters are identity modules
- `pvt_v2_b0 -> pvt_v2_b5`: adapters map `[32, 64, 160, 256]` to `[64, 128, 320, 512]`

### Config Fields

Added to `distillation` config:

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

Teacher-structure distillation fields were also added:

```yaml
teacher_structure_loss_weight: 0.0
teacher_structure_loss_levels: final
teacher_structure_temperature: 1.0
```

This loss supervises Student masks with the Teacher's soft mask using the same boundary-aware structure loss. It is disabled by default.

`feature_loss_weight: 0.0` disables feature distillation and preserves old behavior.

Enabled in:

- `configs/poolformer_s12.yaml`
- `configs/pvt_v2_b0_lowerlr.yaml`
- `configs/pvt_v2_b0.yaml`

### Resume Control for Finetuning

Added optional resume controls:

```yaml
resume_optimizer: true
resume_lr_scheduler: true
resume_scaler: true
resume_epoch: true
resume_strict: true
```

The defaults preserve the previous full-resume behavior. For finetuning, a config can now load model weights while resetting optimizer, scheduler, AMP scaler, and epoch counter. `resume_strict: false` is useful when a new training-only module, such as feature adapters, has been added after an older checkpoint was trained.

### Strong PoolFormer Mask-KD Finetune Config

Added `configs/poolformer_s12_maskkd_finetune.yaml`. It combines the currently most promising lightweight improvements:

- starts from `/root/data-tmp/ESCNet/checkpoints/poolformer_s12_higherlr/latest.ckpt`
- resets optimizer/scheduler/scaler/epoch for clean finetuning
- uses stronger mask and edge logit KD
- increases feature KD weight with warmup
- enables mask-guided feature KD with stronger boundary weighting
- slightly increases supervised edge loss weight

Run:

```bash
cd /root/CV-class
bash run.sh -c configs/poolformer_s12_maskkd_finetune.yaml
```

### PVT-v2-B0 Mask-KD Finetune Config

Added `configs/pvt_v2_b0_maskkd_finetune.yaml` after comparing the current logs/results. `pvt_v2_b0_lowerlr` reaches `S=0.8097`, `wF=0.7052`, and `MAE=0.0317` at epoch 120, and its curve is still improving late in training. This suggests PVT-v2-B0 has more headroom than PoolFormer-S12 in the current framework.

This config:

- starts from `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0_lowerlr/epoch_120.pth`
- resets optimizer/scheduler/scaler/epoch for clean low-lr finetuning
- uses `resume_strict: false` so newly added feature adapters can initialize cleanly
- keeps feature KD more conservative than the PoolFormer mask-KD run
- slightly strengthens mask/edge KD and supervised edge loss
- emphasizes deeper feature stages with `feature_stage_weights: [0.4, 0.8, 1.2, 1.4]`

Run:

```bash
cd /root/CV-class
bash run.sh -c configs/pvt_v2_b0_maskkd_finetune.yaml
```

### PVT-v2-B0 512 Structure-KD Config

Added `configs/pvt_v2_b0_512_structkd.yaml` as a more aggressive experiment after the PVT-v2-B0 mask-KD finetune only gave small gains. The new direction avoids pushing the already weak feature KD signal and instead attacks mask quality directly:

- trains/evaluates at `512x512` for more boundary and small-object detail
- trains ESCNet from epoch 0 without resuming any ESCNet checkpoint
- uses `120` epochs with `lr: 5e-5`, a conservative full-training LR for the smaller 512-resolution batch
- uses weighted structure loss for GT masks
- adds teacher-structure KD from the teacher's final soft mask
- adds a small mask-edge consistency loss
- disables feature KD so the optimization is not dominated by weak adapter alignment
- adds color enhancement augmentation

This is intentionally higher-risk and may need more memory, so the config uses `batch_size: 2` and `batch_size_valid: 4`. The PVT-v2-B0 backbone still uses its configured ImageNet pretrained weights; only ESCNet training checkpoint resume is disabled.

Run:

```bash
cd /root/CV-class
bash run.sh -c configs/pvt_v2_b0_512_structkd.yaml
```

### PVT-v2-B0 512 No-TS Config

Added `configs/pvt_v2_b0_512_no_ts.yaml` as the direct no-Teacher-Student control for the aggressive 512 experiment.

It keeps the non-distillation changes from `pvt_v2_b0_512_structkd.yaml`:

- `512x512` training/evaluation
- weighted GT structure loss
- stronger supervised edge loss
- final-mask edge consistency loss
- color enhancement augmentation
- no ESCNet training checkpoint resume
- `120` epochs with `lr: 5e-5`

It disables the whole `distillation` block with `enabled: false`, so no teacher model is built and no TS/KD loss is used. This makes it a clean ablation for checking whether the gain comes from higher-resolution structure training or from Teacher-Student supervision.

Run:

```bash
cd /root/CV-class
bash run.sh -c configs/pvt_v2_b0_512_no_ts.yaml
```

## Lightweight Decoder/Head Update

Added a separate lightweight model architecture, `lite_escnet`, without changing the original `escnet` model.

Files:

- `models/LiteESCNet.py`
- `models/build_model.py`
- config field: `architecture`, defaulting to `escnet`
- config field: `lite_head_channels`, defaulting to `64`
- training config: `configs/pvt_v2_b0_litehead_512_no_ts.yaml`

The lightweight model keeps the selected backbone but replaces the heavy ESCNet head with a compact depthwise-separable FPN:

- 1x1 projections map backbone features into a shared light channel width
- top-down fusion uses depthwise-separable convolution and a lightweight channel gate
- edge prediction uses shallow fused high-resolution features
- four mask logits are still returned, preserving the existing multi-level structure loss interface

With PVT-v2-B0 and `lite_head_channels: 64`, the student model has about `3.50M` parameters:

- total: about `3.50M`
- backbone: about `3.41M`
- lightweight decoder/head: about `0.09M`

This is a much more direct lightweight baseline than only changing the backbone, because the original PVT-v2-B0 ESCNet model has about `21.80M` parameters and most of them are in the decoder/head.

Run:

```bash
cd /root/CV-class
bash run.sh -c configs/pvt_v2_b0_litehead_512_no_ts.yaml
```

## Structure-Preserving ESCNet Slim Update

Added `escnet_slim` for a more method-faithful lightweight variant. Unlike `lite_escnet`, this keeps the original ESCNet decoder/head design:

- AETP edge prediction
- FEM blocks
- MTA blocks
- deformable convolutions
- image patch injection
- edge-guided semantic decoding
- four mask outputs and one edge output

The only architectural reduction is the internal ESCNet width:

```yaml
architecture: escnet_slim
escnet_width: 64
```

The original `escnet` keeps `escnet_width: 128`, so existing configs preserve the original model. The PVT-v2-B0 slim config is `configs/pvt_v2_b0_escnet_slim_512_no_ts.yaml`.

With PVT-v2-B0, `escnet_width: 64` has about `8.34M` parameters:

- backbone: about `3.41M`
- original-method slim decoder/head: about `4.93M`

For comparison, the original-width PVT-v2-B0 ESCNet has about `21.80M` parameters.

This variant is less aggressive than `lite_escnet`, but it is better suited for experiments that need to claim the original ESCNet method is mostly preserved.

Run:

```bash
cd /root/CV-class
bash run.sh -c configs/pvt_v2_b0_escnet_slim_512_no_ts.yaml
```

## Additional Alignment Loss Ideas

The current implementation uses feature MSE plus attention transfer because it is stable, cheap, and works when teacher/student architectures differ. Other useful advanced alignment losses for COD are:

### Relational Knowledge Distillation

Align pairwise pixel or patch relations instead of raw feature values. This can transfer teacher context modeling and object-background separation better than pointwise MSE, but it is more memory intensive.

### Contrastive Feature Distillation

Use foreground/background regions from GT masks to form positive and negative feature pairs. This is well matched to COD because the model must separate camouflaged foreground from highly similar background. It requires careful sampling to avoid noisy small objects.

### Mask-Guided Feature Distillation

Weight feature alignment by the GT mask, edge mask, or teacher confidence map. This focuses KD on object interior and boundary regions, reducing pressure to copy background activations.

### Channel-Wise KL Distillation

Convert each feature map into a channel distribution and minimize KL divergence between teacher and student. This transfers channel importance while being less sensitive to spatial misalignment.

### Multi-Scale Gram Loss

Align feature covariance or Gram matrices at each stage. This can transfer texture/context statistics, but it may be less directly tied to object localization than attention or mask-guided losses.

## Verification

Completed focused checks:

- `py_compile` passed for modified Python files
- `configs/poolformer_s12.yaml` loads with the converted checkpoint
- PoolFormer-S12 pretrained weights strictly match the timm feature model after conversion
- PoolFormer-S12 backbone outputs four feature maps at `[104, 52, 26, 13]` for `416x416` input
- Full ESCNet forward with PoolFormer-S12 returns edge output `(1, 1, 416, 416)`
- Feature KD small forward/backward passed for `pvt_v2_b0 -> pvt_v2_b5`
- PVT-B0 feature adapters receive gradients
