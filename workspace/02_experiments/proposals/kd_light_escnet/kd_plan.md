# KD Plan: Light-ESCNet B2-C64

Date: 2026-06-13

## Scope

This is a proposal-only plan. Do not modify or stop:

- `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42`
- `/root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64`
- `/root/ESCNet`

All KD implementation should be isolated in a new copied code directory, for example:

- Code copy: `/root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64`
- Run output: `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42`

## Fixed Teacher And Student

Teacher:

- Architecture: ESCNet-B5, original ESCNet decoder width 128.
- Checkpoint: `/root/data-tmp/epoch_120.pth`.
- Reason: route decision identifies this checkpoint as the historical strong baseline/teacher that matches the 2026-06-11 predictions and reproduces CAMO probability metrics closely.

Student:

- Architecture: Light-ESCNet B2-C64.
- Backbone: `pvt_v2_b2`.
- Decoder/channel width: `inter_channel: 64`.
- Existing base config: `/root/data-tmp/workspace/02_experiments/configs/light_b2_c64.yaml`.
- Current structural profile evidence: 29.81M params, 36.39 GMACs, 113.74 MB model size, 38.73 ms latency, 25.82 FPS, 237.44 MB peak memory at 416 input on V100.

## Current Training Interface

The student training loop in `train.py` uses:

- `out_edge, out_pred_masks = model(inputs)`
- edge loss: `EdgeDiceLoss(out_edge, edges)`
- mask loss: weighted `StructureLoss` over the four decoder outputs, resized to GT size.

The final mask output is `out_pred_masks[-1]`, whose sigmoid probability is the natural KD target.

## Candidate A: Online Teacher KD

Online KD runs the frozen B5 teacher in the same training step as the B2-C64 student.

Recommended loss:

```python
with torch.no_grad():
    _, teacher_masks = teacher(inputs)
    teacher_prob = teacher_masks[-1].sigmoid()

student_logit = interpolate(out_pred_masks[-1], size=gts.shape[2:])
teacher_prob = interpolate(teacher_prob, size=gts.shape[2:])

loss_kd_mse = mse_loss(student_logit.sigmoid(), teacher_prob)
loss_kd_kl = kl_div(
    logsigmoid(student_logit / T),
    teacher_prob,  # better implemented as binary KL/BCE-style distillation
)
total_loss = loss_structure + loss_dice + kd_weight * loss_kd
```

Use output-level KD first:

- Primary: probability MSE on `out_pred_masks[-1].sigmoid()`.
- Optional if stable: BCE/KL-style soft target loss with temperature `T=2`.
- Initial weights: `kd_weight=0.5`, `kd_loss=mse`, `kd_warmup_epochs=5`.

Pros:

- Simplest data correctness story: teacher sees exactly the same augmented image tensor as the student.
- No cache invalidation, path matching, image transform, or train augmentation mismatch.
- Easy smoke test: one forward pass through teacher and student proves the loss path.

Cons:

- More GPU memory and time per iteration.
- Teacher B5 forward roughly adds the teacher inference footprint. Prior profile shows B5 C128 peak memory around 829.77 MB for batch 1 inference and 129.02 GMACs; training batch 4 with both models will be materially heavier than current student-only training.
- With DDP, every rank will hold one frozen teacher unless explicitly optimized.

Expected cost:

- Memory: likely fits V100 16 GB at batch size 4 because gradients are only stored for the student and teacher uses `no_grad`, but actual peak must be checked. If OOM, drop batch size to 2 or run single-GPU smoke before DDP.
- Time: expect roughly 1.5x to 2.2x student-only wall time per epoch. The teacher forward dominates additional compute, but no teacher backward is needed.

## Candidate B: Cached Teacher Logits

Cached KD precomputes teacher outputs and loads them during student training.

Cache target:

- Prefer full-resolution or 416-resolution teacher probability maps from `teacher_masks[-1].sigmoid()`.
- Store per training sample under a deterministic key derived from the original image path.
- Use `float16` `.pt` tensors or 8-bit PNG probabilities. `.pt` is cleaner for training, PNG is easier to inspect and reuses existing probability-map conventions.

Pros:

- Student training speed and memory are close to non-KD training.
- Avoids loading B5 teacher during every step.
- Cache can be inspected and reused.

Cons:

- Current train augmentations include flip, rotate, pepper, crop. If the cache is generated before augmentation, cached masks no longer match augmented student inputs.
- Correct cached KD requires either disabling geometric augmentations for KD, applying identical transforms to cached teacher maps, or caching after augmentation with a deterministic augmentation pipeline.
- More engineering surface: dataset must return stable sample IDs and KD tensors; cache integrity must be checked.

Expected cost:

- One teacher pass over the training set before training. This is cheaper than doing teacher forward for 120 epochs.
- Storage depends on format. For 416x416 maps, 8-bit PNG is small; float16 `.pt` is about 0.33 MB per sample before filesystem overhead.
- Training memory close to current B2-C64, plus one soft target tensor per batch.

## Recommendation

Prioritize online teacher KD for the first full KD run.

Reason:

1. It is the least ambiguous KD signal because teacher predictions are computed on the same augmented input tensor as the student.
2. It minimizes changes to data loading and avoids silent image-to-cache mismatches.
3. The project currently needs a trustworthy KD result more than the fastest possible KD pipeline.
4. V100 16 GB should be enough for a frozen no-grad B5 teacher plus B2-C64 student at batch size 4, but the smoke command must verify this before full training.

Use cached teacher logits as the second route if online KD is too slow or OOM after batch-size tuning. Cached KD should only be used for the main table after the transform alignment is explicitly verified.

## Minimal KD Run Settings

Initial config additions:

```yaml
kd_enabled: true
kd_mode: online
kd_teacher_config: /root/data-tmp/workspace/02_experiments/proposals/kd_light_escnet/configs/teacher_b5.yaml
kd_teacher_ckpt: /root/data-tmp/epoch_120.pth
kd_loss: mse
kd_weight: 0.5
kd_temperature: 2.0
kd_warmup_epochs: 5
save_model_dir: /root/data-tmp/workspace/02_experiments/runs
name: kd_light_b2_c64_e120_s42
```

Loss schedule:

- Epochs 1-5: linearly increase KD weight from 0 to 0.5.
- Epochs 6-120: keep KD weight at 0.5.
- Keep original structure and edge losses unchanged.

## Risks And Controls

Risk: Online KD OOM.

- Control: smoke with batch size 1 and 4; if batch 4 fails, use batch size 2 and record the change.

Risk: KD over-smooths boundaries.

- Control: keep the edge Dice branch unchanged; log structure, edge, KD, and total losses separately; compare CAMO/COD10K/NC4K probability metrics.

Risk: Teacher checkpoint/config mismatch.

- Control: teacher config must be B5 C128 with `pvt_v2_b5` weights path and `pretrained=False` when loading checkpoint. Load `/root/data-tmp/epoch_120.pth` with the same `check_state_dict` cleanup used by existing inference code.

Risk: Existing `autocast(dtype=torch.float32)` does not provide real AMP savings.

- Control: do not change precision in the first KD patch. If OOM occurs, make AMP dtype a separate controlled patch.

Risk: Evaluation uses thresholded predictions.

- Control: use `/root/data-tmp/workspace/02_experiments/scripts/infer_prob.py` for final probability maps, then `eval.py` and `collect_metrics.py`.

## Evidence To Save

For acceptance, save under `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/`:

- copied KD config(s)
- `log.txt`
- smoke output/log
- checkpoints
- probability predictions for CAMO/COD10K/NC4K
- `eval/<dataset>/result.txt`
- collected metrics markdown/CSV rows
- optional profile JSON for the trained KD checkpoint
