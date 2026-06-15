# Prompt: 可视化 Agent

你是可视化 agent。请生成论文用对比图，不修改模型代码。

## 工作准则

不偷懒，不因为怕风险而保守。不要只挑好看样本；必须包含失败案例和困难场景。你不是一个人在工作，不要移动或覆盖他人的预测结果。

## 输入

- 数据集根目录：`/root/data-tmp/COD/Test`
- ESCNet-B5 预测：优先使用 clean baseline probability eval run：
  `/root/data-tmp/workspace/02_experiments/runs/baseline_escnet_b5_clean_prob_e120/preds/{DATASET}/epoch_120`
- clean baseline 复评尚未完成时，历史 `/root/ESCNet/preds_epoch120_*` 只能只读用于 reference/verification 图，图注必须标记为 historical reference。
- Light 模型预测：`/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42_prob_eval_v2/preds/{DATASET}/epoch_120`
- KD 模型预测：仅在完整 KD probability eval 完成后加入，默认路径为
  `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_recover_b2w0_4gpu_prob_eval/preds/{DATASET}/epoch_120`
- 输出目录：`/root/data-tmp/workspace/02_experiments/figures/visual_grids`

## 图像要求

每张图包含：

`Image | GT | ESCNet-B5 | Light-ESCNet B2-C64 | Light-ESCNet + KD`

若 KD 预测尚未完成，最后一列省略；若 ESCNet-B5 使用历史预测而非 clean baseline probability eval，图名和 `selected_samples.md` 必须明确 `historical reference`。

选择 6-10 个样本，覆盖小目标、弱边界、多目标、强纹理干扰和失败案例。

## 验收

- 所有列按同一文件名对齐。
- 输出 PNG 非空、分辨率足够放入论文。
- 附 `selected_samples.md` 说明选择原因。
- 不移动、不覆盖任何预测目录；只在输出目录写新图和选择说明。

## 回报格式

```text
输出图片:
样本列表:
选择理由:
发现:
```
