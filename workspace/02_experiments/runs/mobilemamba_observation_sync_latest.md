# MobileMamba Observation Sync

- Status: `pass`
- Updated UTC: `2026-06-14T03:46:18Z`
- Latest row: `epoch40 COD10K S=.7462/wF=.5980/meanF=.6446/meanE=.8453/MAE=.0472`
- Best-S row: `epoch40 COD10K S=.7462/wF=.5980/meanF=.6446/meanE=.8453/MAE=.0472`
- Boundary: `external_dirty_tree_observation_only`

## Changed Docs

- `00_project/current_run_snapshot.md`
- `00_project/goal_completion_matrix.md`
- `00_project/orchestrator_status.md`
- `00_project/resume_handoff.md`
- `00_project/route_decision.md`
- `02_experiments/scripts/GPU_QUEUE.md`
- `03_agent_tasks/acceptance/agent_acceptance_ledger.md`
- `03_agent_tasks/pending/P0_gate1_kd_handoff_card.md`
- `03_agent_tasks/task_board.md`
- `04_paper/drafts/evidence_index.md`
- `04_paper/drafts/finalization_gates.md`
- `04_paper/drafts/paper_claim_evidence_matrix.md`
- `04_paper/drafts/paper_delivery_manifest.md`
- `04_paper/drafts/paper_submission_packet.md`
- `04_paper/drafts/paper_submission_readiness.md`
- `04_paper/drafts/writing_status.md`

## Notes

- none

## Steps

- refresh_external_mobilemamba_status: `python /root/data-tmp/workspace/02_experiments/scripts/summarize_external_mobilemamba.py`
- refresh_orchestrator_tick: `python /root/data-tmp/workspace/02_experiments/scripts/orchestrator_tick.py --no_refresh_mobilemamba`
- audit_mobilemamba_status_consistency: `python /root/data-tmp/workspace/02_experiments/scripts/audit_mobilemamba_status_consistency.py`
- audit_gpu_handoff_consistency: `python /root/data-tmp/workspace/02_experiments/scripts/audit_gpu_handoff_consistency.py`
- audit_route_decision_consistency: `python /root/data-tmp/workspace/02_experiments/scripts/audit_route_decision_consistency.py`
- audit_goal_completion_matrix: `python /root/data-tmp/workspace/02_experiments/scripts/audit_goal_completion_matrix.py`
- audit_paper_delivery_manifest: `python /root/data-tmp/workspace/04_paper/scripts/audit_paper_delivery_manifest.py`
- audit_claim_evidence_matrix: `python /root/data-tmp/workspace/04_paper/scripts/audit_claim_evidence_matrix.py`
- audit_submission_protocol: `python /root/data-tmp/workspace/04_paper/scripts/audit_submission_protocol.py`
- audit_agent_acceptance_ledger: `python /root/data-tmp/workspace/03_agent_tasks/acceptance/audit_agent_acceptance_ledger.py`
- audit_task_board_consistency: `python /root/data-tmp/workspace/03_agent_tasks/audit_task_board_consistency.py`
