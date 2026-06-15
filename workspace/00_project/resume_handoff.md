# Resume Handoff

更新时间：2026-06-14T15:31:36Z / 2026-06-14 23:31:36 CST

## 最新恢复锚点

- 当前没有活跃 train-like 或 GPU-like 进程；GPU0-3 空闲。
- Gate 1 clean ESCNet-B5 probability baseline 已完成 CAMO/COD10K/NC4K，三行均为 `clean_prob_re_eval_complete`。
- Gate 2 KD B2-C64 已完成 final checkpoint、三数据集 probability eval 和 integrity 证据，但结果相对 no-KD 基本持平或略低，不能写 KD 提升。
- Gate 3 controlled speed 已完成，可以按 idle V100 same-command profile 条件报告 latency/FPS。
- B0 与 MobileMamba-T2 都是 `external_dirty_tree_observation_only`，不进入主表、摘要或结论。
- 当前阶段是 Gate 2/3 论文回填、汇总刷新和 release audit，不是继续训练。

本文件用于目标模式暂停/恢复时快速接上当前状态。所有新产物继续写入 `/root/data-tmp/workspace` 或 `/root/data-tmp/tmp`；不要把大文件写回根分区或 `/root/ESCNet`。

短状态锚点：`/root/data-tmp/workspace/00_project/current_run_snapshot.md`。

## 空间与路径边界

- `/root/data-tmp` 是数据盘和主要工作区，新 checkpoint、日志、临时文件、论文材料都应写到 `/root/data-tmp/workspace` 或 `/root/data-tmp/tmp`。
- `/root/ESCNet` 是 dirty 实验基底，不再作为 clean baseline 直接引用。
- clean baseline snapshot：`/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean`。
- 主 teacher：`/root/data-tmp/epoch_120.pth`。
- `/root/ESCNet/checkpoints/escnet/epoch_120.pth` 是 legacy artifact，不是主 teacher。

根分区诊断补充：此前 `df`/`du` 显示严重不一致；不要移动 `/root/miniconda3` 或系统目录。后续训练若再启动，必须继续把输出、cache 和临时数据放到 data-tmp 或 local tmpfs，并减少 checkpoint 保存频率。

## 当前训练状态

当前没有训练正在跑。

KD 历史路线概述：

- 早期 KD full train 在 epoch5/6 附近经历过 SIGKILL、DataLoader/IO 和 DDP/NCCL 初始化问题。
- 主控修复了 `train.py` 的 resume、DDP device mapping、resume map_location、初始化超时和 rank traceback。
- 为解决 NFS IO 等待，后续切到 fast-shm/local 数据与输出，并按用户要求减少保存频率。
- 最终训练配置为 `config_continue_epoch20_b6_w8_4gpu.yaml`，从 epoch20 后继续四卡 batch6 workers8 路线完成到 epoch120。

KD final evidence：

```text
config /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config_continue_epoch20_b6_w8_4gpu.yaml
run    /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu
ckpt   /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu/epoch_120.pth
eval   /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval
sha256 36f0680943279d77c038ee16f4e5a341dd4b9f61600d2a2d0bd579c13693c2ae
```

KD metrics：

| Dataset | S | wF | meanF | meanE | MAE |
| --- | ---: | ---: | ---: | ---: | ---: |
| CAMO | .863 | .818 | .844 | .920 | .050 |
| COD10K | .864 | .782 | .809 | .929 | .024 |
| NC4K | .885 | .838 | .860 | .932 | .033 |

写作边界：Gate 2 通过，但不是正向改进。不要把 KD 写成有效提升；只能写当前 online output-level MSE KD 未带来稳定正向收益，后续可探索 teacher cache、feature-level KD 或 boundary KD。

历史恢复 marker 仍保留给审计：

- `epoch_5.pth`
- `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_recover_b2w0_1gpu/epoch_7.pth`
- `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/kd_interruption_analysis.md`
- `/root/data-tmp/workspace/05_reviews/kd_recovery_config_audit.md`
- `/dev/shm/escnet_fast_kd/logs/train_continue_epoch20_b6_w8_4gpu_20260614T100610Z.log`

不要重启：

- `start_kd_full_train.sh`
- `start_kd_fast_shm_train.sh`
- `watch_baseline_then_start_kd.sh`
- 单卡 KD 长训

## Baseline 源码边界

`/root/ESCNet` 当前是 dirty 工作树，包含后续 B0/KD 等实验修改和未跟踪文件，不能再口头等同于 clean baseline。已从 `/root/ESCNet` git HEAD `25c4387e4ea94c247d83a91a749e87b959483a4e` 导出干净 baseline 快照：

`/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean`

验证状态：

- `config.py`、`models/ESCNet.py`、`train.py` 与 git HEAD 对比一致。
- `python -m py_compile` 已通过。
- `load_config('config.local.yaml')` 已通过。
- CPU strict checkpoint 加载已通过：`/root/data-tmp/epoch_120.pth` 对 clean ESCNet-B5 模型 missing=0、unexpected=0，参数量 99,903,234。
- baseline 统一复评入口 `start_baseline_prob_eval_clean.sh` 已完成其职责；不要重复启动。

Gate 1 clean baseline metrics：

| Dataset | S | wF | meanF | meanE | MAE |
| --- | ---: | ---: | ---: | ---: | ---: |
| CAMO | .881 | .842 | .864 | .933 | .043 |
| COD10K | .877 | .802 | .824 | .938 | .021 |
| NC4K | .897 | .857 | .878 | .942 | .029 |

## Light 主结果

Light-ESCNet B2-C64 no-KD 是当前核心学生模型：

```text
/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42
/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42_prob_eval_v2
```

| Dataset | S | wF | meanF | meanE | MAE |
| --- | ---: | ---: | ---: | ---: | ---: |
| CAMO | .862 | .818 | .843 | .918 | .051 |
| COD10K | .866 | .782 | .808 | .928 | .024 |
| NC4K | .886 | .840 | .862 | .933 | .033 |

profile：29.807714M params，36.391 GMACs，113.743 MB model，237.439 MB peak memory。

## Controlled Speed

受控条件：idle V100、input size 416、batch=1、warmup=50、repeat=100、same profile command。

| Model | Latency | FPS |
| --- | ---: | ---: |
| ESCNet-B5 C128 | 73.0148 ms | 13.6958 |
| Light-ESCNet B2-C64 | 34.3106 ms | 29.1455 |
| KD Light-ESCNet B2-C64 | 34.8350 ms | 28.7067 |

只写 controlled speed，不写 edge-device deployment、real-time deployment 或最终部署速度。

## B0 分支状态

B0 外部 dirty 分支训练/eval 已完成，最新完整 COD10K 中间行为 epoch120：

```text
S=.8004, wF=.6862, meanF=.7203, meanE=.8878, MAE=.0350
```

最好 S 行仍是 epoch100：

```text
S=.8014, wF=.6882, meanF=.7221, meanE=.8899, MAE=.0346
```

它仍显著低于 accepted Light-B2-C64 COD10K，且未通过独立 candidate gate。用户已把 B0 排除在当前计划外，不要重启 B0 训练、`all.sh` 或 `watch_external_b0_progress.sh`。

B0 观察记录：

```text
/root/data-tmp/workspace/02_experiments/runs/b0_external_observation.md
/root/data-tmp/workspace/02_experiments/runs/b0_external_status_latest.md
/root/data-tmp/workspace/02_experiments/code/external_b0_dirty_snapshot_20260613T200614Z_epoch70_metrics_observation
```

## MobileMamba-T2 分支状态

MobileMamba-T2 是 dirty-tree observation branch。最新且最高 S 的 COD10K 观察行：

```text
epoch50 S=.7487, wF=.6019, meanF=.6482, meanE=.8477, MAE=.0465
```

无 accepted checkpoint。不能进主表、摘要或结论。只读 watcher 可记录状态变化，但不得启动、停止或 signal 训练。

状态入口：

```text
/root/data-tmp/workspace/02_experiments/runs/mobilemamba_t2_external_status_latest.md
/root/data-tmp/workspace/02_experiments/scripts/summarize_external_mobilemamba.py
/root/data-tmp/workspace/02_experiments/scripts/watch_external_mobilemamba_progress.sh
```

## GPU 空闲后的队列

权威命令队列见：

`/root/data-tmp/workspace/02_experiments/scripts/GPU_QUEUE.md`

当前顺序：

1. 不重启 Gate 1 baseline wrapper 或 resume watcher。
2. 不重启 KD watcher 或 KD 训练。
3. 不重启 B0 训练或 watcher。
4. 完成论文/交付文档 Gate 2/3 回填。
5. 重新生成汇总并运行 release audit。

刷新命令：

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

## 已验收的新文档

- `04_paper/drafts/paper_revision_plan.md`
- `05_reviews/experiment_gap_audit.md`
- `01_literature/literature_gap_update_2026.md`
- `04_paper/drafts/evidence_index.md`
- `04_paper/drafts/finalization_gates.md`
- `04_paper/drafts/claim_evidence_audit.md`
- `04_paper/drafts/paper_final_patch_plan.md`
- `04_paper/drafts/submission_protocol_checklist.md`
- `04_paper/drafts/paper_submission_readiness.md`
- `04_paper/drafts/paper_claim_evidence_matrix.md`
- `04_paper/drafts/paper_delivery_manifest.md`
- `04_paper/drafts/reproducibility_manifest.md`
- `04_paper/drafts/teacher_share_pack.md`
- `04_paper/drafts/presentation_outline.md`

## 当前论文边界

可以写：

- Light B2-C64 no-KD 120 epoch 完成，CAMO/COD10K/NC4K 概率图评估完整。
- clean ESCNet-B5 三数据集 probability baseline 完成。
- 相对 clean ESCNet-B5 baseline，Light 平均 S-measure 下降约 0.014、MAE 增加约 0.005，同时参数量、GMACs、模型大小、峰值显存约下降 70%。
- Controlled speed profile 完成：baseline 73.01 ms / 13.70 FPS，Light 34.31 ms / 29.15 FPS，KD Light 34.84 ms / 28.71 FPS。
- KD 完成但未带来稳定正向收益，可作为负结果和训练成本分析。

暂不能写：

- KD 有效或提升。
- B0 极限压缩结论。
- MobileMamba 主结果。
- edge-device deployment、real-time deployment 或最终部署速度。
- B2-C128/B5-C64 独立消融贡献，直到训练/评测完成。
- SOTA 或首次提出。

恢复写作前先检查：

```bash
sed -n '1,220p' /root/data-tmp/workspace/04_paper/drafts/finalization_gates.md
sed -n '1,180p' /root/data-tmp/workspace/04_paper/drafts/claim_evidence_audit.md
sed -n '1,220p' /root/data-tmp/workspace/04_paper/drafts/paper_claim_evidence_matrix.md
```

## 历史 Marker

以下 marker 供审计和追溯使用：

- `P0_gate1_kd_handoff_card.md`
- `epoch_5.pth`
- `resume_stopped_prob_eval_when_gpu_idle.sh`
- `watch_baseline_then_start_kd.sh`
- `clean_prob_re_eval_complete`
- `external_dirty_tree_observation_only`
- `release_audit_latest.md`
