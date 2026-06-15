# Experiment Gap Audit

审计时间：2026-06-13

审计角色：实验验收/缺口审计 subagent

课题：面向伪装目标分割的轻量化模型研究，实验基底 ESCNet

范围：只读审计 `00_project/orchestrator_status.md`、`00_project/route_decision.md`、`02_experiments/experiment_matrix.md`、`02_experiments/tables/metrics_all.csv`、`02_experiments/tables/profiles.csv`、`04_paper/tables/aggregated_results.md`、`05_reviews/subagent_reviews.md`，并参考已记录命令/日志路径核对风险。不启动训练，不使用 GPU。

2026-06-13T17:36:30Z 主控补充：本审计中的“GPU 空闲后建议执行队列”是历史建议，已被
`/root/data-tmp/workspace/02_experiments/scripts/GPU_QUEUE.md` 取代。后续不得再用其中直接指向 dirty
`/root/ESCNet` 的 baseline 命令；clean baseline 复评必须使用
`/root/data-tmp/workspace/02_experiments/scripts/start_baseline_prob_eval_clean.sh`，KD 恢复必须使用
`/root/data-tmp/workspace/02_experiments/scripts/start_kd_full_train.sh` 或该 runbook 中的降级命令。

## 总结判断

当前实验链条已经具备一条可写论文的主线：ESCNet-B5 teacher/heavy baseline 与 Light-ESCNet B2-C64 no-KD student 的精度-效率折中。最稳妥的论文核心结论是：在保留 ESCNet 边界-语义协同结构的前提下，将主干从 PVTv2-B5 换为 PVTv2-B2，并将解码通道压到 C64，可以在 CAMO/COD10K/NC4K 上维持接近性能，同时显著降低参数量、GMACs、模型大小和峰值显存。

但当前还不能写 KD 有效、速度真实提升、结构消融完整、可视化充分，也不能把 `/root/ESCNet/checkpoints/escnet/epoch_120.pth` 或 `test.py` 二值化评测混入主表。`aggregated_results.md` 中 `light_b2_c64_trained_416` 的 FPS=11.90 来自受并发任务影响的训练后 profile，不应作为最终速度结论。

## 已验收证据

### 可用于论文主结果的精度证据

1. ESCNet-B5 历史 baseline 三数据集指标已在 `metrics_all.csv` 和 `experiment_matrix.md` 中记录：
   - COD10K：S=.873，wF=.808，meanF=.827，meanE=.942，MAE=.020。
   - CAMO：S=.875，wF=.849，meanF=.867，meanE=.937，MAE=.041。
   - NC4K：S=.893，wF=.864，meanF=.881，meanE=.945，MAE=.028。
   - 来源为 `/root/ESCNet/results_epoch120/result.txt`，对应历史 teacher checkpoint `/root/data-tmp/epoch_120.pth`。

2. Light-ESCNet B2-C64 no-KD 完整闭环已验收：
   - 训练 run：`/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42`。
   - checkpoint：`epoch_120.pth`。
   - 概率图评测 run：`/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42_prob_eval_v2`。
   - CAMO：S=.862，wF=.818，meanF=.843，meanE=.918，MAE=.051。
   - COD10K：S=.866，wF=.782，meanF=.808，meanE=.928，MAE=.024。
   - NC4K：S=.886，wF=.840，meanF=.862，meanE=.933，MAE=.033。
   - 完整性记录显示预测数量 CAMO/COD10K/NC4K 分别为 250/2026/4121，概率图灰度唯一值检查通过。

3. 与历史 ESCNet-B5 相比，Light B2-C64 no-KD 的平均变化可写为：
   - S-measure：0.880 -> 0.871，下降约 .009。
   - wF-measure：0.840 -> 0.813，下降约 .027。
   - mean F-measure：0.858 -> 0.838，下降约 .021。
   - mean E-measure：0.941 -> 0.926，下降约 .015。
   - MAE：0.030 -> 0.036，增加约 .006。

### 可用于论文效率表的结构证据

1. Baseline profile：
   - Exp ID：`baseline_escnet_b5_416_e120`。
   - Params：99.90M。
   - GMACs：129.02。
   - Model size：381.17 MB。
   - Peak memory：829.77 MB。
   - Latency/FPS 初始记录：61.806 ms / 16.18 FPS。

2. Light B2-C64 profile：
   - Params：29.81M。
   - GMACs：36.39。
   - Model size：113.74 MB。
   - Peak memory：237.44 MB。
   - 结构压缩比例：参数量 -70.16%，GMACs -71.79%，模型大小 -70.16%，峰值显存 -71.38%。

3. 以上 Params、GMACs、model size、peak memory 可进入论文效率表。FLOPs/GMACs 来自 `torch.profiler.profile(with_flops=True)`，状态为 `estimated`，论文中应写成估计计算量，不要暗示为硬件无关的精确理论 FLOPs。

### 已验收工具链

1. `infer_prob.py` 和 `run_prob_eval_suite.sh` 已作为主表评测协议，输出 sigmoid 概率图并按 GT 原尺寸保存。
2. `collect_metrics.py` 可幂等更新指标 CSV。
3. `profile_model.py` 已支持 checkpoint/随机初始化 profile，并记录环境、设备、warmup/repeat、checkpoint load 状态。
4. KD 独立代码目录存在，batch 1/batch 4 smoke 已通过；但 full train 只到 epoch 5 中断，不能作为论文结果。

## 需要重跑或重新测的结果

### P0 必须补齐

1. Baseline 三数据集统一概率图复评。
   - 当前 baseline 主表三数据集来自历史预测目录，CAMO 概率图复评已证明 `/root/data-tmp/epoch_120.pth` 与历史结果高度一致，但三数据集统一概率图 run 尚未完成。
   - 目的：消除历史预测目录与新 `run_prob_eval_suite.sh` 之间的协议差异风险。

2. KD B2-C64 full train 与三数据集概率图评测。
   - 当前 KD train 在 epoch 5 收到 SIGKILL，日志只证明链路和 loss 下降趋势，不证明最终效果。
   - KD 配置应使用实际 run config `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config.yaml`，该文件已经是 `multi_GPU: true`、`device_ids: [0,1,2,3]`、`save_last: 120`、`save_step: 1`。
   - 源码目录下 `configs/kd_light_b2_c64.yaml` 仍显示 `save_last: 30`、`save_step: 3`，重启前必须核对不要误用旧保存策略。

3. Baseline 与 Light 的空闲 GPU 同条件 latency/FPS 复测。
   - `profiles.csv` 中 Light trained latency/FPS 为 84.01 ms / 11.90 FPS，已被 `route_decision.md` 和 `subagent_reviews.md` 标记为受并发任务影响。
   - 当前论文只能写结构复杂度和显存收益，不能写 Light trained 实测速度慢于或快于 baseline。

### P1 强烈建议补齐

1. `light_b2_c128_e120_s42`：PVTv2-B2 + C128，隔离 backbone 压缩收益。
2. `light_b5_c64_e60_s42`：PVTv2-B5 + C64，隔离 decoder 窄化收益。
3. 可视化：Image、GT、ESCNet-B5、Light B2-C64 no-KD、KD/B0 如完成。优先 CAMO 复杂边界、COD10K 小目标、NC4K 保持较好的案例，以及 CAMO 失败案例。

### P2 可选

1. PVTv2-B0 + C64 极限压缩分支：当前 `/root/ESCNet` 中 B0 KD 分支被记录为 running，输出到 `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0`。完成后必须 profile + 概率图评估，且只能作为高风险附录/消融候选。
2. depthwise FEM、INT8/ONNX 等部署扩展：当前不应挤占 KD、baseline 复评和核心消融的 GPU 时段。

## 数值污染与协议不一致风险

### R1: Baseline checkpoint 污染

严重级别：高。

证据：`route_decision.md` 和 `subagent_reviews.md` 明确指出 `/root/ESCNet/checkpoints/escnet/epoch_120.pth` 是 2026-06-13 后续重训产物；用它重推 CAMO 约 S=.819/MAE=.069，低于历史 baseline。主 baseline 与 teacher 必须固定为 `/root/data-tmp/epoch_120.pth`。

处理：所有 KD teacher、baseline 复评、teacher 预测缓存均使用 `/root/data-tmp/epoch_120.pth`。论文和表格不得引用 `/root/ESCNet/checkpoints/escnet/epoch_120.pth` 的指标作为 ESCNet-B5 baseline。

### R2: 二值化 `test.py` 与概率图协议混用

严重级别：高。

证据：Ptolemy 的 CAMO smoke 指标 S=.811/MAE=.067 被判定不能入论文；Huygens 已将概率图推理定为主协议。`run_prob_eval_suite.sh` 明确使用 `infer_prob.py`，而不是 ESCNet 原 `test.py`。

处理：论文主表只接受概率图协议或已确认与 `/root/data-tmp/epoch_120.pth` 匹配的历史 baseline。所有新模型必须走 `run_prob_eval_suite.sh`。

### R3: Latency/FPS 受并发任务污染

严重级别：高。

证据：`profiles.csv` 中 Light pretrained 为 38.73 ms / 25.82 FPS，trained 为 84.01 ms / 11.90 FPS；`route_decision.md` 明确训练后 latency/FPS 受并发任务影响。`aggregated_results.md` 目前把 11.90 FPS 填进主紧凑表，存在误导风险。

处理：最终论文速度表必须在 GPU 空闲时统一复测 baseline、teacher checkpoint、Light trained、KD trained。复测前不要写“FPS 提升”作为实测结论，只写 Params/GMACs/model size/peak memory 的稳定收益。

### R4: KD 结果未完成

严重级别：高。

证据：KD smoke 通过，但 full train 在 epoch 5 因 SIGKILL 中断。当前没有 KD checkpoint epoch 120，也没有三数据集概率图指标。

处理：不能写 KD 提升精度、补偿 CAMO 边界或改善 wF/MAE。只能写“KD 分支已实现并通过 smoke，等待完整训练验证”。

### R5: 聚合表混合 pretrain/trained rows

严重级别：中。

证据：`aggregated_results.md` 同时列出 `light_b2_c64_pretrain_416` 与 `light_b2_c64_trained_416`；前者是 random_init profile，无精度；后者有精度但速度受污染。

处理：论文主表建议只保留已训练模型的精度行；结构 profile 可单独放效率表。`light_b2_c64_pretrain_416` 只能作为结构复杂度预验证，不应出现在最终主结果表。

### R6: 消融证据不足

严重级别：中。

证据：已准备 `light_b2_c128.yaml` 和 `light_b5_c64.yaml`，但没有训练/评测结果。当前只能证明 B2-C64 组合有效，不能定量拆分 backbone 替换与 decoder 窄化各自贡献。

处理：若论文需要“系统轻量化分析”，至少补 B2-C128 或 B5-C64 之一；最优是两者都做。

## 阻塞项优先级

| Priority | 阻塞项 | 当前状态 | 解锁后的论文收益 |
| --- | --- | --- | --- |
| P0 | Baseline 三数据集统一概率图复评 | CAMO 已局部验证，三数据集未闭环 | 消除主表协议争议 |
| P0 | KD B2-C64 full train + prob eval | smoke 通过，epoch 5 SIGKILL | 支撑或否定“蒸馏补偿”贡献 |
| P0 | 空闲 GPU latency/FPS 同条件复测 | trained Light 速度受并发污染 | 让效率表可写实测速度 |
| P1 | B2-C128 消融 | config 已准备，未训练 | 拆出 backbone 压缩效果 |
| P1 | B5-C64 消融 | config 已准备，未训练 | 拆出 decoder 窄化效果 |
| P1 | 可视化与失败案例 | 未见完整生成结果 | 支撑边界/小目标叙事，解释 CAMO 下降 |
| P2 | B0 极限压缩分支验收 | 外部分支 running | 可作为附录或高压缩候选 |

## 下一轮 GPU 空闲后的最优命令队列

以下命令为 GPU 空闲后建议执行队列，本次审计未运行。所有输出必须继续写入 `/root/data-tmp/workspace` 或 `/root/data-tmp/tmp`。

### 0. 启动前检查

```bash
mkdir -p /root/data-tmp/tmp
nvidia-smi
sed -n '1,80p' /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config.yaml
ls -lh /root/data-tmp/epoch_120.pth
```

验收点：确认四卡空闲；KD run config 为 `multi_GPU: true`、`device_ids: [0,1,2,3]`、`save_last: 120`、`save_step: 1`；teacher checkpoint 是 `/root/data-tmp/epoch_120.pth`。

### 1. 先跑 baseline 统一概率图复评

```bash
TMPDIR=/root/data-tmp/tmp bash /root/data-tmp/workspace/02_experiments/scripts/run_prob_eval_suite.sh \
  --repo /root/ESCNet \
  --template_config /root/ESCNet/config.yaml \
  --ckpt /root/data-tmp/epoch_120.pth \
  --exp_id baseline_escnet_b5_prob_e120 \
  --datasets CAMO,COD10K,NC4K \
  --device cuda:0 \
  --batch_size_valid 8
```

验收点：三数据集 GT/pred 数量对齐；概率图非二值；指标写入 `metrics_all.csv`。若与历史 baseline 差异很小，可用统一概率图结果替换主表 baseline；若差异明显，必须在论文中解释历史预测与新协议差异。

### 2. 重启 KD full training

```bash
mkdir -p /root/data-tmp/tmp /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/logs
cd /root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64
TMPDIR=/root/data-tmp/tmp torchrun --nproc_per_node=4 train.py \
  --config /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config.yaml \
  2>&1 | tee /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/train_ddp_rerun.log
```

验收点：至少保存 `epoch_120.pth` 或最高 epoch checkpoint；训练日志完整；若再次 SIGKILL，由于逐 epoch 保存，可从最高 checkpoint 判定是否需要 resume 或直接短评。

### 3. KD 三数据集概率图评测

```bash
TMPDIR=/root/data-tmp/tmp bash /root/data-tmp/workspace/02_experiments/scripts/run_prob_eval_suite.sh \
  --repo /root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64 \
  --template_config /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config.yaml \
  --ckpt /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/epoch_120.pth \
  --exp_id kd_light_b2_c64_e120_s42_prob_eval \
  --datasets CAMO,COD10K,NC4K \
  --device cuda:0 \
  --batch_size_valid 8
```

验收点：只接受概率图结果；若 `epoch_120.pth` 不存在，显式替换为最高 epoch checkpoint，并在结果表和论文中标出 epoch。

### 4. 空闲 GPU 同条件 profile 复测

```bash
python /root/data-tmp/workspace/02_experiments/scripts/profile_model.py \
  --repo /root/ESCNet \
  --config /root/ESCNet/config.yaml \
  --ckpt /root/data-tmp/epoch_120.pth \
  --out /root/data-tmp/workspace/02_experiments/runs/profile_escnet_b5_prob_e120_idle/profile.json \
  --device cuda:0 \
  --warmup 50 \
  --repeat 100 \
  --exp-id baseline_escnet_b5_416_e120_idle

python /root/data-tmp/workspace/02_experiments/scripts/profile_model.py \
  --repo /root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64 \
  --config /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/config.yaml \
  --ckpt /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/epoch_120.pth \
  --out /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/profile_epoch120_idle.json \
  --device cuda:0 \
  --warmup 50 \
  --repeat 100 \
  --exp-id light_b2_c64_trained_416_idle

python /root/data-tmp/workspace/02_experiments/scripts/profile_model.py \
  --repo /root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64 \
  --config /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config.yaml \
  --ckpt /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/epoch_120.pth \
  --out /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/profile_epoch120_idle.json \
  --device cuda:0 \
  --warmup 50 \
  --repeat 100 \
  --exp-id kd_light_b2_c64_trained_416_idle
```

验收点：三者在同一 GPU、同一 input size、同一 warmup/repeat 下测；论文速度结论只使用 `_idle` 行。

### 5. 核心消融训练顺序

如果 KD 完成且仍有 GPU 时间，优先顺序如下：

```bash
cd /root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64
TMPDIR=/root/data-tmp/tmp torchrun --nproc_per_node=4 train.py \
  --config /root/data-tmp/workspace/02_experiments/configs/light_b2_c128.yaml \
  2>&1 | tee /root/data-tmp/workspace/02_experiments/runs/light_b2_c128_e120_s42/train_ddp.log
```

```bash
cd /root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64
TMPDIR=/root/data-tmp/tmp torchrun --nproc_per_node=4 train.py \
  --config /root/data-tmp/workspace/02_experiments/configs/light_b5_c64.yaml \
  2>&1 | tee /root/data-tmp/workspace/02_experiments/runs/light_b5_c64_e60_s42/train_ddp.log
```

训练完成后两者均使用 `run_prob_eval_suite.sh` 评 CAMO/COD10K/NC4K，并用 `profile_model.py` 生成结构效率行。若时间只够一个消融，优先 `light_b2_c128_e120_s42`，因为它直接回答“B5->B2 的主干压缩贡献”。

### 6. 可视化队列

等待 baseline 统一概率图、Light no-KD、KD 结果齐备后再生成可视化。优先挑选：

1. CAMO：Light wF/MAE 下降明显的复杂边界失败例。
2. COD10K：小目标或弱对比目标，展示压缩代价。
3. NC4K：Light 接近 baseline 的成功例。

可视化必须包含 Image、GT、ESCNet-B5、Light B2-C64 no-KD；KD 只有在完整训练通过后加入。

## 论文当前可写结论边界

### 可以写

1. 本项目基于 ESCNet 构建了隔离 run、统一概率图评测和 profiling workflow。
2. ESCNet-B5 是强 teacher/heavy baseline，Light-ESCNet B2-C64 是当前主 student。
3. Light-ESCNet B2-C64 在三数据集上相对 ESCNet-B5 平均 S-measure 仅下降约 .009、MAE 增加约 .006。
4. Light-ESCNet B2-C64 的参数量、GMACs、模型大小和峰值显存约下降 70%。
5. CAMO 上 wF/MAE 下降更明显，提示复杂边界和小样本场景仍需要 KD 或边界补偿。

### 暂时不能写

1. 不能宣称 KD 已提升性能或弥补 CAMO 下降。
2. 不能宣称最终实测 FPS 提升，直到空闲 GPU 同条件复测完成。
3. 不能宣称 backbone 压缩和 decoder 窄化的独立贡献已经定量证明。
4. 不能把 `test.py` 二值化输出或 Ptolemy smoke 指标写进主表。
5. 不能把 `/root/ESCNet/checkpoints/escnet/epoch_120.pth` 作为主 baseline 或 teacher 结果。
6. 不能宣称 Light-ESCNet 是 SOTA；当前证据支持的是“强基线上的轻量化精度-效率折中”。

## 主控后记

更新时间：2026-06-13T15:36:00Z

本审计完成后状态已有更新：

- KD B2-C64 full train 已重启，teacher 成功加载，训练进入正常迭代，并已保存逐 epoch checkpoint；后续仍需等待 epoch 120 和三数据集概率图评估后才能写 KD 有效性。
- PVTv2-B0 外部蒸馏分支当时已停止，日志停在 epoch 5 iter 100，未保存 checkpoint；当前只作为失败记录，不再作为 running 分支等待。注意：该外部分支后来重新启动，见下方二次后记。
- `aggregated_results.md` 已修复 Light trained FPS 误导风险，训练后精度行暂使用干净同结构 profile，并在表下注明受并发污染的 trained latency/FPS 不作为 compact speed comparison。

## 主控二次后记

更新时间：2026-06-13T16:10:13Z

本审计完成后状态再次变化：

- KD B2-C64 第一次 rerun 已保存 `epoch_1.pth` 至 `epoch_5.pth`，但 epoch 6 附近 DataLoader worker 被 SIGKILL。
- 主控已补充 `train.py` resume 支持，并以 `num_workers=0` 从 `epoch_5.pth` 恢复；恢复成功进入 epoch 6，但在 iter 100/252 后 rank0 再次 SIGKILL，未保存 `epoch_6.pth`。
- 当前 KD 不能写入论文结果；`epoch_5.pth` 只是恢复点。完整分析见 `02_experiments/runs/kd_light_b2_c64_e120_s42/kd_interruption_analysis.md`。
- `/root/ESCNet` 外部 PVTv2-B0 online KD 四卡任务重新运行，日志已到 epoch 3 附近。主控当前不抢占该任务，等待四卡释放后恢复 KD B2-C64。

## 最重要风险

1. 主表 baseline 若不统一概率图复评，容易被质疑历史预测协议与新 student 协议不完全一致。
2. `aggregated_results.md` 当前训练后 Light FPS=11.90 有污染风险，最终论文必须删除或替换为空闲复测行。
3. KD 是论文贡献叙事里最诱人的补偿分支，但当前没有完整结果；若 GPU 时间有限，应优先跑 KD 而不是扩展新模块。
4. 消融不足会让“为什么这样轻量化”显得像经验选择；至少补一个 B2-C128，最好再补 B5-C64。
5. 可视化缺失会削弱对 CAMO 下降、边界保留和失败模式的解释力。
