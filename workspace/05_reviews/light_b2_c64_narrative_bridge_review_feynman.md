# Light B2-C64 Narrative Bridge Review - Feynman

日期：2026-06-13

范围：

- `/root/data-tmp/workspace/04_paper/drafts/paper_interim_submission.md`
- `/root/data-tmp/workspace/04_paper/drafts/method_light_b2_c64.md`

任务：只读审稿式检查，聚焦“文献/课题动机 -> Light-B2-C64 方法设计 -> 当前实验结论”之间的论文叙事断点。审稿准则是不偷懒、不因风险而保守，但必须遵守当前证据边界：ESCNet-B5 clean baseline pending、KD pending、B0 observation only。

## 高优先级意见

1. `paper_interim_submission.md` 的方法动机需要更正面回答“为什么是 PVTv2-B2 + C64，而不是 B1/B3/C96/C32”。建议增加设计选择准则：接口兼容、压缩幅度足够、保留四级特征、解码端同步降宽，强调 B2-C64 是主力 student，B0/KD/消融是后续验证分支。

2. `paper_interim_submission.md` 2.3 轻量化相关工作需要更明确地区分本文与 FINet、CSFIN、BPNet、LiteCOD 等工作的研究问题。已有工作多从零设计轻量网络或引入新模块，本文则控制同一强基底，回答“保留边缘-语义协同后，主干和解码宽度压缩能换来怎样的精度-效率折中”。

3. `paper_interim_submission.md` 3.2 和 `method_light_b2_c64.md` 中“为什么保留边缘分支”的证据闭环需要更清楚。保留边缘分支不是因为当前已经证明它最优，而是为了避免轻量化时首先破坏 COD 的关键归纳偏置；CAMO wF/MAE 下降说明即使保留边缘，容量压缩仍会伤害细节，因此边界消融和 KD 是必要后续。

4. `paper_interim_submission.md` 4.4 中“比直接删除边界路径更适合”存在消融越界风险。建议改为“保留边界协同是一条更合理的主线假设；是否优于删除边界路径仍需边界分支消融确认”。

5. 论文正文中“gate、回填、工程状态”等项目管理词偏重，会稀释论文感。建议保留 clean baseline pending、KD pending、speed pending 的事实，但用“证据边界、限制、待补实验”等论文式表述替代内部流程词。

6. 4.5 效率结果需要一句更强的 punchline：以平均 S-measure 下降 0.009、MAE 增加 0.006 的代价，换取约 70% 的参数量、计算量、模型大小和峰值显存下降。注意继续标注为相对 historical ESCNet-B5 reference。

7. 主文 4.8 中 B0 observation 过细，容易分散主线。建议正文只保留“B0 极限压缩仅有 COD10K 中间观察，尚未通过 checkpoint 验证和三数据集评估，不进入结论”，详细 epoch 走势放实验日志。

8. `method_light_b2_c64.md` 中“这更适合课程论文”不宜迁移到正式论文或答辩稿。建议改为正式表述：同族替换减少接口适配变量，使实验更能聚焦于主干容量和解码宽度对精度-效率折中的影响。

## 主控采纳情况

- 已在 `paper_interim_submission.md` 3.2 增加 B2-C64 的控制变量论证：PVTv2 同族缩放保持四级接口，C64 同步压缩 AETP/FEM/MTA/mask head。
- 已将 4.4 的边界路径比较改为“主线假设”，并明确需要边界分支消融确认。
- 已将 4.5 增加“精度代价 vs 结构收益”的量化句式。
- 已压缩 4.8 中 B0 的主文描述，去掉易过期 iter 和多 epoch 细节。
- 已将 `method_light_b2_c64.md` 中“课程论文”表述替换为正式研究表述。
- 已保留 KD、clean baseline、speed 的证据边界，没有升级为结论。
