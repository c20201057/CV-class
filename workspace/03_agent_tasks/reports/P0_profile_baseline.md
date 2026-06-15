# P0 Profile Baseline Report

任务 ID / 实验 ID: `P0_profile_baseline` / `baseline_escnet_b5_416_e120`

完成状态: pass

## 写入或修改文件

- `/root/data-tmp/workspace/02_experiments/scripts/profile_model.py`
- `/root/data-tmp/workspace/02_experiments/runs/profile_escnet_b5_416/profile.json`
- `/root/data-tmp/workspace/02_experiments/runs/profile_escnet_b5_416/profile_command.log`
- `/root/data-tmp/workspace/02_experiments/runs/profile_escnet_b5_416/smoke_profile_cpu.json`
- `/root/data-tmp/workspace/02_experiments/runs/profile_escnet_b5_416/random_init_smoke_cpu.json`
- `/root/data-tmp/workspace/02_experiments/runs/profile_escnet_b5_416/random_init_smoke_profiles.csv`
- `/root/data-tmp/workspace/02_experiments/tables/profiles.csv`
- `/root/data-tmp/workspace/03_agent_tasks/reports/P0_profile_baseline.md`

## 使用命令

正式 baseline profile:

```bash
python /root/data-tmp/workspace/02_experiments/scripts/profile_model.py \
  --repo /root/ESCNet \
  --config /root/ESCNet/config.yaml \
  --ckpt /root/ESCNet/checkpoints/escnet/epoch_120.pth \
  --out /root/data-tmp/workspace/02_experiments/runs/profile_escnet_b5_416/profile.json \
  --device cuda:0 \
  --warmup 20 \
  --repeat 50 \
  --exp-id baseline_escnet_b5_416_e120 \
  2>&1 | tee /root/data-tmp/workspace/02_experiments/runs/profile_escnet_b5_416/profile_command.log
```

无 checkpoint 随机初始化 smoke:

```bash
python /root/data-tmp/workspace/02_experiments/scripts/profile_model.py \
  --repo /root/ESCNet \
  --config /root/ESCNet/config.yaml \
  --out /root/data-tmp/workspace/02_experiments/runs/profile_escnet_b5_416/random_init_smoke_cpu.json \
  --device cpu \
  --warmup 0 \
  --repeat 1 \
  --exp-id smoke_random_init_cpu \
  --profiles-csv /root/data-tmp/workspace/02_experiments/runs/profile_escnet_b5_416/random_init_smoke_profiles.csv
```

## 使用数据/配置/checkpoint

- Repo: `/root/ESCNet`
- Config: `/root/ESCNet/config.yaml`
- Checkpoint: `/root/ESCNet/checkpoints/escnet/epoch_120.pth`
- Input: batch 1, `3x416x416`
- Device: `cuda:0`, Tesla V100-SXM2-16GB
- PyTorch/CUDA: `2.5.1+cu121` / `12.1`

## 关键结果

- Params: `99,903,234`
- Trainable params: `99,903,234`
- Model size: `381.169 MB`
- FLOPs status: `estimated`
- FLOPs: `258.043600386 GFLOPs`
- GMACs: `129.021800193`
- Latency: `62.9983 ms`
- FPS: `15.8734`
- Peak GPU memory: `829.771 MB`
- Warmup / repeat: `20 / 50`
- Checkpoint load: `loaded`, missing keys `0`, unexpected keys `0`
- Forward output: `out_edge` shape `[1, 1, 416, 416]`; mask list shapes `[1,1,13,13]`, `[1,1,26,26]`, `[1,1,52,52]`, `[1,1,416,416]`

## 证据路径

- Profile JSON: `/root/data-tmp/workspace/02_experiments/runs/profile_escnet_b5_416/profile.json`
- Command log: `/root/data-tmp/workspace/02_experiments/runs/profile_escnet_b5_416/profile_command.log`
- CSV table: `/root/data-tmp/workspace/02_experiments/tables/profiles.csv`
- Loaded-checkpoint CPU smoke JSON: `/root/data-tmp/workspace/02_experiments/runs/profile_escnet_b5_416/smoke_profile_cpu.json`
- Random-init smoke JSON: `/root/data-tmp/workspace/02_experiments/runs/profile_escnet_b5_416/random_init_smoke_cpu.json`

## 风险和异常

- `thop`, `ptflops`, `fvcore` are not installed. No new packages were installed.
- FLOPs are estimated via `torch.profiler.profile(with_flops=True)`. PyTorch profiler counts supported ops such as convolution and matrix multiplication; unsupported ops are not included. JSON records `flops_status: estimated`, method, package availability, and note.
- Formal latency/FPS were measured on a shared machine GPU and should be rerun under the final paper protocol if strict deployment comparability is required.

## 是否可入论文

only as initial profile. It contains the required efficiency fields and reproducible evidence, but final paper table should use the main controller's accepted profiling protocol.

## 建议下一步

Run the same tool for Light-ESCNet student candidates with identical `img_size`, device, warmup, and repeat, then aggregate baseline/student rows into the paper efficiency table.
