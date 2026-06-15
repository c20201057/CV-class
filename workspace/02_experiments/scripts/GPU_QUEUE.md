# GPU Queue Runbook

更新时间：2026-06-15T04:48:00Z / 2026-06-15 12:48:00 CST

## 最新调度锚点

- 用户已授权进入下一阶段结构消融扩展。当前 GPU0-3 正在运行 Light-B2-C64 `no_edge_supervision` 四卡训练，PID `1256510`；同步 watcher PID `1259831`。该分支不是已验收结果，训练完成、三数据集 probability eval、profile、integrity/audit 通过前，不得进入主表、摘要或结论。
- 当前 active ablation 代码：`/root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64_no_edge_supervision`。配置：`/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_no_edge_supervision_e120_s42/config_no_edge_supervision_b6_w8_4gpu.yaml`。active log：`/dev/shm/escnet_ablation_no_edge_supervision/logs/train_no_edge_supervision_b6_w8_4gpu_20260615T044543Z.log`。运行期输出：`/dev/shm/escnet_ablation_no_edge_supervision/runs/light_b2_c64_no_edge_supervision_e120_s42_b6_w8_4gpu`。持久同步目录：`/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_no_edge_supervision_e120_s42/light_b2_c64_no_edge_supervision_e120_s42_b6_w8_4gpu`。
- no-edge-supervision 配置边界：B2-C64、`disable_decoder_edge_guidance: false`、decoder 继续使用 edge 引导、`edge_loss_weight: 0.0` 关闭 edge GT 直接监督；`batch_size=6`、`num_workers=8`、`persistent_workers=true`、`prefetch_factor=4`、`save_step=20`，active train data 使用 `/dev/shm/escnet_fast_kd/data/Train`，checkpoint 运行期写 `/dev/shm/escnet_ablation_no_edge_supervision/runs` 并由专用 watcher 同步到 `/root/data-tmp/workspace`。
- 上一阶段 no-edge-guidance 已完成 120 epoch 和 CAMO/COD10K/NC4K probability eval，并随 release audit 通过 integrity。结果为 CAMO S=.846/wF=.786/meanF=.818/meanE=.899/MAE=.058；COD10K S=.847/wF=.749/meanF=.779/meanE=.917/MAE=.028；NC4K S=.873/wF=.815/meanF=.842/meanE=.921/MAE=.038，低于 accepted Light-B2-C64，只能作为“移除 decoder edge guidance 会退化”的结构消融证据候选。
- 当前 Gate 2 KD 四卡 fast-shm 训练已完成到 epoch120；训练进程已退出，GPU 空闲。最终 checkpoint 已在 `/dev/shm/escnet_fast_kd/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu/epoch_120.pth` 生成，并已同步到 `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu/epoch_120.pth`，两者 sha256 均为 `36f0680943279d77c038ee16f4e5a341dd4b9f61600d2a2d0bd579c13693c2ae`。训练配置为 `kd_light_b2_c64_e120_s42/config_continue_epoch20_b6_w8_4gpu.yaml`，active log 为 `/dev/shm/escnet_fast_kd/logs/train_continue_epoch20_b6_w8_4gpu_20260614T100610Z.log`，`latest_train_state.pth` 已验证 `epoch=120`。Gate 2 CAMO/COD10K/NC4K probability eval、integrity check 和 release audit 已通过；KD 三数据集结果基本持平或略低于 no-KD，不得写作 KD 提升。
- Gate 3 controlled speed 已完成：ESCNet-B5 clean baseline 为 73.01 ms / 13.70 FPS，Light-B2-C64 no-KD 为 34.31 ms / 29.15 FPS，KD student 为 34.84 ms / 28.71 FPS；均为 idle `cuda:0`、416 输入、warmup=50、repeat=100。
- Gate 1 clean ESCNet-B5 probability baseline 已 complete；不要再恢复或重复启动 NC4K baseline wrapper。
- MobileMamba-T2 只读 watcher 已启动，PID 530956；它只刷新 `mobilemamba_t2_external_status_latest.md` 和事件日志，不干预训练。
- Gate 1 baseline/resume watcher 不再需要；若旧日志存在仅作历史证据。
- Gate 2 KD watcher 已完成接力后退出；当前不要重启 watcher，也不要重复启动 `start_kd_full_train.sh` 或 `start_kd_fast_shm_train.sh`。当前任务是把 Gate 2/3 已完成证据回填到论文、证据矩阵、交付清单和交接文档，并重新运行 release audit。
- KD 只读状态入口为 `02_experiments/runs/kd_recovery_status_latest.md`，由 `02_experiments/scripts/summarize_kd_recovery.py` 刷新；该脚本只解析 log/checkpoint/process/GPU 快照，不启动、不停止、不 signal 训练。
- 最近单卡证据仅作回退/历史证据：已保存 `kd_light_b2_c64_e120_s42_recover_b2w0_1gpu/epoch_6.pth` 和 `epoch_7.pth`，epoch8 跑到 iter1950 左右后被用户要求停止，未保存 epoch8。单卡日志为 `kd_light_b2_c64_e120_s42/logs/train_resume_epoch5_b2_workers0_1gpu_20260614T063851Z.log`。当前不要自动回到单卡长训。
- 当前一页总览优先看 `00_project/orchestrator_tick_latest.md`。

本文件是 GPU 调度的唯一优先命令队列。旧审计文档里若出现直接使用 dirty `/root/ESCNet` 跑 baseline 的命令，以本文件为准。

## 0. 空闲检查

```bash
mkdir -p /root/data-tmp/tmp
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader,nounits
ps -eo pid,ppid,stat,etime,rss,cmd | grep -E 'torchrun|train.py|run.sh' | grep -v grep
```

若看到 `config_no_edge_supervision_b6_w8_4gpu.yaml`，这是当前用户授权的结构消融训练；只监控，不要重复启动。若仍有外部 `/root/ESCNet` 的 `run.sh`/`torchrun`/`train.py`/`test.py` 进程，先核对是否为用户授权的新任务；当前 Gate 1/2/3 主线已完成，默认不应有 B0/MobileMamba/KD 训练占卡。若看到 `config_resume_epoch5_b2_workers0_1gpu.yaml`，这是旧单卡 KD 路线复活，应先停下并回到四卡完成结果的论文回填策略。B0 历史完整观察为 epoch120 COD10K intermediate eval：S=.8004、wF=.6862、meanF=.7203、meanE=.8878、MAE=.0350；epoch100 仍是当前最好已落表中间行 S=.8014、wF=.6882、meanF=.7221、meanE=.8899、MAE=.0346，但仍显著低于 Light-B2-C64 COD10K。原始 dirty checkpoint 已观察到 `epoch_120.pth`；完整最新 B0 checkpoint/eval/progress 状态以 `b0_external_status_latest.md` 为准。MobileMamba-T2 实时 epoch/iter 以 `orchestrator_tick_latest.md` 和 `mobilemamba_t2_external_status_latest.md` 为准；最新且最高 S 的观察行是 epoch50 COD10K S=.7487, wF=.6019, meanF=.6482, meanE=.8477, MAE=.0465，checkpoint 仍 absent；证据边界为 `external_dirty_tree_observation_only`。

调度优先级：当前先让 no-edge-supervision 消融训练跑到可判断节点。Gate 1 clean baseline、Gate 2 KD eval 和 Gate 3 controlled speed 均已 complete。不要重启 KD watcher，不要重复启动 baseline，不要启动 B0/MobileMamba candidate eval 抢占当前消融。B0/MobileMamba candidate eval 只有在用户或主控明确重新纳入 Gate 4 时再人工触发，否则保留为附录/失败分析候选。

B0 只读状态报告入口：

```bash
python /root/data-tmp/workspace/02_experiments/scripts/summarize_external_b0.py
```

MobileMamba-T2 只读状态报告入口：

```bash
python /root/data-tmp/workspace/02_experiments/scripts/summarize_external_mobilemamba.py
```

MobileMamba 新 checkpoint 或新 COD10K 中间指标行落表后，优先用一键只读同步入口刷新状态、
orchestrator tick、路线/交付控制文档和审计：

```bash
python /root/data-tmp/workspace/02_experiments/scripts/sync_mobilemamba_observation_state.py
```

该入口不启动、不停止、不 signal 训练；只维护 observation artifacts。若只想做
MobileMamba 专项状态刷新而暂不跑完整 release audit：

```bash
python /root/data-tmp/workspace/02_experiments/scripts/sync_mobilemamba_observation_state.py \
  --skip_release_audit
```

B0 新 checkpoint 或新 COD10K 中间指标行落表后，优先用一键只读同步入口刷新状态、
趋势图、orchestrator tick 和审计：

```bash
python /root/data-tmp/workspace/02_experiments/scripts/sync_b0_observation_state.py
```

该入口不启动、不停止、不 signal 训练；只维护 observation artifacts。若只想做 B0
专项状态刷新而暂不跑完整 release audit：

```bash
python /root/data-tmp/workspace/02_experiments/scripts/sync_b0_observation_state.py \
  --skip_release_audit
```

B0 只读进度 watcher 入口：

```bash
setsid env TMPDIR=/root/data-tmp/tmp /root/data-tmp/workspace/02_experiments/scripts/watch_external_b0_progress.sh \
  --poll_seconds 300 \
  > /root/data-tmp/workspace/02_experiments/runs/watch_external_b0_progress.nohup.log 2>&1 < /dev/null &
```

该 watcher 只记录外部 B0 的 iter/latest eval status/result/checkpoint 签名变化，不启动、不停止、不 signal 训练；如已有
`watch_external_b0_progress.sh` 进程存活，不要重复启动。

当前 B0 watcher 已按用户范围约束停止；`watch_external_b0_progress.log` 仅保留为历史证据。不要重启 B0 watcher，除非用户或主控明确重新纳入 B0 观察。

MobileMamba-T2 只读进度 watcher 入口：

```bash
setsid env TMPDIR=/root/data-tmp/tmp /root/data-tmp/workspace/02_experiments/scripts/watch_external_mobilemamba_progress.sh \
  --poll_seconds 300 \
  > /root/data-tmp/workspace/02_experiments/runs/watch_external_mobilemamba_progress.nohup.log 2>&1 < /dev/null &
```

该 watcher 只记录外部 MobileMamba-T2 的 iter/latest eval status/result/checkpoint 签名变化，不启动、不停止、不 signal 训练；如已有
`watch_external_mobilemamba_progress.sh` 进程存活，不要重复启动。

当前已观察到该 watcher 存活，PID 530956，日志为
`/root/data-tmp/workspace/02_experiments/runs/watch_external_mobilemamba_progress.log`。

未来若需要让 watcher 在新 result/checkpoint 签名出现后自动刷新 observation 控制文档，可重启时显式增加：

```bash
  --sync_on_change
```

默认自动同步会调用 `sync_mobilemamba_observation_state.py --skip_release_audit`，仍只做状态、tick、路线/交付控制文档和 MobileMamba 专项审计刷新，不启动、不停止、不 signal 训练；若确实要在每次新签名后跑完整 release audit，再额外加 `--sync_release_audit`。当前 PID 530956 是旧启动参数，只读观察仍有效。

MobileMamba-T2 候选 checkpoint 验收入口已经准备好，但默认会在 GPU 忙时拒绝启动：

```bash
TMPDIR=/root/data-tmp/tmp /root/data-tmp/workspace/02_experiments/scripts/start_mobilemamba_candidate_eval.sh \
  --device cuda:0
```

若只是预览命令，不启动 GPU work：

```bash
/root/data-tmp/workspace/02_experiments/scripts/start_mobilemamba_candidate_eval.sh \
  --dry_run
```

该 wrapper 会创建 `external_mobilemamba_dirty_snapshot_*_candidate_eval`，并用
`status=external_dirty_tree_observation_candidate` 写入 metrics；它只能服务 Gate 4
附录/失败分析，不能把 MobileMamba 升级为主结果。

B0 dirty-tree 轻量源码/配置快照入口：

```bash
/root/data-tmp/workspace/02_experiments/scripts/snapshot_external_b0_dirty_tree.sh
```

已生成当前观察快照：

```text
/root/data-tmp/workspace/02_experiments/code/external_b0_dirty_snapshot_20260613T200614Z_epoch70_metrics_observation
```

该快照只用于追溯外部分支跑了什么；当前 dirty B0 checkpoint 仍必须先有独立
workspace code/config snapshot、checkpoint load/profile、CAMO/COD10K/NC4K probability eval 和完整 metadata/integrity gate，
才能考虑作为附加探索结果。dirty snapshot 本身不能进入主表。

B0 候选 checkpoint 验收入口已经准备好，但默认会在 GPU 忙时拒绝启动：

```bash
TMPDIR=/root/data-tmp/tmp /root/data-tmp/workspace/02_experiments/scripts/start_b0_candidate_eval.sh \
  --device cuda:0
```

若只是预览命令，不启动 GPU work：

```bash
/root/data-tmp/workspace/02_experiments/scripts/start_b0_candidate_eval.sh \
  --dry_run
```

推荐等 B0 完整训练结束后把 `--ckpt/--epoch` 换成最新 checkpoint。该 wrapper 会创建
`external_b0_dirty_snapshot_*_candidate_eval`，并用
`status=external_dirty_tree_observation_candidate` 写入 metrics；它只能服务 Gate 4
附录/失败分析，不能把 B0 升级为主结果。

当前可选自动等待器：

```bash
/root/data-tmp/workspace/02_experiments/scripts/watch_gpu_then_start_baseline_clean.sh \
  --poll_seconds 120 \
  --device cuda:0
```

该 watcher 只会在 GPU 空闲后启动第 1 步 clean baseline 复评，不会启动 KD。它按
`metrics_all.csv` 中 baseline 三数据集 `clean_prob_re_eval_complete` 状态判断是否完成；
如果 run 目录已经存在但 metrics 未完成，会用 `--allow_existing` 重试 clean baseline。
若已有
`/root/data-tmp/workspace/02_experiments/runs/watch_gpu_then_start_baseline_clean.pid`
对应进程存活，不要重复启动。

Gate 1 已 complete；该 watcher 当前可以缺席。若未来因审计回归需要重跑 baseline，必须先确认 metrics 不完整并经主控批准。

Gate 1 被暂停后的自动恢复入口（历史/故障恢复用；当前 Gate 1 已 complete，不应运行）：

```bash
/root/data-tmp/workspace/02_experiments/scripts/resume_stopped_prob_eval_when_gpu_idle.sh \
  --pid 513078 \
  --poll_seconds 120
```

若 PID 已变化，以 `00_project/orchestrator_tick_latest.md` 中
`Gate 1 stopped process lines` 和 process snapshot 为准。

baseline 完成后的 KD 接力 watcher（历史/故障恢复用；当前不应运行，避免绕过四卡修复策略）：

```bash
TMPDIR=/root/data-tmp/tmp nohup /root/data-tmp/workspace/02_experiments/scripts/watch_baseline_then_start_kd.sh \
  --poll_seconds 120 \
  > /root/data-tmp/workspace/02_experiments/runs/watch_baseline_then_start_kd.nohup.log 2>&1 &
```

该 watcher 只在 `metrics_all.csv` 中出现 `baseline_escnet_b5_clean_prob_e120`
三数据集 `clean_prob_re_eval_complete` 后，先运行 release gate，再等待 GPU 空闲并调用
`start_kd_full_train.sh`。

当前 KD watcher 已完成接力后退出。不要重启 watcher；四卡 KD 训练、评测和 controlled speed 均已完成，后续只保留恢复链路日志与 checkpoint 作为历史证据。

## 1. Clean ESCNet-B5 三数据集概率复评

```bash
TMPDIR=/root/data-tmp/tmp bash /root/data-tmp/workspace/02_experiments/scripts/start_baseline_prob_eval_clean.sh \
  --device cuda:0
```

验收（当前已满足；不要重复运行，除非验收回归）：

- 代码必须是 `/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean`。
- checkpoint 必须是 `/root/data-tmp/epoch_120.pth`。
- `metrics_all.csv` 中新行 status 应升级为 `clean_prob_re_eval_complete`。
- `check_run_integrity.py` 通过后，才能把 ESCNet-B5 从 historical reference 升级为 clean probability baseline；当前 Gate 1 已满足该条件并使用 clean baseline delta。
- wrapper 现在会在完整性检查后自动刷新 `aggregated_results.md`，运行 `audit_paper_evidence.py` 与 `audit_claim_text.py`，并在默认三数据集 Gate 1 路径下调用 `run_release_audits.sh --add-integrity` 把 baseline run 纳入完整 release audit。

## 2. KD B2-C64 恢复训练

```bash
TMPDIR=/dev/shm/escnet_fast_kd/tmp /root/data-tmp/workspace/02_experiments/scripts/start_kd_fast_shm_train.sh
```

当前四卡 KD 训练已完成；不要重复运行上面的命令。最终训练证据：

```text
config /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config_continue_epoch20_b6_w8_4gpu.yaml
log /dev/shm/escnet_fast_kd/logs/train_continue_epoch20_b6_w8_4gpu_20260614T100610Z.log
local run /dev/shm/escnet_fast_kd/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu
persistent run /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu
final checkpoint /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu/epoch_120.pth
```

最终四卡配置：

```text
/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config_continue_epoch20_b6_w8_4gpu.yaml
```

最终持久输出目录：

```text
/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu
```

四卡 batch2 曾在 DDP/NCCL 初始化阶段失败；随后四卡 workers0 路线已通过 pure NCCL allreduce probe、KD model DDP init probe，并保存到 `epoch_10.pth`/`latest_train_state.pth`。fast-shm 路线先从 epoch10 恢复到 epoch20，再经 batch6/worker8 加速从 epoch20 跑到 epoch120；训练数据和输出热路径在 `/dev/shm`，持久证据同步到 `/root/data-tmp`，`save_step=20`，实际保留 epoch40/60/80/100/120 checkpoint。双卡 fallback 历史启动后未生成 checkpoint；单卡 fallback 已从 `epoch_5.pth` 恢复并保存到 `epoch_7.pth`，但因过慢已按用户要求停止。当前不要继续单卡长训，优先评测四卡完成结果。

只读状态刷新：

```bash
python /root/data-tmp/workspace/02_experiments/scripts/summarize_kd_recovery.py
sed -n '1,160p' /root/data-tmp/workspace/02_experiments/runs/kd_recovery_status_latest.md
```

## 3. KD 三数据集概率评测

当前四卡 KD epoch120 final checkpoint 的 CAMO/COD10K/NC4K probability eval 已完成，exp_id 为 `kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval`，metadata status 为 `final_main_kd`。结果为 CAMO S=.863/wF=.818/MAE=.050，COD10K S=.864/wF=.782/MAE=.024，NC4K S=.885/wF=.838/MAE=.033。相对 no-KD，KD 仅基本持平或略低，不得写作正向提升。下面命令只作为复现/回归重跑入口，默认不要重复运行。

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

验收：

```bash
python /root/data-tmp/workspace/02_experiments/scripts/check_run_integrity.py \
  --run_dir /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval \
  --exp_id kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu_prob_eval \
  --datasets CAMO,COD10K,NC4K
```

## 4. 空闲同条件速度复测

Gate 3 已完成；以下为已验收的 idle `cuda:0`、416 输入、batch=1、warmup=50、repeat=100 受控 profile。若 profile 证据回归或代码/checkpoint 变化，才重跑本节命令。

```text
ESCNet-B5 clean baseline: 73.01 ms / 13.70 FPS
Light-B2-C64 no-KD:       34.31 ms / 29.15 FPS
KD Light-B2-C64:          34.84 ms / 28.71 FPS
```

```bash
python /root/data-tmp/workspace/02_experiments/scripts/profile_model.py \
  --repo /root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean \
  --config /root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean/config.local.yaml \
  --ckpt /root/data-tmp/epoch_120.pth \
  --out /root/data-tmp/workspace/02_experiments/runs/profile_escnet_b5_416_idle/profile.json \
  --device cuda:0 \
  --warmup 50 \
  --repeat 100 \
  --exp-id baseline_escnet_b5_416_idle
```

```bash
python /root/data-tmp/workspace/02_experiments/scripts/profile_model.py \
  --repo /root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64 \
  --config /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/config.yaml \
  --ckpt /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/epoch_120.pth \
  --out /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/profile_epoch120_idle.json \
  --device cuda:0 \
  --warmup 50 \
  --repeat 100 \
  --exp-id light_b2_c64_trained_416_idle
```

```bash
python /root/data-tmp/workspace/02_experiments/scripts/profile_model.py \
  --repo /root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64 \
  --config /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config_continue_epoch20_b6_w8_4gpu.yaml \
  --ckpt /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu/epoch_120.pth \
  --out /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42_continue_epoch20_b6_w8_4gpu/profile_epoch120_idle.json \
  --device cuda:0 \
  --warmup 50 \
  --repeat 100 \
  --exp-id kd_light_b2_c64_trained_416_idle
```

复测后刷新：

```bash
python /root/data-tmp/workspace/02_experiments/scripts/aggregate_results.py \
  --out_md /root/data-tmp/workspace/04_paper/tables/aggregated_results.md
```

## 5. 每次结果回填后的非 GPU 验收

```bash
bash /root/data-tmp/workspace/02_experiments/scripts/run_release_audits.sh
```

对于每个进入 final 主表的 probability eval run，还必须运行：

```bash
python /root/data-tmp/workspace/02_experiments/scripts/check_run_integrity.py \
  --run_dir <prob_eval_run_dir> \
  --exp_id <exp_id> \
  --datasets CAMO,COD10K,NC4K
```

若任一审计失败，不要改摘要/结论为最终主张；先修正 metadata、表格或正文表述。

baseline/KD 等新 probability eval 完成后，把额外 run 显式加到 release gate：

```bash
bash /root/data-tmp/workspace/02_experiments/scripts/run_release_audits.sh \
  --add-integrity <prob_eval_run_dir> <exp_id> CAMO,COD10K,NC4K
```
