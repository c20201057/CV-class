# P0 Task: Implement Light-ESCNet B2-C64

## Agent Role

轻量模型工程 agent。

## Goal

实现最小 Light-ESCNet：`pvt_v2_b2 + inter_channel=64`，保持 ESCNet 训练/测试/评估接口兼容。

## Work Principle

不偷懒，不因为怕风险而保守。实现必须可训练、可 smoke、可 profile；高风险结构尝试可以提出或隔离实现，但不能污染 baseline 或覆盖他人成果。

## Scope

优先写到隔离副本：

- `/root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64/`
- `/root/data-tmp/workspace/02_experiments/configs/light_b2_c64.yaml`
- `/root/data-tmp/workspace/03_agent_tasks/reports/P0_light_b2_c64_impl.md`

不要直接覆盖 `/root/ESCNet`。

## Requirements

1. 将 `inter_channel=128` 配置化。
2. 支持 `backbone=pvt_v2_b2`。
3. 输出通道仍使用 lateral `[512,320,128,64]`。
4. 随机输入 smoke test 通过。
5. 报告参数量，目标约 29.8M。

## Acceptance

可用随机输入完成：

```text
out_edge, out_masks = model(torch.randn(1, 3, 416, 416).cuda())
len(out_masks) == 4
```
