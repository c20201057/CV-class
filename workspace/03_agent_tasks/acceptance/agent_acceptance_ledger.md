# Agent Acceptance Ledger

更新时间：2026-06-14T08:31:44Z / 2026-06-14 16:31:44 CST

用途：集中记录主控对 subagent / review agent 产物的验收结论。`task_board.md` 记录任务状态，本文件记录“为什么接收、接收到什么证据边界、哪些内容不能写进论文”。后续 agent 交付后必须先进入 `03_agent_tasks/reports/` 或 `05_reviews/`，再由主控更新本 ledger。

工作准则保持不变：不偷懒，不因为怕风险而保守。高风险路线可以做，但交付必须留下可复查路径、命令、日志和写作边界。

## Acceptance States

- `accepted_main_evidence`：可支撑当前论文主线或交付 workflow。
- `accepted_tooling`：工具链通过，可用于后续实验；工具 smoke 指标不自动进入论文。
- `accepted_review`：审稿/审计意见已被主控采纳或转化为门禁。
- `accepted_reference_only`：可作为历史参考、趋势、失败分析或 observation，不进入主表强结论。
- `pending_gate`：等待 GPU、checkpoint、三数据集评测、完整性检查或 release audit。
- `rejected_for_paper`：工程上保留，但不得写入论文结果。

Boundary keywords for audits: partial smoke metrics and dirty-tree observations must `not enter paper`
as results and must `not enter main table` before their gates pass.

## Ledger

| ID | Agent / Source | Artifact | Acceptance | Evidence Checked | Paper Boundary | Follow-up |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | Maxwell / ESCNet 基底侦察 | `05_reviews/subagent_reviews.md` | accepted_review | 结构瓶颈、核心文件、B2-C64 参数估算、二值评测风险已被 `project_profile.md`、`route_decision.md`、prompt 采纳 | 支撑路线选择，不是实验结果 | 继续保持 `/root/ESCNet` dirty boundary |
| A02 | Mill / 环境与数据侦察 | `05_reviews/subagent_reviews.md` | accepted_review | 四卡环境、数据集数量、根分区空间风险、随机 forward smoke | 支撑 workflow 和资源约束 | 新大文件继续写 `/root/data-tmp/workspace` 或 `/root/data-tmp/tmp` |
| A03 | Galileo / 文献核验 | `05_reviews/subagent_reviews.md`, `01_literature/verified_literature.md` | accepted_review | 文献按基准、轻量、频域、边界、扩展方向分组；后续由 `citation_manifest.md` 和 `audit_literature_citations.py` 硬化 | 支撑 related work；不能主张首个轻量 COD、首个 KD-COD 或 SOTA | 2025-2026 文献继续按 DOI/publisher/project metadata 核验 |
| A04 | Ohm / Workflow 方案 | `05_reviews/subagent_reviews.md` | accepted_review | workspace 分层、脚本规格、独立 run 目录、拒绝覆盖规则被工作区结构和 prompt 采纳 | 支撑多 agent workflow | 后续新增脚本必须接入审计或 runbook |
| A05 | Zeno / ESCNet 代码审计 | `05_reviews/subagent_reviews.md` | accepted_review | 指出 PVT-B5/FEM/MTA/AETP 等瓶颈，B2-C64/B0-C64 路线和协议风险被采纳 | 支撑方法路线，不是性能证据 | 边界分支消融仍 pending |
| A06 | Pauli / Baseline profiling | `03_agent_tasks/reports/P0_profile_baseline.md`, `02_experiments/runs/profile_escnet_b5_416/profile.json`, `02_experiments/tables/profiles.csv` | accepted_reference_only | 参数量、GMACs、模型大小、峰值显存字段完整；checkpoint load missing=0/unexpected=0 | 结构 profile 可用；latency/FPS 受并发影响，Gate 3 前不能写最终速度 | idle-GPU controlled speed 待 Gate 3 |
| A07 | Ptolemy / Eval suite | `03_agent_tasks/reports/P0_eval_suite.md`, `02_experiments/scripts/run_eval_suite.sh`, `02_experiments/scripts/collect_metrics.py` | accepted_tooling | runner、metric parser、CAMO smoke 和 idempotent CSV 更新通过 | binary smoke metric rejected_for_paper；工具可作为历史工程资产 | 主表评测改用 probability suite |
| A08 | Dewey / Light B2-C64 implementation | `03_agent_tasks/reports/P0_light_b2_c64_impl.md`, `02_experiments/code/light_escnet_b2_c64` | accepted_main_evidence | isolated code、B2+C64 smoke、29.807714M 参数、ESCNet output interface 兼容 | 实现和 profile 可支撑方法；初始 `bb_pretrained=false` smoke 不等于最终训练配置 | 最终训练已由主控用 B2 pretrained 完成并验收 |
| A09 | Huygens / Probability inference | `03_agent_tasks/reports/P1_probability_inference.md`, `02_experiments/scripts/infer_prob.py` | accepted_tooling | sigmoid probability path、文件数量对齐、CAMO smoke、teacher checkpoint mismatch 风险定位 | CAMO smoke metric rejected_for_paper；probability inference 成为主评测协议基础 | 主表只走 `run_prob_eval_suite.sh` 和 integrity |
| A10 | Aristotle / paper narrative review | `03_agent_tasks/task_board.md`, `04_paper/drafts/paper_draft.md` | accepted_review | 写作边界和表格计划被论文草稿采纳 | 支撑叙事结构，不是实验结果 | Gate 回填后继续审稿 |
| A11 | Poincare / KD proposal | `03_agent_tasks/task_board.md`, `03_agent_tasks/pending/P1_distill_light_b2_c64.md` | accepted_reference_only | online KD 路线采纳，MSE teacher-student 输出蒸馏已实现并 smoke | KD 效果 pending_gate，不能写提升 | 等 Gate 1 后恢复 KD full train |
| A12 | Lagrange / Experiment gap audit | `05_reviews/experiment_gap_audit.md` | accepted_review | baseline/KD/speed/消融/可视化缺口被 finalization gates 和 GPU queue 采纳 | 支撑 gap 判断；其中旧 dirty baseline 命令被后续 clean wrapper 取代 | 以 `GPU_QUEUE.md` 和 acceptance runbook 为最新入口 |
| A13 | Lagrange / KD recovery config audit | `05_reviews/kd_recovery_config_audit.md`, `02_experiments/scripts/start_kd_full_train.sh` | accepted_review | epoch5 resume、workers0 失败、四卡 batch2 -> 双卡 -> 单卡降级策略核查 | 支撑 KD recovery，不证明 KD 有效 | Gate 2 等 GPU 和 Gate 1 完成 |
| A14 | Lagrange / Paper evidence audit | `05_reviews/paper_evidence_audit_20260613.md` | accepted_review | baseline/FPS/KD/消融/可视化/参考文献/训练集边界已被论文和审计收紧 | 支撑论文边界，不新增实验结论 | release audit 持续检查 |
| A15 | Epicurus / Baseline boundary audit | `05_reviews/paper_baseline_boundary_audit_20260613.md` | accepted_review | historical reference vs clean probability baseline 边界被 `metrics_all.csv` metadata、Gate 1、claim audit 采纳 | Gate 1 前只能写 historical reference delta | 等 NC4K clean baseline 完成 |
| A16 | Feynman / Gate patch matrix review | `05_reviews/paper_gate_patch_matrix_review_feynman.md`, `04_paper/drafts/paper_gate_patch_matrix.md` | accepted_review | Gate 1/2/3 漏改点已补入 matrix；Gate 4A/4B 和外发稿同步要求已补充 | 支撑回填 workflow | `audit_gate_patch_readiness.py` 已自动检查 matrix coverage |
| A17 | Feynman / Light B2-C64 narrative bridge | `05_reviews/light_b2_c64_narrative_bridge_review_feynman.md`, `04_paper/drafts/paper_interim_submission.md`, `04_paper/drafts/method_light_b2_c64.md` | accepted_review | B2-C64 设计动机、同族主干压缩、边缘协同边界、B0 降噪叙事已采纳 | 支撑外发稿质量 | Gate 回填后同步重审摘要和结论 |
| A18 | Main orchestrator / Light full train and prob eval | `02_experiments/runs/light_b2_c64_e120_s42`, `02_experiments/runs/light_b2_c64_e120_s42_prob_eval_v2`, `04_paper/drafts/light_final_metadata_audit_latest.md` | accepted_main_evidence | 120 epoch checkpoint、final loss、CAMO/COD10K/NC4K probability metrics、integrity、profile 和 metadata audit 通过 | 当前唯一 accepted main student result | 保持 checkpoint immutable |
| A19 | Main orchestrator / Clean baseline snapshot and Gate 1 wrapper | `02_experiments/code/baseline_escnet_clean`, `02_experiments/runs/baseline_escnet_b5_clean_prob_e120`, `03_agent_tasks/acceptance/gate_result_acceptance_runbook.md` | accepted_main_evidence | clean snapshot strict load 通过；Gate 1 CAMO/COD10K/NC4K probability eval、integrity 和 `clean_prob_re_eval_complete` metadata 完成 | 可作为 clean probability baseline；历史 ESCNet-B5 reference 只保留追溯 | 随 release audit 继续复核 integrity；不要重复启动 baseline wrapper |
| A20 | Main orchestrator / B0 external observation | `02_experiments/runs/b0_external_status_latest.md`, `04_paper/drafts/b0_status_consistency_audit_latest.md` | accepted_reference_only | dirty-tree B0 epoch120 COD10K intermediate row 已记录；低于 Light-B2-C64；未过 candidate gate | observation only，不进主表、摘要、结论 | Gate 4A 只在不阻塞主队列时做 candidate eval |
| A21 | Main orchestrator / MobileMamba external observation | `02_experiments/runs/mobilemamba_t2_external_status_latest.md`, `04_paper/drafts/mobilemamba_status_consistency_audit_latest.md`, `02_experiments/scripts/watch_external_mobilemamba_progress.sh` | accepted_reference_only | dirty-tree MobileMamba 当前未观察到运行；latest/highest-S epoch50 COD10K row 已记录，S=.7487/wF=.6019/meanF=.6482/meanE=.8477/MAE=.0465；无已验收 checkpoint，状态一致性审计 pass；watcher 已支持未来重启时用 `--sync_on_change` 触发 observation sync | observation only，不进主表、摘要、结论 | checkpoint 出现后才能 Gate 4B candidate；不抢占 Gate 2 KD 主队列 |
| A22 | Main orchestrator / Task-board consistency gate | `03_agent_tasks/task_board.md`, `03_agent_tasks/audit_task_board_consistency.py`, `03_agent_tasks/task_board_consistency_audit_latest.md` | accepted_tooling | task board 路径、dispatch section、GPU queue、prompt/pending/report 引用、planned KD run 边界和工作准则均已自动检查；release audit 已接入并 pass | workflow/tooling only，不是实验结果，不进入论文主表 | 每次改 task board、prompt 路径或队列状态后重跑 release audit |
| A23 | Main orchestrator / GPU runtime state gate | `02_experiments/scripts/audit_gpu_runtime_state.py`, `00_project/gpu_runtime_state_audit_latest.md`, `02_experiments/scripts/run_release_audits.sh` | accepted_tooling | live paused Gate 1 wrapper、resume watcher target PID、KD watcher、MobileMamba process state、watcher logs 和 premature KD launch 风险均已只读检查；首跑 pass，release audit 已接入 | workflow/runtime guard only，不是实验结果，不进入论文主表 | 每次改 GPU watcher、handoff 或 queue 逻辑后重跑 release audit |
| A24 | Main orchestrator / Release audit registry gate | `02_experiments/scripts/RELEASE_AUDIT_REGISTRY.md`, `02_experiments/scripts/audit_release_audit_registry.py`, `02_experiments/scripts/release_audit_registry_audit_latest.md` | accepted_tooling | fixed release gates 的脚本顺序、latest release report 命令、报告路径和控制文档均由 registry 审计检查；release audit 已接入 | workflow/meta-audit only，不是实验结果，不进入论文主表 | 每次新增、删除或重命名 release audit 固定项后先更新 registry 再重跑 release audit |
| A25 | Main orchestrator / Paper delivery manifest gate | `04_paper/drafts/paper_delivery_manifest.md`, `04_paper/scripts/audit_paper_delivery_manifest.py`, `04_paper/drafts/paper_delivery_manifest_audit_latest.md` | accepted_tooling | manifest 已列出当前可外发稿件、核心图表、内部证据、允许主张、withheld claims 和必跑命令；审计已能区分禁止写作语句与危险宣称；release audit 已接入 | delivery/workflow boundary only，不是实验结果，不进入论文主表 | 每次新增外发稿、图表资产、证据文档或 withheld claim 后重跑 delivery manifest audit 和 release audit |
| A26 | Main orchestrator / MobileMamba observation sync | `02_experiments/scripts/sync_mobilemamba_observation_state.py`, `02_experiments/runs/mobilemamba_observation_sync_latest.md`, `02_experiments/runs/mobilemamba_t2_external_status_latest.md`, `02_experiments/scripts/watch_external_mobilemamba_progress.sh` | accepted_tooling | sync 脚本 dry-run 通过；真实运行会刷新 MobileMamba 状态、tick、路线/交付控制文档和相关审计，且不启动、不停止、不 signal 训练；watcher 可选 `--sync_on_change` 会在新 result/checkpoint 签名出现后调用该入口 | observation sync tooling only，不是实验结果，不进入论文主表 | 每次 MobileMamba 新 COD10K 行或 checkpoint 出现后优先运行该入口；若未来重启 watcher，可加 `--sync_on_change` 减少人工漏同步，再检查 release audit |
| A27 | Kant + main orchestrator / KD four-GPU recovery diagnosis | `05_reviews/kd_4gpu_recovery_diagnosis_kant_20260614.md`, `02_experiments/scripts/probe_nccl_allreduce.py`, `02_experiments/scripts/probe_kd_ddp_init.py`, `02_experiments/runs/kd_light_b2_c64_e120_s42/logs/train_resume_epoch5_b2_workers0_4gpu_20260614T073026Z.log` | accepted_tooling | Kant 的只读诊断将历史 NCCL store 错误定位为 rank0 早退后的二级症状；主控新增 pure NCCL allreduce probe 与 KD model DDP init probe并通过，修正 DDP device mapping/resume map_location/timeout/rank traceback，四卡 recovery PID 806897 已完成 DDP/resume/teacher load，保存 `epoch_6.pth`/`epoch_7.pth`/`epoch_8.pth`/`epoch_9.pth` 并运行 epoch10 | tooling/recovery evidence only；Gate 2 仍是 pending，不能写 KD 提升或把 partial checkpoint 当 final result | 继续监控到 final checkpoint；完成后跑 CAMO/COD10K/NC4K probability eval、integrity、manifest/claim/release audits |
| A28 | Main orchestrator / KD recovery read-only status monitor | `02_experiments/scripts/summarize_kd_recovery.py`, `02_experiments/runs/kd_recovery_status_latest.md`, `00_project/orchestrator_tick_latest.md` | accepted_tooling | 新增只读 KD recovery 汇总入口并接入 orchestrator tick；当前报告记录 latest iter、latest checkpoint、final checkpoint status、process/GPU snapshot，且明确 `pending_gate_no_kd_claims` | monitoring/tooling only；不是 KD 结果，不能写 KD 提升或把 partial checkpoint 当 final result | 后续接棒先刷 tick 或运行 summarize 脚本；final checkpoint 出现后再走 Gate 2 prob eval 与完整审计 |

## Required Future Updates

1. 新增 `03_agent_tasks/reports/*.md` 后，本 ledger 必须新增一行，写清 acceptance 和 paper boundary。
2. 新增 `05_reviews/*.md` 后，本 ledger 必须新增一行，写清主控是否采纳以及转化到哪个 gate、prompt、论文或审计。
3. 如果某个 agent 产物被拒收，不能只从 task board 删除；必须在本 ledger 中标记 `rejected_for_paper` 并写明原因。
4. Gate 1/2/3/4A/4B 任一完成后，相关 ledger 行要从 `pending_gate` 更新为 `accepted_main_evidence`、`accepted_reference_only` 或 `rejected_for_paper`。

## Audit Command

```bash
python /root/data-tmp/workspace/03_agent_tasks/acceptance/audit_agent_acceptance_ledger.py
```
