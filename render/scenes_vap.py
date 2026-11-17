"""20 adegan video "Bedah Bisnis: Liquid Vape" (gaya sinematik neon; timeline = VO hasil humanize_vo.py, ±81 dtk).

  python3 render/scenes_vap.py -- --scene V01 --out OUT/V01 [--res 720x1280] [--samples 4] [--frames a-b]

Isi VO: hook (1 botol Rp120 rb, siapa dapat bagian terbesar? penjual? pabrik? bukan) -> bedah 60 ml: toko
Rp30 rb, brand Rp48 rb tapi dipotong bahan baku/botol/produksi/distribusi/marketing, untung bersih kecil ->
Rp42 rb sisanya ke mana? -> pita cukai Rp636/ml x 60 ml = ±Rp38 rb + pajak rokok ±Rp4 rb = Rp42 rb ke negara,
bagian terbesar -> pasar jadi "aneh": liquid tanpa pita cukai lebih murah bukan karena efisien tapi melewati
kewajiban, ilegal -> pelajaran: hitung siapa saja yang ambil bagian dari harga jual -> CTA (TAHU / BARU TAHU,
kirim ke teman, follow part 2: modal bikin brand liquid).
Kamera sengaja berganti-ganti: sudut rendah, atas, kiri, kanan, zoom in & zoom out.
"""
import argparse
import json
import math
import os
import random
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowpoly as lp  # noqa: E402
import world as W  # noqa: E402
import world_amdk as M  # noqa: E402
import world_ctd as C  # noqa: E402
import world_hotel as H  # noqa: E402
import world_pst as P  # noqa: E402
import world_vap as V  # noqa: E402
import world_prk as R  # noqa: E402
from scenes import key, make_camera, orbit  # noqa: E402
from scenes_laundry import pop, grow_z, fly, emission_ramp, _anchor_pos  # noqa: E402

FPS = 30
TIMELINE = [("V01", 0.00), ("V02", 3.83), ("V03", 8.85), ("V04", 11.95), ("V05", 14.53), ("V06", 19.77),
            ("V07", 24.47), ("V08", 29.38), ("V09", 34.39), ("V10", 38.82), ("V11", 41.62), ("V12", 44.27),
            ("V13", 46.70), ("V14", 51.26), ("V15", 54.68), ("V16", 59.28), ("V17", 64.40), ("V18", 68.71),
            ("V19", 72.43), ("V20", 75.45)]
END_T = 81.07
PORSI = (("lq_toko", 30), ("lq_brand", 48), ("lq_negara", 42))
CAP_Z = V.BOT_H + .5 + .8        # puncak tutup botol (s=1, tanpa ujung)


def scene_range(sid):
    ids = [s for s, _ in TIMELINE]
    i = ids.index(sid)
    t0 = TIMELINE[i][1]
    t1 = TIMELINE[i + 1][1] if i + 1 < len(TIMELINE) else END_T
    f0, f1 = round(t0 * FPS), round(t1 * FPS)
    return t0, t1, f0, f1 - f0


def fr(sid, t):
    """frame lokal adegan untuk detik `t` di timeline video."""
    return max(1, int(round((t - dict(TIMELINE)[sid]) * FPS)) + 1)


# ------------------------------------------------------------------ bantu
def smooth(*obs):
    """kurva kunci kamera/objek jadi halus (ease in-out)."""
    for ob in obs:
        ad = getattr(ob, "animation_data", None)
        if not ad or not ad.action:
            continue
        for fc in _fcs(ad.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
                kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"


def _fcs(action):
    if hasattr(action, "fcurves") and len(action.fcurves):
        return list(action.fcurves)
    out = []
    for layer in getattr(action, "layers", []):
        for strip in layer.strips:
            for cb in strip.channelbags:
                out += list(cb.fcurves)
    return out


def camera(sid, keys, lens=24, shift=0.0, dof=None, fstop=3.2):
    """keys: [(detik, posisi, target)] atau [(detik, (target, az, el, dist))]. lens: angka atau [(detik, lens)]."""
    cam, tgt = make_camera(lens=lens if not isinstance(lens, list) else lens[0][1], shift_y=shift)
    for k in keys:
        if len(k) == 2:
            t, (tg, az, el, dist) = k
            p = orbit(tg, az, el, dist)
        else:
            t, p, tg = k
        f = fr(sid, t)
        cam.location = p
        cam.keyframe_insert("location", frame=f)
        tgt.location = tg
        tgt.keyframe_insert("location", frame=f)
    if isinstance(lens, list):
        for t, v in lens:
            key(cam.data, "lens", fr(sid, t), v)
        smooth(cam.data)
    if dof:
        cam.data.dof.use_dof = True
        cam.data.dof.focus_object = tgt
        cam.data.dof.aperture_fstop = fstop
    smooth(cam, tgt)
    return cam, tgt


def base(grid="vp_grid", em=2.2, center=(0, 0), rig_c=(0, 0, 1.5), rig_s=1.0, key_e=2200.0, rim=1500.0,
         fade=(8.0, 40.0)):
    st = V.stage(center=center, grid_key=grid, grid_em=em, fade=fade)
    lights = V.rig(rig_c, key_e, rim, rig_s)
    return st, lights


def appear(ob, f, s=1.0):
    pop(ob, f, s)
    return ob


def _tree(ob):
    return [ob] + list(ob.children_recursive)


def hide_until(ob, f):
    for o in _tree(ob):
        o.hide_render = True
        o.keyframe_insert("hide_render", frame=1)
        o.hide_render = False
        o.keyframe_insert("hide_render", frame=max(1, f))


def hide_after(ob, f):
    for o in _tree(ob):
        o.hide_render = False
        o.keyframe_insert("hide_render", frame=1)
        o.hide_render = True
        o.keyframe_insert("hide_render", frame=max(2, f))


def em_keys(ob, key_part, keys):
    """kunci kekuatan emisi material objek yang namanya memuat key_part."""
    for m in ob.data.materials:
        if m and key_part in m.name:
            nt = m.node_tree
            if "Principled BSDF" in nt.nodes:
                emission_ramp(m, keys)
            else:
                for n in nt.nodes:
                    if n.type == "EMISSION":
                        inp = n.inputs["Strength"]
                        for f, v in keys:
                            inp.default_value = v
                            inp.keyframe_insert("default_value", frame=f)


def unique_mat(ob):
    """salin material supaya animasi emisi tidak menular ke objek lain."""
    for i, m in enumerate(ob.data.materials):
        if m:
            ob.data.materials[i] = m.copy()
    return ob


def spin(ob, f0, f1, deg):
    key(ob, "rotation_euler", f0, (ob.rotation_euler.x, ob.rotation_euler.y, ob.rotation_euler.z))
    key(ob, "rotation_euler", f1, (ob.rotation_euler.x, ob.rotation_euler.y,
                                   ob.rotation_euler.z + math.radians(deg)))


def bob(ob, f0, f1, amp=.2, period=50):
    z0 = ob.location.z
    f = f0
    k = 0
    while f <= f1:
        key(ob, "location", f, (ob.location.x, ob.location.y, z0 + (amp if k % 2 else 0)))
        f += period // 2
        k += 1
    smooth(ob)


def spot_keys(li, keys):
    for f, v in keys:
        li.data.energy = v
        li.data.keyframe_insert("energy", frame=f)


def bg_bottles(n=7, r=(16, 26), seed=3, z=0.0, s=.8, behind=True):
    """botol-botol jauh di belakang (kedalaman & bokeh)."""
    rnd = random.Random(seed)
    mb = W.MB("bgb")
    cols = ["lq_pink", "lq_toko", "lq_brand", "lq_negara", "lq_cheap"]
    for k in range(n):
        a = math.radians(rnd.uniform(35, 145)) if behind else rnd.uniform(0, 2 * math.pi)
        d = rnd.uniform(*r)
        x, y = math.cos(a) * d, math.sin(a) * d
        mb.cyl(x, y, 0, .3, 1.4 * s, "bd_dark2", n=20)
        V.bottle_mb(mb, x, y, .3 + z, s * rnd.uniform(.9, 1.2), rnd.choice(cols))
    ob = mb.build()
    V.glow(ob, {c: 2.0 for c in cols})
    return ob


def chip(name, key_, s, loc, em=3.0):
    return V.block(name, key_, s, loc, em, 6.0)


# ------------------------------------------------------------------ adegan
def v03(n, A):
    """Bedah 1 botol 60 ml: cincin pemindai turun, isi terbelah jadi 3 porsi. Kamera crane atas -> depan."""
    sid = "V03"
    base(grid="vp_grid2", em=1.6, rig_c=(0, 0, 3))
    V.disc_ped("pd", 3.0, "n_cyan", (0, 0, 0))
    s = 2.0
    b = V.bottle("b", s, PORSI, label=False, loc=(0, 0, .5))
    # isi polos pink menutupi lapisan, menyusut dari atas saat cincin lewat
    cov = W.MB("cov")
    h = V.FILL[1] - V.FILL[0]
    M.lathe(cov, 0, 0, 0, [(0, 0), (.905, 0), (.905, h), (0, h)], "lq_pink", n=28)
    co = cov.build((0, 0, .5 + V.FILL[0] * s))
    co.scale = (s, s, s)
    V.set_mat(co, V.emis("lq_pink", 1.3))
    for ob in b["layers"]:
        ob.scale = (.97, .97, 1)
    f0, f1 = fr(sid, 9.4), fr(sid, 11.0)
    key(co, "scale", 1, (s, s, s))
    key(co, "scale", f0, (s, s, s))
    key(co, "scale", f1, (s, s, .001))
    ring = V.ring_obj("scan", (0, 0, 0), 2.35, .1, "n_cyan", 8.0)
    z_top, z_bot = .5 + V.FILL[1] * s, .5 + V.FILL[0] * s
    hide_until(ring, f0 - 6)
    key(ring, "location", 1, (0, 0, z_top + .4))
    key(ring, "location", f0, (0, 0, z_top))
    key(ring, "location", f1, (0, 0, z_bot))
    key(ring, "location", f1 + 8, (0, 0, z_bot - .4))
    hide_after(ring, f1 + 9)
    spin(b["root"], 1, n, 30)
    camera(sid, [(8.85, ((0, 0, 5.2), -60, 38, 9.0)), (10.4, ((0, 0, 3.6), -85, 16, 11.5)),
                 (11.95, ((0, 0, 3.2), -105, 8, 12.5))], lens=28, dof=True, fstop=3.5)
    zs = [z_bot]
    tot = sum(p for _, p in PORSI)
    for _, p in PORSI:
        zs.append(zs[-1] + h * s * p / tot)
    for i, nm in enumerate(("TOKO", "BRAND", "TOP")):
        A[nm] = ((0, -1.9, (zs[i] + zs[i + 1]) / 2))


def v06(n, A):
    """Untung bersih kecil: pilar sisa mungil + bayangan pilar awal; kamera atas zoom in + kaca pembesar."""
    sid = "V06"
    base(grid="vp_grid", em=1.6, rig_c=(0, 0, 1), rig_s=1.0, key_e=1500)
    ghost = V.pillar("gh", 7.6, 2.8, 2.8, "n_purple", .12, 1.2, (0, 0, 0))
    small = V.pillar("sm", 7.6 * .18, 2.8, 2.8, "n_purple", 2.2, 7.0, (0, 0, 0))
    gem = V.block("gem", "n_green", .9, (0, 0, 7.6 * .18 + .05), 2.6, 7.0)
    appear(gem, fr(sid, 20.3), 1.0)
    for i, kind in enumerate(("bahan", "botol", "produksi", "distribusi", "marketing")):
        a = math.radians(90 + 72 * i)
        V.icon("ic%d" % i, kind, .8, (math.cos(a) * 7.5, math.sin(a) * 7.5, 0), em=1.2)
    mg = V.magnifier("mg", (0, -1.2, 4.5), 1.7)
    mg.rotation_euler = (math.radians(70), 0, 0)
    fly(mg, fr(sid, 20.4), fr(sid, 21.6), (6, -6, 9), (0, -1.2, 4.2), arc=1.0)
    hide_until(mg, fr(sid, 20.4))
    camera(sid, [(19.77, ((0, 0, 0), -90, 82, 34)), (22.0, ((0, 0, 1.2), -100, 72, 17)),
                 (24.47, ((0, 0, 1.4), -115, 58, 10.5))], lens=24)
    A["SMALL"] = (small, (0, 0, 7.6 * .18 + 1.0))
    A["GHOST"] = (ghost, (0, 0, 7.6))


def v07(n, A):
    """Rp42 rb sisanya ke mana? Panggung gelap, lapisan emas berdenyut, tanda tanya; orbit lambat."""
    sid = "V07"
    base(grid="vp_grid", em=.9, rig_c=(0, 0, 3), key_e=600, rim=500)
    V.disc_ped("pd", 2.8, "n_gold", (0, 0, 0))
    b = V.bottle("b", 1.7, PORSI, label=False, loc=(0, 0, .5))
    top = unique_mat(b["layers"][2])
    for i, lq in enumerate(b["layers"][:2]):
        unique_mat(lq)
        em_keys(lq, PORSI[i][0], [(1, .25)])
    ks = [(1, 1.3)]
    f = 8
    while f < n:
        ks += [(f, 4.5), (f + 10, 1.4)]
        f += 22
    em_keys(top, "lq_negara", ks)
    sp = P.spot("sp", (0, -2, 16), (0, 0, 2), 6000, 26, (1, .85, .5), .3)
    P.light_beam("beam", (0, 0, 17), 16, 2.6, "n_gold", .3)
    q = V.qmark("q", (0, -.5, 7.6), 1.6, "n_gold", 7)
    appear(q, fr(sid, 25.0), 1.0)
    bob(q, fr(sid, 25.3), n, .35, 44)
    camera(sid, [(24.47, ((0, 0, 3.2), -150, 24, 15)), (27.0, ((0, 0, 3.6), -110, 16, 12)),
                 (29.38, ((0, 0, 4.0), -72, 10, 10))], lens=28, dof=True, fstop=4.0)
    A["TOP"] = (b["root"], (0, -1.7, .5 + 1.7 * (V.FILL[1] - .35)))
    A["Q"] = (q, (0, 0, 3.0))


def v08(n, A):
    """Pita cukai menempel di tutup; tetes 1 ml = Rp636. Kamera makro dari kanan atas ke depan."""
    sid = "V08"
    base(grid="vp_grid2", em=1.4, rig_c=(0, 0, 5), key_e=1800)
    V.disc_ped("pd", 3.0, "n_pink", (0, 0, 0))
    s = 2.0
    b = V.bottle("b", s, (("lq_pink", 1),), label=True, loc=(0, 0, .5))
    pc = V.pita_cukai("pc", b["root"])
    fp = fr(sid, 30.45)
    key(pc, "location", 1, (0, 0, 3.0))
    key(pc, "location", fp, (0, 0, 3.0))
    key(pc, "location", fp + 6, (0, 0, -.05))
    key(pc, "location", fp + 9, (0, 0, 0))
    hide_until(pc, fp)
    cz = .5 + s * CAP_Z
    d = V.drop("drop", (4.2, -1.2, 2.2), 1.6, "n_gold")
    appear(d, fr(sid, 31.75), 1.6)
    bob(d, fr(sid, 32.1), n, .25, 36)
    V.disc_ped("pd2", 1.2, "n_gold", (4.2, -1.2, 0), em=3.0, h=.3)
    camera(sid, [(29.38, ((0, 0, cz - .6), -25, 34, 7.5)), (31.2, ((0, 0, cz - 1.2), -65, 20, 9.5)),
                 (34.39, ((1.8, -.5, cz - 2.6), -100, 12, 14))], lens=30, dof=True, fstop=4.5)
    A["PITA"] = (b["root"], (0, -1.3 * s, CAP_Z * s - .1))
    A["DROP"] = (d, (0, 0, 2.4))


def v09(n, A):
    """60 kubus emas (60 ml) menyala satu per satu = ±Rp38 rb. Kamera atas, naik & berputar (zoom out)."""
    sid = "V09"
    base(grid="vp_grid", em=1.6, rig_c=(0, 0, 1), rig_s=1.4, key_e=1200)
    V.base_plate("pl", 13.6, 8.4, "n_gold", (0, 0, 0))
    f0, f1 = fr(sid, 35.5), fr(sid, 37.1)
    k = 0
    for j in range(6):
        for i in range(10):
            x, y = -5.85 + i * 1.3, -3.25 + j * 1.3
            c = V.block("c%02d" % k, "n_gold", 1.0, (x, y, .14), 2.4, 6.0)
            f = f0 + int((f1 - f0) * k / 59)
            pop(c, f, 1.0)
            k += 1
    camera(sid, [(34.39, ((0, 0, 0), -90, 88, 9.5)), (36.6, ((0, 0, 0), -110, 74, 17)),
                 (38.82, ((0, 0, 0), -135, 55, 21))], lens=22)
    A["GRID"] = ((0, -3.6, 1.2))


def v10(n, A):
    """Cukai ±Rp38 rb (balok emas) + pajak rokok ±Rp4 rb (balok oranye) mendarat di atasnya. Kamera kanan->kiri."""
    sid = "V10"
    base(grid="vp_grid", em=1.8, rig_c=(0, 0, 2.5), key_e=1500)
    V.disc_ped("pd", 2.6, "n_gold", (0, 0, 0))
    big = V.pillar("big", 3.8, 2.6, 2.6, "n_gold", 1.6, 6.0, (0, 0, .5))
    small = V.pillar("sm", .45, 2.6, 2.6, "n_orange", 2.0, 7.0, (0, 0, 0))
    f0, f1 = fr(sid, 39.3), fr(sid, 40.4)
    fly(small, f0, f1, (9, -2, 6), (0, 0, 4.32), arc=2.5)
    hide_until(small, f0)
    pop(small, f0, 1.0)
    camera(sid, [(38.82, ((0, 0, 2.6), -35, 12, 13)), (40.4, ((0, 0, 2.8), -78, 10, 12.5)),
                 (41.62, ((0, 0, 2.6), -122, 14, 14))], lens=26)
    A["BIG"] = (big, (0, -1.3, 2.0))
    A["SMALL"] = (small, (0, 0, .5))


def v12(n, A):
    """Tiga pilar: toko, brand (sebagian besar biaya), negara bermahkota. Kamera rendah kiri -> kanan."""
    sid = "V12"
    base(grid="vp_grid", em=2.0, rig_c=(0, 0, 3), rig_s=1.5, key_e=1300)
    k = .13
    xs = (-6.0, 0.0, 6.0)
    t0 = V.pillar("toko", 30 * k, 3, 3, "lq_toko", 1.5, 6.0, (xs[0], 0, 0))
    b0 = V.pillar("brand_c", 40 * k, 3, 3, "n_purple", .35, 2.0, (xs[1], 0, 0))
    b1 = V.pillar("brand_u", 8 * k, 3, 3, "n_purple", 2.2, 7.0, (xs[1], 0, 40 * k))
    g0 = V.pillar("negara", 42 * k, 3, 3, "n_gold", 1.8, 7.0, (xs[2], 0, 0))
    for i, ob in enumerate((t0, b0, g0)):
        grow_z(ob, fr(sid, 44.3) + i * 3, fr(sid, 44.9) + i * 3, 1.0)
    pop(b1, fr(sid, 44.95) + 3, 1.0)
    cr = V.crown("cr", (xs[2], 0, 42 * k + .6), 1.1)
    appear(cr, fr(sid, 45.3), 1.1)
    spin(cr, fr(sid, 45.3), n, 90)
    camera(sid, [(44.27, ((0, 0, 3.0), -140, 6, 25)), (45.5, ((0, 0, 3.2), -108, 9, 24)),
                 (46.70, ((1.0, 0, 3.2), -68, 12, 24))], lens=22)
    A["TOKO"] = (t0, (0, 0, 30 * k))
    A["BRAND"] = (b1, (0, 0, 8 * k))
    A["NEGARA"] = (cr, (0, 0, 1.6))


def v14(n, A):
    """Resmi (berpita cukai) vs tanpa pita: yang tanpa pita jauh lebih murah. Kamera dorong ke tengah."""
    sid = "V14"
    base(grid="vp_grid", em=1.8, rig_c=(0, 0, 2.5), rig_s=1.4, key_e=1600)
    V.disc_ped("pdL", 2.4, "n_cyan", (-4.2, 0, 0))
    V.disc_ped("pdR", 2.4, "n_red", (4.2, 0, 0))
    bL = V.bottle("bL", 1.3, (("lq_pink", 1),), pita=True, loc=(-4.2, 0, .5))
    bR = V.bottle("bR", 1.3, (("lq_cheap", 1),), label=False, loc=(4.2, 0, .5))
    ar = W.MB("arrow")
    ar.prism_y([(-.35, 0), (.35, 0), (.35, -1.6), (.85, -1.6), (0, -2.6), (-.85, -1.6), (-.35, -1.6)], -.15, .15,
               "n_green")
    ao = ar.build((7.6, 0, 6.2))
    V.glow(ao, {"n_green": 6})
    fa = fr(sid, 52.9)
    appear(ao, fa, 1.0)
    key(ao, "location", fa + 7, (7.6, 0, 6.2))
    key(ao, "location", fa + 16, (7.6, 0, 4.6))
    camera(sid, [(51.26, ((0, 0, 2.6), -90, 10, 19)), (53.0, ((.8, 0, 2.8), -86, 9, 15.5)),
                 (54.68, ((1.2, 0, 2.6), -82, 8, 14))], lens=26, dof=True, fstop=5.0)
    A["L"] = (bL["root"], (0, 0, 1.3 * CAP_Z + .6))
    A["R"] = (bR["root"], (0, 0, 1.3 * CAP_Z + .6))


def v16(n, A):
    """Pelajaran: pai harga jual Rp120 rb terbelah ke 3 pihak. Kamera atas berputar lalu turun."""
    sid = "V16"
    base(grid="vp_grid2", em=1.6, rig_c=(0, 0, 1), rig_s=1.5, key_e=1300)
    V.disc_ped("pd", 6.0, "n_pink", (0, 0, 0), h=.4)
    sl = V.pie("pie", PORSI, r=4.6, h=1.1, loc=(0, 0, .45))
    f0, f1 = fr(sid, 61.3), fr(sid, 62.1)
    for i, ob in enumerate(sl):
        mx, my = ob["mid"]
        key(ob, "location", f0 + i * 3, (0, 0, .45))
        key(ob, "location", f1 + i * 3, (mx * 2.4, my * 2.4, .45 + .6))
        A[["TOKO", "BRAND", "NEGARA"][i]] = (ob, (mx * 2.6, my * 2.6, 1.3))
    camera(sid, [(59.28, ((0, 0, 0), -90, 80, 30)), (61.5, ((0, 0, .5), -130, 62, 31)),
                 (64.40, ((0, 0, .8), -165, 42, 30))], lens=24)


def v18(n, A):
    """Ketik TAHU atau BARU TAHU: dua papan neon, kamera geser kiri -> kanan lalu mundur."""
    sid = "V18"
    base(grid="vp_grid", em=2.0, rig_c=(0, 0, 3), rig_s=2.0, key_e=800, rim=900)
    t1, f1_ = V.neon_sign("s1", "TAHU", (-6, 2, 3.2), 1.6, "n_cyan", 9)
    t2, f2_ = V.neon_sign("s2", "BARU TAHU", (6.5, 2, 3.2), 1.6, "n_pink", 9)
    for ob, t in ((t1, 69.35), (f1_, 69.35), (t2, 70.2), (f2_, 70.2)):
        appear(ob, fr(sid, t), 1.0)
    for x in (-6, 6.5):
        V.base_plate("bp%d" % x, 8 if x < 0 else 12, 3, "n_purple", (x, 2.4, 0))
    camera(sid, [(68.71, ((-6, 2, 3.6), -100, 8, 13)), (69.9, ((-1, 2, 3.6), -92, 8, 14)),
                 (70.9, ((5.5, 2, 3.6), -80, 8, 14)), (72.43, ((.5, 2, 3.4), -90, 14, 26))], lens=24)
    A["S1"] = (t1, (0, 0, 2.4))
    A["S2"] = (t2, (0, 0, 2.4))



# ================================================================== adegan KOTA SIANG (template seri)
CITY = {"V01", "V02", "V04", "V05", "V11", "V13", "V15", "V17", "V19", "V20"}


def city(n, **kw):
    V.setup_day_light()
    return V.town(n_frames=n, **kw)


def v01(n, A):
    """HOOK (kota): kamera menukik dari udara ke botol raksasa di plaza depan toko vape."""
    sid = "V01"
    city(n, focus="vape")
    V.disc_ped("pd", 2.6, "n_pink", (0, -7, .24), em=3.0)
    b = V.bottle("b", 1.5, (("lq_pink", 1),), loc=(0, -7, .74))
    spin(b["root"], 1, n, 50)
    camera(sid, [(0.0, ((0, -2, 2), -104, 50, 85)), (2.2, ((0, -5, 3), -92, 22, 26)),
                 (3.83, ((0, -6, 3.4), -76, 10, 15))], lens=24)
    A["BOTOL"] = (b["root"], (0, 0, .74 + 1.5 * CAP_Z))


def v02(n, A):
    """Siapa dapat bagian terbesar? (kota) Toko vape kiri, pabrik kanan, botol di tengah. Kamera udara."""
    sid = "V02"
    info = city(n, focus=None, center_clear=48)
    shop = V.vape_store_day("shop", (-24, 4, .24))
    fac = V.factory_day("fac", (26, 18, .24))
    V.disc_ped("pd", 2.8, "n_pink", (0, -8, .24), em=3.0)
    b = V.bottle("b", 1.6, (("lq_pink", 1),), loc=(0, -8, .74))
    spin(b["root"], 1, n, 60)
    q = V.qmark("q", (0, -8.5, 7.6), 1.4, "n_gold")
    appear(q, fr(sid, 4.3), 1.0)
    bob(q, fr(sid, 4.6), n, .4, 40)
    for nm, loc, t, k in (("pinL", (-24, 2, 12), 6.35, "n_cyan"), ("pinR", (22, 2, 16), 7.22, "n_purple")):
        rg = V.ring_obj(nm, (loc[0], loc[1] - 4, .3), 9.0, .35, k, 4.0)
        appear(rg, fr(sid, t), 1.0)
    xL = V.xmark("xL", (-24, -1.5, 12), 3.0)
    xR = V.xmark("xR", (22, 1, 16), 3.0)
    appear(xL, fr(sid, 8.03), 3.0)
    appear(xR, fr(sid, 8.03) + 3, 3.0)
    camera(sid, [(3.83, ((0, -6, 3), -100, 30, 34)), (5.6, ((-6, -3, 3), -104, 34, 44)),
                 (6.5, ((-22, 2, 4), -100, 30, 40)), (7.0, ((-20, 2, 4), -96, 30, 40)),
                 (7.4, ((20, 6, 5), -88, 32, 52)), (7.9, ((20, 6, 5), -84, 32, 54)),
                 (8.85, ((0, 2, 4), -90, 42, 84))], lens=24)
    A["SHOP"] = (shop["sign"], (0, 0, 1.4))
    A["FAC"] = (fac["sign"], (6, 0, 1.6))
    A["BOTOL"] = (b["root"], (0, 0, .74 + 1.6 * CAP_Z))


def v04(n, A):
    """Toko ambil margin Rp30 rb (kota): kubus cyan terbang dari botol ke kasir toko. Kamera dari kiri."""
    sid = "V04"
    city(n, focus="vape")
    V.disc_ped("pd", 2.2, "n_pink", (9, -8, .24), em=3.0)
    b = V.bottle("b", 1.3, PORSI, label=False, loc=(9, -8, .74))
    lq = unique_mat(b["layers"][0])
    fo = fr(sid, 13.0)
    em_keys(lq, "lq_toko", [(1, 1.3), (fo, 1.3), (fo + 8, .15)])
    blk = chip("blk", "lq_toko", 1.6, (9, -8, 1.0))
    fly(blk, fo, fr(sid, 13.6), (9, -9.5, 1.2), (0, 3.6, 1.2), arc=6.0)
    pop(blk, fo, 1.0)
    hide_until(blk, fo)
    rg = V.ring_obj("rg", (0, 2.6, .3), 2.6, .16, "n_cyan", 5)
    appear(rg, fr(sid, 13.6), 1.0)
    camera(sid, [(11.95, ((0, -2, 3), -150, 12, 34)), (13.4, ((2, -3, 3), -118, 15, 29)),
                 (14.53, ((1, -3, 3), -96, 18, 27))], lens=24)
    A["SHOP"] = ((0, 3.8, 5.0))
    A["BLK"] = (blk, (0, 0, 1.8))


def v05(n, A):
    """Brand Rp48 rb dipotong 5 biaya (kota): pilar ungu di depan pabrik menyusut tiap ikon muncul."""
    sid = "V05"
    city(n, focus="factory")
    H0 = 7.6
    pl = V.pillar("pl", H0, 2.8, 2.8, "n_purple", 1.4, 6.0, (0, -7, .24))
    grow_z(pl, fr(sid, 14.9), fr(sid, 15.7), 1.0)
    words = [("bahan", 17.23), ("botol", 17.93), ("produksi", 18.19), ("distribusi", 18.64), ("marketing", 19.19)]
    sc_steps = [.8, .63, .47, .32, .18]
    pos = [(-4.6, -9.5), (-2.6, -12.4), (0, -13.4), (2.6, -12.4), (4.6, -9.5)]
    for i, ((kind, t), (x, y)) in enumerate(zip(words, pos)):
        f = fr(sid, t)
        ic = V.icon("ic%d" % i, kind, 1.25, (x, y, .24))
        appear(ic, f, 1.25)
        key(pl, "scale", f, (1, 1, 1 if i == 0 else sc_steps[i - 1]))
        key(pl, "scale", f + 5, (1, 1, sc_steps[i]))
        ch = chip("ch%d" % i, "n_purple", .7, (0, 0, 0))
        fly(ch, f - 3, f + 4, (0, -7, H0 * (sc_steps[i - 1] if i else 1) - .5), (x, y, 3.4), arc=1.5)
        hide_until(ch, f - 3)
        hide_after(ch, f + 5)
        A["IC%d" % i] = (ic, (0, 0, 3.2))
    camera(sid, [(14.53, ((0, -6, 5.6), -92, -2, 15)), (16.6, ((0, -8, 3.4), -82, 10, 21)),
                 (19.77, ((0, -6, 3.0), -100, 26, 32))], lens=[(14.53, 20), (16.6, 20), (19.77, 22)])
    A["PL"] = (pl, (0, 0, H0))


def v11(n, A):
    """Total Rp42 rb masuk ke negara (kota): pilar emas terbang masuk gedung KAS NEGARA. Kamera mundur & naik."""
    sid = "V11"
    info = city(n, focus="gov")
    pl = V.pillar("pl", 4.25, 2.6, 2.6, "n_gold", 1.7, 6.0, (0, -9, .24))
    f0, f1 = fr(sid, 42.6), fr(sid, 43.6)
    fly(pl, f0, f1, (0, -9, .24), (0, 2.5, 1.0), arc=6.0)
    key(pl, "scale", f0, (1, 1, 1))
    key(pl, "scale", f1, (.25, .25, .25))
    hide_after(pl, f1 + 1)
    rg = V.ring_obj("rg", (0, 1.0, .35), 4.0, .2, "n_gold", 6)
    appear(rg, f1, 1.0)
    camera(sid, [(41.62, ((0, -8, 2.8), -96, 6, 13)), (42.9, ((0, -3, 3.4), -94, 14, 24)),
                 (44.27, ((0, 2, 4.0), -80, 24, 46))], lens=24)
    A["PL"] = (pl, (0, 0, 4.4))
    A["GOV"] = (info["focus"]["sign"], (0, 0, 1.2))


def v13(n, A):
    """Pasar liquid jadi 'aneh' (kota): deretan toko vape + lapak gelap tanpa pita; kamera dolly sepanjang jalan."""
    sid = "V13"
    city(n, focus="market", center_clear=52)
    st = V.shady_stall("stall", (10, -7, .24))
    em_keys(unique_mat(st), "lq_cheap", [(1, 2.0), (fr(sid, 49.6), 2.0), (fr(sid, 49.8), 9.0), (fr(sid, 50.0), 1.0),
                                          (fr(sid, 50.2), 9.0), (fr(sid, 50.5), 3.0)])
    camera(sid, [(46.70, (-48, -16, 5), (-32, 2, 3)), (49.0, (-14, -17, 5.5), (2, 0, 2.6)),
                 (51.26, (16, -18, 6.5), (30, 2, 2.4))], lens=[(46.70, 20), (51.26, 24)])
    A["ODD"] = (st, (0, 0, 3.6))


def v15(n, A):
    """Bukan efisien, kewajiban dilewati -> ILEGAL (kota): gerbang CUKAI melintang jalan, mobil boks resmi lewat
    gerbang; van gelap memutar lewat plaza (jalur merah), sirine & cap ILEGAL."""
    sid = "V15"
    city(n, focus=None, people=False)
    emp = bpy.data.objects.new("gate_root", None)
    lp._link(emp)
    emp.location = (0, -27, 0)
    emp.rotation_euler.z = math.radians(90)
    g = V.gate("gt", (0, 0, 0), 15.0, "CUKAI")
    for ob in (g["body"], g["arm"], g["trim"], g["sign"]):
        ob.parent = emp
    ok = V.box_van("ok", (-40, -23.2, 0))
    for t, x in ((54.68, -40), (56.0, -6), (56.8, -6), (58.0, 16), (59.28, 30)):
        key(ok, "location", fr(sid, t), (x, -23.2, 0))
    smooth(ok)
    path = W.MB("path")
    pts = [(-30, -30.8), (-12, -30.8), (-8, -12), (8, -12), (12, -23.2), (30, -23.2)]
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        L_ = math.hypot(x1 - x0, y1 - y0)
        for k in range(int(L_ / 1.6)):
            u0, u1 = k * 1.6 / L_, (k * 1.6 + 1.0) / L_
            ax, ay = x0 + (x1 - x0) * u0, y0 + (y1 - y0) * u0
            bx, by = x0 + (x1 - x0) * u1, y0 + (y1 - y0) * u1
            nx, ny = -(by - ay), (bx - ax)
            nl = math.hypot(nx, ny) or 1
            nx, ny = nx / nl * .2, ny / nl * .2
            path.poly([(ax - nx, ay - ny, .35), (bx - nx, by - ny, .35), (bx + nx, by + ny, .35),
                       (ax + nx, ay + ny, .35)], [(0, 1, 2, 3)], "n_red")
    po = path.build()
    V.glow(po, {"n_red": 4})
    hide_until(po, fr(sid, 56.4))
    bad = V.box_van("bad", (-30, -30.8, 0))
    bad.data.materials[0] = lp.mat("stall")
    crates = W.MB("crates")
    for k in range(4):
        V.bottle_mb(crates, -1.8 + k * .9, 0, 3.0, .3, "lq_cheap")
    co = crates.build(parent=bad)
    V.glow(co, {"lq_cheap": 2.5})
    t_pts = [56.4, 56.9, 57.4, 57.8, 58.1, 58.6]
    for (x, y), t in zip(pts, t_pts):
        key(bad, "location", fr(sid, t), (x, y, .24 if -16 < y < 3 else 0))
    ic = V.icon("gear", "produksi", 1.6, (-14, -6, .24))
    appear(ic, fr(sid, 55.2), 1.6)
    xg = V.xmark("xg", (-14, -6.6, 2.2), 1.3)
    appear(xg, fr(sid, 55.7), 1.3)
    sr, li = V.siren("sr", (0, -19.6, 4.6), 1.3)
    flash_f = fr(sid, 58.4)
    V.flash_siren(sr, li, flash_f, n, 8)
    stp = C.stamp("ilegal", "ILEGAL", 2.4, "x_red")
    for ob in [stp] + list(stp.children):
        V.glow(ob, {"x_red": 3.0})
    stp.location = (8, -14, 9)
    stp.rotation_euler = (math.radians(40), 0, math.radians(-6))
    appear(stp, flash_f, 1.0)
    camera(sid, [(54.68, ((-4, -18, 0), -70, 46, 60)), (57.0, ((0, -20, 0), -88, 50, 54)),
                 (59.28, ((4, -18, 2), -104, 42, 46))], lens=24)
    A["GEAR"] = (ic, (0, 0, 3.4))
    A["CHEAP"] = (bad, (0, 0, 4.0))
    A["GATE"] = ((0, -20, 6))


def v17(n, A):
    """'Kamu tahu nggak Rp42 rb itu buat negara?' (kota): balok emas di plaza depan gedung negara; orbit."""
    sid = "V17"
    city(n, focus="gov")
    V.disc_ped("pd", 2.8, "n_gold", (0, -8, .24), em=3.0)
    pl = V.pillar("pl", 3.0, 2.4, 2.4, "n_gold", 1.8, 7.0, (0, -8, .74))
    q = V.qmark("q", (0, -8.3, 5.8), 1.0, "n_pink")
    appear(q, fr(sid, 67.3), 1.0)
    bob(q, fr(sid, 67.6), n, .25, 30)
    camera(sid, [(64.40, ((0, -5, 3.2), -150, 12, 22)), (66.5, ((0, -4, 3.4), -96, 16, 21)),
                 (68.71, ((0, -3, 3.6), -40, 20, 23))], lens=24)
    A["PL"] = (pl, (0, 0, 3.4))


def v19(n, A):
    """Kirim ke teman (kota): dua orang di trotoar, pesawat kertas terbang dari ponsel ke ponsel teman."""
    sid = "V19"
    info = city(n, focus="vape", people=False)
    a = R.shopper("pa", 1, (-7, -10, .24), 0.4, "phone")
    b_ = R.shopper("pb", 4, (7, -9, .24), -0.4, "phone")
    p1 = V.phone("p1", (-8.6, -10.4, .24), .65)
    p2 = V.phone("p2", (8.6, -9.4, .24), .65, bubbles=(("ph_bub", .6), ("x_red", .7), ("ph_bub", .5)))
    p1.rotation_euler.z = math.radians(15)
    p2.rotation_euler.z = math.radians(-15)
    pl = V.paper_plane("pl", (-8.6, -11, 4.0), .9)
    f0, f1 = fr(sid, 72.6), fr(sid, 73.7)
    pl.rotation_euler = (0, 0, math.radians(-75))
    fly(pl, f0, f1, (-8.6, -11, 4.0), (8.2, -10, 3.6), arc=4.0)
    smooth(pl)
    hide_until(pl, f0)
    hide_after(pl, f1 + 2)
    t, fo = V.neon_sign("mahal", "MAHAL!", (7.5, -9.2, 4.6), .9, "n_red", 6)
    appear(t, fr(sid, 74.2), 1.0)
    appear(fo, fr(sid, 74.2), 1.0)
    camera(sid, [(72.43, ((-5, -10, 2.4), -122, 10, 15)), (73.6, ((0, -9, 2.8), -98, 12, 20)),
                 (75.45, ((5, -9, 3.0), -74, 12, 15))], lens=24)
    A["P1"] = (a["body"] if isinstance(a, dict) and "body" in a else p1, (0, 0, 2.4))
    A["P2"] = (b_["body"] if isinstance(b_, dict) and "body" in b_ else p2, (0, 0, 2.4))


def v20(n, A):
    """Part 2 (kota): benda tertutup kain di plaza + baliho PART 2; kamera mundur & naik ke udara."""
    sid = "V20"
    city(n, focus=None, center_clear=22)
    V.disc_ped("pd", 3.4, "n_pink", (0, -7, .24), em=3.0)
    cl = W.MB("cloth")
    import world_laundry as L
    L.rbox(cl, -2.2, -1.6, .5, 2.2, 1.6, 3.6, "vs_awn", c=.5)
    co = cl.build((0, -7, .24))
    V.qmark("q", (0, -8.7, 1.4), .8, "n_gold", 4)
    bb, bt = V.billboard_day("p2", "PART 2", (0, 8, .24), 16, 6, "vs_pink", 1.0)
    for i, (x, kind) in enumerate(((-7, "bahan"), (-4.5, "botol"), (4.5, "produksi"), (7, "marketing"))):
        ic = V.icon("ic%d" % i, kind, .9, (x, -8, .24), em=2.0)
        appear(ic, fr(sid, 77.6) + i * 3, .9)
    camera(sid, [(75.45, ((0, -7, 2.6), -92, 6, 12)), (78.0, ((0, -3, 5.0), -88, 16, 30)),
                 (81.07, ((0, 0, 6.0), -96, 30, 58))], lens=24)
    A["BOX"] = (co, (0, 0, 4.0))
    A["P2"] = (bt, (0, 0, 4.0))


SCENES = {f"V{i:02d}": globals()[f"v{i:02d}"] for i in range(1, 21)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--res", default="720x1280")
    ap.add_argument("--samples", type=int, default=4)
    ap.add_argument("--frames", default=None)
    args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])

    t0, t1, gf0, n = scene_range(args.scene)
    lp.reset()
    W.PLACED.clear()
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
    rx, ry = map(int, args.res.split("x"))
    lp.setup_render(rx, ry, args.samples)
    bpy.context.scene.cycles.denoising_prefilter = "FAST"
    bpy.context.scene.cycles.denoising_quality = "FAST"
    W.setup_world_light()
    M.glass_setup()
    if args.scene not in CITY:
        V.setup_neon_light()
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, n
    A = {}
    SCENES[args.scene](n, A)
    cam = sc.camera

    os.makedirs(os.path.join(args.out, "frames"), exist_ok=True)
    data = {"scene": args.scene, "t0": t0, "t1": t1, "global_f0": gf0, "n": n, "fps": FPS, "res": [rx, ry],
            "frames": {}}
    for f in range(1, n + 1):
        sc.frame_set(f)
        pos = {}
        for name, p in A.items():
            v = world_to_camera_view(sc, cam, _anchor_pos(p))
            if v.z > 0:
                pos[name] = [round(v.x * rx, 1), round((1 - v.y) * ry, 1)]
        data["frames"][f] = pos
    with open(os.path.join(args.out, "anchors.json"), "w") as fh:
        json.dump(data, fh)

    lo, hi = (1, n) if not args.frames else map(int, args.frames.split("-"))
    for f in range(lo, hi + 1):
        path = os.path.join(args.out, "frames", f"{f:04d}.png")
        if os.path.exists(path) and not args.frames:
            continue
        sc.frame_set(f)
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
    print("DONE", args.scene, n)


if __name__ == "__main__":
    main()
