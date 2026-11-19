"""buat render/scenes/gta.json (overlay & efek) + render/scenes/gta_sfx.json (efek suara) — GTA VI, Rp17 triliun sebelum rilis.
Label: detik absolut -> lokal adegan. hero/fx/komentar: detik absolut (timeline video).
Efek dibuat HALUS: zoom-punch tanpa guncang, kilat lembut, chroma tipis, crossfade antaradegan (di compositor)."""
import json
import re

src = open("render/scenes_gta.py").read()
TL = [(a, float(b)) for a, b in re.findall(r'\("(G\d\d)", ([\d.]+)\)', src)]
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


def hud(title, t, keys, mx, unit, tgt, dur=1.2, start=0, prefix="", decimals=0):
    d = dict(title=title, start=start, keys=keys, max=mx, unit=unit, t=t, dur=dur, target_text=tgt, prefix=prefix)
    if decimals:
        d["decimals"] = decimals
    return d


# (id, bubble, labels, hud, tilt-shift)
S = [
    ("G01", "Jutaan orang **pre-order** GTA 6", [lb("QUEUE", "PEMBELI SELURUH DUNIA", .9, "cyan", "antre pre-order", 60)],
     None, .3),
    ("G02", "Padahal **belum bisa dimainkan**", [lb("CASE", "GTA VI", 3.4, "pink", "sudah dibayar", 50),
                                                 lb("LOCK", "BELUM RILIS", 5.15, "gold", "", 40)], None, 0),
    ("G03", "Belum lihat **gameplay barunya**", [lb("SCREEN", "CUPLIKAN RESMI", 6.6, "cyan", "trailer & artwork", 50, 8.3),
                                                 lb("YOU", "KAMU?", 8.9, "gold", "", 70)], None, .25),
    ("G04", "Namanya **GTA 6**", [lb("JL", "JASON & LUCIA", 10.8, "pink", "tokoh utama", 50, 12.3)], None, 0),
    ("G05", "Pre-order **9,69 juta kopi**", [lb("ID", "INDONESIA", 15.7, "red", "ikut pre-order", 50, 18.0)],
     hud("PRE-ORDER (ESTIMASI)", 15.4, [[17.35, 9.69]], 10, "juta kopi", "sebelum rilis", 1.4, 0, "", 2), 0),
    ("G06", "Nilainya **hampir Rp17 triliun**", [lb("TOWER", "UANG PRE-ORDER", 22.3, "gold", "", 50)],
     hud("NILAI PRE-ORDER", 19.9, [[20.96, 942]], 942, "juta", "hampir Rp17 triliun", 1.6, 0, "US$"), 0),
    ("G07", "Uang masuk **duluan**", [lb("HQ", "ROCKSTAR GAMES", 25.8, "gold", "uang sudah masuk", 60),
                                      lb("LATE", "GAME-NYA", 27.0, "cyan", "belakangan", 50)], None, .25),
    ("G08", "Bayar **tanpa lihat isinya**?", [lb("BOX", "ISINYA?", 29.0, "pink", "belum ada yang main", 60)], None, 0),
    ("G09", "Jawabannya: **13 tahun**", [lb("Y13", "2013 • GTA V", 32.6, "green", "", 40, 33.8),
                                         lb("Y26", "2026 • GTA VI", 34.0, "pink", "", 40)], None, 0),
    ("G10", "Rockstar **nggak perlu promosi**", [lb("RS", "ROCKSTAR GAMES", 35.15, "gold", "", 60)], None, .2),
    ("G11", "Stok fisik **habis** dalam jam", [lb("SHELF", "STOK FISIK PERTAMA", 36.45, "cyan", "", 40, 37.9),
                                               lb("CLOCK", "HITUNGAN JAM", 37.25, "pink", "", 40)], None, .25),
    ("G12", "Edisi mahal **paling laris**", [lb("STD", "STANDARD", 39.0, "cyan", "", 50),
                                            lb("ULT", "ULTIMATE EDITION", 39.5, "gold", "lebih mahal", 50)], None, 0),
    ("G13", "Harga dasar **termahal**", [lb("VI", "GTA VI", 44.8, "gold", "termahal sepanjang sejarah GTA", 50)],
     None, 0),
    ("G14", "Tapi **tunggu**...", [lb("T17", "Rp17 TRILIUN", 47.45, "gold", "pre-order", 50, 49.6),
                                   lb("GHOST", "PROYEKSI ANALIS", 50.0, "cyan", "", 60)], None, 0),
    ("G15", "Proyeksi **minggu pertama**", [lb("AN", "ANALIS", 52.0, "purple", "proyeksi pendapatan", 60),
                                            lb("B1", "US$3,25 MILIAR", 55.0, "cyan", "", 40),
                                            lb("B2", "US$5,2 MILIAR", 56.7, "pink", "", 40)], None, 0),
    ("G16", "Cuma dalam **1 minggu**", [lb("T17", "Rp17 T", 58.6, "gold", "", 40),
                                        lb("T58", "Rp58 T", 59.3, "cyan", "", 40),
                                        lb("T93", "Rp93 T", 60.2, "pink", "", 40)],
     hud("PROYEKSI 1 MINGGU", 58.4, [[58.67, 58], [59.64, 93]], 93, "triliun", "sampai", .8, 0, "Rp"), .2),
    ("G17", "Dan itu **tanpa versi PC**", [lb("PS5", "PS5", 63.55, "cyan", "sudah bisa", 50),
                                           lb("PC", "PC", 65.1, "purple", "belum ada", 50)], None, 0),
    ("G18", "Tim **PS5** atau **PC**?", [], None, .2),
    ("G19", "Kirim ke **temen** yang pre-order", [lb("ME", "KAMU", 74.8, "gold", "", 70, 76.4),
                                                  lb("TEMAN", "TEMEN KAMU", 76.7, "cyan", "udah pre-order", 70, 78.2)],
     None, .25),
]

HERO = [
    hero(1.38, 3.13, "**Rp1,19 juta**", "per kopi, dibayar di muka", style="gold"),
    hero(5.0, 6.26, "**BELUM BISA DIMAINKAN**", "", style="red", size=96),
    hero(17.35, 19.65, "**9,69 juta** kopi", "estimasi pre-order", style="cyan", size=112),
    hero(20.96, 23.9, "**US$942 juta**", "nilai pre-order", dict(t0=20.96, t1=21.8, frm=0, to=942, fmt="US${} juta"),
         style="gold", size=118),
    hero(24.06, 25.45, "hampir **Rp17 triliun**", "", style="gold", size=124),
    hero(31.4, 32.45, "Kok **bisa**?", "", style="pink", size=118),
    hero(33.05, 34.96, "**13 tahun**", "penantian", dict(t0=33.05, t1=33.7, frm=0, to=13, fmt="{} tahun"),
         style="pink"),
    hero(41.6, 42.9, "**PALING LARIS**", "", style="gold", size=118),
    hero(44.3, 47.0, "**Rp1,19 juta**", "harga dasar GTA termahal", style="purple"),
    hero(50.3, 51.7, "baru **pemanasan**", "", style="pink", size=112),
    hero(56.43, 58.19, "**US$3,25–5,2 M**", "proyeksi pendapatan minggu pertama", style="cyan", size=104),
    hero(60.2, 63.0, "**Rp58–93 T**", "cuma dalam 1 minggu", style="gold", size=124),
    hero(64.82, 66.79, "**TANPA PC**", "", style="red", size=124),
    hero(78.25, 83.4, "**ESTIMASI**", "pihak ketiga & analis, bukan data resmi Rockstar", style="gold", size=112),
]

COMMENTS = [dict(t=71.3, text="PS5", y=1395), dict(t=72.95, text="PC", y=1545)]

PUNCH = [(1.4, .8), (5.0, .7), (8.9, .5), (10.75, .9), (13.5, .5), (17.35, .7), (21.0, .7), (24.06, 1.0),
         (25.6, .5), (27.0, .5), (31.4, .7), (33.05, .9), (35.55, .6), (38.3, .9), (41.9, .7), (44.6, .7),
         (49.3, .5), (50.4, .8), (56.43, .9), (60.2, 1.0), (65.0, .9), (68.3, .5), (70.2, .5), (78.3, .6)]
FLASH = [(10.75, .22, "w"), (24.06, .22, "w"), (60.2, .2, "w"), (38.3, .2, "r")]
CHROMA = [(10.75, .25), (24.06, .25), (50.4, .2), (65.0, .2)]
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

cfg = dict(scenes=scenes, hero=HERO, comments=COMMENTS, comment_scene="G18",
           fx=dict(punch=PUNCH, flash=FLASH, chroma=CHROMA, pale=PALE),
           keywords=["jutaan", "1,19", "juta", "game", "belum", "mainkan", "gameplay", "kamu", "gta", "6", "6,",
                     "19", "november", "pre-ordernya", "9,69", "kopi", "942", "dolar", "17", "triliun", "duluan",
                     "belakangan", "muka", "isinya", "13", "tahun", "penantian", "rockstar", "promosi", "stok",
                     "habis", "jam", "mahal", "laris", "termahal", "sejarah", "tunggu", "pemanasan", "analis",
                     "minggu", "3,25", "5,2", "miliar", "58", "93", "satu", "pc", "ps5", "komentar", "kirim", "temen",
                     "pre-order", "estimasi", "resmi"])
json.dump(cfg, open("render/scenes/gta.json", "w"), ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- SFX
ev = [[0.05, "boom", .4]]
for sid, t in TL[1:]:
    ev.append([t - .22, "whoosh_low", .28, .55])
for t, g in PUNCH:
    ev.append([t, "impact" if g >= .9 else "pop", .4 * g if g >= .9 else .35])
for h in HERO:
    if h.get("count"):
        c = h["count"]
        ev.append([c["t0"], "ticks", .26, c["t1"] - c["t0"]])
        ev.append([c["t1"], "coin", .4])
# --- desain per adegan / per kata VO
SCN = {
    "G01": [[0.0, "heli", .32, 2.8], [.3, "car", .22, 1.6], [.8, "crowd", .32, 2.4], [1.38, "cash", .5],
            [1.9, "flutter", .35, .6]],
    "G02": [[3.2, "whoosh", .3, .5], [4.6, "chain", .5, .7], [4.8, "chain", .35, .5], [4.95, "clank", .6],
            [5.0, "bass_drop", .4, 1.2]],
    "G03": [[6.3, "crowd", .28, 4.0], [6.9, "pop", .4], [7.4, "glitch", .2], [8.5, "glitch", .2],
            [9.5, "glitch", .2], [8.25, "whoosh", .25, .6], [8.9, "star", .35]],
    "G04": [[10.3, "flutter", .4, .7], [10.42, "sparkle", .45, 1.0], [11.6, "whoosh", .25, .7],
            [12.8, "whoosh_rev", .22, .7], [14.0, "whoosh", .22, .7], [13.45, "ding", .4], [13.5, "star", .35]],
    "G05": [[15.3, "scan", .2, 2.2], [16.0, "whoosh", .22, 1.2], [17.35, "ding", .4]] +
           [[15.45 + .11 * i, "ping", .22, (1568.0, 1760.0, 2093.0)[i % 3]] for i in range(20)],
    "G06": [[19.9, "coins_pour", .32, 3.8], [20.96, "cash", .5], [24.06, "bass_drop", .55, 1.4], [24.3, "ding", .4]],
    "G07": [[25.55, "whoosh_low", .4, 1.0], [25.6, "coins_pour", .3, 1.2], [26.4, "cash", .42],
            [26.95, "pop", .45], [27.2, "ticks", .22, .8]],
    "G08": [[29.5, "coin", .32], [29.85, "coin", .3], [30.2, "coin", .3], [30.55, "coin", .3], [30.9, "coin", .3],
            [30.6, "heart", .4], [31.3, "heart", .35]],
    "G09": [[32.5, "whoosh", .35, 2.3], [32.5, "ticks", .22, 1.7], [33.9, "sparkle", .35, .8], [34.0, "ding", .4]],
    "G10": [[35.1, "star", .4], [35.55, "stamp", .45]],
    "G11": [[36.3, "crowd", .34, 2.4], [36.45, "ticks", .28, 1.6], [37.0, "tick", .3], [38.3, "stamp", .55],
            [38.3, "bass_drop", .3, 1.0]],
    "G12": [[39.9, "riser", .2, 1.6], [41.0, "cash", .35], [41.9, "cheer", .35, 1.2], [41.9, "ding", .4]],
    "G13": [[42.4, "pop", .35], [42.85, "pop", .35], [43.3, "pop", .35], [44.0, "riser", .25, .8],
            [44.3, "cash", .42], [46.0, "ding", .4]],
    "G14": [[47.3, "heart", .5], [48.1, "heart", .45], [48.8, "riser", .3, 1.5], [49.2, "whoosh_low", .45, 2.0],
            [50.4, "bass_drop", .5, 1.4]],
    "G15": [[52.0, "scan", .2, 1.0], [52.2, "type", .3, 6], [52.4, "riser", .2, 4.5], [52.0, "pop", .35],
            [54.7, "pop", .4], [56.4, "pop", .4], [56.43, "ding", .4]],
    "G16": [[58.2, "whoosh_low", .4, 1.4], [58.9, "whoosh_low", .35, 1.4], [59.7, "whoosh_low", .35, 1.4],
            [58.3, "coins_pour", .32, 3.0], [60.2, "bass_drop", .6, 1.6], [61.0, "car", .22, 1.6],
            [61.6, "ding", .4], [62.0, "siren", .1, 1.2]],
    "G17": [[63.4, "pop", .35], [65.0, "clank", .55], [65.0, "bass_drop", .35, 1.0]],
    "G18": [[66.9, "crowd", .24, 7.5], [68.3, "pop", .45], [68.4, "cheer", .4, 1.6], [70.2, "pop", .45],
            [70.3, "cheer", .4, 1.6], [71.3, "type", .45, 3], [71.7, "notif", .4], [72.95, "type", .45, 2],
            [73.3, "notif", .4], [72.5, "car", .2, 1.6]],
    "G19": [[75.2, "whoosh", .35, 1.3], [76.7, "notif", .45], [78.3, "riser", .3, 1.0], [78.4, "sparkle", .4, 1.0],
            [78.4, "heli", .25, 3.6], [79.0, "whoosh_low", .35, 2.5], [82.0, "star", .3]],
}
for sid, evs in SCN.items():
    ev += evs
ev.sort(key=lambda e: e[0])
json.dump(ev, open("render/scenes/gta_sfx.json", "w"))
print(len(scenes), "adegan,", len(ev), "sfx")
