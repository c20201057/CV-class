# P0 Light-ESCNet B2-C64 Implementation Report

任务 ID / 实验 ID: P0_light_b2_c64_impl / light_b2_c64

完成状态: pass

## 写入或修改文件

- `/root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64/`
  - copied runnable ESCNet code into an isolated experiment directory.
  - `config.py`: added `inter_channel: int = 128` and `bb_pretrained: bool = True`; validation now requires a selected backbone weight only when `bb_pretrained` is true.
  - `models/ESCNet.py`: replaced hard-coded `inter_channel = 128` with `getattr(config, "inter_channel", 128)`.
  - `train.py`: model construction now uses `pretrained=self.config.bb_pretrained`; fixed dataloader config reference from module-level `config` to `self.config`.
  - `tools/smoke_light_b2_c64.py`: added random-input forward smoke test and parameter counter.
- `/root/data-tmp/workspace/02_experiments/configs/light_b2_c64.yaml`
  - new Light-ESCNet B2-C64 config.
- `/root/data-tmp/workspace/03_agent_tasks/reports/P0_light_b2_c64_impl.md`
  - this report.

No direct writes were made intentionally to `/root/ESCNet`.

## 配置示例

```yaml
backbone: pvt_v2_b2
img_size: 416
lateral_channels: [512, 320, 128, 64]
inter_channel: 64
bb_pretrained: false
save_model_dir: /root/data-tmp/workspace/02_experiments/runs
name: light_b2_c64
```

Full config: `/root/data-tmp/workspace/02_experiments/configs/light_b2_c64.yaml`

`bb_pretrained: false` is used because the local weights directory currently contains only `pvt_v2_b5_22k.pth`; no PVTv2-B2 pretrained checkpoint was present.

## 使用命令

Static checks:

```bash
cd /root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64
python -m py_compile config.py models/ESCNet.py train.py test.py eval.py tools/smoke_light_b2_c64.py
python - <<'PY'
from config import load_config
cfg = load_config('/root/data-tmp/workspace/02_experiments/configs/light_b2_c64.yaml')
print(cfg.model_dump_json(indent=2))
PY
```

Forward smoke and parameter count:

```bash
cd /root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64
python tools/smoke_light_b2_c64.py \
  --config /root/data-tmp/workspace/02_experiments/configs/light_b2_c64.yaml \
  --batch-size 1 \
  --device cuda
```

Interface compatibility checks:

```bash
cd /root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64
python train.py --help
python test.py --help
python eval.py --help
python - <<'PY'
from config import load_config
from models.ESCNet import ESCNet
cfg = load_config('config.yaml')
model = ESCNet(cfg, pretrained=False)
print('backbone', cfg.backbone)
print('inter_channel', cfg.inter_channel)
print('bb_pretrained', cfg.bb_pretrained)
print('params', sum(p.numel() for p in model.parameters()))
PY
```

## 使用数据/配置/checkpoint

- Config: `/root/data-tmp/workspace/02_experiments/configs/light_b2_c64.yaml`
- Dataset paths referenced by config:
  - train: `/root/data-tmp/COD/Train`
  - test: `/root/data-tmp/COD/Test/COD10K`
- Checkpoint: none used for smoke test.
- Local pretrained weights observed: `/root/data-tmp/weights/pvt_v2_b5_22k.pth` only.

## 关键结果

Smoke test result:

```json
{
  "variant": "Light-ESCNet B2-C64",
  "device": "cuda",
  "input_shape": [1, 3, 416, 416],
  "edge_shape": [1, 1, 416, 416],
  "mask_shapes": [
    [1, 1, 13, 13],
    [1, 1, 26, 26],
    [1, 1, 52, 52],
    [1, 1, 416, 416]
  ],
  "params": 29807714,
  "params_m": 29.808,
  "backbone": "pvt_v2_b2",
  "lateral_channels": [512, 320, 128, 64],
  "inter_channel": 64,
  "bb_pretrained": false
}
```

Parameter count is 29.807714M, matching the target of about 29.8M.

Backward-compatible default construction was also checked using the copied original `config.yaml`: `pvt_v2_b5`, `inter_channel=128`, `bb_pretrained=True`, `params=99903234`.

## 证据路径

- Isolated code: `/root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64/`
- Config: `/root/data-tmp/workspace/02_experiments/configs/light_b2_c64.yaml`
- Smoke script: `/root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64/tools/smoke_light_b2_c64.py`
- Report: `/root/data-tmp/workspace/03_agent_tasks/reports/P0_light_b2_c64_impl.md`

## 训练/测试/评估兼容启动方式

Train:

```bash
cd /root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64
python train.py --config /root/data-tmp/workspace/02_experiments/configs/light_b2_c64.yaml
```

Test after training produces a checkpoint:

```bash
cd /root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64
python test.py \
  --config /root/data-tmp/workspace/02_experiments/configs/light_b2_c64.yaml \
  --ckpt /root/data-tmp/workspace/02_experiments/runs/light_b2_c64/epoch_120.pth \
  --pred_root /root/data-tmp/workspace/02_experiments/runs/light_b2_c64/preds_cod10k
```

Eval after predictions exist:

```bash
cd /root/data-tmp/workspace/02_experiments/code/light_escnet_b2_c64
python eval.py \
  --config /root/data-tmp/workspace/02_experiments/configs/light_b2_c64.yaml \
  --pred_root /root/data-tmp/workspace/02_experiments/runs/light_b2_c64/preds_cod10k \
  --save_dir /root/data-tmp/workspace/02_experiments/runs/light_b2_c64/results_cod10k
```

## 风险和异常

- No full training was run, per task requirement.
- The local environment does not include a PVTv2-B2 pretrained weight file. The current config uses random B2 initialization via `bb_pretrained: false`. For a serious training run, add a B2 weight path under `weights.pvt_v2_b2` and set `bb_pretrained: true`.
- The final mask output is full-resolution `[1, 1, 416, 416]`, while earlier masks are `[13, 13]`, `[26, 26]`, and `[52, 52]`. This matches the copied ESCNet decoder behavior and is compatible with the existing training code, which resizes every mask to GT size before computing structure loss.
- `/root/ESCNet` already had a dirty git state when inspected; this task did not clean, revert, or overwrite those files.

## 是否可入论文

only as ablation

The implementation and profile are usable as an ablation candidate. Accuracy claims require full training/testing/evaluation and main-controller acceptance.

## 建议下一步

1. Add a real PVTv2-B2 pretrained checkpoint, update `weights.pvt_v2_b2`, and switch `bb_pretrained: true`.
2. Launch the training command above into `/root/data-tmp/workspace/02_experiments/runs/light_b2_c64`.
3. Run COD10K/CAMO/NC4K test and eval with the same isolated code after checkpoints are produced.
4. Profile FLOPs/GMACs, FPS, latency, model size, and peak memory for the efficiency table.
