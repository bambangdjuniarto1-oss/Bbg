"""16 adegan video "Omzet 50 Juta dari Cuci Sepatu" di dunia diorama.

  python3 render/scenes.py -- --scene S01 --out out/S01 [--res 720x1280] [--samples 8] [--frames a-b]

Tiap adegan: frame PNG di OUT/frames + OUT/anchors.json (posisi 2D titik label per frame).
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

FPS = 30
# (id, mulai detik) — selesai = mulai adegan berikutnya
TIMELINE = [("S01", 0.0), ("S02", 6.55), ("S03", 11.3), ("S04", 15.45), ("S05", 21.6), ("S06", 26.4),
            ("S07", 31.2), ("S08", 34.9), ("S09", 39.7), ("S10", 43.3), ("S11", 48.9), ("S12", 53.4),
            ("S13", 58.3), ("S14", 61.4), ("S15", 65.1), ("S16", 68.7)]
END_T = 74.32


def scene_range(sid):
    ids = [s for s, _ in TIMELINE]
    i = ids.index(sid)
    t0 = TIMELINE[i][1]
    t1 = TIMELINE[i + 1][1] if i + 1 < len(TIMELINE) else END_T
    f0, f1 = round(t0 * FPS), round(t1 * FPS)
    return t0, t1, f0, f1 - f0


# ------------------------------------------------------------------ helper
def key(ob, path, frame, value):
    setattr(ob, path, value)
    ob.keyframe_insert(path, frame=frame)


def make_camera(lens=None, ortho=None, shift_y=0.08):
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    lp._link(cam)
    cam.data.sensor_fit = "VERTICAL"
    cam.data.sensor_height = 24
    cam.data.clip_start = 0.05
    cam.data.clip_end = 3000
    cam.data.shift_y = shift_y
    if ortho:
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = ortho
    else:
        cam.data.lens = lens or 18
    tgt = bpy.data.objects.new("cam_target", None)
    lp._link(tgt)
    c = cam.constraints.new("TRACK_TO")
    c.target = tgt
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"
    bpy.context.scene.camera = cam
    return cam, tgt


def cam_keys(cam, tgt, keys):
    """keys: [(frame, (x,y,z) posisi, (x,y,z) target)]"""
    for f, p, t in keys:
        cam.location = p
        cam.keyframe_insert("location", frame=f)
        tgt.location = t
        tgt.keyframe_insert("location", frame=f)


def orbit(target, az, el, dist):
    a, e = math.radians(az), math.radians(el)
    return (target[0] + dist * math.cos(e) * math.cos(a), target[1] + dist * math.cos(e) * math.sin(a),
            target[2] + dist * math.sin(e))


def ease_keys(ob, path, f0, f1, v0, v1, interp="BEZIER"):
    key(ob, path, f0, v0)
    key(ob, path, f1, v1)
    if ob.animation_data and ob.animation_data.action:
        for fc in _fcurves(ob):
            if fc.data_path == path:
                for kp in fc.keyframe_points:
                    kp.interpolation = interp


def _fcurves(ob):
    act = ob.animation_data.action
    if hasattr(act, "fcurves"):
        return act.fcurves
    out = []
    for layer in act.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                out += list(cb.fcurves)
    return out


def visible_between(ob, f_on, f_off=None):
    for o in [ob] + list(ob.children_recursive):
        key(o, "hide_render", 1, True) if f_on > 1 else key(o, "hide_render", 1, False)
        key(o, "hide_render", f_on, False)
        if f_off:
            key(o, "hide_render", f_off, True)


def route_ribbon(name, pts, f0, f1, z=.42, width=.75):
    ob, cu = lp.poly_curve(name, pts, z=0.0)
    cu.bevel_depth = width
    cu.bevel_resolution = 0
    cu.bevel_factor_mapping_end = "SPLINE"
    ob.location.z = z
    ob.scale.z = .15
    ob.data.materials.append(lp.mat("route", emission=0.5))
    key(cu, "bevel_factor_end", f0, 0.0)
    key(cu, "bevel_factor_end", f1, 1.0)
    return ob


def couriers(name, pts, starts, n_frames, speed=24.0, z=.25, scale=1.25, loop=False):
    """motor kurir bergerak di sepanjang rute; return frame tiba."""
    pob, pcu = lp.poly_curve(name + "_path", pts, z=z)
    pcu.use_path = True
    pob.hide_render = True
    L = lp.path_length(pts)
    per = speed / FPS / L
    arrivals = []
    for k, st in enumerate(starts):
        s = lp.scooter(f"{name}_{k}", scale=scale)
        c = s.constraints.new("FOLLOW_PATH")
        c.target = pob
        c.use_curve_follow = True
        c.use_fixed_location = True
        c.forward_axis = "FORWARD_X"
        c.up_axis = "UP_Z"
        if loop:
            start_off = (st % 1.0)
            c.offset_factor = start_off
            c.keyframe_insert("offset_factor", frame=1)
            end = start_off + per * (n_frames - 1)
            # bagi jadi segmen 0..1 berulang
            f = 1
            cur = start_off
            while True:
                f_hit = f + (1 - cur) / per
                if f_hit >= n_frames:
                    c.offset_factor = cur + per * (n_frames - f)
                    c.keyframe_insert("offset_factor", frame=n_frames)
                    break
                c.offset_factor = 1.0
                c.keyframe_insert("offset_factor", frame=f_hit)
                c.offset_factor = 0.0
                c.keyframe_insert("offset_factor", frame=f_hit + 0.01)
                f, cur = f_hit + 0.01, 0.0
            _ = end
            continue
        f_end = st + int(1 / per)
        c.offset_factor = 0.0
        c.keyframe_insert("offset_factor", frame=st)
        c.offset_factor = min(1.0, (min(f_end, n_frames + 1) - st) * per)
        c.keyframe_insert("offset_factor", frame=min(f_end, n_frames + 1))
        visible_between(s, max(st, 1), f_end if f_end <= n_frames else None)
        if f_end <= n_frames:
            arrivals.append(f_end)
    return arrivals


def traffic(n_frames, seed=3, n=7):
    rnd = random.Random(seed)
    for k in range(n):
        r = rnd.choice(W.ROADS)
        lane = rnd.choice((-2.5, 2.5))
        horiz = rnd.random() < .5
        c = lp.car(f"car{k}", length=4.0)
        c.scale = (1.0,) * 3
        sp = (8 + rnd.random() * 4) * (1 if lane < 0 else -1)
        t0 = rnd.uniform(-60, 60)
        if horiz:
            c.rotation_euler.z = 0 if sp > 0 else math.pi
            key(c, "location", 1, (t0, r + lane, .05))
            key(c, "location", n_frames, (t0 + sp * n_frames / FPS, r + lane, .05))
        else:
            c.rotation_euler.z = math.pi / 2 if sp < 0 else -math.pi / 2
            sp = -sp
            key(c, "location", 1, (r + lane, t0, .05))
            key(c, "location", n_frames, (r + lane, t0 + sp * n_frames / FPS, .05))


def studio_floor(cx, cy, size=14, wall=True, wall_col="wall_cream2"):
    mb = W.MB(f"studio{cx}")
    mb.box(cx - size, cy - size, -6, cx + size, cy + size, -.7, "soil")
    mb.box(cx - size, cy - size, -.7, cx + size, cy + size, 0, "wood")
    if wall:
        mb.box(cx - size, cy + 3, 0, cx + size, cy + 3.4, 8, wall_col)
    mb.build()


# ------------------------------------------------------------------ adegan
def s01(n, info, A):
    cam, tgt = make_camera(lens=16, shift_y=.15)
    cam_keys(cam, tgt, [(1, (-7, -31.8, 4.6), (-7, -14, 5.2)), (n, (-7, -26.5, 3.8), (-7, -14, 4.6))])
    owner = W.person("owner", "sole", apron=True, arms_forward=True).build()
    owner.location = (-3.2, -17.4, .25)
    t = W.MB("counter_out")
    t.box(-4.2, -19.0, .25, -2.2, -18.2, 1.25, "wood")
    W.sneaker(t, -3.75, -18.6, 1.25, .9, depth=.32)
    t.build()
    couriers("pass", [(-60, -26), (60, -26)], [int(n * .25)], n, speed=14, scale=1.3)
    traffic(n)


def s02(n, info, A):
    cam, tgt = make_camera(lens=18, shift_y=.1)
    cam_keys(cam, tgt, [(1, (-7, -30, 6), (-7, -14, 5)), (int(n * .55), (-40, -75, 45), (-5, -10, 2)),
                        (n, (-82, -112, 92), (-2, -4, 0))])
    # tanda tanya di rumah-rumah acak
    rnd = random.Random(9)
    picks = rnd.sample([p for p in W.PLACED if abs(p[1][0]) > 20 or abs(p[1][1]) > 20], 6)
    for i, (_, (x, y, top)) in enumerate(picks):
        A[f"Q{i + 1}"] = (x, y, top)
    traffic(n)


def studio_counter(n, info, A, cx=300, cy=0):
    studio_floor(cx, cy, size=10)
    mb = W.MB("counter")
    mb.box(cx - 2.5, cy - .8, 0, cx + 2.5, cy + .8, 1.0, "wood")
    mb.box(cx - 2.6, cy - .9, 1.0, cx + 2.6, cy + .9, 1.08, "bench_wood")
    # rak di dinding belakang
    cols = ["red_aw", "yellow", "sneaker", "sole", "teal", "wall_orange", "green_aw"]
    rnd = random.Random(4)
    for r in range(4):
        z = 1.2 + r * .9
        mb.box(cx - 6, cy + 2.6, z, cx + 6, cy + 3.0, z + .06, "shelf")
        for i in range(12):
            W.sneaker(mb, cx - 5.7 + i * .95, cy + 2.8, z + .06, .7, upper=rnd.choice(cols), depth=.25)
    # botol semprot + sikat
    mb.cyl(cx + 1.2, cy - .1, 1.08, 1.5, .1, "teal", n=8)
    mb.box(cx + 1.15, cy - .14, 1.5, cx + 1.38, cy - .06, 1.6, "metal")
    mb.build()
    shoe = W.MB("hero_shoe")
    W.sneaker(shoe, -.45, 0, 0, .9, upper="sole", depth=.32)
    hero = shoe.build((cx - .1, cy - .05, 1.08))
    dirt = W.MB("dirt")
    dirt.box(0, -.18, .12, .5, .18, .55, "dirt")
    d = dirt.build((cx - .55, cy - .05, 1.08))
    ease_keys(d, "scale", int(n * .25), int(n * .7), (1, 1, 1), (0.001, 1, 1))
    br = W.MB("brush")
    br.box(-.12, -.06, 0, .12, .06, .06, "yellow")
    br.box(-.1, -.05, -.06, .1, .05, 0, "frame")
    br.box(-.03, -.02, .06, .03, .02, .3, "wood")
    b = br.build()
    b.rotation_euler.y = math.radians(-20)
    key(b, "location", int(n * .2), (cx - .6, cy - .25, 1.7))
    for k in range(4):
        f = int(n * (.25 + k * .11))
        key(b, "location", f, (cx - .55 + k * .14, cy - .25, 1.62 if k % 2 else 1.55))
    key(b, "location", int(n * .75), (cx - .0, cy - .3, 1.85))
    cam, tgt = make_camera(lens=28, shift_y=.12)
    tg = (cx - .1, cy, 1.45)
    cam_keys(cam, tgt, [(1, orbit(tg, -112, 20, 4.6), tg), (n, orbit(tg, -88, 17, 4.0), tg)])
    _ = hero


def s04(n, info, A, cx=400, cy=0):
    studio_floor(cx, cy, size=16, wall=False)
    g = W.MB("plaza")
    g.box(cx - 16, cy - 16, 0, cx + 16, cy + 16, .25, "sidewalk")
    g.build()
    mb, top = W.shoe_shop("shop_b")
    mb.build((cx, cy + 9, -W.Z_LAWN + .25), 0)
    rnd = random.Random(2)
    cols = ["red_aw", "yellow", "sneaker", "sole", "teal", "wall_orange", "green_aw", "laundry_aw"]
    N = 150
    for i in range(N):
        fr = i / N
        h = 4.2 * (fr ** .8)
        r = 4.6 * (1 - h / 4.6) + .3
        a = rnd.uniform(0, 2 * math.pi)
        rr = r * math.sqrt(rnd.random())
        x, y = cx + rr * math.cos(a), cy - 1 + rr * math.sin(a)
        p = W.shoe_pair(f"pile{i}", rnd.choice(cols), scale=.85).build()
        p.rotation_euler = (rnd.uniform(-.25, .25), rnd.uniform(-.25, .25), rnd.uniform(0, 6.3))
        f_land = int(6 + (n - 30) * fr)
        key(p, "location", 1, (x, y, h + 30))
        key(p, "location", max(2, f_land - 9), (x, y, h + 14))
        key(p, "location", f_land, (x, y, .25 + h))
    cam, tgt = make_camera(lens=18, shift_y=.08)
    cam_keys(cam, tgt, [(1, (cx - 7, cy - 17, 2.2), (cx, cy, 2.0)), (n, (cx - 9, cy - 19, 7.5), (cx, cy, 4.2))])


def s05(n, info, A, cx=500, cy=0):
    studio_floor(cx, cy, size=12, wall_col="wall_cream2")
    mb = W.MB("shelf55")
    rows, cols_n = 5, 11
    for r in range(rows + 1):
        z = .4 + r * .95
        mb.box(cx - 5.6, cy + 2.2, z - .06, cx + 5.6, cy + 3.0, z, "shelf")
    for i in range(cols_n + 1):
        x = cx - 5.6 + i * (11.2 / cols_n)
        mb.box(x - .05, cy + 2.2, .34, x + .05, cy + 3.0, .4 + rows * .95, "shelf")
    mb.build()
    rnd = random.Random(8)
    colors = ["red_aw", "yellow", "sneaker", "sole", "teal", "wall_orange", "green_aw", "laundry_aw"]
    order = [(r, c) for c in range(cols_n) for r in range(rows)]
    f_a, f_b = 6, n - 18
    for k, (r, c) in enumerate(order):
        x = cx - 5.6 + (c + .5) * (11.2 / cols_n)
        z = .4 + r * .95
        p = W.shoe_pair(f"s55_{k}", rnd.choice(colors), scale=.75).build()
        p.location = (x, cy + 2.55, z)
        f = int(f_a + (f_b - f_a) * k / (len(order) - 1))
        key(p, "scale", 1, (0.001,) * 3)
        key(p, "scale", f, (0.001,) * 3)
        key(p, "scale", f + 4, (1.15,) * 3)
        key(p, "scale", f + 7, (1.0,) * 3)
    cam, tgt = make_camera(lens=22, shift_y=.04)
    cam_keys(cam, tgt, [(1, (cx - 3.5, cy - 7.5, 3.0), (cx - 2.5, cy + 2.5, 2.6)),
                        (n, (cx + 3.5, cy - 7.5, 3.0), (cx + 2.5, cy + 2.5, 2.6))])


def s06(n, info, A):
    owner = W.person("owner", "sole", apron=True).build()
    owner.location = (-7, -16.8, .25)
    stool = W.MB("stool")
    stool.box(-9.2, -17.4, .25, -8.4, -16.6, .9, "wood")
    stool.build()
    clock = W.MB("clock")
    clock.disc_y(0, 0, 0, .55, .1, "frame", n=16)
    clock.box(-.03, -.12, -.03, .03, -.1, .4, "door")
    ck = clock.build((-11.5, -15.6, 3.0))
    hand = W.MB("hand")
    hand.box(-.02, -.14, -.02, .35, -.12, .02, "red_aw")
    h = hand.build((-11.5, -15.6, 3.0))
    key(h, "rotation_euler", 1, (0, 0, 0))
    key(h, "rotation_euler", n, (0, math.radians(720), 0))
    _ = ck
    cam, tgt = make_camera(lens=16, shift_y=.15)
    cam_keys(cam, tgt, [(1, (-7, -28, 3.6), (-7, -14, 3.6)), (n, (-7, -25.5, 3.3), (-7, -14, 3.4))])


def s07(n, info, A):
    a = W.person("owner", "sole", apron=True, arms_forward=True).build()
    a.location = (2.0, -17.3, .25)
    a.rotation_euler.z = math.pi / 2
    b = W.person("laundry_owner", "laundry_aw", arms_forward=True).build()
    b.location = (3.4, -17.3, .25)
    b.rotation_euler.z = -math.pi / 2
    for o in (a, b):
        for k in range(0, n, 8):
            key(o, "location", k + 1, (o.location.x, o.location.y, .25 + (.06 if (k // 8) % 2 else 0)))
    A["SALAM"] = (2.7, -17.3, 2.4)
    cam, tgt = make_camera(lens=16, shift_y=.15)
    cam_keys(cam, tgt, [(1, (-2, -28, 4.0), (-7, -14, 4.0)), (12, (-1, -27.6, 3.8), (3.0, -14, 3.2)),
                        (n, (1.5, -25, 3.2), (3.0, -14, 3.0))])


def s08(n, info, A):
    rnd = random.Random(6)
    for k in range(6):
        p = W.person(f"cust{k}", rnd.choice(W.SHIRTS), bag=True).build()
        st = 1 + k * int(n / 7)
        x0 = 8.5 + rnd.choice((-1, 1)) * rnd.uniform(5, 9)
        p.rotation_euler.z = math.pi / 2 if x0 > 8.5 else -math.pi / 2
        key(p, "location", 1, (x0, -18.2, .25))
        key(p, "location", st, (x0, -18.2, .25))
        key(p, "location", st + 40, (8.5, -18.2, .25))
        key(p, "location", st + 55, (8.5, -15.8, .25))
        visible_between(p, max(1, st), st + 56)
    cam, tgt = make_camera(lens=16, shift_y=.15)
    cam_keys(cam, tgt, [(1, (13, -29, 4.0), (8.5, -14, 3.2)), (n, (10.5, -24.5, 3.4), (8.5, -14, 3.0))])


def s09(n, info, A):
    pts = info["routes"]["MITRA 3"]
    route_ribbon("r_m3", pts, 4, int(n * .6))
    couriers("c_m3", pts, [int(n * .35)], n, speed=26)
    A["SISTEM"] = (26, -11, 2)
    traffic(n)
    cam, tgt = make_camera(ortho=105, shift_y=.12)
    tg = (12, -12, 0)
    cam_keys(cam, tgt, [(1, orbit(tg, -128, 38, 400), tg), (n, orbit(tg, -118, 38, 400), tg)])


def s10(n, info, A):
    lo = W.person("laundry_owner", "laundry_aw", bag=True).build()
    lo.location = (8.5, -17.0, .25)
    bags = W.MB("bags")
    for i in range(5):
        bags.box(10.6 + (i % 3) * .7, -17.6 + (i // 3) * .7, .25 + (i // 3) * 0, 11.2 + (i % 3) * .7,
                 -17.0 + (i // 3) * .7, .9, "sole")
    bags.build()
    A["HARGA_A"] = (4.5, -15.5, 9.5)
    A["HARGA_B"] = (12.5, -15.5, 9.5)
    A["SELISIH"] = (8.5, -16.5, 2.4)
    cam, tgt = make_camera(lens=16, shift_y=.15)
    cam_keys(cam, tgt, [(1, (8.5, -30, 4.4), (8.5, -14, 4.6)), (n, (8.5, -26.5, 4.0), (8.5, -14, 4.4))])


def s11(n, info, A):
    cam, tgt = make_camera(lens=14, shift_y=-.02)
    cam_keys(cam, tgt, [(1, (-62, -21.6, 2.3), (-40, -20.5, 1.9)), (n, (-24, -21.6, 2.3), (-2, -19.0, 1.9))])
    rig = W.MB("handlebar")
    rig.box(-.6, -.62, -1.0, .6, -.56, -.94, "scooter")
    for sx in (-1, 1):
        rig.box(sx * .6 - .1 * (sx > 0), -.66, -1.02, sx * .6 + .1 * (sx < 0) + (0 if sx > 0 else 0), -.52, -.92,
                "red_aw")
        rig.box(sx * .6 - .09, -.66, -1.06, sx * .6 + .09, -.52, -.9, "red_aw")
        rig.box(sx * .45 - .03, -.5, -.9, sx * .45 + .03, -.47, -.75, "metal")
        rig.box(sx * .45 - .08, -.47, -.78, sx * .45 + .08, -.42, -.72, "glass2")
    ob = rig.build()
    ob.parent = cam
    sp = W.MB("speedo")
    sp.cyl(0, 0, 0, .03, .1, "scooter", n=16)
    sp.cyl(0, 0, .03, .04, .085, "frame", n=16)
    so = sp.build()
    so.parent = cam
    so.location = (0, -.5, -.95)
    so.rotation_euler.x = math.radians(25)
    nd = W.MB("needle")
    nd.box(-.004, 0, 0, .004, .075, .008, "red_aw")
    no = nd.build()
    no.parent = so
    no.location = (0, 0, .04)
    key(no, "rotation_euler", 1, (0, 0, math.radians(110)))
    key(no, "rotation_euler", int(n * .4), (0, 0, math.radians(20)))
    key(no, "rotation_euler", n, (0, 0, math.radians(10)))
    bag = W.MB("frontbag")
    bag.box(-.22, -.78, -1.25, .22, -.6, -1.0, "sole")
    bo = bag.build()
    bo.parent = cam
    couriers("ahead", [(-50, -21.6), (60, -21.6)], [1], n, speed=9, scale=1.25)
    traffic(n)


def s12(n, info, A):
    for i, (name, pts) in enumerate(info["routes"].items()):
        f0 = 4 + i * 6
        route_ribbon(f"route{i}", pts, f0, f0 + 30)
        couriers(f"c{i}", pts, [f0 + 8, f0 + 40], n, speed=26)
    traffic(n)
    cam, tgt = make_camera(ortho=150, shift_y=.12)
    tg = (0, -4, 0)
    cam_keys(cam, tgt, [(1, orbit(tg, -140, 36, 400), tg), (n, orbit(tg, -128, 36, 400), tg)])


def s13(n, info, A):
    o = W.person("owner", "sole", apron=True, arms_up=True).build()
    for k in range(0, n + 1, 9):
        key(o, "location", k + 1, (-7, -17.2, .25 + (.45 if (k // 9) % 2 else 0)))
    bags = W.MB("bags")
    for i in range(8):
        bags.box(-12 + (i % 4) * .8, -18.6 + (i // 4) * .8, .25, -11.4 + (i % 4) * .8, -18.0 + (i // 4) * .8, .95,
                 "sole")
    bags.build()
    cam, tgt = make_camera(lens=16, shift_y=.15)
    cam_keys(cam, tgt, [(1, (-7, -29, 4.6), (-7, -14, 4.8)), (n, (-7, -24.5, 3.6), (-7, -14, 4.0))])


def s14(n, info, A):
    o = W.person("owner", "sole", apron=True).build()
    o.location = (-7, -16.6, .25)
    for k in range(0, n + 1, 22):
        key(o, "rotation_euler", k + 1, (0, 0, math.radians(35 if (k // 22) % 2 else -35)))
    rnd = random.Random(12)
    for k in range(5):
        p = W.person(f"walker{k}", rnd.choice(W.SHIRTS)).build()
        y = -17.9 - (k % 2) * .9
        x0, x1 = (-22, 10) if k % 2 else (10, -22)
        st = 1 + k * int(n / 6)
        p.rotation_euler.z = -math.pi / 2 if x1 > x0 else math.pi / 2
        key(p, "location", st, (x0, y, .25))
        key(p, "location", st + 150, (x1, y, .25))
        visible_between(p, st)
    cam, tgt = make_camera(lens=16, shift_y=.15)
    cam_keys(cam, tgt, [(1, (-5, -27.5, 3.4), (-7, -14, 3.2)), (n, (-6, -27, 3.4), (-7, -14, 3.2))])


def s15(n, info, A):
    for i, (name, pts) in enumerate(info["routes"].items()):
        route_ribbon(f"route{i}", pts, 1, 2)
        couriers(f"c{i}", pts, [.1 + .33 * k + .07 * i for k in range(3)], n, speed=26, loop=True)
    traffic(n)
    cam, tgt = make_camera(lens=24, shift_y=.1)
    tg = (-2, -6, 0)
    cam_keys(cam, tgt, [(1, orbit(tg, -125, 25, 120), tg), (n, orbit(tg, -132, 42, 170), tg)])


def s16(n, info, A):
    for i, (name, pts) in enumerate(info["routes"].items()):
        route_ribbon(f"route{i}", pts, 1, 2)
        couriers(f"c{i}", pts, [.2 + .5 * k + .1 * i for k in range(2)], n, speed=26, loop=True)
    traffic(n)
    cam, tgt = make_camera(ortho=150, shift_y=.12)
    tg = (0, -4, 0)
    cam_keys(cam, tgt, [(1, orbit(tg, -128, 36, 400), tg), (n, orbit(tg, -138, 36, 400), tg)])
    key(cam.data, "ortho_scale", 1, 150)
    key(cam.data, "ortho_scale", n, 300)
    key(cam.data, "shift_y", 1, .12)
    key(cam.data, "shift_y", n, .16)


SCENES = {"S01": s01, "S02": s02, "S03": studio_counter, "S04": s04, "S05": s05, "S06": s06, "S07": s07,
          "S08": s08, "S09": s09, "S10": s10, "S11": s11, "S12": s12, "S13": s13, "S14": s14, "S15": s15,
          "S16": s16}
NO_PEOPLE = {"S06"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--res", default="720x1280")
    ap.add_argument("--samples", type=int, default=8)
    ap.add_argument("--frames", default=None)
    ap.add_argument("--speed", type=float, default=1.0,
                    help="percepat adegan (mis. 1.28 = ikut VO yang dipercepat 1.28x)")
    args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])

    t0, t1, gf0, n = scene_range(args.scene)
    r = args.speed
    # timeline keluaran: waktu dibagi r; frame keluaran k memakai posisi sumber 1 + (k-1)*r
    gf0_out = round(t0 / r * FPS)
    n_out = round(t1 / r * FPS) - gf0_out

    def src_set(k):
        p = min(float(n), 1 + (k - 1) * r)
        sc.frame_set(int(p), subframe=p - int(p))
    lp.reset()
    W.PLACED.clear()
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
    rx, ry = map(int, args.res.split("x"))
    lp.setup_render(rx, ry, args.samples)
    W.setup_world_light()
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, n
    info = W.build_world(people=args.scene not in NO_PEOPLE)
    W.animate_people(info, n)
    A = dict(info["anchors"])
    SCENES[args.scene](n, info, A)
    cam = sc.camera

    os.makedirs(os.path.join(args.out, "frames"), exist_ok=True)
    data = {"scene": args.scene, "t0": t0, "t1": t1, "global_f0": gf0_out, "n": n_out, "fps": FPS,
            "res": [rx, ry], "speed": r, "frames": {}}
    for f in range(1, n_out + 1):
        src_set(f)
        pos = {}
        for name, p in A.items():
            v = world_to_camera_view(sc, cam, Vector(p))
            if v.z > 0:
                pos[name] = [round(v.x * rx, 1), round((1 - v.y) * ry, 1)]
        data["frames"][f] = pos
    with open(os.path.join(args.out, "anchors.json"), "w") as fh:
        json.dump(data, fh)

    lo, hi = (1, n_out) if not args.frames else map(int, args.frames.split("-"))
    for f in range(lo, hi + 1):
        path = os.path.join(args.out, "frames", f"{f:04d}.png")
        if os.path.exists(path) and not args.frames:
            continue
        src_set(f)
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
    print("DONE", args.scene, n_out)


if __name__ == "__main__":
    main()
