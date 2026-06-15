# External PVTv2-B0 Online KD Observation

更新时间：2026-06-13T22:23:06Z / 2026-06-14 06:23:06 CST

This file tracks the external high-risk B0 branch that is running from the dirty
`/root/ESCNet` working tree. It is not a validated paper result.

## Current Process

- Command observed: `bash run.sh -c configs/pvt_v2_b0.yaml`
- Torchrun: `torchrun --nproc_per_node=4 --master_port=29501 train.py --config configs/pvt_v2_b0.yaml`
- Output log: `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/log.txt`
- Checkpoint directory: `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0`
- Current status: running on four GPUs. Epoch 110 COD10K intermediate
  evaluation has completed. It regressed relative to epoch 100, which remains
  the best B0 row on S, weighted F, mean F, mean E and MAE, and both rows are
  far below accepted Light-B2-C64 COD10K evidence. Live training progress is
  authoritative in `b0_external_status_latest.md`.

## Intermediate Evidence

COD10K intermediate evaluations:

```text
epoch,Smeasure,wFmeasure,meanFm,meanEm,MAE
10,0.7692,0.6384,0.6826,0.8664,0.0425
20,0.7091,0.5296,0.5713,0.7945,0.0629
30,0.7604,0.6168,0.6559,0.8522,0.0466
40,0.7791,0.6523,0.6937,0.8688,0.0384
50,0.7773,0.6493,0.6888,0.8681,0.0392
60,0.7726,0.6366,0.6730,0.8651,0.0418
70,0.7858,0.6623,0.6992,0.8771,0.0387
80,0.7945,0.6744,0.7071,0.8829,0.0370
90,0.7962,0.6764,0.7087,0.8828,0.0365
100,0.8014,0.6882,0.7221,0.8899,0.0346
110,0.7960,0.6799,0.7162,0.8863,0.0356
120,0.8004,0.6862,0.7203,0.8878,0.0350
```

Epoch 120 is the latest completed B0 intermediate row. Epoch 100 remains the
best completed B0 row so far on S-measure, weighted F-measure, mean F-measure,
mean E-measure and MAE. These rows are still COD10K-only and dirty-tree
evidence, and remain observation only.

At `2026-06-13T18:59Z`, epoch 50 had been appended to
`/root/data-tmp/results_train/pvt_v2_b0/result.txt`. It was slightly worse than
epoch 40 on S-measure, weighted F-measure and MAE at that time.

At `2026-06-13T19:31Z`, epoch 60 had been appended to the same result file. It
is weaker than epoch 40 and epoch 50 on S-measure, weighted F-measure,
mean F-measure and MAE, reinforcing that B0 is an observation branch rather
than a replacement for Light-B2-C64.

At `2026-06-13T19:57Z`, epoch 70 produced raw checkpoint
`/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_70.pth` and began COD10K
evaluation. At `2026-06-13T20:05Z`, the epoch 70 row was appended with
S=.7858, wF=.6623, meanF=.6992, meanE=.8771 and MAE=.0387. This does not change the evidence level: the branch is still
dirty-tree, COD10K-only observation until load/profile and CAMO/COD10K/NC4K
probability evaluation pass in an isolated workspace run.

At `2026-06-13T20:29Z`, epoch 80 produced raw checkpoint
`/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_80.pth` and began COD10K
evaluation. At `2026-06-13T20:38Z`, the epoch80 row was appended with
S=.7945, wF=.6744, meanF=.7071, meanE=.8829 and MAE=.0370. This is the
best B0 observation row so far, but it remains below accepted Light-B2-C64
COD10K evidence and does not pass Gate 4.

At `2026-06-13T21:03Z`, epoch 90 produced raw checkpoint
`/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_90.pth` and began COD10K
evaluation. At `2026-06-13T21:11Z`, the epoch90 row was appended with
S=.7962, wF=.6764, meanF=.7087, meanE=.8828 and MAE=.0365. This is the best
B0 observation row so far, but it remains below accepted Light-B2-C64 COD10K
evidence and does not pass Gate 4.

At `2026-06-13T21:36Z`, epoch 100 produced raw checkpoint
`/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_100.pth` and began COD10K
evaluation. At `2026-06-13T21:48Z`, the epoch100 row was appended with
S=.8014, wF=.6882, meanF=.7221, meanE=.8899 and MAE=.0346. This is the best
B0 observation row so far, but it remains below accepted Light-B2-C64 COD10K
evidence and does not pass Gate 4.

At `2026-06-13T22:10Z`, epoch 110 produced raw checkpoint
`/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_110.pth` and began COD10K
evaluation. At `2026-06-13T22:19Z`, the epoch110 row was appended with
S=.7960, wF=.6799, meanF=.7162, meanE=.8863 and MAE=.0356. This row regressed
relative to epoch100 and remains below accepted Light-B2-C64 COD10K evidence.

At `2026-06-13T22:43Z`, epoch 120 completed training with avg loss 2.259 and
saved raw checkpoint `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_120.pth`.
The epoch120 COD10K eval started at `2026-06-13T22:43:59Z` and produced
`/root/data-tmp/preds_train/pvt_v2_b0/epoch_120`. At `2026-06-13T22:53Z`, the
epoch120 row was appended with S=.8004, wF=.6862, meanF=.7203, meanE=.8878 and
MAE=.0350. This is the latest completed metrics row; epoch100 remains the best
observed metrics row.

Evidence paths:

- Metrics: `/root/data-tmp/results_train/pvt_v2_b0/result.txt`
- Latest status report: `/root/data-tmp/workspace/02_experiments/runs/b0_external_status_latest.md`
- Engineering trend note: `/root/data-tmp/workspace/04_paper/drafts/b0_cod10k_trend_note.md`
- Engineering trend figure: `/root/data-tmp/workspace/04_paper/figures/b0_cod10k_intermediate_trend.png`
- Predictions: `/root/data-tmp/preds_train/pvt_v2_b0/epoch_10`,
  `/root/data-tmp/preds_train/pvt_v2_b0/epoch_20`
- Predictions: `/root/data-tmp/preds_train/pvt_v2_b0/epoch_30`,
  `/root/data-tmp/preds_train/pvt_v2_b0/epoch_40`
- Predictions: `/root/data-tmp/preds_train/pvt_v2_b0/epoch_50`
- Predictions: `/root/data-tmp/preds_train/pvt_v2_b0/epoch_60`
- Predictions: `/root/data-tmp/preds_train/pvt_v2_b0/epoch_70`
- Raw checkpoint: `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_60.pth`
- Raw checkpoint: `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_70.pth`
- Raw checkpoint: `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_80.pth`
- Raw checkpoint: `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_90.pth`
- Raw checkpoint: `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_100.pth`
- Raw checkpoint: `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_110.pth`
- Raw checkpoint: `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_120.pth`
- Epoch 80 predictions: `/root/data-tmp/preds_train/pvt_v2_b0/epoch_80`
- Epoch 90 predictions: `/root/data-tmp/preds_train/pvt_v2_b0/epoch_90`
- Epoch 100 predictions: `/root/data-tmp/preds_train/pvt_v2_b0/epoch_100`
- Epoch 110 predictions: `/root/data-tmp/preds_train/pvt_v2_b0/epoch_110`
- Epoch 120 predictions: `/root/data-tmp/preds_train/pvt_v2_b0/epoch_120`
- Live training state: see `b0_external_status_latest.md`
- Prediction count: 2026 for each observed COD10K intermediate eval
- COD10K GT count: 2026
- Epoch 40 eval status: metrics appended to
  `/root/data-tmp/results_train/pvt_v2_b0/result.txt`
- Epoch 50 eval status: metrics appended to
  `/root/data-tmp/results_train/pvt_v2_b0/result.txt`
- Epoch 60 eval status: metrics appended to
  `/root/data-tmp/results_train/pvt_v2_b0/result.txt`
- Epoch 70 eval status: metrics appended to
  `/root/data-tmp/results_train/pvt_v2_b0/result.txt`
- Epoch 80 eval status: metrics appended to
  `/root/data-tmp/results_train/pvt_v2_b0/result.txt`
- Epoch 90 eval status: metrics appended to
  `/root/data-tmp/results_train/pvt_v2_b0/result.txt`
- Epoch 100 eval status: metrics appended to
  `/root/data-tmp/results_train/pvt_v2_b0/result.txt`
- Epoch 110 eval status: metrics appended to
  `/root/data-tmp/results_train/pvt_v2_b0/result.txt`
- Latest dirty-tree observation snapshot:
  `/root/data-tmp/workspace/02_experiments/code/external_b0_dirty_snapshot_20260613T200614Z_epoch70_metrics_observation`

## Acceptance Boundary

This branch cannot enter the paper main table yet because:

- The raw B0 checkpoints have not been load/profile/eval verified.
- Only COD10K intermediate eval exists; CAMO and NC4K are missing.
- The run is launched from dirty `/root/ESCNet`, not from a clean archived
  experiment code directory.
- It is an external high-risk branch and does not replace the accepted
  Light-B2-C64 no-KD main result.

Before any paper-facing use, the next required steps are:

1. Verify checkpoint load and model profile.
2. Run CAMO/COD10K/NC4K probability evaluation under an isolated run directory.
3. Run `check_run_integrity.py`.
4. Treat it as an ablation or appendix branch unless all evidence passes.
