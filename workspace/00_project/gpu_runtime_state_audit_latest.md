# GPU Runtime State Audit

- Status: `pass`
- Tick JSON: `/root/data-tmp/workspace/00_project/orchestrator_tick_latest.json`
- Metrics CSV: `/root/data-tmp/workspace/02_experiments/tables/metrics_all.csv`
- Errors: 0
- Warnings: 0

## Errors

- none

## Warnings

- none

## Notes

- tick updated: 2026-06-15T04:41:06Z
- log ok: /root/data-tmp/workspace/02_experiments/runs/watch_gpu_then_start_baseline_clean.log
- log ok: /root/data-tmp/workspace/02_experiments/runs/resume_stopped_baseline_prob_eval_when_gpu_idle.log
- log ok: /root/data-tmp/workspace/02_experiments/runs/watch_baseline_then_start_kd.log
- log ok: /root/data-tmp/workspace/02_experiments/runs/watch_external_mobilemamba_progress.log
- baseline metrics complete; runtime audit allows Gate 1 -> KD handoff
- baseline watcher count after completion: 0
- resume watcher count after baseline completion: 0
- KD watcher is absent because KD recovery has launched/completed: watchers=0
- KD recovery process is allowed because baseline metrics are complete
- KD recovery final checkpoint exists; Gate 2 eval/acceptance must decide whether it is paper evidence: /dev/shm/escnet_fast_kd/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu/epoch_120.pth
- KD recovery final checkpoint exists; Gate 2 eval/acceptance must decide whether it is paper evidence: /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu/epoch_120.pth
- MobileMamba is not marked running in tick; Gate 1 handoff may be imminent
