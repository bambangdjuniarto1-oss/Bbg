"""Thumbnail Bedah Bisnis: Liquid Vape (1080x1920, aman dipotong 3:4 di grid profil).

  python3 render/thumb_vap.py BG.png OUT.jpg
BG = frame V03 resolusi penuh (botol 3 lapis: emas = toko, ungu = brand, cyan = negara).
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "PlusJakartaSans-800.ttf")
W, H = 1080, 1920
YEL, PINK, CYAN, PURP, WHITE, INK = (255, 214, 0), (255, 64, 160), (60, 240, 255), (196, 140, 255), (255, 255, 255), (12, 6, 24)


def f(sz):
    return ImageFont.truetype(FONT, sz)


def fit(text, sz, maxw):
    while f(sz).getlength(text) > maxw and sz > 20:
        sz -= 2
    return f(sz)


def text_c(d, y, text, font, fill, stroke=10, sc=INK, x=W // 2):
    d.text((x, y), text, font=font, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=sc)


def glow_layer(size, draw_fn, radius=18, strength=2):
    g = Image.new("RGBA", size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(g))
    out = g.filter(ImageFilter.GaussianBlur(radius))
    for _ in range(strength - 1):
        out = Image.alpha_composite(out, g.filter(ImageFilter.GaussianBlur(radius)))
    return out


def pill(d, cx, cy, text, font, bg, fg, padx=34, pady=18, r=999):
    w = font.getlength(text)
    box = (cx - w / 2 - padx, cy - font.size / 2 - pady, cx + w / 2 + padx, cy + font.size / 2 + pady + 4)
    d.rounded_rectangle(box, radius=min(r, (box[3] - box[1]) / 2), fill=bg)
    d.text((cx, cy + 2), text, font=font, fill=fg, anchor="mm")
    return box


def main():
    bg, out = sys.argv[1], sys.argv[2]
    im = Image.open(bg).convert("RGB").resize((W, H), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(1.35)
    im = ImageEnhance.Contrast(im).enhance(1.08)
    # bloom tipis
    hi = im.point(lambda v: max(0, v - 150) * 2).filter(ImageFilter.GaussianBlur(28))
    im = Image.fromarray(np.clip(np.asarray(im, "float32") + np.asarray(hi, "float32") * .6, 0, 255).astype("uint8"))
    im = im.convert("RGBA")

    # gradasi gelap atas & bawah supaya teks kebaca
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        a = 0
        if y < 640:
            a = int(215 * (1 - y / 640) ** 1.3)
        if y > 1460:
            a = max(a, int(235 * ((y - 1460) / 460) ** 1.1))
        gd.line([(0, y), (W, y)], fill=(10, 4, 22, a))
    im = Image.alpha_composite(im, grad)

    # vignette
    vg = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vg).ellipse((-260, -200, W + 260, H + 200), fill=255)
    vg = vg.filter(ImageFilter.GaussianBlur(160))
    dark = Image.new("RGBA", (W, H), (6, 2, 14, 255))
    im = Image.composite(im, dark, vg)

    d = ImageDraw.Draw(im)

    # --- ATAS: label seri + hook harga ---
    pill(d, W // 2, 168, "BEDAH BISNIS", f(40), PINK, WHITE)
    text_c(d, 285, "1 BOTOL LIQUID VAPE", fit("1 BOTOL LIQUID VAPE", 84, 960), WHITE, 9)
    price = "Rp120 RIBU"
    pf = fit(price, 210, 1000)
    im = Image.alpha_composite(im, glow_layer((W, H), lambda g: g.text((W // 2, 445), price, font=pf, fill=YEL + (255,),
                                                                     anchor="mm"), 30, 3))
    d = ImageDraw.Draw(im)
    text_c(d, 445, price, pf, YEL, 14)

    # --- TENGAH: label tiap lapisan cairan ---
    tags = [(865, "TOKO", YEL), (1170, "BRAND", PURP), (1380, "NEGARA", CYAN)]
    tf = f(104)
    for y, name, col in tags:
        im = Image.alpha_composite(im, glow_layer((W, H), lambda g, y=y, name=name, col=col: g.text(
            (W // 2, y), name + " ?", font=tf, fill=col + (255,), anchor="mm"), 22, 2))
        d = ImageDraw.Draw(im)
        text_c(d, y, name + " ?", tf, WHITE, 12)

    # stiker miring: hook rasa penasaran
    st = Image.new("RGBA", (560, 150), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    sd.rounded_rectangle((8, 8, 552, 142), radius=26, fill=(235, 30, 60, 255), outline=WHITE, width=6)
    sd.text((280, 78), "BUKAN TOKONYA!", font=fit("BUKAN TOKONYA!", 62, 500), fill=WHITE, anchor="mm")
    st = st.rotate(6, expand=True, resample=Image.BICUBIC)
    sh = st.copy()
    sh.putalpha(sh.getchannel("A").point(lambda v: v * .55))
    sh = Image.merge("RGBA", (*[Image.new("L", sh.size, 0)] * 3, sh.getchannel("A"))).filter(ImageFilter.GaussianBlur(10))
    im.alpha_composite(sh, (W - st.width - 20 + 10, 585 + 14))
    im.alpha_composite(st, (W - st.width - 20, 585))
    d = ImageDraw.Draw(im)

    # --- BAWAH: pertanyaan utama ---
    q1, q2 = "SIAPA YANG DAPAT", "PALING GEDE?"
    text_c(d, 1500, q1, fit(q1, 92, 980), WHITE, 10)
    qf = fit(q2, 150, 1000)
    im = Image.alpha_composite(im, glow_layer((W, H), lambda g: g.text((W // 2, 1598), q2, font=qf, fill=PINK + (255,),
                                                                     anchor="mm"), 28, 3))
    d = ImageDraw.Draw(im)
    text_c(d, 1598, q2, qf, YEL, 14)

    d.text((W // 2, 1858), "@juniart.ai", font=f(36), fill=(255, 255, 255, 200), anchor="mm",
           stroke_width=4, stroke_fill=INK)

    im.convert("RGB").save(out, quality=95)
    print("wrote", out)


if __name__ == "__main__":
    main()
