# Paper Gate Patch Matrix

更新时间：2026-06-14T02:48:00Z / 2026-06-14 10:48:00 CST

本矩阵把 Gate 1/2/3 结果回来后的论文收束动作拆成具体文件、章节和验收项。它不替代 `finalization_gates.md`；它用于防止结果落盘后漏改摘要、表格、图或证据索引。

外部复核：Feynman 已复核本矩阵，报告见
`/root/data-tmp/workspace/05_reviews/paper_gate_patch_matrix_review_feynman.md`。
其关键意见已吸收：Gate 1/2/3 回来后必须同步更新结论段、`evidence_index.md`、
`aggregated_results.md` coverage/notes、readiness/audit 产物；KD 不改善时必须落到
失败分析而非正向贡献；Gate 3 允许 KD 未完成时只完成 baseline/Light 的 controlled
speed，并把 KD speed 明确标为 absent。

外发稿同步要求：`paper_interim_submission.md` 是当前推荐给老师/组员阅读的正文稿，
因此 Gate 1/2/3/4A/4B 任一结果通过后，不能只更新 `paper_draft.md`。必须同步检查
`paper_interim_submission.md`、`paper_claim_evidence_matrix.md`、`teacher_share_pack.md`、
`presentation_outline.md`、`paper_submission_packet.md` 和 `reproducibility_manifest.md`；
若不适用，也要在对应文件中保持明确的 pending、observation 或 absent 边界。
外部分支 Gate 4A/4B 回填还必须同步 `agent_acceptance_ledger.md`，并重跑
`audit_b0_status_consistency.py` 或 `audit_mobilemamba_status_consistency.py`，确保
dirty-tree observation 不会从实验日志滑入主表、摘要或结论。

## Gate 1: Clean ESCNet-B5 Probability Baseline

Gate 1 回填核心口径：`clean ESCNet-B5 probability baseline`。只有完整三数据集
probability eval、integrity 和 metadata 都通过后，才能从 historical reference 升级。

触发条件：

- `baseline_escnet_b5_clean_prob_e120` 在 CAMO、COD10K、NC4K 上完成概率图评测。
- `check_run_integrity.py` 通过。
- `metrics_all.csv` 三行均为 `status=clean_prob_re_eval_complete`，且 `protocol=prob_map`、`repo_boundary=baseline_escnet_clean` 或等价 clean 标记。

必须更新：

| File | Location | Patch |
| --- | --- | --- |
| `04_paper/drafts/paper_draft.md` | 摘要 | 将“历史 ESCNet-B5 参考行”改为“clean ESCNet-B5 probability baseline”，删除“仍需等待 clean 复评确认”。 |
| `04_paper/drafts/paper_draft.md` | 3.1 | 保留 clean snapshot 和 strict load 描述；补充三数据集 clean probability eval 已完成。 |
| `04_paper/drafts/paper_draft.md` | 4.1 | 删除“ESCNet-B5 当前只作为历史三数据集参考行和 CAMO checkpoint 复核证据，完整 clean snapshot 三数据集复评待补齐”之类旧口径；改为 ESCNet-B5 与 Light 均按统一概率图协议评测。 |
| `04_paper/drafts/paper_draft.md` | 4.3 | 将 CAMO-only verification 降级为核验过程，新增 clean 三数据集评测结果。 |
| `04_paper/drafts/paper_draft.md` | 4.4 | 主表 ESCNet-B5 行替换为 clean probability baseline；重新计算 Light-vs-baseline 平均 delta。 |
| `04_paper/drafts/paper_draft.md` | 4.5/图 2 | 若 scatter 使用三数据集平均 S，重新生成 `accuracy_efficiency_scatter.png`；正文和图注都要说明 ESCNet-B5 点来自 clean probability baseline，不再写“最终位置待确认”。 |
| `04_paper/drafts/paper_draft.md` | 5 结论 | 删除 baseline pending 语句；把差值改为 clean same-protocol 差值。 |
| `04_paper/drafts/paper_interim_submission.md` | 摘要/4.x/结论/参考脚注 | 与工作稿同步升级 clean baseline 口径；外发稿不得继续保留 historical reference delta 或 pending clean baseline 旧句。 |
| `04_paper/tables/main_results_template.md` | Table 1A/1B | 将 ESCNet-B5 clean 行移入 completed probability-protocol table；historical row 保留到 reference note。 |
| `04_paper/tables/aggregated_results.md` | Main Compact Table/notes/coverage | 运行 `aggregate_results.py`；明确是否用 `baseline_escnet_b5_clean_prob_e120` 替换 historical exp_id，更新脚注说明和 Metric Coverage，避免 clean 与 historical 两行混作主表。 |
| `04_paper/drafts/evidence_index.md` | 参考证据与待确认 baseline | 将 Gate 1 证据从待确认移到已可支撑主结论，保留历史结果来源说明。 |
| `04_paper/drafts/claim_evidence_audit.md` | Interim/Accepted | 将 Light-vs-ESCNet delta 从 `interim/reference only` 移到 `accepted`。 |
| `04_paper/drafts/paper_claim_evidence_matrix.md` | baseline/delta claims | 将 clean baseline、same-protocol delta 和 historical row boundary 分开列证据；不得让 historical 和 clean 两种口径共用一个 accepted claim。 |
| `04_paper/drafts/teacher_share_pack.md` | 可讲结论/边界 | 将分享包中的 baseline 口径同步为 clean same-protocol；若数值变化，更新老师可讲版 delta。 |
| `04_paper/drafts/presentation_outline.md` | 主结果页/结论页 | 将组会/答辩 slide 提纲同步为 clean baseline；图表页和结论页不能残留 Gate 1 pending。 |
| `04_paper/drafts/paper_evidence_audit_latest.md` | 全文 | 通过 `run_release_audits.sh --add-integrity ...` 重新生成，确认 clean baseline final metadata 合法。 |
| `04_paper/drafts/claim_text_audit_latest.md` | 全文 | 通过 release audit 重新生成，确认摘要/实验/结论不再残留 pending clean baseline 或越界主张。 |
| `04_paper/drafts/paper_submission_readiness.md` | Evidence Matrix | 将 clean baseline 行从 pending 改为 pass，并更新 Current Verdict。 |
| `04_paper/drafts/current_delta_summary.md` | 全文 | 重新运行 `generate_delta_summary.py`，用新的 clean baseline delta 替换摘要和 4.4 数字。 |
| `04_paper/drafts/paper_submission_packet.md` | Current Accepted Claims/Forbidden Claims | 将 clean baseline 从 forbidden/pending 移到 accepted evidence；保留 Gate 2/3/4 的禁止主张。 |
| `04_paper/drafts/reproducibility_manifest.md` | Metrics Evidence/Pending Gates | 写入 clean baseline prob eval run、checkpoint、integrity 和 metrics metadata；Gate 1 从 pending 移出。 |

Gate 1 后必须全文检索并处理这些旧口径：

```text
历史
参考行
0.009
0.006
0.027
clean
待确认
pending
```

验收命令：

```bash
python /root/data-tmp/workspace/02_experiments/scripts/aggregate_results.py \
  --out_md /root/data-tmp/workspace/04_paper/tables/aggregated_results.md
python /root/data-tmp/workspace/04_paper/scripts/generate_delta_summary.py
bash /root/data-tmp/workspace/02_experiments/scripts/run_release_audits.sh \
  --add-integrity /root/data-tmp/workspace/02_experiments/runs/baseline_escnet_b5_clean_prob_e120 \
  baseline_escnet_b5_clean_prob_e120 CAMO,COD10K,NC4K
```

## Gate 2: KD B2-C64 Final Result

触发条件：

- KD recovery 产生完整 checkpoint。
- KD 完成 CAMO、COD10K、NC4K 概率图评测。
- `check_run_integrity.py` 通过。
- `metrics_all.csv` KD 三行均为 `status=final_main_kd`。

必须更新：

| File | Location | Patch |
| --- | --- | --- |
| `04_paper/drafts/paper_draft.md` | 摘要 | 如果 KD 改善 Light，则写“KD 进一步改善/缩小差距”；若无改善，则写“KD 未稳定追回差距”并给原因，不得强行正向表述。 |
| `04_paper/drafts/paper_draft.md` | 引言贡献点 | 将“用于检验/后续验证 KD 潜力”改为真实结论：已验证改善、未改善但有分析，或不稳定失败。 |
| `04_paper/drafts/paper_draft.md` | 2.4 | 将 KD 定位从 pending 技术路线改为本文实际 KD 设置与结果边界；不能把未改善结果写成贡献。 |
| `04_paper/drafts/paper_draft.md` | 3.3 | 将 KD 从“后续/待验证”改为完整训练设置，写明 teacher、student、loss、lambda、resume 和 checkpoint。 |
| `04_paper/drafts/paper_draft.md` | 4.4 | 加入 KD 行或新增 KD comparison table；同时给出 KD-vs-noKD、KD-vs-clean baseline delta。 |
| `04_paper/drafts/paper_draft.md` | 4.6 | 将 KD 从消融计划移到已完成消融；若失败，改成“KD 补偿实验与负结果分析”，讨论 output-level MSE、teacher/student 容量差距、训练恢复和 CAMO 边界误差等可能原因。 |
| `04_paper/drafts/paper_draft.md` | 4.7 | 更新运行状态，删除“只能描述为工程状态”的旧句。 |
| `04_paper/drafts/paper_draft.md` | 4.8 | 若 KD predictions 已生成，重做可视化图并增加 KD 列；若未做图，不把 KD 写进可视化结论。若沿用 CAMO 样本选择，说明 KD 只增加预测列，不改变样本选择原则。 |
| `04_paper/drafts/paper_draft.md` | 5 结论 | 只按真实结果写 KD：提升、无提升或不稳定三种分支不能混淆。 |
| `04_paper/drafts/paper_interim_submission.md` | 摘要/方法/实验/结论 | 与工作稿同步 KD 真实结果；如果 KD 不改善，外发稿也必须写负结果或移出主贡献，不得只在工作稿中降级。 |
| `04_paper/tables/main_results_template.md` | Table 1A/1C/Table 3 | KD 从 pending 移到 completed 或 failure table；消融计划状态更新。 |
| `04_paper/tables/aggregated_results.md` | Main Compact Table/coverage/profile notes | 刷新 KD 行、`Metric Status=final_main_kd`、三数据集 coverage 和 checkpoint/status metadata。若 KD 结构同 B2-C64 而 profile 复用，也要标明来源，不能留 TBD。 |
| `04_paper/drafts/evidence_index.md` | KD B2-C64/图表资产 | 将 checkpoint、prob eval、integrity、delta、profile 来源和可视化图路径写入。 |
| `04_paper/drafts/claim_evidence_audit.md` | Pending/Accepted | 根据真实结果把 KD claim 标为 accepted 或 failure-analysis accepted。 |
| `04_paper/drafts/paper_claim_evidence_matrix.md` | KD claim | 根据 KD-vs-noKD 与 KD-vs-baseline 数字，将 claim 标为 accepted、failure-analysis accepted 或继续 pending；不能只写“KD 提升”。 |
| `04_paper/drafts/teacher_share_pack.md` | 可讲结论/风险边界 | 若 KD 改善，写具体提升；若 KD 不改善，写负结果和原因假设；若不稳定，写不能入主表。 |
| `04_paper/drafts/presentation_outline.md` | KD/消融页 | 增加 KD 结果或负结果页；结论页必须与真实结果一致。 |
| `04_paper/drafts/paper_evidence_audit_latest.md` | 全文 | 通过 release audit 加入 KD integrity 后重新生成，确认 KD final metadata 合法。 |
| `04_paper/drafts/claim_text_audit_latest.md` | 全文 | 重新生成，确认没有在 KD 无改善时写成改善。 |
| `04_paper/drafts/paper_submission_readiness.md` | Evidence Matrix | 将 KD training/eval 行改为 pass 或 failed-but-documented，并更新 Current Verdict。 |
| `04_paper/drafts/current_delta_summary.md` | 新增 KD comparison | 重新运行生成器；若脚本尚未输出 KD delta，手动补入后再扩展脚本。 |
| `04_paper/drafts/paper_submission_packet.md` | Accepted/Forbidden Claims | 只在 KD 通过 Gate 2 后改写 KD 状态；KD 不改善时从 forbidden 转为 failure-analysis boundary，不得转为正向贡献。 |
| `04_paper/drafts/reproducibility_manifest.md` | KD evidence | 写入 KD checkpoint、sha256、prob eval run、integrity、metrics status 和复查命令。 |

验收命令：

```bash
python /root/data-tmp/workspace/02_experiments/scripts/check_run_integrity.py \
  --run_dir /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_recover_b2w0_4gpu_prob_eval \
  --exp_id kd_light_b2_c64_e120_s42_recover_b2w0_4gpu_prob_eval \
  --datasets CAMO,COD10K,NC4K
python /root/data-tmp/workspace/04_paper/scripts/generate_delta_summary.py
bash /root/data-tmp/workspace/02_experiments/scripts/run_release_audits.sh \
  --add-integrity /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_recover_b2w0_4gpu_prob_eval \
  kd_light_b2_c64_e120_s42_recover_b2w0_4gpu_prob_eval CAMO,COD10K,NC4K
```

## Gate 3: Controlled Speed Retest

Gate 3 回填核心口径：`controlled speed`。速度只在 idle GPU、同一命令、同一
warmup/repeat/input size 条件下成立；否则继续只写结构复杂度。

触发条件：

- baseline、Light、KD 或 available subset 在空闲 GPU 上使用同一 `profile_model.py` 参数完成 profiling。
- profile JSON 写入独立 idle run 目录。
- `profiles.csv` 包含 idle profile rows。

必须更新：

| File | Location | Patch |
| --- | --- | --- |
| `04_paper/drafts/paper_draft.md` | 摘要 | 只有同条件结果显示更快时才写 latency/FPS 改善；否则只写结构复杂度下降。 |
| `04_paper/drafts/paper_draft.md` | 4.2 | 补充 speed profile 的 warmup、repeat、device、batch size 和空闲条件。 |
| `04_paper/drafts/paper_draft.md` | 4.5 | 新增 latency/FPS 表格列或单独速度表；注明是否包含 KD。 |
| `04_paper/drafts/paper_draft.md` | 4.7/5 结论 | 删除“速度复测待完成”旧句；如果 KD 未完成，只写 baseline/Light controlled speed，不暗示 KD speed 已完成。 |
| `04_paper/drafts/paper_interim_submission.md` | 摘要/实验/结论 | 与工作稿同步 controlled speed 数字；若速度没有改善，外发稿只保留结构效率，不写 speedup。 |
| `04_paper/tables/main_results_template.md` | Table 2 | 将 Latency/FPS 从禁用状态移动到 final speed table。 |
| `04_paper/tables/aggregated_results.md` | Main Compact Table/notes | 将 `Speed Status` 从 pending 改为 final idle profile 或 explicit absent。若 KD checkpoint 不存在，KD 行写 `not available: no final checkpoint`，不要让 Gate 3 卡死在 KD 上。 |
| `04_paper/drafts/evidence_index.md` | Controlled speed profile | 添加 baseline/Light/KD 或 available subset 的 profile JSON、同一命令、空闲 GPU 检查依据、latency/FPS 数字和可写边界。 |
| `04_paper/drafts/claim_evidence_audit.md` | Pending/Accepted | 将 speed claim 改为 accepted，或说明速度结果不支持“更快”主张。 |
| `04_paper/drafts/paper_claim_evidence_matrix.md` | speed/efficiency claim | 将结构效率和 controlled speed 拆成两个 claim；若速度未改善，speed claim 不能标 accepted positive。 |
| `04_paper/drafts/paper_evidence_audit_latest.md` | 全文 | 重新生成，确认 speed/profile metadata 与表格一致。 |
| `04_paper/drafts/claim_text_audit_latest.md` | 全文 | 重新生成，确认没有在速度未改善时写成 speedup。 |
| `04_paper/drafts/paper_submission_readiness.md` | Evidence Matrix | 将 Latency/FPS 行改为 pass 或 explicit withheld。 |
| `04_paper/drafts/paper_submission_packet.md` | Current Accepted Claims | 只有 controlled speed 支持时才写 latency/FPS；否则继续写结构指标。 |
| `04_paper/drafts/reproducibility_manifest.md` | Profile Evidence | 写入 idle profile JSON、命令、device、warmup/repeat 和 Speed Status。 |
| `04_paper/drafts/teacher_share_pack.md` | 可讲结论 | 将“速度待测”改为 controlled speed 数字或 explicit withheld。 |
| `04_paper/drafts/presentation_outline.md` | 效率页 | 更新速度表/脚注；若 KD speed absent，直接标 absent，不推断。 |

Gate 3 可接受的分支：

- KD 已完成：baseline、Light、KD 同条件 profile 全部入表。
- KD 未完成：baseline 与 Light 可完成 controlled speed；KD speed 明确写 absent/no final checkpoint，不阻塞 baseline-vs-Light 速度证据。
- 若同条件结果没有更快：报告 latency/FPS 数字，但摘要和结论不写速度提升。

验收命令：

```bash
python /root/data-tmp/workspace/02_experiments/scripts/aggregate_results.py \
  --out_md /root/data-tmp/workspace/04_paper/tables/aggregated_results.md
python /root/data-tmp/workspace/04_paper/scripts/generate_delta_summary.py
bash /root/data-tmp/workspace/02_experiments/scripts/run_release_audits.sh
```

## Gate 4A: B0 Observation Candidate

触发条件：

- 外部 B0 训练结束或出现主控指定 checkpoint 后，`start_b0_candidate_eval.sh` 完成。
- dirty-tree source/config 已 snapshot 到 `/root/data-tmp/workspace/02_experiments/code/external_b0_dirty_snapshot_*_candidate_eval`。
- paired profile row `b0_external_epoch<E>_candidate_profile` 存在，checkpoint load/profile forward 通过。
- `b0_external_epoch<E>_candidate_prob_eval` 在 CAMO、COD10K、NC4K 上完成 probability eval。
- `metrics_all.csv` 三行均为 `status=external_dirty_tree_observation_candidate`、`protocol=prob_map`、`repo_boundary=external_b0_dirty_snapshot_candidate`。
- `check_run_integrity.py` 与 `run_release_audits.sh --add-integrity ...` 通过。

必须更新：

| File | Location | Patch |
| --- | --- | --- |
| `04_paper/drafts/paper_draft.md` | 4.6 或工程观察段 | 只写 B0 作为高风险极限压缩观察或负结果；不得把它写成主方法、主表胜出结果或摘要贡献。 |
| `04_paper/drafts/paper_draft.md` | 4.8 可视化 | 只有三数据集 prediction 已生成且样本选择原则不变时，才可增加 B0 列；图注必须写 observation candidate。 |
| `04_paper/drafts/paper_draft.md` | 摘要/引言贡献/结论 | 默认不加入 B0；除非用户明确要求附录式观察摘要，也只能写为 exploratory observation，不能写性能结论。 |
| `04_paper/drafts/paper_interim_submission.md` | 工程观察/附录边界 | 默认不加入 B0；若加入，只能写 observation candidate 或 failure-analysis，不得进入摘要和结论。 |
| `04_paper/tables/main_results_template.md` | Main table notes / appendix table | B0 不能进入主表；若需要，新增 observation/failure-analysis table，保留 `external_dirty_tree_observation_candidate` 状态。 |
| `04_paper/tables/aggregated_results.md` | Notes/coverage | 运行 `aggregate_results.py`；确保 B0 行不会被标为 final main evidence。 |
| `04_paper/drafts/evidence_index.md` | B0 evidence | 写入 snapshot、checkpoint、profile JSON、prob eval run、integrity report 和 release audit 路径。 |
| `04_paper/drafts/claim_evidence_audit.md` | B0 claim | 将 B0 从 dirty observation 更新为 observation candidate 或 negative evidence；仍不能升级为 accepted main claim。 |
| `04_paper/drafts/paper_claim_evidence_matrix.md` | C11 | 更新 B0 evidence paths，claim status 只能是 observation only / failure-analysis accepted。 |
| `04_paper/drafts/paper_submission_readiness.md` | Evidence Matrix | 将 B0 行从 live observation 改为 observation candidate pass/failed-but-documented；Current Verdict 仍不得依赖 B0 定稿。 |
| `03_agent_tasks/acceptance/agent_acceptance_ledger.md` | A20 | 将 B0 的验收状态、候选 checkpoint/profile/prob-eval 证据和 paper boundary 同步为 accepted_reference_only 或 rejected_for_paper；不得保持旧 live-observation 口径。 |
| `04_paper/drafts/b0_status_consistency_audit_latest.md` | 全文 | 通过 `audit_b0_status_consistency.py` 重新生成，确认 B0 latest/best、checkpoint 状态和 observation-only/candidate 边界一致。 |
| `03_agent_tasks/acceptance/agent_acceptance_ledger_audit_latest.md` | 全文 | 通过 `audit_agent_acceptance_ledger.py` 重新生成，确认 agent 验收账本引用最新 B0 evidence 和 boundary。 |
| `04_paper/drafts/teacher_share_pack.md` | 风险边界 | 若分享给老师，说明 B0 是否失败、是否低于 Light，以及为什么不进入主表。 |
| `04_paper/drafts/presentation_outline.md` | 实验状态页 | 将 B0 更新为候选观察/负例，避免听众误解为主线结果。 |

Gate 4A 后必须全文检索并处理这些口径：

```text
B0
pvt_v2_b0
external_dirty_tree_observation_only
external_dirty_tree_observation_candidate
主表
摘要
结论
```

验收命令：

```bash
TMPDIR=/root/data-tmp/tmp /root/data-tmp/workspace/02_experiments/scripts/start_b0_candidate_eval.sh \
  --device cuda:0
python /root/data-tmp/workspace/02_experiments/scripts/aggregate_results.py \
  --out_md /root/data-tmp/workspace/04_paper/tables/aggregated_results.md
python /root/data-tmp/workspace/02_experiments/scripts/audit_b0_status_consistency.py
python /root/data-tmp/workspace/03_agent_tasks/acceptance/audit_agent_acceptance_ledger.py
bash /root/data-tmp/workspace/02_experiments/scripts/run_release_audits.sh \
  --add-integrity /root/data-tmp/workspace/02_experiments/runs/b0_external_epoch<E>_candidate_prob_eval \
  b0_external_epoch<E>_candidate_prob_eval CAMO,COD10K,NC4K
```

如果 Gate 4A 结果不完整、profile 缺失、只评了 COD10K 或状态不是
`external_dirty_tree_observation_candidate`，不得修改论文正文为 B0 结论；只在
`b0_cod10k_trend_note.md` 或实验日志中保留观察。

## Gate 4B: MobileMamba-T2 Observation Candidate

触发条件：

- 外部 MobileMamba-T2 训练结束或出现主控指定 checkpoint 后，`start_mobilemamba_candidate_eval.sh` 完成。
- dirty-tree source/config 已 snapshot 到 `/root/data-tmp/workspace/02_experiments/code/external_mobilemamba_dirty_snapshot_*_candidate_eval`。
- paired profile row `mobilemamba_t2_epoch<E>_candidate_profile` 存在，checkpoint load/profile forward 通过。
- `mobilemamba_t2_epoch<E>_candidate_prob_eval` 在 CAMO、COD10K、NC4K 上完成 probability eval。
- `metrics_all.csv` 三行均为 `status=external_dirty_tree_observation_candidate`、`protocol=prob_map`、`repo_boundary=external_mobilemamba_dirty_snapshot_candidate`。
- `check_run_integrity.py` 与 `run_release_audits.sh --add-integrity ...` 通过。

必须更新：

| File | Location | Patch |
| --- | --- | --- |
| `04_paper/drafts/paper_draft.md` | 4.6 或工程观察段 | 只写 MobileMamba-T2 作为替代轻量主干探索或负结果；不得把它写成主方法、主表胜出结果或摘要贡献。 |
| `04_paper/drafts/paper_draft.md` | 4.8 可视化 | 只有三数据集 prediction 已生成且样本选择原则不变时，才可增加 MobileMamba 列；图注必须写 observation candidate。 |
| `04_paper/drafts/paper_draft.md` | 摘要/引言贡献/结论 | 默认不加入 MobileMamba；除非用户明确要求附录式观察摘要，也只能写 exploratory observation，不能替代 Light-B2-C64 主线。 |
| `04_paper/drafts/paper_interim_submission.md` | 工程观察/附录边界 | 默认不加入 MobileMamba；若加入，只能写 observation candidate 或 failure-analysis，不得进入摘要和结论。 |
| `04_paper/tables/main_results_template.md` | Main table notes / appendix table | MobileMamba 不能进入主表；若需要，新增 observation/failure-analysis table，保留 `external_dirty_tree_observation_candidate` 状态。 |
| `04_paper/tables/aggregated_results.md` | Notes/coverage | 运行 `aggregate_results.py`；确保 MobileMamba 行不会被标为 final main evidence。 |
| `04_paper/drafts/evidence_index.md` | MobileMamba evidence | 写入 snapshot、checkpoint、profile JSON、prob eval run、integrity report 和 release audit 路径。 |
| `04_paper/drafts/claim_evidence_audit.md` | MobileMamba claim | 将 MobileMamba 从 dirty observation 更新为 observation candidate 或 negative evidence；仍不能升级为 accepted main claim。 |
| `04_paper/drafts/paper_claim_evidence_matrix.md` | C13 | 更新 MobileMamba evidence paths，claim status 只能是 observation only / failure-analysis accepted。 |
| `04_paper/drafts/paper_submission_readiness.md` | Evidence Matrix | 将 MobileMamba 行从 live observation 改为 observation candidate pass/failed-but-documented；Current Verdict 仍不得依赖 MobileMamba 定稿。 |
| `03_agent_tasks/acceptance/agent_acceptance_ledger.md` | A21 | 将 MobileMamba 的验收状态、候选 checkpoint/profile/prob-eval 证据和 paper boundary 同步为 accepted_reference_only 或 rejected_for_paper；不得保持旧 live-observation 口径。 |
| `04_paper/drafts/mobilemamba_status_consistency_audit_latest.md` | 全文 | 通过 `audit_mobilemamba_status_consistency.py` 重新生成，确认 MobileMamba latest/best、checkpoint 状态和 observation-only/candidate 边界一致。 |
| `03_agent_tasks/acceptance/agent_acceptance_ledger_audit_latest.md` | 全文 | 通过 `audit_agent_acceptance_ledger.py` 重新生成，确认 agent 验收账本引用最新 MobileMamba evidence 和 boundary。 |
| `04_paper/drafts/teacher_share_pack.md` | 风险边界 | 若分享给老师，说明 MobileMamba 是否失败、是否低于 Light，以及为什么不进入主表。 |
| `04_paper/drafts/presentation_outline.md` | 实验状态页 | 将 MobileMamba 更新为候选观察/负例，避免听众误解为主线结果。 |

Gate 4B 后必须全文检索并处理这些口径：

```text
MobileMamba
mobilemamba_t2
external_mobilemamba_dirty_snapshot_candidate
external_dirty_tree_observation_candidate
主表
摘要
结论
```

验收命令：

```bash
TMPDIR=/root/data-tmp/tmp /root/data-tmp/workspace/02_experiments/scripts/start_mobilemamba_candidate_eval.sh \
  --device cuda:0
python /root/data-tmp/workspace/02_experiments/scripts/aggregate_results.py \
  --out_md /root/data-tmp/workspace/04_paper/tables/aggregated_results.md
python /root/data-tmp/workspace/02_experiments/scripts/audit_mobilemamba_status_consistency.py
python /root/data-tmp/workspace/03_agent_tasks/acceptance/audit_agent_acceptance_ledger.py
bash /root/data-tmp/workspace/02_experiments/scripts/run_release_audits.sh \
  --add-integrity /root/data-tmp/workspace/02_experiments/runs/mobilemamba_t2_epoch<E>_candidate_prob_eval \
  mobilemamba_t2_epoch<E>_candidate_prob_eval CAMO,COD10K,NC4K
```

如果 Gate 4B 结果不完整、profile 缺失、只评了 COD10K 或状态不是
`external_dirty_tree_observation_candidate`，不得修改论文正文为 MobileMamba 结论；
只在外部观察状态和实验日志中保留观察。

## Always Re-Run Before Submission

```bash
python -m py_compile \
  /root/data-tmp/workspace/04_paper/scripts/generate_delta_summary.py \
  /root/data-tmp/workspace/04_paper/scripts/audit_claim_text.py
bash /root/data-tmp/workspace/02_experiments/scripts/run_release_audits.sh
```

如果上述审计失败，不更新摘要和结论为最终强主张；先修正文档或 metadata。
