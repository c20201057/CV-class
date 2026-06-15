# Reproducibility Manifest

更新时间：2026-06-14T15:12:38Z

本文档是当前论文包的复现入口。它列出当前可复查的代码、数据、checkpoint、评测结果、profile、图表和审计命令。Gate 1 clean baseline、Gate 2 KD eval 和 Gate 3 controlled speed 已完成；KD 只能作为中性/负向结果分析，不能写作精度提升。

## Environment

- Workspace: `/root/data-tmp/workspace`
- Dataset root: `/root/data-tmp/COD`
- Hardware: 4 x Tesla V100-SXM2-16GB
- PyTorch/CUDA for accepted profile: PyTorch 2.5.1+cu121, CUDA 12.1
- Input size: 416
- Main accepted student: Light-ESCNet B2-C64 no-KD

## Code Boundaries

| Purpose | Path | Boundary |
| --- | --- | --- |
| Clean ESCNet-B5 baseline snapshot | `/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean` | clean baseline only |
| Light-ESCNet B2-C64 code | `/root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64` | accepted student code |
| KD Light-ESCNet code | `/root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64` | completed measured KD branch; neutral/negative result |
| Dirty external tree | `/root/ESCNet` | external observation; do not use as clean baseline |

Teacher checkpoint:

```text
/root/data-tmp/epoch_120.pth
sha256: 61847f70a489bf610f9c24d161611833a99c9558b4d628ed01567a5b538ed0dc
size: 382M
```

Do not use `/root/ESCNet/checkpoints/escnet/epoch_120.pth` as teacher or main baseline.

## Accepted Light-B2-C64 Run

| Item | Path / Value |
| --- | --- |
| Run directory | `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42` |
| Config | `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/config.yaml` |
| Checkpoint | `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/epoch_120.pth` |
| Checkpoint sha256 | `a6886fded30bef1e59f1ddc3d05078d6b8023aa0387867ded225b4d0775b3c7d` |
| Checkpoint size | 115M |
| Final train loss summary | `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/train_loss.csv` |
| Eval run | `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42_prob_eval_v2` |
| Eval metadata | `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42_prob_eval_v2/metadata.json` |
| Integrity | `check_run_integrity.py` pass through release audit |
| Final metadata audit | `/root/data-tmp/workspace/04_paper/drafts/light_final_metadata_audit_latest.md` |

Run metadata: `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/metadata.json` has been finalized with `status=complete_final_main_light`, final checkpoint sha256, final loss, eval run, profile JSON and integrity evidence paths.

Training config anchors:

- `backbone=pvt_v2_b2`
- `inter_channel=64`
- `epochs=120`
- `rand_seed=42`
- `batch_size=4` per GPU
- `batch_size_valid=8`
- `lr=7.5e-05`
- `weight_decay=0.00015`
- `device_ids=[0,1,2,3]`
- augmentations: flip, rotate, pepper, crop

## Metrics Evidence

Metrics CSV:

```text
/root/data-tmp/workspace/02_experiments/tables/metrics_all.csv
sha256: 76771307991a1bb4fcbba93204a6726050ee11b4a96f9c57865c031dd8efce7d
```

Accepted Light-B2-C64 probability metrics:

| Dataset | S | wF | meanF | meanE | MAE | Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| CAMO | 0.862 | 0.818 | 0.843 | 0.918 | 0.051 | final_main_light |
| COD10K | 0.866 | 0.782 | 0.808 | 0.928 | 0.024 | final_main_light |
| NC4K | 0.886 | 0.840 | 0.862 | 0.933 | 0.033 | final_main_light |

Current ESCNet-B5 reference boundary:

- Historical row is `historical_reference_not_clean_prob_final`.
- Gate 1 clean probability re-eval is complete for CAMO/COD10K/NC4K with `status=clean_prob_re_eval_complete` and `protocol=prob_map`.
- Clean ESCNet-B5 metrics are CAMO S=.881/wF=.842/meanF=.864/meanE=.933/MAE=.043, COD10K S=.877/wF=.802/meanF=.824/meanE=.938/MAE=.021, and NC4K S=.897/wF=.857/meanF=.878/meanE=.942/MAE=.029.
- Light-vs-ESCNet deltas in the current manuscript use the clean probability baseline; historical reference rows remain internal traceability evidence.

KD-B2-C64 probability metrics:

| Dataset | S | wF | meanF | meanE | MAE | Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| CAMO | 0.863 | 0.818 | 0.844 | 0.920 | 0.050 | final_main_kd |
| COD10K | 0.864 | 0.782 | 0.809 | 0.929 | 0.024 | final_main_kd |
| NC4K | 0.885 | 0.838 | 0.860 | 0.932 | 0.033 | final_main_kd |

KD evidence:

| Item | Path / Value |
| --- | --- |
| Config | `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config_continue_epoch20_b6_w8_4gpu.yaml` |
| Final run | `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu` |
| Final checkpoint | `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu/epoch_120.pth` |
| Checkpoint sha256 | `36f0680943279d77c038ee16f4e5a341dd4b9f61600d2a2d0bd579c13693c2ae` |
| Eval run | `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval` |
| Integrity | `check_run_integrity.py` pass through release audit with added KD integrity |
| Paper boundary | measured neutral/negative versus no-KD; no KD-improvement claim |

## Profile Evidence

Profiles CSV:

```text
/root/data-tmp/workspace/02_experiments/tables/profiles.csv
sha256: 055f668f5970310efc881d977ba74395b533e1f76418f05d88fe7ddbeb2bada5
```

Profile JSONs:

- ESCNet-B5 structural profile: `/root/data-tmp/workspace/02_experiments/runs/profile_escnet_b5_416/profile.json`
- Light-B2-C64 trained profile: `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/profile_epoch120.json`
- ESCNet-B5 idle profile: `/root/data-tmp/workspace/02_experiments/runs/profile_escnet_b5_416_idle/profile.json`
- Light-B2-C64 idle profile: `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/profile_epoch120_idle.json`
- KD-B2-C64 idle profile: `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu/profile_epoch120_idle.json`

Structural comparison:

| Model | Params(M) | GMACs | Model Size(MB) | Peak Mem(MB) | Status |
| --- | ---: | ---: | ---: | ---: | --- |
| ESCNet-B5 C128 | 99.90 | 129.02 | 381.17 | 829.77 | structural reference |
| Light-B2-C64 | 29.81 | 36.39 | 113.74 | 237.44 | accepted student |

Controlled idle-GPU speed profile:

| Model | Latency(ms) | FPS | Condition |
| --- | ---: | ---: | --- |
| ESCNet-B5 C128 | 73.01 | 13.70 | idle V100, 416, batch 1, warmup 50, repeat 100 |
| Light-B2-C64 | 34.31 | 29.15 | idle V100, 416, batch 1, warmup 50, repeat 100 |
| KD-B2-C64 | 34.84 | 28.71 | idle V100, 416, batch 1, warmup 50, repeat 100 |

## Paper-Facing Assets

| Asset | Path |
| --- | --- |
| Interim manuscript | `/root/data-tmp/workspace/04_paper/drafts/paper_interim_submission.md` |
| Working draft | `/root/data-tmp/workspace/04_paper/drafts/paper_draft.md` |
| Submission packet | `/root/data-tmp/workspace/04_paper/drafts/paper_submission_packet.md` |
| Claim-evidence matrix | `/root/data-tmp/workspace/04_paper/drafts/paper_claim_evidence_matrix.md` |
| Citation manifest | `/root/data-tmp/workspace/04_paper/drafts/citation_manifest.md` |
| Main table template | `/root/data-tmp/workspace/04_paper/tables/main_results_template.md` |
| Aggregated results | `/root/data-tmp/workspace/04_paper/tables/aggregated_results.md` |
| Method figure | `/root/data-tmp/workspace/04_paper/figures/light_b2_c64_method.png` |
| Accuracy-efficiency figure | `/root/data-tmp/workspace/04_paper/figures/accuracy_efficiency_scatter.png` |
| CAMO visual grid | `/root/data-tmp/workspace/04_paper/figures/camo_visual_grid_b5_light_b2c64.png` |
| CAMO failure note | `/root/data-tmp/workspace/04_paper/drafts/camo_failure_case_analysis.md` |
| CAMO failure-number audit | `/root/data-tmp/workspace/04_paper/drafts/camo_failure_case_number_audit_latest.md` |

## Recheck Commands

Run all non-GPU release checks:

```bash
TMPDIR=/root/data-tmp/tmp /root/data-tmp/workspace/02_experiments/scripts/run_release_audits.sh \
  --add-integrity /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval \
  kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval \
  CAMO,COD10K,NC4K
```

Check accepted Light probability eval integrity:

```bash
python /root/data-tmp/workspace/02_experiments/scripts/check_run_integrity.py \
  --run_dir /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42_prob_eval_v2 \
  --exp_id light_b2_c64_e120_s42_prob_eval_v2 \
  --datasets CAMO,COD10K,NC4K \
  --dataset_root /root/data-tmp/COD/Test \
  --metrics_csv /root/data-tmp/workspace/02_experiments/tables/metrics_all.csv
```

Check accepted KD probability eval integrity:

```bash
python /root/data-tmp/workspace/02_experiments/scripts/check_run_integrity.py \
  --run_dir /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval \
  --exp_id kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval \
  --datasets CAMO,COD10K,NC4K \
  --dataset_root /root/data-tmp/COD/Test \
  --metrics_csv /root/data-tmp/workspace/02_experiments/tables/metrics_all.csv
```

Refresh global status:

```bash
python /root/data-tmp/workspace/02_experiments/scripts/orchestrator_tick.py
```

## Pending Gates

| Gate | Status | Next action |
| --- | --- | --- |
| Gate 1 clean ESCNet-B5 probability baseline | complete | keep baseline integrity in release audit; do not duplicate the wrapper |
| Gate 2 KD B2-C64 | complete | use as neutral/negative KD evidence; do not claim KD improvement |
| Gate 3 idle speed | complete | report latency/FPS only with controlled idle V100 profile condition |
| Gate 4A B0 | observation only | candidate eval only if it does not block Gate 1/KD |
| Gate 4B MobileMamba | observation only | candidate eval only after checkpoint appears and main queue is protected |
