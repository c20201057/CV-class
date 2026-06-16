import argparse
import time
from contextlib import nullcontext
from pathlib import Path

import torch
from thop import profile
from thop.utils import clever_format

from config import load_config
from models.build_model import build_model


def count_parameters(model):
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return total, trainable


def _sync_device(device):
    if torch.device(device).type == "cuda":
        torch.cuda.synchronize(torch.device(device))


def benchmark_fps(model, dummy, device, warmup=20, repeats=100, use_amp=False):
    if repeats <= 0:
        raise ValueError("--repeats must be greater than 0 when FPS benchmarking is enabled.")
    if warmup < 0:
        raise ValueError("--warmup must be greater than or equal to 0.")

    device_type = torch.device(device).type
    amp_context = (
        torch.autocast(device_type="cuda", dtype=torch.float16)
        if use_amp and device_type == "cuda"
        else nullcontext()
    )

    with torch.inference_mode(), amp_context:
        for _ in range(warmup):
            model(dummy)

        _sync_device(device)
        start = time.perf_counter()
        for _ in range(repeats):
            model(dummy)
        _sync_device(device)
        elapsed = time.perf_counter() - start

    batch_size = dummy.shape[0]
    images = repeats * batch_size
    fps = images / elapsed
    ms_per_batch = elapsed * 1000.0 / repeats
    ms_per_image = elapsed * 1000.0 / images

    return {
        "fps": fps,
        "ms_per_batch": ms_per_batch,
        "ms_per_image": ms_per_image,
        "warmup": warmup,
        "repeats": repeats,
        "use_amp": use_amp and device_type == "cuda",
    }


def profile_one(
    config_path,
    batch_size=1,
    device=None,
    benchmark=True,
    warmup=20,
    repeats=100,
    fps_amp=False,
):
    cfg = load_config(config_path)
    device = device or ("cuda:0" if torch.cuda.is_available() else "cpu")

    model = build_model(cfg, pretrained=False).to(device)
    model.eval()

    dummy = torch.randn(
        batch_size,
        3,
        cfg.img_size,
        cfg.img_size,
        device=device,
    )

    with torch.no_grad():
        macs, thop_params = profile(model, inputs=(dummy,), verbose=False)

    fps_stats = None
    if benchmark:
        fps_stats = benchmark_fps(
            model,
            dummy,
            device,
            warmup=warmup,
            repeats=repeats,
            use_amp=fps_amp,
        )

    params, trainable_params = count_parameters(model)
    flops = macs * 2

    macs_fmt, flops_fmt, params_fmt, thop_params_fmt = clever_format(
        [macs, flops, params, thop_params],
        "%.3f",
    )
    _, _, trainable_fmt = clever_format(
        [macs, flops, trainable_params],
        "%.3f",
    )

    print("=" * 80)
    print(f"Config: {config_path}")
    print(f"Name: {cfg.name}")
    print(f"Architecture: {cfg.architecture}")
    print(f"Backbone: {cfg.backbone}")
    print(f"Input: {batch_size} x 3 x {cfg.img_size} x {cfg.img_size}")
    print(f"Device: {device}")
    print("-" * 80)
    print(f"MACs: {macs_fmt}")
    print(f"FLOPs: {flops_fmt}  (reported as 2 x MACs)")
    print(f"Params: {params_fmt}")
    print(f"Trainable Params: {trainable_fmt}")
    print(f"THOP Params: {thop_params_fmt}")
    if fps_stats is not None:
        print("-" * 80)
        print(
            f"FPS: {fps_stats['fps']:.2f} images/s "
            f"(warmup={fps_stats['warmup']}, repeats={fps_stats['repeats']}, "
            f"amp={fps_stats['use_amp']})"
        )
        print(f"Latency: {fps_stats['ms_per_image']:.3f} ms/image")
        print(f"Batch Latency: {fps_stats['ms_per_batch']:.3f} ms/batch")
    print("=" * 80)

    result = {
        "config": str(config_path),
        "name": cfg.name,
        "architecture": cfg.architecture,
        "backbone": cfg.backbone,
        "input_size": cfg.img_size,
        "batch_size": batch_size,
        "macs": macs,
        "flops": flops,
        "params": params,
        "trainable_params": trainable_params,
        "thop_params": thop_params,
    }
    if fps_stats is not None:
        result.update(fps_stats)
    return result


def parse_args():
    parser = argparse.ArgumentParser(
        description="Profile model MACs/FLOPs, parameter count, and inference FPS."
    )
    parser.add_argument(
        "-c",
        "--config",
        nargs="+",
        required=True,
        help="One or more config YAML paths.",
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=1,
        help="Dummy input batch size for profiling.",
    )
    parser.add_argument(
        "--device",
        default=None,
        help="Profiling device, e.g. cuda:0 or cpu. Default: cuda:0 if available else cpu.",
    )
    parser.add_argument(
        "--skip_fps",
        action="store_true",
        help="Only report MACs/FLOPs/params and skip the FPS benchmark.",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=20,
        help="Warmup forward passes before measuring FPS.",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=100,
        help="Measured forward passes for FPS benchmarking.",
    )
    parser.add_argument(
        "--fps_amp",
        action="store_true",
        help="Use CUDA fp16 autocast during FPS benchmarking. FLOPs/params remain unchanged.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    for config_path in args.config:
        path = Path(config_path)
        if not path.is_file():
            raise FileNotFoundError(f"Config not found: {config_path}")
        profile_one(
            path,
            batch_size=args.batch_size,
            device=args.device,
            benchmark=not args.skip_fps,
            warmup=args.warmup,
            repeats=args.repeats,
            fps_amp=args.fps_amp,
        )


if __name__ == "__main__":
    main()
