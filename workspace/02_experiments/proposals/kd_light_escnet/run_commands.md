# KD Run Commands

Date: 2026-06-13

All commands below write outputs to:

`/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/`

Do not use or modify:

- `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42`
- `/root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64`
- `/root/ESCNet`

These commands assume the minimal KD patch has been implemented in:

`/root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64`

## Environment Variables

```bash
export KD_CODE=/root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64
export KD_RUN=/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42
export KD_CONFIG=$KD_CODE/configs/kd_light_b2_c64.yaml
export TEACHER_CKPT=/root/data-tmp/epoch_120.pth
mkdir -p "$KD_RUN"/{smoke,eval,preds,logs,profiles}
```

## Smoke

Forward-only student smoke:

```bash
cd "$KD_CODE"
python tools/smoke_light_b2_c64.py \
  --config "$KD_CONFIG" \
  --batch-size 1 \
  --device cuda:0 \
  2>&1 | tee "$KD_RUN/smoke/student_forward_b1.log"
```

Online KD one-batch smoke after adding `tools/smoke_kd_online.py`:

```bash
cd "$KD_CODE"
python tools/smoke_kd_online.py \
  --config "$KD_CONFIG" \
  --device cuda:0 \
  --batch-size 1 \
  --max-batches 1 \
  2>&1 | tee "$KD_RUN/smoke/kd_online_b1.log"
```

Batch-size 4 smoke before full training:

```bash
cd "$KD_CODE"
python tools/smoke_kd_online.py \
  --config "$KD_CONFIG" \
  --device cuda:0 \
  --batch-size 4 \
  --max-batches 1 \
  2>&1 | tee "$KD_RUN/smoke/kd_online_b4.log"
```

If batch 4 OOMs, set `batch_size: 2` in the copied KD config and rerun smoke. Record the config change in `$KD_RUN/logs/config_change_batch_size.txt`.

## Full Train

Single-GPU conservative run:

```bash
cd "$KD_CODE"
CUDA_VISIBLE_DEVICES=0 python train.py \
  --config "$KD_CONFIG" \
  2>&1 | tee "$KD_RUN/logs/train_single_gpu.log"
```

Multi-GPU DDP run, only if KD config has `multi_GPU: true` and matching `device_ids`:

```bash
cd "$KD_CODE"
torchrun --standalone --nproc_per_node=4 train.py \
  --config "$KD_CONFIG" \
  2>&1 | tee "$KD_RUN/logs/train_ddp_4gpu.log"
```

Expected checkpoint pattern:

```text
/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/epoch_*.pth
```

Use the final saved checkpoint for evaluation, for example:

```bash
export KD_CKPT=$KD_RUN/epoch_120.pth
```

If `save_last` and `save_step` do not produce `epoch_120.pth`, use the highest epoch checkpoint and record the exact path.

## Eval

Use probability-map inference, not thresholded `test.py`, for final metrics.

Create dataset-specific eval configs in the KD code copy before running, or copy and edit the YAML files so that only `test_dir` changes:

- COD10K: `/root/data-tmp/COD/Test/COD10K`
- CAMO: `/root/data-tmp/COD/Test/CAMO`
- NC4K: `/root/data-tmp/COD/Test/NC4K`

COD10K probability inference:

```bash
python /root/data-tmp/workspace/02_experiments/scripts/infer_prob.py \
  --repo "$KD_CODE" \
  --config "$KD_CODE/configs/kd_light_b2_c64_cod10k.yaml" \
  --ckpt "$KD_CKPT" \
  --pred_root "$KD_RUN/preds/COD10K" \
  --method kd_light_b2_c64_e120_s42 \
  --device cuda:0 \
  --batch_size_valid 8 \
  2>&1 | tee "$KD_RUN/logs/infer_cod10k.log"
```

CAMO probability inference:

```bash
python /root/data-tmp/workspace/02_experiments/scripts/infer_prob.py \
  --repo "$KD_CODE" \
  --config "$KD_CODE/configs/kd_light_b2_c64_camo.yaml" \
  --ckpt "$KD_CKPT" \
  --pred_root "$KD_RUN/preds/CAMO" \
  --method kd_light_b2_c64_e120_s42 \
  --device cuda:0 \
  --batch_size_valid 8 \
  2>&1 | tee "$KD_RUN/logs/infer_camo.log"
```

NC4K probability inference:

```bash
python /root/data-tmp/workspace/02_experiments/scripts/infer_prob.py \
  --repo "$KD_CODE" \
  --config "$KD_CODE/configs/kd_light_b2_c64_nc4k.yaml" \
  --ckpt "$KD_CKPT" \
  --pred_root "$KD_RUN/preds/NC4K" \
  --method kd_light_b2_c64_e120_s42 \
  --device cuda:0 \
  --batch_size_valid 8 \
  2>&1 | tee "$KD_RUN/logs/infer_nc4k.log"
```

Evaluate each dataset:

```bash
cd "$KD_CODE"
python eval.py \
  --config "$KD_CODE/configs/kd_light_b2_c64_cod10k.yaml" \
  --pred_root "$KD_RUN/preds/COD10K" \
  --save_dir "$KD_RUN/eval/COD10K" \
  --model_lst kd_light_b2_c64_e120_s42 \
  --n_threads 4 \
  2>&1 | tee "$KD_RUN/logs/eval_cod10k.log"
```

```bash
cd "$KD_CODE"
python eval.py \
  --config "$KD_CODE/configs/kd_light_b2_c64_camo.yaml" \
  --pred_root "$KD_RUN/preds/CAMO" \
  --save_dir "$KD_RUN/eval/CAMO" \
  --model_lst kd_light_b2_c64_e120_s42 \
  --n_threads 4 \
  2>&1 | tee "$KD_RUN/logs/eval_camo.log"
```

```bash
cd "$KD_CODE"
python eval.py \
  --config "$KD_CODE/configs/kd_light_b2_c64_nc4k.yaml" \
  --pred_root "$KD_RUN/preds/NC4K" \
  --save_dir "$KD_RUN/eval/NC4K" \
  --model_lst kd_light_b2_c64_e120_s42 \
  --n_threads 4 \
  2>&1 | tee "$KD_RUN/logs/eval_nc4k.log"
```

Collect metrics:

```bash
python /root/data-tmp/workspace/02_experiments/scripts/collect_metrics.py \
  --exp_id kd_light_b2_c64_e120_s42 \
  --result_root "$KD_RUN/eval" \
  --datasets CAMO,COD10K,NC4K \
  --out_csv /root/data-tmp/workspace/02_experiments/tables/metrics_all.csv \
  --out_md "$KD_RUN/eval/metrics.md" \
  2>&1 | tee "$KD_RUN/logs/collect_metrics.log"
```

Optional profile after training:

```bash
python /root/data-tmp/workspace/02_experiments/scripts/profile_model.py \
  --repo "$KD_CODE" \
  --config "$KD_CONFIG" \
  --ckpt "$KD_CKPT" \
  --out "$KD_RUN/profiles/profile_epoch120.json" \
  --device cuda:0 \
  --warmup 20 \
  --repeat 50 \
  --exp-id kd_light_b2_c64_e120_s42 \
  2>&1 | tee "$KD_RUN/logs/profile_epoch120.log"
```
