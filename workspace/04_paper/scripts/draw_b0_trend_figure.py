#!/usr/bin/env python3
"""Draw the external B0 COD10K intermediate trend figure.

The B0 branch is dirty-tree observation only. This figure is an engineering
route artifact, not a main-table result.
"""

from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WORKSPACE = Path("/root/data-tmp/workspace")
RESULT_CSV = Path("/root/data-tmp/results_train/pvt_v2_b0/result.txt")
FIG_DIR = WORKSPACE / "04_paper" / "figures"
OUT_MD = WORKSPACE / "04_paper" / "drafts" / "b0_cod10k_trend_note.md"
OUT_FIG = FIG_DIR / "b0_cod10k_intermediate_trend.png"

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

LIGHT_COD10K = {
    "Smeasure": 0.866,
    "wFmeasure": 0.782,
    "meanFm": 0.808,
    "meanEm": 0.928,
    "MAE": 0.024,
}


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def read_rows() -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    with RESULT_CSV.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            rows.append(
                {
                    "epoch": float(row["epoch"]),
                    "Smeasure": float(row["Smeasure"]),
                    "wFmeasure": float(row["wFmeasure"]),
                    "meanFm": float(row["meanFm"]),
                    "meanEm": float(row["meanEm"]),
                    "MAE": float(row["MAE"]),
                }
            )
    if not rows:
        raise SystemExit(f"No B0 result rows found in {RESULT_CSV}")
    return rows


def scale(value: float, src_min: float, src_max: float, dst_min: float, dst_max: float) -> float:
    if src_max == src_min:
        return (dst_min + dst_max) / 2
    return dst_min + (value - src_min) / (src_max - src_min) * (dst_max - dst_min)


def draw_line_chart(draw: ImageDraw.ImageDraw, box, rows, key, title, color, higher_better=True):
    x1, y1, x2, y2 = box
    plot_top = y1 + 58
    plot_bottom = y2 - 30
    draw.rectangle(box, outline=(98, 112, 122), width=2)
    for i in range(1, 4):
        y = plot_top + (plot_bottom - plot_top) * i / 4
        draw.line([(x1, y), (x2, y)], fill=(226, 231, 235), width=1)

    epochs = [row["epoch"] for row in rows]
    values = [row[key] for row in rows]
    pad = 0.01 if key != "MAE" else 0.004
    v_min = min(values + [LIGHT_COD10K[key]]) - pad
    v_max = max(values + [LIGHT_COD10K[key]]) + pad

    points = []
    for row in rows:
        px = scale(row["epoch"], min(epochs), max(epochs), x1 + 32, x2 - 24)
        py = scale(row[key], v_min, v_max, plot_bottom, plot_top)
        points.append((px, py))
    for left, right in zip(points, points[1:]):
        draw.line([left, right], fill=color, width=4)
    for (px, py), row in zip(points, rows):
        draw.ellipse((px - 6, py - 6, px + 6, py + 6), fill=color, outline=(20, 28, 34), width=1)
        if int(row["epoch"]) in {40, 70}:
            draw.text((px - 18, py - 28), f"{row[key]:.4f}", font=font(13, True), fill=color)

    light_y = scale(LIGHT_COD10K[key], v_min, v_max, plot_bottom, plot_top)
    dash_color = (76, 117, 98)
    x = x1
    while x < x2:
        draw.line([(x, light_y), (min(x + 12, x2), light_y)], fill=dash_color, width=2)
        x += 22
    label_y = light_y - 24
    if label_y < y1 + 34:
        label_y = light_y + 8
    if label_y > y2 - 24:
        label_y = light_y - 30
    label_y = max(y1 + 34, min(label_y, y2 - 30))
    draw.text((x1 + 12, label_y), f"Light B2-C64 {LIGHT_COD10K[key]:.3f}", font=font(13, True), fill=dash_color)

    draw.text((x1 + 8, y1 + 6), title, font=font(18, True), fill=(32, 42, 50))
    arrow = "higher better" if higher_better else "lower better"
    draw.text((x2 - 120, y1 + 9), arrow, font=font(12), fill=(92, 104, 112))
    for epoch in [10, 30, 50, 70]:
        px = scale(epoch, min(epochs), max(epochs), x1 + 32, x2 - 24)
        draw.text((px - 10, y2 + 8), str(epoch), font=font(12), fill=(68, 80, 90))


def draw_figure(rows: list[dict[str, float]]) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    width, height = 1450, 980
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    draw.text((56, 34), "External B0 COD10K Intermediate Trend", font=font(34, True), fill=(24, 34, 42))
    draw.text(
        (58, 82),
        "Dirty-tree observation only. Dashed line is accepted Light-B2-C64 COD10K evidence.",
        font=font(20),
        fill=(84, 96, 106),
    )

    boxes = [
        (80, 155, 680, 405),
        (770, 155, 1370, 405),
        (80, 500, 680, 750),
        (770, 500, 1370, 750),
    ]
    draw_line_chart(draw, boxes[0], rows, "Smeasure", "S-measure", (43, 103, 164), True)
    draw_line_chart(draw, boxes[1], rows, "wFmeasure", "weighted F-measure", (137, 92, 36), True)
    draw_line_chart(draw, boxes[2], rows, "meanEm", "mean E-measure", (112, 78, 154), True)
    draw_line_chart(draw, boxes[3], rows, "MAE", "MAE", (190, 79, 73), False)

    latest = max(rows, key=lambda item: item["epoch"])
    best_s = max(rows, key=lambda item: item["Smeasure"])
    best_mae = min(rows, key=lambda item: item["MAE"])
    summary_top = (
        f"Latest completed row: epoch {int(latest['epoch'])}, "
        f"S={latest['Smeasure']:.4f}, wF={latest['wFmeasure']:.4f}, "
        f"mE={latest['meanEm']:.4f}, MAE={latest['MAE']:.4f}."
    )
    summary_bottom = (
        f"Best S is epoch {int(best_s['epoch'])}; best MAE is epoch {int(best_mae['epoch'])}."
    )
    draw.rounded_rectangle((80, 825, 1370, 925), radius=10, fill=(247, 249, 250), outline=(204, 214, 222), width=2)
    draw.text((105, 842), summary_top, font=font(19, True), fill=(34, 45, 52))
    draw.text((105, 870), summary_bottom, font=font(18, True), fill=(34, 45, 52))
    draw.text(
        (105, 898),
        "Route decision: useful as risk evidence, not as a final paper result before checkpoint/profile/three-dataset gates.",
        font=font(17),
        fill=(84, 96, 106),
    )
    tmp_fig = OUT_FIG.with_name(f"{OUT_FIG.stem}.tmp{OUT_FIG.suffix}")
    img.save(tmp_fig)
    tmp_fig.replace(OUT_FIG)


def write_note(rows: list[dict[str, float]]) -> None:
    latest = max(rows, key=lambda item: item["epoch"])
    best_s = max(rows, key=lambda item: item["Smeasure"])
    best_mae = min(rows, key=lambda item: item["MAE"])
    lines = [
        "# B0 COD10K Trend Note",
        "",
        "This note summarizes the external dirty-tree PVTv2-B0 online KD branch.",
        "It is observation evidence only and must not enter the main table, abstract or conclusion.",
        "",
        f"- Source CSV: `{RESULT_CSV}`",
        f"- Figure: `{OUT_FIG}`",
        f"- Latest completed row: epoch {int(latest['epoch'])}, S={latest['Smeasure']:.4f}, "
        f"wF={latest['wFmeasure']:.4f}, meanF={latest['meanFm']:.4f}, "
        f"meanE={latest['meanEm']:.4f}, MAE={latest['MAE']:.4f}",
        f"- Best B0 S row: epoch {int(best_s['epoch'])}, S={best_s['Smeasure']:.4f}",
        f"- Best B0 MAE row: epoch {int(best_mae['epoch'])}, MAE={best_mae['MAE']:.4f}",
        "- Accepted Light-B2-C64 COD10K reference: S=.866, wF=.782, meanF=.808, meanE=.928, MAE=.024",
        "",
        "## Rows",
        "",
        "| epoch | S | wF | meanF | meanE | MAE |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {int(row['epoch'])} | {row['Smeasure']:.4f} | {row['wFmeasure']:.4f} | "
            f"{row['meanFm']:.4f} | {row['meanEm']:.4f} | {row['MAE']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Dirty `/root/ESCNet` branch.",
            "- COD10K-only intermediate evaluation.",
            "- No accepted checkpoint load/profile or CAMO/COD10K/NC4K probability evaluation.",
            "- Use only as engineering risk evidence or appendix material after Gate 4A.",
        ]
    )
    tmp_md = OUT_MD.with_name(f"{OUT_MD.stem}.tmp{OUT_MD.suffix}")
    tmp_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    tmp_md.replace(OUT_MD)


def main() -> int:
    rows = read_rows()
    draw_figure(rows)
    write_note(rows)
    print(f"figure={OUT_FIG}")
    print(f"note={OUT_MD}")
    print(f"rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
