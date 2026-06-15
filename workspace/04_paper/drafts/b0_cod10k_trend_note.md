# B0 COD10K Trend Note

This note summarizes the external dirty-tree PVTv2-B0 online KD branch.
It is observation evidence only and must not enter the main table, abstract or conclusion.

- Source CSV: `/root/data-tmp/results_train/pvt_v2_b0/result.txt`
- Figure: `/root/data-tmp/workspace/04_paper/figures/b0_cod10k_intermediate_trend.png`
- Latest completed row: epoch 120, S=0.8004, wF=0.6862, meanF=0.7203, meanE=0.8878, MAE=0.0350
- Best B0 S row: epoch 100, S=0.8014
- Best B0 MAE row: epoch 100, MAE=0.0346
- Accepted Light-B2-C64 COD10K reference: S=.866, wF=.782, meanF=.808, meanE=.928, MAE=.024

## Rows

| epoch | S | wF | meanF | meanE | MAE |
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

## Boundary

- Dirty `/root/ESCNet` branch.
- COD10K-only intermediate evaluation.
- No accepted checkpoint load/profile or CAMO/COD10K/NC4K probability evaluation.
- Use only as engineering risk evidence or appendix material after Gate 4A.
