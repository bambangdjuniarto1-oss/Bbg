"""buat render/scenes/nkh.json (overlay & efek) + render/scenes/nkh_sfx.json (efek suara) — Nikahan Rp100 Juta.
Label: detik absolut -> lokal adegan. hero/fx/komentar: detik absolut (timeline video).
Efek dibuat HALUS: zoom-punch tanpa guncang, kilat lembut, chroma tipis, crossfade antaradegan (di compositor)."""
import json
import re

src = open("render/scenes_nkh.py").read()
TL = [(a, float(b)) for a, b in re.findall(r'\("(N\d\d)", ([\d.]+)\)', src)]
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


def hud(title, t, keys, mx, unit, tgt, dur=1.2):
    return dict(title=title, start=0, keys=keys, max=mx, unit=unit, t=t, dur=dur, target_text=tgt)


# (id, bubble, labels, hud, tilt-shift)
S = [
    ("N01", "Habis **Rp100 juta**", [lb("DIMAS", "DIMAS", .9, "pink", "pengantin baru", 70)], None, .3),
    ("N02", "Modal balik dari **amplop**?", [lb("BOX", "KOTAK AMPLOP", 3.9, "gold", "", 60),
                                            lb("PEL", "MODAL PESTA", 4.75, "pink", "Rp100 juta", 60)], None, 0),
    ("N03", "Malam itu amplop **dihitung**", [lb("PILE", "AMPLOP TAMU", 8.9, "gold", "", 50, 10.4)], None, 0),
    ("N04", "500 undangan × **Rp100 rb**", [lb("GRID", "500 UNDANGAN", 13.4, "cyan", "", 50, 16.9)],
     hud("UNDANGAN", 12.85, [[12.9, 500]], 500, "amplop", "rata-rata Rp100 rb", 1.35), 0),
    ("N05", "Cuma balik **setengah**", [lb("BIAYA", "BIAYA PESTA", 19.3, "pink", "Rp100 juta", 50),
                                       lb("BALIK", "AMPLOP BALIK", 19.55, "cyan", "Rp50 juta", 50)], None, 0),
    ("N06", "1 undangan = **2 orang**", [lb("PAIR", "1 UNDANGAN = 2 ORANG", 21.5, "cyan", "", 60)], None, .25),
    ("N07", "1.000 porsi × **Rp60 rb**", [lb("PLATE", "1 PORSI", 24.0, "gold", "", 50, 25.9)],
     hud("PORSI MAKANAN", 23.2, [[23.27, 1000]], 1000, "porsi", "500 undangan × 2", .8), 0),
    ("N08", "Amplopnya **nggak cukup**", [lb("AMPLOP", "AMPLOP", 28.0, "cyan", "Rp50 juta", 40),
                                         lb("KATERING", "TAGIHAN KATERING", 28.6, "pink", "Rp60 juta", 40)], None, 0),
    ("N09", "**Rp60 juta** ke mana?", [lb("TOWER", "Rp60 JUTA", 31.6, "pink", "bayar katering", 50, 33.6)], None, 0),
    ("N10", "Ke **pemilik katering**", [lb("CHEF", "PEMILIK KATERING", 35.35, "gold", "", 60)], None, 0),
    ("N11", "Margin katering **±30%**", [lb("COST", "BAHAN • STAF • SEWA", 37.2, "purple", "biaya ±70%", 60),
                                         lb("MARGIN", "MARGIN 30%", 38.6, "gold", "", 50, 39.6),
                                         lb("CHEF", "PEMILIK KATERING", 41.0, "gold", "", 60)], None, 0),
    ("N12", "Nikahan = **akhir pekan**", [lb("WE", "AKHIR PEKAN", 44.0, "pink", "Sabtu & Minggu", 50),
                                          lb("SAT", "4 ACARA / BULAN", 45.3, "gold", "", 40)], None, 0),
    ("N13", "Yang untung **bukan pengantin**", [lb("DIMAS", "PENGANTIN", 49.0, "red", "tekor Rp50 juta", 70),
                                               lb("CHEF", "KATERING", 50.0, "green", "+Rp18 juta / acara", 70)],
     None, 0),
    ("N14", "Kenapa banyak yang **tutup**?", [lb("MID", "BANYAK YANG TUTUP", 54.5, "red", "", 60)], None, .3),
    ("N15", "Part 2: **jebakan katering**", [lb("BAIT", "MODAL BUKA KATERING", 56.9, "gold", "", 60, 58.1)],
     None, 0),
    ("N16", "Part 2: **modal katering**", [lb("P2", "MODAL KATERING", 60.8, "pink", "& jebakannya", 60)], None, .3),
    ("N17", "Tim **PESTA** atau **MODAL**?", [], None, .25),
    ("N18", "Ini **simulasi** ya", [], None, .3),
]

HERO = [
    hero(1.86, 3.05, "**Rp100 juta**", "habis buat pesta", dict(t0=1.86, t1=2.4, frm=0, to=100, fmt="Rp{} juta")),
    hero(15.44, 16.95, "× **Rp100 rb**", "rata-rata isi amplop", style="gold"),
    hero(17.63, 19.2, "**Rp50 juta**", "total amplop", dict(t0=17.63, t1=18.25, frm=0, to=50, fmt="Rp{} juta"),
         style="cyan"),
    hero(24.85, 25.9, "× **Rp60 rb**", "per porsi", style="gold"),
    hero(26.26, 27.6, "**Rp60 juta**", "biaya katering", dict(t0=26.26, t1=26.9, frm=0, to=60, fmt="Rp{} juta")),
    hero(29.9, 31.3, "Kurang **Rp10 juta**", "amplop < tagihan katering", style="red", size=104),
    hero(38.52, 39.55, "Margin **30%**", "", style="gold", size=110),
    hero(41.74, 42.75, "**Rp18 juta**", "dibawa pulang per acara", dict(t0=41.74, t1=42.25, frm=0, to=18,
                                                                         fmt="Rp{} juta"), style="gold"),
    hero(46.19, 47.9, "**Rp72 juta**", "potensi sebulan (4 acara)", dict(t0=46.19, t1=46.95, frm=18, to=72,
                                                                          fmt="Rp{} juta"), style="gold"),
    hero(58.25, 59.7, "**JEBAKAN**", "", style="red", size=150),
    hero(70.66, 74.6, "**SIMULASI**", "angka tiap daerah bisa beda jauh", style="gold", size=120),
]

COMMENTS = [dict(t=67.72, text="PESTA", y=1395), dict(t=68.56, text="MODAL", y=1545)]

PUNCH = [(1.9, .8), (13.0, .5), (15.5, .6), (17.7, .9), (19.95, .8), (23.3, .5), (24.9, .5), (26.3, .9), (29.5, .9),
         (30.0, .6), (34.15, .7), (35.25, .8), (38.55, .6), (41.8, .8), (44.0, .5), (46.25, .9), (50.55, .8),
         (54.05, .5), (54.8, .6), (58.35, 1.2), (59.9, .7), (63.45, .5), (64.65, .5), (70.7, .6)]
FLASH = [(35.2, .22, "w"), (58.35, .3, "r"), (11.85, .18, "w")]
CHROMA = [(34.1, .25), (58.35, .3), (59.84, .2)]
PALE = [10.6, 11.4, "N03"]

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
    if sid == "N16":
        d["cta"] = .25
    scenes.append(d)

cfg = dict(scenes=scenes, hero=HERO, comments=COMMENTS, comment_scene="N17",
           fx=dict(punch=PUNCH, flash=FLASH, chroma=CHROMA, pale=PALE),
           keywords=["nikah", "100", "juta", "amplop", "pucat", "500", "undangan", "ribu", "50", "setengah", "berdua",
                     "1.000", "porsi", "60", "katering", "nggak", "cukup", "siapa", "pemilik", "30%", "18", "akhir",
                     "pekan", "72", "untung", "bukan", "tunggu", "tutup", "part", "2", "jebakan", "bangkrut",
                     "follow", "pesta", "modal", "usaha", "simulasi"])
json.dump(cfg, open("render/scenes/nkh.json", "w"), ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- SFX
ev = [[0.05, "boom", .45]]
for sid, t in TL[1:]:
    ev.append([t - .22, "whoosh_low", .3, .55])
for t, g in PUNCH:
    ev.append([t, "impact" if g >= .9 else "pop", .4 * g if g >= .9 else .55])
for h in HERO:
    if h.get("count"):
        c = h["count"]
        ev.append([c["t0"], "ticks", .28, c["t1"] - c["t0"]])
        ev.append([c["t1"], "coin", .4])
ev += [[4.15, "pop", .3], [4.95, "pop", .3], [5.75, "pop", .3], [6.55, "pop", .3], [7.25, "pop", .3],
       [9.2, "tick", .5], [9.7, "tick", .5], [10.2, "tick", .5], [10.65, "tick", .5], [10.7, "boom", .4],
       [11.97, "riser", .25, 1.4], [12.9, "ticks", .3, 1.35], [15.45, "ding", .35], [19.92, "stamp", .45],
       [23.27, "ticks", .28, .8], [24.85, "ding", .35], [29.5, "stamp", .35], [32.3, "whoosh", .4, .9],
       [34.15, "riser", .22, 1.2], [33.95, "pop", .5], [35.3, "ding", .4], [37.0, "scan", .25, 1.0],
       [38.55, "ding", .35], [39.6, "whoosh", .35, .8], [41.0, "coin", .4], [43.97, "ding", .35],
       [44.75, "pop", .4], [45.02, "pop", .4], [45.29, "pop", .4], [45.56, "pop", .4], [50.55, "stamp", .4],
       [54.4, "stamp", .3], [54.75, "stamp", .3], [55.1, "stamp", .3], [55.45, "riser", .2, 1.0],
       [56.15, "pop", .45], [58.35, "stamp", .8], [59.9, "boom", .45], [60.9, "notif", .45], [61.3, "ding", .3],
       [63.45, "pop", .4], [64.65, "pop", .4], [67.72, "type", .45, 5], [68.1, "notif", .4],
       [68.56, "type", .45, 5], [68.95, "notif", .4], [70.7, "stamp", .45], [72.4, "whoosh_low", .35, .9]]
ev.sort(key=lambda e: e[0])
json.dump(ev, open("render/scenes/nkh_sfx.json", "w"))
print(len(scenes), "adegan,", len(ev), "sfx")
