# KD Patch Notes: Minimal Implementation Draft

Date: 2026-06-13

This document describes a patch plan only. Do not edit the active student code directory or `/root/ESCNet` directly. Implement by copying the current light code to an isolated KD code directory.

## Files To Copy

Create isolated implementation area:

```bash
cp -a /root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64 \
  /root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64
```

Copy base config:

```bash
mkdir -p /root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64/configs
cp /root/data-tmp/workspace/02_experiments/configs/light_b2_c64.yaml \
  /root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64/configs/kd_light_b2_c64.yaml
```

Add a teacher config in the KD code copy or proposal config folder:

- `configs/teacher_b5.yaml`
- Same as B5 ESCNet config, but used only to construct teacher architecture.
- `backbone: pvt_v2_b5`
- `lateral_channels: [512, 320, 128, 64]`
- no `inter_channel` needed, or `inter_channel: 128`.
- `bb_pretrained: false` is acceptable because checkpoint is loaded.
- `test_dir` can point to COD10K as a valid placeholder; teacher training does not use it.

## Config Changes

Extend `config.py` `Config` with optional KD fields so existing non-KD configs continue to validate:

```python
kd_enabled: bool = False
kd_mode: str = "none"  # none|online|cache
kd_teacher_config: Optional[str] = None
kd_teacher_ckpt: Optional[str] = None
kd_loss: str = "mse"  # first patch: mse only
kd_weight: float = Field(0.0, ge=0)
kd_temperature: float = Field(1.0, gt=0)
kd_warmup_epochs: int = Field(0, ge=0)
kd_cache_dir: Optional[str] = None
```

Add validation:

```python
if self.kd_enabled:
    if self.kd_mode not in {"online", "cache"}:
        raise ValueError("kd_mode must be online or cache when kd_enabled=true")
    if self.kd_mode == "online" and (not self.kd_teacher_config or not self.kd_teacher_ckpt):
        raise ValueError("online KD requires kd_teacher_config and kd_teacher_ckpt")
    if self.kd_mode == "cache" and not self.kd_cache_dir:
        raise ValueError("cached KD requires kd_cache_dir")
```

## New Helper: `kd.py`

Add `kd.py` in the KD code copy.

Responsibilities:

- Load teacher config from `kd_teacher_config`.
- Build `ESCNet(teacher_config, pretrained=False)`.
- Load `/root/data-tmp/epoch_120.pth`.
- Clean checkpoint prefixes with existing `utils.check_state_dict`.
- Freeze parameters and set eval mode.
- Compute final-mask probability targets under `torch.no_grad()`.
- Compute KD weight warmup.
- Compute MSE KD loss.

Pseudo-code:

```python
import torch
import torch.nn.functional as F

from config import load_config
from models.ESCNet import ESCNet
from utils import check_state_dict


def load_teacher(config, device):
    teacher_config = load_config(config.kd_teacher_config)
    teacher = ESCNet(teacher_config, pretrained=False).to(device)
    state = torch.load(config.kd_teacher_ckpt, map_location=device, weights_only=True)
    teacher.load_state_dict(check_state_dict(state))
    teacher.eval()
    for param in teacher.parameters():
        param.requires_grad_(False)
    return teacher


def kd_scale(config, epoch):
    if not config.kd_enabled or config.kd_weight <= 0:
        return 0.0
    warmup = max(int(config.kd_warmup_epochs), 0)
    if warmup <= 0:
        return float(config.kd_weight)
    return float(config.kd_weight) * min(float(epoch) / float(warmup), 1.0)


def output_kd_loss(student_masks, teacher_masks, target_size):
    student_logit = F.interpolate(
        student_masks[-1], size=target_size, mode="bilinear", align_corners=False
    )
    teacher_prob = F.interpolate(
        teacher_masks[-1].sigmoid(), size=target_size, mode="bilinear", align_corners=False
    )
    return F.mse_loss(student_logit.sigmoid(), teacher_prob)
```

## `train.py` Changes

Import helper:

```python
from kd import kd_scale, load_teacher, output_kd_loss
```

In `Trainer.__init__`, after model/loss setup:

```python
self.teacher = None
if self.config.kd_enabled and self.config.kd_mode == "online":
    self.teacher = load_teacher(self.config, self.device)
    self.log(f"Online KD enabled with teacher {self.config.kd_teacher_ckpt}")
```

In `train_epoch`, after student forward:

```python
loss_kd = torch.zeros((), device=self.device)
if self.teacher is not None:
    with torch.no_grad():
        _, teacher_masks = self.teacher(inputs)
    loss_kd = output_kd_loss(out_pred_masks, teacher_masks, gts.shape[2:])

kd_w = kd_scale(self.config, epoch)
total_loss = loss_structure + loss_dice + kd_w * loss_kd
```

Update rank-0 logging:

```python
f"KD Loss: {loss_kd.item():.3f} | KD Weight: {kd_w:.3f}"
```

Important details:

- Keep teacher outside DDP. Each rank can hold a frozen local teacher.
- Do not include teacher parameters in optimizer.
- Teacher must stay in `eval()` every epoch; call `self.teacher.eval()` after `self.model.train()` if needed.
- Do not wrap teacher in `SyncBatchNorm` or DDP.

## Optional Cached KD Patch

Only implement after online KD smoke is understood.

Required changes:

- Add `tools/cache_teacher_logits.py`.
- Add dataset support to return image paths or stable IDs in train mode.
- Add deterministic mapping from image path to cache file.
- If using train augmentations, apply the same geometric transform to cached teacher maps. Without this, cached KD is not equivalent to online KD.

Minimum cache script shape:

```python
for inputs, _, _, image_paths in train_loader_without_random_aug:
    _, masks = teacher(inputs)
    prob = masks[-1].sigmoid()
    save prob as float16 .pt or uint8 PNG by image stem
```

This route is not recommended for the first full KD run because current random crop/flip/rotate augmentations make alignment easy to get wrong.

## Diff-Level Summary

Expected files changed inside the copied KD code directory:

- `config.py`: add optional KD fields and validation.
- `train.py`: load frozen teacher, compute and log KD loss.
- `kd.py`: new helper module for teacher load and KD loss.
- `configs/kd_light_b2_c64.yaml`: student config with KD enabled and output run name.
- `configs/teacher_b5.yaml`: teacher architecture config.
- optional `tools/smoke_kd_online.py`: fast forward/backward check.

Expected files not changed:

- `/root/ESCNet/**`
- `/root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64/**`
- `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/**`

## Smoke Test Acceptance

The KD code copy is minimally viable when:

- Student forward returns 4 masks and 1 edge output.
- Teacher checkpoint loads with no missing or unexpected keys.
- One batch computes `loss_structure`, `loss_dice`, `loss_kd`, and `total_loss`.
- One optimizer step finishes.
- Peak GPU memory is recorded.
- Output log is written under `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/`.
