# Web Search Notes

检索日期：2026-06-13

用途：为论文相关工作、方法动机和路线判断保留可追溯网络来源。正文优先引用论文官网、CVF OpenAccess、出版社页面、官方 GitHub 或 DOI 页面。

## 核心基准

| Topic | Source | Notes |
| --- | --- | --- |
| COD10K / SINet | https://openaccess.thecvf.com/content_CVPR_2020/papers/Fan_Camouflaged_Object_Detection_CVPR_2020_paper.pdf | CVPR 2020，COD10K 与 SINet 的主要来源。 |
| COD10K project page | https://mmcheng.net/cod/ | 项目页说明 COD10K 覆盖 10,000 张图、78 类，并提供 SINet 背景。 |
| NC4K / Rank-Net | https://openaccess.thecvf.com/content/CVPR2021/papers/Lv_Simultaneously_Localize_Segment_and_Rank_the_Camouflaged_Objects_CVPR_2021_paper.pdf | CVPR 2021，NC4K 与 ranking COD 任务来源。 |
| NC4K code/data entry | https://github.com/JingZhang617/COD-Rank-Localize-and-Segment | 官方 repo 入口，辅助确认 NC4K。 |

## 边界、频域与强基线

| Topic | Source | Notes |
| --- | --- | --- |
| PVTv2 | https://arxiv.org/abs/2106.13797 | Backbone 来源。PVTv2 引入 overlapping patch embedding、convolutional FFN、linear complexity attention。 |
| ESCNet | https://openaccess.thecvf.com/content/ICCV2025/html/Ye_ESCNetEdge-Semantic_Collaborative_Network_for_Camouflaged_Object_Detection_ICCV_2025_paper.html | ICCV 2025 OpenAccess。强调 AETP、DSFA、MFMM 与 edge-texture collaboration。 |
| ESCNet official repo | https://github.com/suy9/ESCNet | 本项目实验基底的上游官方实现。 |
| FDCOD | https://openaccess.thecvf.com/content/CVPR2022/papers/Zhong_Detecting_Camouflaged_Object_in_Frequency_Domain_CVPR_2022_paper.pdf | CVPR 2022，频域 COD 代表工作。 |

## 轻量化 COD

| Topic | Source | Notes |
| --- | --- | --- |
| DGNet / DGNet-S | https://link.springer.com/article/10.1007/s11633-022-1365-9 | Machine Intelligence Research 2023，高效 COD 与 gradient supervision。 |
| DGNet arXiv | https://arxiv.org/abs/2205.12853 | 摘要提到 DGNet-S 的实时与低参数优势，可用于轻量化动机。 |
| FINet | https://github.com/CRRCOO/FINet | IEEE SPL 2024 官方 repo，Frequency Injection Network for Lightweight COD，DOI: 10.1109/LSP.2024.3356416。 |
| BPNet | https://github.com/h0t-zer0/BPNet | IEEE SPL 2025 官方 repo，Vision-Inspired Boundary Perception Network for Lightweight COD，DOI: 10.1109/LSP.2025.3549698。 |
| LiteCOD | https://www.mdpi.com/2673-2688/6/9/197 | AI 2025，轻量 COD local-global + multi-scale fusion。 |
| LiteCOD citation page | https://www.mdpi.com/2673-2688/6/9/197/notes | DOI: 10.3390/ai6090197。 |

## 模型压缩与 KD

| Topic | Source | Notes |
| --- | --- | --- |
| Knowledge Distillation | https://arxiv.org/abs/1503.02531 | Hinton/Vinyals/Dean 2015，teacher-student 压缩基础引用。 |

## 路线推断

1. ESCNet 的 edge-texture collaboration 与本项目开题报告中的边界辅助分支高度契合，因此可作为 teacher 和结构基底。
2. DGNet-S、FINet、BPNet、LiteCOD 说明轻量 COD 的主流补偿机制集中在 gradient/boundary、frequency、local-global multi-scale 三类。
3. 对 `/root/ESCNet` 最低风险的第一步不是引入全新 MobileNet/GhostNet，而是使用已经支持的 PVTv2-B2，并将 decoder hidden channel 从 128 降为 64。
4. 频域或 depthwise FEM 可作为 P2 高收益风险分支，不应阻塞 B2-C64 与 KD 主实验。
