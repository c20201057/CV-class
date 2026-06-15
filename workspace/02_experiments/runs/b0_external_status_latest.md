# External B0 Status Latest

- Updated UTC: `2026-06-15T09:33:49Z`
- Status: `not_observed_running`
- Evidence boundary: `external_dirty_tree_observation_only`
- Log: `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/log.txt`
- Result CSV: `/root/data-tmp/results_train/pvt_v2_b0/result.txt`
- Checkpoint dir: `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0`
- Checkpoint status: `present`

## Latest Training

- Latest iter: epoch 10/120, iter 250/252, log time `2026-06-14 13:59:16,338`
- Latest completed epoch: 10/120 with avg loss 3.379
- Latest eval start: epoch 10, log time `2026-06-14 13:59:17,446`, predictions `/root/data-tmp/preds_train/pvt_v2_b0/epoch_10`, status `metrics_appended`

## Intermediate COD10K Results

| epoch | Smeasure | wFmeasure | meanFm | meanEm | MAE |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 0.7692 | 0.6384 | 0.6826 | 0.8664 | 0.0425 |
| 20 | 0.7091 | 0.5296 | 0.5713 | 0.7945 | 0.0629 |
| 30 | 0.7604 | 0.6168 | 0.6559 | 0.8522 | 0.0466 |
| 40 | 0.7791 | 0.6523 | 0.6937 | 0.8688 | 0.0384 |
| 50 | 0.7773 | 0.6493 | 0.6888 | 0.8681 | 0.0392 |
| 60 | 0.7726 | 0.6366 | 0.6730 | 0.8651 | 0.0418 |
| 70 | 0.7858 | 0.6623 | 0.6992 | 0.8771 | 0.0387 |
| 80 | 0.7945 | 0.6744 | 0.7071 | 0.8829 | 0.0370 |
| 90 | 0.7962 | 0.6764 | 0.7087 | 0.8828 | 0.0365 |
| 100 | 0.8014 | 0.6882 | 0.7221 | 0.8899 | 0.0346 |
| 110 | 0.7960 | 0.6799 | 0.7162 | 0.8863 | 0.0356 |
| 120 | 0.8004 | 0.6862 | 0.7203 | 0.8878 | 0.0350 |

## Checkpoints

- `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_100.pth`
- `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_110.pth`
- `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_120.pth`
- `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_60.pth`
- `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_70.pth`
- `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_80.pth`
- `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_90.pth`

## GPU Snapshot

- `0, 9897, 16384, 37`
- `1, 10041, 16384, 28`
- `2, 9921, 16384, 27`
- `3, 9895, 16384, 34`

## Process Snapshot

- none

## Acceptance Boundary

- Do not use this branch as a final main-table result while it is launched from dirty `/root/ESCNet`.
- Require a checkpoint, code/config snapshot under `/root/data-tmp/workspace`, and CAMO/COD10K/NC4K probability evaluation before any paper-facing result use.
- Current COD10K-only intermediate rows are observation evidence only.
