# KD Epoch20 Batch/Worker Probe Summary

- Updated UTC: 2026-06-14T10:10:57Z
- Purpose: speed up Gate 2 online-KD recovery without changing KD loss, teacher, augmentation, SyncBN, model, or evaluation protocol.
- Safe checkpoint used for all probes: `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_recover_epoch10_fast_shm_4gpu/latest_train_state.pth` (`epoch=20`, persisted on `/root/data-tmp`).
- Hot training data/output: `/dev/shm/escnet_fast_kd` for runtime speed; persisted evidence is synced under `/root/data-tmp/workspace/02_experiments/runs/`.

## Baseline Before Probe

- Previous active config: `config_resume_epoch10_fast_shm_4gpu.yaml`
- Previous setting: `batch_size=4`, `num_workers=4`, `steps/epoch=252`
- Observed epoch time from logs: about 3m44s-3m46s per epoch after teacher load.
- Checkpoint policy: `save_step=20`; epoch20 was saved and synced before stopping the old process.

## Probes

| Probe | Config | Steps/epoch | Outcome | Timing Evidence | Decision |
| --- | --- | ---: | --- | --- | --- |
| b6/w6 | `config_probe_epoch20_b6_w6_i120_4gpu.yaml` | 168 | completed, no OOM | iter0 17:57:33, iter50 17:58:20, iter100 17:59:06; 50 iters ~= 46.6s | viable |
| b6/w8 | `config_probe_epoch20_b6_w8_i120_4gpu.yaml` | 168 | completed, no OOM | iter0 18:03:01, iter50 18:03:47, iter100 18:04:33; 50 iters ~= 46.1s | selected |

## Active Continuation

- Active config: `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config_continue_epoch20_b6_w8_4gpu.yaml`
- Active run name: `kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu`
- Active log: `/dev/shm/escnet_fast_kd/logs/train_continue_epoch20_b6_w8_4gpu_20260614T100610Z.log`
- Active PID: `864536`
- Resumed correctly: `loaded_epoch=20, start_epoch=21`.
- Confirmed training: epoch21 iter100/168 at 2026-06-14 18:10:27.
- GPU memory after switch: about 11.2-11.4 GB per 16 GB V100.

## Boundary

This is recovery/speed evidence only. Gate 2 KD remains pending until final checkpoint, CAMO/COD10K/NC4K probability eval, integrity checks, and release audits pass. No KD improvement claim is allowed yet.
