"""Compositing video gaya sinematik neon (Liquid Vape): efek kamera & pasca-proses ala video referensi +
overlay seri Bedah Bisnis.

Efek: transisi zoom/whip antaradegan (blur radial / blur gerak + geser), guncang + zoom-punch saat impact,
kilat putih/merah, glitch RGB-split, tilt-shift (blur atas-bawah) untuk tembakan atas, bloom/glow, vinyet.
Overlay: header gelap, bubble judul, label 3D, HUD, angka besar (hero, bisa menghitung naik), subtitle,
kartu komentar, CTA follow.

  python3 render/compose_vap.py --render DIR --audio final.wav --out out/video.mp4 --comp DIR \
      [--config render/scenes/vap.json] [--words render/scenes/vap_words.json] [--only V01,V02] [--jobs 2]
"""
import argparse
import json
import math
import os
import random
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compose as C  # noqa: E402
import compose_full as CF  # noqa: E402

FPS = 30
W_, H_ = 1080, 1920
C.LABEL_COL.update({"cyan": (20, 170, 200), "pink": (226, 46, 140), "gold": (214, 150, 20)})
STYLE = {"pink": (255, 63, 164), "cyan": (44, 230, 255), "purple": (176, 116, 255), "gold": (255, 192, 40),
         "red": (255, 45, 75), "green": (61, 255, 154), "orange": (255, 130, 50)}

_yy, _xx = np.mgrid[0:H_, 0:W_].astype(np.float32)
_r = np.sqrt(((_xx - W_ / 2) / (W_ / 2)) ** 2 + ((_yy - H_ / 2) / (H_ / 2)) ** 2)
VIGNETTE = np.clip(1.0 - .38 * np.clip(_r - .55, 0, None) ** 1.6, .45, 1.0)[..., None]
_TS = np.clip((np.abs(_yy[:, :1] - H_ * .47) - H_ * .17) / (H_ * .2), 0, 1)       # tilt-shift mask (kolom 1)


# ------------------------------------------------------------------ efek kamera
def zoom_crop(img, s, dx=0.0, dy=0.0, rot=0.0):
    """perbesar s kali dari tengah (+ geser/rotasi kecil), ukuran tetap."""
    if abs(s - 1) < 1e-4 and abs(dx) < .5 and abs(dy) < .5 and abs(rot) < 1e-4:
        return img
    w, h = img.size
    cx, cy = w / 2 - dx, h / 2 - dy
    a = math.radians(rot)
    ca, sa = math.cos(a) / s, math.sin(a) / s
    # inverse affine: output (x,y) -> input
    m = (ca, sa, cx - ca * w / 2 - sa * h / 2, -sa, ca, cy + sa * w / 2 - ca * h / 2)
    return img.transform((w, h), Image.AFFINE, m, resample=Image.BILINEAR)


def radial_blur(img, amt, n=6):
    if amt < .004:
        return img
    acc = np.asarray(img, np.float32)
    for k in range(1, n):
        acc = acc + np.asarray(zoom_crop(img, 1 + amt * k / (n - 1)), np.float32)
    return Image.fromarray((acc / n).astype(np.uint8))


def motion_blur_x(img, px, n=7):
    if px < 2:
        return img
    a = np.asarray(img, np.float32)
    acc = np.zeros_like(a)
    for k in range(n):
        acc += np.roll(a, int(px * (k / (n - 1) - .5)), axis=1)
    return Image.fromarray((acc / n).astype(np.uint8))


def bloom(arr, strength=.55):
    """arr float32 0..255 (H,W,3) -> + glow dari bagian terang."""
    small = Image.fromarray(arr.astype(np.uint8)).resize((W_ // 4, H_ // 4), Image.BILINEAR)
    s = np.asarray(small, np.float32) / 255
    lum = s.max(axis=2, keepdims=True)
    bright = (s * np.clip((lum - .55) / .45, 0, 1)) * 255
    bi = Image.fromarray(bright.astype(np.uint8))
    g1 = np.asarray(bi.filter(ImageFilter.GaussianBlur(4)), np.float32)
    g2 = np.asarray(bi.filter(ImageFilter.GaussianBlur(14)), np.float32)
    g = Image.fromarray(np.clip(g1 * .6 + g2 * .9, 0, 255).astype(np.uint8)).resize((W_, H_), Image.BILINEAR)
    return arr + np.asarray(g, np.float32) * strength


def tilt_shift(img, amt):
    if amt <= 0:
        return img
    bl = img.filter(ImageFilter.GaussianBlur(9 * amt + 2))
    a = np.asarray(img, np.float32)
    b = np.asarray(bl, np.float32)
    m = (_TS * min(1.0, amt * 1.6))[..., None] if _TS.ndim == 2 else _TS
    m = np.broadcast_to(m, a.shape[:2] + (1,))
    return Image.fromarray((a * (1 - m) + b * m).astype(np.uint8))


def glitch(img, amt, seed):
    rnd = random.Random(seed)
    a = np.asarray(img).copy()
    sh = int(10 + 26 * amt)
    out = a.copy()
    out[..., 0] = np.roll(a[..., 0], sh, axis=1)
    out[..., 2] = np.roll(a[..., 2], -sh, axis=1)
    for _ in range(int(3 + 7 * amt)):
        y0 = rnd.randrange(0, H_ - 40)
        hh = rnd.randrange(8, 70)
        out[y0:y0 + hh] = np.roll(out[y0:y0 + hh], rnd.randint(-90, 90), axis=1)
    if rnd.random() < .5:
        y0 = rnd.randrange(0, H_ - 200)
        out[y0:y0 + 6] = 255 - out[y0:y0 + 6]
    return Image.fromarray(out)


def fx_state(tg, fx):
    """kembalikan parameter efek untuk detik timeline tg."""
    st = dict(scale=1.0, dx=0.0, dy=0.0, rot=0.0, radial=0.0, mblur=0.0, slide=0.0, flash=None, glitch=0.0)
    for t, g in fx["impact"]:
        d = tg - t
        if 0 <= d < .45:
            e = math.exp(-d * 9)
            st["scale"] *= 1 + .07 * g * e
            rnd = random.Random(int(tg * 1000))
            amp = 22 * g * math.exp(-d * 7)
            st["dx"] += rnd.uniform(-amp, amp)
            st["dy"] += rnd.uniform(-amp, amp) * .7
            st["rot"] += rnd.uniform(-.6, .6) * g * math.exp(-d * 7)
    for tr in fx["trans"]:
        p = (tg - tr["t"]) / .2
        if -1 <= p <= 1:
            s = 1 - abs(p)
            k = tr["kind"]
            if k.startswith("zoom"):
                st["radial"] = max(st["radial"], .16 * s)
                inward = (k == "zoom")
                st["scale"] *= 1 + (.18 if inward else .1) * s * (1 if (p < 0) == inward else .6)
            else:
                dirn = -1 if k == "whip_l" else 1
                st["mblur"] = max(st["mblur"], 160 * s)
                st["slide"] += dirn * 240 * s * (-1 if p < 0 else 1)
    for t, a, col in fx["flash"]:
        d = tg - t
        if -.03 <= d < .3:
            v = a * math.exp(-max(0, d) * 12)
            if not st["flash"] or v > st["flash"][0]:
                st["flash"] = (v, (255, 255, 255) if col == "w" else (255, 30, 60))
    for t, d in fx["glitch"]:
        if t <= tg < t + d:
            st["glitch"] = max(st["glitch"], 1 - (tg - t) / d * .5)
    return st


# ------------------------------------------------------------------ overlay
def draw_dark_header(img):
    ov = np.zeros((640, W_, 4), np.uint8)
    ov[..., :3] = (10, 5, 20)
    y = np.arange(640, dtype=np.float32)
    a = np.where(y < 300, 205, 205 * np.clip(1 - (y - 300) / 340, 0, 1) ** 1.5)
    ov[..., 3] = a[:, None].astype(np.uint8)
    img.alpha_composite(Image.fromarray(ov, "RGBA"), (0, 0))


def dotted(v):
    return f"{int(round(v)):,}".replace(",", ".")


def draw_hero(img, h, tg, city=False):
    t_in, t_out = tg - h["t0"], h["t1"] - tg
    if t_in < 0 or t_out < -.15:
        return
    parts = C.parse_rich(h["text"])
    if h.get("count"):
        c = h["count"]
        u = min(1.0, max(0.0, (tg - c["t0"]) / max(.01, c["t1"] - c["t0"])))
        u = 1 - (1 - u) ** 2.2
        val = c["frm"] + (c["to"] - c["frm"]) * u
        txt = c["fmt"].format(dotted(val))
        done = False
        new = []
        for t, hl in parts:
            if hl and not done:
                new.append((txt, True))
                done = True
            else:
                new.append((t, hl))
        parts = new
    col = STYLE.get(h.get("style", "pink"), STYLE["pink"])
    size = h.get("size", 124)
    f = C.font(C.F800, size)
    tw = C.rich_width(parts, f)
    if tw > 1000:
        f = C.font(C.F800, int(size * 1000 / tw))
        tw = C.rich_width(parts, f)
    fs = C.font(C.F700, 40)
    sub = h.get("sub", "")
    lh = int(f.size * 1.25)
    lw = int(max(tw, fs.getlength(sub)) + 160)
    layer = Image.new("RGBA", (lw, lh + 90), (0, 0, 0, 0))
    glow_l = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    d, dg = ImageDraw.Draw(layer), ImageDraw.Draw(glow_l)
    x = (lw - tw) / 2
    for t, hl in parts:
        d.text((x, 0), t, font=f, fill=col + (255,) if hl else (255, 255, 255, 255),
               stroke_width=7 if city else 0, stroke_fill=(24, 14, 36, 255))
        dg.text((x, 0), t, font=f, fill=col + (255,) if hl else (255, 255, 255, 120))
        x += f.getlength(t)
    if sub:
        d.text(((lw - fs.getlength(sub)) / 2, lh + 10), sub, font=fs, fill=(240, 232, 255, 235),
               stroke_width=4 if city else 0, stroke_fill=(24, 14, 36, 255))
    glow_l = glow_l.filter(ImageFilter.GaussianBlur(16))
    shadow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    shadow.putalpha(layer.getchannel("A").filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * .7)))
    comp = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    comp.alpha_composite(shadow, (0, 6))
    comp.alpha_composite(glow_l)
    comp.alpha_composite(glow_l)
    comp.alpha_composite(layer)
    s = 1.0 + .3 * (1 - C.ease_out_back(t_in / .28))
    a = min(1.0, t_in / .12) * (min(1.0, max(0.0, (t_out + .15) / .15)))
    if a <= .01:
        return
    if abs(s - 1) > .002:
        comp = comp.resize((max(1, int(comp.width * s)), max(1, int(comp.height * s))), Image.LANCZOS)
    if a < 1:
        comp.putalpha(comp.getchannel("A").point(lambda v: int(v * a)))
    y = h.get("y", 1440)
    img.alpha_composite(comp, (int(W_ / 2 - comp.width / 2), int(y - lh * s / 2)))


def draw_comment(img, c, tg):
    t_in = tg - c["t"]
    if t_in < 0:
        return
    w, h = 820, 150
    layer = Image.new("RGBA", (w + 30, h + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([10, 14, w + 10, h + 14], 34, fill=(0, 0, 0, 90))
    d.rounded_rectangle([0, 0, w, h], 34, fill=(255, 255, 255, 250))
    av = Image.new("RGBA", (84, 84), (0, 0, 0, 0))
    ad = ImageDraw.Draw(av)
    for r in range(42, 0, -1):
        u = r / 42
        ad.ellipse([42 - r, 42 - r, 42 + r, 42 + r],
                   fill=(int(255 * u + 157 * (1 - u)), int(63 * u + 77 * (1 - u)), int(164 * u + 255 * (1 - u)), 255))
    layer.alpha_composite(av, (30, 33))
    fn, fm, ft = C.font(C.F800, 30), C.font(C.F700, 26), C.font(C.F800, 50)
    d.text((136, 26), "kamu", font=fn, fill=(20, 18, 28))
    d.text((136 + fn.getlength("kamu ") + 4, 29), "· baru saja", font=fm, fill=(140, 136, 150))
    n = len(c["text"])
    k = min(n, int(max(0, t_in - .1) / .05))
    txt = c["text"][:k]
    d.text((136, 66), txt, font=ft, fill=(20, 18, 28))
    if k < n and int(t_in * 6) % 2 == 0:
        x = 136 + ft.getlength(txt) + 4
        d.rectangle([x, 74, x + 4, 120], fill=(255, 63, 164))
    hx, hy = w - 76, 52
    liked = t_in > .1 + n * .05 + .25
    hs = 1.0 + (.35 * math.exp(-(t_in - (.1 + n * .05 + .25)) * 8) if liked else 0)
    r = 16 * hs
    pts = []
    for i in range(40):
        a = 2 * math.pi * i / 40
        x = 16 * math.sin(a) ** 3
        y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((hx + x * r / 16, hy + 20 + y * r / 16))
    if liked:
        d.polygon(pts, fill=(255, 45, 85))
    else:
        d.line(pts + [pts[0]], fill=(150, 146, 160), width=4)
    s = C.ease_out_back(t_in / .3)
    a = min(1.0, t_in / .15)
    lay = layer.resize((max(1, int(layer.width * s)), max(1, int(layer.height * s))), Image.LANCZOS)
    if a < 1:
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    img.alpha_composite(lay, (int(W_ / 2 - lay.width / 2), int(c["y"] - lay.height / 2 + 40 * (1 - s))))


# ------------------------------------------------------------------ per adegan
def do_scene(job):
    sc, a = job
    cfg = json.load(open(a.config))
    words = json.load(open(a.words))
    subs = CF.global_chunks(words, cfg["keywords"])
    fx = cfg["fx"]
    sdir = os.path.join(a.render, sc["id"])
    anch = json.load(open(os.path.join(sdir, "anchors.json")))
    sx = anch["res"][0] / 1080
    n_out, gf0 = anch["n"], anch["global_f0"]
    done = 0
    for k in range(1, n_out + 1):
        src = os.path.join(sdir, "frames", f"{k:04d}.png")
        dst = os.path.join(a.comp, f"{gf0 + k:05d}.png")
        if not os.path.exists(src) or (a.skip_done and os.path.exists(dst)):
            continue
        t = (k - 1) / FPS
        tg = anch["t0"] + t
        img = Image.open(src).convert("RGB")
        if img.size != (W_, H_):
            img = img.resize((W_, H_), Image.LANCZOS)
        st = fx_state(tg, fx)
        if st["radial"]:
            img = radial_blur(img, st["radial"])
        if st["mblur"]:
            img = motion_blur_x(img, st["mblur"])
        img = zoom_crop(img, st["scale"] * (1.03 if (st["dx"] or st["dy"]) else 1), st["dx"] + st["slide"], st["dy"],
                        st["rot"])
        img = tilt_shift(img, sc.get("tilt", 0))
        arr = np.asarray(img, np.float32)
        city = sc.get("theme") == "city"
        arr = bloom(arr, .12 if city else .55) * (VIGNETTE * .35 + .65 if city else VIGNETTE)
        if st["flash"]:
            v, col = st["flash"]
            arr = arr * (1 - v) + np.array(col, np.float32) * v
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
        if city:
            C.draw_header(img, 470, 640)
        else:
            draw_dark_header(img)
        pos = anch["frames"][str(k)]
        if sc.get("hud"):
            hud = sc["hud"]
            C.draw_hud(img, hud, CF.hud_value(hud, t), t - hud["t"], *hud.get("pos", [56, 1430]))
        for lb in sc.get("labels", []):
            if lb["anchor"] not in pos or t > lb.get("until", 1e9):
                continue
            ax, ay = pos[lb["anchor"]]
            ax, ay = ax / sx, ay / sx
            ax = (ax - W_ / 2) * st["scale"] + W_ / 2 + st["slide"]
            ay = (ay - H_ / 2) * st["scale"] + H_ / 2
            if not (-40 < ax < 1120 and ay < 1900) or ay - lb.get("lift", 110) - 90 < 500:
                continue
            half = max(C.font(C.F800, 34).getlength(lb["title"]), 120) / 2 + 40
            ax = min(max(ax, half + 10), 1070 - half)
            C.draw_label(img, lb["title"], lb.get("sub", ""), lb["color"], ax, ay, t - lb.get("t", .2),
                         lb.get("lift", 110))
        for h in cfg["hero"]:
            if h["t0"] - .01 <= tg <= h["t1"] + .2:
                draw_hero(img, h, tg, city)
        for c in cfg.get("comments", []):
            if anch["t0"] <= c["t"] <= anch["t1"] + 5 and tg >= c["t"] and sc["id"] == "V18":
                draw_comment(img, c, tg)
        CF.draw_bubble_center(img, sc["bubble"], t - .05)
        cur = None
        for s0, s1, parts in subs:
            if s0 <= tg < s1:
                cur = (s0, parts)
        if cur:
            C.draw_subtitle(img, cur[1], 1250, tg - cur[0])
        if sc.get("cta") is not None:
            CF.draw_cta(img, t - sc["cta"])
        out = img.convert("RGB")
        if st["glitch"]:
            out = glitch(out, st["glitch"], gf0 + k)
        out.save(dst, compress_level=1)
        done += 1
    return sc["id"], done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", required=True)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--comp", required=True)
    ap.add_argument("--config", default="render/scenes/vap.json")
    ap.add_argument("--words", default="render/scenes/vap_words.json")
    ap.add_argument("--only", default=None)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--skip-done", action="store_true")
    ap.add_argument("--no-encode", action="store_true")
    ap.add_argument("--encode-only", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.comp, exist_ok=True)
    cfg = json.load(open(a.config))
    only = set(a.only.split(",")) if a.only else None
    jobs = [(sc, a) for sc in cfg["scenes"] if not only or sc["id"] in only]
    if not a.encode_only:
        if a.jobs > 1:
            with Pool(a.jobs) as pool:
                for sid, k in pool.imap_unordered(do_scene, jobs):
                    print("composited", sid, k, flush=True)
        else:
            for j in jobs:
                print("composited", *do_scene(j), flush=True)
    if a.no_encode:
        return
    frames = sorted(os.listdir(a.comp))
    first = frames[0].split(".")[0]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-start_number", str(int(first)),
                    "-i", os.path.join(a.comp, "%05d.png"), "-i", a.audio,
                    "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", a.out], check=True)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
