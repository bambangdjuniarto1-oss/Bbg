"""Render gambar cek aset/dunia laundry koin.  python3 render/preview_laundry.py -- OUTDIR [res] [samples] [shot,...]"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowpoly as lp  # noqa: E402
import world as W  # noqa: E402
import world_laundry as L  # noqa: E402
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
L.H.glassy("wm_glass", .45)
L.H.glassy("lw_glass", .35)
info = L.build_world()

# deret karakter
SC.studio_floor(300, 0, size=16, wall=False)
holds = [None, "phone", "basket", "tablet", None, "clothes", "tablet", "wrench", None, None]
for k, (nm, hold) in enumerate(zip(L.LOOKS, holds)):
    p = L.character(f"c{k}", nm, (300 - 6.75 + k * 1.5, 0, 0), 0, 1.0, hold=hold)
    if nm == "cowok":
        L.pose(p, "wave")
    if nm == "bapak":
        L.pose(p, "cheer")
it = L.interior_set("int", 500, 0)
L.conventional_set("conv", 700, 0)
SC.studio_floor(900, 0, size=10, wall=False)
mb = W.MB("wm1")
door = L.washer(mb, 900, 0, 0, 1.6)
mb.build()
L.drum_clothes("dc", door, 1.6)
L.kiosk("k1").location = (902.6, 0, 0)

cam, tgt = SC.make_camera(lens=18, shift_y=0)
shots = {
    "a_aerial": ((-80, -110, 85), (0, -6, 0), 18),
    "b_front": ((-12, -36, 6), (0, -8, 4.5), 20),
    "c_chars": ((300 - 3.75, -13, 2.2), (300 - 3.75, 0, 1.1), 50),
    "c2_chars": ((300 + 3.75, -13, 2.2), (300 + 3.75, 0, 1.1), 50),
    "c3_face": ((300 - 6.0, -4.5, 2.0), (300 - 6.0, 0, 1.55), 50),
    "d_int": ((500 - 7, -15, 10), (500 + .5, 1.5, 1.2), 18),
    "e_conv": ((700 - 4, -11, 7), (700, 0, 1.2), 22),
    "f_wm": ((900 - 2, -6, 3.2), (900.8, 0, 1.3), 30),
    "g_kos": ((-14, -24, 9), (0, -44, 5), 20),
    "h_city": ((40, -40, 30), (40, 10, 5), 18),
}
for name, (pos, tg, lens) in shots.items():
    if only and name not in only:
        continue
    cam.location = pos
    tgt.location = tg
    cam.data.lens = lens
    bpy.context.scene.render.filepath = os.path.join(out, name + ".png")
    bpy.ops.render.render(write_still=True)
print("DONE")
