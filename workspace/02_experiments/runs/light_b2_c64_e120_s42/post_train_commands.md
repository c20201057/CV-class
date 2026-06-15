# Post-Train Commands: light_b2_c64_e120_s42

等训练完成后执行。不要在四卡 DDP 训练还占用 GPU 时启动这些命令。

## 1. 确认 checkpoint

```bash
ls -lh /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/epoch_*.pth
```

优先使用：

```text
/root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/epoch_120.pth
```

若没有 `epoch_120.pth`，使用最高 epoch checkpoint，并写入 metadata 与论文实验设置。

## 2. 三数据集概率图评测

```bash
bash /root/data-tmp/workspace/02_experiments/scripts/run_prob_eval_suite.sh \
  --repo /root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64 \
  --template_config /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/config.yaml \
  --ckpt /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/epoch_120.pth \
  --exp_id light_b2_c64_e120_s42_prob_eval_v2 \
  --datasets CAMO,COD10K,NC4K \
  --device cuda:0 \
  --method epoch_120
```

## 3. 训练后 profile

```bash
python /root/data-tmp/workspace/02_experiments/scripts/profile_model.py \
  --repo /root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64 \
  --config /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/config.yaml \
  --ckpt /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/epoch_120.pth \
  --out /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42/profile_epoch120.json \
  --device cuda:0 \
  --warmup 20 \
  --repeat 50 \
  --exp-id light_b2_c64_trained_416
```

## 4. 完整性检查

```bash
python /root/data-tmp/workspace/02_experiments/scripts/check_run_integrity.py \
  --run_dir /root/data-tmp/workspace/02_experiments/runs/light_b2_c64_e120_s42_prob_eval_v2 \
  --exp_id light_b2_c64_e120_s42_prob_eval_v2 \
  --datasets CAMO,COD10K,NC4K
```

## 5. 生成论文表格

```bash
python /root/data-tmp/workspace/02_experiments/scripts/aggregate_results.py \
  --out_md /root/data-tmp/workspace/04_paper/tables/aggregated_results.md
```

## 6. 接着启动 KD smoke

```bash
cd /root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64

python tools/smoke_kd_online.py \
  --config configs/kd_light_b2_c64.yaml \
  --device cuda:0 \
  --batch-size 1 \
  --max-batches 1 \
  2>&1 | tee /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/smoke/kd_online_b1.log

python tools/smoke_kd_online.py \
  --config configs/kd_light_b2_c64.yaml \
  --device cuda:0 \
  --batch-size 4 \
  --max-batches 1 \
  2>&1 | tee /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/smoke/kd_online_b4.log
```

## 7. 启动 KD full training

```bash
mkdir -p /root/data-tmp/tmp /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/logs
cd /root/data-tmp/workspace/02_experiments/code/kd_light_escnet_b2_c64
TMPDIR=/root/data-tmp/tmp torchrun --nproc_per_node=4 train.py \
  --config /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/config.yaml \
  2>&1 | tee /root/data-tmp/workspace/02_experiments/runs/kd_light_b2_c64_e120_s42/train_ddp.log
```

所有临时目录、预测、日志与 checkpoint 均写入 `/root/data-tmp`，避免继续占用根分区。
