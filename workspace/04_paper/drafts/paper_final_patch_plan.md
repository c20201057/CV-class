# Paper Final Patch Plan

更新时间：2026-06-14T02:48:00Z / 2026-06-14 10:48:00 CST

本文档是 gate 结果回来后的执行索引。更细的逐文件、逐章节改法以
`04_paper/drafts/paper_gate_patch_matrix.md` 为准；本文档负责规定执行顺序、
禁止越界和最终验收命令。

当前工作准则保持不变：不偷懒，不因为怕风险而保守。高风险分支可以继续验收，
但任何结果都必须先过 gate，再进入论文主张。

## Always Keep

- 主线模型：Light-ESCNet B2-C64，即 PVTv2-B2 + inter_channel=64 + 保留边缘-语义协同。
- 主训练结果：`light_b2_c64_e120_s42` 120 epoch complete。
- 主评测协议：probability-map evaluation，不使用 `test.py` 二值输出作为主表。
- 结构效率口径：params、GMACs、model size、peak memory 已可写。
- 速度口径：没有 Gate 3 前不写最终 latency/FPS speedup。
- 外发稿同步：任何 gate 回填都必须检查 `paper_interim_submission.md`、`teacher_share_pack.md`、`presentation_outline.md`、`paper_submission_packet.md` 和 `reproducibility_manifest.md`，不能只改 `paper_draft.md`。
- 验收同步：任何外部分支 Gate 4A/4B 状态变化都必须同步 `agent_acceptance_ledger.md`，并重跑 `audit_b0_status_consistency.py` 或 `audit_mobilemamba_status_consistency.py`，不能只更新观察日志或论文草稿。

## Execution Order After Any Gate Changes

1. 刷新状态：

```bash
python /root/data-tmp/workspace/02_experiments/scripts/orchestrator_tick.py
```

2. 判定 gate 是否真的 ready：

```bash
python /root/data-tmp/workspace/04_paper/scripts/audit_gate_patch_readiness.py \
  --metrics_csv /root/data-tmp/workspace/02_experiments/tables/metrics_all.csv
```

3. 只有对应 gate 是 `ready_to_patch`，才按 `paper_gate_patch_matrix.md` 修改论文、表格、图和证据文档。
4. 更新 `paper_claim_evidence_matrix.md`，让每条新增或改变的主张都有本地证据路径。
5. 重新生成聚合表和当前差值：

```bash
python /root/data-tmp/workspace/02_experiments/scripts/aggregate_results.py \
  --out_md /root/data-tmp/workspace/04_paper/tables/aggregated_results.md
python /root/data-tmp/workspace/04_paper/scripts/generate_delta_summary.py \
  --metrics_csv /root/data-tmp/workspace/02_experiments/tables/metrics_all.csv
```

6. 跑 release audit。若新增 final probability eval run，必须带 `--add-integrity`。

## Gate 1: Clean ESCNet-B5 Baseline

Patch entry: `paper_gate_patch_matrix.md` Gate 1 section.

只有以下全部成立时，才能把 ESCNet-B5 从历史参考行升级为 clean probability baseline：

- `baseline_escnet_b5_clean_prob_e120` 完成 CAMO、COD10K、NC4K。
- `check_run_integrity.py` 通过。
- `metrics_all.csv` 三行均为 `status=clean_prob_re_eval_complete`、`protocol=prob_map`。

回填原则：

- 将 Light-vs-ESCNet 差值从 historical reference 口径改为 clean same-protocol 口径。
- 重新计算摘要、主表、结论、scatter 和 `current_delta_summary.md` 中的 delta。
- 保留历史参考行作为核验背景，不再把它混作主 baseline。
- 同步更新 submission packet、teacher share pack、presentation outline 和 reproducibility manifest。

若 Gate 1 只有 CAMO/COD10K 或缺 integrity，只能写 progress，不能写 final clean baseline。

## Gate 2: KD B2-C64

Patch entry: `paper_gate_patch_matrix.md` Gate 2 section.

只有 KD recovery 产生完整 checkpoint、完成三数据集 probability eval、integrity 通过且
`metrics_all.csv` 三行均为 `status=final_main_kd`，才能回填 KD。

回填原则：

- KD 优于 no-KD：写具体提升和差值。
- KD 不优于 no-KD：写负结果分析，不能把失败包装成提升。
- KD 训练不稳定或无完整 checkpoint：继续写 engineering route，不进入主表。
- 若 KD predictions 已生成并通过完整性检查，才更新可视化图并增加 KD 列。

## Gate 3: Controlled Speed

Patch entry: `paper_gate_patch_matrix.md` Gate 3 section.

只有空闲 GPU、同一命令、同一 input size、同一 warmup/repeat 条件下的 baseline/Light
profile 都存在，才回填 latency/FPS。

回填原则：

- 数字支持 speedup 才在摘要和结论写 speedup。
- 数字不支持 speedup 时，只报告受控速度结果，不写“更快”。
- KD 没有 final checkpoint 时，KD speed 写 absent/no final checkpoint，不推断。
- 结构效率和 controlled speed 是两个 claim，必须在 `paper_claim_evidence_matrix.md` 中分开。

## Gate 4A: B0 Observation Candidate

Patch entry: `paper_gate_patch_matrix.md` Gate 4A section.

B0 即使通过候选验收，也只能作为 appendix、exploratory observation 或 failure analysis，
不能替代 Light-B2-C64 主线。

回填条件：

- dirty tree source/config snapshot 到 workspace。
- checkpoint load/profile forward 通过。
- CAMO/COD10K/NC4K probability eval 完整。
- integrity 和 release audit 通过。
- `metrics_all.csv` 三行均为 `status=external_dirty_tree_observation_candidate`。

回填原则：

- 不进摘要、主贡献或主表。
- 若结果弱于 Light，写过度压缩导致的定位/边界损失分析。
- 若只有 COD10K intermediate eval，继续只保留观察日志。

## Gate 4B: MobileMamba-T2 Observation Candidate

Patch entry: `paper_gate_patch_matrix.md` Gate 4B section.

MobileMamba-T2 即使通过候选验收，也只能作为 alternative lightweight backbone observation
或负例，不替代 Light-B2-C64。

回填条件：

- dirty tree source/config snapshot 到 workspace。
- checkpoint load/profile forward 通过。
- CAMO/COD10K/NC4K probability eval 完整。
- integrity 和 release audit 通过。
- `metrics_all.csv` 三行均为 `status=external_dirty_tree_observation_candidate`。

回填原则：

- 不进摘要、主贡献或主表。
- 若结果弱于 Light，写替代主干风险分析。
- 若只有 live training log、COD10K intermediate eval 或无完整三数据集 probability eval，继续不入正文结果表。

## No-Gate Final Draft Option

如果时间截止前 Gate 1/2/3 未完成，论文仍可提交为 honest interim version：

- 标题、摘要和结论围绕 Light-B2-C64。
- ESCNet-B5 只写历史参考口径。
- KD/B0/MobileMamba/speed 写为未完成或工程观察。
- 不写 SOTA、KD 有效、最终速度提升或 clean baseline 结论。

## Final Audit Commands

每次修改正文、表格、图像引用、metrics、profile、gate 文档或 prompt 后，运行：

```bash
TMPDIR=/root/data-tmp/tmp bash /root/data-tmp/workspace/02_experiments/scripts/run_release_audits.sh
```

如果新增 final probability eval run：

```bash
TMPDIR=/root/data-tmp/tmp bash /root/data-tmp/workspace/02_experiments/scripts/run_release_audits.sh \
  --add-integrity <prob_eval_run_dir> <exp_id> CAMO,COD10K,NC4K
```

必须通过的关键审计：

- `audit_paper_evidence.py`
- `audit_claim_text.py`
- `audit_gate_patch_readiness.py`
- `audit_route_decision_consistency.py`
- `audit_gpu_handoff_consistency.py`
- `audit_b0_status_consistency.py`
- `audit_mobilemamba_status_consistency.py`
- `audit_agent_acceptance_ledger.py`
- `audit_submission_protocol.py`
- `check_run_integrity.py` for every final probability eval run

如果任一审计失败，不更新摘要和结论为最终强主张；先修 evidence、metadata 或文本边界。
