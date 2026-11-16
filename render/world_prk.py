"""Aset & dunia diorama untuk video "Bedah Bisnis: Juru Parkir Minimarket".

Isi: jalan kota + trotoar + tiang listrik & kabel, minimarket generik 1 lantai (muka kaca, rak warna-warni,
papan nama hijau-oranye "MINIMARKET", teras beratap), lahan parkir paving dengan garis, deretan motor matic
(beberapa warna) & mobil, juru parkir (rompi oranye bergaris reflektif, topi, peluit di dada), kasir minimarket,
pembeli, ruko tetangga, pohon, lampu jalan (menyala malam), kota di kejauhan, uang kertas Rp2.000 / Rp5.000,
ikat uang merah, kantong pinggang, "orang di balik layar" (siluet di depan layar berpendar), ikon cuaca
(matahari, awan hujan + hujan), kartu jaminan sosial, peta mini kota dengan titik parkir.
Semua generik (tanpa logo/merek asli). Kamera umumnya dari -Y.
"""
import math
import random

import bpy

import lowpoly as lp
import world as W
import world_hotel as H         # text(), money_bundle(), calculator()
import world_laundry as L       # character(), pose(), rbox/ball/tube
import world_tahu as T          # beam(), pin()
import world_ctd as C           # person(), street_tree(), skyline(), coin() ...

lp.PAL.update({
    # jalan & lahan
    "pk_asph": "#50545B", "pk_asph2": "#5A5F67", "pk_line": "#EEEEEA", "pk_liney": "#F2C230",
    "pk_walk": "#CFC8BC", "pk_walk2": "#BDB5A8", "pk_curb": "#9EA3A8", "pk_pave": "#C2BCB1", "pk_pave2": "#B5AEA2",
    "pk_grass": "#7DB653", "pk_far": "#A9C7A0", "pk_ground": "#C9D3C4",
    # minimarket (generik: hijau + oranye)
    "mm_wall2": "#F4F2ED", "mm_green": "#1E9C6B", "mm_green2": "#167A53", "mm_orange": "#F28C28",
    "mm_glass": "#9CC8DA", "mm_frame": "#3A3F46", "mm_roof": "#D9DDE1", "mm_floor": "#E6E2DA",
    "shelf1": "#E2453C", "shelf2": "#F2C230", "shelf3": "#3D8BFF", "shelf4": "#3FAE6A", "shelf5": "#F2559C",
    "shelf6": "#FF9A2E", "mm_uni": "#1E9C6B",
    # juru parkir
    "vest": "#FF7A1A", "vest2": "#E25F0A", "vest_ref": "#E8EEF2", "whistle": "#F4F4F4", "whistle2": "#C9CED5",
    "cap_n": "#1F2A44", "pouch": "#3A3128",
    # kendaraan
    "bk_red": "#D9473F", "bk_blue": "#2F6FD6", "bk_blk": "#24272D", "bk_wht": "#EDEFF2", "bk_grey": "#8A929C",
    "bk_seat": "#1B1D21", "bk_sil": "#B9BFC6", "tire2": "#1E2024",
    "cr_white": "#F1F2F4", "cr_silver": "#B9C0C8", "cr_red": "#C8433C", "cr_black": "#2B2E34", "cr_blue": "#3E6FB0",
    "cr_glass": "#3E5466", "cr_light": "#FFE7A8", "cr_tail": "#E8423F",
    # ruko & kota
    "rk1": "#E8D9C0", "rk2": "#D7E3E8", "rk3": "#EAD2CF", "rk4": "#DDE6D3", "rk_shut": "#9AA3AC", "rk_shut2": "#868F98",
    "rk_awn1": "#3D8BFF", "rk_awn2": "#E2453C", "rk_awn3": "#F2C230", "rk_win": "#7FA9CB",
    "pole_c": "#9A9FA6", "wire": "#2B2E33", "lamp_w": "#FFE9B8",
    # uang
    "n2k": "#9FB0C0", "n2k2": "#7F91A3", "n5k": "#C29A62", "n5k2": "#9E7A48", "money_red": "#E25A55",
    "money_red2": "#B8423E", "money_band": "#F4EFE6", "money_dk": "#8E2F2B", "money_dk2": "#6E2420",
    # layar & cuaca
    "scr_glow": "#FFB45C", "scr_frame": "#2A2D33", "shadow_p": "#0E0F12", "sun_y": "#FFC233", "cloud": "#AEB7C2",
    "cloud2": "#8E99A6", "rain": "#BFE3FF", "card_g": "#2FA36B", "card_w": "#F7F8FA", "pin_g": "#1E9C6B",
    "pin_r": "#E2453C", "pin_y": "#F2C230",
})

SKIN = ("skin1", "skin2", "skin3")
SHIRTS = ("c_coral", "c_mint", "c_sky", "c_mustard", "c_lilac", "c_white", "c_navy", "c_pink", "c_olive", "c_brick")

# tata letak (satuan dunia; tokoh ±2,3 tinggi)
ROAD_Y0, ROAD_Y1 = -34.0, -20.0          # jalan raya (sumbu x)
WALK_Y1 = -17.0                           # trotoar sampai y ini
LOT = (-19.0, -17.0, 19.0, 4.0)           # lahan parkir (x0, y0, x1, y1)
STORE = (-13.0, 4.0, 13.0, 20.0)          # minimarket (muka kaca di y = 4)
STORE_H = 6.2
JUKIR_POS = (3.0, -5.2)


# ------------------------------------------------------------------ bantu
def emit_mat(key_, strength):
    return lp.mat(key_, strength)


_GLASS = []


def glass_mat():
    """kaca etalase: sebagian besar tembus (isi toko terlihat) + sedikit warna & kilap."""
    if _GLASS and _GLASS[0].name in bpy.data.materials:
        return _GLASS[0]
    m = bpy.data.materials.new("prk_glass")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = lp.hex_rgba(lp.PAL["mm_glass"])
    bsdf.inputs["Roughness"].default_value = .15
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs["Fac"].default_value = .28
    out = nt.nodes["Material Output"]
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(bsdf.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    _GLASS[:] = [m]
    return m


def linked_copy(src, name, loc, rot_z=0.0, s=1.0):
    ob = src.copy()
    ob.name = name
    lp._link(ob)
    ob.location = loc
    ob.rotation_euler = (0, 0, rot_z)
    ob.scale = (s, s, s)
    ob.hide_render = False
    return ob


# ------------------------------------------------------------------ kendaraan
_TPL = {}


def motor_tpl(color):
    """motor matic generik (menghadap +X, panjang ±2,5)."""
    k = ("motor", color)
    if k in _TPL:
        return _TPL[k]
    mb = W.MB(f"tpl_motor_{color}")
    for x in (-.85, .85):
        mb.disc_y(x, .09, .36, .36, .18, "tire2", n=12)
        mb.disc_y(x, .095, .36, .17, .19, "bk_sil", n=10)
    L.rbox(mb, -1.2, -.24, .45, -.05, .24, .95, color, c=.1)          # bodi belakang
    L.rbox(mb, -1.15, -.25, .92, -.15, .25, 1.06, "bk_seat", c=.1)      # jok
    mb.box(-.1, -.16, .3, .45, .16, .52, "bk_blk")                     # dek kaki
    L.rbox(mb, .4, -.22, .35, .75, .22, 1.2, color, c=.08)             # tameng depan
    mb.box(.6, -.15, 1.15, .85, .15, 1.38, color)                      # kepala
    mb.box(.72, -.48, 1.33, .8, .48, 1.39, "bk_blk")                   # setang
    mb.box(.84, -.1, 1.18, .88, .1, 1.3, "cr_light")                   # lampu
    mb.box(-1.24, -.12, .78, -1.2, .12, .88, "cr_tail")
    mb.box(-1.0, .2, .25, -.3, .27, .42, "bk_sil")                     # knalpot
    ob = mb.build()
    ob.hide_render = True
    ob.location = (0, 0, -500)
    _TPL[k] = ob
    return ob


def motor(name, loc, rot_z=0.0, color="bk_red", s=1.0):
    return linked_copy(motor_tpl(color), name, loc, rot_z, s)


def car_tpl(color):
    """mobil keluarga (MPV) generik, menghadap +X, panjang ±5,6."""
    k = ("car", color)
    if k in _TPL:
        return _TPL[k]
    mb = W.MB(f"tpl_car_{color}")
    L.rbox(mb, -2.8, -1.2, .45, 2.8, 1.2, 1.55, color, c=.25)
    L.rbox(mb, -2.45, -1.08, 1.5, 1.2, 1.08, 2.45, color, c=.22)
    for sy in (-1, 1):
        mb.box(-2.3, sy * 1.085 - .01, 1.62, 1.05, sy * 1.085 + .01, 2.32, "cr_glass")
    mb.box(1.15, -.95, 1.6, 1.62, .95, 2.32, "cr_glass")                 # kaca depan (miring disederhanakan)
    mb.box(-2.5, -.95, 1.62, -2.44, .95, 2.3, "cr_glass")
    for x in (-1.8, 1.8):
        for sy in (-1, 1):
            mb.disc_y(x, sy * 1.12 + (.16 if sy > 0 else 0), .5, .5, .32, "tire2", n=12)
            mb.disc_y(x, sy * 1.12 + (.17 if sy > 0 else -.01), .5, .24, .34, "bk_sil", n=10)
    for sy in (-1, 1):
        mb.box(2.78, sy * .8 - .2, 1.0, 2.83, sy * .8 + .2, 1.2, "cr_light")
        mb.box(-2.83, sy * .85 - .18, 1.05, -2.78, sy * .85 + .18, 1.3, "cr_tail")
    mb.box(2.79, -.6, .55, 2.84, .6, .8, "bk_blk")
    ob = mb.build()
    ob.hide_render = True
    ob.location = (0, 0, -500)
    _TPL[k] = ob
    return ob


def car(name, loc, rot_z=0.0, color="cr_white", s=1.0):
    return linked_copy(car_tpl(color), name, loc, rot_z, s)


def rider_motor(name, loc, rot_z=0.0, color="bk_red", shirt="c_coral", helmet="c_white", s=.78):
    """motor + pengendara (duduk, helm) sebagai anak objek motor."""
    mo = motor(name, loc, rot_z, color, s)
    mb = W.MB(name + "_r")
    mb.box(-.78, -.2, 1.05, -.38, .2, 1.75, shirt)                      # badan
    mb.sphere(-.55, 0, 2.0, .2, "skin2")
    mb.sphere(-.56, 0, 2.06, .24, helmet, sz=.2)
    for sy in (-1, 1):
        T.beam(mb, (-.5, sy * .24, 1.65), (.72, sy * .4, 1.38), .1, shirt)
        mb.box(-.75, sy * .2 - .09, 1.0, -.05, sy * .2 + .09, 1.16, "c_denim")
        T.beam(mb, (-.08, sy * .2, 1.08), (.12, sy * .2, .55), .13, "c_denim")
        mb.box(.02, sy * .2 - .08, .5, .3, sy * .2 + .08, .58, "shoe_dk")
    r = mb.build()
    r.parent = mo
    return mo


def hq(name, loc, s=1.0):
    """markas 'orang di balik layar' untuk peta: gedung gelap + layar berpendar + siluet besar di depannya."""
    mb = W.MB(name)
    mb.box(-5 * s, -4 * s, 0, 5 * s, 4 * s, 16 * s, "scr_frame")
    mb.box(-5.4 * s, -4.4 * s, 16 * s, 5.4 * s, 4.4 * s, 16.6 * s, "shadow_p")
    bld = mb.build(loc)
    fr, sc = glow_screen(name + "_scr", (loc[0], loc[1] - 4.3 * s, loc[2] + 16.6 * s), 9 * s, 6 * s, 4.0)
    fr.rotation_euler.z = 0
    sil = pengelola(name + "_p", (loc[0], loc[1] - 4.9 * s, loc[2] + 16.6 * s), 0)
    sil["body"].scale = (2.4 * s,) * 3
    return dict(bld=bld, frame=fr, screen=sc, sil=sil)


BIKE_COLS = ("bk_red", "bk_blue", "bk_blk", "bk_wht", "bk_grey", "bk_blk", "bk_red")
CAR_COLS = ("cr_white", "cr_silver", "cr_black", "cr_red", "cr_blue", "cr_white")


# ------------------------------------------------------------------ orang
def jukir(name, loc=(0, 0, 0), rot=0.0, s=C.CH_S, hold=None):
    """juru parkir: kaus navy, celana krem, topi, ROMPI oranye bergaris reflektif, peluit di dada, tas pinggang."""
    lk = dict(skin="skin2", top="c_navy", sleeve="c_navy", bottom="c_khaki", shoe="shoe_dk", hair="cap",
              hair_col="cap_n", acc=())
    parts = L.character(name, lk, loc, rot, s, hold)
    mb = W.MB(name + "_vest")
    L.tube(mb, 0, 0, .9, 1.45, .222, .162, .29, .182, "vest", n=14)
    L.ball(mb, 0, 0, 1.43, .29, "vest", sz=.07, sy=.18, seg=14, rings=4)
    for z in (1.04, 1.22):
        L.tube(mb, 0, 0, z, z + .055, .232 + (z - .9) * .12, .168 + (z - .9) * .04, .236 + (z - .9) * .12,
               .17 + (z - .9) * .04, "vest_ref", n=14)
    mb.box(-.02, -.19, .92, .02, -.17, 1.42, "vest2")                    # belahan depan
    # tali peluit + peluit
    T.beam(mb, (-.1, -.17, 1.44), (.06, -.2, 1.22), .018, "c_white")
    T.beam(mb, (.13, -.17, 1.44), (.06, -.2, 1.22), .018, "c_white")
    mb.cyl(.06, -.24, 1.12, 1.26, .045, "whistle", n=10)
    mb.box(.04, -.3, 1.2, .08, -.24, 1.24, "whistle2")
    # tas pinggang
    L.rbox(mb, -.22, -.2, .8, .06, -.08, .95, "pouch", c=.03)
    vest = mb.build()
    vest.parent = parts["body"]
    parts["vest"] = vest
    return parts


def kasir(name, loc=(0, 0, 0), rot=0.0, s=C.CH_S):
    lk = dict(skin="skin1", top="mm_uni", sleeve="mm_uni", bottom="c_black", shoe="shoe_dk", hair="hijab",
              hair_col="hij_navy", acc=("lanyard",))
    return L.character(name, lk, loc, rot, s)


def shopper(name, k, loc=(0, 0, 0), rot=0.0, hold=None):
    rr = random.Random(k * 7 + 3)
    shirt = SHIRTS[k % len(SHIRTS)]
    hair = rr.choice(("short", "long", "hijab", "cap", "short"))
    lk = dict(skin=SKIN[k % 3], top=shirt, sleeve=shirt, bottom=rr.choice(("c_denim", "c_black", "c_khaki")),
              shoe=rr.choice(("shoe_w", "shoe_dk")), hair=hair,
              hair_col={"hijab": rr.choice(("hij_cream", "hij_navy")), "cap": "c_black"}.get(hair, "hair_blk"),
              acc=())
    return L.character(name, lk, loc, rot, C.CH_S, hold)


def pengelola(name, loc=(0, 0, 0), rot=0.0):
    """'orang di balik layar': setelan gelap + kacamata hitam, dipakai sebagai siluet."""
    lk = dict(skin="shadow_p", top="shadow_p", sleeve="shadow_p", bottom="shadow_p", shoe="shadow_p", hair="short",
              hair_col="shadow_p", acc=())
    return L.character(name, lk, loc, rot, C.CH_S)


# ------------------------------------------------------------------ bangunan
def minimarket(name="mm", loc=(0, 0, 0), sign=True, glow=0.0):
    """minimarket generik. Asal = tengah muka kaca di tanah. Return dict(body, sign, glass_mat, light)."""
    x0, x1, d, h = -13.0, 13.0, 16.0, STORE_H
    mb = W.MB(name)
    mb.box(x0, d - .3, 0, x1, d, h, "mm_wall2")                       # dinding belakang
    mb.box(x0, 0, 0, x0 + .3, d, h, "mm_wall2")
    mb.box(x1 - .3, 0, 0, x1, d, h, "mm_wall2")
    mb.box(x0, 0, h - .3, x1, d, h, "mm_wall2")                       # atap
    mb.box(x0, 0, 4.1, x1, .3, h, "mm_wall2")                         # dinding atas muka
    mb.box(x0, 0, 0, x0 + .6, .3, 4.1, "mm_wall2")
    mb.box(x1 - .6, 0, 0, x1, .3, 4.1, "mm_wall2")
    mb.box(x0 - .2, -3.4, 0, x1 + .2, d, .22, "mm_floor")              # lantai teras + dalam
    # muka kaca + kusen
    for k in range(9):
        x = x0 + .6 + k * (x1 - x0 - 1.2) / 8
        mb.box(x - .07, -.12, .22, x + .07, .02, 4.1, "mm_frame")
    mb.box(x0 + .6, -.12, 3.95, x1 - .6, .02, 4.1, "mm_frame")
    # rak warna-warni di balik kaca
    rnd = random.Random(5)
    for row in range(3):
        y = 1.6 + row * 3.4
        for lv in range(4):
            z = .5 + lv * .78
            mb.box(x0 + 1.2, y, z, x1 - 4.2, y + .9, z + .06, "pole_c")
            x = x0 + 1.3
            while x < x1 - 4.4:
                w = rnd.uniform(.25, .55)
                mb.box(x, y + .1, z + .06, x + w - .04, y + .8, z + .06 + rnd.uniform(.3, .6),
                       rnd.choice(("shelf1", "shelf2", "shelf3", "shelf4", "shelf5", "shelf6", "c_white")))
                x += w
    # meja kasir di sisi kanan dalam
    mb.box(x1 - 3.6, 1.2, .22, x1 - 1.0, 2.6, 1.3, "mm_green")
    mb.box(x1 - 3.7, 1.1, 1.3, x1 - .9, 2.7, 1.38, "c_white")
    # teras: atap kanopi + tiang
    mb.box(x0 - .4, -3.6, 4.55, x1 + .4, 0, 4.85, "mm_roof")
    mb.box(x0 - .4, -3.75, 4.3, x1 + .4, -3.55, 4.9, "mm_green")
    for x in (x0 + .2, x1 - .2):
        mb.box(x - .15, -3.5, .22, x + .15, -3.2, 4.55, "mm_frame")
    # papan nama: pita hijau + strip oranye
    mb.box(x0 - .1, -.25, 4.9, x1 + .1, .05, h, "mm_green")
    mb.box(x0 - .1, -.27, 4.85, x1 + .1, .03, 5.05, "mm_orange")
    mb.box(x0 - .3, -.3, h, x1 + .3, d + .3, h + .35, "mm_green2")
    # unit AC & tangki di atap
    for x in (-7, -3):
        mb.box(x, d - 4, h + .35, x + 2.2, d - 2.4, h + 1.6, "mm_roof")
    mb.cyl(8, d - 4, h + .35, h + 2.6, .9, "bk_sil", n=12)
    # tempat sampah & bangku teras
    mb.box(x0 + 1.0, -2.6, .22, x0 + 1.8, -1.9, 1.3, "mm_orange")
    mb.box(x1 - 4.5, -2.8, .22, x1 - 1.5, -2.2, .9, "tn_wood" if "tn_wood" in lp.PAL else "mm_frame")
    body = mb.build(loc)
    # kaca bening tipis + panel lampu plafon (berpendar; lebih terang saat malam)
    g = W.MB(name + "_gl")
    g.box(x0 + .6, -.03, .22, x1 - .6, .03, 3.95, "mm_glass")
    glass = g.build(loc)
    glass.data.materials[0] = glass_mat()
    c = W.MB(name + "_ceil")
    for k in range(4):
        y = 2.0 + k * 3.6
        c.box(x0 + 1.5, y, h - .36, x1 - 1.5, y + .8, h - .3, "lamp_w")
    ceil = c.build(loc)
    cm = lp.mat("lamp_w", 0.0).copy()
    cm.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = lp.hex_rgba("#FFF6E2")
    cm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 3.0
    ceil.data.materials[0] = cm
    out = dict(body=body, glass=glass, ceil=ceil, ceil_mat=cm)
    if sign:
        t = H.text(name + "_txt", "MINIMARKET", 1.0, "c_white", depth=.06,
                   loc=(loc[0], loc[1] - .3, loc[2] + 5.18), emission=.6)
        out["sign"] = t
    # lampu dalam toko (terlihat lewat kaca saat malam)
    li = bpy.data.lights.new(name + "_in", "AREA")
    li.energy = glow
    li.size = 20
    li.color = (1.0, .97, .9)
    lo = bpy.data.objects.new(name + "_in", li)
    lp._link(lo)
    lo.location = (loc[0], loc[1] - 4.0, loc[2] + 4.2)
    out["light"] = lo
    return out


def ruko(mb, x0, x1, y0, depth, rnd, floors=2):
    """deretan ruko sederhana menghadap -Y (muka di y0)."""
    n = max(1, int((x1 - x0) // 6.5))
    uw = (x1 - x0) / n
    for i in range(n):
        ux = x0 + i * uw
        h = 3.6 * floors + rnd.uniform(-.3, 1.2)
        col = rnd.choice(("rk1", "rk2", "rk3", "rk4"))
        mb.box(ux + .05, y0, 0, ux + uw - .05, y0 + depth, h, col)
        mb.box(ux + .6, y0 - .08, .1, ux + uw - .6, y0 + .02, 3.0, rnd.choice(("rk_shut", "rk_shut2")))
        for k in range(6):
            z = .4 + k * .45
            mb.box(ux + .6, y0 - .1, z, ux + uw - .6, y0 - .08, z + .05, "rk_shut2")
        awn = rnd.choice(("rk_awn1", "rk_awn2", "rk_awn3"))
        mb.prism_x([(y0 - 1.5, 3.2), (y0, 3.2), (y0, 3.9)], ux + .2, ux + uw - .2, awn)
        if floors > 1:
            for wx in (.25, .6):
                cx = ux + uw * wx
                mb.box(cx - .9, y0 - .06, 4.5, cx + .9, y0 + .02, 6.2, "rk_win")
        mb.box(ux + uw * .2, y0 - .25, 3.95, ux + uw * .8, y0 - .1, 4.35, "c_white")     # papan nama polos
        mb.box(ux + .05, y0 - .05, h - .3, ux + uw - .05, y0 + depth, h, "rk_shut2")


def power_pole(mb, x, y, h=11.0):
    mb.cyl(x, y, 0, h, .2, "pole_c", n=8, r_top=.15)
    mb.box(x - 1.5, y - .1, h - 1.0, x + 1.5, y + .1, h - .8, "pole_c")
    mb.cyl(x, y + .35, h - 3.0, h - 1.8, .45, "pole_c", n=8)         # trafo kecil


def street_lamp(name, x, y, h=7.5, facing=1, light=0.0):
    mb = W.MB(name)
    mb.cyl(x, y, 0, h, .12, "pole_c", n=8)
    T.beam(mb, (x, y, h), (x, y + facing * 1.8, h + .3), .12, "pole_c")
    mb.box(x - .3, y + facing * 1.8 - .5, h - .05, x + .3, y + facing * 1.8 + .5, h + .35, "mm_frame")
    lamp = W.MB(name + "_b")
    lamp.box(x - .25, y + facing * 1.8 - .45, h - .1, x + .25, y + facing * 1.8 + .45, h - .02, "lamp_w")
    ob = mb.build()
    lb = lamp.build()
    out = dict(pole=ob, bulb=lb)
    if light > 0:
        li = bpy.data.lights.new(name + "_pt", "POINT")
        li.energy = light
        li.color = (1.0, .85, .6)
        li.shadow_soft_size = 1.0
        lo = bpy.data.objects.new(name + "_pt", li)
        lp._link(lo)
        lo.location = (x, y + facing * 1.8, h - .6)
        out["light"] = lo
    return out


def wires(mb, xs, y, h):
    for k in range(len(xs) - 1):
        for dz in (-.85, -1.15):
            a, b = (xs[k], y, h + dz), (xs[k + 1], y, h + dz)
            mid = ((a[0] + b[0]) / 2, y, h + dz - .6)
            T.beam(mb, a, mid, .035, "wire")
            T.beam(mb, mid, b, .035, "wire")


# ------------------------------------------------------------------ dunia
def build_street(seed=3, bikes=True, cars=True, people=True, ext=140.0, night_lamps=0.0, store_glow=0.0,
                 far=True):
    """dunia: jalan, trotoar, lahan parkir, minimarket, ruko, motor & mobil. Return info dict."""
    rnd = random.Random(seed)
    g = W.MB("ground")
    g.box(-ext, -ext, -.3, ext, ext, 0, "pk_ground")
    g.box(-ext, ROAD_Y0, -.02, ext, ROAD_Y1, .02, "pk_asph")
    for x in range(int(-ext), int(ext), 8):                               # marka putus-putus
        g.box(x, -27.15, .02, x + 4, -26.85, .035, "pk_line")
    for yy in (ROAD_Y0 + .5, ROAD_Y1 - .5):
        g.box(-ext, yy - .1, .02, ext, yy + .1, .035, "pk_line")
    g.box(-ext, ROAD_Y1, 0, ext, WALK_Y1, .26, "pk_walk")               # trotoar depan
    g.box(-ext, ROAD_Y1, 0, ext, ROAD_Y1 + .35, .3, "pk_curb")
    g.box(-ext, ROAD_Y0 - 3.2, 0, ext, ROAD_Y0, .26, "pk_walk")          # trotoar seberang
    g.box(-ext, ROAD_Y0 - .35, 0, ext, ROAD_Y0, .3, "pk_curb")
    x0, y0, x1, y1 = LOT
    g.box(x0, y0, 0, x1, y1, .2, "pk_pave")                             # lahan parkir (paving)
    g.box(x0 + 7, ROAD_Y1 + .35, 0, x1 - 7, y0, .205, "pk_pave2")        # mulut masuk (trotoar diturunkan)
    for k in range(25):                                                  # slot motor depan toko
        x = -12.0 + k * 1.0
        g.box(x - .03, -.2, .2, x + .03, 2.9, .215, "pk_line")
    for k in range(17):                                                  # slot motor baris tengah
        x = -8.0 + k * 1.0
        g.box(x - .03, -10.4, .2, x + .03, -7.6, .215, "pk_line")
    for x in (-18.0, -14.6, -11.2, 11.2, 14.6, 18.0):                    # slot mobil
        g.box(x - .05, -16.6, .2, x + .05, -10.6, .215, "pk_line")
    # lahan samping ruko (paving lebih gelap)
    g.box(-60, -17, 0, x0, 2, .12, "pk_pave2")
    g.box(x1, -17, 0, 60, 2, .12, "pk_pave2")
    g.build()
    store = minimarket("mm", (0, STORE[1], .2), glow=store_glow)
    b = W.MB("bldg")
    ruko(b, -58, -21, 2.5, 14, rnd)
    ruko(b, 21, 58, 2.5, 14, rnd)
    ruko(b, -110, -60, 2.5, 14, rnd, floors=3)
    ruko(b, 60, 110, 2.5, 14, rnd, floors=3)
    # seberang jalan (rendah supaya tidak menutup kamera)
    b.box(-ext, -ext, 0, ext, ROAD_Y0 - 3.2, .1, "pk_grass")             # taman seberang jalan
    for x in range(-110, 111, 9):
        b.box(x, ROAD_Y0 - 3.6, 0, x + .12, ROAD_Y0 - 3.4, 1.1, "pole_c")
    b.box(-ext, ROAD_Y0 - 3.6, .9, ext, ROAD_Y0 - 3.4, 1.0, "pole_c")
    xs = list(range(-100, 101, 22))
    for x in xs:
        power_pole(b, x, -18.6)
    wires(b, xs, -18.6, 11.0)
    for x in range(-96, 97, 12):
        if abs(x) > 10:
            C.street_tree(b, x + 5, -36.2, 1.1, rnd)
    for x in (-34, -26, 26, 34):
        C.street_tree(b, x, -18.6 + 1.3, 1.0, rnd)
    b.build()
    lamps = [street_lamp(f"lamp{k}", x, -19.2, 7.5, 1, night_lamps) for k, x in enumerate((-44, -11, 11, 44))]
    if far:
        f = W.MB("far")
        for k in range(46):
            x = -150 + k * 6.7 + rnd.uniform(-1, 1)
            y = 80 + rnd.uniform(0, 40)
            w, h = rnd.uniform(5, 9), rnd.uniform(8, 34)
            f.box(x, y, 0, x + w, y + w, h, rnd.choice(("ct_glass", "ct_glass2", "ct_con", "ct_white", "ct_glass3")))
        f.box(-150, 22, 0, 150, 78, .05, "pk_grass")
        for k in range(60):
            C.street_tree(f, rnd.uniform(-140, 140), rnd.uniform(24, 76), rnd.uniform(1.0, 1.6), rnd)
        f.build()
    info = dict(store=store, lamps=lamps, bikes=[], cars=[], people=[])
    if bikes:
        k = 0
        for i in range(24):
            if rnd.random() < .82:
                x = -11.5 + i * 1.0
                info["bikes"].append(motor(f"bk{k}", (x, 1.3, .2), math.pi / 2 + rnd.uniform(-.06, .06),
                                           rnd.choice(BIKE_COLS), .78))
                k += 1
        for i in range(16):
            if rnd.random() < .7:
                x = -7.5 + i * 1.0
                info["bikes"].append(motor(f"bk{k}", (x, -9.0, .2), -math.pi / 2 + rnd.uniform(-.06, .06),
                                           rnd.choice(BIKE_COLS), .78))
                k += 1
        # motor di depan ruko tetangga
        for i in range(30):
            x = rnd.choice((-1, 1)) * rnd.uniform(22, 56)
            info["bikes"].append(motor(f"bk{k}", (x, rnd.uniform(-3, 0), .12), math.pi / 2 + rnd.uniform(-.1, .1),
                                       rnd.choice(BIKE_COLS), .78))
            k += 1
    if cars:
        for j, x in enumerate((-16.3, -12.9, 12.9, 16.3)):
            if j != 2:
                info["cars"].append(car(f"car{j}", (x, -13.6, .2), math.pi / 2, CAR_COLS[j], .78))
    if people:
        for k in range(5):
            x = rnd.uniform(-10, 10)
            p = shopper(f"sh{k}", k, (x, rnd.uniform(-2.8, -1.2), .2), rnd.uniform(-.6, .6))
            info["people"].append(p)
    return info


# ------------------------------------------------------------------ props data & cerita
def note(mb, x, y, z, kind="n2k", s=1.0):
    """lembar uang kertas datar (Rp2.000 abu-biru, Rp5.000 cokelat)."""
    mb.box(x - .7 * s, y - .34 * s, z, x + .7 * s, y + .34 * s, z + .03 * s, kind)
    mb.box(x - .2 * s, y - .2 * s, z + .03 * s, x + .2 * s, y + .2 * s, z + .04 * s, kind + "2")


def note_obj(name, kind="n2k", s=1.0, loc=(0, 0, 0)):
    mb = W.MB(name)
    note(mb, 0, 0, 0, kind, s)
    ob = mb.build(loc)
    ob.rotation_euler = (math.pi / 2 - .25, 0, 0)        # berdiri menghadap kamera
    return ob


def money_stack(name, layers, loc, kind="money_red", nx=2, ny=1, s=.8):
    """tumpukan ikat uang merah; 1 lapis = Rp500 rb. Return (objek, tinggi)."""
    k2 = {"money_red": "money_red2", "money_dk": "money_dk2", "money_g": "money_g2"}[kind]
    mb = W.MB(name)
    for k in range(int(layers)):
        for i in range(nx):
            for j in range(ny):
                x, y, z = (i - (nx - 1) / 2) * 1.68 * s, (j - (ny - 1) / 2) * .82 * s, k * .29 * s
                mb.box(x - .8 * s, y - .38 * s, z, x + .8 * s, y + .38 * s, z + .26 * s, kind)
                mb.box(x - .82 * s, y - .4 * s, z + .24 * s, x + .82 * s, y + .4 * s, z + .27 * s, k2)
                mb.box(x - .14 * s, y - .41 * s, z - .005, x + .14 * s, y + .41 * s, z + .275 * s, "money_band")
    return mb.build(loc), int(layers) * .29 * s


def glow_screen(name, loc, w=7.0, h=5.0, em=3.5):
    """layar berpendar hangat (untuk siluet 'orang di balik layar')."""
    mb = W.MB(name)
    mb.box(-w / 2 - .3, -.2, 0, w / 2 + .3, .2, h + .6, "scr_frame")
    fr = mb.build(loc)
    s = W.MB(name + "_s")
    s.box(-w / 2, -.25, .3, w / 2, -.21, h + .3, "scr_glow")
    sc = s.build(loc)
    sc.data.materials[0] = emit_mat("scr_glow", em)
    return fr, sc


def sun_icon(name, s=1.0):
    mb = W.MB(name)
    mb.sphere(0, 0, 0, 1.0 * s, "sun_y")
    for k in range(10):
        a = 2 * math.pi * k / 10
        T.beam(mb, (math.cos(a) * 1.35 * s, 0, math.sin(a) * 1.35 * s),
               (math.cos(a) * 1.95 * s, 0, math.sin(a) * 1.95 * s), .22 * s, "sun_y")
    ob = mb.build()
    ob.data.materials[0] = emit_mat("sun_y", 2.0)
    return ob


def cloud(mb, x, y, z, s=1.0, key_="cloud"):
    for dx, dz, r in ((-1.2, 0, .9), (0, .35, 1.2), (1.2, 0, .95), (.5, -.25, .8), (-.5, -.25, .8)):
        mb.sphere(x + dx * s, y, z + dz * s, r * s, key_)


def rain(name, center, area=(26.0, 18.0), h=16.0, n=700, seed=4, f0=1, f1=300, speed=.9):
    """garis hujan: mesh banyak garis tipis, digeser turun berulang (siklus)."""
    rnd = random.Random(seed)
    mb = W.MB(name)
    for _ in range(n):
        x = center[0] + rnd.uniform(-area[0] / 2, area[0] / 2)
        y = center[1] + rnd.uniform(-area[1] / 2, area[1] / 2)
        z = rnd.uniform(0, h)
        mb.box(x - .012, y - .012, z, x + .012, y + .012, z + .45, "rain")
        mb.box(x - .012, y - .012, z + h, x + .012, y + .012, z + h + .45, "rain")
    ob = mb.build()
    ob.data.materials[0] = emit_mat("rain", .6)
    period = max(2, int(h / speed))
    f = f0
    while f <= f1 + period:
        ob.location.z = 0
        ob.keyframe_insert("location", index=2, frame=f)
        ob.location.z = -h
        ob.keyframe_insert("location", index=2, frame=f + period - 1)
        f += period
    return ob


def card(name, body="BPJS", s=1.0):
    """kartu jaminan sosial generik (hijau-putih) berdiri menghadap -Y."""
    mb = W.MB(name)
    L.rbox(mb, -1.6 * s, -.06 * s, 0, 1.6 * s, .06 * s, 2.0 * s, "card_w", c=.15 * s)
    mb.box(-1.6 * s, -.08 * s, 1.35 * s, 1.6 * s, .0, 2.0 * s, "card_g")
    for k in range(3):
        mb.box(-1.3 * s, -.08 * s, (.35 + k * .28) * s, (0 - k * .3) * s, -.06 * s, (.47 + k * .28) * s, "ph_ui2")
    mb.box(.6 * s, -.08 * s, .3 * s, 1.3 * s, -.06 * s, 1.15 * s, "ph_ui")
    ob = mb.build()
    t = H.text(name + "_t", body, .48 * s, "c_white", depth=.03 * s, loc=(0, -.09 * s, 1.5 * s))
    t.parent = ob
    return ob


def mini_store(mb, x, y, s=1.0, busy=1.0, rnd=None):
    """minimarket mini untuk peta kota (+ motor-motor mini sesuai keramaian)."""
    rnd = rnd or random.Random(1)
    mb.box(x - 3 * s, y, 0, x + 3 * s, y + 4 * s, 2.2 * s, "mm_wall2")
    mb.box(x - 3.05 * s, y - .1 * s, 1.6 * s, x + 3.05 * s, y + .1 * s, 2.2 * s, "mm_green")
    mb.box(x - 3.05 * s, y - .12 * s, 1.5 * s, x + 3.05 * s, y + .05 * s, 1.62 * s, "mm_orange")
    mb.box(x - 2.6 * s, y - .05 * s, .1, x + 2.6 * s, y + .02 * s, 1.4 * s, "mm_glass")
    mb.box(x - 3.5 * s, y - 4 * s, 0, x + 3.5 * s, y, .08, "pk_pave")
    for k in range(int(10 * busy)):
        bx = x - 3.0 * s + (k % 10) * .62 * s
        by = y - 1.0 * s - (k // 10) * 1.6 * s
        mb.box(bx - .14 * s, by - .45 * s, .08, bx + .14 * s, by + .45 * s, .55 * s,
               rnd.choice(("bk_red", "bk_blue", "bk_blk", "bk_wht", "bk_grey")))


def city_map(name="map", n_stores=9, seed=8):
    """peta kota mini: blok-blok, jalan, beberapa minimarket dengan parkiran. Return (lokasi toko list)."""
    rnd = random.Random(seed)
    mb = W.MB(name)
    mb.box(-60, -60, -.3, 60, 60, 0, "pk_ground")
    for v in (-36, -12, 12, 36):
        mb.box(v - 2.5, -60, 0, v + 2.5, 60, .05, "pk_asph")
        mb.box(-60, v - 2.5, 0, 60, v + 2.5, .05, "pk_asph")
    spots = []
    cells = [(cx, cy) for cx in (-48, -24, 0, 24, 48) for cy in (-48, -24, 0, 24, 48) if (cx, cy) != (0, 0)]
    rnd.shuffle(cells)
    for i, (cx, cy) in enumerate(cells):
        if i < n_stores:
            mini_store(mb, cx, cy - 2, 1.4, rnd.uniform(.6, 2.0), rnd)
            spots.append((cx, cy - 6))
            for k in range(3):
                bx = cx + rnd.choice((-1, 1)) * rnd.uniform(5, 8)
                mb.box(bx - 2, cy + rnd.uniform(-3, 4), 0, bx + 2, cy + rnd.uniform(5, 8), rnd.uniform(3, 8),
                       rnd.choice(("rk1", "rk2", "rk3", "rk4")))
        else:
            for k in range(4):
                bx, by = cx + rnd.uniform(-7, 4), cy + rnd.uniform(-7, 4)
                mb.box(bx, by, 0, bx + rnd.uniform(3, 6), by + rnd.uniform(3, 6), rnd.uniform(3, 14),
                       rnd.choice(("rk1", "rk2", "rk3", "rk4", "ct_glass", "ct_con")))
            C.street_tree(mb, cx + 6, cy + 6, 1.1, rnd)
    mb.build()
    return spots


def setup_prk_light():
    """siang terik: matahari hangat agak tinggi, langit kamera terang."""
    sun = bpy.data.objects.get("sun")
    sun.data.energy = 3.6
    sun.data.color = (1.0, .95, .86)
    sun.data.angle = math.radians(5)
    sun.rotation_euler = (math.radians(40), 0, math.radians(-38))


def world_nodes():
    w = bpy.context.scene.world
    nt = w.node_tree
    bgs = [n for n in nt.nodes if n.type == "BACKGROUND"]
    return bgs   # [b_light, b_cam] (urutan dibuat di W.setup_world_light)


def day_night(f0, f1, store=None, lamps=(), night=1.0):
    """transisi siang -> malam (f0..f1): langit gelap, matahari redup kebiruan, toko & lampu jalan menyala."""
    sun = bpy.data.objects.get("sun")
    bl, bc = world_nodes()
    day_sky = lp.hex_rgba(lp.PAL["sky"])
    night_sky = lp.hex_rgba("#1E2440")
    pairs = [(f0, 0.0), (f1, night)]
    for f, t in pairs:
        sun.data.energy = 3.6 * (1 - t) + .35 * t
        sun.data.color = (1.0 - .45 * t, .95 - .3 * t, .86 + .1 * t)
        sun.data.keyframe_insert("energy", frame=f)
        sun.data.keyframe_insert("color", frame=f)
        col = tuple(day_sky[i] * (1 - t) + night_sky[i] * t for i in range(3)) + (1,)
        for b, base in ((bl, .75), (bc, 1.0)):
            b.inputs["Color"].default_value = col
            b.inputs["Strength"].default_value = base * (1 - .55 * t)
            b.inputs["Color"].keyframe_insert("default_value", frame=f)
            b.inputs["Strength"].keyframe_insert("default_value", frame=f)
        if store:
            store["light"].data.energy = 2600 * t
            store["light"].data.keyframe_insert("energy", frame=f)
        for lm in lamps:
            if "light" in lm:
                lm["light"].data.energy = 1400 * t
                lm["light"].data.keyframe_insert("energy", frame=f)
    if store:
        b = store["ceil_mat"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
        for f, v in ((f0, 3.0), (f1, 3.0 + 9.0 * night)):
            b.default_value = v
            b.keyframe_insert("default_value", frame=f)
    for lm in lamps:
        m = lp.mat("lamp_w", 0.0).copy()
        lm["bulb"].data.materials[0] = m
        b = m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
        m.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = lp.hex_rgba("#FFE0A0")
        for f, v in ((f0, 0.0), (f1, 6.0 * night)):
            b.default_value = v
            b.keyframe_insert("default_value", frame=f)
