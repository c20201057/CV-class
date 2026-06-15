# P0 Task: Build Evaluation Suite

## Agent Role

实验工程 agent。

## Goal

实现 `run_eval_suite.sh` 和 `collect_metrics.py`，让任意 checkpoint 可以在 CAMO、COD10K、NC4K 上独立评估并写入 workspace。

## Work Principle

不偷懒，不因为怕风险而保守。能做 smoke 就做 smoke，能写入 metadata 就写入 metadata；失败也必须留下可复现命令、日志和最小证据。

## Scope

只写：

- `/root/data-tmp/workspace/02_experiments/scripts/run_eval_suite.sh`
- `/root/data-tmp/workspace/02_experiments/scripts/collect_metrics.py`
- `/root/data-tmp/workspace/03_agent_tasks/reports/P0_eval_suite.md`

不要修改 `/root/ESCNet/test.py` 或 `/root/ESCNet/eval.py`，除非另有任务授权。

## Inputs

Smoke input 可使用：

- Checkpoint: `/root/data-tmp/epoch_120.pth`
- Repo/config: `/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean` and
  `/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean/config.local.yaml`

历史注意：`/root/ESCNet` 当前是 dirty 工作树；`/root/ESCNet/checkpoints/escnet/epoch_120.pth`
是后续重训产物，不是 clean baseline/teacher。baseline 三数据集概率图复评应优先使用
`/root/data-tmp/workspace/02_experiments/scripts/start_baseline_prob_eval_clean.sh`。

## Acceptance

1. 三个数据集的预测和 `result.txt` 分开保存。
2. `collect_metrics.py` 能解析 result 并更新 `metrics_all.csv`。
3. 不写主仓库公共 `preds/results`。
