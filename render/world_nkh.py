"""Aset 3D video "Bedah Bisnis: Nikahan Rp100 Juta" — gabungan kota diorama siang + dunia neon
(dipakai bersama world_vap). Semua generik, tanpa merek.

Isi: pengantin pria (Dimas, beskap + peci) & wanita (kebaya + siger), tamu berbatik, amplop & kotak amplop,
gedung resepsi + janur kuning, tenda pesta, meja bundar, prasmanan, pelaminan, piring nasi (grid 1.000 porsi),
toko & van katering (rolling door bisa ditutup + papan TUTUP), koki pemilik katering, kalender neon,
timbangan neon, jebakan tikus berisi uang, hati neon.
"""
import math
import random

import bpy

import lowpoly as lp
import world as W
import world_hotel as H
import world_laundry as L
import world_prk as R
import world_pst as P
import world_vap as V

lp.PAL.update({
    "wd_wall": "#FBF6EE", "wd_wall2": "#EADFCB", "wd_trim": "#C9A45C", "wd_roof": "#B85C4A", "wd_glass": "#A9CFDD",
    "wd_gold": "#D9A93A", "wd_cream": "#F6EEDC", "wd_red": "#B0263A", "wd_white": "#FFFFFF", "wd_pink": "#F2A7B8",
    "wd_rose": "#E0567A", "wd_leaf": "#3F9B4A", "janur": "#EAD34C", "janur2": "#C8B232", "wd_carpet": "#A3233A",
    "wd_tent": "#FFFDF8", "wd_pole": "#D8CFC0", "tbl_cloth": "#FFFFFF", "tbl_sash": "#E9B9C6", "chair_w": "#F1ECE4",
    "chafing": "#C9CED6", "chafing2": "#8E949E", "rice": "#FAF7F0", "food1": "#C8692E", "food2": "#5E9A3A",
    "food3": "#E2B23C", "plate": "#F4F4F2", "env": "#FFFFFF", "env2": "#E4DDD0", "env_gold": "#D9A93A",
    "abox": "#F7E7EC", "groom_suit": "#22232F", "groom_sh": "#F3F1EA", "peci": "#121218", "bride_keb": "#FFF8F0",
    "batik": "#7A4E2A", "siger": "#E0B040", "chef": "#FFFFFF", "kt_wall": "#FFF3E2", "kt_awn": "#E2563B",
    "kt_awn2": "#FFFFFF", "kt_dark": "#3A2E2A", "shutter": "#A2A8B0", "shutter2": "#838991", "tutup": "#D7263D",
    "cal_bg": "#140C26", "cal_cell": "#2A1D4A", "wood": "#B98A55", "wood2": "#8C6238", "spring": "#C7CCD4",
    "skin_dimas": "#E3A888",
})

BATIK = ["#8A4B2A", "#2B5D8A", "#7A2E4A", "#2F6B4A", "#B06A22", "#4B3C8A", "#9A3B2E"]
SKIN = ["skin1", "skin2", "skin3"]
HEAD_Z = 1.66                       # pusat kepala karakter (skala 1)


def _hat(parts, mb_fn, name):
    mb = W.MB(name)
    mb_fn(mb)
    ob = mb.build()
    ob.parent = parts["body"]
    return ob


# ------------------------------------------------------------------ karakter
def groom(name, loc=(0, 0, 0), rot=0.0, s=L.CH_S, skin="skin_dimas"):
    """pengantin pria: beskap gelap, kemeja putih, peci hitam, bunga melati di dada."""
    lk = dict(skin=skin, top="groom_suit", sleeve="groom_suit", bottom="groom_suit", shoe="shoe_dk", hair="short",
              hair_col="hair_blk", acc=())
    parts = L.character(name, lk, loc, rot, s)

    def deco(mb):
        mb.cyl(0, .01, HEAD_Z + .12, HEAD_Z + .33, .262, "peci", n=16)           # peci
        mb.box(-.07, -.205, 1.05, .07, -.17, 1.42, "groom_sh")                    # kemeja di belahan
        for k in range(4):                                                        # untaian melati
            L.ball(mb, .14, -.21, 1.36 - k * .07, .035, "wd_white", seg=6, rings=4)
        mb.box(-.2, -.215, .9, .2, -.17, .97, "wd_gold")                          # sabuk emas
    parts["deco"] = _hat(parts, deco, name + "_deco")
    return parts


def bride(name, loc=(0, 0, 0), rot=0.0, s=L.CH_S):
    """pengantin wanita: kebaya putih, kain batik, sanggul + siger emas + selendang."""
    lk = dict(skin="skin1", top="bride_keb", sleeve="bride_keb", bottom="batik", shoe="shoe_w", hair="bun",
              hair_col="hair_blk", acc=())
    parts = L.character(name, lk, loc, rot, s)

    def deco(mb):
        n = 9
        for k in range(n):                                                         # siger (mahkota setengah lingkar)
            a = math.pi * (.15 + .7 * k / (n - 1))
            x, y = .25 * math.cos(a), -.06 - .19 * math.sin(a) * .9
            h = .1 + .09 * math.sin(math.pi * k / (n - 1))
            mb.box(x - .035, y - .015, HEAD_Z + .2, x + .035, y + .015, HEAD_Z + .2 + h, "siger")
        L.tube(mb, 0, 0, .4, 1.0, .3, .26, .2, .17, "batik", n=14)                  # kain panjang
        mb.box(-.32, .05, .95, -.27, .12, 1.45, "wd_pink")                         # selendang
        for k in range(3):
            L.ball(mb, -.15 + k * .15, -.2, 1.3, .04, "wd_rose", seg=6, rings=4)
    parts["deco"] = _hat(parts, deco, name + "_deco")
    return parts


def guest(name, k, loc=(0, 0, 0), rot=0.0, hold=None):
    """tamu kondangan: kemeja/kebaya batik warna-warni, sebagian berhijab."""
    rr = random.Random(k * 11 + 5)
    top = BATIK[k % len(BATIK)]
    hair = rr.choice(("short", "hijab", "short", "long", "bun"))
    lk = dict(skin=SKIN[k % 3], top=top, sleeve=top, bottom=rr.choice(("c_black", "c_khaki", "batik", "c_denim")),
              shoe=rr.choice(("shoe_w", "shoe_dk")), hair=hair,
              hair_col={"hijab": rr.choice(("hij_cream", "hij_navy", "wd_pink"))}.get(hair, "hair_blk"), acc=())
    return L.character(name, lk, loc, rot, L.CH_S, hold)


def chef(name, loc=(0, 0, 0), rot=0.0, s=L.CH_S):
    """pemilik katering: baju koki putih, celemek, topi koki."""
    lk = dict(skin="skin2", top="chef", sleeve="chef", bottom="c_black", shoe="shoe_dk", hair="short",
              hair_col="hair_blk", acc=("apron",))
    parts = L.character(name, lk, loc, rot, s)

    def deco(mb):
        mb.cyl(0, .01, HEAD_Z + .14, HEAD_Z + .42, .2, "chef", n=14)
        L.ball(mb, 0, .01, HEAD_Z + .5, .27, "chef", seg=12, rings=6, sz=.16)
        for k in range(3):
            L.ball(mb, -.06, -.2, 1.32 - k * .12, .025, "c_black", seg=6, rings=3)
    parts["deco"] = _hat(parts, deco, name + "_deco")
    return parts


# ------------------------------------------------------------------ amplop & uang
def env_mb(mb, x, y, z, s=1.0, upright=False, key="env"):
    """amplop putih (rebah atau berdiri menghadap -Y) dengan lipatan & segel emas."""
    w, h, t = .9 * s, .55 * s, .035 * s
    if not upright:
        mb.box(x - w / 2, y - h / 2, z, x + w / 2, y + h / 2, z + t, key)
        mb.poly([(x - w / 2, y + h / 2, z + t + .002), (x + w / 2, y + h / 2, z + t + .002), (x, y, z + t + .002)],
                [(0, 1, 2)], "env2")
        mb.box(x - .06 * s, y - .04 * s, z + t, x + .06 * s, y + .04 * s, z + t + .006, "env_gold")
    else:
        mb.box(x - w / 2, y - t, z, x + w / 2, y, z + h, key)
        mb.poly([(x - w / 2, y - t - .002, z + h), (x + w / 2, y - t - .002, z + h), (x, y - t - .002, z + h / 2)],
                [(0, 1, 2)], "env2")
        mb.box(x - .06 * s, y - t - .006, z + h / 2 - .04 * s, x + .06 * s, y - t, z + h / 2 + .04 * s, "env_gold")


def envelope(name, loc=(0, 0, 0), s=1.0, upright=False):
    mb = W.MB(name)
    env_mb(mb, 0, 0, 0, s, upright)
    return mb.build(loc)


def envelope_pile(name, n, loc=(0, 0, 0), r=1.4, s=1.0, seed=3):
    """tumpukan amplop berserakan (dihitung di meja)."""
    rnd = random.Random(seed)
    mb = W.MB(name)
    for k in range(n):
        a, d = rnd.uniform(0, 2 * math.pi), r * math.sqrt(rnd.random())
        env_mb(mb, d * math.cos(a), d * math.sin(a), k * .012 * s, s * rnd.uniform(.9, 1.05))
    ob = mb.build(loc)
    ob.rotation_euler.z = rnd.uniform(-.2, .2)
    return ob


def amplop_box(name, loc=(0, 0, 0), s=1.0):
    """meja penerima tamu + kotak amplop berhias (celah di atas, pita emas)."""
    mb = W.MB(name)
    mb.box(-1.6 * s, -.6 * s, 0, 1.6 * s, .6 * s, .95 * s, "tbl_cloth")                # meja bertaplak
    mb.box(-1.62 * s, -.62 * s, .55 * s, 1.62 * s, .62 * s, .75 * s, "tbl_sash")
    L.rbox(mb, -.55 * s, -.4 * s, .95 * s, .55 * s, .4 * s, 1.85 * s, "abox", c=.05 * s)  # kotak
    mb.box(-.57 * s, -.42 * s, 1.75 * s, .57 * s, .42 * s, 1.88 * s, "wd_gold")
    mb.box(-.3 * s, -.05 * s, 1.88 * s, .3 * s, .05 * s, 1.885 * s, "c_black")             # celah
    mb.box(-.06 * s, -.425 * s, .95 * s, .06 * s, -.4 * s, 1.75 * s, "wd_gold")            # pita
    for sx in (-1, 1):                                                                # pita kupu-kupu
        mb.poly([(0, -.43 * s, 1.5 * s), (sx * .28 * s, -.43 * s, 1.62 * s), (sx * .28 * s, -.43 * s, 1.38 * s)],
                [(0, 1, 2)], "wd_gold")
    for k in range(5):                                                                # bunga hiasan meja
        L.ball(mb, (-1.3 + k * .14) * s, -.2 * s, .98 * s, .09 * s, "wd_rose" if k % 2 else "wd_pink", seg=8, rings=5)
    env_mb(mb, 1.0 * s, 0, .95 * s, .8 * s)
    env_mb(mb, 1.05 * s, .05 * s, .99 * s, .8 * s)
    return mb.build(loc)


def money(name, layers, loc=(0, 0, 0), nx=2, ny=1, s=.8):
    """tumpukan uang merah (pakai world_prk). Return (obj, tinggi)."""
    return R.money_stack(name, layers, loc, "money_red", nx, ny, s)


# ------------------------------------------------------------------ gedung & dekor pesta
def janur(mb, x, y, h=6.5, side=1):
    """janur kuning: tiang melengkung + daun kelapa muda menjuntai."""
    pts = []
    for k in range(13):
        u = k / 12
        pts.append((x + side * 1.6 * u ** 2, y, .25 + h * math.sin(u * math.pi / 2)))
    for p0, p1 in zip(pts[:-1], pts[1:]):
        T_beam(mb, p0, p1, .12, "janur2")
    for k, p in enumerate(pts[4:], 4):
        ln = .5 + .1 * (k % 3)
        mb.box(p[0] - .03, p[1] - .2, p[2] - ln, p[0] + .03, p[1] + .2, p[2], "janur")
    for k in range(6):                                                    # rumbai di ujung
        a = math.radians(-150 + k * 22)
        ex, ez = pts[-1][0], pts[-1][2]
        T_beam(mb, (ex, y, ez), (ex + side * .9 * math.cos(a) * -1, y, ez + .9 * math.sin(a)), .05, "janur")


def T_beam(mb, p0, p1, t, key):
    import world_tahu as T
    T.beam(mb, p0, p1, t, key)


def wedding_hall(name, loc=(0, 0, 0), w=26.0, d=14.0, h=9.0, sign="GEDUNG RESEPSI"):
    """gedung resepsi siang: fasad krem bertiang, atap pelana merah bata, pintu kaca, janur kuning di pintu,
    lampu untai di fasad, papan nama emas. Asal = tengah muka gedung di tanah (menghadap -Y)."""
    x, y, z = loc
    mb = W.MB(name)
    mb.box(-w / 2, 0, 0, w / 2, d, h, "wd_wall")
    mb.box(-w / 2 - .3, -.3, h - .2, w / 2 + .3, d + .3, h + .4, "wd_trim")
    mb.prism_x([(-.8, h + .4), (d / 2, h + 4.2), (d + .8, h + .4)], -w / 2 - .4, w / 2 + .4, "wd_roof")
    # serambi bertiang + kanopi
    mb.box(-8, -3.2, 0, 8, 0, .4, "wd_wall2")
    mb.box(-8.4, -3.6, 5.6, 8.4, 0, 6.2, "wd_wall")
    mb.prism_x([(-3.9, 6.2), (-1.6, 7.6), (0, 7.6), (0, 6.2)], -8.4, 8.4, "wd_roof")
    for cx in (-7, -3.5, 3.5, 7):
        mb.cyl(cx, -3.0, .4, 5.6, .35, "wd_wall", n=12)
        mb.box(cx - .5, -3.5, 5.3, cx + .5, -2.5, 5.6, "wd_trim")
    mb.box(-2.4, -.08, .4, 2.4, .02, 4.6, "wd_glass")                         # pintu kaca
    mb.box(-.06, -.12, .4, .06, .02, 4.6, "wd_trim")
    for wx in (-11, -6.5, 6.5, 11):                                           # jendela
        mb.box(wx - 1.4, -.06, 2.2, wx + 1.4, .02, 4.6, "wd_glass")
        mb.box(wx - 1.6, -.15, 2.0, wx + 1.6, .02, 2.2, "wd_trim")
        mb.box(wx - 1.4, -.06, 6.2, wx + 1.4, .02, 8.0, "wd_glass")
    janur(mb, -3.2, -3.9, 7.0, 1)
    janur(mb, 3.2, -3.9, 7.0, -1)
    for cx in (-9.2, 9.2):                                                    # rangkaian bunga di pintu
        for k in range(6):
            L.ball(mb, cx + (k % 3 - 1) * .35, -3.9, .5 + (k // 3) * .4, .3, "wd_rose" if k % 2 else "wd_pink",
                   seg=8, rings=5)
    body = mb.build(loc)
    lights = W.MB(name + "_lights")
    P.string_lights(lights, (x - w / 2, y - .4, z + h - .4), (x + w / 2, y - .4, z + h - .4), n=26, sag=1.0)
    P.string_lights(lights, (x - 8.4, y - 3.7, z + 5.5), (x + 8.4, y - 3.7, z + 5.5), n=16, sag=.6)
    lo = lights.build()
    V.glow(lo, {m.name.split("_", 1)[1].rsplit("_", 1)[0]: 3.0 for m in lo.data.materials if m})
    sg = H.text(name + "_sign", sign, 1.1, "wd_gold", depth=.12, loc=(x, y - .2, z + 8.25), emission=.6)
    return {"body": body, "lights": lo, "sign": sg}


def tent(name, x0, y0, x1, y1, h=4.2, loc=(0, 0, 0)):
    """tenda pesta putih terbuka (atap datar berumbai + tiang + selempang pink)."""
    mb = W.MB(name)
    mb.box(x0, y0, h, x1, y1, h + .18, "wd_tent")
    mb.prism_x([(y0, h + .18), ((y0 + y1) / 2, h + 1.6), (y1, h + .18)], x0, x1, "wd_tent")
    k = x0
    while k < x1 - .1:                                                        # rumbai di sisi depan
        mb.poly([(k, y0 - .01, h), (k + .7, y0 - .01, h), (k + .35, y0 - .01, h - .45)], [(0, 1, 2)], "tbl_sash")
        k += .7
    for px in (x0, (x0 + x1) / 2, x1):
        for py in (y0, y1):
            mb.box(px - .1, py - .1, 0, px + .1, py + .1, h, "wd_pole")
    return mb.build(loc)


def round_table(mb, x, y, z=0.0, r=1.1, chairs=6, seed=0):
    rnd = random.Random(seed)
    mb.cyl(x, y, z, z + .8, r, "tbl_cloth", n=16)
    mb.cyl(x, y, z + .78, z + .82, r + .04, "tbl_sash", n=16)
    L.ball(mb, x, y, z + 1.0, .22, rnd.choice(("wd_rose", "wd_pink")), seg=8, rings=5)
    for k in range(chairs):
        a = 2 * math.pi * k / chairs + .3
        cx, cy = x + (r + .55) * math.cos(a), y + (r + .55) * math.sin(a)
        mb.box(cx - .25, cy - .25, z, cx + .25, cy + .25, z + .5, "chair_w")
        bx, by = x + (r + .78) * math.cos(a), y + (r + .78) * math.sin(a)
        mb.box(bx - .2, by - .2, z + .5, bx + .2, by + .2, z + 1.15, "chair_w")


def buffet(name, loc=(0, 0, 0), length=8.0, rot=0.0):
    """meja prasmanan: taplak putih + rok pink, 4 chafing dish perak, tumpukan piring, bunga."""
    mb = W.MB(name)
    mb.box(-length / 2, -.7, 0, length / 2, .7, .95, "tbl_cloth")
    mb.box(-length / 2 - .02, -.72, .1, length / 2 + .02, .72, .7, "tbl_sash")
    n = 4
    for k in range(n):
        cx = -length / 2 + (k + .5) * length / n
        mb.box(cx - .65, -.45, .95, cx + .65, .45, 1.05, "chafing2")
        V_lathe(mb, cx, 0, 1.05, [(0, 0), (.6, 0), (.6, .18), (.45, .42), (.12, .5), (.08, .58), (0, .6)],
                "chafing", n=14)
    for k in range(6):
        mb.cyl(-length / 2 + .5, .3, .95 + k * .04, .95 + k * .04 + .03, .3, "plate", n=12)
    L.ball(mb, length / 2 - .4, .3, 1.25, .28, "wd_rose", seg=8, rings=5)
    return mb.build(loc, rot)


def V_lathe(mb, cx, cy, z0, prof, key, n=16):
    import world_amdk as M
    M.lathe(mb, cx, cy, z0, prof, key, n=n)


def pelaminan(name, loc=(0, 0, 0), s=1.0):
    """pelaminan: panggung berkarpet merah, latar melengkung krem-emas, dua kursi singgasana, dinding bunga."""
    mb = W.MB(name)
    W_, D_ = 9.0 * s, 4.0 * s
    mb.box(-W_ / 2, 0, 0, W_ / 2, D_, .45 * s, "wd_carpet")
    mb.box(-W_ / 2 - .1, -.1, .4 * s, W_ / 2 + .1, D_ + .1, .5 * s, "wd_gold")
    n = 15                                                                  # latar melengkung
    for k in range(n):
        a0, a1 = math.pi * k / n, math.pi * (k + 1) / n
        xa, xb = -W_ / 2 * math.cos(a0), -W_ / 2 * math.cos(a1)
        ya, yb = D_ - .2 * s + 1.2 * s * math.sin(a0), D_ - .2 * s + 1.2 * s * math.sin(a1)
        hh = (3.6 + 1.4 * math.sin(math.pi * (k + .5) / n)) * s
        mb.poly([(xa, ya, .5 * s), (xb, yb, .5 * s), (xb, yb, hh), (xa, ya, hh)], [(0, 1, 2, 3)],
                "wd_cream" if k % 2 else "wd_wall")
        mb.poly([(xa, ya - .02, hh - .25 * s), (xb, yb - .02, hh - .25 * s), (xb, yb - .02, hh), (xa, ya - .02, hh)],
                [(0, 1, 2, 3)], "wd_gold")
    for sx in (-1, 1):                                                      # singgasana
        cx = sx * .85 * s
        L.rbox(mb, cx - .55 * s, D_ - 1.4 * s, .5 * s, cx + .55 * s, D_ - .5 * s, 1.15 * s, "wd_gold", c=.08)
        L.rbox(mb, cx - .55 * s, D_ - .7 * s, 1.15 * s, cx + .55 * s, D_ - .45 * s, 2.6 * s, "wd_red", c=.08)
        mb.box(cx - .6 * s, D_ - .75 * s, 2.5 * s, cx + .6 * s, D_ - .4 * s, 2.75 * s, "wd_gold")
    rnd = random.Random(4)
    for k in range(26):                                                     # bunga di kaki latar & sisi
        side = -1 if k < 13 else 1
        u = (k % 13) / 12
        bx = side * (W_ / 2 - .3 * s) - side * u * 1.2 * s
        L.ball(mb, bx, D_ - .2 * s + rnd.uniform(-.3, .3), (.6 + u * 2.2) * s, .32 * s,
               rnd.choice(("wd_rose", "wd_pink", "wd_white")), seg=8, rings=5)
    mb.box(-.9 * s, -6 * s, .02, .9 * s, 0, .06, "wd_carpet")                 # karpet jalan
    return mb.build(loc)


def plate_mb(mb, x, y, z, s=1.0, rnd=None):
    mb.cyl(x, y, z, z + .05 * s, .32 * s, "plate", n=12)
    L.ball(mb, x - .06 * s, y, z + .05 * s, .14 * s, "rice", seg=8, rings=4, sz=.1 * s, z_from=0)
    c = (rnd or random).choice(("food1", "food2", "food3"))
    mb.box(x + .06 * s, y - .1 * s, z + .05 * s, x + .2 * s, y + .06 * s, z + .11 * s, c)


def plates_grid(name, nx, ny, sp=.75, loc=(0, 0, 0), s=1.0, seed=2):
    rnd = random.Random(seed)
    mb = W.MB(name)
    for i in range(nx):
        for j in range(ny):
            plate_mb(mb, (i - (nx - 1) / 2) * sp, (j - (ny - 1) / 2) * sp, 0, s, rnd)
    return mb.build(loc)


# ------------------------------------------------------------------ katering
def katering_shop(name, loc=(0, 0, 0), w=13.0, d=9.0, sign="KATERING"):
    """usaha katering: ruko krem berkanopi garis merah-putih, etalase dapur (panci & kukusan), rolling door
    terpisah (bisa diturunkan) + papan TUTUP (tersembunyi; munculkan sendiri)."""
    x, y, z = loc
    h = 7.2
    mb = W.MB(name)
    mb.box(-w / 2, 0, 0, w / 2, d, h, "kt_wall")
    mb.box(-w / 2 - .15, -.15, h, w / 2 + .15, d + .15, h + .35, "wd_wall2")
    mb.box(-w / 2 + .5, -.05, .2, w / 2 - .5, .05, 3.6, "kt_dark")            # lubang toko gelap
    for k in range(10):                                                    # kanopi bergaris
        x0_ = -w / 2 + k * w / 10
        mb.prism_x([(-1.9, 3.75), (0, 4.4), (0, 4.5), (-1.9, 3.85)], x0_, x0_ + w / 10, "kt_awn" if k % 2 else "kt_awn2")
    mb.box(-w / 2, -.25, 4.6, w / 2, .02, 5.9, "kt_awn")                      # papan nama
    for wx in (-w / 4, w / 4):
        mb.box(wx - 1.5, -.05, 6.0, wx + 1.5, .02, 6.9, "wd_glass")
    # dapur dalam: meja + panci + kukusan
    mb.box(-w / 2 + 1, 1.2, 0, w / 2 - 1, 2.4, 1.0, "chafing2")
    for k in range(5):
        cx = -w / 2 + 2 + k * (w - 4) / 4
        mb.cyl(cx, 1.8, 1.0, 1.6, .45, "chafing", n=12)
        mb.cyl(cx, 1.8, 1.6, 1.68, .48, "chafing2", n=12)
    body = mb.build(loc)
    sg = H.text(name + "_sign", sign, 1.0, "c_white", depth=.1, loc=(x, y - .3, z + 4.85), emission=.5)
    sh = W.MB(name + "_door")
    for k in range(18):
        zz = k * .2
        sh.box(-w / 2 + .5, -.18, zz, w / 2 - .5, -.1, zz + .17, "shutter" if k % 2 else "shutter2")
    door = sh.build((x, y, z + 3.6))
    door.scale.z = .02                                                      # tergulung (terbuka)
    tp = W.MB(name + "_tutup")
    tp.box(-1.8, -.3, 1.2, 1.8, -.22, 2.4, "wd_white")
    tp.box(-1.9, -.32, 1.1, 1.9, -.28, 1.2, "tutup")
    tpo = tp.build(loc)
    tt = H.text(name + "_tt", "TUTUP", .75, "tutup", depth=.06, loc=(x, y - .34, z + 1.5), emission=.4)
    tt.parent = tpo
    tt.location = (0, -.34, 1.5)
    tpo.scale = (.001,) * 3                                                  # tersembunyi sampai dimunculkan
    return {"body": body, "sign": sg, "door": door, "tutup": tpo}


def close_shutter(door, f0, f1, h=3.6):
    """turunkan rolling door: skala z 0.02 -> 1 dan geser turun."""
    door.keyframe_insert("scale", frame=f0)
    door.keyframe_insert("location", frame=f0)
    door.scale.z = 1.0
    door.location.z -= h
    door.keyframe_insert("scale", frame=f1)
    door.keyframe_insert("location", frame=f1)


def katering_van(name, loc=(0, 0, 0), rot=0.0):
    van = V.box_van(name, loc, rot)
    t = H.text(name + "_t", "KATERING", .55, "kt_awn", depth=.04, loc=(0, 0, 0), emission=.3)
    t.parent = van
    t.location = (-.7, -1.03, 1.6)
    t.rotation_euler = (math.pi / 2, 0, 0)
    t2 = H.text(name + "_t2", "KATERING", .55, "kt_awn", depth=.04, loc=(0, 0, 0), emission=.3)
    t2.parent = van
    t2.location = (-.7, 1.03, 1.6)
    t2.rotation_euler = (math.pi / 2, 0, math.pi)
    return van


# ------------------------------------------------------------------ neon (dunia data)
def heart(name, loc=(0, 0, 0), s=1.0, key_="n_pink", em=5.0, depth=.3):
    """hati neon berdiri (menghadap -Y)."""
    mb = W.MB(name)
    for sx in (-1, 1):
        mb.disc_y(sx * .5 * s, depth / 2, .55 * s, .55 * s, depth, key_, n=18)
    mb.poly([(-1.03 * s, -depth / 2, .45 * s), (1.03 * s, -depth / 2, .45 * s), (0, -depth / 2, -.85 * s),
             (-1.03 * s, depth / 2, .45 * s), (1.03 * s, depth / 2, .45 * s), (0, depth / 2, -.85 * s)],
            [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)], key_)
    ob = mb.build(loc)
    V.glow(ob, {key_: em})
    return ob


def calendar(name, loc=(0, 0, 0), s=1.0):
    """kalender neon 7 kolom x 5 baris berdiri (menghadap -Y). Sel Sabtu & Minggu dipisah supaya bisa
    dinyalakan. Return dict(frame, weekend=[obj...] urut minggu, cells)."""
    x, y, z = loc
    cw, chh, gap = 1.3 * s, 1.0 * s, .18 * s
    W_ = 7 * cw + 8 * gap
    H_ = 5 * chh + 6 * gap + 1.4 * s
    fr_ = W.MB(name + "_bg")
    fr_.box(-W_ / 2, 0, 0, W_ / 2, .2, H_, "cal_bg")
    t = .08 * s
    for (a, b, c, d) in ((-W_ / 2, -W_ / 2 + t, 0, H_), (W_ / 2 - t, W_ / 2, 0, H_), (-W_ / 2, W_ / 2, 0, t),
                         (-W_ / 2, W_ / 2, H_ - t, H_), (-W_ / 2, W_ / 2, H_ - 1.2 * s, H_ - 1.2 * s + t)):
        fr_.box(a, -.06, c, b, 0, d, "n_purple")
    fo = fr_.build(loc)
    V.glow(fo, {"n_purple": 5.0})
    days = "SSRKJSM"
    hd = []
    for i, ch in enumerate(days):
        tx = H.text(f"{name}_d{i}", ch, .55 * s, "n_white" if i < 5 else "n_pink", depth=.04,
                    loc=(x - W_ / 2 + gap + cw / 2 + i * (cw + gap), y - .08, z + H_ - .95 * s), emission=3.0)
        hd.append(tx)
    cells, weekend = {}, []
    for r in range(5):
        row_we = []
        for c in range(7):
            mb = W.MB(f"{name}_c{r}{c}")
            cx = -W_ / 2 + gap + cw / 2 + c * (cw + gap)
            cz = H_ - 1.4 * s - gap - chh / 2 - r * (chh + gap)
            mb.box(cx - cw / 2, -.1, cz - chh / 2, cx + cw / 2, 0, cz + chh / 2, "cal_cell")
            ob = mb.build(loc)
            cells[(r, c)] = ob
            if c >= 5:
                row_we.append(ob)
        weekend.append(row_we)
    return {"frame": fo, "heads": hd, "cells": cells, "weekend": weekend, "w": W_, "h": H_}


def balance(name, loc=(0, 0, 0), s=1.0, key_="n_cyan"):
    """timbangan neon: tiang + lengan (Empty berputar di poros) + dua piring (posisi dikunci terpisah).
    Return dict(root, beam, pans=(kiri, kanan), arm=panjang lengan, pivot_z)."""
    x, y, z = loc
    mb = W.MB(name + "_base")
    mb.cyl(0, 0, 0, .3 * s, 1.6 * s, "bd_dark2", n=24)
    mb.cyl(0, 0, .3 * s, .36 * s, 1.65 * s, key_, n=24)
    mb.box(-.18 * s, -.18 * s, .3 * s, .18 * s, .18 * s, 5.2 * s, "bd_dark2")
    mb.box(-.2 * s, -.22 * s, .3 * s, -.14 * s, -.18 * s, 5.2 * s, key_)
    mb.box(.14 * s, -.22 * s, .3 * s, .2 * s, -.18 * s, 5.2 * s, key_)
    L.ball(mb, 0, 0, 5.3 * s, .35 * s, "n_gold", seg=12, rings=6)
    base = mb.build(loc)
    V.glow(base, {key_: 5.0, "n_gold": 4.0})
    pz = z + 5.3 * s
    piv = bpy.data.objects.new(name + "_piv", None)
    lp._link(piv)
    piv.location = (x, y, pz)
    arm = 3.6 * s
    bm = W.MB(name + "_beam")
    bm.box(-arm, -.12 * s, -.1 * s, arm, .12 * s, .1 * s, "bd_dark2")
    bm.box(-arm, -.15 * s, -.04 * s, arm, -.12 * s, .04 * s, key_)
    bo = bm.build()
    bo.parent = piv
    V.glow(bo, {key_: 6.0})
    pans = []
    for sx in (-1, 1):
        pm = W.MB(f"{name}_pan{sx}")
        for k in range(3):
            a = 2 * math.pi * k / 3
            T_beam(pm, (0, 0, 0), (1.1 * s * math.cos(a), 1.1 * s * math.sin(a), -2.2 * s), .03 * s, "n_white")
        pm.cyl(0, 0, -2.35 * s, -2.2 * s, 1.35 * s, "bd_dark2", n=24)
        pm.cyl(0, 0, -2.22 * s, -2.18 * s, 1.4 * s, key_, n=24)
        po = pm.build((x + sx * arm, y, pz))
        V.glow(po, {key_: 5.0, "n_white": 2.0})
        pans.append(po)
    return {"piv": piv, "beam": bo, "pans": pans, "arm": arm, "base": base, "pz": pz, "x": x, "y": y}


def balance_key(b, f, deg):
    """kunci kemiringan lengan timbangan (deg > 0: kanan turun) + posisi piring."""
    a = math.radians(deg)
    b["piv"].rotation_euler = (0, a, 0)
    b["piv"].keyframe_insert("rotation_euler", frame=f)
    for sx, po in zip((-1, 1), b["pans"]):
        po.location = (b["x"] + sx * b["arm"] * math.cos(a), b["y"], b["pz"] - sx * b["arm"] * math.sin(a))
        po.keyframe_insert("location", frame=f)


def trap(name, loc=(0, 0, 0), s=1.0):
    """jebakan tikus raksasa: papan kayu, per logam, pemukul (Empty berporos, bisa dikunci menutup), umpan uang.
    Return dict(base, bar_piv)."""
    x, y, z = loc
    mb = W.MB(name)
    mb.box(-3 * s, -1.6 * s, 0, 3 * s, 1.6 * s, .35 * s, "wood")
    mb.box(-3 * s, -1.6 * s, .35 * s, 3 * s, -1.4 * s, .38 * s, "wood2")
    for sx in (-1, 1):
        mb.cyl(sx * .35 * s, 0, .35 * s, .55 * s, .28 * s, "spring", n=12)
    mb.box(-.25 * s, .6 * s, .35 * s, .25 * s, 1.2 * s, .5 * s, "spring")
    base = mb.build(loc)
    piv = bpy.data.objects.new(name + "_piv", None)
    lp._link(piv)
    piv.location = (x, y, z + .5 * s)
    bar = W.MB(name + "_bar")
    for (a, b, c, d) in ((-2.6, -2.5, -2.9, 0), (2.5, 2.6, -2.9, 0), (-2.6, 2.6, -3.0, -2.9)):
        bar.box(a * s, c * s, -.05 * s, b * s, d * s, .05 * s, "n_red")
    bo = bar.build()
    bo.parent = piv
    V.glow(bo, {"n_red": 6.0})
    piv.rotation_euler.x = math.radians(-180)                               # terbuka (ke belakang)
    return {"base": base, "piv": piv}
