"""Render gambar cek aset/dunia hotel.  python3 render/preview_hotel.py -- OUTDIR [res] [samples] [shot,...]"""
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowpoly as lp  # noqa: E402
import world as W  # noqa: E402
import world_hotel as H  # noqa: E402
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
info = H.build_world(branches=True)

# set studio
SC.studio_floor(300, 0, size=22, wall=False)
mb, _ = H.hotel("cut", cut=True, rooms=True, front=False)
mb.build((300, 0, -H.Z))
H.room_set("room", 400, 0)
H.lobby_set("lobby", 500, 0)
H.facilities_set("fac", 600, 0)
SC.studio_floor(700, 0, size=10, wall=False)
H.money_pallet("money").build((700, 0, 0))
H.calculator("calc").build((705, -3, 0))

cam, tgt = SC.make_camera(lens=18, shift_y=.1)
shots = {
    "a_aerial": ((-90, -120, 95), (0, -6, 0), 18),
    "b_hotel": ((-14, -42, 7), (0, -6, 10), 18),
    "c_mm": ((10, -12, 4), (0, -38, 3), 22),
    "d_cut": ((300 - 18, -42, 14), (300, 0, 11), 22),
    "e_room": ((400 - 6, -9.5, 5.2), (400 + .2, .8, 1.0), 20),
    "f_lobby": ((500 - 4, -14, 6), (500 + .5, 1.5, 1.6), 20),
    "g_fac": ((600 - 4, -22, 13), (600, 0, 1.2), 22),
    "h_money": ((700 - 8, -14, 9), (700, -1, 1.2), 26),
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
