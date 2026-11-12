"""Aset & dunia diorama untuk video "Bedah Bisnis AMDK" (air minum dalam kemasan).

Isi: 4 produk (air gelas, botol 600 ml, botol 1.500 ml, galon) dengan plastik bening + air, karton
bermerek, palet, karyawan pabrik berseragam (helm proyek, rompi reflektif, jas lab + masker + penutup
rambut), truk tronton bermerek (boks / bak galon), forklift, pabrik AMDK lengkap (aula gigi-gergaji,
kantor kaca, tangki stainless, dok muat, panel surya), interior lini produksi (filling, capping,
labeling, konveyor berjalan), gudang distributor, dan peta Indonesia low-poly dengan pin distributor.
Merek fiktif: "TIRTA NUSA". Bagian depan bangunan menghadap -Y (sama seperti world.py).
"""
import math
import random

import bpy

import lowpoly as lp
import world as W
import world_tahu as T          # noqa: F401  (palet rumah)
import world_hotel as H         # text(), to_world(), glassy(), minimarket, money
import world_laundry as L       # character(), pose(), walk_to(), ball/tube/rbox

lp.PAL.update({
    # merek & produk
    "br_blue": "#1C6ED8", "br_blue_dk": "#124A9C", "br_aqua": "#3FC8E4", "br_white": "#FFFFFF",
    "pet": "#CFEFFC", "water": "#7CCBF0", "galon_pet": "#8CC8EE", "cup_lid": "#F4F8FB", "cap_blue": "#1550A8",
    "carton": "#D9B27C", "carton_dk": "#BE915A", "tape": "#EAD6AE", "pallet": "#C08A52", "pallet_dk": "#9C6B3A",
    # karyawan
    "wk_navy": "#23345A", "wk_blue": "#2F5FA8", "vest": "#FF8A1F", "reflect": "#EEF4F6", "helmet_y": "#FFC21A",
    "helmet_w": "#F6F6F2", "coat_w": "#F2F5F7", "hairnet": "#8FD0EE", "mask": "#DDF1F8", "tie": "#C93D3D",
    # pabrik
    "fc_wall": "#EEF1F4", "fc_wall2": "#D3DCE5", "fc_blue": "#2A62B8", "fc_roof": "#A3B0BD", "fc_roof2": "#83919F",
    "steel": "#CDD5DC", "steel_dk": "#8E98A2", "epoxy": "#86AFA2", "epoxy2": "#729C8F", "safety_y": "#F5C518",
    "conveyor": "#373C44", "roller": "#A1AAB3", "solar": "#24406E", "solar_fr": "#C9D2DA", "dock": "#4A5260",
    "screen_g": "#58E08A", "lamp_y": "#FFD34D",
    # tronton & forklift
    "tr_cab": "#F2F5F8", "tr_chassis": "#2A2E35", "tr_box": "#F7F9FB", "rim": "#C9CED4", "fork_y": "#F2B71F",
    # gudang
    "wh_wall": "#E7E3DA", "wh_roof": "#55789F", "wh_trim": "#2F4A6B",
    # peta
    "sea": "#5DB9E2", "sea_dk": "#4AA6D4", "land": "#92CF6C", "land2": "#79B957", "sand": "#EFDCA8",
    "mount": "#5E9A48", "pin_b": "#1C6ED8", "pin_o": "#FF8A1F",
})

Z = W.Z_LAWN
CH_S = L.CH_S
BRAND = "TIRTA NUSA"


# ------------------------------------------------------------------ geometri bantu
def lathe(mb, cx, cy, z0, prof, key, n=16):
    """benda putar: prof = [(r, z), ...] dari bawah ke atas (r=0 di ujung = titik pusat)."""
    rings = []
    vs = []
    for r, z in prof:
        if r <= 1e-4:
            vs.append((cx, cy, z0 + z))
            rings.append([len(vs) - 1])
            continue
        row = []
        for j in range(n):
            a = 2 * math.pi * j / n
            vs.append((cx + r * math.cos(a), cy + r * math.sin(a), z0 + z))
            row.append(len(vs) - 1)
        rings.append(row)
    fs = []
    for a, b in zip(rings[:-1], rings[1:]):
        if len(a) == 1 and len(b) > 1:
            fs += [(a[0], b[(j + 1) % n], b[j]) for j in range(n)]
        elif len(b) == 1 and len(a) > 1:
            fs += [(a[j], a[(j + 1) % n], b[0]) for j in range(n)]
        elif len(a) > 1:
            fs += [(a[j], a[(j + 1) % n], b[(j + 1) % n], b[j]) for j in range(n)]
    if len(rings[0]) > 1:
        fs.append(tuple(reversed(rings[0])))
    if len(rings[-1]) > 1:
        fs.append(tuple(rings[-1]))
    mb.poly(vs, fs, key)


def drop_shape(mb, x, y, z, s, key, depth=.15):
    """logo tetes air (berdiri, menghadap -Y)."""
    prof = []
    for k in range(17):
        a = -math.pi / 2 + math.pi * 2 * k / 16
        prof.append((x + .5 * s * math.cos(a), z + .5 * s + .5 * s * math.sin(a)))
    prof = [p for p in prof if p[1] < z + .5 * s + .3 * s] + [(x, z + 1.55 * s)]
    # urutkan berlawanan jarum jam
    cxz = (x, z + .7 * s)
    prof.sort(key=lambda p: math.atan2(p[1] - cxz[1], p[0] - cxz[0]))
    mb.prism_y(prof, y, y + depth, key)


def glass_setup():
    """material plastik bening & air (dipanggil sekali per adegan)."""
    H.glassy("pet", .22)
    H.glassy("galon_pet", .38)
    H.glassy("water", .55)
    H.glassy("glass2", .35)


# ------------------------------------------------------------------ produk
def cup(mb, x, y, z, s=1.0, lid=True):
    """air gelas (cup 220 ml): plastik bening + air + tutup foil bermerek. tinggi ±.95*s."""
    lathe(mb, x, y, z, [(0, 0), (.27 * s, 0), (.36 * s, .86 * s), (.39 * s, .9 * s), (0, .9 * s)], "pet", n=14)
    lathe(mb, x, y, z, [(0, .03 * s), (.25 * s, .03 * s), (.33 * s, .8 * s), (0, .8 * s)], "water", n=14)
    if lid:
        mb.cyl(x, y, z + .9 * s, z + .93 * s, .395 * s, "cup_lid", n=14)
        mb.cyl(x, y, z + .93 * s, z + .945 * s, .3 * s, "br_blue", n=14)
        mb.cyl(x, y, z + .945 * s, z + .95 * s, .15 * s, "br_aqua", n=10)


def bottle(mb, x, y, z, s=1.0, big=False):
    """botol PET (600 ml / 1.500 ml bila big): badan bening + air + label biru + tutup."""
    r = .46 if big else .36
    h = 2.6 if big else 2.2
    sh = h - .85
    prof = [(0, 0), (r * .85, 0), (r, .1), (r, sh * .45), (r * .93, sh * .5), (r, sh * .55), (r, sh),
            (r * .8, sh + .25), (.17, h - .2), (.14, h - .1), (.14, h)]
    lathe(mb, x, y, z, [(a * s, b * s) for a, b in prof], "pet", n=16)
    lathe(mb, x, y, z, [(0, .04 * s), ((r - .04) * s, .06 * s), ((r - .04) * s, sh * s), ((r * .7) * s, (sh + .25) * s),
                        (0, (sh + .25) * s)], "water", n=14)
    mb.cyl(x, y, z + sh * .58 * s, z + sh * .95 * s, (r + .012) * s, "br_blue", n=16)
    mb.cyl(x, y, z + sh * .86 * s, z + sh * .95 * s, (r + .018) * s, "br_aqua", n=16)
    mb.cyl(x, y, z + sh * .66 * s, z + sh * .72 * s, (r + .018) * s, "br_white", n=16)
    mb.cyl(x, y, z + (h - .02) * s, z + (h + .18) * s, .16 * s, "cap_blue", n=12)
    mb.cyl(x, y, z + (h - .1) * s, z + (h - .05) * s, .19 * s, "cap_blue", n=12)


def galon(mb, x, y, z, s=1.0, water=True):
    """galon 19 L: badan bergelombang biru bening + air + tutup + stiker merek. tinggi ±3.25*s."""
    prof = [(0, 0), (.7, 0), (.77, .08), (.77, .6), (.72, .68), (.77, .76), (.77, 1.95), (.72, 2.03), (.77, 2.11),
            (.77, 2.4), (.56, 2.75), (.24, 2.95), (.21, 3.08)]
    lathe(mb, x, y, z, [(a * s, b * s) for a, b in prof], "galon_pet", n=18)
    if water:
        lathe(mb, x, y, z, [(0, .05 * s), (.71 * s, .06 * s), (.71 * s, 2.35 * s), (.45 * s, 2.62 * s), (0, 2.62 * s)],
              "water", n=16)
    mb.cyl(x, y, z + 3.0 * s, z + 3.25 * s, .26 * s, "cap_blue", n=12)
    # stiker merek di depan
    mb.box(x - .42 * s, y - .8 * s, z + 1.0 * s, x + .42 * s, y - .74 * s, z + 1.75 * s, "br_white")
    mb.box(x - .42 * s, y - .815 * s, z + 1.38 * s, x + .42 * s, y - .8 * s, z + 1.62 * s, "br_blue")
    drop_shape(mb, x, y - .83 * s, z + 1.1 * s, .17 * s, "br_aqua", depth=.02 * s)


def carton(mb, x, y, z, w=1.6, d=1.1, h=.9, kind="cup"):
    """karton bermerek: cokelat + lakban + pita biru di sisi depan (-Y) & samping."""
    mb.box(x - w / 2, y - d / 2, z, x + w / 2, y + d / 2, z + h, "carton")
    mb.box(x - .12, y - d / 2 - .005, z + h - .01, x + .12, y + d / 2 + .005, z + h + .012, "tape")
    mb.box(x - w / 2 - .005, y - d / 2 - .012, z + h * .3, x + w / 2 + .005, y + d / 2 + .012, z + h * .62, "br_blue")
    mb.box(x - w / 2 - .012, y - d / 2 - .005, z + h * .3, x + w / 2 + .012, y + d / 2 + .005, z + h * .62, "br_blue")
    mb.box(x - w / 2 - .006, y - d / 2 - .016, z + h * .52, x + w / 2 + .006, y + d / 2 + .016, z + h * .58, "br_aqua")
    if kind == "cup":                              # ikon gelas di depan
        mb.box(x + w * .22, y - d / 2 - .02, z + h * .66, x + w * .38, y - d / 2 - .01, z + h * .9, "br_white")


def pallet(mb, x, y, z, w=3.4, d=2.4):
    for k in range(5):
        xx = x - w / 2 + k * (w - .25) / 4
        mb.box(xx, y - d / 2, z, xx + .25, y + d / 2, z + .14, "pallet_dk")
    for k in range(6):
        yy = y - d / 2 + k * (d - .2) / 5
        mb.box(x - w / 2, yy, z + .14, x + w / 2, yy + .2, z + .26, "pallet")


def carton_stack(mb, x, y, z, nx=2, ny=2, nz=3, w=1.6, d=1.1, h=.9, kind="cup", on_pallet=True):
    if on_pallet:
        pallet(mb, x, y, z, nx * w + .1, ny * d + .1)
        z += .26
    for k in range(nz):
        for i in range(nx):
            for j in range(ny):
                carton(mb, x + (i - (nx - 1) / 2) * w, y + (j - (ny - 1) / 2) * d, z + k * h, w - .03, d - .03, h - .02,
                       kind)


def galon_rack(mb, x, y, z, nx=3, nz=2, s=.55):
    """rak besi berisi galon (dimuat di bak tronton)."""
    for k in range(nz + 1):
        mb.box(x - nx * .95 * s, y - .5, z + k * 3.5 * s, x + nx * .95 * s, y + .5, z + k * 3.5 * s + .08, "steel_dk")
    for i in range(nx):
        for k in range(nz):
            galon(mb, x + (i - (nx - 1) / 2) * 1.75 * s, y, z + .08 + k * 3.5 * s, s)


def product(name, kind, s=1.0):
    """produk tunggal sebagai MB (asal di dasar tengah)."""
    mb = W.MB(name)
    if kind == "cup":
        cup(mb, 0, 0, 0, s)
    elif kind == "b600":
        bottle(mb, 0, 0, 0, s)
    elif kind == "b1500":
        bottle(mb, 0, 0, 0, s, big=True)
    else:
        galon(mb, 0, 0, 0, s)
    return mb


def pedestal(name, r=1.4, key="br_blue"):
    mb = W.MB(name)
    mb.cyl(0, 0, 0, .35, r, "c_white", n=28)
    mb.cyl(0, 0, .35, .42, r * .94, key, n=28)
    return mb


# ------------------------------------------------------------------ karyawan & orang
WORKER_LOOKS = {
    # nama: (atasan, bawahan, helm, rompi, jas, masker)
    "operator": dict(top="wk_blue", bottom="wk_navy", shoe="shoe_dk", hat="helmet_w", vest=False, coat=False, mask=False,
                     skin="skin2"),
    "buruh": dict(top="wk_navy", bottom="wk_navy", shoe="shoe_dk", hat="helmet_y", vest=True, coat=False, mask=False,
                  skin="skin3"),
    "buruh2": dict(top="wk_blue", bottom="c_denim", shoe="shoe_dk", hat="helmet_y", vest=True, coat=False, mask=False,
                   skin="skin1"),
    "qc": dict(top="coat_w", bottom="wk_navy", shoe="shoe_w", hat="hairnet", vest=False, coat=True, mask=True,
               skin="skin1"),
    "qc2": dict(top="coat_w", bottom="c_grey", shoe="shoe_w", hat="hairnet", vest=False, coat=True, mask=True,
                skin="skin2", hijab=True),
    "supir": dict(top="br_blue", bottom="c_khaki", shoe="shoe_dk", hat="cap", vest=False, coat=False, mask=False,
                  skin="skin3"),
    "manajer": dict(top="c_white", bottom="wk_navy", shoe="shoe_dk", hat=None, vest=False, coat=False, mask=False,
                    skin="skin2", tie=True),
}


def worker(name, kind="buruh", loc=(0, 0, 0), rot=0.0, s=CH_S, hold=None):
    """karyawan pabrik: karakter laundry + helm/penutup rambut, rompi reflektif, jas lab, masker, dasi."""
    wk = WORKER_LOOKS[kind]
    hair = "hijab" if wk.get("hijab") else ("cap" if wk["hat"] == "cap" else "short")
    look = dict(skin=wk["skin"], top=wk["top"], sleeve=wk["top"], bottom=wk["bottom"], shoe=wk["shoe"], hair=hair,
                hair_col=("hij_navy" if wk.get("hijab") else ("br_blue_dk" if hair == "cap" else "hair_blk")),
                acc=("lanyard",) if kind == "manajer" else ())
    parts = L.character(name, look, loc, rot, s, None if hold == "carton" else hold)
    mb = W.MB(name + "_gear")
    if hold == "carton":                                   # memanggul karton di depan dada
        carton(mb, 0, -.5, .95, .8, .55, .5)
        for sd in ("armL", "armR"):
            parts[sd].rotation_euler = (-1.05, 0, 0)
        parts["hold"] = None
    hz = 1.66
    hat = wk["hat"]
    if hat in ("helmet_y", "helmet_w"):
        L.ball(mb, 0, .01, hz + .06, .305, hat, seg=14, rings=7, sz=.3, sy=.3, z_from=.0)
        L.ball(mb, 0, .01, hz + .05, .36, hat, seg=14, rings=3, sz=.05, sy=.36, z_from=.6)     # pinggiran
        mb.box(-.03, -.31, hz + .12, .03, .31, hz + .37, hat)                                  # rusuk
        mb.box(-.07, -.33, hz + .13, .07, -.29, hz + .22, "fc_blue")                           # logo
    elif hat == "hairnet" and not wk.get("hijab"):
        L.ball(mb, 0, .02, hz + .04, .29, "hairnet", seg=14, rings=7, sz=.3, sy=.28, z_from=-.05)
    elif hat == "hairnet":
        L.ball(mb, 0, .03, hz + .03, .32, "hairnet", seg=14, rings=7, sz=.33, sy=.3, z_from=.25)
    if wk["mask"]:
        my = -.245 if not wk.get("hijab") else -.29
        L.rbox(mb, -.13, my - .02, hz - .17, .13, my + .04, hz - .03, "mask", c=.03)
    if wk["vest"]:
        L.tube(mb, 0, 0, .9, 1.42, .225, .165, .29, .18, "vest", n=12)
        for zz in (1.02, 1.2):
            L.tube(mb, 0, 0, zz, zz + .05, .26, .18, .265, .182, "reflect", n=12)
    if wk["coat"]:
        L.tube(mb, 0, 0, .55, 1.0, .29, .2, .23, .165, "coat_w", n=12)
        mb.box(-.012, -.23, .6, .012, -.19, 1.36, "steel")
        mb.box(.08, -.205, 1.12, .17, -.18, 1.24, "fc_blue")                                    # saku + pena
    if wk.get("tie"):
        mb.prism_y([(-.04, 1.36), (.04, 1.36), (.06, 1.0), (0, .94), (-.06, 1.0)], -.19, -.165, "tie")
    if kind in ("operator", "buruh", "buruh2"):
        mb.box(.06, -.2, 1.18, .18, -.17, 1.3, "br_white")                                      # badge
    if mb.v:
        g = mb.build()
        g.parent = parts["body"]
        parts["gear"] = g
    return parts


# ------------------------------------------------------------------ kendaraan
def tronton(name, cargo="box", livery=True):
    """truk tronton 10 roda (menghadap +X), panjang ±13. cargo: 'box' | 'galon' | 'carton'."""
    root = bpy.data.objects.new(name, None)
    lp._link(root)
    mb = W.MB(name + "_m")
    # sasis
    mb.box(-6.6, -.75, .9, 6.2, .75, 1.3, "tr_chassis")
    # kabin
    L.rbox(mb, 3.9, -1.3, 1.1, 6.5, 1.3, 4.2, "tr_cab", c=.25)
    mb.box(6.0, -1.18, 2.6, 6.56, 1.18, 3.9, "glass2")                    # kaca depan
    mb.box(4.4, -1.33, 2.65, 5.7, 1.33, 3.75, "glass2")                    # kaca samping
    mb.box(6.45, -1.0, 1.4, 6.62, 1.0, 2.3, "tr_chassis")                  # gril
    for k in range(4):
        mb.box(6.6, -.9, 1.5 + k * .2, 6.64, .9, 1.58 + k * .2, "steel")
    mb.box(6.4, -1.32, .95, 6.7, 1.32, 1.4, "steel_dk")                    # bemper
    for sy in (-1, 1):
        mb.box(6.55, sy * 1.0 - .25, 1.55, 6.66, sy * 1.0 + .25, 1.85, "lamp_y")
        mb.box(5.0, sy * 1.38 - .06, 3.0, 5.3, sy * 1.38 + .06, 3.6, "tr_chassis")   # spion
        mb.box(4.0, sy * 1.31, 1.25, 4.6, sy * 1.36, 2.45, "steel_dk")             # tangga
    mb.box(3.9, -1.32, 4.2, 6.2, 1.32, 4.6, "br_blue" if livery else "tr_cab")     # spoiler atap
    if livery:
        mb.box(3.92, -1.33, 1.8, 6.48, 1.33, 2.15, "br_blue")
    # muatan
    if cargo == "box":
        mb.box(-6.6, -1.35, 1.35, 3.7, 1.35, 4.7, "tr_box")
        mb.box(-6.62, -1.37, 1.3, 3.72, 1.37, 1.45, "steel_dk")
        if livery:
            mb.prism_y([(-6.6, 1.45), (3.7, 1.45), (3.7, 2.6), (-1.0, 3.3), (-6.6, 2.2)], -1.38, 1.38, "br_blue")
            mb.prism_y([(-6.6, 2.2), (-1.0, 3.3), (3.7, 2.6), (3.7, 2.85), (-1.0, 3.55), (-6.6, 2.45)], -1.385, 1.385,
                       "br_aqua")
            for sy in (-1, 1):
                drop_shape(mb, 2.4, sy * 1.37 - (.04 if sy < 0 else 0), 3.05, .55, "br_blue", depth=.04)
    elif cargo == "galon":
        mb.box(-6.6, -1.35, 1.3, 3.7, 1.35, 1.5, "steel_dk")
        for sy in (-1, 1):
            for x in (-6.4, -2.3, 1.8, 3.5):
                mb.box(x, sy * 1.3 - .06, 1.5, x + .15, sy * 1.3 + .06, 3.6, "steel_dk")
        for i in range(5):
            for j in (-.62, .62):
                for k in range(2):
                    galon(mb, -5.6 + i * 1.95, j, 1.5 + k * 1.75, .54)
    else:
        mb.box(-6.6, -1.35, 1.3, 3.7, 1.35, 1.5, "steel_dk")
        for i in range(3):
            carton_stack(mb, -5.0 + i * 3.1, 0, 1.5, 2, 2, 3, 1.4, 1.2, .8, on_pallet=False)
    # roda: depan 1 as, belakang 3 as (ban ganda)
    for x, dbl in ((5.2, False), (-1.2, True), (-3.0, True), (-4.8, True)):
        for sy in (-1, 1):
            outer = sy * (1.42 if dbl else 1.3)
            for k in range(2 if dbl else 1):
                a, b = outer - sy * (.34 + k * .38), outer - sy * k * .38
                mb.disc_y(x, max(a, b), .62, .62, .34, "tire", n=14)
            mb.disc_y(x, outer + (.02 if sy > 0 else 0), .62, .34, .02, "rim", n=10)
        mb.box(x - .85, -1.42 if not dbl else -1.55, 1.35, x + .85, 1.42 if not dbl else 1.55, 1.42, "tr_chassis")
    ob = mb.build()
    ob.parent = root
    if cargo == "box" and livery:
        for sy, rz in ((-1, 0), (1, math.pi)):
            t = H.text(f"{name}_brand{sy}", BRAND, .78, "br_blue_dk", depth=.04,
                       loc=(-2.4, sy * 1.42, 3.65), rot=(math.pi / 2, 0, rz))
            t.parent = root
    return root


def forklift(name, load=True):
    """forklift kuning (menghadap +X) dengan palet karton di garpu."""
    root = bpy.data.objects.new(name, None)
    lp._link(root)
    mb = W.MB(name + "_m")
    L.rbox(mb, -1.4, -.75, .35, .8, .75, 1.5, "fork_y", c=.15)
    mb.box(-1.5, -.7, .4, -1.1, .7, 1.4, "tr_chassis")                     # pemberat
    mb.box(-.6, -.62, 1.5, .1, .62, 1.75, "tr_chassis")                    # jok
    for x in (-.9, .5):
        for sy in (-1, 1):
            mb.box(x, sy * .62 - .04, 1.5, x + .08, sy * .62 + .04, 3.3, "tr_chassis")
    mb.box(-.95, -.7, 3.25, .6, .7, 3.35, "tr_chassis")                    # atap
    for sy in (-1, 1):
        mb.box(.95, sy * .45 - .07, .2, 1.05, sy * .45 + .07, 3.6, "steel_dk")   # tiang angkat
        mb.box(1.05, sy * .35 - .1, .3, 2.6, sy * .35 + .1, .38, "steel_dk")     # garpu
    for x in (-.9, .5):
        for sy in (-1, 1):
            mb.disc_y(x, sy * .78 + (.15 if sy > 0 else 0), .38, .38, .3, "tire", n=12)
    if load:
        carton_stack(mb, 1.85, 0, .38, 1, 1, 2, 1.5, 1.3, .8)
    ob = mb.build()
    ob.parent = root
    drv = worker(name + "_drv", "buruh2", (-.25, 0, 1.2), -math.pi / 2, s=.95)
    L.pose(drv, "sit")
    drv["body"].parent = root
    return root


# ------------------------------------------------------------------ pabrik (eksterior)
FW, FD = 30.0, 26.0


def factory(name):
    """pabrik AMDK: aula produksi atap gigi-gergaji, kantor kaca 2 lantai + panel surya, 3 tangki stainless,
    dok muat 3 pintu, halaman aspal bergaris, gerbang & pos satpam, tiang bendera. Return (MB, top)."""
    mb = W.MB(name)
    x0, x1, y0, y1 = -FW / 2, FW / 2, -FD / 2, FD / 2
    # halaman
    mb.box(x0, y0, Z, x1, y1, Z + .05, "asphalt")
    for k in range(6):
        x = x0 + 2 + k * 1.9
        mb.box(x, y0 + 1.2, Z + .05, x + .1, y0 + 4.2, Z + .07, "road_line")
    # aula produksi
    hx0, hx1, hy0, hy1, hh = -14.0, 8.5, -3.0, 12.5, 8.0
    mb.box(hx0, hy0, Z, hx1, hy1, Z + hh, "fc_wall")
    mb.box(hx0 - .05, hy0 - .05, Z, hx1 + .05, hy1 + .05, Z + 1.3, "fc_blue")
    mb.box(hx0 - .08, hy0 - .08, Z + hh - .8, hx1 + .08, hy1 + .08, Z + hh, "fc_wall2")
    for k in range(5):                                                      # jendela pita sisi kiri
        y = hy0 + 1.0 + k * 3.0
        mb.box(hx0 - .1, y, Z + 4.6, hx0 + .02, y + 2.2, Z + 6.4, "glass2")
    # atap gigi gergaji (skylight kaca menghadap +y)
    n = 5
    step = (hy1 - hy0) / n
    for k in range(n):
        ya, yb = hy0 + k * step, hy0 + (k + 1) * step
        mb.prism_x([(ya, Z + hh), (yb, Z + hh), (yb, Z + hh + 2.4), (yb - .3, Z + hh + 2.4)], hx0, hx1, "fc_roof")
        mb.prism_x([(yb - .02, Z + hh + .2), (yb + .02, Z + hh + .2), (yb + .02, Z + hh + 2.3), (yb - .02, Z + hh + 2.3)],
                   hx0 + .3, hx1 - .3, "glass2")
    # logo tetes besar di fasad aula
    drop_shape(mb, 3.0, hy0 - .22, Z + 5.0, 1.3, "br_aqua", depth=.2)
    # kantor kaca 2 lantai di depan kiri
    ox0, ox1, oy0, oy1, oh = -14.0, -2.5, -10.0, -3.0, 7.2
    mb.box(ox0, oy0, Z, ox1, oy1, Z + oh, "fc_wall")
    for fl in range(2):
        z = Z + .4 + fl * 3.4
        mb.box(ox0 + .4, oy0 - .08, z, ox1 - .4, oy0 + .02, z + 2.6, "glass2")
        for k in range(7):
            x = ox0 + .4 + k * (ox1 - ox0 - .8) / 6
            mb.box(x - .07, oy0 - .14, z, x + .07, oy0 - .04, z + 2.6, "frame")
        mb.box(ox0, oy0 - .3, z + 2.65, ox1, oy0, z + 2.85, "fc_wall2")
    mb.box(ox0 - .1, oy0 - .1, Z + oh, ox1 + .1, oy1 + .1, Z + oh + .4, "fc_blue")
    for i in range(3):                                                     # panel surya
        for j in range(2):
            x = ox0 + .9 + i * 3.6
            y = oy0 + .9 + j * 3.0
            mb.prism_x([(y, Z + oh + .5), (y + 2.6, Z + oh + .5), (y + 2.6, Z + oh + 1.4)], x, x + 3.2, "solar_fr")
            mb.prism_x([(y + .06, Z + oh + .55), (y + 2.55, Z + oh + .55), (y + 2.55, Z + oh + 1.38)], x + .08, x + 3.12,
                       "solar")
    # kanopi lobi
    mb.box(-11.5, oy0 - 2.6, Z + 3.0, -6.0, oy0, Z + 3.25, "fc_wall2")
    for x in (-11.2, -6.3):
        mb.box(x - .12, oy0 - 2.5, Z, x + .12, oy0 - 2.26, Z + 3.0, "steel")
    # dok muat (kanan depan aula)
    for k in range(3):
        x = k * 2.6
        mb.box(x - 1.0, hy0 - .1, Z, x + 1.0, hy0 + .02, Z + 3.6, "rolldoor")
        mb.box(x - 1.15, hy0 - .9, Z + 3.7, x + 1.15, hy0, Z + 3.85, "fc_blue")
    mb.box(-1.6, hy0 - 1.6, Z, 8.5, hy0, Z + 1.3, "dock")
    # tangki stainless
    for k, (tx, ty) in enumerate(((11.4, 9.5), (11.4, 4.8), (11.4, .1))):
        mb.cyl(tx, ty, Z, Z + .5, 2.1, "steel_dk", n=20)
        mb.cyl(tx, ty, Z + .5, Z + 9.0, 1.9, "steel", n=20)
        L.ball(mb, tx, ty, Z + 9.0, 1.9, "steel", seg=20, rings=6, sz=.7, z_from=0.0)
        mb.cyl(tx, ty, Z + 6.0, Z + 6.2, 2.0, "br_blue", n=20)
        mb.cyl(tx, ty, Z + 3.0, Z + 3.2, 2.0, "br_blue", n=20)
        mb.box(tx - 1.95, ty - .3, Z + 1.0, tx - 1.85, ty + .3, Z + 9.2, "steel_dk")         # tangga
        mb.box(8.5, ty - .15, Z + 7.0, tx - 1.8, ty + .15, Z + 7.3, "steel_dk")              # pipa ke aula
    mb.box(9.0, -1.5, Z + 9.6, 13.5, 11.5, Z + 9.8, "steel_dk")                              # jembatan atas
    # pos satpam + gerbang + pagar
    mb.box(9.5, y0 + .6, Z, 12.5, y0 + 3.2, Z + 2.8, "fc_wall")
    mb.box(9.3, y0 + .4, Z + 2.8, 12.7, y0 + 3.4, Z + 3.1, "fc_blue")
    mb.box(9.6, y0 + .55, Z + 1.2, 12.4, y0 + .6, Z + 2.2, "glass2")
    mb.box(4.0, y0 + .2, Z, 9.0, y0 + .4, Z + 1.3, "safety_y")                               # palang
    for x in range(-15, 4, 2):
        mb.box(x, y0 + .2, Z, x + .1, y0 + .35, Z + 1.6, "steel_dk")
    mb.box(-15, y0 + .2, Z + 1.4, 3.8, y0 + .35, Z + 1.55, "steel_dk")
    for k in range(3):                                                     # tiang bendera
        x = -14.6 + k * .85
        mb.box(x - .06, -11.06, Z, x + .06, -10.94, Z + 7.5, "steel")
        mb.box(x + .06, -11.02, Z + 6.4, x + .74, -10.98, Z + 7.2, ("flag_red", "br_blue", "br_aqua")[k])
        if k == 0:
            mb.box(x + .06, -11.03, Z + 6.4, x + .74, -10.97, Z + 6.8, "c_white")
    return mb, Z + 10.0


def factory_sign(prefix, loc, facing, lit=1.0):
    """papan nama merek di atas kantor (huruf berpendar) + tulisan pabrik di fasad aula."""
    obs = []
    o = H.text(prefix + "_brand", BRAND, 1.25, "br_blue", depth=.25, loc=(-8.25, -10.2, Z + 7.75), emission=lit * .4)
    obs.append(H.to_world(o, loc, facing))
    o = H.text(prefix + "_sub", "PABRIK AIR MINUM DALAM KEMASAN", .42, "br_blue_dk", depth=.06,
               loc=(3.0, -3.25, Z + 4.25))
    obs.append(H.to_world(o, loc, facing))
    return obs


# ------------------------------------------------------------------ gudang distributor
def warehouse(name, w=16.0, d=12.0, h=6.5, sign=True):
    """gudang distributor: dinding krem, atap pelana biru, 2 pintu gulung, papan nama, karton di depan."""
    mb = W.MB(name)
    mb.box(-w / 2, -d / 2, Z, w / 2, d / 2, Z + h, "wh_wall")
    mb.box(-w / 2 - .05, -d / 2 - .05, Z, w / 2 + .05, d / 2 + .05, Z + 1.0, "wh_trim")
    mb.prism_x([(-d / 2 - .5, Z + h), (d / 2 + .5, Z + h), (0, Z + h + 2.4)], -w / 2 - .4, w / 2 + .4, "wh_roof")
    for x in (-w / 4, w / 4):
        mb.box(x - 2.0, -d / 2 - .1, Z, x + 2.0, -d / 2 + .02, Z + 4.2, "rolldoor")
        mb.box(x - 2.2, -d / 2 - .2, Z + 4.2, x + 2.2, -d / 2, Z + 4.4, "wh_trim")
    if sign:
        mb.box(-w / 2 + 1.0, -d / 2 - .25, Z + 4.7, w / 2 - 1.0, -d / 2 - .05, Z + 6.1, "br_blue")
    mb.box(-w / 2, -d / 2 - 5, Z, w / 2, -d / 2, Z + .05, "asphalt")
    carton_stack(mb, -w / 2 + 2.2, -d / 2 - 1.8, Z + .05, 2, 1, 2, 1.4, 1.1, .8)
    return mb, Z + h + 2.4


def warehouse_sign(prefix, loc, facing, d=12.0, body="DISTRIBUTOR"):
    o = H.text(prefix + "_ws", body, .82, "br_white", depth=.06, loc=(0, -d / 2 - .27, Z + 4.98), emission=.3)
    return H.to_world(o, loc, facing)


# ------------------------------------------------------------------ interior lini produksi
def conveyor(mb, x0, x1, y, z, w=.9):
    mb.box(x0, y - w / 2, z - .12, x1, y + w / 2, z, "conveyor")
    for sy in (-1, 1):
        mb.box(x0, y + sy * w / 2 - (.08 if sy > 0 else 0), z - .25, x1, y + sy * w / 2 + (.08 if sy < 0 else 0), z + .18,
               "steel")
    x = x0 + .4
    while x < x1:
        for sy in (-1, 1):
            mb.box(x - .06, y + sy * (w / 2 - .02) - .06, 0, x + .06, y + sy * (w / 2 - .02) + .06, z - .25, "steel_dk")
        x += 2.4


def production_line(name, cx, cy):
    """ruang produksi: lantai epoxy + garis kuning, 3 tangki (FILTER/RO/OZON), mesin filling/capping/labeling,
    konveyor, mesin packing, tumpukan karton. Return dict info (posisi penting)."""
    mb = W.MB(name)
    R = 15.0
    mb.box(cx - R, cy - 11, -1.2, cx + R, cy + 9, 0, "epoxy")
    mb.box(cx - R, cy - 11, -6, cx + R, cy + 9, -1.2, "soil")
    for yy in (-3.2, 2.1):                                       # garis jalur aman
        mb.box(cx - R + .5, cy + yy, 0, cx + R - .5, cy + yy + .14, .012, "safety_y")
    mb.box(cx - R, cy + 8.6, 0, cx + R, cy + 9, 9.0, "fc_wall")                   # dinding belakang
    mb.box(cx - R, cy + 8.55, 0, cx + R, cy + 8.6, 1.4, "fc_blue")
    for k in range(6):
        x = cx - R + 2.4 + k * 4.9
        mb.box(x, cy + 8.52, 5.6, x + 3.4, cy + 8.6, 7.6, "glass2")
    mb.box(cx - R - .4, cy - 11, 0, cx - R, cy + 9, 9.0, "fc_wall2")            # dinding kiri
    # tangki pengolahan (belakang)
    tanks = []
    for k, tx in enumerate((-9.0, -5.6, -2.2)):
        x, y = cx + tx, cy + 5.6
        mb.cyl(x, y, 0, .4, 1.55, "steel_dk", n=20)
        mb.cyl(x, y, .4, 5.4, 1.4, "steel", n=20)
        L.ball(mb, x, y, 5.4, 1.4, "steel", seg=20, rings=6, sz=.55, z_from=0.0)
        mb.cyl(x, y, 3.0, 3.25, 1.47, "br_blue", n=20)
        mb.box(x - .2, y - 1.5, 1.2, x + .2, y - 1.38, 2.0, "steel_dk")
        tanks.append((x, y - 1.45, 3.9))
    mb.box(cx - 9.0, cy + 5.6 - .12, 4.6, cx + 2.5, cy + 5.6 + .12, 4.85, "steel_dk")      # pipa atas
    mb.box(cx + 2.3, cy + 5.5, 1.8, cx + 2.55, cy + 5.75, 4.85, "steel_dk")
    mb.box(cx + 2.3, cy + .8, 1.8, cx + 2.55, cy + 5.75, 2.05, "steel_dk")
    # konveyor utama sepanjang X
    zc = 1.15
    conveyor(mb, cx - 11.0, cx + 9.5, cy, zc)
    # mesin: rinser(kiri, sumber botol), filling, capping, labeling, packing(kanan)
    m = {}
    for nm, x, w, h, col in (("RINSER", -11.6, 2.6, 2.8, "steel"), ("FILLING", -2.2, 3.4, 3.6, "steel"),
                             ("CAPPING", 2.4, 2.2, 3.0, "steel"), ("LABEL", 6.0, 2.0, 2.6, "steel"),
                             ("PACKING", 11.3, 3.6, 3.0, "fc_blue")):
        xx = cx + x
        mb.box(xx - w / 2, cy - 1.2, 0, xx + w / 2, cy + 1.2, .9, "steel_dk")
        mb.box(xx - w / 2, cy - 1.2, h - .5, xx + w / 2, cy + 1.2, h, col)
        for sx in (-1, 1):
            mb.box(xx + sx * w / 2 - (.18 if sx > 0 else 0), cy - 1.2, .9, xx + sx * w / 2 + (.18 if sx < 0 else 0),
                   cy + 1.2, h - .5, col)
        mb.box(xx - w / 2 + .18, cy - 1.22, .9, xx + w / 2 - .18, cy - 1.16, h - .5, "glass2")   # kaca depan
        mb.box(xx - w / 2 + .18, cy + 1.16, .9, xx + w / 2 - .18, cy + 1.22, h - .5, "glass2")
        mb.box(xx + w / 2 - .9, cy - 1.32, h - .45, xx + w / 2 - .2, cy - 1.22, h - .05, "phone_blk")
        mb.box(xx + w / 2 - .84, cy - 1.34, h - .4, xx + w / 2 - .26, cy - 1.32, h - .1, "screen_g")
        mb.box(xx - .12, cy - .12, h, xx + .12, cy + .12, h + .6, "lamp_y")                     # lampu status
        m[nm] = (xx, cy - 1.3, h + .3)
        if nm in ("RINSER", "PACKING"):
            mb.box(xx - w / 2, cy - 1.2, .9, xx + w / 2, cy + 1.2, h - .5, col)                # tertutup penuh
    for k in range(6):                                                       # nosel filling
        x = cx - 3.4 + k * .48
        mb.box(x - .06, cy - .06, zc + 2.15, x + .06, cy + .06, 3.1, "steel_dk")
    # tumpukan karton jadi + palet di kanan depan
    carton_stack(mb, cx + 11.0, cy - 5.6, 0, 2, 2, 3, 1.5, 1.2, .85)
    carton_stack(mb, cx + 6.8, cy - 5.6, 0, 2, 2, 2, 1.5, 1.2, .85)
    # papan dinding
    mb.box(cx - 5.4, cy + 8.5, 6.3, cx + 5.4, cy + 8.55, 7.9, "br_blue")
    ob = mb.build()
    t = H.text(name + "_wt", "AREA PRODUKSI  •  " + BRAND, .62, "br_white", depth=.04, loc=(cx, cy + 8.45, 6.75),
               emission=.3)
    labels = []
    for k, (nm, (x, y, z)) in enumerate(zip(("FILTER", "RO", "OZON"), tanks)):
        labels.append(H.text(f"{name}_tk{k}", nm, .42, "br_blue_dk", depth=.03, loc=(x, y - .08, z)))
    return {"ob": ob, "machines": m, "tanks": tanks, "zc": zc, "x0": cx - 10.3, "x1": cx + 9.5, "y": cy}


def bottles_on_line(prefix, x_in, x_out, y, z, n_frames, speed=1.4, gap=1.0, fps=30, s=.42):
    """botol berjalan di konveyor: muncul di x_in (keluar mesin kiri), hilang di x_out (masuk mesin kanan)."""
    obs = []
    dur = n_frames / fps
    count = int((x_out - x_in + speed * dur) / gap) + 2
    for k in range(count):
        xs = x_out - k * gap
        mb = W.MB(f"{prefix}{k}")
        bottle(mb, 0, 0, 0, s)
        ob = mb.build((xs, y, z))
        ob.keyframe_insert("location", frame=1)
        ob.location.x = xs + speed * dur
        ob.keyframe_insert("location", frame=n_frames)
        f_in = 1 + (x_in - xs) / speed * fps
        f_out = 1 + (x_out - xs) / speed * fps
        ob.scale = (1, 1, 1) if x_in <= xs <= x_out else (.001,) * 3
        ob.keyframe_insert("scale", frame=1)
        for f, vis in ((f_in, True), (f_out, False)):
            if 1 < f <= n_frames:
                ob.scale = (1, 1, 1) if vis else (.001,) * 3
                ob.keyframe_insert("scale", frame=int(f))
        for fc in L._fc(ob):
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR" if fc.data_path == "location" else "CONSTANT"
        obs.append(ob)
    return obs


def studio_epoxy(cx, cy, size=14, wall=False):
    """lantai studio industri (epoxy biru-abu + garis kuning)."""
    mb = W.MB(f"stud{cx}_{cy}")
    mb.box(cx - size, cy - size, -6, cx + size, cy + size, -.7, "soil")
    mb.box(cx - size, cy - size, -.7, cx + size, cy + size, 0, "epoxy")
    mb.box(cx - size + .6, cy - size + .6, 0, cx + size - .6, cy - size + .8, .012, "safety_y")
    if wall:
        mb.box(cx - size, cy + 5, 0, cx + size, cy + 5.4, 8, "fc_wall")
    mb.build()


# ------------------------------------------------------------------ peta Indonesia
_ISL = {
    "sumatra": [(95.3, 5.6), (97.6, 5.2), (98.8, 3.6), (100.4, 2.2), (101.6, 1.6), (103.6, .3), (104.4, -1.4),
                (106.0, -3.0), (105.9, -5.8), (104.6, -5.9), (103.0, -4.6), (101.4, -2.9), (100.4, -1.0),
                (99.2, .5), (98.4, 1.8), (96.9, 3.3), (95.4, 4.6)],
    "jawa": [(105.2, -6.8), (106.5, -6.0), (108.3, -6.3), (110.4, -6.9), (111.6, -6.6), (112.7, -6.9),
             (114.4, -7.7), (114.4, -8.6), (112.0, -8.3), (110.0, -8.1), (108.0, -7.8), (106.4, -7.4)],
    "kalimantan": [(109.0, 1.8), (109.5, -.5), (110.2, -2.9), (111.8, -3.5), (114.5, -4.0), (116.3, -3.2),
                   (116.6, -1.2), (117.5, .6), (118.9, 1.1), (117.8, 4.2), (117.0, 6.5), (116.0, 6.9),
                   (115.2, 5.0), (113.0, 3.2), (111.0, 1.8)],
    "sulawesi": [(118.9, -2.7), (119.4, .1), (120.6, .8), (123.0, .9), (125.1, 1.6), (124.6, .4), (121.6, .4),
                 (120.8, -.9), (121.6, -1.8), (123.4, -.9), (122.9, -2.7), (122.0, -4.5), (122.8, -5.5),
                 (121.1, -4.7), (120.5, -2.9), (120.4, -5.6), (119.4, -5.6), (119.1, -3.6)],
    "papua": [(131.0, -1.2), (132.5, -.4), (134.0, -.9), (135.0, -3.2), (137.8, -1.6), (141.0, -2.6),
              (141.0, -9.1), (139.0, -8.1), (138.0, -8.4), (137.6, -5.3), (135.0, -4.4), (133.6, -3.9),
              (132.0, -2.9), (133.0, -2.3), (131.9, -1.7)],
    "bali": [(114.5, -8.1), (115.7, -8.3), (115.6, -8.8), (114.6, -8.6)],
    "lombok": [(116.0, -8.3), (116.7, -8.3), (116.6, -8.9), (116.0, -8.8)],
    "sumbawa": [(116.9, -8.4), (119.0, -8.1), (119.1, -8.7), (117.0, -9.0)],
    "flores": [(119.8, -8.4), (122.9, -8.1), (122.9, -8.6), (119.9, -8.9)],
    "timor": [(123.5, -10.2), (125.2, -9.0), (127.2, -8.4), (125.0, -9.6), (124.0, -10.4)],
    "sumba": [(119.0, -9.6), (120.8, -9.9), (120.6, -10.3), (119.1, -9.9)],
    "halmahera": [(127.5, 2.2), (128.2, 1.9), (128.0, .6), (128.9, .3), (127.9, -.4), (127.4, .8)],
    "seram": [(128.0, -2.9), (130.0, -2.9), (130.8, -3.4), (128.3, -3.5)],
    "buru": [(126.0, -3.1), (127.2, -3.2), (127.0, -3.8), (126.1, -3.7)],
    "bangka": [(105.2, -1.6), (106.3, -1.9), (106.7, -3.0), (105.6, -2.5)],
}
MAP_K = 1.6
MAP_O = (118.0, -2.0)
CITIES = {"Jakarta": (106.8, -6.2), "Surabaya": (112.75, -7.25), "Bandung": (107.6, -6.9), "Semarang": (110.4, -7.0),
          "Medan": (98.7, 3.6), "Palembang": (104.75, -2.98), "Pekanbaru": (101.45, .5), "Padang": (100.35, -.95),
          "Pontianak": (109.3, -.03), "Banjarmasin": (114.6, -3.3), "Balikpapan": (116.85, -1.25),
          "Makassar": (119.43, -5.15), "Manado": (124.85, 1.47), "Denpasar": (115.2, -8.65), "Kupang": (123.6, -10.15),
          "Ambon": (128.2, -3.65), "Jayapura": (140.7, -2.55), "Sorong": (131.25, -.88), "Mataram": (116.1, -8.58),
          "Lampung": (105.25, -5.4)}


def map_xy(lon, lat):
    return ((lon - MAP_O[0]) * MAP_K, (lat - MAP_O[1]) * MAP_K)


def _inside(pt, poly):
    x, y = pt
    c = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-9) + x1:
            c = not c
    return c


def _grow(poly, d):
    """besarkan poligon sedikit dari titik beratnya (untuk tepi pasir)."""
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    out = []
    for x, y in poly:
        v = math.hypot(x - cx, y - cy) + 1e-6
        out.append((x + (x - cx) / v * d, y + (y - cy) / v * d))
    return out


def _tri_fan(mb, poly, z0, z1, key):
    """ekstrusi poligon (boleh cekung) — pakai triangulasi ear-clipping sederhana."""
    pts = list(poly)
    area = sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]))
    if area < 0:
        pts.reverse()
    n = len(pts)
    vs = [(x, y, z0) for x, y in pts] + [(x, y, z1) for x, y in pts]
    idx = list(range(n))
    tris = []
    guard = 0
    while len(idx) > 3 and guard < 2000:
        guard += 1
        for i in range(len(idx)):
            a, b, c = idx[i - 1], idx[i], idx[(i + 1) % len(idx)]
            (ax, ay), (bx, by), (cx, cy) = pts[a], pts[b], pts[c]
            if (bx - ax) * (cy - ay) - (by - ay) * (cx - ax) <= 0:
                continue
            if any(_inside(pts[p], [pts[a], pts[b], pts[c]]) for p in idx if p not in (a, b, c)):
                continue
            tris.append((a, b, c))
            idx.pop(i)
            break
    if len(idx) == 3:
        tris.append(tuple(idx))
    fs = [(n + a, n + b, n + c) for a, b, c in tris] + [(c, b, a) for a, b, c in tris]
    fs += [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    mb.poly(vs, fs, key)


def indonesia_map(name, cx=0.0, cy=0.0, sea_pad=8.0):
    """peta Indonesia low-poly: laut, pulau berlapis pasir, beberapa gunung. Return (objek, poligon dunia)."""
    mb = W.MB(name)
    polys = {}
    for nm, pts in _ISL.items():
        polys[nm] = [(cx + map_xy(*p)[0], cy + map_xy(*p)[1]) for p in pts]
    xs = [x for p in polys.values() for x, _ in p]
    ys = [y for p in polys.values() for _, y in p]
    mb.box(min(xs) - sea_pad, min(ys) - sea_pad, -3.0, max(xs) + sea_pad, max(ys) + sea_pad, -.4, "sea_dk")
    mb.box(min(xs) - sea_pad, min(ys) - sea_pad, -.4, max(xs) + sea_pad, max(ys) + sea_pad, 0, "sea")
    for nm, p in polys.items():
        _tri_fan(mb, _grow(p, .35), 0, .35, "sand")
        _tri_fan(mb, p, .35, 1.0, "land")
    rnd = random.Random(7)
    for nm in ("sumatra", "jawa", "kalimantan", "sulawesi", "papua"):
        p = polys[nm]
        for _ in range({"jawa": 5, "sumatra": 6}.get(nm, 4)):
            for _t in range(40):
                x = rnd.uniform(min(a for a, _ in p), max(a for a, _ in p))
                y = rnd.uniform(min(b for _, b in p), max(b for _, b in p))
                if _inside((x, y), p) and _inside((x + .8, y), p) and _inside((x - .8, y), p):
                    mb.cyl(x, y, 1.0, 1.0 + rnd.uniform(1.0, 1.8), rnd.uniform(.7, 1.1), "mount", n=7, r_top=0)
                    break
    ob = mb.build()
    return ob, polys


def map_points(polys, n, seed=3):
    """titik acak di daratan (Jawa lebih padat) untuk pin distributor."""
    rnd = random.Random(seed)
    w = {"jawa": 9, "sumatra": 5, "kalimantan": 3, "sulawesi": 3, "bali": 1, "papua": 1.5, "lombok": .6,
         "sumbawa": .5, "flores": .5, "timor": .4, "halmahera": .3, "seram": .3, "bangka": .3, "sumba": .2, "buru": .2}
    names = list(w)
    tot = sum(w.values())
    out = []
    while len(out) < n:
        r = rnd.uniform(0, tot)
        for nm in names:
            r -= w[nm]
            if r <= 0:
                break
        p = polys[nm]
        x = rnd.uniform(min(a for a, _ in p), max(a for a, _ in p))
        y = rnd.uniform(min(b for _, b in p), max(b for _, b in p))
        if _inside((x, y), p):
            out.append((x, y))
    return out


def pin(name, loc, s=1.0, key="pin_b"):
    mb = W.MB(name)
    mb.cyl(0, 0, 0, 1.0 * s, .02 * s, key, n=8, r_top=.22 * s)
    L.ball(mb, 0, 0, 1.15 * s, .32 * s, key, seg=10, rings=6)
    L.ball(mb, 0, -.02 * s, 1.17 * s, .14 * s, "br_white", seg=8, rings=5, sy=.33 * s)
    return mb.build(loc)


# ------------------------------------------------------------------ dunia
FACTORY_C = (0.0, -1.0)            # menghadap -y
DIST_C = (0.0, -47.0)              # gudang distributor, menghadap +y
DIST2_C = (47.0, -6.0)             # menghadap -x
MM_C = (-46.0, -8.0)               # minimarket, menghadap +x
DIST3_C = (46.0, 46.0)             # menghadap -y
DOCK_TRUCKS = [(0.0, "box"), (5.2, "galon")]


def build_world(seed=5, people=True, workers=True, parked=True):
    """kota diorama: pabrik AMDK di blok tengah, gudang distributor, minimarket, rumah & ruko."""
    rnd = random.Random(seed)
    info = {"anchors": {}, "people": [], "walkers": [], "trucks": [], "workers": []}
    W.PLACED.clear()
    W.build_ground()
    props = W.MB("props")
    trees = W.MB("trees")
    A = info["anchors"]
    fx, fy = FACTORY_C
    mb, top = factory("factory")
    info["factory"] = mb.build((fx, fy, 0), 0)
    info["fsign"] = factory_sign("fs", (fx, fy, 0), "-y")
    A["PABRIK"] = (fx - 8.25, fy - 10.2, Z + 10.0)
    A["TANGKI"] = (fx + 11.4, fy + 4.8, Z + 10.5)
    A["DOK"] = (fx + 2.6, fy - 4.0, Z + 5.0)
    reserved = [(-15.5, -15.5, 15.5, 15.5)]
    if parked:
        for k, (x, cargo) in enumerate(DOCK_TRUCKS):
            t = tronton(f"dock{k}", cargo)
            t.location = (fx + x, fy - 4.6 - 6.7, Z + .05)
            t.rotation_euler.z = -math.pi / 2
            info["trucks"].append(t)
        fl = forklift("fork0")
        fl.location = (fx - 6.0, fy - 6.0, Z + .05)
        fl.rotation_euler.z = 0.0
        info["forklift"] = fl
    for (nm, c, fc, label) in (("dist", DIST_C, "+y", "GUDANG"), ("dist2", DIST2_C, "-x", "GUDANG2"),
                               ("dist3", DIST3_C, "-y", "GUDANG3")):
        ob, top = W.place(warehouse(nm), c[0], c[1], fc)
        info[nm] = ob
        info[nm + "_sign"] = warehouse_sign(nm, (*c, 0), fc)
        A[label] = (c[0], c[1], top + 1)
        reserved.append((c[0] - 10, c[1] - 10, c[0] + 10, c[1] + 10))
    ob, top = W.place(H.minimarket("mm"), MM_C[0], MM_C[1], "+x")
    info["mm"] = ob
    info["mm_sign"] = H.minimarket_sign("mm", (*MM_C, 0), "+x")
    A["MINIMARKET"] = (MM_C[0], MM_C[1], top + 1)
    reserved.append((MM_C[0] - 9, MM_C[1] - 9, MM_C[0] + 9, MM_C[1] + 9))

    # taman barat-daya
    pb = W.inner((-W.L, -W.L, W.ROADS[0] - W.RW / 2, W.ROADS[0] - W.RW / 2))
    reserved.append(pb)
    for q in range(24):
        x = rnd.uniform(pb[0] + 3, pb[2] - 3)
        y = rnd.uniform(pb[1] + 3, pb[3] - 3)
        if rnd.random() < .45:
            W.tree_conifer(trees, x, y, rnd.uniform(.8, 1.15))
        else:
            W.tree_round(trees, x, y, rnd.uniform(.8, 1.2), rnd)
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
                if k < .12:
                    W.tree_round(trees, cx - 2, cy, 1.1, rnd)
                    W.tree_conifer(trees, cx + 2.5, cy + 1.5, 1.0)
                    continue
                if k < .45:
                    W.place(T.house("hs" + nm, w, d, rnd), cx, cy, facing)
                elif k < .7:
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

    if workers:
        kinds = ["buruh", "operator", "qc", "buruh2", "qc2", "manajer"]
        spots = [(-9.5, -12.2, 0), (-7.6, -12.0, .4), (-12.8, -12.4, -.3), (8.0, -8.5, 2.6), (6.5, -9.0, -2.4),
                 (-10.5, -13.0, .1)]
        for k, (kind, (x, y, r)) in enumerate(zip(kinds, spots)):
            p = worker(f"wk{k}", kind, (fx + x, fy + y, Z), r, hold="tablet" if kind in ("qc", "manajer") else None)
            info["workers"].append(p)
    if people:
        prnd = random.Random(seed + 1)
        for k in range(12):
            r = prnd.choice(W.ROADS)
            off = prnd.choice((-W.RW / 2 - 1.7, W.RW / 2 + 1.7))
            horiz = prnd.random() < .5
            t0 = prnd.uniform(-60, 60)
            if any(abs(t0 - q) < 8 for q in W.ROADS):
                t0 += 25
            sp = prnd.choice((-1, 1)) * prnd.uniform(1.0, 1.4)
            if horiz:
                loc, rot = (t0, r + off, .25), (-math.pi / 2 if sp > 0 else math.pi / 2)
            else:
                loc, rot = (r + off, t0, .25), (0 if sp > 0 else math.pi)
            parts = L.character(f"ped{k}", L.WALKERS[k % len(L.WALKERS)], loc, rot)
            info["people"].append((parts["body"], horiz, sp))
            info["walkers"].append(parts)
    return info


def road_trucks(n_frames, seed=4, n=4, fps=30, speed=9.0, cargo=("box", "galon", "box", "carton")):
    """tronton yang melaju di jalan kota (lajur kiri)."""
    rnd = random.Random(seed)
    out = []
    for k in range(n):
        r = W.ROADS[k % 2]
        horiz = k % 2 == 0
        dirn = 1 if k < 2 else -1
        lane = -2.5 * dirn if horiz else 2.5 * dirn
        t0 = rnd.uniform(-55, 30) if dirn > 0 else rnd.uniform(-30, 55)
        tr = tronton(f"rt{k}", cargo[k % len(cargo)])
        d = speed * dirn * n_frames / fps
        if horiz:
            tr.rotation_euler.z = 0 if dirn > 0 else math.pi
            p0, p1 = (t0, r + lane, .05), (t0 + d, r + lane, .05)
        else:
            tr.rotation_euler.z = math.pi / 2 if dirn > 0 else -math.pi / 2
            p0, p1 = (r - lane, t0, .05), (r - lane, t0 + d, .05)
        tr.location = p0
        tr.keyframe_insert("location", frame=1)
        tr.location = p1
        tr.keyframe_insert("location", frame=n_frames)
        out.append(tr)
    return out


def animate_walkers(info, n):
    W.animate_people(info, n)
    for parts in info["walkers"]:
        L.walk_cycle(parts, 1, n, period=20, amp=.5)
