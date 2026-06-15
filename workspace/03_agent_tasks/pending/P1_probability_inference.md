# P1 Task: Probability Inference Fix

## Agent Role

评估可信度工程 agent。

## Goal

新增概率图推理脚本，避免 `test.py` 中 `sigmoid >= 0.5` 的二值化预测影响 MAE 和曲线指标。

## Work Principle

不偷懒，不因为怕风险而保守。必须用数量检查、灰度检查和评估 smoke 证明概率图协议可用；不能只写脚本不验证。

## Scope

优先新增而不是改原文件：

- `/root/data-tmp/workspace/02_experiments/scripts/infer_prob.py`
- `/root/data-tmp/workspace/03_agent_tasks/reports/P1_probability_inference.md`

除非主控明确允许，不修改 `/root/ESCNet/test.py`。

## Requirements

1. 保存连续概率图到 PNG，范围 0-255。
2. resize 与训练/模型内部保持 `align_corners=False`，并在报告中说明。
3. 与现有 `eval.py` 输出兼容。
4. 对 baseline checkpoint 跑 CAMO smoke。

## Acceptance

- CAMO 预测数量为 250。
- 输出图不是纯二值，抽样图像应包含多个灰度值。
