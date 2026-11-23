"""BYTE STUDIO: renderer grafis gaya "AI filmmaker" (ATM dstudio) untuk @ai.byteinsight.

Footage (talking head loe / klip AI) + grade sinematik + overlay animasi:
kicker mono, judul condensed besar + subjudul serif miring, angka yang menghitung naik,
kartu struk, kartu media melayang, grid "take gagal" bercoret X, caption serif + pill kata kunci,
tag model, kotak komentar CTA, end card. Semua diatur lewat satu file JSON.

  python3 render/byte_studio.py video render/scenes/byte_ep01.json out/byte_ep01.mp4 [--preview]
  python3 render/byte_studio.py cover render/scenes/byte_covers.json out/covers

Background tiap potongan (bg[]): {"src": "klip.mp4", "in": 3.2} untuk footage asli, atau
{"proc": 3} untuk studio prosedural (placeholder sampai footage loe ada).
"""
import json
import math
import os
import re
import subprocess
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
W, H, FPS = 1080, 1920, 30

FONTS = {
    "display": "BigShoulders-Bold.ttf",      # judul condensed (pengganti Anton/Bebas)
    "serif": "InstrumentSerif-Italic.ttf",   # subjudul & caption miring
    "sans": "InstrumentSans-Bold.ttf",       # pill & tag
    "mono": "GeistMono-Regular.ttf",         # label kecil gaya struk
    "monob": "GeistMono-Bold.ttf",
    "wide": "Boldonse-Regular.ttf",          # judul cover grid
}

PALETTE = {
    "accent": (214, 255, 63),     # lime: nyambung ke lampu studio Byteinsight
    "pill": (214, 255, 63),
    "pill_text": (12, 14, 10),
    "white": (246, 244, 238),
    "muted": (190, 196, 186),
    "red": (255, 64, 64),
    "bg_top": (12, 22, 40),
    "bg_bot": (3, 5, 10),
}


@lru_cache(maxsize=None)
def font(kind, size):
    from PIL import ImageFont
    return ImageFont.truetype(os.path.join(FONT_DIR, FONTS[kind]), int(size))


def hexrgb(v):
    if isinstance(v, (list, tuple)):
        return tuple(v)
    v = v.lstrip("#")
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))


# ------------------------------------------------------------------ easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_back(x, s=1.6):
    x = clamp(x) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def envelope(t, ev, fin=0.28, fout=0.22):
    """(alpha, progress_masuk) untuk event pada waktu t."""
    s, e = ev["start"], ev["end"]
    if t < s or t > e:
        return 0.0, 0.0
    pin = ease_out((t - s) / fin)
    pout = 1.0 if ev.get("hold") else ease_out((e - t) / fout)
    return min(pin, pout), pin


# ------------------------------------------------------------------ teks
def text_w(txt, f, track=0):
    if not txt:
        return 0
    return f.getlength(txt) + track * (len(txt) - 1)


def draw_text(d, xy, txt, f, fill, track=0, anchor="ls"):
    """teks dengan letter-spacing. anchor l/m/r + baseline."""
    x, y = xy
    w = text_w(txt, f, track)
    if anchor[0] == "m":
        x -= w / 2
    elif anchor[0] == "r":
        x -= w
    if track == 0:
        d.text((x, y), txt, font=f, fill=fill, anchor="l" + anchor[1])
        return w
    for ch in txt:
        d.text((x, y), ch, font=f, fill=fill, anchor="l" + anchor[1])
        x += f.getlength(ch) + track
    return w


def parse_marks(txt):
    """'10 BULAN *HILANG*' -> [('10 BULAN ', False), ('HILANG', True)]; [kata] = pill."""
    out = []
    for part in re.split(r"(\*[^*]+\*|\[[^\]]+\])", txt):
        if not part:
            continue
        if part.startswith("*"):
            out.append((part[1:-1], "accent"))
        elif part.startswith("["):
            out.append((part[1:-1], "pill"))
        else:
            out.append((part, None))
    return out


def shadowed(layer, radius=10, opacity=0.75, offset=(0, 4)):
    """tambahkan bayangan lembut di bawah isi layer RGBA."""
    a = layer.getchannel("A").filter(ImageFilter.GaussianBlur(radius))
    a = a.point(lambda v: int(v * opacity))
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    sh.putalpha(a)
    base = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    base.alpha_composite(sh, offset)
    base.alpha_composite(layer)
    return base


def rounded_mask(size, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), r, fill=255)
    return m


# ------------------------------------------------------------------ elemen overlay
# Tiap fungsi menggambar ke layer RGBA kosong seukuran kanvas; animasi masuk (geser/skala)
# dihitung dari p (0..1). Alpha keseluruhan diterapkan oleh pemanggil.

def el_kicker(layer, ev, p, pal):
    d = ImageDraw.Draw(layer)
    f = font("mono", ev.get("size", 26))
    y = ev.get("y", 150) + (1 - p) * 16
    draw_text(d, (ev.get("x", W / 2), y), ev["text"].upper(), f, pal["muted"] + (255,), track=7,
              anchor=ev.get("anchor", "ms"))


def el_title(layer, ev, p, pal):
    """judul condensed besar (bagian *aksen* berwarna) + subjudul serif miring."""
    d = ImageDraw.Draw(layer)
    size = ev.get("size", 168)
    f = font("display", size)
    y = ev.get("y", 330) + (1 - p) * 40
    parts = parse_marks(ev["text"].upper())
    track = ev.get("track", 2)
    total = sum(text_w(t, f, track) for t, _ in parts)
    if total > W - 100:                       # kecilkan otomatis biar muat
        f = font("display", size * (W - 100) / total)
        total = sum(text_w(t, f, track) for t, _ in parts)
    x = W / 2 - total / 2
    for t, kind in parts:
        col = pal["accent"] if kind else pal["white"]
        x += draw_text(d, (x, y), t, f, col + (255,), track=track)
    if ev.get("sub"):
        fs = font("serif", ev.get("sub_size", 64))
        draw_text(d, (W / 2, y + fs.size * 0.95), ev["sub"], fs, pal["white"] + (255,), anchor="ms")


def el_counter(layer, ev, p, pal, t):
    """angka besar yang menghitung naik, label mono kecil di atasnya."""
    d = ImageDraw.Draw(layer)
    k = ease_out((t - ev["start"]) / ev.get("count_dur", 1.0))
    v0, v1 = ev.get("from", 0), ev["to"]
    val = v0 + (v1 - v0) * k
    dec = ev.get("decimals", 0)
    num = f"{val:,.{dec}f}".replace(",", ".") if ev.get("id_format", True) else f"{val:,.{dec}f}"
    txt = f"{ev.get('prefix', '')}{num}{ev.get('suffix', '')}"
    f = font("display", ev.get("size", 210))
    s = ease_back(p) if ev.get("pop", True) else 1
    x, y = ev.get("x", 90), ev.get("y", 1150)
    anchor = ev.get("anchor", "ls")
    tmp = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    draw_text(td, (x, y), txt, f, pal["accent"] + (255,), track=1, anchor=anchor)
    if ev.get("label"):
        lx = x if anchor[0] == "l" else x - text_w(txt, f) / 2 if anchor[0] == "m" else x - text_w(txt, f)
        draw_text(td, (lx + 6, y - f.size * 0.86), ev["label"].upper(), font("mono", 24), pal["muted"] + (255,), track=6)
    if abs(s - 1) > 1e-3:                     # pop dari titik jangkar
        bb = tmp.getbbox()
        if bb:
            cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
            tmp = tmp.transform(tmp.size, Image.AFFINE, (1 / s, 0, cx - cx / s, 0, 1 / s, cy - cy / s),
                                resample=Image.BILINEAR)
    layer.alpha_composite(shadowed(tmp, 14, .8))


def media_image(ev, size):
    """isi kartu: gambar dari file, atau placeholder gradien bertuliskan nama slot."""
    w, h = size
    if ev.get("image") and os.path.exists(ev["image"]):
        im = Image.open(ev["image"]).convert("RGB")
        r = max(w / im.width, h / im.height)
        im = im.resize((int(im.width * r + 1), int(im.height * r + 1)), Image.LANCZOS)
        return im.crop(((im.width - w) // 2, (im.height - h) // 2, (im.width - w) // 2 + w, (im.height - h) // 2 + h))
    c1, c2 = hexrgb(ev.get("c1", "#1c3550")), hexrgb(ev.get("c2", "#0a0d14"))
    g = np.linspace(0, 1, h)[:, None, None]
    arr = (np.array(c1) * (1 - g) + np.array(c2) * g).repeat(w, 1)
    im = Image.fromarray(arr.astype(np.uint8))
    ImageDraw.Draw(im).text((w / 2, h / 2), ev.get("slot", "KLIP AI"), font=font("mono", 22),
                            fill=(140, 150, 160), anchor="mm")
    return im


def el_card(layer, ev, p, pal):
    """kartu media melayang (thumbnail project) + caption serif di bawahnya."""
    w, h = ev.get("w", 520), ev.get("h", 300)
    im = media_image(ev, (w, h)).convert("RGBA")
    im.putalpha(rounded_mask((w, h), 18))
    card = Image.new("RGBA", (w + 6, h + 6), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, w + 5, h + 5), 20, outline=(255, 255, 255, 70), width=3)
    card.alpha_composite(im, (3, 3))
    if ev.get("caption"):
        fs = font("serif", ev.get("caption_size", 46))
        grad = Image.new("RGBA", (w, 110), (0, 0, 0, 0))
        ga = np.linspace(0, 170, 110).astype(np.uint8)[:, None].repeat(w, 1)
        grad.putalpha(Image.fromarray(ga))
        card.alpha_composite(grad, (3, h - 107))
        card.putalpha(Image.fromarray(np.minimum(np.asarray(card.getchannel("A")),
                                                 np.asarray(rounded_mask(card.size, 20)))))
        draw_text(ImageDraw.Draw(card), (24, h - 22), ev["caption"], fs, pal["white"] + (255,))
    rot = ev.get("tilt", -3) * (1 - p * 0.6)
    card = card.rotate(rot, resample=Image.BICUBIC, expand=True)
    s = 0.86 + 0.14 * ease_back(p)
    card = card.resize((max(1, int(card.width * s)), max(1, int(card.height * s))), Image.LANCZOS)
    x = ev.get("x", W / 2) - card.width / 2
    y = ev.get("y", 1300) - card.height / 2 + (1 - p) * 70
    tmp = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    tmp.alpha_composite(card, (int(x), int(y)))
    layer.alpha_composite(shadowed(tmp, 22, .85, (0, 16)))


def el_receipt(layer, ev, p, pal, t):
    """kartu struk gelap: baris muncul satu per satu (nama ... nilai)."""
    rows = ev["rows"]
    fm, fb, ft = font("mono", 32), font("monob", 32), font("monob", 26)
    title = ev.get("title", "RECEIPT · BYTEINSIGHT").upper()
    need = max([text_w(title, ft, 4)] + [text_w(f"00  {r[0]}".upper(), fm, 1) + text_w(str(r[1]) if len(r) > 1 else "", fb) + 60
                                        for r in rows])
    w = int(max(ev.get("w", 560), need + 70))
    lh = 60
    h = 120 + lh * len(rows)
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 14, fill=(10, 14, 22, 205), outline=(255, 255, 255, 40), width=2)
    draw_text(d, (32, 60), title, ft, pal["muted"] + (255,), track=4)
    d.line((32, 84, w - 32, 84), fill=(255, 255, 255, 50), width=2)
    for i, row in enumerate(rows):
        k = clamp((t - ev["start"] - 0.25 - i * ev.get("row_gap", 0.35)) / 0.2)
        if k <= 0:
            continue
        a = int(255 * k)
        y = 136 + i * lh
        draw_text(d, (32, y), f"{i + 1:02d}  {row[0]}".upper(), fm, pal["white"] + (a,), track=1)
        if len(row) > 1:
            draw_text(d, (w - 32, y), str(row[1]), fb, pal["accent"] + (a,), anchor="rs")
    card = card.rotate(ev.get("tilt", 4), resample=Image.BICUBIC, expand=True)
    x = ev.get("x", 70) - (1 - p) * 60
    y = ev.get("y", 520)
    tmp = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    tmp.alpha_composite(card, (int(x), int(y)))
    layer.alpha_composite(shadowed(tmp, 18, .8, (0, 12)))


def el_caption(layer, ev, p, pal):
    """caption serif miring di tengah; [kata] jadi pill berwarna (gaya 'way easier to afford')."""
    d = ImageDraw.Draw(layer)
    fs = font("serif", ev.get("size", 60))
    fp = font("sans", int(fs.size * 0.62))
    y = ev.get("y", 1480) + (1 - p) * 18
    lines = ev["text"].split("\n")
    for li, line in enumerate(lines):
        parts = parse_marks(line)
        widths = []
        for t_, kind in parts:
            widths.append(text_w(t_, fp) + 30 if kind == "pill" else text_w(t_, fs))
        x = W / 2 - sum(widths) / 2
        ly = y + li * fs.size * 1.05
        for (t_, kind), wd in zip(parts, widths):
            if kind == "pill":
                d.rounded_rectangle((x + 2, ly - fp.size * 0.95, x + wd - 4, ly + fp.size * 0.32), 8,
                                    fill=pal["pill"] + (255,))
                draw_text(d, (x + 15, ly), t_, fp, pal["pill_text"] + (255,))
            else:
                col = pal["accent"] if kind == "accent" else pal["white"]
                draw_text(d, (x, ly), t_, fs, col + (255,))
            x += wd


def el_tag(layer, ev, p, pal):
    """tag model kecil (mis. 'KLING 3.0') + label mini di atasnya + subteks serif."""
    d = ImageDraw.Draw(layer)
    fp = font("sans", ev.get("size", 60))
    x, y = ev.get("x", 70), ev.get("y", 640)
    x -= (1 - p) * 40
    w = text_w(ev["text"], fp) + 30
    if ev.get("label"):
        draw_text(d, (x, y - fp.size * 1.25), ev["label"].upper(), font("mono", 26), pal["muted"] + (255,), track=6)
    d.rounded_rectangle((x, y - fp.size * 0.98, x + w, y + fp.size * 0.3), 8, fill=pal["pill"] + (255,))
    draw_text(d, (x + 15, y), ev["text"], fp, pal["pill_text"] + (255,))
    if ev.get("sub"):
        draw_text(d, (x + 4, y + fp.size * 1.2), ev["sub"], font("serif", 58), pal["white"] + (255,))


def el_xgrid(layer, ev, p, pal, t):
    """grid kartu 'take yang gagal' lalu dicoret X merah satu per satu."""
    cols, rows = ev.get("cols", 3), ev.get("rows", 2)
    cw, ch, gap = ev.get("cw", 230), ev.get("ch", 150), 18
    tw = cols * cw + (cols - 1) * gap
    x0, y0 = W / 2 - tw / 2, ev.get("y", 1250)
    tmp = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    for i in range(cols * rows):
        r, c = divmod(i, cols)
        kin = clamp((t - ev["start"] - i * 0.06) / 0.25)
        if kin <= 0:
            continue
        im = media_image({"c1": ["#2a3448", "#3a2a30", "#24343a"][i % 3], "c2": "#0b0d12", "slot": f"TAKE {i + 1:02d}"},
                         (cw, ch)).convert("RGBA")
        im.putalpha(rounded_mask((cw, ch), 10).point(lambda v, k=kin: int(v * k)))
        x, y = int(x0 + c * (cw + gap)), int(y0 + r * (ch + gap) + (1 - ease_out(kin)) * 30)
        tmp.alpha_composite(im, (x, y))
        kx = clamp((t - ev["start"] - ev.get("x_delay", 0.8) - i * 0.12) / 0.15)
        if kx > 0:
            d = ImageDraw.Draw(tmp)
            m = 34
            a, b = (x + m, y + m), (x + cw - m, y + ch - m)
            d.line((a[0], a[1], a[0] + (b[0] - a[0]) * kx, a[1] + (b[1] - a[1]) * kx), fill=pal["red"] + (255,), width=9)
            if kx > .5:
                k2 = (kx - .5) * 2
                d.line((x + cw - m, y + m, x + cw - m - (cw - 2 * m) * k2, y + m + (ch - 2 * m) * k2),
                       fill=pal["red"] + (255,), width=9)
    layer.alpha_composite(shadowed(tmp, 14, .7, (0, 10)))


def el_comment(layer, ev, p, pal, t):
    """kotak 'Tambahkan komentar...' lalu kata kunci CTA diketik huruf per huruf."""
    d = ImageDraw.Draw(layer)
    w, h = ev.get("w", 760), 92
    x, y = W / 2 - w / 2, ev.get("y", 1480) + (1 - p) * 40
    d.rounded_rectangle((x, y, x + w, y + h), h / 2, fill=(28, 30, 36, 225), outline=(255, 255, 255, 60), width=2)
    d.ellipse((x + 20, y + 20, x + 72, y + 72), fill=pal["accent"] + (255,))
    word = ev["keyword"]
    n = int(clamp((t - ev["start"] - 0.6) / ev.get("type_dur", 0.8)) * len(word) + 1e-6)
    f = font("sans", 36)
    if n == 0:
        draw_text(d, (x + 96, y + h / 2), ev.get("placeholder", "Tambahkan komentar..."), f, (150, 152, 160, 255), anchor="lm")
    else:
        tw = draw_text(d, (x + 96, y + h / 2), word[:n], f, pal["white"] + (255,), anchor="lm")
        if int(t * 2) % 2 == 0:
            d.line((x + 100 + tw, y + 26, x + 100 + tw, y + h - 26), fill=pal["white"] + (255,), width=3)
    d.ellipse((x + w - 74, y + 18, x + w - 18, y + h - 18), fill=(255, 255, 255, 235))
    d.polygon([(x + w - 56, y + 34), (x + w - 56, y + h - 34), (x + w - 34, y + h / 2)], fill=(20, 20, 24, 255))
    if ev.get("label"):
        draw_text(d, (W / 2, y - 28), ev["label"].upper(), font("mono", 22), pal["muted"] + (255,), track=6, anchor="ms")


def el_endcard(layer, ev, p, pal):
    d = ImageDraw.Draw(layer)
    d.rectangle((0, 0, W, H), fill=(4, 5, 8, 255))
    f = font("display", ev.get("size", 150))
    lines = ev.get("lines", ["BYTE", "INSIGHT"])
    y = H / 2 - (len(lines) - 1) * f.size * 0.45 + (1 - p) * 20
    for i, ln in enumerate(lines):
        draw_text(d, (W / 2, y + i * f.size * 0.88), ln, f, pal["white"] + (255,), track=3, anchor="ms")
    if ev.get("handle"):
        draw_text(d, (W / 2, y + len(lines) * f.size * 0.88 + 20), ev["handle"].upper(), font("mono", 26),
                  pal["accent"] + (255,), track=8, anchor="ms")


ELEMENTS = {"kicker": el_kicker, "title": el_title, "card": el_card, "caption": el_caption,
            "tag": el_tag, "endcard": el_endcard}
TIMED = {"counter": el_counter, "receipt": el_receipt, "xgrid": el_xgrid, "comment": el_comment}


# ------------------------------------------------------------------ background
def proc_studio(seed, pal):
    """studio prosedural: gradien gelap + kerucut lampu + bokeh. Placeholder sampai ada footage."""
    rng = np.random.default_rng(seed)
    bw, bh = int(W * 1.12), int(H * 1.12)
    g = np.linspace(0, 1, bh)[:, None, None] ** 0.8
    top = np.array(pal["bg_top"]) * (1.1 + 0.7 * rng.random())
    arr = (top * (1 - g) + np.array(pal["bg_bot"]) * g).repeat(bw, 1)
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
    light = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(light)
    tint = [(150, 190, 255), (255, 214, 150), (214, 255, 120)][seed % 3]
    for _ in range(rng.integers(2, 4)):                 # kerucut lampu dari atas
        x = rng.uniform(0.1, 0.9) * bw
        spread = rng.uniform(120, 300)
        lean = rng.uniform(-260, 260)
        d.polygon([(x - 18, -10), (x + 18, -10), (x + lean + spread, bh * .85), (x + lean - spread, bh * .85)],
                  fill=tint + (int(rng.uniform(40, 70)),))
        d.ellipse((x - 26, -26, x + 26, 26), fill=(255, 255, 255, 230))
    for _ in range(26):                                  # bokeh
        r = rng.uniform(6, 30)
        x, y = rng.uniform(0, bw), rng.uniform(0, bh * .6)
        d.ellipse((x - r, y - r, x + r, y + r), fill=tint + (int(rng.uniform(40, 120)),))
    light = light.filter(ImageFilter.GaussianBlur(22))
    im.alpha_composite(light)
    floor = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))     # lantai mengkilap
    fa = (np.clip((np.linspace(0, 1, bh) - .72) / .28, 0, 1) * 150).astype(np.uint8)[:, None].repeat(bw, 1)
    floor.putalpha(Image.fromarray(fa))
    im.alpha_composite(floor)
    return im.convert("RGB")


class Footage:
    """baca klip lewat ffmpeg, di-scale & crop ke 9:16."""

    def __init__(self, src, t_in, dur):
        vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}"
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(t_in), "-i", src, "-t", str(dur + 0.2),
                                   "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        self.last = None

    def next(self):
        buf = self.p.stdout.read(W * H * 3)
        if len(buf) == W * H * 3:
            self.last = Image.frombuffer("RGB", (W, H), buf)
        return self.last if self.last is not None else Image.new("RGB", (W, H))

    def close(self):
        self.p.stdout.close()
        self.p.kill()


def push_in(img, k, amt=0.06, drift=(0, 0)):
    """zoom pelan (push-in kamera) ke ukuran kanvas."""
    iw, ih = img.size
    bw = min(iw, ih * W / H)
    cw, ch = bw / (1 + amt * k), bw * H / W / (1 + amt * k)
    cx = clamp(iw / 2 + drift[0] * k, cw / 2, iw - cw / 2)
    cy = clamp(ih / 2 + drift[1] * k, ch / 2, ih - ch / 2)
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    return img.resize((W, H), Image.BILINEAR, box=box)


# ------------------------------------------------------------------ grade
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
_rr = np.sqrt(((_xx - W / 2) / (W / 2)) ** 2 + ((_yy - H / 2) / (H / 2)) ** 2)
VIGN = np.clip(1.0 - 0.42 * np.clip(_rr - 0.5, 0, None) ** 1.5, 0.4, 1.0)[..., None].astype(np.float32)
_rng = np.random.default_rng(7)
GRAIN = [(_rng.standard_normal((H // 2, W // 2, 1)) * 6).astype(np.float32) for _ in range(6)]


def grade(img, fi, strength=1.0):
    """look sinematik: kontras S-curve, bayangan teal, highlight hangat, vinyet, grain."""
    a = np.asarray(img, np.float32) / 255.0
    a = a + strength * 0.6 * (a - a ** 2) * (2 * a - 1)               # S-curve ringan
    lum = (a @ np.array([0.299, 0.587, 0.114], np.float32))[..., None]
    sh, hi = np.clip(1 - lum * 2, 0, 1), np.clip(lum * 2 - 1, 0, 1)
    a = a + strength * (sh * np.array([-0.02, 0.012, 0.035]) + hi * np.array([0.03, 0.01, -0.025]))
    a = a * VIGN
    g = GRAIN[fi % len(GRAIN)].repeat(2, 0).repeat(2, 1)
    a = np.clip(a * 255 + g, 0, 255)
    return Image.fromarray(a.astype(np.uint8))


# ------------------------------------------------------------------ video
def render_video(cfg_path, out, preview=False):
    cfg = json.load(open(cfg_path))
    base = os.path.dirname(os.path.abspath(cfg_path))
    pal = dict(PALETTE)
    pal.update({k: hexrgb(v) for k, v in cfg.get("palette", {}).items()})
    dur = cfg["duration"]
    nfr = int(dur * FPS)
    bgs = cfg["bg"]
    for i, b in enumerate(bgs):
        b["end"] = bgs[i + 1]["start"] if i + 1 < len(bgs) else dur
    events = cfg["events"]
    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    step = 3 if preview else 1
    scale = 0.5 if preview else 1
    ow, oh = int(W * scale) // 2 * 2, int(H * scale) // 2 * 2
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{ow}x{oh}",
           "-r", str(FPS / step), "-i", "-"]
    audio = cfg.get("audio")
    if audio:
        cmd += ["-i", os.path.join(base, audio) if not os.path.isabs(audio) else audio, "-shortest", "-c:a", "aac"]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20" if not preview else "28", "-preset", "medium",
            "-movflags", "+faststart", out]
    enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    cur_bg, bg_src, bg_img = None, None, None
    for fi in range(0, nfr, step):
        t = fi / FPS
        b = next(x for x in bgs if x["start"] <= t < x["end"] or x is bgs[-1])
        if b is not cur_bg:
            if bg_src:
                bg_src.close()
            bg_src, bg_img = None, None
            if "src" in b:
                src = b["src"] if os.path.isabs(b["src"]) else os.path.join(base, b["src"])
                bg_src = Footage(src, b.get("in", 0), b["end"] - b["start"])
            else:
                bg_img = proc_studio(b.get("proc", 0), pal)
            cur_bg = b
        k = (t - b["start"]) / max(0.01, b["end"] - b["start"])
        if bg_src:
            for _ in range(step):
                frame = bg_src.next()
            frame = push_in(frame, k, b.get("zoom", 0.04))
        else:
            frame = push_in(bg_img, k, b.get("zoom", 0.08), tuple(b.get("drift", (0, -40))))
        frame = grade(frame, fi, b.get("grade", 1.0)).convert("RGBA")
        # kilat putih singkat di awal tiap potongan (rasa 'cut' cepat)
        if b.get("flash", True) and t - b["start"] < 0.1 and b is not bgs[0]:
            fl = Image.new("RGBA", (W, H), (255, 255, 255, int(70 * (1 - (t - b["start"]) / 0.1))))
            frame.alpha_composite(fl)
        for ev in events:
            a, p = envelope(t, ev, ev.get("fin", 0.28), ev.get("fout", 0.22))
            if a <= 0:
                continue
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            if ev["type"] in TIMED:
                TIMED[ev["type"]](layer, ev, p, pal, t)
            else:
                ELEMENTS[ev["type"]](layer, ev, p, pal)
            if a < 0.999:
                layer.putalpha(layer.getchannel("A").point(lambda v, a=a: int(v * a)))
            frame.alpha_composite(layer)
        out_im = frame.convert("RGB")
        if scale != 1:
            out_im = out_im.resize((ow, oh), Image.BILINEAR)
        enc.stdin.write(out_im.tobytes())
        if fi % (FPS * 2) < step:
            print(f"  {t:5.1f}s / {dur}s", flush=True)
    if bg_src:
        bg_src.close()
    enc.stdin.close()
    enc.wait()
    print("DONE", out)


# ------------------------------------------------------------------ cover grid
def render_covers(cfg_path, outdir):
    """cover 9:16 gaya grid: label brand kecil di atas, judul lebar di tengah, tombol PLAY.
    Semua teks ada di area aman 3:4 (1080x1440 tengah) supaya tidak terpotong di grid profil."""
    cfg = json.load(open(cfg_path))
    base = os.path.dirname(os.path.abspath(cfg_path))
    pal = dict(PALETTE)
    pal.update({k: hexrgb(v) for k, v in cfg.get("palette", {}).items()})
    os.makedirs(outdir, exist_ok=True)
    brand = cfg.get("brand", "BYTEINSIGHT")
    safe_top = (H - 1440) // 2
    for i, c in enumerate(cfg["covers"]):
        if c.get("image"):
            ev = {"image": os.path.join(base, c["image"]) if not os.path.isabs(c["image"]) else c["image"]}
            bg = media_image(ev, (W, H))
        elif c.get("video"):
            src = c["video"] if os.path.isabs(c["video"]) else os.path.join(base, c["video"])
            fo = Footage(src, c.get("at", 1.0), 0.2)
            bg = fo.next().copy()
            fo.close()
        else:
            bg = push_in(proc_studio(c.get("proc", i), pal), 0.3)
        im = grade(bg, i, 0.8)
        dark = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * c.get("dim", 0.28))))
        im = im.convert("RGBA")
        im.alpha_composite(dark)
        d = ImageDraw.Draw(im)
        draw_text(d, (W / 2, safe_top + 44), brand, font("mono", 24), (230, 230, 230, 230), track=10, anchor="ms")
        title = c["title"].upper()
        f = font("wide", 100)
        f = font("wide", min(150, 100 * W * 0.86 / text_w(title, f)))
        tl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_text(ImageDraw.Draw(tl), (W / 2, H / 2 + f.size * 0.35), title, f, (255, 255, 255, 255), anchor="ms")
        im.alpha_composite(shadowed(tl, 16, .9, (0, 4)))
        pw, ph, py = 128, 54, safe_top + 1440 - 150
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((W / 2 - pw / 2, py, W / 2 + pw / 2, py + ph), 12, outline=(255, 255, 255, 220), width=2)
        draw_text(d, (W / 2, py + ph / 2), "PLAY", font("mono", 22), (255, 255, 255, 255), track=6, anchor="mm")
        name = c.get("name", f"cover_{i + 1:02d}")
        im.convert("RGB").save(os.path.join(outdir, name + ".jpg"), quality=92)
        print("cover", name)


if __name__ == "__main__":
    if len(sys.argv) < 4 or sys.argv[1] not in ("video", "cover"):
        print(__doc__)
        sys.exit(1)
    if sys.argv[1] == "video":
        render_video(sys.argv[2], sys.argv[3], "--preview" in sys.argv)
    else:
        render_covers(sys.argv[2], sys.argv[3])
