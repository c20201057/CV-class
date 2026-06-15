#!/usr/bin/env python3
"""Create aligned visual grids for COD predictions."""

from __future__ import annotations

import argparse
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}


def parse_pred(raw: str) -> tuple[str, Path]:
    if "=" not in raw:
        raise argparse.ArgumentTypeError("--pred must be NAME=DIR")
    name, path = raw.split("=", 1)
    name = name.strip()
    if not name:
        raise argparse.ArgumentTypeError("Prediction column name cannot be empty")
    return name, Path(path).expanduser()


def list_by_stem(root: Path) -> dict[str, Path]:
    files = {}
    for path in sorted(root.iterdir()):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTS:
            files[path.stem] = path
    return files


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def fit_image(path: Path, size: int, rgb: bool) -> Image.Image:
    mode = "RGB" if rgb else "L"
    image = Image.open(path).convert(mode)
    image.thumbnail((size, size), Image.Resampling.BILINEAR)
    canvas = Image.new("RGB", (size, size), "white")
    if not rgb:
        image = image.convert("RGB")
    offset = ((size - image.width) // 2, (size - image.height) // 2)
    canvas.paste(image, offset)
    return canvas


def draw_label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font) -> None:
    draw.text(xy, text, fill=(20, 20, 20), font=font)


def main() -> None:
    parser = argparse.ArgumentParser(description="Make paper-ready visual grids.")
    parser.add_argument("--image_dir", required=True, help="Dataset Image directory.")
    parser.add_argument("--gt_dir", required=True, help="Dataset GT_Object directory.")
    parser.add_argument(
        "--pred",
        action="append",
        type=parse_pred,
        default=[],
        help="Prediction column as NAME=DIR. Can be repeated.",
    )
    parser.add_argument("--out", required=True, help="Output PNG path.")
    parser.add_argument("--samples", type=int, default=6)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--cell", type=int, default=192)
    parser.add_argument("--label_h", type=int, default=30)
    parser.add_argument(
        "--sample_names",
        default="",
        help="Comma/space separated stems to use instead of random sampling.",
    )
    args = parser.parse_args()

    image_dir = Path(args.image_dir).expanduser()
    gt_dir = Path(args.gt_dir).expanduser()
    out_path = Path(args.out).expanduser()
    for required in [image_dir, gt_dir, *[path for _, path in args.pred]]:
        if not required.is_dir():
            raise FileNotFoundError(required)

    images = list_by_stem(image_dir)
    gts = list_by_stem(gt_dir)
    preds = [(name, list_by_stem(path)) for name, path in args.pred]

    common = set(images) & set(gts)
    for _, pred_files in preds:
        common &= set(pred_files)
    common_names = sorted(common)
    if not common_names:
        raise ValueError("No aligned sample names found across image/GT/pred dirs")

    requested = [
        item.strip()
        for item in args.sample_names.replace(",", " ").split()
        if item.strip()
    ]
    if requested:
        missing = [name for name in requested if name not in common]
        if missing:
            raise ValueError(f"Requested sample names missing: {missing}")
        sample_names = requested[: args.samples]
    else:
        rng = random.Random(args.seed)
        sample_names = common_names.copy()
        rng.shuffle(sample_names)
        sample_names = sample_names[: args.samples]

    headers = ["Image", "GT"] + [name for name, _ in preds]
    rows = len(sample_names)
    cols = len(headers)
    width = cols * args.cell
    height = args.label_h + rows * (args.cell + args.label_h)
    grid = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(grid)
    header_font = load_font(18)
    name_font = load_font(14)

    for col, header in enumerate(headers):
        draw_label(draw, (col * args.cell + 8, 6), header, header_font)

    for row, stem in enumerate(sample_names):
        label_y = args.label_h + row * (args.cell + args.label_h)
        y = label_y + args.label_h
        draw.rectangle((0, label_y, width, label_y + args.label_h), fill=(248, 248, 248))
        draw_label(draw, (8, label_y + 6), stem, name_font)

        cells = [
            fit_image(images[stem], args.cell, rgb=True),
            fit_image(gts[stem], args.cell, rgb=False),
        ]
        cells.extend(fit_image(pred_files[stem], args.cell, rgb=False) for _, pred_files in preds)
        for col, cell in enumerate(cells):
            grid.paste(cell, (col * args.cell, y))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    grid.save(out_path)
    print(
        {
            "out": str(out_path),
            "samples": sample_names,
            "columns": headers,
            "size": grid.size,
        }
    )


if __name__ == "__main__":
    main()
