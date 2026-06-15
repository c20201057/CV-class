# Subagent Reviews

## Maxwell: ESCNet 基底侦察

状态：通过。

优点：

- 确认 `/root/ESCNet` 适合作为强基线/教师模型和轻量化改造起点。
- 具体定位了核心文件：`models/ESCNet.py`、`models/modules/AETP.py`、`models/modules/Decoder.py`、`models/backbones/build_backbone.py`、`train.py`、`test.py`、`eval.py`。
- 给出参数瓶颈判断：默认 ESCNet-B5 约 99.90M 参数，PVTv2-B5 主干约 81.44M；B2-C64 约 29.81M，适合作为主 student。
- 指出 `test.py` 二值化、`eval.py` 追加写、`inter_channel=128` 硬编码、`resume` 未实际加载等可信度风险。
- 给出了可直接派发的 smoke test、baseline CAMO 推理/评估命令和四卡训练模板。

主控采纳：

- 将 B2-C64 定为 P0 主模型。
- 将概率图推理与评估套件定为 P0/P1 工程任务。
- 后续所有实验使用 workspace run 目录，不复用 `/root/ESCNet/preds/results/checkpoints`。

结论：接收，用于 `project_profile.md`、`route_decision.md`、`master_plan.md` 和后续工程 prompt。

## Mill: 环境与数据侦察

状态：通过。

优点：

- 确认四卡环境：4 x Tesla V100-SXM2-16GB，PyTorch 2.5.1+cu121，CUDA 可用。
- 确认数据集结构完全匹配 `dataset.py`：Train 4040，COD10K-Test 2026，CAMO-Test 250，NC4K 4121。
- 确认 baseline 产物存在：`epoch_120.pth`、三数据集预测、`results_epoch120/result.txt`。
- 发现关键系统风险：根分区接近满载，`/root/data-tmp` 空间充足，必须把所有新大文件写入 workspace。
- 验证随机输入前向成功，输出 edge 与四层 mask shape 合法。

主控采纳：

- `master_plan.md` 增补磁盘空间约束和 DDP 配置注意事项。
- 四卡用于完整主实验，但保存路径必须指向 `/root/data-tmp/workspace/02_experiments/runs/<exp_id>`。
- 不按 `requirements.txt` 重装环境，优先保持当前可跑的 cu121 环境。

结论：接收，用于环境约束、GPU 调度和实验运行规范。

## Galileo: 文献核验

状态：通过。

优点：

- 按基准、经典、轻量、频域边界、扩展方向分组，符合论文结构。
- 给出了可用链接和每篇文献在本项目中的用途。
- 明确 R2C7K、CamoVid60K 更适合作未来工作，避免主线发散。

需要主控注意：

- CSFIN、FMLNet、FDESNet、edge screening/cross-layer fusion 等部分来源公开材料有限，正文引用时应避免过度展开。
- 轻量化主线优先引用 DGNet/FINet/BPNet/CSFIN，不需要把所有 2026 工作写成重点。

结论：接收，用于 `01_literature/verified_literature.md` 和论文相关工作。

## Ohm: Workflow 方案

状态：通过。

优点：

- 给出了清晰的 workspace 结构。
- 脚本清单覆盖实验初始化、训练、评估、指标汇总、profiling、可视化、完整性检查。
- 强调目录存在即失败、每个 run 独立输出，适合多 agent 协作。

主控调整：

- 本工作区已采用编号目录：`00_project`、`02_experiments`、`03_agent_tasks` 等。
- 暂先落文档和脚本规格，具体脚本实现交给后续工程 agent。

结论：接收，用于 `workflow.md`、`SCRIPT_SPECS.md` 和 agent prompt 模板。

## Zeno: ESCNet 代码审计

状态：通过。

优点：

- 明确了 ESCNet 的结构瓶颈：PVT-B5、DeformConv2d、patch injection、高分辨率 MTA/SA、FEM 大核分支。
- 给出可执行的低风险改造顺序：B5->B2、C128->C64、B0-C64、再考虑 DeformConv/FEM/MTA。
- 补充了关键参数量估算：B2-C128 约 43.3M，B2-C64 约 29.8M，B0-C64 约 8.34M。
- 指出了影响实验可信度的问题，尤其是二值预测、append result、autocast float32、resume 未使用。

主控调整：

- 将 B2-C64 定为 P0 主实验 student。
- 将 B0-C64 定为极限压缩候选，不作为第一完整训练优先级。
- 将概率图推理和 profiling 工具列为 P0/P1 工程任务。

结论：接收，用于项目画像、路线判断、实验矩阵和后续工程 prompt。

## Pauli: P0 Baseline Profiling

状态：通过，标记为 initial profile。

优点：

- 实现 `02_experiments/scripts/profile_model.py`，支持 checkpoint/随机初始化 profile。
- 生成 baseline profile：`02_experiments/runs/profile_escnet_b5_416/profile.json`。
- 更新 `02_experiments/tables/profiles.csv`。
- 记录完整环境、设备、warmup/repeat、checkpoint load 状态。

复核结果：

- Params: 99,903,234。
- Model size: 381.169 MB。
- FLOPs: 258.044 GFLOPs，129.022 GMACs。
- Latency: 62.998 ms，FPS: 15.873。
- Peak GPU memory: 829.771 MB。

主控注意：

- FLOPs 来自 `torch.profiler.profile(with_flops=True)`，为估计值，unsupported ops 可能未计入。
- 可作为当前论文效率表初始证据；主表前建议用同一脚本对所有模型统一复跑。
- 主控发现并修复 `profile_model.py` 中 `inter_channel` 写死 128 的记录字段；已重跑 baseline 与 Light B2-C64 profile。

结论：接收。

## Aristotle: Paper Narrative Review

状态：通过，只读审查。

优点：

- 明确指出当前论文贡献“效率和 workflow 已站住，精度与 KD 结论未站住”，避免提前夸大。
- 建议主叙事改为“基于 ESCNet 的有约束轻量化 + 统一评测协议 + 精度-效率分析”，而不是宣称全新 SOTA。
- 给出主表、结构消融表、KD 消融表和效率表的列设计。
- 强调主表必须使用概率图协议，不能混入 `test.py` 二值化输出。
- 提醒 Light B2-C64 profile 当前为结构 profile，参数量/GMACs 可写，最终 latency/FPS 建议训练后复测。

主控采纳：

- 已新增论文初稿 `/root/data-tmp/workspace/04_paper/drafts/paper_draft.md`，谨慎区分已验证效率证据和待评测精度结论。
- 已新增 `/root/data-tmp/workspace/04_paper/tables/main_results_template.md` 与 `result_fill_checklist.md`。
- 后续论文最终结论等待 Light no-KD、KD 三数据集概率评测后再定稿。

结论：接收，用于论文写作边界和表格设计。

## Poincare: KD Route Proposal

状态：通过，proposal 已接收。

优点：

- 在独立 proposals 目录写出 KD 方案，未触碰正在训练的 no-KD 代码和 run 目录。
- 明确 teacher 固定为 `/root/data-tmp/epoch_120.pth`，student 为 PVTv2-B2 + C64。
- 比较 online teacher KD 与 cached logits KD，指出训练增强导致缓存方案容易错位。
- 推荐先做 online output-level MSE KD，初始 `kd_weight=0.5`、`kd_warmup_epochs=5`。
- 给出 smoke、full train、eval、profile 命令规划。

主控采纳：

- 已复制独立 KD 代码目录 `/root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64`。
- 已新增 `kd.py`、`configs/kd_light_b2_c64.yaml`、`configs/teacher_b5.yaml`、`tools/smoke_kd_online.py`。
- 已修改 KD 副本内 `config.py` 和 `train.py`，实现 online teacher MSE KD；未修改 `/root/ESCNet` 或 no-KD 代码目录。
- 已通过 `py_compile`、配置加载检查、CPU teacher checkpoint 加载检查；GPU smoke 等当前四卡 no-KD 训练结束后执行。

结论：接收，作为 KD 实验 P1 的工程起点。

## Ptolemy: P0 Evaluation Suite

状态：工具通过，smoke 指标不入论文。

优点：

- 实现 `run_eval_suite.sh` 与 `collect_metrics.py`。
- 评估输出隔离到 `runs/<exp_id>/preds/<DATASET>` 与 `results/<DATASET>`。
- CAMO smoke 完整跑通，GT 250、pred 250。
- CSV 解析具备幂等更新能力。

复核结果：

- CAMO smoke 指标：Smeasure 0.811，wFmeasure 0.761，meanFm 0.800，meanEm 0.873，MAE 0.067。
- 该结果低于既有 baseline CAMO 行，不能直接入主表。

主控判断：

- 差异高度提示预测协议/配置/推理实现不可比，尤其 `test.py` 的二值化预测问题。
- `P1_probability_inference` 升级为评估协议定稿前置任务。

结论：接收工具，不接收 smoke 指标作为论文结果。

## Dewey: P0 Light-ESCNet B2-C64

状态：通过。

优点：

- 在隔离副本 `02_experiments/code/light_escnet_b2_c64/` 实现 B2-C64，没有直接修改 `/root/ESCNet`。
- `inter_channel` 已配置化，默认兼容 128。
- `config.py` 新增 `inter_channel` 与 `bb_pretrained`。
- smoke 通过：edge `[1,1,416,416]`，mask `[13,13]/[26,26]/[52,52]/[416,416]`。
- 参数量 29,807,714，符合 29.8M 目标。

主控补充：

- 已下载官方 PVTv2-B2 权重到 `/root/data-tmp/weights/pvt_v2_b2.pth`，SHA256: `80711cd1b37ffba12bec6c7a2a7c54efe2315ed635e6d2055fd51c3e909ede4d`。
- 已更新 `02_experiments/configs/light_b2_c64.yaml`：`bb_pretrained: true`，`weights.pvt_v2_b2` 指向新权重，run name 改为 `light_b2_c64_e120_s42`。
- 复跑 smoke 通过，`bb_pretrained: true`。
- 已用同一 profile 工具测得 Light B2-C64：29.81M params，36.39 GMACs，113.74 MB，38.73 ms，25.82 FPS，237.44 MB peak memory。

结论：接收，具备启动完整训练的工程条件。

## Huygens: P1 Probability Inference

状态：工具通过；发现 baseline checkpoint mismatch。

优点：

- 新增 `02_experiments/scripts/infer_prob.py`，不修改 `/root/ESCNet/test.py` 或 `eval.py`。
- 输出 sigmoid 概率图，按 GT 原尺寸保存，目录结构兼容 `eval.py`。
- CAMO smoke 数量对齐：GT 250，pred 250。
- 灰度检查确认不是纯二值输出。

重要发现：

- 使用 `/root/ESCNet/checkpoints/escnet/epoch_120.pth` 重新推理 CAMO，概率图指标约 S=.819、MAE=.069，低于历史 baseline。
- 历史预测用当前 `eval.py` 复评正常。
- 主控追查发现 `/root/ESCNet/checkpoints/escnet/epoch_120.pth` 是 2026-06-13 后续重训 checkpoint，而历史预测生成于 2026-06-11。
- `/root/data-tmp/epoch_120.pth` 与历史预测时间匹配；用它重新 CAMO 概率推理得到 S=.881、wF=.842、meanF=.864、meanE=.933、MAE=.043，接近历史 baseline。

主控采纳：

- `infer_prob.py` 接收为后续统一评估基础设施。
- Teacher checkpoint 固定为 `/root/data-tmp/epoch_120.pth`。
- `/root/ESCNet/checkpoints/escnet/epoch_120.pth` 标记为后续重训产物，不进入主 baseline。

结论：接收。

## Main: Light B2-C64 Full Train And Eval

状态：通过，作为当前论文主 student 结果。

复核结果：

- 完整训练 run：`/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42`。
- 最终 checkpoint：`epoch_120.pth`。
- 训练 loss：epoch 120 avg loss 1.369。
- 训练后 profile：29.81M params，36.39 GMACs，113.74 MB model size，237.44 MB peak memory。
- 概率图评测 run：`/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42_prob_eval_v2`。
- CAMO：S=.862，wF=.818，meanF=.843，meanE=.918，MAE=.051。
- COD10K：S=.866，wF=.782，meanF=.808，meanE=.928，MAE=.024。
- NC4K：S=.886，wF=.840，meanF=.862，meanE=.933，MAE=.033。

验收说明：

- `run_prob_eval_suite.sh` 在 NC4K eval 打印完结果后被系统 SIGKILL，未执行最后的 `collect_metrics.py`。
- `results/NC4K/result.txt` 已完整写入；主控手动执行 `collect_metrics.py`，并补写 `integrity.csv` 中 NC4K 行。
- `check_run_integrity.py` 对 CAMO/COD10K/NC4K 通过，预测数量分别为 250/2026/4121，且概率图灰度唯一值检查通过。

主控判断：

- Light B2-C64 no-KD 可以支撑论文核心效率-精度折中结论。
- 相对历史 ESCNet-B5，平均 S-measure 下降约 .009，平均 MAE 增加约 .006；CAMO 的 wF/MAE 下降最需要 KD 或边界补偿解释。
- 训练后 latency/FPS profile 受并发任务影响，最终速度结论需要空闲 GPU 同条件复测。

结论：接收，写入 `metrics_all.csv`、`aggregated_results.md`、`main_results_template.md` 和论文草稿。

## Main: KD B2-C64 Smoke And Full-Train Interruption

状态：部分通过，full train 待重启。

复核结果：

- KD 代码目录：`/root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64`。
- batch 1 GPU smoke 通过，peak memory 约 2298.573 MB。
- batch 4 GPU smoke 通过，peak memory 约 6730.948 MB。
- full train 启动后完成 epoch 4，epoch 5 iter 50 后 rank0 收到 SIGKILL。
- 中断前 avg loss：epoch 1 为 4.172，epoch 2 为 3.452，epoch 3 为 3.194，epoch 4 为 2.949。

主控判断：

- 中断更像系统资源/并发冲突，不是 KD 代码逻辑错误。
- 已将 KD run config 调整为 `save_last: 120` 和 `save_step: 1`，下次重启将每个 epoch 保存 checkpoint。
- 当前四卡被 PVTv2-B0 蒸馏分支占用；KD B2-C64 full train 等四卡释放后重启。

结论：smoke 接收，full train 结果暂不入论文结论。

后续更新：

- 2026-06-13T15:54Z 后，主控给 `kd_light_escnet_b2_c64/train.py` 增加 resume 支持：可从 `resume` 指向的 `epoch_N.pth` 继续，并在新 checkpoint 保存时额外写 `latest_train_state.pth`。
- 第一次 rerun 保存 `epoch_1.pth` 至 `epoch_5.pth` 后，在 epoch 6 附近出现 `DataLoader worker ... killed`。
- 已生成安全恢复配置 `config_resume_epoch5_workers0.yaml`，设置 `resume=epoch_5.pth`、`num_workers=0`；恢复日志确认 `loaded_epoch=5, start_epoch=6`，并已进入 epoch 6。注意：该状态随后失败，见下方二次后续更新。

二次后续更新：

- workers=0 恢复在 epoch 6 iter 100/252 后 rank0 收到 SIGKILL，未保存 `epoch_6.pth`。
- 当前 KD 只有 `epoch_1.pth` 至 `epoch_5.pth` partial checkpoints；`epoch_5.pth` 是唯一有效恢复点，不能作为论文 KD 结果。
- 中断分析与恢复策略已写入 `02_experiments/runs/kd_light_b2_c64_e120_s42/kd_interruption_analysis.md`。
- 当前四卡被 `/root/ESCNet` 外部 PVTv2-B0 online KD 任务占用；主控不主动抢占，等待独占 GPU 窗口后再恢复 KD B2-C64。

## Feynman: Paper Revision Plan

状态：通过。

复核结果：

- 写入文件：`/root/data-tmp/workspace/04_paper/drafts/paper_revision_plan.md`。
- 写入范围合规：未修改 `paper_draft.md`、表格或实验文件。
- 内容聚焦论文成稿风险：明确 no-KD B2-C64 已可支撑主结论，KD、B0、B2-C128 与去边界分支均不能提前写成已验证结果。

主控判断：

- 接收其写作主线：论文应定位为“基于 ESCNet 的诚实轻量化改造与精度-效率验证”，而不是夸大为全新网络。
- 接收其表述边界：摘要、贡献点和结论只写已完成的 Light B2-C64 结果；KD/B0 只作为补偿分支或待验证实验。
- 接收其风险提示：训练后 latency/FPS 曾受并发污染，最终速度指标需要空闲 GPU 同条件复测。

结论：接收；作为下一轮 `paper_draft.md` 改写依据。

## Lagrange: Experiment Gap Audit

状态：通过。

复核结果：

- 写入文件：`/root/data-tmp/workspace/05_reviews/experiment_gap_audit.md`。
- 写入范围合规：未启动训练、未使用 GPU、未修改实验产物或表格。
- 审计结论与主控记录一致：Light B2-C64 no-KD 可入论文；baseline 统一概率复评、KD full train、空闲 GPU 速度复测和可视化仍是主要缺口。

主控判断：

- 接收 P0 阻塞排序：先 baseline 三数据集概率复评、KD full train/eval、空闲 GPU latency/FPS 复测。
- 接收风险判断：KD 未完成前不能写有效性；B2-C128/B5-C64 未完成前不能拆分主干与解码器贡献；可视化缺失会削弱 CAMO 下降解释。
- 已修复其指出的 `aggregated_results.md` 速度误导风险：`light_b2_c64_trained_416` 现在使用训练后 profile 的 params/GMACs 等结构数值，但表中不再输出 FPS/latency，统一标记为 pending idle re-test。

结论：接收；作为 GPU 空闲后命令队列和论文结果边界依据。

## Schrodinger: Literature Gap Update 2026

状态：通过。

复核结果：

- 写入文件：`/root/data-tmp/workspace/01_literature/literature_gap_update_2026.md`。
- 写入范围合规：未修改论文正文、实验文件或训练配置。
- 主控抽查了 FINet、BPNet、CamoFormer、ESCNet、HGINet、CamoTeacher、SAM-COD、CSFIN、CFF-KDNet 和 Ulcod-net 的公开来源；核心标题、年份、用途基本可用。

主控判断：

- 接收 novelty 边界：本文应写成“基于 ESCNet 强基线的可控轻量化改造与统一评测”，不能写成首个轻量 COD、首个边界感知轻量 COD、首个 KD-COD 或 SOTA。
- 接收 related work 组织：强 COD/Transformer、轻量 COD、KD/teacher-student、PVTv2 主干四段足够支撑论文，不需要把开放词汇和视频方向放进主实验。
- 已将核验过的 2024-2026 文献补充到 `01_literature/verified_literature.md`；CFF-KDNet 和 Ulcod-net 只作谨慎引用。

结论：接收；作为 related work 与贡献边界依据。

## Lagrange: Paper Evidence Audit

状态：通过，只读审查，主控已处理。

复核结果：

- 审查文件：`04_paper/drafts/paper_draft.md`、`04_paper/tables/main_results_template.md`、`04_paper/tables/aggregated_results.md`、`02_experiments/tables/metrics_all.csv`、`02_experiments/tables/profiles.csv`。
- 写入审查记录：`05_reviews/paper_evidence_audit_20260613.md`。
- 指出 baseline 三数据集主表与“统一概率图协议”之间的证据边界：ESCNet-B5 当前仍以历史三数据集结果为主，只有 CAMO 完成概率图复评。
- 指出 latency/FPS 证据风险：Light clean FPS 是 preliminary structural profile，trained-checkpoint speed 受并发污染，不能写成最终速度结论。
- 指出 KD 损失描述应落到当前实现的 output-level MSE，KL 只能作为后续替代。
- 指出消融章节应写成计划与待补项，可视化结论应绑定 CAMO per-image MAE case selection。

主控采纳：

- 已收紧 `paper_draft.md` 的 baseline、速度、KD、消融、可视化和训练集表述。
- 已将 `main_results_template.md` 与 `aggregated_results.md` 的 FPS/latency 改为 pending idle re-test。
- 已把参考文献从占位替换为已核验条目。

结论：接收；作为论文定稿前证据边界检查的一部分。

## Epicurus: Paper Baseline Boundary Audit

状态：通过，只读审查，主控已处理。

复核结果：

- 审查文件：`04_paper/drafts/paper_draft.md`、`04_paper/tables/main_results_template.md`、`04_paper/tables/aggregated_results.md`、`04_paper/drafts/evidence_index.md`、`02_experiments/tables/metrics_all.csv`。
- 写入审查记录：`05_reviews/paper_baseline_boundary_audit_20260613.md`。
- 核心问题是 ESCNet-B5 历史三数据集结果、CAMO-only probability re-eval、clean snapshot strict load 三类证据容易被读成同一个 final baseline。
- 同时指出 `metrics_all.csv` 缺少机器可读协议/边界字段，`aggregated_results.md` 与主表容易把 historical reference 当完整主表 baseline。

主控采纳：

- `main_results_template.md` 已拆成 Light 完整概率评测、ESCNet-B5 历史参考/验证、KD/B0 pending 三块。
- `metrics_all.csv` 和 `collect_metrics.py` 已补充 `protocol`、`repo_boundary`、`checkpoint`、`status` 字段。
- `aggregate_results.py` 已改为输出 `Speed Status` 和 `Metric Status`，不再抄写未复测的 FPS。
- `paper_draft.md`、`evidence_index.md`、`writing_status.md`、`orchestrator_status.md` 已将 Light-vs-ESCNet 差值降级为“相对历史参考行”，最终 baseline 差值等待 clean snapshot 三数据集复评。
- B0 继续作为外部高风险观察，不进入主表；epoch 20 中间 eval 退化且尚无 checkpoint。

结论：接收；该审查已经变成当前论文证据边界的硬门槛。

## Lagrange: Submission Protocol Audit

状态：通过，主控已处理。

复核结果：

- 审查 `submission_protocol_checklist.md`、`finalization_gates.md`、`metrics_all.csv` 和当前主表证据边界。
- 判断当前 checklist 与 gate 主方向一致：historical baseline、CAMO-only verification、未完成 KD 和 B0 external branch 都不能进入 final 主表。
- 指出 final pass 需要更硬的禁令：final 主表只允许 `final_main_light`、`clean_prob_re_eval_complete`、`final_main_kd`，并且不得把 CAMO-only teacher verification 与 historical COD10K/NC4K 拼成一行。
- 指出 B0 intermediate metrics 和 KD partial checkpoints 不能进入主表、平均差值、摘要或结论。

主控采纳：

- `submission_protocol_checklist.md` 已写入 final 主表 status 白名单、forbidden status 禁令、CAMO-only 拼接禁令、B0 intermediate 禁令和 KD partial checkpoint 禁令。
- `run_release_audits.sh` 已纳入 evidence audit、claim audit、interim number audit、asset audit、claim-evidence matrix audit 和 final Light integrity check。

结论：接收；作为最终入表和 release audit 的执行边界。

## Feynman: Paper Gate Patch Matrix Review

状态：通过，主控已处理。

复核结果：

- 写入文件：`/root/data-tmp/workspace/05_reviews/paper_gate_patch_matrix_review_feynman.md`。
- 判断 `paper_gate_patch_matrix.md` 覆盖了 Gate 1/2/3 的主入口，但仍需强调结论段、`evidence_index.md`、自动审计/readiness 产物、`aggregated_results.md` coverage/notes 和图注同步。
- 指出 Gate 2 后 KD 不改善时必须有明确失败分析落点，不能写成贡献。
- 指出 Gate 3 需要允许 KD 未完成但 baseline/Light controlled speed 已完成的分支，并把 KD speed 标为 absent。

主控采纳：

- `paper_gate_patch_matrix.md` 已补充外部复核说明，并把上述风险纳入 Gate 1/2/3 必改清单或验收分支。
- `paper_submission_readiness.md`、`finalization_gates.md` 和 `GPU_QUEUE.md` 继续作为 gate 前后的短链路执行入口。

结论：接收；Gate 1/2/3 任一结果回来后，按该 review 和 patch matrix 双重检查，不直接改摘要或结论。
