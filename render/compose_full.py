"""Compositing video penuh (tanpa host): header + bubble judul di tengah, label 3D,
HUD, subtitle per frasa, CTA follow, lalu encode dengan narasi lengkap.

  python3 render/compose_full.py --render out/scenes --audio narasi.mp3 --out out/final.mp4 \
      [--only S01,S02] [--encode-only]
"""
import argparse
import json
import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compose as C  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30


def global_chunks(words, keywords, max_words=3):
    keys = {k.lower() for k in keywords}
    chunks, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        gap = (nxt[0] - w[1]) if nxt else 9
        if len(cur) >= max_words or w[2].endswith((",", ".", "?", "!")) or gap > .35:
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    out = []
    for c in chunks:
        parts = []
        for i, (_, _, txt) in enumerate(c):
            bare = txt.strip(",.?!").lower()
            parts.append((txt + (" " if i < len(c) - 1 else ""), bare in keys))
        out.append((c[0][0] - .05, c[-1][1] + .5, parts))
    return out


def draw_bubble_center(img, text, t_in, y=250):
    parts = C.parse_rich(text)
    f = C.font(C.F800, 54)
    bw = C.rich_width(parts, f) + 80
    x = (img.width - (bw + 60)) / 2 + 13
    C.draw_bubble(img, text, t_in, x, y)


def draw_cta(img, t_in, y=1530):
    if t_in <= 0:
        return
    s = C.ease_out_back(t_in / .35) * (1 + .04 * math.sin(max(0, t_in - .35) * 6))
    f = C.font(C.F800, 64)
    txt = "+ FOLLOW"
    tw = f.getlength(txt)
    bw, bh = int(tw + 110), 120
    layer = Image.new("RGBA", (bw + 20, bh + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([8, 12, bw + 8, bh + 12], 60, fill=(20, 20, 24, 255))
    d.rounded_rectangle([0, 0, bw, bh], 60, fill=C.RED + (255,), outline=C.INK, width=4)
    d.text(((bw - tw) / 2, 18), txt, font=f, fill=(255, 255, 255))
    nw, nh = max(1, int(layer.width * s)), max(1, int(layer.height * s))
    layer = layer.resize((nw, nh), Image.LANCZOS)
    img.alpha_composite(layer, (int(img.width / 2 - nw / 2), int(y - nh / 2)))
    f2 = C.font(C.F700, 34)
    t2 = "Insight bisnis dengan hitungan nyata"
    a = C.ease_out((t_in - .3) / .4)
    if a > 0:
        ImageDraw.Draw(img).text(((img.width - f2.getlength(t2)) / 2, y + 85), t2, font=f2,
                                 fill=(255, 255, 255, int(255 * a)), stroke_width=4, stroke_fill=(15, 15, 18))


DAYS = ["SEN", "SEL", "RAB", "KAM", "JUM", "SAB", "MIN"]


def _card(w, h):
    layer = Image.new("RGBA", (w + 14, h + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([8, 12, w + 8, h + 12], 30, fill=(20, 20, 24, 255))
    d.rounded_rectangle([0, 0, w, h], 30, fill=(255, 255, 255, 255), outline=C.INK, width=4)
    return layer, d


def _fade_in(layer, t_in, until=None, t_local=None):
    a = C.ease_out(t_in / .3)
    if until is not None and t_local is not None:
        a *= max(0.0, min(1.0, 1 - (t_local - until) / .25))
    return a


def _place(img, layer, a, x, y, t_in):
    if a <= .01:
        return
    if a < 1:
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * a)))
    img.alpha_composite(layer, (int(x), int(y + (1 - C.ease_out(t_in / .3)) * 40)))


def draw_schedule(img, p, t_in, t_local):
    """panel jadwal kirim mingguan: 7 hari, satu hari ditandai (ikon tahu)."""
    w, h = 900, 250
    layer, d = _card(w, h)
    f1, f2 = C.font(C.F800, 34), C.font(C.F800, 30)
    d.text((36, 26), p.get("title", "JADWAL KIRIM"), font=f1, fill=C.INK)
    tag = p.get("tag", "1x SEMINGGU")
    tw = C.font(C.F800, 26).getlength(tag)
    d.rounded_rectangle([w - 36 - tw - 36, 24, w - 36, 72], 24, fill=C.RED + (255,))
    d.text((w - 36 - tw - 18, 32), tag, font=C.font(C.F800, 26), fill=(255, 255, 255))
    pw = (w - 72 - 6 * 14) / 7
    for i, day in enumerate(DAYS):
        x0 = 36 + i * (pw + 14)
        hit = day == p.get("day", "KAM")
        s = C.ease_out_back((t_in - .5) / .3) if hit else 1
        col = (255, 205, 40, 255) if (hit and t_in > .5) else (238, 241, 244, 255)
        d.rounded_rectangle([x0, 100, x0 + pw, 220], 22, fill=col)
        d.text((x0 + (pw - f2.getlength(day)) / 2, 112), day, font=f2, fill=C.INK)
        if hit and t_in > .5:
            q = 26 * max(.01, s)
            cx, cy = x0 + pw / 2, 182
            d.rounded_rectangle([cx - q, cy - q * .75, cx + q, cy + q * .75], 6, fill=(244, 194, 31, 255),
                                outline=(150, 110, 10, 255), width=3)
    _place(img, layer, _fade_in(layer, t_in, p.get("until"), t_local), (img.width - w) / 2, p.get("y", 700), t_in)


def draw_table(img, p, t_in, t_local):
    """panel database pelanggan: baris muncul satu per satu."""
    rows = p["rows"]
    cols = p.get("cols", ["NAMA", "BLOK", "BKS", "HARI"])
    cw = p.get("widths", [330, 150, 130, 220])
    w = sum(cw) + 72
    rh = 62
    h = 96 + 54 + rh * len(rows) + 24
    layer, d = _card(w, h)
    f1, fh, fr = C.font(C.F800, 34), C.font(C.F800, 24), C.font(C.F700, 32)
    d.text((36, 28), p.get("title", "DATABASE PELANGGAN"), font=f1, fill=C.INK)
    d.ellipse([w - 70, 36, w - 40, 66], fill=(76, 196, 108, 255))
    y = 96
    d.rounded_rectangle([24, y, w - 24, y + 46], 14, fill=(238, 241, 244, 255))
    x = 36
    for c, cwid in zip(cols, cw):
        d.text((x, y + 9), c, font=fh, fill=(110, 118, 128))
        x += cwid
    for k, row in enumerate(rows):
        ra = C.ease_out((t_in - .3 - k * p.get("step", .28)) / .25)
        if ra <= 0:
            continue
        y = 96 + 54 + k * rh
        x = 36 - (1 - ra) * 30
        if k % 2:
            d.rounded_rectangle([24, y - 4, w - 24, y + rh - 8], 12, fill=(248, 249, 250, int(255 * ra)))
        for j, (v, cwid) in enumerate(zip(row, cw)):
            col = C.INK if j != p.get("red_col", 2) else C.RED
            d.text((x, y + 8), str(v), font=fr, fill=col + (int(255 * ra),) if len(col) == 3 else col)
            x += cwid
    _place(img, layer, _fade_in(layer, t_in, p.get("until"), t_local), (img.width - w) / 2, p.get("y", 640), t_in)


def draw_panel(img, p, t_local):
    t_in = t_local - p.get("t", 0)
    if t_in <= 0:
        return
    if p["type"] == "schedule":
        draw_schedule(img, p, t_in, t_local)
    elif p["type"] == "table":
        draw_table(img, p, t_in, t_local)


def hud_value(hud, t):
    p = (t - hud["t"]) / max(.01, hud["dur"])
    return hud["start"] + (hud["to"] - hud["start"]) * C.ease_out(p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", required=True)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--config", default=os.path.join(HERE, "scenes", "full.json"))
    ap.add_argument("--words", default=os.path.join(HERE, "scenes", "words.json"))
    ap.add_argument("--only", default=None)
    ap.add_argument("--encode-only", action="store_true")
    ap.add_argument("--no-encode", action="store_true")
    ap.add_argument("--skip-done", action="store_true")
    ap.add_argument("--speed", type=float, default=None,
                    help="percepat render lama (speed 1.0) dengan mengambil frame terdekat")
    ap.add_argument("--comp", default=None, help="folder frame hasil compositing")
    a = ap.parse_args()

    cfg = json.load(open(a.config))
    words = json.load(open(a.words))
    subs = global_chunks(words, cfg["keywords"])
    comp_dir = a.comp or os.path.join(os.path.dirname(os.path.abspath(a.out)), "composited")
    os.makedirs(comp_dir, exist_ok=True)
    only = set(a.only.split(",")) if a.only else None

    if not a.encode_only:
        for sc in cfg["scenes"]:
            sid = sc["id"]
            if only and sid not in only:
                continue
            sdir = os.path.join(a.render, sid)
            anch = json.load(open(os.path.join(sdir, "anchors.json")))
            sx = anch["res"][0] / 1080
            r = anch.get("speed", 1.0)
            n_out, gf0 = anch["n"], anch["global_f0"]
            resample = bool(a.speed) and r == 1.0 and a.speed != 1.0
            if resample:  # render lama 1x -> ambil frame sumber terdekat
                r = a.speed
                gf0 = round(anch["t0"] / r * FPS)
                n_out = round(anch["t1"] / r * FPS) - gf0
            for k in range(1, n_out + 1):
                f = min(anch["n"], round(1 + (k - 1) * r)) if resample else k
                src = os.path.join(sdir, "frames", f"{f:04d}.png")
                g = gf0 + k
                dst = os.path.join(comp_dir, f"{g:05d}.png")
                if not os.path.exists(src) or (a.skip_done and os.path.exists(dst)):
                    continue
                t = (k - 1) / FPS * r          # waktu adegan dalam skala narasi asli
                tg = anch["t0"] + t
                img = Image.open(src).convert("RGBA")
                if img.size != (1080, 1920):
                    img = img.resize((1080, 1920), Image.LANCZOS)
                C.draw_header(img, 470, 640)
                pos = anch["frames"][str(f)]
                if sc.get("hud"):
                    hud = sc["hud"]
                    C.draw_hud(img, hud, hud_value(hud, t), t - hud["t"], *hud.get("pos", [56, 680]))
                for lb in sc.get("labels", []):
                    if lb["anchor"] not in pos or t > lb.get("until", 1e9):
                        continue
                    ax, ay = pos[lb["anchor"]]
                    ax, ay = ax / sx, ay / sx
                    if not (-40 < ax < 1120 and ay < 1900) or ay - lb.get("lift", 110) - 90 < 500:
                        continue
                    half = max(C.font(C.F800, 34).getlength(lb["title"]), 120) / 2 + 40
                    ax = min(max(ax, half + 10), 1070 - half)
                    C.draw_label(img, lb["title"], lb.get("sub", ""), lb["color"], ax, ay, t - lb.get("t", .2),
                                 lb.get("lift", 110))
                for pn in sc.get("panels", []):
                    draw_panel(img, pn, t)
                draw_bubble_center(img, sc["bubble"], t - .05)
                cur = None
                for st, en, parts in subs:
                    if st <= tg < en:
                        cur = (st, parts)
                if cur:
                    C.draw_subtitle(img, cur[1], 1250, tg - cur[0])
                if sc.get("cta"):
                    draw_cta(img, t - sc["cta"])
                img.convert("RGB").save(dst, compress_level=1)
            print("composited", sid, n_out, flush=True)

    if a.no_encode:
        return
    frames = sorted(os.listdir(comp_dir))
    first = frames[0].split(".")[0]
    cmd = ["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-start_number", str(int(first)),
           "-i", os.path.join(comp_dir, "%05d.png"), "-i", a.audio,
           "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", a.out]
    subprocess.run(cmd, check=True)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
