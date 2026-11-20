"""Aset dunia "Cara brand vape bertahan di tengah fatwa haram" (FOOM): kota diorama Jakarta bernuansa pink sakura
+ panggung neon. Tekstur (logo resmi FOOM, poster campaign, tangkapan artikel berita asli) dibaca dari env FOM_TEX
(dibuat oleh render/fom_assets.py; tidak disimpan di repo).

Isi: logo FOOM 3D (SVG hasil trace), HP raksasa berisi artikel berita yang di-scroll, pohon sakura & kelopak jatuh,
kota (billboard poster campaign, toko vape, menara FOOM), dokumen fatwa, palu, kartu pernyataan, lencana 21+,
perangkat pod pink, gerbang torii neon.
"""
import math
import os
import random

import bpy  # noqa: F401

import lowpoly as lp
import world as W
import world_gta as G
import world_hotel as H
import world_laundry as L
import world_vap as V

TEX = os.environ.get("FOM_TEX", "/tmp/claude-0/-home-user-Bbg/e4570b9b-8bb7-5f4c-a29b-693bb3cf9daa/scratchpad/fom/tex")
G.TEX = TEX                                     # img_plane / screen / img_mat milik world_gta memakai folder ini

POSTERS = ["p_pink", "p_wm", "p_sipaling", "p_ybglass", "p_bloom", "p_guy", "p_yb", "p_blue", "p_eksplor",
           "p_collab", "p_girl"]
ARTS = ["art_sewa", "art_cnn", "art_mui", "art_phk", "art_200", "art_detik"]

lp.PAL.update({
    "sk_pink": "#FFB3D1", "sk_pink2": "#FF8CC0", "sk_pink3": "#FFD3E4", "sk_trunk": "#4A2E33",
    "fm_black": "#151019", "fm_dark": "#231B2B", "fm_pink": "#FF4FA8", "fm_glass": "#3B2A55",
    "doc_paper": "#F3EFE6", "doc_line": "#8E8799", "doc_red": "#E8264A", "ok_green": "#21D07A",
    "ph_body": "#16121C", "ph_rim": "#C9C3D6", "torii": "#FF3355", "badge_red": "#E0203F",
    "gavel_w": "#6B3A22", "gavel_d": "#3A1E12", "pod_pink": "#FF8FC2", "pod_dark": "#2A2230",
})


# ================================================================== logo FOOM 3D
def foom_logo(name, s=6.0, loc=(0, 0, 0), key_="n_white", em=3.0, depth=.25, plate=None):
    """logo FOOM resmi (hasil trace SVG) diekstrusi; berdiri menghadap -Y, pivot tengah. s = lebar logo.
    plate: kunci warna pelat belakang (opsional, kotak neon di belakang tulisan)."""
    import addon_utils
    addon_utils.enable("io_curve_svg", default_set=False)
    before = set(bpy.data.objects)
    bpy.ops.import_curve.svg(filepath=os.path.join(TEX, "foom.svg"))
    new = [o for o in bpy.data.objects if o not in before and o.type == "CURVE"]
    xs, ys = [], []
    for o in new:
        for sp in o.data.splines:
            for p in sp.bezier_points:
                v = o.matrix_world @ p.co
                xs.append(v.x)
                ys.append(v.y)
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    sc = s / (max(xs) - min(xs))
    root = bpy.data.objects.new(name, None)
    lp._link(root)
    for i, o in enumerate(new):
        o.data.extrude = depth / sc / 2
        o.data.offset = 0
        o.data.fill_mode = "BOTH"
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
        me.transform(o.matrix_world)
        me.materials.clear()
        me.materials.append(lp.mat(key_, emission=em))
        ob = bpy.data.objects.new(f"{name}_{i}", me)
        lp._link(ob)
        bpy.data.objects.remove(o)
        ob.parent = root
        ob.rotation_euler = (math.pi / 2, 0, 0)
        ob.scale = (sc, sc, sc)
        ob.location = (-cx * sc, 0, -cy * sc)
    for c in list(bpy.data.collections):
        if c.name.lower().endswith(".svg"):
            for o in list(c.objects):
                c.objects.unlink(o)
            bpy.data.collections.remove(c)
    if plate:
        h = s * 274 / 790
        mb = W.MB(name + "_pl")
        mb.box(-s / 2 - .5, depth, -h / 2 - .45, s / 2 + .5, depth + .25, h / 2 + .45, "fm_black")
        t = .08
        for (a, b, c, d) in ((-s / 2 - .5, -h / 2 - .45, s / 2 + .5, -h / 2 - .45 + t),
                             (-s / 2 - .5, h / 2 + .45 - t, s / 2 + .5, h / 2 + .45),
                             (-s / 2 - .5, -h / 2 - .45, -s / 2 - .5 + t, h / 2 + .45),
                             (s / 2 + .5 - t, -h / 2 - .45, s / 2 + .5, h / 2 + .45)):
            mb.box(a, depth - .05, b, c, depth, d, plate)
        po = mb.build(parent=root)
        V.glow(po, {plate: 6.0})
    root.location = loc
    return root


# ================================================================== HP raksasa + artikel berita yang di-scroll
def article_phone(name, img, h=9.0, loc=(0, 0, 0), rot_z=0.0, scroll=None, em=1.25, tilt=0.0):
    """HP berdiri menghadap -Y (pivot bawah-tengah) berisi tangkapan artikel berita asli.
    scroll: [(frame, u)] u = 0 (paling atas) .. 1 (sejauh mungkin ke bawah)."""
    w = h * .47
    sw, sh = w * .92, h * .9
    root = bpy.data.objects.new(name, None)
    lp._link(root)
    mb = W.MB(name + "_body")
    L.rbox(mb, -w / 2, .02, 0, w / 2, .5, h, "ph_body", c=w * .12)
    mb.box(-w / 2 - .04, .1, h * .02, -w / 2, .42, h * .98, "ph_rim")
    mb.box(w / 2, .1, h * .02, w / 2 + .04, .42, h * .98, "ph_rim")
    mb.box(-w * .12, -.01, h * .955, w * .12, .02, h * .975, "fm_black")      # notch/pulau dinamis
    bo = mb.build(parent=root)
    me = G._quad_mesh(name + "_scr", sw, sh)
    m = G.img_mat(img, em, False, False, mapping=True)
    nt = m.node_tree
    mp = [n for n in nt.nodes if n.type == "MAPPING"][0]
    iw, ih = G.img_size(img)
    frac = min(1.0, (sh / sw) / (ih / iw))
    mp.inputs["Scale"].default_value = (1, frac, 1)

    def _set(f, u):
        mp.inputs["Location"].default_value = (0, (1 - frac) * (1 - u), 0)
        mp.inputs["Location"].keyframe_insert("default_value", frame=f)
    for f, u in (scroll or [(1, 0.0)]):
        _set(f, u)
    me.materials.append(m)
    so = bpy.data.objects.new(name + "_scr", me)
    lp._link(so)
    so.parent = root
    so.location = (0, 0, h * .05)
    root.location = loc
    root.rotation_euler = (tilt, 0, rot_z)
    return {"root": root, "screen": so, "body": bo, "w": w, "h": h}


def news_wall(name, imgs, loc=(0, 0, 0), h=8.0, gap=1.2, arc=10.0, n_frames=200, scroll_speed=.35):
    """dinding HP berita melengkung (tiap HP menggulir pelan)."""
    out = []
    n = len(imgs)
    for i, im in enumerate(imgs):
        a = (i - (n - 1) / 2) * math.radians(arc)
        x = loc[0] + (i - (n - 1) / 2) * (h * .47 + gap)
        y = loc[1] + abs(i - (n - 1) / 2) * 1.3
        ph = article_phone(f"{name}{i}", im, h, (x, y, loc[2]), -a * .9,
                           scroll=[(1, 0.0), (n_frames, min(1.0, scroll_speed))])
        out.append(ph)
    return out


# ================================================================== sakura
def sakura_tree(mb, x, y, s=1.0, rnd=None, z=0.0):
    rnd = rnd or random
    mb.cyl(x, y, z, z + 1.9 * s, .2 * s, "sk_trunk", n=7, r_top=.13 * s)
    for k in range(3):
        a = k * 2.1 + rnd.uniform(-.3, .3)
        mb.cyl(x + math.cos(a) * .35 * s, y + math.sin(a) * .35 * s, z + 1.6 * s, z + 2.5 * s, .08 * s, "sk_trunk", n=5)
    for k in range(6):
        a = k * 1.05 + rnd.uniform(-.4, .4)
        r = rnd.uniform(.35, .85) * s
        mb.sphere(x + math.cos(a) * r, y + math.sin(a) * r, z + rnd.uniform(2.4, 3.1) * s, rnd.uniform(.75, 1.05) * s,
                  rnd.choice(("sk_pink", "sk_pink2", "sk_pink3")), sz=rnd.uniform(.6, .8) * s)


def sakura_patch():
    """ganti pohon jalan diorama dengan pohon sakura."""
    def _tree(mb, x, y, s, rnd):
        sakura_tree(mb, x, y, s * 1.05, rnd)
    V.C.street_tree = _tree


def petals(name, n=60, area=(-10, -8, 10, 8), z=(3, 14), f0=1, f1=200, seed=5, s=.16):
    """kelopak sakura berjatuhan (objek kecil, gerak linear + berputar). Satu material emisi lembut."""
    rnd = random.Random(seed)
    me = bpy.data.meshes.new(name + "_m")
    me.from_pydata([(-s, 0, 0), (0, 0, s * .6), (s, 0, 0), (0, 0, -s * .6)], [], [(0, 1, 2, 3)])
    me.materials.append(lp.mat("sk_pink", emission=1.2))
    obs = []
    span = f1 - f0
    for i in range(n):
        ob = bpy.data.objects.new(f"{name}{i}", me)
        lp._link(ob)
        x, y = rnd.uniform(area[0], area[2]), rnd.uniform(area[1], area[3])
        zt = rnd.uniform(*z)
        fall = rnd.uniform(.9, 1.6) * (z[1] - z[0]) / max(1, span) * 1.2
        ph = rnd.uniform(0, 1)
        z_start = zt - ph * (z[1] - z[0])
        za, zb = z_start + (z[1] - z[0]) * .5, z_start + (z[1] - z[0]) * .5 - fall * span
        dx = rnd.uniform(-2.5, 2.5)
        ob.location = (x, y, za)
        ob.keyframe_insert("location", frame=f0)
        ob.location = (x + dx, y + rnd.uniform(-1, 1), zb)
        ob.keyframe_insert("location", frame=f1)
        ob.rotation_euler = (rnd.uniform(0, 6), rnd.uniform(0, 6), rnd.uniform(0, 6))
        ob.keyframe_insert("rotation_euler", frame=f0)
        ob.rotation_euler = (ob.rotation_euler.x + rnd.uniform(4, 9), ob.rotation_euler.y + rnd.uniform(3, 7),
                             ob.rotation_euler.z + rnd.uniform(-3, 3))
        ob.keyframe_insert("rotation_euler", frame=f1)
        if ob.animation_data and ob.animation_data.action:
            _linear(ob.animation_data.action)
        obs.append(ob)
    return obs


def _linear(action):
    try:
        curves = action.fcurves
    except AttributeError:                      # Blender 5: action berlapis
        curves = [fc for ly in action.layers for st in ly.strips for cb in st.channelbags for fc in cb.fcurves]
    for fc in curves:
        for k in fc.keyframe_points:
            k.interpolation = "LINEAR"


def torii(name, loc=(0, 0, 0), s=1.0, key_="torii", em=4.0):
    """gerbang torii neon (nuansa pop Jepang)."""
    mb = W.MB(name)
    for sx in (-1, 1):
        mb.cyl(sx * 2.6 * s, 0, 0, 6.2 * s, .32 * s, key_, n=12)
        mb.cyl(sx * 2.6 * s, 0, 0, .5 * s, .45 * s, "fm_black", n=12)
    mb.box(-3.9 * s, -.35 * s, 6.2 * s, 3.9 * s, .35 * s, 6.75 * s, key_)
    mb.box(-3.4 * s, -.25 * s, 5.0 * s, 3.4 * s, .25 * s, 5.35 * s, key_)
    mb.box(-4.3 * s, -.45 * s, 6.75 * s, 4.3 * s, .45 * s, 7.05 * s, "fm_black")
    mb.box(-.2 * s, -.2 * s, 5.35 * s, .2 * s, .2 * s, 6.2 * s, key_)
    ob = mb.build(loc)
    V.glow(ob, {key_: em})
    return ob


# ================================================================== properti cerita
def document(name, loc=(0, 0, 0), s=1.0, title="FATWA", sub="No. 131 Tahun 2026", stamp=None, lines=7,
             title_key="doc_red"):
    """lembar dokumen berdiri (menghadap -Y): kertas + judul 3D + baris teks abu + cap opsional."""
    w, h = 4.2 * s, 5.6 * s
    root = bpy.data.objects.new(name, None)
    lp._link(root)
    mb = W.MB(name + "_pp")
    mb.box(-w / 2, 0, 0, w / 2, .06 * s, h, "doc_paper")
    for k in range(lines):
        zz = h * .62 - k * .42 * s
        ww = w * (.78 if k % 3 else .6)
        mb.box(-w / 2 + .4 * s, -.01, zz, -w / 2 + .4 * s + ww, 0, zz + .12 * s, "doc_line")
    mb.box(-w / 2 + .4 * s, -.01, h * .76, w / 2 - .4 * s, 0, h * .76 + .04 * s, title_key)
    pp = mb.build(parent=root)
    t1 = H.text(name + "_t", title, .78 * s, title_key, depth=.06, loc=(0, -.04, h * .82), emission=.6)
    t1.parent = root
    t2 = H.text(name + "_s", sub, .3 * s, "fm_black", depth=.03, loc=(0, -.04, h * .7), emission=0.0)
    t2.parent = root
    st = None
    if stamp:
        st = H.text(name + "_st", stamp, .62 * s, "doc_red", depth=.06, loc=(0, -.12, h * .22), emission=1.4,
                    rot=(math.pi / 2, math.radians(-12), 0))
        st.parent = root
    root.location = loc
    return {"root": root, "paper": pp, "stamp": st, "w": w, "h": h}


def gavel(name, loc=(0, 0, 0), s=1.0):
    """palu hakim: kepala silinder + gagang; poros di ujung gagang (untuk ayunan rotasi Y)."""
    piv = bpy.data.objects.new(name, None)
    lp._link(piv)
    mb = W.MB(name + "_g")
    mb.box(-.1 * s, -.1 * s, 0, .1 * s, .1 * s, 2.4 * s, "gavel_w")           # gagang (sumbu Z)
    hd = W.MB(name + "_h")
    hd.cyl(0, 0, -.9 * s, .9 * s, .42 * s, "gavel_w", n=16)
    hd.cyl(0, 0, -1.0 * s, -.86 * s, .45 * s, "n_gold", n=16)
    hd.cyl(0, 0, .86 * s, 1.0 * s, .45 * s, "n_gold", n=16)
    g = mb.build(parent=piv)
    h = hd.build(parent=piv)
    h.rotation_euler = (0, math.pi / 2, 0)
    h.location = (0, 0, 2.4 * s)
    V.glow(h, {"n_gold": 3.0})
    block = W.MB(name + "_b")
    block.cyl(0, 0, 0, .35 * s, 1.0 * s, "gavel_d", n=20)
    block.cyl(0, 0, .3 * s, .36 * s, 1.02 * s, "n_gold", n=20)
    bo = block.build((loc[0] + 2.4 * s, loc[1], loc[2]))
    V.glow(bo, {"n_gold": 3.0})
    piv.location = loc
    return {"piv": piv, "block": bo}


def badge21(name, loc=(0, 0, 0), s=1.0, em=3.0):
    """lencana bulat 21+ (merah, cincin putih)."""
    mb = W.MB(name)
    mb.disc_y(0, .1 * s, 0, 1.0 * s, .2 * s, "n_white", n=40)
    mb.disc_y(0, -.06 * s, 0, .86 * s, .12 * s, "badge_red", n=40)
    ob = mb.build(loc)
    V.glow(ob, {"n_white": em, "badge_red": em * .6})
    t = H.text(name + "_t", "21+", .78 * s, "n_white", depth=.06, loc=(loc[0], loc[1] - .3 * s, loc[2] - .28 * s),
               emission=em * 1.5)
    t.parent = None
    return ob, t


def warn_strip(name, loc=(0, 0, 0), w=10.0, s=1.0, text="PERINGATAN: MENGANDUNG NIKOTIN"):
    """pita peringatan nikotin (latar hitam, tepi kuning, tulisan putih)."""
    mb = W.MB(name)
    mb.box(-w / 2, 0, 0, w / 2, .15 * s, 1.1 * s, "fm_black")
    mb.box(-w / 2, -.02, 0, w / 2, 0, .09 * s, "n_gold")
    mb.box(-w / 2, -.02, 1.01 * s, w / 2, 0, 1.1 * s, "n_gold")
    ob = mb.build(loc)
    V.glow(ob, {"n_gold": 5.0})
    t = H.text(name + "_t", text, .46 * s, "n_white", depth=.04, loc=(loc[0], loc[1] - .05, loc[2] + .33 * s),
               emission=2.5)
    return ob, t


def pod(name, loc=(0, 0, 0), s=1.0, key_="pod_pink"):
    """perangkat pod vape generik (badan pipih membulat + mouthpiece + jendela cairan)."""
    mb = W.MB(name)
    L.rbox(mb, -.55 * s, -.28 * s, 0, .55 * s, .28 * s, 3.0 * s, key_, c=.24 * s)
    mb.box(-.32 * s, -.18 * s, 3.0 * s, .32 * s, .18 * s, 3.7 * s, "pod_dark")
    mb.box(-.25 * s, -.3 * s, 1.9 * s, .25 * s, -.27 * s, 2.7 * s, "lq_pink")
    mb.box(-.06 * s, -.3 * s, .8 * s, .06 * s, -.27 * s, 1.2 * s, "n_white")
    ob = mb.build(loc)
    V.glow(ob, {"lq_pink": 2.5, "n_white": 4.0})
    return ob


def statement_card(name, loc=(0, 0, 0), s=1.0):
    """kartu pernyataan (bukan tiruan postingan): kartu gelap + bingkai pink + kutipan besar."""
    w, h = 9.0 * s, 5.4 * s
    root = bpy.data.objects.new(name, None)
    lp._link(root)
    mb = W.MB(name + "_c")
    mb.box(-w / 2, 0, 0, w / 2, .2 * s, h, "fm_dark")
    t = .1 * s
    for (a, b, c, d) in ((-w / 2, 0, w / 2, t), (-w / 2, h - t, w / 2, h), (-w / 2, 0, -w / 2 + t, h),
                         (w / 2 - t, 0, w / 2, h)):
        mb.box(a, -.03, b, c, 0, d, "fm_pink")
    co = mb.build(parent=root)
    V.glow(co, {"fm_pink": 6.0})
    l1 = H.text(name + "_l1", "SATU INDUSTRI,", .78 * s, "n_white", depth=.06, loc=(0, -.05, h * .6), emission=2.4)
    l2 = H.text(name + "_l2", "SATU KOMITMEN", .78 * s, "fm_pink", depth=.06, loc=(0, -.05, h * .4), emission=3.0)
    q = H.text(name + "_q", "“", 2.0 * s, "fm_pink", depth=.06, loc=(-w / 2 + .9 * s, -.05, h * .62),
               emission=3.0)
    for o in (l1, l2, q):
        o.parent = root
    root.location = loc
    return {"root": root, "l1": l1, "l2": l2}


def check(name, loc, s=1.0, key_="ok_green", em=5.0):
    """tanda centang neon (menghadap -Y)."""
    mb = W.MB(name)
    pts1 = [(-1.0 * s, .1 * s), (-.6 * s, .5 * s), (0, -.1 * s), (-.35 * s, -.55 * s)]
    pts2 = [(-.35 * s, -.55 * s), (0, -.1 * s), (1.15 * s, 1.05 * s), (1.5 * s, .65 * s)]
    mb.prism_y(pts1, -.12 * s, .12 * s, key_)
    mb.prism_y(pts2, -.12 * s, .12 * s, key_)
    ob = mb.build(loc)
    V.glow(ob, {key_: em})
    return ob


def shop_closed(name, loc=(0, 0, 0)):
    """toko vape kecil dengan rolling door (pintu bisa diturunkan: kembalikan objek pintu)."""
    st = V.vape_store_day(name, loc, 12.0, 9.0, "vs_pink", "TOKO LIQUID", seed=4)
    x, y, z = loc
    mb = W.MB(name + "_door")
    for k in range(12):
        mb.box(-5.6, -.32, k * .32, 5.6, -.24, k * .32 + .28, "ic_metal")
    door = mb.build((x, y, z))
    return st, door


def foom_store(name, loc=(0, 0, 0), w=15.0, d=10.0):
    """flagship store FOOM: fasad hitam, kaca pink, logo 3D di atas, poster campaign di jendela."""
    x, y, z = loc
    mb = W.MB(name)
    mb.box(x - w / 2, y, z, x + w / 2, y + d, z + 7.4, "fm_black")
    mb.box(x - w / 2 - .3, y - .3, z + 7.4, x + w / 2 + .3, y + d + .3, z + 7.9, "fm_dark")
    mb.box(x - w / 2, y - .12, z + 5.6, x + w / 2, y, z + 5.8, "fm_pink")
    mb.box(x - w / 2, y - .12, z, x - w / 2 + .2, y, z + 5.6, "fm_pink")
    mb.box(x + w / 2 - .2, y - .12, z, x + w / 2, y, z + 5.6, "fm_pink")
    ob = mb.build()
    V.glow(ob, {"fm_pink": 6.0})
    lg = foom_logo(name + "_logo", 6.0, (x, y - .3, z + 9.6), "n_white", 3.5, .3, plate="fm_pink")
    p1 = G.img_plane(name + "_p1", "p_pink", h=4.6, loc=(x - 4.4, y - .14, z + .4), em=1.3)
    p2 = G.img_plane(name + "_p2", "p_wm", h=4.6, loc=(x + 4.4, y - .14, z + .4), em=1.3)
    pd = pod(name + "_pod", (x, y - .5, z + .3), .9)
    return {"body": ob, "logo": lg, "posters": [p1, p2], "pod": pd}


def foom_tower(name, loc=(0, 0, 0), h=30.0):
    """menara kantor FOOM: kaca ungu gelap + strip pink + logo 3D raksasa di puncak."""
    x, y, z = loc
    mb = W.MB(name)
    mb.box(x - 7, y - 5, z, x + 7, y + 5, z + h, "fm_glass")
    mb.box(x - 5.5, y - 4, z + h, x + 5.5, y + 4, z + h + 3, "fm_dark")
    for zz in range(3, int(h), 3):
        mb.box(x - 7.05, y - 5.06, z + zz, x + 7.05, y - 5.0, z + zz + .22, "fm_pink")
    ob = mb.build()
    V.glow(ob, {"fm_pink": 3.5})
    lg = foom_logo(name + "_logo", 12.0, (x, y - 5.6, z + h + 7.5), "n_white", 4.0, .5, plate="fm_pink")
    return {"body": ob, "logo": lg}


def fom_city(n, rnd_seed=7, store=True, tower=True, billboards=True, center_clear=22, traffic=True,
             wide=(-74, -42, 74, 44), shops=False, news=False, posters=None):
    """kota diorama Jakarta bernuansa pink sakura (lebar). Return dict komponen."""
    import scenes_vap as SV
    rnd = random.Random(rnd_seed)
    V.DIO = wide
    sakura_patch()
    info = SV.city(n, focus=None, center_clear=center_clear, traffic=traffic, people=False)
    x0, y0, x1, y1 = wide
    # gedung tinggi di baris belakang (kaca gelap + strip neon)
    b = W.MB("towers")
    keys = []
    xx = x0 + 2
    while xx < x1 - 8:
        w = rnd.uniform(7, 10)
        if abs(xx + w / 2) > 14 or not tower:
            hh = rnd.uniform(12, 26)
            tk = rnd.choice(("n_pink", "n_cyan", "n_purple", "fm_pink"))
            keys.append(tk)
            b.box(xx, y1 - 22, 0, xx + w, y1 - 15, hh, rnd.choice(("ct_glass", "ct_glass2", "fm_glass", "ct_glass3")))
            b.box(xx - .05, y1 - 22.1, hh - .3, xx + w + .05, y1 - 22, hh, tk)
            b.box(xx + w / 2 - .1, y1 - 22.1, 1.0, xx + w / 2 + .1, y1 - 22, hh - .3, tk)
        xx += w + rnd.uniform(1.0, 2.5)
    bo = b.build()
    V.glow(bo, {k: 4.0 for k in set(keys)})
    # pohon sakura di plaza & tepi
    tm = W.MB("sakura")
    for xx in range(int(x0) + 4, int(x1) - 2, 7):
        if abs(xx) < center_clear + 2:
            continue
        sakura_tree(tm, xx + rnd.uniform(-1, 1), 1.2 + rnd.uniform(-.4, .4), 1.0 * rnd.uniform(.9, 1.2), rnd, .24)
    for sx in (-1, 1):
        for yy in (-12, -6):
            sakura_tree(tm, sx * (center_clear - 1.5), yy, 1.1, rnd, .24)
    to = tm.build()
    V.glow(to, {"sk_pink3": .25})
    out = {"info": info, "screens": [], "tower": None, "store": None, "shops": []}
    if tower:
        out["tower"] = foom_tower("ft", (0, y1 - 18, .1))
    if billboards:
        imgs = posters or POSTERS
        spots = [(-40, y1 - 23.5, 23.0, 9, 12), (40, y1 - 23.5, 24.0, 9, 12), (-60, y1 - 23.5, 20.0, 7, 9.3),
                 (60, y1 - 23.5, 21.0, 7, 9.3)]
        for i, (x, y, z, w, h) in enumerate(spots):
            seq = [imgs[(i * 3 + j) % len(imgs)] for j in range(3)]
            sc = G.screen(f"bb{i}", seq, w, h, (x, y, z), 0, n_frames=n + 8, em=2.0,
                          frame=("fm_pink", "n_cyan", "n_purple", "fm_pink")[i])
            mb = W.MB(f"bbp{i}")
            mb.box(x - .4, y + .2, 0, x + .4, y + 1.0, z - h / 2, "bd_dark")
            mb.build()
            out["screens"].append(sc)
    if news:
        for i, (x, im) in enumerate(((-28, "art_sewa"), (28, "art_phk"))):
            G.screen(f"nw{i}", [im], 7.5, 11, (x, y1 - 23.2, 18.5), 0, n_frames=n + 8, em=1.6, frame="n_red",
                     zoom=(1.0, 1.05))
    if store:
        out["store"] = foom_store("fs", (0, 4, .24))
    if shops:
        for k, x in enumerate((-36, 36)):
            out["shops"].append(V.vape_store_day(f"vs{k}", (x, 5, .24), 12.0, 9.0, ("vs_pink", "vs_purple")[k],
                                                 "TOKO VAPE", seed=k + 5))
    return out
