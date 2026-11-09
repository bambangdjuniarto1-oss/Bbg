"""Low-poly toolkit + procedural Indonesian neighborhood for Blender (bpy module).

Semua objek dibuat dari geometri sederhana, flat-shaded, warna solid
(tanpa tekstur) supaya mirip gaya video referensi.
"""
import math
import random

import bmesh
import bpy

# ---------------------------------------------------------------- palette
PAL = {
    "sky": "#E2ECEE",
    "grass": "#5DAA45",
    "asphalt": "#5A5F63",
    "road_line": "#F4F4F0",
    "sidewalk": "#D9D4C9",
    "roof_red": "#C4442F",
    "roof_red2": "#A8432F",
    "roof_blue": "#4F7FA8",
    "roof_blue2": "#3F6688",
    "wall_cream": "#F1E6CC",
    "wall_mint": "#CFE8D6",
    "wall_salmon": "#F2C9B8",
    "wall_white": "#F3F1EC",
    "wall_grey": "#C9CBCB",
    "glass": "#3C5A73",
    "tree": "#4C9A3E",
    "tree2": "#3E8A39",
    "trunk": "#7A5236",
    "car_red": "#D23A2E",
    "car_yellow": "#F2C230",
    "car_blue": "#2F6DB5",
    "car_white": "#F4F4F4",
    "tire": "#2A2A2A",
    "shop_red": "#D7262E",
    "laundry_blue": "#2E86DE",
    "route": "#FFD43B",
    "rider": "#D93B2B",
    "scooter": "#3A3F44",
    "bag": "#FFFFFF",
}


def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_rgba(h):
    h = h.lstrip("#")
    return tuple(srgb_to_lin(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)) + (1.0,)


_MATS = {}


def mat(key, emission=0.0):
    hexv = PAL.get(key, key)
    k = (hexv, emission)
    if k in _MATS:
        return _MATS[k]
    m = bpy.data.materials.new(f"m_{key}_{emission}")
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = hex_rgba(hexv)
    bsdf.inputs["Roughness"].default_value = 0.85
    bsdf.inputs["Specular IOR Level"].default_value = 0.15
    if emission:
        bsdf.inputs["Emission Color"].default_value = hex_rgba(hexv)
        bsdf.inputs["Emission Strength"].default_value = emission
    _MATS[k] = m
    return m


_COL = None


def _link(obj):
    (_COL or bpy.context.scene.collection).objects.link(obj)
    return obj


def mesh_obj(name, verts, faces, material, parent=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in verts]
    for f in faces:
        bm.faces.new([vs[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    if parent:
        ob.parent = parent
    return _link(ob)


def box(name, x0, y0, z0, x1, y1, z1, material, parent=None):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return mesh_obj(name, v, f, material, parent)


def boxc(name, cx, cy, z0, w, d, h, material, parent=None):
    return box(name, cx - w / 2, cy - d / 2, z0, cx + w / 2, cy + d / 2, z0 + h, material, parent)


def hip_roof(name, x0, y0, x1, y1, z, hr, material):
    w, d = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if w >= d:
        r1, r2 = (x0 + d / 2, cy, z + hr), (x1 - d / 2, cy, z + hr)
        v = [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z), r1, r2]
        f = [(0, 1, 5, 4), (2, 3, 4, 5), (3, 0, 4), (1, 2, 5), (0, 3, 2, 1)]
    else:
        r1, r2 = (cx, y0 + w / 2, z + hr), (cx, y1 - w / 2, z + hr)
        v = [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z), r1, r2]
        f = [(1, 2, 5, 4), (3, 0, 4, 5), (0, 1, 4), (2, 3, 5), (0, 3, 2, 1)]
    return mesh_obj(name, v, f, material)


def tree(name, x, y, s=1.0):
    box(name + "_trunk", x - .25 * s, y - .25 * s, 0, x + .25 * s, y + .25 * s, 1.6 * s, mat("trunk"))
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.9 * s)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(x, y, 2.9 * s))
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat(random.choice(["tree", "tree2"])))
    _link(bpy.data.objects.new(name, me))


def house(name, cx, cy, w, d, storeys=1):
    wall = random.choice(["wall_cream", "wall_mint", "wall_salmon", "wall_white", "wall_cream"])
    roof = random.choice(["roof_red", "roof_red", "roof_red2", "roof_blue", "roof_blue2"])
    h = 3.6 * storeys
    boxc(name + "_body", cx, cy, 0, w, d, h, mat(wall))
    o = 0.6
    hip_roof(name + "_roof", cx - w / 2 - o, cy - d / 2 - o, cx + w / 2 + o, cy + d / 2 + o, h,
             min(w, d) * 0.38, mat(roof))


def ruko_row(name, x0, x1, y_front, depth, facing=-1, units=None):
    """Deretan ruko 2 lantai menghadap jalan. facing=-1 → menghadap -y."""
    n = units or max(2, int((x1 - x0) // 5.5))
    uw = (x1 - x0) / n
    for i in range(n):
        ux0 = x0 + i * uw
        yb = y_front if facing < 0 else y_front - depth
        ye = y_front + depth if facing < 0 else y_front
        box(f"{name}_{i}", ux0 + .1, yb, 0, ux0 + uw - .1, ye, 8.2,
            mat(random.choice(["wall_white", "wall_grey", "wall_cream"])))
        gy = y_front - .05 * facing * -1
        # kaca lantai 1 & 2
        fy0, fy1 = (y_front - .15, y_front + .05) if facing < 0 else (y_front - .05, y_front + .15)
        box(f"{name}_g{i}", ux0 + .7, fy0, .2, ux0 + uw - .7, fy1, 3.0, mat("glass"))
        box(f"{name}_w{i}", ux0 + 1.2, fy0, 4.6, ux0 + uw - 1.2, fy1, 6.6, mat("glass"))
        aw = random.choice(["shop_red", "laundry_blue", "car_yellow", "wall_mint", "roof_red"])
        ay0, ay1 = (y_front - 1.6, y_front) if facing < 0 else (y_front, y_front + 1.6)
        box(f"{name}_a{i}", ux0 + .3, ay0, 3.2, ux0 + uw - .3, ay1, 3.6, mat(aw))
        _ = gy


def car(name, length=4.2, color=None):
    color = color or random.choice(["car_red", "car_yellow", "car_blue", "car_white", "car_white"])
    root = bpy.data.objects.new(name, None)
    _link(root)
    box(name + "_b", -length / 2, -1, .45, length / 2, 1, 1.35, mat(color), root)
    box(name + "_c", -length / 4, -.9, 1.35, length / 4 + .3, .9, 2.1, mat(color), root)
    box(name + "_gl", -length / 4 - .02, -.85, 1.45, length / 4 + .32, .85, 2.0, mat("glass"), root)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(f"{name}_t{sx}{sy}", sx * length * .32 - .35, sy * 1.0 - .25, 0, sx * length * .32 + .35,
                sy * 1.0 + .25, .7, mat("tire"), root)
    return root


def scooter(name, scale=1.6):
    """Motor kurir + rider + tas sepatu. Menghadap +X."""
    root = bpy.data.objects.new(name, None)
    _link(root)
    s = scale
    box(name + "_body", -.9 * s, -.25 * s, .35 * s, .9 * s, .25 * s, .85 * s, mat("scooter"), root)
    box(name + "_w1", .55 * s, -.1 * s, 0, 1.05 * s, .1 * s, .5 * s, mat("tire"), root)
    box(name + "_w2", -1.05 * s, -.1 * s, 0, -.55 * s, .1 * s, .5 * s, mat("tire"), root)
    box(name + "_torso", -.35 * s, -.3 * s, .85 * s, .2 * s, .3 * s, 1.75 * s, mat("rider"), root)
    box(name + "_head", -.25 * s, -.22 * s, 1.75 * s, .2 * s, .22 * s, 2.2 * s, mat("rider"), root)
    box(name + "_bag", -1.2 * s, -.45 * s, .85 * s, -.4 * s, .45 * s, 1.6 * s, mat("bag"), root)
    return root


def poly_curve(name, pts, z=0.0):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for p, (x, y) in zip(sp.points, pts):
        p.co = (x, y, z, 1)
    ob = bpy.data.objects.new(name, cu)
    return _link(ob), cu


def path_length(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


# ------------------------------------------------------------------ town
H_ROADS = {-80: 6, -40: 6, 0: 14, 40: 6, 80: 6}   # y : lebar (0 = jalan primer)
V_ROADS = {-90: 6, -45: 6, 0: 9, 45: 6, 90: 6}    # x : lebar (0 = jalan sekunder)
EXTENT = 175


def _overlap(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def build_roads():
    E = EXTENT
    box("ground", -E - 60, -E - 60, -.05, E + 60, E + 60, 0, mat("grass"))
    for y, w in H_ROADS.items():
        box(f"rh{y}", -E - 60, y - w / 2, 0, E + 60, y + w / 2, .06, mat("asphalt"))
    for x, w in V_ROADS.items():
        box(f"rv{x}", x - w / 2, -E - 60, 0, x + w / 2, E + 60, .065, mat("asphalt"))
    # trotoar jalan primer & sekunder
    for sgn in (-1, 1):
        box(f"sw_p{sgn}", -E - 60, sgn * 7 if sgn > 0 else -10, 0, E + 60, 10 if sgn > 0 else -7, .22,
            mat("sidewalk"))
    # marka putus-putus
    line = mat("road_line")

    def crossing(val, roads, pad=2):
        return any(abs(val - r) < w / 2 + pad for r, w in roads.items())

    for ly in (-3.5, 3.5):
        x = -E - 60
        while x < E + 60:
            if not crossing(x + 1.5, V_ROADS):
                box("dash", x, ly - .18, .06, x + 3, ly + .18, .08, line)
            x += 7
    box("centre", -E - 60, -.15, .06, E + 60, .15, .08, mat("car_yellow"))
    y = -E - 60
    while y < E + 60:
        if not crossing(y + 1.5, H_ROADS):
            box("dashv", -.15, y, .065, .15, y + 3, .085, line)
        y += 7


def build_blocks(reserved, seed=7):
    random.seed(seed)
    hs = sorted(H_ROADS)
    vs = sorted(V_ROADS)
    ys = [-EXTENT - 40] + hs + [EXTENT + 40]
    xs = [-EXTENT - 40] + vs + [EXTENT + 40]
    hw = {**{k: v for k, v in H_ROADS.items()}, ys[0]: 0, ys[-1]: 0}
    vw = {**{k: v for k, v in V_ROADS.items()}, xs[0]: 0, xs[-1]: 0}
    n = 0
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            bx0 = xs[i] + vw[xs[i]] / 2 + 2
            bx1 = xs[i + 1] - vw[xs[i + 1]] / 2 - 2
            by0 = ys[j] + hw[ys[j]] / 2 + 2 + (3 if ys[j] == 0 else 0)
            by1 = ys[j + 1] - hw[ys[j + 1]] / 2 - 2 - (3 if ys[j + 1] == 0 else 0)
            # ruko di sepanjang jalan primer
            if ys[j + 1] == 0 or ys[j] == 0:
                front = by0 if ys[j] == 0 else by1
                facing = -1 if ys[j] == 0 else 1
                segs = []
                x = bx0
                for r in sorted(reserved):
                    pass
                cuts = sorted([r for r in reserved if (r[1] <= front + 1 <= r[3] or r[1] <= front - 1 <= r[3])
                               and r[2] > bx0 and r[0] < bx1])
                x = bx0
                for r in cuts:
                    if r[0] - x > 6:
                        segs.append((x, r[0] - 1))
                    x = r[2] + 1
                if bx1 - x > 6:
                    segs.append((x, bx1))
                for k, (s0, s1) in enumerate(segs):
                    ruko_row(f"ruko{i}_{j}_{k}", s0, s1, front, 12, facing)
                if facing < 0:
                    by0 += 15
                else:
                    by1 -= 15
            # kavling rumah
            lot = 11.0
            nx = max(1, int((bx1 - bx0) // lot))
            ny = max(1, int((by1 - by0) // lot))
            lx = (bx1 - bx0) / nx
            ly = (by1 - by0) / ny
            for a in range(nx):
                for b in range(ny):
                    cx = bx0 + (a + .5) * lx
                    cy = by0 + (b + .5) * ly
                    rect = (cx - lx / 2, cy - ly / 2, cx + lx / 2, cy + ly / 2)
                    if any(_overlap(rect, r) for r in reserved):
                        continue
                    n += 1
                    r = random.random()
                    if r < .1:
                        tree(f"t{n}", cx + random.uniform(-2, 2), cy + random.uniform(-2, 2), random.uniform(.9, 1.3))
                        continue
                    w = random.uniform(6.5, lx - 2.2)
                    d = random.uniform(6.5, ly - 2.2)
                    house(f"h{n}", cx + random.uniform(-.6, .6), cy + random.uniform(-.6, .6), w, d,
                          2 if random.random() < .18 else 1)
                    if random.random() < .25:
                        tree(f"tt{n}", cx + lx / 2 - 1, cy - ly / 2 + 1, .7)


def shop_building(name, x0, y0, x1, y1, facing, wall, accent, h=7.0):
    """Bangunan usaha dengan kaca depan + kanopi + papan nama di atap.
    facing: '-y', '+y', '-x', '+x' (arah depan toko)."""
    box(name + "_body", x0, y0, 0, x1, y1, h, mat(wall))
    box(name + "_roof", x0 - .3, y0 - .3, h, x1 + .3, y1 + .3, h + .5, mat(accent))
    t = .2
    if facing in ("-y", "+y"):
        fy = y0 if facing == "-y" else y1
        sg = -1 if facing == "-y" else 1
        box(name + "_glass", x0 + 1, fy + sg * t - t / 2, .2, x1 - 1, fy + sg * t + t / 2, 4.2, mat("glass"))
        box(name + "_awn", x0 - .3, min(fy, fy + sg * 2.4), 4.4, x1 + .3, max(fy, fy + sg * 2.4), 4.9, mat(accent))
        sx = (x0 + x1) / 2
        box(name + "_sign", sx - (x1 - x0) * .4, fy + sg * .2 - .3, h + .5, sx + (x1 - x0) * .4, fy + sg * .2 + .3,
            h + 3.2, mat(accent))
        anchor = (sx, fy, h + 3.2)
    else:
        fx = x0 if facing == "-x" else x1
        sg = -1 if facing == "-x" else 1
        box(name + "_glass", fx + sg * t - t / 2, y0 + 1, .2, fx + sg * t + t / 2, y1 - 1, 4.2, mat("glass"))
        box(name + "_awn", min(fx, fx + sg * 2.4), y0 - .3, 4.4, max(fx, fx + sg * 2.4), y1 + .3, 4.9, mat(accent))
        sy = (y0 + y1) / 2
        box(name + "_sign", fx + sg * .2 - .3, sy - (y1 - y0) * .4, h + .5, fx + sg * .2 + .3, sy + (y1 - y0) * .4,
            h + 3.2, mat(accent))
        anchor = (fx, sy, h + 3.2)
    return anchor


def setup_render(res_x, res_y, samples=20):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 3
    sc.cycles.diffuse_bounces = 2
    sc.cycles.glossy_bounces = 1
    sc.cycles.transmission_bounces = 0
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.render.use_persistent_data = True
    sc.render.resolution_x = res_x
    sc.render.resolution_y = res_y
    sc.render.resolution_percentage = 100
    sc.render.fps = 30
    sc.render.image_settings.file_format = "PNG"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    world = bpy.data.worlds.new("w")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = hex_rgba(PAL["sky"])
    bg.inputs["Strength"].default_value = 0.7
    sc.world = world
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.data.energy = 3.4
    sun.data.angle = math.radians(12)
    sun.rotation_euler = (math.radians(38), math.radians(8), math.radians(-35))
    _link(sun)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _MATS.clear()
