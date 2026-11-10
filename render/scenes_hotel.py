"""20 adegan video "Bangun Hotel Rp40 Miliar" (timeline dalam waktu VO yang dipercepat 1.4x).

  python3 render/scenes_hotel.py -- --scene H01 --out OUT/H01 [--res 720x1280] [--samples 4] [--frames a-b]

VO asli berisi 2 take; yang dipakai take pertama (0–101.45 dtk) + jeda 2.24 dtk untuk CTA.
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
import scenes as SC  # noqa: E402
from scenes import key, make_camera, cam_keys, orbit, visible_between, route_ribbon, studio_floor, \
    traffic  # noqa: E402

FPS = 30
SPEED = 1.4
_SRC = [("H01", 0.0), ("H02", 2.4), ("H03", 5.4), ("H04", 9.9), ("H05", 14.5), ("H06", 17.6), ("H07", 19.7),
        ("H08", 25.4), ("H09", 30.0), ("H10", 36.3), ("H11", 41.8), ("H12", 49.5), ("H13", 60.1), ("H14", 65.8),
        ("H15", 70.9), ("H16", 76.1), ("H17", 79.3), ("H18", 84.5), ("H19", 91.4), ("H20", 98.1)]
TIMELINE = [(s, round(t / SPEED, 3)) for s, t in _SRC]
END_T = round(103.69 / SPEED, 3)

HX, HY = H.HOTEL_C
HFRONT = HY - H.HD / 2
ZB = -H.Z                           # hotel/props dibangun dgn dasar Z_LAWN; di studio lantai = 0


def scene_range(sid):
    ids = [s for s, _ in TIMELINE]
    i = ids.index(sid)
    t0 = TIMELINE[i][1]
    t1 = TIMELINE[i + 1][1] if i + 1 < len(TIMELINE) else END_T
    f0, f1 = round(t0 * FPS), round(t1 * FPS)
    return t0, t1, f0, f1 - f0


def pop(ob, f, s=1.0):
    key(ob, "scale", 1, (0.001,) * 3)
    key(ob, "scale", max(1, f), (0.001,) * 3)
    key(ob, "scale", f + 4, (s * 1.18,) * 3)
    key(ob, "scale", f + 7, (s,) * 3)


def place_person(mb, loc, rot=0.0, s=1.25):
    ob = mb.build()
    ob.location = loc
    ob.rotation_euler.z = rot
    ob.scale = (s,) * 3
    return ob


def tsec(src):
    """detik pada VO asli -> detik timeline video."""
    return src / SPEED


def fr(sid, src):
    """frame lokal adegan untuk kata yang diucapkan pada detik `src` VO asli."""
    t0 = dict(TIMELINE)[sid]
    return max(1, int((tsec(src) - t0) * FPS))


def rise(ob, f0, f1, axis_scale=(1, 1)):
    key(ob, "scale", 1, (*axis_scale, .001))
    key(ob, "scale", max(1, f0), (*axis_scale, .001))
    key(ob, "scale", f1, (*axis_scale, 1.04))
    key(ob, "scale", f1 + 5, (*axis_scale, 1.0))
    for fc in SC._fcurves(ob):
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"


def move(obs, frames_locs):
    for ob in obs:
        base = Vector(ob.location)
        for f, d in frames_locs:
            key(ob, "location", f, tuple(base + Vector(d)))


def dusk():
    sun = bpy.data.objects.get("sun")
    sun.data.energy = 1.5
    sun.data.color = (1.0, .78, .6)
    nt = bpy.context.scene.world.node_tree
    for n in nt.nodes:
        if n.type == "BACKGROUND":
            n.inputs["Strength"].default_value *= .55


def hide_hotel_extras(f_show):
    for nm in ("doorman", "guest", "taxi"):
        ob = bpy.data.objects.get(nm)
        if ob:
            visible_between(ob, f_show)


# ------------------------------------------------------------------ adegan
def h01(n, info, A, cx=700, cy=0):
    """hook: punya uang Rp40 miliar — tumpukan uang jatuh lapis demi lapis."""
    studio_floor(cx, cy, size=14, wall=False)
    s = 1.0
    nz = 7
    for k in range(nz):
        mb = W.MB(f"lay{k}")
        for i in range(5):
            for j in range(4):
                H.money_bundle(mb, (i - 2) * 1.68 * s, (j - 1.5) * .82 * s, 0, s)
        ob = mb.build()
        z = k * .29 * s
        f = 2 + k * 4
        key(ob, "location", 1, (cx, cy, z + 9))
        key(ob, "location", f, (cx, cy, z + 9))
        key(ob, "location", f + 6, (cx, cy, z))
    A["MODAL"] = (cx, cy, nz * .29 + .3)
    cam, tgt = make_camera(lens=26, shift_y=.0)
    tg = (cx, cy, 1.4)
    cam_keys(cam, tgt, [(1, orbit(tg, -118, 36, 26), tg), (n, orbit(tg, -84, 30, 22), tg)])


def h02(n, info, A):
    """terus bangun hotel: gedung hotel tumbuh dari tanah, kamera mundur & naik."""
    rise(info["hotel"], 2, int(n * .55))
    for o in info["signs"]:
        pop(o, int(n * .55) + 2, 1.0)
    hide_hotel_extras(int(n * .6))
    cr = W.MB("crane")
    H.crane(cr, HX + 15, HY + 8, 32)
    crane = cr.build()
    visible_between(crane, 1, int(n * .7))
    A["HOTEL"] = info["anchors"]["HOTEL"]
    traffic(n, n=5)
    cam, tgt = make_camera(lens=18, shift_y=.1)
    cam_keys(cam, tgt, [(1, (12, -36, 3.5), (0, -6, 8)), (n, (-22, -58, 16), (0, -4, 11))])


def _cut_hotel(cx, cy):
    studio_floor(cx, cy, size=26, wall=False)
    mb, _ = H.hotel("cut", cut=True, rooms=True, front=False)
    mb.build((cx, cy, ZB))
    front = H.hotel_front_obj("front").build((cx, cy, ZB))
    signs = H.hotel_signs("ms", (cx, cy, ZB), "-y", lit=.8)
    return front, signs


def h03(n, info, A, cx=300, cy=0):
    """beneran untung? kita bedah: fasad model hotel terangkat, isi kamar terlihat; kalkulator raksasa."""
    front, signs = _cut_hotel(cx, cy)
    f0, f1 = int(n * .45), int(n * .8)
    move([front] + signs, [(f0, (0, 0, 0)), (f1, (0, -2, 34))])
    calc = H.calculator("calc", 2.2).build((cx + 15.5, cy - 9, 0))
    calc.rotation_euler.z = math.radians(-20)
    q = H.text("q", "?", 7.0, "sold", depth=1.0, loc=(cx, cy - 6, H.TOP + 4), emission=.3)
    pop(q, 6, 1.0)
    A["UNTUNG"] = (cx - 4, cy - H.HD / 2, H.LOBBY_H + 3 * H.FH)
    A["CALC"] = (cx + 15.5, cy - 9, 1.2)
    cam, tgt = make_camera(lens=22, shift_y=.08)
    tg = (cx + 1, cy, 10.5)
    cam_keys(cam, tgt, [(1, orbit(tg, -112, 14, 52), tg), (n, orbit(tg, -100, 12, 46), tg)])


def h04(n, info, A, cx=300, cy=0):
    """hotel budget-midscale 30 kamar: kamar menyala satu per satu (cutaway)."""
    studio_floor(cx, cy, size=26, wall=False)
    mb, _ = H.hotel("cut", cut=True, rooms=True, front=False)
    mb.build((cx, cy, ZB))
    rw = H.HW / H.ROOMS
    order = [(f, i) for f in range(H.FLOORS) for i in range(H.ROOMS)]
    f_a, f_b = int(n * .25), int(n * .85)
    for k, (f, i) in enumerate(order):
        zf = H.LOBBY_H + f * H.FH
        u = -H.HW / 2 + (i + .5) * rw
        g = W.MB(f"glow{k}")
        by = -H.HD / 2 + .3 + H.ROOM_D - .45
        g.box(u - rw / 2 + .25, by, zf + 1.45, u + rw / 2 - .25, by + .04, zf + H.FH - .45, "win_lit")
        ob = H.emit(g.build((cx, cy, 0)), 1.6)
        visible_between(ob, int(f_a + (f_b - f_a) * k / 29))
    A["KAMAR"] = (cx, cy - H.HD / 2, H.TOP + 1.5)
    A["MIDSCALE"] = (cx - 7, cy - H.HD / 2, H.LOBBY_H * .6)
    cam, tgt = make_camera(lens=22, shift_y=.06)
    tg = (cx, cy, 10.5)
    cam_keys(cam, tgt, [(1, orbit(tg, -98, 10, 44), tg), (n, orbit(tg, -88, 9, 41), tg)])


def h05(n, info, A):
    """tanah 15 M lalu gedung 15 M: kavling kosong + papan DIJUAL, lalu hotel berdiri."""
    fm = fr("H05", 16.0)
    rise(info["hotel"], fm, min(n - 6, fm + 26))
    for o in info["signs"]:
        visible_between(o, min(n - 4, fm + 28))
    hide_hotel_extras(fm + 30)
    lot = W.MB("lot")
    lot.box(HX - 13, HY - 6.2, H.Z, HX + 13, HY + 6.2, H.Z + .06, "dirt")
    for k in range(9):
        lot.box(HX - 13 + k * 3.2, HY - 6.3, H.Z, HX - 12.7 + k * 3.2, HY - 6.1, H.Z + 1.0, "wood")
    lot.box(HX - 13, HY - 6.3, H.Z + .6, HX + 13, HY - 6.15, H.Z + .7, "wood")
    lob = lot.build()
    sb = W.MB("soldboard")
    sb.box(HX - 5.2, HFRONT - 3.2, H.Z, HX - 5.0, HFRONT - 3.0, H.Z + 3.4, "metal")
    sb.box(HX + 1.0, HFRONT - 3.2, H.Z, HX + 1.2, HFRONT - 3.0, H.Z + 3.4, "metal")
    sb.box(HX - 5.6, HFRONT - 3.35, H.Z + 2.0, HX + 1.6, HFRONT - 3.2, H.Z + 4.4, "sold")
    sob = sb.build()
    txt = H.text("sold_t", "DIJUAL", 1.1, "tee", depth=.06, loc=(HX - 2.0, HFRONT - 3.42, H.Z + 2.6))
    for o in (lob, sob, txt):
        visible_between(o, 1, fm + 4)
    A["TANAH"] = (HX, HY, H.Z + .5)
    A["GEDUNG"] = (HX, HFRONT, H.Z + H.TOP + 2)
    cam, tgt = make_camera(lens=20, shift_y=.1)
    cam_keys(cam, tgt, [(1, (-34, -54, 30), (0, -4, 5)), (n, (-30, -50, 27), (0, -4, 6))])


def h06(n, info, A, cx=400, cy=0):
    """interior & furniture Rp3,6 M: kamar hotel lengkap."""
    studio_floor(cx, cy, size=12, wall=False)
    H.room_set("room", cx, cy)
    A["INTERIOR"] = (cx + .4, cy + 1.6, 1.6)
    cam, tgt = make_camera(lens=20, shift_y=.08)
    cam_keys(cam, tgt, [(1, (cx + 6.5, cy - 9.5, 4.8), (cx - .3, cy + 1.0, 1.0)),
                        (n, (cx + 5.0, cy - 7.8, 4.2), (cx - .3, cy + 1.0, 1.0))])


def h07(n, info, A):
    """sisanya: infrastruktur, perizinan, dana cadangan, modal kerja (panel 2D); kamera di atas tapak hotel."""
    A["INFRA"] = (HX + 8.5, HFRONT - 7, H.Z + .5)
    traffic(n, n=4)
    cam, tgt = make_camera(lens=20, shift_y=.24)
    cam_keys(cam, tgt, [(1, (34, -58, 40), (0, -2, 5)), (n, (26, -60, 36), (0, -2, 5))])


def h08(n, info, A):
    """total sekitar Rp40 miliar: hero shot hotel, kamera mengitari."""
    A["HOTEL"] = info["anchors"]["HOTEL"]
    traffic(n, n=5)
    cam, tgt = make_camera(lens=18, shift_y=.1)
    tg = (HX, HY - 3, 10)
    cam_keys(cam, tgt, [(1, orbit(tg, -125, 12, 48), tg), (n, orbit(tg, -75, 16, 46), tg)])


def h09(n, info, A, cx=500, cy=0):
    """pendapatan: 30 kamar, rata-rata Rp350 ribu/malam — lobi resepsionis, tamu check-in."""
    studio_floor(cx, cy, size=14, wall=False)
    H.lobby_set("lobby", cx, cy)
    place_person(H.staff("recept", "give"), (cx - .6, cy + 3.7, 0), 0, 1.15)
    g = place_person(H.guest("guest", "teal", "suitcase2"), (cx + 3.5, cy - 4.0, 0), math.pi, 1.15)
    key(g, "location", 1, (cx + 3.5, cy - 4.0, 0))
    key(g, "location", int(n * .6), (cx + .4, cy + 1.0, 0))
    g2 = place_person(H.guest("guest2", "red_aw"), (cx - 3.5, cy - 1.0, 0), math.pi * .8, 1.15)
    _ = g2
    A["KAMAR"] = (cx + .4, cy + 1.0, 2.6)
    cam, tgt = make_camera(lens=20, shift_y=.08)
    cam_keys(cam, tgt, [(1, (cx - 5, cy - 15, 6.5), (cx + .5, cy + 1.5, 1.6)),
                        (n, (cx - 3, cy - 12.5, 5.5), (cx + .5, cy + 1.5, 1.6))])


def h10(n, info, A):
    """okupansi 60%: 18 dari 30 jendela kamar menyala (senja)."""
    dusk()
    wins = H.room_windows("win", (HX, HY, 0), "-y")
    rnd = random.Random(4)
    lit = rnd.sample(range(30), 18)
    f_a, f_b = int(n * .15), int(n * .8)
    for o in wins:
        o.hide_render = True
    for k, idx in enumerate(lit):
        visible_between(wins[idx], int(f_a + (f_b - f_a) * k / 17))
    A["TERISI"] = (HX, HFRONT - 1.2, H.Z + H.LOBBY_H + 3.6 * H.FH)
    A["LOBI"] = info["anchors"]["LOBI"]
    traffic(n, n=4)
    cam, tgt = make_camera(lens=20, shift_y=.08)
    cam_keys(cam, tgt, [(1, (-9, -44, 8), (0, -6, 11)), (n, (-5, -40, 9), (0, -6, 11.5))])


def h11(n, info, A, cx=800, cy=0):
    """omzet Rp189 jt/bulan: 30 tumpukan uang (1 per hari) tumbuh; lalu Rp2,268 M/tahun."""
    studio_floor(cx, cy, size=16, wall=False)
    f_a, f_b = 3, int(n * .55)
    for d in range(30):
        i, j = d % 6, d // 6
        mb = W.MB(f"day{d}")
        for k in range(5):
            H.money_bundle(mb, 0, 0, k * .3, .6)
        ob = mb.build((cx + (i - 2.5) * 1.35, cy - 3.0 + j * 1.25, 0))
        ob.rotation_euler.z = math.pi / 2
        f = int(f_a + (f_b - f_a) * d / 29)
        key(ob, "scale", 1, (1, 1, .001))
        key(ob, "scale", f, (1, 1, .001))
        key(ob, "scale", f + 6, (1, 1, 1.1))
        key(ob, "scale", f + 9, (1, 1, 1))
    A["HARI"] = (cx - 3.6, cy - 3.0, 1.6)
    A["TAHUN"] = (cx + 1.0, cy + 2.0, 1.8)
    cam, tgt = make_camera(lens=24, shift_y=.02)
    tg = (cx, cy, .4)
    cam_keys(cam, tgt, [(1, orbit(tg, -100, 46, 20), tg), (n, orbit(tg, -84, 40, 18), tg)])


def h12(n, info, A):
    """omzet bukan untung: gaji, listrik, air, laundry, komisi aplikasi, maintenance."""
    # minimarket utama berada di antara kamera dan hotel: sembunyikan agar tidak menutupi
    for o in [info["mm_main"]] + list(info["mm_sign"] if isinstance(info["mm_sign"], (list, tuple)) else [info["mm_sign"]]):
        o.hide_render = True
        for c in getattr(o, "children_recursive", []):
            c.hide_render = True
    props = W.MB("ops")
    # troli laundry penuh linen
    lx, ly = HX + 6.0, HFRONT - 2.2
    props.box(lx - .9, ly - .55, H.Z + .25, lx + .9, ly + .55, H.Z + 1.3, "laundry_aw")
    for k in range(3):
        props.sphere(lx - .5 + k * .5, ly, H.Z + 1.45, .42, "tee")
    for sx in (-.7, .7):
        props.box(lx + sx - .1, ly - .1, H.Z, lx + sx + .1, ly + .1, H.Z + .25, "tire")
    # teknisi + tangga di dinding kiri
    tx = HX - 8.5
    T.beam(props, (tx - .5, HFRONT - 1.4, H.Z), (tx - .5, HFRONT - .25, H.Z + 4.2), .12, "crane")
    T.beam(props, (tx + .5, HFRONT - 1.4, H.Z), (tx + .5, HFRONT - .25, H.Z + 4.2), .12, "crane")
    for k in range(6):
        z = H.Z + .5 + k * .65
        yy = HFRONT - 1.4 + (z - H.Z) / 4.2 * 1.15
        props.box(tx - .5, yy - .05, z, tx + .5, yy + .05, z + .08, "crane")
    # tiang listrik + meteran
    px = HX - 13.5
    props.cyl(px, HFRONT - 9, H.Z, H.Z + 9, .18, "metal", n=8)
    props.box(px - 1.4, HFRONT - 9.1, H.Z + 8.2, px + 1.4, HFRONT - 8.9, H.Z + 8.4, "metal")
    props.box(px - .35, HFRONT - 9.4, H.Z + 1.5, px + .35, HFRONT - 9.15, H.Z + 2.4, "tee")
    # tandon air di menara kecil sisi kiri hotel
    wx, wy = HX - 10.8, HFRONT - 2.8
    for sx in (-.7, .7):
        for sy in (-.7, .7):
            props.box(wx + sx - .08, wy + sy - .08, H.Z, wx + sx + .08, wy + sy + .08, H.Z + 3.0, "metal")
    props.box(wx - .9, wy - .9, H.Z + 3.0, wx + .9, wy + .9, H.Z + 3.15, "metal")
    props.cyl(wx, wy, H.Z + 3.15, H.Z + 4.9, .85, "tank", n=12)
    props.build()
    place_person(H.staff("tech"), (tx, HFRONT - 1.0, H.Z + 1.6), 0)
    place_person(H.staff("hk"), (lx - 1.6, ly, H.Z), math.radians(-30))
    # ikon HP untuk komisi aplikasi
    ph = W.MB("phone")
    ph.box(-.9, -.1, 0, .9, .1, 3.2, "tv")
    ph.box(-.75, -.13, .3, .75, -.1, 2.9, "chart1")
    ph.box(-.5, -.16, 1.6, .5, -.13, 2.4, "tee")
    pob = ph.build((HX + 10.5, HFRONT - 4.5, H.Z))
    pop(pob, fr("H12", 55.0), 1.0)
    A["GAJI"] = (HX - 2.4, HFRONT - 1.6, H.Z + 2.6)
    A["LISTRIK"] = (px, HFRONT - 9, H.Z + 8.6)
    A["AIR"] = (wx, wy, H.Z + 5.0)
    A["LAUNDRY"] = (lx, ly, H.Z + 2.0)
    A["KOMISI"] = (HX + 10.5, HFRONT - 4.5, H.Z + 3.4)
    A["MAINT"] = (tx, HFRONT - 1.0, H.Z + 4.6)
    traffic(n, n=4)
    cam, tgt = make_camera(lens=18, shift_y=-.02)
    cam_keys(cam, tgt, [(1, (-15, -56, 10), (-1, -6, 8)), (n, (-11, -52, 9.5), (-1, -6, 8))])


def _stack(cx, cy, nb, s, name="b"):
    obs = []
    for k in range(nb):
        mb = W.MB(f"{name}{k}")
        H.money_bundle(mb, 0, 0, 0, s)
        obs.append(mb.build((cx, cy, k * .29 * s)))
    return obs


def h13(n, info, A, cx=900, cy=0):
    """sisa surplus Rp59 jt/bulan: 19 ikat (omzet) -> 13 ikat terbang ke tumpukan BIAYA, sisa 6."""
    studio_floor(cx, cy, size=14, wall=False)
    s = 1.5
    obs = _stack(cx - 2.2, cy, 19, s)
    f0 = int(n * .12)
    for k, ob in enumerate(obs[6:]):
        f = f0 + k * 3
        base = ob.location.copy()
        dest = (cx + 3.2 + (k % 2) * .2, cy + (k % 3 - 1) * .3, (k // 2) * .29 * s)
        key(ob, "location", 1, tuple(base))
        key(ob, "location", f, tuple(base))
        key(ob, "location", f + 7, ((base.x + dest[0]) / 2, cy - 1.5, base.z + 2.5))
        key(ob, "location", f + 13, dest)
    A["SURPLUS"] = (cx - 2.2, cy, 6 * .29 * s + .4)
    A["BIAYA"] = (cx + 3.3, cy, 7 * .29 * s + .4)
    cam, tgt = make_camera(lens=24, shift_y=.04)
    tg = (cx + .5, cy, 2.6)
    cam_keys(cam, tgt, [(1, orbit(tg, -96, 18, 19), tg), (n, orbit(tg, -88, 16, 17), tg)])


def h14(n, info, A, cx=900, cy=0):
    """belum termasuk pajak, bunga, penyusutan: potongan kecil keluar dari tumpukan surplus."""
    studio_floor(cx, cy, size=14, wall=False)
    s = 1.5
    _stack(cx - 2.2, cy, 6, s)
    _stack(cx + 3.3, cy, 7, s, "c")
    _stack(cx + 3.5, cy + .3, 6, s, "d")
    names = ("PAJAK", "BUNGA", "SUSUT")
    words = (67.7, 68.6, 69.3)
    dests = ((cx - 5.4, cy + 1.2, 0), (cx - 2.4, cy + 3.8, 0), (cx + .8, cy + 2.4, 0))
    for k, (nm, w, d) in enumerate(zip(names, words, dests)):
        mb = W.MB(f"chip{k}")
        H.money_bundle(mb, 0, 0, 0, .7, "grey_bad")
        ob = mb.build()
        f = fr("H14", w) - 4
        src = (cx - 2.2, cy, 6 * .29 * s)
        key(ob, "location", 1, src)
        key(ob, "location", max(2, f), src)
        key(ob, "location", f + 6, ((src[0] + d[0]) / 2, (src[1] + d[1]) / 2, src[2] + 1.5))
        key(ob, "location", f + 11, d)
        visible_between(ob, max(2, f))
        A[nm] = (d[0], d[1], .6)
    A["SURPLUS"] = (cx - 2.2, cy, 6 * .29 * s + .4)
    cam, tgt = make_camera(lens=24, shift_y=.0)
    tg = (cx - .8, cy - 1.0, 1.2)
    cam_keys(cam, tgt, [(1, orbit(tg, -92, 30, 17), tg), (n, orbit(tg, -84, 28, 16), tg)])


def h15(n, info, A, cx=600, cy=0):
    """jangan cuma jual kamar: restoran, meeting room, paket gathering."""
    studio_floor(cx, cy, size=20, wall=False)
    _, xs = H.facilities_set("fac", cx, cy)
    rnd = random.Random(2)
    for k, (x, y) in enumerate(((xs[0] - 2.4, cy - 1.0), (xs[0] + .8, cy + 1.6), (xs[1] - 1.45, cy - .2),
                                (xs[1] + 1.45, cy + .8), (xs[2] - 2.2, cy - 2.0), (xs[2] + 1.6, cy - 2.4))):
        place_person(W.person(f"p{k}", rnd.choice(W.SHIRTS)), (x, y, 0), rnd.uniform(0, 6.3), 1.0)
    place_person(H.staff("waiter", "give"), (xs[0] - 1.0, cy - 3.0, 0), math.pi, 1.0)
    A["RESTO"] = (xs[0], cy, 1.4)
    A["MEETING"] = (xs[1], cy, 1.4)
    A["GATHER"] = (xs[2], cy, 1.4)
    cam, tgt = make_camera(lens=22, shift_y=.02)
    ks = [(1, xs[0] - 1.0), (fr("H15", 73.6), xs[0] + .5), (fr("H15", 74.6) + 4, xs[1]), (fr("H15", 75.3) + 8, xs[2]),
          (n, xs[2] + .5)]
    cam_keys(cam, tgt, [(f, orbit((x, cy, .5), -90, 50, 21), (x, cy, .5)) for f, x in ks])
    for fc in SC._fcurves(cam) + SC._fcurves(tgt):
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"


def _road(c, facing):
    return T.road_point(c[0], c[1], facing)


def h16(n, info, A):
    """kerja sama dengan perusahaan & travel agent: rute dari gedung mitra ke hotel."""
    hotel_rp = (HX, W.ROADS[0])
    parts = [("PERUSAHAAN", H.OFFICE_C, "-x", fr("H16", 77.0)), ("TRAVEL", H.TRAVEL_C, "-y", fr("H16", 77.9)),
             ("INSTANSI", H.GOV_C, "+x", fr("H16", 76.4))]
    for k, (nm, c, fc, f0) in enumerate(parts):
        rp = _road(c, fc)
        pts = [rp] + T.route(rp, hotel_rp)[1:] + [(HX, HFRONT - 10)]
        route_ribbon(f"r{k}", pts, max(1, f0 - 10), f0 + 18, z=.45, width=.6)
        pn = T.pin(f"pin{k}").build((c[0], c[1], info["anchors"][{"PERUSAHAAN": "OFFICE", "TRAVEL": "TRAVEL",
                                                                  "INSTANSI": "GOV"}[nm]][2] + .5))
        pop(pn, max(1, f0 - 8), 1.6)
        A[nm] = (c[0], c[1], 6.0 if nm == "PERUSAHAAN" else pn.location.z + 3.5)
    A["HOTEL"] = info["anchors"]["HOTEL"]
    traffic(n, n=5)
    cam, tgt = make_camera(ortho=172, shift_y=.04)
    tg = (4, 16, 0)
    cam_keys(cam, tgt, [(1, orbit(tg, -125, 40, 400), tg), (n, orbit(tg, -117, 40, 400), tg)])


def h17(n, info, A):
    """dengan modal sama: jaringan minimarket di banyak cabang (cabang muncul satu per satu)."""
    f_a = fr("H17", 82.3)
    f_b = n - 10
    order = [6, 5, 3, 0, 1, 7, 4, 2]
    for k, (ob, sg, top) in enumerate(info["branches"]):
        f = int(f_a + (f_b - f_a) * order.index(k) / max(1, len(info["branches"]) - 1))
        pop(ob, f)
        pop(sg, f)
        pn = T.pin(f"pin{k}", "laundry_aw").build((top[0], top[1], top[2] + .5))
        pop(pn, f + 3, 1.5)
    for k, (_, _, b0) in enumerate(info["branches"]):
        A[f"CAB{k}"] = (b0[0], b0[1], b0[2] + 5)
    A["HOTEL"] = info["anchors"]["HOTEL"]
    A["MM"] = info["anchors"]["MINIMARKET"]
    traffic(n, n=5)
    cam, tgt = make_camera(ortho=110, shift_y=.1)
    tg = (0, -2, 0)
    cam_keys(cam, tgt, [(1, orbit(tg, -132, 40, 400), tg), (n, orbit(tg, -124, 40, 400), tg)])
    key(cam.data, "ortho_scale", 1, 110)
    key(cam.data, "ortho_scale", n, 165)


def h18(n, info, A):
    """properti & okupansi (hotel) vs distribusi & perputaran barang (minimarket, truk boks)."""
    tr = H.box_truck("truck")
    tr.location = (HX + 3.8, -28.4, .05)
    tr.rotation_euler.z = math.pi
    cr = W.MB("crates")
    for k in range(3):
        cr.boxc(HX - 6.5 + k * .9, -30.6, H.Z, .8, .6, .55, "crate")
        cr.boxc(HX - 6.5 + k * .9, -30.6, H.Z + .58, .8, .6, .55, "crate" if k != 1 else "mm_yellow")
    cr.build()
    b = place_person(W.person("buyer", "yellow", bag=True), (HX - 2.5, -30.5, .25), 0)
    key(b, "location", 1, (HX - 2.5, -30.6, .25))
    key(b, "location", n, (HX - 2.5, -25.6, .25))
    b.rotation_euler.z = math.pi
    A["PROPERTI"] = info["anchors"]["HOTEL_MID"]
    A["OKUPANSI"] = info["anchors"]["LOBI"]
    A["DISTRIBUSI"] = (HX + 3.8, -28.4, 4.4)
    A["BARANG"] = (HX - 2.5, -32.5, 5.2)
    fs = fr("H18", 87.4)
    cam, tgt = make_camera(lens=19, shift_y=.1)
    cam_keys(cam, tgt, [(1, (-9, -26.5, 4.0), (0, -6, 9)), (fs - 6, (-8.5, -26.0, 4.0), (0, -6, 8.5)),
                        (fs + 10, (-9, -20.5, 5.0), (2.5, -35, 2.6)), (n, (-8.5, -19.5, 5.0), (2.5, -35, 2.4))])
    for fc in SC._fcurves(cam) + SC._fcurves(tgt):
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"


def _mini(root_name, loc, s, builders):
    root = bpy.data.objects.new(root_name, None)
    lp._link(root)
    for ob in builders:
        ob.parent = root
    root.location = loc
    root.scale = (s,) * 3
    return root


def h19(n, info, A, cx=1000, cy=0):
    """pilih 1 hotel atau banyak cabang minimarket? model mini di dua podium + VS."""
    studio_floor(cx, cy, size=18, wall=False)
    pd = W.MB("ped")
    for x, col in ((cx - 6.5, "hotel_acc"), (cx + 6.5, "mm_blue")):
        pd.cyl(x, cy, 0, .8, 5.6, "tee", n=28)
        pd.cyl(x, cy, .8, .9, 5.7, col, n=28)
    pd.build()
    mb, _ = H.hotel("mh")
    ho = mb.build((0, 0, ZB))
    sg = H.hotel_signs("mhs", (0, 0, ZB), "-y", lit=.8)
    s = .3
    _mini("mini_hotel", (cx - 6.5, cy + 1.0, .9), s, [ho] + sg)
    spots = ((-2.4, -1.6), (2.4, -1.6), (0, 0.4), (-2.6, 2.6), (2.6, 2.6))
    for k, (dx, dy) in enumerate(spots):
        mm, _ = H.minimarket(f"mm{k}")
        o = mm.build((0, 0, ZB))
        t = H.minimarket_sign(f"mm{k}", (0, 0, ZB), "-y")
        r = _mini(f"mini_mm{k}", (cx + 6.5 + dx * 1.0, cy + dy, .9), .2, [o, t])
        pop(r, 6 + k * 5, .2)
    vs = H.text("vs", "VS", 3.0, "sold", depth=.6, loc=(cx, cy - 1, 2.2), emission=.2)
    pop(vs, 4, 1.0)
    A["HOTEL1"] = (cx - 6.5, cy - 1.0, .9 + s * (H.LOBBY_H + 2 * H.FH))
    A["CABANG"] = (cx + 6.5, cy + 1, 3.4)
    cam, tgt = make_camera(lens=26, shift_y=.0)
    tg = (cx, cy, 3.6)
    cam_keys(cam, tgt, [(1, orbit(tg, -90, 16, 40), tg), (n, orbit(tg, -90, 14, 37), tg)])


def h20(n, info, A):
    """penutup: diorama utuh dengan hotel & cabang minimarket, CTA."""
    traffic(n, n=6)
    A["HOTEL"] = info["anchors"]["HOTEL"]
    cam, tgt = make_camera(ortho=130, shift_y=.12)
    tg = (0, -2, 0)
    cam_keys(cam, tgt, [(1, orbit(tg, -128, 36, 400), tg), (n, orbit(tg, -140, 36, 400), tg)])
    key(cam.data, "ortho_scale", 1, 130)
    key(cam.data, "ortho_scale", n, 230)
    key(cam.data, "shift_y", 1, .12)
    key(cam.data, "shift_y", n, .16)


SCENES = {f"H{k:02d}": fn for k, fn in enumerate(
    (h01, h02, h03, h04, h05, h06, h07, h08, h09, h10, h11, h12, h13, h14, h15, h16, h17, h18, h19, h20), 1)}
STUDIO = {"H01", "H03", "H04", "H06", "H09", "H11", "H13", "H14", "H15", "H19"}
BRANCHES = {"H17", "H20"}
NO_PEOPLE = {"H16", "H17", "H20"}


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
    H.glassy("mm_glass", .55)
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, n
    info = {"people": []}
    if args.scene not in STUDIO:
        info = H.build_world(people=args.scene not in NO_PEOPLE, branches=args.scene in BRANCHES)
        W.animate_people(info, n)
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
            v = world_to_camera_view(sc, cam, Vector(p))
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
