# 实验 Workflow

## 0. 不变原则

所有实验输出必须进入：

`/root/data-tmp/workspace/02_experiments/runs/<exp_id>/`

不要复用 `/root/ESCNet/preds`、`/root/ESCNet/results`、`/root/ESCNet/checkpoints` 作为新实验输出目录。

当前硬件：4 x Tesla V100-SXM2-16GB。优先用四卡加速完整主实验；若多卡工程风险阻塞，则单卡并行短训/推理/profile，但每个任务必须独立 run 目录。

派发 agent 前必须附加 `03_agent_tasks/prompts/MASTER_TARGET_PROMPT.md`。

## 1. 新建实验

每个实验目录应包含：

```text
runs/<exp_id>/
  metadata.json
  config.yaml
  checkpoints/
  preds/
    CAMO/
    COD10K/
    NC4K/
  results/
    CAMO/result.txt
    COD10K/result.txt
    NC4K/result.txt
  profile.json
  logs/
  status.json
```

`metadata.json` 必备字段：

```json
{
  "exp_id": "",
  "owner": "",
  "created_at": "",
  "repo_path": "/root/ESCNet",
  "repo_commit": "",
  "repo_status": "",
  "dataset_root": "/root/data-tmp/COD",
  "model": "",
  "backbone": "",
  "inter_channel": 0,
  "img_size": 416,
  "epochs": 0,
  "seed": 42,
  "hypothesis": "",
  "changes": "",
  "ckpt_path": "",
  "metrics": {},
  "profile": {},
  "status": "pending"
}
```

## 2. 训练

训练前检查：

1. `git -C /root/ESCNet status --short` 记录到日志。
2. config 中 `save_model_dir` 指向 run 目录。
3. 不覆盖已有 checkpoint。
4. 记录 GPU、PyTorch、CUDA、训练开始时间。

短训筛选可用 5-20 epoch，但最终论文主表只能使用明确标记的完整训练或合理收敛训练。

推荐完整训练顺序：

1. `light_b2_c64_e120_s42`
2. `kd_light_b2_c64_e120_s42`
3. `light_b2_c128_e120_s42`
4. `tiny_b0_c64_e60_s42` 或更长，视前两者结果决定

## 3. 评估

对每个 checkpoint 执行：

1. CAMO inference + eval
2. COD10K inference + eval
3. NC4K inference + eval
4. 预测数量与 GT 数量一致性检查
5. 将结果解析进 `02_experiments/tables/metrics_all.csv`

优先补充概率图推理脚本。若沿用二值预测，论文中必须说明。

## 4. Profiling

每个进入论文表格的模型必须报告：

- Params
- FLOPs/GMACs at input 416x416
- model size
- batch=1 latency
- FPS
- peak GPU memory

profiling 必须固定 warmup 次数、重复次数、device、input size。

## 5. 可视化

每个主模型选 6-10 张图，覆盖：

- 小目标
- 弱边界
- 多目标
- 背景纹理强干扰
- 失败案例

图列顺序建议：

`Image | GT | ESCNet-B5 | Light baseline | Light-ESCNet`

## 6. 结果入论文

只有满足以下条件的结果可以进主表：

1. 有唯一 `exp_id`。
2. 有 config 快照、checkpoint、日志和 metadata。
3. 三数据集至少一个完整评估；主模型必须三数据集完整。
4. 指标和 profiling 通过验收。
5. agent 回报已被主控审核。

论文整合时同步更新：

- `02_experiments/tables/metrics_all.csv`
- `02_experiments/tables/profiles.csv`
- `02_experiments/experiment_matrix.md`
- `05_reviews/subagent_reviews.md`
