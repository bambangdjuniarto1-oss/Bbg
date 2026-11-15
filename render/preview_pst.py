"""Render gambar cek aset/dunia Pestapora.  python3 render/preview_pst.py -- OUTDIR [res] [samples] [shot,...]"""
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowpoly as lp  # noqa: E402
import world as W  # noqa: E402
import world_amdk as M  # noqa: E402
import world_pst as P  # noqa: E402
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
P.setup_fest_light()
need_world = not only or any(s.startswith("a_") for s in only)
if need_world:
    info = P.build_fest()
    bd = P.band("bd", (0, P.MAIN[1] - 1), P.DECK_H)
    P.backstage("bk", (0, P.MAIN[1] + P.STAGE_D / 2 + 2))

X = 1500
need_props = not only or any(s[0] in "bcd" for s in only)
if need_props:
    ds = P.data_stage()
    for o in bpy.data.objects:
        if o.name.startswith("ds") and o.parent is None:
            o.location.x += X
    Y2 = 220
    mb = W.MB("pg")
    mb.box(X - 18, Y2 - 8, -1, X + 18, Y2 + 12, 0, "f_grass2")
    mb.build()
    objs = [P.ticket("tk1", "Rp225RB"), P.ticket("tk2", "Rp650RB", "tk_gold", "tk_gold2"), P.wristband("wb"),
            P.warn_sign("wn")]
    for k, o in enumerate(objs):
        o.location = (X - 13 + k * 5.0, Y2 - 4, 0.5 if k == 2 else 0)
    for k, kind in enumerate(("artis", "panggung", "venue", "keamanan", "kru", "operasional")):
        ic = P.cost_icon("ic" + kind, kind)
        ic.location = (X - 10 + k * 3.6, Y2 + 3, 0)
    for k, kind in enumerate(("tent", "dome", "box", "open", "hall")):
        P.small_stage(f"sst{k}", (X - 40 + k * 22, Y2 + 40), kind)
    fw = P.ferris_wheel("fwp", (X + 80, Y2 + 40), 12)
    bb = P.brand_booth("bbp", "sp1", "sp1b")
    bb.location = (X - 8, Y2 + 70, 0)
    mm = P.merch_stand("mp")
    mm.location = (X + 6, Y2 + 66, 0)
    ft = P.food_truck("ftp")
    ft.location = (X + 16, Y2 + 66, 0)
    mb = W.MB("stp")
    import random
    P.food_stall(mb, X - 20, Y2 + 66, "tn_red", random.Random(1))
    mb.build()
    gt = P.gate("gp")
    gt.location = (X, Y2 + 100, 0)
    for k in range(3):
        P.firework(f"fwk{k}", (X - 10 + k * 10, 60, 30), 20, ("led_m", "led_c", "tk_gold")[k])

cam, tgt = SC.make_camera(lens=18, shift_y=0)
shots = {
    "a_aerial": ((-70, -190, 95), (0, 40, 8), 18),
    "a_crowd": ((-14, -10, 9), (0, 58, 9), 20),
    "a_back": ((40, 130, 24), (0, 70, 4), 20),
    "b_data": ((X, -30, 8), (X, 2, 5.5), 20),
    "c_props": ((X, 220 - 26, 7), (X, 220, 1.6), 20),
    "d_stages": ((X + 10, 220 - 30, 30), (X + 10, 270, 8), 18),
    "d_booth": ((X, 220 + 40, 12), (X, 290, 3), 20),
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
