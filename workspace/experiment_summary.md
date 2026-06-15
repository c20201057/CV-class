# 实验汇总

生成时间：2026-06-15

说明：

- 每个数据集下的四个小分数项为 `S / wF / meanE / MAE`。
- `推理时间`优先采用同协议 idle profile 的单张 416x416 输入 latency；没有独立 profile 的实验，补充 probability inference 在 CAMO/COD10K/NC4K 上的整套生成耗时。
- `no-edge-supervision` 仍在训练中，尚无最终三数据集评测分数；Git 快照时最新日志约为 epoch 119/120。

| 实验名 | 实验简述 | 训练时间 | 推理时间 | CAMO S | CAMO wF | CAMO meanE | CAMO MAE | COD10K S | COD10K wF | COD10K meanE | COD10K MAE | NC4K S | NC4K wF | NC4K meanE | NC4K MAE |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline / ESCNet-B5 clean | clean snapshot + `/root/data-tmp/epoch_120.pth`，三数据集 probability re-eval | 未重训，使用既有 teacher checkpoint | 73.01 ms/img；CAMO/COD10K/NC4K 生成耗时 00:15/01:54/03:16 | .881 | .842 | .933 | .043 | .877 | .802 | .938 | .021 | .897 | .857 | .942 | .029 |
| Light-B2-C64 no-KD | 当前 accepted 主学生模型，PVTv2-B2 + C64，120 epoch | 3:00:36 | 34.31 ms/img；CAMO/COD10K/NC4K 00:09/01:16/03:12 | .862 | .818 | .918 | .051 | .866 | .782 | .928 | .024 | .886 | .840 | .933 | .033 |
| KD Light-B2-C64 | Online KD，teacher=ESCNet-B5，最终从恢复链路完成到 epoch120 | 有效完成段 e20-e120：4:24:22；前置恢复/失败排障不并入稳定训练时间 | 34.84 ms/img；CAMO/COD10K/NC4K 00:10/01:17/01:58 | .863 | .818 | .920 | .050 | .864 | .782 | .929 | .024 | .885 | .838 | .932 | .033 |
| Light-B2-C64 no-edge-guidance | 结构消融：关闭 decoder edge guidance，保留 edge head/loss | 4:24:18 | 未做独立 profile；CAMO/COD10K/NC4K 00:11/01:19/02:02 | .846 | .786 | .899 | .058 | .847 | .749 | .917 | .028 | .873 | .815 | .921 | .038 |
| Light-B2-C64 no-edge-supervision | 结构消融进行中：保留 decoder edge guidance，但 `edge_loss_weight=0` | 进行中，当前约 e119/120 | 未评测 | 待测 | 待测 | 待测 | 待测 | 待测 | 待测 | 待测 | 待测 | 待测 | 待测 | 待测 | 待测 |
| PVTv2-B0 external branch | 极轻 B0 分支，dirty-tree observation only，用户已要求不进主线 | 完整 wall-clock 未可靠记录 | 未形成受控推理时间 | - | - | - | - | .8004 | .6862 | .8878 | .0350 | - | - | - | - |

## 当前可用于论文的边界

- 可作为主线结果：`baseline / ESCNet-B5 clean`、`Light-B2-C64 no-KD`。
- 可作为 KD 负结果/成本分析：`KD Light-B2-C64`。当前结果相对 no-KD 基本持平或略低，不能写成 KD 提升。
- 可作为结构消融候选：`Light-B2-C64 no-edge-guidance`。结果低于 accepted Light-B2-C64，可支持“移除 decoder edge guidance 会退化”的候选结论。
- 暂不可写入结论：`Light-B2-C64 no-edge-supervision`。需要 epoch120 checkpoint、三数据集 probability eval、profile 和 integrity/audit。
- 仅路线搜索观察：`PVTv2-B0 external branch`。该分支不能进入主表、摘要或结论。
