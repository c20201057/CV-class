# Release Audit Latest

- Started UTC: `2026-06-15T01:09:02Z`
- Workspace: `/root/data-tmp/workspace`
- Metrics CSV: `/root/data-tmp/workspace/02_experiments/tables/metrics_all.csv`
- Dataset root: `/root/data-tmp/COD/Test`
- Log: `/root/data-tmp/workspace/04_paper/drafts/release_audit_latest.log`
- Overall status: pass

## Command

```bash
python /root/data-tmp/workspace/02_experiments/scripts/audit_paper_evidence.py --metrics_csv /root/data-tmp/workspace/02_experiments/tables/metrics_all.csv 
```

- Status: pass

## Command

```bash
python /root/data-tmp/workspace/04_paper/scripts/audit_claim_text.py 
```

- Status: pass

## Command

```bash
python /root/data-tmp/workspace/04_paper/scripts/audit_cv_report_alignment.py 
```

- Status: pass

## Command

```bash
python /root/data-tmp/workspace/04_paper/scripts/generate_delta_summary.py --metrics_csv /root/data-tmp/workspace/02_experiments/tables/metrics_all.csv 
```

- Status: pass

## Command

```bash
python /root/data-tmp/workspace/02_experiments/scripts/audit_light_final_metadata.py --metrics_csv /root/data-tmp/workspace/02_experiments/tables/metrics_all.csv 
```

- Status: pass

## Command

```bash
python /root/data-tmp/workspace/04_paper/scripts/audit_interim_submission_numbers.py --metrics_csv /root/data-tmp/workspace/02_experiments/tables/metrics_all.csv 
```

- Status: pass

## Command

```bash
python /root/data-tmp/workspace/04_paper/scripts/audit_paper_assets.py 
```

- Status: pass

## Command

```bash
python /root/data-tmp/workspace/04_paper/scripts/audit_camo_failure_case_numbers.py 
```

- Status: pass

## Command

```bash
python /root/data-tmp/workspace/04_paper/scripts/audit_claim_evidence_matrix.py 
```

- Status: pass

## Command

```bash
python /root/data-tmp/workspace/04_paper/scripts/audit_literature_citations.py 
```

- Status: pass

## Command

```bash
python /root/data-tmp/workspace/03_agent_tasks/prompts/audit_prompt_principles.py 
```

- Status: pass

## Command

```bash
python /root/data-tmp/workspace/03_agent_tasks/audit_task_board_consistency.py 
```

- Status: pass

## Command

```bash
python /root/data-tmp/workspace/02_experiments/scripts/audit_b0_status_consistency.py 
```

- Status: pass

## Command

```bash
python /root/data-tmp/workspace/02_experiments/scripts/audit_mobilemamba_status_consistency.py 
```

- Status: pass

## Command

```bash
python /root/data-tmp/workspace/02_experiments/scripts/audit_gpu_handoff_consistency.py 
```

- Status: pass

## Command

```bash
python /root/data-tmp/workspace/02_experiments/scripts/audit_gpu_runtime_state.py --metrics_csv /root/data-tmp/workspace/02_experiments/tables/metrics_all.csv 
```

- Status: pass

## Command

```bash
python /root/data-tmp/workspace/02_experiments/scripts/audit_route_decision_consistency.py 
```

- Status: pass

## Command

```bash
python /root/data-tmp/workspace/02_experiments/scripts/audit_goal_completion_matrix.py 
```

- Status: pass

## Command

```bash
python /root/data-tmp/workspace/04_paper/scripts/audit_gate_patch_readiness.py --metrics_csv /root/data-tmp/workspace/02_experiments/tables/metrics_all.csv 
```

- Status: pass

## Command

```bash
python /root/data-tmp/workspace/04_paper/scripts/audit_paper_delivery_manifest.py 
```

- Status: pass

## Command

```bash
python /root/data-tmp/workspace/03_agent_tasks/acceptance/audit_agent_acceptance_ledger.py 
```

- Status: pass

## Command

```bash
python /root/data-tmp/workspace/04_paper/scripts/audit_submission_protocol.py --metrics_csv /root/data-tmp/workspace/02_experiments/tables/metrics_all.csv 
```

- Status: pass

## Command

```bash
python /root/data-tmp/workspace/02_experiments/scripts/audit_release_audit_registry.py --release_report /root/data-tmp/workspace/04_paper/drafts/release_audit_latest.md 
```

- Status: pass

## Command

```bash
python /root/data-tmp/workspace/02_experiments/scripts/check_run_integrity.py --run_dir /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42_prob_eval_v2 --exp_id light_b2_c64_e120_s42_prob_eval_v2 --datasets CAMO\,COD10K\,NC4K --dataset_root /root/data-tmp/COD/Test --metrics_csv /root/data-tmp/workspace/02_experiments/tables/metrics_all.csv 
```

- Status: pass

## Command

```bash
python /root/data-tmp/workspace/02_experiments/scripts/check_run_integrity.py --run_dir /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_no_edge_guidance_e120_s42_prob_eval --exp_id light_b2_c64_no_edge_guidance_e120_s42_prob_eval --datasets CAMO\,COD10K\,NC4K --dataset_root /root/data-tmp/COD/Test --metrics_csv /root/data-tmp/workspace/02_experiments/tables/metrics_all.csv 
```

- Status: pass

## Final

- Finished UTC: `2026-06-15T01:09:06Z`
- Exit code: 0
- Overall status: `pass`
