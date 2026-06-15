# Paper Gate Patch Matrix Review

复核范围：`paper_draft.md`、`finalization_gates.md`、`paper_final_patch_plan.md`、`evidence_index.md`、`aggregated_results.md`。  
复核问题：Gate 1 clean baseline、Gate 2 KD、Gate 3 speed 任一结果回来后，当前 patch plan 是否漏了必须更新的正文位置、表格、图、审计或证据索引。  
结论：当前 patch plan 能覆盖主入口，但仍漏掉多处会残留旧口径的位置，尤其是 `paper_draft.md` 结论、`evidence_index.md`、自动审计/readiness 产物，以及 `aggregated_results.md` 的 coverage/notes。

## Critical

### C1. Gate 1 通过后，patch plan 漏更新 `paper_draft.md` 结论段

- 位置：`04_paper/drafts/paper_draft.md` 第 203-205 行，`## 5 结论`。
- 当前文本仍写“相对历史 ESCNet-B5 参考行”“仍需 clean baseline 三数据集统一复评确认”“尚未完成 clean snapshot 三数据集统一概率图复评”。
- 现有 patch plan 只列了摘要、4.3、4.4、主表、散点图和 audit，没有列结论段。
- 建议：Gate 1 clean baseline 回来后，必须把结论中所有 historical/reference/pending clean re-eval 口径替换为 final clean probability baseline 口径，并同步重算平均 S/wF/MAE delta。

### C2. Gate 2 通过后，patch plan 漏更新 `paper_draft.md` 结论段与运行状态段

- 位置：`paper_draft.md` 第 191 行、第 203-205 行。
- 第 191 行现在写 KD 多次 SIGKILL、未保存 `epoch_6.pth`、不能写 KD 效果；KD 完成后这段会变成错误事实。
- 第 205 行仍写“KD 是否能进一步缩小差距仍需完整训练后验证”。
- 现有 patch plan 只列摘要、3.3、4.4、4.6、4.8，没有列 4.7 和结论。
- 建议：Gate 2 回来后必须更新 4.7 为 KD final run 状态、checkpoint、eval run、integrity status；结论按结果分支写成“KD 有改善 / KD 未稳定改善”的最终发现。

### C3. Gate 1/2/3 任一通过后，patch plan 漏更新 `evidence_index.md`

- 位置：`04_paper/drafts/evidence_index.md` 全文，尤其第 27-50 行 baseline、第 67-75 行 profile、第 85-94 行 KD、第 106-110 行定稿前必须补齐。
- `finalization_gates.md` 的 Current Priority Queue 明确要求结果回来后更新 `evidence_index.md`，但 `paper_final_patch_plan.md` Gate 1/2/3 均未列它。
- 风险：正文和表格已更新，但 evidence index 仍说 baseline pending、KD 不能写、speed 不可写，审计链会自相矛盾。
- 建议：把 `evidence_index.md` 加入 Gate 1/2/3 的必改清单；每个 gate 都要记录 run 目录、checkpoint/profile JSON、metrics/status、可写结论、写作边界变化。

### C4. Gate 1/2/3 通过后，patch plan 只提 `claim_evidence_audit.md`，漏了实际正在使用的审计产物

- 位置：`evidence_index.md` 第 57-59 行列出 `paper_evidence_audit_latest.md`、`claim_text_audit_latest.md`、`paper_submission_readiness.md`。
- `paper_final_patch_plan.md` 第 41、67、89 行只提 `claim_evidence_audit.md`。
- 风险：旧 audit/readiness 仍显示 pass 或 pending，但内容已不对应新表和新正文。
- 建议：每个 gate patch 后必须重跑或更新至少三类审计/readiness：`paper_evidence_audit_latest.md`、`claim_text_audit_latest.md`、`paper_submission_readiness.md`；若仍保留 `claim_evidence_audit.md`，需说明它和最新 audit 文件的关系。

## High

### H1. Gate 1 通过后，patch plan 漏更新 `paper_draft.md` 4.1 的 baseline 协议口径

- 位置：`paper_draft.md` 第 115 行。
- 当前写“ESCNet-B5 当前只作为历史三数据集参考行和 CAMO checkpoint 复核证据，完整 clean snapshot 三数据集复评待 GPU 空闲后补齐”。
- Gate 1 通过后这句必须改，否则 4.4 即使改为 clean baseline，4.1 仍会否定它。
- 建议：将 4.1 改为“ESCNet-B5、Light-ESCNet 均采用统一概率图协议评测”，并保留 checkpoint 核验作为可靠性说明。

### H2. Gate 1 通过后，patch plan 漏更新 `paper_draft.md` 4.5 图 2 前后文字

- 位置：`paper_draft.md` 第 172 行。
- 当前写“图中 ESCNet-B5 点使用历史参考行，最终位置待 clean baseline 统一概率图复评后确认”。
- patch plan 提到重新生成 `accuracy_efficiency_scatter.png`，但没说要改图注/正文文字。
- 建议：Gate 1 后改为“图中 ESCNet-B5 点使用 clean probability baseline”，并同步检查平均 S-measure 是否重算。

### H3. Gate 2 通过后，patch plan 漏更新引言和相关工作的 KD 叙述

- 位置：`paper_draft.md` 第 17、23、43 行。
- 当前 KD 被写成“用于检验”“实验边界记录”“验证其是否能补偿”，都是 pending 口径。
- Gate 2 完成后，无论结果好坏，这些位置都需要改成最终口径：若提升，写为已验证补偿分支；若未提升，写为受限/失败分析。
- 建议：在 Gate 2 patch 中加入 `paper_draft.md` 引言贡献点和 2.4 KD 定位更新。

### H4. Gate 3 通过后，patch plan 漏更新 `paper_draft.md` 结论和 4.7 当前运行状态

- 位置：`paper_draft.md` 第 165、203、205 行。
- patch plan 覆盖摘要和 4.5，但结论仍可能保留“速度复测待完成”的旧句；4.7 也可能仍把 speed 当作当前运行待办。
- 建议：Gate 3 后在结论中明确“同条件 speed profile 已完成/未显示提升”的最终口径；如果 KD 未完成，只写 baseline 与 Light 的 controlled speed，不要暗示 KD speed 已完成。

### H5. `aggregated_results.md` 的 Gate 1 更新不能只改 status，还要处理 exp_id、notes 和 coverage

- 位置：`04_paper/tables/aggregated_results.md` 第 7、11、18 行。
- patch plan 第 37-38 行只写“metric status 更新”，不够。
- 如果 Gate 1 产出 exp_id 是 `baseline_escnet_b5_clean_prob_e120`，则表中当前 `baseline_escnet_b5_416_e120` 是否替换、保留 historical appendix、还是新增 clean row，都必须明确。
- 建议：同时更新 Main Compact Table、脚注说明、Metric Coverage；historical row 移出主表或标为 appendix/reference note，避免 clean 与 historical 两行混用。

### H6. Gate 2 后 `aggregated_results.md` 不能只填 KD 指标，还要填 metric/status/coverage 和 profile 边界

- 位置：`aggregated_results.md` 第 9 行。
- 当前 KD 行 Params/GMACs/Speed/Metric 全是 TBD/pending。
- patch plan 只说 KD row 进表，但没说 coverage 表和 status 字段。
- 建议：KD 完成后补 `Metric Status=final_main_kd`、三数据集 coverage、checkpoint/status metadata；Params/GMACs 若结构同 B2-C64 可复用也要标明来源，不能留 TBD。

### H7. Gate 3 后 `aggregated_results.md` 需要处理 KD 缺席分支

- 位置：`paper_final_patch_plan.md` 第 74 行要求 baseline、Light、KD 使用同一 profiling 命令。
- 但 `finalization_gates.md` 第 83 行允许“若 KD 未完成，只复测 baseline 与 Light 并注明 KD absent”。
- 当前 patch plan 没有写 KD 未完成但 Gate 3 baseline/Light speed 已完成的处理方式。
- 建议：补一个分支：若 KD 不存在，`aggregated_results.md` 只显示 baseline/Light final speed，KD 行保持 `not available: no final checkpoint`，不要把 Gate 3 卡死在 KD 上。

## Medium

### M1. Gate 1/2 后，完整指标表可能漏更新 meanF/meanE

- 位置：`paper_draft.md` 第 115 行声明指标包括 mean F 和 mean E，但第 154-157 行主表只列 S/wF/MAE。
- patch plan Gate 1/2 只说主表和 KD row，没有提醒附表或完整指标表。
- 建议：若 gate 结果回来，至少在 `aggregated_results.md` 或另一个完整指标表同步更新 S、wF、meanF、meanE、MAE；正文主表可保持紧凑，但证据表不能只剩三项。

### M2. Gate 2 后可视化图更新需要同步 case selection 和 figure assets

- 位置：`paper_draft.md` 第 197-199 行，`evidence_index.md` 第 77-83 行。
- patch plan 只说“可视化图增加 KD column”，但没说更新样本选择说明、图文件名和 evidence index 图表资产。
- 建议：新增或替换 `camo_visual_grid_b5_light_kd...png` 后，更新 `camo_case_selection...md` 中 KD 样本依据；若使用同一批 CAMO 样本，也要说明 KD 只增加预测列，不改变样本选择原则。

### M3. Gate 3 后需要补 profile 命令和 JSON 路径进入证据索引

- 位置：`evidence_index.md` 第 67-75 行。
- 当前只记录结构 profile，明确 latency/FPS 不能写。
- patch plan 第 82-84 行要求正文写清硬件、输入尺寸、batch size、warmup/repeat，但没有要求把 profile JSON、profiles.csv 行、命令参数写入 evidence index。
- 建议：Gate 3 后在 evidence index 加“Controlled speed profile”小节，列 baseline/Light/KD profile JSON、同一命令、空闲 GPU 检查依据、latency/FPS 数字和可写边界。

### M4. Gate 1 后 clean baseline 可能改变 delta，摘要、4.4、图 2、结论之外还要检查所有“约 70% + 小幅下降”组合句

- 位置：`paper_draft.md` 第 7、159、203 行。
- 结构下降 70% 不受 Gate 1 影响，但精度 delta 会受 clean baseline 影响。
- 建议：Gate 1 后全文搜索“历史”“参考行”“0.009”“0.006”“0.027”“clean”“待确认”，逐项确认是否仍成立。

### M5. Gate 2 如果结果不改善，patch plan 对“失败分析”的落点仍不够具体

- 位置：`paper_final_patch_plan.md` 第 55-68 行。
- 它说摘要写未追回、audit 标 failure analysis accepted，但没有规定正文放在哪里。
- 建议：若 KD 不改善，把 4.6 改为“KD 补偿实验与负结果分析”，说明可能原因：online MSE 只约束输出、teacher/student 容量差距、训练中断/恢复设置、CAMO 边界误差未改善；并避免把 KD 放进主贡献。

## Low

### L1. `paper_final_patch_plan.md` 的更新时间应随 gate patch 更新

- 位置：`paper_final_patch_plan.md` 第 3 行。
- 当前时间仍是 2026-06-13T17:38:00Z。
- 建议：任一 gate 回来后更新计划时间戳，避免多人协作时误判版本。

### L2. Gate 1 后 `paper_draft.md` 3.1 中 baseline 描述可保留，但最好减少路径噪声

- 位置：`paper_draft.md` 第 51 行。
- Gate 1 通过后，clean baseline 的证据已经升级，正文可从“路径防污染说明”转为“实验设置说明”，把过细路径留给 evidence index。
- 建议：正文保留 clean snapshot、teacher checkpoint 和不混用 dirty checkpoint 的核心事实即可。

## 建议补充到 patch plan 的最小清单

1. Gate 1 增加：更新 `paper_draft.md` 4.1、4.5 图 2 文字、5 结论；更新 `evidence_index.md`、`paper_evidence_audit_latest.md`、`claim_text_audit_latest.md`、`paper_submission_readiness.md`；更新 `aggregated_results.md` coverage 和 notes。
2. Gate 2 增加：更新 `paper_draft.md` 引言贡献点、2.4、4.7、5 结论；更新 `evidence_index.md` KD final evidence、图表资产、readiness 和两个 audit；若 KD 不改善，明确正文失败分析落点。
3. Gate 3 增加：允许 “KD 未完成但 baseline/Light speed 已完成” 分支；更新 `paper_draft.md` 结论、`evidence_index.md` controlled speed profile、`aggregated_results.md` speed status/notes、readiness 和两个 audit。

