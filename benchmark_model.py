import argparse
import json
import time
from collections import defaultdict
from pathlib import Path

import torch
import torch.nn as nn
from torchvision.ops import DeformConv2d

from config import load_config
from models.ESCNet import ESCNet


def extract_state_dict(checkpoint):
    if isinstance(checkpoint, dict):
        for key in (
            "state_dict",
            "model",
            "model_state_dict",
            "student",
            "student_state_dict",
        ):
            value = checkpoint.get(key)
            if isinstance(value, dict):
                checkpoint = value
                break

    if not isinstance(checkpoint, dict):
        raise TypeError("Checkpoint does not contain a valid state dict.")

    cleaned = {}
    for key, value in checkpoint.items():
        clean_key = key
        changed = True
        while changed:
            changed = False
            for prefix in ("module.", "_orig_mod."):
                if clean_key.startswith(prefix):
                    clean_key = clean_key[len(prefix) :]
                    changed = True
        cleaned[clean_key] = value
    return cleaned


class FlopCounter:
    def __init__(self, model):
        self.model = model
        self.macs_by_type = defaultdict(int)
        self.handles = []

    def _add(self, name, macs):
        self.macs_by_type[name] += int(macs)

    def _conv_hook(self, module, inputs, output):
        if not torch.is_tensor(output):
            return
        kernel_ops = module.kernel_size[0] * module.kernel_size[1]
        kernel_ops *= module.in_channels // module.groups
        self._add(module.__class__.__name__, output.numel() * kernel_ops)

    def _linear_hook(self, module, inputs, output):
        if not torch.is_tensor(output):
            return
        self._add("Linear", output.numel() * module.in_features)

    def _pvt_attention_hook(self, module, inputs, output):
        if not inputs or not torch.is_tensor(inputs[0]):
            return
        x = inputs[0]
        if x.ndim != 3:
            return
        batch, n_tokens, channels = x.shape
        n_heads = module.num_heads
        head_dim = channels // n_heads
        if getattr(module, "sr_ratio", 1) > 1 and len(inputs) >= 3:
            h, w = int(inputs[1]), int(inputs[2])
            sr = int(module.sr_ratio)
            kv_tokens = (h // sr) * (w // sr)
        else:
            kv_tokens = n_tokens
        self._add(
            "AttentionMatMul",
            2 * batch * n_heads * n_tokens * kv_tokens * head_dim,
        )

    def _sa_hook(self, module, inputs, output):
        if not inputs or not torch.is_tensor(inputs[0]):
            return
        x = inputs[0]
        if x.ndim != 4:
            return
        batch, channels, height, width = x.shape
        n_heads = module.num_heads
        head_dim = channels // n_heads
        tokens = height * width
        self._add("SAMatMul", 2 * batch * n_heads * head_dim * head_dim * tokens)

    def register(self):
        for module in self.model.modules():
            if isinstance(module, DeformConv2d):
                self.handles.append(module.register_forward_hook(self._conv_hook))
            elif isinstance(module, nn.Conv2d):
                self.handles.append(module.register_forward_hook(self._conv_hook))
            elif isinstance(module, nn.Linear):
                self.handles.append(module.register_forward_hook(self._linear_hook))

            class_name = module.__class__.__name__
            if class_name == "Attention" and hasattr(module, "sr_ratio"):
                self.handles.append(
                    module.register_forward_hook(self._pvt_attention_hook)
                )
            elif class_name == "SA" and hasattr(module, "num_heads"):
                self.handles.append(module.register_forward_hook(self._sa_hook))

    def close(self):
        for handle in self.handles:
            handle.remove()
        self.handles.clear()

    def profile(self, inputs):
        self.macs_by_type.clear()
        self.register()
        was_training = self.model.training
        self.model.eval()
        with torch.inference_mode():
            self.model(inputs)
        if was_training:
            self.model.train()
        self.close()
        macs = sum(self.macs_by_type.values())
        return {
            "macs": macs,
            "gmacs": macs / 1e9,
            "gflops": 2 * macs / 1e9,
            "breakdown_gmacs": {
                key: value / 1e9 for key, value in sorted(self.macs_by_type.items())
            },
        }


def load_model(args, device):
    config = load_config(args.config)
    config.compile = False
    if args.disable_distillation and hasattr(config, "distillation"):
        config.distillation.enabled = False
        config.distillation.feature_loss_weight = 0.0

    pretrained = not args.no_pretrained and not args.ckpt
    model = ESCNet(config, pretrained=pretrained)

    load_info = None
    if args.ckpt:
        checkpoint = torch.load(args.ckpt, map_location="cpu", weights_only=False)
        state_dict = extract_state_dict(checkpoint)
        load_result = model.load_state_dict(state_dict, strict=args.strict)
        load_info = {
            "checkpoint": str(args.ckpt),
            "strict": args.strict,
            "missing_keys": list(load_result.missing_keys),
            "unexpected_keys": list(load_result.unexpected_keys),
        }

    model = model.to(device)
    model.eval()
    return config, model, load_info


def benchmark_fps(model, inputs, warmup, iters):
    if inputs.is_cuda:
        torch.cuda.synchronize(inputs.device)
        torch.cuda.reset_peak_memory_stats(inputs.device)

    with torch.inference_mode():
        for _ in range(warmup):
            model(inputs)
        if inputs.is_cuda:
            torch.cuda.synchronize(inputs.device)

        start = time.perf_counter()
        for _ in range(iters):
            model(inputs)
        if inputs.is_cuda:
            torch.cuda.synchronize(inputs.device)
        elapsed = time.perf_counter() - start

    images = inputs.shape[0] * iters
    result = {
        "batch_size": inputs.shape[0],
        "iterations": iters,
        "elapsed_sec": elapsed,
        "latency_ms_per_batch": elapsed * 1000 / iters,
        "latency_ms_per_image": elapsed * 1000 / images,
        "fps": images / elapsed,
    }
    if inputs.is_cuda:
        result["max_memory_mb"] = torch.cuda.max_memory_allocated(inputs.device) / 1024**2
    return result


def main():
    parser = argparse.ArgumentParser(description="Benchmark ESCNet Params/FLOPs/FPS.")
    parser.add_argument("--config", required=True, help="Path to config yaml.")
    parser.add_argument("--ckpt", default=None, help="Optional model checkpoint.")
    parser.add_argument("--device", default="cuda:0", help="Benchmark device.")
    parser.add_argument("--input-size", type=int, default=None, help="Input image size.")
    parser.add_argument("--batch-size", type=int, default=1, help="Inference batch size.")
    parser.add_argument("--warmup", type=int, default=20, help="Warmup iterations.")
    parser.add_argument("--iters", type=int, default=100, help="Timed iterations.")
    parser.add_argument(
        "--no-pretrained",
        action="store_true",
        help="Do not load backbone pretrained weights when no checkpoint is given.",
    )
    parser.add_argument(
        "--disable-distillation",
        action="store_true",
        default=True,
        help="Disable distillation-only adapters for deployment-style benchmarking.",
    )
    parser.add_argument(
        "--keep-distillation",
        action="store_false",
        dest="disable_distillation",
        help="Keep distillation modules from config.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Use strict checkpoint loading.",
    )
    parser.add_argument("--json-out", default=None, help="Optional path to save JSON.")
    args = parser.parse_args()

    if args.device.startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but torch.cuda.is_available() is false.")

    device = torch.device(args.device)
    if device.type == "cuda":
        torch.backends.cudnn.benchmark = True
        torch.set_float32_matmul_precision("high")

    config, model, load_info = load_model(args, device)
    input_size = args.input_size or config.img_size
    inputs = torch.randn(args.batch_size, 3, input_size, input_size, device=device)

    params = sum(parameter.numel() for parameter in model.parameters())
    trainable_params = sum(
        parameter.numel() for parameter in model.parameters() if parameter.requires_grad
    )
    flop_result = FlopCounter(model).profile(inputs)
    fps_result = benchmark_fps(model, inputs, args.warmup, args.iters)

    result = {
        "config": str(Path(args.config).resolve()),
        "checkpoint": str(Path(args.ckpt).resolve()) if args.ckpt else None,
        "backbone": config.backbone,
        "input_size": input_size,
        "device": str(device),
        "params": params,
        "params_m": params / 1e6,
        "trainable_params": trainable_params,
        "trainable_params_m": trainable_params / 1e6,
        "flops": flop_result,
        "speed": fps_result,
        "load_info": load_info,
        "notes": [
            "FLOPs are approximate hook-based estimates.",
            "Conv/Linear/DeformConv and attention matmuls are counted.",
            "Interpolation, elementwise ops, activations, normalization, and IO are not fully counted.",
            "GFLOPs are reported as 2 * GMACs.",
        ],
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.json_out:
        out_path = Path(args.json_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
