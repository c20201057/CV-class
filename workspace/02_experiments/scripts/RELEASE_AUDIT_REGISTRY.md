# Release Audit Registry

更新时间：2026-06-14T03:30:00Z / 2026-06-14 11:30:00 CST

用途：登记 `run_release_audits.sh` 的固定非 GPU 审计门禁。每次新增、删除或重命名 release audit 固定项时，必须同步本表、相关证据文档和 agent ledger，再运行 `audit_release_audit_registry.py` 与完整 release audit。

边界：`--add-integrity` 是动态 probability-run 完整性检查，不在本 registry 固定表中逐项登记；它由 `release_audit_latest.md` 中的命令和 `check_run_integrity.py` 输出证明。

| Order | Script | Report | Guarded Surface | Control Docs |
| ---: | --- | --- | --- | --- |
| 1 | `02_experiments/scripts/audit_paper_evidence.py` | `04_paper/drafts/paper_evidence_audit_latest.md` | metrics metadata, final/reference evidence boundary | `04_paper/drafts/evidence_index.md`, `04_paper/drafts/writing_status.md` |
| 2 | `04_paper/scripts/audit_claim_text.py` | `04_paper/drafts/claim_text_audit_latest.md` | paper-facing over-claims | `04_paper/drafts/evidence_index.md`, `04_paper/drafts/writing_status.md` |
| 3 | `04_paper/scripts/audit_cv_report_alignment.py` | `04_paper/drafts/cv_report_alignment_audit_latest.md` | CV proposal alignment | `00_project/goal_completion_matrix.md`, `04_paper/drafts/evidence_index.md` |
| 4 | `04_paper/scripts/generate_delta_summary.py` | `04_paper/drafts/current_delta_summary.md` | current Light-vs-baseline delta summary | `04_paper/drafts/paper_submission_packet.md`, `04_paper/drafts/evidence_index.md` |
| 5 | `02_experiments/scripts/audit_light_final_metadata.py` | `04_paper/drafts/light_final_metadata_audit_latest.md` | accepted Light final run metadata | `04_paper/drafts/paper_submission_packet.md`, `04_paper/drafts/evidence_index.md` |
| 6 | `04_paper/scripts/audit_interim_submission_numbers.py` | `04_paper/drafts/interim_submission_number_audit_latest.md` | interim manuscript numbers | `04_paper/drafts/evidence_index.md`, `04_paper/drafts/writing_status.md` |
| 7 | `04_paper/scripts/audit_paper_assets.py` | `04_paper/drafts/paper_asset_audit_latest.md` | paper-facing image assets | `04_paper/drafts/evidence_index.md`, `04_paper/drafts/writing_status.md` |
| 8 | `04_paper/scripts/audit_camo_failure_case_numbers.py` | `04_paper/drafts/camo_failure_case_number_audit_latest.md` | CAMO failure-case statistics | `04_paper/drafts/evidence_index.md`, `04_paper/drafts/writing_status.md` |
| 9 | `04_paper/scripts/audit_claim_evidence_matrix.py` | `04_paper/drafts/claim_evidence_matrix_audit_latest.md` | claim-evidence path matrix | `04_paper/drafts/paper_claim_evidence_matrix.md`, `04_paper/drafts/evidence_index.md` |
| 10 | `04_paper/scripts/audit_literature_citations.py` | `04_paper/drafts/literature_citation_audit_latest.md` | literature/citation coverage | `04_paper/drafts/citation_manifest.md`, `04_paper/drafts/evidence_index.md` |
| 11 | `03_agent_tasks/prompts/audit_prompt_principles.py` | `03_agent_tasks/prompts/prompt_principles_audit_latest.md` | prompt non-lazy/non-conservative principle | `03_agent_tasks/task_board.md`, `04_paper/drafts/writing_status.md` |
| 12 | `03_agent_tasks/audit_task_board_consistency.py` | `03_agent_tasks/task_board_consistency_audit_latest.md` | task-board path and queue consistency | `03_agent_tasks/task_board.md`, `03_agent_tasks/acceptance/agent_acceptance_ledger.md` |
| 13 | `02_experiments/scripts/audit_b0_status_consistency.py` | `04_paper/drafts/b0_status_consistency_audit_latest.md` | B0 dirty observation boundary | `04_paper/drafts/evidence_index.md`, `04_paper/drafts/paper_submission_packet.md` |
| 14 | `02_experiments/scripts/audit_mobilemamba_status_consistency.py` | `04_paper/drafts/mobilemamba_status_consistency_audit_latest.md` | MobileMamba dirty observation boundary | `04_paper/drafts/evidence_index.md`, `04_paper/drafts/paper_submission_packet.md` |
| 15 | `02_experiments/scripts/audit_gpu_handoff_consistency.py` | `00_project/gpu_handoff_consistency_audit_latest.md` | GPU handoff documents | `03_agent_tasks/task_board.md`, `04_paper/drafts/evidence_index.md` |
| 16 | `02_experiments/scripts/audit_gpu_runtime_state.py` | `00_project/gpu_runtime_state_audit_latest.md` | live GPU watcher and paused-wrapper state | `03_agent_tasks/task_board.md`, `03_agent_tasks/acceptance/agent_acceptance_ledger.md` |
| 17 | `02_experiments/scripts/audit_route_decision_consistency.py` | `00_project/route_decision_consistency_audit_latest.md` | route/gate status consistency | `00_project/route_decision.md`, `00_project/goal_completion_matrix.md` |
| 18 | `02_experiments/scripts/audit_goal_completion_matrix.py` | `00_project/goal_completion_matrix_audit_latest.md` | original-goal completion boundary | `00_project/goal_completion_matrix.md`, `04_paper/drafts/writing_status.md` |
| 19 | `04_paper/scripts/audit_gate_patch_readiness.py` | `04_paper/drafts/gate_patch_readiness_latest.md` | Gate 1/2/3/4A/4B patch readiness | `04_paper/drafts/paper_gate_patch_matrix.md`, `04_paper/drafts/paper_final_patch_plan.md` |
| 20 | `04_paper/scripts/audit_paper_delivery_manifest.py` | `04_paper/drafts/paper_delivery_manifest_audit_latest.md` | paper delivery package boundary | `04_paper/drafts/paper_delivery_manifest.md`, `04_paper/drafts/paper_submission_packet.md` |
| 21 | `03_agent_tasks/acceptance/audit_agent_acceptance_ledger.py` | `03_agent_tasks/acceptance/agent_acceptance_ledger_audit_latest.md` | agent acceptance ledger | `03_agent_tasks/acceptance/agent_acceptance_ledger.md`, `03_agent_tasks/task_board.md` |
| 22 | `04_paper/scripts/audit_submission_protocol.py` | `04_paper/drafts/submission_protocol_audit_latest.md` | final submission protocol | `04_paper/drafts/submission_protocol_checklist.md`, `04_paper/drafts/paper_submission_packet.md` |
| 23 | `02_experiments/scripts/audit_release_audit_registry.py` | `02_experiments/scripts/release_audit_registry_audit_latest.md` | release audit registry and wrapper alignment | `02_experiments/scripts/RELEASE_AUDIT_REGISTRY.md`, `02_experiments/scripts/run_release_audits.sh` |
