"""Aset "Bedah Bisnis: GTA VI, Rp17 triliun sebelum rilis".
Kota diorama Vice City (lebih lebar: palem, hotel art-deco pastel bergaris neon, papan LED cuplikan resmi,
menara Rockstar, toko game + antrean pembeli berbendera), globe titik-daratan dengan pin pembeli dunia,
kotak game PS5 bersampul resmi, kartu gambar resmi, logo Rockstar 3D (SVG), bendera negara.
Tekstur dari render/gta_assets.py (env GTA_TEX)."""
import math
import os
import random

import bpy  # noqa: F401

import lowpoly as lp
import world as W
import world_ctd as C
import world_hotel as H
import world_prk as R
import world_vap as V

TEX = os.environ.get("GTA_TEX", "/tmp/claude-0/-home-user-Bbg/e4570b9b-8bb7-5f4c-a29b-693bb3cf9daa/scratchpad/gta/tex")
SHOTS = ["shot_gas", "shot_beach", "shot_heist", "shot_sunset", "shot_car", "shot_night", "shot_club", "shot_pool",
         "shot_guns", "shot_launch"]
PANELS = ["p_jl", "p_girl", "p_chain", "p_rifle", "p_bike", "p_heli", "p_boat", "p_car", "p_gator"]
MASCOTS = ["m_flamingo", "m_gator", "m_sun", "m_palm", "m_crab", "m_manatee", "m_car"]

lp.PAL.update({
    "case_blu": "#1F4FB8", "case_blk": "#15151B", "deco_pink": "#F6B8CF", "deco_mint": "#A8E6D9",
    "deco_peach": "#FFD1A8", "deco_lilac": "#D7C2F2", "deco_sky": "#AFD8F5", "deco_white": "#FBF6F2",
    "rs_yel": "#FFAB00", "rs_blk": "#0B0B0D", "rs_wht": "#FFFFFF", "hq_glass": "#5B6E9C", "hq_glass2": "#7C8FBD",
    "palm": "#2E9B5A", "palm_trunk": "#9C7A55", "globe_core": "#120C2A", "land_dot": "#4FE3FF",
    "store_wall": "#2B2140", "store_wall2": "#3A2D57", "pc_case": "#2A2A33", "ps_white": "#F3F4F8",
    "ps_black": "#1A1B22", "fl_red": "#E0262E", "fl_white": "#FFFFFF", "fl_blue": "#1F3F99", "fl_green": "#139A48",
    "fl_yellow": "#FFD21F", "fl_black": "#111111", "fl_saff": "#FF9933", "fl_navy": "#0A2A66",
})
DECO = ["deco_pink", "deco_mint", "deco_peach", "deco_lilac", "deco_sky", "deco_white"]
NEON_TRIM = ["n_pink", "n_cyan", "n_purple", "n_gold"]


def tex(name):
    for ext in (".png", ".jpg"):
        p = os.path.join(TEX, name + ext)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(name)


# ================================================================== material gambar
_IMATS = {}


def img_mat(name, em=1.0, lit=False, alpha=None, mapping=False):
    """material gambar resmi. lit=False: layar/kartu berpendar (emisi). lit=True: dicetak (Principled + sedikit emisi).
    alpha: pakai kanal alfa (png). mapping=True: material unik dengan node Mapping (untuk zoom Ken Burns)."""
    path = tex(name)
    if alpha is None:
        alpha = path.endswith(".png")
    k = (path, em, lit, alpha)
    if k in _IMATS and not mapping:
        return _IMATS[k]
    img = bpy.data.images.load(path, check_existing=True)
    m = bpy.data.materials.new(f"img_{name}_{em}")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    ti = nt.nodes.new("ShaderNodeTexImage")
    ti.image = img
    ti.extension = "EXTEND"
    if mapping:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        mp = nt.nodes.new("ShaderNodeMapping")
        nt.links.new(tc.outputs["UV"], mp.inputs["Vector"])
        nt.links.new(mp.outputs["Vector"], ti.inputs["Vector"])
    if lit:
        sh = nt.nodes.new("ShaderNodeBsdfPrincipled")
        nt.links.new(ti.outputs["Color"], sh.inputs["Base Color"])
        nt.links.new(ti.outputs["Color"], sh.inputs["Emission Color"])
        sh.inputs["Emission Strength"].default_value = em
        sh.inputs["Roughness"].default_value = .45
    else:
        sh = nt.nodes.new("ShaderNodeEmission")
        nt.links.new(ti.outputs["Color"], sh.inputs["Color"])
        sh.inputs["Strength"].default_value = em
    if alpha:
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mx = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(ti.outputs["Alpha"], mx.inputs["Fac"])
        nt.links.new(tr.outputs[0], mx.inputs[1])
        nt.links.new(sh.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], out.inputs["Surface"])
    else:
        nt.links.new(sh.outputs[0], out.inputs["Surface"])
    if not mapping:
        _IMATS[k] = m
    return m


def img_size(name):
    img = bpy.data.images.load(tex(name), check_existing=True)
    return img.size[0], img.size[1]


def _quad_mesh(name, w, h, center=False):
    z0 = -h / 2 if center else 0.0
    me = bpy.data.meshes.new(name)
    me.from_pydata([(-w / 2, 0, z0), (w / 2, 0, z0), (w / 2, 0, z0 + h), (-w / 2, 0, z0 + h)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new(name="UV")
    for i, c in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
        uv.data[i].uv = c
    return me


def img_plane(name, img, h=None, w=None, loc=(0, 0, 0), rot_z=0.0, em=1.2, lit=False, alpha=None, center=False,
              frame=None, frame_em=5.0, mat=None):
    """kartu gambar berdiri menghadap -Y (pivot bawah-tengah, atau tengah bila center). Ukuran dari aspek gambar."""
    iw, ih = img_size(img)
    asp = iw / ih
    if w is None and h is None:
        h = 4.0
    if w is None:
        w = h * asp
    if h is None:
        h = w / asp
    me = _quad_mesh(name, w, h, center)
    me.materials.append(mat or img_mat(img, em, lit, alpha))
    ob = bpy.data.objects.new(name, me)
    lp._link(ob)
    ob.location = loc
    ob.rotation_euler.z = rot_z
    if frame:
        mb = W.MB(name + "_fr")
        t = max(.05, .025 * h)
        z0 = -h / 2 if center else 0
        mb.box(-w / 2 - t, .01, z0 - t, w / 2 + t, .06, z0, frame)
        mb.box(-w / 2 - t, .01, z0 + h, w / 2 + t, .06, z0 + h + t, frame)
        mb.box(-w / 2 - t, .01, z0, -w / 2, .06, z0 + h, frame)
        mb.box(w / 2, .01, z0, w / 2 + t, .06, z0 + h, frame)
        mb.box(-w / 2, .06, z0, w / 2, .12, z0 + h, "bd_dark")
        fo = mb.build(parent=ob)
        V.glow(fo, {frame: frame_em})
    ob["w"], ob["h"] = w, h
    return ob


def screen(name, imgs, w, h, loc, rot_z=0.0, switch=None, em=1.6, zoom=(1.0, 1.12), n_frames=200, frame="n_cyan",
           bezel=True):
    """layar LED / 'cuplikan': beberapa gambar resmi bergantian (crossfade 8 frame) + zoom pelan (Ken Burns).
    switch: frame pergantian [f1, f2, ...] (len = len(imgs)-1)."""
    switch = switch or [int(n_frames * (i + 1) / len(imgs)) for i in range(len(imgs) - 1)]
    me = _quad_mesh(name, w, h, center=True)
    m = bpy.data.materials.new(name + "_scr")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    emn = nt.nodes.new("ShaderNodeEmission")
    emn.inputs["Strength"].default_value = em
    nt.links.new(emn.outputs[0], out.inputs["Surface"])
    tc = nt.nodes.new("ShaderNodeTexCoord")
    asp_s = w / h
    cols = []
    for i, im in enumerate(imgs):
        ti = nt.nodes.new("ShaderNodeTexImage")
        ti.image = bpy.data.images.load(tex(im), check_existing=True)
        ti.extension = "EXTEND"
        mp = nt.nodes.new("ShaderNodeMapping")
        nt.links.new(tc.outputs["UV"], mp.inputs["Vector"])
        nt.links.new(mp.outputs["Vector"], ti.inputs["Vector"])
        iw, ih = ti.image.size
        asp_i = iw / ih
        sx, sy = (asp_s / asp_i, 1.0) if asp_i > asp_s else (1.0, asp_i / asp_s)
        f0 = 1 if i == 0 else switch[i - 1] - 4
        f1 = (switch[i] + 8) if i < len(switch) else n_frames
        for f, z in ((f0, zoom[0]), (f1, zoom[1])):
            s = (sx / z, sy / z)
            mp.inputs["Scale"].default_value = (s[0], s[1], 1)
            mp.inputs["Location"].default_value = (.5 * (1 - s[0]), .5 * (1 - s[1]) + (.04 * (z - 1)), 0)
            mp.inputs["Scale"].keyframe_insert("default_value", frame=f)
            mp.inputs["Location"].keyframe_insert("default_value", frame=f)
        cols.append(ti)
    cur = cols[0].outputs["Color"]
    for i, ti in enumerate(cols[1:]):
        mx = nt.nodes.new("ShaderNodeMix")
        mx.data_type = "RGBA"
        nt.links.new(cur, mx.inputs[6])
        nt.links.new(ti.outputs["Color"], mx.inputs[7])
        fs = switch[i]
        for f, v in ((fs - 4, 0.0), (fs + 4, 1.0)):
            mx.inputs[0].default_value = v
            mx.inputs[0].keyframe_insert("default_value", frame=f)
        cur = mx.outputs[2]
    nt.links.new(cur, emn.inputs["Color"])
    me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    lp._link(ob)
    ob.location = loc
    ob.rotation_euler.z = rot_z
    if bezel:
        mb = W.MB(name + "_bz")
        t = .25
        mb.box(-w / 2 - t, .02, -h / 2 - t, w / 2 + t, .4, h / 2 + t, "bd_dark")
        for (a, b, c, d) in ((-w / 2 - t, -h / 2 - t, w / 2 + t, -h / 2), (-w / 2 - t, h / 2, w / 2 + t, h / 2 + t),
                             (-w / 2 - t, -h / 2, -w / 2, h / 2), (w / 2, -h / 2, w / 2 + t, h / 2)):
            mb.box(a, -.02, b, c, .02, d, frame)
        bo = mb.build(parent=ob)
        V.glow(bo, {frame: 5.0})
    return ob


# ================================================================== kotak game
def game_case(name, cover="cover_ps5", s=1.0, loc=(0, 0, 0), rot_z=0.0, em=.35, side="case_blu"):
    """kotak game (13,5 x 17 x 1,4 cm diskala ~10x): sisi muka bersampul resmi. Pivot bawah-tengah."""
    w, h, d = 1.35 * s, 1.7 * s, .16 * s
    x0, x1, y0, y1 = -w / 2, w / 2, -d / 2, d / 2
    vs = [(x0, y0, 0), (x1, y0, 0), (x1, y0, h), (x0, y0, h), (x0, y1, 0), (x1, y1, 0), (x1, y1, h), (x0, y1, h)]
    fs = [(0, 1, 2, 3), (5, 4, 7, 6), (4, 0, 3, 7), (1, 5, 6, 2), (3, 2, 6, 7), (4, 5, 1, 0)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(vs, [], fs)
    uv = me.uv_layers.new(name="UV")
    li = 0
    for fi, f in enumerate(fs):
        for c in ((0, 0), (1, 0), (1, 1), (0, 1)):
            uv.data[li].uv = c if fi == 0 else (.5, .5)
            li += 1
    me.materials.append(img_mat(cover, em, lit=True))
    me.materials.append(lp.mat(side))
    for p in me.polygons:
        p.material_index = 0 if p.index == 0 else 1
    ob = bpy.data.objects.new(name, me)
    lp._link(ob)
    ob.location = loc
    ob.rotation_euler.z = rot_z
    return ob


def dup(ob, name, loc=None):
    o = ob.copy()
    o.name = name
    lp._link(o)
    if loc is not None:
        o.location = loc
    return o


# ================================================================== logo Rockstar 3D (SVG resmi)
def rockstar_logo(name, s=4.0, loc=(0, 0, 0), em=1.2, depth=.12):
    """impor SVG logo Rockstar -> kurva diekstrusi -> mesh; berdiri menghadap -Y, pivot tengah. s = lebar."""
    import addon_utils
    addon_utils.enable("io_curve_svg", default_set=False)
    before = set(bpy.data.objects)
    bpy.ops.import_curve.svg(filepath=os.path.join(TEX, "rockstar.svg"))
    new = [o for o in bpy.data.objects if o not in before and o.type == "CURVE"]
    # urutan path: kotak kuning (latar), R hitam, bintang putih -> warna dari material impor
    keys = []
    for o in new:
        col = o.data.materials[0].diffuse_color if o.data.materials else (1, 1, 1, 1)
        r, g, b = col[0], col[1], col[2]
        k = "rs_yel" if (r > .5 and b < .2) else ("rs_wht" if r > .5 else "rs_blk")
        keys.append(k)
    xs, ys = [], []
    for o in new:
        for sp in o.data.splines:
            for p in sp.bezier_points:
                v = o.matrix_world @ p.co
                xs.append(v.x)
                ys.append(v.y)
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    sc = s / (max(xs) - min(xs))
    order = {"rs_yel": 0, "rs_blk": 1, "rs_wht": 2}
    root = bpy.data.objects.new(name, None)
    lp._link(root)
    dg = bpy.context.evaluated_depsgraph_get()
    for o, k in zip(new, keys):
        o.data.extrude = depth / sc * (1.0 if k == "rs_yel" else .5)
        o.data.offset = 0
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
        me.transform(o.matrix_world)
        me.materials.clear()
        me.materials.append(lp.mat(k, emission=em if k != "rs_blk" else 0.0))
        ob = bpy.data.objects.new(name + "_" + k, me)
        lp._link(ob)
        bpy.data.objects.remove(o)
        # SVG di bidang XY -> berdiri: (x, y) -> (x, z); kuning paling belakang
        ob.parent = root
        ob.rotation_euler = (math.pi / 2, 0, 0)
        ob.scale = (sc, sc, sc)
        ob.location = (-cx * sc, -order[k] * depth * .55, -cy * sc)
    for c in list(bpy.data.collections):
        if c.name.lower().endswith(".svg") or c.name.lower() == "rockstar.svg":
            for o in list(c.objects):
                c.objects.unlink(o)
            bpy.data.collections.remove(c)
    root.location = loc
    return root


# ================================================================== globe pembeli dunia
CITIES = {  # (lat, lon)
    "ID": (-6.2, 106.8), "JP": (35.7, 139.7), "US": (40.7, -74.0), "US2": (34.0, -118.2), "BR": (-23.5, -46.6),
    "GB": (51.5, -0.1), "DE": (52.5, 13.4), "FR": (48.9, 2.35), "KR": (37.6, 127.0), "MX": (19.4, -99.1),
    "IN": (19.1, 72.9), "NG": (6.5, 3.4), "AU": (-33.9, 151.2), "AE": (25.2, 55.3), "ZA": (-26.2, 28.0),
    "CA": (43.7, -79.4), "AR": (-34.6, -58.4), "TR": (41.0, 29.0), "PH": (14.6, 121.0), "SA": (24.7, 46.7),
}


def latlon(lat, lon, r):
    la, lo = math.radians(lat), math.radians(lon)
    return (r * math.cos(la) * math.cos(lo), r * math.cos(la) * math.sin(lo), r * math.sin(la))


def globe(name, r=6.0, loc=(0, 0, 0), step=1.5, face_lon=106.8):
    """globe gelap + titik daratan neon (peta global-land-mask) + garis lintang. Return dict root/pins.
    face_lon menghadap kamera (-Y) di awal."""
    from global_land_mask import globe as GL
    root = bpy.data.objects.new(name, None)
    lp._link(root)
    core = W.MB(name + "_core")
    core.sphere(0, 0, 0, r * .985, "globe_core")
    co = core.build(parent=root)
    V.glow(co, {"globe_core": .6})
    dots = W.MB(name + "_land")
    sz = r * .0055 * step
    lat = -58.0
    while lat <= 80:
        dl = step / max(.25, math.cos(math.radians(lat)))
        lon = -180.0
        while lon < 180:
            if GL.is_land(lat, lon):
                x, y, z = latlon(lat, lon, r)
                dots.box(x - sz, y - sz, z - sz, x + sz, y + sz, z + sz, "land_dot")
            lon += dl
        lat += step
    do = dots.build(parent=root)
    V.glow(do, {"land_dot": 3.2})
    rings = W.MB(name + "_rings")
    for la in range(-60, 61, 30):
        rr = r * math.cos(math.radians(la)) * 1.004
        zz = r * math.sin(math.radians(la))
        n = 72
        for i in range(n):
            a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            p0 = (rr * math.cos(a0), rr * math.sin(a0))
            p1 = (rr * math.cos(a1), rr * math.sin(a1))
            t = .025 * r / 6
            rings.poly([(p0[0], p0[1], zz - t), (p1[0], p1[1], zz - t), (p1[0], p1[1], zz + t),
                        (p0[0], p0[1], zz + t)], [(0, 1, 2, 3)], "n_purple")
    ro = rings.build(parent=root)
    V.glow(ro, {"n_purple": 2.5})
    root.location = loc
    root.rotation_euler.z = math.radians(-90 - face_lon)
    pins = {}
    for code, (la, lo) in CITIES.items():
        p = latlon(la, lo, r)
        pins[code] = p
    return {"root": root, "pins": pins, "r": r}


def pin_beam(name, root, p, r, h=2.4, key_="n_pink", em=6.0):
    """berkas cahaya radial dari titik kota di permukaan globe (anak root -> ikut berputar). Pivot di permukaan."""
    mb = W.MB(name)
    mb.cyl(0, 0, 0, h, .07 * r / 6, key_, n=8)
    mb.sphere(0, 0, h, .2 * r / 6, key_)
    mb.sphere(0, 0, 0, .16 * r / 6, key_)
    ob = mb.build(parent=root)
    V.glow(ob, {key_: em})
    ob.location = p
    n = [c / r for c in p]
    # arahkan sumbu z lokal ke normal permukaan
    ob.rotation_mode = "QUATERNION"
    from mathutils import Vector
    ob.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector(n))
    return ob


# ================================================================== bendera & pembeli
def flag_mb(mb, code, x, y, z, w=1.0):
    """bendera sederhana (sisi muka -Y) di bidang XZ; (x, z) = pojok kiri-bawah."""
    h = w * .66

    def r(a, b, c, d, k):
        mb.box(x + a * w, y, z + b * h, x + c * w, y + .04, z + d * h, k)

    def disc(cx, cz, rad, k, n=14):
        pts = [(x + cx * w + math.cos(2 * math.pi * i / n) * rad * w, z + cz * h + math.sin(2 * math.pi * i / n) * rad * w)
               for i in range(n)]
        mb.prism_y(pts, y - .01, y, k)

    if code == "ID":
        r(0, .5, 1, 1, "fl_red"); r(0, 0, 1, .5, "fl_white")
    elif code == "JP":
        r(0, 0, 1, 1, "fl_white"); disc(.5, .5, .18, "fl_red")
    elif code in ("US", "US2"):
        for i in range(7):
            r(0, i / 7, 1, (i + 1) / 7, "fl_red" if i % 2 == 0 else "fl_white")
        r(0, 3 / 7, .42, 1, "fl_navy")
    elif code == "BR":
        r(0, 0, 1, 1, "fl_green")
        mb.prism_y([(x + .1 * w, z + .5 * h), (x + .5 * w, z + .1 * h), (x + .9 * w, z + .5 * h), (x + .5 * w, z + .9 * h)],
                   y - .01, y, "fl_yellow")
        disc(.5, .5, .15, "fl_navy")
    elif code == "DE":
        r(0, 2 / 3, 1, 1, "fl_black"); r(0, 1 / 3, 1, 2 / 3, "fl_red"); r(0, 0, 1, 1 / 3, "fl_yellow")
    elif code == "FR":
        r(0, 0, 1 / 3, 1, "fl_blue"); r(1 / 3, 0, 2 / 3, 1, "fl_white"); r(2 / 3, 0, 1, 1, "fl_red")
    elif code == "MX":
        r(0, 0, 1 / 3, 1, "fl_green"); r(1 / 3, 0, 2 / 3, 1, "fl_white"); r(2 / 3, 0, 1, 1, "fl_red")
    elif code == "IN":
        r(0, 2 / 3, 1, 1, "fl_saff"); r(0, 1 / 3, 1, 2 / 3, "fl_white"); r(0, 0, 1, 1 / 3, "fl_green")
        disc(.5, .5, .07, "fl_navy")
    elif code == "NG":
        r(0, 0, 1 / 3, 1, "fl_green"); r(1 / 3, 0, 2 / 3, 1, "fl_white"); r(2 / 3, 0, 1, 1, "fl_green")
    elif code == "KR":
        r(0, 0, 1, 1, "fl_white"); disc(.5, .5, .16, "fl_red")
    elif code == "GB":
        r(0, 0, 1, 1, "fl_navy"); r(.42, 0, .58, 1, "fl_white"); r(0, .38, 1, .62, "fl_white")
        r(.46, 0, .54, 1, "fl_red"); r(0, .43, 1, .57, "fl_red")
    else:
        r(0, 0, 1, 1, "fl_white")


FLAGS = ["ID", "US", "JP", "BR", "DE", "FR", "KR", "MX", "IN", "NG", "GB"]


def buyer(name, k, loc, rot=0.0, code=None, flag=True):
    """pembeli (karakter kota) + bendera kecil di tiang (di tangan kanan, ikut badan)."""
    p = R.shopper(name, k, loc, rot)
    if flag and code:
        mb = W.MB(name + "_fl")
        mb.box(.42, -.03, 1.0, .47, .03, 3.25, "fl_black")
        flag_mb(mb, code, .47, -.02, 2.7, .72)
        fo = mb.build(parent=p["body"])
        fo.location = (0, 0, 0)
    return p


# ================================================================== kota Vice City
def deco_hotel(mb, x, y, w, d, h, col, trim, rnd):
    """hotel art-deco pastel: badan + mahkota bertingkat + jendela pita + garis neon (trim)."""
    mb.box(x, y, 0, x + w, y + d, h, col)
    mb.box(x + w * .25, y + d * .2, h, x + w * .75, y + d * .8, h + 1.6, col)
    mb.box(x + w * .4, y + d * .35, h + 1.6, x + w * .6, y + d * .65, h + 3.0, col)
    for zz in range(2, int(h) - 1, 3):
        mb.box(x + .5, y - .06, zz, x + w - .5, y, zz + 1.2, "ct_glass2")
    mb.box(x - .05, y - .1, h - .25, x + w + .05, y, h, trim)
    mb.box(x + w / 2 - .12, y - .12, 1.0, x + w / 2 + .12, y, h - .3, trim)


def palm_patch():
    """ganti pohon jalan diorama dengan palem (khas Vice City / Leonida)."""
    def _palm(mb, x, y, s, rnd):
        H.palm(mb, x, y, s * 1.25 * rnd.uniform(.9, 1.15), .1)
    V.C.street_tree = _palm


def vice_city(n, rnd_seed=6, people=True, store=True, hq=True, billboards=True, mascots=True, wide=(-74, -42, 74, 44),
              center_clear=22, traffic=True, crowd=0, flags=True, screens_imgs=None):
    """kota diorama Vice City lebar di dunia neon. Return dict komponen."""
    import scenes_vap as SV
    rnd = random.Random(rnd_seed)
    V.DIO = wide
    palm_patch()
    info = SV.city(n, focus=None, center_clear=center_clear, traffic=traffic, people=False)
    x0, y0, x1, y1 = wide
    # hotel art-deco pastel di baris belakang + tepi kanan/kiri
    b = W.MB("deco")
    trims = []
    xx = x0 + 2
    while xx < x1 - 8:
        w = rnd.uniform(7, 10)
        if abs(xx + w / 2) > 14 or not hq:
            h = rnd.uniform(9, 20)
            tk = rnd.choice(NEON_TRIM)
            trims.append(tk)
            deco_hotel(b, xx, y1 - 22, w, 7, h, rnd.choice(DECO), tk, rnd)
        xx += w + rnd.uniform(1.0, 2.5)
    bo = b.build()
    V.glow(bo, {k: 4.0 for k in NEON_TRIM})
    # palem di plaza & tepi diorama
    pm = W.MB("palms")
    for xx in range(int(x0) + 4, int(x1) - 2, 7):
        if abs(xx) < center_clear + 2:
            continue
        H.palm(pm, xx + rnd.uniform(-1, 1), 1.2 + rnd.uniform(-.4, .4), 1.1 * rnd.uniform(.9, 1.2), .24)
    for sx in (-1, 1):
        for yy in (-12, -6):
            H.palm(pm, sx * (center_clear - 1.5), yy, 1.15, .24)
    pm.build()
    out = {"info": info, "screens": [], "hq": None, "store": None, "queue": []}
    if hq:
        out["hq"] = rockstar_hq("hq", (0, y1 - 18, .1))
    if billboards:
        imgs = screens_imgs or SHOTS
        spots = [(-40, y1 - 23.5, 23.0, 16, 9), (40, y1 - 23.5, 25.0, 16, 9), (-62, y1 - 23.5, 20.0, 12, 6.75),
                 (62, y1 - 23.5, 21.0, 12, 6.75)]
        for i, (x, y, z, w, h) in enumerate(spots):
            seq = [imgs[(i * 3 + j) % len(imgs)] for j in range(3)]
            sc = screen(f"bb{i}", seq, w, h, (x, y, z), 0, n_frames=n + 8, em=2.2,
                        frame=NEON_TRIM[i % 4])
            # tiang
            mb = W.MB(f"bbp{i}")
            mb.box(x - .4, y + .2, 0, x + .4, y + 1.0, z - h / 2, "bd_dark")
            mb.build()
            out["screens"].append(sc)
    if mascots:
        for i, (m, x, z, hh) in enumerate((("m_flamingo", -28, 17, 7), ("m_gator", 28, 17, 7.5),
                                           ("m_sun", -52, 25, 6), ("m_palm", 52, 23, 7))):
            img_plane(f"masc{i}", m, h=hh, loc=(x, y1 - 23.0, z), em=1.4)
    if store:
        out["store"] = game_store("gs", (0, 4, .24))
    if crowd:
        out["queue"] = queue(crowd, (0, -2.5), flags=flags, rnd=rnd)
    return out


def rockstar_hq(name, loc):
    """menara kantor Rockstar: kaca biru-ungu + mahkota + logo R* 3D raksasa di puncak + papan nama neon."""
    x, y, z = loc
    mb = W.MB(name)
    mb.box(x - 7, y - 5, z, x + 7, y + 5, z + 26, "hq_glass")
    mb.box(x - 5.5, y - 4, z + 26, x + 5.5, y + 4, z + 30, "hq_glass2")
    for zz in range(2, 26, 3):
        mb.box(x - 7.05, y - 5.06, z + zz, x + 7.05, y - 5.0, z + zz + .25, "n_gold")
    ob = mb.build()
    V.glow(ob, {"n_gold": 3.0})
    logo = rockstar_logo(name + "_logo", 8.0, (x, y - 5.6, z + 35.5), em=1.6)
    t, fo = V.neon_sign(name + "_sign", "ROCKSTAR GAMES", (x, y - 5.4, z + 3.0), .9, "n_gold", 6.0)
    return {"body": ob, "logo": logo, "sign": t}


def game_store(name, loc, w=16.0, d=10.0, sign="GAME STORE"):
    """toko game malam-neon: etalase kaca, poster GTA VI resmi, rak kotak game."""
    x, y, z = loc
    mb = W.MB(name)
    mb.box(x - w / 2, y, z, x + w / 2, y + d, z + 6.5, "store_wall")
    mb.box(x - w / 2 - .3, y - .3, z + 6.5, x + w / 2 + .3, y + d + .3, z + 7.1, "store_wall2")
    mb.box(x - w / 2, y - .12, z + 5.2, x + w / 2, y, z + 5.45, "n_pink")
    mb.box(x - w / 2, y - .12, z, x - w / 2 + .25, y, z + 5.2, "n_cyan")
    mb.box(x + w / 2 - .25, y - .12, z, x + w / 2, y, z + 5.2, "n_cyan")
    ob = mb.build()
    V.glow(ob, {"n_pink": 5.0, "n_cyan": 5.0})
    t, fo = V.neon_sign(name + "_sign", sign, (x, y - .2, z + 7.4), .85, "n_pink", 7.0)
    post = img_plane(name + "_post", "cover", h=4.4, loc=(x - 4.6, y - .14, z + .5), em=1.3)
    post2 = img_plane(name + "_post2", "jl_tall", h=4.4, loc=(x + 4.6, y - .14, z + .5), em=1.3)
    # rak kotak game di dalam etalase
    base = game_case(name + "_c0", "cover_ps5", .55, (x - 1.6, y + 1.2, z + .6))
    shelf = [base]
    for row in range(3):
        for col in range(7):
            if row == 0 and col == 0:
                continue
            shelf.append(dup(base, f"{name}_c{row}_{col}", (x - 1.6 + (col - 3) * .82 + 1.6, y + 1.2, z + .6 + row * 1.35)))
    mb = W.MB(name + "_shelf")
    for row in range(3):
        mb.box(x - 3.2, y + .8, z + .45 + row * 1.35, x + 3.2, y + 1.8, z + .6 + row * 1.35, "bd_dark")
    mb.build()
    return {"body": ob, "sign": t, "posters": [post, post2], "cases": shelf}


def queue(n, front=(0, -2.5), flags=True, rnd=None, spacing=1.35):
    """antrean pembeli berbendera mengular ke depan toko."""
    rnd = rnd or random.Random(3)
    out = []
    x, y = front
    pts = []
    for i in range(n):
        row = i // 9
        col = i % 9
        xx = x + (col - 4) * spacing * (1 if row % 2 == 0 else -1)
        yy = y - row * 2.0
        pts.append((xx, yy))
    for i, (xx, yy) in enumerate(pts):
        code = FLAGS[i % len(FLAGS)] if flags and i % 2 == 0 else None
        p = buyer(f"q{i}", i + 2, (xx + rnd.uniform(-.2, .2), yy, .24), rnd.uniform(-.3, .3), code)
        out.append(p)
    return out


# ================================================================== perangkat
def ps5(name, loc=(0, 0, 0), s=1.0):
    """konsol PS5 berdiri (siluet sayap putih + inti hitam)."""
    mb = W.MB(name)
    h = 4.0 * s
    mb.box(-.45 * s, -1.0 * s, 0, .45 * s, 1.0 * s, h * .97, "ps_black")
    pts = [(-1.15 * s, 0), (1.15 * s, 0), (1.35 * s, h * .55), (1.05 * s, h), (-1.05 * s, h), (-1.3 * s, h * .5)]
    mb.prism_x(pts, .45 * s, .62 * s, "ps_white")
    mb.prism_x(pts, -.62 * s, -.45 * s, "ps_white")
    mb.box(-.45 * s, -1.02 * s, h * .1, .45 * s, -1.0 * s, h * .14, "n_cyan")
    ob = mb.build(loc)
    V.glow(ob, {"n_cyan": 5.0, "ps_white": .9})
    return ob


def pc_tower(name, loc=(0, 0, 0), s=1.0, lit=True):
    """PC gaming: casing gelap + panel kaca + kipas RGB + monitor."""
    mb = W.MB(name)
    mb.box(-.9 * s, -1.6 * s, 0, .9 * s, 1.6 * s, 3.6 * s, "pc_case")
    mb.box(-.92 * s, -1.4 * s, .3 * s, -.9 * s, 1.4 * s, 3.3 * s, "ct_glass2")
    for k in range(3):
        mb.disc_y(-.94 * s, 0, (.9 + k * 1.0) * s, .38 * s, .04, "n_purple" if lit else "bd_dark")
    ob = mb.build(loc)
    if lit:
        V.glow(ob, {"n_purple": 4.0})
    ob.rotation_euler.z = math.pi / 2
    return ob


def padlock(name, loc=(0, 0, 0), s=1.0, key_="n_gold", em=4.0):
    mb = W.MB(name)
    L_ = __import__("world_laundry")
    L_.rbox(mb, -1.0 * s, -.35 * s, 0, 1.0 * s, .35 * s, 1.5 * s, "ic_metal", c=.12 * s)
    n = 16
    for i in range(n):
        a0, a1 = math.pi * i / n, math.pi * (i + 1) / n
        r0, r1 = .65 * s, .85 * s
        pts = [(math.cos(a0) * r0, 1.5 * s + math.sin(a0) * r0 * 1.3), (math.cos(a0) * r1, 1.5 * s + math.sin(a0) * r1 * 1.3),
               (math.cos(a1) * r1, 1.5 * s + math.sin(a1) * r1 * 1.3), (math.cos(a1) * r0, 1.5 * s + math.sin(a1) * r0 * 1.3)]
        mb.prism_y(pts, -.15 * s, .15 * s, key_)
    mb.disc_y(0, -.36 * s, .75 * s, .2 * s, .04, "bd_dark")
    ob = mb.build(loc)
    V.glow(ob, {key_: em})
    return ob
