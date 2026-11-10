"""Aset & dunia diorama untuk video "Bangun Hotel Rp40 Miliar".

Hotel budget-midscale 30 kamar (lobi kaca + 5 lantai x 6 kamar, balkon, sirip fasad, papan nama
HOTEL vertikal & di atap, kanopi drop-off, kolam renang di belakang), versi potongan (cutaway)
untuk "membedah" isi kamar, set interior kamar hotel, lobi resepsionis, restoran/meeting/gathering,
minimarket generik (tanpa merek), gedung kantor, kantor instansi, agen travel, uang & kalkulator.
Bagian depan bangunan menghadap -Y (sama seperti world.py).
"""
import math
import os
import random

import bpy

import lowpoly as lp
import world as W
import world_tahu as T          # noqa: F401  (palet orang/motor & helper beam)

beam = T.beam

lp.PAL.update({
    "hotel_wall": "#F3EFE6",
    "hotel_wall2": "#E4DDCF",
    "hotel_acc": "#2E5B78",
    "hotel_acc2": "#264C66",
    "hotel_gold": "#E3B341",
    "hotel_glass": "#5D7F98",
    "lobby_glass": "#7FA6BF",
    "win_lit": "#FFD98A",
    "rail": "#DCE3E8",
    "slab": "#CFC8BA",
    "carpet": "#8C5A4A",
    "carpet2": "#4E6A84",
    "floor_wood": "#C89B6D",
    "floor_tile": "#E9E4DA",
    "bed": "#FBFBF8",
    "bed_runner": "#2E5B78",
    "headboard": "#7A5A44",
    "pillow": "#FFFFFF",
    "lamp_shade": "#F6E7C8",
    "tv": "#22262B",
    "curtain": "#C9B79C",
    "curtain2": "#8E6F57",
    "sofa": "#3F6E8C",
    "sofa2": "#B35B45",
    "plant": "#4E9A50",
    "pot": "#E9E1D2",
    "desk": "#6E4C3A",
    "marble": "#EDEBE6",
    "suitcase": "#E06C4C",
    "suitcase2": "#3D8FD1",
    "brass": "#D8A93A",
    "cloth": "#FFFFFF",
    "food1": "#E8A33D",
    "food2": "#D9534F",
    "food3": "#6BB35A",
    "screen": "#F7F9FB",
    "chart1": "#3D8FD1",
    "chart2": "#4CC46C",
    "uniform": "#2E5B78",
    "pool": "#58C4E0",
    "pool_edge": "#F1EEE6",
    "lounger": "#FFFFFF",
    "palm": "#3E9A4F",
    "palm_trunk": "#9C7450",
    "mm_wall": "#F5F5F2",
    "mm_blue": "#1F5FB4",
    "mm_yellow": "#F6C431",
    "mm_red": "#D93A35",
    "mm_glass": "#BFDCEB",
    "office": "#9FB8C9",
    "office2": "#7F9CB0",
    "gov": "#F1ECE0",
    "gov_roof": "#B5523B",
    "flag_red": "#D93A35",
    "money_red": "#E0605A",
    "money_red2": "#C9463F",
    "money_band": "#F2E6C9",
    "calc": "#2F3640",
    "calc_key": "#E9ECEF",
    "calc_or": "#F39C34",
    "calc_lcd": "#BFE3C4",
    "sold": "#E2534A",
    "crane": "#F2B632",
    "truck": "#F4F4F2",
})

Z = W.Z_LAWN
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "PlusJakartaSans-800.ttf")

# ukuran hotel
HW, HD = 24.0, 11.0               # lebar & dalam bangunan
LOBBY_H = 4.6
FH = 3.2
FLOORS = 5
ROOMS = 6                         # kamar per lantai di sisi depan -> 30 kamar
ROOM_D = 6.6                      # kedalaman kamar dari fasad
TOP = LOBBY_H + FLOORS * FH       # tinggi atap (relatif dasar)


def glassy(key, alpha=.35):
    m = lp.mat(key)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Alpha"].default_value = alpha
    b.inputs["Roughness"].default_value = .1
    return m


def emit(ob, strength=2.0, keys=None):
    """ganti material objek jadi versi berpendar (mis. jendela kamar terisi)."""
    me = ob.data
    for i, m in enumerate(me.materials):
        k = m.name.split("_", 1)[1].rsplit("_", 1)[0]
        if keys is None or k in keys:
            me.materials[i] = lp.mat(k, emission=strength)
    return ob


def text(name, body, size, key, depth=.08, loc=(0, 0, 0), rot=(math.pi / 2, 0, 0), align="CENTER", emission=0.0):
    """tulisan 3D (dikonversi jadi mesh). Default: berdiri tegak menghadap -Y."""
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size
    cu.extrude = depth / 2
    cu.align_x = align
    cu.align_y = "BOTTOM"
    if os.path.exists(FONT):
        cu.font = bpy.data.fonts.load(FONT, check_existing=True)
    tmp = bpy.data.objects.new(name + "_tmp", cu)
    lp._link(tmp)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    me.materials.append(lp.mat(key, emission=emission))
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    return lp._link(ob)


def to_world(ob, loc, facing):
    """pasang objek berkoordinat lokal-bangunan ke posisi/arah dunia."""
    a = W.FACING[facing]
    x, y, z = ob.location
    ob.location = (loc[0] + x * math.cos(a) - y * math.sin(a), loc[1] + x * math.sin(a) + y * math.cos(a), loc[2] + z)
    ob.rotation_euler.z += a
    return ob


# ------------------------------------------------------------------ props kecil
def palm(mb, x, y, s=1.0, z=Z):
    h = 5.2 * s
    for k in range(6):
        mb.cyl(x + .06 * k * s, y, z + k * h / 6, z + (k + 1) * h / 6, (.28 - .02 * k) * s, "palm_trunk", n=7,
               r_top=(.26 - .02 * k) * s)
    tx, tz = x + .36 * s, z + h
    for k in range(7):
        a = 2 * math.pi * k / 7
        ex, ey = tx + math.cos(a) * 2.3 * s, y + math.sin(a) * 2.3 * s
        mb.poly([(tx, y, tz + .1), (tx + math.cos(a + .5) * .8 * s, y + math.sin(a + .5) * .8 * s, tz + .35 * s),
                 (ex, ey, tz - .7 * s), (tx + math.cos(a - .5) * .8 * s, y + math.sin(a - .5) * .8 * s, tz + .35 * s)],
                [(0, 1, 2, 3)], "palm")
    mb.sphere(tx, y, tz, .35 * s, "palm")


def plant(mb, x, y, z, s=1.0):
    mb.cyl(x, y, z, z + .55 * s, .3 * s, "pot", n=8, r_top=.36 * s)
    mb.sphere(x, y, z + .95 * s, .45 * s, "plant", sz=.55 * s)
    mb.sphere(x + .15 * s, y - .1 * s, z + 1.35 * s, .3 * s, "plant")


def suitcase(mb, x, y, z, s=1.0, key="suitcase"):
    mb.box(x - .26 * s, y - .14 * s, z + .05 * s, x + .26 * s, y + .14 * s, z + .75 * s, key)
    mb.box(x - .03 * s, y - .02 * s, z + .75 * s, x + .03 * s, y + .02 * s, z + 1.05 * s, "metal")
    mb.box(x - .14 * s, y - .02 * s, z + 1.02 * s, x + .14 * s, y + .02 * s, z + 1.07 * s, "metal")
    for sx in (-1, 1):
        mb.box(x + sx * .2 * s - .04, y - .04, z, x + sx * .2 * s + .04, y + .04, z + .06, "tire")


def staff(name, pose="stand"):
    """karyawan hotel berseragam biru dongker (asal di kaki, menghadap -Y)."""
    mb = W.person(name, "uniform", pants="tv", arms_forward=(pose == "give"))
    mb.box(-.31, -.2, 1.3, .31, -.18, 1.45, "hotel_gold")       # kerah emas
    return mb


def guest(name, shirt="red_aw", case="suitcase"):
    """tamu dengan koper di sisi kanan."""
    mb = W.person(name, shirt)
    suitcase(mb, .62, .05, 0, .9, case)
    return mb


def car_taxi(name):
    return lp.car(name, length=4.2, color="hotel_gold")


# ------------------------------------------------------------------ hotel
def hotel_core(mb, cut=False):
    """lantai, dinding samping & belakang, atap, lobi. (Dinding depan ada di hotel_front.)"""
    w, d = HW, HD
    z0 = Z
    # podium lobi (dinding samping/belakang)
    mb.box(-w / 2, -d / 2 + .3, z0, w / 2, d / 2, z0 + LOBBY_H, "hotel_wall2")
    # lantai kamar: badan bangunan
    if not cut:
        mb.box(-w / 2, -d / 2 + .2, z0 + LOBBY_H, w / 2, d / 2, z0 + TOP, "hotel_wall")
    else:
        # cutaway: pelat lantai, dinding belakang kamar (koridor), dinding samping
        for f in range(FLOORS + 1):
            zf = z0 + LOBBY_H + f * FH
            mb.box(-w / 2, -d / 2, zf - .25, w / 2, d / 2, zf, "slab")
            mb.box(-w / 2 - .05, -d / 2 - .05, zf - .25, w / 2 + .05, -d / 2 + .05, zf, "hotel_wall")
        mb.box(-w / 2, -d / 2 + ROOM_D, z0 + LOBBY_H, w / 2, d / 2, z0 + TOP, "hotel_wall")
        for sx in (-1, 1):
            mb.box(sx * w / 2 - (.3 if sx > 0 else 0), -d / 2, z0 + LOBBY_H, sx * w / 2 + (.3 if sx < 0 else 0), d / 2,
                   z0 + TOP, "hotel_wall")
    # jendela samping & belakang
    for f in range(FLOORS):
        zc = z0 + LOBBY_H + f * FH + FH * .55
        for sx in (-1, 1):
            for u in (-2.5, 0.5, 3.5):
                mb.box(sx * (w / 2 + .1) - .06, u - .7, zc - .75, sx * (w / 2 + .1) + .06, u + .7, zc + .75, "hotel_glass")
        for i in range(ROOMS):
            u = -w / 2 + (i + .5) * w / ROOMS
            mb.box(u - 1.0, d / 2 - .02, zc - .75, u + 1.0, d / 2 + .1, zc + .75, "hotel_glass")
    # atap: parapet + ruang mesin + tandon + AC
    zt = z0 + TOP
    mb.box(-w / 2 - .2, -d / 2 - .2, zt, w / 2 + .2, d / 2 + .2, zt + .3, "slab")
    for (a, b, c, e) in ((-w / 2 - .2, -d / 2 - .2, w / 2 + .2, -d / 2 + .1), (-w / 2 - .2, d / 2 - .1, w / 2 + .2, d / 2 + .2),
                         (-w / 2 - .2, -d / 2 - .2, -w / 2 + .1, d / 2 + .2), (w / 2 - .1, -d / 2 - .2, w / 2 + .2, d / 2 + .2)):
        mb.box(a, b, zt + .3, c, e, zt + 1.1, "hotel_wall")
    mb.box(4, -1, zt + .3, 9, 4, zt + 3.0, "hotel_wall2")
    mb.cyl(-7, 2.5, zt + .3, zt + 2.6, 1.2, "tank", n=12)
    for k in range(3):
        mb.boxc(-2 + k * 1.6, 3.6, zt + .3, 1.1, .9, .8, "machine")


def hotel_front(mb):
    """fasad depan: dinding, jendela kamar + balkon, sirip biru, lobi kaca, kanopi, papan nama."""
    w, d = HW, HD
    z0 = Z
    y = -d / 2
    # dinding depan lantai kamar
    mb.box(-w / 2, y, z0 + LOBBY_H, w / 2, y + .3, z0 + TOP, "hotel_wall")
    rw = w / ROOMS
    for f in range(FLOORS):
        zb = z0 + LOBBY_H + f * FH
        for i in range(ROOMS):
            u = -w / 2 + (i + .5) * rw
            mb.box(u - 1.35, y - .08, zb + .55, u + 1.35, y + .02, zb + 2.75, "frame")
            mb.box(u - 1.2, y - .12, zb + .65, u + 1.2, y - .06, zb + 2.65, "hotel_glass")
            mb.box(u - .03, y - .14, zb + .65, u + .03, y - .1, zb + 2.65, "frame")
            # balkon kecil + railing
            mb.box(u - 1.45, y - .95, zb + .05, u + 1.45, y, zb + .25, "hotel_wall2")
            mb.box(u - 1.45, y - .97, zb + .25, u + 1.45, y - .9, zb + 1.15, "rail")
            mb.box(u - 1.45, y - .99, zb + 1.1, u + 1.45, y - .88, zb + 1.2, "hotel_acc")
            mb.boxc(u + .95, y + .0 - .45, zb + .25, .7, .35, .5, "machine")     # outdoor AC
    # sirip vertikal biru di antara kamar
    for i in range(ROOMS + 1):
        u = -w / 2 + i * rw
        mb.box(u - .18, y - 1.15, z0 + LOBBY_H, u + .18, y, z0 + TOP + .6, "hotel_acc")
    # pita lantai
    mb.box(-w / 2 - .2, y - 1.2, z0 + LOBBY_H - .5, w / 2 + .2, y + .2, z0 + LOBBY_H, "hotel_acc2")
    # lobi kaca
    mb.box(-w / 2 + .3, y + .2, z0, w / 2 - .3, y + .35, z0 + LOBBY_H - .5, "lobby_glass")
    for k in range(13):
        u = -w / 2 + .3 + k * (w - .6) / 12
        mb.box(u - .08, y + .1, z0, u + .08, y + .3, z0 + LOBBY_H - .5, "tv")
    mb.box(-w / 2 + .3, y + .1, z0 + 2.9, w / 2 - .3, y + .3, z0 + 3.05, "tv")
    # pintu putar / masuk
    mb.box(-1.6, y - .05, z0, 1.6, y + .25, z0 + 2.8, "brass")
    mb.box(-1.4, y - .1, z0, 1.4, y + .2, z0 + 2.6, "lobby_glass")
    # kanopi drop-off dengan tiang
    cz = z0 + 3.9
    mb.box(-5, y - 6.0, cz, 5, y + .1, cz + .45, "hotel_acc")
    mb.box(-5.1, y - 6.1, cz + .45, 5.1, y + .1, cz + .6, "hotel_gold")
    for sx in (-4.4, 4.4):
        mb.box(sx - .2, y - 5.6, z0, sx + .2, y - 5.2, cz, "hotel_wall")
    # papan nama vertikal di sudut kiri
    bx = -w / 2 + .9
    mb.box(bx - .9, y - 1.6, z0 + LOBBY_H + 1.0, bx + .9, y - 1.2, z0 + TOP - .4, "hotel_acc2")
    # tangga lobi
    mb.box(-6, y - 1.2, z0, 6, y, z0 + .15, "marble")


def hotel_signs(prefix, loc, facing, lit=1.2):
    """tulisan HOTEL: vertikal di papan sudut + di atas atap + di kanopi."""
    y = -HD / 2
    obs = []
    bx = -HW / 2 + .9
    letters = "HOTEL"
    zt = Z + TOP - 1.4
    for i, ch in enumerate(letters):
        o = text(f"{prefix}_v{i}", ch, 1.9, "hotel_gold", depth=.25, loc=(bx, y - 1.68, zt - i * 2.95 - 1.5),
                 emission=lit)
        obs.append(o)
    # tulisan atap pada rangka
    fr = W.MB(prefix + "_roofsign")
    zr = Z + TOP + 1.1
    for sx in (-6.2, 6.2):
        fr.box(sx - .1, y + .4, zr - .8, sx + .1, y + .6, zr + 2.4, "metal")
    fr.box(-6.4, y + .4, zr + .1, 6.4, y + .6, zr + .25, "metal")
    obs.append(fr.build())
    obs.append(text(prefix + "_roof", "HOTEL", 2.6, "hotel_gold", depth=.3, loc=(0, y + .3, zr + .2), emission=lit))
    obs.append(text(prefix + "_canopy", "HOTEL", .42, "hotel_gold", depth=.06,
                    loc=(0, y - 6.13, Z + 3.97), emission=lit * .6))
    for o in obs:
        to_world(o, loc, facing)
    return obs


def hotel_rooms(mb, lit_all=False):
    """isi 30 kamar (untuk versi cutaway): sekat, karpet, kasur putih, headboard, nakas, lampu."""
    w, d = HW, HD
    rw = w / ROOMS
    y0 = -d / 2 + .3
    for f in range(FLOORS):
        zf = Z + LOBBY_H + f * FH
        for i in range(ROOMS):
            u0 = -w / 2 + i * rw
            cx = u0 + rw / 2
            mb.box(u0 + .12, y0, zf, u0 + rw - .12, y0 + ROOM_D - .3, zf + .03, "carpet" if (i + f) % 2 else "carpet2")
            mb.box(u0 - .06, y0, zf, u0 + .06, y0 + ROOM_D, zf + FH - .25, "hotel_wall")
            # kasur menghadap jendela, headboard di dinding belakang
            by = y0 + ROOM_D - .3
            mb.box(cx - .95, by - 2.1, zf, cx + .95, by, zf + .55, "bed")
            mb.box(cx - .97, by - 1.15, zf + .5, cx + .97, by - .75, zf + .58, "bed_runner")
            for sx in (-.45, .45):
                mb.box(cx + sx - .35, by - .5, zf + .55, cx + sx + .35, by - .12, zf + .72, "pillow")
            mb.box(cx - 1.15, by - .12, zf, cx + 1.15, by, zf + 1.35, "headboard")
            for sx in (-1.45, 1.45):
                mb.boxc(cx + sx, by - .3, zf, .45, .45, .5, "desk")
                mb.cyl(cx + sx, by - .3, zf + .5, zf + .78, .14, "lamp_shade", n=8, r_top=.1)
            mb.box(cx - .6, by + .0 - .02, zf + 1.6, cx + .6, by - .0, zf + 2.3, "curtain2")   # lukisan
    # lobi (lantai dasar) bila terlihat
    mb.box(-w / 2 + .3, -d / 2 + .4, Z, w / 2 - .3, d / 2 - .3, Z + .04, "marble")
    mb.box(-3.5, d / 2 - 2.2, Z, 3.5, d / 2 - 1.4, Z + 1.15, "desk")
    mb.box(-3.6, d / 2 - 2.3, Z + 1.15, 3.6, d / 2 - 1.3, Z + 1.25, "marble")
    for sx in (-8, 8):
        mb.box(sx - 1.6, -1.5, Z, sx + 1.6, -.6, Z + .7, "sofa")
        plant(mb, sx + 2.6, -1.0, Z, 1.0)


def hotel(name, cut=False, rooms=False, front=True):
    """hotel utuh (atau versi cutaway). Return (MB, tinggi atap)."""
    mb = W.MB(name)
    hotel_core(mb, cut=cut)
    if front:
        hotel_front(mb)
    if rooms:
        hotel_rooms(mb)
    return mb, Z + TOP + 3.5


def hotel_front_obj(name):
    mb = W.MB(name)
    hotel_front(mb)
    return mb


def room_windows(prefix, loc, facing):
    """30 panel jendela (objek terpisah) untuk dinyalakan satu per satu. Urutan: lantai bawah→atas."""
    obs = []
    y = -HD / 2
    rw = HW / ROOMS
    for f in range(FLOORS):
        zb = Z + LOBBY_H + f * FH
        for i in range(ROOMS):
            u = -HW / 2 + (i + .5) * rw
            mb = W.MB(f"{prefix}{f}{i}")
            mb.box(u - 1.2, y - .15, zb + .65, u + 1.2, y - .13, zb + 2.65, "win_lit")
            mb.box(u - 1.2, y - .17, zb + .65, u - .55, y - .15, zb + 2.65, "curtain")
            mb.box(u + .55, y - .17, zb + .65, u + 1.2, y - .15, zb + 2.65, "curtain")
            ob = mb.build()
            emit(ob, 2.2, keys={"win_lit"})
            obs.append(to_world(ob, loc, facing))
    return obs


def hotel_site(mb, cx, cy):
    """halaman hotel: jalur drop-off, parkir, kolam renang belakang, palem, tiang bendera."""
    y = cy - HD / 2
    mb.box(cx - 7, y - 10.5, Z, cx + 7, y - 1.2, Z + .04, "sidewalk")
    mb.box(cx - 3, y - 13.6, .25, cx + 3, y - 10.5, Z + .04, "sidewalk")
    # parkir di kiri-kanan
    for sx in (-1, 1):
        x0 = cx + sx * 8.5
        mb.box(x0 - 3.3, y - 10.5, Z, x0 + 3.3, y - 3.5, Z + .03, "asphalt")
        for k in range(4):
            xx = x0 - 3.3 + k * 2.2
            mb.box(xx - .05, y - 10.3, Z + .03, xx + .05, y - 6.0, Z + .05, "line")
    # tiang bendera
    for k, x in enumerate((-2.2, 0, 2.2)):
        mb.cyl(cx + x, y - 11.8, Z, Z + 6.5, .06, "metal", n=6)
        mb.box(cx + x + .06, y - 11.8 - .02, Z + 5.3, cx + x + 1.5, y - 11.8 + .02, Z + 6.3,
               ("flag_red", "hotel_acc", "hotel_gold")[k])
    for x in (-12.2, -6.3, 6.3, 12.2):
        palm(mb, cx + x, y - 12.0, .85)
    # kolam renang di belakang
    py = cy + HD / 2 + 4.6
    mb.box(cx - 8.5, py - 3.2, Z, cx + 8.5, py + 3.6, Z + .25, "pool_edge")
    mb.box(cx - 7.0, py - 2.2, Z + .1, cx + 7.0, py + 2.6, Z + .27, "pool")
    for k in range(5):
        x = cx - 6 + k * 3
        mb.box(x - .4, py + 3.0, Z + .25, x + .4, py + 3.5, Z + .45, "lounger")
        mb.box(x - .4, py + 3.35, Z + .45, x + .4, py + 3.5, Z + .8, "lounger")
    for x in (-10, 10):
        palm(mb, cx + x, py + 1.5, .8)


# ------------------------------------------------------------------ minimarket generik
def minimarket(name, w=12.0, d=9.0):
    """minimarket 1 lantai: muka kaca, papan nama biru dengan strip kuning-merah, rak warna-warni di dalam,
    ATM, parkir motor. Tanpa logo/merek. Return (MB, top)."""
    mb = W.MB(name)
    h = Z + 4.2
    mb.box(-w / 2, -d / 2, Z, w / 2, d / 2, h, "mm_wall")
    # muka kaca + rak di dalam
    mb.box(-w / 2 + .5, -d / 2 - .1, Z + .1, w / 2 - .5, -d / 2 + .02, Z + 2.9, "frame")
    for k in range(3):
        zb = Z + .35 + k * .8
        mb.box(-w / 2 + .9, -d / 2 + .35, zb, w / 2 - 3.2, -d / 2 + .75, zb + .08, "metal")
        x = -w / 2 + 1.0
        rnd = random.Random(k + 3)
        while x < w / 2 - 3.4:
            ww = rnd.uniform(.25, .45)
            mb.box(x, -d / 2 + .4, zb + .08, x + ww - .04, -d / 2 + .7, zb + rnd.uniform(.35, .6),
                   rnd.choice(["mm_red", "mm_yellow", "mm_blue", "food3", "food1", "tee"]))
            x += ww
    mb.box(-w / 2 + .7, -d / 2 - .16, Z + .2, w / 2 - .7, -d / 2 - .1, Z + 2.8, "mm_glass")
    mb.box(w / 2 - 3.0, -d / 2 - .22, Z + .2, w / 2 - 1.2, -d / 2 - .15, Z + 2.75, "frame")   # pintu
    mb.box(w / 2 - 2.9, -d / 2 - .25, Z + .3, w / 2 - 1.3, -d / 2 - .2, Z + 2.65, "mm_glass")
    # poster promo
    for x, k in ((-4.2, "mm_yellow"), (-2.6, "mm_red")):
        mb.box(x - .6, -d / 2 - .2, Z + 1.6, x + .6, -d / 2 - .17, Z + 2.5, k)
    # papan nama: biru + strip kuning & merah
    mb.box(-w / 2 - .2, -d / 2 - .55, Z + 3.0, w / 2 + .2, -d / 2 + .02, Z + 4.4, "mm_blue")
    mb.box(-w / 2 - .2, -d / 2 - .6, Z + 2.95, w / 2 + .2, -d / 2 - .5, Z + 3.15, "mm_yellow")
    mb.box(-w / 2 - .2, -d / 2 - .6, Z + 2.8, w / 2 + .2, -d / 2 - .5, Z + 2.95, "mm_red")
    # atap datar + parapet
    mb.box(-w / 2 - .2, -d / 2 - .2, h, w / 2 + .2, d / 2 + .2, h + .4, "mm_wall")
    mb.box(-2, 1, h + .4, 2, 3, h + 1.2, "machine")
    # ATM di samping
    mb.box(-w / 2 - 1.2, -d / 2 + .5, Z, -w / 2, -d / 2 + 1.7, Z + 2.4, "mm_blue")
    mb.box(-w / 2 - 1.25, -d / 2 + .7, Z + 1.0, -w / 2 - 1.2, -d / 2 + 1.5, Z + 1.8, "calc_lcd")
    # teras + parkir motor
    mb.box(-w / 2, -d / 2 - 2.0, Z, w / 2, -d / 2, Z + .12, "floor_tile")
    mb.box(-w / 2, -d / 2 - 6.5, Z, w / 2, -d / 2 - 2.0, Z + .05, "asphalt")
    for k in range(4):
        x = -w / 2 + 1.2 + k * 1.1
        mb.box(x - .15, -d / 2 - 5.4, Z + .05, x + .15, -d / 2 - 3.6, Z + .85, ("red_aw", "tv", "laundry_aw", "tv")[k])
        mb.box(x - .17, -d / 2 - 4.8, Z + .85, x + .17, -d / 2 - 4.0, Z + 1.0, "tv")
    return mb, h + 1.2


def minimarket_sign(prefix, loc, facing, w=12.0, d=9.0):
    o = text(prefix + "_txt", "MINIMARKET", .95, "tee", depth=.08, loc=(0, -d / 2 - .6, Z + 3.25), emission=.4)
    return to_world(o, loc, facing)


def box_truck(name):
    """truk boks distribusi (menghadap +X)."""
    root = bpy.data.objects.new(name, None)
    lp._link(root)
    mb = W.MB(name + "_m")
    mb.box(-2.6, -1.1, .55, 1.6, 1.1, 3.2, "truck")
    mb.box(-2.62, -1.12, 1.5, 1.62, 1.12, 2.0, "mm_blue")
    mb.box(1.7, -1.05, .55, 3.2, 1.05, 2.4, "mm_blue")
    mb.box(2.6, -1.0, 1.5, 3.25, 1.0, 2.25, "glass2")
    for x in (-1.8, .6, 2.5):
        for sy in (-1, 1):
            mb.disc_y(x, sy * 1.1 + (.15 if sy > 0 else 0), .5, .5, .3, "tire", n=10)
    ob = mb.build()
    ob.parent = root
    return root


# ------------------------------------------------------------------ gedung mitra
def office_tower(name, w=12.0, d=10.0, floors=9):
    mb = W.MB(name)
    h = Z + floors * 3.4
    mb.box(-w / 2, -d / 2, Z, w / 2, d / 2, h, "office")
    for f in range(floors):
        z = Z + f * 3.4
        for (a, b, c, e) in ((-w / 2 - .08, -d / 2 - .08, w / 2 + .08, d / 2 + .08),):
            mb.box(a, b, z + 2.8, c, e, z + 3.4, "office2")
    mb.box(-w / 2 - .3, -d / 2 - .3, h, w / 2 + .3, d / 2 + .3, h + .5, "office2")
    mb.box(-2, -1.5, h + .5, 2, 2, h + 2.5, "office2")
    mb.box(-1.5, -d / 2 - .15, Z, 1.5, -d / 2 + .02, Z + 2.6, "glass2")
    return mb, h + 2.5


def gov_office(name, w=16.0, d=10.0):
    """kantor instansi: bangunan putih berpilar, atap limasan merah, tiang bendera."""
    mb = W.MB(name)
    h = Z + 4.8
    mb.box(-w / 2, -d / 2, Z, w / 2, d / 2, h, "gov")
    W.windows(mb, w, d, Z + .2, 1, fh=4.4, skip_front_ground=True)
    mb.box(-4, -d / 2 - 2.5, Z, 4, -d / 2, Z + .3, "marble")
    for k in range(6):
        x = -3.5 + k * 1.4
        mb.cyl(x, -d / 2 - 2.0, Z + .3, h, .25, "gov", n=8)
    mb.prism_x([(-d / 2 - 2.6, h), (-d / 2 + 1, h + 1.8), (-d / 2 + 1, h)], -4.2, 4.2, "gov")
    mb.prism_x([(-d / 2 - .6, h - .2), (0, h + 3.2), (d / 2 + .6, h - .2)], -w / 2 - .6, w / 2 + .6, "gov_roof")
    mb.box(-1.0, -d / 2 - .12, Z, 1.0, -d / 2 + .02, Z + 2.8, "door")
    mb.cyl(0, -d / 2 - 6, Z, Z + 8, .07, "metal", n=6)
    mb.box(.07, -d / 2 - 6.02, Z + 6.6, 1.8, -d / 2 - 5.98, Z + 7.2, "flag_red")
    mb.box(.07, -d / 2 - 6.02, Z + 6.0, 1.8, -d / 2 - 5.98, Z + 6.6, "tee")
    return mb, h + 3.2


def travel_agent(name, w=10.0, d=9.0):
    m, top = W.shophouse(name, w, d, 2, random.Random(4), aw="laundry_aw", wall="wall_cream2")
    # papan pesawat sederhana
    m.box(-2.4, -d / 2 - .3, Z + 3.6, 2.4, -d / 2 - .1, Z + 5.4, "laundry_aw")
    m.poly([(-1.2, -d / 2 - .35, Z + 4.4), (1.3, -d / 2 - .35, Z + 4.6), (1.3, -d / 2 - .35, Z + 4.75),
            (-1.2, -d / 2 - .35, Z + 4.6)], [(0, 1, 2, 3)], "tee")
    m.poly([(-.2, -d / 2 - .36, Z + 4.55), (.5, -d / 2 - .36, Z + 4.55), (-.4, -d / 2 - .36, Z + 5.15)],
           [(0, 1, 2)], "tee")
    return m, top


# ------------------------------------------------------------------ uang & kalkulator
def money_bundle(mb, x, y, z, s=1.0, key="money_red"):
    """seikat uang merah (Rp100.000-an) dengan pita."""
    mb.box(x - .8 * s, y - .38 * s, z, x + .8 * s, y + .38 * s, z + .26 * s, key)
    mb.box(x - .82 * s, y - .4 * s, z + .24 * s, x + .82 * s, y + .4 * s, z + .27 * s, "money_red2")
    mb.box(x - .14 * s, y - .41 * s, z - .005, x + .14 * s, y + .41 * s, z + .275 * s, "money_band")


def money_pallet(name, nx=5, ny=4, nz=6, s=1.0):
    """tumpukan uang besar (blok)."""
    mb = W.MB(name)
    for k in range(nz):
        for i in range(nx):
            for j in range(ny):
                money_bundle(mb, (i - (nx - 1) / 2) * 1.68 * s, (j - (ny - 1) / 2) * .82 * s, k * .29 * s, s)
    return mb


def calculator(name, s=1.0):
    mb = W.MB(name)
    mb.box(-1.1 * s, -1.6 * s, 0, 1.1 * s, 1.6 * s, .3 * s, "calc")
    mb.box(-.9 * s, .65 * s, .3 * s, .9 * s, 1.35 * s, .34 * s, "calc_lcd")
    for i in range(4):
        for j in range(4):
            k = "calc_or" if i == 3 else "calc_key"
            mb.box((-.85 + i * .45) * s, (-1.4 + j * .5) * s, .3 * s, (-.5 + i * .45) * s, (-1.0 + j * .5) * s, .42 * s, k)
    return mb


def crane(mb, x, y, h=30.0):
    for sx in (-.6, .6):
        for sy in (-.6, .6):
            mb.box(x + sx - .12, y + sy - .12, Z, x + sx + .12, y + sy + .12, Z + h, "crane")
    for k in range(int(h // 3)):
        beam(mb, (x - .6, y - .6, Z + k * 3), (x + .6, y - .6, Z + k * 3 + 3), .1, "crane")
    mb.box(x - 6, y - .5, Z + h, x + 18, y + .5, Z + h + 1.0, "crane")
    mb.box(x - 6, y - .9, Z + h - 1.8, x - 3, y + .9, Z + h, "slab")
    mb.box(x - .8, y - .8, Z + h + 1.0, x + .8, y + .8, Z + h + 4, "crane")


# ------------------------------------------------------------------ set interior (studio)
def room_set(name, cx, cy):
    """kamar hotel lengkap (dollhouse 2 dinding): kasur + handuk, headboard, nakas & lampu, TV, meja,
    lemari, AC, jendela bergorden, lukisan, karpet, koper. Lantai di z=0, dinding di +Y & -X."""
    mb = W.MB(name)
    w, d, h = 6.4, 7.2, 3.3
    x0, y0, x1, y1 = cx - w / 2, cy - d / 2, cx + w / 2, cy + d / 2
    mb.box(x0 - .3, y0 - .3, -.5, x1 + .3, y1 + .3, 0, "hotel_wall2")
    mb.box(x0, y0, 0, x1, y1, .03, "floor_wood")
    mb.box(x0 + 1.0, y0 + 1.6, .03, x1 - 1.4, y1 - 1.0, .05, "carpet")
    mb.box(x0, y1, 0, x1, y1 + .25, h, "hotel_wall")                       # dinding belakang
    mb.box(x0 - .25, y0, 0, x0, y1 + .25, h, "hotel_wall2")                # dinding kiri
    # panel kayu di belakang kasur
    bx = cx + .4
    mb.box(bx - 1.9, y1 - .06, 0, bx + 1.9, y1, h - .3, "headboard")
    mb.box(bx - 1.4, y1 - .3, .35, bx + 1.4, y1 - .06, 1.5, "carpet2")      # headboard berlapis kain
    # kasur
    mb.box(bx - 1.25, y1 - 2.6, 0, bx + 1.25, y1 - .3, .35, "desk")
    mb.box(bx - 1.2, y1 - 2.55, .35, bx + 1.2, y1 - .3, .68, "bed")
    mb.box(bx - 1.22, y1 - 1.55, .62, bx + 1.22, y1 - 1.05, .72, "bed_runner")
    for sx in (-.6, .6):
        mb.box(bx + sx - .5, y1 - .75, .68, bx + sx + .5, y1 - .35, .92, "pillow")
    # handuk lipat (angsa) di atas kasur
    mb.sphere(bx - .35, y1 - 2.0, .78, .18, "tee", sz=.12)
    mb.sphere(bx + .35, y1 - 2.0, .78, .18, "tee", sz=.12)
    # nakas + lampu
    for sx in (-1.75, 1.75):
        mb.boxc(bx + sx, y1 - .45, 0, .6, .55, .55, "desk")
        mb.cyl(bx + sx, y1 - .45, .55, .9, .05, "brass", n=6)
        mb.cyl(bx + sx, y1 - .45, .9, 1.25, .26, "lamp_shade", n=10, r_top=.18)
    # lukisan
    mb.box(bx - .8, y1 - .08, 2.0, bx + .8, y1 - .06, 2.8, "brass")
    mb.box(bx - .7, y1 - .1, 2.08, bx + .7, y1 - .08, 2.72, "pool")
    mb.poly([(bx - .7, y1 - .11, 2.08), (bx + .2, y1 - .11, 2.08), (bx - .3, y1 - .11, 2.5)], [(0, 1, 2)], "palm")
    # AC split di dinding belakang kanan
    mb.box(x1 - 1.6, y1 - .3, 2.6, x1 - .2, y1, 3.0, "tee")
    # jendela + gorden di dinding kiri
    mb.box(x0 + .02, y0 + 1.0, .9, x0 + .06, y0 + 3.6, 2.7, "pool")
    mb.box(x0 + .02, y0 + .95, .85, x0 + .1, y0 + 3.65, .95, "frame")
    for (a, b) in ((y0 + .6, y0 + 1.25), (y0 + 3.35, y0 + 4.0)):
        mb.box(x0 + .06, a, .05, x0 + .3, b, 3.0, "curtain")
    mb.box(x0 + .06, y0 + .5, 3.0, x0 + .2, y0 + 4.1, 3.08, "metal")
    # meja kerja + kursi + TV di dinding kiri dekat depan
    mb.box(x0 + .05, y0 + 4.3, .75, x0 + .75, y1 - 3.2 + 1.9, .82, "desk")
    for yy in (y0 + 4.4, y1 - 1.4):
        mb.box(x0 + .1, yy, 0, x0 + .7, yy + .08, .75, "desk")
    mb.box(x0 + .9, y0 + 4.8, 0, x0 + 1.4, y0 + 5.3, .45, "sofa2")
    mb.box(x0 + 1.32, y0 + 4.8, .45, x0 + 1.4, y0 + 5.3, 1.0, "sofa2")
    mb.box(x0 + .02, y0 + 4.5, 1.3, x0 + .1, y0 + 5.9, 2.1, "tv")
    # lemari di sudut kanan belakang
    mb.box(x1 - 1.3, y1 - 2.6, 0, x1 - .1, y1 - 1.1, 2.4, "desk")
    mb.box(x1 - 1.32, y1 - 2.0, 1.1, x1 - 1.3, y1 - 1.9, 1.5, "brass")
    # rak koper + koper
    mb.box(x1 - 1.5, y0 + 1.0, 0, x1 - .4, y0 + 1.8, .45, "brass")
    suitcase(mb, x1 - .95, y0 + 1.4, .45, 1.0, "suitcase2")
    plant(mb, x1 - .7, y1 - .6, 0, .8)
    return mb.build()


def lobby_set(name, cx, cy):
    """lobi hotel: meja resepsionis marmer, rak kunci, sofa, tanaman, troli koper, lampu gantung."""
    mb = W.MB(name)
    w, d, h = 14.0, 10.0, 4.4
    x0, y0, x1, y1 = cx - w / 2, cy - d / 2, cx + w / 2, cy + d / 2
    mb.box(x0 - .3, y0 - .3, -.5, x1 + .3, y1 + .3, 0, "hotel_wall2")
    mb.box(x0, y0, 0, x1, y1, .03, "marble")
    for i in range(7):
        for j in range(5):
            if (i + j) % 2:
                mb.box(x0 + i * 2, y0 + j * 2, .03, x0 + i * 2 + 2, y0 + j * 2 + 2, .04, "floor_tile")
    mb.box(x0, y1, 0, x1, y1 + .3, h, "hotel_wall")
    mb.box(x0 - .3, y0, 0, x0, y1 + .3, h, "hotel_wall2")
    # dinding panel kayu di belakang meja
    mb.box(cx - 4.5, y1 - .08, 0, cx + 4.5, y1, h - .4, "headboard")
    # rak kunci / jam dunia
    for k in range(3):
        mb.cyl(cx - 1.6 + k * 1.6, y1 - .12, 3.0, 3.0 + .01, .35, "tee", n=12)
    for k in range(3):
        mb.disc_y(cx - 1.6 + k * 1.6, y1 - .1, 3.0, .38, .05, "tee", n=14)
        mb.disc_y(cx - 1.6 + k * 1.6, y1 - .15, 3.0, .3, .03, "lamp_shade", n=14)
    # meja resepsionis
    mb.box(cx - 3.5, y1 - 3.0, 0, cx + 3.5, y1 - 2.0, 1.15, "marble")
    mb.box(cx - 3.6, y1 - 3.1, 1.15, cx + 3.6, y1 - 1.9, 1.25, "headboard")
    mb.box(cx - 3.5, y1 - 3.05, .15, cx + 3.5, y1 - 2.98, .35, "hotel_gold")
    mb.cyl(cx + 2.3, y1 - 2.5, 1.25, 1.32, .16, "brass", n=10)          # bel
    mb.sphere(cx + 2.3, y1 - 2.5, 1.36, .12, "brass", sz=.08)
    mb.box(cx - 1.6, y1 - 2.6, 1.25, cx - .9, y1 - 2.2, 1.7, "tv")       # monitor
    plant(mb, cx - 4.4, y1 - 2.5, 0, 1.1)
    plant(mb, cx + 4.4, y1 - 2.5, 0, 1.1)
    # area duduk
    mb.box(x0 + .8, y0 + 2.0, 0, x0 + 4.6, y0 + 5.0, .04, "carpet2")
    mb.box(x0 + 1.0, y0 + 2.2, 0, x0 + 1.9, y0 + 4.8, .5, "sofa")
    mb.box(x0 + 1.0, y0 + 2.2, .5, x0 + 1.25, y0 + 4.8, 1.05, "sofa")
    mb.box(x0 + 3.4, y0 + 2.6, 0, x0 + 4.3, y0 + 3.5, .5, "sofa2")
    mb.box(x0 + 2.4, y0 + 3.0, 0, x0 + 3.1, y0 + 4.0, .42, "desk")
    plant(mb, x0 + .9, y1 - .9, 0, 1.2)
    # troli koper emas
    tx, ty = x1 - 2.5, y0 + 3.0
    mb.box(tx - .9, ty - .5, .2, tx + .9, ty + .5, .3, "carpet")
    for sx in (-.85, .85):
        mb.box(tx + sx - .04, ty - .04, .3, tx + sx + .04, ty + .04, 2.2, "brass")
    mb.box(tx - .9, ty - .04, 2.15, tx + .9, ty + .04, 2.25, "brass")
    suitcase(mb, tx - .4, ty, .3, 1.0, "suitcase")
    suitcase(mb, tx + .4, ty, .3, .8, "suitcase2")
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box(tx + sx * .8 - .08, ty + sy * .4 - .08, 0, tx + sx * .8 + .08, ty + sy * .4 + .08, .2, "tire")
    # lampu gantung
    for x in (cx - 2.5, cx + 2.5):
        mb.cyl(x, cy + 1.0, h - .9, h, .03, "brass", n=5)
        mb.cyl(x, cy + 1.0, h - 1.4, h - .9, .5, "lamp_shade", n=12, r_top=.25)
    ob = mb.build()
    sign = text(name + "_sign", "RECEPTION", .5, "hotel_gold", depth=.05, loc=(cx, y1 - .12, 3.75), emission=.6)
    return ob, sign


def facilities_set(name, cx, cy):
    """tiga ruang berjajar (kiri→kanan): RESTORAN, MEETING ROOM, BALLROOM/GATHERING."""
    mb = W.MB(name)
    rw, d, h = 9.0, 8.0, 3.4
    x0 = cx - 1.5 * rw
    y0, y1 = cy - d / 2, cy + d / 2
    mb.box(x0 - .3, y0 - .3, -.5, x0 + 3 * rw + .3, y1 + .3, 0, "hotel_wall2")
    mb.box(x0, y1, 0, x0 + 3 * rw, y1 + .3, h, "hotel_wall")
    mb.box(x0 - .3, y0, 0, x0, y1 + .3, h, "hotel_wall2")
    floors = ("floor_wood", "carpet2", "carpet")
    for r in range(3):
        a = x0 + r * rw
        mb.box(a, y0, 0, a + rw, y1, .03, floors[r])
        if r:
            mb.box(a - .1, y0 + 1.5, 0, a + .1, y1, h, "hotel_wall")
    # restoran: meja bertaplak + kursi, meja prasmanan
    a = x0
    for (tx, ty) in ((a + 2.2, y0 + 2.5), (a + 5.4, y0 + 2.5), (a + 2.2, y0 + 5.0), (a + 5.4, y0 + 5.0)):
        mb.cyl(tx, ty, 0, .75, .7, "cloth", n=12)
        for k in range(4):
            ang = k * math.pi / 2 + math.pi / 4
            mb.boxc(tx + math.cos(ang) * 1.0, ty + math.sin(ang) * 1.0, 0, .45, .45, .48, "sofa2")
        mb.cyl(tx, ty, .75, .95, .08, "plant", n=6)
    mb.box(a + .6, y1 - 1.2, 0, a + rw - .6, y1 - .4, .95, "marble")
    for k in range(5):
        mb.box(a + 1.0 + k * 1.45, y1 - 1.05, .95, a + 2.0 + k * 1.45, y1 - .55, 1.1, "metal")
        mb.box(a + 1.1 + k * 1.45, y1 - 1.0, 1.1, a + 1.9 + k * 1.45, y1 - .6, 1.15,
               ("food1", "food2", "food3", "food1", "food2")[k])
    # meeting room: meja panjang, kursi, layar presentasi dengan grafik
    a = x0 + rw
    mx = a + rw / 2
    mb.box(mx - 1.0, y0 + 1.8, .72, mx + 1.0, y1 - 1.8, .8, "desk")
    for sy in range(4):
        yy = y0 + 2.3 + sy * 1.0
        for sx in (-1, 1):
            mb.boxc(mx + sx * 1.45, yy, 0, .5, .5, .5, "tv")
            mb.boxc(mx + sx * 1.7, yy, .5, .08, .5, .6, "tv")
    mb.box(mx - 2.2, y1 - .1, 1.0, mx + 2.2, y1 - .02, 3.0, "screen")
    for k, hh in enumerate((.6, 1.0, .8, 1.4)):
        mb.box(mx - 1.5 + k * .8, y1 - .14, 1.3, mx - 1.0 + k * .8, y1 - .1, 1.3 + hh, "chart1" if k < 3 else "chart2")
    # gathering / ballroom: meja bundar banquet, panggung, spanduk
    a = x0 + 2 * rw
    for (tx, ty) in ((a + 2.3, y0 + 2.3), (a + 6.0, y0 + 2.3), (a + 4.2, y0 + 4.6)):
        mb.cyl(tx, ty, 0, .75, .95, "cloth", n=14)
        for k in range(6):
            ang = k * math.pi / 3
            mb.boxc(tx + math.cos(ang) * 1.3, ty + math.sin(ang) * 1.3, 0, .4, .4, .9, "hotel_gold")
    mb.box(a + 1.0, y1 - 2.0, 0, a + rw - 1.0, y1, .5, "headboard")
    mb.box(a + 1.8, y1 - .12, 1.4, a + rw - 1.8, y1 - .04, 2.8, "hotel_acc")
    mb.box(a + 2.0, y1 - .16, 1.6, a + rw - 2.0, y1 - .12, 2.6, "hotel_gold")
    return mb.build(), (x0 + rw / 2, x0 + 1.5 * rw, x0 + 2.5 * rw)


# ------------------------------------------------------------------ dunia
HOTEL_C = (0.0, -2.0)
MM_MAIN = (0.0, -36.0)            # minimarket di seberang jalan hotel (menghadap +y)
BRANCHES = [(-46, -40, "+y"), (46, -46, "-x"), (-44, 44, "-y"), (44, 46, "-y"), (-48, -8, "+x"),
            (12, 46, "-y"), (48, 8, "-x"), (-10, -56, "+y")]
OFFICE_C = (46.0, 30.0)
GOV_C = (-46.0, 14.0)
TRAVEL_C = (-14.0, 44.0)


def build_world(seed=5, people=True, branches=False, hotel_visible=True, cut=False):
    """kota diorama dengan hotel di blok tengah. Return info (anchors, obyek penting)."""
    rnd = random.Random(seed)
    info = {"anchors": {}, "branches": [], "people": []}
    W.PLACED.clear()
    W.build_ground()
    props = W.MB("props")
    trees = W.MB("trees")

    # --- hotel
    if hotel_visible:
        mb, top = hotel("hotel", cut=cut)
        info["hotel"] = mb.build((*HOTEL_C, 0), 0)
        info["signs"] = hotel_signs("hs", (*HOTEL_C, 0), "-y")
    info["anchors"]["HOTEL"] = (HOTEL_C[0], HOTEL_C[1] - HD / 2, Z + TOP + 4.5)
    info["anchors"]["HOTEL_MID"] = (HOTEL_C[0], HOTEL_C[1] - HD / 2 - 1, Z + LOBBY_H + 8)
    info["anchors"]["LOBI"] = (HOTEL_C[0], HOTEL_C[1] - HD / 2 - 6, Z + 4.8)
    hotel_site(props, *HOTEL_C)

    # --- minimarket utama di seberang jalan
    mm, mtop = minimarket("mm_main")
    info["mm_main"] = mm.build((*MM_MAIN, 0), W.FACING["+y"])
    info["mm_sign"] = minimarket_sign("mm_main", (*MM_MAIN, 0), "+y")
    info["anchors"]["MINIMARKET"] = (MM_MAIN[0], MM_MAIN[1], mtop + 1.5)
    reserved = [(-15.5, -15.5, 15.5, 15.5), (MM_MAIN[0] - 9, MM_MAIN[1] - 9, MM_MAIN[0] + 9, MM_MAIN[1] + 12)]

    # --- gedung mitra
    for (nm, fn, c, fc) in (("office", office_tower, OFFICE_C, "-x"), ("gov", gov_office, GOV_C, "+x"),
                            ("travel", travel_agent, TRAVEL_C, "-y")):
        ob, top = W.place(fn(nm), c[0], c[1], fc)
        info["anchors"][nm.upper()] = (c[0], c[1], top + 1)
        reserved.append((c[0] - 9, c[1] - 9, c[0] + 9, c[1] + 9))

    # --- cabang minimarket (opsional)
    for k, (x, y, fc) in enumerate(BRANCHES):
        reserved.append((x - 8, y - 8, x + 8, y + 8))
        if branches:
            mm, mtop = minimarket(f"mm{k}")
            ob = mm.build((x, y, 0), W.FACING[fc])
            sg = minimarket_sign(f"mm{k}", (x, y, 0), fc)
            info["branches"].append((ob, sg, (x, y, mtop)))

    # --- taman barat-daya
    pb = W.inner((-W.L, -W.L, W.ROADS[0] - W.RW / 2, W.ROADS[0] - W.RW / 2))
    reserved.append(pb)
    px, py = (pb[0] + pb[2]) / 2, (pb[1] + pb[3]) / 2
    props.box(pb[0] + 2, py - 1.2, Z, pb[2] - 2, py + 1.2, Z + .03, "path")
    props.box(px - 1.2, pb[1] + 2, Z, px + 1.2, pb[3] - 2, Z + .03, "path")
    for q in range(22):
        x = rnd.uniform(pb[0] + 3, pb[2] - 3)
        y = rnd.uniform(pb[1] + 3, pb[3] - 3)
        if abs(x - px) < 3 or abs(y - py) < 3 or any(abs(x - bx) < 9 and abs(y - by) < 9 for bx, by, _ in BRANCHES):
            continue
        if rnd.random() < .45:
            W.tree_conifer(trees, x, y, rnd.uniform(.8, 1.15))
        else:
            W.tree_round(trees, x, y, rnd.uniform(.8, 1.2), rnd)

    # --- kavling lain: rumah, ruko, townhouse
    for b in W.blocks():
        ib = W.inner(b)
        lot = 11.0
        nx, ny = max(1, int((ib[2] - ib[0]) // lot)), max(1, int((ib[3] - ib[1]) // lot))
        lx, ly = (ib[2] - ib[0]) / nx, (ib[3] - ib[1]) / ny
        for a in range(nx):
            for c in range(ny):
                cx, cy = ib[0] + (a + .5) * lx, ib[1] + (c + .5) * ly
                rect = (cx - lx / 2 + .5, cy - ly / 2 + .5, cx + lx / 2 - .5, cy + ly / 2 - .5)
                if any(lp._overlap(rect, r) for r in reserved):
                    continue
                cands = [(abs(cx - r), "+x" if cx < r else "-x") for r in W.ROADS] + \
                        [(abs(cy - r), "+y" if cy < r else "-y") for r in W.ROADS]
                facing = min(cands)[1]
                w = rnd.uniform(7.5, min(lx, ly) - 2.4)
                d = rnd.uniform(7.0, min(lx, ly) - 2.6)
                k = rnd.random()
                nm = f"{a}{c}_{cx:.0f}_{cy:.0f}"
                if k < .1:
                    W.tree_round(trees, cx - 2, cy, 1.1, rnd)
                    W.tree_conifer(trees, cx + 2.5, cy + 1.5, 1.0)
                    continue
                if k < .5:
                    W.place(T.house("hs" + nm, w, d, rnd), cx, cy, facing)
                elif k < .75:
                    W.place(W.townhouse("th" + nm, w, d, rnd.choice([2, 2, 3]), rnd), cx, cy, facing)
                else:
                    W.place(W.shophouse("sh" + nm, w, d, 2, rnd), cx, cy, facing)
                for (tx_, ty_) in ((rect[0] + 1.1, rect[1] + 1.1), (rect[2] - 1.1, rect[3] - 1.1)):
                    if rnd.random() < .5:
                        W.tree_round(trees, tx_, ty_, .65, rnd)

    for r in W.ROADS:
        for t in range(-66, 67, 18):
            if all(abs(t - q) > 9 for q in W.ROADS):
                for off in (-W.RW / 2 - 1.2, W.RW / 2 + 1.2):
                    W.lamp(props, t, r + off)
                    W.lamp(props, r + off, t)
    props.build()
    trees.build()

    # mobil parkir & taksi di drop-off hotel
    hy = HOTEL_C[1] - HD / 2
    for k, (x, col) in enumerate(((-9.6, "car_white"), (-7.4, "car_red"), (7.4, "car_blue"), (9.6, "car_white"))):
        c = lp.car(f"park{k}", length=4.0, color=col)
        c.location = (HOTEL_C[0] + x, hy - 8.2, Z)
        c.rotation_euler.z = math.pi / 2
    tx = car_taxi("taxi")
    tx.location = (HOTEL_C[0] + .5, hy - 3.5, Z)
    info["taxi"] = tx

    if people:
        prnd = random.Random(seed + 1)
        for k in range(16):
            r = prnd.choice(W.ROADS)
            off = prnd.choice((-W.RW / 2 - 1.7, W.RW / 2 + 1.7))
            horiz = prnd.random() < .5
            t0 = prnd.uniform(-60, 60)
            if any(abs(t0 - q) < 8 for q in W.ROADS):
                t0 += 25
            ob = W.person(f"ped{k}", prnd.choice(W.SHIRTS)).build()
            ob.scale = (1.25,) * 3
            sp = prnd.choice((-1, 1)) * prnd.uniform(1.0, 1.5)
            if horiz:
                ob.location = (t0, r + off, .25)
                ob.rotation_euler.z = -math.pi / 2 if sp > 0 else math.pi / 2
            else:
                ob.location = (r + off, t0, .25)
                ob.rotation_euler.z = 0 if sp > 0 else math.pi
            info["people"].append((ob, horiz, sp))
        # doorman & tamu di depan lobi
        d = staff("doorman").build()
        d.location = (HOTEL_C[0] - 2.4, hy - 1.6, Z)
        d.scale = (1.25,) * 3
        g = guest("guest", "red_aw").build()
        g.location = (HOTEL_C[0] + 2.6, hy - 2.4, Z)
        g.scale = (1.25,) * 3
    return info
