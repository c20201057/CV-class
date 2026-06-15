# Claim Evidence Audit

更新时间：2026-06-14T15:12:38Z / 2026-06-14 23:12:38 CST

本文档用于逐条验收 `paper_draft.md` 中的主张是否有证据支撑。结论分为 `accepted`、`interim/reference only`、`pending` 和 `forbidden before gate`。

## Accepted Claims

| Claim | Evidence | Status |
| --- | --- | --- |
| Light-ESCNet B2-C64 no-KD 已完成 120 epoch 训练 | `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/epoch_120.pth`, train log | accepted |
| Light-ESCNet B2-C64 已完成 CAMO/COD10K/NC4K 概率图评测 | `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42_prob_eval_v2`, `metrics_all.csv` | accepted |
| Light-B2-C64 输出不是二值 smoke 结果 | `check_run_integrity.py` 通过，probability output unique value check | accepted |
| Light-B2-C64 params=29.81M, GMACs=36.39, model size=113.74MB, peak mem=237.44MB | `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/profile_epoch120.json`, `profiles.csv` | accepted |
| 相比 ESCNet-B5 结构，Light-B2-C64 参数量、GMACs、模型大小和峰值显存约降 70% | `profiles.csv` baseline/light rows | accepted |
| CAMO failure-case analysis 支持可视化段落中的错误类型解释，但只能作为 CAMO reference visual analysis | `/root/data-tmp/workspace/04_paper/drafts/camo_failure_case_analysis.md`, CAMO case selection CSV/figures | accepted |
| KD 分支已完成 online teacher output-level MSE 的 120 epoch 训练与三数据集评测；结果相对 no-KD 基本持平或略低 | KD final run, KD probability eval, `metrics_all.csv status=final_main_kd`, `current_delta_summary.md` | accepted as failure analysis |
| clean ESCNet-B5 source snapshot 已固化 | `/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean` | accepted |
| `/root/data-tmp/epoch_120.pth` 与 clean ESCNet-B5 strict load 匹配 | strict load check: missing=0, unexpected=0, params=99,903,234 | accepted |
| clean ESCNet-B5 三数据集 probability baseline 已完成 | `/root/data-tmp/workspace/02_experiments/runs/baseline_escnet_b5_clean_prob_e120`, `metrics_all.csv status=clean_prob_re_eval_complete` | accepted |

## Interim / Reference Only Claims

| Claim | Evidence | Required Upgrade |
| --- | --- | --- |
| 历史 ESCNet-B5 reference 可用于追溯早期路线判断 | ESCNet-B5 historical row archived in `metrics_all.csv` and `02_experiments/metadata/baseline_escnet_b5_416_e120.json` | Do not use as current same-protocol delta |

## Pending Claims

| Claim | Missing Evidence | Current Handling |
| --- | --- | --- |
| KD 能提升 Light-B2-C64 精度或缩小 CAMO wF/MAE 差距 | completed KD eval does not support this claim | forbidden by measured deltas |
| B2-C128/B5-C64 能拆分 backbone 与 decoder 贡献 | full train/eval or accepted short-run evidence | keep as ablation plan |
| Edge branch removal 的贡献 | no completed run | keep as ablation plan |
| Light-B2-C64 controlled latency/FPS numbers | idle same-command profile for baseline/light/KD | report only with profile condition |
| B0 extreme compression has useful result | dirty B0 checkpoints now include `epoch_120.pth`; epoch120 metrics are appended, and latest checkpoint/eval state is delegated to `b0_external_status_latest.md`. COD10K intermediate metrics through epoch120 are appended. Latest complete row epoch120 is S=.8004/wF=.6862/meanF=.7203/meanE=.8878/MAE=.0350. Epoch 100 remains current B0 best complete row at S=.8014/wF=.6882/meanF=.7221/meanE=.8899/MAE=.0346, still below accepted Light-B2-C64 COD10K; no acceptable checkpoint or three-dataset eval | observation only |
| MobileMamba-T2 alternative lightweight backbone has useful result | external dirty-tree branch is still training; no candidate checkpoint snapshot, load/profile, three-dataset probability eval, or integrity pass | observation only |

## Forbidden Before Gate

- Do not use the historical ESCNet-B5 reference as the current same-protocol baseline.
- Do not write “KD improves performance”; Gate 2 passed but measured deltas do not support it.
- Do not generalize controlled FPS/latency to real deployment; Gate 3 only supports idle V100 profile conditions.
- Do not put B0 in the main table until Gate 4A passes.
- Do not put MobileMamba in the main table until Gate 4B passes.
- Do not claim SOTA, first KD-COD, real-time deployment, or edge-device deployment without direct evidence.
- Do not cite `/root/ESCNet/checkpoints/escnet/epoch_120.pth` as teacher or main baseline.

## Current Draft Decision

`paper_draft.md` is acceptable as an interim paper draft if it keeps:

- ESCNet-B5 current deltas use the Gate 1 clean probability baseline.
- Historical ESCNet-B5 metrics remain labeled as `historical reference` only where they are used for traceability.
- KD framed as measured neutral/negative failure analysis; B0/MobileMamba/ablation sections framed as observation or plan.
- Speed section reports controlled idle V100 profile conditions.

Before final submission, run this checklist again after Gate 2/3 manuscript patches and release audit.
