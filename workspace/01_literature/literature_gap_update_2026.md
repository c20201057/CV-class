# 2024-2026 文献缺口与论证边界更新

核验日期：2026-06-13  
课题：面向伪装目标分割的轻量化模型研究  
实验基底：ESCNet / PVTv2-B5 teacher / Light-ESCNet B2-C64 student

本文的安全定位应是：在 ESCNet 强基线基础上，研究一种可复现、低风险、部署友好的结构轻量化路线，即保留边缘-语义协同归纳偏置，同时压缩 PVTv2 主干规模与解码器隐藏通道，并用统一概率图评测和效率 profiling 证明精度-效率折中。不要把本文写成 COD 绝对 SOTA、首个轻量 COD、首个 KD-COD 或首个边界感知轻量模型。

## 一、2024-2026 可引用论文清单

### A. 与本文最直接相关的轻量化 COD

1. **FINet: Frequency Injection Network for Lightweight Camouflaged Object Detection**  
   年份/来源：IEEE Signal Processing Letters, 2024, 31:526-530  
   作者：Weiyun Liang, Jiesheng Wu, Yanfeng Wu, Xinyue Mu, Jing Xu  
   链接：[GitHub/论文信息](https://github.com/CRRCOO/FINet)，[dblp](https://dblp.org/rec/journals/spl/LiangWWMX24)，DOI: `10.1109/LSP.2024.3356416`  
   与本文关系：FINet 是近年明确以 lightweight COD 为标题的代表工作，强调频域注入对轻量网络的补偿。本文没有实现频域模块，因此只能用它说明“轻量 COD 正在从单纯缩小模型转向引入补偿线索”，不能暗示本文提出频域创新。

2. **Efficient Camouflaged Object Detection via Progressive Refinement Network**  
   年份/来源：IEEE Signal Processing Letters, 2024, 31:231-235  
   作者：Dongdong Zhang, Chunping Wang, Qiang Fu  
   链接：[dblp](https://dblp.uni-trier.de/pid/17/1352-17.html)，[ResearchGate 信息页](https://www.researchgate.net/publication/376974235_Efficient_Camouflaged_Object_Detection_via_Progressive_Refinement_Network)，DOI: `10.1109/LSP.2023.3348390`  
   与本文关系：可作为“efficient COD”背景引用，说明高效 COD 不只关注参数量，还常借助渐进式细化恢复困难区域。本文路线不同：不是新设计 progressive refinement，而是在 ESCNet 架构内做主干和通道压缩。

3. **CSFIN: A lightweight network for camouflaged object detection via cross-stage feature interaction**  
   年份/来源：Expert Systems with Applications, 2025, 269:126451  
   作者：Minghong Li, Yuqian Zhao, Fan Zhang, Gui Gui, Biao Luo, Chunhua Yang, Weihua Gui, Kan Chang  
   链接：[ResearchGate 信息页](https://www.researchgate.net/publication/387913970_CSFIN_A_lightweight_network_for_camouflaged_object_detection_via_cross-stage_feature_interaction)，[中南大学作者页](https://faculty.csu.edu.cn/zhaoyuqian/zh_CN/zdylm/199455/list/index.htm)，DOI: `10.1016/j.eswa.2025.126451`  
   与本文关系：CSFIN 代表跨阶段特征交互式轻量融合。本文可以把它放在轻量 COD 段落，强调已有工作通过专门融合模块提升轻量模型，而本文聚焦“强 ESCNet 基底的可控轻量化改造”。

4. **Vision-Inspired Boundary Perception Network for Lightweight Camouflaged Object Detection**  
   年份/来源：IEEE Signal Processing Letters, 2025, 32:1176-1180  
   作者：Chunyuan Chen, Weiyun Liang, Donglin Wang, Bin Wang, Jing Xu  
   链接：[GitHub/论文信息](https://github.com/h0t-zer0/BPNet)，[ResearchGate 信息页](https://www.researchgate.net/publication/389744698_Vision-Inspired_Boundary_Perception_Network_for_Lightweight_Camouflaged_Object_Detection)，DOI: `10.1109/LSP.2025.3549698`  
   与本文关系：BPNet 与本文的“轻量 + 边界感知”主题接近，是 related work 中必须承认的边界。本文不能主张首个边界感知轻量 COD；可以主张在 ESCNet 边缘-语义协同基底上进行结构压缩和效率评测。

5. **LiteCOD: Lightweight Camouflaged Object Detection via Holistic Understanding of Local-Global Features and Multi-Scale Fusion**  
   年份/来源：AI, 2025, 6(9):197  
   作者：Abbas Khan, Hayat Ullah, Arslan Munir 等  
   链接：[MDPI 正文页](https://www.mdpi.com/2673-2688/6/9/197)，[MDPI citation notes](https://www.mdpi.com/2673-2688/6/9/197/notes)，DOI: `10.3390/ai6090197`  
   与本文关系：可作为 2025 年轻量 COD 的补充引用，主题是 local-global features 与 multi-scale fusion。除非引用其官方表格并说明评测协议差异，否则不要比较“本文优于 LiteCOD”。

6. **Ulcod-net: an ultra-lightweight camouflage object detection network based on feature reuse and fusion**  
   年份/来源：Complex & Intelligent Systems, 2025/2026 在线信息显示为近期文章  
   链接：[Springer 页面](https://link.springer.com/article/10.1007/s40747-025-02201-3)  
   与本文关系：可谨慎作为“ultra-lightweight COD 进一步成为趋势”的旁证。由于当前只检索到出版社摘要和参考文献信息，建议不放入核心论证，最多在 related work 末句作为近期超轻量化方向。

### B. 2024-2025 COD 主流模型、Transformer 与强基线趋势

7. **CamoFormer: Masked Separable Attention for Camouflaged Object Detection**  
   年份/来源：IEEE TPAMI, 2024, 46(12):10362-10374  
   作者：Bowen Yin, Xuying Zhang, Deng-Ping Fan, Shaohui Jiao, Ming-Ming Cheng, Luc Van Gool, Qibin Hou  
   链接：[PubMed](https://pubmed.ncbi.nlm.nih.gov/39102328/)，[PDF](https://mftp.mmcheng.net/Papers/24PAMI-CamoFormer.pdf)，[Deng-Ping Fan 主页](https://dengpingfan.github.io/)，DOI: `10.1109/TPAMI.2024.3438565`  
   与本文关系：CamoFormer 代表强 Transformer/attention COD 路线，说明高性能 COD 仍依赖更强上下文建模。本文不与其争 SOTA，而是用作“强模型往往复杂，轻量化有必要”的背景。

8. **Hierarchical Graph Interaction Transformer With Dynamic Token Clustering for Camouflaged Object Detection / HGINet**  
   年份/来源：IEEE TIP, 2024, 33:5936-5948；arXiv:2408.15020  
   作者：Siyuan Yao, Hao Sun, Tian-Zhu Xiang, Xiao Wang, Xiaochun Cao  
   链接：[arXiv](https://arxiv.org/abs/2408.15020)，[GitHub](https://github.com/garyson1204/hginet)，[出版信息](https://nchr.elsevierpure.com/en/publications/hierarchical-graph-interaction-transformer-with-dynamic-token-clu/)，DOI: `10.1109/TIP.2024.3475219`  
   与本文关系：HGINet 用动态 token 聚类和层级图交互强化伪装区域判别，适合放在 Transformer COD 段落。它也提示本文的 PVTv2-B2/B5 压缩并非 Transformer 结构创新，而是工程可控的 backbone scale-down。

9. **Decoupling and Integration Network for Camouflaged Object Detection / DINet**  
   年份/来源：IEEE Transactions on Multimedia, 2024, 26:7114-7129  
   作者：Xiaofei Zhou, Zhicong Wu, Runmin Cong  
   链接：[ACM/IEEE DOI页](https://dl.acm.org/doi/abs/10.1109/TMM.2024.3360710)，[researchr](https://researchr.org/publication/ZhouWC24-0)，DOI: `10.1109/TMM.2024.3360710`  
   与本文关系：DINet 可作为近期 COD 模块设计的代表，说明解耦与融合仍是主流问题。本文不提出新的 decoupling/integration 范式。

10. **ESCNet: Edge-Semantic Collaborative Network for Camouflaged Object Detection**  
    年份/来源：ICCV 2025  
    链接：[CVF OpenAccess](https://openaccess.thecvf.com/content/ICCV2025/html/Ye_ESCNetEdge-Semantic_Collaborative_Network_for_Camouflaged_Object_Detection_ICCV_2025_paper.html)  
    与本文关系：本文实验基底和 teacher 来源。必须明确：本文保留 ESCNet 的边缘-语义协同思想，贡献不在重新发明 ESCNet，而在对 ESCNet 做轻量主干和窄通道解码器改造、统一评测与效率分析。

### C. 知识蒸馏、弱/半监督与 foundation model 相关 COD

11. **CamoTeacher: Dual-Rotation Consistency Learning for Semi-Supervised Camouflaged Object Detection**  
    年份/来源：ECCV 2024  
    作者：Xunfa Lai, Zhiyu Yang, Jie Hu, Shengchuan Zhang, Liujuan Cao, Guannan Jiang, Zhiyu Wang, Songan Zhang, Rongrong Ji  
    链接：[arXiv](https://arxiv.org/abs/2408.08050)，[ECCV PDF](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/06215.pdf)，[Springer/ACM DOI页](https://dl.acm.org/doi/10.1007/978-3-031-72995-9_25)，DOI: `10.1007/978-3-031-72995-9_25`  
    与本文关系：CamoTeacher 是 teacher-student 框架在半监督 COD 中的代表，但目标是减少标注依赖和处理伪标签噪声，不是模型压缩。本文的 KD 是 teacher-student 输出蒸馏用于压缩后的精度补偿，应避免把两者混为同一贡献。

12. **SAM-COD: SAM-guided Unified Framework for Weakly-Supervised Camouflaged Object Detection**  
    年份/来源：ECCV 2024  
    作者：Huafeng Chen, Pengxu Wei, Guangqian Guo, Shan Gao  
    链接：[arXiv](https://arxiv.org/abs/2408.10760)，[ECCV PDF](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/05187.pdf)，[GitHub](https://github.com/2231122/SAM-COD)，DOI: `10.1007/978-3-031-72761-0_18`  
    与本文关系：SAM-COD 使用 prompt-adaptive knowledge distillation 处理弱监督 COD。可用来说明 KD 在 COD 场景已有应用，但本文不能主张首次将 KD 引入 COD；只能主张在 ESCNet teacher 到轻量 student 的输出级蒸馏尝试。

13. **Improving SAM for Camouflaged Object Detection via Dual Stream Adapters / SAM-DSA**  
    年份/来源：ICCV 2025  
    作者：Jiaming Liu, Linghe Kong, Guihai Chen  
    链接：[arXiv](https://arxiv.org/abs/2503.06042)，[ICCV PDF](https://openaccess.thecvf.com/content/ICCV2025/papers/Liu_Improving_SAM_for_Camouflaged_Object_Detection_via_Dual_Stream_Adapters_ICCV_2025_paper.pdf)  
    与本文关系：SAM-DSA 说明 foundation model 适配 COD 时也会引入双向知识蒸馏/跨模态蒸馏。本文不是 SAM 或 RGB-D 工作，可在 related work 中轻触，不应占据主线。

14. **CFF-KDNet: Cross-Scale Feature Fusion Network with Knowledge Distillation for Camouflaged Object Detection**  
    年份/来源：Expert Systems with Applications, 2025, 299:130209  
    作者：Bo Cai, Houjie Li, Yanping Yang, Jin Yan  
    链接：[ResearchGate 信息页](https://www.researchgate.net/publication/397226783_CFF-KDNet_Cross-Scale_Feature_Fusion_Network_with_Knowledge_Distillation_for_Camouflaged_Object_Detection)，DOI: `10.1016/j.eswa.2025.130209`  
    与本文关系：标题即为 KD-COD，直接限制本文的 novelty 边界。由于当前检索到的主要是一页元数据，建议只在“已有 KD-COD 相关探索”中谨慎引用，不以其具体性能作为论据。

15. **Knowledge Rectification for Camouflaged Object Detection / KRNet**  
    年份/来源：arXiv, 2025  
    链接：[arXiv HTML](https://arxiv.org/html/2503.22180v1)  
    与本文关系：使用 Leader-Follower 与 knowledge distillation 纠正低质量数据学习到的知识。适合作为“KD 在 COD 中也被用于数据质量/知识纠偏”的趋势引用；不作为核心已发表论据。

### D. 开放词汇、视频与 2026 趋势，建议只放未来工作

16. **Open-Vocabulary Camouflaged Object Segmentation / OVCoser, OVCamo**  
    年份/来源：ECCV 2024  
    作者：Youwei Pang, Xiaoqi Zhao, Jiaming Zuo, Lihe Zhang, Huchuan Lu  
    链接：[arXiv](https://arxiv.org/abs/2311.11241)，[ECCV PDF](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/06409.pdf)，[项目页](https://lartpang.github.io/docs/ovcamo.html)，[GitHub](https://github.com/lartpang/OVCamo)  
    与本文关系：说明 COD 正在扩展到开放词汇和类别语义理解。本文仍是闭集/静态图像 COD，不应引入开放词汇承诺；可放未来工作。

17. **Referring Camouflaged Object Detection / R2C7K**  
    年份/来源：TPAMI 2025，项目页/代码  
    链接：[GitHub](https://github.com/zhangxuying1004/refcod)，[awesome 列表条目](https://github.com/ChunmingHe/awesome-concealed-object-segmentation)  
    与本文关系：指代表达 COD 与本文的静态二值分割不同。只建议在未来工作提及，不进入主实验承诺。

18. **CamSAM2: Segment Anything Accurately in Camouflaged Videos**  
    年份/来源：NeurIPS 2025 poster，OpenReview 页面 2025-09-18，2026-04-21 更新  
    链接：[OpenReview](https://openreview.net/forum?id=WbpzGpVWVx)  
    与本文关系：视频伪装目标分割和 SAM2 适配方向。本文不做视频，最多在未来工作说明模型轻量化后可进一步探索视频部署。

## 二、与本课题的论证关系

1. **轻量化 COD 已经是明确方向**：FINet、CSFIN、BPNet、LiteCOD、Ulcod-net 等工作表明，近年已有多条轻量化路线，包括频域注入、跨阶段交互、边界感知、local-global 与多尺度融合。本文不能把“轻量 COD”本身作为首创。

2. **边界感知不是本文独有**：BPNet、ESCNet 以及许多边界/边缘引导 COD 工作已经证明边界线索重要。本文的合理表述是“保留 ESCNet 中已验证有效的边缘-语义协同机制，并研究其在轻量化 student 中的保真程度”。

3. **Transformer COD 的强模型趋势仍在继续**：CamoFormer、HGINet、DINet、ESCNet 等工作强调 attention、token 交互、解耦融合和边缘语义协同。本文可以据此说明大模型/复杂模块带来精度，但也带来部署成本，从而引出压缩动机。

4. **PVTv2 压缩路线有稳定工程依据**：PVTv2 本身是面向密集预测的层级 Transformer，具有多尺度输出、线性复杂度注意力、重叠 patch embedding 和卷积 FFN。本文从 PVTv2-B5 降到 PVTv2-B2，属于同一 backbone family 内的 scale-down，接口稳定、变量可控，适合作为毕业论文主实验。

5. **KD 可作为补偿策略，但当前不能写成结论**：CamoTeacher、SAM-COD、SAM-DSA、CFF-KDNet、KRNet 表明 teacher-student/KD 在 COD 中已有应用。本文若 KD full train 未完成，只能写作“设计/尝试/待验证的精度补偿分支”；只有三数据集概率图评测完成后，才能写 KD 提升幅度。

## 三、本论文可以安全主张的 novelty 边界

可以主张：

- 本文以 ESCNet 为强基线，构建了面向 COD 的 Light-ESCNet B2-C64 轻量化变体。
- 本文保留 ESCNet 的边缘-语义协同结构，同时将 PVTv2-B5 主干替换为 PVTv2-B2，并将解码器隐藏通道从 128 降到 64，从结构层面显著降低参数量、GMACs、模型大小和峰值显存。
- 本文在 CAMO、COD10K、NC4K 上使用统一概率图评测协议，并配套效率 profiling，系统分析了 ESCNet 轻量化后的精度-效率折中。
- 在当前已有 no-KD 结果下，可以主张 Light-ESCNet B2-C64 在约 70% 复杂度降低下保持接近 ESCNet-B5 的 S-measure，代价主要体现在 wF 和 MAE，尤其 CAMO 较明显。
- 若 KD 完成并通过统一评测，可以进一步主张“输出级 teacher-student 蒸馏可作为轻量 ESCNet 的精度补偿策略”，但要给出具体提升数字。

建议措辞：

> 不同于从零设计新的轻量 COD 网络，本文关注强 COD 模型的可控轻量化改造：在保留 ESCNet 边缘-语义协同机制的基础上，通过同族 PVTv2 主干缩放和解码器通道压缩获得更低复杂度，并以统一概率图评测验证其精度-效率折中。

## 四、不能主张的东西

不能主张：

- 不能说本文是首个轻量 COD 方法。FINet、CSFIN、BPNet、LiteCOD 等已经明确是轻量 COD。
- 不能说本文首次引入边界感知或边缘监督到 COD。BPNet、ESCNet、FindNet、ERRNet、BgCOD 等已有大量相关工作。
- 不能说本文首次将知识蒸馏用于 COD。SAM-COD、CamoTeacher、SAM-DSA、CFF-KDNet、KRNet 等已涉及 teacher-student 或 KD。
- 不能说本文提出了新的 Transformer backbone 或 PVT 压缩理论。本文使用的是 PVTv2 family 内的规模替换。
- 不能在没有统一复现或严格引用官方表格的情况下说本文优于 FINet、CSFIN、BPNet、LiteCOD、CamoFormer、HGINet 等方法。
- 不能把 NC4K 写成训练集。它在本文中应作为测试/泛化评估集。
- 不能把 KD 效果写进摘要或结论，除非 KD checkpoint、概率图推理、三数据集评估和完整性检查都已经完成。
- 不能宣称本文实现了频域模块、量化、剪枝、SAM、开放词汇或视频 COD，除非后续确实完成实验。

## 五、建议写进 Related Work 的中文段落草稿

### 2.1 伪装目标分割与强模型发展

近年来，伪装目标分割从早期数据集和经典网络逐渐发展到更复杂的上下文建模与区域细化方法。CAMO、COD10K 和 NC4K 等基准推动了该任务的标准化评测，SINet、PFNet、FDCOD、DGNet 等方法分别从搜索定位、干扰挖掘、频域增强和梯度学习角度提升伪装区域的可分性。进入 Transformer 阶段后，CamoFormer 通过 masked separable attention 强化伪装目标与背景的区分，HGINet 利用动态 token 聚类和层级图交互挖掘难辨别区域，DINet 从解耦与融合角度提升目标区域表征，ESCNet 则进一步强调边缘线索与语义信息的协同。上述方法说明，COD 精度提升通常依赖更强的上下文建模、多尺度交互和边界恢复能力，但也带来了更高的参数量和计算开销。

### 2.2 轻量化伪装目标分割

面向资源受限部署，轻量化 COD 近年受到更多关注。FINet 将频域线索注入轻量网络，以补偿 RGB 外观相似带来的判别不足；CSFIN 通过跨阶段特征交互提升轻量特征融合能力；BPNet 从视觉启发的边界感知出发，在轻量设置下强化弱边界恢复；LiteCOD 则结合局部-全局理解和多尺度融合探索轻量分割框架。这些工作表明，COD 轻量化并非简单减少通道或替换小主干，还需要保留对弱边界、纹理干扰和多尺度目标的建模能力。与上述从零设计轻量网络的路线不同，本文选择 ESCNet 作为强基底，研究在保留边缘-语义协同结构的前提下，利用同族 PVTv2 主干缩放和解码器通道压缩获得更可控的精度-效率折中。

### 2.3 知识蒸馏与模型压缩

知识蒸馏通过教师模型向学生模型传递软预测或中间表征，是模型压缩中的常用策略。在 COD 领域，CamoTeacher 利用 teacher-student 一致性学习缓解半监督伪标签噪声，SAM-COD 在弱监督场景中引入 prompt-adaptive knowledge distillation，SAM-DSA 通过双向知识蒸馏增强 SAM 在 RGB-D 伪装目标检测中的适配能力，CFF-KDNet 和 KRNet 等近期工作也显示了知识迁移在 COD 中的应用潜力。本文中的蒸馏目标不同于半监督或 foundation model 适配，而是以 ESCNet-B5 作为 teacher，对轻量化后的 Light-ESCNet student 进行输出级概率图约束，用于补偿主干和解码通道压缩带来的表达能力下降。

### 2.4 PVTv2 与轻量 Transformer 主干

PVTv2 通过层级特征输出、重叠 patch embedding、卷积前馈网络和线性复杂度注意力，为检测与分割等密集预测任务提供了通用 Transformer backbone。ESCNet 采用较大的 PVTv2-B5 作为编码器，能够提供较强的全局语义建模能力，但也使 encoder 成为主要参数和计算来源。本文采用 PVTv2-B2 替换 PVTv2-B5，属于同一主干家族内的规模压缩，能够保持多尺度接口一致，降低工程风险，并有利于将精度变化归因于主干规模和解码宽度的减少。

## 六、摘要和结论中的推荐边界表述

摘要可写：

> 本文不追求伪装目标分割绝对 SOTA，而是以 ESCNet 为强基线研究可部署的轻量化改造。通过同族 PVTv2 主干缩放和解码器通道压缩，Light-ESCNet 在显著降低复杂度的同时保持接近的分割性能，体现了边缘-语义协同结构在轻量 student 中的保留价值。

结论可写：

> 实验结果表明，对 ESCNet 进行结构级轻量化是一条有效且可复现的精度-效率折中路线。当前结果支持“轻量主干 + 窄解码器 + 保留边界协同”的结论；知识蒸馏是否能进一步弥合精度差距，需要以完整训练和同协议评测结果为准。

## 七、参考链接汇总

- FINet: https://github.com/CRRCOO/FINet
- BPNet: https://github.com/h0t-zer0/BPNet
- CSFIN: https://www.researchgate.net/publication/387913970_CSFIN_A_lightweight_network_for_camouflaged_object_detection_via_cross-stage_feature_interaction
- LiteCOD: https://www.mdpi.com/2673-2688/6/9/197
- Ulcod-net: https://link.springer.com/article/10.1007/s40747-025-02201-3
- CamoFormer: https://pubmed.ncbi.nlm.nih.gov/39102328/
- HGINet: https://arxiv.org/abs/2408.15020
- DINet: https://dl.acm.org/doi/abs/10.1109/TMM.2024.3360710
- ESCNet: https://openaccess.thecvf.com/content/ICCV2025/html/Ye_ESCNetEdge-Semantic_Collaborative_Network_for_Camouflaged_Object_Detection_ICCV_2025_paper.html
- CamoTeacher: https://arxiv.org/abs/2408.08050
- SAM-COD: https://arxiv.org/abs/2408.10760
- SAM-DSA: https://arxiv.org/abs/2503.06042
- CFF-KDNet: https://www.researchgate.net/publication/397226783_CFF-KDNet_Cross-Scale_Feature_Fusion_Network_with_Knowledge_Distillation_for_Camouflaged_Object_Detection
- KRNet: https://arxiv.org/html/2503.22180v1
- OVCOS/OVCamo: https://arxiv.org/abs/2311.11241
- CamSAM2: https://openreview.net/forum?id=WbpzGpVWVx
- PVTv2: https://arxiv.org/abs/2106.13797
- PVT 官方实现: https://github.com/whai362/PVT
- EfficientViT for dense prediction: https://openaccess.thecvf.com/content/ICCV2023/papers/Cai_EfficientViT_Lightweight_Multi-Scale_Attention_for_High-Resolution_Dense_Prediction_ICCV_2023_paper.pdf
- TinyViT distillation: https://arxiv.org/abs/2207.10666
- EfficientFormerV2: https://openaccess.thecvf.com/content/ICCV2023/papers/Li_Rethinking_Vision_Transformers_for_MobileNet_Size_and_Speed_ICCV_2023_paper.pdf
