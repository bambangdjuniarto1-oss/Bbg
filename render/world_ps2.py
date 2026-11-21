"""Aset dunia "Persib Part 2: mesin uang" (Bedah Bisnis) — melengkapi world_psb (stadion, foto, logo, koin).
Objek baru: tombol YouTube 3D, pintu brankas (bisa terbuka, cahaya dari dalam), TV siaran, podium peringkat,
grid kalender 24 laga kandang, gerbang tiket (turnstile), toko resmi mini per kota, papan skor ACL Two,
corong follower -> uang, ikon follower, batangan emas.
Semua berdiri di z=0 menghadap -Y (ke kamera default)."""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowpoly as lp  # noqa: E402
import world as W  # noqa: E402
import world_psb as P  # noqa: E402
import world_gta as G  # noqa: E402
import world_hotel as Ht  # noqa: E402
import world_vap as V  # noqa: E402
from world_amdk import lathe  # noqa: E402

lp.PAL.update({
    "yt_red": "#FF0033", "yt_white": "#FFFFFF", "door_steel": "#7A8699", "door_dk": "#323C50", "door_in": "#FFD27A",
    "door_frame": "#0E1424", "tv_body": "#0B0E16", "live_red": "#E11D48", "pod_1": "#E9B949", "pod_2": "#C9D2DE",
    "pod_3": "#C07A45", "cal_off": "#121B33", "cal_on": "#2D6BFF", "cal_away": "#334155", "gate_metal": "#9AA3B2",
    "gate_arm": "#E11D48", "store_wall": "#F3F5F9", "store_glass": "#7FB2FF", "store_band": "#1F4FD1",
    "store_floor": "#0E1426", "score_bg": "#060A16", "score_line": "#2D6BFF", "funnel_glass": "#8FB8FF",
    "funnel_rim": "#5FD3FF", "fol_blue": "#4F8BFF", "gold_bar": "#E8B53A", "gold_dk": "#B8862A", "pipe": "#2A3650",
    "pipe_glow": "#5FD3FF", "alarm": "#FF2A2A", "n_cyan": "#5FD3FF",
})


def text3d(name, body, loc, size, key_="psb_white", em=3.0, rot=(math.pi / 2, 0, 0)):
    return Ht.text(name, body, size, key_, depth=.08, loc=loc, emission=em, rot=rot)


def _round_rect(w, h, r, n=6):
    pts = []
    for cx, cz, a0 in ((w / 2 - r, h - r, 0), (-w / 2 + r, h - r, 90), (-w / 2 + r, r, 180), (w / 2 - r, r, 270)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


# ------------------------------------------------------------------ YouTube
def yt_button(name, s=1.0, loc=(0, 0, 0), em=2.4):
    """tombol play YouTube 3D: badan merah membulat + segitiga putih menonjol."""
    mb = W.MB(name)
    w, h = 4.4 * s, 3.1 * s
    mb.prism_y([(x, z) for x, z in _round_rect(w, h, .9 * s)], -.35 * s, .35 * s, "yt_red")
    tri = [(-.62 * s, h / 2 - .78 * s), (.86 * s, h / 2), (-.62 * s, h / 2 + .78 * s)]
    mb.prism_y(tri, -.48 * s, -.3 * s, "yt_white")
    ob = mb.build(loc)
    V.glow(ob, {"yt_red": em, "yt_white": em * 1.4})
    return ob


# ------------------------------------------------------------------ pintu brankas
def vault_door(name, loc=(0, 0, 0), w=3.2, h=5.2, label="LEAGUE", key_="n_gold", rot_z=0.0, sign_size=.55):
    """kusen + daun pintu baja (engsel kiri, buka = putar door.rotation_euler.z negatif) + cahaya hangat di
    dalam + papan neon label di atas. Return dict(root, door, inner, sign)."""
    root = bpy.data.objects.new(name, None)
    lp._link(root)
    fm = W.MB(name + "_frame")
    t = .38
    fm.box(-w / 2 - t, -.25, 0, -w / 2, .45, h + t, "door_frame")
    fm.box(w / 2, -.25, 0, w / 2 + t, .45, h + t, "door_frame")
    fm.box(-w / 2 - t, -.25, h, w / 2 + t, .45, h + t, "door_frame")
    fm.box(-w / 2 - t - .08, -.3, -.02, w / 2 + t + .08, .5, .06, "door_frame")
    fm.box(-w / 2 - t, -.32, h + t - .1, w / 2 + t, -.25, h + t - .04, key_)       # strip neon di atas kusen
    fo = fm.build(parent=root)
    V.glow(fo, {key_: 5.0})
    im = W.MB(name + "_in")
    im.box(-w / 2, .3, 0, w / 2, .4, h, "door_in")
    io = im.build(parent=root)
    V.glow(io, {"door_in": 6.0})
    dm = W.MB(name + "_door")
    dm.box(0, -.18, .02, w, .18, h - .02, "door_steel")
    for z in (h * .2, h * .5, h * .8):                       # rusuk horizontal
        dm.box(.15, -.24, z - .06, w - .15, -.18, z + .06, "door_dk")
    dm.disc_y(w * .62, -.26, h * .5, .62, .08, "door_dk", n=18)  # roda kunci
    dm.disc_y(w * .62, -.3, h * .5, .2, .06, key_, n=14)
    for z0, z1 in ((.06, .14), (h - .14, h - .06)):                 # list tepi menyala
        dm.box(.06, -.22, z0, w - .06, -.18, z1, key_)
    dm.box(w - .14, -.22, .06, w - .06, -.18, h - .06, key_)
    for k in range(4):
        a = math.pi * k / 4
        dm.box(w * .62 - .62 * math.cos(a), -.36, h * .5 - .05, w * .62 + .62 * math.cos(a), -.3, h * .5 + .05, "gate_metal")
    do = dm.build(parent=root)
    do.location = (-w / 2, 0, 0)
    P.metal(do, .32, .12)
    V.glow(do, {key_: 4.0})
    sg = sf = None
    if label:
        sg, sf = V.neon_sign(name + "_sg", label, (0, -.4, h + t + .75), sign_size, key_, 7.0, True)
        for ob in (sg, sf):
            if ob is not None:
                ob.parent = root
    root.location = loc
    root.rotation_euler.z = rot_z
    return {"root": root, "door": do, "inner": io, "sign": (sg, sf)}


# ------------------------------------------------------------------ TV & podium
def tv(name, img, w=7.0, loc=(0, 0, 0), em=1.1, rot_z=0.0):
    """TV siaran berdiri: bingkai gelap, layar foto pertandingan, tag LIVE merah. Pivot bawah-tengah."""
    root = bpy.data.objects.new(name, None)
    lp._link(root)
    iw, ih = G.img_size(img)
    h = w * 9 / 16
    mb = W.MB(name + "_body")
    mb.box(-w / 2 - .25, .05, 1.2, w / 2 + .25, .45, 1.2 + h + .5, "tv_body")
    mb.box(-.25, .2, 0, .25, .5, 1.25, "tv_body")
    mb.box(-1.6, -.4, 0, 1.6, .9, .12, "tv_body")
    bo = mb.build(parent=root)
    me = G._quad_mesh(name + "_scr", w, h)
    me.materials.append(G.img_mat(img, em, False, False))
    so = bpy.data.objects.new(name + "_scr", me)
    lp._link(so)
    so.parent = root
    so.location = (0, 0, 1.45)
    tg = W.MB(name + "_live")
    tg.box(-w / 2 + .3, -.06, 1.45 + h - .75, -w / 2 + 1.9, .0, 1.45 + h - .25, "live_red")
    to = tg.build(parent=root)
    V.glow(to, {"live_red": 4.0})
    lt = text3d(name + "_lt", "LIVE", (-w / 2 + 1.1, -.1, 1.45 + h - .62), .36, "yt_white", 4.0)
    lt.parent = root
    root.location = loc
    root.rotation_euler.z = rot_z
    return {"root": root, "live": to, "w": w, "h": h + 1.7}


def podium(name, loc=(0, 0, 0), s=1.0):
    """podium 1-2-3 (tengah tertinggi) dengan angka. Return dict(blocks=[1,2,3], root)."""
    root = bpy.data.objects.new(name, None)
    lp._link(root)
    blocks = []
    for rank, x, hh, key_ in ((1, 0, 2.4, "pod_1"), (2, -2.3, 1.6, "pod_2"), (3, 2.3, 1.1, "pod_3")):
        mb = W.MB(f"{name}_{rank}")
        mb.box(-1.1 * s, -1.0 * s, 0, 1.1 * s, 1.0 * s, hh * s, key_)
        ob = mb.build(parent=root)
        ob.location = (x * s, 0, 0)
        P.metal(ob, .3, .15)
        tx = text3d(f"{name}_n{rank}", str(rank), (0, -1.05 * s, hh * s * .35), .9 * s, "door_frame", 0.0)
        tx.parent = ob
        blocks.append(ob)
    root.location = loc
    return {"root": root, "blocks": blocks}


# ------------------------------------------------------------------ kalender laga kandang
def cal_grid(name, n=24, cols=6, loc=(0, 0, 0), tile=1.15, gap=.22):
    """grid ubin kalender berdiri (n laga kandang). Tiap ubin objek sendiri (bisa di-flip/pop).
    Return list ubin (urutan baris atas -> bawah)."""
    rows = math.ceil(n / cols)
    tiles = []
    W_ = cols * tile + (cols - 1) * gap
    for i in range(n):
        r, c = divmod(i, cols)
        x = -W_ / 2 + tile / 2 + c * (tile + gap)
        z = (rows - 1 - r) * (tile + gap) + tile / 2
        mb = W.MB(f"{name}_{i}")
        mb.box(-tile / 2, -.1, -tile / 2, tile / 2, .1, tile / 2, "cal_on")
        mb.box(-tile / 2 + .1, -.14, tile / 2 - .3, tile / 2 - .1, -.1, tile / 2 - .12, "psb_white")
        ob = mb.build((loc[0] + x, loc[1], loc[2] + z))
        V.glow(ob, {"cal_on": 2.6, "psb_white": 2.0})
        num = text3d(f"{name}_t{i}", str(i + 1), (0, -.16, -.32), .5, "psb_white", 3.0)
        num.parent = ob
        tiles.append(ob)
    return tiles


# ------------------------------------------------------------------ gerbang tiket
def turnstile(name, loc=(0, 0, 0), s=1.0):
    """gerbang putar tiket: dua tiang + lengan merah + lampu hijau. Return dict(root, arm, led)."""
    root = bpy.data.objects.new(name, None)
    lp._link(root)
    mb = W.MB(name + "_b")
    for x in (-.9, .9):
        mb.box((x - .28) * s, -.5 * s, 0, (x + .28) * s, .5 * s, 1.9 * s, "gate_metal")
        mb.box((x - .3) * s, -.52 * s, 1.9 * s, (x + .3) * s, .52 * s, 2.0 * s, "door_frame")
    bo = mb.build(parent=root)
    P.metal(bo, .3, .1)
    am = W.MB(name + "_arm")
    am.box(-.75 * s, -.05 * s, -.05 * s, .75 * s, .05 * s, .05 * s, "gate_arm")
    ao = am.build(parent=root)
    ao.location = (0, 0, 1.25 * s)
    V.glow(ao, {"gate_arm": 2.0})
    lm = W.MB(name + "_led")
    lm.box(-.18 * s, -.56 * s, 1.55 * s, .18 * s, -.5 * s, 1.75 * s, "candle_g")
    lo = lm.build(parent=root)
    lo.location = (-.9 * s, 0, 0)
    V.glow(lo, {"candle_g": 6.0})
    root.location = loc
    return {"root": root, "arm": ao, "led": lo}


# ------------------------------------------------------------------ toko resmi mini
def store_front(name, city, loc=(0, 0, 0), s=1.0, rot_z=0.0):
    """toko resmi mini: dinding putih, kaca etalase bercahaya, pita biru, papan nama kota, logo kecil."""
    root = bpy.data.objects.new(name, None)
    lp._link(root)
    w, d, h = 4.2 * s, 3.4 * s, 3.4 * s
    mb = W.MB(name + "_b")
    mb.box(-w / 2, 0, 0, w / 2, d, h, "store_wall")
    mb.box(-w / 2 - .1, -.1, h - .7 * s, w / 2 + .1, d, h + .1, "store_band")
    mb.box(-w / 2 + .3, -.05, .25, w / 2 - .3, .02, h - .95 * s, "store_glass")
    mb.box(-.06, -.08, .25, .06, .0, h - .95 * s, "door_frame")
    mb.box(-w / 2 - .3, -.6, -.02, w / 2 + .3, d + .2, .08, "store_floor")
    bo = mb.build(parent=root)
    V.glow(bo, {"store_glass": 2.2, "store_band": 1.2})
    lg = P.logo_card(name + "_lg", "lg_persib", .95 * s, (-w / 2 + .75 * s, -.16, h - .65 * s), 0.0, plate=None,
                     em=1.3)
    lg.parent = root
    tx = text3d(name + "_tx", city, (.45 * s, -.14, h - .5 * s), .34 * s, "yt_white", 3.5)
    tx.parent = root
    root.location = loc
    root.rotation_euler.z = rot_z
    return root


# ------------------------------------------------------------------ papan skor ACL Two
def scoreboard(name, home, away, score, img, loc=(0, 0, 0), w=6.4, rot_z=0.0, photo_h=3.4):
    """papan skor: foto pertandingan di atas + strip skor gelap 'HOME 0-1 AWAY' + garis biru."""
    root = bpy.data.objects.new(name, None)
    lp._link(root)
    mb = W.MB(name + "_b")
    mb.box(-w / 2, .0, 0, w / 2, .3, 1.5, "score_bg")
    mb.box(-w / 2, -.04, 1.42, w / 2, 0, 1.5, "score_line")
    mb.box(-w / 2, -.04, 0, w / 2, 0, .08, "score_line")
    bo = mb.build(parent=root)
    V.glow(bo, {"score_line": 5.0})
    for body, x, sz, key_ in ((home, -w * .3, .36, "psb_white"), (score, 0, .62, "pod_1"), (away, w * .3, .36, "psb_white")):
        t = text3d(f"{name}_{body[:4]}", body, (x, -.06, .5 if key_ != "pod_1" else .42), sz, key_, 4.0)
        t.parent = root
    ph = P.photo(name + "_ph", img, photo_h, (0, .1, 1.55), 0.0, em=.95, border=.08)
    ph.parent = root
    root.location = loc
    root.rotation_euler.z = rot_z
    return root


# ------------------------------------------------------------------ corong follower -> uang
def funnel(name, loc=(0, 0, 0), r_top=4.2, r_bot=.8, h=4.6):
    """corong kaca bercahaya (lebar di atas). Pivot = ujung bawah."""
    mb = W.MB(name)
    prof = [(r_bot, 0), (r_bot, -.9), (r_bot + .12, -.9), (r_bot + .12, 0), (r_top + .12, h), (r_top, h)]
    lathe(mb, 0, 0, 0, [(r_bot, -.9), (r_bot, 0), (r_top, h), (r_top + .15, h + .15)], "funnel_glass", n=40)
    lathe(mb, 0, 0, 0, [(r_top - .05, h - .05), (r_top + .2, h + .05), (r_top + .2, h + .25), (r_top - .05, h + .2)],
          "funnel_rim", n=40)
    ob = mb.build(loc)
    V.set_mat(ob, V.glow_glass("funnel_glass", .5, .22))
    V.glow(ob, {"funnel_rim": 6.0})
    _ = prof
    return ob


def follower(name, loc=(0, 0, 0), s=1.0, key_="fol_blue"):
    """ikon follower (kepala bulat + bahu) bercahaya."""
    mb = W.MB(name)
    mb.sphere(0, 0, .95 * s, .32 * s, key_)
    lathe(mb, 0, 0, 0, [(0, 0), (.55 * s, 0), (.58 * s, .25 * s), (.42 * s, .58 * s), (0, .62 * s)], key_, n=14)
    ob = mb.build(loc)
    V.glow(ob, {key_: 3.0})
    return ob


def pipe(name, x, y, z0, z1, r=.28, key_="pipe", ring="pipe_glow"):
    mb = W.MB(name)
    mb.cyl(x, y, z0, z1, r, key_, n=14)
    for z in (z0 + .15, z1 - .25):
        mb.cyl(x, y, z, z + .12, r + .06, ring, n=14)
    ob = mb.build()
    V.glow(ob, {ring: 5.0})
    return ob


def gold_bar(name, loc=(0, 0, 0), s=1.0):
    """batangan emas trapesium."""
    mb = W.MB(name)
    w, d, h = 1.6 * s, .8 * s, .45 * s
    i = .18 * s
    v = [(-w / 2, -d / 2, 0), (w / 2, -d / 2, 0), (w / 2, d / 2, 0), (-w / 2, d / 2, 0),
         (-w / 2 + i, -d / 2 + i, h), (w / 2 - i, -d / 2 + i, h), (w / 2 - i, d / 2 - i, h), (-w / 2 + i, d / 2 - i, h)]
    f = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    mb.poly(v, f, "gold_bar")
    ob = mb.build(loc)
    P.metal(ob, .25, .35)
    return ob
