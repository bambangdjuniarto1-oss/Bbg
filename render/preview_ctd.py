"""Render gambar cek aset/dunia CTD.  python3 render/preview_ctd.py -- OUTDIR [res] [samples] [shot,...]"""
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowpoly as lp  # noqa: E402
import world as W  # noqa: E402
import world_amdk as M  # noqa: E402
import world_ctd as C  # noqa: E402
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
need_city = not only or any(s.startswith("a_") for s in only)
if need_city:
    C.setup_city_light()
    info = C.build_city()
    C.city_traffic(60, hwy=info.get("hwy"))
    ph = C.phone_channel("ph", 2.2)
    ph.location = (-12, -14, .16)
    ph.rotation_euler.z = .3

X = 1500
st = C.studio("st", (X, 0, 0))
# props
Y2 = 220
mb = W.MB("pg")
mb.box(X - 16, Y2 - 8, -1, X + 16, Y2 + 10, 0, "ct_walk")
mb.build()
objs = [C.play_plaque("pq", 1.0), C.eye_token("ey", 1.0, (0, 0, 1.0)), C.view_cube("vc", 1.0), C.coin("cn", 1.2),
        C.sponsor_box("sa", "sp_a"), C.sponsor_box("sb", "sp_b"), C.member_card("mc", .8), C.stamp("sm", "SIMULASI", .6)]
for k, o in enumerate(objs):
    o.location = (X - 12 + k * 3.4, Y2 - 4, o.location.z)
mm = C.money_machine("mm", .8)
mm["body"].location = (X - 8, Y2 + 5, 0)
for k, kind in enumerate(("host", "tamu", "transport", "studio", "alat", "marketing")):
    ic = C.cost_icon("ic" + kind, kind)
    ic.location = (X + 1 + k * 2.6, Y2 + 5, 0)
cr = C.crowd("cr", 40, X + 3, Y2 + 9, X + 14, Y2 + 14, card_frac=.4)
# orang
Y3 = 300
mb = W.MB("pp")
mb.box(X - 12, Y3 - 6, -1, X + 12, Y3 + 6, 0, "ct_walk")
mb.build()
for k, lk in enumerate(("host", "pejabat", "artis", "kru1", "kru2", "kru3", "kru4", "kru5", "kru6")):
    C.person(f"p{k}", lk, (X - 10 + k * 2.5, Y3, 0), 0, extra=("headset",) if k in (3, 6) else ())

cam, tgt = SC.make_camera(lens=18, shift_y=0)
shots = {
    "a_aerial": ((-150, -230, 140), (0, 0, 10), 22),
    "a_plaza": ((-30, -60, 9), (0, 10, 16), 18),
    "b_studio": ((X - 7, -19, 9.5), (X, .5, 2.4), 20),
    "b_close": ((X - 3.5, -7.5, 3.2), (X, .4, 1.9), 22),
    "c_props": ((X - .5, Y2 - 26, 9), (X - .5, Y2 + 2, 1.5), 18),
    "d_people": ((X, Y3 - 16, 3.5), (X, Y3, 1.4), 20),
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
