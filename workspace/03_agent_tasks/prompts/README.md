# Agent Prompts

本目录保存给不同 agent 的目标模式 prompt。每个 prompt 都要求 agent 明确写入范围、回报格式和验收证据。

## 使用方式

派发任何任务时，先附加 [`MASTER_TARGET_PROMPT.md`](MASTER_TARGET_PROMPT.md)，再附加具体任务 prompt。这样每个 subagent 都会继承同一套目标、路径、证据标准和工作准则。

每个 agent 开工前必须先读：

- `/root/data-tmp/workspace/00_project/orchestrator_tick_latest.md`
- `/root/data-tmp/workspace/00_project/orchestrator_tick_latest.json`

这两个文件是当前 Gate、B0、GPU、watcher、release audit 和下一步队列的一页式入口；如果它们与较旧 handoff 文档冲突，以最新总览和主控最新指令为准。

推荐调度顺序：

1. `engineer_profile_prompt.md`
2. `experiment_runner_prompt.md`
3. `engineer_light_model_prompt.md`
4. `distillation_prompt.md`
5. `visualization_prompt.md`
6. `paper_writer_prompt.md`

## 共同准则

每个 agent 必须遵守：

- 不偷懒：能验证就验证，能产出文件就产出文件。
- 不保守：不要因为担心失败只做低收益工作；高风险实验可以做，但必须隔离和记录。
- 不覆盖：你不是一个人在代码库里，不要回退、清理或覆盖别人结果。
- 不编造：未完成实验不能写成结果。
- 不污染：所有新实验输出进入 workspace 的 run 目录。

## 自动审计

每次新增或修改 prompt/pending 任务后运行：

```bash
python /root/data-tmp/workspace/03_agent_tasks/prompts/audit_prompt_principles.py
```

该审计会检查 `prompts/*.md` 和 `pending/*.md` 是否显式包含“不偷懒”和“不因为风险而保守/不保守”的准则。
