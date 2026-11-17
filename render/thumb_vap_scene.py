"""Adegan 3D khusus thumbnail Liquid Vape (gaya poster sinematik: etalase toko vape malam + botol 3 lapis).

  python3 render/thumb_vap_scene.py -- --out BG.png [--res 1080x1920] [--samples 64]
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
import world_pst as P  # noqa: E402
import world_vap as V  # noqa: E402
from scenes import make_camera  # noqa: E402
from scenes_vap import PORSI  # noqa: E402


def build():
    V.stage(center=(0, 0), grid_key="vp_grid", grid_em=1.4, fade=(6.0, 30.0))
    V.rig((0, 0, 3.5), 2600.0, 1800.0, 1.3)
    # toko vape lebar di belakang, seperti etalase di poster
    V.vape_shop("shop", (0, 6.5, 0), w=13.0, d=6.0, h=8.6, sign="TOKO VAPE")
    # papan marquee neon di atas atap (seperti papan "COMING")
    V.neon_sign("mq", "Rp120.000", (0, 3.25, 9.3), 1.45, "n_gold", 7.0, pad=.45)
    # lampu sorot kecil di atas papan
    for x in (-4.2, 4.2):
        P.spot("sp%d" % (x > 0), (x, 1.2, 9.6), (x * .4, 3.4, 5.6), 260, 40, (1, .75, .9), .2)
    # botol pahlawan di depan etalase: 3 lapis (toko / brand / negara) + pita cukai
    V.disc_ped("ped", 2.1, "n_cyan", (0, 0, 0), em=5.0, h=.45)
    b = V.bottle("hero", 1.45, PORSI, label=False, pita=True, liquid_em=1.6, loc=(0, 0, .45))
    b["root"].rotation_euler = (0, 0, math.radians(-12))
    # tali pembatas ala red-carpet di depan (aksen kecil kiri-kanan)
    for x in (-2.9, 2.9):
        mb = W.MB("post%d" % (x > 0))
        mb.boxc(x, -1.6, 0, .16, .16, 1.1, "bt_cap")
        mb.boxc(x, -1.6, 1.1, .26, .26, .1, "n_gold")
        po = mb.build()
        V.glow(po, {"n_gold": 3.0})
    # lampu isi depan (tak terlihat di pantulan lantai) supaya botol "nyala"
    fl = V.area("fill", (0, -7, 3.0), (0, 0, 2.5), 350, 4, (1, .55, .85))
    fl.visible_glossy = False
    fl.visible_camera = False


def build_diorama():
    """kota diorama melayang di dunia neon: botol raksasa 3 lapis jadi monumen di plaza,
    dikelilingi toko vape (toko), pabrik liquid (brand), KAS NEGARA (negara)."""
    import scenes_vap as SV
    SV.city(1, focus=None, center_clear=48, traffic=True, people=True)
    V.vape_store_day("shop", (-26, 4, .24))
    V.factory_day("fac", (28, 16, .24))
    V.gov_day("gov", (0, 22, .24))
    V.disc_ped("pd", 9.2, "n_cyan", (0, -6, .24), em=4.0, h=.8)
    b = V.bottle("hero", 5.6, PORSI, label=False, pita=True, liquid_em=1.5, loc=(0, -6, 1.04))
    b["root"].rotation_euler = (0, 0, math.radians(-14))
    return b


CAMS = {
    # (posisi, target, lens, shift_y)
    "diorama": ((-70, -104, 84), (-12, -8, 6), 27, .20),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--res", default="1080x1920")
    ap.add_argument("--samples", type=int, default=64)
    ap.add_argument("--mode", default="poster", choices=["poster", "diorama"])
    ap.add_argument("--cam", default=None, help="x,y,z,tx,ty,tz,lens,shift")
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])
    lp.reset()
    W.PLACED.clear()
    rx, ry = map(int, a.res.split("x"))
    lp.setup_render(rx, ry, a.samples)
    W.setup_world_light()
    M.glass_setup()
    if a.mode == "poster":
        V.setup_neon_light()
        build()
        cam, tgt = make_camera(lens=24, shift_y=-.115)
        cam.location = (0, -21.0, 2.6)
        tgt.location = (0, 2.0, 5.2)
        cam.data.dof.use_dof = True
        cam.data.dof.focus_distance = 21.0
        cam.data.dof.aperture_fstop = 4.0
    else:
        build_diorama()
        pos, tg, lens, sh = CAMS["diorama"]
        if a.cam:
            v = [float(x) for x in a.cam.split(",")]
            pos, tg, lens, sh = tuple(v[:3]), tuple(v[3:6]), v[6], v[7]
        cam, tgt = make_camera(lens=lens, shift_y=sh)
        cam.location = pos
        tgt.location = tg
    sc = bpy.context.scene
    sc.frame_set(1)
    sc.render.filepath = a.out
    bpy.ops.render.render(write_still=True)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
