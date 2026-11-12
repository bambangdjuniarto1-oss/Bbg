"""22 adegan video "Bedah Bisnis AMDK" (timeline mengikuti VO hasil humanize_vo.py, ±82,9 dtk).

  python3 render/scenes_amdk.py -- --scene A01 --out OUT/A01 [--res 720x1280] [--samples 4] [--frames a-b]

Isi VO: hook (produk murah, dibeli jutaan kali) -> peluang skala nasional -> model bisnis (pabrik + brand,
4 produk, target 1.000 distributor) -> asumsi order per distributor -> harga jual -> omzet per produk
(9,6 + 12,96 + 7,2 + 7,5 = Rp37,26 M/bulan) -> HPP 30,98 M -> margin 6,28 M -> opex 4 M -> laba 2,28 M ->
syarat (pabrik besar, logistik nasional, distributor aktif) -> tantangan: pasar terus membeli -> CTA.
Waktu (detik) di sini = timeline video (sudah dipercepat), sama dengan render/scenes/amdk_words.json.
"""
import argparse
import json
import math
import os
import random
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowpoly as lp  # noqa: E402
import world as W  # noqa: E402
import world_hotel as H  # noqa: E402
import world_laundry as L  # noqa: E402
import world_amdk as M  # noqa: E402
from scenes import key, make_camera, cam_keys, orbit, route_ribbon  # noqa: E402
from scenes_laundry import pop, grow_z, fly, emission_ramp, ring, _anchor_pos  # noqa: E402

FPS = 30
TIMELINE = [("A01", 0.00), ("A02", 4.27), ("A03", 8.78), ("A04", 10.85), ("A05", 13.20), ("A06", 19.26),
            ("A07", 21.48), ("A08", 25.65), ("A09", 28.84), ("A10", 34.61), ("A11", 40.31), ("A12", 48.52),
            ("A13", 50.60), ("A14", 56.65), ("A15", 63.61), ("A16", 69.04), ("A17", 71.74), ("A18", 77.32),
            ("A19", 83.27), ("A20", 86.89), ("A21", 90.83), ("A22", 95.58)]
END_T = 102.24


def scene_range(sid):
    ids = [s for s, _ in TIMELINE]
    i = ids.index(sid)
    t0 = TIMELINE[i][1]
    t1 = TIMELINE[i + 1][1] if i + 1 < len(TIMELINE) else END_T
    f0, f1 = round(t0 * FPS), round(t1 * FPS)
    return t0, t1, f0, f1 - f0


def fr(sid, t):
    """frame lokal adegan untuk detik `t` di timeline video."""
    return max(1, int((t - dict(TIMELINE)[sid]) * FPS) + 1)


def tower(name, layers, loc, nx=2, ny=2, key_="money_red", s=1.0):
    """tumpukan uang setinggi `layers` lapis (1 lapis = .29*s)."""
    mb = W.MB(name)
    for k in range(layers):
        for i in range(nx):
            for j in range(ny):
                H.money_bundle(mb, (i - (nx - 1) / 2) * 1.68 * s, (j - (ny - 1) / 2) * .82 * s, k * .29 * s, s,
                               key=key_)
    return mb.build(loc)


def sparkles(prefix, center, f0, n=4, r=1.6, s=.35, seed=1):
    rnd = random.Random(seed)
    for k in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        p = (center[0] + math.cos(a) * r, center[1] - .5, center[2] + math.sin(a) * r * .8)
        sp = L.sparkle(f"{prefix}{k}", p, s * rnd.uniform(.8, 1.2))
        pop(sp, f0 + k * 3, 1.0)


def ped_product(name, kind, loc, s=1.0, f=None, key_="br_blue"):
    pd = M.pedestal(name + "_pd", 1.35 if kind != "galon" else 1.6, key_).build(loc)
    pr = M.product(name, kind, s).build((loc[0], loc[1], loc[2] + .42))
    if f is not None:
        pop(pd, f, 1.0)
        pop(pr, f + 2, 1.0)
    return pd, pr


def spin_z(ob, f0, f1, turns):
    key(ob, "rotation_euler", f0, (0, 0, ob.rotation_euler.z))
    key(ob, "rotation_euler", f1, (0, 0, ob.rotation_euler.z + 2 * math.pi * turns))


# ------------------------------------------------------------------ adegan
def a01(n, info, A):
    """hook: 'produk yang tiap hari kita minum, murah, tapi dibeli jutaan kali' — air gelas raksasa + gelas
    berlipat ganda di sekelilingnya."""
    M.studio_epoxy(0, 0, size=16)
    pd = M.pedestal("pd", 2.2).build((0, 0, 0))
    big = M.product("big", "cup", 3.2).build((0, 0, .42))
    pop(pd, 2, 1.0)
    pop(big, 5, 1.0)
    spin_z(big, 1, n, .25)
    rnd = random.Random(4)
    f_j = fr("A01", 2.51)
    k = 0
    for ring_i, (r, cnt) in enumerate(((4.4, 10), (6.4, 16), (8.6, 22))):
        for j in range(cnt):
            a = 2 * math.pi * j / cnt + ring_i * .2
            x, y = r * math.cos(a), r * math.sin(a) + 1.5
            kind = ("cup", "cup", "b600", "b1500")[rnd.randrange(4)] if ring_i else "cup"
            pr = M.product(f"m{k}", kind, rnd.uniform(.8, 1.0)).build((x, y, 0))
            pop(pr, f_j + ring_i * 6 + j // 3, 1.0)
            k += 1
    A["GELAS"] = (0, 0, 3.6)
    A["JUTAAN"] = (5.5, -1.0, 1.6)
    cam, tgt = make_camera(lens=24, shift_y=.1)
    tg = (0, 1.0, 1.6)
    cam_keys(cam, tgt, [(1, orbit(tg, -100, 18, 12.5), tg), (n, orbit(tg, -80, 30, 21.0), tg)])


def _map_base(n, A, pins=0, seed=3, pin_f0=None, pin_f1=None):
    mo, polys = M.indonesia_map("map", 0, 0)
    out = []
    if pins:
        pts = M.map_points(polys, pins, seed)
        for k, p in enumerate(pts):
            pn = M.pin(f"pin{k}", (p[0], p[1], 1.0), .75, "pin_b" if k % 5 else "pin_o")
            if pin_f0 is not None:
                f = pin_f0 + int((pin_f1 - pin_f0) * k / max(1, pins - 1))
                pop(pn, f, 1.0)
            out.append(pn)
    return polys, out


def a02(n, info, A):
    """'di balik produk sederhana ini ada peluang bisnis berskala nasional' — peta Indonesia, gelombang
    peluang menyebar dari Jawa."""
    polys, _ = _map_base(n, A)
    jx, jy = M.map_xy(107.5, -6.9)
    for k in range(4):
        rg = ring(f"rg{k}", (jx, jy, 1.15), 2.0, .5, "br_aqua", em=1.5)
        f0 = fr("A02", 6.15) + k * 12
        key(rg, "scale", 1, (.01,) * 3)
        key(rg, "scale", f0, (.01,) * 3)
        key(rg, "scale", f0 + 40, (7,) * 3)
    big = M.product("cup", "cup", 2.2).build((jx, jy - 1.0, 1.0))
    pop(big, 3, 1.0)
    for k, (nm, (lo, la)) in enumerate(M.CITIES.items()):
        if k % 2:
            continue
        x, y = M.map_xy(lo, la)
        pn = M.pin(f"cp{k}", (x, y, 1.0), 1.0, "pin_o")
        pop(pn, fr("A02", 7.28) + k, 1.0)
    A["NASIONAL"] = (M.map_xy(116, 1)[0], M.map_xy(116, 1)[1], 3.0)
    cam, tgt = make_camera(lens=24, shift_y=.16)
    cam_keys(cam, tgt, [(1, (jx - 30, jy - 26, 16), (jx + 6, jy + 4, 0)),
                        (n, (-62, -44, 30), (6, 2, 0))])


def a03(n, info, A):
    """'Kita bicara bisnis air minum dalam kemasan.' — terbang ke pabrik AMDK, papan merek menyala."""
    for ob in info.get("fsign", []):
        emission_ramp(ob.data.materials[0], [(1, 0.0), (fr("A03", 9.53), 0.0), (fr("A03", 10.04), 2.0)])
    M.road_trucks(n)
    A["PABRIK"] = info["anchors"]["PABRIK"]
    cam, tgt = make_camera(lens=22, shift_y=.12)
    cam_keys(cam, tgt, [(1, (-48, -86, 60), (-2, -6, 4)), (n, (-30, -58, 30), (-3, -6, 5))])


def a04(n, info, A):
    """'Bayangkan kamu bangun perusahaan dengan pabrik dan brand sendiri.' — depan pabrik: manajer
    melambai, karyawan, forklift berjalan, tronton keluar gerbang."""
    for ob in info.get("fsign", []):
        emission_ramp(ob.data.materials[0], [(1, 1.0), (fr("A04", 12.80), 1.0), (fr("A04", 13.17), 4.0),
                                             (fr("A04", 13.17) + 8, 2.0)])
    mgr = info["workers"][5]
    L.pose(mgr, "stand", 1)
    L.pose(mgr, "wave", fr("A04", 11.54))
    fl = info["forklift"]
    key(fl, "location", 1, tuple(fl.location))
    key(fl, "location", n, (fl.location.x + 4.5, fl.location.y, fl.location.z))
    tr = M.tronton("out", "box")
    tr.rotation_euler.z = 0
    key(tr, "location", 1, (-4, -19.5, .05))
    key(tr, "location", n, (14, -19.5, .05))
    A["PABRIK"] = (-8.25, -11.2, 10.5)
    A["BRAND"] = (tr, (-2.4, -1.5, 4.8))
    cam, tgt = make_camera(lens=20, shift_y=.14)
    cam_keys(cam, tgt, [(1, (-24, -40, 9), (-6, -8, 5.5)), (n, (-17, -36, 7.5), (-5, -8, 5.2))])


def a05(n, info, A):
    """'Empat produk: air gelas, botol 600 ml, botol 1.500 ml, dan galon.' — 4 pedestal muncul berurutan."""
    M.studio_epoxy(0, 0, size=16)
    items = (("cup", 14.00, 1.6, "GELAS"), ("b600", 14.62, 1.15, "B600"), ("b1500", 16.00, 1.15, "B1500"),
             ("galon", 17.94, .95, "GALON"))
    for k, (kind, t, s, nm) in enumerate(items):
        x = -5.4 + k * 3.6
        ped_product(f"p{k}", kind, (x, 0, 0), s, fr("A05", t) - 3)
        top = {"cup": 1.5, "b600": 2.6, "b1500": 3.0, "galon": 3.5}[kind]
        A[nm] = (x, 0, .42 + top + .3)
    cam, tgt = make_camera(lens=26, shift_y=.08)
    tg = (0, 0, 1.8)
    cam_keys(cam, tgt, [(1, orbit(tg, -98, 12, 28), tg), (n, orbit(tg, -86, 14, 26), tg)])


def a06(n, info, A):
    """'Targetnya bukan cuma masuk minimarket,' — tronton menurunkan karton di minimarket."""
    mx, my = M.MM_C
    tr = M.tronton("drop", "carton")
    tr.rotation_euler.z = math.pi / 2
    tr.location = (mx + 14.5, my - 1.0, .05)
    key(tr, "location", 1, (mx + 14.5, my - 14, .05))
    key(tr, "location", int(n * .55), (mx + 14.5, my - 1.0, .05))
    wk = M.worker("crr", "buruh", (mx + 11.5, my + 2.2, M.Z), math.pi / 2, hold="carton")
    L.walk_to(wk, [(mx + 11.5, my + 2.2), (mx + 7.2, my + 2.2)], int(n * .5), speed=1.6)
    A["MINIMARKET"] = (mx + 4.5, my, 6.5)
    cam, tgt = make_camera(lens=22, shift_y=.12)
    cam_keys(cam, tgt, [(1, (mx + 27, my - 20, 11), (mx + 4, my, 3.2)), (n, (mx + 24, my - 16, 9), (mx + 4, my, 3.0))])


def a07(n, info, A):
    """'...tapi membangun jaringan 1.000 distributor di seluruh Indonesia.' — pin distributor bermunculan."""
    polys, pins = _map_base(n, A, 160, 3, fr("A07", 22.46), fr("A07", 24.97))
    A["JAWA"] = (M.map_xy(110.5, -7.4)[0], M.map_xy(110.5, -7.4)[1], 2.5)
    A["SUMATRA"] = (M.map_xy(101.5, -.5)[0], M.map_xy(101.5, -.5)[1], 2.5)
    A["SULAWESI"] = (M.map_xy(120.5, -2.5)[0], M.map_xy(120.5, -2.5)[1], 2.5)
    cam, tgt = make_camera(lens=24, shift_y=.16)
    cam_keys(cam, tgt, [(1, (-66, -40, 30), (4, 2, 0)), (n, (-60, -50, 36), (8, 2, 0))])


def a08(n, info, A):
    """'Sekarang kita hitung. Asumsikan tiap distributor beli per bulan,' — gudang distributor, tronton
    datang, buruh memanggul karton."""
    gx, gy = M.DIST_C
    tr = M.tronton("in", "box")
    tr.rotation_euler.z = math.pi
    key(tr, "location", 1, (gx + 26, gy + 14.5, .05))
    key(tr, "location", int(n * .7), (gx + 3, gy + 14.5, .05))
    for k, (dx, d0) in enumerate(((-4.5, 1), (-2.5, 20))):
        wk = M.worker(f"cr{k}", "buruh" if k == 0 else "buruh2", (gx + dx, gy + 10, M.Z), math.pi, hold="carton")
        L.walk_to(wk, [(gx + dx, gy + 10.5), (gx + dx, gy + 7.2)], d0, speed=1.4)
    A["GUDANG"] = (gx, gy + 6, 8.0)
    cam, tgt = make_camera(lens=22, shift_y=.12)
    cam_keys(cam, tgt, [(1, (gx + 20, gy + 36, 12), (gx + 1, gy + 4, 3.0)), (n, (gx + 16, gy + 32, 10), (gx + 1, gy + 5, 3))])


def _order_stack(prefix, kind, loc, layers, f0, nx=2, ny=2, prod_s=1.0):
    """tumpukan karton yang tumbuh + produk contoh di atasnya."""
    mb = W.MB(prefix)
    M.carton_stack(mb, 0, 0, 0, nx, ny, layers, 1.5, 1.1, .85, kind="cup" if kind == "cup" else "bottle")
    ob = mb.build(loc)
    grow_z(ob, f0, f0 + 14)
    top = .26 + layers * .85
    pr = M.product(prefix + "_p", kind, prod_s).build((loc[0], loc[1], loc[2] + top))
    pop(pr, f0 + 12, 1.0)
    return top


def a09(n, info, A):
    """'500 karton air gelas isi 48, 300 karton botol 600 ml isi 24,' — karton menumpuk (gudang)."""
    M.studio_epoxy(0, 0, size=16, wall=True)
    t1 = _order_stack("s0", "cup", (-3.0, 0, 0), 5, fr("A09", 29.05), prod_s=1.3)
    t2 = _order_stack("s1", "b600", (3.0, 0, 0), 3, fr("A09", 31.50), prod_s=.85)
    A["GELAS"] = (-3.0, 0, t1 + 1.6)
    A["B600"] = (3.0, 0, t2 + 2.4)
    w = M.worker("op", "buruh", (0, -2.2, 0), .2)
    L.pose(w, "point", fr("A09", 31.72))
    cam, tgt = make_camera(lens=26, shift_y=.24)
    tg = (0, 0, 2.2)
    cam_keys(cam, tgt, [(1, orbit(tg, -104, 14, 20), tg), (n, orbit(tg, -94, 16, 18.5), tg)])


def a10(n, info, A):
    """'200 karton botol 1.500 ml isi 12, dan 500 galon isi ulang.' — tumpukan karton & rak galon, forklift."""
    M.studio_epoxy(0, 0, size=16, wall=True)
    t1 = _order_stack("s2", "b1500", (-3.4, 0, 0), 2, fr("A10", 34.86), prod_s=.8)
    mb = W.MB("gr")
    for i in range(2):
        M.galon_rack(mb, 3.6 + (i - .5) * 0, -0.6 + i * 1.6, 0, 3, 2, .62)
    gr = mb.build()
    grow_z(gr, fr("A10", 38.30), fr("A10", 38.30) + 14)
    A["B1500"] = (-3.4, 0, t1 + 2.6)
    A["GALON"] = (3.6, 0, 4.9)
    fl = M.forklift("fl")
    fl.rotation_euler.z = math.pi
    key(fl, "location", 1, (12, -4.2, 0))
    key(fl, "location", n, (2.0, -4.2, 0))
    cam, tgt = make_camera(lens=26, shift_y=.24)
    tg = (0, 0, 2.2)
    cam_keys(cam, tgt, [(1, orbit(tg, -86, 14, 19), tg), (n, orbit(tg, -96, 16, 18.5), tg)])


def _four(prefix, f_list=None, gap=3.6, z=0.0):
    out = []
    for k, (kind, s) in enumerate((("cup", 1.6), ("b600", 1.15), ("b1500", 1.15), ("galon", .95))):
        x = (k - 1.5) * gap
        f = f_list[k] if f_list else None
        ped_product(f"{prefix}{k}", kind, (x, 0, z), s, f)
        out.append((x, {"cup": 1.5, "b600": 2.6, "b1500": 3.0, "galon": 3.5}[kind] + .42))
    return out


def a11(n, info, A):
    """'Harga jual ke distributor: 400/gelas, 1.800, 3.000, Rp15.000/galon' — label harga muncul."""
    M.studio_epoxy(0, 0, size=16)
    pos = _four("p", [2, 4, 6, 8])
    for k, (txt, t) in enumerate((("Rp400", 42.11), ("Rp1.800", 43.72), ("Rp3.000", 45.68), ("Rp15.000", 46.87))):
        x, top = pos[k]
        tg = L.price_tag(f"tag{k}", txt, (x, -.6, top + .9), .55)
        pop(tg, fr("A11", t), 1.0)
        A[f"H{k}"] = (x, -.6, top + 1.3)
    cam, tgt = make_camera(lens=26, shift_y=.26)
    tg = (0, 0, 2.0)
    cam_keys(cam, tgt, [(1, orbit(tg, -95, 12, 28), tg), (n, orbit(tg, -87, 13, 26), tg)])


def a12(n, info, A):
    """'Kalikan 1.000 distributor,' — ratusan gudang mini muncul bergelombang."""
    M.studio_epoxy(0, 0, size=26)
    f0 = 3
    for i in range(16):
        for j in range(12):
            x, y = (i - 7.5) * 2.6, (j - 3) * 2.4
            mb = W.MB(f"wh{i}_{j}")
            mb.box(-1, -.8, 0, 1, .8, 1.0, "wh_wall")
            mb.prism_x([(-.95, 1.0), (.95, 1.0), (0, 1.6)], -1.1, 1.1, "wh_roof")
            mb.box(-.5, -.82, 0, .5, -.78, .7, "rolldoor")
            mb.box(-.7, -.84, .78, .7, -.8, .95, "br_blue")
            ob = mb.build((x, y, 0))
            d = math.hypot(i - 7.5, j + 2)
            pop(ob, f0 + int(d * 2.2), 1.0)
    A["DIST"] = (0, -7.2, 2.0)
    cam, tgt = make_camera(lens=24, shift_y=.12)
    tg = (0, 4, 0)
    cam_keys(cam, tgt, [(1, orbit(tg, -90, 30, 26), tg), (n, orbit(tg, -90, 42, 44), tg)])


MONEY_LAYERS = {"cup": 10, "b600": 13, "b1500": 7, "galon": 8}     # ±1 lapis per Rp1 M


def _towers(prefix, grow=None, gap=3.6):
    """4 produk + menara uang di belakangnya. grow: {indeks: frame mulai tumbuh} (None = sudah penuh)."""
    pos = _four(prefix, None, gap)
    tops = []
    for k, kind in enumerate(("cup", "b600", "b1500", "galon")):
        x = pos[k][0]
        lay = MONEY_LAYERS[kind]
        tw = tower(f"{prefix}tw{k}", lay, (x, 2.6, 0), 2, 2, s=.95)
        if grow is not None:
            if k in grow:
                grow_z(tw, grow[k], grow[k] + 18)
            else:
                tw.scale = (1, 1, .001)
        tops.append((x, 2.6, lay * .29 * .95))
    return tops


def a13(n, info, A):
    """'air gelas 9,6 miliar, botol 600 ml 12,96 miliar,' — menara uang tumbuh di belakang produk."""
    M.studio_epoxy(0, 0, size=18)
    tops = _towers("t", {0: fr("A13", 51.46), 1: fr("A13", 54.39)})
    A["O0"] = (tops[0][0], tops[0][1], tops[0][2] + .3)
    A["O1"] = (tops[1][0], tops[1][1], tops[1][2] + .3)
    cam, tgt = make_camera(lens=26, shift_y=.1)
    cam_keys(cam, tgt, [(1, (-6.5, -17, 6), (-3.6, 1, 2.6)), (n, (-4.0, -18, 7), (-1.8, 1, 2.8))])


def a14(n, info, A):
    """'botol 1.500 ml 7,2 miliar, galon 7,5 miliar.' — menara 1-2 sudah penuh, 3-4 tumbuh."""
    M.studio_epoxy(0, 0, size=18)
    pos = _four("t", None)
    tops = []
    for k, kind in enumerate(("cup", "b600", "b1500", "galon")):
        x = pos[k][0]
        lay = MONEY_LAYERS[kind]
        tw = tower(f"tw{k}", lay, (x, 2.6, 0), 2, 2, s=.95)
        if k == 2:
            grow_z(tw, fr("A14", 58.54), fr("A14", 58.54) + 18)
        if k == 3:
            grow_z(tw, fr("A14", 61.16), fr("A14", 61.16) + 18)
        tops.append((x, 2.6, lay * .29 * .95))
    A["O2"] = (tops[2][0], tops[2][1], tops[2][2] + .3)
    A["O3"] = (tops[3][0], tops[3][1], tops[3][2] + .3)
    cam, tgt = make_camera(lens=26, shift_y=.1)
    cam_keys(cam, tgt, [(1, (1.5, -18, 7), (1.8, 1, 2.8)), (n, (4.5, -17, 6), (3.6, 1, 2.6))])


def a15(n, info, A):
    """'Totalnya 37,26 miliar rupiah per bulan.' — keempat menara + kilau, kamera mundur lebar."""
    M.studio_epoxy(0, 0, size=18)
    tops = _towers("t", None)
    f0 = fr("A15", 64.64)
    for k, (x, y, z) in enumerate(tops):
        sparkles(f"sp{k}_", (x, y, z + .6), f0 + k * 4, 3, 1.3, .32, seed=k)
    A["TOTAL"] = (0, 2.6, 4.6)
    cam, tgt = make_camera(lens=26, shift_y=.1)
    tg = (0, 1.2, 2.4)
    cam_keys(cam, tgt, [(1, orbit(tg, -90, 12, 25), tg), (n, orbit(tg, -90, 22, 32), tg)])


def a16(n, info, A):
    """'Tapi, omzet bukan keuntungan.' — menara OMZET besar  ≠  tumpukan UNTUNG kecil."""
    M.studio_epoxy(0, 0, size=16)
    pd1 = M.pedestal("pa", 2.4).build((-3.4, 0, 0))
    tw = tower("om", 30, (-3.4, 0, .42), 2, 2, s=.95)
    pd2 = M.pedestal("pb", 2.0, "check").build((3.4, 0, 0))
    sm = tower("un", 3, (3.4, 0, .42), 2, 2, key_="money_g", s=.95)
    pop(pd2, fr("A16", 70.02), 1.0)
    pop(sm, fr("A16", 70.14), 1.0)
    mb = W.MB("ne")                                       # tanda "tidak sama dengan"
    for dz in (-.32, .32):
        mb.box(-.9, -.15, dz - .13, .9, .15, dz + .13, "xred")
    mb.prism_y([(.25, 1.0), (.55, 1.0), (-.25, -1.0), (-.55, -1.0)], -.18, .18, "xred")
    ne = mb.build((0, -.3, 3.4))
    ne.data.materials[0] = lp.mat("xred", emission=.5)
    pop(ne, fr("A16", 70.27), 1.0)
    A["OMZET"] = (-3.4, 0, 9.2)
    A["UNTUNG"] = (3.4, 0, 1.9)
    cam, tgt = make_camera(lens=26, shift_y=.2)
    tg = (0, 0, 3.6)
    cam_keys(cam, tgt, [(1, orbit(tg, -92, 10, 24), tg), (n, orbit(tg, -88, 12, 22), tg)])


HPP_L, OPS_L, LABA_L = 31, 4, 2


def a17(n, info, A):
    """'Dengan total HPP 30,98 miliar, margin kotornya sekitar 6,28 miliar.' — bagian HPP lepas dari menara."""
    M.studio_epoxy(0, 0, size=18)
    M.pedestal("pa", 2.4).build((-3.0, 0, 0))
    lh = .29 * .95
    base = tower("mg", OPS_L + LABA_L, (-3.0, 0, .42), 2, 2, s=.95)
    hpp = tower("hpp", HPP_L, (-3.0, 0, .42 + (OPS_L + LABA_L) * lh), 2, 2, s=.95)
    f0 = fr("A17", 72.54)
    p0 = tuple(hpp.location)
    key(hpp, "location", 1, p0)
    key(hpp, "location", f0, p0)
    key(hpp, "location", f0 + 10, (p0[0], p0[1], p0[2] + 1.2))
    key(hpp, "location", f0 + 26, (4.2, 2.0, .42))
    M.pedestal("pb", 2.4, "c_grey").build((4.2, 2.0, 0))
    A["HPP"] = (hpp, (0, 0, HPP_L * lh + .3))
    A["MARGIN"] = (-3.0, 0, .42 + (OPS_L + LABA_L) * lh + .4)
    cam, tgt = make_camera(lens=26, shift_y=.1)
    cam_keys(cam, tgt, [(1, (0, -22, 7), (0, 0, 4.0)), (n, (1.0, -24, 7.5), (1.0, 0, 3.8))])


def a18(n, info, A):
    """'Dikurangi biaya operasional 4 miliar, tersisa laba operasional sekitar 2,28 miliar per bulan.'"""
    M.studio_epoxy(0, 0, size=18)
    lh = .29 * .95
    M.pedestal("pa", 2.4).build((-1.0, 0, 0))
    laba = tower("laba", LABA_L, (-1.0, 0, .42), 2, 2, key_="money_g", s=.95)
    ops = tower("ops", OPS_L, (-1.0, 0, .42 + LABA_L * lh), 2, 2, s=.95)
    M.pedestal("pb", 2.4, "c_grey").build((6.2, 4.0, 0))
    tower("hpp", HPP_L, (6.2, 4.0, .42), 2, 2, s=.95)
    M.pedestal("pc", 2.0, "c_grey").build((-7.0, 2.6, 0))
    f0 = fr("A18", 78.12)
    p0 = tuple(ops.location)
    key(ops, "location", 1, p0)
    key(ops, "location", f0, p0)
    key(ops, "location", f0 + 8, (p0[0], p0[1], p0[2] + .9))
    key(ops, "location", f0 + 24, (-7.0, 2.6, .42))
    f1 = fr("A18", 80.94)
    for ob in (laba,):
        key(ob, "scale", f1, (1, 1, 1))
        key(ob, "scale", f1 + 5, (1.12, 1.12, 1.12))
        key(ob, "scale", f1 + 9, (1, 1, 1))
    sparkles("sp", (-1.0, 0, 1.4), f1 + 4, 4, 1.7, .32)
    ck = L.checkmark("ck", (-1.0, -.4, 3.1), .7)
    pop(ck, f1 + 8, 1.0)
    A["OPS"] = (ops, (0, 0, OPS_L * lh + .3))
    A["LABA"] = (-1.0, 0, .42 + LABA_L * lh + .3)
    A["HPP"] = (6.2, 4.0, .42 + HPP_L * lh + .3)
    cam, tgt = make_camera(lens=26, shift_y=.1)
    cam_keys(cam, tgt, [(1, (0, -24, 8), (-.5, 1, 3.4)), (n, (-1.0, -20, 6.0), (-1.0, 0, 2.4))])


def a19(n, info, A):
    """'kamu butuh pabrik berkapasitas besar,' — lini produksi berjalan, operator & QC."""
    pl = M.production_line("pl", 0, 0)
    M.bottles_on_line("bt", pl["x0"], pl["x1"], 0, pl["zc"], n, speed=1.6, gap=.9)
    for k, (kind, x, y, r, hold) in enumerate((("operator", -3.4, -2.1, .2, None), ("qc", 3.6, -2.0, -.3, "tablet"),
                                               ("qc2", 6.4, -2.1, .3, None), ("buruh", 9.6, -4.0, .6, "carton"))):
        w = M.worker(f"pw{k}", kind, (x, y, 0), r, hold=hold)
        if kind == "operator":
            L.pose(w, "point", 10)
    fl = M.forklift("fl")
    fl.rotation_euler.z = math.pi
    key(fl, "location", 1, (16, -7.0, 0))
    key(fl, "location", n, (9.0, -7.0, 0))
    A["FILLING"] = pl["machines"]["FILLING"]
    A["KAPASITAS"] = (-5.6, 5.6, 6.5)
    cam, tgt = make_camera(lens=20, shift_y=.1)
    cam_keys(cam, tgt, [(1, (-8, -24, 10), (0.5, 1.0, 2.4)), (n, (2, -23, 9), (1.5, 1.0, 2.4))])


def a20(n, info, A):
    """'logistik nasional, dan 1.000 distributor yang benar-benar aktif memesan.' — rute dari pabrik di Jawa
    ke kota-kota, pin distributor berdenyut."""
    polys, pins = _map_base(n, A, 110, 9)
    fx, fy = M.map_xy(107.0, -6.6)
    fac = M.product("fac", "galon", 1.2).build((fx, fy, 1.0))
    t_l = fr("A20", 87.14)
    for k, nm in enumerate(("Medan", "Pontianak", "Balikpapan", "Makassar", "Manado", "Ambon", "Jayapura", "Kupang",
                            "Denpasar", "Palembang")):
        lo, la = M.CITIES[nm]
        x, y = M.map_xy(lo, la)
        mx, my = (fx + x) / 2, (fy + y) / 2
        h = math.dist((fx, fy), (x, y)) * .18
        pts = [(fx + (x - fx) * u, fy + (y - fy) * u) for u in (0, .25, .5, .75, 1)]
        rb = route_ribbon(f"rt{k}", pts, t_l + k * 2, t_l + k * 2 + 22, z=1.25, width=.32)
    f_p = fr("A20", 88.27)
    for k, pn in enumerate(pins):
        f = f_p + (k * 7) % 45
        key(pn, "scale", 1, (1, 1, 1))
        key(pn, "scale", f, (1, 1, 1))
        key(pn, "scale", f + 4, (1.5, 1.5, 1.5))
        key(pn, "scale", f + 8, (1, 1, 1))
    A["LOGISTIK"] = (M.map_xy(112, -3.5)[0], M.map_xy(112, -3.5)[1], 2.0)
    A["DIST"] = (M.map_xy(121, -1.5)[0], M.map_xy(121, -1.5)[1], 2.5)
    cam, tgt = make_camera(lens=24, shift_y=.16)
    cam_keys(cam, tgt, [(1, (-40, -34, 18), (2, 0, 0)), (n, (-60, -46, 32), (8, 2, 0))])


def a21(n, info, A):
    """'tantangan terbesar bukan memproduksi airnya, tapi membuat pasar terus membeli produkmu.' —
    minimarket ramai pembeli, tronton memasok."""
    mx, my = M.MM_C
    looks = ["hijab", "mahasiswa", "cewek", "pekerja", "hijab2", "cowok"]
    for k, lk in enumerate(looks):
        c = L.character(f"buy{k}", lk, (mx + 14, my - 10 + k * 1.2, M.Z), 0, hold="phone" if k % 3 == 0 else None)
        y0 = my - 12 + k * 2.6
        L.walk_to(c, [(mx + 14, y0), (mx + 9.5, y0 * .3 + my * .7), (mx + 7.0, my + 2.6)], 1 + k * 14, speed=2.0)
    A["PASAR"] = (mx + 5.5, my, 6.2)
    A["PEMBELI"] = (mx + 11.0, my - 1.0, 3.6)
    cam, tgt = make_camera(lens=22, shift_y=.12)
    cam_keys(cam, tgt, [(1, (mx + 30, my - 12, 10), (mx + 6, my + 1, 3)), (n, (mx + 27, my - 18, 11), (mx + 6, my, 3))])


def a22(n, info, A):
    """CTA: 'Kalau ada kesempatan, kamu tertarik bangun bisnis AMDK seperti ini?' — kota diorama ortografis."""
    M.road_trucks(n, n=4)
    for ob in info.get("fsign", []):
        emission_ramp(ob.data.materials[0], [(1, 2.0)])
    cam, tgt = make_camera(ortho=110, shift_y=.12)
    tg = (0, -2, 0)
    cam_keys(cam, tgt, [(1, orbit(tg, -125, 36, 400), tg), (n, orbit(tg, -140, 36, 400), tg)])
    key(cam.data, "ortho_scale", 1, 110)
    key(cam.data, "ortho_scale", n, 190)
    A["PABRIK"] = info["anchors"]["PABRIK"]


SCENES = {f"A{k:02d}": fn for k, fn in enumerate(
    (a01, a02, a03, a04, a05, a06, a07, a08, a09, a10, a11, a12, a13, a14, a15, a16, a17, a18, a19, a20, a21, a22),
    1)}
WORLD = {"A03", "A04", "A06", "A08", "A21", "A22"}
NO_PEOPLE = set()


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
    M.glass_setup()
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, n
    info = {"people": [], "walkers": [], "workers": []}
    if args.scene in WORLD:
        info = M.build_world(people=args.scene not in NO_PEOPLE)
        M.animate_walkers(info, n)
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
