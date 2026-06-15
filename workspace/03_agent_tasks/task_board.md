# Agent Task Board

更新时间：2026-06-15T04:48:00Z / 2026-06-15 12:48:00 CST

工作准则：不偷懒，不因为怕风险而保守；高风险路线可以推进，但必须隔离写入范围、留下证据路径，并经主控验收后才能影响论文主张。

## Current Dispatch Note

- 用户已授权进入下一阶段结构分支消融；当前 Light-B2-C64 `no_edge_supervision` 四卡训练正在 GPU0-3 运行，torchrun PID 1256510，同步 watcher PID 1259831。该分支仅为 active ablation，训练、评测和验收完成前不能进入论文主表、摘要或结论。
- 上一阶段 Light-B2-C64 `no_edge_guidance` 已完成 120 epoch、CAMO/COD10K/NC4K probability eval、integrity 和 release audit。结果低于 accepted Light-B2-C64，不能进主表/摘要/结论，只能作为“移除 decoder edge guidance 会退化”的结构消融证据候选。
- Gate 1 clean baseline 已 complete；不要再恢复或重复启动 baseline NC4K。
- MobileMamba-T2 只读 watcher 已启动，PID 530956；新 agent 只读状态即可，不要重复启动 watcher 或抢占训练。脚本已支持未来重启时用 `--sync_on_change` 自动触发 observation sync。
- KD watcher 已完成接力后退出；当前不要重启 watcher，也不要重复调用 `start_kd_full_train.sh` 或 `start_kd_fast_shm_train.sh`。
- 所有新 agent 行动前先读 `00_project/orchestrator_tick_latest.md`；不要重复启动 baseline，也不要重复启动 KD recovery。
- 所有 agent 交付被主控验收后必须更新 `03_agent_tasks/acceptance/agent_acceptance_ledger.md`，并通过 `audit_agent_acceptance_ledger.py`；被拒收或仅 observation 的结果也要进账本。

## In Progress By Main Orchestrator

Short status anchor: `00_project/orchestrator_tick_latest.md`; fallback:
`00_project/current_run_snapshot.md`.

| Task | Owner | Status | Output |
| --- | --- | --- | --- |
| Master plan/workflow/prompts | main-orchestrator | done | `00_project/master_plan.md`, `03_agent_tasks/prompts/MASTER_TARGET_PROMPT.md`, `03_agent_tasks/prompts/DISPATCH_PACKETS.md` |
| ESCNet/code/workspace audit | main-orchestrator + explorer agents | done | `00_project/project_profile.md`, `05_reviews/subagent_reviews.md` |
| Global route integration | main-orchestrator | active | `00_project/route_decision.md`, `04_paper/drafts/paper_draft.md` |
| Goal completion tracking | main-orchestrator | active | `00_project/goal_completion_matrix.md`, `00_project/orchestrator_tick_latest.md` |

## Running

| Priority | Task | Agent | Write Scope |
| --- | --- | --- | --- |
| P0 | Light-B2-C64 no-edge-supervision structural ablation | main | running on GPU0-3, torchrun PID 1256510; sync watcher PID 1259831; code `02_experiments/code/light_escnet_b2_c64_no_edge_supervision`; config `02_experiments/runs/light_b2_c64_no_edge_supervision_e120_s42/config_no_edge_supervision_b6_w8_4gpu.yaml`; active log `/dev/shm/escnet_ablation_no_edge_supervision/logs/train_no_edge_supervision_b6_w8_4gpu_20260615T044543Z.log`; local output `/dev/shm/escnet_ablation_no_edge_supervision/runs/light_b2_c64_no_edge_supervision_e120_s42_b6_w8_4gpu`; sync output `02_experiments/runs/light_b2_c64_no_edge_supervision_e120_s42/light_b2_c64_no_edge_supervision_e120_s42_b6_w8_4gpu`; `disable_decoder_edge_guidance=false`, `edge_loss_weight=0.0`, `save_step=20`; not accepted until full train/eval/profile/integrity |
| P1 | PVTv2-B0 online KD extreme branch | external/main | `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0`; `external_dirty_tree_observation_only`; not observed running after user-authorized stop; latest completed COD10K intermediate row is epoch120 S=.8004/wF=.6862/meanF=.7203/meanE=.8878/MAE=.0350; best observed row remains epoch100 S=.8014/wF=.6882/meanF=.7221/meanE=.8899/MAE=.0346, still below accepted Light B2-C64; live state is tracked in `b0_external_status_latest.md` |
| P1 | MobileMamba-T2 online KD external branch | external/main | `/root/data-tmp/ESCNet/checkpoints/mobilemamba_t2`; `external_dirty_tree_observation_only`; not observed running; live epoch/iter delegated to `orchestrator_tick_latest.md` and `mobilemamba_t2_external_status_latest.md`; MobileMamba latest/highest-S observation row is epoch50 COD10K S=.7487/wF=.6019/meanF=.6482/meanE=.8477/MAE=.0465; no accepted checkpoint yet |

## Completed

| Priority | Task | Agent | Result |
| --- | --- | --- | --- |
| P0 | Baseline profiling | Pauli | pass, initial profile accepted |
| P0 | Evaluation suite | Ptolemy | pass, tool accepted; smoke metric rejected for paper |
| P0 | Light B2-C64 implementation | Dewey | pass, B2 pretrained smoke verified |
| P1 | Probability inference | Huygens | pass, tool accepted; found teacher checkpoint mismatch |
| P1 | Paper narrative review | Aristotle | pass, writing boundaries and table plan accepted |
| P1 | KD proposal | Poincare | pass, online KD plan accepted |
| P1 | Visual grid script | main | pass, baseline CAMO smoke grid generated |
| P0 | Full train Light B2-C64 | main | pass, 120 epoch + profile + CAMO/COD10K/NC4K probability eval accepted |
| P1 | KD B2-C64 smoke | main | pass, batch 1/batch 4 smoke accepted; full train interrupted at epoch 5 by SIGKILL |
| P1 | KD recovery config audit | Lagrange | pass, recovery configs accepted |
| P1 | Literature/gap update 2026 | Schrodinger | pass |
| P1 | Experiment gap audit | Lagrange | pass |
| P1 | Paper revision plan | Feynman | pass |
| P1 | Paper evidence audit | Lagrange | pass, baseline/FPS/KD boundaries tightened |
| P1 | Paper baseline boundary audit | Epicurus | pass, historical/reference/final evidence boundary tightened |
| P0 | Clean baseline source snapshot | main | pass, `baseline_escnet_clean`; strict checkpoint load missing=0/unexpected=0 |
| P0 | Paper finalization gates | main | pass, `04_paper/drafts/finalization_gates.md` defines required evidence before final claims |
| P0 | Claim/evidence audit | main | pass, `04_paper/drafts/claim_evidence_audit.md` maps current paper claims to evidence and gates |
| P0 | Paper final patch plan | main | pass, `04_paper/drafts/paper_final_patch_plan.md` maps Gate 1/2/3/4A/4B results to execution order, paper/table/figure edits, external-facing packet sync and release audit commands |
| P0 | Metrics evidence metadata gate | main | pass, `metrics_all.csv` and runners carry protocol/repo_boundary/checkpoint/status |
| P0 | GPU queue runbook | main | pass, `02_experiments/scripts/GPU_QUEUE.md` is authoritative queue while MobileMamba occupies GPUs and after it releases them |
| P0 | KD safe recovery launcher | main | pass, `02_experiments/scripts/start_kd_full_train.sh` refuses busy GPUs and defaults to epoch-5 recovery |
| P0 | Clean baseline idle watcher | main | pass, `02_experiments/scripts/watch_gpu_then_start_baseline_clean.sh` waits for idle GPUs before Gate 1 baseline eval and checks `metrics_all.csv` completion instead of only run-directory existence |
| P0 | Submission protocol checklist | main | pass, `04_paper/drafts/submission_protocol_checklist.md` defines final table, claim and reproducibility acceptance |
| P0 | Gate result acceptance runbook | main | pass, `03_agent_tasks/acceptance/gate_result_acceptance_runbook.md` defines post-Gate integrity, paper patch and audit steps for GPU queue handoff |
| P0 | Agent acceptance ledger | main | pass, `03_agent_tasks/acceptance/agent_acceptance_ledger.md` plus `audit_agent_acceptance_ledger.py` records main-controller verdicts for subagent reports/reviews and is wired into release audit |
| P0 | Paper evidence audit script | main | pass, `02_experiments/scripts/audit_paper_evidence.py` checks final/status/table metadata boundaries |
| P0 | Submission protocol audit | Lagrange | pass after patch, review warnings converted into checklist/script hard gates |
| P0 | Claim text audit script | main | pass, `04_paper/scripts/audit_claim_text.py` scans paper-facing deliverables for over-claims |
| P0 | Release audit wrapper | main | pass, `02_experiments/scripts/run_release_audits.sh` runs evidence, claim and final-run integrity gates; lock/tmp handling hardened |
| P0 | Release audit registry | main | pass, `02_experiments/scripts/RELEASE_AUDIT_REGISTRY.md` and `02_experiments/scripts/audit_release_audit_registry.py` keep fixed release gates, reports and control docs aligned; wired into release audit |
| P1 | External B0 monitor | main | pass, `02_experiments/scripts/summarize_external_b0.py` writes read-only dirty-branch status |
| P1 | External B0 progress watcher | main | pass, `02_experiments/scripts/watch_external_b0_progress.sh` logs read-only iter/result/checkpoint changes during long B0 training |
| P1 | External B0 dirty snapshot | main | pass, `02_experiments/scripts/snapshot_external_b0_dirty_tree.sh`; latest observation snapshot at `02_experiments/code/external_b0_dirty_snapshot_20260613T200614Z_epoch70_metrics_observation` |
| P0 | Baseline-to-KD queue watcher | main | pass, `02_experiments/scripts/watch_baseline_then_start_kd.sh` waits for clean baseline completion before KD recovery |
| P0 | Paper gate patch matrix and delta summary | main | pass, `paper_gate_patch_matrix.md` plus `generate_delta_summary.py` keep Gate 1/2/3/4A/4B final patch actions and current deltas explicit |
| P0 | Paper claim-evidence matrix | main | pass, `paper_claim_evidence_matrix.md` plus `audit_claim_evidence_matrix.py` keep claim-level evidence paths checkable |
| P0 | CV report alignment audit | main | pass, `audit_cv_report_alignment.py` checks current workflow/paper alignment with `CV开题报告.pdf`; wired into release audit |
| P0 | Literature citation audit | main | pass, `audit_literature_citations.py` checks verified literature notes and 18 core references in paper drafts; wired into release audit |
| P0 | Agent prompt principle audit | main | pass, `prompts/audit_prompt_principles.py` checks prompts/pending tasks for the non-lazy, non-conservative work principle |
| P0 | Task-board consistency audit | main | pass, `03_agent_tasks/audit_task_board_consistency.py` checks task board paths, dispatch sections, planned run boundaries and queue markers; wired into release audit and accepted in ledger A22 |
| P0 | Orchestrator tick entrypoint | main | pass, `02_experiments/scripts/orchestrator_tick.py` writes `00_project/orchestrator_tick_latest.md` and `00_project/orchestrator_tick_latest.json` for all agents before they act; it now refreshes KD recovery status from `02_experiments/scripts/summarize_kd_recovery.py` |
| P0 | GPU handoff consistency audit | main | pass, `02_experiments/scripts/audit_gpu_handoff_consistency.py` checks orchestrator tick and handoff docs for Gate 1/KD queue consistency; wired into release audit |
| P0 | GPU runtime state audit | main | pass, `02_experiments/scripts/audit_gpu_runtime_state.py` checks live paused Gate 1 wrapper, resume watcher target PID, KD watcher, MobileMamba process state and premature KD launch risk; wired into release audit |
| P0 | Route decision consistency audit | main | pass, `02_experiments/scripts/audit_route_decision_consistency.py` checks route/gate/status docs against latest tick for B0/MobileMamba/Gate state; wired into release audit |
| P0 | Goal completion matrix | main | pass, `00_project/goal_completion_matrix.md` maps original user goal to proven evidence, pending gates, observation-only branches and final completion criteria |
| P0 | Paper delivery manifest | main | pass, `04_paper/drafts/paper_delivery_manifest.md` plus `04_paper/scripts/audit_paper_delivery_manifest.py` define and audit the current external-facing files, internal evidence, figure assets and withheld claims; latest report `04_paper/drafts/paper_delivery_manifest_audit_latest.md`; wired into release audit |
| P0 | Clean baseline probability full re-eval | main | pass, `02_experiments/runs/baseline_escnet_b5_clean_prob_e120`; CAMO/COD10K/NC4K complete with `clean_prob_re_eval_complete`; Gate 1 clean baseline accepted |
| P0 | KD recovery read-only status monitor | main | pass, `02_experiments/scripts/summarize_kd_recovery.py` writes `02_experiments/runs/kd_recovery_status_latest.md`; report shows latest iter/checkpoint/process/GPU snapshot and keeps evidence boundary `pending_gate_no_kd_claims` |
| P1 | External MobileMamba-T2 monitor | main | pass, `02_experiments/scripts/summarize_external_mobilemamba.py` writes read-only dirty-branch status |
| P1 | External MobileMamba-T2 progress watcher | main | pass, `02_experiments/scripts/watch_external_mobilemamba_progress.sh` logs read-only iter/result/checkpoint changes during long MobileMamba training; script now supports opt-in `--sync_on_change` observation sync; PID 530956 at latest tick is the existing read-only watcher |
| P1 | External MobileMamba-T2 observation sync | main | pass, `02_experiments/scripts/sync_mobilemamba_observation_state.py` refreshes MobileMamba status, tick, internal control docs and consistency audits after new COD10K rows/checkpoints without starting, stopping or signaling training; latest report `02_experiments/runs/mobilemamba_observation_sync_latest.md` |
| P1 | External MobileMamba-T2 candidate gate | main | pass, `02_experiments/scripts/start_mobilemamba_candidate_eval.sh --dry_run` verifies snapshot/profile/prob-eval/integrity/release-audit command chain; real run refuses busy GPUs by default |
| P0 | Teacher share pack | main | pass, `04_paper/drafts/teacher_share_pack.md` gives one-page sharing guidance and is covered by claim/asset audits |
| P0 | Presentation outline | main | pass, `04_paper/drafts/presentation_outline.md` gives a 10-12 slide group-meeting/defense outline and is covered by claim/asset audits |
| P0 | Paper gate patch matrix review | Feynman + main follow-up | pass, `05_reviews/paper_gate_patch_matrix_review_feynman.md` confirms Gate 1/2/3 patch matrix coverage; main follow-up added Gate 4A B0 and Gate 4B MobileMamba observation-candidate patch/readiness gates |
| P1 | Light B2-C64 narrative bridge review | Feynman | pass, `05_reviews/light_b2_c64_narrative_bridge_review_feynman.md` recommendations adopted in `paper_interim_submission.md` and `method_light_b2_c64.md` |

## Ready / Pending

| Priority | Task | Prompt | Write Scope | Acceptance |
| --- | --- | --- | --- | --- |
| P0 | GPU queue operator / gate validator | `03_agent_tasks/prompts/DISPATCH_PACKETS.md#p0-gpu-queue-operator-and-gate-validator` + `03_agent_tasks/pending/P0_gpu_queue_operator.md` + `03_agent_tasks/pending/P0_gate1_kd_handoff_card.md` + `03_agent_tasks/acceptance/gate_result_acceptance_runbook.md` | KD/profile run dirs under `02_experiments/runs/` | take over after external B0/GPU-like work releases GPUs; do not duplicate completed Gate 1 wrapper; enforce Gate 2/3 acceptance and paper回填 without dirty baseline leakage |
| P0 | KD probability eval | `03_agent_tasks/prompts/distillation_prompt.md` + `03_agent_tasks/pending/P1_distill_light_b2_c64.md` | planned: `02_experiments/runs/kd_light_b2_c64_e120_s42_recover_b2w0_4gpu_prob_eval` | after recovery checkpoint, three-dataset probability eval with metadata |
| P0 | Controlled speed re-profile | `03_agent_tasks/prompts/engineer_profile_prompt.md` | profile run dirs under `02_experiments/runs/` | idle GPU baseline vs Light latency/FPS |
| P1 | Visual grid final figures | `03_agent_tasks/prompts/visualization_prompt.md` + `03_agent_tasks/pending/P1_visual_grid.md` | `02_experiments/figures` | Add Light/KD columns after final predictions; B0/MobileMamba only after Gate 4A/4B candidate evidence |
| P1 | B2-C128 or B5-C64 ablation | `pending/P1_ablation_configs.md` | new isolated run dir | choose after current no-edge-supervision ablation has final evidence |

## Dispatch Rules

1. 每次派发都先附加 `prompts/MASTER_TARGET_PROMPT.md`。
2. 每个 agent 只拥有一个清晰写入范围。
3. P0 工程任务可并行；完整训练任务应由主控统一分配 GPU。
4. 任何实验目录已存在时，agent 必须停止并报告，不允许覆盖。
5. agent 回报先进入 `03_agent_tasks/reports/`，主控验收后再移动任务状态。

## GPU Queue

| Queue | Suggested GPU | Task |
| --- | --- | --- |
| current | GPU0-3 | Light-B2-C64 no-edge-supervision ablation is running; monitor log/checkpoints and do not duplicate |
| complete-eval | none | Gate 1 clean baseline complete; `resume_stopped_prob_eval_when_gpu_idle.sh` retained as historical marker only; do not duplicate `start_baseline_prob_eval_clean.sh` |
| next-train | none | wait for current no-edge-supervision ablation to finish or fail with evidence |
| next-eval-2 | 0 after no-edge-supervision checkpoint | no-edge-supervision probability eval on CAMO/COD10K/NC4K, then profile and integrity |
| side-ablation | free GPU only | B2-C128 / B5-C64 after current ablation has a checkpoint/evidence boundary |
