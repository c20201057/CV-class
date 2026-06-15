# P1 Task: Visual Comparison Grid

## Agent Role

可视化 agent。

## Goal

生成论文用预测对比图。

## Work Principle

不偷懒，不因为怕风险而保守。不要只挑漂亮样本；必须包含困难样本、失败样本和清晰证据边界，缺失列不能伪装成 final result。

## Inputs

- Images/GT: `/root/data-tmp/COD/Test`
- ESCNet-B5 preds: prefer clean probability eval
  `/root/data-tmp/workspace/02_experiments/runs/baseline_escnet_b5_clean_prob_e120/preds/{DATASET}/epoch_120`
- Historical ESCNet-B5 preds: `/root/ESCNet/preds_epoch120_*` is read-only reference only; do not label it as final clean baseline.
- Light preds:
  `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42_prob_eval_v2/preds/{DATASET}/epoch_120`
- KD preds: add only after final KD probability eval exists.

## Output

- `/root/data-tmp/workspace/02_experiments/figures/visual_grids/*.png`
- `/root/data-tmp/workspace/02_experiments/figures/visual_grids/selected_samples.md`

## Current Tool

- Script: `/root/data-tmp/workspace/02_experiments/scripts/make_visual_grid.py`
- Smoke output: `/root/data-tmp/workspace/04_paper/tables/visual_grid_smoke_camo_b5.png`
- Smoke columns: `Image | GT | ESCNet-B5`

## Acceptance

图列顺序：

`Image | GT | ESCNet-B5 | Light-ESCNet B2-C64 | Light-ESCNet + KD`

至少 6 个样本，包含失败案例。若 clean baseline 或 KD 预测缺失，缺失列必须省略或显式标记为 historical/pending，不能拼接成 final 图。
