"""20 adegan video "Distribusi Tahu Kuning" (timeline sudah dalam waktu VO yang dipercepat 1.4x).

  python3 render/scenes_tahu.py -- --scene T01 --out OUT/T01 [--res 720x1280] [--samples 4] [--frames a-b]
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
import scenes as SC  # noqa: E402
from scenes import key, make_camera, cam_keys, orbit, ease_keys, visible_between, route_ribbon, \
    studio_floor, traffic  # noqa: E402

FPS = 30
SPEED = 1.4
_SRC = [("T01", 0.0), ("T02", 3.5), ("T03", 10.7), ("T04", 16.5), ("T05", 22.4), ("T06", 26.2), ("T07", 33.2),
        ("T08", 40.2), ("T09", 45.8), ("T10", 50.4), ("T11", 54.3), ("T12", 56.8), ("T13", 61.1), ("T14", 66.1),
        ("T15", 69.6), ("T16", 77.9), ("T17", 85.8), ("T18", 95.4), ("T19", 104.5), ("T20", 107.5)]
TIMELINE = [(s, round(t / SPEED, 3)) for s, t in _SRC]
END_T = round(113.6856 / SPEED, 3)

# motor kurir = motor tukang tahu (warna kaos bisa diganti untuk kurir rekrutan)
_TEES = []


def _bike(name, scale=1.25):
    tee = _TEES.pop(0) if _TEES else "tee"
    return T.tahu_bike(name, scale=scale, tee=tee, sleeve="sleeve" if tee == "tee" else tee)


lp.scooter = _bike


def scene_range(sid):
    ids = [s for s, _ in TIMELINE]
    i = ids.index(sid)
    t0 = TIMELINE[i][1]
    t1 = TIMELINE[i + 1][1] if i + 1 < len(TIMELINE) else END_T
    f0, f1 = round(t0 * FPS), round(t1 * FPS)
    return t0, t1, f0, f1 - f0


def couriers(name, pts, starts, n, speed=24.0, loop=False):
    return SC.couriers(name, pts, starts, n, speed=speed, z=.05, scale=1.25, loop=loop)


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


def street_cam(n, x=0.0, push=True):
    cam, tgt = make_camera(lens=20, shift_y=.12)
    a = ((x + 4.5, -17.5, 3.6), (x - .5, -31, 2.0))
    b = ((x + 3.0, -20.5, 2.8), (x - .5, -31, 1.8))
    cam_keys(cam, tgt, [(1, *a), (n, *(b if push else a))])
    return cam, tgt


def customers_by(info, pred, k, seed=1):
    c = [x for x in info["customers"] if pred(x)]
    random.Random(seed).shuffle(c)
    return c[:k]


# ------------------------------------------------------------------ adegan
def t01(n, info, A):
    """hook: tukang tahu & motornya di depan rumah kompleks."""
    b = T.tahu_bike("bike", rider=False)
    b.location = (-2.4, -28.0, .05)
    s = place_person(T.seller("seller", "wave"), (.5, -29.4, .25), math.pi)
    for k in range(0, n + 1, 10):
        key(s, "rotation_euler", k + 1, (0, 0, math.pi + (math.radians(8) if (k // 10) % 2 else -math.radians(8))))
    A["SELLER"] = (.5, -29.4, 3.1)
    street_cam(n)


def t02(n, info, A):
    """income 7,5 jt: kamera naik dari jalan ke udara, motor berangkat."""
    cam, tgt = make_camera(lens=18, shift_y=.1)
    cam_keys(cam, tgt, [(1, (3.5, -20, 3.2), (-.5, -30, 2)), (int(n * .5), (-30, -72, 42), (0, -18, 2)),
                        (n, (-78, -108, 88), (0, -6, 0))])
    pts = [(-2.4, -28.0), (-40, -28.0)]
    couriers("go", [(-2.4, -27.6), (-24, -27.6), (-24, -60)], [8], n, speed=11)
    T.steam("steam", info["chimney"], n)
    traffic(n, n=5)
    _ = pts


def t03(n, info, A, cx=300, cy=0):
    """produk: tampah bambu berisi tahu kuning (tanpa toko, tanpa stok besar)."""
    studio_floor(cx, cy, size=9)
    st = W.MB("tbl")
    st.box(cx - 2.6, cy - 1.3, 0, cx + 2.6, cy + 1.3, 1.0, "wood")
    st.box(cx - 2.7, cy - 1.4, 1.0, cx + 2.7, cy + 1.4, 1.06, "bench_wood")
    T.tampah(st, cx, cy - .1, 1.06, 1.15)
    st.build()
    spots = ((-.36, -.42, 0), (.36, -.42, .08), (-.36, .22, -.08), (.36, .22, .05), (0, -.1, .2))
    for i, (dx, dy, rz) in enumerate(spots):
        t = T.tofu_obj(f"tofu{i}", .62).build()
        z = 1.2 + (.45 if i == 4 else 0)
        t.rotation_euler.z = rz
        f = 4 + i * 6
        key(t, "location", 1, (cx + dx, cy - .1 + dy, z + 4))
        key(t, "location", f, (cx + dx, cy - .1 + dy, z + 4))
        key(t, "location", f + 8, (cx + dx, cy - .1 + dy, z))
    A["NOTOKO"] = (cx - 1.4, cy, 2.6)
    A["NOSTOK"] = (cx + 1.4, cy, 2.6)
    A["SISTEM"] = (cx, cy - .2, 1.9)
    cam, tgt = make_camera(lens=30, shift_y=.1)
    tg = (cx, cy - .1, 1.45)
    cam_keys(cam, tgt, [(1, orbit(tg, -110, 34, 6.2), tg), (n, orbit(tg, -80, 30, 5.4), tg)])


def t04(n, info, A):
    """cari pabrik tahu kuning, ajak kerja sama (salaman di depan pabrik)."""
    a = place_person(T.seller("seller", "give"), (-.75, -16.6, .25), math.pi / 2)
    b = place_person(W.person("owner", "tee", apron=True, arms_forward=True), (.75, -16.6, .25), -math.pi / 2)
    for o in (a, b):
        for k in range(0, n, 8):
            key(o, "location", k + 1, (o.location.x, o.location.y, .25 + (.06 if (k // 8) % 2 else 0)))
    bk = T.tahu_bike("bike", rider=False)
    bk.location = (-5.0, -18.0, .05)
    A["SALAM"] = (0, -16.6, 2.9)
    A["PABRIK_FRONT"] = info["anchors"]["PABRIK_FRONT"]
    T.steam("steam", info["chimney"], n)
    cam, tgt = make_camera(lens=18, shift_y=.12)
    cam_keys(cam, tgt, [(1, (-14, -38, 6.5), (0, -12, 5.0)), (n, (-5, -31, 4.0), (0, -12, 4.2))])


def t05(n, info, A, cx=400, cy=0):
    """1 bungkus isi 10 = Rp6.000 (harga pabrik)."""
    studio_floor(cx, cy, size=9, wall_col="wall_cream2")
    pd = W.MB("pedestal")
    pd.cyl(cx, cy, 0, .9, 1.6, "tee", n=24)
    pd.cyl(cx, cy, .9, .98, 1.7, "yellow", n=24)
    pd.build()
    s = .42
    for i in range(5):
        for j in range(2):
            t = T.tofu_obj(f"tf{i}{j}", s * .97).build()
            x, y = cx + (i - 2) * s, cy + (j - .5) * s
            f = 3 + (i * 2 + j) * 3
            key(t, "location", 1, (x, y, 5))
            key(t, "location", f, (x, y, 5))
            key(t, "location", f + 7, (x, y, .99))
    sh = T.tofu_pack("shell", s, contents=False).build((cx, cy, .98))
    pop(sh, int(n * .55))
    A["ISI10"] = (cx, cy, 1.9)
    cam, tgt = make_camera(lens=30, shift_y=.06)
    tg = (cx, cy, 1.15)
    cam_keys(cam, tgt, [(1, orbit(tg, -100, 26, 8.2), tg), (n, orbit(tg, -80, 22, 7.4), tg)])


def t06(n, info, A):
    """jual Rp8.500, siap antar sampai rumah: motor datang, serahkan tahu di pagar."""
    stop = int(n * .45)
    ride = T.tahu_bike("ride")
    key(ride, "location", 1, (-34, -27.8, .05))
    key(ride, "location", stop, (-2.4, -27.8, .05))
    for fc in SC._fcurves(ride):
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
            kp.easing = "EASE_OUT"
    visible_between(ride, 1, stop + 1)
    park = T.tahu_bike("park", rider=False)
    park.location = (-2.4, -27.8, .05)
    visible_between(park, stop + 1)
    s = place_person(T.seller("seller", "give"), (.3, -30.6, .25), 0)
    pk = T.tofu_pack("pk", .16).build()
    pk.parent = s
    pk.location = (0, -.78, 1.05)
    pk.scale = (.8,) * 3
    visible_between(s, stop + 1)
    key(s, "location", stop + 1, (-.6, -28.9, .25))
    key(s, "location", stop + 14, (.0, -30.9, .25))
    place_person(T.customer("cust", "red_aw", hijab=True, give=True), (0, -32.9, .25), math.pi)
    A["RUMAH"] = (0, -32.6, 4.2)
    cam, tgt = make_camera(lens=20, shift_y=.12)
    cam_keys(cam, tgt, [(1, (-14, -18.5, 3.4), (-12, -29, 1.8)), (stop, (2.5, -19.0, 3.0), (-1.0, -30.5, 1.8)),
                        (n, (3.2, -20.5, 2.8), (-.4, -31, 1.8))])


def t07(n, info, A, cx=500, cy=0):
    """margin Rp2.500: tumpukan koin 6.000 vs 8.500."""
    studio_floor(cx, cy, size=9, wall_col="wall_cream2")
    pk = T.tofu_pack("pk", .3).build((cx, cy - 1.4, 0))
    _ = pk
    th = .3
    for side, cnt in ((-1, 6), (1, 8.5)):
        x = cx + side * 1.7
        k = 0
        while k < cnt:
            hgt = th if cnt - k >= 1 else th * (cnt - k)
            green = side > 0 and k >= 6
            mb = W.MB(f"coin{side}_{k}")
            mb.cyl(0, 0, 0, hgt - .02, .62, "money" if green else "coin", n=16)
            mb.cyl(0, 0, hgt - .02, hgt, .5, "money_dk" if green else "coin_dk", n=16)
            ob = mb.build((x, cy, k * th))
            f = (4 + k * 4) if not green else int(n * .45) + (k - 6) * 8
            key(ob, "location", 1, (x, cy, k * th + 6))
            key(ob, "location", f, (x, cy, k * th + 6))
            key(ob, "location", f + 6, (x, cy, k * th))
            k += 1
    A["HPABRIK"] = (cx - 1.7, cy, 2.1)
    A["HJUAL"] = (cx + 1.7, cy, 2.85)
    A["MARGIN"] = (cx + 2.2, cy, 2.1)
    cam, tgt = make_camera(lens=26, shift_y=.04)
    tg = (cx, cy - .4, 1.2)
    cam_keys(cam, tgt, [(1, orbit(tg, -96, 20, 13), tg), (n, orbit(tg, -86, 17, 12), tg)])


def t08(n, info, A, cx=600, cy=0):
    """stok kebanyakan -> menumpuk & terbuang."""
    studio_floor(cx, cy, size=14, wall=False)
    g = W.MB("plaza")
    g.box(cx - 14, cy - 14, 0, cx + 14, cy + 14, .25, "sidewalk")
    g.build()
    rnd = random.Random(5)
    N = 70
    for i in range(N):
        fr = i / N
        h = 3.0 * (fr ** .8)
        r = 3.6 * (1 - h / 3.4) + .3
        a = rnd.uniform(0, 2 * math.pi)
        rr = r * math.sqrt(rnd.random())
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        bad = fr > .25 and rnd.random() < .45
        p = T.tofu_pack(f"pile{i}", .3, key="grey_bad" if bad else "tahu").build()
        p.rotation_euler = (rnd.uniform(-.3, .3), rnd.uniform(-.3, .3), rnd.uniform(0, 6.3))
        f_land = int(5 + (n * .7) * fr)
        key(p, "location", 1, (x, y, h + 25))
        key(p, "location", max(2, f_land - 8), (x, y, h + 12))
        key(p, "location", f_land, (x, y, .25 + h))
    # lalat kecil berputar di atas tumpukan
    for k in range(4):
        mb = W.MB(f"fly{k}")
        mb.sphere(0, 0, 0, .09, "bike_blk")
        fl = mb.build()
        for f in range(1, n + 1, 4):
            a = f * .25 + k * 1.6
            key(fl, "location", f, (cx + 1.4 * math.cos(a), cy + 1.4 * math.sin(a), 3.6 + .3 * math.sin(f * .4 + k)))
        visible_between(fl, int(n * .55))
    A["TUMPUK"] = (cx - 2.2, cy, 2.6)
    A["RUGI"] = (cx + 2.0, cy, 2.0)
    cam, tgt = make_camera(lens=20, shift_y=.08)
    cam_keys(cam, tgt, [(1, (cx - 6, cy - 14, 2.4), (cx, cy, 1.8)), (n, (cx - 7, cy - 15, 6.0), (cx, cy, 2.8))])


def _tour(info, cust):
    """rute motor dari pabrik mengunjungi daftar pelanggan berurutan (+ panjang kumulatif)."""
    pts = [(T.FACTORY_C[0] + 2.5, -16.5), (T.FACTORY_C[0] + 2.5, T.STREET_Y)]
    marks = []
    for c in cust:
        seg = T.route(pts[-1], c["road"])
        pts += seg[1:]
        marks.append(lp.path_length(pts))
    return pts, marks


def t09(n, info, A):
    """hunting customer dari kompleks ke kompleks: pin hijau muncul tiap rumah didatangi."""
    cust = customers_by(info, lambda c: c["road"][1] == -24 or c["road"][0] == 24, 7, seed=3)
    cust.sort(key=lambda c: (c["road"][0] if c["road"][1] == -24 else 30 + c["road"][1]))
    pts, marks = _tour(info, cust)
    L = lp.path_length(pts)
    speed = L / (n * .92 / FPS)
    couriers("hunt", pts, [1], n, speed=speed)
    route_ribbon("hunt_r", pts, 1, int(n * .92))
    for i, (c, m) in enumerate(zip(cust, marks)):
        f = int(1 + m / (speed / FPS))
        pn = T.pin(f"pin{i}").build((c["pos"][0], c["pos"][1], c["pos"][2] + .8))
        pop(pn, f, 1.6)
        A[f"PIN{i}"] = (c["pos"][0], c["pos"][1], c["pos"][2] + 4)
    A["KOMPLEKS_A"] = (0, -50, 6)
    A["KOMPLEKS_B"] = (48, 0, 6)
    cam, tgt = make_camera(ortho=118, shift_y=.1)
    tg = (14, -18, 0)
    cam_keys(cam, tgt, [(1, orbit(tg, -125, 40, 400), tg), (n, orbit(tg, -115, 40, 400), tg)])


def _doorstep(n, info, A, hx, cust_shirt="teal", hijab=False, seller_pose="give", bike_side=-1):
    park = T.tahu_bike("park", rider=False)
    park.location = (hx + bike_side * 2.6, -27.8, .05)
    s = place_person(T.seller("seller", seller_pose), (hx - .6, -31.0, .25), math.radians(-25))
    _ = s
    c = place_person(T.customer("cust", cust_shirt, hijab=hijab, give=True), (hx + .3, -32.8, .25), math.pi - math.radians(25))
    _ = c
    return park


def t10(n, info, A):
    """pengiriman terjadwal seminggu sekali (panel jadwal 2D)."""
    _doorstep(n, info, A, 10.6, "green_aw")
    pk = T.tofu_pack("pk", .16).build((10.6, -31.9, 1.6))
    key(pk, "location", int(n * .3), (10.6, -31.7, 1.55))
    key(pk, "location", int(n * .6), (10.6, -32.2, 1.55))
    A["RUMAH"] = (10.6, -32.6, 4.2)
    cam, tgt = make_camera(lens=22, shift_y=.12)
    cam_keys(cam, tgt, [(1, (18.5, -22.0, 3.0), (10.4, -31.8, 1.9)), (n, (17.0, -23.5, 2.7), (10.4, -31.8, 1.8))])


def t11(n, info, A):
    """catat pesanan di database: tukang tahu cek HP di samping motor."""
    b = T.tahu_bike("bike", rider=False)
    b.location = (-2.4, -27.8, .05)
    place_person(T.seller("seller", "phone"), (.2, -28.9, .25), math.pi * .85)
    cam, tgt = make_camera(lens=24, shift_y=.1)
    cam_keys(cam, tgt, [(1, (3.0, -22.5, 2.6), (-.6, -29, 1.8)), (n, (2.3, -23.6, 2.4), (-.4, -29, 1.8))])


def t12(n, info, A):
    """ambil dari pabrik sesuai pesanan: bungkus tahu terbang masuk ke boks motor."""
    bk = T.tahu_bike("bike", rider=False)
    bk.location = (3.5, -17.6, .05)
    bk.rotation_euler.z = math.pi
    place_person(T.seller("seller", "stand"), (6.6, -17.2, .25), math.pi / 2)
    door = (0, -14.0, 1.4)
    rnd = random.Random(2)
    for k in range(14):
        p = T.tofu_pack(f"fly{k}", .16).build()
        f0 = 3 + k * int((n - 25) / 14)
        side = 1 if k % 2 else -1
        tx, ty, tz = 3.5 + 1.1 * 1.25, -17.6 + side * .65, 1.5
        mid = ((door[0] + tx) / 2, (door[1] + ty) / 2, 3.6 + rnd.uniform(-.3, .3))
        key(p, "location", f0, door)
        key(p, "location", f0 + 6, mid)
        key(p, "location", f0 + 12, (tx, ty, tz))
        visible_between(p, f0, f0 + 13)
    A["PABRIK_FRONT"] = info["anchors"]["PABRIK_FRONT"]
    A["BOKS"] = (4.9, -17.6, 2.6)
    T.steam("steam", info["chimney"], n)
    cam, tgt = make_camera(lens=18, shift_y=.12)
    cam_keys(cam, tgt, [(1, (10, -31, 4.6), (1.5, -14, 3.6)), (n, (8, -28, 3.8), (1.5, -14, 3.2))])


def t13(n, info, A):
    """jaringan pelanggan tetap: rute dari pabrik ke banyak rumah + pin."""
    cust = customers_by(info, lambda c: True, 14, seed=7)
    for i, c in enumerate(cust):
        f0 = 2 + i * 4
        route_ribbon(f"r{i}", c["route"], f0, f0 + 26, z=.45, width=.55)
        pn = T.pin(f"pin{i}").build((c["pos"][0], c["pos"][1], c["pos"][2] + .8))
        pop(pn, f0 + 26, 1.6)
    A["PABRIK"] = info["anchors"]["PABRIK"]
    T.steam("steam", info["chimney"], n)
    traffic(n, n=5)
    cam, tgt = make_camera(ortho=150, shift_y=.1)
    tg = (0, -4, 0)
    cam_keys(cam, tgt, [(1, orbit(tg, -140, 38, 400), tg), (n, orbit(tg, -128, 38, 400), tg)])


def t14(n, info, A, cx=700, cy=0):
    """target 100 bungkus sehari: grid 10x10 bungkus muncul satu per satu."""
    studio_floor(cx, cy, size=16, wall=False)
    s = .22
    order = [(i, j) for j in range(10) for i in range(10)]
    f_a, f_b = 3, int(n * .85)
    for k, (i, j) in enumerate(order):
        p = T.tofu_pack(f"p{k}", s).build((cx + (i - 4.5) * 1.35, cy - 4.0 + j * .82, 0))
        pop(p, int(f_a + (f_b - f_a) * k / 99))
    A["GRID"] = (cx, cy + 4.5, 1.0)
    cam, tgt = make_camera(lens=22, shift_y=.0)
    tg = (cx, cy - .3, 0)
    cam_keys(cam, tgt, [(1, orbit(tg, -90, 60, 25), tg), (n, orbit(tg, -96, 55, 23), tg)])


def t15(n, info, A, cx=800, cy=0):
    """Rp2.500 x 100 x 30 hari = Rp7,5 juta: 30 tumpukan uang (1 per hari) tumbuh."""
    studio_floor(cx, cy, size=16, wall=False)
    f_a, f_b = 3, int(n * .8)
    for d in range(30):
        i, j = d % 6, d // 6
        mb = W.MB(f"day{d}")
        for k in range(5):
            mb.box(-.45, -.25, k * .24, .45, .25, k * .24 + .2, "money")
            mb.box(-.47, -.27, k * .24 + .2, .47, .27, k * .24 + .24, "money_dk")
        mb.box(-.12, -.27, 0, .12, .27, 1.2, "tee")
        ob = mb.build((cx + (i - 2.5) * 1.3, cy - 3.0 + j * 1.5, 0))
        f = int(f_a + (f_b - f_a) * d / 29)
        key(ob, "scale", 1, (1, 1, .001))
        key(ob, "scale", f, (1, 1, .001))
        key(ob, "scale", f + 6, (1, 1, 1.1))
        key(ob, "scale", f + 9, (1, 1, 1))
    cam, tgt = make_camera(lens=24, shift_y=.02)
    tg = (cx, cy, .4)
    cam_keys(cam, tgt, [(1, orbit(tg, -100, 48, 21), tg), (n, orbit(tg, -84, 42, 19), tg)])


def t16(n, info, A):
    """laba kotor: belum dipotong bensin, kurir, operasional."""
    b = T.tahu_bike("bike", rider=False)
    b.location = (-2.4, -27.8, .05)
    place_person(T.seller("seller", "stand"), (.4, -29.0, .25), math.pi)
    A["BENSIN"] = (-2.0, -27.8, 2.6)
    A["KURIR"] = (.4, -29.0, 3.0)
    A["OPS"] = (-3.0, -31.5, 4.6)
    street_cam(n)


def t17(n, info, A):
    """rekrut kurir & perluas area: beberapa kurir berangkat dari pabrik, area melebar."""
    _TEES[:] = ["tee", "red_aw", "laundry_aw", "yellow", "green_aw", "wall_orange", "teal", "red_aw"]
    cust = customers_by(info, lambda c: True, 8, seed=11)
    for i, c in enumerate(cust):
        f0 = 3 + i * 7
        route_ribbon(f"r{i}", c["route"], f0, f0 + 30, z=.45, width=.55)
        couriers(f"k{i}", c["route"], [f0 + 4], n, speed=30)
    A["AREA1"] = (-50, 50, 5)
    A["AREA2"] = (50, -50, 5)
    T.steam("steam", info["chimney"], n)
    cam, tgt = make_camera(ortho=105, shift_y=.1)
    tg = (0, -6, 0)
    cam_keys(cam, tgt, [(1, orbit(tg, -132, 38, 400), tg), (n, orbit(tg, -124, 38, 400), tg)])
    key(cam.data, "ortho_scale", 1, 105)
    key(cam.data, "ortho_scale", n, 175)


def t18(n, info, A):
    """kebutuhan sederhana yang dibeli berulang: pelanggan menerima tahu lagi."""
    _doorstep(n, info, A, -10.6, "yellow", hijab=True, bike_side=1)
    pk = T.tofu_pack("pk", .16).build()
    key(pk, "location", 1, (-10.6, -31.9, 1.55))
    key(pk, "location", int(n * .35), (-10.6, -31.9, 1.55))
    key(pk, "location", int(n * .55), (-10.6, -32.25, 1.55))
    A["RUMAH"] = (-10.6, -32.6, 4.2)
    cam, tgt = make_camera(lens=22, shift_y=.12)
    cam_keys(cam, tgt, [(1, (-18.5, -22.0, 3.0), (-10.8, -31.8, 1.9)), (n, (-17.0, -23.5, 2.7), (-10.8, -31.8, 1.8))])


def t19(n, info, A):
    """layak dicoba? tukang tahu naik motor di depan pabrik, kamera mengitari."""
    bk = T.tahu_bike("bike")
    bk.location = (0, -21.5, .05)
    bk.rotation_euler.z = math.radians(-8)
    T.steam("steam", info["chimney"], n)
    A["SELLER"] = (0, -21.5, 3.3)
    cam, tgt = make_camera(lens=20, shift_y=.12)
    tg = (0, -18, 3.2)
    cam_keys(cam, tgt, [(1, orbit(tg, -60, 12, 14), tg), (n, orbit(tg, -105, 14, 13), tg)])


def t20(n, info, A):
    """penutup: diorama utuh, kurir-kurir berputar, CTA follow."""
    _TEES[:] = ["tee", "red_aw", "laundry_aw", "yellow", "green_aw", "wall_orange"] * 2
    cust = customers_by(info, lambda c: True, 6, seed=11)
    for i, c in enumerate(cust):
        route_ribbon(f"r{i}", c["route"], 1, 2, z=.45, width=.55)
        couriers(f"k{i}", c["route"], [.15 + .5 * k + .09 * i for k in range(2)], n, speed=26, loop=True)
    T.steam("steam", info["chimney"], n)
    traffic(n, n=5)
    cam, tgt = make_camera(ortho=150, shift_y=.12)
    tg = (0, -4, 0)
    cam_keys(cam, tgt, [(1, orbit(tg, -128, 36, 400), tg), (n, orbit(tg, -138, 36, 400), tg)])
    key(cam.data, "ortho_scale", 1, 150)
    key(cam.data, "ortho_scale", n, 290)
    key(cam.data, "shift_y", 1, .12)
    key(cam.data, "shift_y", n, .16)


SCENES = {"T01": t01, "T02": t02, "T03": t03, "T04": t04, "T05": t05, "T06": t06, "T07": t07, "T08": t08,
          "T09": t09, "T10": t10, "T11": t11, "T12": t12, "T13": t13, "T14": t14, "T15": t15, "T16": t16,
          "T17": t17, "T18": t18, "T19": t19, "T20": t20}
NO_PEOPLE = {"T03", "T05", "T07", "T08", "T14", "T15"}


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
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, n
    info = T.build_world(people=args.scene not in NO_PEOPLE)
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
