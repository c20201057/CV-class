# Finalization Gates

更新时间：2026-06-14T15:12:38Z / 2026-06-14 23:12:38 CST

## 最新 Gate 状态

- 总控原则：不偷懒，不因为怕风险而保守；高风险路线保留隔离验收入口，但不应抢占 Gate 1/2/3 已完成证据的论文回填和审计闭环。
- Gate 1 clean ESCNet-B5 probability baseline 已完成：CAMO/COD10K/NC4K 均为 `clean_prob_re_eval_complete`，baseline state 为 complete。
- Gate 2 KD 已完成：final checkpoint、CAMO/COD10K/NC4K probability eval、integrity 和 `final_main_kd` metadata 已完成；相对 no-KD 基本持平或略低，只能写负结果分析。
- Gate 3 speed 已完成：baseline、Light、KD 的 idle V100 same-command latency/FPS profile 已完成。
- 外部 B0 dirty-tree rerun 已按用户明确要求停止；外部 MobileMamba-T2 当前未观察到运行，两者同样是 observation。
- MobileMamba-T2 只读 watcher 已启动，PID 530956；它只刷新状态和事件日志，不干预训练。
- 论文可以使用 clean baseline 与 Light-B2-C64 no-KD 的同协议差值、KD 中性/负向结果和受控 speed 数字；B0/MobileMamba 仍不能越过各自 gate。

本文档定义论文从 interim/reference 草稿进入定稿前必须满足的证据门槛。任何未通过 gate 的结果只能写作“待验证”“历史参考”或“工程观察”，不能进入主结论。

## Gate 0: Workspace And Baseline Boundary

- 所有新增实验代码、run、表格和论文产物必须位于 `/root/data-tmp/workspace` 或 `/root/data-tmp/tmp`。
- `/root/ESCNet` 当前为 dirty 工作树，不作为 clean baseline repo。
- clean baseline repo 固定为 `/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean`。
- ESCNet-B5 teacher checkpoint 固定为 `/root/data-tmp/epoch_120.pth`。
- 不得使用 `/root/ESCNet/checkpoints/escnet/epoch_120.pth` 作为 teacher 或主 baseline。
- `/root/ESCNet/checkpoints/escnet` 当前为 symlink，指向 data-tmp legacy checkpoint 归档；该路径保持可读只是为了追溯，不提升为 baseline。
- 根分区当前仍显示 100%/0 可用；所有新大产物和临时文件必须写入 `/root/data-tmp/workspace` 或 `/root/data-tmp/tmp`。

验收证据：

- `baseline_escnet_clean/BASELINE_SOURCE.md`
- clean ESCNet-B5 strict load：missing=0, unexpected=0
- `metrics_all.csv` 中 baseline 行必须有 `protocol`, `repo_boundary`, `checkpoint`, `status`

## Gate 1: Clean ESCNet-B5 Probability Baseline

目标：把 ESCNet-B5 从 historical reference 升级为 clean probability baseline。

必须完成：

1. 使用 clean snapshot 和 `/root/data-tmp/epoch_120.pth` 评测 CAMO、COD10K、NC4K。
2. 预测数量与 GT 数量一致。
3. 输出为概率灰度图，不能是二值图。
4. `check_run_integrity.py` 通过。
5. `metrics_all.csv` 中对应行 `status=clean_prob_re_eval_complete`。

推荐命令：

```bash
TMPDIR=/root/data-tmp/tmp bash /root/data-tmp/workspace/02_experiments/scripts/start_baseline_prob_eval_clean.sh \
  --device cuda:0
```

GPU 忙时 wrapper 会拒绝启动；除非明确要共享 GPU，不使用 `--force_busy_gpu`。

当前验收状态：Gate 1 已 complete。当前 clean baseline 值为 CAMO S=.881/wF=.842/meanF=.864/meanE=.933/MAE=.043，COD10K S=.877/wF=.802/meanF=.824/meanE=.938/MAE=.021，NC4K S=.897/wF=.857/meanF=.878/meanE=.942/MAE=.029。

## Gate 2: KD B2-C64 Completion

目标：验证 output-level online KD 是否能缩小 Light-B2-C64 与 ESCNet-B5 的精度差距。

已完成：

1. fast-shm 四卡路线完成 120 epoch。
2. 产生完整最终 checkpoint：`kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu/epoch_120.pth`。
3. 完成 CAMO、COD10K、NC4K 概率图评测。
4. `check_run_integrity.py` 通过。
5. `metrics_all.csv` 中 KD 行标记为 `final_main_kd`。

历史四卡恢复命令，仅作追溯，不要重复运行：

```bash
TMPDIR=/dev/shm/escnet_fast_kd/tmp /root/data-tmp/workspace/02_experiments/scripts/start_kd_fast_shm_train.sh
```

最终完成 run 使用：

```text
/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config_continue_epoch20_b6_w8_4gpu.yaml
```

最终结果：CAMO S=.863/wF=.818/MAE=.050，COD10K S=.864/wF=.782/MAE=.024，NC4K S=.885/wF=.838/MAE=.033。相对 no-KD，三数据集平均 S 约 -0.001，wF 约 -0.001，MAE 基本不变。

KD 评测复现命令：

```bash
TMPDIR=/root/data-tmp/tmp bash /root/data-tmp/workspace/02_experiments/scripts/run_prob_eval_suite.sh \
  --repo /root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64 \
  --template_config /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config_continue_epoch20_b6_w8_4gpu.yaml \
  --ckpt /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu/epoch_120.pth \
  --exp_id kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval \
  --datasets CAMO,COD10K,NC4K \
  --device cuda:0 \
  --batch_size_valid 8 \
  --method epoch_120 \
  --protocol prob_map \
  --repo_boundary kd_light_b2_c64_recovery_snapshot \
  --metrics_checkpoint /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu/epoch_120.pth \
  --status final_main_kd
```

## Gate 3: Speed And Latency

目标：只有在公平条件下报告速度。

必须完成：

- baseline、Light 和最终 KD 使用同一 `profile_model.py` 命令。
- GPU 空闲、无并发训练/评测任务。
- 同一输入尺寸 416、batch size 1、warmup/repeat 设置一致。
- 若条件不满足，论文只报告 params、GMACs、model size 和 peak memory。

当前状态：

- Gate 3 已 complete。可写受控 speed 数字，但必须保留 profile 条件。

| Model | Latency | FPS | Condition |
| --- | ---: | ---: | --- |
| ESCNet-B5 C128 | 73.01 ms | 13.70 | idle V100, 416, batch 1, warmup 50, repeat 100 |
| Light-B2-C64 | 34.31 ms | 29.15 | idle V100, 416, batch 1, warmup 50, repeat 100 |
| KD Light-B2-C64 | 34.84 ms | 28.71 | idle V100, 416, batch 1, warmup 50, repeat 100 |

## Gate 4A: B0 Extreme Branch

目标：判断外部 PVTv2-B0 online KD 是否值得作为附录或负例。

当前状态：

- `/root/ESCNet` dirty 工作树外部运行。
- COD10K epoch 10 intermediate eval: S=.7692, wF=.6384, MAE=.0425。
- COD10K epoch 20 intermediate eval degraded: S=.7091, wF=.5296, MAE=.0629。
- COD10K epoch 30 intermediate eval recovered: S=.7604, wF=.6168, MAE=.0466，但仍低于 epoch 10。
- COD10K intermediate eval 已落表到 epoch120。该分支在早期明显退化后逐步恢复；epoch100 是当前 B0 最好已落表中间行 S=.8014、wF=.6882、meanF=.7221、meanE=.8899、MAE=.0346。epoch120 最新完整行 S=.8004、wF=.6862、meanF=.7203、meanE=.8878、MAE=.0350；两者仍弱于 Light-B2-C64 COD10K。
- B0 dirty-tree observation rerun 已按用户明确要求停止；实时状态以 `b0_external_status_latest.md` 为准。它不应抢占或阻塞 Gate 2，只能由 KD watcher 等待 GPU 空闲。
- MobileMamba-T2 只读 watcher 日志为 `02_experiments/runs/watch_external_mobilemamba_progress.log`；实时 epoch/iter 以 tick/status 为准且 checkpoint 仍 absent。当前已落表的最新/最佳 COD10K 中间 eval 为 epoch50（S=.7487、wF=.6019、meanF=.6482、meanE=.8477、MAE=.0465），证据边界为 `external_dirty_tree_observation_only`，因此只能作为替代轻量主干路线观察。
- 原始 checkpoint 已包括 `epoch_120.pth`，epoch120 eval metrics 已落表；最新 checkpoint/eval 状态以 `b0_external_status_latest.md` 为准。epoch100 COD10K metrics 仍是当前最好 B0 完整中间行。它们尚未通过 checkpoint load/profile、三数据集 probability eval 与 integrity gate。
- 已做 dirty-tree 观察快照：`/root/data-tmp/workspace/02_experiments/code/external_b0_dirty_snapshot_20260613T200614Z_epoch70_metrics_observation`。

进入论文条件：

1. 验证 checkpoint 能严格/预期加载。
2. 快照代码/config 到 `/root/data-tmp/workspace`。
3. 完成 profile、CAMO/COD10K/NC4K probability eval。
4. 完整性检查通过。
5. 只作为附录探索或失败分析，不替代 Light-B2-C64 主线。

验收入口：

```bash
TMPDIR=/root/data-tmp/tmp /root/data-tmp/workspace/02_experiments/scripts/start_b0_candidate_eval.sh \
  --device cuda:0
```

该 wrapper 会先创建 dirty-tree snapshot，再在 snapshot/source 上执行 profile/load
gate、三数据集 probability eval、integrity 和 release audit。输出 metrics status
固定为 `external_dirty_tree_observation_candidate`，不得改成 `final_main_*`。
真实运行前应优先等待 Gate 1/KD 主队列空闲；`--dry_run` 已通过，可用于预览命令。

## Gate 4B: MobileMamba-T2 Alternative Backbone Branch

目标：判断外部 MobileMamba-T2 替代主干是否值得作为附录探索或负例。

当前状态：

- dirty `/root/ESCNet` 外部运行，当前未观察到训练进程。
- 最新 iter/result/checkpoint 状态以 `02_experiments/runs/mobilemamba_t2_external_status_latest.md` 为准。
- 在 checkpoint load/profile、CAMO/COD10K/NC4K probability eval 和 integrity 全部通过前，只能写作替代轻量主干观察，不进入主表、摘要或结论。

MobileMamba-T2 候选验收入口：

```bash
TMPDIR=/root/data-tmp/tmp /root/data-tmp/workspace/02_experiments/scripts/start_mobilemamba_candidate_eval.sh \
  --device cuda:0
```

该 wrapper 会先创建 `external_mobilemamba_dirty_snapshot_*_candidate_eval`，再执行
profile/load gate、三数据集 probability eval、integrity 和 release audit。输出 metrics
status 同样固定为 `external_dirty_tree_observation_candidate`；`--dry_run` 已通过。

## Gate 5: Paper Claims

定稿允许写：

- Light-B2-C64 no-KD 完成 120 epoch 和三数据集概率图评测。
- 相对 clean ESCNet-B5 probability baseline 的主差值。
- params、GMACs、model size、peak memory 约 70% 降低。
- controlled latency/FPS，必须注明 idle V100 profile 条件。
- KD 的中性/负向结果、B0 和 MobileMamba 的工程状态及风险边界。

定稿前禁止写：

- KD 有效提升；Gate 2 已通过但实测不支持。
- 把 controlled V100 latency/FPS 推广为真实边缘端部署。
- B0 极限压缩结论，除非 Gate 4A 通过。
- MobileMamba 替代主干结论，除非 Gate 4B 通过。
- SOTA、首次提出 KD-COD、实时部署等没有证据的强主张。

## Current Priority Queue

1. 根据 Gate 2/3 结果先执行 `paper_final_patch_plan.md`，再按 `paper_gate_patch_matrix.md` 更新正文、表格、外发材料和证据文档。
2. 重新生成 aggregated results、delta summary、orchestrator tick 和 gate readiness。
3. 运行完整 release audit，并显式加入 KD probability eval integrity。
4. 保持 `watch_baseline_then_start_kd.sh` 为历史 marker；不要重启 watcher 或重复启动 KD。
5. Gate 4A/4B 只有用户或主控明确重新纳入时再做候选验收。
