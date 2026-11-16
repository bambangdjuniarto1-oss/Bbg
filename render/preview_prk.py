"""Render gambar cek aset/dunia Juru Parkir.  python3 render/preview_prk.py -- OUTDIR [res] [samples] [shot,...]"""
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowpoly as lp  # noqa: E402
import world as W  # noqa: E402
import world_amdk as M  # noqa: E402
import world_laundry as L  # noqa: E402
import world_prk as R  # noqa: E402
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
R.setup_prk_light()
night = bool(only and "a_night" in only)
info = R.build_street(night_lamps=1.0 if night else 0.0)
jk = R.jukir("jk", (R.JUKIR_POS[0], R.JUKIR_POS[1], .2), 0)
L.pose(jk, "wave")
ks = R.kasir("ks", (10.5, R.STORE[1] + 2.6, .2), 0)
if night:
    R.day_night(1, 2, info["store"], info["lamps"])

X = 1500
need_props = not only or any(s[0] in "bc" for s in only)
if need_props:
    mb = W.MB("pg")
    mb.box(X - 30, -20, -1, X + 30, 40, 0, "pk_pave")
    R.note(mb, X - 10, -6, .1, "n2k", 1.4)
    R.note(mb, X - 7, -6, .1, "n5k", 1.4)
    mb.build()
    st, h = R.money_stack("ms", 24, (X - 2, -4, 0))
    st2, h2 = R.money_stack("ms2", 9, (X + 2, -4, 0), "money_dk")
    fr, sc = R.glow_screen("scr", (X + 9, 0, 0))
    pg = R.pengelola("pg1", (X + 9, -1.2, 0), 0)
    s = R.sun_icon("sun1")
    s.location = (X - 8, -2, 9)
    cm = W.MB("cl")
    R.cloud(cm, X - 2, -2, 10, 1.4)
    cm.build()
    R.rain("rn", (X - 2, -2), (6, 3), 8, 120)
    cd = R.card("cd")
    cd.location = (X + 4, -6, 6)
    R.motor("mt", (X - 12, 2, 0), 0, "bk_blue")
    R.car("cr", (X + 18, 4, 0), 0, "cr_red")
    jk2 = R.jukir("jk2", (X - 5, -8, 0), 0)
    L.pose(jk2, "wave")
    spots = None
    mpo = W.MB("mp_o")
    mpo.build()

cam, tgt = SC.make_camera(lens=18, shift_y=0)
shots = {
    "a_aerial": ((-40, -95, 48), (0, -2, 2), 20),
    "a_lot": ((-2, -24, 5.5), (2, -2, 2.6), 20),
    "a_night": ((-14, -46, 14), (0, 0, 3), 20),
    "b_props": ((X, -36, 9), (X, 0, 4), 20),
}
for name, (pos, tg, lens) in shots.items():
    if only and name not in only:
        continue
    cam.location = pos
    tgt.location = tg
    cam.data.lens = lens
    bpy.context.scene.frame_set(30 if name != "a_night" else 2)
    bpy.context.scene.render.filepath = os.path.join(out, name + ".png")
    bpy.ops.render.render(write_still=True)
print("DONE")
