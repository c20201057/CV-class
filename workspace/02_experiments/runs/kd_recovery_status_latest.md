# KD Recovery Status Latest

- Updated UTC: `2026-06-15T09:33:50Z`
- Status: `not_observed_running`
- Gate: `Gate 2 KD`
- Evidence boundary: `pending_gate_no_kd_claims`
- Config: `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config_continue_epoch20_b6_w8_4gpu.yaml`
- Log: `/dev/shm/escnet_fast_kd/logs/train_continue_epoch20_b6_w8_4gpu_20260614T100610Z.log`
- Run dir: `/dev/shm/escnet_fast_kd/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu`
- Latest checkpoint: `epoch_120.pth`
- Final checkpoint status: `present`

## Latest Training

- Latest iter: epoch 120/120, iter 150/168, log time `2026-06-14 22:30:31,624`, total loss 1.592, KD loss 0.005
- Latest completed epoch: 120/120 with avg loss 1.485, log time `2026-06-14 22:30:46,549`
- Latest checkpoint save log: `epoch_120.pth` at `2026-06-14 22:30:46,788`

## Checkpoints

| checkpoint | bytes | mtime UTC |
| --- | ---: | --- |
| `epoch_40.pth` | 119674702 | `2026-06-14T11:01:14Z` |
| `epoch_60.pth` | 119674702 | `2026-06-14T11:53:17Z` |
| `epoch_80.pth` | 119674702 | `2026-06-14T12:46:34Z` |
| `epoch_100.pth` | 119675805 | `2026-06-14T13:39:14Z` |
| `epoch_120.pth` | 119675805 | `2026-06-14T14:30:46Z` |

## GPU Snapshot

- `0, Tesla V100-SXM2-16GB, 9897, 16384, 14`
- `1, Tesla V100-SXM2-16GB, 10041, 16384, 34`
- `2, Tesla V100-SXM2-16GB, 9921, 16384, 33`
- `3, Tesla V100-SXM2-16GB, 9895, 16384, 12`

## Process Snapshot

- none

## Acceptance Boundary

- Final checkpoint is present; do not claim KD improvement until CAMO/COD10K/NC4K probability eval, integrity checks, and release audits pass.
- Do not restart `watch_baseline_then_start_kd.sh` or duplicate `start_kd_full_train.sh` while this run is active.
