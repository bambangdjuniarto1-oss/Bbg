"""Render gambar cek aset/dunia sawit.  python3 render/preview_sawit.py -- OUTDIR [res] [samples] [shot,...]"""
import os
import random
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowpoly as lp  # noqa: E402
import world as W  # noqa: E402
import world_laundry as L  # noqa: E402
import world_amdk as M  # noqa: E402
import world_sawit as K  # noqa: E402
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
need_world = not only or any(s.startswith(("a_", "h_")) for s in only)
if need_world:
    info = K.build_world(burnt=(-60, -70, -12, -30))
    K.road_trucks(60)
    K.smoke("sm", [(-40, -50, 1), (-25, -45, 1), (-50, -38, 1)], 60)

X = 1500
# tahapan pohon
mb = W.MB("stages")
mb.box(X - 14, -8, -1, X + 14, 8, 0, "kb_grass")
for k, st in enumerate(("bibit", "muda", "remaja", "dewasa")):
    K.palm(mb, X - 10 + k * 6.5, 0, 0, 1.0, st, random.Random(k))
mb.build()
# pekerja & alat
Y2 = 40
mb = W.MB("st2")
mb.box(X - 14, Y2 - 8, -1, X + 14, Y2 + 8, 0, "kb_grass")
mb.build()
for k, (kind, hold) in enumerate((("pemanen", "egrek"), ("pengangkut", "gerobak"), ("pemanen2", None),
                                  ("pemupuk", "karung"), ("penanam", "bibit"), ("mandor", None))):
    K.worker(f"w{k}", kind, (X - 9 + k * 3.4, Y2, 0), 0, hold=hold)
wb = K.wheelbarrow("wb_solo", "tbs")
wb.location = (X + 10, Y2 + 4, 0)
wb.rotation_euler.z = .8
tb, tp = K.tph("tphA", 3)
tb.location = (X + 10, Y2 - 4, 0)
# kendaraan
Y3 = 90
mb = W.MB("st3")
mb.box(X - 16, Y3 - 10, -1, X + 16, Y3 + 10, 0, "kb_soil")
mb.build()
t = K.truk_tbs("tk", True)
t["root"].location = (X, Y3, 0)
t["root"].rotation_euler.z = -.5
ex = K.excavator("ex")
ex["root"].location = (X - 9, Y3 + 6, 0)
ex["root"].rotation_euler.z = -.3
sk = K.sack_pile("sk").build((X + 9, Y3 + 4, 0))
# petak + kalender
Y4 = 140
pt = K.plot_tile("pt", "dewasa", 3, sign="1 HA")
pt.location = (X - 7, Y4, 0)
pt2 = K.plot_tile("pt2", "muda", 3, seed=3)
pt2.location = (X + 13, Y4, 0)
K.calendar("cal", "10", (X + 3, Y4 - 14, 0))

cam, tgt = SC.make_camera(lens=18, shift_y=0)
shots = {
    "a_aerial": ((-70, -120, 80), (10, -10, 0), 20),
    "a2_low": ((-28, -34, 10), (0, -4, 4), 20),
    "b_stages": ((X - 0.5, -30, 7), (X - .5, 0, 4), 22),
    "c_workers": ((X - 1, Y2 - 24, 6), (X - 1, Y2, 3.0), 22),
    "c2_close": ((X - 2, Y2 - 9, 3.0), (X - 5.5, Y2, 2.6), 22),
    "d_vehicles": ((X + 14, Y3 - 22, 9), (X - 1, Y3 + 2, 2.2), 24),
    "e_plots": ((X + 3, Y4 - 34, 18), (X + 3, Y4, 1.5), 26),
    "h_burnt": ((-80, -95, 30), (-36, -50, 2), 22),
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
