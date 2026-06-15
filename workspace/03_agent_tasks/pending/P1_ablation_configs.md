# P1 Task: Structural Ablation Runs

## Goal

在主线 no-KD/KD 结果之后，补充结构消融，隔离主干轻量化和解码器通道缩减的贡献。

## Work Principle

不偷懒，不因为怕风险而保守。消融可以失败或只形成趋势，但必须隔离 run、保留日志和协议边界；不能因为风险高就只写计划。

## Prepared Configs

- B2-C128: `/root/data-tmp/workspace/02_experiments/configs/light_b2_c128.yaml`
- B5-C64: `/root/data-tmp/workspace/02_experiments/configs/light_b5_c64.yaml`

## Priority

1. `light_b2_c128_e120_s42`：优先级最高，用于判断 B2-C64 的精度损失主要来自 backbone 替换还是 decoder 窄化。
2. `light_b5_c64_e60_s42`：可作为 decoder 窄化消融，若算力不足可先 60 epoch 并明确标记。

## Acceptance

- 不覆盖 `light_b2_c64_e120_s42` 或 `kd_light_b2_c64_e120_s42`。
- 每个 run 都必须保存 config、metadata、训练日志。
- 进入论文主表前必须使用概率图评测协议。
- 若只训练 60 epoch，只能作为消融/趋势证据，不得冒充完整收敛结果。
