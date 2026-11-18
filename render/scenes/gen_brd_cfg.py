"""buat render/scenes/brd.json (overlay & efek) + render/scenes/brd_sfx.json (efek suara) — Liquid Vape Part 2 (Raka bikin brand).
Label: detik absolut -> lokal adegan. hero/fx/komentar: detik absolut (timeline video).
Efek dibuat HALUS: zoom-punch tanpa guncang, kilat lembut, chroma tipis, crossfade antaradegan (di compositor)."""
import json
import re

src = open("render/scenes_brd.py").read()
TL = [(a, float(b)) for a, b in re.findall(r'\("(B\d\d)", ([\d.]+)\)', src)]
END = float(re.search(r"END_T = ([\d.]+)", src).group(1))
T0 = dict(TL)
CITY = set(re.search(r"CITY = \{([^}]*)\}", src).group(1).replace('"', "").replace(" ", "").split(","))


def lb(anchor, title, t, color="purple", sub="", lift=80, until=None):
    d = dict(anchor=anchor, title=title, sub=sub, color=color, t=t, lift=lift)
    if until is not None:
        d["until"] = until
    return d


def hero(t0, t1, text, sub="", count=None, style="pink", size=124, y=1440):
    d = dict(t0=t0, t1=t1, text=text, sub=sub, style=style, size=size, y=y)
    if count:
        d["count"] = count
    return d


def hud(title, t, keys, mx, unit, tgt, dur=1.2, start=0, prefix=""):
    return dict(title=title, start=start, keys=keys, max=mx, unit=unit, t=t, dur=dur, target_text=tgt, prefix=prefix)


# (id, bubble, labels, hud, tilt-shift)
S = [
    ("B01", "Raka mau bikin **brand liquid**", [lb("RAKA", "RAKA", .7, "purple", "calon pemilik brand", 70),
                                                lb("FLASK", "RACIKAN RASA", 3.95, "pink", "modal terbesar?", 50)],
     None, .3),
    ("B02", "Ternyata **salah besar**", [], None, 0),
    ("B03", "Part 1: **Rp42 ribu** ke negara", [lb("BOTTLE", "1 BOTOL 60 ML", 7.0, "cyan", "Rp120 ribu", 50, 9.8),
                                                lb("GOV", "NEGARA", 10.4, "gold", "cukai + pajak rokok", 50)],
     None, 0),
    ("B04", "Gimana rasanya jadi **brand**?", [lb("STORE", "BRAND RAKA", 12.2, "purple", "", 60)], None, .3),
    ("B05", "Mulai dari **1.000 botol**", [lb("CARTON", "1.000 BOTOL", 16.4, "cyan", "60 ml", 50, 19.6),
                                          lb("FAC", "PABRIK BERIZIN CUKAI", 18.9, "green", "kerja sama produksi", 50)],
     hud("PRODUKSI PERTAMA", 15.6, [[15.93, 1000]], 1000, "botol", "60 ml / botol", 1.1), .25),
    ("B06", "Rincian **modal** Raka", [lb("P1", "PRODUKSI • BOTOL • LABEL • BOX", 24.1, "cyan", "Rp25 juta", 40),
                                       lb("P2", "DESAIN & LEGALITAS MEREK", 26.4, "purple", "Rp8 juta", 40),
                                       lb("P3", "MARKETING AWAL", 28.0, "pink", "Rp15 juta", 40)],
     hud("TOTAL MODAL", 20.9, [[24.03, 25], [26.37, 33], [27.99, 48]], 90, "juta", "berjalan", .7, 0, "Rp"), 0),
    ("B07", "Pos terbesar: **cukai & pajak**", [lb("P4", "CUKAI + PAJAK ROKOK", 31.95, "gold", "Rp42 juta", 40)],
     hud("TOTAL MODAL", 28.9, [[31.88, 90]], 90, "juta", "berjalan", .9, 48, "Rp"), 0),
    ("B08", "Dibayar **di depan**", [lb("MONEY", "CUKAI DIBAYAR DULU", 33.7, "gold", "", 50, 35.0),
                                     lb("CARTON", "BELUM LAKU", 35.6, "red", "0 botol terjual", 60)], None, .25),
    ("B09", "Total modal **±Rp90 juta**", [], None, 0),
    ("B10", "1.000 botol habis, **untung berapa**?", [lb("STORE", "TOKO VAPE", 41.0, "cyan", "", 60),
                                                     lb("RAKA", "RAKA", 41.3, "purple", "", 70)], None, .3),
    ("B11", "Brand jual ke toko **Rp90 ribu**", [lb("BRAND", "BRAND", 44.0, "purple", "", 70),
                                                 lb("TOKO", "TOKO VAPE", 44.6, "cyan", "", 70)], None, 0),
    ("B12", "1.000 × **Rp90 ribu**", [lb("GRID", "1.000 BOTOL", 48.4, "cyan", "", 50, 49.5)], None, 0),
    ("B13", "Pas. Cuma **balik modal**", [lb("MODAL", "MODAL", 50.9, "gold", "Rp90 juta", 40),
                                          lb("JUAL", "PENJUALAN", 51.1, "cyan", "Rp90 juta", 40)], None, 0),
    ("B14", "Untung mulai **batch kedua**", [lb("COST", "BIAYA PRODUKSI + CUKAI", 53.2, "purple", "±Rp67 ribu", 40),
                                             lb("PROFIT", "UNTUNG", 54.35, "green", "±Rp23 ribu", 40)], None, 0),
    ("B15", "Kuncinya **repeat order**", [lb("FLASK", "RASA", 57.45, "pink", "bukan penentu", 50)], None, .3),
    ("B16", "Stok **cepat habis** dulu", [lb("G0", "STOK", 61.35, "green", "", 40, 62.5),
                                          lb("G1", "STOK", 61.5, "green", "", 40, 62.5),
                                          lb("NEW", "TOKO BARU", 62.95, "cyan", "", 50)], None, .3),
    ("B17", "Yang menang: **dipesan ulang**", [lb("SPIKE", "RAMAI DI AWAL", 65.2, "pink", "", 40),
                                               lb("STEPS", "SERING DIPESAN ULANG", 67.1, "cyan", "", 40)], None, 0),
    ("B18", "Tim **BRAND** atau **TOKO**?", [lb("RAKA", "MODAL Rp90 JUTA", 69.9, "gold", "", 70, 71.3)], None, .25),
    ("B19", "Ini **simulasi** ya (18+)", [lb("TEMAN", "TEMEN KAMU", 78.7, "cyan", "pengin punya brand", 70, 79.9)],
     None, .3),
]

HERO = [
    hero(5.97, 6.75, "**SALAH BESAR**", "", style="red", size=130),
    hero(8.62, 10.6, "**Rp42 ribu**", "per botol masuk ke negara", dict(t0=8.62, t1=9.2, frm=0, to=42, fmt="Rp{} ribu"),
         style="gold"),
    hero(31.88, 33.3, "**Rp42 juta**", "cukai + pajak rokok di depan", dict(t0=31.88, t1=32.5, frm=0, to=42,
                                                                           fmt="Rp{} juta"), style="gold"),
    hero(34.9, 36.15, "Terjual: **0** botol", "", style="red", size=104),
    hero(38.3, 40.5, "**Rp90 juta**", "total modal", dict(t0=38.3, t1=39.0, frm=0, to=90, fmt="Rp{} juta")),
    hero(42.89, 43.65, "Untung **berapa**?", "", style="gold", size=110),
    hero(46.05, 48.1, "**Rp90 ribu**", "harga jual brand ke toko", dict(t0=46.05, t1=46.6, frm=0, to=90,
                                                                       fmt="Rp{} ribu"), style="purple"),
    hero(49.41, 50.8, "**Rp90 juta**", "1.000 botol × Rp90 ribu", dict(t0=49.41, t1=50.0, frm=0, to=90,
                                                                      fmt="Rp{} juta"), style="cyan"),
    hero(51.54, 52.65, "**BALIK MODAL**", "untung Rp0", style="orange", size=118),
    hero(54.31, 55.9, "**+Rp23 ribu**", "untung per botol (batch 2)", dict(t0=54.31, t1=54.9, frm=0, to=23,
                                                                          fmt="+Rp{} ribu"), style="green"),
    hero(58.27, 59.25, "**REPEAT ORDER**", "", style="cyan", size=118),
    hero(79.41, 82.2, "**SIMULASI**", "khusus 18 tahun ke atas", style="gold", size=120),
]

COMMENTS = [dict(t=73.45, text="BRAND", y=1395), dict(t=74.22, text="TOKO", y=1545)]

PUNCH = [(5.97, 1.0), (8.65, .6), (15.95, .5), (24.05, .6), (26.4, .5), (28.0, .5), (31.9, 1.1), (35.0, .6),
         (38.35, .9), (42.9, .5), (46.1, .7), (49.45, .8), (50.97, .9), (54.35, .8), (58.3, .8), (62.6, .5),
         (65.45, .5), (68.07, .7), (71.67, .5), (72.36, .5), (79.45, .6)]
FLASH = [(5.97, .28, "r"), (31.9, .22, "w"), (54.35, .18, "w")]
CHROMA = [(5.97, .3), (31.9, .25), (50.97, .2)]
PALE = [0, 0, "NONE"]

scenes = []
for i, (sid, bub, labels, hd, ts) in enumerate(S):
    t0 = T0[sid]
    for l_ in labels:
        l_["t"] = round(l_["t"] - t0, 3)
        if "until" in l_:
            l_["until"] = round(l_["until"] - t0, 3)
    d = dict(id=sid, bubble=bub, labels=labels, tilt=ts, theme="city" if sid in CITY else "neon")
    if hd:
        hd = dict(hd)
        hd["t"] = round(hd["t"] - t0, 3)
        hd["keys"] = [[round(a - t0, 3), b] for a, b in hd["keys"]]
        hd["pos"] = [56, 1640]
        d["hud"] = hd
    scenes.append(d)

cfg = dict(scenes=scenes, hero=HERO, comments=COMMENTS, comment_scene="B18",
           fx=dict(punch=PUNCH, flash=FLASH, chroma=CHROMA, pale=PALE),
           keywords=["brand", "liquid", "racikan", "rasa", "salah", "besar", "42 ribu", "negara", "1.000", "botol",
                     "60", "izin", "cukai", "25", "juta", "8", "15", "pos", "terbesarnya", "pajak", "rokok", "depan",
                     "laku", "90", "90 ribu", "modal", "untung", "berapa", "toko", "pas", "balik", "batch", "kedua",
                     "23 ribu", "repeat", "order", "sedikit", "habis", "menang", "ramai", "sering", "ulang", "vape",
                     "toko vape", "komentar", "simpan", "kirim", "simulasi", "18"])
json.dump(cfg, open("render/scenes/brd.json", "w"), ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- SFX
ev = [[0.05, "boom", .4]]
for sid, t in TL[1:]:
    ev.append([t - .22, "whoosh_low", .3, .55])
for t, g in PUNCH:
    ev.append([t, "impact" if g >= .9 else "pop", .4 * g if g >= .9 else .55])
for h in HERO:
    if h.get("count"):
        c = h["count"]
        ev.append([c["t0"], "ticks", .28, c["t1"] - c["t0"]])
        ev.append([c["t1"], "coin", .4])
ev += [[3.9, "pop", .4], [4.05, "pop", .3], [4.15, "pop", .3], [5.95, "stamp", .7], [9.9, "whoosh", .35, .9],
       [10.95, "ding", .35], [13.9, "pop", .45], [15.93, "ticks", .28, 1.1], [16.0, "pop", .3], [16.2, "pop", .3],
       [16.4, "pop", .3], [16.6, "pop", .3], [19.95, "ding", .4], [20.85, "pop", .4], [21.9, "pop", .4],
       [23.0, "pop", .4], [23.6, "whoosh", .3, .8], [27.3, "pop", .4], [30.2, "riser", .25, 1.6],
       [33.6, "whoosh", .4, 1.4], [35.6, "stamp", .4], [37.2, "scan", .25, 1.7], [39.0, "ding", .4],
       [40.55, "riser", .2, 3.0], [42.9, "pop", .45], [44.2, "whoosh", .3, 1.0], [45.9, "ding", .35],
       [48.25, "ticks", .28, .9], [49.6, "whoosh", .3, 1.0], [53.4, "pop", .4], [57.45, "stamp", .4],
       [58.15, "pop", .45], [61.3, "scan", .2, .9], [62.35, "coin", .4], [62.9, "pop", .45],
       [64.9, "riser", .2, .7], [65.9, "whoosh_low", .3, 1.0], [66.75, "pop", .35], [66.95, "pop", .35],
       [67.15, "pop", .35], [67.35, "pop", .35], [67.55, "pop", .35], [67.75, "pop", .35], [68.05, "ding", .45],
       [71.6, "pop", .45], [72.3, "pop", .45], [73.45, "type", .45, 5], [73.85, "notif", .4],
       [74.22, "type", .45, 4], [74.6, "notif", .4], [77.3, "whoosh", .35, 1.2], [78.7, "notif", .45],
       [79.45, "stamp", .45], [80.4, "whoosh_low", .35, 1.0]]
ev.sort(key=lambda e: e[0])
json.dump(ev, open("render/scenes/brd_sfx.json", "w"))
print(len(scenes), "adegan,", len(ev), "sfx")
