"""Generator aset logo Ayam Goreng Mas Bambang (v2, arah heritage tipografi).

Semua teks dikonversi ke kurva (outline), jadi file SVG aman dibuka di
Illustrator / Inkscape / CorelDRAW / percetakan tanpa perlu install font.

Jalankan:  python3 brand-kit/generate.py
Butuh:     pip install fonttools uharfbuzz
"""
import math
import os

import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
OUT = os.path.join(HERE, "svg")

# ---------------------------------------------------------------- warna brand
TUA = "#7A1E1C"     # Merah Bata Tua (utama)
KREM = "#F3EAD9"    # Krem Santan
KUNYIT = "#C9973F"  # Kuning Kunyit
DAUN = "#3F5A3A"    # Hijau Daun Pisang
ARANG = "#2E1A17"   # Cokelat Arang


class Font:
    def __init__(self, filename):
        path = os.path.join(FONT_DIR, filename)
        self.tt = TTFont(path)
        self.glyphs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        self.upem = self.tt["head"].unitsPerEm
        bp = BoundsPen(self.glyphs)
        self.glyphs[self.tt.getBestCmap()[ord("H")]].draw(bp)
        self.cap = bp.bounds[3] / self.upem
        self.hb = hb.Font(hb.Face(hb.Blob.from_file_path(path)))

    def shape(self, text):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hb, buf, {"kern": True, "liga": True})
        return [
            (self.order[i.codepoint], p.x_advance, p.x_offset, p.y_offset)
            for i, p in zip(buf.glyph_infos, buf.glyph_positions)
        ]

    def width(self, text, size, tracking=0):
        g = self.shape(text)
        return sum(a for _, a, _, _ in g) * size / self.upem + tracking * (len(g) - 1)

    def path(self, text, size, x, y, tracking=0, anchor="start"):
        s = size / self.upem
        w = self.width(text, size, tracking)
        if anchor == "middle":
            x -= w / 2
        elif anchor == "end":
            x -= w
        pen = SVGPathPen(self.glyphs)
        cx = x
        for name, adv, xo, yo in self.shape(text):
            self.glyphs[name].draw(TransformPen(pen, (s, 0, 0, -s, cx + xo * s, y - yo * s)))
            cx += adv * s + tracking
        return pen.getCommands()

    def ink_bounds(self, text, size, x=0, y=0, tracking=0, anchor="start"):
        """Batas tinta sebenarnya (berguna untuk huruf script yang ekornya keluar)."""
        s = size / self.upem
        w = self.width(text, size, tracking)
        if anchor == "middle":
            x -= w / 2
        bp = BoundsPen(self.glyphs)
        cx = x
        for name, adv, xo, yo in self.shape(text):
            self.glyphs[name].draw(TransformPen(bp, (s, 0, 0, -s, cx + xo * s, y - yo * s)))
            cx += adv * s + tracking
        return bp.bounds  # xmin, ymin, xmax, ymax (koordinat SVG, y ke bawah)

    def arc(self, text, size, cx, cy, r, center_deg, tracking=0, bottom=False):
        s = size / self.upem
        w = self.width(text, size, tracking)
        pen = SVGPathPen(self.glyphs)
        pos = 0.0
        for name, adv, xo, yo in self.shape(text):
            mid = pos + adv * s / 2
            if bottom:
                theta = math.radians(center_deg) + (w / 2 - mid) / r
                phi = theta - math.pi
            else:
                theta = math.radians(center_deg) + (mid - w / 2) / r
                phi = theta
            px, py = cx + r * math.sin(theta), cy - r * math.cos(theta)
            du = -adv * s / 2 + xo * s
            c, sn = math.cos(phi), math.sin(phi)
            self.glyphs[name].draw(TransformPen(pen, (s * c, s * sn, s * sn, -s * c, du * c + px, du * sn + py)))
            pos += adv * s + tracking
        return pen.getCommands()


SCRIPT = Font("MrDafoe-Regular.ttf")
SERIF = Font("CormorantGaramond-Bold.ttf")


def svg_doc(w, h, body, bg=None):
    bg_rect = f'<rect width="{w:.0f}" height="{h:.0f}" fill="{bg}"/>' if bg else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" '
        f'width="{w:.0f}" height="{h:.0f}">{bg_rect}{body}</svg>\n'
    )


def p(d, fill):
    return f'<path fill="{fill}" d="{d}"/>'


def script_fit(text, max_w, max_size, cx, baseline):
    """Ukuran huruf script disesuaikan agar lebar tintanya pas max_w, dipusatkan ke cx."""
    size = max_size
    b = SCRIPT.ink_bounds(text, size)
    if b[2] - b[0] > max_w:
        size *= max_w / (b[2] - b[0])
        b = SCRIPT.ink_bounds(text, size)
    x = cx - (b[0] + b[2]) / 2
    return SCRIPT.path(text, size, x, baseline), size


# ---------------------------------------------------------------- 1. logo utama: lencana bulat
def badge(bg=TUA, ink=KREM, accent=KUNYIT):
    c = 200
    script, _ = script_fit("Mas Bambang", 316, 124, c, 238)
    body = (
        f'<circle cx="{c}" cy="{c}" r="200" fill="{bg}"/>'
        f'<circle cx="{c}" cy="{c}" r="184" fill="none" stroke="{ink}" stroke-width="1.6"/>'
        + p(SERIF.path("AYAM GORENG", 25, c, 150, 7.5, "middle"), ink)
        + p(script, ink)
        + f'<rect x="{c - 46}" y="275" width="34" height="1.6" fill="{ink}"/>'
        f'<circle cx="{c}" cy="276" r="4" fill="{accent}"/>'
        f'<rect x="{c + 12}" y="275" width="34" height="1.6" fill="{ink}"/>'
        + p(SERIF.path("RESEP RUMAHAN", 18, c, 312, 6, "middle"), ink)
    )
    return svg_doc(400, 400, body)


# ---------------------------------------------------------------- 2. wordmark
def wordmark(ink=TUA, small=None, bg=None, tagline=False):
    small = small or ink
    size = 170
    pad = 36
    b = SCRIPT.ink_bounds("Mas Bambang", size)
    ink_w, ink_h = b[2] - b[0], b[3] - b[1]
    top_size, top_tr = 26, 7
    top_w = SERIF.width("AYAM GORENG", top_size, top_tr)
    top_gap = 14
    top_h = top_size * SERIF.cap
    w = ink_w + pad * 2
    x0 = pad - b[0]
    y_script_top = pad + top_h + top_gap
    baseline = y_script_top - b[1]
    # "AYAM GORENG" rata kanan di atas kata Bambang
    top_x = pad + ink_w - top_w - 8
    body = p(SERIF.path("AYAM GORENG", top_size, top_x, pad + top_h, top_tr), small) + p(
        SCRIPT.path("Mas Bambang", size, x0, baseline), ink
    )
    h = y_script_top + ink_h + pad
    if tagline:
        tg = "KRIUKNYA KEDENGERAN SAMPAI TETANGGA"
        ty = h + 4
        body += p(SERIF.path(tg, 24, w / 2, ty + 10, 5, "middle"), small)
        h = ty + 10 + pad
    return svg_doc(w, h, body, bg)


# ---------------------------------------------------------------- 3. monogram
def monogram(bg=TUA, ink=KREM):
    c = 100
    script, _ = script_fit("Mb", 118, 150, c, 132)
    body = (
        f'<circle cx="{c}" cy="{c}" r="100" fill="{bg}"/>'
        f'<circle cx="{c}" cy="{c}" r="90" fill="none" stroke="{ink}" stroke-width="1.4"/>'
        + p(script, ink)
    )
    return svg_doc(200, 200, body)


# ---------------------------------------------------------------- 4. stempel satu warna
def stamp(ink=TUA):
    c = 200
    top = SERIF.arc("AYAM GORENG MAS BAMBANG", 24, c, c, 152, 0, tracking=3.6)
    bot = SERIF.arc("RESEP RUMAHAN", 24, c, c, 152 + 24 * SERIF.cap, 180, tracking=6, bottom=True)
    script, _ = script_fit("Mb", 150, 190, c, 236)
    dots = "".join(
        f'<circle cx="{c + 160 * math.sin(math.radians(a)):.2f}" cy="{c - 160 * math.cos(math.radians(a)):.2f}" r="4.5" fill="{ink}"/>'
        for a in (121, 239)
    )
    body = (
        f'<circle cx="{c}" cy="{c}" r="196" fill="none" stroke="{ink}" stroke-width="5"/>'
        f'<circle cx="{c}" cy="{c}" r="186" fill="none" stroke="{ink}" stroke-width="1.5"/>'
        f'<circle cx="{c}" cy="{c}" r="128" fill="none" stroke="{ink}" stroke-width="1.5"/>'
        + p(top, ink) + p(bot, ink) + dots + p(script, ink)
    )
    return svg_doc(400, 400, body)


# ---------------------------------------------------------------- 5. sampul highlight IG
def highlight(lines, bg=TUA, ink=KREM, accent=KUNYIT):
    c = 150
    size = 34 if max(len(l) for l in lines) <= 8 else 28
    lh = size * 1.12
    total = lh * (len(lines) - 1)
    body = f'<circle cx="{c}" cy="{c}" r="150" fill="{bg}"/>'
    body += f'<circle cx="{c}" cy="{c}" r="136" fill="none" stroke="{ink}" stroke-width="1.5"/>'
    y0 = c - total / 2 + size * SERIF.cap / 2
    for i, line in enumerate(lines):
        body += p(SERIF.path(line, size, c, y0 + i * lh, 4, "middle"), ink)
    body += f'<circle cx="{c}" cy="{y0 + total + 30:.1f}" r="4" fill="{accent}"/>'
    return svg_doc(300, 300, body)


# ---------------------------------------------------------------- 6. pola tegel
def tegel(bg=KREM, ink=TUA, accent=KUNYIT):
    t = 200
    r = 52
    sw = 2.4
    arcs = "".join(
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{ink}" stroke-width="{sw}"/>'
        f'<circle cx="{x}" cy="{y}" r="{r - 12}" fill="none" stroke="{ink}" stroke-width="1.2"/>'
        for x in (0, t) for y in (0, t)
    )
    m = t / 2
    d = 20
    diamond = f'<path d="M{m} {m - d} L{m + d} {m} L{m} {m + d} L{m - d} {m} Z" fill="{bg}" stroke="{ink}" stroke-width="{sw}"/>'
    petals = "".join(
        f'<path d="M{m} {m} Q{m + dx * 34 + dy * 14} {m + dy * 34 - dx * 14} {m + dx * 50} {m + dy * 50} '
        f'Q{m + dx * 34 - dy * 14} {m + dy * 34 + dx * 14} {m} {m} Z" fill="{ink}"/>'
        for dx, dy in ((1, 1), (1, -1), (-1, 1), (-1, -1))
    )
    body = arcs + petals + diamond + f'<circle cx="{m}" cy="{m}" r="7" fill="{accent}"/>'
    return svg_doc(t, t, body, bg=bg)


def profile_pic():
    """Foto profil IG: lencana memenuhi kanvas persegi krem."""
    inner = badge()
    inner = inner.split(">", 1)[1].rsplit("</svg>", 1)[0]
    body = f'<rect width="440" height="440" fill="{KREM}"/><g transform="translate(20 20)">{inner}</g>'
    return svg_doc(440, 440, body)


HIGHLIGHTS = {
    "menu": ["MENU"],
    "jam-buka": ["JAM", "BUKA"],
    "lokasi": ["LOKASI"],
    "pesan-online": ["PESAN", "ONLINE"],
    "kata-mereka": ["KATA", "MEREKA"],
}

FILES = {
    "logo-lencana-merah.svg": lambda: badge(),
    "logo-lencana-krem.svg": lambda: badge(bg=KREM, ink=TUA, accent=KUNYIT),
    "logo-lencana-hitam.svg": lambda: badge(bg=ARANG, ink=KREM, accent=KREM),
    "wordmark-merah.svg": lambda: wordmark(),
    "wordmark-krem.svg": lambda: wordmark(ink=KREM, small=KUNYIT),
    "wordmark-hitam.svg": lambda: wordmark(ink=ARANG),
    "wordmark-tagline-merah.svg": lambda: wordmark(tagline=True),
    "monogram-merah.svg": lambda: monogram(),
    "monogram-krem.svg": lambda: monogram(bg=KREM, ink=TUA),
    "stempel-merah.svg": lambda: stamp(),
    "stempel-hitam.svg": lambda: stamp(ARANG),
    "foto-profil-ig.svg": profile_pic,
    "pola-tegel.svg": tegel,
    "pola-tegel-merah.svg": lambda: tegel(bg=TUA, ink=KREM, accent=KUNYIT),
}
for key, lines in HIGHLIGHTS.items():
    FILES[f"highlight-{key}.svg"] = (lambda l: lambda: highlight(l))(lines)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in FILES.items():
        with open(os.path.join(OUT, name), "w") as f:
            f.write(fn())
    print(len(FILES), "file SVG dibuat di", OUT)
