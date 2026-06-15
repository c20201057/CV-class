# 主结果表模板

本文件只放论文表格结构和填表规则。正式数值来源以 `/root/data-tmp/workspace/02_experiments/tables/*.csv` 和对应 run metadata 为准。

## Table 1A. Completed Probability-Protocol Accuracy Results

主精度表必须使用概率图推理结果。不要混用 `test.py` 二值化输出。当前可作为完整主结果的是固定源码同协议 ESCNet-B5 基线和 Light-ESCNet B2-C64；KD 行作为已完成负结果分析，不作为提升主张。

| Model | Backbone | Training | Protocol | CAMO S↑ | CAMO wF↑ | CAMO mF↑ | CAMO mE↑ | CAMO MAE↓ | COD10K S↑ | COD10K wF↑ | COD10K mF↑ | COD10K mE↑ | COD10K MAE↓ | NC4K S↑ | NC4K wF↑ | NC4K mF↑ | NC4K mE↑ | NC4K MAE↓ | Evidence Status |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| ESCNet-B5 | PVTv2-B5 C128 | no KD, epoch120 | prob_map | 0.881 | 0.842 | 0.864 | 0.933 | 0.043 | 0.877 | 0.802 | 0.824 | 0.938 | 0.021 | 0.897 | 0.857 | 0.878 | 0.942 | 0.029 | clean_prob_re_eval_complete |
| Light-ESCNet | PVTv2-B2 C64 | no KD, epoch120 | prob_map | 0.862 | 0.818 | 0.843 | 0.918 | 0.051 | 0.866 | 0.782 | 0.808 | 0.928 | 0.024 | 0.886 | 0.840 | 0.862 | 0.933 | 0.033 | final_main_light |
| Light-ESCNet + KD | PVTv2-B2 C64 | online output-level KD, epoch120 | prob_map | 0.863 | 0.818 | 0.844 | 0.920 | 0.050 | 0.864 | 0.782 | 0.809 | 0.929 | 0.024 | 0.885 | 0.838 | 0.860 | 0.932 | 0.033 | final_main_kd; failure analysis |

## Table 1B. ESCNet-B5 Reference And Baseline Verification

这些数值用于追溯历史参考，不作为当前主差值口径。

| Model | Backbone | Evidence Type | Protocol | CAMO S↑ | CAMO wF↑ | CAMO mF↑ | CAMO mE↑ | CAMO MAE↓ | COD10K S↑ | COD10K wF↑ | COD10K mF↑ | COD10K mE↑ | COD10K MAE↓ | NC4K S↑ | NC4K wF↑ | NC4K mF↑ | NC4K mE↑ | NC4K MAE↓ | Evidence Status |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| ESCNet-B5 | PVTv2-B5 | historical result file | historical_legacy | 0.875 | 0.849 | 0.867 | 0.937 | 0.041 | 0.873 | 0.808 | 0.827 | 0.942 | 0.020 | 0.893 | 0.864 | 0.881 | 0.945 | 0.028 | historical_reference_not_clean_prob_final |

## Table 1C. Observation-Only Accuracy Rows

| Model | Backbone | Training | CAMO | COD10K | NC4K | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Tiny-ESCNet | PVTv2-B0 C64 | KD/extreme compression | TBD | COD10K intermediate rows through epoch120, delegated to `02_experiments/runs/b0_external_status_latest.md`; latest complete row epoch120 S=.8004/wF=.6862/mF=.7203/mE=.8878/MAE=.0350; best observed row epoch100 S=.8014/wF=.6882/mF=.7221/mE=.8899/MAE=.0346 | TBD | external dirty-tree observation only; no accepted code snapshot, profile, or three-dataset probability eval |
| MobileMamba-ESCNet | MobileMamba-T2 C64-style decoder | online KD/alternative lightweight backbone | TBD | COD10K observation delegated to `02_experiments/runs/mobilemamba_t2_external_status_latest.md`; latest observed row epoch50 S=.7487/wF=.6019/mF=.6482/mE=.8477/MAE=.0465 | TBD | external dirty-tree observation only; no accepted checkpoint snapshot, profile, or three-dataset probability eval |

## Table 2. Structural Efficiency Comparison

效率表使用结构 profile 中可稳定复核的参数量、GMACs、模型大小和峰值显存。Latency/FPS 已完成受控复测；报告时必须注明 idle V100、416 输入、batch 1、warmup=50、repeat=100。

| Model | Backbone | Channel | Params (M)↓ | GMACs↓ | Model Size (MB)↓ | Peak Mem (MB)↓ | Reduction vs ESCNet-B5 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| ESCNet-B5 | PVTv2-B5 | 128 | 99.90 | 129.02 | 381.17 | 829.77 | reference |
| Light-ESCNet | PVTv2-B2 | 64 | 29.81 | 36.39 | 113.74 | 237.44 | Params -70.16%; GMACs -71.79%; Size -70.16%; Mem -71.38% |

## Table 2B. Controlled Speed Profile

| Model | Backbone | Channel | Latency (ms)↓ | FPS↑ | Condition |
| --- | --- | ---: | ---: | ---: | --- |
| ESCNet-B5 | PVTv2-B5 | 128 | 73.01 | 13.70 | idle V100, 416, batch 1 |
| Light-ESCNet | PVTv2-B2 | 64 | 34.31 | 29.15 | idle V100, 416, batch 1 |
| Light-ESCNet + KD | PVTv2-B2 | 64 | 34.84 | 28.71 | idle V100, 416, batch 1 |

## Table 3. Ablation Plan

| ID | Model | Backbone | Channel | Boundary Branch | KD | Purpose | Status |
| --- | --- | --- | ---: | --- | --- | --- | --- |
| A0 | ESCNet-B5 | PVTv2-B5 | 128 | yes | no | heavy teacher/reference | clean probability baseline complete |
| A1 | LightBackbone | PVTv2-B2 | 128 | yes | no | isolate backbone compression | optional |
| A2 | Light-ESCNet | PVTv2-B2 | 64 | yes | no | main lightweight student | full train/eval complete |
| A3 | Light-ESCNet + KD | PVTv2-B2 | 64 | yes | yes | test distillation compensation | full train/eval complete; neutral/negative vs no-KD |
| A4 | Light-ESCNet w/o edge | PVTv2-B2 | 64 | no | no | test edge branch value | optional/high risk |
| A5 | Tiny-ESCNet | PVTv2-B0 | 64 | yes | yes | extreme compression | external high-risk branch under `/root/ESCNet`; include only if full checkpoint/eval exists |
| A6 | MobileMamba-ESCNet | MobileMamba-T2 | config-defined | yes | yes | alternative lightweight backbone observation | external high-risk branch under dirty `/root/ESCNet`; not eligible for final result table unless Gate 4B full candidate eval passes |

## Fill Rules

1. Accuracy cells must cite the `metrics_all.csv` row, including `protocol`, `repo_boundary`, `checkpoint`, and `status`.
2. Efficiency cells must cite `profiles.csv` and the profile JSON.
3. Do not report `/root/ESCNet/checkpoints/escnet/epoch_120.pth` as the teacher baseline.
4. Mark binary-threshold smoke results as smoke only; they are not main paper results.
5. If full probability baseline differs slightly from historical predictions, report the unified probability re-eval in the main table and mention historical baseline only as reference evidence.
6. Report FPS/latency only with the controlled idle V100 profile condition; do not generalize to real edge-device deployment.
7. Light-vs-ESCNet deltas now use the clean probability baseline; historical rows stay only as reference evidence.
