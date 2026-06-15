# 实验矩阵

## 统一设置

- Train: `/root/data-tmp/COD/Train`
- Test: CAMO, COD10K, NC4K
- Metrics: S-measure, weighted F-measure, mean F-measure, mean E-measure, MAE
- Efficiency: Params, FLOPs/GMACs, model size, peak memory; latency/FPS only after idle same-command re-test
- Device record: GPU name, CUDA/PyTorch version, batch size, input size

## Baseline

| Exp ID | Status | Config | Checkpoint | Notes |
| --- | --- | --- | --- | --- |
| baseline_escnet_b5_416_e120 | historical reference | `/root/ESCNet/config.yaml` | `/root/data-tmp/epoch_120.pth` | 历史三数据集结果；不是 clean snapshot probability-protocol final baseline |
| baseline_escnet_b5_clean_prob_e120 | pending | `/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean/config.local.yaml` | `/root/data-tmp/epoch_120.pth` | clean snapshot 三数据集统一概率图复评，GPU 空闲后运行 |

Baseline metrics:

| Dataset | Smeasure | wFmeasure | meanFm | meanEm | MAE |
| --- | ---: | ---: | ---: | ---: | ---: |
| COD10K | .873 | .808 | .827 | .942 | .020 |
| CAMO | .875 | .849 | .867 | .937 | .041 |
| NC4K | .893 | .864 | .881 | .945 | .028 |

## Completed Main Student

| Exp ID | Status | Config | Checkpoint | Notes |
| --- | --- | --- | --- | --- |
| light_b2_c64_e120_s42 | done | `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/config.yaml` | `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/epoch_120.pth` | PVTv2-B2 + C64, no KD; 120 epoch full train complete |
| light_b2_c64_e120_s42_prob_eval_v2 | pass | same run config via `--template_config` | above | probability-map CAMO/COD10K/NC4K eval complete; integrity check passed |

Light B2-C64 no-KD metrics:

| Dataset | Smeasure | wFmeasure | meanFm | meanEm | MAE |
| --- | ---: | ---: | ---: | ---: | ---: |
| CAMO | .862 | .818 | .843 | .918 | .051 |
| COD10K | .866 | .782 | .808 | .928 | .024 |
| NC4K | .886 | .840 | .862 | .933 | .033 |

Average delta vs historical ESCNet-B5 reference: S -0.009, wF -0.027, meanF -0.021, meanE -0.015, MAE +0.006. Final baseline deltas require clean ESCNet-B5 probability re-eval.

## Planned Runs

| Priority | Exp ID Template | Change | Expected Evidence |
| --- | --- | --- | --- |
| P0 | `light_b2_c64_e120_s42` | PVTv2-B2 + `inter_channel=64` | done；完整训练、profile、三数据集概率评测均已验收 |
| P0 | `kd_light_b2_c64_e120_s42` | 上一模型 + ESCNet-B5 output KD | batch 1/batch 4 smoke 通过；rerun 保存到 `epoch_5.pth` 后中断；workers=0 batch4 从 epoch 6 恢复后在 iter 100/252 rank0 SIGKILL；当前只保留 `epoch_5.pth` partial checkpoint，已准备四卡/双卡/单卡 batch2 recovery 配置 |
| P1 | `light_b2_c128_e120_s42` | PVTv2-B2 + 原 128 decoder | 主干替换消融 |
| P1 | `light_b5_c64_e60_s42` | PVTv2-B5 + 64 decoder | decoder 窄化消融 |
| P1 | `tiny_b0_c64_e60_s42` | PVTv2-B0 + 64 decoder | 极限压缩边界；当前 `/root/ESCNet/configs/pvt_v2_b0.yaml` 外部蒸馏分支又在运行，输出到 `/root/data-tmp/ESCNet/checkpoints/pvt_v2_b0`，先观察不纳入主表 |
| P2 | `light_b2_c64_dwfem_e60_s42` | 替换 FEM 为 depthwise FEM | 模块轻量化消融 |
| P2 | `light_b2_c64_int8_profile_s42` | 最佳 student 量化/部署 profile | 部署收益 |

## 风险优先级

| Change | Risk | Reason |
| --- | --- | --- |
| B5 -> B2 | Low | PVTv2-B2 输出通道仍为 `[64,128,320,512]`，对应 lateral `[512,320,128,64]` 不变 |
| C128 -> C64 | Low-Medium | 需要把 `inter_channel` 从硬编码改为 config，但结构兼容 |
| B5/B2 -> B0 | Medium | lateral channels 需改为 `[256,160,64,32]`，配置权重字段也需扩展 |
| Output KD | Medium | 训练工程多 teacher forward，但结构风险低；smoke 已证明链路可跑 |
| Online KD resource contention | High | B2-C64 KD full train 多次在 epoch 5/6 附近遭 SIGKILL；需独占 GPU 窗口、`num_workers=0`、逐 epoch checkpoint，必要时降 batch 或单/双卡继续 |
| Replace DeformConv/FEM | Medium-High | FPS/导出收益可能大，但边界质量可能下降 |
| Simplify MTA/SA | High | 直接触及 ESCNet 核心融合逻辑 |
| INT8/ONNX | High | DeformConv2d、Kornia、einops patch 注入可能阻碍导出 |

## 成功标准

主实验成功线：

- 参数量相对 ESCNet-B5 降低至少 40%。
- FLOPs/GMACs 显著下降；latency/FPS 只在空闲 GPU 同命令复测后作为定稿证据。
- COD10K/CAMO/NC4K 的 S-measure 平均下降控制在可解释范围内。
- MAE 不出现灾难性恶化。
- 至少一组可视化能展示边界/小目标优势或失败案例。

若最终精度差距较大，论文可以转为“轻量化代价分析”：重点解释压缩点、失败模式和蒸馏补偿效果。

## Tooling Status

| Tool | Status | Notes |
| --- | --- | --- |
| `profile_model.py` | pass | Baseline and Light B2-C64 profile complete; Light params -70.16%, GMACs -71.79% |
| `run_eval_suite.sh` | pass | CAMO smoke complete, but smoke metric not accepted for paper due protocol mismatch |
| `collect_metrics.py` | pass | Idempotent CSV parsing verified; writes protocol/repo_boundary/checkpoint/status metadata |
| `infer_prob.py` | pass | Probability-map inference verified on CAMO teacher checkpoint |
| `run_prob_eval_suite.sh` | pass | Probability-map evaluation wrapper; `bash -n` and py_compile checks passed |
| `kd_light_escnet_b2_c64` | partial pass | Config/py_compile/CPU teacher load/GPU batch1/GPU batch4 smoke pass; full train interrupted after `epoch_5.pth`; resume support added |
| `/root/ESCNet` B0 KD branch | running externally | PVTv2-B0 + teacher distillation is a high-risk external branch; epoch 20 COD10K intermediate eval degraded and no checkpoint exists, so do not treat as main result |

## Prepared KD Recovery Configs

| Config | Run Name | Devices | Batch | LR | Purpose |
| --- | --- | --- | ---: | ---: | --- |
| `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config_resume_epoch5_b2_workers0_4gpu.yaml` | `kd_light_b2_c64_e120_s42_recover_b2w0_4gpu` | `[0,1,2,3]` DDP | 2/GPU | 0.0000375 | first recovery after external B0 releases GPUs |
| `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config_resume_epoch5_b2_workers0_2gpu.yaml` | `kd_light_b2_c64_e120_s42_recover_b2w0_2gpu` | `[0,1]` DDP | 2/GPU | 0.00001875 | fallback if four-card DDP remains unstable |
| `/root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config_resume_epoch5_b2_workers0_1gpu.yaml` | `kd_light_b2_c64_e120_s42_recover_b2w0_1gpu` | `[0]` single process | 2 | 0.000009375 | last-resort continuation to avoid DDP rank cascade |

## Pretrained Weights

| Backbone | Path | Status |
| --- | --- | --- |
| PVTv2-B5 | `/root/data-tmp/weights/pvt_v2_b5_22k.pth` | available |
| PVTv2-B2 | `/root/data-tmp/weights/pvt_v2_b2.pth` | downloaded and smoke-verified |
| PVTv2-B0 | `/root/data-tmp/weights/pvt_v2_b0.pth` | available; B0 distillation branch currently running externally without checkpoint |

## Prepared Ablation Configs

| Exp ID | Config | Purpose |
| --- | --- | --- |
| `light_b2_c128_e120_s42` | `/root/data-tmp/workspace/02_experiments/configs/light_b2_c128.yaml` | isolate backbone compression with original decoder width |
| `light_b5_c64_e60_s42` | `/root/data-tmp/workspace/02_experiments/configs/light_b5_c64.yaml` | isolate decoder width reduction |

## Checkpoint Warning

`/root/ESCNet/checkpoints/escnet/epoch_120.pth` 是 2026-06-13 后续重训产物，不复现历史 CAMO baseline；teacher 和主 baseline 使用 `/root/data-tmp/epoch_120.pth`。
