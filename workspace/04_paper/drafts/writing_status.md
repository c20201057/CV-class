# Writing Status

更新时间：2026-06-14T15:31:36Z / 2026-06-14 23:31:36 CST

## 已可定稿的内容

- 研究背景：COD/COS 的弱边界、低对比、多尺度和部署需求。
- 相关工作结构：CAMO/COD10K/NC4K；经典 COD；边界/频域增强；轻量化 COD。
- 方法主线：基于 ESCNet 的 Light-ESCNet，使用 PVTv2-B2 + C64，保留边缘-语义协同。
- 评测协议：主表使用概率图，不使用 `test.py` 二值化输出。
- 效率证据：ESCNet-B5 C128 vs Light-ESCNet B2-C64 的结构 profile。
- Teacher checkpoint 决策：固定 `/root/data-tmp/epoch_120.pth`。
- Light-ESCNet B2-C64 no-KD 完整训练与三数据集概率图评测：CAMO S=.862/wF=.818/MAE=.051，COD10K S=.866/wF=.782/MAE=.024，NC4K S=.886/wF=.840/MAE=.033。
- 主精度判断：相对 clean ESCNet-B5 probability baseline，Light B2-C64 平均 S-measure 下降约 .014、平均 MAE 增加约 .005；历史 ESCNet-B5 参考行只保留为内部追溯证据。
- 论文草稿已完成 Gate 1/2/3 边界修订：不把 KD 写成提升，不把 B0/MobileMamba/消融写成已完成主结果，Related Work 已补入 2024-2026 轻量 COD 与 KD-COD 边界。
- Light-ESCNet B2-C64 方法说明已补强：论文草稿 3.2 已展开 encoder、64 通道投影、AETP 边缘分支、edge-guided decoder 和 B2/C64 两个压缩来源。
- Light-B2-C64 方法图与精度-效率散点图已生成，可用于论文方法与实验分析部分。
- `paper_draft.md` 已嵌入方法图、精度-效率散点图和 CAMO 可视化图，参考文献已从占位替换为已核验条目。
- 已新增清洁版 interim 论文稿 `paper_interim_submission.md`：该稿比 `paper_draft.md` 更适合直接给老师/组员阅读，保留已验收 Light 主线与 clean baseline 证据边界，弱化内部路径和 gate 流水账。
- `paper_draft.md` 与 `paper_interim_submission.md` 的当前证据边界已同步到 Gate 1 clean baseline、Gate 2 KD final eval、Gate 3 controlled speed、B0/MobileMamba observation-only 的状态；两份稿件都不把 KD 写成提升，也不把 B0/MobileMamba 或待补消融写成主结果。
- 已新增老师/组内外发阅读包说明 `teacher_share_pack.md`，用于随 `paper_interim_submission.md` 一起说明当前可讲结论、证据边界和后续 gate。
- 已新增组会/答辩汇报提纲 `presentation_outline.md`，用于把当前 Light-ESCNet 结果、证据边界和后续 gate 组织成 10-12 页汇报。
- 已新增 `evidence_index.md`，用于追溯论文关键数字、图表和待完成项。
- 已新增复现 manifest `reproducibility_manifest.md`，集中记录当前可复查的代码边界、checkpoint sha256、metrics/profile CSV、图表资产、审计命令和 pending gate。
- 已新增文献引用 manifest `citation_manifest.md`，把 18 条核心参考文献映射到论文用途、调研证据和 novelty 边界；后续改相关工作、摘要、结论或参考文献时必须先检查它。
- 已新增 CAMO 失败案例分析 `camo_failure_case_analysis.md`：250 个 CAMO 样本中 Light 相对 ESCNet-B5 reference 的平均 MAE delta 为 +0.008056，140 个样本 `abs(delta)<0.005`，36 个样本 `delta>=0.02`，主要失败类型包括强纹理低对比下的局部漏检、细长结构过扩张、背景高置信误检和多部件目标局部遗漏。
- Lagrange 已完成论文证据边界审查；主控已按意见收紧 baseline 协议、FPS、KD、消融和可视化表述，审查记录见 `05_reviews/paper_evidence_audit_20260613.md`。
- clean ESCNet-B5 baseline 源码边界已固化到 `/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean`，从 `/root/ESCNet` git HEAD `25c4387e4ea94c247d83a91a749e87b959483a4e` 导出；后续复评不直接依赖 dirty `/root/ESCNet` 工作树。
- clean ESCNet-B5 与 `/root/data-tmp/epoch_120.pth` 已完成 CPU strict 加载验证，missing=0、unexpected=0；Gate 1 复评已完成 CAMO/COD10K/NC4K，三行均为 `clean_prob_re_eval_complete`。
- `/root/ESCNet/checkpoints/escnet` 已归档为指向 data-tmp legacy 目录的 symlink；其中 2026-06-13 checkpoint 只能作为 legacy artifact，不能作为 teacher 或主 baseline。
- Epicurus baseline boundary audit 已采纳：主结果表已拆分为 Light 完整概率评测、clean ESCNet-B5 baseline、KD 负结果分析以及 B0/MobileMamba 工程观察；`metrics_all.csv` 已补充 `protocol`、`repo_boundary`、`checkpoint`、`status` 字段。
- `run_prob_eval_suite.sh`、`start_baseline_prob_eval_clean.sh` 和 `aggregate_results.py` 已同步证据边界：新增评测会写入 metadata，聚合表显示 `Metric Status` 和 `Speed Status`；当前 latency/FPS 只按 controlled idle V100 profile 条件写入。
- GPU 空闲后的权威队列已写入 `02_experiments/scripts/GPU_QUEUE.md`；Gate 1/2/3 已完成，当前不要重启 baseline wrapper、KD watcher 或 KD 训练。
- 定稿提交前的入表、证据和复现实验协议已写入 `04_paper/drafts/submission_protocol_checklist.md`，后续 Gate 1/2/3/4A/4B 结果回填必须按该清单和 gate patch 矩阵验收。
- 论文入表证据边界已新增自动审计脚本 `02_experiments/scripts/audit_paper_evidence.py`，用于检查 `metrics_all.csv` 的 metadata、final status 三数据集完整性和 B0/KD/baseline 边界；Lagrange 的 checklist 审查意见已采纳，新增了 CAMO-only 禁止拼接、B0 intermediate 禁入摘要/主表、KD partial checkpoint 禁入主表、dirty/legacy repo_boundary 禁作 final 等硬门禁。
- 论文交付文本越界扫描已新增 `04_paper/scripts/audit_claim_text.py`，默认扫描 `paper_draft.md`、`paper_interim_submission.md`、`teacher_share_pack.md`、`presentation_outline.md`、`paper_outline.md` 和结果表，避免把 gate 文档里的禁令本身误报。
- 已新增清洁版论文数字一致性审计 `04_paper/scripts/audit_interim_submission_numbers.py`，核对 `paper_interim_submission.md` 中的核心指标、均值、profile 数字和降幅是否来自 CSV。
- 已新增 Light final metadata 审计 `02_experiments/scripts/audit_light_final_metadata.py`，核对 Light 主 run 的 metadata、checkpoint sha256、最终 loss、eval integrity、metrics status 和 profile row 一致性。
- 已新增论文图像资产审计 `04_paper/scripts/audit_paper_assets.py`，检查 `paper_draft.md`、`paper_interim_submission.md`、`teacher_share_pack.md` 和 `presentation_outline.md` 中的 Markdown 图像引用是否存在且非空。
- 已新增 CAMO 失败案例数字审计 `04_paper/scripts/audit_camo_failure_case_numbers.py`，从 `camo_case_selection_b5_light.csv` 重新计算 per-image MAE 统计，并检查论文稿、interim 稿、汇报提纲和失败案例说明中的关键数字。
- 已新增逐条主张-证据矩阵 `04_paper/drafts/paper_claim_evidence_matrix.md` 与路径审计 `04_paper/scripts/audit_claim_evidence_matrix.py`，用于在 Gate 1/2/3/4A/4B 结果回填前后验证每个论文主张都有本地证据。
- 已强化 Gate 回填矩阵、`paper_final_patch_plan.md` 和 `audit_gate_patch_readiness.py`：Gate 1/2/3/4A/4B 结果回填必须覆盖 `paper_interim_submission.md`、`paper_claim_evidence_matrix.md`、`teacher_share_pack.md`、`presentation_outline.md`、`paper_submission_packet.md` 和 `reproducibility_manifest.md`，防止只更新内部工作稿而外发材料过期。
- 已强化 `audit_submission_protocol.py` 的 public-facing style 检查：四份外发材料禁止本地绝对路径、脚本清单、内部 CSV/status 字段和调度状态噪声；`paper_draft.md` 的复现细节已改为论文式描述，详细命令和路径由 `reproducibility_manifest.md` 承担。
- 已完成外发材料证据状态中文化：`paper_interim_submission.md`、`paper_draft.md`、`teacher_share_pack.md` 和 `presentation_outline.md` 不再使用 `historical reference`、`probability eval complete`、`current main result` 等英文工程状态标签；`audit_submission_protocol.py` 已新增规则防止这些标签回流。
- 已新增 subagent prompt 准则审计 `03_agent_tasks/prompts/audit_prompt_principles.py`，并接入 release audit，确保所有 prompt/pending 任务显式包含“不偷懒、不因为怕风险而保守”。
- 已新增 GPU 接力一致性审计 `02_experiments/scripts/audit_gpu_handoff_consistency.py`，检查 orchestrator tick、GPU_QUEUE、handoff、task_board、短卡片和 dispatch packet 对 Gate 1/KD 接力规则的一致性，防止重复启动 baseline wrapper、跳过 KD 或把 B0/MobileMamba 误升主结果；已接入 release audit。
- 已新增 GPU runtime 状态审计 `02_experiments/scripts/audit_gpu_runtime_state.py`，只读检查 live paused Gate 1 wrapper、resume watcher 目标 PID、KD watcher、MobileMamba 进程状态、watcher logs 和 premature KD launch 风险；已接入 release audit，并在 agent acceptance ledger A23 中验收。
- 已新增路线判断一致性审计 `02_experiments/scripts/audit_route_decision_consistency.py`，检查 `route_decision.md`、`finalization_gates.md`、readiness、evidence index 和 task board 是否与最新 tick 中的 B0/MobileMamba/Gate 状态一致，防止旧中间结果继续影响路线判断；已接入 release audit。
- 已新增 task board 一致性审计 `03_agent_tasks/audit_task_board_consistency.py`，检查 `03_agent_tasks/task_board.md` 中的 prompt、pending、report、GPU queue、planned KD run 和验收路径是否存在且没有过期短路径；已接入 release audit，并在 agent acceptance ledger A22 中验收。
- 已新增 release audit registry `02_experiments/scripts/RELEASE_AUDIT_REGISTRY.md` 与 `02_experiments/scripts/audit_release_audit_registry.py`，检查固定 release gates、latest release report 命令、报告路径和控制文档是否一致；已接入 release audit，并在 agent acceptance ledger A24 中验收。
- 已新增论文交付清单 `04_paper/drafts/paper_delivery_manifest.md` 与 `04_paper/scripts/audit_paper_delivery_manifest.py`，把外发稿件、核心图表、内部证据、允许主张、withheld claims 和必跑命令纳入机器验收；已接入 release audit，并在 agent acceptance ledger A25 中验收。
- 已新增外部分支状态一致性审计 `02_experiments/scripts/audit_b0_status_consistency.py` 与 `02_experiments/scripts/audit_mobilemamba_status_consistency.py`，分别检查 B0 和 MobileMamba-T2 dirty observation 的 checkpoint/result 状态、observation-only 边界，并强制这些 observation 不进入主表、摘要或结论；两者均已接入 release audit。
- 已新增 MobileMamba-T2 只读同步入口 `02_experiments/scripts/sync_mobilemamba_observation_state.py`，在新 COD10K 中间行或 checkpoint 出现后自动刷新状态、tick、路线/交付控制文档和相关审计；该入口不启动、不停止、不 signal 训练。
- 已新增目标完成度矩阵 `00_project/goal_completion_matrix.md`，将用户原始目标拆成已证明、pending gate、observation-only 和最终完成条件，避免把 interim 论文状态误判为完整目标完成；已纳入路线一致性审计。
- 当前自动验收状态：Gate 2/3 结果正在回填到论文和控制文档；完整 `release_audit_latest.md` 需要在本轮文档更新后复跑，并额外纳入 KD probability eval integrity。`audit_paper_evidence.py`、`audit_claim_text.py`、`audit_interim_submission_numbers.py`、`audit_paper_assets.py`、`audit_claim_evidence_matrix.py`、`audit_literature_citations.py`、`audit_submission_protocol.py`、`audit_prompt_principles.py`、`audit_b0_status_consistency.py`、`audit_mobilemamba_status_consistency.py`、`audit_route_decision_consistency.py`、`audit_release_audit_registry.py`、Light final probability eval run 和 KD probability eval run 的 `check_run_integrity.py` 均应保持 pass。
- 文献引用验收已扩展为检查 `citation_manifest.md`、两份论文稿参考文献、正文 inline citation 和 18 个核心 COD/轻量化/KD 文献覆盖；最新报告为 `literature_citation_audit_latest.md`。

## 定稿前仍需处理

- 本轮 Gate 2/3 回填后的完整 release audit。
- B2-C64 是否是最佳精度-效率折中仍需更多消融支持；当前论文只声称它是已验收主力轻量模型。
- 边界监督对轻量模型是否有实证增益。
- COD10K/NC4K 的 per-image 失败案例类型与可视化分析；当前只有 CAMO reference visual analysis 可写。
- online KD full train/eval 已完成，但未带来稳定正向收益；定稿时只能作为负结果和训练成本分析。
- B0 极限压缩分支当前只作为外部高风险观察；没有 checkpoint load/profile、三数据集评估和完整性检查前，不纳入论文结果。
- 外部 B0 分支已完成 epoch 10、epoch 20、epoch 30、epoch 40、epoch 50、epoch 60、epoch 70、epoch 80、epoch 90、epoch 100、epoch 110 和 epoch 120 COD10K 中间 eval；最新 eval/checkpoint 状态以 `b0_external_status_latest.md` 为准。epoch120 最新完整行为 S=.8004、wF=.6862、meanF=.7203、meanE=.8878、MAE=.0350。epoch100 是当前 B0 最好已落表行，S=.8014、wF=.6882、meanF=.7221、meanE=.8899、MAE=.0346，但仍显著低于已验收 Light-B2-C64 COD10K。尚未完成 checkpoint 验证、profile、三数据集评估和完整性检查。观察记录见 `02_experiments/runs/b0_external_observation.md`，继续观察，不抢占 GPU。
- 外部 MobileMamba-T2 替代主干分支当前未观察到运行；实时 epoch/iter 以 `orchestrator_tick_latest.md` 和 `mobilemamba_t2_external_status_latest.md` 为准，checkpoint 仍 absent；最新且最高 S 的 epoch50 COD10K 中间 eval 已落表，S=.7487、wF=.6019、meanF=.6482、meanE=.8477、MAE=.0465。它的证据边界为 `external_dirty_tree_observation_only`，只能作为 Gate 4B observation candidate，不能进入主表、摘要或结论。
- Gate 1 baseline、Gate 2 KD 和 Gate 3 controlled speed 均已完成；下一步是完成文档回填、刷新汇总和 release audit，不重启 KD watcher。

## 当前图表资产

- 主结果模板：`/root/data-tmp/workspace/04_paper/tables/main_results_template.md`
- 聚合表：`/root/data-tmp/workspace/04_paper/tables/aggregated_results.md`
- 清洁版 interim 论文稿：`/root/data-tmp/workspace/04_paper/drafts/paper_interim_submission.md`
- 老师/组内外发阅读包说明：`/root/data-tmp/workspace/04_paper/drafts/teacher_share_pack.md`
- 组会/答辩汇报提纲：`/root/data-tmp/workspace/04_paper/drafts/presentation_outline.md`
- 可视化 smoke：`/root/data-tmp/workspace/04_paper/tables/visual_grid_smoke_camo_b5.png`
- CAMO 可视化四列图：`/root/data-tmp/workspace/04_paper/figures/camo_visual_grid_b5_light_b2c64.png`
- CAMO 证据选例：`/root/data-tmp/workspace/04_paper/figures/camo_case_selection_b5_light.md`
- CAMO 失败案例分析：`/root/data-tmp/workspace/04_paper/drafts/camo_failure_case_analysis.md`
- CAMO Light 失败/接近/更优案例图：`camo_light_worse_cases.png`、`camo_light_close_cases.png`、`camo_light_better_cases.png`
- Light-B2-C64 方法图：`/root/data-tmp/workspace/04_paper/figures/light_b2_c64_method.png`
- 精度-效率散点图：`/root/data-tmp/workspace/04_paper/figures/accuracy_efficiency_scatter.png`
- 方法图/散点图脚本：`/root/data-tmp/workspace/04_paper/scripts/draw_light_b2_c64_figures.py`
- 训练 loss：`/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/train_loss.md`
- Light no-KD 评测 run：`/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42_prob_eval_v2`
- Light no-KD 入表来源：`/root/data-tmp/workspace/02_experiments/tables/metrics_all.csv`
- KD 中断分析：`/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/kd_interruption_analysis.md`
- GPU 队列：`/root/data-tmp/workspace/02_experiments/scripts/GPU_QUEUE.md`
- Light-B2-C64 方法讲解：`/root/data-tmp/workspace/04_paper/drafts/method_light_b2_c64.md`
- 论文证据索引：`/root/data-tmp/workspace/04_paper/drafts/evidence_index.md`
- 定稿 gate：`/root/data-tmp/workspace/04_paper/drafts/finalization_gates.md`
- 主张-证据自查：`/root/data-tmp/workspace/04_paper/drafts/claim_evidence_audit.md`
- Gate 结果回填计划：`/root/data-tmp/workspace/04_paper/drafts/paper_final_patch_plan.md`
- 定稿提交协议：`/root/data-tmp/workspace/04_paper/drafts/submission_protocol_checklist.md`
- 定稿 readiness 矩阵：`/root/data-tmp/workspace/04_paper/drafts/paper_submission_readiness.md`
- 最新自动证据审计报告：`/root/data-tmp/workspace/04_paper/drafts/paper_evidence_audit_latest.md`
- 最新交付文本审计报告：`/root/data-tmp/workspace/04_paper/drafts/claim_text_audit_latest.md`
- 最新清洁版论文数字审计报告：`/root/data-tmp/workspace/04_paper/drafts/interim_submission_number_audit_latest.md`
- 最新 Light final metadata 审计报告：`/root/data-tmp/workspace/04_paper/drafts/light_final_metadata_audit_latest.md`
- 最新论文图像资产审计报告：`/root/data-tmp/workspace/04_paper/drafts/paper_asset_audit_latest.md`
- 最新 CAMO 失败案例数字审计报告：`/root/data-tmp/workspace/04_paper/drafts/camo_failure_case_number_audit_latest.md`
- 主张-证据矩阵：`/root/data-tmp/workspace/04_paper/drafts/paper_claim_evidence_matrix.md`
- 复现 manifest：`/root/data-tmp/workspace/04_paper/drafts/reproducibility_manifest.md`
- 文献引用 manifest：`/root/data-tmp/workspace/04_paper/drafts/citation_manifest.md`
- 最新主张-证据矩阵审计报告：`/root/data-tmp/workspace/04_paper/drafts/claim_evidence_matrix_audit_latest.md`
- 最新 Gate 回填 readiness 审计报告：`/root/data-tmp/workspace/04_paper/drafts/gate_patch_readiness_latest.md`
- 最新 B0 状态一致性审计报告：`/root/data-tmp/workspace/04_paper/drafts/b0_status_consistency_audit_latest.md`
- 最新 MobileMamba 状态一致性审计报告：`/root/data-tmp/workspace/04_paper/drafts/mobilemamba_status_consistency_audit_latest.md`
- 最新 MobileMamba observation sync 报告：`/root/data-tmp/workspace/02_experiments/runs/mobilemamba_observation_sync_latest.md`
- 最新 prompt 准则审计报告：`/root/data-tmp/workspace/03_agent_tasks/prompts/prompt_principles_audit_latest.md`
- 最新 task board 一致性审计报告：`/root/data-tmp/workspace/03_agent_tasks/task_board_consistency_audit_latest.md`
- 最新 GPU runtime 状态审计报告：`/root/data-tmp/workspace/00_project/gpu_runtime_state_audit_latest.md`
- 最新 release audit registry 审计报告：`/root/data-tmp/workspace/02_experiments/scripts/release_audit_registry_audit_latest.md`
- 论文交付清单：`/root/data-tmp/workspace/04_paper/drafts/paper_delivery_manifest.md`
- 最新 paper delivery manifest 审计报告：`/root/data-tmp/workspace/04_paper/drafts/paper_delivery_manifest_audit_latest.md`
- 目标完成度矩阵：`/root/data-tmp/workspace/00_project/goal_completion_matrix.md`

## 定稿前检查

1. 主结果表只使用概率图评测行。
2. 所有数值能追溯到 `metrics_all.csv`、`profiles.csv`、run config 和日志。
3. 摘要和结论不得包含还没有实验证据的提升或保持精度表述。
4. 若 KD 失败，必须写失败分析，而不是删除 KD 叙事。
5. 2026 年公开信息不足的工作只放趋势或未来工作。
6. ESCNet-B5 三数据集行在固定基线复评前必须标记为历史参考行。
7. 定稿前逐项通过 `finalization_gates.md`；未通过 gate 的内容不得写入主结论。
8. 每次改摘要、实验和结论后，用 `claim_evidence_audit.md` 检查主张是否仍有证据支撑。
9. Gate 1/2/3/4A/4B 任一完成后，先按 `paper_final_patch_plan.md` 判断执行顺序，再按 `paper_gate_patch_matrix.md` 更新正文、表格、外发材料和证据文档。
10. 定稿前按 `submission_protocol_checklist.md` 做一次逐项验收；任何未通过项必须在正文中降级为历史参考、待验证或失败分析。
11. 每次更新 `metrics_all.csv` 后运行 `audit_paper_evidence.py`，确保新结果没有越过 evidence status 边界。
12. 每次更新摘要、实验、结论或结果表后运行 `audit_claim_text.py`，确保交付文本没有 SOTA、KD 提升、最终速度提升等越界主张。
