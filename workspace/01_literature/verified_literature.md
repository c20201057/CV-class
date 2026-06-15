# 已核验文献清单

核验日期：2026-06-13。正文写作优先使用一手来源；公开材料不足的 2026 工作只作趋势或未来工作，不作为核心论据。

## 核心基准与经典 COD

| Paper | Year | Use |
| --- | ---: | --- |
| [Anabranch Network for Camouflaged Object Segmentation](https://dl.acm.org/doi/10.1016/j.cviu.2019.04.006) | 2019 | CAMO 数据集来源，正文重点 |
| [Camouflaged Object Detection](https://openaccess.thecvf.com/content_CVPR_2020/papers/Fan_Camouflaged_Object_Detection_CVPR_2020_paper.pdf) | 2020 | COD10K 与 SINet，正文重点 |
| [Simultaneously Localize, Segment and Rank the Camouflaged Objects](https://openaccess.thecvf.com/content/CVPR2021/papers/Lv_Simultaneously_Localize_Segment_and_Rank_the_Camouflaged_Objects_CVPR_2021_paper.pdf) | 2021 | NC4K 泛化测试，正文引用 |
| [Camouflaged Object Segmentation with Distraction Mining](https://openaccess.thecvf.com/content/CVPR2021/papers/Mei_Camouflaged_Object_Segmentation_With_Distraction_Mining_CVPR_2021_paper.pdf) | 2021 | PFNet，经典对比/相关工作 |
| [Deep Gradient Learning for Efficient Camouflaged Object Detection](https://link.springer.com/article/10.1007/s11633-022-1365-9) | 2023 | DGNet/DGNet-S，高效 COD 相关工作 |

## 轻量化、频域与边界

| Paper | Year | Use |
| --- | ---: | --- |
| [PVT v2: Improved Baselines with Pyramid Vision Transformer](https://arxiv.org/abs/2106.13797) | 2021 | PVTv2 backbone 来源，方法/实现细节引用 |
| [Detecting Camouflaged Object in Frequency Domain](https://openaccess.thecvf.com/content/CVPR2022/html/Zhong_Detecting_Camouflaged_Object_in_Frequency_Domain_CVPR_2022_paper.html) | 2022 | FDCOD，频域 COD 核心文献 |
| [FINet: Frequency Injection Network for Lightweight Camouflaged Object Detection](https://github.com/CRRCOO/FINet) | 2024 | 轻量+频域，正文重点 |
| [CamoFormer: Masked Separable Attention for Camouflaged Object Detection](https://pubmed.ncbi.nlm.nih.gov/39102328/) | 2024 | Transformer/attention 强 COD，背景引用；DOI: 10.1109/TPAMI.2024.3438565 |
| [HGINet: Hierarchical Graph Interaction Transformer With Dynamic Token Clustering for Camouflaged Object Detection](https://arxiv.org/abs/2408.15020) | 2024 | Transformer/token 聚类强模型趋势，相关工作 |
| [ESCNet: Edge-Semantic Collaborative Network for Camouflaged Object Detection](https://openaccess.thecvf.com/content/ICCV2025/html/Ye_ESCNetEdge-Semantic_Collaborative_Network_for_Camouflaged_Object_Detection_ICCV_2025_paper.html) | 2025 | 本项目基底，方法核心 |
| [CSFIN: A lightweight network for camouflaged object detection via cross-stage feature interaction](https://www.researchgate.net/publication/387913970_CSFIN_A_lightweight_network_for_camouflaged_object_detection_via_cross-stage_feature_interaction) | 2025 | 跨阶段轻量融合，相关工作；DOI: 10.1016/j.eswa.2025.126451 |
| [Vision-Inspired Boundary Perception Network for Lightweight Camouflaged Object Detection](https://github.com/h0t-zer0/BPNet) | 2025 | 轻量边界感知，相关工作；代码与论文入口 |
| [LiteCOD: Lightweight Camouflaged Object Detection via Holistic Understanding of Local-Global Features and Multi-Scale Fusion](https://www.mdpi.com/2673-2688/6/9/197) | 2025 | 轻量 COD 旁证 |
| [Ulcod-net: an ultra-lightweight camouflage object detection framework with gated multi-level feature fusion and dual-constraint refinement](https://link.springer.com/article/10.1007/s40747-025-02201-3) | 2025/2026 | 超轻量 COD 趋势；不作为核心性能对比 |
| FMLNet: A lightweight camouflage object detection network based on RGB-frequency domain mutual learning | 2026 | 频域互学习，可简短引用 |
| Frequency domain-based edge sensing for camouflaged object detection | 2026 | 频域边界趋势，可简短引用 |

## 蒸馏与模型压缩基础

| Paper | Year | Use |
| --- | ---: | --- |
| [Distilling the Knowledge in a Neural Network](https://arxiv.org/abs/1503.02531) | 2015 | teacher-student KD 基础引用 |
| [CamoTeacher: Dual-Rotation Consistency Learning for Semi-Supervised Camouflaged Object Detection](https://arxiv.org/abs/2408.08050) | 2024 | teacher-student 一致性在半监督 COD 中的代表；不要等同于模型压缩 KD |
| [SAM-COD: SAM-guided Unified Framework for Weakly-Supervised Camouflaged Object Detection](https://arxiv.org/abs/2408.10760) | 2024 | 弱监督 COD 中的 prompt-adaptive KD；限制本文“首次 KD-COD”主张 |
| [CFF-KDNet: Cross-scale feature fusion network with knowledge distillation for camouflaged object detection](https://github.com/caibo297/CFF-KDNet) | 2026 | KD-COD 近期工作；DOI: 10.1016/j.eswa.2025.130209，谨慎引用 |

## 扩展方向

| Paper/Dataset | Year | Use |
| --- | ---: | --- |
| [Referring Camouflaged Object Detection / R2C7K](https://github.com/zhangxuying1004/refcod) | 2025 | 开放/参考式 COD，未来工作 |
| [CamoVid60K](https://camovid60k.hkustvgd.com/) | 2026 | 视频伪装理解，未来工作 |

## 写作使用建议

正文相关工作不要堆满 2026 新论文。建议按三段写：

1. 数据集与经典 COD：CAMO、COD10K/SINet、NC4K、PFNet。
2. 边界与频域增强：FDCOD、ESCNet、FINet、FDESNet。
3. 轻量化 COD：DGNet-S、CSFIN、BPNet、LiteCOD，并引出本项目的 Light-ESCNet。

补充核验：Schrodinger 的 2024-2026 文献缺口已由主控抽查。FINet、BPNet、CamoFormer、ESCNet、HGINet、CamoTeacher、SAM-COD、CSFIN、CFF-KDNet 和 Ulcod-net 均能找到公开论文/代码/出版社/索引来源；CFF-KDNet 建议按 ESWA 2026 volume 299、DOI 2025 写法处理，Ulcod-net 使用 Springer 页面的完整标题。

补充写作卡片见：`/root/data-tmp/workspace/01_literature/citation_notes.md`。
