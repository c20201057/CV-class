# Paper Evidence Audit

审查时间：2026-06-13T16:44:03Z  
审查 agent：Lagrange  
审查对象：`04_paper/drafts/paper_draft.md`、主结果表、聚合表、metrics/profile 表与文献边界。

## 主要发现

1. Baseline 主表与“统一概率图协议”表述需要收紧。ESCNet-B5 三数据集当前仍主要来自历史 baseline，只有 CAMO 已用 `/root/data-tmp/epoch_120.pth` 做概率图复评。
2. 速度/FPS 结论容易越界。Light clean FPS 来自 same-architecture preliminary profile，trained-checkpoint latency/FPS 受并发污染，不能写成最终速度收益。
3. KD 方法描述中的“或 KL”与当前实现不完全一致。当前代码只实现 output-level MSE，KL 只能作为后续替代方案。
4. 消融章节当前是计划，不是已有结果，标题和文字需要明确“待补项”。
5. 可视化定性结论需要绑定 CAMO per-image MAE case selection，避免泛化到所有数据集。
6. 参考文献不能保留聚合占位条目，FINet、CSFIN、BPNet、LiteCOD、CFF-KDNet 等需要分别列出。
7. 训练集表述需与实际 `/root/data-tmp/COD/Train` 目录对齐。

## 主控处理

- 已将摘要和实验协议改为：Light-ESCNet 主结果使用概率图评测，ESCNet-B5 baseline 当前由历史三数据集结果和 CAMO 概率图复核共同支撑。
- 已将速度/FPS 改为 pending idle re-test；正文当前只把 params、GMACs、model size、peak memory 作为稳定效率结论。
- 已将 KD 损失描述改为当前实现采用 output-level MSE，KL 仅作为后续替代。
- 已将 4.6 标题改为“消融实验计划与待补项”，并明确未完成分支不作为结果结论。
- 已将可视化结论限定为“已选 CAMO per-image MAE 样本中”的初步观察，并引用 case selection 文件。
- 已将参考文献从占位替换为已核验条目。
- 已将训练集写法改为项目整理后的 `/root/data-tmp/COD/Train`，共 4040 张图像。

## 当前结论

审稿意见已处理。当前论文草稿更适合继续作为可交稿骨架：可靠结论集中在 Light-B2-C64 no-KD 完整训练、三数据集概率图评测和结构复杂度下降；KD、B0、最终 FPS、完整消融仍保持待验证状态。
