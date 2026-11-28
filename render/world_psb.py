"""Aset dunia dokumenter "Persib Bandung" (Bedah Bisnis).
Stadion GBLA malam hari (mangkuk tribun bertingkat penuh bobotoh berbaju biru, atap cincin + lampu sorot, lapangan
bergaris, lintasan atletik), kartu foto dokumenter (foto resmi persib.co.id), plakat logo (Persib & 4 kompetisi),
trofi metalik, pilar nilai pasar, tong sampah terpilah, stopwatch 90', jersey 3D, papan bursa (lilin naik),
peta Google Maps di lantai + pin + rute menyala (Graha Persib -> GBLA), mesin uang (teaser part 2).
Tekstur dibaca dari env PSB_TEX (dibuat render/psb_assets.py; tidak disimpan di repo).
"""
import math
import os
import random

import bpy  # noqa: F401

import lowpoly as lp
import world as W
import world_ctd as C
import world_fom as F            # article_phone()
import world_gta as G
import world_hotel as H
import world_laundry as L
import world_vap as V

TEX = os.environ.get("PSB_TEX", "/tmp/claude-0/-home-user-Bbg/e4570b9b-8bb7-5f4c-a29b-693bb3cf9daa/scratchpad/psb/tex")
G.TEX = TEX                       # img_plane / img_mat / article_phone memakai folder ini
F.TEX = TEX

PLAYERS = sorted(os.path.splitext(f)[0] for f in os.listdir(TEX) if f.startswith("pl_")) if os.path.isdir(TEX) else []

lp.PAL.update({
    "psb_blue": "#1F4FD1", "psb_blue2": "#2D6BFF", "psb_navy": "#0C1D4F", "psb_white": "#F2F5FA",
    "psb_gold": "#E9B949", "psb_ground": "#0B0F18", "psb_wall": "#1A2233", "psb_wall2": "#243049",
    "seat_a": "#1B3F9E", "seat_b": "#15307A", "seat_c": "#2A56C4", "track": "#B8553A", "pitch1": "#1F6B2C",
    "pitch2": "#277A34", "pline": "#F4F7F4", "roof": "#D8DEE8", "roof_dk": "#8D97A8", "flood": "#FFFFFF",
    "tr_gold": "#E8B53A", "tr_silver": "#D6DCE6", "tr_base": "#1B1B22", "photo_w": "#F4F1EA",
    "bin_green": "#24A148", "bin_blue": "#1E63D6", "bin_grey": "#6B7280", "bag_dk": "#22252C",
    "bag_lt": "#C9CED6", "sw_body": "#F4F6FA", "sw_dark": "#121722", "candle_g": "#22C55E", "candle_r": "#EF4444",
    "board": "#070B14", "pin_red": "#EA4335", "pin_blue": "#2D6BFF", "route": "#5B8CFF", "gear": "#9AA3B2",
    "gear_dk": "#4B5563", "mach": "#141A2A", "coin_g": "#F2C14E", "psb_grid": "#2D6BFF", "psb_grid2": "#5FD3FF",
    "plate_w": "#FFFFFF", "shirt_w": "#F3F4F6",
})
lp.PAL["vp_floor"] = "#05070D"      # panggung neon versi biru-malam (dokumenter)
lp.PAL["vp_dome"] = "#050A1A"
lp.PAL["vp_dome2"] = "#1D4ED8"     # cakrawala biru (bukan pink)
lp.PAL["vp_dome3"] = "#0B2466"

FANS = ("psb_blue", "psb_blue", "psb_blue2", "psb_navy", "shirt_w", "psb_blue")


def metal(ob, rough=.28, glow_=.25):
    """logam (emas/perak): metalik + sedikit emisi warna dasar supaya tidak memantulkan hijau rumput."""
    for i, m in enumerate(ob.data.materials):
        if m and m.use_nodes and "Principled BSDF" in m.node_tree.nodes:
            m = m.copy()
            ob.data.materials[i] = m
            p = m.node_tree.nodes["Principled BSDF"]
            p.inputs["Metallic"].default_value = .75
            p.inputs["Roughness"].default_value = max(rough, .35)
            base = p.inputs["Base Color"].default_value
            if "Emission Color" in p.inputs:
                p.inputs["Emission Color"].default_value = base
                p.inputs["Emission Strength"].default_value = glow_


# ================================================================== stadion GBLA
def _ell(a, b, t):
    return a * math.cos(t), b * math.sin(t)


def stadium(name="gbla", crowd=True, seed=4, n_seg=120, lights=True, ground=True):
    """stadion oval: lapangan + lintasan + 2 cincin tribun (bawah 8 trap, atas 9 trap) penuh bobotoh,
    atap cincin putih + lampu sorot, dinding luar dengan strip biru menyala. Pusat lapangan di (0,0,0).
    Return dict(fans=[obj grup], roof, pitch, a_out, b_out, z_top)."""
    rnd = random.Random(seed)
    out = {}
    # ---- lapangan + lintasan
    pm = W.MB(name + "_pitch")
    PW, PH = 21.0, 13.6
    for k in range(12):
        x0 = -PW / 2 + k * PW / 12
        pm.box(x0, -PH / 2, 0, x0 + PW / 12, PH / 2, .06, "pitch1" if k % 2 else "pitch2")
    t = .07

    def ln(x0, y0, x1, y1):
        pm.box(min(x0, x1) - t / 2, min(y0, y1) - t / 2, .06, max(x0, x1) + t / 2, max(y0, y1) + t / 2, .075, "pline")
    ln(-PW / 2, -PH / 2, PW / 2, -PH / 2)
    ln(-PW / 2, PH / 2, PW / 2, PH / 2)
    ln(-PW / 2, -PH / 2, -PW / 2, PH / 2)
    ln(PW / 2, -PH / 2, PW / 2, PH / 2)
    ln(0, -PH / 2, 0, PH / 2)
    for sx in (-1, 1):
        x = sx * PW / 2
        ln(x, -4.0, x - sx * 3.3, -4.0)
        ln(x, 4.0, x - sx * 3.3, 4.0)
        ln(x - sx * 3.3, -4.0, x - sx * 3.3, 4.0)
        ln(x, -1.8, x - sx * 1.1, -1.8)
        ln(x, 1.8, x - sx * 1.1, 1.8)
        ln(x - sx * 1.1, -1.8, x - sx * 1.1, 1.8)
        # gawang
        gx = x + sx * .35
        pm.box(gx - .05, -.75, 0, gx + .05, -.65, .5, "pline")
        pm.box(gx - .05, .65, 0, gx + .05, .75, .5, "pline")
        pm.box(gx - .05, -.75, .45, gx + .05, .75, .55, "pline")
    for i in range(48):
        a0, a1 = 2 * math.pi * i / 48, 2 * math.pi * (i + 1) / 48
        pm.poly([(1.75 * math.cos(a0), 1.75 * math.sin(a0), .075), (1.82 * math.cos(a0), 1.82 * math.sin(a0), .075),
                 (1.82 * math.cos(a1), 1.82 * math.sin(a1), .075), (1.75 * math.cos(a1), 1.75 * math.sin(a1), .075)],
                [(0, 1, 2, 3)], "pline")
    # lintasan (cincin elips oranye) + apron
    for i in range(n_seg):
        t0, t1 = 2 * math.pi * i / n_seg, 2 * math.pi * (i + 1) / n_seg
        for (a0_, b0_, a1_, b1_, key_) in ((12.2, 8.6, 14.6, 10.6, "track"), (14.6, 10.6, 15.4, 11.4, "psb_wall")):
            p0, p1 = _ell(a0_, b0_, t0), _ell(a0_, b0_, t1)
            q0, q1 = _ell(a1_, b1_, t0), _ell(a1_, b1_, t1)
            pm.poly([(p0[0], p0[1], .03), (q0[0], q0[1], .03), (q1[0], q1[1], .03), (p1[0], p1[1], .03)],
                    [(0, 1, 2, 3)], key_)
    pm.box(-12.4, -8.8, 0, 12.4, 8.8, .02, "pitch2")
    out["pitch"] = pm.build()
    # ---- tribun bertingkat
    tm = W.MB(name + "_tiers")
    a, b, z = 15.4, 11.4, .0
    tiers = []
    for k in range(17):
        upper = k >= 8
        dr = .95 if not upper else .9
        dz = .5 if not upper else .72
        if k == 8:                      # selasar antara tribun bawah & atas
            tm_a, tm_b = a, b
            a, b, z = a + 1.2, b + 1.2, z + 1.4
            for i in range(n_seg):
                t0, t1 = 2 * math.pi * i / n_seg, 2 * math.pi * (i + 1) / n_seg
                p0, p1, q0, q1 = _ell(tm_a, tm_b, t0), _ell(tm_a, tm_b, t1), _ell(a, b, t0), _ell(a, b, t1)
                tm.poly([(p0[0], p0[1], z - 1.4), (p1[0], p1[1], z - 1.4), (p1[0], p1[1], z), (p0[0], p0[1], z)],
                        [(0, 1, 2, 3)], "psb_wall2")
                tm.poly([(p0[0], p0[1], z), (p1[0], p1[1], z), (q1[0], q1[1], z), (q0[0], q0[1], z)],
                        [(0, 1, 2, 3)], "psb_wall")
        z1 = z + dz
        for i in range(n_seg):
            t0, t1 = 2 * math.pi * i / n_seg, 2 * math.pi * (i + 1) / n_seg
            p0, p1 = _ell(a, b, t0), _ell(a, b, t1)
            q0, q1 = _ell(a + dr, b + dr, t0), _ell(a + dr, b + dr, t1)
            key_ = ("seat_a", "seat_b", "seat_c")[(i // 6 + k) % 3] if (i // 3) % 7 else "psb_white"
            tm.poly([(p0[0], p0[1], z), (p1[0], p1[1], z), (p1[0], p1[1], z1), (p0[0], p0[1], z1)], [(0, 1, 2, 3)],
                    "psb_wall2")
            tm.poly([(p0[0], p0[1], z1), (p1[0], p1[1], z1), (q1[0], q1[1], z1), (q0[0], q0[1], z1)], [(0, 1, 2, 3)],
                    key_)
        tiers.append((a + dr * .5, b + dr * .5, z1))
        a, b, z = a + dr, b + dr, z1
    out["a_out"], out["b_out"], out["z_top"] = a, b, z
    # dinding luar + strip biru menyala
    gl = W.MB(name + "_strip")
    for i in range(n_seg):
        t0, t1 = 2 * math.pi * i / n_seg, 2 * math.pi * (i + 1) / n_seg
        p0, p1 = _ell(a, b, t0), _ell(a, b, t1)
        tm.poly([(p0[0], p0[1], 0), (p0[0], p0[1], z + 1.0), (p1[0], p1[1], z + 1.0), (p1[0], p1[1], 0)],
                [(0, 1, 2, 3)], "psb_wall")
        if i % 4 == 0:
            q0 = _ell(a + .08, b + .08, t0)
            q1 = _ell(a + .08, b + .08, t0 + .012)
            gl.poly([(q0[0], q0[1], .6), (q0[0], q0[1], z + .6), (q1[0], q1[1], z + .6), (q1[0], q1[1], .6)],
                    [(0, 1, 2, 3)], "psb_blue2")
    out["tiers"] = tm.build()
    so = gl.build()
    V.glow(so, {"psb_blue2": 6.0})
    # ---- atap cincin (menaungi tribun atas) + lampu sorot di bibir dalam
    rm = W.MB(name + "_roof")
    fl = W.MB(name + "_flood")
    a_in, b_in = 19.5, 15.5
    zr = z + 3.6
    for i in range(n_seg):
        t0, t1 = 2 * math.pi * i / n_seg, 2 * math.pi * (i + 1) / n_seg
        p0, p1 = _ell(a_in, b_in, t0), _ell(a_in, b_in, t1)
        q0, q1 = _ell(a + .6, b + .6, t0), _ell(a + .6, b + .6, t1)
        rm.poly([(p0[0], p0[1], zr), (q0[0], q0[1], zr + .8), (q1[0], q1[1], zr + .8), (p1[0], p1[1], zr)],
                [(0, 1, 2, 3)], "roof" if i % 2 else "roof_dk")
        rm.poly([(p0[0], p0[1], zr - .25), (p1[0], p1[1], zr - .25), (q1[0], q1[1], zr + .55), (q0[0], q0[1], zr + .55)],
                [(0, 1, 2, 3)], "roof_dk")
        if i % 3 == 0:                 # tiang penyangga di dinding luar
            c0 = _ell(a + .3, b + .3, t0)
            rm.box(c0[0] - .12, c0[1] - .12, z, c0[0] + .12, c0[1] + .12, zr + .8, "roof_dk")
        if i % 2 == 0:
            f0, f1 = _ell(a_in + .1, b_in + .1, t0), _ell(a_in + .1, b_in + .1, t0 + .03)
            fl.poly([(f0[0], f0[1], zr - .32), (f1[0], f1[1], zr - .32), (f1[0], f1[1], zr - .12), (f0[0], f0[1], zr - .12)],
                    [(0, 1, 2, 3)], "flood")
    out["roof"] = rm.build()
    fo = fl.build()
    V.glow(fo, {"flood": 14.0})
    if lights:
        for (x, y) in ((-9, -6), (9, -6), (-9, 6), (9, 6), (0, 0)):
            li = bpy.data.lights.new(name + f"_L{x}{y}", "AREA")
            li.energy, li.size, li.color = 2600, 9.0, (1, .97, .92)
            lo = bpy.data.objects.new(li.name, li)
            lp._link(lo)
            lo.location = (x, y, zr + 2)
    # ---- bobotoh di tribun (3 grup untuk lompat bergantian)
    if crowd:
        mbs = [W.MB(f"{name}_fans{g}") for g in range(3)]
        for k, (ta, tb, tz) in enumerate(tiers):
            for i in range(n_seg * 2):
                if (i // 6) % 7 == 0 and k % 5 == 2:
                    continue
                tt_ = 2 * math.pi * (i / 2 + rnd.uniform(.05, .45)) / n_seg
                x, y = _ell(ta, tb, tt_)
                mb = mbs[rnd.randrange(3)]
                C.mini_person(mb, x, y, tz, .62 * rnd.uniform(.92, 1.08), rnd.choice(FANS), rnd.choice(("skin1", "skin2", "skin3")),
                              "hair_blk")
                if rnd.random() < .3:            # tangan terangkat / syal
                    mb.box(x - .05, y - .05, tz + .45, x + .05, y + .05, tz + .95, rnd.choice(("psb_blue", "psb_white")))
        out["fans"] = [m.build() for m in mbs]
    if not ground:
        return out
    # ---- halaman luar gelap + lampu jalan
    gm = W.MB(name + "_ground")
    gm.box(-90, -90, -.05, 90, 90, 0, "psb_ground")
    lm = W.MB(name + "_lamps")
    for i in range(28):
        tt_ = 2 * math.pi * i / 28
        x, y = _ell(a + 7, b + 7, tt_)
        gm.cyl(x, y, 0, 3.2, .08, "roof_dk", n=6)
        lm.sphere(x, y, 3.3, .22, "flood")
    gm.build()
    lo_ = lm.build()
    V.glow(lo_, {"flood": 10.0})
    return out


def crowd_jump(obs, f0, f1, amp=.18, period=12.0):
    for g, ob in enumerate(obs):
        z0 = ob.location.z
        f = f0 + g * period / len(obs)
        while f <= f1 + period:
            ob.location.z = z0
            ob.keyframe_insert("location", frame=int(f))
            ob.location.z = z0 + amp
            ob.keyframe_insert("location", frame=int(f + period * .4))
            f += period


def flares(name, n, area, z, seed=2):
    """nyala suar biru di tribun (titik cahaya + asap tipis)."""
    rnd = random.Random(seed)
    mb = W.MB(name)
    x0, y0, x1, y1 = area
    for k in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        mb.sphere(x, y, z + rnd.uniform(0, 1.0), .18, "psb_blue2")
    ob = mb.build()
    V.glow(ob, {"psb_blue2": 12.0})
    return ob


# ================================================================== kartu foto & plakat logo
def photo(name, img, h=4.0, loc=(0, 0, 0), rot_z=0.0, em=.95, border=.14, tilt=0.0):
    """foto dokumenter: cetakan berbingkai kertas putih (pivot bawah-tengah, menghadap -Y)."""
    root = bpy.data.objects.new(name, None)
    lp._link(root)
    ip = G.img_plane(name + "_i", img, h=h, loc=(0, -.03, border), em=em)
    ip.parent = root
    w = ip["w"]
    mb = W.MB(name + "_p")
    mb.box(-w / 2 - border, 0, 0, w / 2 + border, .08, h + 2 * border, "photo_w")
    po = mb.build(parent=root)
    V.glow(po, {"photo_w": .35})
    root.location = loc
    root.rotation_euler = (tilt, 0, rot_z)
    root["w"], root["h"] = w + 2 * border, h + 2 * border
    return root


def logo_card(name, img, h=3.0, loc=(0, 0, 0), rot_z=0.0, plate="plate_w", pad=.35, em=1.0, plate_em=.6):
    """plakat logo: pelat putih membulat + logo (png alfa) di depannya. Pivot bawah-tengah."""
    root = bpy.data.objects.new(name, None)
    lp._link(root)
    ip = G.img_plane(name + "_i", img, h=h, loc=(0, -.06, pad), em=em)
    ip.parent = root
    w = ip["w"]
    if plate:
        mb = W.MB(name + "_pl")
        L.rbox(mb, -w / 2 - pad, 0, 0, w / 2 + pad, .2, h + 2 * pad, plate, c=.35)
        po = mb.build(parent=root)
        V.glow(po, {plate: plate_em})
    root.location = loc
    root.rotation_euler.z = rot_z
    root["w"], root["h"] = w + 2 * pad, h + 2 * pad
    return root


# ================================================================== trofi, pilar, tong sampah, stopwatch
def trophy(name, s=1.0, loc=(0, 0, 0), key_="tr_gold"):
    mb = W.MB(name)
    mb.box(-.55 * s, -.55 * s, 0, .55 * s, .55 * s, .4 * s, "tr_base")
    mb.cyl(0, 0, .4 * s, .62 * s, .34 * s, key_, n=16, r_top=.2 * s)
    mb.cyl(0, 0, .62 * s, 1.05 * s, .1 * s, key_, n=12)
    mb.cyl(0, 0, 1.05 * s, 1.22 * s, .13 * s, key_, n=14, r_top=.3 * s)
    mb.cyl(0, 0, 1.22 * s, 2.15 * s, .3 * s, key_, n=18, r_top=.66 * s)
    mb.cyl(0, 0, 2.15 * s, 2.25 * s, .7 * s, key_, n=18)
    for sx in (-1, 1):
        x = sx * .72 * s
        mb.box(x - .07 * s, -.07 * s, 1.35 * s, x + .07 * s, .07 * s, 2.0 * s, key_)
        mb.box(min(x, sx * .55 * s) - .02 * s, -.07 * s, 1.95 * s, max(x, sx * .55 * s) + .02 * s, .07 * s, 2.07 * s, key_)
        mb.box(min(x, sx * .45 * s) - .02 * s, -.07 * s, 1.33 * s, max(x, sx * .45 * s) + .02 * s, .07 * s, 1.45 * s, key_)
    ob = mb.build(loc)
    metal(ob, .22)
    return ob


def bins(name, loc=(0, 0, 0), s=1.0):
    """3 tong sampah terpilah (organik / anorganik / residu) + label. Return dict(bins=[obj], labels=[obj])."""
    out = {"bins": [], "labels": [], "x": []}
    for i, (key_, lab) in enumerate((("bin_green", "ORGANIK"), ("bin_blue", "ANORGANIK"), ("bin_grey", "RESIDU"))):
        x = (i - 1) * 2.6 * s
        mb = W.MB(f"{name}{i}")
        L.rbox(mb, -.95 * s, -.8 * s, 0, .95 * s, .8 * s, 2.4 * s, key_, c=.2 * s)
        L.rbox(mb, -1.05 * s, -.9 * s, 2.4 * s, 1.05 * s, .9 * s, 2.65 * s, "sw_dark", c=.2 * s)
        mb.box(-.5 * s, -.82 * s, 1.0 * s, .5 * s, -.8 * s, 1.9 * s, "psb_white")
        ob = mb.build((loc[0] + x, loc[1], loc[2]))
        t = H.text(f"{name}_t{i}", lab, .36 * s, "psb_white", depth=.04, loc=(loc[0] + x, loc[1] - .95 * s, loc[2] + 2.9 * s),
                   emission=3.0)
        out["bins"].append(ob)
        out["labels"].append(t)
        out["x"].append(loc[0] + x)
    return out


def trash_bag(name, loc, s=1.0, key_="bag_dk"):
    mb = W.MB(name)
    mb.sphere(0, 0, .45 * s, .5 * s, key_, sz=.45 * s)
    mb.cyl(0, 0, .85 * s, 1.05 * s, .12 * s, key_, n=6, r_top=.05 * s)
    return mb.build(loc)


def stopwatch(name, loc=(0, 0, 0), s=1.0):
    """stopwatch berdiri (menghadap -Y): badan putih, cincin biru, jarum berputar. Return dict(root, hand)."""
    root = bpy.data.objects.new(name, None)
    lp._link(root)
    mb = W.MB(name + "_b")
    mb.disc_y(0, .3 * s, 0, 2.0 * s, .6 * s, "sw_body", n=36)
    mb.disc_y(0, -.32 * s, 0, 1.75 * s, .05 * s, "sw_dark", n=36)
    mb.box(-.25 * s, -.1 * s, 2.0 * s, .25 * s, .1 * s, 2.45 * s, "sw_body")
    mb.box(-.45 * s, -.12 * s, 2.45 * s, .45 * s, .12 * s, 2.65 * s, "psb_blue")
    for k in range(12):
        a = 2 * math.pi * k / 12
        x, z = math.sin(a) * 1.5 * s, math.cos(a) * 1.5 * s
        mb.box(x - .05 * s, -.4 * s, z - .05 * s, x + .05 * s, -.37 * s, z + .05 * s, "psb_blue2")
    bo = mb.build(parent=root)
    V.glow(bo, {"psb_blue2": 5.0})
    hm = W.MB(name + "_h")
    hm.box(-.05 * s, -.48 * s, -.1 * s, .05 * s, -.42 * s, 1.35 * s, "candle_r")
    hand = hm.build(parent=root)
    V.glow(hand, {"candle_r": 4.0})
    root.location = loc
    return {"root": root, "hand": hand}


# ================================================================== jersey 3D
def jersey(name, loc=(0, 0, 0), s=1.0, key_="psb_blue", trim="psb_white", number="25"):
    """jersey berdiri (menghadap -Y): siluet kaus diekstrusi, kerah & strip lengan, tulisan PERSIB + nomor."""
    mb = W.MB(name)
    P = [(-1.25, 0), (1.25, 0), (1.25, 2.2), (2.05, 1.75), (2.45, 2.45), (1.45, 3.35), (.55, 3.5), (0, 3.15),
         (-.55, 3.5), (-1.45, 3.35), (-2.45, 2.45), (-2.05, 1.75), (-1.25, 2.2)]
    mb.prism_y([(x * s, z * s) for x, z in P], -.18 * s, .18 * s, key_)
    mb.prism_y([(x * s, z * s) for x, z in ((-.55, 3.5), (0, 3.15), (.55, 3.5), (.45, 3.55), (0, 3.25), (-.45, 3.55))],
               -.2 * s, .2 * s, trim)
    for sx in (-1, 1):
        mb.prism_y([(sx * x * s, z * s) for x, z in ((2.05, 1.75), (2.25, 2.1), (2.35, 2.2), (2.13, 1.85))], -.2 * s, .2 * s,
                   trim)
    ob = mb.build(loc)
    t1 = H.text(name + "_t", "PERSIB", .42 * s, trim, depth=.04, loc=(loc[0], loc[1] - .21 * s, loc[2] + 2.45 * s))
    t2 = H.text(name + "_n", number, 1.0 * s, trim, depth=.04, loc=(loc[0], loc[1] - .21 * s, loc[2] + 1.0 * s))
    for t in (t1, t2):
        t.parent = ob
        t.location = (t.location.x - loc[0], t.location.y - loc[1], t.location.z - loc[2])
    return ob


# ================================================================== papan bursa
def stock_board(name, loc=(0, 0, 0), w=16.0, h=8.0, n=14, seed=5, rise=True):
    """papan bursa LED: panel gelap berbingkai biru, garis grid, lilin (candlestick) tren naik.
    Return dict(board, candles=[obj per lilin])."""
    rnd = random.Random(seed)
    mb = W.MB(name)
    mb.box(-w / 2, 0, 0, w / 2, .3, h, "board")
    mb.box(-w / 2 + .2, -.02, .2, w / 2 - .2, 0, h - .2, "psb_navy")
    t = .2
    for (a, b, c, d) in ((-w / 2, -w / 2 + t, 0, h), (w / 2 - t, w / 2, 0, h), (-w / 2, w / 2, 0, t), (-w / 2, w / 2, h - t, h)):
        mb.box(a, -.06, c, b, 0, d, "psb_blue2")
    for k in range(1, 5):
        z = h * k / 5
        mb.box(-w / 2 + .3, -.05, z - .02, w / 2 - .3, -.02, z + .02, "psb_grid")
    bo = mb.build(loc)
    V.glow(bo, {"psb_blue2": 6.0, "psb_navy": .5, "psb_grid": 3.0})
    cs = []
    step = h * .66 / (n - 1)                 # tren naik yang jelas (tiap lilin ke-3 dari 4 merah/koreksi)
    v = h * .12
    for i in range(n):
        x = -w / 2 + 1.0 + i * (w - 2.0) / (n - 1)
        close = h * .12 + step * (i + 1) + (-.9 if i % 4 == 2 else .2 + rnd.uniform(0, .3)) * step
        if not rise:
            close = h - close
        d = close - v
        up = d >= 0
        lo_, hi_ = min(v, v + d), max(v, v + d) + .12
        cm = W.MB(f"{name}_c{i}")
        cm.box(x - .26, -.12, lo_, x + .26, -.05, hi_, "candle_g" if up else "candle_r")
        cm.box(x - .03, -.1, lo_ - .3, x + .03, -.07, hi_ + .3, "candle_g" if up else "candle_r")
        co = cm.build(loc)
        V.glow(co, {"candle_g": 5.0, "candle_r": 5.0})
        cs.append(co)
        v = min(h * .9, max(h * .1, v + d))
    return {"board": bo, "candles": cs}


# ================================================================== peta lantai + pin + rute
def map_floor(name, img="map_area", w=24.0, loc=(0, 0, 0), em=.9):
    """peta (tangkapan Google Maps kiriman user) rebah di lantai. Return dict(ob, w, h, at(u,v) -> (x,y,z))."""
    iw, ih = G.img_size(img)
    h = w * ih / iw
    me = G._quad_mesh(name, w, h, center=True)
    me.materials.append(G.img_mat(img, em, False, False))
    ob = bpy.data.objects.new(name, me)
    lp._link(ob)
    ob.rotation_euler.x = -math.pi / 2          # rebah: atas gambar -> +Y
    ob.location = loc
    mb = W.MB(name + "_fr")
    t = .25
    for (a, b, c, d) in ((-w / 2 - t, -h / 2 - t, w / 2 + t, -h / 2), (-w / 2 - t, h / 2, w / 2 + t, h / 2 + t),
                         (-w / 2 - t, -h / 2, -w / 2, h / 2), (w / 2, -h / 2, w / 2 + t, h / 2)):
        mb.box(a + loc[0], b + loc[1], loc[2] - .05, c + loc[0], d + loc[1], loc[2] + .06, "psb_blue2")
    fo = mb.build()
    V.glow(fo, {"psb_blue2": 5.0})

    def at(u, v, z=0.0):
        return (loc[0] + (u - .5) * w, loc[1] + (.5 - v) * h, loc[2] + z)
    return {"ob": ob, "w": w, "h": h, "at": at}


def map_pin(name, loc, s=1.0, key_="pin_red", em=2.5):
    """pin peta 3D (kepala bola + kerucut), ujung di loc."""
    mb = W.MB(name)
    mb.cyl(0, 0, 0, 1.1 * s, .02 * s, key_, n=12, r_top=.42 * s)
    mb.sphere(0, 0, 1.35 * s, .5 * s, key_)
    mb.sphere(0, -.32 * s, 1.4 * s, .18 * s, "psb_white")
    ob = mb.build(loc)
    V.glow(ob, {key_: em, "psb_white": 2.0})
    return ob


def route_curve(name, pts, key_="route", bevel=.18, em=6.0):
    """garis rute menyala (kurva ber-bevel). Animasikan data.bevel_factor_end 0 -> 1 untuk 'menggambar' rute."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p[0], p[1], p[2], 1)
    cu.bevel_depth = bevel
    cu.bevel_resolution = 2
    cu.use_fill_caps = True
    ob = bpy.data.objects.new(name, cu)
    lp._link(ob)
    ob.data.materials.append(lp.mat(key_, emission=em))
    return ob


# ================================================================== mesin uang (teaser part 2)
def gear(name, r=1.6, teeth=14, depth=.5, key_="gear", loc=(0, 0, 0)):
    mb = W.MB(name)
    mb.disc_y(0, depth / 2, 0, r, depth, key_, n=32)
    for k in range(teeth):
        a = 2 * math.pi * k / teeth
        cx, cz = math.cos(a) * (r + .18), math.sin(a) * (r + .18)
        hw = .2
        pts = [(cx - math.sin(a) * hw - math.cos(a) * .25, cz + math.cos(a) * hw - math.sin(a) * .25),
               (cx + math.sin(a) * hw - math.cos(a) * .25, cz - math.cos(a) * hw - math.sin(a) * .25),
               (cx + math.sin(a) * hw * .7 + math.cos(a) * .2, cz - math.cos(a) * hw * .7 + math.sin(a) * .2),
               (cx - math.sin(a) * hw * .7 + math.cos(a) * .2, cz + math.cos(a) * hw * .7 + math.sin(a) * .2)]
        mb.prism_y(pts, -depth / 2, depth / 2, key_)
    mb.disc_y(0, depth / 2 + .02, 0, r * .35, depth + .04, "gear_dk", n=16)
    ob = mb.build(loc)
    metal(ob, .35)
    return ob


def money_machine(name, loc=(0, 0, 0)):
    """mesin uang: badan besar gelap berbingkai biru + logo Persib + corong koin. Return dict(body, logo, gears)."""
    x, y, z = loc
    mb = W.MB(name)
    L.rbox(mb, -5, -2.5, 0, 5, 2.5, 7.0, "mach", c=.5)
    mb.box(-5.1, -2.6, 6.9, 5.1, 2.6, 7.2, "psb_blue2")
    mb.box(-5.1, -2.6, -.05, 5.1, 2.6, .25, "psb_blue2")
    mb.box(-1.6, -3.4, .25, 1.6, -2.5, 1.6, "gear_dk")          # corong keluar koin
    bo = mb.build(loc)
    V.glow(bo, {"psb_blue2": 6.0})
    lg = logo_card(name + "_lg", "lg_persib", 3.4, (x, y - 2.55, z + 2.4), plate=None, em=1.2)
    gs = [gear(f"{name}_g{i}", r, t_, .5, "gear", (x + gx, y - 2.6, z + gz))
          for i, (r, t_, gx, gz) in enumerate(((1.5, 14, -3.4, 5.2), (1.0, 10, -1.6, 6.3), (1.3, 12, 3.5, 5.0)))]
    return {"body": bo, "logo": lg, "gears": gs}


def coin(name, loc, s=1.0):
    mb = W.MB(name)
    mb.disc_y(0, .08 * s, 0, .55 * s, .16 * s, "coin_g", n=20)
    ob = mb.build(loc)
    metal(ob, .3)
    return ob
