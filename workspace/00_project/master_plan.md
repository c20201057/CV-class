# Master Plan

更新时间：2026-06-13T19:53:20Z

课题：面向伪装目标分割的轻量化模型研究

基底：`/root/ESCNet`

工作区：`/root/data-tmp/workspace`

## 总控目标

以 ESCNet 为强基线和教师，完成一条可复现实验路线，并写成课程论文。论文不以“口头设计”为成果，而以可验收证据为成果：代码快照、配置、checkpoint、三数据集指标、效率 profile、可视化和失败案例。

最终论文主线定为：

> ESCNet 的边缘-语义协同机制对伪装目标边界有效，但原始 PVTv2-B5 与 128 通道解码器过重。本文构建 Light-ESCNet，通过轻量主干、窄解码器、边界分支保留与教师蒸馏，在可解释精度损失内显著降低参数量、计算量、模型大小和峰值显存；推理延迟与 FPS 只在空闲 GPU 同条件复测后进入最终结论。

## 决策原则

1. 不偷懒：所有实验结论必须绑定路径、命令、日志、配置和指标，不接受只描述“应该可以”的结果。
2. 不保守：P0 完成后立刻推进完整训练和蒸馏，不因担心失败而只做安全小改；高风险路线可以做，但必须隔离写入范围。
3. 不混乱：所有新结果写入 `02_experiments/runs/<exp_id>`，不覆盖 `/root/ESCNet` 既有 checkpoint、preds、results。
4. 不编造：短训结果只能用于筛选；论文主表只能使用通过验收的完整评估结果。
5. 不孤立：每个 agent 都要假设代码库中有其他人同时工作，不能回退、清理或覆盖他人结果。

## 阶段计划

### Phase 0: 固化事实与工具

目标：让后续实验结果可入表。

必做：

- 固化 ESCNet-B5 epoch 120 基线：指标、checkpoint、预测路径、配置。
- 实现/验收 `profile_model.py`，补齐 Params、FLOPs/GMACs、latency、FPS、model size、peak memory。
- 实现/验收三数据集评估套件，避免公共 `preds/results` 目录污染。
- 新增概率图推理或明确二值图评估限制，优先解决 MAE 与曲线指标可信度。

通过条件：

- `metrics_all.csv` 与 `profiles.csv` 可被论文表格直接引用。
- 任一实验 run 可由 `metadata.json` 回溯到配置、checkpoint、日志和命令。

### Phase 1: 主模型 Light-ESCNet

目标：得到第一条有论文价值的轻量模型。

必做：

- 实现 `pvt_v2_b2 + inter_channel=64`，保留 ESCNet 的 AETP/Decoder 接口。
- 将 `inter_channel=128` 从硬编码改为 config 控制。
- smoke test：随机输入 forward，输出 `out_edge` 和 4 层 mask。
- 完整训练 `light_b2_c64_e120_s42`，三数据集评估与 profile。

通过条件：

- 参数量预计约 30M 量级，相对 99.9M 基线有明确压缩。
- 至少 CAMO/COD10K/NC4K 完整评估一次。

### Phase 2: 蒸馏补偿

目标：证明轻量化不是简单降配，而是有补偿机制。

必做：

- ESCNet-B5 epoch 120 作为 teacher，eval/frozen。
- Student 为 B2-C64。
- 输出级 KD：MSE/KL 约束最终 mask 概率；可选 edge KD。
- 完整训练 `kd_light_b2_c64_e120_s42`。

通过条件：

- 与无 KD 的 B2-C64 在同一协议下比较。
- 若 KD 不提升，论文转为“蒸馏失败分析”，说明原因和困难样本。

### Phase 3: 消融与高收益风险线

目标：把论文从“一个轻量模型”变成“系统研究”。

优先级：

1. `pvt_v2_b2 + C128`：主干轻量化消融。
2. `pvt_v2_b5 + C64`：解码宽度消融，可 60 epoch 或完整训练。
3. `pvt_v2_b0 + C64`：极限压缩候选。
4. Depthwise FEM / 轻量 DeformConv 替代：高风险高收益，只在主线结果已经可用后推进。
5. INT8/PTQ/ONNX：部署验证，失败也能作为工程限制写入。

### Phase 4: 论文整合

目标：将实验资产转为论文。

必做：

- 相关工作：CAMO/COD10K/NC4K、SINet/PFNet、FDCOD、ESCNet、DGNet/FINet/BPNet/CSFIN/LiteCOD。
- 方法图：ESCNet teacher 与 Light-ESCNet student。
- 表格：精度表、效率表、消融表、精度-效率折中图。
- 可视化：至少 6-10 组，包含成功与失败案例。
- 结论：不夸大 SOTA，强调轻量化折中与边界保留价值。

## 四卡调度建议

当前环境：4 x Tesla V100-SXM2-16GB，PyTorch 2.5.1+cu121。根分区 `/` 已接近满载，后续 checkpoint、预测图和日志必须写入 `/root/data-tmp/workspace`，不要继续堆在 `/root/ESCNet`。

调度：

- GPU 0：baseline/profile/probability inference smoke，低占用任务。
- GPU 1-2：`light_b2_c64_e120_s42` DDP 或单实验加速。
- GPU 3：短训筛选、可视化推理或 KD smoke。

若 DDP 稳定，完整训练优先用 4 卡跑单个 P0/P1 主实验；若 DDP 出现工程风险，则单卡并行不同实验，但必须防止输出目录冲突。

DDP 注意：README 的 `torchrun --nproc_per_node=4 train.py` 不能直接照搬，config 必须同时设置 `multi_GPU: true`、`device_ids: [0,1,2,3]`，并把 `save_model_dir` 指向 run 目录。

## 立即任务队列

1. `P0_profile_baseline`: 先补效率表，避免论文只有精度。
2. `P0_eval_suite`: 固化三数据集独立评估流程。
3. `P1_probability_inference`: 提升评估可信度，必要时重跑 baseline 指标。
4. `P0_light_b2_c64_impl`: 实现 Light-ESCNet 最小变体。
5. `light_b2_c64_e120_s42`: 完整训练主 student。
6. `kd_light_b2_c64_e120_s42`: 完整训练 KD student。

## 路线切换条件

- 如果 B2-C64 精度损失小：进入 KD 与 B0-C64，争取更强压缩。
- 如果 B2-C64 精度损失大但边界尚可：优先 KD、edge KD 和保留 C128 消融。
- 如果 B2-C64 边界崩坏：回退到 B2-C128 或 B5-C64，论文强调边界分支容量对 COD 的影响。
- 如果 DeformConv 导致 profile/部署困难：保留主线，另开 Depthwise FEM 高风险分支，不阻塞论文。
