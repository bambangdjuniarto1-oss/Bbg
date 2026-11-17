"""Thumbnail gaya feed @juniart.ai: header langit terang + bubble judul + pill @juniart.ai, judul besar
slab-serif putih berkontur, subtitle kata kunci kuning, kartu HUD kiri-bawah. Dipakai di atas render 3D
(mis. kota diorama melayang di dunia neon). Elemen penting ada di zona aman crop 3:4 (y 240..1680).

  python3 render/thumb_feed.py BG.png OUT.jpg --bubble "Liquid **Rp120 ribu**" \
      --title "Bisnis|Liquid Vape" --sub "siapa dapat **paling gede**?" \
      --hud "HARGA 1 BOTOL 60 ML|Rp|120|ribu|dibagi 3"
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compose as C  # noqa: E402
import compose_full as CF  # noqa: E402
import watermark as WM  # noqa: E402

SLAB = os.path.join(C.FONT_DIR, "RobotoSlab-700.woff")


def draw_title(img, lines, y, size=150, track=4):
    """judul besar slab-serif putih, kontur hitam tebal + bayangan lembut; tiap baris di tengah."""
    f = ImageFont.truetype(SLAB, size)
    lh = int(size * 1.02)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i, ln in enumerate(lines):
        fs = f
        while sum(fs.getlength(ch) + track for ch in ln) > img.width - 70:
            fs = ImageFont.truetype(SLAB, fs.size - 4)
        w = sum(fs.getlength(ch) + track for ch in ln) - track
        x = (img.width - w) / 2
        yy = y + i * lh
        for ch in ln:
            d.text((x, yy), ch, font=fs, fill=(255, 255, 255, 255), anchor="ls",
                   stroke_width=max(6, fs.size // 16), stroke_fill=(16, 16, 20, 255))
            x += fs.getlength(ch) + track
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.putalpha(layer.getchannel("A").filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * .5)))
    img.alpha_composite(sh, (6, 10))
    img.alpha_composite(layer)
    return y + (len(lines) - 1) * lh


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bg")
    ap.add_argument("out")
    ap.add_argument("--bubble", default="Liquid **Rp120 ribu**")
    ap.add_argument("--title", default="Bisnis|Liquid Vape")
    ap.add_argument("--sub", default="siapa dapat **paling gede**?")
    ap.add_argument("--hud", default="HARGA 1 BOTOL 60 ML|Rp|120|ribu|dibagi ke 3 pihak")
    ap.add_argument("--title-y", type=int, default=800, help="baseline baris judul pertama")
    ap.add_argument("--hud-y", type=int, default=1430)
    a = ap.parse_args()

    img = Image.open(a.bg).convert("RGBA").resize((1080, 1920), Image.LANCZOS)
    C.draw_header(img, 470, 640)
    CF.draw_bubble_center(img, a.bubble, 1.0)
    img.alpha_composite(WM.make_overlay("@juniart.ai", 420))
    last = draw_title(img, a.title.split("|"), a.title_y)
    if a.sub:
        C.draw_subtitle(img, C.parse_rich(a.sub), last + 95, 1.0)
    if a.hud:
        title, prefix, val, unit, tgt = a.hud.split("|")
        v = float(val)
        C.draw_hud(img, dict(title=title, prefix=prefix, unit=unit, max=v, to=v, target_text=tgt), v, 1.0,
                   56, a.hud_y)
    img.convert("RGB").save(a.out, quality=95)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
