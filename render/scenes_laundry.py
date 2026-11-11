"""20 adegan video "Laundry Koin" (timeline mengikuti VO yang dipercepat 1.35x).

  python3 render/scenes_laundry.py -- --scene L01 --out OUT/L01 [--res 720x1280] [--samples 4] [--frames a-b]

Isi VO: hook satire "cuci uang" -> laundry koin -> model bisnis (mesin, bayar koin/QRIS, tanpa kasir,
tercatat otomatis) -> strategi lokasi (kos, apartemen, kantor; jam ramai) -> hitungan omzet
(1 mesin x 5 putaran x Rp15rb = Rp75rb/hari; 10 mesin Rp750rb; x30 = Rp22,5 jt) -> biaya -> ekspansi ->
penutup satire (uang masuk lewat mesin, bukan pintu belakang) -> CTA.
"""
import argparse
import json
import math
import os
import random
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowpoly as lp  # noqa: E402
import world as W  # noqa: E402
import world_tahu as T  # noqa: E402
import world_hotel as H  # noqa: E402
import world_laundry as L  # noqa: E402
import scenes as SC  # noqa: E402
from scenes import key, make_camera, cam_keys, orbit, visible_between, route_ribbon, studio_floor, \
    traffic  # noqa: E402

FPS = 30
SPEED = 1.35
_SRC = [("L01", 0.0), ("L02", 4.9), ("L03", 9.1), ("L04", 10.9), ("L05", 14.1), ("L06", 17.6), ("L07", 21.2),
        ("L08", 25.4), ("L09", 30.0), ("L10", 33.1), ("L11", 38.4), ("L12", 44.8), ("L13", 48.0), ("L14", 51.4),
        ("L15", 55.9), ("L16", 62.1), ("L17", 67.9), ("L18", 71.9), ("L19", 76.9), ("L20", 81.5)]
TIMELINE = [(s, round(t / SPEED, 3)) for s, t in _SRC]
END_T = round(93.45 / SPEED, 3)                 # VO 92.25 dtk + jeda 1.2 dtk

LX, LY = L.LAUNDRY_C
LFRONT = LY - L.LD / 2


def scene_range(sid):
    ids = [s for s, _ in TIMELINE]
    i = ids.index(sid)
    t0 = TIMELINE[i][1]
    t1 = TIMELINE[i + 1][1] if i + 1 < len(TIMELINE) else END_T
    f0, f1 = round(t0 * FPS), round(t1 * FPS)
    return t0, t1, f0, f1 - f0


def fr(sid, src):
    """frame lokal adegan untuk kata yang diucapkan pada detik `src` VO asli."""
    t0 = dict(TIMELINE)[sid]
    return max(1, int((src / SPEED - t0) * FPS))


def pop(ob, f, s=1.0):
    sc = s if isinstance(s, tuple) else (s,) * 3
    key(ob, "scale", 1, (0.001,) * 3)
    key(ob, "scale", max(1, f), (0.001,) * 3)
    key(ob, "scale", f + 4, tuple(v * 1.18 for v in sc))
    key(ob, "scale", f + 7, sc)


def grow_z(ob, f0, f1, s=1.0):
    key(ob, "scale", 1, (s, s, .001))
    key(ob, "scale", max(1, f0), (s, s, .001))
    key(ob, "scale", f1, (s, s, s * 1.05))
    key(ob, "scale", f1 + 4, (s, s, s))


def fly(ob, f0, f1, p0, p1, arc=0.0):
    key(ob, "location", 1, p0)
    key(ob, "location", max(1, f0), p0)
    if arc:
        mid = tuple((a + b) / 2 for a, b in zip(p0, p1))
        key(ob, "location", (f0 + f1) // 2, (mid[0], mid[1], mid[2] + arc))
    key(ob, "location", f1, p1)


def emission_ramp(mat, keys):
    """keys: [(frame, kekuatan)] untuk material berpendar (mis. papan nama menyala)."""
    b = mat.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for f, v in keys:
        b.default_value = v
        b.keyframe_insert("default_value", frame=f)


def ring(name, loc, r=1.0, w=.25, key_="lw_teal", n=40, em=1.0):
    mb = W.MB(name)
    vs = []
    for i in range(n):
        a = 2 * math.pi * i / n
        vs += [(math.cos(a) * (r - w), math.sin(a) * (r - w), 0), (math.cos(a) * r, math.sin(a) * r, 0)]
    fs = [(2 * i, 2 * ((i + 1) % n), 2 * ((i + 1) % n) + 1, 2 * i + 1) for i in range(n)]
    mb.poly(vs, fs, key_)
    ob = mb.build(loc)
    ob.data.materials[0] = lp.mat(key_, emission=em)
    return ob


def studio_money(cx=1000, cy=0, size=20):
    studio_floor(cx, cy, size=size, wall=False)


def pedestal_washer(name, loc, s=1.5, money=False, spin_f=(1, 400)):
    mb = W.MB(name)
    mb.cyl(0, 0, 0, .4, 1.25 * s, "c_white", n=24)
    mb.cyl(0, 0, .4, .46, 1.18 * s, "lw_teal", n=24)
    dc = L.washer(mb, 0, 0, .46, s)
    ob = mb.build(loc)
    drum = L.drum_clothes(name + "_drum", (loc[0] + dc[0], loc[1] + dc[1], loc[2] + dc[2]), s, n=8, money=money)
    L.spin(drum, *spin_f, turns_per_sec=.9)
    return ob, drum, (loc[0], loc[1], loc[2] + .46 + 1.5 * s)


# ------------------------------------------------------------------ adegan
def l01(n, info, A, cx=600, cy=0):
    """hook: 'katanya laundry itu cara bikin uang jadi bersih' — HP berita + mesin cuci berisi uang."""
    studio_floor(cx, cy, size=16, wall=False)
    ph = L.phone_feed("phone", 1.0).build((cx - 2.6, cy + 1.2, 0), .3)
    t1 = H.text("hl1", "TRENDING", .2, "c_white", depth=.02, loc=(0, -.19, 3.5 + .86))
    t2 = H.text("hl2", "CUCI UANG?", .36, "news_red", depth=.03, loc=(0, -.19, 3.5 + .22))
    for t in (t1, t2):
        t.parent = ph
    pop(ph, 3, 1.0)
    wm, drum, top = pedestal_washer("wm", (cx + 2.2, cy, 0), 1.4, money=True, spin_f=(1, n))
    pop(wm, 8, 1.0)
    pop(drum, 8, 1.0)
    rnd = random.Random(2)
    door = (cx + 2.2, cy - .77 - .25, .46 + .68 * 1.4)
    for k in range(6):                      # lembaran uang terbang masuk ke pintu mesin
        mb = W.MB(f"note{k}")
        L.money_note(mb, 0, 0, 0, .9)
        ob = mb.build()
        ob.rotation_euler = (math.pi / 2, rnd.uniform(-.6, .6), rnd.uniform(-.5, .5))
        f0 = 18 + k * 9
        p0 = (cx + 2.2 + rnd.uniform(-2.5, 2.5), cy - 3.5, 4.5 + rnd.uniform(0, 1.5))
        fly(ob, f0, f0 + 16, p0, door)
        key(ob, "scale", f0 + 13, (1, 1, 1))
        key(ob, "scale", f0 + 17, (.01, .01, .01))
    f_b = fr("L01", 3.66)
    for k, (dx, dz) in enumerate(((-1.6, 3.6), (1.5, 3.9), (1.9, 1.6))):
        sp = L.sparkle(f"sp{k}", (cx + 2.2 + dx, cy - 1.4, dz), .45)
        pop(sp, f_b + k * 3, 1.0)
    A["UANG"] = (cx + 2.2, cy - 1.0, top[2] + .3)
    A["BERITA"] = (cx - 2.6, cy + 1.0, 3.4)
    cam, tgt = make_camera(lens=24, shift_y=.1)
    tg = (cx + .1, cy + .5, 2.4)
    cam_keys(cam, tgt, [(1, orbit(tg, -96, 12, 19), tg), (n, orbit(tg, -86, 11, 17), tg)])


def l02(n, info, A):
    """'Tenang, ini laundry koin yang dicuci' — gedung laundry koin, papan nama menyala, pelanggan datang."""
    sign_mat = lp.mat("lw_sign", emission=1.4)
    emission_ramp(sign_mat, [(1, .0), (fr("L02", 6.5), .0), (fr("L02", 6.5) + 8, 2.4), (fr("L02", 6.5) + 16, 1.4)])
    sub = lp.mat("lw_yellow", emission=1.4 * .8)
    emission_ramp(sub, [(1, .0), (fr("L02", 7.2), .0), (fr("L02", 7.2) + 10, 1.2)])
    c = L.character("cust", "hijab", (LX - 9, LFRONT - 9.5, L.Z), 0, hold="basket")
    L.walk_to(c, [(LX - 9, LFRONT - 9.5), (LX - 2.5, LFRONT - 6.0), (LX - .4, LFRONT - 2.2)], 6, speed=1.9)
    A["LAUNDRY"] = (LX + .75, LFRONT - .6, L.Z + L.LH1 + 1.4)
    A["MESIN"] = (LX - 2.5, LY + 4.0, L.Z + 1.8)
    traffic(n, n=4)
    cam, tgt = make_camera(lens=20, shift_y=.06)
    cam_keys(cam, tgt, [(1, (-11, -38, 4.2), (0, -9, 4.6)), (n, (-7.5, -33, 4.0), (0, -9, 4.6))])


def l03(n, info, A, cx=900, cy=0):
    """'Cuma bajunya' — mesin berisi baju berputar, pelanggan memegang baju bersih yang berkilau."""
    studio_floor(cx, cy, size=14, wall=False)
    wm, drum, top = pedestal_washer("wm", (cx, cy, 0), 1.6, spin_f=(1, n))
    c = L.character("girl", "cewek", (cx + 2.6, cy - 1.2, 0), -.35, hold="clothes")
    f = fr("L03", 9.3)
    for k, (dx, dz) in enumerate(((2.0, 2.6), (3.1, 2.2), (2.5, 3.0), (-1.2, 3.2))):
        sp = L.sparkle(f"sp{k}", (cx + dx, cy - 1.8, dz), .35)
        pop(sp, f + k * 3, 1.0)
    A["BAJU"] = (cx, cy - 1.2, 1.55)
    cam, tgt = make_camera(lens=26, shift_y=.0)
    tg = (cx + 1.0, cy, 1.7)
    cam_keys(cam, tgt, [(1, orbit(tg, -100, 9, 9.5), tg), (n, orbit(tg, -88, 8, 8.5), tg)])


def l04(n, info, A, cx=500, cy=0):
    """'Model bisnisnya sederhana. Sediakan mesin cuci dan pengering' — mesin muncul satu per satu."""
    it = L.interior_set("int", cx, cy)
    f0 = fr("L04", 12.5)
    for k, w in enumerate(it["washers"]):
        pop(w, f0 + k * 3, 1.0)
    pop(it["dry"], fr("L04", 13.44), 1.0)
    wx, wy = it["washers"][2].location[0], it["washers"][2].location[1]
    A["MESIN"] = (wx + .7, wy, 1.7)
    A["PENGERING"] = (it["x0"] + .65, it["y0"] + 5.0, 2.7)
    c = L.character("own", "owner", (cx + 1.5, cy - .5, 0), -.2)
    L.pose(c, "point")
    c["body"].rotation_euler.z = .5
    cam, tgt = make_camera(lens=20, shift_y=.1)
    cam_keys(cam, tgt, [(1, (cx - 4.5, cy - 11.5, 6.6), (cx - 1.0, cy + 2.5, 1.3)),
                        (n, (cx - 3.5, cy - 10.0, 6.0), (cx - 1.0, cy + 2.5, 1.3))])


def l05(n, info, A, cx=500, cy=0):
    """'pelanggan bayar sendiri pakai koin atau QRIS' — pelanggan scan QR di kios, koin masuk slot."""
    it = L.interior_set("int", cx, cy)
    k = it["kiosk"]
    kx, ky = k.location[0], k.location[1]
    c = L.character("cust", "mahasiswa", (kx - .1, ky - 1.25, 0), math.pi, hold="phone")
    # koin besar meluncur ke slot
    mb = W.MB("coin")
    L.coin(mb, 0, 0, 0, 2.2)
    co = mb.build()
    fk = fr("L05", 15.6)
    fly(co, fk, fk + 12, (kx + 1.2, ky - .9, 2.2), (kx + .18, ky - .4, .42), arc=.6)
    key(co, "scale", fk + 10, (1, 1, 1))
    key(co, "scale", fk + 14, (.01, .01, .01))
    pop(co, fk - 4, 1.0)
    fq = fr("L05", 16.6)
    ok = H.text("lunas", "LUNAS", .2, "check", depth=.02, loc=(kx, ky - .36, 1.25), emission=1.5)
    pop(ok, fq + 6, 1.0)
    ck = L.checkmark("ck", (kx, ky - .5, 2.45), .35)
    pop(ck, fq + 8, 1.0)
    A["KOIN"] = (kx + .18, ky - .35, .45)
    A["QRIS"] = (kx, ky - .35, 1.6)
    cam, tgt = make_camera(lens=24, shift_y=.04)
    cam_keys(cam, tgt, [(1, (kx + 5.8, ky - 7.0, 3.2), (kx - .6, ky - .4, 1.2)),
                        (n, (kx + 5.0, ky - 6.2, 3.0), (kx - .6, ky - .4, 1.2))])


def l06(n, info, A, cx=700, cy=0):
    """'Nggak perlu kasir, nggak perlu nota tulis tangan' — laundry konvensional dicoret."""
    L.conventional_set("conv", cx, cy)
    x0, y0 = cx - 4.5, cy - 3.5
    kas = L.character("kasir", "staf", (x0 + 3.0, y0 + 3.9, 0), 0)
    L.pose(kas, "arms_fwd")
    cu = L.character("cust", "bapak", (x0 + 3.4, y0 + 1.2, 0), math.pi * .9, hold="basket")
    mb = W.MB("nota")
    mb.box(-.35, -.25, 0, .35, .25, .06, "paper_w")
    for j in range(4):
        mb.box(-.28, -.18 + j * .1, .06, .1 + .05 * (j % 2), -.15 + j * .1, .065, "lw_navy")
    mb.box(.15, -.3, .07, .55, -.26, .1, "kiosk")
    nota = mb.build((x0 + 1.9, y0 + 2.8, 1.12))
    nota.rotation_euler.z = .2
    f1 = fr("L06", 18.1)
    x1 = L.xmark("x1", (x0 + 3.0, y0 + 3.6, 3.4), .55)
    pop(x1, f1, 1.0)
    f2 = fr("L06", 19.5)
    x2 = L.xmark("x2", (x0 + 1.9, y0 + 2.6, 2.1), .4)
    pop(x2, f2, 1.0)
    A["KASIR"] = (x0 + 3.0, y0 + 3.9, 2.4)
    A["NOTA"] = (x0 + 1.9, y0 + 2.8, 1.2)
    cam, tgt = make_camera(lens=22, shift_y=.06)
    cam_keys(cam, tgt, [(1, (cx - 5.5, cy - 11, 5.6), (cx - .8, cy + .2, 1.5)),
                        (n, (cx - 4.2, cy - 9.8, 5.0), (cx - .8, cy + .2, 1.5))])


def l07(n, info, A, cx=500, cy=0):
    """'Setiap putaran mesin, tercatat otomatis' — drum berputar, data terkirim ke tablet pemilik."""
    it = L.interior_set("int", cx, cy)
    for k, d in enumerate(it["doors"]):
        dr = L.drum_clothes(f"drum{k}", d, 1.0, n=6, seed=k + 2)
        L.spin(dr, 1, n, turns_per_sec=.7 + .1 * (k % 3))
    o = L.character("own", "owner", (cx + 1.2, cy - 1.6, 0), -.25, hold="tablet")
    tab = (cx + 1.2 + .1, cy - 1.6 - .75, 1.55)
    rnd = random.Random(7)
    f_on = fr("L07", 21.3)
    for k in range(10):                      # paket data (kotak kecil berpendar) dari mesin ke tablet
        d = it["doors"][k % 6]
        mb = W.MB(f"pkt{k}")
        mb.boxc(0, 0, -.08, .16, .16, .16, "neon")
        ob = mb.build()
        ob.data.materials[0] = lp.mat("neon", emission=4.0)
        f0 = f_on + k * 9 + rnd.randint(0, 4)
        fly(ob, f0, f0 + 22, (d[0], d[1] - .1, d[2] + .9), tab, arc=1.2)
        key(ob, "scale", 1, (.01,) * 3)
        key(ob, "scale", max(1, f0 - 1), (.01,) * 3)
        key(ob, "scale", f0, (1,) * 3)
        key(ob, "scale", f0 + 21, (1,) * 3)
        key(ob, "scale", f0 + 23, (.01,) * 3)
    A["TABLET"] = (tab[0], tab[1], 2.0)
    A["MESIN"] = (it["doors"][1][0], it["doors"][1][1], 1.7)
    cam, tgt = make_camera(lens=20, shift_y=.26)
    cam_keys(cam, tgt, [(1, (cx - 1.5, cy - 11.5, 5.2), (cx - .5, cy + 2.0, 1.5)),
                        (n, (cx - .5, cy - 10.0, 4.8), (cx - .5, cy + 2.0, 1.5))])


def l08(n, info, A):
    """'Strategi pertama: pilih lokasi yang uangnya jelas datang dari mana' — aerial, pin & radius."""
    p = T.pin("pin", "lw_teal").build((LX, LY, L.Z + 13))
    p.scale = (3,) * 3
    pop(p, fr("L08", 27.3), 3.0)
    for k in range(3):
        r = ring(f"ring{k}", (LX, LY, L.Z + .3), 1.0, .08)
        f0 = fr("L08", 27.5) + k * 18
        key(r, "scale", 1, (.01,) * 3)
        key(r, "scale", f0, (.01,) * 3)
        key(r, "scale", f0 + 40, (30, 30, 1))
    A["LOKASI"] = (LX, LY, L.Z + 13 + 3 * 2.5)
    cam, tgt = make_camera(lens=30, shift_y=.1)
    tg = (0, -10, 0)
    cam_keys(cam, tgt, [(1, orbit(tg, -112, 30, 75), tg), (n, orbit(tg, -100, 46, 120), tg)])


ROUTES = {
    "KOS": [(0, -41.5), (0, -24), (0, -16)],
    "KOS2": [(-40.5, -8), (-24, -8), (-24, -20), (-4, -20), (-2, -16)],
    "APARTEMEN": [(40.5, -6), (24, -6), (24, -20), (4, -20), (2, -16)],
    "KANTOR": [(47, 41), (47, 24), (24, 24), (24, -20), (4, -20)],
}


def l09(n, info, A):
    """'Dekat kos, apartemen, atau kantor' — jalur pelanggan dari kos/apartemen/kantor ke laundry."""
    times = {"KOS": 30.4, "KOS2": 30.6, "APARTEMEN": 30.9, "KANTOR": 31.8}
    for nm, pts in ROUTES.items():
        f0 = fr("L09", times[nm])
        route_ribbon("rt_" + nm, pts, f0, f0 + 22, z=.45, width=.9)
        pn = T.pin("pin_" + nm, "lw_yellow" if nm != "KANTOR" else "c_sky").build((*pts[0], L.Z + 1))
        pop(pn, f0, 2.2)
    lp_ = T.pin("pinL", "lw_teal").build((LX, LY, L.Z + 13))
    lp_.scale = (3,) * 3
    for k in ("KOS", "KOS2", "APARTEMEN", "KANTOR"):
        x, y, z = info["anchors"][k]
        A[k] = (x, y, min(z, 14.0))               # titik label di badan gedung, bukan puncak menara
    x, y, _ = info["anchors"]["KANTOR2"]
    A["KANTOR"] = (x, y, 8.0)                      # menara kantor depan (yang belakang terlalu tinggi di layar)
    cam, tgt = make_camera(ortho=150, shift_y=.15)
    tg = (2, -2, 0)
    cam_keys(cam, tgt, [(1, orbit(tg, -125, 42, 400), tg), (n, orbit(tg, -132, 44, 400), tg)])
    key(cam.data, "ortho_scale", 1, 150)
    key(cam.data, "ortho_scale", n, 165)


def l10(n, info, A):
    """'Asal usul pelanggannya jelas. Jam ramainya juga jelas.' — anak kos jalan ke laundry bawa cucian."""
    ws = []
    for k, (look, hold, dx, delay) in enumerate((("mahasiswa", "basket", -.8, 1), ("hijab2", "basket", .9, 22),
                                                 ("pekerja", "basket", -.2, 46))):
        c = L.character(f"w{k}", look, (dx, -40.5, L.Z), 0, hold=hold)
        L.walk_to(c, [(dx, -40.5), (dx, -30), (dx * .6, -21), (dx * .4, -15.6)], delay, speed=2.6)
        ws.append(c)
    A["PELANGGAN"] = (ws[0]["body"], (0, 0, 2.8))
    traffic(n, n=3)
    cam, tgt = make_camera(lens=20, shift_y=.2)
    cam_keys(cam, tgt, [(1, (10.5, -15.5, 6.0), (-.5, -33, 1.6)), (n, (9.5, -17.5, 5.2), (-.5, -31, 1.6))])


def _money_base(cx=1000, cy=0):
    studio_money(cx, cy, 22)


def l11(n, info, A, cx=1000, cy=0):
    """'Satu mesin, 5 putaran sehari, 15 ribu per putaran.'"""
    _money_base(cx, cy)
    wm, drum, top = pedestal_washer("wm", (cx, cy + 1, 0), 1.4, spin_f=(1, n))
    pop(wm, fr("L11", 40.3), 1.0)
    pop(drum, fr("L11", 40.3), 1.0)
    f5 = fr("L11", 41.4)
    for k in range(5):
        a = math.radians(150 - k * 30)
        mb = W.MB(f"c{k}")
        L.coin(mb, 0, 0, 0, 3.0)
        ob = mb.build((cx + math.cos(a) * 2.6, cy + .6, top[2] + .8 + math.sin(a) * 1.4))
        pop(ob, f5 + k * 4, 1.0)
        t = H.text(f"ct{k}", str(k + 1), .32, "lw_navy", depth=.03, loc=(0, -.11, -.14))
        t.parent = ob
    tag = L.price_tag("tag", "Rp15rb", (cx + 2.9, cy - .2, 1.7), 1.0)
    pop(tag, fr("L11", 42.9), 1.0)
    A["PUTARAN"] = (cx, cy + .6, top[2] + 2.4)
    A["TARIF"] = (cx + 2.9, cy - .2, 2.3)
    cam, tgt = make_camera(lens=26, shift_y=.17)
    tg = (cx + .4, cy + .5, 2.4)
    cam_keys(cam, tgt, [(1, orbit(tg, -100, 12, 14), tg), (n, orbit(tg, -90, 10, 12.5), tg)])


def _coin_stack(name, loc, n_layers, f0, step=3, s=1.0):
    obs = []
    for k in range(n_layers):
        mb = W.MB(f"{name}{k}")
        H.money_bundle(mb, 0, 0, 0, s)
        ob = mb.build((loc[0], loc[1], loc[2] + k * .29 * s))
        ob.rotation_euler.z = math.pi / 2
        pop(ob, f0 + k * step, 1.0)
        obs.append(ob)
    return obs


def l12(n, info, A, cx=1000, cy=0):
    """'Berarti, 75 ribu per hari.' — 5 koin turun jadi tumpukan uang di samping mesin."""
    _money_base(cx, cy)
    wm, drum, top = pedestal_washer("wm", (cx, cy + 1, 0), 1.4, spin_f=(1, n))
    fs = fr("L12", 45.2)
    for k in range(5):
        a = math.radians(150 - k * 30)
        mb = W.MB(f"c{k}")
        L.coin(mb, 0, 0, 0, 3.0)
        ob = mb.build()
        p0 = (cx + math.cos(a) * 2.6, cy + .6, top[2] + .8 + math.sin(a) * 1.4)
        fly(ob, fs + k * 3, fs + k * 3 + 12, p0, (cx + 3.0, cy - .6, .5 + k * .3), arc=1.0)
        key(ob, "scale", fs + k * 3 + 11, (1, 1, 1))
        key(ob, "scale", fs + k * 3 + 14, (.01, .01, .01))
    _coin_stack("st", (cx + 3.0, cy - .6, 0), 5, fs + 12, step=3, s=1.1)
    A["HARI"] = (cx + 3.0, cy - .6, 1.9)
    cam, tgt = make_camera(lens=26, shift_y=.06)
    tg = (cx + 1.2, cy + .2, 2.0)
    cam_keys(cam, tgt, [(1, orbit(tg, -96, 13, 13.5), tg), (n, orbit(tg, -84, 12, 12.5), tg)])


def l13(n, info, A, cx=1000, cy=0):
    """'10 mesin, 750 ribu.' — 10 mesin berderet, masing-masing dengan tumpukan uangnya."""
    _money_base(cx, cy)
    f0 = fr("L13", 48.2)
    for k in range(10):
        i, j = k % 5, k // 5
        x, y = cx - 6.4 + i * 3.2, cy + 1.6 - j * 4.4
        mb = W.MB(f"wm{k}")
        L.washer(mb, 0, 0, 0, 1.1)
        ob = mb.build((x, y, 0))
        pop(ob, f0 + k * 2, 1.0)
        _coin_stack(f"s{k}_", (x + 1.25, y - .5, 0), 3, f0 + 6 + k * 2, step=2, s=.7)
    A["SEPULUH"] = (cx, cy + 1.6, 2.4)
    cam, tgt = make_camera(lens=24, shift_y=.08)
    tg = (cx, cy - .6, .8)
    cam_keys(cam, tgt, [(1, orbit(tg, -96, 24, 21), tg), (n, orbit(tg, -88, 28, 23), tg)])


def l14(n, info, A, cx=1000, cy=0):
    """'Kali 30 hari, 22,5 juta rupiah.' — kalender 30 hari, tiap hari tumpukan uang."""
    _money_base(cx, cy)
    f0 = fr("L14", 51.6)
    for d in range(30):
        i, j = d % 6, d // 6
        x, y = cx - 6.25 + i * 2.5, cy + 4.6 - j * 2.3
        mb = W.MB(f"tile{d}")
        L.rbox(mb, -1.05, -.95, 0, 1.05, .95, .12, "c_white", c=.15)
        mb.box(-1.05, .55, .12, 1.05, .95, .16, "news_red")
        ob = mb.build((x, y, 0))
        pop(ob, f0 + d, 1.0)
        t = H.text(f"dt{d}", str(d + 1), .38, "lw_navy", depth=.02, loc=(-.55, -.6, .13), rot=(0, 0, 0))
        t.parent = ob
        mb2 = W.MB(f"m{d}")
        for k in range(3):
            H.money_bundle(mb2, 0, 0, k * .29 * .6, .6)
        st = mb2.build((x + .25, y - .1, .12))
        st.rotation_euler.z = math.pi / 2
        pop(st, fr("L14", 53.0) + d, 1.0)
    A["BULAN"] = (cx, cy + 2.3, 1.2)
    cam, tgt = make_camera(lens=24, shift_y=.06)
    tg = (cx, cy - .2, 0)
    cam_keys(cam, tgt, [(1, orbit(tg, -96, 52, 26), tg), (n, orbit(tg, -88, 58, 24), tg)])


def l15(n, info, A, cx=1000, cy=0):
    """'Itu omzet kotor, belum listrik, air, sabun, dan sewa tempat.' — potongan biaya terbang dari tumpukan."""
    _money_base(cx, cy)
    H.money_pallet("pallet", 4, 3, 5, 1.0).build((cx, cy, 0))
    chips = (("LISTRIK", 57.7, (-3.6, -1.6, 3.9)), ("AIR", 58.8, (-2.4, -3.4, 1.2)),
             ("SABUN", 59.5, (2.6, -3.2, 1.2)), ("SEWA", 60.4, (3.6, -1.4, 3.9)))
    for k, (nm, src, d) in enumerate(chips):
        mb = W.MB(f"chip{k}")
        for j in range(2):
            H.money_bundle(mb, 0, 0, j * .29, .9)
        ob = mb.build()
        f0 = fr("L15", src)
        p1 = (cx + d[0], cy + d[1], d[2])
        fly(ob, f0, f0 + 12, (cx, cy, 1.8), p1, arc=1.5)
        A[nm] = (p1[0], p1[1], p1[2] + .7)
    A["KOTOR"] = (cx, cy, 2.0)
    cam, tgt = make_camera(lens=24, shift_y=.04)
    tg = (cx, cy - .8, 1.8)
    cam_keys(cam, tgt, [(1, orbit(tg, -98, 22, 23), tg), (n, orbit(tg, -88, 20, 21), tg)])


def l16(n, info, A):
    """'tambah unit, buka cabang, dan pasang sistem pembayaran digital' — cabang baru bermunculan."""
    for k, (ob, sg, (x, y, top)) in enumerate(info["branches"]):
        f = fr("L16", 64.9) + k * 6
        pop(ob, f, 1.0)
        for s_ in sg:
            visible_between(s_, f + 5)
        p = T.pin(f"bp{k}", "lw_teal").build((x, y, top + 2))
        p.scale = (2.2,) * 3
        pop(p, f + 6, 2.2)
        A[f"CAB{k}"] = (x, y, top + 8)
    A["UNIT"] = (LX, LY, L.Z + 11)
    A["DIGITAL"] = (LX + 5, LFRONT, L.Z + 6)
    cam, tgt = make_camera(ortho=110, shift_y=.08)
    tg = (2, -2, 0)
    cam_keys(cam, tgt, [(1, orbit(tg, -125, 42, 400), tg), (n, orbit(tg, -132, 44, 400), tg)])
    key(cam.data, "ortho_scale", 1, 110)
    key(cam.data, "ortho_scale", n, 165)


def l17(n, info, A, cx=1100, cy=0):
    """'Makin terbuka, makin gampang dipantau.' — pemilik memantau semua cabang dari tablet."""
    studio_floor(cx, cy, size=18, wall=False)
    o = L.character("own", "owner", (cx, cy - 2.2, 0), 0, hold="tablet")
    # layar dasbor melayang
    mb = W.MB("dash")
    L.rbox(mb, -3.2, -.1, 0, 3.2, .1, 3.4, "lw_navy", c=.2)
    mb.box(-3.0, -.12, .2, 3.0, -.1, 3.2, "kiosk_scr")
    dash = mb.build((cx, cy + 2.6, 2.2))
    pop(dash, 4, 1.0)
    for k, v in enumerate((.45, .6, .55, .8, .7, .95)):
        bm = W.MB(f"bar{k}")
        bm.box(-.3, -.05, 0, .3, .05, 2.4 * v, "lw_teal" if k < 5 else "check")
        bo = bm.build((cx - 2.4 + k * .95, cy + 2.45, 2.45))
        grow_z(bo, 10 + k * 4, 22 + k * 4)
    minis = []
    for k, (dx, dy, rot) in enumerate(((-6.0, 1.5, .5), (6.0, 1.5, -.5), (0, 6.5, 0))):
        m, top = L.laundromat(f"mini{k}", interior=True)
        ob = m.build((cx + dx, cy + dy, -L.Z * .22), rot)
        ob.scale = (.22,) * 3
        pop(ob, 6 + k * 5, .22)
        minis.append((cx + dx, cy + dy, top * .22))
        route_ribbon(f"ln{k}", [(cx + dx, cy + dy - .6), (cx + dx * .4, cy + 1.6), (cx, cy - 1.4)], 20 + k * 6,
                     40 + k * 6, z=.12, width=.18)
    A["PANTAU"] = (cx, cy + 2.6, 5.7)
    A["TABLET"] = (cx, cy - 2.95, 2.0)
    cam, tgt = make_camera(lens=24, shift_y=.05)
    tg = (cx, cy + 1.2, 2.4)
    cam_keys(cam, tgt, [(1, orbit(tg, -96, 16, 18), tg), (n, orbit(tg, -88, 14, 16.5), tg)])


def l18(n, info, A, cx=1200, cy=0):
    """'uangnya masuk lewat mesin, bukan lewat pintu belakang'."""
    studio_floor(cx, cy, size=16, wall=False)
    k = L.kiosk("kiosk", 1.5)
    k.location = (cx - 2.4, cy, 0)
    mb = W.MB("coin")
    L.coin(mb, 0, 0, 0, 3.0)
    co = mb.build()
    f1 = fr("L18", 73.5)
    fly(co, f1, f1 + 14, (cx - 4.2, cy - 1.2, 4.0), (cx - 2.4 + .27, cy - .5, .62), arc=.8)
    key(co, "scale", f1 + 12, (1, 1, 1))
    key(co, "scale", f1 + 16, (.01, .01, .01))
    pop(co, f1 - 4, 1.0)
    ck = L.checkmark("ck", (cx - 2.4, cy - .6, 3.4), .55)
    pop(ck, f1 + 16, 1.0)
    # dinding belakang gedung dengan pintu belakang
    wb = W.MB("backwall")
    wb.box(-2.2, -.2, 0, 2.6, .2, 4.2, "lw_wall")
    wb.box(-2.2, -.22, 0, 2.6, -.2, .9, "lw_teal")
    wb.box(-.7, -.28, 0, .9, -.18, 2.6, "kos_door")
    wb.box(.6, -.36, 1.2, .72, -.28, 1.5, "metal")
    wb.box(-1.0, -.6, 2.6, 1.2, -.2, 2.75, "lw_frame")
    wb.cyl(1.9, -.6, 0, 1.0, .45, "c_grey", n=10)                  # tong sampah
    wb.build((cx + 2.6, cy + 1.2, 0))
    x = L.xmark("x", (cx + 2.7, cy + .7, 1.5), .75)
    pop(x, fr("L18", 75.3), 1.0)
    A["MESIN"] = (cx - 2.4, cy - .45, 2.2)
    A["PINTU"] = (cx + 2.7, cy + 1.0, 2.7)
    cam, tgt = make_camera(lens=24, shift_y=.04)
    tg = (cx, cy + .3, 1.8)
    cam_keys(cam, tgt, [(1, orbit(tg, -95, 10, 14), tg), (n, orbit(tg, -89, 9, 13), tg)])


def l19(n, info, A, cx=900, cy=0):
    """'Yang butuh dicuci cuma bajunya, bukan asal usul uangnya.'"""
    studio_floor(cx, cy, size=16, wall=False)
    wm, drum, top = pedestal_washer("wm", (cx - 2.3, cy, 0), 1.4, spin_f=(1, n))
    doc = L.report_doc("doc", 1.0).build((cx + 2.4, cy + .4, 0), -.25)
    t = H.text("doc_t", "LAPORAN KEUANGAN", .17, "lw_navy", depth=.02, loc=(0, -.12, 2.4))
    t.parent = doc
    st = L.money_stack("ms", 8, 1.6).build((cx + .7, cy - 1.2, 0))
    ck = L.checkmark("ck", (cx + 2.4, cy - .5, 3.6), .5)
    f2 = fr("L19", 79.5)
    pop(ck, f2 + 4, 1.0)
    for k, (dx, dz) in enumerate(((1.4, 3.1), (3.4, 2.6), (2.4, 3.9))):
        sp = L.sparkle(f"sp{k}", (cx + dx, cy - .8, dz), .32)
        pop(sp, f2 + 6 + k * 3, 1.0)
    A["BAJU"] = (cx - 2.3, cy - .9, 1.9)
    A["JELAS"] = (cx + 2.4, cy + .2, 3.1)
    cam, tgt = make_camera(lens=24, shift_y=.04)
    tg = (cx, cy + .2, 1.8)
    cam_keys(cam, tgt, [(1, orbit(tg, -96, 10, 13.5), tg), (n, orbit(tg, -88, 9, 12.5), tg)])


def l20(n, info, A):
    """'Menurut kamu ... Tulis di komentar. Follow ...' — kota diorama (ortografis) + CTA."""
    cam, tgt = make_camera(ortho=130, shift_y=.12)
    tg = (0, -2, 0)
    cam_keys(cam, tgt, [(1, orbit(tg, -128, 36, 400), tg), (n, orbit(tg, -140, 36, 400), tg)])
    key(cam.data, "ortho_scale", 1, 130)
    key(cam.data, "ortho_scale", n, 220)
    key(cam.data, "shift_y", 1, .12)
    key(cam.data, "shift_y", n, .16)
    A["LAUNDRY"] = info["anchors"]["LAUNDRY"]


SCENES = {f"L{k:02d}": fn for k, fn in enumerate(
    (l01, l02, l03, l04, l05, l06, l07, l08, l09, l10, l11, l12, l13, l14, l15, l16, l17, l18, l19, l20), 1)}
STUDIO = {"L01", "L03", "L04", "L05", "L06", "L07", "L11", "L12", "L13", "L14", "L15", "L17", "L18", "L19"}
BRANCHES = {"L16", "L20"}
NO_PEOPLE = {"L08", "L09", "L16"}


def _anchor_pos(p):
    if isinstance(p, tuple) and len(p) == 2 and hasattr(p[0], "matrix_world"):
        ob, off = p
        return ob.matrix_world.translation + Vector(off)
    return Vector(p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--res", default="720x1280")
    ap.add_argument("--samples", type=int, default=4)
    ap.add_argument("--frames", default=None)
    args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])

    t0, t1, gf0, n = scene_range(args.scene)
    lp.reset()
    W.PLACED.clear()
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
    rx, ry = map(int, args.res.split("x"))
    lp.setup_render(rx, ry, args.samples)
    W.setup_world_light()
    H.glassy("wm_glass", .45)
    H.glassy("lw_glass", .35)
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, n
    info = {"people": [], "walkers": []}
    if args.scene not in STUDIO:
        info = L.build_world(people=args.scene not in NO_PEOPLE, branches=args.scene in BRANCHES)
        L.animate_walkers(info, n)
    A = {}
    SCENES[args.scene](n, info, A)
    cam = sc.camera

    os.makedirs(os.path.join(args.out, "frames"), exist_ok=True)
    data = {"scene": args.scene, "t0": t0, "t1": t1, "global_f0": gf0, "n": n, "fps": FPS, "res": [rx, ry],
            "frames": {}}
    for f in range(1, n + 1):
        sc.frame_set(f)
        pos = {}
        for name, p in A.items():
            v = world_to_camera_view(sc, cam, _anchor_pos(p))
            if v.z > 0:
                pos[name] = [round(v.x * rx, 1), round((1 - v.y) * ry, 1)]
        data["frames"][f] = pos
    with open(os.path.join(args.out, "anchors.json"), "w") as fh:
        json.dump(data, fh)

    lo, hi = (1, n) if not args.frames else map(int, args.frames.split("-"))
    for f in range(lo, hi + 1):
        path = os.path.join(args.out, "frames", f"{f:04d}.png")
        if os.path.exists(path) and not args.frames:
            continue
        sc.frame_set(f)
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
    print("DONE", args.scene, n)


if __name__ == "__main__":
    main()
