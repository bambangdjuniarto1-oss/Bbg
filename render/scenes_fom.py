"""Adegan "Bedah Bisnis: Cara brand vape bertahan di tengah fatwa haram" (FOOM) — alur 3K: Korban -> Kejutan -> Kail.
Visual: kota diorama Jakarta bernuansa pink sakura (billboard poster campaign FOOM x YB, menara FOOM, toko vape)
+ panggung neon (HP raksasa berisi artikel berita ASLI yang di-scroll, dokumen fatwa & palu, logo FOOM 3D,
galeri poster, lencana 21+). Kamera spline per-frame (scenes_nkh), lintasan menyusur/mengitari/menukik.

  FOM_TEX=DIR python3 render/scenes_fom.py -- --scene F01 --out DIR [--res 720x1280] [--samples 4] [--frames a-b]
"""
import math
import os
import random
import sys

import bpy  # noqa: F401  (harus sebelum lowpoly: bmesh)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowpoly as lp  # noqa: E402
import world as W  # noqa: E402
import world_fom as F  # noqa: E402
import world_gta as G  # noqa: E402
import world_laundry as L  # noqa: E402
import world_nkh as N  # noqa: E402
import world_prk as R  # noqa: E402
import world_vap as V  # noqa: E402
import scenes_nkh as K  # noqa: E402
import scenes_vap as SV  # noqa: E402
from scenes_nkh import FPS, TAIL, anim, arc_move, grow, hide_until, key, pop_in, pop_out  # noqa: E402

TIMELINE = [("F01", 0.00), ("F02", 3.27), ("F03", 6.30), ("F04", 12.47), ("F05", 18.68), ("F06", 20.55),
            ("F07", 27.93), ("F08", 30.68), ("F09", 34.64), ("F10", 40.32), ("F11", 43.67), ("F12", 46.05),
            ("F13", 53.18), ("F14", 57.62), ("F15", 60.62), ("F16", 66.43), ("F17", 72.61), ("F18", 78.72),
            ("F19", 82.16)]
END_T = 86.8
CITY = {"F01", "F05", "F08", "F16", "F17", "F18", "F19"}
K.TIMELINE, K.END_T, K.CITY = TIMELINE, END_T, CITY
Z0 = .24
TW_Y = 44 - 18                 # menara FOOM (y1 diorama - 18)


def fr(sid, t):
    return K.fr(sid, t)


def camera(sid, keys, **kw):
    return K.camera(sid, keys, **kw)


def neon(**kw):
    return K.neon(**kw)


def n_all(n):
    return n + TAIL


def city(n, **kw):
    return F.fom_city(n + TAIL, **kw)


def float_bob(ob, f0, f1, amp=.25, period=70, phase=0.0):
    z0 = ob.location.z
    for f in range(f0, f1 + 1, 2):
        key(ob, "location", f, (ob.location.x, ob.location.y, z0 + amp * math.sin(2 * math.pi * f / period + phase)))


def label3d(name, body, loc, size=.7, key_="n_white", em=3.0):
    return V.neon_sign(name, body, loc, size, key_, em)


def pop_pair(pair, f, s=1.0):
    for ob in pair:
        if ob is not None:
            pop_in(ob, f, s)


def xm(name, loc, f, s=1.2):
    x = V.xmark(name, loc, s, "x_red", 6.0)
    pop_in(x, f, s)
    return x


# ================================================================== KORBAN (hook)
def f01(n, A):
    """Penjual liquid di Jakarta ditolak perpanjang sewa: kamera menukik ke toko kecil; artikel asli melayang;
    cap DITOLAK; rolling door turun."""
    sid = "F01"
    c = city(n, store=False)
    st, door = F.shop_closed("shop", (0, 4, Z0))
    key(door, "location", 1, (0, 4, Z0 + 3.9))
    anim(door, "location", fr(sid, 2.3), fr(sid, 3.2), (0, 4, Z0 + 3.9), (0, 4, Z0), "in")
    own = L.character("own", "owner", (-1.4, -1.6, Z0), .2)
    L.pose(own, "stand", 1)
    L.pose(own, "think", fr(sid, 1.6))
    ll = L.character("land", "bapak", (1.6, -1.9, Z0), -.5, hold="tablet")
    L.pose(ll, "stand", 1)
    doc = F.document("doc", (1.2, -2.6, 4.2), .55, "SEWA TOKO", "Perpanjangan kontrak", "DITOLAK", 5)
    doc["root"].rotation_euler.z = -.25
    pop_in(doc["root"], fr(sid, 1.0), 1.0)
    st_ = doc["stamp"]
    st_.scale = (.001,) * 3
    pop_in(st_, fr(sid, 1.57), 1.0, 7)
    ph = F.article_phone("art", "art_sewa", 7.0, (-6.2, -3.5, Z0 + .3), .35,
                         scroll=[(1, 0.0), (fr(sid, 1.2), 0.0), (n_all(n), .22)])
    pop_in(ph["root"], fr(sid, .55), 1.0, 12)
    camera(sid, [(0.0, (0, 0, 2), -118, 50, 175), (1.1, (-1, -2, 3.5), -104, 26, 52),
                 (2.2, (-1, -2.5, 3.6), -96, 14, 24), (3.27, (-.5, -2.5, 3.4), -88, 10, 20)], lens=24)
    A["ART"] = (ph["root"], (0, 0, 7.4))
    A["DOC"] = (doc["root"], (0, 0, 3.4))
    A["OWN"] = (own["body"], (0, 0, 2.6))


def f02(n, A):
    """Bukan karena nunggak (tagihan LUNAS ✓) — tapi karena satu fatwa (dokumen + palu diketuk)."""
    sid = "F02"
    neon(grid="vp_grid2", em=1.8, rig_c=(0, 0, 2.5), rig_s=1.3, fade=(10, 46))
    V.disc_ped("pdL", 2.6, "n_cyan", (-4.2, 0, 0), em=3.5, h=.4)
    V.disc_ped("pdR", 2.6, "n_pink", (4.2, 0, 0), em=3.5, h=.4)
    bill = F.document("bill", (-4.2, 0, .45), .75, "TAGIHAN", "Sewa toko", None, 6, "n_cyan")
    pop_in(bill["root"], fr(sid, 3.3), 1.0)
    ok = F.check("ok", (-4.2, -.6, 2.6), 1.3)
    pop_in(ok, fr(sid, 3.85), 1.3)
    lun = H_text("lunas", "LUNAS", (-4.2, -.7, .9), .7, "ok_green", 4.0)
    pop_in(lun, fr(sid, 3.95), 1.0)
    fat = F.document("fat", (4.2, 0, .45), .82, "FATWA", "MUI No. 131 Tahun 2026", None, 7)
    pop_in(fat["root"], fr(sid, 4.45), 1.0)
    gv = F.gavel("gv", (7.0, -2.2, .45), .9)
    gv["piv"].rotation_euler = (0, math.radians(-55), 0)
    pop_in(gv["piv"], fr(sid, 4.5), 1.0, 8)
    pop_in(gv["block"], fr(sid, 4.5), 1.0, 8)
    anim(gv["piv"], "rotation_euler", fr(sid, 4.62), fr(sid, 5.0), (0, math.radians(-55), 0),
         (0, math.radians(-88), 0), "in")
    anim(gv["piv"], "rotation_euler", fr(sid, 5.0), fr(sid, 5.5), (0, math.radians(-88), 0),
         (0, math.radians(-70), 0), "out")
    rg = V.ring_obj("shock", (6.8, -2.2, .5), 2.0, .12, "n_gold", 6.0)
    pop_in(rg, fr(sid, 5.04), 1.8, 10)
    camera(sid, [(3.27, (-4.2, 0, 2.4), -108, 8, 13), (4.3, (-1.0, 0, 2.6), -96, 10, 15),
                 (5.0, (4.6, -.5, 2.6), -84, 12, 13.5), (6.3, (4.8, -.5, 2.6), -74, 14, 12.5)], lens=26)
    A["BILL"] = (bill["root"], (0, 0, 4.6))
    A["FAT"] = (fat["root"], (0, 0, 5.0))


def H_text(name, body, loc, size, key_, em):
    import world_hotel as H
    return H.text(name, body, size, key_, depth=.08, loc=loc, emission=em)


# ================================================================== KEJUTAN 1
def f03(n, A):
    """6 November, MUI menetapkan Fatwa No. 131/2026: dinding HP berisi artikel asli (MUI, CNN, detik) di-scroll."""
    sid = "F03"
    neon(grid="vp_grid", em=1.8, rig_c=(0, 0, 3), rig_s=1.6, fade=(14, 56))
    cal, cf = label3d("cal", "6 NOV 2026", (0, 1.2, 10.3), 1.1, "n_gold", 7.0)
    pop_pair((cal, cf), fr(sid, 6.63))
    ph = []
    for i, (im, x, y, rz, t) in enumerate((("art_cnn", -6.4, 1.6, .32, 6.75), ("art_mui", 0, 0, 0, 6.45),
                                           ("art_detik", 6.4, 1.6, -.32, 7.05))):
        p = F.article_phone(f"ph{i}", im, 8.6, (x, y, .2), rz,
                            scroll=[(1, 0.0), (fr(sid, t + .4), 0.0), (n_all(n), .55 if i == 1 else .35)])
        pop_in(p["root"], fr(sid, t), 1.0, 12)
        ph.append(p)
    no, nf = label3d("no", "No. 131 / 2026", (0, -1.6, -.2 + 1.0), .9, "n_pink", 7.0)
    for ob in (no, nf):
        ob.location.z += 0
    pop_pair((no, nf), fr(sid, 9.92))
    camera(sid, [(6.3, (0, 0, 9.6), -96, 4, 16), (7.6, (0, 0, 6.0), -102, 8, 22),
                 (9.9, (0, -.5, 4.2), -84, 10, 24), (12.47, (0, 0, 4.4), -74, 12, 22)], lens=24)
    A["CAL"] = ((0, 1.2, 12.0))
    A["MUI"] = (ph[1]["root"], (0, 0, 9.0))
    A["NO"] = ((0, -1.6, 2.0))


def f04(n, A):
    """Bukan cuma pakai: produksi & perdagangan juga haram (3 stasiun di-X), alasan: kesehatan & lingkungan."""
    sid = "F04"
    neon(grid="vp_grid2", em=1.8, rig_c=(0, 0, 2.5), rig_s=1.6, fade=(14, 56))
    xs = (-7.5, 0, 7.5)
    for i, (x, k) in enumerate(zip(xs, ("n_pink", "n_purple", "n_cyan"))):
        V.disc_ped(f"pd{i}", 3.0, k, (x, 0, 0), em=3.5, h=.4)
    pd = F.pod("pod", (-7.5, 0, .45), 1.1)
    SV.spin(pd, 1, n_all(n), 60)
    pop_in(pd, fr(sid, 12.6), 1.0)
    fac = V.brand_factory("fac", (0, .4, .45), "PRODUKSI")
    for o in (fac["body"], fac["trim"], fac["sign"]):
        o.scale = (.001,) * 3
    for o in (fac["body"], fac["trim"], fac["sign"]):
        pop_in(o, fr(sid, 13.1), .42)
    shp = V.vape_shop("shp", (7.5, .4, .45), 6.0, 4.0, 4.0, "JUAL")
    for o in shp.values():
        if hasattr(o, "scale") and o.type != "LIGHT":
            pop_in(o, fr(sid, 13.4), 1.0)
    for i, (x, t) in enumerate(zip(xs, (14.11, 14.62, 15.06))):
        xm(f"x{i}", (x, -2.4, 3.6), fr(sid, t), 1.5)
    for i, (txt, x, k) in enumerate((("PAKAI", -7.5, "n_pink"), ("PRODUKSI", 0, "n_purple"), ("PERDAGANGAN", 7.5, "n_cyan"))):
        t, f_ = label3d(f"lb{i}", txt, (x, -2.9, -.1 + .0), .55, k, 5.0)
        for ob in (t, f_):
            ob.location.z = .9 if ob is t else ob.location.z
        pop_pair((t, f_), fr(sid, (13.52, 14.62, 14.96)[i]))
    hr = N.heart("hr", (-3.6, -1.0, 9.0), 1.4, "n_red", 6.0)
    pop_in(hr, fr(sid, 17.1), 1.4)
    float_bob(hr, fr(sid, 17.4), n_all(n), .25, 50)
    gl = G.globe("gl", 1.8, (3.6, -1.0, 9.0), 3.0)
    for o in (gl["root"],):
        pop_in(o, fr(sid, 17.59), 1.0)
    SV.spin(gl["root"], fr(sid, 17.6), n_all(n), 40)
    camera(sid, [(12.47, (-7.5, 0, 2.6), -112, 12, 13), (13.9, (-4.5, 0, 2.8), -100, 14, 17),
                 (15.1, (2.5, 0, 3.0), -86, 16, 22), (16.6, (0, 0, 4.6), -90, 20, 30),
                 (18.68, (0, 0, 6.2), -96, 18, 30)], lens=24)
    A["POD"] = (pd, (0, 0, 4.5))
    A["HR"] = (hr, (0, 0, 1.8))
    A["GL"] = (gl["root"], (0, 0, 2.4))


def f05(n, A):
    """Terus, siapa yang paling kena? — kota dari udara, tanda tanya raksasa di atas plaza, sirene di toko."""
    sid = "F05"
    c = city(n, store=True)
    q = V.qmark("q", (0, -6, 16), 3.2, "n_gold", 7.0)
    pop_in(q, fr(sid, 19.5), 3.2)
    float_bob(q, fr(sid, 19.8), n_all(n), .5, 40)
    for i, x in enumerate((-30, -14, 14, 30)):
        so, li = V.siren(f"sr{i}", (x, 2.0, 7.4), 1.0)
        V.flash_siren(so, li, fr(sid, 19.0), n_all(n), 10)
    camera(sid, [(18.68, (0, 0, 4), -132, 34, 120), (20.55, (0, -2, 6), -100, 30, 92)], lens=24)
    A["Q"] = (q, (0, 0, 3.5))


def f06(n, A):
    """Ancaman PHK sampai 100 ribu pekerja; 200 industri terancam — artikel asli + kerumunan pekerja + 200 pabrik."""
    sid = "F06"
    neon(grid="vp_grid2", em=1.8, rig_c=(0, -2, 3), rig_s=2.0, fade=(18, 70))
    rnd = random.Random(6)
    crowd = []
    for i in range(32):
        x = -10.5 + (i % 8) * 1.45 + rnd.uniform(-.2, .2)
        y = -2.0 + (i // 8) * 1.6
        p = L.character(f"w{i}", "pekerja" if i % 3 else "teknisi", (x, y, 0), rnd.uniform(-.3, .3))
        L.pose(p, "stand", 1)
        if i % 4 == 0:
            L.pose(p, "think", fr(sid, 23.5))
        for o in (p["body"],):
            pop_in(o, fr(sid, 21.2 + .02 * i), L.CH_S, 9)
        crowd.append(p)
    hk, hf = label3d("phk", "PHK", (-5.5, 4.8, 6.6), 1.4, "n_red", 8.0)
    pop_pair((hk, hf), fr(sid, 21.8))
    p1 = F.article_phone("ap1", "art_phk", 7.6, (-15.0, 2.0, 0), .5,
                         scroll=[(1, 0.0), (fr(sid, 21.5), 0.0), (n_all(n), .3)])
    pop_in(p1["root"], fr(sid, 20.7), 1.0, 12)
    rows = []
    for r in range(10):
        mb = W.MB(f"fac{r}")
        for c in range(20):
            x, y = 3.0 + c * .9, -1.5 + r * 1.0
            mb.box(x, y, 0, x + .6, y + .6, .5, "ct_glass2")
            mb.box(x + .42, y + .4, .5, x + .55, y + .53, 1.0, "ct_con")
            mb.box(x - .02, y - .02, .5, x + .62, y + .62, .58, "n_red")
        ob = mb.build()
        V.glow(ob, {"n_red": 4.0})
        pop_in(ob, fr(sid, 24.83 + .16 * r), 1.0, 8)
        rows.append(ob)
    tt, tf = label3d("i200", "200 INDUSTRI", (11.5, 9.6, 5.4), 1.0, "n_gold", 7.0)
    pop_pair((tt, tf), fr(sid, 25.3))
    p2 = F.article_phone("ap2", "art_200", 7.6, (24.0, 3.0, 0), -.55,
                         scroll=[(1, 0.0), (fr(sid, 25.2), 0.0), (n_all(n), .3)])
    pop_in(p2["root"], fr(sid, 24.6), 1.0, 12)
    for i, x in enumerate((6.0, 17.0)):
        so, li = V.siren(f"sr{i}", (x, 9.3, 0), 1.2)
        pop_in(so, fr(sid, 26.8), 1.2)
        V.flash_siren(so, li, fr(sid, 26.9), n_all(n), 10)
    camera(sid, [(20.55, (-9, 0, 2.8), -118, 14, 20), (22.6, (-6.5, 0, 2.6), -98, 16, 22),
                 (24.4, (2, 1, 2.6), -92, 22, 28), (26.0, (11, 3, 1.4), -84, 30, 26),
                 (27.93, (12, 3, 1.4), -74, 34, 28)], lens=24)
    A["CROWD"] = (crowd[3]["body"], (0, 0, 2.8))
    A["FAC"] = ((12.0, 3.0, 2.0))


def f07(n, A):
    """Salah satu brand lokal yang paling disorot: FOOM — logo 3D naik di bawah lampu sorot & kilat kamera."""
    sid = "F07"
    neon(grid="vp_grid", em=1.2, rig_c=(0, 0, 3), rig_s=1.2, fade=(10, 46))
    V.disc_ped("ped", 3.4, "fm_pink", (0, 0, 0), em=4.0, h=.5)
    lg = F.foom_logo("logo", 7.0, (0, 0, 3.4), "n_white", 4.0, .45, plate="fm_pink")
    anim(lg, "location", fr(sid, 29.6), fr(sid, 30.3), (0, 0, -1.5), (0, 0, 3.4), "out")
    pop_in(lg, fr(sid, 29.6), 1.0, 10)
    sp = bpy.data.lights.new("spot", "SPOT")
    sp.energy, sp.spot_size, sp.color = 9000, math.radians(26), (1, .75, .9)
    so = bpy.data.objects.new("spot", sp)
    lp._link(so)
    so.location = (0, -6, 16)
    for f, (x, y) in ((1, (-9, 3)), (fr(sid, 28.8), (6, 2)), (fr(sid, 29.8), (0, 0))):
        tgt = (x, y, 0)
        d = (tgt[0] - so.location.x, tgt[1] - so.location.y, tgt[2] - so.location.z)
        so.rotation_euler = (math.atan2(math.hypot(d[0], d[1]), -d[2]), 0, math.atan2(d[1], d[0]) + math.pi / 2)
        so.keyframe_insert("rotation_euler", frame=f)
    rnd = random.Random(3)
    for i in range(8):
        a = -math.pi * (.15 + .7 * i / 7)
        li = bpy.data.lights.new(f"fl{i}", "POINT")
        li.color = (1, 1, 1)
        lo = bpy.data.objects.new(f"fl{i}", li)
        lp._link(lo)
        lo.location = (math.cos(a) * 9, math.sin(a) * 9 - 2, 2.0 + rnd.uniform(-.5, 1.0))
        for f, e in ((1, 0),):
            li.energy = e
            li.keyframe_insert("energy", frame=f)
        f0 = fr(sid, 29.97 + i * .08 + rnd.uniform(0, .05))
        for f, e in ((f0 - 1, 0), (f0, 6000), (f0 + 2, 0)):
            li.energy = e
            li.keyframe_insert("energy", frame=f)
    for i, im in enumerate(("art_cnn", "art_phk", "art_mui", "art_200")):
        a = math.radians(-150 + i * 40)
        x, y = math.cos(a + math.pi) * 0 + (-12 + i * 8), 9.0
        p = F.article_phone(f"bp{i}", im, 7.0, (x, y, .2), -(i - 1.5) * .25, em=.6)
    camera(sid, [(27.93, (-2, 2, 3), -118, 18, 22), (29.4, (0, 0, 3.4), -100, 12, 20),
                 (30.68, (0, 0, 3.6), -90, 8, 17)], lens=26)
    A["LOGO"] = (lg, (0, 0, 2.4))


# ================================================================== KAIL 2 + campaign
def f08(n, A):
    """Isu datang pas FOOM jalanin campaign besar: kota pink sakura, billboard poster campaign, store & menara FOOM."""
    sid = "F08"
    c = city(n, store=True, tower=True)
    F.petals("pt", 70, (-16, -14, 16, 6), (2, 16), 1, n_all(n), 4)
    camera(sid, [(30.68, (0, -3, 3.0), -100, 6, 22), (32.4, (0, 0, 6.5), -94, 12, 40),
                 (34.64, (0, 6, 14), -90, 16, 74)], lens=24)
    A["STORE"] = (c["store"]["logo"], (0, 0, 1.6))
    A["BB"] = (c["screens"][1], (0, 0, 7.0))
    A["TW"] = (c["tower"]["logo"], (0, 0, 3.0))


def f09(n, A):
    """Kolaborasi FOOM x YB (Reza Arap): Pink Sakura, visual rame, gaya pop Jepang — galeri poster asli + torii."""
    sid = "F09"
    neon(grid="vp_grid", em=1.6, rig_c=(0, 2, 4), rig_s=2.0, fade=(16, 60))
    F.torii("tor", (0, 10, 0), 1.6)
    tm = W.MB("sk")
    rnd = random.Random(2)
    for x, y in ((-12, 6), (12, 6), (-16, 12), (16, 12), (-9, 14), (9, 14)):
        F.sakura_tree(tm, x, y, 1.6, rnd)
    tm.build()
    F.petals("pt", 90, (-16, -6, 16, 14), (1, 16), 1, n_all(n), 9, .2)
    cards = [("p_collab", 34.97, -12.0), ("ig_post", 35.4, -8.0), ("p_pink", 37.48, -4.0), ("p_ybglass", 37.69, 0.0),
             ("p_wm", 38.25, 4.0), ("p_sipaling", 38.68, 8.0), ("p_guy", 39.37, 12.0)]
    obs = {}
    for i, (im, t, x) in enumerate(cards):
        y = 2.0 + (x / 12.0) ** 2 * 3.0
        ob = G.img_plane(f"c{i}", im, h=5.6, loc=(x, y, .6), rot_z=-x * .045, em=1.25,
                         frame="fm_pink" if i % 2 == 0 else "n_cyan", frame_em=5.0)
        pop_in(ob, fr(sid, t - .1), 1.0, 12)
        float_bob(ob, fr(sid, t + .4), n_all(n), .18, 60, i)
        obs[im] = ob
    sk, skf = label3d("pink", "PINK SAKURA", (0, 9.6, 12.6), 1.2, "fm_pink", 8.0)
    pop_pair((sk, skf), fr(sid, 37.48))
    camera(sid, [(34.64, (-11, 2, 3.4), -104, 8, 13), (35.8, (-9, 2, 3.4), -96, 8, 14),
                 (37.4, (-3, 2.5, 3.6), -92, 9, 15), (38.5, (4, 2.5, 3.6), -88, 9, 15),
                 (39.5, (9, 3, 3.8), -84, 10, 15), (40.32, (4, 4, 5.0), -92, 12, 28)], lens=24)
    A["COLLAB"] = (obs["p_collab"], (0, 0, 6.6))
    A["IG"] = (obs["ig_post"], (0, 0, 6.6))
    A["GUY"] = (obs["p_guy"], (0, 0, 7.4))


def f10(n, A):
    """Jurus klasik: pinjam fanbase (fans bersorak, hati beterbangan), produk terasa eksklusif (tali beludru + mahkota)."""
    sid = "F10"
    neon(grid="vp_grid2", em=1.6, rig_c=(0, 0, 2.5), rig_s=1.6, fade=(12, 50))
    V.disc_ped("ped", 2.4, "n_gold", (0, 2, 0), em=4.0, h=.9)
    pd = F.pod("pod", (0, 2, .95), 1.2, "pod_pink")
    SV.spin(pd, 1, n_all(n), 70)
    cr = V.crown("cr", (0, 2, 6.0), 1.2, "n_gold", 6.0)
    pop_in(cr, fr(sid, 42.7), 1.2)
    mb = W.MB("rope")
    for k in range(7):
        a = math.pi * (1.1 + .8 * k / 6)
        x, y = math.cos(a) * 4.2, 2 + math.sin(a) * 4.2
        mb.cyl(x, y, 0, 1.3, .1, "n_gold", n=8)
        mb.sphere(x, y, 1.35, .16, "n_gold")
        if k < 6:
            a2 = math.pi * (1.1 + .8 * (k + 1) / 6)
            x2, y2 = math.cos(a2) * 4.2, 2 + math.sin(a2) * 4.2
            for j in range(6):
                u0, u1 = j / 6, (j + 1) / 6
                sag = lambda u: 1.15 - .35 * math.sin(math.pi * u)  # noqa: E731
                mb.box(min(x + (x2 - x) * u0, x + (x2 - x) * u1) - .06, min(y + (y2 - y) * u0, y + (y2 - y) * u1) - .06,
                       sag(u0) - .07, max(x + (x2 - x) * u0, x + (x2 - x) * u1) + .06,
                       max(y + (y2 - y) * u0, y + (y2 - y) * u1) + .06, sag(u0) + .07, "doc_red")
    ro = mb.build()
    V.glow(ro, {"n_gold": 3.0})
    rnd = random.Random(12)
    fans = []
    for i in range(18):
        a = math.pi * (1.08 + .84 * (i % 9) / 8)
        r = 6.4 + (i // 9) * 1.6
        x, y = math.cos(a) * r, 2 + math.sin(a) * r
        p = R.shopper(f"fan{i}", i + 3, (x, y, 0), math.atan2(2 - y, -x) - math.pi / 2)
        L.pose(p, "stand", 1)
        L.pose(p, "cheer", fr(sid, 41.36 + .03 * i))
        fans.append(p)
    for i in range(7):
        hx = (i - 3) * 1.6
        h_ = N.heart(f"h{i}", (hx, -3.5, 2.5), .45, "fm_pink", 6.0)
        f0 = fr(sid, 41.4 + .1 * i)
        hide_until(h_, f0)
        arc_move(h_, f0, f0 + 24, (hx, -3.5, 2.5), (0, 2, 4.8), 2.5)
        pop_out(h_, f0 + 24, 6)
    ex, exf = label3d("ex", "EKSKLUSIF", (0, 6.0, 8.2), .9, "n_gold", 8.0)
    pop_pair((ex, exf), fr(sid, 42.7))
    camera(sid, [(40.32, (0, 0, 2.4), -120, 18, 20), (41.6, (0, 1, 2.6), -100, 14, 17),
                 (43.67, (0, 2, 3.8), -78, 12, 13)], lens=24)
    A["FANS"] = (fans[4]["body"], (0, 0, 2.8))
    A["POD"] = (pd, (0, 0, 4.4))


# ================================================================== KEJUTAN 3: respons krisis
def f11(n, A):
    """Waktu isu meledak: artikel beterbangan keluar (gelombang merah), logo FOOM tetap tenang di tengah."""
    sid = "F11"
    neon(grid="vp_grid", em=1.4, rig_c=(0, 0, 3), rig_s=1.6, fade=(12, 50))
    V.disc_ped("ped", 3.0, "fm_pink", (0, 0, 0), em=4.0, h=.5)
    lg = F.foom_logo("logo", 6.0, (0, 0, 3.4), "n_white", 3.5, .4, plate="fm_pink")
    f_b = fr(sid, 44.13)
    for i, im in enumerate(F.ARTS):
        a = math.radians(-90 + (i - 2.5) * 32)
        p0 = (0, 0, 3.0)
        p1 = (math.cos(a) * 11, 6 + math.sin(a) * 4 + 4, 1.0 + (i % 2) * 2.2)
        ph = F.article_phone(f"x{i}", im, 5.6, p0, -(i - 2.5) * .25, em=1.1,
                             scroll=[(1, 0.0), (n_all(n), .25)])
        ph["root"].scale = (.001,) * 3
        key(ph["root"], "scale", f_b - 1, (.001,) * 3)
        anim(ph["root"], "scale", f_b, f_b + 10, (.001,) * 3, (1, 1, 1), "out")
        arc_move(ph["root"], f_b, f_b + 16, p0, p1, 3.0, "out")
    for k in range(3):
        rg = V.ring_obj(f"sw{k}", (0, 0, .6), 3.0, .14, "n_red", 7.0)
        pop_in(rg, f_b + k * 5, 4.0 + k * 1.2, 14)
        pop_out(rg, f_b + k * 5 + 16, 8)
    sh = V.ring_obj("shield", (0, 0, .55), 4.4, .16, "n_cyan", 6.0)
    pop_in(sh, fr(sid, 44.84), 1.0)
    SV.spin(sh, fr(sid, 44.84), n_all(n), 40)
    xm("x1", (-6.0, -2.0, 6.6), fr(sid, 44.84), 1.0)
    xm("x2", (6.0, -2.0, 6.6), fr(sid, 45.54), 1.0)
    for i, (txt, x, t) in enumerate((("PANIK", -6.0, 44.84), ("NYERANG BALIK", 6.0, 45.54))):
        tt, tf = label3d(f"l{i}", txt, (x, -2.0, 4.4), .55, "n_red", 6.0)
        pop_pair((tt, tf), fr(sid, t))
    camera(sid, [(43.67, (0, 0, 3.4), -96, 8, 15), (44.4, (0, 2, 4.2), -100, 14, 24),
                 (46.05, (0, 1, 4.4), -84, 12, 22)], lens=24)
    A["LOGO"] = (lg, (0, 0, 2.6))


def f12(n, A):
    """Pernyataan "Satu Industri, Satu Komitmen" — hormati semua pandangan (timbangan seimbang) — patuh aturan
    pemerintah (gedung pemerintah + centang)."""
    sid = "F12"
    neon(grid="vp_grid2", em=1.6, rig_c=(4, 0, 3), rig_s=2.0, fade=(16, 60))
    card = F.statement_card("st", (-8, 0, .6), 1.0)
    pop_in(card["root"], fr(sid, 46.3), 1.0, 12)
    card["l1"].scale = (.001,) * 3
    card["l2"].scale = (.001,) * 3
    pop_in(card["l1"], fr(sid, 47.27), 1.0, 8)
    pop_in(card["l2"], fr(sid, 48.13), 1.0, 8)
    lg = F.foom_logo("lg", 3.2, (-8, -.2, 7.4), "n_white", 3.5, .25)
    pop_in(lg, fr(sid, 46.1), 1.0)
    b = N.balance("bal", (4, 1, 0), .9, "n_cyan")
    N.balance_key(b, 1, -8)
    N.balance_key(b, fr(sid, 49.13), -8)
    N.balance_key(b, fr(sid, 49.13) + 18, 0)
    for k, (sx, kk) in enumerate(((-1, "n_pink"), (1, "n_purple"))):
        hh = N.heart(f"hp{k}", (4 + sx * 3.24, 1, 3.6), .55, kk, 5.0)
        hh.parent = b["pans"][k]
        hh.location = (0, 0, -1.4)
    gv = V.gov_building("gov", (16, 2, 0), "PEMERINTAH", .8)
    ck = F.check("ck", (16, -2.6, 8.4), 1.6)
    pop_in(ck, fr(sid, 51.9), 1.6)
    camera(sid, [(46.05, (-8, 0, 3.4), -98, 6, 14), (48.6, (-6, 0, 3.6), -90, 8, 16),
                 (49.6, (2.5, 0, 4.0), -94, 10, 18), (51.2, (12, 0, 4.4), -86, 12, 22),
                 (53.18, (15, 1, 4.8), -78, 14, 24)], lens=24)
    A["CARD"] = (card["root"], (0, 0, 6.2))
    A["BAL"] = ((4, 1, 6.4))
    A["GOV"] = ((16, 2, 9.6))


def f13(n, A):
    """Di setiap poster campaign: label 21+ dan peringatan nikotin tetap dipasang — galeri poster, zoom ke label."""
    sid = "F13"
    neon(grid="vp_grid", em=1.6, rig_c=(0, 0, 3), rig_s=1.8, fade=(14, 54))
    ims = ["p_sipaling", "p_pink", "p_wm", "p_bloom", "p_guy"]
    obs = []
    for i, im in enumerate(ims):
        x = (i - 2) * 5.0
        ob = G.img_plane(f"ps{i}", im, h=6.4, loc=(x, abs(i - 2) * .9, .6), rot_z=-(i - 2) * .12, em=1.25,
                         frame="fm_pink", frame_em=4.0)
        pop_in(ob, fr(sid, 53.2 + .07 * i), 1.0, 10)
        obs.append(ob)
    bd, bt = F.badge21("b21", (2.6, -1.8, 2.4), 1.3)
    pop_in(bd, fr(sid, 54.8), 1.0)
    pop_in(bt, fr(sid, 54.8), 1.0)
    ws, wt = F.warn_strip("ws", (0, -2.2, .05), 13.0, 1.0, "PERINGATAN: MENGANDUNG NIKOTIN")
    pop_in(ws, fr(sid, 55.88), 1.0, 9)
    pop_in(wt, fr(sid, 55.88), 1.0, 9)
    camera(sid, [(53.18, (0, 0, 4.0), -98, 8, 22), (54.6, (1.5, -.5, 2.4), -92, 6, 13),
                 (55.9, (0, -1.5, 1.6), -86, 10, 13), (57.62, (0, -1, 2.6), -94, 14, 19)], lens=24)
    A["B21"] = (bd, (0, 0, 1.6))
    A["WARN"] = (ws, (0, 0, 1.4))


def f14(n, A):
    """Pesannya satu: REGULASI (naik, centang hijau) — bukan ELIMINASI (turun, silang merah)."""
    sid = "F14"
    neon(grid="vp_grid2", em=1.6, rig_c=(0, 0, 3), rig_s=1.6, fade=(12, 50))
    rg = V.pillar("pr", 4.6, 2.4, 2.4, "ok_green", 1.4, 6.0, (-4.2, 0, 0))
    el = V.pillar("pe", 4.6, 2.4, 2.4, "n_red", 1.4, 6.0, (4.2, 0, 0))
    key(rg, "scale", 1, (1, 1, .55))
    anim(rg, "scale", fr(sid, 58.72), fr(sid, 59.3), (1, 1, .55), (1, 1, 1.25), "back")
    key(el, "scale", 1, (1, 1, .9))
    anim(el, "scale", fr(sid, 59.58), fr(sid, 60.2), (1, 1, .9), (1, 1, .25), "inout")
    t1, f1 = label3d("reg", "REGULASI", (-4.2, -1.8, 8.6), .9, "ok_green", 8.0)
    pop_pair((t1, f1), fr(sid, 58.72))
    t2, f2 = label3d("eli", "ELIMINASI", (4.2, -1.8, 5.6), .9, "n_red", 8.0)
    pop_pair((t2, f2), fr(sid, 59.37))
    ck = F.check("ck", (-4.2, -1.8, 11.2), 1.2)
    pop_in(ck, fr(sid, 58.9), 1.2)
    xm("xx", (4.2, -1.8, 8.0), fr(sid, 59.6), 1.2)
    camera(sid, [(57.62, (0, 0, 5.4), -104, 10, 29), (59.0, (0, 0, 5.6), -92, 10, 27),
                 (60.62, (0, 0, 5.8), -82, 12, 28)], lens=24)
    A["REG"] = ((-4.2, -1.8, 10.0))
    A["ELI"] = ((4.2, -1.8, 7.0))


# ================================================================== CTA
def f15(n, A):
    """Saat krisis, yang paling mahal bukan produk, tapi kepercayaan: timbangan produk vs kepercayaan (+ mahkota)."""
    sid = "F15"
    neon(grid="vp_grid", em=1.6, rig_c=(0, 0, 3), rig_s=1.8, fade=(14, 54))
    b = N.balance("bal", (0, 0, 0), 1.0, "n_gold")
    N.balance_key(b, 1, 0)
    N.balance_key(b, fr(sid, 63.82), 0)
    N.balance_key(b, fr(sid, 65.05), 14)
    N.balance_key(b, fr(sid, 65.05) + 10, 12)
    pd = F.pod("pd", (0, 0, 0), .55)
    pd.parent = b["pans"][0]
    pd.location = (0, 0, -2.2)
    hr = N.heart("hr", (0, 0, 0), .95, "fm_pink", 7.0)
    hr.parent = b["pans"][1]
    hr.location = (0, 0, -1.0)
    pop_in(hr, fr(sid, 64.87), .95)
    cr = V.crown("cr", (3.6, 0, 9.2), 1.0, "n_gold", 6.0)
    pop_in(cr, fr(sid, 65.3), 1.0)
    float_bob(cr, fr(sid, 65.6), n_all(n), .2, 40)
    t1, f1 = label3d("lp", "PRODUK", (-3.6, -2.2, .2), .6, "n_cyan", 6.0)
    t2, f2 = label3d("lk", "KEPERCAYAAN", (3.6, -2.2, .2), .6, "fm_pink", 7.0)
    pop_pair((t1, f1), fr(sid, 64.26))
    pop_pair((t2, f2), fr(sid, 65.05))
    camera(sid, [(60.62, (0, 0, 4.6), -112, 16, 22), (62.5, (0, 0, 4.4), -98, 10, 17),
                 (64.3, (0, 0, 4.4), -90, 8, 16), (66.43, (1.5, 0, 4.6), -78, 10, 17)], lens=24)
    A["PRODUK"] = ((-3.6, 0, 5.6))
    A["TRUST"] = ((3.6, 0, 5.0))


def f16(n, A):
    """Kalau kamu pemilik brand & tiba-tiba diterpa isu sebesar ini — kota: kamu di depan toko, layar berita merah."""
    sid = "F16"
    c = city(n, store=False, news=True)
    st = V.vape_store_day("my", (0, 4, Z0), 14.0, 10.0, "vs_purple", "BRAND KAMU", seed=8)
    me = L.character("kamu", "cowok", (0, -2.6, Z0), 0.0)
    L.pose(me, "stand", 1)
    L.pose(me, "think", fr(sid, 70.9))
    for i, x in enumerate((-8, 8)):
        so, li = V.siren(f"sr{i}", (x, 2.4, 7.6), 1.0)
        V.flash_siren(so, li, fr(sid, 69.5), n_all(n), 10)
    q = V.qmark("q", (0, -2.6, 5.2), 1.2, "n_gold", 7.0)
    pop_in(q, fr(sid, 72.0), 1.2)
    camera(sid, [(66.43, (0, -2, 3.0), -120, 20, 30), (68.4, (0, -2, 2.6), -100, 12, 16),
                 (70.0, (0, 0, 8), -94, 16, 42), (72.61, (0, -2, 3.2), -84, 10, 14)], lens=24)
    A["ME"] = (me["body"], (0, 0, 2.7))
    A["NEWS"] = ((-28, 26, 22))


def f17(n, A):
    """Tulis di komentar — jawaban paling menarik dibedah; simpan video ini: HP di tangan + ikon simpan (bookmark)."""
    sid = "F17"
    c = city(n, store=True, tower=True)
    me = L.character("kamu", "cowok", (-1.6, -5.0, Z0), .25, hold="phone")
    L.pose(me, "stand", 1)
    L.pose(me, "point", fr(sid, 72.84))
    ph = V.phone("ph", (2.6, -5.2, 2.0), 1.2)
    pop_in(ph, fr(sid, 72.7), 1.0)
    mb = W.MB("bm")
    mb.poly([(-.7, 0, 1.6), (.7, 0, 1.6), (.7, 0, -.6), (0, 0, 0), (-.7, 0, -.6)], [(0, 1, 2, 3, 4)], "n_gold")
    bm = mb.build((3.8, -5.6, 5.0))
    V.glow(bm, {"n_gold": 6.0})
    pop_in(bm, fr(sid, 75.53), 1.2)
    F.petals("pt", 40, (-10, -12, 10, 2), (2, 12), 1, n_all(n), 7)
    camera(sid, [(72.61, (0, -5, 2.8), -102, 10, 14), (75.0, (1, -5, 3.0), -92, 12, 15),
                 (78.72, (0, -3, 4.2), -80, 16, 22)], lens=24)
    A["ME"] = (me["body"], (0, 0, 2.7))
    A["BM"] = (bm, (0, 0, 1.4))


def f18(n, A):
    """Buat tim FOOM: kalau kalian nonton, aku pengen bedah langsung strategi kalian — pesawat kertas ke menara FOOM."""
    sid = "F18"
    c = city(n, store=True, tower=True)
    me = L.character("kamu", "cowok", (-3.0, -8.0, Z0), .3, hold="phone")
    L.pose(me, "point", 1)
    pl = V.paper_plane("pl", (0, 0, 0), .8)
    p0, p1 = (-2.6, -8.4, 2.6), (0, TW_Y - 6.5, 30.0)
    pl.rotation_euler = (0, 0, math.pi * .5)
    hide_until(pl, fr(sid, 79.2))
    arc_move(pl, fr(sid, 79.2), fr(sid, 81.4), p0, p1, 4.0)
    camera(sid, [(78.72, (-2, -8, 2.6), -110, 12, 16), (80.2, (0, 0, 10), -96, 14, 52),
                 (82.16, (0, TW_Y - 6, 31), -90, 6, 46)], lens=24)
    A["ME"] = (me["body"], (0, 0, 2.7))
    A["TW"] = (c["tower"]["logo"], (0, 0, 4.0))


def f19(n, A):
    """Disclaimer: edukasi bisnis untuk 21+, bukan ajakan — kamera mundur ke seluruh kota diorama, lencana 21+."""
    sid = "F19"
    c = city(n, store=True, tower=True)
    bd, bt = F.badge21("b21", (0, -10, 16), 3.0)
    pop_in(bd, fr(sid, 83.46), 1.0)
    pop_in(bt, fr(sid, 83.46), 1.0)
    F.petals("pt", 60, (-30, -20, 30, 10), (4, 24), 1, n_all(n), 11, .3)
    camera(sid, [(82.16, (0, TW_Y - 6, 31), -92, 8, 48), (84.0, (0, -4, 14), -100, 18, 110),
                 (86.8, (0, 0, 10), -112, 28, 190)], lens=24)
    A["B21"] = (bd, (0, 0, 3.6))


SCENES = {f"F{i:02d}": globals()[f"f{i:02d}"] for i in range(1, 20)}
K.SCENES = SCENES

if __name__ == "__main__":
    K.main()
