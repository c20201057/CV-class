# Paper Baseline Boundary Audit 20260613

审查时间：2026-06-14 UTC  
审查方式：只读 `nl -ba`、`wc -l`、`grep -nE`；未运行 GPU 任务，未改动结果文件。  
审查范围：用户指定的论文草稿、表格、状态文档、clean baseline source boundary、baseline eval wrapper、`metrics_all.csv`、`profiles.csv`。

## 总体结论

当前文档已经显式承认 `/root/ESCNet` 是 dirty 工作树、teacher checkpoint 应固定为 `/root/data-tmp/epoch_120.pth`、KD/B0 不能入主结果、速度/FPS 需要复测。这些护栏是对的。

但论文草稿和主结果表仍存在一个核心证据链风险：**ESCNet-B5 三数据集主表数字来自历史 `/root/ESCNet/results_epoch120/result.txt`，只有 CAMO 完成了 `/root/data-tmp/epoch_120.pth` 的概率图复评，而 clean baseline snapshot 目前只完成了 CPU strict load 验证，并未完成三数据集统一概率图复评。** 摘要、主精度表和结论现在把 Light-vs-ESCNet 的数值差距写得过像“同一协议最终结果”，读者容易误解。

## 必须修正的问题（按严重程度）

### 1. 摘要和结论把混合证据写成了近似最终结论

- 文件/行号：
  - `/root/data-tmp/workspace/04_paper/drafts/paper_draft.md:7`
  - `/root/data-tmp/workspace/04_paper/drafts/paper_draft.md:205`
  - `/root/data-tmp/workspace/04_paper/drafts/paper_draft.md:207`
  - `/root/data-tmp/workspace/02_experiments/tables/metrics_all.csv:2`
  - `/root/data-tmp/workspace/02_experiments/tables/metrics_all.csv:5`
  - `/root/data-tmp/workspace/04_paper/drafts/evidence_index.md:35`
  - `/root/data-tmp/workspace/04_paper/drafts/evidence_index.md:36`

草稿摘要直接写“实验显示”Light 相比 ESCNet-B5 平均 S 下降约 0.009、MAE 增加约 0.006，并在结论中写“仅产生较小损失”。但这些差值依赖的 ESCNet-B5 三数据集行仍是历史结果：`metrics_all.csv:2-4` 来源为 `/root/ESCNet/results_epoch120/result.txt`；统一概率图复评目前只有 CAMO 一行 `teacher_escnet_b5_prob_e120`（`metrics_all.csv:5`）。`evidence_index.md:35-36` 也承认 COD10K/NC4K 复评待补，只是“主表可暂用历史三数据集结果”。

必须修正：摘要和结论不能把该差值写成 clean snapshot + 三数据集统一概率图协议下的最终结论。应明确为“相对已核验历史 ESCNet-B5 参考行”，或在 baseline 三数据集 clean 概率复评完成前把这些差值从摘要/结论中降级。

### 2. 主结果表模板自相矛盾：要求概率图主表，却把 full probability pending 的历史 baseline 放进主表

- 文件/行号：
  - `/root/data-tmp/workspace/04_paper/tables/main_results_template.md:7`
  - `/root/data-tmp/workspace/04_paper/tables/main_results_template.md:11`
  - `/root/data-tmp/workspace/04_paper/tables/main_results_template.md:12`
  - `/root/data-tmp/workspace/04_paper/drafts/paper_draft.md:154`
  - `/root/data-tmp/workspace/04_paper/drafts/paper_draft.md:156`
  - `/root/data-tmp/workspace/04_paper/drafts/paper_draft.md:161`

`main_results_template.md:7` 写明“主精度表必须使用概率图推理结果”，但 `main_results_template.md:11` 把 ESCNet-B5 历史行放入 Table 1，状态却是“full probability re-eval pending”；`main_results_template.md:12` 又单列一行 CAMO-only probability re-eval，COD10K/NC4K 均为 TBD。草稿 `paper_draft.md:154-158` 的主表则只展示历史 baseline 行，`paper_draft.md:161` 才在表后解释统一复评未完成。

必须修正：最终主表不能同时承担“正式概率图主表”和“历史 baseline 临时引用”两个角色。否则读者会默认 ESCNet-B5 三数据集行与 Light 行来自完全相同的概率图协议。

### 3. `metrics_all.csv` 的 source boundary 会让 dirty `/root/ESCNet` 历史结果被自动当成 clean baseline

- 文件/行号：
  - `/root/data-tmp/workspace/02_experiments/tables/metrics_all.csv:1`
  - `/root/data-tmp/workspace/02_experiments/tables/metrics_all.csv:2`
  - `/root/data-tmp/workspace/02_experiments/tables/metrics_all.csv:3`
  - `/root/data-tmp/workspace/02_experiments/tables/metrics_all.csv:4`
  - `/root/data-tmp/workspace/04_paper/tables/main_results_template.md:38`
  - `/root/data-tmp/workspace/04_paper/drafts/evidence_index.md:29`
  - `/root/data-tmp/workspace/04_paper/drafts/evidence_index.md:37`

`metrics_all.csv` 只有 `exp_id,dataset,method,metrics,source`，没有 `protocol`、`repo_boundary`、`checkpoint`、`status` 字段。历史 baseline 三行的 `source` 均为 `/root/ESCNet/results_epoch120/result.txt`，但 `evidence_index.md:37` 又说明 `/root/ESCNet` 当前 dirty，不能作为 clean baseline repo。`main_results_template.md:38` 要求 accuracy cells cite `metrics_all.csv`，这会让后续聚合脚本或填表者把 dirty 路径历史结果当成普通 baseline 行。

必须修正：历史三数据集行必须被机器可读地标记为 `historical_legacy_not_clean_snapshot` 或同等状态；clean baseline 概率复评完成后应以新的 `baseline_escnet_b5_clean_prob_e120` 行替换主表来源。

### 4. baseline 三种证据的边界在草稿中仍被串成了一条过强因果链

- 文件/行号：
  - `/root/data-tmp/workspace/04_paper/drafts/paper_draft.md:148`
  - `/root/data-tmp/workspace/04_paper/drafts/paper_draft.md:152`
  - `/root/data-tmp/workspace/04_paper/drafts/paper_draft.md:161`
  - `/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean/BASELINE_SOURCE.md:36`
  - `/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean/BASELINE_SOURCE.md:37`
  - `/root/data-tmp/workspace/04_paper/drafts/evidence_index.md:35`
  - `/root/data-tmp/workspace/04_paper/drafts/evidence_index.md:38`

草稿 `paper_draft.md:148` 把 clean snapshot strict load、历史目录时间戳、CAMO 概率图复评“高度一致”串联后，得出固定 `/root/data-tmp/epoch_120.pth` 为 baseline/teacher 的结论。问题是这三类证据证明的是不同事情：

- clean strict load 只证明 checkpoint 与 clean ESCNet-B5 结构匹配（`BASELINE_SOURCE.md:36-37`，`evidence_index.md:38`）。
- CAMO probability re-eval 只证明该 checkpoint 在 CAMO 上与历史 CAMO 接近（`evidence_index.md:35`）。
- 历史三数据集结果仍来自 `/root/ESCNet/results_epoch120/result.txt`，COD10K/NC4K 未完成 clean probability re-eval。

尤其 `paper_draft.md:161` 写“历史三数据集概率预测结果”，但提供的 `metrics_all.csv:2-4` 只给 `result.txt` 来源，没有协议字段证明它们是概率图协议结果。

必须修正：4.3 Baseline 核验应改成三段式边界说明，不能用“时间戳一致”替代 checkpoint-to-prediction provenance。

### 5. 速度/FPS 没有被写成正式最终结果，但仍有容易被引用成速度收益的措辞

- 文件/行号：
  - `/root/data-tmp/workspace/04_paper/drafts/paper_draft.md:15`
  - `/root/data-tmp/workspace/04_paper/drafts/paper_draft.md:17`
  - `/root/data-tmp/workspace/04_paper/drafts/paper_draft.md:165`
  - `/root/data-tmp/workspace/04_paper/tables/main_results_template.md:20`
  - `/root/data-tmp/workspace/04_paper/tables/main_results_template.md:23`
  - `/root/data-tmp/workspace/04_paper/tables/main_results_template.md:43`
  - `/root/data-tmp/workspace/02_experiments/tables/profiles.csv:2`
  - `/root/data-tmp/workspace/02_experiments/tables/profiles.csv:3`
  - `/root/data-tmp/workspace/02_experiments/tables/profiles.csv:5`

好消息：草稿 `paper_draft.md:165` 和模板 `main_results_template.md:43` 已明确 final speed pending。问题是草稿仍在引言写“更快”（`paper_draft.md:17`），并在效率节写“初始结构 profile 中 latency/FPS 呈现潜在速度收益”（`paper_draft.md:165`）。`profiles.csv` 同时存在三种相互冲突的速度信号：baseline 61.806 ms / 16.1797 FPS（`profiles.csv:2`），random-init Light 38.725 ms / 25.8231 FPS（`profiles.csv:3`），trained Light under contention 84.0076 ms / 11.9037 FPS（`profiles.csv:5`）。

必须修正：在空闲 GPU 同条件复测完成前，不应写“更快”或“潜在速度收益”。当前可写的是 params、GMACs、model size、peak memory 下降；latency/FPS 只能写“待同条件复测，现有数值不支持最终方向判断”。

### 6. B0 状态在论文草稿和状态文档之间不一致，容易被误读为已有可报告探索结果

- 文件/行号：
  - `/root/data-tmp/workspace/04_paper/drafts/paper_draft.md:193`
  - `/root/data-tmp/workspace/04_paper/drafts/paper_draft.md:195`
  - `/root/data-tmp/workspace/00_project/orchestrator_status.md:37`
  - `/root/data-tmp/workspace/00_project/orchestrator_status.md:48`
  - `/root/data-tmp/workspace/04_paper/drafts/evidence_index.md:72`
  - `/root/data-tmp/workspace/04_paper/drafts/evidence_index.md:74`
  - `/root/data-tmp/workspace/00_project/resume_handoff.md:66`
  - `/root/data-tmp/workspace/00_project/resume_handoff.md:70`

草稿 `paper_draft.md:195` 只写 B0 完成 epoch 10 并进入 eval，checkpoint 目录仍只有 `log.txt`；但 `orchestrator_status.md:37`、`evidence_index.md:72`、`resume_handoff.md:70` 又写它已继续到 epoch 18，并有 epoch 10 COD10K 中间 eval 数值。虽然所有文件都说没有可验收 checkpoint，但论文草稿状态已滞后，且“已完成 epoch 10 训练”容易被不仔细的读者误读成阶段性可用结果。

必须修正：论文正文最好删除 B0 段，或只保留一句“外部 B0/KD 分支运行中，无可验收 checkpoint，不进入本文结果”。不要在论文草稿中列中间 loss、预测目录或单数据集中间 eval。

### 7. KD 没有被误写成已完成主结果，但主精度表文本仍把 KD 放进“将比较”的主表范围

- 文件/行号：
  - `/root/data-tmp/workspace/04_paper/drafts/paper_draft.md:103`
  - `/root/data-tmp/workspace/04_paper/drafts/paper_draft.md:152`
  - `/root/data-tmp/workspace/04_paper/drafts/paper_draft.md:191`
  - `/root/data-tmp/workspace/04_paper/tables/main_results_template.md:14`
  - `/root/data-tmp/workspace/04_paper/tables/main_results_template.md:32`
  - `/root/data-tmp/workspace/04_paper/drafts/evidence_index.md:65`
  - `/root/data-tmp/workspace/04_paper/drafts/evidence_index.md:67`

KD 状态总体写得谨慎：`paper_draft.md:103` 和 `paper_draft.md:191` 都说明只有 smoke/epoch_5 partial，不能入结论；`evidence_index.md:67` 也明确不能写 KD 提升。风险在于 `paper_draft.md:152` 写“主精度表将在 ... 比较 ... Light-ESCNet B2-C64 + KD”，而模板 `main_results_template.md:14` 已放 KD 行。若该表被直接导出或截取，读者会看到一个主结果模型但全是 TBD/partial。

必须修正：KD 在完整 checkpoint + 三数据集概率图评估 + 完整性检查前，不应出现在主精度表主体；可放在“pending experiments”或状态段。

### 8. 填表 checklist 没把 clean baseline 三数据集复评列为最终主表前置条件

- 文件/行号：
  - `/root/data-tmp/workspace/04_paper/tables/result_fill_checklist.md:3`
  - `/root/data-tmp/workspace/04_paper/tables/result_fill_checklist.md:5`
  - `/root/data-tmp/workspace/04_paper/tables/result_fill_checklist.md:6`
  - `/root/data-tmp/workspace/04_paper/tables/result_fill_checklist.md:8`
  - `/root/data-tmp/workspace/04_paper/tables/result_fill_checklist.md:25`
  - `/root/data-tmp/workspace/04_paper/tables/result_fill_checklist.md:34`
  - `/root/data-tmp/workspace/04_paper/drafts/evidence_index.md:79`

`result_fill_checklist.md:3-8` 的“必须先完成”主要针对 Light 训练、Light 概率图评测、Light profile；clean ESCNet-B5 baseline 三数据集复评只在 `result_fill_checklist.md:25-34` 作为“GPU 空闲后统一复评”推荐命令出现。`evidence_index.md:79` 则把它列为定稿前必须补齐。两者不一致，会让填表者以为历史 baseline 行可以满足最终主表要求。

必须修正：把 clean baseline snapshot + `/root/data-tmp/epoch_120.pth` 的 CAMO/COD10K/NC4K 统一概率图复评移入 checklist 的“必须先完成”，除非主表显式标为 interim。

## 专项检查结论

### dirty `/root/ESCNet` 是否仍被当作 clean baseline

没有发现新的 clean baseline 运行命令直接使用 dirty `/root/ESCNet`。`start_baseline_prob_eval_clean.sh:25-28` 固定使用 `/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean` 和 `/root/data-tmp/epoch_120.pth`，且脚本说明 `start_baseline_prob_eval_clean.sh:9-11` 明确不是 dirty `/root/ESCNet`。

仍需修正的是历史结果残留：`metrics_all.csv:2-4` 和 `evidence_index.md:29` 仍以 `/root/ESCNet/results_epoch120/result.txt` 作为 ESCNet-B5 三数据集结果来源。它可以作为 historical verification evidence，但不能被自动聚合成 clean baseline 主表行。

### baseline 历史三数据集、CAMO 概率复评、clean snapshot strict load 边界

边界在状态文档里基本存在，但在论文草稿和表格里不够清楚。必须分开写：

1. 历史三数据集：`metrics_all.csv:2-4`，来源 `/root/ESCNet/results_epoch120/result.txt`，协议字段缺失。
2. CAMO 概率复评：`metrics_all.csv:5`，只覆盖 CAMO，exp_id 是 `teacher_escnet_b5_prob_e120`。
3. Clean snapshot strict load：`BASELINE_SOURCE.md:36-38`，证明结构/checkpoint load，无 missing/unexpected，不证明 COD10K/NC4K probability results。

当前 `paper_draft.md:148` 和 `paper_draft.md:161` 把这三者粘得太紧，是主要误导源。

### speed/FPS 是否仍被写成最终结论

没有看到表格或结论把 FPS/latency 写成最终定量收益；`main_results_template.md:23` 与 `main_results_template.md:43` 已标 pending，`paper_draft.md:165` 也说当前定稿结论只用非速度结构指标。

但仍应修正 `paper_draft.md:17` 的“更快”和 `paper_draft.md:165` 的“潜在速度收益”。在 `profiles.csv:5` 的 trained Light under contention 慢于 `profiles.csv:2` baseline 的情况下，这类措辞很容易被读者或后续作者误引。

### KD/B0 是否被误写成已完成主结果

KD 没有被写成已完成主结果；`paper_draft.md:103`、`paper_draft.md:191`、`evidence_index.md:67` 的限制明确。需要做的是不要让 KD 的 TBD 行出现在主精度表主体。

B0 没有被写成主结果，但状态有滞后和中间指标暴露风险。建议从论文正文删除 B0 细节，只保留“高风险探索，未验收，不入表”。

## 具体修订建议（最多 8 条）

1. 改写 `paper_draft.md:7` 和 `paper_draft.md:205-207`：把“实验显示/结果表明 Light 相比 ESCNet-B5 ...”改为“相对已核验历史 ESCNet-B5 参考行，Light 显示 ...；最终差值以 clean snapshot 三数据集概率图复评为准”，或暂时移除平均差值。
2. 重构 Table 1：最终主表只保留统一概率图协议完成的行；历史 ESCNet-B5 放到 footnote 或 verification table。不要在同一主表里同时放 historical ESCNet-B5 和 CAMO-only prob re-eval ESCNet-B5。
3. 给 `metrics_all.csv` 或聚合表增加机器可读边界字段：`protocol=historical|prob_map`、`repo_boundary=dirty_history|clean_snapshot|light_snapshot`、`checkpoint=/root/data-tmp/epoch_120.pth`、`status=final|pending|verification_only`。
4. 改写 `paper_draft.md:148`：分三条写 strict load、CAMO prob re-eval、historical results；删除“时间戳一致”作为强证据的表达，删除或降级“历史三数据集概率预测结果”。
5. 在所有最终表格和正文中暂时移除 Light latency/FPS 数字与“更快/潜在速度收益”措辞；保留 Params、GMACs、model size、peak memory。速度只写“待空闲 GPU 同命令复测”。
6. KD 在完整训练和三数据集概率评估前，不放入主精度表主体。保留在方法或状态段，并标为 `implemented, smoke-tested, not evaluated`。
7. B0 从论文正文结果段移除；若必须保留，只写“一条外部高风险分支仍无可验收 checkpoint，不进入本文主表/结论”，不要列 epoch、loss、单数据集中间 eval 或预测目录。
8. 更新 `result_fill_checklist.md` 的“必须先完成”：加入 clean ESCNet-B5 baseline 三数据集概率图复评、baseline run integrity、以及“若报告 speed/FPS，则 baseline/Light/KD 必须空闲 GPU 同条件复测”。
