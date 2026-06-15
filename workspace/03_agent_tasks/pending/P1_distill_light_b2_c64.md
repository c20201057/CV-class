# P1 Task: Distill Light-ESCNet B2-C64

## Agent Role

蒸馏实验 agent。

## Goal

在 Light-ESCNet B2-C64 可训练后，使用 ESCNet-B5 epoch 120 作为 teacher 训练 student。

## Work Principle

不偷懒，不因为怕风险而保守。KD 是高风险补偿主线，不能因一次中断就放弃；每次降级或失败都必须留下 checkpoint 状态、日志、命令和下一步方案。

## Inputs

- Teacher checkpoint: `/root/data-tmp/epoch_120.pth`
- Student code/config: 由 `P0_light_b2_c64_impl` 产出
- Dataset: `/root/data-tmp/COD/Train`

## Current Implementation

- Proposal: `/root/data-tmp/workspace/02_experiments/proposals/kd_light_escnet/`
- Code copy: `/root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64/`
- Config: `/root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64/configs/kd_light_b2_c64.yaml`
- Run dir: `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/`
- Current valid recovery checkpoint: `/dev/shm/escnet_fast_kd/checkpoints/latest_train_state_epoch_10.pth`
- Safe recovery launcher: `/root/data-tmp/workspace/02_experiments/scripts/start_kd_fast_shm_train.sh`
- Default recovery config: `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config_resume_epoch10_fast_shm_4gpu.yaml`
- Default recovery output run: `/dev/shm/escnet_fast_kd/runs/kd_light_b2_c64_e120_s42_recover_epoch10_fast_shm_4gpu/`
- GPU queue: `/root/data-tmp/workspace/02_experiments/scripts/GPU_QUEUE.md`

## Output

- Original partial run dir: `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/`
- Recovery run dir: `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_recover_b2w0_4gpu/`
- Probability eval run dir: `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_recover_b2w0_4gpu_prob_eval/`
- Metrics on CAMO/COD10K/NC4K
- KD vs no-KD comparison report

## Acceptance

1. Teacher 处于 eval/frozen。
2. 报告 KD loss 权重。
3. 至少输出 final mask KD；edge KD 可选。
4. 结果不能覆盖无 KD run。
5. 当前已通过 py_compile、配置加载、CPU teacher checkpoint load，以及 GPU batch 1/batch 4 smoke。
6. 训练必须从 `epoch_5.pth` 恢复；默认先用四卡 batch2 workers0。如果继续 SIGKILL，不许直接放弃，必须依次尝试双卡/单卡恢复或给出离线 teacher-map 方案。
7. GPU 有外部 `torchrun|train.py` 任务时不得强行启动；除非主控明确授权，否则使用 `start_kd_full_train.sh` 的默认拒绝策略。
8. 完整 checkpoint 产生后，必须用概率图协议评估 CAMO/COD10K/NC4K，并写入 `metrics_all.csv` 的 `protocol/repo_boundary/checkpoint/status` 字段。
