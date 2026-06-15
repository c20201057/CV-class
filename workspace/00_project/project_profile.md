# 项目画像

## 任务与目标

课题：面向伪装目标分割的轻量化模型研究。

给定 RGB 图像 `I`，模型输出伪装目标概率掩码 `P=f(I)`。论文目标不是追逐绝对 SOTA，而是在 ESCNet 强基线基础上证明轻量化方案的精度-效率折中价值。

## 开题报告约束

开题报告明确提出四条技术线：

- 轻量编码器：MobileNetV3、GhostNet、ShuffleNetV2 或轻量 PVT。
- 轻量多尺度融合：减少融合层数，使用 depthwise separable conv、Ghost module、轻量 ASPP 或频域线索。
- 边界辅助分支：用浅层特征预测边界，并回注解码器。
- 知识蒸馏与量化：用强模型教师约束学生输出，训练后尝试 INT8 或剪枝。

报告指定核心数据集为 COD10K、CAMO、NC4K；R2C7K、CamoVid60K、MoCA-Mask 只作为扩展方向。

## ESCNet 基底现状

仓库：`/root/ESCNet`

数据：`/root/data-tmp/COD`

数据规模：

| Split | Image | GT |
| --- | ---: | ---: |
| Train | 4040 | 4040 |
| CAMO-Test | 250 | 250 |
| COD10K-Test | 2026 | 2026 |
| NC4K | 4121 | 4121 |

当前模型：

- Backbone: `pvt_v2_b5`
- Input size: 416
- Lateral channels: `[512, 320, 128, 64]`
- Decoder hidden channel: hard-coded `inter_channel=128`
- Loss: edge Dice + multi-level structure loss

参数量拆分：

| Part | Params |
| --- | ---: |
| Encoder | 81.44M |
| ASA lateral convs | 0.13M |
| AETP edge branch | 3.47M |
| Decoder | 14.86M |
| Total | 99.90M |

轻量变体的只读估算：

| Variant | Approx Params | Note |
| --- | ---: | --- |
| PVTv2-B5 + C128 | 99.9M | 当前 ESCNet |
| PVTv2-B2 + C128 | 43.3M | 最低风险主干替换 |
| PVTv2-B2 + C64 | 29.8M | 推荐主实验 student |
| PVTv2-B0 + C128 | 21.8M | decoder/AETP 开始成为主体 |
| PVTv2-B0 + C64 | 8.34M | 极限轻量候选 |

已有历史 teacher/baseline 指标：

| Dataset | Smeasure | wFmeasure | meanFm | meanEm | MAE |
| --- | ---: | ---: | ---: | ---: | ---: |
| COD10K | .873 | .808 | .827 | .942 | .020 |
| CAMO | .875 | .849 | .867 | .937 | .041 |
| NC4K | .893 | .864 | .881 | .945 | .028 |

训练成本：单卡 Tesla V100-SXM2 16GB，120 epoch 约 64,398 秒，即约 17.9 小时。

关键 checkpoint 判断：

- 历史强 baseline/teacher checkpoint 应固定为 `/root/data-tmp/epoch_120.pth`，时间为 2026-06-11，和历史预测目录 `preds_epoch120_*` 时间匹配。
- `/root/ESCNet/checkpoints/escnet/epoch_120.pth` 现在经 symlink 指向 `/root/data-tmp/workspace/02_experiments/runs/legacy_root_ESCNet_checkpoints_escnet_20260613/epoch_120.pth`；它是 2026-06-13 重新训练保存的 checkpoint，CAMO 重新推理显著低于历史 baseline，不应作为 teacher 或历史 baseline 使用。
- 使用 `/root/data-tmp/epoch_120.pth` 进行 CAMO 概率图重推理得到 S=.881、wF=.842、meanF=.864、meanE=.933、MAE=.043，和历史 CAMO baseline 高度一致。

## 已知工程风险

- `/root/ESCNet` 工作树已有未提交改动，不应被实验 agent 随意还原。
- 根分区当前仍显示满载，新 checkpoint、预测、日志和临时文件必须写入 `/root/data-tmp/workspace` 或 `/root/data-tmp/tmp`，不要继续写 `/root/ESCNet`。
- `test.py` 当前保存的是 `sigmoid >= 0.5` 后的二值预测，可能影响 MAE 和曲线类指标。最终论文应统一说明，最好补充保存概率图的评估版本。
- 历史 baseline 与当前 checkpoint 文件存在时间线差异，所有 agent 必须使用 `/root/data-tmp/epoch_120.pth` 作为 teacher。
- `eval.py` 以追加方式写 `result.txt`，多次运行会混入旧结果。workflow 中必须每个 run 独立保存结果。
- `config.py` 目前只声明 `pvt_v2_b2/b4/b5` 权重字段，若使用 `pvt_v2_b0/b1` 或 torchvision 主干，需要同步改配置模型。
- `train.py` 中 autocast 使用 `dtype=torch.float32`，实际不会带来 fp16 混合精度收益。
- 原始 run 脚本只有一个 `preds/results` 公共目录，不适合多实验并发。
- DeformConv2d、Kornia Laplacian 和 `einops.rearrange` patch 注入会增加 FLOPs 统计、ONNX 导出和量化难度。
- `resume` 字段存在但训练脚本未实际加载 checkpoint/optimizer/scheduler。
- `eval.py --check_integrity type=bool` 不可靠，且 `evaluate_model()` 依赖模块全局 `config`。
