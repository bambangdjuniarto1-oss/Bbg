"""Pratinjau aset Nikahan: --set city (diorama: gedung resepsi, tenda, pelaminan, tamu, katering) atau
--set neon (kalender, timbangan, jebakan, hati, piring, amplop, uang).

  python3 render/preview_nkh.py -- --set city --out OUT.png [--res 540x960] [--samples 16] [--cam x,y,z,tx,ty,tz,lens]
"""
import argparse
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowpoly as lp  # noqa: E402
import world as W  # noqa: E402
import world_amdk as M  # noqa: E402
import world_laundry as L  # noqa: E402
import world_vap as V  # noqa: E402
import world_nkh as N  # noqa: E402
from scenes import make_camera  # noqa: E402


def city_set():
    import scenes_vap as SV
    SV.city(1, focus=None, people=False)
    N.wedding_hall("hall", (0, 8, .24))
    N.tent("tent", -10, -15, 10, -4, 4.4, (0, 0, .24))
    N.pelaminan("pel", (0, -8.6, .24), .8)
    g = N.groom("dimas", (-.7, -6.2, .24 + .4), 0)
    b = N.bride("sari", (.7, -6.2, .24 + .4), 0)
    mb = W.MB("tables")
    for k, (x, y) in enumerate(((-7, -11), (-3.5, -13), (3.5, -13), (7, -11))):
        N.round_table(mb, x, y, .24, 1.0, 6, k)
    mb.build()
    N.buffet("buf", (-15, -8, .24), 7.0, math.pi / 2)
    N.amplop_box("abox", (13, -12, .24), .9)
    for k in range(6):
        N.guest(f"g{k}", k, (-4 + k * 1.6, -15.5, .24), 0)
    N.katering_shop("kt", (30, 8, .24))
    N.katering_van("van", (22, -20, .24), 0)
    N.chef("chef", (30, 2, .24), 0)


def neon_set():
    V.setup_neon_light()
    V.stage(center=(0, 0), size=70, fade=(10, 50))
    V.rig((0, 0, 3), 2600, 1800, 1.4)
    N.calendar("cal", (-9, 6, 0), .8)
    b = N.balance("bal", (0, 4, 0), .9)
    N.balance_key(b, 1, 14)
    t = N.trap("trap", (9, 2, 0), .8)
    N.heart("ht", (-6, -4, 2.4), 1.2)
    N.plates_grid("pl", 12, 6, .75, (4, -6, 0), 1.0)
    N.envelope_pile("ep", 40, (-1, -6, 0), 1.6)
    N.money("mn", 12, (9, -4, 0), 2, 2)
    N.envelope("e1", (-3, -9, 1.5), 1.6, upright=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="city")
    ap.add_argument("--out", required=True)
    ap.add_argument("--res", default="540x960")
    ap.add_argument("--samples", type=int, default=16)
    ap.add_argument("--cam", default=None)
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])
    lp.reset()
    W.PLACED.clear()
    rx, ry = map(int, a.res.split("x"))
    lp.setup_render(rx, ry, a.samples)
    bpy.context.scene.cycles.denoising_prefilter = "FAST"
    bpy.context.scene.cycles.denoising_quality = "FAST"
    W.setup_world_light()
    M.glass_setup()
    if a.set == "city":
        city_set()
        cam_d = (-38, -62, 40, 2, -4, 3, 24)
    else:
        neon_set()
        cam_d = (0, -30, 16, 0, 0, 3, 24)
    v = [float(x) for x in a.cam.split(",")] if a.cam else cam_d
    cam, tgt = make_camera(lens=v[6], shift_y=0)
    cam.location = v[:3]
    tgt.location = v[3:6]
    sc = bpy.context.scene
    sc.render.filepath = a.out
    bpy.ops.render.render(write_still=True)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
