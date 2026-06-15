# B0 Intermediate Trend Note

更新时间：2026-06-13T22:23:06Z / 2026-06-14 06:23:06 CST

This note summarizes the external PVTv2-B0 online KD branch currently running
from the dirty `/root/ESCNet` working tree. It is not a paper result.

## Evidence

Source files:

- Log: `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/log.txt`
- Metrics: `/root/data-tmp/results_train/pvt_v2_b0/result.txt`
- Live latest status:
  `/root/data-tmp/workspace/02_experiments/runs/b0_external_status_latest.md`
- Observation record:
  `/root/data-tmp/workspace/02_experiments/runs/b0_external_observation.md`

Observed COD10K intermediate evaluations:

| Epoch | S | wF | meanF | meanE | MAE |
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

## Route Judgment

- Epoch 20 degraded sharply relative to epoch 10.
- Epoch 30 recovered most of the epoch 20 drop, but still trails epoch 10 on
  S-measure, weighted F-measure, mean F-measure, mean E-measure and MAE.
- Epoch 40 improved over epoch 10 and reduced MAE to 0.0384.
- Epoch 50 has been appended and is slightly worse than epoch 40 on S-measure,
  weighted F-measure, mean F-measure, mean E-measure and MAE.
- Epoch 60 has also been appended and weakens further relative to epoch 40/50
  on S-measure, weighted F-measure, mean F-measure and MAE.
- Epoch 70 has been appended and improved over epoch 60 on S-measure,
  weighted F-measure, mean F-measure and mean E-measure, while MAE remains
  slightly worse than epoch 40.
- Epoch 80 has been appended and improved over epoch 70 on S-measure,
  weighted F-measure, mean F-measure, mean E-measure and MAE:
  `80,0.7945,0.6744,0.7071,0.8829,0.0370`.
- Epoch 90 has been appended and improved over epoch 80 on S-measure,
  weighted F-measure, mean F-measure and MAE:
  `90,0.7962,0.6764,0.7087,0.8828,0.0365`.
- Epoch 100 has been appended and is now the strongest completed B0 row on
  S-measure, weighted F-measure, mean F-measure, mean E-measure and MAE:
  `100,0.8014,0.6882,0.7221,0.8899,0.0346`.
- Epoch 110 was appended after epoch 100:
  `110,0.7960,0.6799,0.7162,0.8863,0.0356`.
- The epoch 110 row regressed relative to epoch 100 and remains much weaker
  than accepted Light-B2-C64 COD10K evidence.
- Epoch 120 has been appended as the latest completed B0 row:
  `120,0.8004,0.6862,0.7203,0.8878,0.0350`.
- The epoch 120 row partially recovers from epoch 110 but remains much weaker
  than accepted Light-B2-C64 COD10K evidence.
- The epoch 100 COD10K row is still much weaker than accepted Light-B2-C64
  COD10K evidence (Light S=.866, wF=.782, meanF=.808, meanE=.928, MAE=.024).
- Raw checkpoint `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_60.pth`
  has appeared, along with epoch60 COD10K predictions and metrics.
- Raw checkpoint `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_70.pth`
  has also appeared, and epoch70 COD10K metrics have been appended to the
  intermediate result table.
- Raw checkpoint `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_80.pth`
  has appeared, and epoch80 COD10K metrics have been appended to the
  intermediate result table.
- Raw checkpoint `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_90.pth`
  has appeared, and epoch90 COD10K metrics have been appended to the
  intermediate result table.
- Raw checkpoint `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_100.pth`
  has appeared, and epoch100 COD10K metrics have been appended to the
  intermediate result table.
- Raw checkpoint `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_110.pth`
  has appeared, and epoch110 COD10K metrics have been appended to the
  intermediate result table.
- Raw checkpoint `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0/epoch_120.pth`
  has appeared, and epoch120 COD10K metrics have been appended to the
  intermediate result table.
- The online KD training process has finished; the external `run.sh` may still
  have a follow-up `test.py` process. Use
  `/root/data-tmp/workspace/02_experiments/runs/b0_external_status_latest.md`
  for minute-level latest progress.
- The branch is launched from dirty `/root/ESCNet`, so even a later checkpoint
  must be accompanied by a code/config snapshot before it can be evaluated as
  an appendix or failure-analysis branch.

## Paper Boundary

Do not use this branch in the main accuracy table, abstract, average deltas or
conclusion. It can only support an engineering observation such as:

> The external PVTv2-B0 online KD branch recovered on COD10K by epoch 40,
> weakened at epoch 50 and epoch 60, improved again through epoch 100, then
> regressed at epoch 110. The latest completed epoch 120 row partially
> recovered, but the branch still lacks validated load/profile and three-dataset
> evidence during the main experiment window.

This sentence should only be used if the branch still lacks validated
checkpoint loading and three-dataset probability evaluation at submission time.
