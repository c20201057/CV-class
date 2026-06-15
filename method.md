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
```

The defaults preserve the previous full-resume behavior. For finetuning, a config can now load model weights while resetting optimizer, scheduler, AMP scaler, and epoch counter.

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
