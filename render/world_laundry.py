"""Aset & dunia diorama untuk video "Laundry Koin".

Isi: karakter generasi baru (kepala bulat bermata, rambut beragam, lengan/kaki terpisah sehingga bisa
berjalan & berpose), mesin cuci front-loader dengan drum berputar, mesin pengering bertumpuk, kios bayar
QR/koin, gedung laundry koin modern (muka kaca, papan nama menyala), set interior lengkap, laundry
konvensional, kos-kosan dengan jemuran, apartemen, kampus, kantor, dan props satire (uang, gedung
pengadilan, laporan keuangan). Bagian depan bangunan menghadap -Y (sama seperti world.py).
"""
import math
import random

import bpy
from mathutils import Vector

import lowpoly as lp
import world as W
import world_tahu as T          # noqa: F401  (palet orang/motor)
import world_hotel as H         # text(), to_world(), glassy(), emit(), plant(), uang, kantor

lp.PAL.update({
    # karakter
    "skin1": "#F1C6A0", "skin2": "#D9A47A", "skin3": "#B07A52",
    "eye": "#1E1E24", "blush": "#F09A8A", "mouth": "#9C4A42",
    "hair_blk": "#24201E", "hair_brn": "#5A3A28", "hair_dk": "#3A2A22",
    "hij_rose": "#D98CA8", "hij_sage": "#8FB89A", "hij_navy": "#3D4E78", "hij_cream": "#E8D8BE",
    "c_coral": "#F07A5E", "c_mint": "#5CC7A8", "c_sky": "#5BA8E6", "c_mustard": "#E9B530",
    "c_lilac": "#A58BE0", "c_white": "#F7F7F4", "c_navy": "#2F3E66", "c_olive": "#7D8B4A",
    "c_pink": "#F2A0B8", "c_grey": "#9AA3AD", "c_black": "#2B2D33", "c_denim": "#4A6FA5",
    "c_khaki": "#C9B48A", "c_brick": "#C2553F",
    "shoe_w": "#F4F4F2", "shoe_sole": "#E2E2DE", "shoe_dk": "#33353B",
    "basket": "#5BB8D6", "basket2": "#F2A24A",
    # laundry
    "lw_wall": "#F6F3EC", "lw_teal": "#2BB3A3", "lw_teal_dk": "#1F8C80", "lw_navy": "#22344F",
    "lw_floor": "#E9E6DF", "lw_floor2": "#D8D4CB", "lw_wood": "#C9965F", "lw_wood2": "#A9763F",
    "lw_frame": "#2A2E35", "lw_glass": "#9FD3E6", "lw_sign": "#FFFFFF", "lw_yellow": "#FFCF3F",
    "wm_body": "#F4F6F8", "wm_panel": "#D7DEE5", "wm_ring": "#8C98A4", "wm_glass": "#7FC3E0",
    "wm_drum": "#3C4652", "wm_lcd": "#5BE08A", "dr_body": "#E7ECF1",
    "kiosk": "#22344F", "kiosk_scr": "#EAF7FF", "qr": "#1C1F26",
    "foam": "#FFFFFF", "cushion": "#F28C6B", "cushion2": "#4FB3D9",
    "det1": "#3D8FD1", "det2": "#F06C5A", "det3": "#5CC77A", "det4": "#F6C431",
    "cloth1": "#F07A5E", "cloth2": "#5BA8E6", "cloth3": "#F6C431", "cloth4": "#5CC7A8", "cloth5": "#A58BE0",
    "neon": "#7FF0E0",
    # kota & bangunan lain
    "kos_wall": "#F4E3C7", "kos_wall2": "#E9C99A", "kos_trim": "#B9673F", "kos_door": "#7A4E35",
    "apt_wall": "#E8EEF2", "apt_acc": "#6F8FAE", "apt_glass": "#6B8CA8",
    "kampus": "#EDE3D2", "kampus_roof": "#2F5E8C", "kampus_acc": "#C74B3B",
    "court": "#EEE9DF", "court_roof": "#8E8A82", "court_dk": "#6A665F",
    "money_g": "#5DBB7A", "money_g2": "#3E9A5C", "paper_w": "#FFFFFF", "paper_l": "#DDE4EA",
    "check": "#2EAD5B", "xred": "#E2453C", "news_red": "#D93A35", "phone_blk": "#1F2228",
    "balloon1": "#F25C54", "balloon2": "#FFC93C", "balloon3": "#3D8FD1", "ribbon": "#E2453C",
    "spark": "#FFF4B0",
})

Z = W.Z_LAWN
CH_S = 1.25                       # skala karakter di dunia (tinggi ±2.2 unit)


# ------------------------------------------------------------------ geometri bantu
def ball(mb, cx, cy, cz, r, key, seg=12, rings=8, sz=None, sy=None, z_from=-1.0):
    """bola UV halus (rx=r, ry=sy, rz=sz). z_from>-1 -> hanya tudung atas sampai cos(theta)=z_from."""
    sz = sz or r
    sy = sy or r
    cap = z_from > -1
    lo = math.acos(max(-1.0, min(1.0, z_from))) if cap else math.pi
    vs = [(cx, cy, cz + sz)]
    rows = []
    last = rings if cap else rings - 1
    for i in range(1, last + 1):
        th = lo * i / rings
        row = []
        for j in range(seg):
            ph = 2 * math.pi * j / seg
            vs.append((cx + r * math.sin(th) * math.cos(ph), cy + sy * math.sin(th) * math.sin(ph),
                       cz + sz * math.cos(th)))
            row.append(len(vs) - 1)
        rows.append(row)
    fs = [(0, rows[0][(j + 1) % seg], rows[0][j]) for j in range(seg)]
    for a, b in zip(rows[:-1], rows[1:]):
        for j in range(seg):
            fs.append((a[j], a[(j + 1) % seg], b[(j + 1) % seg], b[j]))
    if cap:
        fs.append(tuple(rows[-1]))
    else:
        vs.append((cx, cy, cz - sz))
        bot = len(vs) - 1
        fs += [(rows[-1][j], rows[-1][(j + 1) % seg], bot) for j in range(seg)]
    mb.poly(vs, fs, key)


def tube(mb, cx, cy, z0, z1, rx0, ry0, rx1, ry1, key, n=10):
    """silinder elips meruncing (torso, rok)."""
    vs = [(cx + rx0 * math.cos(2 * math.pi * i / n), cy + ry0 * math.sin(2 * math.pi * i / n), z0) for i in range(n)]
    vs += [(cx + rx1 * math.cos(2 * math.pi * i / n), cy + ry1 * math.sin(2 * math.pi * i / n), z1) for i in range(n)]
    fs = [list(range(n - 1, -1, -1)), list(range(n, 2 * n))]
    fs += [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    mb.poly(vs, fs, key)


def limb(mb, p0, p1, r0, r1, key, n=8):
    """silinder dari p0 ke p1 (lengan/kaki), ujung membulat ditangani bola terpisah."""
    a, b = Vector(p0), Vector(p1)
    d = (b - a).normalized()
    up = Vector((0, 0, 1)) if abs(d.z) < .9 else Vector((1, 0, 0))
    u = d.cross(up).normalized()
    v = d.cross(u).normalized()
    vs = []
    for p, r in ((a, r0), (b, r1)):
        for i in range(n):
            t = 2 * math.pi * i / n
            vs.append(tuple(p + (u * math.cos(t) + v * math.sin(t)) * r))
    fs = [list(range(n - 1, -1, -1)), list(range(n, 2 * n))]
    fs += [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    mb.poly(vs, fs, key)


def rbox(mb, x0, y0, z0, x1, y1, z1, key, c=.06):
    """kotak dengan tepi tegak dipotong (chamfer) supaya tidak terlalu kaku."""
    c = min(c, (x1 - x0) / 3, (y1 - y0) / 3)
    prof = [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)]
    n = len(prof)
    vs = [(x, y, z0) for x, y in prof] + [(x, y, z1) for x, y in prof]
    fs = [list(range(n - 1, -1, -1)), list(range(n, 2 * n))]
    fs += [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    mb.poly(vs, fs, key)


# ------------------------------------------------------------------ karakter
LOOKS = {
    # nama: kulit, atasan, lengan, bawahan, sepatu, rambut, warna rambut, aksesori
    "mahasiswa": dict(skin="skin1", top="c_mint", sleeve="c_mint", bottom="c_denim", shoe="shoe_w", hair="short",
                      hair_col="hair_blk", acc=("backpack", "glasses")),
    "pekerja": dict(skin="skin2", top="c_white", sleeve="c_white", bottom="c_navy", shoe="shoe_dk", hair="short",
                    hair_col="hair_dk", acc=("lanyard",)),
    "hijab": dict(skin="skin1", top="c_coral", sleeve="c_coral", bottom="c_khaki", shoe="shoe_w", hair="hijab",
                  hair_col="hij_cream", acc=("tote",)),
    "hijab2": dict(skin="skin2", top="c_lilac", sleeve="c_lilac", bottom="c_navy", shoe="shoe_w", hair="hijab",
                   hair_col="hij_navy", acc=()),
    "cewek": dict(skin="skin1", top="c_mustard", sleeve="c_mustard", bottom="c_black", shoe="shoe_w", hair="long",
                  hair_col="hair_brn", acc=()),
    "cowok": dict(skin="skin3", top="c_sky", sleeve="c_sky", bottom="c_khaki", shoe="shoe_w", hair="cap",
                  hair_col="c_coral", acc=()),
    "owner": dict(skin="skin2", top="lw_teal", sleeve="lw_teal", bottom="c_navy", shoe="shoe_dk", hair="short",
                  hair_col="hair_blk", acc=("apron",)),
    "teknisi": dict(skin="skin3", top="c_navy", sleeve="c_navy", bottom="c_navy", shoe="shoe_dk", hair="cap",
                    hair_col="lw_yellow", acc=("belt",)),
    "staf": dict(skin="skin1", top="c_pink", sleeve="c_pink", bottom="c_black", shoe="shoe_dk", hair="bun",
                 hair_col="hair_blk", acc=("apron",)),
    "bapak": dict(skin="skin2", top="c_olive", sleeve="c_olive", bottom="c_grey", shoe="shoe_dk", hair="short",
                  hair_col="hair_blk", acc=()),
}
WALKERS = ["mahasiswa", "pekerja", "hijab", "cewek", "cowok", "hijab2", "bapak"]


def _head(mb, lk, look_down=False):
    skin, hc = lk["skin"], lk["hair_col"]
    hz = 1.66
    mb.cyl(0, 0, 1.43, 1.52, .075, skin, n=8)                       # leher
    ball(mb, 0, 0, hz, .25, skin, sz=.27, sy=.24)                   # kepala
    # telinga
    for sx in (-1, 1):
        ball(mb, sx * .245, .02, hz, .045, skin, seg=6, rings=4)
    # wajah: mata, pipi, senyum (menghadap -Y)
    ey = -.222
    for sx in (-1, 1):
        ball(mb, sx * .085, ey, hz + .01, .034, "eye", seg=8, rings=5, sy=.02, sz=.042)
        ball(mb, sx * .145, ey + .02, hz - .07, .03, "blush", seg=6, rings=3, sy=.012)
    mb.box(-.04, ey - .006, hz - .1, .04, ey + .01, hz - .085, "mouth")
    h = lk["hair"]
    if h == "short":
        ball(mb, 0, .02, hz + .03, .265, hc, sz=.28, sy=.26, z_from=.05)
        mb.box(-.2, -.24, hz + .1, .18, -.14, hz + .2, hc)              # poni
        mb.box(-.26, -.05, hz - .08, -.23, .2, hz + .12, hc)            # cambang
        mb.box(.23, -.05, hz - .08, .26, .2, hz + .12, hc)
    elif h == "long":
        ball(mb, 0, .02, hz + .03, .275, hc, sz=.29, sy=.27, z_from=.0)
        mb.box(-.22, -.245, hz + .08, .22, -.15, hz + .2, hc)
        rbox(mb, -.27, -.02, hz - .5, .27, .27, hz + .05, hc, c=.08)   # rambut panjang ke punggung
    elif h == "bun":
        ball(mb, 0, .02, hz + .03, .265, hc, sz=.28, sy=.26, z_from=.05)
        ball(mb, 0, .14, hz + .3, .12, hc, seg=10, rings=6)
        mb.box(-.2, -.24, hz + .11, .2, -.15, hz + .2, hc)
    elif h == "hijab":
        ball(mb, 0, .03, hz + .02, .3, hc, sz=.31, sy=.29)              # kerudung menutup kepala
        tube(mb, 0, .03, 1.18, 1.56, .4, .3, .24, .24, hc, n=12)        # jatuh ke bahu
        # bukaan wajah: lapisan kulit di depan kerudung
        ball(mb, 0, -.215, hz - .02, .17, skin, seg=12, rings=6, sy=.07, sz=.2)
        for sx in (-1, 1):
            ball(mb, sx * .07, -.282, hz + .0, .03, "eye", seg=8, rings=5, sy=.015, sz=.038)
            ball(mb, sx * .12, -.27, hz - .07, .028, "blush", seg=6, rings=3, sy=.01)
        mb.box(-.035, -.287, hz - .1, .035, -.275, hz - .087, "mouth")
    elif h == "cap":
        ball(mb, 0, .02, hz + .03, .265, "hair_blk", sz=.28, sy=.26, z_from=.1)
        ball(mb, 0, .02, hz + .06, .27, hc, sz=.26, sy=.265, z_from=.3)
        mb.box(-.2, -.48, hz + .1, .2, -.16, hz + .14, hc)              # lidah topi
    if "glasses" in lk["acc"]:
        for sx in (-1, 1):
            mb.box(sx * .085 - .06, ey - .03, hz - .03, sx * .085 + .06, ey - .015, hz + .06, "lw_frame")
            mb.box(sx * .085 - .045, ey - .033, hz - .015, sx * .085 + .045, ey - .028, hz + .045, "lw_glass")


def _body(mb, lk):
    top, bottom = lk["top"], lk["bottom"]
    tube(mb, 0, 0, .86, 1.47, .2, .14, .27, .16, top, n=12)          # badan
    ball(mb, 0, 0, 1.44, .27, top, sz=.08, sy=.16, seg=12, rings=4)   # bahu membulat
    tube(mb, 0, 0, .78, .92, .22, .15, .2, .14, bottom, n=12)          # pinggul
    acc = lk["acc"]
    if "apron" in acc:
        mb.box(-.19, -.17, .62, .19, -.13, 1.36, "lw_navy" if lk["top"] != "lw_navy" else "c_white")
        mb.box(-.1, -.18, 1.0, .1, -.16, 1.12, "lw_yellow")
    if "backpack" in acc:
        rbox(mb, -.2, .13, .9, .2, .36, 1.4, "c_coral", c=.07)
        mb.box(-.14, .35, .95, .14, .4, 1.15, "c_coral")
    if "tote" in acc:
        mb.box(.28, -.1, .72, .48, .14, 1.08, "hij_cream")
    if "lanyard" in acc:
        mb.box(-.05, -.175, 1.05, .05, -.16, 1.18, "lw_teal")
    if "belt" in acc:
        tube(mb, 0, 0, .88, .95, .215, .155, .215, .155, "lw_yellow", n=12)
    # kerah
    mb.box(-.09, -.165, 1.38, .09, -.13, 1.46, "c_white" if top != "c_white" else "c_navy")


def _leg(name, lk):
    mb = W.MB(name)
    limb(mb, (0, 0, 0), (0, 0, -.72), .095, .08, lk["bottom"])
    rbox(mb, -.085, -.2, -.86, .085, .1, -.76, lk["shoe"], c=.04)
    mb.box(-.088, -.205, -.88, .088, .105, -.84, "shoe_sole")
    return mb


def _arm(name, lk):
    mb = W.MB(name)
    ball(mb, 0, 0, 0, .085, lk["sleeve"], seg=8, rings=5)
    limb(mb, (0, 0, 0), (0, 0, -.3), .08, .075, lk["sleeve"])
    limb(mb, (0, 0, -.3), (0, 0, -.56), .06, .055, lk["skin"])
    ball(mb, 0, 0, -.6, .07, lk["skin"], seg=8, rings=5)
    return mb


def character(name, look="mahasiswa", loc=(0, 0, 0), rot=0.0, s=CH_S, hold=None):
    """karakter: badan+kepala (1 objek) + 2 kaki + 2 lengan (anak, berporos di pinggul/bahu).
    hold: None | 'basket' | 'phone' | 'clothes' | 'tablet' | 'wrench' | 'card'."""
    lk = LOOKS[look] if isinstance(look, str) else look
    mb = W.MB(name)
    _body(mb, lk)
    _head(mb, lk)
    body = mb.build()
    body.location = loc
    body.rotation_euler.z = rot
    body.scale = (s,) * 3
    parts = {"body": body}
    for side, sx in (("L", -1), ("R", 1)):
        lg = _leg(f"{name}_leg{side}", lk).build()
        lg.parent = body
        lg.location = (sx * .11, 0, .86)
        parts["leg" + side] = lg
        ar = _arm(f"{name}_arm{side}", lk).build()
        ar.parent = body
        ar.location = (sx * .31, 0, 1.4)
        ar.rotation_euler.y = sx * -.12
        parts["arm" + side] = ar
    if hold:
        hb = W.MB(f"{name}_hold")
        if hold == "basket":
            rbox(hb, -.36, -.62, .78, .36, -.18, 1.08, "basket", c=.06)
            for k, col in enumerate(("cloth1", "cloth2", "cloth3", "cloth4")):
                ball(hb, -.2 + k * .13, -.4, 1.1, .12, col, seg=8, rings=5, sz=.08)
            for sx in (-1, 1):
                parts["arm" + ("L" if sx < 0 else "R")].rotation_euler = (-1.05, 0, 0)
        elif hold == "clothes":
            rbox(hb, -.3, -.6, 1.0, .3, -.25, 1.18, "cloth2", c=.04)
            rbox(hb, -.28, -.58, 1.18, .28, -.27, 1.3, "cloth1", c=.04)
            for sx in (-1, 1):
                parts["arm" + ("L" if sx < 0 else "R")].rotation_euler = (-1.0, 0, 0)
        elif hold in ("phone", "card"):
            hb.box(.2, -.58, 1.08, .34, -.56, 1.34, "phone_blk" if hold == "phone" else "lw_teal")
            if hold == "phone":
                hb.box(.215, -.585, 1.1, .325, -.58, 1.32, "kiosk_scr")
            parts["armR"].rotation_euler = (-1.25, 0, .25)
        elif hold == "tablet":
            hb.box(-.25, -.6, 1.02, .25, -.55, 1.38, "phone_blk")
            hb.box(-.22, -.605, 1.05, .22, -.6, 1.35, "kiosk_scr")
            for sx in (-1, 1):
                parts["arm" + ("L" if sx < 0 else "R")].rotation_euler = (-1.15, 0, sx * -.3)
        elif hold == "wrench":
            hb.box(.27, -.5, 1.0, .33, -.45, 1.42, "wm_ring")
            parts["armR"].rotation_euler = (-1.1, 0, 0)
        hob = hb.build()
        hob.parent = body
        parts["hold"] = hob
    return parts


def pose(parts, kind, f=None):
    """pose statis: stand | wave | cheer | point | sit | think | arms_fwd. Jika f diberi: keyframe."""
    ar, al, lr, ll = parts["armR"], parts["armL"], parts["legR"], parts["legL"]
    vals = {
        "stand": ((0, -.12, 0), (0, .12, 0), (0, 0, 0), (0, 0, 0)),
        "wave": ((0, -2.6, 0), (0, .12, 0), (0, 0, 0), (0, 0, 0)),
        "cheer": ((0, -2.7, 0), (0, 2.7, 0), (0, 0, 0), (0, 0, 0)),
        "point": ((-1.5, -.2, 0), (0, .12, 0), (0, 0, 0), (0, 0, 0)),
        "sit": ((-.5, -.12, 0), (-.5, .12, 0), (-1.5, 0, 0), (-1.5, 0, 0)),
        "think": ((-2.3, -.5, 0), (-.6, .3, 0), (0, 0, 0), (0, 0, 0)),
        "arms_fwd": ((-1.2, 0, 0), (-1.2, 0, 0), (0, 0, 0), (0, 0, 0)),
        "shrug": ((0, -.9, 0), (0, .9, 0), (0, 0, 0), (0, 0, 0)),
    }[kind]
    for ob, v in zip((ar, al, lr, ll), vals):
        ob.rotation_euler = v
        if f is not None:
            ob.keyframe_insert("rotation_euler", frame=f)


def walk_cycle(parts, f0, f1, period=18, amp=.55, arms=True):
    """ayunan kaki & lengan (keyframe tiap seperempat langkah)."""
    for f in range(f0, f1 + 1, max(1, period // 4)):
        ph = 2 * math.pi * (f - f0) / period
        a = amp * math.sin(ph)
        for side, sgn in (("L", 1), ("R", -1)):
            lg = parts["leg" + side]
            lg.rotation_euler.x = sgn * a
            lg.keyframe_insert("rotation_euler", frame=f)
            if arms and "hold" not in parts:
                ar = parts["arm" + side]
                ar.rotation_euler.x = -sgn * a * .8
                ar.keyframe_insert("rotation_euler", frame=f)
    for nm in ("legL", "legR", "armL", "armR"):
        ob = parts[nm]
        if ob.animation_data and ob.animation_data.action:
            for fc in _fc(ob):
                for kp in fc.keyframe_points:
                    kp.interpolation = "BEZIER"


def _fc(ob):
    act = ob.animation_data.action
    if hasattr(act, "fcurves"):
        return act.fcurves
    out = []
    for layer in act.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                out += list(cb.fcurves)
    return out


def walk_to(parts, pts, f0, speed=2.2, fps=30, period=18):
    """jalan menyusuri titik-titik (x,y) dari frame f0; menghadap arah gerak. return frame tiba."""
    b = parts["body"]
    f = f0
    z = b.location.z
    b.location = (pts[0][0], pts[0][1], z)
    b.keyframe_insert("location", frame=max(1, f))
    for p, q in zip(pts[:-1], pts[1:]):
        d = math.dist(p, q)
        ang = math.atan2(q[1] - p[1], q[0] - p[0]) + math.pi / 2
        b.rotation_euler.z = ang
        b.keyframe_insert("rotation_euler", frame=max(1, f))
        f2 = f + max(1, int(d / speed * fps))
        b.location = (q[0], q[1], z)
        b.keyframe_insert("location", frame=f2)
        f = f2
    walk_cycle(parts, max(1, f0), f, period=period)
    for nm in ("legL", "legR", "armL", "armR"):
        ob = parts[nm]
        rest = (0, -.12 if nm == "armR" else (.12 if nm == "armL" else 0), 0)
        if "hold" in parts and nm.startswith("arm"):
            continue
        ob.rotation_euler = rest
        ob.keyframe_insert("rotation_euler", frame=f + 3)
    return f


# ------------------------------------------------------------------ mesin & props laundry
def washer(mb, x, y, z, s=1.0, key="wm_body", lcd=True):
    """mesin cuci front-loader (depan menghadap -Y), lebar 1.2*s. Return pusat pintu (x,y,z)."""
    w, d, h = 1.2 * s, 1.1 * s, 1.5 * s
    rbox(mb, x - w / 2, y - d / 2, z, x + w / 2, y + d / 2, z + h, key, c=.08 * s)
    mb.box(x - w / 2 + .02, y - d / 2 - .02, z + h - .32 * s, x + w / 2 - .02, y - d / 2 + .05, z + h - .04 * s,
           "wm_panel")
    if lcd:
        mb.box(x + .12 * s, y - d / 2 - .035, z + h - .26 * s, x + .42 * s, y - d / 2 - .015, z + h - .12 * s,
               "wm_lcd")
    mb.cyl(x - .32 * s, y - d / 2 - .02, z + h - .2 * s, z + h - .17 * s, .06 * s, "wm_ring", n=8)   # kenop
    mb.box(x - .5 * s, y - d / 2 - .03, z + h - .29 * s, x - .1 * s, y - d / 2 - .01, z + h - .27 * s, "lw_teal")
    cz = z + .68 * s
    fy = y - d / 2
    mb.disc_y(x, fy + .01, cz, .43 * s, .07 * s, "wm_ring", n=20)
    mb.disc_y(x, fy - .06, cz, .35 * s, .01 * s, "wm_drum", n=20)          # rongga drum gelap
    mb.disc_y(x, fy - .22 * s, cz, .35 * s, .015 * s, "wm_glass", n=20)     # kaca pintu (transparan)
    mb.disc_y(x + .4 * s, fy - .1, cz, .06 * s, .12 * s, "wm_ring", n=8)   # engsel/handle
    mb.box(x - .5 * s, fy - .04, z, x + .5 * s, fy + .02, z + .1 * s, "wm_panel")    # plint
    return (x, fy - .13 * s, cz)


def dryer(mb, x, y, z, s=1.0):
    """mesin pengering (lebih pendek, pintu besar)."""
    w, d, h = 1.2 * s, 1.1 * s, 1.25 * s
    rbox(mb, x - w / 2, y - d / 2, z, x + w / 2, y + d / 2, z + h, "dr_body", c=.07 * s)
    mb.box(x - w / 2 + .03, y - d / 2 - .02, z + h - .22 * s, x + w / 2 - .03, y - d / 2 + .05, z + h - .03 * s,
           "lw_navy")
    mb.box(x + .15 * s, y - d / 2 - .035, z + h - .17 * s, x + .45 * s, y - d / 2 - .015, z + h - .08 * s, "wm_lcd")
    cz = z + .5 * s
    fy = y - d / 2
    mb.disc_y(x, fy + .01, cz, .42 * s, .07 * s, "wm_ring", n=20)
    mb.disc_y(x, fy - .06, cz, .35 * s, .01 * s, "wm_drum", n=20)
    mb.disc_y(x, fy - .2 * s, cz, .35 * s, .015 * s, "wm_glass", n=20)
    return (x, fy - .12 * s, cz)


def drum_clothes(name, center, s=1.0, n=7, money=False, seed=3):
    """isi drum (pakaian warna-warni / lembaran uang) yang bisa diputar (sumbu Y)."""
    rnd = random.Random(seed)
    mb = W.MB(name)
    for k in range(n):
        a = 2 * math.pi * k / n + rnd.uniform(-.3, .3)
        r = rnd.uniform(.08, .24) * s
        x, z = math.cos(a) * r, math.sin(a) * r
        if money:
            mb.box(x - .14 * s, -.02 * s, z - .07 * s, x + .14 * s, .02 * s, z + .07 * s,
                   rnd.choice(["money_g", "money_g2"]))
        else:
            ball(mb, x, 0, z, .11 * s, rnd.choice(["cloth1", "cloth2", "cloth3", "cloth4", "cloth5"]), seg=7,
                 rings=4, sy=.05 * s)
    ob = mb.build()
    ob.location = center
    return ob


def spin(ob, f0, f1, turns_per_sec=1.0, fps=30):
    from scenes import key
    key(ob, "rotation_euler", f0, (0, 0, 0))
    key(ob, "rotation_euler", f1, (0, 2 * math.pi * turns_per_sec * (f1 - f0) / fps, 0))
    for fc in _fc(ob):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"


def kiosk(name, s=1.0):
    """kios pembayaran: layar QR + slot koin + tap kartu. Asal di lantai, menghadap -Y. Return (obj, screen)."""
    mb = W.MB(name)
    rbox(mb, -.42 * s, -.3 * s, 0, .42 * s, .3 * s, 1.75 * s, "kiosk", c=.08)
    mb.box(-.32 * s, -.32 * s, .85 * s, .32 * s, -.29 * s, 1.6 * s, "kiosk_scr")
    # pola QR
    rnd = random.Random(11)
    q0x, q0z, cell = -.2 * s, 1.0 * s, .045 * s
    for i in range(9):
        for j in range(9):
            corner = (i < 3 and j < 3) or (i > 5 and j < 3) or (i < 3 and j > 5)
            if corner or rnd.random() < .45:
                mb.box(q0x + i * cell, -.335 * s, q0z + j * cell, q0x + (i + 1) * cell, -.322 * s, q0z + (j + 1) * cell,
                       "qr")
    mb.box(-.2 * s, -.34 * s, .55 * s, .2 * s, -.29 * s, .72 * s, "lw_teal")        # tap kartu
    mb.box(.1 * s, -.34 * s, .38 * s, .26 * s, -.29 * s, .44 * s, "wm_ring")         # slot koin
    mb.box(-.42 * s, -.3 * s, 1.75 * s, .42 * s, .3 * s, 1.85 * s, "lw_teal")
    ob = mb.build()
    return ob


def coin(mb, x, y, z, s=1.0):
    mb.disc_y(x, y, z, .12 * s, .03 * s, "coin", n=12)


def detergent_shelf(mb, x0, y, z, w=2.4):
    mb.box(x0, y - .2, z + 1.4, x0 + w, y + .2, z + 1.47, "lw_wood")
    mb.box(x0, y - .2, z + 2.0, x0 + w, y + .2, z + 2.07, "lw_wood")
    rnd = random.Random(5)
    for zz in (z + 1.47, z + 2.07):
        x = x0 + .1
        while x < x0 + w - .25:
            ww = rnd.uniform(.18, .26)
            rbox(mb, x, y - .1, zz, x + ww, y + .1, zz + rnd.uniform(.3, .42),
                 rnd.choice(["det1", "det2", "det3", "det4"]), c=.03)
            x += ww + .05


def folding_table(mb, x, y, z, w=2.6, d=1.2):
    mb.box(x - w / 2, y - d / 2, z + .9, x + w / 2, y + d / 2, z + .98, "lw_wood")
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box(x + sx * (w / 2 - .12) - .05, y + sy * (d / 2 - .12) - .05, z, x + sx * (w / 2 - .12) + .05,
                   y + sy * (d / 2 - .12) + .05, z + .9, "lw_frame")
    # tumpukan baju terlipat
    for k, (dx, col) in enumerate(((-.7, "cloth2"), (-.2, "cloth1"), (.45, "cloth4"))):
        for j in range(3):
            rbox(mb, x + dx - .22, y - .2, z + .98 + j * .07, x + dx + .22, y + .2, z + 1.04 + j * .07,
                 (col, "cloth3", "cloth5")[j % 3] if j else col, c=.03)


def seat_bench(mb, x, y, z, w=2.4, key="cushion"):
    mb.box(x - w / 2, y - .35, z + .4, x + w / 2, y + .35, z + .5, "lw_wood")
    rbox(mb, x - w / 2 + .05, y - .32, z + .5, x + w / 2 - .05, y + .32, z + .62, key, c=.05)
    mb.box(x - w / 2, y + .28, z + .5, x + w / 2, y + .38, z + 1.1, "lw_wood")
    for sx in (-1, 1):
        mb.box(x + sx * (w / 2 - .1) - .05, y - .3, z, x + sx * (w / 2 - .1) + .05, y + .3, z + .4, "lw_frame")


def basket_obj(mb, x, y, z, col="basket", full=True):
    rbox(mb, x - .35, y - .25, z, x + .35, y + .25, z + .35, col, c=.06)
    if full:
        for k, c in enumerate(("cloth1", "cloth3", "cloth2")):
            ball(mb, x - .18 + k * .18, y, z + .38, .13, c, seg=8, rings=5, sz=.09)


def pendant(mb, x, y, z_ceiling, drop=1.0):
    mb.box(x - .01, y - .01, z_ceiling - drop, x + .01, y + .01, z_ceiling, "lw_frame")
    mb.cyl(x, y, z_ceiling - drop - .25, z_ceiling - drop, .3, "lw_yellow", n=12, r_top=.08)


def sparkle(name, loc, s=.4, key="spark"):
    """bintang kilau 4 sudut (pakai untuk 'bersih')."""
    mb = W.MB(name)
    pts = []
    for k in range(8):
        a = math.pi / 4 * k
        r = s if k % 2 == 0 else s * .28
        pts.append((math.cos(a) * r, math.sin(a) * r))
    mb.prism_y(pts, -.03, .03, key)
    ob = mb.build(loc)
    ob.data.materials[0] = lp.mat(key, emission=3.0)
    return ob


# ------------------------------------------------------------------ gedung laundry koin
LW, LD = 14.0, 11.0                 # ukuran gedung
LH1 = 4.2                           # tinggi lantai dasar


def laundromat(name, interior=True):
    """gedung laundry koin 2 lantai, muka kaca penuh, papan nama, isi mesin di balik kaca. Return (MB, top)."""
    mb = W.MB(name)
    w, d = LW, LD
    z0 = Z
    h2 = z0 + LH1 + 3.4
    # lantai & dinding samping/belakang
    mb.box(-w / 2, -d / 2, z0, w / 2, d / 2, z0 + .12, "lw_floor")
    mb.box(-w / 2, d / 2 - .3, z0, w / 2, d / 2, h2, "lw_wall")
    mb.box(-w / 2, -d / 2, z0, -w / 2 + .3, d / 2, h2, "lw_wall")
    mb.box(w / 2 - .3, -d / 2, z0, w / 2, d / 2, h2, "lw_wall")
    # aksen teal di dinding samping + garis
    mb.box(-w / 2 - .02, -d / 2, z0, -w / 2 + .02, d / 2, z0 + 1.2, "lw_teal")
    mb.box(w / 2 - .02, -d / 2, z0, w / 2 + .02, d / 2, z0 + 1.2, "lw_teal")
    # plafon lantai dasar + lantai atas
    mb.box(-w / 2, -d / 2, z0 + LH1, w / 2, d / 2, z0 + LH1 + .3, "lw_wall")
    # lantai atas: kayu slat + jendela
    mb.box(-w / 2, -d / 2 + .3, z0 + LH1 + .3, w / 2, -d / 2 + .5, h2, "lw_wood")
    for k in range(int(w / .5)):
        x = -w / 2 + .1 + k * .5
        mb.box(x, -d / 2 + .15, z0 + LH1 + .3, x + .22, -d / 2 + .3, h2, "lw_wood2")
    for x in (-3.6, 3.6):
        mb.box(x - 1.9, -d / 2 + .05, z0 + LH1 + .9, x + 1.9, -d / 2 + .2, h2 - .6, "lw_frame")
        mb.box(x - 1.75, -d / 2, z0 + LH1 + 1.0, x + 1.75, -d / 2 + .1, h2 - .7, "lw_glass")
    # atap datar + parapet + unit AC
    mb.box(-w / 2 - .2, -d / 2 - .2, h2, w / 2 + .2, d / 2 + .2, h2 + .35, "lw_navy")
    mb.box(3, 1, h2 + .35, 5, 3, h2 + 1.3, "wm_panel")
    mb.box(-5, 0, h2 + .35, -3.2, 1.6, h2 + 1.1, "wm_panel")
    # rangka kaca depan lantai dasar
    fy = -d / 2
    for x in (-w / 2 + .15, -2.4, 2.4, w / 2 - .15):
        mb.box(x - .12, fy - .12, z0, x + .12, fy + .12, z0 + LH1, "lw_frame")
    mb.box(-w / 2, fy - .12, z0 + LH1 - .25, w / 2, fy + .12, z0 + LH1, "lw_frame")
    mb.box(-w / 2, fy - .12, z0, w / 2, fy + .12, z0 + .25, "lw_frame")
    mb.box(-1.15, fy - .16, z0 + .25, -1.05, fy + .05, z0 + 3.2, "lw_frame")      # pintu kaca ganda
    mb.box(1.05, fy - .16, z0 + .25, 1.15, fy + .05, z0 + 3.2, "lw_frame")
    mb.box(-1.15, fy - .16, z0 + 3.1, 1.15, fy + .05, z0 + 3.25, "lw_frame")
    mb.box(-.05, fy - .2, z0 + 1.2, .05, fy - .12, z0 + 2.0, "metal")
    # papan nama besar (teks ditambah terpisah)
    mb.box(-w / 2 - .1, fy - .5, z0 + LH1 - .1, w / 2 + .1, fy + .02, z0 + LH1 + 1.35, "lw_teal")
    mb.box(-w / 2 - .1, fy - .55, z0 + LH1 - .15, w / 2 + .1, fy - .45, z0 + LH1 - .02, "lw_yellow")
    # ikon mesin cuci di papan
    ix = -w / 2 + 1.25
    mb.box(ix - .55, fy - .58, z0 + LH1 + .1, ix + .55, fy - .5, z0 + LH1 + 1.2, "wm_body")
    mb.disc_y(ix, fy - .6, z0 + LH1 + .58, .33, .05, "lw_navy", n=16)
    mb.disc_y(ix, fy - .64, z0 + LH1 + .58, .22, .03, "wm_glass", n=16)
    # kanopi kecil di atas pintu
    mb.box(-2.6, fy - 1.5, z0 + 3.35, 2.6, fy, z0 + 3.5, "lw_navy")
    # teras: lantai, tanaman, bangku, rak sepeda
    mb.box(-w / 2, fy - 4.0, z0, w / 2, fy, z0 + .1, "lw_floor2")
    for x in (-w / 2 + .7, w / 2 - .7):
        H.plant(mb, x, fy - .6, z0 + .1, 1.1)
    seat_bench(mb, -4.6, fy - 1.0, z0 + .1, w=2.6, key="cushion2")
    for k in range(3):
        x = 4.2 + k * .9
        mb.box(x - .04, fy - 3.4, z0 + .1, x + .04, fy - 1.6, z0 + .16, "metal")
        mb.box(x - .04, fy - 2.6, z0 + .1, x + .04, fy - 2.5, z0 + .9, "metal")
    # isi di balik kaca: deret mesin cuci menghadap jalan? -> mesin di dinding kiri & kanan, terlihat dari depan
    if interior:
        laundromat_inside(mb, z0 + .12)
    return mb, h2 + 1.3


def laundromat_inside(mb, z):
    """deret mesin (dinding belakang), pengering bertumpuk (dinding kanan), meja lipat, kios."""
    w, d = LW, LD
    back = d / 2 - .3 - .6
    for k in range(6):
        washer(mb, -5.2 + k * 1.35, back, z, 1.0)
    for j in range(2):                               # pengering bertumpuk di pojok kanan belakang
        dryer(mb, w / 2 - 1.2, back, z + j * 1.3, 1.0)
    folding_table(mb, 0, -1.2, z, 3.0, 1.1)
    seat_bench(mb, -4.3, -3.6, z, 2.4, "cushion")
    mb.box(4.6, -3.9, z, 5.4, -3.3, z + 1.75, "kiosk")
    mb.box(4.7, -3.92, z + .85, 5.3, -3.88, z + 1.6, "kiosk_scr")
    for x in (-4, 0, 4):
        pendant(mb, x, -1.5, z + LH1 - .15, .8)


def laundromat_sign(prefix, loc, facing, lit=1.4):
    """tulisan 'LAUNDRY KOIN' + 'SELF SERVICE' di papan (menyala)."""
    fy = -LD / 2
    t1 = H.text(prefix + "_t1", "LAUNDRY KOIN", .92, "lw_sign", depth=.1, loc=(.75, fy - .6, Z + LH1 + .38),
                emission=lit)
    t2 = H.text(prefix + "_t2", "SELF SERVICE  •  CUCI KERING", .3, "lw_yellow", depth=.05,
                loc=(.75, fy - .6, Z + LH1 + .05), emission=lit * .8)
    return [H.to_world(t1, loc, facing), H.to_world(t2, loc, facing)]


# ------------------------------------------------------------------ set interior studio (cutaway)
RW_, RD_ = 16.0, 12.0               # ukuran ruangan studio


def interior_set(name, cx, cy, people=True):
    """ruang laundry koin terbuka (2 dinding): mesin cuci, pengering bertumpuk, kios bayar, meja lipat,
    bangku, rak deterjen, tanaman, lampu gantung, papan dinding. Return dict titik-titik penting."""
    mb = W.MB(name)
    w, d = RW_, RD_
    x0, y0 = cx - w / 2, cy - d / 2
    hz = 4.6
    # lantai tegel kotak-kotak
    mb.box(x0, y0, -.2, x0 + w, y0 + d, 0, "lw_floor2")
    for i in range(int(w)):
        for j in range(int(d)):
            if (i + j) % 2 == 0:
                mb.box(x0 + i + .02, y0 + j + .02, 0, x0 + i + .98, y0 + j + .98, .01, "lw_floor")
    # dinding belakang (teal bawah, krem atas) & dinding kiri
    mb.box(x0, y0 + d, -.2, x0 + w, y0 + d + .3, hz, "lw_wall")
    mb.box(x0, y0 + d - .02, 0, x0 + w, y0 + d, 1.3, "lw_teal")
    mb.box(x0 - .3, y0, -.2, x0, y0 + d + .3, hz, "lw_wall")
    mb.box(x0, y0, 0, x0 + .02, y0 + d, 1.3, "lw_teal")
    mb.box(x0, y0 + d - .03, 1.3, x0 + w, y0 + d - .01, 1.4, "lw_yellow")
    # deret mesin cuci di dinding belakang (6 unit)
    doors, washers = [], []
    for k in range(6):                       # tiap mesin objek sendiri (bisa muncul satu per satu)
        wx, wy = x0 + 1.3 + k * 1.4, y0 + d - .65
        wmb = W.MB(f"{name}_wm{k}")
        dc = washer(wmb, 0, 0, 0, 1.0)
        washers.append(wmb.build((wx, wy, 0)))
        doors.append((wx + dc[0], wy + dc[1], dc[2]))
    # papan dinding: ikon & petunjuk (teks terpisah)
    mb.box(x0 + 1.0, y0 + d - .05, 2.3, x0 + 8.8, y0 + d - .02, 3.9, "lw_navy")
    # pengering bertumpuk di dinding kiri (menghadap +X): dibangun lokal lalu diputar -> pakai objek terpisah
    dmb = W.MB(name + "_dry")
    dry_doors = []
    for k in range(3):
        for j in range(2):
            dry_doors.append(dryer(dmb, -1.4 + k * 1.4, 0, j * 1.3, 1.0))
    dob = dmb.build((x0 + .65, y0 + 5.0, 0), -math.pi / 2)
    # rak deterjen di dinding kiri bagian depan
    smb = W.MB(name + "_shelf")
    detergent_shelf(smb, -1.2, 0, 0, 2.4)
    smb.build((x0 + .3, y0 + 1.8, 0), -math.pi / 2)
    # vending deterjen di pojok kanan dinding belakang
    rbox(mb, x0 + 10.0, y0 + d - 1.0, 0, x0 + 11.3, y0 + d - .1, 2.4, "lw_teal", c=.08)
    mb.box(x0 + 10.1, y0 + d - 1.03, .9, x0 + 11.2, y0 + d - .98, 2.2, "lw_glass")
    for i in range(3):
        for j in range(3):
            mb.box(x0 + 10.2 + i * .35, y0 + d - .95, 1.0 + j * .4, x0 + 10.45 + i * .35, y0 + d - .7, 1.28 + j * .4,
                   ("det1", "det2", "det3", "det4")[(i + j) % 4])
    # kios bayar
    kob = kiosk(name + "_kiosk")
    kob.location = (x0 + 12.4, y0 + d - .7, 0)
    # meja lipat & bangku tunggu
    folding_table(mb, x0 + 7.0, y0 + 5.2, 0, 3.2, 1.2)
    seat_bench(mb, x0 + 12.5, y0 + 4.6, 0, 3.0, "cushion")
    mb.box(x0 + 11.4, y0 + 3.2, 0, x0 + 13.6, y0 + 3.9, .45, "lw_wood")         # meja kopi
    mb.cyl(x0 + 12.0, y0 + 3.55, .45, .62, .14, "c_white", n=10)
    # tanaman, keranjang, tempat sampah
    for (px, py, s) in ((x0 + w - .8, y0 + d - .8, 1.3), (x0 + .9, y0 + d - .8, 1.2), (x0 + w - .8, y0 + 1.0, 1.0)):
        H.plant(mb, px, py, 0, s)
    basket_obj(mb, x0 + 3.0, y0 + d - 2.0, 0, "basket2")
    basket_obj(mb, x0 + 5.7, y0 + 4.2, .98, "basket", full=False)
    # lampu gantung & plafon tipis (hanya bingkai)
    for (px, py) in ((x0 + 4, y0 + 5), (x0 + 8, y0 + 5), (x0 + 12, y0 + 5)):
        pendant(mb, px, py, hz, 1.2)
    # jam dinding & TV
    mb.disc_y(x0 + 13.5, y0 + d - .03, 3.3, .45, .06, "c_white", n=16)
    mb.disc_y(x0 + 13.5, y0 + d - .09, 3.3, .38, .02, "lw_wall", n=16)
    mb.box(x0 + 13.48, y0 + d - .11, 3.3, x0 + 13.52, y0 + d - .1, 3.6, "lw_frame")
    mb.box(x0 + 13.5, y0 + d - .11, 3.28, x0 + 13.75, y0 + d - .1, 3.32, "lw_frame")
    ob = mb.build()
    info = {"obj": ob, "doors": doors, "washers": washers, "dry": dob, "dry_doors": dry_doors, "kiosk": kob,
            "x0": x0, "y0": y0, "w": w, "d": d}
    t = H.text(name + "_wall_t", "LAUNDRY KOIN", .62, "lw_sign", depth=.04,
               loc=(x0 + 4.9, y0 + d - .06, 3.05), emission=.8)
    t2 = H.text(name + "_wall_t2", "1. MASUKKAN  2. BAYAR  3. CUCI", .27, "lw_yellow", depth=.03,
                loc=(x0 + 4.9, y0 + d - .06, 2.55), emission=.6)
    info["wall_text"] = [t, t2]
    return info


# ------------------------------------------------------------------ laundry konvensional
def conventional_set(name, cx, cy):
    """laundry kiloan konvensional: meja kasir, timbangan, tumpukan baju, setrika, karyawan."""
    mb = W.MB(name)
    w, d = 9.0, 7.0
    x0, y0 = cx - w / 2, cy - d / 2
    mb.box(x0, y0, -.2, x0 + w, y0 + d, 0, "floor_tile")
    mb.box(x0, y0 + d, -.2, x0 + w, y0 + d + .25, 3.6, "kos_wall")
    mb.box(x0 - .25, y0, -.2, x0, y0 + d + .25, 3.6, "kos_wall")
    # meja kasir & timbangan
    mb.box(x0 + 1.0, y0 + 2.4, 0, x0 + 5.0, y0 + 3.2, 1.05, "lw_wood")
    mb.box(x0 + 1.0, y0 + 2.35, 1.05, x0 + 5.0, y0 + 3.25, 1.12, "lw_wood2")
    mb.box(x0 + 1.4, y0 + 2.5, 1.12, x0 + 2.2, y0 + 3.1, 1.25, "wm_panel")
    mb.box(x0 + 1.5, y0 + 2.45, 1.16, x0 + 1.9, y0 + 2.5, 1.22, "wm_lcd")
    # rak penuh bungkusan plastik
    for j in range(3):
        mb.box(x0 + .3, y0 + d - .8, .6 + j * .9, x0 + 5.5, y0 + d - .1, .66 + j * .9, "metal")
        for k in range(6):
            rbox(mb, x0 + .45 + k * .85, y0 + d - .7, .66 + j * .9, x0 + 1.15 + k * .85, y0 + d - .2, 1.2 + j * .9,
                 ("cloth2", "cloth1", "cloth4", "cloth3", "cloth5", "cloth2")[(k + j) % 6], c=.08)
    # gunungan cucian
    for k in range(9):
        ball(mb, x0 + 6.5 + (k % 3) * .55, y0 + 4.6 + (k // 3) * .5, .35 + (k // 3) * .1, .45,
             ("cloth1", "cloth2", "cloth3", "cloth4", "cloth5")[k % 5], seg=8, rings=5, sz=.35)
    # meja setrika
    mb.box(x0 + 6.0, y0 + 1.6, .9, x0 + 8.4, y0 + 2.3, .96, "c_grey")
    mb.box(x0 + 7.0, y0 + 1.9, 0, x0 + 7.1, y0 + 2.0, .9, "metal")
    mb.box(x0 + 7.4, y0 + 1.75, .96, x0 + 7.9, y0 + 2.1, 1.1, "c_white")
    # 2 mesin cuci besar di belakang
    washer(mb, x0 + 7.0, y0 + d - .7, 0, 1.05)
    washer(mb, x0 + 8.3, y0 + d - .7, 0, 1.05)
    ob = mb.build()
    return ob


# ------------------------------------------------------------------ kos, apartemen, kampus, kantor
def kos(name, w=16.0, d=10.0, floors=3, rnd=None):
    """kos-kosan 3 lantai: koridor luar, pintu kamar berderet, jemuran penuh baju di balkon."""
    rnd = rnd or random.Random(2)
    mb = W.MB(name)
    fh = 3.0
    h = Z + floors * fh
    mb.box(-w / 2, -d / 2 + 2, Z, w / 2, d / 2, h, "kos_wall")
    for f in range(floors):
        z = Z + f * fh
        mb.box(-w / 2, -d / 2, z + fh - .2, w / 2, -d / 2 + 2, z + fh, "kos_wall2")        # lantai koridor
        mb.box(-w / 2, -d / 2, z + fh, w / 2, -d / 2 + .12, z + fh + 1.0, "kos_trim")       # pagar
        for k in range(5):
            x = -w / 2 + 1.6 + k * 3.0
            mb.box(x - .5, -d / 2 + 1.98, z + .1, x + .5, -d / 2 + 2.05, z + 2.2, "kos_door")
            mb.box(x + .8, -d / 2 + 1.98, z + 1.0, x + 1.8, -d / 2 + 2.05, z + 2.0, "frame")
            mb.box(x + .87, -d / 2 + 1.95, z + 1.07, x + 1.73, -d / 2 + 2.0, z + 1.93, "glass2")
        # jemuran di pagar
        for k in range(12):
            if rnd.random() < .7:
                x = -w / 2 + .6 + k * 1.25
                mb.box(x, -d / 2 - .06, z + fh + .2, x + .8, -d / 2 + .02, z + fh + .2 + rnd.uniform(.55, .9),
                       rnd.choice(["cloth1", "cloth2", "cloth3", "cloth4", "cloth5", "c_white"]))
    for f in range(1, floors):
        mb.box(-w / 2, -d / 2, Z + f * fh - .2, -w / 2 + .3, -d / 2 + 2, Z + f * fh, "kos_wall2")
    for x in (-w / 2 + .2, w / 2 - .2):
        mb.box(x - .2, -d / 2, Z, x + .2, -d / 2 + .4, h + 1.0, "kos_wall2")
    mb.box(-w / 2 - .3, -d / 2 - .3, h + 1.0, w / 2 + .3, d / 2 + .3, h + 1.3, "kos_trim")
    mb.box(-w / 2 + 1, d / 2 - 3, h + 1.3, -w / 2 + 2.6, d / 2 - 1.4, h + 3.0, "tank")      # tandon
    # papan "KOS PUTRA/PUTRI" (teks terpisah)
    mb.box(-2.2, -d / 2 - .4, Z + 1.0, 2.2, -d / 2 - .3, Z + 2.0, "c_white")
    for sx in (-1.9, 1.9):
        mb.box(sx - .06, -d / 2 - .38, Z, sx + .06, -d / 2 - .3, Z + 1.0, "metal")
    return mb, h + 1.3


def kos_sign(prefix, loc, facing, d=10.0):
    o = H.text(prefix + "_t", "KOS", .62, "kos_trim", depth=.06, loc=(0, -d / 2 - .42, Z + 1.18))
    return H.to_world(o, loc, facing)


def apartment(name, w=14.0, d=12.0, floors=12):
    mb = W.MB(name)
    fh = 3.0
    h = Z + 1.0 + floors * fh
    mb.box(-w / 2, -d / 2, Z, w / 2, d / 2, h, "apt_wall")
    W.windows(mb, w, d, Z + 1.0, floors, fh=fh, ww=1.6, wh=1.8)
    for f in range(1, floors):
        z = Z + 1.0 + f * fh
        mb.box(-w / 2 + 1, -d / 2 - 1.0, z - .1, -w / 2 + 5, -d / 2, z + .05, "apt_acc")        # balkon
        mb.box(-w / 2 + 1, -d / 2 - 1.05, z, -w / 2 + 5, -d / 2 - .95, z + .9, "lw_glass")
        mb.box(w / 2 - 5, -d / 2 - 1.0, z - .1, w / 2 - 1, -d / 2, z + .05, "apt_acc")
        mb.box(w / 2 - 5, -d / 2 - 1.05, z, w / 2 - 1, -d / 2 - .95, z + .9, "lw_glass")
    mb.box(-1.0, -d / 2 - .05, Z, 1.0, -d / 2 + .1, h, "apt_acc")                             # pita vertikal
    mb.box(-w / 2 - .3, -d / 2 - .3, h, w / 2 + .3, d / 2 + .3, h + .5, "apt_acc")
    mb.box(-3, -2, h + .5, 3, 2, h + 2.2, "apt_wall")
    mb.box(-4, -d / 2 - 2.5, Z + 3.5, 4, -d / 2, Z + 3.8, "apt_acc")                          # kanopi
    return mb, h + 2.2


def campus(name, w=26.0, d=13.0):
    mb = W.MB(name)
    h = Z + 9.0
    mb.box(-w / 2, -d / 2, Z, w / 2, d / 2, h, "kampus")
    W.windows(mb, w, d, Z + .2, 3, fh=2.9, skip_front_ground=False, ww=1.4, wh=1.7)
    # portiko bertiang + atap pelana
    mb.box(-5.5, -d / 2 - 3.2, Z, 5.5, -d / 2, Z + .4, "pool_edge")
    for k in range(6):
        x = -4.8 + k * 1.92
        mb.cyl(x, -d / 2 - 2.6, Z + .4, h - .5, .35, "c_white", n=10)
    mb.box(-5.8, -d / 2 - 3.4, h - .5, 5.8, -d / 2 + .1, h + .2, "c_white")
    mb.prism_x([(-d / 2 - 3.4, h + .2), (-d / 2 + .1, h + .2), (-d / 2 + .1, h + 2.4)], -5.8, 5.8, "kampus_roof")
    mb.box(-w / 2 - .3, -d / 2 - .3, h, w / 2 + .3, d / 2 + .3, h + .5, "kampus_roof")
    # tiang bendera
    mb.box(w / 2 - 2, -d / 2 - 5, Z, w / 2 - 1.85, -d / 2 - 4.85, Z + 10, "metal")
    mb.box(w / 2 - 1.85, -d / 2 - 4.93, Z + 8.6, w / 2 + .4, -d / 2 - 4.9, Z + 9.3, "flag_red")
    mb.box(w / 2 - 1.85, -d / 2 - 4.93, Z + 7.9, w / 2 + .4, -d / 2 - 4.9, Z + 8.6, "c_white")
    return mb, h + 2.4


def courthouse(name, w=14.0, d=9.0):
    """gedung pengadilan generik (tiang klasik + atap segitiga) untuk satire penutup."""
    mb = W.MB(name)
    mb.box(-w / 2 - 1, -d / 2 - 2.4, 0, w / 2 + 1, d / 2 + 1, .5, "court")
    mb.box(-w / 2 - .6, -d / 2 - 1.9, .5, w / 2 + .6, d / 2 + .6, .9, "court")
    mb.box(-w / 2, -d / 2 + .8, .9, w / 2, d / 2, 7.0, "court")
    for k in range(6):
        x = -w / 2 + 1.2 + k * (w - 2.4) / 5
        mb.cyl(x, -d / 2 - .8, .9, 6.6, .42, "c_white", n=12)
        mb.box(x - .55, -d / 2 - 1.35, 6.5, x + .55, -d / 2 - .25, 6.9, "c_white")
    mb.box(-w / 2 - .3, -d / 2 - 1.6, 6.9, w / 2 + .3, d / 2 + .2, 7.6, "court")
    mb.prism_x([(-d / 2 - 1.6, 7.6), (d / 2 + .2, 7.6), (d / 2 * 0 - .6, 10.0)], -w / 2 - .3, w / 2 + .3, "court_roof")
    mb.box(-1.2, -d / 2 + .75, .9, 1.2, -d / 2 + .85, 4.0, "court_dk")
    return mb


def scales_icon(name, loc, s=1.0):
    """timbangan keadilan emas."""
    mb = W.MB(name)
    mb.cyl(0, 0, 0, .15 * s, .7 * s, "brass", n=12)
    mb.cyl(0, 0, .15 * s, 2.4 * s, .08 * s, "brass", n=8)
    mb.box(-1.4 * s, -.05 * s, 2.3 * s, 1.4 * s, .05 * s, 2.42 * s, "brass")
    for sx in (-1, 1):
        mb.box(sx * 1.3 * s - .02, -.02, 1.4 * s, sx * 1.3 * s + .02, .02, 2.3 * s, "brass")
        mb.cyl(sx * 1.3 * s, 0, 1.3 * s, 1.42 * s, .5 * s, "brass", n=12, r_top=.55 * s)
    mb.sphere(0, 0, 2.55 * s, .16 * s, "brass")
    return mb.build(loc)


def xmark(name, loc, s=1.0, key="xred"):
    """tanda silang merah tebal (berdiri menghadap -Y)."""
    mb = W.MB(name)
    for a in (math.pi / 4, -math.pi / 4):
        c, si = math.cos(a), math.sin(a)
        L_, t = 1.0 * s, .22 * s
        pts = [(-L_ * c - t * si, -L_ * si + t * c), (L_ * c - t * si, L_ * si + t * c),
               (L_ * c + t * si, L_ * si - t * c), (-L_ * c + t * si, -L_ * si - t * c)]
        mb.prism_y(pts, -.1 * s, .1 * s, key)
    ob = mb.build(loc)
    ob.data.materials[0] = lp.mat(key, emission=.6)
    return ob


def checkmark(name, loc, s=1.0, key="check"):
    """centang hijau tebal (berdiri menghadap -Y)."""
    mb = W.MB(name)
    t = .2 * s
    for (p0, p1) in (((-.8 * s, .05 * s), (-.25 * s, -.5 * s)), ((-.25 * s, -.5 * s), (.9 * s, .75 * s))):
        dx, dz = p1[0] - p0[0], p1[1] - p0[1]
        n = math.hypot(dx, dz)
        nx, nz = -dz / n * t, dx / n * t
        e0 = (p0[0] - dx / n * t * .9, p0[1] - dz / n * t * .9)
        mb.prism_y([(e0[0] + nx, e0[1] + nz), (p1[0] + nx, p1[1] + nz), (p1[0] - nx, p1[1] - nz),
                    (e0[0] - nx, e0[1] - nz)], -.1 * s, .1 * s, key)
    ob = mb.build(loc)
    ob.data.materials[0] = lp.mat(key, emission=.6)
    return ob


def price_tag(name, body, loc, s=1.0, key="lw_yellow"):
    """label harga 3D (papan + lubang tali) dengan teks menghadap -Y."""
    mb = W.MB(name)
    w = .32 * s * len(body) + .5 * s
    mb.prism_y([(-w / 2, -.45 * s), (w / 2, -.45 * s), (w / 2 + .35 * s, 0), (w / 2, .45 * s), (-w / 2, .45 * s)],
               -.06 * s, .06 * s, key)
    mb.disc_y(w / 2 + .05 * s, -.07 * s, 0, .1 * s, .02 * s, "lw_frame", n=10)
    ob = mb.build(loc)
    t = H.text(name + "_t", body, .5 * s, "lw_navy", depth=.04 * s, loc=(0, -.08 * s, -.22 * s))
    t.parent = ob
    return ob


def money_note(mb, x, y, z, s=1.0, key="money_g"):
    mb.box(x - .6 * s, y - .3 * s, z, x + .6 * s, y + .3 * s, z + .025 * s, key)
    mb.box(x - .18 * s, y - .18 * s, z + .025 * s, x + .18 * s, y + .18 * s, z + .03 * s, "money_g2")


def money_stack(name, n=6, s=1.0):
    mb = W.MB(name)
    for k in range(n):
        money_note(mb, (k % 2) * .05, 0, k * .05 * s, s, "money_g" if k % 2 else "money_g2")
    mb.box(-.12 * s, -.31 * s, 0, .12 * s, .31 * s, n * .05 * s + .01, "money_band")
    return mb


def report_doc(name, s=1.0):
    """papan klip 'laporan keuangan' (berdiri, menghadap -Y): kertas, baris angka, grafik batang, cap BERSIH."""
    mb = W.MB(name)
    rbox(mb, -1.1 * s, -.06 * s, 0, 1.1 * s, .06 * s, 3.0 * s, "lw_wood", c=.1)
    mb.box(-.95 * s, -.09 * s, .15 * s, .95 * s, -.06 * s, 2.7 * s, "paper_w")
    mb.box(-.35 * s, -.12 * s, 2.75 * s, .35 * s, -.04 * s, 3.05 * s, "metal")
    for k in range(5):
        z = 2.1 * s - k * .22 * s
        mb.box(-.8 * s, -.1 * s, z, (.1 + .1 * (k % 3)) * s, -.09 * s, z + .08 * s, "paper_l")
        mb.box(.45 * s, -.1 * s, z, .8 * s, -.09 * s, z + .08 * s, "lw_teal")
    for k, hh in enumerate((.25, .4, .5, .7)):
        mb.box((-.75 + k * .3) * s, -.11 * s, .35 * s, (-.55 + k * .3) * s, -.09 * s, (.35 + hh) * s, "chart2")
    return mb


def phone_feed(name, s=1.0):
    """HP besar berdiri dengan kartu-kartu berita (menghadap -Y). Teks ditambahkan terpisah."""
    mb = W.MB(name)
    rbox(mb, -1.3 * s, -.12 * s, 0, 1.3 * s, .12 * s, 5.2 * s, "phone_blk", c=.25)
    mb.box(-1.15 * s, -.14 * s, .25 * s, 1.15 * s, -.12 * s, 4.95 * s, "kiosk_scr")
    for k in range(3):
        z = 3.5 * s - k * 1.3 * s
        mb.box(-1.0 * s, -.16 * s, z, 1.0 * s, -.14 * s, z + 1.1 * s, "c_white")
        if k == 0:                                   # kartu berita utama: strip merah (teks ditambah terpisah)
            mb.box(-1.0 * s, -.17 * s, z + .78 * s, 1.0 * s, -.16 * s, z + 1.1 * s, "news_red")
            continue
        mb.box(-.9 * s, -.17 * s, z + .1 * s, -.25 * s, -.16 * s, z + 1.0 * s, ("news_red", "c_grey", "c_grey")[k])
        for j in range(3):
            mb.box(-.15 * s, -.17 * s, z + .75 * s - j * .25 * s, (.85 - .2 * j) * s, -.16 * s, z + .85 * s - j * .25 * s,
                   "paper_l")
    return mb


def balloons(mb, x, y, z, s=1.0):
    for k, (dx, dz, c) in enumerate(((-.4, 0, "balloon1"), (.35, .3, "balloon2"), (0, .7, "balloon3"))):
        mb.box(x + dx * .3 - .01, y - .01, z, x + dx * .3 + .01, y + .01, z + (2.0 + dz) * s, "metal")
        ball(mb, x + dx * s, y, z + (2.3 + dz) * s, .35 * s, c, seg=10, rings=6, sz=.42 * s)


# ------------------------------------------------------------------ dunia
LAUNDRY_C = (0.0, -6.0)
KOS_C = (0.0, -47.0)                # menghadap +y (ke jalan, ke arah laundry)
KOS2_C = (-46.0, -8.0)              # menghadap +x
APT_C = (47.0, -6.0)                # menghadap -x
CAMPUS_C = (-46.0, 47.0)            # menghadap -y
OFFICE_C = (47.0, 47.0)             # menghadap -y
OFFICE2_C = (47.0, 30.0)


BRANCHES = [(0.0, 42.0, "-y"), (50.0, -47.0, "+y"), (-47.0, 12.0, "+x")]


def build_world(seed=5, people=True, laundry_visible=True, opening=False, branches=False):
    """kota diorama dengan laundry koin di blok tengah, dikelilingi kos, apartemen, kampus, kantor."""
    rnd = random.Random(seed)
    info = {"anchors": {}, "people": [], "walkers": []}
    W.PLACED.clear()
    W.build_ground()
    props = W.MB("props")
    trees = W.MB("trees")
    A = info["anchors"]

    if laundry_visible:
        mb, top = laundromat("laundry")
        info["laundry"] = mb.build((*LAUNDRY_C, 0), 0)
        info["sign"] = laundromat_sign("ls", (*LAUNDRY_C, 0), "-y")
    A["LAUNDRY"] = (LAUNDRY_C[0], LAUNDRY_C[1] - LD / 2, Z + LH1 + 3.6 + 3.5)
    A["LAUNDRY_DOOR"] = (LAUNDRY_C[0], LAUNDRY_C[1] - LD / 2 - 1, Z + 2.5)
    reserved = [(-15.5, -15.5, 15.5, 15.5)]
    # halaman belakang laundry: parkir motor + pohon
    for x in (-12.5, 12.5):
        W.tree_round(trees, x, 6, 1.0, rnd)
        W.tree_round(trees, x, -12, .8, rnd)
    props.box(-7, 2, Z, 7, 12, Z + .04, "asphalt")
    for k in range(6):
        x = -5.5 + k * 2.2
        props.box(x - .15, 8.2, Z + .05, x + .15, 10, Z + .85, ("red_aw", "tv", "laundry_aw", "tv", "c_coral", "tv")[k])
        props.box(x - .17, 8.8, Z + .85, x + .17, 9.6, Z + 1.0, "tv")

    for (nm, fn, c, fc, label) in (("kos", kos, KOS_C, "+y", "KOS"), ("kos2", kos, KOS2_C, "+x", "KOS2"),
                                   ("apt", apartment, APT_C, "-x", "APARTEMEN"),
                                   ("campus", campus, CAMPUS_C, "-y", "KAMPUS")):
        ob, top = W.place(fn(nm), c[0], c[1], fc)
        A[label] = (c[0], c[1], top + 1)
        info[nm] = ob
        reserved.append((c[0] - 14, c[1] - 9, c[0] + 14, c[1] + 9) if nm == "campus" else
                        (c[0] - 9.5, c[1] - 9.5, c[0] + 9.5, c[1] + 9.5))
        if nm.startswith("kos"):
            info[nm + "_sign"] = kos_sign(nm, (*c, 0), fc)
    info["branches"] = []
    for k, (bx, by, fc) in enumerate(BRANCHES):
        reserved.append((bx - 9, by - 9, bx + 9, by + 9))
        if branches:
            mb, top = laundromat(f"br{k}")
            ob = mb.build((bx, by, 0), W.FACING[fc])
            sg = laundromat_sign(f"br{k}", (bx, by, 0), fc)
            info["branches"].append((ob, sg, (bx, by, top)))
    for (nm, c, fl) in (("office", OFFICE_C, 10), ("office2", OFFICE2_C, 7)):
        ob, top = W.place(H.office_tower(nm, 12.0, 10.0, fl), c[0], c[1], "-y" if nm == "office" else "-x")
        info[nm] = ob
        A["KANTOR" if nm == "office" else "KANTOR2"] = (c[0], c[1], top + 1)
        reserved.append((c[0] - 8, c[1] - 7, c[0] + 8, c[1] + 7))

    # taman barat-daya
    pb = W.inner((-W.L, -W.L, W.ROADS[0] - W.RW / 2, W.ROADS[0] - W.RW / 2))
    reserved.append(pb)
    px, py = (pb[0] + pb[2]) / 2, (pb[1] + pb[3]) / 2
    props.box(pb[0] + 2, py - 1.2, Z, pb[2] - 2, py + 1.2, Z + .03, "path")
    props.box(px - 1.2, pb[1] + 2, Z, px + 1.2, pb[3] - 2, Z + .03, "path")
    for q in range(22):
        x = rnd.uniform(pb[0] + 3, pb[2] - 3)
        y = rnd.uniform(pb[1] + 3, pb[3] - 3)
        if abs(x - px) < 3 or abs(y - py) < 3:
            continue
        if rnd.random() < .45:
            W.tree_conifer(trees, x, y, rnd.uniform(.8, 1.15))
        else:
            W.tree_round(trees, x, y, rnd.uniform(.8, 1.2), rnd)

    # kavling lain
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
    if opening:
        fy = LAUNDRY_C[1] - LD / 2
        for x in (-6.2, 6.2):
            balloons(props, x, fy - 3.4, Z + .1, 1.0)
    props.build()
    trees.build()

    if people:
        prnd = random.Random(seed + 1)
        for k in range(14):
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
            parts = character(f"ped{k}", WALKERS[k % len(WALKERS)], loc, rot)
            info["people"].append((parts["body"], horiz, sp))
            info["walkers"].append(parts)
    return info


def animate_walkers(info, n):
    """pejalan kaki: geser lokasi (world.animate_people) + ayunan kaki."""
    W.animate_people(info, n)
    for parts in info["walkers"]:
        walk_cycle(parts, 1, n, period=20, amp=.5)
