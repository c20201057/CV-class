# 结果填表 Checklist

## 必须先完成

- Light-ESCNet B2-C64 no KD 训练完成，checkpoint 应位于 `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/epoch_120.pth`。
- 使用 `/root/data-tmp/workspace/02_experiments/scripts/run_prob_eval_suite.sh` 进行 CAMO、COD10K、NC4K 概率图评测。
- 将评测结果追加或合并到 `/root/data-tmp/workspace/02_experiments/tables/metrics_all.csv`。
- 用训练完成 checkpoint 重新 profile 一次 Light-ESCNet，确认结构数值与当前 profile 一致。
- 使用 `baseline_escnet_clean` 和 `/root/data-tmp/epoch_120.pth` 完成 ESCNet-B5 CAMO、COD10K、NC4K 三数据集统一概率图复评；复评前只能写“历史参考 baseline”，不能写“最终统一协议 baseline”。
- 所有 `metrics_all.csv` 行必须填写 `protocol`、`repo_boundary`、`checkpoint` 和 `status`，否则不得进入主结果表。
- 若论文报告 latency/FPS，必须在 GPU 空闲时用同一 profiling 命令重测 baseline、Light 和最终 KD；当前速度数值只可作为内部记录。

## 推荐命令

训练完成后评测 Light-ESCNet：

```bash
bash /root/data-tmp/workspace/02_experiments/scripts/run_prob_eval_suite.sh \
  --repo /root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64 \
  --template_config /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/config.yaml \
  --ckpt /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/epoch_120.pth \
  --exp_id light_b2_c64_e120_s42_prob_eval_v2 \
  --datasets CAMO,COD10K,NC4K \
  --device cuda:0 \
  --method epoch_120 \
  --protocol prob_map \
  --repo_boundary light_b2_c64_snapshot \
  --metrics_checkpoint /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/epoch_120.pth \
  --status final_main_light
```

GPU 空闲后统一复评 clean ESCNet-B5 baseline：

```bash
bash /root/data-tmp/workspace/02_experiments/scripts/start_baseline_prob_eval_clean.sh \
  --device cuda:0
```

该 wrapper 固定使用
`/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean` 和
`/root/data-tmp/epoch_120.pth`，避免误用 dirty `/root/ESCNet` 工作树。

训练后 profile Light-ESCNet：

```bash
python /root/data-tmp/workspace/02_experiments/scripts/profile_model.py \
  --repo /root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64 \
  --config /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/config.yaml \
  --ckpt /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/epoch_120.pth \
  --out /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/profile_epoch120.json \
  --device cuda:0 \
  --warmup 20 \
  --repeat 50 \
  --exp-id light_b2_c64_trained_416
```

完整性检查：

```bash
python /root/data-tmp/workspace/02_experiments/scripts/check_run_integrity.py \
  --run_dir /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42_prob_eval_v2 \
  --exp_id light_b2_c64_e120_s42_prob_eval_v2 \
  --datasets CAMO,COD10K,NC4K
```

轻量模型必须显式传入训练 run config。不要让 wrapper 回退到代码目录默认 `config.yaml`，否则会按 ESCNet-B5/C128 建模并导致 checkpoint 形状不匹配。

刷新聚合表：

```bash
python /root/data-tmp/workspace/02_experiments/scripts/aggregate_results.py \
  --out_md /root/data-tmp/workspace/04_paper/tables/aggregated_results.md
```

注意：如果最终 checkpoint 不是 `epoch_120.pth`，以最高 epoch checkpoint 为准，并在论文和 metadata 中写清楚。

## 写作判断规则

- 若 Light-ESCNet 在 S-measure 上距离 clean ESCNet-B5 统一复评 baseline 平均小于约 0.03，且 MAE 增幅可控，可将其描述为“在显著降低复杂度的同时保持接近性能”。复评未完成前，只能写“相对历史 ESCNet-B5 参考行”。
- 若 Light-ESCNet 精度下降明显但 KD 能追回主要差距，则论文主线改为“轻量结构 + 蒸馏补偿是必要组合”。
- 若 no KD 与 KD 都明显不足，则保留效率贡献，同时启动 B2-C128 或 B5-C64 补救实验，避免论文只剩失败复现。
- 若 clean baseline 复评缺失 COD10K 或 NC4K，不得在摘要、结论或主表中写“最终同协议 ESCNet-B5 baseline 差值”；只能写“历史参考行差值”。
- 不管结果好坏，都要报告失败案例；失败分析能提高论文可信度。
