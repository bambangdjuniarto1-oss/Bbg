"""Adegan S12 (53.4–58.3 dtk): aerial, beberapa laundry mitra kirim sepatu ke toko.

Pemakaian:
  python3 render/s12_mitra.py --out OUTDIR [--res 1080x1920] [--frames 1-147] [--samples 20]
Menghasilkan OUTDIR/frames/####.png + OUTDIR/anchors.json (posisi 2D label per frame).
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

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--res", default="1080x1920")
ap.add_argument("--frames", default="1-147")
ap.add_argument("--samples", type=int, default=20)
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])

FPS = 30
N_FRAMES = 147  # 4.9 dtk

lp.reset()
bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
rx, ry = map(int, args.res.split("x"))
lp.setup_render(rx, ry, args.samples)
sc = bpy.context.scene
sc.frame_start, sc.frame_end = 1, N_FRAMES

# ------------------------------------------------------------ bangunan utama
SHOP = (8, 12, 28, 24)
LAUNDRIES = {
    "MITRA 1": ((-70, 45, -60, 54), "-y", [(-65, 45), (-65, 40), (-45, 40), (-45, 3), (18, 3), (18, 12)]),
    "MITRA 2": ((-25, -54, -15, -45), "+y", [(-20, -45), (-20, -40), (-1.5, -40), (-1.5, 3), (18, 3), (18, 12)]),
    "MITRA 3": ((50, 55, 59, 65), "-x", [(50, 60), (44, 60), (44, 3), (18, 3), (18, 12)]),
    "MITRA 4": ((65, -54, 75, -45), "+y", [(70, -45), (70, -40), (46.5, -40), (46.5, 3), (18, 3), (18, 12)]),
    "MITRA 5": ((-16, 55, -6.5, 65), "+x", [(-6.5, 60), (1.5, 60), (1.5, 3), (18, 3), (18, 12)]),
}
pad = 2
reserved = [(SHOP[0] - pad, SHOP[1] - 3, SHOP[2] + pad, SHOP[3] + pad)]
reserved += [(r[0] - pad, r[1] - pad, r[2] + pad, r[3] + pad) for r, _, _ in LAUNDRIES.values()]

lp.build_roads()
lp.build_blocks(reserved)

anchors = {}
anchors["TOKO CUCI SEPATU"] = lp.shop_building("shop", *SHOP, "-y", "wall_white", "shop_red", h=8)
# rak sepatu warna-warni di balik kaca
random.seed(3)
for i in range(14):
    lp.box(f"shoe{i}", SHOP[0] + 1.5 + i * 1.2, SHOP[1] + .35, 1.0 + (i % 3) * 1.0,
           SHOP[0] + 2.3 + i * 1.2, SHOP[1] + .6, 1.6 + (i % 3) * 1.0,
           lp.mat(random.choice(["car_red", "car_yellow", "car_blue", "car_white", "wall_mint"])))
for i, (name, (rect, facing, _)) in enumerate(LAUNDRIES.items()):
    anchors[name] = lp.shop_building(f"laundry{i}", *rect, facing, "wall_mint", "laundry_blue", h=6.5)
for x in (4, 31):
    lp.tree(f"shop_tree{x}", x, 11, 1.1)

# ------------------------------------------------------------ garis rute + motor
arrivals = []
for i, (name, (_, _, pts)) in enumerate(LAUNDRIES.items()):
    # garis rute (pita kuning yang "tergambar")
    ob, cu = lp.poly_curve(f"route{i}", pts, z=0.0)
    cu.bevel_depth = .7
    cu.bevel_resolution = 0
    cu.bevel_factor_mapping_end = "SPLINE"
    ob.location.z = .35
    ob.scale.z = .18
    ob.data.materials.append(lp.mat("route", emission=0.6))
    f0 = 4 + i * 6
    cu.bevel_factor_end = 0.0
    cu.keyframe_insert("bevel_factor_end", frame=f0)
    cu.bevel_factor_end = 1.0
    cu.keyframe_insert("bevel_factor_end", frame=f0 + 30)

    # jalur motor
    pob, pcu = lp.poly_curve(f"path{i}", pts, z=.15)
    pcu.use_path = True
    pob.hide_render = True
    L = lp.path_length(pts)
    speed = 26.0 / FPS / L  # faktor per frame (timelapse)
    for k, start in enumerate((f0 + 8, f0 + 40)):
        s = lp.scooter(f"scoot{i}_{k}", scale=2.3)
        c = s.constraints.new("FOLLOW_PATH")
        c.target = pob
        c.use_curve_follow = True
        c.use_fixed_location = True
        c.forward_axis = "FORWARD_X"
        c.up_axis = "UP_Z"
        end_frame = min(N_FRAMES + 1, start + int(1 / speed))
        c.offset_factor = 0.0
        c.keyframe_insert("offset_factor", frame=start)
        c.offset_factor = min(1.0, (end_frame - start) * speed)
        c.keyframe_insert("offset_factor", frame=end_frame)
        for ob_ in [s] + list(s.children):
            ob_.hide_render = True
            ob_.keyframe_insert("hide_render", frame=1)
            ob_.hide_render = False
            ob_.keyframe_insert("hide_render", frame=start)
            if end_frame <= N_FRAMES:
                ob_.hide_render = True
                ob_.keyframe_insert("hide_render", frame=end_frame)
        if end_frame <= N_FRAMES:
            arrivals.append(end_frame)

# mobil di jalan primer
random.seed(11)
for k in range(9):
    lane = random.choice([-5.2, -2, 2, 5.2])
    direction = 1 if lane < 0 else -1
    c = lp.car(f"car{k}")
    x0 = random.uniform(-110, 110)
    c.rotation_euler.z = 0 if direction > 0 else math.pi
    c.location = (x0, lane, 0)
    c.keyframe_insert("location", frame=1)
    c.location = (x0 + direction * 12 * N_FRAMES / FPS, lane, 0)
    c.keyframe_insert("location", frame=N_FRAMES)
for k in range(4):
    c = lp.car(f"carv{k}")
    lane = random.choice([-2.2, 2.2])
    direction = 1 if lane > 0 else -1
    y0 = random.uniform(-100, 100)
    c.rotation_euler.z = math.pi / 2 if direction > 0 else -math.pi / 2
    c.location = (lane, y0, 0)
    c.keyframe_insert("location", frame=1)
    c.location = (lane, y0 + direction * 10 * N_FRAMES / FPS, 0)
    c.keyframe_insert("location", frame=N_FRAMES)

# ------------------------------------------------------------ kamera drone
target = bpy.data.objects.new("target", None)
target.location = (2, 8, 0)
lp._link(target)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
lp._link(cam)
cam.data.lens = 25
cam.data.sensor_fit = "VERTICAL"
cam.data.sensor_height = 24
cam.data.shift_y = 0.10
cam.data.clip_end = 2000
tc = cam.constraints.new("TRACK_TO")
tc.target = target
tc.track_axis = "TRACK_NEGATIVE_Z"
tc.up_axis = "UP_Y"
sc.camera = cam
R, H = 135, 140
for f, az in ((1, -138), (N_FRAMES, -127)):
    a = math.radians(az)
    cam.location = (target.location.x + R * math.cos(a), target.location.y + R * math.sin(a), H)
    cam.keyframe_insert("location", frame=f)

# ------------------------------------------------------------ render + anchors
f_lo, f_hi = map(int, args.frames.split("-"))
os.makedirs(os.path.join(args.out, "frames"), exist_ok=True)
data = {"fps": FPS, "res": [rx, ry], "arrivals": sorted(arrivals), "frames": {}}
for f in range(1, N_FRAMES + 1):
    sc.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    pos = {}
    from mathutils import Vector
    for name, p in anchors.items():
        v = world_to_camera_view(sc, cam, Vector(p))
        pos[name] = [round(v.x * rx, 1), round((1 - v.y) * ry, 1)]
    data["frames"][f] = pos
with open(os.path.join(args.out, "anchors.json"), "w") as fh:
    json.dump(data, fh)

for f in range(f_lo, f_hi + 1):
    sc.frame_set(f)
    sc.render.filepath = os.path.join(args.out, "frames", f"{f:04d}.png")
    bpy.ops.render.render(write_still=True)
print("DONE", f_lo, f_hi)
