"""Render gambar cek aset/dunia AMDK.  python3 render/preview_amdk.py -- OUTDIR [res] [samples] [shot,...]"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowpoly as lp  # noqa: E402
import world as W  # noqa: E402
import world_laundry as L  # noqa: E402
import world_amdk as M  # noqa: E402
import scenes as SC  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
out = args[0]
res = args[1] if len(args) > 1 else "540x960"
smp = int(args[2]) if len(args) > 2 else 6
only = set(args[3].split(",")) if len(args) > 3 else None
os.makedirs(out, exist_ok=True)
lp.reset()
rx, ry = map(int, res.split("x"))
lp.setup_render(rx, ry, smp)
W.setup_world_light()
M.glass_setup()
info = M.build_world()
M.road_trucks(60)

# produk
M.studio_epoxy(300, 0, size=12)
for k, kind in enumerate(("cup", "b600", "b1500", "galon")):
    x = 300 - 4.5 + k * 3
    M.pedestal(f"pd{k}").build((x, 0, 0))
    M.product(f"pr{k}", kind, 1.0).build((x, 0, .42))
mb = W.MB("cartons")
M.carton_stack(mb, 300 - 3, 4, 0, 2, 2, 3)
M.carton_stack(mb, 300 + 2, 4, 0, 2, 2, 2, kind="bottle")
mb.build()
# karyawan
M.studio_epoxy(400, 0, size=12)
for k, kind in enumerate(M.WORKER_LOOKS):
    p = M.worker(f"w{k}", kind, (400 - 4.5 + k * 1.5, 0, 0), 0, 1.0, hold="tablet" if kind == "qc" else None)
    if kind == "buruh":
        L.pose(p, "wave")
# kendaraan
M.studio_epoxy(500, 0, size=16)
t = M.tronton("t1", "box")
t.location = (500, 0, 0)
t.rotation_euler.z = -.5
t2 = M.tronton("t2", "galon")
t2.location = (500 + 4, 9, 0)
t2.rotation_euler.z = -.5
f = M.forklift("f1")
f.location = (500 - 7, -5, 0)
# lini produksi
pl = M.production_line("pl", 700, 0)
M.bottles_on_line("bt", pl["x0"], pl["x1"], 0, pl["zc"], 60)
for k, (kind, x, y) in enumerate((("operator", 696.5, -2.2), ("qc", 703, -2.0), ("buruh", 710, -4.0))):
    M.worker(f"pw{k}", kind, (x, y, 0), .3, hold="tablet" if kind == "qc" else None)
# peta
mo, polys = M.indonesia_map("map", 0, 600)
for k, p in enumerate(M.map_points(polys, 80)):
    M.pin(f"pin{k}", (p[0], p[1], 1.0), .9)

cam, tgt = SC.make_camera(lens=18, shift_y=0)
shots = {
    "a_aerial": ((-80, -110, 85), (0, -2, 0), 18),
    "b_factory": ((-26, -48, 18), (-1, -4, 4), 22),
    "b2_factory": ((30, -40, 14), (2, -2, 4), 22),
    "c_prod": ((300, -12, 4.0), (300, 0, 1.4), 32),
    "d_workers": ((400, -12, 2.2), (400, 0, 1.1), 40),
    "d2_face": ((400 + 1.5, -4.5, 2.0), (400 + 1.5, 0, 1.6), 50),
    "e_truck": ((500 + 14, -16, 7), (500 + 1, 2, 2.2), 24),
    "f_line": ((700 - 2, -17, 9), (700 + .5, 1.5, 2.0), 18),
    "g_map": ((0, 600 - 70, 70), (0, 600, 0), 22),
    "h_city": ((40, -60, 40), (20, -20, 3), 18),
}
for name, (pos, tg, lens) in shots.items():
    if only and name not in only:
        continue
    cam.location = pos
    tgt.location = tg
    cam.data.lens = lens
    bpy.context.scene.frame_set(30)
    bpy.context.scene.render.filepath = os.path.join(out, name + ".png")
    bpy.ops.render.render(write_still=True)
print("DONE")
