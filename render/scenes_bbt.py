"""Adegan "Bedah Bisnis: Sponsor terbesar Persib itu bukan Indofood, bukan bank bjb — tapi kamu (bobotoh)".
Konsep 2 dunia: kota BANDUNG diorama besar (GBLA penuh bobotoh, Gedung Sate, Jl. Asia Afrika dengan 16 papan
sponsor, toko PERSIB, alun-alun & Masjid Raya, menara NexAI) + panggung neon gaya video edukasi bisnis (logo resmi
16 sponsor, pilar perbandingan, timbangan, grid bobotoh, jersey 3D, papan saham, berita). Tiap adegan langsung
terisi sejak frame pertama, kamera selalu bergerak, sudut bervariasi.

  PSB_TEX=DIR python3 render/scenes_bbt.py -- --scene B01 --out DIR [--res 864x1536] [--samples 4] [--frames a-b]
"""
import math
import os
import random
import sys

import bpy  # noqa: F401

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowpoly as lp  # noqa: E402,F401
import world as W  # noqa: E402
import world_psb as P  # noqa: E402   (sebelum world_fom: set G.TEX dari PSB_TEX)
import world_fom as F  # noqa: E402
import world_laundry as L  # noqa: E402
import world_prk as R  # noqa: E402
import world_vap as V  # noqa: E402
import world_bdg as B  # noqa: E402
import scenes_nkh as K  # noqa: E402
import scenes_ojl as SO  # noqa: E402
import scenes_vap as SV  # noqa: E402
from scenes_nkh import TAIL, anim, arc_move, key, pop_in, pop_out  # noqa: E402

TIMELINE = [("B01", 0.00), ("B02", 2.30), ("B03", 4.45), ("B04", 5.83), ("B05", 9.30), ("B06", 13.69),
            ("B07", 17.41), ("B08", 21.30), ("B09", 27.25), ("B10", 30.50), ("B11", 35.39), ("B12", 41.54),
            ("B13", 47.40), ("B14", 51.98), ("B15", 55.96), ("B16", 60.85), ("B17", 65.87), ("B18", 69.50),
            ("B19", 73.53)]
END_T = 79.3
CITY = {"B01", "B03", "B04", "B06", "B09", "B11", "B19"}
K.TIMELINE, K.END_T, K.CITY = TIMELINE, END_T, CITY
G0 = B.G0
sign, pop_pair, phone, coin_arc, float_bob = SO.sign, SO.pop_pair, SO.phone, SO.coin_arc, SO.float_bob


def fr(sid, t):
    return K.fr(sid, t)


def camera(sid, keys, **kw):
    return K.camera(sid, keys, **kw)


def n_all(n):
    return n + TAIL


def kota(n, jump=True):
    info = B.city_bdg(n + TAIL)
    if jump:
        P.crowd_jump(info["gbla"]["fans"], 1, n_all(n), .12, 13)
    return info


def neon(**kw):
    kw.setdefault("grid", "vp_grid")
    return K.neon(**kw)


def grow_z(ob, f0, f1, kind="out"):
    key(ob, "scale", 1, (1, 1, .001))
    key(ob, "scale", f0, (1, 1, .001))
    anim(ob, "scale", f0, f1, (1, 1, .001), (1, 1, 1), kind)


def slam(ob, f, z_from, z_to, dur=7):
    """jatuh dari atas lalu menghentak (logo/kartu)."""
    x, y = ob.location.x, ob.location.y
    key(ob, "location", 1, (x, y, z_from))
    key(ob, "location", f, (x, y, z_from))
    anim(ob, "location", f, f + dur, (x, y, z_from), (x, y, z_to), "in")
    key(ob, "scale", 1, (.001,) * 3)
    key(ob, "scale", f - 1, (.001,) * 3)
    key(ob, "scale", f, (1, 1, 1))
    key(ob, "scale", f + dur, (1.12, 1.12, .86))
    key(ob, "scale", f + dur + 4, (1, 1, 1))


# ================================================================== KORBAN
def b01(n, A):
    """Sponsor terbesar Persib itu...: kota Bandung dari udara (Gedung Sate, jalan, papan sponsor) menukik ke
    Stadion GBLA yang penuh bobotoh melompat."""
    sid = "B01"
    info = kota(n)
    cx, cy = B.GBLA_C
    P.flares("fl", 30, (cx - 16, cy - 15, cx + 16, cy - 12), G0 + 4.0, 3)
    camera(sid, [(0.0, (20, 20, 0), -120, 46, 250), (1.25, (cx - 6, cy - 6, 4), -104, 36, 92),
                 (2.30, (cx, cy - 2, 5), -94, 30, 46)], lens=24)
    A["GBLA"] = (info["gbla"]["sign"], (0, 0, 2.6))


def b02(n, A):
    """...bukan Indofood, bukan bank bjb: dua plakat logo resmi menghentak masuk lalu dicoret silang merah."""
    sid = "B02"
    neon(rig_c=(0, 0, 3.5), rig_s=1.4)
    c1 = P.logo_card("c1", "sp01", 1.3, (0, 0, 4.7), 0.0, pad=.32, em=1.2, plate_em=.8)
    c2 = P.logo_card("c2", "sp03", 1.5, (0, 0, 1.6), 0.0, pad=.32, em=1.2, plate_em=.8)
    slam(c1, fr(sid, 2.62), 9.0, 4.7)
    slam(c2, fr(sid, 3.70), 7.5, 1.6)
    x1 = B.cross_x("x1", (0, -.4, 5.65), 1.25)
    x2 = B.cross_x("x2", (0, -.4, 2.7), 1.25)
    pop_in(x1, fr(sid, 3.30), 1.0, 6)
    pop_in(x2, fr(sid, 4.30), 1.0, 6)
    camera(sid, [(2.30, (0, 0, 4.0), -80, 6, 12.5), (3.6, (0, 0, 3.9), -90, 5, 11.5), (4.45, (0, 0, 3.8), -98, 6, 11)],
           lens=24)


def b03(n, A):
    """...tapi KAMU: di dalam GBLA, bobotoh berjersey biru di pinggir tribun menunjuk ke kamera; tribun melompat,
    suar biru menyala di belakang."""
    sid = "B03"
    info = kota(n)
    cx, cy = B.GBLA_C
    s = B.GBLA_S
    yb = cy - 9.3 * s
    me = B.bobotoh("me", (cx, yb, G0), math.pi, None, "bobotoh")
    L.pose(me, "point", 1)
    L.pose(me, "point", n_all(n))
    for k, dx in enumerate((-1.3, 1.25, -2.4, 2.3)):
        o = B.bobotoh(f"fan{k}", (cx + dx, yb - .9 - .3 * (k // 2), G0), math.pi + .2 * (1 if dx < 0 else -1), "cheer")
        _ = o
    P.flares("fl", 26, (cx - 10, cy - 16, cx + 10, cy - 12), G0 + 4.4, 5)
    camera(sid, [(4.45, (cx, yb + .2, 1.9), 92, 10, 7.6), (5.2, (cx, yb, 1.75), 90, 7, 5.6), (5.83, (cx, yb, 1.7), 88, 6, 5.0)],
           lens=24)
    _ = info


# ================================================================== KEJUTAN 1: sponsor vs bobotoh
def b04(n, A):
    """16 sponsor Persib musim ini: menyusuri Jl. Asia Afrika, 16 papan reklame logo sponsor muncul beruntun di
    dua sisi jalan; lalu lintas motor bobotoh."""
    sid = "B04"
    info = kota(n)
    for i, bd in enumerate(info["boards"]):
        pop_in(bd, fr(sid, 5.9 + .17 * i), 1.0, 8)
    camera(sid, [(5.83, (14, 1, 4.0), 206, 30, 38), (7.6, (28, 1, 4.5), 194, 30, 38), (9.30, (42, 1, 5.0), 180, 28, 36)],
           lens=24)
    A["BD"] = (info["boards"][2], (0, 0, 7.0))


def b05(n, A):
    """...diperkirakan menyetor Rp43–77 miliar setahun: dinding 16 logo resmi (4x4) menyala beruntun, tumpukan uang
    naik di depan; berita RM.id (Deputy CEO Adhitia) di kanan depan."""
    sid = "B05"
    neon(rig_c=(0, 0, 4), rig_s=1.6)
    for i, img in enumerate(B.SPONSORS):
        r, c = divmod(i, 4)
        x = (c - 1.5) * 1.72
        z = 6.3 - r * 1.05
        cd = P.logo_card(f"lw{i}", img, .55, (x, 2.0, z), 0.0, pad=.16, em=1.25, plate_em=.85)
        if cd["w"] > 1.6:
            sc = 1.6 / cd["w"]
            cd.scale = (sc, sc, sc)
        pop_in(cd, fr(sid, 9.35 + .045 * i), cd.scale.x, 7)
    m, h = R.money_stack("mn", 6, (-1.5, -2.2, 0), "money_red", 2, 2, .7)
    grow_z(m, fr(sid, 9.4), fr(sid, 11.0))
    rm = phone("rm", "art_rm16", 4.0, (2.55, -2.2, .1), -.28, sid, 10.2, n, .35)
    camera(sid, [(9.30, (0, 0, 4.0), -80, 8, 15), (11.5, (0, 0, 3.9), -90, 7, 14.5), (13.69, (.2, 0, 3.8), -100, 8, 14.5)],
           lens=24)
    A["RM"] = (rm["root"], (0, 0, 4.2))
    _ = h


def b06(n, A):
    """Sementara bobotoh, dari tiket dan jersey aja: toko PERSIB di Jl. Asia Afrika — antrean bobotoh berjersey,
    jersey di etalase; papan TIKET & JERSEY menyala tepat di kata; lalu kamera naik melihat arus bobotoh."""
    sid = "B06"
    info = kota(n)
    cx, cy = B.STORE_C
    yf = cy - 5.0
    s1, s1f = sign("tk", "TIKET", (cx - 5.0, yf - 1.2, 4.3), .55, "n_cyan", 8.0)
    s2, s2f = sign("js", "JERSEY", (cx + 5.0, yf - 1.2, 4.3), .55, "n_gold", 8.0)
    pop_pair((s1, s1f), fr(sid, 14.95))
    pop_pair((s2, s2f), fr(sid, 15.45))
    for k, q in enumerate(info["store"]["queue"]):
        L.walk_cycle(q, 1, n_all(n), 18, .25, arms=False)
    camera(sid, [(13.69, (cx - 3, yf - 1, 3.2), -66, 14, 22), (15.6, (cx - 1, yf - 1, 3.6), -80, 16, 21),
                 (17.41, (cx + 1, yf, 5.0), -94, 24, 22)], lens=24)
    A["ST"] = (info["store"]["sign"], (0, 0, 1.6))


def b07(n, A):
    """bisa menyumbang Rp68–118 miliar: dua pilar neon — SPONSOR (16 brand) vs BOBOTOH; pilar bobotoh menjulang
    lebih tinggi dengan kerumunan mini di puncaknya."""
    sid = "B07"
    neon(rig_c=(0, 0, 4), rig_s=1.6, fade=(14, 60))
    p1 = V.pillar("ps", 3.6, 2.2, 2.2, "n_cyan", 1.4, 6.0, (-1.6, 0, 0))
    p2 = V.pillar("pb", 5.6, 2.2, 2.2, "n_purple", 1.4, 6.0, (1.6, 0, 0))
    grow_z(p1, fr(sid, 17.5), fr(sid, 18.3))
    grow_z(p2, fr(sid, 17.45 + 0), fr(sid, 17.46 + .02))
    key(p2, "scale", fr(sid, 17.5), (1, 1, .001))
    anim(p2, "scale", fr(sid, 18.6), fr(sid, 19.9), (1, 1, .001), (1, 1, 1), "out")
    rows = B.mini_grid("tb", 12, 4, (1.6, 0, 5.62), .5, .5)
    for k, r in enumerate(rows):
        pop_in(r, fr(sid, 19.9 + .1 * k), 1.0, 7)
    l1 = P.logo_card("l1", "sp01", .5, (-1.6, -1.25, 1.2), 0.0, pad=.14, em=1.2, plate_em=.8)
    l2 = P.logo_card("l2", "sp03", .55, (-1.6, -1.25, 2.3), 0.0, pad=.14, em=1.2, plate_em=.8)
    for c in (l1, l2):
        if c["w"] > 1.9:
            sc = 1.9 / c["w"]
            c.scale = (sc, sc, sc)
        pop_in(c, fr(sid, 17.9), c.scale.x, 7)
    lg = P.logo_card("lb", "lg_persib", 1.1, (1.6, -1.25, 2.6), 0.0, plate=None, em=1.4)
    pop_in(lg, fr(sid, 19.0), 1.0, 8)
    v1, v1f = sign("v1", "Rp43-77 M", (-1.6, -1.3, 4.3), .36, "n_cyan", 8.0)
    v2, v2f = sign("v2", "Rp68-118 M", (1.6, -1.3, 7.05), .36, "n_purple", 8.0)
    pop_pair((v1, v1f), fr(sid, 17.7))
    pop_pair((v2, v2f), fr(sid, 19.6))
    camera(sid, [(17.41, (0, 0, 4.2), -104, 8, 15.5), (19.4, (0, 0, 4.4), -90, 7, 15.5), (21.30, (.2, 0, 4.5), -78, 8, 16)],
           lens=24)


def b08(n, A):
    """Kalau bobotoh itu perusahaan, dia sponsor terbesar — lebih besar dari semua brand digabung: timbangan
    neon; 16 logo sponsor berdatangan ke piring kiri, bobotoh berjersey di piring kanan — timbangan miring ke
    bobotoh."""
    sid = "B08"
    neon(rig_c=(0, 0, 4), rig_s=1.6)
    bl = B.balance("bal", (0, 0, 0), 3.0, 6.4, 1.4)
    bl["set"](fr(sid, 22.0), -.10)
    bl["set"](fr(sid, 23.0), .02)
    bl["set"](fr(sid, 23.55), .24)
    bl["set"](fr(sid, 25.2), .22)
    bl["set"](fr(sid, 26.0), .32)
    bl["set"](n_all(n), .32)
    pl, pr = bl["pans"]
    me = B.bobotoh("me", (0, 0, 0), 0.0, "cheer", "bobotoh")
    me["body"].parent = pr
    me["body"].location = (0, 0, .02)
    me["body"].scale = (.8, .8, .8)
    pop_in(me["body"], fr(sid, 21.4), .8, 8)
    stack = []
    for i, img in enumerate(B.SPONSORS):
        cd = P.logo_card(f"sk{i}", img, .32, (0, 0, 0), 0.0, pad=.09, em=1.2, plate_em=.8)
        sc = min(1.0, .72 / cd["w"])
        cd.parent = pl
        col, row = i % 4, i // 4
        tgt = ((col - 1.5) * .72, .3 - .3 * row, .05 + row * .34)
        f0 = fr(sid, 24.3 + .07 * i)
        key(cd, "location", 1, (tgt[0] * 3, -2.0, tgt[2] + 6))
        key(cd, "location", f0, (tgt[0] * 3, -2.0, tgt[2] + 6))
        anim(cd, "location", f0, f0 + 9, (tgt[0] * 3, -2.0, tgt[2] + 6), tgt, "out")
        key(cd, "scale", 1, (.001,) * 3)
        key(cd, "scale", f0, (.001,) * 3)
        key(cd, "scale", f0 + 4, (sc, sc, sc))
        stack.append(cd)
    sg, sgf = sign("pt", "BOBOTOH", (2.9, -1.4, 9.0), .4, "n_cyan", 8.0)
    pop_pair((sg, sgf), fr(sid, 22.2))
    s2, s2f = sign("all", "16 BRAND DIGABUNG", (-2.4, -1.4, 9.9), .32, "n_gold", 8.0)
    pop_pair((s2, s2f), fr(sid, 25.25))
    camera(sid, [(21.30, (0, 0, 5.0), -100, 6, 17.5), (24.0, (0, 0, 5.1), -90, 6, 17.5), (27.25, (.2, 0, 5.2), -80, 8, 18)],
           lens=24)


def b09(n, A):
    """Bedanya makin kerasa kalau dihitung per kepala: dari atas alun-alun Bandung yang penuh bobotoh, Masjid Raya
    di sampingnya; kamera turun mendekati kepala-kepala bobotoh."""
    sid = "B09"
    info = kota(n)
    ax, ay = info["alun"]["center"]
    camera(sid, [(27.25, (ax - 8, ay + 2, 6), -46, 46, 80), (29.0, (ax - 4, ay + 1, 3), -56, 40, 52),
                 (30.50, (ax, ay, 1.5), -66, 36, 34)], lens=24)
    A["AL"] = ((ax, ay - 12, G0 + 1.0))
    A["MJ"] = ((B.MASJID_C[0] + 4, B.MASJID_C[1] - 12, G0 + 35))


def b10(n, A):
    """Uang sponsor dibagi ke ~6 juta bobotoh = cuma ~Rp10 ribu/orang/tahun: tumpukan uang melayang di atas
    lautan bobotoh mini, pecah jadi hujan koin kecil."""
    sid = "B10"
    neon(rig_c=(0, 0, 3), rig_s=1.6)
    B.pad("pad", 8.4, 5.4, (0, -1.0, 0), "pad_lt", .35)
    rows = B.mini_grid("cr", 15 * 10, 15, (0, -1.0, .06), .52, .48, seed=9)
    for k, r in enumerate(rows):
        pop_in(r, fr(sid, 30.55 + .05 * k), 1.0, 7)
    m, h = R.money_stack("mn", 6, (0, 2.6, 4.0), "money_red", 2, 2, .7)
    pop_in(m, fr(sid, 30.6), 1.0, 8)
    key(m, "scale", fr(sid, 32.3), (1, 1, 1))
    anim(m, "scale", fr(sid, 32.3), fr(sid, 33.4), (1, 1, 1), (.25, .25, .25), "in")
    coin_arc("cc", sid, 32.4, 34, (0, 2.6, 4.4), (0, -1.0, .6), .035, .32, 1.0, 7, 16)
    sg, sgf = sign("dv", "DIBAGI 6 JUTA BOBOTOH", (0, 2.6, 6.4), .34, "n_cyan", 8.0)
    pop_pair((sg, sgf), fr(sid, 31.9))
    camera(sid, [(30.50, (0, 0, 2.8), -96, 26, 15), (33.0, (0, 0, 2.6), -90, 30, 14.5), (35.39, (0, 0, 2.4), -84, 34, 14)],
           lens=24)


def b11(n, A):
    """Sedangkan kamu, buat satu jersey versi pemain aja, keluar Rp1,19 juta: depan toko PERSIB — bobotoh berjalan
    ke jersey pemain yang dipajang besar; label harga menyala; berita peluncuran jersey 2026/27 melayang."""
    sid = "B11"
    info = kota(n)
    cx, cy = B.STORE_C
    yf = cy - 5.0
    js = B.jersey("jz", (cx + 1.6, yf - 1.6, G0 + .4), .62, chest="sp10")
    pop_in(js["root"], fr(sid, 36.6), 1.0, 9)
    me = B.bobotoh("me", (cx - 3.6, yf - 4.2, G0), -math.pi / 2 + .5, None, "bobotoh2")
    K.path_walk(me, [(cx - 3.6, yf - 4.2, G0), (cx - .4, yf - 3.0, G0)], 1, fr(sid, 37.4), 16)
    pr, prf = sign("pr", "Rp1.191.919", (cx + 1.6, yf - 2.0, 3.25), .34, "n_gold", 8.0)
    pop_pair((pr, prf), fr(sid, 38.9))
    camera(sid, [(35.39, (cx - .6, yf - 2.2, 2.2), -62, 8, 10.5), (38.0, (cx, yf - 2.2, 2.2), -80, 6, 9.0),
                 (41.54, (cx + .4, yf - 2.2, 2.3), -96, 6, 8.6)], lens=24)
    A["ST"] = (info["store"]["sign"], (0, 0, 1.6))


def b12(n, A):
    """Satu jersey = jatah 119 bobotoh dari uang sponsor: jersey di belakang, 119 bobotoh mini muncul bergelombang
    di depan."""
    sid = "B12"
    neon(rig_c=(0, 0, 3), rig_s=1.6)
    js = B.jersey("jz", (0, 2.8, 2.0), 1.0, chest="sp10")
    pop_in(js["root"], fr(sid, 41.6), 1.0, 9)
    float_bob(js["root"], 1, n_all(n), .12, 60)
    B.pad("pad", 6.2, 5.6, (0, -2.2, 0), "pad_lt", .35)
    aj = phone("aj", "art_acl", 3.4, (-3.0, .9, .1), .3, sid, 41.7, n, .3)
    A["AJ"] = (aj["root"], (0, 0, 3.6))
    rows = B.mini_grid("g", 119, 11, (0, -2.2, .06), .5, .52, seed=4)
    for k, r in enumerate(rows):
        pop_in(r, fr(sid, 43.75 + .07 * k), 1.0, 7)
    eq, eqf = sign("eq", "=", (0, .8, 1.3), .7, "n_white", 8.0)
    pop_pair((eq, eqf), fr(sid, 43.6))
    camera(sid, [(41.54, (0, 0, 3.2), -98, 18, 14), (44.4, (0, -.5, 3.0), -90, 24, 14), (47.40, (0, -1, 2.8), -82, 28, 14)],
           lens=24)


# ================================================================== KAIL: dada jersey & NexAI
def b13(n, A):
    """Tapi yang bayar paling besar justru nggak dapat tempat di jersey: jersey raksasa, logo sponsor kecil
    menempel di lengan/bawah; kartu BOBOTOH terbang ke dada lalu terpental, silang merah."""
    sid = "B13"
    neon(rig_c=(0, 0, 3.5), rig_s=1.6)
    js = B.jersey("jz", (0, 1.0, .4), 1.45)
    pop_in(js["root"], fr(sid, 47.45), 1.0, 8)
    s = 1.45
    for k, (img, lx, lz) in enumerate((("sp01", -2.75, 3.05), ("sp03", 2.75, 3.05), ("sp02", -1.1, 1.0), ("sp11", 1.1, 1.0))):
        c = P.logo_card(f"pt{k}", img, .26 * s, (lx, .75, lz + .4), 0.0, pad=.06 * s, em=1.2, plate_em=.8)
        if c["w"] > 1.3:
            sc = 1.3 / c["w"]
            c.scale = (sc, sc, sc)
        pop_in(c, fr(sid, 47.9 + .18 * k), c.scale.x, 7)
    slot = W.MB("slot")
    w, h = 2.2, 1.0
    z0 = .4 + 1.35 * s - .1
    for (a, b, c_, d) in ((-w / 2, w / 2, 0, .06), (-w / 2, w / 2, h - .06, h), (-w / 2, -w / 2 + .06, 0, h), (w / 2 - .06, w / 2, 0, h)):
        slot.box(a, -.02, c_, b, .02, d, "n_white")
    so = slot.build((0, .7, z0))
    V.glow(so, {"n_white": 6.0})
    pop_in(so, fr(sid, 48.7), 1.0, 7)
    bc, bcf = sign("bb", "BOBOTOH", (0, -3.0, z0 + .3), .34, "n_cyan", 8.0)
    pop_pair((bc, bcf), fr(sid, 49.6))
    f0, f1, f2 = fr(sid, 50.0), fr(sid, 50.6), fr(sid, 51.2)
    for ob in (bc, bcf):
        if ob is None:
            continue
        p0 = tuple(ob.location)
        p1 = (p0[0], .2, p0[2])
        p2 = (p0[0] - 3.2, -2.6, p0[2] - 2.4)
        key(ob, "location", f0, p0)
        anim(ob, "location", f0, f1, p0, p1, "in")
        anim(ob, "location", f1, f2, p1, p2, "out")
        key(ob, "rotation_euler", f1, (0, 0, 0))
        key(ob, "rotation_euler", f2, (0, -.6, 0))
    for ob in (bc, bcf):
        if ob is not None:
            pop_out(ob, f2 - 2, 6)
    xx = B.cross_x("xx", (0, .5, z0 + .5), .7)
    pop_in(xx, fr(sid, 50.75), 1.0, 6)
    camera(sid, [(47.40, (0, 0, 3.6), -76, 6, 16.5), (49.6, (0, 0, 3.6), -88, 6, 16), (51.98, (0, 0, 3.6), -98, 6, 15.5)],
           lens=24)


def b14(n, A):
    """Bagian dada, posisi paling mahal, ditempati NexAI: kamera mendekat ke dada jersey, cincin sorot menyala,
    papan POSISI PALING MAHAL, logo NexAI menghentak ke dada."""
    sid = "B14"
    neon(rig_c=(0, 0, 3.5), rig_s=1.6)
    s = 1.45
    js = B.jersey("jz", (0, 1.0, .4), s)
    for k, (img, lx, lz) in enumerate((("sp01", -2.75, 3.05), ("sp03", 2.75, 3.05), ("sp02", -1.1, 1.0), ("sp11", 1.1, 1.0))):
        c = P.logo_card(f"pt{k}", img, .26 * s, (lx, .75, lz + .4), 0.0, pad=.06 * s, em=1.2, plate_em=.8)
        if c["w"] > 1.3:
            sc = 1.3 / c["w"]
            c.scale = (sc, sc, sc)
    zc = .4 + 1.35 * s
    rg = V.ring_obj("rg", (0, .6, zc + .45), 1.2, .06, "n_gold", 8.0)
    rg.rotation_euler = (math.pi / 2, 0, 0)
    pop_in(rg, fr(sid, 52.3), 1.0, 8)
    mh, mhf = sign("mh", "POSISI PALING MAHAL", (0, -.6, zc + 1.78), .22, "n_gold", 8.0)
    pop_pair((mh, mhf), fr(sid, 53.25))
    lg = B.chest_logo("nx", "sp10", s)
    lg.location = (0, .78, zc - .1)
    slam(lg, fr(sid, 54.75), zc + 6.0, zc - .1, 6)
    camera(sid, [(51.98, (0, 0, 3.6), -98, 6, 15.5), (53.6, (0, .3, zc + .6), -92, 4, 9.5), (55.96, (0, .4, zc + .5), -88, 3, 7.0)],
           lens=24)
    _ = js


def b15(n, A):
    """...nilai kontraknya diperkirakan paling kecil, cuma Rp0,8–2 miliar: pilar total 16 sponsor vs pilar mungil
    NexAI; berita EmitenNews (NexAI masuk daftar sponsor) di kanan depan."""
    sid = "B15"
    neon(rig_c=(0, 0, 4), rig_s=1.6, fade=(14, 60))
    p1 = V.pillar("pt", 5.0, 2.2, 2.2, "n_cyan", 1.4, 6.0, (-1.6, 0, 0))
    p2 = V.pillar("pn", .5, 2.2, 2.2, "n_pink", 1.4, 6.0, (1.6, 0, 0))
    grow_z(p1, fr(sid, 56.0), fr(sid, 56.7))
    grow_z(p2, fr(sid, 58.2), fr(sid, 58.6))
    l2 = P.logo_card("ln", "sp10", .9, (1.6, -.2, .75), 0.0, pad=.18, em=1.2, plate_em=.85)
    pop_in(l2, fr(sid, 56.1), 1.0, 8)
    v1, v1f = sign("v1", "16 SPONSOR Rp43-77 M", (-1.4, -1.3, 5.75), .26, "n_cyan", 8.0)
    v2, v2f = sign("v2", "Rp0,8-2 M", (1.6, -1.3, 2.9), .42, "n_pink", 8.0)
    pop_pair((v1, v1f), fr(sid, 56.6))
    pop_pair((v2, v2f), fr(sid, 58.3))
    an = phone("an", "art_nxsp", 4.0, (2.95, -2.7, .1), -.3, sid, 57.3, n, .3)
    camera(sid, [(55.96, (0, 0, 4.0), -110, 8, 16), (58.4, (0, 0, 3.9), -92, 6, 15.5), (60.85, (.3, 0, 3.9), -80, 8, 15.5)],
           lens=24)
    A["AN"] = (an["root"], (0, 0, 4.4))


def b16(n, A):
    """Padahal Januari–September nilai perusahaannya naik ~Rp24 triliun: papan bursa LED dengan lilin naik
    beruntun, logo NexAI di atasnya, panah menembus; berita Kontan (saham MGLV melesat) kiri depan."""
    sid = "B16"
    neon(rig_c=(0, 0, 4), rig_s=1.6)
    bd = P.stock_board("bd", (0, 2.2, .3), 7.4, 4.6, 12, 7)
    pop_in(bd["board"], fr(sid, 60.9), 1.0, 8)
    for i, c in enumerate(bd["candles"]):
        pop_in(c, fr(sid, 61.5 + .17 * i), 1.0, 5)
    lg = P.logo_card("nx", "sp10", .8, (0, 2.0, 5.2), 0.0, pad=.16, em=1.2, plate_em=.85)
    pop_in(lg, fr(sid, 60.95), 1.0, 8)
    ar = W.MB("arrow")
    ar.box(-.25, -.25, 0, .25, .25, 5.0, "n_green")
    ar.poly([(-.9, 0, 5.0), (.9, 0, 5.0), (0, 0, 6.6)], [(0, 1, 2)], "n_green")
    aro = ar.build((3.0, -.6, 0))
    V.glow(aro, {"n_green": 7.0})
    grow_z(aro, fr(sid, 64.9), fr(sid, 65.6))
    ak = phone("ak", "art_kontan", 4.0, (-2.8, -2.4, .1), .3, sid, 62.0, n, .3)
    camera(sid, [(60.85, (0, 0, 3.8), -74, 8, 15.5), (63.5, (0, 0, 3.7), -90, 6, 15), (65.87, (0, 0, 3.6), -102, 8, 15)],
           lens=24)
    A["AK"] = (ak["root"], (0, 0, 4.4))


def b17(n, A):
    """...setara 400 tahun uang sponsor Persib: satu tumpukan kecil '1 TAHUN' di depan, lalu 400 tumpukan mini
    (20x20) naik bergelombang di belakang."""
    sid = "B17"
    neon(rig_c=(0, 0, 3), rig_s=1.6)
    m1, _h = R.money_stack("one", 3, (0, -3.6, 0), "money_red", 1, 1, .6)
    pop_in(m1, fr(sid, 65.95), 1.0, 7)
    s1, s1f = sign("s1", "1 TAHUN", (0, -3.8, 1.6), .3, "n_white", 7.0)
    pop_pair((s1, s1f), fr(sid, 66.0))
    rows = []
    for r in range(20):
        mb = W.MB(f"w{r}")
        for c in range(20):
            x = (c - 9.5) * .42
            y = r * .5
            mb.box(x - .17, y - .1, 0, x + .17, y + .1, .32, "money_red")
            mb.box(x - .175, y - .105, .3, x + .175, y + .105, .33, "money_red2")
        ob = mb.build((0, -1.6, 0))
        rows.append(ob)
        grow_z(ob, fr(sid, 66.9 + .045 * r), fr(sid, 66.9 + .045 * r + .35))
    sg, sgf = sign("x4", "x400", (0, 4.0, 4.2), .9, "n_gold", 8.0)
    pop_pair((sg, sgf), fr(sid, 67.2))
    camera(sid, [(65.87, (0, -2.6, 1.4), -90, 18, 9.5), (67.4, (0, 0, 2.0), -90, 30, 14), (69.50, (0, 1, 2.4), -90, 38, 16)],
           lens=24)


def b18(n, A):
    """Di jajaran manajemen NexAI ada Glenn Sugita — orang yang juga mengendalikan Persib: logo NexAI & Persib
    tersambung kabel cahaya; papan GLENN SUGITA; berita EmitenNews ('Bos Persib pegang kendali') & ANTARA."""
    sid = "B18"
    neon(rig_c=(0, 0, 4), rig_s=1.6)
    l1 = P.logo_card("l1", "sp10", .85, (-2.2, .6, 6.0), 0.0, pad=.2, em=1.2, plate_em=.85)
    l2 = P.logo_card("l2", "lg_persib", 1.1, (2.2, .6, 5.85), 0.0, pad=.15, em=1.3, plate_em=.85)
    pop_in(l1, fr(sid, 69.55), 1.0, 8)
    pop_in(l2, fr(sid, 69.75), 1.0, 8)
    ln = W.MB("link")
    ln.box(-1.05, .5, 6.65, 1.05, .62, 6.77, "n_gold")
    lo = ln.build()
    V.glow(lo, {"n_gold": 8.0})
    key(lo, "scale", 1, (.001, 1, 1))
    key(lo, "scale", fr(sid, 71.6), (.001, 1, 1))
    anim(lo, "scale", fr(sid, 71.6), fr(sid, 72.5), (.001, 1, 1), (1, 1, 1), "out")
    gs, gsf = sign("gs", "GLENN SUGITA", (0, -.6, 5.0), .4, "n_white", 8.0)
    pop_pair((gs, gsf), fr(sid, 70.9))
    a1 = phone("a1", "art_bos", 4.6, (-1.5, -1.2, .1), .14, sid, 70.0, n, .25)
    a2 = phone("a2", "art_bjb", 4.6, (1.5, -1.4, .1), -.14, sid, 71.7, n, .3)
    camera(sid, [(69.50, (0, 0, 4.0), -82, 6, 15.5), (71.5, (0, 0, 4.0), -90, 6, 15), (73.53, (0, 0, 4.0), -98, 7, 15)],
           lens=24)
    A["A1"] = (a1["root"], (0, 0, 5.3))
    A["A2"] = (a2["root"], (0, 0, 5.3))


# ================================================================== CTA
def b19(n, A):
    """Kalau bobotoh boleh pasang logo sendiri di jersey, kamu mau tulis apa? Di dalam GBLA yang bergemuruh,
    jersey raksasa melayang di atas lapangan dengan tanda tanya di dada; kamera naik mundur sampai seluruh kota
    Bandung terlihat."""
    sid = "B19"
    info = kota(n)
    cx, cy = B.GBLA_C
    js = B.jersey("jz", (cx, cy, G0 + 2.0), 1.8)
    pop_in(js["root"], fr(sid, 73.6), 1.0, 10)
    float_bob(js["root"], 1, n_all(n), .25, 60)
    q = V.qmark("q", (0, 0, 0), .7, "n_gold", 7.0)
    q.parent = js["root"]
    q.location = (0, -.4, 1.35 * 1.8 - .7)
    pop_in(q, fr(sid, 75.0), .7, 9)
    P.flares("fl", 40, (cx - 16, cy - 15, cx + 16, cy - 12), G0 + 4.0, 7)
    camera(sid, [(73.53, (cx, cy, G0 + 4.0), -90, 34, 24), (76.4, (cx, cy, 5), -98, 40, 62),
                 (79.3, (40, 15, 6), -110, 40, 240)], lens=24)
    A["JZ"] = (js["root"], (0, 0, 4.6))
    _ = info


SCENES = {f"B{i:02d}": globals()[f"b{i:02d}"] for i in range(1, 20)}
K.SCENES = SCENES

if __name__ == "__main__":
    K.main()
