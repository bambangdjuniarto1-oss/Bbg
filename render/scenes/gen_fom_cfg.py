"""buat render/scenes/fom.json (overlay & efek) + render/scenes/fom_sfx.json (efek suara) —
Cara brand vape bertahan di tengah fatwa haram (FOOM).
Label: detik absolut -> lokal adegan. hero/fx/komentar: detik absolut (timeline video)."""
import json
import re

src = open("render/scenes_fom.py").read()
TL = [(a, float(b)) for a, b in re.findall(r'\("(F\d\d)", ([\d.]+)\)', src)]
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


S = [
    ("F01", "Sewa toko **ditolak**", [lb("ART", "KATADATA", .7, "cyan", "berita 18 Nov 2026", 40, 2.2),
                                     lb("DOC", "SEWA DITOLAK", 1.65, "red", "", 50)], None, .3),
    ("F02", "Bukan nunggak, tapi **fatwa**", [lb("BILL", "LUNAS", 3.95, "green", "bukan nunggak", 50),
                                             lb("FAT", "FATWA MUI", 4.6, "red", "", 50)], None, 0),
    ("F03", "**Fatwa MUI** No. 131/2026", [lb("MUI", "MUI • CNN • DETIK", 8.7, "cyan", "berita asli", 60, 11.6)],
     None, 0),
    ("F04", "Bukan cuma **pakai** yang haram", [lb("HR", "KESEHATAN", 17.15, "red", "", 40),
                                                lb("GL", "LINGKUNGAN", 17.65, "green", "", 40)], None, 0),
    ("F05", "Siapa yang **paling kena**?", [], None, .3),
    ("F06", "Ancaman **PHK 100 ribu** pekerja", [lb("CROWD", "PEKERJA", 21.3, "gold", "rantai industri vape", 50, 24.2),
                                                lb("FAC", "200 INDUSTRI", 25.3, "red", "terancam", 70)],
     hud("ANCAMAN PHK (KLAIM INDUSTRI)", 21.0, [[22.77, 100]], 100, "ribu pekerja", "200 industri terancam", 1.4),
     0),
    ("F07", "Brand lokal **paling disorot**", [lb("LOGO", "FOOM", 30.05, "pink", "brand lokal", 60)], None, 0),
    ("F08", "Pas lagi **campaign besar**", [lb("BB", "CAMPAIGN FOOM x YB", 31.6, "pink", "", 60),
                                           lb("TW", "FOOM", 33.6, "cyan", "", 40)], None, .25),
    ("F09", "Kolab **FOOM x YB**", [lb("COLLAB", "FOOM x YB", 35.0, "pink", "kolaborasi", 40, 36.9),
                                    lb("IG", "REZA ARAP (YB)", 36.6, "cyan", "", 40, 38.1),
                                    lb("GUY", "GAYA POP JEPANG", 39.4, "gold", "", 40)], None, 0),
    ("F10", "Pinjam **fanbase**", [lb("FANS", "FANBASE", 41.4, "pink", "", 60),
                                   lb("POD", "EKSKLUSIF", 42.75, "gold", "", 50)], None, 0),
    ("F11", "Isu meledak, **nggak panik**", [lb("LOGO", "FOOM", 44.0, "pink", "tetap tenang", 60)], None, 0),
    ("F12", "**Satu Industri, Satu Komitmen**", [lb("BAL", "HORMATI SEMUA PANDANGAN", 49.2, "cyan", "", 60, 51.2),
                                                 lb("GOV", "PATUH ATURAN", 51.95, "green", "pemerintah", 50)], None, 0),
    ("F13", "Label **21+** tetap dipasang", [lb("B21", "21+", 54.85, "red", "", 50),
                                             lb("WARN", "PERINGATAN NIKOTIN", 55.95, "gold", "", 40)], None, 0),
    ("F14", "**Regulasi**, bukan eliminasi", [], None, 0),
    ("F15", "Yang paling mahal: **kepercayaan**", [lb("PRODUK", "PRODUK", 64.3, "cyan", "", 40),
                                                   lb("TRUST", "KEPERCAYAAN", 65.1, "pink", "", 50)], None, 0),
    ("F16", "Kalau **kamu** pemilik brand?", [lb("ME", "KAMU", 67.2, "gold", "pemilik brand", 70, 70.0)], None, .25),
    ("F17", "Tulis **jawabanmu** di komentar", [lb("BM", "SIMPAN", 75.6, "gold", "buat referensi", 50)], None, .25),
    ("F18", "Buat **tim FOOM**", [lb("TW", "TIM FOOM", 80.0, "pink", "yuk bedah strategi", 60)], None, .2),
    ("F19", "Konten edukasi bisnis **21+**", [], None, .25),
]

HERO = [
    hero(1.57, 3.2, "Sewa **DITOLAK**", "bukan karena nunggak", style="red", size=118),
    hero(5.04, 6.3, "karena **satu fatwa**", "", style="gold", size=112),
    hero(9.92, 12.4, "Fatwa **No. 131/2026**", "MUI, 6 November 2026", style="pink", size=104),
    hero(14.11, 16.2, "pakai • produksi • **jual**", "semuanya dinyatakan haram", style="red", size=96),
    hero(22.77, 24.5, "**100 ribu** pekerja", "ancaman PHK (klaim industri)",
         dict(t0=22.77, t1=23.5, frm=0, to=100, fmt="{} ribu"), style="red", size=118),
    hero(24.83, 27.8, "**200** industri", "rokok elektrik terancam", dict(t0=24.83, t1=25.6, frm=0, to=200, fmt="{}"),
         style="gold", size=118),
    hero(29.97, 30.68, "**FOOM**", "", style="pink", size=150),
    hero(37.48, 40.2, "**PINK SAKURA**", "FOOM x YB", style="pink", size=118),
    hero(42.7, 43.6, "**EKSKLUSIF**", "", style="gold", size=118),
    hero(47.27, 49.0, "**Satu Industri, Satu Komitmen**", "pernyataan FOOM", style="pink", size=84),
    hero(58.72, 60.6, "**REGULASI**, bukan eliminasi", "", style="green", size=96),
    hero(65.05, 66.4, "**KEPERCAYAAN**", "aset termahal saat krisis", style="pink", size=112),
    hero(83.4, 86.6, "**EDUKASI BISNIS 21+**", "bukan ajakan menggunakan produk", style="gold", size=96),
]

COMMENTS = [dict(t=73.3, text="Klarifikasi resmi dulu", y=1395), dict(t=74.4, text="Cek fakta, baru bicara", y=1545)]

PUNCH = [(1.57, .9), (5.04, 1.0), (6.63, .6), (6.45, .5), (9.92, .8), (14.11, .7), (14.62, .5), (15.06, .5),
         (17.1, .5), (19.5, .7), (21.8, .8), (22.77, .9), (24.83, .8), (26.9, .5), (29.97, 1.0), (33.5, .5),
         (34.97, .7), (37.48, .8), (41.36, .5), (42.7, .8), (44.13, 1.0), (44.84, .5), (45.54, .5), (47.27, .7),
         (48.13, .7), (51.9, .7), (54.8, .9), (55.88, .6), (58.72, .8), (59.58, .6), (65.05, .9), (69.5, .7),
         (72.0, .6), (75.53, .6), (80.75, .5), (83.46, .7)]
FLASH = [(5.04, .22, "w"), (29.97, .25, "w"), (44.13, .22, "r"), (65.05, .18, "w")]
CHROMA = [(5.04, .25), (29.97, .3), (44.13, .3), (69.5, .2)]
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

cfg = dict(scenes=scenes, hero=HERO, comments=COMMENTS, comment_scene="F17",
           fx=dict(punch=PUNCH, flash=FLASH, chroma=CHROMA, pale=PALE),
           keywords=["jakarta", "ditolak", "sewa", "nunggak", "fatwa", "fatwa.", "6", "november", "mui", "131",
                     "2026", "haram", "produksi", "perdagangannya", "kesehatan", "lingkungan", "phk", "100", "ribu",
                     "200", "terancam", "disorot", "foom", "foom.", "foom,", "campaign", "yb", "reza", "arap",
                     "pink", "sakura", "jepang", "fanbase", "eksklusif", "meledak", "panik", "balik", "satu",
                     "industri", "komitmen", "menghormati", "patuh", "pemerintah", "21+", "nikotin", "regulasi",
                     "eliminasi", "krisis", "mahal", "produk", "kepercayaan", "kamu", "brand", "isu", "komentar",
                     "simpan", "strategi", "edukasi", "21", "bukan"])
json.dump(cfg, open("render/scenes/fom.json", "w"), ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- SFX (keren & sesuai tiap adegan / kata VO)
ev = [[0.02, "news", .55], [0.05, "boom", .4]]
for sid, t in TL[1:]:
    ev.append([t - .22, "whoosh_low", .28, .55])
for t, g in PUNCH:
    ev.append([t, "impact" if g >= .9 else "pop", .4 * g if g >= .9 else .32])
for h in HERO:
    if h.get("count"):
        c = h["count"]
        ev.append([c["t0"], "ticks", .26, c["t1"] - c["t0"]])
        ev.append([c["t1"], "ding", .35])
SCN = {
    "F01": [[0.0, "car", .22, 1.6], [.5, "paper", .45, .5], [.55, "whoosh", .3, .6], [1.0, "paper", .4, .45],
            [1.57, "stamp", .6], [2.3, "door", .55, 1.0]],
    "F02": [[3.3, "paper", .4], [3.85, "ding", .4], [3.95, "coin", .35], [4.45, "paper", .45], [4.5, "whoosh", .3, .5],
            [5.04, "gavel", .75], [5.06, "bass_drop", .35, 1.2]],
    "F03": [[6.3, "news", .45], [6.45, "paper", .45], [6.75, "paper", .35], [7.05, "paper", .35],
            [9.0, "type", .25, 6], [9.92, "stamp", .45]],
    "F04": [[12.6, "pop", .35], [13.1, "pop", .35], [13.4, "pop", .35], [14.11, "stamp", .45],
            [14.62, "stamp", .42], [15.06, "stamp", .42], [17.1, "heart", .4], [17.59, "sparkle", .35, .8]],
    "F05": [[18.7, "whoosh_low", .4, 1.4], [19.0, "siren", .14, 1.5], [19.5, "pop", .4]],
    "F06": [[20.7, "paper", .4], [21.2, "crowd", .25, 2.8], [21.8, "glitch", .3], [22.77, "bass_drop", .45, 1.3],
            [24.6, "paper", .4], [24.83, "ticks", .25, 1.6], [26.8, "siren", .16, 1.1], [26.9, "glass", .35, 1.0]],
    "F07": [[28.0, "heart", .4], [28.8, "whoosh", .25, .7], [29.6, "riser", .3, .4], [29.97, "bass_drop", .55, 1.4],
            [29.97, "flash", .55], [30.1, "flash", .45], [30.25, "flash", .45], [30.4, "flash", .4]],
    "F08": [[30.7, "car", .2, 1.6], [31.3, "sparkle", .3, .9], [32.4, "whoosh", .3, 1.2], [33.5, "kawaii", .35]],
    "F09": [[34.97, "kawaii", .45], [35.4, "paper", .35], [35.4, "notif", .35], [37.48, "sparkle", .45, 1.0],
            [37.69, "kawaii", .4], [38.25, "pop", .35], [38.68, "pop", .35], [39.37, "star", .4]],
    "F10": [[41.36, "cheer", .4, 1.8], [41.4, "sparkle", .3, .8], [42.7, "ding", .45], [42.75, "star", .4]],
    "F11": [[43.7, "riser", .3, .45], [44.13, "glass", .55, 1.2], [44.13, "bass_drop", .5, 1.3],
            [44.84, "stamp", .4], [45.54, "stamp", .4]],
    "F12": [[46.3, "paper", .45], [47.27, "type", .3, 7], [48.13, "type", .3, 7], [49.2, "whoosh", .25, .7],
            [50.0, "ding", .3], [51.2, "whoosh", .25, .7], [51.9, "ding", .45]],
    "F13": [[53.2, "paper", .35], [53.5, "paper", .3], [54.8, "sticker", .55], [54.85, "pop", .35],
            [55.88, "sticker", .5]],
    "F14": [[58.72, "riser", .25, .6], [58.9, "ding", .45], [59.6, "stamp", .45], [59.65, "whoosh_low", .3, .6]],
    "F15": [[60.7, "whoosh_low", .3, 1.2], [62.5, "tick", .3], [63.82, "clank", .35], [64.87, "heart", .4],
            [65.05, "bass_drop", .4, 1.2], [65.3, "star", .45]],
    "F16": [[66.5, "car", .2, 1.6], [69.5, "news", .45], [69.5, "siren", .14, 2.6], [69.6, "glitch", .3],
            [72.0, "pop", .4]],
    "F17": [[72.7, "pop", .3], [73.3, "type", .4, 5], [73.7, "notif", .4], [74.4, "type", .4, 5],
            [74.8, "notif", .4], [75.53, "ding", .45], [75.6, "sparkle", .35, .8]],
    "F18": [[78.8, "pop", .3], [79.2, "whoosh", .4, 2.2], [80.75, "star", .35], [81.5, "sparkle", .35, .9]],
    "F19": [[82.3, "whoosh_low", .35, 2.5], [83.46, "sticker", .4], [83.5, "kawaii", .3]],
}
for sid, evs in SCN.items():
    ev += evs
ev.sort(key=lambda e: e[0])
json.dump(ev, open("render/scenes/fom_sfx.json", "w"))
print(len(scenes), "adegan,", len(ev), "sfx")
