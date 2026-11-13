"""Generator aset logo Ayam Goreng Mas Bambang.

Semua teks dikonversi ke kurva (outline), jadi file SVG aman dibuka di
Illustrator / Inkscape / CorelDRAW / percetakan tanpa perlu install font.

Jalankan:  python3 brand-kit/generate.py
Butuh:     pip install fonttools uharfbuzz
"""
import math
import os

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
OUT = os.path.join(HERE, "svg")

# ---------------------------------------------------------------- warna brand
TUA = "#7B1113"     # Merah Jengger (warna utama)
CABAI = "#C1272D"   # Merah Cabai
KUNING = "#E9A23B"  # Kuning Kremes
KREM = "#F7EDE0"    # Krem Tepung
ARANG = "#2A1715"   # Cokelat Arang


class Font:
    def __init__(self, filename):
        path = os.path.join(FONT_DIR, filename)
        self.tt = TTFont(path)
        self.glyphs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        self.upem = self.tt["head"].unitsPerEm
        cap = getattr(self.tt["OS/2"], "sCapHeight", 0)
        if not cap:
            from fontTools.pens.boundsPen import BoundsPen
            bp = BoundsPen(self.glyphs)
            self.glyphs[self.tt.getBestCmap()[ord("H")]].draw(bp)
            cap = bp.bounds[3]
        self.cap = cap / self.upem
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
        """Teks lurus -> atribut d path SVG."""
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

    def fit_tracking(self, text, size, target):
        n = len(self.shape(text))
        return (target - self.width(text, size)) / (n - 1)

    def arc(self, text, size, cx, cy, r, center_deg, tracking=0, bottom=False):
        """Teks melingkar. center_deg: 0 = atas, searah jarum jam.
        Atas: baseline di radius r, huruf menghadap keluar.
        Bawah: baseline di radius r, huruf menghadap ke pusat, terbaca kiri-ke-kanan."""
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
            px = cx + r * math.sin(theta)
            py = cy - r * math.cos(theta)
            du = -adv * s / 2 + xo * s
            c, sn = math.cos(phi), math.sin(phi)
            t = (s * c, s * sn, s * sn, -s * c, du * c + px, du * sn + py)
            self.glyphs[name].draw(TransformPen(pen, t))
            pos += adv * s + tracking
        return pen.getCommands()


SLAB = Font("AlfaSlabOne-Regular.ttf")
SCRIPT = Font("Yellowtail-Regular.ttf")
SANS = Font("PlusJakartaSans-ExtraBold.ttf")
SANS_SEMI = Font("PlusJakartaSans-SemiBold.ttf")


# ---------------------------------------------------------------- simbol
# Simbol = kepala ayam bulat: jengger 3 bulatan, paruh, pial, mata, alis
# yang sedikit naik (kesan ramah & percaya diri). Kanvas 200 x 200.
HEAD = (100, 112, 62)
COMB = [(76, 58, 21), (102, 44, 25), (128, 58, 21)]
BEAK = "M150 93 L192 110 L150 127 Z"
WATTLE = (158, 142, 15)
EYE = (122, 98, 12)
PUPIL = (125.5, 98, 6)
BROW = "M106 79 Q121 68 138 77"

PALETTES = {
    "warna": dict(head=TUA, comb=CABAI, beak=KUNING, wattle=CABAI, eye=KREM, pupil=ARANG, brow=KREM),
    "terang": dict(head=KREM, comb=CABAI, beak=KUNING, wattle=CABAI, eye=TUA, pupil=KREM, brow=TUA),
}


def circle(c, fill, extra=""):
    return f'<circle cx="{c[0]}" cy="{c[1]}" r="{c[2]}" fill="{fill}"{extra}/>'


def symbol(palette="warna", mono=None, uid="s"):
    """Kembalikan grup SVG simbol (kanvas 200x200)."""
    if mono:
        # Satu warna: detail mata/alis/garis kepala dibuat transparan lewat mask.
        h = HEAD
        # mask 1: celah tipis di sekeliling kepala supaya jengger/paruh/pial terpisah
        gap = (
            f'<mask id="ga-{uid}" maskUnits="userSpaceOnUse" x="0" y="0" width="200" height="200">'
            f'<rect width="200" height="200" fill="#fff"/>'
            f'<circle cx="{h[0]}" cy="{h[1]}" r="{h[2] + 4}" fill="#000"/></mask>'
        )
        # mask 2: mata & alis dilubangi dari kepala
        face = (
            f'<mask id="fa-{uid}" maskUnits="userSpaceOnUse" x="0" y="0" width="200" height="200">'
            f'<rect width="200" height="200" fill="#fff"/>{circle(EYE, "#000")}{circle(PUPIL, "#fff")}'
            f'<path d="{BROW}" fill="none" stroke="#000" stroke-width="6" stroke-linecap="round"/></mask>'
        )
        return (
            gap + face
            + f'<g mask="url(#ga-{uid})" fill="{mono}">'
            + "".join(circle(c, mono) for c in COMB)
            + f'<path d="{BEAK}" stroke="{mono}" stroke-width="8" stroke-linejoin="round"/>'
            + circle(WATTLE, mono)
            + "</g>"
            + f'<circle cx="{h[0]}" cy="{h[1]}" r="{h[2]}" fill="{mono}" mask="url(#fa-{uid})"/>'
        )
    p = PALETTES[palette]
    return (
        "".join(circle(c, p["comb"]) for c in COMB)
        + f'<path d="{BEAK}" fill="{p["beak"]}" stroke="{p["beak"]}" stroke-width="8" stroke-linejoin="round"/>'
        + circle(WATTLE, p["wattle"])
        + circle(HEAD, p["head"])
        + circle(EYE, p["eye"])
        + circle(PUPIL, p["pupil"])
        + f'<path d="{BROW}" fill="none" stroke="{p["brow"]}" stroke-width="6" stroke-linecap="round"/>'
    )


# ---------------------------------------------------------------- wordmark
def wordmark(x, y_top, colors, size=100):
    """Susunan teks: AYAM GORENG / Mas BAMBANG / KRIUK · GURIH · JUJUR.
    Kembalikan (svg, lebar, tinggi)."""
    k = size / 100
    mas_size, slab_size = 92 * k, 100 * k
    gap = 14 * k
    w_mas = SCRIPT.width("Mas", mas_size)
    w_bam = SLAB.width("BAMBANG", slab_size)
    total = w_mas + gap + w_bam

    top_size = 34 * k
    top_base = y_top + top_size * SANS.cap
    top_tr = SANS.fit_tracking("AYAM GORENG", top_size, w_bam)

    main_base = top_base + 18 * k + slab_size * SLAB.cap

    tag_size = 19 * k
    tag_text = "KRIUK · GURIH · JUJUR"
    tag_tr = 6 * k
    w_tag = SANS_SEMI.width(tag_text, tag_size, tag_tr)
    tag_base = main_base + 22 * k + tag_size * SANS_SEMI.cap
    line_y = tag_base - tag_size * SANS_SEMI.cap / 2
    rule_w = (total - w_tag) / 2 - 16 * k

    svg = (
        f'<path fill="{colors["top"]}" d="{SANS.path("AYAM GORENG", top_size, x + w_mas + gap + 4 * k, top_base, top_tr)}"/>'
        f'<path fill="{colors["mas"]}" d="{SCRIPT.path("Mas", mas_size, x, main_base + 4 * k)}"/>'
        f'<path fill="{colors["main"]}" d="{SLAB.path("BAMBANG", slab_size, x + w_mas + gap, main_base)}"/>'
        f'<rect x="{x:.2f}" y="{line_y - 1.5 * k:.2f}" width="{rule_w:.2f}" height="{3 * k:.2f}" fill="{colors["tag"]}"/>'
        f'<rect x="{x + total - rule_w:.2f}" y="{line_y - 1.5 * k:.2f}" width="{rule_w:.2f}" height="{3 * k:.2f}" fill="{colors["tag"]}"/>'
        f'<path fill="{colors["tag"]}" d="{SANS_SEMI.path(tag_text, tag_size, x + total / 2, tag_base, tag_tr, "middle")}"/>'
    )
    return svg, total, tag_base - y_top


WM_WARNA = dict(top=CABAI, mas=CABAI, main=TUA, tag=ARANG)
WM_TERANG = dict(top=KUNING, mas=KUNING, main=KREM, tag=KREM)


def mono_wm(c):
    return dict(top=c, mas=c, main=c, tag=c)


def svg_doc(w, h, body, bg=None):
    bg_rect = f'<rect width="{w:.0f}" height="{h:.0f}" fill="{bg}"/>' if bg else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" '
        f'width="{w:.0f}" height="{h:.0f}">{bg_rect}{body}</svg>\n'
    )


# ---------------------------------------------------------------- layouts
def horizontal(sym_kw, wm_colors, bg=None, pad=40):
    wm, ww, wh = wordmark(0, 0, wm_colors)
    sym_size = 230
    s = sym_size / 200
    text_x = pad + sym_size + 26
    h = pad * 2 + sym_size
    text_y = (h - wh) / 2 + 6
    wm, ww, wh = wordmark(text_x, text_y, wm_colors)
    w = text_x + ww + pad
    body = f'<g transform="translate({pad} {pad}) scale({s})">{symbol(**sym_kw)}</g>{wm}'
    return svg_doc(w, h, body, bg)


def stacked(sym_kw, wm_colors, bg=None, pad=40):
    _, ww, wh = wordmark(0, 0, wm_colors)
    w = ww + pad * 2
    sym_size = 220
    sx = (w - sym_size) / 2
    wm, ww, wh = wordmark(pad, pad + sym_size + 16, wm_colors)
    h = pad + sym_size + 16 + wh + pad
    body = f'<g transform="translate({sx:.2f} {pad}) scale({sym_size / 200})">{symbol(**sym_kw)}</g>{wm}'
    return svg_doc(w, h, body, bg)


def stamp(ring=TUA, ink=KREM, accent=KUNING, inner=KREM, sym_kw=None):
    c = 200
    top = SANS.arc("AYAM GORENG MAS BAMBANG", 23, c, c, 152, 0, tracking=2.4)
    bot_r = 152 + 23 * SANS.cap
    bot = SANS.arc("KRIUK · GURIH · JUJUR", 22, c, c, bot_r, 180, tracking=3.2, bottom=True)
    dots = "".join(
        f'<circle cx="{c + 160 * math.sin(math.radians(a)):.2f}" cy="{c - 160 * math.cos(math.radians(a)):.2f}" r="5" fill="{accent}"/>'
        for a in (112, 248)
    )
    sym_kw = sym_kw or {"palette": "warna", "uid": "stamp"}
    s = 1.12
    body = (
        f'<circle cx="{c}" cy="{c}" r="198" fill="{ring}"/>'
        f'<circle cx="{c}" cy="{c}" r="187" fill="none" stroke="{ink}" stroke-width="3"/>'
        f'<circle cx="{c}" cy="{c}" r="133" fill="{inner}"/>'
        f'<circle cx="{c}" cy="{c}" r="133" fill="none" stroke="{ink}" stroke-width="3"/>'
        f'<path fill="{ink}" d="{top}"/><path fill="{accent}" d="{bot}"/>{dots}'
        f'<g transform="translate({c - 100 * s - 6:.2f} {c - 112 * s + 4:.2f}) scale({s})">{symbol(**sym_kw)}</g>'
    )
    return svg_doc(400, 400, body)


def app_icon():
    s = 0.86
    body = (
        f'<rect width="512" height="512" rx="112" fill="{TUA}"/>'
        f'<g transform="translate({256 - 100 * s * 2.2 - 12:.2f} {256 - 112 * s * 2.2 + 8:.2f}) scale({s * 2.2:.3f})">'
        f'{symbol("terang", uid="icon")}</g>'
    )
    return svg_doc(512, 512, body)


def pattern():
    tile = 240
    s = 0.42
    cells = []
    for i, (x, y) in enumerate([(30, 24), (150, 144)]):
        cells.append(
            f'<g transform="translate({x} {y}) scale({s})">{symbol(mono=CABAI, uid=f"p{i}")}</g>'
        )
    crumbs = "".join(
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="{KUNING}"/>'
        for x, y, r in [(170, 46, 5), (186, 62, 3.5), (160, 70, 3), (48, 168, 5), (66, 186, 3.5), (36, 196, 3)]
    )
    return svg_doc(tile, tile, "".join(cells) + crumbs, bg=TUA)


def symbol_file(**kw):
    return svg_doc(200, 200, f"<g>{symbol(**kw)}</g>")


def wordmark_file(colors, pad=30):
    wm, ww, wh = wordmark(pad, pad, colors)
    return svg_doc(ww + 2 * pad, wh + 2 * pad, wm)


FILES = {
    "logo-horizontal-warna.svg": lambda: horizontal({"palette": "warna", "uid": "h1"}, WM_WARNA),
    "logo-horizontal-terang.svg": lambda: horizontal({"palette": "terang", "uid": "h2"}, WM_TERANG, bg=TUA),
    "logo-horizontal-hitam.svg": lambda: horizontal({"mono": ARANG, "uid": "h3"}, mono_wm(ARANG)),
    "logo-horizontal-putih.svg": lambda: horizontal({"mono": "#FFFFFF", "uid": "h4"}, mono_wm("#FFFFFF")),
    "logo-tegak-warna.svg": lambda: stacked({"palette": "warna", "uid": "v1"}, WM_WARNA),
    "logo-tegak-terang.svg": lambda: stacked({"palette": "terang", "uid": "v2"}, WM_TERANG, bg=TUA),
    "simbol-warna.svg": lambda: symbol_file(palette="warna", uid="sy1"),
    "simbol-terang.svg": lambda: symbol_file(palette="terang", uid="sy2"),
    "simbol-hitam.svg": lambda: symbol_file(mono=ARANG, uid="sy3"),
    "wordmark-warna.svg": lambda: wordmark_file(WM_WARNA),
    "stempel-bulat.svg": stamp,
    "ikon-aplikasi.svg": app_icon,
    "pola-kemasan.svg": pattern,
}


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in FILES.items():
        with open(os.path.join(OUT, name), "w") as f:
            f.write(fn())
        print("ok", name)
