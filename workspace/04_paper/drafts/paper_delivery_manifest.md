# Paper Delivery Manifest

更新时间：2026-06-14T15:12:38Z / 2026-06-14 23:12:38 CST

用途：这是当前论文交付包的机器可审计清单。它说明哪些文件可以直接外发阅读，哪些是内部证据，哪些结论仍被 gate 限制。当前外发稿按 honest interim 管理；最终提交、组会或给老师阅读前，先读本文件，再运行 `audit_paper_delivery_manifest.py` 和完整 `run_release_audits.sh`。

工作准则：不偷懒，不因为怕风险而保守；高风险路线继续推进，但所有外发结论必须以已验收证据为边界。

## External-Facing Files

| Purpose | Path | Use |
| --- | --- | --- |
| Interim manuscript | `04_paper/drafts/paper_interim_submission.md` | 当前最适合给老师/组员阅读的论文稿 |
| Teacher/share note | `04_paper/drafts/teacher_share_pack.md` | 随稿说明可讲结论、证据边界和后续 gate |
| Presentation outline | `04_paper/drafts/presentation_outline.md` | 组会或答辩用 10-12 页提纲 |

## Core Figure Assets

| Figure | Path | Status |
| --- | --- | --- |
| Light-B2-C64 method figure | `04_paper/figures/light_b2_c64_method.png` | ready |
| Accuracy-efficiency scatter | `04_paper/figures/accuracy_efficiency_scatter.png` | ready; ESCNet-B5 point uses clean probability baseline; 历史 ESCNet-B5 reference 保留为内部追溯证据 |
| CAMO comparison grid | `04_paper/figures/camo_visual_grid_b5_light_b2c64.png` | ready |
| CAMO worse cases | `04_paper/figures/camo_light_worse_cases.png` | ready |
| CAMO close cases | `04_paper/figures/camo_light_close_cases.png` | ready |
| CAMO better cases | `04_paper/figures/camo_light_better_cases.png` | ready |
| B0 trend figure | `04_paper/figures/b0_cod10k_intermediate_trend.png` | internal/appendix candidate only |

## Internal Evidence And Reproducibility

| Purpose | Path |
| --- | --- |
| Submission packet | `04_paper/drafts/paper_submission_packet.md` |
| Reproducibility manifest | `04_paper/drafts/reproducibility_manifest.md` |
| Evidence index | `04_paper/drafts/evidence_index.md` |
| KD recovery status | `02_experiments/runs/kd_recovery_status_latest.md` |
| Claim-evidence matrix | `04_paper/drafts/paper_claim_evidence_matrix.md` |
| Submission protocol checklist | `04_paper/drafts/submission_protocol_checklist.md` |
| Goal completion matrix | `00_project/goal_completion_matrix.md` |
| Latest orchestrator tick | `00_project/orchestrator_tick_latest.md` |
| Release audit report | `04_paper/drafts/release_audit_latest.md` |
| Release audit registry | `02_experiments/scripts/RELEASE_AUDIT_REGISTRY.md` |
| Release audit registry report | `02_experiments/scripts/release_audit_registry_audit_latest.md` |

## Allowed Delivery Claims

- Light-ESCNet B2-C64 no-KD 已完成 120 epoch 训练和 CAMO/COD10K/NC4K 三数据集概率图评测。
- Light-ESCNet B2-C64 当前主结果为 CAMO S=.862/wF=.818/MAE=.051，COD10K S=.866/wF=.782/MAE=.024，NC4K S=.886/wF=.840/MAE=.033。
- 相对 clean ESCNet-B5 probability baseline，当前平均 S-measure 为 0.885 -> 0.871，MAE 为 0.031 -> 0.036；历史 ESCNet-B5 reference 只保留为内部追溯证据。
- 结构复杂度可以写约 70% 降低：参数量、GMACs、模型大小和峰值显存。
- 受控速度可以写：ESCNet-B5 73.01 ms / 13.70 FPS，Light-B2-C64 34.31 ms / 29.15 FPS，KD student 34.84 ms / 28.71 FPS；条件为 idle V100、416 输入、batch 1、warmup=50、repeat=100。
- KD 可以写作已完成但中性/负向：CAMO 0.863/0.818/0.050，COD10K 0.864/0.782/0.024，NC4K 0.885/0.838/0.033；不能写作已证明提升。
- B0、MobileMamba-T2 只能写作工程观察或失败风险，不能写作已证明提升。

## Withheld Claims

- 不把历史 ESCNet-B5 reference 写作当前同协议 baseline；Gate 1 已通过，当前同协议 baseline 使用 clean probability baseline。
- 不写 KD 提升、蒸馏有效或缩小差距；Gate 2 已通过，但实测 deltas 不支持这些主张。
- latency/FPS 只能按 Gate 3 的 controlled profile 条件报告，不能推广为真实边缘端部署表现。
- 不把 B0 写入主表、摘要或结论，直到 Gate 4A 通过；即使通过也只能先作为附录探索或失败分析。
- 不把 MobileMamba-T2 写入主表、摘要或结论，直到 Gate 4B 通过；即使通过也只能先作为替代主干观察。
- 不写 SOTA、首次 KD-COD、实时部署或边缘端部署。

## Current Gate Snapshot

最新状态委托 `00_project/orchestrator_tick_latest.md`。当前核心论文 Gate 1/2/3 已闭合；长期目标仍保留 Gate 4 observation 和后续消融边界。

- Light main result: pass.
- Gate 1 clean baseline: complete; CAMO/COD10K/NC4K probability eval、integrity 和 `clean_prob_re_eval_complete` metadata 已完成。
- Gate 2 KD: complete; final checkpoint/eval/integrity 已完成，但结果相对 no-KD 基本持平或略低，只能作为负结果分析。
- Gate 3 speed: complete;受控 latency/FPS 已完成，必须带 profile 条件报告。
- Gate 4A B0: observation only.
- Gate 4B MobileMamba-T2: observation only; epoch50 COD10K intermediate row is now the latest/highest-S observation, S=.7487/wF=.6019/meanF=.6482/meanE=.8477/MAE=.0465, with no accepted checkpoint yet.

## Required Commands

```bash
python /root/data-tmp/workspace/04_paper/scripts/audit_paper_delivery_manifest.py
bash /root/data-tmp/workspace/02_experiments/scripts/run_release_audits.sh \
  --add-integrity /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval \
  kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval \
  CAMO,COD10K,NC4K
```
