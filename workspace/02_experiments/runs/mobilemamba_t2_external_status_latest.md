# External MobileMamba-T2 Status Latest

- Updated UTC: `2026-06-15T09:43:18Z`
- Status: `not_observed_running`
- Evidence boundary: `external_dirty_tree_observation_only`
- Process pattern: `mobilemamba_t2`
- Log: `/root/data-tmp/ESCNet/checkpoints/mobilemamba_t2/log.txt`
- Result CSV: `/root/data-tmp/results_train/mobilemamba_t2/result.txt`
- Checkpoint dir: `/root/data-tmp/ESCNet/checkpoints/mobilemamba_t2`
- Checkpoint status: `absent`

## Latest Training

- Latest iter: epoch 59/120, iter 200/252, log time `2026-06-14 13:15:35,193`
- Latest completed epoch: 58/120 with avg loss 2.342
- Latest eval start: epoch 50, log time `2026-06-14 12:18:36,313`, predictions `/root/data-tmp/preds_train/mobilemamba_t2/epoch_50`, status `metrics_appended`

## Intermediate COD10K Results

| epoch | Smeasure | wFmeasure | meanFm | meanEm | MAE |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 0.7190 | 0.5578 | 0.6139 | 0.8103 | 0.0497 |
| 20 | 0.7376 | 0.5861 | 0.6370 | 0.8400 | 0.0487 |
| 30 | 0.7347 | 0.5781 | 0.6281 | 0.8285 | 0.0520 |
| 40 | 0.7462 | 0.5980 | 0.6446 | 0.8453 | 0.0472 |
| 50 | 0.7487 | 0.6019 | 0.6482 | 0.8477 | 0.0465 |

Best observed row by S-measure:
`epoch 50: S=0.7487, wF=0.6019, meanF=0.6482, meanE=0.8477, MAE=0.0465`

## Checkpoints

- none

## GPU Snapshot

- `0, 9897, 16384, 30`
- `1, 10041, 16384, 25`
- `2, 9921, 16384, 30`
- `3, 9895, 16384, 28`

## Process Snapshot

- none

## Acceptance Boundary

- Do not use this branch as a final main-table result while it is launched from dirty `/root/ESCNet`.
- Require an isolated workspace snapshot, checkpoint load/profile, CAMO/COD10K/NC4K probability eval, and run integrity before paper-facing use.
- Until then, treat it only as route-search evidence for whether a state-space/mobile backbone is promising.
