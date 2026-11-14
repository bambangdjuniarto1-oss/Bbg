"""25 adegan video "Bedah Bisnis: Close The Door" (timeline mengikuti VO hasil humanize_vo.py, ±107,8 dtk).

  python3 render/scenes_ctd.py -- --scene C01 --out OUT/C01 [--res 720x1280] [--samples 4] [--frames a-b]

Isi VO: hook (25 jt subscriber, miliaran views, tamu pejabat & artis) -> biaya & uang per bulan? ->
Close The Door = perusahaan media digital -> 43 jt views / 28 hari -> simulasi: RPM Rp4.000, 41 jt views
= Rp165 jt; 2 sponsor x Rp100 jt; 3.000 member x Rp30rb = Rp90 jt -> tambahan Rp290 jt, total Rp455 jt ->
biaya: 18 orang tim, host, tamu, transport, studio, alat, marketing = Rp388 jt -> sisa Rp67 jt -> bukan
laporan asli -> pelajaran: audience x kepintaran monetisasi -> CTA. Waktu (detik) = timeline video,
sama dengan render/scenes/ctd_words.json.
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
from scenes import key, make_camera, cam_keys, orbit  # noqa: E402
from scenes_laundry import pop, grow_z, fly, emission_ramp, _anchor_pos  # noqa: E402
from scenes_amdk import tower, sparkles  # noqa: E402

FPS = 30
TIMELINE = [("C01", 0.00), ("C02", 2.82), ("C03", 4.00), ("C04", 7.73), ("C05", 11.91), ("C06", 15.87),
            ("C07", 19.86), ("C08", 25.93), ("C09", 32.34), ("C10", 34.05), ("C11", 37.01), ("C12", 42.82),
            ("C13", 46.52), ("C14", 49.69), ("C15", 55.73), ("C16", 60.11), ("C17", 66.00), ("C18", 68.07),
            ("C19", 70.35), ("C20", 75.93), ("C21", 81.17), ("C22", 85.63), ("C23", 89.76), ("C24", 95.50),
            ("C25", 103.32)]
END_T = 107.80
LH = .29 * .8                     # tinggi 1 lapis menara uang (s=.8)
JT = 10.0                         # 1 lapis = Rp10 juta


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
def rooftop(w=36.0, d=28.0, seed=2, base=-58.0):
    """atap gedung tinggi (panggung data) + kota di bawahnya sejauh mata memandang."""
    rnd = random.Random(seed)
    mb = W.MB("roof")
    mb.box(-w / 2, -d / 2, -3, w / 2, d / 2, 0, "ct_con")
    for k in range(int(w / 3)):
        x = -w / 2 + k * 3
        mb.box(x - .03, -d / 2, 0, x + .03, d / 2, .01, "ct_con2")
    for (a, b, c, e) in ((-w / 2, -d / 2, w / 2, -d / 2 + .4), (-w / 2, d / 2 - .4, w / 2, d / 2),
                         (-w / 2, -d / 2, -w / 2 + .4, d / 2), (w / 2 - .4, -d / 2, w / 2, d / 2)):
        mb.box(a, b, 0, c, e, .8, "ct_con2")
        mb.box(a, b, .8, c, e, .9, "st_metal")
    for x, y in ((-w / 2 + 3, d / 2 - 3), (w / 2 - 3.5, d / 2 - 3)):
        L.rbox(mb, x - 1.4, y - 1.0, 0, x + 1.4, y + 1.0, 1.6, "c_grey", c=.15)
        mb.cyl(x, y, 1.6, 1.7, .8, "st_metal_dk", n=12)
    mb.box(-w / 2 - 1, -d / 2 - 1, base, w / 2 + 1, d / 2 + 1, -3, "ct_glass3")        # badan gedung
    mb.build()
    g = W.MB("roof_city")
    g.box(-600, -600, base - 1, 600, 600, base, "ct_ground")
    for k in range(-6, 7):
        g.box(-600, k * 44 - 4.5, base, 600, k * 44 + 4.5, base + .05, "ct_road")
        g.box(k * 44 - 4.5, -600, base, k * 44 + 4.5, 600, base + .06, "ct_road")
    g.build()
    sk = W.MB("roof_towers")
    for i in range(-7, 8):
        for j in range(-4, 9):
            cx, cy = i * 22 + rnd.uniform(-4, 4), j * 22 + rnd.uniform(-4, 4)
            if cy < 38 and abs(cx) < 110:                   # depan & samping dekat dibiarkan terbuka
                continue
            dist = math.hypot(cx, cy)
            hh = rnd.uniform(.4, 1.0) * max(30, 120 - dist * .35)
            ob_top = C.tower(sk, cx, cy, rnd.uniform(9, 15), rnd.uniform(9, 15), hh, rnd)
            _ = ob_top
    ob = sk.build()
    ob.location.z = base


def ped(name, r, loc, key_="st_chair2", f=None):
    p = M.pedestal(name, r, key_).build(loc)
    if f is not None:
        pop(p, f, 1.0)
    return p


def mtower(name, juta, loc, key_="money_g", f0=None, f1=None):
    """menara uang `juta` (1 lapis = Rp10 jt). Return (objek, tinggi)."""
    layers = max(1, int(round(juta / JT)))
    ob = tower(name, layers, loc, 2, 2, key_=key_, s=.8)
    if f0 is not None:
        grow_z(ob, f0, f1 or f0 + 30)
    return ob, layers * LH


def qmark(name, loc, s=1.0, key_="ct_acc", f=None):
    q = H.text(name, "?", 2.6 * s, key_, depth=.4 * s, loc=loc, emission=.4)
    if f is not None:
        pop(q, f, 1.0)
    return q


def tag(name, body, loc, s=1.0, key_="lw_yellow", f=None):
    t = L.price_tag(name, body, loc, s, key_)
    if f is not None:
        pop(t, f, 1.0)
    return t


def bob(ob, f0, f1, amp=.25, period=40):
    z0 = ob.location.z
    for f in range(f0, f1 + 1, period // 2):
        ob.location.z = z0 + (amp if ((f - f0) // (period // 2)) % 2 else 0)
        ob.keyframe_insert("location", frame=f)


def glow_line(name, p0, p1, key_="led_b", t=.12, f=None, em=3.0):
    """garis bercahaya p0 -> p1 (jaringan); muncul memanjang dari p0."""
    mb = W.MB(name)
    d = math.dist(p0, p1)
    mb.box(0, -t / 2, -t / 2, d, t / 2, t / 2, key_)
    ob = mb.build(p0)
    ob.data.materials[0] = lp.mat(key_, emission=em)
    dx, dy, dz = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
    ob.rotation_euler = (0, -math.atan2(dz, math.hypot(dx, dy)), math.atan2(dy, dx))
    if f is not None:
        key(ob, "scale", 1, (.001, 1, 1))
        key(ob, "scale", f, (.001, 1, 1))
        key(ob, "scale", f + 10, (1, 1, 1))
    return ob


def studio_cam(cam, tgt, n, tg=(0, .3, 2.0), az0=-104, az1=-96, el=17, d0=22, d1=20):
    cam_keys(cam, tgt, [(1, orbit(tg, az0, el, d0), tg), (n, orbit(tg, az1, el + 1, d1), tg)])


def host_talk(st, n, seed=1, who=("host",)):
    for k, nm in enumerate(who):
        if nm in st:
            C.talk(st[nm], 1, n, seed + k)


# ------------------------------------------------------------------ adegan
def c01(n, info, A):
    """'Satu channel YouTube punya 25 juta subscriber,' — HP raksasa di plaza kota, plakat emas muncul."""
    ph = C.phone_channel("ph", 2.2)
    ph.location = (-9, -13, .16)
    ph.rotation_euler.z = .22
    pop(ph, 3, 1.0)
    p = ped("pd", 1.6, (-1.5, -15.5, .16), "st_chair2", fr("C01", 1.2))
    pq = C.play_plaque("pq", 1.0)
    pq.location = (-1.5, -15.5, .58)
    pq.rotation_euler.z = -.15
    pop(pq, fr("C01", 1.3), 1.0)
    sparkles("sp", (-1.5, -15.5, 2.4), fr("C01", 1.6), 4, 1.6, .35)
    _ = p
    A["SUBS"] = (-9, -13.2, 13.9)
    A["PLAKAT"] = (-1.5, -15.5, 3.7)
    C.city_traffic(n, hwy=info.get("hwy"))
    cam, tgt = make_camera(lens=20, shift_y=.12)
    tg = (-6, -13, 6.0)
    cam_keys(cam, tgt, [(1, orbit(tg, -100, 6, 20), tg), (n, orbit(tg, -86, 13, 30), (tg[0], tg[1], 7.5))])


def c02(n, info, A):
    """'miliaran views,' — terbang di atas kota, token 'views' bermunculan di atas gedung."""
    rnd = random.Random(4)
    for k in range(12):
        x, y = rnd.uniform(-60, 60), rnd.uniform(-30, 90)
        e = C.eye_token(f"ey{k}", 8.0, (x, y, rnd.uniform(78, 104)))
        e.rotation_euler.z = rnd.uniform(-.3, .3)
        pop(e, 1 + k * 2, 1.0)
        bob(e, 2, n, 1.0, 30)
    A["VIEWS"] = (0, 30, 112)
    C.city_traffic(n, hwy=info.get("hwy"))
    cam, tgt = make_camera(lens=22, shift_y=.1)
    cam_keys(cam, tgt, [(1, (-30, -190, 125), (0, 25, 66)), (n, (-18, -150, 118), (0, 30, 68))])


def c03(n, info, A):
    """'dan bisa mengundang pejabat sampai artis papan atas.' — studio podcast: host & tamu pejabat,
    pintu terbuka, artis berkacamata hitam masuk."""
    st = C.studio("st", guest="pejabat")
    host_talk(st, n, 3, ("host", "guest"))
    f_open = fr("C03", 5.0)
    C.open_door(st["door"], f_open, f_open + 12)
    ar = C.person("artis", "artis", (C.DOOR_X, 6.4, 0), math.pi)
    dx = C.DOOR_X
    L.walk_to(ar, [(dx, 7.2), (dx, 4.4), (dx + 1.2, 2.6), (dx + 4.6, -.6)], f_open + 6, speed=2.2)
    L.pose(ar, "wave", fr("C03", 6.9))
    A["PEJABAT"] = st["anchors"]["GUEST"]
    A["ARTIS"] = (ar["body"], (0, 0, 2.9))
    cam, tgt = make_camera(lens=20, shift_y=.1)
    studio_cam(cam, tgt, n, tg=(0, 1.2, 2.2), az0=-108, az1=-98, el=16, d0=21, d1=19)


def c04(n, info, A):
    """'Tapi pernah kepikiran nggak, berapa sebenarnya biaya untuk menjalankan bisnis sebesar ini?' —
    studio, label harga 'Rp ?' bermunculan di kamera, lampu, mic, kursi; tanda tanya besar."""
    st = C.studio("st", guest="artis")
    host_talk(st, n, 4, ("host", "guest"))
    f0 = fr("C04", 9.62)
    spots = [(-5.6, -3.6, 3.3), (6.2, -1.2, 3.8), (5.4, -3.4, 3.1), (-6.3, -1.0, 3.8), (-1.75, .35, 2.6),
             (-5.4, 6.0, 5.5)]
    for k, p in enumerate(spots):
        tag(f"tg{k}", "Rp ?", p, .62, "lw_yellow", f0 + k * 5)
    qmark("q", (0, .8, 3.0), 1.0, "ct_acc", fr("C04", 10.9))
    A["BIAYA"] = (0, .8, 6.0)
    cam, tgt = make_camera(lens=20, shift_y=.1)
    studio_cam(cam, tgt, n, tg=(0, .5, 2.3), az0=-96, az1=-104, el=19, d0=21, d1=20)


def c05(n, info, A):
    """'Dan berapa uang yang bisa dihasilkan tiap bulan?' — atap gedung: menara uang tumbuh + tanda tanya +
    kalender 1 bulan."""
    rooftop()
    ped("pd", 2.2, (0, 0, 0))
    ob, h = mtower("m", 120, (0, 0, .42), "money_g", fr("C05", 12.38), fr("C05", 13.6))
    qmark("q", (0, -.2, .42 + h + .6), .9, "ct_acc", fr("C05", 13.4))
    cal = K.calendar("cal", "30", (4.0, -1.5, 0), 1.6)
    pop(cal, fr("C05", 14.2), 1.0)
    A["UANG"] = (0, 0, .42 + h + .4)
    A["BULAN"] = (4.0, -1.5, 3.0)
    cam, tgt = make_camera(lens=22, shift_y=.1)
    tg = (1.6, 0, 2.6)
    cam_keys(cam, tgt, [(1, orbit(tg, -96, 12, 16), tg), (n, orbit(tg, -88, 15, 14.5), tg)])


def c06(n, info, A):
    """'Kita bicara Close The Door milik Deddy Corbuzier.' — gedung studio di tengah kota; pintu raksasa
    yang terbuka menutup tepat di kata 'Door'."""
    hq = info["hq"]
    f_close = fr("C06", 17.2)
    for d, ang in zip(hq["doors"], (1.55, -1.55)):
        key(d, "rotation_euler", 1, (0, 0, ang))
        key(d, "rotation_euler", f_close, (0, 0, ang))
        key(d, "rotation_euler", f_close + 7, (0, 0, -.04 * math.copysign(1, ang)))
        key(d, "rotation_euler", f_close + 10, (0, 0, 0))
    emission_ramp(hq["glow"].data.materials[0], [(1, 6), (f_close + 6, 6), (f_close + 14, 10)])
    C.city_traffic(n, hwy=info.get("hwy"))
    A["DOOR"] = (0, 20.5, 7.4)
    A["HQ"] = (0, 30, 27)
    cam, tgt = make_camera(lens=20, shift_y=.1)
    tg0, tg1 = (0, 20.5, 10.0), (0, 20.5, 6.0)
    cam_keys(cam, tgt, [(1, orbit(tg0, -92, 16, 66), tg0), (n, orbit(tg1, -88, 9, 31), tg1)])


def c07(n, info, A):
    """'Bukan lagi sekadar podcast, tapi perusahaan media digital dengan tim produksi, jaringan kreator, dan
    distribusi konten.' — studio mini di tengah; tim produksi, jaringan kreator, layar distribusi muncul
    dengan garis cahaya."""
    rooftop()
    ped("pc", 2.6, (0, 1.5, 0))
    core = C.cost_icon("core", "studio")
    core.location = (0, 1.5, .42)
    core.scale = (1.6, 1.6, 1.6)
    pop(core, 3, 1.6)
    cz = 2.2
    # tim produksi (kiri)
    ft = fr("C07", 22.45)
    for k, lk in enumerate(("kru1", "kru2", "kru3", "kru4")):
        p = C.person(f"tm{k}", lk, (-6.2 + (k % 2) * 1.5, -1.6 + (k // 2) * 1.8, 0), .3,
                     extra=("headset",) if k % 2 == 0 else ())
        pop(p["body"], ft + k * 3, C.CH_S)
    cam1 = C.tripod_cam("tc", (-3.6, -3.0, 0), (-6, 0, 1.5))
    pop(cam1, ft + 4, 1.0)
    glow_line("gl0", (0, 1.5, cz), (-5.6, -.6, 2.2), "led_y", f=ft)
    # jaringan kreator (atas/belakang): 6 HP kecil + garis
    fk = fr("C07", 23.47)
    for k in range(6):
        a = math.radians(30 + k * 24)
        x, y = math.cos(a) * 6.0, 5.5 + math.sin(a) * 3.5
        ph = C.phone_channel(f"cr{k}", .45)
        ph.location = (x, y, 0)
        pop(ph, fk + k * 2, 1.0)
        glow_line(f"gk{k}", (0, 1.5, cz + 1.4), (x, y, 1.6), "led_b", f=fk + k * 2)
    # distribusi konten (kanan): layar TV, laptop, HP
    fd = fr("C07", 24.42)
    for k, (x, y) in enumerate(((5.4, -2.2), (6.6, .8), (4.4, 2.2))):
        bb = C.billboard(f"sc{k}", (x, y), 2.2, 1.35, ("led_r", "led_b", "led_y")[k], -.25, 1.6, 1.2)
        pop(bb, fd + k * 3, 1.0)
        mb = W.MB(f"st{k}")
        mb.box(x - .1, y - .1, 0, x + .1, y + .1, 1.2, "st_metal_dk")
        stand = mb.build()
        pop(stand, fd + k * 3, 1.0)
        glow_line(f"gd{k}", (0, 1.5, cz), (x, y, 2.0), "led_r", f=fd + k * 3)
    A["PRODUKSI"] = (-5.6, -.8, 3.2)
    A["KREATOR"] = (0, 9.0, 3.4)
    A["DISTRIBUSI"] = (5.6, -.6, 3.4)
    A["MEDIA"] = (0, 1.5, 5.0)
    cam, tgt = make_camera(lens=18, shift_y=.08)
    tg = (0, 1.5, 2.2)
    cam_keys(cam, tgt, [(1, orbit(tg, -95, 22, 23), tg), (n, orbit(tg, -88, 25, 22), tg)])


def c08(n, info, A):
    """'Di salah satu periode pengamatan, kanal ini dapat lebih dari 43 juta views dalam 28 hari.' —
    kalender 28 hari + grafik batang 4 minggu tumbuh, token views melayang."""
    rooftop()
    cal = K.calendar("cal", "28", (-4.4, -1.0, 0), 1.8)
    pop(cal, fr("C08", 26.5), 1.0)
    f0 = fr("C08", 28.29)
    hs = (2.6, 4.6, 6.6, 8.8)
    for k, h in enumerate(hs):
        b = C.bar3d(f"b{k}", h, (-.2 + k * 2.1, 1.0, 0), 1.5, "chart_b" if k < 3 else "chart_g")
        grow_z(b, f0 + k * 8, f0 + k * 8 + 20)
    rnd = random.Random(8)
    for k in range(7):
        e = C.eye_token(f"ey{k}", 1.0, (rnd.uniform(-1, 7.5), rnd.uniform(-1, 1), rnd.uniform(9.5, 11.5)))
        pop(e, f0 + 20 + k * 4, 1.0)
        bob(e, f0 + 24 + k * 4, n, .4, 30)
    A["VIEWS"] = (6.1, 1.0, 9.2)
    A["HARI"] = (-4.4, -1.0, 3.6)
    cam, tgt = make_camera(lens=20, shift_y=.12)
    tg = (1.0, .5, 4.4)
    cam_keys(cam, tgt, [(1, orbit(tg, -98, 10, 24), tg), (n, orbit(tg, -90, 13, 22), tg)])


def c09(n, info, A):
    """'Sekarang kita simulasikan ya.' — kalkulator besar berdiri + cap SIMULASI."""
    rooftop()
    ped("pd", 2.4, (0, 0, 0))
    calc = H.calculator("calc", 1.4).build((0, .4, 1.6))
    calc.rotation_euler.x = math.radians(78)
    pop(calc, 3, 1.0)
    sm = C.stamp("sm", "SIMULASI", .7)
    sm.location = (0, -1.6, 5.6)
    sm.rotation_euler.y = .12
    pop(sm, fr("C09", 33.1), 1.0)
    A["SIM"] = (0, -1.6, 6.8)
    cam, tgt = make_camera(lens=22, shift_y=.1)
    tg = (0, 0, 3.2)
    cam_keys(cam, tgt, [(1, orbit(tg, -94, 10, 17), tg), (n, orbit(tg, -88, 12, 15), tg)])


def c10(n, info, A):
    """'Anggap pendapatan iklan per 1.000 views itu Rp4.000.' — kubus 1.000 views masuk mesin, keluar
    uang Rp4.000."""
    rooftop()
    mm = C.money_machine("mm", 1.0)
    mm["body"].location = (0, 2.0, 0)
    vc = C.view_cube("vc", 1.0)
    fin = fr("C10", 35.38)
    fly(vc, fin + 8, fin + 26, (-6.5, 0, 0), (-1.2, 2.0, 5.4), arc=3.0)
    pop(vc, fr("C10", 34.4), 1.0)
    key(vc, "scale", fin + 22, (1, 1, 1))
    key(vc, "scale", fin + 28, (.001, .001, .001))
    emission_ramp(lp.mat("mach_acc", emission=3), [(1, 3), (fin + 24, 3), (fin + 28, 9), (fin + 40, 3)])
    fo = fr("C10", 36.17)
    ms = L.money_stack("ms", 8, 1.6).build((3.2, 2.0, .35))
    pop(ms, fo, 1.0)
    tag("tg", "Rp4.000", (4.6, .4, 2.2), .8, "lw_yellow", fo + 4)
    A["VIEWS"] = (vc, (0, 0, 2.2))
    A["RP"] = (4.4, .4, 3.1)
    cam, tgt = make_camera(lens=20, shift_y=.12)
    tg = (.9, 1.0, 2.4)
    cam_keys(cam, tgt, [(1, orbit(tg, -96, 14, 18), tg), (n, orbit(tg, -88, 16, 16.5), tg)])


def c11(n, info, A):
    """'Dari sekitar 41 juta views video panjang, iklannya bisa mencapai Rp165 juta.' — layar video panjang,
    tumpukan 41 kubus views, menara uang Rp165 jt tumbuh."""
    rooftop()
    tv = C.billboard("tv", (-5.5, 3.5), 7.2, 4.05, "tv_scr", 0.15, 1.4, 1.6)
    mb = W.MB("tvst")
    mb.box(-5.7, 3.4, 0, -5.3, 3.8, 1.6, "st_metal_dk")
    mb.build()
    pl = W.MB("tvplay")
    pl.poly([(-6.2, 2.9, 2.9), (-4.7, 2.9, 3.6), (-6.2, 2.9, 4.3)], [(0, 1, 2)], "play_w")
    pl.build().data.materials[0] = lp.mat("play_w", emission=2)
    _ = tv
    f0 = fr("C11", 37.48)
    k = 0
    for r in range(4):
        for c in range(6):
            if k >= 21:
                break
            cube = C.view_cube(f"vc{k}", .55, (-7.8 + c * 1.05, -1.4 + (r % 2) * .5, r * 1.0), label=None)
            pop(cube, f0 + k, 1.0)
            k += 1
    ped("pd", 2.2, (4.8, 0, 0))
    fg = fr("C11", 40.22)
    ob, h = mtower("m", 165, (4.8, 0, .42), "money_g", fg, fr("C11", 41.9))
    sparkles("sp", (4.8, 0, h + .8), fr("C11", 42.0), 4, 1.8, .35)
    A["VIEWS"] = (-5.0, -1.2, 4.6)
    A["IKLAN"] = (4.8, 0, .42 + h + .3)
    cam, tgt = make_camera(lens=20, shift_y=.12)
    tg = (-.5, 0, 3.0)
    cam_keys(cam, tgt, [(1, orbit(tg, -95, 11, 25), tg), (n, orbit(tg, -88, 13, 23), tg)])


def c12(n, info, A):
    """'Itu baru dari YouTube, belum sponsor dan sumber lainnya.' — menara iklan YouTube + 2 alas kosong
    bertanda tanya."""
    rooftop()
    ped("p0", 2.0, (-5.2, 0, 0))
    ob, h = mtower("m", 165, (-5.2, 0, .42), "money_g")
    for k, (x, t) in enumerate(((1.0, 44.2), (6.4, 44.88))):
        ped(f"p{k + 1}", 1.8, (x, 0, 0), "st_panel", fr("C12", t - .2))
        qmark(f"q{k}", (x, -.2, .8), .9, "lw_yellow" if k == 0 else "member", fr("C12", t))
    A["YT"] = (-5.2, 0, .42 + h + .3)
    A["SPONSOR"] = (1.0, 0, 3.6)
    A["LAIN"] = (6.4, 0, 3.6)
    cam, tgt = make_camera(lens=20, shift_y=.12)
    tg = (.6, 0, 2.4)
    cam_keys(cam, tgt, [(1, orbit(tg, -93, 12, 23), tg), (n, orbit(tg, -87, 14, 21), tg)])


def c13(n, info, A):
    """'Tambahkan 2 kerja sama sponsor, masing-masing Rp100 juta.' — kotak sponsor di meja podcast,
    2 menara Rp100 jt naik di kiri-kanan."""
    st = C.studio("st", guest="artis")
    host_talk(st, n, 13, ("host", "guest"))
    fs = fr("C13", 47.17)
    for k, (x, kk) in enumerate(((-.7, "sp_a"), (.7, "sp_b"))):
        sb = C.sponsor_box(f"sb{k}", kk, .55)
        sb.location = (x, .1, C.TABLE_Z)
        pop(sb, fs + k * 6, 1.0)
    fm = fr("C13", 48.73)
    for k, x in enumerate((-4.6, 4.6)):
        ped(f"pd{k}", 1.7, (x, -2.6, 0), "st_chair2", fm - 6)
        mtower(f"m{k}", 100, (x, -2.6, .42), "money_red", fm + k * 3, fm + k * 3 + 16)
        A[f"S{k}"] = (x, -2.6, .42 + 10 * LH + .3)
    cam, tgt = make_camera(lens=20, shift_y=.1)
    studio_cam(cam, tgt, n, tg=(0, -.6, 2.0), az0=-96, az1=-90, el=16, d0=23, d1=22)


def c14(n, info, A):
    """'Lalu 3.000 anggota membership yang bayar rata-rata Rp30.000 per bulan.' — barisan penonton mini
    memegang kartu emas (1 figur = 10 member) + kartu member raksasa."""
    rooftop()
    f0 = fr("C14", 50.08)
    rows = 10
    for r in range(rows):
        cr = C.crowd(f"cr{r}", 30, -15, 1.0 + r * 1.15, 15, 2.1 + r * 1.15, seed=r, s=.9, card_frac=.8)
        pop(cr, f0 + r * 3, 1.0)
    mc = C.member_card("mc", 1.3)
    mc.location = (0, -4.5, .3)
    mc.rotation_euler.x = math.radians(-8)
    pop(mc, fr("C14", 51.1), 1.0)
    fc = fr("C14", 53.04)
    for k in range(5):
        cn = C.coin(f"cn{k}", 1.0)
        fly(cn, fc + k * 5, fc + k * 5 + 22, (-3 + k * 1.5, -4.0, 2.5), (-3 + k * 1.5, -4.0, 6.0))
        pop(cn, fc + k * 5, 1.0)
    A["MEMBER"] = (0, 6.0, 2.6)
    A["KARTU"] = (0, -4.5, 3.0)
    cam, tgt = make_camera(lens=20, shift_y=.1)
    tg = (0, 2.0, 1.8)
    cam_keys(cam, tgt, [(1, orbit(tg, -96, 22, 30), tg), (n, orbit(tg, -88, 26, 28), tg)])


def c15(n, info, A):
    """'Berarti tambahan omzet Rp290 juta.' — menara sponsor Rp200 jt + member Rp90 jt; menara member
    terbang naik ke atas menara sponsor jadi Rp290 jt."""
    rooftop()
    ped("pa", 2.0, (-2.4, 0, 0))
    a, ha = mtower("sp", 200, (-2.4, 0, .42), "money_red")
    ped("pb", 1.8, (4.2, 0, 0))
    b, hb = mtower("mb", 90, (4.2, 0, .42), "member")
    f0 = fr("C15", 56.69)
    top = .42 + ha
    key(b, "location", 1, (4.2, 0, .42))
    key(b, "location", f0, (4.2, 0, .42))
    key(b, "location", f0 + 10, (4.2, 0, top + 1.5))
    key(b, "location", f0 + 22, (-2.4, 0, top + .4))
    key(b, "location", f0 + 26, (-2.4, 0, top))
    sparkles("sp", (-2.4, 0, top + hb), f0 + 26, 4, 1.8, .35)
    A["SP"] = (-2.4, 0, top + .3)
    A["MB"] = (b, (0, 0, hb + .3))
    A["TOTAL"] = (-2.4, 0, top + hb + .3)
    cam, tgt = make_camera(lens=20, shift_y=.12)
    tg = (.8, 0, 3.6)
    cam_keys(cam, tgt, [(1, orbit(tg, -94, 10, 25), tg), (n, orbit(tg, -88, 12, 24), tg)])


def c16(n, info, A):
    """'Total omzet simulasinya sekitar Rp455 juta sebulan.' — tiga segmen (iklan hijau, sponsor merah,
    member ungu) jatuh bertumpuk jadi menara Rp455 jt."""
    rooftop()
    ped("pd", 2.2, (0, 0, 0))
    z = .42
    f0 = 6
    for k, (nm, v, col) in enumerate((("yt", 165, "money_g"), ("sp", 200, "money_red"), ("mb", 90, "member"))):
        ob, h = mtower(nm, v, (0, 0, z), col)
        fly(ob, f0 + k * 12, f0 + k * 12 + 12, (0, 0, z + 12), (0, 0, z))
        pop(ob, f0 + k * 12, 1.0)
        z += h
    sparkles("sp", (0, 0, z), fr("C16", 62.1), 5, 2.2, .4)
    A["TOTAL"] = (0, 0, z + .3)
    cam, tgt = make_camera(lens=20, shift_y=.26)
    tg = (0, 0, 6.0)
    cam_keys(cam, tgt, [(1, orbit(tg, -95, 8, 34), tg), (n, orbit(tg, -88, 10, 32), tg)])


def c17(n, info, A):
    """'Tapi menjalankan perusahaan media nggak murah.' — studio berubah merah: label biaya merah
    bermunculan di peralatan, uang beterbangan keluar."""
    st = C.studio("st", guest="pejabat")
    host_talk(st, n, 17, ("host", "guest"))
    li = bpy.data.lights.new("red", "AREA")
    li.size = 10
    li.color = (1.0, .25, .2)
    lo = bpy.data.objects.new("red", li)
    lp._link(lo)
    lo.location = (0, -2, 7.5)
    f0 = fr("C17", 67.13)
    li.energy = 0
    li.keyframe_insert("energy", frame=1)
    li.keyframe_insert("energy", frame=f0)
    li.energy = 3000
    li.keyframe_insert("energy", frame=f0 + 8)
    for k, p in enumerate(((-5.6, -3.6, 3.4), (6.2, -1.2, 3.9), (5.4, -3.4, 3.2), (0, .4, 2.4))):
        tag(f"t{k}", "Rp", p, .7, "led_r", f0 + 2 + k * 3)
    for k in range(6):
        ms = L.money_stack(f"ms{k}", 4, .9).build((0, .4, 1.2))
        a = k * math.pi / 3
        fly(ms, f0 + k * 2, f0 + k * 2 + 26, (0, .4, 1.4), (math.cos(a) * 6, .4 + math.sin(a) * 2, 7.5 + k * .3), arc=2)
        key(ms, "rotation_euler", f0, (0, 0, 0))
        key(ms, "rotation_euler", f0 + 26, (1.2, .6, a))
    A["BIAYA"] = (0, .4, 5.4)
    cam, tgt = make_camera(lens=20, shift_y=.1)
    studio_cam(cam, tgt, n, tg=(0, .5, 2.3), az0=-92, az1=-90, el=17, d0=21, d1=18)


def c18(n, info, A):
    """'Ada 18 orang tim produksi dan operasional,' — 18 kru berbaris 3 x 6 di depan meja podcast."""
    st = C.studio("st", guest=None, host=False)
    _ = st
    f0 = fr("C18", 68.25)
    looks = C.KRU
    k = 0
    for r in range(3):
        for c in range(6):
            x = -4.6 + c * 1.85 + (r % 2) * .4
            y = -2.2 - r * 1.6
            p = C.person(f"k{k}", looks[(k + r) % 6], (x, y, 0), 0, extra=("headset",) if k % 3 == 0 else ())
            pop(p["body"], f0 + k * 2, C.CH_S)
            k += 1
    A["TIM"] = (0, -3.8, 3.4)
    cam, tgt = make_camera(lens=20, shift_y=.12)
    studio_cam(cam, tgt, n, tg=(.2, -1.6, 1.8), az0=-93, az1=-90, el=15, d0=22, d1=20)


COSTS = [("host", 70.35, "HOST"), ("tamu", 71.29, "TAMU"), ("transport", 72.53, "TRANSPORT"),
         ("studio", 73.31, "STUDIO"), ("alat", 73.96, "ALAT"), ("marketing", 74.89, "MARKETING")]


def c19(n, info, A):
    """'kompensasi host, honor bintang tamu, transportasi, studio, peralatan, sampai marketing.' — 6 ikon
    biaya di atas alas, muncul satu per satu."""
    st = C.studio("st", guest=None, host=False, people=False)
    _ = st
    for k, (kind, t, nm) in enumerate(COSTS):
        c, r = k % 3, k // 3
        x, y = -4.2 + c * 4.2, -1.0 - r * 3.4
        f = fr("C19", t)
        ped(f"pd{k}", 1.35, (x, y, 0), "st_chair2", f)
        ic = C.cost_icon(f"ic{k}", kind, .95)
        ic.location = (x, y, .42)
        pop(ic, f + 2, 1.0)
        A[nm] = (x, y, 3.2)
    cam, tgt = make_camera(lens=20, shift_y=.08)
    studio_cam(cam, tgt, n, tg=(0, -2.2, 1.4), az0=-92, az1=-89, el=26, d0=25, d1=24)


def c20(n, info, A):
    """'Di simulasi kita, total pengeluarannya sekitar Rp388 juta.' — menara omzet Rp455 jt (hijau) di
    kiri, menara pengeluaran Rp388 jt (merah) tumbuh di kanan."""
    rooftop()
    ped("pa", 2.0, (-3.0, 0, 0))
    a, ha = mtower("om", 455, (-3.0, 0, .42), "money_g")
    ped("pb", 2.0, (3.0, 0, 0))
    b, hb = mtower("ex", 388, (3.0, 0, .42), "money_red", fr("C20", 77.6), fr("C20", 80.0))
    A["OMZET"] = (-3.0, 0, .42 + ha + .3)
    A["KELUAR"] = (3.0, 0, .42 + hb + .3)
    cam, tgt = make_camera(lens=20, shift_y=.1)
    tg = (0, 0, 5.6)
    cam_keys(cam, tgt, [(1, orbit(tg, -93, 8, 33), tg), (n, orbit(tg, -88, 10, 31), tg)])


def c21(n, info, A):
    """'Artinya masih ada sisa operasional sekitar Rp67 juta per bulan.' — menara Rp455 jt: bagian merah
    Rp388 jt lepas & terbang, sisa hijau Rp67 jt menyala + centang."""
    rooftop()
    ped("pa", 2.0, (-1.5, 0, 0))
    g, hg = mtower("sisa", 67, (-1.5, 0, .42), "money_g")
    r, hr = mtower("ops", 388, (-1.5, 0, .42 + hg), "money_red")
    ped("pb", 1.8, (5.5, 4.0, 0), "st_panel")
    f0 = fr("C21", 82.39)
    p0 = tuple(r.location)
    key(r, "location", 1, p0)
    key(r, "location", f0, p0)
    key(r, "location", f0 + 8, (p0[0], p0[1], p0[2] + 1.2))
    key(r, "location", f0 + 26, (5.5, 4.0, .42))
    f1 = fr("C21", 83.76)
    for k, s in ((f1, 1), (f1 + 5, 1.12), (f1 + 9, 1)):
        key(g, "scale", k, (s, s, s))
    sparkles("sp", (-1.5, 0, hg + 1.0), f1 + 3, 4, 1.6, .3)
    ck = L.checkmark("ck", (-1.5, -.6, .42 + hg + 1.6), .8)
    pop(ck, f1 + 8, 1.0)
    A["SISA"] = (-1.5, 0, .42 + hg + .3)
    A["OPS"] = (r, (0, 0, hr + .3))
    cam, tgt = make_camera(lens=20, shift_y=.1)
    tg0, tg1 = (1.5, 1.0, 5.4), (1.0, 1.0, 2.6)
    cam_keys(cam, tgt, [(1, orbit(tg0, -94, 9, 31), tg0), (fr("C21", 82.4), orbit(tg0, -92, 10, 30), tg0),
                        (n, orbit(tg1, -88, 13, 22), tg1)])


def c22(n, info, A):
    """'Tapi ingat, ini bukan laporan keuangan asli Close The Door.' — dokumen laporan di meja podcast,
    cap merah SIMULASI menghantam."""
    st = C.studio("st", guest="pejabat")
    host_talk(st, n, 22, ("host", "guest"))
    rd = L.report_doc("rd", 1.25).build((0, .55, C.TABLE_Z))
    pop(rd, 4, 1.0)
    sm = C.stamp("sm", "SIMULASI", .55)
    f0 = fr("C22", 86.7)
    fly(sm, f0, f0 + 6, (0, .2, 7.5), (0, .4, 2.6))
    key(sm, "rotation_euler", 1, (0, .15, 0))
    for k, s in ((f0 + 6, 1.15), (f0 + 9, 1.0)):
        key(sm, "scale", k, (s, s, s))
    A["DOC"] = (0, .55, 4.9)
    cam, tgt = make_camera(lens=22, shift_y=.1)
    studio_cam(cam, tgt, n, tg=(0, .5, 2.6), az0=-95, az1=-90, el=12, d0=15, d1=13)


def c23(n, info, A):
    """'Pelajaran bisnisnya, makin besar audience, makin besar peluang monetisasinya.' — 3 tangga:
    penonton makin banyak -> menara uang makin tinggi, panah naik."""
    rooftop()
    steps = [(-6.5, 8, 30, 91.59), (0, 22, 80, 92.0), (6.5, 50, 160, 92.4)]
    fm = fr("C23", 93.54)
    for k, (x, npp, juta, t) in enumerate(steps):
        cr = C.crowd(f"cr{k}", npp, x - 2.6, -3.8, x + 2.6, -3.8 + .6 + npp * .06, seed=k, s=.8)
        pop(cr, fr("C23", t), 1.0)
        ped(f"pd{k}", 1.5, (x, 1.5, 0), "st_chair2", fr("C23", t))
        mtower(f"m{k}", juta, (x, 1.5, .42), "money_g", fm + k * 6, fm + k * 6 + 20)
    ar = C.arrow_up("ar", 1.4)
    ar.location = (9.8, 1.5, 3.0)
    ar.rotation_euler.y = -.3
    pop(ar, fm + 26, 1.0)
    A["AUD"] = (0, -3.0, 1.8)
    A["MON"] = (6.5, 1.5, .42 + 16 * LH + .3)
    cam, tgt = make_camera(lens=20, shift_y=.1)
    tg = (.8, -.8, 1.8)
    cam_keys(cam, tgt, [(1, orbit(tg, -95, 16, 22), tg), (n, orbit(tg, -88, 19, 21), tg)])


def c24(n, info, A):
    """'Tapi yang menentukan bukan cuma seberapa banyak orang menonton, melainkan seberapa pintar perusahaan
    mengubah perhatian audience jadi pendapatan.' — penonton -> token perhatian -> mesin monetisasi -> uang."""
    rooftop()
    C.crowd("cr", 36, -12.5, -2.5, -6.0, 3.5, seed=5, s=.9)
    mm = C.money_machine("mm", 1.0)
    mm["body"].location = (0, 1.5, 0)
    f_on = fr("C24", 99.43)
    emission_ramp(lp.mat("mach_acc", emission=3), [(1, .2), (f_on, .2), (f_on + 6, 6)])
    rnd = random.Random(2)
    # token perhatian mengalir dari penonton ke corong (mulai sejak awal, terus berulang)
    for k in range(10):
        e = C.eye_token(f"ey{k}", .55)
        p0 = (rnd.uniform(-11.5, -7), rnd.uniform(-1.5, 2.5), 1.8)
        p1 = (-1.2, 1.5, 5.6)
        fs = 6 + k * 12
        while fs < n - 30:
            key(e, "location", max(1, fs - 1), p0)
            key(e, "scale", max(1, fs - 1), (.001,) * 3)
            key(e, "scale", fs + 3, (1, 1, 1))
            key(e, "location", fs + 26, p1)
            key(e, "scale", fs + 26, (1, 1, 1))
            key(e, "scale", fs + 30, (.001,) * 3)
            fs += 120
    # uang keluar & menumpuk setelah mesin menyala
    for k in range(6):
        ms = L.money_stack(f"ms{k}", 6, 1.2).build()
        f = f_on + 8 + k * 9
        fly(ms, f, f + 10, (3.0, 1.5, .9), (4.2 + (k % 3) * 1.3, -.4 + (k // 3) * 1.1, .35))
        pop(ms, f, 1.0)
    ob, h = mtower("m", 60, (9.0, .6, 0), "money_g", f_on + 30, f_on + 70)
    A["PERHATIAN"] = (-9.0, .5, 3.2)
    A["UANG"] = (9.0, .6, h + .4)
    A["MESIN"] = (0, 1.5, 5.4)
    cam, tgt = make_camera(lens=18, shift_y=.1)
    tg = (-1.4, .5, 2.2)
    cam_keys(cam, tgt, [(1, orbit(tg, -96, 18, 26), tg), (n, orbit(tg, -88, 21, 24.5), tg)])


def c25(n, info, A):
    """CTA: 'Kalau kamu punya modal untuk bangun bisnis media, berani nggak bersaing di industri ini?' —
    kota metropolitan dari atas, gedung studio bercahaya, papan LED."""
    C.city_traffic(n, hwy=info.get("hwy"), n=22)
    emission_ramp(info["hq"]["glow"].data.materials[0], [(1, 6), (40, 12)])
    A["HQ"] = (0, 30, 27)
    cam, tgt = make_camera(lens=20, shift_y=.12)
    tg = (0, 25, 12)
    cam_keys(cam, tgt, [(1, orbit(tg, -112, 30, 120), tg), (n, orbit(tg, -96, 34, 150), tg)])


SCENES = {f"C{k:02d}": fn for k, fn in enumerate(
    (c01, c02, c03, c04, c05, c06, c07, c08, c09, c10, c11, c12, c13, c14, c15, c16, c17, c18, c19, c20, c21, c22,
     c23, c24, c25), 1)}
WORLD = {"C01", "C02", "C06", "C25"}


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
    C.setup_city_light()
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, n
    info = {}
    if args.scene in WORLD:
        info = C.build_city(ext=230.0 if args.scene != "C25" else 270.0)
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
