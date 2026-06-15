# Current Run Snapshot

更新时间：2026-06-14T15:31:36Z / 2026-06-14 23:31:36 CST

## 最新权威状态

- 当前没有活跃 train-like 或 GPU-like 进程；GPU0-3 均空闲。
- Gate 1 clean ESCNet-B5 probability baseline 已完成，CAMO/COD10K/NC4K 三行均为 `clean_prob_re_eval_complete`。
- Gate 2 KD B2-C64 已完成 120 epoch、三数据集 probability eval 和完整性证据；结果相对 no-KD 基本持平或略低，只能作为负结果/成本分析，不能写作 KD 提升。
- Gate 3 controlled speed 已完成；latency/FPS 只能按 idle V100、416 input、batch=1、warmup=50、repeat=100 条件报告，不能推广为边缘端部署或真实实时系统。
- B0 与 MobileMamba-T2 均为 `external_dirty_tree_observation_only`，不能进入主表、摘要或结论。
- 当前下一阶段不是继续训练，而是把 Gate 2/3 结果回填到论文、证据矩阵、交付清单和 handoff 文档，然后重新生成汇总并跑完整 release audit。

本文件是恢复目标模式时的短状态锚点；权威细节仍以
`orchestrator_tick_latest.md`、`GPU_QUEUE.md`、`goal_completion_matrix.md`、
`paper_submission_readiness.md` 和 `new_conversation_handoff.md` 为准。

## 当前运行

- Active train-like processes: 0。
- Active GPU-like processes: 0。
- KD recovery running: false；final checkpoint 已存在。
- B0 running: false；`watch_external_b0_progress.sh` 不应重启。
- MobileMamba-T2 running: false；只读 watcher `watch_external_mobilemamba_progress.sh` 仍可保留为观察链路，PID 以最新 tick 为准。
- baseline/resume watcher 不需要运行：`resume_stopped_prob_eval_when_gpu_idle.sh` 只保留为历史 marker。
- KD handoff watcher 不需要运行：`watch_baseline_then_start_kd.sh` 已完成接力，不要重复启动。

## 已验收核心证据

### Clean ESCNet-B5 Baseline

路径：`/root/data-tmp/workspace/02_experiments/runs/baseline_escnet_b5_clean_prob_e120`

| Dataset | S | wF | meanF | meanE | MAE |
| --- | ---: | ---: | ---: | ---: | ---: |
| CAMO | .881 | .842 | .864 | .933 | .043 |
| COD10K | .877 | .802 | .824 | .938 | .021 |
| NC4K | .897 | .857 | .878 | .942 | .029 |

### Light-ESCNet B2-C64 No-KD

路径：

- run: `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42`
- eval: `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42_prob_eval_v2`

| Dataset | S | wF | meanF | meanE | MAE |
| --- | ---: | ---: | ---: | ---: | ---: |
| CAMO | .862 | .818 | .843 | .918 | .051 |
| COD10K | .866 | .782 | .808 | .928 | .024 |
| NC4K | .886 | .840 | .862 | .933 | .033 |

结构 profile：29.807714M params，36.391 GMACs，113.743 MB model，237.439 MB peak memory。

### KD B2-C64

路径：

- final run: `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu`
- final checkpoint: `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu/epoch_120.pth`
- eval: `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval`
- checkpoint sha256: `36f0680943279d77c038ee16f4e5a341dd4b9f61600d2a2d0bd579c13693c2ae`

| Dataset | S | wF | meanF | meanE | MAE |
| --- | ---: | ---: | ---: | ---: | ---: |
| CAMO | .863 | .818 | .844 | .920 | .050 |
| COD10K | .864 | .782 | .809 | .929 | .024 |
| NC4K | .885 | .838 | .860 | .932 | .033 |

写作边界：KD 相对 no-KD 的三数据集平均差异约为 S -0.001、wF -0.001、meanF 约 0、meanE +0.001、MAE 约 0；不能写作已证明提升。

### Controlled Speed

| Model | Latency | FPS | Profile |
| --- | ---: | ---: | --- |
| ESCNet-B5 C128 | 73.0148 ms | 13.6958 | `/root/data-tmp/workspace/02_experiments/runs/profile_escnet_b5_416_idle/profile.json` |
| Light-ESCNet B2-C64 | 34.3106 ms | 29.1455 | `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/profile_epoch120_idle.json` |
| KD Light-ESCNet B2-C64 | 34.8350 ms | 28.7067 | `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu/profile_epoch120_idle.json` |

## Observation-Only Branches

- B0 dirty branch: epoch120 COD10K S=.8004、wF=.6862、meanF=.7203、meanE=.8878、MAE=.0350；best observed epoch100 S=.8014、wF=.6882、meanF=.7221、meanE=.8899、MAE=.0346。用户已说明 B0 不在当前计划范围，不要重启 B0 训练或 watcher。
- MobileMamba-T2 dirty branch: 最新且最高 S 的观察行是 epoch50 COD10K S=.7487、wF=.6019、meanF=.6482、meanE=.8477、MAE=.0465；无 accepted checkpoint。

## 文件与空间边界

- `/root/ESCNet` 是 dirty 工作树，不能作为 clean baseline。
- clean baseline snapshot：`/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean`。
- teacher checkpoint：`/root/data-tmp/epoch_120.pth`；不要使用 `/root/ESCNet/checkpoints/escnet/epoch_120.pth` 作为主 teacher。
- 新产物、大文件、日志和临时文件继续写 `/root/data-tmp/workspace` 或 `/root/data-tmp/tmp`。不要把 checkpoint 写回根分区或 `/root/ESCNet`。

## 历史恢复 Marker

这些 marker 用于审计和追溯，不代表当前需要运行：

- `epoch_5.pth`：KD 早期恢复锚点。
- `P0_gate1_kd_handoff_card.md`：早期 Gate1->KD handoff 任务卡。
- `resume_stopped_prob_eval_when_gpu_idle.sh`：Gate 1 历史恢复 watcher。
- `watch_baseline_then_start_kd.sh`：Gate 1 完成后启动 KD 的历史 watcher。
- `external_dirty_tree_observation_only`：B0/MobileMamba 的证据边界。

## 最新审计

- 进入本阶段前 release audit 已通过：`/root/data-tmp/workspace/04_paper/drafts/release_audit_latest.md`。
- 当前正在做 Gate 2/3 回填；回填完成后必须再次运行：

```bash
bash /root/data-tmp/workspace/02_experiments/scripts/run_release_audits.sh \
  --add-integrity /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval \
  kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval \
  CAMO,COD10K,NC4K
```

## 下一步

1. 完成论文正文、表格、证据矩阵、交付清单和 handoff 的 Gate 2/3 回填。
2. 重新生成 `aggregated_results.md`、`current_delta_summary.md`、`gate_patch_readiness_latest.md` 和 `orchestrator_tick_latest.md`。
3. 跑完整 release audit，并把结果写回交接说明。
4. 不重启 baseline wrapper、KD watcher、B0 watcher、单卡 KD 或任何训练。
