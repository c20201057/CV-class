# Visual Case Selection

Baseline: `ESCNet-B5`
Target: `Light-B2-C64`

MAE is computed per image after resizing predictions to GT size if needed.

## Recommended Groups

- Light worse than baseline: camourflage_01141, camourflage_01168, camourflage_00519, camourflage_01052, camourflage_00102, camourflage_00270, camourflage_01154, camourflage_00166
- Light close to baseline: camourflage_01148, camourflage_01050, camourflage_00259, camourflage_01210, camourflage_00141, camourflage_00224, camourflage_00750, camourflage_00337
- Light better than baseline: camourflage_01180, camourflage_01087, camourflage_01158, camourflage_01194, camourflage_01175, camourflage_01170, camourflage_01133, camourflage_01110
- Hard cases for Light: camourflage_01141, camourflage_01170, camourflage_01194, camourflage_01126, camourflage_01168, camourflage_00285, camourflage_01016, camourflage_00478

## Top Light-Worse Cases

| stem | ESCNet-B5 MAE | Light-B2-C64 MAE | delta |
| --- | ---: | ---: | ---: |
| camourflage_01141 | 0.304469 | 0.589189 | 0.284720 |
| camourflage_01168 | 0.048627 | 0.269970 | 0.221343 |
| camourflage_00519 | 0.048121 | 0.175054 | 0.126934 |
| camourflage_01052 | 0.054415 | 0.176913 | 0.122498 |
| camourflage_00102 | 0.058718 | 0.167425 | 0.108708 |
| camourflage_00270 | 0.013665 | 0.113067 | 0.099402 |
| camourflage_01154 | 0.056788 | 0.147171 | 0.090382 |
| camourflage_00166 | 0.054904 | 0.141966 | 0.087061 |

## Top Light-Better Cases

| stem | ESCNet-B5 MAE | Light-B2-C64 MAE | delta |
| --- | ---: | ---: | ---: |
| camourflage_01180 | 0.196785 | 0.125717 | -0.071069 |
| camourflage_01087 | 0.145089 | 0.075531 | -0.069558 |
| camourflage_01158 | 0.114429 | 0.050555 | -0.063874 |
| camourflage_01194 | 0.411613 | 0.360561 | -0.051052 |
| camourflage_01175 | 0.086789 | 0.035772 | -0.051017 |
| camourflage_01170 | 0.457674 | 0.411342 | -0.046332 |
| camourflage_01133 | 0.056579 | 0.011537 | -0.045041 |
| camourflage_01110 | 0.077910 | 0.040879 | -0.037030 |
