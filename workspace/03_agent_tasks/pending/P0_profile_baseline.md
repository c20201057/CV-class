# P0 Task: Profile ESCNet Baseline

## Agent Role

Profiling 工程 agent。

## Goal

实现并运行 `profile_model.py`，为 ESCNet-B5 epoch 120 输出论文所需效率指标。

## Work Principle

不偷懒，不因为怕风险而保守。效率数字必须尽量真实跑出；FLOPs/latency 等失败时要记录原因和命令，不能静默留空或用不可追溯数字代替。

## Scope

只写：

- `/root/data-tmp/workspace/02_experiments/scripts/profile_model.py`
- `/root/data-tmp/workspace/02_experiments/runs/profile_escnet_b5_416/`
- `/root/data-tmp/workspace/02_experiments/tables/profiles.csv`

不要修改 `/root/ESCNet`。

## Inputs

- Repo for current clean baseline reruns: `/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean`
- Config for current clean baseline reruns: `/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean/config.local.yaml`
- Checkpoint for current clean baseline reruns: `/root/data-tmp/epoch_120.pth`
- Input size: `416`
- Device: CUDA 0

历史注意：早期 profile 曾使用 `/root/ESCNet` 和
`/root/ESCNet/checkpoints/escnet/epoch_120.pth`。当前 `/root/ESCNet` 是 dirty
工作树，且该 checkpoint 是后续重训产物；新任务不得把它当作 clean baseline。

## Required Outputs

- `profile.json`
- Updated `profiles.csv`
- Command log
- Short report under `03_agent_tasks/reports/`

## Acceptance

见 `03_agent_tasks/acceptance/acceptance_criteria.md` 和 `02_experiments/scripts/SCRIPT_SPECS.md`。
