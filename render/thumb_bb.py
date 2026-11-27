"""Thumbnail feed 9:16 gaya "Business Breakdown": latar gelap berwarna + petak frame video buram, logo/angka besar
bercahaya di atas, dua kartu foto miring di tengah, judul tebal di bawah, tulisan kecil "Business Breakdown".
Isi penting berada di area tengah 3:4 (y 240..1680) supaya tetap utuh di grid profil Instagram.

  python3 render/thumb_bb.py FRAMES_DIR OUT_DIR [--only psb,gta] [--sheet sheet.jpg]

FRAMES_DIR/<key>/00..17.jpg = frame dari video <key> (1080x1920).
"""
import argparse
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
F800 = os.path.join(HERE, "fonts", "PlusJakartaSans-800.ttf")
W, H = 1080, 1920
TEX = os.environ.get("TN_TEX", "/tmp/claude-0/-home-user-Bbg/e4570b9b-8bb7-5f4c-a29b-693bb3cf9daa/scratchpad")

SPEC = {
    "psb": dict(logo="psb/tex/lg_persib.png", card_imgs=["psb/tex/ph_trophies.jpg", "psb/tex/ph_koreo.jpg"],
                tile_glob=["psb/tex/ph_*.jpg", "psb/tex/pl_*.jpg"], title="3x Champions.", accent="#2563EB", bg="#06122E"),
    "ps2": dict(logo="psb/tex/lg_persib.png", part="PART 2", card_imgs=["ps2/tex/ph_seoul.jpg", "ps2/tex/ph_store2.jpg"],
                tile_glob=["ps2/tex/ph_*.jpg", "psb/tex/pl_*.jpg"], title="Persib's Money Machine.", accent="#2563EB",
                bg="#06122E"),
    "fom": dict(logo="fom/tex/logo_p.png", card_imgs=["fom/tex/p_pink.jpg", "fom/tex/art_mui.jpg"],
                tile_glob=["fom/tex/p_*.jpg", "fom/tex/art_*.jpg"], title="Surviving the Fatwa.", accent="#FF3E9A",
                bg="#1A0614"),
    "kpr": dict(label="KPR · BI RATE 6%", hero="+Rp98M", card_imgs=["kfull/K06/frames/0230.png", "kfull/K12/frames/0100.png"],
                tile_glob=["kfull/K0[1-9]/frames/01[0-9]0.png", "kfull/K1[0-4]/frames/01[0-9]0.png"],
                title="Your Mortgage Just Grew.", accent="#FF3FA4", bg="#170A22"),
    "vap": dict(cards=(0, 13), label="LIQUID VAPE · 60 ML", hero="Rp120K", title="Who Takes the Cut?", accent="#A855F7", bg="#12081F"),
    "pst": dict(label="PESTAPORA · 3 DAYS", hero="Rp16B", title="More Than Tickets.", accent="#EC4899", bg="#1A0716"),
    "gta": dict(logo="gta/tex/logo.png", card_imgs=["gta/tex/p_jl.jpg", "gta/tex/shot_beach.jpg"],
                tile_glob=["gta/tex/shot_*.jpg", "gta/tex/p_*.jpg"], title="Sold Before Launch.", accent="#F472B6", bg="#150A1F"),
    "brd": dict(cards=(4, 10), label="LIQUID VAPE · PART 2", hero="1,000 Bottles", title="Your Own Brand?", accent="#22D3EE",
                bg="#04141A"),
    "nkh": dict(cards=(0, 5), label="WEDDING", hero="Rp100M", title="Who Really Profits.", accent="#F43F5E", bg="#1A060B"),
    "prk": dict(label="PARKING ATTENDANT", hero="Rp12M/mo", title="Vest & Whistle.", accent="#F97316", bg="#1A0D04"),
    "ctd": dict(label="CLOSE THE DOOR", hero="25M Subs", title="Podcast Money.", accent="#EF4444", bg="#120808"),
    "sawit": dict(label="PALM OIL · 1 HECTARE", hero="Rp55M/ha", title="Palm Oil Math.", accent="#22C55E",
                  bg="#04150A"),
    "amdk": dict(cards=(3, 17), label="BOTTLED WATER", hero="Millions/Day", title="Selling Water.", accent="#38BDF8", bg="#041320"),
    "laundry": dict(cards=(1, 3), label="COIN LAUNDRY", hero="No Cashier", title="Clean Money?", accent="#60A5FA", bg="#06101F"),
    "hotel": dict(label="30-ROOM HOTEL", hero="Rp40B", title="Don't Build a Hotel.", accent="#FBBF24", bg="#151004"),
    "tahu": dict(label="TOFU DELIVERY", hero="Rp7.5M/mo", title="Tofu on Wheels.", accent="#FACC15", bg="#141204"),
    "sepatu": dict(label="SHOE CLEANING", hero="Rp50M/mo", title="Clean Shoes, Real Cash.", accent="#FB923C",
                   bg="#170C05"),
    "ojl": dict(label="OJOL · GOTO Q3", hero="Rp441B", card_imgs=["ojl/full/O09/frames/0200.png", "ojl/full/O11/frames/0200.png"],
                tile_glob=["ojl/full/O0[1-9]/frames/01[0-9]0.png", "ojl/full/O1[0-2]/frames/01[0-9]0.png"],
                title="Where Does Your Fare Go?", accent="#00D26A", bg="#04140B"),
}
ORDER = [k for k in SPEC if k not in ("ps2", "fom", "kpr", "ojl")] + ["ps2", "fom", "kpr", "ojl"]      # nomor lama tetap; Part 2 = 15, FOOM = 16


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def font(size):
    return ImageFont.truetype(F800, size)


def crop_photo(im, aspect=.8):
    if im.width / im.height > aspect:
        w = int(im.height * aspect)
        x0 = (im.width - w) // 2
        return im.crop((x0, 0, x0 + w, im.height))
    h = int(im.width / aspect)
    y0 = (im.height - h) // 3
    return im.crop((0, y0, im.width, y0 + h))


def crop_card(im, aspect=.8):
    """area tengah frame (bebas header/subtitle): y 370..1170."""
    if im.size != (W, H):
        return crop_photo(im, aspect)
    y0, y1 = 370, 1170
    h = y1 - y0
    w = int(h * aspect)
    x0 = (im.width - w) // 2
    return im.crop((x0, y0, x0 + w, y1))


def score(im):
    a = np.asarray(crop_card(im).resize((90, 112)), dtype=np.float32)
    rg, yb = a[..., 0] - a[..., 1], (a[..., 0] + a[..., 1]) / 2 - a[..., 2]
    colorful = math.sqrt(rg.std() ** 2 + yb.std() ** 2) + .3 * math.sqrt(rg.mean() ** 2 + yb.mean() ** 2)
    return colorful + .6 * a.mean(axis=2).std()


def rounded(im, r):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), r, fill=255)
    out = im.convert("RGBA")
    out.putalpha(m)
    return out


def paste_rot(base, im, cx, cy, ang):
    r = im.rotate(ang, Image.BICUBIC, expand=True)
    base.alpha_composite(r, (int(cx - r.width / 2), int(cy - r.height / 2)))


def tracked(draw, xy, text, f, fill, track=0, anchor_center=True):
    widths = [f.getlength(c) for c in text]
    total = sum(widths) + track * (len(text) - 1)
    x, y = xy
    if anchor_center:
        x -= total / 2
    for c, w in zip(text, widths):
        draw.text((x, y), c, font=f, fill=fill)
        x += w + track
    return total


def text_layer(text, f, fill, track):
    tmp = Image.new("RGBA", (W, f.size * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    tracked(d, (W / 2, f.size * .3), text, f, fill, track)
    return tmp


def glow(layer, color, radius, strength=1.0):
    a = layer.split()[3].filter(ImageFilter.GaussianBlur(radius))
    a = a.point(lambda v: min(255, int(v * strength)))
    g = Image.new("RGBA", layer.size, color + (0,))
    g.putalpha(a)
    return g


def wrap(text, f, maxw, track):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if f.getlength(t) + track * len(t) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def build(key, frames_dir):
    sp = SPEC[key]
    acc, bgc = hexrgb(sp["accent"]), hexrgb(sp["bg"])
    files = sorted(os.listdir(os.path.join(frames_dir, key)))
    ims = [Image.open(os.path.join(frames_dir, key, f)).convert("RGB") for f in files]
    sc = [score(im) for im in ims]
    order = sorted(range(len(ims)), key=lambda i: -sc[i])
    pick = []
    for i in order:
        if all(abs(i - j) >= 4 for j in pick):
            pick.append(i)
        if len(pick) == 2:
            break
    if sp.get("cards"):
        pick = list(sp["cards"])
    rest = [i for i in range(len(ims)) if i not in pick]
    if sp.get("card_imgs"):
        cims = [Image.open(os.path.join(TEX, f)).convert("RGB") for f in sp["card_imgs"]]
        ims = ims + cims
        pick = [len(ims) - 2, len(ims) - 1]
    if sp.get("tile_glob"):
        import glob
        tl = sorted(f for g in sp["tile_glob"] for f in glob.glob(os.path.join(TEX, g)))
        random.Random(key).shuffle(tl)
        tl = [f for f in tl if os.path.relpath(f, TEX) not in sp.get("card_imgs", [])]
        base_n = len(ims)
        ims = ims + [Image.open(f).convert("RGB") for f in tl]
        rest = list(range(base_n, len(ims)))

    # ---- latar: warna dasar + cahaya aksen + petak frame buram
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - 820) / H * 1.1) ** 2)
    k = np.clip(1 - d * 1.9, 0, 1)[..., None] ** 1.6
    base = np.array(bgc, np.float32) * (1 - .35 * k) + np.array(acc, np.float32) * .30 * k
    canvas = Image.fromarray(base.clip(0, 255).astype(np.uint8)).convert("RGBA")
    rnd = random.Random(key)
    slots = [(150, 260), (930, 230), (60, 760), (1020, 720), (110, 1300), (980, 1260), (300, 1760), (800, 1790),
             (540, 120), (40, 1750), (1050, 1700), (560, 1880)]
    for n, (sx, sy) in enumerate(slots):
        im = ims[rest[(n * 5) % len(rest)]]
        t = crop_card(im, .78).resize((300, 385), Image.LANCZOS)
        t = t.filter(ImageFilter.GaussianBlur(2.2))
        t = Image.eval(t, lambda v: int(v * .34))
        t = rounded(t, 22)
        a = t.split()[3].point(lambda v: int(v * .85))
        t.putalpha(a)
        paste_rot(canvas, t, sx + rnd.uniform(-30, 30), sy + rnd.uniform(-30, 30), rnd.uniform(-10, 10))
    # vinyet + gelapkan bawah untuk judul
    vig = np.clip(1 - (np.sqrt(((xx - W / 2) / (W * .62)) ** 2 + ((yy - 860) / (H * .58)) ** 2) - .55) * .9, .25, 1)
    bot = np.clip((yy - 1150) / 500, 0, 1) * .55
    shade = (vig * (1 - bot))[..., None]
    arr = np.asarray(canvas, np.float32)
    arr[..., :3] *= shade
    canvas = Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")

    # ---- dua kartu foto miring
    for idx, (cx, cy, ang, sz) in zip(pick, ((372, 985, 7, 1.0), (712, 955, -7, 1.0))):
        c = crop_card(ims[idx], .8).resize((int(352 * sz), int(440 * sz)), Image.LANCZOS)
        card = Image.new("RGBA", (c.width + 12, c.height + 12), (255, 255, 255, 0))
        card = rounded(Image.new("RGB", card.size, (235, 238, 245)), 34)
        card.alpha_composite(rounded(c, 28), (6, 6))
        sh = Image.new("RGBA", (card.width + 120, card.height + 120), (0, 0, 0, 0))
        sh.paste((0, 0, 0, 170), (60, 70, 60 + card.width, 70 + card.height))
        sh = sh.filter(ImageFilter.GaussianBlur(26))
        paste_rot(canvas, sh, cx, cy + 14, ang)
        paste_rot(canvas, card, cx, cy, ang)

    # ---- logo / label + angka besar
    if sp.get("part"):                                  # lencana "PART 2" di atas logo/angka
        bf = font(46)
        tw = bf.getlength(sp["part"]) + 4 * len(sp["part"])
        bw, bh = int(tw + 70), 78
        badge = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        ImageDraw.Draw(badge).rounded_rectangle((0, 0, bw - 1, bh - 1), bh // 2, fill=acc + (255,))
        bl = Image.new("RGBA", (W, 140), (0, 0, 0, 0))
        bl.alpha_composite(badge, ((W - bw) // 2, 30))
        tx = text_layer(sp["part"], bf, (255, 255, 255, 255), 4)
        canvas.alpha_composite(glow(bl, acc, 26, 1.3), (0, 232))
        canvas.alpha_composite(bl, (0, 232))
        canvas.alpha_composite(tx, (0, 232 + 30 + (bh - 46) // 2 - 14))
    if sp.get("logo"):
        lg = Image.open(os.path.join(TEX, sp["logo"])).convert("RGBA")
        lg.thumbnail((560, 400 if not sp.get("part") else 360), Image.LANCZOS)
        lay = Image.new("RGBA", (W, 600), (0, 0, 0, 0))
        lay.alpha_composite(lg, ((W - lg.width) // 2, (270 if not sp.get("part") else 330) - lg.height // 2))
        canvas.alpha_composite(glow(lay, acc, 40, 1.4), (0, 230))
        canvas.alpha_composite(lay, (0, 230))
    else:
        lab = text_layer(sp["label"], font(34), acc + (255,), 7)
        canvas.alpha_composite(lab, (0, 300))
        hs = 196
        while font(hs).getlength(sp["hero"]) - 6 * len(sp["hero"]) > 960:
            hs -= 6
        hero = text_layer(sp["hero"], font(hs), (255, 255, 255, 255), -6)
        canvas.alpha_composite(glow(hero, acc, 34, 2.2), (0, 362 + (196 - hs) // 2))
        canvas.alpha_composite(glow(hero, acc, 10, 1.2), (0, 362 + (196 - hs) // 2))
        canvas.alpha_composite(hero, (0, 362 + (196 - hs) // 2))

    # ---- judul + teks kecil
    ts = 118
    while True:
        lines = wrap(sp["title"], font(ts), 960, -3)
        if len(lines) <= 2 and all(font(ts).getlength(l) - 3 * len(l) <= 980 for l in lines):
            break
        ts -= 4
    y = 1300 if len(lines) == 1 else 1262
    for ln in lines:
        lay = text_layer(ln, font(ts), (255, 255, 255, 255), -3)
        canvas.alpha_composite(glow(lay, (0, 0, 0), 16, 1.2), (0, y))
        canvas.alpha_composite(lay, (0, y))
        y += int(ts * 1.04)
    foot = text_layer("Business Breakdown", font(30), (150, 156, 168, 255), 1)
    canvas.alpha_composite(foot, (0, y + int(ts * .32) + 6))
    return canvas.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("frames")
    ap.add_argument("out")
    ap.add_argument("--only")
    ap.add_argument("--sheet")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    keys = a.only.split(",") if a.only else ORDER
    outs = []
    for k in keys:
        im = build(k, a.frames)
        p = os.path.join(a.out, f"thumb_{ORDER.index(k) + 1:02d}_{k}.jpg")
        im.save(p, quality=94)
        outs.append(im)
        print("wrote", p, file=sys.stderr)
    if a.sheet:
        cols = 5
        rows = math.ceil(len(outs) / cols)
        sh = Image.new("RGB", (cols * 270, rows * 480), (20, 20, 20))
        for i, im in enumerate(outs):
            sh.paste(im.resize((270, 480)), ((i % cols) * 270, (i // cols) * 480))
        sh.save(a.sheet, quality=88)


if __name__ == "__main__":
    main()
