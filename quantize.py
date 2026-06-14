import argparse
import os
from pathlib import Path

import torch

from config import load_config
from models.ESCNet import ESCNet
from utils import check_state_dict


def parse_args():
    parser = argparse.ArgumentParser(description="Quantize ESCNet checkpoints.")
    parser.add_argument("--config", default="config.yaml", help="Path to config file.")
    parser.add_argument(
        "--ckpt",
        required=True,
        help="Float checkpoint to quantize, e.g. checkpoints/escnet/epoch_120.pth.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output path for the quantized model, e.g. /root/data-tmp/escnet_runs/quantized/escnet_dynamic.pt.",
    )
    parser.add_argument(
        "--mode",
        default="dynamic",
        choices=["dynamic"],
        help="Quantization mode. The first experiment supports dynamic quantization.",
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Run a dummy forward pass before saving.",
    )
    return parser.parse_args()


def load_float_model(config_path, ckpt_path):
    config = load_config(config_path)
    model = ESCNet(config, pretrained=False).cpu().eval()
    state_dict = torch.load(ckpt_path, map_location="cpu", weights_only=True)
    model.load_state_dict(check_state_dict(state_dict))
    return model, config


def quantize_dynamic(model):
    return torch.quantization.quantize_dynamic(
        model,
        {torch.nn.Linear},
        dtype=torch.qint8,
    )


def smoke_test(model, image_size):
    with torch.no_grad():
        dummy = torch.randn(1, 3, image_size, image_size)
        out_edge, out_masks = model(dummy)
    print(f"smoke out_edge: {tuple(out_edge.shape)}")
    print("smoke out_masks:", [tuple(mask.shape) for mask in out_masks])


def main():
    args = parse_args()
    model, config = load_float_model(args.config, args.ckpt)

    if args.mode == "dynamic":
        quantized_model = quantize_dynamic(model)
    else:
        raise ValueError(f"Unsupported mode: {args.mode}")

    if args.smoke_test:
        smoke_test(quantized_model, config.img_size)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "mode": args.mode,
            "config": args.config,
            "source_ckpt": os.path.abspath(args.ckpt),
            "model": quantized_model,
        },
        output_path,
    )
    print(f"Saved quantized model to {output_path}")


if __name__ == "__main__":
    main()
