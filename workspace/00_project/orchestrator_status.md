# Orchestrator Status

更新时间：2026-06-14T15:31:36Z / 2026-06-14 23:31:36 CST

## 最新状态覆盖

- 当前无活跃 train-like/GPU-like 进程，GPU0-3 空闲。
- Gate 1 clean ESCNet-B5 probability baseline 已完成 CAMO/COD10K/NC4K，三行均为 `clean_prob_re_eval_complete`。
- Gate 2 KD B2-C64 已完成 120 epoch final checkpoint、三数据集 probability eval 和 checkpoint 完整性证据；它不是正向提升结果，只能作为中性/负向结果与 online teacher 成本分析。
- Gate 3 controlled speed 已完成，速度数字只能按 idle V100、416 input、batch=1、warmup=50、repeat=100 条件写入。
- B0 和 MobileMamba-T2 继续保持 `external_dirty_tree_observation_only`，不能进入主表、摘要或结论。
- 当前工作阶段：回填论文和交付控制文档，刷新聚合结果与 tick，随后跑完整 release audit。不要启动新的训练。

## 已完成

- 抽取并阅读 `CV开题报告.pdf`，文本位于 `00_project/cv_report_extracted.txt`。
- 审计 `/root/ESCNet`：确认适合作为强基线/teacher 和轻量化改造基底，但当前 dirty tree 不能作为 clean baseline。
- 审计环境：4 x Tesla V100-SXM2-16GB，PyTorch 2.5.1+cu121，数据集完整。
- 建立/补强工作区 workflow、master plan、agent prompt、验收协议、任务板。
- 派发并验收 P0 worker：baseline profile、评估套件、Light-ESCNet B2-C64 实现。
- 已下载 PVTv2-B2 预训练权重，并将 `light_b2_c64.yaml` 切换为 `bb_pretrained: true`。
- 完成 `smoke_light_b2_c64_ddp_e1` 四卡 1 epoch smoke。
- 概率图推理协议已定稿，`infer_prob.py` 与 `run_prob_eval_suite.sh` 可用于主表评测。
- 论文初稿、主结果表模板、证据矩阵和交付清单已建立在 `/root/data-tmp/workspace/04_paper/`。
- clean ESCNet baseline snapshot 已固化：`/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean`，来源 git HEAD `25c4387e4ea94c247d83a91a749e87b959483a4e`。
- clean ESCNet-B5 teacher checkpoint 固定为 `/root/data-tmp/epoch_120.pth`，CPU strict load missing=0、unexpected=0。
- clean ESCNet-B5 probability baseline 已完成：
  - CAMO S=.881, wF=.842, meanF=.864, meanE=.933, MAE=.043。
  - COD10K S=.877, wF=.802, meanF=.824, meanE=.938, MAE=.021。
  - NC4K S=.897, wF=.857, meanF=.878, meanE=.942, MAE=.029。
- Light-ESCNet B2-C64 no-KD 完成 120 epoch、三数据集 probability eval 和结构 profile：
  - CAMO S=.862, wF=.818, meanF=.843, meanE=.918, MAE=.051。
  - COD10K S=.866, wF=.782, meanF=.808, meanE=.928, MAE=.024。
  - NC4K S=.886, wF=.840, meanF=.862, meanE=.933, MAE=.033。
  - profile: 29.807714M params，36.391 GMACs，113.743 MB model，237.439 MB peak memory。
- KD B2-C64 经过 smoke、DDP/NCCL 排障、fast-shm IO 加速和 batch/worker 调优后完成 120 epoch：
  - final config: `02_experiments/runs/kd_light_b2_c64_e120_s42/config_continue_epoch20_b6_w8_4gpu.yaml`。
  - final run: `02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu`。
  - checkpoint: `epoch_120.pth`，sha256 `36f0680943279d77c038ee16f4e5a341dd4b9f61600d2a2d0bd579c13693c2ae`。
  - eval: `02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval`。
  - CAMO S=.863, wF=.818, meanF=.844, meanE=.920, MAE=.050。
  - COD10K S=.864, wF=.782, meanF=.809, meanE=.929, MAE=.024。
  - NC4K S=.885, wF=.838, meanF=.860, meanE=.932, MAE=.033。
  - 结论：相对 no-KD 基本持平或略低，不能写 KD 提升。
- Controlled speed profile 已完成：
  - ESCNet-B5 C128: 73.0148 ms / 13.6958 FPS。
  - Light-ESCNet B2-C64: 34.3106 ms / 29.1455 FPS。
  - KD Light-ESCNet B2-C64: 34.8350 ms / 28.7067 FPS。
- 已生成 CAMO 可视化、case selection、Light-B2-C64 方法图和精度-效率散点图。
- 已新增并接入 release audit 的关键审计：paper evidence、claim text、CV report alignment、literature citations、prompt principles、task board、B0/MobileMamba status、GPU handoff/runtime、route decision、goal matrix、gate patch readiness、delivery manifest、agent ledger、submission protocol、release registry、probability-run integrity。
- 已新增论文 Gate 结果回填矩阵 `04_paper/drafts/paper_gate_patch_matrix.md` 和 delta 摘要脚本 `04_paper/scripts/generate_delta_summary.py`。
- 已将 `/root/ESCNet/checkpoints/escnet` 下 2026-06-13 后续重训产物归档到 `/root/data-tmp/workspace/02_experiments/runs/legacy_root_ESCNet_checkpoints_escnet_20260613` 并替换为 symlink；这些 checkpoint 不是主 teacher/main baseline。
- 已记录根分区空间诊断：新产物、大文件、临时文件和日志继续写 `/root/data-tmp/workspace` 或 `/root/data-tmp/tmp`，不要把 checkpoint 写回根分区或 `/root/ESCNet`。

## 当前关键判断

短状态锚点：`00_project/current_run_snapshot.md`。恢复目标模式时可先读该文件，再读本长状态。

1. 论文主线采用 Light-ESCNet：PVTv2-B2 + C64 + 边界分支保留。
2. ESCNet-B5 epoch 120 是 teacher/heavy baseline，不作为轻量模型。
3. `/root/ESCNet` 当前是 dirty 工作树；后续 baseline 复评/记录使用 `baseline_escnet_clean`。
4. 概率图推理是论文主表协议。
5. Teacher checkpoint 固定为 `/root/data-tmp/epoch_120.pth`；`/root/ESCNet/checkpoints/escnet/epoch_120.pth` 只可作为 legacy artifact。
6. Light B2-C64 no-KD 支撑核心效率-精度折中结论：相对 clean ESCNet-B5 probability baseline 平均 S 下降约 0.014、平均 MAE 增加约 0.005，同时结构复杂度约降 70%。
7. KD full train/eval 已完成，但不支持“蒸馏提升/缩小差距”的正向主张；论文只能写负结果、训练成本和后续改进方向。
8. Controlled speed 可写入效率表，但必须限定为 idle V100 same-command profile，不推广到 edge-device deployment 或 real-time deployment。
9. PVTv2-B0 dirty branch epoch120 COD10K S=.8004、wF=.6862、meanF=.7203、meanE=.8878、MAE=.0350；best observed epoch100 S=.8014、wF=.6882、meanF=.7221、meanE=.8899、MAE=.0346。该分支仍是 COD10K-only、dirty-tree、未验收 observation。
10. MobileMamba-T2 最新且最高 S 的观察行是 epoch50 COD10K S=.7487、wF=.6019、meanF=.6482、meanE=.8477、MAE=.0465；仍无 accepted checkpoint。
11. B0/MobileMamba 不应抢占 Gate 1/2/3 已完成证据的论文回填和审计闭环。
12. baseline/resume watcher 不需要运行；KD watcher 已完成接力后退出。不要重复启动 `watch_baseline_then_start_kd.sh`。
13. 新增或修改 subagent prompt/pending 任务后，必须跑 `audit_prompt_principles.py`，确保“不偷懒、不因为怕风险而保守”准则没有丢。
14. 改摘要、表格、结论或任何主张前，先查 `paper_claim_evidence_matrix.md`；改后跑 `run_release_audits.sh`。

## 已派发 Worker

| Agent | Task | Status |
| --- | --- | --- |
| Pauli | P0 baseline profiling | pass |
| Ptolemy | P0 evaluation suite | pass |
| Dewey | P0 Light B2-C64 implementation | pass |
| Huygens | P1 probability inference | pass |
| Aristotle | Paper narrative review | pass |
| Poincare | KD route proposal | pass |
| main | `light_b2_c64_e120_s42` full training/eval | pass |
| Feynman | paper revision plan | pass |
| Lagrange | experiment gap audit | pass |
| Lagrange | KD recovery config audit | pass |
| Schrodinger | 2024-2026 literature gap | pass |
| Epicurus | paper baseline boundary audit | pass |
| Feynman | Light B2-C64 narrative bridge review | pass |
| main | `kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu` full training/eval/profile | pass, neutral/negative result |
| external/main | `pvt_v2_b0` distilled extreme branch | high risk; dirty-tree observation only; not main evidence |
| external/main | `mobilemamba_t2` branch | high risk; dirty-tree observation only; not main evidence |

## 等待回收

- 不再等待 Gate 1 clean baseline、Gate 2 KD 或 Gate 3 speed。
- 当前等待的是 Gate 2/3 论文回填后的完整 release audit。
- B0/MobileMamba 候选分支如未来继续推进，必须单独通过 snapshot/load/profile/三数据集 eval/integrity gate；当前不阻塞主线。

## 下一步

1. 完成论文正文、表格、证据矩阵、交付清单、handoff 和任务队列的 Gate 2/3 回填。
2. 重新生成 `aggregated_results.md`、`current_delta_summary.md`、`gate_patch_readiness_latest.md` 和 `orchestrator_tick_latest.md`。
3. 运行完整 release audit，并额外检查 KD probability eval integrity：

```bash
bash /root/data-tmp/workspace/02_experiments/scripts/run_release_audits.sh \
  --add-integrity /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval \
  kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval \
  CAMO,COD10K,NC4K
```

4. 如果 audit 通过，当前阶段可以进入“核心论文交付/老师阅读包”阶段；如果失败，先修复具体审计报告，不启动训练。

## 不要做

- 不要重启 baseline wrapper、baseline/resume watcher 或 `watch_baseline_then_start_kd.sh`。
- 不要重启 B0 训练、`all.sh` 或 B0 watcher。
- 不要自动重启单卡 KD 长训；Gate 2 已完成。
- 不要把 `/root/ESCNet` dirty tree 当成 clean baseline。
- 不要把 `/root/ESCNet/checkpoints/escnet/epoch_120.pth` 当成主 teacher。
- 不要将任何 dirty observation 升级为论文核心结果、摘要贡献或结论依据。
- 不要写 KD 已证明提升。
- 不要写最终部署速度、实时部署或边缘端部署。

## 历史 Marker

以下条目用于审计追溯，不表示当前需要运行：

- `epoch_5.pth`
- `P0_gate1_kd_handoff_card.md`
- `resume_stopped_prob_eval_when_gpu_idle.sh`
- `watch_baseline_then_start_kd.sh`
- `clean_prob_re_eval_complete`
- `external_dirty_tree_observation_only`
