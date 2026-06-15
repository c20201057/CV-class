# New Conversation Handoff Prompt

请把下面整段作为新对话的第一条任务提示词使用。

````text
你是接棒的 Codex 主控 agent。继续推进“面向伪装目标分割的轻量化模型研究”实验与论文项目。

原始目标：
- 基于 `CV开题报告.pdf` 和 `/root/ESCNet` 实验基底，在 `/root/data-tmp/workspace` 中继续搭建 workflow、派发/验收 subagent、整合全局信息做路线判断，并写出课题论文。
- 课题方向是“面向伪装目标分割的轻量化模型研究”。
- 工作准则必须保持：不偷懒，不因为怕风险而保守。高风险路线可以推进，但必须隔离写入范围、保留证据、经主控验收后才能影响论文主张。

启动后第一步必须执行：

```bash
python /root/data-tmp/workspace/02_experiments/scripts/orchestrator_tick.py
sed -n '1,180p' /root/data-tmp/workspace/00_project/orchestrator_tick_latest.md
sed -n '1,220p' /root/data-tmp/workspace/00_project/new_conversation_handoff.md
```

不要凭聊天记忆直接操作 GPU；以当前 tick、进程和文件状态为准。

当前已知状态锚点：
- 工作区：`/root/data-tmp/workspace`
- 实验基底：`/root/ESCNet`，但它是 dirty 工作树，不能直接当 clean baseline。
- clean baseline snapshot：`/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean`
- teacher/baseline checkpoint：`/root/data-tmp/epoch_120.pth`
- 禁用 teacher：`/root/ESCNet/checkpoints/escnet/epoch_120.pth` 不是主 teacher。
- 最新总览：`/root/data-tmp/workspace/00_project/orchestrator_tick_latest.md`
- GPU 队列：`/root/data-tmp/workspace/02_experiments/scripts/GPU_QUEUE.md`
- 目标完成度矩阵：`/root/data-tmp/workspace/00_project/goal_completion_matrix.md`
- 任务板：`/root/data-tmp/workspace/03_agent_tasks/task_board.md`
- agent 验收账本：`/root/data-tmp/workspace/03_agent_tasks/acceptance/agent_acceptance_ledger.md`
- 论文交付清单：`/root/data-tmp/workspace/04_paper/drafts/paper_delivery_manifest.md`
- 当前推荐外发稿：`/root/data-tmp/workspace/04_paper/drafts/paper_interim_submission.md`
- 完整 release audit：`bash /root/data-tmp/workspace/02_experiments/scripts/run_release_audits.sh`

当前主结果：
- Light-ESCNet B2-C64 no-KD 是当前唯一 accepted main student result。
- run：`/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42`
- eval：`/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42_prob_eval_v2`
- metrics：CAMO S=.862/wF=.818/meanF=.843/meanE=.918/MAE=.051；COD10K S=.866/wF=.782/meanF=.808/meanE=.928/MAE=.024；NC4K S=.886/wF=.840/meanF=.862/meanE=.933/MAE=.033。
- profile：29.807714M params，36.391 GMACs，113.743 MB model，237.439 MB peak memory。

当前 pending gates：
- Gate 1 clean ESCNet-B5 probability baseline：已完成；CAMO/COD10K/NC4K 三行均为 `clean_prob_re_eval_complete`，不要重复启动 baseline wrapper。
- Gate 2 KD B2-C64：四卡 DDP/NCCL 初始化曾失败、双卡未产出 checkpoint；单卡 recovery 曾从 epoch5 跑到 epoch8 附近并保存 epoch6/epoch7，但用户判断单卡过慢，已要求停止单卡并优先恢复四卡。当前没有 accepted KD final checkpoint，不能声称 KD 提升。
- Gate 3 speed：没有 idle-GPU 同条件 FPS/latency，不能写最终速度。
- Gate 4A B0：dirty observation only，epoch120 COD10K S=.8004/wF=.6862/meanF=.7203/meanE=.8878/MAE=.0350；用户已明确说 B0 不在计划范围，B0 训练和 B0 read-only watcher 已停止，不要重启；不能进主表、摘要或结论。
- Gate 4B MobileMamba-T2：dirty observation only，当前未观察到运行；最新/最佳落表 epoch50 COD10K S=.7487/wF=.6019/meanF=.6482/meanE=.8477/MAE=.0465；不能进主表、摘要或结论。

当前 GPU 策略：
- 当前主线不是单卡长训，而是优先修复/恢复 Gate 2 KD 四卡训练。若 B0 再次占卡或 B0 watcher 复活，以用户当前指令为准：B0 不在计划范围，应停止；停止时只动 B0 相关进程组，不要误伤主线。其他外部分支除非用户明确要求，不抢占。
- Gate 1 baseline/resume watcher 不需要运行。
- 不要重启 `watch_baseline_then_start_kd.sh`。它的接力职责已经完成，当前需要主控人工排查四卡；默认 `start_kd_full_train.sh` 已改回四卡配置。单卡配置只能显式 `--config ...1gpu.yaml` 且需用户/主控确认。
- 每次 metrics/profile/manuscript/queue/prompt/watcher 有变化，都要跑相应审计；定稿或交接前跑完整 release audit。

当前 KD 锚点：
- 四卡优先 config：`/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config_resume_epoch10_fast_shm_4gpu.yaml`
- 四卡失败证据 log：`/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/logs/train_resume_epoch5_b2w0_4gpu_20260614T062550Z.log`
- 单卡已停止证据 log：`/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/logs/train_resume_epoch5_b2_workers0_1gpu_20260614T063851Z.log`
- 单卡回退 checkpoint 证据：`/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_recover_b2w0_1gpu/epoch_7.pth`
- 下一步：确认 GPU 空闲和无 B0/单卡残留后，优先诊断四卡 DDP/NCCL 初始化失败并恢复四卡 KD；不要默认启动单卡长训。

交接文档：
- 详细交接文件在 `/root/data-tmp/workspace/00_project/new_conversation_handoff.md`。
- 先读它，再行动。
````
