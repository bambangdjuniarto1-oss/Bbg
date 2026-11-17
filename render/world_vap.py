"""Aset 3D video "Bedah Bisnis: Liquid Vape" — gaya sinematik neon (lantai grid gelap mengilap, kubah
langit ungu-pink, cahaya neon), mengikuti nuansa video referensi. Semua generik, tanpa logo merek.

Isi: panggung neon, botol liquid 60 ml (isi berlapis = porsi harga), pita cukai, pilar kaca bercahaya,
toko vape, pabrik brand, gedung negara, ikon biaya, gerbang cukai, sirine, rak pasar, diagram pai,
ponsel, pesawat kertas, mahkota, tanda tanya/silang.
"""
import math
import random

import bpy

import lowpoly as lp
import world as W
import world_hotel as H
import world_laundry as L
import world_amdk as M
import world_ctd as C
import world_pst as P

lp.PAL.update({
    "vp_floor": "#0B0712", "vp_grid": "#A23CFF", "vp_grid2": "#FF3FA4", "vp_dome": "#170A2A",
    "vp_dome2": "#FF4FA0", "vp_dome3": "#5B1F9E",
    "n_pink": "#FF3FA4", "n_cyan": "#2CE6FF", "n_purple": "#9D4DFF", "n_gold": "#FFB21F", "n_red": "#FF2D4B",
    "n_green": "#3DFF9A", "n_white": "#F5F0FF", "n_orange": "#FF7A2E",
    # liquid: porsi harga
    "lq_toko": "#1FD3F0", "lq_brand": "#A45CFF", "lq_negara": "#FFB000", "lq_pink": "#FF4FA8",
    "lq_cheap": "#7CFF5A", "lq_amber": "#FF8A2E",
    # botol
    "bt_glass": "#2A1A44", "bt_cap": "#141218", "bt_cap2": "#26222E", "bt_label": "#F2ECF8", "bt_label2": "#FF3FA4",
    "pc_paper": "#E8EEF4", "pc_blue": "#2F6FD0", "pc_green": "#2FA36B", "pc_red": "#D23A48",
    # bangunan
    "bd_dark": "#231436", "bd_dark2": "#2E1A47", "bd_trim": "#3B2459", "bd_glass": "#3A2A66",
    "gv_wall": "#E7E1F2", "gv_col": "#F4F0FA", "gv_roof": "#CFC5E0", "gv_step": "#B7ADC9",
    "pl_glass": "#FF3FA4",
    "ic_metal": "#9AA0B4", "ic_dark": "#2A2833", "ic_box": "#C98B4E", "ic_tape": "#E8C27A",
    "ph_body": "#16131D", "ph_screen": "#20183A", "ph_bub": "#F5F0FF", "ph_bub2": "#9D4DFF",
    "plane": "#F5F0FF", "gate_post": "#3A3448", "gate_red": "#E8323F", "gate_wht": "#F2F2F2",
    "shelf_dk": "#1E1430", "x_red": "#FF2D4B",
})

GLOW = {}


def glow(ob, keys, strength=None):
    """jadikan material ber-key tertentu berpendar. keys: {key: kekuatan} atau list + strength."""
    if not isinstance(keys, dict):
        keys = {k: strength for k in keys}
    me = ob.data
    for i, m in enumerate(me.materials):
        if m is None:
            continue
        k = m.name.split("_", 1)[1].rsplit("_", 1)[0]
        if k in keys:
            me.materials[i] = lp.mat(k, emission=keys[k])
    return ob


def set_mat(ob, m):
    ob.data.materials.clear()
    ob.data.materials.append(m)
    return ob


def emis(key_, s):
    return lp.mat(key_, emission=s)


# ------------------------------------------------------------------ material khusus
def glossy_floor():
    m = bpy.data.materials.get("vp_floor_m")
    if m:
        return m
    m = bpy.data.materials.new("vp_floor_m")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = lp.hex_rgba(lp.PAL["vp_floor"])
    b.inputs["Roughness"].default_value = .22
    b.inputs["Specular IOR Level"].default_value = .7
    b.inputs["Metallic"].default_value = .35
    return m


def fade_emit(name, key_, strength, center=(0, 0), r0=10.0, r1=60.0):
    """emisi yang memudar menjauhi `center` (garis grid hilang di kejauhan)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = lp.hex_rgba(lp.PAL[key_])
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sub = nt.nodes.new("ShaderNodeVectorMath")
    sub.operation = "SUBTRACT"
    sub.inputs[1].default_value = (center[0], center[1], 0)
    ln = nt.nodes.new("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = r0
    mr.inputs["From Max"].default_value = r1
    mr.inputs["To Min"].default_value = strength
    mr.inputs["To Max"].default_value = 0.0
    nt.links.new(geo.outputs["Position"], sub.inputs[0])
    nt.links.new(sub.outputs[0], ln.inputs[0])
    nt.links.new(ln.outputs["Value"], mr.inputs["Value"])
    nt.links.new(mr.outputs[0], em.inputs["Strength"])
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m


def dome_mat():
    """kubah langit: bawah (cakrawala) pink-ungu menyala, atas gelap."""
    m = bpy.data.materials.get("vp_dome_m")
    if m:
        return m
    m = bpy.data.materials.new("vp_dome_m")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.elements[0].position = 0.0
    cr.elements[0].color = lp.hex_rgba(lp.PAL["vp_dome2"])
    cr.elements[1].position = .55
    cr.elements[1].color = lp.hex_rgba(lp.PAL["vp_dome"])
    e = cr.elements.new(.16)
    e.color = lp.hex_rgba(lp.PAL["vp_dome3"])
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
    em.inputs["Strength"].default_value = 1.0
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m


def glass_tint(key_="bt_glass", fac=.55, name=None):
    """kaca/plastik berwarna: sebagian tembus + kilap."""
    name = name or f"vp_glass_{key_}_{fac}"
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = lp.hex_rgba(lp.PAL[key_])
    b.inputs["Roughness"].default_value = .08
    b.inputs["Specular IOR Level"].default_value = .8
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs["Fac"].default_value = 1 - fac
    out = nt.nodes["Material Output"]
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(b.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def glow_glass(key_, strength=1.2, fac=.45):
    """kaca berpendar (isi pilar): tembus sebagian + emisi."""
    name = f"vp_gg_{key_}_{strength}_{fac}"
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    add = nt.nodes.new("ShaderNodeAddShader")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = lp.hex_rgba(lp.PAL[key_])
    em.inputs["Strength"].default_value = strength
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs["Fac"].default_value = fac
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


# ------------------------------------------------------------------ panggung
def setup_neon_light(world_str=.35):
    """lampu dasar: tanpa matahari terang; langit ungu gelap."""
    sc = bpy.context.scene
    for ob in list(bpy.data.objects):
        if ob.type == "LIGHT" and ob.data.type == "SUN":
            ob.data.energy = .5
            ob.data.color = (.75, .7, 1.0)
            ob.rotation_euler = (math.radians(50), 0, math.radians(-30))
    bg = sc.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = lp.hex_rgba("#1A0C2E")
    bg.inputs["Strength"].default_value = world_str
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.cycles.glossy_bounces = 2
    sc.cycles.max_bounces = 4


def stage(name="stg", center=(0, 0), size=70.0, sp=2.0, grid_key="vp_grid", grid_em=2.2, fade=(8.0, 40.0),
          dome=True, dome_r=180.0):
    """lantai gelap mengilap + grid neon memudar + kubah cakrawala."""
    cx, cy = center
    fl = W.MB(name + "_floor")
    fl.box(cx - size, cy - size, -.2, cx + size, cy + size, 0, "vp_floor")
    f = fl.build()
    set_mat(f, glossy_floor())
    g = W.MB(name + "_grid")
    n = int(size / sp)
    t = .035
    for i in range(-n, n + 1):
        g.box(cx + i * sp - t, cy - size, 0, cx + i * sp + t, cy + size, .004, grid_key)
        g.box(cx - size, cy + i * sp - t, 0, cx + size, cy + i * sp + t, .004, grid_key)
    go = g.build()
    set_mat(go, fade_emit(name + "_gm", grid_key, grid_em, center, *fade))
    P.no_light(go)
    out = {"floor": f, "grid": go}
    if dome:
        d = W.MB(name + "_dome")
        d.cyl(cx, cy, -2, 70, dome_r, "vp_dome", n=48)
        do = d.build()
        set_mat(do, dome_mat())
        P.no_light(do)
        do.visible_shadow = False
        out["dome"] = do
    return out


def area(name, loc, aim, energy=800.0, size=6.0, color=(1, 1, 1)):
    li = bpy.data.lights.new(name, "AREA")
    li.energy = energy
    li.size = size
    li.color = color
    ob = bpy.data.objects.new(name, li)
    lp._link(ob)
    ob.location = loc
    d = (aim[0] - loc[0], aim[1] - loc[1], aim[2] - loc[2])
    ob.rotation_euler = (math.atan2(math.hypot(d[0], d[1]), -d[2]), 0, math.atan2(d[1], d[0]) + math.pi / 2)
    return ob


def rig(center=(0, 0, 0), key_e=2200.0, rim=1500.0, s=1.0):
    """3 lampu khas: atas putih-pink (kunci), kiri cyan, kanan pink."""
    x, y, z = center
    out = [P.spot("key", (x + 3 * s, y - 6 * s, z + 16 * s), (x, y, z), key_e, 50, (1, .88, .96), .5),
           area("rimL", (x - 9 * s, y + 4 * s, z + 6 * s), (x, y, z + 1), rim, 6 * s, (.35, .9, 1.0)),
           area("rimR", (x + 9 * s, y + 4 * s, z + 6 * s), (x, y, z + 1), rim, 6 * s, (1.0, .3, .7))]
    return out


def pulse_light(li, f0, f1, period=15, lo=.4, hi=1.0):
    e = li.data.energy
    f = f0
    while f <= f1:
        li.data.energy = e * hi
        li.data.keyframe_insert("energy", frame=int(f))
        li.data.energy = e * lo
        li.data.keyframe_insert("energy", frame=int(f + period / 2))
        f += period


# ------------------------------------------------------------------ botol liquid
BOT_H = 2.2           # tinggi badan botol (s=1)
BOT_R = 1.0
FILL = (.12, 2.0)     # dasar & batas atas isi


def bottle(name, s=1.0, layers=(("lq_pink", 1.0),), label=True, pita=False, cheap=False, liquid_em=1.3,
           loc=(0, 0, 0)):
    """botol liquid 60 ml generik (badan bulat + tutup ulir hitam berujung runcing), menghadap -Y.
    layers: [(key, porsi)] dari bawah; isi berpendar sedikit. Kembali dict: root, layers[], cap, pita, label."""
    root = bpy.data.objects.new(name, None)
    lp._link(root)
    root.location = loc
    root.scale = (s, s, s)
    # badan (kaca/plastik berwarna)
    b = W.MB(name + "_body")
    prof = [(0, 0), (.92, 0), (1.0, .08), (1.0, BOT_H), (.92, BOT_H + .22), (.6, BOT_H + .42), (.42, BOT_H + .48),
            (.42, BOT_H + .6), (0, BOT_H + .6)]
    M.lathe(b, 0, 0, 0, prof, "bt_glass", n=28)
    body = b.build(parent=root)
    set_mat(body, glass_tint("bt_glass", .32))
    # isi berlapis
    lay = []
    tot = sum(p for _, p in layers)
    z = FILL[0]
    for i, (k, p) in enumerate(layers):
        h = (FILL[1] - FILL[0]) * p / tot
        mb = W.MB(f"{name}_lq{i}")
        M.lathe(mb, 0, 0, 0, [(0, 0), (.9, 0), (.9, h), (0, h)], k, n=28)
        ob = mb.build((0, 0, z), parent=root)
        set_mat(ob, emis(k, liquid_em))
        lay.append(ob)
        z += h
    # tutup ulir + ujung tetes
    c = W.MB(name + "_cap")
    cz = BOT_H + .5
    M.lathe(c, 0, 0, cz, [(0, 0), (.62, 0), (.62, .72), (.5, .8), (0, .8)], "bt_cap", n=24)
    for k in range(18):
        a = 2 * math.pi * k / 18
        c.boxc(.62 * math.cos(a), .62 * math.sin(a), cz + .06, .07, .07, .6, "bt_cap2")
    M.lathe(c, 0, 0, cz + .8, [(.26, 0), (.2, .35), (.07, .75), (0, .78)], "bt_cap", n=16)
    cap = c.build(parent=root)
    out = {"root": root, "body": body, "layers": lay, "cap": cap, "pita": None, "label": None}
    if label:
        lb = W.MB(name + "_lab")
        # pita label melingkar di bagian bawah badan (isi tetap terlihat di atasnya)
        n = 28
        for k in range(n):
            a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
            r = 1.012
            lb.poly([(r * math.cos(a0), r * math.sin(a0), .28), (r * math.cos(a1), r * math.sin(a1), .28),
                     (r * math.cos(a1), r * math.sin(a1), .82), (r * math.cos(a0), r * math.sin(a0), .82)],
                    [(0, 1, 2, 3)], "bt_label")
        for k in range(n):
            a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
            r = 1.016
            lb.poly([(r * math.cos(a0), r * math.sin(a0), .74), (r * math.cos(a1), r * math.sin(a1), .74),
                     (r * math.cos(a1), r * math.sin(a1), .82), (r * math.cos(a0), r * math.sin(a0), .82)],
                    [(0, 1, 2, 3)], "bt_label2")
        lab = lb.build(parent=root)
        glow(lab, {"bt_label2": 2.0})
        t = H.text(name + "_lt", "60 ML", .3, "bt_cap", depth=.02, loc=(0, -1.02, .38))
        t.parent = root
        out["label"] = lab
    if pita:
        out["pita"] = pita_cukai(name + "_pc", root)
    return out


def pita_cukai(name, parent=None, s=1.0):
    """pita cukai generik: pita kertas melintang di atas tutup (turun di kedua sisi), garis biru-hijau."""
    mb = W.MB(name)
    w = .34
    cz = BOT_H + .5
    top = cz + .8
    r = .64
    t = .025
    # sisi depan (-Y), atas, sisi belakang
    mb.box(-w / 2, -r - t, cz - .35, w / 2, -r, top, "pc_paper")
    mb.box(-w / 2, -r - t, top, w / 2, r + t, top + t, "pc_paper")
    mb.box(-w / 2, r, cz - .35, w / 2, r + t, top, "pc_paper")
    for dz, k in ((.12, "pc_blue"), (.3, "pc_green"), (.48, "pc_blue")):
        mb.box(-w / 2 + .02, -r - t - .004, cz - .35 + dz, w / 2 - .02, -r - t, cz - .35 + dz + .07, k)
    mb.box(-.05, -r - t - .006, cz + .45, .05, -r - t, cz + .6, "pc_red")
    ob = mb.build(parent=parent)
    ob.scale = (s, s, s)
    return ob


def bottle_mb(mb, x, y, z, s, liq, cap="bt_cap", fill=.8):
    """botol sederhana (satu mesh) untuk rak/barisan banyak botol."""
    M.lathe(mb, x, y, z, [(0, 0), (.92 * s, 0), (s, .08 * s), (s, BOT_H * s), (.6 * s, (BOT_H + .4) * s),
                         (.42 * s, (BOT_H + .5) * s), (0, (BOT_H + .5) * s)], "bt_glass", n=12)
    M.lathe(mb, x, y, z, [(0, .1 * s), (1.02 * s, .1 * s), (1.02 * s, (.1 + 2 * fill) * s),
                         (0, (.1 + 2 * fill) * s)], liq, n=12)
    M.lathe(mb, x, y, z + (BOT_H + .5) * s, [(0, 0), (.6 * s, 0), (.6 * s, .7 * s), (.25 * s, .8 * s),
                                             (.06 * s, 1.4 * s), (0, 1.42 * s)], cap, n=10)


# ------------------------------------------------------------------ pilar kaca bercahaya (ala referensi)
def pillar(name, h, w=2.4, d=2.4, key_="n_pink", em=1.6, frame_em=5.0, loc=(0, 0, 0), cap=True):
    """kolom kaca berpendar + rangka tepi neon. Berporos di dasar (tumbuh dengan scale z)."""
    root = bpy.data.objects.new(name, None)
    lp._link(root)
    root.location = loc
    inner = W.MB(name + "_in")
    inner.box(-w / 2, -d / 2, 0, w / 2, d / 2, h, key_)
    io = inner.build(parent=root)
    set_mat(io, glow_glass(key_, em, .55))
    P.no_light(io)
    fr = W.MB(name + "_fr")
    t = .07
    for sx in (-1, 1):
        for sy in (-1, 1):
            fr.box(sx * w / 2 - t, sy * d / 2 - t, 0, sx * w / 2 + t, sy * d / 2 + t, h, key_)
    for zz in ((0, t), (h - t, h)) if cap else ((0, t),):
        for sy in (-1, 1):
            fr.box(-w / 2, sy * d / 2 - t, zz[0], w / 2, sy * d / 2 + t, zz[1], key_)
        for sx in (-1, 1):
            fr.box(sx * w / 2 - t, -d / 2, zz[0], sx * w / 2 + t, d / 2, zz[1], key_)
    fo = fr.build(parent=root)
    set_mat(fo, emis(key_, frame_em))
    return root


def base_plate(name, w, d, key_="n_pink", loc=(0, 0, 0), em=4.0):
    """alas tipis + garis tepi berpendar di lantai."""
    mb = W.MB(name)
    mb.box(-w / 2, -d / 2, 0, w / 2, d / 2, .12, "bd_dark")
    t = .06
    mb.box(-w / 2 - t, -d / 2 - t, 0, w / 2 + t, -d / 2 + t, .14, key_)
    mb.box(-w / 2 - t, d / 2 - t, 0, w / 2 + t, d / 2 + t, .14, key_)
    mb.box(-w / 2 - t, -d / 2, 0, -w / 2 + t, d / 2, .14, key_)
    mb.box(w / 2 - t, -d / 2, 0, w / 2 + t, d / 2, .14, key_)
    ob = mb.build(loc)
    glow(ob, {key_: em})
    return ob


def disc_ped(name, r=2.2, key_="n_pink", loc=(0, 0, 0), em=4.0, h=.5):
    mb = W.MB(name)
    mb.cyl(0, 0, 0, h, r, "bd_dark2", n=40)
    mb.cyl(0, 0, h, h + .04, r * .98, "bd_dark", n=40)
    ob = mb.build(loc)
    rg = ring_obj(name + "_ring", (loc[0], loc[1], loc[2] + h + .045), r * .98, .08, key_, em)
    rg2 = ring_obj(name + "_ring2", (loc[0], loc[1], loc[2] + .02), r + .02, .06, key_, em * .6, flat=False, h=h - .04)
    return ob, rg, rg2


def ring_obj(name, loc, r, w, key_, em, n=48, flat=True, h=.0):
    mb = W.MB(name)
    if flat:
        vs = []
        for i in range(n):
            a = 2 * math.pi * i / n
            vs += [(math.cos(a) * (r - w), math.sin(a) * (r - w), 0), (math.cos(a) * r, math.sin(a) * r, 0)]
        fs = [(2 * i, 2 * ((i + 1) % n), 2 * ((i + 1) % n) + 1, 2 * i + 1) for i in range(n)]
        mb.poly(vs, fs, key_)
    else:
        mb.cyl(0, 0, h - w, h, r, key_, n=n)
    ob = mb.build(loc)
    set_mat(ob, emis(key_, em))
    return ob


# ------------------------------------------------------------------ bangunan
def vape_shop(name, loc=(0, 0, 0), w=9.0, d=6.0, h=5.6, sign="TOKO VAPE"):
    """toko vape generik: dinding gelap, etalase kaca berisi rak botol berpendar, papan neon."""
    mb = W.MB(name)
    t = .3
    mb.box(-w / 2, -d / 2, 0, w / 2, d / 2, .2, "bd_trim")
    mb.box(-w / 2, d / 2 - t, 0, w / 2, d / 2, h, "bd_dark")
    mb.box(-w / 2, -d / 2, 0, -w / 2 + t, d / 2, h, "bd_dark")
    mb.box(w / 2 - t, -d / 2, 0, w / 2, d / 2, h, "bd_dark")
    mb.box(-w / 2, -d / 2, h - 1.5, w / 2, d / 2, h, "bd_dark2")      # fasad atas (papan)
    mb.box(-w / 2 - .1, -d / 2 - .1, h, w / 2 + .1, d / 2 + .1, h + .25, "bd_trim")
    mb.box(-w / 2, -d / 2, 0, w / 2, -d / 2 + .25, .5, "bd_dark2")     # ambang etalase
    for x in (-w / 2 + .15, -1.1, 1.1, w / 2 - .15):
        mb.box(x - .08, -d / 2, .5, x + .08, -d / 2 + .2, h - 1.5, "bd_trim")
    # rak dalam + botol-botol berpendar
    sh = W.MB(name + "_sh")
    cols = ["lq_pink", "lq_toko", "lq_brand", "lq_negara", "lq_cheap", "lq_amber"]
    rnd = random.Random(3)
    for k, zz in enumerate((.8, 1.8, 2.8)):
        sh.box(-w / 2 + .4, d / 2 - 1.2, zz - .06, w / 2 - .4, d / 2 - .4, zz, "shelf_dk")
        for i in range(14):
            x = -w / 2 + .8 + i * (w - 1.6) / 13
            bottle_mb(sh, x, d / 2 - .8, zz, .17, rnd.choice(cols))
    so = sh.build(loc)
    glow(so, {c: 2.2 for c in cols})
    body = mb.build(loc)
    gl = W.MB(name + "_gl")
    gl.box(-w / 2 + .3, -d / 2 + .1, .5, w / 2 - .3, -d / 2 + .14, h - 1.5, "bd_glass")
    go = gl.build(loc)
    set_mat(go, glass_tint("bd_glass", .18))
    # trim neon atap & papan
    tr = W.MB(name + "_trim")
    tr.box(-w / 2 - .12, -d / 2 - .14, h + .25, w / 2 + .12, -d / 2 - .06, h + .35, "n_cyan")
    tr.box(-w / 2 - .12, -d / 2 - .14, h - 1.55, w / 2 + .12, -d / 2 - .06, h - 1.47, "n_cyan")
    to = tr.build(loc)
    glow(to, {"n_cyan": 6.0})
    sg = H.text(name + "_sign", sign, .9, "n_pink", depth=.12,
                loc=(loc[0], loc[1] - d / 2 - .12, loc[2] + h - 1.2), emission=7.0)
    li = P.point(name + "_li", (loc[0], loc[1], loc[2] + 2.8), 600, (1, .5, .85), 2.0)
    return {"body": body, "shelf": so, "glass": go, "trim": to, "sign": sg, "light": li}


def brand_factory(name, loc=(0, 0, 0), sign="BRAND"):
    """pabrik/lab brand: gedung bergerigi + tangki + papan neon ungu."""
    mb = W.MB(name)
    w, d = 12.0, 8.0
    mb.box(-w / 2, -d / 2, 0, w / 2, d / 2, 5.0, "bd_dark")
    for k in range(4):
        x0 = -w / 2 + k * w / 4
        mb.prism_y([(x0, 5.0), (x0 + w / 4, 5.0), (x0 + w / 4, 6.6)], -d / 2, d / 2, "bd_dark2")
    for k in range(5):
        x = -w / 2 + 1.2 + k * 2.4
        mb.box(x - .7, -d / 2 - .05, 1.2, x + .7, -d / 2, 3.6, "bd_glass")
    for k, (x, y) in enumerate(((w / 2 + 1.8, -1.2), (w / 2 + 1.8, 1.8))):
        mb.cyl(x, y, 0, 6.5, 1.3, "bd_trim", n=20)
        mb.cyl(x, y, 6.5, 7.2, 1.3, "bd_dark2", n=20, r_top=.4)
    mb.cyl(-w / 2 + 1.5, d / 2 - 1.5, 5, 10, .5, "bd_trim", n=12)
    ob = mb.build(loc)
    glow(ob, {"bd_glass": 1.6})
    tr = W.MB(name + "_trim")
    tr.box(-w / 2, -d / 2 - .12, 4.9, w / 2, -d / 2 - .04, 5.02, "n_purple")
    tr.box(-w / 2 - .06, -d / 2 - .1, 0, -w / 2 + .06, -d / 2 - .02, 5.0, "n_purple")
    tr.box(w / 2 - .06, -d / 2 - .1, 0, w / 2 + .06, -d / 2 - .02, 5.0, "n_purple")
    for x, y in ((w / 2 + 1.8, -1.2), (w / 2 + 1.8, 1.8)):
        tr.cyl(x, y, 3.0, 3.15, 1.33, "n_purple", n=20)
    to = tr.build(loc)
    glow(to, {"n_purple": 6.0})
    sg = H.text(name + "_sign", sign, 1.1, "n_purple", depth=.14,
                loc=(loc[0], loc[1] - d / 2 - .15, loc[2] + 3.7), emission=7.0)
    return {"body": ob, "trim": to, "sign": sg}


def gov_building(name, loc=(0, 0, 0), sign="NEGARA", s=1.0):
    """gedung negara generik bergaya klasik: tangga, 6 kolom, atap segitiga, aksen emas berpendar."""
    mb = W.MB(name)
    w, d = 12.0, 7.0
    for k in range(3):
        mb.box(-w / 2 - 1.2 + k * .4, -d / 2 - 1.6 + k * .45, k * .3, w / 2 + 1.2 - k * .4, d / 2 + .5, (k + 1) * .3,
               "gv_step")
    z0 = .9
    mb.box(-w / 2 + .6, -d / 2 + 1.2, z0, w / 2 - .6, d / 2, z0 + 5.0, "gv_wall")
    for k in range(6):
        x = -w / 2 + 1.1 + k * (w - 2.2) / 5
        mb.cyl(x, -d / 2 + .3, z0, z0 + 5.0, .38, "gv_col", n=14)
        mb.box(x - .5, -d / 2 - .2, z0, x + .5, -d / 2 + .8, z0 + .2, "gv_step")
        mb.box(x - .5, -d / 2 - .2, z0 + 4.8, x + .5, -d / 2 + .8, z0 + 5.0, "gv_step")
    mb.box(-w / 2, -d / 2 - .3, z0 + 5.0, w / 2, d / 2, z0 + 5.8, "gv_roof")
    mb.prism_y([(-w / 2, z0 + 5.8), (w / 2, z0 + 5.8), (0, z0 + 8.0)], -d / 2 - .3, d / 2, "gv_roof")
    mb.box(-1.0, -d / 2 + 1.15, z0, 1.0, -d / 2 + 1.2, z0 + 3.0, "n_gold")
    ob = mb.build(loc)
    ob.scale = (s, s, s)
    glow(ob, {"n_gold": 3.0})
    tr = W.MB(name + "_trim")
    tr.box(-w / 2, -d / 2 - .36, z0 + 5.05, w / 2, -d / 2 - .3, z0 + 5.15, "n_gold")
    tr.prism_y([(-w / 2, z0 + 5.8), (w / 2, z0 + 5.8), (w / 2 - .25, z0 + 5.95), (0, z0 + 8.1), (-w / 2 + .25, z0 + 5.95)],
               -d / 2 - .36, -d / 2 - .3, "n_gold")
    to = tr.build(loc)
    to.scale = (s, s, s)
    glow(to, {"n_gold": 5.0})
    sg = H.text(name + "_sign", sign, .85 * s, "n_gold", depth=.1,
                loc=(loc[0], loc[1] + (-d / 2 - .38) * s, loc[2] + (z0 + 5.15) * s), emission=6.0)
    return {"body": ob, "trim": to, "sign": sg}


# ------------------------------------------------------------------ ikon
def icon(name, kind, s=1.0, loc=(0, 0, 0), em=3.0):
    """ikon biaya neon: bahan (labu kimia), botol, produksi (roda gigi), distribusi (kardus), marketing
    (megafon). Berdiri di z=0, menghadap -Y."""
    mb = W.MB(name)
    col = {"bahan": "n_green", "botol": "n_cyan", "produksi": "n_orange", "distribusi": "n_gold",
           "marketing": "n_pink"}[kind]
    if kind == "bahan":
        M.lathe(mb, 0, 0, 0, [(0, 0), (1.0, 0), (1.05, .2), (.35, 1.4), (.35, 2.0), (.45, 2.1), (0, 2.1)],
                "bt_glass", n=18)
        M.lathe(mb, 0, 0, 0, [(0, .05), (.98, .05), (.62, .75), (0, .75)], col, n=18)
    elif kind == "botol":
        bottle_mb(mb, 0, 0, 0, .62, col)
    elif kind == "produksi":
        n = 10
        pts = []
        for i in range(n * 2):
            a = math.pi * i / n
            r = 1.05 if i % 2 == 0 else .8
            for da in (-.12, .12):
                pts.append((math.cos(a + da) * r, 1.1 + math.sin(a + da) * r))
        mb.prism_y(pts, -.2, .2, "ic_metal")
        mb.disc_y(0, -.22, 1.1, .32, .05, col, n=16)
    elif kind == "distribusi":
        L.rbox(mb, -1.0, -.8, 0, 1.0, .8, 1.5, "ic_box", c=.05)
        mb.box(-.2, -.82, 0, .2, -.8, 1.5, "ic_tape")
        mb.box(-.2, -.8, 1.5, .2, .8, 1.52, "ic_tape")
        mb.box(-1.02, -.82, .2, -.4, -.8, .5, col)
    elif kind == "marketing":
        mb.cyl(0, 0, 0, .9, .09, "ic_dark", n=8)
        mb.poly([(-.35, -.0, 1.0), (.35, 0, 1.0), (.35, 0, 1.4), (-.35, 0, 1.4)], [(0, 1, 2, 3)], "ic_dark")
        verts, faces = [], []
        n = 14
        for i in range(n):
            a = 2 * math.pi * i / n
            verts.append((.3 * math.cos(a), -.3, 1.2 + .3 * math.sin(a)))
        for i in range(n):
            a = 2 * math.pi * i / n
            verts.append((.75 * math.cos(a), -1.6, 1.2 + .75 * math.sin(a)))
        faces = [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)] + [tuple(range(n - 1, -1, -1))]
        mb.poly(verts, faces, "ic_metal")
        rv = [(.75 * math.cos(2 * math.pi * i / n), -1.62, 1.2 + .75 * math.sin(2 * math.pi * i / n)) for i in range(n)]
        mb.poly(rv, [tuple(range(n))], col)
    ob = mb.build(loc)
    ob.scale = (s, s, s)
    glow(ob, {col: em})
    return ob


def qmark(name, loc, s=1.0, key_="n_pink", em=6.0):
    return H.text(name, "?", 2.6 * s, key_, depth=.4 * s, loc=loc, emission=em)


def xmark(name, loc, s=1.0, key_="x_red", em=5.0, rot_x=math.pi / 2):
    mb = W.MB(name)
    for a in (math.pi / 4, -math.pi / 4):
        c, si = math.cos(a), math.sin(a)
        L_, T_ = 1.6, .32
        pts = [(-L_ / 2, -T_ / 2), (L_ / 2, -T_ / 2), (L_ / 2, T_ / 2), (-L_ / 2, T_ / 2)]
        pts = [(x * c - z * si, x * si + z * c) for x, z in pts]
        mb.prism_y(pts, -.1, .1, key_)
    ob = mb.build(loc)
    ob.scale = (s, s, s)
    glow(ob, {key_: em})
    return ob


def crown(name, loc, s=1.0, key_="n_gold", em=5.0):
    mb = W.MB(name)
    n = 10
    M.lathe(mb, 0, 0, 0, [(0, 0), (1.0, 0), (1.0, .45), (.88, .45), (.88, .1), (0, .1)], key_, n=30)
    for i in range(n // 2):
        a = 2 * math.pi * i / (n // 2)
        x, y = math.cos(a) * .94, math.sin(a) * .94
        mb.cyl(x, y, .4, 1.25, .2, key_, n=6, r_top=0)
        mb.sphere(x, y, 1.3, .12, "n_white")
    ob = mb.build(loc)
    ob.scale = (s, s, s)
    glow(ob, {key_: em, "n_white": 6.0})
    return ob


def magnifier(name, loc, s=1.0):
    mb = W.MB(name)
    n = 30
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        r0, r1 = 1.0, 1.18
        p = [(r0 * math.cos(a0), r0 * math.sin(a0)), (r1 * math.cos(a0), r1 * math.sin(a0)),
             (r1 * math.cos(a1), r1 * math.sin(a1)), (r0 * math.cos(a1), r0 * math.sin(a1))]
        mb.prism_y(p, -.1, .1, "n_cyan")
    mb.prism_y([(.8, -.8), (.95, -.65), (1.9, -1.6), (1.75, -1.75)], -.12, .12, "ic_dark")
    ob = mb.build(loc)
    ob.rotation_euler.x = 0
    ob.scale = (s, s, s)
    glow(ob, {"n_cyan": 5.0})
    lens = W.MB(name + "_lens")
    lens.disc_y(0, .02, 0, 1.0, .04, "n_cyan", n=30)
    lo = lens.build(parent=ob)
    set_mat(lo, glow_glass("n_cyan", .4, .2))
    return ob


def siren(name, loc, s=1.0):
    mb = W.MB(name)
    mb.cyl(0, 0, 0, .3, .9, "ic_dark", n=20)
    M.lathe(mb, 0, 0, .3, [(.75, 0), (.75, .5), (.6, .9), (.3, 1.1), (0, 1.15)], "n_red", n=20)
    ob = mb.build(loc)
    ob.scale = (s, s, s)
    glow(ob, {"n_red": 6.0})
    li = P.point(name + "_li", (loc[0], loc[1], loc[2] + .9 * s), 900, (1, .1, .15), .4)
    return ob, li


def flash_siren(ob, li, f0, f1, period=10):
    m = ob.data.materials[[i for i, mm in enumerate(ob.data.materials) if "n_red" in mm.name][0]]
    inp = m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    e = li.data.energy
    f = f0
    while f <= f1:
        for fr_, v in ((f, 1.0), (f + period // 2, .1)):
            inp.default_value = 8.0 * v
            inp.keyframe_insert("default_value", frame=int(fr_))
            li.data.energy = e * v
            li.data.keyframe_insert("energy", frame=int(fr_))
        f += period
    if f0 > 1:
        inp.default_value = .2
        inp.keyframe_insert("default_value", frame=1)
        li.data.energy = 0
        li.data.keyframe_insert("energy", frame=1)
        inp.default_value = .2
        inp.keyframe_insert("default_value", frame=int(f0) - 1)
        li.data.energy = 0
        li.data.keyframe_insert("energy", frame=int(f0) - 1)


def gate(name, loc=(0, 0, 0), w=7.0, sign="CUKAI"):
    """gerbang pemeriksaan: 2 tiang + palang merah-putih + papan neon. Palang = objek 'arm' (putar y)."""
    mb = W.MB(name)
    for x in (-w / 2, w / 2):
        mb.box(x - .35, -.35, 0, x + .35, .35, 4.2, "gate_post")
    mb.box(-w / 2 - .5, -.5, 4.2, w / 2 + .5, .5, 4.9, "gate_post")
    ob = mb.build(loc)
    arm = W.MB(name + "_arm")
    n = 8
    for i in range(n):
        x0 = i * (w - .6) / n
        arm.box(x0, -.12, -.15, x0 + (w - .6) / n, .12, .15, "gate_red" if i % 2 == 0 else "gate_wht")
    ao = arm.build((loc[0] - w / 2 + .35, loc[1] - .45, loc[2] + 1.6))
    glow(ao, {"gate_red": 2.0})
    tr = W.MB(name + "_tr")
    tr.box(-w / 2 - .5, -.56, 4.2, w / 2 + .5, -.5, 4.3, "n_gold")
    tr.box(-w / 2 - .5, -.56, 4.8, w / 2 + .5, -.5, 4.9, "n_gold")
    to = tr.build(loc)
    glow(to, {"n_gold": 5.0})
    sg = H.text(name + "_sign", sign, .5, "n_gold", depth=.06, loc=(loc[0], loc[1] - .56, loc[2] + 4.33),
                emission=6.0)
    return {"body": ob, "arm": ao, "trim": to, "sign": sg}


def conveyor(name, x0, x1, y, z=0.0, w=1.6, key_="n_cyan"):
    mb = W.MB(name)
    mb.box(x0, y - w / 2, z, x1, y + w / 2, z + .5, "ic_dark")
    mb.box(x0, y - w / 2 - .05, z + .5, x1, y - w / 2 + .05, z + .6, key_)
    mb.box(x0, y + w / 2 - .05, z + .5, x1, y + w / 2 + .05, z + .6, key_)
    ob = mb.build()
    glow(ob, {key_: 5.0})
    return ob


def market_shelves(name, loc=(0, 0, 0), rows=3, length=24.0, seed=4, gap=5.0):
    """lorong rak-rak liquid berpendar (pasar). Satu mesh besar."""
    rnd = random.Random(seed)
    mb = W.MB(name)
    cols = ["lq_pink", "lq_toko", "lq_brand", "lq_negara", "lq_cheap", "lq_amber"]
    for r in range(rows):
        y = r * gap
        mb.box(-length / 2, y - .8, 0, length / 2, y + .8, .2, "shelf_dk")
        mb.box(-length / 2, y + .55, 0, length / 2, y + .8, 4.2, "shelf_dk")
        for zz in (.2, 1.5, 2.8):
            mb.box(-length / 2, y - .8, zz, length / 2, y + .55, zz + .08, "shelf_dk")
            mb.box(-length / 2, y - .84, zz + .08, length / 2, y - .8, zz + .14, "n_purple")
            x = -length / 2 + .5
            while x < length / 2 - .4:
                bottle_mb(mb, x, y - .1, zz + .08, .25, rnd.choice(cols))
                x += .72
    ob = mb.build(loc)
    glow(ob, {**{c: 1.8 for c in cols}, "n_purple": 5.0})
    return ob


def pie(name, parts, r=3.0, h=.8, loc=(0, 0, 0), n=60, em=1.6):
    """diagram pai 3D: parts = [(key, porsi)], mulai dari sudut 90° searah jarum jam.
    Tiap irisan objek terpisah berporos di pusat (bisa digeser keluar)."""
    tot = sum(p for _, p in parts)
    a = math.pi / 2
    out = []
    for i, (k, p) in enumerate(parts):
        da = 2 * math.pi * p / tot
        m = max(3, int(n * p / tot))
        mb = W.MB(f"{name}_{i}")
        pts = [(0, 0)] + [(r * math.cos(a - da * j / m), r * math.sin(a - da * j / m)) for j in range(m + 1)]
        vs = [(x, y, 0) for x, y in pts] + [(x, y, h) for x, y in pts]
        N = len(pts)
        fs = [tuple(range(N - 1, -1, -1)), tuple(range(N, 2 * N))]
        fs += [(j, (j + 1) % N, N + (j + 1) % N, N + j) for j in range(N)]
        mb.poly(vs, fs, k)
        ob = mb.build(loc)
        set_mat(ob, emis(k, em))
        mid = a - da / 2
        ob["mid"] = (math.cos(mid), math.sin(mid))
        out.append(ob)
        a -= da
    return out


def phone(name, loc=(0, 0, 0), s=1.0, bubbles=(("ph_bub", .7), ("ph_bub2", .5), ("ph_bub", .6))):
    """ponsel berdiri (layar menghadap -Y) dengan gelembung chat."""
    mb = W.MB(name)
    L.rbox(mb, -1.0, -.12, 0, 1.0, .12, 4.0, "ph_body", c=.18)
    mb.box(-.88, -.13, .25, .88, -.12, 3.75, "ph_screen")
    ob = mb.build(loc)
    ob.scale = (s, s, s)
    glow(ob, {"ph_screen": .8})
    bb = W.MB(name + "_bub")
    z = 3.3
    for i, (k, w) in enumerate(bubbles):
        x0 = -.75 if i % 2 == 0 else .75 - 1.5 * w
        L.rbox(bb, x0, -.16, z - .42, x0 + 1.5 * w, -.13, z, k, c=.08)
        z -= .62
    bo = bb.build(parent=ob)
    glow(bo, {"ph_bub": 2.0, "ph_bub2": 3.0})
    return ob


def paper_plane(name, loc=(0, 0, 0), s=1.0, key_="plane"):
    mb = W.MB(name)
    mb.poly([(0, 1.6, 0), (-1.1, -1.0, 0), (0, -.6, -.25)], [(0, 1, 2)], key_)
    mb.poly([(0, 1.6, 0), (0, -.6, -.25), (1.1, -1.0, 0)], [(0, 1, 2)], key_)
    mb.poly([(0, 1.6, 0), (0, -.6, -.25), (0, -.9, -.6)], [(0, 1, 2)], "n_cyan")
    ob = mb.build(loc)
    ob.scale = (s, s, s)
    glow(ob, {key_: 2.5, "n_cyan": 5})
    return ob


def neon_sign(name, body, loc, size=1.2, key_="n_pink", em=8.0, frame=True, pad=.5):
    """tulisan neon + bingkai tabung neon."""
    t = H.text(name, body, size, key_, depth=.15, loc=loc, emission=em)
    if frame:
        w = .62 * size * len(body) + 2 * pad
        h = size * 1.05 + 2 * pad
        mb = W.MB(name + "_fr")
        x0, x1 = loc[0] - w / 2, loc[0] + w / 2
        z0, z1 = loc[2] - pad + .05 * size, loc[2] - pad + h
        y = loc[1] + .05
        tt = .08
        mb.box(x0, y, z0, x1, y + .1, z0 + tt, key_)
        mb.box(x0, y, z1 - tt, x1, y + .1, z1, key_)
        mb.box(x0, y, z0, x0 + tt, y + .1, z1, key_)
        mb.box(x1 - tt, y, z0, x1, y + .1, z1, key_)
        mb.box(x0, y + .1, z0, x1, y + .2, z1, "bd_dark")
        fo = mb.build()
        glow(fo, {key_: em * .7})
        return t, fo
    return t, None


def block(name, key_="n_gold", s=1.0, loc=(0, 0, 0), em=2.4, frame_em=6.0):
    """kubik 'uang' berpendar (porsi Rp) dengan rangka tepi terang."""
    return pillar(name, s, s, s, key_, em, frame_em, loc)


def drop(name, loc, s=1.0, key_="n_gold", em=4.0):
    mb = W.MB(name)
    M.drop_shape(mb, 0, 0, 0, 1.0, key_, depth=.3)
    ob = mb.build(loc)
    ob.scale = (s, s, s)
    glow(ob, {key_: em})
    return ob


# =================================================================== KOTA SIANG (template seri)
import world_prk as R  # noqa: E402

lp.PAL.update({
    "vs_wall": "#FBF7FB", "vs_wall2": "#EADCF5", "vs_pink": "#E8418F", "vs_purple": "#7B4FD6", "vs_glass": "#B9D6E6",
    "vs_floor": "#E9E3EC", "vs_shelf": "#F4F0F6", "vs_awn": "#8E5BE0", "vs_awn2": "#F06AAA",
    "tw_plaza": "#D8D1C6", "tw_plaza2": "#CBC3B6", "stall": "#3B3346", "stall_t": "#2E2838", "van": "#F2F3F5",
    "van2": "#3E6FB0", "bb_frame": "#2F2F38", "bb_face": "#FFFFFF",
})


def vape_store_day(name, loc=(0, 0, 0), w=14.0, d=11.0, accent="vs_pink", sign="TOKO VAPE", seed=3):
    """toko vape siang: fasad putih-lila, kaca lebar berisi rak botol warna-warni, papan nama, kanopi.
    Asal = tengah muka toko di tanah, menghadap -Y."""
    rnd = random.Random(seed)
    x, y, z = loc
    h = 7.6
    mb = W.MB(name)
    mb.box(-w / 2, 0, 0, w / 2, d, .2, "vs_floor")
    mb.box(-w / 2, d - .3, 0, w / 2, d, h, "vs_wall")
    mb.box(-w / 2, 0, 0, -w / 2 + .4, d, h, "vs_wall")
    mb.box(w / 2 - .4, 0, 0, w / 2, d, h, "vs_wall")
    mb.box(-w / 2, 0, 3.9, w / 2, d, h, "vs_wall")                  # lantai 2 (masif)
    mb.box(-w / 2 - .15, -.15, h, w / 2 + .15, d + .15, h + .35, "vs_wall2")
    for cx in (-w / 4, w / 4):
        mb.box(cx - 1.6, -.06, 4.9, cx + 1.6, .02, 6.6, "vs_glass")
    mb.box(-w / 2, -.2, 3.9, w / 2, .05, 4.9, accent)              # papan nama
    for xx in (-w / 2 + .2, -w / 6, w / 6, w / 2 - .2):
        mb.box(xx - .1, -.05, 0, xx + .1, .2, 3.9, "vs_wall2")
    mb.prism_x([(-1.8, 3.6), (0, 3.6), (0, 3.85)], -w / 2, w / 2, "vs_awn")
    body = mb.build(loc)
    sh = W.MB(name + "_sh")
    cols = ["lq_pink", "lq_toko", "lq_brand", "lq_negara", "lq_cheap", "lq_amber"]
    for zz in (.6, 1.6, 2.6):
        sh.box(-w / 2 + .8, d - 1.4, zz - .06, w / 2 - .8, d - .4, zz, "vs_shelf")
        xx = -w / 2 + 1.1
        while xx < w / 2 - 1:
            bottle_mb(sh, xx, d - .9, zz, .17, rnd.choice(cols))
            xx += .52
    sh.box(-3, 3.2, 0, 3, 4.2, 1.1, "vs_wall2")                    # meja kasir
    so = sh.build(loc)
    glow(so, {c: 1.2 for c in cols})
    gl = W.MB(name + "_gl")
    gl.box(-w / 2 + .4, -.02, .2, w / 2 - .4, .04, 3.9, "vs_glass")
    go = gl.build(loc)
    set_mat(go, glass_tint("vs_glass", .22))
    sg = H.text(name + "_sign", sign, .78, "c_white", depth=.08, loc=(x, y - .25, z + 4.03), emission=.6)
    li = P.point(name + "_li", (x, y + d / 2, z + 3.2), 500, (1, .9, .95), 2.5)
    return {"body": body, "shelf": so, "glass": go, "sign": sg, "light": li}


def factory_day(name, loc=(0, 0, 0), sign="PABRIK LIQUID"):
    mb, top = M.factory(name)
    ob = mb.build(loc)
    t = H.text(name + "_sign", sign, 1.2, "vs_purple", depth=.25, loc=(loc[0] - 8.25, loc[1] - 10.2, loc[2] + 7.75 + M.Z),
               emission=.4)
    return {"body": ob, "sign": t, "top": top}


def gov_day(name, loc=(0, 0, 0), sign="KAS NEGARA", w=20.0, d=12.0):
    mb, top = H.gov_office(name, w, d)
    ob = mb.build(loc)
    t = H.text(name + "_sign", sign, .8, "c_white", depth=.1,
               loc=(loc[0], loc[1] - d / 2 - 2.62, loc[2] + H.Z + 5.25), emission=.4)
    return {"body": ob, "sign": t, "top": top}


def shady_stall(name, loc=(0, 0, 0)):
    """lapak gelap pinggir jalan (liquid tanpa pita), tenda hitam + meja botol hijau."""
    mb = W.MB(name)
    for sx in (-2, 2):
        for sy in (-1.4, 1.4):
            mb.box(sx - .06, sy - .06, 0, sx + .06, sy + .06, 2.6, "stall")
    mb.prism_x([(-1.8, 2.6), (1.8, 2.6), (0, 3.4)], -2.4, 2.4, "stall_t")
    mb.box(-1.8, -1.0, 0, 1.8, -.2, .9, "stall")
    for k in range(8):
        bottle_mb(mb, -1.5 + k * .42, -.6, .9, .14, "lq_cheap")
    ob = mb.build(loc)
    glow(ob, {"lq_cheap": 2.0})
    return ob


def box_van(name, loc=(0, 0, 0), rot=0.0):
    mb = W.MB(name)
    L.rbox(mb, -2.6, -1.0, .5, 1.2, 1.0, 3.0, "van", c=.12)
    L.rbox(mb, 1.2, -1.0, .5, 2.6, 1.0, 2.3, "van2", c=.15)
    mb.box(2.0, -1.02, 1.4, 2.62, 1.02, 2.1, "cr_glass")
    for wx in (-1.6, 1.8):
        for wy in (-1.0, 1.0):
            mb.disc_y(wx, wy + (.15 if wy > 0 else 0), .45, .45, .3, "tire2", n=12)
    ob = mb.build(loc, rot)
    return ob


def billboard_day(name, body, loc, w=16.0, h=6.0, key_="vs_pink", em=1.5):
    mb = W.MB(name)
    for sx in (-w / 3, w / 3):
        mb.box(sx - .25, -.25, 0, sx + .25, .25, 8, "bb_frame")
    mb.box(-w / 2 - .3, -.3, 8, w / 2 + .3, .3, 8 + h + .6, "bb_frame")
    mb.box(-w / 2, -.36, 8.3, w / 2, -.3, 8 + h + .3, key_)
    ob = mb.build(loc)
    glow(ob, {key_: em})
    t = H.text(name + "_t", body, h * .55, "c_white", depth=.1, loc=(loc[0], loc[1] - .42, loc[2] + 8.3 + h * .2),
               emission=1.5)
    return ob, t


def town(seed=3, focus="vape", people=True, bikes=True, traffic=True, n_frames=200, ext=150.0, center_clear=22.0,
         shops=None):
    """template kota siang (jalan + trotoar + ruko + tiang listrik + pohon + kota jauh). Bangunan fokus di tengah
    (y=4..): 'vape' | 'gov' | 'factory' | 'market' | None. Return info dict."""
    rnd = random.Random(seed)
    g = W.MB("ground")
    g.box(-ext, -ext, -.3, ext, ext, 0, "pk_ground")
    g.box(-ext, R.ROAD_Y0, -.02, ext, R.ROAD_Y1, .02, "pk_asph")
    for xx in range(int(-ext), int(ext), 8):
        g.box(xx, -27.15, .02, xx + 4, -26.85, .035, "pk_line")
    for yy in (R.ROAD_Y0 + .5, R.ROAD_Y1 - .5):
        g.box(-ext, yy - .1, .02, ext, yy + .1, .035, "pk_line")
    g.box(-ext, R.ROAD_Y1, 0, ext, 2.5, .22, "pk_walk")
    g.box(-ext, R.ROAD_Y1, 0, ext, R.ROAD_Y1 + .35, .3, "pk_curb")
    g.box(-center_clear, -16, 0, center_clear, 2.5, .24, "tw_plaza")
    for k in range(-int(center_clear), int(center_clear), 3):
        g.box(k, -16, .24, k + .08, 2.5, .245, "tw_plaza2")
    g.box(-ext, R.ROAD_Y0 - 3.2, 0, ext, R.ROAD_Y0, .26, "pk_walk")
    g.box(-ext, R.ROAD_Y0 - .35, 0, ext, R.ROAD_Y0, .3, "pk_curb")
    g.build()
    b = W.MB("bldg")
    cc = center_clear
    R.ruko(b, -60, -cc - 1, 2.5, 14, rnd)
    R.ruko(b, cc + 1, 60, 2.5, 14, rnd)
    R.ruko(b, -116, -62, 2.5, 14, rnd, floors=3)
    R.ruko(b, 62, 116, 2.5, 14, rnd, floors=3)
    b.box(-ext, -ext, 0, ext, R.ROAD_Y0 - 3.2, .1, "pk_grass")
    for side in (-1, 1):                         # tiang listrik hanya jauh dari pusat (tidak menutup kamera)
        xs = [side * x for x in range(66, 111, 22)]
        for xx in xs:
            R.power_pole(b, xx, -18.6)
        R.wires(b, sorted(xs), -18.6, 11.0)
    for xx in range(-96, 97, 12):
        if abs(xx) > 10:
            C.street_tree(b, xx + 5, -36.2, 1.1, rnd)
    for xx in (-cc + 2, cc - 2):
        C.street_tree(b, xx, -14.5, 1.0, rnd)
    b.build()
    f = W.MB("far")
    for k in range(46):
        xx = -150 + k * 6.7 + rnd.uniform(-1, 1)
        yy = 80 + rnd.uniform(0, 40)
        w, h = rnd.uniform(5, 9), rnd.uniform(8, 34)
        f.box(xx, yy, 0, xx + w, yy + w, h, rnd.choice(("ct_glass", "ct_glass2", "ct_con", "ct_white", "ct_glass3")))
    f.box(-150, 22, 0, 150, 78, .05, "pk_grass")
    for k in range(60):
        C.street_tree(f, rnd.uniform(-140, 140), rnd.uniform(26, 76), rnd.uniform(1.0, 1.6), rnd)
    f.build()
    info = {"focus": None, "people": [], "cars": []}
    if focus == "vape":
        info["focus"] = vape_store_day("shop", (0, 4, .24))
    elif focus == "gov":
        info["focus"] = gov_day("gov", (0, 10, .24))
    elif focus == "factory":
        info["focus"] = factory_day("fac", (0, 16, .24))
    elif focus == "market":
        cols = ["vs_pink", "vs_purple", "vs_awn2", "vs_awn", "vs_pink"]
        info["focus"] = [vape_store_day(f"shop{i}", (-40 + i * 20, 4, .22), 15, 10, cols[i], seed=i + 2)
                         for i in range(5)]
    if bikes:
        k = 0
        for i in range(36):
            xx = rnd.choice((-1, 1)) * rnd.uniform(cc + 2, 58)
            R.motor(f"bk{k}", (xx, rnd.uniform(-3, 0), .22), math.pi / 2 + rnd.uniform(-.1, .1), rnd.choice(R.BIKE_COLS),
                    .78)
            k += 1
    if people:
        for k in range(7):
            xx = rnd.uniform(-cc + 3, cc - 3)
            p = R.shopper(f"sh{k}", k, (xx, rnd.uniform(-12, -4), .24), rnd.uniform(-.8, .8))
            info["people"].append(p)
    if traffic:
        for k in range(4):
            lane = -23.2 if k % 2 == 0 else -30.8
            dirn = 1 if lane > -27 else -1
            cr = R.car(f"tc{k}", (0, lane, 0), 0 if dirn > 0 else math.pi, R.CAR_COLS[k % len(R.CAR_COLS)], .9)
            x0 = rnd.uniform(-90, 60) * dirn
            sp = 9.0
            for fk in (1, n_frames):
                cr.location.x = x0 + dirn * sp * (fk - 1) / 30
                cr.keyframe_insert("location", frame=fk)
            info["cars"].append(cr)
    return info


def setup_day_light():
    """cahaya siang template seri (matahari hangat + langit terang)."""
    R.setup_prk_light()
