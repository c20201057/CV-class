# New Conversation Handoff

更新时间：2026-06-15T04:48:00Z / 2026-06-15 12:48:00 CST

用途：给新开的 Codex 对话接棒使用。本文档不是最终论文，也不是静态真相；新对话必须先刷新 `orchestrator_tick.py`，再以当前文件系统、进程和审计结果为准继续推进。

工作准则：不偷懒，不因为怕风险而保守。高风险实验可以继续做，但必须隔离写入范围、保留命令/配置/checkpoint/日志/指标证据，并经主控验收后才能影响论文主张。

## 0. 新对话第一步

```bash
python /root/data-tmp/workspace/02_experiments/scripts/orchestrator_tick.py
sed -n '1,180p' /root/data-tmp/workspace/00_project/orchestrator_tick_latest.md
sed -n '1,220p' /root/data-tmp/workspace/00_project/new_conversation_handoff.md
sed -n '1,220p' /root/data-tmp/workspace/02_experiments/scripts/GPU_QUEUE.md
```

不要凭本文档直接操作 GPU。当前 Gate 1/2/3 已完成；用户随后明确授权进入结构消融扩展，上一阶段 `no_edge_guidance` 已完成并评估为负向消融候选；当前 GPU0-3 已挂起 Light-B2-C64 `no_edge_supervision` 四卡训练。新对话必须先刷新 tick，再读 `GPU_QUEUE.md` 中最新 active ablation 锚点。

当前 active ablation：

```text
task Light-B2-C64 no-edge-supervision structural ablation
status running_not_accepted
torchrun_pid 1256510
sync_watcher_pid 1259831
code /root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64_no_edge_supervision
config /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_no_edge_supervision_e120_s42/config_no_edge_supervision_b6_w8_4gpu.yaml
active_log /dev/shm/escnet_ablation_no_edge_supervision/logs/train_no_edge_supervision_b6_w8_4gpu_20260615T044543Z.log
local_run /dev/shm/escnet_ablation_no_edge_supervision/runs/light_b2_c64_no_edge_supervision_e120_s42_b6_w8_4gpu
persistent_sync /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_no_edge_supervision_e120_s42/light_b2_c64_no_edge_supervision_e120_s42_b6_w8_4gpu
```

该训练是消融候选，不是已验收结果。配置含义是保留 decoder edge guidance，但设置 `edge_loss_weight=0.0` 关闭 edge GT 直接监督。完整 120 epoch checkpoint、CAMO/COD10K/NC4K probability eval、profile、integrity/audit 完成前，不得写入主表、摘要或结论。

上一阶段 `no_edge_guidance` 已完成，不要重复启动。其边界是 `disable_decoder_edge_guidance=true`、edge head/edge loss 保留、decoder 不使用 edge 引导；结果为 CAMO S=.846/wF=.786/meanF=.818/meanE=.899/MAE=.058，COD10K S=.847/wF=.749/meanF=.779/meanE=.917/MAE=.028，NC4K S=.873/wF=.815/meanF=.842/meanE=.921/MAE=.038，低于 accepted Light-B2-C64，只能作为移除 decoder edge guidance 会退化的结构消融候选证据。

## 1. 原始目标

项目基于 `CV开题报告.pdf` 和实验基底 `/root/ESCNet`。后续工作空间固定为 `/root/data-tmp/workspace`，大临时文件放 `/root/data-tmp/tmp`。

主控职责：

- 制定和维护工作计划。
- 搭建实验、审计、写作 workflow。
- 为 subagent 写目标模式 prompt，并要求所有 subagent 遵守“不偷懒、不因为怕风险而保守”。
- 整合全局信息做路线判断。
- 验收 subagent 和外部分支工作。
- 基于开题报告路线、论文调研、网络调研和实验结果，写出“面向伪装目标分割的轻量化模型研究”论文。

## 2. 权限与空间

当前环境最后一次确认：

- 文件系统：全权限，`/root` 可读写。
- 网络：enabled。
- approval policy：`never`，不要请求 escalated sandbox。
- 新产物继续写 `/root/data-tmp/workspace` 或 `/root/data-tmp/tmp`。
- 不要把大文件、checkpoint、日志写回根分区或 `/root/ESCNet`。

## 3. 代码边界

`/root/ESCNet` 是实验基底，但当前是 dirty 工作树，包含外部 B0/MobileMamba/KD 等探索修改。它不能再口头等同于 clean baseline。

clean ESCNet-B5 baseline snapshot：

```text
/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean
```

clean snapshot 来源 HEAD：

```text
25c4387e4ea94c247d83a91a749e87b959483a4e
```

主 teacher / baseline checkpoint：

```text
/root/data-tmp/epoch_120.pth
sha256 61847f70a489bf610f9c24d161611833a99c9558b4d628ed01567a5b538ed0dc
```

不要使用：

```text
/root/ESCNet/checkpoints/escnet/epoch_120.pth
```

该文件是 2026-06-13 后续重训/legacy artifact，不是主 teacher。

## 4. 当前已验收主结果

当前 accepted main student result 是 Light-ESCNet B2-C64 no-KD。KD B2-C64 也已完成，但只作为中性/负向蒸馏结果分析，不作为提升主张。

Light 核心路径：

```text
/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42
/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42_prob_eval_v2
/root/data-tmp/workspace/02_experiments/tables/metrics_all.csv
/root/data-tmp/workspace/02_experiments/tables/profiles.csv
```

Light checkpoint sha256：

```text
a6886fded30bef1e59f1ddc3d05078d6b8023aa0387867ded225b4d0775b3c7d
```

Light 三数据集 probability eval：

| Dataset | S | wF | meanF | meanE | MAE |
| --- | ---: | ---: | ---: | ---: | ---: |
| CAMO | .862 | .818 | .843 | .918 | .051 |
| COD10K | .866 | .782 | .808 | .928 | .024 |
| NC4K | .886 | .840 | .862 | .933 | .033 |

结构 profile：

| Model | Params | GMACs | Model Size | Peak Memory |
| --- | ---: | ---: | ---: | ---: |
| ESCNet-B5 C128 reference | 99.903M | 129.022 | 381.17 MB | 829.77 MB |
| Light-B2-C64 | 29.808M | 36.391 | 113.743 MB | 237.439 MB |

当前写作允许：

- Light-B2-C64 完整训练和三数据集 probability eval 已完成。
- clean ESCNet-B5 probability baseline 已完成。
- 结构参数、GMACs、模型大小、峰值显存显著下降。
- Controlled speed 可按 idle V100 profile 条件报告。
- KD 可以写为完成实验与负结果/成本分析。

当前写作禁止：

- 不要写 KD 已证明提升或有效缩小差距。
- 不要把 controlled speed 写成 edge-device deployment、real-time deployment 或最终部署速度。
- 不要把 dirty B0/MobileMamba 写入主表、摘要或结论。
- 不要把 historical ESCNet-B5 reference 当作当前同协议 baseline。
- 不要写 SOTA、首次提出或首次 KD-COD。

## 5. Gate 状态

以 `00_project/orchestrator_tick_latest.md` 为实时准。本文档生成时的状态如下。

### Gate 1 Clean Baseline

状态：complete。

路径：

```text
/root/data-tmp/workspace/02_experiments/runs/baseline_escnet_b5_clean_prob_e120
```

结果：

| Dataset | S | wF | meanF | meanE | MAE |
| --- | ---: | ---: | ---: | ---: | ---: |
| CAMO | .881 | .842 | .864 | .933 | .043 |
| COD10K | .877 | .802 | .824 | .938 | .021 |
| NC4K | .897 | .857 | .878 | .942 | .029 |

`metrics_all.csv` 三行均为 `status=clean_prob_re_eval_complete`、`protocol=prob_map`。baseline/resume watcher 不需要运行，不要重复启动 baseline wrapper。

### Gate 2 KD

状态：complete。

代码与历史控制路径：

```text
/root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64
/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42
```

最终训练配置：

```text
/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config_continue_epoch20_b6_w8_4gpu.yaml
```

最终 run、checkpoint 与 eval：

```text
/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu
/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu/epoch_120.pth
/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval
```

checkpoint sha256：

```text
36f0680943279d77c038ee16f4e5a341dd4b9f61600d2a2d0bd579c13693c2ae
```

KD 三数据集 probability eval：

| Dataset | S | wF | meanF | meanE | MAE |
| --- | ---: | ---: | ---: | ---: | ---: |
| CAMO | .863 | .818 | .844 | .920 | .050 |
| COD10K | .864 | .782 | .809 | .929 | .024 |
| NC4K | .885 | .838 | .860 | .932 | .033 |

验收判断：Gate 2 通过，但结果不支持 KD 提升。相对 no-KD，三数据集平均约 S -0.001、wF -0.001、meanF 约 0、meanE +0.001、MAE 约 0。论文写作只能使用“在线输出级 MSE KD 在当前设置下未带来稳定正向收益”。

历史恢复 marker 仍保留用于审计，不代表当前要重启训练：

```text
epoch_5.pth
/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_recover_b2w0_1gpu/epoch_7.pth
/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/logs/train_resume_epoch5_b2_workers0_1gpu_20260614T063851Z.log
/dev/shm/escnet_fast_kd/logs/train_continue_epoch20_b6_w8_4gpu_20260614T100610Z.log
```

不要重启 `watch_baseline_then_start_kd.sh`、`start_kd_full_train.sh`、`start_kd_fast_shm_train.sh` 或单卡 KD。

### Gate 3 Speed

状态：complete。

受控条件：idle V100、input size 416、batch=1、warmup=50、repeat=100、same profile command。

| Model | Latency | FPS | Profile |
| --- | ---: | ---: | --- |
| ESCNet-B5 C128 | 73.0148 ms | 13.6958 | `/root/data-tmp/workspace/02_experiments/runs/profile_escnet_b5_416_idle/profile.json` |
| Light-ESCNet B2-C64 | 34.3106 ms | 29.1455 | `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/profile_epoch120_idle.json` |
| KD Light-ESCNet B2-C64 | 34.8350 ms | 28.7067 | `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu/profile_epoch120_idle.json` |

论文可以写 controlled latency/FPS；不能写最终部署速度、边缘端部署或真实实时部署。

### Gate 4A B0

状态：observation only。

B0 外部 dirty 分支训练/eval 已完成，最新完整 COD10K 中间行为 epoch120：

```text
S=.8004, wF=.6862, meanF=.7203, meanE=.8878, MAE=.0350
```

最好 S 行仍是 epoch100：

```text
S=.8014, wF=.6882, meanF=.7221, meanE=.8899, MAE=.0346
```

它仍显著低于 accepted Light-B2-C64 COD10K，且未完成独立候选 snapshot/load/profile/三数据集 eval/integrity。不能进主表、摘要或结论。

用户已明确指出 B0 不在当前计划范围，并要求停掉 B0 后执行主线任务。不要重启 B0 训练、`all.sh` 或 B0 watcher。若发现 B0 相关训练或 watcher 复活，先核对进程命令，只停止 B0 相关进程组，不要误伤其他外部进程。

### Gate 4B MobileMamba-T2

状态：observation only。

最新且最高 S 的 COD10K 观察行：

```text
epoch50 S=.7487, wF=.6019, meanF=.6482, meanE=.8477, MAE=.0465
```

无 accepted checkpoint。不能进主表、摘要或结论。

## 6. 当前活进程与 watcher

生成本文档时：

- active train-like processes: 0。
- active GPU-like processes: 0。
- `/root/ESCNet/all.sh` 已按用户明确要求停止。
- Gate 1 baseline/resume watcher 不需要运行。
- Gate 2 KD watcher 已完成接力后退出；当前不要重启。
- B0 read-only watcher 已按用户要求停止；不要重启。
- MobileMamba read-only watcher 可保持只读观察，PID 以最新 tick 为准。

恢复时用这些命令确认：

```bash
nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits
ps -eo pid,ppid,stat,etime,cmd | grep -E 'MobileMamba|mobilemamba|baseline_escnet_b5_clean_prob|watch_external|run_prob_eval_suite|torchrun|train.py|all.sh|watch_baseline_then_start_kd|resume_stopped_prob_eval' | grep -v grep || true
```

## 7. MobileMamba 观察链路

只读状态脚本：

```bash
python /root/data-tmp/workspace/02_experiments/scripts/summarize_external_mobilemamba.py
```

只读 watcher：

```bash
/root/data-tmp/workspace/02_experiments/scripts/watch_external_mobilemamba_progress.sh --poll_seconds 300
```

该 watcher 只刷新状态，不启动、不停止、不 signal 训练。候选 checkpoint 验收入口默认 GPU 忙时拒绝启动；即使未来候选评估完成，status 也必须是 `external_dirty_tree_observation_candidate`，不能自动升级为主结果。

## 8. 论文材料

当前推荐外发/阅读材料：

```text
/root/data-tmp/workspace/04_paper/drafts/paper_interim_submission.md
/root/data-tmp/workspace/04_paper/drafts/teacher_share_pack.md
/root/data-tmp/workspace/04_paper/drafts/presentation_outline.md
```

内部主控材料：

```text
/root/data-tmp/workspace/04_paper/drafts/paper_draft.md
/root/data-tmp/workspace/04_paper/drafts/evidence_index.md
/root/data-tmp/workspace/04_paper/drafts/writing_status.md
/root/data-tmp/workspace/04_paper/drafts/paper_claim_evidence_matrix.md
/root/data-tmp/workspace/04_paper/drafts/paper_delivery_manifest.md
/root/data-tmp/workspace/04_paper/drafts/paper_submission_packet.md
/root/data-tmp/workspace/04_paper/drafts/reproducibility_manifest.md
```

当前可以讲的论文主线：

- 伪装目标分割在低对比、弱边界和复杂纹理下计算代价高。
- 以 ESCNet 为基底构建 Light-ESCNet B2-C64：PVTv2-B2 轻量主干、64 通道解码投影、保留边缘-语义协同。
- Light-B2-C64 完成三数据集 probability eval，并显著降低参数、GMACs、模型大小和峰值显存。
- 相对 clean ESCNet-B5 probability baseline，精度小幅下降但结构复杂度约降 70%。
- Controlled speed profile 已完成：ESCNet-B5 73.01 ms / 13.70 FPS，Light 34.31 ms / 29.15 FPS，KD Light 34.84 ms / 28.71 FPS。
- KD 完成三数据集 eval，但当前在线 output-level MSE 蒸馏没有稳定正向收益。

当前不能讲成结论：

- “KD 提升了性能”。
- “部署速度/边缘端实时部署已经验证”。
- “B0/MobileMamba 是有效主结果”。
- “历史 ESCNet-B5 reference 是当前同协议 baseline”。
- “SOTA”或“首次提出”。

## 9. 审计入口

每次重要改动后至少运行相关定向审计。交接、定稿、论文主张变化后跑完整 release audit：

```bash
bash /root/data-tmp/workspace/02_experiments/scripts/run_release_audits.sh \
  --add-integrity /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval \
  kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval \
  CAMO,COD10K,NC4K
```

重要定向审计：

```bash
python /root/data-tmp/workspace/03_agent_tasks/prompts/audit_prompt_principles.py
python /root/data-tmp/workspace/03_agent_tasks/audit_task_board_consistency.py
python /root/data-tmp/workspace/03_agent_tasks/acceptance/audit_agent_acceptance_ledger.py
python /root/data-tmp/workspace/02_experiments/scripts/audit_gpu_handoff_consistency.py
python /root/data-tmp/workspace/02_experiments/scripts/audit_gpu_runtime_state.py
python /root/data-tmp/workspace/02_experiments/scripts/audit_route_decision_consistency.py
python /root/data-tmp/workspace/02_experiments/scripts/audit_goal_completion_matrix.py
python /root/data-tmp/workspace/04_paper/scripts/audit_claim_text.py
python /root/data-tmp/workspace/04_paper/scripts/audit_submission_protocol.py
python /root/data-tmp/workspace/04_paper/scripts/audit_paper_delivery_manifest.py
```

## 10. Subagent 与验收

公共 prompt：

```text
/root/data-tmp/workspace/03_agent_tasks/prompts/MASTER_TARGET_PROMPT.md
/root/data-tmp/workspace/03_agent_tasks/prompts/DISPATCH_PACKETS.md
```

新对话用提示词：

```text
/root/data-tmp/workspace/03_agent_tasks/prompts/NEW_CONVERSATION_HANDOFF_PROMPT.md
```

任务板：

```text
/root/data-tmp/workspace/03_agent_tasks/task_board.md
```

验收账本：

```text
/root/data-tmp/workspace/03_agent_tasks/acceptance/agent_acceptance_ledger.md
```

规则：

- 新增 subagent 报告必须进入 `03_agent_tasks/reports/` 或 `05_reviews/`。
- 主控验收后更新 ledger。
- 被拒收或 observation-only 的结果也要写入 ledger。
- prompt/pending 任务必须包含“不偷懒、不因为怕风险而保守”；修改后跑 prompt principles audit。

## 11. 推荐下一步

当前主线是进入论文交付闭环，不是训练监工。下一棒进入后先刷新 tick，再执行：

```bash
python /root/data-tmp/workspace/02_experiments/scripts/aggregate_results.py \
  --out_md /root/data-tmp/workspace/04_paper/tables/aggregated_results.md
python /root/data-tmp/workspace/04_paper/scripts/generate_delta_summary.py \
  --metrics_csv /root/data-tmp/workspace/02_experiments/tables/metrics_all.csv
python /root/data-tmp/workspace/04_paper/scripts/audit_gate_patch_readiness.py \
  --metrics_csv /root/data-tmp/workspace/02_experiments/tables/metrics_all.csv
python /root/data-tmp/workspace/02_experiments/scripts/orchestrator_tick.py
bash /root/data-tmp/workspace/02_experiments/scripts/run_release_audits.sh \
  --add-integrity /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval \
  kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval \
  CAMO,COD10K,NC4K
```

推荐操作顺序：

1. 不重启 Gate 1 baseline/resume watcher；Gate 1 clean baseline 已完成。
2. 不重启 `watch_baseline_then_start_kd.sh`；Gate 2 KD 已完成。
3. 不重启 B0 训练或 B0 read-only watcher；若 B0 相关进程复活，按用户指令只停 B0 相关进程组。
4. 不启动单卡 KD 长训或新的 KD 训练；当前 KD 结论已经由 final checkpoint/eval 决定。
5. 用 Gate 2/3 结果更新论文和交付材料后，必须跑完整 release audit。
6. 如果 release audit 通过，可以进入老师阅读包/最终打磨阶段；如果失败，按审计报告修文档或脚本。

## 12. 不要做

- 不要自动重启单卡 KD 长训。
- 不要重启 B0 训练、`all.sh` 或 `watch_external_b0_progress.sh`。
- 不要重复启动已完成的 Gate 1 baseline wrapper。
- 不要跳过 Gate 1 直接宣称 clean baseline delta；Gate 1 已完成，使用 `clean_prob_re_eval_complete` 行。
- 不要宣称 KD 有效或提升。
- 不要把 B0/MobileMamba dirty observation 放进主表、摘要或结论。
- 不要把 `/root/ESCNet` 当前 dirty tree 当作 clean baseline。
- 不要把大文件写入根分区或 `/root/ESCNet`。
- 不要为了显得完成而标记原始总目标 complete；除非论文、审计和用户接受的交付条件全部闭合。

## 13. 历史 Marker

以下 marker 用于审计脚本和追溯，不表示当前仍是待训练状态：

- `P0_gate1_kd_handoff_card.md`
- `epoch_5.pth`
- `resume_stopped_prob_eval_when_gpu_idle.sh`
- `watch_baseline_then_start_kd.sh`
- `clean_prob_re_eval_complete`
- `external_dirty_tree_observation_only`
