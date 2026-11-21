"""Adegan "Persib Part 2: mesin uang Persib" (Bedah Bisnis, dokumenter).
Alur: YouTube 2,5 jt subscriber tapi iklan kecil -> uang besar dari mana? -> 5 pintu brankas: liga (subsidi
Rp19 M -> Rp27 M), hak siar & bonus peringkat -> bobotoh di stadion -> 4 kompetisi, 24 laga kandang, tiket,
jersey PO, 7 toko resmi, membership -> Asia (ACL Two: menang di Seoul & vs Cong Viettel) -> insiden: denda AFC
US$200 rb + 2 laga tanpa penonton -> follower jadi uang (corong) -> valuasi Rp1 triliun -> CTA.
Sudut kamera sengaja bervariasi per adegan (depan, kanan, atas, rendah, orbit, geser lateral, crane).

  PSB_TEX=DIR python3 render/scenes_ps2.py -- --scene Q01 --out DIR [--res 864x1536] [--samples 4] [--frames a-b]
"""
import math
import os
import random
import sys

import bpy  # noqa: F401

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lowpoly as lp  # noqa: E402
import world_psb as P  # noqa: E402   (sebelum world_fom: set G.TEX)
import world_ps2 as Q  # noqa: E402
import world_fom as F  # noqa: E402
import world_gta as G  # noqa: E402
import world_pst as PS  # noqa: E402
import world_vap as V  # noqa: E402
import scenes_nkh as K  # noqa: E402
import scenes_vap as SV  # noqa: E402
from scenes_nkh import FPS, TAIL, anim, arc_move, key, pop_in, pop_out  # noqa: E402

TIMELINE = [("Q01", 0.00), ("Q02", 3.05), ("Q03", 7.40), ("Q04", 9.60), ("Q05", 11.70), ("Q06", 17.85),
            ("Q07", 20.45), ("Q08", 24.90), ("Q09", 29.35), ("Q10", 36.15), ("Q11", 41.00), ("Q12", 45.50),
            ("Q13", 49.05), ("Q14", 55.05), ("Q15", 58.90), ("Q16", 61.65), ("Q17", 69.65), ("Q18", 77.85),
            ("Q19", 84.85)]
END_T = 93.4
CITY = set()
STADIUM = {"Q07", "Q16"}
K.TIMELINE, K.END_T, K.CITY = TIMELINE, END_T, CITY


def _night(world_str=.3):
    """langit malam biru tua (dua node Background: cahaya & yang terlihat kamera)."""
    sc = bpy.context.scene
    for ob in list(bpy.data.objects):
        if ob.type == "LIGHT" and ob.data.type == "SUN":
            ob.data.energy = .35
            ob.data.color = (.7, .8, 1.0)
            ob.rotation_euler = (math.radians(55), 0, math.radians(-30))
    for bg in sc.world.node_tree.nodes:
        if bg.type == "BACKGROUND":
            bg.inputs["Color"].default_value = lp.hex_rgba("#081226")
            bg.inputs["Strength"].default_value = world_str
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.cycles.glossy_bounces = 2
    sc.cycles.max_bounces = 4


V.setup_neon_light = lambda *a, **k: _night()
_coin0 = P.coin


def _coin(name, loc, s=1.0):
    """koin emas sedikit berpendar (supaya tidak tampak cokelat kusam di panggung gelap)."""
    ob = _coin0(name, loc, s)
    V.glow(ob, {"coin_g": .9})
    return ob


P.coin = _coin


def fr(sid, t):
    return K.fr(sid, t)


def camera(sid, keys, **kw):
    return K.camera(sid, keys, **kw)


def n_all(n):
    return n + TAIL


def stage(**kw):
    kw.setdefault("grid", "psb_grid")
    kw.setdefault("em", 1.4)
    return K.neon(**kw)


def sign(name, body, loc, size=.8, key_="n_white", em=6.0, frame=True):
    return V.neon_sign(name, body, loc, size, key_, em, frame)


def pop_pair(pair, f, s=1.0, dur=8):
    for ob in pair:
        if ob is not None:
            pop_in(ob, f, s, dur)


def out_pair(pair, f, dur=7):
    for ob in pair:
        if ob is not None:
            pop_out(ob, f, dur)


def phone(name, img, h, loc, rot_z, sid, t_pop, n, span=.45, t_scroll=None):
    p = F.article_phone(name, img, h, loc, rot_z,
                        scroll=[(1, 0.0), (fr(sid, t_scroll or t_pop + .5), 0.0), (n_all(n), span)])
    pop_in(p["root"], fr(sid, t_pop), 1.0, 12)
    return p


def float_bob(ob, f0, f1, amp=.2, period=70, phase=0.0):
    z0 = ob.location.z
    for f in range(f0, f1 + 1, 2):
        key(ob, "location", f, (ob.location.x, ob.location.y, z0 + amp * math.sin(2 * math.pi * f / period + phase)))


def coin_burst(prefix, sid, t, n, src, spread=4.0, seed=1, dz=-1.0, s=1.0, dur=14, y_land=None):
    """koin melompat dari src lalu jatuh ke lantai di sekitar."""
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        f0 = fr(sid, t + .05 * i)
        c = P.coin(f"{prefix}{i}", src, s)
        p1 = (src[0] + rnd.uniform(-spread, spread), (y_land if y_land is not None else src[1]) + rnd.uniform(-1.5, 1.5),
              .1)
        arc_move(c, f0, f0 + dur, src, p1, 1.4, "lin")
        key(c, "scale", 1, (.001,) * 3)
        key(c, "scale", f0 - 1, (.001,) * 3)
        key(c, "scale", f0, (s, s, s))
        c.rotation_euler = (rnd.uniform(0, 3), rnd.uniform(0, 3), 0)
        out.append(c)
    return out


def open_door(d, f0, f1, deg=-105):
    key(d["door"], "rotation_euler", 1, (0, 0, 0))
    key(d["door"], "rotation_euler", f0, (0, 0, 0))
    anim(d["door"], "rotation_euler", f0, f1, (0, 0, 0), (0, 0, math.radians(deg)), "out")


DOORS = [("LEAGUE", "n_gold"), ("TICKETS", "n_cyan"), ("JERSEY", "n_cyan"), ("MEMBERS", "n_cyan"), ("ASIA", "n_gold")]


def door_row(prefix, y=0.0, gap=4.6):
    out = []
    for i, (lab, k_) in enumerate(DOORS):
        x = (i - 2) * gap
        ang = math.radians(-(i - 2) * 9)                 # sedikit melengkung menghadap kamera
        out.append(Q.vault_door(f"{prefix}{i}", (x, y + abs(i - 2) * .9, 0), 3.0, 4.8, lab, k_, ang, .46))
    return out


# ================================================================== HOOK: YouTube
def q01(n, A):
    """Channel YouTube Persib punya >2 juta subscriber: HP raksasa berisi tangkapan channel asli (2,54 jt) +
    tombol play 3D melayang; kamera sudut rendah naik (crane) ke depan."""
    sid = "Q01"
    stage(rig_c=(0, 0, 3.5), rig_s=1.6, fade=(12, 56))
    yt = phone("yt", "art_yt", 10.0, (-1.2, 1.4, .1), .1, sid, 0.05, n, .22, 1.2)
    bt = Q.yt_button("ytb", .8, (3.4, -.6, 7.0))
    bt.rotation_euler.z = math.radians(-18)
    pop_in(bt, fr(sid, .2), 1.0, 12)
    float_bob(bt, fr(sid, .4), n_all(n), .25, 60)
    SV.spin(bt, fr(sid, .2), n_all(n), 25)
    pt = P.photo("ptv", "ph_ptv", 3.4, (-6.4, 3.0, .3), .4, em=.85, border=.08)
    pop_in(pt, fr(sid, 1.0), 1.0, 12)
    rnd = random.Random(3)
    for i in range(14):                               # ikon subscriber beterbangan naik
        f0 = fr(sid, 1.5 + .06 * i)
        fo = Q.follower(f"fl{i}", (0, 0, 0), .5, "fol_blue" if i % 3 else "yt_red")
        x0 = rnd.uniform(-5.5, 4.5)
        arc_move(fo, f0, f0 + 30, (x0, 3.2, .2), (x0 * .5 + 3.0, 3.0 + rnd.uniform(0, 1.5), 9.0 + rnd.uniform(0, 2.5)),
                 .6, "out")
        key(fo, "scale", 1, (.001,) * 3)
        key(fo, "scale", f0 - 1, (.001,) * 3)
        key(fo, "scale", f0 + 4, (1, 1, 1))
        key(fo, "scale", f0 + 26, (1, 1, 1))
        key(fo, "scale", f0 + 32, (.001,) * 3)
    camera(sid, [(0.0, (1.0, 0, 3.6), -58, 2, 13), (1.6, (.8, 0, 4.4), -78, 7, 16.5),
                 (3.05, (.6, 0, 4.8), -96, 10, 20)], lens=24)
    A["YT"] = (yt["root"], (0, 0, 10.6))
    A["BT"] = (bt, (0, 0, 3.4))


def q02(n, A):
    """Tapi iklannya cuma ±US$2,7 rb/bulan: tombol YouTube raksasa vs tumpukan koin mungil + kaca pembesar;
    kamera dari atas-kanan turun ke koin. Tangkapan vidIQ (estimasi)."""
    sid = "Q02"
    stage(rig_c=(0, 0, 2.5), rig_s=1.5, fade=(12, 56))
    bt = Q.yt_button("ytb", 1.35, (-3.0, 3.0, .2))
    pop_in(bt, fr(sid, 3.1), 1.0, 10)
    V.disc_ped("ped", 1.6, "psb_blue2", (3.0, -1.0, 0), em=4.0, h=.35)
    cs = []
    for i in range(3):
        c = P.coin(f"c{i}", (2.45 + i * .55, -1.0, .88), .9)          # berdiri menghadap kamera (jelas koin)
        c.rotation_euler = (0, 0, math.radians(-24))
        pop_in(c, fr(sid, 5.5 + .12 * i), .9, 8)
        cs.append(c)
    mg = V.magnifier("mg", (4.6, -2.4, 1.4), 1.0)
    pop_in(mg, fr(sid, 5.9), 1.0, 12)
    arc_move(mg, fr(sid, 5.9), fr(sid, 6.9), (6.0, -3.2, 2.6), (4.2, -2.4, 1.3), .5, "out")
    vq = phone("vq", "art_vidiq", 7.2, (-8.8, 4.6, .1), .45, sid, 4.0, n, .25)
    camera(sid, [(3.05, (-.5, 1.0, 2.0), -38, 52, 26), (5.2, (1.4, 0, .2), -52, 36, 19),
                 (7.40, (2.8, -1.2, -1.2), -66, 22, 13.5)], lens=26)
    A["VQ"] = (vq["root"], (0, 0, 7.6))
    A["CN"] = (cs[-1], (0, 0, .5))


def q03(n, A):
    """Terus uang besarnya dari mana? Pintu brankas raksasa tertutup + tanda tanya; kamera orbit dari kanan."""
    sid = "Q03"
    stage(rig_c=(0, 0, 3.5), rig_s=1.6, fade=(12, 56))
    d = Q.vault_door("vd", (0, 1.0, 0), 4.6, 7.0, None, "n_gold", 0.0, .9)
    pop_in(d["root"], fr(sid, 7.45), 1.0, 12)
    qm = V.qmark("qm", (0, -1.6, 7.4), 1.3, "n_gold", 7.0)
    pop_in(qm, fr(sid, 8.6), 1.0, 10)
    SV.spin(qm, fr(sid, 8.6), n_all(n), 40)
    rnd = random.Random(5)
    for i in range(10):
        side = -1 if i % 2 else 1
        c = P.coin(f"c{i}", (side * rnd.uniform(3.4, 6.5), rnd.uniform(-3, 2), rnd.uniform(1.5, 8.0)), .7)
        c.rotation_euler = (math.radians(90) + rnd.uniform(-.4, .4), 0, rnd.uniform(-.6, .6))
        pop_in(c, fr(sid, 8.5 + .04 * i), .7, 10)
        float_bob(c, fr(sid, 8.5), n_all(n), .3, 50, i)
    camera(sid, [(7.40, (0, 0, 3.8), 12, 8, 20), (8.6, (0, 0, 4.0), -40, 10, 19),
                 (9.60, (0, 0, 4.0), -70, 9, 18)], lens=26)


def q04(n, A):
    """Pintu pertama: liga. Lima pintu brankas berlabel; pintu LEAGUE terbuka di kata 'door', cahaya keluar;
    kamera dari kanan-atas lalu mendorong masuk ke pintu pertama."""
    sid = "Q04"
    stage(rig_c=(0, 0, 3.5), rig_s=1.8, fade=(14, 60))
    ds = door_row("d", 1.0)
    for i, d in enumerate(ds):
        pop_in(d["root"], fr(sid, 9.62 + .07 * i), 1.0, 10)
    open_door(ds[0], fr(sid, 10.32), fr(sid, 11.0))
    camera(sid, [(9.60, (0, 1, 3.4), -52, 20, 30), (10.5, (-5.5, 1, 3.0), -70, 12, 20),
                 (11.70, (-8.6, 1.4, 2.8), -84, 6, 12.5)], lens=24)


def q05(n, A):
    """Musim ini tiap klub dapat ±US$1,6 jt (Rp27 M) dari operator, naik dari US$1,1 jt (Rp19 M): logo Super
    League, 18 koin klub, 2 pilar naik; artikel Bola.com. Kamera rendah dari kanan, lalu ke kiri-depan."""
    sid = "Q05"
    stage(rig_c=(0, 0, 3.5), rig_s=1.6, fade=(12, 56))
    lg = P.logo_card("lg", "lg_bri", 3.2, (0, 4.5, 6.4), 0.0, plate="plate_w", em=1.1)
    pop_in(lg, fr(sid, 11.8), 1.0, 12)
    rnd = random.Random(2)
    for i in range(18):                                # 18 klub = 18 koin sama besar
        a = math.pi * (.15 + .7 * i / 17)
        c = P.coin(f"k{i}", (7.2 * math.cos(a), 2.4 - 3.6 * math.sin(a) + 3.6, .25), .8)
        c.rotation_euler = (math.radians(90), 0, a + math.pi / 2)
        pop_in(c, fr(sid, 12.73 + .03 * i), .8, 8)
    p1 = V.pillar("p19", 3.2, 2.0, 2.0, "n_cyan", 1.2, 5.0, (-2.0, 0, 0))
    p2 = V.pillar("p27", 4.6, 2.0, 2.0, "n_gold", 1.4, 6.0, (2.0, 0, 0))
    for p, t in ((p1, 16.6), (p2, 13.8)):
        key(p, "scale", 1, (1, 1, .001))
        key(p, "scale", fr(sid, t) - 1, (1, 1, .001))
        anim(p, "scale", fr(sid, t), fr(sid, t + .7), (1, 1, .001), (1, 1, 1), "out")
    t1, t1f = sign("t19", "Rp19 M", (-2.0, -1.2, 3.85), .42, "n_cyan", 6.0)
    t2, t2f = sign("t27", "Rp27 M", (2.0, -1.2, 5.25), .5, "n_gold", 7.0)
    pop_pair((t1, t1f), fr(sid, 17.0))
    pop_pair((t2, t2f), fr(sid, 14.4))
    y1 = Q.text3d("y1", "2025/26", (-2.0, -1.05, .35), .34, "psb_white", 3.0)
    y2 = Q.text3d("y2", "2026/27", (2.0, -1.05, .35), .34, "psb_white", 3.0)
    pop_in(y1, fr(sid, 16.6), 1.0, 8)
    pop_in(y2, fr(sid, 13.8), 1.0, 8)
    ar = phone("ar", "art_subsidi", 7.0, (-8.2, 3.6, .1), .42, sid, 15.3, n, .3)
    camera(sid, [(11.70, (0, 1, 3.4), -26, 4, 20), (14.2, (0, 1, 3.4), -62, 7, 19),
                 (16.3, (0, .5, 3.2), -100, 8, 18), (17.85, (-.5, .5, 3.2), -118, 9, 18.5)], lens=26)
    A["AR"] = (ar["root"], (0, 0, 7.4))


def q06(n, A):
    """...belum termasuk hak siar TV & bonus peringkat: TV siaran (foto laga) + podium 1-2-3 dengan koin;
    kamera dari atas (top-down) turun ke depan-kanan."""
    sid = "Q06"
    stage(rig_c=(0, 0, 3), rig_s=1.5, fade=(12, 56))
    tvo = Q.tv("tv", "ph_seoul", 7.2, (-3.0, 1.5, 0), .25)
    pop_in(tvo["root"], fr(sid, 18.55), 1.0, 12)
    pd = Q.podium("pd", (4.2, 0, 0), 1.0)
    pop_in(pd["root"], fr(sid, 19.3), 1.0, 12)
    for i, (x, hh) in enumerate(((4.2, 2.4), (1.9, 1.6), (6.5, 1.1))):
        c = P.coin(f"pc{i}", (x, 0, hh + .55), 1.0)
        c.rotation_euler = (math.radians(90), 0, 0)
        pop_in(c, fr(sid, 19.66 + .1 * i), 1.0, 8)
        SV.spin(c, fr(sid, 19.66), n_all(n), 180)
    s1, s1f = sign("s1", "TV RIGHTS", (-3.0, .9, 7.4), .5, "n_cyan", 7.0)
    s2, s2f = sign("s2", "RANKING BONUS", (4.2, -1.2, 4.6), .42, "n_gold", 7.0)
    pop_pair((s1, s1f), fr(sid, 18.62))
    pop_pair((s2, s2f), fr(sid, 19.4))
    camera(sid, [(17.85, (.5, 0, 1.5), -90, 74, 24), (19.2, (.6, 0, 2.6), -72, 40, 21),
                 (20.45, (.8, 0, 3.2), -60, 14, 20)], lens=24)


# ================================================================== BOBOTOH
def q07(n, A):
    """Semua klub dapat itu. Yang beda: bobotoh. Stadion malam penuh, 18 koin klub di lapangan lalu hilang,
    logo Persib naik, kamera berputar dari kanan ke tribun bobotoh + suar biru."""
    sid = "Q07"
    st = P.stadium()
    P.crowd_jump(st["fans"], 1, n_all(n), .16, 12)
    for i in range(18):
        a = 2 * math.pi * i / 18
        c = P.coin(f"k{i}", (5.2 * math.cos(a), 4.0 * math.sin(a), .5), 1.1)
        c.rotation_euler = (math.radians(90), 0, a)
        pop_in(c, fr(sid, 20.6 + .02 * i), 1.1, 8)
        pop_out(c, fr(sid, 21.9 + .015 * i), 7)
    V.disc_ped("lp", 2.4, "psb_blue2", (0, 0, .08), em=5.0, h=.3)
    lg = P.logo_card("lg", "lg_persib", 4.6, (0, 0, .4), 0.0, plate=None, em=1.4)
    anim(lg, "location", fr(sid, 22.2), fr(sid, 22.9), (0, 0, -5.0), (0, 0, .4), "out")
    pop_in(lg, fr(sid, 22.2), 1.0, 10)
    SV.spin(lg, fr(sid, 22.9), n_all(n), 30)
    P.flares("fl", 30, (-24, 9, 24, 16), 6.2, 7)
    camera(sid, [(20.45, (0, 0, 2.2), 24, 22, 26), (22.3, (0, 0, 3.0), -20, 12, 19),
                 (23.6, (0, 3, 5.0), -55, 10, 17.5), (24.90, (0, 8, 7.0), -72, 12, 17.5)], lens=24)
    A["LG"] = (lg, (0, 0, 5.4))


def q08(n, A):
    """Musim ini 4 kompetisi, minimal 24 laga kandang: logo Persib muncul dulu, lalu 4 logo kompetisi berjajar
    di atas, grid kalender 24 ubin menyala satu per satu; kamera tinggi dari kiri-depan lalu turun ke kanan."""
    sid = "Q08"
    stage(rig_c=(0, 0, 3.5), rig_s=1.6, fade=(12, 56))
    V.disc_ped("ped", 2.2, "psb_blue2", (0, -1.2, 0), em=4.5, h=.35)
    pl = P.logo_card("pl", "lg_persib", 3.4, (0, -1.2, .4), 0.0, plate=None, em=1.35)
    pop_in(pl, fr(sid, 24.95), 1.0, 10)
    out_pair((pl,), fr(sid, 27.35), 8)
    for i, im in enumerate(("lg_bri", "lg_ileague_cup", "lg_shopee", "lg_acl2")):
        lc = P.logo_card(f"lg{i}", im, 1.9, ((i - 1.5) * 2.7, 1.6, 6.9), 0.0, plate="plate_w", em=1.1, pad=.25)
        pop_in(lc, fr(sid, 26.44 + .09 * i), 1.0, 10)
    tiles = Q.cal_grid("cal", 24, 6, (0, 1.5, .4), 1.05, .2)
    for i, tl in enumerate(tiles):
        pop_in(tl, fr(sid, 27.6 + .03 * i), 1.0, 7)
    hs, hsf = sign("hm", "HOME MATCHES", (0, .9, 6.05), .36, "n_cyan", 7.0)
    pop_pair((hs, hsf), fr(sid, 28.45))
    camera(sid, [(24.90, (0, 0, 2.4), -124, 26, 19), (26.6, (0, .5, 4.2), -104, 14, 22),
                 (28.2, (0, 1, 4.2), -84, 8, 22.5), (29.35, (0, 1, 4.2), -72, 8, 22)], lens=26)
    A["CAL"] = (tiles[2], (0, 0, 1.4))


def q09(n, A):
    """Kalau tiap laga 14-20 rb penonton -> tiket ±US$2,7-5 jt semusim: foto GBLA di belakang, 3 gerbang tiket,
    tiket mengalir masuk, tumpukan koin naik; artikel GoodStats (penonton). Kamera rendah dari kanan lalu naik."""
    sid = "Q09"
    stage(rig_c=(0, 0, 3), rig_s=1.6, fade=(12, 56))
    bg = P.photo("gb", "ph_gbla_full", 7.0, (0, 6.5, .3), 0.0, em=.8, border=.1)
    pop_in(bg, fr(sid, 29.4), 1.0, 12)
    gates = []
    for i, x in enumerate((-3.6, 0, 3.6)):
        g = Q.turnstile(f"g{i}", (x, 0, 0), 1.2)
        pop_in(g["root"], fr(sid, 29.5 + .08 * i), 1.0, 10)
        gates.append(g)
    rnd = random.Random(7)
    for i in range(18):                               # tiket mengalir lewat gerbang
        x = (-3.6, 0, 3.6)[i % 3]
        tk = PS.ticket(f"tk{i}", "PERSIB", "psb_blue", "psb_navy", .38, "TIKET")
        f0 = fr(sid, 30.4 + .16 * i)
        arc_move(tk, f0, f0 + 22, (x, -6.0, 1.8), (x + rnd.uniform(-.4, .4), 4.5, 2.4), .4, "lin")
        key(tk, "scale", 1, (.001,) * 3)
        key(tk, "scale", f0 - 1, (.001,) * 3)
        key(tk, "scale", f0 + 3, (1, 1, 1))
        key(tk, "scale", f0 + 18, (1, 1, 1))
        key(tk, "scale", f0 + 22, (.001,) * 3)
    for g in gates:
        for k in range(6):
            f = fr(sid, 30.6 + .5 * k)
            key(g["arm"], "rotation_euler", f, (0, 0, 0))
            key(g["arm"], "rotation_euler", f + 6, (0, 0, math.radians(90)))
            key(g["arm"], "rotation_euler", f + 12, (0, 0, math.radians(180)))
    for i in range(12):                               # koin bertumpuk naik di depan
        c = P.coin(f"st{i}", (6.6, -2.2, .2 + i * .17), 1.0)
        pop_in(c, fr(sid, 32.6 + .2 * i), 1.0, 6)
    ap = phone("ap", "art_penonton", 6.6, (-7.8, 3.0, .1), .45, sid, 30.2, n, .3)
    camera(sid, [(29.35, (0, -1, 1.8), -18, 3, 15), (31.6, (.5, 0, 2.6), -44, 8, 17),
                 (34.0, (1.5, 0, 3.4), -66, 18, 21), (36.15, (2.0, 0, 3.6), -78, 24, 23)], lens=24)
    A["AP"] = (ap["root"], (0, 0, 7.0))
    A["GT"] = (gates[1]["root"], (0, 0, 2.6))


def q10(n, A):
    """Jersey: PO pertama kabarnya ±US$400-600 rb (Rp7-10 M): jersey 3D di podium + foto 'Edankeun di Asia' &
    'Lives Inside Us', tag harga Rp1,19 jt, artikel Bola.com. Kamera orbit ±200 derajat."""
    sid = "Q10"
    stage(rig_c=(0, 0, 3.5), rig_s=1.6, fade=(12, 56))
    V.disc_ped("jp", 2.6, "psb_blue2", (0, 0, 0), em=4.5, h=.5)
    js = P.jersey("js", (0, 0, .6), 1.35)
    pop_in(js, fr(sid, 36.3), 1.0, 12)
    SV.spin(js, fr(sid, 36.3), n_all(n), 120)
    p1 = P.photo("pa", "ph_jersey_asia", 4.6, (-6.2, 2.6, .3), .45, em=.85)
    p2 = P.photo("pl", "ph_jersey_lives", 4.0, (6.2, 2.6, .3), -.45, em=.85)
    pop_in(p1, fr(sid, 36.5), 1.0, 12)
    pop_in(p2, fr(sid, 36.8), 1.0, 12)
    po, pof = sign("po", "PRE-ORDER", (0, -1.4, 6.6), .55, "n_cyan", 7.0)
    pop_pair((po, pof), fr(sid, 37.51))
    pr, prf = sign("pr", "Rp1,19 jt", (2.6, -2.0, 2.4), .36, "n_gold", 7.0)
    pop_pair((pr, prf), fr(sid, 37.9))
    aj = phone("aj", "art_jersey10", 6.6, (0, 6.2, .1), 0.0, sid, 38.6, n, .3)
    coin_burst("cb", sid, 38.77, 16, (0, -1.0, 3.0), 3.4, 3, s=.9)
    camera(sid, [(36.15, (0, 0, 3.4), 30, 10, 17), (37.6, (0, 0, 3.6), -40, 12, 17.5),
                 (39.3, (0, 0, 3.8), -110, 12, 18), (41.0, (0, 0, 3.8), -150, 10, 18.5)], lens=26)
    A["AJ"] = (aj["root"], (0, 0, 7.0))
    A["JS"] = (js, (0, 0, 4.9))


def q11(n, A):
    """Ditambah toko resmi di 7 lokasi + membership di aplikasi: deretan 7 toko mini (nama kota) di jalan
    melengkung, foto Persib Store Cibubur, HP membership; kamera menyamping (truck) kanan -> kiri."""
    sid = "Q11"
    stage(rig_c=(0, 0, 3), rig_s=1.8, fade=(14, 60))
    cities = ["GRAHA PERSIB", "TSM BANDUNG", "CIANJUR", "SUKABUMI", "SUMEDANG", "LEMBANG", "CIBUBUR"]
    for i, c in enumerate(cities):
        x = 12.0 - i * 4.6
        y = 2.0 + .045 * (x ** 2) / 3
        sf = Q.store_front(f"st{i}", c, (x, y, 0), .95, math.radians(-x * 1.6))
        pop_in(sf, fr(sid, 41.75 + .1 * i), 1.0, 10)
        ns = Q.text3d(f"no{i}", str(i + 1), (x, y - 1.2, 4.2), .55, "pod_1", 5.0)
        pop_in(ns, fr(sid, 42.35 + .08 * i), 1.0, 8)
    ph = P.photo("ps", "ph_store2", 4.2, (-14.0, 4.6, .3), .5, em=.85)
    pop_in(ph, fr(sid, 42.8), 1.0, 12)
    mp = phone("mp", "art_loyalty", 6.4, (-9.4, -1.2, .1), .2, sid, 43.66, n, .3)
    mc = P.photo("mc", "ph_member", 2.0, (-6.4, -3.0, 3.0), .15, em=1.1, border=.06)
    pop_in(mc, fr(sid, 44.2), 1.0, 10)
    float_bob(mc, fr(sid, 44.2), n_all(n), .15, 50)
    camera(sid, [(41.0, (9.0, 2, 2.4), -62, 10, 17), (42.6, (3.0, 2, 2.4), -80, 12, 19),
                 (44.0, (-5.0, 1, 2.6), -100, 10, 17), (45.5, (-8.0, 0, 2.8), -112, 8, 15)], lens=26)
    A["ST"] = (ph, (0, 0, 4.6))
    A["MP"] = (mp["root"], (0, 0, 6.8))


def q12(n, A):
    """Bobotoh bukan cuma penonton, mereka pelanggan tetap: dinding foto bobotoh (koreo, nobar, Pesta Biru),
    papan FANS berputar jadi CUSTOMERS; kamera sudut rendah dorong masuk."""
    sid = "Q12"
    stage(rig_c=(0, 0, 3.5), rig_s=1.6, fade=(12, 56))
    for i, (im, x, z, r) in enumerate((("ph_koreo", -5.8, 3.4, .35), ("ph_nobar", 0, 4.4, 0.0),
                                       ("ph_pesta", 5.8, 3.4, -.35))):
        p = P.photo(f"ph{i}", im, 4.4, (x, 3.6 + abs(x) * .2, z - 3.0), r, em=.85)
        pop_in(p, fr(sid, 45.6 + .12 * i), 1.0, 12)
    f1, f1f = sign("fans", "FANS", (0, -1.4, 3.0), .9, "n_cyan", 7.0)
    c1, c1f = sign("cust", "LOYAL CUSTOMERS", (0, -1.4, 3.0), .62, "n_gold", 8.0)
    pop_pair((f1, f1f), fr(sid, 46.6))
    out_pair((f1, f1f), fr(sid, 47.55), 6)
    pop_pair((c1, c1f), fr(sid, 47.85))
    for i in range(10):
        c = P.coin(f"c{i}", (0, 0, 0), .8)
        f0 = fr(sid, 48.1 + .07 * i)
        arc_move(c, f0, f0 + 18, (-6 + 1.3 * i, -4.0, 0.0), (-.4 + .1 * i, -1.6, 1.6), 2.0, "out")
        key(c, "scale", 1, (.001,) * 3)
        key(c, "scale", f0 - 1, (.001,) * 3)
        key(c, "scale", f0 + 2, (.8, .8, .8))
        key(c, "scale", f0 + 16, (.8, .8, .8))
        key(c, "scale", f0 + 18, (.001,) * 3)
    camera(sid, [(45.5, (0, 0, 3.4), -102, 2, 17), (47.4, (0, 0, 3.4), -92, 6, 15),
                 (49.05, (0, 0, 3.3), -84, 9, 13.5)], lens=24)


# ================================================================== ASIA
def q13(n, A):
    """Dari Asia ada uang tambahan; ACL Two: tiap menang ada bonus: globe berputar ke Asia, pin Bandung-Seoul-
    Hanoi, logo ACL Two, koin 'WIN BONUS'; artikel luar negeri (A-Leagues, Australia). Orbit dari kanan-atas."""
    sid = "Q13"
    stage(rig_c=(0, 0, 3.5), rig_s=1.6, fade=(12, 56))
    gl = G.globe("gl", 3.6, (0, 1.0, 4.6), 1.8, 112.0)
    pop_in(gl["root"], fr(sid, 49.1), 1.0, 12)
    rz0 = gl["root"].rotation_euler.z
    key(gl["root"], "rotation_euler", fr(sid, 49.1), (0, 0, rz0 - math.radians(40)))
    key(gl["root"], "rotation_euler", fr(sid, 51.5), (0, 0, rz0))
    key(gl["root"], "rotation_euler", n_all(n), (0, 0, rz0 + math.radians(6)))
    for code, (la, lo), t, k_ in (("BDG", (-6.9, 107.6), 49.63, "n_cyan"), ("SEL", (37.6, 127.0), 50.34, "n_gold"),
                                  ("HAN", (21.0, 105.8), 50.6, "n_gold")):
        pb = G.pin_beam("pin" + code, gl["root"], G.latlon(la, lo, 3.6), 3.6, 1.5, k_, 7.0)
        pop_in(pb, fr(sid, t), 1.0, 9)
    lc = P.logo_card("acl", "lg_acl2", 2.6, (-5.6, -.5, 4.0), .35, plate="plate_w", em=1.1)
    pop_in(lc, fr(sid, 51.56), 1.0, 10)
    wb, wbf = sign("wb", "WIN BONUS", (5.2, -.8, 6.2), .45, "n_gold", 7.0)
    pop_pair((wb, wbf), fr(sid, 53.09))
    coin_burst("cb", sid, 53.79, 10, (5.2, -.8, 5.2), 2.0, 4, s=.85)
    aa = phone("aa", "art_aleagues", 6.4, (6.4, 4.0, .1), -.4, sid, 52.2, n, .25)
    camera(sid, [(49.05, (0, 1, 4.4), 38, 32, 24), (51.0, (0, 1, 4.4), -30, 18, 21),
                 (53.2, (.5, 1, 4.2), -78, 10, 20), (55.05, (1.0, 1, 4.2), -96, 8, 20)], lens=24)
    A["ACL"] = (lc, (0, 0, 3.0))
    A["AA"] = (aa["root"], (0, 0, 6.8))


def q14(n, A):
    """Dua kemenangan pertama: FC Seoul 0-1 Persib (Seoul, 16/9) & Persib 1-0 Cong Viettel (14/10); total
    ±US$400 rb (partisipasi grup + bonus menang). Kamera menyapu dari kanan ke kiri."""
    sid = "Q14"
    stage(rig_c=(0, 0, 3.5), rig_s=1.6, fade=(12, 56))
    s1 = Q.scoreboard("sb1", "FC SEOUL", "PERSIB", "0 - 1", "ph_seoul", (-3.6, 1.0, .2), 6.2, .18)
    s2 = Q.scoreboard("sb2", "PERSIB", "CONG VIETTEL", "1 - 0", "ph_viettel", (3.6, 1.0, .2), 6.2, -.18)
    pop_in(s1, fr(sid, 55.43), 1.0, 12)
    pop_in(s2, fr(sid, 55.83), 1.0, 12)
    for i, (pl, x) in enumerate((("pl_julio_cesar", -8.4), ("pl_mariano_peralta", 8.4))):
        p = P.photo(f"pl{i}", pl, 3.6, (x, 3.4, .3), .5 if x < 0 else -.5, em=.9, border=.08)
        pop_in(p, fr(sid, 55.9 + .2 * i), 1.0, 12)
    V.disc_ped("jar", 1.7, "psb_blue2", (0, -2.6, 0), em=4.5, h=.35)
    for i in range(16):
        c = P.coin(f"st{i}", (0, -2.6, .45 + i * .16), 1.0)
        c.rotation_euler = (0, 0, i * .4)
        pop_in(c, fr(sid, 56.6 + .08 * i), 1.0, 6)
    camera(sid, [(55.05, (.5, 0, 3.0), -22, 9, 18), (56.6, (0, 0, 3.0), -70, 10, 19),
                 (58.90, (-.5, 0, 3.0), -128, 9, 18)], lens=24)
    A["SB1"] = (s1, (0, 0, 5.3))
    A["SB2"] = (s2, (0, 0, 5.3))


# ================================================================== INSIDEN
def q15(n, A):
    """Satu insiden bisa bikin semua pintu bocor: 5 pintu brankas (sama seperti di awal) berlampu alarm merah,
    koin bocor keluar dari bawah tiap pintu; kamera tinggi dari kiri lalu turun."""
    sid = "Q15"
    stage(rig_c=(0, 0, 3.5), rig_s=1.8, fade=(14, 60))
    ds = door_row("d", 1.0)
    for i, d in enumerate(ds):
        pop_in(d["root"], fr(sid, 58.95 + .04 * i), 1.0, 8)
        rnd = random.Random(10 + i)
        x0, y0 = d["root"].location.x, d["root"].location.y
        for k in range(7):                            # koin bocor
            f0 = fr(sid, 60.6 + .12 * k + .05 * i)
            c = P.coin(f"lk{i}_{k}", (x0, y0 - .3, .3), .55)
            arc_move(c, f0, f0 + 16, (x0 + rnd.uniform(-.8, .8), y0 - .4, .25),
                     (x0 + rnd.uniform(-1.6, 1.6), y0 - 3.4 - rnd.uniform(0, 1.5), .06), .4, "out")
            key(c, "scale", 1, (.001,) * 3)
            key(c, "scale", f0 - 1, (.001,) * 3)
            key(c, "scale", f0, (.55, .55, .55))
            c.rotation_euler = (math.radians(90), 0, rnd.uniform(0, 3))
    for i, x in enumerate((-9.2, 0, 9.2)):
        sr, sli = V.siren(f"sr{i}", (x, -.5, 6.6), .9)
        pop_in(sr, fr(sid, 59.54), .9, 8)
        V.flash_siren(sr, sli, fr(sid, 59.54), n_all(n), 10)
    li = V.area("alarm", (0, -6, 9), (0, 1, 2), 2400.0, 10.0, (1, .12, .1))
    V.pulse_light(li, fr(sid, 59.54), n_all(n), 14, .15, 1.0)
    camera(sid, [(58.90, (0, 1, 2.6), -128, 48, 28), (60.4, (0, 0, 2.4), -110, 28, 24),
                 (61.65, (0, -1, 2.0), -96, 14, 20)], lens=24)


def q16(n, A):
    """Denda AFC US$200 rb + 2 laga kandang tanpa penonton -> total ±US$0,5 jt melayang: stadion KOSONG bernuansa
    merah, papan denda, cap 'NO FANS x2', koin menguap; artikel MetroTV. Kamera tinggi dari kanan berputar."""
    sid = "Q16"
    st = P.stadium(crowd=False)
    for i, (x, y) in enumerate(((-9, -6), (9, 6), (0, -9))):
        V.area(f"red{i}", (x, y, st["z_top"] + 6), (0, 0, 0), 2200.0, 9.0, (1, .15, .12))
    fn, fnf = sign("fine", "- US$200K", (0, -1.0, 6.2), 1.0, "n_red", 9.0)
    pop_pair((fn, fnf), fr(sid, 62.06), 1.0, 9)
    nf, nff = sign("nofans", "NO FANS  x2", (0, -1.0, 3.6), .8, "n_red", 9.0)
    pop_pair((nf, nff), fr(sid, 64.49), 1.0, 9)
    for ob in (nf, nff):
        if ob is not None:
            ob.rotation_euler.y = math.radians(-7)
    tot, totf = sign("tot", "US$0,5 JT", (0, -1.0, 8.8), .8, "n_gold", 9.0)
    pop_pair((tot, totf), fr(sid, 67.61), 1.0, 9)
    out_pair((tot, totf), fr(sid, 68.95), 10)
    for i in range(20):                               # koin naik lalu menguap
        c = P.coin(f"ev{i}", (0, 0, 0), .9)
        f0 = fr(sid, 66.6 + .06 * i)
        a = 2 * math.pi * i / 20
        arc_move(c, f0, f0 + 40, (3.0 * math.cos(a), 3.0 * math.sin(a), .3),
                 (6.0 * math.cos(a), 6.0 * math.sin(a), 10.0), .5, "inout")
        key(c, "scale", 1, (.001,) * 3)
        key(c, "scale", f0 - 1, (.001,) * 3)
        key(c, "scale", f0 + 3, (.9, .9, .9))
        key(c, "scale", fr(sid, 68.91), (.9, .9, .9))
        key(c, "scale", fr(sid, 68.91) + 8, (.001,) * 3)
    ad = phone("ad", "art_denda", 6.4, (-6.2, 2.0, .1), .4, sid, 62.92, n, .3)
    camera(sid, [(61.65, (0, 0, 4.0), 36, 26, 27), (64.0, (0, 0, 4.0), -10, 16, 22),
                 (66.6, (0, 0, 4.6), -50, 12, 20), (69.65, (0, 0, 5.2), -78, 14, 22)], lens=24)
    A["AD"] = (ad["root"], (0, 0, 6.8))


# ================================================================== RESOLUSI
def q17(n, A):
    """Follower jutaan tidak otomatis jadi uang; Persib mengubahnya lewat tiket, jersey, toko, membership,
    sponsor: corong kaca, ikon follower jatuh masuk, 5 pipa berlabel mengalirkan koin; kamera crane turun."""
    sid = "Q17"
    stage(rig_c=(0, 0, 4), rig_s=1.8, fade=(14, 60))
    fu = Q.funnel("fu", (0, 1.0, 7.4), 3.4, .7, 3.4)
    pop_in(fu, fr(sid, 69.8), 1.0, 12)
    rnd = random.Random(8)
    for i in range(24):
        f0 = fr(sid, 70.4 + .1 * i)
        fo = Q.follower(f"fo{i}", (0, 0, 0), .45, "fol_blue" if i % 4 else "yt_red")
        a = rnd.uniform(0, 2 * math.pi)
        arc_move(fo, f0, f0 + 24, (2.8 * math.cos(a), 1.0 + 2.2 * math.sin(a), 13.8), (0, 1.0, 7.2), .2, "in")
        key(fo, "scale", 1, (.001,) * 3)
        key(fo, "scale", f0 - 1, (.001,) * 3)
        key(fo, "scale", f0 + 3, (1, 1, 1))
        key(fo, "scale", f0 + 20, (1, 1, 1))
        key(fo, "scale", f0 + 24, (.001,) * 3)
    hub = V.block("hub", "n_cyan", 1.3, (0, 1.0, 5.4), 2.0, 6.0)
    pop_in(hub, fr(sid, 70.0), 1.3, 10)
    bar = Q.pipe("bar", 0, 1.0, 0, 0)                 # (placeholder: pipa horizontal dibangun di bawah)
    bar.scale = (.001,) * 3
    mb = Q.W.MB("hbar")
    mb.box(-5.8, .78, 5.0, 5.8, 1.22, 5.35, "pipe")
    mb.box(-5.8, .74, 4.98, 5.8, .78, 5.06, "pipe_glow")
    hb = mb.build()
    V.glow(hb, {"pipe_glow": 5.0})
    pop_in(hb, fr(sid, 72.9), 1.0, 8)
    labels = [("TICKETS", 74.41), ("JERSEYS", 75.03), ("STORES", 75.69), ("MEMBERS", 76.37), ("SPONSORS", 77.11)]
    for i, (lab, t) in enumerate(labels):
        x = (i - 2) * 2.9
        pp = Q.pipe(f"pp{i}", x, 1.0, 1.2, 5.1, .24)
        pop_in(pp, fr(sid, 73.0 + .06 * i), 1.0, 8)
        sg, sgf = sign(f"lb{i}", lab, (x, -.3, 2.6), .3, "n_gold", 8.0)
        pop_pair((sg, sgf), fr(sid, t))
        coin_burst(f"cp{i}_", sid, t + .05, 7, (x, .6, 1.2), 1.0, 20 + i, s=.6, dur=10, y_land=-1.2)
    camera(sid, [(69.65, (0, 1, 9.0), -72, 30, 21), (72.4, (0, 1, 6.6), -84, 18, 22),
                 (74.4, (0, 0, 4.2), -92, 8, 24.5), (77.85, (0, 0, 3.8), -98, 6, 23.5)], lens=24)


def q18(n, A):
    """Kalau aset beres, nilai klub ditaksir Rp1 triliun (±US$60 jt): batangan emas bertumpuk, pintu brankas
    terbuka, logo Persib, papan 'Rp1 TRILIUN'; artikel Wikipedia EN musim 2026-27. Kamera crane naik dari kiri."""
    sid = "Q18"
    stage(rig_c=(0, 0, 3.5), rig_s=1.6, fade=(12, 56))
    vd = Q.vault_door("vd", (0, 3.0, 0), 4.4, 6.4, "PERSIB", "n_cyan", 0.0, .6)
    pop_in(vd["root"], fr(sid, 77.9), 1.0, 10)
    open_door(vd, fr(sid, 79.11), fr(sid, 79.9), -110)
    k = 0
    for layer in range(4):                            # piramida batangan emas
        for r in range(4 - layer):
            for c in range(5 - layer):
                x = (c - (4 - layer) / 2) * 1.7
                y = -1.0 + (r - (3 - layer) / 2) * .9
                gb = Q.gold_bar(f"gb{k}", (x, y, layer * .46), 1.0)
                pop_in(gb, fr(sid, 80.2 + .025 * k), 1.0, 6)
                k += 1
    lg = P.logo_card("lg", "lg_persib", 2.6, (0, 2.4, 6.8), 0.0, plate=None, em=1.4)
    pop_in(lg, fr(sid, 80.18), 1.0, 10)
    rp, rpf = sign("rp", "Rp1 TRILIUN", (0, -1.6, 4.4), 1.0, "n_gold", 9.0)
    pop_pair((rp, rpf), fr(sid, 81.48), 1.0, 9)
    aw = phone("aw", "art_wiki2", 6.4, (-7.8, 3.4, .1), .45, sid, 78.6, n, .25)
    camera(sid, [(77.85, (0, 0, 2.4), -142, 4, 17), (80.2, (0, 0, 2.8), -118, 12, 19),
                 (82.4, (0, 0, 3.4), -96, 22, 21), (84.85, (0, 0, 3.6), -88, 28, 22)], lens=24)
    A["AW"] = (aw["root"], (0, 0, 6.8))


def q19(n, A):
    """CTA: klub di negaramu yang menghasilkan uang dari fans seperti ini? Logo Persib di podium bercahaya,
    bendera-bendera komentar; kamera orbit pelan dari kanan."""
    sid = "Q19"
    stage(rig_c=(0, 0, 3.5), rig_s=1.6, fade=(12, 56))
    V.disc_ped("ped", 3.0, "psb_blue2", (0, 0, 0), em=5.0, h=.5)
    lg = P.logo_card("lg", "lg_persib", 4.4, (0, 0, .5), 0.0, plate=None, em=1.35)
    pop_in(lg, fr(sid, 84.9), 1.0, 10)
    rg = V.ring_obj("ring", (0, 0, .55), 3.6, .1, "psb_blue2", 8.0)
    pop_in(rg, fr(sid, 85.1), 1.6, 12)
    P.flares("fl", 16, (-9, 3, 9, 7), .2, 9)
    for i, pl in enumerate(P.PLAYERS[:10]):
        side = -1 if i < 5 else 1
        k = i % 5
        p = P.photo(f"c{i}", pl, 3.4, (side * (6.4 + k * 2.2), 2.0 + k * 1.2, .3), side * -.4, em=.85, border=.08)
        pop_in(p, fr(sid, 85.4 + .06 * i), 1.0, 10)
    q, qf = sign("cm", "YOUR CLUB?", (0, -1.0, 8.6), .7, "n_gold", 8.0)
    pop_pair((q, qf), fr(sid, 85.73))
    camera(sid, [(84.85, (0, 0, 3.8), -58, 10, 21), (88.4, (0, 0, 4.0), -80, 9, 22),
                 (93.4, (0, 0, 4.0), -98, 8, 23)], lens=24)


SCENES = {f"Q{i:02d}": globals()[f"q{i:02d}"] for i in range(1, 20)}
K.SCENES = SCENES

if __name__ == "__main__":
    K.main()
