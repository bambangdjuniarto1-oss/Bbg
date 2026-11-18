"""Latar 3D thumbnail "Liquid Vape Part 2 — Raka bikin brand" (gaya feed @juniart.ai): kota diorama melayang
di dunia neon. Tengah plaza: menara modal Rp90 juta (produksi / desain / marketing + balok emas cukai & pajak
di puncak) di atas alas neon. Kiri: toko brand RAKA LIQUID + Raka angkat bahu di meja racik rasa.
Kanan: KAS NEGARA (ke mana balok emas pergi) + toko vape.

  python3 render/thumb_brd_scene.py -- --out BG.png [--res 1080x1920] [--samples 64] [--cam x,y,z,tx,ty,tz,lens,shift]
"""
import argparse
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowpoly as lp  # noqa: E402
import world as W  # noqa: E402
import world_amdk as M  # noqa: E402
import world_brd as B  # noqa: E402
import world_laundry as L  # noqa: E402
import world_vap as V  # noqa: E402
import scenes_vap as SV  # noqa: E402
from scenes import make_camera  # noqa: E402

Z0 = .24
COSTS = [(25, "n_cyan"), (8, "n_purple"), (15, "n_pink"), (42, "n_gold")]


def build(unit=.115, w=5.4):
    SV.city(1, focus=None, center_clear=48, traffic=True, people=True)
    # kiri: toko brand Raka; kanan-depan menara: meja racik rasa + Raka angkat bahu
    B.brand_store("bs", (-13, 9, Z0), "RAKA LIQUID")
    B.lab_table("lab", (8.5, -11.2, Z0))
    L.pose(B.raka("raka", (8.5, -9.8, Z0), 0), "shrug")
    # kanan: KAS NEGARA + toko vape
    V.gov_day("gov", (18, 12, Z0), w=16.0, d=10.0)
    V.vape_store_day("ts", (24, -1, Z0), 11.0, 8.0, sign="TOKO VAPE")
    # tengah: menara modal di alas neon
    V.disc_ped("ped", 5.2, "n_gold", (0, -7, Z0), em=4.0, h=.8)
    z = Z0 + .8
    for i, (jt, k) in enumerate(COSTS):
        h = jt * unit
        V.pillar(f"mt{i}", h, w, w, k, 1.8 if k != "n_gold" else 2.6, 5.0, (0, -7, z))
        z += h + .08
    V.crown("cr", (0, -7, z + .9), 1.6, "n_gold", 6.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--res", default="1080x1920")
    ap.add_argument("--samples", type=int, default=64)
    ap.add_argument("--cam", default="-34,-62,44,1,-8,7.2,27,.20")
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])
    lp.reset()
    W.PLACED.clear()
    rx, ry = map(int, a.res.split("x"))
    lp.setup_render(rx, ry, a.samples)
    W.setup_world_light()
    M.glass_setup()
    build()
    v = [float(x) for x in a.cam.split(",")]
    cam, tgt = make_camera(lens=v[6], shift_y=v[7])
    cam.location = tuple(v[:3])
    tgt.location = tuple(v[3:6])
    sc = bpy.context.scene
    sc.frame_set(1)
    sc.render.filepath = a.out
    bpy.ops.render.render(write_still=True)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
