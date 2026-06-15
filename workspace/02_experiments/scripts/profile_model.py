#!/usr/bin/env python3
"""Profile ESCNet-style segmentation models for paper efficiency tables."""

from __future__ import annotations

import argparse
import csv
import importlib
import json
import os
import platform
import sys
import time
from collections import OrderedDict
from contextlib import nullcontext
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
sys.dont_write_bytecode = True

import torch
import yaml


DEFAULT_CSV = Path("/root/data-tmp/workspace/02_experiments/tables/profiles.csv")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Profile an ESCNet checkpoint.")
    parser.add_argument("--repo", required=True, help="Path to ESCNet repository.")
    parser.add_argument("--config", required=True, help="Path to config YAML.")
    parser.add_argument("--ckpt", default="", help="Optional checkpoint path.")
    parser.add_argument("--out", required=True, help="Output profile JSON path.")
    parser.add_argument("--device", default="cuda:0", help="Device, e.g. cuda:0 or cpu.")
    parser.add_argument("--warmup", type=int, default=20, help="Warmup forward passes.")
    parser.add_argument("--repeat", type=int, default=50, help="Timed forward passes.")
    parser.add_argument(
        "--profiles-csv",
        default=str(DEFAULT_CSV),
        help="CSV table to update with the profile row.",
    )
    parser.add_argument(
        "--exp-id",
        default="",
        help="Experiment id for CSV/JSON. Defaults to output directory name.",
    )
    return parser.parse_args()


def read_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Config did not parse to a mapping: {path}")
    return data


def import_from_repo(repo: Path, config_path: Path) -> Tuple[Any, Any]:
    repo = repo.resolve()
    config_path = config_path.resolve()
    sys.path.insert(0, str(repo))
    old_cwd = Path.cwd()
    os.chdir(repo)
    try:
        config_mod = importlib.import_module("config")
        escnet_mod = importlib.import_module("models.ESCNet")
        config = config_mod.load_config(str(config_path))
        return config, escnet_mod.ESCNet
    finally:
        os.chdir(old_cwd)


def resolve_device(device_arg: str) -> Tuple[torch.device, str, Optional[str]]:
    requested = device_arg
    if requested.startswith("cuda") and not torch.cuda.is_available():
        return torch.device("cpu"), requested, "CUDA requested but torch.cuda.is_available() is False; fell back to CPU."
    device = torch.device(requested)
    if device.type == "cuda":
        if device.index is not None and device.index >= torch.cuda.device_count():
            return torch.device("cpu"), requested, f"CUDA device {requested} is unavailable; fell back to CPU."
    return device, requested, None


def clean_state_dict(state: Any) -> OrderedDict:
    if isinstance(state, dict):
        for key in ("state_dict", "model", "model_state_dict", "net"):
            if key in state and isinstance(state[key], dict):
                state = state[key]
                break
    if not isinstance(state, dict):
        raise TypeError(f"Checkpoint did not contain a state_dict-like mapping: {type(state)!r}")

    cleaned = OrderedDict()
    for key, value in state.items():
        new_key = str(key)
        for prefix in ("module.", "_orig_mod."):
            if new_key.startswith(prefix):
                new_key = new_key[len(prefix) :]
        cleaned[new_key] = value
    return cleaned


def load_checkpoint(model: torch.nn.Module, ckpt_path: Path, device: torch.device) -> Dict[str, Any]:
    raw = torch.load(str(ckpt_path), map_location=device, weights_only=True)
    state_dict = clean_state_dict(raw)
    incompatible = model.load_state_dict(state_dict, strict=False)
    missing = list(incompatible.missing_keys)
    unexpected = list(incompatible.unexpected_keys)
    status = "loaded" if not missing and not unexpected else "loaded_non_strict"
    return {
        "status": status,
        "path": str(ckpt_path),
        "missing_keys_count": len(missing),
        "unexpected_keys_count": len(unexpected),
        "missing_keys_sample": missing[:20],
        "unexpected_keys_sample": unexpected[:20],
    }


def count_params(model: torch.nn.Module) -> Tuple[int, int]:
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return int(total), int(trainable)


def model_size_mb(model: torch.nn.Module) -> float:
    bytes_total = 0
    for tensor in list(model.parameters()) + list(model.buffers()):
        bytes_total += tensor.numel() * tensor.element_size()
    return bytes_total / (1024**2)


def output_summary(output: Any) -> Any:
    if isinstance(output, torch.Tensor):
        return {"type": "Tensor", "shape": list(output.shape), "dtype": str(output.dtype)}
    if isinstance(output, (list, tuple)):
        return [output_summary(item) for item in output]
    if isinstance(output, dict):
        return {str(k): output_summary(v) for k, v in output.items()}
    return {"type": type(output).__name__}


def synchronize(device: torch.device) -> None:
    if device.type == "cuda":
        torch.cuda.synchronize(device)


def timed_latency(
    model: torch.nn.Module,
    sample: torch.Tensor,
    device: torch.device,
    warmup: int,
    repeat: int,
) -> Tuple[float, float, Any]:
    if warmup < 0 or repeat <= 0:
        raise ValueError("--warmup must be >= 0 and --repeat must be > 0")

    ctx = torch.inference_mode()
    with ctx:
        last_output = None
        for _ in range(warmup):
            last_output = model(sample)
        synchronize(device)

        if device.type == "cuda":
            starter = torch.cuda.Event(enable_timing=True)
            ender = torch.cuda.Event(enable_timing=True)
            timings = []
            for _ in range(repeat):
                starter.record()
                last_output = model(sample)
                ender.record()
                torch.cuda.synchronize(device)
                timings.append(starter.elapsed_time(ender))
            latency_ms = float(sum(timings) / len(timings))
        else:
            timings = []
            for _ in range(repeat):
                start = time.perf_counter()
                last_output = model(sample)
                timings.append((time.perf_counter() - start) * 1000.0)
            latency_ms = float(sum(timings) / len(timings))

    fps = 1000.0 / latency_ms if latency_ms > 0 else 0.0
    return latency_ms, fps, last_output


def peak_memory_mb(device: torch.device) -> Optional[float]:
    if device.type != "cuda":
        return None
    return float(torch.cuda.max_memory_allocated(device) / (1024**2))


def profile_flops_with_torch_profiler(
    model: torch.nn.Module,
    sample: torch.Tensor,
    device: torch.device,
) -> Dict[str, Any]:
    try:
        activities = [torch.profiler.ProfilerActivity.CPU]
        if device.type == "cuda":
            activities.append(torch.profiler.ProfilerActivity.CUDA)
        synchronize(device)
        with torch.inference_mode():
            with torch.profiler.profile(activities=activities, with_flops=True) as prof:
                model(sample)
        synchronize(device)

        total_flops = 0
        for event in prof.key_averages():
            flops = getattr(event, "flops", 0)
            if flops:
                total_flops += int(flops)

        if total_flops <= 0:
            return {
                "flops_status": "unavailable",
                "flops_error": "torch.profiler with_flops produced zero FLOPs; likely unsupported operators dominate or this build does not expose FLOPs.",
                "flops_method": "torch.profiler.profile(with_flops=True)",
            }

        return {
            "flops_status": "estimated",
            "flops": int(total_flops),
            "flops_g": float(total_flops / 1e9),
            "gmacs": float(total_flops / 2e9),
            "flops_method": "torch.profiler.profile(with_flops=True)",
            "flops_note": "PyTorch profiler estimates FLOPs for supported ops such as conv/matmul; unsupported ops are not included.",
        }
    except Exception as exc:  # noqa: BLE001 - profiling must record failure instead of hiding it.
        return {
            "flops_status": "unavailable",
            "flops_error": f"{type(exc).__name__}: {exc}",
            "flops_method": "torch.profiler.profile(with_flops=True)",
        }


def installed_flops_packages() -> Dict[str, bool]:
    packages = {}
    for name in ("thop", "ptflops", "fvcore"):
        try:
            importlib.import_module(name)
            packages[name] = True
        except Exception:
            packages[name] = False
    return packages


def maybe_set_precision(config: Any) -> None:
    if bool(getattr(config, "precisionHigh", False)) and hasattr(torch, "set_float32_matmul_precision"):
        torch.set_float32_matmul_precision("high")


def update_profiles_csv(csv_path: Path, row: Dict[str, Any]) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    preferred = [
        "exp_id",
        "model",
        "backbone",
        "inter_channel",
        "params",
        "trainable_params",
        "model_size_mb",
        "flops_g",
        "gmacs",
        "flops_gmacs",
        "flops_status",
        "latency_ms",
        "fps",
        "peak_mem_mb",
        "device",
        "img_size",
        "warmup",
        "repeat",
        "checkpoint_status",
        "source",
        "profile_json",
    ]

    rows = []
    existing_fields = []
    if csv_path.exists() and csv_path.stat().st_size > 0:
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            existing_fields = list(reader.fieldnames or [])
            rows = list(reader)

    fields = []
    for field in preferred + existing_fields + list(row.keys()):
        if field not in fields:
            fields.append(field)

    replaced = False
    for existing in rows:
        if existing.get("exp_id") == row.get("exp_id"):
            existing.update({k: "" if v is None else v for k, v in row.items()})
            replaced = True
            break
    if not replaced:
        rows.append({k: "" if v is None else v for k, v in row.items()})

    tmp_path = csv_path.with_suffix(csv_path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for existing in rows:
            writer.writerow({field: existing.get(field, "") for field in fields})
    tmp_path.replace(csv_path)


def round_or_none(value: Optional[float], digits: int = 4) -> Optional[float]:
    if value is None:
        return None
    return round(float(value), digits)


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).resolve()
    config_path = Path(args.config).resolve()
    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    command = " ".join([Path(sys.executable).name] + sys.argv)
    config_dict = read_yaml(config_path)
    exp_id = args.exp_id or out_path.parent.name

    device, requested_device, device_warning = resolve_device(args.device)
    maybe_cuda_index = device.index if device.type == "cuda" else None
    if device.type == "cuda" and maybe_cuda_index is not None:
        torch.cuda.set_device(maybe_cuda_index)

    config, escnet_cls = import_from_repo(repo, config_path)
    maybe_set_precision(config)
    model = escnet_cls(config, pretrained=False)
    model.to(device)
    model.eval()

    ckpt_path = Path(args.ckpt).resolve() if args.ckpt else None
    if ckpt_path and ckpt_path.exists():
        checkpoint_info = load_checkpoint(model, ckpt_path, device)
    elif ckpt_path:
        checkpoint_info = {
            "status": "missing_random_init",
            "path": str(ckpt_path),
            "reason": "Checkpoint path was provided but does not exist; profiled randomly initialized weights.",
        }
    else:
        checkpoint_info = {
            "status": "random_init",
            "path": "",
            "reason": "No checkpoint path was provided; profiled randomly initialized weights.",
        }

    img_size = int(getattr(config, "img_size", config_dict.get("img_size", 416)))
    sample = torch.randn(1, 3, img_size, img_size, device=device)

    params, trainable_params = count_params(model)
    size_mb = model_size_mb(model)

    if device.type == "cuda":
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats(device)

    forward_status = "ok"
    forward_error = None
    latency_ms = None
    fps = None
    outputs = None
    try:
        latency_ms, fps, outputs = timed_latency(model, sample, device, args.warmup, args.repeat)
    except Exception as exc:  # noqa: BLE001 - record profile failure in JSON.
        forward_status = "failed"
        forward_error = f"{type(exc).__name__}: {exc}"

    mem_mb = peak_memory_mb(device)
    flops_info = profile_flops_with_torch_profiler(model, sample, device) if forward_status == "ok" else {
        "flops_status": "unavailable",
        "flops_error": "Forward profiling failed; FLOPs were not attempted.",
        "flops_method": "torch.profiler.profile(with_flops=True)",
    }

    cuda_name = torch.cuda.get_device_name(device) if device.type == "cuda" else None
    profile = {
        "exp_id": exp_id,
        "model": "ESCNet",
        "backbone": str(getattr(config, "backbone", config_dict.get("backbone", ""))),
        "inter_channel": int(getattr(config, "inter_channel", config_dict.get("inter_channel", 128))),
        "repo": str(repo),
        "config": str(config_path),
        "checkpoint": checkpoint_info,
        "command": command,
        "params": params,
        "trainable_params": trainable_params,
        "model_size_mb": round_or_none(size_mb, 4),
        "latency_ms": round_or_none(latency_ms, 4),
        "fps": round_or_none(fps, 4),
        "peak_mem_mb": round_or_none(mem_mb, 4),
        "device": str(device),
        "requested_device": requested_device,
        "device_name": cuda_name,
        "device_warning": device_warning,
        "torch_version": torch.__version__,
        "cuda_version": torch.version.cuda,
        "cudnn_version": torch.backends.cudnn.version(),
        "python_version": platform.python_version(),
        "img_size": img_size,
        "input_shape": [1, 3, img_size, img_size],
        "batch_size": 1,
        "warmup": args.warmup,
        "repeat": args.repeat,
        "forward_status": forward_status,
        "forward_error": forward_error,
        "output_summary": output_summary(outputs) if outputs is not None else None,
        "flops_packages": installed_flops_packages(),
        **flops_info,
    }

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, sort_keys=True)
        f.write("\n")

    csv_row = {
        "exp_id": exp_id,
        "model": profile["model"],
        "backbone": profile["backbone"],
        "inter_channel": profile["inter_channel"],
        "params": profile["params"],
        "trainable_params": profile["trainable_params"],
        "model_size_mb": profile["model_size_mb"],
        "flops_g": profile.get("flops_g"),
        "gmacs": profile.get("gmacs"),
        "flops_gmacs": profile.get("gmacs"),
        "flops_status": profile.get("flops_status"),
        "latency_ms": profile["latency_ms"],
        "fps": profile["fps"],
        "peak_mem_mb": profile["peak_mem_mb"],
        "device": profile["device"],
        "img_size": profile["img_size"],
        "warmup": profile["warmup"],
        "repeat": profile["repeat"],
        "checkpoint_status": checkpoint_info["status"],
        "source": "profile_model.py",
        "profile_json": str(out_path),
    }
    update_profiles_csv(Path(args.profiles_csv), csv_row)

    print(json.dumps(profile, indent=2, sort_keys=True))
    return 0 if forward_status == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
