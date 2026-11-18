"""Adegan "Bedah Bisnis: Liquid Vape Part 2 — Raka bikin brand liquid" (alur 3K: Korban -> Kejutan -> Kail).
Visual: kota diorama siang melayang di dunia neon (cerita) + panggung neon (angka). Infrastruktur kehalusan
(kamera spline per-frame, easing per-frame, frame ekor untuk crossfade) dipakai dari scenes_nkh.

  python3 render/scenes_brd.py -- --scene B01 --out DIR [--res 720x1280] [--samples 4] [--frames a-b]
"""
import math
import os
import random
import sys

import bpy  # noqa: F401  (harus sebelum lowpoly: bmesh)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowpoly as lp  # noqa: E402
import world as W  # noqa: E402
import world_amdk as M  # noqa: E402
import world_brd as B  # noqa: E402
import world_laundry as L  # noqa: E402
import world_nkh as N  # noqa: E402
import world_vap as V  # noqa: E402
import scenes_nkh as K  # noqa: E402
import scenes_vap as SV  # noqa: E402
from scenes_nkh import FPS, TAIL, anim, arc_move, ease, emit_ramp, grow, hide_until, key, pop_in, pop_out  # noqa

TIMELINE = [("B01", 0.00), ("B02", 5.20), ("B03", 6.75), ("B04", 11.55), ("B05", 14.65), ("B06", 20.65),
            ("B07", 28.85), ("B08", 33.30), ("B09", 36.15), ("B10", 40.50), ("B11", 43.65), ("B12", 48.10),
            ("B13", 50.80), ("B14", 52.65), ("B15", 55.90), ("B16", 59.25), ("B17", 63.60), ("B18", 68.75),
            ("B19", 75.85)]
END_T = 82.2
CITY = {"B01", "B04", "B05", "B08", "B10", "B11", "B15", "B16", "B18", "B19"}
K.TIMELINE, K.END_T, K.CITY = TIMELINE, END_T, CITY
Z0 = .24
UNIT = .2                       # tinggi per Rp1 juta di menara modal
COSTS = [("p1", 25, "n_cyan"), ("p2", 8, "n_purple"), ("p3", 15, "n_pink"), ("p4", 42, "n_gold")]


def fr(sid, t):
    return K.fr(sid, t)


def camera(sid, keys, **kw):
    return K.camera(sid, keys, **kw)


def city(n, **kw):
    return K.city(n, **kw)


def neon(**kw):
    return K.neon(**kw)


def money_tower(name, layers, loc, s=.9, nx=2, ny=2):
    return N.money(name, layers, loc, nx, ny, s)


def modal_tower(prefix, loc=(0, 0, 0), w=3.6, upto=4, em=1.4):
    """menara modal bertumpuk: produksi 25 / desain 8 / marketing 15 / cukai+pajak 42 (juta). Return list pilar
    [(root, z_bawah, tinggi)]."""
    out, z = [], 0.0
    for i, (nm, jt, k) in enumerate(COSTS[:upto]):
        h = jt * UNIT
        p = V.pillar(f"{prefix}_{nm}", h, w, w, k, em, 5.0, (loc[0], loc[1], loc[2] + z))
        out.append((p, z, h))
        z += h + .06
    return out


def tower_total():
    return sum(jt * UNIT + .06 for _, jt, _ in COSTS)


def raka(name="raka", loc=(0, 0, Z0), rot=0.0, pose=None, hold=None):
    r = B.raka(name, loc, rot, hold)
    if pose:
        L.pose(r, pose)
    return r


def pose_at(parts, kind, f):
    L.pose(parts, kind, f)


# ================================================================== KORBAN
def b01(n, A):
    """Raka mau bikin brand liquid sendiri; dia pikir modal terbesar ada di racikan rasa. Kamera menukik."""
    sid = "B01"
    city(n, focus=None, center_clear=22)
    B.brand_store("bs", (0, 5, Z0), "RAKA LIQUID")
    tb = B.lab_table("lab", (0, -6.5, Z0))
    r = raka("raka", (0, -5.1, Z0), 0)
    pose_at(r, "stand", 1)
    pose_at(r, "stand", fr(sid, 1.7))
    pose_at(r, "think", fr(sid, 2.2))
    pose_at(r, "think", fr(sid, 3.7))
    pose_at(r, "point", fr(sid, 4.1))
    ic = V.icon("flask", "bahan", 1.0, (0, -6.5, 4.6), em=3.5)
    pop_in(ic, fr(sid, 3.85), 1.0)
    SV.spin(ic, 1, n + TAIL, 70)
    for k, c in enumerate(("n_pink", "n_cyan", "n_gold")):
        d = V.drop(f"dr{k}", (-1.6 + k * 1.6, -6.4, 3.0), .35, c, 4.0)
        pop_in(d, fr(sid, 4.0) + k * 3, .35)
        anim(d, "location", fr(sid, 4.0) + k * 3, n + TAIL, (-1.6 + k * 1.6, -6.4, 3.0), (-1.6 + k * 1.6, -6.4, 3.8))
    camera(sid, [(0.0, (0, -4, 0), -104, 40, 150), (2.3, (0, -6, 2.0), -96, 20, 22),
                 (5.20, (0, -6.2, 2.4), -88, 12, 12.5)], lens=24)
    A["RAKA"] = (r["body"], (0, 0, 2.7))
    A["FLASK"] = (ic, (0, 0, 2.4))


def b02(n, A):
    """Ternyata... salah besar: ikon racikan rasa dicoret X merah."""
    sid = "B02"
    neon(grid="vp_grid2", em=1.6, rig_c=(0, 0, 2), rig_s=1.1)
    V.disc_ped("ped", 2.4, "n_pink", (0, 0, 0), em=3.0)
    ic = V.icon("flask", "bahan", 1.5, (0, 0, .5), em=3.5)
    SV.spin(ic, 1, n + TAIL, 25)
    x = V.xmark("x", (0, -2.6, 2.4), 1.35)
    key(x, "scale", 1, (.001,) * 3)
    anim(x, "scale", fr(sid, 5.95), fr(sid, 5.95) + 6, (2.4,) * 3, (1.35,) * 3, "out")
    hide_until(x, fr(sid, 5.95))
    camera(sid, [(5.20, (0, 0, 2.0), -98, 10, 15), (6.75, (0, 0, 2.1), -90, 9, 13)], lens=26)
    A["FLASK"] = (ic, (0, 0, 2.6))


def b03(n, A):
    """Part 1: Rp42 ribu per botol masuk ke negara. Lapisan negara di botol berpendar lalu terbang ke NEGARA."""
    sid = "B03"
    neon(grid="vp_grid", em=1.8, rig_c=(3, 3, 2), rig_s=1.6, fade=(14, 50))
    V.disc_ped("ped", 2.4, "n_cyan", (0, 0, 0), em=3.0)
    b = V.bottle("hb", 1.25, SV.PORSI, label=False, pita=True, liquid_em=1.4, loc=(0, 0, .5))
    b["root"].rotation_euler.z = math.radians(-14)
    gv = V.gov_building("gov", (9, 9, 0), "NEGARA", 1.0)
    blk = V.block("blk", "n_gold", 1.5, (0, 0, 0))
    p0, p1 = (0, -.2, 6.6), (9, 6.5, 2.6)
    key(blk, "location", 1, p0)
    pop_in(blk, fr(sid, 8.6), 1.0)
    arc_move(blk, fr(sid, 9.9), fr(sid, 11.0), p0, p1, 3.0)
    key(blk, "location", fr(sid, 8.6), p0)
    pop_out(blk, fr(sid, 11.05), 8)
    neg = lp.mat("lq_negara")
    emit_ramp(neg, fr(sid, 8.4), fr(sid, 8.9), 1.4, 6.0)
    camera(sid, [(6.75, (0, 0, 3.0), -100, 10, 15), (9.6, (2.5, 2.5, 3.8), -102, 14, 22),
                 (11.55, (4.5, 4.5, 3.8), -100, 15, 27)], lens=24)
    A["BOTTLE"] = (b["root"], (0, 0, 6.2))
    A["GOV"] = (gv if not isinstance(gv, dict) else gv["body"], (0, 0, 8.0))


def b04(n, A):
    """Sekarang: gimana rasanya ada di posisi brand? Toko/kantor brand RAKA LIQUID + Raka + tanda tanya."""
    sid = "B04"
    city(n, focus=None, center_clear=22)
    B.brand_store("bs", (0, 5, Z0), "RAKA LIQUID")
    r = raka("raka", (1.2, -2.0, Z0), -.3, "stand")
    pose_at(r, "stand", fr(sid, 12.8))
    pose_at(r, "shrug", fr(sid, 13.3))
    q = V.qmark("q", (1.2, -2.2, 4.4), .7, "n_purple", 6)
    pop_in(q, fr(sid, 13.9), 1.0)
    camera(sid, [(11.55, (0, 1, 4.0), -120, 14, 30), (13.2, (.6, -1, 3.0), -104, 12, 21),
                 (14.65, (1.0, -1.6, 2.8), -94, 10, 16)], lens=24)
    A["STORE"] = ((0, 4.8, 8.6))
    A["RAKA"] = (r["body"], (0, 0, 2.7))


def b05(n, A):
    """Mulai dari 1.000 botol 60 ml, diproduksi bareng pabrik yang sudah punya izin cukai."""
    sid = "B05"
    city(n, focus=None, center_clear=48)
    fac = V.factory_day("fac", (6, 14, Z0), "PABRIK LIQUID")
    r = raka("raka", (-4.5, -8.0, Z0), .5, "point")
    vn = V.box_van("van", (4.5, -9.5, Z0), 0)
    stacks = []
    for k, (x, y) in enumerate(((-1.0, -6.2), (1.6, -6.2), (-1.0, -4.0), (1.6, -4.0))):
        mb = W.MB(f"ct{k}")
        M.carton_stack(mb, 0, 0, 0, 2, 2, 3, 1.2, .9, .7, kind="liq")
        ob = mb.build((x, y, Z0))
        grow(ob, fr(sid, 16.0) + k * 6, fr(sid, 16.0) + k * 6 + 12)
        stacks.append(ob)
    t, fo = V.neon_sign("izin", "IZIN CUKAI", (6, 3.0, 12.6), 1.0, "n_green", 7.0)
    for ob in (t, fo):
        pop_in(ob, fr(sid, 19.95), 1.0)
    camera(sid, [(14.65, (0, -6, 2.0), -112, 22, 30), (17.4, (0, -4, 3.0), -100, 18, 34),
                 (20.65, (2, 2, 5.0), -94, 16, 46)], lens=24)
    A["RAKA"] = (r["body"], (0, 0, 2.7))
    A["CARTON"] = ((.3, -5.1, 2.7))
    A["FAC"] = (fac["sign"], (0, 0, 2.2))


# ================================================================== KEJUTAN 1: rincian modal
def b06(n, A):
    """Produksi+botol+label+box 25 jt, desain & legalitas merek 8 jt, marketing 15 jt: menara modal naik."""
    sid = "B06"
    neon(grid="vp_grid", em=1.7, rig_c=(0, 0, 4), rig_s=1.8, fade=(14, 50))
    V.base_plate("bp", 5.2, 5.2, "n_cyan", (0, 0, 0), 3.0)
    tw = modal_tower("mt", (0, 0, .14), upto=3)
    times = [(23.4, 24.6), (25.4, 26.5), (27.45, 28.4)]
    for (p, z, h), (t0, t1) in zip(tw, times):
        grow(p, fr(sid, t0), fr(sid, t1), 1.0)
    ics = []
    for i, (kind, t, x) in enumerate((("produksi", 20.85, -3.6), ("botol", 21.9, 0), ("distribusi", 23.0, 3.6))):
        ic = V.icon(f"ic{i}", kind, .8, (x, -3.4, .2), em=3.0)
        pop_in(ic, fr(sid, t), .8)
        arc_move(ic, fr(sid, 23.6), fr(sid, 24.4), (x, -3.4, .2), (0, 0, 2.6), 2.0, "in")
        anim(ic, "scale", fr(sid, 24.0), fr(sid, 24.45), (.8,) * 3, (.001,) * 3, "in")
        ics.append(ic)
    mg = V.icon("mg", "marketing", .9, (3.6, -2.8, .2), em=3.0)
    pop_in(mg, fr(sid, 27.3), .9)
    top = sum(h + .06 for _, _, h in tw)
    camera(sid, [(20.65, (0, -2.6, 1.2), -96, 10, 13), (23.2, (0, -1.6, 1.6), -100, 12, 15.5),
                 (25.4, (0, 0, 3.6), -106, 13, 19), (28.85, (0, 0, 5.2), -112, 14, 23)], lens=26)
    A["P1"] = (tw[0][0], (2.0, 0, tw[0][2] * .5))
    A["P2"] = (tw[1][0], (2.0, 0, tw[1][2] * .5))
    A["P3"] = (tw[2][0], (2.0, 0, tw[2][2] * .5))
    A["TOP"] = ((0, 0, top + .8))


def b07(n, A):
    """Pos terbesarnya justru cukai & pajak rokok ±42 jt: balok emas raksasa jatuh di puncak menara."""
    sid = "B07"
    neon(grid="vp_grid", em=1.7, rig_c=(0, 0, 8), rig_s=2.4, fade=(16, 60))
    V.base_plate("bp", 5.2, 5.2, "n_cyan", (0, 0, 0), 3.0)
    tw = modal_tower("mt", (0, 0, .14), upto=4)
    p4, z4, h4 = tw[3]
    hi = (0, 0, .14 + z4 + 14)
    lo = (0, 0, .14 + z4)
    key(p4, "location", 1, hi)
    hide_until(p4, fr(sid, 30.2))
    anim(p4, "location", fr(sid, 30.2), fr(sid, 31.85), hi, lo, "in")
    camera(sid, [(28.85, (0, 0, 6.0), -112, 12, 26), (31.0, (0, 0, 9.0), -100, 10, 33),
                 (33.30, (0, 0, 10.0), -92, 12, 36)], lens=24)
    A["P4"] = (p4, (2.0, 0, h4 * .5))
    A["P1"] = (tw[0][0], (2.0, 0, tw[0][2] * .5))


def b08(n, A):
    """Dibayar di depan, sebelum satu botol pun laku: uang masuk KAS NEGARA, kardus Raka masih utuh."""
    sid = "B08"
    city(n, focus=None, center_clear=48)
    gv = V.gov_day("gov", (6, 12, Z0))
    r = raka("raka", (-6.5, -6.0, Z0), .35, "stand")
    pose_at(r, "stand", fr(sid, 34.3))
    pose_at(r, "shrug", fr(sid, 35.0))
    mb = W.MB("cts")
    M.carton_stack(mb, 0, 0, 0, 3, 2, 3, 1.2, .9, .7, kind="liq")
    ct = mb.build((-10.5, -5.0, Z0))
    mn, h = money_tower("mn", 14, (0, 0, 0), 1.15)
    p0, p1 = (-2.0, -7.0, Z0), (5.5, 4.5, Z0 + .5)
    key(mn, "location", 1, p0)
    arc_move(mn, fr(sid, 33.6), fr(sid, 35.2), p0, p1, 5.0)
    anim(mn, "scale", fr(sid, 35.0), fr(sid, 35.45), (1, 1, 1), (.001,) * 3, "in")
    x = V.xmark("x", (-10.5, -6.4, 4.6), .9)
    pop_in(x, fr(sid, 35.6), .9)
    camera(sid, [(33.30, (-3, -2, 3.2), -110, 18, 36), (36.15, (-1, 1, 4.0), -98, 18, 40)], lens=24)
    A["MONEY"] = (mn, (0, 0, h + .4))
    A["CARTON"] = (ct, (0, 0, 2.6))
    A["GOV"] = (gv["sign"], (0, 0, 1.6))


def b09(n, A):
    """Total modal sekitar Rp90 juta: menara utuh, kamera mengitari dari bawah ke atas."""
    sid = "B09"
    neon(grid="vp_grid2", em=1.6, rig_c=(0, 0, 8), rig_s=2.4, fade=(16, 60))
    V.base_plate("bp", 5.2, 5.2, "n_gold", (0, 0, 0), 3.0)
    tw = modal_tower("mt", (0, 0, .14), upto=4, em=1.7)
    top = tower_total()
    rg = V.ring_obj("rg", (0, 0, .2), 3.4, .12, "n_gold", 6.0)
    anim(rg, "location", fr(sid, 37.2), fr(sid, 38.9), (0, 0, .2), (0, 0, top + .2), "inout")
    cr = V.crown("cr", (0, 0, top + .9), .9, "n_gold")
    pop_in(cr, fr(sid, 39.0), .9)
    camera(sid, [(36.15, (0, 0, 3.0), -130, 6, 22), (38.3, (0, 0, 8.0), -100, 10, 32),
                 (40.50, (0, 0, 10.0), -72, 16, 36)], lens=24)
    A["TOP"] = (cr, (0, 0, 2.2))


# ================================================================== KAIL 1
def b10(n, A):
    """Kalau 1.000 botol habis, Raka untung berapa? Van brand mengantar ke toko vape; Raka berpikir."""
    sid = "B10"
    info = city(n, focus=None, center_clear=22)
    V.vape_store_day("ts", (0, 5, Z0), sign="TOKO VAPE")
    vn = V.box_van("van", (0, 0, 0), 0)
    p0, p1 = (-26, -11, Z0), (-5.5, -10.5, Z0)
    key(vn, "location", 1, p0)
    anim(vn, "location", 1, fr(sid, 42.6), p0, p1, "out")
    r = raka("raka", (3.2, -6.0, Z0), -.4, "stand")
    pose_at(r, "stand", fr(sid, 42.1))
    pose_at(r, "think", fr(sid, 42.7))
    q = V.qmark("q", (3.2, -6.2, 4.4), .7, "n_gold", 6)
    pop_in(q, fr(sid, 42.9), 1.0)
    camera(sid, [(40.50, (0, -3, 1), -100, 34, 70), (42.2, (1, -5, 2.4), -96, 18, 26),
                 (43.65, (2.2, -5.8, 2.6), -92, 12, 17)], lens=24)
    A["STORE"] = ((0, 4.8, 8.4))
    A["RAKA"] = (r["body"], (0, 0, 2.7))


# ================================================================== KEJUTAN 2
def b11(n, A):
    """Brand jual ke toko sekitar Rp90 ribu per botol: botol di depan toko + papan harga neon."""
    sid = "B11"
    city(n, focus=None, center_clear=22)
    V.vape_store_day("ts", (0, 5, Z0), sign="TOKO VAPE")
    V.disc_ped("pd", 1.8, "n_purple", (0, -5.5, Z0), em=3.0)
    b = V.bottle("hb", .95, (("lq_brand", 1),), label=True, pita=True, loc=(0, -5.5, Z0 + .5))
    SV.spin(b["root"], 1, n + TAIL, 70)
    t, fo = V.neon_sign("tag", "Rp90.000", (0, -5.5, 6.6), .9, "n_gold", 7.0)
    for ob in (t, fo):
        pop_in(ob, fr(sid, 45.9), 1.0)
    r = raka("raka", (-3.6, -6.5, Z0), .45, "arms_fwd")
    ow = L.character("owner", "owner", (3.6, -6.5, Z0), -.45)
    L.pose(ow, "wave")
    mb = W.MB("box1")
    M.carton(mb, 0, 0, 0, 1.0, .8, .6, "liq")
    bx = mb.build((-2.6, -6.8, Z0 + 1.3))
    arc_move(bx, fr(sid, 44.2), fr(sid, 45.2), (-2.6, -6.8, Z0 + 1.3), (2.5, -6.8, Z0 + 1.3), 1.2)
    camera(sid, [(43.65, (0, -5.5, 2.4), -112, 10, 16), (46.0, (0, -5.5, 3.2), -94, 10, 16),
                 (48.10, (0, -5.5, 3.6), -80, 12, 18)], lens=24)
    A["BRAND"] = (r["body"], (0, 0, 2.7))
    A["TOKO"] = (ow["body"], (0, 0, 2.7))
    A["TAG"] = (t, (0, 0, 1.0))


def b12(n, A):
    """1.000 botol x Rp90 ribu = Rp90 juta: barisan botol berubah jadi menara uang."""
    sid = "B12"
    neon(grid="vp_grid", em=1.8, rig_c=(0, 0, 1), rig_s=1.8, fade=(14, 50))
    nx, ny, sx, sy = 40, 25, .5, .6
    rows = []
    cols = ["lq_brand", "lq_pink", "lq_toko", "lq_amber"]
    for j in range(ny):
        mb = W.MB(f"row{j}")
        for i in range(nx):
            V.bottle_mb(mb, (i - (nx - 1) / 2) * sx, 0, 0, .16, cols[(i + j) % 4])
        y = (ny - 1) / 2 * sy - j * sy
        ob = mb.build((0, y, 0))
        V.glow(ob, {c: 1.4 for c in cols})
        f0 = fr(sid, 48.25 + .9 * j / (ny - 1))
        key(ob, "location", 1, (0, y, 3.0))
        hide_until(ob, f0)
        anim(ob, "location", f0, f0 + 8, (0, y, 3.0), (0, y, 0), "out")
        g = fr(sid, 49.45 + .35 * j / ny)
        anim(ob, "scale", g, g + 9, (1, 1, 1), (.001,) * 3, "in")
        rows.append(ob)
    tower, th = money_tower("tw", 30, (0, 0, 0), 1.0)
    grow(tower, fr(sid, 49.6), fr(sid, 50.6))
    camera(sid, [(48.10, (0, 0, 0), -92, 62, 26), (49.4, (0, -1, .6), -98, 40, 22),
                 (50.80, (0, 0, th * .45), -106, 16, 17)], lens=24)
    A["GRID"] = ((0, (ny - 1) / 2 * sy + .4, .4))
    A["TOWER"] = (tower, (0, 0, th + .3))


def b13(n, A):
    """Pas. Cuma balik modal: timbangan seimbang — MODAL Rp90 jt vs PENJUALAN Rp90 jt."""
    sid = "B13"
    neon(grid="vp_grid2", em=1.5, rig_c=(0, 0, 3), rig_s=1.3)
    bl = N.balance("bal", (0, 0, 0), 1.0, "n_gold")
    pl, pr = bl["pans"]
    mg = W.MB("modal")
    zz = 0
    for nm, jt, k in COSTS:
        h = jt * .028
        mg.box(-.75, -.75, zz, .75, .75, zz + h, k)
        zz += h + .02
    mo = mg.build()
    V.glow(mo, {k: 2.0 for _, _, k in COSTS})
    mo.parent = pl
    mo.location = (0, 0, -2.18)
    mr, hr = money_tower("mr", 9, (0, 0, 0), .55)
    mr.parent = pr
    mr.location = (0, 0, -2.18)
    f_a = fr(sid, 50.95)
    for f in range(1, n + TAIL + 1):
        u = (f - 1) / FPS
        deg = 9.0 * math.exp(-2.6 * u) * math.cos(6.5 * u)
        N.balance_key(bl, f, deg)
    camera(sid, [(50.80, (0, 0, 3.4), -104, 12, 21), (52.65, (0, 0, 3.4), -92, 12, 19.5)], lens=26)
    A["MODAL"] = (pl, (0, 0, -.2))
    A["JUAL"] = (pr, (0, 0, -.2))


def b14(n, A):
    """Untung baru mulai di batch kedua: ±Rp23 ribu per botol (lapisan hijau di puncak botol)."""
    sid = "B14"
    neon(grid="vp_grid", em=1.7, rig_c=(0, 0, 2), rig_s=1.3)
    V.disc_ped("ped", 2.4, "n_green", (0, 0, 0), em=3.0)
    b = V.bottle("hb", 1.25, (("lq_brand", 25), ("lq_negara", 42), ("lq_cheap", 23)), label=False, pita=True,
                 liquid_em=1.2, loc=(0, 0, .5))
    b["root"].rotation_euler.z = math.radians(-12)
    g = lp.mat("lq_cheap")
    emit_keys = K.emit_keys
    emit_keys(g, [(1, 1.2), (fr(sid, 54.1), 1.2), (fr(sid, 54.5), 6.0), (fr(sid, 55.0), 3.2), (n + TAIL, 3.6)])
    t, fo = V.neon_sign("b2", "BATCH 2", (0, 2.4, 8.0), .75, "n_cyan", 7.0)
    for ob in (t, fo):
        pop_in(ob, fr(sid, 53.4), 1.0)
    camera(sid, [(52.65, (0, 0, 3.8), -110, 10, 17), (55.90, (0, 0, 4.2), -88, 10, 16)], lens=26)
    A["PROFIT"] = (b["root"], (1.6, 0, 5.0))
    A["COST"] = (b["root"], (1.6, 0, 2.2))


def b15(n, A):
    """Yang menentukan untung bukan rasanya, tapi REPEAT ORDER: van bolak-balik + panah putar di atas toko."""
    sid = "B15"
    city(n, focus=None, center_clear=22)
    V.vape_store_day("ts", (0, 5, Z0), sign="TOKO VAPE")
    la = B.loop_arrow("loop", (0, 3.0, 12.0), 2.6, "n_cyan", 6.0)
    pop_in(la, fr(sid, 58.15), 1.0)
    for f in range(fr(sid, 58.15), n + TAIL + 1):
        key(la, "rotation_euler", f, (0, -.07 * (f - fr(sid, 58.15)), 0))
    t, fo = V.neon_sign("ro", "REPEAT ORDER", (0, 2.9, 9.0), .8, "n_cyan", 7.0)
    for ob in (t, fo):
        pop_in(ob, fr(sid, 58.3), 1.0)
    ic = V.icon("flask", "bahan", .8, (-4.5, -6.5, Z0), em=3.0)
    x = V.xmark("x", (-4.5, -7.4, 1.4), .8)
    pop_in(x, fr(sid, 57.45), .8)
    r = raka("raka", (-2.2, -6.0, Z0), .2, "stand")
    vans = []
    for k in range(2):
        vn = V.box_van(f"van{k}", (0, 0, 0), 0)
        x0 = -30 - k * 16
        for f in range(1, n + TAIL + 1):
            xx = x0 + 11.0 * (f - 1) / FPS
            key(vn, "location", f, (xx, -24.0, .02))
        vans.append(vn)
    camera(sid, [(55.90, (-2, -5, 2.6), -100, 12, 18), (57.6, (0, -2, 5.0), -96, 14, 26),
                 (59.25, (0, 0, 7.0), -92, 14, 32)], lens=24)
    A["FLASK"] = (ic, (0, 0, 2.2))
    A["LOOP"] = (la, (0, 0, 3.2))


def b16(n, A):
    """Mulai dari sedikit toko, stok harus cepat habis, baru tambah toko baru."""
    sid = "B16"
    city(n, focus=None, center_clear=48)
    xs = (-15.0, 0.0, 15.0)
    gauges = []
    for k, x in enumerate(xs):
        st = V.vape_store_day(f"ts{k}", (x, 5, Z0), 12.0, 10.0, ("vs_pink", "vs_purple", "vs_awn")[k],
                              "TOKO VAPE", seed=3 + k)
        g = B.stock_gauge(f"g{k}", (x + 4.2, -1.5, Z0), 4.0, .9, "n_green")
        gauges.append(g)
        if k == 2:
            for ob in [st["body"], st["shelf"], st["glass"], st["sign"], g["frame"], g["fill"]]:
                grow(ob, fr(sid, 62.55), fr(sid, 63.3), 1.0, "back") if ob is not st["sign"] else \
                    pop_in(ob, fr(sid, 62.9), 1.0)
        else:
            fl = g["fill"]
            key(fl, "scale", 1, (1, 1, 1))
            anim(fl, "scale", fr(sid, 61.3), fr(sid, 62.2), (1, 1, 1), (1, 1, .08), "inout")
            anim(fl, "scale", fr(sid, 62.35), fr(sid, 62.9), (1, 1, .08), (1, 1, 1), "out")
    camera(sid, [(59.25, (-4, 0, 3.0), -100, 24, 54), (61.5, (0, 0, 3.0), -96, 24, 60),
                 (63.60, (3, 0, 3.0), -90, 24, 62)], lens=24)
    A["G0"] = (gauges[0]["frame"], (0, 0, 4.6))
    A["G1"] = (gauges[1]["frame"], (0, 0, 4.6))
    A["NEW"] = ((15, 4.8, 8.6))


def b17(n, A):
    """Brand yang menang bukan yang paling ramai di awal (kilat lalu redup), tapi yang paling sering dipesan ulang
    (tangga order naik terus + mahkota)."""
    sid = "B17"
    neon(grid="vp_grid", em=1.7, rig_c=(0, 0, 3), rig_s=1.8, fade=(14, 50))
    V.base_plate("bpL", 4.0, 4.0, "n_pink", (-4.5, 0, 0), 3.0)
    V.base_plate("bpR", 9.0, 4.0, "n_cyan", (5.5, 0, 0), 3.0)
    sp = V.pillar("spike", 8.0, 2.4, 2.4, "n_pink", 1.6, 5.0, (-4.5, 0, .14))
    key(sp, "scale", 1, (1, 1, .001))
    anim(sp, "scale", fr(sid, 64.9), fr(sid, 65.6), (1, 1, .001), (1, 1, 1), "out")
    anim(sp, "scale", fr(sid, 65.9), fr(sid, 66.9), (1, 1, 1), (1, 1, .12), "inout")
    hide_until(sp, fr(sid, 64.9))
    steps = []
    for k in range(6):
        h = 1.2 + k * 1.15
        p = V.pillar(f"st{k}", h, 1.2, 2.4, "n_cyan", 1.6, 5.0, (2.0 + k * 1.4, 0, .14))
        grow(p, fr(sid, 66.75 + k * .2), fr(sid, 66.75 + k * .2) + 9, 1.0)
        steps.append((p, h))
    cr = V.crown("cr", (2.0 + 5 * 1.4, 0, .14 + steps[-1][1] + .5), .7, "n_gold")
    pop_in(cr, fr(sid, 68.05), .7)
    camera(sid, [(63.60, (-.5, 0, 3.4), -104, 12, 24), (66.0, (0, 0, 3.8), -98, 12, 25),
                 (68.75, (1.5, 0, 4.4), -92, 12, 26)], lens=24)
    A["SPIKE"] = ((-4.5, 0, 8.6))
    A["STEPS"] = ((5.5, 0, 8.9))


# ================================================================== KAIL 3 / CTA
def b18(n, A):
    """Modal 90 jt: bikin BRAND atau buka TOKO vape? Kiri brand Raka, kanan toko vape, Raka + uang di tengah."""
    sid = "B18"
    city(n, focus=None, center_clear=48)
    B.brand_store("bs", (-14, 5, Z0), "RAKA LIQUID")
    V.vape_store_day("ts", (14, 5, Z0), sign="TOKO VAPE")
    r = raka("raka", (-1.0, -6.0, Z0), 0, "stand")
    pose_at(r, "stand", fr(sid, 70.8))
    pose_at(r, "shrug", fr(sid, 71.4))
    mn, h = money_tower("mn", 12, (1.4, -6.4, Z0), .7)
    for nm, body, x, k, t in (("sgB", "BRAND", -10, "n_purple", 71.6), ("sgT", "TOKO", 10, "n_cyan", 72.3)):
        tt, fo = V.neon_sign(nm, body, (x, 1.5, 11.0), 1.6, k, 7.0)
        for ob in (tt, fo):
            pop_in(ob, fr(sid, t), 1.0)
    camera(sid, [(68.75, (0, -5.6, 2.2), -96, 10, 12), (70.6, (0, -4, 3.0), -94, 14, 22),
                 (72.4, (0, -2, 5.0), -92, 20, 50), (75.85, (0, -2, 5.4), -90, 22, 56)], lens=24)
    A["RAKA"] = (r["body"], (0, 0, 2.7))
    A["MONEY"] = (mn, (0, 0, h + .4))


def b19(n, A):
    """Simpan & kirim ke temen yang pengin punya brand sendiri; ini simulasi, khusus 18+. Kamera mundur."""
    sid = "B19"
    city(n, focus=None, center_clear=48)
    B.brand_store("bs", (-14, 5, Z0), "RAKA LIQUID")
    V.vape_store_day("ts", (14, 5, Z0), sign="TOKO VAPE")
    r = raka("raka", (-3.0, -6.0, Z0), .3, None, hold="phone")
    pose_at(r, "point", 1)
    fd = L.character("teman", "cowok", (5.0, -6.5, Z0), -.5)
    L.pose(fd, "stand", 1)
    L.pose(fd, "stand", fr(sid, 78.6))
    L.pose(fd, "wave", fr(sid, 79.0))
    pl = V.paper_plane("pl", (0, 0, 0), .6)
    p0, p1 = (-2.6, -6.4, 2.6), (4.6, -6.6, 2.8)
    key(pl, "location", 1, p0)
    pl.rotation_euler = (0, 0, -math.pi / 2)
    pop_in(pl, fr(sid, 77.1), .6)
    arc_move(pl, fr(sid, 77.3), fr(sid, 78.6), p0, p1, 2.2)
    pop_out(pl, fr(sid, 78.7))
    camera(sid, [(75.85, (1, -6, 2.4), -96, 12, 16), (78.6, (1, -5, 2.4), -94, 16, 26),
                 (80.2, (0, -4, 1.4), -100, 26, 80), (82.2, (0, -4, 0), -106, 32, 150)], lens=24)
    A["RAKA"] = (r["body"], (0, 0, 2.7))
    A["TEMAN"] = (fd["body"], (0, 0, 2.7))


SCENES = {f"B{i:02d}": globals()[f"b{i:02d}"] for i in range(1, 20)}
K.SCENES = SCENES

if __name__ == "__main__":
    K.main()
