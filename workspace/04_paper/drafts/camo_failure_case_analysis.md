# CAMO Failure Case Analysis

更新时间：2026-06-14T00:30:00Z

本文档记录 Light-ESCNet B2-C64 与 ESCNet-B5 reference prediction 在 CAMO 可视化样本上的失败案例分析。它用于支撑论文中的可视化讨论和误差来源解释，不替代 clean ESCNet-B5 三数据集统一概率图复评。

## Evidence Inputs

- Case CSV: `/root/data-tmp/workspace/04_paper/figures/camo_case_selection_b5_light.csv`
- Case selection note: `/root/data-tmp/workspace/04_paper/figures/camo_case_selection_b5_light.md`
- Four-column visual grid: `/root/data-tmp/workspace/04_paper/figures/camo_visual_grid_b5_light_b2c64.png`
- Light-worse cases: `/root/data-tmp/workspace/04_paper/figures/camo_light_worse_cases.png`
- Light-close cases: `/root/data-tmp/workspace/04_paper/figures/camo_light_close_cases.png`
- Light-better cases: `/root/data-tmp/workspace/04_paper/figures/camo_light_better_cases.png`

Per-image MAE is computed after resizing predictions to the GT size if needed. The ESCNet-B5 column is a historical/reference visual comparator. It must not be described as the final clean same-protocol baseline until Gate 1 finishes NC4K, integrity checking and metadata aggregation.

## Summary Statistics

| Item | Value |
| --- | ---: |
| CAMO samples | 250 |
| Mean MAE delta, Light minus ESCNet-B5 reference | +0.008056 |
| Light worse than reference | 141 |
| Light better than reference | 109 |
| `abs(delta) < 0.005` | 140 |
| Light worse by at least 0.02 MAE | 36 |
| Light better by at least 0.02 MAE | 13 |
| Largest Light-worse delta | `camourflage_01141`, +0.284720 |
| Largest Light-better delta | `camourflage_01180`, -0.071069 |

The distribution is not a uniform collapse. More than half of the samples have very small MAE differences, while a smaller set of difficult images contributes most of the visible degradation. This is consistent with the main metric pattern: Light-B2-C64 keeps relatively close S-measure but loses more on weighted F-measure and MAE, especially on CAMO.

## Top Light-Worse Cases

| Case | ESCNet-B5 reference MAE | Light-B2-C64 MAE | Delta |
| --- | ---: | ---: | ---: |
| `camourflage_01141` | 0.304469 | 0.589189 | +0.284720 |
| `camourflage_01168` | 0.048627 | 0.269970 | +0.221343 |
| `camourflage_00519` | 0.048121 | 0.175054 | +0.126934 |
| `camourflage_01052` | 0.054415 | 0.176913 | +0.122498 |
| `camourflage_00102` | 0.058718 | 0.167425 | +0.108708 |
| `camourflage_00270` | 0.013665 | 0.113067 | +0.099402 |
| `camourflage_01154` | 0.056788 | 0.147171 | +0.090382 |
| `camourflage_00166` | 0.054904 | 0.141966 | +0.087061 |

Observed patterns:

1. Target parts are missed or shifted under strong texture and low contrast.
2. Thin structures are over-expanded or merged with nearby background texture.
3. Background regions sometimes receive high confidence, causing region bleeding.
4. Multi-part human or animal-like targets are more vulnerable to partial omission.

## Top Light-Better Cases

| Case | ESCNet-B5 reference MAE | Light-B2-C64 MAE | Delta |
| --- | ---: | ---: | ---: |
| `camourflage_01180` | 0.196785 | 0.125717 | -0.071069 |
| `camourflage_01087` | 0.145089 | 0.075531 | -0.069558 |
| `camourflage_01158` | 0.114429 | 0.050555 | -0.063874 |
| `camourflage_01194` | 0.411613 | 0.360561 | -0.051052 |
| `camourflage_01175` | 0.086789 | 0.035772 | -0.051017 |
| `camourflage_01170` | 0.457674 | 0.411342 | -0.046332 |
| `camourflage_01133` | 0.056579 | 0.011537 | -0.045041 |
| `camourflage_01110` | 0.077910 | 0.040879 | -0.037030 |

Observed patterns:

1. Light-B2-C64 can suppress scattered background highlights in some cases.
2. Some predictions become more compact, producing lower MAE even when boundaries are imperfect.
3. These better cases should be described as evidence of non-uniform degradation, not as proof that Light is generally superior on CAMO.

## Paper Wording Boundary

Safe wording:

- "CAMO per-image MAE analysis shows that Light-B2-C64 differs only slightly from the reference prediction on many images, but a smaller subset of cluttered or thin-structure cases contributes most of the MAE increase."
- "The failure cases suggest that the remaining gap is concentrated in local boundary quality, target-part completeness and background false positives."
- "This supports using KD and boundary-focused ablations as the next compensation routes."

Unsafe wording:

- Do not claim ESCNet-B5 final clean baseline superiority from this visual analysis alone.
- Do not generalize this CAMO-only pattern to COD10K or NC4K without per-image analysis on those datasets.
- Do not claim KD fixes these errors until KD full training and three-dataset probability evaluation pass.

