# Light-B2-C64 No-Edge-Supervision Ablation

- Status: `running_not_accepted`
- Updated UTC: `2026-06-15T04:48:00Z`
- Boundary: `structural_ablation_candidate`
- Code: `/root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64_no_edge_supervision`
- Config: `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_no_edge_supervision_e120_s42/config_no_edge_supervision_b6_w8_4gpu.yaml`
- Active log: `/dev/shm/escnet_ablation_no_edge_supervision/logs/train_no_edge_supervision_b6_w8_4gpu_20260615T044543Z.log`
- Local run: `/dev/shm/escnet_ablation_no_edge_supervision/runs/light_b2_c64_no_edge_supervision_e120_s42_b6_w8_4gpu`
- Persistent sync: `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_no_edge_supervision_e120_s42/light_b2_c64_no_edge_supervision_e120_s42_b6_w8_4gpu`
- Torchrun PID: `1256510`
- Sync watcher PID: `1259831`

## Experiment Definition

This branch keeps the Light-B2-C64 architecture and decoder edge guidance active
(`disable_decoder_edge_guidance=false`), but disables direct edge-GT supervision
by setting `edge_loss_weight=0.0`. The edge head can still receive gradients
through decoder-guided structure losses.

## Training Policy

- Runtime data: `/dev/shm/escnet_fast_kd/data/Train`
- Runtime outputs: `/dev/shm/escnet_ablation_no_edge_supervision/runs`
- Persistent outputs: `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_no_edge_supervision_e120_s42`
- Per-GPU batch size: `6`
- Data workers: `8`
- Checkpoint retention: every 20 epochs only (`save_step=20`)

## Acceptance Gate

Do not use this branch in the paper main table, abstract or conclusion until:

1. 120-epoch training finishes with `epoch_120.pth`.
2. CAMO/COD10K/NC4K probability eval finishes with metadata rows.
3. Profile/integrity checks pass.
4. Release audit passes after any metrics or manuscript changes.
