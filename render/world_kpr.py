"""Kota diorama BESAR untuk video KPR (melayang di dunia neon, konsep 2 dunia):
  - Perumahan cluster "GRIYA ASRI" (barat daya): gerbang, tembok keliling, 3 deret rumah tipe sama (carport,
    pagar, pohon), jalan lingkungan, kantor pemasaran + spanduk KPR, motor/mobil, warga.
  - Pusat kota (utara): menara BANK INDONESIA (putih, sirip vertikal, tulisan besar di mahkota) + gedung klasik
    berpilar + plaza tiang bendera, dikelilingi gedung kantor kaca.
  - Jalan perbankan (tenggara): deret ruko/cabang bank + ATM + papan kurs LED raksasa di plaza.
  - Boulevard + avenue dengan lalu lintas, pohon & lampu jalan.
Semua permukaan atas = G0. Kembalikan dict titik penting untuk kamera & objek adegan."""
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
X0, Y0, X1, Y1 = -92.0, -72.0, 92.0, 62.0
BLV = (-4.0, 6.0)          # boulevard (sumbu x): y0..y1
AVE = (8.0, 16.0)          # avenue (sumbu y): x0..x1
ROWS_Y = (-18.0, -37.0, -56.0)              # pusat deret rumah (muka menghadap -y ke jalan lingkungan)
STREETS_Y = (-25.5, -44.5, -63.5)
HOUSE_XS = (-82.0, -73.5, -65.0, -56.5, -48.0, -31.0, -22.5, -14.0, -5.5)
SPINE_X = (-43.0, -36.0)                   # jalan poros perumahan (dari gerbang ke selatan)
BI_C = (-20.0, 40.0)
KURS_C = (48.0, -12.0)

lp.PAL.update({
    "kp_fence": "#ECE6DA", "kp_gate": "#2F6B45", "kp_gate2": "#E9DFC8", "kp_carport": "#4A5263", "kp_wall": "#D9D2C3",
    "bi_white": "#F4F4F0", "bi_fin": "#D5DAE2", "bi_glass": "#7FA6CF", "bi_base": "#C9CDD4", "bank_blue": "#1F4FD1",
    "bank_navy": "#13235C", "atm": "#E5E9F0", "kp_pole": "#2B2F38", "kp_lamp": "#FFE6A8", "kp_spine": "#3A3F4A",
})


def _text(name, body, loc, size, key="tee", em=0.0, rot=(math.pi / 2, 0, 0), depth=.12):
    return H.text(name, body, size, key, depth=depth, loc=loc, rot=rot, emission=em)


# ------------------------------------------------------------------ dasar diorama + jalan
def base_plate():
    g = W.MB("kp_ground")
    g.box(X0, Y0, -.3, X1, Y1, 0, "pk_ground")
    g.box(X0, Y0, -3.6, X1, Y1, -.3, "dio_soil")
    for z in (-1.3, -2.5):
        g.box(X0 - .02, Y0 - .02, z - .2, X1 + .02, Y1 + .02, z, "dio_soil2")
    g.box(X0 + .5, Y0 + .5, -4.6, X1 - .5, Y1 - .5, -3.6, "dio_base")
    g.box(X0, Y0, 0, X1, Y1, G0 - .02, "pk_grass")
    # boulevard & avenue
    g.box(X0, BLV[0], G0 - .02, X1, BLV[1], G0, "pk_asph")
    g.box(AVE[0], Y0, G0 - .02, AVE[1], Y1, G0, "pk_asph")
    for xx in range(int(X0), int(X1), 7):
        if not (AVE[0] - 1 < xx < AVE[1] + 1):
            g.box(xx, (BLV[0] + BLV[1]) / 2 - .12, G0, xx + 3.5, (BLV[0] + BLV[1]) / 2 + .12, G0 + .015, "pk_line")
    for yy in range(int(Y0), int(Y1), 7):
        if not (BLV[0] - 1 < yy < BLV[1] + 1):
            g.box((AVE[0] + AVE[1]) / 2 - .12, yy, G0, (AVE[0] + AVE[1]) / 2 + .12, yy + 3.5, G0 + .015, "pk_line")
    for yy in (BLV[0] - 2.2, BLV[1]):                     # trotoar boulevard
        g.box(X0, yy, G0 - .02, X1, yy + 2.2, G0 + .12, "pk_walk")
    for xx in (AVE[0] - 2.2, AVE[1]):
        g.box(xx, Y0, G0 - .02, xx + 2.2, Y1, G0 + .12, "pk_walk")
    g.build()
    # neon di kaki diorama + tiang cahaya + panggung neon di bawah
    rim = W.MB("kp_rim")
    t = .14
    for (ax, ay, bx, by) in ((X0, Y0, X1, Y0), (X0, Y1, X1, Y1), (X0, Y0, X0, Y1), (X1, Y0, X1, Y1)):
        rim.box(min(ax, bx) - t, min(ay, by) - t, -3.7, max(ax, bx) + t, max(ay, by) + t, -3.5, "n_pink")
    V.glow(rim.build(), {"n_pink": 6.0})
    for k, (bx, by) in enumerate(((X0, Y0), (X1, Y0), (X0, Y1), (X1, Y1))):
        mb_ = W.MB(f"kp_beam{k}")
        mb_.box(bx - .2, by - .2, -14, bx + .2, by + .2, -4.6, "n_cyan")
        V.glow(mb_.build(), {"n_cyan": 5.0})
    st = V.stage(center=(0, -5), size=320, sp=5.0, grid_em=2.2, fade=(90, 300), dome_r=480, dome_h=560)
    for ob in st.values():
        ob.location.z = -14.0


# ------------------------------------------------------------------ perumahan KPR
def kpr_house(name, x, y, seed, wall, roof):
    """rumah tipe 36 kompleks: rumah + carport beratap + pagar depan + pohon kecil. Muka menghadap -y."""
    rnd = random.Random(seed)
    mb, h = T.house(name, 6.2, 6.4, rnd, wall, roof)
    ob = mb.build((x, y, G0 - T.Z))
    ex = W.MB(name + "_ex")
    ex.box(-4.8, -6.6, G0 - .02, 4.2, 3.4, G0 + .04, "pk_walk")              # halaman + carport
    for px in (3.25, 4.15):
        ex.box(px - .08, -5.6, G0, px + .08, -5.44, G0 + 2.5, "kp_carport")
    ex.box(3.1, -5.7, G0 + 2.5, 4.3, -.8, G0 + 2.62, "kp_carport")
    ex.box(-4.8, -6.7, G0, -1.0, -6.55, G0 + 1.0, "kp_fence")                 # pagar depan
    ex.box(1.0, -6.7, G0, 2.9, -6.55, G0 + 1.0, "kp_fence")
    for xx in (-4.8, -1.0, 1.0, 2.9):
        ex.box(xx - .12, -6.75, G0, xx + .12, -6.5, G0 + 1.25, "kp_wall")
    C.street_tree(ex, -3.9, -5.4, .55, rnd)
    eo = ex.build((x, y, 0))
    _ = eo
    return ob, h - T.Z + G0


def perumahan(n_frames, seed=3):
    rnd = random.Random(seed)
    out = {"houses": {}, "people": []}
    px0, px1, py0, py1 = -88.0, 2.0, -70.0, -9.0
    g = W.MB("kp_estate")
    g.box(px0, py0, G0 - .015, px1, py1, G0 + .005, "pk_grass")
    for sy in STREETS_Y:                                      # jalan lingkungan
        g.box(px0 + 1, sy - 2.2, G0 - .01, px1 - 1, sy + 2.2, G0 + .01, "pk_asph")
        g.box(px0 + 1, sy - 2.5, G0 - .01, px1 - 1, sy - 2.2, G0 + .1, "pk_curb")
    g.box(SPINE_X[0], py0 + 1, G0 - .01, SPINE_X[1], py1, G0 + .012, "pk_asph")
    # tembok keliling (rendah) dengan bukaan gerbang
    gx0, gx1 = SPINE_X[0] - 1.5, SPINE_X[1] + 1.5
    for (a, b, c, d) in ((px0, py1 - .4, gx0, py1), (gx1, py1 - .4, px1, py1), (px0, py0, px1, py0 + .4),
                         (px0, py0, px0 + .4, py1), (px1 - .4, py0, px1, py1)):
        g.box(a, b, G0, c, d, G0 + 1.8, "kp_wall")
    g.build()
    # gerbang cluster dengan nama perumahan (terbaca dari boulevard)
    gt = W.MB("kp_gatearch")
    for xx in (gx0 - .8, gx1 + .8):
        gt.box(xx - .8, py1 - 1.0, G0, xx + .8, py1 + .6, G0 + 7.2, "kp_gate2")
    gt.box(gx0 - 1.8, py1 - .8, G0 + 6.0, gx1 + 1.8, py1 + .4, G0 + 8.4, "kp_gate")
    gt.build()
    _text("kp_gatetx", "GRIYA ASRI", ((gx0 + gx1) / 2, py1 - .9, G0 + 6.55), 1.25, "tee", 2.5)
    out["gate"] = ((gx0 + gx1) / 2, py1, G0 + 7.2)
    walls = ("wall_cream2", "wall_peach", "wall_beige", "laundry_wall")
    roofs = ("roof_orange", "roof_brown")
    k = 0
    for r, y in enumerate(ROWS_Y):
        for c, x in enumerate(HOUSE_XS):
            if r == 0 and c == 5:                               # kantor pemasaran di dekat gerbang
                continue
            ob, top = kpr_house(f"rm{r}_{c}", x, y, seed + k, walls[(r + c) % 4], roofs[(r * 3 + c) % 2])
            out["houses"][(r, c)] = (ob, (x, y), top)
            k += 1
    # kantor pemasaran + spanduk KPR
    mx, my = HOUSE_XS[5], ROWS_Y[0]
    mo = W.MB("kp_market")
    mo.box(mx - 3.6, my - 3.0, G0, mx + 3.6, my + 3.2, G0 + 4.0, "ct_white")
    mo.box(mx - 3.4, my - 3.08, G0 + .3, mx + 3.4, my - 3.0, G0 + 3.2, "ct_glass")
    mo.box(mx - 4.0, my - 4.2, G0 + 4.0, mx + 4.0, my + 3.6, G0 + 4.35, "kp_gate")
    mo.build()
    for i, (img, dx) in enumerate((("bn_kpr", -2.6), ("bn_rumah", 2.6))):
        pole = W.MB(f"kp_bnp{i}")
        pole.box(mx + dx - 1.9, my - 5.8, G0, mx + dx - 1.78, my - 5.66, G0 + 4.6, "kp_pole")
        pole.box(mx + dx + 1.78, my - 5.8, G0, mx + dx + 1.9, my - 5.66, G0 + 4.6, "kp_pole")
        pole.build()
        me = G._quad_mesh(f"kp_bn{i}", 3.6, 1.55)
        me.materials.append(G.img_mat(img, 1.1, False, False))
        bo = bpy.data.objects.new(f"kp_bn{i}", me)
        lp._link(bo)
        bo.location = (mx + dx, my - 5.85, G0 + 2.9)
    out["market"] = (mx, my)
    # kendaraan & warga di jalan lingkungan
    for i in range(8):
        sy = STREETS_Y[i % 3]
        R.motor(f"kp_mt{i}", (rnd.choice(HOUSE_XS) + 3.7, sy + 4.4, G0), math.radians(90), rnd.choice(R.BIKE_COLS), .8)
    for i in range(5):
        R.car(f"kp_car{i}", (rnd.choice(HOUSE_XS) + 3.7, ROWS_Y[i % 3] - 3.4, G0), math.radians(90),
              R.CAR_COLS[i % len(R.CAR_COLS)], .8)
    looks = ("bapak", "hijab", "cowok", "cewek", "mahasiswa", "hijab2")
    for i in range(9):
        sy = STREETS_Y[i % 3]
        p = L.character(f"kp_w{i}", looks[i % len(looks)], (rnd.uniform(-84, -2), sy + rnd.uniform(-1.4, 1.4), G0),
                        rnd.uniform(-1.2, 1.2))
        out["people"].append(p)
    return out


# ------------------------------------------------------------------ pusat kota + Bank Indonesia
def bi_complex():
    cx, cy = BI_C
    out = {}
    tw = W.MB("bi_tower")
    tw.box(cx - 9, cy - 4, G0, cx + 9, cy + 10, G0 + 50, "bi_white")
    for k in range(13):                                       # sirip vertikal muka depan
        x = cx - 8.4 + k * 1.4
        tw.box(x - .18, cy - 4.5, G0 + 8, x + .18, cy - 4.0, G0 + 46, "bi_fin")
    for z in range(10, 46, 4):
        tw.box(cx - 8.6, cy - 4.2, G0 + z, cx + 8.6, cy - 4.05, G0 + z + 2.6, "bi_glass")
    tw.box(cx - 9.6, cy - 4.6, G0 + 46, cx + 9.6, cy + 10.6, G0 + 51.5, "bi_white")   # mahkota
    tw.box(cx - 10, cy - 5, G0, cx + 10, cy + 11, G0 + 8, "bi_base")                   # podium
    tw.build()
    _text("bi_tx", "BANK INDONESIA", (cx, cy - 4.7, G0 + 47.6), 2.0, "bank_navy", 0.0, depth=.25)
    out["crown"] = (cx, cy - 5, G0 + 49)
    # gedung klasik berpilar di depan + plaza bendera
    mb, hh = H.gov_office("bi_old", 22.0, 10.0)
    ob = mb.build((cx, cy - 16, G0 - H.Z))
    out["old"] = (cx, cy - 16, hh)
    _text("bi_tx2", "BANK INDONESIA", (cx, cy - 21.3, G0 + 7.6), .9, "bank_navy", 0.0)
    pz = W.MB("bi_plaza")
    pz.box(cx - 14, cy - 30, G0 - .01, cx + 14, cy - 22, G0 + .06, "tw_plaza")
    for i, x in enumerate((cx - 6, cx, cx + 6)):
        pz.box(x - .1, cy - 26, G0, x + .1, cy - 25.8, G0 + 11, "kp_pole")
        pz.box(x + .1, cy - 26, G0 + 9.6, x + 2.6, cy - 25.95, G0 + 10.3, "flag_red")
        pz.box(x + .1, cy - 26, G0 + 8.9, x + 2.6, cy - 25.95, G0 + 9.6, "tee")
    pz.build()
    out["plaza"] = (cx, cy - 26)
    return out


def cbd(seed=5):
    rnd = random.Random(seed)
    b = W.MB("cbd")
    spots = [(x, y) for x in (22, 34, 46, 58, 70, 82) for y in (20, 34, 48)] + \
            [(x, y) for x in (-86, -74, -62, -50) for y in (16, 30, 44)] + [(4, 30), (-4, 54), (2, 44)]
    for (x, y) in spots:
        w, d = rnd.uniform(7, 10), rnd.uniform(7, 10)
        h = rnd.uniform(12, 38) if abs(x - BI_C[0]) > 16 else rnd.uniform(8, 16)
        b.box(x - w / 2, y - d / 2, G0, x + w / 2, y + d / 2, G0 + h,
              rnd.choice(("ct_glass", "ct_glass2", "ct_glass3", "ct_con", "ct_white")))
        b.box(x - w / 2 - .2, y - d / 2 - .2, G0 + h, x + w / 2 + .2, y + d / 2 + .2, G0 + h + .5, "ct_con")
    b.build()


# ------------------------------------------------------------------ jalan perbankan + papan kurs
def bank_street(seed=7):
    rnd = random.Random(seed)
    out = {"banks": []}
    st = W.MB("bk_street")
    st.box(20, -46.5, G0 - .01, 90, -40.0, G0 + .01, "pk_asph")
    st.box(20, -40.0, G0 - .01, 90, -36.0, G0 + .1, "pk_walk")
    st.build()
    b = W.MB("bk_row")
    R.ruko(b, 22, 90, -36, 11, rnd)
    R.ruko(b, 22, 90, -66, 10, rnd)
    b.build()
    for i, x in enumerate((28, 46, 64, 82)):                    # papan nama cabang bank
        sg = W.MB(f"bk_sg{i}")
        sg.box(x - 4.4, -36.6, G0 + 6.4, x + 4.4, -36.2, G0 + 8.0, "bank_blue")
        V.glow(sg.build(), {"bank_blue": 1.6})
        _text(f"bk_tx{i}", "BANK", (x, -36.7, G0 + 6.75), .95, "tee", 2.0)
        at = W.MB(f"bk_atm{i}")
        at.box(x + 4.8, -38.2, G0, x + 6.2, -37.0, G0 + 2.4, "atm")
        at.box(x + 4.9, -38.25, G0 + 1.3, x + 6.1, -38.2, G0 + 2.0, "bank_blue")
        at.build()
        out["banks"].append((x, -36))
    # plaza + papan kurs LED raksasa
    kx, ky = KURS_C
    pz = W.MB("kurs_plaza")
    pz.box(kx - 16, ky - 4, G0 - .01, kx + 16, ky + 6, G0 + .06, "tw_plaza")
    for xx in (kx - 9.5, kx + 9.5):
        pz.box(xx - .5, ky - .5, G0, xx + .5, ky + .5, G0 + 15, "kp_pole")
    pz.box(kx - 10.4, ky - .7, G0 + 4.8, kx + 10.4, ky + .6, G0 + 16.2, "kp_pole")
    pz.build()
    me = G._quad_mesh("kurs_led", 20.0, 11.25)
    me.materials.append(G.img_mat("kurs", 2.2, False, False))
    ko = bpy.data.objects.new("kurs_led", me)
    lp._link(ko)
    ko.location = (kx, ky + .75, G0 + 4.95)
    ko.rotation_euler.z = math.pi                         # menghadap boulevard (+y)
    out["kurs"] = (kx, ky, G0 + 10.5)
    return out


# ------------------------------------------------------------------ pohon, lampu, lalu lintas
def street_dressing(n_frames, seed=9):
    rnd = random.Random(seed)
    tr = W.MB("kp_trees")
    for xx in range(int(X0) + 3, int(X1) - 2, 9):
        if not (AVE[0] - 3 < xx < AVE[1] + 3) and not (KURS_C[0] - 22 < xx < KURS_C[0] + 22):
            for yy in (BLV[0] - 1.2, BLV[1] + 1.2):
                C.street_tree(tr, xx, yy, 1.0, rnd)
    for yy in range(int(Y0) + 3, int(Y1) - 2, 9):
        if not (BLV[0] - 3 < yy < BLV[1] + 3):
            for xx in (AVE[0] - 1.2, AVE[1] + 1.2):
                C.street_tree(tr, xx, yy, 1.0, rnd)
    for x in HOUSE_XS:
        for sy in STREETS_Y:
            pass
    tr.build()
    lamps = W.MB("kp_lamps")
    for xx in range(int(X0) + 7, int(X1), 14):
        lamps.box(xx - .08, BLV[0] - 2.0, G0, xx + .08, BLV[0] - 1.84, G0 + 5.2, "kp_pole")
        lamps.box(xx - .3, BLV[0] - 2.1, G0 + 5.1, xx + .3, BLV[0] - 1.1, G0 + 5.3, "kp_lamp")
    V.glow(lamps.build(), {"kp_lamp": 3.0})
    cars = []
    for k in range(10):
        lane = BLV[0] + 2.2 if k % 2 == 0 else BLV[1] - 2.2
        dirn = 1 if k % 2 == 0 else -1
        cr = R.car(f"kp_tc{k}", (0, lane, G0), 0 if dirn > 0 else math.pi, R.CAR_COLS[k % len(R.CAR_COLS)], .9)
        xs = rnd.uniform(X0 + 8, X1 - 8)
        for fk in (1, n_frames):
            x = xs + dirn * 7.0 * (fk - 1) / 30
            while x > X1 - 3:
                x -= (X1 - X0 - 6)
            while x < X0 + 3:
                x += (X1 - X0 - 6)
            cr.location.x = x
            cr.keyframe_insert("location", frame=fk)
        cars.append(cr)
    for k in range(6):
        lanex = AVE[0] + 2.0 if k % 2 == 0 else AVE[1] - 2.0
        dirn = 1 if k % 2 else -1
        cr = R.car(f"kp_av{k}", (lanex, 0, G0), math.pi / 2 if dirn > 0 else -math.pi / 2,
                   R.CAR_COLS[(k + 3) % len(R.CAR_COLS)], .9)
        ys = rnd.uniform(Y0 + 8, Y1 - 8)
        for fk in (1, n_frames):
            cr.location.y = max(Y0 + 3, min(Y1 - 3, ys + dirn * 6.0 * (fk - 1) / 30))
            cr.keyframe_insert("location", frame=fk)
        cars.append(cr)
    return cars


def city_kpr(n_frames, seed=3):
    """bangun seluruh kota. Return dict titik penting."""
    V.setup_day_light()
    base_plate()
    info = {"estate": perumahan(n_frames, seed), "bi": bi_complex(), "bank": bank_street()}
    cbd()
    info["cars"] = street_dressing(n_frames)
    sc = bpy.context.scene
    for bg in sc.world.node_tree.nodes:
        if bg.type == "BACKGROUND" and bg.name == "Background":
            bg.inputs["Color"].default_value = lp.hex_rgba("#2A1840")
            bg.inputs["Strength"].default_value = .8
    return info
