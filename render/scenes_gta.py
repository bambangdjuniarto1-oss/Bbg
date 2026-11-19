"""Adegan "Bedah Bisnis: GTA VI, Rp17 triliun sebelum rilis" (alur 3K: Korban -> Kejutan -> Kail, berulang).
Visual: kota diorama Vice City lebar (pembeli berbendera dari seluruh dunia, papan LED cuplikan resmi, menara
Rockstar) + panggung neon (angka, globe pembeli, galeri karakter resmi). Kamera spline per-frame (scenes_nkh),
lintasan lebih kompleks: spiral, menukik, menyusur, mengitari.

  GTA_TEX=DIR python3 render/scenes_gta.py -- --scene G01 --out DIR [--res 720x1280] [--samples 4] [--frames a-b]
"""
import math
import os
import random
import sys

import bpy  # noqa: F401  (harus sebelum lowpoly: bmesh)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowpoly as lp  # noqa: E402
import world as W  # noqa: E402
import world_gta as G  # noqa: E402
import world_laundry as L  # noqa: E402
import world_nkh as N  # noqa: E402
import world_vap as V  # noqa: E402
import scenes_nkh as K  # noqa: E402
import scenes_vap as SV  # noqa: E402
from scenes_nkh import FPS, TAIL, anim, arc_move, grow, hide_until, key, pop_in, pop_out  # noqa: E402

TIMELINE = [("G01", 0.00), ("G02", 3.13), ("G03", 6.26), ("G04", 10.29), ("G05", 15.10), ("G06", 19.65),
            ("G07", 25.45), ("G08", 28.10), ("G09", 32.45), ("G10", 34.96), ("G11", 36.29), ("G12", 38.64),
            ("G13", 42.36), ("G14", 47.16), ("G15", 51.70), ("G16", 58.19), ("G17", 63.27), ("G18", 66.79),
            ("G19", 74.52)]
END_T = 83.6
CITY = {"G01", "G03", "G07", "G10", "G11", "G16", "G18", "G19"}
K.TIMELINE, K.END_T, K.CITY = TIMELINE, END_T, CITY
Z0 = .24
HQ_Y = 44 - 18                 # menara Rockstar (y1 diorama - 18)


def fr(sid, t):
    return K.fr(sid, t)


def camera(sid, keys, **kw):
    return K.camera(sid, keys, **kw)


def neon(**kw):
    return K.neon(**kw)


def city(n, **kw):
    return G.vice_city(n + TAIL, **kw)


def n_all(n):
    return n + TAIL


def money(name, h, loc, s=1.0, nx=2, ny=2):
    """tumpukan uang setinggi h."""
    layers = max(1, round(h / (.29 * s)))
    return N.money(name, layers, loc, nx, ny, s)


def float_bob(ob, f0, f1, amp=.25, period=70, phase=0.0):
    z0 = ob.location.z
    for f in range(f0, f1 + 1, 2):
        key(ob, "location", f, (ob.location.x, ob.location.y, z0 + amp * math.sin(2 * math.pi * f / period + phase)))


# ================================================================== KORBAN (hook)
def g01(n, A):
    """Jutaan orang bayar Rp1,19 juta: kamera menukik dari langit ke kota Vice City, antrean berbendera di toko."""
    sid = "G01"
    c = city(n, crowd=27)
    t, fo = V.neon_sign("price", "Rp1,19 JUTA", (0, 3.4, 11.2), 1.2, "n_gold", 8.0)
    for ob in (t, fo):
        pop_in(ob, fr(sid, 1.35), 1.0)
    case = G.game_case("hc", "cover_ps5", .6, (0, 0, 0))
    rnd = random.Random(4)
    for i, p in enumerate(c["queue"][:16]):
        b = p["body"]
        cs = G.dup(case, f"hc{i}", (b.location.x + .2, b.location.y - .3, 3.3))
        cs.rotation_euler.z = rnd.uniform(-.3, .3)
        pop_in(cs, fr(sid, 1.9 + .05 * i), 1.0, 9)
        float_bob(cs, 1, n_all(n), .12, 40, i)
    case.scale = (.001,) * 3
    camera(sid, [(0.0, (0, 0, 2), -128, 48, 190), (1.3, (0, -2, 3), -112, 30, 78),
                 (3.13, (0, -2.5, 3.2), -98, 14, 30)], lens=24)
    A["QUEUE"] = ((0, -4.5, 3.6))
    A["PRICE"] = (t, (0, 0, 1.5))


def g02(n, A):
    """...buat game yang waktu itu belum bisa dimainkan: kotak GTA VI di alas neon, digembok."""
    sid = "G02"
    neon(grid="vp_grid2", em=1.8, rig_c=(0, 0, 2.5), rig_s=1.3, fade=(10, 46))
    V.disc_ped("ped", 2.6, "n_cyan", (0, 0, 0), em=4.0, h=.45)
    cs = G.game_case("case", "cover_ps5", 2.3, (0, 0, .45), math.radians(-14))
    SV.spin(cs, 1, n_all(n), 22)
    lk = G.padlock("lock", (0, -1.2, 1.2), .85, "n_gold", 5.0)
    pop_in(lk, fr(sid, 4.95), .85)
    for k, x in enumerate((-2.2, 2.2)):
        mb = W.MB(f"chain{k}")
        for i in range(9):
            mb.cyl(x * (1 - i / 9), -.9 - .02 * i, .8 + i * .38, .8 + i * .38 + .3, .09, "ic_metal", n=6)
        ch = mb.build()
        grow(ch, fr(sid, 4.6 + .1 * k), fr(sid, 5.1 + .1 * k), 1.0)
    camera(sid, [(3.13, (0, 0, 2.0), -120, 6, 10.5), (4.9, (0, 0, 2.1), -100, 9, 10.0),
                 (6.26, (0, 0, 2.2), -82, 12, 10.5)], lens=26)
    A["CASE"] = (cs, (0, 0, 4.2))
    A["LOCK"] = (lk, (0, 0, 1.9))


def g03(n, A):
    """Bahkan belum lihat gameplay barunya — layar raksasa cuplikan resmi; 'mungkin kamu salah satunya'."""
    sid = "G03"
    c = city(n, crowd=0, store=False)
    scr = G.screen("big", ["shot_launch", "shot_beach", "shot_heist", "shot_sunset"], 24, 13.5, (0, 6, 9.5),
                   switch=[fr(sid, 7.4), fr(sid, 8.5), fr(sid, 9.5)], n_frames=n_all(n), em=2.4, frame="n_pink")
    mb = W.MB("scr_leg")
    for x in (-9, 9):
        mb.box(x - .5, 6.2, 0, x + .5, 7.0, 3.0, "bd_dark")
    mb.build()
    rnd = random.Random(8)
    crowd = []
    for i in range(30):
        x, y = -13 + (i % 10) * 2.9 + rnd.uniform(-.4, .4), -3.5 - (i // 10) * 2.6 + rnd.uniform(-.3, .3)
        code = G.FLAGS[i % len(G.FLAGS)] if i % 3 == 0 else None
        if i == 14:
            code = "ID"
        crowd.append(G.buyer(f"v{i}", i + 5, (x, y, Z0), math.pi + rnd.uniform(-.25, .25), code))
    you = crowd[14]
    yb = you["body"]
    key(yb, "rotation_euler", 1, (0, 0, math.pi))
    anim(yb, "rotation_euler", fr(sid, 8.2), fr(sid, 8.9), (0, 0, math.pi), (0, 0, 0.15), "inout")
    L.pose(you, "stand", 1)
    L.pose(you, "stand", fr(sid, 8.5))
    L.pose(you, "point", fr(sid, 9.0))
    q = V.qmark("q", (0, 6.3, 13.0), 1.6, "n_gold", 7)
    pop_in(q, fr(sid, 6.9), 1.6)
    pop_out(q, fr(sid, 7.35))
    bx, by = you["body"].location.x, you["body"].location.y
    camera(sid, [(6.26, (0, 4, 7.0), -90, 4, 46), (7.8, (0, 2, 6.0), -78, 10, 34),
                 (9.0, (bx, by, 2.0), -64, 10, 9.5), (10.29, (bx, by, 2.0), -78, 8, 7.5)], lens=24)
    A["SCREEN"] = (scr, (0, 0, 7.4))
    A["YOU"] = (you["body"], (0, 0, 2.7))


# ================================================================== KEJUTAN 1
def g04(n, A):
    """Namanya GTA 6 — logo resmi + galeri karakter resmi melayang; kamera spiral; rilis 19 November."""
    sid = "G04"
    neon(grid="vp_grid", em=1.8, rig_c=(0, 0, 5), rig_s=2.2, fade=(14, 60))
    lg = G.img_plane("logo", "logo", h=7.5, loc=(0, 0, 7.2), center=True, em=1.8)
    pop_in(lg, fr(sid, 10.75), 1.0, 14)
    float_bob(lg, 1, n_all(n), .25, 80)
    cards = []
    order = ["p_jl", "p_girl", "p_chain", "p_rifle", "p_bike", "p_heli", "p_boat", "p_car", "p_gator", "jl_tall"]
    keys = ["n_pink", "n_cyan", "n_purple", "n_gold"]
    for i, nm in enumerate(order):
        a = 2 * math.pi * i / len(order) - math.pi / 2
        r = 10.5
        x, y = r * math.cos(a), r * math.sin(a)
        cd = G.img_plane(f"card{i}", nm, h=5.0 if nm != "jl_tall" else 6.0, loc=(x, y, 5.4 + (i % 2) * 1.6),
                         rot_z=a + math.pi / 2, center=True, em=1.4, frame=keys[i % 4])
        pop_in(cd, fr(sid, 10.29 + .05 * i), 1.0, 12)
        float_bob(cd, 1, n_all(n), .2, 60, i)
        cards.append(cd)
    t, fo = V.neon_sign("date", "19 NOVEMBER 2026", (0, -1.0, 1.6), .8, "n_gold", 8.0)
    for ob in (t, fo):
        pop_in(ob, fr(sid, 13.45), 1.0)
    # kamera spiral: dari bawah di depan kartu Jason & Lucia, naik mengitari, berakhir di depan logo
    cam, _ = camera(sid, [(10.29, (0, -6.5, 5.6), -92, 4, 9.5), (11.6, (0, -2, 6.4), -30, 10, 21),
                 (12.8, (0, 0, 6.6), 50, 14, 24), (14.0, (0, 0, 6.4), 150, 12, 23), (15.10, (0, 0, 6.0), 230, 8, 20)],
           lens=24)
    for ob in [lg] + cards:                       # selalu menghadap kamera (tidak pernah terlihat terbalik)
        c_ = ob.constraints.new("LOCKED_TRACK")
        c_.target = cam
        c_.track_axis = "TRACK_NEGATIVE_Y"
        c_.lock_axis = "LOCK_Z"
    A["JL"] = (cards[0], (0, 0, 2.7))
    A["LOGO"] = (lg, (0, 0, 4.0))


def g05(n, A):
    """Pre-order diperkirakan 9,69 juta kopi — globe titik daratan, pin pembeli menyala di seluruh dunia."""
    sid = "G05"
    neon(grid="vp_grid2", em=1.4, rig_c=(0, 0, 6), rig_s=2.0, fade=(16, 60))
    g = G.globe("gl", 6.0, (0, 0, 7.0))
    root = g["root"]
    rz = root.rotation_euler.z
    anim(root, "rotation_euler", 1, n_all(n), (0, 0, rz), (0, 0, rz + math.radians(120)), "lin")
    codes = ["ID", "JP", "KR", "PH", "AU", "IN", "AE", "SA", "TR", "DE", "GB", "FR", "NG", "ZA", "BR", "AR", "MX",
             "US", "US2", "CA"]
    for i, cd in enumerate(codes):
        b = G.pin_beam(f"pin{cd}", root, g["pins"][cd], 6.0, 1.4 + (i % 3) * .5,
                       ["n_pink", "n_gold", "n_cyan"][i % 3], 6.0)
        f0 = fr(sid, 15.45 + .11 * i)
        key(b, "scale", 1, (.001,) * 3)
        anim(b, "scale", f0, f0 + 9, (.001,) * 3, (1, 1, 1), "back")
    # kotak game kecil mengorbit (arus pre-order)
    case = G.game_case("oc", "cover_ps5", .55, (0, 0, 0))
    for i in range(18):
        cs = G.dup(case, f"oc{i}")
        a0 = 2 * math.pi * i / 18
        r = 8.6 + (i % 3) * .7
        f0 = fr(sid, 16.0 + .06 * i)
        for f in range(1, n_all(n) + 1):
            a = a0 + .035 * f
            key(cs, "location", f, (r * math.cos(a), r * math.sin(a), 6.2 + 1.6 * math.sin(a * 2 + i)))
            cs.rotation_euler.z = a + math.pi
            cs.keyframe_insert("rotation_euler", frame=f)
        pop_in(cs, f0, 1.0, 9)
    case.scale = (.001,) * 3
    camera(sid, [(15.10, (0, 0, 7.0), -70, 6, 22), (17.4, (0, 0, 7.2), -100, 14, 25),
                 (19.65, (0, 0, 7.6), -130, 20, 27)], lens=24)
    A["ID"] = ((0, -6.6, 6.2))
    A["GLOBE"] = ((0, 0, 13.6))


def g06(n, A):
    """Nilainya ~US$942 juta ≈ Rp17 triliun: hujan kotak game masuk brankas -> menara uang naik."""
    sid = "G06"
    neon(grid="vp_grid", em=1.8, rig_c=(0, 0, 4), rig_s=2.0, fade=(14, 55))
    V.base_plate("bp", 7.0, 7.0, "n_gold", (0, 0, 0), 3.0)
    tw, h = money("tw", 11.0, (0, 0, .14), 1.25, 3, 3)
    grow(tw, fr(sid, 20.1), fr(sid, 24.4), 1.0, "inout")
    case = G.game_case("rc", "cover_ps5", .8, (0, 0, 0))
    rnd = random.Random(3)
    for i in range(34):
        cs = G.dup(case, f"rc{i}")
        x, y = rnd.uniform(-7, 7), rnd.uniform(-5, 6)
        f0 = fr(sid, 19.8 + .13 * i)
        p0, p1 = (x, y, 18), (x * .15, y * .15, 1 + .3 * i)
        key(cs, "location", 1, p0)
        cs.rotation_euler = (rnd.uniform(-.5, .5), rnd.uniform(-.5, .5), rnd.uniform(0, 6))
        hide_until(cs, f0)
        anim(cs, "location", f0, f0 + 14, p0, p1, "in")
        anim(cs, "scale", f0 + 12, f0 + 17, (1, 1, 1), (.001,) * 3, "in")
    case.scale = (.001,) * 3
    cr = V.crown("cr", (0, 0, h + 1.2), 1.4, "n_gold", 6.0)
    pop_in(cr, fr(sid, 24.3), 1.4)
    camera(sid, [(19.65, (0, 0, 2.0), -112, 34, 30), (22.0, (0, 0, 5.5), -96, 16, 28),
                 (25.45, (0, 0, h * .7), -76, 12, 30)], lens=24)
    A["TOWER"] = (tw, (0, 0, h + .6))


def g07(n, A):
    """Uangnya masuk duluan, game-nya belakangan: uang terbang dari antrean ke menara Rockstar; game datang telat."""
    sid = "G07"
    c = city(n, crowd=18)
    hq = c["hq"]
    rnd = random.Random(2)
    for i in range(10):
        mn, _ = N.money(f"mf{i}", 2, (0, 0, 0), 1, 1, .9)
        p0 = (rnd.uniform(-8, 8), -4.5 - rnd.uniform(0, 3), 2.5)
        p1 = (rnd.uniform(-3, 3), HQ_Y - 5.5, 12 + rnd.uniform(-3, 6))
        f0 = fr(sid, 25.55 + .08 * i)
        key(mn, "location", 1, p0)
        hide_until(mn, f0)
        arc_move(mn, f0, f0 + 22, p0, p1, 6.0)
        anim(mn, "scale", f0 + 19, f0 + 24, (1, 1, 1), (.001,) * 3, "in")
    gc = G.game_case("late", "cover_ps5", 1.4, (0, -1.0, Z0 + 4.6))
    pop_in(gc, fr(sid, 26.95), 1.0, 12)
    SV.spin(gc, fr(sid, 26.95), n_all(n), 40)
    camera(sid, [(25.45, (0, -3, 3.0), -100, 12, 30), (26.6, (0, 12, 14), -96, 18, 62),
                 (28.10, (0, 0, 6.0), -92, 14, 34)], lens=24)
    A["HQ"] = (hq["logo"], (0, 0, 4.8))
    A["LATE"] = (gc, (0, 0, 2.8))


# ================================================================== KAIL 1
def g08(n, A):
    """Kok bisa orang rela bayar di muka tanpa lihat isinya? Kotak misteri + pembeli dunia membayar."""
    sid = "G08"
    neon(grid="vp_grid2", em=1.6, rig_c=(0, 0, 2), rig_s=1.4)
    V.disc_ped("ped", 2.8, "n_purple", (0, 0, 0), em=4.0, h=.5)
    mb = W.MB("mbox")
    mb.box(-1.6, -1.6, .5, 1.6, 1.6, 3.7, "case_blk")
    mb.box(-.25, -1.62, .5, .25, 1.62, 3.72, "n_gold")
    mb.box(-1.62, -.25, .5, 1.62, .25, 3.72, "n_gold")
    bx = mb.build()
    V.glow(bx, {"n_gold": 3.5})
    SV.spin(bx, 1, n_all(n), 30)
    q = V.qmark("q", (0, -.2, 4.4), 1.0, "n_pink", 7)
    pop_in(q, fr(sid, 31.4), 1.0)
    SV.spin(q, fr(sid, 31.4), n_all(n), 40)
    for i, (code, a) in enumerate((("ID", -2.4), ("US", -1.4), ("JP", -.4), ("BR", .6), ("DE", 1.6))):
        x, y = 6.2 * math.cos(a - math.pi / 2), 6.2 * math.sin(a - math.pi / 2)
        p = G.buyer(f"pb{i}", i + 3, (x, y, 0), a, code)
        L.pose(p, "arms_fwd", 1)
        mn, _ = N.money(f"pm{i}", 1, (0, 0, 0), 1, 1, .7)
        p0, p1 = (x * .85, y * .85, 1.4), (0, 0, 2.6)
        f0 = fr(sid, 29.0 + .35 * i)
        key(mn, "location", 1, p0)
        hide_until(mn, f0)
        arc_move(mn, f0, f0 + 16, p0, p1, 2.5)
        anim(mn, "scale", f0 + 14, f0 + 18, (1, 1, 1), (.001,) * 3, "in")
    camera(sid, [(28.10, (0, 0, 2.2), -60, 30, 20), (30.3, (0, 0, 2.4), -90, 18, 17),
                 (32.45, (0, 0, 2.8), -110, 10, 13)], lens=24)
    A["BOX"] = (bx, (0, 0, 4.0))


# ================================================================== KEJUTAN 2
def g09(n, A):
    """Jawabannya: 13 tahun penantian — jalan waktu neon 2013 -> 2026, kamera menyusur cepat."""
    sid = "G09"
    neon(grid="vp_grid", em=1.6, rig_c=(0, 14, 2), rig_s=2.4, fade=(20, 80))
    for k, yr in enumerate(range(2013, 2027)):
        y = k * 3.0
        hk = "n_green" if yr == 2013 else ("n_pink" if yr == 2026 else "n_purple")
        p = V.pillar(f"yr{k}", 1.2 + .25 * k, 1.4, 1.4, hk, 1.6, 5.0, (-2.4, y, 0))
        t = G.H.text(f"yt{k}", str(yr), 1.0, "c_white", depth=.08, loc=(-2.4, y - .3, 1.45 + .25 * k), emission=1.6)
        t.rotation_euler.z = math.radians(-30)
        f0 = fr(sid, 32.5 + .12 * k)
        grow(p, f0, f0 + 7, 1.0)
        pop_in(t, f0 + 3, 1.0, 8)
    v5 = G.H.text("gta5", "GTA V", 1.0, "n_green", depth=.15, loc=(2.0, -.5, 1.2), emission=4.0)
    v5.rotation_euler.z = math.radians(-30)
    lg = G.img_plane("logo6", "logo", h=4.6, loc=(1.8, 13 * 3.0 + .5, 4.4), center=True, em=1.8)
    lg.rotation_euler.z = math.radians(-25)
    pop_in(lg, fr(sid, 33.9), 1.0, 12)
    camera(sid, [(32.45, (0, 0, 1.8), -120, 12, 9.5), (33.7, (0, 18, 2.6), -150, 10, 11),
                 (34.96, (1, 38, 3.8), -118, 8, 12)], lens=24)
    A["Y13"] = ((-2.4, 0, 3.0))
    A["Y26"] = ((-2.4, 39, 6.5))


def g10(n, A):
    """Rockstar nggak perlu banyak promosi: logo raksasa di puncak menara; megafon dicoret."""
    sid = "G10"
    c = city(n, crowd=0, store=True)
    hq = c["hq"]
    lz = hq["logo"].location.z
    ic = V.icon("mg", "marketing", 1.5, (4.8, HQ_Y - 8.5, lz - 4.6), em=4.0)
    ic.rotation_euler.z = math.radians(-35)
    x = V.xmark("x", (4.8, HQ_Y - 10.1, lz - 2.8), 1.5)
    pop_in(x, fr(sid, 35.55), 1.5)
    camera(sid, [(34.96, (2.5, HQ_Y - 7, lz - 2.6), -122, 4, 27), (36.29, (3.5, HQ_Y - 7, lz - 2.2), -86, 8, 26)],
           lens=24)
    A["RS"] = (hq["logo"], (0, 0, 4.8))


def g11(n, A):
    """Stok fisik pertama habis dalam hitungan jam: rak toko kosong cepat, antrean panjang, SOLD OUT."""
    sid = "G11"
    c = city(n, crowd=27)
    st = c["store"]
    cases = st["cases"]
    for i, cs in enumerate(cases):
        f = fr(sid, 36.45 + 1.6 * i / len(cases))
        pop_out(cs, f, 6)
    cl = W.MB("clock")
    cl.disc_y(0, 0, 0, 1.4, .2, "case_blk", n=24)
    cl.disc_y(0, -.12, 0, 1.25, .05, "c_white", n=24)
    clk = cl.build((6.5, 2.6, 9.6))
    hand = W.MB("hand")
    hand.box(-.06, -.25, -.05, .06, -.2, 1.05, "n_pink")
    hd = hand.build((6.5, 2.6, 9.6))
    V.glow(hd, {"n_pink": 5.0})
    anim(hd, "rotation_euler", 1, n_all(n), (0, 0, 0), (0, math.radians(1080), 0), "lin")
    pop_in(clk, fr(sid, 36.5), 1.0)
    t, fo = V.neon_sign("so", "SOLD OUT", (0, 3.0, 9.0), 1.15, "x_red", 9.0)
    for ob in (t, fo):
        pop_in(ob, fr(sid, 38.3), 1.0)
    camera(sid, [(36.29, (0, 4, 4.2), -100, 16, 17), (37.6, (0, 2, 4.6), -94, 13, 19),
                 (38.64, (0, 0, 5.4), -86, 14, 24)], lens=24)
    A["SHELF"] = ((0, 5.2, 4.6))
    A["CLOCK"] = (clk, (0, 0, 1.8))


def g12(n, A):
    """Anehnya, edisi yang lebih mahal justru paling laris: STANDARD vs ULTIMATE, bar penjualan."""
    sid = "G12"
    neon(grid="vp_grid2", em=1.6, rig_c=(0, 0, 3), rig_s=1.6)
    out = {}
    for k, (nm, cov, x, key_, hb, t0) in enumerate((("std", "cover_ps5", -3.6, "n_cyan", 3.2, 39.9),
                                                     ("ult", "cover_ult", 3.6, "n_gold", 8.4, 40.3))):
        V.disc_ped(f"pd{k}", 2.2, key_, (x, 0, 0), em=3.5, h=.4)
        cs = G.game_case(f"c{k}", cov, 1.6, (x, -.2, .4), math.radians(10 if x < 0 else -10))
        p = V.pillar(f"bar{k}", hb, 1.6, 1.6, key_, 1.6, 5.0, (x, 2.8, 0))
        grow(p, fr(sid, t0), fr(sid, t0 + 1.4 + .25 * k), 1.0)
        out[nm] = (cs, p, hb, x)
    cr = V.crown("cr", (3.6, 2.8, 8.4 + 1.0), 1.0, "n_gold", 6.0)
    pop_in(cr, fr(sid, 41.9), 1.0)
    camera(sid, [(38.64, (0, 0, 2.4), -112, 10, 17), (40.5, (0, 0, 3.4), -96, 12, 19),
                 (42.36, (1.2, 0, 4.6), -80, 14, 21)], lens=24)
    A["STD"] = (out["std"][0], (0, 0, 3.0))
    A["ULT"] = (out["ult"][0], (0, 0, 3.0))
    A["BARU"] = (out["ult"][1], (0, 0, 8.8))


def g13(n, A):
    """Padahal ini harga dasar GTA paling mahal sepanjang sejarah: tangga harga, GTA VI tertinggi."""
    sid = "G13"
    neon(grid="vp_grid", em=1.6, rig_c=(0, 0, 3), rig_s=1.8)
    items = [("GTA III", 2.2, "n_purple"), ("GTA IV", 3.4, "n_purple"), ("GTA V", 4.6, "n_cyan"), ("GTA VI", 8.0, "n_gold")]
    tops = []
    for k, (lab, h, key_) in enumerate(items):
        x = -6 + k * 4.0
        p = V.pillar(f"pr{k}", h, 2.4, 2.4, key_, 1.7, 5.0, (x, 0, 0))
        f0 = fr(sid, 42.4 + .45 * k) if k < 3 else fr(sid, 44.0)
        grow(p, f0, f0 + 10 + 6 * (k == 3), 1.0)
        t = G.H.text(f"pl{k}", lab, .55, "c_white", depth=.05, loc=(x, -1.35, .25), emission=1.2)
        pop_in(t, f0, 1.0, 8)
        tops.append((p, h, x))
    cs = G.game_case("vi", "cover_ps5", .9, (6, -.2, 8.0))
    pop_in(cs, fr(sid, 44.6), 1.0)
    SV.spin(cs, 1, n_all(n), 50)
    cr = V.crown("cr", (6, 0, 10.4), .9, "n_gold", 6.0)
    pop_in(cr, fr(sid, 46.0), .9)
    camera(sid, [(42.36, (-4, 0, 1.6), -120, 8, 16), (44.6, (0, 0, 3.4), -98, 10, 20),
                 (47.16, (3, 0, 6.0), -78, 12, 18)], lens=24)
    A["VI"] = (cs, (0, 0, 2.2))
    A["V"] = ((2, 0, 5.2))


# ================================================================== KAIL 2
def g14(n, A):
    """Tapi tunggu, Rp17 triliun itu baru pemanasan: menara emas kecil, lalu bayangan menara raksasa di belakang."""
    sid = "G14"
    neon(grid="vp_grid2", em=1.5, rig_c=(0, 4, 6), rig_s=2.6, fade=(18, 80))
    V.base_plate("bp", 5.0, 5.0, "n_gold", (0, 0, 0), 3.0)
    tw, h = money("tw", 4.0, (0, 0, .14), 1.0, 2, 2)
    ghost = V.pillar("ghost", 30.0, 9.0, 9.0, "n_cyan", .5, 6.0, (0, 14, 0))
    grow(ghost, fr(sid, 49.2), fr(sid, 51.2), 1.0, "inout")
    key(ghost, "scale", 1, (.001,) * 3)
    key(ghost, "scale", fr(sid, 49.2) - 1, (.001,) * 3)
    t, fo = V.neon_sign("wu", "BARU PEMANASAN", (0, -2.6, .9), .55, "n_pink", 7.0)
    for ob in (t, fo):
        pop_in(ob, fr(sid, 50.4), 1.0)
    camera(sid, [(47.16, (0, 0, 2.4), -96, 8, 10), (48.9, (0, 1, 3.0), -92, 10, 13),
                 (50.4, (0, 8, 10), -98, 12, 46), (51.70, (0, 10, 14), -100, 12, 58)], lens=24)
    A["T17"] = (tw, (0, 0, h + .5))
    A["GHOST"] = (ghost, (0, 0, 30.5))


# ================================================================== KEJUTAN 3
def g15(n, A):
    """Analis: pendapatan minggu pertama bisa US$3,25–5,2 miliar — papan grafik neon + dua bar proyeksi."""
    sid = "G15"
    neon(grid="vp_grid", em=1.6, rig_c=(0, 0, 4), rig_s=2.0)
    an = L.character("analis", dict(skin="skin2", top="c_navy", sleeve="c_navy", bottom="c_black", shoe="shoe_dk",
                                    hair="short", hair_col="hair_blk", acc=()), (-6.2, -1.5, 0), .5)
    L.pose(an, "stand", 1)
    L.pose(an, "stand", fr(sid, 52.6))
    L.pose(an, "point", fr(sid, 53.0))
    bd = W.MB("board")
    bd.box(-5.5, .6, 0, 5.5, .9, 8.2, "bd_dark")
    for k in range(5):
        bd.box(-5.0, .55, 1.0 + k * 1.6, 5.0, .6, 1.04 + k * 1.6, "n_purple")
    bo = bd.build()
    V.glow(bo, {"n_purple": 1.8})
    bars = []
    for k, (h, key_, t0) in enumerate(((2.0, "n_gold", 52.0), (4.4, "n_cyan", 54.7), (7.0, "n_pink", 56.4))):
        x = -3.0 + k * 3.0
        p = V.pillar(f"pb{k}", h, 1.8, 1.0, key_, 1.7, 5.0, (x, 0, .2))
        grow(p, fr(sid, t0), fr(sid, t0 + .9), 1.0)
        bars.append((p, h, x))
    pts = [(-4.2, 1.2), (-1.5, 2.2), (0.5, 4.0), (2.4, 5.4), (4.4, 7.6)]
    ln = W.MB("line")
    for (a, b), (c, d) in zip(pts[:-1], pts[1:]):
        L_ = math.hypot(c - a, d - b)
        ang = math.atan2(d - b, c - a)
        ln.prism_y([(a - .1 * math.sin(ang), b + .1 * math.cos(ang)), (c - .1 * math.sin(ang), d + .1 * math.cos(ang)),
                    (c + .1 * math.sin(ang), d - .1 * math.cos(ang)), (a + .1 * math.sin(ang), b - .1 * math.cos(ang))],
                   -.3, -.2, "n_green")
    lo = ln.build()
    V.glow(lo, {"n_green": 6.0})
    key(lo, "scale", 1, (.001, 1, 1))
    anim(lo, "scale", fr(sid, 52.4), fr(sid, 57.0), (.001, 1, 1), (1, 1, 1), "inout")
    lo.location.x = -4.2
    for o in lo.data.vertices:
        o.co.x += 4.2
    camera(sid, [(51.70, (-3, 0, 2.6), -116, 8, 15), (54.5, (0, 0, 3.6), -100, 8, 17),
                 (58.19, (1, 0, 4.4), -76, 10, 18)], lens=24)
    A["B1"] = (bars[1][0], (0, 0, 4.8))
    A["B2"] = (bars[2][0], (0, 0, 7.4))
    A["AN"] = (an["body"], (0, 0, 2.7))


def g16(n, A):
    """Sekitar Rp58–93 triliun, cuma dalam satu minggu: menara uang raksasa menjulang di atas kota Vice City."""
    sid = "G16"
    c = city(n, crowd=18, hq=True, billboards=True)
    towers = []
    for k, (h, x, t0) in enumerate(((5.5, -13, 58.2), (19.0, -4.5, 58.9), (30.0, 6.0, 59.7))):
        tw, th = money(f"mt{k}", h, (x, -9.0, Z0), 1.6, 2, 2)
        grow(tw, fr(sid, t0), fr(sid, t0 + 1.4), 1.0, "inout")
        towers.append((tw, th))
    t, fo = V.neon_sign("wk", "1 MINGGU", (16, -9, 6.0), 1.0, "n_cyan", 8.0)
    for ob in (t, fo):
        pop_in(ob, fr(sid, 61.6), 1.0)
    camera(sid, [(58.19, (-6, -9, 2.6), -108, 4, 26), (60.3, (0, -6, 12), -100, 6, 44),
                 (63.27, (2, -2, 16), -90, 14, 72)], lens=24)
    A["T17"] = (towers[0][0], (0, 0, towers[0][1] + .6))
    A["T58"] = (towers[1][0], (0, 0, towers[1][1] + .6))
    A["T93"] = (towers[2][0], (0, 0, towers[2][1] + .6))


def g17(n, A):
    """Dan itu tanpa versi PC: PS5 menyala dengan GTA VI; PC redup digembok."""
    sid = "G17"
    neon(grid="vp_grid2", em=1.5, rig_c=(0, 0, 2), rig_s=1.5)
    V.disc_ped("p1", 2.6, "n_cyan", (-3.6, 0, 0), em=4.0, h=.4)
    V.disc_ped("p2", 2.6, "n_purple", (3.6, 0, 0), em=1.0, h=.4)
    ps = G.ps5("ps5", (-4.4, .4, .4), .95)
    cs = G.game_case("cs", "cover_ps5", 1.3, (-2.3, -.6, .4), math.radians(14))
    pc = G.pc_tower("pc", (3.6, .4, .4), 1.0, lit=False)
    lk = G.padlock("lk", (3.6, -1.7, 1.2), .8, "x_red", 5.0)
    pop_in(lk, fr(sid, 65.0), .8)
    camera(sid, [(63.27, (-3.4, 0, 2.0), -110, 8, 10), (65.0, (0, 0, 2.2), -92, 10, 15),
                 (66.79, (2.5, 0, 2.2), -76, 10, 12)], lens=24)
    A["PS5"] = (ps, (0, 0, 4.6))
    A["PC"] = (pc, (0, 0, 4.2))


# ================================================================== CTA
def g18(n, A):
    """Tim beli sekarang di PS5 atau tim sabar nunggu PC? Dua kubu pembeli dunia di plaza Vice City."""
    sid = "G18"
    c = city(n, crowd=0, store=False)
    rnd = random.Random(9)
    for side, label, key_, t0 in ((-1, "PS5", "n_cyan", 68.3), (1, "PC", "n_purple", 70.2)):
        tt, fo = V.neon_sign(f"s{label}", label, (side * 10, 2.0, 12.0), 2.0, key_, 8.0)
        for ob in (tt, fo):
            pop_in(ob, fr(sid, t0), 1.0)
        for i in range(14):
            x = side * (5.0 + (i % 5) * 2.2) + rnd.uniform(-.3, .3)
            y = -1.5 - (i // 5) * 2.4
            code = G.FLAGS[(i + (side > 0) * 5) % len(G.FLAGS)] if i % 2 == 0 else None
            p = G.buyer(f"t{label}{i}", i + 7 + (side > 0) * 20, (x, y, Z0), rnd.uniform(-.3, .3), code)
            L.pose(p, "cheer" if i % 3 == 0 else "stand", fr(sid, t0 + .2))
    G.ps5("ps", (-10, -10.5, Z0), .7)
    G.pc_tower("pc", (10, -10.5, Z0), .7, lit=True)
    camera(sid, [(66.79, (0, -4, 3.0), -96, 10, 22), (69.5, (-4, -3, 4.5), -110, 16, 40),
                 (72.0, (4, -3, 5.0), -76, 18, 44), (74.52, (0, -2, 5.6), -90, 22, 54)], lens=24)
    A["PS5"] = ((-10, 2.0, 15.0))
    A["PC"] = ((10, 2.0, 15.0))


def g19(n, A):
    """Kirim ke temen yang udah pre-order; angka = estimasi pihak ketiga. Kamera mundur ke seluruh Vice City."""
    sid = "G19"
    c = city(n, crowd=18)
    me = L.character("kamu", "cowok", (-3.0, -8.0, Z0), .3, hold="phone")
    L.pose(me, "point", 1)
    fd = L.character("teman", "mahasiswa", (5.0, -8.5, Z0), -.5, hold=None)
    L.pose(fd, "stand", 1)
    L.pose(fd, "stand", fr(sid, 76.6))
    L.pose(fd, "wave", fr(sid, 77.0))
    pl = V.paper_plane("pl", (0, 0, 0), .6)
    p0, p1 = (-2.6, -8.4, 2.6), (4.6, -8.6, 2.8)
    key(pl, "location", 1, p0)
    pl.rotation_euler = (0, 0, -math.pi / 2)
    pop_in(pl, fr(sid, 75.0), .6)
    arc_move(pl, fr(sid, 75.2), fr(sid, 76.6), p0, p1, 2.2)
    pop_out(pl, fr(sid, 76.7))
    lg = G.img_plane("logo", "logo", h=22, loc=(0, 10, 52), center=True, em=1.6)
    pop_in(lg, fr(sid, 78.4), 1.0, 16)
    camera(sid, [(74.52, (1, -8, 2.4), -96, 12, 16), (76.6, (1, -7, 2.4), -94, 16, 26),
                 (78.6, (0, -4, 8), -100, 24, 90), (83.6, (0, 0, 22), -112, 26, 190)], lens=24)
    A["ME"] = (me["body"], (0, 0, 2.7))
    A["TEMAN"] = (fd["body"], (0, 0, 2.7))


SCENES = {f"G{i:02d}": globals()[f"g{i:02d}"] for i in range(1, 20)}
K.SCENES = SCENES

if __name__ == "__main__":
    K.main()
