#!/usr/bin/env python3
"""Poster GOAL - PRDN Blue.

Isi poster hanya: background grid biru ala PRDN Blue, tulisan GOAL,
foto pemain (sudah dipotong tanpa background), dan watermark PRDN BLUE.

Pemakaian:
  python3 poster/goal_poster.py FOTO OUTPUT.png [--crop x0,y0,x1,y1] [--size 1080x1350]

  FOTO   : PNG transparan (pemain sudah dipotong), atau foto biasa.
           Foto biasa otomatis dihapus background-nya dengan rembg (BiRefNet).
  --crop : potong area foto dulu sebelum hapus background (mis. dari screenshot).
"""
import argparse
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.join(HERE, "assets", "prdn_logo.jpg")
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"

# Warna diambil dari logo PRDN Blue
CELL_DARK = (17, 54, 110)    # kotak grid sisi gelap (kiri bawah)
CELL_LIGHT = (46, 80, 132)   # kotak grid sisi terang (kanan atas)
LINE = (4, 34, 84)           # garis grid
GRID_COLS = 28               # jumlah kotak mendatar (sama rapatnya dengan logo)


# ---------------------------------------------------------------- background
def grid_background(W, H, seed=7):
    """Grid biru bertekstur seperti logo PRDN Blue."""
    # Gradasi diagonal: gelap di kiri bawah, terang di kanan atas
    small = Image.new("RGB", (64, 80))
    px = small.load()
    for y in range(80):
        for x in range(64):
            t = min(1, max(0, (x / 63) * 0.65 + (1 - y / 79) * 0.35))
            t = t * t * (3 - 2 * t)
            px[x, y] = tuple(round(a + (b - a) * t) for a, b in zip(CELL_DARK, CELL_LIGHT))
    bg = small.resize((W, H), Image.BICUBIC)

    # Garis grid
    step = W / GRID_COLS
    lw = max(2, round(step * 0.07))
    lines = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(lines)
    x = 0.0
    while x < W + step:
        d.rectangle((round(x), 0, round(x) + lw - 1, H), fill=235)
        x += step
    y = 0.0
    while y < H + step:
        d.rectangle((0, round(y), W, round(y) + lw - 1), fill=235)
        y += step
    bg.paste(Image.new("RGB", (W, H), LINE), (0, 0), lines.filter(ImageFilter.GaussianBlur(0.6)))

    # Grain seperti kertas cetak
    rnd = random.Random(seed)
    noise = Image.frombytes("L", (W, H), bytes(rnd.getrandbits(8) for _ in range(W * H)))
    noise = noise.filter(ImageFilter.GaussianBlur(0.7))
    grain = Image.merge("RGB", [noise] * 3)
    bg = Image.blend(bg, ImageChops.overlay(bg, grain), 0.35)
    return bg


# ---------------------------------------------------------------- pemain
def load_cutout(path, crop=None):
    img = ImageOps.exif_transpose(Image.open(path))
    if crop:
        img = img.crop(crop)
    if img.mode != "RGBA" or img.getchannel("A").getextrema()[0] == 255:
        from rembg import new_session, remove  # hanya dipakai bila perlu
        img = remove(img.convert("RGB"), session=new_session("birefnet-general"))
    img = img.convert("RGBA")
    # Rapikan tepi: kikis 1px agar sisa warna background lama tidak terlihat
    a = img.getchannel("A").filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    img.putalpha(a)
    return img.crop(a.getbbox())


# ---------------------------------------------------------------- watermark
def watermark_mask(width):
    """Ambil tulisan putih 'PRDN BLUE.' dari logo sebagai mask transparan."""
    logo = Image.open(LOGO).convert("RGB")
    r, g, b = logo.split()
    lum = ImageChops.darker(ImageChops.darker(r, g), b)
    mask = lum.point(lambda v: 0 if v < 150 else min(255, (v - 150) * 3))
    mask = mask.crop(mask.getbbox())
    return mask.resize((width, round(mask.height * width / mask.width)), Image.LANCZOS)


def fit_font(text, target_w):
    f = ImageFont.truetype(FONT, 100)
    l, _, r, _ = f.getbbox(text)
    return ImageFont.truetype(FONT, int(100 * target_w / (r - l)))


# ---------------------------------------------------------------- poster
def make_poster(photo, out, size=(1080, 1350), crop=None):
    W, H = size
    canvas = grid_background(W, H).convert("RGBA")
    margin = round(W * 0.055)

    # 1) Tulisan GOAL raksasa di belakang pemain
    text = "GOAL"
    font = fit_font(text, W - 2 * margin)
    l, t, r, b = font.getbbox(text)
    tx = (W - (r - l)) // 2 - l
    ty = round(H * 0.80) - b
    txt = Image.new("L", (W, H), 0)
    ImageDraw.Draw(txt).text((tx, ty), text, font=font, fill=255)
    shadow = txt.filter(ImageFilter.GaussianBlur(W * 0.012)).point(lambda v: v * 0.45)
    canvas.paste((2, 20, 55, 255), (round(W * 0.008), round(W * 0.012)), shadow)
    canvas.paste((255, 255, 255, 255), (0, 0), txt)

    # 2) Pemain di depan tulisan
    player = load_cutout(photo, crop)
    ph = round(H * 0.86)
    pw = round(player.width * ph / player.height)
    if pw > W * 0.95:
        pw = round(W * 0.95)
        ph = round(player.height * pw / player.width)
    player = player.resize((pw, ph), Image.LANCZOS)
    px, py = (W - pw) // 2, H - ph - round(H * 0.015)
    # Bayangan lembut di belakang pemain supaya terpisah dari tulisan
    pshadow = Image.new("L", (W, H), 0)
    pshadow.paste(player.getchannel("A"), (px, py))
    pshadow = pshadow.filter(ImageFilter.GaussianBlur(W * 0.018)).point(lambda v: v * 0.6)
    canvas.paste((2, 16, 45, 255), (round(W * 0.012), round(W * 0.01)), pshadow)
    canvas.alpha_composite(player, (px, py))

    # Garis tepi GOAL di depan pemain, agar huruf yang tertutup tetap terbaca
    stroke = Image.new("L", (W, H), 0)
    ImageDraw.Draw(stroke).text((tx, ty), text, font=font, fill=0,
                                stroke_width=max(2, round(W * 0.003)), stroke_fill=255)
    stroke = ImageChops.subtract(stroke, txt).point(lambda v: round(v * 0.85))
    canvas.paste((255, 255, 255, 255), (0, 0), stroke)

    # 3) Watermark PRDN BLUE. (pojok kiri atas)
    wm = watermark_mask(round(W * 0.22)).point(lambda v: round(v * 0.95))
    canvas.paste((255, 255, 255, 255), (margin, margin), wm)

    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    canvas.convert("RGB").save(out, quality=95)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("photo")
    ap.add_argument("out")
    ap.add_argument("--size", default="1080x1350")
    ap.add_argument("--crop", help="x0,y0,x1,y1")
    a = ap.parse_args()
    w, h = map(int, a.size.lower().split("x"))
    crop = tuple(map(int, a.crop.split(","))) if a.crop else None
    print(make_poster(a.photo, a.out, (w, h), crop))
