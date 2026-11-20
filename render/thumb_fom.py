"""Thumbnail "Cara brand vape bertahan di tengah fatwa haram" (gaya feed @juniart.ai).
Latar = frame render adegan reveal logo FOOM (F07); header + bubble + pill @juniart.ai di atas,
judul besar di bawah yang digelapkan.

  python3 render/thumb_fom.py OUT.jpg --frame RENDER/F07/frames/0085.png
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compose as C  # noqa: E402
import compose_full as CF  # noqa: E402
import thumb_feed as TF  # noqa: E402
import watermark as WM  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--frame", required=True)
    ap.add_argument("--bubble", default="Bedah Bisnis **FOOM**")
    ap.add_argument("--title", default="FATWA HARAM")
    ap.add_argument("--sub", default="cara brand vape **bertahan**")
    ap.add_argument("--title-y", type=int, default=1560)
    a = ap.parse_args()

    W_, H_ = 1080, 1920
    img = Image.open(a.frame).convert("RGBA").resize((W_, H_), Image.LANCZOS)
    g = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    y0 = 1250
    for y in range(y0, H_):
        u = min(1.0, (y - y0) / 300)
        d.line([(0, y), (W_, y)], fill=(26, 8, 40, int(240 * u ** 1.3)))
    img.alpha_composite(g)
    C.draw_header(img, 470, 640)
    CF.draw_bubble_center(img, a.bubble, 1.0)
    img.alpha_composite(WM.make_overlay("@juniart.ai", 420))
    last = TF.draw_title(img, a.title.split("|"), a.title_y, size=150)
    if a.sub:
        C.draw_subtitle(img, C.parse_rich(a.sub), last + 92, 1.0)
    img.convert("RGB").save(a.out, quality=95)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
