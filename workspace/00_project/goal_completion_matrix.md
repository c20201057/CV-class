# Goal Completion Matrix

更新时间：2026-06-15T04:48:00Z / 2026-06-15 12:48:00 CST

本文档把用户原始目标拆成可证明的完成项、缺口和下一证据。它不替代
`orchestrator_tick_latest.md`、`finalization_gates.md` 或 `paper_submission_readiness.md`；
它用于防止把 interim 论文状态误判为整个目标完成。

工作准则：不偷懒，不因为怕风险而保守。高风险路线可以继续做，但每个论文主张都必须有可验收证据。
调度边界：不要抢占 Gate 1/2/3 主线证据链；当前 Gate 1 clean baseline、Gate 2 KD eval 和 Gate 3 speed 已完成，B0/MobileMamba 等风险分支不得阻塞论文回填和审计闭环。

## Current Verdict

当前目标未完成，但主线已经可以支撑一篇核心证据闭合的 Light-ESCNet 论文；当前外发稿仍按 honest interim 管理，直到本轮 Gate 2/3 回填后的 release audit 通过。

已证明的核心成果是 Light-ESCNet B2-C64 no-KD：完整训练、三数据集概率图评测、结构效率 profile、受控速度 profile、方法图、可视化、文献引用、提交包、`paper_delivery_manifest.md` 和多项 release audit 均已就绪。Gate 1 clean ESCNet-B5 三数据集 probability baseline 已完成并写入 `clean_prob_re_eval_complete`。Gate 2 KD final checkpoint/eval 已完成，但结果相对 no-KD 基本持平或略低，只能作为负结果分析。Gate 3 controlled speed 已完成。用户已授权继续结构分支消融；上一阶段 `no_edge_guidance` 已完整训练和评估，结果低于主模型，只能作为移除 decoder edge guidance 的负向消融证据候选；当前 Light-B2-C64 `no_edge_supervision` 四卡训练正在运行，尚未形成已验收结论。尚未完成的是 B0/MobileMamba 候选分支的完整候选验收，以及当前/后续结构消融扩展。

最新运行状态以 `00_project/orchestrator_tick_latest.md` 为准；当前 Gate 1/2/3 均为 pass，外部 B0 dirty rerun 已按用户明确要求停止，MobileMamba-T2 未观察到运行但仍为 `external_dirty_tree_observation_only`。

## Objective Coverage

| Requirement | Current Evidence | Status | Remaining Proof |
| --- | --- | --- | --- |
| 根据 `CV开题报告.pdf` 推进课题 | `cv_report_extracted.txt`, `project_profile.md`, `audit_cv_report_alignment.py` pass | pass | major route edits 后重跑 CV alignment audit |
| 以 `/root/ESCNet` 为实验基底 | clean baseline snapshot、Light/KD code snapshots、teacher checkpoint boundary | pass | 不把 dirty `/root/ESCNet` 升级为 clean baseline |
| 以 `/root/data-tmp/workspace` 为后续工作空间 | 所有主控文档、runs、scripts、paper assets 位于 workspace；TMPDIR 使用 data-tmp | pass | 新大产物继续写 data-tmp |
| 制定工作计划 | `master_plan.md`, `route_decision.md`, `finalization_gates.md` | pass but living | Gate 状态变化后更新 route/finalization docs |
| 搭建 workflow | `GPU_QUEUE.md`, `orchestrator_tick.py`, release audits, gate acceptance runbook, `task_board_consistency_audit_latest.md`, `gpu_runtime_state_audit_latest.md`, `RELEASE_AUDIT_REGISTRY.md`, `paper_delivery_manifest.md`, `audit_paper_delivery_manifest.py` | pass | Gate 1/2/3/4 完成后按 runbook 回填 |
| 给 subagent 的目标模式 prompt | `MASTER_TARGET_PROMPT.md`, `DISPATCH_PACKETS.md`, role prompts | pass | prompt 变更后重跑 `audit_prompt_principles.py` |
| subagent 准则包含不偷懒、不因风险保守 | `audit_prompt_principles.py` pass | pass | 所有 pending/task prompt 继续保留该原则 |
| 整合全局信息做路线判断 | `route_decision.md`, `route_decision_consistency_audit_latest.md` pass | pass but living | tick 中 B0/MobileMamba/Gate 状态变化后重跑路线审计 |
| 验收 agent 工作 | `agent_acceptance_ledger.md`, `audit_agent_acceptance_ledger.py` pass, `audit_task_board_consistency.py` pass, `audit_gpu_runtime_state.py` pass, `audit_release_audit_registry.py` pass | pass | 新报告必须进 ledger，task board/prompt/queue/watcher/release audit 变更后必须重跑 release audit |
| 论文草稿 | `paper_interim_submission.md`, `paper_draft.md` | core gates patched in progress | Gate 2/3 回填后跑完整 release audit |
| 文献和网络调研支撑 | `verified_literature.md`, `literature_gap_update_2026.md`, `citation_manifest.md`, `audit_literature_citations.py` pass | pass | Related Work 修改后重跑 citation audit |
| Light 轻量模型实验证据 | Light-B2-C64 120 epoch, prob eval, profile, integrity pass | pass | checkpoint 保持 immutable |
| Clean ESCNet-B5 final baseline | Gate 1 clean baseline | complete; CAMO/COD10K/NC4K probability eval, integrity and `clean_prob_re_eval_complete` rows present | pass | 定稿前随 release audit 继续复核 baseline integrity |
| KD 补偿路线 | final checkpoint/eval complete; CAMO 0.863/0.818/0.050, COD10K 0.864/0.782/0.024, NC4K 0.885/0.838/0.033; vs no-KD 基本持平或略低 | complete Gate 2; failure-analysis only | 不写 KD 提升；只写负结果/成本分析 |
| Controlled speed | idle V100 same-command profile complete: baseline 73.01 ms/13.70 FPS, Light 34.31 ms/29.15 FPS, KD 34.84 ms/28.71 FPS | complete Gate 3 | 只按受控 profile 条件报告 |
| No-edge-guidance structural ablation | run `light_b2_c64_no_edge_guidance_e120_s42_b6_w8_4gpu`; CAMO .846/.786/.818/.899/.058, COD10K .847/.749/.779/.917/.028, NC4K .873/.815/.842/.921/.038; release audit and integrity passed | complete as candidate evidence; negative vs accepted Light | 不进入主表/摘要/结论；可作为“decoder edge guidance removal degrades performance”的消融候选，定稿前需决定放入消融表或附录 |
| No-edge-supervision structural ablation | active run `light_b2_c64_no_edge_supervision_e120_s42_b6_w8_4gpu`; code/config/log/checkpoint path isolated under workspace and `/dev/shm/escnet_ablation_no_edge_supervision`; decoder edge guidance retained, `edge_loss_weight=0.0` | running, not accepted | 需要完整训练、CAMO/COD10K/NC4K probability eval、profile、integrity/audit 后才能写为消融结论 |
| B0 risk branch | epoch120 dirty observation, below Light on COD10K | observation_only Gate 4A | 候选 snapshot/load/profile/三数据集 eval 后才能附录讨论 |
| MobileMamba risk branch | not observed running; epoch50 latest/best COD10K row, no accepted checkpoint | observation_only Gate 4B | checkpoint 后候选 snapshot/load/profile/三数据集 eval |
| 最终论文强结论 | core Gate 1/2/3 evidence supports final core paper with KD negative boundary | pending release audit after patch | Gate 4/消融若不做则显式 withheld |

## Current Accepted Evidence

- Light-B2-C64 metrics: CAMO S=.862/wF=.818/MAE=.051; COD10K S=.866/wF=.782/MAE=.024; NC4K S=.886/wF=.840/MAE=.033。
- Light-B2-C64 profile: 29.81M params, 36.39 GMACs, 113.74 MB model size, 237.44 MB peak memory。
- Clean ESCNet-B5 probability baseline is active for Light-vs-ESCNet deltas: CAMO S=.881/wF=.842/MAE=.043; COD10K S=.877/wF=.802/MAE=.021; NC4K S=.897/wF=.857/MAE=.029。
- KD-B2-C64 metrics: CAMO S=.863/wF=.818/MAE=.050; COD10K S=.864/wF=.782/MAE=.024; NC4K S=.885/wF=.838/MAE=.033；相对 no-KD 不支持提升主张。
- KD historical recovery marker: `epoch_5.pth` 仅作恢复链路追溯，不代表当前仍有 KD pending 训练。
- Controlled speed: ESCNet-B5 73.01 ms / 13.70 FPS; Light-B2-C64 34.31 ms / 29.15 FPS; KD-B2-C64 34.84 ms / 28.71 FPS。
- No-edge-guidance structural ablation completed with lower metrics than accepted Light: CAMO S=.846/wF=.786/MAE=.058; COD10K S=.847/wF=.749/MAE=.028; NC4K S=.873/wF=.815/MAE=.038。
- No-edge-supervision structural ablation is currently running and is not accepted evidence yet: code `02_experiments/code/light_escnet_b2_c64_no_edge_supervision`, config `02_experiments/runs/light_b2_c64_no_edge_supervision_e120_s42/config_no_edge_supervision_b6_w8_4gpu.yaml`, active log `/dev/shm/escnet_ablation_no_edge_supervision/logs/train_no_edge_supervision_b6_w8_4gpu_20260615T044543Z.log`。
- B0 latest observation: epoch120 COD10K S=.8004, wF=.6862, meanF=.7203, meanE=.8878, MAE=.0350; still observation only。
- MobileMamba latest and best observed row: epoch50 COD10K S=.7487, wF=.6019, meanF=.6482, meanE=.8477, MAE=.0465; still no accepted checkpoint。

## Completion Blockers

| Blocker | Current State | Owner/Mechanism | Do Not Do |
| --- | --- | --- | --- |
| Gate 4 observations not clean candidates | B0/MobileMamba dirty observation only | candidate wrappers after main queue | do not put them in main table |
| Active no-edge-supervision ablation has no final checkpoint/eval | training running on GPU0-3 | main orchestrator + sync watcher | do not write edge-supervision conclusions yet |
| Release audit after Gate 2/3 manuscript patch | patch in progress | run full release audit with KD integrity | do not treat patched paper as final until audit passes |

## Final Completion Criteria

Do not mark the full goal complete until current-state evidence proves all of the following:

1. A final manuscript or explicitly accepted interim manuscript exists with all allowed claims backed by local evidence.
2. Gate 1 clean baseline is either complete and patched, or explicitly withheld in the final submitted version.
3. Gate 2 KD is either complete and patched, or documented as failed/absent without positive KD claims.
4. Gate 3 speed is either complete and patched, or latency/FPS claims are explicitly withheld.
5. Gate 4A/4B are either candidate-validated and documented as appendix/failure analysis, or explicitly withheld.
6. `run_release_audits.sh` passes after the final set of edits.
7. `orchestrator_tick_latest.md` confirms no pending gate has been accidentally promoted.

## Next Action

Next, monitor the active no-edge-supervision ablation to epoch20 checkpoint and then to epoch120 if healthy. After final checkpoint, run CAMO/COD10K/NC4K probability eval, profile, integrity checks and release audits before adding any edge-supervision ablation claim. Do not restart `watch_baseline_then_start_kd.sh`, baseline wrappers, B0 watcher or single-GPU KD.
