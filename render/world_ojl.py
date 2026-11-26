"""Kota metropolitan diorama BESAR untuk video "Ojol & GoTo" (melayang di dunia neon, konsep 2 dunia).
Kawasan:
  - Pusat bisnis (timur laut): gedung kantor rapat + MENARA GoTo (kaca gelap, sirip hijau, logo goto menyala di
    mahkota, papan gojek di lobi, plaza).
  - Barat laut: mal + gedung kantor + papan LED.
  - Tengah: pangkalan ojol di pojok perempatan (halte + minimarket + belasan driver jaket hijau & motor), deret
    warung/kuliner tempat driver antar-makanan menunggu.
  - Selatan: kampung padat (rumah-rumah kecil) + gang.
  - 2 boulevard + 2 avenue penuh lalu lintas: mobil + banyak ojol jaket hijau yang melaju.
Semua permukaan atas = G0. Return dict titik penting untuk kamera & objek adegan."""
import math
import os
import random
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowpoly as lp  # noqa: E402
import world as W  # noqa: E402
import world_ctd as C  # noqa: E402
import world_gta as G  # noqa: E402
import world_hotel as H  # noqa: E402
import world_laundry as L  # noqa: E402
import world_prk as R  # noqa: E402
import world_tahu as T  # noqa: E402
import world_vap as V  # noqa: E402

G0 = .30
X0, Y0, X1, Y1 = -124.0, -96.0, 124.0, 84.0
BLV = ((-4.0, 6.0), (-52.0, -44.0))          # boulevard (sumbu x)
AVE = ((-6.0, 4.0), (58.0, 66.0))            # avenue (sumbu y)
GOTO_C = (30.0, 34.0)                        # menara GoTo
BASE_C = (-14.0, -10.0)                      # pangkalan ojol (pojok barat daya perempatan utama)
FOOD = (10.0, 54.0, -40.0, -8.0)             # deret kuliner x0, x1, y0, y1

lp.PAL.update({
    "ojl_green": "#00AA13", "ojl_green2": "#0B7A1E", "ojl_helm": "#08A62E", "ojl_dark": "#0E2A1A",
    "goto_glass": "#21443A", "goto_fin": "#1FD14E", "goto_white": "#F3F6F4", "shelter": "#2D3440",
    "shelter_roof": "#0B7A1E", "stall1": "#F4C542", "stall2": "#E8563B", "stall3": "#3B82F6", "food_box": "#00AA13",
    "kp_pole": "#2B2F38", "kp_lamp": "#FFE6A8", "mall": "#E9E4DA", "mall_glass": "#6FA3D8",
})

# karakter driver ojol (jaket hijau, helm hijau)
L.LOOKS["ojol"] = dict(skin="skin2", top="ojl_green", sleeve="ojl_green", bottom="c_black", shoe="shoe_dk", hair="cap",
                       hair_col="ojl_helm", acc=())
L.LOOKS["ojol2"] = dict(skin="skin3", top="ojl_green", sleeve="ojl_green", bottom="c_navy", shoe="shoe_dk",
                        hair="cap", hair_col="ojl_green2", acc=())


def _text(name, body, loc, size, key="tee", em=0.0, rot=(math.pi / 2, 0, 0), depth=.12):
    return H.text(name, body, size, key, depth=depth, loc=loc, rot=rot, emission=em)


def _img_plane(name, img, w, loc, rot_z=0.0, em=1.2, h=None):
    iw, ih = G.img_size(img)
    h = h or w * ih / iw
    me = G._quad_mesh(name, w, h)
    me.materials.append(G.img_mat(img, em, True, False))
    ob = bpy.data.objects.new(name, me)
    lp._link(ob)
    ob.location = loc
    ob.rotation_euler.z = rot_z
    return ob


def ojol_rider(name, loc, rot_z=0.0, s=.8, color=None):
    """motor + pengendara jaket & helm hijau (motor menghadap +X lokal)."""
    rnd = random.Random(name)
    return R.rider_motor(name, loc, rot_z, color or rnd.choice(R.BIKE_COLS), "ojl_green", "ojl_helm", s)


def ojol_driver(name, loc, rot=0.0, pose=None, phone=False, look="ojol"):
    p = L.character(name, look, loc, rot, hold="phone" if phone else None)
    if pose:
        L.pose(p, pose)
    return p


# ------------------------------------------------------------------ dasar diorama + jalan
def base_plate():
    g = W.MB("oj_ground")
    g.box(X0, Y0, -.3, X1, Y1, 0, "pk_ground")
    g.box(X0, Y0, -3.8, X1, Y1, -.3, "dio_soil")
    for z in (-1.4, -2.7):
        g.box(X0 - .02, Y0 - .02, z - .2, X1 + .02, Y1 + .02, z, "dio_soil2")
    g.box(X0 + .5, Y0 + .5, -4.8, X1 - .5, Y1 - .5, -3.8, "dio_base")
    g.box(X0, Y0, 0, X1, Y1, G0 - .02, "pk_grass")
    for (b0, b1) in BLV:
        g.box(X0, b0, G0 - .02, X1, b1, G0, "pk_asph")
        for xx in range(int(X0), int(X1), 7):
            g.box(xx, (b0 + b1) / 2 - .12, G0, xx + 3.5, (b0 + b1) / 2 + .12, G0 + .015, "pk_line")
        g.box(X0, b0 - 2.4, G0 - .02, X1, b0, G0 + .12, "pk_walk")
        g.box(X0, b1, G0 - .02, X1, b1 + 2.4, G0 + .12, "pk_walk")
    for (a0, a1) in AVE:
        g.box(a0, Y0, G0 - .015, a1, Y1, G0 + .005, "pk_asph")
        for yy in range(int(Y0), int(Y1), 7):
            g.box((a0 + a1) / 2 - .12, yy, G0 + .005, (a0 + a1) / 2 + .12, yy + 3.5, G0 + .02, "pk_line")
        g.box(a0 - 2.4, Y0, G0 - .02, a0, Y1, G0 + .12, "pk_walk")
        g.box(a1, Y0, G0 - .02, a1 + 2.4, Y1, G0 + .12, "pk_walk")
    # zebra cross di perempatan utama
    for k in range(8):
        x = AVE[0][0] - 6 + k * .9
        g.box(x, BLV[0][0] - 2.2, G0 + .01, x + .45, BLV[0][0] - .2, G0 + .025, "pk_line")
    g.build()
    rim = W.MB("oj_rim")
    t = .16
    for (ax, ay, bx, by) in ((X0, Y0, X1, Y0), (X0, Y1, X1, Y1), (X0, Y0, X0, Y1), (X1, Y0, X1, Y1)):
        rim.box(min(ax, bx) - t, min(ay, by) - t, -3.9, max(ax, bx) + t, max(ay, by) + t, -3.7, "n_cyan")
    V.glow(rim.build(), {"n_cyan": 6.0})
    for k, (bx, by) in enumerate(((X0, Y0), (X1, Y0), (X0, Y1), (X1, Y1))):
        mb_ = W.MB(f"oj_beam{k}")
        mb_.box(bx - .25, by - .25, -16, bx + .25, by + .25, -4.8, "n_pink")
        V.glow(mb_.build(), {"n_pink": 5.0})
    st = V.stage(center=(0, -5), size=420, sp=6.0, grid_em=2.2, fade=(120, 380), dome_r=600, dome_h=700)
    for ob in st.values():
        ob.location.z = -16.0


# ------------------------------------------------------------------ menara GoTo
def goto_tower():
    cx, cy = GOTO_C
    out = {}
    tw = W.MB("goto_tower")
    tw.box(cx - 9, cy - 8, G0, cx + 9, cy + 8, G0 + 62, "goto_glass")
    for k in range(10):                                   # sirip hijau vertikal muka depan
        x = cx - 8.1 + k * 1.8
        tw.box(x - .15, cy - 8.5, G0 + 9, x + .15, cy - 8.0, G0 + 58, "goto_fin")
    for z in range(12, 58, 6):
        tw.box(cx - 9.1, cy - 8.15, G0 + z, cx + 9.1, cy - 8.05, G0 + z + .35, "goto_fin")
    tw.box(cx - 9.6, cy - 8.6, G0 + 58, cx + 9.6, cy + 8.6, G0 + 66, "goto_glass")   # mahkota
    tw.box(cx - 12, cy - 11, G0, cx + 12, cy + 10, G0 + 9, "goto_white")             # podium lobi
    tw.box(cx - 3.5, cy - 11.1, G0, cx + 3.5, cy - 11.0, G0 + 5, "ct_glass")
    to = tw.build()
    V.glow(to, {"goto_fin": 2.6})
    out["logo"] = _img_plane("goto_logo", "goto_logo", 16.0, (cx, cy - 8.7, G0 + 58.8), 0.0, 2.6, 6.66)
    out["gojek"] = _img_plane("gojek_sign", "gojek", 14.0, (cx, cy - 11.15, G0 + 6.1), 0.0, 2.0, 4.0)
    pz = W.MB("goto_plaza")
    pz.box(cx - 16, cy - 24, G0 - .01, cx + 16, cy - 11, G0 + .06, "tw_plaza")
    pz.build()
    out["crown"] = (cx, cy - 9, G0 + 62)
    out["lobby"] = (cx, cy - 12, G0)
    return out


def cbd(seed=5):
    rnd = random.Random(seed)
    b = W.MB("oj_cbd")
    spots = [(x, y) for x in (10, 22, 46, 76, 88, 100, 112) for y in (16, 30, 44, 60, 74)] + \
            [(x, y) for x in (-114, -102, -90, -78, -66, -54, -42, -30, -18) for y in (16, 30, 44, 60, 74)]
    for (x, y) in spots:
        if abs(x - GOTO_C[0]) < 15 and abs(y - GOTO_C[1]) < 14:
            continue
        if -70 < x < -40 and 14 < y < 34:                      # tempat mal
            continue
        w, d = rnd.uniform(7, 10), rnd.uniform(7, 10)
        h = rnd.uniform(14, 46) if y > 24 else rnd.uniform(9, 22)
        b.box(x - w / 2, y - d / 2, G0, x + w / 2, y + d / 2, G0 + h,
              rnd.choice(("ct_glass", "ct_glass2", "ct_glass3", "ct_con", "ct_white")))
        b.box(x - w / 2 - .2, y - d / 2 - .2, G0 + h, x + w / 2 + .2, y + d / 2 + .2, G0 + h + .5, "ct_con")
        for z in range(4, int(h) - 2, 4):                      # garis lantai supaya tidak polos
            b.box(x - w / 2 - .05, y - d / 2 - .05, G0 + z, x + w / 2 + .05, y - d / 2, G0 + z + .25, "ct_con")
    b.build()
    # mal + papan LED
    m = W.MB("oj_mall")
    m.box(-68, 14, G0, -42, 32, G0 + 14, "mall")
    m.box(-67.5, 13.9, G0 + 1, -42.5, 14.0, G0 + 12.5, "mall_glass")
    m.build()
    _text("mall_tx", "MAL KOTA", (-55, 13.8, G0 + 12.0), 1.6, "ojl_dark", 0.0)


# ------------------------------------------------------------------ pangkalan ojol + minimarket
def pangkalan(seed=11):
    bx, by = BASE_C
    rnd = random.Random(seed)
    out = {"drivers": [], "bikes": []}
    sh = W.MB("oj_shelter")
    for xx in (bx - 6, bx + 6):
        for yy in (by - 2.5, by + 2.5):
            sh.box(xx - .12, yy - .12, G0, xx + .12, yy + .12, G0 + 3.0, "shelter")
    sh.box(bx - 6.6, by - 3.0, G0 + 3.0, bx + 6.6, by + 3.0, G0 + 3.3, "shelter_roof")
    sh.box(bx - 4.5, by - 2.2, G0, bx + 4.5, by - 1.6, G0 + .5, "shelter")               # bangku (belakang)
    sh.box(bx - 7, by - 3.5, G0 - .01, bx + 7, by + 4.6, G0 + .05, "pk_walk")
    so = sh.build()
    V.glow(so, {"shelter_roof": .6})
    _text("oj_shtx", "PANGKALAN OJOL", (bx, by + 3.05, G0 + 3.12), .5, "tee", 2.0, rot=(math.pi / 2, 0, math.pi))
    mb, top = H.minimarket("oj_mini", 12.0, 9.0)
    mb.build((bx - 15, by - 2, G0 - H.Z))
    # motor parkir berjajar + driver
    for i in range(7):
        x = bx - 6 + i * 2.0
        R.motor(f"oj_pk{i}", (x, by + 3.9, G0), math.radians(-90), rnd.choice(R.BIKE_COLS), .78)
    poses = ("stand", "think", "sit", "stand", "point", "sit", "stand", "wave", "stand")
    for i in range(9):
        x = bx - 5.5 + i * 1.35
        y = by + (-1.9 if poses[i] == "sit" else rnd.uniform(-.6, 1.8))
        d = ojol_driver(f"oj_dr{i}", (x, y, G0 + (.5 if poses[i] == "sit" else 0)), math.pi + rnd.uniform(-.5, .5), poses[i],
                        phone=(i % 3 == 1), look="ojol" if i % 2 else "ojol2")
        out["drivers"].append(d)
    out["center"] = (bx, by)
    return out


# ------------------------------------------------------------------ deret kuliner (antar makanan)
def food_street(seed=13):
    x0, x1, y0, y1 = FOOD
    rnd = random.Random(seed)
    out = {"stalls": []}
    b = W.MB("oj_food")
    n = 6
    w = (x1 - x0) / n
    for row, (ya, face) in enumerate(((y1 - 1, -1), (y0 + 9, -1))):
        for i in range(n):
            xa = x0 + i * w + .4
            col = ("stall1", "stall2", "stall3")[(i + row) % 3]
            b.box(xa, ya - 7, G0, xa + w - .8, ya, G0 + 4.2, rnd.choice(("rk1", "rk2", "rk3", "rk4")))
            b.box(xa + .5, ya - 7.05, G0 + .2, xa + w - 1.3, ya - 7.0, G0 + 2.8, "rk_shut")
            b.prism_x([(ya - 8.6, 3.1), (ya - 7, 3.1), (ya - 7, 3.9)], xa, xa + w - .8, col)
            b.box(xa + .6, ya - 8.0, G0, xa + w - 1.4, ya - 7.4, G0 + 1.0, "c_white")     # meja etalase
            out["stalls"].append((xa + (w - .8) / 2, ya - 8.6))
    b.build()
    for i, (sx, sy) in enumerate(out["stalls"][:6]):
        if i % 2 == 0:
            ojol_rider(f"oj_fr{i}", (sx - 1.2, sy - 1.6, G0), 0.0, .8)
            bx = W.MB(f"oj_fb{i}")
            bx.box(sx - 1.75, sy - 1.95, G0 + 1.05, sx - .85, sy - 1.25, G0 + 1.75, "food_box")
            bx.build()
    return out


# ------------------------------------------------------------------ kampung padat
def kampung(seed=17):
    rnd = random.Random(seed)
    walls = ("wall_cream2", "wall_peach", "wall_beige", "laundry_wall")
    roofs = ("roof_orange", "roof_brown")
    k = 0
    for y in range(-90, -56, 9):
        for x in range(-118, 120, 8):
            if AVE[0][0] - 3 < x < AVE[0][1] + 3 or AVE[1][0] - 3 < x < AVE[1][1] + 3:
                continue
            if rnd.random() < .12:
                continue
            mb, h = T.house(f"kp{k}", rnd.uniform(5.2, 6.4), rnd.uniform(5.4, 6.4), rnd, rnd.choice(walls),
                            rnd.choice(roofs))
            mb.build((x + rnd.uniform(-.5, .5), y + rnd.uniform(-.5, .5), G0 - T.Z))
            k += 1
    # deret ruko di tepi boulevard selatan
    b = W.MB("oj_ruko")
    R.ruko(b, -118, -10, -42 + 2.6, 9, rnd)
    R.ruko(b, 70, 120, -42 + 2.6, 9, rnd)
    b.build()


# ------------------------------------------------------------------ pohon, lampu, lalu lintas
def dressing(n_frames, seed=9, riders=40):
    rnd = random.Random(seed)
    tr = W.MB("oj_trees")
    for (b0, b1) in BLV:
        for xx in range(int(X0) + 4, int(X1) - 2, 10):
            if any(a0 - 3 < xx < a1 + 3 for a0, a1 in AVE):
                continue
            for yy in (b0 - 1.3, b1 + 1.3):
                C.street_tree(tr, xx, yy, 1.0, rnd)
    tr.build()
    lamps = W.MB("oj_lamps")
    for (b0, b1) in BLV:
        for xx in range(int(X0) + 8, int(X1), 16):
            lamps.box(xx - .08, b0 - 2.1, G0, xx + .08, b0 - 1.94, G0 + 5.4, "kp_pole")
            lamps.box(xx - .3, b0 - 2.2, G0 + 5.3, xx + .3, b0 - 1.1, G0 + 5.5, "kp_lamp")
    V.glow(lamps.build(), {"kp_lamp": 3.0})
    movers = []

    def lane_anim(ob, axis, start, dirn, speed, lo, hi):
        for fk in (1, n_frames):
            v = start + dirn * speed * (fk - 1) / 30
            span = hi - lo
            while v > hi:
                v -= span
            while v < lo:
                v += span
            setattr(ob.location, axis, v)
            ob.keyframe_insert("location", frame=fk)

    for bi, (b0, b1) in enumerate(BLV):
        for k in range(14):
            east = k % 2 == 0
            lane = b0 + (1.4 if east else (b1 - b0) - 1.4) + rnd.uniform(-.3, .3)
            if k % 3 == 0:
                ob = R.car(f"oj_c{bi}_{k}", (0, lane, G0), 0 if east else math.pi, rnd.choice(R.CAR_COLS), .9)
                sp = rnd.uniform(6, 8)
            else:
                ob = ojol_rider(f"oj_r{bi}_{k}", (0, lane, G0), 0 if east else math.pi, .8)
                sp = rnd.uniform(7, 10)
            lane_anim(ob, "x", rnd.uniform(X0 + 6, X1 - 6), 1 if east else -1, sp, X0 + 4, X1 - 4)
            movers.append(ob)
    for ai, (a0, a1) in enumerate(AVE):
        for k in range(10):
            north = k % 2 == 0
            lanex = a0 + (1.4 if north else (a1 - a0) - 1.4)
            rot = math.pi / 2 if north else -math.pi / 2
            if k % 3 == 0:
                ob = R.car(f"oj_ca{ai}_{k}", (lanex, 0, G0), rot, rnd.choice(R.CAR_COLS), .9)
            else:
                ob = ojol_rider(f"oj_ra{ai}_{k}", (lanex, 0, G0), rot, .8)
            lane_anim(ob, "y", rnd.uniform(Y0 + 6, Y1 - 6), 1 if north else -1, rnd.uniform(6, 9), Y0 + 4, Y1 - 4)
            movers.append(ob)
    return movers


def city_ojl(n_frames, seed=3):
    V.setup_day_light()
    base_plate()
    info = {"goto": goto_tower(), "base": pangkalan(), "food": food_street()}
    cbd()
    kampung()
    info["movers"] = dressing(n_frames)
    sc = bpy.context.scene
    for bg in sc.world.node_tree.nodes:
        if bg.type == "BACKGROUND" and bg.name == "Background":
            bg.inputs["Color"].default_value = lp.hex_rgba("#1B1838")
            bg.inputs["Strength"].default_value = .8
    return info
