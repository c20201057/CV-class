# Script Specs

这些脚本是后续工程 agent 的实现任务，不要求一次全部完成。优先级按 P0/P1/P2 排列。

## P0

### `profile_model.py`

功能：加载指定 config/model/checkpoint，输出参数量、FLOPs、latency、FPS、peak memory。

输入：

- `--repo <ESCNet-compatible code directory>`
- `--config <config.yaml>`
- `--ckpt <epoch.pth>`
- `--out <profile.json>`

说明：clean ESCNet-B5 baseline 的后续复评/复测应使用
`/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean`，不要直接使用
dirty `/root/ESCNet` 工作树。

验收：

- 随机输入可完成一次 forward。
- 输出 JSON 至少包含 `params`, `model_size_mb`, `latency_ms`, `fps`, `device`, `img_size`。
- 若 FLOPs 依赖包不可用，必须明确写 `flops_status: unavailable`，不能静默跳过。

### `run_eval_suite.sh`

功能：对 CAMO/COD10K/NC4K 批量运行 `test.py` 和 `eval.py`。

验收：

- 每个数据集预测目录数量等于 GT 数量。
- 每个数据集生成独立 `result.txt`。
- 不写入主仓库公共 `preds/results`。

### `run_prob_eval_suite.sh`

功能：对 CAMO/COD10K/NC4K 批量运行概率图推理 `infer_prob.py` 和 `eval.py`，作为论文主表评估协议。

轻量模型用法：必须通过 `--template_config <run_dir>/config.yaml` 指定训练配置，避免回退到代码目录默认 ESCNet-B5/C128 配置。

验收：

- 每个数据集预测目录数量等于 GT 数量。
- 抽样预测图 unique gray values 大于 2。
- 每个数据集生成独立 `result.txt`。
- 汇总到公共 `metrics_all.csv` 或调用者指定 CSV。
- 汇总行必须写入 `protocol`、`repo_boundary`、`checkpoint`、`status`；字段为空的结果不能进入论文主表。
- 不写入主仓库公共 `preds/results`。

### `start_baseline_prob_eval_clean.sh`

功能：封装 ESCNet-B5 clean baseline 三数据集概率图复评，固定使用
`/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean` 和
`/root/data-tmp/epoch_120.pth`。

验收：

- 默认 exp id 为 `baseline_escnet_b5_clean_prob_e120`。
- GPU 已有训练进程时默认拒绝启动，除非显式传入 `--force_busy_gpu`。
- 调用 `run_prob_eval_suite.sh` 后自动运行 `check_run_integrity.py`。
- 默认 Gate 1 三数据集完整复评完成后，自动调用
  `run_release_audits.sh --add-integrity <baseline_run> baseline_escnet_b5_clean_prob_e120 CAMO,COD10K,NC4K`。
- 不直接使用 dirty `/root/ESCNet` 工作树。

### `collect_metrics.py`

功能：解析多个 `result.txt`，汇总成 CSV/Markdown。

验收：

- 输出字段包含 `exp_id,dataset,method,Smeasure,wFmeasure,meanFm,meanEm,MAE,source,protocol,repo_boundary,checkpoint,status`。
- 可解析已有 `/root/ESCNet/results_epoch120/result.txt` 的副本。

## P1

### `init_experiment.py`

功能：创建 run 目录、复制 config、写 metadata。

验收：

- 已存在 `exp_id` 时失败，不覆盖。
- config 输出路径指向 run 目录。

### `make_visual_grid.py`

功能：生成论文对比图。

验收：

- 输出图片非空。
- 各列样本严格同名对齐。

### `summarize_train_log.py`

功能：解析训练日志中的 epoch avg loss，输出 CSV/Markdown，用于训练曲线和状态追踪。

验收：

- 能解析 `@==Final== Epoch[...] Avg Training Loss` 行。
- 输出字段包含 `epoch,total_epochs,avg_loss`。
- 若日志没有可解析 epoch 行，必须明确失败。

### `check_run_integrity.py`

功能：检查单个实验是否可入表。

验收：

- 缺 checkpoint、缺预测、指标缺失、数量不一致都给出明确错误。

当前实现说明：

- 支持 `--run_dir`、`--exp_id`、`--datasets`、`--metrics_csv`。
- 默认检查 `preds/<DATASET>/<method>`、`results/<DATASET>/result.txt` 或 `eval/<DATASET>/result.txt`。
- metric 缺失先作为 warning；预测/GT 数量不一致作为 error。

### `audit_paper_evidence.py`

功能：检查 `metrics_all.csv` 中的论文入表证据边界，防止历史参考、CAMO-only
verification、未完成 KD 或 B0 外部分支被误写成 final paper evidence。

验收：

- 必须检查 `protocol`、`repo_boundary`、`checkpoint`、`status` 等 metadata 字段。
- `final_main_light`、`final_main_kd`、`clean_prob_re_eval_complete` 必须使用 `prob_map`。
- final 状态必须覆盖 CAMO、COD10K、NC4K 三个数据集。
- historical/reference/verification-only 行只能作为 note，不能导致主表 final 通过。
- B0/extreme branch 若被标成 final 必须报错。
- final 状态不得使用 `dirty_history_result` 或 `legacy_repo_camo_verification`。
- final checkpoint 必须位于 `/root/data-tmp/workspace`，或为固定 teacher `/root/data-tmp/epoch_120.pth`。

当前实现说明：

- 默认读取 `/root/data-tmp/workspace/02_experiments/tables/metrics_all.csv`。
- 默认写出 `/root/data-tmp/workspace/04_paper/drafts/paper_evidence_audit_latest.md`。
- 当前审计状态为 pass；baseline historical rows 和 teacher CAMO verification row 被记录为 reference notes。

### `audit_claim_text.py`

功能：扫描论文交付文本是否出现超出当前 evidence gates 的主张。默认只扫描
`paper_draft.md`、`paper_outline.md`、`main_results_template.md` 和
`aggregated_results.md`，避免把 gate/checklist 文档中的禁令本身误报。

验收：

- 禁止 SOTA/first KD-COD/实时或边缘端部署等无证据强主张。
- Gate 1 之前禁止把 ESCNet-B5 写成 final clean probability baseline。
- Gate 2 之前禁止写 KD 提升或缩小差距。
- Gate 3 之前禁止写 latency/FPS 最终速度提升。
- Gate 4 之前禁止 B0 进入主表或主结论。

当前实现说明：

- 脚本路径：`/root/data-tmp/workspace/04_paper/scripts/audit_claim_text.py`。
- 默认报告：`/root/data-tmp/workspace/04_paper/drafts/claim_text_audit_latest.md`。
- 当前审计状态为 pass。

### `run_release_audits.sh`

功能：非 GPU 总验收入口，串联论文 evidence metadata、claim text、当前 delta 摘要刷新和 final probability run integrity 检查。

验收：

- 默认运行 `audit_paper_evidence.py`。
- 默认运行 `audit_claim_text.py`。
- 默认运行 `generate_delta_summary.py`，输出 `04_paper/drafts/current_delta_summary.md`。
- 默认运行 `audit_gate_patch_readiness.py`，检查 Gate 1/2/3 是否处于 pending、ready_to_patch 或 partial_invalid 的安全状态。
- 默认检查当前唯一 final 主结果 `light_b2_c64_e120_s42_prob_eval_v2` 的 CAMO/COD10K/NC4K 预测数量、结果文件和 metrics 行。
- 支持 `--add-integrity RUN_DIR EXP_ID DATASETS`，用于把后续 clean baseline、KD 或其他 final run 纳入同一次 release gate。
- 任一子检查失败时整体失败，不允许继续定稿。

当前实现说明：

- 脚本路径：`/root/data-tmp/workspace/02_experiments/scripts/run_release_audits.sh`。
- 不启动训练或评测，不占 GPU。
- 使用 `flock` 和唯一临时报告文件保护 `release_audit_latest.md`，避免并发/重入写入导致 wrapper 误报失败。

### `audit_gate_patch_readiness.py`

功能：只读检查 Gate 1 clean baseline、Gate 2 KD 和 Gate 3 controlled speed 是否已经满足论文回填触发条件。

验收：

- Gate 未完成时输出 `pending` 并整体通过，提醒论文保持当前证据边界。
- 如果发现半落盘结果，例如只出现部分数据集、status/protocol 不一致、source/checkpoint/profile_json 缺失，输出 `partial_invalid` 并失败。
- Gate 1 ready 条件：`baseline_escnet_b5_clean_prob_e120` 覆盖 CAMO/COD10K/NC4K，三行均为 `protocol=prob_map` 和 `status=clean_prob_re_eval_complete`。
- Gate 2 ready 条件：KD probability eval 覆盖 CAMO/COD10K/NC4K，三行均为 `protocol=prob_map` 和 `status=final_main_kd`。
- Gate 3 ready 条件：baseline 与 Light 均有 idle profile 行，并且 device/img_size/warmup/repeat 等可比字段一致。
- 默认报告：`/root/data-tmp/workspace/04_paper/drafts/gate_patch_readiness_latest.md`。

当前实现说明：

- 脚本路径：`/root/data-tmp/workspace/04_paper/scripts/audit_gate_patch_readiness.py`。
- 当前 Gate 1/2/3 均为 pending，状态安全；已接入 `run_release_audits.sh`。

### `orchestrator_tick.py`

功能：生成目标模式的一页只读总览，把当前 Gate 状态、B0/MobileMamba 外部观察分支、GPU/进程快照、watcher、
release audit 和 Light-B2-C64 核心结果汇总到 Markdown/JSON，供主控和 subagent 快速恢复上下文。

验收：

- 不启动、不停止、不 signal 任何训练或评测进程。
- 默认可调用 `summarize_external_b0.py` 和 `summarize_external_mobilemamba.py`
  刷新只读外部分支状态；支持 `--no_refresh_b0` 和 `--no_refresh_mobilemamba` 跳过刷新。
- 默认输出：
  - `/root/data-tmp/workspace/00_project/orchestrator_tick_latest.md`
  - `/root/data-tmp/workspace/00_project/orchestrator_tick_latest.json`
- Markdown 必须包含 Gate 1/2/3/4A/4B 状态、watcher 存活状态、GPU 快照、B0 与 MobileMamba 最新 iter/eval/result 和下一步队列。
- JSON 必须可供后续脚本读取，不依赖人工解析 Markdown。

当前实现说明：

- 脚本路径：`/root/data-tmp/workspace/02_experiments/scripts/orchestrator_tick.py`。
- 已通过 `py_compile` 和一次真实运行；当前报告显示 Light main result pass，Gate 1/2/3 pending，Gate 4A B0 与 Gate 4B MobileMamba observation only。

### `generate_delta_summary.py`

功能：从 `metrics_all.csv` 和 `profiles.csv` 生成论文当前可引用的 delta 摘要，避免摘要、4.4、
4.5 和结论中的差值靠手工计算。

验收：

- 默认输出 `04_paper/drafts/current_delta_summary.md`。
- Gate 1 未完成时，Light-vs-ESCNet delta 必须自动标注为相对 historical reference。
- Gate 1 完成后，必须自动优先使用 `baseline_escnet_b5_clean_prob_e120` 的 clean probability baseline。
- Gate 2 完成后，必须自动补充 KD-vs-Light 和 KD-vs-active-baseline delta。
- 必须输出结构降幅和 Gate 1/2/3 当前状态。

当前实现说明：

- 脚本路径：`/root/data-tmp/workspace/04_paper/scripts/generate_delta_summary.py`。
- 只读 CSV，不启动训练、评测或 GPU profiling。

### `summarize_external_b0.py`

功能：只读汇总 dirty `/root/ESCNet` 外部 PVTv2-B0 online KD 分支的进度、COD10K
中间结果、checkpoint 状态、GPU 快照和进程快照。

验收：

- 不启动、不停止任何进程。
- 报告必须显式标注 `external_dirty_tree_observation_only`。
- 若没有 checkpoint，必须写明 `Checkpoint status: absent`。
- 中间 COD10K eval 不得被提升为 final paper evidence。

当前实现说明：

- 脚本路径：`/root/data-tmp/workspace/02_experiments/scripts/summarize_external_b0.py`。
- 默认报告：`/root/data-tmp/workspace/02_experiments/runs/b0_external_status_latest.md`。

### `watch_external_b0_progress.sh`

功能：只读轮询 dirty `/root/ESCNet` 外部 PVTv2-B0 online KD 分支，定期调用
`summarize_external_b0.py` 并只在 iter、latest eval status、COD10K result 行或 checkpoint
签名变化时记录事件。

验收：

### `sync_b0_observation_state.py`

功能：当外部 B0 分支出现新 checkpoint 或 COD10K 中间指标行时，一键刷新只读观察状态、趋势图、
orchestrator tick、B0 状态一致性审计和 release audit。

验收：

- 不启动、不停止、不 signal 任何训练或评测进程。
- 默认依次调用 `summarize_external_b0.py`、`draw_b0_trend_figure.py`、
  `orchestrator_tick.py --no_refresh_b0`、`audit_b0_status_consistency.py` 和
  `run_release_audits.sh`。
- 支持 `--skip_release_audit` 只做 B0 状态刷新和 B0 专项审计。
- 支持 `--dry_run` 预览命令。
- 输出必须列出 live status、tick、趋势说明和审计报告路径。

当前实现说明：

- 脚本路径：`/root/data-tmp/workspace/02_experiments/scripts/sync_b0_observation_state.py`。
- 只维护 observation artifacts；不会把 B0 升级为 final evidence。

- 不启动、不停止、不 signal 任何训练进程。
- 默认日志写入 `/root/data-tmp/workspace/02_experiments/runs/watch_external_b0_progress.log`。
- 支持 `--once` 做单次安全检查，支持 `--poll_seconds` 和 `--max_wait_seconds`。
- 日志签名必须包含 `eval_epoch` 和 `eval_status`，用于发现 epoch80/90 等 eval 从
  `in_progress_or_pending_metrics` 变为 `metrics_appended`。
- 日志必须只作为外部分支观察记录，不能把 B0 提升为 final paper evidence。

当前实现说明：

- 脚本路径：`/root/data-tmp/workspace/02_experiments/scripts/watch_external_b0_progress.sh`。
- 适合在长训练期间常驻，轮询负载很低；如已有 PID 存活，不要重复启动。

### `snapshot_external_b0_dirty_tree.sh`

功能：为 dirty `/root/ESCNet` 外部 PVTv2-B0 online KD 分支创建轻量可审计源码/配置快照，
用于结束后回收证据边界，而不是把该分支提升为论文 final evidence。

验收：

- 默认输出到 `/root/data-tmp/workspace/02_experiments/code/external_b0_dirty_snapshot_<UTC>`。
- 复制源码和配置，但排除 `.git`、`__pycache__`、`.pyc`、`checkpoints`、`logs`、`preds`、`results` 等运行产物。
- 必须保存 `git_head.txt`、`git_status_short.txt`、`git_diff.patch`、`source_file_manifest.txt`。
- 若存在 B0 result/status/log，必须只复制 result 表、status md 和 log tail，不复制完整预测或 checkpoint。
- README 必须标注 `external_dirty_tree_observation_only`，并说明不能直接进论文主表。

当前实现说明：

- 脚本路径：`/root/data-tmp/workspace/02_experiments/scripts/snapshot_external_b0_dirty_tree.sh`。
- 已生成最新观察快照：`/root/data-tmp/workspace/02_experiments/code/external_b0_dirty_snapshot_20260613T1859Z_epoch50_observation`。

### `start_b0_candidate_eval.sh`

功能：在外部 B0 dirty-tree 分支产生候选 checkpoint 后，把 Gate 4 所需的快照、profile/load gate、三数据集 probability eval、integrity 和 release audit 串成一个验收入口。

验收：

- 默认使用 `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0` 中最新 `epoch_*.pth`，也可用 `--ckpt` 指定。
- 默认先调用 `snapshot_external_b0_dirty_tree.sh` 创建 `external_b0_dirty_snapshot_*_candidate_eval`，再使用 snapshot/source 进行 profile/eval，不直接依赖可变的 `/root/ESCNet`。
- GPU 有 `torchrun|train.py` 活跃时默认拒绝启动，除非显式传入 `--force_busy_gpu`。
- profile 后必须检查 checkpoint strict load：`status=loaded`、missing=0、unexpected=0、forward ok。
- probability eval 行必须写 `status=external_dirty_tree_observation_candidate`，不能写 `final_main_*`。
- 支持 `--dry_run` 预览全部命令，不创建 snapshot、不启动 GPU work。

当前实现说明：

- 脚本路径：`/root/data-tmp/workspace/02_experiments/scripts/start_b0_candidate_eval.sh`。
- 已通过 `bash -n` 和 epoch70 `--dry_run`；真实运行需等待 Gate 1/KD 主队列空闲或用户明确允许抢占。

### MobileMamba-T2 observation scripts

功能：为 dirty `/root/ESCNet` 外部 MobileMamba-T2 online KD 分支提供只读监控、
轻量快照和候选 checkpoint 验收入口。该分支是替代轻量主干观察路线，不是
clean baseline、Light 主结果或 KD 主线。

包含脚本：

- `summarize_external_mobilemamba.py`：只读汇总 MobileMamba-T2 训练进度、结果、checkpoint
  状态、GPU 快照和进程快照。
- `watch_external_mobilemamba_progress.sh`：常驻只读 watcher，只记录 iter/result/checkpoint
  签名变化，不启动、不停止、不 signal 训练。
- `snapshot_external_mobilemamba_dirty_tree.sh`：创建
  `external_mobilemamba_dirty_snapshot_*` 轻量源码/config/runtime 快照，排除预测、checkpoint
  和大运行产物。
- `start_mobilemamba_candidate_eval.sh`：在候选 checkpoint 出现后执行 snapshot、
  load/profile gate、CAMO/COD10K/NC4K probability eval、integrity 和 release audit。

验收：

- 所有监控脚本必须显式标注 `external_dirty_tree_observation_only`。
- 候选 eval 的 metrics status 固定为 `external_dirty_tree_observation_candidate`，
  repo boundary 固定为 `external_mobilemamba_dirty_snapshot_candidate`。
- GPU 有 `torchrun|train.py` 活跃时，候选 eval 默认拒绝启动，除非显式传入
  `--force_busy_gpu`。
- MobileMamba-T2 不得进入主表、摘要或结论；Gate 4B 通过后也只能作为附录观察或失败分析。

当前实现说明：

- 只读状态入口：`/root/data-tmp/workspace/02_experiments/runs/mobilemamba_t2_external_status_latest.md`。
- 只读 watcher 日志：`/root/data-tmp/workspace/02_experiments/runs/watch_external_mobilemamba_progress.log`。
- 候选验收入口：`/root/data-tmp/workspace/02_experiments/scripts/start_mobilemamba_candidate_eval.sh`。
- 当前占用四卡的正是该外部分支；不要重复启动 watcher，不要抢占，除非用户明确要求。

### `watch_baseline_then_start_kd.sh`

功能：等待 clean baseline 三数据集概率复评完成并通过 release gate，再在 GPU 空闲时调用
`start_kd_full_train.sh` 接力启动 KD B2-C64 恢复训练。

验收：

- baseline 未完成时只能等待，不能启动 KD。
- 启动 KD 前必须确认 `metrics_all.csv` 中 baseline 三数据集都是
  `clean_prob_re_eval_complete` 且协议为 `prob_map`。
- 启动 KD 前必须把 baseline run 加入 `run_release_audits.sh --add-integrity`。
- GPU 或训练进程忙时必须等待。
- 支持 `--dry_run` 和 `--max_wait_seconds` 做安全短测。

当前实现说明：

- 脚本路径：`/root/data-tmp/workspace/02_experiments/scripts/watch_baseline_then_start_kd.sh`。
- 默认日志：`/root/data-tmp/workspace/02_experiments/runs/watch_baseline_then_start_kd.log`。

## P2

### `aggregate_results.py`

功能：合并 metrics、profile、metadata，生成论文表格和消融表。

验收：

- 可输出按数据集分组和按模型分组的 Markdown 表。

当前实现说明：

- 读取 `metrics_all.csv` 与 `profiles.csv`。
- 输出紧凑主表和 metric coverage。
- 默认包含 historical baseline reference、Light trained、KD trained 的 exp id，占位缺失结果为 `TBD`。
- 输出 `Metric Status` 和 `Speed Status`；latency/FPS 在空闲同条件复测前不得作为最终速度结论。

### `export_or_quantize.py`

功能：对最佳 student 尝试 ONNX/PTQ/dynamic quantization。

验收：

- 若失败，记录失败阶段和原因。
- 若成功，报告模型大小和 latency 变化。
