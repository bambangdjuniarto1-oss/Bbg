"""Compositing "Bedah Bisnis: Nikahan" — overlay seri Bedah Bisnis + efek pasca yang HALUS.

Beda dari compose_vap (yang terasa "patah"):
 - transisi antaradegan = crossfade 8 frame memakai frame ekor adegan sebelumnya (kamera keduanya tetap bergerak),
   bukan whip/zoom geser;
 - impact = zoom-punch lembut (naik cepat, turun pelan) TANPA guncang acak / rotasi;
 - glitch diganti chroma tipis (geser kanal warna kecil, tanpa potongan baris);
 - efek "pucat" (desaturasi + dingin) di adegan malam saat muka pengantin memucat.

  python3 render/compose_nkh.py --render DIR --audio final.wav --out out/video.mp4 --comp DIR \
      [--config render/scenes/nkh.json] [--words render/scenes/nkh_words.json] [--only N01,N02] [--jobs 3]
"""
import argparse
import json
import math
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compose as C  # noqa: E402
import compose_full as CF  # noqa: E402
import compose_vap as CV  # noqa: E402

FPS = 30
W_, H_ = CV.W_, CV.H_


def punch_scale(tg, punch):
    s = 1.0
    for t, g in punch:
        d = tg - t
        if -.08 <= d < .9:
            if d < 0:
                v = (d + .08) / .08
                v = v * v * (3 - 2 * v)
            else:
                v = math.exp(-d * 5.5)
            s *= 1 + .045 * g * v
    return s


def fx_state(tg, sid, fx):
    st = dict(scale=punch_scale(tg, fx["punch"]), flash=None, chroma=0.0, pale=0.0)
    for t, a, col in fx["flash"]:
        d = tg - t
        if -.05 <= d < .5:
            v = a * (min(1, (d + .05) / .05)) * math.exp(-max(0, d) * 7)
            if not st["flash"] or v > st["flash"][0]:
                st["flash"] = (v, (255, 255, 255) if col == "w" else (255, 40, 70))
    for t, a in fx["chroma"]:
        d = tg - t
        if 0 <= d < .3:
            st["chroma"] = max(st["chroma"], a * math.sin(math.pi * d / .3))
    p0, p1, psid = fx["pale"]
    if sid == psid and tg >= p0:
        u = min(1.0, (tg - p0) / (p1 - p0))
        st["pale"] = u * u * (3 - 2 * u)
    return st


def chroma(arr, amt):
    sh = int(round(14 * amt))
    if sh < 1:
        return arr
    out = arr.copy()
    out[..., 0] = np.roll(arr[..., 0], sh, axis=1)
    out[..., 2] = np.roll(arr[..., 2], -sh, axis=1)
    return out


def pale(arr, u):
    if u <= 0:
        return arr
    lum = arr.mean(axis=2, keepdims=True)
    gray = lum * np.array([.92, .98, 1.06], np.float32)
    return arr * (1 - .55 * u) + gray * (.55 * u)


def load_raw(path):
    img = Image.open(path).convert("RGB")
    if img.size != (W_, H_):
        img = img.resize((W_, H_), Image.LANCZOS)
    return img


def doc_look(arr, tg):
    """look dokumenter: kontras lembut (kurva S), sedikit desaturasi, bayangan teal / sorotan hangat,
    plus butiran film halus yang berubah tiap frame."""
    x = arr / 255.0
    x = x + .15 * (x - x * x) * (2 * x - 1)               # kurva S lembut
    lum = (x * np.array([.299, .587, .114], np.float32)).sum(axis=2, keepdims=True)
    x = lum + (x - lum) * .88
    sh = np.clip(1 - lum * 2, 0, 1)
    hi = np.clip(lum * 2 - 1, 0, 1)
    x = x + sh * np.array([-.012, .012, .03], np.float32) + hi * np.array([.035, .012, -.02], np.float32)
    rng = np.random.default_rng(int(tg * 30) + 7)
    g = rng.standard_normal((x.shape[0] // 2, x.shape[1] // 2, 1)).astype(np.float32)
    g = np.repeat(np.repeat(g, 2, axis=0), 2, axis=1)[: x.shape[0], : x.shape[1]]
    x = x + g * .022 * (.6 + .4 * (1 - lum))
    return np.clip(x, 0, 1) * 255.0


def grade(img, sc, st, tg=0.0):
    city = sc.get("theme") == "city"
    img = CV.zoom_crop(img, st["scale"])
    img = CV.tilt_shift(img, sc.get("tilt", 0))
    arr = np.asarray(img, np.float32)
    if sc.get("look") == "doc":
        arr = CV.bloom(arr, .28) * (CV.VIGNETTE * .8 + .2)
        return doc_look(arr, tg)
    arr = CV.bloom(arr, .18 if city else .5) * (CV.VIGNETTE * .6 + .4 if city else CV.VIGNETTE)
    return pale(arr, st["pale"])


def do_scene(job):
    sc, prev, a = job
    cfg = json.load(open(a.config))
    words = json.load(open(a.words))
    subs = CF.global_chunks(words, cfg["keywords"])
    fx = cfg["fx"]
    sdir = os.path.join(a.render, sc["id"])
    anch = json.load(open(os.path.join(sdir, "anchors.json")))
    sx = anch["res"][0] / 1080
    n_out, gf0 = anch["n"], anch["global_f0"]
    tail_prev = None
    if prev:
        pa = json.load(open(os.path.join(a.render, prev, "anchors.json")))
        tail_prev = (os.path.join(a.render, prev, "frames"), pa["n"], pa.get("tail", 0))
        prev_sc = next(x for x in cfg["scenes"] if x["id"] == prev)
    city = sc.get("theme") == "city"
    done = 0
    for k in range(1, n_out + 1):
        src = os.path.join(sdir, "frames", f"{k:04d}.png")
        dst = os.path.join(a.comp, f"{gf0 + k:05d}.png")
        if not os.path.exists(src) or (a.skip_done and os.path.exists(dst)):
            continue
        t = (k - 1) / FPS
        tg = anch["t0"] + t
        img = load_raw(src)
        st = fx_state(tg, sc["id"], fx)
        arr = grade(img, sc, st, tg)
        # crossfade dari ekor adegan sebelumnya: ekor diproses dengan gaya adegannya SENDIRI (bloom/tilt/vignette)
        # supaya tidak ada lonjakan terang/gelap di frame sambungan
        if tail_prev and k <= tail_prev[2]:
            pp = os.path.join(tail_prev[0], f"{tail_prev[1] + k:04d}.png")
            if os.path.exists(pp):
                u = k / (tail_prev[2] + 1)
                w = u * u * (3 - 2 * u)
                arr = grade(load_raw(pp), prev_sc, fx_state(tg, prev_sc["id"], fx), tg) * (1 - w) + arr * w
        if st["flash"]:
            v, col = st["flash"]
            arr = arr * (1 - v) + np.array(col, np.float32) * v
        arr = np.clip(arr, 0, 255)
        if st["chroma"] > 0:
            arr = chroma(arr, st["chroma"])
        img = Image.fromarray(arr.astype(np.uint8)).convert("RGBA")
        CV.draw_dark_header(img)
        pos = anch["frames"][str(k)]
        if sc.get("hud"):
            hud = sc["hud"]
            C.draw_hud(img, hud, CF.hud_value(hud, t), t - hud["t"], *hud.get("pos", [56, 1640]))
        for lb in sc.get("labels", []):
            if lb["anchor"] not in pos or t > lb.get("until", 1e9) or t < lb["t"]:
                continue
            ax, ay = pos[lb["anchor"]]
            ax, ay = ax / sx, ay / sx
            ax = (ax - W_ / 2) * st["scale"] + W_ / 2
            ay = (ay - H_ / 2) * st["scale"] + H_ / 2
            if not (-40 < ax < 1120 and ay < 1900) or ay - lb.get("lift", 110) - 90 < 500:
                continue
            half = max(C.font(C.F800, 34).getlength(lb["title"]), 120) / 2 + 40
            ax = min(max(ax, half + 10), 1070 - half)
            C.draw_label(img, lb["title"], lb.get("sub", ""), lb["color"], ax, ay, t - lb["t"], lb.get("lift", 110))
        for h in cfg["hero"]:
            if h["t0"] - .01 <= tg <= h["t1"] + .2:
                CV.draw_hero(img, h, tg, city)
        if sc["id"] == cfg.get("comment_scene"):
            for c in cfg.get("comments", []):
                if tg >= c["t"]:
                    CV.draw_comment(img, c, tg)
        elif tail_prev and prev_sc["id"] == cfg.get("comment_scene") and k <= tail_prev[2]:
            # kartu komentar memudar bersama crossfade (tidak hilang mendadak)
            lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            for c in cfg.get("comments", []):
                CV.draw_comment(lay, c, tg)
            u = k / (tail_prev[2] + 1)
            al = lay.getchannel("A").point(lambda v: int(v * (1 - u * u * (3 - 2 * u))))
            lay.putalpha(al)
            img.alpha_composite(lay)
        CF.draw_bubble_center(img, sc["bubble"], t - .05)
        if cfg.get("bisubs"):
            for s0, s1, en, idt in cfg["bisubs"]:
                if s0 <= tg < s1:
                    C.draw_subtitle_bi(img, C.parse_rich(en), idt, cfg.get("sub_y", 1235), tg - s0)
        else:
            cur = None
            for s0, s1, parts in subs:
                if s0 <= tg < s1:
                    cur = (s0, parts)
            if cur:
                C.draw_subtitle(img, cur[1], 1250, tg - cur[0])
        if sc.get("cta") is not None:
            CF.draw_cta(img, t - sc["cta"])
        img.convert("RGB").save(dst, compress_level=1)
        done += 1
    return sc["id"], done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", required=True)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--comp", required=True)
    ap.add_argument("--config", default="render/scenes/nkh.json")
    ap.add_argument("--words", default="render/scenes/nkh_words.json")
    ap.add_argument("--only", default=None)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--skip-done", action="store_true")
    ap.add_argument("--no-encode", action="store_true")
    ap.add_argument("--encode-only", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.comp, exist_ok=True)
    cfg = json.load(open(a.config))
    only = set(a.only.split(",")) if a.only else None
    ids = [sc["id"] for sc in cfg["scenes"]]
    jobs = [(sc, ids[i - 1] if i > 0 else None, a) for i, sc in enumerate(cfg["scenes"]) if not only or sc["id"] in only]
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
