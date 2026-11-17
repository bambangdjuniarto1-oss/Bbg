"""Render cek aset/gaya neon Liquid Vape.  python3 render/preview_vap.py -- OUTDIR [res] [samples] [shot,...]"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowpoly as lp  # noqa: E402
import world as W  # noqa: E402
import world_amdk as M  # noqa: E402
import world_vap as V  # noqa: E402
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
V.setup_neon_light()
V.stage()
V.rig((0, 0, 1.5))
b = V.bottle("b1", 1.0, (("lq_toko", 30), ("lq_brand", 48), ("lq_negara", 42)), pita=True, loc=(-2.6, 0, .5))
V.disc_ped("pd", 1.8, "n_pink", (-2.6, 0, 0))
V.pillar("pl", 5.0, loc=(2.2, 0, 0), key_="n_pink")
V.pillar("pl2", 3.0, loc=(5.2, 1, 0), key_="n_gold")
V.vape_shop("shop", (-16, 14, 0))
V.brand_factory("fac", (2, 18, 0))
V.gov_building("gov", (20, 14, 0))
for i, k in enumerate(("bahan", "botol", "produksi", "distribusi", "marketing")):
    V.icon("ic%d" % i, k, .9, (-8 + i * 3.2, -6, 0))
V.crown("cr", (5.2, 1, 3.3), .8)
V.qmark("q", (-6.5, 2, 1))
V.xmark("x", (9, -2, 2))
V.gate("gt", (12, 4, 0))
o, li = V.siren("sr", (8.5, 4, 0))
V.market_shelves("mk", (0, 40, 0), rows=2)
V.pie("pie", [("lq_toko", 30), ("lq_brand", 48), ("lq_negara", 42)], loc=(-12, -2, 0))
V.phone("ph", (14, -4, 0))
V.paper_plane("pp", (16, -5, 3))
V.magnifier("mg", (-4, -8, 2.5))
V.neon_sign("ns", "BARU TAHU", (0, 10, 6), 1.2)

cam, tgt = SC.make_camera(lens=20, shift_y=0)
shots = {
    "a_hero": ((-2.6, -9, 3.0), (-1.0, 0, 2.2), 32),
    "b_wide": ((0, -40, 16), (2, 6, 2), 20),
    "c_low": ((-1, -12, .6), (1, 0, 3.5), 18),
    "d_top": ((0, -6, 30), (0, 2, 0), 22),
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
