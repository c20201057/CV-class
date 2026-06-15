#!/usr/bin/env python3
"""Draw paper figures for Light-ESCNet B2-C64 without extra plotting deps."""

from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/root/data-tmp/workspace")
FIG_DIR = ROOT / "04_paper" / "figures"
METRICS_CSV = ROOT / "02_experiments" / "tables" / "metrics_all.csv"
PROFILES_CSV = ROOT / "02_experiments" / "tables" / "profiles.csv"
HISTORICAL_BASELINE_EXP = "baseline_escnet_b5_416_e120"
CLEAN_BASELINE_EXP = "baseline_escnet_b5_clean_prob_e120"
LIGHT_EXP = "light_b2_c64_e120_s42_prob_eval_v2"

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def rounded_box(draw: ImageDraw.ImageDraw, xy, fill, outline, width=2, radius=16):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def center_text(draw: ImageDraw.ImageDraw, box, text, fnt, fill=(28, 34, 38), spacing=5):
    x1, y1, x2, y2 = box
    lines = text.split("\n")
    heights = []
    widths = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=fnt)
        widths.append(bbox[2] - bbox[0])
        heights.append(bbox[3] - bbox[1])
    total_h = sum(heights) + spacing * (len(lines) - 1)
    y = y1 + ((y2 - y1) - total_h) / 2
    for line, w, h in zip(lines, widths, heights):
        draw.text((x1 + ((x2 - x1) - w) / 2, y), line, font=fnt, fill=fill)
        y += h + spacing


def arrow(draw: ImageDraw.ImageDraw, start, end, fill=(58, 74, 86), width=4):
    draw.line([start, end], fill=fill, width=width)
    sx, sy = start
    ex, ey = end
    if abs(ex - sx) >= abs(ey - sy):
        sign = 1 if ex >= sx else -1
        pts = [(ex, ey), (ex - sign * 14, ey - 8), (ex - sign * 14, ey + 8)]
    else:
        sign = 1 if ey >= sy else -1
        pts = [(ex, ey), (ex - 8, ey - sign * 14), (ex + 8, ey - sign * 14)]
    draw.polygon(pts, fill=fill)


def draw_method_figure():
    metrics = read_metrics()
    reference_exp = choose_baseline_exp(metrics)
    avg_s_ref = avg_metric(metrics, reference_exp, "Smeasure")
    avg_s_light = avg_metric(metrics, LIGHT_EXP, "Smeasure")
    avg_mae_ref = avg_metric(metrics, reference_exp, "MAE")
    avg_mae_light = avg_metric(metrics, LIGHT_EXP, "MAE")

    W, H = 1800, 1050
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)

    title = "Light-ESCNet B2-C64: lightweight edge-semantic collaboration"
    d.text((70, 42), title, font=font(36, True), fill=(23, 32, 38))
    d.text(
        (72, 92),
        "B2 compresses the encoder; C64 narrows AETP/FEM/MTA/heads while preserving edge-guided decoding.",
        font=font(22),
        fill=(82, 94, 104),
    )

    colors = {
        "input": (245, 247, 249),
        "encoder": (232, 243, 250),
        "proj": (235, 247, 241),
        "edge": (255, 244, 226),
        "decoder": (239, 238, 250),
        "mask": (232, 247, 246),
        "border": (76, 91, 102),
    }

    # Main pipeline boxes.
    boxes = {
        "input": (70, 210, 300, 360),
        "encoder": (390, 180, 720, 390),
        "proj": (820, 180, 1130, 390),
        "decoder": (1240, 590, 1610, 810),
        "masks": (1670, 620, 1770, 780),
    }
    rounded_box(d, boxes["input"], colors["input"], colors["border"])
    center_text(d, boxes["input"], "Input\nimage", font(25, True))

    rounded_box(d, boxes["encoder"], colors["encoder"], colors["border"])
    center_text(d, boxes["encoder"], "PVTv2-B2\nencoder\nF1, F2, F3, F4", font(25, True))
    d.text((405, 402), "Backbone: B5 -> B2", font=font(19, True), fill=(18, 111, 150))

    rounded_box(d, boxes["proj"], colors["proj"], colors["border"])
    center_text(d, boxes["proj"], "1x1 projection\nall levels -> 64 ch\nX1, X2, X3, X4", font(24, True))
    d.text((835, 402), "Width: C128 -> C64", font=font(19, True), fill=(31, 124, 74))

    # Edge branch.
    edge_box = (1240, 180, 1610, 405)
    rounded_box(d, edge_box, colors["edge"], colors["border"])
    center_text(d, edge_box, "AETP edge branch\nsemantic + detail fusion\nedge logits E", font(24, True))

    rounded_box(d, boxes["decoder"], colors["decoder"], colors["border"])
    center_text(d, boxes["decoder"], "Edge-guided decoder\npatch cues + FEM + MTA\ncoarse-to-fine fusion", font(24, True))

    rounded_box(d, boxes["masks"], colors["mask"], colors["border"])
    center_text(d, boxes["masks"], "P4\nP3\nP2\nP1", font(23, True))

    arrow(d, (300, 285), (390, 285))
    arrow(d, (720, 285), (820, 285))
    arrow(d, (1130, 270), (1240, 270))
    arrow(d, (1425, 405), (1425, 590))
    arrow(d, (1130, 330), (1240, 680))
    arrow(d, (1610, 700), (1670, 700))

    d.text((1160, 130), "edge supervision", font=font(19), fill=(145, 92, 32))
    arrow(d, (1260, 155), (1330, 180), fill=(167, 106, 37), width=3)
    d.text((1460, 500), "sigmoid(E) guides FEM", font=font(19), fill=(96, 73, 147))

    # Bottom evidence strip.
    strip = (70, 900, 1730, 1000)
    rounded_box(d, strip, (248, 249, 250), (205, 212, 218), width=2, radius=12)
    evidence = [
        ("Params", "99.90M -> 29.81M", "-70.16%"),
        ("GMACs", "129.02 -> 36.39", "-71.79%"),
        ("Avg S", f"{avg_s_ref:.3f} -> {avg_s_light:.3f}", f"{avg_s_light - avg_s_ref:+.3f}"),
        ("Avg MAE", f"{avg_mae_ref:.3f} -> {avg_mae_light:.3f}", f"{avg_mae_light - avg_mae_ref:+.3f}"),
    ]
    x = 110
    for label, val, delta in evidence:
        d.text((x, 918), label, font=font(18, True), fill=(68, 80, 90))
        d.text((x, 946), val, font=font(24, True), fill=(24, 35, 42))
        d.text((x, 976), delta, font=font(18), fill=(68, 105, 91))
        x += 400

    out = FIG_DIR / "light_b2_c64_method.png"
    img.save(out)
    return out


def read_metrics():
    rows = []
    with METRICS_CSV.open(newline="") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


def read_profiles():
    rows = []
    with PROFILES_CSV.open(newline="") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


def avg_metric(rows, exp_id, metric):
    vals = [float(r[metric]) for r in rows if r["exp_id"] == exp_id and r["dataset"] in {"CAMO", "COD10K", "NC4K"}]
    if len(vals) != 3:
        raise ValueError(f"Expected 3 rows for {exp_id}, got {len(vals)}")
    return sum(vals) / len(vals)


def choose_baseline_exp(rows):
    clean_rows = [
        r
        for r in rows
        if r["exp_id"] == CLEAN_BASELINE_EXP
        and r["dataset"] in {"CAMO", "COD10K", "NC4K"}
        and r.get("status") == "clean_prob_re_eval_complete"
    ]
    return CLEAN_BASELINE_EXP if len(clean_rows) == 3 else HISTORICAL_BASELINE_EXP


def profile_value(rows, exp_id, key):
    matches = [r for r in rows if r["exp_id"] == exp_id]
    if not matches:
        raise ValueError(f"No profile row for {exp_id}")
    return float(matches[0][key])


def draw_scatter():
    metrics = read_metrics()
    profiles = read_profiles()
    points = [
        {
            "label": "ESCNet-B5 C128",
            "exp": choose_baseline_exp(metrics),
            "profile": "baseline_escnet_b5_416_e120",
            "color": (50, 83, 132),
        },
        {
            "label": "Light-B2-C64",
            "exp": "light_b2_c64_e120_s42_prob_eval_v2",
            "profile": "light_b2_c64_pretrain_416",
            "color": (30, 132, 99),
        },
    ]
    for p in points:
        p["s"] = avg_metric(metrics, p["exp"], "Smeasure")
        p["mae"] = avg_metric(metrics, p["exp"], "MAE")
        p["params_m"] = profile_value(profiles, p["profile"], "params") / 1e6
        p["gmacs"] = profile_value(profiles, p["profile"], "gmacs")

    W, H = 1400, 900
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    d.text((70, 42), "Accuracy-efficiency trade-off", font=font(34, True), fill=(23, 32, 38))
    d.text((72, 88), "Three-dataset average S-measure vs. model complexity", font=font(21), fill=(82, 94, 104))

    plot = (140, 165, 1210, 735)
    x1, y1, x2, y2 = plot
    d.rectangle(plot, outline=(96, 108, 118), width=3)
    for i in range(1, 5):
        x = x1 + (x2 - x1) * i / 5
        y = y1 + (y2 - y1) * i / 5
        d.line([(x, y1), (x, y2)], fill=(226, 231, 235), width=1)
        d.line([(x1, y), (x2, y)], fill=(226, 231, 235), width=1)

    min_x, max_x = 0, 140
    min_y, max_y = 0.84, 0.89

    def sx(v):
        return x1 + (v - min_x) / (max_x - min_x) * (x2 - x1)

    def sy(v):
        return y2 - (v - min_y) / (max_y - min_y) * (y2 - y1)

    # Axis labels and ticks.
    d.text((140, 130), "Avg S-measure", font=font(22, True), fill=(38, 48, 56))
    d.text((500, 795), "GMACs (lower is better)", font=font(24, True), fill=(38, 48, 56))
    for val in [0, 35, 70, 105, 140]:
        x = sx(val)
        d.line([(x, y2), (x, y2 + 8)], fill=(65, 75, 83), width=2)
        txt = str(val)
        bb = d.textbbox((0, 0), txt, font=font(17))
        d.text((x - (bb[2] - bb[0]) / 2, y2 + 14), txt, font=font(17), fill=(65, 75, 83))
    for val in [0.84, 0.85, 0.86, 0.87, 0.88, 0.89]:
        y = sy(val)
        d.line([(x1 - 8, y), (x1, y)], fill=(65, 75, 83), width=2)
        d.text((82, y - 10), f"{val:.2f}", font=font(17), fill=(65, 75, 83))

    for p in points:
        x = sx(p["gmacs"])
        y = sy(p["s"])
        r = 17
        d.ellipse((x - r, y - r, x + r, y + r), fill=p["color"], outline=(20, 30, 35), width=2)
        label = f"{p['label']}\n{p['gmacs']:.2f} GMACs, S={p['s']:.3f}"
        tx = x + 25 if p["gmacs"] < 70 else x - 250
        ty = y - 42
        d.text((tx, ty), label, font=font(19, True), fill=p["color"], spacing=5)

    # Reduction annotation.
    base = points[0]
    light = points[1]
    summary_lines = [
        "Light-B2-C64: params -70.16%, GMACs -71.79%",
        f"Avg S -{base['s'] - light['s']:.3f}, Avg MAE +0.006",
    ]
    for idx, line in enumerate(summary_lines):
        d.text((185, 842 + idx * 28), line, font=font(20, True), fill=(30, 132, 99))

    out = FIG_DIR / "accuracy_efficiency_scatter.png"
    img.save(out)
    return out


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    paths = [draw_method_figure(), draw_scatter()]
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
