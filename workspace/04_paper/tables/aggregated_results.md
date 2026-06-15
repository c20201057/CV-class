# Aggregated Results

## Main Compact Table

| Exp ID | Params(M) | GMACs | Speed Status | Metric Status | CAMO S/wF/MAE | COD10K S/wF/MAE | NC4K S/wF/MAE |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| baseline_escnet_b5_clean_prob_e120 | 99.90 | 129.02 | 73.01 ms / 13.70 FPS (cuda:0, warmup=50, repeat=100) | clean_prob_re_eval_complete | 0.881/0.842/0.043 | 0.877/0.802/0.021 | 0.897/0.857/0.029 |
| light_b2_c64_trained_416 | 29.81 | 36.39 | 34.31 ms / 29.15 FPS (cuda:0, warmup=50, repeat=100) | final_main_light | 0.862/0.818/0.051 | 0.866/0.782/0.024 | 0.886/0.840/0.033 |
| kd_light_b2_c64_trained_416 | 29.81 | 36.39 | 34.84 ms / 28.71 FPS (cuda:0, warmup=50, repeat=100) | final_main_kd | 0.863/0.818/0.050 | 0.864/0.782/0.024 | 0.885/0.838/0.033 |

- `baseline_escnet_b5_clean_prob_e120` is the accepted clean probability baseline row when CAMO/COD10K/NC4K all have `clean_prob_re_eval_complete`; its structural profile is shared with `baseline_escnet_b5_416_idle` for controlled speed.
- `light_b2_c64_trained_416` uses the trained-checkpoint profile for params/GMACs/model size/peak memory and the idle same-command profile for latency/FPS.
- `kd_light_b2_c64_trained_416` reports the final KD checkpoint only as measured evidence; precision claims must follow the observed deltas.

## Metric Coverage

| Exp ID | Datasets | Three Datasets Present | Evidence Status |
| --- | --- | --- | --- |
| baseline_escnet_b5_416_e120 | CAMO, COD10K, NC4K | yes | historical_reference_not_clean_prob_final |
| baseline_escnet_b5_clean_prob_e120 | CAMO, COD10K, NC4K | yes | clean_prob_re_eval_complete |
| kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval | CAMO, COD10K, NC4K | yes | final_main_kd |
| light_b2_c64_e120_s42_prob_eval_v2 | CAMO, COD10K, NC4K | yes | final_main_light |
| teacher_escnet_b5_prob_e120 | CAMO | no | verification_only_camo |
