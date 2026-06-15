# Agent 工作验收标准

验收总原则：先证据，后结论。主控只接受能够复核的结果。

## 通用验收

每个 agent 回报必须包含：

- 任务 ID 或实验 ID
- 修改/新增文件列表
- 使用的 config、checkpoint、数据集路径
- 运行命令或核心步骤
- 成功证据：日志、指标、图片或 JSON
- 失败和异常说明

不接受：

- 没有路径的口头结果
- 覆盖公共目录的结果
- 未标明训练 epoch 的指标
- 把短训结果伪装成完整训练
- 未经说明地修改 `/root/ESCNet`
- 因为担心失败而只给计划、不交付可运行资产
- 高风险尝试失败却不留下最小复现命令和日志

每个派发给 agent 的 prompt 或 pending 任务文件还必须显式继承项目工作准则：不偷懒，不因为怕风险而保守。新增 prompt 后运行：

```bash
python /root/data-tmp/workspace/03_agent_tasks/prompts/audit_prompt_principles.py
```

主控验收后还必须更新：

```bash
/root/data-tmp/workspace/03_agent_tasks/acceptance/agent_acceptance_ledger.md
python /root/data-tmp/workspace/03_agent_tasks/acceptance/audit_agent_acceptance_ledger.py
```

如果结果被拒收或只能作为 smoke/observation，也必须进入 ledger，标明
`rejected_for_paper`、`accepted_reference_only` 或 `pending_gate`，不能只在口头说明中降级。

## 实验结果入表标准

P0 主表结果必须满足：

1. 三数据集 CAMO/COD10K/NC4K 至少完整评估一次。
2. 预测数量与 GT 数量一致。
3. 指标文件、config 快照、checkpoint 和日志均存在。
4. profile 至少包含 params、GMACs/FLOPs status、model size、peak memory；latency/FPS 必须来自空闲 GPU 同条件复测，否则只能标记为 pending。
5. 主控复核指标解析无误。

补充要求：

6. 指标使用的预测协议必须明确：概率图或二值图。
7. 如果 FLOPs 无法统计，必须在 profile JSON 中记录原因，不能空字段混过去。
8. 若 DDP/多卡训练失败，必须保留单卡 fallback 命令。
9. `metrics_all.csv` 入表行必须包含 `protocol`、`repo_boundary`、`checkpoint` 和 `status`；字段为空的结果不能进入主结果表。
10. clean ESCNet-B5 baseline 复评必须使用 `/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean` 和 `/root/data-tmp/epoch_120.pth`，不能直接使用 dirty `/root/ESCNet`。
11. KD/B0/MobileMamba 结果在完整 checkpoint、三数据集概率图评估和完整性检查通过前，只能写为待验证、partial 或 failure analysis。

## 模型代码验收

模型工程 agent 的代码必须满足：

1. 随机输入 forward smoke test 通过。
2. 输出格式与原 ESCNet 兼容：`out_edge, out_mask_list`。
3. `out_mask_list` 包含 4 个尺度预测。
4. 可被现有 train/test/eval 流程调用或给出兼容 wrapper。
5. 参数量统计可复现。

## 文献验收

文献 agent 输出必须满足：

1. 每篇有题名、年份、来源链接。
2. 标明是核心正文、对比启发还是未来工作。
3. 不能只给二手博客链接。
4. 2025-2026 信息必须明确 DOI、publisher、项目页或可信元数据。

## 可视化验收

可视化 agent 输出必须满足：

1. 图像列名清晰。
2. 样本同名对齐。
3. 输出图片非空且可打开。
4. 附样本选择理由。
5. 至少包含 1-2 个失败案例。
