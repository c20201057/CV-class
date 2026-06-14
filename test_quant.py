import argparse
import os
import time

import cv2
import torch
from tqdm import tqdm

from config import load_config
from dataset import MyData
from utils import save_tensor_img


def parse_args():
    parser = argparse.ArgumentParser(description="ESCNet quantized inference script.")
    parser.add_argument("--config", default="config.yaml", help="Path to config file.")
    parser.add_argument(
        "--model",
        required=True,
        help="Quantized model produced by quantize.py.",
    )
    parser.add_argument(
        "--pred_root",
        default="/root/data-tmp/escnet_runs/quant_preds",
        help="Prediction output root.",
    )
    parser.add_argument(
        "--method",
        default=None,
        help="Prediction subfolder name. Defaults to the quantized model stem.",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        choices=["cpu"],
        help="Dynamic quantized model is intended to run on CPU.",
    )
    return parser.parse_args()


def load_quantized_model(path):
    payload = torch.load(path, map_location="cpu", weights_only=False)
    if isinstance(payload, dict) and "model" in payload:
        model = payload["model"]
    else:
        model = payload
    return model.cpu().eval()


def inference(model, data_loader_test, pred_root, method):
    os.makedirs(os.path.join(pred_root, method), exist_ok=True)
    total_images = 0
    started_at = time.perf_counter()

    for batch in tqdm(data_loader_test, total=len(data_loader_test)):
        inputs = batch[0].cpu()
        label_paths = batch[-1]

        with torch.no_grad():
            out_edge, scaled_preds = model(inputs)

        pred_lvl = (scaled_preds[-1].sigmoid() >= 0.5).float()

        for idx_sample in range(pred_lvl.shape[0]):
            label_shape = cv2.imread(
                label_paths[idx_sample], cv2.IMREAD_GRAYSCALE
            ).shape[:2]
            res = torch.nn.functional.interpolate(
                pred_lvl[idx_sample].unsqueeze(0),
                size=label_shape,
                mode="bilinear",
                align_corners=True,
            )
            save_tensor_img(
                res,
                os.path.join(
                    pred_root,
                    method,
                    label_paths[idx_sample].replace("\\", "/").split("/")[-1],
                ),
            )
            total_images += 1

    elapsed = time.perf_counter() - started_at
    print(f"Saved {total_images} predictions to {os.path.join(pred_root, method)}")
    print(f"Total inference time: {elapsed:.2f}s")
    if total_images:
        print(f"Average time per image: {elapsed / total_images:.4f}s")


def main():
    args = parse_args()
    config = load_config(args.config)
    method = args.method or os.path.splitext(os.path.basename(args.model))[0]
    model = load_quantized_model(args.model)

    data_loader_test = torch.utils.data.DataLoader(
        dataset=MyData(config, config.test_dir, image_size=config.img_size, is_train=False),
        batch_size=config.batch_size_valid,
        shuffle=False,
        num_workers=config.num_workers,
        pin_memory=False,
    )

    inference(model, data_loader_test, args.pred_root, method)


if __name__ == "__main__":
    main()
