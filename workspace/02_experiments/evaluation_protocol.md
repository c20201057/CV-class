# Evaluation Protocol

更新时间：2026-06-13

## 结论

论文主表统一使用概率图评估协议：

1. 推理输出最终 mask logits 的 `sigmoid()` 概率。
2. 按 GT 原尺寸 resize，`align_corners=False`。
3. 保存为 0-255 灰度 PNG，不做 `>=0.5` 阈值化。
4. 使用现有 `eval.py` 计算 S-measure、wFmeasure、meanFm、meanEm、MAE。
5. 所有指标必须由 `collect_metrics.py` 汇总到 `metrics_all.csv`。

## 为什么不用原 `test.py`

`/root/ESCNet/test.py` 当前做了：

```python
pred_lvl = (scaled_preds[-1].sigmoid() >= 0.5).float()
```

这会把预测保存为二值图，可能影响 MAE 和曲线类 F/E 指标。它可以作为工程 smoke，但不能作为论文主表协议。

## Teacher Checkpoint

ESCNet-B5 teacher 固定为：

`/root/data-tmp/epoch_120.pth`

不要使用：

`/root/ESCNet/checkpoints/escnet/epoch_120.pth`

原因：后者是 2026-06-13 后续重训产物，CAMO 复评低于历史 baseline；前者与 2026-06-11 历史预测时间匹配，并可复现 CAMO 高分。

## 已验证 Baseline CAMO

使用 `/root/data-tmp/epoch_120.pth` 与 `infer_prob.py`：

| Dataset | Smeasure | wFmeasure | meanFm | meanEm | MAE |
| --- | ---: | ---: | ---: | ---: | ---: |
| CAMO | 0.881 | 0.842 | 0.864 | 0.933 | 0.043 |

这与历史 baseline CAMO 行 `0.875/0.849/0.867/0.937/0.041` 高度一致。

## 标准命令模板

单数据集概率推理：

```bash
python /root/data-tmp/workspace/02_experiments/scripts/infer_prob.py \
  --repo <repo_or_code_dir> \
  --config <dataset_config.yaml> \
  --ckpt <checkpoint.pth> \
  --pred_root <run_dir>/preds/<DATASET> \
  --device cuda:0 \
  --batch_size_valid 8
```

评估：

```bash
python <repo_or_code_dir>/eval.py \
  --config <dataset_config.yaml> \
  --pred_root <run_dir>/preds/<DATASET> \
  --save_dir <run_dir>/results/<DATASET> \
  --model_lst <method> \
  --n_threads 4
```

汇总：

```bash
python /root/data-tmp/workspace/02_experiments/scripts/collect_metrics.py \
  --exp_id <exp_id> \
  --out_csv /root/data-tmp/workspace/02_experiments/tables/metrics_all.csv \
  --result CAMO=<run_dir>/results/CAMO/result.txt \
  --result COD10K=<run_dir>/results/COD10K/result.txt \
  --result NC4K=<run_dir>/results/NC4K/result.txt
```

## 主表准入

每个模型进入主表前必须满足：

- CAMO、COD10K、NC4K 三数据集均完成概率图推理。
- 每个数据集 pred 数量等于 GT 数量。
- 随机抽样预测图 unique gray values 大于 2。
- 指标、config、checkpoint、日志和 profile 路径写入 run metadata。
- `metrics_all.csv` 和 `profiles.csv` 都已更新。

## 轻量模型配置规则

评估 Light-ESCNet 或 KD/消融模型时，`run_prob_eval_suite.sh` 必须传入对应训练 run 的 YAML：

```bash
--template_config <run_dir>/config.yaml
```

不要使用代码目录默认 `config.yaml` 作为轻量模型评测模板；该文件可能仍是 ESCNet-B5/C128 默认结构，会导致 B2/C64 checkpoint 加载形状不匹配。
