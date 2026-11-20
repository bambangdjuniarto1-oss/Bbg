"""Adegan dokumenter "Persib Bandung: juara 3x beruntun, rahasianya di luar lapangan" (Bedah Bisnis).
Visual: stadion GBLA malam (tribun penuh bobotoh, lampu sorot) + panggung gelap biru gaya dokumenter berisi foto
resmi (persib.co.id), artikel berita asli (lokal & luar negeri) di HP raksasa yang di-scroll, logo Persib &
4 kompetisi, pilar nilai pasar vs JDT, tiket aplikasi, tong sampah zero waste, kalender 365 vs stopwatch 90',
jersey + globe pembeli, papan bursa IPO, peta Google Maps Graha Persib -> GBLA, galeri foto pemain, mesin uang.

  PSB_TEX=DIR python3 render/scenes_psb.py -- --scene P01 --out DIR [--res 720x1280] [--samples 4] [--frames a-b]
"""
import math
import os
import random
import sys

import bpy  # noqa: F401

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowpoly as lp  # noqa: E402
import world_psb as P  # noqa: E402   (harus sebelum world_fom dipakai: set G.TEX)
import world_fom as F  # noqa: E402
import world_gta as G  # noqa: E402
import world_hotel as Ht  # noqa: E402
import world_nkh as N  # noqa: E402
import world_pst as PS  # noqa: E402
import world_vap as V  # noqa: E402
import scenes_nkh as K  # noqa: E402
import scenes_vap as SV  # noqa: E402
from scenes_nkh import FPS, TAIL, anim, arc_move, key, pop_in, pop_out  # noqa: E402

TIMELINE = [("P01", 0.00), ("P02", 3.85), ("P03", 7.05), ("P04", 12.89), ("P05", 20.31), ("P06", 24.65),
            ("P07", 31.37), ("P08", 33.52), ("P09", 36.64), ("P10", 40.81), ("P11", 46.53), ("P12", 53.31),
            ("P13", 60.52), ("P14", 64.00), ("P15", 68.31), ("P16", 74.25)]
END_T = 79.2
CITY = set()
STADIUM = {"P01", "P05", "P15"}
K.TIMELINE, K.END_T, K.CITY = TIMELINE, END_T, CITY


def _night(world_str=.3):
    """langit malam biru tua (dipakai semua adegan; menggantikan langit ungu panggung neon)."""
    sc = bpy.context.scene
    for ob in list(bpy.data.objects):
        if ob.type == "LIGHT" and ob.data.type == "SUN":
            ob.data.energy = .35
            ob.data.color = (.7, .8, 1.0)
            ob.rotation_euler = (math.radians(55), 0, math.radians(-30))
    bg = sc.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = lp.hex_rgba("#081226")
    bg.inputs["Strength"].default_value = world_str
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.cycles.glossy_bounces = 2
    sc.cycles.max_bounces = 4


V.setup_neon_light = lambda *a, **k: _night()


def fr(sid, t):
    return K.fr(sid, t)


def camera(sid, keys, **kw):
    return K.camera(sid, keys, **kw)


def n_all(n):
    return n + TAIL


def stage(**kw):
    kw.setdefault("grid", "psb_grid")
    kw.setdefault("em", 1.4)
    return K.neon(**kw)


def sign(name, body, loc, size=.8, key_="n_white", em=6.0, frame=True):
    return V.neon_sign(name, body, loc, size, key_, em, frame)


def pop_pair(pair, f, s=1.0):
    for ob in pair:
        if ob is not None:
            pop_in(ob, f, s)


def text3d(name, body, loc, size, key_="psb_white", em=3.0):
    return Ht.text(name, body, size, key_, depth=.08, loc=loc, emission=em)


def float_bob(ob, f0, f1, amp=.2, period=70, phase=0.0):
    z0 = ob.location.z
    for f in range(f0, f1 + 1, 2):
        key(ob, "location", f, (ob.location.x, ob.location.y, z0 + amp * math.sin(2 * math.pi * f / period + phase)))


def phone(name, img, h, loc, rot_z, sid, t_pop, n, span=.45, t_scroll=None):
    p = F.article_phone(name, img, h, loc, rot_z,
                        scroll=[(1, 0.0), (fr(sid, t_scroll or t_pop + .5), 0.0), (n_all(n), span)])
    pop_in(p["root"], fr(sid, t_pop), 1.0, 12)
    return p


def stadium(n, sid, jump=True, **kw):
    st = P.stadium(**kw)
    if jump and st.get("fans"):
        P.crowd_jump(st["fans"], 1, n_all(n), .14, 13)
    return st


# ================================================================== HOOK
def p01(n, A):
    """Di Indonesia ada klub yang juara 3x beruntun: terbang malam ke GBLA yang penuh bobotoh; 3 trofi naik di
    tengah lapangan tepat di 'three times'."""
    sid = "P01"
    st = stadium(n, sid)
    trs = []
    for i, (x, t) in enumerate(zip((-3.2, 0, 3.2), (2.64, 2.94, 3.19))):
        V.disc_ped(f"pd{i}", 1.3, "psb_blue2", (x, 0, .08), em=5.0, h=.35)
        tr = P.trophy(f"tr{i}", 1.15 if i == 1 else .95, (x, 0, .43))
        anim(tr, "location", fr(sid, t - .1), fr(sid, t + .45), (x, 0, -2.5), (x, 0, .43), "out")
        pop_in(tr, fr(sid, t - .1), 1.0, 12)
        trs.append(tr)
    P.flares("fl", 26, (-22, 9, 22, 15), 6.0, 3)
    camera(sid, [(0.0, (0, 0, 4), -128, 36, 105), (1.6, (0, 0, 3), -110, 26, 58),
                 (3.0, (0, 0, 2.0), -98, 14, 22), (3.85, (0, 0, 2.0), -94, 11, 16.5)], lens=24)
    A["TR"] = (trs[1], (0, 0, 3.2))
    A["GBLA"] = ((0, 26, 12))


def p02(n, A):
    """...padahal skuadnya bukan yang termahal di Asia Tenggara: foto resmi Bojan Hodak + 3 trofi, kartu pemain
    berjejer; label BUKAN TERMAHAL."""
    sid = "P02"
    stage(rig_c=(0, 0, 3), rig_s=1.3, fade=(10, 46))
    ph = P.photo("ph", "ph_trophies", 6.2, (0, 1.0, .3), 0.0)
    pop_in(ph, fr(sid, 3.95), 1.0, 12)
    rnd = random.Random(2)
    cards = []
    for i, pl in enumerate(P.PLAYERS[:8]):
        side = -1 if i < 4 else 1
        k = i % 4
        x = side * (7.2 + k * 2.6)
        c = P.photo(f"c{i}", pl, 4.2, (x, 2.0 + k * 1.3, .3), side * -.35, em=.85, border=.1)
        pop_in(c, fr(sid, 4.3 + .07 * i), 1.0, 10)
        cards.append(c)
    tg, tf = sign("tag", "BUKAN TERMAHAL", (0, -2.2, 8.4), .8, "n_red", 7.0)
    pop_pair((tg, tf), fr(sid, 4.92))
    camera(sid, [(3.85, (0, 1, 4.0), -96, 6, 15), (5.4, (0, 1, 4.4), -90, 8, 21), (7.05, (0, 1, 4.6), -84, 10, 25)],
           lens=26)
    A["PH"] = (ph, (0, 0, 7.2))


def p03(n, A):
    """Namanya Persib Bandung: logo resmi naik dari bawah di antara suar biru; artikel Kompas (EN) & Wikipedia
    (EN) tentang rekor 3 musim beruntun; tiga bintang emas."""
    sid = "P03"
    stage(rig_c=(0, 0, 3), rig_s=1.3, fade=(10, 50))
    V.disc_ped("ped", 3.0, "psb_blue2", (0, 0, 0), em=5.0, h=.5)
    lg = P.logo_card("logo", "lg_persib", 5.0, (0, 0, .5), plate=None, em=1.25)
    anim(lg, "location", fr(sid, 7.3), fr(sid, 8.0), (0, 0, -5.5), (0, 0, .5), "out")
    pop_in(lg, fr(sid, 7.3), 1.0, 10)
    rg = V.ring_obj("ring", (0, 0, .55), 3.6, .1, "psb_blue2", 8.0)
    pop_in(rg, fr(sid, 7.54), 1.6, 12)
    P.flares("fl", 18, (-9, 3, 9, 7), .2, 5)
    stars = []
    for i, x in enumerate((-1.3, 0, 1.3)):
        mb = P.W.MB(f"star{i}")
        pts = [(math.cos(math.pi / 2 + k * math.pi / 5) * (.55 if k % 2 == 0 else .22),
                math.sin(math.pi / 2 + k * math.pi / 5) * (.55 if k % 2 == 0 else .22)) for k in range(10)]
        mb.prism_y(pts, -.08, .08, "psb_gold")
        so = mb.build((x, -.3, 6.75 + (.25 if i == 1 else 0)))
        V.glow(so, {"psb_gold": 6.0})
        pop_in(so, fr(sid, 11.23 + .18 * i), 1.0, 10)
        stars.append(so)
    p1 = phone("pk", "art_kompas", 7.4, (-7.6, 2.4, .1), .42, sid, 8.6, n, .3)
    p2 = phone("pw", "art_wiki", 7.4, (7.6, 2.4, .1), -.42, sid, 9.0, n, .35)
    bk = P.photo("klok", "ph_klok", 4.6, (0, 7.5, .3), 0.0, em=.7)
    se, _ = sign("ss", "2023/24 · 2024/25 · 2025/26", (0, -2.6, .25), .42, "n_white", 4.0, False)
    pop_in(se, fr(sid, 11.6), 1.0)
    camera(sid, [(7.05, (0, 0, 3.0), -96, 2, 10), (8.3, (0, 0, 3.4), -92, 6, 14),
                 (10.0, (0, 1.5, 3.6), -88, 8, 22), (12.89, (0, 1.5, 3.8), -84, 9, 23)], lens=26)
    A["LOGO"] = (lg, (0, 0, 6.2))
    A["PK"] = (p1["root"], (0, 0, 7.8))
    A["PW"] = (p2["root"], (0, 0, 7.8))


def p04(n, A):
    """Nilai pasar skuad ±€9 juta — cuma sekitar separuh JDT (klub termahal Asia Tenggara): dua pilar tumbuh +
    garis separuh; artikel GoodStats (Transfermarkt)."""
    sid = "P04"
    stage(rig_c=(0, 0, 3), rig_s=1.5, fade=(12, 52))
    hp, hj = 4.6, 8.2
    pl = V.pillar("pP", hp, 3.0, 3.0, "psb_blue2", 1.6, 6.0, (-3.6, 0, 0))
    pj = V.pillar("pJ", hj, 3.0, 3.0, "n_red", 1.6, 6.0, (3.6, 0, 0))
    for ob, t0 in ((pl, 13.6), (pj, 18.4)):
        key(ob, "scale", 1, (1, 1, .001))
        anim(ob, "scale", fr(sid, t0), fr(sid, t0 + .9), (1, 1, .001), (1, 1, 1), "out")
    lgp = P.logo_card("lgp", "lg_persib", 2.2, (-3.6, -1.7, hp + .2), plate=None)
    lgj = P.logo_card("lgj", "lg_jdt", 2.2, (3.6, -1.7, hj + .2), plate=None)
    anim(lgp, "location", fr(sid, 13.6), fr(sid, 14.5), (-3.6, -1.7, .2), (-3.6, -1.7, hp + .2), "out")
    anim(lgj, "location", fr(sid, 18.4), fr(sid, 19.3), (3.6, -1.7, .2), (3.6, -1.7, hj + .2), "out")
    pop_in(lgp, fr(sid, 13.6), 1.0)
    pop_in(lgj, fr(sid, 18.4), 1.0)
    mb = P.W.MB("half")
    for k in range(9):
        x0 = -5.2 + k * 1.25
        mb.box(x0, -1.7, hj / 2 - .05, x0 + .7, -1.6, hj / 2 + .05, "n_white")
    hl = mb.build()
    V.glow(hl, {"n_white": 6.0})
    pop_in(hl, fr(sid, 16.16), 1.0, 10)
    ph = phone("gs", "art_goodstats", 7.6, (10.5, 3.2, .1), -.45, sid, 13.3, n, .25)
    camera(sid, [(12.89, (-3.6, 0, 2.8), -104, 10, 14), (14.8, (-2.0, 0, 3.6), -96, 12, 19),
                 (17.0, (0, 0, 4.4), -90, 12, 24), (20.31, (1.0, 0, 5.0), -86, 12, 27)], lens=26)
    A["PP"] = (lgp, (0, 0, 2.8))
    A["PJ"] = (lgj, (0, 0, 2.8))
    A["GS"] = (ph["root"], (0, 0, 8.0))


def p05(n, A):
    """Terus, rahasianya di mana? Jawabannya: di luar lapangan — kamera naik dari rumput, keluar melewati atap."""
    sid = "P05"
    st = stadium(n, sid)
    q = V.qmark("q", (0, 0, 4.2), 2.0, "psb_blue2", 7.0)
    pop_in(q, fr(sid, 21.57), 2.0)
    float_bob(q, fr(sid, 21.9), fr(sid, 23.0), .25, 40)
    pop_out(q, fr(sid, 23.0), 8)
    camera(sid, [(20.31, (0, 0, 2.2), -96, 3, 13), (21.8, (0, 0, 3.6), -94, 6, 15),
                 (23.2, (0, 4, 6.0), -96, 22, 36), (24.65, (0, 10, 8.0), -100, 34, 80)], lens=24)
    A["Q"] = (q, (0, 0, 2.6))


def p06(n, A):
    """Persib dikelola sebagai perusahaan, profesional & transparan (langka di sepak bola Indonesia): foto
    Graha Persib + store; papan PT; artikel Graha Persib & I.League (Deputy CEO)."""
    sid = "P06"
    stage(rig_c=(0, 0, 3), rig_s=1.6, fade=(12, 56))
    g = P.photo("graha", "ph_graha", 6.0, (-2.2, 1.2, .3), .12)
    pop_in(g, fr(sid, 24.8), 1.0, 12)
    s_ = P.photo("store", "ph_store", 4.4, (6.2, 3.5, .3), -.3, em=.85)
    pop_in(s_, fr(sid, 25.6), 1.0, 12)
    pt, pf = sign("pt", "PT PERSIB BANDUNG BERMARTABAT", (0, -2.0, 7.9), .32, "n_white", 6.0)
    pop_pair((pt, pf), fr(sid, 25.31))
    p1, f1 = sign("pro", "PROFESIONAL", (-5.0, -3.2, .8), .55, "n_cyan", 7.0)
    p2, f2 = sign("tra", "TRANSPARAN", (2.6, -3.2, .8), .55, "n_cyan", 7.0)
    pop_pair((p1, f1), fr(sid, 26.49))
    pop_pair((p2, f2), fr(sid, 27.18))
    a1 = phone("ag", "art_graha", 7.2, (-11.0, 3.6, .1), .45, sid, 25.9, n, .35)
    a2 = phone("ai", "art_ileague", 7.2, (11.6, 4.2, .1), -.45, sid, 28.6, n, .35)
    camera(sid, [(24.65, (-2, 1, 3.6), -100, 6, 15), (27.0, (0, 1, 3.8), -92, 8, 19),
                 (29.0, (3, 2, 4.0), -84, 9, 22), (31.37, (4, 2, 4.2), -80, 10, 24)], lens=26)
    A["GRAHA"] = (g, (0, 0, 6.9))
    A["AI"] = (a2["root"], (0, 0, 7.6))


def p07(n, A):
    """Tiket pertandingan dijual lewat aplikasi resmi: HP raksasa PERSIB App, tiket melesat keluar; artikel
    resmi 'tiket hanya di PERSIB App'."""
    sid = "P07"
    stage(rig_c=(0, 0, 3), rig_s=1.2, fade=(10, 46))
    app = phone("app", "app_persib", 8.0, (0, 0, .1), 0.0, sid, 31.45, n, .4)
    tks = []
    for i in range(3):
        tk = PS.ticket(f"tk{i}", "PERSIB APP", "psb_blue", "psb_navy", .8, "TIKET")
        p0 = (0, -.6, 4.0)
        p1 = (4.2 + i * .9, -1.6 - i * .4, 2.0 + i * 1.6)
        arc_move(tk, fr(sid, 31.9 + .18 * i), fr(sid, 32.6 + .18 * i), p0, p1, 1.2, "out")
        pop_in(tk, fr(sid, 31.9 + .18 * i), 1.0, 8)
        tk.rotation_euler.z = -.3
        tks.append(tk)
    ar = phone("at", "art_tiket", 6.8, (-6.6, 2.8, .1), .4, sid, 31.8, n, .3)
    camera(sid, [(31.37, (0, 0, 4.2), -96, 4, 13), (33.52, (1.2, 0, 4.2), -86, 6, 16)], lens=26)
    A["APP"] = (app["root"], (0, 0, 8.4))
    A["TK"] = (tks[1], (0, 0, 2.0))


def p08(n, A):
    """Sampah stadion dikelola zero waste to landfill: 3 tong terpilah, kantong jatuh masuk; foto relawan
    Jubelo di GBLA; artikel resmi 65,4 ton sampah 2025/26."""
    sid = "P08"
    stage(rig_c=(0, 0, 2.5), rig_s=1.4, fade=(10, 50))
    b = P.bins("bin", (0, 0, .02), 1.0)
    for i, ob in enumerate(b["bins"]):
        pop_in(ob, fr(sid, 33.6 + .1 * i), 1.0, 10)
        pop_in(b["labels"][i], fr(sid, 33.7 + .1 * i), 1.0, 10)
    for i, x in enumerate(b["x"]):
        bg = P.trash_bag(f"bag{i}", (x, 0, 8), .7, ("bag_lt", "bag_dk", "bag_dk")[i])
        arc_move(bg, fr(sid, 34.1 + .25 * i), fr(sid, 34.75 + .25 * i), (x - 1.5, -1.5, 7.5), (x, 0, 1.4), 1.0, "in")
        pop_in(bg, fr(sid, 34.1 + .25 * i), .7, 6)
        pop_out(bg, fr(sid, 34.8 + .25 * i), 5)
    zw, zf = sign("zw", "ZERO WASTE TO LANDFILL", (0, -1.6, 4.4), .5, "n_green", 7.0)
    pop_pair((zw, zf), fr(sid, 34.88))
    j1 = P.photo("j1", "ph_jubelo1", 4.0, (-7.4, 3.0, .3), .38, em=.85)
    j2 = P.photo("j2", "ph_jubelo2", 4.0, (7.4, 3.0, .3), -.38, em=.85)
    pop_in(j1, fr(sid, 33.8), 1.0, 12)
    pop_in(j2, fr(sid, 34.0), 1.0, 12)
    az = phone("az", "art_zw", 7.0, (0, 7.5, .1), 0.0, sid, 34.3, n, .3)
    camera(sid, [(33.52, (0, 0, 2.6), -98, 10, 14), (35.0, (0, 1, 3.2), -92, 12, 17),
                 (36.64, (0, 2, 3.6), -86, 13, 20)], lens=26)
    A["BIN"] = (b["bins"][1], (0, 0, 3.6))
    A["AZ"] = (az["root"], (0, 0, 7.4))


def p09(n, A):
    """Suporter dirawat 365 hari, bukan cuma 90 menit: kalender vs stopwatch; foto bobotoh (koreo, pawai juara,
    nobar) di belakang."""
    sid = "P09"
    stage(rig_c=(0, 0, 3), rig_s=1.5, fade=(12, 52))
    cal = N.calendar("cal", (-4.2, 0, .2), .62)
    for ob in [cal["frame"]] + list(cal["cells"].values()):
        pop_in(ob, fr(sid, 36.8), 1.0, 10)
    c3, c3f = sign("c365", "365 HARI", (-4.2, -1.4, 6.2), .62, "n_gold", 7.0)
    pop_pair((c3, c3f), fr(sid, 37.41))
    sw = P.stopwatch("sw", (4.2, 0, 3.0), 1.05)
    pop_in(sw["root"], fr(sid, 39.3), 1.0, 10)
    key(sw["hand"], "rotation_euler", fr(sid, 39.3), (0, 0, 0))
    key(sw["hand"], "rotation_euler", n_all(n), (0, math.radians(-540), 0))
    m9, m9f = sign("m90", "90 MENIT", (4.2, -1.4, 6.0), .6, "n_white", 6.0)
    pop_pair((m9, m9f), fr(sid, 39.9))
    for i, (im, x, y, rz) in enumerate((("ph_koreo", -9.5, 6.0, .3), ("ph_pawai", -3.2, 7.5, .08),
                                         ("ph_nobar", 3.2, 7.5, -.08), ("ph_bus", 9.5, 6.0, -.3))):
        ph = P.photo(f"b{i}", im, 3.8, (x, y, .3), rz, em=.8)
        pop_in(ph, fr(sid, 36.9 + .12 * i), 1.0, 12)
    camera(sid, [(36.64, (-4.2, 0, 3.4), -100, 8, 15), (38.6, (0, 1, 3.8), -92, 10, 23),
                 (40.81, (3.2, 1, 3.8), -86, 10, 21)], lens=26)
    A["CAL"] = (cal["frame"], (0, 0, 6.0))
    A["SW"] = (sw["root"], (0, 0, 2.9))


def p10(n, A):
    """Jersey-nya dibeli sampai Jepang, Taiwan, Hong Kong, bahkan Brasil: jersey 3D berputar + globe dengan pin
    negara pada kata VO; foto peluncuran jersey; artikel resmi jersey 2026/27."""
    sid = "P10"
    stage(rig_c=(0, 0, 3), rig_s=1.5, fade=(12, 52))
    js = P.jersey("js", (-5.4, 0, .6), 1.25)
    pop_in(js, fr(sid, 40.9), 1.0, 12)
    SV.spin(js, fr(sid, 40.9), n_all(n), 50)
    V.disc_ped("jp", 2.6, "psb_blue2", (-5.4, 0, 0), em=4.0, h=.5)
    gl = G.globe("gl", 3.4, (4.6, 0, 4.4), 1.8, 125.0)
    pop_in(gl["root"], fr(sid, 41.3), 1.0, 12)
    rz0 = gl["root"].rotation_euler.z
    key(gl["root"], "rotation_euler", fr(sid, 41.3), (0, 0, rz0))
    key(gl["root"], "rotation_euler", fr(sid, 44.7), (0, 0, rz0 + math.radians(8)))
    key(gl["root"], "rotation_euler", fr(sid, 45.5), (0, 0, rz0 + math.radians(173)))    # putar sampai Brasil
    for code, (la, lo), t in (("JP", (35.7, 139.7), 43.08), ("TW", (25.0, 121.5), 43.76),
                              ("HK", (22.3, 114.2), 44.51), ("BR", (-15.8, -47.9), 45.55)):
        pb = G.pin_beam("pin" + code, gl["root"], G.latlon(la, lo, 3.4), 3.4, 1.4, "n_gold", 7.0)
        pop_in(pb, fr(sid, t), 1.0, 9)
    a1 = P.photo("pj", "ph_jersey", 4.2, (-9.6, 5.2, .3), .3, em=.85)
    a2 = P.photo("pa", "ph_asia", 4.2, (0, 7.6, .3), 0.0, em=.85)
    pop_in(a1, fr(sid, 41.0), 1.0, 12)
    pop_in(a2, fr(sid, 41.2), 1.0, 12)
    aj = phone("aj", "art_jersey", 6.8, (11.4, 4.4, .1), -.45, sid, 41.6, n, .3)
    camera(sid, [(40.81, (-5, 0, 3.0), -98, 8, 14), (42.6, (0, 0, 4.0), -92, 8, 20),
                 (44.5, (3.6, 0, 4.4), -88, 6, 16), (46.53, (4.2, 0, 4.4), -86, 6, 15)], lens=26)
    A["JS"] = (js, (0, 0, 4.8))
    A["GL"] = ((4.6, -3.4, 8.2))


def p11(n, A):
    """Mimpi masuk bursa saham (IPO) — rencananya tertunda: papan bursa lilin naik, tanda IPO, cap TERTUNDA;
    artikel Katadata & detikFinance."""
    sid = "P11"
    stage(rig_c=(0, 0, 3.5), rig_s=1.6, fade=(12, 56))
    bd = P.stock_board("bd", (0, 1.5, .4), 15.0, 8.0, 14, 7)
    pop_in(bd["board"], fr(sid, 46.6), 1.0, 12)
    for i, c in enumerate(bd["candles"]):
        pop_in(c, fr(sid, 47.1 + .2 * i), 1.0, 8)
    ip, ipf = sign("ipo", "IPO", (0, -.6, 9.4), 1.3, "n_gold", 8.0)
    pop_pair((ip, ipf), fr(sid, 49.53))
    st, stf = sign("td", "TERTUNDA", (0, -1.2, 4.0), 1.0, "n_red", 9.0)
    pop_pair((st, stf), fr(sid, 52.63), 1.0)
    for ob in (st, stf):
        ob.rotation_euler.y = math.radians(-8)
    ak = phone("ak", "art_katadata", 7.2, (-11.2, 3.4, .1), .45, sid, 47.6, n, .35)
    ad = phone("ad", "art_detikipo", 7.2, (11.2, 3.4, .1), -.45, sid, 51.6, n, .35)
    camera(sid, [(46.53, (0, 1, 4.6), -96, 6, 22), (49.4, (0, 1, 5.2), -92, 8, 24),
                 (51.5, (2, 1, 4.6), -86, 8, 24), (53.31, (1, 1, 4.4), -88, 8, 21)], lens=26)
    A["BD"] = (bd["board"], (0, 0, 8.6))
    A["AK"] = (ak["root"], (0, 0, 7.6))
    A["AD"] = (ad["root"], (0, 0, 7.6))


ROUTE_UV = [(1085, 580), (1150, 578), (1205, 590), (1250, 665), (1275, 688), (1325, 690), (1322, 780),
            (1310, 860), (1305, 905), (1380, 885), (1450, 862), (1540, 855), (1650, 848), (1655, 885),
            (1720, 905), (1795, 932)]


def _uv(px, py):
    """koordinat layar tangkapan peta (2000x1500) -> uv peta terpotong (x 785.., y 60..)."""
    return (px - 785) / 1215.0, (py - 60) / 1440.0


def p12(n, A):
    """Kalau aset sudah dirapikan, valuasi ditaksir Rp1 triliun: peta Google Maps (kiriman) di lantai,
    pin Graha Persib & GBLA, rute menyala; tanda Rp1 TRILIUN; kartu info GBLA; artikel Investortrust."""
    sid = "P12"
    stage(rig_c=(0, 0, 3), rig_s=1.6, fade=(14, 60))
    mp = P.map_floor("map", "map_area", 20.0, (0, 0, .05), .95)
    u0, v0 = _uv(1085, 580)
    u1, v1 = _uv(1800, 955)
    pg = P.map_pin("pinG", mp["at"](u0, v0, .1), 1.6, "pin_blue", 3.0)
    pb = P.map_pin("pinB", mp["at"](u1, v1, .1), 1.9, "pin_red", 3.0)
    pop_in(pg, fr(sid, 53.7), 1.6, 10)
    pop_in(pb, fr(sid, 54.2), 1.9, 10)
    pts = [mp["at"](*_uv(x, y), .16) for x, y in ROUTE_UV]
    rt = P.route_curve("route", pts, "route", .14, 7.0)
    rt.data.bevel_factor_end = 0.0
    rt.data.keyframe_insert("bevel_factor_end", frame=1)
    rt.data.keyframe_insert("bevel_factor_end", frame=fr(sid, 54.4))
    rt.data.bevel_factor_end = 1.0
    rt.data.keyframe_insert("bevel_factor_end", frame=fr(sid, 55.7))
    cd = P.photo("card", "map_card", 7.4, (12.2, 4.0, .2), -.42, em=.95, border=.08)
    pop_in(cd, fr(sid, 55.2), 1.0, 12)
    rp, rpf = sign("rp", "Rp1 TRILIUN", (0, 2.0, 5.2), 1.3, "n_gold", 8.0)
    pop_pair((rp, rpf), fr(sid, 56.86))
    ai = phone("ai", "art_ipo", 7.0, (-12.0, 4.0, .1), .42, sid, 57.6, n, .3)
    camera(sid, [(53.31, (0, 0, 0), -92, 62, 21), (55.6, (1.5, 0, .5), -90, 52, 22),
                 (57.6, (0, 2.0, 3.0), -90, 26, 27), (60.52, (0, 2.0, 3.4), -88, 20, 30)], lens=24)
    A["PG"] = (pg, (0, 0, 3.2))
    A["PB"] = (pb, (0, 0, 3.8))
    A["RP"] = ((0, 2.0, 7.2))


def p13(n, A):
    """Ujian terberat: empat kompetisi sekaligus — BRI Super League, I.League Cup, ASEAN Club Championship
    (Shopee Cup), AFC Champions League Two; foto starting XI di Asia; artikel AFC & ESPN (luar negeri)."""
    sid = "P13"
    stage(rig_c=(0, 0, 3), rig_s=1.6, fade=(12, 56))
    xi = P.photo("xi", "ph_xi", 5.6, (0, 7.0, .3), 0.0, em=.8)
    pop_in(xi, fr(sid, 60.6), 1.0, 12)
    lgs = []
    for i, (im, t) in enumerate((("lg_bri", 62.18), ("lg_ileague_cup", 62.45), ("lg_shopee", 62.72),
                                 ("lg_acl2", 62.98))):
        x = (i - 1.5) * 4.4
        y = abs(i - 1.5) * 1.1
        V.disc_ped(f"pd{i}", 1.9, "psb_blue2", (x, y, 0), em=4.0, h=.4)
        lg = P.logo_card(f"lg{i}", im, 2.6, (x, y - .2, .45), -(i - 1.5) * .12, pad=.3)
        pop_in(lg, fr(sid, t), 1.0, 10)
        lgs.append(lg)
    af = phone("af", "art_afc", 6.8, (-12.0, 4.2, .1), .45, sid, 60.9, n, .3)
    es = phone("es", "art_espn", 6.8, (12.0, 4.2, .1), -.45, sid, 61.3, n, .3)
    camera(sid, [(60.52, (0, 4, 4.8), -94, 8, 22), (62.0, (0, 1.5, 3.4), -90, 8, 25),
                 (64.0, (0, 1.5, 3.4), -87, 9, 27)], lens=26)
    for i, lg in enumerate(lgs):
        A[f"L{i}"] = (lg, (0, 0, 4.2))
    A["AF"] = (af["root"], (0, 0, 7.2))
    A["ES"] = (es["root"], (0, 0, 7.2))


def p14(n, A):
    """Potensi 64 laga semusim dengan skuad cuma 29 pemain: galeri foto resmi pemain berjejer melengkung (kartu
    muncul beruntun), kamera menyapu kiri -> kanan; artikel CNN Indonesia & Radar Bandung."""
    sid = "P14"
    stage(rig_c=(0, 0, 3), rig_s=2.0, fade=(14, 64))
    cards = []
    pls = P.PLAYERS
    nn = len(pls)
    for i, pl in enumerate(pls):
        u = (i - (nn - 1) / 2) / ((nn - 1) / 2)
        row = i % 2
        x = u * 17.0
        y = 2.0 + (u * u) * 5.0 + row * 1.6
        z = .3 + row * 4.7
        c = P.photo(f"c{i}", pl, 4.0, (x, y, z), -u * .55, em=.85, border=.09)
        pop_in(c, fr(sid, 64.1 + .1 * i), 1.0, 9)
        cards.append(c)
    c1 = phone("cn", "art_cnn4", 6.6, (-20.0, 8.0, .1), .7, sid, 64.3, n, .3)
    c2 = phone("rb", "art_radar29", 6.6, (20.0, 8.0, .1), -.7, sid, 66.4, n, .3)
    camera(sid, [(64.0, (-11, 4, 5.0), -112, 6, 17), (65.6, (-4, 3, 5.0), -100, 6, 19),
                 (67.0, (5, 3, 5.0), -84, 6, 20), (68.31, (10, 4, 5.0), -74, 6, 20)], lens=24)
    A["C0"] = (cards[nn // 2], (0, 0, 9.6))
    A["RB"] = (c2["root"], (0, 0, 7.0))


def p15(n, A):
    """Di negaramu ada nggak klub yang dikelola serapi ini? — tribun GBLA bergemuruh (bobotoh melompat, suar
    biru); kamera mengitari pelan; kartu komentar di compose."""
    sid = "P15"
    st = stadium(n, sid)
    P.flares("fl", 40, (-24, -16, 24, -11), 6.0, 7)
    P.flares("fl2", 30, (-24, 11, 24, 16), 6.0, 8)
    lg = P.logo_card("logo", "lg_persib", 4.0, (0, 0, .2), plate=None, em=1.2)
    pop_in(lg, fr(sid, 68.5), 1.0, 12)
    camera(sid, [(68.31, (0, 0, 4), -150, 22, 20), (71.0, (0, 0, 4), -122, 18, 18),
                 (74.25, (0, 0, 3.5), -96, 14, 16.5)], lens=24)
    A["LOGO"] = (lg, (0, 0, 4.8))


def p16(n, A):
    """...dan follow buat part 2: mesin uang Persib — mesin raksasa berlogo Persib, roda gigi berputar, koin
    keluar; tanda PART 2."""
    sid = "P16"
    stage(rig_c=(0, 0, 3.5), rig_s=1.5, fade=(12, 52))
    mm = P.money_machine("mm", (0, 1.5, 0))
    pop_in(mm["body"], fr(sid, 74.35), 1.0, 12)
    pop_in(mm["logo"], fr(sid, 74.5), 1.0, 12)
    for i, g in enumerate(mm["gears"]):
        pop_in(g, fr(sid, 74.6 + .1 * i), 1.0, 10)
        key(g, "rotation_euler", fr(sid, 74.6), (0, 0, 0))
        key(g, "rotation_euler", n_all(n), (0, math.radians(360 * (1 if i % 2 else -1)), 0))
    rnd = random.Random(4)
    for i in range(22):
        f0 = fr(sid, 75.6 + .16 * i)
        c = P.coin(f"co{i}", (0, -1.0, 1.0), 1.0)
        p1 = (rnd.uniform(-4.5, 4.5), rnd.uniform(-5.0, -3.2), .1)
        arc_move(c, f0, f0 + 14, (rnd.uniform(-.8, .8), -3.0, 1.0), p1, 1.6, "lin")
        key(c, "scale", 1, (.001,) * 3)
        key(c, "scale", f0 - 1, (.001,) * 3)
        key(c, "scale", f0, (1, 1, 1))
        c.rotation_euler = (rnd.uniform(0, 3), rnd.uniform(0, 3), 0)
    p2, p2f = sign("p2", "PART 2", (0, -1.0, 9.2), 1.1, "n_gold", 8.0)
    pop_pair((p2, p2f), fr(sid, 74.81))
    camera(sid, [(74.25, (0, 0, 4.4), -96, 8, 26), (76.4, (0, 0, 4.4), -92, 8, 21),
                 (79.2, (0, 0, 4.2), -88, 8, 19)], lens=26)
    A["MM"] = (mm["body"], (0, -2.5, 7.6))


SCENES = {f"P{i:02d}": globals()[f"p{i:02d}"] for i in range(1, 17)}
K.SCENES = SCENES

if __name__ == "__main__":
    K.main()
