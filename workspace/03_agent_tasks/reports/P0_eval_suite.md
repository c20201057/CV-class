# P0 Evaluation Suite Report

## Task ID / Experiment ID

- Task: P0_eval_suite
- Smoke experiment: smoke_eval_suite_b5_camo

## Completion Status

pass

## Files Written Or Modified

- /root/data-tmp/workspace/02_experiments/scripts/run_eval_suite.sh
- /root/data-tmp/workspace/02_experiments/scripts/collect_metrics.py
- /root/data-tmp/workspace/03_agent_tasks/reports/P0_eval_suite.md
- /root/data-tmp/workspace/02_experiments/runs/smoke_eval_suite_b5_camo/ created for CAMO smoke

No changes were made to /root/ESCNet/test.py or /root/ESCNet/eval.py.

## Implementation Summary

### run_eval_suite.sh

- Supports --repo, --ckpt, --exp_id/--exp-id, --out_root/--out-root, --datasets, --device_ids/--device-ids, --config, --dataset_root, --batch_size_valid, --num_workers, --n_threads, and --metrics_csv.
- Defaults to CAMO,COD10K,NC4K and uses the existing dataset-specific ESCNet configs when --config is omitted:
  - CAMO: /root/ESCNet/config.camo.yaml
  - COD10K: /root/ESCNet/config.yaml
  - NC4K: /root/ESCNet/config.nc4k.yaml
- Refuses to overwrite an existing run directory.
- Keeps all generated configs, predictions, results, logs, metadata, and default metrics CSV under the run directory.
- Writes one derived config per dataset and sends each dataset to independent directories:
  - configs/<DATASET>.yaml
  - preds/<DATASET>/<method>/*.png
  - results/<DATASET>/result.txt
  - logs/<DATASET>_test.log and logs/<DATASET>_eval.log
- Checks prediction count against GT count before evaluation.
- Records git status and latest commit from /root/ESCNet without reverting or cleaning anything.

### collect_metrics.py

- Parses ESCNet prettytable result.txt output.
- Supports one or more --result DATASET=path inputs.
- Supports --result_root containing DATASET/result.txt children.
- Supports old appended multi-table result files when --datasets gives the table order.
- Creates or updates a CSV with fields:
  exp_id,dataset,method,Smeasure,wFmeasure,meanFm,meanEm,MAE,source
- Updates are idempotent by key exp_id,dataset,method: repeated parses replace the existing row instead of duplicating it.
- Optional --out_md can emit a Markdown table for newly parsed rows.

## Commands Used

Static checks:

```bash
chmod +x /root/data-tmp/workspace/02_experiments/scripts/run_eval_suite.sh /root/data-tmp/workspace/02_experiments/scripts/collect_metrics.py
bash -n /root/data-tmp/workspace/02_experiments/scripts/run_eval_suite.sh
python -m py_compile /root/data-tmp/workspace/02_experiments/scripts/collect_metrics.py
```

Parser compatibility check against existing appended result format:

```bash
python /root/data-tmp/workspace/02_experiments/scripts/collect_metrics.py \
  --exp_id parser_check \
  --result /root/ESCNet/results_epoch120/result.txt \
  --datasets COD10K,CAMO,NC4K \
  --out_csv /root/data-tmp/workspace/02_experiments/runs/parser_check_metrics_all.csv
```

The temporary parser_check CSV and py_compile cache were removed after this check because they were not part of the authorized final outputs.

CAMO smoke:

```bash
/root/data-tmp/workspace/02_experiments/scripts/run_eval_suite.sh \
  --repo /root/ESCNet \
  --ckpt /root/ESCNet/checkpoints/escnet/epoch_120.pth \
  --exp_id smoke_eval_suite_b5_camo \
  --out_root /root/data-tmp/workspace/02_experiments/runs \
  --datasets CAMO \
  --device_ids 0 \
  --n_threads 4
```

Idempotent CSV update check:

```bash
python /root/data-tmp/workspace/02_experiments/scripts/collect_metrics.py \
  --exp_id smoke_eval_suite_b5_camo \
  --out_csv /root/data-tmp/workspace/02_experiments/runs/smoke_eval_suite_b5_camo/metrics_all.csv \
  --result CAMO=/root/data-tmp/workspace/02_experiments/runs/smoke_eval_suite_b5_camo/results/CAMO/result.txt
```

## Data / Config / Checkpoint

- Repo: /root/ESCNet
- Repo commit recorded by smoke run: 25c4387 Update README.md
- Checkpoint: /root/ESCNet/checkpoints/escnet/epoch_120.pth
- Dataset root: /root/data-tmp/COD/Test
- Smoke dataset: /root/data-tmp/COD/Test/CAMO
- Derived smoke config: /root/data-tmp/workspace/02_experiments/runs/smoke_eval_suite_b5_camo/configs/CAMO.yaml
- Device ids: 0

## Smoke Results

Prediction integrity:

```text
dataset,gt_count,pred_count,result_txt
CAMO,250,250,/root/data-tmp/workspace/02_experiments/runs/smoke_eval_suite_b5_camo/results/CAMO/result.txt
```

Parsed CAMO metrics from the smoke run:

```text
exp_id,dataset,method,Smeasure,wFmeasure,meanFm,meanEm,MAE,source
smoke_eval_suite_b5_camo,CAMO,epoch_120,0.811,0.761,0.800,0.873,0.067,/root/data-tmp/workspace/02_experiments/runs/smoke_eval_suite_b5_camo/results/CAMO/result.txt
```

Raw result.txt:

```text
+-----------+----------+-----------+--------+--------+-----+
&   Method  & Smeasure & wFmeasure & meanFm & meanEm & MAE &
+-----------+----------+-----------+--------+--------+-----+
& epoch_120 &   811    &    761    &  800   &  873   & 067 &
+-----------+----------+-----------+--------+--------+-----+
```

Metrics CSV update:

- Smoke run CSV: /root/data-tmp/workspace/02_experiments/runs/smoke_eval_suite_b5_camo/metrics_all.csv
- Initial smoke collection: parsed=1 inserted=1 replaced=0
- Re-run idempotency check: parsed=1 inserted=0 replaced=1
- Public table /root/data-tmp/workspace/02_experiments/tables/metrics_all.csv was not modified because the task write scope did not authorize changing it.

## Evidence Paths

- Smoke metadata: /root/data-tmp/workspace/02_experiments/runs/smoke_eval_suite_b5_camo/metadata.json
- Derived config: /root/data-tmp/workspace/02_experiments/runs/smoke_eval_suite_b5_camo/configs/CAMO.yaml
- Inference log: /root/data-tmp/workspace/02_experiments/runs/smoke_eval_suite_b5_camo/logs/CAMO_test.log
- Evaluation log: /root/data-tmp/workspace/02_experiments/runs/smoke_eval_suite_b5_camo/logs/CAMO_eval.log
- Predictions: /root/data-tmp/workspace/02_experiments/runs/smoke_eval_suite_b5_camo/preds/CAMO/epoch_120/
- Result file: /root/data-tmp/workspace/02_experiments/runs/smoke_eval_suite_b5_camo/results/CAMO/result.txt
- Run metrics CSV: /root/data-tmp/workspace/02_experiments/runs/smoke_eval_suite_b5_camo/metrics_all.csv
- Integrity CSV: /root/data-tmp/workspace/02_experiments/runs/smoke_eval_suite_b5_camo/integrity.csv
- Git status snapshot: /root/data-tmp/workspace/02_experiments/runs/smoke_eval_suite_b5_camo/git_status_short.txt

## Risks And Exceptions

- /root/ESCNet was already dirty before this task. The smoke run recorded that state and did not revert, clean, or overwrite it.
- The smoke CAMO metrics are lower than the existing public baseline CAMO row in /root/data-tmp/workspace/02_experiments/tables/metrics_all.csv. Current /root/ESCNet/test.py saves thresholded binary predictions, which can change metric values versus probability-map evaluation. Because this task explicitly forbids editing test.py or eval.py, this is reported as a comparability risk rather than patched here.
- Full COD10K and NC4K evaluation was not run in this worker turn to avoid a long uncontrolled job. The runner defaults to all three datasets and the CAMO smoke verifies the full path: derived config, isolated predictions, isolated result.txt, and CSV parsing.
- --metrics_csv can update any caller-specified CSV, including the public table, but this smoke used the default run-local CSV to respect the stated write scope.

## Paper Readiness

是否可入论文: no for the smoke metrics; yes for the evaluation tooling after main-controller acceptance.

The smoke metrics should not be used as final paper results until the probability-vs-binary prediction issue is resolved or accepted as the intended evaluation protocol.

## Suggested Next Step

Run the same suite for all three datasets under a fresh exp_id after confirming the intended prediction protocol, for example:

```bash
/root/data-tmp/workspace/02_experiments/scripts/run_eval_suite.sh \
  --repo /root/ESCNet \
  --ckpt /root/ESCNet/checkpoints/escnet/epoch_120.pth \
  --exp_id baseline_escnet_b5_eval_suite_full \
  --datasets CAMO,COD10K,NC4K \
  --device_ids 0
```
