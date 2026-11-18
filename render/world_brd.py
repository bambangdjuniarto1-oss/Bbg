"""Aset tambahan "Bedah Bisnis: Liquid Vape Part 2 — Raka bikin brand" (dipakai bersama world_vap & world_nkh).
Raka (pemuda hoodie ungu), meja racik rasa + labu kimia berpendar, panah putar 'repeat order', meteran stok."""
import math

import bpy  # noqa: F401

import bpy

import lowpoly as lp
import world as W
import world_amdk as M
import world_hotel as H
import world_laundry as L
import world_vap as V

lp.PAL.update({
    "rk_hood": "#6B3FD1", "rk_hood2": "#4E2BA6", "rk_skin": "#C98E66", "lab_top": "#F3EEF8", "lab_leg": "#3A3346",
    "lab_mat": "#2A2433", "gauge_bg": "#1E1A28",
})

RAKA = dict(skin="rk_skin", top="rk_hood", sleeve="rk_hood2", bottom="c_denim", shoe="shoe_w", hair="short",
            hair_col="hair_blk", acc=())


def raka(name="raka", loc=(0, 0, 0), rot=0.0, hold=None, s=L.CH_S):
    return L.character(name, RAKA, loc, rot, s, hold)


def flask_mb(mb, x, y, z, s, liq):
    """labu erlenmeyer kecil berisi cairan berwarna."""
    M.lathe(mb, x, y, z, [(0, 0), (.5 * s, 0), (.52 * s, .1 * s), (.18 * s, .75 * s), (.18 * s, 1.05 * s),
                          (.23 * s, 1.1 * s), (0, 1.1 * s)], "bt_glass", n=14)
    M.lathe(mb, x, y, z, [(0, .02 * s), (.49 * s, .02 * s), (.3 * s, .42 * s), (0, .42 * s)], liq, n=14)


def lab_table(name, loc=(0, 0, 0), w=4.4, d=1.6):
    """meja racik rasa: taplak gelap, deretan labu warna-warni + botol kecil + pipet. Menghadap -Y."""
    mb = W.MB(name)
    mb.box(-w / 2, -d / 2, .95, w / 2, d / 2, 1.05, "lab_top")
    mb.box(-w / 2 + .1, -d / 2 + .1, 1.05, w / 2 - .1, d / 2 - .1, 1.07, "lab_mat")
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box(sx * (w / 2 - .15) - .06, sy * (d / 2 - .15) - .06, 0, sx * (w / 2 - .15) + .06,
                   sy * (d / 2 - .15) + .06, .95, "lab_leg")
    cols = ["lq_pink", "lq_toko", "lq_brand", "lq_negara", "lq_cheap", "lq_amber"]
    for k, c in enumerate(cols):
        flask_mb(mb, -w / 2 + .45 + k * (w - .9) / 5, .25, 1.07, .62 + .12 * (k % 2), c)
    for k in range(5):
        V.bottle_mb(mb, -1.2 + k * .6, -.42, 1.07, .16, cols[(k + 2) % 6])
    ob = mb.build(loc)
    V.glow(ob, {c: 1.6 for c in cols})
    return ob


def loop_arrow(name, loc=(0, 0, 0), r=2.4, key_="n_cyan", em=6.0, w=.32):
    """panah melingkar berdiri (menghadap -Y): 3 busur + kepala panah — simbol repeat order. Putar rot y."""
    mb = W.MB(name)
    n_seg = 3
    for s_ in range(n_seg):
        a0 = 2 * math.pi * s_ / n_seg + .25
        a1 = a0 + 2 * math.pi / n_seg - .55
        steps = 12
        for i in range(steps):
            u0 = a0 + (a1 - a0) * i / steps
            u1 = a0 + (a1 - a0) * (i + 1) / steps
            pts = []
            for u in (u0, u1):
                for rr in (r - w / 2, r + w / 2):
                    pts.append((math.cos(u) * rr, 0, math.sin(u) * rr))
            vs = [(p[0], -.12, p[2]) for p in pts] + [(p[0], .12, p[2]) for p in pts]
            mb.poly(vs, [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (1, 3, 7, 5), (0, 4, 6, 2)], key_)
        # kepala panah di ujung busur (arah putar +)
        ca, sa = math.cos(a1), math.sin(a1)
        tx, tz = -sa, ca
        base = [(ca * (r - w * 1.4), sa * (r - w * 1.4)), (ca * (r + w * 1.4), sa * (r + w * 1.4))]
        tip = (ca * r + tx * w * 2.6, sa * r + tz * w * 2.6)
        vs = [(base[0][0], -.12, base[0][1]), (base[1][0], -.12, base[1][1]), (tip[0], -.12, tip[1]),
              (base[0][0], .12, base[0][1]), (base[1][0], .12, base[1][1]), (tip[0], .12, tip[1])]
        mb.poly(vs, [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)], key_)
    ob = mb.build(loc)
    V.glow(ob, {key_: em})
    return ob


def stock_gauge(name, loc=(0, 0, 0), h=4.0, w=.9, key_="n_green"):
    """meteran stok berdiri: bingkai gelap + isi berpendar (objek 'fill', berporos di dasar -> scale z)."""
    mb = W.MB(name)
    t = .12
    mb.box(-w / 2 - t, -t, 0, w / 2 + t, t, h + t, "gauge_bg")
    fr_ = mb.build(loc)
    fl = W.MB(name + "_fill")
    fl.box(-w / 2, -t - .03, 0, w / 2, t + .03, h, key_)
    fo = fl.build((loc[0], loc[1], loc[2] + t / 2))
    V.glow(fo, {key_: 3.5})
    return {"frame": fr_, "fill": fo}


def brand_store(name, loc=(0, 0, 0), sign="RAKA LIQUID", w=13.0, d=10.0):
    """toko/kantor brand Raka (versi ungu dari toko vape siang)."""
    return V.vape_store_day(name, loc, w, d, "vs_purple", sign, seed=7)


def label_text(name, body, loc, size=.6, key_="c_white", em=1.0, parent=None):
    t = H.text(name, body, size, key_, depth=.05, loc=loc, emission=em)
    if parent:
        t.parent = parent
    return t
