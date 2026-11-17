"""Adegan video "Bedah Bisnis: Nikahan Rp100 Juta" (alur 3K: Korban -> Kejutan -> Kail, berulang).
Visual: kota diorama siang melayang di dunia neon (adegan cerita) + panggung neon (adegan angka).

Kehalusan gerak (perbaikan dari video sebelumnya):
 - kamera: jalur spline C1 (Hermite) di ruang orbit (target, azimut, elevasi, log jarak), DIKUNCI TIAP FRAME
   -> tidak ada berhenti-jalan di titik kunci; kecepatan tidak pernah nol di tengah adegan;
 - animasi objek: nilai di-ease per frame (tanpa pop 7-frame / kurva linear patah);
 - tiap adegan dirender TAIL frame lebih panjang (kamera & animasi terus jalan) untuk crossfade di compositor.

  python3 render/scenes_nkh.py -- --scene N01 --out DIR [--res 720x1280] [--samples 4] [--frames a-b]
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
import world_laundry as L  # noqa: E402
import world_prk as R  # noqa: E402
import world_pst as P  # noqa: E402
import world_vap as V  # noqa: E402
import world_nkh as N  # noqa: E402
import scenes_vap as SV  # noqa: E402
from scenes import make_camera, orbit  # noqa: E402
from scenes_laundry import _anchor_pos  # noqa: E402

FPS = 30
TAIL = 8
TIMELINE = [("N01", 0.00), ("N02", 3.10), ("N03", 7.40), ("N04", 11.80), ("N05", 19.20), ("N06", 20.30),
            ("N07", 22.95), ("N08", 27.60), ("N09", 31.30), ("N10", 35.10), ("N11", 36.45), ("N12", 42.75),
            ("N13", 47.90), ("N14", 51.95), ("N15", 55.40), ("N16", 60.60), ("N17", 62.50), ("N18", 70.35)]
END_T = 74.6
CITY = {"N01", "N02", "N06", "N10", "N13", "N14", "N16", "N17", "N18"}
PEL_Y = -7.2                      # pelaminan (asal = depan panggung)
COUPLE_Y = PEL_Y + 1.55
Z0 = .24                          # tinggi plaza


def scene_range(sid):
    ids = [s for s, _ in TIMELINE]
    i = ids.index(sid)
    t0 = TIMELINE[i][1]
    t1 = TIMELINE[i + 1][1] if i + 1 < len(TIMELINE) else END_T
    f0, f1 = round(t0 * FPS), round(t1 * FPS)
    return t0, t1, f0, f1 - f0


def fr(sid, t):
    return max(1, int(round((t - dict(TIMELINE)[sid]) * FPS)) + 1)


def key(ob, path, f, v):
    setattr(ob, path, v)
    ob.keyframe_insert(path, frame=f)


# ------------------------------------------------------------------ easing & animasi per frame
def ease(u, kind="inout"):
    u = max(0.0, min(1.0, u))
    if kind == "lin":
        return u
    if kind == "out":
        return 1 - (1 - u) ** 3
    if kind == "in":
        return u ** 3
    if kind == "back":
        c1, c3 = 1.4, 2.4
        return 1 + c3 * (u - 1) ** 3 + c1 * (u - 1) ** 2
    return u * u * u * (u * (u * 6 - 15) + 10)            # smootherstep


def _lerp(a, b, u):
    if isinstance(a, (tuple, list)):
        return tuple(x + (y - x) * u for x, y in zip(a, b))
    return a + (b - a) * u


def anim(ob, path, f0, f1, v0, v1, kind="inout"):
    f1 = max(f1, f0 + 1)
    for f in range(f0, f1 + 1):
        key(ob, path, f, _lerp(v0, v1, ease((f - f0) / (f1 - f0), kind)))


def pop_in(ob, f, s=1.0, dur=11):
    sc = s if isinstance(s, tuple) else (s,) * 3
    key(ob, "scale", 1, (.001,) * 3)
    anim(ob, "scale", max(1, f), max(1, f) + dur, (.001,) * 3, sc, "back")


def pop_out(ob, f, dur=8):
    s0 = tuple(ob.scale)
    anim(ob, "scale", f, f + dur, s0, (.001,) * 3, "in")


def arc_move(ob, f0, f1, p0, p1, arc=0.0, kind="inout"):
    key(ob, "location", 1, p0)
    for f in range(f0, f1 + 1):
        u = ease((f - f0) / max(1, f1 - f0), kind)
        p = _lerp(p0, p1, u)
        key(ob, "location", f, (p[0], p[1], p[2] + arc * 4 * u * (1 - u)))


def path_walk(parts, pts, f0, f1, period=16):
    """jalan sepanjang polyline dengan kecepatan tetap (ayunan kaki halus)."""
    body = parts["body"]
    seg = [math.dist(a, b) for a, b in zip(pts[:-1], pts[1:])]
    tot = sum(seg) or 1
    for f in range(f0, f1 + 1):
        d = tot * (f - f0) / max(1, f1 - f0)
        i = 0
        while i < len(seg) - 1 and d > seg[i]:
            d -= seg[i]
            i += 1
        u = d / (seg[i] or 1)
        a, b = pts[i], pts[i + 1]
        key(body, "location", f, _lerp(a, b, min(1, u)))
        body.rotation_euler.z = math.atan2(b[1] - a[1], b[0] - a[0]) + math.pi / 2
        body.keyframe_insert("rotation_euler", frame=f)
    L.walk_cycle(parts, f0, f1, period, .5)


def hide_until(ob, f):
    SV.hide_until(ob, f)


def mat_color(m, keys):
    """kunci warna dasar material: [(frame, '#hex')]."""
    b = m.node_tree.nodes["Principled BSDF"].inputs["Base Color"]
    for f, hx in keys:
        b.default_value = lp.hex_rgba(hx)
        b.keyframe_insert("default_value", frame=f)


def emit_keys(m, keys):
    b = m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for f, v in keys:
        b.default_value = v
        b.keyframe_insert("default_value", frame=f)


def emit_ramp(m, f0, f1, v0, v1, kind="inout"):
    emit_keys(m, [(f, _lerp(v0, v1, ease((f - f0) / max(1, f1 - f0), kind))) for f in range(f0, f1 + 1)])


# ------------------------------------------------------------------ kamera halus
def _to_orbit(k):
    if len(k) == 5:
        t, tg, az, el, d = k
    else:
        t, p, tg = k
        dx, dy, dz = p[0] - tg[0], p[1] - tg[1], p[2] - tg[2]
        d = math.sqrt(dx * dx + dy * dy + dz * dz)
        az, el = math.degrees(math.atan2(dy, dx)), math.degrees(math.asin(dz / d))
    return t, [tg[0], tg[1], tg[2], az, el, math.log(d)]


def _hermite(ts, ps, t, endf=.7):
    n = len(ts)
    if n == 1:
        return ps[0]
    ms = []
    for i in range(n):
        if i == 0:
            m = [(b - a) / (ts[1] - ts[0]) * endf for a, b in zip(ps[0], ps[1])]
        elif i == n - 1:
            m = [(b - a) / (ts[-1] - ts[-2]) * endf for a, b in zip(ps[-2], ps[-1])]
        else:
            m = [(c - a) / (ts[i + 1] - ts[i - 1]) for a, c in zip(ps[i - 1], ps[i + 1])]
        ms.append(m)
    if t <= ts[0]:
        return [p + m * (t - ts[0]) for p, m in zip(ps[0], ms[0])]
    if t >= ts[-1]:
        return [p + m * (t - ts[-1]) for p, m in zip(ps[-1], ms[-1])]
    i = 0
    while t > ts[i + 1]:
        i += 1
    h = ts[i + 1] - ts[i]
    u = (t - ts[i]) / h
    h00, h10, h01, h11 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u, -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
    return [h00 * a + h10 * h * ma + h01 * b + h11 * h * mb
            for a, b, ma, mb in zip(ps[i], ps[i + 1], ms[i], ms[i + 1])]


def camera(sid, keys, lens=24, dof=None, fstop=3.2, shift=0.0):
    """keys: [(t, target, az, el, dist)] atau [(t, posisi, target)] (detik timeline). Dikunci tiap frame."""
    t0, t1, _, n = scene_range(sid)
    cam, tgt = make_camera(lens=lens if not isinstance(lens, list) else lens[0][1], shift_y=shift)
    ks = sorted((_to_orbit(k) for k in keys), key=lambda x: x[0])
    ts = [k[0] for k in ks]
    ps = [k[1] for k in ks]
    for i in range(1, len(ps)):                        # azimut menerus (tanpa loncat 360)
        while ps[i][3] - ps[i - 1][3] > 180:
            ps[i][3] -= 360
        while ps[i][3] - ps[i - 1][3] < -180:
            ps[i][3] += 360
    if isinstance(lens, list):
        lt = [x[0] for x in lens]
        lv = [[x[1]] for x in lens]
    for f in range(1, n + TAIL + 1):
        t = t0 + (f - 1) / FPS
        tx, ty, tz, az, el, ld = _hermite(ts, ps, t)
        key(tgt, "location", f, (tx, ty, tz))
        key(cam, "location", f, orbit((tx, ty, tz), az, el, math.exp(ld)))
        if isinstance(lens, list):
            cam.data.lens = _hermite(lt, lv, t, 0.0)[0] if len(lt) > 1 else lv[0][0]
            cam.data.keyframe_insert("lens", frame=f)
    if dof:
        cam.data.dof.use_dof = True
        cam.data.dof.focus_object = tgt
        cam.data.dof.aperture_fstop = fstop
    return cam, tgt


# ------------------------------------------------------------------ set dunia
def city(n, **kw):
    kw.setdefault("people", False)
    return SV.city(n + TAIL, **kw)


def neon(grid="vp_grid", em=2.0, rig_c=(0, 0, 2), rig_s=1.0, key_e=2200.0, rim=1500.0, fade=(8.0, 40.0)):
    return SV.base(grid, em, (0, 0), rig_c, rig_s, key_e, rim, fade)


def wedding_set(couple=True, pale=False, guests=10, abox=True, seed=1, buffet=True, chef_at=None):
    """gedung resepsi + pelaminan di tengah plaza + dua tenda (meja bundar / prasmanan) + tamu."""
    rnd = random.Random(seed)
    out = {"hall": N.wedding_hall("hall", (0, 6, Z0))}
    out["pel"] = N.pelaminan("pel", (0, PEL_Y, Z0), .85)
    N.tent("tentL", -21, -15.5, -10, -3.5, 4.2, (0, 0, Z0))
    N.tent("tentR", 10, -15.5, 21, -3.5, 4.2, (0, 0, Z0))
    mb = W.MB("tables")
    for k, (x, y) in enumerate(((-18, -12.5), (-13.5, -12.5), (-18, -7), (-13.5, -7))):
        N.round_table(mb, x, y, Z0, 1.0, 6, k)
    mb.build()
    if buffet:
        out["buffet"] = N.buffet("buf", (15.5, -6, Z0), 8.0, math.pi / 2)
    if abox:
        out["abox"] = N.amplop_box("abox", (-5.2, -13.6, Z0), .9)
    if couple:
        sk = "skin_dimas"
        out["groom"] = N.groom("dimas", (-.65, COUPLE_Y, Z0 + .38), 0, skin=sk)
        out["bride"] = N.bride("sari", (.65, COUPLE_Y, Z0 + .38), 0)
        if pale:
            mat_color(lp.mat("skin_dimas"), [(1, "#D5DECB")])
    out["guests"] = []
    spots = [(-17, -10), (-14.5, -9.6), (-19.5, -5), (-12, -14.5), (12.5, -12), (13, -9), (18, -13.5), (-7, -10),
             (6.5, -10.5), (7.5, -14), (-8.5, -6), (8.5, -5.5)]
    for k in range(min(guests, len(spots))):
        x, y = spots[k]
        out["guests"].append(N.guest(f"gs{k}", k + seed, (x, y, Z0), rnd.uniform(-.6, .6)))
    if chef_at:
        out["chef"] = N.chef("chef", chef_at, -.3)
    return out


def money_tower(name, layers, loc, s=.9, nx=2, ny=2):
    ob, h = N.money(name, layers, loc, nx, ny, s)
    return ob, h


def grow(ob, f0, f1, s=1.0, kind="out"):
    """tumbuh dari dasar (scale z)."""
    key(ob, "scale", 1, (s, s, .001))
    anim(ob, "scale", f0, f1, (s, s, .001), (s, s, s), kind)
    if f0 > 1:
        hide_until(ob, f0)


# ------------------------------------------------------------------ ADEGAN
def n01(n, A):
    """KORBAN: Dimas baru nikah, habis Rp100 juta. Diorama melayang -> menukik ke pelaminan."""
    sid = "N01"
    city(n, focus=None)
    w = wedding_set(couple=True, guests=12)
    L.pose(w["groom"], "wave")
    camera(sid, [(0.0, (0, -6, 0), -104, 30, 150), (1.7, (0, -6, 1.5), -97, 20, 46),
                 (3.10, (0, COUPLE_Y, 2.4), -92, 11, 14.5)], lens=24)
    A["DIMAS"] = (w["groom"]["body"], (0, 0, 2.7))
    A["PEL"] = ((0, PEL_Y + 2, 4.6))


def n02(n, A):
    """Rencana: modal pesta balik dari amplop tamu. Tamu antre, amplop melayang masuk kotak."""
    sid = "N02"
    city(n, focus=None)
    w = wedding_set(couple=True, guests=8, seed=3)
    bx, by = -5.2, -13.6
    q = []
    for k in range(4):
        g = N.guest(f"q{k}", 20 + k, (bx - .2 + k * .2, by - 2.2 - k * 1.3, Z0), math.pi * 0)
        q.append(g)
    L.pose(q[0], "arms_fwd")
    for k, t in enumerate((3.6, 4.4, 5.2, 6.0, 6.7)):
        e = N.envelope(f"env{k}", (0, 0, 0), .7, upright=False)
        f0, f1 = fr(sid, t), fr(sid, t + .55)
        hide_until(e, f0)
        p0 = (bx + .3, by - 2.0, Z0 + 1.6)
        p1 = (bx, by, Z0 + .9 * 1.9)
        arc_move(e, f0, f1, p0, p1, 1.4)
        anim(e, "rotation_euler", f0, f1, (0, 0, 0), (math.radians(90), 0, math.radians(20)))
        SV.hide_after(e, f1 + 1)
    camera(sid, [(3.10, (bx, by, 1.6), -128, 22, 15), (5.2, (bx + .5, by, 1.7), -104, 18, 13),
                 (7.40, (-1, by + 3, 2.2), -76, 16, 16)], lens=26)
    A["BOX"] = (w["abox"], (0, 0, 2.0))
    A["PEL"] = ((0, PEL_Y + 2, 4.4))


def n03(n, A):
    """Malam itu amplop dihitung, muka Dimas pucat. Panggung neon gelap, lampu meja, keringat dingin."""
    sid = "N03"
    neon(grid="vp_grid", em=1.2, rig_c=(0, 0, 1.5), key_e=1400, rim=1100, fade=(6, 26))
    mb = W.MB("desk")
    mb.cyl(0, 0, 0, .8, 1.25, "tbl_cloth", n=20)
    mb.cyl(0, 0, .78, .82, 1.29, "tbl_sash", n=20)
    mb.box(-.32, 1.15, 0, .32, 1.75, .5, "chair_w")
    mb.box(-.3, 1.6, .5, .3, 1.75, 1.25, "chair_w")
    mb.cyl(-.85, .3, .82, .86, .18, "bd_dark2", n=10)                         # lampu meja
    mb.box(-.87, .28, .86, -.83, .32, 1.5, "bd_dark2")
    mb.cyl(-.85, .2, 1.4, 1.62, .2, "n_gold", n=10, r_top=.08)
    d = mb.build()
    V.glow(d, {"n_gold": 6.0})
    lamp = P.point("lamp", (-.8, .1, 1.35), 140, (1, .8, .55), .2)
    pile = N.envelope_pile("pile", 46, (.1, -.1, .82), .55, .55)
    g = N.groom("dimas", (0, 1.25, -.56), math.pi * 0, skin="skin_dimas")
    L.pose(g, "sit")
    for side in ("armL", "armR"):
        g[side].rotation_euler = (-1.15, 0, (-.35 if side == "armR" else .35))
    counted = []
    for k, t in enumerate((8.85, 9.35, 9.85, 10.3)):
        e = N.envelope(f"c{k}", (0, 0, 0), .55)
        p0 = (.1, -.1, .9)
        p1 = (.75, -.35, .84 + k * .025)
        key(e, "location", 1, p0)
        hide_until(e, fr(sid, t))
        arc_move(e, fr(sid, t), fr(sid, t + .35), p0, p1, .25)
        counted.append(e)
    m = lp.mat("skin_dimas")
    f0, f1 = fr(sid, 10.6), fr(sid, 11.3)
    keys = []
    for f in range(f0, f1 + 1):
        u = ease((f - f0) / (f1 - f0))
        a, b = lp.hex_rgba("#E3A888"), lp.hex_rgba("#D2DCC8")
        keys.append((f, a, b, u))
    bc = m.node_tree.nodes["Principled BSDF"].inputs["Base Color"]
    for f, a, b, u in keys:
        bc.default_value = tuple(x + (y - x) * u for x, y in zip(a, b))
        bc.keyframe_insert("default_value", frame=f)
    sw = V.drop("sweat", (.2, 1.25 - .27, 1.62), .14, "n_cyan", 3.0)
    hide_until(sw, fr(sid, 11.0))
    anim(sw, "location", fr(sid, 11.0), n + TAIL, (.2, .98, 1.62), (.22, .97, 1.35), "lin")
    li = bpy.data.objects.get("key")
    if li:
        anim(li.data, "energy", fr(sid, 10.5), fr(sid, 11.4), li.data.energy, li.data.energy * .45)
    camera(sid, [(7.40, (0, .6, 1.4), -62, 28, 9.5), (9.6, (0, .8, 1.45), -80, 17, 6.6),
                 (11.80, (0, 1.2, 1.5), -91, 7, 3.9)], lens=30, dof=True, fstop=2.8)
    A["FACE"] = ((0, 1.0, 1.95))
    A["PILE"] = (pile, (0, 0, .3))


def n04(n, A):
    """KEJUTAN 1: 500 undangan x Rp100 rb = Rp50 juta. Grid amplop jatuh baris demi baris lalu jadi menara uang."""
    sid = "N04"
    neon(grid="vp_grid", em=1.8, rig_c=(0, 0, 1), rig_s=1.6, key_e=2600, rim=1600, fade=(14, 50))
    nx, ny, sx, sy = 20, 25, 1.05, .72
    rows = []
    t_a, t_b = 12.3, 13.9
    for j in range(ny):
        mb = W.MB(f"row{j}")
        for i in range(nx):
            N.env_mb(mb, (i - (nx - 1) / 2) * sx, 0, 0, .95)
        y = (ny - 1) / 2 * sy - j * sy
        ob = mb.build((0, y, 0))
        V.glow(ob, {"env": .55, "env2": .35, "env_gold": 1.2})
        f0 = fr(sid, t_a + (t_b - t_a) * j / (ny - 1))
        key(ob, "location", 1, (0, y, 4.0))
        hide_until(ob, f0)
        anim(ob, "location", f0, f0 + 9, (0, y, 4.0), (0, y, 0), "out")
        rows.append(ob)
    big = N.envelope("big", (0, 0, 0), 3.2, upright=True)
    V.glow(big, {"env": .7, "env2": .4, "env_gold": 1.5})
    t = H.text("big_t", "Rp100.000", .62, "money_red", depth=.04, loc=(0, -.14, .55), emission=.5)
    t.parent = big
    t.location = (0, -.16, .55)
    bp = (0, -11.2, .3)
    key(big, "location", 1, bp)
    pop_in(big, fr(sid, 15.4), 1.0)
    pop_out(big, fr(sid, 17.1))
    tower, th = money_tower("tw", 26, (0, 0, 0), 1.0)
    grow(tower, fr(sid, 17.3), fr(sid, 18.4))
    for j, ob in enumerate(rows):
        f = fr(sid, 16.95 + .3 * j / ny)
        anim(ob, "scale", f, f + 10, (1, 1, 1), (.001, .001, .001), "in")
    camera(sid, [(11.80, (0, 0, 0), -90, 72, 34), (14.3, (0, -2, 0), -98, 52, 27), (15.9, (0, -8.5, 1.4), -96, 22, 15),
                 (17.3, (0, -3, 2.5), -100, 24, 20), (19.20, (0, 0, th * .55), -112, 18, 17)], lens=24)
    A["TOWER"] = (tower, (0, 0, th + .3))
    A["BIG"] = (big, (0, 0, 1.9))
    A["GRID"] = ((0, (ny - 1) / 2 * sy + .5, .3))


def n05(n, A):
    """Cuma balik setengah: pilar BIAYA vs pilar BALIK (setengah) + bayangan bagian yang hilang."""
    sid = "N05"
    neon(grid="vp_grid2", em=1.6, rig_c=(0, 0, 3), rig_s=1.2)
    a = V.pillar("biaya", 8.0, 2.6, 2.6, "n_pink", 1.8, 7.0, (-2.4, 0, 0))
    b = V.pillar("balik", 4.0, 2.6, 2.6, "n_cyan", 1.8, 7.0, (2.4, 0, 0))
    gh = V.pillar("ghost", 8.0, 2.6, 2.6, "n_cyan", .1, 1.0, (2.4, 0, 0))
    grow(a, 1, fr(sid, 19.55), 1.0)
    grow(b, fr(sid, 19.4), fr(sid, 19.8), 1.0)
    grow(gh, fr(sid, 19.6), fr(sid, 20.0), 1.0)
    for x, k in ((-2.4, "n_pink"), (2.4, "n_cyan")):
        V.disc_ped("pd" + k, 2.4, k, (x, 0, -.3), 3.0, .3)
    camera(sid, [(19.20, (0, 0, 3.8), -104, 12, 17.5), (20.30, (0, 0, 3.6), -90, 9, 14.8)], lens=26)
    A["BIAYA"] = (a, (0, 0, 8.3))
    A["BALIK"] = (b, (0, 0, 4.3))


def n06(n, A):
    """Tiap undangan datang berdua: pasangan-pasangan tamu berjalan dari trotoar ke tenda."""
    sid = "N06"
    city(n, focus=None, traffic=False)
    w = wedding_set(couple=True, guests=6, seed=5)
    f0, f1 = 1, n + TAIL
    lead = None
    for k in range(7):
        x = -12 + k * 3.6 + (1.0 if k % 2 else 0)
        y0 = -19.3 + (k % 3) * .9
        for side, dx in ((0, -.42), (1, .42)):
            g = N.guest(f"p{k}{side}", k * 2 + side + 40, (x + dx, y0, Z0))
            path_walk(g, [(x + dx, y0, Z0 - .02), (x + dx * .9, y0 + 7.0, Z0)], f0, f1, 18)
            if k == 3 and side == 0:
                lead = g
    camera(sid, [(20.30, (-4, -17, 1.6), -124, 15, 21), (22.95, (1, -14, 1.9), -96, 13, 17.5)], lens=26)
    A["PAIR"] = (lead["body"], (.42, 0, 2.7))


def n07(n, A):
    """1.000 porsi x Rp60 rb = Rp60 juta: lautan piring nasi -> menara uang."""
    sid = "N07"
    neon(grid="vp_grid", em=1.8, rig_c=(0, 0, 1), rig_s=1.8, key_e=2600, rim=1600, fade=(16, 56))
    nx, ny, sp = 40, 25, .78
    rows = []
    for j in range(ny):
        mb = W.MB(f"pr{j}")
        rnd = random.Random(j)
        for i in range(nx):
            N.plate_mb(mb, (i - (nx - 1) / 2) * sp, 0, 0, 1.0, rnd)
        y = (ny - 1) / 2 * sp - j * sp
        ob = mb.build((0, y, 0))
        V.glow(ob, {"plate": .5, "rice": .55, "food1": .5, "food2": .5, "food3": .5})
        f0 = fr(sid, 23.0 + .9 * j / (ny - 1))
        key(ob, "location", 1, (0, y, 3.0))
        hide_until(ob, f0)
        anim(ob, "location", f0, f0 + 9, (0, y, 3.0), (0, y, 0), "out")
        rows.append(ob)
    pd = V.disc_ped("pd", 1.8, "n_gold", (0, -12.4, 0), 4.0, .5)
    pl = W.MB("hero_plate")
    N.plate_mb(pl, 0, 0, 0, 3.4, random.Random(1))
    hp = pl.build((0, -12.4, .55))
    V.glow(hp, {"plate": .6, "rice": .6, "food1": .6, "food2": .6, "food3": .6})
    tg = H.text("tag", "Rp60.000", .7, "n_gold", depth=.06, loc=(0, -14.3, .7), emission=4.0)
    for ob in (hp, tg, *pd):
        key(ob, "scale", 1, (.001,) * 3)
        pop_in(ob, fr(sid, 24.8), 1.0)
        pop_out(ob, fr(sid, 26.0))
    tower, th = money_tower("tw", 31, (0, 0, 0), 1.0)
    grow(tower, fr(sid, 26.1), fr(sid, 27.0))
    for j, ob in enumerate(rows):
        f = fr(sid, 25.9 + .35 * j / ny)
        anim(ob, "scale", f, f + 10, (1, 1, 1), (.001, .001, .001), "in")
    camera(sid, [(22.95, (0, 0, 0), -62, 64, 40), (24.6, (0, -8, .8), -76, 30, 18), (25.9, (0, -11, 1.4), -86, 18, 12),
                 (27.60, (0, 0, th * .5), -98, 20, 20)], lens=24)
    A["TOWER"] = (tower, (0, 0, th + .3))
    A["PLATE"] = (hp, (0, 0, 1.2))


def n08(n, A):
    """Amplop nggak cukup buat bayar katering: timbangan miring ke tagihan katering."""
    sid = "N08"
    neon(grid="vp_grid2", em=1.5, rig_c=(0, 0, 3), rig_s=1.3)
    b = N.balance("bal", (0, 0, 0), 1.0, "n_cyan")
    pl, pr = b["pans"]
    ep = N.envelope_pile("ep", 26, (0, 0, 0), .8, .7)
    ep.parent = pl
    ep.location = (0, 0, -2.18)
    ml, hl = money_tower("ml", 5, (0, 0, 0), .55)
    ml.parent = pl
    ml.location = (.45, .3, -2.18)
    bill = W.MB("bill")
    bill.box(-.75, -.05, 0, .75, .05, 1.9, "wd_white")
    bill.box(-.6, -.07, 1.45, .6, -.05, 1.6, "kt_awn")
    for k in range(4):
        bill.box(-.6, -.07, .4 + k * .22, .4, -.05, .48 + k * .22, "c_black")
    bo = bill.build()
    bo.parent = pr
    bo.location = (-.3, -.4, -2.18)
    bo.rotation_euler = (math.radians(-12), 0, 0)
    mr, hr = money_tower("mr", 7, (0, 0, 0), .55)
    mr.parent = pr
    mr.location = (.45, .3, -2.18)
    f_a, f_b = fr(sid, 28.85), fr(sid, 30.4)
    for f in range(1, n + TAIL + 1):
        if f <= f_a:
            deg = -4.0 * math.sin(math.pi * min(1, f / f_a) * 1.0) * .4
        else:
            u = (f - f_a) / FPS
            deg = 14.0 * (1 - math.exp(-3.2 * u) * math.cos(5.5 * u))
        N.balance_key(b, f, deg)
    camera(sid, [(27.60, (0, 0, 3.4), -114, 12, 18.5), (29.5, (0, 0, 3.2), -98, 13, 16.5),
                 (31.30, (.8, 0, 3.0), -82, 15, 15.5)], lens=26)
    A["AMPLOP"] = (pl, (0, 0, -.4))
    A["KATERING"] = (pr, (0, 0, -.4))


def n09(n, A):
    """KAIL 1: Rp60 juta itu masuk ke kantong siapa? Menara uang melayang menyusuri jalur neon ke tanda tanya."""
    sid = "N09"
    neon(grid="vp_grid", em=1.6, rig_c=(0, 14, 2), rig_s=2.2, fade=(20, 70))
    tower, th = money_tower("tw", 18, (0, 0, 0), .8)
    path = W.MB("path")
    for k in range(40):
        y = k * 1.0
        path.box(-.12, y, .01, .12, y + .6, .04, "n_gold")
    po = path.build()
    V.glow(po, {"n_gold": 5.0})
    for ob in (po,):
        key(ob, "scale", 1, (1, .001, 1))
        anim(ob, "scale", fr(sid, 31.6), fr(sid, 33.0), (1, .001, 1), (1, 1, 1), "out")
    f0, f1 = fr(sid, 32.3), fr(sid, 34.7)
    for f in range(1, n + TAIL + 1):
        u = ease((f - f0) / (f1 - f0)) if f >= f0 else 0.0
        lift = 1.6 * ease((f - f0) / 10) if f >= f0 else 0.0
        key(tower, "location", f, (0, 32 * u, lift + .25 * math.sin(f / 9)))
        key(tower, "rotation_euler", f, (0, 0, .6 * u))
    sil = W.MB("sil")
    sil.box(-5, 38, 0, 5, 44, 7, "bd_dark")
    sil.prism_x([(37.5, 7), (41, 9.5), (44.5, 7)], -5.2, 5.2, "bd_dark2")
    sil.box(-5.1, 37.9, 6.9, 5.1, 38.0, 7.1, "n_pink")
    so = sil.build()
    V.glow(so, {"n_pink": 4.0})
    q = V.qmark("q", (0, 36.5, 9.5), 1.5, "n_pink", 7)
    key(q, "scale", 1, (.001,) * 3)
    pop_in(q, fr(sid, 33.9), 1.0)
    camera(sid, [(31.30, (0, 0, 2.0), -122, 18, 15), (33.2, (0, 12, 3.6), -102, 13, 17),
                 (35.10, (0, 31, 5.4), -93, 9, 19)], lens=26)
    A["TOWER"] = (tower, (0, 0, th + .4))
    A["Q"] = ((0, 37, 13.5))


def n10(n, A):
    """Ke pemilik katering: usaha katering + koki pemilik + van katering (kota)."""
    sid = "N10"
    city(n, focus=None)
    kt = N.katering_shop("kt", (0, 5, Z0))
    ch = N.chef("chef", (2.4, -2.6, Z0), -.25)
    L.pose(ch, "cheer")
    for k, x in enumerate((-4.5, -2.6)):
        s_ = N.chef(f"st{k}", (x, -1.2, Z0), .4)
        L.pose(s_, "arms_fwd")
    N.katering_van("van", (-9, -6.5, Z0), 0)
    mn, h = money_tower("mn", 4, (3.9, -3.6, Z0), .5)
    camera(sid, [(35.10, (0, 0, 2.8), -102, 24, 34), (36.45, (1.5, -2.4, 2.4), -95, 13, 16.5)], lens=26)
    A["CHEF"] = (ch["body"], (0, 0, 2.9))


def n11(n, A):
    """KEJUTAN 2: margin 30% -> Rp18 juta dibawa pulang pemilik katering."""
    sid = "N11"
    neon(grid="vp_grid", em=1.6, rig_c=(2, 0, 3), rig_s=1.6)
    cost = V.pillar("cost", 7.0, 3.0, 3.0, "n_purple", 1.3, 5.0, (-2.5, 0, 0))
    gold_root = bpy.data.objects.new("gold_root", None)
    lp._link(gold_root)
    gold = V.pillar("gold", 3.0, 3.0, 3.0, "n_gold", 2.2, 8.0, (0, 0, 0))
    gold.parent = gold_root
    p0 = (-2.5, 0, 7.05)
    key(gold_root, "location", 1, p0)
    gi = [c for c in gold.children if "_in" in c.name][0]
    m = gi.data.materials[0].copy()
    gi.data.materials[0] = m
    V.disc_ped("pc", 2.6, "n_purple", (-2.5, 0, -.3), 3.0, .3)
    V.disc_ped("pk", 2.2, "n_gold", (6.5, 0, -.3), 3.0, .3)
    ch = N.chef("chef", (6.5, .6, 0), -.35)
    L.pose(ch, "stand")
    for k, kind in enumerate(("bahan", "produksi", "distribusi")):
        ic = V.icon(f"ic{k}", kind, .8, (-4.6 + k * 2.1, -2.6, 0), em=1.4)
        key(ic, "scale", 1, (.001,) * 3)
        pop_in(ic, fr(sid, 37.0) + k * 4, .8)
    f0, f1 = fr(sid, 39.6), fr(sid, 40.9)
    arc_move(gold_root, f0, f1, p0, (6.5, -.9, .1), 3.5)
    anim(gold_root, "scale", f0, f1, (1, 1, 1), (.45, .45, .45))
    pop_out(gold_root, fr(sid, 40.95), 6)
    mn, h = money_tower("mn", 9, (6.5, -1.0, 0), .65)
    grow(mn, fr(sid, 40.95), fr(sid, 41.6))
    pr = m.node_tree.nodes.get("Emission")
    if pr is not None:
        st = pr.inputs["Strength"]
        for f, v in ((1, 2.2), (fr(sid, 38.45), 2.2), (fr(sid, 38.8), 5.5), (fr(sid, 39.5), 3.0)):
            st.default_value = v
            st.keyframe_insert("default_value", frame=f)
    L.pose(ch, "stand", fr(sid, 41.0))
    L.pose(ch, "cheer", fr(sid, 41.5))
    camera(sid, [(36.45, (-1, 0, 4.8), -108, 14, 22), (39.2, (1.2, 0, 4.6), -96, 15, 21),
                 (42.75, (5.8, 0, 2.6), -80, 11, 13)], lens=26)
    A["MARGIN"] = (gold_root, (0, 0, 3.3))
    A["COST"] = (cost, (0, 0, 7.4))
    A["CHEF"] = (ch["body"], (0, 0, 2.9))


def n12(n, A):
    """Nikahan biasanya akhir pekan; 4 acara sebulan = Rp72 juta. Kalender neon, kolom Sabtu-Minggu menyala."""
    sid = "N12"
    neon(grid="vp_grid", em=1.4, rig_c=(0, 0, 4), rig_s=1.4, key_e=1800)
    cal = N.calendar("cal", (0, 2, 0), 1.0)
    for r, row in enumerate(cal["weekend"]):
        for c, ob in enumerate(row):
            m = lp.mat("n_pink", .0001 * (r * 2 + c + 1)).copy()
            V.set_mat(ob, m)
            f = fr(sid, 43.95 + .07 * (r * 2 + c))
            emit_keys(m, [(1, 0.0), (f, 0.0)])
            emit_ramp(m, f, f + 8, 0.0, 2.6, "out")
    stacks = []
    for r in range(4):
        x = cal["cells"][(r, 5)].location.x
        cell = cal["cells"][(r, 5)]
        cx = -cal["w"] / 2 + .18 + 1.3 / 2 + 5 * (1.3 + .18)
        cz = cal["h"] - 1.4 - .18 - 1.0 / 2 - r * (1.0 + .18)
        ob, h = money_tower(f"m{r}", 3, (cx, 2 - .5, cz - .35), .32, 1, 1)
        key(ob, "scale", 1, (.001,) * 3)
        pop_in(ob, fr(sid, 44.75 + r * .27), 1.0)
        stacks.append(ob)
    camera(sid, [(42.75, (0, 2, 4.0), -128, 10, 17.5), (44.6, (0, 2, 3.9), -102, 5, 14.5),
                 (47.90, (1.8, 2, 3.7), -88, 3, 12.5)], lens=26)
    A["WE"] = ((cal["w"] / 2 - 1.3, 1.6, cal["h"] + .2))
    A["SAT"] = (stacks[0], (0, 0, 1.2))


def n13(n, A):
    """Di hari bahagia Dimas, yang paling untung bukan pengantinnya: geser dari pengantin pucat ke koki."""
    sid = "N13"
    city(n, focus=None, traffic=False)
    w = wedding_set(couple=True, pale=True, guests=10, seed=7, chef_at=(12.5, -17.0, .22))
    L.pose(w["chef"], "cheer")
    mn, h = money_tower("mn", 6, (14.0, -17.8, .22), .55)
    camera(sid, [(47.90, (-.4, COUPLE_Y, 2.3), -100, 11, 13), (49.8, (6, -12, 2.3), -94, 12, 15),
                 (51.95, (12.6, -16.8, 2.2), -86, 11, 12.5)], lens=26)
    A["DIMAS"] = (w["groom"]["body"], (0, 0, 2.7))
    A["CHEF"] = (w["chef"]["body"], (0, 0, 2.9))


def n14(n, A):
    """KAIL 2: kalau seuntung itu, kenapa banyak yang tutup? Deretan usaha katering menurunkan rolling door."""
    sid = "N14"
    city(n, focus=None)
    shops = [N.katering_shop(f"k{i}", (x, 4.5, Z0), 13.0, 9.0, "KATERING") for i, x in enumerate((-15.5, 0, 15.5))]
    for i, (sh, t) in enumerate(zip(shops, (53.95, 54.3, 54.65))):
        N.close_shutter(sh["door"], fr(sid, t), fr(sid, t + .45))
        key(sh["tutup"], "scale", 1, (.001,) * 3)
        pop_in(sh["tutup"], fr(sid, t + .45), 1.0)
    q = V.qmark("q", (0, -2, 9.0), 1.3, "n_pink", 7)
    key(q, "scale", 1, (.001,) * 3)
    pop_in(q, fr(sid, 54.8), 1.0)
    for k in range(4):
        g = N.guest(f"w{k}", 60 + k, (-10 + k * 6.5, -8 - (k % 2) * 2, Z0), 0)
        L.pose(g, "shrug" if k % 2 else "stand")
    camera(sid, [(51.95, (0, 3, 3.0), -102, 30, 62), (53.6, (0, 3, 3.4), -96, 20, 40),
                 (55.40, (0, 2.5, 4.0), -90, 13, 31)], lens=24)
    A["MID"] = (shops[1]["body"], (0, 0, 7.8))
    A["Q"] = (q, (0, 0, 3.0))


def n15(n, A):
    """Jawabannya di part 2: modal buka katering & jebakan yang bikin bangkrut. Jebakan tikus raksasa berumpan uang."""
    sid = "N15"
    neon(grid="vp_grid2", em=1.5, rig_c=(0, 0, 1.5), rig_s=1.5)
    tr = N.trap("trap", (0, 0, 0), 1.25)
    mn, h = money_tower("bait", 6, (0, -1.6, .44), .6)
    t, fo = V.neon_sign("p2", "PART 2", (0, 9, 3.6), 1.6, "n_cyan", 7.0)
    for ob in (t, fo):
        key(ob, "scale", 1, (.001,) * 3)
        pop_in(ob, fr(sid, 56.15), 1.0)
    piv = tr["piv"]
    fs = fr(sid, 58.15)
    key(piv, "rotation_euler", 1, (math.radians(-180), 0, 0))
    key(piv, "rotation_euler", fs, (math.radians(-180), 0, 0))
    for f in range(fs, fs + 9):
        u = (f - fs) / 8
        key(piv, "rotation_euler", f, (math.radians(-180 + 186 * u ** 2.2), 0, 0))
    for f, a in ((fs + 10, -4), (fs + 13, 2), (fs + 16, -1), (fs + 19, 0)):
        key(piv, "rotation_euler", f, (math.radians(a), 0, 0))
    m = mn.data.materials[0]
    camera(sid, [(55.40, (0, -.6, 1.2), -126, 34, 15), (57.8, (0, -.8, 1.2), -102, 24, 11.5),
                 (60.60, (0, 2.5, 2.6), -92, 11, 17)], lens=26)
    A["BAIT"] = (mn, (0, 0, h + .3))
    A["P2"] = (t, (0, 0, 2.2))


def n16(n, A):
    """Follow: diorama dengan baliho PART 2 (kota), kamera naik pelan."""
    sid = "N16"
    city(n, focus=None)
    N.katering_shop("kt", (0, 5, Z0), 13, 9, "KATERING")
    bb, bt = V.billboard_day("p2", "PART 2", (0, 17, Z0), 14, 6, "vs_pink", 1.2)
    N.chef("chef", (2, -2.5, Z0), -.2)
    N.katering_van("van", (-6, -6, Z0), 0)
    camera(sid, [(60.60, (0, 4, 5.0), -98, 12, 32), (62.50, (0, 3, 4.4), -92, 22, 46)], lens=24)
    A["P2"] = (bt, (0, 0, 3.0))


def n17(n, A):
    """Tim PESTA besar vs tim nikah sederhana + MODAL usaha: kiri pesta, kanan usaha kecil."""
    sid = "N17"
    city(n, focus=None, center_clear=22)
    rnd = random.Random(9)
    N.pelaminan("pel", (-13, -9.2, Z0), .7)
    mb = W.MB("tbl")
    for k, (x, y) in enumerate(((-18.5, -13), (-7.5, -13), (-18.5, -6), (-7.5, -6))):
        N.round_table(mb, x, y, Z0, .9, 6, k)
    for k in range(5):
        L.balloons(mb, -20.5 + k * 3.8, -15.3, Z0, .9)
    mb.build()
    for k in range(9):
        g = N.guest(f"pg{k}", 70 + k, (-19 + (k % 5) * 3.3, -11 + (k // 5) * 3 + rnd.uniform(-.4, .4), Z0),
                    rnd.uniform(-.5, .5))
        if k % 3 == 0:
            L.pose(g, "cheer")
    N.groom("dimasL", (-13.6, -9.2 + 1.3, Z0 + .32), 0, skin="skin2")
    N.bride("sariL", (-12.4, -9.2 + 1.3, Z0 + .32), 0)
    sh = N.katering_shop("usaha", (12, 3.5, Z0), 11.0, 8.0, "USAHA")
    g2 = N.groom("dimasR", (10.6, -4.5, Z0), -.2, skin="skin2")
    b2 = N.bride("sariR", (12.0, -4.6, Z0), .2)
    L.pose(g2, "wave")
    mn, h = money_tower("mn", 10, (14.6, -5.2, Z0), .6)
    for nm, body, x, k in (("sgP", "PESTA", -11, "n_pink"), ("sgM", "MODAL", 11, "n_cyan")):
        t, fo = V.neon_sign(nm, body, (x, -1.0, 10.5), 1.7, k, 7.0)
        for ob in (t, fo):
            key(ob, "scale", 1, (.001,) * 3)
            pop_in(ob, fr(sid, 63.4 if body == "PESTA" else 64.6), 1.0)
    camera(sid, [(62.50, (-12, -6, 3.2), -102, 17, 27), (65.2, (11, -5, 3.2), -84, 17, 27),
                 (67.6, (0, -4, 4.6), -92, 24, 58), (70.35, (0, -4, 4.6), -93, 25, 62)], lens=24)
    A["PESTA"] = ((-11, -1.0, 12.8))
    A["MODAL"] = ((11, -1.0, 12.8))


def n18(n, A):
    """Ini simulasi: kamera mundur ke diorama utuh yang melayang di dunia neon."""
    sid = "N18"
    city(n, focus=None)
    w = wedding_set(couple=True, guests=12, seed=11)
    N.katering_van("van", (16, -18.2, Z0), 0)
    camera(sid, [(70.35, (0, -4, 2.4), -94, 22, 34), (72.4, (0, -4, 1.2), -100, 26, 80),
                 (74.60, (0, -4, 0), -108, 30, 150)], lens=24)
    A["HALL"] = (w["hall"]["sign"], (0, 0, 1.5))


SCENES = {f"N{i:02d}": globals()[f"n{i:02d}"] for i in range(1, 19)}


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
    nt = n + TAIL
    sc.frame_start, sc.frame_end = 1, nt
    A = {}
    SCENES[args.scene](n, A)
    cam = sc.camera
    os.makedirs(os.path.join(args.out, "frames"), exist_ok=True)
    data = {"scene": args.scene, "t0": t0, "t1": t1, "global_f0": gf0, "n": n, "tail": TAIL, "fps": FPS,
            "res": [rx, ry], "frames": {}}
    for f in range(1, nt + 1):
        sc.frame_set(f)
        pos = {}
        for name, p in A.items():
            v = world_to_camera_view(sc, cam, _anchor_pos(p))
            if v.z > 0:
                pos[name] = [round(v.x * rx, 1), round((1 - v.y) * ry, 1)]
        data["frames"][f] = pos
    with open(os.path.join(args.out, "anchors.json"), "w") as fh:
        json.dump(data, fh)
    lo, hi = (1, nt) if not args.frames else map(int, args.frames.split("-"))
    for f in range(lo, hi + 1):
        path = os.path.join(args.out, "frames", f"{f:04d}.png")
        if os.path.exists(path) and not args.frames:
            continue
        sc.frame_set(f)
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
    print("DONE", args.scene, nt)


if __name__ == "__main__":
    main()
