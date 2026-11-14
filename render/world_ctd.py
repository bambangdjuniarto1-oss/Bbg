"""Aset & dunia diorama untuk video "Bedah Bisnis Podcast (Close The Door)".

Isi: studio podcast gelap bergaya talk-show (dinding gelap + kisi kayu, panel akustik, pintu besar
berbingkai lampu hangat, tulisan neon ON AIR, meja kayu, 2 kursi kulit, mic lengan, kamera bertripod,
lampu panel LED, TV, rak + plakat, jendela kaca ke kota), host & bintang tamu (pejabat berpeci, artis
berkacamata hitam), kru produksi, kota metropolitan (gedung kaca tinggi, jalan tol layang, lalu lintas,
papan LED), HP raksasa berisi halaman kanal, plakat subscriber, token "views", kubus 1.000 views, mesin
monetisasi (perhatian -> uang), kotak sponsor, kartu member, penonton mini, ikon biaya, dokumen simulasi.
Semua desain generik (tanpa logo/merek asli). Karakter & bangunan menghadap -Y.
"""
import math
import random

import bpy

import lowpoly as lp
import world as W
import world_hotel as H         # text(), money_bundle(), glassy(), emit()
import world_laundry as L       # character(), pose(), rbox/ball/tube, checkmark, xmark
import world_amdk as M          # pedestal()
import world_tahu as T          # beam()
import world_sawit as K         # calendar()

lp.PAL.update({
    # studio
    "st_wall": "#25272C", "st_wall2": "#1C1E22", "st_panel": "#34373E", "st_panel2": "#2B2E34",
    "st_slat": "#6B4A31", "st_slat2": "#563B27", "st_floor": "#4B3A2E", "st_floor2": "#3F3027",
    "st_rug": "#6E2A27", "st_rug2": "#8A3833", "st_table": "#7A5434", "st_table2": "#5E3F27",
    "st_chair": "#1A1B1E", "st_chair2": "#2D2F34", "st_metal": "#8E959D", "st_metal_dk": "#3A3D43",
    "mic": "#17181B", "mic_grill": "#4A4E55", "warm": "#FFC170", "warm2": "#FFE2B0",
    "neon_red": "#FF3B3B", "door_dk": "#141518", "door_frame": "#5A4130", "led_w": "#FFF6E6",
    "cam_body": "#1E2025", "cam_lens": "#0D0E10", "tally": "#FF2A2A", "tv_scr": "#1F6FE0",
    "st_glass": "#9EC3DD", "pot": "#D8D0C2", "leaf": "#3E8C4E", "leaf2": "#5BAA5E", "mug": "#F2F2F0",
    "book1": "#C2553F", "book2": "#3D6FA8", "book3": "#E2B23A", "book4": "#4F8F5B",
    # orang
    "c_batik": "#8A5A2B", "c_batik2": "#D9A441", "peci": "#16171A", "c_suit": "#2B3442", "c_wine": "#8E2F45",
    "shade": "#121316", "headset": "#202226", "c_black2": "#1C1D21",
    # kota
    "ct_ground": "#C9CCC9", "ct_walk": "#DCDDD8", "ct_road": "#4A4E57", "ct_lane": "#F2F2F2",
    "ct_glass": "#5E87AB", "ct_glass2": "#7FA9CB", "ct_glass3": "#3F6889", "ct_glass4": "#8FBBD0",
    "ct_con": "#D3D6DA", "ct_con2": "#B3B9C0", "ct_white": "#EEF1F4", "ct_dark": "#334255", "ct_acc": "#E3A33B",
    "ct_band": "#E6EAEE", "ct_band2": "#2E3B4B", "ct_park": "#7DB653", "ct_park2": "#6AA548",
    "ct_hwy": "#BFC4C9", "ct_hwy2": "#9CA3AA", "ct_water": "#6FB7D9", "hq_glass": "#2A2F38", "hq_frame": "#14161A",
    "led_r": "#FF3D3D", "led_b": "#3D8BFF", "led_y": "#FFC233", "led_g": "#33D17A",
    # props digital & bisnis
    "yt_red": "#F22B2B", "play_w": "#FFFFFF", "ph_scr": "#F7F8FA", "ph_ui": "#E3E6EA", "ph_ui2": "#C9CED5",
    "gold": "#E8B53A", "gold2": "#C9922A", "silver": "#D7DCE2", "diamond": "#BFE9FF",
    "eye_w": "#FFFFFF", "eye_iris": "#2F80ED", "eye_pupil": "#14161A", "view_cube": "#2F80ED", "view_cube2": "#5AA0FF",
    "sp_a": "#2F80ED", "sp_a2": "#1F5FB8", "sp_b": "#F2994A", "sp_b2": "#C9722F", "member": "#7B5CE6",
    "member2": "#5A3FC0", "coin": "#F2C230", "coin2": "#D9A51E", "mach": "#2B3A55", "mach2": "#3E5478",
    "mach_acc": "#33D17A", "stamp": "#D7322E", "chart_b": "#5AA0FF", "chart_g": "#33C46F",
    "money_g": "#5DBB7A", "money_g2": "#3E9A5C",
})

CH_S = L.CH_S                   # 1.25
SEAT = .56                      # tinggi dudukan kursi
TABLE_Z = .92                   # tinggi meja


# ------------------------------------------------------------------ orang
LOOKS = {
    "host": dict(skin="skin2", top="c_black2", sleeve="c_black2", bottom="c_black2", shoe="shoe_dk", hair="short",
                 hair_col="hair_blk", acc=()),
    "pejabat": dict(skin="skin2", top="c_batik", sleeve="c_batik", bottom="c_black", shoe="shoe_dk", hair="short",
                    hair_col="hair_blk", acc=()),
    "artis": dict(skin="skin1", top="c_wine", sleeve="c_wine", bottom="c_black", shoe="shoe_w", hair="long",
                  hair_col="hair_brn", acc=()),
    "kru1": dict(skin="skin1", top="c_black", sleeve="c_black", bottom="c_denim", shoe="shoe_w", hair="cap",
                 hair_col="c_black", acc=("lanyard",)),
    "kru2": dict(skin="skin3", top="c_grey", sleeve="c_grey", bottom="c_black", shoe="shoe_dk", hair="short",
                 hair_col="hair_dk", acc=("lanyard",)),
    "kru3": dict(skin="skin2", top="c_navy", sleeve="c_navy", bottom="c_khaki", shoe="shoe_w", hair="hijab",
                 hair_col="hij_cream", acc=("lanyard",)),
    "kru4": dict(skin="skin1", top="c_white", sleeve="c_white", bottom="c_black", shoe="shoe_dk", hair="bun",
                 hair_col="hair_blk", acc=("lanyard",)),
    "kru5": dict(skin="skin2", top="c_olive", sleeve="c_olive", bottom="c_black", shoe="shoe_dk", hair="short",
                 hair_col="hair_blk", acc=("lanyard", "glasses")),
    "kru6": dict(skin="skin3", top="c_mustard", sleeve="c_mustard", bottom="c_denim", shoe="shoe_w", hair="hijab",
                 hair_col="hij_navy", acc=("lanyard",)),
}
KRU = ["kru1", "kru2", "kru3", "kru4", "kru5", "kru6"]


def person(name, look, loc=(0, 0, 0), rot=0.0, s=CH_S, hold=None, extra=None):
    """karakter (world_laundry) + aksesori: 'peci', 'shades', 'headset', 'card', 'batik'."""
    lk = dict(LOOKS[look]) if isinstance(look, str) else look
    parts = L.character(name, lk, loc, rot, s, hold)
    extra = extra or ()
    if look == "pejabat":
        extra = tuple(extra) + ("peci", "batik")
    if look == "artis":
        extra = tuple(extra) + ("shades",)
    if extra:
        mb = W.MB(name + "_acc")
        hz = 1.66
        if "peci" in extra:
            mb.cyl(0, .01, hz + .12, hz + .33, .262, "peci", n=14, r_top=.25)
        if "shades" in extra:
            for sx in (-1, 1):
                L.rbox(mb, sx * .09 - .075, -.25, hz - .035, sx * .09 + .075, -.225, hz + .045, "shade", c=.02)
            mb.box(-.02, -.25, hz + .01, .02, -.23, hz + .03, "shade")
        if "headset" in extra:
            mb.box(-.29, -.06, hz - .06, -.25, .06, hz + .08, "headset")
            mb.box(.25, -.06, hz - .06, .29, .06, hz + .08, "headset")
            mb.box(-.27, -.03, hz + .26, .27, .03, hz + .31, "headset")
            T.beam(mb, (-.27, -.04, hz - .04), (-.12, -.25, hz - .1), .03, "headset")
        if "batik" in extra:
            for k in range(4):
                z = .95 + k * .12
                L.tube(mb, 0, 0, z, z + .035, .205 + k * .015, .148, .21 + k * .015, .152, "c_batik2", n=12)
        if "card" in extra:
            L.rbox(mb, .2, -.62, 1.08, .52, -.58, 1.28, "gold", c=.03)
            parts["armR"].rotation_euler = (-1.25, 0, .25)
        acc = mb.build()
        acc.parent = parts["body"]
        parts["acc"] = acc
    return parts


def sit(parts, seat_z=SEAT, f=None):
    """posisi duduk: pinggul di atas dudukan, kaki ke depan, tangan di atas meja."""
    b = parts["body"]
    s = b.scale[0]
    b.location.z = seat_z - .86 * s + .1
    for side in ("L", "R"):
        parts["leg" + side].rotation_euler = (-1.5, 0, 0)
        parts["arm" + side].rotation_euler = (-1.05, 0, (.18 if side == "L" else -.18))
    if f is not None:
        for nm in ("legL", "legR", "armL", "armR"):
            parts[nm].keyframe_insert("rotation_euler", frame=f)


def talk(parts, f0, f1, seed=1, amp=.32, period=22):
    """gestur bicara: lengan bergantian naik-turun + badan sedikit bergoyang."""
    rnd = random.Random(seed)
    b = parts["body"]
    rz = b.rotation_euler.z
    f = f0
    while f <= f1:
        side = rnd.choice(("L", "R"))
        ar = parts["arm" + side]
        base = ar.rotation_euler.copy()
        ar.keyframe_insert("rotation_euler", frame=f)
        ar.rotation_euler = (base.x - amp * rnd.uniform(.6, 1.2), base.y, base.z + (.25 if side == "L" else -.25))
        ar.keyframe_insert("rotation_euler", frame=f + period // 2)
        ar.rotation_euler = base
        ar.keyframe_insert("rotation_euler", frame=f + period)
        b.rotation_euler.z = rz + rnd.uniform(-.06, .06)
        b.keyframe_insert("rotation_euler", frame=f + period // 2)
        f += period + rnd.randint(0, 8)
    b.rotation_euler.z = rz
    b.keyframe_insert("rotation_euler", frame=f)


def mini_person(mb, x, y, z, s, shirt, skin="skin1", hair="hair_blk", card=False):
    """penonton mini (murah): badan silinder + kepala bola."""
    mb.cyl(x, y, z, z + .55 * s, .2 * s, shirt, n=8, r_top=.16 * s)
    mb.sphere(x, y, z + .74 * s, .19 * s, skin)
    mb.sphere(x, y + .03 * s, z + .82 * s, .17 * s, hair, sz=.12 * s)
    if card:
        mb.box(x - .14 * s, y - .32 * s, z + .5 * s, x + .14 * s, y - .29 * s, z + .7 * s, "gold")


# ------------------------------------------------------------------ studio podcast
def armchair(mb, x, y, rot_back, key="st_chair"):
    """kursi kulit; rot_back = arah sandaran (vektor satuan (dx,dy))."""
    dx, dy = rot_back
    L.rbox(mb, x - .62, y - .62, .25, x + .62, y + .62, SEAT, key, c=.12)
    mb.cyl(x, y, 0, .25, .28, "st_metal_dk", n=10)
    mb.cyl(x, y, 0, .05, .6, "st_metal_dk", n=10)
    bx, by = x + dx * .55, y + dy * .55
    if abs(dx) > abs(dy):
        L.rbox(mb, bx - .14, by - .62, SEAT - .05, bx + .14, by + .62, SEAT + 1.15, key, c=.1)
        for sy in (-1, 1):
            L.rbox(mb, x - .55, y + sy * .62 - .12, SEAT - .05, x + .55, y + sy * .62 + .12, SEAT + .32, "st_chair2", c=.05)
    else:
        L.rbox(mb, bx - .62, by - .14, SEAT - .05, bx + .62, by + .14, SEAT + 1.15, key, c=.1)
        for sx in (-1, 1):
            L.rbox(mb, x + sx * .62 - .12, y - .55, SEAT - .05, x + sx * .62 + .12, y + .55, SEAT + .32, "st_chair2", c=.05)


def mic_boom(mb, base, mouth):
    """mic lengan: penjepit di tepi meja -> tiang -> lengan -> mic menggantung ke arah mulut."""
    bx, by = base
    mx, my, mz = mouth
    mb.box(bx - .08, by - .08, TABLE_Z - .1, bx + .08, by + .08, TABLE_Z + .06, "st_metal_dk")
    T.beam(mb, (bx, by, TABLE_Z), (bx, by, mz + .55), .05, "st_metal_dk")
    T.beam(mb, (bx, by, mz + .55), (mx, my, mz + .3), .045, "st_metal_dk")
    mb.cyl(mx, my, mz - .12, mz + .3, .095, "mic", n=10)
    mb.cyl(mx, my, mz - .14, mz + .02, .1, "mic_grill", n=10)


def tripod_cam(name, loc, aim, h=1.8):
    """kamera video di atas tripod, lensa mengarah ke titik `aim`."""
    mb = W.MB(name)
    for k in range(3):
        a = 2 * math.pi * k / 3 + .3
        T.beam(mb, (math.cos(a) * .55, math.sin(a) * .55, 0), (0, 0, h - .1), .05, "st_metal_dk")
    mb.box(-.2, -.2, h - .15, .2, .2, h, "st_metal_dk")
    L.rbox(mb, -.28, -.45, h, .28, .35, h + .5, "cam_body", c=.06)
    mb.box(-.06, .1, h + .5, .06, .3, h + .62, "cam_body")
    mb.disc_y(0, -.45, h + .24, .17, .32, "cam_lens", n=12)
    mb.box(.12, .34, h + .3, .26, .37, h + .46, "tv_scr")
    ob = mb.build(loc)
    ob.rotation_euler.z = math.atan2(aim[1] - loc[1], aim[0] - loc[0]) + math.pi / 2
    tl = W.MB(name + "_tally")
    tl.box(-.05, -.47, h + .44, .05, -.4, h + .5, "tally")
    t = tl.build()
    t.data.materials[0] = lp.mat("tally", emission=6)
    t.parent = ob
    return ob


def led_panel(name, loc, aim, h=2.6, energy=260.0):
    """lampu panel LED di stand + lampu area sungguhan (warm)."""
    mb = W.MB(name)
    for k in range(3):
        a = 2 * math.pi * k / 3
        T.beam(mb, (math.cos(a) * .5, math.sin(a) * .5, 0), (0, 0, h - .5), .045, "st_metal_dk")
    T.beam(mb, (0, 0, h - .6), (0, 0, h), .05, "st_metal_dk")
    L.rbox(mb, -.62, -.12, h - .45, .62, .1, h + .45, "cam_body", c=.04)
    ob = mb.build(loc)
    ang = math.atan2(aim[1] - loc[1], aim[0] - loc[0]) + math.pi / 2
    ob.rotation_euler.z = ang
    sc = W.MB(name + "_s")
    sc.box(-.55, -.14, h - .38, .55, -.12, h + .38, "led_w")
    s = sc.build()
    s.data.materials[0] = lp.mat("led_w", emission=4)
    s.parent = ob
    li = bpy.data.lights.new(name + "_L", "AREA")
    li.size = 1.4
    li.energy = energy
    li.color = (1.0, .86, .68)
    lo = bpy.data.objects.new(name + "_L", li)
    lp._link(lo)
    lo.location = (loc[0], loc[1], loc[2] + h)
    dx, dy = aim[0] - loc[0], aim[1] - loc[1]
    lo.rotation_euler = (math.radians(70), 0, math.atan2(dy, dx) - math.pi / 2)
    return ob


def plant_pot(mb, x, y, s=1.0):
    mb.cyl(x, y, 0, .7 * s, .42 * s, "pot", n=10, r_top=.5 * s)
    rnd = random.Random(int(x * 13 + y * 7))
    for k in range(7):
        a = 2 * math.pi * k / 7 + rnd.uniform(-.3, .3)
        L_ = rnd.uniform(1.0, 1.6) * s
        T.beam(mb, (x, y, .6 * s), (x + math.cos(a) * .55 * s, y + math.sin(a) * .55 * s, .6 * s + L_), .02, "leaf")
        mb.sphere(x + math.cos(a) * .6 * s, y + math.sin(a) * .6 * s, .6 * s + L_, .32 * s,
                  rnd.choice(("leaf", "leaf2")), sz=.16 * s)


ROOM_W, ROOM_D, ROOM_H = 16.0, 12.0, 6.6
DOOR_X, DOOR_W, DOOR_H = -1.6, 2.6, 4.4


def studio(name, loc=(0, 0, 0), window=True, guest="pejabat", host=True, people=True, sign=True):
    """set podcast lengkap. Return dict: door (objek daun pintu, berengsel di kiri), host/guest (parts),
    cams, anchors (titik-titik penting dalam koordinat dunia)."""
    ox, oy, oz = loc
    hw, hd = ROOM_W / 2, ROOM_D / 2
    mb = W.MB(name)
    # lantai kayu + garis papan
    mb.box(-hw, -hd, -.5, hw, hd + .4, 0, "st_floor")
    for k in range(int(ROOM_W)):
        x = -hw + k + .5
        mb.box(x - .02, -hd, 0, x + .02, hd, .006, "st_floor2")
    mb.cyl(0, .4, 0, .03, 4.4, "st_rug", n=32)
    mb.cyl(0, .4, .03, .04, 4.0, "st_rug2", n=32)
    # dinding belakang (y=+hd): kiri pintu kisi kayu, pintu, kanan jendela kaca
    wy0, wy1 = hd, hd + .4
    win_x0 = 2.4 if window else hw
    mb.box(-hw, wy0, 0, DOOR_X - DOOR_W / 2 - .3, wy1, ROOM_H, "st_wall")
    mb.box(DOOR_X + DOOR_W / 2 + .3, wy0, 0, win_x0, wy1, ROOM_H, "st_wall")
    mb.box(DOOR_X - DOOR_W / 2 - .3, wy0, DOOR_H + .3, DOOR_X + DOOR_W / 2 + .3, wy1, ROOM_H, "st_wall")
    x = -hw + .4
    while x < DOOR_X - DOOR_W / 2 - .7:
        mb.box(x, wy0 - .12, .0, x + .2, wy0, ROOM_H - .3, "st_slat")
        x += .46
    # kusen pintu (kayu) + strip lampu hangat (objek terpisah, berpendar)
    for sx in (-1, 1):
        mb.box(DOOR_X + sx * (DOOR_W / 2 + .05) - .2, wy0 - .25, 0, DOOR_X + sx * (DOOR_W / 2 + .05) + .2, wy1, DOOR_H + .3,
               "door_frame")
    mb.box(DOOR_X - DOOR_W / 2 - .25, wy0 - .25, DOOR_H, DOOR_X + DOOR_W / 2 + .25, wy1, DOOR_H + .35, "door_frame")
    mb.box(DOOR_X - DOOR_W / 2, wy1 - .05, 0, DOOR_X + DOOR_W / 2, wy1 + .4, DOOR_H, "warm2")   # cahaya di balik pintu
    if window:
        mb.box(win_x0, wy0, 0, hw, wy1, .9, "st_wall")
        mb.box(win_x0, wy0, ROOM_H - .5, hw, wy1, ROOM_H, "st_wall")
        for k in range(4):
            x = win_x0 + k * (hw - win_x0) / 3
            mb.box(x - .07, wy0 - .05, .9, x + .07, wy1, ROOM_H - .5, "hq_frame")
        mb.box(win_x0, wy0 - .05, 3.6, hw, wy1, 3.72, "hq_frame")
    # dinding kiri (x=-hw) + panel akustik
    mb.box(-hw - .4, -hd, 0, -hw, wy1, ROOM_H, "st_wall2")
    for i in range(6):
        for j in range(3):
            y = -hd + 1.0 + i * 1.75
            z = 1.4 + j * 1.6
            L.rbox(mb, -hw, y, z, -hw + .14, y + 1.5, z + 1.4, ("st_panel", "st_panel2")[(i + j) % 2], c=.08)
    # rak dinding kiri + buku + plakat emas
    for z in (1.0, 2.2):
        mb.box(-hw, hd - 3.6, z, -hw + .5, hd - .6, z + .08, "st_slat")
        rnd = random.Random(int(z * 10))
        y = hd - 3.5
        while y < hd - 1.6:
            w = rnd.uniform(.12, .2)
            mb.box(-hw + .05, y, z + .08, -hw + .4, y + w, z + .08 + rnd.uniform(.45, .7), rnd.choice(("book1", "book2", "book3", "book4")))
            y += w + .02
    L.rbox(mb, -hw + .1, hd - 1.45, 2.3, -hw + .2, hd - .75, 3.2, "gold", c=.04)
    mb.box(-hw + .2, hd - 1.3, 2.45, -hw + .23, hd - .9, 3.05, "silver")
    # TV di dinding belakang kiri
    tvx = -5.4
    mb.box(tvx - 1.7, wy0 - .22, 2.7, tvx + 1.7, wy0 - .12, 4.7, "cam_body")
    # meja kayu + kaki
    L.rbox(mb, -1.7, -.6, TABLE_Z - .1, 1.7, 1.4, TABLE_Z, "st_table", c=.35)
    for sx in (-1.2, 1.2):
        mb.box(sx - .1, .3, 0, sx + .1, .5, TABLE_Z - .1, "st_table2")
    mb.box(-1.3, .3, .05, 1.3, .5, .2, "st_table2")
    # barang di meja: 2 cangkir, laptop, kertas
    for x, y in ((-1.05, .9), (1.1, -.1)):
        mb.cyl(x, y, TABLE_Z, TABLE_Z + .26, .11, "mug", n=10)
    mb.box(-.45, .55, TABLE_Z, .45, 1.15, TABLE_Z + .04, "st_metal")
    T.beam(mb, (-.45, 1.15, TABLE_Z + .04), (-.45, 1.32, TABLE_Z + .62), .01, "st_metal")
    mb.poly([(-.45, 1.13, TABLE_Z + .04), (.45, 1.13, TABLE_Z + .04), (.45, 1.33, TABLE_Z + .64), (-.45, 1.33, TABLE_Z + .64)],
            [(0, 1, 2, 3)], "st_metal")
    mb.box(.1, -.4, TABLE_Z, .55, -.0, TABLE_Z + .015, "paper_w")
    # 2 kursi
    hx, gx = -2.35, 2.35
    armchair(mb, hx, .4, (-1, 0))
    armchair(mb, gx, .4, (1, 0))
    # mic
    mz = SEAT + 1.0
    mic_boom(mb, (-1.55, 1.25), (-1.75, .35, mz))
    mic_boom(mb, (1.55, 1.25), (1.75, .35, mz))
    # tanaman
    plant_pot(mb, -hw + 1.0, -hd + 1.2, 1.1)
    plant_pot(mb, -hw + 1.0, hd - 4.5, .9)
    plant_pot(mb, hw - 1.0, hd - 1.0, 1.0)
    # rangka lampu atas (truss) + lampu sorot
    for y in (-1.5, 2.5):
        mb.box(-hw, y - .12, ROOM_H + .2, hw * .7, y + .12, ROOM_H + .44, "st_metal_dk")
        for x in (-4.5, -1.5, 1.5, 4.5):
            mb.box(x - .03, y - .03, ROOM_H - .2, x + .03, y + .03, ROOM_H + .2, "st_metal_dk")
            mb.cyl(x, y, ROOM_H - .65, ROOM_H - .2, .22, "cam_body", n=8, r_top=.16)
    room = mb.build((ox, oy, oz))
    # bagian berpendar: strip lampu kusen, layar TV, neon
    gl = W.MB(name + "_glow")
    for sx in (-1, 1):
        gl.box(DOOR_X + sx * (DOOR_W / 2 + .3) - .04, wy0 - .28, .1, DOOR_X + sx * (DOOR_W / 2 + .3) + .04, wy0 - .22, DOOR_H + .3,
               "warm")
    gl.box(DOOR_X - DOOR_W / 2 - .3, wy0 - .28, DOOR_H + .38, DOOR_X + DOOR_W / 2 + .3, wy0 - .22, DOOR_H + .44, "warm")
    gl.box(-hw + .5, wy0 - .14, ROOM_H - .45, DOOR_X - DOOR_W / 2 - .6, wy0 - .1, ROOM_H - .38, "warm")
    for x in (-4.5, -1.5, 1.5, 4.5):
        for y in (-1.5, 2.5):
            gl.cyl(x, y, ROOM_H - .67, ROOM_H - .64, .15, "warm2", n=8)
    glow = gl.build((ox, oy, oz))
    glow.data.materials[0] = lp.mat("warm", emission=5)
    if len(glow.data.materials) > 1:
        glow.data.materials[1] = lp.mat("warm2", emission=4)
    tv = W.MB(name + "_tv")
    tv.box(tvx - 1.58, wy0 - .24, 2.82, tvx + 1.58, wy0 - .22, 4.58, "tv_scr")
    tvo = tv.build((ox, oy, oz))
    tvo.data.materials[0] = lp.mat("tv_scr", emission=1.6)
    tvp = W.MB(name + "_tvplay")
    tvp.poly([(tvx - .5, wy0 - .26, 3.15), (tvx + .62, wy0 - .26, 3.7), (tvx - .5, wy0 - .26, 4.25)], [(0, 1, 2)], "play_w")
    tvp.build((ox, oy, oz)).data.materials[0] = lp.mat("play_w", emission=2.5)
    if sign:
        nt = H.text(name + "_onair", "ON AIR", .62, "neon_red", depth=.06, loc=(ox - 5.4, oy + wy0 - .3, oz + 5.0),
                    emission=6)
        _ = nt
    # daun pintu (engsel kiri), menghadap -Y; buka = rotasi z negatif
    dm = W.MB(name + "_door")
    dm.box(0, -.12, 0, DOOR_W, .0, DOOR_H, "door_dk")
    for k in range(3):
        dm.box(.25, -.15, .5 + k * 1.3, DOOR_W - .25, -.12, 1.5 + k * 1.3, "st_wall")
    dm.box(DOOR_W - .45, -.3, 2.0, DOOR_W - .35, -.15, 2.6, "gold")
    door = dm.build((ox + DOOR_X - DOOR_W / 2, oy + wy0 - .02, oz))
    # jendela kaca + kota di baliknya (studio di lantai atas: gedung-gedung mulai dari bawah)
    if window:
        skyline(name + "_sky", (ox, oy + hd + 18, oz - 14))
        gm = W.MB(name + "_glass")
        gm.box(win_x0, wy0 + .15, .9, hw, wy0 + .2, ROOM_H - .5, "st_glass")
        g = gm.build((ox, oy, oz))
        H.glassy("st_glass", .18)
        _ = g
    out = {"room": room, "door": door, "glow": glow, "anchors": {}}
    A = out["anchors"]
    A["DOOR"] = (ox + DOOR_X, oy + wy0, oz + DOOR_H + .6)
    A["TABLE"] = (ox, oy + .4, oz + TABLE_Z + .2)
    A["TV"] = (ox + tvx, oy + wy0, oz + 4.8)
    A["CAM"] = (ox - 5.6, oy - 3.6, oz + 2.6)
    A["LIGHT"] = (ox + 6.2, oy - 1.2, oz + 3.2)
    A["MIC"] = (ox - 1.75, oy + .35, oz + mz + .5)
    if people:
        if host:
            hp = person(name + "_host", "host", (ox + hx, oy + .4, oz), math.pi / 2)
            sit(hp)
            hp["body"].location.z += oz
            out["host"] = hp
            A["HOST"] = (ox + hx, oy + .4, oz + 2.75)
        if guest:
            gp = person(name + "_guest", guest, (ox + gx, oy + .4, oz), -math.pi / 2)
            sit(gp)
            gp["body"].location.z += oz
            out["guest"] = gp
            A["GUEST"] = (ox + gx, oy + .4, oz + 2.75)
    out["cams"] = [tripod_cam(name + "_c1", (ox - 5.6, oy - 3.6, oz), (ox + gx, oy + .4, 1.6)),
                   tripod_cam(name + "_c2", (ox + 5.4, oy - 3.4, oz), (ox + hx, oy + .4, 1.6)),
                   tripod_cam(name + "_c3", (ox + 6.4, oy + 3.6, oz), (ox, oy + .4, 1.4))]
    out["leds"] = [led_panel(name + "_l1", (ox - 6.3, oy - 1.0, oz), (ox, oy + .4, 1.5)),
                   led_panel(name + "_l2", (ox + 6.2, oy - 1.2, oz), (ox, oy + .4, 1.5))]
    # lampu atas hangat (lembut) supaya ruangan gelap tetap terbaca
    li = bpy.data.lights.new(name + "_top", "AREA")
    li.size = 9.0
    li.energy = 900.0
    li.color = (1.0, .9, .78)
    lo = bpy.data.objects.new(name + "_top", li)
    lp._link(lo)
    lo.location = (ox, oy + .5, oz + ROOM_H + .1)
    return out


def skyline(name, loc, seed=11):
    """deretan gedung di balik jendela studio (dasar di z loc[2])."""
    rnd = random.Random(seed)
    mb = W.MB(name)
    mb.box(-60, -6, -1, 70, 90, 0, "ct_ground")
    for k in range(16):
        x = -30 + k * 6.5 + rnd.uniform(-1.5, 1.5)
        y = rnd.uniform(4, 60)
        tower(mb, x, y, rnd.uniform(6, 10), rnd.uniform(6, 10), rnd.uniform(26, 62), rnd)
    return mb.build(loc)


def open_door(door, f0, f1, ang=-1.9):
    from scenes import key
    key(door, "rotation_euler", 1, (0, 0, 0))
    key(door, "rotation_euler", f0, (0, 0, 0))
    key(door, "rotation_euler", f1, (0, 0, ang))


# ------------------------------------------------------------------ kota metropolitan
def tower(mb, cx, cy, w, d, h, rnd, kind=None):
    """gedung tinggi di koordinat dunia. kind: glass | step | round | slab | crown."""
    kind = kind or rnd.choice(("glass", "glass", "step", "round", "slab", "crown"))
    glass = rnd.choice(("ct_glass", "ct_glass2", "ct_glass3", "ct_glass4"))
    band = rnd.choice(("ct_band", "ct_band", "ct_band2", "ct_con"))
    fh = 3.4
    if kind == "round":
        n = 10
        mb.cyl(cx, cy, 0, h, min(w, d) / 2, glass, n=n)
        for f in range(1, int(h / fh)):
            mb.cyl(cx, cy, f * fh, f * fh + .35, min(w, d) / 2 + .12, band, n=n)
        mb.cyl(cx, cy, h, h + 1.2, min(w, d) / 2 * .8, band, n=n)
        mb.cyl(cx, cy, h + 1.2, h + 7, .25, "ct_con2", n=6)
        return h + 7
    if kind == "step":
        tiers = [(w, d, h * .55), (w * .78, d * .78, h * .82), (w * .55, d * .55, h)]
        z0 = 0
        for tw, td, th in tiers:
            mb.box(cx - tw / 2, cy - td / 2, z0, cx + tw / 2, cy + td / 2, th, glass)
            f = z0 + fh
            while f < th - .5:
                mb.box(cx - tw / 2 - .1, cy - td / 2 - .1, f, cx + tw / 2 + .1, cy + td / 2 + .1, f + .35, band)
                f += fh
            mb.box(cx - tw / 2 - .25, cy - td / 2 - .25, th, cx + tw / 2 + .25, cy + td / 2 + .25, th + .6, "ct_con")
            z0 = th
        mb.cyl(cx, cy, h + .6, h + 9, .3, "ct_con2", n=6)
        return h + 9
    if kind == "slab":
        mb.box(cx - w / 2, cy - d / 2, 0, cx + w / 2, cy + d / 2, h, "ct_con")
        f = fh
        while f < h - .5:
            mb.box(cx - w / 2 - .05, cy - d / 2 - .25, f + .8, cx + w / 2 + .05, cy + d / 2 + .25, f + 2.6, glass)
            f += fh
        mb.box(cx - w / 2 - .3, cy - d / 2 - .3, h, cx + w / 2 + .3, cy + d / 2 + .3, h + .6, "ct_con2")
        return h + .6
    mb.box(cx - w / 2, cy - d / 2, 0, cx + w / 2, cy + d / 2, h, glass)
    f = fh
    while f < h - .5:
        mb.box(cx - w / 2 - .1, cy - d / 2 - .1, f, cx + w / 2 + .1, cy + d / 2 + .1, f + .3, band)
        f += fh
    # garis vertikal (mullion) di sisi depan & samping
    for k in range(1, 4):
        x = cx - w / 2 + k * w / 4
        mb.box(x - .12, cy - d / 2 - .14, 0, x + .12, cy - d / 2 + .1, h, band)
        y = cy - d / 2 + k * d / 4
        mb.box(cx - w / 2 - .14, y - .12, 0, cx - w / 2 + .1, y + .12, h, band)
        mb.box(cx + w / 2 - .1, y - .12, 0, cx + w / 2 + .14, y + .12, h, band)
    if kind == "crown":
        mb.box(cx - w / 2 - .3, cy - d / 2 - .3, h, cx + w / 2 + .3, cy + d / 2 + .3, h + 1.0, "ct_acc")
        mb.poly([(cx - w / 2, cy - d / 2, h + 1), (cx + w / 2, cy - d / 2, h + 1), (cx + w / 2, cy + d / 2, h + 1),
                 (cx - w / 2, cy + d / 2, h + 1), (cx, cy, h + 1 + min(w, d) * .9)],
                [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)], glass)
        return h + 1 + min(w, d) * .9
    mb.box(cx - w / 2 - .3, cy - d / 2 - .3, h, cx + w / 2 + .3, cy + d / 2 + .3, h + .7, "ct_con")
    mb.box(cx - w * .25, cy - d * .25, h + .7, cx + w * .25, cy + d * .25, h + 3.0, "ct_con2")
    return h + 3


BLOCK = 44.0          # jarak antar sumbu jalan
RD = 9.0              # lebar jalan biasa
BLVD = 16.0           # lebar jalan protokol (x=0)
HWY_Y = -BLOCK / 2    # jalan tol layang sejajar sumbu X di y ini... (di atas jalan y = -22)
HQ = (0.0, 30.0)      # kantor/studio utama (blok depan plaza)


def road_lines(mb, ext):
    n = int(ext // BLOCK) + 1
    for k in range(-n, n + 1):
        c = k * BLOCK + BLOCK / 2
        w = RD
        mb.box(-ext, c - w / 2, 0, ext, c + w / 2, .04, "ct_road")
        x = -ext
        while x < ext:
            mb.box(x, c - .08, .04, x + 2.4, c + .08, .05, "ct_lane")
            x += 6
        if k != 0:
            mb.box(c - w / 2, -ext, 0, c + w / 2, ext, .045, "ct_road")
            y = -ext
            while y < ext:
                mb.box(c - .08, y, .045, c + .08, y + 2.4, .055, "ct_lane")
                y += 6
    # jalan protokol x=0 dengan median taman
    mb.box(-BLVD / 2, -ext, 0, BLVD / 2, ext, .05, "ct_road")
    mb.box(-1.0, -ext, .05, 1.0, ext, .3, "ct_park2")
    for sx in (-1, 1):
        y = -ext
        while y < ext:
            mb.box(sx * 4.2 - .08, y, .05, sx * 4.2 + .08, y + 2.4, .06, "ct_lane")
            y += 6


def street_tree(mb, x, y, s=1.0, rnd=None):
    mb.box(x - .18 * s, y - .18 * s, 0, x + .18 * s, y + .18 * s, 1.6 * s, "trunk")
    mb.sphere(x, y, 2.6 * s, 1.3 * s, (rnd or random).choice(("tree_l", "tree_m")), sz=1.4 * s)


def hq_building(name, loc=HQ, h=26.0, w=22.0, d=16.0):
    """gedung studio/kantor media: kaca gelap, pintu raksasa berbingkai cahaya di lantai dasar,
    lantai atas dengan strip lampu. Menghadap -Y. Return dict(door, glow, top)."""
    cx, cy = loc
    mb = W.MB(name)
    mb.box(cx - w / 2, cy - d / 2, 0, cx + w / 2, cy + d / 2, h, "hq_glass")
    f = 7.0
    while f < h - 1:
        mb.box(cx - w / 2 - .15, cy - d / 2 - .15, f, cx + w / 2 + .15, cy + d / 2 + .15, f + .35, "hq_frame")
        f += 3.8
    for k in range(1, 6):
        x = cx - w / 2 + k * w / 6
        mb.box(x - .1, cy - d / 2 - .2, 7, x + .1, cy - d / 2, h, "hq_frame")
    mb.box(cx - w / 2 - .4, cy - d / 2 - .4, h, cx + w / 2 + .4, cy + d / 2 + .4, h + .8, "hq_frame")
    mb.box(cx - w / 2 - .2, cy - d / 2 - .6, 0, cx + w / 2 + .2, cy - d / 2, 7.0, "st_wall")       # lobi gelap
    mb.box(cx - 4.6, cy - d / 2 - 1.4, 0, cx + 4.6, cy - d / 2 - .6, 6.2, "door_frame")              # kusen pintu besar
    mb.box(cx - 3.6, cy - d / 2 - 1.5, 0, cx + 3.6, cy - d / 2 - .6, 5.4, "warm2")                  # cahaya di balik pintu
    for k in range(7):
        y = cy - d / 2 - 3 - k * 1.1
        mb.box(cx - 4.0 - k * .3, y - .55, 0, cx + 4.0 + k * .3, y + .55, .12 - k * .015, "ct_walk")
    ob = mb.build()
    gl = W.MB(name + "_glow")
    gl.box(cx - 4.0, cy - d / 2 - 1.55, 5.4, cx + 4.0, cy - d / 2 - 1.45, 5.6, "warm")
    for sx in (-1, 1):
        gl.box(cx + sx * 3.8 - .1, cy - d / 2 - 1.55, 0, cx + sx * 3.8 + .1, cy - d / 2 - 1.45, 5.6, "warm")
    gl.box(cx - w / 2, cy - d / 2 - .25, h - .6, cx + w / 2, cy - d / 2 - .15, h - .3, "warm")
    glow = gl.build()
    glow.data.materials[0] = lp.mat("warm", emission=6)
    # 2 daun pintu (engsel di luar) -> buka ke dalam (rotasi)
    doors = []
    for sx in (-1, 1):
        dm = W.MB(f"{name}_d{sx}")
        x0, x1 = (0, 3.6) if sx < 0 else (-3.6, 0)
        dm.box(x0, -.3, 0, x1, 0, 5.4, "door_dk")
        dm.box(x0 + .3, -.35, .5, x1 - .3, -.3, 4.9, "hq_frame")
        hx = 3.25 if sx < 0 else -3.25
        dm.box(hx - .07, -.5, 2.3, hx + .07, -.35, 3.1, "gold")
        doors.append(dm.build((cx + sx * 3.6, cy - d / 2 - 1.5, 0)))
    return {"body": ob, "glow": glow, "doors": doors, "top": (cx, cy, h + .8), "door_pos": (cx, cy - d / 2 - 1.5, 3.0)}


def billboard(name, loc, w, h, key_="led_r", facing=0.0, em=2.5, z=0.0):
    """papan LED (menghadap -Y sebelum diputar `facing`)."""
    mb = W.MB(name)
    mb.box(-w / 2 - .3, -.4, -.3, w / 2 + .3, .4, h + .3, "hq_frame")
    ob = mb.build((loc[0], loc[1], z))
    ob.rotation_euler.z = facing
    sm = W.MB(name + "_s")
    sm.box(-w / 2, -.45, 0, w / 2, -.4, h, key_)
    s = sm.build()
    s.data.materials[0] = lp.mat(key_, emission=em)
    s.parent = ob
    return ob


def build_city(seed=5, ext=230.0, hq=True, clear=None, plaza=True, highway=True, dense=1.0):
    """kota metropolitan: grid jalan + jalan protokol bermedian, gedung tinggi (makin tinggi ke pusat),
    taman, jalan tol layang, plaza + gedung studio utama. clear: (x0,y0,x1,y1) area dikosongkan."""
    rnd = random.Random(seed)
    g = W.MB("city_ground")
    g.box(-ext * 2.4, -ext * 2.4, -1, ext * 2.4, ext * 2.4, -.05, "ct_con2")
    g.box(-ext, -ext, -1, ext, ext, 0, "ct_ground")
    road_lines(g, ext)
    g.build()
    info = {"hq": None, "billboards": []}
    n = int(ext // BLOCK)
    chunk = {}
    for i in range(-n, n):
        for j in range(-n, n):
            bx0 = i * BLOCK + BLOCK / 2 + RD / 2 + 1.0
            bx1 = (i + 1) * BLOCK + BLOCK / 2 - RD / 2 - 1.0
            by0 = j * BLOCK + BLOCK / 2 + RD / 2 + 1.0
            by1 = (j + 1) * BLOCK + BLOCK / 2 - RD / 2 - 1.0
            # jalan protokol x=0 memotong blok i=-1 (x -22..22)
            if bx0 < BLVD / 2 + 1 and bx1 > -BLVD / 2 - 1:
                parts = [(bx0, -BLVD / 2 - 1.5), (BLVD / 2 + 1.5, bx1)]
            else:
                parts = [(bx0, bx1)]
            key_ = (i // 2, j // 2)
            mb = chunk.setdefault(key_, W.MB(f"city_{key_[0]}_{key_[1]}"))
            for px0, px1 in parts:
                if px1 - px0 < 6:
                    continue
                cxm, cym = (px0 + px1) / 2, (by0 + by1) / 2
                if clear and clear[0] < cxm < clear[2] and clear[1] < cym < clear[3]:
                    mb.box(px0, by0, 0, px1, by1, .12, "ct_walk")
                    continue
                if hq and abs(cxm - HQ[0]) < 30 and abs(cym - HQ[1]) < 22:
                    continue
                if plaza and abs(cxm) < 30 and -22 < cym < 8:
                    continue
                mb.box(px0, by0, 0, px1, by1, .14, "ct_walk")
                dist = math.hypot(cxm, cym)
                if rnd.random() < .12 and dist > 40:          # taman
                    mb.box(px0 + .8, by0 + .8, .14, px1 - .8, by1 - .8, .3, "ct_park")
                    for _ in range(int((px1 - px0) * (by1 - by0) / 70)):
                        street_tree(mb, rnd.uniform(px0 + 2, px1 - 2), rnd.uniform(by0 + 2, by1 - 2), rnd.uniform(.9, 1.3), rnd)
                    continue
                hmax = (110 - min(dist, ext) * .32) * dense
                cols = 2 if px1 - px0 > 20 else 1
                rows = 2 if by1 - by0 > 20 else 1
                cw, rh = (px1 - px0) / cols, (by1 - by0) / rows
                for a in range(cols):
                    for b in range(rows):
                        if rnd.random() < .12:
                            continue
                        tw = rnd.uniform(cw * .55, cw * .85)
                        td = rnd.uniform(rh * .55, rh * .85)
                        tcx = px0 + (a + .5) * cw + rnd.uniform(-1, 1)
                        tcy = by0 + (b + .5) * rh + rnd.uniform(-1, 1)
                        hh = rnd.uniform(.3, 1.0) * hmax
                        hh = max(14, hh)
                        top = tower(mb, tcx, tcy, tw, td, hh, rnd)
                        if rnd.random() < .08 and len(info["billboards"]) < 10:
                            info["billboards"].append((tcx, tcy - td / 2, hh * .55, tw * .8))
                        _ = top
    for k, mb in chunk.items():
        if mb.v:
            mb.build()
    # pohon di median & trotoar jalan protokol
    tm = W.MB("city_trees")
    y = -ext
    while y < ext:
        if not (-30 < y < 40):
            street_tree(tm, 0, y, 1.0, rnd)
        for sx in (-1, 1):
            street_tree(tm, sx * (BLVD / 2 + 2.6), y + 4, .8, rnd)
        y += 9
    tm.build()
    # billboard LED di fasad gedung
    for k, (x, y_, z, w) in enumerate(info["billboards"]):
        billboard(f"bb{k}", (x, y_ - .5), min(w, 12), min(w, 12) * .55, rnd.choice(("led_r", "led_b", "led_y")), 0.0,
                  2.2, z)
    if plaza:
        pm = W.MB("plaza")
        pm.box(-30, -21, 0, 30, 7, .16, "ct_walk")
        pm.cyl(0, -8, .16, .9, 6.5, "ct_con", n=24)
        pm.cyl(0, -8, .9, 1.0, 5.6, "ct_water", n=24)
        pm.cyl(0, -8, .9, 3.4, .5, "ct_con", n=10)
        for sx in (-1, 1):
            for yy in (-16, 0):
                pm.box(sx * 20 - 5, yy - 3, .16, sx * 20 + 5, yy + 3, .5, "ct_park")
                street_tree(pm, sx * 20, yy, 1.1, rnd)
        pm.build()
    if hq:
        info["hq"] = hq_building("hq")
    if highway:
        hwy = W.MB("hwy")
        yc = -BLOCK * 1.5
        z = 9.0
        hwy.box(-ext * 1.6, yc - 6, z, ext * 1.6, yc + 6, z + 1.0, "ct_hwy")
        for sy in (-1, 1):
            hwy.box(-ext * 1.6, yc + sy * 6 - .3, z + 1.0, ext * 1.6, yc + sy * 6 + .3, z + 1.9, "ct_hwy2")
        x = -ext * 1.6
        while x < ext * 1.6:
            hwy.box(x - 1.0, yc - 2.0, 0, x + 1.0, yc + 2.0, z, "ct_hwy2")
            hwy.box(x - 1.2, yc - 5.5, z - 1.2, x + 1.2, yc + 5.5, z, "ct_hwy2")
            hwy.box(x, yc - .1, z + 1.0, x + 3, yc + .1, z + 1.03, "ct_lane")
            x += 18
        hwy.build()
        info["hwy"] = (yc, z + 1.0)
    return info


def city_traffic(n_frames, ext=200.0, seed=9, n=16, fps=30, speed=11.0, hwy=None):
    """mobil bergerak di jalan protokol (x=0), jalan melintang, dan tol layang."""
    rnd = random.Random(seed)
    cars = []
    lanes = [("y", -2.2, 1), ("y", 2.2, -1), ("y", -6.0, 1), ("y", 6.0, -1)]
    lanes += [("x", BLOCK / 2 - 2.2, 1), ("x", BLOCK / 2 + 2.2, -1), ("x", -BLOCK / 2 - 2.2, 1),
              ("x", BLOCK * 1.5 + 2.2, -1)]
    if hwy:
        yc, z = hwy
        lanes += [("hx", yc - 3, 1), ("hx", yc + 3, -1), ("hx", yc - 1.2, 1)]
    for k in range(n):
        ax, off, sg = lanes[k % len(lanes)]
        c = lp.car(f"car{k}", 4.4)
        d = speed * n_frames / fps
        s0 = rnd.uniform(-ext * .6, ext * .6)
        if ax == "y":                 # bergerak sepanjang Y di jalan protokol
            c.rotation_euler.z = math.pi / 2 if sg > 0 else -math.pi / 2
            p0, p1 = (off, s0, .05), (off, s0 + sg * d, .05)
        elif ax == "x":
            c.rotation_euler.z = 0 if sg > 0 else math.pi
            p0, p1 = (s0, off, .05), (s0 + sg * d, off, .05)
        else:
            c.rotation_euler.z = 0 if sg > 0 else math.pi
            p0, p1 = (s0, off, hwy[1]), (s0 + sg * d * 1.4, off, hwy[1])
        c.location = p0
        c.keyframe_insert("location", frame=1)
        c.location = p1
        c.keyframe_insert("location", frame=n_frames)
        for fc in W_fcurves(c):
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"
        cars.append(c)
    return cars


def W_fcurves(ob):
    return L._fc(ob)


# ------------------------------------------------------------------ props digital
def phone_channel(name, s=1.0):
    """HP raksasa berdiri (menghadap -Y) berisi halaman kanal: banner, avatar, tombol subscribe merah,
    grid thumbnail video. Return objek HP (teks 'SUBSCRIBE' sudah terpasang)."""
    mb = W.MB(name)
    L.rbox(mb, -1.5 * s, -.14 * s, 0, 1.5 * s, .14 * s, 6.2 * s, "phone_blk", c=.3 * s)
    mb.box(-1.36 * s, -.16 * s, .25 * s, 1.36 * s, -.14 * s, 5.95 * s, "ph_scr")
    mb.box(-1.36 * s, -.17 * s, 4.75 * s, 1.36 * s, -.16 * s, 5.95 * s, "ct_dark")              # banner
    mb.box(-1.2 * s, -.18 * s, 5.2 * s, .2 * s, -.17 * s, 5.5 * s, "ct_glass2")
    mb.disc_y(-.75 * s, -.17 * s, 4.45 * s, .42 * s, .02 * s, "st_chair", n=16)                # avatar
    mb.disc_y(-.75 * s, -.19 * s, 4.45 * s, .34 * s, .02 * s, "gold", n=16)
    mb.box(-.15 * s, -.18 * s, 4.5 * s, 1.15 * s, -.17 * s, 4.62 * s, "ph_ui2")
    mb.box(-.15 * s, -.18 * s, 4.3 * s, .7 * s, -.17 * s, 4.38 * s, "ph_ui")
    mb.box(-1.2 * s, -.18 * s, 3.5 * s, 1.2 * s, -.17 * s, 3.95 * s, "yt_red")                # tombol subscribe
    for r in range(3):
        for c in range(2):
            x0 = -1.2 * s + c * 1.25 * s
            z0 = 2.35 * s - r * 1.0 * s
            mb.box(x0, -.18 * s, z0, x0 + 1.15 * s, -.17 * s, z0 + .75 * s,
                   ("ct_glass3", "st_rug", "ct_acc", "ct_glass", "c_batik", "st_chair2")[r * 2 + c])
            mb.poly([(x0 + .48 * s, -.185 * s, z0 + .22 * s), (x0 + .72 * s, -.185 * s, z0 + .375 * s),
                     (x0 + .48 * s, -.185 * s, z0 + .53 * s)], [(0, 1, 2)], "play_w")
    ob = mb.build()
    t = H.text(name + "_sub", "SUBSCRIBE", .3 * s, "play_w", depth=.02 * s, loc=(0, -.19 * s, 3.6 * s))
    t.parent = ob
    return ob


def play_plaque(name, s=1.0, key_="gold"):
    """plakat penghargaan (bingkai + tombol play generik), berdiri menghadap -Y."""
    mb = W.MB(name)
    L.rbox(mb, -1.3 * s, -.1 * s, 0, 1.3 * s, .1 * s, 3.1 * s, "st_chair", c=.12 * s)
    L.rbox(mb, -1.1 * s, -.14 * s, .2 * s, 1.1 * s, -.08 * s, 2.9 * s, key_, c=.1 * s)
    mb.disc_y(0, -.14 * s, 1.75 * s, .72 * s, .06 * s, "play_w" if key_ != "play_w" else "gold", n=20)
    mb.poly([(-.25 * s, -.21 * s, 1.43 * s), (.38 * s, -.21 * s, 1.75 * s), (-.25 * s, -.21 * s, 2.07 * s)],
            [(0, 1, 2)], key_)
    mb.box(-.8 * s, -.16 * s, .45 * s, .8 * s, -.13 * s, .62 * s, "st_chair")
    return mb.build()


def eye_token(name, s=1.0, loc=(0, 0, 0)):
    """token 'views' (mata): cakram putih + iris biru + pupil, menghadap -Y."""
    mb = W.MB(name)
    mb.disc_y(0, .06 * s, 0, .55 * s, .12 * s, "eye_w", n=18)
    mb.disc_y(0, -.06 * s, 0, .3 * s, .03 * s, "eye_iris", n=16)
    mb.disc_y(0, -.09 * s, 0, .14 * s, .03 * s, "eye_pupil", n=12)
    mb.disc_y(.1 * s, -.12 * s, .1 * s, .05 * s, .02 * s, "eye_w", n=8)
    return mb.build(loc)


def view_cube(name, s=1.0, loc=(0, 0, 0), label="1.000"):
    """kubus '1.000 views' biru dengan ikon mata di depan + teks."""
    mb = W.MB(name)
    L.rbox(mb, -.9 * s, -.9 * s, 0, .9 * s, .9 * s, 1.8 * s, "view_cube", c=.18 * s)
    mb.box(-.82 * s, -.82 * s, 1.8 * s, .82 * s, .82 * s, 1.84 * s, "view_cube2")
    mb.disc_y(0, -.9 * s, 1.15 * s, .38 * s, .04 * s, "eye_w", n=16)
    mb.disc_y(0, -.93 * s, 1.15 * s, .2 * s, .02 * s, "eye_iris", n=12)
    mb.disc_y(0, -.95 * s, 1.15 * s, .09 * s, .02 * s, "eye_pupil", n=8)
    ob = mb.build(loc)
    if label:
        t = H.text(name + "_t", label, .42 * s, "play_w", depth=.03 * s, loc=(0, -.93 * s, .25 * s))
        t.parent = ob
    return ob


def coin(name, s=1.0, loc=(0, 0, 0)):
    mb = W.MB(name)
    mb.disc_y(0, .06 * s, 0, .5 * s, .12 * s, "coin", n=18)
    mb.disc_y(0, -.06 * s, 0, .36 * s, .02 * s, "coin2", n=16)
    ob = mb.build(loc)
    t = H.text(name + "_t", "Rp", .32 * s, "coin", depth=.02 * s, loc=(0, -.09 * s, -.13 * s))
    t.parent = ob
    return ob


def money_machine(name, s=1.0):
    """mesin monetisasi: corong masuk (kiri, menerima 'perhatian'), badan bergaris lampu, corong keluar
    (kanan) mengeluarkan uang. Menghadap -Y. Return dict(body, in_pt, out_pt, lights)."""
    mb = W.MB(name)
    L.rbox(mb, -2.2 * s, -1.4 * s, 0, 2.2 * s, 1.4 * s, 3.2 * s, "mach", c=.3 * s)
    L.rbox(mb, -2.0 * s, -1.45 * s, .3 * s, 2.0 * s, -1.38 * s, 2.9 * s, "mach2", c=.2 * s)
    mb.cyl(-1.2 * s, 0, 3.2 * s, 4.6 * s, .7 * s, "mach2", n=12, r_top=1.25 * s)                   # corong
    mb.cyl(-1.2 * s, 0, 4.55 * s, 4.7 * s, 1.3 * s, "st_metal", n=12)
    mb.prism_x([(-.8 * s, .3 * s), (.8 * s, .3 * s), (.8 * s, 1.6 * s), (-.8 * s, 1.6 * s)], 2.2 * s, 3.6 * s, "mach2")
    mb.box(2.2 * s, -.9 * s, .2 * s, 3.8 * s, .9 * s, .32 * s, "st_metal")                        # nampan keluar
    for k in range(3):                                                                            # roda gigi dekor
        mb.disc_y((-1.2 + k * 1.2) * s, -1.48 * s, 1.0 * s, .32 * s, .05 * s, "st_metal", n=8)
    ob = mb.build()
    lm = W.MB(name + "_lamp")
    for k in range(5):
        lm.box((-1.6 + k * .8) * s - .18 * s, -1.5 * s, 2.3 * s, (-1.6 + k * .8) * s + .18 * s, -1.46 * s, 2.55 * s,
               "mach_acc")
    lo = lm.build()
    lo.data.materials[0] = lp.mat("mach_acc", emission=3)
    lo.parent = ob
    return {"body": ob, "lamps": lo, "in": (-1.2 * s, 0, 5.2 * s), "out": (3.2 * s, 0, .6 * s)}


def sponsor_box(name, key_="sp_a", s=1.0, label="SPONSOR"):
    """kotak produk sponsor generik (garis warna + label)."""
    mb = W.MB(name)
    L.rbox(mb, -.9 * s, -.6 * s, 0, .9 * s, .6 * s, 2.0 * s, "c_white", c=.1 * s)
    mb.box(-.92 * s, -.62 * s, .5 * s, .92 * s, .62 * s, 1.3 * s, key_)
    mb.box(-.92 * s, -.62 * s, 1.75 * s, .92 * s, .62 * s, 1.85 * s, key_)
    ob = mb.build()
    t = H.text(name + "_t", label, .26 * s, "play_w", depth=.02 * s, loc=(0, -.64 * s, .78 * s))
    t.parent = ob
    return ob


def member_card(name, s=1.0, key_="gold"):
    """kartu member (berdiri menghadap -Y): kartu emas + chip + garis + tulisan MEMBER."""
    mb = W.MB(name)
    L.rbox(mb, -1.6 * s, -.06 * s, 0, 1.6 * s, .06 * s, 2.0 * s, key_, c=.18 * s)
    mb.box(-1.25 * s, -.08 * s, 1.0 * s, -.65 * s, -.06 * s, 1.45 * s, "silver")
    mb.box(-1.4 * s, -.08 * s, .3 * s, .6 * s, -.06 * s, .4 * s, "gold2")
    mb.box(-1.4 * s, -.08 * s, .5 * s, .2 * s, -.06 * s, .58 * s, "gold2")
    ob = mb.build()
    t = H.text(name + "_t", "MEMBER", .32 * s, "st_chair", depth=.02 * s, loc=(.55 * s, -.09 * s, 1.55 * s))
    t.parent = ob
    return ob


def crowd(name, n, x0, y0, x1, y1, seed=3, s=1.0, card_frac=0.0):
    """kerumunan penonton mini merata di persegi (satu objek)."""
    rnd = random.Random(seed)
    mb = W.MB(name)
    shirts = ("c_coral", "c_mint", "c_sky", "c_mustard", "c_lilac", "c_white", "c_navy", "c_pink", "c_olive", "c_brick")
    cols = max(1, int(round(math.sqrt(n * (x1 - x0) / max(.1, (y1 - y0))))))
    rows = max(1, int(math.ceil(n / cols)))
    for k in range(n):
        c, r = k % cols, k // cols
        x = x0 + (c + .5) * (x1 - x0) / cols + rnd.uniform(-.15, .15)
        y = y0 + (r + .5) * (y1 - y0) / rows + rnd.uniform(-.15, .15)
        mini_person(mb, x, y, 0, s * rnd.uniform(.9, 1.1), rnd.choice(shirts), rnd.choice(("skin1", "skin2", "skin3")),
                    rnd.choice(("hair_blk", "hair_brn", "hair_dk", "hij_cream", "hij_navy")), rnd.random() < card_frac)
    return mb.build()


# ------------------------------------------------------------------ ikon biaya
def cost_icon(name, kind, s=1.0):
    """ikon 3D kecil: host (kursi kulit + mic), tamu (kursi + bintang), transport (van), studio (gedung
    mini berpintu), alat (kamera tripod), marketing (megafon). Berdiri di atas z=0."""
    mb = W.MB(name)
    if kind == "host":
        armchair(mb, 0, 0, (0, 1))
        mb.box(-.06, -.95, 0, .06, -.83, 1.2, "st_metal_dk")
        mb.cyl(0, -.89, 1.2, 1.6, .12, "mic", n=10)
    elif kind == "tamu":
        armchair(mb, 0, 0, (0, 1), "c_wine")
        pts = []
        for k in range(10):
            a = math.pi / 2 + k * math.pi / 5
            r = .55 if k % 2 == 0 else .23
            pts.append((math.cos(a) * r, 2.45 + math.sin(a) * r))
        mb.prism_y(pts, -.08, .08, "gold")
    elif kind == "transport":
        L.rbox(mb, -1.4, -.75, .3, 1.4, .75, 1.75, "c_white", c=.15)
        mb.box(.75, -.78, 1.0, 1.42, .78, 1.6, "ct_glass3")
        mb.box(-1.2, -.78, 1.05, .5, -.76, 1.55, "ct_glass3")
        mb.box(-1.42, -.77, .7, 1.42, -.75, .85, "yt_red")
        for sx in (-.85, .85):
            for sy in (-.7, .7):
                mb.disc_y(sx, sy + .1, .32, .3, .2, "tire", n=10)
    elif kind == "studio":
        mb.box(-1.1, -.9, 0, 1.1, .9, 2.2, "hq_glass")
        mb.box(-1.2, -1.0, 2.2, 1.2, 1.0, 2.4, "hq_frame")
        mb.box(-.45, -.95, 0, .45, -.9, 1.3, "warm")
        mb.box(-.55, -.97, 1.3, .55, -.9, 1.42, "door_frame")
    elif kind == "alat":
        for k in range(3):
            a = 2 * math.pi * k / 3 + .3
            T.beam(mb, (math.cos(a) * .5, math.sin(a) * .5, 0), (0, 0, 1.3), .05, "st_metal_dk")
        L.rbox(mb, -.3, -.45, 1.3, .3, .35, 1.85, "cam_body", c=.06)
        mb.disc_y(0, -.45, 1.57, .2, .3, "cam_lens", n=12)
        mb.box(-.05, -.47, 1.78, .05, -.43, 1.84, "tally")
    elif kind == "marketing":
        mb.cyl(0, 0, .0, 1.2, .1, "st_metal_dk", n=8)
        T.beam(mb, (0, 0, 1.2), (0, -.3, 1.5), .12, "st_metal_dk")
        verts, faces = [], []
        n = 12
        for i in range(n):
            a = 2 * math.pi * i / n
            verts.append((math.cos(a) * .22, -.3, 1.6 + math.sin(a) * .22))
        for i in range(n):
            a = 2 * math.pi * i / n
            verts.append((math.cos(a) * .7, -1.4, 1.75 + math.sin(a) * .7))
        faces = [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)] + [list(range(n - 1, -1, -1))]
        mb.poly(verts, faces, "yt_red")
        mb.cyl(0, -.2, 1.38, 1.82, .26, "c_white", n=10)
    return mb.build()


def stamp(name, body="SIMULASI", s=1.0, key_="stamp"):
    """cap merah bertulisan (berdiri, menghadap -Y): bingkai persegi + teks."""
    w = .52 * s * len(body) + .8 * s
    mb = W.MB(name)
    t_ = .14 * s
    for (a, b, c, d) in ((-w / 2, 0, w / 2, t_), (-w / 2, 1.3 * s - t_, w / 2, 1.3 * s), (-w / 2, 0, -w / 2 + t_, 1.3 * s),
                         (w / 2 - t_, 0, w / 2, 1.3 * s)):
        mb.box(a, -.05 * s, b, c, .0, d, key_)
    ob = mb.build()
    t = H.text(name + "_t", body, .62 * s, key_, depth=.05 * s, loc=(0, -.03 * s, .33 * s))
    t.parent = ob
    return ob


def bar3d(name, h, loc, w=1.4, key_="chart_b"):
    mb = W.MB(name)
    L.rbox(mb, -w / 2, -w / 2, 0, w / 2, w / 2, h, key_, c=.12)
    return mb.build(loc)


def arrow_up(name, s=1.0, key_="chart_g"):
    mb = W.MB(name)
    mb.prism_y([(-.35 * s, 0), (.35 * s, 0), (.35 * s, 1.6 * s), (.85 * s, 1.6 * s), (0, 2.6 * s), (-.85 * s, 1.6 * s),
                (-.35 * s, 1.6 * s)], -.15 * s, .15 * s, key_)
    ob = mb.build()
    ob.data.materials[0] = lp.mat(key_, emission=.6)
    return ob


def setup_city_light():
    """matahari sore sedikit hangat untuk adegan kota."""
    sun = bpy.data.objects.get("sun")
    sun.data.energy = 3.4
    sun.data.color = (1.0, .95, .88)
    sun.rotation_euler = (math.radians(48), 0, math.radians(-50))
