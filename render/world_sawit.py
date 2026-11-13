"""Aset & dunia diorama untuk video "Bedah Bisnis Kebun Sawit".

Isi: pohon sawit low-poly (bibit polybag, muda, remaja, dewasa berbuah) dengan pelepah bergerigi,
tandan buah segar (TBS), piringan (lingkaran bersih di pangkal pohon), kebun luas pola segitiga + jalan
tanah + parit, pekerja kebun (sepatu bot, caping/helm, kaos lengan panjang) yang bisa memegang egrek
(galah panen) atau mendorong gerobak dorong roda satu (merah, mengikuti foto referensi), truk pengangkut
TBS (bak kayu), ekskavator buka lahan, karung pupuk, TPH (tempat pengumpulan hasil), lahan terbakar +
asap, dan petak "1 hektare" untuk adegan hitungan. Depan karakter/kendaraan: karakter menghadap -Y,
kendaraan menghadap +X.
"""
import math
import random

import bpy

import lowpoly as lp
import world as W
import world_hotel as H         # text(), money_bundle()
import world_laundry as L       # character(), pose(), walk_to(), ball/tube/rbox
import world_amdk as M          # lathe(), palet karyawan (helm), tronton palette

lp.PAL.update({
    # sawit
    "trunk_p": "#7B5B3C", "trunk_p2": "#6A4C31", "frond": "#3F8F37", "frond2": "#2F7A2E", "frond3": "#6E9A33",
    "frond_y": "#A9A23C", "spear": "#7CBF47", "crown": "#5A6A2A",
    "tbs_red": "#C2391E", "tbs_or": "#E86F24", "tbs_dk": "#4B1B15",
    # tanah & kebun
    "kb_grass": "#7EB65A", "kb_grass2": "#5E9C44", "kb_far": "#5E9A45", "kb_soil": "#A8784E", "kb_soil2": "#8E6240",
    "kb_soil_dk": "#6A4630", "road_dirt": "#D2AE78", "road_dirt2": "#BF9963", "canal": "#4E95B8",
    "burnt": "#3D3631", "ash": "#8B8279", "char": "#231E1B", "smoke": "#F2F0EC", "smoke2": "#DAD6D0",
    "ember": "#FF7A1A",
    # orang
    "kb_shirt1": "#3C6E9E", "kb_shirt2": "#6B8E3A", "kb_shirt3": "#C8553D", "kb_shirt4": "#E0A33A",
    "kb_pants": "#3A3F4A", "kb_pants2": "#55606E", "boot": "#1D1F22", "caping": "#D9B56A", "caping2": "#B8924C",
    "towel": "#F2EEE4", "pole": "#C8C9C2", "sickle": "#9EA6AD",
    # alat & kendaraan
    "wb_red": "#D8262A", "wb_red2": "#A81B1F", "wb_grip": "#1D1F22",
    "truk_cab": "#F2B630", "truk_cab2": "#2E8B57", "wood": "#A8743E", "wood2": "#8A5C2F", "exc_y": "#F2B71F",
    "exc_dk": "#33373D", "pupuk_w": "#F1F0E8", "pupuk_g": "#2F9E4F", "polybag": "#26282B", "stake": "#E9E2D0",
    "board": "#F7F3E8", "board_g": "#2F8F4E", "cal_red": "#E0453A", "cal_w": "#FFFFFF",
})

Z = 0.0
CH_S = L.CH_S
SP = 8.4                     # jarak tanam (segitiga sama sisi) dalam unit dunia


# ------------------------------------------------------------------ pohon sawit
def blob(mb, x, y, z, r, h, key, n=6):
    M.lathe(mb, x, y, z, [(0, 0), (r * .75, h * .18), (r, h * .5), (r * .7, h * .85), (0, h)], key, n=n)


def tbs(mb, x, y, z, s=1.0, detail=True):
    """tandan buah segar: badan oval merah-oranye + pucuk gelap (+ bintil buah bila detail)."""
    blob(mb, x, y, z, .42 * s, .78 * s, "tbs_red", n=7 if detail else 5)
    blob(mb, x, y, z + .3 * s, .36 * s, .55 * s, "tbs_dk", n=7 if detail else 5)
    if detail:
        for k in range(6):
            a = k * 1.05 + .3
            mb.cyl(x + .4 * s * math.cos(a), y + .4 * s * math.sin(a), z + .22 * s + (k % 2) * .18 * s,
                   z + .34 * s + (k % 2) * .18 * s, .1 * s, "tbs_or", n=4)


def frond(mb, cx, cy, cz, ang, length, elev, droop, width, key, steps=7, v=.38):
    """pelepah: pita bergerigi melengkung (tulang tengah sedikit lebih tinggi -> bentuk V)."""
    ca, sa = math.cos(ang), math.sin(ang)
    px, py = -sa, ca
    L_, C_, R_ = [], [], []
    for i in range(steps + 1):
        t = i / steps
        r = length * t * math.cos(elev)
        z = cz + length * t * math.sin(elev) - droop * length * t * t
        w = width * math.sin(math.pi * min(1.0, t * 1.08 + .02)) ** .7 * (1.0 if i % 2 == 0 else .72)
        if i == 0:
            w = width * .12
        cxp, cyp = cx + r * ca, cy + r * sa
        C_.append((cxp, cyp, z))
        L_.append((cxp + px * w, cyp + py * w, z - v * w))
        R_.append((cxp - px * w, cyp - py * w, z - v * w))
    vs = L_ + C_ + R_
    n = steps + 1
    fs = []
    for i in range(steps):
        fs.append((i, n + i, n + i + 1, i + 1))
        fs.append((n + i, 2 * n + i, 2 * n + i + 1, n + i + 1))
    mb.poly(vs, fs, key)


STAGES = {
    # trunk tinggi, panjang pelepah, jumlah pelepah (bawah, atas), buah
    "bibit": (0.0, .95, (0, 4), 0),
    "muda": (0.0, 3.0, (7, 5), 0),
    "remaja": (1.3, 3.8, (8, 6), 2),
    "dewasa": (5.0, 4.5, (9, 7), 3),
}


def palm(mb, x, y, z, s=1.0, stage="dewasa", rnd=None, detail=True, fruit=True, circle=True):
    """sawit di (x,y,z). stage: bibit | muda | remaja | dewasa. circle = piringan tanah di pangkal."""
    rnd = rnd or random.Random(int(x * 13 + y * 7))
    th, fl, (n_lo, n_hi), n_fr = STAGES[stage]
    th *= s
    fl *= s
    rot = rnd.uniform(0, 2 * math.pi)
    if stage == "bibit":
        mb.cyl(x, y, z, z + .5 * s, .33 * s, "polybag", n=8, r_top=.36 * s)
        mb.cyl(x, y, z + .5 * s, z + .52 * s, .32 * s, "kb_soil_dk", n=8)
        for k in range(4):
            frond(mb, x, y, z + .5 * s, rot + k * 1.57, fl, 1.05, .55, .2 * s, "frond3" if k % 2 else "frond", steps=4)
        return z + .5 * s + fl * .6
    if circle:
        r_c = (1.6 if stage == "dewasa" else 1.25) * s
        mb.cyl(x, y, z - .02, z + .03, r_c, "kb_soil", n=10)
    # batang bergerigi (bekas pelepah)
    top = z + th
    if th > 0:
        seg = max(2, int(th / .55))
        h = th / seg
        for k in range(seg):
            r0, r1 = (.48, .6) if k % 2 == 0 else (.5, .62)
            mb.cyl(x, y, z + k * h, z + (k + 1) * h, r0 * s, "trunk_p" if k % 2 else "trunk_p2", n=7 if detail else 5,
                   r_top=r1 * s)
        mb.cyl(x, y, z - .05, z + .45 * s, .72 * s, "trunk_p2", n=7, r_top=.5 * s)      # pangkal melebar
    else:
        mb.cyl(x, y, z, z + .55 * s, .55 * s, "trunk_p2", n=7, r_top=.38 * s)
        top = z + .45 * s
    mb.cyl(x, y, top - .1 * s, top + .45 * s, .5 * s, "crown", n=6, r_top=.2 * s)
    # tandan buah di bawah pelepah
    if fruit and n_fr:
        for k in range(n_fr):
            a = rot + k * 2 * math.pi / n_fr + .4
            tbs(mb, x + .55 * s * math.cos(a), y + .55 * s * math.sin(a), top - .75 * s, .95 * s, detail)
    if not detail:
        n_lo, n_hi = max(5, n_lo - 3), max(4, n_hi - 3)
    st = 6 if detail else 4
    for k in range(n_lo):                                  # pelepah bawah: rebah & melengkung
        a = rot + k * 2 * math.pi / n_lo
        key = ("frond2", "frond", "frond3")[k % 3]
        if stage == "dewasa" and k % 4 == 1:
            key = "frond_y"
        frond(mb, x, y, top, a, fl * rnd.uniform(.92, 1.05), .35, .5, .62 * s, key, st)
    for k in range(n_hi):                                  # pelepah atas: lebih tegak
        a = rot + (k + .5) * 2 * math.pi / n_hi
        frond(mb, x, y, top + .25 * s, a, fl * .82 * rnd.uniform(.9, 1.05), .95, .65, .5 * s,
              ("frond", "frond2")[k % 2], st)
    if detail:
        frond(mb, x, y, top + .3 * s, rot, fl * .5, 1.4, .1, .12 * s, "spear", 3)  # pucuk
    return top


def palm_obj(name, stage="dewasa", s=1.0, seed=1, fruit=True, circle=True):
    mb = W.MB(name)
    palm(mb, 0, 0, 0, s, stage, random.Random(seed), True, fruit, circle)
    return mb


def tri_grid(x0, y0, x1, y1, sp=SP, jit=.25, seed=1):
    """titik tanam pola segitiga dalam persegi panjang."""
    rnd = random.Random(seed)
    pts = []
    dy = sp * .866
    j = 0
    y = y0 + dy / 2
    while y < y1:
        x = x0 + sp / 2 + (sp / 2 if j % 2 else 0)
        while x < x1:
            pts.append((x + rnd.uniform(-jit, jit), y + rnd.uniform(-jit, jit)))
            x += sp
        y += dy
        j += 1
    return pts


def plantation(name, x0, y0, x1, y1, stage="dewasa", sp=SP, seed=1, detail=True, fruit=True, ground=True,
               skip=None):
    """blok kebun: alas rumput + piringan + pohon sawit pola segitiga. skip(x,y)->True untuk mengosongkan."""
    rnd = random.Random(seed)
    mb = W.MB(name)
    if ground:
        mb.box(x0, y0, -.6, x1, y1, 0, "kb_grass")
    for (x, y) in tri_grid(x0, y0, x1, y1, sp, .3, seed):
        if skip and skip(x, y):
            continue
        palm(mb, x, y, 0, rnd.uniform(.9, 1.08), stage, rnd, detail, fruit)
    return mb.build()


# ------------------------------------------------------------------ pekerja kebun
KB_LOOKS = {
    "pemanen": dict(skin="skin3", top="kb_shirt1", bottom="kb_pants", hat="caping"),
    "pemanen2": dict(skin="skin2", top="kb_shirt2", bottom="kb_pants2", hat="helmet_y"),
    "pengangkut": dict(skin="skin2", top="kb_shirt3", bottom="kb_pants", hat="caping"),
    "pengangkut2": dict(skin="skin3", top="kb_shirt4", bottom="kb_pants2", hat="helmet_y"),
    "penanam": dict(skin="skin1", top="kb_shirt2", bottom="kb_pants", hat="caping"),
    "pemupuk": dict(skin="skin2", top="kb_shirt1", bottom="kb_pants2", hat="caping", hijab=True),
    "mandor": dict(skin="skin2", top="c_white", bottom="kb_pants", hat="helmet_w"),
}


def worker(name, kind="pemanen", loc=(0, 0, 0), rot=0.0, s=CH_S, hold=None, load="tbs", pole=4.9):
    """pekerja kebun: kaos lengan panjang, sepatu bot karet, caping / helm, handuk di leher.
    hold: None | 'egrek' (galah panen diangkat) | 'gerobak' (dorong gerobak roda satu, muatan `load`) |
          'karung' (memanggul karung pupuk) | 'bibit' (membawa bibit polybag)."""
    wk = KB_LOOKS[kind]
    hijab = wk.get("hijab")
    look = dict(skin=wk["skin"], top=wk["top"], sleeve=wk["top"], bottom=wk["bottom"], shoe="boot",
                hair="hijab" if hijab else "short", hair_col="hij_navy" if hijab else "hair_blk", acc=())
    parts = L.character(name, look, loc, rot, s, None)
    mb = W.MB(name + "_gear")
    hz = 1.66
    if wk["hat"] == "caping":                                       # caping bambu kerucut
        mb.cyl(0, 0, hz + .12, hz + .42, .62, "caping", n=12, r_top=.04)
        mb.cyl(0, 0, hz + .1, hz + .14, .63, "caping2", n=12)
    else:
        L.ball(mb, 0, .01, hz + .06, .305, wk["hat"], seg=14, rings=7, sz=.3, sy=.3, z_from=.0)
        L.ball(mb, 0, .01, hz + .05, .36, wk["hat"], seg=14, rings=3, sz=.05, sy=.36, z_from=.6)
    if not hijab:
        L.tube(mb, 0, .02, 1.36, 1.44, .2, .16, .2, .16, "towel", n=10)       # handuk di leher
    g = mb.build()
    g.parent = parts["body"]
    parts["gear"] = g
    for sd in ("legL", "legR"):                                     # sepatu bot karet
        bb = W.MB(f"{name}_{sd}_boot")
        L.tube(bb, 0, -.02, -.8, -.42, .105, .105, .1, .1, "boot", n=8)
        bb.build().parent = parts[sd]
    if hold == "egrek":
        parts["armR"].rotation_euler = (-2.45, 0, .1)
        parts["armL"].rotation_euler = (-2.2, 0, -.1)
        pm = W.MB(name + "_egrek")
        tilt = .32
        ln = pole
        pm.cyl(0, 0, -.4, ln, .045, "pole", n=6)
        # arit melengkung di ujung
        pm.prism_y([(0, ln - .1), (.08, ln - .1), (.42, ln + .25), (.5, ln + .05), (.62, ln + .12),
                    (.4, ln + .42), (0, ln + .12)], -.02, .02, "sickle")
        pole = pm.build()
        pole.parent = parts["body"]
        pole.location = (.05, -.45, 1.78)
        pole.rotation_euler = (-tilt, 0, 0)
        parts["hold"] = pole
    elif hold == "gerobak":
        for sd, sx in (("armL", -1), ("armR", 1)):
            parts[sd].rotation_euler = (-.62, 0, 0)
        wb = wheelbarrow(name + "_wb", load)
        wb.parent = parts["body"]
        wb.location = (0, 0, 0)
        parts["hold"] = wb
    elif hold == "karung":
        hb = W.MB(name + "_sack")
        sack(hb, 0, .05, 1.6, .7, rot90=True)
        for sd in ("armL", "armR"):
            parts[sd].rotation_euler = (-2.7, 0, 0)
        ob = hb.build()
        ob.parent = parts["body"]
        parts["hold"] = ob
    elif hold == "bibit":
        hb = W.MB(name + "_bibit")
        palm(hb, 0, -.5, .85, .8, "bibit", random.Random(3))
        for sd in ("armL", "armR"):
            parts[sd].rotation_euler = (-1.0, 0, 0)
        ob = hb.build()
        ob.parent = parts["body"]
        parts["hold"] = ob
    return parts


def egrek_cut(parts, f0, f1, period=16, amp=.07):
    """gerakan menarik egrek (memotong tandan) berulang."""
    pole = parts["hold"]
    r0 = tuple(pole.rotation_euler)
    for f in range(f0, f1 + 1, period // 2):
        ph = ((f - f0) // (period // 2)) % 2
        pole.rotation_euler = (r0[0] + (amp if ph else 0), r0[1], r0[2])
        pole.keyframe_insert("rotation_euler", frame=f)
        for sd, base in (("armR", -2.45), ("armL", -2.2)):
            a = parts[sd]
            a.rotation_euler.x = base + (amp * 1.5 if ph else 0)
            a.keyframe_insert("rotation_euler", frame=f)


# ------------------------------------------------------------------ alat
def wheelbarrow(name, load=None):
    """gerobak dorong roda satu (merah, ban hitam, gagang hitam) dalam koordinat pendorong:
    pegangan di y≈-.38 (tangan), bak di depan (-y), roda paling depan. load: None|'tbs'|'bibit'|'pupuk'."""
    mb = W.MB(name)
    # bak (trapesium)
    vt = [(-.46, -.55, 1.0), (.46, -.55, 1.0), (.46, -1.62, .95), (-.46, -1.62, .95)]
    vb = [(-.27, -.72, .5), (.27, -.72, .5), (.27, -1.35, .52), (-.27, -1.35, .52)]
    mb.poly(vt + vb, [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], "wb_red")
    mb.box(-.42, -1.58, .97, .42, -.6, 1.0, "wb_red2")             # bagian dalam (gelap)
    # gagang (2 pipa) dari tangan ke roda
    for sx in (-1, 1):
        L.limb(mb, (sx * .31, -.32, .86), (sx * .3, -1.0, .55), .035, .035, "wb_red", n=6)
        L.limb(mb, (sx * .3, -1.0, .55), (sx * .1, -1.86, .3), .035, .035, "wb_red", n=6)
        L.limb(mb, (sx * .31, -.22, .9), (sx * .31, -.42, .85), .045, .045, "wb_grip", n=6)
        L.limb(mb, (sx * .27, -.82, .52), (sx * .3, -.72, .02), .03, .03, "wb_red", n=5)   # kaki
        mb.box(sx * .3 - .06, -.78, 0, sx * .3 + .06, -.66, .04, "wb_red2")
    # roda depan
    wheel = W.MB(name + "_tire")
    # ban (silinder sumbu X)
    n = 12
    vs = []
    for i in range(n):
        a = 2 * math.pi * i / n
        vs += [(-.08, math.cos(a) * .3, math.sin(a) * .3), (.08, math.cos(a) * .3, math.sin(a) * .3)]
    fs = [(2 * i, 2 * ((i + 1) % n), 2 * ((i + 1) % n) + 1, 2 * i + 1) for i in range(n)]
    fs += [tuple(2 * i for i in range(n - 1, -1, -1)), tuple(2 * i + 1 for i in range(n))]
    wheel.poly(vs, fs, "wb_grip")
    vs2 = []
    for i in range(8):
        a = 2 * math.pi * i / 8
        vs2 += [(-.09, math.cos(a) * .15, math.sin(a) * .15), (.09, math.cos(a) * .15, math.sin(a) * .15)]
    fs2 = [(2 * i, 2 * ((i + 1) % 8), 2 * ((i + 1) % 8) + 1, 2 * i + 1) for i in range(8)]
    fs2 += [tuple(2 * i for i in range(7, -1, -1)), tuple(2 * i + 1 for i in range(8))]
    wheel.poly(vs2, fs2, "wb_red")
    # muatan
    if load == "tbs":
        for k, (dx, dy, dz) in enumerate(((-.2, -.85, .9), (.2, -.95, .9), (0, -1.3, .88), (-.05, -1.05, 1.15))):
            tbs(mb, dx, dy, dz, .62)
    elif load == "bibit":
        for k, (dx, dy) in enumerate(((-.2, -.85), (.2, -.95), (0, -1.3))):
            palm(mb, dx, dy, .9, .6, "bibit", random.Random(k))
    elif load == "pupuk":
        sack(mb, 0, -1.05, .95, .6)
    ob = mb.build()
    tw = wheel.build((0, -1.86, .3))
    tw.parent = ob
    ob["tire"] = tw.name
    return ob


def sack(mb, x, y, z, s=1.0, rot90=False):
    """karung pupuk putih dengan pita hijau."""
    w, d, h = (.9 * s, .55 * s, .32 * s) if not rot90 else (.55 * s, .9 * s, .32 * s)
    L.rbox(mb, x - w / 2, y - d / 2, z, x + w / 2, y + d / 2, z + h, "pupuk_w", c=.08 * s)
    if not rot90:
        mb.box(x - w * .18, y - d / 2 - .01, z + .02, x + w * .18, y + d / 2 + .01, z + h - .02, "pupuk_g")
    else:
        mb.box(x - w / 2 - .01, y - d * .18, z + .02, x + w / 2 + .01, y + d * .18, z + h - .02, "pupuk_g")


def sack_pile(name, n=(3, 2, 2), s=1.0):
    mb = W.MB(name)
    nx, ny, nz = n
    for k in range(nz):
        for i in range(nx - k):
            for j in range(ny):
                sack(mb, (i - (nx - k - 1) / 2) * .95 * s, j * .6 * s, k * .33 * s, s)
    return mb


def tbs_pile(mb, x, y, z, r=1.6, layers=3, seed=2, s=.85):
    """tumpukan TBS bentuk kubah."""
    rnd = random.Random(seed)
    for k in range(layers):
        rr = r * (1 - k / (layers + .5))
        n = max(1, int(rr * rr * 2.2))
        for i in range(n):
            a = rnd.uniform(0, 2 * math.pi)
            d = rr * math.sqrt(rnd.uniform(0, 1))
            tbs(mb, x + d * math.cos(a), y + d * math.sin(a), z + k * .5 * s, s * rnd.uniform(.85, 1.05), False)


def tph(name, n_layers=3, seed=2):
    """TPH: lantai papan + tumpukan TBS + papan nomor."""
    mb = W.MB(name)
    mb.box(-2.2, -1.6, 0, 2.2, 1.6, .18, "wood")
    for k in range(5):
        mb.box(-2.2, -1.6 + k * .66, .18, 2.2, -1.6 + k * .66 + .5, .22, "wood2")
    pile = W.MB(name + "_pile")
    tbs_pile(pile, 0, 0, .22, 1.5, n_layers, seed)
    mb.box(2.4, -.05, 0, 2.5, .05, 2.0, "wood2")
    mb.box(2.0, -.08, 1.5, 2.9, .08, 2.1, "board")
    base = mb.build()
    pl = pile.build()
    pl.parent = base
    return base, pl


def truk_tbs(name, load=True, cab="truk_cab"):
    """truk pengangkut TBS (6 roda, bak kayu terbuka), menghadap +X, panjang ±9."""
    root = bpy.data.objects.new(name, None)
    lp._link(root)
    mb = W.MB(name + "_m")
    mb.box(-4.6, -.7, .75, 3.9, .7, 1.1, "tr_chassis")
    L.rbox(mb, 1.7, -1.2, .95, 4.1, 1.2, 3.55, cab, c=.22)
    mb.box(3.75, -1.08, 2.2, 4.16, 1.08, 3.3, "glass2")
    mb.box(2.2, -1.23, 2.25, 3.4, 1.23, 3.15, "glass2")
    mb.box(4.05, -.95, 1.15, 4.2, .95, 1.85, "tr_chassis")
    mb.box(4.0, -1.22, .8, 4.3, 1.22, 1.15, "steel_dk")
    for sy in (-1, 1):
        mb.box(4.12, sy * .9 - .22, 1.3, 4.24, sy * .9 + .22, 1.55, "lamp_y")
        mb.box(3.0, sy * 1.28 - .05, 2.6, 3.25, sy * 1.28 + .05, 3.1, "tr_chassis")
    mb.box(1.72, -1.21, 1.6, 4.12, 1.21, 1.85, "wood2" if cab == "truk_cab" else "c_white")   # strip
    # bak kayu
    mb.box(-4.7, -1.3, 1.1, 1.5, 1.3, 1.3, "wood2")
    for sy in (-1, 1):
        for k in range(4):
            mb.box(-4.7, sy * 1.3 - .06, 1.3 + k * .5, 1.5, sy * 1.3 + .06, 1.3 + k * .5 + .4, "wood")
        for x in (-4.6, -3.0, -1.4, .2, 1.4):
            mb.box(x, sy * 1.3 - .1, 1.25, x + .12, sy * 1.3 + .1, 3.3, "wood2")
    for k in range(4):
        mb.box(-4.78, -1.3, 1.3 + k * .5, -4.66, 1.3, 1.3 + k * .5 + .4, "wood")
        mb.box(1.42, -1.3, 1.3 + k * .5, 1.54, 1.3, 1.3 + k * .5 + .4, "wood")
    # roda
    for x, dbl in ((3.0, False), (-2.4, True), (-3.6, True)):
        for sy in (-1, 1):
            outer = sy * (1.32 if dbl else 1.2)
            for k in range(2 if dbl else 1):
                a, b = outer - sy * (.3 + k * .33), outer - sy * k * .33
                mb.disc_y(x, max(a, b), .55, .55, .3, "tire", n=12)
            mb.disc_y(x, outer + (.02 if sy > 0 else 0), .55, .3, .02, "rim", n=8)
    ob = mb.build()
    ob.parent = root
    out = {"root": root, "body": ob, "load": None}
    lm = W.MB(name + "_load")
    rnd = random.Random(7)
    for k in range(4):                                   # gundukan TBS di bak
        nx, ny = 7 - k, 3 - (k // 2)
        for i in range(nx):
            for j in range(ny):
                x = -4.3 + (i + .5) * (5.6 / nx) + rnd.uniform(-.15, .15) + k * .15
                y = (j - (ny - 1) / 2) * .78 + rnd.uniform(-.1, .1)
                tbs(lm, x, y, 1.2 + k * .55, .78, False)
    ld = lm.build()
    ld.parent = root
    out["load"] = ld
    if not load:
        ld.scale = (1, 1, .001)
    return out


def excavator(name):
    """ekskavator buka lahan (menghadap +X). return dict root, arm (lengan berporos)."""
    root = bpy.data.objects.new(name, None)
    lp._link(root)
    mb = W.MB(name + "_m")
    for sy in (-1, 1):                                              # rantai
        L.rbox(mb, -2.2, sy * 1.15 - .4, 0, 2.2, sy * 1.15 + .4, .85, "exc_dk", c=.3)
        for k in range(9):
            mb.box(-2.0 + k * .5, sy * 1.15 - .42, .0, -1.85 + k * .5, sy * 1.15 + .42, .1, "steel_dk")
    mb.cyl(0, 0, .85, 1.05, 1.0, "exc_dk", n=12)
    L.rbox(mb, -2.0, -1.25, 1.05, 1.0, 1.25, 2.3, "exc_y", c=.15)   # badan + mesin
    L.rbox(mb, -2.3, -1.2, 1.1, -1.6, 1.2, 2.1, "exc_dk", c=.15)    # pemberat
    L.rbox(mb, .1, -1.25, 1.1, 1.6, -.05, 3.6, "exc_y", c=.1)       # kabin
    mb.box(1.58, -1.15, 2.2, 1.64, -.15, 3.4, "glass2")
    mb.box(.3, -1.27, 2.2, 1.4, -1.25, 3.4, "glass2")
    ob = mb.build()
    ob.parent = root
    am = W.MB(name + "_arm")                                         # lengan: poros di (1.0, .5, 1.6)
    am.prism_y([(0, -.25), (0, .3), (2.6, 2.2), (3.0, 2.0), (2.7, 1.6)], -.22, .22, "exc_y")
    am.prism_y([(2.75, 2.15), (3.05, 2.0), (4.1, -.6), (3.8, -.65)], -.18, .18, "exc_y")
    am.prism_y([(3.6, -.5), (4.4, -.6), (4.6, -1.2), (4.0, -1.5), (3.5, -1.1)], -.55, .55, "exc_dk")
    arm = am.build()
    arm.parent = root
    arm.location = (1.0, .55, 1.6)
    return {"root": root, "arm": arm}


def dig(exc, f0, f1, period=40):
    arm = exc["arm"]
    for f in range(f0, f1 + 1, period // 2):
        ph = ((f - f0) // (period // 2)) % 2
        arm.rotation_euler = (0, .28 if ph else -.12, 0)
        arm.keyframe_insert("rotation_euler", frame=f)


# ------------------------------------------------------------------ lahan & efek
def burnt_patch(name, x0, y0, x1, y1, seed=3):
    """lahan bekas bakar: tanah gosong, abu, tunggul hangus, bara."""
    rnd = random.Random(seed)
    mb = W.MB(name)
    mb.box(x0, y0, -.6, x1, y1, .02, "burnt")
    for k in range(int((x1 - x0) * (y1 - y0) / 70)):
        x, y = rnd.uniform(x0 + 1, x1 - 1), rnd.uniform(y0 + 1, y1 - 1)
        mb.cyl(x, y, 0, .05, rnd.uniform(1.2, 3.2), "ash", n=5)
    for k in range(int((x1 - x0) * (y1 - y0) / 60)):
        x, y = rnd.uniform(x0 + 1, x1 - 1), rnd.uniform(y0 + 1, y1 - 1)
        h = rnd.uniform(.4, 2.6)
        mb.cyl(x, y, 0, h, rnd.uniform(.18, .35), "char", n=5, r_top=.12)
        if h > 2.0:
            mb.box(x, y - .07, h * .7, x + rnd.uniform(.6, 1.2), y + .07, h * .7 + .12, "char")
    ob = mb.build()
    em = W.MB(name + "_ember")
    for k in range(int((x1 - x0) * (y1 - y0) / 90)):
        x, y = rnd.uniform(x0 + 1, x1 - 1), rnd.uniform(y0 + 1, y1 - 1)
        em.cyl(x, y, 0, .07, rnd.uniform(.25, .5), "ember", n=6)
    eo = em.build()
    eo.data.materials[0] = lp.mat("ember", emission=2.5)
    return ob, eo


def smoke(prefix, pts, n_frames, seed=5, rise=16.0, s=4.0, per=5):
    """kepulan asap: bola abu-abu naik, membesar, lalu mengecil; berulang (looping) tiap sumber."""
    rnd = random.Random(seed)
    obs = []
    life = 70
    for k_, a_ in (("smoke", .42), ("smoke2", .48)):
        m = lp.mat(k_)
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Alpha"].default_value = a_
        b.inputs["Roughness"].default_value = 1.0
    for si, (x, y, z) in enumerate(pts):
        for k in range(per):
            mb = W.MB(f"{prefix}{si}_{k}")
            mb.sphere(0, 0, 0, 1.0, "smoke" if k % 2 else "smoke2", sz=.8)
            mb.sphere(.6, .3, .35, .7, "smoke", sz=.6)
            mb.sphere(-.55, -.2, .25, .65, "smoke2", sz=.55)
            ob = mb.build((x, y, z))
            off = rnd.randint(0, life) + k * life // per
            for f in range(1 - off % life - life, n_frames + life, life):
                f_a, f_b = f, f + life
                if f_b < 1:
                    continue
                def key(fr, loc, sc, ob=ob):
                    ob.location = loc
                    ob.keyframe_insert("location", frame=fr)
                    ob.scale = (sc,) * 3
                    ob.keyframe_insert("scale", frame=fr)
                dx = rnd.uniform(-1.5, 1.5)
                key(f_a, (x, y, z + 1.2), .12 * s)
                key(f_a + int(life * .6), (x + dx * .6 + 1.2, y, z + rise * .6), s * .9)
                key(f_b - 1, (x + dx + 2.4, y, z + rise), .05)
            obs.append(ob)
    return obs


def plot_tile(name, stage="dewasa", n=3, sp=6.0, seed=1, ground="kb_grass2", sign=None, fruit=True, rim="kb_soil2"):
    """petak kebun kecil simbolis (mis. '1 hektare') di atas balok tanah. asal = tengah atas."""
    rnd = random.Random(seed)
    mb = W.MB(name)
    half = n * sp / 2
    z0 = .35                                                        # sedikit di atas tanah sekitar
    mb.box(-half, -half, -1.4, half, half, z0 - .14, rim)
    mb.box(-half + .02, -half + .02, z0 - .14, half - .02, half - .02, z0, ground)
    for i in range(n):
        for j in range(n):
            x = (i - (n - 1) / 2) * sp + (sp / 4 if j % 2 else -sp / 8)
            y = (j - (n - 1) / 2) * sp
            palm(mb, x, y, z0, .72 * rnd.uniform(.95, 1.05), stage, rnd, True, fruit)
    for sx in (-1, 1):                                              # patok sudut
        for sy in (-1, 1):
            mb.box(sx * half - .12, sy * half - .12, z0, sx * half + .12, sy * half + .12, z0 + .9, "stake")
            mb.box(sx * half - .13, sy * half - .13, z0 + .7, sx * half + .13, sy * half + .13, z0 + .85, "cal_red")
    ob = mb.build()
    if sign:
        board(name + "_sign", sign, (0, -half - .15, 0), .9).parent = ob
    return ob


def board(name, body, loc, s=1.0):
    """papan nama kebun (berdiri, menghadap -Y)."""
    mb = W.MB(name)
    w = .5 * s * len(body) + .7 * s
    for sx in (-1, 1):
        mb.box(sx * (w / 2 - .25 * s) - .07 * s, -.07 * s, 0, sx * (w / 2 - .25 * s) + .07 * s, .07 * s, 1.6 * s, "wood2")
    mb.box(-w / 2, -.08 * s, 1.1 * s, w / 2, .08 * s, 2.0 * s, "board_g")
    mb.box(-w / 2 + .08 * s, -.1 * s, 1.18 * s, w / 2 - .08 * s, -.08 * s, 1.92 * s, "board")
    ob = mb.build(loc)
    t = H.text(name + "_t", body, .6 * s, "board_g", depth=.04 * s, loc=(0, -.12 * s, 1.27 * s))
    t.parent = ob
    return ob


def calendar(name, body, loc, s=1.0, top="cal_red"):
    """kartu kalender 3D berdiri (header merah + angka)."""
    mb = W.MB(name)
    L.rbox(mb, -.8 * s, -.12 * s, 0, .8 * s, .12 * s, 1.7 * s, "cal_w", c=.08 * s)
    L.rbox(mb, -.82 * s, -.14 * s, 1.25 * s, .82 * s, .14 * s, 1.75 * s, top, c=.08 * s)
    for sx in (-.4, .4):
        mb.cyl(sx * s, 0, 1.68 * s, 1.92 * s, .06 * s, "steel_dk", n=6)
    ob = mb.build(loc)
    t = H.text(name + "_t", body, .8 * s, "lw_navy", depth=.05 * s, loc=(0, -.15 * s, .25 * s))
    t.parent = ob
    return ob


# ------------------------------------------------------------------ dunia kebun luas
EXT = 230.0                  # kebun detail sampai ±EXT
FAR = 520.0                  # kanopi jauh (LOD rendah) sampai ±FAR
ROAD_W = 7.0
ROADS_X = (0.0, -96.0, 96.0)          # jalan utara-selatan (x tetap)
ROADS_Y = (0.0, -84.0, 84.0)          # jalan barat-timur (y tetap)
TPH_POS = [(10.0, -5.6), (-30.0, 5.6), (52.0, 5.6), (5.6, -40.0), (-5.6, 34.0), (101.6, -22.0)]
HOUSES = [(-12.0, -14.0), (-21.0, -14.0), (-30.0, -14.0)]


def _on_road(x, y, pad=4.6):
    for rx in ROADS_X:
        if abs(x - rx) < ROAD_W / 2 + pad:
            return True
    for ry in ROADS_Y:
        if abs(y - ry) < ROAD_W / 2 + pad:
            return True
    return False


def build_world(seed=5, near=90.0, burnt=None, young=None, workers=True, fruit=True):
    """kebun sawit luas: jalan tanah berparit, blok kebun (detail dekat pusat, LOD makin jauh),
    TPH dengan tumpukan TBS, barak/kantor kebun. burnt / young: (x0,y0,x1,y1) blok khusus."""
    rnd = random.Random(seed)
    info = {"anchors": {}, "tph": [], "trucks": [], "workers": []}
    g = W.MB("ground")
    g.box(-FAR - 40, -FAR - 40, -2, FAR + 40, FAR + 40, -.05, "kb_far")
    g.box(-EXT, -EXT, -.6, EXT, EXT, -.02, "kb_grass")
    for rx in ROADS_X:
        g.box(rx - ROAD_W / 2, -FAR, -.6, rx + ROAD_W / 2, FAR, .06, "road_dirt")
        for sx in (-1, 1):
            g.box(rx + sx * (ROAD_W / 2 + .3) - .6, -FAR, -.6, rx + sx * (ROAD_W / 2 + .3) + .6, FAR, -.01, "canal")
    for ry in ROADS_Y:
        g.box(-FAR, ry - ROAD_W / 2, -.6, FAR, ry + ROAD_W / 2, .07, "road_dirt")
        for sy in (-1, 1):
            g.box(-FAR, ry + sy * (ROAD_W / 2 + .3) - .6, -.6, FAR, ry + sy * (ROAD_W / 2 + .3) + .6, -.005, "canal")
    for rx in ROADS_X:                                              # bekas roda di jalan
        for sx in (-1.1, 1.1):
            g.box(rx + sx - .25, -FAR, .06, rx + sx + .25, FAR, .075, "road_dirt2")
    g.build()
    special = [b for b in (burnt, young) if b]

    def skip(x, y):
        if _on_road(x, y):
            return True
        for (a0, b0, a1, b1) in special:
            if a0 - 2 < x < a1 + 2 and b0 - 2 < y < b1 + 2:
                return True
        for hx, hy in HOUSES:
            if abs(x - hx) < 7 and abs(y - hy) < 7:
                return True
        for tx, ty in TPH_POS:
            if abs(x - tx) < 4.5 and abs(y - ty) < 4.5:
                return True
        return False

    # kebun: grid potongan 60x60, detail tergantung jarak ke pusat
    step = 60.0
    k = 0
    for i in range(int(-FAR // step), int(FAR // step) + 1):
        for j in range(int(-FAR // step), int(FAR // step) + 1):
            x0, y0 = i * step, j * step
            cx, cy = x0 + step / 2, y0 + step / 2
            d = max(abs(cx), abs(cy))
            if d > FAR:
                continue
            mb = W.MB(f"blk{k}")
            k += 1
            sp = SP if d < EXT else SP * 1.15
            for (x, y) in tri_grid(x0, y0, x0 + step, y0 + step, sp, .3, seed + k):
                if skip(x, y):
                    continue
                if d < near:
                    palm(mb, x, y, 0, rnd.uniform(.92, 1.08), "dewasa", rnd, True, fruit)
                elif d < EXT:
                    palm(mb, x, y, 0, rnd.uniform(.92, 1.08), "dewasa", rnd, False, fruit)
                else:                                           # kanopi jauh: tanpa batang detail
                    palm(mb, x, y, 0, rnd.uniform(.95, 1.1), "dewasa", rnd, False, False, circle=False)
            if mb.v:
                mb.build()
    if burnt:
        info["burnt"] = burnt_patch("burnt", *burnt)
    if young:
        info["young"] = plantation("young", *young, stage="muda", seed=11, ground=True)
    # TPH
    for t, (x, y) in enumerate(TPH_POS):
        b, p = tph(f"tph{t}", 2 + t % 2, t)
        b.location = (x, y, .07)
        b.rotation_euler.z = 0 if abs(y) < abs(x) else math.pi / 2
        info["tph"].append((b, p))
    # barak / kantor kebun
    for h, (x, y) in enumerate(HOUSES):
        mb = W.MB(f"house{h}")
        mb.box(-3.2, -2.6, 0, 3.2, 2.6, .5, "kb_soil2")
        mb.box(-3.0, -2.4, .5, 3.0, 2.4, 3.4, ("wall_cream", "wall_mint", "wall_white")[h % 3])
        mb.prism_x([(-2.9, 3.4), (2.9, 3.4), (0, 5.3)], -3.4, 3.4, ("roof_red", "roof_blue", "roof_red2")[h % 3])
        mb.box(-.6, -2.45, .5, .6, -2.4, 2.6, "wood2")
        for sx in (-1.9, 1.9):
            mb.box(sx - .55, -2.45, 1.4, sx + .55, -2.4, 2.4, "glass")
        mb.build((x, y, 0))
    info["anchors"]["KEBUN"] = (40.0, 40.0, 9.0)
    return info


def road_trucks(n_frames, seed=4, fps=30, speed=7.0, routes=None):
    """truk TBS lalu-lalang di jalan kebun."""
    rnd = random.Random(seed)
    routes = routes or [((-200, -2.0), (200, -2.0)), ((200, 2.0), (-200, 2.0)), ((-2.0, 200), (-2.0, -200)),
                        ((98.0, -200), (98.0, 200))]
    out = []
    for k, (p0, p1) in enumerate(routes):
        tr = truk_tbs(f"rtk{k}", load=True, cab=("truk_cab", "truk_cab2")[k % 2])
        rt = tr["root"]
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        rt.rotation_euler.z = ang
        d = math.dist(p0, p1)
        off = rnd.uniform(.15, .55)
        f_total = int(d / speed * fps)
        f_start = -int(off * f_total)
        rt.location = (p0[0], p0[1], .07)
        rt.keyframe_insert("location", frame=f_start)
        rt.location = (p1[0], p1[1], .07)
        rt.keyframe_insert("location", frame=f_start + f_total)
        out.append(tr)
    return out
