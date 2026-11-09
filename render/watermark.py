"""Tambahkan watermark akun Instagram ke video jadi (tanpa render ulang).

Watermark: pil gelap semi-transparan + ikon Instagram + handle, di area header (bawah bubble judul),
jadi tidak menabrak bubble, label, panel angka, subtitle, maupun tombol FOLLOW, dan tetap di zona aman
UI TikTok/Reels.

  python3 render/watermark.py IN.mp4 OUT.mp4 [--handle @juniart.ai] [--y 420] [--crf 18]
"""
import argparse
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compose as C  # noqa: E402


def ig_glyph(size, color):
    s = size * 4  # supersample
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w = max(4, s // 11)
    d.rounded_rectangle([w // 2, w // 2, s - w // 2, s - w // 2], s // 4, outline=color, width=w)
    r = s * .22
    d.ellipse([s / 2 - r, s / 2 - r, s / 2 + r, s / 2 + r], outline=color, width=w)
    r2 = s * .06
    d.ellipse([s * .75 - r2, s * .25 - r2, s * .75 + r2, s * .25 + r2], fill=color)
    return im.resize((size, size), Image.LANCZOS)


def make_overlay(handle, y, W=1080, H=1920):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f = C.font(C.F700, 32)
    tw = f.getlength(handle)
    g = 34
    pad, gap, ph = 22, 12, 58
    pw = int(pad + g + gap + tw + pad)
    x0, y0 = (W - pw) // 2, int(y - ph / 2)
    d = ImageDraw.Draw(ov)
    d.rounded_rectangle([x0, y0, x0 + pw, y0 + ph], ph // 2, fill=(20, 22, 26, 150))
    ov.alpha_composite(ig_glyph(g, (255, 255, 255, 235)), (x0 + pad, y0 + (ph - g) // 2))
    d.text((x0 + pad + g + gap, y0 + (ph - 42) / 2), handle, font=f, fill=(255, 255, 255, 235))
    return ov


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp")
    ap.add_argument("out")
    ap.add_argument("--handle", default="@juniart.ai")
    ap.add_argument("--y", type=int, default=420)
    ap.add_argument("--crf", type=int, default=18)
    a = ap.parse_args()
    png = os.path.join(tempfile.mkdtemp(), "wm.png")
    make_overlay(a.handle, a.y).save(png)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.inp, "-i", png,
                    "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]",
                    "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-preset", "slow", "-crf", str(a.crf),
                    "-profile:v", "high", "-c:a", "copy", "-movflags", "+faststart", a.out], check=True)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
