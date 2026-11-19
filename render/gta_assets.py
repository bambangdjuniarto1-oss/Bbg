"""Siapkan tekstur untuk video "GTA VI, Rp17 triliun sebelum rilis" dari materi promosi resmi
(rockstargames.com/VI) + peta daratan (global-land-mask) untuk globe pembeli.

Aset hak cipta TIDAK disimpan di repo: script ini mengunduh dan merakitnya ke folder lokal.

  python3 render/gta_assets.py OUTDIR [--dl DLDIR]
  (scenes_gta.py membaca folder ini dari env GTA_TEX)
"""
import argparse
import os
import re
import shutil
import subprocess

from PIL import Image, ImageDraw, ImageFont

BASE = "https://www.rockstargames.com"
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
WANT = {   # nama lokal -> awalan nama file di situs
    "keyart": "39akk424a9oo53", "shot_car": "39ak81277255o9", "shot_logo": "89834o94713o21",
    "shot_gas": "an-extended-look.0ijbsha5fo1te", "shot_night": "desktop.00.5pzu2sm-z4",
    "shot_beach": "desktop.0iky3x6.hl8fo", "shot_launch": "launch-trailer.0_q-sdrgufc.s",
    "shot_heist": "mediaDesktop", "shot_sunset": "musicDesktop", "shot_pool": "onlyInLeonidaDesktop",
    "shot_club": "screenshotsDesktop", "shot_guns": "pre-load.0h87nx-881hca", "jl_tall": "pre-load.0zuzm7cd1f3h1",
    "jl_tall2": "trailer-1", "jl_tall3": "trailer-2", "cover": "poster_full.02ig6s_80ei58",
    "ultimate": "ultimate_desktop_en_us", "logo": "poster_logo.0gjrky9to8luz", "logo_wide": "vi.0hxa9",
    "m_car": "poster.0-z03r2w7a0qd", "m_sun": "poster.01rwkio33", "m_palm": "poster.07uroypnuyvq3",
    "m_manatee": "poster.0e9tstcjv0wjq", "m_flamingo": "poster.0v1cz_bp10xu3", "m_gator": "poster.13qatrg",
    "m_crab": "poster.14d0",
}
PANELS = {  # potongan panel key art 4K (karakter & ikon resmi)
    "p_heli": (60, 60, 656, 928), "p_girl": (60, 965, 656, 2100), "p_jl": (780, 60, 1500, 900),
    "p_car": (780, 1240, 1550, 2100), "p_boat": (1920, 60, 3000, 700), "p_gator": (1730, 1650, 2330, 2100),
    "p_chain": (2390, 850, 3000, 2100), "p_rifle": (3040, 60, 3780, 1100), "p_bike": (3040, 1140, 3780, 2100),
}


def fetch(dl):
    os.makedirs(dl, exist_ok=True)
    html = subprocess.run(["curl", "-s", "-m", "60", "-A", "Mozilla/5.0", BASE + "/VI"], capture_output=True,
                          text=True).stdout
    paths = sorted(set(re.findall(r'/VI/_next/static/media/[A-Za-z0-9_~.-]+\.(?:jpg|png)', html)))
    for p in paths:
        f = os.path.join(dl, os.path.basename(p))
        if any(os.path.basename(p).startswith(v) for v in WANT.values()) and not os.path.exists(f):
            subprocess.run(["curl", "-s", "-m", "120", "-A", "Mozilla/5.0", "-o", f, BASE + p])
    svg = os.path.join(dl, "rs.svg")
    if not os.path.exists(svg):
        subprocess.run(["curl", "-sL", "-m", "60", "-A", "BbgRender/1.0", "-o", svg,
                        "https://commons.wikimedia.org/wiki/Special:FilePath/Rockstar_Games_Logo.svg"])


def find(dl, prefix):
    for f in sorted(os.listdir(dl)):
        if f.startswith(prefix) and f.endswith((".jpg", ".png")):
            return os.path.join(dl, f)
    raise FileNotFoundError(prefix)


def trim(im):
    bb = im.getchannel("A").getbbox()
    return im.crop(bb) if bb else im


def font(size, bold=True):
    for n in ("Poppins-ExtraBold.ttf", "Poppins-Bold.ttf", "Montserrat-ExtraBold.ttf"):
        p = os.path.join(FONT, n)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    fs = [f for f in os.listdir(FONT) if f.endswith((".ttf", ".otf", ".woff"))]
    return ImageFont.truetype(os.path.join(FONT, fs[0]), size)


def cover(src, out, band, band_col, text_col=(255, 255, 255), crop=None, fit=False):
    """sampul kotak game PS5 1350x1700: pita atas + key art (fit=True: muat lebar, sisa latar ungu)."""
    W_, H_, B = 1350, 1700, 150
    im = Image.open(src).convert("RGB")
    if crop:
        im = im.crop(crop)
    sc = W_ / im.width if fit else max(W_ / im.width, (H_ - B) / im.height)
    im = im.resize((int(im.width * sc + .5), int(im.height * sc + .5)), Image.LANCZOS)
    x0 = (im.width - W_) // 2
    im = im.crop((x0, 0, x0 + W_, min(im.height, H_ - B)))
    c = Image.new("RGB", (W_, H_), band_col if isinstance(band_col, tuple) else (0, 0, 0))
    if fit:
        d0 = ImageDraw.Draw(c)
        for y in range(B, H_):
            u = (y - B) / (H_ - B)
            d0.line([(0, y), (W_, y)], fill=(int(40 + 190 * u), int(22 + 60 * u), int(70 + 30 * u)))
    if not isinstance(band_col, tuple):          # gradien emas
        d = ImageDraw.Draw(c)
        for x in range(W_):
            u = x / W_
            d.line([(x, 0), (x, B)], fill=(int(200 + 40 * u), int(150 + 40 * u), int(40 + 30 * u)))
    c.paste(im, (0, B + ((H_ - B - im.height) // 2 if fit else 0)))
    d = ImageDraw.Draw(c)
    d.text((60, B / 2), band, font=font(84), fill=text_col, anchor="lm")
    c.save(out, quality=92)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--dl", default=None)
    a = ap.parse_args()
    dl = a.dl or os.path.join(a.out, "_dl")
    fetch(dl)
    os.makedirs(a.out, exist_ok=True)
    for k, pre in WANT.items():
        src = find(dl, pre)
        im = Image.open(src)
        if k.startswith(("m_", "logo")):
            im = trim(im.convert("RGBA"))
            im.thumbnail((1600, 1600), Image.LANCZOS)
            im.save(os.path.join(a.out, k + ".png"))
        else:
            im = im.convert("RGB")
            im.thumbnail((2400, 2400), Image.LANCZOS)
            im.save(os.path.join(a.out, k + ".jpg"), quality=92)
    ka = Image.open(find(dl, WANT["keyart"])).convert("RGB")
    for k, box in PANELS.items():
        ka.crop(box).save(os.path.join(a.out, k + ".jpg"), quality=92)
    cover(find(dl, WANT["cover"]), os.path.join(a.out, "cover_ps5.jpg"), "PS5", (0, 82, 204))
    cover(find(dl, WANT["cover"]), os.path.join(a.out, "cover_ult.jpg"), "ULTIMATE EDITION", None,
          (40, 20, 10))
    shutil.copy(os.path.join(dl, "rs.svg"), os.path.join(a.out, "rockstar.svg"))
    print("tekstur ->", a.out, len(os.listdir(a.out)))


if __name__ == "__main__":
    main()
