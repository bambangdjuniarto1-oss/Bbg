"""19 adegan video "Bedah Bisnis: Juru Parkir Minimarket" (timeline mengikuti VO hasil humanize_vo.py, ±61 dtk).

  python3 render/scenes_prk.py -- --scene Q01 --out OUT/Q01 [--res 720x1280] [--samples 4] [--frames a-b]

Isi VO: hook (modal rompi & peluit, sebulan Rp12 jt? lebih cuan dari karyawan minimarket?) -> hitung: 150 motor
+ 20 mobil sehari, tarif Rp2.000 / Rp5.000 -> Rp400 rb sehari = Rp12 jt sebulan -> tapi ada setoran ke
pengelola Rp150 rb/hari = Rp4,5 jt sebulan -> sisa ±Rp7,5 jt, kerja pagi-malam, panas, hujan, tanpa BPJS,
tanpa kepastian -> pelajaran: yang mahal lokasinya, yang kuasai titik ramai kuasai uangnya -> simulasi, tiap
lokasi beda -> siapa paling untung: jukir atau orang di balik layar? -> CTA.
Waktu (detik) = timeline video, sama dengan render/scenes/prk_words.json.
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
import world_ctd as C  # noqa: E402
import world_prk as R  # noqa: E402
from scenes import key, make_camera, cam_keys, orbit  # noqa: E402
from scenes_laundry import pop, grow_z, fly, _anchor_pos  # noqa: E402
from scenes_amdk import sparkles  # noqa: E402

FPS = 30
TIMELINE = [("Q01", 0.00), ("Q02", 1.30), ("Q03", 4.20), ("Q04", 7.60), ("Q05", 9.62), ("Q06", 15.00),
            ("Q07", 17.70), ("Q08", 21.82), ("Q09", 25.20), ("Q10", 31.05), ("Q11", 35.15), ("Q12", 36.70),
            ("Q13", 38.55), ("Q14", 41.30), ("Q15", 45.15), ("Q16", 48.60), ("Q17", 50.25), ("Q18", 53.40),
            ("Q19", 59.00)]
END_T = 60.99
Z0 = .2                       # permukaan lahan parkir
JX, JY = R.JUKIR_POS
LS = .8                       # skala ikat uang (1 lapis = Rp500 rb)
LH = .29 * LS


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


# ------------------------------------------------------------------ bantu
def cam_move(n, tg0, tg1, a0, a1, lens=22, shift=.1):
    """a0/a1 = (az, el, dist)."""
    cam, tgt = make_camera(lens=lens, shift_y=shift)
    cam_keys(cam, tgt, [(1, orbit(tg0, *a0), tg0), (n, orbit(tg1, *a1), tg1)])
    return cam


def ped(name, r, loc, key_="mm_green", f=None):
    p = M.pedestal(name, r, key_).build(loc)
    if f is not None:
        pop(p, f, 1.0)
    return p


def qmark(name, loc, s=1.0, key_="mm_orange", f=None):
    q = H.text(name, "?", 2.6 * s, key_, depth=.4 * s, loc=loc, emission=.8)
    if f is not None:
        pop(q, f, 1.0)
    return q


def wave(parts, f0, f1, period=16, side="R"):
    """lambaian tangan berulang (juru parkir mengatur kendaraan)."""
    ar = parts["arm" + side]
    sg = -1 if side == "R" else 1
    f = f0
    k = 0
    while f <= f1:
        ar.rotation_euler = (0, sg * (2.75 if k % 2 == 0 else 2.15), 0)
        ar.keyframe_insert("rotation_euler", frame=f)
        f += period // 2
        k += 1


def whistle_blow(parts, f0, f1):
    """tangan kanan ke mulut (meniup peluit) lalu kembali."""
    ar = parts["armR"]
    for f, v in ((f0, (0, -.12, 0)), (f0 + 5, (-2.45, -.1, .35)), (f1 - 5, (-2.45, -.1, .35)), (f1, (0, -2.6, 0))):
        ar.rotation_euler = v
        ar.keyframe_insert("rotation_euler", frame=f)


def stack(name, layers, loc, kind="money_red", f0=None, f1=None, nx=2, ny=1):
    ob, h = R.money_stack(name, layers, loc, kind, nx, ny, LS)
    if f0 is not None:
        grow_z(ob, f0, f1 or f0 + 24)
    return ob, h


def split_stack(name, keep, take, loc, f0=None, f1=None):
    """menara Rp12 jt = `keep` lapis merah (sisa) + `take` lapis merah tua (setoran) di atasnya."""
    a, ha = stack(name + "_a", keep, loc, "money_red", f0, f1)
    b, hb = R.money_stack(name + "_b", take, (loc[0], loc[1], loc[2] + ha), "money_dk", 2, 1, LS)
    if f0 is not None:
        # ikut tumbuh: mulai saat bagian bawah hampir penuh
        fb = (f1 or f0 + 24)
        grow_z(b, fb - 4, fb + 10)
    return a, b, ha, hb


def drive(ob, pts, f0, speed=7.0):
    """jalankan kendaraan melewati titik-titik (x,y) di permukaan, menghadap arah gerak."""
    f = f0
    z = ob.location.z
    key(ob, "location", 1, (pts[0][0], pts[0][1], z))
    key(ob, "location", f, (pts[0][0], pts[0][1], z))
    ang = math.atan2(pts[1][1] - pts[0][1], pts[1][0] - pts[0][0])
    key(ob, "rotation_euler", 1, (0, 0, ang))
    key(ob, "rotation_euler", f, (0, 0, ang))
    for a, b in zip(pts[:-1], pts[1:]):
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        key(ob, "rotation_euler", f + 3, (0, 0, ang))
        f += max(2, int(d / speed * FPS))
        key(ob, "location", f, (b[0], b[1], z))
    return f


def street(n, **kw):
    info = R.build_street(**kw)
    jk = R.jukir("jk", (JX, JY, Z0), 0)
    L.pose(jk, "stand")
    info["jukir"] = jk
    return info


# ------------------------------------------------------------------ adegan
def q01(n, info, A):
    """'Modal rompi dan peluit,' — close-up juru parkir: rompi oranye, meniup peluit, lalu melambai."""
    jk = info["jukir"]
    whistle_blow(jk, 1, 22)
    wave(jk, 22, n + 20)
    A["ROMPI"] = (JX - .32, JY - .3, Z0 + 1.55)
    A["PELUIT"] = (JX + .1, JY - .35, Z0 + 1.5)
    cam_move(n, (JX, JY, Z0 + 1.75), (JX, JY, Z0 + 1.8), (-72, 6, 7.2), (-84, 7, 6.2), lens=30, shift=.1)


def q02(n, info, A):
    """'sebulan bisa pegang 12 juta rupiah.' — menara uang Rp12 jt tumbuh di samping juru parkir."""
    jk = info["jukir"]
    wave(jk, 1, n + 20)
    sx, sy = JX + 3.2, JY - .6
    ped("pd", 2.0, (sx, sy, Z0), "mm_green", 2)
    st, h = stack("st", 24, (sx, sy, Z0 + .42), "money_red", fr("Q02", 2.35), fr("Q02", 3.1))
    sparkles("sp", (sx, sy, Z0 + 4.0), fr("Q02", 3.2), n=5, r=2.0, s=.4)
    A["STACK"] = (sx, sy, Z0 + .42 + h)
    cam_move(n, (JX + 1.5, JY, Z0 + 2.6), (JX + 1.6, JY, Z0 + 2.8), (-98, 8, 15.5), (-90, 9, 13.5), lens=24,
             shift=.12)


def q03(n, info, A):
    """'Kok bisa juru parkir minimarket lebih cuan dari karyawannya?' — jukir di luar, kasir di dalam toko,
    koin 'cuan' berputar di sekitar jukir, tanda tanya."""
    jk = info["jukir"]
    wave(jk, 1, n + 20)
    ks = R.kasir("ks", (10.7, R.STORE[1] + 3.3, Z0 + .22), 0)
    L.pose(ks, "stand")
    f = fr("Q03", 6.3)
    for k in range(5):
        a = 2 * math.pi * k / 5
        cn = C.coin(f"cn{k}", .9, (JX + math.cos(a) * 1.4, JY - .4 + math.sin(a) * .5, Z0 + 2.9 + .25 * math.sin(a)))
        pop(cn, f + k * 2, 1.0)
    q = qmark("q", (6.8, -1.0, Z0 + 3.2), .9, f=fr("Q03", 7.05))
    _ = q
    A["JUKIR"] = (JX, JY, Z0 + 2.5)
    A["KASIR"] = (10.7, R.STORE[1] + 3.3, Z0 + 2.7)
    cam_move(n, (6.5, -1.0, Z0 + 2.3), (7.0, -.5, Z0 + 2.4), (-112, 9, 17), (-102, 10, 15.5), lens=22, shift=.12)


def q04(n, info, A):
    """'Kita hitung, satu minimarket ramai.' — pemandangan udara minimarket + kalkulator muncul."""
    for k, x in enumerate((-30, 30)):
        mo = R.rider_motor(f"rm{k}", (x, -24 + k * 4, .03), 0, R.BIKE_COLS[k], R.SHIRTS[k])
        drive(mo, [(x, -24 + k * 4 * 1.0), (x + (1 if k == 0 else -1) * 120, -24 + k * 4 * 1.0)], 1, 9)
    cal = H.calculator("calc", 1.0).build((0, -8, 11))
    cal.rotation_euler = (math.pi / 2 - .35, 0, 0)
    cal.scale = (2.6,) * 3
    pop(cal, 4, 2.6)
    A["CALC"] = (0, -8, 15.5)
    A["STORE"] = (0, R.STORE[1], 6.8)
    cam_move(n, (0, -4, 2), (0, -4, 2), (-116, 34, 64), (-100, 31, 57), lens=22, shift=.08)


def q05(n, info, A):
    """'Sehari didatangi sekitar 150 motor dan 20 mobil.' — motor & mobil berdatangan, parkir penuh."""
    jk = info["jukir"]
    wave(jk, 1, n + 20, 14)
    # motor-motor datang dari jalan, masuk ke barisan tengah (slot kosong dibuat di x 8..12)
    for k in range(7):
        x = -30 - k * 9
        mo = R.rider_motor(f"am{k}", (x, -24.5, .03), 0, R.BIKE_COLS[k], R.SHIRTS[k + 2],
                           ("c_white", "c_navy", "c_coral")[k % 3])
        slot = (8.5 + (k % 4) * 1.0, -9.0 - (k // 4) * 2.6)
        drive(mo, [(x, -24.5), (-6, -24.5), (-2, -18.5), (-2, -6.0), (slot[0], -6.0), slot], 4 + k * 14, 11)
    # mobil datang ke slot kosong
    cr = R.car("ac", (-60, -23.5, .03), 0, "cr_silver", .78)
    drive(cr, [(-60, -23.5), (-8, -23.5), (-3, -18), (-3, -14.5), (6, -14.5), (12.9, -13.6)], fr("Q05", 12.6), 12)
    A["MOTOR"] = (-4, -9.0, Z0 + 2.2)
    A["MOBIL"] = (-12.9, -13.6, Z0 + 2.6)
    cam_move(n, (0, -7, 1.2), (0, -7, 1.2), (-103, 25, 37), (-86, 24, 33), lens=22, shift=.12)


def q06(n, info, A):
    """'Tarif motor Rp2.000, mobil Rp5.000,' — jukir di antara motor & mobil; uang Rp2.000 muncul di atas motor,
    Rp5.000 di atas mobil, lalu terbang ke tangan jukir."""
    jx, jy = 6.6, -12.4
    for lm in info["lamps"]:
        lm["pole"].hide_render = True
        lm["bulb"].hide_render = True
    jk = R.jukir("jk6", (jx, jy, Z0), 0)
    L.pose(jk, "arms_fwd")
    mx, my = 3.4, -13.2
    R.motor("m6", (mx, my, Z0), 0, "bk_blue", .78)
    cx, cy = 10.6, -13.9
    R.car("c6", (cx, cy, Z0), math.pi / 2, "cr_silver", .78)
    f2, f5 = fr("Q06", 15.5), fr("Q06", 16.5)
    n2 = R.note_obj("n2", "n2k", 1.2, (mx, my, Z0 + 3.4))
    pop(n2, f2, 1.0)
    fly(n2, f2 + 22, f2 + 36, (mx, my, Z0 + 3.4), (jx, jy - .6, Z0 + 1.7), arc=.8)
    n5 = R.note_obj("n5", "n5k", 1.2, (cx, cy, Z0 + 4.2))
    pop(n5, f5, 1.0)
    fly(n5, f5 + 20, f5 + 34, (cx, cy, Z0 + 4.2), (jx + .2, jy - .6, Z0 + 1.8), arc=.8)
    A["MOTOR"] = (mx, my, Z0 + 4.0)
    A["MOBIL"] = (cx, cy, Z0 + 4.8)
    cam_move(n, (jx + .4, jy - 1, Z0 + 2.4), (jx + .4, jy - 1, Z0 + 2.4), (-94, 11, 16.5), (-88, 12, 15), lens=22,
             shift=.13)


def q07(n, info, A):
    """'totalnya 400 ribu sehari, atau 12 juta sebulan.' — tumpukan Rp400 rb (sehari), kalender 30 hari,
    lalu menara Rp12 jt. Tabel ringkas di layar (compositor)."""
    jk = info["jukir"]
    wave(jk, 1, n + 20, 18)
    sx, sy = JX + 3.4, JY - .6
    ped("pd", 2.0, (sx, sy, Z0), "mm_green")
    day = W.MB("day")
    for k in range(5):
        R.note(day, (k % 2) * .08, 0, k * .05, "money_red", 1.0)
    d = day.build((sx, sy, Z0 + .42))
    pop(d, fr("Q07", 18.2), 1.0)
    key(d, "scale", fr("Q07", 19.9), (1, 1, 1))
    key(d, "scale", fr("Q07", 20.1), (.001,) * 3)
    cal = K.calendar("cal", "30", (sx - 3.4, sy + .4, Z0), 1.3)
    pop(cal, fr("Q07", 19.55), 1.0)
    st, h = stack("st", 24, (sx, sy, Z0 + .42), "money_red", fr("Q07", 19.9), fr("Q07", 20.9))
    sparkles("sp", (sx, sy, Z0 + 4.0), fr("Q07", 21.0), n=5, r=2.0, s=.4)
    A["DAY"] = (sx, sy, Z0 + 1.2)
    A["STACK"] = (sx, sy, Z0 + .42 + h)
    A["CAL"] = (sx - 3.4, sy + .4, Z0 + 2.5)
    cam_move(n, (JX + 1.8, JY, Z0 + 2.3), (JX + 1.9, JY, Z0 + 2.4), (-95, 7, 15), (-90, 8, 14), lens=24, shift=.26)


def q08(n, info, A):
    """'Tapi, uang itu nggak masuk kantong semua.' — suasana meredup; menara terbelah: bagian atas (merah tua)
    terangkat lepas dari tumpukan milik jukir."""
    jk = info["jukir"]
    L.pose(jk, "shrug", 1)
    sun = bpy.data.objects.get("sun")
    for f, e, c in ((1, 3.6, (1.0, .95, .86)), (24, 2.4, (.8, .86, 1.0))):
        sun.data.energy = e
        sun.data.color = c
        sun.data.keyframe_insert("energy", frame=f)
        sun.data.keyframe_insert("color", frame=f)
    sx, sy = JX + 3.4, JY - .6
    ped("pd", 2.0, (sx, sy, Z0), "mm_green")
    a, b, ha, hb = split_stack("st", 15, 9, (sx, sy, Z0 + .42))
    f = fr("Q08", 24.1)
    key(b, "location", 1, b.location.copy())
    key(b, "location", f, b.location.copy())
    key(b, "location", f + 10, (sx + .6, sy, b.location.z + 1.2))
    A["POUCH"] = (JX - .1, JY - .3, Z0 + 1.1)
    A["TOP"] = (sx + .6, sy, Z0 + .42 + ha + hb + 1.2)
    cam_move(n, (JX + 1.8, JY, Z0 + 2.4), (JX + 1.9, JY, Z0 + 2.6), (-88, 8, 14), (-92, 9, 13.5), lens=24,
             shift=.14)


def map_scene(n, A, sid, flows=True, busy=None, pile_t=None):
    spots = R.city_map("map", 9, 8)
    h = R.hq("hq", (0, 0, 0), 1.0)
    pins = []
    for k, (x, y) in enumerate(spots):
        pn = T_pin(f"pin{k}", "pin_y" if (busy and k in busy) else "pin_g")
        pn.location = (x, y + 2, 2.5)
        pn.scale = (2.4,) * 3
        pins.append(pn)
    return spots, h, pins


def T_pin(name, color):
    import world_tahu as T
    return T.pin(name, color).build()


def q09(n, info, A):
    """'Di banyak titik, ada setoran ke pengelola, misalnya 150 ribu per hari.' — peta kota: titik-titik parkir
    minimarket menyala, lalu uang mengalir ke markas 'pengelola' (siluet di depan layar)."""
    spots, h, pins = map_scene(n, A, "Q09")
    for k, pn in enumerate(pins):
        pop(pn, fr("Q09", 25.3) + k * 3, 2.4)
    for part in (h["frame"], h["screen"], h["sil"]["body"]):
        pop(part, fr("Q09", 27.6), part.scale[0])
    f0 = fr("Q09", 28.4)
    for k, (x, y) in enumerate(spots):
        for r in range(3):
            nt = R.note_obj(f"fn{k}_{r}", "money_red", 2.2, (x, y, 4))
            fs = f0 + k * 3 + r * 26
            if fs > n - 8:
                continue
            pop(nt, fs, 1.0)
            fly(nt, fs, fs + 22, (x, y, 4.0), (0, -4.6, 18.0), arc=8.0)
            key(nt, "scale", fs + 20, (1, 1, 1))
            key(nt, "scale", fs + 23, (.001,) * 3)
    A["PIN"] = (spots[0][0], spots[0][1] + 2, 7.5)
    A["HQ"] = (0, -4.6, 27.5)
    A["SETOR"] = (0, -4.6, 18.5)
    cam_move(n, (0, -2, 6), (0, -2, 6), (-104, 50, 112), (-82, 46, 100), lens=24, shift=.06)


def q10(n, info, A):
    """'Berarti, 4,5 juta sebulan keluar sebagai setoran.' — 9 lapis atas (Rp4,5 jt) terbang ke layar
    'pengelola' di sisi parkiran."""
    jk = info["jukir"]
    L.pose(jk, "stand")
    sx, sy = JX + 1.0, JY - .6
    ped("pd", 2.0, (sx, sy, Z0), "mm_green")
    a, b, ha, hb = split_stack("st", 15, 9, (sx, sy, Z0 + .42))
    scx, scy = sx + 7.0, sy + 3.0
    fr_, sc = R.glow_screen("scr", (scx, scy, Z0), 6.0, 4.6, 3.5)
    pg = R.pengelola("pg", (scx, scy - 1.0, Z0), 0)
    _ = (fr_, sc, pg)
    f = fr("Q10", 33.3)
    z_b = b.location.z
    fly(b, f, f + 20, (sx, sy, z_b), (scx, scy - 1.6, Z0 + 2.0), arc=3.0)
    key(b, "scale", f + 16, (1, 1, 1))
    key(b, "scale", f + 21, (.001,) * 3)
    A["SETOR"] = (sx, sy, Z0 + .42 + ha + hb)
    A["LAYAR"] = (scx, scy, Z0 + 5.6)
    cam_move(n, (sx + 3.5, sy + 1.5, Z0 + 2.8), (sx + 3.6, sy + 1.5, Z0 + 2.8), (-96, 9, 21), (-90, 10, 19.5),
             lens=22, shift=.12)


def q11(n, info, A):
    """'Sisanya sekitar 7,5 juta.' — sisa 15 lapis (Rp7,5 jt) bersinar di samping jukir."""
    jk = info["jukir"]
    L.pose(jk, "stand")
    sx, sy = JX + 3.0, JY - .6
    ped("pd", 2.0, (sx, sy, Z0), "mm_green")
    st, h = stack("st", 15, (sx, sy, Z0 + .42))
    sparkles("sp", (sx, sy, Z0 + 2.6), 4, n=5, r=1.8, s=.4)
    A["SISA"] = (sx, sy, Z0 + .42 + h)
    cam_move(n, (JX + 1.5, JY, Z0 + 2.2), (JX + 1.5, JY, Z0 + 2.2), (-92, 8, 13), (-88, 8, 12), lens=24, shift=.13)


def q12(n, info, A):
    """'Dengan kerja dari pagi sampai malam,' — time-lapse siang -> malam, lampu toko & jalan menyala,
    jukir terus melambai."""
    jk = info["jukir"]
    wave(jk, 1, n + 20, 14)
    R.day_night(fr("Q12", 37.3), fr("Q12", 38.2), info["store"], info["lamps"])
    for k in range(3):
        mo = R.rider_motor(f"rm{k}", (-40 - k * 12, -24.5, .03), 0, R.BIKE_COLS[k + 1], R.SHIRTS[k + 4])
        drive(mo, [(-40 - k * 12, -24.5), (80, -24.5)], 1, 14)
    A["JUKIR"] = (JX, JY, Z0 + 2.5)
    cam_move(n, (JX - 1, JY + 2, Z0 + 2.4), (JX - 1, JY + 2, Z0 + 2.4), (-70, 13, 23), (-80, 14, 21), lens=22,
             shift=.12)


def q13(n, info, A):
    """'panas, hujan, tanpa BPJS, dan tanpa kepastian.' — ikon matahari terik, awan + hujan, kartu jaminan
    sosial dicoret, tanda tanya."""
    jk = info["jukir"]
    wave(jk, 1, fr("Q13", 38.85), 14)
    L.pose(jk, "shrug", fr("Q13", 40.3))
    sun = R.sun_icon("sun1", .72)
    sun.location = (JX - 2.7, JY - .5, Z0 + 4.9)
    pop(sun, fr("Q13", 38.6), 1.0)
    key(sun, "rotation_euler", 1, (0, 0, 0))
    key(sun, "rotation_euler", n, (0, .8, 0))
    cm = W.MB("cl")
    R.cloud(cm, 0, 0, 0, .8, "cloud2")
    cl = cm.build((JX + .6, JY - .2, Z0 + 5.5))
    pop(cl, fr("Q13", 38.9), 1.0)
    fr_r = fr("Q13", 38.95)
    rn = R.rain("rn", (JX + .6, JY - .2), (3.0, 1.6), 4.9, 50, f0=fr_r, f1=n)
    rn.scale = (1, 1, 1)
    key(rn, "hide_render", 1, True)
    key(rn, "hide_render", fr_r, False)
    cd = R.card("cd", "BPJS", .7)
    cd.location = (JX + 3.0, JY - .6, Z0 + 2.2)
    pop(cd, fr("Q13", 39.35), 1.0)
    xm = L.xmark("xm", (JX + 3.0, JY - .9, Z0 + 2.9), .8)
    pop(xm, fr("Q13", 39.6), 1.0)
    q = qmark("q", (JX - 2.7, JY - .6, Z0 + .8), .6, f=fr("Q13", 40.35))
    _ = q
    A["PANAS"] = (JX - 2.7, JY - .5, Z0 + 6.4)
    A["HUJAN"] = (JX + .6, JY - .2, Z0 + 6.7)
    A["BPJS"] = (JX + 3.0, JY - .6, Z0 + 3.8)
    A["Q"] = (JX - 2.7, JY - .6, Z0 + 2.7)
    cam_move(n, (JX + .2, JY, Z0 + 3.0), (JX + .2, JY, Z0 + 3.0), (-90, 6, 14.5), (-90, 7, 13.5), lens=24, shift=.12)


def q14(n, info, A):
    """'Pelajarannya, yang mahal itu bukan jasanya, tapi lokasinya.' — close-up jukir (jasa), lalu pin lokasi
    raksasa jatuh di parkiran minimarket & kamera mundur ke udara."""
    jk = info["jukir"]
    wave(jk, 1, n + 20, 16)
    f_pin = fr("Q14", 44.05)
    import world_tahu as T
    pn = T.pin("pin", "pin_y").build()
    pn.scale = (4.0,) * 3
    fly(pn, f_pin, f_pin + 8, (0, -6, 60), (0, -6, Z0))
    pop(pn, f_pin, 4.0)
    ring = W.MB("ring")
    for k in range(40):
        a0, a1 = 2 * math.pi * k / 40, 2 * math.pi * (k + 1) / 40
        r0, r1 = 13.5, 15.0
        ring.poly([(math.cos(a0) * r0, math.sin(a0) * r0, 0), (math.cos(a1) * r0, math.sin(a1) * r0, 0),
                   (math.cos(a1) * r1, math.sin(a1) * r1, 0), (math.cos(a0) * r1, math.sin(a0) * r1, 0)],
                  [(0, 1, 2, 3)], "pin_y")
    rg = ring.build((0, -6, Z0 + .05))
    rg.data.materials[0] = lp.mat("pin_y", 1.2)
    pop(rg, f_pin + 6, 1.0)
    A["JASA"] = (JX, JY, Z0 + 2.6)
    A["LOKASI"] = (0, -6, Z0 + 10.5)
    cam, tgt = make_camera(lens=24, shift_y=.12)
    t0 = (JX, JY, Z0 + 1.9)
    t1 = (0, -4, 2.0)
    cam_keys(cam, tgt, [(1, orbit(t0, -84, 7, 8), t0), (fr("Q14", 43.6), orbit(t0, -92, 9, 9.5), t0),
                        (n, orbit(t1, -104, 32, 66), t1)])


def q15(n, info, A):
    """'Siapa yang menguasai titik ramai, dia yang menguasai uangnya.' — peta kota: titik ramai menyala kuning,
    uang dari semuanya mengalir ke satu tumpukan besar di markas."""
    busy = {0, 2, 3, 5, 7}
    spots, h, pins = map_scene(n, A, "Q15", busy=busy)
    f0 = fr("Q15", 45.4)
    for k, pn in enumerate(pins):
        key(pn, "scale", 1, (2.4,) * 3)
        if k in busy:
            key(pn, "scale", f0 + k * 2, (2.4,) * 3)
            key(pn, "scale", f0 + k * 2 + 5, (3.2,) * 3)
            key(pn, "scale", f0 + k * 2 + 9, (2.9,) * 3)
    pile, hp = stack("pile", 14, (0, -9.5, 0), "money_red", fr("Q15", 46.9), fr("Q15", 48.2), nx=3, ny=2)
    pile.scale = (1.6, 1.6, 1.6)
    grow_z(pile, fr("Q15", 46.9), fr("Q15", 48.2), 1.6)
    f1 = fr("Q15", 46.6)
    for k, (x, y) in enumerate(spots):
        if k not in busy:
            continue
        for r in range(3):
            nt = R.note_obj(f"fn{k}_{r}", "money_red", 2.2, (x, y, 4))
            fs = f1 + k * 2 + r * 18
            if fs > n - 6:
                continue
            pop(nt, fs, 1.0)
            fly(nt, fs, fs + 18, (x, y, 4.0), (0, -9.5, 6.0), arc=7.0)
            key(nt, "scale", fs + 16, (1, 1, 1))
            key(nt, "scale", fs + 19, (.001,) * 3)
    A["RAMAI"] = (spots[2][0], spots[2][1] + 2, 8.2)
    A["UANG"] = (0, -9.5, 7.6)
    cam_move(n, (0, -4, 4), (0, -4, 4), (-78, 44, 100), (-96, 40, 92), lens=24, shift=.06)


def q16(n, info, A):
    """'Ingat, ini simulasi.' — papan laporan + cap merah SIMULASI menghantam."""
    g = W.MB("g")
    g.box(-30, -30, -1, 30, 30, 0, "pk_pave")
    g.build()
    ped("pd", 3.0, (0, 0, 0), "mm_green")
    doc = L.report_doc("doc", 2.2).build((0, 0, .42))
    pop(doc, 3, 1.0)
    f = fr("Q16", 49.4)
    st = C.stamp("st", "SIMULASI", 1.0)
    fly(st, f, f + 6, (0, -3.0, 12), (0, -1.6, 3.0))
    pop(st, f, 1.0)
    for k, s in ((f + 6, 1.15), (f + 9, 1.0)):
        key(st, "scale", k, (s, s, s))
    A["DOC"] = (0, 0, 7.1)
    cam_move(n, (0, 0, 3.6), (0, 0, 3.6), (-94, 9, 20), (-88, 11, 18.5), lens=22, shift=.08)


def q17(n, info, A):
    """'Angka tiap lokasi bisa beda jauh.' — tiga minimarket mini: ramai / sedang / sepi, tumpukan uang beda."""
    g = W.MB("g")
    g.box(-60, -40, -1, 60, 40, 0, "pk_ground")
    g.box(-60, -14, 0, 60, -8, .05, "pk_asph")
    rr = random.Random(3)
    for k, (x, busy) in enumerate(((-8.5, 2.0), (0, 1.0), (8.5, .3))):
        R.mini_store(g, x, 0, 1.25, busy, rr)
    g.build()
    for k, (x, lay) in enumerate(((-8.5, 22), (0, 12), (8.5, 4))):
        stack(f"st{k}", lay, (x, -4.5, .08), "money_red", fr("Q17", 50.6) + k * 10, fr("Q17", 51.4) + k * 10)
        A[("RAMAI", "SEDANG", "SEPI")[k]] = (x, -4.5, .08 + lay * LH + .4)
    for k in range(14):
        rr2 = random.Random(k)
        tb = W.MB(f"bg{k}")
        x = -30 + k * 4.6
        tb.box(x, 14, 0, x + 3.8, 18, rr2.uniform(4, 11), rr2.choice(("rk1", "rk2", "rk3", "rk4", "ct_glass")))
        C.street_tree(tb, x + 2, 11, 1.0, rr2)
        tb.build()
    cam_move(n, (0, -2, 2.4), (0, -2, 2.4), (-92, 24, 37), (-88, 26, 34), lens=22, shift=.1)


def q18(n, info, A):
    """'Menurut kamu, yang paling untung itu juru parkirnya, atau orang di balik layarnya?' — jukir di alas kiri,
    siluet di depan layar berpendar di kanan, tanda tanya di tengah."""
    jk = info["jukir"]
    jk["body"].location = (-4.0, JY, Z0 + .42)
    wave(jk, 1, n + 20, 16)
    ped("pd", 2.0, (-4.0, JY, Z0), "mm_green")
    scx = 5.5
    fr_, sc = R.glow_screen("scr", (scx, JY + 1.2, Z0), 6.0, 4.6, 3.5)
    pg = R.pengelola("pg", (scx, JY + .2, Z0), 0)
    L.pose(pg, "stand")
    for part in (fr_, sc, pg["body"]):
        pop(part, fr("Q18", 57.6), part.scale[0])
    q = qmark("q", (.8, JY - .6, Z0 + 3.4), .9, f=fr("Q18", 58.45))
    _ = q
    A["JUKIR"] = (-4.0, JY, Z0 + 2.9)
    A["LAYAR"] = (scx, JY + 1.2, Z0 + 5.4)
    cam_move(n, (.6, JY, Z0 + 2.7), (.6, JY, Z0 + 2.7), (-92, 8, 21), (-90, 9, 18.5), lens=22, shift=.12)


def q19(n, info, A):
    """'Tulis di kolom komentar.' — udara malam: minimarket menyala, motor lalu-lalang (CTA)."""
    jk = info["jukir"]
    wave(jk, 1, n + 20, 14)
    R.day_night(1, 2, info["store"], info["lamps"])
    for k in range(4):
        mo = R.rider_motor(f"rm{k}", (-60 - k * 10, -24.5 + (k % 2) * 4, .03), 0, R.BIKE_COLS[k], R.SHIRTS[k])
        drive(mo, [(-60 - k * 10, -24.5 + (k % 2) * 4), (80, -24.5 + (k % 2) * 4)], 1, 12)
    A["STORE"] = (0, R.STORE[1], 7.2)
    cam_move(n, (0, -4, 2), (0, -4, 2), (-96, 30, 56), (-90, 33, 52), lens=22, shift=.08)


SCENES = {f"Q{k:02d}": fn for k, fn in enumerate(
    (q01, q02, q03, q04, q05, q06, q07, q08, q09, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19), 1)}
WORLD = {"Q01", "Q02", "Q03", "Q04", "Q05", "Q06", "Q07", "Q08", "Q10", "Q11", "Q12", "Q13", "Q14", "Q18", "Q19"}


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
    R.setup_prk_light()
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, n
    info = {}
    if args.scene in WORLD:
        night = args.scene in ("Q12", "Q19")
        info = street(n, night_lamps=1.0 if night else 0.0, people=args.scene not in ("Q01", "Q18"))
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
