#!/usr/bin/env python3
"""Save ESCNet sigmoid probability masks without thresholding.

The output layout is compatible with ESCNet/eval.py:

    <pred_root>/<method>/<gt_filename>.png
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from tqdm import tqdm


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ESCNet probability-map inference for COD-style test sets."
    )
    parser.add_argument("--repo", required=True, help="Path to the ESCNet repository.")
    parser.add_argument("--config", required=True, help="Path to ESCNet YAML config.")
    parser.add_argument("--ckpt", required=True, help="Path to ESCNet checkpoint.")
    parser.add_argument(
        "--pred_root",
        required=True,
        help="Prediction root. Outputs are written to pred_root/method/*.png.",
    )
    parser.add_argument(
        "--device",
        default="cuda:0",
        help="Device for inference, e.g. cuda:0, 0, cuda, or cpu.",
    )
    parser.add_argument(
        "--batch_size_valid",
        type=int,
        default=None,
        help="Override config.batch_size_valid for inference.",
    )
    parser.add_argument(
        "--method",
        default=None,
        help="Method subdirectory under pred_root. Defaults to checkpoint stem.",
    )
    return parser.parse_args()


def add_repo_to_path(repo: Path) -> None:
    repo = repo.resolve()
    if not repo.is_dir():
        raise FileNotFoundError(f"ESCNet repo does not exist: {repo}")
    sys.path.insert(0, str(repo))


def normalize_device(device_arg: str) -> torch.device:
    if device_arg.isdigit():
        device_arg = f"cuda:{device_arg}"
    device = torch.device(device_arg)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError(f"CUDA device requested but CUDA is unavailable: {device_arg}")
    return device


def checkpoint_to_method(ckpt: Path) -> str:
    return ckpt.name[:-4] if ckpt.name.endswith(".pth") else ckpt.stem


def load_state_dict(ckpt: Path, device: torch.device) -> dict:
    try:
        state_dict = torch.load(ckpt, map_location=device, weights_only=True)
    except TypeError:
        state_dict = torch.load(ckpt, map_location=device)
    if not isinstance(state_dict, dict):
        raise TypeError(f"Checkpoint did not load to a state dict: {ckpt}")
    return state_dict


def gt_size(label_path: str) -> tuple[int, int]:
    label = cv2.imread(label_path, cv2.IMREAD_GRAYSCALE)
    if label is None:
        raise FileNotFoundError(f"Could not read GT mask: {label_path}")
    return label.shape[:2]


def save_prob_png(prob: torch.Tensor, path: Path) -> None:
    array = prob.detach().cpu().squeeze().clamp(0, 1).numpy()
    array_u8 = np.rint(array * 255.0).astype(np.uint8)
    Image.fromarray(array_u8, mode="L").save(path)


def infer(
    model: torch.nn.Module,
    data_loader: Iterable,
    pred_dir: Path,
    device: torch.device,
) -> int:
    model.eval()
    pred_dir.mkdir(parents=True, exist_ok=True)
    n_saved = 0

    with torch.no_grad():
        for batch in tqdm(data_loader, total=len(data_loader), desc="infer_prob"):
            inputs = batch[0].to(device, non_blocking=True)
            label_paths = batch[-1]

            _, scaled_preds = model(inputs)
            probs = scaled_preds[-1].sigmoid()

            for idx_sample, label_path in enumerate(label_paths):
                height, width = gt_size(label_path)
                resized = F.interpolate(
                    probs[idx_sample].unsqueeze(0),
                    size=(height, width),
                    mode="bilinear",
                    align_corners=False,
                )
                out_path = pred_dir / Path(label_path).name
                save_prob_png(resized, out_path)
                n_saved += 1

    return n_saved


def main() -> None:
    args = parse_args()
    repo = Path(args.repo)
    config_path = Path(args.config)
    ckpt = Path(args.ckpt)
    pred_root = Path(args.pred_root)
    method = args.method or checkpoint_to_method(ckpt)

    add_repo_to_path(repo)

    from config import load_config
    from dataset import MyData
    from models.ESCNet import ESCNet
    from utils import check_state_dict

    if args.batch_size_valid is not None and args.batch_size_valid <= 0:
        raise ValueError("--batch_size_valid must be positive when provided.")

    device = normalize_device(args.device)
    config = load_config(str(config_path))
    if args.batch_size_valid is not None:
        config = config.model_copy(update={"batch_size_valid": args.batch_size_valid})

    if config.precisionHigh:
        torch.set_float32_matmul_precision("high")

    model = ESCNet(config, pretrained=False).to(device)
    state_dict = check_state_dict(load_state_dict(ckpt, device))
    model.load_state_dict(state_dict)

    data_loader = torch.utils.data.DataLoader(
        dataset=MyData(config, config.test_dir, image_size=config.img_size, is_train=False),
        batch_size=config.batch_size_valid,
        shuffle=False,
        num_workers=config.num_workers,
        pin_memory=(device.type == "cuda"),
    )

    pred_dir = pred_root / method
    n_saved = infer(model, data_loader, pred_dir, device)
    print(f"Saved {n_saved} probability PNGs to {pred_dir}")


if __name__ == "__main__":
    main()
