# Orchestrator Tick Latest

- Updated UTC: `2026-06-15T09:33:50Z`
- Workspace: `/root/data-tmp/workspace`
- Release audit: `pass` (finished `2026-06-15T01:09:06Z`)

## Gate State

| Gate | Status | Action |
| --- | --- | --- |
| Light main result | pass | Use Light B2-C64 as current accepted student result. |
| Gate 1 clean baseline | pass | Upgrade Light-vs-ESCNet deltas to clean probability baseline. |
| Gate 2 KD | pass | Patch KD result into paper according to measured improvement/failure. |
| Gate 3 speed | pass | Patch controlled latency/FPS according to same-command idle profiles. |
| Gate 4A B0 | observation_only | Keep B0 out of main table, abstract and conclusion. |
| Gate 4B MobileMamba | observation_only | Keep MobileMamba-T2 out of main table, abstract and conclusion. |

## Current Runs

- Active train-like processes: 37
- Active GPU-like processes: 37
- B0 running: `false` (process lines: 0)
- MobileMamba-T2 running: `false` (process lines: 0)
- KD recovery running: `false` (process lines: 0)
- KD recovery config: `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config_continue_epoch20_b6_w8_4gpu.yaml`
- KD recovery log: `/dev/shm/escnet_fast_kd/logs/train_continue_epoch20_b6_w8_4gpu_20260614T100610Z.log`
- KD recovery status report: `/root/data-tmp/workspace/02_experiments/runs/kd_recovery_status_latest.md`
- KD recovery latest iter: epoch 120/120, iter 150/168, log time `2026-06-14 22:30:31,624`, total loss 1.592, KD loss 0.005
- KD recovery latest checkpoint: `epoch_120.pth`
- KD recovery final checkpoint: `present`
- MobileMamba-T2 latest iter: epoch 59/120, iter 200/252, log time `2026-06-14 13:15:35,193`
- MobileMamba-T2 latest result: epoch 50: S=0.7487, wF=0.6019, meanF=0.6482, meanE=0.8477, MAE=0.0465
- MobileMamba-T2 boundary: `external_dirty_tree_observation_only`
- B0 status updated: `2026-06-15T09:33:49Z`
- B0 latest iter: epoch 10/120, iter 250/252, log time `2026-06-14 13:59:16,338`
- B0 latest eval: epoch 10, log time `2026-06-14 13:59:17,446`, predictions `/root/data-tmp/preds_train/pvt_v2_b0/epoch_10`, status `metrics_appended`
- B0 latest result: epoch 120: S=0.8004, wF=0.6862, meanF=0.7203, meanE=0.8878, MAE=0.0350
- B0 boundary: `external_dirty_tree_observation_only`
- Gate 1 baseline run: `complete`
- Gate 1 stopped process lines: 0

## Watchers

| Watcher | Status | Process |
| --- | --- | --- |
| Gate 1 baseline watcher | missing | `` |
| Gate 1 resume watcher | missing | `` |
| Gate 2 KD watcher | missing | `` |
| B0 read-only watcher | missing | `` |
| MobileMamba read-only watcher | running | `530956       1 Ss    1-09:57:39 bash /root/data-tmp/workspace/02_experiments/scripts/watch_external_mobilemamba_progress.sh --poll_seconds 300` |

## GPU Snapshot

- `0, Tesla V100-SXM2-16GB, 9897, 16384, 65`
- `1, Tesla V100-SXM2-16GB, 10041, 16384, 77`
- `2, Tesla V100-SXM2-16GB, 9921, 16384, 76`
- `3, Tesla V100-SXM2-16GB, 9895, 16384, 74`

## Gate 1 Baseline Progress

- Run dir: `/root/data-tmp/workspace/02_experiments/runs/baseline_escnet_b5_clean_prob_e120`
- Completed result files: `CAMO,COD10K,NC4K`

| Dataset | GT | Pred PNG | Result | S | wF | meanF | meanE | MAE | Metrics Status |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| CAMO | 250 | 250 | yes | 0.881 | 0.842 | 0.864 | 0.933 | 0.043 | `clean_prob_re_eval_complete` |
| COD10K | 2026 | 2026 | yes | 0.877 | 0.802 | 0.824 | 0.938 | 0.021 | `clean_prob_re_eval_complete` |
| NC4K | 4121 | 4121 | yes | 0.897 | 0.857 | 0.878 | 0.942 | 0.029 | `clean_prob_re_eval_complete` |

## Accepted Core Result

- Light-ESCNet B2-C64 no-KD remains the accepted student result.
- Params: 29.81M vs baseline 99.90M.
- GMACs: 36.39 vs baseline 129.02.
- Light peak memory: 237.44 MB.
- Current Light-vs-ESCNet deltas use the clean probability baseline.

## Next Queue

1. Gate 1 baseline state is `complete`; do not duplicate the wrapper.
2. Gate 1 is complete; baseline/resume watchers are no longer required.
3. Gate 2 KD eval and Gate 3 controlled speed are complete. Patch the paper and delivery docs with the measured KD neutral/negative result and the controlled latency/FPS evidence, then rerun release audits.
4. Keep B0/MobileMamba external dirty-tree branches out of the main table unless their candidate integrity gates pass.
5. Re-run release audits after every metrics/profile/manuscript change.
