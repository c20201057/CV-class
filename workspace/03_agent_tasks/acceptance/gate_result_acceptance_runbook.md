# Gate Result Acceptance Runbook

更新时间：2026-06-14T00:35:00Z

本文档给 GPU queue operator、后续实验 agent 和主控交接使用。它把“跑完实验”之后必须做的验收、论文回填和审计动作集中到一页，避免 Gate 结果落盘后只更新指标、不更新论文证据边界。

工作准则保持不变：不偷懒，不因为怕风险而保守。高风险路线可以继续做，但必须隔离写入范围、保留日志、通过 gate 后再写论文结论。

## 0. 接管前状态确认

先读：

- `/root/data-tmp/workspace/00_project/orchestrator_tick_latest.md`
- `/root/data-tmp/workspace/00_project/orchestrator_tick_latest.json`
- `/root/data-tmp/workspace/02_experiments/scripts/GPU_QUEUE.md`
- `/root/data-tmp/workspace/04_paper/drafts/finalization_gates.md`
- `/root/data-tmp/workspace/04_paper/drafts/paper_gate_patch_matrix.md`

然后记录：

```bash
python /root/data-tmp/workspace/02_experiments/scripts/orchestrator_tick.py
nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits
ps -eo pid,ppid,stat,etime,rss,cmd | grep -E 'torchrun|train.py|test.py|infer_prob.py|run_prob_eval_suite' | grep -v grep || true
```

如果 MobileMamba-T2 或其他外部 GPU 任务仍在运行，不抢占、不重复启动 baseline/KD。只刷新状态并等待，除非用户明确要求终止或抢占。

## 1. Gate 1 Clean Baseline 验收

Gate 1 只有在以下条件同时满足时才能升级论文 baseline：

1. `baseline_escnet_b5_clean_prob_e120` 在 CAMO、COD10K、NC4K 三个数据集都有 result。
2. `check_run_integrity.py` 对该 run 通过。
3. `metrics_all.csv` 中三行均为 `status=clean_prob_re_eval_complete`。
4. 三行均为 `protocol=prob_map`，且 repo boundary 指向 clean baseline。
5. release audit 通过。

验收命令：

```bash
python /root/data-tmp/workspace/02_experiments/scripts/check_run_integrity.py \
  --run_dir /root/data-tmp/workspace/02_experiments/runs/baseline_escnet_b5_clean_prob_e120 \
  --exp_id baseline_escnet_b5_clean_prob_e120 \
  --datasets CAMO,COD10K,NC4K \
  --dataset_root /root/data-tmp/COD/Test \
  --metrics_csv /root/data-tmp/workspace/02_experiments/tables/metrics_all.csv

TMPDIR=/root/data-tmp/tmp /root/data-tmp/workspace/02_experiments/scripts/run_release_audits.sh \
  --add-integrity /root/data-tmp/workspace/02_experiments/runs/baseline_escnet_b5_clean_prob_e120 \
  baseline_escnet_b5_clean_prob_e120 CAMO,COD10K,NC4K
```

Gate 1 通过后的论文回填：

- 按 `04_paper/drafts/paper_gate_patch_matrix.md` 的 Gate 1 section 更新 `paper_draft.md`、`paper_interim_submission.md`、`main_results_template.md`、`aggregated_results.md`、`evidence_index.md`、`paper_claim_evidence_matrix.md`、`paper_submission_readiness.md`。
- 运行 `generate_delta_summary.py`，用 clean baseline delta 替换 historical reference delta。
- 全文检索并处理旧口径：`historical reference`、`历史参考`、`pending`、`待确认`、`0.009`、`0.006`、`0.027`。
- 如果任一条件缺失，只能写 Gate 1 progress，不能写 final clean probability baseline。

## 2. Gate 2 KD 验收

Gate 2 只有在以下条件同时满足时才能把 KD 写入结果：

1. KD recovery 产生完整 checkpoint。
2. KD 完成 CAMO、COD10K、NC4K 三数据集 probability eval。
3. `check_run_integrity.py` 通过。
4. `metrics_all.csv` 三行均为 `status=final_main_kd` 和 `protocol=prob_map`。
5. release audit 通过。

KD 结果分三种写法：

- KD 优于 no-KD：写实证提升和 delta。
- KD 不优于 no-KD：写负结果分析，讨论 output-level MSE、teacher/student 容量差距、边界误差和训练稳定性。
- KD 未产生完整结果：继续写 engineering route，不进入主表。

禁止把 `epoch_1.pth` 到 `epoch_5.pth`、中断日志或 smoke 指标写成 KD 主结果。

## 3. Gate 3 Speed 验收

Gate 3 只有在空闲 GPU、同一命令、同一输入尺寸、同一 warmup/repeat 条件下成立。

必须检查：

- 无 `torchrun|train.py|test.py|infer_prob.py` 活跃。
- baseline 和 Light 至少都有 idle profile row。
- `profiles.csv` 中 latency/FPS/profile_json/device/img_size/warmup/repeat 字段完整。
- baseline 与 Light 的 device/img_size/warmup/repeat 一致。

如果同条件速度没有更快，仍可报告 latency/FPS 数字，但摘要和结论不得写 speedup。若 KD 无 final checkpoint，KD speed 写 absent/no final checkpoint，不插值、不推断。

## 4. Gate 4A/4B Observation Candidate 验收

B0 和 MobileMamba-T2 都不是主线结果。即使候选 checkpoint 出现，也只能在以下条件通过后作为附录探索或失败分析：

1. dirty tree source/config snapshot 到 `/root/data-tmp/workspace`。
2. checkpoint load/profile forward 通过。
3. CAMO/COD10K/NC4K probability eval 完整。
4. integrity 和 release audit 通过。
5. `metrics_all.csv` status 为 `external_dirty_tree_observation_candidate`。

Gate 4A/4B 通过后仍不能自动进入主表、摘要或结论；是否写入由主控按论文叙事决定。

## 5. 每次 Gate 更新后的通用审计

```bash
python /root/data-tmp/workspace/02_experiments/scripts/aggregate_results.py \
  --out_md /root/data-tmp/workspace/04_paper/tables/aggregated_results.md
python /root/data-tmp/workspace/04_paper/scripts/generate_delta_summary.py
TMPDIR=/root/data-tmp/tmp /root/data-tmp/workspace/02_experiments/scripts/run_release_audits.sh
python /root/data-tmp/workspace/02_experiments/scripts/orchestrator_tick.py
```

如果新增 final probability eval run，`run_release_audits.sh` 必须带 `--add-integrity`。如果审计失败，不更新摘要和结论为强主张。

## 6. 接管回报模板

```text
任务 ID / 实验 ID:
完成状态: pass / partial / fail
GPU 状态:
Gate 状态变化:
使用命令:
写入或修改文件:
新增 metrics/profile/status:
完整性检查:
release audit:
论文回填动作:
仍禁止写入论文的内容:
风险和异常:
下一步:
```

