# Paper Submission Readiness Matrix

更新时间：2026-06-14T15:12:38Z / 2026-06-14 23:12:38 CST

This matrix is the short-form submission dashboard. It does not replace
`finalization_gates.md`; it tells the orchestrator and subagents what can be
claimed now, what is still pending, and what command closes each gap.
For result-to-paper edits after Gate 1/2/3/4A/4B, use
`04_paper/drafts/paper_gate_patch_matrix.md`; for current citeable deltas, use
`04_paper/drafts/current_delta_summary.md`.

## Current Verdict

The paper can now be written as a final core Light-ESCNet paper, with careful
claim boundaries. The accepted core is Light-ESCNet B2-C64 no-KD: full
120-epoch training, three-dataset probability evaluation, structural profile,
and controlled idle-GPU speed profile. Gate 1 clean ESCNet-B5 baseline, Gate 2
KD evaluation, and Gate 3 speed retest are complete. The KD result is measured
as neutral/negative versus no-KD, so it supports failure analysis rather than a
KD improvement claim.
The cleanest current manuscript for sharing is
`04_paper/drafts/paper_interim_submission.md`; pair it with
`04_paper/drafts/teacher_share_pack.md` when sending to a teacher or teammate.
Use `04_paper/drafts/presentation_outline.md` as the current 10-12 slide
group-meeting/defense outline; it keeps the same evidence boundaries as the
interim manuscript.
`paper_draft.md` remains the more verbose evidence-rich working draft.

## Evidence Matrix

| Requirement | Current Evidence | Status | Paper Use Now | Next Closure Action |
| --- | --- | --- | --- | --- |
| Workspace boundary | Outputs under `/root/data-tmp/workspace`; clean baseline snapshot exists; `/root/ESCNet/checkpoints/escnet` legacy checkpoint path is a symlink into data-tmp | pass | can cite reproducibility boundary | keep all new artifacts and TMPDIR in data-tmp |
| ESCNet-B5 teacher checkpoint | `/root/data-tmp/epoch_120.pth` strict-loads into clean ESCNet-B5 with missing=0/unexpected=0 | pass | can cite teacher/checkpoint decision | never use `/root/ESCNet/checkpoints/escnet/epoch_120.pth` |
| Light B2-C64 full training | `light_b2_c64_e120_s42/epoch_120.pth` and final loss 1.369 | pass | main method result | keep checkpoint immutable |
| Light B2-C64 three-dataset probability eval | `light_b2_c64_e120_s42_prob_eval_v2`, integrity passed, `status=final_main_light` | pass | main accuracy row | rerun integrity before final submission |
| Structural profile | 29.81M params, 36.39 GMACs, 113.74 MB, 237.44 MB peak mem | pass | efficiency table | rerun profile only if code/checkpoint changes |
| ESCNet-B5 clean probability baseline | clean snapshot probability eval complete for CAMO/COD10K/NC4K; integrity and `clean_prob_re_eval_complete` metadata present | pass | clean same-protocol baseline deltas | keep baseline integrity in release audit; do not rerun unless evidence regresses |
| KD B2-C64 | final checkpoint at epoch120 from four-GPU fast-shm route; training log ended cleanly; checkpoints retained every 20 epochs | pass | failure analysis and neutral/negative KD comparison; no improvement claim | keep final checkpoint immutable; rerun only if KD definition changes |
| KD probability eval | CAMO/COD10K/NC4K probability eval complete with `status=final_main_kd`; integrity passed | pass | KD row may appear as measured evidence, not as promoted student | keep KD integrity in release audit |
| B0 extreme branch | COD10K epoch 10/20/30/40/50/60/70/80/90/100/110/120 intermediate metrics; raw dirty checkpoints have appeared through `epoch_120.pth`, with latest state delegated to `b0_external_status_latest.md`; latest complete row epoch120 is S=.8004/wF=.6862/meanF=.7203/meanE=.8878/MAE=.0350; epoch100 is the best complete B0 row at S=.8014/wF=.6882/meanF=.7221/meanE=.8899/MAE=.0346, still below accepted Light-B2-C64 COD10K | observation only | not in main table; possible engineering note after Gate 4A | do not preempt Gate 1/KD for B0 candidate eval; verify checkpoint load/profile with `start_b0_candidate_eval.sh` only as Gate 4A appendix/failure-analysis evidence |
| MobileMamba-T2 branch | external dirty `/root/ESCNet` run is not observed running; live epoch/iter delegated to `orchestrator_tick_latest.md` and `mobilemamba_t2_external_status_latest.md`; no accepted checkpoint yet; MobileMamba latest/highest-S epoch50 COD10K row is S=.7487/wF=.6019/meanF=.6482/meanE=.8477/MAE=.0465; candidate eval wrapper and snapshot script are ready | observation only | not in main table; possible engineering note after Gate 4B | do not preempt Gate 2 KD for MobileMamba candidate eval; verify checkpoint load/profile with `start_mobilemamba_candidate_eval.sh` only as Gate 4B appendix/failure-analysis evidence |
| Latency/FPS | controlled idle V100 profiles complete: ESCNet-B5 73.01 ms / 13.70 FPS; Light 34.31 ms / 29.15 FPS; KD 34.84 ms / 28.71 FPS | pass | report controlled speed numbers with profile conditions | rerun only if code/checkpoint/profile protocol changes |
| Claim text audit | `audit_claim_text.py` pass | pass | current draft has no over-claim found | rerun after any abstract/results/conclusion edits |
| Evidence metadata audit | `audit_paper_evidence.py` pass | pass | current metrics table boundary is clean | rerun after every metrics update |
| Claim-evidence matrix | `paper_claim_evidence_matrix.md` plus `audit_claim_evidence_matrix.py` | pass after audit | use as the claim-level acceptance map before paper edits | update matrix after every Gate 1/2/3/4A/4B result |
| Gate patch readiness | `audit_gate_patch_readiness.py` writes `gate_patch_readiness_latest.md`; pending gates are allowed but partial/malformed evidence fails, now including Gate 4A B0, Gate 4B MobileMamba, patch-matrix coverage and `paper_final_patch_plan.md` coverage for external-facing packet sync | pass | prevents patching paper claims from half-landed Gate evidence or updating only the internal draft while the external-facing packet goes stale | rerun after every metrics/profile/update to `paper_gate_patch_matrix.md` or `paper_final_patch_plan.md`; release audit runs it automatically |
| External branch status consistency | `audit_b0_status_consistency.py` and `audit_mobilemamba_status_consistency.py` pass; control docs agree on B0 epoch120/epoch100 observation rows, MobileMamba epoch50/latest/highest-S observation row, checkpoint state and observation-only boundaries | pass | keeps dirty-tree B0/MobileMamba observations not in the main table, abstract or conclusion | rerun after every external watcher refresh, result row append, checkpoint appearance, route edit or paper-control edit; release audit runs both automatically |
| GPU handoff consistency | `audit_gpu_handoff_consistency.py` pass; tick, GPU_QUEUE, current_run_snapshot, resume_handoff, orchestrator_status, task_board, P0_gpu_queue_operator, P0_gate1_kd_handoff_card, DISPATCH_PACKETS and gate runbook agree on paused Gate 1 wrapper/resume watcher/KD watcher/MobileMamba observation boundary | pass | prevents duplicate baseline wrapper, premature KD, or promotion of external observation branches | rerun after every handoff, queue or status edit; release audit runs it automatically |
| Route decision consistency | `audit_route_decision_consistency.py` pass; route decision, finalization gates, readiness, evidence index and task board agree with latest tick for B0/MobileMamba/Gate state | pass | keeps route judgment aligned with current evidence instead of stale intermediate rows | rerun after every route, gate, status or observation edit; release audit runs it automatically |
| CV report alignment | `audit_cv_report_alignment.py` pass; current workflow and drafts cover the opening report routes: light backbone/fusion, boundary, KD/quantization, metrics, visualization and datasets | pass | paper direction remains tied to `CV开题报告.pdf` | rerun after major route or paper-structure edits |
| Literature/citation audit | `audit_literature_citations.py` pass; `verified_literature.md`, `literature_gap_update_2026.md`, `citation_notes.md`, `web_search_notes.md` and two paper drafts cover 18 core works in both reference lists and inline citations | pass | related work and references have a checkable evidence boundary | rerun after any Related Work or reference edits |
| Public-facing style audit | `audit_submission_protocol.py` pass; paper draft, interim draft, share pack and presentation outline have no local absolute paths, script lists, internal CSV/status tokens, scheduler noise or English engineering evidence-status labels | pass | outward-facing materials are readable as paper artifacts, while reproducibility details stay in manifest/internal evidence docs | rerun after any paper-facing text edit |
| Prompt principle audit | `audit_prompt_principles.py` pass | pass | all subagent prompt/pending tasks explicitly include the non-lazy, non-conservative work principle | rerun after every prompt/task edit |
| Teacher/share pack | `teacher_share_pack.md` included in claim-text and asset audits | pass | use as a one-page reading guide with interim manuscript | update after any Gate 1/2/3/4A/4B result or major paper edit |
| Presentation outline | `presentation_outline.md` included in claim-text and asset audits | pass | use as the current 10-12 slide group-meeting/defense outline | update after any Gate 1/2/3/4A/4B result or major paper edit |
| Delta summary | `generate_delta_summary.py` writes `current_delta_summary.md`; release audit refreshes it | pass | cite current deltas only with stated evidence boundary | rerun after every metrics/profile update |
| Interim manuscript number audit | `audit_interim_submission_numbers.py` pass for `paper_interim_submission.md` | pass | clean interim draft numbers match CSV/profile evidence | rerun after every manuscript or table edit |
| Paper asset audit | `audit_paper_assets.py` pass for paper-facing Markdown figures | pass | current figure links exist and are non-empty | rerun after adding or moving figures |

## Immediate Queue

1. Patch public-facing manuscripts and paper-control documents with Gate 2/3
   evidence: KD is neutral/negative, controlled speed is complete.
2. Refresh aggregation, deltas, tick and readiness after manuscript edits:

```bash
python /root/data-tmp/workspace/02_experiments/scripts/aggregate_results.py \
  --out_md /root/data-tmp/workspace/04_paper/tables/aggregated_results.md
python /root/data-tmp/workspace/04_paper/scripts/generate_delta_summary.py
python /root/data-tmp/workspace/02_experiments/scripts/orchestrator_tick.py
```

3. Run the full release audit with KD integrity included:

```bash
bash /root/data-tmp/workspace/02_experiments/scripts/run_release_audits.sh \
  --add-integrity /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval \
  kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval \
  CAMO,COD10K,NC4K
```

## Writing Rules Until Gates Close

- Write Light B2-C64 as the accepted main student.
- Write ESCNet-B5 deltas with the clean same-protocol baseline now that Gate 1
  is complete; keep the historical row only as internal reference evidence.
- Write KD as completed and measured neutral/negative, not as effective.
- Write B0 and MobileMamba as high-risk external observations, not as results.
- Write controlled speed numbers only with the idle V100 profile condition.
