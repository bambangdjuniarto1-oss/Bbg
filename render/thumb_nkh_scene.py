"""Latar 3D thumbnail "Nikahan Rp100 Juta" (gaya feed @juniart.ai): kota diorama melayang di dunia neon.
Tengah plaza: amplop raksasa di atas alas neon (monumen). Kiri: gedung resepsi + pelaminan + pengantin.
Kanan: usaha katering + koki pemilik bersorak + menara uang tinggi (yang untung).

  python3 render/thumb_nkh_scene.py -- --out BG.png [--res 1080x1920] [--samples 64] [--cam x,y,z,tx,ty,tz,lens,shift]
"""
import argparse
import math
import os
import random
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowpoly as lp  # noqa: E402
import world as W  # noqa: E402
import world_amdk as M  # noqa: E402
import world_laundry as L  # noqa: E402
import world_nkh as N  # noqa: E402
import world_vap as V  # noqa: E402
import scenes_vap as SV  # noqa: E402
from scenes import make_camera  # noqa: E402

Z0 = .24


def build():
    SV.city(1, focus=None, center_clear=48, traffic=True, people=True)
    rnd = random.Random(5)
    # kiri: gedung resepsi + pelaminan + pengantin + tamu
    N.wedding_hall("hall", (-14.5, 9, Z0), w=17.0, d=10.0, h=8.0)
    N.pelaminan("pel", (-14.5, -1.5, Z0), .9)
    N.groom("dimas", (-15.15, -1.5 + 1.6, Z0 + .4), 0, skin="skin_dimas")
    N.bride("sari", (-13.85, -1.5 + 1.6, Z0 + .4), 0)
    for k in range(6):
        N.guest(f"g{k}", k + 3, (-20.5 + k * 2.4, -6.5 - (k % 2) * 1.3, Z0), rnd.uniform(-.5, .5))
    N.heart("hrt", (-14.5, -1.0, 11.5), 2.2, "n_pink", 6.0)
    # tengah: amplop raksasa berdiri di alas neon
    V.disc_ped("ped", 8.0, "n_pink", (0, -8, Z0), em=4.0, h=.8)
    mb = W.MB("bigenv")
    N.env_mb(mb, 0, 0, 0, 14.0, upright=True)
    env = mb.build((0, -8, Z0 + .8))
    env.rotation_euler.z = math.radians(-30)
    # kanan: usaha katering + koki pemilik + menara uang
    N.katering_shop("kt", (17, 7, Z0), 13.0, 8.0)
    ch = N.chef("chef", (14.0, -1.0, Z0), -.35)
    L.pose(ch, "cheer")
    for k, x in enumerate((19.5, 21.5)):
        L.pose(N.chef(f"st{k}", (x, 0.8, Z0), .3), "arms_fwd")
    N.money("mn", 22, (16.8, -2.6, Z0), 2, 2, 1.0)
    N.katering_van("van", (26, -5.0, Z0), 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--res", default="1080x1920")
    ap.add_argument("--samples", type=int, default=64)
    ap.add_argument("--cam", default="-48,-80,60,-2,-11,5,27,.20")
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
