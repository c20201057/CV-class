# Submission Protocol Checklist

更新时间：2026-06-14T06:15:24Z / 2026-06-14 14:15:24 CST

本文档是论文定稿前的最后验收清单。它的作用不是替代实验，而是防止
historical reference、verification-only 结果和 final paper evidence 混在一起。

## 1. Artifact Boundary

必须满足：

- 论文主线代码、run、表格、图和草稿均位于 `/root/data-tmp/workspace`。
- `/root/ESCNet` 只作为外部探索运行目录或源头参考，不作为 clean baseline。
- clean baseline 固定为 `/root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean`。
- ESCNet-B5 teacher checkpoint 固定为 `/root/data-tmp/epoch_120.pth`。
- `/root/ESCNet/checkpoints/escnet/epoch_120.pth` 不得进入 teacher、baseline 或主表证据链。
- `/root/ESCNet/checkpoints/escnet` 当前为 symlink，指向 data-tmp legacy checkpoint 归档；该路径只用于追溯 2026-06-13 后续重训产物。
- 根分区仍显示满载时，所有新大产物和 `TMPDIR` 必须放在 `/root/data-tmp`。
- agent 调度入口固定为 `/root/data-tmp/workspace/03_agent_tasks/task_board.md`，task board 路径和队列状态必须通过 `task_board_consistency_audit_latest.md`。
- 论文交付包入口固定为 `/root/data-tmp/workspace/04_paper/drafts/paper_delivery_manifest.md`，其路径、核心图表、内部证据、允许主张和 withheld claims 必须通过 `paper_delivery_manifest_audit_latest.md`。

验收命令：

```bash
git -C /root/ESCNet status --short
test -f /root/data-tmp/workspace/02_experiments/code/baseline_escnet_clean/BASELINE_SOURCE.md
test -f /root/data-tmp/epoch_120.pth
python /root/data-tmp/workspace/02_experiments/scripts/audit_paper_evidence.py
python /root/data-tmp/workspace/04_paper/scripts/audit_claim_text.py
python /root/data-tmp/workspace/04_paper/scripts/audit_paper_delivery_manifest.py
python /root/data-tmp/workspace/03_agent_tasks/audit_task_board_consistency.py
bash /root/data-tmp/workspace/02_experiments/scripts/run_release_audits.sh
```

## 2. Main Accuracy Table Entry Rule

一行模型结果进入主精度表前，必须同时满足：

- 三个数据集 CAMO、COD10K、NC4K 均有结果。
- 预测图数量与 GT 数量一致。
- 预测图是概率灰度图，不是二值化 smoke 输出。
- `check_run_integrity.py` 通过。
- `metrics_all.csv` 中写明 `protocol`, `repo_boundary`, `checkpoint`, `status`。
- `status` 不得是 `historical_reference_not_clean_prob_final`、`verification_only_camo` 或其他 pending 状态。
- final 主表只允许 `status` 属于 `final_main_light`、`clean_prob_re_eval_complete`、`final_main_kd`。
- final 主表不得包含 `repo_boundary=dirty_history_result` 或 `repo_boundary=legacy_repo_camo_verification`。
- final 主表 checkpoint 必须位于 `/root/data-tmp/workspace`，或是固定 teacher `/root/data-tmp/epoch_120.pth`。

禁止拼接：

- `teacher_escnet_b5_prob_e120` 只有 CAMO，不能和 historical COD10K/NC4K 拼成一行 final baseline。
- B0 的 intermediate epoch metrics 不能进入主表、平均差值、摘要或结论。
- MobileMamba-T2 的 intermediate epoch metrics 不能进入主表、平均差值、摘要或结论。
- KD 的 `epoch_1.pth` 到 `epoch_5.pth`、resume failed logs 和 partial metrics 只能写作工程状态，不能作为 KD 主表来源。

当前可以作为 final 主表证据的行：

- `light_b2_c64_e120_s42_prob_eval_v2`，status=`final_main_light`。

当前只能作为参考或验证的行：

- `baseline_escnet_b5_416_e120`，status=`historical_reference_not_clean_prob_final`。
- `teacher_escnet_b5_prob_e120`，status=`verification_only_camo`。
- B0/MobileMamba 只有在候选验收完成后才能使用 `status=external_dirty_tree_observation_candidate`，且仍不得进入 final 主表状态集合。

最新自动审计：

- `audit_paper_evidence.py` 于 2026-06-13T17:54 左右运行，状态为 pass。
- baseline historical rows 和 teacher CAMO verification row 被正确列为 reference notes。
- `run_release_audits.sh` 已加入最终验收入口；它会同时运行 evidence audit、claim audit 和当前 final Light run integrity check。
- `audit_paper_delivery_manifest.py` 已加入最终验收入口；它会检查 `paper_delivery_manifest.md` 和 `paper_delivery_manifest_audit_latest.md` 对当前交付包边界的覆盖。

## 3. Efficiency Table Entry Rule

结构效率可以报告：

- Params(M)
- GMACs
- Model Size(MB)
- Peak Mem(MB)

latency/FPS 只有在以下条件满足时才能写成最终结论：

- GPU 空闲，无并发训练或评测。
- baseline、Light、KD 使用同一 `profile_model.py`。
- 输入尺寸、batch size、warmup、repeat、device 一致。
- profile json 和聚合表均保留。

若条件不满足，论文只能写结构效率，不写最终速度提升。

## 4. Claim Level Rule

定稿允许：

- Light-ESCNet B2-C64 完成 120 epoch 训练。
- Light-ESCNet B2-C64 完成三数据集概率图评测。
- Light-ESCNet B2-C64 相对 Gate 1 clean ESCNet-B5 probability baseline 的同协议差值。
- 结构复杂度约 70% 降低。
- KD/B0/MobileMamba 当前作为工程状态、补偿路线或失败风险。

定稿禁止，除非对应 gate 通过：

- 将历史 ESCNet-B5 reference 写作当前同协议 baseline。
- 写 KD 已提升精度或缩小差距。
- 写 latency/FPS 的最终速度提升。
- 将 B0 写入主表或主结论，除非 Gate 4A 通过。
- 将 MobileMamba 写入主表或主结论，除非 Gate 4B 通过。
- 写 SOTA、首次提出 KD-COD、实时部署或边缘端部署。

## 5. Gate Update Actions

Gate 1 clean baseline 已完成：

1. clean baseline 三数据集结果已写入 `metrics_all.csv`。
2. 运行或复跑 `aggregate_results.py`。
3. 保持 `main_results_template.md`、`aggregated_results.md`、`paper_draft.md` 与 clean baseline 口径一致。
4. 摘要和结论里的 baseline 差值使用 clean probability baseline。
5. 重新跑 `claim_evidence_audit.md` 的主张检查。

Gate 2 KD 完成后：

1. 验证完整 checkpoint 和三数据集 probability eval。
2. 若 KD 优于 Light no-KD，写成实证提升；若不优，写成失败分析。
3. 更新可视化图，增加 KD 列。
4. 只在 `status=final_main_kd` 后进入主表。

Gate 3 speed 完成后：

1. 用同一命令重测 baseline、Light 和已完成 KD。
2. 将 latency/FPS 写入效率表。
3. 如果只能复测 baseline/Light，KD speed 标为 absent，不插值、不推断。

Gate 4A B0 或 Gate 4B MobileMamba 候选验收完成后：

1. 只能使用 `status=external_dirty_tree_observation_candidate`，不得改成 `final_main_*`。
2. 必须更新 `paper_gate_patch_matrix.md`、`paper_final_patch_plan.md`、`paper_claim_evidence_matrix.md`、`paper_submission_readiness.md`、`paper_submission_packet.md` 和 `reproducibility_manifest.md`。
3. 必须同步 `agent_acceptance_ledger.md`，并运行 `audit_agent_acceptance_ledger.py`。
4. B0 必须运行 `audit_b0_status_consistency.py`；MobileMamba 必须运行 `audit_mobilemamba_status_consistency.py`。
5. 即使候选验收通过，也只能写作附录探索、工程观察或失败分析；不进入主表、摘要或结论强主张。

## 6. Final Paper Pass

提交前按顺序检查：

1. `paper_draft.md` 中所有数值均能追溯到 CSV、profile JSON、日志或图表脚本。
2. 摘要、实验和结论没有超出 `claim_evidence_audit.md` 允许范围。
3. 所有表格都带 Evidence Status 或等价说明。
4. B0 若没有完整验收，最多出现在工程观察或失败分析，不出现在主结果。
5. KD 若未完成，保留为补偿路线和失败风险，不删除中断事实。
6. 参考文献里的 2024-2026 轻量 COD/KD-COD 工作只支撑趋势和定位，不支撑“首次”主张。
7. 运行 `run_release_audits.sh`，状态必须为 pass。
8. 若新增 baseline/KD final probability eval，用 `--add-integrity` 把对应 run 纳入同一次验收。
9. 重新运行每个 final run 对应的 `check_run_integrity.py`，并保留命令输出或报告路径。
10. 最终表格如果展示 reference/verification/pending 行，必须显式标注，且不得参与 final average delta。
11. 若 B0/MobileMamba 有新 observation 或 candidate 结果，必须检查状态一致性审计和 agent acceptance ledger audit 均为 pass。
12. 若改动 prompt、pending card、GPU queue、task board 或 agent 验收记录，必须检查 `03_agent_tasks/task_board.md`、`audit_task_board_consistency.py` 和 `task_board_consistency_audit_latest.md` 均同步，并重新运行 release audit。
13. 若新增外发稿、图表资产、证据文档或 withheld claim，必须更新 `paper_delivery_manifest.md`，运行 `audit_paper_delivery_manifest.py`，并确认 `paper_delivery_manifest_audit_latest.md` 和完整 release audit 均为 pass。

当前提交包入口：

```text
/root/data-tmp/workspace/04_paper/drafts/paper_submission_packet.md
```
