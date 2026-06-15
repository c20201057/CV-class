# Light-B2-C64 No-Edge-Guidance Ablation Status

- Updated UTC: `2026-06-14T16:30:31Z`
- Status: `running_not_accepted`
- Code: `/root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64_no_edge_guidance`
- Config: `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_no_edge_guidance_e120_s42/config_no_edge_guidance_b6_w8_4gpu.yaml`
- Torchrun PID: `1001292`
- Sync watcher PID: `997609`
- Active log: `/dev/shm/escnet_ablation_no_edge/logs/train_no_edge_guidance_b6_w8_4gpu_20260614T162810Z.log`
- Local run: `/dev/shm/escnet_ablation_no_edge/runs/light_b2_c64_no_edge_guidance_e120_s42_b6_w8_4gpu`
- Persistent sync run: `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_no_edge_guidance_e120_s42/light_b2_c64_no_edge_guidance_e120_s42_b6_w8_4gpu`
- Boundary: B2-C64, edge head and edge loss retained, decoder edge guidance disabled with `disable_decoder_edge_guidance: true`.
- Runtime: four V100 GPUs, `batch_size=6`, `num_workers=8`, `persistent_workers=true`, `prefetch_factor=4`, `save_step=20`.
- Paper rule: no paper/table/abstract claim until 120-epoch checkpoint, three-dataset probability evaluation, profile and integrity/audit pass.

First attempt log `/dev/shm/escnet_ablation_no_edge/logs/train_no_edge_guidance_b6_w8_4gpu_20260614T162550Z.log` failed in epoch1 because DDP detected unused `decoder.De_conv*.dwconv.offset_edge.*` parameters after decoder edge guidance was disabled. The isolated code snapshot was patched so `disable_decoder_edge_guidance=true` prevents FEM from constructing edge-offset modules.
