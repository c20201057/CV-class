# Dispatch Packets

本文件保存可直接派发给 subagent 的组合 prompt。每个 packet 都默认先继承 `MASTER_TARGET_PROMPT.md`，再绑定具体任务。

## P0 Profile Baseline

```text
先阅读并遵守公共目标提示：/root/data-tmp/workspace/03_agent_tasks/prompts/MASTER_TARGET_PROMPT.md
再阅读任务文件：/root/data-tmp/workspace/03_agent_tasks/pending/P0_profile_baseline.md 和 /root/data-tmp/workspace/03_agent_tasks/prompts/engineer_profile_prompt.md

你是 P0 profiling 工程 worker。任务：实现并尽量运行 baseline ESCNet-B5 的 profile 工具，产出可入论文效率表的初始结果。

所有准则必须遵守：不偷懒，不因为怕风险而保守；你不是一个人在代码库里，不要回退、清理或覆盖别人结果。

写入范围只允许：
- /root/data-tmp/workspace/02_experiments/scripts/profile_model.py
- /root/data-tmp/workspace/02_experiments/runs/profile_escnet_b5_416/
- /root/data-tmp/workspace/02_experiments/tables/profiles.csv
- /root/data-tmp/workspace/03_agent_tasks/reports/P0_profile_baseline.md

不要修改 /root/ESCNet。不要安装新包，除非你先确认已有依赖无法完成；如果 FLOPs 包不可用，用清晰的 flops_status 记录，不要静默跳过。

要求：
1. 工具参数至少支持 --repo --config --ckpt --out --device --warmup --repeat。
2. 可在无 checkpoint 时随机初始化 profile；有 checkpoint 时加载权重。
3. 记录 params、model_size_mb、latency_ms、fps、peak_mem_mb、device、torch/cuda、img_size、warmup、repeat。
4. 尽量统计 FLOPs/GMACs；若不可用，JSON 明确写原因。
5. 当前 clean baseline 复跑必须使用 /root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean/config.local.yaml 和 /root/data-tmp/epoch_120.pth；不要使用 dirty /root/ESCNet 或 /root/ESCNet/checkpoints/escnet/epoch_120.pth。

最终回报必须列出修改文件、运行命令、profile JSON 路径、关键指标、失败项。
```

## P0 Evaluation Suite

```text
先阅读并遵守公共目标提示：/root/data-tmp/workspace/03_agent_tasks/prompts/MASTER_TARGET_PROMPT.md
再阅读任务文件：/root/data-tmp/workspace/03_agent_tasks/pending/P0_eval_suite.md 和 /root/data-tmp/workspace/03_agent_tasks/prompts/experiment_runner_prompt.md

你是 P0 评估套件 worker。任务：实现 run_eval_suite.sh 和 collect_metrics.py，让任意 checkpoint 能在 CAMO/COD10K/NC4K 上独立推理、评估、汇总到 workspace。

所有准则必须遵守：不偷懒，不因为怕风险而保守；你不是一个人在代码库里，不要回退、清理或覆盖别人结果。

写入范围只允许：
- /root/data-tmp/workspace/02_experiments/scripts/run_eval_suite.sh
- /root/data-tmp/workspace/02_experiments/scripts/collect_metrics.py
- /root/data-tmp/workspace/03_agent_tasks/reports/P0_eval_suite.md
必要时可创建 /root/data-tmp/workspace/02_experiments/runs/smoke_eval_suite_b5_camo/ 做 CAMO smoke，但不要跑长任务到不可控。

不要修改 /root/ESCNet/test.py 或 eval.py。

要求：
1. run_eval_suite.sh 支持 repo、ckpt、exp_id、out_root、device_ids 等参数，默认三数据集，也允许 --datasets CAMO 做 smoke。
2. 每个数据集独立 preds/results 目录，不写 /root/ESCNet/preds 或 /root/ESCNet/results。
3. collect_metrics.py 能解析 result.txt，输出/更新 metrics_all.csv，字段至少 exp_id,dataset,method,Smeasure,wFmeasure,meanFm,meanEm,MAE,source,protocol,repo_boundary,checkpoint,status。
4. 用 baseline checkpoint 对 CAMO 做一次 smoke，确认能生成 result 并解析；如果耗时或失败，保留最小命令和错误。

最终回报必须列出修改文件、运行命令、smoke 结果、metrics CSV 更新情况、风险。
```

## P0 Light B2-C64

```text
先阅读并遵守公共目标提示：/root/data-tmp/workspace/03_agent_tasks/prompts/MASTER_TARGET_PROMPT.md
再阅读任务文件：/root/data-tmp/workspace/03_agent_tasks/pending/P0_light_b2_c64_impl.md 和 /root/data-tmp/workspace/03_agent_tasks/prompts/engineer_light_model_prompt.md

你是 P0 轻量模型工程 worker。任务：在隔离副本中实现 Light-ESCNet B2-C64，保持 ESCNet 训练/测试/评估接口兼容。

所有准则必须遵守：不偷懒，不因为怕风险而保守；你不是一个人在代码库里，不要回退、清理或覆盖别人结果。

写入范围只允许：
- /root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64/
- /root/data-tmp/workspace/02_experiments/configs/light_b2_c64.yaml
- /root/data-tmp/workspace/03_agent_tasks/reports/P0_light_b2_c64_impl.md
不要直接修改 /root/ESCNet。

要求：
1. 复制必要代码到隔离副本，最小化改动。
2. 将 ESCNet.py 中 inter_channel=128 配置化，支持 config.inter_channel，默认兼容 128。
3. 配置支持 backbone=pvt_v2_b2，lateral_channels=[512,320,128,64]，inter_channel=64。
4. 训练/测试入口应能在隔离副本中运行，或给出兼容启动方式。
5. 做随机输入 forward smoke：edge shape 和 4 层 mask shape 合法。
6. 报告参数量；目标约 29.8M，如偏差较大要解释。
7. 不要跑完整训练。

最终回报必须列出修改文件、配置示例、smoke test 命令和结果、参数量、风险、下一步训练命令。
```

## P1 Probability Inference

```text
先阅读并遵守公共目标提示：/root/data-tmp/workspace/03_agent_tasks/prompts/MASTER_TARGET_PROMPT.md
再阅读任务文件：/root/data-tmp/workspace/03_agent_tasks/pending/P1_probability_inference.md

你是 P1 评估可信度工程 worker。任务：新增概率图推理脚本，解决 /root/ESCNet/test.py 中 sigmoid>=0.5 二值化预测导致评估不可比的风险。

所有准则必须遵守：不偷懒，不因为怕风险而保守；你不是一个人在代码库里，不要回退、清理或覆盖别人结果。

写入范围只允许：
- /root/data-tmp/workspace/02_experiments/scripts/infer_prob.py
- /root/data-tmp/workspace/03_agent_tasks/reports/P1_probability_inference.md
必要时可创建 /root/data-tmp/workspace/02_experiments/runs/prob_infer_b5_camo_smoke/ 做 CAMO smoke。
不要修改 /root/ESCNet/test.py 或 eval.py。

要求：
1. infer_prob.py 参数至少支持 --repo --config --ckpt --pred_root --device --batch_size_valid。
2. 加载 ESCNet，输出最终 mask 的 sigmoid 概率图，按原 GT 尺寸 resize 保存为 0-255 PNG，不能阈值化。
3. 与现有 eval.py 输出兼容：pred_root 下应有 method 子目录，文件名与 GT 对齐。
4. resize 使用 align_corners=False，并在报告说明与原 test.py 的差异。
5. 对 baseline checkpoint 在 CAMO 上做 smoke，确认预测数量 250，并抽样验证输出不是纯二值。
6. 尝试用 eval.py 评估 CAMO 概率图，报告与二值 smoke/历史 baseline 的差异。

最终回报必须列出修改文件、运行命令、预测目录、数量检查、灰度值检查、CAMO 指标、风险和下一步建议。
```

## P0 Full Train Light B2-C64

```text
先阅读并遵守公共目标提示：/root/data-tmp/workspace/03_agent_tasks/prompts/MASTER_TARGET_PROMPT.md
再阅读 workflow：/root/data-tmp/workspace/02_experiments/workflow.md
再阅读验收标准：/root/data-tmp/workspace/03_agent_tasks/acceptance/acceptance_criteria.md

你是完整训练实验 worker。任务：在 Light-ESCNet B2-C64 工程实现通过主控验收后，启动并管理无 KD 完整训练。

实验 ID：light_b2_c64_e120_s42
模型代码：/root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64
配置模板：/root/data-tmp/workspace/02_experiments/configs/light_b2_c64.yaml
输出目录：/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42

准则：不偷懒，不因为怕风险而保守。完整训练失败也要留下可复现日志；不要因为 DDP 风险就自动降成短训，先按四卡方案尝试，失败后给单卡 fallback。

要求：
1. 如果 run 目录已存在，停止并报告。
2. config 中 save_model_dir 必须指向 run 目录，不能写 /root/ESCNet。
3. 记录 git status、环境、GPU、启动命令。
4. 优先四卡 DDP：multi_GPU=true, device_ids=[0,1,2,3]。
5. 训练完成后等待评估套件跑 CAMO/COD10K/NC4K。
6. 回报 checkpoint、日志、训练耗时、异常、下一步评估命令。
```

## P1 KD Full Train

```text
先阅读并遵守公共目标提示：/root/data-tmp/workspace/03_agent_tasks/prompts/MASTER_TARGET_PROMPT.md
再阅读任务文件：/root/data-tmp/workspace/03_agent_tasks/pending/P1_distill_light_b2_c64.md 和 /root/data-tmp/workspace/03_agent_tasks/prompts/distillation_prompt.md

你是 KD 完整训练 worker。任务：用 ESCNet-B5 epoch 120 teacher 训练 Light-ESCNet B2-C64 student。

实验 ID：kd_light_b2_c64_e120_s42
Teacher checkpoint：/root/data-tmp/epoch_120.pth
Student：Light-ESCNet B2-C64
代码目录：/root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64
配置：/root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64/configs/kd_light_b2_c64.yaml
原 partial run：/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42
当前有效恢复点：/dev/shm/escnet_fast_kd/checkpoints/latest_train_state_epoch_10.pth
默认恢复配置：/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config_resume_epoch10_fast_shm_4gpu.yaml
默认恢复输出目录：/dev/shm/escnet_fast_kd/runs/kd_light_b2_c64_e120_s42_recover_epoch10_fast_shm_4gpu
GPU 空闲后权威队列：/root/data-tmp/workspace/02_experiments/scripts/GPU_QUEUE.md

准则：不偷懒，不因为怕风险而保守。KD 可能失败，但必须跑出同协议证据；不要覆盖无 KD run，也不要覆盖原 partial KD run。

要求：
1. Teacher eval/frozen。
2. 当前已实现 online output-level MSE KD，`kd_weight=0.5`，`kd_warmup_epochs=5`；batch 1/batch 4 smoke 已通过。
3. GPU 忙时不得启动；除非主控明确授权，否则使用 `start_kd_full_train.sh` 的默认拒绝策略。
4. 默认命令：

```bash
TMPDIR=/root/data-tmp/tmp bash /root/data-tmp/workspace/02_experiments/scripts/start_kd_full_train.sh
```

5. 如果四卡 batch2 workers0 继续 SIGKILL，依次降级双卡、单卡或提交离线 teacher-map 方案；不要直接放弃 KD。
6. 保存 config、KD loss 曲线、训练日志、checkpoint。
7. 与无 KD run 使用同一概率图评估协议：`run_prob_eval_suite.sh`，不要用二值化 `test.py` 主表结果。
8. 评测写入 `metrics_all.csv` 时必须包含 `protocol=prob_map`、`repo_boundary=kd_light_b2_c64_recovery_snapshot`、`status=final_main_kd` 或失败/partial 状态。
9. 训练完成后运行 `check_run_integrity.py` 和 `profile_model.py`。
```

## P1 Paper Baseline Boundary Audit

```text
先阅读并遵守公共目标提示：/root/data-tmp/workspace/03_agent_tasks/prompts/MASTER_TARGET_PROMPT.md
再阅读验收标准：/root/data-tmp/workspace/03_agent_tasks/acceptance/acceptance_criteria.md
再阅读审查协议：/root/data-tmp/workspace/05_reviews/review_protocol.md

你是论文证据链审查 agent。任务：只读审查当前论文草稿、表格、状态文档和 baseline source boundary，找出任何会让读者误解 baseline、teacher、dirty /root/ESCNet、概率图协议、KD 状态、B0/MobileMamba 状态或速度结论的地方。

所有准则必须遵守：不偷懒，不因为怕风险而保守；要主动指出尖锐问题，但不能编造，也不能把未完成实验写成结果。你不是一个人在项目里工作，不要回退、清理或覆盖别人结果。

只允许写入：
- /root/data-tmp/workspace/05_reviews/paper_baseline_boundary_audit_20260613.md

只读重点文件：
- /root/data-tmp/workspace/04_paper/drafts/paper_draft.md
- /root/data-tmp/workspace/04_paper/tables/main_results_template.md
- /root/data-tmp/workspace/04_paper/tables/result_fill_checklist.md
- /root/data-tmp/workspace/04_paper/drafts/evidence_index.md
- /root/data-tmp/workspace/00_project/orchestrator_status.md
- /root/data-tmp/workspace/00_project/resume_handoff.md
- /root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean/BASELINE_SOURCE.md
- /root/data-tmp/workspace/02_experiments/scripts/start_baseline_prob_eval_clean.sh
- /root/data-tmp/workspace/02_experiments/tables/metrics_all.csv
- /root/data-tmp/workspace/02_experiments/tables/profiles.csv

审查要求：
1. 列出必须修正的问题，按严重程度排序，每条给文件和行号。
2. 专门检查是否仍有把 dirty `/root/ESCNet` 当 clean baseline 的命令或表述。
3. 专门检查 baseline 三数据集历史结果、CAMO 概率复评和 clean snapshot strict load 三者的边界是否清晰。
4. 专门检查 speed/FPS 是否仍被写成最终结论。
5. 专门检查 KD/B0/MobileMamba 是否被误写成已完成主结果。
6. 给出最多 8 条具体修订建议；不要泛泛建议。

最终回报按审查格式写入目标文件，并在消息中只给摘要。
```

## P0 GPU Queue Operator And Gate Validator

```text
先阅读并遵守公共目标提示：/root/data-tmp/workspace/03_agent_tasks/prompts/MASTER_TARGET_PROMPT.md
再阅读权威队列：/root/data-tmp/workspace/02_experiments/scripts/GPU_QUEUE.md
再阅读短接力卡片：/root/data-tmp/workspace/03_agent_tasks/pending/P0_gate1_kd_handoff_card.md
再阅读定稿门槛：/root/data-tmp/workspace/04_paper/drafts/finalization_gates.md
再阅读 Gate 结果验收 runbook：/root/data-tmp/workspace/03_agent_tasks/acceptance/gate_result_acceptance_runbook.md
再阅读当前状态：/root/data-tmp/workspace/00_project/orchestrator_tick_latest.md、/root/data-tmp/workspace/00_project/orchestrator_tick_latest.json、/root/data-tmp/workspace/02_experiments/runs/b0_external_status_latest.md、/root/data-tmp/workspace/00_project/orchestrator_status.md 和 /root/data-tmp/workspace/00_project/resume_handoff.md

你是 GPU 队列接管与 gate 验收 worker。任务：在四卡资源释放后，按主控已定义顺序推进 clean baseline 复评、KD 恢复训练、KD 评测和同条件速度复测，并把每一步结果交给主控验收。

所有准则必须遵守：不偷懒，不因为怕风险而保守。不要因为 KD 有风险就跳过；也不要为了“看起来完成”把历史结果、dirty-tree 结果或 partial checkpoint 写成 final evidence。

关键边界：
- 当前 `/root/ESCNet` 是 dirty 外部探索工作树，不是 clean baseline。
- Gate 1 clean baseline 已完成；baseline/resume watcher 不需要运行，不要重复启动 wrapper。
- clean baseline 只能使用 `/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean`。
- ESCNet-B5 teacher checkpoint 固定为 `/root/data-tmp/epoch_120.pth`。
- 不得使用 `/root/ESCNet/checkpoints/escnet/epoch_120.pth` 作为 teacher 或主 baseline。
- 大文件、日志、TMPDIR 只能写入 `/root/data-tmp/workspace` 或 `/root/data-tmp/tmp`。
- 如果发现已有 watcher 存活，不要重复启动 watcher；先读日志判断是否已经托管。

执行顺序：
1. 只读刷新状态：
   - 先读 `/root/data-tmp/workspace/00_project/orchestrator_tick_latest.md` 和 `/root/data-tmp/workspace/00_project/orchestrator_tick_latest.json`。
   - 例行 B0 状态刷新使用：`python /root/data-tmp/workspace/02_experiments/scripts/sync_b0_observation_state.py --skip_release_audit`
   - 例行 MobileMamba 状态刷新使用：`python /root/data-tmp/workspace/02_experiments/scripts/summarize_external_mobilemamba.py`
   - 例行 KD recovery 状态刷新使用：`python /root/data-tmp/workspace/02_experiments/scripts/summarize_kd_recovery.py`
   - 若发现 B0 新 checkpoint、新 COD10K 指标行，或准备回报/交接，使用完整同步：`python /root/data-tmp/workspace/02_experiments/scripts/sync_b0_observation_state.py`
   - 该同步入口只调用只读观察、趋势图、tick 和审计流程；不得启动、停止或 signal 训练。
   - `nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader,nounits`
   - `ps -eo pid,ppid,stat,etime,cmd | grep -E 'torchrun|train.py|run.sh' | grep -v grep`
2. 若外部 B0 或 MobileMamba 仍占用四卡，先按最新用户指令和 `orchestrator_tick_latest.md` 判断；B0 不在当前计划范围，应停止，其他外部分支除非用户明确要求不抢占。
3. Gate 1 已完成；不要重复启动 baseline wrapper 或 resume watcher。
4. Gate 1 完成后复核：
   - baseline run 三数据集完整。
   - `metrics_all.csv` 对应行 `status=clean_prob_re_eval_complete`。
   - `check_run_integrity.py` 通过。
   - `run_release_audits.sh` 通过。
5. Gate 1 通过后运行 Gate 2 KD 恢复：
   - `TMPDIR=/root/data-tmp/tmp bash /root/data-tmp/workspace/02_experiments/scripts/start_kd_full_train.sh`
   - 若四卡 batch2 workers0 再次 SIGKILL，按 `kd_interruption_analysis.md` 降级双卡、单卡，不直接放弃 KD。
6. KD 完成后运行三数据集 probability eval，命令以 `GPU_QUEUE.md` 第 3 节为准。
7. 最后在 GPU 空闲时运行 Gate 3 同条件 speed profile；没有空闲条件时只记录 pending，不写速度结论。

允许写入：
- `/root/data-tmp/workspace/02_experiments/runs/baseline_escnet_b5_clean_prob_e120/`
- `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_recover_b2w0_4gpu/`
- `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_recover_b2w0_4gpu_prob_eval/`
- 新 profile run 目录，必须在 `/root/data-tmp/workspace/02_experiments/runs/`
- `/root/data-tmp/workspace/03_agent_tasks/reports/P0_gpu_queue_operator.md`

最终回报必须包含：
任务 ID / 实验 ID:
完成状态: pass / partial / fail
GPU 空闲证据:
启动或未启动原因:
使用命令:
写入或修改文件:
新增 metrics/profile/status:
完整性检查结果:
release audit 结果:
风险和异常:
是否可入论文: yes / no / only as reference / only as failure analysis
下一步:
```
