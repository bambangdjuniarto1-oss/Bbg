"""Kota BANDUNG diorama besar untuk video "Sponsor terbesar Persib itu kamu" (melayang di dunia neon).
Kawasan (bukan replika arsitektur persis, gaya low-poly):
  - Timur laut : Stadion GBLA (tribun penuh bobotoh biru) + plaza dengan arus bobotoh.
  - Barat laut : Gedung Sate (badan putih memanjang, menara tengah beratap susun + tusuk sate) + lapangan depan.
  - Barat      : Jembatan layang kabel (gaya Pasupati) di tepi utara.
  - Tengah     : Jl. Asia Afrika (boulevard utama) — deret papan reklame 16 sponsor di sisi timur, toko resmi PERSIB
                 (fasad biru, logo, etalase jersey, antrean bobotoh), deret bangunan kolonial gaya Braga di selatan.
  - Barat daya : Alun-alun (rumput sintetis hijau) + Masjid Raya (dua menara kembar).
  - Tenggara   : menara kaca NexAI (logo menyala di puncak).
  - Selatan    : permukiman padat + ruko.
  - Jalan penuh lalu lintas: mobil + motor bobotoh jaket biru.
Semua permukaan atas = G0. Return dict titik penting untuk kamera & objek adegan."""
import math
import os
import random
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowpoly as lp  # noqa: E402
import world as W  # noqa: E402
import world_ctd as C  # noqa: E402
import world_gta as G  # noqa: E402
import world_hotel as H  # noqa: E402
import world_laundry as L  # noqa: E402
import world_ojl as OJ  # noqa: E402
import world_prk as R  # noqa: E402
import world_psb as P  # noqa: E402
import world_vap as V  # noqa: E402

G0 = OJ.G0
X0, Y0, X1, Y1 = OJ.X0, OJ.Y0, OJ.X1, OJ.Y1
BLV = ((-4.0, 6.0), (-52.0, -44.0))
AVE = ((-6.0, 4.0), (58.0, 66.0))
OJ.BLV, OJ.AVE = BLV, AVE
GBLA_C, GBLA_S = (96.0, 45.0), .74          # pusat & skala stadion
SATE_C = (-64.0, 46.0)                      # Gedung Sate (menghadap -y)
STORE_C = (-30.0, 17.5)                     # toko PERSIB (muka di y=STORE_C[1]-5, menghadap jalan)
ALUN = (-60.0, -30.0, -40.0, -19.0)         # alun-alun x0, x1, y0, y1
MASJID_C = (-78.0, -25.0)
NEXAI_C = (96.0, -24.0)
BOARD_X = [7.5 + 6.6 * k for k in range(8)]  # papan sponsor (2 sisi Jl. Asia Afrika)
SPONSORS = ["sp01", "sp03", "sp02", "sp04", "sp05", "sp06", "sp07", "sp08",
            "sp09", "sp10", "sp11", "sp12", "sp13", "sp14", "sp15", "sp16"]

lp.PAL.update({
    "bb_blue": "#1F4FD1", "bb_blue2": "#2D6BFF", "bb_navy": "#0C1D4F", "bb_white": "#F2F5FA",
    "sate_w": "#F1ECE2", "sate_trim": "#D9CFBE", "sate_roof": "#4A4038", "sate_win": "#2E3A4A",
    "masjid_w": "#F3EEE4", "masjid_g": "#2F8F5B", "alun": "#4CC36A", "alun2": "#3FAE5C",
    "braga1": "#F2E3C6", "braga2": "#E9D2A8", "braga3": "#F4F0E6", "braga_tr": "#8C5A3C",
    "store_bl": "#1F4FD1", "store_gl": "#9CC8F0", "nx_glass": "#18263F", "nx_line": "#29C5F6",
    "bridge": "#C9CCD2", "pad_lt": "#D6E4FF", "cable": "#F2F4F7", "board_pole": "#3A3F4A", "board_w": "#FFFFFF",
})

# bobotoh: kaus jersey biru Persib (kerah putih via lengan putih tipis tidak ada -> lengan biru)
L.LOOKS["bobotoh"] = dict(skin="skin2", top="bb_blue", sleeve="bb_blue", bottom="c_black", shoe="shoe_w", hair="short",
                          hair_col="hair_blk", acc=())
L.LOOKS["bobotoh2"] = dict(skin="skin1", top="bb_blue2", sleeve="bb_blue2", bottom="c_denim", shoe="shoe_w", hair="cap",
                           hair_col="bb_navy", acc=())
L.LOOKS["bobotoh3"] = dict(skin="skin3", top="bb_blue", sleeve="bb_blue", bottom="c_navy", shoe="shoe_dk", hair="hijab",
                           hair_col="bb_navy", acc=())
L.LOOKS["bobotoh4"] = dict(skin="skin1", top="bb_white", sleeve="bb_white", bottom="c_black", shoe="shoe_w", hair="long",
                           hair_col="hair_blk", acc=())
BOBO = ("bobotoh", "bobotoh2", "bobotoh3", "bobotoh", "bobotoh2", "bobotoh4")
FANS = ("bb_blue", "bb_blue", "bb_blue2", "bb_navy", "bb_white", "bb_blue")


def _text(name, body, loc, size, key="tee", em=0.0, rot=(math.pi / 2, 0, 0), depth=.12):
    return H.text(name, body, size, key, depth=depth, loc=loc, rot=rot, emission=em)


def bobotoh(name, loc, rot=0.0, pose=None, look=None, hold=None):
    p = L.character(name, look or BOBO[sum(map(ord, name)) % len(BOBO)], loc, rot, hold=hold)
    if pose:
        L.pose(p, pose)
    return p


def bobotoh_rider(name, loc, rot_z=0.0, s=.8, color=None):
    rnd = random.Random(name)
    return R.rider_motor(name, loc, rot_z, color or rnd.choice(R.BIKE_COLS), "bb_blue", rnd.choice(("bb_blue2", "bb_white")), s)


OJ.ojol_rider = bobotoh_rider          # lalu lintas kota: motor bobotoh jaket biru


def crowd_patch(name, x0, y0, x1, y1, n, seed=1, z=None, s=.62):
    """kerumunan mini bobotoh (murah) di area persegi."""
    rnd = random.Random(seed)
    mb = W.MB(name)
    zz = G0 if z is None else z
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        C.mini_person(mb, x, y, zz, s * rnd.uniform(.9, 1.1), rnd.choice(FANS), rnd.choice(("skin1", "skin2", "skin3")))
        if rnd.random() < .25:
            mb.box(x - .05, y - .05, zz + .45 * s, x + .05, y + .05, zz + .95 * s, rnd.choice(("bb_blue", "bb_white")))
    return mb.build()


# ------------------------------------------------------------------ stadion GBLA (skala & posisi)
def gbla():
    before = set(bpy.data.objects)
    info = P.stadium("gbla", crowd=True, seed=4, n_seg=96, lights=True, ground=False)
    cx, cy = GBLA_C
    s = GBLA_S
    for ob in set(bpy.data.objects) - before:
        if ob.parent is None:
            ob.location = (cx + ob.location.x * s, cy + ob.location.y * s, G0 + ob.location.z * s)
            ob.scale = (ob.scale.x * s, ob.scale.y * s, ob.scale.z * s)
            if ob.type == "LIGHT":
                ob.data.energy *= s * s
    info["center"] = (cx, cy)
    info["top"] = G0 + info["z_top"] * s
    info["a"], info["b"] = info["a_out"] * s, info["b_out"] * s
    # plaza + arus bobotoh menuju stadion
    pz = W.MB("gbla_plaza")
    pz.box(cx - 30, cy - 30, G0 - .01, cx + 28, cy - 18, G0 + .06, "pk_walk")
    pz.build()
    info["crowd"] = crowd_patch("gbla_crowd", cx - 26, cy - 29, cx + 24, cy - 21, 340, 7)
    sg = _text("gbla_tx", "STADION GBLA", (cx, cy - info["b"] - .4, G0 + info["top"] - G0 + 1.2), 2.2, "bb_white", 1.5)
    info["sign"] = sg
    return info


# ------------------------------------------------------------------ Gedung Sate
def gedung_sate():
    cx, cy = SATE_C
    b = W.MB("sate")
    b.box(cx - 22, cy - 5, G0, cx + 22, cy + 5, G0 + 7.0, "sate_w")                 # sayap memanjang
    b.box(cx - 22.3, cy - 5.3, G0 + 6.8, cx + 22.3, cy + 5.3, G0 + 7.4, "sate_trim")
    b.prism_x([(cy - 5.3, G0 + 7.4), (cy + 5.3, G0 + 7.4), (cy, G0 + 10.2)], cx - 22, cx + 22, "sate_roof")
    for k in range(-10, 11):                                                        # jendela lengkung (gelap)
        if abs(k) <= 2:
            continue
        x = cx + k * 2.0
        b.box(x - .45, cy - 5.06, G0 + 1.0, x + .45, cy - 5.0, G0 + 2.8, "sate_win")
        b.box(x - .45, cy - 5.06, G0 + 3.9, x + .45, cy - 5.0, G0 + 5.7, "sate_win")
    # badan tengah menjorok + menara beratap susun
    b.box(cx - 6, cy - 7.5, G0, cx + 6, cy + 6, G0 + 10.0, "sate_w")
    b.box(cx - 6.3, cy - 7.8, G0 + 9.8, cx + 6.3, cy + 6.3, G0 + 10.4, "sate_trim")
    for k in range(5):
        x = cx - 4 + k * 2.0
        b.box(x - .5, cy - 7.56, G0 + 1.0, x + .5, cy - 7.5, G0 + 4.2, "sate_win")
        b.box(x - .5, cy - 7.56, G0 + 5.4, x + .5, cy - 7.5, G0 + 8.4, "sate_win")
    z = G0 + 10.4
    for (w, h) in ((5.2, 2.2), (4.0, 2.0), (2.8, 1.8)):                            # atap susun (meru)
        b.box(cx - w / 2 + .5, cy - w / 2 + .5, z, cx + w / 2 - .5, cy + w / 2 - .5, z + h * .45, "sate_w")
        b.poly([(cx - w / 2 - .6, cy - w / 2 - .6, z + h * .45), (cx + w / 2 + .6, cy - w / 2 - .6, z + h * .45),
                (cx + w / 2 + .6, cy + w / 2 + .6, z + h * .45), (cx - w / 2 - .6, cy + w / 2 + .6, z + h * .45),
                (cx, cy, z + h * 1.3)], [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (3, 2, 1, 0)], "sate_roof")
        z += h * .95
    b.cyl(cx, cy, z, z + 4.2, .1, "psb_gold", n=6)                                 # tusuk sate
    for k in range(6):
        b.sphere(cx, cy, z + .6 + k * .55, .22, "psb_gold")
    b.build()
    # halaman depan + jalan setapak + air mancur
    lw = W.MB("sate_lawn")
    lw.box(cx - 24, cy - 26, G0 - .01, cx + 24, cy - 8, G0 + .04, "alun")
    lw.box(cx - 2, cy - 26, G0 - .01, cx + 2, cy - 7.5, G0 + .06, "pk_walk")
    lw.cyl(cx, cy - 17, G0, G0 + .5, 2.6, "sate_trim", n=16)
    lw.cyl(cx, cy - 17, G0 + .5, G0 + .55, 2.2, "store_gl", n=16)
    lw.build()
    _text("sate_tx", "GEDUNG SATE", (cx, cy - 26.2, G0 + .1), 1.3, "sate_roof", 0.0, rot=(math.pi / 2, 0, 0))
    return {"center": (cx, cy), "spire": (cx, cy, z + 4.2), "front": (cx, cy - 8, G0)}


# ------------------------------------------------------------------ alun-alun + Masjid Raya
def alun_alun():
    x0, x1, y0, y1 = ALUN
    g = W.MB("alun")
    for k in range(6):
        g.box(x0 + k * (x1 - x0) / 6, y0, G0 - .01, x0 + (k + 1) * (x1 - x0) / 6, y1, G0 + .05,
              "alun" if k % 2 else "alun2")
    g.box(x0 - 1.2, y0 - 1.2, G0 - .02, x1 + 1.2, y1 + 1.2, G0 + .03, "pk_walk")
    g.build()
    crowd_patch("alun_crowd", x0 + 1, y0 + 1, x1 - 1, y1 - 1, 260, 21)
    mx, my = MASJID_C
    m = W.MB("masjid")
    m.box(mx - 8, my - 9, G0, mx + 8, my + 9, G0 + 7.5, "masjid_w")
    m.box(mx - 8.4, my - 9.4, G0 + 7.5, mx + 8.4, my + 9.4, G0 + 8.0, "sate_trim")
    m.poly([(mx - 7, my - 7, G0 + 8.0), (mx + 7, my - 7, G0 + 8.0), (mx + 7, my + 7, G0 + 8.0), (mx - 7, my + 7, G0 + 8.0),
            (mx, my, G0 + 13.5)], [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)], "masjid_g")
    m.sphere(mx, my, G0 + 13.8, .5, "psb_gold")
    for sy in (-1, 1):                                                                 # menara kembar
        ty = my + sy * 12
        m.box(mx + 4 - 1.3, ty - 1.3, G0, mx + 4 + 1.3, ty + 1.3, G0 + 30, "masjid_w")
        for zz in (8, 16, 24):
            m.box(mx + 4 - 1.5, ty - 1.5, G0 + zz, mx + 4 + 1.5, ty + 1.5, G0 + zz + .5, "sate_trim")
        m.box(mx + 4 - 1.6, ty - 1.6, G0 + 30, mx + 4 + 1.6, ty + 1.6, G0 + 31.6, "masjid_w")
        m.cyl(mx + 4, ty, G0 + 31.6, G0 + 34.5, 1.3, "masjid_g", n=8, r_top=0.0)
        m.cyl(mx + 4, ty, G0 + 34.5, G0 + 35.6, .08, "psb_gold", n=6)
    m.build()
    return {"center": ((x0 + x1) / 2, (y0 + y1) / 2), "masjid": (mx, my)}


# ------------------------------------------------------------------ deret kolonial (gaya Braga)
def braga(seed=31):
    rnd = random.Random(seed)
    b = W.MB("braga")
    y = BLV[0][0] - 2.6                                   # muka bangunan menghadap +y (ke jalan)
    x = -58.0
    while x < -10:
        w = rnd.uniform(5.5, 7.5)
        h = rnd.uniform(6.5, 9.5)
        col = rnd.choice(("braga1", "braga2", "braga3"))
        b.box(x, y - 9, G0, x + w - .3, y, G0 + h, col)
        b.box(x - .1, y - .2, G0 + h, x + w - .2, y + .3, G0 + h + .7, "braga_tr")      # list atap
        if rnd.random() < .5:                                                            # kubah/menara sudut
            b.cyl(x + w / 2, y - 1.5, G0 + h + .7, G0 + h + 2.6, 1.1, col, n=8, r_top=.2)
        for k in range(2):
            wx = x + .9 + k * (w - 2.4) / 1.0 * .5
            b.box(wx, y + .01, G0 + 3.8, wx + 1.0, y + .06, G0 + 5.8, "sate_win")
        b.box(x + .8, y + .01, G0, x + w - 1.1, y + .06, G0 + 2.8, "store_gl")             # etalase
        b.box(x + .4, y, G0 + 2.9, x + w - .7, y + 1.4, G0 + 3.1, "braga_tr")            # kanopi
        x += w
    b.build()
    _text("braga_tx", "JALAN BRAGA", (-34, y + 1.5, G0 + 9.8), 1.1, "braga_tr", 0.0, rot=(math.pi / 2, 0, math.pi))
    return {"center": (-34.0, y)}


# ------------------------------------------------------------------ toko PERSIB
def persib_store():
    cx, cy = STORE_C
    yf = cy - 5.0                                         # muka toko (menghadap -y, ke Jl. Asia Afrika)
    b = W.MB("store")
    b.box(cx - 10, yf, G0, cx + 10, cy + 6, G0 + 9.0, "store_bl")
    b.box(cx - 10.3, yf - .3, G0 + 8.6, cx + 10.3, cy + 6.3, G0 + 9.4, "bb_white")
    b.box(cx - 8.5, yf - .05, G0 + .3, cx + 8.5, yf, G0 + 5.6, "store_gl")
    b.box(cx - 1.4, yf - .06, G0, cx + 1.4, yf - .01, G0 + 3.6, "bb_navy")
    b.box(cx - 10, yf - 3.0, G0 - .01, cx + 10, yf, G0 + .08, "pk_walk")
    so = b.build()
    V.glow(so, {"store_gl": .25})
    lg = P.logo_card("store_lg", "lg_persib", 2.4, (cx - 6.0, yf - .25, G0 + 5.9), 0.0, plate=None, em=1.4)
    tx = _text("store_tx", "PERSIB STORE", (cx + 1.6, yf - .25, G0 + 6.4), 1.25, "bb_white", 2.0)
    # jersey di etalase
    for k, x in enumerate((-6.0, -3.0, 3.0, 6.0)):
        P.jersey(f"store_j{k}", (cx + x, yf - .35, G0 + .8), .55, "psb_blue" if k % 2 == 0 else "psb_white",
                 "psb_white" if k % 2 == 0 else "psb_blue", ("7", "10", "25", "14")[k])
    # antrean bobotoh
    q = []
    for k in range(7):
        q.append(bobotoh(f"store_q{k}", (cx - 9.0 - k * 1.05, yf - 1.6, G0), -math.pi / 2 + .2 * ((k % 3) - 1)))
    return {"center": (cx, cy), "front": (cx, yf, G0), "logo": lg, "sign": tx, "queue": q}


# ------------------------------------------------------------------ menara NexAI
def nexai_tower():
    cx, cy = NEXAI_C
    t = W.MB("nexai")
    t.box(cx - 7, cy - 7, G0, cx + 7, cy + 7, G0 + 46, "nx_glass")
    for z in range(4, 46, 3):
        t.box(cx - 7.05, cy - 7.05, G0 + z, cx + 7.05, cy - 6.95, G0 + z + .12, "nx_line")
    for k in range(-3, 4):
        t.box(cx + k * 2 - .08, cy - 7.1, G0 + 2, cx + k * 2 + .08, cy - 7.0, G0 + 45, "nx_line")
    t.box(cx - 9, cy - 9, G0, cx + 9, cy + 9, G0 + 4, "ct_white")
    to = t.build()
    V.glow(to, {"nx_line": 3.0})
    lg = P.logo_card("nx_logo", "sp10", 6.0, (cx, cy - 7.5, G0 + 47.0), 0.0, plate="plate_w", em=1.2, plate_em=.9)
    return {"center": (cx, cy), "logo": lg, "crown": (cx, cy - 8, G0 + 50)}


# ------------------------------------------------------------------ jembatan kabel (gaya Pasupati)
def bridge():
    y = 64.0
    b = W.MB("bridge")
    b.box(-122, y - 3, G0 + 7.5, -70, y + 3, G0 + 8.3, "bridge")
    for x in range(-118, -70, 8):
        b.box(x - .6, y - 1.2, G0, x + .6, y + 1.2, G0 + 7.5, "bridge")
    px = -96
    b.poly([(px - 3, y - 2, G0 + 8.3), (px - 3, y + 2, G0 + 8.3), (px, y, G0 + 24)], [(0, 1, 2)], "bridge")
    b.poly([(px + 3, y - 2, G0 + 8.3), (px + 3, y + 2, G0 + 8.3), (px, y, G0 + 24)], [(0, 1, 2)], "bridge")
    b.box(px - 3.2, y - 2.2, G0 + 8.3, px + 3.2, y + 2.2, G0 + 9.0, "bridge")
    for k in range(1, 9):                                 # kabel: pita tipis dari pylon ke lantai jembatan
        for sx in (-1, 1):
            x1 = px + sx * k * 2.8
            z1, zt = G0 + 8.4, G0 + 23 - k * .35
            for dy in (-.9, .9):
                b.poly([(x1, y + dy, z1 - .06), (x1, y + dy, z1 + .06), (px, y + dy * .2, zt + .06), (px, y + dy * .2, zt - .06)],
                       [(0, 1, 2, 3)], "cable")
                b.poly([(x1, y + dy - .06, z1), (x1, y + dy + .06, z1), (px, y + dy * .2 + .06, zt), (px, y + dy * .2 - .06, zt)],
                       [(0, 1, 2, 3)], "cable")
    b.build()
    return {"pylon": (px, y, G0 + 24)}


# ------------------------------------------------------------------ papan reklame 16 sponsor
def sponsor_boards():
    """16 papan reklame putih berlogo sponsor (8 per sisi Jl. Asia Afrika, menghadap jalan). Return list root."""
    out = []
    for i, img in enumerate(SPONSORS):
        side = i % 2                       # 0: sisi utara (menghadap -y), 1: sisi selatan (menghadap +y)
        x = BOARD_X[i // 2]
        y = BLV[0][1] + 1.7 if side == 0 else BLV[0][0] - 1.7
        rot = 0.0 if side == 0 else math.pi
        root = bpy.data.objects.new(f"bd{i}", None)
        lp._link(root)
        mb = W.MB(f"bd{i}_s")
        mb.box(-.15, -.15, 0, .15, .15, 3.9, "board_pole")
        L.rbox(mb, -3.0, -.12, 3.8, 3.0, .12, 7.0, "board_w", c=.3)
        so = mb.build(parent=root)
        V.glow(so, {"board_w": .7})
        ip = G.img_plane(f"bd{i}_i", img, h=2.8, loc=(0, -.14, 4.0), em=1.25)
        ip.parent = root
        if ip["w"] > 5.5:
            sc = 5.5 / ip["w"]
            ip.scale = (sc, 1, sc)
            ip.location.z = 4.0 + (2.8 - 2.8 * sc) / 2
        root.location = (x, y, G0)
        root.rotation_euler.z = rot
        out.append(root)
    return out


# ------------------------------------------------------------------ gedung kota (hindari landmark)
def cbd(seed=5):
    rnd = random.Random(seed)
    b = W.MB("bd_cbd")
    keep = [(GBLA_C[0] - 32, GBLA_C[1] - 32, GBLA_C[0] + 32, GBLA_C[1] + 30),
            (SATE_C[0] - 26, SATE_C[1] - 28, SATE_C[0] + 26, SATE_C[1] + 8),
            (STORE_C[0] - 12, STORE_C[1] - 9, STORE_C[0] + 12, STORE_C[1] + 8),
            (-124, 58, -66, 70)]
    spots = [(x, y) for x in range(-116, 122, 12) for y in (16, 30, 44, 58, 74)]
    spots += [(x, y) for x in range(-116, 122, 12) for y in (-16, -28)]
    for (x, y) in spots:
        if any(a0 < x < a1 and b0 < y < b1 for a0, b0, a1, b1 in keep):
            continue
        if any(a0 - 5 < x < a1 + 5 for a0, a1 in AVE):
            continue
        if y < 0 and (-62 < x < -10 or -90 < x < -66 or abs(x - NEXAI_C[0]) < 12):
            continue
        w, d = rnd.uniform(6.5, 9), rnd.uniform(6.5, 9)
        h = rnd.uniform(12, 34) if y > 24 else rnd.uniform(8, 18)
        b.box(x - w / 2, y - d / 2, G0, x + w / 2, y + d / 2, G0 + h,
              rnd.choice(("ct_glass", "ct_glass2", "ct_glass3", "ct_con", "ct_white")))
        b.box(x - w / 2 - .2, y - d / 2 - .2, G0 + h, x + w / 2 + .2, y + d / 2 + .2, G0 + h + .5, "ct_con")
        for z in range(4, int(h) - 2, 4):
            b.box(x - w / 2 - .05, y - d / 2 - .05, G0 + z, x + w / 2 + .05, y - d / 2, G0 + z + .25, "ct_con")
    b.build()


def kampung(seed=17):
    """permukiman padat di selatan (di luar alun-alun/masjid) + ruko di tepi boulevard selatan."""
    rnd = random.Random(seed)
    walls = ("wall_cream2", "wall_peach", "wall_beige", "laundry_wall")
    roofs = ("roof_orange", "roof_brown")
    k = 0
    T = OJ.T
    for y in range(-90, -56, 9):
        for x in range(-118, 120, 8):
            if any(a0 - 3 < x < a1 + 3 for a0, a1 in AVE) or rnd.random() < .12:
                continue
            mb, h = T.house(f"kp{k}", rnd.uniform(5.2, 6.4), rnd.uniform(5.4, 6.4), rnd, rnd.choice(walls), rnd.choice(roofs))
            mb.build((x + rnd.uniform(-.5, .5), y + rnd.uniform(-.5, .5), G0 - T.Z))
            k += 1


def hills():
    """perbukitan hijau di tepi utara (cekungan Bandung)."""
    h = W.MB("bd_hills")
    rnd = random.Random(41)
    for k in range(9):
        x = X0 + 14 + k * 28 + rnd.uniform(-4, 4)
        h.cyl(x, Y1 + 24, -3.8, rnd.uniform(14, 26), rnd.uniform(14, 20), rnd.choice(("tree_l", "tree_m")), n=7, r_top=1.5)
    h.build()


def city_bdg(n_frames, seed=3):
    V.setup_day_light()
    OJ.base_plate()
    info = {"gbla": gbla(), "sate": gedung_sate(), "alun": alun_alun(), "braga": braga(), "store": persib_store(),
            "nexai": nexai_tower(), "bridge": bridge(), "boards": sponsor_boards()}
    cbd()
    kampung()
    _st = C.street_tree

    def _tree(mb, x, y, s=1.0, rnd=None):          # jangan menutupi toko PERSIB & deret papan sponsor
        if BLV[0][0] - 3 < y < BLV[0][1] + 3 and (STORE_C[0] - 14 < x < STORE_C[0] + 14 or 2 < x < 58):
            return
        _st(mb, x, y, s, rnd)
    C.street_tree = _tree
    info["movers"] = OJ.dressing(n_frames)
    C.street_tree = _st
    sc = bpy.context.scene
    for bg in sc.world.node_tree.nodes:
        if bg.type == "BACKGROUND" and bg.name == "Background":
            bg.inputs["Color"].default_value = lp.hex_rgba("#121A3A")
            bg.inputs["Strength"].default_value = .8
    return info


# ------------------------------------------------------------------ properti panggung neon
def jersey(name, loc=(0, 0, 0), s=1.0, key_="bb_blue", trim="bb_white", chest=None, back_text=None):
    """jersey Persib berdiri (menghadap -Y, pivot bawah-tengah): siluet kaus, kerah & manset putih, logo Persib di
    dada kiri, logo apparel di dada kanan, slot sponsor dada (chest = nama tekstur logo atau None).
    Return dict(root, chest_loc (lokal), w, h)."""
    root = bpy.data.objects.new(name, None)
    lp._link(root)
    mb = W.MB(name + "_b")
    Pp = [(-1.25, 0), (1.25, 0), (1.25, 2.2), (2.05, 1.75), (2.45, 2.45), (1.45, 3.35), (.55, 3.5), (0, 3.15),
          (-.55, 3.5), (-1.45, 3.35), (-2.45, 2.45), (-2.05, 1.75), (-1.25, 2.2)]
    mb.prism_y([(x * s, z * s) for x, z in Pp], -.16 * s, .16 * s, key_)
    mb.prism_y([(x * s, z * s) for x, z in ((-.55, 3.5), (0, 3.15), (.55, 3.5), (.42, 3.56), (0, 3.26), (-.42, 3.56))],
               -.18 * s, .18 * s, trim)
    for sx in (-1, 1):
        mb.prism_y([(sx * x * s, z * s) for x, z in ((2.05, 1.75), (2.25, 2.1), (2.37, 2.22), (2.13, 1.87))],
                   -.18 * s, .18 * s, trim)
        mb.box(sx * 1.22 * s - .03 * s, -.17 * s, .05 * s, sx * 1.22 * s + .03 * s, -.16 * s, 2.15 * s, trim)
    bo = mb.build(parent=root)
    V.glow(bo, {key_: .25, trim: .4})
    cr = G.img_plane(name + "_cr", "lg_persib", h=.55 * s, loc=(-.62 * s, -.18 * s, 2.45 * s), em=1.3)
    cr.parent = root
    ap = G.img_plane(name + "_ap", "sp05", h=.42 * s, loc=(.62 * s, -.18 * s, 2.52 * s), em=1.3)
    ap.parent = root
    out = {"root": root, "chest_loc": (0, -.2 * s, 1.35 * s), "w": 4.9 * s, "h": 3.55 * s}
    if chest:
        out["chest"] = chest_logo(name + "_ch", chest, s)
        out["chest"].parent = root
        out["chest"].location = out["chest_loc"]
    root.location = loc
    return out


def chest_logo(name, img, s=1.0, h=.62):
    """logo sponsor dada (kartu putih membulat tipis)."""
    return P.logo_card(name, img, h * s, (0, 0, 0), 0.0, plate="plate_w", pad=.14 * s, em=1.3, plate_em=.8)


def balance(name, loc=(0, 0, 0), arm=4.2, post=6.0, pan_r=1.9):
    """timbangan neon: tiang + balok (berporos di puncak) + 2 piring tergantung (tetap tegak).
    Return dict(root, beam, pans=[L, R], set(f, ang)) — ang>0: piring kanan turun."""
    root = bpy.data.objects.new(name, None)
    lp._link(root)
    mb = W.MB(name + "_post")
    mb.cyl(0, 0, 0, .35, 1.6, "n_gold", n=20)
    mb.cyl(0, 0, .35, post, .22, "n_gold", n=10)
    mb.sphere(0, 0, post + .1, .42, "n_gold")
    po = mb.build(parent=root)
    V.glow(po, {"n_gold": 3.0})
    bm = W.MB(name + "_beam")
    bm.box(-arm - .2, -.16, -.16, arm + .2, .16, .16, "n_gold")
    for sx in (-1, 1):
        bm.sphere(sx * arm, 0, 0, .26, "n_gold")
    beam = bm.build(parent=root)
    V.glow(beam, {"n_gold": 4.0})
    beam.location = (0, 0, post + .1)
    pans = []
    for sx in (-1, 1):
        pm = W.MB(f"{name}_pan{sx}")
        pm.cyl(0, 0, -.2, 0, pan_r, "n_cyan", n=24, r_top=pan_r * 1.1)
        for k in range(3):
            a = 2 * math.pi * k / 3 + math.pi / 2
            r_ = pan_r * .95
            pm.poly([(r_ * math.cos(a), r_ * math.sin(a), 0), (r_ * math.cos(a) + .05, r_ * math.sin(a), 0),
                     (.05, 0, 2.6), (0, 0, 2.6)], [(0, 1, 2, 3)], "n_cyan")
        pan = pm.build(parent=root)
        V.glow(pan, {"n_cyan": 3.0})
        pans.append(pan)

    def set_(f, ang):
        beam.rotation_euler = (0, ang, 0)
        beam.keyframe_insert("rotation_euler", frame=f)
        for sx, pan in zip((-1, 1), pans):
            pan.location = (sx * arm * math.cos(ang), 0, post + .1 - sx * arm * math.sin(ang) - 2.6)
            pan.keyframe_insert("location", frame=f)
    set_(1, 0.0)
    root.location = loc
    return {"root": root, "beam": beam, "pans": pans, "set": set_}


def cross_x(name, loc, s=1.0, em=6.0):
    """tanda silang merah menyala (menghadap -Y)."""
    mb = W.MB(name)
    for sg in (-1, 1):
        mb.poly([(-1.0 * s, -.1, -1.0 * s * sg - .18 * s * sg), (-1.0 * s, -.1, -1.0 * s * sg + .18 * s * sg),
                 (1.0 * s, -.1, 1.0 * s * sg + .18 * s * sg), (1.0 * s, -.1, 1.0 * s * sg - .18 * s * sg)],
                [(0, 1, 2, 3)], "n_red")
    ob = mb.build(loc)
    V.glow(ob, {"n_red": em})
    return ob


def pad(name, w, d, loc, key_="n_cyan", em=1.0):
    """alas menyala persegi (supaya kerumunan mini kontras di panggung gelap)."""
    mb = W.MB(name)
    mb.box(-w / 2, -d / 2, 0, w / 2, d / 2, .06, key_)
    ob = mb.build(loc)
    V.glow(ob, {key_: em})
    return ob


def mini_grid(name, n, cols, loc=(0, 0, 0), sp=.62, s=.55, rows_obj=True, seed=3):
    """grid n bobotoh mini (baris-baris terpisah supaya bisa muncul bergelombang). Return list objek baris."""
    rnd = random.Random(seed)
    rows = []
    nrow = (n + cols - 1) // cols
    k = 0
    for r in range(nrow):
        mb = W.MB(f"{name}_r{r}")
        for c in range(cols):
            if k >= n:
                break
            x = (c - (cols - 1) / 2) * sp
            y = (r - (nrow - 1) / 2) * sp * .9
            C.mini_person(mb, x, y, 0, s, rnd.choice(FANS), rnd.choice(("skin1", "skin2", "skin3")))
            k += 1
        ob = mb.build((loc[0], loc[1] + 0, loc[2]))
        rows.append(ob)
    return rows
