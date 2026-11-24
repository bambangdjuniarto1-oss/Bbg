"""Adegan "Bedah Bisnis: KPR naik Rp83 rb, BI Rate 6%" (alur 3K: Korban -> Kejutan -> Kail).
Konsep 2 dunia (seperti video Nikahan): kota diorama siang melayang di dunia neon (adegan cerita: perumahan,
keluarga, motor) + panggung neon (adegan angka: notifikasi tagihan, riwayat cicilan, grafik BI Rate & rupiah,
berita asli). Titik KEJUTAN diberi efek bom (lihat gen_kpr_cfg: flash/chroma/punch + SFX boom).

  PSB_TEX=DIR python3 render/scenes_kpr.py -- --scene K01 --out DIR [--res 864x1536] [--samples 4] [--frames a-b]
"""
import math
import os
import random
import sys

import bpy  # noqa: F401

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowpoly as lp  # noqa: E402
import world as W  # noqa: E402
import world_psb as P  # noqa: E402   (sebelum world_fom: set G.TEX)
import world_ps2 as Q  # noqa: E402
import world_fom as F  # noqa: E402
import world_hotel as H  # noqa: E402
import world_laundry as L  # noqa: E402
import world_nkh as N  # noqa: E402
import world_prk as R  # noqa: E402
import world_tahu as T  # noqa: E402
import world_vap as V  # noqa: E402
import scenes_nkh as K  # noqa: E402
import scenes_vap as SV  # noqa: E402
from scenes_nkh import TAIL, Z0, anim, arc_move, hide_until, key, pop_in, pop_out  # noqa: E402

from kpr_time import tm  # noqa: E402   (waktu di file ini = timeline VO v1 -> dipetakan ke VO v2)
import world_kpr as KC  # noqa: E402

TIMELINE_V1 = [("K01", 0.00), ("K02", 5.50), ("K03", 9.30), ("K04", 14.45), ("K05", 21.25), ("K06", 25.35),
               ("K07", 35.45), ("K08", 40.55), ("K09", 48.70), ("K10", 52.50), ("K11", 57.15), ("K12", 63.55),
               ("K13", 66.90), ("K14", 73.75)]
TIMELINE = [(sid, round(tm(t), 3)) for sid, t in TIMELINE_V1]
END_T = round(tm(82.6), 2)
CITY = {"K01", "K03", "K06", "K10", "K11", "K12", "K14"}
K.TIMELINE, K.END_T, K.CITY = TIMELINE, END_T, CITY

_coin0 = P.coin


def _coin(name, loc, s=1.0):
    ob = _coin0(name, loc, s)
    V.glow(ob, {"coin_g": .9})
    return ob


P.coin = _coin


def fr(sid, t):
    return K.fr(sid, tm(t))


def camera(sid, keys, **kw):
    return K.camera(sid, [(tm(k[0]),) + tuple(k[1:]) for k in keys], **kw)


G0 = KC.G0


def kota(n):
    """kota diorama besar (perumahan KPR, pusat kota + Bank Indonesia, jalan perbankan + papan kurs)."""
    return KC.city_kpr(n + TAIL)


def n_all(n):
    return n + TAIL


def city(n, **kw):
    kw.setdefault("people", False)
    kw.setdefault("focus", None)
    return SV.city(n + TAIL, **kw)


def neon(**kw):
    return K.neon(**kw)


def sign(name, body, loc, size=.8, key_="n_white", em=6.0, frame=True):
    return V.neon_sign(name, body, loc, size, key_, em, frame)


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
    pop_in(p["root"], fr(sid, t_pop), 1.0, 12)
    return p


def float_bob(ob, f0, f1, amp=.2, period=70, phase=0.0):
    z0 = ob.location.z
    for f in range(f0, f1 + 1, 2):
        key(ob, "location", f, (ob.location.x, ob.location.y, z0 + amp * math.sin(2 * math.pi * f / period + phase)))


def house(name, loc, seed=1, w=7.0, d=6.5, wall=None, roof=None):
    """rumah tapak (kompleks KPR) berdiri di plaza diorama."""
    mb, h = T.house(name, w, d, random.Random(seed), wall, roof)
    ob = mb.build((loc[0], loc[1], loc[2] - T.Z + Z0))
    return ob, h - T.Z


def person(name, look, loc, rot=0.0, pose=None):
    p = L.character(name, look, (loc[0], loc[1], Z0 if len(loc) < 3 else loc[2]), rot)
    if pose:
        L.pose(p, pose)
    return p


def coin_stream(prefix, sid, t, n, p0, p1, dt=.07, s=.7, arc=1.6, seed=1, dur=14):
    rnd = random.Random(seed)
    for i in range(n):
        f0 = fr(sid, t + dt * i)
        c = P.coin(f"{prefix}{i}", p0, s)
        q1 = (p1[0] + rnd.uniform(-.8, .8), p1[1] + rnd.uniform(-.6, .6), p1[2])
        arc_move(c, f0, f0 + dur, p0, q1, arc, "lin")
        key(c, "scale", 1, (.001,) * 3)
        key(c, "scale", f0 - 1, (.001,) * 3)
        key(c, "scale", f0, (s, s, s))
        key(c, "scale", f0 + dur - 2, (s, s, s))
        key(c, "scale", f0 + dur + 3, (.001,) * 3)
        c.rotation_euler = (rnd.uniform(0, 3), rnd.uniform(0, 3), 0)


def street_of_houses(seed=1, xs=(-15.5, -7.8, 0.0, 7.8, 15.5), y=-2.0):
    cols = [("wall_cream2", "roof_orange"), ("wall_peach", "roof_brown"), ("wall_beige", "roof_orange"),
            ("laundry_wall", "roof_brown"), ("wall_cream2", "roof_brown")]
    out = []
    for i, x in enumerate(xs):
        ob, h = house(f"rm{i}", (x, y, 0), seed + i, 7.0, 6.5, *cols[i % len(cols)])
        out.append((ob, h, x))
    return out


# ================================================================== KORBAN
def k01(n, A):
    """KORBAN: 83 ribu sebulan. Kota besar melayang -> menukik ke perumahan GRIYA ASRI -> satu rumah KPR; bapak &
    ibu di halaman, notifikasi tagihan melayang di atas rumah."""
    sid = "K01"
    info = kota(n)
    x, y = KC.HOUSE_XS[3], KC.ROWS_Y[0]
    bp = person("bapak", "bapak", (x - 1.6, y - 5.0, G0), 0.0, "think")
    ib = person("ibu", "hijab", (x + .4, y - 5.2, G0), -.3, "stand")
    nt = P.photo("nt", "notif", 2.0, (x - .6, y - 4.6, 4.3), 0.0, em=.9, border=.05)
    pop_in(nt, fr(sid, .6), 1.0, 12)
    float_bob(nt, fr(sid, .6), n_all(n), .15, 60)
    camera(sid, [(0.0, (-10, -8, 0), -100, 42, 250), (2.0, (-40, -16, 2), -96, 26, 70),
                 (5.50, (x - .6, y - 5.2, 3.4), -90, 19, 8.8)], lens=24)
    A["NT"] = (nt, (0, 0, 2.2))
    A["GATE"] = (info["estate"]["gate"])
    _ = (bp, ib)


def k02(n, A):
    """...kebanyakan santai, kalau dibagi per hari nggak sampai 3 ribu: kartu hitungan Rp83.000 ÷ 30 = Rp2.770,
    kalender 30 hari, bapak santai (angkat bahu); kamera dari kanan-depan."""
    sid = "K02"
    neon(rig_c=(0, 0, 3), rig_s=1.3)
    cd = P.photo("cd", "per_hari", 4.6, (0, 2.0, 2.6), 0.0, em=.75, border=.06)
    pop_in(cd, fr(sid, 5.6), 1.0, 12)
    cal = N.calendar("cal", (-3.9, .6, .2), .5)
    pop_in(cal["frame"], fr(sid, 7.72), 1.0, 10)
    bp = person("bapak", "bapak", (3.0, -1.4, 0), -.5, "shrug")
    pop_in(bp["body"], fr(sid, 5.6), L.CH_S, 10)
    for i in range(6):
        c = P.coin(f"c{i}", (3.2 + i * .5, -2.6, .55), .55)
        c.rotation_euler = (0, 0, -.4)
        pop_in(c, fr(sid, 8.85 + .04 * i), .55, 6)
    camera(sid, [(5.50, (0, 0, 3.4), -52, 8, 13), (7.4, (0, 0, 3.4), -72, 9, 13.5),
                 (9.30, (.3, 0, 3.4), -88, 9, 13)], lens=26)
    A["CD"] = (cd, (0, 0, 5.4))


def k03(n, A):
    """Tambahan itu muncul setelah BI naikkan suku bunga acuan jadi 6%: pusat kota, menara BANK INDONESIA; kamera
    dari boulevard mendongak lalu naik ke mahkota menara; papan neon BI RATE 6,00% menyala; layar berita di plaza."""
    sid = "K03"
    info = kota(n)
    cx, cy = KC.BI_C
    rt, rtf = sign("rate", "BI RATE 6,00%", (cx, cy - 7.5, G0 + 56.5), 2.8, "n_pink", 9.0)
    pop_pair((rt, rtf), fr(sid, 13.56), 1.0, 9)
    a1 = P.photo("ak", "art_kata", 9.0, (cx - 17, cy - 27, G0 + .2), .35, em=1.1, border=.1)
    a2 = P.photo("ai", "art_ibp", 9.0, (cx + 17, cy - 27, G0 + .2), -.35, em=1.1, border=.1)
    pop_in(a1, fr(sid, 12.4), 1.0, 12)
    pop_in(a2, fr(sid, 12.9), 1.0, 12)
    camera(sid, [(9.30, (cx, cy - 20, 9), -100, 4, 44), (11.8, (cx, cy - 14, 26), -94, 8, 52),
                 (14.45, (cx, cy - 6, 55), -90, 6, 40)], lens=24)
    A["AK"] = (a1, (0, 0, 9.4))
    A["AI"] = (a2, (0, 0, 9.4))
    _ = info


def k04(n, A):
    """Coba buka riwayat cicilan dari awal tahun -> ternyata kenaikannya DICICIL: HP raksasa aplikasi bank menggulir
    riwayat Jan-Nov (angka merah naik di Mei, Jun, Nov); BOM di 'ternyata' -> cap DICICIL! Kamera dari atas-kanan."""
    sid = "K04"
    neon(rig_c=(0, 0, 4), rig_s=1.5)
    ph = phone("ph", "riwayat", 10.0, (0, 1.5, .1), 0.0, sid, 14.6, n, .85, 16.1)
    lt, ltf = sign("dc", "DICICIL!", (.6, -1.4, 6.2), .85, "n_red", 9.0)
    pop_pair((lt, ltf), fr(sid, 19.65), 1.2, 7)
    for ob in (lt, ltf):
        if ob is not None:
            ob.rotation_euler.y = math.radians(-10)
    mg = V.magnifier("mg", (-3.2, -1.6, 4.8), 1.1)
    pop_in(mg, fr(sid, 16.1), 1.0, 10)
    arc_move(mg, fr(sid, 16.1), fr(sid, 19.4), (-3.4, -1.6, 7.6), (-1.6, -1.4, 4.4), .4, "inout")
    camera(sid, [(14.45, (0, 0, 5.2), -60, 38, 21), (17.0, (0, 0, 5.0), -78, 14, 17),
                 (21.25, (.6, 0, 4.8), -92, 8, 15)], lens=26)
    A["PH"] = (ph["root"], (0, 0, 10.6))


def k05(n, A):
    """Sedikit-sedikit sejak Mei, waktu bunga acuan masih 4,75%: tangga 11 pilar (Jan-Nov) naik bertahap +
    grafik BI Rate di layar belakang; kamera menyusuri tangga dari kiri-rendah ke kanan."""
    sid = "K05"
    neon(rig_c=(0, 0, 3), rig_s=1.6)
    bg = P.photo("cb", "chart_bi", 6.0, (0, 7.0, .3), 0.0, em=1.0, border=.06)
    pop_in(bg, fr(sid, 21.3), 1.0, 12)
    months = [("JAN", 4.75), ("FEB", 4.75), ("MAR", 4.75), ("APR", 4.75), ("MEI", 5.25), ("JUN", 5.75), ("JUL", 5.75),
              ("AGU", 5.75), ("SEP", 5.75), ("OKT", 5.75), ("NOV", 6.00)]
    for i, (m, v) in enumerate(months):
        x = (i - 5) * 1.35
        hgt = (v - 4.0) * 2.0
        col = "n_cyan" if v <= 4.75 else "n_pink"
        p = V.pillar(f"pl{i}", hgt, 1.05, 1.05, col, 1.4, 5.0, (x, 0, 0))
        t = 21.45 + .2 * i
        key(p, "scale", 1, (1, 1, .001))
        key(p, "scale", fr(sid, t) - 1, (1, 1, .001))
        anim(p, "scale", fr(sid, t), fr(sid, t + .45), (1, 1, .001), (1, 1, 1), "out")
        lb = Q.text3d(f"m{i}", m, (x, -.6, .25), .38, "psb_white", 3.5)
        pop_in(lb, fr(sid, t), 1.0, 6)
    s1, s1f = sign("s475", "4,75%", (-4.0, -.8, 2.3), .42, "n_cyan", 7.0)
    pop_pair((s1, s1f), fr(sid, 24.11))
    camera(sid, [(21.25, (-4.5, 0, 1.8), -120, 6, 12), (23.2, (-1, 0, 2.4), -100, 10, 14),
                 (25.35, (2.5, 0, 2.8), -78, 12, 15)], lens=24)


def k06(n, A):
    """KPR Rp500 jt: dulu Rp4,5 jt, sekarang hampir Rp4,9 jt -> Rp410 rb lebih tiap bulan. Rumah di deret kedua
    perumahan dengan papan KPR Rp500 JT, dua tumpukan uang di halaman, koin keluar dari pintu ke jalan."""
    sid = "K06"
    kota(n)
    x, y = KC.HOUSE_XS[2], KC.ROWS_Y[1]
    tg, tgf = sign("tag", "KPR Rp500 JT", (x, y - 4.0, 9.4), .75, "n_gold", 8.0)
    pop_pair((tg, tgf), fr(sid, 26.39))
    person("bapak", "bapak", (x - 3.4, y - 5.0, G0), .3, "think")
    person("ibu", "hijab", (x - 2.2, y - 5.3, G0), .1, "stand")
    m1, h1 = N.money("m1", 9, (x - .6, y - 5.6, G0), 2, 2, .62)
    m2, h2 = N.money("m2", 10, (x + 1.5, y - 5.6, G0), 2, 2, .62)
    for m, t in ((m1, 28.17), (m2, 29.89)):
        key(m, "scale", 1, (1, 1, .001))
        key(m, "scale", fr(sid, t) - 1, (1, 1, .001))
        anim(m, "scale", fr(sid, t), fr(sid, t + .5), (1, 1, .001), (1, 1, 1), "out")
    l1, l1f = sign("l1", "4,5 JT", (x - .6, y - 6.4, h1 + .9), .38, "n_cyan", 7.0)
    l2, l2f = sign("l2", "4,9 JT", (x + 1.5, y - 6.4, h2 + .9), .38, "n_pink", 7.0)
    pop_pair((l1, l1f), fr(sid, 28.17))
    pop_pair((l2, l2f), fr(sid, 29.89))
    coin_stream("cs", sid, 32.59, 16, (x, y - 3.4, 1.8), (x + 3.0, y - 9.5, G0 + .1), .1, .55, 2.0, 3)
    camera(sid, [(25.35, (x, y - 4, 4.0), -42, 34, 30), (29.0, (x, y - 5.5, 2.8), -66, 16, 11),
                 (35.45, (x + .4, y - 5.8, 2.6), -86, 11, 8.6)], lens=24)
    A["M2"] = (m2, (0, 0, 2.0))


def k07(n, A):
    """BOM: ditotal sampai lunas hampir Rp98 juta. Menara uang menjulang tinggi di panggung neon + kalender 20 tahun
    berputar; kamera rendah menatap ke atas lalu mundur."""
    sid = "K07"
    neon(rig_c=(0, 0, 5), rig_s=1.8, fade=(14, 60))
    V.disc_ped("ped", 3.2, "n_pink", (0, 0, 0), em=5.0, h=.4)
    tw, th = N.money("tw", 120, (0, 0, .4), 3, 3, .8)
    key(tw, "scale", 1, (1, 1, .001))
    key(tw, "scale", fr(sid, 35.6) - 1, (1, 1, .001))
    anim(tw, "scale", fr(sid, 35.6), fr(sid, 38.0), (1, 1, .001), (1, 1, .45), "inout")
    anim(tw, "scale", fr(sid, 38.0), fr(sid, 38.9), (1, 1, .45), (1, 1, 1), "out")
    rg = V.ring_obj("ring", (0, 0, .45), 3.6, .12, "n_pink", 8.0)
    pop_in(rg, fr(sid, 38.64), 1.6, 10)
    s20, s20f = sign("t20", "20 TAHUN", (-3.6, -1.0, 4.4), .55, "n_cyan", 7.0)
    pop_pair((s20, s20f), fr(sid, 36.99))
    cal = N.calendar("cal", (4.0, -.4, .2), .5)
    pop_in(cal["frame"], fr(sid, 36.34), 1.0, 10)
    camera(sid, [(35.45, (0, 0, 3.0), -98, 6, 14), (38.6, (0, 0, 6.5), -92, 3, 18),
                 (40.55, (0, 0, 8.0), -88, 6, 24)], lens=24)
    A["TW"] = (tw, (0, 0, th + .8))


# ================================================================== KAIL
def k08(n, A):
    """Setidaknya tabungan ikut naik? Deposito Rp100 jt cuma +Rp17 rb/bulan setelah pajak: timbangan neon, kiri
    tambahan cicilan +Rp83 rb (berat, turun), kanan tambahan bunga deposito +Rp17 rb; artikel Akurat."""
    sid = "K08"
    neon(rig_c=(0, 0, 3.5), rig_s=1.5)
    b = N.balance("bal", (0, 1.0, 0), 1.3, "n_cyan")
    pl, pr = b["pans"]
    for side, pan, nn in ((-1, pl, 9), (1, pr, 2)):       # kiri: tambahan cicilan (banyak), kanan: deposito (sedikit)
        for k in range(nn):
            c = P.coin(f"pc{side}{k}", (0, 0, 0), .55)
            c.parent = pan
            c.location = ((k % 3 - 1) * .5, 0, -2.75 + .17 * (k // 3) + .3)
            c.rotation_euler = (0, 0, k * .7)
            pop_in(c, fr(sid, (41.2 if side < 0 else 47.42) + .05 * k), .55, 6)
    f_a = fr(sid, 47.6)
    for f in range(1, n_all(n) + 1):
        if f <= f_a:
            deg = 0.0
        else:
            u = (f - f_a) / 30.0
            deg = -14.0 * (1 - math.exp(-3.2 * u) * math.cos(5.5 * u))
        N.balance_key(b, f, deg)
    s1, s1f = sign("kpr", "CICILAN +Rp83 RB", (-3.6, -.6, 8.4), .5, "n_pink", 7.0)
    s2, s2f = sign("dep", "DEPOSITO +Rp17 RB", (3.6, -.6, 7.0), .5, "n_cyan", 7.0)
    pop_pair((s1, s1f), fr(sid, 41.2))
    pop_pair((s2, s2f), fr(sid, 47.42))
    aa = phone("aa", "art_akurat", 5.8, (-9.4, 3.0, .1), .5, sid, 42.2, n, .3)
    camera(sid, [(40.55, (0, 0, 4.4), 20, 14, 23), (44.0, (-1.0, 0, 4.4), -40, 10, 23),
                 (48.70, (-1.0, 0, 4.4), -86, 8, 24)], lens=24)
    A["AA"] = (aa["root"], (0, 0, 6.2))


def k09(n, A):
    """Kata ekonom: bunga kredit cepat naiknya, lambat turunnya. Dua jalur: kiri lift neon melesat naik (KREDIT),
    kanan tangga panjang turun pelan; artikel Kontan (ekonom). Kamera top-down turun ke depan."""
    sid = "K09"
    neon(rig_c=(0, 0, 4), rig_s=1.6)
    sh = W.MB("shaft")
    sh.box(-4.6, .6, 0, -4.5, .7, 10.0, "n_cyan")
    sh.box(-2.5, .6, 0, -2.4, .7, 10.0, "n_cyan")
    so = sh.build()
    V.glow(so, {"n_cyan": 5.0})
    lift = V.block("lift", "n_pink", 1.6, (-3.5, 0, .2), 2.6, 7.0)
    key(lift, "location", 1, (-3.5, 0, .2))
    key(lift, "location", fr(sid, 50.79), (-3.5, 0, .2))
    anim(lift, "location", fr(sid, 50.79), fr(sid, 51.3), (-3.5, 0, .2), (-3.5, 0, 8.0), "out")
    st = W.MB("stairs")
    for k in range(10):
        st.box(1.4 + k * .75, -1.0, 0, 2.2 + k * .75, 1.0, 8.0 - k * .8, "vp_stair" if False else "n_cyan")
    sto = st.build()
    V.glow(sto, {"n_cyan": .8})
    ball = V.block("down", "n_cyan", .9, (1.8, 0, 8.0), 2.4, 6.0)
    for k in range(10):
        key(ball, "location", fr(sid, 51.72 + k * .35), (1.8 + k * .75, 0, 8.0 - k * .8 + .02))
    key(ball, "location", 1, (1.8, 0, 8.0))
    bk, bkf = sign("bk", "BUNGA KREDIT", (1.0, -1.0, 12.2), .6, "n_gold", 8.0)
    pop_pair((bk, bkf), fr(sid, 48.8))
    up, upf = sign("up", "CEPAT NAIK", (-3.5, -1.2, 10.4), .5, "n_pink", 7.0)
    dn, dnf = sign("dn", "LAMBAT TURUN", (5.4, -1.6, 9.0), .5, "n_cyan", 7.0)
    pop_pair((up, upf), fr(sid, 50.79))
    pop_pair((dn, dnf), fr(sid, 51.72))
    ae = phone("ae", "art_ekonom", 5.6, (-9.6, 3.0, .1), .5, sid, 49.3, n, .3)
    camera(sid, [(48.70, (0, 0, 4.0), -90, 70, 24), (50.6, (0, 0, 5.0), -96, 24, 24),
                 (52.50, (0, 0, 5.2), -86, 10, 23)], lens=24)
    A["AE"] = (ae["root"], (0, 0, 6.0))


def k10(n, A):
    """KPR bunga tetap atau cicilan motor: tenang, cicilan nggak berubah. Deret ketiga perumahan: rumah ber-papan
    hijau FIXED AMAN + motor di carport-nya ber-papan MOTOR AMAN; kamera orbit pelan dari kiri ke kanan."""
    sid = "K10"
    kota(n)
    x, y = KC.HOUSE_XS[6], KC.ROWS_Y[2]
    sf, sff = sign("fix", "FIXED AMAN", (x - .6, y - 4.0, 8.0), .8, "n_green", 8.0)
    pop_pair((sf, sff), fr(sid, 53.77))
    mt = R.motor("mt", (x + 3.7, y - 4.6, G0), math.radians(90), "bk_red", .95)
    pop_in(mt, fr(sid, 54.82), .95, 10)
    sm, smf = sign("mot", "MOTOR AMAN", (x + 3.7, y - 6.6, 3.4), .45, "n_green", 8.0)
    pop_pair((sm, smf), fr(sid, 54.82))
    person("p", "cowok", (x + 2.0, y - 6.0, G0), .2, "wave")
    camera(sid, [(52.50, (x + .6, y - 5, 4.4), -74, 15, 16.5), (54.8, (x + 1.2, y - 5, 4.2), -88, 14, 16),
                 (57.15, (x + 1.6, y - 5, 4.0), -102, 13, 15)], lens=24)


def k11(n, A):
    """Yang kena: floating, masa fixed mau habis, baru mau akad. Tiga rumah di deret kedua diberi papan merah +
    sirene tepat di tiap kata; kamera tinggi dari kiri menyapu ke kanan."""
    sid = "K11"
    kota(n)
    y = KC.ROWS_Y[1]
    for i, (lab, t, xi) in enumerate((("FLOATING", 58.84, 6), ("FIXED HABIS", 61.38, 7), ("BARU AKAD", 63.01, 8))):
        x = KC.HOUSE_XS[xi]
        sg, sgf = sign(f"lb{i}", lab, (x, y - 4.0, 10.4 + 1.6 * (i % 2)), 1.0, "n_red", 9.0)
        pop_pair((sg, sgf), fr(sid, t), 1.0, 8)
        sr, sli = V.siren(f"sr{i}", (x + 2.4, y - 4.2, 6.6), .8)
        pop_in(sr, fr(sid, t), .8, 8)
        V.flash_siren(sr, sli, fr(sid, t), n_all(n), 10)
    camera(sid, [(57.15, (-26, y - 4, 7.0), -120, 38, 32), (59.2, (-22, y - 4, 7.5), -108, 34, 30),
                 (61.6, (-14, y - 4, 7.5), -94, 32, 30), (63.55, (-7, y - 4, 7.5), -80, 30, 30)], lens=24)


def k12(n, A):
    """Yang bikin garuk kepala: semua kenaikan katanya buat jaga rupiah. Plaza jalan perbankan: bapak garuk kepala
    di depan papan kurs LED raksasa (menghadap boulevard); papan neon JAGA RUPIAH; kamera dari boulevard orbit."""
    sid = "K12"
    kota(n)
    kx, ky = KC.KURS_C
    bp = person("bapak", "bapak", (kx - 3.0, ky + 3.0, G0), math.pi - .25, "think")
    qm = V.qmark("qm", (kx - 2.9, ky + 3.1, 3.3), .6, "n_gold", 7.0)
    qm.rotation_euler.z = math.pi
    pop_in(qm, fr(sid, 64.52), .6, 8)
    float_bob(qm, fr(sid, 64.52), n_all(n), .12, 40)
    jr, jrf = sign("jr", "JAGA RUPIAH", (kx + 4.0, ky + 2.0, 4.2), .6, "n_cyan", 8.0)
    for ob in (jr, jrf):
        if ob is not None:
            ob.rotation_euler.z = math.pi
    pop_pair((jr, jrf), fr(sid, 66.41))
    camera(sid, [(63.55, (kx - 2, ky + 3, 2.4), 62, 6, 11), (65.4, (kx - 1, ky + 2, 5.0), 78, 8, 17),
                 (66.90, (kx, ky + 1, 8.5), 90, 8, 24)], lens=24)
    A["BP"] = (bp["body"], (0, 0, 2.7))


def k13(n, A):
    """BOM: padahal rupiah ditutup di rekor terlemah (Rp18.268/US$, 16 Nov): layar grafik rupiah, panah merah
    menjulang, cap REKOR TERLEMAH; berita Kontan & Afu. Kamera rendah dari kiri lalu dorong masuk."""
    sid = "K13"
    neon(rig_c=(0, 0, 4), rig_s=1.6, fade=(14, 60))
    tvo = Q.tv("tv", "chart_idr", 9.0, (0, 2.5, 0), em=1.3, rot_z=0.0)
    pop_in(tvo["root"], fr(sid, 67.0), 1.0, 12)
    ar = W.MB("arrow")
    ar.box(-.25, -.25, 0, .25, .25, 6.0, "n_red")
    ar.poly([(-.9, 0, 6.0), (.9, 0, 6.0), (0, 0, 7.6)], [(0, 1, 2)], "n_red")
    aro = ar.build((4.0, -1.2, 0))
    V.glow(aro, {"n_red": 7.0})
    key(aro, "scale", 1, (1, 1, .001))
    key(aro, "scale", fr(sid, 69.17) - 1, (1, 1, .001))
    anim(aro, "scale", fr(sid, 69.17), fr(sid, 69.8), (1, 1, .001), (1, 1, 1), "out")
    st, stf = sign("rek", "REKOR TERLEMAH", (0, -1.6, 1.2), .62, "n_red", 9.0)
    pop_pair((st, stf), fr(sid, 71.72), 1.15, 7)
    for ob in (st, stf):
        if ob is not None:
            ob.rotation_euler.y = math.radians(-8)
    a1 = phone("a1", "art_rupiah", 5.6, (-8.6, 1.0, .1), .5, sid, 68.0, n, .3)
    a2 = phone("a2", "art_afu", 5.6, (9.0, 1.4, .1), -.5, sid, 70.4, n, .3)
    camera(sid, [(66.90, (0, 1, 3.6), -128, 6, 19), (69.2, (0, 1, 3.4), -100, 6, 15.5),
                 (73.75, (0, 1, 3.6), -90, 4, 11.5)], lens=24)
    A["A1"] = (a1["root"], (0, 0, 6.0))
    A["A2"] = (a2["root"], (0, 0, 6.0))


# ================================================================== CTA
def k14(n, A):
    """CTA: KPR-mu pakai bunga apa? Tulis FIXED atau FLOATING. Perumahan GRIYA ASRI dari udara, dua papan neon
    raksasa FIXED & FLOATING melayang di atasnya; kamera naik mundur sampai seluruh kota terlihat."""
    sid = "K14"
    kota(n)
    f1, f1f = sign("fx", "FIXED", (-54, -34, 26), 4.2, "n_green", 9.0)
    f2, f2f = sign("fl", "FLOATING", (-22, -34, 26), 4.2, "n_pink", 9.0)
    pop_pair((f1, f1f), fr(sid, 76.94))
    pop_pair((f2, f2f), fr(sid, 77.57))
    camera(sid, [(73.75, (-40, -30, 6), -96, 18, 50), (77.0, (-40, -30, 14), -94, 22, 85),
                 (82.6, (-34, -24, 14), -92, 30, 150)], lens=24)


SCENES = {f"K{i:02d}": globals()[f"k{i:02d}"] for i in range(1, 15)}
K.SCENES = SCENES

if __name__ == "__main__":
    K.main()
