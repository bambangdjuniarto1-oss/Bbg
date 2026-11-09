"""Compositor 2D: tempel header, host cutout, speech bubble, label 3D, HUD, subtitle
di atas frame render Blender, lalu gabung dengan narasi jadi MP4.

  python3 render/compose.py --scene render/scenes/s12.json --frames DIR/frames \
      --anchors DIR/anchors.json --audio narasi.mp3 --words words.json --out out.mp4 [--host host.png]
"""
import argparse
import json
import math
import os
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
F800 = os.path.join(FONT_DIR, "PlusJakartaSans-800.woff")
F700 = os.path.join(FONT_DIR, "PlusJakartaSans-700.woff")

SKY = (226, 236, 238)
RED = (215, 38, 46)
YELLOW = (255, 212, 59)
INK = (24, 24, 27)
LABEL_COL = {"green": (46, 158, 91), "red": (215, 38, 46), "orange": (224, 123, 57),
             "blue": (46, 134, 222), "purple": (124, 77, 214)}

_fonts = {}


def font(path, size):
    k = (path, size)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(path, size)
    return _fonts[k]


def ease_out_back(t):
    t = max(0.0, min(1.0, t))
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def rich_width(parts, fnt):
    return sum(fnt.getlength(t) for t, _ in parts)


def parse_rich(text):
    """'Mitra **tiap hari**' -> [('Mitra ', False), ('tiap hari', True)]"""
    out, hl = [], False
    for i, chunk in enumerate(text.split("**")):
        if chunk:
            out.append((chunk, hl))
        hl = not hl
    return out


# ------------------------------------------------------------------ layers
def draw_header(img, H0, H1):
    W = img.width
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rectangle([0, 0, W, H0], fill=SKY + (255,))
    for y in range(H0, H1):
        a = int(255 * (1 - (y - H0) / (H1 - H0)) ** 1.6)
        d.line([(0, y), (W, y)], fill=SKY + (a,))
    img.alpha_composite(ov)


def host_placeholder(w, h):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    body = (120, 132, 140, 255)
    d.ellipse([w * .08, h * .62, w * .92, h * 1.45], fill=body)
    d.ellipse([w * .3, h * .1, w * .7, h * .62], fill=(150, 160, 168, 255))
    f = font(F800, int(h * .1))
    t = "FOTO HOST"
    d.text(((w - f.getlength(t)) / 2, h * .8), t, font=f, fill=(255, 255, 255, 230))
    return im


def draw_host(img, host_img, name, t_local, x, y, w):
    h = int(w * host_img.height / host_img.width)
    hi = host_img.resize((w, h), Image.LANCZOS)
    # sedikit "bernapas" biar tidak kaku
    bob = int(3 * math.sin(t_local * 2.4))
    # bayangan halus di bawah cutout
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 50), (x + 6, y + 10 + bob), hi)
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    img.alpha_composite(hi, (x, y + bob))
    f = font(F800, 34)
    tw = f.getlength(name)
    ImageDraw.Draw(img).text((x + (w - tw) / 2, y + h + 6 + bob), name, font=f, fill=INK)
    return h


def draw_bubble(img, text, t_in, x, y):
    parts = parse_rich(text)
    f = font(F800, 54)
    tw = rich_width(parts, f)
    pw, ph = 40, 26
    bw, bh = int(tw + 2 * pw), 98
    s = ease_out_back(t_in / 0.3) if t_in < 0.3 else 1.0
    if s <= 0.01:
        return
    layer = Image.new("RGBA", (bw + 60, bh + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    ox, oy = 26, 10
    # bayangan keras kanan-bawah
    d.rounded_rectangle([ox + 7, oy + 8, ox + bw + 7, oy + bh + 8], 30, fill=(20, 20, 24, 255))
    d.polygon([(ox + 2, oy + bh * .48 + 8), (ox - 22 + 7, oy + bh * .62 + 8), (ox + 10, oy + bh * .72 + 8)],
              fill=(20, 20, 24, 255))
    d.rounded_rectangle([ox, oy, ox + bw, oy + bh], 30, fill=(255, 255, 255, 255), outline=INK, width=4)
    d.polygon([(ox + 2, oy + bh * .38), (ox - 22, oy + bh * .58), (ox + 2, oy + bh * .66)],
              fill=(255, 255, 255, 255), outline=None)
    d.line([(ox + 1, oy + bh * .38), (ox - 22, oy + bh * .58), (ox + 1, oy + bh * .66)], fill=INK, width=4)
    cx = ox + pw
    for t, hl in parts:
        d.text((cx, oy + (bh - 70) / 2 + 2), t, font=f, fill=RED if hl else INK)
        cx += f.getlength(t)
    if s != 1.0:
        nw, nh = max(1, int(layer.width * s)), max(1, int(layer.height * s))
        layer = layer.resize((nw, nh), Image.LANCZOS)
        img.alpha_composite(layer, (int(x), int(y + (bh + 40) * (1 - s) / 2)))
    else:
        img.alpha_composite(layer, (int(x), int(y)))


def draw_label(img, title, sub, color, ax, ay, t_in, lift=110):
    s = ease_out_back(t_in / 0.35)
    if s <= 0.02:
        return
    col = LABEL_COL.get(color, color)
    ft, fs = font(F800, 34), font(F700, 20)
    tw = max(ft.getlength(title), fs.getlength(sub) * 1.0 + 20)
    bw, bh = int(tw + 44), 84 if sub else 58
    lw, lh = bw + 20, bh + lift + 30
    layer = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx = lw / 2
    d.line([(cx, bh), (cx, bh + lift)], fill=(255, 255, 255, 235), width=4)
    d.ellipse([cx - 9, bh + lift - 9, cx + 9, bh + lift + 9], fill=(255, 255, 255, 255), outline=col + (255,),
              width=4)
    d.rounded_rectangle([10 + 3, 4, 10 + bw + 3, bh + 4], 14, fill=(0, 0, 0, 70))
    d.rounded_rectangle([10, 0, 10 + bw, bh], 14, fill=col + (255,))
    d.text((10 + (bw - ft.getlength(title)) / 2, 8), title, font=ft, fill=(255, 255, 255))
    if sub:
        spaced = " ".join(sub)
        d.text((10 + (bw - fs.getlength(spaced)) / 2, 50), spaced, font=fs, fill=(255, 255, 255, 225))
    nw, nh = max(1, int(lw * s)), max(1, int(lh * s))
    layer = layer.resize((nw, nh), Image.LANCZOS)
    img.alpha_composite(layer, (int(ax - nw / 2), int(ay - nh + 30 * s - 9 * s)))


def draw_hud(img, hud, value, t_in, x, y):
    a = ease_out(t_in / 0.3)
    if a <= 0.01:
        return
    w, h = 500, 150
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([0, 0, w, h], 22, fill=(28, 32, 38, 215))
    fc = font(F800, 22)
    d.text((26, 20), hud["title"], font=fc, fill=(220, 225, 230))
    fn = font(F800, 58)
    num = hud.get("prefix", "") + f"{int(round(value)):,}".replace(",", ".")
    d.text((26, 52), num, font=fn, fill=YELLOW)
    fu = font(F700, 28)
    d.text((32 + fn.getlength(num), 78), hud.get("unit", ""), font=fu, fill=(220, 225, 230))
    frac = max(0.0, min(1.0, value / hud["max"]))
    d.rounded_rectangle([26, 124, w - 26, 136], 6, fill=(70, 76, 84))
    if frac > 0:
        bar = (76, 196, 108) if (frac >= .999 and hud.get("green_when_full")) else YELLOW
        d.rounded_rectangle([26, 124, 26 + (w - 52) * frac, 136], 6, fill=bar)
    fm = font(F700, 22)
    tgt = hud.get("target_text", f"target {hud['max']:,}".replace(",", "."))
    d.text((w - 26 - fm.getlength(tgt), 21), tgt, font=fm, fill=(160, 168, 176))
    if a < 1:
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * a)))
    img.alpha_composite(layer, (int(x - (1 - a) * 40), int(y)))


def draw_subtitle(img, parts, y, t_in):
    f = font(F800, 70)
    tw = rich_width(parts, f)
    x = (img.width - tw) / 2
    s = 0.85 + 0.15 * ease_out_back(t_in / 0.18)
    layer = Image.new("RGBA", (int(tw + 60), 130), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx = 30
    for t, hl in parts:
        d.text((cx, 20), t, font=f, fill=YELLOW if hl else (255, 255, 255), stroke_width=7,
               stroke_fill=(15, 15, 18))
        cx += f.getlength(t)
    sh = layer.getchannel("A").filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * .45))
    shadow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    shadow.putalpha(sh)
    if s != 1:
        nw, nh = int(layer.width * s), int(layer.height * s)
        layer, shadow = layer.resize((nw, nh), Image.LANCZOS), shadow.resize((nw, nh), Image.LANCZOS)
    px = int(img.width / 2 - layer.width / 2)
    py = int(y - layer.height / 2)
    img.alpha_composite(shadow, (px + 4, py + 6))
    img.alpha_composite(layer, (px, py))


# ------------------------------------------------------------------ build
def subtitle_chunks(words, scene):
    t0, t1 = scene["t_start"], scene["t_end"]
    ws = [w for w in words if t0 - 0.05 <= w[0] < t1]
    keys = {k.lower() for k in scene.get("keywords", [])}
    chunks, cur = [], []
    if scene.get("chunks"):
        i = 0
        for n in scene["chunks"]:
            chunks.append(ws[i:i + n])
            i += n
        ws = []
    for w in ws:
        cur.append(w)
        if len(cur) >= scene.get("words_per_chunk", 3) or w[2].endswith((",", ".", "?", "!")):
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    out = []
    for c in [c for c in chunks if c]:
        parts = []
        for i, (_, _, txt) in enumerate(c):
            bare = txt.strip(",.?!").lower()
            parts.append((txt + (" " if i < len(c) - 1 else ""), bare in keys))
        out.append((c[0][0] - t0, parts))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", required=True)
    ap.add_argument("--frames", required=True)
    ap.add_argument("--anchors", required=True)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--words", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--host")
    a = ap.parse_args()

    scene = json.load(open(a.scene))
    anch = json.load(open(a.anchors))
    words = json.load(open(a.words))
    fps = anch["fps"]
    W, H = anch["res"]
    sx = W / 1080
    host_img = Image.open(a.host).convert("RGBA") if a.host else host_placeholder(240, 240)
    subs = subtitle_chunks(words, scene)
    frames = sorted(os.listdir(a.frames))
    tmp = tempfile.mkdtemp(dir=os.path.dirname(os.path.abspath(a.out)))
    hud = scene.get("hud")
    for fname in frames:
        fno = int(fname.split(".")[0])
        t = (fno - 1) / fps
        img = Image.open(os.path.join(a.frames, fname)).convert("RGBA")
        if img.size != (1080, 1920):
            img = img.resize((1080, 1920), Image.LANCZOS)
        pos = anch["frames"][str(fno)]
        draw_header(img, 470, 640)
        if hud:
            p = (t - hud["t"]) / max(0.01, hud["dur"])
            v = hud["start"] + (hud["to"] - hud["start"]) * ease_out(p) ** 1.2
            draw_hud(img, hud, v, t - hud["t"], *hud.get("pos", [56, 680]))
        # label 3D (di atas header, posisi dikunci ke titik 3D hasil render)
        for lb in scene.get("labels", []):
            if lb["anchor"] not in pos:
                continue
            ax, ay = pos[lb["anchor"]]
            ax, ay = ax / sx, ay / sx
            if not (-40 < ax < 1120 and 0 < ay < 1900):
                continue
            ax = min(max(ax, 150), 930)
            draw_label(img, lb["title"], lb.get("sub", ""), lb["color"], ax, ay, t - lb["t"],
                       lb.get("lift", 110))
        hh = draw_host(img, host_img, scene["host_name"], t, 70, 222, 240)
        _ = hh
        draw_bubble(img, scene["bubble"], t - scene.get("bubble_t", 0.0), 330, 250)
        cur = None
        for st, parts in subs:
            if t >= st:
                cur = (st, parts)
        if cur:
            draw_subtitle(img, cur[1], 1250, t - cur[0])
        img.convert("RGB").save(os.path.join(tmp, fname), compress_level=1)

    dur = len(frames) / fps
    cmd = ["ffmpeg", "-v", "error", "-y", "-framerate", str(fps), "-start_number", frames[0].split(".")[0], "-i", os.path.join(tmp, "%04d.png"),
           "-ss", str(scene["t_start"]), "-t", str(dur), "-i", a.audio,
           "-af", f"afade=t=in:d=0.08,afade=t=out:st={max(0.0, dur - 0.15):.3f}:d=0.15",
           "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", a.out]
    subprocess.run(cmd, check=True)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
