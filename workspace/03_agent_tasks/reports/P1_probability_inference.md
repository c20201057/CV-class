# P1 Probability Inference Report

## 任务 ID / 实验 ID

- Task: P1_probability_inference
- Experiment: prob_infer_b5_camo_smoke

## 完成状态

pass

## 写入或修改文件

- `/root/data-tmp/workspace/02_experiments/scripts/infer_prob.py`
- `/root/data-tmp/workspace/03_agent_tasks/reports/P1_probability_inference.md`
- Smoke outputs: `/root/data-tmp/workspace/02_experiments/runs/prob_infer_b5_camo_smoke/`

未修改 `/root/ESCNet/test.py` 或 `/root/ESCNet/eval.py`。

## 使用命令

```bash
python -m py_compile /root/data-tmp/workspace/02_experiments/scripts/infer_prob.py

mkdir -p \
  /root/data-tmp/workspace/02_experiments/runs/prob_infer_b5_camo_smoke/logs \
  /root/data-tmp/workspace/02_experiments/runs/prob_infer_b5_camo_smoke/preds/CAMO \
  /root/data-tmp/workspace/02_experiments/runs/prob_infer_b5_camo_smoke/results/CAMO

python /root/data-tmp/workspace/02_experiments/scripts/infer_prob.py \
  --repo /root/ESCNet \
  --config /root/ESCNet/config.camo.yaml \
  --ckpt /root/ESCNet/checkpoints/escnet/epoch_120.pth \
  --pred_root /root/data-tmp/workspace/02_experiments/runs/prob_infer_b5_camo_smoke/preds/CAMO \
  --device cuda:0 \
  --batch_size_valid 8 \
  2>&1 | tee /root/data-tmp/workspace/02_experiments/runs/prob_infer_b5_camo_smoke/logs/CAMO_infer_prob.log

python /root/ESCNet/eval.py \
  --config /root/ESCNet/config.camo.yaml \
  --pred_root /root/data-tmp/workspace/02_experiments/runs/prob_infer_b5_camo_smoke/preds/CAMO \
  --save_dir /root/data-tmp/workspace/02_experiments/runs/prob_infer_b5_camo_smoke/results/CAMO \
  --model_lst epoch_120 \
  --n_threads 1 \
  2>&1 | tee /root/data-tmp/workspace/02_experiments/runs/prob_infer_b5_camo_smoke/logs/CAMO_eval_prob.log

python /root/ESCNet/eval.py \
  --config /root/ESCNet/config.camo.yaml \
  --pred_root /root/ESCNet/preds_epoch120_camo \
  --save_dir /root/data-tmp/workspace/02_experiments/runs/prob_infer_b5_camo_smoke/results/CAMO_current_eval_historic_pred \
  --model_lst epoch_120 \
  --n_threads 1 \
  2>&1 | tee /root/data-tmp/workspace/02_experiments/runs/prob_infer_b5_camo_smoke/logs/CAMO_eval_historic_pred_current_eval.log
```

## 使用数据 / 配置 / checkpoint

- Repo: `/root/ESCNet`
- Config: `/root/ESCNet/config.camo.yaml`
- Dataset: `/root/data-tmp/COD/Test/CAMO`
- Checkpoint: `/root/ESCNet/checkpoints/escnet/epoch_120.pth`
- Device: `cuda:0`

## 实现说明

新增 `infer_prob.py` 参数支持：

- `--repo`
- `--config`
- `--ckpt`
- `--pred_root`
- `--device`
- `--batch_size_valid`
- 额外支持 `--method`，默认使用 checkpoint stem，例如 `epoch_120`。

推理流程沿用 ESCNet 仓库接口：加载 `load_config`、`MyData`、`ESCNet(config, pretrained=False)`、`check_state_dict`，取 `scaled_preds[-1].sigmoid()` 作为最终 mask 概率图，按原 GT 尺寸 resize 后保存为 0-255 grayscale PNG。输出目录为：

```text
<pred_root>/<method>/<gt_filename>.png
```

因此可直接被现有 `/root/ESCNet/eval.py` 用 `--pred_root <pred_root> --model_lst <method>` 评估。

与原 `/root/ESCNet/test.py` 的关键差异：

- 原 `test.py`: `scaled_preds[-1].sigmoid() >= 0.5`，先二值化，再保存。
- 新 `infer_prob.py`: 仅做 `sigmoid()`，不做阈值化。
- 原 `test.py` resize 保存使用 `align_corners=True`。
- 新 `infer_prob.py` resize 使用 `align_corners=False`，与 ESCNet decoder 内部多处 bilinear upsample 设置保持一致。

## 关键结果

### 预测目录

```text
/root/data-tmp/workspace/02_experiments/runs/prob_infer_b5_camo_smoke/preds/CAMO/epoch_120
```

### 数量检查

- GT count: 250
- Prediction count: 250
- Filename alignment: pass, no missing and no extra files.

### 灰度值检查

抽样前 5 张输出均为连续灰度 PNG，不是纯二值：

| sample | shape | unique_count | min | max |
|---|---:|---:|---:|---:|
| camourflage_00012.png | 420x632 | 256 | 0 | 255 |
| camourflage_00018.png | 628x940 | 256 | 0 | 255 |
| camourflage_00061.png | 640x960 | 256 | 0 | 255 |
| camourflage_00064.png | 617x589 | 256 | 0 | 255 |
| camourflage_00071.png | 203x249 | 256 | 0 | 255 |

全量统计：

- min unique_count: 175
- max unique_count: 256
- least varied sample: `camourflage_01164.png`, unique_count 175, min 0, max 255

注意：原 `test.py` 即使先阈值化，后续 bilinear resize 也会在边界产生多个灰度值。因此“多个灰度值”只能作为输出文件非纯二值的 smoke 证据；真正避免阈值化的证据是新脚本代码路径只使用 `scaled_preds[-1].sigmoid()`。

### CAMO 指标

使用现有 `eval.py` 评估概率图：

| source | Smeasure | wFmeasure | meanFm | meanEm | MAE |
|---|---:|---:|---:|---:|---:|
| probability smoke, this task | 0.819 | 0.753 | 0.794 | 0.867 | 0.069 |
| binary smoke, existing P0 run | 0.811 | 0.761 | 0.800 | 0.873 | 0.067 |
| historic baseline table | 0.875 | 0.849 | 0.867 | 0.937 | 0.041 |
| historic pred re-evaluated now | 0.875 | 0.849 | 0.867 | 0.937 | 0.041 |

Probability smoke vs existing binary smoke:

- Smeasure: +0.008
- wFmeasure: -0.008
- meanFm: -0.006
- meanEm: -0.006
- MAE: +0.002

Probability smoke vs historic baseline:

- Smeasure: -0.056
- wFmeasure: -0.096
- meanFm: -0.073
- meanEm: -0.070
- MAE: +0.028

## 证据路径

- Inference log: `/root/data-tmp/workspace/02_experiments/runs/prob_infer_b5_camo_smoke/logs/CAMO_infer_prob.log`
- Probability eval log: `/root/data-tmp/workspace/02_experiments/runs/prob_infer_b5_camo_smoke/logs/CAMO_eval_prob.log`
- Probability eval result: `/root/data-tmp/workspace/02_experiments/runs/prob_infer_b5_camo_smoke/results/CAMO/result.txt`
- Historic prediction re-eval log: `/root/data-tmp/workspace/02_experiments/runs/prob_infer_b5_camo_smoke/logs/CAMO_eval_historic_pred_current_eval.log`
- Historic prediction re-eval result: `/root/data-tmp/workspace/02_experiments/runs/prob_infer_b5_camo_smoke/results/CAMO_current_eval_historic_pred/result.txt`
- Existing binary smoke result: `/root/data-tmp/workspace/02_experiments/runs/smoke_eval_suite_b5_camo/results/CAMO/result.txt`
- Historic baseline table: `/root/data-tmp/workspace/02_experiments/tables/metrics_all.csv`

## 风险和异常

1. 当前从 `/root/ESCNet/checkpoints/escnet/epoch_120.pth` 重新推理得到的 binary smoke 与历史预测 `/root/ESCNet/preds_epoch120_camo/epoch_120` 不逐像素一致；250 张共同文件中 0 张完全相同，平均 absolute pixel difference 约 13.74，最大差异 255。
2. 历史预测用当前 `eval.py` 复评仍得到 CAMO 0.875/0.849/0.867/0.937/0.041，说明历史表本身可复评；差异更可能来自当前推理链路、当前仓库 dirty 状态、checkpoint/代码组合、推理 device/环境或 config 复现链条，而不是 `eval.py` 解析失败。
3. 现有 `metrics.py::_prepare_data` 会对每张预测先除以 255，再做 min-max normalization。概率图保留连续值后仍会被 per-image normalize，这会影响 MAE 绝对概率解释。此任务未修改 `eval.py`，因此该行为保持原样，只报告风险。
4. 概率图指标是 CAMO smoke，不应作为论文主表结果。

## 是否可入论文

no

脚本可作为后续可信评估基础设施；本次 CAMO smoke 指标只用于验证推理和评估链路，不进入论文主表。

## 建议下一步

1. 用 `infer_prob.py` 对 COD10K/CAMO/NC4K 全量重新生成 probability predictions，并用同一套 `eval.py` 输出统一概率评估表。
2. 单独追查当前重新推理预测低于历史预测的原因：固定 repo commit、记录 dirty diff、复核 checkpoint 来源、比较 `test.py` multiprocessing 推理与单进程推理的 logits/PNG。
3. 评估是否需要新增一个不做 per-image min-max normalization 的 MAE/curve evaluator，专门用于概率图可信度分析；这应作为单独任务处理，避免污染现有 `eval.py`。
