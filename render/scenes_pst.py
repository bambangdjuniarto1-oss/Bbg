"""23 adegan video "Bedah Bisnis: Pestapora 2026" (timeline mengikuti VO hasil humanize_vo.py, ±82,2 dtk).

  python3 render/scenes_pst.py -- --scene P01 --out OUT/P01 [--res 720x1280] [--samples 4] [--frames a-b]

Isi VO: hook (potensi Rp16 M dari festival 3 hari, bukan tiket konser biasa, bisnis di balik Pestapora) ->
330+ penampil, 19 panggung, 120 rb+ pergerakan pengunjung -> hitung: tiket Rp225-650 rb, rata-rata Rp250 rb
x 120 rb = Rp30 M; sponsor (SIMPATI, BINTANG, VIBE) Rp15 M; tenant + merch + aktivasi Rp3 M -> total Rp48 M ->
biaya artis, produksi, venue, keamanan, kru, operasional Rp32 M -> sisa Rp16 M -> simulasi, bukan laporan
resmi -> festival menjual perhatian ke brand -> menarik atau berisiko? -> CTA.
Waktu (detik) = timeline video, sama dengan render/scenes/pst_words.json.
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
import world_pst as P  # noqa: E402
from scenes import key, make_camera, cam_keys, orbit  # noqa: E402
from scenes_laundry import pop, grow_z, fly, emission_ramp, _anchor_pos  # noqa: E402
from scenes_amdk import sparkles  # noqa: E402

FPS = 30
TIMELINE = [("P01", 0.00), ("P02", 3.05), ("P03", 5.15), ("P04", 6.50), ("P05", 8.70), ("P06", 12.90),
            ("P07", 14.00), ("P08", 17.45), ("P09", 19.45), ("P10", 24.90), ("P11", 29.15), ("P12", 33.00),
            ("P13", 36.70), ("P14", 39.00), ("P15", 43.00), ("P16", 47.15), ("P17", 51.25), ("P18", 54.10),
            ("P19", 59.30), ("P20", 63.95), ("P21", 68.10), ("P22", 72.05), ("P23", 76.80)]
END_T = 82.21
S_M = .8                          # skala ikat uang
LH = .29 * S_M                    # tinggi 1 lapis = Rp1 miliar
DZ = P.DECK_H                     # tinggi lantai panggung data
MONEY = {"tiket": ("money_b", "money_b2"), "sponsor": ("money_y", "money_y2"), "tenant": ("money_g", "money_g2"),
         "biaya": ("money_r", "money_r2"), "sisa": ("money_g", "money_g2")}


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
def money_tower(name, miliar, loc, kind="tiket", f0=None, f1=None, nx=3, ny=2, s=S_M):
    """menara uang `miliar` lapis (1 lapis = Rp1 M). Return (objek, tinggi)."""
    k1, k2 = MONEY[kind]
    mb = W.MB(name)
    for k in range(int(miliar)):
        for i in range(nx):
            for j in range(ny):
                x, y, z = (i - (nx - 1) / 2) * 1.68 * s, (j - (ny - 1) / 2) * .82 * s, k * .29 * s
                mb.box(x - .8 * s, y - .38 * s, z, x + .8 * s, y + .38 * s, z + .26 * s, k1)
                mb.box(x - .82 * s, y - .4 * s, z + .24 * s, x + .82 * s, y + .4 * s, z + .27 * s, k2)
                mb.box(x - .14 * s, y - .41 * s, z - .005, x + .14 * s, y + .41 * s, z + .275 * s, "money_band")
    ob = mb.build(loc)
    if f0 is not None:
        grow_z(ob, f0, f1 or f0 + 30)
    return ob, int(miliar) * .29 * s


def ped(name, r, loc, key_="led_p", f=None):
    p = M.pedestal(name, r, key_).build(loc)
    if f is not None:
        pop(p, f, 1.0)
    return p


def qmark(name, loc, s=1.0, key_="tk_gold", f=None):
    q = H.text(name, "?", 2.6 * s, key_, depth=.4 * s, loc=loc, emission=.8)
    if f is not None:
        pop(q, f, 1.0)
    return q


def live_world(info, n, crowd=True, beams=True, wheel=True, pulse=(1.4, 4.0)):
    ms = info["main"]
    P.pulse_led(ms["mats"], 1, n, lo=pulse[0], hi=pulse[1])
    if beams:
        for k, b in enumerate(ms["beams"]):
            if k < 9:
                P.sweep(b, 1, n, rx=(.65, .2), rz=((k - 4) * .08 - .25, (k - 4) * .08 + .25), period=58, phase=k % 2)
            else:
                P.sweep(b, 1, n, rx=(math.pi - .45, math.pi - .1), rz=(-.35, .35), period=72, phase=k % 2)
    if crowd and info.get("crowd"):
        P.jump(info["crowd"], 1, n, .3)
    if wheel and info.get("wheel"):
        P.turn(info["wheel"], 1, n, 1.4)


def stage_set(n, led=(.25, .7), beams=True, crowd_n=260):
    """panggung data (close-up) + animasi dasar. Return dict."""
    ms = P.data_stage(crowd_n=crowd_n, beams=beams)
    P.pulse_led(ms["mats"], 1, n, lo=led[0], hi=led[1])
    for k, b in enumerate(ms["beams"]):
        if k < 9:
            P.sweep(b, 1, n, rx=(.7, .3), rz=((k - 4) * .07 - .2, (k - 4) * .07 + .2), period=66, phase=k % 2)
        else:
            P.sweep(b, 1, n, rx=(math.pi - .4, math.pi - .12), rz=(-.3, .3), period=80, phase=k % 2)
    P.jump(ms["crowd"], 1, n, .22)
    return ms


def data_cam(n, tg=(0, 2.5, 7.0), az=(-94, -88), el=(9, 11), d=(31, 29), lens=20, shift=.1):
    cam, tgt = make_camera(lens=lens, shift_y=shift)
    cam_keys(cam, tgt, [(1, orbit(tg, az[0], el[0], d[0]), tg), (n, orbit(tg, az[1], el[1], d[1]), tg)])
    return cam


def beacon(name, loc, h=34.0, key_="beam_y", f=None):
    """tiang cahaya penanda panggung (berkas ke atas) + bola menyala di bawahnya."""
    b = P.light_beam(name, (loc[0], loc[1], loc[2] + h), h, 1.6, key_, 1.6, rx=0.0)
    b.rotation_euler = (math.pi, 0, 0)
    b.location = (loc[0], loc[1], loc[2])
    mb = W.MB(name + "_o")
    mb.sphere(0, 0, 0, 1.6, "tk_gold")
    o = mb.build((loc[0], loc[1], loc[2] + 2.5))
    P.lit(o, "tk_gold", 6.0)
    P.no_light(o)
    if f is not None:
        pop(o, f, 1.0)
        key(b, "scale", 1, (1, 1, .001))
        key(b, "scale", f, (1, 1, .001))
        key(b, "scale", f + 8, (1, 1, 1))
    return o


# ------------------------------------------------------------------ adegan
def p01(n, info, A):
    """hook: 'Gimana caranya menghasilkan potensi 16 miliar rupiah' — festival senja dari udara, menara uang
    Rp16 M menjulang di belakang panggung utama, kembang api."""
    live_world(info, n)
    f = fr("P01", 1.9)
    ob, h = money_tower("big", 16, (40, 84, 0), "sisa", f - 18, f + 6, nx=3, ny=2, s=5.2)
    sparkles("sp", (40, 80, h), f + 6, 5, 11, 2.0)
    P.fireworks("fw", (0, 70, 52), 8, n, (36, 12, 8), 14, seed=1)
    A["TOWER"] = (40, 84, h + 1)
    A["STAGE"] = (0, 54, 20)
    cam, tgt = make_camera(lens=20, shift_y=.08)
    tg0, tg1 = (0, 60, 14), (0, 66, 18)
    cam_keys(cam, tgt, [(1, orbit(tg0, -104, 30, 200), tg0), (n, orbit(tg1, -94, 22, 150), tg1)])


def p02(n, info, A):
    """'cuma dari festival musik 3 hari?' — dari tengah penonton: band tampil, kalender '3' raksasa muncul."""
    live_world(info, n)
    bd = P.band("bd", (0, P.MAIN[1] - 1), P.DECK_H)
    P.perform(bd, 1, n)
    f = fr("P02", 4.2)
    cal = K.calendar("cal", "3", (0, 28, 13), 5.5, top="tn_red")
    pop(cal, f, 1.0)
    P.fireworks("fw", (0, 70, 46), f, n, (26, 8, 6), 12, seed=2)
    A["CAL"] = (0, 28, 13 + 9.8)
    A["STAGE"] = (0, 54, 12)
    cam, tgt = make_camera(lens=20, shift_y=.04)
    cam_keys(cam, tgt, [(1, (-3, 0, 7), (0, 50, 13)), (n, (-1.5, 6, 7.5), (0, 50, 14))])


def p03(n, info, A):
    """'Bukan jualan tiket konser biasa,' — tiket konser raksasa di panggung, silang merah menghantam."""
    stage_set(n)
    ped("pd", 3.4, (0, 2, DZ), "tk_blue")
    tk = P.ticket("tk", "KONSER", s=1.9, label="TIKET")
    tk.location = (0, 2, DZ + .42)
    pop(tk, 2, 1.0)
    key(tk, "rotation_euler", 1, (0, 0, -.25))
    key(tk, "rotation_euler", n, (0, 0, .15))
    f = fr("P03", 6.0)
    x = L.xmark("x", (0, -.6, DZ + 2.4), 2.6)
    pop(x, f, 1.0)
    A["TIKET"] = (0, 2, DZ + 4.4)
    data_cam(n, tg=(0, 2, DZ + 2.4), d=(19, 17), el=(8, 10), shift=.06)


def p04(n, info, A):
    """'ini bisnis di balik Pestapora.' — kamera berputar ke belakang panggung: truk, genset, peti alat, kru."""
    live_world(info, n, crowd=False)
    P.backstage("bk", (0, P.MAIN[1] + P.STAGE_D / 2 + 2))
    bd = P.band("bd", (0, P.MAIN[1] - 1), P.DECK_H)
    P.perform(bd, 1, n)
    rnd = random.Random(4)
    yb = P.MAIN[1] + P.STAGE_D / 2 + 2
    for k in range(7):
        lk = C.KRU[k % len(C.KRU)]
        x0, y0 = rnd.uniform(-14, 14), yb + rnd.uniform(4, 16)
        pr = C.person(f"kr{k}", lk, (x0, y0, 0), rnd.uniform(-3, 3), extra=("headset",) if k % 2 else ())
        if k < 4:
            L.walk_to(pr, [(x0, y0), (x0 + rnd.uniform(-5, 5), y0 + rnd.uniform(-5, 3))], 1, speed=1.6)
    A["BACK"] = (0, yb + 10, 4)
    tg0, tg1 = (0, 66, 6), (0, 78, 3)
    cam, tgt = make_camera(lens=20, shift_y=.06)
    cam_keys(cam, tgt, [(1, orbit(tg0, -60, 26, 62), tg0), (n, orbit(tg1, 62, 30, 48), tg1)])


def p05(n, info, A):
    """'Pestapora 2026 menghadirkan lebih dari 330 penampil,' — panggung utama, band tampil, sorot lampu
    menyapu, penonton melompat."""
    live_world(info, n, pulse=(1.6, 4.5))
    bd = P.band("bd", (0, P.MAIN[1] - 1), P.DECK_H)
    P.perform(bd, 1, n)
    f = fr("P05", 11.6)
    P.fireworks("fw", (0, 70, 34), f, n, (20, 6, 5), 12, seed=5)
    A["BAND"] = (0, 58, 7.8)
    A["SCREEN"] = (0, 69, 16)
    cam, tgt = make_camera(lens=22, shift_y=.04)
    cam_keys(cam, tgt, [(1, (4, 30, 6.5), (0, 60, 7.5)), (n, (1, 38, 6.2), (0, 60, 7.2))])


def p06(n, info, A):
    """'19 panggung,' — festival dari atas, 19 tiang cahaya penanda panggung muncul beruntun."""
    live_world(info, n)
    stg = info["stages"]
    order = sorted(range(len(stg)), key=lambda i: math.hypot(stg[i][1][0], stg[i][1][1] - 40))
    for j, i in enumerate(order):
        kind, (x, y, top) = stg[i]
        beacon(f"bc{i}", (x, y, top + 1), 40, "beam_y", 2 + int(j * 1.2))
    A["MAIN"] = (0, 62, 30)
    A["FIELD"] = (0, 90, 4)
    cam, tgt = make_camera(lens=18, shift_y=.12)
    tg = (0, 74, 0)
    cam_keys(cam, tgt, [(1, orbit(tg, -92, 52, 330), tg), (n, orbit(tg, -90, 54, 312), tg)])


def p07(n, info, A):
    """'dan lebih dari 120 ribu pergerakan pengunjung selama 3 hari.' — gerbang masuk: arus pengunjung
    mengalir melewati pemindai, panah arus bercahaya di jalur."""
    live_world(info, n, crowd=False)
    gy = P.GATE_Y
    rnd = random.Random(7)
    for g in range(6):
        obs, _ = P.fest_crowd(f"q{g}", 34, -11, gy - 30 + g * 0, 11, gy - 2, seed=20 + g, s=1.0, groups=1,
                              arms_frac=.05, phone_frac=0)
        ob = obs[0]
        off = rnd.uniform(0, 4)
        key(ob, "location", 1, (rnd.uniform(-.4, .4), -off - 14 + g * 0, 0))
        key(ob, "location", n, (rnd.uniform(-.4, .4), -off - 14 + 16, 0))
        if g >= 3:
            ob.hide_render = True
    inside, _ = P.fest_crowd("in", 150, -12, gy + 2, 12, gy + 40, seed=31, s=1.0, groups=2, arms_frac=.15,
                             phone_frac=0)
    for ob in inside:
        key(ob, "location", 1, (0, 0, 0))
        key(ob, "location", n, (0, 9, 0))
    # panah arus (chevron bercahaya) di jalur utama
    for k in range(6):
        mb = W.MB(f"ar{k}")
        mb.poly([(-2.2, 0, .1), (0, 2.2, .1), (2.2, 0, .1), (2.2, -1.2, .1), (0, 1.0, .1), (-2.2, -1.2, .1)],
                [(0, 1, 2, 3, 4, 5)], "led_g")
        ob = mb.build((0, gy + 6 + k * 9, 0))
        P.lit(ob, "led_g", 4.0)
        key(ob, "location", 1, (0, gy + 6 + k * 9, .05))
        key(ob, "location", n, (0, gy + 6 + k * 9 + 9, .05))
    f = fr("P07", 14.6)
    A["GATE"] = (0, gy, 14.5)
    A["FLOW"] = (0, gy + 22, 3)
    A["DAYS"] = (0, P.MAIN[1], 26)
    cam, tgt = make_camera(lens=20, shift_y=.08)
    tg0, tg1 = (0, gy + 8, 4), (0, gy + 18, 6)
    cam_keys(cam, tgt, [(1, orbit(tg0, -98, 26, 58), tg0), (n, orbit(tg1, -92, 30, 64), tg1)])
    _ = f


def p08(n, info, A):
    """'Sekarang kita hitung uangnya.' — kalkulator raksasa di panggung disorot, koin bermunculan."""
    stage_set(n, led=(.5, 1.4))
    ped("pd", 3.2, (0, 2.5, DZ), "tk_gold")
    cal = H.calculator("calc", 2.2).build((0, 2.5, DZ + 2.6))
    cal.rotation_euler = (1.15, 0, 0)
    pop(cal, 3, 1.0)
    f = fr("P08", 18.4)
    for k in range(5):
        a = -1.0 + k * .5
        cn = C.coin(f"cn{k}", 1.0, (math.sin(a) * 5.2, .5, DZ + 3.2 + math.cos(a) * 3.6))
        pop(cn, f + k * 3, 1.0)
        key(cn, "rotation_euler", 1, (0, 0, 0))
        key(cn, "rotation_euler", n, (0, 0, 3.0))
    A["CALC"] = (0, 2.5, DZ + 6.4)
    data_cam(n, tg=(0, 2.5, DZ + 3.4), d=(21, 19), el=(9, 12), shift=.06)


def p09(n, info, A):
    """'Harga tiket mulai dari 225 ribu sampai 650 ribu.' — dua tiket di atas kolom harga (biru Rp225rb,
    emas Rp650rb), tinggi kolom sebanding harga."""
    stage_set(n)
    f1, f2 = fr("P09", 20.7), fr("P09", 23.3)
    for (x, price, k1, k2, hh, f, nm) in ((-4.6, "Rp225RB", "tk_blue", "tk_blue2", 2.25 * 1.2, f1, "T1"),
                                          (4.6, "Rp650RB", "tk_gold", "tk_gold2", 6.5 * 1.2, f2, "T2")):
        ped(f"pd{nm}", 2.4, (x, 2.5, DZ), k1, f - 6)
        b = C.bar3d(f"bar{nm}", hh, (x, 2.5, DZ + .42), 2.6, k1)
        grow_z(b, f, f + 16)
        tk = P.ticket(f"tk{nm}", price, k1, k2, 1.15, label="TIKET")
        p0 = (x, 2.0, DZ + .42 + hh + 8)
        p1 = (x, 2.0, DZ + .42 + hh + .2)
        fly(tk, f + 4, f + 18, p0, p1)
        pop(tk, f + 4, 1.0)
        A[nm] = (x, 2.0, DZ + .42 + hh + 2.6)
    data_cam(n, tg=(0, 2.5, DZ + 5.2), d=(27, 25.5), el=(8, 10), shift=.06)


def p10(n, info, A):
    """'Kalau rata-rata pendapatan tiket kita asumsikan 250 ribu per kunjungan,' — pemindai tiket di gerbang:
    pengunjung lewat satu per satu, tiap kunjungan memunculkan koin Rp250rb."""
    live_world(info, n, crowd=False)
    gy = P.GATE_Y
    lane_x = [-13 + 2 + k * 22 / 6 + 22 / 12 for k in range(6)]
    xl = lane_x[2]
    looks = [dict(skin=s_, top=t_, sleeve=t_, bottom=b_, shoe="shoe_w", hair=h_, hair_col=hc, acc=())
             for s_, t_, b_, h_, hc in (("skin2", "c_coral", "c_denim", "short", "hair_blk"),
                                         ("skin1", "c_mint", "c_black", "hijab", "hij_cream"),
                                         ("skin3", "c_mustard", "c_khaki", "cap", "c_navy"),
                                         ("skin2", "c_lilac", "c_denim", "long", "hair_brn"))]
    for k, lk in enumerate(looks):
        pr = C.person(f"v{k}", lk, (xl, gy - 14 - k * 3.2, 0), 0)
        f0 = 1 + 0
        t_arr = L.walk_to(pr, [(xl, gy - 14 - k * 3.2), (xl, gy + 10 - k * 3.2)], f0, speed=2.3)
        # koin Rp250rb muncul saat melewati pemindai (y = gy)
        f_scan = f0 + int((14 + k * 3.2) / 2.3 * FPS)
        if f_scan < n - 6:
            cn = C.coin(f"cn{k}", 1.1, (xl + .6, gy - 1.2, 4.2))
            pop(cn, f_scan, 1.0)
            fly(cn, f_scan + 8, f_scan + 22, (xl + .6, gy - 1.2, 4.2), (xl + 8.5, gy - 3, 2.0))
            key(cn, "scale", f_scan + 22, (1, 1, 1))
            key(cn, "scale", f_scan + 25, (.001,) * 3)
        _ = t_arr
    # antrean statis di jalur lain
    for j, x in enumerate(lane_x):
        if j == 2:
            continue
        mb = W.MB(f"qq{j}")
        rr = random.Random(j)
        for k in range(5):
            P.fan(mb, x, gy - 3 - k * 2.2, 0, 1.1, rr, arms=False)
        mb.build()
    ped("pd", 2.4, (xl + 8.5, gy - 3, 0), "tk_gold")
    pile, hp = money_tower("pile", 3, (xl + 8.5, gy - 3, .42), "tiket", fr("P10", 27.0), fr("P10", 28.6), nx=2, ny=2,
                           s=.7)
    A["SCAN"] = (xl, gy - .6, 3.4)
    A["COIN"] = (xl + 8.5, gy - 3, 3.6)
    cam, tgt = make_camera(lens=20, shift_y=.05)
    tg = (xl + 3, gy - 2, 2.6)
    cam_keys(cam, tgt, [(1, orbit(tg, -68, 16, 21), tg), (n, orbit(tg, -80, 18, 19), tg)])


def p11(n, info, A):
    """'potensi omzet tiketnya 30 miliar rupiah.' — tiket-tiket terbang masuk, menara uang biru Rp30 M tumbuh."""
    stage_set(n)
    ped("pd", 2.8, (0, 2.5, DZ), "tk_blue")
    f = fr("P11", 30.5)
    ob, h = money_tower("tk", 30, (0, 2.5, DZ + .42), "tiket", f - 8, f + 34)
    for k in range(8):
        t = P.ticket(f"t{k}", "Rp250RB", s=.5, label="")
        a = -1.2 + k * .34
        p0 = (math.sin(a) * 13, -4, DZ + 2 + math.cos(a) * 9)
        fs = 4 + k * 5
        fly(t, fs, fs + 14, p0, (0, 2.5, DZ + .42 + min(h, (fs + 14 - f + 8) / 42 * h) + .5))
        key(t, "scale", 1, (.001,) * 3)
        key(t, "scale", fs, (1, 1, 1))
        key(t, "scale", fs + 14, (1, 1, 1))
        key(t, "scale", fs + 16, (.001,) * 3)
    sparkles("sp", (0, 2.5, DZ + .42 + h), f + 36, 5, 2.6, .4)
    A["TIKET"] = (0, 2.5, DZ + .42 + h + .3)
    data_cam(n, tg=(0, 2.5, DZ + 4.4), d=(26, 24), el=(8, 10), shift=.18)


def p12(n, info, A):
    """'Belum dari sponsor, seperti SIMPATI, BINTANG, dan VIBE.' — area booth aktivasi sponsor (generik),
    backdrop tiap booth menyala bergantian sesuai nama yang disebut."""
    live_world(info, n)
    bb = info["booths"]
    for k, (x, y) in enumerate(bb):
        ob = bpy.data.objects.get(f"bb{k}_g")
        if ob:
            f = fr("P12", (34.25, 35.18, 36.1)[k])
            emission_ramp(ob.data.materials[0], [(1, .4), (f, .4), (f + 6, 4.5)])
    for k in range(3):
        x, y = bb[k]
        A[f"B{k + 1}"] = (x, y + 3.4, 7.6)
    cam, tgt = make_camera(lens=18, shift_y=.04)
    tg0, tg1 = (0, -18, 3), (0, -16, 3)
    cam_keys(cam, tgt, [(1, orbit(tg0, -96, 34, 72), tg0), (n, orbit(tg1, -88, 36, 66), tg1)])


def p13(n, info, A):
    """'Kita asumsikan sponsor menyumbang 15 miliar,' — menara tiket Rp30 M di kiri, kotak sponsor terbang
    masuk & menara emas Rp15 M tumbuh di kanan."""
    stage_set(n)
    ped("pa", 2.8, (-4.4, 2.5, DZ), "tk_blue")
    a, ha = money_tower("tk", 30, (-4.4, 2.5, DZ + .42), "tiket")
    ped("pb", 2.8, (4.4, 2.5, DZ), "tk_gold")
    f = fr("P13", 37.9)
    b, hb = money_tower("sp", 15, (4.4, 2.5, DZ + .42), "sponsor", f - 2, f + 24)
    for k, (k1, k2) in enumerate((("sp1", "sp1b"), ("sp2", "sp2b"), ("sp3", "sp3b"))):
        bx = C.sponsor_box(f"sb{k}", k1, 1.0, "SPONSOR")
        p0 = (9 + k * 2.2, -3, DZ + 7 + k * 1.5)
        fs = 4 + k * 8
        fly(bx, fs, fs + 16, p0, (4.4, 2.5, DZ + .42 + hb * min(1, (fs + 16) / (f + 24)) + .4))
        key(bx, "scale", 1, (.001,) * 3)
        key(bx, "scale", fs, (1, 1, 1))
        key(bx, "scale", fs + 16, (1, 1, 1))
        key(bx, "scale", fs + 19, (.001,) * 3)
    A["TIKET"] = (-4.4, 2.5, DZ + .42 + ha + .3)
    A["SPONSOR"] = (4.4, 2.5, DZ + .42 + hb + .3)
    data_cam(n, tg=(0, 2.5, DZ + 4.2), d=(27, 25), el=(8, 10), shift=.18)


def p14(n, info, A):
    """'ditambah tenant, merchandise, dan aktivasi brand 3 miliar.' — area kuliner & merchandise: koin muncul
    di atas tenant, stan kaos, booth brand; menara hijau kecil Rp3 M."""
    live_world(info, n)
    pts = {"TENANT": (-44, -24, 5.0), "MERCH": (-14, -14, 4.0), "BRAND": (-26, -2, 8.5)}
    for k, (nm, t) in enumerate((("TENANT", 39.6), ("MERCH", 40.25), ("BRAND", 40.95))):
        x, y, z = pts[nm]
        f = fr("P14", t)
        for j in range(3):
            cn = C.coin(f"cn{k}{j}", 1.4, (x - 2.2 + j * 2.2, y - 1, z + 1.0 + (j % 2) * .8))
            pop(cn, f + j * 2, 1.0)
            fly(cn, f + 26, f + 44, (x - 2.2 + j * 2.2, y - 1, z + 1.0 + (j % 2) * .8), (-24, -36, 6))
            key(cn, "scale", f + 44, (1, 1, 1))
            key(cn, "scale", f + 47, (.001,) * 3)
        A[nm] = (x, y, z + 3.2)
    f3 = fr("P14", 41.6)
    ped("pd", 3.2, (-24, -36, 0), "tn_grn", f3 - 8)
    ob, h = money_tower("tn", 3, (-24, -36, .42), "tenant", f3, f3 + 14, nx=3, ny=2, s=1.6)
    A["TOTAL3"] = (-24, -36, .42 + h + .6)
    cam, tgt = make_camera(lens=20, shift_y=.06)
    tg0, tg1 = (-27, -22, 3), (-26, -24, 3)
    cam_keys(cam, tgt, [(1, orbit(tg0, -64, 36, 58), tg0), (n, orbit(tg1, -74, 38, 54), tg1)])


def p15(n, info, A):
    """'Total potensi pendapatannya 48 miliar rupiah.' — segmen tiket Rp30 M, sponsor Rp15 M, tenant Rp3 M
    jatuh bertumpuk jadi menara Rp48 M, konfeti."""
    stage_set(n, led=(.6, 2.0))
    ped("pd", 3.0, (0, 2.5, DZ), "led_p")
    z = DZ + .42
    f0 = 6
    for k, (nm, v, kind) in enumerate((("tk", 30, "tiket"), ("sp", 15, "sponsor"), ("tn", 3, "tenant"))):
        ob, h = money_tower(nm, v, (0, 2.5, z), kind)
        fly(ob, f0 + k * 12, f0 + k * 12 + 12, (0, 2.5, z + 14), (0, 2.5, z))
        pop(ob, f0 + k * 12, 1.0)
        z += h
    f = fr("P15", 44.5)
    sparkles("sp", (0, 2.5, z), f, 5, 3.0, .45)
    P.confetti("cf", (0, 2, DZ), f, n, 140, (12, 6), 14)
    A["TOTAL"] = (0, 2.5, z + .3)
    data_cam(n, tg=(0, 2.5, DZ + 6.2), d=(36, 34), el=(7, 9), shift=.26)


def p16(n, info, A):
    """'Tapi biaya artis, produksi panggung, venue, keamanan, kru, dan operasional...' — panggung meredup
    merah, 6 ikon biaya muncul satu per satu."""
    stage_set(n, led=(.25, .6), beams=False, crowd_n=200)
    P.point("red", (0, -4, DZ + 9), 9000, (1.0, .22, .2), 4.0)
    times = (47.9, 48.75, 49.7, 50.05, 50.5, 50.85)
    kinds = ("artis", "panggung", "venue", "keamanan", "kru", "operasional")
    names = ("ARTIS", "PANGGUNG", "VENUE", "KEAMANAN", "KRU", "OPS")
    for k, (kind, t, nm) in enumerate(zip(kinds, times, names)):
        col, row = k % 2, k // 2
        x, y = (col - .5) * 6.4 + (row % 2) * .8 - .4, 10.0 - row * 4.6
        f = fr("P16", t)
        ped(f"pd{k}", 1.9, (x, y, DZ), "money_r", f - 3)
        ic = P.cost_icon(f"ic{k}", kind)
        ic.location = (x, y, DZ + .42)
        ic.scale = (1.25,) * 3
        pop(ic, f, 1.25)
        A[nm] = (x, y, DZ + .42 + 3.9)
    data_cam(n, tg=(0, 5.4, DZ + 2.4), d=(31, 29), el=(30, 32), shift=.06)


def p17(n, info, A):
    """'kita estimasikan 32 miliar.' — menara pendapatan Rp48 M (kiri) vs menara biaya merah Rp32 M tumbuh."""
    stage_set(n, led=(.3, .8), crowd_n=200)
    P.point("red", (4, -4, DZ + 9), 5000, (1.0, .25, .2), 3.0)
    ped("pa", 2.8, (-4.4, 2.5, DZ), "tn_grn")
    a, ha = money_tower("om", 48, (-4.4, 2.5, DZ + .42), "sisa")
    ped("pb", 2.8, (4.4, 2.5, DZ), "money_r")
    f = fr("P17", 52.3)
    b, hb = money_tower("by", 32, (4.4, 2.5, DZ + .42), "biaya", f - 4, f + 26)
    A["PENDAPATAN"] = (-4.4, 2.5, DZ + .42 + ha + .3)
    A["BIAYA"] = (4.4, 2.5, DZ + .42 + hb + .3)
    data_cam(n, tg=(0, 2.5, DZ + 6.0), d=(36, 34), el=(7, 9), shift=.2)


def p18(n, info, A):
    """'Artinya, ada potensi sisa operasional sekitar 16 miliar.' — (drop musik) bagian merah Rp32 M lepas &
    terbang, sisa hijau Rp16 M menyala + centang, konfeti & kembang api."""
    ms = stage_set(n, led=(1.2, 4.0))
    ped("pa", 2.8, (0, 2.5, DZ), "tn_grn")
    g, hg = money_tower("sisa", 16, (0, 2.5, DZ + .42), "sisa")
    r, hr = money_tower("ops", 32, (0, 2.5, DZ + .42 + hg), "biaya")
    f0 = fr("P18", 54.3)
    p0 = tuple(r.location)
    key(r, "location", 1, p0)
    key(r, "location", f0, p0)
    key(r, "location", f0 + 8, (p0[0], p0[1], p0[2] + 1.5))
    key(r, "location", f0 + 30, (16, 10, p0[2] + 10))
    key(r, "scale", f0 + 22, (1, 1, 1))
    key(r, "scale", f0 + 30, (.001,) * 3)
    f1 = fr("P18", 57.8)
    for k, s in ((f1, 1), (f1 + 5, 1.12), (f1 + 9, 1)):
        key(g, "scale", k, (s, s, s))
    sparkles("sp", (0, 2.5, DZ + hg + 1.2), f1 + 3, 5, 2.4, .4)
    ck = L.checkmark("ck", (0, 1.2, DZ + .42 + hg + 2.2), 1.2)
    pop(ck, f1 + 8, 1.0)
    P.confetti("cf", (0, 2, DZ), f0 + 4, n, 200, (14, 7), 16)
    P.fireworks("fw", (0, 18, 30), f0 + 2, n, (22, 4, 6), 13, seed=8)
    A["SISA"] = (0, 2.5, DZ + .42 + hg + .3)
    A["OPS"] = (r, (0, 0, hr + .3))
    cam, tgt = make_camera(lens=20, shift_y=.12)
    tg0, tg1 = (0, 2.5, DZ + 6.0), (0, 2.5, DZ + 3.4)
    cam_keys(cam, tgt, [(1, orbit(tg0, -93, 8, 35), tg0), (f0 + 6, orbit(tg0, -92, 8, 34), tg0),
                        (n, orbit(tg1, -88, 11, 24), tg1)])
    _ = ms


def p19(n, info, A):
    """'Ingat ya, ini simulasi, bukan laporan laba resmi Pestapora.' — dokumen laporan di panggung, cap merah
    SIMULASI menghantam."""
    stage_set(n, led=(.4, 1.0), beams=False, crowd_n=200)
    ped("pd", 3.0, (0, 2.5, DZ), "stg_deck2")
    doc = L.report_doc("doc", 2.2).build((0, 2.5, DZ + .42))
    pop(doc, 3, 1.0)
    f = fr("P19", 60.5)
    st = C.stamp("st", "SIMULASI", 1.0)
    fly(st, f, f + 6, (0, -1.2, DZ + 12), (0, .9, DZ + 3.0))
    pop(st, f, 1.0)
    for k, s in ((f + 6, 1.15), (f + 9, 1.0)):
        key(st, "scale", k, (s, s, s))
    A["DOC"] = (0, 2.5, DZ + .42 + 6.9)
    data_cam(n, tg=(0, 2.5, DZ + 3.6), d=(21, 19), el=(9, 11), shift=.08)


def p20(n, info, A):
    """'Ternyata, bisnis festival bukan cuma menjual hiburan,' — pertunjukan penuh: band, konfeti, kembang api,
    kamera naik dari tengah penonton."""
    live_world(info, n, pulse=(1.8, 5.0))
    bd = P.band("bd", (0, P.MAIN[1] - 1), P.DECK_H)
    P.perform(bd, 1, n)
    P.confetti("cf", (0, 40, 2), 10, n, 220, (26, 14), 22)
    P.fireworks("fw", (0, 72, 40), 6, n, (30, 8, 8), 11, seed=9)
    A["SHOW"] = (0, 60, 12)
    cam, tgt = make_camera(lens=20, shift_y=.04)
    cam_keys(cam, tgt, [(1, (-2, 8, 6.5), (0, 56, 12)), (n, (-4, 2, 16), (0, 56, 12))])


def p21(n, info, A):
    """'tapi menjual perhatian puluhan ribu orang kepada brand.' — token mata naik dari lautan penonton lalu
    terbang ke booth sponsor; backdrop booth makin terang."""
    live_world(info, n)
    bb = info["booths"][:2]
    rnd = random.Random(21)
    f0 = fr("P21", 68.8)
    for k in range(18):
        src = (rnd.uniform(-24, 24), rnd.uniform(14, 44), 3.0)
        dst_b = bb[k % 2]
        dst = (dst_b[0] + rnd.uniform(-2, 2), dst_b[1] + 2, 6 + rnd.uniform(-1, 1))
        e = C.eye_token(f"e{k}", 2.8, src)
        e.rotation_euler = (0, 0, 0)
        fs = f0 + (k % 9) * 4
        mid = (src[0], src[1], 11)
        key(e, "location", 1, src)
        key(e, "location", fs, src)
        key(e, "location", fs + 12, mid)
        key(e, "location", fs + 36, dst)
        key(e, "scale", 1, (.001,) * 3)
        key(e, "scale", fs, (.001,) * 3)
        key(e, "scale", fs + 5, (1, 1, 1))
        key(e, "scale", fs + 34, (1, 1, 1))
        key(e, "scale", fs + 38, (.001,) * 3)
    for k in range(2):
        ob = bpy.data.objects.get(f"bb{k}_g")
        if ob:
            emission_ramp(ob.data.materials[0], [(1, 1.0), (f0 + 30, 1.0), (f0 + 60, 6.0)])
    A["CROWD"] = (0, 30, 5)
    A["B1"] = (bb[0][0], bb[0][1] + 3.4, 7.6)
    A["B2"] = (bb[1][0], bb[1][1] + 3.4, 7.6)
    cam, tgt = make_camera(lens=18, shift_y=.04)
    tg0, tg1 = (0, 12, 4), (0, 10, 4)
    cam_keys(cam, tgt, [(1, orbit(tg0, -96, 30, 62), tg0), (n, orbit(tg1, -88, 28, 56), tg1)])


def p22(n, info, A):
    """'Menurut kalian, ... lebih menarik, atau justru terlalu berisiko?' — jungkat-jungkit di panggung:
    kiri panah hijau (menarik), kanan tanda peringatan (berisiko), berayun lalu menggantung seimbang + '?'."""
    stage_set(n, led=(.5, 1.6))
    mb = W.MB("fulc")
    mb.prism_y([(-1.4, 0), (1.4, 0), (0, 2.6)], -1.0, 1.0, "stg_truss2")
    mb.build((0, 2.5, DZ))
    pv = bpy.data.objects.new("pivot", None)
    lp._link(pv)
    pv.location = (0, 2.5, DZ + 2.7)
    pl = W.MB("plank")
    L.rbox(pl, -8.5, -1.2, -.25, 8.5, 1.2, .2, "tn_wood", c=.08)
    pl.cyl(-7, 0, .2, .4, 1.4, "tn_grn", n=16)
    pl.cyl(7, 0, .2, .4, 1.4, "money_r", n=16)
    po = pl.build()
    po.parent = pv
    ar = C.arrow_up("ar", 1.5, "chart_g")
    ar.parent = pv
    ar.location = (-7, 0, .4)
    cns = []
    for k in range(3):
        cn = C.coin(f"cn{k}", .9, (-7 + (k - 1) * 1.6, -.9, 1.0 + (k % 2) * .5))
        cn.parent = pv
        cns.append(cn)
    wn = P.warn_sign("wn", 1.4)
    wn.parent = pv
    wn.location = (7, 0, .4)
    f1, f2 = fr("P22", 74.5), fr("P22", 76.25)
    key(pv, "rotation_euler", 1, (0, 0, 0))
    key(pv, "rotation_euler", f1 - 4, (0, 0, 0))
    key(pv, "rotation_euler", f1 + 10, (0, .2, 0))         # kiri turun (menarik berat)
    key(pv, "rotation_euler", f2 - 6, (0, .16, 0))
    key(pv, "rotation_euler", f2 + 10, (0, -.2, 0))        # kanan turun (berisiko berat)
    key(pv, "rotation_euler", min(n, f2 + 30), (0, .04, 0))
    pop(ar, f1 - 2, 1.0)
    pop(wn, f2 - 4, 1.0)
    for k, cn in enumerate(cns):
        pop(cn, f1 + k * 2, 1.0)
    q = qmark("q", (0, 2.0, DZ + 9.0), 1.3, "tk_gold", f2 + 12)
    A["MENARIK"] = (-7, 2.5, DZ + 7.5)
    A["RISIKO"] = (7, 2.5, DZ + 7.0)
    A["Q"] = (0, 2.0, DZ + 13)
    data_cam(n, tg=(0, 2.5, DZ + 4.4), d=(30, 28), el=(9, 11), shift=.06)
    _ = q


def p23(n, info, A):
    """CTA: 'Tulis pendapat kalian di kolom komentar, dan follow untuk bedah bisnis lainnya.' — festival malam
    dari udara, bianglala berputar, kembang api besar."""
    live_world(info, n)
    P.fireworks("fw", (0, 80, 60), 4, n, (60, 30, 12), 7, seed=23)
    A["FEST"] = (0, 62, 30)
    cam, tgt = make_camera(lens=20, shift_y=.1)
    tg0, tg1 = (0, 60, 18), (0, 70, 22)
    cam_keys(cam, tgt, [(1, orbit(tg0, -100, 20, 130), tg0), (n, orbit(tg1, -90, 30, 210), tg1)])


SCENES = {f"P{k:02d}": fn for k, fn in enumerate(
    (p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22,
     p23), 1)}
WORLD = {"P01", "P02", "P04", "P05", "P06", "P07", "P10", "P12", "P14", "P20", "P21", "P23"}


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
    P.setup_fest_light()
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, n
    info = {}
    if args.scene in WORLD:
        dens = {"P07": .6, "P10": .6, "P04": .5}.get(args.scene, 1.0)
        info = P.build_fest(people_density=dens)
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
