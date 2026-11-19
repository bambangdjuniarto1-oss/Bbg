#!/usr/bin/env python3
"""Poster HALF TIME - PRDN Blue.

Background grid PRDN Blue, tulisan HALF TIME, foto pemain, papan skor, watermark.

Pemakaian:
  python3 poster/halftime_poster.py OUTPUT.png --score 1-0 \
      [--home PERSIB] [--away "SHAN UNITED"] [--event "SHOPEE CUP"] \
      [--players poster/foto/sekulic.png poster/foto/peralta.png] [--size 1080x1350]
"""
import argparse
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

from goal_poster import HERE, grid_background, load_cutout, watermark_mask

BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
BOLD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
NAVY = (8, 30, 78)


def font_for_width(path, text, target_w, max_size=None):
    f = ImageFont.truetype(path, 100)
    l, _, r, _ = f.getbbox(text)
    size = int(100 * target_w / (r - l))
    if max_size:
        size = min(size, max_size)
    return ImageFont.truetype(path, size)


def draw_centered(draw, cx, cy, text, font, fill):
    l, t, r, b = font.getbbox(text)
    draw.text((cx - (l + r) / 2, cy - (t + b) / 2), text, font=font, fill=fill)


def make_poster(out, score, home, away, event, players, size=(1080, 1350), scales=None):
    W, H = size
    canvas = grid_background(W, H).convert("RGBA")
    margin = round(W * 0.055)

    # 1) Tulisan HALF TIME raksasa di belakang pemain
    text = "HALF TIME"
    font = font_for_width(BLACK, text, W - 2 * margin)
    l, t, r, b = font.getbbox(text)
    tx, ty = (W - (r - l)) // 2 - l, round(H * 0.14) - t
    txt = Image.new("L", (W, H), 0)
    ImageDraw.Draw(txt).text((tx, ty), text, font=font, fill=255)
    shadow = txt.filter(ImageFilter.GaussianBlur(W * 0.01)).point(lambda v: v * 0.45)
    canvas.paste((2, 20, 55, 255), (round(W * 0.006), round(W * 0.01)), shadow)
    canvas.paste((255, 255, 255, 255), (0, 0), txt)

    # 2) Pemain (1 atau 2), berdiri di atas papan skor
    bar_top = round(H * 0.80)
    cutouts = [load_cutout(p) for p in players]
    ph = round(H * 0.66)
    slot = W / len(cutouts)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    scales = scales or [1.0] * len(cutouts)
    for i, c in enumerate(cutouts):
        h = round(ph * scales[i])
        w = round(c.width * h / c.height)
        if w > slot * 1.25:
            w = round(slot * 1.25)
            h = round(c.height * w / c.width)
        c = c.resize((w, h), Image.LANCZOS)
        # sedikit merapat ke tengah bila 2 pemain
        cx = slot * (i + 0.5) + (slot * 0.12 if i == 0 else -slot * 0.12) * (len(cutouts) > 1)
        layer.alpha_composite(c, (round(cx - w / 2), bar_top + round(H * 0.02) - h))
    pshadow = layer.getchannel("A").filter(ImageFilter.GaussianBlur(W * 0.018)).point(lambda v: v * 0.6)
    canvas.paste((2, 16, 45, 255), (round(W * 0.012), round(W * 0.01)), pshadow)
    canvas.alpha_composite(layer)

    # Garis tepi HALF TIME di depan pemain, agar huruf yang tertutup tetap terbaca
    stroke = Image.new("L", (W, H), 0)
    ImageDraw.Draw(stroke).text((tx, ty), text, font=font, fill=0,
                                stroke_width=max(2, round(W * 0.003)), stroke_fill=255)
    stroke = ImageChops.subtract(stroke, txt).point(lambda v: round(v * 0.85))
    canvas.paste((255, 255, 255, 255), (0, 0), stroke)

    # 3) Papan skor
    d = ImageDraw.Draw(canvas)
    bar_h = round(H * 0.115)
    bar = (margin, bar_top, W - margin, bar_top + bar_h)
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).rounded_rectangle(bar, radius=round(bar_h * 0.18), fill=200)
    canvas.paste((2, 16, 45, 255), (0, round(W * 0.01)), sh.filter(ImageFilter.GaussianBlur(W * 0.015)))
    d.rounded_rectangle(bar, radius=round(bar_h * 0.18), fill=(255, 255, 255))

    box_w = round(W * 0.26)
    box = (W // 2 - box_w // 2, bar_top - round(bar_h * 0.12), W // 2 + box_w // 2, bar_top + bar_h + round(bar_h * 0.12))
    d.rounded_rectangle(box, radius=round(bar_h * 0.18), fill=NAVY)
    sfont = font_for_width(BLACK, "0 - 0", box_w * 0.78, max_size=round(bar_h * 0.95))
    draw_centered(d, W / 2, bar_top + bar_h / 2, score.replace("-", " - "), sfont, (255, 255, 255))

    side_w = (box[0] - bar[0]) - round(W * 0.05)
    nfont = min((font_for_width(BLACK, n, side_w, max_size=round(bar_h * 0.36)) for n in (home, away)),
                key=lambda f: f.size)
    cy = bar_top + bar_h / 2
    draw_centered(d, (bar[0] + box[0]) / 2, cy, home, nfont, NAVY)
    draw_centered(d, (box[2] + bar[2]) / 2, cy, away, nfont, NAVY)

    # Keterangan kecil di bawah papan skor
    efont = ImageFont.truetype(BOLD, round(H * 0.022))
    draw_centered(d, W / 2, (box[3] + H) / 2, f"BABAK PERTAMA  ·  {event}", efont, (255, 255, 255))

    # 4) Watermark PRDN BLUE.
    wm = watermark_mask(round(W * 0.22)).point(lambda v: round(v * 0.95))
    canvas.paste((255, 255, 255, 255), (margin, margin), wm)

    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    canvas.convert("RGB").save(out, quality=95)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--score", required=True, help="mis. 1-0 (kandang-tamu)")
    ap.add_argument("--home", default="PERSIB")
    ap.add_argument("--away", default="SHAN UNITED")
    ap.add_argument("--event", default="SHOPEE CUP")
    ap.add_argument("--players", nargs="+", default=[os.path.join(HERE, "foto", "sekulic.png"),
                                                     os.path.join(HERE, "foto", "peralta.png")])
    ap.add_argument("--scales", nargs="+", type=float, default=[0.87, 0.86],
                    help="skala tinggi tiap pemain (default: Peralta sedikit dikecilkan)")
    ap.add_argument("--size", default="1080x1350")
    a = ap.parse_args()
    w, h = map(int, a.size.lower().split("x"))
    print(make_poster(a.out, a.score, a.home.upper(), a.away.upper(), a.event.upper(), a.players, (w, h), a.scales))
