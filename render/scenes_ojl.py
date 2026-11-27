"""Adegan "Bedah Bisnis: Ojol bayar Rp15.500, driver bawa pulang Rp11.040 — uangnya ke mana?" (GoTo Q3 2026).
Konsep 2 dunia: kota metropolitan diorama besar (dominan: driver jaket hijau, HP Android, pangkalan ojol, menara
GoTo, deret kuliner, lalu lintas penuh ojol) + panggung neon (angka: slide earnings resmi GoTo, laporan keuangan,
berita, rincian potongan di aplikasi driver, dompet digital). Tiap adegan langsung terisi sejak frame pertama,
kamera selalu bergerak, sudut bervariasi.

  PSB_TEX=DIR python3 render/scenes_ojl.py -- --scene O01 --out DIR [--res 864x1536] [--samples 4] [--frames a-b]
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
import world_ps2 as Q  # noqa: E402
import world_fom as F  # noqa: E402
import world_laundry as L  # noqa: E402
import world_ojl as OJ  # noqa: E402
import world_prk as R  # noqa: E402
import world_vap as V  # noqa: E402
import scenes_nkh as K  # noqa: E402
import scenes_vap as SV  # noqa: E402
from scenes_nkh import TAIL, anim, arc_move, key, pop_in, pop_out  # noqa: E402

TIMELINE = [("O01", 0.00), ("O02", 2.95), ("O03", 8.75), ("O04", 12.95), ("O05", 18.60), ("O06", 23.60),
            ("O07", 28.25), ("O08", 32.60), ("O09", 36.70), ("O10", 43.60), ("O11", 51.20), ("O12", 58.45),
            ("O13", 61.45), ("O14", 67.20), ("O15", 71.70)]
END_T = 79.2
CITY = {"O01", "O02", "O03", "O05", "O08", "O10", "O13", "O14", "O15"}
K.TIMELINE, K.END_T, K.CITY = TIMELINE, END_T, CITY
G0 = OJ.G0

_coin0 = P.coin


def _coin(name, loc, s=1.0):
    ob = _coin0(name, loc, s)
    V.glow(ob, {"coin_g": .9})
    return ob


P.coin = _coin


def fr(sid, t):
    return K.fr(sid, t)


def camera(sid, keys, **kw):
    return K.camera(sid, keys, **kw)


def n_all(n):
    return n + TAIL


def kota(n):
    return OJ.city_ojl(n + TAIL)


def neon(**kw):
    kw.setdefault("grid", "vp_grid")
    return K.neon(**kw)


def sign(name, body, loc, size=.8, key_="n_white", em=6.0, frame=True, rot_z=0.0):
    a, b = V.neon_sign(name, body, loc, size, key_, em, frame)
    for ob in (a, b):
        if ob is not None and rot_z:
            ob.rotation_euler.z = rot_z
    return a, b


def pop_pair(pair, f, s=1.0, dur=8):
    for ob in pair:
        if ob is not None:
            pop_in(ob, f, s, dur)


def out_pair(pair, f, dur=7):
    for ob in pair:
        if ob is not None:
            pop_out(ob, f, dur)


def phone(name, img, h, loc, rot_z, sid, t_pop, n, span=.45, t_scroll=None):
    p = F.article_phone(name, img, h, loc, rot_z,
                        scroll=[(1, 0.0), (fr(sid, t_scroll or t_pop + .5), 0.0), (n_all(n), span)])
    pop_in(p["root"], fr(sid, t_pop), 1.0, 10)
    return p


def float_bob(ob, f0, f1, amp=.2, period=70, phase=0.0):
    z0 = ob.location.z
    for f in range(f0, f1 + 1, 2):
        key(ob, "location", f, (ob.location.x, ob.location.y, z0 + amp * math.sin(2 * math.pi * f / period + phase)))


def coin_arc(prefix, sid, t, n, p0, p1, dt=.06, s=.7, arc=4.0, seed=1, dur=18):
    rnd = random.Random(seed)
    for i in range(n):
        f0 = fr(sid, t + dt * i)
        c = P.coin(f"{prefix}{i}", p0, s)
        q0 = (p0[0] + rnd.uniform(-1, 1), p0[1] + rnd.uniform(-1, 1), p0[2])
        q1 = (p1[0] + rnd.uniform(-1.2, 1.2), p1[1] + rnd.uniform(-1, 1), p1[2] + rnd.uniform(-.5, .5))
        arc_move(c, f0, f0 + dur, q0, q1, arc, "inout")
        key(c, "scale", 1, (.001,) * 3)
        key(c, "scale", f0 - 1, (.001,) * 3)
        key(c, "scale", f0 + 2, (s, s, s))
        key(c, "scale", f0 + dur - 2, (s, s, s))
        key(c, "scale", f0 + dur + 2, (.001,) * 3)
        c.rotation_euler = (rnd.uniform(0, 3), rnd.uniform(0, 3), 0)


def screen(name, img, w, loc, rot_z=0.0, em=1.1, t_pop=None, sid=None):
    """panel layar/slide berbingkai tipis (P.photo dengan border hitam tipis)."""
    ob = P.photo(name, img, w * .5625 if False else w, loc, rot_z, em=em, border=.05)
    if t_pop is not None:
        pop_in(ob, fr(sid, t_pop), 1.0, 10)
    return ob


# ================================================================== KORBAN
def o01(n, A):
    """Bayar ojol Rp15.500: kota metropolitan dari udara menukik ke pojok perempatan; ojol berhenti, penumpang turun
    membayar lewat HP; kartu 'Rp15.500' melayang."""
    sid = "O01"
    info = kota(n)
    bx, by = OJ.BASE_C
    rd = OJ.ojol_rider("rd", (bx + 6.0, by + 6.6, G0), 0.0, .85)
    anim(rd, "location", 1, fr(sid, 1.4), (bx - 14, by + 7.4, G0), (bx + 4.0, by + 7.4, G0), "out")
    ps = L.character("ps", "cewek", (bx + 5.4, by + 5.0, G0), math.pi - .4, hold="phone")
    pop_in(ps["body"], fr(sid, 1.2), L.CH_S, 8)
    fc = P.photo("fc", "fare_card", 2.2, (bx + 4.6, by + 5.4, 4.2), math.pi, em=.85, border=.05)
    pop_in(fc, fr(sid, 1.4), 1.0, 9)
    camera(sid, [(0.0, (0, 0, 0), 64, 52, 300), (1.4, (bx, by + 4, 2), 74, 36, 64),
                 (2.95, (bx + 4.4, by + 6.0, 2.4), 86, 12, 11)], lens=24)
    A["FC"] = (fc, (0, 0, 2.4))
    _ = info


def o02(n, A):
    """Driver cuma bawa pulang Rp11.040, padahal potongan 'katanya' 8%: driver jaket hijau di atas motor menatap HP
    Android; layar aplikasi raksasa melayang di sampingnya; papan '8%?'. Kamera orbit dari kanan ke depan."""
    sid = "O02"
    kota(n)
    bx, by = OJ.BASE_C
    x, y = bx + 2.0, by + 6.8
    R.motor("mt", (x, y, G0), math.radians(90), "bk_blk", .85)
    dr = OJ.ojol_driver("dr", (x + 1.0, y + .6, G0), math.pi + .25, None, phone=True)
    ap = P.photo("app", "app_driver", 5.2, (x - 1.7, y + .9, 1.4), math.pi - .25, em=.9, border=.06)
    pop_in(ap, fr(sid, 3.0), 1.0, 9)
    s8, s8f = sign("s8", "8%?", (x + .9, y + 1.6, 5.3), .7, "n_pink", 8.0, rot_z=math.pi)
    pop_pair((s8, s8f), fr(sid, 7.6))
    camera(sid, [(2.95, (x - .2, y + .6, 2.8), 48, 10, 10.5), (5.5, (x - .4, y + .6, 3.4), 72, 9, 11.5),
                 (8.75, (x - .4, y + .6, 3.6), 96, 8, 12.5)], lens=24)
    A["APP"] = (ap, (0, 0, 5.6))
    A["DR"] = (dr["body"], (0, 0, 2.6))


def o03(n, A):
    """GoTo, induk Gojek: kamera dari boulevard naik menyusuri menara GoTo sampai logo goto di mahkota menyala."""
    sid = "O03"
    info = kota(n)
    cx, cy = OJ.GOTO_C
    camera(sid, [(8.75, (cx, cy - 14, 6), -120, 6, 40), (10.6, (cx, cy - 12, 30), -100, 8, 54),
                 (12.95, (cx, cy - 10, 58), -90, 6, 46)], lens=24)
    A["LOGO"] = ((cx, cy - 9, G0 + 66.5))
    _ = info


def o04(n, A):
    """BOM: GoTo cetak untung Rp441 miliar cuma dalam 3 bulan: slide resmi 'Third Consecutive Quarter of Net
    Profit' di layar raksasa, tumpukan uang merah naik di depannya, sampul laporan keuangan interim (dilaporkan ke
    BEI) di kiri depan, berita detikFinance di kanan depan. Semua dalam lebar frame 9:16."""
    sid = "O04"
    neon(rig_c=(0, 0, 4), rig_s=1.6, fade=(14, 60))
    sl = Q.tv("sl", "sl_profit", 8.0, (0, 3.0, 0), em=1.1, rot_z=0.0)
    pop_in(sl["root"], fr(sid, 12.95), 1.0, 8)
    m, h = R.money_stack("mn", 9, (0, -1.2, 0), "money_red", 4, 3, .75)
    key(m, "scale", 1, (1, 1, .001))
    key(m, "scale", fr(sid, 14.1), (1, 1, .001))
    anim(m, "scale", fr(sid, 14.1), fr(sid, 14.9), (1, 1, .001), (1, 1, 1), "out")
    lk = P.photo("lk", "lk_cover", 3.6, (-2.7, -3.0, .15), .3, em=1.0, border=.06)
    pop_in(lk, fr(sid, 15.8), 1.0, 9)
    ad = phone("ad", "art_detik441", 4.3, (2.75, -2.9, .1), -.3, sid, 16.4, n, .3)
    camera(sid, [(12.95, (0, 0, 4.6), -72, 6, 17), (15.2, (0, -.5, 3.8), -88, 8, 15.5),
                 (18.6, (0, -1, 3.4), -102, 10, 14.5)], lens=24)
    A["LK"] = (lk, (0, 0, 3.9))
    A["AD"] = (ad["root"], (0, 0, 4.6))
    _ = h


def o05(n, A):
    """Kedengarannya uang driver pindah ke kantong perusahaan... tapi nggak sesederhana itu: koin melayang dari
    pangkalan ojol menuju menara GoTo, lalu tanda tanya besar; kamera tinggi menyapu dari pangkalan ke menara."""
    sid = "O05"
    info = kota(n)
    bx, by = OJ.BASE_C
    cx, cy = OJ.GOTO_C
    coin_arc("ca", sid, 19.4, 26, (bx, by, 3.0), (cx, cy - 10, 30.0), .05, 1.4, 22.0, 5, 40)
    qm = V.qmark("qm", (cx - 16, cy - 18, 30.0), 4.0, "n_gold", 7.0)
    pop_in(qm, fr(sid, 21.6), 4.0, 10)
    SV.spin(qm, fr(sid, 21.6), n_all(n), 40)
    camera(sid, [(18.6, (bx + 4, by + 4, 6), -132, 30, 48), (20.6, (8, 10, 18), -112, 30, 85),
                 (23.6, (cx - 8, cy - 14, 30), -96, 22, 92)], lens=24)
    _ = info


# ================================================================== KATA GOJEK
def o06(n, A):
    """Driver GoRide sekarang dapat 92% dari tarif: diagram lingkaran neon 92/8 (irisan 8% lepas), papan DRIVER 92%
    di atas, APLIKASI 8% di samping irisan, driver bersorak di kiri depan, berita JawaPos di kanan depan."""
    sid = "O06"
    neon(rig_c=(0, 0, 3.5), rig_s=1.5)
    root = bpy.data.objects.new("pie_root", None)
    lp._link(root)
    root.location = (0, 1.0, 5.0)
    root.rotation_euler = (math.radians(90), 0, 0)
    for sl in V.pie("pie", [("n_green", .92), ("n_pink", .08)], 3.2, .9, (0, 0, 0), 64, 2.2):
        sl.parent = root
        if sl.name.endswith("_1"):
            mx, my = sl["mid"]
            anim(sl, "location", fr(sid, 26.4), fr(sid, 26.9), (0, 0, 0), (mx * .9, my * .9, 0), "out")
    pop_in(root, fr(sid, 23.65), 1.0, 10)
    s1, s1f = sign("d92", "DRIVER 92%", (-.4, -.6, 10.3), .6, "n_green", 8.0)
    s2, s2f = sign("a8", "APLIKASI 8%", (2.3, -.8, 8.75), .38, "n_pink", 7.0)
    pop_pair((s1, s1f), fr(sid, 25.81))
    pop_pair((s2, s2f), fr(sid, 26.4))
    dr = OJ.ojol_driver("dr", (-2.9, -2.4, 0), .25, "cheer")
    pop_in(dr["body"], fr(sid, 23.8), L.CH_S, 9)
    aj = phone("aj", "art_jawapos8", 4.4, (2.9, -2.6, .1), -.3, sid, 24.4, n, .3)
    camera(sid, [(23.6, (0, 0, 5.9), -112, 8, 16.5), (26.0, (0, 0, 6.0), -94, 8, 16), (28.25, (.2, 0, 6.0), -80, 9, 16)],
           lens=24)
    A["AJ"] = (aj["root"], (0, 0, 4.7))


def o07(n, A):
    """Harga penumpang tidak dinaikkan, insentif driver malah diperluas: label harga Rp15.500 'TARIF TETAP' dikunci
    gembok emas (kiri), kotak hadiah 'INSENTIF +' memuntahkan koin (kanan), berita Katadata di tengah belakang."""
    sid = "O07"
    neon(rig_c=(0, 0, 3.5), rig_s=1.5)
    import world_gta as GT
    ak = phone("ak", "art_insentif", 6.6, (0, 2.4, .1), 0.0, sid, 28.3, n, .3)
    tg, tgf = sign("tg", "Rp15.500", (-2.0, -1.0, 4.4), .55, "n_cyan", 8.0)
    pop_pair((tg, tgf), fr(sid, 28.33))
    tt, ttf = sign("tt", "TARIF TETAP", (-2.0, -1.0, 6.0), .4, "n_white", 6.0)
    pop_pair((tt, ttf), fr(sid, 28.9))
    lk = GT.padlock("lock", (-2.0, -1.3, 2.0), .8, "n_gold", 4.0)
    pop_in(lk, fr(sid, 29.2), 1.0, 9)
    gb = W.MB("gift")
    gb.box(-1.0, -1.0, 0, 1.0, 1.0, 1.7, "n_green")
    gb.box(-1.12, -1.12, 1.7, 1.12, 1.12, 2.05, "n_gold")
    gb.box(-.15, -1.15, 0, .15, 1.15, 2.06, "n_gold")
    go = gb.build((2.2, -1.2, 0))
    V.glow(go, {"n_green": 1.4, "n_gold": 4.0})
    pop_in(go, fr(sid, 30.3), 1.0, 9)
    ins, insf = sign("ins", "INSENTIF +", (2.2, -1.6, 3.4), .42, "n_gold", 8.0)
    pop_pair((ins, insf), fr(sid, 30.53))
    coin_arc("cg", sid, 30.9, 12, (2.2, -1.2, 2.2), (2.2, -2.4, 6.4), .06, .55, 1.5, 9, 16)
    camera(sid, [(28.25, (0, 0, 4.0), -70, 10, 15), (30.4, (.2, -.4, 3.8), -88, 8, 14), (32.6, (.4, -.6, 3.6), -104, 9, 14)],
           lens=24)
    A["AK"] = (ak["root"], (0, 0, 7.0))


def o08(n, A):
    """Gojek ngaku untung ojek & antar makanan cuma tumbuh 3%: deret kuliner — driver jaket hijau menunggu
    pesanan dengan kotak makanan, ojol keluar-masuk; papan neon +3% melayang di atas jalan. Kamera menyamping."""
    sid = "O08"
    kota(n)
    x0, x1, y0, y1 = OJ.FOOD
    yc = (y0 + y1) / 2 + 1.0                     # sumbu jalan kuliner
    s3, s3f = sign("p3", "+3%", (x0 + 34, yc, 6.4), 1.2, "n_green", 8.0, rot_z=-math.pi / 2)
    pop_pair((s3, s3f), fr(sid, 35.85))
    for i in range(4):
        rd = OJ.ojol_rider(f"fr{i}", (0, 0, G0), 0.0, .82)
        y = yc + (-1.8 if i % 2 else 1.8)
        anim(rd, "location", 1, n_all(n), (x0 - 4 + 5 * i, y, G0), (x0 + 30 + 5 * i, y, G0), "lin")
    # kamera menyusuri jalan kuliner (dari ujung barat), warung kiri-kanan, papan +3% di ujung jalan
    camera(sid, [(32.6, (x0 + 10, yc, 2.2), 172, 12, 12), (34.6, (x0 + 18, yc, 2.8), 180, 14, 13),
                 (36.7, (x0 + 28, yc, 4.4), 188, 12, 14)], lens=24)


def o09(n, A):
    """Potongan yang masih terasa besar datang dari biaya aplikasi & asuransi yang dihitung sebelum komisi:
    HP Android raksasa dengan rincian pendapatan (kiri), tiga papan potongan bertumpuk (kanan), papan 'DIHITUNG
    SEBELUM KOMISI' di atas, berita detikFinance kanan bawah."""
    sid = "O09"
    neon(rig_c=(0, 0, 4), rig_s=1.6)
    ph = phone("ph", "app_driver", 9.0, (-1.7, 1.2, .1), .1, sid, 36.75, n, .2, 39.0)
    for i, (lab, t, col) in enumerate((("APLIKASI -Rp2.500", 39.81, "n_pink"), ("ASURANSI -Rp1.000", 40.79, "n_pink"),
                                       ("KOMISI 8%", 42.59, "n_gold"))):
        s, sf = sign(f"c{i}", lab, (2.1, -.8, 8.5 - i * 1.4), .36, col, 8.0)
        pop_pair((s, sf), fr(sid, t))
    st, stf = sign("seb", "DIHITUNG SEBELUM KOMISI", (.4, -1.4, 10.5), .32, "n_cyan", 8.0)
    pop_pair((st, stf), fr(sid, 42.17))
    ah = phone("ah", "art_hitung", 4.4, (2.7, -1.4, .1), -.25, sid, 37.4, n, .3)
    camera(sid, [(36.7, (.4, 0, 6.6), -74, 12, 17.5), (39.6, (.6, 0, 6.8), -88, 8, 17), (43.6, (.6, 0, 6.9), -98, 8, 17.5)],
           lens=24)
    A["PH"] = (ph["root"], (0, 0, 9.6))
    A["AH"] = (ah["root"], (0, 0, 4.8))


def o10(n, A):
    """Kalau ojek cuma tumbuh 3%, untung ratusan miliar datang dari tempat lain — ada di HP kamu: dari pangkalan,
    kamera naik; HP Android raksasa (dompet digital) bangkit dari tengah perempatan dengan logo GoPay."""
    sid = "O10"
    kota(n)
    bx, by = OJ.BASE_C
    gx, gy = -10.0, -1.0
    gp = F.article_phone("gp", "app_wallet", 26.0, (gx + 9, gy + 2, G0), math.pi)
    key(gp["root"], "location", 1, (gx + 9, gy + 2, G0 - 30))
    key(gp["root"], "location", fr(sid, 48.6), (gx + 9, gy + 2, G0 - 30))
    anim(gp["root"], "location", fr(sid, 48.6), fr(sid, 50.4), (gx + 9, gy + 2, G0 - 30), (gx + 9, gy + 2, G0 + 4.0), "out")  # melayang di atas lalu lintas
    lg = OJ._img_plane("gpl", "gopay_card", 11.0, (gx + 9, gy + 3.3, G0 + 24.5), math.pi, 1.4)
    pop_in(lg, fr(sid, 50.28), 1.0, 9)
    camera(sid, [(43.6, (bx, by + 2, 2.6), 70, 12, 16), (47.0, (bx + 6, by, 10), 86, 20, 40),
                 (51.2, (gx + 9, gy + 2, 17), 90, 12, 48)], lens=24)
    A["GP"] = (lg, (0, 0, 3.4))


# ================================================================== GoPay
def o11(n, A):
    """GoPay (fintech) Rp550 miliar — lebih besar dari seluruh ojek & antar makanan (Rp347 miliar): dua pilar
    neon naik (biru vs hijau) dengan logo; slide resmi Fintech di belakang; berita Katadata kanan depan."""
    sid = "O11"
    neon(rig_c=(0, 0, 4), rig_s=1.6, fade=(14, 60))
    p1 = V.pillar("pg", 7.2, 2.2, 2.2, "n_cyan", 1.4, 6.0, (1.6, 0, 0))
    p2 = V.pillar("po", 4.55, 2.2, 2.2, "n_green", 1.4, 6.0, (-1.6, 0, 0))
    for p, t in ((p2, 51.5), (p1, 53.9)):
        key(p, "scale", 1, (1, 1, .001))
        key(p, "scale", fr(sid, t), (1, 1, .001))
        anim(p, "scale", fr(sid, t), fr(sid, t + .8), (1, 1, .001), (1, 1, 1), "out")
    l1 = OJ._img_plane("l1", "gopay_card", 2.6, (1.6, -1.2, 8.0), 0.0, 1.4)
    l2 = OJ._img_plane("l2", "gojek", 2.8, (-1.6, -1.2, 5.3), 0.0, 2.0)
    pop_in(l1, fr(sid, 54.0), 1.0, 8)
    pop_in(l2, fr(sid, 51.6), 1.0, 8)
    v1, v1f = sign("v1", "Rp550 M", (1.6, -1.3, 9.6), .48, "n_cyan", 8.0)
    v2, v2f = sign("v2", "Rp347 M", (-1.6, -1.3, 6.8), .48, "n_green", 8.0)
    pop_pair((v1, v1f), fr(sid, 54.4))
    pop_pair((v2, v2f), fr(sid, 56.3))
    sl = P.photo("sl", "sl_fintech", 5.2, (0, 4.6, 2.4), 0.0, em=1.0, border=.05)
    pop_in(sl, fr(sid, 52.6), 1.0, 9)
    ag = phone("ag", "art_gopay", 4.2, (3.0, -2.6, .1), -.3, sid, 55.6, n, .3)
    camera(sid, [(51.2, (0, 0, 5.6), -108, 8, 17), (54.6, (0, 0, 6.2), -92, 6, 17), (58.45, (.3, 0, 6.2), -78, 8, 17.5)],
           lens=24)
    A["SL"] = (sl, (0, 0, 5.6))
    A["AG"] = (ag["root"], (0, 0, 4.6))


def o12(n, A):
    """Pinjaman naik: panah neon melesat naik + slide resmi 'Loan Book Grows 51% YoY to IDR 12 Trillion'."""
    sid = "O12"
    neon(rig_c=(0, 0, 4), rig_s=1.6)
    sl = Q.tv("sl", "sl_loan", 10.0, (0, 3.0, 0), em=1.1, rot_z=0.0)
    pop_in(sl["root"], fr(sid, 58.5), 1.0, 8)
    ar = W.MB("arrow")
    ar.box(-.3, -.3, 0, .3, .3, 6.0, "n_green")
    ar.poly([(-1.0, 0, 6.0), (1.0, 0, 6.0), (0, 0, 7.8)], [(0, 1, 2)], "n_green")
    aro = ar.build((3.5, -1.2, 0))
    V.glow(aro, {"n_green": 7.0})
    key(aro, "scale", 1, (1, 1, .001))
    key(aro, "scale", fr(sid, 59.6), (1, 1, .001))
    anim(aro, "scale", fr(sid, 59.6), fr(sid, 60.3), (1, 1, .001), (1, 1, 1), "out")
    pj, pjf = sign("pj", "PINJAMAN", (2.4, -1.4, 9.4), .45, "n_green", 8.0)
    pop_pair((pj, pjf), fr(sid, 59.31))
    lr = P.photo("lr", "lk_rev", 3.0, (-1.2, -3.2, .3), .12, em=1.0, border=.05)
    pop_in(lr, fr(sid, 59.75), 1.0, 9)
    camera(sid, [(58.45, (1, 0, 5.6), -64, 6, 17), (61.45, (1.2, -.6, 5.6), -94, 8, 17.5)], lens=24)
    A["LR"] = (lr, (0, 0, 3.6))


# ================================================================== RESOLUSI + CTA
def o13(n, A):
    """Aplikasi ojek = pintu masuk, uangnya di dompet digital: HP raksasa berdiri seperti gerbang di boulevard;
    ojol jaket hijau melaju menembus layar; koin mengalir masuk ke dompet bergambar logo GoPay."""
    sid = "O13"
    kota(n)
    gx, gy = -40.0, 1.0
    gt = W.MB("gate")
    for xx in (gx - 6.0, gx + 6.0):
        gt.box(xx - .7, gy - .6, G0, xx + .7, gy + .6, G0 + 12, "phone_blk")
    gt.box(gx - 6.7, gy - .6, G0 + 12, gx + 6.7, gy + .6, G0 + 13.4, "phone_blk")
    gt.box(gx - 5.3, gy - .25, G0 + 11.2, gx + 5.3, gy + .25, G0 + 12.0, "n_green")
    go = gt.build()
    V.glow(go, {"n_green": 5.0})
    pop_in(go, fr(sid, 61.5), 1.0, 9)
    pm, pmf = sign("pm", "PINTU MASUK", (gx, gy - .8, 14.6), .85, "n_green", 8.0)
    pop_pair((pm, pmf), fr(sid, 63.99))
    for i in range(5):
        rd = OJ.ojol_rider(f"gr{i}", (0, 0, G0), 0.0, .82)
        f0 = fr(sid, 61.6 + .55 * i)
        lane = gy + (-1.6 if i % 2 else 1.6)
        anim(rd, "location", 1, n_all(n), (gx - 30 + 4 * i, lane, G0), (gx + 34 + 4 * i, lane, G0), "lin")
        _ = f0
    wl = F.article_phone("wl", "app_wallet", 9.0, (gx + 16, gy + 9, G0), -.35)
    pop_in(wl["root"], fr(sid, 65.75), 1.0, 9)
    coin_arc("cw", sid, 64.9, 16, (gx, gy, 6.0), (gx + 16, gy + 8, 5.0), .07, .8, 4.0, 13, 20)
    camera(sid, [(61.45, (gx - 6, gy, 7), -118, 10, 34), (64.0, (gx, gy, 8), -96, 12, 30),
                 (67.2, (gx + 2, gy + 2, 9), -88, 16, 25)], lens=24)


def o14(n, A):
    """Driver: tulis pendapatanmu sejak Juli naik, sama, atau turun. Pangkalan ojol — belasan driver jaket hijau;
    tiga papan neon NAIK / SAMA / TURUN muncul tepat di kata; kamera rendah orbit."""
    sid = "O14"
    kota(n)
    bx, by = OJ.BASE_C
    for i, (lab, t, col, dx) in enumerate((("NAIK", 70.16, "n_green", 2.4), ("SAMA", 70.66, "n_gold", 0.0),
                                           ("TURUN", 71.31, "n_pink", -2.4))):
        s, sf = sign(f"v{i}", lab, (bx + dx, by + 3.6, 7.5 - 1.15 * i), .75, col, 8.0, rot_z=math.pi)
        pop_pair((s, sf), fr(sid, t))
    camera(sid, [(67.2, (bx, by, 2.4), 60, 8, 15), (69.4, (bx, by + .5, 3.4), 84, 10, 16.5),
                 (71.7, (bx, by + 1, 4.6), 100, 10, 18.5)], lens=24)


def o15(n, A):
    """Penumpang: tag teman yang narik ojol, biar tahu ke mana uang ini mengalir. Kamera naik mundur dari jalan
    penuh ojol sampai seluruh kota metropolitan terlihat; menara GoTo menyala di kejauhan."""
    sid = "O15"
    kota(n)
    camera(sid, [(71.7, (-20, 0, 2.4), -96, 8, 22), (74.6, (-6, 4, 12), -100, 22, 90),
                 (79.2, (4, 10, 18), -104, 34, 260)], lens=24)


SCENES = {f"O{i:02d}": globals()[f"o{i:02d}"] for i in range(1, 16)}
K.SCENES = SCENES

if __name__ == "__main__":
    K.main()
