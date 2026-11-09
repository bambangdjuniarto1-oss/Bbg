"""Dunia diorama isometrik low-poly (gaya: potongan kota melayang dengan tepi tanah).

Semua bangunan dibuat di koordinat lokal dengan bagian depan menghadap -Y,
lalu diputar sesuai arah jalan. Satu bangunan = satu objek (multi-material).
"""
import math
import random

import bmesh
import bpy
from mathutils import Vector

import lowpoly as lp

lp.PAL.update({
    "sky": "#E2ECEE",
    "lawn": "#86BC4C",
    "lawn2": "#79B043",
    "soil": "#7B5136",
    "soil_top": "#6FA63F",
    "asphalt": "#4A4E57",
    "line": "#F2F2F2",
    "sidewalk": "#D3D6DA",
    "path": "#E6DCC4",
    "brick": "#A85440",
    "brick2": "#B8664C",
    "brick3": "#94503F",
    "roof_brown": "#86402F",
    "roof_orange": "#E07B45",
    "roof_slab": "#8E7C78",
    "roof_slab2": "#A8968C",
    "wall_beige": "#E2C7A0",
    "wall_cream2": "#EFDDBB",
    "wall_orange": "#E8954F",
    "wall_peach": "#F0B27A",
    "frame": "#F2E8D5",
    "glass2": "#4C6378",
    "door": "#6B4A35",
    "teal": "#3DB3A4",
    "yellow": "#F2C230",
    "green_aw": "#5DAE6B",
    "red_aw": "#D9534F",
    "tree_l": "#8CC152",
    "tree_m": "#6AAE45",
    "conifer": "#3E8E4F",
    "shop_roof": "#C9463D",
    "board_frame": "#8D99A3",
    "board": "#EEF2F5",
    "sneaker": "#8FB3DA",
    "sole": "#FFFFFF",
    "lace": "#2F4A6B",
    "laundry_wall": "#EAF2F4",
    "laundry_aw": "#3D8FD1",
    "machine": "#DDE3E8",
    "machine_door": "#5B7A99",
    "bench_wood": "#C9A27A",
    "metal": "#6D737B",
    "skin": "#E2B48C",
    "pants": "#3B4A63",
    "apron": "#2E6DB5",
    "wood": "#B98552",
    "shelf": "#D9C3A1",
    "dirt": "#8A6A4A",
    "umbrella": "#F4F4F4",
})

L = 72.0                       # setengah lebar tile
ROADS = (-24.0, 24.0)          # posisi jalan (x dan y)
RW = 10.0                      # lebar jalan
SW = 3.5                       # lebar trotoar
Z_LAWN = 0.32


# ------------------------------------------------------------------ mesh builder
_ICO = None


def _ico():
    global _ICO
    if _ICO is None:
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
        _ICO = ([tuple(v.co) for v in bm.verts], [[v.index for v in f.verts] for f in bm.faces])
        bm.free()
    return _ICO


class MB:
    def __init__(self, name):
        self.name, self.v, self.f, self.fm, self.mats, self.mi = name, [], [], [], [], {}

    def _m(self, key):
        if key not in self.mi:
            self.mi[key] = len(self.mats)
            self.mats.append(key)
        return self.mi[key]

    def poly(self, verts, faces, key):
        b = len(self.v)
        self.v += [tuple(v) for v in verts]
        m = self._m(key)
        for f in faces:
            self.f.append([b + i for i in f])
            self.fm.append(m)

    def box(self, x0, y0, z0, x1, y1, z1, key):
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        self.poly([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                   (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
                  [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], key)

    def boxc(self, cx, cy, z0, w, d, h, key):
        self.box(cx - w / 2, cy - d / 2, z0, cx + w / 2, cy + d / 2, z0 + h, key)

    def cyl(self, cx, cy, z0, z1, r, key, n=10, r_top=None):
        rt = r if r_top is None else r_top
        vs = []
        for i in range(n):
            a = 2 * math.pi * i / n
            vs.append((cx + r * math.cos(a), cy + r * math.sin(a), z0))
        for i in range(n):
            a = 2 * math.pi * i / n
            vs.append((cx + rt * math.cos(a), cy + rt * math.sin(a), z1))
        faces = [list(range(n - 1, -1, -1)), list(range(n, 2 * n))]
        faces += [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
        if rt == 0:
            vs = vs[:n] + [(cx, cy, z1)]
            faces = [list(range(n - 1, -1, -1))] + [(i, (i + 1) % n, n) for i in range(n)]
        self.poly(vs, faces, key)

    def disc_y(self, cx, y, cz, r, depth, key, n=14):
        """silinder dengan sumbu Y (mis. pintu mesin cuci)."""
        vs = [(cx + r * math.cos(2 * math.pi * i / n), y, cz + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
        vs += [(x, y - depth, z) for x, _, z in vs]
        faces = [list(range(n)), list(range(2 * n - 1, n - 1, -1))]
        faces += [(i, n + i, n + (i + 1) % n, (i + 1) % n) for i in range(n)]
        self.poly(vs, faces, key)

    def sphere(self, cx, cy, cz, r, key, sz=None):
        vs, fs = _ico()
        sz = sz or r
        self.poly([(cx + x * r, cy + y * r, cz + z * sz) for x, y, z in vs], fs, key)

    def prism_x(self, profile, x0, x1, key):
        """profil 2D (y,z) diekstrusi sepanjang X."""
        n = len(profile)
        vs = [(x0, y, z) for y, z in profile] + [(x1, y, z) for y, z in profile]
        faces = [list(range(n - 1, -1, -1)), list(range(n, 2 * n))]
        faces += [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
        self.poly(vs, faces, key)

    def prism_y(self, profile, y0, y1, key):
        """profil 2D (x,z) diekstrusi sepanjang Y."""
        n = len(profile)
        vs = [(x, y0, z) for x, z in profile] + [(x, y1, z) for x, z in profile]
        faces = [list(range(n)), list(range(2 * n - 1, n - 1, -1))]
        faces += [(i, n + i, n + (i + 1) % n, (i + 1) % n) for i in range(n)]
        self.poly(vs, faces, key)

    def build(self, loc=(0, 0, 0), rot_z=0.0, parent=None):
        me = bpy.data.meshes.new(self.name)
        me.from_pydata(self.v, [], self.f)
        for p, m in zip(me.polygons, self.fm):
            p.material_index = m
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(me)
        bm.free()
        for k in self.mats:
            me.materials.append(lp.mat(k))
        ob = bpy.data.objects.new(self.name, me)
        ob.location = loc
        ob.rotation_euler.z = rot_z
        if parent:
            ob.parent = parent
        return lp._link(ob)


FACING = {"-y": 0.0, "+x": math.pi / 2, "+y": math.pi, "-x": -math.pi / 2}


def local_to_world(p, loc, facing):
    a = FACING[facing]
    x, y, z = p
    return (loc[0] + x * math.cos(a) - y * math.sin(a), loc[1] + x * math.sin(a) + y * math.cos(a), loc[2] + z)


# ------------------------------------------------------------------ detail fasad
def windows(mb, w, d, z0, floors, fh=3.2, skip_front_ground=False, ww=1.25, wh=1.6):
    """jendela berbingkai di keempat sisi (bangunan lokal: x∈[-w/2,w/2], y∈[-d/2,d/2])."""
    for side in ("-y", "+y", "-x", "+x"):
        length = w if side in ("-y", "+y") else d
        n = max(1, int((length - 1.2) // 2.8))
        step = length / n
        for fl in range(floors):
            if fl == 0 and skip_front_ground and side == "-y":
                continue
            zc = z0 + fl * fh + fh * 0.55
            for i in range(n):
                u = -length / 2 + step * (i + .5)
                fw, fz = ww / 2 + .14, wh / 2 + .14
                if side == "-y":
                    mb.box(u - fw, -d / 2 - .1, zc - fz, u + fw, -d / 2 + .02, zc + fz, "frame")
                    mb.box(u - ww / 2, -d / 2 - .14, zc - wh / 2, u + ww / 2, -d / 2 - .08, zc + wh / 2, "glass2")
                elif side == "+y":
                    mb.box(u - fw, d / 2 - .02, zc - fz, u + fw, d / 2 + .1, zc + fz, "frame")
                    mb.box(u - ww / 2, d / 2 + .08, zc - wh / 2, u + ww / 2, d / 2 + .14, zc + wh / 2, "glass2")
                elif side == "-x":
                    mb.box(-w / 2 - .1, u - fw, zc - fz, -w / 2 + .02, u + fw, zc + fz, "frame")
                    mb.box(-w / 2 - .14, u - ww / 2, zc - wh / 2, -w / 2 - .08, u + ww / 2, zc + wh / 2, "glass2")
                else:
                    mb.box(w / 2 - .02, u - fw, zc - fz, w / 2 + .1, u + fw, zc + fz, "frame")
                    mb.box(w / 2 + .08, u - ww / 2, zc - wh / 2, w / 2 + .14, u + ww / 2, zc + wh / 2, "glass2")


def gable(mb, w, d, h, hr, roof, wall, o=.6):
    """atap pelana, bubungan sejajar sisi terpanjang."""
    if w >= d:
        mb.prism_x([(-d / 2 - o, h - .25), (d / 2 + o, h - .25), (0, h + hr)], -w / 2 - o, w / 2 + o, roof)
        mb.prism_x([(-d / 2, h), (d / 2, h), (0, h + hr * (d / 2) / (d / 2 + o))], -w / 2 + .05, w / 2 - .05, wall)
    else:
        mb.prism_y([(-w / 2 - o, h - .25), (w / 2 + o, h - .25), (0, h + hr)], -d / 2 - o, d / 2 + o, roof)
        mb.prism_y([(-w / 2, h), (w / 2, h), (0, h + hr * (w / 2) / (w / 2 + o))], -d / 2 + .05, d / 2 - .05, wall)


def awning(mb, x0, x1, y_front, z, depth, key):
    mb.prism_x([(y_front, z + .9), (y_front - depth, z), (y_front - depth, z - .45), (y_front - depth + .12, z - .45),
                (y_front - depth + .12, z - .05), (y_front, z + .78)], x0, x1, key)


# ------------------------------------------------------------------ tipe bangunan
def townhouse(name, w, d, floors, rnd):
    mb = MB(name)
    wall = rnd.choice(["brick", "brick2", "brick3", "wall_beige"])
    h = Z_LAWN + floors * 3.2 + .3
    mb.box(-w / 2, -d / 2, Z_LAWN, w / 2, d / 2, h, wall)
    windows(mb, w, d, Z_LAWN + .1, floors, skip_front_ground=True)
    mb.box(-.8, -d / 2 - .12, Z_LAWN, .8, -d / 2 + .02, Z_LAWN + 2.4, "door")
    gable(mb, w, d, h, min(w, d) * .42, rnd.choice(["roof_brown", "roof_brown", "roof_brown", "roof_orange"]), wall)
    mb.box(w * .2, -.4, h + .5, w * .2 + .9, .5, h + min(w, d) * .5, "brick3")
    return mb, h + min(w, d) * .42


def shophouse(name, w, d, floors, rnd, aw=None, wall=None):
    mb = MB(name)
    wall = wall or rnd.choice(["wall_orange", "wall_peach", "wall_beige", "brick2", "wall_cream2"])
    h = Z_LAWN + floors * 3.2 + .5
    mb.box(-w / 2, -d / 2, Z_LAWN, w / 2, d / 2, h, wall)
    windows(mb, w, d, Z_LAWN + .1, floors, skip_front_ground=True)
    mb.box(-w / 2 + .6, -d / 2 - .1, Z_LAWN + .1, w / 2 - .6, -d / 2 + .02, Z_LAWN + 2.7, "frame")
    mb.box(-w / 2 + .8, -d / 2 - .16, Z_LAWN + .2, w / 2 - .8, -d / 2 - .05, Z_LAWN + 2.55, "glass2")
    awning(mb, -w / 2 + .3, w / 2 - .3, -d / 2, Z_LAWN + 3.05, 1.8,
           aw or rnd.choice(["teal", "yellow", "green_aw", "red_aw", "teal"]))
    slab = rnd.choice(["roof_slab", "roof_slab2"])
    mb.box(-w / 2 - .15, -d / 2 - .15, h, w / 2 + .15, d / 2 + .15, h + .25, slab)
    for (a, b, c, e) in ((-w / 2 - .15, -d / 2 - .15, w / 2 + .15, -d / 2 + .2), (-w / 2 - .15, d / 2 - .2, w / 2 + .15, d / 2 + .15),
                         (-w / 2 - .15, -d / 2 - .15, -w / 2 + .2, d / 2 + .15), (w / 2 - .2, -d / 2 - .15, w / 2 + .15, d / 2 + .15)):
        mb.box(a, b, h + .25, c, e, h + .75, wall)
    mb.box(-w * .2, -d * .1, h + .25, w * .1, d * .2, h + 1.3, "roof_slab2")
    return mb, h + .75


def cottage(name, w, d, rnd):
    mb = MB(name)
    wall = rnd.choice(["wall_beige", "wall_cream2", "wall_peach"])
    h = Z_LAWN + 3.6
    mb.box(-w / 2, -d / 2, Z_LAWN, w / 2, d / 2, h, wall)
    windows(mb, w, d, Z_LAWN + .1, 1, skip_front_ground=True, fh=3.4)
    mb.box(-.7, -d / 2 - .12, Z_LAWN, .7, -d / 2 + .02, Z_LAWN + 2.3, "door")
    gable(mb, w, d, h, min(w, d) * .55, "roof_orange", wall)
    return mb, h + min(w, d) * .55


def sneaker(mb, x0, y, z0, length, upper="sneaker", depth=.5, facing_y=True):
    """sepatu low-poly dilihat dari samping, diekstrusi di sumbu Y (tebal = depth)."""
    s = length / 3.2
    mb.box(x0, y - depth / 2, z0, x0 + length, y + depth / 2, z0 + .35 * s, "sole")
    prof = [(0, .35), (3.2, .35), (3.25, .7), (2.3, 1.0), (1.45, 1.75), (.35, 1.85), (0, 1.35)]
    mb.prism_y([(x0 + px * s, z0 + pz * s) for px, pz in prof], y - depth / 2 * .92, y + depth / 2 * .92, upper)
    for i in range(3):
        lx = x0 + (1.55 + i * .32) * s
        mb.box(lx, y - depth / 2 - .02, z0 + (1.45 - i * .2) * s, lx + .18 * s, y + depth / 2 + .02,
               z0 + (1.58 - i * .2) * s, "lace")


def shoe_pair(name, color, scale=1.0):
    """sepasang sepatu (objek terpisah, untuk animasi). Asal di tengah bawah."""
    mb = MB(name)
    ln = 1.0 * scale
    for dy in (-.22 * scale, .22 * scale):
        sneaker(mb, -ln / 2, dy, 0, ln, upper=color, depth=.34 * scale)
    return mb


def shoe_shop(name, w=14, d=11.5):
    mb = MB(name)
    h = Z_LAWN + 2 * 3.4 + .5
    mb.box(-w / 2, -d / 2, Z_LAWN, w / 2, d / 2, h, "brick2")
    windows(mb, w, d, Z_LAWN + .3, 2, fh=3.4, skip_front_ground=True)
    # etalase besar + rak sepatu di balik kaca
    mb.box(-w / 2 + .5, -d / 2 - .12, Z_LAWN + .1, w / 2 - .5, -d / 2 + .02, Z_LAWN + 3.0, "frame")
    mb.box(-w / 2 + .7, -d / 2 - .18, Z_LAWN + .25, w / 2 - .7, -d / 2 - .06, Z_LAWN + 2.85, "glass2")
    cols = ["red_aw", "yellow", "sneaker", "sole", "teal", "wall_orange"]
    for row in range(3):
        for i in range(9):
            x = -w / 2 + 1.3 + i * 1.3
            mb.box(x, -d / 2 - .26, Z_LAWN + .55 + row * .75, x + .8, -d / 2 - .18, Z_LAWN + .85 + row * .75,
                   cols[(i + row * 2) % len(cols)])
    mb.box(-.9, -d / 2 - .2, Z_LAWN, .9, -d / 2 - .1, Z_LAWN + 2.5, "door")
    awning(mb, -w / 2 + .2, w / 2 - .2, -d / 2, Z_LAWN + 3.6, 2.3, "teal")
    mb.box(-w / 2 - .2, -d / 2 - .2, h, w / 2 + .2, d / 2 + .2, h + .3, "shop_roof")
    for (a, b, c, e) in ((-w / 2 - .2, -d / 2 - .2, w / 2 + .2, -d / 2 + .25), (-w / 2 - .2, d / 2 - .25, w / 2 + .2, d / 2 + .2),
                         (-w / 2 - .2, -d / 2 - .2, -w / 2 + .25, d / 2 + .2), (w / 2 - .25, -d / 2 - .2, w / 2 + .2, d / 2 + .2)):
        mb.box(a, b, h + .3, c, e, h + .9, "shop_roof")
    # papan reklame sepatu di atap
    bz = h + .3
    for px in (-2.6, 2.6):
        mb.box(px - .15, -1.0, bz, px + .15, -.7, bz + 2.0, "metal")
    mb.box(-4.2, -1.25, bz + 1.6, 4.2, -.85, bz + 6.0, "board_frame")
    mb.box(-3.9, -1.35, bz + 1.9, 3.9, -1.2, bz + 5.7, "board")
    sneaker(mb, -2.9, -1.55, bz + 2.4, 5.8, depth=.4)
    return mb, (0, -1.3, bz + 6.0)


def laundry(name, w=11, d=10, floors=2):
    mb = MB(name)
    h = Z_LAWN + floors * 3.2 + .5
    mb.box(-w / 2, -d / 2, Z_LAWN, w / 2, d / 2, h, "laundry_wall")
    windows(mb, w, d, Z_LAWN + .1, floors, skip_front_ground=True)
    mb.box(-w / 2 + .5, -d / 2 - .12, Z_LAWN + .1, w / 2 - .5, -d / 2 + .02, Z_LAWN + 2.8, "frame")
    mb.box(-w / 2 + .7, -d / 2 - .18, Z_LAWN + .25, w / 2 - .7, -d / 2 - .06, Z_LAWN + 2.65, "glass2")
    for i in range(4):  # mesin cuci di balik kaca
        x = -w / 2 + 1.6 + i * 2.2
        mb.box(x, -d / 2 - .3, Z_LAWN + .25, x + 1.6, -d / 2 - .2, Z_LAWN + 1.85, "machine")
        mb.disc_y(x + .8, -d / 2 - .3, Z_LAWN + 1.0, .5, .08, "machine_door")
    awning(mb, -w / 2 + .2, w / 2 - .2, -d / 2, Z_LAWN + 3.3, 2.0, "laundry_aw")
    mb.box(-w / 2 - .15, -d / 2 - .15, h, w / 2 + .15, d / 2 + .15, h + .25, "roof_slab2")
    # papan ikon mesin cuci
    mb.box(-1.8, -d / 2 - .3, h - .2, 1.8, -d / 2 + .2, h + 3.2, "laundry_aw")
    mb.box(-1.2, -d / 2 - .42, h + .3, 1.2, -d / 2 - .25, h + 2.7, "machine")
    mb.disc_y(0, -d / 2 - .42, h + 1.4, .75, .1, "machine_door")
    return mb, (0, -d / 2, h + 3.2)


# ------------------------------------------------------------------ props
def tree_round(mb, x, y, s, rnd):
    mb.box(x - .22 * s, y - .22 * s, Z_LAWN, x + .22 * s, y + .22 * s, Z_LAWN + 1.8 * s, "trunk")
    mb.sphere(x, y, Z_LAWN + 3.2 * s, 1.75 * s, rnd.choice(["tree_l", "tree_m", "tree_m"]), sz=1.9 * s)


def tree_conifer(mb, x, y, s):
    mb.box(x - .2 * s, y - .2 * s, Z_LAWN, x + .2 * s, y + .2 * s, Z_LAWN + 1.0 * s, "trunk")
    mb.cyl(x, y, Z_LAWN + .9 * s, Z_LAWN + 6.0 * s, 1.5 * s, "conifer", n=7, r_top=0)


def lamp(mb, x, y):
    mb.box(x - .1, y - .1, .25, x + .1, y + .1, 5.0, "metal")
    mb.box(x - .35, y - .35, 5.0, x + .35, y + .35, 5.35, "metal")
    mb.box(x - .25, y - .25, 4.85, x + .25, y + .25, 5.0, "frame")


def bench(mb, x, y, key, rot90=False):
    if rot90:
        mb.box(x - .35, y - 1, Z_LAWN + .45, x + .35, y + 1, Z_LAWN + .6, key)
        mb.box(x + .25, y - 1, Z_LAWN + .6, x + .35, y + 1, Z_LAWN + 1.1, key)
    else:
        mb.box(x - 1, y - .35, Z_LAWN + .45, x + 1, y + .35, Z_LAWN + .6, key)
        mb.box(x - 1, y + .25, Z_LAWN + .6, x + 1, y + .35, Z_LAWN + 1.1, key)
    mb.box(x - .1, y - .1, Z_LAWN, x + .1, y + .1, Z_LAWN + .45, "metal")


def umbrella_set(mb, x, y, key):
    mb.box(x - .05, y - .05, .25, x + .05, y + .05, 2.4, "metal")
    mb.cyl(x, y, 2.1, 2.9, 1.4, key, n=8, r_top=0)
    mb.cyl(x, y, .25, 1.0, .5, "frame", n=8)
    for dx, dy in ((-.9, 0), (.9, 0)):
        mb.box(x + dx - .2, y + dy - .2, .25, x + dx + .2, y + dy + .2, .7, "bench_wood")


def person(name, shirt, pants="pants", apron=False, arms_forward=False, bag=False, arms_up=False):
    """orang low-poly ±1.75 m, asal di kaki, menghadap -Y."""
    mb = MB(name)
    mb.box(-.25, -.14, 0, -.03, .14, .85, pants)
    mb.box(.03, -.14, 0, .25, .14, .85, pants)
    mb.box(-.3, -.18, .85, .3, .18, 1.45, shirt)
    if apron:
        mb.box(-.26, -.21, .7, .26, -.17, 1.38, "apron")
    if arms_up:
        mb.box(-.5, -.1, 1.3, -.36, .1, 2.15, shirt)
        mb.box(.36, -.1, 1.3, .5, .1, 2.15, shirt)
    elif arms_forward:
        mb.box(-.42, -.75, 1.12, -.3, -.05, 1.32, shirt)
        mb.box(.3, -.75, 1.12, .42, -.05, 1.32, shirt)
    else:
        mb.box(-.42, -.1, .8, -.3, .1, 1.42, shirt)
        mb.box(.3, -.1, .8, .42, .1, 1.42, shirt)
    if bag:
        mb.box(.42, -.3, .45, .62, .3, 1.05, "sole")
    mb.sphere(0, 0, 1.68, .24, "skin")
    mb.box(-.22, -.05, 1.8, .22, .24, 1.95, "door")
    return mb


SHIRTS = ["red_aw", "teal", "yellow", "sneaker", "green_aw", "wall_orange", "sole"]


# ------------------------------------------------------------------ dunia
def blocks():
    """daftar blok (x0,y0,x1,y1) termasuk trotoar."""
    edges = [-L, ROADS[0] - RW / 2, ROADS[0] + RW / 2, ROADS[1] - RW / 2, ROADS[1] + RW / 2, L]
    xs = [(edges[0], edges[1]), (edges[2], edges[3]), (edges[4], edges[5])]
    return [(a, b, c, d) for (a, c) in xs for (b, d) in xs]


def build_ground():
    g = MB("ground")
    g.box(-L, -L, -6, L, L, -.7, "soil")
    g.box(-L, -L, -.7, L, L, 0, "soil_top")
    for r in ROADS:
        g.box(-L, r - RW / 2, -.7, L, r + RW / 2, .05, "asphalt")
        cuts = [-L] + [v for q in ROADS for v in (q - RW / 2, q + RW / 2)] + [L]
        for i in range(0, len(cuts), 2):
            g.box(r - RW / 2, cuts[i], -.7, r + RW / 2, cuts[i + 1], .05, "asphalt")
    # marka tengah putus-putus
    for r in ROADS:
        t = -L + 1
        while t < L - 3:
            if all(abs(t + 1.25 - q) > RW / 2 + 4 for q in ROADS):
                g.box(t, r - .12, .05, t + 2.5, r + .12, .07, "line")
                g.box(r - .12, t, .05, r + .12, t + 2.5, .07, "line")
            t += 5
    # zebra cross di tiap sisi persimpangan
    for cx in ROADS:
        for cy in ROADS:
            for sgn in (-1, 1):
                yb = cy + sgn * (RW / 2 + 1.7)
                for i in range(7):
                    x = cx - RW / 2 + .6 + i * 1.3
                    g.box(x, yb - 1.2, .05, x + .7, yb + 1.2, .075, "line")
                xb = cx + sgn * (RW / 2 + 1.7)
                for i in range(7):
                    y = cy - RW / 2 + .6 + i * 1.3
                    g.box(xb - 1.2, y, .05, xb + 1.2, y + .7, .075, "line")
    for (x0, y0, x1, y1) in blocks():
        g.box(x0, y0, -.7, x1, y1, .25, "sidewalk")
        ix0 = x0 + (SW if x0 > -L + .1 else 0)
        iy0 = y0 + (SW if y0 > -L + .1 else 0)
        ix1 = x1 - (SW if x1 < L - .1 else 0)
        iy1 = y1 - (SW if y1 < L - .1 else 0)
        g.box(ix0, iy0, .25, ix1, iy1, Z_LAWN, "lawn")
    return g.build()


def inner(b):
    x0, y0, x1, y1 = b
    return (x0 + (SW if x0 > -L + .1 else 1), y0 + (SW if y0 > -L + .1 else 1),
            x1 - (SW if x1 < L - .1 else 1), y1 - (SW if y1 < L - .1 else 1))


PLACED = []


def place(mb_and_top, cx, cy, facing):
    mb, top = mb_and_top
    ob = mb.build((cx, cy, 0), FACING[facing])
    PLACED.append((ob.name, (cx, cy, top)))
    return ob, top


def build_world(seed=5, people=True):
    """membangun seluruh diorama. Mengembalikan dict titik-titik penting."""
    rnd = random.Random(seed)
    info = {"anchors": {}, "routes": {}, "objects": {}}
    build_ground()
    props = MB("props")
    trees = MB("trees")

    # --- blok tengah: toko cuci sepatu + laundry utama + kafe
    shop_c = (-7.0, -9.75)
    mb, top = shoe_shop("shoe_shop")
    mb.build((*shop_c, 0), 0)
    info["anchors"]["TOKO"] = local_to_world(top, (*shop_c, 0), "-y")
    info["anchors"]["TOKO_FRONT"] = (shop_c[0] - 3.5, -18.0, 4.6)
    info["shop_front"] = (shop_c[0], -15.5)
    lau_c = (8.5, -10.5)
    mb, top = laundry("laundry_main", w=12, d=10)
    mb.build((*lau_c, 0), 0)
    info["anchors"]["LAUNDRY"] = local_to_world(top, (*lau_c, 0), "-y")
    info["laundry_front"] = (lau_c[0], -15.5)
    place(shophouse("cafe", 12, 10, 2, rnd, aw="yellow"), -8, 9.5, "+y")
    place(townhouse("th_c1", 10, 10, 3, rnd), 8, 9.5, "+y")
    for x in (-14.5, 14.5):
        tree_round(trees, x, 0, 1.0, rnd)
    for x in (-13.5, -1, 13.5):
        lamp(props, x, -17.5)

    # --- laundry mitra di blok luar
    MITRA = {
        "MITRA 1": ((-38.5, -.5), "+x", [(-33, -.5), (-26, -.5), (-26, -22), (-7, -22), (-7, -17)]),
        "MITRA 2": ((0, 38), "-y", [(0, 32.5), (0, 26), (22, 26), (22, -22), (-7, -22), (-7, -17)]),
        "MITRA 3": ((38.5, -.5), "-x", [(33, -.5), (26, -.5), (26, -22), (-7, -22), (-7, -17)]),
        "MITRA 4": ((46, -38.5), "+y", [(46, -32.5), (46, -26), (-7, -26), (-7, -17)]),
        "MITRA 5": ((-46, 38), "-y", [(-46, 32.5), (-46, 22), (-22, 22), (-22, -22), (-7, -22), (-7, -17)]),
    }
    reserved = [(-15.5, -15.5, 15.5, 15.5)]
    for i, (name, (c, facing, route)) in enumerate(MITRA.items()):
        mb, top = laundry(f"laundry{i}", w=11, d=10)
        mb.build((*c, 0), FACING[facing])
        info["anchors"][name] = local_to_world(top, (*c, 0), facing)
        info["routes"][name] = route
        reserved.append((c[0] - 7, c[1] - 7, c[0] + 7, c[1] + 7))

    # --- taman (blok barat-daya)
    pb = inner((-L, -L, ROADS[0] - RW / 2, ROADS[0] - RW / 2))
    reserved.append(pb)
    px, py = (pb[0] + pb[2]) / 2, (pb[1] + pb[3]) / 2
    props.box(pb[0] + 2, py - 1.2, Z_LAWN, pb[2] - 2, py + 1.2, Z_LAWN + .03, "path")
    props.box(px - 1.2, pb[1] + 2, Z_LAWN, px + 1.2, pb[3] - 2, Z_LAWN + .03, "path")
    for (bx, by, k, r90) in ((px - 8, py + 2.4, "teal", False), (px + 7, py - 2.4, "yellow", False),
                             (px + 2.6, py + 9, "teal", True), (px - 2.6, py - 8, "yellow", True)):
        bench(props, bx, by, k, r90)
    for i in range(int((pb[2] - pb[0]) // 1.6)):
        x = pb[0] + 1 + i * 1.6
        props.box(x, pb[3] - 1.2, Z_LAWN, x + .15, pb[3] - 1.05, Z_LAWN + 1.0, "bench_wood")
    props.box(pb[0] + 1, pb[3] - 1.2, Z_LAWN + .7, pb[2] - 1, pb[3] - 1.05, Z_LAWN + .85, "bench_wood")
    for q in range(26):
        x = rnd.uniform(pb[0] + 3, pb[2] - 3)
        y = rnd.uniform(pb[1] + 3, pb[3] - 3)
        if abs(x - px) < 3 or abs(y - py) < 3:
            continue
        if rnd.random() < .45:
            tree_conifer(trees, x, y, rnd.uniform(.8, 1.15))
        else:
            tree_round(trees, x, y, rnd.uniform(.8, 1.2), rnd)

    # --- deret ruko + kafe payung (blok selatan-tengah, menghadap +y)
    sb = inner((ROADS[0] + RW / 2, -L, ROADS[1] - RW / 2, ROADS[0] - RW / 2))
    reserved.append((sb[0], sb[3] - 12, sb[2], sb[3]))
    n = 4
    uw = (sb[2] - sb[0]) / n
    for i in range(n):
        place(shophouse(f"row_s{i}", uw - .4, 10, rnd.choice([2, 3]), rnd), sb[0] + uw * (i + .5), sb[3] - 5.5, "+y")
    for i in range(3):
        umbrella_set(props, sb[0] + 5 + i * 11, sb[3] + 1.6, ["umbrella", "teal", "umbrella"][i])

    # --- isi kavling lain
    for b in blocks():
        ib = inner(b)
        lot = 11.5
        nx, ny = max(1, int((ib[2] - ib[0]) // lot)), max(1, int((ib[3] - ib[1]) // lot))
        lx, ly = (ib[2] - ib[0]) / nx, (ib[3] - ib[1]) / ny
        for a in range(nx):
            for c in range(ny):
                cx, cy = ib[0] + (a + .5) * lx, ib[1] + (c + .5) * ly
                rect = (cx - lx / 2 + .5, cy - ly / 2 + .5, cx + lx / 2 - .5, cy + ly / 2 - .5)
                if any(lp._overlap(rect, r) for r in reserved):
                    continue
                # hadap ke jalan terdekat
                cands = [(abs(cx - r), "+x" if cx < r else "-x") for r in ROADS] + \
                        [(abs(cy - r), "+y" if cy < r else "-y") for r in ROADS]
                facing = min(cands)[1]
                w = rnd.uniform(7.5, min(lx, ly) - 2.6)
                d = rnd.uniform(7.5, min(lx, ly) - 2.6)
                k = rnd.random()
                if k < .12:
                    tree_round(trees, cx - 2, cy, 1.1, rnd)
                    tree_conifer(trees, cx + 2.5, cy + 1.5, 1.0)
                    continue
                if k < .45:
                    place(townhouse(f"th{a}{c}{cx:.0f}{cy:.0f}", w, d, rnd.choice([2, 2, 3]), rnd), cx, cy, facing)
                elif k < .85:
                    place(shophouse(f"sh{a}{c}{cx:.0f}{cy:.0f}", w, d, rnd.choice([2, 3]), rnd), cx, cy, facing)
                else:
                    place(cottage(f"co{a}{c}{cx:.0f}{cy:.0f}", w * .9, d * .9, rnd), cx, cy, facing)
                for (tx_, ty_) in ((rect[0] + 1.1, rect[1] + 1.1), (rect[2] - 1.1, rect[3] - 1.1)):
                    if rnd.random() < .55:
                        if rnd.random() < .35:
                            tree_conifer(trees, tx_, ty_, .6)
                        else:
                            tree_round(trees, tx_, ty_, .65, rnd)

    # lampu jalan di sepanjang trotoar
    for r in ROADS:
        for t in range(-66, 67, 18):
            if all(abs(t - q) > 9 for q in ROADS):
                for off in (-RW / 2 - 1.2, RW / 2 + 1.2):
                    if not (r + off < -10 and abs(t + 7) < 4):
                        lamp(props, t, r + off)
                        lamp(props, r + off, t)
    props.build()
    trees.build()

    # pejalan kaki
    info["people"] = []
    if people:
        prnd = random.Random(seed + 1)
        for k in range(26):
            r = prnd.choice(ROADS)
            off = prnd.choice((-RW / 2 - 1.7, RW / 2 + 1.7))
            horiz = prnd.random() < .5
            t0 = prnd.uniform(-60, 60)
            if any(abs(t0 - q) < 8 for q in ROADS):
                t0 += 12
            ob = person(f"ped{k}", prnd.choice(SHIRTS)).build()
            ob.scale = (1.25,) * 3
            sp = prnd.choice((-1, 1)) * prnd.uniform(1.0, 1.5)
            if horiz:
                ob.location = (t0, r + off, .25)
                ob.rotation_euler.z = -math.pi / 2 if sp > 0 else math.pi / 2
            else:
                ob.location = (r + off, t0, .25)
                ob.rotation_euler.z = 0 if sp > 0 else math.pi
            info["people"].append((ob, horiz, sp))
    info["MITRA"] = MITRA
    return info


def animate_people(info, n_frames, fps=30):
    for ob, horiz, sp in info["people"]:
        start = Vector(ob.location)
        ob.keyframe_insert("location", frame=1)
        d = sp * n_frames / fps
        ob.location = start + (Vector((d, 0, 0)) if horiz else Vector((0, d, 0)))
        ob.keyframe_insert("location", frame=n_frames)


def setup_world_light():
    sc = bpy.context.scene
    w = bpy.data.worlds.new("w2")
    w.use_nodes = True
    nt = w.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputWorld")
    mix = nt.nodes.new("ShaderNodeMixShader")
    lpth = nt.nodes.new("ShaderNodeLightPath")
    b_light = nt.nodes.new("ShaderNodeBackground")
    b_cam = nt.nodes.new("ShaderNodeBackground")
    col = lp.hex_rgba(lp.PAL["sky"])
    b_light.inputs["Color"].default_value = col
    b_light.inputs["Strength"].default_value = 0.75
    b_cam.inputs["Color"].default_value = col
    b_cam.inputs["Strength"].default_value = 1.0
    nt.links.new(lpth.outputs["Is Camera Ray"], mix.inputs["Fac"])
    nt.links.new(b_light.outputs[0], mix.inputs[1])
    nt.links.new(b_cam.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    sc.world = w
    sun = bpy.data.objects.get("sun")
    sun.data.energy = 3.3
    sun.data.color = (1.0, .96, .9)
    sun.data.angle = math.radians(6)
    sun.rotation_euler = (math.radians(42), 0, math.radians(-62))
