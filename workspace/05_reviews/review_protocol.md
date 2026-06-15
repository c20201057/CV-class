# Review Protocol

主控 agent 对 subagent 产物采用“先证据、后结论”的验收方式。

## 验收流程

1. 读 agent 回报，确认任务 ID、写入范围、证据路径。
2. 检查是否触碰了未授权文件，尤其是 `/root/ESCNet` 公共结果目录。
3. 运行最小复核命令：例如 `ls`、数量检查、JSON/CSV 解析、forward smoke 或抽样可视化。
4. 对指标进行来源追踪：config、checkpoint、preds、GT、result.txt 是否一一对应。
5. 写入 `05_reviews/subagent_reviews.md`：通过、部分通过、拒收。
6. 通过后更新 `02_experiments/tables`、`experiment_matrix.md` 和论文素材。

## 拒收条件

- 没有可访问的结果路径。
- 覆盖或混入公共 `preds/results`。
- 指标无法回溯到 checkpoint 和 config。
- 短训结果未明确标记。
- 推理图数量与 GT 数量不一致。
- 论文文字中编造未完成实验或夸大结论。

## 部分通过条件

以下结果可以作为工程记录或消融线索，但不能进入主表：

- 只跑了单数据集。
- 只有短训。
- 缺少 profile 的模型结果。
- 概率图/二值图协议不一致。
- 失败实验有完整日志和明确根因。

## 主表通过条件

进入论文主表的模型必须满足：

- 有唯一 `exp_id`。
- 有 config 快照、checkpoint、训练日志、评估日志。
- CAMO、COD10K、NC4K 三数据集完整评估。
- 有 Params、model size、latency/FPS；FLOPs 若不可用必须说明原因。
- 有 run metadata，且 `metrics_all.csv` 与 `profiles.csv` 已更新。
