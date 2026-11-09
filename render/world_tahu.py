"""Aset & dunia diorama untuk video "Distribusi Tahu Kuning".

Memakai toolkit world.py (MB, jalan, bangunan, props) dengan isi baru:
pabrik tahu kuning di blok tengah, deret rumah pelanggan (kompleks) di selatan,
tukang tahu (topi hijau zaitun, kaos putih + lengan panjang marun, jeans, tas selempang)
dengan motor ber-boks toska + ember biru, tahu kuning, bungkus isi 10, tampah bambu.
"""
import math
import random

import bpy

import lowpoly as lp
import world as W

lp.PAL.update({
    "tahu": "#F4C21F",
    "tahu_dk": "#DDA810",
    "tahu_lt": "#FFD84A",
    "cap": "#5B6142",
    "tee": "#F2F2EE",
    "sleeve": "#8A4A55",
    "jeans": "#2C3E66",
    "shoe_blk": "#26262A",
    "strap": "#2A2A2A",
    "skin_tan": "#C68E62",
    "bike_or": "#E8792B",
    "bike_blk": "#2E3036",
    "bike_sil": "#B8BEC6",
    "box_teal": "#2FA79A",
    "box_teal2": "#258C81",
    "bucket": "#2B6CB0",
    "factory": "#ECE6D8",
    "factory2": "#D9CDB4",
    "zinc": "#9AA6AE",
    "zinc2": "#87939B",
    "rolldoor": "#A7B0B8",
    "crate": "#3D8FD1",
    "drum": "#4E7FB0",
    "tank": "#3C7DC4",
    "steam": "#FFFFFF",
    "bamboo": "#B98552",
    "bamboo2": "#9C6C3F",
    "paper": "#EDE6D6",
    "plastic": "#F7FBFF",
    "coin": "#E8B83A",
    "coin_dk": "#C99A22",
    "money": "#4CC46C",
    "money_dk": "#36A055",
    "pin": "#4CC46C",
    "pin_red": "#E2534A",
    "fence": "#F4F1EA",
    "hijab": "#D98CA8",
    "grey_bad": "#9A9A8C",
})

Z = W.Z_LAWN


def beam(mb, p0, p1, t, key):
    """balok persegi (tebal t) dari titik p0 ke p1."""
    from mathutils import Vector
    a, b = Vector(p0), Vector(p1)
    d = (b - a).normalized()
    up = Vector((0, 0, 1)) if abs(d.z) < .9 else Vector((1, 0, 0))
    u = d.cross(up).normalized() * t / 2
    v = d.cross(u).normalized() * t / 2
    vs = [tuple(p + du + dv) for p in (a, b) for du, dv in ((u, v), (-u, v), (-u, -v), (u, -v))]
    mb.poly(vs, [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], key)


def clear_plastic():
    m = lp.mat("plastic")
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Alpha"].default_value = .14
    b.inputs["Roughness"].default_value = .25
    return m


# ------------------------------------------------------------------ tahu
def tofu(mb, x, y, z, s, key="tahu"):
    """satu potong tahu kuning (asal: tengah bawah)."""
    h = .72 * s
    mb.box(x - s / 2, y - s / 2, z, x + s / 2, y + s / 2, z + h, key)
    # garis tekstur kain di atas & samping
    for i in range(3):
        u = -s * .3 + i * s * .3
        mb.box(x - s * .44, y + u - s * .025, z + h, x + s * .44, y + u + s * .025, z + h + s * .025, "tahu_dk")
    mb.box(x - s * .46, y - s / 2 - s * .02, z + h * .45, x + s * .46, y - s / 2, z + h * .5, "tahu_dk")


def tofu_pack(name, s=.16, key="tahu", contents=True, shell=True):
    """bungkus plastik bening isi 10 tahu (5x2). Asal: tengah bawah. Lebar ≈ 5.2*s.
    contents/shell: bisa dibuat terpisah untuk animasi (tahu dulu, plastik menyusul)."""
    clear_plastic()
    mb = W.MB(name)
    g = s * 1.0
    if contents:
        for i in range(5):
            for j in range(2):
                tofu(mb, (i - 2) * g, (j - .5) * g, .01 * s, s * .97, key)
    if shell:
        top = .74 * s
        bw, bd, zt = 2.62 * g, 1.12 * g, top + .06 * s
        t = .05 * s
        for sx in (-1, 1):
            for sy in (-1, 1):
                beam(mb, (sx * bw, sy * bd, 0), (sx * bw, sy * bd, zt), t, "tee")
                beam(mb, (sx * bw, sy * bd, zt), (sx * .2 * s, sy * .12 * s, top + .75 * s), t, "tee")
        for sy in (-1, 1):
            beam(mb, (-bw, sy * bd, zt), (bw, sy * bd, zt), t, "tee")
        for sx in (-1, 1):
            beam(mb, (sx * bw, -bd, zt), (sx * bw, bd, zt), t, "tee")
        mb.poly([(-bw, -bd, zt), (bw, -bd, zt), (bw, bd, zt), (-bw, bd, zt),
                 (-.2 * s, -.12 * s, top + .75 * s), (.2 * s, -.12 * s, top + .75 * s), (.2 * s, .12 * s, top + .75 * s),
                 (-.2 * s, .12 * s, top + .75 * s)],
                [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], "plastic")
        mb.sphere(0, 0, top + .85 * s, .16 * s, "tee", sz=.2 * s)
        mb.sphere(-.22 * s, 0, top + 1.05 * s, .13 * s, "tee")
        mb.sphere(.22 * s, 0, top + 1.05 * s, .13 * s, "tee")
    return mb


def tofu_obj(name, s, key="tahu"):
    mb = W.MB(name)
    tofu(mb, 0, 0, 0, s, key)
    return mb


def tampah(mb, cx, cy, z, r):
    """tampah / nampan bambu dengan alas kertas."""
    mb.cyl(cx, cy, z, z + .12 * r, r, "bamboo2", n=24)
    mb.cyl(cx, cy, z + .12 * r, z + .14 * r, r * .93, "paper", n=24)
    for k in range(24):
        a = 2 * math.pi * k / 24
        a2 = 2 * math.pi * (k + 1) / 24
        vs = [(cx + r * math.cos(a), cy + r * math.sin(a), z), (cx + r * math.cos(a2), cy + r * math.sin(a2), z),
              (cx + r * 1.03 * math.cos(a2), cy + r * 1.03 * math.sin(a2), z + .28 * r),
              (cx + r * 1.03 * math.cos(a), cy + r * 1.03 * math.sin(a), z + .28 * r)]
        mb.poly(vs, [(0, 1, 2, 3)], "bamboo" if k % 2 else "bamboo2")
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        mb.boxc(cx + r * 1.02 * math.cos(a), cy + r * 1.02 * math.sin(a), z + .08 * r, .1 * r, .1 * r, .2 * r, "paper")


# ------------------------------------------------------------------ karakter
def seller(name, pose="stand", tee="tee", sleeve="sleeve"):
    """tukang tahu ±1.75 m, asal di kaki, menghadap -Y.
    pose: stand | give (tangan ke depan) | phone (satu tangan pegang HP) | wave | cheer"""
    mb = W.MB(name)
    mb.box(-.25, -.15, 0, -.03, .17, .1, "shoe_blk")
    mb.box(.03, -.15, 0, .25, .17, .1, "shoe_blk")
    mb.box(-.24, -.13, .1, -.03, .13, .88, "jeans")
    mb.box(.03, -.13, .1, .24, .13, .88, "jeans")
    mb.box(-.31, -.19, .86, .31, .19, 1.47, tee)
    # lengan pendek kaos + lengan panjang marun di dalam
    for sx in (-1, 1):
        mb.box(sx * .31, -.12, 1.25, sx * .43, .12, 1.46, tee)
    if pose in ("give", "phone"):
        mb.box(-.43, -.72, 1.12, -.31, -.04, 1.3, sleeve)
        mb.sphere(-.37, -.76, 1.2, .07, "skin_tan")
        if pose == "give":
            mb.box(.31, -.72, 1.12, .43, -.04, 1.3, sleeve)
            mb.sphere(.37, -.76, 1.2, .07, "skin_tan")
        else:
            mb.box(.31, -.08, .82, .43, .08, 1.27, sleeve)
            mb.box(-.48, -.82, 1.18, -.28, -.78, 1.45, "bike_blk")      # HP
            mb.box(-.46, -.83, 1.21, -.30, -.82, 1.42, "glass2")
    elif pose == "wave":
        mb.box(-.43, -.08, .82, -.31, .08, 1.27, sleeve)
        mb.box(.31, -.08, 1.3, .43, .08, 2.05, sleeve)
        mb.sphere(.37, 0, 2.1, .08, "skin_tan")
    elif pose == "cheer":
        for sx in (-1, 1):
            mb.box(sx * .31, -.08, 1.3, sx * .43, .08, 2.05, sleeve)
            mb.sphere(sx * .37, 0, 2.1, .08, "skin_tan")
    else:
        for sx in (-1, 1):
            mb.box(sx * .31, -.08, .82, sx * .43, .08, 1.27, sleeve)
            mb.sphere(sx * .37, 0, .78, .07, "skin_tan")
    # tas selempang: tali diagonal + tas di pinggang kanan
    beam(mb, (-.21, -.2, 1.47), (.27, -.2, .97), .07, "strap")
    beam(mb, (-.21, .2, 1.47), (.27, .2, .97), .07, "strap")
    mb.box(.24, -.2, .78, .36, .14, 1.02, "strap")
    mb.box(-.06, -.17, 1.44, .06, .17, 1.5, "sleeve")  # kerah
    mb.sphere(0, 0, 1.68, .23, "skin_tan")
    # topi hijau zaitun + lidah topi ke depan
    mb.cyl(0, 0, 1.78, 1.97, .25, "cap", n=10, r_top=.2)
    mb.box(-.2, -.42, 1.79, .2, -.12, 1.83, "cap")
    return mb


def customer(name, shirt, hijab=False, give=False):
    mb = W.MB(name)
    mb.box(-.25, -.14, 0, -.03, .14, .85, "pants")
    mb.box(.03, -.14, 0, .25, .14, .85, "pants")
    mb.box(-.3, -.18, .85, .3, .18, 1.45, shirt)
    if give:
        for sx in (-1, 1):
            mb.box(sx * .42 - .06, -.7, 1.12, sx * .42 + .06, -.05, 1.3, shirt)
    else:
        for sx in (-1, 1):
            mb.box(sx * .36 - .06, -.1, .8, sx * .36 + .06, .1, 1.42, shirt)
    mb.sphere(0, 0, 1.68, .24, "skin")
    if hijab:
        mb.sphere(0, .03, 1.72, .29, "hijab", sz=.3)
        mb.box(-.32, -.2, 1.3, .32, .22, 1.55, "hijab")
        mb.box(-.17, -.3, 1.6, .17, -.2, 1.78, "skin")
    else:
        mb.box(-.22, -.05, 1.8, .22, .24, 1.95, "door")
    return mb


def tahu_bike(name, scale=1.25, rider=True, tee="tee", sleeve="sleeve"):
    """motor tukang tahu: 2 boks toska di samping belakang + ember biru di atas. Menghadap +X."""
    root = bpy.data.objects.new(name, None)
    lp._link(root)
    mb = W.MB(name + "_m")
    # roda
    for x in (-.72, .72):
        mb.disc_y(x, .07, .3, .3, .14, "tire", n=12)
        mb.disc_y(x, .075, .3, .14, .15, "bike_sil", n=10)
    # bodi motor bebek / matic
    mb.box(-.9, -.17, .45, .35, .17, .78, "bike_or")
    mb.box(-.95, -.18, .7, -.1, .18, .9, "bike_blk")          # jok
    mb.box(.25, -.16, .3, .62, .16, 1.05, "bike_or")           # tameng depan
    mb.box(.5, -.12, .95, .72, .12, 1.25, "bike_blk")          # kepala
    mb.box(.62, -.42, 1.18, .7, .42, 1.24, "bike_sil")         # setang
    mb.box(.7, -.08, 1.0, .76, .08, 1.12, "frame")             # lampu
    mb.box(-.95, -.2, .25, -.35, -.17, .45, "bike_sil")        # knalpot
    # rak + boks toska kiri-kanan
    mb.box(-1.25, -.25, .88, -.45, .25, .93, "bike_blk")
    for sy in (-1, 1):
        y0, y1 = sorted((sy * .26, sy * .78))
        mb.box(-1.4, y0, .3, -.35, y1, 1.08, "box_teal")
        mb.box(-1.43, y0 - .02, 1.02, -.32, y1 + .02, 1.12, "box_teal2")
    # ember biru di atas
    mb.cyl(-.9, 0, .93, 1.45, .3, "bucket", n=12, r_top=.36)
    mb.cyl(-.9, 0, 1.45, 1.48, .37, "bucket", n=12)
    mb.box(-1.0, -.06, 1.47, -.6, .06, 1.53, "bamboo2")
    if rider:
        mb.box(-.3, -.26, .85, .15, .26, 1.0, "jeans")                     # paha
        for sy in (-.15, .15):
            mb.box(.05, sy - .1, .42, .2, sy + .1, .95, "jeans")           # betis
            mb.box(.05, sy - .1, .38, .32, sy + .1, .46, "shoe_blk")
        mb.box(-.42, -.3, .95, .05, .3, 1.6, tee)
        beam(mb, (.06, -.31, 1.55), (.06, .31, 1.05), .07, "strap")
        for sy in (-1, 1):
            beam(mb, (-.17, sy * .36, 1.48), (.6, sy * .4, 1.22), .13, sleeve)
            mb.box(-.3, sy * .3 - .08, 1.36, -.04, sy * .3 + .08, 1.58, tee)
        mb.sphere(-.17, 0, 1.82, .23, "skin_tan")
        mb.cyl(-.17, 0, 1.92, 2.1, .25, "cap", n=10, r_top=.2)
        mb.box(-.05, -.2, 1.93, .25, .2, 1.97, "cap")
    ob = mb.build()
    ob.parent = root
    ob.scale = (scale,) * 3
    return root


# ------------------------------------------------------------------ bangunan
def factory(name, w=22, d=15):
    """pabrik tahu kuning: aula beratap seng, pintu gulung, papan nama kuning bergambar tahu."""
    mb = W.MB(name)
    h = Z + 6.2
    mb.box(-w / 2, -d / 2, Z, w / 2, d / 2, h, "factory")
    mb.box(-w / 2 - .05, -d / 2 - .05, Z, w / 2 + .05, d / 2 + .05, Z + 1.0, "factory2")
    # jendela tinggi (ventilasi)
    for i in range(7):
        x = -w / 2 + 1.8 + i * (w - 3.6) / 6
        for y, s in ((-d / 2, -1), (d / 2, 1)):
            mb.box(x - .7, y + s * .02, h - 2.2, x + .7, y + s * .12, h - 1.2, "glass2")
    for i in range(4):
        y = -d / 2 + 2.2 + i * (d - 4.4) / 3
        for x, s in ((-w / 2, -1), (w / 2, 1)):
            mb.box(x + s * .02, y - .7, h - 2.2, x + s * .12, y + .7, h - 1.2, "glass2")
    # pintu gulung besar + pintu kecil
    mb.box(-3.2, -d / 2 - .15, Z, 3.2, -d / 2 + .02, Z + 4.0, "bike_sil")
    mb.box(-3.0, -d / 2 - .2, Z, 3.0, -d / 2 - .1, Z + 3.85, "rolldoor")
    for k in range(9):
        mb.box(-3.0, -d / 2 - .24, Z + .3 + k * .4, 3.0, -d / 2 - .18, Z + .36 + k * .4, "zinc2")
    mb.box(6.0, -d / 2 - .12, Z, 7.4, -d / 2 + .02, Z + 2.4, "door")
    mb.box(-8.5, -d / 2 - .12, Z + 1.4, -5.5, -d / 2 + .02, Z + 3.0, "frame")
    mb.box(-8.3, -d / 2 - .16, Z + 1.55, -5.7, -d / 2 - .08, Z + 2.85, "glass2")
    # kanopi di atas pintu
    W.awning(mb, -4.2, 4.2, -d / 2, Z + 4.6, 2.2, "zinc2")
    # atap pelana seng
    W.gable(mb, w, d, h, 3.4, "zinc", "factory", o=.8)
    for i in range(12):
        x = -w / 2 - .8 + i * (w + 1.6) / 11
        mb.prism_x([(-d / 2 - .85, h - .2), (0, h + 3.45), (d / 2 + .85, h - .2)], x - .05, x + .05, "zinc2")
    # papan nama kuning dengan ikon tahu
    bz = Z + 4.4
    mb.box(-4.6, -d / 2 - .45, bz + 1.2, 4.6, -d / 2 - .2, bz + 3.9, "yellow")
    mb.box(-4.4, -d / 2 - .52, bz + 1.4, 4.4, -d / 2 - .44, bz + 3.7, "tee")
    for i in range(3):
        tx = -2.2 + i * 2.2
        mb.box(tx - .8, -d / 2 - .7, bz + 1.85, tx + .8, -d / 2 - .52, bz + 3.25, "tahu")
        for k in range(3):
            mb.box(tx - .72, -d / 2 - .74, bz + 2.15 + k * .38, tx + .72, -d / 2 - .69, bz + 2.2 + k * .38, "tahu_dk")
    return mb, (0, -d / 2 - .5, bz + 3.9)


def factory_yard(mb, cx, cy, w, d):
    """cerobong, tandon air, tumpukan krat & drum di sekitar pabrik (koordinat dunia)."""
    chx, chy = cx + w / 2 - 3.5, cy + d / 2 - 3.0
    mb.cyl(chx, chy, Z, Z + 14.5, .9, "brick3", n=10, r_top=.75)
    mb.cyl(chx, chy, Z + 14.5, Z + 15.0, .9, "bike_blk", n=10)
    # tandon air di atas menara kaki empat
    tx, ty = cx - w / 2 - 2.6, cy + d / 2 - 2.5
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box(tx + sx * 1.0 - .1, ty + sy * 1.0 - .1, Z, tx + sx * 1.0 + .1, ty + sy * 1.0 + .1, Z + 5.0, "metal")
    mb.box(tx - 1.3, ty - 1.3, Z + 5.0, tx + 1.3, ty + 1.3, Z + 5.2, "metal")
    mb.cyl(tx, ty, Z + 5.2, Z + 7.6, 1.3, "tank", n=14)
    mb.cyl(tx, ty, Z + 7.6, Z + 8.1, 1.3, "tank", n=14, r_top=.3)
    # krat biru bertumpuk & drum di halaman depan
    for (bx, by, n) in ((cx - w / 2 + 1.0, cy - d / 2 - 1.6, 3), (cx + w / 2 - 1.0, cy - d / 2 - 1.6, 2)):
        for k in range(n):
            mb.boxc(bx, by, Z + k * .62, 1.1, .8, .58, "crate")
            mb.boxc(bx, by - .41, Z + k * .62 + .38, .7, .03, .12, "bike_blk")
    for k in range(3):
        mb.cyl(cx + w / 2 - 2.6 - k * 1.0, cy - d / 2 - 1.5, Z, Z + 1.1, .42, "drum", n=10)
    return (chx, chy, Z + 15.0)


def fence(mb, x0, x1, y, gaps=()):
    x = x0
    while x < x1:
        if not any(abs(x - g) < 1.1 for g in gaps):
            mb.box(x - .07, y - .07, Z, x + .07, y + .07, Z + 1.0, "fence")
        x += .55
    segs = [x0] + [v for g in gaps for v in (g - 1.0, g + 1.0)] + [x1]
    for a, b in zip(segs[::2], segs[1::2]):
        mb.box(a, y - .05, Z + .65, b, y + .05, Z + .78, "fence")


def house(name, w, d, rnd, wall=None, roof=None):
    """rumah tapak kompleks: 1 lantai, atap pelana, teras kecil."""
    mb = W.MB(name)
    wall = wall or rnd.choice(["wall_cream2", "wall_beige", "wall_peach", "laundry_wall"])
    h = Z + 3.5
    mb.box(-w / 2, -d / 2, Z, w / 2, d / 2, h, wall)
    W.windows(mb, w, d, Z + .1, 1, fh=3.3, skip_front_ground=True)
    mb.box(-.75, -d / 2 - .12, Z, .75, -d / 2 + .02, Z + 2.3, "door")
    for sx in (-1, 1):
        mb.box(sx * 2.4 - .6, -d / 2 - .12, Z + 1.0, sx * 2.4 + .6, -d / 2 + .02, Z + 2.3, "frame")
        mb.box(sx * 2.4 - .5, -d / 2 - .16, Z + 1.1, sx * 2.4 + .5, -d / 2 - .08, Z + 2.2, "glass2")
    mb.box(-w / 2 + .3, -d / 2 - 1.6, Z, w / 2 - .3, -d / 2, Z + .18, "sidewalk")   # teras
    W.gable(mb, w, d, h, min(w, d) * .5, roof or rnd.choice(["roof_orange", "roof_brown", "roof_orange"]), wall)
    return mb, h + min(w, d) * .5


# ------------------------------------------------------------------ dunia
FACTORY_C = (0.0, -6.0)
FACTORY_WD = (22.0, 15.0)
STREET_Y = -24.0           # jalan depan pabrik & kompleks
HOME_Y = -38.5             # deret rumah pelanggan di selatan jalan
HOME_XS = (-10.6, 0.0, 10.6)


def road_point(cx, cy, facing):
    """titik di jalan depan bangunan (None jika menghadap tepi tile)."""
    if facing in ("+y", "-y"):
        cands = [r for r in W.ROADS if (r > cy if facing == "+y" else r < cy)]
        if not cands:
            return None
        r = min(cands) if facing == "+y" else max(cands)
        return (cx, r)
    cands = [r for r in W.ROADS if (r > cx if facing == "+x" else r < cx)]
    if not cands:
        return None
    r = min(cands) if facing == "+x" else max(cands)
    return (r, cy)


def _on(p):
    """garis jalan tempat p berada: ('h', y) atau ('v', x)."""
    if any(abs(p[1] - r) < .01 for r in W.ROADS):
        return ("h", p[1])
    return ("v", p[0])


def route(a, b):
    """rute manhattan di jaringan jalan (2 jalan x & 2 jalan y)."""
    la, lb = _on(a), _on(b)
    if la == lb:
        return [a, b]
    if la[0] != lb[0]:
        c = (lb[1], la[1]) if la[0] == "h" else (la[1], lb[1])
        return [a, c, b]
    best = None
    for r in W.ROADS:                       # dua garis sejajar: lewat jalan tegak lurus
        pts = [a, (r, a[1]), (r, b[1]), b] if la[0] == "h" else [a, (a[0], r), (b[0], r), b]
        L = lp.path_length(pts)
        if best is None or L < best[0]:
            best = (L, pts)
    return best[1]


def build_world(seed=5, people=True):
    rnd = random.Random(seed)
    info = {"anchors": {}, "routes": {}, "customers": []}
    W.PLACED.clear()
    W.build_ground()
    props = W.MB("props")
    trees = W.MB("trees")

    # --- pabrik tahu di blok tengah
    mb, top = factory("factory", *FACTORY_WD)
    mb.build((*FACTORY_C, 0), 0)
    info["anchors"]["PABRIK"] = W.local_to_world(top, (*FACTORY_C, 0), "-y")
    info["anchors"]["PABRIK_FRONT"] = (FACTORY_C[0] - 5.5, -16.5, 6.0)
    info["chimney"] = factory_yard(props, *FACTORY_C, *FACTORY_WD)
    info["factory_door"] = (FACTORY_C[0], FACTORY_C[1] - FACTORY_WD[1] / 2 - 1.0)
    for x in (-13.5, 13.5):
        W.tree_round(trees, x, 9, 1.0, rnd)
    for x in (-13.5, 13.5):
        W.lamp(props, x, -17.5)

    # --- deret rumah pelanggan (kompleks) di selatan jalan
    reserved = [(-15.5, -15.5, 15.5, 15.5), (-16, HOME_Y - 6, 16, -29)]
    for i, x in enumerate(HOME_XS):
        mb, top = house(f"home{i}", 8.6, 8.0, rnd, wall=["wall_peach", "laundry_wall", "wall_cream2"][i],
                        roof=["roof_orange", "roof_brown", "roof_orange"][i])
        mb.build((x, HOME_Y, 0), W.FACING["+y"])
        info["anchors"][f"RUMAH{i + 1}"] = (x, HOME_Y, top)
    info["home_door"] = [(x, HOME_Y + 4.0 + 1.6) for x in HOME_XS]
    fence(props, -15.3, 15.3, -31.8, gaps=HOME_XS)
    for x in (-15.0, -5.3, 5.3, 15.0):
        W.tree_round(trees, x, -34.0, .7, rnd)
    for i, x in enumerate(HOME_XS):
        for dx in (-3.2, 3.2):
            trees.sphere(x + dx, -32.6, Z + .45, .55, "tree_m", sz=.5)

    # --- taman (blok barat-daya)
    pb = W.inner((-W.L, -W.L, W.ROADS[0] - W.RW / 2, W.ROADS[0] - W.RW / 2))
    reserved.append(pb)
    px, py = (pb[0] + pb[2]) / 2, (pb[1] + pb[3]) / 2
    props.box(pb[0] + 2, py - 1.2, Z, pb[2] - 2, py + 1.2, Z + .03, "path")
    props.box(px - 1.2, pb[1] + 2, Z, px + 1.2, pb[3] - 2, Z + .03, "path")
    for (bx, by, k, r90) in ((px - 8, py + 2.4, "teal", False), (px + 7, py - 2.4, "yellow", False),
                             (px + 2.6, py + 9, "teal", True), (px - 2.6, py - 8, "yellow", True)):
        W.bench(props, bx, by, k, r90)
    for q in range(26):
        x = rnd.uniform(pb[0] + 3, pb[2] - 3)
        y = rnd.uniform(pb[1] + 3, pb[3] - 3)
        if abs(x - px) < 3 or abs(y - py) < 3:
            continue
        if rnd.random() < .45:
            W.tree_conifer(trees, x, y, rnd.uniform(.8, 1.15))
        else:
            W.tree_round(trees, x, y, rnd.uniform(.8, 1.2), rnd)

    # --- kavling lain: dominan rumah tapak (kompleks)
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
                if k < .62:
                    ob, top = W.place(house("hs" + nm, w, d, rnd), cx, cy, facing)
                    rp = road_point(cx, cy, facing)
                    if rp:
                        info["customers"].append({"name": ob.name, "pos": (cx, cy, top), "road": rp})
                elif k < .85:
                    ob, top = W.place(W.townhouse("th" + nm, w, d, rnd.choice([2, 2, 3]), rnd), cx, cy, facing)
                    rp = road_point(cx, cy, facing)
                    if rp:
                        info["customers"].append({"name": ob.name, "pos": (cx, cy, top), "road": rp})
                else:
                    W.place(W.shophouse("sh" + nm, w, d, 2, rnd), cx, cy, facing)
                for (tx_, ty_) in ((rect[0] + 1.1, rect[1] + 1.1), (rect[2] - 1.1, rect[3] - 1.1)):
                    if rnd.random() < .55:
                        if rnd.random() < .35:
                            W.tree_conifer(trees, tx_, ty_, .6)
                        else:
                            W.tree_round(trees, tx_, ty_, .65, rnd)

    for r in W.ROADS:
        for t in range(-66, 67, 18):
            if all(abs(t - q) > 9 for q in W.ROADS):
                for off in (-W.RW / 2 - 1.2, W.RW / 2 + 1.2):
                    if not (abs(r + off + 30) < 2 and abs(t) < 17):
                        W.lamp(props, t, r + off)
                    W.lamp(props, r + off, t)
    props.build()
    trees.build()

    # rute dari depan pabrik ke tiap rumah pelanggan
    start = (FACTORY_C[0] + 2.5, STREET_Y)
    for cst in info["customers"]:
        cst["route"] = [(FACTORY_C[0] + 2.5, -16.5)] + route(start, cst["road"])

    info["people"] = []
    if people:
        prnd = random.Random(seed + 1)
        for k in range(18):
            r = prnd.choice(W.ROADS)
            off = prnd.choice((-W.RW / 2 - 1.7, W.RW / 2 + 1.7))
            horiz = prnd.random() < .5
            t0 = prnd.uniform(-60, 60)
            if any(abs(t0 - q) < 8 for q in W.ROADS) or (horiz and r < 0 and abs(t0) < 20):
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
    return info


def steam(name, base, n_frames, puffs=5, seed=1):
    """kepulan uap dari cerobong (bola putih naik, membesar, menghilang)."""
    rnd = random.Random(seed)
    for k in range(puffs):
        mb = W.MB(f"{name}{k}")
        mb.sphere(0, 0, 0, 1.0, "steam")
        ob = mb.build()
        period = 60
        off = k * period / puffs
        f = 1 - off
        while f < n_frames + period:
            f0 = f
            ob.location = (base[0], base[1], base[2])
            ob.scale = (.5,) * 3
            ob.keyframe_insert("location", frame=f0)
            ob.keyframe_insert("scale", frame=f0)
            ob.location = (base[0] + 3.0 + rnd.uniform(-.5, .5), base[1] + 1.5, base[2] + 6.5)
            ob.scale = (1.7,) * 3
            ob.keyframe_insert("location", frame=f0 + period - 1)
            ob.keyframe_insert("scale", frame=f0 + period - 1)
            ob.scale = (.001,) * 3
            ob.keyframe_insert("scale", frame=f0 + period - .5)
            f += period


def pin(name, color="pin"):
    """penanda lokasi (tetes terbalik). Asal di ujung bawah."""
    mb = W.MB(name)
    mb.cyl(0, 0, 0, 1.4, .03, color, n=10, r_top=.75)
    mb.sphere(0, 0, 1.65, .8, color)
    mb.sphere(0, -.55, 1.7, .32, "tee")
    return mb
