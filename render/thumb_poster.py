"""Thumbnail gaya poster sinematik: adegan 3D di atas, gradasi gelap di bawah, judul putih bersih 2 baris,
subjudul kecil abu-abu. Teks berada di zona aman crop 3:4 (grid profil).

  python3 render/thumb_poster.py BG.png OUT.jpg --l1 "1 Botol Liquid," --l2 "Dibagi Tiga." \
      --sub "bedah bisnis · @juniart.ai"
"""
import argparse

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

W, H = 1080, 1920
BOLD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
REG = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
BOT = np.array([26, 14, 40], "float32")        # ungu gelap dasar poster


def fit(path, text, sz, maxw):
    while ImageFont.truetype(path, sz).getlength(text) > maxw and sz > 20:
        sz -= 2
    return ImageFont.truetype(path, sz)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bg")
    ap.add_argument("out")
    ap.add_argument("--l1", default="1 Botol Liquid,")
    ap.add_argument("--l2", default="Dibagi Tiga.")
    ap.add_argument("--sub", default="bedah bisnis · @juniart.ai")
    ap.add_argument("--y", type=int, default=1150, help="pusat baris judul pertama")
    a = ap.parse_args()

    im = Image.open(a.bg).convert("RGB").resize((W, H), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(1.12)
    arr = np.asarray(im, "float32")
    # bloom halus
    hi = Image.fromarray(np.clip((arr - 140) * 1.6, 0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(24))
    arr = arr + np.asarray(hi, "float32") * .45
    # grade sinematik: bayangan sedikit ungu, highlight hangat
    lum = arr.mean(2, keepdims=True) / 255
    arr = arr * (1 - .10 * (1 - lum)) + np.array([14, 4, 26], "float32") * (1 - lum) * .5
    # gradasi bawah -> ungu gelap pekat
    y = np.arange(H, dtype="float32")[:, None, None] / H
    gs = (a.y - 210) / H
    g = np.clip((y - gs) / .17, 0, 1) ** 1.2 * .97
    arr = arr * (1 - g) + BOT * g
    # vignette atas & sisi tipis
    yy, xx = np.mgrid[0:H, 0:W].astype("float32")
    v = 1 - .35 * np.clip(((xx - W / 2) / (W * .62)) ** 2 + ((yy - H * .42) / (H * .7)) ** 2, 0, 1)
    arr = arr * v[..., None]
    # butiran film halus
    rng = np.random.default_rng(3)
    arr += rng.normal(0, 3.2, arr.shape[:2])[..., None]
    im = Image.fromarray(np.clip(arr, 0, 255).astype("uint8")).convert("RGBA")

    d = ImageDraw.Draw(im)
    f1 = fit(BOLD, a.l1, 150, 900)
    f2 = fit(BOLD, a.l2, 150, 900)
    sz = min(f1.size, f2.size)
    f1 = f2 = ImageFont.truetype(BOLD, sz)
    lh = int(sz * 1.02)
    # bayangan lembut di belakang judul
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for i, (t, f) in enumerate(((a.l1, f1), (a.l2, f2))):
        sd.text((W // 2, a.y + i * lh + 6), t, font=f, fill=(0, 0, 0, 150), anchor="mm")
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(im)
    for i, (t, f) in enumerate(((a.l1, f1), (a.l2, f2))):
        d.text((W // 2, a.y + i * lh), t, font=f, fill=(255, 255, 255), anchor="mm")
    fs = ImageFont.truetype(REG, 38)
    d.text((W // 2, a.y + lh + int(sz * .62) + 48), a.sub, font=fs, fill=(178, 170, 190), anchor="mm")
    im.convert("RGB").save(a.out, quality=95)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
