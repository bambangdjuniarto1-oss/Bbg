#!/usr/bin/env python3
"""Poster HALF TIME / FULL TIME - PRDN Blue (tanpa foto pemain).

Full time: --title FULL TIME --label "SKOR AKHIR" --title-scale 0.8

Background grid PRDN Blue, tulisan HALF TIME, papan skor, pencetak gol, watermark.

Pemakaian:
  python3 poster/halftime_poster.py OUTPUT.png --score 2-0 \
      [--home PERSIB] [--away "SHAN UNITED"] [--event "SHOPEE CUP"] \
      [--home-goals "SEKULIĆ 12'" "PERALTA 17' (P)"] [--away-goals ...] [--size 1080x1350]
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from goal_poster import grid_background, watermark_mask

BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
BOLD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
SEMI = "/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf"
NAVY = (8, 30, 78)
SHADOW = (2, 16, 45, 255)


def font_for_width(path, text, target_w, max_size=None):
    f = ImageFont.truetype(path, 100)
    l, _, r, _ = f.getbbox(text)
    size = int(100 * target_w / (r - l))
    return ImageFont.truetype(path, min(size, max_size) if max_size else size)


def draw_centered(draw, cx, cy, text, font, fill):
    l, t, r, b = font.getbbox(text)
    draw.text((cx - (l + r) / 2, cy - (t + b) / 2), text, font=font, fill=fill)


def soft_shadow(canvas, mask, blur, offset, strength=0.5):
    sh = mask.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: round(v * strength))
    canvas.paste(SHADOW, offset, sh)


def make_poster(out, score, home, away, event, home_goals=(), away_goals=(), size=(1080, 1350),
                title=("HALF", "TIME"), label="BABAK PERTAMA", title_scale=1.0):
    W, H = size
    canvas = grid_background(W, H).convert("RGBA")
    margin = round(W * 0.07)

    # 1) Judul bertumpuk (HALF/TIME, FULL/TIME), satu ukuran huruf untuk semua baris
    fonts = [font_for_width(BLACK, line, (W - 2 * margin) * title_scale) for line in title]
    font = min(fonts, key=lambda f: f.size)
    hb = font.getbbox("H")
    cap_h = hb[3] - hb[1]
    gap = round(cap_h * 0.12)
    top = round(H * 0.17)
    txt = Image.new("L", (W, H), 0)
    td = ImageDraw.Draw(txt)
    for i, line in enumerate(title):
        l, t, r, b = font.getbbox(line)
        td.text(((W - (r - l)) / 2 - l, top + i * (cap_h + gap) - hb[1]), line, font=font, fill=255)
    soft_shadow(canvas, txt, W * 0.01, (round(W * 0.006), round(W * 0.01)), 0.45)
    canvas.paste((255, 255, 255, 255), (0, 0), txt)
    text_bottom = top + len(title) * cap_h + (len(title) - 1) * gap

    # 2) Papan skor
    d = ImageDraw.Draw(canvas)
    bar_h = round(H * 0.11)
    bar_top = text_bottom + round(H * (0.09 if title_scale >= 1 else 0.07))
    bar = (margin, bar_top, W - margin, bar_top + bar_h)
    radius = round(bar_h * 0.2)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).rounded_rectangle(bar, radius=radius, fill=220)
    soft_shadow(canvas, m, W * 0.015, (0, round(W * 0.012)), 0.9)
    d.rounded_rectangle(bar, radius=radius, fill=(255, 255, 255))

    box_w = round(W * 0.27)
    ext = round(bar_h * 0.14)
    box = (W // 2 - box_w // 2, bar_top - ext, W // 2 + box_w // 2, bar_top + bar_h + ext)
    d.rounded_rectangle(box, radius=radius, fill=NAVY)
    sfont = font_for_width(BLACK, "0 - 0", box_w * 0.76, max_size=round(bar_h * 0.95))
    cy = bar_top + bar_h / 2
    draw_centered(d, W / 2, cy, score.replace("-", " - "), sfont, (255, 255, 255))

    side_w = (box[0] - bar[0]) - round(W * 0.05)
    nfont = min((font_for_width(BLACK, n, side_w, max_size=round(bar_h * 0.34)) for n in (home, away)),
                key=lambda f: f.size)
    home_cx, away_cx = (bar[0] + box[0]) / 2, (box[2] + bar[2]) / 2
    draw_centered(d, home_cx, cy, home, nfont, NAVY)
    draw_centered(d, away_cx, cy, away, nfont, NAVY)

    # 3) Pencetak gol di bawah nama tim masing-masing
    gfont = ImageFont.truetype(SEMI, round(H * 0.026))
    _, gt, _, gb = gfont.getbbox("Ag")
    line_h = round((gb - gt) * 1.5)
    gy = box[3] + round(H * 0.03)
    if away_goals or len(home_goals) <= 3:
        for cx, goals in ((home_cx, home_goals), (away_cx, away_goals)):
            for i, g in enumerate(goals):
                draw_centered(d, cx, gy + i * line_h + line_h / 2, g, gfont, (255, 255, 255))
    else:
        # Banyak gol satu tim: susun rata tengah selebar papan skor, dipisah titik
        rows, cur = [], ""
        for g in home_goals:
            cand = f"{cur}   ·   {g}" if cur else g
            if gfont.getlength(cand) > bar[2] - bar[0] and cur:
                rows.append(cur)
                cur = g
            else:
                cur = cand
        rows.append(cur)
        for i, row in enumerate(rows):
            draw_centered(d, W / 2, gy + i * line_h + line_h / 2, row, gfont, (255, 255, 255))

    # 4) Keterangan di bawah
    efont = ImageFont.truetype(BOLD, round(H * 0.022))
    ey = H - margin - round(H * 0.01)
    label = f"{label}  ·  {event}"
    l, t, r, b = efont.getbbox(label)
    pad_x, pad_y = round(W * 0.03), round(H * 0.012)
    pill = (W / 2 - (r - l) / 2 - pad_x, ey - (b - t) / 2 - pad_y,
            W / 2 + (r - l) / 2 + pad_x, ey + (b - t) / 2 + pad_y)
    d.rounded_rectangle(pill, radius=round((pill[3] - pill[1]) / 2),
                        outline=(255, 255, 255), width=max(2, round(W * 0.0025)))
    draw_centered(d, W / 2, ey, label, efont, (255, 255, 255))

    # 5) Watermark PRDN BLUE.
    wm = watermark_mask(round(W * 0.22)).point(lambda v: round(v * 0.95))
    canvas.paste((255, 255, 255, 255), (round(W * 0.055), round(W * 0.055)), wm)

    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    canvas.convert("RGB").save(out, quality=95)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--score", required=True, help="mis. 2-0 (kandang-tamu)")
    ap.add_argument("--home", default="PERSIB")
    ap.add_argument("--away", default="SHAN UNITED")
    ap.add_argument("--event", default="SHOPEE CUP")
    ap.add_argument("--home-goals", nargs="*", default=[])
    ap.add_argument("--away-goals", nargs="*", default=[])
    ap.add_argument("--title", nargs="+", default=["HALF", "TIME"])
    ap.add_argument("--label", default="BABAK PERTAMA")
    ap.add_argument("--title-scale", type=float, default=1.0)
    ap.add_argument("--size", default="1080x1350")
    a = ap.parse_args()
    w, h = map(int, a.size.lower().split("x"))
    print(make_poster(a.out, a.score, a.home.upper(), a.away.upper(), a.event.upper(),
                      a.home_goals, a.away_goals, (w, h),
                      [t.upper() for t in a.title], a.label.upper(), a.title_scale))
