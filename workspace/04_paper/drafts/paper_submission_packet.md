# Paper Submission Packet

更新时间：2026-06-14T15:12:38Z / 2026-06-14 23:12:38 CST

本文档是当前论文提交包入口。它不替代审计脚本；它告诉总控、组员和后续
agent 现在应该读哪份稿、哪些结论可以写、哪些 gate 仍需边界约束。

## Recommended Manuscript

当前最适合作为外发或阶段提交的正文稿：

```text
/root/data-tmp/workspace/04_paper/drafts/paper_interim_submission.md
```

理由：

- 章节完整，已覆盖摘要、引言、相关工作、方法、实验、结论和参考文献。
- Light-ESCNet B2-C64 数字与 `metrics_all.csv`、`profiles.csv` 对齐。
- KD、B0、MobileMamba、clean baseline 和 speed 都保留了正确证据边界；其中 KD eval 与 speed 已完成。
- 已通过 release audit 中的数字、图像、主张、文献和提交协议检查。

工作稿仍可继续维护：

```text
/root/data-tmp/workspace/04_paper/drafts/paper_draft.md
```

它内容更细，适合继续吸收 Gate 4 或后续消融证据。

目标级完成度入口：

```text
/root/data-tmp/workspace/00_project/goal_completion_matrix.md
```

该矩阵说明当前核心论文证据已闭合，但原始长期目标仍保留 Gate 4 和消融扩展边界。

## Current Accepted Claims

- Light-ESCNet B2-C64 no-KD 已完成 120 epoch 四卡训练。
- Light-ESCNet B2-C64 已完成 CAMO、COD10K、NC4K 三数据集概率图评测。
- 当前主结果指标：

| Dataset | S | wF | meanF | meanE | MAE |
| --- | ---: | ---: | ---: | ---: | ---: |
| CAMO | 0.862 | 0.818 | 0.843 | 0.918 | 0.051 |
| COD10K | 0.866 | 0.782 | 0.808 | 0.928 | 0.024 |
| NC4K | 0.886 | 0.840 | 0.862 | 0.933 | 0.033 |

- 相对 clean ESCNet-B5 probability baseline，当前平均 S-measure 为 0.885 -> 0.871，
  MAE 为 0.031 -> 0.036。历史 ESCNet-B5 reference 只保留为内部追溯证据。
- 结构效率可写：参数量、GMACs、模型大小和峰值显存约降低 70%。
- 受控速度可写：ESCNet-B5 73.01 ms / 13.70 FPS，Light-B2-C64 34.31 ms / 29.15 FPS，KD student 34.84 ms / 28.71 FPS；条件是 idle V100、416 输入、batch 1、warmup=50、repeat=100。
- KD 可写为已完成但中性/负向：CAMO 0.863/0.818/0.050，COD10K 0.864/0.782/0.024，NC4K 0.885/0.838/0.033；不能写 KD 提升。
- Teacher checkpoint 固定为 `/root/data-tmp/epoch_120.pth`。

## Current Forbidden Claims

- 不把历史 ESCNet-B5 reference 写作当前同协议 baseline；当前同协议 baseline 使用 Gate 1 已验收的 clean probability baseline。
- 不写 KD 提升、蒸馏有效或缩小差距；Gate 2 已通过，但实测 deltas 不支持这些主张。
- latency/FPS 只能按 Gate 3 的 controlled profile 条件报告，不能推广为真实边缘端部署表现。
- 不把 B0 写入主表、摘要或结论，直到 Gate 4A 通过；即使通过也只能作为附录探索或失败分析。
- 不把 MobileMamba-T2 写入主表、摘要或结论，直到 Gate 4B 通过；即使通过也只能作为替代主干观察。
- 不写 SOTA、首次 KD-COD、实时部署或边缘端部署。

## Live Experiment State

- 外部 `/root/ESCNet` PVTv2-B0 online KD 已完成 dirty-tree 训练与 COD10K 中间评测，仍是 observation only。
- dirty checkpoint 已包括 `epoch_120.pth`，epoch120 metrics 已落表。
- 最新完整 B0 COD10K 中间行是 epoch120：
  S=.8004、wF=.6862、meanF=.7203、meanE=.8878、MAE=.0350。
- 当前最好 B0 COD10K 中间行仍是 epoch100：
  S=.8014、wF=.6882、meanF=.7221、meanE=.8899、MAE=.0346。
- B0 仍低于已验收 Light-B2-C64 COD10K，不抢占 Gate 1 clean baseline 和
  Gate 2 KD 的优先级。
- 当前没有外部 B0/MobileMamba 占卡进程；同一 dirty `/root/ESCNet/all.sh`
  已按用户明确要求停止。MobileMamba-T2 实时 epoch/iter 委托
  `orchestrator_tick_latest.md`，最新且最高 S 的 epoch50 COD10K 中间行为
  S=.7487、wF=.6019、meanF=.6482、meanE=.8477、MAE=.0465。它仍未完成候选
  checkpoint 验收、profile、三数据集 probability eval 和完整性检查，不能进入主表或摘要。

实时状态入口：

```text
/root/data-tmp/workspace/00_project/orchestrator_tick_latest.md
/root/data-tmp/workspace/02_experiments/runs/b0_external_status_latest.md
/root/data-tmp/workspace/02_experiments/runs/mobilemamba_t2_external_status_latest.md
```

## Required Evidence Files

| Purpose | Path |
| --- | --- |
| Metrics table | `/root/data-tmp/workspace/02_experiments/tables/metrics_all.csv` |
| Profile table | `/root/data-tmp/workspace/02_experiments/tables/profiles.csv` |
| Main table template | `/root/data-tmp/workspace/04_paper/tables/main_results_template.md` |
| Aggregated results | `/root/data-tmp/workspace/04_paper/tables/aggregated_results.md` |
| Claim-evidence matrix | `/root/data-tmp/workspace/04_paper/drafts/paper_claim_evidence_matrix.md` |
| Citation manifest | `/root/data-tmp/workspace/04_paper/drafts/citation_manifest.md` |
| Current delta summary | `/root/data-tmp/workspace/04_paper/drafts/current_delta_summary.md` |
| Reproducibility manifest | `/root/data-tmp/workspace/04_paper/drafts/reproducibility_manifest.md` |
| Light final metadata audit | `/root/data-tmp/workspace/04_paper/drafts/light_final_metadata_audit_latest.md` |
| Submission readiness | `/root/data-tmp/workspace/04_paper/drafts/paper_submission_readiness.md` |
| Gate patch matrix | `/root/data-tmp/workspace/04_paper/drafts/paper_gate_patch_matrix.md` |
| Gate patch plan | `/root/data-tmp/workspace/04_paper/drafts/paper_final_patch_plan.md` |
| Paper delivery manifest | `/root/data-tmp/workspace/04_paper/drafts/paper_delivery_manifest.md` |
| Paper delivery manifest audit | `/root/data-tmp/workspace/04_paper/drafts/paper_delivery_manifest_audit_latest.md` |
| Goal completion matrix | `/root/data-tmp/workspace/00_project/goal_completion_matrix.md` |
| Agent acceptance ledger | `/root/data-tmp/workspace/03_agent_tasks/acceptance/agent_acceptance_ledger.md` |
| Task-board consistency audit | `/root/data-tmp/workspace/03_agent_tasks/task_board_consistency_audit_latest.md` |
| GPU runtime state audit | `/root/data-tmp/workspace/00_project/gpu_runtime_state_audit_latest.md` |
| Release audit registry | `/root/data-tmp/workspace/02_experiments/scripts/RELEASE_AUDIT_REGISTRY.md` |
| Release audit registry audit | `/root/data-tmp/workspace/02_experiments/scripts/release_audit_registry_audit_latest.md` |
| B0 status consistency audit | `/root/data-tmp/workspace/04_paper/drafts/b0_status_consistency_audit_latest.md` |
| MobileMamba status consistency audit | `/root/data-tmp/workspace/04_paper/drafts/mobilemamba_status_consistency_audit_latest.md` |
| Release audit | `/root/data-tmp/workspace/04_paper/drafts/release_audit_latest.md` |
| CAMO failure-case number audit | `/root/data-tmp/workspace/04_paper/drafts/camo_failure_case_number_audit_latest.md` |

## Figure Assets

| Figure | Path | Status |
| --- | --- | --- |
| Light-B2-C64 method | `/root/data-tmp/workspace/04_paper/figures/light_b2_c64_method.png` | ready |
| Accuracy-efficiency scatter | `/root/data-tmp/workspace/04_paper/figures/accuracy_efficiency_scatter.png` | ready; ESCNet-B5 point uses clean probability baseline |
| CAMO visual grid | `/root/data-tmp/workspace/04_paper/figures/camo_visual_grid_b5_light_b2c64.png` | ready |
| CAMO failure-case analysis note | `/root/data-tmp/workspace/04_paper/drafts/camo_failure_case_analysis.md` | ready; CAMO-only reference visual analysis |
| CAMO failure-case number audit | `/root/data-tmp/workspace/04_paper/drafts/camo_failure_case_number_audit_latest.md` | ready; verifies per-image MAE statistics from CSV |
| CAMO worse cases | `/root/data-tmp/workspace/04_paper/figures/camo_light_worse_cases.png` | ready |
| CAMO close cases | `/root/data-tmp/workspace/04_paper/figures/camo_light_close_cases.png` | ready |
| CAMO better cases | `/root/data-tmp/workspace/04_paper/figures/camo_light_better_cases.png` | ready |
| B0 trend | `/root/data-tmp/workspace/04_paper/figures/b0_cod10k_intermediate_trend.png` | observation only |

## Finalization Gates

| Gate | Status | Patch Entry |
| --- | --- | --- |
| Gate 1 clean baseline | complete | `paper_gate_patch_matrix.md`, Gate 1 section |
| Gate 2 KD | complete | `paper_gate_patch_matrix.md`, Gate 2 section |
| Gate 3 speed | complete | `paper_gate_patch_matrix.md`, Gate 3 section |
| Gate 4A B0 | observation only | `paper_gate_patch_matrix.md`, Gate 4A section |
| Gate 4B MobileMamba-T2 | observation only | `paper_gate_patch_matrix.md`, Gate 4B section |

回填顺序先读 `paper_final_patch_plan.md`，再执行 `paper_gate_patch_matrix.md` 的对应 section。

## Audit Command

每次修改正文、表格、图像引用、metrics 或 profile 后运行：

```bash
python /root/data-tmp/workspace/04_paper/scripts/audit_paper_delivery_manifest.py
bash /root/data-tmp/workspace/02_experiments/scripts/run_release_audits.sh
```

如果新增 final probability eval run，必须加入同一次完整性检查：

```bash
bash /root/data-tmp/workspace/02_experiments/scripts/run_release_audits.sh \
  --add-integrity <prob_eval_run_dir> <exp_id> CAMO,COD10K,NC4K
```

当前 KD final probability eval 应显式加入：

```bash
bash /root/data-tmp/workspace/02_experiments/scripts/run_release_audits.sh \
  --add-integrity /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval \
  kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval \
  CAMO,COD10K,NC4K
```
