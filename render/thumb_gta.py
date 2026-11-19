"""Thumbnail "GTA VI, Rp17 triliun sebelum rilis" (gaya feed @juniart.ai) dari key art resmi GTA VI.
Header terang + bubble + pill @juniart.ai di atas; key art resmi (logo di tengah) di bawahnya; judul besar
slab-serif di bagian bawah yang digelapkan; kartu HUD pre-order.

  python3 render/thumb_gta.py OUT.jpg [--tex DIR] [--art cover] [--art-y 420] [--art-h 1560]
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compose as C  # noqa: E402
import compose_full as CF  # noqa: E402
import thumb_feed as TF  # noqa: E402
import watermark as WM  # noqa: E402

TEX = os.environ.get("GTA_TEX", "/tmp/claude-0/-home-user-Bbg/e4570b9b-8bb7-5f4c-a29b-693bb3cf9daa/scratchpad/gta/tex")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--tex", default=TEX)
    ap.add_argument("--art", default="keyart")
    ap.add_argument("--art-y", type=int, default=440)
    ap.add_argument("--art-h", type=int, default=1060)
    ap.add_argument("--bubble", default="Bisnis **GTA VI**")
    ap.add_argument("--title", default="Rp17 Triliun")
    ap.add_argument("--sub", default="masuk **sebelum game-nya rilis**")
    ap.add_argument("--title-y", type=int, default=1625)
    ap.add_argument("--hud-y", type=int, default=0, help="0 = tanpa HUD")
    a = ap.parse_args()

    W_, H_ = 1080, 1920
    img = Image.new("RGBA", (W_, H_), (40, 22, 70, 255))
    art = Image.open(os.path.join(a.tex, a.art + ".jpg")).convert("RGB")
    sc = max(W_ / art.width, a.art_h / art.height)
    art = art.resize((int(art.width * sc + .5), int(art.height * sc + .5)), Image.LANCZOS)
    x0 = (art.width - W_) // 2
    art = art.crop((x0, 0, x0 + W_, min(art.height, a.art_h)))
    img.paste(art, (0, a.art_y))
    # gradien gelap ungu di bawah untuk keterbacaan judul (gaya sunset Leonida)
    g = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    for y in range(a.art_y + a.art_h - 330, H_):
        u = min(1.0, (y - (a.art_y + a.art_h - 330)) / 330)
        d.line([(0, y), (W_, y)], fill=(28, 10, 48, int(235 * u ** 1.3)))
    img.alpha_composite(g)
    C.draw_header(img, 470, 640)
    CF.draw_bubble_center(img, a.bubble, 1.0)
    img.alpha_composite(WM.make_overlay("@juniart.ai", 420))
    last = TF.draw_title(img, a.title.split("|"), a.title_y, size=150)
    if a.sub:
        C.draw_subtitle(img, C.parse_rich(a.sub), last + 92, 1.0)
    if a.hud_y:
        C.draw_hud(img, dict(title="PRE-ORDER (ESTIMASI)", prefix="", unit="juta kopi", max=9.69, to=9.69,
                             target_text="nilai US$942 juta", decimals=2), 9.69, 1.0, 56, a.hud_y)
    img.convert("RGB").save(a.out, quality=95)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
