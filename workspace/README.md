# Light-COS Orchestration Workspace

本工作区用于围绕 `/root/ESCNet` 完成课程论文《面向伪装目标分割的轻量化模型研究》的实验组织、agent 分工、结果验收和论文写作。

## 总控入口

- [Master Plan](00_project/master_plan.md)
- [Task Board](03_agent_tasks/task_board.md)
- [Master Target Prompt](03_agent_tasks/prompts/MASTER_TARGET_PROMPT.md)
- [Review Protocol](05_reviews/review_protocol.md)

## 当前判断

ESCNet 已经可以作为强教师/重基线：现有 `pvt_v2_b5` 版本约 99.9M 参数，训练集为 COD10K-Train + CAMO-Train 共 4040 张，已有 epoch 120 在 COD10K、CAMO、NC4K 三个测试集上的预测和指标。单卡 V100 完整训练 120 epoch 约 17.9 小时，因此核心实验不应铺太多完整训练。

论文主线建议收敛为：以 ESCNet 为强基线和教师，构建 Light-ESCNet，通过轻主干、窄解码通道、边界语义保留和蒸馏，在较小精度损失下显著降低参数量、FLOPs、模型大小和延迟。

当前硬件已确认：4 x Tesla V100-SXM2-16GB，PyTorch 2.5.1+cu121。P0 工程任务已经完成，`light_b2_c64_e120_s42` no-KD 四卡 120 epoch 训练与三数据集概率图评估已验收；`kd_light_b2_c64_e120_s42` 已重启四卡 full train，并确认 teacher 加载、epoch 1 checkpoint 保存。长训恢复入口见 [Resume Handoff](00_project/resume_handoff.md)。

## 工作区结构

- `00_project/`: 开题报告抽取文本、项目画像、全局路线判断。
- `01_literature/`: 已核验文献、引用素材、相关工作写作卡片。
- `02_experiments/`: 配置、运行目录、脚本规格、表格和图。
- `03_agent_tasks/`: 给实验/文献/写作 agent 的 prompt、回报和验收表。
- `04_paper/`: 论文大纲、章节草稿、图表资产。
- `05_reviews/`: 对 agent 产物和论文版本的验收记录。

## 核心文件

- [项目画像](00_project/project_profile.md)
- [路线判断](00_project/route_decision.md)
- [实验矩阵](02_experiments/experiment_matrix.md)
- [Workflow](02_experiments/workflow.md)
- [Agent Prompts](03_agent_tasks/prompts/README.md)
- [验收标准](03_agent_tasks/acceptance/acceptance_criteria.md)
- [论文大纲](04_paper/outline/paper_outline.md)
- [论文初稿](04_paper/drafts/paper_draft.md)
- [主结果表模板](04_paper/tables/main_results_template.md)
- [概率图评测协议](02_experiments/evaluation_protocol.md)

## 调度原则

1. 不直接覆盖 `/root/ESCNet` 的现有结果和未提交改动。
2. 每个实验只写 `02_experiments/runs/<exp_id>`。
3. 每个 agent 只能拥有清晰、互不重叠的写入范围。
4. 所有结论必须绑定配置、checkpoint、测试集、指标表和日志路径。
5. 论文只采用通过验收的结果；短训结果可用于筛选，但不能冒充最终性能。
6. 所有 subagent prompt 必须包含“不偷懒、不保守、不覆盖、不编造”的工作准则。
