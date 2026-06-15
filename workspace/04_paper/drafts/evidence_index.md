# Paper Evidence Index

更新时间：2026-06-14T15:12:38Z / 2026-06-14 23:12:38 CST

本文档用于把论文草稿中的关键数字、图表和结论追溯到实验产物。没有列在这里的结果不要直接写成定稿结论。

## 已可支撑的主结论

### Light-ESCNet B2-C64 完整训练

- 运行目录：`/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42`
- checkpoint：`epoch_120.pth`
- 配置：`config.yaml`
- 训练结论：120 epoch 完成，最终平均训练损失 1.369。
- 可写结论：Light-ESCNet B2-C64 no-KD 已完成完整训练。

### 三数据集概率图评测

- 评测目录：`/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42_prob_eval_v2`
- 汇总表：`/root/data-tmp/workspace/02_experiments/tables/metrics_all.csv`
- 元数据状态：`protocol=prob_map`, `repo_boundary=light_b2_c64_snapshot`, `status=final_main_light`。
- CAMO：S=.862, wF=.818, meanF=.843, meanE=.918, MAE=.051
- COD10K：S=.866, wF=.782, meanF=.808, meanE=.928, MAE=.024
- NC4K：S=.886, wF=.840, meanF=.862, meanE=.933, MAE=.033
- 可写结论：Light-B2-C64 在三个主流 COD 测试集上完成概率图评测。

## 参考证据与已验收 baseline

### 历史 ESCNet-B5 reference

- 汇总表：`/root/data-tmp/workspace/02_experiments/tables/metrics_all.csv`
- 历史结果记录的原始来源：`/root/ESCNet/results_epoch120/result.txt`；该原始文件在当前工作树中不再可见，当前可复核归档为 `metrics_all.csv` 和 `02_experiments/metadata/baseline_escnet_b5_416_e120.json`。
- clean baseline 源码快照：`/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean`
- clean baseline 来源 commit：`/root/ESCNet` git HEAD `25c4387e4ea94c247d83a91a749e87b959483a4e`
- CAMO：S=.875, wF=.849, meanF=.867, meanE=.937, MAE=.041
- COD10K：S=.873, wF=.808, meanF=.827, meanE=.942, MAE=.020
- NC4K：S=.893, wF=.864, meanF=.881, meanE=.945, MAE=.028
- 证据状态：`historical_reference_not_clean_prob_final`。
- 元数据状态：`protocol=historical_legacy`, `repo_boundary=dirty_history_result`；只作为 reference evidence。
- 写作边界：历史 ESCNet-B5 参考行只保留为内部追溯证据；当前同协议 baseline 使用 Gate 1 clean probability baseline。
- 代码边界：`/root/ESCNet` 当前为 dirty 工作树，后续 baseline 复评不要直接以其作为 clean baseline repo。
- checkpoint 归档边界：`/root/ESCNet/checkpoints/escnet` 现在是指向 `/root/data-tmp/workspace/02_experiments/runs/legacy_root_ESCNet_checkpoints_escnet_20260613` 的 symlink；其中 `epoch_120.pth` 是 2026-06-13 后续重训产物，只能作为 legacy artifact。

### Clean ESCNet-B5 checkpoint verification

- strict 加载验证：clean ESCNet-B5 + `/root/data-tmp/epoch_120.pth` 在 CPU 上 missing=0、unexpected=0，参数量 99,903,234。
- Gate 1 clean probability 复评：`/root/data-tmp/epoch_120.pth` 已在 clean snapshot 中完成 CAMO/COD10K/NC4K，CAMO S=.881, wF=.842, meanF=.864, meanE=.933, MAE=.043；COD10K S=.877, wF=.802, meanF=.824, meanE=.938, MAE=.021；NC4K S=.897, wF=.857, meanF=.878, meanE=.942, MAE=.029。
- 元数据状态：`teacher_escnet_b5_prob_e120` 仅为 `verification_only_camo`。
- 复核边界：Gate 1 已完成，当前 clean baseline 行为 `status=clean_prob_re_eval_complete`；后续只需随 release audit 继续复核 integrity。
- 复评入口：`/root/data-tmp/workspace/02_experiments/scripts/start_baseline_prob_eval_clean.sh`。

### Gate 1 clean baseline run

- 运行目录：`/root/data-tmp/workspace/02_experiments/runs/baseline_escnet_b5_clean_prob_e120`
- 当前状态：CAMO/COD10K/NC4K result files 已完成；baseline state 为 complete，baseline/resume watcher 不需要重复启动。
- CAMO result：S=.881, wF=.842, meanF=.864, meanE=.933, MAE=.043。
- COD10K result：S=.877, wF=.802, meanF=.824, meanE=.938, MAE=.021。
- NC4K result：S=.897, wF=.857, meanF=.878, meanE=.942, MAE=.029。
- 证据边界：这是 Gate 1 的完整 clean probability baseline evidence，可用于当前 Light-vs-ESCNet 同协议差值；历史 ESCNet-B5 reference 只保留为内部追溯证据。

### Metrics metadata gate

- `metrics_all.csv` 已包含 `protocol`、`repo_boundary`、`checkpoint` 和 `status` 字段。
- 新增评测必须通过 `collect_metrics.py` 或兼容脚本写入这些字段；字段为空的结果不得进入主结果表。
- B0 候选评估只能使用 `status=external_dirty_tree_observation_candidate`；即使完成三数据集评估，也先作为 Gate 4A observation/reference note，不能自动进入主表。
- MobileMamba-T2 候选评估同样只能使用 `status=external_dirty_tree_observation_candidate`；即使完成三数据集评估，也先作为 Gate 4B observation/reference note，不能自动进入主表。
- `aggregate_results.py` 默认显示 `Metric Status` 和 `Speed Status`；Gate 3 通过后已显示 idle same-command latency/FPS。
- `audit_paper_evidence.py` 已用于自动审计 `metrics_all.csv` 的入表边界；最新报告为 `04_paper/drafts/paper_evidence_audit_latest.md`，当前状态 pass，baseline historical rows 和 teacher CAMO row 均被识别为 reference/verification notes。
- `audit_claim_text.py` 已用于扫描 paper-facing deliverables 的越界主张；最新报告为 `04_paper/drafts/claim_text_audit_latest.md`，当前状态 pass。
- `generate_delta_summary.py` 已用于从 metrics/profile CSV 生成 `04_paper/drafts/current_delta_summary.md`；Gate 1 通过后自动切换 clean baseline，Gate 2 通过后自动补充 KD 对比。
- 定稿 readiness 矩阵：`04_paper/drafts/paper_submission_readiness.md`，用于把已可写结论、pending gate 和下一条闭环命令压缩到一页。
- Gate 回填 readiness 审计：`04_paper/drafts/gate_patch_readiness_latest.md`，用于判断 Gate 1/2/3/4A/4B 是安全 pending、可回填，还是半落盘不可写；同时检查 `paper_gate_patch_matrix.md` 是否覆盖外发稿 `paper_interim_submission.md` 及 share pack、presentation、submission packet、repro manifest 等配套材料。

### Light final run integrity

- 命令：`python 02_experiments/scripts/check_run_integrity.py --run_dir 02_experiments/runs/light_b2_c64_e120_s42_prob_eval_v2 --exp_id light_b2_c64_e120_s42_prob_eval_v2 --datasets CAMO,COD10K,NC4K`
- 状态：passed。
- 说明：该 eval run 是预测/GT 数量和 result.txt 完整性已通过的 final Light evidence。

### 结构效率与受控速度 profile

- 汇总表：`/root/data-tmp/workspace/02_experiments/tables/profiles.csv`
- Baseline profile：`/root/data-tmp/workspace/02_experiments/runs/profile_escnet_b5_416/profile.json`
- Light profile：`/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/profile_epoch120.json`
- Baseline idle profile：`/root/data-tmp/workspace/02_experiments/runs/profile_escnet_b5_416_idle/profile.json`
- Light idle profile：`/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/profile_epoch120_idle.json`
- KD idle profile：`/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu/profile_epoch120_idle.json`
- ESCNet-B5 C128：99.903M params, 129.022 GMACs, 381.169 MB model, 829.771 MB peak mem.
- Light-B2-C64：29.808M params, 36.391 GMACs, 113.743 MB model, 237.439 MB peak mem.
- 可写结论：参数量 -70.16%，GMACs -71.79%，模型大小 -70.16%，峰值显存 -71.38%。
- 受控速度：ESCNet-B5 73.01 ms / 13.70 FPS；Light-B2-C64 34.31 ms / 29.15 FPS；KD Light-B2-C64 34.84 ms / 28.71 FPS。
- 写作边界：latency/FPS 只能描述为 idle V100、416 输入、batch 1、warmup=50、repeat=100 的受控 profile；不要推广为真实边缘端部署表现。

## 图表资产

- 清洁版 interim 论文稿：`/root/data-tmp/workspace/04_paper/drafts/paper_interim_submission.md`
- 当前复现 manifest：`/root/data-tmp/workspace/04_paper/drafts/reproducibility_manifest.md`
- 老师/组内外发阅读包说明：`/root/data-tmp/workspace/04_paper/drafts/teacher_share_pack.md`
- 组会/答辩汇报提纲：`/root/data-tmp/workspace/04_paper/drafts/presentation_outline.md`
- 方法图：`/root/data-tmp/workspace/04_paper/figures/light_b2_c64_method.png`
- 精度-效率散点图：`/root/data-tmp/workspace/04_paper/figures/accuracy_efficiency_scatter.png`
- CAMO 四列对比：`/root/data-tmp/workspace/04_paper/figures/camo_visual_grid_b5_light_b2c64.png`
- CAMO case selection：`/root/data-tmp/workspace/04_paper/figures/camo_case_selection_b5_light.md`
- CAMO failure-case analysis：`/root/data-tmp/workspace/04_paper/drafts/camo_failure_case_analysis.md`
- 失败/接近/更优案例图：`camo_light_worse_cases.png`, `camo_light_close_cases.png`, `camo_light_better_cases.png`
- B0 工程观察趋势图：`/root/data-tmp/workspace/04_paper/figures/b0_cod10k_intermediate_trend.png`；仅作路线判断/附录候选证据，不进入主表、摘要或结论。

## Paper-Facing Draft Audits

- `paper_interim_submission.md` 是当前最适合外发阅读的诚实 interim 稿；`paper_draft.md` 保留更多证据边界说明，但已清理外发可见的内部路径和英文工程状态标签。
- `teacher_share_pack.md` 是当前最适合随稿发送的阅读说明，压缩了可讲结论、证据边界和后续证据项。
- `presentation_outline.md` 是当前组会/答辩用 slide 提纲，按 10-12 页组织当前证据和待完成证据项。
- `paper_claim_evidence_matrix.md` 是当前最细的主张到证据映射表；新增结果进入论文前应先补该矩阵。
- `citation_manifest.md` 是当前 18 条核心参考文献到论文用途、证据来源和 novelty 边界的映射表；改 Related Work、摘要、结论或参考文献前应先检查它。
- `audit_claim_text.py` 默认扫描论文草稿、清洁版 interim 稿、外发说明、展示提纲和结果表，最新状态 pass。
- `audit_interim_submission_numbers.py` 已核对清洁版论文中的 Light/ESCNet 指标、三数据集均值、profile 数字和结构降幅，最新状态 pass。
- `audit_paper_assets.py` 已核对论文草稿、清洁版 interim 稿、外发说明和展示提纲中的图像引用，最新状态 pass。
- `audit_claim_evidence_matrix.py` 已核对 `paper_claim_evidence_matrix.md` 中 accepted/reference/observation 主张引用的本地证据路径是否存在。
- `audit_gate_patch_readiness.py` 已核对 Gate 结果是否只处于 pending/ready/invalid 的安全状态，并检查 Gate 回填矩阵覆盖 `paper_interim_submission.md`、`paper_claim_evidence_matrix.md`、`teacher_share_pack.md`、`presentation_outline.md`、`paper_submission_packet.md` 和 `reproducibility_manifest.md`，最新状态 pass。
- `audit_literature_citations.py` 已核对 `01_literature` 四个调研文件、`citation_manifest.md`、两份论文稿参考文献列表、正文 inline citation 和 18 个核心 COD/轻量化/KD 文献覆盖，最新状态 pass。
- `audit_submission_protocol.py` 已加严 public-facing style 检查：`paper_draft.md`、`paper_interim_submission.md`、`teacher_share_pack.md` 和 `presentation_outline.md` 不得出现本地绝对路径、脚本清单、内部 CSV/status 字段、调度状态噪声或 `historical reference`、`probability eval complete`、`current main result` 等英文证据状态标签；详细复现信息统一留在 `reproducibility_manifest.md` 和内部证据文档。
- `audit_b0_status_consistency.py` 已检查 B0 dirty observation 在路线、handoff 和论文控制文档中的 checkpoint/result 状态是否过期，并防止把 Gate 4A observation 提升到主表；最新报告为 `04_paper/drafts/b0_status_consistency_audit_latest.md`。
- `audit_mobilemamba_status_consistency.py` 已检查 MobileMamba-T2 dirty observation 在路线、handoff 和论文控制文档中的最新 result 行、checkpoint absent/present 状态和 `external_dirty_tree_observation_only` 边界，并强制 Gate 4B observation 不进入主表、摘要或结论；最新报告为 `04_paper/drafts/mobilemamba_status_consistency_audit_latest.md`。
- `sync_mobilemamba_observation_state.py` 是 MobileMamba 新 COD10K 行或 checkpoint 出现后的只读同步入口；它刷新 `mobilemamba_t2_external_status_latest.md`、`orchestrator_tick_latest.md`、路线/交付控制文档和相关审计，最新报告为 `02_experiments/runs/mobilemamba_observation_sync_latest.md`。
- `audit_gpu_handoff_consistency.py` 已检查 tick、GPU_QUEUE、current_run_snapshot、resume_handoff、orchestrator_status、task_board、P0_gpu_queue_operator、P0_gate1_kd_handoff_card、DISPATCH_PACKETS 和 gate runbook 对 paused Gate 1 wrapper、resume watcher、KD watcher 与 MobileMamba observation boundary 的一致性，最新状态 pass。
- `audit_gpu_runtime_state.py` 已只读检查 live paused Gate 1 wrapper、resume watcher 目标 PID、KD watcher、MobileMamba 进程状态、watcher logs 和 premature KD launch 风险；最新报告为 `00_project/gpu_runtime_state_audit_latest.md`，当前状态 pass。
- `audit_route_decision_consistency.py` 已检查 `route_decision.md`、`finalization_gates.md`、readiness、evidence index 和 task board 与最新 tick 中的 Gate、B0、MobileMamba 状态一致；最新状态 pass。
- `audit_task_board_consistency.py` 已检查 `03_agent_tasks/task_board.md` 中的 prompt、pending、report、GPU queue、planned KD run 和验收路径是否存在且不使用过期短路径；最新报告为 `03_agent_tasks/task_board_consistency_audit_latest.md`，当前状态 pass。
- `audit_release_audit_registry.py` 已检查 `run_release_audits.sh` 的固定审计项、`RELEASE_AUDIT_REGISTRY.md`、最新 release report 命令和控制文档是否一致；最新报告为 `02_experiments/scripts/release_audit_registry_audit_latest.md`，当前状态 pass。
- `paper_delivery_manifest.md` 是当前论文交付包清单，列出外发文件、图表资产、内部证据、允许主张、withheld claims 和必跑命令；`audit_paper_delivery_manifest.py` 已检查清单中的路径、章节、核心数字和危险宣称边界，最新报告为 `04_paper/drafts/paper_delivery_manifest_audit_latest.md`。
- `goal_completion_matrix.md` 已将原始目标拆成已证明证据、pending gate、observation-only 分支和最终完成条件；它是判断目标是否真的完成的当前入口之一。
- 最新 `release_audit_latest.md` 为 pass；`submission_protocol_audit_latest.md` 显示 public-facing style 检查无错误、无警告。
- `audit_cv_report_alignment.py` 已核对 `CV开题报告.pdf` 抽取文本与当前 project profile、master plan、route decision、论文稿和汇报提纲的一致性，覆盖轻量主干、轻量融合、边界辅助、KD/量化、精度效率和可视化要求，最新状态 pass。
- 最新数字审计报告：`/root/data-tmp/workspace/04_paper/drafts/interim_submission_number_audit_latest.md`。
- 最新 Light final metadata 审计报告：`/root/data-tmp/workspace/04_paper/drafts/light_final_metadata_audit_latest.md`。
- 最新图像资产审计报告：`/root/data-tmp/workspace/04_paper/drafts/paper_asset_audit_latest.md`。
- 最新 CAMO 失败案例数字审计报告：`/root/data-tmp/workspace/04_paper/drafts/camo_failure_case_number_audit_latest.md`。
- 最新主张-证据矩阵审计报告：`/root/data-tmp/workspace/04_paper/drafts/claim_evidence_matrix_audit_latest.md`。
- 最新 Gate 回填 readiness 审计报告：`/root/data-tmp/workspace/04_paper/drafts/gate_patch_readiness_latest.md`。
- 最新 B0 状态一致性审计报告：`/root/data-tmp/workspace/04_paper/drafts/b0_status_consistency_audit_latest.md`。
- 最新 MobileMamba 状态一致性审计报告：`/root/data-tmp/workspace/04_paper/drafts/mobilemamba_status_consistency_audit_latest.md`。
- 最新 task board 一致性审计报告：`/root/data-tmp/workspace/03_agent_tasks/task_board_consistency_audit_latest.md`。
- 最新 GPU runtime 状态审计报告：`/root/data-tmp/workspace/00_project/gpu_runtime_state_audit_latest.md`。
- 最新 release audit registry 审计报告：`/root/data-tmp/workspace/02_experiments/scripts/release_audit_registry_audit_latest.md`。
- 最新 paper delivery manifest 审计报告：`/root/data-tmp/workspace/04_paper/drafts/paper_delivery_manifest_audit_latest.md`。
- 最新文献引用审计报告：`/root/data-tmp/workspace/04_paper/drafts/literature_citation_audit_latest.md`。
- 文献引用 manifest：`/root/data-tmp/workspace/04_paper/drafts/citation_manifest.md`。
- 最新开题报告对齐审计报告：`/root/data-tmp/workspace/04_paper/drafts/cv_report_alignment_audit_latest.md`。

## 已完成但需谨慎表述

### KD B2-C64

- 代码目录：`/root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64`
- run 目录：`/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42`
- final run 目录：`/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu`
- final checkpoint：`/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu/epoch_120.pth`
- final checkpoint sha256：`36f0680943279d77c038ee16f4e5a341dd4b9f61600d2a2d0bd579c13693c2ae`
- probability eval：`/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval`
- 只读状态报告：`/root/data-tmp/workspace/02_experiments/runs/kd_recovery_status_latest.md`
- 状态：online KD smoke 通过后，经 fast-shm 四卡路线完成 120 epoch；最终持久证据同步到 workspace，保留 epoch40/60/80/100/120 checkpoint。
- 指标：CAMO S=.863, wF=.818, meanF=.844, meanE=.920, MAE=.050；COD10K S=.864, wF=.782, meanF=.809, meanE=.929, MAE=.024；NC4K S=.885, wF=.838, meanF=.860, meanE=.932, MAE=.033。
- 与 no-KD 差异：三数据集平均 S -0.001，wF -0.001，meanF 约持平，meanE +0.001，MAE 约持平。
- 写作边界：可写作“在线输出级 KD 未带来稳定正向收益”的负结果分析；不能写 KD 提升、蒸馏有效或缩小差距。

## 仍为 observation only 的探索分支

### PVTv2-B0 极限压缩分支

- 外部目录：`/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0`
- 最新观察：COD10K 中间 eval 已落表到 epoch120。该分支在早期明显退化后逐步恢复；epoch120 最新完整行 S=.8004, wF=.6862, meanF=.7203, meanE=.8878, MAE=.0350。epoch100 是当前 B0 最好已落表中间行，S=.8014, wF=.6882, meanF=.7221, meanE=.8899, MAE=.0346，但仍低于已验收 Light-B2-C64 COD10K S=.866, wF=.782, meanF=.808, meanE=.928, MAE=.024。
- 中间结果文件：`/root/data-tmp/results_train/pvt_v2_b0/result.txt`
- 观察记录：`/root/data-tmp/workspace/02_experiments/runs/b0_external_observation.md`
- 趋势说明：`/root/data-tmp/workspace/02_experiments/runs/b0_intermediate_trend_note.md`
- 论文侧趋势图说明：`/root/data-tmp/workspace/04_paper/drafts/b0_cod10k_trend_note.md`
- 论文侧趋势图：`/root/data-tmp/workspace/04_paper/figures/b0_cod10k_intermediate_trend.png`
- B0 候选 checkpoint 验收入口：`/root/data-tmp/workspace/02_experiments/scripts/start_b0_candidate_eval.sh`
- checkpoint 状态：dirty B0 checkpoint 已包括 `epoch_120.pth`，epoch120 eval metrics 已落表；完整最新清单和 latest eval 状态委托 `/root/data-tmp/workspace/02_experiments/runs/b0_external_status_latest.md`。这些 raw checkpoint 仍不是可验收论文 checkpoint。
- 写作边界：只能作为高风险探索观察；没有完整 checkpoint 和三数据集评估前，不进入主表。

### MobileMamba-T2 替代轻量主干分支

- 外部目录：`/root/data-tmp/ESCNet/checkpoints/mobilemamba_t2`
- 只读状态报告：`/root/data-tmp/workspace/02_experiments/runs/mobilemamba_t2_external_status_latest.md`
- 只读 watcher 日志：`/root/data-tmp/workspace/02_experiments/runs/watch_external_mobilemamba_progress.log`
- 只读同步入口：`/root/data-tmp/workspace/02_experiments/scripts/sync_mobilemamba_observation_state.py`
- 最新同步报告：`/root/data-tmp/workspace/02_experiments/runs/mobilemamba_observation_sync_latest.md`
- 候选 checkpoint 验收入口：`/root/data-tmp/workspace/02_experiments/scripts/start_mobilemamba_candidate_eval.sh`
- 最新观察：外部 dirty `/root/ESCNet/all.sh` 产生过 `configs/mobilemamba_t2.yaml` 四卡 online KD 训练痕迹；当前未观察到运行，实时 epoch/iter 委托 `orchestrator_tick_latest.md` 和状态报告记录。
- 当前 checkpoint/result：checkpoint 仍 absent；MobileMamba latest/highest-S epoch50 COD10K 中间 eval 已落表，S=.7487、wF=.6019、meanF=.6482、meanE=.8477、MAE=.0465。
- 证据边界：这是 `external_dirty_tree_observation_only`，只能服务路线判断；没有独立 snapshot、checkpoint load/profile、CAMO/COD10K/NC4K probability eval 和 integrity gate 前，不进入主表、摘要或结论。

## 定稿前必须补齐

1. 将 Gate 2/3 结果补丁同步到所有论文交付材料。
2. 补丁后运行完整 release audit，并显式加入 KD probability eval integrity。
3. 若 B0 或 MobileMamba 产生最终候选 checkpoint，先做完整性检查和三数据集评估，再决定是否作为附录探索。
