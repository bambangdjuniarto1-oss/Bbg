#!/usr/bin/env python3
"""Poster GOAL - PRDN Blue.

Isi poster hanya: foto pemain, tulisan GOAL, dan watermark PRDN BLUE.

Pemakaian:
  python3 poster/goal_poster.py FOTO.jpg OUTPUT.png [--focus-y 0.35] [--size 1080x1350]

  --focus-y : posisi titik fokus vertikal foto (0 = atas, 1 = bawah) saat dipotong
              agar wajah pemain tidak terpotong. Default 0.3.
"""
import argparse
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.join(HERE, "assets", "prdn_logo.jpg")
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-BlackItalic.otf"

NAVY = (10, 26, 66)      # biru gelap dasar gradasi
BRAND = (28, 64, 140)    # biru PRDN


def cover(img, w, h, focus_y):
    """Potong + skala foto agar memenuhi kanvas (object-fit: cover)."""
    img = ImageOps.exif_transpose(img).convert("RGB")
    s = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x = (img.width - w) // 2
    y = round((img.height - h) * min(max(focus_y, 0), 1))
    return img.crop((x, y, x + w, y + h))


def watermark_mask(width):
    """Ambil tulisan putih 'PRDN BLUE.' dari logo sebagai mask transparan."""
    logo = Image.open(LOGO).convert("RGB")
    lum = ImageChops.darker(ImageChops.darker(*logo.split()[:2]), logo.split()[2])
    mask = lum.point(lambda v: 0 if v < 150 else min(255, (v - 150) * 3))
    mask = mask.crop(mask.getbbox())
    h = round(mask.height * width / mask.width)
    return mask.resize((width, h), Image.LANCZOS)


def vertical_gradient(w, h, start, stops):
    """Mask gradasi vertikal: stops = [(posisi 0..1, alpha 0..255), ...]."""
    g = Image.new("L", (1, h))
    for y in range(h):
        t = y / (h - 1)
        a = stops[0][1]
        for (p0, a0), (p1, a1) in zip(stops, stops[1:]):
            if p0 <= t <= p1:
                k = (t - p0) / (p1 - p0) if p1 > p0 else 0
                k = k * k * (3 - 2 * k)  # smoothstep
                a = a0 + (a1 - a0) * k
                break
            if t > p1:
                a = a1
        g.putpixel((0, y), round(a))
    return g.resize((w, h))


def fit_font(text, target_w):
    size = 100
    font = ImageFont.truetype(FONT, size)
    box = font.getbbox(text)
    size = int(size * target_w / (box[2] - box[0]))
    return ImageFont.truetype(FONT, size)


def make_poster(photo, out, size=(1080, 1350), focus_y=0.3):
    W, H = size
    base = cover(Image.open(photo), W, H, focus_y)

    # Grading biru tipis supaya senada dengan brand
    tint = Image.new("RGB", (W, H), BRAND)
    base = Image.blend(base, ImageChops.multiply(base, tint).point(lambda v: min(255, v * 2)), 0.25)

    # Gradasi gelap di bawah (tempat tulisan GOAL) dan sedikit di atas (watermark)
    navy = Image.new("RGB", (W, H), NAVY)
    base.paste(navy, (0, 0), vertical_gradient(W, H, 0, [(0, 150), (0.18, 0), (0.5, 0), (0.78, 215), (1, 245)]))

    # Tulisan GOAL
    margin = round(W * 0.055)
    text = "GOAL"
    font = fit_font(text, W - 2 * margin)
    l, t, r, b = font.getbbox(text)
    tx = (W - (r - l)) // 2 - l
    ty = H - round(H * 0.06) - b

    # Glow lembut di belakang teks
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).text((tx, ty), text, font=font, fill=255)
    glow = glow.filter(ImageFilter.GaussianBlur(W * 0.03)).point(lambda v: v * 0.55)
    base.paste(Image.new("RGB", (W, H), (70, 130, 255)), (0, 0), glow)

    draw = ImageDraw.Draw(base)
    draw.text((tx, ty), text, font=font, fill=(255, 255, 255))

    # Watermark PRDN BLUE. (pojok kiri atas)
    wm = watermark_mask(round(W * 0.2))
    wm = wm.point(lambda v: round(v * 0.92))
    base.paste(Image.new("RGB", wm.size, (255, 255, 255)), (margin, margin), wm)

    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    base.save(out, quality=95)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("photo")
    ap.add_argument("out")
    ap.add_argument("--focus-y", type=float, default=0.3)
    ap.add_argument("--size", default="1080x1350")
    a = ap.parse_args()
    w, h = map(int, a.size.lower().split("x"))
    print(make_poster(a.photo, a.out, (w, h), a.focus_y))
