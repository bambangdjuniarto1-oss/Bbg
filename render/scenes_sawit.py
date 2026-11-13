"""20 adegan video "Bedah Bisnis Kebun Sawit" (timeline mengikuti VO hasil humanize_vo.py, ±97 dtk).

  python3 render/scenes_sawit.py -- --scene K01 --out OUT/K01 [--res 720x1280] [--samples 4] [--frames a-b]

Isi VO: hook (lahan dibakar demi uang?) -> berapa uang 1 hektare, panen tiap 10 hari, modalnya? ->
modal buka kebun Rp55 jt/ha (1/5/10 ha = 55/275/550 jt) -> baru panen 2,5-3 tahun -> 1 ton TBS/ha/10 hari,
Rp3.000/kg, 3x panen = Rp9 jt/ha/bulan (5 ha 45 jt, 10 ha 90 jt) -> 2 pekerja x Rp150rb x 3 = 900rb + pupuk
700rb + perawatan 350rb + angkut 400rb + lain-lain 150rb = Rp2,5 jt -> sisa 6,5 / 32,5 / 65 jt -> hanya
untuk kebun produktif -> CTA. Waktu (detik) di sini = timeline video, sama dengan render/scenes/sawit_words.json.
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
import world_hotel as H  # noqa: E402
import world_laundry as L  # noqa: E402
import world_amdk as M  # noqa: E402
import world_sawit as K  # noqa: E402
from scenes import key, make_camera, cam_keys, orbit  # noqa: E402
from scenes_laundry import pop, grow_z, fly, emission_ramp, _anchor_pos  # noqa: E402
from scenes_amdk import tower, sparkles  # noqa: E402

FPS = 30
TIMELINE = [("K01", 0.00), ("K02", 4.80), ("K03", 9.04), ("K04", 12.89), ("K05", 14.52), ("K06", 20.24),
            ("K07", 24.35), ("K08", 32.66), ("K09", 37.16), ("K10", 43.29), ("K11", 46.61), ("K12", 50.02),
            ("K13", 54.38), ("K14", 61.46), ("K15", 64.85), ("K16", 72.63), ("K17", 77.34), ("K18", 80.56),
            ("K19", 86.40), ("K20", 92.40)]
END_T = 97.05
BURNT = (-58.0, -68.0, -14.0, -26.0)


def scene_range(sid):
    ids = [s for s, _ in TIMELINE]
    i = ids.index(sid)
    t0 = TIMELINE[i][1]
    t1 = TIMELINE[i + 1][1] if i + 1 < len(TIMELINE) else END_T
    f0, f1 = round(t0 * FPS), round(t1 * FPS)
    return t0, t1, f0, f1 - f0


def fr(sid, t):
    """frame lokal adegan untuk detik `t` di timeline video."""
    return max(1, int((t - dict(TIMELINE)[sid]) * FPS) + 1)


# ------------------------------------------------------------------ set bantu
def field(clear=(-14, -12, 14, 8), ext=70, seed=1, ground="kb_grass", stage_ground=None, side_gap=5.0):
    """latar kebun: alas rumput luas + sawit dewasa di belakang & samping area panggung `clear`."""
    x0, y0, x1, y1 = clear
    g = W.MB("fld_g")
    g.box(-ext * 2.5, -ext * 2.5, -1, ext * 2.5, ext * 2.5, -.02, "kb_far")
    g.box(-ext, -ext, -1, ext, ext, 0, ground)
    if stage_ground:
        g.box(x0, y0, -.9, x1, y1, .02, stage_ground)
    g.build()

    def skip(x, y):
        if y < y1 + 1.5 and x0 - side_gap < x < x1 + side_gap:
            return True
        if y < y0 - 2:
            return True
        return False
    K.plantation("fld", -ext, -ext, ext, ext, "dewasa", seed=seed, ground=False, skip=skip,
                 detail=True)


def money_tower(name, layers, loc, key_="money_red", s=.8):
    return tower(name, layers, loc, 2, 2, key_=key_, s=s)


def falling_bunch(name, p0, p1, f0, s=1.0):
    mb = W.MB(name)
    K.tbs(mb, 0, 0, 0, s)
    ob = mb.build(p0)
    key(ob, "location", 1, p0)
    key(ob, "location", f0, p0)
    key(ob, "location", f0 + 9, p1)
    key(ob, "location", f0 + 13, (p1[0], p1[1], p1[2] + .35))
    key(ob, "location", f0 + 17, p1)
    key(ob, "rotation_euler", f0, (0, 0, 0))
    key(ob, "rotation_euler", f0 + 12, (.6, .3, 0))
    return ob


def square_frame(name, x0, y0, x1, y1, z=.3, w=.6, key_="lw_yellow", em=2.0):
    mb = W.MB(name)
    mb.box(x0, y0, z, x1, y0 + w, z + .25, key_)
    mb.box(x0, y1 - w, z, x1, y1, z + .25, key_)
    mb.box(x0, y0, z, x0 + w, y1, z + .25, key_)
    mb.box(x1 - w, y0, z, x1, y1, z + .25, key_)
    ob = mb.build()
    ob.data.materials[0] = lp.mat(key_, emission=em)
    return ob


def tiles(prefix, n, cols, loc, stage="muda", sp=7.6, f=None, stagger=2, seed=0, fruit=True):
    """n petak kecil (mis. 5 hektare) dalam `cols` kolom, mengisi ke belakang (+y)."""
    obs = []
    for k in range(n):
        c, r = k % cols, k // cols
        x = loc[0] + (c - (cols - 1) / 2) * sp
        y = loc[1] + r * sp
        t = K.plot_tile(f"{prefix}{k}", stage, 2, 3.4, seed=seed + k, fruit=fruit)
        t.location = (x, y, 0)
        if f is not None:
            pop(t, f + k * stagger, 1.0)
        obs.append(t)
    return obs


def ok_mark(name, loc, f, s=.9):
    ck = L.checkmark(name, loc, s)
    pop(ck, f, 1.0)
    return ck


def x_mark(name, loc, f, s=.9):
    xm = L.xmark(name, loc, s)
    pop(xm, f, 1.0)
    return xm


# ------------------------------------------------------------------ adegan
def k01(n, info, A):
    """hook: 'Katanya, ada lahan yang harus dibakar demi menghasilkan uang.' — lahan gosong berasap di tepi
    kebun luas."""
    x0, y0, x1, y1 = BURNT
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rnd = random.Random(2)
    pts = [(rnd.uniform(x0 + 4, x1 - 4), rnd.uniform(y0 + 4, y1 - 4), .5) for _ in range(7)]
    K.smoke("sm", pts, n)
    K.road_trucks(n)
    A["BAKAR"] = (cx, cy, 3.0)
    cam, tgt = make_camera(lens=20, shift_y=.12)
    cam_keys(cam, tgt, [(1, (cx - 46, cy - 64, 44), (cx + 4, cy + 4, 2)), (n, (cx - 34, cy - 52, 34), (cx + 6, cy + 8, 3))])


def k02(n, info, A):
    """'Tapi sebenarnya, berapa sih uang dari 1 hektare kebun sawit?' — terbang di atas kebun luas,
    satu petak 1 hektare menyala."""
    K.road_trucks(n)
    sq = square_frame("ha", 8.0, 8.0, 40.0, 40.0, z=.4, w=.8)
    pop(sq, fr("K02", 7.0), 1.0)
    A["HEKTARE"] = (24.0, 8.0, 3.0)
    cam, tgt = make_camera(lens=20, shift_y=.1)
    cam_keys(cam, tgt, [(1, (-70, -110, 90), (10, 0, 0)), (n, (-22, -62, 62), (24, 24, 0))])


def k03(n, info, A):
    """'Bayangkan, tiap 10 hari kamu bisa panen dan dapat uang,' — pemanen memotong tandan dengan egrek,
    tandan jatuh, pengangkut mendorong gerobak."""
    field((-12, -10, 12, 2), seed=3)
    mb = W.MB("hp")
    top = K.palm(mb, 0, 0, 0, 1.25, "dewasa", random.Random(5))
    mb.build()
    w = K.worker("pm", "pemanen", (0.3, -2.6, 0), math.pi, hold="egrek", pole=3.3)
    K.egrek_cut(w, 1, fr("K03", 10.0))
    falling_bunch("fb", (0, -.8, top - 1.0), (.6, -3.6, .05), fr("K03", 10.1), 1.1)
    c = K.worker("ga", "pengangkut", (9, -6.5, 0), 0, hold="gerobak")
    L.walk_to(c, [(9, -6.5), (-9, -6.5)], 1, speed=1.6)
    cal = K.calendar("cal", "10", (-6.5, -3.0, 0), 1.0)
    pop(cal, fr("K03", 10.1), 1.0)
    A["PANEN"] = (0, -.8, top - .6)
    A["HARI"] = (-6.5, -3.0, 2.1)
    cam, tgt = make_camera(lens=22, shift_y=.12)
    cam_keys(cam, tgt, [(1, (6.5, -15, 2.6), (0, -1.5, 3.4)), (n, (4.5, -13.5, 2.4), (-.5, -1.5, 3.3))])


def k04(n, info, A):
    """'tapi modalnya berapa?' — tumpukan uang di atas petak tanah + tanda tanya besar."""
    field((-10, -8, 10, 4), seed=4)
    M.pedestal("pd", 2.2, "kb_soil2").build((0, 0, 0))
    tw = money_tower("tw", 8, (0, 0, .42))
    pop(tw, 1, 1.0)
    q = H.text("q", "?", 3.6, "lw_yellow", depth=.5, loc=(0, -.5, 3.4), emission=.6)
    pop(q, 6, 1.0)
    A["MODAL"] = (0, 0, 3.0)
    cam, tgt = make_camera(lens=24, shift_y=.1)
    tg = (0, 0, 3.0)
    cam_keys(cam, tgt, [(1, orbit(tg, -96, 10, 18), tg), (n, orbit(tg, -84, 14, 16), tg)])


def k05(n, info, A):
    """'membuka lahan, biaya buka lahan, bibit unggul, tanam, jalan kebun dan perawatan sampai siap panen'
    — ekskavator buka lahan, bibit polybag, pekerja menanam, jalan kebun dibuat, pemupukan."""
    field((-16, -12, 16, 12), seed=5, stage_ground="kb_soil")
    ex = K.excavator("ex")
    ex["root"].location = (-10, 8, 0)
    ex["root"].rotation_euler.z = -.4
    K.dig(ex, 1, n)
    mb = W.MB("dirt")
    mb.cyl(-6.2, 6.5, 0, .8, 2.0, "kb_soil_dk", n=8, r_top=.6)
    mb.build()
    # bibit unggul (pembibitan polybag)
    nur = W.MB("nur")
    for i in range(5):
        for j in range(3):
            K.palm(nur, 7 + i * 1.1, 6 + j * 1.1, 0, .9, "bibit", random.Random(i * 3 + j))
    nob = nur.build()
    pop(nob, fr("K05", 16.68), 1.0)
    # tanam: lubang + bibit muncul berurutan
    f_t = fr("K05", 17.46)
    for k in range(6):
        x = -8 + k * 3.2
        h = W.MB(f"hole{k}")
        h.cyl(x, 0, 0, .04, .7, "kb_soil_dk", n=8)
        h.build()
        p = K.palm_obj(f"sd{k}", "bibit", 1.0, seed=k, circle=False).build((x, 0, 0))
        pop(p, f_t + k * 4, 1.0)
    pt = K.worker("pt", "penanam", (-9.5, -2.0, 0), 0, hold="bibit")
    L.walk_to(pt, [(-9.5, -2.0), (9.5, -2.0)], 1, speed=1.7)
    # jalan kebun (tumbuh dari kiri)
    rd = W.MB("road")
    rd.box(-16, -9, 0, 16, -5.6, .08, "road_dirt")
    rd.box(-16, -8.0, .08, 16, -7.7, .1, "road_dirt2")
    rd.box(-16, -6.9, .08, 16, -6.6, .1, "road_dirt2")
    ro = rd.build()
    f_r = fr("K05", 17.98)
    key(ro, "scale", 1, (.001, 1, 1))
    key(ro, "scale", f_r, (.001, 1, 1))
    key(ro, "scale", f_r + 18, (1, 1, 1))
    gb = K.worker("gb", "pengangkut2", (14, -7.3, 0), -math.pi / 2, hold="gerobak", load="pupuk")
    L.walk_to(gb, [(14, -7.3), (-2, -7.3)], fr("K05", 18.5), speed=1.8)
    sk = K.sack_pile("sk").build((11, -1.5, 0))
    pop(sk, fr("K05", 18.56), 1.0)
    A["LAHAN"] = (-10, 8, 4.0)
    A["BIBIT"] = (9.2, 7.1, 1.6)
    A["TANAM"] = (0, 0, 1.6)
    cam, tgt = make_camera(lens=20, shift_y=.24)
    tg = (0, 1.0, 1.5)
    cam_keys(cam, tgt, [(1, orbit(tg, -100, 28, 33), tg), (n, orbit(tg, -86, 31, 30), tg)])


def k06(n, info, A):
    """'sekitar 55 juta rupiah per hektare di luar harga tanah.' — petak 1 HA (sawit muda) + menara uang."""
    field((-14, -10, 14, 8), seed=6)
    pt = K.plot_tile("pt", "muda", 3, 4.4, seed=2, sign="1 HA")
    pt.location = (-4.5, 0, 0)
    pop(pt, 1, 1.0)
    M.pedestal("pd", 2.0, "kb_soil2").build((6.0, -.5, 0))
    tw = money_tower("tw", 11, (6.0, -.5, .42))
    f0 = fr("K06", 20.64)
    grow_z(tw, f0, f0 + 22)
    A["MODAL"] = (6.0, -.5, .42 + 11 * .29 * .8 + .4)
    A["TANAH"] = (-4.5, -3.0, .8)
    cam, tgt = make_camera(lens=22, shift_y=.1)
    tg = (-1.5, 0, 2.2)
    cam.data.lens = 20
    cam_keys(cam, tgt, [(1, orbit(tg, -96, 16, 30), tg), (n, orbit(tg, -88, 19, 28), tg)])


GRP = {1: (-17.0, 1, 1), 5: (-1.0, 5, 2), 10: (17.0, 10, 2)}


def _groups(sid, times, layers, key_="money_red", stage="muda", fruit=True):
    """kelompok 1 / 5 / 10 petak + menara uang di kanan masing-masing."""
    out = {}
    for (h, t), lay in zip(times.items(), layers):
        gx, cnt, cols = GRP[h]
        f = fr(sid, t) if t is not None else None
        tiles(f"g{h}_", cnt, cols, (gx - (1.8 if cols > 1 else 0), -4.0), stage, 7.6, f, 2, seed=h, fruit=fruit)
        tx = gx + (6.0 if cols > 1 else 5.0)
        tw = money_tower(f"tw{h}", lay, (tx, -4.6, 0), key_, .7)
        if f is not None:
            grow_z(tw, f + 4, f + 22)
        out[h] = (tx, -4.6, lay * .29 * .7 + .4)
    return out


def _pan(sid, cam, tgt, n, t5, t10, end_wide=True):
    """kamera menyorot kelompok 1 -> 5 -> 10 petak bergantian."""
    g1, g5, g10 = GRP[1][0], GRP[5][0] + 1.5, GRP[10][0] + 1.5
    keys = [(1, (g1 - 2, -26, 11), (g1 + 1.5, 2, 2.2)),
            (max(2, fr(sid, t5) - 6), (g1 - 2, -25, 11), (g1 + 1.5, 2, 2.2)),
            (fr(sid, t5) + 8, (g5 - 2, -30, 14), (g5, 4, 2.4)),
            (max(fr(sid, t5) + 9, fr(sid, t10) - 6), (g5 - 1, -30, 14), (g5, 4, 2.4)),
            (fr(sid, t10) + 8, (g10 - 1, -36, 18), (g10, 8, 2.6))]
    if end_wide:
        keys.append((n, (g10 - 4, -40, 20), (g10 - 2, 8, 2.6)))
    else:
        keys.append((n, (g10 - 1, -37, 18), (g10, 8, 2.6)))
    cam_keys(cam, tgt, sorted(keys, key=lambda k: k[0]))


def k07(n, info, A):
    """'Jadi 1 hektare 55 juta. 5 hektare 275 juta, 10 hektare sekitar 550 juta.'"""
    field((-26, -12, 28, 36), seed=7)
    tops = _groups("K07", {1: 24.6, 5: 26.75, 10: 29.1}, (2, 10, 20))
    for h, p in tops.items():
        A[f"G{h}"] = p
    cam, tgt = make_camera(lens=22, shift_y=.1)
    _pan("K07", cam, tgt, n, 26.75, 29.1)


def k08(n, info, A):
    """'Tapi ingat, sawit baru menghasilkan sekitar 2,5 sampai 3 tahun.' — bibit tumbuh jadi pohon berbuah
    di sepanjang garis waktu (diagonal ke belakang)."""
    field((-13, -10, 13, 13), seed=8)
    P = [(-6.5, -5.0), (-2.2, -.4), (2.2, 4.2), (6.5, 8.8)]
    mb = W.MB("tl")
    (x0, y0), (x1, y1) = P[0], P[-1]
    dx, dy = x1 - x0, y1 - y0
    ln = math.hypot(dx, dy)
    px, py = -dy / ln * .45, dx / ln * .45
    ex, ey = dx / ln * 2.0, dy / ln * 2.0
    mb.poly([(x0 - ex + px, y0 - ey + py, .02), (x1 + ex + px, y1 + ey + py, .02), (x1 + ex - px, y1 + ey - py, .02),
             (x0 - ex - px, y0 - ey - py, .02), (x0 - ex + px, y0 - ey + py, .12), (x1 + ex + px, y1 + ey + py, .12),
             (x1 + ex - px, y1 + ey - py, .12), (x0 - ex - px, y0 - ey - py, .12)],
            [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], "lw_yellow")
    for (x, y) in P:
        mb.cyl(x, y, 0, .2, .75, "lw_navy", n=10)
    mb.build()
    tl_t = (33.5, 34.2, 34.9, 35.6)
    for k, st in enumerate(("bibit", "muda", "remaja", "dewasa")):
        x, y = P[k]
        p = K.palm_obj(f"st{k}", st, 1.0 if k < 3 else .95, seed=k).build((x, y, .2))
        pop(p, fr("K08", tl_t[k]), 1.0)
        c = K.calendar(f"cal{k}", ("0", "1", "2", "3")[k], (x - 2.6, y - 1.2, 0), .6)
        pop(c, fr("K08", tl_t[k]) + 3, 1.0)
    A["BIBIT"] = (P[0][0], P[0][1], 1.4)
    A["PANEN"] = (P[3][0], P[3][1], 6.6)
    cam, tgt = make_camera(lens=20, shift_y=.1)
    tg = (0, 1.8, 2.4)
    cam_keys(cam, tgt, [(1, orbit(tg, -104, 15, 27), tg), (n, orbit(tg, -96, 18, 25), tg)])


def k09(n, info, A):
    """'Asumsikan kebun sudah produktif, 1 ton tandan buah segar per hektare tiap 10 hari.' — TBS dikumpulkan
    di TPH, tumpukan bertambah."""
    field((-14, -12, 14, 4), seed=9)
    b, pile = K.tph("tph", 3, 4)
    b.location = (0, -1.0, 0)
    f0 = fr("K09", 39.6)
    grow_z(pile, f0, f0 + 60)
    for k, (kind, y0, d) in enumerate((("pengangkut", -6.0, 1), ("pengangkut2", -8.0, 40))):
        c = K.worker(f"ga{k}", kind, (12, y0, 0), 0, hold="gerobak")
        L.walk_to(c, [(13, y0), (3.4, y0 + 1.5), (3.0, -3.6)], d, speed=1.7)
    mb = W.MB("hp")
    K.palm(mb, -9, 1.5, 0, 1.15, "dewasa", random.Random(2))
    mb.build()
    w = K.worker("pm", "pemanen2", (-8.7, -1.1, 0), math.pi, hold="egrek", pole=3.0)
    K.egrek_cut(w, 1, n)
    cal = K.calendar("cal", "10", (6.0, 2.0, 0), .9)
    pop(cal, fr("K09", 41.9), 1.0)
    A["TON"] = (0, -1.0, 2.4)
    A["HARI"] = (6.0, 2.0, 1.9)
    cam, tgt = make_camera(lens=22, shift_y=.12)
    tg = (-1.0, -1.5, 2.0)
    cam_keys(cam, tgt, [(1, orbit(tg, -102, 14, 21), tg), (n, orbit(tg, -92, 17, 19), tg)])


def k10(n, info, A):
    """'Harga 3.000 rupiah per kilo, 3 kali panen sebulan,' — truk TBS + label harga, 3 kalender panen."""
    field((-16, -12, 16, 6), seed=10)
    rd = W.MB("road")
    rd.box(-70, -1.5, 0, 70, 4.5, .08, "road_dirt")
    rd.build()
    tr = K.truk_tbs("tk", True)
    key(tr["root"], "location", 1, (-14, 1.6, .08))
    key(tr["root"], "location", fr("K10", 44.6), (-1.5, 1.6, .08))
    tg_ = L.price_tag("tag", "Rp3.000/kg", (-2.5, .2, 5.6), .6)
    pop(tg_, fr("K10", 43.6), 1.0)
    for k, (txt, t) in enumerate((("10", 45.27), ("20", 45.5), ("30", 45.73))):
        c = K.calendar(f"cal{k}", txt, (-4.0 + k * 4.0, -5.0, 0), .9)
        pop(c, fr("K10", t), 1.0)
    A["HARGA"] = (-2.5, .2, 6.2)
    A["PANEN3"] = (0, -5.0, 1.9)
    cam, tgt = make_camera(lens=22, shift_y=.12)
    tg = (0, -1.5, 2.6)
    cam_keys(cam, tgt, [(1, orbit(tg, -100, 12, 24), tg), (n, orbit(tg, -90, 15, 22), tg)])


def k11(n, info, A):
    """'jadi 1 hektare omzetnya 9 juta rupiah per bulan.' — petak 1 HA berbuah + menara uang 9 juta."""
    field((-14, -10, 14, 8), seed=11)
    pt = K.plot_tile("pt", "dewasa", 3, 4.4, seed=5, sign="1 HA")
    pt.location = (-4.5, 0, 0)
    M.pedestal("pd", 2.0, "kb_soil2").build((6.0, -.5, 0))
    tw = money_tower("tw", 9, (6.0, -.5, .42))
    f0 = fr("K11", 47.4)
    grow_z(tw, f0, f0 + 24)
    sparkles("sp", (6.0, -.5, 3.0), f0 + 26, 3, 1.4, .3)
    A["OMZET"] = (6.0, -.5, .42 + 9 * .29 * .8 + .4)
    cam, tgt = make_camera(lens=22, shift_y=.1)
    tg = (-1.5, 0, 2.6)
    cam.data.lens = 20
    cam_keys(cam, tgt, [(1, orbit(tg, -96, 15, 30), tg), (n, orbit(tg, -88, 18, 28), tg)])


def k12(n, info, A):
    """'5 hektare 45 juta. 10 hektare 90 juta.' — 1 / 5 / 10 petak berbuah + menara uang."""
    field((-26, -12, 28, 36), seed=12)
    tops = _groups("K12", {1: None, 5: 50.1, 10: 52.2}, (2, 9, 18), stage="dewasa")
    for h, p in tops.items():
        A[f"G{h}"] = p
    cam, tgt = make_camera(lens=22, shift_y=.1)
    _pan("K12", cam, tgt, n, 49.6, 52.2)


def k13(n, info, A):
    """'Tapi kebun nggak jalan sendiri, tiap hektare butuh 2 pekerja panen, upahnya 150 ribu per orang, tiap
    panen,' — dua pekerja: pemanen ber-egrek & pengangkut gerobak."""
    field((-12, -12, 12, 3), seed=13)
    mb = W.MB("hp")
    top = K.palm(mb, -3.0, 0, 0, 1.2, "dewasa", random.Random(8))
    K.palm(mb, 6.5, 2.0, 0, 1.15, "dewasa", random.Random(9))
    mb.build()
    w = K.worker("pm", "pemanen", (-2.7, -2.5, 0), math.pi, hold="egrek", pole=3.2)
    K.egrek_cut(w, 1, n)
    falling_bunch("fb", (-3.0, -.8, top - 1.0), (-2.3, -3.6, .05), fr("K13", 55.2), 1.05)
    c = K.worker("ga", "pengangkut2", (8, -5.0, 0), 0, hold="gerobak")
    L.walk_to(c, [(9, -5.0), (2.4, -4.4)], 1, speed=1.5)
    A["PEKERJA"] = (-.2, -3.6, 3.0)
    A["UPAH"] = (2.4, -4.4, 2.6)
    cam, tgt = make_camera(lens=22, shift_y=.12)
    tg = (.5, -2.5, 2.4)
    cam_keys(cam, tgt, [(1, orbit(tg, -100, 9, 17), tg), (n, orbit(tg, -88, 11, 15.5), tg)])


def k14(n, info, A):
    """'jadi biaya pekerja sekitar 900 ribu per bulan,' — 2 pekerja + 3 kalender panen + uang upah."""
    field((-12, -10, 12, 6), seed=14)
    for k, (kind, x) in enumerate((("pemanen", -2.0), ("pengangkut", 2.0))):
        w = K.worker(f"w{k}", kind, (x, 1.0, 0), 0)
        L.pose(w, "stand", 1)
        L.pose(w, "wave" if k == 0 else "cheer", fr("K14", 62.2))
    for k in range(3):
        x = -6 + k * 6
        c = K.calendar(f"cal{k}", ("10", "20", "30")[k], (x, 4.0, 0), .8)
        st = L.money_stack(f"ms{k}", 6, 1.3).build((x, -3.0, 0))
        pop(c, 2 + k * 4, 1.0)
        pop(st, fr("K14", 62.3) + k * 5, 1.0)
    A["UPAH"] = (0, -3.0, .9)
    cam, tgt = make_camera(lens=22, shift_y=.1)
    tg = (0, 0, 1.6)
    cam_keys(cam, tgt, [(1, orbit(tg, -94, 12, 20), tg), (n, orbit(tg, -86, 15, 18), tg)])


def k15(n, info, A):
    """'ditambah pupuk 700 ribu, perawatan 350 ribu, angkut hasil panen 400 ribu, dan lain-lain 150 ribu.'
    — pemupukan di piringan, karung pupuk, truk diangkut."""
    field((-18, -12, 18, 6), seed=15)
    mb = W.MB("hp")
    for k, x in enumerate((-8.0, 0.0)):
        K.palm(mb, x, 2.5, 0, 1.0, "dewasa", random.Random(20 + k))
    mb.build()
    sk = K.sack_pile("sk").build((-12.5, -2.0, 0))
    pop(sk, fr("K15", 65.4), 1.0)
    pm = K.worker("pu", "pemupuk", (-11, -3.5, 0), 0, hold="karung")
    L.walk_to(pm, [(-11, -3.5), (-8.0, .2), (-5.5, 2.5)], fr("K15", 65.6), speed=1.4)
    pr = K.worker("pr", "pemanen2", (2.6, -1.0, 0), .6)
    L.pose(pr, "point", fr("K15", 66.8))
    tr = K.truk_tbs("tk", True)
    tr["root"].location = (9.5, -1.5, 0)
    tr["root"].rotation_euler.z = math.pi
    key(tr["root"], "location", 1, (22, -1.5, 0))
    key(tr["root"], "location", fr("K15", 69.3), (9.5, -1.5, 0))
    A["PUPUK"] = (-12.5, -2.0, 1.4)
    A["ANGKUT"] = (9.5, -1.5, 4.6)
    cam, tgt = make_camera(lens=20, shift_y=.24)
    tg = (0, 0, 1.5)
    cam_keys(cam, tgt, [(1, orbit(tg, -98, 20, 34), tg), (n, orbit(tg, -88, 24, 31), tg)])


COSTS = [("PEKERJA", .9, "kb_shirt1"), ("PUPUK", .7, "pupuk_g"), ("PERAWATAN", .35, "kb_shirt4"),
         ("ANGKUT", .4, "truk_cab"), ("LAIN", .15, "c_grey")]


def k16(n, info, A):
    """'Total operasional sekitar 2,5 juta per hektare.' — 5 balok biaya jatuh bertumpuk jadi satu menara."""
    field((-12, -10, 12, 6), seed=16)
    M.pedestal("pd", 2.4, "kb_soil2").build((0, 0, 0))
    z = .42
    f0 = 4
    for k, (nm, v, col) in enumerate(COSTS):
        h = v * 3.2
        mb = W.MB(f"c{k}")
        L.rbox(mb, -1.5, -1.1, 0, 1.5, 1.1, h, col, c=.08)
        ob = mb.build((0, 0, z))
        fly(ob, f0 + k * 7, f0 + k * 7 + 10, (0, 0, z + 9), (0, 0, z))
        pop(ob, f0 + k * 7, 1.0)
        z += h
    sparkles("sp", (0, 0, z), fr("K16", 74.6), 4, 2.0, .35)
    A["TOTAL"] = (0, 0, z + .3)
    cam, tgt = make_camera(lens=24, shift_y=.1)
    tg = (0, 0, 3.6)
    cam_keys(cam, tgt, [(1, orbit(tg, -94, 10, 25), tg), (n, orbit(tg, -86, 14, 23), tg)])


def k17(n, info, A):
    """'Sisanya, 6,5 juta untuk 1 hektare,' — menara omzet 9 jt: bagian biaya 2,5 jt lepas, sisa hijau."""
    field((-12, -10, 12, 6), seed=17)
    lh = .29 * .8
    M.pedestal("pa", 2.2, "kb_soil2").build((-2.0, 0, 0))
    laba = money_tower("laba", 13, (-2.0, 0, .42), "money_g")
    ops = money_tower("ops", 5, (-2.0, 0, .42 + 13 * lh))
    M.pedestal("pb", 1.8, "c_grey").build((5.5, 3.0, 0))
    f0 = fr("K17", 77.6)
    p0 = tuple(ops.location)
    key(ops, "location", 1, p0)
    key(ops, "location", f0, p0)
    key(ops, "location", f0 + 8, (p0[0], p0[1], p0[2] + 1.0))
    key(ops, "location", f0 + 24, (5.5, 3.0, .42))
    f1 = fr("K17", 78.7)
    key(laba, "scale", f1, (1, 1, 1))
    key(laba, "scale", f1 + 5, (1.1, 1.1, 1.1))
    key(laba, "scale", f1 + 9, (1, 1, 1))
    sparkles("sp", (-2.0, 0, 2.2), f1 + 4, 4, 1.6, .3)
    ok_mark("ck", (-2.0, -.6, 13 * lh + 1.4), f1 + 8, .7)
    A["LABA"] = (-2.0, 0, .42 + 13 * lh + .3)
    A["OPS"] = (ops, (0, 0, 5 * lh + .3))
    cam, tgt = make_camera(lens=24, shift_y=.1)
    tg = (1.0, 1.0, 2.4)
    cam_keys(cam, tgt, [(1, orbit(tg, -94, 12, 24), tg), (n, orbit(tg, -86, 14, 22), tg)])


def k18(n, info, A):
    """'32,5 juta untuk 5 hektare, 65 juta untuk 10 hektare, tiap bulan.' — 1/5/10 petak + menara hijau."""
    field((-26, -12, 28, 36), seed=18)
    tops = _groups("K18", {1: None, 5: 80.7, 10: 83.1}, (2, 10, 20), key_="money_g", stage="dewasa")
    for h, p in tops.items():
        A[f"G{h}"] = p
    cam, tgt = make_camera(lens=22, shift_y=.1)
    _pan("K18", cam, tgt, n, 80.2, 83.1)


def k19(n, info, A):
    """'Tapi ingat, angka ini untuk kebun yang sudah produktif, bukan sejak hari pertama tanam.' — kanan:
    kebun berbuah + truk penuh (✓), kiri: bibit baru tanam (✗)."""
    field((-22, -12, 22, 6), seed=19)
    young = K.plot_tile("yg", "bibit", 3, 3.6, seed=4, ground="kb_soil", sign="TANAM")
    young.location = (-9.5, 0, 0)
    old = K.plot_tile("old", "dewasa", 3, 4.4, seed=6, sign="PANEN")
    old.location = (8.5, 2.0, 0)
    tr = K.truk_tbs("tk", True)
    tr["root"].location = (8.0, -9.0, 0)
    ok_mark("ck", (8.5, -1.0, 9.0), fr("K19", 88.7), 1.0)
    x_mark("xm", (-9.5, -1.0, 3.6), fr("K19", 90.1), 1.0)
    A["PRODUKTIF"] = (8.5, 2.0, 7.0)
    A["HARI1"] = (-9.5, 0, 2.0)
    cam, tgt = make_camera(lens=22, shift_y=.12)
    tg = (-.5, -1.5, 2.8)
    cam.data.lens = 18
    cam_keys(cam, tgt, [(1, orbit(tg, -95, 14, 36), tg), (n, orbit(tg, -89, 17, 33), tg)])


def k20(n, info, A):
    """CTA: 'Menurut kamu, bisnis sawit masih menarik, dengan waktu tunggu selama itu?' — diorama kebun luas."""
    K.road_trucks(n)
    cam, tgt = make_camera(ortho=110, shift_y=.12)
    tg = (10, 10, 0)
    cam_keys(cam, tgt, [(1, orbit(tg, -125, 36, 400), tg), (n, orbit(tg, -140, 36, 400), tg)])
    key(cam.data, "ortho_scale", 1, 110)
    key(cam.data, "ortho_scale", n, 190)
    A["KEBUN"] = (24.0, 24.0, 6.0)


SCENES = {f"K{k:02d}": fn for k, fn in enumerate(
    (k01, k02, k03, k04, k05, k06, k07, k08, k09, k10, k11, k12, k13, k14, k15, k16, k17, k18, k19, k20), 1)}
WORLD = {"K01", "K02", "K20"}


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
    W.setup_world_light()
    M.glass_setup()
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, n
    info = {}
    if args.scene in WORLD:
        info = K.build_world(burnt=BURNT if args.scene == "K01" else None, near=80.0 if args.scene != "K20" else 40.0)
        if args.scene == "K01":
            emission_ramp(info["burnt"][1].data.materials[0], [(1, 2.5)])
    A = {}
    SCENES[args.scene](n, info, A)
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
