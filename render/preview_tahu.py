"""Render gambar cek aset/dunia tahu.  python3 render/preview_tahu.py -- OUTDIR [res] [samples]"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowpoly as lp  # noqa: E402
import world as W  # noqa: E402
import world_tahu as T  # noqa: E402
import scenes as SC  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
out = args[0]
res = args[1] if len(args) > 1 else "540x960"
smp = int(args[2]) if len(args) > 2 else 6
os.makedirs(out, exist_ok=True)
lp.reset()
rx, ry = map(int, res.split("x"))
lp.setup_render(rx, ry, smp)
W.setup_world_light()
info = T.build_world()
print("customers", len(info["customers"]))

# karakter + motor di depan rumah pelanggan
b = T.tahu_bike("bike", scale=1.25)
b.location = (-2.0, -28.0, .05)
s = T.seller("seller", "stand").build()
s.location = (.6, -29.0, .25)
s.rotation_euler.z = math.pi
s.scale = (1.25,) * 3
c = T.customer("cust", "red_aw", hijab=True).build()
c.location = (0, HY := T.HOME_Y + 5.2, .25)
c.rotation_euler.z = math.pi
c.scale = (1.25,) * 3
p = T.tofu_pack("pack", s=.5).build((300, 0, 1.08))
studio = W.MB("st")
SC.studio_floor(300, 0, size=8)
st = W.MB("tbl")
st.box(297.5, -1, 0, 302.5, 1, 1.0, "wood")
T.tampah(st, 300, -.2, 1.0, 1.0)
for i, (dx, dy, rz) in enumerate(((-.3, -.45, 0), (.3, -.45, .1), (-.3, .1, -.1), (.3, .1, .05), (0, -.2, .2))):
    T.tofu(st, 300 + dx, -.2 + dy, 1.12 + (.32 if i == 4 else 0), .5)
st.build()
p.location = (301.5, .6, 1.0)
for k, bb in enumerate(range(3)):
    pk = T.tofu_pack(f"pk{k}", s=.16).build((-6 + k * 1.2, -15.8, .25))
T.pin("pin").build((info["customers"][3]["pos"][0], info["customers"][3]["pos"][1], info["customers"][3]["pos"][2] + 1))

cam, tgt = SC.make_camera(lens=18, shift_y=.1)
shots = {
    "a_aerial": ((-80, -110, 90), (0, -6, 0), 18, None),
    "b_factory": ((-6, -36, 7), (0, -8, 5), 18, None),
    "c_street": ((3.5, -19.5, 3.0), (-.5, -31.5, 2.0), 20, None),
    "d_bike": ((4.5, -24.5, 2.2), (-1.4, -28.2, 1.3), 30, None),
    "e_studio": ((300, -5.2, 3.3), (300.4, 0, 1.4), 34, None),
}
for name, (pos, tg, lens, _) in shots.items():
    cam.location = pos
    tgt.location = tg
    cam.data.lens = lens
    bpy.context.scene.render.filepath = os.path.join(out, name + ".png")
    bpy.ops.render.render(write_still=True)
print("DONE")
