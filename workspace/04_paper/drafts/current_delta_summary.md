# Current Delta Summary

This file is generated from `metrics_all.csv` and `profiles.csv`.
It is safe to cite only within the evidence boundaries shown below.

## Evidence Status

- Historical ESCNet-B5 status: `historical_reference_not_clean_prob_final`.
- Clean ESCNet-B5 status: `clean_prob_re_eval_complete`.
- Light B2-C64 status: `final_main_light`.
- KD B2-C64 status: `final_main_kd`.
- Active reference for delta tables: `baseline_escnet_b5_clean_prob_e120` (clean ESCNet-B5 probability baseline).
- Current Light-vs-ESCNet deltas are clean same-protocol deltas.

## Light B2-C64 vs Active ESCNet Reference

| Dataset | Ref S | Light S | Delta S | Ref wF | Light wF | Delta wF | Ref MAE | Light MAE | Delta MAE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| CAMO | 0.881 | 0.862 | -0.019 | 0.842 | 0.818 | -0.024 | 0.043 | 0.051 | +0.008 |
| COD10K | 0.877 | 0.866 | -0.011 | 0.802 | 0.782 | -0.020 | 0.021 | 0.024 | +0.003 |
| NC4K | 0.897 | 0.886 | -0.011 | 0.857 | 0.840 | -0.017 | 0.029 | 0.033 | +0.004 |

### Three-Dataset Mean Deltas

| Metric | Reference Mean | Light Mean | Delta Light-Reference |
| --- | ---: | ---: | ---: |
| Smeasure | 0.885 | 0.871 | -0.014 |
| wFmeasure | 0.834 | 0.813 | -0.020 |
| meanFm | 0.855 | 0.838 | -0.018 |
| meanEm | 0.938 | 0.926 | -0.011 |
| MAE | 0.031 | 0.036 | +0.005 |

## Structural Reductions

| Quantity | Reference | Light | Reduction |
| --- | ---: | ---: | ---: |
| Params | 99.90M | 29.81M | 70.16% |
| GMACs | 129.02 | 36.39 | 71.79% |
| Model size MB | 381.17 | 113.74 | 70.16% |
| Peak memory MB | 829.77 | 237.44 | 71.38% |

## Gate Status

| Gate | Status | Paper Action |
| --- | --- | --- |
| Gate 1 clean baseline | pass | Promote ESCNet-B5 to clean probability baseline. |
| Gate 2 KD | pass | Add KD result and rewrite KD claims according to measured deltas. |
| Gate 3 speed | pass | Latency/FPS can be reported if same-command idle profiles agree. |

## KD B2-C64 vs Light B2-C64 no-KD

| Dataset | Ref S | Light S | Delta S | Ref wF | Light wF | Delta wF | Ref MAE | Light MAE | Delta MAE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| CAMO | 0.862 | 0.863 | +0.001 | 0.818 | 0.818 | +0.000 | 0.051 | 0.050 | -0.001 |
| COD10K | 0.866 | 0.864 | -0.002 | 0.782 | 0.782 | +0.000 | 0.024 | 0.024 | +0.000 |
| NC4K | 0.886 | 0.885 | -0.001 | 0.840 | 0.838 | -0.002 | 0.033 | 0.033 | +0.000 |

### Three-Dataset Mean Deltas

| Metric | Reference Mean | Light Mean | Delta Light-Reference |
| --- | ---: | ---: | ---: |
| Smeasure | 0.871 | 0.871 | -0.001 |
| wFmeasure | 0.813 | 0.813 | -0.001 |
| meanFm | 0.838 | 0.838 | +0.000 |
| meanEm | 0.926 | 0.927 | +0.001 |
| MAE | 0.036 | 0.036 | -0.000 |

## KD B2-C64 vs clean ESCNet-B5 probability baseline

| Dataset | Ref S | Light S | Delta S | Ref wF | Light wF | Delta wF | Ref MAE | Light MAE | Delta MAE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| CAMO | 0.881 | 0.863 | -0.018 | 0.842 | 0.818 | -0.024 | 0.043 | 0.050 | +0.007 |
| COD10K | 0.877 | 0.864 | -0.013 | 0.802 | 0.782 | -0.020 | 0.021 | 0.024 | +0.003 |
| NC4K | 0.897 | 0.885 | -0.012 | 0.857 | 0.838 | -0.019 | 0.029 | 0.033 | +0.004 |

### Three-Dataset Mean Deltas

| Metric | Reference Mean | Light Mean | Delta Light-Reference |
| --- | ---: | ---: | ---: |
| Smeasure | 0.885 | 0.871 | -0.014 |
| wFmeasure | 0.834 | 0.813 | -0.021 |
| meanFm | 0.855 | 0.838 | -0.018 |
| meanEm | 0.938 | 0.927 | -0.011 |
| MAE | 0.031 | 0.036 | +0.005 |
