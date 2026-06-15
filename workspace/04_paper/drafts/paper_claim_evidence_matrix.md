# Paper Claim Evidence Matrix

更新时间：2026-06-14T15:12:38Z / 2026-06-14 23:12:38 CST

本文档把 `paper_interim_submission.md` 中可以写、只能暂写、必须等待 gate 的论文主张逐条绑定到证据。它比 `claim_evidence_audit.md` 更细，供总控和后续 agent 回填结果时逐项验收。

总原则：先证据，后结论。任何 agent 新增结果都必须先补齐路径、metadata、完整性检查和审计，再进入摘要、主表和结论。

## 当前可写入论文的主张

| ID | 主张 | 证据路径 | 论文位置 | 状态 |
| --- | --- | --- | --- | --- |
| C01 | Light-ESCNet B2-C64 no-KD 已完成 120 epoch 四卡训练。 | `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/epoch_120.pth`; `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/log.txt`; `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/train_loss.csv` | 摘要、4.2、4.8 | accepted |
| C02 | Light-ESCNet B2-C64 使用概率图协议完成 CAMO/COD10K/NC4K 三数据集评测。 | `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42_prob_eval_v2/metadata.json`; `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42_prob_eval_v2/integrity.csv`; `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42_prob_eval_v2/results/CAMO/result.txt`; `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42_prob_eval_v2/results/COD10K/result.txt`; `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42_prob_eval_v2/results/NC4K/result.txt`; `/root/data-tmp/workspace/02_experiments/tables/metrics_all.csv` | 摘要、4.1、4.4 | accepted |
| C03 | Light-ESCNet B2-C64 的三数据集结果为 CAMO S=.862/wF=.818/MAE=.051，COD10K S=.866/wF=.782/MAE=.024，NC4K S=.886/wF=.840/MAE=.033。 | `/root/data-tmp/workspace/02_experiments/tables/metrics_all.csv`; `/root/data-tmp/workspace/04_paper/drafts/interim_submission_number_audit_latest.md` | 摘要、表 1、表 2 | accepted |
| C04 | Light-vs-ESCNet 当前使用固定源码同协议 clean probability baseline：三数据集平均 S 0.885 -> 0.871，MAE 0.031 -> 0.036。 | `/root/data-tmp/workspace/02_experiments/tables/metrics_all.csv`; `/root/data-tmp/workspace/02_experiments/runs/baseline_escnet_b5_clean_prob_e120`; `/root/data-tmp/workspace/02_experiments/runs/baseline_escnet_b5_clean_prob_e120/integrity.csv`; `/root/data-tmp/workspace/04_paper/drafts/current_delta_summary.md` | 摘要、4.3、4.4、5 | accepted |
| C05 | Light-ESCNet B2-C64 相对 ESCNet-B5 C128 将参数量、GMACs、模型大小和峰值显存降低约 70%。 | `/root/data-tmp/workspace/02_experiments/tables/profiles.csv`; `/root/data-tmp/workspace/02_experiments/runs/profile_escnet_b5_416/profile.json`; `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/profile_epoch120.json`; `/root/data-tmp/workspace/04_paper/drafts/current_delta_summary.md` | 摘要、4.5、5 | accepted |
| C06 | Light-ESCNet 的结构改造是 PVTv2-B5 到 PVTv2-B2 的主干压缩，以及 decoder hidden channel 128 到 64 的宽度压缩，同时保留边缘-语义协同路径。 | `/root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64`; `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/config.yaml`; `/root/data-tmp/workspace/02_experiments/configs/light_b2_c64.yaml`; `/root/data-tmp/workspace/04_paper/drafts/method_light_b2_c64.md`; `/root/data-tmp/workspace/04_paper/figures/light_b2_c64_method.png` | 3.2、3.4、图 1 | accepted |
| C07 | ESCNet-B5 teacher/checkpoint 固定为 `/root/data-tmp/epoch_120.pth`，不能使用 `/root/ESCNet/checkpoints/escnet/epoch_120.pth` 作为 teacher 或主 baseline。 | `/root/data-tmp/epoch_120.pth`; `/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean/BASELINE_SOURCE.md`; `/root/data-tmp/workspace/04_paper/drafts/evidence_index.md`; `/root/data-tmp/workspace/04_paper/drafts/finalization_gates.md` | 3.1、4.3 | accepted |
| C08 | clean ESCNet-B5 source snapshot 已固化，且 `/root/data-tmp/epoch_120.pth` 可严格加载到 clean ESCNet-B5。 | `/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean/BASELINE_SOURCE.md`; `/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean/config.local.yaml`; `/root/data-tmp/workspace/04_paper/drafts/evidence_index.md` | 3.1、4.3 | accepted for checkpoint boundary |
| C09 | KD 分支已完成 online teacher output-level MSE 的 120 epoch 训练、三数据集概率图评测和完整性检查；相对 no-KD 基本持平或略低，不能写 KD 提升。 | `/root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64`; `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu/epoch_120.pth`; `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval`; `/root/data-tmp/workspace/02_experiments/tables/metrics_all.csv`; `/root/data-tmp/workspace/04_paper/drafts/current_delta_summary.md` | 3.3、4.4、4.6、4.8、5 | accepted |
| C10 | 当前论文可以报告受控 latency/FPS 数字：ESCNet-B5 73.01 ms / 13.70 FPS，Light-B2-C64 34.31 ms / 29.15 FPS，KD student 34.84 ms / 28.71 FPS；条件为 idle V100、416 输入、batch 1、warmup=50、repeat=100。 | `/root/data-tmp/workspace/02_experiments/tables/profiles.csv`; `/root/data-tmp/workspace/02_experiments/runs/profile_escnet_b5_416_idle/profile.json`; `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/profile_epoch120_idle.json`; `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu/profile_epoch120_idle.json`; `/root/data-tmp/workspace/04_paper/drafts/current_delta_summary.md` | 4.1、4.5、5 | accepted |
| C11 | B0/PVTv2-B0 外部分支只有 COD10K 中间观察；raw checkpoints 已包括 `epoch_120.pth`，epoch120 metrics 已落表，最新 checkpoint/eval 状态以 live status 为准。epoch120 是最新完整行。epoch100 仍是当前最好行。该分支尚未完成 checkpoint 验证、profile、三数据集评估和完整性检查，不能入主表或摘要。 | `/root/data-tmp/results_train/pvt_v2_b0/result.txt`; `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0`; `/root/data-tmp/preds_train/pvt_v2_b0`; `/root/data-tmp/workspace/02_experiments/runs/b0_external_observation.md`; `/root/data-tmp/workspace/02_experiments/runs/b0_external_status_latest.md`; `/root/data-tmp/workspace/02_experiments/runs/b0_intermediate_trend_note.md`; `/root/data-tmp/workspace/04_paper/drafts/b0_cod10k_trend_note.md`; `/root/data-tmp/workspace/04_paper/figures/b0_cod10k_intermediate_trend.png`; `/root/data-tmp/workspace/02_experiments/code/external_b0_dirty_snapshot_20260613T200614Z_epoch70_metrics_observation` | 4.6、4.8 或工程备注 | observation only |
| C12 | 当前清洁版 interim 论文稿中的关键数字、图像引用和越界主张均已通过自动审计。 | `/root/data-tmp/workspace/04_paper/drafts/paper_interim_submission.md`; `/root/data-tmp/workspace/04_paper/drafts/interim_submission_number_audit_latest.md`; `/root/data-tmp/workspace/04_paper/drafts/paper_asset_audit_latest.md`; `/root/data-tmp/workspace/04_paper/drafts/claim_text_audit_latest.md`; `/root/data-tmp/workspace/04_paper/drafts/release_audit_latest.md` | 全文交付状态 | accepted |
| C13 | MobileMamba-T2 外部分支当前未观察到运行，仍只作为 dirty `/root/ESCNet` 替代轻量主干观察。最新且最高 S 的 COD10K 观察行是 epoch50 S=.7487/wF=.6019/meanF=.6482/meanE=.8477/MAE=.0465；最新状态以 live status 为准，未完成候选 checkpoint 验证、profile、三数据集评估和完整性检查前，不能入主表或摘要。 | `/root/data-tmp/workspace/02_experiments/runs/mobilemamba_t2_external_status_latest.md`; `/root/data-tmp/workspace/02_experiments/runs/watch_external_mobilemamba_progress.log`; `/root/data-tmp/workspace/02_experiments/scripts/start_mobilemamba_candidate_eval.sh`; `/root/data-tmp/workspace/02_experiments/scripts/snapshot_external_mobilemamba_dirty_tree.sh`; `/root/data-tmp/ESCNet/checkpoints/mobilemamba_t2` | 4.6、4.8 或工程备注 | observation only |
| C14 | CAMO failure-case analysis 可用于解释 Light-B2-C64 在 CAMO 上 wF/MAE 损失更明显：多数样本差异较小，但强纹理、细长结构、背景高置信误检和多部件目标局部遗漏构成主要失败类型。该结论只限 CAMO reference visual analysis，不推广到 COD10K/NC4K。 | `/root/data-tmp/workspace/04_paper/drafts/camo_failure_case_analysis.md`; `/root/data-tmp/workspace/04_paper/figures/camo_case_selection_b5_light.csv`; `/root/data-tmp/workspace/04_paper/figures/camo_case_selection_b5_light.md`; `/root/data-tmp/workspace/04_paper/figures/camo_light_worse_cases.png`; `/root/data-tmp/workspace/04_paper/figures/camo_light_close_cases.png`; `/root/data-tmp/workspace/04_paper/figures/camo_light_better_cases.png` | 4.7/4.8 可视化分析 | accepted |

## Gate 后才能升级的主张

| Gate | 允许升级的主张 | 触发证据 | 升级前写法 |
| --- | --- | --- | --- |
| Gate 1 clean baseline | ESCNet-B5 clean probability baseline 已通过；Light-vs-baseline 差值已经可写成同协议差值。 | `baseline_escnet_b5_clean_prob_e120` 三数据集 probability eval、integrity pass、`metrics_all.csv status=clean_prob_re_eval_complete` | 已升级为 clean baseline 口径 |
| Gate 2 KD | KD 负结果分析已可写；KD 提升或缩小差距不能写。 | KD 完整 checkpoint、三数据集 probability eval、integrity pass、`metrics_all.csv status=final_main_kd` | 已升级为 failure-analysis 口径 |
| Gate 3 speed | baseline/Light/KD 的受控 latency/FPS 数字。 | 空闲 GPU、同命令、同输入尺寸、profile metadata 完整 | 已升级为 controlled speed 口径 |
| Gate 4A B0 | B0 作为附录探索或失败分析。 | 可验收 checkpoint、代码快照、profile、三数据集 probability eval、integrity pass | 只能写外部观察 |
| Gate 4B MobileMamba | MobileMamba-T2 作为附录探索或失败分析。 | 可验收 checkpoint、代码快照、profile、三数据集 probability eval、integrity pass | 只能写外部观察 |

## 明确禁止的写法

- 不混用 dirty/historical baseline；Gate 1 已通过后仍必须只使用 clean snapshot 和 `/root/data-tmp/epoch_120.pth` 的同协议证据。
- 不写 “KD 提升”“蒸馏有效”“缩小差距”；Gate 2 已通过但实测 deltas 不支持这些主张。
- latency/FPS 只能按 Gate 3 的 idle V100 controlled profile 条件报告，不推广为真实边缘端部署表现。
- 不把 B0 或 MobileMamba 写入主表、摘要或结论，直到对应 Gate 4A/4B 通过。
- 不写 SOTA、首次 KD-COD、实时部署、边缘端部署等没有直接证据的强主张。

## 使用方式

1. 修改摘要、4.4、4.5 或结论前，先检查本矩阵对应 ID 是否为 `accepted` 或明确允许的 `reference only`。
2. 新结果落盘后，先补本矩阵证据路径，再运行 release audit。
3. Gate 1/2/3 任一完成后，按 `paper_gate_patch_matrix.md` 更新正文和表格，再更新本矩阵状态。
