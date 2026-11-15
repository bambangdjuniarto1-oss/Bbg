"""Aset & dunia diorama untuk video "Bedah Bisnis: Pestapora 2026" (festival musik 3 hari).

Isi: area festival senja (lapangan rumput luas, jalur, pagar), panggung utama raksasa (atap truss, dinding
LED berdenyut, layar samping, speaker line-array, lampu sorot + berkas cahaya bergerak), panggung-panggung
kecil (tenda sirkus, kubah, kontainer, panggung terbuka) -> total 19 panggung, band di panggung, lautan
penonton (tangan terangkat, lampu HP), gerbang masuk + antrean + pemindai tiket, tiket 3D & gelang,
tenant makanan, food truck, stan merchandise, booth aktivasi sponsor (generik, tanpa logo asli), bianglala,
tiang lampu, untaian lampu, kembang api, konfeti, area belakang panggung (truk, genset, kru, peti alat),
ikon biaya festival, kota di kejauhan. Semua generik (tanpa logo/merek asli). Menghadap -Y.
"""
import math
import random

import bpy

import lowpoly as lp
import world as W
import world_hotel as H         # text(), money_bundle(), calculator()
import world_laundry as L       # character(), pose(), rbox/ball/tube
import world_tahu as T          # beam()
import world_ctd as C           # person(), mini_person(), tower(), coin(), eye_token(), stamp() ...

lp.PAL.update({
    # langit & tanah senja
    "f_sky": "#2C2A5A", "f_grass": "#4F8A45", "f_grass2": "#447C3D", "f_path": "#B9A98F", "f_path2": "#A69479",
    "f_dirt": "#8C7A60", "f_far": "#3B5A3E", "f_fence": "#C9CDD3", "f_fence2": "#8E959D",
    # panggung
    "stg_deck": "#1B1C21", "stg_deck2": "#2A2C33", "stg_truss": "#B8BEC6", "stg_truss2": "#7D848D",
    "stg_black": "#121317", "stg_spk": "#17181C", "stg_grill": "#33363D", "stg_skirt": "#0E0F12",
    "led_m": "#FF3EA5", "led_c": "#2EE6FF", "led_o": "#FF9A2E", "led_p": "#8E5BFF", "led_wh": "#FFF4E0",
    "beam_m": "#FF5FBF", "beam_c": "#58E8FF", "beam_y": "#FFD45A", "beam_w": "#FFF1D6",
    # panggung kecil
    "tent_r": "#E2453C", "tent_w": "#F4EFE6", "tent_b": "#2F6FD6", "tent_y": "#F2B632", "dome": "#E9ECF0",
    "dome2": "#C9D0D8", "cont_o": "#E77B2E", "cont_t": "#1E9C8C", "cont_p": "#7B4FD6",
    # tiket & gelang
    "tk_blue": "#2F80ED", "tk_blue2": "#1F5FB8", "tk_gold": "#E8B53A", "tk_gold2": "#C9922A", "tk_pink": "#F2559C",
    "tk_paper": "#FBF7EE", "band_r": "#E8423F",
    # tenant & booth
    "tn_red": "#D9473F", "tn_yel": "#F2C230", "tn_grn": "#3FAE6A", "tn_blu": "#3D8BFF", "tn_wood": "#9A6B43",
    "tn_wood2": "#7C5435", "truck_w": "#F1F2F4", "shirt_b": "#1F2430", "shirt_w": "#F6F6F6", "shirt_r": "#D9473F",
    "sp1": "#D8323A", "sp1b": "#A82329", "sp2": "#1E9A55", "sp2b": "#167A42", "sp3": "#7A44E0", "sp3b": "#5A2FB0",
    # bianglala, lampu
    "fw_white": "#F4F6F8", "fw_red": "#E2453C", "bulb": "#FFD68A", "pole": "#3A3D43",
    # belakang panggung
    "gen": "#E3B23C", "gen2": "#2E3138", "case": "#25272C", "case2": "#9CA3AA", "truck_box": "#D9DCE0",
    # data & biaya
    "money_b": "#4F8FE6", "money_b2": "#3A72C2", "money_y": "#E8B53A", "money_y2": "#C9922A",
    "money_r": "#E25A55", "money_r2": "#B8423E", "warn": "#F2C230", "shield": "#2F80ED",
})

SKIN = ("skin1", "skin2", "skin3")
SHIRTS = ("c_coral", "c_mint", "c_sky", "c_mustard", "c_lilac", "c_white", "c_navy", "c_pink", "c_olive",
          "c_brick", "c_black", "c_black2")
HAIRS = ("hair_blk", "hair_brn", "hair_dk", "hij_cream", "hij_navy", "hair_blk")

STAGE_W, STAGE_D, DECK_H = 34.0, 16.0, 2.4
MAIN = (0.0, 62.0)                # pusat panggung utama (depan deck di y = MAIN[1] - STAGE_D/2)


# ------------------------------------------------------------------ material khusus
_BEAM = {}


def beam_mat(key_, strength=1.2):
    """berkas cahaya: transparan + emisi (aditif), tidak menerangi/membayangi benda lain."""
    k = (key_, strength)
    if k in _BEAM and _BEAM[k].name in bpy.data.materials:
        return _BEAM[k]
    m = bpy.data.materials.new(f"beam_{key_}_{strength}")
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
    # memudar ke ujung: kekuatan x (koordinat generated z)^2  (z=1 di kepala lampu, 0 di ujung)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    pw = nt.nodes.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = 2.2
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = strength
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], pw.inputs[0])
    nt.links.new(pw.outputs[0], mul.inputs[0])
    nt.links.new(mul.outputs[0], em.inputs["Strength"])
    nt.links.new(tr.outputs[0], add.inputs[0])
    nt.links.new(em.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs["Surface"])
    _BEAM[k] = m
    return m


def no_light(ob):
    """objek hanya terlihat kamera (berkas cahaya, glow)."""
    for a in ("visible_diffuse", "visible_glossy", "visible_transmission", "visible_shadow",
              "visible_volume_scatter"):
        if hasattr(ob, a):
            setattr(ob, a, False)
    return ob


def lit(ob, key_, strength):
    """ganti semua material objek jadi versi berpendar dari `key_`."""
    ob.data.materials.clear()
    ob.data.materials.append(lp.mat(key_, emission=strength))
    return ob


def setup_fest_light(dusk=True):
    """senja ungu-jingga: langit indigo, matahari terbenam rendah, isian lembut."""
    sc = bpy.context.scene
    w = sc.world
    nt = w.node_tree
    sky = lp.hex_rgba(lp.PAL["f_sky"])
    fill = lp.hex_rgba("#8A86C9")
    for n in nt.nodes:
        if n.type == "BACKGROUND":
            n.inputs["Color"].default_value = sky
    # isian (light path non-kamera) lebih terang & ungu supaya bayangan tidak hitam
    bgs = [n for n in nt.nodes if n.type == "BACKGROUND"]
    if len(bgs) == 2:
        bgs[0].inputs["Color"].default_value = fill
        bgs[0].inputs["Strength"].default_value = 1.15
        bgs[1].inputs["Strength"].default_value = 1.0
    sun = bpy.data.objects.get("sun")
    sun.data.energy = 2.6
    sun.data.color = (1.0, .66, .42)
    sun.data.angle = math.radians(8)
    sun.rotation_euler = (math.radians(56), 0, math.radians(-128))
    rim = bpy.data.objects.new("rim", bpy.data.lights.new("rim", "SUN"))
    rim.data.energy = 1.2
    rim.data.color = (.62, .7, 1.0)
    rim.rotation_euler = (math.radians(55), 0, math.radians(40))
    lp._link(rim)
    sc.view_settings.look = "None"


def spot(name, loc, aim, energy=3000.0, size=35.0, color=(1, 1, 1), blend=.4):
    li = bpy.data.lights.new(name, "SPOT")
    li.energy = energy
    li.spot_size = math.radians(size)
    li.spot_blend = blend
    li.color = color
    ob = bpy.data.objects.new(name, li)
    lp._link(ob)
    ob.location = loc
    d = (aim[0] - loc[0], aim[1] - loc[1], aim[2] - loc[2])
    ob.rotation_euler = (math.atan2(math.hypot(d[0], d[1]), -d[2]), 0, math.atan2(d[1], d[0]) + math.pi / 2)
    return ob


def point(name, loc, energy=500.0, color=(1, 1, 1), r=.5):
    li = bpy.data.lights.new(name, "POINT")
    li.energy = energy
    li.color = color
    li.shadow_soft_size = r
    ob = bpy.data.objects.new(name, li)
    lp._link(ob)
    ob.location = loc
    return ob


# ------------------------------------------------------------------ berkas cahaya
def light_beam(name, origin, length=40.0, r_end=3.2, key_="beam_c", strength=.9, rx=0.0, rz=0.0):
    """kerucut cahaya dari `origin` ke arah bawah-depan; diputar lewat rotation (x=tilt, z=pan).
    Objek berporos di kepala lampu, sumbu kerucut = -Z lokal."""
    mb = W.MB(name)
    n = 12
    vs = [(0, 0, 0)]
    for i in range(n):
        a = 2 * math.pi * i / n
        vs.append((math.cos(a) * r_end, math.sin(a) * r_end, -length))
    fs = [(0, 1 + (i + 1) % n, 1 + i) for i in range(n)]
    mb.poly(vs, fs, "beam_w")
    ob = mb.build(origin)
    ob.data.materials.clear()
    ob.data.materials.append(beam_mat(key_, strength))
    ob.rotation_euler = (rx, 0, rz)
    return no_light(ob)


def sweep(ob, f0, f1, rx=(.5, -.5), rz=(-.3, .3), period=60, phase=0):
    """berkas menyapu kiri-kanan & maju-mundur."""
    f = f0
    k = phase
    while f <= f1 + period:
        t = k % 2
        ob.rotation_euler = (rx[t], 0, rz[t])
        ob.keyframe_insert("rotation_euler", frame=f)
        f += period // 2
        k += 1


# ------------------------------------------------------------------ panggung utama
def _truss(mb, p0, p1, w=.55, key_="stg_truss"):
    """batang truss kotak (4 pipa + silang)."""
    dx, dy, dz = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
    L_ = math.dist(p0, p1)
    if L_ < 1e-6:
        return
    # vektor tegak lurus sederhana
    if abs(dz) > max(abs(dx), abs(dy)):
        u, v = (w / 2, 0, 0), (0, w / 2, 0)
    elif abs(dx) >= abs(dy):
        u, v = (0, w / 2, 0), (0, 0, w / 2)
    else:
        u, v = (w / 2, 0, 0), (0, 0, w / 2)
    corners = [(su, sv) for su in (-1, 1) for sv in (-1, 1)]
    for su, sv in corners:
        o = (su * u[0] + sv * v[0], su * u[1] + sv * v[1], su * u[2] + sv * v[2])
        T.beam(mb, (p0[0] + o[0], p0[1] + o[1], p0[2] + o[2]), (p1[0] + o[0], p1[1] + o[1], p1[2] + o[2]), .07, key_)
    n = max(1, int(L_ / 1.6))
    for k in range(n):
        a = k / n
        b = (k + 1) / n
        pa = (p0[0] + dx * a, p0[1] + dy * a, p0[2] + dz * a)
        pb = (p0[0] + dx * b, p0[1] + dy * b, p0[2] + dz * b)
        s0 = (1, 1) if k % 2 else (-1, -1)
        s1 = (-1, 1) if k % 2 else (1, -1)
        T.beam(mb, (pa[0] + s0[0] * u[0] + s0[1] * v[0], pa[1] + s0[0] * u[1] + s0[1] * v[1], pa[2] + s0[0] * u[2] + s0[1] * v[2]),
               (pb[0] + s1[0] * u[0] + s1[1] * v[0], pb[1] + s1[0] * u[1] + s1[1] * v[1], pb[2] + s1[0] * u[2] + s1[1] * v[2]),
               .04, "stg_truss2")


def main_stage(name, loc=MAIN, w=STAGE_W, d=STAGE_D, beams=True, lights=True, beam_str=.6, led_em=3.0):
    """panggung utama. Return dict: deck_z, screen (objek LED), mats (material LED utk diberi denyut),
    beams (list), heads (titik lampu), anchors."""
    ox, oy = loc
    mb = W.MB(name)
    y0, y1 = oy - d / 2, oy + d / 2
    # deck + rok hitam + tangga samping
    mb.box(ox - w / 2, y0, 0, ox + w / 2, y1, DECK_H, "stg_deck")
    mb.box(ox - w / 2 - .05, y0 - .05, 0, ox + w / 2 + .05, y0 + .2, DECK_H - .15, "stg_skirt")
    mb.box(ox - w / 2, y0, DECK_H - .02, ox + w / 2, y1, DECK_H + .02, "stg_deck2")
    # sayap (wing) kiri-kanan untuk speaker & layar
    for sx in (-1, 1):
        xa = ox + sx * (w / 2 + 1)
        mb.box(xa - 3.5, y0 + 2, 0, xa + 3.5, y1, DECK_H, "stg_deck")
        # menara scaffolding layar samping
        _truss(mb, (xa - 2.6, y0 + 3, DECK_H), (xa - 2.6, y0 + 3, 20), .6)
        _truss(mb, (xa + 2.6, y0 + 3, DECK_H), (xa + 2.6, y0 + 3, 20), .6)
    # tiang atap (4 menara truss) + atap rangka
    H_ROOF = 21.0
    cols = [(ox - w / 2 + .6, y0 + 1.2), (ox + w / 2 - .6, y0 + 1.2), (ox - w / 2 + .6, y1 - .6), (ox + w / 2 - .6, y1 - .6)]
    for (x, y) in cols:
        _truss(mb, (x, y, DECK_H), (x, y, H_ROOF), .8)
    _truss(mb, (ox - w / 2 + .6, y0 + 1.2, H_ROOF), (ox + w / 2 - .6, y0 + 1.2, H_ROOF), .8)
    _truss(mb, (ox - w / 2 + .6, y1 - .6, H_ROOF), (ox + w / 2 - .6, y1 - .6, H_ROOF), .8)
    for x in (ox - w / 2 + .6, ox, ox + w / 2 - .6):
        _truss(mb, (x, y0 + 1.2, H_ROOF), (x, y1 - .6, H_ROOF), .7)
    # atap membran lengkung (segmen)
    segs = 10
    for k in range(segs):
        a0, a1 = k / segs, (k + 1) / segs
        xa, xb = ox - w / 2 + a0 * w, ox - w / 2 + a1 * w
        za = H_ROOF + .6 + math.sin(a0 * math.pi) * 3.2
        zb = H_ROOF + .6 + math.sin(a1 * math.pi) * 3.2
        mb.poly([(xa - .3, y0 - .5, za), (xb + .3, y0 - .5, zb), (xb + .3, y1 + .3, zb + .4), (xa - .3, y1 + .3, za + .4),
                 (xa - .3, y0 - .5, za + .35), (xb + .3, y0 - .5, zb + .35), (xb + .3, y1 + .3, zb + .75),
                 (xa - .3, y1 + .3, za + .75)],
                [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], "stg_black")
    # dinding belakang hitam
    mb.box(ox - w / 2, y1 - .5, DECK_H, ox + w / 2, y1, H_ROOF, "stg_black")
    # speaker line-array menggantung + subwoofer di lantai
    for sx in (-1, 1):
        xs = ox + sx * (w / 2 - 2.2)
        for k in range(8):
            z = 17.5 - k * 1.05
            tilt = k * .06
            mb.box(xs - 1.0, y0 - .2 - tilt, z, xs + 1.0, y0 + 1.0 - tilt, z + .95, "stg_spk")
            mb.box(xs - .9, y0 - .25 - tilt, z + .1, xs + .9, y0 - .2 - tilt, z + .85, "stg_grill")
        T.beam(mb, (xs, y0 + .4, 18.4), (xs, y0 + 1.2, H_ROOF), .05, "stg_truss2")
    for k in range(10):
        x = ox - w / 2 + 1.8 + k * (w - 3.6) / 9
        if abs(x - ox) < 3:
            continue
        mb.box(x - .8, y0 - 1.6, 0, x + .8, y0 - .2, 1.3, "stg_spk")
        mb.box(x - .7, y0 - 1.65, .15, x + .7, y0 - 1.6, 1.15, "stg_grill")
    # barikade depan (silver)
    for k in range(int(w / 2.2) + 4):
        x = ox - w / 2 - 4 + k * 2.2
        mb.box(x, y0 - 4.2, 0, x + 2.1, y0 - 3.9, 1.25, "f_fence")
        mb.box(x, y0 - 4.6, 0, x + 2.1, y0 - 3.5, .08, "f_fence2")
    ob = mb.build()
    # dinding LED: grid ubin 4 warna (material terpisah -> bisa berdenyut)
    led = W.MB(name + "_led")
    cols_n, rows_n = 16, 7
    lw, lh = w - 6, 13.0
    keys = ("led_m", "led_c", "led_p", "led_o")
    for i in range(cols_n):
        for j in range(rows_n):
            x0 = ox - lw / 2 + i * lw / cols_n
            z0 = DECK_H + 2.6 + j * lh / rows_n
            k = keys[(i // 2 + j + (i * j) % 3) % 4]
            led.box(x0 + .05, y1 - .62, z0 + .05, x0 + lw / cols_n - .05, y1 - .52, z0 + lh / rows_n - .05, k)
    lo = led.build()
    mats = {}
    for i, m in enumerate(lo.data.materials):
        k = m.name.split("_", 1)[1].rsplit("_", 1)[0]
        lo.data.materials[i] = lp.mat(k, emission=led_em)
        mats[k] = lo.data.materials[i]
    # layar samping (biru-ungu)
    side = W.MB(name + "_side")
    for sx in (-1, 1):
        xa = ox + sx * (w / 2 + 1)
        side.box(xa - 2.3, y0 + 2.6, 9, xa + 2.3, y0 + 2.75, 18.5, "led_c" if sx < 0 else "led_m")
    so = side.build()
    for i, m in enumerate(so.data.materials):
        k = m.name.split("_", 1)[1].rsplit("_", 1)[0]
        so.data.materials[i] = lp.mat(k, emission=2.2)
    # kepala lampu di truss depan
    heads = []
    hm = W.MB(name + "_heads")
    for k in range(9):
        x = ox - w / 2 + 2.5 + k * (w - 5) / 8
        p = (x, y0 + 1.2, H_ROOF - 1.0)
        hm.cyl(x, y0 + 1.2, H_ROOF - 1.3, H_ROOF - .5, .35, "stg_black", n=8)
        heads.append(p)
    for k in range(6):
        x = ox - w / 2 + 4 + k * (w - 8) / 5
        heads.append((x, y1 - 2.5, DECK_H + .4))
        hm.cyl(x, y1 - 2.5, DECK_H, DECK_H + .5, .3, "stg_black", n=8)
    hm.build()
    bulbs = W.MB(name + "_bulbs")
    for (x, y, z) in heads:
        bulbs.sphere(x, y - .02, z - .05, .22, "beam_w")
    bo = bulbs.build()
    lit(bo, "led_wh", 6.0)
    out = {"body": ob, "led": lo, "side": so, "mats": mats, "heads": heads, "deck_z": DECK_H,
           "front_y": y0, "back_y": y1, "roof": H_ROOF, "beams": [], "bulbs": bo}
    if beams:
        cols_b = ("beam_c", "beam_m", "beam_y", "beam_m", "beam_w", "beam_m", "beam_y", "beam_m", "beam_c")
        for k, hp in enumerate(heads[:9]):
            b = light_beam(f"{name}_bm{k}", (hp[0], hp[1] - .1, hp[2] - .3), 34, 2.6, cols_b[k], beam_str,
                           rx=.55, rz=(k - 4) * .08)
            out["beams"].append(b)
        for k, hp in enumerate(heads[9:]):
            b = light_beam(f"{name}_fb{k}", hp, 90, 2.6, ("beam_c", "beam_m")[k % 2], beam_str * .9, rx=math.pi - .25,
                           rz=(k - 2.5) * .12)
            out["beams"].append(b)
    if lights:
        # cahaya panggung sungguhan (warna) supaya deck & band terang
        spot(name + "_sp1", (ox - 8, y0 - 14, 18), (ox - 2, oy - 2, DECK_H), 9000, 40, (1.0, .45, .8))
        spot(name + "_sp2", (ox + 8, y0 - 14, 18), (ox + 2, oy - 2, DECK_H), 9000, 40, (.45, .85, 1.0))
        spot(name + "_sp3", (ox, y0 - 6, 22), (ox, oy - 1, DECK_H), 7000, 35, (1.0, .9, .75))
        point(name + "_pl", (ox, y1 - 3, DECK_H + 8), 9000, (.8, .45, 1.0), 2.0)
    return out


def pulse_led(mats, f0, f1, period=14.5, lo=1.2, hi=4.0, seed=1):
    """denyut LED mengikuti ketukan (124 BPM ~ 14,5 frame)."""
    rnd = random.Random(seed)
    for i, (k, m) in enumerate(sorted(mats.items())):
        b = m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
        f = f0 + i * period / len(mats)
        while f <= f1 + period:
            b.default_value = hi * rnd.uniform(.85, 1.1)
            b.keyframe_insert("default_value", frame=int(f))
            b.default_value = lo
            b.keyframe_insert("default_value", frame=int(f + period * .6))
            f += period


# ------------------------------------------------------------------ band
BAND = {
    "vokal": dict(skin="skin2", top="c_white", sleeve="c_white", bottom="c_black", shoe="shoe_w", hair="long",
                  hair_col="hair_blk", acc=()),
    "gitar": dict(skin="skin1", top="c_black2", sleeve="c_black2", bottom="c_denim", shoe="shoe_dk", hair="short",
                  hair_col="hair_brn", acc=()),
    "bass": dict(skin="skin3", top="c_wine", sleeve="c_wine", bottom="c_black", shoe="shoe_dk", hair="cap",
                 hair_col="c_black", acc=()),
    "drum": dict(skin="skin2", top="c_mustard", sleeve="c_mustard", bottom="c_black", shoe="shoe_dk", hair="short",
                 hair_col="hair_blk", acc=()),
    "keys": dict(skin="skin1", top="c_lilac", sleeve="c_lilac", bottom="c_black", shoe="shoe_w", hair="bun",
                 hair_col="hair_dk", acc=()),
}


def guitar(name, key_="tn_red"):
    mb = W.MB(name)
    mb.disc_y(0, .06, 0, .32, .12, key_, n=12)
    mb.disc_y(.28, .06, .1, .24, .12, key_, n=10)
    mb.box(.35, -.02, .03, 1.25, .04, .11, "tn_wood2")
    mb.box(1.2, -.03, .0, 1.42, .05, .14, "stg_black")
    return mb.build()


def band(name, loc, deck_z):
    """band 5 orang di deck: vokalis + stand mic di depan, gitar & bass di sisi, drum di riser, keyboard."""
    ox, oy = loc
    parts = {}
    rig = W.MB(name + "_rig")
    # riser drum
    rig.box(ox - 3, oy + 2.2, deck_z, ox + 3, oy + 5.6, deck_z + .9, "stg_deck2")
    dz = deck_z + .9
    for (x, y, r, h) in ((ox, oy + 3.5, .55, .7), (ox - 1.0, oy + 3.0, .35, .9), (ox + 1.0, oy + 3.0, .35, .9),
                         (ox + 1.3, oy + 3.9, .45, .55)):
        rig.cyl(x, y, dz, dz + h, r, "c_white", n=12)
        rig.cyl(x, y, dz + h, dz + h + .03, r, "c_grey", n=12)
    for (x, y) in ((ox - 1.6, oy + 3.6), (ox + 1.8, oy + 3.0)):
        T.beam(rig, (x, y, dz), (x, y, dz + 1.6), .03, "stg_truss2")
        rig.cyl(x, y, dz + 1.6, dz + 1.63, .5, "money_y", n=12)
    # stand keyboard
    rig.box(ox + 6.2, oy + 1.4, deck_z + .9, ox + 7.8, oy + 2.0, deck_z + 1.0, "stg_black")
    rig.box(ox + 6.25, oy + 1.4, deck_z + 1.0, ox + 7.75, oy + 1.75, deck_z + 1.03, "c_white")
    T.beam(rig, (ox + 6.5, oy + 1.7, deck_z), (ox + 7.5, oy + 1.7, deck_z + .9), .04, "stg_truss2")
    T.beam(rig, (ox + 7.5, oy + 1.7, deck_z), (ox + 6.5, oy + 1.7, deck_z + .9), .04, "stg_truss2")
    # stand mic vokal + monitor wedge
    T.beam(rig, (ox, oy - 2.6, deck_z), (ox, oy - 2.6, deck_z + 1.75), .03, "stg_truss2")
    rig.cyl(ox, oy - 2.6, deck_z, deck_z + .03, .3, "stg_truss2", n=8)
    for x in (ox - 4.5, ox, ox + 4.5):
        rig.prism_x([(oy - 4.2, deck_z), (oy - 3.2, deck_z), (oy - 3.2, deck_z + .55)], x - .7, x + .7, "stg_spk")
    # amp di belakang gitar & bass
    for x in (ox - 6, ox + 4.5):
        rig.box(x - .7, oy + 1.8, deck_z, x + .7, oy + 2.6, deck_z + 1.2, "stg_spk")
        rig.box(x - .6, oy + 1.75, deck_z + .1, x + .6, oy + 1.8, deck_z + .9, "stg_grill")
    rig.build()
    s = 1.35
    parts["vokal"] = C.person(name + "_v", BAND["vokal"], (ox, oy - 2.1, deck_z), 0, s)
    parts["gitar"] = C.person(name + "_g", BAND["gitar"], (ox - 5.2, oy - .6, deck_z), -.25, s)
    parts["bass"] = C.person(name + "_b", BAND["bass"], (ox + 3.8, oy - .4, deck_z), .25, s)
    parts["drum"] = C.person(name + "_d", BAND["drum"], (ox, oy + 4.5, dz), 0, s * .95)
    parts["keys"] = C.person(name + "_k", BAND["keys"], (ox + 7.0, oy + 2.6, deck_z), .3, s)
    C.sit(parts["drum"], seat_z=dz + .55)
    for nm, col in (("gitar", "tn_red"), ("bass", "tn_blu")):
        g = guitar(f"{name}_{nm}_inst", col)
        g.parent = parts[nm]["body"]
        g.location = (-.45, -.3, 1.05)
        g.rotation_euler = (0, -.45, 0)
        parts[nm]["armR"].rotation_euler = (-.9, 0, .3)
        parts[nm]["armL"].rotation_euler = (-1.1, 0, -.5)
    parts["keys"]["armL"].rotation_euler = (-1.2, 0, .1)
    parts["keys"]["armR"].rotation_euler = (-1.2, 0, -.1)
    return parts


def perform(parts, f0, f1, seed=2):
    """animasi band: vokalis angkat tangan bergantian, gitaris & bassis mengangguk, drummer memukul."""
    rnd = random.Random(seed)
    v = parts["vokal"]
    f = f0
    up = False
    while f <= f1 + 30:
        v["armR"].rotation_euler = (0, -2.7, 0) if up else (-1.3, 0, .2)
        v["armR"].keyframe_insert("rotation_euler", frame=f)
        v["armL"].rotation_euler = (-.4, .3, 0) if up else (0, 2.5, 0)
        v["armL"].keyframe_insert("rotation_euler", frame=f)
        f += rnd.randint(22, 34)
        up = not up
    for nm in ("gitar", "bass", "keys"):
        b = parts[nm]["body"]
        rx0 = b.rotation_euler.x
        f = f0 + rnd.randint(0, 6)
        while f <= f1 + 15:
            b.rotation_euler.x = rx0 + .1
            b.keyframe_insert("rotation_euler", frame=f)
            b.rotation_euler.x = rx0
            b.keyframe_insert("rotation_euler", frame=f + 7)
            f += 14.5 if nm != "keys" else 29
            f = int(f)
    d = parts["drum"]
    f = f0
    k = 0
    while f <= f1 + 8:
        for side, a in (("L", -1.6 if k % 2 else -1.0), ("R", -1.0 if k % 2 else -1.6)):
            d["arm" + side].rotation_euler = (a, 0, .25 if side == "L" else -.25)
            d["arm" + side].keyframe_insert("rotation_euler", frame=f)
        f += 7
        k += 1


# ------------------------------------------------------------------ penonton
def fan(mb, x, y, z, s, rnd, arms=None, phone=False, z_off=0.0):
    """penonton mini dengan opsi tangan terangkat & lampu HP."""
    shirt = rnd.choice(SHIRTS)
    skin = rnd.choice(SKIN)
    C.mini_person(mb, x, y, z + z_off, s, shirt, skin, rnd.choice(HAIRS))
    arms = rnd.random() < .45 if arms is None else arms
    if arms:
        for sx in ((-1, 1) if rnd.random() < .6 else (rnd.choice((-1, 1)),)):
            T.beam(mb, (x + sx * .17 * s, y, z + z_off + .5 * s), (x + sx * .3 * s, y - .05 * s, z + z_off + 1.15 * s),
                   .05 * s, skin)
    return phone


def fest_crowd(name, n, x0, y0, x1, y1, seed=3, s=1.0, groups=3, phone_frac=.12, arms_frac=.45):
    """lautan penonton; dibagi `groups` objek (fase lompat berbeda). Return list objek + objek lampu HP."""
    rnd = random.Random(seed)
    mbs = [W.MB(f"{name}{g}") for g in range(groups)]
    ph = W.MB(name + "_ph")
    cols = max(1, int(round(math.sqrt(n * (x1 - x0) / max(.1, (y1 - y0))))))
    rows = max(1, int(math.ceil(n / cols)))
    for k in range(n):
        c, r = k % cols, k // cols
        x = x0 + (c + .5) * (x1 - x0) / cols + rnd.uniform(-.3, .3)
        y = y0 + (r + .5) * (y1 - y0) / rows + rnd.uniform(-.3, .3)
        ss = s * rnd.uniform(.9, 1.1)
        mb = mbs[rnd.randrange(groups)]
        up = rnd.random() < arms_frac
        fan(mb, x, y, 0, ss, rnd, arms=up)
        if up and rnd.random() < phone_frac / max(arms_frac, .01):
            ph.box(x + .27 * ss, y - .1 * ss, 1.15 * ss, x + .37 * ss, y - .05 * ss, 1.3 * ss, "led_wh")
    obs = [m.build() for m in mbs]
    po = ph.build() if ph.v else None
    if po:
        lit(po, "led_wh", 8.0)
    return obs, po


def jump(obs, f0, f1, amp=.28, period=14.5):
    """penonton melompat ikut ketukan (tiap grup beda fase)."""
    for g, ob in enumerate(obs):
        z0 = ob.location.z
        f = f0 + g * period / len(obs)
        while f <= f1 + period:
            ob.location.z = z0
            ob.keyframe_insert("location", frame=int(f))
            ob.location.z = z0 + amp
            ob.keyframe_insert("location", frame=int(f + period * .4))
            f += period


# ------------------------------------------------------------------ panggung kecil
def small_stage(name, loc, kind="tent", s=1.0, rot=0.0, key_=None):
    """panggung kecil: tent (tenda sirkus bergaris), dome (kubah), box (panggung kontainer), open (deck + truss),
    hall (aula beratap pelana). Return dict(body, glow, top)."""
    rnd = random.Random(int(loc[0] * 7 + loc[1] * 3))
    mb = W.MB(name)
    gl = W.MB(name + "_g")
    top = 0
    if kind == "tent":
        r, h = 9 * s, 5 * s
        col = key_ or rnd.choice(("tent_r", "tent_b", "tent_y"))
        n = 16
        for i in range(n):
            a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            k = col if i % 2 == 0 else "tent_w"
            mb.poly([(math.cos(a0) * r, math.sin(a0) * r, 0), (math.cos(a1) * r, math.sin(a1) * r, 0),
                     (math.cos(a1) * r, math.sin(a1) * r, h), (math.cos(a0) * r, math.sin(a0) * r, h)],
                    [(0, 1, 2, 3)], k)
            mb.poly([(math.cos(a0) * r, math.sin(a0) * r, h), (math.cos(a1) * r, math.sin(a1) * r, h),
                     (0, 0, h + 6 * s)], [(0, 1, 2)], k)
        mb.cyl(0, 0, h + 6 * s, h + 8 * s, .12 * s, "pole", n=6)
        mb.poly([(0, 0, h + 8 * s), (1.6 * s, 0, h + 7.6 * s), (0, 0, h + 7.1 * s)], [(0, 1, 2)], col)
        gl.box(-3.2 * s, -r - .05, .2, 3.2 * s, -r + .2, 4.2 * s, "led_o")       # pintu bercahaya
        top = h + 8 * s
    elif kind == "dome":
        r = 10 * s
        rings, seg = 5, 14
        pts = []
        for j in range(rings + 1):
            e = (math.pi / 2) * j / rings
            pts.append([(math.cos(2 * math.pi * i / seg) * r * math.cos(e), math.sin(2 * math.pi * i / seg) * r * math.cos(e),
                         r * .8 * math.sin(e)) for i in range(seg)])
        for j in range(rings):
            for i in range(seg):
                a, b = pts[j][i], pts[j][(i + 1) % seg]
                c, d = pts[j + 1][(i + 1) % seg], pts[j + 1][i]
                mb.poly([a, b, c, d], [(0, 1, 2, 3)], "dome" if (i + j) % 2 else "dome2")
        gl.box(-4 * s, -r - .1, .2, 4 * s, -r + .6, 4.5 * s, key_ or "led_p")
        top = r * .8
    elif kind == "box":
        col = key_ or rnd.choice(("cont_o", "cont_t", "cont_p"))
        mb.box(-6 * s, -2.5 * s, 0, 6 * s, 2.5 * s, 2.6 * s, col)
        for k in range(12):
            x = -5.8 * s + k * 1.05 * s
            mb.box(x, -2.55 * s, .1, x + .5 * s, -2.5 * s, 2.5 * s, col)
        mb.box(-6.3 * s, -2.8 * s, 2.6 * s, 6.3 * s, 2.8 * s, 2.9 * s, "stg_black")
        mb.box(-6 * s, -6 * s, 0, 6 * s, -2.5 * s, .9 * s, "stg_deck")
        for sx in (-1, 1):
            _truss(mb, (sx * 5.6 * s, -5.6 * s, .9 * s), (sx * 5.6 * s, -5.6 * s, 7 * s), .4)
        _truss(mb, (-5.6 * s, -5.6 * s, 7 * s), (5.6 * s, -5.6 * s, 7 * s), .4)
        gl.box(-4 * s, -2.6 * s, .9 * s, 4 * s, -2.55 * s, 2.4 * s, "led_c")
        top = 7 * s
    elif kind == "hall":
        w_, d_, h_ = 18 * s, 14 * s, 6 * s
        mb.box(-w_ / 2, -d_ / 2, 0, w_ / 2, d_ / 2, h_, "tent_w")
        mb.prism_x([(-d_ / 2 - .4, h_), (d_ / 2 + .4, h_), (0, h_ + 4 * s)], -w_ / 2 - .4, w_ / 2 + .4, key_ or "cont_p")
        gl.box(-5 * s, -d_ / 2 - .1, .2, 5 * s, -d_ / 2 + .2, 4.4 * s, "led_m")
        top = h_ + 4 * s
    else:                                    # open
        mb.box(-7 * s, -4.5 * s, 0, 7 * s, 4.5 * s, 1.2 * s, "stg_deck")
        mb.box(-7 * s, 4.0 * s, 1.2 * s, 7 * s, 4.5 * s, 7.5 * s, "stg_black")
        for sx in (-1, 1):
            for sy in (-1, 1):
                _truss(mb, (sx * 6.6 * s, sy * 4.1 * s, 1.2 * s), (sx * 6.6 * s, sy * 4.1 * s, 8.4 * s), .45)
        _truss(mb, (-6.6 * s, -4.1 * s, 8.4 * s), (6.6 * s, -4.1 * s, 8.4 * s), .45)
        _truss(mb, (-6.6 * s, 4.1 * s, 8.4 * s), (6.6 * s, 4.1 * s, 8.4 * s), .45)
        mb.box(-7.2 * s, -4.6 * s, 8.8 * s, 7.2 * s, 4.6 * s, 9.1 * s, key_ or "tent_b")
        gl.box(-5 * s, 3.9 * s, 2.2 * s, 5 * s, 3.95 * s, 7.0 * s, "led_m")
        top = 9.1 * s
    ob = mb.build(loc if len(loc) == 3 else (loc[0], loc[1], 0))
    ob.rotation_euler.z = rot
    go = gl.build()
    for i, m in enumerate(go.data.materials):
        k = m.name.split("_", 1)[1].rsplit("_", 1)[0]
        go.data.materials[i] = lp.mat(k, emission=3.0)
    go.parent = ob
    return {"body": ob, "glow": go, "top": top}


# ------------------------------------------------------------------ bianglala & lampu
def ferris_wheel(name, loc, r=14.0):
    """bianglala: kaki A-frame (statis) + roda (berputar di sumbu Y) dengan lampu di pelek & gondola."""
    ox, oy = loc
    base = W.MB(name)
    hub_z = r + 2.5
    for sy in (-1.6, 1.6):
        T.beam(base, (ox - r * .55, oy + sy, 0), (ox, oy + sy, hub_z), .35, "fw_white")
        T.beam(base, (ox + r * .55, oy + sy, 0), (ox, oy + sy, hub_z), .35, "fw_white")
    base.box(ox - r * .7, oy - 3, 0, ox + r * .7, oy + 3, .5, "f_fence2")
    base.build()
    wh = W.MB(name + "_wheel")
    n = 16
    for side in (-1.4, 1.4):
        for i in range(n):
            a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            T.beam(wh, (math.cos(a0) * r, side, math.sin(a0) * r), (math.cos(a1) * r, side, math.sin(a1) * r), .18, "fw_white")
            T.beam(wh, (0, side, 0), (math.cos(a0) * r, side, math.sin(a0) * r), .07, "fw_white")
    for i in range(n):
        a = 2 * math.pi * i / n
        cx, cz = math.cos(a) * r, math.sin(a) * r
        T.beam(wh, (cx, -1.4, cz), (cx, 1.4, cz), .1, "fw_white")
        L.rbox(wh, cx - .8, -1.0, cz - 2.2, cx + .8, 1.0, cz - .7, ("fw_red", "tent_b", "tent_y", "cont_t")[i % 4], c=.2)
    wh.cyl(0, 0, -.5, .5, .9, "fw_white", n=10)
    wo = wh.build((ox, oy, hub_z))
    lt = W.MB(name + "_lights")
    for side in (-1.55, 1.55):
        for i in range(n * 2):
            a = 2 * math.pi * i / (n * 2)
            lt.sphere(math.cos(a) * r, side, math.sin(a) * r, .22, "bulb")
    lo = lt.build()
    lit(lo, "bulb", 5.0)
    lo.parent = wo
    return wo


def turn(ob, f0, f1, rpm=1.5, axis=1, fps=30):
    from scenes import key
    rot = list(ob.rotation_euler)
    key(ob, "rotation_euler", f0, tuple(rot))
    rot2 = list(rot)
    rot2[axis] += 2 * math.pi * rpm * (f1 - f0) / fps / 60
    key(ob, "rotation_euler", f1, tuple(rot2))
    for fc in L._fc(ob):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"


def light_pole(mb, gl, x, y, h=11.0):
    mb.cyl(x, y, 0, h, .18, "pole", n=6)
    mb.box(x - 1.2, y - .3, h, x + 1.2, y + .3, h + .5, "pole")
    for k in range(3):
        gl.box(x - 1.0 + k * .8, y - .35, h - .1, x - .5 + k * .8, y + .35, h, "led_wh")


def string_lights(gl, p0, p1, n=14, sag=1.2):
    for i in range(n + 1):
        t = i / n
        x = p0[0] + (p1[0] - p0[0]) * t
        y = p0[1] + (p1[1] - p0[1]) * t
        z = p0[2] + (p1[2] - p0[2]) * t - math.sin(t * math.pi) * sag
        gl.sphere(x, y, z, .16, "bulb")


# ------------------------------------------------------------------ tenant, merch, booth sponsor
def food_stall(mb, x, y, col, rnd, rot90=False):
    """tenda tenant 3x3 beratap runcing + meja + papan menu."""
    s = 3.0
    mb.box(x - s / 2, y - s / 2, 0, x + s / 2, y - s / 2 + .7, 1.0, "tn_wood")
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.cyl(x + sx * s / 2, y + sy * s / 2, 0, 2.5, .05, "f_fence2", n=6)
    mb.poly([(x - s / 2 - .2, y - s / 2 - .2, 2.5), (x + s / 2 + .2, y - s / 2 - .2, 2.5),
             (x + s / 2 + .2, y + s / 2 + .2, 2.5), (x - s / 2 - .2, y + s / 2 + .2, 2.5), (x, y, 3.7)],
            [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (3, 2, 1, 0)], col)
    for k in range(6):
        xa = x - s / 2 - .2 + k * (s + .4) / 6
        mb.poly([(xa, y - s / 2 - .21, 2.5), (xa + (s + .4) / 6, y - s / 2 - .21, 2.5),
                 (xa + (s + .4) / 12, y - s / 2 - .21, 2.15)], [(0, 1, 2)], "tent_w" if k % 2 else col)
    mb.box(x - .9, y + s / 2 - .2, 1.2, x + .9, y + s / 2 - .1, 2.2, "c_black2")
    for k in range(3):
        mb.cyl(x - .7 + k * .6, y - s / 2 + .35, 1.0, 1.25, .17, rnd.choice(("tn_yel", "c_coral", "c_mint", "tn_red")), n=8)


def food_truck(name, col="tn_yel"):
    mb = W.MB(name)
    L.rbox(mb, -3.2, -1.3, .5, 3.2, 1.3, 3.4, col, c=.25)
    mb.box(-2.0, -1.33, 1.5, 1.6, -1.3, 2.6, "stg_black")
    mb.box(-2.2, -1.9, 1.35, 1.8, -1.3, 1.45, "c_white")
    mb.prism_x([(-1.32, 2.7), (-2.6, 2.4), (-2.6, 2.5), (-1.32, 2.9)], -2.2, 1.8, "tent_w")
    mb.box(2.0, -1.32, 2.0, 3.1, 1.32, 3.0, "ct_glass3")
    for sx in (-2.0, 2.0):
        for sy in (-1.2, 1.2):
            mb.disc_y(sx, sy + .15, .5, .5, .3, "tire", n=10)
    return mb.build()


def merch_stand(name):
    """stan merchandise: meja + rak kaos tergantung + papan kaos besar."""
    mb = W.MB(name)
    mb.box(-3, -1.2, 0, 3, -.2, 1.0, "tn_wood")
    mb.box(-3.2, -1.4, 1.0, 3.2, 0, 1.08, "tn_wood2")
    T.beam(mb, (-3, .6, 0), (-3, .6, 2.6), .06, "f_fence2")
    T.beam(mb, (3, .6, 0), (3, .6, 2.6), .06, "f_fence2")
    T.beam(mb, (-3, .6, 2.6), (3, .6, 2.6), .05, "f_fence2")
    for k in range(6):
        x = -2.5 + k * 1.0
        col = ("shirt_b", "shirt_w", "shirt_r", "shirt_b", "c_mustard", "shirt_w")[k]
        mb.poly([(x - .42, .6, 2.45), (x + .42, .6, 2.45), (x + .6, .6, 2.2), (x + .36, .6, 2.05), (x + .32, .6, 1.3),
                 (x - .32, .6, 1.3), (x - .36, .6, 2.05), (x - .6, .6, 2.2)], [tuple(range(8))], col)
    for k in range(5):
        L.rbox(mb, -2.6 + k * 1.2, -1.1, 1.08, -1.9 + k * 1.2, -.4, 1.24, ("shirt_b", "shirt_r", "shirt_w", "c_mustard",
                                                                             "shirt_b")[k], c=.04)
    # tote bag & topi
    mb.cyl(2.6, -.8, 1.08, 1.35, .25, "c_black2", n=10, r_top=.22)
    return mb.build()


def brand_booth(name, key_="sp1", key2="sp1b", s=1.0):
    """booth aktivasi sponsor generik: panggung mini berlantai warna, backdrop LED, gapura balon, kubus brand."""
    mb = W.MB(name)
    mb.box(-6 * s, -4 * s, 0, 6 * s, 4 * s, .35 * s, key2)
    mb.box(-6 * s, 3.4 * s, .35, 6 * s, 4 * s, 6.5 * s, key_)
    mb.box(-6.3 * s, 3.3 * s, 6.5 * s, 6.3 * s, 4.1 * s, 7.0 * s, key2)
    # gapura balon (lengkung)
    for i in range(14):
        a = math.pi * i / 13
        mb.sphere(math.cos(a) * 5.2 * s, -3.6 * s, .4 + math.sin(a) * 5.4 * s, .55 * s, key_ if i % 2 else "c_white")
    # kubus brand + meja
    L.rbox(mb, -4.8 * s, -1.5 * s, .35, -2.6 * s, .7 * s, 2.6 * s, key_, c=.2 * s)
    mb.box(1.5 * s, -1.0 * s, .35, 4.5 * s, .2 * s, 1.35 * s, "c_white")
    mb.box(1.4 * s, -1.1 * s, 1.35, 4.6 * s, .3 * s, 1.45 * s, key2)
    ob = mb.build()
    gl = W.MB(name + "_g")
    gl.box(-4.5 * s, 3.35 * s, 1.6 * s, 4.5 * s, 3.4 * s, 5.8 * s, "led_wh")
    go = gl.build()
    lit(go, key_, 2.5)
    go.parent = ob
    return ob


# ------------------------------------------------------------------ gerbang & tiket
def gate(name, w=26.0):
    """gerbang masuk festival: gapura truss + papan atas bercahaya + jalur antrean + pemindai tiket."""
    mb = W.MB(name)
    gl = W.MB(name + "_g")
    for sx in (-1, 1):
        _truss(mb, (sx * w / 2, 0, 0), (sx * w / 2, 0, 10), .9)
        mb.box(sx * w / 2 - 1.2, -1.2, 0, sx * w / 2 + 1.2, 1.2, .4, "f_fence2")
    _truss(mb, (-w / 2, 0, 10), (w / 2, 0, 10), .9)
    mb.box(-w / 2 + 2, -.5, 10.6, w / 2 - 2, .3, 14.2, "stg_black")
    gl.box(-w / 2 + 2.3, -.55, 10.9, w / 2 - 2.3, -.5, 13.9, "led_p")
    # jalur & pemindai
    lanes = 6
    for k in range(lanes + 1):
        x = -w / 2 + 2 + k * (w - 4) / lanes
        mb.box(x - .12, -14, 0, x + .12, 0, 1.1, "f_fence")
        mb.box(x - .35, -.6, 0, x + .35, .6, 1.25, "stg_deck2")
        gl.box(x - .25, -.62, 1.0, x + .25, -.6, 1.2, "led_g")
    ob = mb.build()
    go = gl.build()
    for i, m in enumerate(go.data.materials):
        k = m.name.split("_", 1)[1].rsplit("_", 1)[0]
        go.data.materials[i] = lp.mat(k, emission=3.0)
    go.parent = ob
    t = H.text(name + "_t", "FESTIVAL", 2.2, "led_wh", depth=.1, loc=(0, -.62, 11.3), emission=4.0)
    t.parent = ob
    return ob


def ticket(name, price="Rp225RB", key_="tk_blue", key2="tk_blue2", s=1.0, label="TIKET"):
    """tiket 3D berdiri (menghadap -Y): badan berwarna dengan sobekan, garis putus-putus, teks harga."""
    mb = W.MB(name)
    w, h = 4.2 * s, 2.0 * s
    prof = [(-w / 2, 0), (w / 2, 0), (w / 2, h * .38), (w / 2 - .25 * s, h * .5), (w / 2, h * .62), (w / 2, h),
            (-w / 2, h), (-w / 2, h * .62), (-w / 2 + .25 * s, h * .5), (-w / 2, h * .38)]
    mb.prism_y(prof, -.08 * s, .08 * s, key_)
    for k in range(7):
        z = .15 * s + k * .26 * s
        mb.box(w * .22 - .03 * s, -.1 * s, z, w * .22 + .03 * s, -.08 * s, z + .14 * s, "tk_paper")
    mb.box(w * .27, -.1 * s, .3 * s, w / 2 - .35 * s, -.08 * s, h - .3 * s, key2)
    ob = mb.build()
    t = H.text(name + "_p", price, .5 * s, "tk_paper", depth=.03 * s, loc=(-.45 * s, -.11 * s, .45 * s))
    t.parent = ob
    t2 = H.text(name + "_l", label, .36 * s, "tk_paper", depth=.03 * s, loc=(-.45 * s, -.11 * s, 1.2 * s))
    t2.parent = ob
    return ob


def wristband(name, s=1.0, key_="band_r"):
    """gelang festival (cincin pipih berdiri) + kepala chip."""
    mb = W.MB(name)
    n = 20
    r, t = 1.0 * s, .28 * s
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        p = [(math.cos(a0) * r, -t, math.sin(a0) * r), (math.cos(a1) * r, -t, math.sin(a1) * r),
             (math.cos(a1) * r, t, math.sin(a1) * r), (math.cos(a0) * r, t, math.sin(a0) * r)]
        q = [(x * .86, y, z * .86) for x, y, z in p]
        mb.poly(p + q, [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (3, 2, 6, 7)], key_)
    L.rbox(mb, -.35 * s, -.32 * s, -1.12 * s, .35 * s, .32 * s, -.82 * s, "tk_gold", c=.08 * s)
    return mb.build()


# ------------------------------------------------------------------ belakang panggung
def backstage(name, loc, w=40.0):
    """area belakang panggung: truk boks, genset, peti alat (road case), tenda kru, kabel."""
    ox, oy = loc
    mb = W.MB(name)
    mb.box(ox - w / 2, oy, -.02, ox + w / 2, oy + 24, .02, "f_dirt")
    # 2 truk boks
    for k, x in enumerate((ox - 12, ox + 10)):
        y = oy + 14
        mb.box(x - 2.4, y - 6, .9, x + 2.4, y + 4, 5.6, "truck_box")
        L.rbox(mb, x - 2.3, y - 9.2, .9, x + 2.3, y - 6.2, 4.4, ("tn_red", "tent_b")[k], c=.25)
        mb.box(x - 2.1, y - 9.25, 3.0, x + 2.1, y - 9.2, 4.1, "ct_glass3")
        for yy in (y - 7.8, y - 3, y + 2.5):
            for sx in (-1, 1):
                mb.disc_y(x + sx * 2.35, yy + .3, .65, .65, .5, "tire", n=10)
        # rampa
        mb.prism_x([(y - 6, .9), (y - 6, 1.0), (y - 10.5, 0), (y - 10.5, -.05)], x - 1.2, x + 1.2, "f_fence2")
    # genset
    for x in (ox + 17, ox - 18):
        L.rbox(mb, x - 1.5, oy + 4, 0, x + 1.5, oy + 9, 2.6, "gen", c=.15)
        mb.box(x - 1.3, oy + 3.95, .4, x + 1.3, oy + 4, 2.2, "gen2")
        mb.cyl(x + .8, oy + 8, 2.6, 3.6, .2, "gen2", n=8)
    # road case bertumpuk
    rnd = random.Random(4)
    for k in range(14):
        x = ox - 6 + (k % 7) * 1.9
        y = oy + 3 + (k // 7) * 2.0
        hh = rnd.choice((1.0, 1.3, 1.6))
        L.rbox(mb, x - .8, y - .7, 0, x + .8, y + .7, hh, "case", c=.06)
        mb.box(x - .82, y - .72, hh - .2, x + .82, y + .72, hh - .1, "case2")
        if rnd.random() < .5:
            L.rbox(mb, x - .7, y - .6, hh, x + .7, y + .6, hh + 1.0, "case", c=.06)
    # tenda kru
    for x in (ox - 2, ox + 4):
        y = oy + 18
        for sx in (-1, 1):
            for sy in (-1, 1):
                mb.cyl(x + sx * 2, y + sy * 2, 0, 2.6, .05, "f_fence2", n=6)
        mb.poly([(x - 2.2, y - 2.2, 2.6), (x + 2.2, y - 2.2, 2.6), (x + 2.2, y + 2.2, 2.6), (x - 2.2, y + 2.2, 2.6),
                 (x, y, 3.6)], [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)], "tent_w")
    # kabel (gulungan pipih) ke panggung
    for k in range(4):
        x = ox - 5 + k * 3
        mb.box(x - .07, oy - 2, .02, x + .07, oy + 6, .09, "stg_black")
    return mb.build()


# ------------------------------------------------------------------ efek
def firework(name, loc, f0, key_="led_m", r=6.0, n=26, seed=1, life=26):
    """kembang api: bola-bola kecil memancar dari pusat (skala 0 -> 1) lalu meredup + jatuh sedikit."""
    from scenes import key
    rnd = random.Random(seed)
    mb = W.MB(name)
    for i in range(n):
        u = rnd.uniform(-1, 1)
        a = rnd.uniform(0, 2 * math.pi)
        rr = math.sqrt(1 - u * u)
        d = (rr * math.cos(a), rr * math.sin(a), u)
        for t_ in (1.0, .8, .62):
            mb.sphere(d[0] * r * t_, d[1] * r * t_, d[2] * r * t_, .22 * (1.2 - t_ * .5), key_)
    ob = mb.build(loc)
    ob.data.materials.clear()
    m = lp.mat(key_, emission=12.0)
    ob.data.materials.append(m)
    no_light(ob)
    key(ob, "scale", 1, (.001,) * 3)
    key(ob, "scale", max(1, f0), (.001,) * 3)
    key(ob, "scale", f0 + 8, (1, 1, 1))
    key(ob, "scale", f0 + life, (1.25, 1.25, 1.25))
    key(ob, "scale", f0 + life + 2, (.001,) * 3)
    key(ob, "location", f0 + 8, loc)
    key(ob, "location", f0 + life, (loc[0], loc[1], loc[2] - 1.5))
    return ob


def fireworks(prefix, center, f0, f1, spread=(30, 10, 8), every=16, seed=3):
    rnd = random.Random(seed)
    cols = ("led_m", "led_c", "led_o", "led_p", "tk_gold", "led_wh")
    f = f0
    k = 0
    while f < f1 - 10:
        p = (center[0] + rnd.uniform(-spread[0], spread[0]), center[1] + rnd.uniform(-spread[1], spread[1]),
             center[2] + rnd.uniform(-spread[2], spread[2]))
        firework(f"{prefix}{k}", p, f, rnd.choice(cols), rnd.uniform(4.5, 7.5), seed=seed * 100 + k)
        f += every + rnd.randint(-4, 6)
        k += 1


def confetti(name, center, f0, f1, n=160, area=(16, 8), h=14.0, seed=5):
    """konfeti jatuh berputar (satu objek per 'lapisan' supaya murah)."""
    from scenes import key
    rnd = random.Random(seed)
    cols = ("led_m", "led_c", "tk_gold", "led_wh", "led_p", "led_o")
    obs = []
    for g in range(4):
        mb = W.MB(f"{name}{g}")
        for i in range(n // 4):
            x = rnd.uniform(-area[0], area[0])
            y = rnd.uniform(-area[1], area[1])
            z = rnd.uniform(0, h)
            a = rnd.uniform(0, math.pi)
            dx, dz = math.cos(a) * .22, math.sin(a) * .22
            mb.poly([(x - dx, y - .02, z - dz), (x + dx, y - .02, z + dz), (x + dx + .05, y + .1, z + dz + .14),
                     (x - dx + .05, y + .1, z - dz + .14)], [(0, 1, 2, 3)], rnd.choice(cols))
        ob = mb.build((center[0], center[1], center[2] + h))
        for i, m in enumerate(ob.data.materials):
            k = m.name.split("_", 1)[1].rsplit("_", 1)[0]
            ob.data.materials[i] = lp.mat(k, emission=1.5)
        no_light(ob)
        key(ob, "location", 1, (center[0], center[1], center[2] + h + 30))
        key(ob, "location", max(1, f0 + g * 4), (center[0], center[1], center[2] + h + 2))
        key(ob, "location", f1, (center[0], center[1], center[2] - h * .25 + g * 1.2))
        key(ob, "rotation_euler", f0, (0, 0, 0))
        key(ob, "rotation_euler", f1, (0, 0, (g - 1.5) * .35))
        obs.append(ob)
    return obs


# ------------------------------------------------------------------ ikon biaya
def cost_icon(name, kind, s=1.0):
    """ikon 3D: artis (mic + bintang), panggung (truss mini + atap), venue (lapangan + pin),
    keamanan (perisai), kru (headset + papan klip), operasional (genset + roda gigi)."""
    mb = W.MB(name)
    if kind == "artis":
        mb.cyl(0, 0, 0, .1, .6, "stg_truss2", n=10)
        T.beam(mb, (0, 0, .1), (0, 0, 1.6), .05, "stg_truss2")
        mb.cyl(0, 0, 1.6, 2.2, .2, "mic", n=10)
        mb.sphere(0, 0, 2.3, .26, "mic_grill")
        pts = []
        for k in range(10):
            a = math.pi / 2 + k * math.pi / 5
            rr = .75 if k % 2 == 0 else .32
            pts.append((.9 + math.cos(a) * rr, 2.6 + math.sin(a) * rr))
        mb.prism_y(pts, -.1, .1, "tk_gold")
    elif kind == "panggung":
        mb.box(-1.4, -.9, 0, 1.4, .9, .5, "stg_deck")
        for sx in (-1, 1):
            _truss(mb, (sx * 1.25, -.75, .5), (sx * 1.25, -.75, 2.6), .22)
        _truss(mb, (-1.25, -.75, 2.6), (1.25, -.75, 2.6), .22)
        mb.box(-1.2, .7, .5, 1.2, .85, 2.4, "led_m")
        mb.box(-1.5, -1.0, 2.75, 1.5, 1.0, 2.9, "stg_black")
    elif kind == "venue":
        mb.box(-1.6, -1.2, 0, 1.6, 1.2, .2, "f_grass")
        mb.box(-1.6, -.12, .2, 1.6, .12, .22, "f_path")
        for sx in (-1, 1):
            for sy in (-1, 1):
                mb.cyl(sx * 1.5, sy * 1.1, .2, .7, .05, "f_fence2", n=6)
        prof = []
        for k in range(16):
            a = 2 * math.pi * k / 16
            prof.append((math.cos(a) * .55, 2.1 + math.sin(a) * .55))
        mb.prism_y(prof, -.15, .15, "tn_red")
        mb.prism_y([(-.42, 1.75), (.42, 1.75), (0, .3)], -.15, .15, "tn_red")
        mb.disc_y(0, -.16, 2.1, .22, .03, "c_white", n=12)
    elif kind == "keamanan":
        prof = [(-1, 2.6), (1, 2.6), (1, 1.4), (0, .2), (-1, 1.4)]
        mb.prism_y(prof, -.18, .18, "shield")
        prof2 = [(-.75, 2.4), (.75, 2.4), (.75, 1.45), (0, .5), (-.75, 1.45)]
        mb.prism_y(prof2, -.22, -.18, "c_white")
        mb.prism_y([(-.4, 1.6), (-.15, 1.35), (.45, 1.95), (.3, 2.1), (-.15, 1.62), (-.28, 1.75)], -.26, -.22, "shield")
    elif kind == "kru":
        L.rbox(mb, -.8, -.1, 0, .8, .1, 2.1, "tn_wood", c=.06)
        mb.box(-.68, -.13, .1, .68, -.1, 1.85, "paper_w")
        for k in range(4):
            mb.box(-.5, -.15, 1.5 - k * .32, .5 - (k % 2) * .3, -.13, 1.6 - k * .32, "paper_l")
        mb.box(-.3, -.15, 1.95, .3, -.08, 2.15, "metal")
        # headset di atas
        n = 10
        for i in range(n):
            a0, a1 = math.pi * i / n, math.pi * (i + 1) / n
            T.beam(mb, (math.cos(a0) * .7, -.35, 2.5 + math.sin(a0) * .7), (math.cos(a1) * .7, -.35, 2.5 + math.sin(a1) * .7),
                   .07, "headset")
        for sx in (-1, 1):
            mb.disc_y(sx * .7, -.2, 2.45, .28, .3, "headset", n=10)
    else:                                       # operasional
        L.rbox(mb, -1.3, -.8, 0, 1.3, .8, 1.5, "gen", c=.12)
        mb.box(-1.1, -.82, .3, 1.1, -.8, 1.2, "gen2")
        n = 12
        prof = []
        for k in range(n * 2):
            a = 2 * math.pi * k / (n * 2)
            rr = .85 if k % 2 == 0 else .65
            prof.append((math.cos(a) * rr, 2.45 + math.sin(a) * rr))
        mb.prism_y(prof, -.15, .15, "stg_truss2")
        mb.disc_y(0, -.16, 2.45, .3, .05, "stg_deck", n=10)
    return mb.build()


def warn_sign(name, s=1.0):
    """segitiga peringatan kuning + tanda seru (berdiri menghadap -Y)."""
    mb = W.MB(name)
    mb.prism_y([(-1.3 * s, 0), (1.3 * s, 0), (0, 2.25 * s)], -.12 * s, .12 * s, "warn")
    mb.prism_y([(-1.0 * s, .2 * s), (1.0 * s, .2 * s), (0, 1.95 * s)], -.14 * s, -.12 * s, "stg_black")
    mb.prism_y([(-.85 * s, .3 * s), (.85 * s, .3 * s), (0, 1.75 * s)], -.16 * s, -.14 * s, "warn")
    mb.box(-.1 * s, -.18 * s, .75 * s, .1 * s, -.16 * s, 1.45 * s, "stg_black")
    mb.box(-.1 * s, -.18 * s, .45 * s, .1 * s, -.16 * s, .62 * s, "stg_black")
    return mb.build()


# ------------------------------------------------------------------ dunia festival
STAGES = [  # (x, y, kind, s, rot) -> 18 panggung kecil + panggung utama = 19
    (-62, 52, "tent", 1.0, 0), (64, 50, "dome", 1.0, 0), (-104, 18, "box", 1.0, .4), (100, 14, "open", 1.0, -.4),
    (-40, 104, "hall", 1.0, 0), (42, 106, "tent", .9, 0), (-92, 92, "dome", .8, .3), (124, 88, "box", 1.0, -.3),
    (-138, 60, "open", .9, .6), (150, 52, "tent", .8, -.5), (-6, 142, "open", 1.1, 0), (-70, 140, "box", .9, .2),
    (80, 148, "hall", .9, -.2), (-150, 120, "tent", .8, .5), (160, 130, "dome", .8, -.4), (-128, -22, "tent", .8, .6),
    (132, -30, "box", .9, -.6), (-30, 178, "dome", .9, 0),
]
FERRIS = (118, 192 - 70)
GATE_Y = -70.0


def build_fest(seed=5, crowd=True, stages=True, city=True, people_density=1.0, wheel=True, booths=True, ext=260.0):
    """lapangan festival lengkap. Return info dict."""
    rnd = random.Random(seed)
    info = {}
    g = W.MB("f_ground")
    g.box(-ext * 3, -ext * 3, -1.2, ext * 3, ext * 3, -.6, "f_far")
    g.box(-ext, -ext * .55, -1, ext, ext, 0, "f_grass")
    for k in range(40):                                    # petak rumput beda warna
        x, y = rnd.uniform(-ext, ext), rnd.uniform(-ext * .5, ext)
        g.box(x - rnd.uniform(6, 16), y - rnd.uniform(6, 16), -.98, x + rnd.uniform(6, 16), y + rnd.uniform(6, 16),
              .001 + k * .0005, "f_grass2")          # tinggi beda tiap petak (hindari bidang bertumpuk -> hitam)
    # jalur utama: gerbang -> panggung utama, dan lingkar
    g.box(-5, GATE_Y - 20, 0, 5, MAIN[1] - 30, .03, "f_path")
    for j, (x0, y0, x1, y1) in enumerate(((-150, -12, 150, -6), (-150, 80, 150, 86), (-80, -12, -74, 170),
                                           (74, -12, 80, 170))):
        g.box(x0, y0, 0, x1, y1, .036 + j * .004, "f_path2")
    # pagar keliling
    for k in range(int(2 * ext / 4)):
        x = -ext + k * 4
        g.box(x, -ext * .55 + 50, 0, x + 3.8, -ext * .55 + 50.2, 1.6, "f_fence")
    g.build()
    # kota di kejauhan
    if city:
        sk = W.MB("f_city")
        for k in range(70):
            a = rnd.uniform(-.25, 1.25) * math.pi
            r = rnd.uniform(ext + 30, ext + 170)
            cx, cy = math.cos(a) * r, math.sin(a) * r * .8 + 60
            if cy < -60:
                continue
            C.tower(sk, cx, cy, rnd.uniform(12, 22), rnd.uniform(12, 22), rnd.uniform(40, 120), rnd)
        sk.build()
    # panggung utama + penonton
    ms = main_stage("ms", MAIN)
    info["main"] = ms
    if crowd:
        y_front = MAIN[1] - STAGE_D / 2 - 6
        obs, ph = fest_crowd("fc", int(1500 * people_density), -30, y_front - 46, 30, y_front, seed=seed, s=1.15)
        info["crowd"] = obs
        info["phones"] = ph
        # FOH (tenda mixing) di tengah penonton
        fo = W.MB("foh")
        fo.box(-3, y_front - 30, 0, 3, y_front - 26, 1.2, "stg_deck")
        for sx in (-1, 1):
            for sy in (-1, 1):
                fo.cyl(sx * 2.9, y_front - 28 + sy * 1.9, 1.2, 4.2, .08, "stg_truss2", n=6)
        fo.box(-3.3, y_front - 30.3, 4.2, 3.3, y_front - 25.7, 4.5, "stg_black")
        fo.build()
    # panggung kecil (18)
    info["stages"] = [("UTAMA", (MAIN[0], MAIN[1], 26.0))]
    if stages:
        for k, (x, y, kind, s, rot) in enumerate(STAGES):
            st = small_stage(f"ss{k}", (x, y), kind, s, rot)
            info["stages"].append((kind, (x, y, st["top"])))
            if crowd:
                fest_crowd(f"sc{k}", int(70 * people_density * s), x - 8 * s, y - 24 * s, x + 8 * s, y - 11 * s,
                           seed=seed + k, s=1.0, groups=1, phone_frac=.05)
    # bianglala
    if wheel:
        info["wheel"] = ferris_wheel("fw", FERRIS, 15)
    # tenant & booth
    if booths:
        mb = W.MB("stalls")
        cols = ("tn_red", "tn_yel", "tn_grn", "tn_blu")
        for k in range(10):
            food_stall(mb, -58 + k * 4.0, -24, cols[k % 4], rnd)
            food_stall(mb, 22 + k * 4.0, -24, cols[(k + 2) % 4], rnd)
        mb.build()
        for k, x in enumerate((-30, 30)):
            ft = food_truck(f"ftr{k}", ("tn_yel", "tent_b")[k])
            ft.location = (x * 1.9, -36, 0)
        ms_ = merch_stand("merch")
        ms_.location = (-14, -14, 0)
        info["booths"] = []
        for k, (x, y, a, b) in enumerate(((-26, -2, "sp1", "sp1b"), (26, -2, "sp2", "sp2b"), (0, -50, "sp3", "sp3b"))):
            bb = brand_booth(f"bb{k}", a, b, 1.0)
            bb.location = (x, y, 0)
            info["booths"].append((x, y))
        # area makan: untaian lampu + penonton jajan
        gl = W.MB("f_bulbs")
        for k in range(5):
            string_lights(gl, (-60 + k * 8, -28, 4.2), (-52 + k * 8, -20, 4.2), 10, .7)
            string_lights(gl, (20 + k * 8, -28, 4.2), (28 + k * 8, -20, 4.2), 10, .7)
        lp_ = W.MB("f_poles")
        for (x, y) in ((-34, -10), (34, -10), (-34, 30), (34, 30), (-70, 70), (70, 70), (0, -50), (-100, 40), (100, 40)):
            light_pole(lp_, gl, x, y, 12)
        lp_.build()
        go = gl.build()
        lit(go, "bulb", 6.0)
        fest_crowd("fcf", int(160 * people_density), -60, -18, 60, -6, seed=seed + 50, s=1.0, groups=1, arms_frac=.1,
                   phone_frac=.0)
    # gerbang
    gt = gate("gate")
    gt.location = (0, GATE_Y, 0)
    info["gate"] = gt
    return info


# ------------------------------------------------------------------ panggung data (close-up deck)
def data_stage(name="ds", crowd_n=260, beams=True, seed=4):
    """panggung utama dari dekat untuk adegan angka: deck lebar dengan dinding LED di belakang, penonton
    siluet di depan (y < -9), tanpa band. Titik tengah deck = (0, 0, DECK_H)."""
    ms = main_stage(name, (0, 6.0), beams=beams, lights=False, beam_str=.3, led_em=1.0)
    # cahaya panggung untuk properti data
    spot(name + "_k1", (-10, -16, 14), (-2, 2, DECK_H + 2), 7000, 50, (1.0, .82, .92))
    spot(name + "_k2", (10, -16, 14), (2, 2, DECK_H + 2), 7000, 50, (.82, .92, 1.0))
    spot(name + "_k3", (0, -6, 18), (0, 3, DECK_H), 5000, 45, (1.0, .95, .85))
    point(name + "_bk", (0, 10, DECK_H + 9), 6000, (.75, .45, 1.0), 3.0)
    obs, ph = fest_crowd(name + "_cr", crowd_n, -22, -26, 22, -6.8, seed=seed, s=1.15, groups=3)
    g = W.MB(name + "_gr")
    g.box(-300, -300, -1, 300, 300, -.02, "f_grass2")
    g.build()
    ms["crowd"] = obs
    ms["phones"] = ph
    return ms
