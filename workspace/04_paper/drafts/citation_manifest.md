# Citation Manifest

更新时间：2026-06-14T01:35:39Z

用途：把论文参考文献、已有调研材料和正文主张边界绑定起来。后续 agent 改相关工作、摘要、结论或参考文献时，应先检查本文件，避免把趋势材料写成已完成贡献，或把已有工作误写成本文首创。

## 使用准则

- Paper use：说明该文献在正文中支撑哪类论述。
- Evidence source：说明本地哪份调研材料记录了该引用。
- Boundary：说明正文不能越过的主张边界。
- Inline citation：两份论文稿必须在正文中显式引用 18 条核心文献，不能只把文献放在参考文献列表里。
- Do not claim：本文不主张 COD SOTA、首个轻量 COD、首个边界感知轻量 COD、首个 KD-COD、实时部署或已完成 SAM/开放词汇/视频 COD。
- Pending evidence：固定基线相关结论必须等待完整同协议复评，KD 相关结论必须等待完整训练与三数据集评测，speed/FPS 相关结论必须等待空闲 GPU 同条件复测；当前文献只支撑动机和边界，不替代实验结果。

## Reference Map

| Ref | Core work | Paper use | Evidence source | Boundary |
| --- | --- | --- | --- | --- |
| R01 / [1] | Anabranch Network for Camouflaged Object Segmentation / CAMO | 任务与 CAMO 数据集来源，支撑引言和相关工作 2.1。 | `verified_literature.md`, `citation_notes.md` | 只说明 CAMO 来源；不要把 CAMO 写成本文训练集外的新数据贡献。 |
| R02 / [2] | Camouflaged Object Detection / COD10K / SINet | COD10K 基准、经典搜索-识别路线和 COD 任务背景。 | `verified_literature.md`, `web_search_notes.md` | 不把 COD10K 项目页或 SINet 结果写成本文复现结果。 |
| R03 / [3] | Simultaneously Localize, Segment and Rank the Camouflaged Objects / NC4K / Rank | NC4K 泛化测试来源，支撑三数据集评测设置。 | `verified_literature.md`, `citation_notes.md` | NC4K 只能写作测试/泛化评估集，不能写成训练集。 |
| R04 / [4] | PFNet / Distraction Mining | 经典 COD 干扰挖掘路线，用于相关工作背景。 | `verified_literature.md`, `citation_notes.md` | 不与本文做未复现的性能优劣比较。 |
| R05 / [5] | FDCOD / Detecting Camouflaged Object in Frequency Domain | 频域信息对伪装目标分割有帮助，用于边界/频域增强背景。 | `verified_literature.md`, `literature_gap_update_2026.md` | 本文当前没有频域模块；只能作动机和相关工作。 |
| R06 / [6] | DGNet / Deep Gradient Learning for Efficient Camouflaged Object Detection | 高效 COD 与梯度监督代表，支撑轻量化趋势。 | `verified_literature.md`, `web_search_notes.md` | 不写本文优于 DGNet/DGNet-S，除非后续统一复现或严格引用官方协议。 |
| R07 / [7] | PVT v2 / Pyramid Vision Transformer | 解释 PVTv2-B5 到 PVTv2-B2 的同族主干压缩和多尺度接口。 | `verified_literature.md`, `web_search_notes.md` | 不声称本文提出新的 Transformer backbone 或 PVT 压缩理论。 |
| R08 / [8] | ESCNet / Edge-Semantic Collaborative Network | 本文实验基底、教师模型和保留的边缘-语义协同归纳偏置。 | `verified_literature.md`, `literature_gap_update_2026.md` | 本文贡献不是重新提出 ESCNet；固定基线结论等待完整同协议复评。 |
| R09 / [9] | CamoFormer / Masked Separable Attention | 近期强 Transformer/attention COD 背景，说明高精度模型复杂化趋势。 | `verified_literature.md`, `literature_gap_update_2026.md` | 不把本文写成优于 CamoFormer 或 COD SOTA。 |
| R10 / [10] | HGINet / Hierarchical Graph Interaction Transformer | 动态 token 聚类和图交互代表，支撑强模型趋势。 | `verified_literature.md`, `literature_gap_update_2026.md` | 不声称本文提出 token clustering 或 graph interaction。 |
| R11 / [11] | FINet / Frequency Injection Network for Lightweight COD | 轻量 COD + 频域补偿代表，说明轻量化不是简单缩小模型。 | `verified_literature.md`, `literature_gap_update_2026.md` | 本文不是首个轻量 COD，也没有频域注入模块。 |
| R12 / [12] | CSFIN / Cross-Stage Feature Interaction | 跨阶段特征交互式轻量网络代表。 | `verified_literature.md`, `literature_gap_update_2026.md` | 不写本文优于 CSFIN；只用于界定轻量 COD 现有路线。 |
| R13 / [13] | BPNet / Boundary Perception Network | 轻量边界感知 COD 代表，限制本文 novelty 边界。 | `verified_literature.md`, `literature_gap_update_2026.md` | 本文不能主张首个边界感知轻量 COD。 |
| R14 / [14] | LiteCOD / Local-Global Features and Multi-Scale Fusion | 2025 轻量 COD 旁证，说明 local-global 和多尺度融合趋势。 | `verified_literature.md`, `literature_gap_update_2026.md` | 不在无统一协议下比较本文与 LiteCOD 的性能优劣。 |
| R15 / [15] | Distilling the Knowledge in a Neural Network / Hinton KD | 知识蒸馏基础，支撑 teacher-student 输出约束设计。 | `verified_literature.md`, `citation_notes.md` | 只支撑方法动机；不能替代 KD 完整训练结果。 |
| R16 / [16] | CamoTeacher / Dual-Rotation Consistency | teacher-student 一致性在半监督 COD 的代表。 | `verified_literature.md`, `literature_gap_update_2026.md` | 不把 CamoTeacher 的半监督目标等同于本文模型压缩 KD。 |
| R17 / [17] | SAM-COD / SAM-guided Weakly-Supervised COD | COD 中 prompt-adaptive KD 的相关工作，限制“首次 KD-COD”表述。 | `verified_literature.md`, `literature_gap_update_2026.md` | 本文不是 SAM 或弱监督方法，不能写成 SAM-COD 复现或扩展。 |
| R18 / [18] | CFF-KDNet / Cross-Scale Feature Fusion with KD | 近期 KD-COD 边界文献。 | `verified_literature.md`, `literature_gap_update_2026.md` | 本文不能主张首次将 KD 用于 COD；KD 效果必须等待完整训练与三数据集评测。 |

## Paper Use By Section

- 引言：R01、R02、R03 支撑任务和基准；R08、R09、R10 支撑强模型复杂化；R11、R12、R13、R14 支撑轻量化需求。
- 相关工作 2.1：R01、R02、R03、R04、R05、R06 组织经典 COD、数据集、干扰挖掘、频域和高效模型。
- 相关工作 2.2：R11、R12、R13、R14 组织轻量 COD，并明确本文不是首个轻量 COD。
- 相关工作 2.3：R15、R16、R17、R18 组织 KD 和 teacher-student COD 边界。
- 方法：R07、R08、R15 支撑 PVTv2 同族压缩、ESCNet 基底和 KD 设计。
- 实验：R01、R02、R03 支撑 CAMO/COD10K/NC4K 数据集描述；R08 只能作为基线和教师模型来源。
- 结论：只能总结已经完成的 Light-B2-C64 no-KD 结果；KD、固定基线和速度结论需要等待对应证据项完成。

## Claim Boundaries

- Safe claim：本文研究强 ESCNet 基底的可控轻量化改造，保留边缘-语义协同结构，并通过 PVTv2-B2 与 C64 解码器降低复杂度。
- Safe claim：当前已完成 Light-ESCNet B2-C64 no-KD 的三数据集概率图评测和结构效率 profile。
- Safe claim：当前与 ESCNet-B5 的差值只能写作历史参考口径，直到固定源码概率图基线完成。
- Unsafe claim：本文是首个轻量 COD、首个边界感知轻量 COD、首个 KD-COD、COD SOTA、实时部署完成。
- Unsafe claim：KD 有效提升、速度/FPS 最终加速、B0/MobileMamba 是主结果，除非对应证据项完整通过并进入指标表、复杂度表、完整性检查和发布审计。

## Local Cross-Checks

- Literature notes：`/root/data-tmp/workspace/01_literature/verified_literature.md`
- Gap/boundary note：`/root/data-tmp/workspace/01_literature/literature_gap_update_2026.md`
- Citation placement note：`/root/data-tmp/workspace/01_literature/citation_notes.md`
- Web-source note：`/root/data-tmp/workspace/01_literature/web_search_notes.md`
- Paper drafts：`/root/data-tmp/workspace/04_paper/drafts/paper_interim_submission.md`, `/root/data-tmp/workspace/04_paper/drafts/paper_draft.md`
- Audit：`python /root/data-tmp/workspace/04_paper/scripts/audit_literature_citations.py`；该审计同时检查参考文献列表和正文 inline citation 覆盖。
